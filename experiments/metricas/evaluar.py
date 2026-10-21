"""Evaluador de métricas para corridas de detección de vishing.

Implementa la CLI y adaptadores de datos para:
1. Corridas de slm-directo (actualizaciones.csv + casos/referencia/*.json en LÍNEAS).
2. Salida de replay (eventos.csv + referencia en SEGUNDOS).

Fuente única de fórmulas: docs/evaluacion/METRICAS.md.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

_DIR_METRICAS = Path(__file__).resolve().parent
_DIR_REPO = Path(__file__).resolve().parents[2]
if str(_DIR_REPO) not in sys.path:
    sys.path.insert(0, str(_DIR_REPO))
if str(_DIR_METRICAS) not in sys.path:
    sys.path.insert(0, str(_DIR_METRICAS))

try:
    from metricas import (
        calcular_margenes,
        calcular_rtf,
        intervalo_wilson,
        metricas_clasificacion_conversacion,
        precision_con_prevalencia,
        preventive_at,
        resumen_distribucion,
        tasa_falsas_alarmas,
    )
except ImportError:
    from experiments.metricas.metricas import (  # type: ignore
        calcular_margenes,
        calcular_rtf,
        intervalo_wilson,
        metricas_clasificacion_conversacion,
        precision_con_prevalencia,
        preventive_at,
        resumen_distribucion,
        tasa_falsas_alarmas,
    )

# Intentar importar módulos de slm-directo para reutilización
_DIR_SLM = Path(__file__).resolve().parents[1] / "slm-directo"
if str(_DIR_SLM) not in sys.path:
    sys.path.insert(0, str(_DIR_SLM))

try:
    import casos  # type: ignore
    import resumen  # type: ignore
except ImportError:
    casos = None
    resumen = None

ADVERTENCIA_METODOLOGICA = (
    "> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin "
    "revisión humana; no es test reservado ni evidencia de rendimiento final. "
    "Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) "
    "continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../docs/gestion/MAPA-DECISIONES.md)."
)

DELTAS_CANDIDATOS_SEGUNDOS = [5.0, 10.0, 20.0]
DELTAS_CANDIDATOS_LINEAS = [0, 1, 2]
PREVALENCIAS_SENSIBILIDAD = [0.001, 0.01, 0.05, 0.10, 0.50]


@dataclass
class CasoEvaluado:
    case_id: str
    clase: str  # "vishing", "legitima_dificil", "legitima_cotidiana", etc.
    grupo: str  # "piloto_escrito", "trampa", "laboratorio", "desconocido"
    subtipo_legitima: str  # "negativo_dificil", "cotidiana", o "no_aplica"
    t_a: float | int | None
    t_r: float | int | None
    t_c: float | int | None
    aviso: bool
    l_r: float | int | None
    l_c: float | int | None
    tiempo_computo_s: float | None = None
    duracion_audio_s: float | None = None
    ms_actualizaciones: list[float] | None = None
    categoria: str = ""
    completo: bool = True


def _porcentaje(val: float | None, decimales: int = 1) -> str:
    if val is None:
        return "—"
    return f"{val * 100:.{decimales}f} %"


def _ic_str(ic: tuple[float, float] | None, decimales: int = 1) -> str:
    if not ic:
        return "—"
    inf, sup = ic
    return f"[{inf * 100:.{decimales}f} %, {sup * 100:.{decimales}f} %]"


def _num(val: float | int | None, decimales: int = 1) -> str:
    if val is None:
        return "—"
    if isinstance(val, int) or (isinstance(val, float) and val.is_integer()):
        return str(int(val))
    return f"{val:.{decimales}f}"


def cargar_corrida_slm(carpeta: Path) -> dict[str, list[CasoEvaluado]]:
    """Carga una corrida de slm-directo usando resumen.py y casos.py."""
    if resumen is None or casos is None:
        raise RuntimeError(f"No se pudieron importar casos o resumen desde {_DIR_SLM}")

    manifiesto, filas = resumen.leer_corrida(carpeta)
    analisis = resumen.analizar(manifiesto, filas)

    resultado: dict[str, list[CasoEvaluado]] = {}
    for config, cs in analisis.items():
        casos_lista: list[CasoEvaluado] = []
        for case_id, c in cs.items():
            if c["categoria"] in resumen.SIN_EVALUAR:
                continue
            ref = c["ref"]
            clase = ref["clase"]
            grupo = ref.get("grupo", "desconocido")
            subtipo = ref.get("tipo_legitima") or ("negativo_dificil" if clase == "legitima_dificil" else (
                "cotidiana" if "cotidiana" in clase else "no_aplica"
            ))
            t_a = c["aviso"]
            t_r = ref.get("t_r_linea")
            t_c = ref.get("t_c_linea")
            lr, lc = calcular_margenes(t_a=t_a, t_r=t_r, t_c=t_c)
            ms_list = c.get("ms", [])
            tiempo_comp = sum(ms_list) / 1000.0 if ms_list else None

            casos_lista.append(
                CasoEvaluado(
                    case_id=case_id,
                    clase=clase,
                    grupo=grupo,
                    subtipo_legitima=subtipo,
                    t_a=t_a,
                    t_r=t_r,
                    t_c=t_c,
                    aviso=t_a is not None,
                    l_r=lr,
                    l_c=lc,
                    tiempo_computo_s=tiempo_comp,
                    duracion_audio_s=None,  # No aplica en texto sin timestamps
                    ms_actualizaciones=ms_list,
                    categoria=c.get("categoria", ""),
                    completo=c.get("completo", True),
                )
            )
        resultado[config] = casos_lista
    return resultado


def cargar_salida_replay(
    ruta_eventos: Path,
    ruta_referencia: Path,
) -> dict[str, list[CasoEvaluado]]:
    """Adaptador para la salida de experiments/replay/ (eventos.csv + referencia humana en segundos).

    Columnas esperadas en eventos.csv:
    - case_id: identificador de la conversación.
    - aviso: booleano ("true" / "false" o 1 / 0) indicando si este evento dispara alerta.
    - disponible_s (o t_a / T_A): timestamp en segundos desde el inicio del audio.
    - config: nombre de la configuración (opcional, por defecto 'replay').
    - ms o tiempo_computo_s: tiempo de cómputo del detector (opcional).
    - duracion_audio_s: duración del audio en segundos (opcional).

    Referencia (archivo JSON o carpeta de JSONs):
    - case_id: str
    - clase: "vishing" | "legitima" | "legitima_dificil" | "legitima_cotidiana"
    - t_r o t_r_s: float | None
    - t_c o t_c_s: float | None
    - grupo: str (opcional)
    - duracion_s: float (opcional)
    """
    # 1. Cargar referencia
    refs: dict[str, dict[str, Any]] = {}
    if ruta_referencia.is_dir():
        for p in ruta_referencia.glob("*.json"):
            data = json.loads(p.read_text(encoding="utf-8"))
            cid = data.get("case_id", p.stem)
            refs[cid] = data
    else:
        raw_ref = json.loads(ruta_referencia.read_text(encoding="utf-8"))
        if isinstance(raw_ref, list):
            for item in raw_ref:
                refs[item["case_id"]] = item
        elif isinstance(raw_ref, dict):
            # Puede ser {case_id: {...}} o un único caso
            if "case_id" in raw_ref and "clase" in raw_ref:
                refs[raw_ref["case_id"]] = raw_ref
            else:
                refs = raw_ref

    # 2. Leer eventos.csv
    with ruta_eventos.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))

    por_cfg_caso: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for fila in filas:
        cfg = fila.get("config", "replay")
        cid = fila.get("case_id") or fila.get("llamada_id")
        if not cid:
            continue
        por_cfg_caso[cfg][cid].append(fila)

    resultado: dict[str, list[CasoEvaluado]] = {}
    for cfg, casos_dict in por_cfg_caso.items():
        lista: list[CasoEvaluado] = []
        for case_id, evs in casos_dict.items():
            if case_id not in refs:
                raise ValueError(f"Falta referencia explícita para la llamada {case_id!r}.")
            ref = refs[case_id]
            clase = ref.get("clase")
            if clase not in {"vishing", "legitima", "legitima_dificil", "legitima_cotidiana"}:
                raise ValueError(f"Clase ausente o desconocida en la referencia de {case_id!r}: {clase!r}.")
            grupo = ref.get("grupo", "desconocido")
            subtipo = ref.get("tipo_legitima") or (
                "negativo_dificil"
                if clase == "legitima_dificil"
                else ("cotidiana" if "cotidiana" in clase else "no_aplica")
            )

            # Buscar primer aviso
            t_a = None
            for e in evs:
                av = str(e.get("aviso", "")).strip().lower()
                if av in ("true", "1", "t", "yes"):
                    ts = e.get("t_a") or e.get("T_A") or e.get("disponible_s")
                    if ts is not None and ts != "":
                        t_a = float(ts)
                        break

            t_r = ref.get("t_r") if "t_r" in ref else ref.get("t_r_s")
            t_c = ref.get("t_c") if "t_c" in ref else ref.get("t_c_s")
            if t_r is not None:
                t_r = float(t_r)
            if t_c is not None:
                t_c = float(t_c)

            lr, lc = calcular_margenes(t_a=t_a, t_r=t_r, t_c=t_c)

            # Tiempos de cómputo y duración de audio si existen
            dur = ref.get("duracion_s") or ref.get("duracion_audio_s")
            if dur is None:
                for e in evs:
                    if e.get("duracion_audio_s"):
                        dur = float(e["duracion_audio_s"])
                        break
                    if e.get("fin_audio_s"):
                        dur = max(dur or 0.0, float(e["fin_audio_s"]))
            comp_s = None
            ms_vals = []
            for e in evs:
                ms_val = e.get("ms") or e.get("ms_detector")
                if ms_val:
                    ms_vals.append(float(ms_val))
                elif "tiempo_computo_s" in e and e["tiempo_computo_s"]:
                    comp_s = (comp_s or 0.0) + float(e["tiempo_computo_s"])
            if ms_vals and comp_s is None:
                comp_s = sum(ms_vals) / 1000.0

            lista.append(
                CasoEvaluado(
                    case_id=case_id,
                    clase=clase,
                    grupo=grupo,
                    subtipo_legitima=subtipo,
                    t_a=t_a,
                    t_r=t_r,
                    t_c=t_c,
                    aviso=t_a is not None,
                    l_r=lr,
                    l_c=lc,
                    tiempo_computo_s=comp_s,
                    duracion_audio_s=dur,
                    ms_actualizaciones=ms_vals or None,
                    categoria="",
                    completo=True,
                )
            )
        resultado[cfg] = lista
    return resultado


def evaluar_configuracion(
    nombre_config: str,
    casos_evaluados: list[CasoEvaluado],
    unidad: str,  # "lineas" o "segundos"
    deltas: list[float | int] | None = None,
    metadatos: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Calcula todas las métricas de METRICAS.md para un conjunto de casos evaluados."""
    if deltas is None:
        deltas = DELTAS_CANDIDATOS_SEGUNDOS if unidad == "segundos" else DELTAS_CANDIDATOS_LINEAS

    casos_dicts = [asdict(c) for c in casos_evaluados]
    vishing = [c for c in casos_dicts if c["clase"] == "vishing"]
    legitimas = [c for c in casos_dicts if c["clase"] != "vishing"]

    # 1. Métricas de clasificación por conversación
    clasif = metricas_clasificacion_conversacion(casos_dicts)

    # 2. Falsas alarmas en legítimas
    fa = tasa_falsas_alarmas(legitimas)

    # 3. Márgenes L_R y L_C
    lr_vals = [c["l_r"] for c in vishing if c["l_r"] is not None]
    lc_vals = [c["l_c"] for c in vishing if c["l_c"] is not None]
    dist_lr = resumen_distribucion(lr_vals)
    dist_lc = resumen_distribucion(lc_vals)

    # 4. Preventive@δ
    preventive_tr = [preventive_at(delta=d, referencia="T_R", casos_vishing=vishing) for d in deltas]
    preventive_tc = [preventive_at(delta=d, referencia="T_C", casos_vishing=vishing) for d in deltas]

    # 5. Sensibilidad precision(p)
    recall = clasif["recall"]
    tasa_fa = fa["tasa"]
    sensibilidad_p = {}
    for p in PREVALENCIAS_SENSIBILIDAD:
        p_str = f"{p * 100:.1f}%"
        sensibilidad_p[p_str] = precision_con_prevalencia(p, recall, tasa_fa)

    # 6. Desglose por grupo
    grupos_set = sorted({c["grupo"] for c in casos_dicts})
    desglose_grupos = {}
    for g in grupos_set:
        sub_casos = [c for c in casos_dicts if c["grupo"] == g]
        sub_vishing = [c for c in sub_casos if c["clase"] == "vishing"]
        sub_legit = [c for c in sub_casos if c["clase"] != "vishing"]
        sub_clasif = metricas_clasificacion_conversacion(sub_casos)
        sub_fa = tasa_falsas_alarmas(sub_legit)
        sub_lr = resumen_distribucion([c["l_r"] for c in sub_vishing if c["l_r"] is not None])
        sub_lc = resumen_distribucion([c["l_c"] for c in sub_vishing if c["l_c"] is not None])
        desglose_grupos[g] = {
            "total": len(sub_casos),
            "vishing": len(sub_vishing),
            "vishing_con_aviso": sub_clasif["tp"],
            "recall": sub_clasif["recall"],
            "recall_ic95": sub_clasif["recall_ic95"],
            "legitimas": len(sub_legit),
            "falsas_alarmas": sub_fa["falsas_alarmas"],
            "tasa_fa": sub_fa["tasa"],
            "tasa_fa_ic95": sub_fa["ic95"],
            "mediana_lr": sub_lr["mediana"],
            "iqr_lr": sub_lr["iqr"],
            "n_lr": sub_lr["n"],
            "mediana_lc": sub_lc["mediana"],
            "iqr_lc": sub_lc["iqr"],
            "n_lc": sub_lc["n"],
        }

    # 7. Desglose de legítimas: cotidianas vs negativos difíciles
    subtipos = sorted({c["subtipo_legitima"] for c in legitimas})
    desglose_legitimas = {}
    for st in subtipos:
        sub_leg = [c for c in legitimas if c["subtipo_legitima"] == st]
        fa_st = tasa_falsas_alarmas(sub_leg)
        desglose_legitimas[st] = {
            "total": len(sub_leg),
            "falsas_alarmas": fa_st["falsas_alarmas"],
            "tasa": fa_st["tasa"],
            "ic95": fa_st["ic95"],
        }
    if "cotidiana" not in desglose_legitimas:
        desglose_legitimas["cotidiana"] = {
            "total": 0,
            "falsas_alarmas": 0,
            "tasa": None,
            "ic95": None,
            "nota": "sin casos cotidianos en este conjunto de desarrollo",
        }

    # 8. Rendimiento y RTF
    ms_todos = [ms for c in casos_evaluados if c.ms_actualizaciones for ms in c.ms_actualizaciones]
    ms_p50 = resumen.percentil(ms_todos, 50) if (resumen and ms_todos) else None
    ms_p95 = resumen.percentil(ms_todos, 95) if (resumen and ms_todos) else None

    # RTF si hay audio
    tiempos_comp = [c.tiempo_computo_s for c in casos_evaluados if c.tiempo_computo_s is not None]
    duraciones = [c.duracion_audio_s for c in casos_evaluados if c.duracion_audio_s is not None]
    rtf_global = None
    if tiempos_comp and duraciones and len(tiempos_comp) == len(duraciones) and sum(duraciones) > 0:
        rtf_global = calcular_rtf(sum(tiempos_comp), sum(duraciones))

    return {
        "configuracion": nombre_config,
        "unidad": unidad,
        "metadatos": metadatos or {},
        "casos_totales": len(casos_evaluados),
        "vishing_total": len(vishing),
        "legitimas_total": len(legitimas),
        "clasificacion": clasif,
        "falsas_alarmas": fa,
        "margenes": {
            "l_r": dist_lr,
            "l_c": dist_lc,
        },
        "preventive_at": {
            "t_r": preventive_tr,
            "t_c": preventive_tc,
        },
        "sensibilidad_prevalencia": sensibilidad_p,
        "desglose_grupos": desglose_grupos,
        "desglose_legitimas": desglose_legitimas,
        "rendimiento": {
            "ms_p50": ms_p50,
            "ms_p95": ms_p95,
            "rtf": rtf_global,
        },
    }


def armar_reporte_md(
    evaluaciones: list[dict[str, Any]],
    titulo: str = "Evaluación de Métricas",
    ruta_salida: Path | None = None,
) -> str:
    """Genera un informe Markdown exhaustivo y autocontenido según METRICAS.md."""
    lineas: list[str] = [
        f"# {titulo}",
        "",
        ADVERTENCIA_METODOLOGICA,
        "",
        "> **Parámetros candidatos:** Los umbrales $\\delta$ evaluados son candidatos de trabajo "
        "(5, 10, 20 s para audio; 0, 1, 2 líneas para texto). "
        "Las marcas temporales y referencias principales permanecen sujetas a acuerdo en "
        "[D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y "
        "[D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).",
        "",
        "## 1. Resumen General de Detección y Clasificación por Configuración",
        "",
        "| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]

    for ev in evaluaciones:
        cfg = ev["configuracion"].replace("|", "\\|")
        u = ev["unidad"]
        cl = ev["clasificacion"]
        fa = ev["falsas_alarmas"]
        lr = ev["margenes"]["l_r"]
        lc = ev["margenes"]["l_c"]
        rend = ev["rendimiento"]

        rec_str = f"{cl['tp']}/{cl['total_vishing']} ({_porcentaje(cl['recall'])}) {_ic_str(cl['recall_ic95'])}"
        fa_str = f"{fa['falsas_alarmas']}/{fa['total_legitimas']} ({_porcentaje(fa['tasa'])}) {_ic_str(fa['ic95'])}"
        prec_str = f"{cl['tp']}/{cl['tp'] + cl['fp']} ({_porcentaje(cl['precision'])}) {_ic_str(cl['precision_ic95'])}"
        f1_str = _num(cl["f1"], 3)

        lr_str = f"{_num(lr['mediana'])} [IQR {_num(lr['iqr'])}, n={lr['n']}]" if lr["n"] > 0 else "—"
        lc_str = f"{_num(lc['mediana'])} [IQR {_num(lc['iqr'])}, n={lc['n']}]" if lc["n"] > 0 else "—"

        ms_str = f"{_num(rend['ms_p50'], 0)} / {_num(rend['ms_p95'], 0)}" if rend["ms_p50"] is not None else (
            f"RTF {_num(rend['rtf'], 2)}" if rend["rtf"] is not None else "—"
        )

        lineas.append(
            f"| `{cfg}` | {u} | {rec_str} | {fa_str} | {prec_str} | {f1_str} | {lr_str} | {lc_str} | {ms_str} |"
        )

    lineas += [
        "",
        "## 2. Alertas con Margen Suficiente (Preventive@δ)",
        "",
        "Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.",
        "Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.",
        "",
        "| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |",
        "|---|---|---|---|---|---|",
    ]

    for ev in evaluaciones:
        cfg = ev["configuracion"].replace("|", "\\|")
        u = ev["unidad"]
        for p in ev["preventive_at"]["t_r"]:
            d_label = f"{p['delta']} {u}"
            prop_str = f"{p['numerador']}/{p['denominador']} ({_porcentaje(p['proporcion'])})" if p['denominador'] > 0 else "—"
            lineas.append(
                f"| `{cfg}` | $T_R$ (pedido) | {d_label} | {prop_str} | {_ic_str(p['ic95'])} | {p['excluidas']} ({p['motivo_exclusion']}) |"
            )
        for p in ev["preventive_at"]["t_c"]:
            d_label = f"{p['delta']} {u}"
            prop_str = f"{p['numerador']}/{p['denominador']} ({_porcentaje(p['proporcion'])})" if p['denominador'] > 0 else "—"
            lineas.append(
                f"| `{cfg}` | $T_C$ (cumplimiento) | {d_label} | {prop_str} | {_ic_str(p['ic95'])} | {p['excluidas']} ({p['motivo_exclusion']}) |"
            )

    lineas += [
        "",
        "## 3. Desglose por Grupo de Casos",
        "",
        "| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |",
        "|---|---|---|---|---|---|",
    ]

    for ev in evaluaciones:
        cfg = ev["configuracion"].replace("|", "\\|")
        for g, d in ev["desglose_grupos"].items():
            rec_str = f"{d['vishing_con_aviso']}/{d['vishing']} ({_porcentaje(d['recall'])})" if d["vishing"] > 0 else "0/0"
            fa_str = f"{d['falsas_alarmas']}/{d['legitimas']} ({_porcentaje(d['tasa_fa'])})" if d["legitimas"] > 0 else "0/0"
            lr_str = f"{_num(d['mediana_lr'])} (n={d['n_lr']})" if d["n_lr"] > 0 else "—"
            lc_str = f"{_num(d['mediana_lc'])} (n={d['n_lc']})" if d["n_lc"] > 0 else "—"
            lineas.append(f"| `{cfg}` | `{g}` | {rec_str} | {fa_str} | {lr_str} | {lc_str} |")

    lineas += [
        "",
        "## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles",
        "",
        "| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |",
        "|---|---|---|---|---|---|",
    ]

    for ev in evaluaciones:
        cfg = ev["configuracion"].replace("|", "\\|")
        for st, d in ev["desglose_legitimas"].items():
            if d["total"] == 0:
                lineas.append(f"| `{cfg}` | `{st}` | 0 | 0 | — | — (no disponible en este set) |")
            else:
                lineas.append(
                    f"| `{cfg}` | `{st}` | {d['total']} | {d['falsas_alarmas']} | {_porcentaje(d['tasa'])} | {_ic_str(d['ic95'])} |"
                )

    lineas += [
        "",
        "## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude",
        "",
        "Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.",
        "*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. "
        "Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.",
        "",
        "| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\\%$ | $p = 1.0\\%$ | $p = 5.0\\%$ | $p = 10.0\\%$ | $p = 50.0\\%$ |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for ev in evaluaciones:
        cfg = ev["configuracion"].replace("|", "\\|")
        r = ev["clasificacion"]["recall"]
        f_val = ev["falsas_alarmas"]["tasa"]
        sens = ev["sensibilidad_prevalencia"]
        p01 = _porcentaje(sens.get("0.1%"))
        p1 = _porcentaje(sens.get("1.0%"))
        p5 = _porcentaje(sens.get("5.0%"))
        p10 = _porcentaje(sens.get("10.0%"))
        p50 = _porcentaje(sens.get("50.0%"))
        lineas.append(
            f"| `{cfg}` | {_porcentaje(r)} | {_porcentaje(f_val)} | {p01} | {p1} | {p5} | {p10} | {p50} |"
        )

    lineas.append("")
    base = ruta_salida.resolve().parent if ruta_salida else Path.cwd()
    mapa = os.path.relpath(_DIR_REPO / "docs/gestion/MAPA-DECISIONES.md", base)
    return "\n".join(lineas).replace("../../docs/gestion/MAPA-DECISIONES.md", mapa)


def parsear_argumentos(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "corridas",
        nargs="*",
        type=Path,
        help="Carpetas de corridas de slm-directo (ej. experiments/slm-directo/corridas/<x>)",
    )
    parser.add_argument(
        "--replay-eventos",
        type=Path,
        default=None,
        help="Ruta al archivo eventos.csv de experiments/replay",
    )
    parser.add_argument(
        "--replay-referencia",
        type=Path,
        default=None,
        help="Ruta al archivo JSON o carpeta de referencias de replay",
    )
    parser.add_argument(
        "--salida-dir",
        type=Path,
        default=None,
        help="Directorio donde guardar metricas.json y metricas.md",
    )
    parser.add_argument(
        "--salida-json",
        type=Path,
        default=None,
        help="Ruta directa de salida para metricas.json",
    )
    parser.add_argument(
        "--salida-md",
        type=Path,
        default=None,
        help="Ruta directa de salida para metricas.md",
    )
    parser.add_argument(
        "--delta",
        type=float,
        nargs="+",
        default=None,
        help="Valores candidatos para delta de Preventive@δ",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parsear_argumentos(argv)

    corridas_slm = list(args.corridas)
    # Si no se pasaron corridas ni replay, cargar las corridas canónicas del desarrollo
    if not corridas_slm and not args.replay_eventos:
        dir_corridas = _DIR_SLM / "corridas"
        canonicas = [
            dir_corridas / "2026-10-13_224418_linea-base-reglas",
            dir_corridas / "2026-10-14_173532_demo-qwen3.5-0.8b",
            dir_corridas / "2026-10-14_172930_demo-qwen3.5-2b",
            dir_corridas / "2026-10-14_175451_demo-qwen3.5-2b",
            dir_corridas / "2026-10-14_174602_demo-qwen3.5-4b",
        ]
        corridas_slm = [p for p in canonicas if p.exists()]

    evaluaciones: list[dict[str, Any]] = []

    # 1. Evaluar corridas de slm-directo
    for c_path in corridas_slm:
        if not c_path.exists():
            print(f"ADVERTENCIA: la carpeta {c_path} no existe.", file=sys.stderr)
            continue
        por_cfg = cargar_corrida_slm(c_path)
        for cfg_nombre, casos_lista in por_cfg.items():
            label = f"{c_path.name} | {cfg_nombre}"
            ev = evaluar_configuracion(
                nombre_config=label,
                casos_evaluados=casos_lista,
                unidad="lineas",
                deltas=args.delta,
                metadatos={"origen": "slm-directo", "corrida": c_path.name, "config": cfg_nombre},
            )
            evaluaciones.append(ev)

    # 2. Evaluar replay si se especificó
    if args.replay_eventos and args.replay_referencia:
        if not args.replay_eventos.exists() or not args.replay_referencia.exists():
            print(f"ERROR: no existen los archivos de replay {args.replay_eventos} o {args.replay_referencia}", file=sys.stderr)
            return 1
        por_cfg_replay = cargar_salida_replay(args.replay_eventos, args.replay_referencia)
        for cfg_nombre, casos_lista in por_cfg_replay.items():
            label = f"replay | {cfg_nombre}"
            ev = evaluar_configuracion(
                nombre_config=label,
                casos_evaluados=casos_lista,
                unidad="segundos",
                deltas=args.delta,
                metadatos={"origen": "replay", "eventos": str(args.replay_eventos)},
            )
            evaluaciones.append(ev)

    if not evaluaciones:
        print("No se encontraron corridas para evaluar.", file=sys.stderr)
        return 1

    # Preparar salidas
    salida_md_path = args.salida_md
    salida_json_path = args.salida_json
    if args.salida_dir:
        salida_dir = Path(args.salida_dir)
        salida_dir.mkdir(parents=True, exist_ok=True)
        salida_md_path = salida_md_path or (salida_dir / "metricas.md")
        salida_json_path = salida_json_path or (salida_dir / "metricas.json")

    contenido_md = armar_reporte_md(evaluaciones, ruta_salida=salida_md_path)

    if salida_md_path:
        salida_md_path.parent.mkdir(parents=True, exist_ok=True)
        salida_md_path.write_text(contenido_md, encoding="utf-8")
        print(f"Reporte Markdown guardado en: {salida_md_path}")

    if salida_json_path:
        salida_json_path.parent.mkdir(parents=True, exist_ok=True)
        salida_json_path.write_text(
            json.dumps({"advertencia": ADVERTENCIA_METODOLOGICA, "evaluaciones": evaluaciones}, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Métricas JSON guardadas en: {salida_json_path}")

    if not salida_md_path and not salida_json_path:
        print(contenido_md)

    return 0


if __name__ == "__main__":
    sys.exit(main())
