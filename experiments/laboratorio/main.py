#!/usr/bin/env python3
"""Corrida #29: entra, procesa, escribe JSON, termina.

Audio (--wav, defecto): replay en streaming con Zipformer.
Texto (--texto): reglas + TF-IDF + contador sobre transcripto, sin ASR.
"""

import argparse
import json
import os
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from config import cargar_gama  # noqa: E402
from pipeline import correr, correr_texto  # noqa: E402
from report import armar, guardar  # noqa: E402


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Spike de laboratorio, config por gama.")
    p.add_argument("--wav", default="/data/llamada.wav", help="WAV 16kHz mono (fuera de Git)")
    p.add_argument("--texto", default=None, help="Transcripto: una linea = un turno")
    p.add_argument("--salida", default=None, help="Defecto: artifacts/corrida[.texto].json")
    p.add_argument("--gama", default=None, help="baja|media|alta (defecto: env GAMA o alta)")
    p.add_argument("--semillas", default=str(AQUI / "semillas.json"))
    p.add_argument("--modelos", default=os.environ.get("MODELOS_DIR", "/models/hf"))
    p.add_argument("--chunk-ms", type=int, default=300)
    p.add_argument("--umbral", type=float, default=0.5, help="Umbral goteo, de spike")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    gama = cargar_gama(args.gama)
    if args.texto:
        resultado = correr_texto(
            txt_path=args.texto, semillas_path=args.semillas, umbral_goteo=args.umbral
        )
        entrada, chunk_ms = args.texto, None
        defecto = AQUI / "artifacts" / "corrida-texto.json"
    else:
        if not Path(args.wav).is_file():
            raise SystemExit(
                f"No hay WAV en {args.wav}. Corre con WAV=/ruta/a/llamada.wav "
                "(16kHz mono, fuera de Git) o usa --texto para modo transcripto."
            )
        resultado = correr(
            wav=args.wav,
            gama=gama,
            semillas_path=args.semillas,
            modelos_dir=args.modelos,
            chunk_ms=args.chunk_ms,
            umbral_goteo=args.umbral,
        )
        entrada, chunk_ms = args.wav, args.chunk_ms
        defecto = AQUI / "artifacts" / "corrida.json"
    reporte = armar(gama, resultado, entrada, f"GAMA={gama.nombre} " + " ".join(sys.argv), chunk_ms)
    ruta = guardar(reporte, args.salida or defecto)
    print(json.dumps(reporte, indent=2, ensure_ascii=False))
    print(f"\nGuardado en {ruta}", file=sys.stderr)


if __name__ == "__main__":
    main()
