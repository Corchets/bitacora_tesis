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
heuristicas ni marca supervision como ejecutada: el paso de supervision
verifica el artefacto contextual real
(`SUPERVISION-CONTEXTUAL-TITO-99-2026-10-29.jsonl`) y el entrenamiento
falla cerrado (fail-closed) sin inventar etiquetas si falta, esta
incompleto o no pasa la validacion (modelo/revision/hash por prefijo,
evidencia con lineas de soporte, segunda pasada sin futuro, cobertura
total, etiquetas solo 0/1/nulo). Los nulos quedan fuera de perdida y
metricas binarias y se conservan en cobertura. No se toca
`revision_humana` ni la puerta formal de `datos_tito.py`; la autorizacion
de desarrollo es explicita y esta separada de la puerta humana.

Auditoria semantica del otro worker
(`AUDITORIA-SEMANTICA-CONTEXTUAL-TITO-99-2026-10-29.json`, dueno: otro
worker): el entrenamiento la exige validada y enlazada (hashes, grupos,
banco, veinte) antes de entrenar. La auditoria lexica propia
(igualdad/subcadena/Jaccard) se conserva solo como cota auxiliar, sin
declararla semantica suficiente y sin sobrescribir el archivo semantico.

Criterio operativo de desarrollo para `oportuna`: derivacion <= `T_R`
(coherente con #98). Sin `T_R` el caso es no evaluable: se mantiene en
caso/denominador/cobertura aparte y se informan ambos margenes `T_R`/`T_C`
sin inventar cumplimiento. Criterio exploratorio vinculado a D08; no
cierra arquitectura ni margen final. Mismo criterio para candidato nuevo
y Tito viejo; no se decide con las veinte.

No lee la reserva (rechazo por identificador/particion). No decide con
las veinte de comparacion ni con el diagnostico: seleccion solo con
entrenamiento/validacion.

Sin autorizacion explicita del coordinador tras auditoria y etiquetas
reales no hay inferencia ni entrenamiento: los pasos `entrenar`/`evaluar`
fallan cerrado.

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

SUPERVISION_REAL_NOMBRE = "SUPERVISION-CONTEXTUAL-TITO-99-2026-10-29.jsonl"
AUDITORIA_SEMANTICA_REAL_NOMBRE = (
    "AUDITORIA-SEMANTICA-CONTEXTUAL-TITO-99-2026-10-29.json")
AUDITORIA_LEXICA_AUX_NOMBRE = "AUDITORIA-LEXICA-AUXILIAR-TITO-99-2026-10-29.json"
VALIDACION_RECIBO_NOMBRE = "VALIDACION-PROMPTS-SUPERVISION-TITO-99-2026-10-29.json"
MOTIVOS_SUPERVISION_VALIDOS = ("acuerdo", "desacuerdo", "respuesta_invalida")
GRUPOS_AUDITORIA_EXIGIDOS = ("entrenamiento", "validacion", "comparacion_20")

CRITERIO_OPORTUNA = (
    "Criterio operativo de desarrollo (exploratorio, vinculado a D08): "
    "derivacion <= T_R sobre referencias sin revision humana (#98). Sin T_R "
    "el caso es no evaluable y se informa aparte con ambos margenes T_R/T_C. "
    "No cierra arquitectura ni margen final.")


def _rutas_reales() -> tuple[Path, Path]:
    """Rutas del supervisor real sin editar su modulo.

    Si `supervision_tito_99.py` esta disponible se usan sus constantes
    (fuente del otro worker); si no, los nombres fijados arriba.
    """
    try:
        from supervision_tito_99 import (AUDITORIA_RUTA, SUPERVISION_RUTA)
        return Path(SUPERVISION_RUTA), Path(AUDITORIA_RUTA)
    except ImportError:
        return (AQUI / SUPERVISION_REAL_NOMBRE,
                AQUI / AUDITORIA_SEMANTICA_REAL_NOMBRE)

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

def _etiqueta_valida(etiqueta) -> bool:
    """Solo 0/1 enteros o nulo. Rechaza booleanos, cadenas y otros tipos."""
    if etiqueta is None:
        return True
    return isinstance(etiqueta, int) and not isinstance(etiqueta, bool) \
        and etiqueta in (0, 1)


def _firma_prompts_vigente() -> str:
    """Firma de prompts vigente (corrector, `prompts_supervision_tito_99`).

    Los registros con firma ausente o distinta (borrador viejo o prompts no
    validados) se rechazan: no se heredan como verdad ni habilitan ajuste.
    """
    from prompts_supervision_tito_99 import firma_prompts
    return firma_prompts()


def validar_recibo_controles(ruta: Path | None = None) -> dict:
    """Valida el recibo de controles sintéticos de los prompts vigentes.

    Rechaza (fail-closed) recibo ausente/ilegible, con firma distinta a la
    vigente, sin identidad del modelo o con controles no conformes: sin
    controles verdes no hay entrenamiento. Devuelve el resumen enlazado.
    """
    ruta = AQUI / VALIDACION_RECIBO_NOMBRE if ruta is None else Path(ruta)
    try:
        recibo = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(
            f"recibo de controles ausente o ilegible ({ruta.name}): "
            f"{type(e).__name__}; sin controles no hay entrenamiento.") from e
    if not isinstance(recibo, dict):
        raise ValueError("recibo de controles ilegible: no es objeto JSON.")
    if recibo.get("firma_prompts") != _firma_prompts_vigente():
        raise ValueError(
            "recibo de controles con firma distinta a la vigente: los "
            "controles validaron otros prompts; revalidar, no heredar.")
    modelo = recibo.get("modelo")
    if (not isinstance(modelo, dict) or not modelo.get("tag")
            or not modelo.get("digest")
            or modelo.get("digest") == "desconocido"
            or not modelo.get("ollama_version")):
        raise ValueError("recibo de controles sin identidad del modelo.")
    controles = recibo.get("controles")
    if not isinstance(controles, list) or not controles:
        raise ValueError("recibo de controles sin controles registrados.")
    no_conformes = [c.get("control", "?") for c in controles
                    if not isinstance(c, dict) or not c.get("conforme")]
    if no_conformes or recibo.get("conformidad") != recibo.get("total"):
        raise ValueError(
            "recibo de controles no conforme "
            f"(desvios: {no_conformes[:5]}); gate cerrado, sin entrenamiento.")
    return {"firma": recibo["firma_prompts"],
            "modelo": modelo["tag"], "digest": modelo["digest"],
            "ollama_version": modelo["ollama_version"],
            "conformidad": recibo["conformidad"], "total": recibo["total"]}


def validar_registros_supervision(registros: list[dict], textos: dict,
                                  particion_de: dict[str, str]) -> dict:
    """Valida el artefacto contextual real prefijo por prefijo.

    Rechaza (fail-closed) firma ausente o distinta a la vigente, ademas de
    heuristico/manipulado/futuro: hash del prefijo visible, etiqueta fuera
    de 0/1/nulo, evidencia sin lineas de soporte en rango, motivo invalido
    o incoherente con la etiqueta, pasada sin prompt con las lineas
    visibles o con sufijo futuro, modelo sin identidad (tag/digest/opciones
    deterministas) y cobertura distinta de la esperada (todos los prefijos
    de entrenamiento/validacion, exactamente una vez, con ambas clases en
    entrenamiento).
    """
    firma_vigente = _firma_prompts_vigente()
    esperados = {(cid, k) for cid, lineas in textos.items()
                 for k in range(1, len(lineas) + 1)}
    vistos: set[tuple[str, int]] = set()
    for r in registros:
        cid, k = r.get("case_id"), r.get("hasta_linea")
        if r.get("firma_prompts") != firma_vigente:
            raise ValueError(
                f"{cid}#{k}: firma_prompts ausente o distinta a la vigente "
                "(borrador viejo o prompts no validados); reanotar con los "
                "prompts vigentes, no heredar.")
        if (cid, k) in vistos:
            raise ValueError(f"supervision duplicada: {(cid, k)}.")
        if cid not in textos or not isinstance(k, int) or (cid, k) not in esperados:
            raise ValueError(f"supervision fuera de cobertura: {(cid, k)}.")
        vistos.add((cid, k))
        visibles = textos[cid][:k]
        if r.get("particion") != particion_de[cid]:
            raise ValueError(f"{cid}#{k}: particion inconsistente.")
        if r.get("texto_hash") != sha("\n".join(visibles).encode("utf-8")):
            raise ValueError(f"{cid}#{k}: texto_hash no coincide con el "
                             "prefijo visible (posible futuro/manipulacion).")
        if not _etiqueta_valida(r.get("etiqueta")):
            raise ValueError(f"{cid}#{k}: etiqueta invalida "
                             f"{r.get('etiqueta')!r}; solo 0/1/nulo.")
        motivo = r.get("motivo")
        if motivo not in MOTIVOS_SUPERVISION_VALIDOS:
            raise ValueError(f"{cid}#{k}: motivo invalido {motivo!r}.")
        if (motivo == "acuerdo") != (r.get("etiqueta") is not None):
            raise ValueError(f"{cid}#{k}: motivo/etiqueta incoherentes "
                             f"({motivo}, {r.get('etiqueta')!r}).")
        soporte = r.get("lineas_soporte")
        if not isinstance(soporte, list) or not all(
                isinstance(n, int) and 1 <= n <= k for n in soporte):
            raise ValueError(f"{cid}#{k}: lineas_soporte fuera de 1..{k}.")
        if r.get("etiqueta") is not None and not soporte:
            raise ValueError(f"{cid}#{k}: etiqueta decidida sin soporte.")
        if not isinstance(r.get("fundamento"), str) or not r["fundamento"].strip():
            raise ValueError(f"{cid}#{k}: sin fundamento textual.")
        for pasada in ("pasada1", "pasada2"):
            p = r.get(pasada)
            if not isinstance(p, dict) or not isinstance(p.get("prompt"), str):
                raise ValueError(f"{cid}#{k}: {pasada} sin prompt registrado.")
            for linea in visibles:
                if linea not in p["prompt"]:
                    raise ValueError(f"{cid}#{k}: {pasada} no ve una linea "
                                     "visible.")
            for futura in textos[cid][k:]:
                if len(futura.strip()) >= 8 and futura in p["prompt"]:
                    raise ValueError(f"{cid}#{k}: {pasada} con sufijo futuro.")
        meta = r.get("modelo")
        if not isinstance(meta, dict) or not meta.get("tag") \
                or not meta.get("digest") or meta.get("digest") == "desconocido":
            raise ValueError(f"{cid}#{k}: modelo sin identidad auditable.")
        opciones = meta.get("opciones", {})
        if opciones.get("temperature") != 0 or opciones.get("seed") != SEMILLA:
            raise ValueError(f"{cid}#{k}: opciones del modelo no "
                             "deterministas (temperature 0, seed 42).")
    faltantes = sorted(esperados - vistos)
    if faltantes:
        raise ValueError(f"supervision incompleta: {len(faltantes)} prefijos "
                         f"sin revisar (p. ej. {faltantes[:3]}).")
    clases_train = {r["etiqueta"] for r in registros
                    if particion_de[r["case_id"]] == "entrenamiento"}
    if 0 not in clases_train or 1 not in clases_train:
        raise ValueError("supervision sin ambas clases (0/1) en entrenamiento.")
    cobertura: dict[str, int] = {}
    for r in registros:
        et = "nulo" if r["etiqueta"] is None else r["etiqueta"]
        cobertura[f"{r['particion']}/{et}"] = \
            cobertura.get(f"{r['particion']}/{et}", 0) + 1
    modelos = sorted({r["modelo"]["tag"] for r in registros})
    return {"por_particion_etiqueta": cobertura,
            "prefijos": len(registros),
            "nulos": sum(1 for r in registros if r["etiqueta"] is None),
            "modelos": modelos,
            "digests": sorted({r["modelo"]["digest"] for r in registros})}


def leer_supervision_real() -> list[dict]:
    """Lee el JSONL del supervisor real. Falla cerrado si falta o es invalido."""
    ruta, _ = _rutas_reales()
    if not ruta.exists():
        raise SystemExit(
            f"supervision fail-closed: falta {ruta.name}; el supervisor real "
            "(`supervision_tito_99.py`, otro worker) aun no lo materializo. "
            "No se inventan etiquetas ni se marca ejecutado.")
    try:
        return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines()
                if l.strip()]
    except (OSError, ValueError) as e:
        raise SystemExit(f"supervision fail-closed: {ruta.name} ilegible "
                         f"({type(e).__name__}).") from e


def construir_supervision(textos: dict, particion_de: dict[str, str]) -> tuple[list[dict], dict]:
    """Contrato `construir_supervision(textos, particion_de)` (otro worker).

    Este modulo no genera etiquetas: exige el recibo de controles sinteticos
    de los prompts vigentes y carga el artefacto contextual real del
    supervisor y lo valida (firma vigente, modelo/revision/hash por prefijo,
    evidencia y segunda pasada sin futuro, cobertura total, 0/1/nulo). Si el
    recibo falta, no coincide o no esta conforme, o si el artefacto no
    valida, falla cerrado (fail-closed): no inventa etiquetas ni marca
    supervision como ejecutada.
    """
    try:
        import supervision_tito_99  # noqa: F401 (dueno: otro worker)
    except ImportError as e:
        raise SystemExit(
            "supervision fail-closed: `supervision_tito_99.py` no disponible "
            f"({type(e).__name__}); el supervisor real es del otro worker. "
            "No se inventan etiquetas ni se marca ejecutado.") from e
    try:
        recibo = validar_recibo_controles()
    except ValueError as e:
        raise SystemExit(f"supervision fail-closed: {e}") from e
    registros = leer_supervision_real()
    try:
        cobertura = validar_registros_supervision(registros, textos, particion_de)
    except ValueError as e:
        raise SystemExit(f"supervision fail-closed: {e}") from e
    cobertura["recibo_controles"] = recibo
    return registros, cobertura


def validar_auditoria_semantica(aud: dict, particiones: dict) -> dict:
    """Valida la auditoria semantica del otro worker antes de entrenar.

    Rechaza parcial/antigua/no enlazada: exige lista de exclusiones, umbral
    calibrado con metodo, los grupos con las veinte, conteo del banco igual
    al de particiones y semilla 42. Devuelve el resumen enlazado.
    """
    if not isinstance(aud, dict):
        raise ValueError("auditoria semantica ilegible.")
    excluidas = aud.get("familias_excluidas_ajuste")
    if not isinstance(excluidas, list) or not all(isinstance(f, str) for f in excluidas):
        raise ValueError("auditoria sin lista de exclusiones registrada.")
    umbral = aud.get("umbral_usado")
    if not isinstance(umbral, (int, float)) or not 0 < float(umbral) <= 1:
        raise ValueError("auditoria sin umbral calibrado en (0, 1].")
    grupos = aud.get("grupos", [])
    if any(g not in grupos for g in GRUPOS_AUDITORIA_EXIGIDOS):
        raise ValueError("auditoria parcial: grupos "
                         f"{GRUPOS_AUDITORIA_EXIGIDOS} no cubiertos ({grupos}).")
    if aud.get("frases_auditadas") != len(particiones.get("banco", [])):
        raise ValueError("auditoria no enlazada al banco de particiones "
                         f"({aud.get('frases_auditadas')} vs "
                         f"{len(particiones.get('banco', []))}).")
    calib = aud.get("calibracion", {})
    if "umbral" not in calib or "metodo" not in calib:
        raise ValueError("auditoria sin calibracion de umbral registrada.")
    if aud.get("semilla") != SEMILLA:
        raise ValueError("auditoria con semilla inesperada.")
    advertencias = []
    if calib.get("metodo", "").startswith("reserva:"):
        advertencias.append("calibracion sin pares declarados; umbral de reserva.")
    return {"excluidas": sorted(excluidas), "umbral": float(umbral),
            "metodo_calibracion": calib.get("metodo"),
            "pares_declarados": calib.get("pares_declarados"),
            "grupos": list(grupos), "advertencias": advertencias}


def leer_auditoria_semantica(particiones: dict) -> tuple[dict, dict]:
    """Lee y valida la auditoria semantica real. Falla cerrado si no valida."""
    _, ruta = _rutas_reales()
    if not ruta.exists():
        raise SystemExit(
            f"auditoria fail-closed: falta {ruta.name}; la auditoria semantica "
            "completa es del otro worker (`supervision_tito_99.py --paso "
            "auditoria`). La cota lexica propia no la sustituye.")
    try:
        aud = json.loads(ruta.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise SystemExit(f"auditoria fail-closed: {ruta.name} ilegible "
                         f"({type(e).__name__}).") from e
    try:
        resumen = validar_auditoria_semantica(aud, particiones)
    except ValueError as e:
        raise SystemExit(f"auditoria fail-closed: {e}") from e
    return aud, resumen


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

    Criterio operativo de desarrollo (`oportuna`): derivacion <= `T_R`
    (coherente con #98), fijado ANTES de medir. Sin `T_R` el caso es no
    evaluable (`oportuna` None): se mantiene en caso/denominador/cobertura
    aparte (`vishing_no_evaluable_sin_TR`) y se informan ambos margenes
    `T_R`/`T_C` disponibles sin inventar cumplimiento. Criterio
    exploratorio vinculado a D08; no cierra arquitectura ni margen final.
    Mismo criterio para candidato nuevo y Tito viejo.

    Conserva posiciones: los puntajes `None` (fallos de inferencia) no se
    filtran antes de la primera derivacion; la derivacion es el primer `k`
    con puntaje no nulo >= umbral. Los fallos se cuentan y diagnostican
    (fail-open: no derivan por si mismos).
    """
    por_caso, omisiones, legit_derivadas, no_evaluables = [], 0, 0, 0
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
        margen_tr = (der is not None and der <= t_r) \
            if (der is not None and t_r is not None) else None
        margen_tc = (der is not None and der <= t_c) \
            if (der is not None and t_c is not None) else None
        if clase == "vishing":
            if t_r is None:
                a_tiempo = None
                no_evaluables += 1
                posicion = "sin_T_R_no_evaluable"
            else:
                a_tiempo = margen_tr
                if not a_tiempo:
                    omisiones += 1
                posicion = ("sin_derivacion" if der is None
                            else "antes_de_T_R" if der < t_r
                            else "en_T_R" if der == t_r
                            else "tras_T_R")
        else:
            a_tiempo = None
            posicion = "sin_derivacion" if der is None else "derivada"
            if der is not None:
                legit_derivadas += 1
        por_caso.append({"case_id": cid, "clase": clase, "n_lineas": n,
                         "t_r": t_r, "t_c": t_c, "derivacion": der,
                         "oportuna": a_tiempo, "margen_TR": margen_tr,
                         "margen_TC": margen_tc,
                         "evaluable_TR": (clase != "vishing" or t_r is not None),
                         "posicion": posicion,
                         "consultas": der if der is not None else n,
                         "fallos": fallos, "errores": errores,
                         "puntajes": [(None if p is None else round(p, 4))
                                      for p in puntajes]})
    consultas = [c["consultas"] for c in por_caso]
    return {"umbral": umbral, "omisiones_oportunas": omisiones,
            "legitimas_derivadas": legit_derivadas,
            "denominador_vishing": sum(1 for c in por_caso if c["clase"] == "vishing"),
            "denominador_legitimas": sum(1 for c in por_caso if c["clase"] != "vishing"),
            "vishing_no_evaluable_sin_TR": no_evaluables,
            "criterio_oportuna": CRITERIO_OPORTUNA,
            "prefijos_con_fallo": total_fallos,
            "consultas_media": round(sum(consultas) / len(consultas), 2),
            "por_caso": por_caso}


def metricas_prefijos_revisados(puntajes_por_caso: dict[str, list[float | None]],
                                etiqueta_de: dict, umbral: float) -> dict:
    """Clasificacion por prefijo SOLO sobre prefijos revisados (0/1).

    Los inciertos (nulo) y los sin registro quedan fuera de las metricas
    binarias y se conservan en cobertura. No se informa F1 exhaustivo: si no
    hay prefijos revisados, las metricas son None con motivo.
    """
    tp = fp = tn = fn = revisados = inciertos = sin_registro = fallos = 0
    for cid, puntajes in puntajes_por_caso.items():
        for k, p in enumerate(puntajes, start=1):
            et = etiqueta_de.get((cid, k), "sin_registro")
            if et == "sin_registro":
                sin_registro += 1
                continue
            if et not in (0, 1, None) or isinstance(et, bool):
                raise ValueError(f"{cid}#{k}: etiqueta invalida {et!r}.")
            if et is None:
                inciertos += 1
                continue
            if p is None:
                fallos += 1
                continue
            revisados += 1
            pred = 1 if p >= umbral else 0
            if pred == 1 and et == 1:
                tp += 1
            elif pred == 1:
                fp += 1
            elif et == 1:
                fn += 1
            else:
                tn += 1
    if revisados == 0:
        return {"umbral": umbral, "revisados": 0, "inciertos_null": inciertos,
                "sin_registro": sin_registro, "prefijos_con_fallo": fallos,
                "tp": 0, "fp": 0, "tn": 0, "fn": 0,
                "exactitud": None, "precision": None, "recall": None,
                "f1": None,
                "motivo": "sin prefijos revisados; no se inventa F1."}
    exactitud = (tp + tn) / revisados
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    f1 = (2 * precision * recall / (precision + recall)) \
        if precision and recall and (precision + recall) else None
    return {"umbral": umbral, "revisados": revisados,
            "inciertos_null": inciertos, "sin_registro": sin_registro,
            "prefijos_con_fallo": fallos,
            "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "exactitud": round(exactitud, 4),
            "precision": None if precision is None else round(precision, 4),
            "recall": None if recall is None else round(recall, 4),
            "f1": None if f1 is None else round(f1, 4),
            "nota": ("F1 solo sobre prefijos revisados (0/1); inciertos y sin "
                     "registro en cobertura, fuera de metricas.")}


def _frontera(configs: list[dict], costo_de) -> list[str]:
    """Configs no dominadas en (omisiones, legitimas, costo)."""
    frente = []
    for r in configs:
        cr = costo_de(r)
        dominado = any(
            o["omisiones_oportunas"] <= r["omisiones_oportunas"]
            and o["legitimas_derivadas"] <= r["legitimas_derivadas"]
            and costo_de(o) <= cr
            and (o["omisiones_oportunas"] < r["omisiones_oportunas"]
                 or o["legitimas_derivadas"] < r["legitimas_derivadas"]
                 or costo_de(o) < cr)
            for o in configs if o is not r)
        if not dominado:
            frente.append(r["config"])
    return sorted(frente)


def seleccionar_candidatos(resultados: list[dict], costos_p95: dict) -> dict:
    """Frontera de Pareto sobre HISTORIAL + desempates de la configuracion.

    La seleccion usa la frontera de `historial_acumulado` con costo p95
    real; el principal DEBE usar historial (sin sustitucion por frase).
    El control `frase_actual_control` y la frontera global (con
    `consultas_media`, informativa) se conservan para interpretar, sin
    permitir sustitucion. Desempates exactos de la configuracion: menor
    suma de errores, menor costo p95, C cercano a 1, umbral cercano a 0.5.
    Solo validacion.
    """
    for r in resultados:
        if r["config"] not in costos_p95:
            raise ValueError(f"sin costo p95 real para {r['config']}.")
    hist = [r for r in resultados if r["entrada"] == "historial_acumulado"]
    frase = [r for r in resultados if r["entrada"] == "frase_actual_control"]
    if not hist:
        raise ValueError("sin candidatos de historial; el principal debe "
                         "usar historial.")
    frente_hist = _frontera(hist, lambda r: costos_p95[r["config"]])
    cands = [r for r in hist if r["config"] in frente_hist]
    cands.sort(key=lambda r: (r["omisiones_oportunas"] + r["legitimas_derivadas"],
                              costos_p95[r["config"]],
                              abs(r["C"] - 1.0), abs(r["umbral"] - 0.5)))
    elegida = cands[0]
    frente_global = _frontera(resultados, lambda r: r["consultas_media"])
    return {"frontera_pareto": frente_hist,
            "frontera_historial": frente_hist,
            "frontera_global_informativa": frente_global,
            "controles_frase": sorted(r["config"] for r in frase),
            "orden": [r["config"] for r in cands],
            "elegida": elegida["config"],
            "criterio": ("Pareto sobre HISTORIAL en omisiones oportunas, "
                         "legitimas derivadas y costo p95 real sobre "
                         "validacion conversacional; desempate por menor suma, "
                         "menor costo p95, C cercano a 1 y umbral cercano a "
                         "0.5. Principal con historial, sin sustitucion por "
                         "frase. Frontera global con consultas_media solo "
                         "informativa.")}


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

    # Paso 1: cota lexica propia (auxiliar) + auditoria semantica real.
    # Este paso NUNCA sobrescribe el archivo semantico del otro worker.
    lexica = None
    if args.paso in ("auditoria", "todo"):
        lexica = auditar_relaciones(banco, textos, particion_de)
        (AQUI / AUDITORIA_LEXICA_AUX_NOMBRE).write_text(
            json.dumps({"fecha": "2026-10-29", "semilla": SEMILLA,
                        "nota": ("Cota lexica auxiliar (igualdad/subcadena/"
                                 "Jaccard); no es evidencia semantica "
                                 "suficiente ni sustituye la auditoria del "
                                 "otro worker."),
                        "cota_lexica": lexica, "codigo": codigo},
                       ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"cota lexica auxiliar: "
              f"{len(lexica['familias_relacionadas_excluidas'])} familias con "
              f"coincidencia literal; no sustituye la semantica.")
    try:
        auditoria_sem, resumen_aud = leer_auditoria_semantica(particiones)
        _, ruta_aud = _rutas_reales()
    except SystemExit as e:
        print(e)
        return 2
    excluidas = set(resumen_aud["excluidas"])
    banco_ajuste = [f for f in banco if f["familia"] not in excluidas]
    print(f"auditoria semantica: umbral={resumen_aud['umbral']} "
          f"metodo={resumen_aud['metodo_calibracion']} "
          f"excluidas={len(excluidas)}")
    for adv in resumen_aud["advertencias"]:
        print(f"auditoria semantica, advertencia: {adv}")
    clases_ajuste = {f["clase_autoral"] for f in banco_ajuste}
    if len(clases_ajuste) < 2:
        print("auditoria: FALTA UNA CLASE tras exclusiones semanticas; "
              "se requiere material sintetico trazable antes de entrenar "
              "(sin reserva, sin sustituir las veinte).")
        return 2

    if args.paso in ("supervision", "todo"):
        # Este paso NO genera etiquetas ni escribe artefactos: verifica el
        # artefacto contextual real del supervisor (fail-closed).
        try:
            registros, cobertura = construir_supervision(textos, particion_de)
        except SystemExit as e:
            print(e)
            return 3
        print(f"supervision validada: {cobertura}")

    if args.paso not in ("entrenar", "evaluar", "todo"):
        return 0

    import sklearn, tokenizers, transformers  # noqa: F401
    import torch

    if args.paso in ("entrenar", "todo"):
        # Entrena SOLO con el artefacto contextual validado (fail-closed).
        # La validacion ocurre ANTES de cargar el encoder: sin etiquetas
        # reales no hay inferencia ni entrenamiento.
        try:
            sup, cobertura_sup = construir_supervision(textos, particion_de)
        except SystemExit as e:
            print(e)
            return 3
        ruta_sup, _ = _rutas_reales()
        librerias = {"torch": torch.__version__,
                     "transformers": transformers.__version__,
                     "scikit-learn": sklearn.__version__,
                     "tokenizers": tokenizers.__version__,
                     "numpy": __import__("numpy").__version__}
        tokenizer, modelo, torch_mod, tok_sha = _cargar_tokenizer_modelo()
        dispositivo = "cpu"
        etiqueta_de = {(r["case_id"], r["hasta_linea"]): r["etiqueta"] for r in sup}
        identidad_supervision = {
            "artefacto": ruta_sup.name,
            "sha256": sha(ruta_sup.read_bytes()),
            "cobertura": cobertura_sup,
            "modelos": cobertura_sup["modelos"],
            "digests": cobertura_sup["digests"],
        }
        identidad_auditoria = {
            "artefacto": ruta_aud.name,
            "sha256": sha(ruta_aud.read_bytes()),
            "umbral": resumen_aud["umbral"],
            "metodo_calibracion": resumen_aud["metodo_calibracion"],
            "familias_excluidas": resumen_aud["excluidas"],
        }

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
                    "supervision_identidad": identidad_supervision,
                    "auditoria_identidad": identidad_auditoria,
                    "particiones_sha256": sha((AQUI / CONFIG["particiones"])
                                              .read_bytes()),
                    "configuracion_sha256": sha((AQUI / "CONFIGURACION-TITO-2026-10-29.json")
                                                .read_bytes()),
                    "semilla": SEMILLA,
                    "autorizacion": AUTORIZACION_DESARROLLO,
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
    puntajes_guardados, vectores_guardados = {}, {}
    n_cfgs = 0
    for e in ENTRADAS:
        cids, Ns, V = X_val[e]
        for C in VALORES_C:
            coef, b = recargados[(e, C)]
            punt = puntajes_matriz(V, coef, b)
            vectores_guardados[(e, C)] = V
            # Verificacion de recarga realmente inferida: puntaje
            # independiente (suma exacta) sobre los primeros prefijos, sin
            # ajuste. Cualquier diferencia aborta la evaluacion.
            for v, p in zip(V[:5], punt[:5]):
                z_suma = sum(c * x for c, x in zip(coef, v)) + b
                z_exacta = math.fsum(c * x for c, x in zip(coef, v)) + b
                if abs(z_suma - z_exacta) > 1e-9 or abs(sigmoide(z_exacta) - p) > 1e-9:
                    raise ValueError("verificacion de recarga: puntaje no "
                                     "reproduce el artefacto recargado.")
            por_caso_punt, i = {}, 0
            for cid, n in zip(cids, Ns):
                por_caso_punt[cid] = punt[i:i + n]
                i += n
            puntajes_guardados[(e, C)] = por_caso_punt
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
    # Clasificacion por prefijo SOLO sobre prefijos revisados (0/1) con las
    # etiquetas validadas; inciertos fuera de metricas y en cobertura.
    try:
        _sup_val, _ = construir_supervision(textos, particion_de)
    except SystemExit as e:
        print(e)
        return 3
    etiqueta_val = {(r["case_id"], r["hasta_linea"]): r["etiqueta"]
                    for r in _sup_val if particion_de[r["case_id"]] == "validacion"}
    _eleg_e, _eleg_C = eleg["entrada"], eleg["C"]
    clasif_elegida = metricas_prefijos_revisados(
        puntajes_guardados[(_eleg_e, _eleg_C)], etiqueta_val, eleg["umbral"])
    verificacion_recarga = {
        "metodo": ("artefactos recargados desde disco y puntaje lineal+sigmoide "
                   "reverificado con suma independiente en los primeros 5 "
                   "prefijos de cada configuracion; sin ajuste en evaluar"),
        "configuraciones_reverificadas": n_cfgs,
        "ajuste_en_evaluar": False,
    }
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
    _ruta_sup_rep, _ruta_aud_rep = _rutas_reales()
    reporte = {"fecha": "2026-10-29", "issue": 99, "semilla": SEMILLA,
               "encoder": {"id": ENCODER_ID, "revision": ENCODER_REVISION,
                           "congelado": True, "tokenizer_sha256": tok_sha},
               "auditoria_semantica": auditoria_sem,
               "auditoria_semantica_resumen": resumen_aud,
               "cota_lexica_auxiliar": lexica,
               "supervision_identidad": {
                   "artefacto": _ruta_sup_rep.name,
                   "sha256": sha(_ruta_sup_rep.read_bytes()),
                   "modelos": sorted({r["modelo"]["tag"] for r in _sup_val}),
                   "autorizacion": AUTORIZACION_DESARROLLO},
               "criterio_oportuna": CRITERIO_OPORTUNA,
               "clasificacion_prefijos_revisados_elegida": clasif_elegida,
               "verificacion_recarga": verificacion_recarga,
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
                           "Criterio oportuna operativo exploratorio (D08); "
                           "sin T_R no evaluable, con ambos margenes.",
                           "F1 solo sobre prefijos revisados; inciertos en cobertura.",
                           "Cota lexica auxiliar; no es evidencia semantica suficiente.",
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
    resumen_aud = r.get("auditoria_semantica_resumen", {})
    sup_id = r.get("supervision_identidad", {})
    clasif = r.get("clasificacion_prefijos_revisados_elegida", {})
    verif = r.get("verificacion_recarga", {})
    lineas = [f"# Reporte #99 — frase y contexto con RoBERTuito congelado",
              f"",
              f"Fecha: {r['fecha']}. Encoder `{r['encoder']['id']}` "
              f"revision `{r['encoder']['revision'][:12]}` congelado. "
              f"Seed {r['semilla']}.",
              f"",
              f"## Auditoria semantica (otro worker)",
              f"",
              f"Artefacto validado con umbral {resumen_aud.get('umbral')} "
              f"({resumen_aud.get('metodo_calibracion')}). "
              f"Familias excluidas del ajuste: {len(resumen_aud.get('excluidas', []))}.",
              f"Supervision: `{sup_id.get('artefacto')}` modelos "
              f"{sup_id.get('modelos')}.",
              f"Cota lexica propia solo auxiliar, sin valor semantico.",
              f"",
              f"## Criterio operativo de oportunidad",
              f"",
              f"{r.get('criterio_oportuna', '')}",
              f"",
              f"## Entrenamiento",
              f"",
              f"{r['entrenamiento']['ejemplos']} ejemplos "
              f"({r['entrenamiento']['unos']} unos). "
              f"{r['entrenamiento']['clasificadores']} clasificadores, "
              f"{r['entrenamiento']['configuraciones']} configuraciones.",
              f"",
              f"## Clasificacion por prefijo (elegida, solo revisados)",
              f"",
              f"Revisados: {clasif.get('revisados')}, inciertos: "
              f"{clasif.get('inciertos_null')}, sin registro: "
              f"{clasif.get('sin_registro')}. F1 (solo revisados): "
              f"{clasif.get('f1')}.",
              f"Recarga verificada sin ajuste: {verif.get('metodo', '')}.",
              f"",
              f"## Seleccion (solo validacion)",
              f"",
              f"Elegida: `{r['seleccion']['elegida']}`. "
              f"Frontera historial: {r['seleccion']['frontera_pareto']}. "
              f"Controles frase: {r['seleccion'].get('controles_frase')}.",
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
