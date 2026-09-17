"""Replay en streaming: WAV en pedazos, ASR, reglas, turnos y contador.

Sin sleep: el RTF es computo / duracion. No es llamada en vivo.

Modo texto (--texto): misma logica sin ASR ni segundos, para el brazo
"transcripcion manual" de E1. La latencia se reporta en turnos.
"""

import time
import wave
from pathlib import Path

import numpy as np

import asr
import detector
import rules
import turns

TERMINOS_CRITICOS = ("codigo", "token", "transferencia")
VENTANA_GOTEO = 3


class ContadorGoteo:
    """Maximo de los ultimos 3 puntajes; dispara si se mantiene alto dos turnos."""

    def __init__(self, umbral: float = 0.5, ventana: int = VENTANA_GOTEO):
        self._umbral = umbral
        self._ventana = ventana
        self._ps: list[float] = []
        self._prev_alto = False

    def agregar(self, p: float) -> bool:
        self._ps.append(p)
        alto = max(self._ps[-self._ventana :]) >= self._umbral
        disparo = alto and self._prev_alto
        self._prev_alto = alto
        return disparo


def leer_wav_mono_16k(path: str | Path) -> tuple[np.ndarray, int, float]:
    """WAV 16 kHz mono 16-bit a float32 [-1, 1]. Sin resampleo: entra asi o falla claro."""
    with wave.open(str(path), "rb") as w:
        if w.getnchannels() != 1 or w.getsampwidth() != 2 or w.getframerate() != 16000:
            raise ValueError(
                f"{path}: se espera WAV 16kHz mono 16-bit, llego "
                f"{w.getframerate()}Hz / {w.getnchannels()} canal(es) / {w.getsampwidth() * 8}-bit. "
                "Convertilo fuera del repo antes de correr."
            )
        crudo = w.readframes(w.getnframes())
    muestras = np.frombuffer(crudo, dtype=np.int16).astype(np.float32) / 32768.0
    sr = 16000
    return muestras, sr, len(muestras) / sr


def leer_turnos_txt(path: str | Path) -> list[str]:
    """Una linea = un turno. Vacias y `#` se ignoran."""
    lineas = [
        l.strip()
        for l in Path(path).read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.strip().startswith("#")
    ]
    if not lineas:
        raise ValueError(f"{path}: sin turnos (una linea = un turno, `#` comentarios)")
    return lineas


def memoria_pico_mb() -> float | None:
    """Pico RSS del proceso en MB. None si la plataforma no lo da."""
    try:
        import resource

        kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return round(kb / 1024.0, 1)
    except Exception:
        return None


def correr(
    wav: str | Path,
    gama,
    semillas_path: str | Path,
    modelos_dir: str | Path,
    chunk_ms: int = 300,
    umbral_goteo: float = 0.5,
) -> dict:
    """Una corrida sobre audio: devuelve turnos, eventos, RTF y memoria."""
    muestras, sr, duracion_s = leer_wav_mono_16k(wav)
    model_dir = asr.descargar_modelo(gama.asr, modelos_dir)
    rec = asr.crear_reconocedor(model_dir, gama.hilos_asr)
    stream = rec.create_stream()
    det = detector.DetectorTfidf(semillas_path)
    cortador = turns.CortadorTurnos(sample_rate=sr)
    contador = ContadorGoteo(umbral_goteo)

    chunk_n = int(sr * chunk_ms / 1000)
    turnos: list[dict] = []
    eventos_incendio: list[dict] = []
    prev_etiquetas: set[str] = set()
    t_incendio: float | None = None
    t_goteo: float | None = None
    turno_incendio: int | None = None
    turno_goteo: int | None = None
    t_computo = 0.0

    def cerrar_turno(t_s: float, texto: str):
        nonlocal t_goteo, turno_goteo
        p = det.puntaje(texto)
        n = len(turnos) + 1
        if contador.agregar(p) and t_goteo is None:
            t_goteo = round(t_s, 2)
            turno_goteo = n
        turnos.append(
            {"n": n, "fin_s": round(t_s, 2), "texto": texto, "puntaje": round(p, 3)}
        )
        rec.reset(stream)

    for i in range(0, len(muestras), chunk_n):
        pedazo = muestras[i : i + chunk_n]
        t_s = (i + len(pedazo)) / sr
        t0 = time.perf_counter()
        borrador = asr.alimentar(rec, stream, pedazo, sr)
        etiquetas = set(rules.incendio_en(borrador))
        nuevas = etiquetas - prev_etiquetas
        if nuevas:
            eventos_incendio.append(
                {
                    "t_s": round(t_s, 2),
                    "turno": len(turnos) + 1,
                    "etiquetas": sorted(nuevas),
                    "texto": borrador,
                }
            )
            if t_incendio is None:
                t_incendio = round(t_s, 2)
                turno_incendio = len(turnos) + 1
        prev_etiquetas = etiquetas
        if cortador.agregar(pedazo):
            cerrar_turno(t_s, borrador.strip())
        t_computo += time.perf_counter() - t0

    t0 = time.perf_counter()
    ultimo = asr.vaciar_final(rec, stream, sr).strip()
    if ultimo or not turnos:
        cerrar_turno(duracion_s, ultimo)
    t_computo += time.perf_counter() - t0

    texto_final = " ".join(t["texto"] for t in turnos if t["texto"])
    ts = [t for t in (t_incendio, t_goteo) if t is not None]
    ns = [n for n in (turno_incendio, turno_goteo) if n is not None]
    return {
        "modo": "audio",
        "duracion_s": round(duracion_s, 2),
        "rtf": round(t_computo / duracion_s, 3) if duracion_s else None,
        "memoria_pico_mb": memoria_pico_mb(),
        "latencia_decision_s": min(ts) if ts else None,
        "latencia_decision_turno": min(ns) if ns else None,
        "incendio": {"disparo": t_incendio is not None, "t_s": t_incendio, "eventos": eventos_incendio},
        "goteo": {"disparo": t_goteo is not None, "t_s": t_goteo, "umbral": umbral_goteo},
        "texto_final": texto_final,
        "turnos": turnos,
        "terminos_criticos": {t: t in texto_final.lower() for t in TERMINOS_CRITICOS},
    }


def correr_texto(
    txt_path: str | Path, semillas_path: str | Path, umbral_goteo: float = 0.5
) -> dict:
    """Una corrida sobre transcripto: reglas + TF-IDF + contador, sin ASR ni segundos."""
    textos = leer_turnos_txt(txt_path)
    det = detector.DetectorTfidf(semillas_path)
    contador = ContadorGoteo(umbral_goteo)
    turnos: list[dict] = []
    eventos: list[dict] = []
    turno_incendio: int | None = None
    turno_goteo: int | None = None
    for n, texto in enumerate(textos, 1):
        etiquetas = rules.incendio_en(texto)
        if etiquetas:
            eventos.append(
                {"t_s": None, "turno": n, "etiquetas": sorted(etiquetas), "texto": texto}
            )
            if turno_incendio is None:
                turno_incendio = n
        p = det.puntaje(texto)
        if contador.agregar(p) and turno_goteo is None:
            turno_goteo = n
        turnos.append({"n": n, "fin_s": None, "texto": texto, "puntaje": round(p, 3)})
    texto_final = " ".join(textos)
    ns = [n for n in (turno_incendio, turno_goteo) if n is not None]
    return {
        "modo": "texto",
        "duracion_s": None,
        "rtf": None,
        "memoria_pico_mb": memoria_pico_mb(),
        "latencia_decision_s": None,
        "latencia_decision_turno": min(ns) if ns else None,
        "incendio": {"disparo": turno_incendio is not None, "t_s": None, "eventos": eventos},
        "goteo": {"disparo": turno_goteo is not None, "t_s": None, "umbral": umbral_goteo},
        "texto_final": texto_final,
        "turnos": turnos,
        "terminos_criticos": {t: t in texto_final.lower() for t in TERMINOS_CRITICOS},
        "nota": "Sin audio: RTF y segundos no aplican; latencia en turnos.",
    }
