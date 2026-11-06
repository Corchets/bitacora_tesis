"""Lee las corridas del prompt v5 y las compara con v4. No corre modelos ni lee la reserva.

Sostiene las cifras de corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md.

Uso, desde experiments/slm-directo:
    python -I analizar_v5.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CORRIDAS = RAIZ / "corridas"
V5 = CORRIDAS / "2026-11-05_prompt-v5-tito-sin-indicio"
TITO = "tito-slm-sin-indicio"
FUENTES = {
    # v4 repetida en la tanda de roles: también sigue después del aviso.
    "v4": CORRIDAS / "2026-11-04_tanda-roles-tito-sin-indicio" / "d",
    "v5-maniobras": V5 / "a",
    "v5": V5 / "b",
    "v5-indirectos": V5 / "c",
    "v5-sin-excepcion": V5 / "d",
}
POLITICAS = (("primer aviso", 1, False), ("2 en la llamada", 2, False), ("2 seguidas", 2, True), ("3 en la llamada", 3, False), ("3 seguidas", 3, True))

csv.field_size_limit(10**9)


def leer_csv(archivo: Path, detector: str = TITO, prompt: str | None = None) -> dict[str, list[dict]]:
    casos: dict[str, list[dict]] = defaultdict(list)
    with archivo.open(encoding="utf-8-sig", newline="") as fh:
        for fila in csv.DictReader(fh):
            if fila["detector"] == detector and (prompt is None or fila["prompt"] == prompt):
                casos[fila["case_id"]].append(fila)
    for filas in casos.values():
        filas.sort(key=lambda f: int(f["linea"]))
    return casos


def leer_corridas() -> dict[str, dict[str, list[dict]]]:
    return {nombre: leer_csv(next(carpeta.glob("*/actualizaciones.csv"))) for nombre, carpeta in FUENTES.items()}


def referencias(ids) -> dict[str, dict]:
    return {c: json.loads((RAIZ / "casos" / "referencia" / f"{c}.json").read_text(encoding="utf-8")) for c in ids}


def avisa(filas: list[dict], veces: int, seguidas: bool) -> bool:
    """Simula la política sobre `alerta_sugerida`: alerta en `veces` líneas, seguidas o no."""
    alertas = [f["alerta_sugerida"] == "true" for f in filas]
    if not seguidas:
        return sum(alertas) >= veces
    racha = 0
    for alerta in alertas:
        racha = racha + 1 if alerta else 0
        if racha >= veces:
            return True
    return False


def contar(corrida, ref, veces: int, seguidas: bool, filtro=lambda caso: True) -> tuple[int, int]:
    """(estafas con aviso, falsas alarmas) según la política."""
    con = [c for c in corrida if filtro(c) and avisa(corrida[c], veces, seguidas)]
    estafas = sum(ref[c]["clase"] == "vishing" for c in con)
    return estafas, len(con) - estafas


def main() -> int:
    corridas = leer_corridas()
    ids = sorted(corridas["v4"])
    ref = referencias(ids)
    es_v2 = lambda c: c.startswith("CV2")  # noqa: E731
    con_pedido = lambda c: bool(ref[c].get("t_r_linea"))  # noqa: E731

    print("## Estafas / falsas alarmas por política, los 150\n")
    print("condición |", " | ".join(p[0] for p in POLITICAS))
    for nombre, c in corridas.items():
        print(nombre, "|", " | ".join("%d/%d" % contar(c, ref, v, s) for _, v, s in POLITICAS))

    print("\n## Corpus v2: estafas de 46, con pedido de 36, falsas alarmas de 51\n")
    for nombre, c in corridas.items():
        e, f = contar(c, ref, 1, False, es_v2)
        p, _ = contar(c, ref, 1, False, lambda x: es_v2(x) and con_pedido(x))
        e2, f2 = contar(c, ref, 2, False, es_v2)
        print(f"{nombre}: {e}/{f}, con pedido {p}; con 2 en la llamada {e2}/{f2}")

    print("\n## Cambios contra v4, primer aviso\n")
    base = {c for c in ids if avisa(corridas["v4"][c], 1, False)}
    for nombre, c in corridas.items():
        if nombre == "v4":
            continue
        con = {i for i in ids if avisa(c[i], 1, False)}
        clase = lambda g, e: sorted(i for i in g if (ref[i]["clase"] == "vishing") == e)  # noqa: E731
        print(f"{nombre}: gana {clase(con - base, True)} pierde {clase(base - con, True)}")
        print(f"   agrega FA {clase(con - base, False)} saca FA {clase(base - con, False)}")

    print("\n## Riesgo en la línea del pedido, estafas que ninguna condición avisa\n")
    for caso in sorted(i for i in ids if con_pedido(i) and not any(avisa(c[i], 1, False) for c in corridas.values())):
        tr = ref[caso]["t_r_linea"]
        print(caso, {n: next((f["riesgo"] or "sin consulta" for f in c[caso] if int(f["linea"]) == tr), None) for n, c in corridas.items()})

    print("\n## Controles de maniobras (6 estafas, 12 legítimas)\n")
    archivo = next((V5 / "controles").glob("*/actualizaciones.csv"))
    clases = json.loads((RAIZ / "casos" / "controles-maniobras.json").read_text(encoding="utf-8"))
    for detector in ("slm", TITO):
        for prompt in ("v4", "v5-maniobras", "v5"):
            c = leer_csv(archivo, detector, prompt)
            con = [i for i in c if avisa(c[i], 1, False)]
            print(detector, prompt, "estafas", sum(clases[i]["clase"] == "vishing" for i in con), "legítimas", [i for i in con if clases[i]["clase"] != "vishing"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
