"""Resumen de latencia de a56-congelada-latencia. Solo tiempos y tokens.

No lee ni imprime riesgo, aviso, motivo ni evidencia: las conversaciones son del test de #144 y sus salidas no se
miran antes de la evaluación final. La única marca de aviso que usa es `ms_etapa2 is not None`, para separar las
consultas que pidieron el motivo, y no informa en qué línea ni en qué caso ocurrió.

    python -I resumir.py
"""
import json
import math
import statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def p95(valores):
    orden = sorted(valores)
    return orden[max(0, math.ceil(0.95 * len(orden)) - 1)]  # rango más próximo superior


def fila(nombre, valores, unidad="s", escala=1000):
    if not valores:
        return f"| {nombre} | 0 | — | — | — |"
    f = (lambda v: f"{v / escala:.2f} {unidad}".replace(".", ",")) if escala else (lambda v: f"{v:.0f}")
    return (f"| {nombre} | {len(valores)} | {f(statistics.median(valores))} | {f(p95(valores))} | "
            f"{f(max(valores))} |")


def main():
    turnos = [json.loads(l) for l in (AQUI / "turnos.jsonl").read_text(encoding="utf-8").splitlines()]
    consultas = [t for t in turnos if t["consulta"] == "slm"]
    con_motivo = [t for t in consultas if t.get("ms_etapa2") is not None]
    sin_motivo = [t for t in consultas if t.get("ms_etapa2") is None]
    ns = lambda campo, ts: [t[campo] / 1e6 for t in ts if t.get(campo) is not None]
    salida = {
        "lineas": len(turnos), "consultas": len(consultas),
        "validas": sum(bool(t["valida"]) for t in consultas),
        "consultas_con_motivo": len(con_motivo),
        "por_caso": {c: sum(1 for t in consultas if t["case_id"] == c) for c in dict.fromkeys(t["case_id"] for t in turnos)},
    }
    tabla = [
        "| Medición | n | Mediana | p95 | Máximo |", "|---|---:|---:|---:|---:|",
        fila("Actualización completa (todas las consultas)", [t["total_ms"] for t in consultas]),
        fila("Actualización sin motivo", [t["total_ms"] for t in sin_motivo]),
        fila("Primera consulta (riesgo, 14 tokens)", [t["ms_etapa1"] for t in consultas if t.get("ms_etapa1")]),
        fila("Segunda consulta (motivo, primer aviso)", [t["ms_etapa2"] for t in con_motivo]),
        fila("Procesar prompt, runtime (1.ª consulta)", ns("runtime_prompt_eval_ns", consultas)),
        fila("Generar, runtime (1.ª consulta)", ns("runtime_eval_ns", consultas)),
        fila("Tokens de prompt (1.ª consulta)", [t["tokens_prompt"] for t in consultas if t.get("tokens_prompt")], escala=0),
        # En las consultas con motivo, tokens_cache es de la segunda consulta (la última que vio el cliente).
        fila("Tokens de prefijo reutilizados (sin motivo)", [t["tokens_cache"] for t in sin_motivo if t.get("tokens_cache") is not None], escala=0),
        fila("Tokens generados (1.ª consulta)", [t["tokens_salida"] for t in consultas if t.get("tokens_salida")], escala=0),
    ]
    salida["tabla"] = tabla
    (AQUI / "resumen.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in salida.items() if k != "tabla"}, ensure_ascii=False))
    print("\n".join(tabla))


if __name__ == "__main__":
    main()
