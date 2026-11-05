"""Analiza salidas del experimento de catálogo sin volver a ejecutar modelos.

Selecciona un umbral solo en seleccion-57 y lo aplica a rapida-20. La regla de
alerta exploratoria requiere que POSSIBLE_DECEPTION sea la situación principal;
los dos indicios se conservan aparte y un pedido aislado no prueba estafa.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from functools import lru_cache
from pathlib import Path

from casos import DIR_REFERENCIA, cargar_referencia, cargar_texto
from ensayo_catalogo_qwen import CATALOGO, lista, sha

DETECCION = "POSSIBLE_DECEPTION"
SITUACIONES = {c["id"] for c in json.loads(CATALOGO.read_text(encoding="utf-8"))["categorias"]
               if c["grupo"] == "situacion"}
PEDIDOS = {"REQUEST_AUTH_CODE", "REQUEST_SECRET", "REQUEST_PERSONAL_DATA", "REQUEST_TRANSFER", "REQUEST_ACCESS_ACTION"}
referencia = lru_cache(maxsize=None)(cargar_referencia)


def leer(ruta: Path, split: str):
    registros = [json.loads(s) for s in ruta.read_text(encoding="utf-8").splitlines()]
    if not registros or registros[0].get("tipo") != "manifiesto" or registros[-1].get("tipo") != "fin":
        raise ValueError(f"Corrida incompleta o sin manifiesto: {ruta}")
    m = registros[0]
    if m["lista"] != split or set(m["casos"]) != set(lista(split)):
        raise ValueError(f"La corrida debe cubrir toda la lista {split}")
    if any(r["tipo"].startswith("error_") for r in registros):
        raise ValueError("Hay fallos de inferencia: informar y resolver antes de calcular métricas")
    filas = [r for r in registros if r["tipo"] == "actualizacion"]
    esperadas = {(c, i, v) for c in m["casos"] for i in range(1, len(cargar_texto(c)) + 1)
                 for v in ("cuatro", "acumulada")}
    claves = [(r["case_id"], r["linea"], r["ventana"]) for r in filas]
    if len(claves) != len(set(claves)) or set(claves) != esperadas:
        raise ValueError("La corrida tiene líneas ausentes o duplicadas")
    return m, filas


def primer_aviso(filas, ids, ventana, con_tito, umbral):
    salida = {c: None for c in ids}
    for r in sorted(filas, key=lambda x: (x["case_id"], x["linea"])):
        if r["ventana"] != ventana or (con_tito and not r["tito_activa"]):
            continue
        puntajes = r["puntajes"]
        ganador = max((k for k in puntajes if k in SITUACIONES), key=puntajes.get)
        if ganador == DETECCION and puntajes[ganador] > umbral and salida[r["case_id"]] is None:
            salida[r["case_id"]] = r["linea"]
    return salida


def evaluar(filas, ids, ventana, con_tito, umbral):
    avisos = primer_aviso(filas, ids, ventana, con_tito, umbral)
    positivos = [c for c in ids if referencia(c)["clase"] == "vishing"]
    negativos = [c for c in ids if c not in positivos]
    def cantidad(casos):
        return sum(avisos[c] is not None for c in casos)
    def wilson(aciertos, total):
        if not total:
            return None
        z = 1.959963984540054
        p = aciertos / total
        denominador = 1 + z * z / total
        centro = (p + z * z / (2 * total)) / denominador
        radio = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominador
        return [max(0.0, centro - radio), min(1.0, centro + radio)]
    antes_pedido = sum(avisos[c] is not None and referencia(c).get("t_r_linea") is not None
                       and avisos[c] <= referencia(c)["t_r_linea"] for c in positivos)
    antes_cumplimiento = sum(avisos[c] is not None and referencia(c).get("t_c_linea") is not None
                             and avisos[c] < referencia(c)["t_c_linea"] for c in positivos)
    return {"estafas_con_aviso": cantidad(positivos), "estafas": len(positivos),
            "legitimas_con_aviso": cantidad(negativos), "legitimas": len(negativos),
            "deteccion_wilson_95": wilson(cantidad(positivos), len(positivos)),
            "falsa_alarma_wilson_95": wilson(cantidad(negativos), len(negativos)),
            "avisos_antes_o_en_linea_pedido": antes_pedido,
            "avisos_en_linea_anterior_al_cumplimiento": antes_cumplimiento,
            "estafas_con_referencia_pedido": sum(referencia(c).get("t_r_linea") is not None for c in positivos),
            "estafas_con_referencia_cumplimiento": sum(referencia(c).get("t_c_linea") is not None for c in positivos),
            "avisos_por_caso": avisos}


def contar_avisos(avisos):
    positivos = [c for c in avisos if referencia(c)["clase"] == "vishing"]
    negativos = [c for c in avisos if c not in positivos]
    return {"estafas_con_aviso": sum(avisos[c] is not None for c in positivos),
            "estafas": len(positivos),
            "legitimas_con_aviso": sum(avisos[c] is not None for c in negativos),
            "legitimas": len(negativos)}


def tipos_pedido(filas, ids, ventana, con_tito):
    """Acierto condicional entre cinco tipos en la línea de referencia disponible."""
    indice = {(r["case_id"], r["linea"]): r for r in filas if r["ventana"] == ventana}
    total = disponibles = correctos = 0
    for c in ids:
        ref = referencia(c)
        pedido, linea = ref.get("pedido"), ref.get("t_r_linea")
        if pedido in {"REQUEST_REMOTE_ACCESS", "REQUEST_SECURITY_ACTION"}:
            pedido = "REQUEST_ACCESS_ACTION"
        if pedido not in PEDIDOS or linea is None:
            continue
        total += 1
        r = indice.get((c, linea))
        if r is None or (con_tito and not r["tito_activa"]):
            continue
        disponibles += 1
        puntajes = r["puntajes"]
        correcto = max((k for k in puntajes if k in PEDIDOS), key=puntajes.get) == pedido
        correctos += int(correcto)
    return {"casos_con_referencia": total, "consultas_disponibles": disponibles,
            "tipo_correcto_entre_cinco_pedidos": correctos,
            "nota": "Clasificación forzada entre pedidos en T_R; no mide si hubo pedido ni si es fraude."}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("seleccion", type=Path)
    p.add_argument("informe", type=Path)
    p.add_argument("--salida", type=Path, required=True)
    p.add_argument("--umbrales", type=Path, required=True, help="umbrales congelados solo con selección")
    p.add_argument("--reglas", type=Path, help="CSV de actualizaciones de reglas para comparar casos compartidos")
    args = p.parse_args()
    ms, seleccion = leer(args.seleccion, "seleccion-57")
    mi, informe = leer(args.informe, "rapida-20")
    claves = ("experimento", "revision_resuelta", "catalogo_sha256", "ejecutor_sha256", "tito_sha256",
              "max_tokens_par", "dispositivo", "gpu", "precision_qwen", "precision_tito", "lote", "seed")
    if not ms.get("revision_resuelta") or not mi.get("revision_resuelta"):
        raise ValueError("Las corridas deben registrar la revisión resuelta del modelo")
    if any(ms.get(k) != mi.get(k) for k in claves):
        raise ValueError("Las corridas no tienen la misma configuración")
    if set(ms["casos"]) & set(mi["casos"]):
        raise ValueError("Las particiones tienen casos en común")
    seleccion_umbrales = json.loads(args.umbrales.read_text(encoding="utf-8"))
    if seleccion_umbrales.get("seleccion_sha256") != sha(args.seleccion):
        raise ValueError("Los umbrales no corresponden a esta selección")
    umbrales = {(u["ventana"], u["con_tito"]): u["umbral"] for u in seleccion_umbrales["umbrales"]}
    if set(umbrales) != {(v, t) for v in ("cuatro", "acumulada") for t in (False, True)}:
        raise ValueError("Faltan umbrales o hay configuraciones inesperadas")
    resultados = []
    costos = {}
    for nombre, filas in (("seleccion", seleccion), ("informe", informe)):
        costos[nombre] = {}
        for ventana in ("cuatro", "acumulada"):
            fs = [r for r in filas if r["ventana"] == ventana]
            duraciones = sorted(r["qwen_ms"] for r in fs)
            costos[nombre][ventana] = {"consultas": len(fs), "qwen_ms_p50": statistics.median(duraciones),
                                       "qwen_ms_p95": duraciones[min(len(duraciones)-1, int(0.95*len(duraciones)))],
                                       "gpu_pico_asignado_bytes": max(r["gpu_pico_asignado_bytes"] for r in fs),
                                       "consultas_activadas_por_tito": sum(r["tito_activa"] for r in fs),
                                       "pares_con_recorte": sum(sum(v > 0 for v in r["tokens_documento_recortados"].values()) for r in fs)}
    for ventana in ("cuatro", "acumulada"):
        for con_tito in (False, True):
            t = umbrales[(ventana, con_tito)]
            for nombre, umbral in (("mayor_puntaje", -1.0), ("mayor_y_umbral", t)):
                resultados.append({"ventana": ventana, "con_tito": con_tito, "politica": nombre,
                                   "umbral": None if umbral < 0 else umbral,
                                   "seleccion": evaluar(seleccion, ms["casos"], ventana, con_tito, umbral),
                                   "informe": evaluar(informe, mi["casos"], ventana, con_tito, umbral),
                                   "tipo_pedido_seleccion": tipos_pedido(seleccion, ms["casos"], ventana, con_tito),
                                   "tipo_pedido_informe": tipos_pedido(informe, mi["casos"], ventana, con_tito)})
    comparadores = {}
    for nombre, meta, filas in (("seleccion", ms, seleccion), ("informe", mi, informe)):
        # Umbral de Tito como detector de sospecha; no equivale al aviso de su cascada original.
        avisos = {c: None for c in meta["casos"]}
        for r in sorted(filas, key=lambda x: (x["case_id"], x["linea"])):
            if r["ventana"] == "cuatro" and r["tito_activa"] and avisos[r["case_id"]] is None:
                avisos[r["case_id"]] = r["linea"]
        comparadores[nombre] = {"tito_activacion_por_caso": avisos,
                                "tito_activacion_resumen": contar_avisos(avisos)}
    if args.reglas:
        with args.reglas.open(encoding="utf-8-sig", newline="") as f:
            reglas = list(csv.DictReader(f))
        for nombre, meta in (("seleccion", ms), ("informe", mi)):
            por_caso = {}
            for c in meta["casos"]:
                filas_caso = [r for r in reglas if r["case_id"] == c]
                esperadas = set(range(1, len(cargar_texto(c)) + 1))
                recibidas = {int(r["linea"]) for r in filas_caso if r["valida"].lower() == "true"}
                if recibidas != esperadas:
                    continue
                alertas = [int(r["linea"]) for r in filas_caso if r["alerta_sugerida"].lower() == "true"]
                por_caso[c] = min(alertas) if alertas else None
            comparadores[nombre]["reglas_aviso_por_caso"] = por_caso
            comparadores[nombre]["reglas_cobertura"] = [len(por_caso), len(meta["casos"])]
            comparadores[nombre]["reglas_resumen"] = contar_avisos(por_caso)
    with args.salida.open("x", encoding="utf-8") as f:
        json.dump({"estado": "desarrollo, no evaluación final", "resultados": resultados,
                   "comparadores": comparadores, "costos": costos,
                   "procedencia": {"analizador_sha256": sha(Path(__file__)),
                                   "seleccion_sha256": sha(args.seleccion),
                                   "informe_sha256": sha(args.informe),
                                   "umbrales_sha256": sha(args.umbrales),
                                   "reglas_sha256": sha(args.reglas) if args.reglas else None,
                                   "referencias_sha256": {c: sha(DIR_REFERENCIA / f"{c}.json")
                                                           for c in ms["casos"] + mi["casos"]}}}, f,
                  ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
