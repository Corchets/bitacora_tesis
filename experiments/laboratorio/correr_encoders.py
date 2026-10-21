#!/usr/bin/env python3
"""Suite de texto con encoders congelados en lugar del stub TF-IDF.

No cierra D09. No toca el oracle de chequear_casos.py. Escribe un CSV por
modelo en resultados/. Las reglas de incendio y la histeresis quedan igual.
"""

import csv
import gc
import statistics
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

import sklearn.metrics as skm

import chequear_casos as ch
import detector_encoder
import pipeline
import rules

AQUI = Path(__file__).resolve().parent
SEMILLAS = AQUI / "semillas.json"
CASOS = AQUI / "casos"
UMBRAL = 0.5
MODELOS = (
    "dccuchile/bert-base-spanish-wwm-cased",
    "pysentimiento/robertuito-base-uncased",
    "dccuchile/distilbert-base-spanish-uncased",
    "dccuchile/albert-tiny-spanish",
)
NOTA = (
    "Modo texto. Encoder congelado + regresion logistica sobre semillas.json inventadas. "
    "No cierra D09. T_A = turno de goteo. T_R = primer incendio. "
    "Sin audio: T_C, L_C, Preventive@δ, WER y RTF no aplican. "
    "Sin opinion solo si el turno esta vacio."
)


def _leer(rel: str) -> list[str]:
    return [
        linea.strip()
        for linea in (CASOS / rel).read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]


def correr(det, path: Path) -> dict:
    textos = [
        linea.strip()
        for linea in Path(path).read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.strip().startswith("#")
    ]
    contador = pipeline.ContadorGoteo(UMBRAL)
    turnos = []
    eventos = []
    turno_incendio = None
    turno_goteo = None
    for n, texto in enumerate(textos, 1):
        etiquetas = rules.incendio_en(texto)
        if etiquetas:
            eventos.append({"turno": n, "etiquetas": sorted(etiquetas), "texto": texto})
            if turno_incendio is None:
                turno_incendio = n
        p = det.puntaje(texto)
        if contador.agregar(p) and turno_goteo is None:
            turno_goteo = n
        turnos.append({"n": n, "texto": texto, "puntaje": pipeline._puntaje(p)})
    texto_final = " ".join(textos)
    ns = [n for n in (turno_incendio, turno_goteo) if n is not None]
    return {
        "turnos": turnos,
        "incendio": {"eventos": eventos},
        "goteo": {"disparo": turno_goteo is not None, "turno": turno_goteo},
        "latencia_decision_turno": min(ns) if ns else None,
        "terminos_criticos": {
            t: t in texto_final.lower() for t in pipeline.TERMINOS_CRITICOS
        },
        "memoria_pico_mb": pipeline.memoria_pico_mb(),
    }


def fila_de(rel, clase, r, esperado_etiquetas, fecha, commit, modelo):
    evs = r["incendio"]["eventos"]
    todas = sorted({e for ev in evs for e in ev["etiquetas"]})
    tr = evs[0]["turno"] if evs else None
    ta = r["goteo"]["turno"] if r["goteo"]["disparo"] else None
    lr = (tr - ta) if tr is not None and ta is not None else None
    puntajes = [t["puntaje"] for t in r["turnos"] if t["puntaje"] is not None]
    alerta = bool(evs) or r["goteo"]["disparo"]
    return {
        "fecha": fecha,
        "commit": commit,
        "detector_incendio": "reglas",
        "detector_goteo": modelo,
        "duracion_s": "",
        "caso": rel,
        "clase": clase,
        "n_turnos": len(r["turnos"]),
        "incendio": int(bool(evs)),
        "T_R_turno": tr if tr is not None else "",
        "etiquetas_incendio": "|".join(todas),
        "etiquetas_esperadas": "|".join(sorted(esperado_etiquetas)),
        "cobertura_etiquetas": int(esperado_etiquetas <= set(todas)) if clase == "V" else "",
        "goteo": int(r["goteo"]["disparo"]),
        "T_A_turno": ta if ta is not None else "",
        "umbral_goteo": UMBRAL,
        "L_R_turnos": lr if lr is not None else "",
        "latencia_decision_turno": r["latencia_decision_turno"] if r["latencia_decision_turno"] is not None else "",
        "T_C_turno": "",
        "L_C_turnos": "",
        "puntaje_max": max(puntajes) if puntajes else "",
        "puntajes": ",".join(
            f"t{t['n']}={t['puntaje']}" for t in r["turnos"] if t["puntaje"] is not None
        ),
        "falsa_alarma": int(clase == "L" and alerta),
        "terminos_criticos": "|".join(t for t, ok in r["terminos_criticos"].items() if ok),
        "memoria_pico_mb": r["memoria_pico_mb"],
        "typo_ok": "",
        "robusto_upper": "",
        "robusto_tildes": "",
        "robusto_muletilla": "",
        "nota": NOTA,
    }


def _igual(a: dict, b: dict) -> bool:
    ev_a = [(e["turno"], tuple(e["etiquetas"])) for e in a["incendio"]["eventos"]]
    ev_b = [(e["turno"], tuple(e["etiquetas"])) for e in b["incendio"]["eventos"]]
    return ev_a == ev_b and a["goteo"]["turno"] == b["goteo"]["turno"]


def ok_typo(rel, clase, etiquetas, turno) -> int:
    todas = {e for t in ch.con_typo(_leer(rel)) for e in rules.incendio_en(t)}
    if clase == "V" and turno is not None:
        return int(etiquetas <= todas)
    return int(not todas)


def ok_robusto(det, rel, limpio, modo) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".txt", encoding="utf-8") as f:
        f.write("\n".join(ch._perturbar(_leer(rel), modo)) + "\n")
        f.flush()
        perturbado = correr(det, Path(f.name))
    return int(_igual(limpio, perturbado))


def correr_modelo(model_id: str, fecha: str, commit: str) -> None:
    t0 = time.perf_counter()
    det = detector_encoder.DetectorEncoder(model_id, SEMILLAS)
    filas = []
    scores = []
    y = []
    limpios = {}
    for rel, clase, etiquetas, _turno, _got in ch.ESPERADO:
        r = correr(det, CASOS / rel)
        limpios[rel] = r
        filas.append(fila_de(rel, clase, r, etiquetas, fecha, commit, model_id))
        ps = [t["puntaje"] for t in r["turnos"] if t["puntaje"] is not None]
        scores.append(max(ps) if ps else 0.0)
        y.append(1 if clase == "V" else 0)
    r_ej = correr(det, AQUI / "ejemplo.txt")
    filas.append(fila_de("ejemplo.txt", "ejemplo", r_ej, {"REQUEST_AUTH_CODE"}, fecha, commit, model_id))

    for fila, (rel, clase, etiquetas, turno, _got) in zip(filas, ch.ESPERADO):
        fila["typo_ok"] = ok_typo(rel, clase, etiquetas, turno)
        for modo, col in (
            ("upper", "robusto_upper"),
            ("tildes", "robusto_tildes"),
            ("muletilla", "robusto_muletilla"),
        ):
            fila[col] = ok_robusto(det, rel, limpios[rel], modo)

    duracion_s = round(time.perf_counter() - t0, 3)
    v = [f for f in filas if f["clase"] == "V"]
    legit = [f for f in filas if f["clase"] == "L"]
    lrs = [f["L_R_turnos"] for f in v if f["L_R_turnos"] != ""]
    qs = statistics.quantiles(lrs, n=4, method="inclusive") if len(lrs) >= 2 else []
    tp = sum(f["goteo"] for f in v)
    fp = sum(f["goteo"] for f in legit)
    fn = len(v) - tp
    prec = tp / (tp + fp) if tp + fp else ""
    rec = tp / (tp + fn) if tp + fn else ""
    f1 = (2 * prec * rec / (prec + rec)) if prec != "" and rec != "" and (prec + rec) else ""
    auroc = skm.roc_auc_score(y, scores) if len(set(y)) > 1 else ""
    auprc = skm.average_precision_score(y, scores) if len(set(y)) > 1 else ""
    margen_vals = [float(f["puntaje_max"]) for f in legit if f["puntaje_max"] != ""]
    margen = max(margen_vals) if margen_vals else ""
    for f in filas:
        f["duracion_s"] = duracion_s
    filas.append(
        {
            "fecha": fecha,
            "commit": commit,
            "detector_incendio": "reglas",
            "detector_goteo": model_id,
            "duracion_s": duracion_s,
            "caso": "_suite",
            "clase": "resumen",
            "n_turnos": len(ch.ESPERADO),
            "incendio": f"{sum(f['incendio'] for f in v)}/{len(v)}",
            "T_R_turno": "",
            "etiquetas_incendio": "",
            "etiquetas_esperadas": "",
            "cobertura_etiquetas": f"{sum(f['cobertura_etiquetas'] for f in v)}/{len(v)}",
            "goteo": f"{tp}/{len(v)}",
            "T_A_turno": "",
            "umbral_goteo": UMBRAL,
            "L_R_turnos": statistics.median(lrs) if lrs else "",
            "latencia_decision_turno": "",
            "T_C_turno": "",
            "L_C_turnos": "",
            "puntaje_max": margen,
            "puntajes": f"L_R_q1={qs[0]};L_R_q3={qs[2]}" if qs else "",
            "falsa_alarma": f"{sum(f['falsa_alarma'] for f in legit)}/{len(legit)}",
            "terminos_criticos": (
                f"precision_goteo={prec};recall_goteo={rec};f1_goteo={f1};"
                f"auroc_max_puntaje={auroc if auroc == '' else f'{auroc:.3f}'};"
                f"auprc_max_puntaje={auprc if auprc == '' else f'{auprc:.3f}'}"
            ),
            "memoria_pico_mb": filas[0]["memoria_pico_mb"],
            "typo_ok": f"{sum(f['typo_ok'] for f in filas if f['typo_ok'] != '')}/{len(ch.ESPERADO)}",
            "robusto_upper": f"{sum(f['robusto_upper'] for f in filas if f['robusto_upper'] != '')}/{len(ch.ESPERADO)}",
            "robusto_tildes": f"{sum(f['robusto_tildes'] for f in filas if f['robusto_tildes'] != '')}/{len(ch.ESPERADO)}",
            "robusto_muletilla": f"{sum(f['robusto_muletilla'] for f in filas if f['robusto_muletilla'] != '')}/{len(ch.ESPERADO)}",
            "nota": (
                "Resumen de los 21 casos (ejemplo aparte). "
                "24 frases inventadas: la regresion de arriba se sobreajusta y estos numeros "
                "no sustituyen al corpus ni al piloto. "
                "precision/recall/F1 del goteo como alerta, V=positivo. "
                "mediana de L_R en L_R_turnos. AUROC/AUPRC usan el puntaje maximo del caso."
            ),
        }
    )
    slug = model_id.split("/")[-1]
    out = AQUI / "resultados" / "2026-09-24" / f"resultados-2026-09-24-{slug}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    print(f"{model_id} {duracion_s}s goteo {tp}/{len(v)} falsas {fp}/{len(legit)} -> {out.name}", flush=True)
    del det
    gc.collect()


DIFICILES = (
    ("dificiles/vishing/digitos-sin-palabra.txt", "V", {"REQUEST_AUTH_CODE"}),
    ("dificiles/vishing/pantalla-sin-programa.txt", "V", {"REQUEST_REMOTE_ACCESS"}),
    ("dificiles/vishing/giro-sin-plata.txt", "V", {"REQUEST_TRANSFER"}),
    ("dificiles/legitima/portero-codigo-puerta.txt", "L", set()),
    ("dificiles/legitima/banco-gasto-sin-pedido.txt", "L", set()),
)
NOTA_DIFICIL = (
    "Caso dificil agregado el 2026-09-24. Pesos leidos desde experiments/laboratorio/modelos/. "
    + NOTA
)


def _resumen(filas: list[dict], fecha: str, commit: str, modelo: str, nota_extra: str) -> dict:
    v = [f for f in filas if f["clase"] == "V"]
    legit = [f for f in filas if f["clase"] == "L"]
    lrs = []
    for f in v:
        if f["L_R_turnos"] != "":
            lrs.append(float(f["L_R_turnos"]))
    qs = statistics.quantiles(lrs, n=4, method="inclusive") if len(lrs) >= 2 else []
    def _uno(fila, col):
        return int(fila[col]) if str(fila[col]) in ("0", "1") else 0
    tp = sum(_uno(f, "goteo") for f in v)
    fp = sum(_uno(f, "goteo") for f in legit)
    fn = len(v) - tp
    prec = tp / (tp + fp) if tp + fp else ""
    rec = tp / (tp + fn) if tp + fn else ""
    f1 = (2 * prec * rec / (prec + rec)) if prec != "" and rec != "" and (prec + rec) else ""
    scores, y = [], []
    for f in v + legit:
        if f["puntaje_max"] == "":
            scores.append(0.0)
        else:
            scores.append(float(f["puntaje_max"]))
        y.append(1 if f["clase"] == "V" else 0)
    auroc = skm.roc_auc_score(y, scores) if len(set(y)) > 1 else ""
    auprc = skm.average_precision_score(y, scores) if len(set(y)) > 1 else ""
    margen_vals = [float(f["puntaje_max"]) for f in legit if f["puntaje_max"] != ""]
    n_typo = [f for f in filas if str(f["typo_ok"]) in ("0", "1")]
    def _cuenta(col):
        return f"{sum(int(f[col]) for f in n_typo)}/{len(n_typo)}" if n_typo else ""
    return {
        "fecha": fecha,
        "commit": commit,
        "detector_incendio": "reglas",
        "detector_goteo": modelo,
        "duracion_s": "",
        "caso": "_suite",
        "clase": "resumen",
        "n_turnos": len(v) + len(legit),
        "incendio": f"{sum(_uno(f, 'incendio') for f in v)}/{len(v)}",
        "T_R_turno": "",
        "etiquetas_incendio": "",
        "etiquetas_esperadas": "",
        "cobertura_etiquetas": f"{sum(int(f['cobertura_etiquetas']) for f in v if str(f['cobertura_etiquetas']) in ('0', '1'))}/{len(v)}",
        "goteo": f"{tp}/{len(v)}",
        "T_A_turno": "",
        "umbral_goteo": UMBRAL,
        "L_R_turnos": statistics.median(lrs) if lrs else "",
        "latencia_decision_turno": "",
        "T_C_turno": "",
        "L_C_turnos": "",
        "puntaje_max": max(margen_vals) if margen_vals else "",
        "puntajes": f"L_R_q1={qs[0]};L_R_q3={qs[2]}" if qs else "",
        "falsa_alarma": f"{sum(_uno(f, 'falsa_alarma') for f in legit)}/{len(legit)}",
        "terminos_criticos": (
            f"precision_goteo={prec};recall_goteo={rec};f1_goteo={f1};"
            f"auroc_max_puntaje={auroc if auroc == '' else f'{auroc:.3f}'};"
            f"auprc_max_puntaje={auprc if auprc == '' else f'{auprc:.3f}'}"
        ),
        "memoria_pico_mb": filas[0]["memoria_pico_mb"],
        "typo_ok": _cuenta("typo_ok"),
        "robusto_upper": _cuenta("robusto_upper"),
        "robusto_tildes": _cuenta("robusto_tildes"),
        "robusto_muletilla": _cuenta("robusto_muletilla"),
        "nota": nota_extra,
    }


def _sumar_en(csv_path: Path, det, modelo: str, fecha: str, commit: str, nota_fila: str, nota_suite: str) -> None:
    t0 = time.perf_counter()
    nuevas = []
    limpios = {}
    for rel, clase, etiquetas in DIFICILES:
        r = correr(det, CASOS / rel)
        limpios[rel] = r
        fila = fila_de(rel, clase, r, etiquetas, fecha, commit, modelo)
        fila["nota"] = nota_fila
        fila["typo_ok"] = ok_typo(rel, clase, etiquetas, 1 if clase == "V" else None)
        for modo, col in (
            ("upper", "robusto_upper"),
            ("tildes", "robusto_tildes"),
            ("muletilla", "robusto_muletilla"),
        ):
            fila[col] = ok_robusto(det, rel, limpios[rel], modo)
        nuevas.append(fila)
        print(f"  {rel} incendio={fila['incendio']} goteo={fila['goteo']} tA={fila['T_A_turno']}", flush=True)
    duracion_s = round(time.perf_counter() - t0, 3)
    with csv_path.open(encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    previas = [f for f in filas if f["caso"] != "_suite" and not f["caso"].startswith("dificiles/")]
    for fila in nuevas:
        fila["duracion_s"] = duracion_s
    todas = previas + nuevas
    resumen = _resumen(
        todas, fecha, commit, modelo,
        nota_suite + f" duracion_s de esta pasada (solo dificiles)={duracion_s}.",
    )
    resumen["duracion_s"] = duracion_s
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(todas + [resumen])
    print(f"sumados {len(nuevas)} en {csv_path.name} ({duracion_s}s)", flush=True)


def sumar_dificiles() -> None:
    import detector

    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=AQUI.parents[1], text=True
    ).strip()
    fecha = datetime.now().astimezone().isoformat(timespec="seconds")
    nota_suite = (
        "Resumen de los 21 casos, ejemplo aparte, mas los 5 dificiles. "
        "Los dificiles no entran al oracle de chequear_casos.py. "
        "24 frases inventadas: no sustituyen al corpus ni al piloto."
    )
    det = detector.DetectorTfidf(SEMILLAS)
    _sumar_en(
        AQUI / "resultados" / "2026-09-24" / "resultados-2026-09-24.csv",
        det, "tfidf-stub-semillas", fecha, commit,
        "Caso dificil agregado el 2026-09-24. Modo texto. TF-IDF + regresion logistica sobre semillas.json inventadas. No cierra D09. T_A = turno de goteo. T_R = primer incendio. Sin audio: T_C, L_C, Preventive@δ, WER y RTF no aplican.",
        nota_suite,
    )
    del det
    gc.collect()
    for model_id in MODELOS:
        slug = model_id.split("/")[-1]
        local = AQUI / "modelos" / slug
        det = detector_encoder.DetectorEncoder(str(local), SEMILLAS)
        _sumar_en(
            AQUI / "resultados" / "2026-09-24" / f"resultados-2026-09-24-{slug}.csv",
            det, model_id, fecha, commit, NOTA_DIFICIL, nota_suite,
        )
        del det
        gc.collect()


def main() -> None:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=AQUI.parents[1], text=True
    ).strip()
    fecha = datetime.now().astimezone().isoformat(timespec="seconds")
    for model_id in MODELOS:
        correr_modelo(model_id, fecha, commit)


if __name__ == "__main__":
    main()
