"""Congela umbrales exploratorios usando únicamente la corrida de selección."""
import argparse
import json
from pathlib import Path

from analizar_catalogo_qwen import DETECCION, evaluar, leer
from ensayo_catalogo_qwen import sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("seleccion", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    args = p.parse_args()
    m, filas = leer(args.seleccion, "seleccion-57")
    umbrales = []
    for ventana in ("cuatro", "acumulada"):
        for con_tito in (False, True):
            candidatos = sorted({0.0, 1.0} | {r["puntajes"][DETECCION] for r in filas
                                            if r["ventana"] == ventana})
            opciones = [(t, evaluar(filas, m["casos"], ventana, con_tito, t)) for t in candidatos]
            validas = [(t, x) for t, x in opciones if x["legitimas"] and
                       x["legitimas_con_aviso"] / x["legitimas"] <= 0.15]
            if not validas:
                raise ValueError("No hay umbral admisible")
            t, resultado = max(validas, key=lambda tx: (tx[1]["estafas_con_aviso"],
                                                        -tx[1]["legitimas_con_aviso"], tx[0]))
            umbrales.append({"ventana": ventana, "con_tito": con_tito,
                             "umbral": t, "seleccion": resultado})
    with args.salida.open("x", encoding="utf-8") as f:
        json.dump({"estado": "desarrollo; umbrales elegidos solo en seleccion-57",
                   "seleccion_sha256": sha(args.seleccion), "script_sha256": sha(Path(__file__)),
                   "umbrales": umbrales}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
