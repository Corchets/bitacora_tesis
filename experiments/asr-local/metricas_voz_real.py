"""Métricas de la medición con voz real (#94): alineado por frase, etiquetas, recall, agregados y regla de paso.

Todo son funciones puras sobre textos y números, sin modelos ni audio, para probarlas con ejemplos
chicos (tests/test_metricas_voz_real.py). `medir_voz_real.py` las usa sobre lo que corre cada variante.

La medida principal son las etiquetas de `slm-directo/reglas.py`, que se usan como instrumento y no
se modifican: se corren sobre cada frase de la referencia («Lo que dije en realidad») y sobre la
parte de la transcripción que le toca, y se comparan.
"""

from __future__ import annotations

import math
import re
import statistics
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hotwords import HOTWORDS_POR_DEFECTO, leer_secciones, sin_puntaje
from wer import calcular_cer, calcular_wer, normalizar_texto

DIR_ASR = Path(__file__).resolve().parent
DIR_REGLAS = DIR_ASR.parent / "slm-directo"
JERGA_POR_DEFECTO = DIR_ASR / "voz-real" / "jerga.txt"

# «luca» y «mango» son plata: reglas.py no los tiene, el plan los pasa a la lista crítica (§2).
TERMINOS_PLATA = ("luca", "mango")

# Regla de paso del plan (PLAN-VOZ-REAL.md §2), medida en la toma 2.
MIN_FRASES_MAS = 2
MAX_DEMORA_EXTRA_S = 0.3
MAX_WER_EXTRA = 0.02  # 2 puntos


def modulo_reglas() -> Any:
    """`reglas.py` de slm-directo, el instrumento de medida. No se modifica."""
    if str(DIR_REGLAS) not in sys.path:
        sys.path.insert(0, str(DIR_REGLAS))
    import reglas

    return reglas


# --- Alineado por frase ---------------------------------------------------------------------------


def alinear(ref: list[str], hip: list[str]) -> list[tuple[int | None, int | None]]:
    """Alineado de Levenshtein por palabra: pares (índice en ref, índice en hip); None = falta de ese lado.

    Costo unitario. A igual costo se prefiere emparejar (acierto o sustitución) antes que borrar o insertar.
    """
    n, m = len(ref), len(hip)
    costo = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        costo[i][0] = i
    for j in range(1, m + 1):
        costo[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            costo[i][j] = min(costo[i - 1][j - 1] + (ref[i - 1] != hip[j - 1]),
                              costo[i - 1][j] + 1, costo[i][j - 1] + 1)
    pares: list[tuple[int | None, int | None]] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and costo[i][j] == costo[i - 1][j - 1] + (ref[i - 1] != hip[j - 1]):
            pares.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif i > 0 and costo[i][j] == costo[i - 1][j] + 1:
            pares.append((i - 1, None))
            i -= 1
        else:
            pares.append((None, j - 1))
            j -= 1
    pares.reverse()
    return pares


def _clave(palabra: str) -> str:
    return normalizar_texto(palabra, sin_tildes=True)


def partir_por_frases(lineas_ref: list[str], hipotesis: str) -> list[str]:
    """Parte la transcripción en una cadena por cada línea de la referencia.

    Alinea las palabras de la hipótesis con las de la referencia y cada palabra va a la frase de la
    palabra de referencia con la que quedó emparejada. Una palabra de más (inserción) va a la frase
    de la última palabra de referencia que la precede (a la primera si está al principio).
    """
    ref_palabras: list[tuple[str, int]] = []
    for k, linea in enumerate(lineas_ref):
        ref_palabras += [(_clave(p), k) for p in linea.split() if _clave(p)]
    hip_palabras = [(p, _clave(p)) for p in hipotesis.split() if _clave(p)]
    partes: list[list[str]] = [[] for _ in lineas_ref]
    if not lineas_ref:
        return []
    frase_actual = 0
    for i, j in alinear([c for c, _ in ref_palabras], [c for _, c in hip_palabras]):
        if i is not None:
            frase_actual = ref_palabras[i][1]
        if j is not None:
            partes[frase_actual].append(hip_palabras[j][0])
    return [" ".join(p) for p in partes]


# --- Términos: críticos, entidades y jerga ----------------------------------------------------------


def normalizar_conservando_n(texto: str) -> str:
    """Minúsculas, sin tildes ni signos, pero con la ñ: «ñaño» y «nano» son palabras distintas."""
    protegido = texto.lower().replace("ñ", "\x00")
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", protegido) if unicodedata.category(c) != "Mn")
    return " ".join(re.sub(r"[^\w\x00]", " ", sin_tildes, flags=re.UNICODE).replace("\x00", "ñ").split())


@dataclass
class Terminos:
    """Qué términos se buscan en cada frase. Los críticos salen de reglas.py más «luca» y «mango»."""

    patrones: list[str] = field(default_factory=list)  # PATRONES de reglas.py (con la tolerancia de un typo de reglas)
    imperativos: list[str] = field(default_factory=list)  # _IMPERATIVOS de reglas.py (subcadena)
    plata: list[str] = field(default_factory=lambda: list(TERMINOS_PLATA))
    entidades: list[str] = field(default_factory=list)  # bancos y apps
    jerga: list[str] = field(default_factory=list)  # informativo


def cargar_terminos(hotwords: str | Path = HOTWORDS_POR_DEFECTO, jerga: str | Path = JERGA_POR_DEFECTO) -> Terminos:
    reglas = modulo_reglas()
    patrones = sorted({p for pals in reglas.PATRONES.values() for p in pals})
    secciones = leer_secciones(hotwords)
    entidades = []
    for h in secciones.get("bancos_y_apps", []):
        n = normalizar_conservando_n(sin_puntaje(h))
        if n not in entidades:
            entidades.append(n)
    lista_jerga = []
    for linea in Path(jerga).read_text(encoding="utf-8").splitlines():
        if linea.strip() and not linea.lstrip().startswith("#"):
            lista_jerga.append(normalizar_conservando_n(linea))
    return Terminos(patrones=patrones, imperativos=list(reglas._IMPERATIVOS), entidades=entidades, jerga=lista_jerga)


def _palabra_entera(norm: str, termino: str) -> bool:
    plural = r"(?:s|es)?" if len(termino) >= 4 else ""
    return re.search(rf"(?<!\w){re.escape(termino)}{plural}(?!\w)", norm) is not None


def terminos_en(texto: str, terminos: Terminos) -> dict[str, set[str]]:
    """Qué términos de cada grupo aparecen en el texto: `criticos`, `entidades`, `jerga`."""
    reglas = modulo_reglas()
    norm = reglas._normalizar(texto)  # como lo ve el detector: sin tildes y con la ñ convertida en n
    propio = normalizar_conservando_n(texto)
    criticos = {p for p in terminos.patrones if reglas._cerca(norm, p)}
    criticos |= {i for i in terminos.imperativos if i in norm}
    criticos |= {t for t in terminos.plata if _palabra_entera(propio, t)}
    return {
        "criticos": criticos,
        "entidades": {e for e in terminos.entidades if _palabra_entera(propio, e)},
        "jerga": {j for j in terminos.jerga if _palabra_entera(propio, j)},
    }


# --- Etiquetas y métricas por prueba ---------------------------------------------------------------


def etiquetas(texto: str) -> set[str]:
    return set(modulo_reglas().incendio_en(texto))


def evaluar_frases(lineas_ref: list[str], frases_hip: list[str], terminos: Terminos,
                   tipos: list[str | None] | None = None) -> dict[str, Any]:
    """Compara, frase por frase, las etiquetas y los términos de la referencia con los de la transcripción."""
    tipos = tipos or [None] * len(lineas_ref)
    frases = []
    recall: dict[str, dict[str, dict[str, int]]] = {"criticos": {}, "entidades": {}, "jerga": {}}
    for i, (ref, hip) in enumerate(zip(lineas_ref, frases_hip)):
        e_ref, e_hip = etiquetas(ref), etiquetas(hip)
        t_ref, t_hip = terminos_en(ref, terminos), terminos_en(hip, terminos)
        for grupo in recall:
            for t in t_ref[grupo]:
                celda = recall[grupo].setdefault(t, {"ref": 0, "ok": 0})
                celda["ref"] += 1
                celda["ok"] += t in t_hip[grupo]
        frases.append({
            "n": i + 1, "tipo": tipos[i], "referencia": ref, "hipotesis": hip,
            "etiquetas_ref": sorted(e_ref), "etiquetas_hip": sorted(e_hip),
            "correcta": e_ref == e_hip,
            "perdidas": sorted(e_ref - e_hip), "nuevas": sorted(e_hip - e_ref),
        })
    con_etiquetas = [f for f in frases if f["etiquetas_ref"]]
    sin_etiquetas = [f for f in frases if not f["etiquetas_ref"]]
    return {
        "frases": frases,
        "n_frases": len(frases),
        "frases_con_etiquetas_ref": len(con_etiquetas),
        "frases_correctas": sum(f["correcta"] for f in frases),
        "positivas_correctas": sum(f["correcta"] for f in con_etiquetas),
        "negativas": len(sin_etiquetas),
        "negativas_correctas": sum(f["correcta"] for f in sin_etiquetas),
        "etiquetas_nuevas_en_negativas": sum(len(f["nuevas"]) for f in sin_etiquetas),
        "etiquetas_perdidas": sum(len(f["perdidas"]) for f in frases),
        "etiquetas_nuevas_en_positivas": sum(len(f["nuevas"]) for f in con_etiquetas),
        "recall": recall,
    }


def error_de_texto(referencia: str, hipotesis: str) -> dict[str, Any]:
    """WER y CER del bloque entero (sin tildes ni mayúsculas, como en wer.py), con las cuentas para agregar."""
    w = calcular_wer(referencia, hipotesis, sin_tildes=True)
    c = calcular_cer(referencia, hipotesis, sin_tildes=True)
    return {"wer": w["wer"], "wer_distancia": w["distancia"], "palabras_ref": w["palabras_referencia"],
            "cer": c["cer"], "cer_distancia": c["distancia"], "caracteres_ref": c["caracteres_referencia"]}


# --- Estadísticos y agregados -----------------------------------------------------------------------


def percentil(valores: list[float], p: float) -> float | None:
    """Percentil por rango más cercano (p entre 0 y 100); None si no hay datos."""
    if not valores:
        return None
    orden = sorted(valores)
    return orden[max(0, min(len(orden) - 1, math.ceil(p / 100 * len(orden)) - 1))]


def resumen_demoras(demoras: list[float]) -> dict[str, Any]:
    if not demoras:
        return {"n": 0, "mediana_s": None, "p95_s": None, "max_s": None}
    return {"n": len(demoras), "mediana_s": round(statistics.median(demoras), 3),
            "p95_s": round(percentil(demoras, 95), 3), "max_s": round(max(demoras), 3)}


def _sumar_recall(destino: dict, origen: dict) -> None:
    for grupo, terminos in origen.items():
        for t, celda in terminos.items():
            d = destino.setdefault(grupo, {}).setdefault(t, {"ref": 0, "ok": 0})
            d["ref"] += celda["ref"]
            d["ok"] += celda["ok"]


def agregar(resultados: list[dict[str, Any]]) -> dict[str, Any]:
    """Junta los resultados de varias pruebas (un grupo de toma/condición, o toda una toma).

    Cada resultado trae `etiquetas` (de evaluar_frases), `error` (de error_de_texto), `demoras_s`,
    `segmentos`, `proceso_s`, `audio_s` y `p95_bloque_ms` (None en motores que no van por bloques).
    WER y CER se calculan sobre las sumas (no es el promedio de los WER).
    """
    et = [r["etiquetas"] for r in resultados]
    recall: dict = {}
    for r in resultados:
        _sumar_recall(recall, r["etiquetas"]["recall"])
    palabras = sum(r["error"]["palabras_ref"] for r in resultados)
    caracteres = sum(r["error"]["caracteres_ref"] for r in resultados)
    demoras = [d for r in resultados for d in r["demoras_s"]]
    audio = sum(r["audio_s"] for r in resultados)
    proceso = sum(r["proceso_s"] for r in resultados)
    p95s = [r["p95_bloque_ms"] for r in resultados if r.get("p95_bloque_ms") is not None]
    n_frases = sum(e["n_frases"] for e in et)
    segmentos = sum(r["segmentos"] for r in resultados)

    def recall_de(grupo: str) -> dict[str, Any]:
        celdas = recall.get(grupo, {})
        ref, ok = sum(c["ref"] for c in celdas.values()), sum(c["ok"] for c in celdas.values())
        return {"ocurrencias_ref": ref, "acertadas": ok, "recall": round(ok / ref, 4) if ref else None,
                "por_termino": {t: dict(c, recall=round(c["ok"] / c["ref"], 4)) for t, c in sorted(celdas.items())}}

    return {
        "pruebas": len(resultados),
        "frases": n_frases,
        "frases_correctas": sum(e["frases_correctas"] for e in et),
        "frases_con_etiquetas_ref": sum(e["frases_con_etiquetas_ref"] for e in et),
        "positivas_correctas": sum(e["positivas_correctas"] for e in et),
        "negativas": sum(e["negativas"] for e in et),
        "negativas_correctas": sum(e["negativas_correctas"] for e in et),
        "etiquetas_nuevas_en_negativas": sum(e["etiquetas_nuevas_en_negativas"] for e in et),
        "etiquetas_perdidas": sum(e["etiquetas_perdidas"] for e in et),
        "etiquetas_nuevas_en_positivas": sum(e["etiquetas_nuevas_en_positivas"] for e in et),
        "recall_criticos": recall_de("criticos"),
        "recall_entidades": recall_de("entidades"),
        "recall_jerga": recall_de("jerga"),
        "wer": round(sum(r["error"]["wer_distancia"] for r in resultados) / palabras, 4) if palabras else None,
        "cer": round(sum(r["error"]["cer_distancia"] for r in resultados) / caracteres, 4) if caracteres else None,
        "segmentos_finales": segmentos,
        "segmentos_por_frase": round(segmentos / n_frases, 3) if n_frases else None,
        "demora_final": resumen_demoras(demoras),
        "audio_s": round(audio, 3),
        "proceso_s": round(proceso, 3),
        "rtf": round(proceso / audio, 4) if audio else None,
        "p95_bloque_ms": ({"mediana": round(statistics.median(p95s), 2), "max": round(max(p95s), 2)} if p95s else None),
    }


# --- Regla de paso del plan --------------------------------------------------------------------------


def regla_de_paso(candidato: dict[str, Any], anterior: dict[str, Any]) -> dict[str, Any]:
    """Aplica la regla del plan (§2) a dos agregados de la toma 2: el candidato contra el paso anterior.

    Se queda solo si cumple las cuatro:
    1. acierta las etiquetas de al menos 2 frases más;
    2. no agrega etiquetas en las frases negativas (no tiene más que el paso anterior);
    3. la mediana de la demora de la frase final no sube más de 0,3 s;
    4. el WER no empeora más de 2 puntos.
    Si falta un dato (por ejemplo, la demora de un motor por lotes) el criterio no se puede evaluar
    y el paso no se queda.
    """
    frases_mas = candidato["frases_correctas"] - anterior["frases_correctas"]
    nuevas = candidato["etiquetas_nuevas_en_negativas"] - anterior["etiquetas_nuevas_en_negativas"]
    d_cand, d_ant = candidato["demora_final"]["mediana_s"], anterior["demora_final"]["mediana_s"]
    demora_extra = None if d_cand is None or d_ant is None else round(d_cand - d_ant, 3)
    wer_extra = (None if candidato["wer"] is None or anterior["wer"] is None
                 else round(candidato["wer"] - anterior["wer"], 4))
    criterios = {
        "etiquetas": {"frases_mas": frases_mas, "minimo": MIN_FRASES_MAS, "cumple": frases_mas >= MIN_FRASES_MAS},
        "negativas": {"etiquetas_nuevas": nuevas, "maximo": 0, "cumple": nuevas <= 0},
        "demora": {"extra_s": demora_extra, "maximo_s": MAX_DEMORA_EXTRA_S,
                   "cumple": demora_extra is not None and demora_extra <= MAX_DEMORA_EXTRA_S + 1e-9},
        "wer": {"extra": wer_extra, "maximo": MAX_WER_EXTRA,
                "cumple": wer_extra is not None and wer_extra <= MAX_WER_EXTRA + 1e-9},
    }
    return {"pasa": all(c["cumple"] for c in criterios.values()), "criterios": criterios}
