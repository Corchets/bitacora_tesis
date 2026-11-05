"""Datos para el panel de lectura: corridas terminadas, sin inferencia ni reserva.

Los IDs y las huellas se toman de los manifiestos; no se enumera el corpus.
El comando de actualización vive en actualizar_panel_lectura.py.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import re

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
DESDE = "2026-11-04"


def manifiesto_completo(m):
    if m.get("particion") != "desarrollo":
        raise ValueError("Solo se admiten manifiestos de desarrollo")
    ids = m.get("casos", {})
    if not ids or any(cid.startswith("CV2-T") or not re.fullmatch(r"[A-Za-z0-9_-]+", cid) for cid in ids):
        raise ValueError("ID inseguro o de reserva; no se abre ningún caso")
    return bool(m.get("fin")) and m.get("interrumpida") is False


def resumir(filas, n_lineas):
    if [int(r["linea"]) for r in filas] != list(range(1, len(filas) + 1)) or len(filas) > n_lineas:
        raise ValueError("Prefijo incompleto, repetido o fuera del texto")
    aviso = next((r for r in filas if r["aviso"] == "true"), None)
    fallos = [r for r in filas if r["valida"] != "true" and r["consulta"] != "omitida"]
    # Un corte sin aviso o un fallo nunca cuenta como estafa perdida o legítima correcta.
    completo = not fallos and (aviso is not None or len(filas) == n_lineas)
    return {"aviso": int(aviso["linea"]) if aviso else None,
            "motivo": aviso["motivo"] if aviso else "",
            "evidencia": aviso["evidencia"] if aviso else "",
            "completo": completo,
            "filas": [[float(r["riesgo"]) if r["riesgo"] else None,
                       "omitida" if r["consulta"] == "omitida" else "válida" if r["valida"] == "true" else "error",
                       r["error"]] for r in filas]}


def cargar_datos(raiz=SLM):
    raiz = Path(raiz)
    casos, corridas, pendientes = {}, [], []
    huellas = None
    for p in sorted((raiz / "corridas").rglob("manifiesto.json")):
        if p.parent.name[:10] < DESDE:
            continue
        m = json.loads(p.read_text(encoding="utf-8"))
        if m.get("particion") != "desarrollo":
            continue
        if m.get("casos") and all(cid.startswith("CTRL-") for cid in m["casos"]):
            continue
        if not manifiesto_completo(m):
            pendientes.append(p.parent.relative_to(raiz).as_posix())
            continue
        if huellas is None:
            huellas = m["casos"]
            for cid, huella in huellas.items():
                texto = (raiz / "casos/texto" / f"{cid}.txt").read_text(encoding="utf-8")
                if hashlib.sha256(texto.encode()).hexdigest()[:16] != huella:
                    raise ValueError(f"Texto distinto al ejecutado: {cid}")
                ref = json.loads((raiz / "casos/referencia" / f"{cid}.json").read_text(encoding="utf-8"))
                if ref.get("particion", "desarrollo") != "desarrollo" or ref["case_id"] != cid:
                    raise ValueError("Referencia ajena al desarrollo")
                casos[cid] = {"id": cid, "clase": ref["clase"], "grupo": ref["grupo"],
                              "familia": ref.get("familia"), "pedido": ref.get("pedido"),
                              "prueba": ref.get("que_prueba", ""), "notas": ref.get("notas", ""),
                              "tr": ref.get("t_r_linea"), "tc": ref.get("t_c_linea"),
                              "revision_humana": ref.get("revision_humana", False), "texto": texto.splitlines()}
        elif m["casos"] != huellas:
            raise ValueError(f"Los IDs o las huellas difieren: {p.parent.name}")
        grupos = collections.defaultdict(lambda: collections.defaultdict(list))
        with (p.parent / "actualizaciones.csv").open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r["case_id"] not in huellas:
                    raise ValueError("CSV con un ID ajeno al manifiesto")
                grupos[r["config"]][r["case_id"]].append(r)
        for config in m["configs"]:
            registros = grupos[config["config"]]
            if set(registros) != set(casos):
                raise ValueError(f"Faltan casos en {p.parent.name}: {config['config']}")
            resultados = {cid: resumir(sorted(rs, key=lambda r: int(r["linea"])), len(casos[cid]["texto"]))
                          for cid, rs in registros.items()}
            detector = {"slm": "SLM solo", "tito-slm": "Tito con indicio",
                        "tito-slm-sin-indicio": "Tito sin indicio", "reglas": "Reglas"}.get(config["detector"], config["detector"])
            prompt = "v1" if config["prompt"] == "tarea" else config["prompt"]
            roles = "roles" if config.get("hablantes") == "rol" else "A/B"
            sistema = m.get("maquina", {}).get("sistema", "?").split("-")[0]
            carpeta = p.parent.relative_to(raiz).as_posix()
            corridas.append({"id": carpeta + "|" + config["config"],
                             "nombre": f"{prompt or 'Sin prompt'} · {detector} · {roles} · {sistema} · {m['inicio'][11:19]}",
                             "inicio": m["inicio"], "fin": m["fin"], "carpeta": carpeta,
                             "modelo": config["modelo"] or "reglas", "prompt": config["prompt"],
                             "hablantes": config.get("hablantes", "ab"), "commit": m["codigo"]["commit"],
                             "politica": m.get("politica"), "parametros": m.get("parametros_slm"),
                             "resultados": resultados})
    corridas.sort(key=lambda r: r["inicio"], reverse=True)
    if not corridas:
        raise ValueError("No hay corridas completas para mostrar")
    return {"casos": casos, "corridas": corridas, "pendientes": pendientes,
            "hasta": max(r["fin"] for r in corridas)}
