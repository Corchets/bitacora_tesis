#!/usr/bin/env python3
"""Arma semillas.json (cabeza del encoder) desde semillas_manifiesto.json.

El manifiesto va en Git; el texto no (voces de terceros y corpus externo).
Salida por defecto: <entrenamiento>/semillas.json, fuera del repo.

    python armar_semillas.py --entrenamiento /ruta/fuera-de-git/entrenamiento-lab

Espera <entrenamiento>/esport/**/esport_dialogue.*.json y los ASR de YouTube en
artifacts/asr-ent-<id>.json (salida de main.py sobre youtube/ent-<id>-16k.wav).
"""

import argparse
import json
import random
import re
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MANIFIESTO = AQUI / "semillas_manifiesto.json"


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _limpiar(s: str) -> str:
    return s.strip().lstrip(".,; ").strip()


def _sin_marcas_esport(s: str) -> str:
    """Saca falsos comienzos (<den->), desenvuelve rellenos (<%eh> -> eh) y el '=' de alargamiento."""
    s = re.sub(r"<[^<>]*->", "", s)
    s = re.sub(r"<%?([^<>]*)>", r"\1", s).replace("=", "")
    return re.sub(r"\s+", " ", s).strip()


def turnos_youtube(asr_dir: Path, vid: str, ns: list[int], min_chars: int) -> list[str]:
    d = json.loads((asr_dir / f"asr-ent-{vid}.json").read_text(encoding="utf-8"))
    por_n = {t["n"]: _limpiar(t["texto"]) for t in d["turnos"]}
    return [por_n[n] for n in ns if len(por_n.get(n, "")) >= min_chars]


def turnos_esport(raiz: Path, cfg: dict, min_chars: int) -> list[str]:
    todos: list[str] = []
    for f in sorted(raiz.rglob("esport_dialogue.*.json")):
        for t in json.loads(f.read_text(encoding="utf-8"))["turns"]:
            texto = _limpiar(_sin_marcas_esport(t.get("filtered-text") or ""))
            if len(texto) >= max(min_chars, 40):
                todos.append(texto)
    rng = random.Random(cfg["seed"])
    sensibles = [t for t in todos if any(p in _norm(t) for p in cfg["palabras_sensibles"])]
    elegidos = rng.sample(sensibles, cfg["n_con_palabra_sensible"])
    resto = [t for t in todos if t not in set(elegidos)]
    return elegidos + rng.sample(resto, cfg["n_aleatorios"])


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--entrenamiento", required=True, type=Path)
    p.add_argument("--asr", default=AQUI / "artifacts", type=Path)
    p.add_argument("--salida", default=None, type=Path)
    a = p.parse_args()
    m = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    mc = m["min_chars"]
    estafa: list[str] = []
    for vid, ns in m["youtube"]["estafa"].items():
        estafa += turnos_youtube(a.asr, vid, ns, mc)
    legitima: list[str] = []
    for vid, ns in m["youtube"]["legitima"].items():
        legitima += turnos_youtube(a.asr, vid, ns, mc)
    legitima += turnos_esport(a.entrenamiento / "esport", m["esport"], mc)
    salida = a.salida or a.entrenamiento / "semillas.json"
    salida.write_text(
        json.dumps(
            {"estado": m["estado"], "fecha": m["fecha"], "estafa": estafa, "legitima": legitima},
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"{salida}: estafa={len(estafa)} legitima={len(legitima)}")


if __name__ == "__main__":
    main()
