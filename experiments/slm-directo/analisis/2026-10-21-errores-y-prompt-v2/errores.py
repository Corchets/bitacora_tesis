"""Errores del prompt v1 y comparación con el v2 sobre las mismas corridas.

Para cada configuración (corrida + config) calcula:
- estafas con aviso y falsas alarmas, con la política del ensayo (primer alerta_sugerida);
- las mismas cuentas exigiendo además que la cita aparezca en lo dicho (`evidencia_en_texto`);
- líneas con riesgo >= 0,6 y sin alerta, y con alerta y riesgo < 0,5 (incoherencias);
- para cada estafa sin aviso: riesgo en la línea del pedido y riesgo máximo.

    python analisis/2026-10-21-errores-y-prompt-v2/errores.py
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
sys.path.insert(0, str(SLM))

import casos  # noqa: E402

CONFIGS = [
    ("2026-10-14_173532_demo-qwen3.5-0.8b", "slm|qwen3.5:0.8b|tarea|ab", "0.8B v1 · Windows"),
    ("2026-10-14_172930_demo-qwen3.5-2b", "slm|qwen3.5:2b|tarea|ab", "2B v1 · Windows (1)"),
    ("2026-10-14_175451_demo-qwen3.5-2b", "slm|qwen3.5:2b|tarea|ab", "2B v1 · Windows (2)"),
    ("2026-10-14_174602_demo-qwen3.5-4b", "slm|qwen3.5:4b|tarea|ab", "4B v1 · Windows"),
    ("2026-10-17_150516_m1-gguf", "slm|qwen3.5:0.8b-q8_0|tarea|ab", "0.8B v1 · M1"),
    ("2026-10-17_150516_m1-gguf", "slm|qwen3.5:2b-q8_0|tarea|ab", "2B v1 · M1"),
    ("2026-10-17_150516_m1-gguf", "slm|qwen3.5:4b-q4_K_M|tarea|ab", "4B v1 · M1 (parcial)"),
]
# Corridas nuevas: se agregan si existen.
NUEVAS = [
    ("2026-10-21_182201_m1-0.8b-v1v2-nb32", "slm|qwen3.5:0.8b-q8_0|tarea|ab", "0.8B v1 · M1 nb32"),
    ("2026-10-21_182201_m1-0.8b-v1v2-nb32", "slm|qwen3.5:0.8b-q8_0|v2|ab", "0.8B v2 · M1 nb32"),
]


def leer(carpeta: str, config: str) -> dict[str, list[dict]]:
    por_caso = defaultdict(list)
    ruta = SLM / "corridas" / carpeta / "actualizaciones.csv"
    with ruta.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["config"] == config:
                por_caso[r["case_id"]].append(r)
    # Solo casos completos.
    return {c: filas for c, filas in por_caso.items() if len(filas) == len(casos.cargar_texto(c))}


def analizar(carpeta: str, config: str) -> dict:
    datos = leer(carpeta, config)
    cuenta = defaultdict(int)
    perdidas = []
    for cid, filas in sorted(datos.items()):
        ref = casos.cargar_referencia(cid)
        validas = [r for r in filas if r["valida"] == "true"]
        aviso = any(r["alerta_sugerida"] == "true" for r in validas)
        con_cita = any(r["alerta_sugerida"] == "true" and r["evidencia_en_texto"] == "true" for r in validas)
        clase = "vishing" if ref["clase"] == "vishing" else "legitima"
        cuenta[clase] += 1
        cuenta[f"{clase}_aviso"] += aviso
        cuenta[f"{clase}_aviso_con_cita"] += con_cita
        for r in validas:
            riesgo, alerta = float(r["riesgo"]), r["alerta_sugerida"] == "true"
            cuenta["lineas"] += 1
            cuenta["alertas"] += alerta
            cuenta["riesgo_alto_sin_alerta"] += riesgo >= 0.6 and not alerta
            cuenta["alerta_con_riesgo_bajo"] += riesgo < 0.5 and alerta
        if ref["clase"] == "vishing" and not aviso:
            tr = ref.get("t_r_linea")
            en_tr = next((float(r["riesgo"]) for r in validas if tr and int(r["linea"]) == tr), None)
            perdidas.append({"caso": cid, "pedido": ref.get("pedido"), "t_r": tr, "riesgo_en_t_r": en_tr,
                             "riesgo_max": max((float(r["riesgo"]) for r in validas), default=None)})
    return {"corrida": carpeta, "config": config, **cuenta, "vishing_sin_aviso": perdidas}


def main() -> int:
    configs = CONFIGS + [c for c in NUEVAS if (SLM / "corridas" / c[0] / "actualizaciones.csv").exists()]
    resultados = []
    print("| Configuración | Estafas con aviso | Falsas alarmas | Con cita verificada: estafas / FA | Riesgo ≥ 0,6 sin alerta | Alerta con riesgo < 0,5 |")
    print("|---|---|---|---|---|---|")
    for carpeta, config, nombre in configs:
        r = analizar(carpeta, config)
        if not r.get("lineas"):
            continue
        r["nombre"] = nombre
        resultados.append(r)
        print(f"| {nombre} | {r['vishing_aviso']}/{r['vishing']} | {r['legitima_aviso']}/{r['legitima']} | "
              f"{r['vishing_aviso_con_cita']}/{r['vishing']} · {r['legitima_aviso_con_cita']}/{r['legitima']} | "
              f"{r['riesgo_alto_sin_alerta']} de {r['lineas']} | {r['alerta_con_riesgo_bajo']} de {r['alertas']} |")
    print()
    for r in resultados:
        if r["vishing_sin_aviso"]:
            print(f"{r['nombre']}: " + ", ".join(
                f"{p['caso']} ({p['pedido']}, riesgo en T_R {p['riesgo_en_t_r']}, máx {p['riesgo_max']})" for p in r["vishing_sin_aviso"]))
    (AQUI / "errores.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
