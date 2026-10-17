#!/usr/bin/env python3
"""Generador de audio sintético de humo para el par H1.

Lee los diálogos de texto en experiments/slm-directo/casos/texto/
y genera archivos WAV de 16 kHz mono (y opcionalmente estéreo A/B)
utilizando el comando del sistema macOS `say` con voces en español
(Paulina para A, Mónica para B) y ffmpeg para resampling.

Los archivos generados se guardan en experiments/asr-local/audio/
(carpeta fuera de Git e ignorada por *.wav).
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import tempfile
from pathlib import Path


CASOS_DEFECTO = [
    {
        "id": "SC-WA-CODE-01-tts",
        "texto_path": "experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt",
    },
    {
        "id": "LG-WA-CONSULTA-01-tts",
        "texto_path": "experiments/slm-directo/casos/texto/LG-WA-CONSULTA-01-e01.txt",
    },
]


def parsear_dialogo(ruta_txt: Path) -> list[tuple[str, str]]:
    """Lee un archivo de diálogo y retorna lista de (hablante, texto)."""
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
                # Si no tiene prefijo, asumir hablante A
                turnos.append(("A", linea_limpia))
    return turnos


def sintetizar_turno(
    texto: str,
    voz: str,
    salida_wav: Path,
    sample_rate: int = 16000,
) -> float:
    """Sintetiza un turno con `say` y lo convierte a WAV 16kHz mono con ffmpeg.

    Retorna la duración en segundos del audio generado.
    """
    with tempfile.NamedTemporaryFile(suffix=".aiff", delete=False) as tmp_aiff:
        tmp_aiff_path = tmp_aiff.name

    try:
        # Generar con say
        subprocess.run(
            ["say", "-v", voz, "-o", tmp_aiff_path, texto],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Convertir a WAV mono 16 kHz
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
                str(salida_wav),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    finally:
        if os.path.exists(tmp_aiff_path):
            os.remove(tmp_aiff_path)

    # Medir duración
    duracion = float(
        subprocess.check_output(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(salida_wav),
            ],
            text=True,
        ).strip()
    )
    return duracion


def crear_silencio_wav(duracion_s: float, salida_wav: Path, sample_rate: int = 16000) -> None:
    """Crea un archivo WAV con silencio."""
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=r={sample_rate}:cl=mono",
            "-t",
            str(duracion_s),
            str(salida_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def generar_audio_caso(
    caso_id: str,
    texto_path: Path,
    salida_dir: Path,
    voz_a: str = "Paulina",
    voz_b: str = "Mónica",
    pausa_turno_s: float = 0.8,
    generar_estereo: bool = True,
) -> dict[str, Path]:
    """Genera audio WAV mono y opcionalmente estéreo para un caso."""
    turnos = parsear_dialogo(texto_path)
    salida_dir.mkdir(parents=True, exist_ok=True)

    ruta_mono = salida_dir / f"{caso_id}.wav"
    ruta_estereo = salida_dir / f"{caso_id}-estereo.wav"

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        partes_mono: list[Path] = []
        partes_canal_a: list[Path] = []
        partes_canal_b: list[Path] = []

        silencio_entre_turnos = tmp_path / "silencio_pausa.wav"
        crear_silencio_wav(pausa_turno_s, silencio_entre_turnos)

        for i, (hablante, texto) in enumerate(turnos):
            voz = voz_a if hablante == "A" else voz_b
            turno_wav = tmp_path / f"turno_{i}_{hablante}.wav"
            duracion = sintetizar_turno(texto, voz, turno_wav)

            # Para mono concatenado
            partes_mono.append(turno_wav)
            if i < len(turnos) - 1:
                partes_mono.append(silencio_entre_turnos)

            # Para estéreo separado por canal
            if hablante == "A":
                partes_canal_a.append(turno_wav)
                silencio_b = tmp_path / f"silencio_b_{i}.wav"
                crear_silencio_wav(duracion, silencio_b)
                partes_canal_b.append(silencio_b)
            else:
                silencio_a = tmp_path / f"silencio_a_{i}.wav"
                crear_silencio_wav(duracion, silencio_a)
                partes_canal_a.append(silencio_a)
                partes_canal_b.append(turno_wav)

            if i < len(turnos) - 1:
                partes_canal_a.append(silencio_entre_turnos)
                partes_canal_b.append(silencio_entre_turnos)

        # Concatenar mono con ffmpeg concat demuxer
        concat_txt = tmp_path / "concat_mono.txt"
        with open(concat_txt, "w") as f:
            for p in partes_mono:
                f.write(f"file '{p.resolve()}'\n")

        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_txt),
                "-c",
                "copy",
                str(ruta_mono),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        if generar_estereo:
            # Concatenar track A
            concat_a = tmp_path / "concat_a.txt"
            with open(concat_a, "w") as f:
                for p in partes_canal_a:
                    f.write(f"file '{p.resolve()}'\n")
            track_a = tmp_path / "track_a.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_a), "-c", "copy", str(track_a)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Concatenar track B
            concat_b = tmp_path / "concat_b.txt"
            with open(concat_b, "w") as f:
                for p in partes_canal_b:
                    f.write(f"file '{p.resolve()}'\n")
            track_b = tmp_path / "track_b.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_b), "-c", "copy", str(track_b)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # Unir track A (canal 0) y track B (canal 1) en estéreo
            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(track_a),
                    "-i",
                    str(track_b),
                    "-filter_complex",
                    "[0:a][1:a]join=inputs=2:channel_layout=stereo[a]",
                    "-map",
                    "[a]",
                    "-ar",
                    "16000",
                    str(ruta_estereo),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

    salidas = {"mono": ruta_mono}
    if generar_estereo:
        salidas["estereo"] = ruta_estereo
    return salidas


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera audio sintético TTS para pruebas de ASR.")
    parser.add_argument(
        "--salida-dir",
        default="experiments/asr-local/audio",
        help="Directorio de salida para los audios (defecto: experiments/asr-local/audio).",
    )
    parser.add_argument("--voz-a", default="Paulina", help="Voz macOS para hablante A (defecto: Paulina).")
    parser.add_argument("--voz-b", default="Mónica", help="Voz macOS para hablante B (defecto: Mónica).")
    parser.add_argument(
        "--pausa-s",
        type=float,
        default=0.8,
        help="Pausa de silencio en segundos entre turnos (defecto: 0.8).",
    )
    parser.add_argument(
        "--sin-estereo",
        action="store_true",
        help="No generar versiones estéreo de dos canales.",
    )

    args = parser.parse_args()
    salida_dir = Path(args.salida_dir)

    print("=== Generando audios sintéticos TTS con macOS `say` y ffmpeg ===")
    print(f"Voces: Hablante A = {args.voz_a} | Hablante B = {args.voz_b}")
    print(f"Directorio de salida: {salida_dir}")

    for caso in CASOS_DEFECTO:
        txt_path = Path(caso["texto_path"])
        if not txt_path.exists():
            print(f"ADVERTENCIA: Archivo no encontrado: {txt_path}")
            continue

        print(f"\nSintetizando caso: {caso['id']} desde {txt_path}...")
        rutas = generar_audio_caso(
            caso_id=caso["id"],
            texto_path=txt_path,
            salida_dir=salida_dir,
            voz_a=args.voz_a,
            voz_b=args.voz_b,
            pausa_turno_s=args.pausa_s,
            generar_estereo=not args.sin_estereo,
        )
        print(f"  -> Generado mono: {rutas['mono']}")
        if "estereo" in rutas:
            print(f"  -> Generado estéreo (canal A/B): {rutas['estereo']}")

    print("\n[OK] Síntesis finalizada.")


if __name__ == "__main__":
    main()
