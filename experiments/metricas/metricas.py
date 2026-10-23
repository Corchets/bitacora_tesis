"""Módulo de métricas de evaluación de detección de vishing.

Fuente única de definiciones y fórmulas: docs/evaluacion/METRICAS.md.

Métricas implementadas:
- Marcas temporales / de posición: T_A, T_R, T_C.
- Márgenes: L_R = T_R − T_A, L_C = T_C − T_A.
- Alertas con margen suficiente: Preventive@δ(X) con X en {T_R, T_C}.
- Tasa de legítimas con al menos una alerta (falsas alarmas).
- Precision, recall y F1 por conversación (con conteos y denominadores).
- Intervalo de confianza de Wilson (95 %) para proporciones binomiales.
- Distribución de márgenes: mediana, cuartiles (Q1, Q3) y rango intercuartil (IQR) con n.
- Sensibilidad a frecuencia hipotética de fraude: precision(p) = (p * r) / (p * r + (1 - p) * f).
- Factor de tiempo real: RTF = tiempo_computo / duracion_audio.

Unidades:
- Segundos cuando hay audio ("segundos").
- Líneas cuando el diálogo es texto sin timestamps ("lineas"). Nunca se convierten líneas a segundos.
"""

from __future__ import annotations

import math
import statistics
from typing import Any, Sequence

# Valor crítico de la distribución normal estándar para 95 % de confianza (bilateral).
Z_95 = 1.959963984540054


def calcular_margen_lr(
    t_r: float | int | None,
    t_a: float | int | None,
) -> float | int | None:
    """Calcula el margen respecto del pedido peligroso: L_R = T_R − T_A.

    Positivo: la alerta llegó antes del pedido.
    Cero: al mismo tiempo / misma línea.
    Negativo: la alerta llegó después del pedido.
    Sin alerta (t_a is None) o sin pedido (t_r is None): retorna None (sin dato).
    """
    if t_a is None or t_r is None:
        return None
    return t_r - t_a


def calcular_margen_lc(
    t_c: float | int | None,
    t_a: float | int | None,
) -> float | int | None:
    """Calcula el margen respecto del cumplimiento simulado: L_C = T_C − T_A.

    Positivo: la alerta llegó antes del cumplimiento.
    Cero: al mismo tiempo / misma línea.
    Negativo: la alerta llegó después del cumplimiento.
    Sin alerta (t_a is None) o sin cumplimiento (t_c is None): retorna None.
    "Sin cumplimiento, no se infiere prevención lograda" (METRICAS.md §2).
    """
    if t_a is None or t_c is None:
        return None
    return t_c - t_a


def calcular_margenes(
    t_a: float | int | None,
    t_r: float | int | None,
    t_c: float | int | None,
) -> tuple[float | int | None, float | int | None]:
    """Retorna la tupla (L_R, L_C) para una llamada."""
    return calcular_margen_lr(t_r, t_a), calcular_margen_lc(t_c, t_a)


def intervalo_wilson(
    k: int,
    n: int,
    confianza: float = 0.95,
) -> tuple[float, float] | None:
    """Intervalo de confianza de Wilson para una proporción binomial k / n.

    Apto para proporciones extremas (0 o 1) y muestras pequeñas (METRICAS.md §4).
    Retorna (limite_inferior, limite_superior) o None si n == 0.
    """
    if n == 0:
        return None
    if k < 0 or k > n:
        raise ValueError(f"k ({k}) debe estar entre 0 y n ({n})")

    # z para 95 % por defecto; si cambia el parámetro se aproxima o usa Z_95
    if math.isclose(confianza, 0.95, rel_tol=1e-3):
        z = Z_95
    else:
        # Aproximación común si se requiriese otro nivel de confianza
        z = math.sqrt(2.0) * math.erf((confianza)) if hasattr(math, "erf") else Z_95

    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    centro = (p + z2 / (2.0 * n)) / denom
    margen = (z / denom) * math.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * n * n)))
    if k == 0:
        inferior = 0.0
    else:
        inferior = max(0.0, centro - margen)

    if k == n:
        superior = 1.0
    else:
        superior = min(1.0, centro + margen)
    return inferior, superior


def resumen_distribucion(valores: Sequence[float | int | None]) -> dict[str, Any]:
    """Calcula distribución, mediana y rango intercuartil (IQR) con conteo n.

    METRICAS.md §2: "Se informa la distribución, mediana y rango intercuartil
    de los márgenes y cuántas conversaciones permiten calcularlos."
    Filtra los valores None (márgenes sin dato).
    """
    validos = [float(v) for v in valores if v is not None]
    n = len(validos)
    if n == 0:
        return {
            "n": 0,
            "mediana": None,
            "q1": None,
            "q3": None,
            "iqr": None,
            "min": None,
            "max": None,
        }
    if n == 1:
        val = validos[0]
        return {
            "n": 1,
            "mediana": val,
            "q1": val,
            "q3": val,
            "iqr": 0.0,
            "min": val,
            "max": val,
        }

    validos_ordenados = sorted(validos)
    med = float(statistics.median(validos_ordenados))
    # method='inclusive' devuelve cuartiles equivalentes a la mediana partida
    cuartiles = statistics.quantiles(validos_ordenados, n=4, method="inclusive")
    q1 = float(cuartiles[0])
    q3 = float(cuartiles[2])
    iqr = float(q3 - q1)
    return {
        "n": n,
        "mediana": med,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "min": float(validos_ordenados[0]),
        "max": float(validos_ordenados[-1]),
    }


def _extraer_marca(caso: dict[str, Any], clave_corta: str) -> float | int | None:
    """Extrae t_r o t_c aceptando nombres con o sin prefijo/sufijo de línea/segundos."""
    clave_corta = clave_corta.lower()
    for candidato in (
        clave_corta,
        f"{clave_corta}_linea",
        f"{clave_corta}_s",
        f"{clave_corta.upper()}",
    ):
        if candidato in caso and caso[candidato] is not None:
            return caso[candidato]
    return None


def _extraer_aviso(caso: dict[str, Any]) -> tuple[bool, float | int | None]:
    """Determina si hubo aviso y el valor de T_A (en segundos o líneas)."""
    t_a = None
    for cand_ta in ("t_a", "T_A", "aviso_posicion", "aviso_linea", "disponible_s"):
        if cand_ta in caso and caso[cand_ta] is not None:
            t_a = caso[cand_ta]
            break

    # Si hay un campo booleano 'aviso'
    aviso_raw = caso.get("aviso")
    if isinstance(aviso_raw, str):
        aviso_bool = aviso_raw.lower() in ("true", "1", "t", "yes")
    elif isinstance(aviso_raw, bool):
        aviso_bool = aviso_raw
    else:
        aviso_bool = t_a is not None

    if not aviso_bool:
        t_a = None

    return aviso_bool, t_a


def preventive_at(
    delta: float | int,
    referencia: str,
    casos_vishing: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Calcula Preventive@δ(X) según METRICAS.md §3:

    Preventive@δ(X) = (llamadas de vishing con T_A ≤ X − δ) / (llamadas de vishing evaluables para X)

    - X ∈ {'T_R', 'T_C'}.
    - Las llamadas sin alerta (T_A is None) permanecen en el denominador.
    - Si falta la marca de referencia X en la llamada, queda excluida del denominador
      y se reporta el motivo y cantidad.
    """
    ref_norm = referencia.upper()
    if ref_norm not in ("T_R", "T_C"):
        raise ValueError(f"Referencia inválida {referencia!r}; debe ser 'T_R' o 'T_C'")

    clave = "t_r" if ref_norm == "T_R" else "t_c"
    evaluables = 0
    numerador = 0
    excluidas = 0

    for caso in casos_vishing:
        x_val = _extraer_marca(caso, clave)
        if x_val is None:
            excluidas += 1
            continue

        evaluables += 1
        _, t_a = _extraer_aviso(caso)
        if t_a is not None and t_a <= (x_val - delta):
            numerador += 1

    proporcion = numerador / evaluables if evaluables > 0 else None
    ic = intervalo_wilson(numerador, evaluables) if evaluables > 0 else None

    return {
        "referencia": ref_norm,
        "delta": delta,
        "numerador": numerador,
        "denominador": evaluables,
        "proporcion": proporcion,
        "ic95": ic,
        "excluidas": excluidas,
        "motivo_exclusion": (
            f"llamadas de vishing sin marca {ref_norm} en la referencia humana"
            if excluidas > 0
            else "ninguna"
        ),
        "total_vishing": len(casos_vishing),
    }


def tasa_falsas_alarmas(casos_legitimos: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Proporción de legítimas con al menos una alerta (METRICAS.md §4)."""
    total = len(casos_legitimos)
    falsas_alarmas = 0
    for caso in casos_legitimos:
        aviso_bool, _ = _extraer_aviso(caso)
        if aviso_bool:
            falsas_alarmas += 1

    tasa = falsas_alarmas / total if total > 0 else None
    ic = intervalo_wilson(falsas_alarmas, total) if total > 0 else None
    return {
        "falsas_alarmas": falsas_alarmas,
        "total_legitimas": total,
        "tasa": tasa,
        "ic95": ic,
    }


def metricas_clasificacion_conversacion(
    casos: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Precision, recall y F1 por conversación con conteos y denominadores (METRICAS.md §4).

    Clasificación binaria por llamada completa/prefijo evaluado:
    - Positivo = Vishing
    - Negativo = Legítima
    - Disparo = al menos una alerta emitida (aviso es True).
    """
    tp = 0
    fn = 0
    fp = 0
    tn = 0

    for caso in casos:
        clase = caso.get("clase", "")
        es_vishing = clase == "vishing"
        aviso_bool, _ = _extraer_aviso(caso)

        if es_vishing:
            if aviso_bool:
                tp += 1
            else:
                fn += 1
        else:
            if aviso_bool:
                fp += 1
            else:
                tn += 1

    total_vishing = tp + fn
    total_legitimas = fp + tn
    total_avisos = tp + fp

    precision = tp / total_avisos if total_avisos > 0 else None
    recall = tp / total_vishing if total_vishing > 0 else None

    if precision is not None and recall is not None and (precision + recall) > 0:
        f1 = (2.0 * precision * recall) / (precision + recall)
    else:
        f1 = None

    prec_ic = intervalo_wilson(tp, total_avisos) if total_avisos > 0 else None
    rec_ic = intervalo_wilson(tp, total_vishing) if total_vishing > 0 else None

    return {
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "tn": tn,
        "total_vishing": total_vishing,
        "total_legitimas": total_legitimas,
        "total_conversaciones": len(casos),
        "precision": precision,
        "precision_ic95": prec_ic,
        "recall": recall,
        "recall_ic95": rec_ic,
        "f1": f1,
    }


def precision_con_prevalencia(
    p: float,
    r: float | None,
    f: float | None,
) -> float | None:
    """Calcula la precisión bajo una frecuencia hipotética de fraude p (METRICAS.md §4):

    precision(p) = (p × r) / (p × r + (1 − p) × f)

    - p: frecuencia hipotética de fraude (0.0 <= p <= 1.0).
    - r: recall / tasa de detección en vishing (0.0 <= r <= 1.0).
    - f: tasa de falsas alarmas en legítimas (0.0 <= f <= 1.0).
    - Si el denominador es cero, retorna None ("No se calcula precisión si el denominador es cero").
    - Si r o f son None, retorna None.
    """
    if r is None or f is None:
        return None
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p ({p}) debe estar entre 0.0 y 1.0")
    if not (0.0 <= r <= 1.0):
        raise ValueError(f"r ({r}) debe estar entre 0.0 y 1.0")
    if not (0.0 <= f <= 1.0):
        raise ValueError(f"f ({f}) debe estar entre 0.0 y 1.0")

    numerador = p * r
    denominador = numerador + (1.0 - p) * f
    if math.isclose(denominador, 0.0, abs_tol=1e-12):
        return None
    return numerador / denominador


def calcular_rtf(
    tiempo_computo_s: float | None,
    duracion_audio_s: float | None,
) -> float | None:
    """Calcula el factor de tiempo real (Real-Time Factor, RTF):

    RTF = tiempo_computo / duracion_audio (METRICAS.md §4).
    Retorna None si falta algún dato, la duración es <= 0 o no aplica (modo texto).
    """
    if tiempo_computo_s is None or duracion_audio_s is None or duracion_audio_s <= 0:
        return None
    return float(tiempo_computo_s / duracion_audio_s)
