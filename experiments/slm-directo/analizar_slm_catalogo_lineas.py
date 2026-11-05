"""Resumen separado de Gemma para el ensayo de una línea y pares."""
import argparse
import json
import statistics
from pathlib import Path

from analizar_catalogo_lineas import VENTANAS
from casos import cargar_referencia
from ensayo_catalogo_qwen import sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corrida", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    args = p.parse_args()
    filas = [json.loads(s) for s in args.corrida.read_text(encoding="utf-8").splitlines()]
    if not filas or filas[0].get("tipo") != "manifiesto" or filas[-1].get("tipo") != "fin":
        raise ValueError("La integración está incompleta")
    consultas = [r for r in filas if r["tipo"] == "consulta"]
    condiciones = filas[-1]["consultas_con_alerta_por_condicion"]
    resumen = []
    for ventana in VENTANAS:
        for tito in (False, True):
            for politica in ("mayor_puntaje", "mayor_y_umbral"):
                estados = [r for r in condiciones if r["ventana"] == ventana and
                           r["con_tito"] == tito and r["politica"] == politica]
                invalidos = {r["case_id"] for r in consultas if not r["respuesta"]["valida"] and
                             [ventana, tito, politica] in r["condiciones"]}
                estafas = [r for r in estados if cargar_referencia(r["case_id"])["clase"] == "vishing"]
                legitimas = [r for r in estados if cargar_referencia(r["case_id"])["clase"] != "vishing"]
                resumen.append({"ventana": ventana, "con_tito": tito, "politica": politica,
                                "estafas_con_alerta_slm": sum(x["alerto"] for x in estafas),
                                "estafas": len(estafas),
                                "legitimas_con_alerta_slm": sum(x["alerto"] for x in legitimas),
                                "legitimas": len(legitimas),
                                "sin_alerta_con_fallo": sum(not x["alerto"] and x["case_id"] in invalidos for x in estados)})
    tiempos = sorted(r["respuesta"]["ms"] for r in consultas if r["respuesta"]["ms"] is not None)
    with args.salida.open("x", encoding="utf-8") as f:
        json.dump({"estado": "integración secundaria, desarrollo", "corrida_sha256": sha(args.corrida),
                   "analizador_sha256": sha(Path(__file__)), "consultas": len(consultas),
                   "consultas_invalidas": sum(not r["respuesta"]["valida"] for r in consultas),
                   "slm_ms_p50": statistics.median(tiempos) if tiempos else None,
                   "slm_ms_p95": tiempos[min(len(tiempos)-1, int(.95*len(tiempos)))] if tiempos else None,
                   "resumen": resumen}, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
