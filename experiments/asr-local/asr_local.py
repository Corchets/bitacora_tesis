#!/usr/bin/env python3
"""Procedimiento repetible de ASR local.

Transcribe audio por bloques emitiendo el contrato compartido en JSONL
(actualizaciones.jsonl), registrando hardware, tiempos, RTF y memoria en
manifiesto.json y generando un resumen en resumen.md.

Uso:
    python asr_local.py <audio.wav> --salida <dir> [--motor sherpa-zipformer|whisper]
                        [--hilos N] [--bloque-ms 100] [--simular-tiempo-real | --rapido]
                        [--referencia <texto.txt>] [--canal A|B]
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

from motores import MotorASR, MotorFasterWhisper, MotorSherpaZipformer
from wer import (
    analizar_errores_clave,
    calcular_cer,
    calcular_wer,
    extraer_texto_referencia,
)


def obtener_memoria_pico_mb() -> float:
    """Devuelve la memoria residente máxima (RSS) del proceso en MB.

    En macOS (Darwin), ru_maxrss se expresa en bytes.
    En Linux, ru_maxrss se expresa en kilobytes.
    """
    uso = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if sys.platform == "darwin":
        return round(uso / (1024.0 * 1024.0), 2)
    return round(uso / 1024.0, 2)


def obtener_info_hardware() -> dict[str, Any]:
    """Recopila información del entorno y hardware disponible."""
    info: dict[str, Any] = {
        "sistema": platform.system(),
        "release": platform.release(),
        "arquitectura": platform.machine(),
        "procesador": platform.processor(),
        "nucleos_cpu": os.cpu_count(),
        "ram_total_gb": None,
    }

    # Intentar obtener RAM total en macOS
    if sys.platform == "darwin":
        try:
            salida = subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True)
            bytes_ram = int(salida.strip())
            info["ram_total_gb"] = round(bytes_ram / (1024**3), 2)
        except Exception:
            pass
    # En Linux leer /proc/meminfo
    elif os.path.exists("/proc/meminfo"):
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        kb = int(line.split()[1])
                        info["ram_total_gb"] = round(kb / (1024**2), 2)
                        break
        except Exception:
            pass

    return info


def obtener_info_git() -> dict[str, Any]:
    """Obtiene hash commit y estado del repositorio Git."""
    try:
        hash_git = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        diff = subprocess.check_output(
            ["git", "status", "--porcelain"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        es_dirty = len(diff) > 0
    except Exception:
        hash_git = "desconocido"
        es_dirty = False

    return {
        "hash": hash_git,
        "dirty": es_dirty,
    }


def obtener_versiones_paquetes() -> dict[str, str]:
    """Obtiene versiones de los paquetes relevantes instalados."""
    versiones = {
        "python": platform.python_version(),
    }
    for pkg in ("sherpa_onnx", "onnxruntime", "faster_whisper", "soundfile", "numpy"):
        try:
            mod = __import__(pkg)
            versiones[pkg] = getattr(mod, "__version__", "disponible")
        except ImportError:
            versiones[pkg] = "no_instalado"
    return versiones


def leer_audio_wav(ruta: str | Path) -> tuple[np.ndarray, int]:
    """Lee un archivo WAV retornando muestras float32 y sample_rate.

    Usa soundfile si está disponible; en caso contrario recurre al módulo estándar wave.
    """
    try:
        import soundfile as sf
        data, sr = sf.read(str(ruta), dtype="float32")
        return data, sr
    except ImportError:
        import wave
        with wave.open(str(ruta), "rb") as wf:
            channels = wf.getnchannels()
            width = wf.getsampwidth()
            sr = wf.getframerate()
            frames = wf.getnframes()
            raw = wf.readframes(frames)
            if width == 2:
                samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
            elif width == 1:
                samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
            elif width == 4:
                samples = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
            else:
                raise ValueError(f"Ancho de muestra no soportado: {width}")
            if channels > 1:
                samples = samples.reshape(-1, channels)
            return samples, sr


def transcribir_audio(
    audio_path: str | Path,
    motor: MotorASR,
    salida_dir: str | Path,
    bloque_ms: int = 100,
    simular_tiempo_real: bool = False,
    llamada_id: str | None = None,
    canal: str | None = None,
    referencia_path: str | Path | None = None,
) -> dict[str, Any]:
    """Ejecuta el reconocimiento local sobre el archivo de audio.

    Escribe actualizaciones.jsonl, manifiesto.json y resumen.md en salida_dir.
    """
    salida_dir = Path(salida_dir)
    salida_dir.mkdir(parents=True, exist_ok=True)
    audio_path = Path(audio_path)

    if llamada_id is None:
        llamada_id = audio_path.stem

    # Leer audio completo
    data, sample_rate = leer_audio_wav(audio_path)
    if data.ndim > 1:
        # Si es multicanal y no se especificó canal, se promedia a mono
        if canal == "A":
            muestras_totales = data[:, 0]
        elif canal == "B" and data.shape[1] > 1:
            muestras_totales = data[:, 1]
        else:
            muestras_totales = np.mean(data, axis=1)
    else:
        muestras_totales = data

    duracion_audio_s = len(muestras_totales) / float(sample_rate)
    tam_bloque_muestras = int((bloque_ms / 1000.0) * sample_rate)

    motor.inicializar()

    ruta_jsonl = salida_dir / "actualizaciones.jsonl"
    ruta_manifiesto = salida_dir / "manifiesto.json"
    ruta_resumen = salida_dir / "resumen.md"

    actualizaciones: list[dict[str, Any]] = []
    meta_motor = motor.metadatos()
    info_hw = obtener_info_hardware()
    info_git = obtener_info_git()
    versiones_pkg = obtener_versiones_paquetes()

    linea_meta = {
        "meta": {
            "motor": motor.nombre,
            "modelo": motor.modelo_id,
            "tipo_entrega": motor.tipo_entrega,
            "es_streaming": motor.es_streaming,
            "sample_rate": sample_rate,
            "bloque_ms": bloque_ms,
            "hardware": info_hw,
            "git": info_git,
            "versiones": versiones_pkg,
        }
    }

    t_inicio_ejecucion = time.perf_counter()
    reloj_reproduccion_s = 0.0
    reloj_sistema_s = 0.0
    tiempo_proceso_acum_s = 0.0
    n_actualizacion = 1

    with open(ruta_jsonl, "w", encoding="utf-8") as f_jsonl:
        f_jsonl.write(json.dumps(linea_meta, ensure_ascii=False) + "\n")

        # Procesamiento por bloques
        num_muestras = len(muestras_totales)
        offset = 0

        while offset < num_muestras:
            fin_offset = min(offset + tam_bloque_muestras, num_muestras)
            bloque = muestras_totales[offset:fin_offset]

            inicio_bloque_s = offset / float(sample_rate)
            fin_bloque_s = fin_offset / float(sample_rate)
            duracion_bloque_s = fin_bloque_s - inicio_bloque_s

            t0_bloque = time.perf_counter()
            eventos = motor.procesar_bloque(bloque, inicio_bloque_s, fin_bloque_s)
            t_proc_bloque = time.perf_counter() - t0_bloque
            tiempo_proceso_acum_s += t_proc_bloque

            # Avance del reloj
            reloj_reproduccion_s = fin_bloque_s
            reloj_sistema_s = max(reloj_sistema_s + t_proc_bloque, reloj_reproduccion_s + t_proc_bloque)

            # Si simular_tiempo_real, dormir la diferencia si el cómputo fue más rápido que el audio
            if simular_tiempo_real:
                demora_restante = duracion_bloque_s - t_proc_bloque
                if demora_restante > 0:
                    time.sleep(demora_restante)

            for ev in eventos:
                disponible_s = round(max(reloj_sistema_s, ev.fin_audio_s + (ev.proceso_ms / 1000.0)), 3)
                act = {
                    "llamada_id": llamada_id,
                    "n": n_actualizacion,
                    "tipo": ev.tipo,
                    "segmento": ev.segmento,
                    "texto": ev.texto,
                    "inicio_audio_s": ev.inicio_audio_s,
                    "fin_audio_s": ev.fin_audio_s,
                    "disponible_s": disponible_s,
                    "proceso_ms": ev.proceso_ms,
                    "canal": canal,
                }
                actualizaciones.append(act)
                f_jsonl.write(json.dumps(act, ensure_ascii=False) + "\n")
                n_actualizacion += 1

            offset = fin_offset

        # Vaciar cola final del motor
        t0_fin = time.perf_counter()
        eventos_finales = motor.vaciar_final(duracion_audio_s)
        t_proc_fin = time.perf_counter() - t0_fin
        tiempo_proceso_acum_s += t_proc_fin
        reloj_sistema_s = max(reloj_sistema_s + t_proc_fin, duracion_audio_s + t_proc_fin)

        for ev in eventos_finales:
            disponible_s = round(max(reloj_sistema_s, ev.fin_audio_s + (ev.proceso_ms / 1000.0)), 3)
            act = {
                "llamada_id": llamada_id,
                "n": n_actualizacion,
                "tipo": ev.tipo,
                "segmento": ev.segmento,
                "texto": ev.texto,
                "inicio_audio_s": ev.inicio_audio_s,
                "fin_audio_s": ev.fin_audio_s,
                "disponible_s": disponible_s,
                "proceso_ms": ev.proceso_ms,
                "canal": canal,
            }
            actualizaciones.append(act)
            f_jsonl.write(json.dumps(act, ensure_ascii=False) + "\n")
            n_actualizacion += 1

    t_total_ejecucion_s = time.perf_counter() - t_inicio_ejecucion
    rtf = round(tiempo_proceso_acum_s / max(0.001, duracion_audio_s), 4)
    memoria_pico_mb = obtener_memoria_pico_mb()

    # Reconstruir transcripción final
    segmentos_finales: dict[int, str] = {}
    for act in actualizaciones:
        if act["tipo"] == "final":
            segmentos_finales[act["segmento"]] = act["texto"]
    texto_transcrito_final = " ".join(texto for _, texto in sorted(segmentos_finales.items()))

    # Métricas de error si hay referencia
    metricas_wer = None
    metricas_cer = None
    reporte_clave = None
    texto_referencia = None

    if referencia_path and os.path.exists(referencia_path):
        texto_referencia = extraer_texto_referencia(str(referencia_path))
        metricas_wer = calcular_wer(texto_referencia, texto_transcrito_final, sin_tildes=True)
        metricas_cer = calcular_cer(texto_referencia, texto_transcrito_final, sin_tildes=True)
        reporte_clave = analizar_errores_clave(texto_referencia, texto_transcrito_final)

    # Manifiesto
    manifiesto = {
        "audio_path": str(audio_path),
        "audio_duracion_s": round(duracion_audio_s, 3),
        "sample_rate": sample_rate,
        "llamada_id": llamada_id,
        "canal": canal,
        "motor": meta_motor,
        "bloque_ms": bloque_ms,
        "modo": "tiempo_real" if simular_tiempo_real else "rapido",
        "duracion_total_ejecucion_s": round(t_total_ejecucion_s, 3),
        "tiempo_proceso_total_s": round(tiempo_proceso_acum_s, 3),
        "rtf": rtf,
        "memoria_pico_mb": memoria_pico_mb,
        "total_actualizaciones": len(actualizaciones),
        "total_parciales": sum(1 for a in actualizaciones if a["tipo"] == "parcial"),
        "total_finales": sum(1 for a in actualizaciones if a["tipo"] == "final"),
        "total_segmentos": len(segmentos_finales),
        "hardware": info_hw,
        "git": info_git,
        "versiones": versiones_pkg,
        "texto_transcrito_final": texto_transcrito_final,
        "evaluacion": {
            "referencia_path": str(referencia_path) if referencia_path else None,
            "texto_referencia": texto_referencia,
            "wer": metricas_wer,
            "cer": metricas_cer,
            "analisis_palabras_clave": reporte_clave,
        },
    }

    with open(ruta_manifiesto, "w", encoding="utf-8") as f_man:
        json.dump(manifiesto, f_man, indent=2, ensure_ascii=False)

    # Resumen Markdown
    generar_resumen_md(ruta_resumen, manifiesto)

    return manifiesto


def generar_resumen_md(ruta_resumen: Path, m: dict[str, Any]) -> None:
    """Genera resumen legible con advertencias metodológicas obligatorias."""
    eval_info = m.get("evaluacion", {})
    wer_info = eval_info.get("wer")
    cer_info = eval_info.get("cer")
    clave_info = eval_info.get("analisis_palabras_clave")

    lineas = [
        "# Resumen de corrida ASR local",
        "",
        "> **ADVERTENCIA: audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09; la corrida de entrega espera las grabaciones de #39.**",
        "",
        "> **Estado: propuesta sin discutir.** Motor propuesto como procedimiento repetible; no cierra D09 "
        "(ver [MAPA-DECISIONES.md](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)).",
        "",
        "## 1. Identificación y Hardware",
        "",
        f"- **Llamada ID:** `{m['llamada_id']}`",
        f"- **Audio fuente:** `{m['audio_path']}`",
        f"- **Duración audio:** {m['audio_duracion_s']} s ({m['sample_rate']} Hz)",
        f"- **Canal:** `{m['canal']}`",
        f"- **Motor:** `{m['motor']['motor']}` (modelo: `{m['motor']['modelo_id']}`)",
        f"- **Streaming:** `{m['motor']['es_streaming']}` | **Entrega:** `{m['motor']['tipo_entrega']}`",
        f"- **Modo de ejecución:** `{m['modo']}` (bloque: {m['bloque_ms']} ms)",
        f"- **Hardware medido:** {m['hardware']['sistema']} {m['hardware']['release']} ({m['hardware']['arquitectura']}) | {m['hardware']['nucleos_cpu']} núcleos | {m['hardware']['ram_total_gb']} GB RAM",
        f"- **Git commit:** `{m['git']['hash']}` {'(con cambios sin commit)' if m['git']['dirty'] else '(limpio)'}",
        "",
        "## 2. Rendimiento y Cómputo",
        "",
        f"- **Tiempo de proceso acumulado:** {m['tiempo_proceso_total_s']} s",
        f"- **RTF (Real-Time Factor):** **{m['rtf']}** (un RTF < 1.0 indica procesamiento más rápido que tiempo real)",
        f"- **Memoria pico (RSS):** **{m['memoria_pico_mb']} MB**",
        f"- **Actualizaciones totales:** {m['total_actualizaciones']} ({m['total_parciales']} parciales, {m['total_finales']} finales)",
        f"- **Segmentos cerrados:** {m['total_segmentos']}",
        "",
        "## 3. Transcripción Final",
        "",
        f"```text\n{m['texto_transcrito_final']}\n```",
        "",
    ]

    if eval_info.get("texto_referencia"):
        lineas.extend([
            "## 4. Comparación con Texto de Referencia",
            "",
            f"- **Texto de referencia:** `{eval_info['referencia_path']}`",
            f"- **WER:** **{wer_info['wer'] * 100:.2f}%** (distancia={wer_info['distancia']}, sub={wer_info['sustituciones']}, del={wer_info['eliminaciones']}, ins={wer_info['inserciones']})",
            f"- **CER:** **{cer_info['cer'] * 100:.2f}%** (distancia={cer_info['distancia']}, sub={cer_info['sustituciones']}, del={cer_info['eliminaciones']}, ins={cer_info['inserciones']})",
            "",
            "### Análisis de palabras clave críticas",
            "",
            "| Palabra clave | En referencia | Encontrada en hipótesis | Estado |",
            "|---|---|---|---|",
        ])
        if clave_info:
            for c in clave_info:
                lineas.append(
                    f"| `{c['palabra_clave']}` | {c['conteo_referencia']} | {'Sí' if c['detectada_en_hipotesis'] else 'No'} | **{c['estado']}** |"
                )
        else:
            lineas.append("| (ninguna palabra clave del catálogo detectada en referencia) | - | - | - |")
        lineas.append("")

    with open(ruta_resumen, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


def crear_motor(
    motor_nombre: str,
    modelo_custom: str | None = None,
    hilos: int = 4,
) -> MotorASR:
    """Instancia el motor seleccionado."""
    if motor_nombre == "sherpa-zipformer":
        modelo = modelo_custom or MotorSherpaZipformer.MODELO_POR_DEFECTO
        return MotorSherpaZipformer(
            modelo_dir_o_repo=modelo,
            hilos=hilos,
        )
    elif motor_nombre == "whisper":
        tamanio = modelo_custom or "base"
        return MotorFasterWhisper(
            modelo_tamanio=tamanio,
            hilos=hilos,
        )
    else:
        raise ValueError(f"Motor no reconocido: {motor_nombre}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Procedimiento repetible de ASR local sobre audio WAV."
    )
    parser.add_argument("audio", help="Ruta al archivo WAV de entrada.")
    parser.add_argument("--salida", required=True, help="Directorio para guardar salidas.")
    parser.add_argument(
        "--motor",
        choices=["sherpa-zipformer", "whisper"],
        default="sherpa-zipformer",
        help="Motor de ASR a utilizar (defecto: sherpa-zipformer).",
    )
    parser.add_argument(
        "--modelo",
        default=None,
        help="Ruta local o repo_id del modelo en Hugging Face (opcional).",
    )
    parser.add_argument(
        "--hilos",
        type=int,
        default=4,
        help="Cantidad de hilos CPU a utilizar (defecto: 4).",
    )
    parser.add_argument(
        "--bloque-ms",
        type=int,
        default=100,
        help="Tamaño de bloque en milisegundos para streaming (defecto: 100).",
    )
    parser.add_argument(
        "--simular-tiempo-real",
        action="store_true",
        help="Simula el paso de tiempo real mediante sleeps entre bloques.",
    )
    parser.add_argument(
        "--rapido",
        action="store_true",
        help="Procesa el audio lo más rápido posible sin esperas (defecto).",
    )
    parser.add_argument(
        "--referencia",
        default=None,
        help="Ruta a archivo de texto de referencia para calcular WER/CER.",
    )
    parser.add_argument(
        "--llamada-id",
        default=None,
        help="Identificador de la llamada (defecto: nombre base del audio).",
    )
    parser.add_argument(
        "--canal",
        choices=["A", "B"],
        default=None,
        help="Canal a procesar ('A' o 'B' para estéreo; null para mono/mezcla).",
    )

    args = parser.parse_args()

    tiempo_real = args.simular_tiempo_real and not args.rapido

    motor = crear_motor(args.motor, modelo_custom=args.modelo, hilos=args.hilos)

    transcribir_audio(
        audio_path=args.audio,
        motor=motor,
        salida_dir=args.salida,
        bloque_ms=args.bloque_ms,
        simular_tiempo_real=tiempo_real,
        llamada_id=args.llamada_id,
        canal=args.canal,
        referencia_path=args.referencia,
    )


if __name__ == "__main__":
    main()
