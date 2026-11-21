"""Tabla de antes y después de «solo el número», con el código de la corrida del iPhone (2026-11-20).

    python3 -I resumir.py --base s6-hoy-1 s6-numero s6-hoy-2

Mismas definiciones que aquel `resumir.py`. Suma, contra `--base`, cuántas diferencias de riesgo cruzan el umbral de
0,3 y si alguna conversación deja de avisar o empieza a avisar. Escribe `resumen.json` en esta carpeta.
"""
import argparse
import importlib.util
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location(
    "resumir_iphone", AQUI.parent / "2026-11-20_iphone-15-pro-max-latencia" / "resumir.py")
r = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r)
UMBRAL = 0.3 - 1e-9


def main():
    p = argparse.ArgumentParser()
    p.add_argument("carpetas", nargs="+")
    p.add_argument("--base", required=True)
    p.add_argument("--salida", default="resumen.json")
    a = p.parse_args()
    ruta = lambda c: str(AQUI / c)
    filas = {c: r.resumen(ruta(c)) for c in [a.base, *a.carpetas]}
    print("| Corrida | Válidas | Por línea: mediana / p95 / máx. | Procesar: mediana / p95 (tokens nuevos) | Generar: "
          "mediana / p95 (tokens) | Sin esperar el motivo: mediana / máx. | Riesgo distinto | …que cruza 0,3 | "
          "Primer aviso distinto |")
    print("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    comparaciones = {}
    for c, f in filas.items():
        if c == a.base:
            dif = ("—", "—", "—")
        else:
            d = r.diferencias(ruta(a.base), ruta(c))
            for x in d["riesgo_distinto"] + d["primer_aviso_en_otra_linea"]:  # claves cortas en vez de rutas
                x["base"], x["otra"] = x.pop(ruta(a.base)), x.pop(ruta(c))
            d["cruzan_umbral"] = [x for x in d["riesgo_distinto"] if None in (x["base"], x["otra"])
                                  or (x["base"] >= UMBRAL) != (x["otra"] >= UMBRAL)]
            casos = len({t["case_id"] for t in r.turnos(ruta(c))})
            comparaciones[c] = d
            dif = (f"{len(d['riesgo_distinto'])}/{d['lineas']}", f"{len(d['cruzan_umbral'])}/{d['lineas']}",
                   f"{len(d['primer_aviso_en_otra_linea'])}/{casos}")
        print(f"| `{c}` | {f['validas']}/{f['consultas']} | {r.s(f['linea_med'])} / {r.s(f['linea_p95'])} / "
              f"{r.s(f['linea_max'])} s (n={f['linea_n']}) | {r.s(f['procesar_med'])} / {r.s(f['procesar_p95'])} s "
              f"({f['tokens_nuevos_med']:.0f}) | {r.s(f['generar_med'])} / {r.s(f['generar_p95'])} s "
              f"({f['tokens_gen_med']:.0f}) | {r.s(f['aviso_sin_esperar_med'])} / {r.s(f['aviso_sin_esperar_max'])} s "
              f"(n={f['avisos']}) | {dif[0]} | {dif[1]} | {dif[2]} |")
    for c, d in comparaciones.items():
        for x in d["riesgo_distinto"] + d["primer_aviso_en_otra_linea"]:
            print("   ", c, x)
    (AQUI / a.salida).write_text(json.dumps({"base": a.base, "corridas": filas, "contra_base": comparaciones},
                                            ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
