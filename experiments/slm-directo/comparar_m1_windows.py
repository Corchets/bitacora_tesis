#!/usr/bin/env python3
"""Comparador de reproducibilidad entre Apple M1 y Windows 11 (#50).

Compara caso por caso las decisiones del SLM en Apple M1 (Metal GGUF) contra
las corridas canónicas de Windows 11 (GPU GGUF):
- Mismo caso con/sin aviso
- Misma línea de aviso
- Diferencias observadas
- Latencias (p50 / p95) por modelo y plataforma.

Guarda el análisis en experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/
(README.md y comparacion_m1_vs_windows.json).
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path
from typing import Any

DIR_SLM = Path(__file__).resolve().parent
DIR_CORRIDAS = DIR_SLM / "corridas"
DIR_ANALISIS = DIR_SLM / "analisis" / "2026-10-17-m1-vs-windows"

CORRIDAS_WINDOWS = {
    "0.8b": DIR_CORRIDAS / "2026-10-14_173532_demo-qwen3.5-0.8b",
    "2b": DIR_CORRIDAS / "2026-10-14_175451_demo-qwen3.5-2b",
    "4b": DIR_CORRIDAS / "2026-10-14_174602_demo-qwen3.5-4b",
}


def cargar_avisos_y_tiempos(ruta_actualizaciones: Path, modelo_filtro: str | None = None) -> dict[str, dict[str, Any]]:
    """Lee actualizaciones.csv y extrae para cada caso el primer aviso y la lista de latencias ms."""
    casos: dict[str, dict[str, Any]] = {}

    with open(ruta_actualizaciones, "r", encoding="utf-8-sig") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            mod = fila.get("modelo", "")
            if modelo_filtro and modelo_filtro not in mod:
                continue

            cid = fila["case_id"]
            if cid not in casos:
                casos[cid] = {
                    "case_id": cid,
                    "aviso": False,
                    "linea_aviso": None,
                    "motivo_aviso": "",
                    "evidencia_aviso": "",
                    "ms_lista": [],
                }

            if fila.get("ms"):
                try:
                    casos[cid]["ms_lista"].append(float(fila["ms"]))
                except ValueError:
                    pass

            es_aviso = str(fila.get("aviso", "")).strip().lower() in ("true", "1")
            if es_aviso and not casos[cid]["aviso"]:
                casos[cid]["aviso"] = True
                casos[cid]["linea_aviso"] = int(fila["linea"])
                casos[cid]["motivo_aviso"] = fila.get("motivo", "")
                casos[cid]["evidencia_aviso"] = fila.get("evidencia", "")

    return casos


def calcular_percentiles(valores: list[float]) -> tuple[float | None, float | None]:
    if not valores:
        return None, None
    s = sorted(valores)
    p50 = statistics.median(s)
    # p95
    k = (len(s) - 1) * 0.95
    f = int(k)
    c = f + 1 if f + 1 < len(s) else f
    p95 = s[f] + (k - f) * (s[c] - s[f])
    return round(p50, 1), round(p95, 1)


def comparar_modelos(carpeta_m1: Path) -> dict[str, Any]:
    ruta_act_m1 = carpeta_m1 / "actualizaciones.csv"
    if not ruta_act_m1.exists():
        raise FileNotFoundError(f"No existe {ruta_act_m1}")

    manifiesto_m1 = json.loads((carpeta_m1 / "manifiesto.json").read_text(encoding="utf-8"))

    resultado_total: dict[str, Any] = {
        "m1_corrida": carpeta_m1.name,
        "m1_inicio": manifiesto_m1.get("inicio"),
        "m1_fin": manifiesto_m1.get("fin"),
        "modelos": {},
    }

    mapeo_modelos = {
        "0.8b": "qwen3.5:0.8b-q8_0",
        "2b": "qwen3.5:2b-q8_0",
        "4b": "qwen3.5:4b-q4_K_M",
    }

    for clave_tam, mod_m1 in mapeo_modelos.items():
        dir_win = CORRIDAS_WINDOWS[clave_tam]
        if not dir_win.exists():
            continue
        manifiesto_win = json.loads((dir_win / "manifiesto.json").read_text(encoding="utf-8"))

        datos_win = cargar_avisos_y_tiempos(dir_win / "actualizaciones.csv")
        datos_m1 = cargar_avisos_y_tiempos(ruta_act_m1, modelo_filtro=mod_m1)

        if not datos_m1:
            continue

        todos_casos = sorted(set(datos_win.keys()) | set(datos_m1.keys()))

        coincidencias_aviso = 0
        coincidencias_linea = 0
        diferencias = []
        filas_comparacion = []

        todos_ms_win = []
        todos_ms_m1 = []

        for cid in todos_casos:
            cw = datos_win.get(cid, {"aviso": False, "linea_aviso": None, "motivo_aviso": "", "ms_lista": []})
            cm = datos_m1.get(cid, {"aviso": False, "linea_aviso": None, "motivo_aviso": "", "ms_lista": []})

            todos_ms_win.extend(cw["ms_lista"])
            todos_ms_m1.extend(cm["ms_lista"])

            mismo_aviso = cw["aviso"] == cm["aviso"]
            misma_linea = cw["linea_aviso"] == cm["linea_aviso"]

            if mismo_aviso:
                coincidencias_aviso += 1
            if misma_linea:
                coincidencias_linea += 1
            else:
                diferencias.append({
                    "case_id": cid,
                    "win_aviso": cw["aviso"],
                    "win_linea": cw["linea_aviso"],
                    "win_motivo": cw["motivo_aviso"],
                    "m1_aviso": cm["aviso"],
                    "m1_linea": cm["linea_aviso"],
                    "m1_motivo": cm["motivo_aviso"],
                })

            filas_comparacion.append({
                "case_id": cid,
                "win_aviso": cw["aviso"],
                "win_linea": cw["linea_aviso"],
                "m1_aviso": cm["aviso"],
                "m1_linea": cm["linea_aviso"],
                "coincide_aviso": mismo_aviso,
                "coincide_linea": misma_linea,
            })

        p50_w, p95_w = calcular_percentiles(todos_ms_win)
        p50_m, p95_m = calcular_percentiles(todos_ms_m1)

        total_casos = len(todos_casos)
        resultado_total["modelos"][clave_tam] = {
            "modelo_win": manifiesto_win.get("comando", ""),
            "modelo_m1": mod_m1,
            "total_casos": total_casos,
            "coincidencias_aviso": coincidencias_aviso,
            "tasa_coincidencia_aviso": round(coincidencias_aviso / total_casos, 3) if total_casos else 0.0,
            "coincidencias_linea": coincidencias_linea,
            "tasa_coincidencia_linea": round(coincidencias_linea / total_casos, 3) if total_casos else 0.0,
            "total_diferencias": len(diferencias),
            "latencia_win_p50_ms": p50_w,
            "latencia_win_p95_ms": p95_w,
            "latencia_m1_p50_ms": p50_m,
            "latencia_m1_p95_ms": p95_m,
            "diferencias": diferencias,
            "detalle_casos": filas_comparacion,
        }

    return resultado_total


def generar_markdown(res: dict[str, Any], ruta_md: Path) -> None:
    lineas = [
        "# Comparación de Reproducibilidad entre Máquinas: Apple M1 vs Windows 11 (#50)",
        "",
        "> **Advertencia metodológica:** Material de desarrollo con casos escritos y semillas fijadas (seed=42). "
        "Las mediciones corresponden a hardware y motores distintos (Apple M1 8 GB Metal GGUF vs Windows 11 NVIDIA GPU GGUF). "
        "Sin interpretar más allá de lo estrictamente observado empíricamente.",
        "",
        f"- **Corrida M1:** `{res['m1_corrida']}`",
        f"- **Fecha M1:** {res.get('m1_inicio', 'desconocido')} a {res.get('m1_fin', 'desconocido')}",
        "",
        "## 1. Resumen de Acuerdo por Modelo",
        "",
        "| Modelo | Casos | Acuerdo Aviso (Sí/No) | Acuerdo Línea Exacta | Latencia M1 (p50 / p95) | Latencia Win (p50 / p95) |",
        "|---|---|---|---|---|---|",
    ]

    for tam, info in res["modelos"].items():
        ac_aviso = f"{info['coincidencias_aviso']}/{info['total_casos']} ({info['tasa_coincidencia_aviso']*100:.1f}%)"
        ac_lin = f"{info['coincidencias_linea']}/{info['total_casos']} ({info['tasa_coincidencia_linea']*100:.1f}%)"
        lat_m1 = f"{info['latencia_m1_p50_ms']} ms / {info['latencia_m1_p95_ms']} ms"
        lat_win = f"{info['latencia_win_p50_ms']} ms / {info['latencia_win_p95_ms']} ms"
        lineas.append(f"| **{tam.upper()}** (`{info['modelo_m1']}`) | {info['total_casos']} | {ac_aviso} | {ac_lin} | {lat_m1} | {lat_win} |")

    lineas.append("")
    lineas.append("## 2. Diferencias Observadas Caso por Caso")
    lineas.append("")

    for tam, info in res["modelos"].items():
        lineas.append(f"### Modelo {tam.upper()} (`{info['modelo_m1']}`)")
        difs = info["diferencias"]
        if not difs:
            lineas.append("No se observaron diferencias en ningún caso (acuerdo 100% en aviso y línea).")
        else:
            lineas.append(f"Se registraron {len(difs)} discrepancias entre plataformas:")
            lineas.append("")
            lineas.append("| Caso | Windows (Aviso @ Línea) | M1 (Aviso @ Línea) | Motivo Windows | Motivo M1 |")
            lineas.append("|---|---|---|---|---|")
            for d in difs:
                w_str = f"{'Sí' if d['win_aviso'] else 'No'} @ L{d['win_linea'] if d['win_linea'] else '-'}"
                m_str = f"{'Sí' if d['m1_aviso'] else 'No'} @ L{d['m1_linea'] if d['m1_linea'] else '-'}"
                mw = (d['win_motivo'] or '—').replace('|', '/')
                mm = (d['m1_motivo'] or '—').replace('|', '/')
                lineas.append(f"| `{d['case_id']}` | {w_str} | {m_str} | {mw} | {mm} |")
        lineas.append("")

    ruta_md.parent.mkdir(parents=True, exist_ok=True)
    ruta_md.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara corrida M1 contra corridas Windows.")
    parser.add_argument("corrida_m1", type=Path, help="Ruta a la carpeta de corrida M1 (ej. corridas/2026-10-17_..._m1-gguf)")
    args = parser.parse_args()

    carpeta_m1 = args.corrida_m1.resolve()
    print(f"Comparando corrida M1: {carpeta_m1} contra Windows...")

    res = comparar_modelos(carpeta_m1)

    DIR_ANALISIS.mkdir(parents=True, exist_ok=True)
    ruta_json = DIR_ANALISIS / "comparacion_m1_vs_windows.json"
    ruta_md = DIR_ANALISIS / "README.md"

    ruta_json.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    generar_markdown(res, ruta_md)

    print(f"[OK] Análisis guardado en:")
    print(f"     - Markdown: {ruta_md}")
    print(f"     - JSON:     {ruta_json}")


if __name__ == "__main__":
    main()
