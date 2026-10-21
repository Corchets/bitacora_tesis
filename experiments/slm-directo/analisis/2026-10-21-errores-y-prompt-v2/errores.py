"""Errores del prompt v1 y comparación con el v2 sobre las mismas corridas.

Para cada configuración (corrida + config) calcula:
- estafas con aviso y falsas alarmas, con la política del ensayo (primer alerta_sugerida);
- las mismas cuentas exigiendo además que la cita aparezca en lo dicho (`evidencia_en_texto`);
- líneas con riesgo >= 0,6 y sin alerta, y con alerta y riesgo < 0,5 (incoherencias);
- para cada estafa sin aviso: riesgo en la línea del pedido y riesgo máximo;
- Preventive@δ en líneas (METRICAS.md): estafas con aviso en la línea T_X − δ o antes,
  sobre las estafas que tienen esa marca, para δ = 0, 1 y 2 y X = T_R o T_C.

Cada configuración se informa sobre todos sus casos completos y por separado sobre los 53
históricos y los 97 de corpus_v2 (el v2 se escribió mirando solo los históricos).

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
# Corridas nuevas: todas las configs SLM de las carpetas *-nb32 (cola_m1.sh), en orden.
PROMPT = {"tarea": "v1", "v2": "v2"}
DELTAS = (0, 1, 2)
GRUPOS = [("todos", None), ("53 históricos", lambda g: g != "corpus_v2"), ("corpus_v2", lambda g: g == "corpus_v2")]


def nuevas() -> list[tuple[str, str, str]]:
    salida = []
    for carpeta in sorted(p.name for p in (SLM / "corridas").glob("*-nb32") if (p / "actualizaciones.csv").exists()):
        with (SLM / "corridas" / carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
            configs = dict.fromkeys(r["config"] for r in csv.DictReader(f) if r["detector"] == "slm")
        for config in configs:
            _, modelo, prompt, _ = config.split("|")
            tam = modelo.split(":")[1].split("-")[0].upper()
            salida.append((carpeta, config, f"{tam} {PROMPT.get(prompt, prompt)} · M1 nb32 · {carpeta[:17]}"))
    return salida


def leer(carpeta: str, config: str) -> dict[str, list[dict]]:
    por_caso = defaultdict(list)
    ruta = SLM / "corridas" / carpeta / "actualizaciones.csv"
    with ruta.open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            if r["config"] == config:
                por_caso[r["case_id"]].append(r)
    # Solo casos completos.
    return {c: filas for c, filas in por_caso.items() if len(filas) == len(casos.cargar_texto(c))}


def analizar(carpeta: str, config: str, filtro=None) -> dict:
    datos = leer(carpeta, config)
    if filtro:
        datos = {c: f for c, f in datos.items() if filtro(casos.cargar_referencia(c)["grupo"])}
    cuenta = dict.fromkeys(["vishing", "legitima", "vishing_aviso", "legitima_aviso", "vishing_aviso_con_cita",
                            "legitima_aviso_con_cita", "lineas", "alertas", "riesgo_alto_sin_alerta",
                            "alerta_con_riesgo_bajo"], 0)
    preventive = {f"{x}@{d}": [0, 0] for x in ("t_r", "t_c") for d in DELTAS}
    perdidas = []
    for cid, filas in sorted(datos.items()):
        ref = casos.cargar_referencia(cid)
        validas = [r for r in filas if r["valida"] == "true"]
        aviso = any(r["alerta_sugerida"] == "true" for r in validas)
        t_a = next((int(r["linea"]) for r in validas if r["alerta_sugerida"] == "true"), None)
        for x in ("t_r", "t_c"):
            marca = ref.get(f"{x}_linea") if ref["clase"] == "vishing" else None
            for d in DELTAS if marca else ():
                preventive[f"{x}@{d}"][0] += t_a is not None and t_a <= marca - d
                preventive[f"{x}@{d}"][1] += 1
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
    return {"corrida": carpeta, "config": config, **cuenta, "preventive": preventive, "vishing_sin_aviso": perdidas}


def wilson(k: int, n: int, z: float = 1.96) -> str:
    if not n:
        return "—"
    p, d = k / n, 1 + z * z / n
    c, m = p + z * z / (2 * n), z * (p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5
    return f"{100 * max(0, (c - m) / d):.0f}–{100 * min(1, (c + m) / d):.0f} %"


def main() -> int:
    configs = CONFIGS + nuevas()
    resultados = []
    print("| Configuración | Casos | Estafas con aviso | IC 95 % | Falsas alarmas | IC 95 % | Con cita verificada: estafas / FA | Riesgo ≥ 0,6 sin alerta | Alerta con riesgo < 0,5 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for carpeta, config, nombre in configs:
        for grupo, filtro in GRUPOS:
            r = analizar(carpeta, config, filtro)
            if not r.get("lineas"):
                continue
            r["nombre"], r["grupo"] = nombre, grupo
            resultados.append(r)
            print(f"| {nombre} | {grupo} | {r['vishing_aviso']}/{r['vishing']} | {wilson(r['vishing_aviso'], r['vishing'])} | "
                  f"{r['legitima_aviso']}/{r['legitima']} | {wilson(r['legitima_aviso'], r['legitima'])} | "
                  f"{r['vishing_aviso_con_cita']}/{r['vishing']} · {r['legitima_aviso_con_cita']}/{r['legitima']} | "
                  f"{r['riesgo_alto_sin_alerta']} de {r['lineas']} | {r['alerta_con_riesgo_bajo']} de {r['alertas']} |")
    print()
    print("| Configuración | Casos | " + " | ".join(f"Prev@{d} T_R" for d in DELTAS) + " | " + " | ".join(f"Prev@{d} T_C" for d in DELTAS) + " |")
    print("|---|---|" + "---|" * 2 * len(DELTAS))
    for r in resultados:
        pr = r["preventive"]
        print(f"| {r['nombre']} | {r['grupo']} | " + " | ".join(f"{pr[k][0]}/{pr[k][1]}" for k in pr) + " |")
    print()
    for r in resultados:
        if r["vishing_sin_aviso"] and r["grupo"] == "todos":
            print(f"{r['nombre']}: " + ", ".join(
                f"{p['caso']} ({p['pedido']}, riesgo en T_R {p['riesgo_en_t_r']}, máx {p['riesgo_max']})" for p in r["vishing_sin_aviso"]))
    (AQUI / "errores.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
