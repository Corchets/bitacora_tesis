"""¿`num_batch` 32 cambia las respuestas o solo el tiempo?

Compara una configuración (modelo, prompt, hablantes) entre dos corridas sobre los
mismos casos: respuestas crudas idénticas, misma alerta, mismo aviso por caso y tiempos.

    python analisis/2026-10-21-cache-prefijo/comparar_num_batch.py \\
        corridas/2026-10-17_150516_m1-gguf corridas/<nueva> --config "slm|qwen3.5:0.8b-q8_0|tarea|ab"
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path


def leer(carpeta: Path, config: str) -> dict[tuple[str, int], dict]:
    with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
        return {(r["case_id"], int(r["linea"])): r for r in csv.DictReader(f) if r["config"] == config}


def p(valores: list[float], q: float) -> float:
    valores = sorted(valores)
    return valores[min(len(valores) - 1, round(q * (len(valores) - 1)))]


def primer_aviso(filas: dict, caso: str) -> int | None:
    lineas = sorted(n for c, n in filas if c == caso and filas[(c, n)]["aviso"] == "true")
    return lineas[0] if lineas else None


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("base", type=Path)
    a.add_argument("nueva", type=Path)
    a.add_argument("--config", required=True)
    a.add_argument("--config-nueva", help="si la configuración tiene otro nombre en la corrida nueva")
    args = a.parse_args()
    base, nueva = leer(args.base, args.config), leer(args.nueva, args.config_nueva or args.config)
    comunes = sorted(set(base) & set(nueva))
    casos = sorted({c for c, _ in comunes})
    # Solo casos completos en las dos corridas.
    casos = [c for c in casos if {k for k in base if k[0] == c} == {k for k in nueva if k[0] == c}]
    comunes = [k for k in comunes if k[0] in casos]
    resultado = {
        "base": args.base.name,
        "nueva": args.nueva.name,
        "config": args.config,
        "casos": len(casos),
        "lineas": len(comunes),
        "crudo_identico": sum(base[k]["crudo"] == nueva[k]["crudo"] for k in comunes),
        "misma_alerta": sum(base[k]["alerta_sugerida"] == nueva[k]["alerta_sugerida"] for k in comunes),
        "mismo_riesgo": sum(base[k]["riesgo"] == nueva[k]["riesgo"] for k in comunes),
        "mismo_aviso_por_caso": sum(primer_aviso(base, c) == primer_aviso(nueva, c) for c in casos),
        "casos_con_otro_aviso": [
            {"caso": c, "base": primer_aviso(base, c), "nueva": primer_aviso(nueva, c)}
            for c in casos if primer_aviso(base, c) != primer_aviso(nueva, c)
        ],
        "ms": {},
    }
    for nombre, filas in (("base", base), ("nueva", nueva)):
        ms = [float(filas[k]["ms"]) for k in comunes if filas[k]["ms"]]
        resultado["ms"][nombre] = {"p50": round(statistics.median(ms)), "p95": round(p(ms, 0.95)), "media": round(statistics.mean(ms))}
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
