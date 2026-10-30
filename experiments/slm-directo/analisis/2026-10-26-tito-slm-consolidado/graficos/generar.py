#!/usr/bin/env python3
"""Construye el informe visual autónomo, sin ejecutar modelos ni usar reserva.

Uso desde cualquier carpeta:
    python /ruta/a/graficos/generar.py

Datos: cobertura.json, CSV de las corridas canónicas, las dos
demostraciones y referencias de sus casos explícitos. La presentación vive en
plantilla.html. index.html es la salida generada, legible y sin dependencias web.
"""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANALISIS = HERE.parent
LAB = ANALISIS.parents[1]

# Orden y nombres de presentación: siempre asociados al identificador del modelo.
MODEL_LABELS = {
    "qwen3.5:4b-q4_K_M": ("Qwen 3.5 · 4B", "Q4_K_M", 71),
    "qwen3.5:0.8b-q8_0": ("Qwen 3.5 · 0.8B", "Q8_0", 72),
    "qwen3.5:0.8b": ("Qwen 3.5 · 0.8B", "tag sin sufijo", 72),
    "qwen3.5:2b-q8_0": ("Qwen 3.5 · 2B", "Q8_0", 72),
    "qwen3.5:9b-q4_K_M": ("Qwen 3.5 · 9B", "Q4_K_M", 72),
    "llama3.2:1b-instruct-q4_K_M": ("Llama 3.2 · 1B", "Q4_K_M", 73),
}
CASE_LABELS = {
    "SC-SOPORTE-REMOTO-01-e01": ("Soporte remoto", "SC-SOPORTE"),
    "SC-FAMILIAR-DINERO-01-e01": ("Familiar que pide dinero", "SC-FAMILIAR"),
    "TR-04-pedido-tras-charla-larga": ("Pedido tras una charla larga", "TR-04"),
    "TR-07-pedido-partido-en-dos-lineas": ("Pedido dividido en dos líneas", "TR-07"),
    "LG-SUPPORT-INFO-01-e02": ("Asistencia legítima", "LG-SUPPORT"),
    "TR-06-banco-alerta-legitima": ("Alerta bancaria legítima", "TR-06"),
    "TR-08-frase-cortada-candado": ("Frase cortada: candado", "TR-08"),
    "TR-11-familiar-real-pide-plata": ("Familiar real que pide plata", "TR-11"),
    "SC-WA-CODE-01-e01": ("Pedido de código de WhatsApp", "SC-WA-CODE"),
    "LG-WA-CONSULTA-01-e01": ("Consulta legítima de WhatsApp", "LG-WA-CONSULTA"),
}
ALTERNATIVES = {
    "TR-04-pedido-tras-charla-larga": {"tr": 21, "tc": 22},
    "TR-07-pedido-partido-en-dos-lineas": {"tr": 8, "tc": 9},
}
DEMOS = {
    "69": "2026-10-26_125526_demo-tito-slm-simulado",
    "70": "2026-10-26_132027_tito-real-8casos",
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def group_rows(run_name: str) -> dict[str, dict[str, list[dict]]]:
    """Agrupa por variante y conversación; conserva las consultas omitidas."""
    grouped = {"directo": defaultdict(list), "filtrado": defaultdict(list)}
    with (LAB / "corridas" / run_name / "actualizaciones.csv").open(
        encoding="utf-8-sig", newline=""
    ) as stream:
        for row in csv.DictReader(stream):
            config = row["config"]
            if config.startswith("tito-slm|"):
                variant = "filtrado"
            elif config.startswith("slm|"):
                variant = "directo"
            else:
                continue
            grouped[variant][row["case_id"]].append(row)
    return grouped


def summarize(rows: list[dict], filtered: bool) -> dict:
    ordered = sorted(rows, key=lambda row: int(row["linea"]))
    calls = [r for r in ordered if not filtered or r["consulta"] in {"slm_valida", "slm_fallo"}]
    alert = next((r for r in ordered if r["aviso"] == "true"), None)
    failures = [
        int(r["linea"]) for r in calls
        if r["valida"] == "false" or r.get("error", "").strip()
    ]
    return {
        "lines": len(ordered),
        "calls": len(calls),
        "avoided": len(ordered) - len(calls),
        "tokens": sum(int(r.get(k) or 0) for r in calls for k in ("tokens_prompt", "tokens_salida")),
        "ms": round(sum(float(r["ms"] or 0) for r in ordered), 1),
        "failures": failures,
        "gate": int(calls[0]["linea"]) if filtered and calls else None,
        "alert": int(alert["linea"]) if alert else None,
        "reason": alert["motivo"] if alert else "",
        "evidence": alert["evidencia"] if alert else "",
        "literal": alert["evidencia_en_texto"] == "true" if alert else None,
    }


def case_data(case_id: str) -> dict:
    """Solo lee los IDs presentes en las corridas explícitas del informe."""
    reference = read_json(LAB / "casos" / "referencia" / f"{case_id}.json")
    if reference.get("particion", "desarrollo") != "desarrollo":
        raise ValueError(f"El informe no puede incluir reserva: {case_id}")
    transcript = []
    for number, line in enumerate(
        (LAB / "casos" / "texto" / f"{case_id}.txt").read_text(encoding="utf-8").splitlines(), 1
    ):
        speaker, text = line.split(": ", 1)
        transcript.append({"line": number, "speaker": speaker, "text": text})
    label, short = CASE_LABELS[case_id]
    return {
        "id": case_id, "label": label, "short": short,
        "fraud": reference["clase"] == "vishing",
        "tr": reference["t_r_linea"], "tc": reference["t_c_linea"],
        "alternative": ALTERNATIVES.get(case_id),
        "description": reference["que_prueba"],
        "lines": len(transcript), "transcript": transcript,
    }


def load_run(run_name: str) -> dict:
    grouped = group_rows(run_name)
    case_ids = list(grouped["directo"])
    cases = {
        case_id: {
            variant: summarize(grouped[variant][case_id], variant == "filtrado")
            for variant in ("directo", "filtrado")
        }
        for case_id in case_ids
    }
    return {"run": run_name, "cases": cases}


def build_report() -> dict:
    coverage = read_json(ANALISIS / "cobertura.json")
    if not coverage["matriz_ok"]:
        raise ValueError("La cobertura consolidada contiene errores; revisar antes de graficar.")
    models = []
    for model_id, (name, quantization, ticket) in MODEL_LABELS.items():
        aggregate = coverage["modelos"][model_id]
        run = load_run(aggregate["corrida"])
        for variant in ("directo", "filtrado"):
            # Impide presentar agregados y detalles que provengan de salidas distintas.
            totals = aggregate[variant]
            details = [case[variant] for case in run["cases"].values()]
            for field, total_key in (("calls", "consultas_slm"), ("tokens", "tokens"), ("avoided", "evitadas")):
                if sum(d[field] for d in details) != totals[total_key]:
                    raise ValueError(f"Discrepancia {model_id}/{variant}/{field}")
            alerts = {key: c[variant]["alert"] for key, c in run["cases"].items() if c[variant]["alert"] is not None}
            if alerts != totals["avisos"]:
                raise ValueError(f"Discrepancia de avisos: {model_id}/{variant}")
            if abs(sum(d["ms"] for d in details) - totals["ms_total"]) > 1:
                raise ValueError(f"Discrepancia de costo: {model_id}/{variant}")
            if sum(len(d["failures"]) for d in details) != totals["fallos_slm"]:
                raise ValueError(f"Discrepancia de fallos: {model_id}/{variant}")
        models.append({
            "id": model_id, "name": name, "quantization": quantization,
            "ticket": ticket, **run,
            "directo": aggregate["directo"], "filtrado": aggregate["filtrado"],
        })
    main_case_ids = [cid for cid in CASE_LABELS if cid in models[0]["cases"]]
    if any(set(model["cases"]) != set(main_case_ids) for model in models):
        raise ValueError("Los modelos no comparten exactamente las mismas conversaciones.")
    demos = {ticket: load_run(run) for ticket, run in DEMOS.items()}
    all_case_ids = set(main_case_ids)
    for demo in demos.values():
        all_case_ids.update(demo["cases"])
    artifact = read_json(LAB / "tito_logreg.json")
    return {
        "date": "2026-10-26", "evaluations": coverage["evaluaciones_conversacion"],
        "models": models, "mainCases": main_case_ids,
        "cases": {cid: case_data(cid) for cid in sorted(all_case_ids)},
        "demos": demos,
        "training": {**artifact["datos"], "seed": artifact["config_regresion"]["semilla"]},
    }


def main() -> None:
    report = build_report()
    template = (HERE / "plantilla.html").read_text(encoding="utf-8")
    marker = "<!-- REPORT_DATA -->"
    if template.count(marker) != 1:
        raise ValueError("La plantilla debe contener exactamente un marcador de datos.")
    data = json.dumps(report, ensure_ascii=False, indent=2).replace("<", "\\u003c")
    output = template.replace(marker, f'<script type="application/json" id="report-data">\n{data}\n  </script>')
    (HERE / "index.html").write_text(output, encoding="utf-8")
    print(f"Informe generado: {len(report['models'])} modelos, {len(report['mainCases'])} conversaciones, {report['evaluations']} evaluaciones.")


if __name__ == "__main__":
    main()
