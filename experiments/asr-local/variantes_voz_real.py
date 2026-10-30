"""Variantes de ASR que se miden con voz real (#94) y cómo se corre cada una sobre audio guardado.

Orden de trabajo del plan (PLAN-VOZ-REAL.md §4), un paso detrás de otro; cada candidato se arma
sobre la configuración que se quedó en los pasos anteriores:

1. `greedy`: la línea base, tal como queda el panel por defecto (corte «Automático»).
2. Lo barato: corte de silencio fijo, `rule2`, umbral RMS y normalización de ganancia.
3. `beam` (modified_beam_search) y `beam+hotwords`.
4. `+diccionario` sobre la frase final.
5. Techo offline con faster-whisper (`small` y `large-v3-turbo`, int8), con y sin ayudas. No es un paso
   de la cadena: no pasa al panel.

Aparte de la cadena (que es de Zipformer, retirado el 2026-10-29), Parakeet por frases con distintos
cortes de silencio y umbrales RMS (PLAN-VOZ-REAL.md §9 y §10), y con Silero VAD en lugar del RMS para
decidir qué bloque es voz (§12). Cada una se compara con una de referencia (la del panel, salvo que se
pida otra); no se elige sola.

La ganancia y el umbral RMS de *captura* ya quedaron grabados en el audio y no se pueden rehacer:
lo único que se rehace offline es el umbral RMS que usa el motor para cortar y una normalización de
nivel del audio guardado, que aproxima subir la ganancia (sube también el ruido).

`ejecutar_variante` corre una variante sobre todas las pruebas y devuelve los textos finales con sus
tiempos. No calcula métricas: de eso se ocupa `medir_voz_real.py`.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable

import numpy as np

from motores import DetectorSilero, MotorASR, MotorFasterWhisper, MotorSherpaParakeet, MotorSherpaZipformer

DIR_ASR = Path(__file__).resolve().parent
DIR_MODELO = DIR_ASR / "modelos" / "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"
DIR_MODELO_PARAKEET = DIR_ASR / "modelos" / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
# https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx (fuera de Git, como los otros)
MODELO_SILERO = DIR_ASR / "modelos" / "silero-vad" / "silero_vad.onnx"
CORTE_AUTO = "auto"
CORTE_RESPALDO_S = 0.8  # lo mismo que servidor.py: corte del motor cuando el modelo no cierra la frase solo
SAMPLE_RATE = 16000
PICO_NORMALIZADO = 0.9  # nivel de pico al que lleva el audio la variante «norm»
GANANCIA_MAXIMA = 20.0  # tope para no amplificar un tramo casi mudo hasta el infinito
HILOS_POR_DEFECTO = 2  # como `servidor.py --hilos`
BLOQUE_MS_POR_DEFECTO = 40  # los bloques de 640 muestras que manda el panel


@dataclass(frozen=True)
class ConfigKroko:
    corte: float | str = CORTE_AUTO  # «auto» = endpoint nativo con 0,8 s de respaldo; un número = corte fijo en s
    rule2: float = 1.0  # rule2_min_trailing_silence del endpoint nativo
    umbral_rms: float = 0.005
    normalizar: bool = False
    beam: bool = False
    max_paths: int = 4
    hotwords: bool = False
    hotwords_score: float = 1.5
    bpe_puntaje: str = "log"
    diccionario: bool = False

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConfigWhisper:
    tamanio: str
    ayudas: bool = False  # hotwords (críticos y bancos) e initial_prompt (jerga)
    compute_type: str = "int8"

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConfigParakeet:
    corte: float = 0.9  # corte de silencio en s; el panel no tiene «auto» para Parakeet
    # Con «rms» decide qué bloque es voz; con «silero» solo marca el fin de la voz para medir la demora.
    umbral_rms: float = 0.003
    vad: str = "rms"  # «rms» (el del panel) o «silero»
    umbral_silero: float = 0.5

    def como_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Candidato:
    nombre: str
    cambios: dict[str, Any]  # sobre la configuración que se quedó hasta ese paso
    requiere: dict[str, Any] = field(default_factory=dict)  # valores que debe tener esa configuración para que aplique


@dataclass(frozen=True)
class Paso:
    nombre: str
    descripcion: str
    candidatos: tuple[Candidato, ...]


PASOS: tuple[Paso, ...] = (
    Paso("linea_base", "greedy actual del panel (corte «Automático», umbral 0,005)",
         (Candidato("greedy", {}),)),
    Paso("corte", "corte de silencio fijo (apaga el endpoint nativo)",
         (Candidato("corte-0.5", {"corte": 0.5}), Candidato("corte-0.6", {"corte": 0.6}),
          Candidato("corte-1.2", {"corte": 1.2}))),
    Paso("rule2", "rule2 del endpoint nativo (silencio mínimo tras decodificar algo)",
         (Candidato("rule2-0.5", {"rule2": 0.5}, {"corte": CORTE_AUTO}),
          Candidato("rule2-0.7", {"rule2": 0.7}, {"corte": CORTE_AUTO}))),
    Paso("rms", "umbral RMS con que el motor decide qué es silencio",
         (Candidato("rms-0.003", {"umbral_rms": 0.003}), Candidato("rms-0.01", {"umbral_rms": 0.01}))),
    Paso("norm", "audio normalizado (aproxima subir la ganancia del micrófono)",
         (Candidato("norm", {"normalizar": True}),)),
    Paso("beam", "modified_beam_search (4 caminos) sin hotwords",
         (Candidato("beam", {"beam": True}),)),
    Paso("hotwords", "hotwords de sherpa (críticos, bancos y apps)",
         (Candidato("beam+hotwords", {"beam": True, "hotwords": True}),
          Candidato("beam+hotwords-id", {"beam": True, "hotwords": True, "bpe_puntaje": "id"}))),
    Paso("diccionario", "diccionario de corrección sobre la frase final",
         (Candidato("+diccionario", {"diccionario": True}),)),
)

VARIANTES_WHISPER: tuple[tuple[str, ConfigWhisper], ...] = (
    ("whisper-small", ConfigWhisper("small")),
    ("whisper-small+hotwords", ConfigWhisper("small", ayudas=True)),
    ("whisper-large-v3-turbo", ConfigWhisper("large-v3-turbo")),
    ("whisper-large-v3-turbo+hotwords", ConfigWhisper("large-v3-turbo", ayudas=True)),
)


def _parakeet(corte: float, umbral: float) -> tuple[str, ConfigParakeet]:
    return f"parakeet-{corte}-rms-{umbral}", ConfigParakeet(corte, umbral)


def _parakeet_silero(corte: float, umbral: float = 0.5) -> tuple[str, ConfigParakeet]:
    # El RMS 0,008 ya no decide: deja el fin de la voz igual que en la referencia del laboratorio para comparar demoras.
    return f"parakeet-{corte}-silero-{umbral}", ConfigParakeet(corte, 0.008, vad="silero", umbral_silero=umbral)


# La primera es la del panel desde c21001c (0,9 s y 0,003): por defecto las demás se comparan con ella.
VARIANTES_PARAKEET: tuple[tuple[str, ConfigParakeet], ...] = (
    _parakeet(0.9, 0.003), _parakeet(0.8, 0.003), _parakeet(0.5, 0.003),
    _parakeet(0.3, 0.008), _parakeet(0.5, 0.008), _parakeet(0.6, 0.008), _parakeet(0.8, 0.008),
    _parakeet_silero(0.8), _parakeet_silero(0.5), _parakeet_silero(0.3),
)
PARAKEET_PANEL = VARIANTES_PARAKEET[0][0]
PARAKEET_LABORATORIO = "parakeet-0.8-rms-0.008"  # lo que arranca «Probar el ASR» desde el 2026-10-29 (§11)


def nombres_de_variantes() -> list[str]:
    return ([c.nombre for p in PASOS for c in p.candidatos] + [n for n, _ in VARIANTES_WHISPER]
            + [n for n, _ in VARIANTES_PARAKEET])


def aplicar(config: ConfigKroko, candidato: Candidato) -> ConfigKroko | None:
    """La configuración con los cambios del candidato, o None si no aplica sobre ésta."""
    if any(getattr(config, k) != v for k, v in candidato.requiere.items()):
        return None
    return replace(config, **candidato.cambios)


def ayudas_de_whisper(hotwords_txt: str | Path, jerga_txt: str | Path) -> dict[str, str]:
    """`hotwords` (críticos, bancos y apps) e `initial_prompt` (jerga) de la variante con ayudas."""
    from hotwords import leer_hotwords

    vistas, terminos = set(), []
    for h in leer_hotwords(hotwords_txt):
        if h.lower() not in vistas:
            vistas.add(h.lower())
            terminos.append(h)
    jerga = [l.strip() for l in Path(jerga_txt).read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.lstrip().startswith("#")]
    return {"hotwords": ", ".join(terminos),
            "initial_prompt": "Conversación en español de Tucumán, Argentina. Jerga: " + ", ".join(jerga) + "."}


# --- Motores ---------------------------------------------------------------------------------------


def crear_motor_kroko(config: ConfigKroko, spec: dict[str, Any]) -> MotorASR:
    """El motor del panel con la configuración de la variante (y el diccionario si la lleva)."""
    motor = MotorSherpaZipformer(
        str(spec.get("modelo_dir") or DIR_MODELO), hilos=spec.get("hilos", HILOS_POR_DEFECTO),
        rule2_silence=config.rule2,
        decoding_method="modified_beam_search" if config.beam else "greedy_search",
        max_active_paths=config.max_paths,
        hotwords_file=spec["hotwords_file"] if config.hotwords else None,
        hotwords_score=config.hotwords_score, bpe_puntaje=config.bpe_puntaje)
    automatico = config.corte == CORTE_AUTO
    motor.corte_silencio_s = CORTE_RESPALDO_S if automatico else float(config.corte)
    motor.umbral_rms_silencio = config.umbral_rms
    motor.enable_endpoint = automatico  # con un número manda ese corte, como en el panel
    if config.diccionario:
        from diccionario import Diccionario, MotorConDiccionario

        return MotorConDiccionario(motor, Diccionario.desde_archivo(spec["diccionario_file"]))
    return motor


def crear_motor_whisper(config: ConfigWhisper, spec: dict[str, Any]) -> MotorASR:
    ayudas = ayudas_de_whisper(spec["hotwords_file"], spec["jerga_file"]) if config.ayudas else {}
    return MotorFasterWhisper(config.tamanio, hilos=spec.get("hilos", HILOS_POR_DEFECTO),
                              compute_type=config.compute_type,
                              hotwords=ayudas.get("hotwords"), initial_prompt=ayudas.get("initial_prompt"))


def crear_motor_parakeet(config: ConfigParakeet, spec: dict[str, Any]) -> MotorASR:
    """Parakeet como en el panel (borradores cada 0,5 s y filtro de idioma), con el corte de la variante."""
    motor = MotorSherpaParakeet(str(spec.get("modelo_dir") or DIR_MODELO_PARAKEET), hilos=spec.get("hilos", HILOS_POR_DEFECTO))
    motor.corte_silencio_s = config.corte
    motor.umbral_rms_silencio = config.umbral_rms
    if config.vad == "silero":
        motor.detector_voz = DetectorSilero(spec.get("modelo_silero") or MODELO_SILERO, config.umbral_silero)
    elif config.vad != "rms":
        raise ValueError(f"vad desconocido: {config.vad}")
    return motor


def crear_motor(spec: dict[str, Any]) -> MotorASR:
    if spec["motor"] == "kroko":
        return crear_motor_kroko(ConfigKroko(**spec["config"]), spec)
    if spec["motor"] == "parakeet":
        return crear_motor_parakeet(ConfigParakeet(**spec["config"]), spec)
    return crear_motor_whisper(ConfigWhisper(**spec["config"]), spec)


# --- Corrida ---------------------------------------------------------------------------------------


def leer_canal(ruta_wav: str | Path, indice_canal: int) -> np.ndarray:
    """Un canal del estéreo guardado, en float32 y a 16 kHz (el panel siempre graba a 16 kHz)."""
    import soundfile as sf

    datos, hz = sf.read(str(ruta_wav), dtype="float32", always_2d=True)
    if hz != SAMPLE_RATE:
        raise ValueError(f"{ruta_wav}: se esperaban {SAMPLE_RATE} Hz y tiene {hz}")
    if indice_canal >= datos.shape[1]:
        raise ValueError(f"{ruta_wav}: no tiene el canal {indice_canal}")
    return np.ascontiguousarray(datos[:, indice_canal])


def normalizar_nivel(muestras: np.ndarray) -> np.ndarray:
    """Lleva el pico a PICO_NORMALIZADO con una ganancia fija (tope GANANCIA_MAXIMA); audio mudo queda igual."""
    pico = float(np.max(np.abs(muestras))) if len(muestras) else 0.0
    if pico <= 0.0:
        return muestras
    return np.clip(muestras * min(PICO_NORMALIZADO / pico, GANANCIA_MAXIMA), -1.0, 1.0).astype(np.float32)


def correr_por_bloques(motor: MotorASR, muestras: np.ndarray, bloque_ms: int, umbral_voz: float) -> dict[str, Any]:
    """Pasa el audio por el motor en bloques, como el panel, con el reloj simulado de asr_local.py.

    El reloj del sistema avanza `max(reloj + t_proceso, fin_bloque + t_proceso)`; una frase está
    disponible en `max(reloj, fin_audio + proceso_ms)`. La demora de una final es `disponible_s -
    fin de la voz`, donde la voz termina en el último bloque con RMS sobre el umbral (o en el fin del
    audio de la frase, lo que ocurra antes), igual que `llamada.py`. Las finales que salen de
    `vaciar_final` (el cierre de la prueba) cuentan como segmento pero no tienen demora comparable.
    """
    tam = int(bloque_ms / 1000 * SAMPLE_RATE)
    reloj = 0.0
    ultima_voz: float | None = None
    tiempos_ms: list[float] = []
    finales, parciales = [], 0
    t_proceso = 0.0

    def registrar(eventos, cierre: bool) -> None:
        nonlocal parciales
        for ev in eventos:
            if not any(c.isalnum() for c in ev.texto):
                continue
            if ev.tipo == "parcial":
                parciales += 1
                continue
            disponible = round(max(reloj, ev.fin_audio_s + ev.proceso_ms / 1000.0), 3)
            fin_voz = min(ultima_voz if ultima_voz is not None else ev.fin_audio_s, ev.fin_audio_s)
            finales.append({"segmento": ev.segmento, "texto": ev.texto, "inicio_audio_s": ev.inicio_audio_s,
                            "fin_audio_s": ev.fin_audio_s, "disponible_s": disponible,
                            "demora_s": None if cierre else round(max(0.0, disponible - fin_voz), 3),
                            "cierre": cierre})

    for desde in range(0, len(muestras), tam):
        bloque = muestras[desde:desde + tam]
        fin_bloque = (desde + len(bloque)) / SAMPLE_RATE
        if len(bloque) and float(np.sqrt(np.mean(bloque ** 2))) >= umbral_voz:
            ultima_voz = fin_bloque
        t0 = time.perf_counter()
        eventos = motor.procesar_bloque(bloque, desde / SAMPLE_RATE, fin_bloque)
        dt = time.perf_counter() - t0
        t_proceso += dt
        tiempos_ms.append(dt * 1000.0)
        reloj = max(reloj + dt, fin_bloque + dt)
        registrar(eventos, cierre=False)
    t0 = time.perf_counter()
    eventos = motor.vaciar_final(len(muestras) / SAMPLE_RATE)
    dt = time.perf_counter() - t0
    t_proceso += dt
    reloj = max(reloj + dt, len(muestras) / SAMPLE_RATE + dt)
    registrar(eventos, cierre=True)
    return {"finales": finales, "parciales": parciales, "proceso_s": round(t_proceso, 4),
            "bloques_ms": tiempos_ms}


def correr_por_lote(motor: MotorASR, muestras: np.ndarray) -> dict[str, Any]:
    """Motores que no son streaming (Whisper): se entrega todo el audio y se mide la transcripción entera."""
    motor.procesar_bloque(muestras, 0.0, len(muestras) / SAMPLE_RATE)
    t0 = time.perf_counter()
    eventos = motor.vaciar_final(len(muestras) / SAMPLE_RATE)
    dt = time.perf_counter() - t0
    finales = [{"segmento": e.segmento, "texto": e.texto, "inicio_audio_s": e.inicio_audio_s,
                "fin_audio_s": e.fin_audio_s, "disponible_s": None, "demora_s": None, "cierre": False}
               for e in eventos if e.tipo == "final" and any(c.isalnum() for c in e.texto)]
    return {"finales": finales, "parciales": 0, "proceso_s": round(dt, 4), "bloques_ms": []}


def ejecutar_variante(spec: dict[str, Any], crear: Callable[[dict[str, Any]], MotorASR] = crear_motor) -> dict[str, Any]:
    """Corre una variante sobre todas las pruebas del `spec` y devuelve los finales con sus tiempos.

    `spec`: `motor` («kroko», «parakeet» o «whisper»), `config`, `pruebas` (lista de `{id, wav, canal}` con `canal`
    0 o 1), `bloque_ms`, `hilos` y las rutas de hotwords, jerga y diccionario. El modelo se carga una vez.
    """
    t0 = time.perf_counter()
    motor = crear(spec)
    motor.inicializar()
    carga_s = round(time.perf_counter() - t0, 3)
    por_bloques = spec["motor"] in ("kroko", "parakeet")
    normalizar = bool(spec["config"].get("normalizar"))
    umbral = float(spec["config"].get("umbral_rms", 0.005))
    resultados = []
    for i, prueba in enumerate(spec["pruebas"]):
        if i > 0:
            getattr(motor, "nueva_sesion", motor.inicializar)()
        muestras = leer_canal(prueba["wav"], prueba["canal"])
        if normalizar:
            muestras = normalizar_nivel(muestras)
        corrida = (correr_por_bloques(motor, muestras, spec.get("bloque_ms", BLOQUE_MS_POR_DEFECTO), umbral)
                   if por_bloques else correr_por_lote(motor, muestras))
        bloques = corrida.pop("bloques_ms")
        resultados.append({"id": prueba["id"], "audio_s": round(len(muestras) / SAMPLE_RATE, 3), **corrida,
                           "bloques": _resumen_bloques(bloques)})
    return {"carga_s": carga_s, "metadatos_motor": motor.metadatos(), "pruebas": resultados}


def _resumen_bloques(tiempos_ms: list[float]) -> dict[str, Any] | None:
    if not tiempos_ms:
        return None
    from metricas_voz_real import percentil

    return {"n": len(tiempos_ms), "p95_ms": round(percentil(tiempos_ms, 95), 2),
            "max_ms": round(max(tiempos_ms), 2), "mediana_ms": round(float(np.median(tiempos_ms)), 2)}
