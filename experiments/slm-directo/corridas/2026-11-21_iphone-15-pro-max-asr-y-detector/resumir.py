"""Resumen de las pasadas a ritmo real, contra la corrida `metal` sin ASR del 2026-11-20.

    python3 -I resumir.py asr-y-detector solo-detector seco-mac

La latencia del detector sale de `resumen()` del `resumir.py` anterior (las mismas definiciones). Se agregan:
- «servidor por línea»: procesar + generar según `llama-server`, sin la red; lo comparable entre cable y Wi-Fi;
- el retraso de las consultas respecto de su hora (si una consulta salió tarde porque la anterior no había terminado);
- el ASR, de `asr.jsonl`: atraso de los bloques respecto del audio, transcripciones y tiempo de proceso;
- muestras de estado térmico, batería y si estaba enchufado, de `recursos.log`.
"""
import argparse
import importlib.util
import json
import re
import statistics
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
REFERENCIA = AQUI.parent / "2026-11-20_iphone-15-pro-max-latencia" / "metal"
_spec = importlib.util.spec_from_file_location("resumir_anterior", REFERENCIA.parent / "resumir.py")
anterior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(anterior)
p95, s = anterior.p95, anterior.s


def extra(carpeta):
    ts = anterior.turnos(carpeta)
    servidor = [(t["runtime_prompt_eval_ns"] + t["runtime_eval_ns"]) / 1e6 for t in ts if t.get("ms_etapa2") is None]
    r = {"servidor_med": statistics.median(servidor), "servidor_p95": p95(servidor), "servidor_max": max(servidor)}
    retrasos = [t["retraso_s"] for t in ts if "retraso_s" in t]
    if retrasos:
        r.update(retraso_med_s=statistics.median(retrasos), retraso_max_s=max(retrasos),
                 retrasadas_mas_de_1s=sum(x > 1 for x in retrasos))
    log = carpeta / "recursos.log"
    if log.exists():
        texto = log.read_text(encoding="utf-8")
        r["termico_muestras"] = dict(Counter(re.findall(r"termico=(\w+)", texto)))
        r["cargando_muestras"] = dict(Counter(re.findall(r"cargando=(\d)", texto)))
        bateria = [float(x) for x in re.findall(r"bateria=([\d.-]+)", texto)]
        r["bateria_inicio_fin"] = [bateria[0], bateria[-1]] if bateria else None
        horas = re.findall(r"^(\S+) footprint", texto, flags=re.M)
        r["recursos_desde_hasta"] = [horas[0], horas[-1]] if horas else None
        disponible = [int(x) for x in re.findall(r"disponible_kb=(\d+)", texto)]
        r["disponible_min_gib"] = min(disponible) / 2**20 if disponible else None
    asr = carpeta / "asr.jsonl"
    if asr.exists():
        eventos = [json.loads(x) for x in asr.read_text(encoding="utf-8").splitlines()]
        fin = next((e for e in eventos if e["tipo"] == "fin"), None)
        carga = next((e for e in eventos if e["tipo"] == "carga"), None)
        finales = [e for e in eventos if e["tipo"] == "final"]
        parciales = [e for e in eventos if e["tipo"] == "parcial"]
        r["asr"] = {
            "terminado": fin is not None, "carga_ms": carga and carga["carga_ms"],
            "faltaban_s_al_cargar": carga and carga["faltan_s"], "finales": len(finales), "parciales": len(parciales),
            "final_proceso_ms_med": statistics.median(e["proceso_ms"] for e in finales) if finales else None,
            "final_proceso_ms_max": max((e["proceso_ms"] for e in finales), default=None),
            "parcial_proceso_ms_med": statistics.median(e["proceso_ms"] for e in parciales) if parciales else None,
            "final_atraso_s_med": statistics.median(e["atraso_s"] for e in finales) if finales else None,
            "final_atraso_s_max": max((e["atraso_s"] for e in finales), default=None),
            **({k: fin[k] for k in ("audio_s", "bloques", "atraso_mediana_s", "atraso_p95_s", "atraso_max_s",
                                     "bloques_mas_de_1s")} if fin else {}),
            "ultimo_evento": eventos[-1] if eventos else None,
        }
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("carpetas", nargs="+")
    a = p.parse_args()
    filas = {"metal (2026-11-20, sin ASR, sin ritmo)": REFERENCIA, **{c: AQUI / c for c in a.carpetas}}
    resumen = {}
    print("| Corrida | Válidas | Por línea: mediana / p95 / máx. | Servidor por línea: mediana / p95 / máx. | "
          "Primer aviso con motivo: mediana / máx. | Sin esperar el motivo: mediana / máx. | Memoria pico |")
    print("|---|---:|---:|---:|---:|---:|---|")
    for nombre, carpeta in filas.items():
        r = {**anterior.resumen(carpeta), **extra(carpeta)}
        resumen[nombre] = r
        memoria = "; ".join(f"{k} {v:.2f} GiB".replace(".", ",") for k, v in r["memoria_gib"].items()) or "—"
        print(f"| `{nombre}` | {r['validas']}/{r['consultas']} | {s(r['linea_med'])} / {s(r['linea_p95'])} / "
              f"{s(r['linea_max'])} s | {s(r['servidor_med'])} / {s(r['servidor_p95'])} / {s(r['servidor_max'])} s | "
              f"{s(r['aviso_con_motivo_med'])} / {s(r['aviso_con_motivo_max'])} s (n={r['avisos']}) | "
              f"{s(r['aviso_sin_esperar_med'])} / {s(r['aviso_sin_esperar_max'])} s | {memoria} |")
    for nombre, r in resumen.items():
        print(f"\n`{nombre}`:", json.dumps({k: v for k, v in r.items() if k not in ("memoria_gib",) and
                                             not k.startswith(("linea", "procesar", "generar", "aviso", "tokens"))},
                                            ensure_ascii=False))
    (AQUI / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
