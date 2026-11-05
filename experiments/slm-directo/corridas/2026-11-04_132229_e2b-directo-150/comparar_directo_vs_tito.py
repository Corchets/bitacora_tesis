"""Compara caso por caso SLM solo contra Tito→SLM (mismo modelo, prompt y máquina).

Uso, desde experiments/slm-directo:
    python corridas/2026-11-04_132229_e2b-directo-150/comparar_directo_vs_tito.py \
        corridas/2026-11-04_132229_e2b-directo-150 corridas/2026-11-04_003715_e2b-tito-viejo-150

Solo lee los CSV y las referencias; no corre modelos.
"""
import collections
import csv
import hashlib
import json
import re
import statistics
import sys
from pathlib import Path

def cargar(carpeta, detector, permitidos):
    filas = collections.defaultdict(list)
    with open(Path(carpeta) / "actualizaciones.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["case_id"] not in permitidos:
                raise ValueError("CSV con un ID ajeno al manifiesto de desarrollo")
            if r["detector"] == detector:
                filas[r["case_id"]].append(r)
    for v in filas.values():
        v.sort(key=lambda r: int(r["linea"]))
    return filas


def datos(dir_directo, dir_tito, raiz=None):
    """Lista permitida desde manifiestos; nunca enumera casos ni abre el catálogo."""
    raiz = Path(raiz) if raiz is not None else Path(__file__).resolve().parents[2]
    manifiestos = [json.loads((Path(d) / "manifiesto.json").read_text(encoding="utf-8"))
                   for d in (dir_directo, dir_tito)]
    for m in manifiestos:
        if m.get("particion") != "desarrollo" or m.get("interrumpida") is not False:
            raise ValueError("Se requieren corridas completas de desarrollo")
        if not m["casos"] or any(
            cid.startswith("CV2-T") or not re.fullmatch(r"[A-Za-z0-9_-]+", cid)
            for cid in m["casos"]
        ):
            raise ValueError("Manifiesto con reserva o ID inseguro; no se abre ningún caso")
    if manifiestos[0]["casos"] != manifiestos[1]["casos"]:
        raise ValueError("Las corridas no tienen los mismos IDs y huellas")
    ids = manifiestos[0]["casos"]
    d = cargar(dir_directo, "slm", ids)
    t = cargar(dir_tito, "tito-slm", ids)
    if set(d) != set(ids) or set(t) != set(ids):
        raise ValueError("Faltan casos de una condición en el CSV")
    referencias = {}
    for cid, huella in ids.items():
        texto = (raiz / "casos" / "texto" / f"{cid}.txt").read_text(encoding="utf-8")
        if hashlib.sha256(texto.encode("utf-8")).hexdigest()[:16] != huella:
            raise ValueError(f"Texto distinto al ejecutado: {cid}")
        ref = json.loads((raiz / "casos" / "referencia" / f"{cid}.json").read_text(encoding="utf-8"))
        if ref.get("particion", "desarrollo") != "desarrollo" or ref["case_id"] != cid:
            raise ValueError("Referencia ajena al desarrollo identificado")
        referencias[cid] = ref
    return d, t, referencias


def aviso(filas):
    return next((int(r["linea"]) for r in filas if r["aviso"] == "true"), None)


def main(dir_directo, dir_tito):
    d, t, referencias = datos(dir_directo, dir_tito)
    casos_ = []
    for cid, ref in sorted(referencias.items()):
        act = next((int(r["linea"]) for r in t[cid] if r["consulta"] != "omitida"), None)
        casos_.append(dict(cid=cid, clase=ref["clase"], grupo=ref["grupo"], tr=ref["t_r_linea"],
                           ad=aviso(d[cid]), at=aviso(t[cid]), act=act))
    V = [c for c in casos_ if c["clase"] == "vishing"]
    L = [c for c in casos_ if c["clase"] != "vishing"]
    print("Estafas con aviso: solo", sum(bool(c["ad"]) for c in V), "· Tito", sum(bool(c["at"]) for c in V), "de", len(V))
    for cl in ("legitima", "legitima_dificil"):
        g = [c for c in L if c["clase"] == cl]
        print(f"Falsas alarmas {cl}: solo", sum(bool(c["ad"]) for c in g), "· Tito", sum(bool(c["at"]) for c in g), "de", len(g))
    for nombre, filas in (("solo", d), ("Tito", t)):
        todas = [r for grupo in filas.values() for r in grupo]
        consultas = [r for r in todas if r["consulta"] != "omitida"]
        print(nombre, "líneas", len(todas), "consultas", len(consultas),
              "p50 SLM ms", statistics.median(float(r["slm_ms"]) for r in consultas))
    perdidas_ambas = [c for c in V if not c["ad"] and not c["at"]]
    print("Perdidas por ambos: con T_R", sum(c["tr"] is not None for c in perdidas_ambas),
          "· sin T_R", sum(c["tr"] is None for c in perdidas_ambas))
    ambos = [c for c in V if c["ad"] and c["at"]]
    print("Ambos avisan:", len(ambos), collections.Counter(
        "solo antes" if c["ad"] < c["at"] else "igual" if c["ad"] == c["at"] else "Tito antes" for c in ambos))
    adel = [c["at"] - c["ad"] for c in ambos if c["ad"] < c["at"]]
    if adel:
        print("  adelanto medio del SLM solo:", round(statistics.mean(adel), 1), "líneas")
    act = collections.Counter(
        "nunca" if c["act"] is None else "antes" if c["act"] < c["tr"] else "en" if c["act"] == c["tr"] else "después"
        for c in V if c["tr"])
    print("Activación de Tito respecto de T_R:", dict(act))
    print("\nSolo el SLM solo detecta:", [c["cid"] for c in V if c["ad"] and not c["at"]])
    print("Solo Tito→SLM detecta:", [c["cid"] for c in V if c["at"] and not c["ad"]])
    print("Ninguno detecta:", [c["cid"] for c in V if not c["ad"] and not c["at"]])
    print("Falsas alarmas solo del SLM solo:", [c["cid"] for c in L if c["ad"] and not c["at"]])
    print("Falsas alarmas solo de Tito→SLM:", [c["cid"] for c in L if c["at"] and not c["ad"]])
    # Misma línea consultada en ambas: ¿cambia la respuesta del SLM?
    dl = {(r["case_id"], r["linea"]): r for v in d.values() for r in v}
    cambio = collections.Counter()
    for v in t.values():
        for r in v:
            k = (r["case_id"], r["linea"])
            if r["consulta"] == "slm_valida" and k in dl:
                cls = "vishing" if referencias[k[0]]["clase"] == "vishing" else "legítima"
                cambio[(cls, dl[k]["alerta_sugerida"], r["alerta_sugerida"])] += 1
    print("\nLíneas consultadas en ambas (clase, alerta solo, alerta Tito):")
    for k, n in sorted(cambio.items()):
        print(" ", k, n)


if __name__ == "__main__":
    main(*sys.argv[1:3])
