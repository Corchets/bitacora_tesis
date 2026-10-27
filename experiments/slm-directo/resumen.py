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
    if ref["clase"] in casos.LEGITIMAS:
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


def _num(fila: dict, clave: str) -> float | None:
    """Número de una columna de la traza; None si la columna falta o está vacía."""
    valor = fila.get(clave)
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def analizar(manifiesto: dict, filas: list[dict]) -> dict:
    """Por configuración y caso: línea del aviso, categoría, fallos, riesgos y tiempos.

    Terminar en el aviso (#97) es un fin normal: un caso con aviso cuenta como
    completo aunque no recorra todas las líneas. `fin` distingue ese cierre de
    una interrupción (`interrumpido`), de un caso sin respuestas válidas
    (`fallo`) y de una llamada completa sin aviso (`completo-sin-aviso`).
    `ms_hasta_aviso` acumula el costo de las actualizaciones evaluadas hasta el
    aviso incluido; sin aviso es el total del caso.
    """
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
            total_lineas = len(casos.cargar_texto(case_id))
            # El aviso termina la llamada en modo operativo: no es un corte.
            completo = len(actualizaciones) == total_lineas or aviso is not None
            if not completo:
                cat = "incompleto"
            elif len(fallos) == len(actualizaciones):
                cat = "sin_respuesta_valida"
            else:
                cat = categoria(ref, aviso)
            if aviso is not None:
                fin = "aviso"
            elif cat == "incompleto":
                fin = "interrumpido"
            elif cat == "sin_respuesta_valida":
                fin = "fallo"
            else:
                fin = "completo-sin-aviso"
            evaluadas = actualizaciones if aviso is None else actualizaciones[:actualizaciones.index(aviso_fila) + 1]
            tiene_split = any((f.get("tito_ms") or "") != "" or (f.get("slm_ms") or "") != ""
                              for f in evaluadas)
            casos_cfg[case_id] = {
                "tiene_costos_split": tiene_split,
                "ref": ref,
                "aviso": aviso,
                "aviso_fila": aviso_fila,
                "categoria": cat,
                "fin": fin,
                "fallos": fallos,
                "riesgos": [f["riesgo"] for f in actualizaciones],
                "ms": [float(f["ms"]) for f in actualizaciones if f["ms"] and f["valida"] == "true"],
                "ms_hasta_aviso": sum(_num(f, "ms") or 0.0 for f in evaluadas),
                "tito_ms_total": sum(_num(f, "tito_ms") or 0.0 for f in evaluadas),
                "slm_ms_total": sum(_num(f, "slm_ms") or 0.0 for f in evaluadas),
                "tokens_hasta_aviso": sum(
                    (_num(f, "tokens_prompt") or 0.0) + (_num(f, "tokens_salida") or 0.0)
                    for f in evaluadas
                ),
                "runtime_con_dato": sum(1 for f in evaluadas if (f.get("runtime_ns") or "") != ""),
                "runtime_ausente": sum(1 for f in evaluadas if (f.get("runtime_ns") or "") == ""),
                "completo": completo,
            }
        resultado[config] = casos_cfg
    return resultado


def metricas(cs: dict) -> dict:
    """Totales de una configuración: los mismos números que muestran resumen.md y el visor."""
    evaluados = [c for c in cs.values() if c["categoria"] not in SIN_EVALUAR]
    vish = [c for c in evaluados if c["ref"]["clase"] == "vishing"]
    legit = [c for c in evaluados if c["ref"]["clase"] in casos.LEGITIMAS]
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


def configs_filtradas(manifiesto: dict) -> list[str]:
    """Configuraciones Tito→SLM de la corrida (vacío en corridas directas viejas)."""
    return [c["config"] for c in manifiesto.get("configs", []) if c["config"].startswith("tito-slm|")]


def analisis_filtro(manifiesto: dict, filas: list[dict], analisis: dict) -> dict:
    """Derivación, ahorro y costo por configuración filtrada y caso.

    Una fila omitida (`consulta == "omitida"`) es una actualización procesada
    sin consultar al SLM: no es fallo ni predicción de legitimidad. Su `ms`
    es solo costo de Tito; en filas consultadas es Tito + SLM. `tito_ms_total`
    y `slm_ms_total` separan ambos componentes y su suma reconstruye
    `ms_total` sin doble conteo. En modo operativo las filas ya terminan en
    el aviso, así que estos totales son costos hasta el aviso.
    """
    resultado: dict[str, dict[str, dict]] = {}
    for config in configs_filtradas(manifiesto):
        filas_cfg = [f for f in filas if f["config"] == config]
        por_caso: dict[str, list[dict]] = {}
        for f in filas_cfg:
            por_caso.setdefault(f["case_id"], []).append(f)
        casos_cfg = {}
        for case_id, fs in por_caso.items():
            fs = sorted(fs, key=lambda f: int(f["linea"]))
            consultadas = [f for f in fs if (f.get("consulta") or "") in ("slm_valida", "slm_fallo")]
            evitadas = [f for f in fs if (f.get("consulta") or "") == "omitida"]
            derivacion = min((int(f["linea"]) for f in consultadas), default=None)
            ms_total = sum(float(f["ms"]) for f in fs if f.get("ms"))
            tito_total = sum(_num(f, "tito_ms") or 0.0 for f in fs)
            slm_total = sum(_num(f, "slm_ms") or 0.0 for f in fs)
            tokens = sum(
                (int(f["tokens_prompt"]) if f.get("tokens_prompt") else 0)
                + (int(f["tokens_salida"]) if f.get("tokens_salida") else 0)
                for f in consultadas
            )
            c = analisis[config][case_id]
            casos_cfg[case_id] = {
                "derivacion": derivacion,
                "consultas": len(consultadas),
                "evitadas": len(evitadas),
                "fallos_slm": sum(1 for f in consultadas if f.get("consulta") == "slm_fallo"),
                "fallos_tito": sum(1 for f in fs if (f.get("tito_error") or "").strip()),
                "ms_total": ms_total,
                "tito_ms_total": tito_total,
                "slm_ms_total": slm_total,
                "tokens_slm": tokens,
                "aviso": c["aviso"],
                "categoria": c["categoria"],
                "fin": c["fin"],
                "ms_hasta_aviso": c["ms_hasta_aviso"],
            }
        resultado[config] = casos_cfg
    return resultado


def seccion_filtro(manifiesto: dict, analisis: dict, detalle: dict) -> list[str]:
    salida = ["## Filtro Tito→SLM (derivación y ahorro)", ""]
    filtro = manifiesto.get("filtro_tito") or {}
    origen = "Tito real" if str(filtro.get("tito", "")).startswith("real-") else "Tito simulado"
    modo = manifiesto.get("modo_termino", "no informado (corrida histórica, conversación completa)")
    salida.append(
        f"{origen} (`{filtro.get('tito', 'no informado')}`), umbral {filtro.get('umbral', '—')}: "
        "el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; "
        "un fallo técnico de Tito también deriva, sin fabricar sospecha."
    )
    salida.append(f"Modo de término: `{modo}`: cada llamada termina en su primer aviso válido.")
    if filtro.get("arranque_ms") is not None or filtro.get("calentamiento_ms") is not None:
        salida.append(
            f"Arranque Tito: {_ms(filtro.get('arranque_ms'))} ms; calentamiento Tito: "
            f"{_ms(filtro.get('calentamiento_ms'))} ms (unidad: {filtro.get('unidad', 'ms')})."
        )
    salida.append(
        "Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso "
        "cuenta como falso negativo y legítima sin aviso como verdadero negativo."
    )
    salida.append("")
    for config, cs in detalle.items():
        total_consultas = sum(c["consultas"] for c in cs.values())
        total_evitadas = sum(c["evitadas"] for c in cs.values())
        total_ms = sum(c["ms_total"] for c in cs.values())
        total_fallos_tito = sum(c.get("fallos_tito", 0) for c in cs.values())
        if total_fallos_tito:
            salida.append(
                f"**Fallos técnicos de Tito: {total_fallos_tito}** (esas actualizaciones "
                "derivaron por fallo, sin puntaje ni sospecha; no son decisiones del filtro)."
            )
        salida += [
            f"### `{config}`",
            "",
            f"Consultas al SLM: {total_consultas}; evitadas por el filtro: {total_evitadas}; "
            f"costo Tito+SLM: {_ms(total_ms)} ms (omitidas: solo Tito; consultadas: Tito+SLM).",
            "",
            "| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |",
            "|---|---|---|---|---|---|---|",
        ]
        for case_id, c in sorted(cs.items()):
            salida.append(
                f"| `{case_id}` | {c['derivacion'] or 'nunca'} | "
                f"{('L' + str(c['aviso'])) if c['aviso'] else 'sin aviso'} | "
                f"{c['consultas']} | {c['evitadas']} | {c['fallos_slm']} | {_ms(c['ms_total'])} |"
            )
        nunca = sorted(cid for cid, c in cs.items() if c["derivacion"] is None)
        if nunca:
            fn = [cid for cid in nunca if cs[cid]["categoria"] == "sin_aviso"]
            tn = [cid for cid in nunca if cs[cid]["categoria"] == "sin_aviso_correcto"]
            salida += ["", "Nunca derivados (permanecen en sus denominadores):"]
            for cid in fn:
                salida.append(f"- `{cid}` · vishing sin aviso (falso negativo visible).")
            for cid in tn:
                salida.append(f"- `{cid}` · legítima sin aviso (verdadero negativo).")
            resto = [cid for cid in nunca if cid not in fn and cid not in tn]
            for cid in resto:
                salida.append(f"- `{cid}` · categoría `{cs[cid]['categoria']}`.")
        salida.append("")
    return salida


def seccion_costos_hasta_aviso(manifiesto: dict, analisis: dict) -> list[str]:
    """Totales por configuración con componentes separados y sin doble conteo.

    En modo operativo cada caso ya termina en su aviso: estos costos son hasta
    el aviso (o el total del caso si nunca avisó). En modo diagnóstico la
    conversación sigue tras el aviso y estos costos no son operativos.
    """
    modo = manifiesto.get("modo_termino", "no informado (corrida histórica, conversación completa)")
    diagnostico = modo == "diagnostico-completo"
    salida = ["## Costos por componente hasta el aviso", ""]
    salida.append(f"Modo de término: `{modo}`.")
    if diagnostico:
        salida.append(
            "Diagnóstico de conversación completa: estos costos cubren actualizaciones "
            "posteriores al aviso y no se mezclan con el costo operativo hasta el aviso."
        )
    else:
        salida.append(
            "Cada caso aporta sus actualizaciones evaluadas hasta el aviso incluido; "
            "una llamada sin aviso aporta la conversación completa. `ms` total = "
            "Tito + SLM por actualización, sin doble conteo."
        )
    if not any(c.get("tiene_costos_split") for cs in analisis.values() for c in cs.values()):
        salida.append(
            "Traza histórica sin columnas `tito_ms`/`slm_ms`: los parciales por "
            "componente no están disponibles y se muestran como — (no son cero)."
        )
    salida += ["", "| Configuración | ms hasta aviso | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |",
               "|---|---|---|---|---|---|---|"]
    for config, cs in analisis.items():
        ms_total = sum(c["ms_hasta_aviso"] for c in cs.values())
        tito = sum(c["tito_ms_total"] for c in cs.values())
        slm = sum(c["slm_ms_total"] for c in cs.values())
        toks = sum(c["tokens_hasta_aviso"] for c in cs.values())
        n_act = sum(len(c["ms"]) for c in cs.values())
        con_dato = sum(c["runtime_con_dato"] for c in cs.values())
        ausente = sum(c["runtime_ausente"] for c in cs.values())
        if any(c.get("tiene_costos_split") for c in cs.values()):
            parciales = f"{_ms(round(tito, 1))} | {_ms(round(slm, 1))}"
        else:
            parciales = "— | —"
        salida.append(
            f"| {_celda(config)} | {_ms(round(ms_total, 1))} | {parciales} | "
            f"{toks:g} | {n_act} | {con_dato}/{ausente} |"
        )
    salida += ["",
               "Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); "
               "SLM ms, solo las consultas al SLM. `Runtime` es la duración que informa "
               "el runtime (ns) por actualización válida del SLM: con dato o ausente explícito."]
    return salida


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
        f"- **Ollama:** {ollama.get('version', 'no usado')} · **Política:** {manifiesto['politica']} · **Modo:** `{manifiesto.get('modo_termino', 'no informado (corrida histórica, conversación completa)')}`",
        f"- **Casos:** {len(refs)} ({clases['vishing']} vishing, {sum(clases[c] for c in casos.LEGITIMAS)} legítimas); "
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
    detalle_filtro = analisis_filtro(manifiesto, filas, analisis)
    if detalle_filtro:
        lineas += ["", *seccion_filtro(manifiesto, analisis, detalle_filtro)]
    lineas += ["", *seccion_costos_hasta_aviso(manifiesto, analisis)]
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
