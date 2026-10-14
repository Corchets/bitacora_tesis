"""Genera los datos del tablero «Ensayo SLM directo» a partir de las corridas guardadas.

Uso (desde experiments/slm-directo):
    python analisis/tablero/armar_datos.py

Escribe un JSON por conjunto de datos en analisis/tablero/datos/. Cada número del
tablero sale de estos archivos, y estos archivos salen de corridas/ y de la
clasificación de avisos: nada se copia a mano, salvo los textos de pasos y preguntas
y las dos referencias externas que se citan con su fuente.
"""

from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ))

import casos  # noqa: E402
import resumen  # noqa: E402

SALIDA = Path(__file__).resolve().parent / "datos"
CLASIFICACION = RAIZ / "analisis" / "2026-10-14-fundamento-de-avisos" / "clasificaciones.json"

# Las configuraciones que se comparan, en el orden en que se muestran.
DETECTORES = [
    {"id": "reglas", "nombre": "Reglas", "corrida": "2026-10-13_224418_linea-base-reglas"},
    {"id": "q08", "nombre": "qwen3.5 0.8B", "corrida": "2026-10-14_173532_demo-qwen3.5-0.8b"},
    {"id": "q2", "nombre": "qwen3.5 2B", "corrida": "2026-10-14_172930_demo-qwen3.5-2b"},
    {"id": "q4", "nombre": "qwen3.5 4B", "corrida": "2026-10-14_174602_demo-qwen3.5-4b"},
]
REPETICION_2B = "2026-10-14_175451_demo-qwen3.5-2b"
CASOS_TRAYECTORIA = {
    "SC-SOPORTE-CLAVE-01-e01": "Falsa mesa de ayuda pide la contraseña (estafa)",
    "TR-01-pedido-indirecto-digitos": "«Leeme lo que te llegó, de a uno» (estafa)",
    "TR-08-frase-cortada-candado": "«Pasame el código» / «del candado…» (legítima)",
}
GRUPOS = {"piloto_escrito": "Piloto escrito", "trampa": "Trampas", "laboratorio": "Laboratorio"}
CATEGORIAS_FUNDAMENTO = [
    ("pedido_presente_bien_descrito", "Pedido real, bien descrito"),
    ("pedido_presente_mal_descrito", "Pedido real, mal descrito"),
    ("pedido_relatado_o_negado", "Pedido relatado o negado"),
    ("sospecha_sin_pedido", "Sospecha sin pedido"),
    ("pedido_inventado", "Pedido inventado"),
]
MODELOS_CLASIFICADOS = {"0.8b": "q08", "2b": "q2", "4b": "q4"}


def leer(carpeta: str):
    manifiesto, filas = resumen.leer_corrida(RAIZ / "corridas" / carpeta)
    analisis = list(resumen.analizar(manifiesto, filas).values())[0]
    return manifiesto, filas, analisis


def codigo(c: dict) -> str:
    base = resumen.CODIGOS[c["categoria"]] or "aviso"
    return f"{base} L{c['aviso']}" if c["aviso"] else base


def acierta(c: dict) -> bool:
    return c["categoria"] in ("antes_del_pedido", "en_el_pedido", "despues_del_pedido", "aviso_sin_pedido_de_referencia", "sin_aviso_correcto")


def guardar(nombre: str, filas: list[dict]) -> None:
    (SALIDA / f"{nombre}.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{nombre}.json: {len(filas)} filas")


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    corridas = {d["id"]: leer(d["corrida"]) for d in DETECTORES}

    # 1. Totales por detector
    detectores = []
    for d in DETECTORES:
        manifiesto, filas, cs = corridas[d["id"]]
        m = resumen.metricas(cs)
        cat = Counter(c["categoria"] for c in cs.values())
        mem = next(iter(manifiesto.get("modelos", {}).values()), {}).get("memoria") or {}
        riesgos = {f["riesgo"] for f in filas if f["riesgo"] != ""}
        detectores.append({
            "id": d["id"],
            "nombre": d["nombre"],
            "corrida": d["corrida"],
            "vishing": m["vishing"],
            "vishing_con_aviso": m["vishing_con_aviso"],
            "vishing_sin_aviso": m["vishing"] - m["vishing_con_aviso"],
            "antes_del_pedido": m["antes_del_pedido"],
            "en_el_pedido": m["en_el_pedido"],
            "despues_del_pedido": m["despues_del_pedido"],
            "despues_del_cumplimiento": m["en_o_despues_del_cumplimiento"],
            "aviso_sin_pedido_de_referencia": cat["aviso_sin_pedido_de_referencia"],
            "legitimas": m["legitimas"],
            "falsas_alarmas": m["falsas_alarmas"],
            "actualizaciones": m["actualizaciones"],
            "fallos": m["fallos"],
            "lineas_con_alerta": sum(1 for f in filas if f["alerta_sugerida"] == "true"),
            "ms_p50": None if d["id"] == "reglas" else round(m["ms_p50"]),
            "ms_p95": None if d["id"] == "reglas" else round(m["ms_p95"]),
            "memoria_mb": round(mem["size_bytes"] / 1024**2) if mem.get("size_bytes") else None,
            "valores_de_riesgo": len(riesgos),
        })
    guardar("detectores", detectores)

    # 2. Por grupo de casos
    por_grupo = []
    for d in DETECTORES:
        cs = corridas[d["id"]][2]
        for g, nombre_g in GRUPOS.items():
            m = resumen.metricas({k: v for k, v in cs.items() if v["ref"]["grupo"] == g})
            por_grupo.append({
                "clave": f"{d['id']}|{g}", "detector": d["id"], "nombre": d["nombre"], "grupo": nombre_g,
                "vishing_con_aviso": m["vishing_con_aviso"], "vishing": m["vishing"],
                "falsas_alarmas": m["falsas_alarmas"], "legitimas": m["legitimas"],
            })
    guardar("por_grupo", por_grupo)

    # 3. Caso por caso (una fila por conversación, una columna por detector)
    filas_casos = []
    for cid in sorted(corridas["q2"][2], key=lambda c: (list(GRUPOS).index(casos.cargar_referencia(c)["grupo"]), c)):
        ref = casos.cargar_referencia(cid)
        fila = {
            "caso": cid, "grupo": GRUPOS[ref["grupo"]],
            "clase": "estafa" if ref["clase"] == "vishing" else "legítima",
            "pedido_linea": ref["t_r_linea"], "cumplimiento_linea": ref["t_c_linea"],
        }
        for d in DETECTORES:
            c = corridas[d["id"]][2][cid]
            fila[d["id"]] = codigo(c)
            fila[f"{d['id']}_acierta"] = acierta(c)
            fila[f"{d['id']}_avisa"] = c["aviso"] is not None
        filas_casos.append(fila)
    guardar("casos", filas_casos)

    # 4. Fundamento de los avisos (revisor 1) y acuerdo entre revisores
    clasif = json.loads(CLASIFICACION.read_text(encoding="utf-8"))
    fundamento, acuerdo = [], []
    for modelo, det_id in MODELOS_CLASIFICADOS.items():
        r1 = {c["id"]: c["categoria"] for c in clasif[modelo]["revisor_1"]}
        r2 = {c["id"]: c["categoria"] for c in clasif[modelo]["revisor_2"]}
        nombre = next(d["nombre"] for d in DETECTORES if d["id"] == det_id)
        for cat_id, etiqueta in CATEGORIAS_FUNDAMENTO:
            ids = [i for i, c in r1.items() if c == cat_id]
            clases = Counter(casos.cargar_referencia(i.split("@")[0])["clase"] for i in ids)
            fundamento.append({
                "clave": f"{det_id}|{cat_id}", "detector": det_id, "nombre": nombre,
                "categoria": cat_id, "etiqueta": etiqueta, "avisos": len(ids),
                "en_estafas": clases["vishing"], "en_legitimas": clases["legitima_dificil"],
            })
        comunes = [i for i in r1 if i in r2]
        coinciden = sum(1 for i in comunes if r1[i] == r2[i])
        n = len(comunes)
        po = coinciden / n
        pe = sum(Counter(r1[i] for i in comunes)[c] * Counter(r2[i] for i in comunes)[c] for c, _ in CATEGORIAS_FUNDAMENTO) / n**2
        acuerdo.append({"detector": det_id, "nombre": nombre, "avisos": n, "coinciden": coinciden, "kappa": round((po - pe) / (1 - pe), 2)})
    guardar("fundamento", fundamento)
    guardar("acuerdo", acuerdo)

    # 5. Trayectorias de riesgo de tres conversaciones
    trayectorias = []
    for cid, titulo in CASOS_TRAYECTORIA.items():
        ref = casos.cargar_referencia(cid)
        lineas = casos.cargar_texto(cid)
        for d in DETECTORES:
            filas = {int(f["linea"]): f for f in corridas[d["id"]][1] if f["case_id"] == cid}
            for n, linea in enumerate(lineas, start=1):
                f = filas[n]
                trayectorias.append({
                    "clave": f"{cid}|{d['id']}|{n}", "caso": cid, "titulo": titulo, "detector": d["id"],
                    "nombre": d["nombre"], "linea": n, "texto": f"{linea.hablante}: {linea.texto}",
                    "riesgo": float(f["riesgo"]) if f["riesgo"] else None,
                    "alerta": f["alerta_sugerida"] == "true", "aviso": f["aviso"] == "true",
                    "pedido_linea": ref["t_r_linea"], "cumplimiento_linea": ref["t_c_linea"],
                })
    guardar("trayectorias", trayectorias)

    # 6. Dos corridas iguales del 2B
    _, filas_a, cs_a = corridas["q2"]
    _, filas_b, cs_b = leer(REPETICION_2B)
    A = {(f["case_id"], f["linea"]): f for f in filas_a}
    B = {(f["case_id"], f["linea"]): f for f in filas_b}
    comunes = sorted(set(A) & set(B))
    campos = ("riesgo", "alerta_sugerida", "aviso", "motivo", "evidencia", "crudo")
    distintos = [
        {"caso": c, "corrida_1": codigo(cs_a[c]), "corrida_2": codigo(cs_b[c])}
        for c in cs_a if (cs_a[c]["categoria"], cs_a[c]["aviso"]) != (cs_b[c]["categoria"], cs_b[c]["aviso"])
    ]
    guardar("repeticion", [{
        "comparacion": "2B corrida 1 contra corrida 2",
        "actualizaciones": len(comunes),
        "respuestas_distintas": sum(1 for k in comunes if any(A[k][c] != B[k][c] for c in campos)),
        "riesgos_distintos": sum(1 for k in comunes if A[k]["riesgo"] != B[k]["riesgo"]),
        "conversaciones": len(cs_a),
        "conversaciones_con_otro_resultado": len(distintos),
        "vishing_con_aviso_1": resumen.metricas(cs_a)["vishing_con_aviso"],
        "vishing_con_aviso_2": resumen.metricas(cs_b)["vishing_con_aviso"],
    }])
    guardar("repeticion_casos", distintos)

    # 7. Referencias externas, citadas con su fuente
    guardar("gamas", [
        {"gama": "Baja", "techo_mb": 256, "hilos_detector": 1, "fuente": "docs/investigacion/PREFACTIBILIDAD-TECNICA.md"},
        {"gama": "Media", "techo_mb": 512, "hilos_detector": 1, "fuente": "docs/investigacion/PREFACTIBILIDAD-TECNICA.md"},
        {"gama": "Alta", "techo_mb": 1024, "hilos_detector": 2, "fuente": "docs/investigacion/PREFACTIBILIDAD-TECNICA.md"},
        # Pico de la corrida de audio del laboratorio: ASR más un detector TF-IDF muy liviano.
        {"gama": "ASR del laboratorio (aprox.)", "techo_mb": 420, "hilos_detector": None, "fuente": "docs/investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md, corrida de audio del 2026-09-25 (ASR con detector TF-IDF)"},
    ])
    return 0


if __name__ == "__main__":
    sys.exit(main())
