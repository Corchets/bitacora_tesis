"""Selecciona umbrales o informa la prueba línea a línea y pares no solapados."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from analizar_catalogo_qwen import DETECCION, evaluar
from casos import DIR_REFERENCIA, cargar_texto
from ensayo_catalogo_qwen import lista, sha

VENTANAS = ("linea", "par")


def leer(ruta: Path, split: str):
    registros = [json.loads(s) for s in ruta.read_text(encoding="utf-8").splitlines()]
    if not registros or registros[0].get("tipo") != "manifiesto" or registros[-1].get("tipo") != "fin":
        raise ValueError("Corrida incompleta")
    m = registros[0]
    if m["experimento"] != "catalogo-qwen-linea-y-par-v1" or m["lista"] != split:
        raise ValueError("Experimento o lista incorrecta")
    if set(m["casos"]) != set(lista(split)):
        raise ValueError("Se necesita la lista completa")
    if any(r["tipo"].startswith("error_") for r in registros):
        raise ValueError("Hay fallos de inferencia")
    filas = [r for r in registros if r["tipo"] == "actualizacion"]
    esperadas = {(c, n, v) for c in m["casos"] for n in range(1, len(cargar_texto(c)) + 1)
                 for v in VENTANAS if v == "linea" or n % 2 == 0}
    claves = [(r["case_id"], r["linea"], r["ventana"]) for r in filas]
    if len(claves) != len(set(claves)) or set(claves) != esperadas:
        raise ValueError("Actualizaciones ausentes o duplicadas")
    for r in filas:
        inicio = r["linea"] if r["ventana"] == "linea" else r["linea"] - 1
        if r["linea_inicio"] != inicio:
            raise ValueError("Ventana incorrecta")
    incompletos = {r["case_id"] for r in registros if r["tipo"] == "par_final_incompleto"}
    esperados = {c for c in m["casos"] if len(cargar_texto(c)) % 2}
    if incompletos != esperados:
        raise ValueError("Faltan registros de pares incompletos")
    return m, filas, incompletos


def seleccionar(m, filas):
    umbrales = []
    for ventana in VENTANAS:
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
    return umbrales


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("seleccion", type=Path)
    p.add_argument("--informe", type=Path)
    p.add_argument("--umbrales", type=Path)
    p.add_argument("--anterior", type=Path, help="métricas de cuatro líneas y contexto acumulado")
    p.add_argument("--salida", type=Path, required=True)
    args = p.parse_args()
    ms, seleccion, incompletos_s = leer(args.seleccion, "seleccion-57")
    if args.informe is None:
        resultado = {"estado": "umbrales seleccionados exclusivamente en desarrollo",
                     "seleccion_sha256": sha(args.seleccion), "analizador_sha256": sha(Path(__file__)),
                     "umbrales": seleccionar(ms, seleccion)}
    else:
        if not args.umbrales:
            p.error("Se requieren umbrales congelados antes del informe")
        datos_u = json.loads(args.umbrales.read_text(encoding="utf-8"))
        if datos_u["seleccion_sha256"] != sha(args.seleccion):
            raise ValueError("Los umbrales no corresponden a esta selección")
        mi, informe, incompletos_i = leer(args.informe, "rapida-20")
        claves = ("experimento", "revision_resuelta", "catalogo_sha256", "ejecutor_sha256", "soporte_sha256",
                  "tito_sha256", "max_tokens_par", "dispositivo", "gpu", "precision_qwen", "precision_tito", "lote", "seed")
        if any(ms.get(k) != mi.get(k) for k in claves) or not ms.get("revision_resuelta"):
            raise ValueError("Configuraciones incompatibles")
        if set(ms["casos"]) & set(mi["casos"]):
            raise ValueError("Las listas comparten casos")
        umbrales = {(x["ventana"], x["con_tito"]): x["umbral"] for x in datos_u["umbrales"]}
        if set(umbrales) != {(v, t) for v in VENTANAS for t in (False, True)}:
            raise ValueError("Umbrales incompletos")
        resultados, costos = [], {}
        for v in VENTANAS:
            fs = [r for r in informe if r["ventana"] == v]
            tiempos = sorted(r["qwen_ms"] for r in fs)
            costos[v] = {"consultas": len(fs), "qwen_ms_p50": statistics.median(tiempos),
                         "qwen_ms_p95": tiempos[min(len(tiempos)-1, int(len(tiempos)*.95))],
                         "tito_activa": sum(r["tito_activa"] for r in fs),
                         "gpu_pico_asignado_bytes": max(r["gpu_pico_asignado_bytes"] for r in fs),
                         "pares_con_recorte": sum(sum(x > 0 for x in r["tokens_documento_recortados"].values()) for r in fs)}
            for tito in (False, True):
                for nombre, umbral in (("mayor_puntaje", -1.0), ("mayor_y_umbral", umbrales[(v, tito)])):
                    resultados.append({"ventana": v, "con_tito": tito, "politica": nombre,
                                       "umbral": None if umbral < 0 else umbral,
                                       "seleccion": evaluar(seleccion, ms["casos"], v, tito, umbral),
                                       "informe": evaluar(informe, mi["casos"], v, tito, umbral)})
        resultado = {"estado": "desarrollo; no evaluación final", "resultados": resultados,
                     "costos_informe": costos, "pares_incompletos_seleccion": sorted(incompletos_s),
                     "pares_incompletos_informe": sorted(incompletos_i),
                     "procedencia": {"seleccion_sha256": sha(args.seleccion), "informe_sha256": sha(args.informe),
                                    "umbrales_sha256": sha(args.umbrales), "analizador_sha256": sha(Path(__file__)),
                                    "referencias_sha256": {c: sha(DIR_REFERENCIA / f"{c}.json")
                                                          for c in ms["casos"] + mi["casos"]}}}
        if args.anterior:
            anterior = json.loads(args.anterior.read_text(encoding="utf-8"))
            resultado["comparacion_anterior"] = {"sha256": sha(args.anterior), "resultados": anterior["resultados"],
                                                "nota": "Mismos casos de desarrollo, evaluación de Qwen en cada línea."}
    with args.salida.open("x", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
