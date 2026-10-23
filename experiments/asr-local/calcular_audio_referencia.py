#!/usr/bin/env python3
"""Calcula la referencia temporal del audio sintético TTS (#19, #28).

El audio TTS se construye concatenando turnos con 1,0 s de silencio. Por lo tanto,
los instantes temporales T_R (inicio del turno del pedido) y T_C (inicio del turno
del cumplimiento) se derivan con exactitud a partir de las duraciones medidas
de cada turno sintetizado.

Guarda los metadatos en experiments/asr-local/audio-referencia/<llamada>.json con:
"origen": "derivado de la construcción del audio TTS, no anotación humana".
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

DIR_ASR = Path(__file__).resolve().parent
DIR_REPO = DIR_ASR.parent.parent
DIR_CASOS_TEXTO = DIR_REPO / "experiments" / "slm-directo" / "casos" / "texto"
DIR_AUDIO_REF = DIR_ASR / "audio-referencia"


CASOS_TTS = [
    {
        "id": "SC-WA-CODE-01-tts",
        "texto": DIR_CASOS_TEXTO / "SC-WA-CODE-01-e01.txt",
        "clase": "vishing",
        "grupo": "piloto_escrito",
        "linea_tr": 4,  # Línea 4: "A: Decime el código de activación..."
        "linea_tc": 5,  # Línea 5: "B: Es cero, cero..."
    },
    {
        "id": "LG-WA-CONSULTA-01-tts",
        "texto": DIR_CASOS_TEXTO / "LG-WA-CONSULTA-01-e01.txt",
        "clase": "legitima_dificil",
        "grupo": "piloto_escrito",
        "linea_tr": None,
        "linea_tc": None,
    },
]


def parsear_dialogo(ruta_txt: Path) -> list[tuple[str, str]]:
    turnos = []
    with open(ruta_txt, "r", encoding="utf-8") as f:
        for linea in f:
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue
            match = re.match(r"^([AB]):\s*(.*)$", linea_limpia)
            if match:
                hablante = match.group(1)
                texto = match.group(2).strip()
                turnos.append((hablante, texto))
            else:
                turnos.append(("A", linea_limpia))
    return turnos


def medir_duracion_turno(texto: str, voz: str, sample_rate: int = 16000) -> float:
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp_aiff:
        tmp_aiff_path = tmp_aiff.name
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        tmp_wav_path = tmp_wav.name

    try:
        subprocess.run(
            ["say", "-v", voz, "-o", tmp_aiff_path, texto],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                tmp_aiff_path,
                "-ar",
                str(sample_rate),
                "-ac",
                "1",
                tmp_wav_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        salida = subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                tmp_wav_path,
            ],
            text=True,
        ).strip()
        return float(salida)
    finally:
        for p in (tmp_aiff_path, tmp_wav_path):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    pass


def calcular_referencia_caso(
    caso_def: dict[str, Any],
    voz_a: str = "Paulina",
    voz_b: str = "Mónica",
    pausa_s: float = 1.0,
    medidor_duracion: Any | None = None,
) -> dict[str, Any]:
    turnos = parsear_dialogo(caso_def["texto"])
    tiempo_actual_s = 0.0
    turnos_info = []

    t_r = None
    t_c = None
    medir_fn = medidor_duracion or medir_duracion_turno

    for i, (hablante, texto) in enumerate(turnos, start=1):
        voz = voz_a if hablante == "A" else voz_b
        dur = medir_fn(texto, voz)

        inicio_s = round(tiempo_actual_s, 3)
        fin_s = round(inicio_s + dur, 3)

        if caso_def["linea_tr"] == i:
            t_r = inicio_s
        if caso_def["linea_tc"] == i:
            t_c = inicio_s

        turnos_info.append({
            "linea": i,
            "hablante": hablante,
            "texto": texto,
            "inicio_s": inicio_s,
            "fin_s": fin_s,
            "duracion_s": round(dur, 3),
        })

        tiempo_actual_s = fin_s
        if i < len(turnos):
            tiempo_actual_s += pausa_s

    total_duracion_s = round(tiempo_actual_s, 3)

    return {
        "case_id": caso_def["id"],
        "clase": caso_def["clase"],
        "grupo": caso_def["grupo"],
        "t_r": t_r,
        "t_c": t_c,
        "duracion_s": total_duracion_s,
        "turnos": turnos_info,
        "origen": "derivado de la construcción del audio TTS, no anotación humana",
    }


def main() -> None:
    DIR_AUDIO_REF.mkdir(parents=True, exist_ok=True)
    print("=== Calculando referencias temporales para audio sintético TTS ===")

    for c in CASOS_TTS:
        print(f"Calculando {c['id']}...")
        ref = calcular_referencia_caso(c)
        ruta_salida = DIR_AUDIO_REF / f"{c['id']}.json"
        ruta_salida.write_text(json.dumps(ref, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  -> Guardado: {ruta_salida}")
        print(f"     T_R: {ref['t_r']} s | T_C: {ref['t_c']} s | Duración: {ref['duracion_s']} s")

    print("[OK] Referencias temporales generadas con éxito.")


if __name__ == "__main__":
    main()
