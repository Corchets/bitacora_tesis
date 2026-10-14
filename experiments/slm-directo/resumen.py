"""Compara una corrida con la referencia humana de los casos y escribe resumen.md.

Uso:
    python resumen.py corridas/<carpeta>
    python resumen.py corridas/<carpeta> --trayectorias   agrega el riesgo línea por línea

La referencia (casos/referencia/) recién se lee acá, después de correr los detectores.
Las posiciones son líneas del diálogo, no segundos: no se calculan márgenes temporales.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

import casos

LEYENDA = (
    "`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · "
    "`>R` después del pedido y antes del cumplimiento · `≥C` en o después del "
    "cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · "
    "`—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · "
    "`x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso."
)

# Casos que no dicen nada sobre el detector: no se cuentan como aciertos ni como errores.
SIN_EVALUAR = ("incompleto", "sin_respuesta_valida")


def categoria(ref: dict, aviso: int | None) -> str:
    """Ubicación del aviso respecto de las marcas humanas."""
    if ref["clase"] == "legitima_dificil":
        return "falsa_alarma" if aviso else "sin_aviso_correcto"
    if aviso is None:
        return "sin_aviso"
    t_r, t_c = ref["t_r_linea"], ref["t_c_linea"]
    if t_r is None:
        return "aviso_sin_pedido_de_referencia"
    if t_c is not None and aviso >= t_c:
        return "en_o_despues_del_cumplimiento"
    if aviso < t_r:
        return "antes_del_pedido"
    if aviso == t_r:
        return "en_el_pedido"
    return "despues_del_pedido"


CODIGOS = {
    "incompleto": "…",
    "sin_respuesta_valida": "x",
    "falsa_alarma": "FA",
    "sin_aviso_correcto": "ok",
    "sin_aviso": "—",
    "aviso_sin_pedido_de_referencia": "",
    "en_o_despues_del_cumplimiento": "≥C",
    "antes_del_pedido": "<R",
    "en_el_pedido": "=R",
    "despues_del_pedido": ">R",
}


def commit_corto(commit: str) -> str:
    return commit[:10] if commit != "desconocido" else commit


def _celda(texto: str) -> str:
    """Código en línea apto para tablas Markdown (el `|` separaría columnas)."""
    return "`" + texto.replace("|", "\\|") + "`"


def percentil(valores: list[float], p: int) -> float | None:
    if not valores:
        return None
    if len(valores) == 1:
        return valores[0]
    return statistics.quantiles(valores, n=100, method="inclusive")[p - 1]


def _ms(x: float | None) -> str:
    return "—" if x is None else f"{x:,.0f}".replace(",", ".")


def leer_corrida(carpeta: Path) -> tuple[dict, list[dict]]:
    manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
    with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    return manifiesto, filas


def analizar(manifiesto: dict, filas: list[dict]) -> dict:
    """Por configuración y caso: línea del aviso, categoría, fallos, riesgos y tiempos."""
    configs = [c["config"] for c in manifiesto["configs"]]
    por = defaultdict(lambda: defaultdict(list))
    for fila in filas:
        por[fila["config"]][fila["case_id"]].append(fila)
    refs = {c: casos.cargar_referencia(c) for c in manifiesto["casos"]}
    resultado = {}
    for config in configs:
        casos_cfg = {}
        for case_id, ref in refs.items():
            # Una fila por línea, en orden; si una línea aparece dos veces, vale la primera.
            por_linea: dict[int, dict] = {}
            for f in por[config].get(case_id, []):
                por_linea.setdefault(int(f["linea"]), f)
            actualizaciones = [por_linea[n] for n in sorted(por_linea)]
            if not actualizaciones:
                continue  # corrida interrumpida antes de este caso
            aviso_fila = next((f for f in actualizaciones if f["aviso"] == "true"), None)
            aviso = int(aviso_fila["linea"]) if aviso_fila else None
            fallos = [f for f in actualizaciones if f["valida"] != "true"]
            completo = len(actualizaciones) == len(casos.cargar_texto(case_id))
            if not completo:
                cat = "incompleto"
            elif len(fallos) == len(actualizaciones):
                cat = "sin_respuesta_valida"
            else:
                cat = categoria(ref, aviso)
            casos_cfg[case_id] = {
                "ref": ref,
                "aviso": aviso,
                "aviso_fila": aviso_fila,
                "categoria": cat,
                "fallos": fallos,
                "riesgos": [f["riesgo"] for f in actualizaciones],
                "ms": [float(f["ms"]) for f in actualizaciones if f["ms"] and f["valida"] == "true"],
                "completo": completo,
            }
        resultado[config] = casos_cfg
    return resultado


def metricas(cs: dict) -> dict:
    """Totales de una configuración: los mismos números que muestran resumen.md y el visor."""
    evaluados = [c for c in cs.values() if c["categoria"] not in SIN_EVALUAR]
    vish = [c for c in evaluados if c["ref"]["clase"] == "vishing"]
    legit = [c for c in evaluados if c["ref"]["clase"] == "legitima_dificil"]
    cat = Counter(c["categoria"] for c in cs.values())
    ms = [m for c in cs.values() for m in c["ms"]]
    avisos = [c["aviso_fila"] for c in evaluados if c["aviso_fila"]]
    return {
        "sin_evaluar": cat["incompleto"] + cat["sin_respuesta_valida"],
        "vishing_con_aviso": sum(1 for c in vish if c["aviso"] is not None),
        "vishing": len(vish),
        "antes_del_pedido": cat["antes_del_pedido"],
        "en_el_pedido": cat["en_el_pedido"],
        "despues_del_pedido": cat["despues_del_pedido"],
        "en_o_despues_del_cumplimiento": cat["en_o_despues_del_cumplimiento"],
        "falsas_alarmas": cat["falsa_alarma"],
        "legitimas": len(legit),
        "fallos": sum(len(c["fallos"]) for c in cs.values()),
        "actualizaciones": sum(len(c["riesgos"]) for c in cs.values()),
        "ms_p50": percentil(ms, 50),
        "ms_p95": percentil(ms, 95),
        "avisos": len(avisos),
        "avisos_con_cita_textual": sum(1 for a in avisos if a["evidencia_en_texto"] == "true"),
    }


def tabla_general(analisis: dict) -> list[str]:
    filas = [
        "| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for config, cs in analisis.items():
        m = metricas(cs)
        filas.append(
            f"| {_celda(config)} | {m['vishing_con_aviso']}/{m['vishing']} | {m['antes_del_pedido']} | {m['en_el_pedido']} | "
            f"{m['despues_del_pedido']} | {m['en_o_despues_del_cumplimiento']} | "
            f"{m['falsas_alarmas']}/{m['legitimas']} | {m['fallos']}/{m['actualizaciones']} | {_ms(m['ms_p50'])} | "
            f"{_ms(m['ms_p95'])} | {m['avisos_con_cita_textual']}/{m['avisos']} | {m['sin_evaluar']} |"
        )
    return filas


def tabla_por_caso(analisis: dict) -> list[str]:
    configs = list(analisis)
    ids = sorted({c for cs in analisis.values() for c in cs}, key=lambda c: (casos.cargar_referencia(c)["grupo"], c))
    filas = [
        "| Caso | Clase | T_R | T_C | " + " | ".join(f"C{i}" for i in range(1, len(configs) + 1)) + " |",
        "|---|---|---|---|" + "---|" * len(configs),
    ]
    for case_id in ids:
        ref = casos.cargar_referencia(case_id)
        celdas = []
        for config in configs:
            c = analisis[config].get(case_id)
            if c is None:
                celdas.append("")
                continue
            codigo = CODIGOS[c["categoria"]]
            celda = f"{codigo} L{c['aviso']}".strip() if c["aviso"] else codigo
            if c["fallos"]:
                celda += f" (x{len(c['fallos'])})"
            celdas.append(celda)
        clase = "vishing" if ref["clase"] == "vishing" else "legítima"
        filas.append(
            f"| `{case_id}` | {clase} | {ref['t_r_linea'] or '—'} | {ref['t_c_linea'] or '—'} | " + " | ".join(celdas) + " |"
        )
    return filas


def para_revisar(analisis: dict) -> list[str]:
    salida = ["### Falsas alarmas", ""]
    hubo = False
    for config, cs in analisis.items():
        for case_id, c in cs.items():
            if c["categoria"] == "falsa_alarma":
                hubo = True
                a = c["aviso_fila"]
                cita = "cita textual" if a["evidencia_en_texto"] == "true" else "cita NO textual"
                salida.append(f"- `{case_id}` · `{config}` · línea {c['aviso']}: «{a['motivo']}» — evidencia ({cita}): «{a['evidencia']}»")
    if not hubo:
        salida.append("Ninguna.")
    salida += ["", "### Vishing sin aviso", ""]
    hubo = False
    for config, cs in analisis.items():
        for case_id, c in cs.items():
            if c["categoria"] == "sin_aviso":
                hubo = True
                riesgos = [float(r) for r in c["riesgos"] if r != ""]
                maximo = f"riesgo máximo {max(riesgos):.2f}" if riesgos else "sin riesgo registrado"
                salida.append(f"- `{case_id}` · `{config}` · {maximo}")
    if not hubo:
        salida.append("Ninguno.")
    salida += ["", "### Sin evaluar", ""]
    hubo = False
    for config, cs in analisis.items():
        for case_id, c in cs.items():
            if c["categoria"] in SIN_EVALUAR:
                hubo = True
                motivo = "la corrida se cortó antes de terminarlo" if c["categoria"] == "incompleto" else "ninguna respuesta válida"
                salida.append(f"- `{case_id}` · `{config}` · {motivo}")
    if not hubo:
        salida.append("Ninguno.")
    salida += ["", "### Fallos por tipo", ""]
    tipos = Counter((config, f["error"].split(":")[0]) for config, cs in analisis.items() for c in cs.values() for f in c["fallos"])
    if tipos:
        salida += [f"- `{config}` · {tipo}: {n}" for (config, tipo), n in sorted(tipos.items())]
    else:
        salida.append("Ninguno.")
    return salida


def trayectorias(analisis: dict) -> list[str]:
    salida = ["## Trayectorias de riesgo", "", "Riesgo por línea; entre corchetes, la línea del aviso; `x` = fallo.", "", "```text"]
    for config, cs in analisis.items():
        salida.append(f"{config}")
        for case_id, c in cs.items():
            valores = []
            for n, r in enumerate(c["riesgos"], start=1):
                v = "x" if r == "" and any(int(f["linea"]) == n for f in c["fallos"]) else (r or "·")
                valores.append(f"[{v}]" if c["aviso"] == n else v)
            salida.append(f"  {case_id:42} {' '.join(valores)}")
    salida.append("```")
    return salida


def armar_resumen(carpeta: Path, con_trayectorias: bool = False) -> str:
    manifiesto, filas = leer_corrida(carpeta)
    analisis = analizar(manifiesto, filas)
    refs = [casos.cargar_referencia(c) for c in manifiesto["casos"]]
    sin_revision = sum(1 for r in refs if not r["revision_humana"])
    clases = Counter(r["clase"] for r in refs)
    maquina = manifiesto["maquina"]
    codigo = manifiesto["codigo"]
    ollama = manifiesto.get("ollama") or {}
    lineas = [
        f"# Resumen de la corrida `{carpeta.name}`",
        "",
        "> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):",
        "> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.",
        "> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).",
        "",
        f"- **Comando:** `{manifiesto['comando']}`",
        f"- **Inicio / fin:** {manifiesto['inicio']} / {manifiesto['fin'] or 'sin terminar'}"
        + (" — **interrumpida**" if manifiesto["interrumpida"] else ""),
        f"- **Código:** `{commit_corto(codigo['commit'])}`" + (" con cambios sin commit en la carpeta" if codigo["cambios_sin_commit_en_la_carpeta"] else ""),
        f"- **Máquina:** {maquina['sistema']}, {maquina['nucleos_logicos']} núcleos lógicos, {maquina['ram_total_gb']} GB de RAM",
        f"- **Ollama:** {ollama.get('version', 'no usado')} · **Política:** {manifiesto['politica']}",
        f"- **Casos:** {len(refs)} ({clases['vishing']} vishing, {clases['legitima_dificil']} legítimas); "
        f"{sin_revision} todavía sin revisión humana",
        "",
        "## Resultados por configuración",
        "",
        *tabla_general(analisis),
        "",
        "«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. "
        "«Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta "
        "solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.",
        "",
        "## Caso por caso",
        "",
        "Configuraciones: " + " · ".join(f"**C{i}** {_celda(c)}" for i, c in enumerate(analisis, start=1)),
        "",
        LEYENDA,
        "",
        *tabla_por_caso(analisis),
        "",
        "## Para revisar",
        "",
        *para_revisar(analisis),
    ]
    if manifiesto.get("modelos"):
        lineas += ["", "## Carga y memoria informadas por Ollama", "", "| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |", "|---|---|---|---|"]
        for modelo, m in manifiesto["modelos"].items():
            mem = m.get("memoria") or {}
            mb = lambda b: "—" if not b else f"{b / 1024**2:,.0f}".replace(",", ".")
            lineas.append(f"| `{modelo}` | {_ms(m.get('carga_ms'))} | {mb(mem.get('size_bytes'))} | {mb(mem.get('size_vram_bytes'))} |")
        lineas += ["", "La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android."]
    if con_trayectorias:
        lineas += ["", *trayectorias(analisis)]
    return "\n".join(lineas) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("carpeta", type=Path, help="carpeta de la corrida, p. ej. corridas/2026-10-13_153012")
    p.add_argument("--trayectorias", action="store_true", help="agregar el riesgo línea por línea")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    texto = armar_resumen(args.carpeta, args.trayectorias)
    (args.carpeta / "resumen.md").write_text(texto, encoding="utf-8")
    print(texto)
    print(f"(guardado en {args.carpeta / 'resumen.md'})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
