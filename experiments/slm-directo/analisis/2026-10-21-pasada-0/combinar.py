"""Pasada 0 hacia 95/5: combinar lo que ya está guardado, sin correr modelos.

Prueba, sobre las corridas completas de los 150 de desarrollo:
- cada detector solo, con condición (`alerta_sugerida` y riesgo ≥ τ, o solo riesgo ≥ τ)
  y persistencia k (líneas seguidas);
- pares de detectores: Y (los dos disparan en la misma línea) y O (cualquiera).

Para no elegir y medir sobre lo mismo, corpus_v2 se parte en dos mitades fijas (A y B,
por SHA-256 del case_id, balanceadas por clase). Se elige mirando los 53 históricos + A y
se informa B. Regla de elección: el mayor recall con falsas alarmas ≤ presupuesto en la
selección (5, 10 y 20 %), para ver la curva y no solo el punto de la meta.

    python analisis/2026-10-21-pasada-0/combinar.py

> **Estado: propuesta sin discutir.** La meta 95/5, la partición A/B y la regla de elección
> son propuestas (D08). Todo es desarrollo: no reemplaza el test reservado.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))

import casos  # noqa: E402

CORRIDAS = SLM / "corridas"


def _ultima(patron: str) -> str | None:
    hay = sorted(p.name for p in CORRIDAS.glob(patron) if (p / "actualizaciones.csv").exists())
    return hay[-1] if hay else None


# nombre: (carpeta, config). Los que no estén completos en los 150 se saltean.
DETECTORES = {
    "reglas v1": ("2026-10-21_200147_m1-reglas-150", "reglas"),
    "reglas v2": ("2026-10-21_201914_m1-reglas-v2-150", "reglas_v2"),
    "0.8B v1": (_ultima("*_m1-0.8b-v1v2-nb32"), "slm|qwen3.5:0.8b-q8_0|tarea|ab"),
    "0.8B v2": (_ultima("*_m1-0.8b-v1v2-nb32"), "slm|qwen3.5:0.8b-q8_0|v2|ab"),
    "2B v1": (_ultima("*_m1-2b-v1v2-nb32"), "slm|qwen3.5:2b-q8_0|tarea|ab"),
    "2B v2": (_ultima("*_m1-2b-v1v2-nb32"), "slm|qwen3.5:2b-q8_0|v2|ab"),
    "4B v1": (_ultima("*_m1-4b-v1v2-nb32"), "slm|qwen3.5:4b-q4_K_M|tarea|ab"),
    "4B v2": (_ultima("*_m1-4b-v1v2-nb32"), "slm|qwen3.5:4b-q4_K_M|v2|ab"),
}
TAUS = [round(0.05 * i, 2) for i in range(21)]
KS = (1, 2, 3)
PRESUPUESTOS = (0.05, 0.10, 0.20)


def cargar(carpeta: str, config: str, ids: list[str]) -> dict | None:
    """case_id -> lista por línea de (dispara_alerta, riesgo), o None si falta algún caso."""
    por_caso: dict[str, dict[int, tuple[bool, float]]] = {}
    with (CORRIDAS / carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["config"] != config:
                continue
            valida = r["valida"] == "true"
            alerta = valida and r["alerta_sugerida"] == "true"
            riesgo = float(r["riesgo"]) if valida and r["riesgo"] else (1.0 if alerta else 0.0)
            por_caso.setdefault(r["case_id"], {})[int(r["linea"])] = (alerta, riesgo)
    salida = {}
    for cid in ids:
        n = len(casos.cargar_texto(cid))
        lineas = por_caso.get(cid, {})
        if len(lineas) != n:
            return None
        salida[cid] = [lineas[i] for i in sorted(lineas)]
    return salida


def politicas(es_slm: bool) -> list[tuple]:
    if not es_slm:
        return [("alerta", 0.0)]
    return [(b, t) for b in ("alerta", "riesgo") for t in TAUS if not (b == "riesgo" and t == 0)]


def senal(datos: dict, pol: tuple) -> dict[str, list[bool]]:
    base, tau = pol
    return {c: [(a or base == "riesgo") and r >= tau for a, r in filas] for c, filas in datos.items()}


def aviso(linea_ok: list[bool], k: int) -> int | None:
    racha = 0
    for i, ok in enumerate(linea_ok, 1):
        racha = racha + 1 if ok else 0
        if racha >= k:
            return i
    return None


def medir(sen: dict[str, list[bool]], k: int, ids: list[str], refs: dict) -> dict:
    tp = nv = fp = nl = tp_p = nv_p = 0
    for c in ids:
        a = aviso(sen[c], k)
        if refs[c]["clase"] == "vishing":
            nv += 1
            tp += a is not None
            if refs[c].get("t_r_linea"):
                nv_p += 1
                tp_p += a is not None
        else:
            nl += 1
            fp += a is not None
    return {"tp": tp, "nv": nv, "fp": fp, "nl": nl, "tp_p": tp_p, "nv_p": nv_p,
            "rec": tp / nv if nv else 0, "fa": fp / nl if nl else 0}


def wilson(k: int, n: int, z: float = 1.96) -> str:
    if not n:
        return "—"
    p, d = k / n, 1 + z * z / n
    c, m = p + z * z / (2 * n), z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return f"{100 * max(0, (c - m) / d):.0f}–{100 * min(1, (c + m) / d):.0f} %"


def mitades(ids: list[str], refs: dict) -> tuple[list[str], list[str]]:
    a, b = [], []
    for clase in ("vishing", "legitima"):
        grupo = sorted((c for c in ids if (refs[c]["clase"] == "vishing") == (clase == "vishing")),
                       key=lambda c: hashlib.sha256(c.encode()).hexdigest())
        a += grupo[0::2]
        b += grupo[1::2]
    return a, b


def elegir(candidatos: list[dict], presupuesto: float) -> dict | None:
    ok = [x for x in candidatos if x["sel"]["fa"] <= presupuesto]
    return max(ok, key=lambda x: (x["sel"]["rec"], -x["sel"]["fa"], -x["piezas"])) if ok else None


def main() -> int:
    ids = casos.ids_de_casos(particion="desarrollo")
    refs = {c: casos.cargar_referencia(c) for c in ids}
    hist = [c for c in ids if refs[c]["grupo"] != "corpus_v2"]
    a, b = mitades([c for c in ids if refs[c]["grupo"] == "corpus_v2"], refs)
    sel = hist + a

    datos = {}
    for nombre, (carpeta, config) in DETECTORES.items():
        d = cargar(carpeta, config, ids) if carpeta else None
        if d is None:
            print(f"(salteo {nombre}: corrida incompleta o inexistente)")
            continue
        datos[nombre] = d
    print(f"Detectores completos: {', '.join(datos)}")
    print(f"Selección: 53 históricos + mitad A ({len(a)}); verificación: mitad B ({len(b)}).\n")

    # Señales por detector y política; se guardan las de la frontera de selección para combinar.
    senales, solos = {}, []
    for nombre, d in datos.items():
        es_slm = not nombre.startswith("reglas")
        for pol in politicas(es_slm):
            s = senal(d, pol)
            senales[(nombre, pol)] = s
            for k in KS:
                solos.append({"desc": f"{nombre} · {pol[0]} ≥ {pol[1]:.2f} · k={k}", "sen": s, "k": k, "piezas": 1,
                              "sel": medir(s, k, sel, refs)})

    def frontera(xs: list[dict], n: int = 6) -> list:
        xs = sorted(xs, key=lambda x: (-x["sel"]["rec"], x["sel"]["fa"]))
        salida, mejor_fa = [], 2.0
        for x in xs:
            if x["sel"]["fa"] < mejor_fa:
                salida.append(x)
                mejor_fa = x["sel"]["fa"]
        return salida[:n] if len(salida) <= n else salida[:: max(1, len(salida) // n)][:n]

    por_detector = {}
    for x in solos:
        if x["k"] == 1:
            por_detector.setdefault(x["desc"].split(" · ")[0], []).append(x)
    base = {n: frontera(xs) for n, xs in por_detector.items()}

    combos = []
    for (n1, xs1), (n2, xs2) in itertools.combinations(base.items(), 2):
        for x1, x2 in itertools.product(xs1, xs2):
            for op, f in (("Y", lambda p, q: p and q), ("O", lambda p, q: p or q)):
                s = {c: [f(p, q) for p, q in zip(x1["sen"][c], x2["sen"][c])] for c in ids}
                for k in (1, 2):
                    d1, d2 = x1["desc"].rsplit(" · k=", 1)[0], x2["desc"].rsplit(" · k=", 1)[0]
                    combos.append({"desc": f"({d1}) {op} ({d2}) · k={k}", "sen": s, "k": k, "piezas": 2,
                                   "sel": medir(s, k, sel, refs)})

    filas = []
    for pres in PRESUPUESTOS:
        for nombre in datos:
            mios = [x for x in solos if x["desc"].startswith(nombre + " ·")]
            filas.append((f"FA ≤ {pres:.0%} · {nombre}", elegir(mios, pres)))
        filas.append((f"FA ≤ {pres:.0%} · **mejor de todo**", elegir(solos + combos, pres)))
    filas = [(t, x) for t, x in filas if x and x["sel"]["tp"]]

    print("| Elección | Configuración | Selección: estafas / FA | Mitad B: estafas (IC 95 %) | Mitad B: con pedido | Mitad B: FA (IC 95 %) |")
    print("|---|---|---|---|---|---|")
    salida = []
    for titulo, x in filas:
        v = medir(x["sen"], x["k"], b, refs)
        s = x["sel"]
        print(f"| {titulo} | {x['desc']} | {s['tp']}/{s['nv']} · {s['fp']}/{s['nl']} | "
              f"{v['tp']}/{v['nv']} ({wilson(v['tp'], v['nv'])}) | {v['tp_p']}/{v['nv_p']} | "
              f"{v['fp']}/{v['nl']} ({wilson(v['fp'], v['nl'])}) |")
        salida.append({"eleccion": titulo, "config": x["desc"], "seleccion": s, "mitad_b": v})
    alcanza = [x for x in combos + solos if x["sel"]["fa"] <= 0.05 and x["sel"]["rec"] >= 0.95]
    print(f"\nConfiguraciones con ≥ 95 % y ≤ 5 % en la selección: {len(alcanza)} de {len(solos) + len(combos)}.")
    (AQUI / "combinar.json").write_text(json.dumps({"mitad_a": a, "mitad_b": b, "filas": salida},
                                                   ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
