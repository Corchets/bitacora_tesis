"""Compara reglas v1 y v2 por grupo (53 históricos vs corpus_v2) con Wilson 95 %.

    python analisis/2026-10-21-reglas-v2/comparar.py CORRIDA_V1 CORRIDA_V2 [--detalle]

Solo lee corridas de la partición de desarrollo. Con --detalle lista, por config,
las falsas alarmas (línea y patrón) y las estafas sin aviso.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SLM = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SLM))

import casos  # noqa: E402
import resumen  # noqa: E402

GRUPOS = {"53 históricos": ("piloto_escrito", "trampa", "laboratorio"), "corpus_v2": ("corpus_v2",)}


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    mitad = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / den
    return (centro - mitad, centro + mitad)


def _fmt(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.0f} %) [{100 * lo:.0f}–{100 * hi:.0f}]"


def cargar(carpeta: str) -> dict[str, dict]:
    man, filas = resumen.leer_corrida(Path(carpeta))
    an = resumen.analizar(man, filas)
    assert len(an) == 1, "se espera una sola configuración"
    return next(iter(an.values()))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("v1")
    p.add_argument("v2")
    p.add_argument("--detalle", action="store_true")
    a = p.parse_args()
    corridas = {"v1": cargar(a.v1), "v2": cargar(a.v2)}
    print("| Grupo | Reglas | Estafas con aviso [Wilson 95 %] | Falsas alarmas [Wilson 95 %] |\n|---|---|---|---|")
    for nombre, grupos in list(GRUPOS.items()) + [("150 desarrollo", sum(GRUPOS.values(), ()))]:
        for v, cs in corridas.items():
            sel = [c for cid, c in cs.items() if casos.cargar_referencia(cid)["grupo"] in grupos]
            vis = [c for c in sel if c["ref"]["clase"] not in casos.LEGITIMAS]
            leg = [c for c in sel if c["ref"]["clase"] in casos.LEGITIMAS]
            print(f"| {nombre} | {v} | {_fmt(sum(c['aviso'] is not None for c in vis), len(vis))} | "
                  f"{_fmt(sum(c['aviso'] is not None for c in leg), len(leg))} |")
    if a.detalle:
        for v, cs in corridas.items():
            print(f"\n## {v}")
            for cid, c in sorted(cs.items()):
                esleg = c["ref"]["clase"] in casos.LEGITIMAS
                if esleg and c["aviso"]:
                    print(f"FA  {cid} L{c['aviso']} | {c['aviso_fila']['motivo']} | {c['aviso_fila']['evidencia']}")
                if not esleg and c["aviso"] is None:
                    print(f"MISS {cid} (T_R={c['ref']['t_r_linea']})")


main()
