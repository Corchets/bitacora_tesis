"""Resumen de #172: por corrida, tiempos por línea, primer aviso, memoria y, contra una base, cuántas líneas cambian.

    python -I resumir.py                       # todas las carpetas con turnos.jsonl
    python -I resumir.py --base s6-base-t4 s6-t6 s6-t8

«Por línea» es la actualización de una línea de OTRA sin motivo (la que se repite en toda la llamada). «Primer aviso»
es la línea del primer aviso de cada conversación: con motivo, la actualización entera (hoy); sin esperarlo
(propuesta 1), solo la primera consulta. La memoria es el máximo de `VmHWM` de llama-server en recursos.log.
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


def s(ms):
    return f"{ms / 1000:.2f}".replace(".", ",")


def turnos(etiqueta):
    return [json.loads(l) for l in (AQUI / etiqueta / "turnos.jsonl").read_text(encoding="utf-8").splitlines()]


def memoria_gib(etiqueta):
    texto = (AQUI / etiqueta / "recursos.log").read_text(encoding="utf-8")
    # Solo el llama-server de la corrida: uno colgado de la corrida anterior (pasó tras s6-vk) queda con pocos MB
    # residentes y su VmHWM es el de su propia corrida.
    picos = []
    for bloque in re.split(r"^PID=", texto, flags=re.M)[1:]:
        if "llama-server" in bloque.splitlines()[0]:
            hwm = re.search(r"VmHWM:\s+(\d+) kB", bloque)
            rss = re.search(r"VmRSS:\s+(\d+) kB", bloque)
            if hwm and rss and int(rss.group(1)) > 100 * 1024:
                picos.append(int(hwm.group(1)))
    return max(picos) / 2**20 if picos else None


def resumen(etiqueta):
    ts = [t for t in turnos(etiqueta) if t["consulta"] == "slm"]
    sin_motivo = [t for t in ts if t.get("ms_etapa2") is None]
    primeros = [t for t in ts if t.get("primer_aviso")]
    return {
        "etiqueta": etiqueta,
        "consultas": len(ts), "validas": sum(bool(t["valida"]) for t in ts),
        "linea_med": statistics.median(t["total_ms"] for t in sin_motivo),
        "linea_p95": p95([t["total_ms"] for t in sin_motivo]),
        "linea_max": max(t["total_ms"] for t in sin_motivo),
        "procesar_med": statistics.median(t["runtime_prompt_eval_ns"] / 1e6 for t in ts),
        "generar_med": statistics.median(t["runtime_eval_ns"] / 1e6 for t in ts),
        "tokens_gen_med": statistics.median(t["tokens_salida"] for t in ts),
        "tokens_nuevos_med": statistics.median(t["tokens_prompt"] for t in ts),
        "avisos": len(primeros),
        "aviso_con_motivo_med": statistics.median(t["total_ms"] for t in primeros) if primeros else None,
        "aviso_con_motivo_max": max(t["total_ms"] for t in primeros) if primeros else None,
        "aviso_sin_esperar_med": statistics.median(t["ms_etapa1"] for t in primeros) if primeros else None,
        "aviso_sin_esperar_max": max(t["ms_etapa1"] for t in primeros) if primeros else None,
        "motivo_med": statistics.median(t["ms_etapa2"] for t in primeros) if primeros else None,
        "memoria_gib": memoria_gib(etiqueta),
    }


def diferencias(base, otra):
    """Líneas de OTRA en que cambia el riesgo, y conversaciones en que cambia la línea del primer aviso."""
    b = {(t["case_id"], t["linea"]): t for t in turnos(base) if t["consulta"] == "slm"}
    o = {(t["case_id"], t["linea"]): t for t in turnos(otra) if t["consulta"] == "slm"}
    comunes = sorted(set(b) & set(o))
    riesgo = [k for k in comunes if b[k].get("riesgo") != o[k].get("riesgo")]
    aviso_b = {k[0]: k[1] for k in comunes if b[k].get("primer_aviso")}
    aviso_o = {k[0]: k[1] for k in comunes if o[k].get("primer_aviso")}
    casos = sorted({k[0] for k in comunes})
    return len(comunes), riesgo, [c for c in casos if aviso_b.get(c) != aviso_o.get(c)], b, o


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--base")
    p.add_argument("etiquetas", nargs="*")
    a = p.parse_args()
    etiquetas = a.etiquetas or sorted(d.name for d in AQUI.iterdir() if (d / "turnos.jsonl").exists())
    print("| Corrida | Válidas | Línea mediana | p95 | Máx. | Procesar | Generar (tokens) | Primer aviso con motivo "
          "(med. / máx.) | Sin esperar el motivo (med. / máx.) | Memoria |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    filas = {}
    for e in etiquetas:
        r = filas[e] = resumen(e)
        mem = f"{r['memoria_gib']:.2f} GiB".replace(".", ",") if r["memoria_gib"] else "—"
        aviso = (f"{s(r['aviso_con_motivo_med'])} / {s(r['aviso_con_motivo_max'])} s (n={r['avisos']})"
                 if r["avisos"] else "—")
        sin = f"{s(r['aviso_sin_esperar_med'])} / {s(r['aviso_sin_esperar_max'])} s" if r["avisos"] else "—"
        print(f"| `{e}` | {r['validas']}/{r['consultas']} | {s(r['linea_med'])} s | {s(r['linea_p95'])} s | "
              f"{s(r['linea_max'])} s | {s(r['procesar_med'])} s | {s(r['generar_med'])} s "
              f"({r['tokens_gen_med']:.0f}) | {aviso} | {sin} | {mem} |")
    if a.base:
        print()
        for e in etiquetas:
            if e == a.base:
                continue
            n, riesgo, avisos, b, o = diferencias(a.base, e)
            print(f"- `{e}` contra `{a.base}`: riesgo distinto en {len(riesgo)}/{n} líneas; "
                  f"primer aviso en otra línea en {len(avisos)} conversaciones {avisos or ''}")
            for k in riesgo[:12]:
                print(f"    {k}: {b[k].get('riesgo')} → {o[k].get('riesgo')}  "
                      f"{b[k].get('crudo', '')[:22]!r} → {o[k].get('crudo', '')[:22]!r}")
    (AQUI / "resumen.json").write_text(json.dumps(filas, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
