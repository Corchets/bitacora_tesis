"""Cálculo de Word Error Rate (WER) y Character Error Rate (CER).

Permite comparar transcripciones de ASR frente a un texto de referencia,
con normalización de texto y análisis de palabras clave de alto riesgo.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


def normalizar_texto(texto: str, sin_tildes: bool = False) -> str:
    """Normaliza texto para comparación de ASR:

    - Convierte a minúsculas.
    - Opcionalmente elimina tildes y diacríticos si sin_tildes=True.
    - Remueve signos de puntuación (.,;:¿?¡!\"'()–-).
    - Colapsa espacios en blanco múltiples.
    """
    if not texto:
        return ""

    texto = texto.lower()

    if sin_tildes:
        # NFD separa caracteres base de sus diacríticos
        texto = "".join(
            c for c in unicodedata.normalize("NFD", texto)
            if unicodedata.category(c) != "Mn"
        )

    # Remover puntuación manteniendo letras, números y espacios
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)
    # Colapsar espacios
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto


def _distancia_levenshtein(ref: list[Any], hyp: list[Any]) -> tuple[int, int, int, int]:
    """Calcula la distancia de edición a nivel de tokens.

    Devuelve (distancia, sustituciones, eliminaciones, inserciones).
    """
    n = len(ref)
    m = len(hyp)

    # dp[i][j] almacena (costo, s, d, i_ops)
    dp = [[(0, 0, 0, 0) for _ in range(m + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        dp[i][0] = (i, 0, i, 0)  # i eliminaciones

    for j in range(1, m + 1):
        dp[0][j] = (j, 0, 0, j)  # j inserciones

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                costo_sub, s, d, ins = dp[i - 1][j - 1]
                op_sub = (costo_sub + 1, s + 1, d, ins)

                costo_del, s, d, ins = dp[i - 1][j]
                op_del = (costo_del + 1, s, d + 1, ins)

                costo_ins, s, d, ins = dp[i][j - 1]
                op_ins = (costo_ins + 1, s, d, ins + 1)

                dp[i][j] = min(op_sub, op_del, op_ins, key=lambda x: x[0])

    costo_total, s, d, ins = dp[n][m]
    return costo_total, s, d, ins


def calcular_wer(referencia: str, hipotesis: str, sin_tildes: bool = False) -> dict[str, Any]:
    """Calcula WER (Word Error Rate) entre referencia e hipótesis."""
    ref_norm = normalizar_texto(referencia, sin_tildes=sin_tildes)
    hyp_norm = normalizar_texto(hipotesis, sin_tildes=sin_tildes)

    ref_words = ref_norm.split() if ref_norm else []
    hyp_words = hyp_norm.split() if hyp_norm else []

    n = len(ref_words)
    if n == 0:
        if len(hyp_words) == 0:
            wer = 0.0
        else:
            wer = 1.0
        return {
            "wer": wer,
            "distancia": len(hyp_words),
            "sustituciones": 0,
            "eliminaciones": 0,
            "inserciones": len(hyp_words),
            "palabras_referencia": 0,
            "palabras_hipotesis": len(hyp_words),
            "ref_normalizada": ref_norm,
            "hyp_normalizada": hyp_norm,
        }

    costo, s, d, ins = _distancia_levenshtein(ref_words, hyp_words)
    wer = round(costo / n, 4)

    return {
        "wer": wer,
        "distancia": costo,
        "sustituciones": s,
        "eliminaciones": d,
        "inserciones": ins,
        "palabras_referencia": n,
        "palabras_hipotesis": len(hyp_words),
        "ref_normalizada": ref_norm,
        "hyp_normalizada": hyp_norm,
    }


def calcular_cer(referencia: str, hipotesis: str, sin_tildes: bool = False) -> dict[str, Any]:
    """Calcula CER (Character Error Rate) entre referencia e hipótesis."""
    ref_norm = normalizar_texto(referencia, sin_tildes=sin_tildes)
    hyp_norm = normalizar_texto(hipotesis, sin_tildes=sin_tildes)

    ref_chars = list(ref_norm)
    hyp_chars = list(hyp_norm)

    n = len(ref_chars)
    if n == 0:
        if len(hyp_chars) == 0:
            cer = 0.0
        else:
            cer = 1.0
        return {
            "cer": cer,
            "distancia": len(hyp_chars),
            "sustituciones": 0,
            "eliminaciones": 0,
            "inserciones": len(hyp_chars),
            "caracteres_referencia": 0,
            "caracteres_hipotesis": len(hyp_chars),
        }

    costo, s, d, ins = _distancia_levenshtein(ref_chars, hyp_chars)
    cer = round(costo / n, 4)

    return {
        "cer": cer,
        "distancia": costo,
        "sustituciones": s,
        "eliminaciones": d,
        "inserciones": ins,
        "caracteres_referencia": n,
        "caracteres_hipotesis": len(hyp_chars),
    }


PALABRAS_CLAVE_DEFECTO = [
    "codigo",
    "cero",
    "whatsapp",
    "sms",
    "activacion",
    "seguridad",
    "soporte",
    "cuenta",
    "numero",
    "clave",
    "token",
    "banco",
]


def analizar_errores_clave(
    referencia: str,
    hipotesis: str,
    palabras_clave: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Analiza si palabras clave de la referencia están presentes o ausentes en la hipótesis.

    Útil para detectar si términos críticos para vishing (como 'código', 'cero', 'sms')
    fueron capturados por el reconocedor.
    """
    if palabras_clave is None:
        palabras_clave = PALABRAS_CLAVE_DEFECTO

    ref_norm = normalizar_texto(referencia, sin_tildes=True)
    hyp_norm = normalizar_texto(hipotesis, sin_tildes=True)

    ref_palabras = ref_norm.split()
    hyp_palabras = set(hyp_norm.split())

    reporte = []
    for clave in palabras_clave:
        clave_norm = normalizar_texto(clave, sin_tildes=True)
        conteo_ref = ref_palabras.count(clave_norm)
        if conteo_ref > 0:
            presente_en_hyp = clave_norm in hyp_palabras
            reporte.append({
                "palabra_clave": clave,
                "conteo_referencia": conteo_ref,
                "detectada_en_hipotesis": presente_en_hyp,
                "estado": "OK" if presente_en_hyp else "PERDIDA",
            })

    return reporte


def extraer_texto_referencia(ruta_archivo: str) -> str:
    """Extrae el texto de referencia eliminando prefijos de turno 'A: ' o 'B: ' si existen."""
    lineas = []
    with open(ruta_archivo, "r", encoding="utf-8") as f:
        for linea in f:
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue
            # Remover prefijo de hablante A: o B:
            linea_limpia = re.sub(r"^[A-Z]:\s*", "", linea_limpia)
            lineas.append(linea_limpia)
    return " ".join(lineas)
