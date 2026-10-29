"""Compara frase aislada y contexto reciente con RoBERTuito congelado (#99).

Entrena, guarda, recarga y valida clasificadores con el mismo encoder
congelado usando frase aislada y ventanas recientes. Solo stdlib + las
dependencias ya usadas por `entrenar_tito.py`/`tito_real.py`
(torch/transformers/scikit-learn).

Limites de la preparacion delegada (CONFIGURACION-TITO-2026-10-29.json):
encoder `pysentimiento/robertuito-base-uncased` revision `20cb39...`,
congelado; dos entradas (frase control / historial acumulado);
C en {0.1, 1.0, 10.0}; umbrales {0.3, 0.5, 0.7}; seed 42.
Seis clasificadores y 18 configuraciones como maximo. Seleccion y
desempates definidos en la configuracion, solo con validacion; el
candidato principal usa historial. Tito viejo queda inalterado.

Supervision por prefijo (0/1/nulo) provista por `supervision_tito_99.py`
(dueno: otro worker, issue #99). Este modulo NO genera etiquetas con
heuristicas ni marca supervision como ejecutada: si el supervisor real
no esta disponible, el paso de supervision y el entrenamiento fallan
cerrado (fail-closed) sin inventar etiquetas. Los nulos quedan fuera de
perdida y metricas binarias y se conservan en cobertura. No se toca
`revision_humana` ni la puerta formal de `datos_tito.py`; la autorizacion
de desarrollo es explicita y esta separada de la puerta humana.

No lee la reserva (rechazo por identificador/particion). No decide con
las veinte de comparacion ni con el diagnostico: seleccion solo con
entrenamiento/validacion.

Uso (desde este directorio, con .venv activado en la raiz):
    python entrenar_tito_99.py --paso auditoria
    python entrenar_tito_99.py --paso supervision
    python entrenar_tito_99.py --paso entrenar
    python entrenar_tito_99.py --paso evaluar
    python entrenar_tito_99.py   # todo en orden
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import re
import subprocess
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]

CONFIG = json.loads((AQUI / "CONFIGURACION-TITO-2026-10-29.json").read_text(encoding="utf-8"))
SEMILLA = 42
ENCODER_ID = "pysentimiento/robertuito-base-uncased"
ENCODER_REVISION = "20cb399e4b93f270c0cd6b6f533bcb0ada3cb658"
TOKENIZER_SHA_DECLARADO = "9465c3d57686e6b117d7c8f0e65b2b7d3a6bfb1d3c5154b52b175b3e37f2047c"
TOKENS_POR_BLOQUE = 128
CONTENIDO_POR_BLOQUE = TOKENS_POR_BLOQUE - 2  # espacio para CLS/SEP
ENTRADAS = ("frase_actual_control", "historial_acumulado")
VALORES_C = (0.1, 1.0, 10.0)
UMBRALES = (0.3, 0.5, 0.7)
SOLVER, MAX_ITER = "lbfgs", 1000

AUTORIZACION_DESARROLLO = (
    "autorizacion_desarrollo_99: etiquetado IA de desarrollo para exploracion, "
    "separado de la puerta formal humana de datos_tito.py. NO es revision_humana; "
    "no habilita uso ni cierra D07/D08/D09."
)

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def sha(crudo: bytes) -> str:
    return hashlib.sha256(crudo).hexdigest()


def git_show(commit: str, ruta: str) -> bytes:
    r = subprocess.run(["git", "show", f"{commit}:{ruta}"],
                       cwd=RAIZ, capture_output=True, check=True, timeout=120)
    return r.stdout


def normalizar(texto: str) -> str:
    """Minusculas, sin acentos, espacios colapsados. Para comparacion y reglas."""
    base = unicodedata.normalize("NFKD", texto.casefold())
    base = "".join(c for c in base if not unicodedata.combining(c))
    return " ".join(base.split())


def info_codigo() -> dict:
    def git(*args: str) -> str:
        try:
            r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True,
                               text=True, timeout=10, check=True)
            return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return "desconocido"
    return {
        "commit": git("rev-parse", "HEAD"),
        "estado": git("status", "--porcelain", "--", ".", ":(exclude)corridas"),
        "script_sha256": sha(Path(__file__).read_bytes()),
    }


def info_maquina() -> dict:
    try:
        from torch import cuda
        gpu = cuda.get_device_name(0) if cuda.is_available() else None
    except Exception:
        gpu = None
    mem_gb = None
    try:
        if sys.platform.startswith("linux"):
            for renglon in Path("/proc/meminfo").read_text().splitlines():
                if renglon.startswith("MemTotal:"):
                    mem_gb = round(int(renglon.split()[1]) / 1024 ** 2, 1)
    except OSError:
        pass
    return {"sistema": platform.platform(),
            "procesador": platform.processor() or "no informado",
            "nucleos_logicos": os.cpu_count(), "ram_total_gb": mem_gb,
            "gpu": gpu, "python": platform.python_version()}


# ---------------------------------------------------------------------------
# Carga de particiones, textos y referencias (sin reserva, sin modelos)
# ---------------------------------------------------------------------------

def cargar_particiones() -> dict:
    ruta = AQUI / CONFIG["particiones"]
    particiones = json.loads(ruta.read_text(encoding="utf-8"))
    if particiones.get("semilla") != SEMILLA:
        raise ValueError("particiones con semilla inesperada.")
    return particiones


def _rechazar_reserva_ids(ids: list[str]) -> None:
    from datos_tito import rechazar_reserva
    rechazar_reserva(ids)


def cargar_conversaciones(particiones: dict) -> tuple[dict, dict]:
    """Devuelve (textos, referencias) por case_id para train/val. Solo esas."""
    from casos import cargar_referencia, cargar_texto
    from datos_tito import rechazar_reserva
    convs = [c for c in particiones["conversaciones"]
             if c["particion_preparacion"] in ("entrenamiento", "validacion")]
    textos, referencias = {}, {}
    for c in convs:
        cid = c["case_id"]
        rechazar_reserva([cid])
        lineas = cargar_texto(cid)
        crudo_txt = (AQUI / "casos" / "texto" / f"{cid}.txt").read_bytes()
        crudo_ref = (AQUI / "casos" / "referencia" / f"{cid}.json").read_bytes()
        if sha(crudo_txt) != c["texto_sha256"]:
            raise ValueError(f"{cid}: el texto cambio desde la particion.")
        if sha(crudo_ref) != c["referencia_sha256"]:
            raise ValueError(f"{cid}: la referencia cambio desde la particion.")
        textos[cid] = [f"{l.hablante}: {l.texto}" for l in lineas]
        referencias[cid] = cargar_referencia(cid)
    return textos, referencias


def cargar_banco(particiones: dict) -> tuple[list[dict], dict]:
    """Frases del banco conservadas con particion train/val, desde el commit fijado."""
    from entrenar_tito import (BANCO_BASE, BANCO_COMMIT, EJEMPLOS_SHA_DECLARADO,
                               EXCLUSIONES_SHA_DECLARADA)
    ejemplos_raw = git_show(BANCO_COMMIT, f"{BANCO_BASE}/ejemplos.jsonl")
    exclusiones_raw = git_show(BANCO_COMMIT, f"{BANCO_BASE}/exclusiones.json")
    if sha(ejemplos_raw) != EJEMPLOS_SHA_DECLARADO:
        raise ValueError("ejemplos.jsonl no coincide con el hash declarado.")
    if sha(exclusiones_raw) != EXCLUSIONES_SHA_DECLARADA:
        raise ValueError("exclusiones.json no coincide con el hash declarado.")
    por_id = {json.loads(l)["id"]: json.loads(l)
              for l in ejemplos_raw.decode("utf-8").splitlines()}
    banco = []
    for b in particiones["banco"]:
        if b["particion_preparacion"] not in ("entrenamiento", "validacion"):
            continue
        fila = por_id.get(b["id"])
        if fila is None or fila["familia"] != b["familia"]:
            raise ValueError(f"banco {b['id']}: no esta en el commit fijado.")
        if normalizar(fila["texto"]) and sha(fila["texto"].encode("utf-8")) != b.get(
                "texto_sha256", sha(fila["texto"].encode("utf-8"))):
            raise ValueError(f"banco {b['id']}: el texto cambio.")
        banco.append({"id": b["id"], "familia": b["familia"],
                      "clase_autoral": b["clase_autoral"],
                      "particion": b["particion_preparacion"],
                      "texto": fila["texto"],
                      "etiqueta": 1 if fila["etiqueta"] == "estafa" else 0})
    return banco, {"banco_commit": BANCO_COMMIT,
                   "ejemplos_sha256": sha(ejemplos_raw),
                   "exclusiones_sha256": sha(exclusiones_raw)}


# ---------------------------------------------------------------------------
# Paso 1: auditoria semantica banco <-> conversaciones
# ---------------------------------------------------------------------------

def auditar_relaciones(banco: list[dict], textos: dict,
                       particion_de: dict[str, str]) -> dict:
    """Relaciones semanticas entre frases del banco y lineas de train/val.

    Tres criterios sobre texto normalizado: igualdad exacta, inclusion
    como subcadena (minimo 20 caracteres) y Jaccard de tokens >= 0.80.
    Agrega por familia del banco: una familia relacionada se excluye del
    ajuste. La separacion por ID no prueba independencia; esto la audita.
    """
    lineas_norm: list[tuple[str, str, int]] = []  # (cid, norm, idx)
    bolsas: list[tuple[str, set[str]]] = []
    for cid, lineas in textos.items():
        for i, linea in enumerate(lineas):
            n = normalizar(linea)
            lineas_norm.append((cid, n, i))
            bolsas.append((cid, set(n.split())))
    exactas = {n for _, n, _ in lineas_norm}
    relacionadas: dict[str, list[dict]] = {}
    for frase in banco:
        fn = normalizar(frase["texto"])
        if not fn:
            continue
        fset = set(fn.split())
        hallazgos = []
        if fn in exactas:
            hallazgos.append({"criterio": "igualdad_exacta", "linea": fn[:80]})
        for cid, ln, idx in lineas_norm:
            if len(fn) >= 20 and (fn in ln or ln in fn) and fn != ln:
                hallazgos.append({"criterio": "subcadena", "caso": cid,
                                  "linea": idx + 1, "texto": ln[:80]})
                break
        if not hallazgos:
            for cid, bset in bolsas:
                if fset and bset and len(fset & bset) / len(fset | bset) >= 0.80:
                    hallazgos.append({"criterio": "jaccard>=0.80", "caso": cid})
                    break
        if hallazgos:
            relacionadas.setdefault(frase["familia"], []).append(
                {"id": frase["id"], "hallazgo": hallazgos[0]})
    familias_excluidas = sorted(relacionadas)
    banco_restante = [f for f in banco if f["familia"] not in relacionadas]
    conteo_antes = dict(Counter((f["particion"], f["clase_autoral"]) for f in banco))
    conteo_despues = dict(Counter((f["particion"], f["clase_autoral"]) for f in banco_restante))
    clases_restantes = {f["clase_autoral"] for f in banco_restante}
    return {"criterios": ["igualdad_exacta", "subcadena>=20", "jaccard>=0.80"],
            "frases_auditadas": len(banco),
            "familias_relacionadas_excluidas": familias_excluidas,
            "detalle_por_familia": {k: v[:3] for k, v in relacionadas.items()},
            "conteo_antes": {f"{k[0]}/{k[1]}": v for k, v in conteo_antes.items()},
            "conteo_despues": {f"{k[0]}/{k[1]}": v for k, v in conteo_despues.items()},
            "clases_restantes": sorted(clases_restantes),
            "sintetico_necesario": len(clases_restantes) < 2,
            "nota": ("Exclusion por familia completa. Si falta una clase se "
                     "prepara material sintetico de desarrollo trazable sin "
                     "reserva; no se sustituyen las veinte ni se pide al usuario.")}


# ---------------------------------------------------------------------------
# Paso 2: supervision por prefijo (delegada al supervisor real, sin heuristicas)
# ---------------------------------------------------------------------------

def construir_supervision(textos: dict, particion_de: dict[str, str]) -> tuple[list[dict], dict]:
    """Delega al supervisor real `supervision_tito_99.py` (dueno: otro worker).

    Este modulo no genera etiquetas heuristicas. Si el supervisor real no
    esta disponible, falla cerrado (fail-closed): no inventa etiquetas ni
    marca supervision como ejecutada.
    """
    try:
        from supervision_tito_99 import construir_supervision as _real
    except ImportError as e:
        raise SystemExit(
            "supervision fail-closed: `supervision_tito_99.py` no disponible "
            f"({type(e).__name__}); el supervisor real es del otro worker. "
            "No se inventan etiquetas ni se marca ejecutado.") from e
    return _real(textos, particion_de)


# ---------------------------------------------------------------------------
# Entradas, embeddings por bloques y ajuste (encoder congelado)
# ---------------------------------------------------------------------------

def construir_entrada(lineas_visibles: list[str], entrada: str,
                      sintetico: bool = False) -> str:
    """Misma construccion en entrenamiento e inferencia. Sin futuro.

    `frase_actual_control`: solo la linea nueva. `historial_acumulado`:
    todo lo disponible hasta la actualizacion, con hablantes A/B, y
    reinicio por conversacion (cada llamada empieza vacia). Un ejemplo del
    banco se presenta como frase sintetica de una linea, nunca como
    conversacion real.
    """
    if entrada == "frase_actual_control":
        texto = lineas_visibles[-1].split(": ", 1)[-1] if not sintetico else lineas_visibles[-1]
        return ("FRASE SINTETICA: " + texto) if sintetico else texto
    if entrada == "historial_acumulado":
        if sintetico:
            return "FRASE SINTETICA | A: " + lineas_visibles[-1]
        return "\n".join(lineas_visibles)
    raise ValueError(f"entrada desconocida: {entrada!r}")


def _cargar_tokenizer_modelo():
    import torch
    from transformers import AutoModel, AutoTokenizer
    from huggingface_hub import snapshot_download
    snap = Path(snapshot_download(ENCODER_ID, revision=ENCODER_REVISION))
    tok_sha = sha((snap / "tokenizer.json").read_bytes())
    if tok_sha != TOKENIZER_SHA_DECLARADO:
        raise ValueError(f"tokenizer.json inesperado: {tok_sha}.")
    tokenizer = AutoTokenizer.from_pretrained(str(snap))
    modelo = AutoModel.from_pretrained(str(snap))
    for p in modelo.parameters():
        p.requires_grad_(False)
    modelo.eval()
    if any(p.requires_grad for p in modelo.parameters()):
        raise ValueError("El encoder no quedo congelado.")
    return tokenizer, modelo, torch, tok_sha


def incrustar_bloques(textos: list[str], tokenizer, modelo, torch,
                      dispositivo: str = "cpu") -> tuple[list[list[float]], dict]:
    """Promedio ponderado por tokens de contenido en bloques de 128.

    Tokeniza el historial completo sin truncar; lo divide en bloques
    consecutivos sin solapamiento con espacio para tokens especiales;
    promedia estados de tokens de contenido por bloque (excluye padding y
    especiales) y combina bloques ponderando por cantidad de tokens. No
    descarta lineas. Conserva contenido, pero no hay atencion conjunta
    entre bloques: se registra el limite.
    """
    import torch as _t  # noqa: F401 (verificacion de presencia)
    vectores, bloques_total, tokens_total, t0 = [], 0, 0, time.perf_counter()
    cls_id = tokenizer.cls_token_id
    sep_id = tokenizer.sep_token_id
    with torch.no_grad():
        for texto in textos:
            contenido = tokenizer(texto, add_special_tokens=False,
                                  padding=False, truncation=False)["input_ids"]
            if not contenido:
                vectores.append([0.0] * int(modelo.config.hidden_size))
                continue
            partes = [contenido[i:i + CONTENIDO_POR_BLOQUE]
                      for i in range(0, len(contenido), CONTENIDO_POR_BLOQUE)]
            suma, peso = None, 0
            for parte in partes:
                ids = _t.tensor([[cls_id, *parte, sep_id]])
                mask = _t.ones_like(ids, dtype=_t.float)
                h = modelo(input_ids=ids, attention_mask=mask).last_hidden_state[0]
                estados = h[1:1 + len(parte)]
                bloque = estados.mean(dim=0)
                contrib = bloque * len(parte)
                suma = contrib if suma is None else suma + contrib
                peso += len(parte)
            vectores.append((suma / peso).tolist())
            bloques_total += len(partes)
            tokens_total += len(contenido)
    return vectores, {"bloques": bloques_total, "tokens_contenido": tokens_total,
                      "truncamientos": 0, "limite_entre_bloques":
                      "sin atencion conjunta entre bloques; promedio ponderado por tokens",
                      "ms_incrustacion": round((time.perf_counter() - t0) * 1000, 1)}


def ajustar_regresion(X, y: list[int], C: float) -> dict:
    from sklearn.linear_model import LogisticRegression
    clf = LogisticRegression(C=C, solver=SOLVER, max_iter=MAX_ITER,
                             random_state=SEMILLA)
    t0 = time.perf_counter()
    clf.fit(X, y)
    ms = (time.perf_counter() - t0) * 1000
    if clf.classes_.tolist() != [0, 1]:
        raise ValueError(f"clases inesperadas: {clf.classes_.tolist()}.")
    return {"coef": clf.coef_[0].tolist(),
            "intercepto": float(clf.intercept_[0]),
            "n_iter": [int(n) for n in clf.n_iter_],
            "ms_ajuste": round(ms, 1)}


FORMATO_99 = "tito-99-logreg-v1"


def guardar_artefacto(ruta: Path, entrada: str, C: float, pesos: dict,
                      tok_sha: str, datos_info: dict, codigo: dict,
                      maquina: dict, librerias: dict) -> None:
    arte = {"formato": FORMATO_99, "entrada": entrada,
            "config_regresion": {"semilla": SEMILLA, "C": C, "solver": SOLVER,
                                 "max_iter": MAX_ITER, "class_weight": None},
            "pesos": pesos,
            "encoder": {"id": ENCODER_ID, "revision": ENCODER_REVISION,
                        "congelado": True,
                        "representacion": "promedio_ponderado_bloques_128_ultima_capa",
                        "hidden": len(pesos["coef"])},
            "tokenizador": {"revision_declarada": ENCODER_REVISION,
                            "tokenizer_sha256": tok_sha,
                            "tokens_por_bloque": TOKENS_POR_BLOQUE,
                            "truncamientos": 0},
            "datos": datos_info, "codigo": codigo, "maquina": maquina,
            "librerias": librerias,
            "nota_uso": ("Candidato #99 con encoder congelado. Recargable para "
                         "recorrer conversaciones sin reentrenar. Tito viejo "
                         "(tito_logreg.json) inalterado.")} 
    ruta.write_text(json.dumps(arte, ensure_ascii=False, indent=1), encoding="utf-8")


def cargar_artefacto_99(ruta: str | Path) -> dict:
    arte = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if arte.get("formato") != FORMATO_99:
        raise ValueError(f"artefacto desconocido: {arte.get('formato')!r}.")
    if arte["config_regresion"].get("semilla") != SEMILLA:
        raise ValueError("semilla inesperada en el artefacto.")
    if arte["encoder"]["revision"] != ENCODER_REVISION:
        raise ValueError("revision de encoder inesperada.")
    if len(arte["pesos"]["coef"]) != arte["encoder"]["hidden"]:
        raise ValueError("pesos y dimension del encoder no coinciden.")
    return arte


class Tito99:
    """Filtro recargado desde un artefacto #99. Sin estado entre llamadas."""

    nombre = "tito-99"

    def __init__(self, artefacto: str | Path) -> None:
        self.arte = cargar_artefacto_99(artefacto)
        self.entrada = self.arte["entrada"]
        self.coef = self.arte["pesos"]["coef"]
        self.intercepto = float(self.arte["pesos"]["intercepto"])
        self._tok = self._mod = self._torch = None

    def _asegurar_encoder(self):
        if self._tok is None:
            self._tok, self._mod, self._torch, _ = _cargar_tokenizer_modelo()
        return self._tok, self._mod, self._torch

    def puntuar_entrada(self, texto_entrada: str) -> tuple[float | None, str, float]:
        inicio = time.perf_counter()
        try:
            tok, mod, torch = self._asegurar_encoder()
            (vec,) = incrustar_bloques([texto_entrada], tok, mod, torch)[0]
        except Exception as e:  # noqa: BLE001 - el flujo lo registra como fallo
            return None, f"tito99_error: {type(e).__name__}", \
                (time.perf_counter() - inicio) * 1000
        z = sum(c * x for c, x in zip(self.coef, vec)) + self.intercepto
        if not math.isfinite(z):
            return None, f"tito99_error: puntaje no finito (z={z!r})", \
                (time.perf_counter() - inicio) * 1000
        return sigmoide(z), "", (time.perf_counter() - inicio) * 1000

    def puntuar_prefijo(self, lineas_visibles: list[str],
                        sintetico: bool = False) -> tuple[float | None, str, float]:
        return self.puntuar_entrada(construir_entrada(lineas_visibles, self.entrada,
                                                      sintetico))


# ---------------------------------------------------------------------------
# Paso 3: evaluacion por replay conversacional (seleccion solo validacion)
# ---------------------------------------------------------------------------

def sigmoide(z: float) -> float:
    """Sigmoide numericamente estable y finita (sin OverflowError)."""
    if math.isnan(z):
        raise ValueError(f"sigmoide con z no finita: {z!r}.")
    if math.isinf(z):
        return 1.0 if z > 0 else 0.0
    if z >= 0:
        return 1.0 / (1.0 + math.exp(-z))
    e = math.exp(z)
    return e / (1.0 + e)


def puntajes_matriz(X, coef, intercepto: float) -> list[float]:
    out = []
    for vec in X:
        z = sum(c * x for c, x in zip(coef, vec)) + intercepto
        if not math.isfinite(z):
            raise ValueError(f"puntaje no finito (z={z!r}); revisar pesos/vectores.")
        out.append(sigmoide(z))
    return out


def percentil_95(muestras: list[float]) -> float:
    """Percentil 95 por rango mas cercano (no la media)."""
    if not muestras:
        return 0.0
    orden = sorted(muestras)
    k = math.ceil(0.95 * len(orden)) - 1
    return float(orden[max(0, min(k, len(orden) - 1))])


def recorrer_conversacion(puntajes: list[float], umbral: float) -> int | None:
    """Primera actualizacion con puntaje >= umbral (igualdad incluida)."""
    for k, p in enumerate(puntajes, start=1):
        if p >= umbral:
            return k
    return None


def evaluar_configuracion(registros_val: list[dict], textos_val: dict,
                          referencias: dict, puntaje_de,
                          umbral: float) -> dict:
    """Metricas conversacionales sobre validacion. Sin F1 como criterio.

    Conserva posiciones: los puntajes `None` (fallos de inferencia) no se
    filtran antes de la primera derivacion; la derivacion es el primer `k`
    con puntaje no nulo >= umbral. Los fallos se cuentan y diagnostican
    (fail-open: no derivan por si mismos).
    """
    por_caso, omisiones, legit_derivadas = [], 0, 0
    total_fallos = 0
    for cid in sorted(textos_val):
        lineas = textos_val[cid]
        puntajes: list[float | None] = []
        errores: list[str] = []
        fallos = 0
        ms = []
        for k in range(1, len(lineas) + 1):
            p, err, m = puntaje_de(cid, k)
            puntajes.append(p)
            ms.append(m)
            if p is None:
                fallos += 1
                total_fallos += 1
                if err:
                    errores.append(f"k={k}:{err}")
        der = None
        for k, p in enumerate(puntajes, start=1):
            if p is not None and p >= umbral:
                der = k
                break
        ref = referencias[cid]
        clase = ref.get("clase")
        t_r, t_c = ref.get("t_r_linea"), ref.get("t_c_linea")
        n = len(lineas)
        if clase == "vishing":
            a_tiempo = der is not None and (t_c is None or der <= t_c)
            if not a_tiempo:
                omisiones += 1
            posicion = ("sin_derivacion" if der is None
                        else "antes_de_T_R" if t_r is not None and der < t_r
                        else "en_T_R" if t_r is not None and der == t_r
                        else "tras_T_R")
        else:
            a_tiempo = None
            posicion = "sin_derivacion" if der is None else "derivada"
            if der is not None:
                legit_derivadas += 1
        por_caso.append({"case_id": cid, "clase": clase, "n_lineas": n,
                         "t_r": t_r, "t_c": t_c, "derivacion": der,
                         "oportuna": a_tiempo, "posicion": posicion,
                         "consultas": der if der is not None else n,
                         "fallos": fallos, "errores": errores,
                         "puntajes": [(None if p is None else round(p, 4))
                                      for p in puntajes]})
    consultas = [c["consultas"] for c in por_caso]
    return {"umbral": umbral, "omisiones_oportunas": omisiones,
            "legitimas_derivadas": legit_derivadas,
            "denominador_vishing": sum(1 for c in por_caso if c["clase"] == "vishing"),
            "denominador_legitimas": sum(1 for c in por_caso if c["clase"] != "vishing"),
            "prefijos_con_fallo": total_fallos,
            "consultas_media": round(sum(consultas) / len(consultas), 2),
            "por_caso": por_caso}


def seleccionar_candidatos(resultados: list[dict], costos_p95: dict) -> dict:
    """Frontera de Pareto + desempates de la configuracion. Solo validacion."""
    frente = []
    for r in resultados:
        dominado = any(
            o["omisiones_oportunas"] <= r["omisiones_oportunas"]
            and o["legitimas_derivadas"] <= r["legitimas_derivadas"]
            and o["consultas_media"] <= r["consultas_media"]
            and (o["omisiones_oportunas"] < r["omisiones_oportunas"]
                 or o["legitimas_derivadas"] < r["legitimas_derivadas"]
                 or o["consultas_media"] < r["consultas_media"])
            for o in resultados)
        if not dominado:
            frente.append(r["config"])
    cands = [r for r in resultados if r["config"] in frente]
    cands.sort(key=lambda r: (r["omisiones_oportunas"] + r["legitimas_derivadas"],
                              costos_p95.get(r["config"], float("inf")),
                              abs(r["C"] - 1.0), abs(r["umbral"] - 0.5)))
    elegida = next((r for r in cands if r["entrada"] == "historial_acumulado"), cands[0])
    return {"frontera_pareto": sorted(frente),
            "orden": [r["config"] for r in cands],
            "elegida": elegida["config"],
            "criterio": ("Pareto en omisiones oportunas, legitimas derivadas y "
                         "costo sobre validacion conversacional; desempate por "
                         "menor suma, menor costo p95, C cercano a 1 y umbral "
                         "cercano a 0.5. Principal con historial.")}


# ---------------------------------------------------------------------------
# Orquestacion
# ---------------------------------------------------------------------------

def _nombre_arte(entrada: str, C: float) -> str:
    return f"tito_99_{'historial' if entrada == 'historial_acumulado' else 'frase'}_C{C}.json"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paso", choices=["auditoria", "supervision", "entrenar",
                                      "evaluar", "todo"], default="todo")
    args = p.parse_args(argv)

    particiones = cargar_particiones()
    _rechazar_reserva_ids([c["case_id"] for c in particiones["conversaciones"]])
    _rechazar_reserva_ids([c["case_id"] for c in particiones["conversaciones"]
                           if c["particion_preparacion"] == "comparacion_20"])
    particion_de = {c["case_id"]: c["particion_preparacion"]
                    for c in particiones["conversaciones"]}
    textos, referencias = cargar_conversaciones(particiones)
    banco, banco_info = cargar_banco(particiones)
    codigo, maquina = info_codigo(), info_maquina()

    if args.paso in ("auditoria", "todo"):
        auditoria = auditar_relaciones(banco, textos, particion_de)
        (AQUI / "AUDITORIA-SEMANTICA-TITO-99-2026-10-29.json").write_text(
            json.dumps({"fecha": "2026-10-29", "semilla": SEMILLA,
                        "auditoria": auditoria, "codigo": codigo},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"auditoria: {len(auditoria['familias_relacionadas_excluidas'])} "
              f"familias relacionadas excluidas; "
              f"conteo despues={auditoria['conteo_despues']}")
        if auditoria["sintetico_necesario"]:
            print("auditoria: FALTA UNA CLASE tras exclusiones; "
                  "se requiere material sintetico antes de entrenar.")
            return 2 if args.paso == "auditoria" else 2

    auditoria = json.loads((AQUI / "AUDITORIA-SEMANTICA-TITO-99-2026-10-29.json").read_text(
        encoding="utf-8"))["auditoria"]
    excluidas = set(auditoria["familias_relacionadas_excluidas"])
    banco_ajuste = [f for f in banco if f["familia"] not in excluidas]

    if args.paso in ("supervision", "todo"):
        registros, cobertura = construir_supervision(textos, particion_de)
        with (AQUI / "SUPERVISION-TITO-99-2026-10-29.jsonl").open(
                "w", encoding="utf-8") as f:
            for r in registros:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"supervision: {cobertura}")
        nulos = sum(1 for r in registros if r["etiqueta"] is None)
        unos = sum(1 for r in registros if r["etiqueta"] == 1)
        if unos == 0 or sum(1 for r in registros if r["etiqueta"] == 0) == 0:
            print("supervision: FALTA UNA CLASE en prefijos; "
                  "preparar material sintetico trazable antes de entrenar.")
            return 3

    if args.paso not in ("entrenar", "evaluar", "todo"):
        return 0

    import sklearn, tokenizers, transformers  # noqa: F401
    import torch

    if args.paso in ("entrenar", "todo"):
        librerias = {"torch": torch.__version__,
                     "transformers": transformers.__version__,
                     "scikit-learn": sklearn.__version__,
                     "tokenizers": tokenizers.__version__,
                     "numpy": __import__("numpy").__version__}
        tokenizer, modelo, torch_mod, tok_sha = _cargar_tokenizer_modelo()
        dispositivo = "cpu"

        sup = [json.loads(l) for l in (AQUI / "SUPERVISION-TITO-99-2026-10-29.jsonl")
               .read_text(encoding="utf-8").splitlines()]
        etiqueta_de = {(r["case_id"], r["hasta_linea"]): r["etiqueta"] for r in sup}

        # Conjuntos: prefijos etiquetados (train) + banco sintetico (train).
        # Misma construccion de entradas que en inferencia (sin futuro).
        X_textos = {e: [] for e in ENTRADAS}
        y, de_conversacion = [], []
        for (cid, k), et in sorted(etiqueta_de.items(),
                                   key=lambda kv: (kv[0][0], kv[0][1])):
            if particion_de[cid] != "entrenamiento" or et is None:
                continue
            visibles = textos[cid][:k]
            for e in ENTRADAS:
                X_textos[e].append(construir_entrada(visibles, e))
            y.append(et)
            de_conversacion.append(f"{cid}#{k}")
        for f in banco_ajuste:
            if f["particion"] != "entrenamiento":
                continue
            for e in ENTRADAS:
                X_textos[e].append(construir_entrada([f["texto"]], e, sintetico=True))
            y.append(f["etiqueta"])
            de_conversacion.append(f"banco:{f['id']}")
        print(f"entrenamiento: {len(y)} ejemplos "
              f"({sum(y)} unos, {len(y) - sum(y)} ceros)")

        artefactos = {}
        for e in ENTRADAS:
            X, info_emb = incrustar_bloques(X_textos[e], tokenizer, modelo,
                                            torch_mod, dispositivo)
            assert info_emb["truncamientos"] == 0
            for C in VALORES_C:
                pesos = ajustar_regresion(X, y, C)
                datos_info = {**banco_info, "prefijos_conversacionales": len(
                    [d for d in de_conversacion if not d.startswith("banco:")]),
                    "frases_banco": len(
                        [d for d in de_conversacion if d.startswith("banco:")]),
                    "familias_banco_excluidas": sorted(excluidas),
                    "split": "train=PARTICIONES-TITO-2026-10-29/entrenamiento",
                    "incrustacion": info_emb}
                guardar_artefacto(AQUI / _nombre_arte(e, C), e, C, pesos, tok_sha,
                                  datos_info, codigo, maquina, librerias)
                artefactos[(e, C)] = pesos
                print(f"  guardado {_nombre_arte(e, C)}")
        if len(artefactos) > 6:
            raise ValueError("mas de seis clasificadores.")
        if args.paso == "entrenar":
            return 0

    # --- Evaluacion: solo carga desde disco, sin reentrenar ni sobrescribir ---
    # No se ajusta ni se guarda ningun artefacto en este paso; el encoder se
    # carga una sola vez para incrustar validacion (preparacion separada del
    # costo de inferencia) y nunca una vez por candidato.
    import sklearn as _sk, tokenizers as _tok, transformers as _tr  # noqa: F401
    import torch as _torch
    librerias = {"torch": _torch.__version__,
                 "transformers": _tr.__version__,
                 "scikit-learn": _sk.__version__,
                 "tokenizers": _tok.__version__,
                 "numpy": __import__("numpy").__version__}
    recargados = {}
    tok_sha = None
    for e in ENTRADAS:
        for C in VALORES_C:
            ruta = AQUI / _nombre_arte(e, C)
            if not ruta.exists():
                raise SystemExit(
                    f"evaluacion fail-closed: falta {ruta.name}; entrene "
                    "primero (--paso entrenar) sin sobrescribir historico.")
            arte = cargar_artefacto_99(ruta)
            recargados[(e, C)] = (arte["pesos"]["coef"],
                                  float(arte["pesos"]["intercepto"]))
            tok_sha = arte["tokenizador"]["tokenizer_sha256"]
    if tok_sha != TOKENIZER_SHA_DECLARADO:
        raise ValueError(f"tokenizer_sha256 inesperado en artefactos: {tok_sha}.")
    tokenizer, modelo, torch_mod, tok_sha_carga = _cargar_tokenizer_modelo()
    if tok_sha_carga != TOKENIZER_SHA_DECLARADO:
        raise ValueError(f"tokenizer.json inesperado: {tok_sha_carga}.")
    tok_sha = tok_sha_carga
    dispositivo = "cpu"

    textos_val = {cid: l for cid, l in textos.items()
                  if particion_de[cid] == "validacion"}
    # Preparacion separada: incrustar validacion una vez por entrada.
    X_val, preparacion_ms = {}, {}
    for e in ENTRADAS:
        lista = []
        for cid in sorted(textos_val):
            for k in range(1, len(textos_val[cid]) + 1):
                lista.append(construir_entrada(textos_val[cid][:k], e))
        V, info_prep = incrustar_bloques(lista, tokenizer, modelo, torch_mod,
                                         dispositivo)
        X_val[e] = (sorted(textos_val),
                    [len(textos_val[c]) for c in sorted(textos_val)], V)
        preparacion_ms[e] = info_prep["ms_incrustacion"]
    resultados, costos = [], {}
    n_cfgs = 0
    for e in ENTRADAS:
        cids, Ns, V = X_val[e]
        for C in VALORES_C:
            coef, b = recargados[(e, C)]
            punt = puntajes_matriz(V, coef, b)
            por_caso_punt, i = {}, 0
            for cid, n in zip(cids, Ns):
                por_caso_punt[cid] = punt[i:i + n]
                i += n
            # Costo de inferencia: p95 real de latencias por prefijo
            # (solo puntaje lineal+sigmoide sobre vectores ya preparados;
            # sin recargar encoder por candidato). La preparacion se informa
            # aparte en `preparacion_ms_por_entrada`.
            latencias = []
            for vec in V:
                t0 = time.perf_counter()
                z = sum(c * x for c, x in zip(coef, vec)) + b
                sigmoide(z)
                latencias.append((time.perf_counter() - t0) * 1000)
            costo_p95 = percentil_95(latencias)
            for u in UMBRALES:
                n_cfgs += 1
                ev = evaluar_configuracion(
                    [], textos_val, referencias,
                    lambda cid, k, _p=por_caso_punt: (_p[cid][k - 1], "", 0.0), u)
                ev = {"config": f"{e}/C={C}/u={u}", "entrada": e, "C": C,
                      "umbral": u,
                      **{k: v for k, v in ev.items() if k != "umbral"}}
                resultados.append(ev)
                costos[ev["config"]] = round(float(costo_p95), 3)
    assert n_cfgs <= 18, f"mas de 18 configuraciones: {n_cfgs}"
    seleccion = seleccionar_candidatos(resultados, costos)

    # Baseline Tito viejo: frase aislada, umbral 0.5, artefacto inalterado.
    from tito_real import TitoReal
    viejo = TitoReal()
    viejo.preparar()
    def puntaje_viejo(cid, k):
        linea = textos_val[cid][k - 1].split(": ", 1)[-1]
        return viejo.puntuar(k, linea)
    base = evaluar_configuracion([], textos_val, referencias, puntaje_viejo, 0.5)
    eleg = next(r for r in resultados if r["config"] == seleccion["elegida"])
    # Condicion exacta de la configuracion: NINGUN candidato congelado
    # conserva ambas fallas frente al viejo, y existe al menos un error
    # observable que justifique ajustar. Igualar ambos conteos no exige
    # fine-tuning (conserva => no activar).
    conserva_alguno = any(
        r["omisiones_oportunas"] <= base["omisiones_oportunas"]
        and r["legitimas_derivadas"] <= base["legitimas_derivadas"]
        for r in resultados)
    hay_error_observable = (
        (base["omisiones_oportunas"] + base["legitimas_derivadas"] > 0)
        or any(r["omisiones_oportunas"] + r["legitimas_derivadas"] > 0
               for r in resultados))
    activar_ft = (not conserva_alguno) and hay_error_observable
    fine_tuning = {
        "regla": CONFIG["fine_tuning_100"]["activar_si"],
        "baseline_viejo": {"omisiones_oportunas": base["omisiones_oportunas"],
                           "legitimas_derivadas": base["legitimas_derivadas"],
                           "denominador_vishing": base["denominador_vishing"],
                           "denominador_legitimas": base["denominador_legitimas"],
                           "prefijos_con_fallo": base.get("prefijos_con_fallo", 0)},
        "elegido": {"config": eleg["config"],
                    "omisiones_oportunas": eleg["omisiones_oportunas"],
                    "legitimas_derivadas": eleg["legitimas_derivadas"],
                    "denominador_vishing": eleg["denominador_vishing"],
                    "denominador_legitimas": eleg["denominador_legitimas"],
                    "prefijos_con_fallo": eleg.get("prefijos_con_fallo", 0)},
        "candidatos": [{"config": r["config"],
                        "omisiones_oportunas": r["omisiones_oportunas"],
                        "legitimas_derivadas": r["legitimas_derivadas"],
                        "denominador_vishing": r["denominador_vishing"],
                        "denominador_legitimas": r["denominador_legitimas"],
                        "conserva_ambas": bool(
                            r["omisiones_oportunas"] <= base["omisiones_oportunas"]
                            and r["legitimas_derivadas"]
                            <= base["legitimas_derivadas"])}
                       for r in resultados],
        "ningun_congelado_conserva_ambas": (not conserva_alguno),
        "hay_error_observable": hay_error_observable,
        "conserva_o_reduce_elegido": bool(
            eleg["omisiones_oportunas"] <= base["omisiones_oportunas"]
            and eleg["legitimas_derivadas"] <= base["legitimas_derivadas"]),
        "activar_fine_tuning_100": activar_ft,
        "recomendacion_para_100":
            ("evaluar fine-tuning en #100: ningun candidato congelado conserva "
             "ambas fallas frente al viejo en validacion y hay errores "
             "observables que lo justifican" if activar_ft else
             "no forzar fine-tuning por ahora: algun candidato congelado conserva "
             "o reduce ambas fallas frente al viejo en validacion (igualar "
             "ambos conteos no obliga a fine-tuning) o no hay error "
             "observable; #100 decide con errores observables"),
        "advertencia": ("Comparacion solo con validacion de desarrollo; las "
                        "veinte de comparacion y la reserva no intervienen.")}

    if args.paso == "todo":
        n_ej = len(y)
        n_unos = sum(y)
    else:
        primero = cargar_artefacto_99(AQUI / _nombre_arte(ENTRADAS[0], VALORES_C[0]))
        n_ej = (primero["datos"].get("prefijos_conversacionales", 0)
                + primero["datos"].get("frases_banco", 0))
        coef0 = primero["pesos"]["coef"]
        n_unos = f"ver artefacto {primero['datos'].get('frases_banco', '?')} banco + prefijos"
        _ = coef0
    reporte = {"fecha": "2026-10-29", "issue": 99, "semilla": SEMILLA,
               "encoder": {"id": ENCODER_ID, "revision": ENCODER_REVISION,
                           "congelado": True, "tokenizer_sha256": tok_sha},
               "auditoria_semantica": auditoria,
               "entrenamiento": {"ejemplos": n_ej, "unos": n_unos,
                                 "clasificadores": len(ENTRADAS) * len(VALORES_C),
                                 "configuraciones": n_cfgs},
               "preparacion_ms_por_entrada": preparacion_ms,
               "resultados_validacion": resultados,
               "costos_p95_ms": costos, "seleccion": seleccion,
               "criterio_fine_tuning": fine_tuning,
               "codigo": codigo, "maquina": maquina, "librerias": librerias,
               "artefactos": [_nombre_arte(e, C) for e in ENTRADAS for C in VALORES_C],
               "tito_viejo_inalterado": {
                   "artefacto": "tito_logreg.json",
                   "sha256": sha((AQUI / "tito_logreg.json").read_bytes())},
               "limites": ["Seleccion solo con validacion de desarrollo.",
                           "Nulos fuera de perdida y metricas, con cobertura.",
                           "Sin revision humana inventada; puerta formal intacta.",
                           "Reserva no leida; veinte de comparacion sin usar."]}
    (AQUI / "REPORTE-TITO-99-2026-10-29.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=1), encoding="utf-8")
    (AQUI / "REPORTE-TITO-99-2026-10-29.md").write_text(
        armar_informe(reporte), encoding="utf-8")
    print(f"evaluacion: elegida={seleccion['elegida']} "
          f"baseline_viejo={base['omisiones_oportunas']}/{base['legitimas_derivadas']} "
          f"elegido={eleg['omisiones_oportunas']}/{eleg['legitimas_derivadas']} "
          f"-> {fine_tuning['recomendacion_para_100'][:60]}...")
    return 0


def armar_informe(r: dict) -> str:
    eleg = next(x for x in r["resultados_validacion"] if x["config"] == r["seleccion"]["elegida"])
    lineas = [f"# Reporte #99 — frase y contexto con RoBERTuito congelado",
              f"",
              f"Fecha: {r['fecha']}. Encoder `{r['encoder']['id']}` "
              f"revision `{r['encoder']['revision'][:12]}` congelado. "
              f"Seed {r['semilla']}.",
              f"",
              f"## Auditoria semantica",
              f"",
              f"Familias del banco excluidas del ajuste: "
              f"{len(r['auditoria_semantica']['familias_relacionadas_excluidas'])}.",
              f"Conteo despues: {r['auditoria_semantica']['conteo_despues']}.",
              f"",
              f"## Entrenamiento",
              f"",
              f"{r['entrenamiento']['ejemplos']} ejemplos "
              f"({r['entrenamiento']['unos']} unos). "
              f"{r['entrenamiento']['clasificadores']} clasificadores, "
              f"{r['entrenamiento']['configuraciones']} configuraciones.",
              f"",
              f"## Seleccion (solo validacion)",
              f"",
              f"Elegida: `{r['seleccion']['elegida']}`. "
              f"Frontera: {r['seleccion']['frontera_pareto']}.",
              f"",
              f"| config | omisiones | legit_deriv | consultas_media |",
              f"|---|---|---|---|"]
    for x in r["resultados_validacion"]:
        lineas.append(f"| `{x['config']}` | {x['omisiones_oportunas']}/{x['denominador_vishing']} "
                      f"| {x['legitimas_derivadas']}/{x['denominador_legitimas']} "
                      f"| {x['consultas_media']} |")
    ft = r["criterio_fine_tuning"]
    lineas += [f"",
               f"## Criterio de fine-tuning (#100)",
               f"",
               f"Baseline viejo (frase, u=0.5): "
               f"{ft['baseline_viejo']['omisiones_oportunas']}/"
               f"{ft['baseline_viejo']['denominador_vishing']} omisiones, "
               f"{ft['baseline_viejo']['legitimas_derivadas']}/"
               f"{ft['baseline_viejo']['denominador_legitimas']} legitimas derivadas.",
               f"Elegido: {ft['elegido']['omisiones_oportunas']} omisiones, "
               f"{ft['elegido']['legitimas_derivadas']} legitimas derivadas.",
               f"{ft['recomendacion_para_100']}.",
               f"",
               f"## Limites",
               f""]
    lineas += [f"- {l}" for l in r["limites"]]
    return "\n".join(lineas) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
