"""Resumen de las corridas del iPhone, con las del A56 pasadas por el mismo código.

    python3 -I resumir.py metal cpu-t4 ../2026-11-11_a56-latencia-172/s6-base-t4
    python3 -I resumir.py --riesgo metal-premisa ../2026-11-11_a56-latencia-172/s6-base-t4

Las mismas definiciones que `resumir.py` de la corrida del A56 (2026-11-11): «por línea» es la actualización de una
línea de OTRA sin motivo; «primer aviso», la línea del primer aviso de cada conversación, con el motivo (la
actualización entera) o sin esperarlo (solo la primera consulta). El p95 es el valor por rango más próximo superior.

Memoria: en el iPhone, el pico de `footprint` (lo que iOS cuenta contra el límite de la app) y el pico residente, de
`recursos.log`; en el A56, el pico de `VmHWM` de `llama-server`. `--riesgo A B` lista las líneas en que el riesgo de
A no coincide con el de B.
"""
import argparse
import json
import math
import re
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def p95(v):
    o = sorted(v)
    return o[max(0, math.ceil(0.95 * len(o)) - 1)]


def turnos(carpeta):
    lineas = (AQUI / carpeta / "turnos.jsonl").read_text(encoding="utf-8").splitlines()
    return [t for t in map(json.loads, lineas) if t["consulta"] == "slm"]


def recursos(carpeta):
    """(memoria en GiB por nombre, estados térmicos vistos en orden)."""
    ruta = AQUI / carpeta / "recursos.log"
    if not ruta.exists():
        return {}, []
    texto = ruta.read_text(encoding="utf-8")
    if "footprint_kb" in texto:
        pico = lambda campo: max(map(int, re.findall(rf"\b{campo}=(\d+)", texto))) / 2**20
        termico = list(dict.fromkeys(re.findall(r"termico=(\w+)", texto)))
        return {"footprint_pico": pico("footprint_pico_kb"), "residente_pico": pico("residente_pico_kb")}, termico
    picos = []  # A56: solo el llama-server de la corrida (ver resumir.py del 2026-11-11)
    for bloque in re.split(r"^PID=", texto, flags=re.M)[1:]:
        hwm, rss = re.search(r"VmHWM:\s+(\d+) kB", bloque), re.search(r"VmRSS:\s+(\d+) kB", bloque)
        if "llama-server" in bloque.splitlines()[0] and hwm and rss and int(rss.group(1)) > 100 * 1024:
            picos.append(int(hwm.group(1)))
    return ({"vmhwm": max(picos) / 2**20} if picos else {}), []


def resumen(carpeta):
    ts = turnos(carpeta)
    sin_motivo = [t["total_ms"] for t in ts if t.get("ms_etapa2") is None]
    primeros = [t for t in ts if t.get("primer_aviso")]
    memoria, termico = recursos(carpeta)
    med = statistics.median
    return {
        "consultas": len(ts), "validas": sum(bool(t["valida"]) for t in ts),
        "linea_n": len(sin_motivo), "linea_med": med(sin_motivo), "linea_p95": p95(sin_motivo),
        "linea_max": max(sin_motivo),
        "procesar_med": med(t["runtime_prompt_eval_ns"] / 1e6 for t in ts),
        "procesar_p95": p95([t["runtime_prompt_eval_ns"] / 1e6 for t in ts]),
        "generar_med": med(t["runtime_eval_ns"] / 1e6 for t in ts),
        "generar_p95": p95([t["runtime_eval_ns"] / 1e6 for t in ts]),
        "tokens_gen_med": med(t["tokens_salida"] for t in ts),
        "tokens_nuevos_med": med(t["tokens_prompt"] for t in ts),
        "tokens_cache_med": med(t["tokens_cache"] for t in ts if t.get("tokens_cache") is not None),
        "avisos": len(primeros),
        "aviso_con_motivo_med": med(t["total_ms"] for t in primeros) if primeros else None,
        "aviso_con_motivo_max": max(t["total_ms"] for t in primeros) if primeros else None,
        "aviso_sin_esperar_med": med(t["ms_etapa1"] for t in primeros) if primeros else None,
        "aviso_sin_esperar_max": max(t["ms_etapa1"] for t in primeros) if primeros else None,
        "memoria_gib": memoria, "termico": termico,
    }


def diferencias(a, b):
    ta = {(t["case_id"], t["linea"]): t for t in turnos(a)}
    tb = {(t["case_id"], t["linea"]): t for t in turnos(b)}
    comunes = sorted(set(ta) & set(tb))
    riesgo = [k for k in comunes if ta[k].get("riesgo") != tb[k].get("riesgo")]
    aviso = lambda t: {k[0]: k[1] for k in comunes if t[k].get("primer_aviso")}
    casos = sorted({k[0] for k in comunes})
    return {"lineas": len(comunes),
            "riesgo_distinto": [{"caso": k[0], "linea": k[1], a: ta[k].get("riesgo"), b: tb[k].get("riesgo")}
                                for k in riesgo],
            "primer_aviso_en_otra_linea": [{"caso": c, a: aviso(ta).get(c), b: aviso(tb).get(c)} for c in casos
                                           if aviso(ta).get(c) != aviso(tb).get(c)]}


def s(ms):
    return "—" if ms is None else f"{ms / 1000:.2f}".replace(".", ",")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("carpetas", nargs="*")
    p.add_argument("--riesgo", nargs=2, action="append", default=[], metavar=("A", "B"))
    a = p.parse_args()
    filas = {c: resumen(c) for c in a.carpetas}
    print("| Corrida | Válidas | Por línea: mediana / p95 / máx. | Procesar: mediana / p95 | Generar: mediana / p95 "
          "(tokens) | Primer aviso con motivo: mediana / máx. | Sin esperar el motivo: mediana / máx. | Memoria pico "
          "| Estado térmico |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for c, r in filas.items():
        memoria = "; ".join(f"{k} {v:.2f} GiB".replace(".", ",") for k, v in r["memoria_gib"].items()) or "—"
        print(f"| `{Path(c).name}` | {r['validas']}/{r['consultas']} | {s(r['linea_med'])} / {s(r['linea_p95'])} / "
              f"{s(r['linea_max'])} s (n={r['linea_n']}) | {s(r['procesar_med'])} / {s(r['procesar_p95'])} s | "
              f"{s(r['generar_med'])} / {s(r['generar_p95'])} s ({r['tokens_gen_med']:.0f}) | "
              f"{s(r['aviso_con_motivo_med'])} / {s(r['aviso_con_motivo_max'])} s (n={r['avisos']}) | "
              f"{s(r['aviso_sin_esperar_med'])} / {s(r['aviso_sin_esperar_max'])} s | {memoria} | "
              f"{', '.join(r['termico']) or '—'} |")
    comparaciones = {}
    for x, y in a.riesgo:
        d = comparaciones[f"{x} vs {y}"] = diferencias(x, y)
        print(f"\n- `{x}` contra `{y}`: riesgo distinto en {len(d['riesgo_distinto'])}/{d['lineas']} líneas; primer "
              f"aviso en otra línea en {len(d['primer_aviso_en_otra_linea'])} conversaciones")
        for fila in d["riesgo_distinto"] + d["primer_aviso_en_otra_linea"]:
            print("   ", fila)
    (AQUI / "resumen.json").write_text(json.dumps({"corridas": filas, "riesgo": comparaciones}, ensure_ascii=False,
                                                  indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
