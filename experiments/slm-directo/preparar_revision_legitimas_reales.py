"""Fichas ciegas de las 33 legítimas reales de CallCenterEN, con la política de producto de #143.

Uso desde la raíz, con la carpeta `sets/` de la custodia en data/private/legitimas-reales/sets (la fuente prohíbe
redistribuir los textos: no van a Git):
    python3 experiments/slm-directo/preparar_revision_legitimas_reales.py fichas
    python3 experiments/slm-directo/preparar_revision_legitimas_reales.py etiquetas data/private/REVISION-LEGITIMAS-REALES-….json

`fichas` escribe el formulario y la clave en data/private/. El formulario no lleva identificadores, referencia, tipo
de legítima ni nada de las corridas: se completa sin saber en cuáles avisó el detector.
`etiquetas` pasa las respuestas al formato de etiquetas-producto.json (corridas/2026-11-10_revision-producto/), que
lee `corridas/2026-11-12_evaluacion-final/analizar.py --anotacion-legitimas`: solo las «no_avisar» cuentan como FA.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPO = BASE.parents[1]
sys.path.insert(0, str(BASE))
from conjuntos import MANIFIESTO_LEGITIMAS, _leer_congelado  # noqa: E402

PRIVADO = REPO / "data/private"
SETS = PRIVADO / "legitimas-reales/sets"
PLANTILLA = BASE / "analisis/tablero/revision_legitimas_reales_plantilla.html"
FORMULARIO = PRIVADO / "REVISION-LEGITIMAS-REALES.html"
CLAVE = PRIVADO / "CLAVE-REVISION-LEGITIMAS-REALES.json"
ISSUE = "52-legitimas-reales"
SEMILLA = 52
ETIQUETAS = {"no_avisar", "tolerable", "avisar"}


def sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def conservar(ruta: Path, contenido: str) -> None:
    if ruta.exists() and ruta.read_text(encoding="utf-8") != contenido:
        raise ValueError(f"No se reemplaza una entrega diferente: {ruta}")
    ruta.write_text(contenido, encoding="utf-8")
    ruta.chmod(0o600)


def fichas(sets: Path, manifiesto: Path, privado: Path) -> str:
    ids, textos, roles, _, _ = _leer_congelado(sets / "set-legitimas", manifiesto, "set-legitimas")
    orden = sorted(ids)
    random.Random(SEMILLA).shuffle(orden)
    publico, clave = [], {}
    for n, cid in enumerate(orden, 1):
        alias = f"Llamada {n:02d}"
        lineas, protegida = textos[cid].splitlines(), roles[cid]["protegida"]
        turnos = []
        for linea in lineas:
            hablante, texto = linea.split(": ", 1)
            if hablante not in ("A", "B"):
                raise ValueError(f"Turno inválido en {alias}")
            turnos.append({"hablante": "PROTEGIDA" if hablante == protegida else "OTRA", "texto": texto})
        publico.append({"id": alias, "turnos": turnos})
        clave[alias] = {"case_id": cid, "protegida_original": protegida, "texto_sha256": sha(textos[cid])}
    muestra = sha(json.dumps(publico, ensure_ascii=False, sort_keys=True))
    privado.mkdir(parents=True, exist_ok=True)
    # La clave se conserva antes de escribir el formulario, para no perder la correspondencia.
    conservar(privado / CLAVE.name, json.dumps({"issue": ISSUE, "semilla": SEMILLA, "muestra": muestra,
                                                "manifiesto_sha256": hashlib.sha256(manifiesto.read_bytes()).hexdigest(),
                                                "casos": clave}, ensure_ascii=False, indent=2) + "\n")
    # Los textos nunca se interpretan como HTML; escapar '<' también protege el bloque JSON.
    paquete = json.dumps({"issue": ISSUE, "version": 1, "muestra": muestra, "casos": publico},
                         ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    html = PLANTILLA.read_text(encoding="utf-8").replace("__DATOS_REVISION__", paquete)
    if any(c in html for c in ids):
        raise ValueError("Se filtró un identificador original al formulario.")
    conservar(privado / FORMULARIO.name, html)
    return muestra


def etiquetas(respuestas: Path, clave: Path) -> dict:
    r, k = (json.loads(p.read_text(encoding="utf-8")) for p in (respuestas, clave))
    if r.get("issue") != ISSUE or r.get("muestra") != k["muestra"]:
        raise ValueError("Las respuestas son de otra muestra.")
    faltan = sorted(set(k["casos"]) - {a for a, v in r["respuestas"].items() if v.get("completa")})
    if faltan:
        raise ValueError(f"Faltan {len(faltan)} fichas completas: {', '.join(faltan)}")
    casos = {}
    for alias, v in sorted(r["respuestas"].items(), key=lambda x: k["casos"][x[0]]["case_id"]):
        if v["etiqueta"] not in ETIQUETAS:
            raise ValueError(f"{alias}: etiqueta desconocida {v['etiqueta']!r}")
        casos[k["casos"][alias]["case_id"]] = {
            "etiqueta": v["etiqueta"], "intencion": v["intencion"], "pide": v["pide"],
            "linea": int(v["etiqueta_linea"]) if v["etiqueta_linea"] else None, "razon": v["razon"].strip(),
            "roles": v["roles"], "legitima": v["legitima"], "conocido": v["conocido"], "alias": alias}
    return {"_meta": {"fecha": r["exportado"][:10], "revisor": r["revisor"], "muestra": r["muestra"],
                      "para": "#52, evaluación final: qué legítimas reales de CallCenterEN no deberían avisar",
                      "metodo": "Fichas ciegas (preparar_revision_legitimas_reales.py): las 33 transcripciones con "
                                "roles, sin identificadores, referencia ni corridas, con la política de "
                                "corridas/2026-11-10_revision-producto/POLITICA.md, escrita antes.",
                      "etiquetas": {"no_avisar": "Un aviso es una falsa alarma.",
                                    "tolerable": "Avisar o no avisar son aceptables: no cuenta como FA ni se exige.",
                                    "avisar": "La llamada pide un acto que las fuentes dicen no aceptar de quien llamó."}},
            "casos": casos}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="orden", required=True)
    pf = sub.add_parser("fichas", help="escribe el formulario y la clave en data/private/")
    pf.add_argument("sets", type=Path, nargs="?", default=SETS)
    pf.add_argument("--manifiesto", type=Path, default=MANIFIESTO_LEGITIMAS)
    pf.add_argument("--privado", type=Path, default=PRIVADO)
    pe = sub.add_parser("etiquetas", help="pasa las respuestas al formato de etiquetas-producto.json")
    pe.add_argument("respuestas", type=Path)
    pe.add_argument("--clave", type=Path, default=CLAVE)
    pe.add_argument("--salida", type=Path, default=PRIVADO / "ETIQUETAS-LEGITIMAS-REALES.json")
    a = p.parse_args(argv)
    if a.orden == "fichas":
        muestra = fichas(a.sets, a.manifiesto, a.privado)
        print(f"Fichas listas en {a.privado / FORMULARIO.name}; muestra {muestra[:12]}. La clave queda fuera de Git.")
    else:
        datos = etiquetas(a.respuestas, a.clave)
        a.salida.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        cuenta = {e: sum(v["etiqueta"] == e for v in datos["casos"].values()) for e in sorted(ETIQUETAS)}
        print(f"{a.salida}: {cuenta}. Correr analizar.py --anotacion-legitimas con este archivo.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
