#!/usr/bin/env python3
"""Mezclador de canales ASR (#19, #28).

Une dos flujos de actualizaciones JSONL (canal A y canal B) en un único flujo
ordenado cronológicamente por `disponible_s`, renumerando `n` secuencialmente
y garantizando segmentos únicos por canal y etiquetas canal = A / B.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def mezclar_flujos(
    actualizaciones_a: list[dict[str, Any]],
    actualizaciones_b: list[dict[str, Any]],
    etiqueta_a: str = "A",
    etiqueta_b: str = "B",
) -> list[dict[str, Any]]:
    """Mezcla dos listas de actualizaciones ASR ordenándolas por `disponible_s` y renumerando `n`.

    - Asegura que cada actualización tenga su etiqueta de canal correspondiente ("A" o "B").
    - Mantiene los segmentos únicos de cada canal sin sobreescribir los del otro.
    - Ordena por `disponible_s` ascendente (desempate estable por `fin_audio_s` y orden original).
    - Renumera el campo `n` de 1 a N.
    """
    combinadas: list[tuple[float, float, int, dict[str, Any]]] = []

    for i, act in enumerate(actualizaciones_a):
        copia = dict(act)
        copia["canal"] = etiqueta_a
        disp = float(copia.get("disponible_s") or 0.0)
        fin = float(copia.get("fin_audio_s") or 0.0)
        combinadas.append((disp, fin, i, copia))

    for i, act in enumerate(actualizaciones_b):
        copia = dict(act)
        copia["canal"] = etiqueta_b
        disp = float(copia.get("disponible_s") or 0.0)
        fin = float(copia.get("fin_audio_s") or 0.0)
        combinadas.append((disp, fin, len(actualizaciones_a) + i, copia))

    # Ordenar por disponible_s ascendente, luego fin_audio_s, luego índice original
    combinadas.sort(key=lambda x: (x[0], x[1], x[2]))

    resultado: list[dict[str, Any]] = []
    for nuevo_n, (_, _, _, act) in enumerate(combinadas, start=1):
        act["n"] = nuevo_n
        resultado.append(act)

    return resultado


def mezclar_archivos_jsonl(
    ruta_a: Path,
    ruta_b: Path,
    ruta_salida: Path,
    etiqueta_a: str = "A",
    etiqueta_b: str = "B",
) -> None:
    """Lee dos archivos JSONL de ASR, los mezcla y escribe el resultado en ruta_salida."""
    meta_a = None
    meta_b = None
    acts_a: list[dict[str, Any]] = []
    acts_b: list[dict[str, Any]] = []

    with open(ruta_a, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            item = json.loads(linea)
            if "meta" in item:
                meta_a = item["meta"]
            else:
                acts_a.append(item)

    with open(ruta_b, "r", encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea:
                continue
            item = json.loads(linea)
            if "meta" in item:
                meta_b = item["meta"]
            else:
                acts_b.append(item)

    mezcladas = mezclar_flujos(acts_a, acts_b, etiqueta_a=etiqueta_a, etiqueta_b=etiqueta_b)

    # Construir cabecera meta combinada
    meta_combinada: dict[str, Any] = {
        "tipo": "mezcla_canales_estereo",
        "canales": [etiqueta_a, etiqueta_b],
        "origen_a": meta_a,
        "origen_b": meta_b,
    }
    if meta_a and "motor" in meta_a:
        meta_combinada["motor"] = meta_a["motor"]
    elif meta_b and "motor" in meta_b:
        meta_combinada["motor"] = meta_b["motor"]

    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_salida, "w", encoding="utf-8") as f_out:
        f_out.write(json.dumps({"meta": meta_combinada}, ensure_ascii=False) + "\n")
        for act in mezcladas:
            f_out.write(json.dumps(act, ensure_ascii=False) + "\n")


def parsear_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Une dos flujos JSONL de ASR (canal A y B) en un único flujo ordenado por disponible_s."
    )
    parser.add_argument("canal_a", type=Path, help="Ruta al JSONL de canal A.")
    parser.add_argument("canal_b", type=Path, help="Ruta al JSONL de canal B.")
    parser.add_argument(
        "-o",
        "--salida",
        type=Path,
        required=True,
        help="Ruta donde guardar el JSONL resultante mezclado.",
    )
    parser.add_argument("--etiqueta-a", default="A", help="Etiqueta para canal A (defecto: 'A').")
    parser.add_argument("--etiqueta-b", default="B", help="Etiqueta para canal B (defecto: 'B').")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parsear_args(argv)
    if not args.canal_a.exists():
        print(f"ERROR: No existe el archivo de canal A: {args.canal_a}", file=sys.stderr)
        return 1
    if not args.canal_b.exists():
        print(f"ERROR: No existe el archivo de canal B: {args.canal_b}", file=sys.stderr)
        return 1

    mezclar_archivos_jsonl(
        ruta_a=args.canal_a,
        ruta_b=args.canal_b,
        ruta_salida=args.salida,
        etiqueta_a=args.etiqueta_a,
        etiqueta_b=args.etiqueta_b,
    )
    print(f"[OK] Flujos mezclados guardados en: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
