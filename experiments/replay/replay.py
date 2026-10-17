"""Replay incremental de transcripciones ASR con detector y política de aviso único (#28).

Integra en una corrida replay la transcripción local (contrato JSONL de ASR) o un
caso de texto, y evalúa el detector incrementalmente con un único aviso por llamada.
Modela la cola secuencial de evaluación del detector: inicio_eval_n = max(disponible_s_n, fin_eval_{n-1}).

Uso:
    python replay.py --actualizaciones <actualizaciones.jsonl> --detector reglas|slm [--modelo qwen3.5:2b] [--prompt tarea] [--hablantes ab|sin] [--disparo final|parcial] --salida <dir>
    python replay.py --texto <caso.txt> --detector reglas|slm [--salida <dir>]

Salida en <dir>:
    eventos.csv      Traza detallada por cada actualización procesada con cola de evaluación
    manifiesto.json  Entradas con hash sha256, config, código git, hardware, seed
    resumen.md       T_A, motivo, evidencia, espera de cola, atraso e información del aviso

> Estado: propuesta sin discutir. Política de aviso único y ventana abiertas en D08.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Importar dependencias de slm-directo y locales
DIR_REPLAY = Path(__file__).resolve().parent
DIR_SLM_DIRECTO = DIR_REPLAY.parent / "slm-directo"
if str(DIR_SLM_DIRECTO) not in sys.path:
    sys.path.insert(0, str(DIR_SLM_DIRECTO))
if str(DIR_REPLAY) not in sys.path:
    sys.path.insert(0, str(DIR_REPLAY))

import cliente_ollama
import correr
import detectores
from contexto import Actualizacion, ContextoLlamada

POLITICA = "aviso_unico_primer_true_valido"

COLUMNAS_EVENTOS = [
    "llamada_id",
    "n",
    "tipo",
    "segmento",
    "canal",
    "texto",
    "texto_disponible_resumido",
    "inicio_audio_s",
    "fin_audio_s",
    "disponible_s",
    "inicio_eval_s",
    "fin_eval_s",
    "espera_cola_ms",
    "ms_detector",
    "riesgo",
    "alerta_sugerida",
    "motivo",
    "evidencia",
    "valida",
    "error",
    "aviso",
    "t_a",
]


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=DIR_REPLAY, capture_output=True, text=True, timeout=10, check=True
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def info_codigo() -> dict:
    commit = _git("rev-parse", "HEAD") or "desconocido"
    cambios = _git("status", "--porcelain", "--", ".", ":(exclude)corridas")
    return {"commit": commit, "cambios_sin_commit": bool(cambios)}


def _ram_total_gb() -> float | None:
    try:
        if sys.platform.startswith("linux"):
            for renglon in Path("/proc/meminfo").read_text().splitlines():
                if renglon.startswith("MemTotal:"):
                    return round(int(renglon.split()[1]) / 1024**2, 1)
        if sys.platform == "darwin":
            salida = subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True)
            return round(int(salida.stdout) / 1024**3, 1)
    except Exception:
        return None
    return None


def info_maquina() -> dict:
    return {
        "sistema": platform.platform(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor() or "no informado",
        "nucleos_logicos": os.cpu_count(),
        "ram_total_gb": _ram_total_gb(),
        "python": platform.python_version(),
    }


def cargar_actualizaciones_jsonl(ruta: Path) -> tuple[dict | None, list[Actualizacion]]:
    """Carga un archivo JSONL del contrato ASR. Separa meta opcional y devuelve actualizaciones."""
    meta = None
    actualizaciones = []
    with open(ruta, "r", encoding="utf-8") as f:
        for num_linea, linea in enumerate(f, start=1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                data = json.loads(linea)
            except json.JSONDecodeError as e:
                raise ValueError(f"Error de formato JSON en {ruta}:{num_linea}: {e}")

            if "meta" in data:
                meta = data["meta"]
                continue

            act = Actualizacion(
                llamada_id=str(data.get("llamada_id", "llamada_01")),
                n=int(data.get("n", len(actualizaciones) + 1)),
                tipo=str(data.get("tipo", "final")),
                segmento=int(data.get("segmento", 0)),
                texto=str(data.get("texto", "")),
                inicio_audio_s=float(data["inicio_audio_s"]) if data.get("inicio_audio_s") is not None else None,
                fin_audio_s=float(data["fin_audio_s"]) if data.get("fin_audio_s") is not None else None,
                disponible_s=float(data["disponible_s"]) if data.get("disponible_s") is not None else None,
                proceso_ms=float(data["proceso_ms"]) if data.get("proceso_ms") is not None else None,
                canal=data.get("canal"),
            )
            actualizaciones.append(act)
    return meta, actualizaciones


_REGEX_LINEA_TEXTO = re.compile(r"^(A|B):\s*(.*)$")


def cargar_caso_texto(ruta: Path) -> list[Actualizacion]:
    """Carga un caso de texto y lo convierte en actualizaciones secuenciales finales sin tiempo."""
    if not ruta.exists():
        # Buscar en slm-directo/casos/texto/
        alternativa = DIR_SLM_DIRECTO / "casos" / "texto" / ruta.name
        if alternativa.exists():
            ruta = alternativa
        else:
            alternativa_txt = DIR_SLM_DIRECTO / "casos" / "texto" / f"{ruta.name}.txt"
            if alternativa_txt.exists():
                ruta = alternativa_txt
            else:
                raise FileNotFoundError(f"No se encontró el archivo de texto: {ruta}")

    llamada_id = ruta.stem
    actualizaciones = []
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    for n, linea_raw in enumerate(lineas, start=1):
        linea = linea_raw.strip()
        if not linea:
            continue
        m = _REGEX_LINEA_TEXTO.match(linea)
        if m:
            canal = m.group(1)
            texto = m.group(2)
        else:
            canal = None
            texto = linea

        act = Actualizacion(
            llamada_id=llamada_id,
            n=n,
            tipo="final",
            segmento=n,
            texto=texto,
            inicio_audio_s=None,
            fin_audio_s=None,
            disponible_s=None,
            proceso_ms=None,
            canal=canal,
        )
        actualizaciones.append(act)
    return actualizaciones


def formatear_texto_resumido(lineas: tuple[Any, ...], hablantes_modo: str) -> str:
    """Genera la representación en una sola línea del texto acumulado disponible."""
    if hablantes_modo == "ab":
        partes = [f"{l.hablante}: {l.texto}" if l.hablante else l.texto for l in lineas]
    else:
        partes = [l.texto for l in lineas]
    return " // ".join(partes)


def construir_detector(
    nombre: str,
    modelo: str = "qwen3.5:2b",
    prompt_nombre: str = "tarea",
    hablantes: str = "ab",
    seed: int = 42,
    num_ctx: int = 4096,
    ollama_url: str = cliente_ollama.URL_POR_DEFECTO,
) -> Any:
    """Instancia el detector correspondiente de slm-directo."""
    if nombre == "reglas":
        return detectores.DetectorReglas()
    elif nombre == "slm":
        prompt_str = detectores.cargar_prompt(prompt_nombre)
        cliente = cliente_ollama.ClienteOllama(ollama_url)
        detector = detectores.DetectorSLM(
            cliente=cliente,
            modelo=modelo,
            prompt=prompt_str,
            hablantes=hablantes,
            num_ctx=num_ctx,
            seed=seed,
        )
        # Compartir el calentamiento y la negociación de `think` con slm-directo.
        # Qwen3.5 necesita pensar=False para responder dentro del formato y presupuesto.
        detector.carga = correr.calentar(cliente, modelo, num_ctx)
        detector.pensar = detector.carga["pensar"]
        return detector
    else:
        raise ValueError(f"Detector desconocido {nombre!r}; opciones: 'reglas', 'slm'")


def correr_replay(
    actualizaciones: list[Actualizacion],
    detector: Any,
    hablantes: str = "ab",
    disparo: str = "final",
    salida_dir: Path | None = None,
    meta_extra: dict | None = None,
) -> tuple[list[dict], list[ContextoLlamada]]:
    """Ejecuta el replay sobre la lista de actualizaciones en orden secuencial.

    Modela la cola del detector: una evaluación no puede iniciar antes de que termine
    la previa (inicio_eval = max(disponible_s, fin_eval_{prev})).
    Devuelve (filas_eventos, lista_contextos_llamadas).
    """
    if not actualizaciones:
        return [], []

    # Verificar si hay canales disponibles
    tiene_canales = any(a.canal in ("A", "B") for a in actualizaciones)
    if not tiene_canales and hablantes == "ab":
        print(
            "[replay] Aviso: las actualizaciones no contienen canal (canal=null); usando hablantes='sin'.",
            file=sys.stderr,
        )
        hablantes = "sin"

    # Si el detector es SLM y cambió hablantes, actualizar su propiedad
    if hasattr(detector, "hablantes"):
        detector.hablantes = hablantes

    filas_eventos: list[dict] = []
    contextos: list[ContextoLlamada] = []
    ctx_actual: ContextoLlamada | None = None

    for act in actualizaciones:
        if ctx_actual is None or ctx_actual.llamada_id != act.llamada_id:
            # Reinicio de contexto y cola secuencial entre llamadas distintas
            ctx_actual = ContextoLlamada(llamada_id=act.llamada_id)
            contextos.append(ctx_actual)

        # 1. Aplicar al contexto incremental
        lineas_disponibles = ctx_actual.aplicar(act, hablantes)

        # 2. Determinar si se dispara el detector
        debe_evaluar = (disparo == "parcial") or (act.tipo == "final")

        if debe_evaluar:
            # Pasar únicamente lo disponible hasta el instante actual
            respuesta = detector.evaluar(lineas_disponibles)
            inicio_eval_s, fin_eval_s, espera_cola_ms, es_aviso, t_a = ctx_actual.registrar_evaluacion(
                act, respuesta, lineas_disponibles
            )
        else:
            respuesta = None
            inicio_eval_s = None
            fin_eval_s = None
            espera_cola_ms = None
            es_aviso = False
            t_a = None

        # 3. Armar fila para eventos.csv
        texto_resumido = formatear_texto_resumido(lineas_disponibles, hablantes)

        fila = {
            "llamada_id": act.llamada_id,
            "n": act.n,
            "tipo": act.tipo,
            "segmento": act.segmento,
            "canal": act.canal or "",
            "texto": act.texto,
            "texto_disponible_resumido": texto_resumido,
            "inicio_audio_s": f"{act.inicio_audio_s:.2f}" if act.inicio_audio_s is not None else "",
            "fin_audio_s": f"{act.fin_audio_s:.2f}" if act.fin_audio_s is not None else "",
            "disponible_s": f"{act.disponible_s:.3f}" if act.disponible_s is not None else "",
            "inicio_eval_s": f"{inicio_eval_s:.3f}" if inicio_eval_s is not None else "",
            "fin_eval_s": f"{fin_eval_s:.3f}" if fin_eval_s is not None else "",
            "espera_cola_ms": f"{espera_cola_ms:.1f}" if espera_cola_ms is not None else "",
            "ms_detector": f"{respuesta.ms:.1f}" if respuesta and respuesta.ms is not None else "",
            "riesgo": f"{respuesta.riesgo:.3f}" if respuesta and respuesta.riesgo is not None else "",
            "alerta_sugerida": (
                ("true" if respuesta.alerta_sugerida else "false")
                if respuesta and respuesta.alerta_sugerida is not None
                else ""
            ),
            "motivo": respuesta.motivo if respuesta else "",
            "evidencia": respuesta.evidencia if respuesta else "",
            "valida": ("true" if respuesta.valida else "false") if respuesta else "",
            "error": getattr(respuesta, "error", "") if respuesta else "",
            "aviso": "true" if es_aviso else "false",
            "t_a": f"{t_a:.4f}" if t_a is not None else "",
        }
        filas_eventos.append(fila)

    if salida_dir is not None:
        salida_dir = Path(salida_dir)
        salida_dir.mkdir(parents=True, exist_ok=True)
        guardar_eventos_csv(salida_dir / "eventos.csv", filas_eventos)

    return filas_eventos, contextos


def guardar_eventos_csv(ruta: Path, filas: list[dict]) -> None:
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNAS_EVENTOS)
        writer.writeheader()
        writer.writerows(filas)


def guardar_manifiesto(
    ruta: Path,
    ruta_entrada: Path,
    modo: str,
    detector_nombre: str,
    modelo: str | None,
    prompt: str | None,
    hablantes: str,
    disparo: str,
    seed: int | str,
    asr_meta: dict | None = None,
    carga: dict | None = None,
) -> None:
    manifiesto = {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "comando": " ".join(sys.argv),
        "entradas": {
            "ruta": str(ruta_entrada),
            "sha256": sha256_archivo(ruta_entrada),
            "tamano_bytes": ruta_entrada.stat().st_size,
            "tipo": "actualizaciones_jsonl" if modo == "audio" else "caso_texto",
        },
        "config": {
            "detector": detector_nombre,
            "modelo": modelo if detector_nombre == "slm" else None,
            "prompt": prompt if detector_nombre == "slm" else None,
            "hablantes": hablantes,
            "disparo": disparo,
            "politica": POLITICA,
            "seed": seed if detector_nombre == "slm" else "no-aplica",
        },
        "codigo": info_codigo(),
        "hardware": info_maquina(),
    }
    if detector_nombre == "slm":
        manifiesto["carga"] = carga
    if asr_meta:
        manifiesto["asr_meta"] = asr_meta

    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(manifiesto, f, indent=2, ensure_ascii=False)


def guardar_resumen(
    ruta: Path,
    ruta_entrada: Path,
    modo: str,
    detector_nombre: str,
    modelo: str | None,
    prompt: str | None,
    hablantes: str,
    disparo: str,
    contextos: list[ContextoLlamada],
    filas_eventos: list[dict],
) -> None:
    sha = sha256_archivo(ruta_entrada)
    codigo = info_codigo()

    total_actualizaciones = len(filas_eventos)
    total_parciales = sum(1 for f in filas_eventos if f["tipo"] == "parcial")
    total_finales = sum(1 for f in filas_eventos if f["tipo"] == "final")
    total_evaluaciones = sum(1 for f in filas_eventos if f["valida"] != "")
    total_validas = sum(1 for f in filas_eventos if f["valida"] == "true")
    total_fallos = sum(1 for f in filas_eventos if f["valida"] == "false")

    ms_valores = [float(f["ms_detector"]) for f in filas_eventos if f["ms_detector"]]
    tiempo_total_ms = sum(ms_valores) if ms_valores else 0.0
    tiempo_promedio_ms = (tiempo_total_ms / len(ms_valores)) if ms_valores else 0.0

    modelo_str = modelo if detector_nombre == "slm" else "no-aplica"
    prompt_str = prompt if detector_nombre == "slm" else "no-aplica"

    lineas_md = [
        "# Resumen de corrida replay",
        "",
        f"- **Fecha/hora:** {datetime.now().isoformat(timespec='seconds')}",
        f"- **Entrada:** `{ruta_entrada}` (sha256: `{sha}`)",
        f"- **Modo:** {'Audio ASR incremental (JSONL)' if modo == 'audio' else 'Modo texto (sin audio)'}",
        f"- **Detector:** `{detector_nombre}`",
        f"- **Configuración:** modelo: `{modelo_str}`, prompt: `{prompt_str}`, hablantes: `{hablantes}`, disparo: `{disparo}`",
        f"- **Política de aviso:** `{POLITICA}`",
        f"- **Código git:** commit `{codigo.get('commit', 'desconocido')[:10]}` (cambios sin commit: {codigo.get('cambios_sin_commit', False)})",
        "",
        "## Resultados por llamada",
        "",
    ]

    for ctx in contextos:
        lineas_md.append(f"### Llamada `{ctx.llamada_id}`")
        lineas_md.append("")
        if ctx.aviso_emitido and ctx.aviso_actualizacion is not None:
            act = ctx.aviso_actualizacion
            resp = ctx.aviso_respuesta
            lineas_md.append("- **Aviso emitido:** Sí")
            if act.disponible_s is not None and ctx.aviso_t_a is not None:
                ms_resp = resp.ms if resp and resp.ms is not None else 0.0
                ini_s = ctx.aviso_inicio_eval_s if ctx.aviso_inicio_eval_s is not None else act.disponible_s
                cola_ms = ctx.aviso_espera_cola_ms if ctx.aviso_espera_cola_ms is not None else 0.0
                lineas_md.append(
                    f"- **T_A (reloj de audio):** `{ctx.aviso_t_a:.4f} s` (disponible_s: `{act.disponible_s:.3f} s`, inicio_eval: `{ini_s:.3f} s`, espera_cola: `{cola_ms:.1f} ms`, detector: `{ms_resp:.1f} ms`)"
                )
            else:
                lineas_md.append(f"- **T_A:** No aplica (modo texto sin audio; aviso en turno n={act.n}, segmento={act.segmento})")

            lineas_md.append(f"- **Motivo:** {resp.motivo if resp else '—'}")
            lineas_md.append(f"- **Evidencia citada:** {resp.evidencia if resp else '—'}")
            lineas_md.append("- **Actualización desencadenante:**")
            lineas_md.append(f"  - **n:** {act.n}")
            lineas_md.append(f"  - **Tipo:** `{act.tipo}`")
            lineas_md.append(f"  - **Segmento:** {act.segmento}")
            lineas_md.append(f"  - **Canal:** `{act.canal or 'null'}`")
            lineas_md.append(f"  - **Texto de la actualización:** {act.texto}")
            if act.inicio_audio_s is not None and act.fin_audio_s is not None:
                lineas_md.append(
                    f"  - **Intervalo de audio:** [{act.inicio_audio_s:.2f} s - {act.fin_audio_s:.2f} s] (disponible a los {act.disponible_s:.3f} s)"
                )

            lineas_md.append("- **Información disponible al momento del aviso:**")
            if ctx.aviso_lineas:
                for idx_l, l in enumerate(ctx.aviso_lineas, start=1):
                    prefix = f"{l.hablante}: " if l.hablante and hablantes == "ab" else ""
                    lineas_md.append(f"  {idx_l}. {prefix}{l.texto}")
            else:
                lineas_md.append("  (sin líneas acumuladas)")
        else:
            lineas_md.append("- **Aviso emitido:** No (la llamada finalizó sin generar alertas sugeridas válidas)")

        if modo == "audio":
            lineas_md.append(f"- **Espera de cola máxima:** `{ctx.max_espera_cola_ms:.1f} ms`")
            atraso_str = (
                "Sí (el detector acumuló retraso respecto de la llegada del audio)"
                if ctx.hubo_atraso
                else "No (procesamiento al día)"
            )
            lineas_md.append(f"- **Atraso respecto del audio:** {atraso_str}")
        else:
            lineas_md.append("- **Espera de cola máxima:** No aplica (modo texto sin audio)")
            lineas_md.append("- **Atraso respecto del audio:** No aplica (modo texto sin audio)")

        lineas_md.append(f"- **Fallos del detector:** {ctx.fallos}")
        if ctx.errores:
            lineas_md.append(f"  - Errores registrados: {', '.join(ctx.errores)}")
        lineas_md.append("")

    if modo == "audio":
        max_cola_global = max((c.max_espera_cola_ms for c in contextos), default=0.0)
        atraso_global = any(c.hubo_atraso for c in contextos)
        cola_global_str = f"`{max_cola_global:.1f} ms`"
        atraso_global_str = "Sí" if atraso_global else "No"
    else:
        cola_global_str = "No aplica (modo texto sin audio)"
        atraso_global_str = "No aplica (modo texto sin audio)"

    lineas_md.extend(
        [
            "## Métricas generales de ejecución",
            "",
            f"- **Llamadas procesadas:** {len(contextos)}",
            f"- **Actualizaciones totales:** {total_actualizaciones} (parciales: {total_parciales}, finales: {total_finales})",
            f"- **Evaluaciones del detector:** {total_evaluaciones} (válidas: {total_validas}, fallos: {total_fallos})",
            f"- **Tiempo de inferencia del detector:** total `{tiempo_total_ms:.1f} ms`, promedio `{tiempo_promedio_ms:.1f} ms` por evaluación",
            f"- **Espera de cola máxima observada:** {cola_global_str}",
            f"- **Detector se atrasó respecto del audio:** {atraso_global_str}",
            "",
            "> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.",
            "",
        ]
    )

    ruta.write_text("\n".join(lineas_md), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay incremental de transcripción y detector con aviso único (#28)."
    )
    grupo_entrada = parser.add_mutually_exclusive_group(required=True)
    grupo_entrada.add_argument(
        "--actualizaciones",
        type=Path,
        help="Ruta al archivo JSONL del contrato ASR con las actualizaciones incrementales.",
    )
    grupo_entrada.add_argument(
        "--texto",
        type=Path,
        help="Ruta a un caso de texto (.txt) de experiments/slm-directo/casos/texto/ sin audio.",
    )

    parser.add_argument(
        "--detector",
        choices=["reglas", "slm"],
        required=True,
        help="Detector a utilizar: 'reglas' (comparador) o 'slm' (modelo local).",
    )
    parser.add_argument(
        "--modelo",
        type=str,
        default="qwen3.5:2b",
        help="Modelo SLM a utilizar en Ollama (por defecto: qwen3.5:2b).",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="tarea",
        help="Variante de prompt para SLM: 'tarea' o 'tarea+base' (por defecto: tarea).",
    )
    parser.add_argument(
        "--hablantes",
        choices=["ab", "sin"],
        default="ab",
        help="Modo de hablantes: 'ab' (con canales A/B) o 'sin' (sin etiquetas de hablante).",
    )
    parser.add_argument(
        "--disparo",
        choices=["final", "parcial"],
        default="final",
        help="Momento de invocación del detector: 'final' (solo en segmentos finales) o 'parcial' (en cada actualización).",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        required=True,
        help="Directorio donde se guardarán eventos.csv, manifiesto.json y resumen.md.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semilla aleatoria para SLM (por defecto: 42; no aplica para reglas).",
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=4096,
        help="Tamaño de ventana de contexto en tokens para SLM (por defecto: 4096).",
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default=cliente_ollama.URL_POR_DEFECTO,
        help=f"URL del servidor Ollama (por defecto: {cliente_ollama.URL_POR_DEFECTO}).",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    salida_dir = Path(args.salida)
    salida_dir.mkdir(parents=True, exist_ok=True)

    asr_meta = None
    if args.actualizaciones:
        modo = "audio"
        ruta_entrada = args.actualizaciones
        asr_meta, actualizaciones = cargar_actualizaciones_jsonl(ruta_entrada)
    else:
        modo = "texto"
        ruta_entrada = args.texto
        actualizaciones = cargar_caso_texto(ruta_entrada)

    hablantes = args.hablantes
    tiene_canales = any(a.canal in ("A", "B") for a in actualizaciones)
    if not tiene_canales and hablantes == "ab":
        print(
            "[replay] Aviso: las actualizaciones no contienen canales de hablante (canal=null); usando hablantes='sin'.",
            file=sys.stderr,
        )
        hablantes = "sin"

    detector = construir_detector(
        nombre=args.detector,
        modelo=args.modelo,
        prompt_nombre=args.prompt,
        hablantes=hablantes,
        seed=args.seed,
        num_ctx=args.num_ctx,
        ollama_url=args.ollama_url,
    )

    filas_eventos, contextos = correr_replay(
        actualizaciones=actualizaciones,
        detector=detector,
        hablantes=hablantes,
        disparo=args.disparo,
        salida_dir=salida_dir,
    )

    guardar_manifiesto(
        ruta=salida_dir / "manifiesto.json",
        ruta_entrada=ruta_entrada,
        modo=modo,
        detector_nombre=args.detector,
        modelo=args.modelo,
        prompt=args.prompt,
        hablantes=hablantes,
        disparo=args.disparo,
        seed=args.seed,
        asr_meta=asr_meta,
        carga=getattr(detector, "carga", None),
    )

    guardar_resumen(
        ruta=salida_dir / "resumen.md",
        ruta_entrada=ruta_entrada,
        modo=modo,
        detector_nombre=args.detector,
        modelo=args.modelo,
        prompt=args.prompt,
        hablantes=hablantes,
        disparo=args.disparo,
        contextos=contextos,
        filas_eventos=filas_eventos,
    )

    print(f"[replay] Corrida completada exitosamente. Salidas en: {salida_dir}")


if __name__ == "__main__":
    main()
