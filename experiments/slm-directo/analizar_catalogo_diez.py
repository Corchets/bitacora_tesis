"""Evalúa la cascada de diez opciones con Gemma consultado en cada actualización."""
from __future__ import annotations

import argparse
import collections
import json
import math
import statistics
from pathlib import Path

from casos import DIR_REFERENCIA, cargar_referencia, cargar_texto
from ensayo_catalogo_qwen import lista, sha
from slm_catalogo_diez import leer


def wilson(exitos, total):
    if not total:
        return None
    z = 1.959963984540054
    p = exitos / total
    d = 1 + z*z/total
    centro = (p + z*z/(2*total))/d
    radio = z * math.sqrt(p*(1-p)/total + z*z/(4*total*total))/d
    return [max(0.0, centro-radio), min(1.0, centro+radio)]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("reranker", type=Path)
    p.add_argument("gemma", type=Path)
    p.add_argument("--anterior", type=Path, help="métricas de la prueba con once categorías")
    p.add_argument("--salida", type=Path, required=True)
    args = p.parse_args()
    ids = lista("rapida-20")
    m_rr, rr = leer(args.reranker, ids)
    registros = [json.loads(s) for s in args.gemma.read_text(encoding="utf-8").splitlines()]
    if not registros or registros[0].get("tipo") != "manifiesto" or registros[-1].get("tipo") != "fin":
        raise ValueError("La corrida de Gemma está incompleta")
    m = registros[0]
    if m.get("experimento") != "catalogo-diez-gemma-siempre-v1" or m.get("modelo") != "gemma4:e2b":
        raise ValueError("Modelo o experimento incorrecto")
    if m.get("reranker_sha256") != sha(args.reranker) or set(m.get("casos", [])) != set(ids):
        raise ValueError("La corrida de Gemma no corresponde al reranker o no cubre todos los casos")
    filas = [r for r in registros if r["tipo"] == "consulta"]
    claves = [(r["case_id"], r["linea"], r["ventana"]) for r in filas]
    esperadas = {(r["case_id"], r["linea"], r["ventana"]) for r in rr}
    if len(claves) != len(set(claves)) or set(claves) != esperadas:
        raise ValueError("Gemma no fue consultado exactamente una vez por actualización")
    rr_indice = {(r["case_id"], r["linea"], r["ventana"]): r for r in rr}
    for r in filas:
        datos = rr_indice[(r["case_id"], r["linea"], r["ventana"])]
        if r["tito_activa"] != datos["tito_activa"] or r["opcion_principal"] != max(datos["puntajes"], key=datos["puntajes"].get):
            raise ValueError("Consulta o activación inconsistentemente registrada")
    referencias = {c: cargar_referencia(c) for c in ids}
    estafas = [c for c in ids if referencias[c]["clase"] == "vishing"]
    legitimas = [c for c in ids if referencias[c]["clase"] != "vishing"]
    resultados, costos = [], {}
    for ventana in ("linea", "par"):
        fs = [r for r in filas if r["ventana"] == ventana]
        tiempos_slm = sorted(r["respuesta"]["ms"] for r in fs if r["respuesta"]["ms"] is not None)
        tiempos_rr = sorted(r["qwen_ms"] for r in rr if r["ventana"] == ventana)
        costos[ventana] = {"consultas_directas": len(fs), "consultas_con_tito_simuladas": sum(r["tito_activa"] for r in fs),
                           "reranker_ms_p50": statistics.median(tiempos_rr),
                           "reranker_ms_p95": tiempos_rr[min(len(tiempos_rr)-1, int(.95*len(tiempos_rr)))],
                           "gemma_ms_p50": statistics.median(tiempos_slm),
                           "gemma_ms_p95": tiempos_slm[min(len(tiempos_slm)-1, int(.95*len(tiempos_slm)))],
                           "qwen_suma_ms": sum(tiempos_rr), "gemma_suma_ms": sum(tiempos_slm)}
        for con_tito in (False, True):
            activas = [r for r in fs if not con_tito or r["tito_activa"]]
            por_caso = {c: [] for c in ids}
            for r in activas:
                por_caso[r["case_id"]].append(r)
            avisos, fallos = {}, {}
            for case_id, consultas in por_caso.items():
                validos = [r["linea"] for r in consultas if r["respuesta"]["valida"] and r["respuesta"]["alerta_sugerida"]]
                avisos[case_id] = min(validos) if validos else None
                fallos[case_id] = sum(not r["respuesta"]["valida"] for r in consultas)
            detectadas = sum(avisos[c] is not None for c in estafas)
            falsas = sum(avisos[c] is not None for c in legitimas)
            inciertas = [c for c in ids if avisos[c] is None and fallos[c]]
            antes_pedido = sum(avisos[c] is not None and referencias[c].get("t_r_linea") is not None and
                               avisos[c] <= referencias[c]["t_r_linea"] for c in estafas)
            antes_cumplimiento = sum(avisos[c] is not None and referencias[c].get("t_c_linea") is not None and
                                     avisos[c] < referencias[c]["t_c_linea"] for c in estafas)
            resultados.append({"ventana": ventana, "con_tito": con_tito,
                               "estafas_con_alerta": detectadas, "estafas": len(estafas),
                               "legitimas_con_alerta": falsas, "legitimas": len(legitimas),
                               "deteccion_wilson_95": wilson(detectadas,len(estafas)),
                               "falsa_alarma_wilson_95": wilson(falsas,len(legitimas)),
                               "avisos_antes_o_en_linea_pedido": antes_pedido,
                               "avisos_en_linea_anterior_al_cumplimiento": antes_cumplimiento,
                               "estafas_con_referencia_pedido": sum(referencias[c].get("t_r_linea") is not None for c in estafas),
                               "estafas_con_referencia_cumplimiento": sum(referencias[c].get("t_c_linea") is not None for c in estafas),
                               "casos_sin_alerta_con_error": inciertas,
                               "consultas_invalidas": sum(fallos.values()),
                               "opciones_principales": dict(collections.Counter(r["opcion_principal"] for r in activas)),
                               "avisos_por_caso": avisos})
    anterior = None
    if args.anterior:
        anterior = {"sha256": sha(args.anterior),
                    "resultado": json.loads(args.anterior.read_text(encoding="utf-8"))["resumen"],
                    "nota": "Mismos casos y modelos, pero la regla de derivación y el catálogo cambiaron."}
    output = {"estado": "desarrollo, sin revisión humana y sin independencia del informe previo",
              "experimento": "catalogo-diez-gemma-siempre-v1", "resultados": resultados, "costos": costos,
              "version_anterior": anterior,
              "pares_incompletos": [c for c in ids if len(cargar_texto(c)) % 2],
              "procedencia": {"analizador_sha256": sha(Path(__file__)),
                             "reranker_sha256": sha(args.reranker), "gemma_sha256": sha(args.gemma),
                             "referencias_sha256": {c: sha(DIR_REFERENCIA / f"{c}.json") for c in ids}}}
    with args.salida.open("x", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
