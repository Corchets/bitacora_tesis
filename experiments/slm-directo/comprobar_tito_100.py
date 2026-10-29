"""Comprobación del candidato congelado de Tito (#100, sin pesos nuevos).

Lee los resultados reales de #99 (`REPORTE-TITO-99-2026-10-29.json`),
aplica la regla condicional exacta de `CONFIGURACION-TITO-2026-10-29.json`
(fine-tuning SOLO si NINGUN candidato congelado conserva o reduce a la vez
omisiones oportunas y legítimas derivadas frente al viejo en validación Y
hay un error observable que lo justifique; el empate en ambos NO fuerza FT)
y, si no corresponde, congela el candidato/umbral/entrada elegidos SOLO con
validación en `CANDIDATO-TITO-100-2026-10-29.json` para comprobarlos después
sobre las veinte de comparación.

Si corresponde FT pero la rama afinada no está implementada, el
congelamiento queda BLOQUEADO explícito con el trabajo faltante: no se
finge skip, ni fine-tuning, ni se mide un candidato sin resolver.

La comprobación usa las APIs existentes (`entrenar_tito_99`,
`matriz_101.resolver_tito_nuevo`, `datos_tito`, `casos`): viejo histórico
inmutable (frase aislada, umbral 0,5) y nuevo recargado sin entrenar
(`Tito99`, historial acumulado A/B hasta cada línea, sin futuro). Recorre
cada conversación prefijo a prefijo con la MISMA construcción de entrada
de entrenamiento, trazas/costos/preparación separados y márgenes T_R/T_C.
Sin T_R el caso es no evaluable en oportunidad pero conserva
denominadores; la clasificación binaria cubre SOLO prefijos revisados
(0/1), nunca F1 exhaustivo de las veinte sin etiquetas.

Etapas (CLI): `congelar` / `evaluar` / `regenerar`. `congelar` NUNCA abre
las veinte de comparación (decide y congela SOLO con validación);
`evaluar` exige manifiesto congelado previo y comprueba EXACTAMENTE las
veinte aprobadas (`evaluacion_ids` de PARTICIONES, orden de #101), sin
abrir validación, entrenamiento, diagnóstico ni reserva. La rama afinada
(`tito-100-*`) queda pendiente: sin loader acordado con el integrador #99
no se carga como Tito99.

Secuencia posterior (puerta de ejecución, no de este dispatch): congelar
#100 desde validación -> seleccionar/congelar política #102 SOLO con
validación -> comprobar #100 sobre las veinte -> 600 recorridos de #101
-> 400 de #102. Las veinte nunca se usan para elegir candidato ni
política. `evaluar` acepta un `--politica-manifiesto` opcional para
exigir esa puerta cuando ya exista.

No inventa decisiones ni cierra D07/D08/D09. La revisión de referencia
sigue sin ser humana (`revision_humana: false`): es exploratoria de
desarrollo con autorización explícita separada de la puerta formal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from datos_tito import es_identificador_reserva, rechazar_reserva

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]

CONFIG_NOMBRE = "CONFIGURACION-TITO-2026-10-29.json"
PARTICIONES_NOMBRE = "PARTICIONES-TITO-2026-10-29.json"
MANIFIESTO_CONGELADO_NOMBRE = "CANDIDATO-TITO-100-2026-10-29.json"
DIR_CASOS_TEXTO = AQUI / "casos" / "texto"
DIR_CASOS_REFERENCIA = AQUI / "casos" / "referencia"

SEMILLA = 42
ENTRADA_NUEVA = "historial_acumulado"
ENTRADA_VIEJA = "frase_actual_aislada"
UMBRAL_VIEJO = 0.5
N_CONFIGS_MAX = 18
N_COMPARACION_20 = 20

# Presupuesto máximo de la preparación delegada (CONFIG §fine_tuning_100).
# Solo documenta el techo para el dispatch que implemente el ajuste.
FT_LRS = (1e-5, 2e-5)
FT_EPOCHS_MAX = 3
FT_BATCH = 4
FT_ACUMULACION = 4
FT_MAX_AJUSTES = 2
FT_HORAS_MAX = 2

AUTORIZACION_DESARROLLO = (
    "autorizacion_desarrollo_100: comprobacion de desarrollo sobre "
    "referencias sin revision humana (revision_humana=false), separada de "
    "la puerta formal humana de datos_tito.py. NO es revision_humana; no "
    "habilita uso ni cierra D07/D08/D09."
)

ESTADO_CONGELADO = "congelado_antes_de_comprobar"
ESTADO_BLOQUEADO_FT = "bloqueado_falta_rama_afinada"

RC_USO = 2
RC_BLOQUEADO_FT = 3


class BloqueoFineTuning(Exception):
    """FT corresponde pero la rama afinada no existe: bloquear, no fingir."""


# ---------------------------------------------------------------------------
# Huellas e identidad
# ---------------------------------------------------------------------------

def sha_bytes(crudo: bytes) -> str:
    return hashlib.sha256(crudo).hexdigest()


def sha_archivo(ruta: Path) -> str:
    return sha_bytes(Path(ruta).read_bytes())


def _es_hex64(valor: object) -> bool:
    return (isinstance(valor, str) and len(valor) == 64
            and all(c in "0123456789abcdef" for c in valor.lower()))


def info_codigo() -> dict:
    def git(*args: str) -> str:
        try:
            r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True,
                               text=True, timeout=10, check=True)
            return r.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return "desconocido"
    return {"commit": git("rev-parse", "HEAD"),
            "script_sha256": sha_archivo(Path(__file__))}


def info_runtime() -> dict:
    return {"python": sys.version.split()[0],
            "plataforma": platform.platform(),
            "semilla": SEMILLA}


def cargar_config() -> dict:
    return json.loads((AQUI / CONFIG_NOMBRE).read_text(encoding="utf-8"))


def cargar_particiones() -> dict:
    particiones = json.loads((AQUI / PARTICIONES_NOMBRE).read_text(encoding="utf-8"))
    if particiones.get("semilla") != SEMILLA:
        raise ValueError("particiones con semilla inesperada.")
    return particiones


def grupos_por_particion(particiones: dict, clave: str) -> dict[str, list[str]]:
    """case_id por particion_preparacion (helper de validación, decisión #99)."""
    grupos: dict[str, list[str]] = {}
    for c in particiones.get("conversaciones", []):
        grupos.setdefault(c.get("particion_preparacion", "?"), []).append(c["case_id"])
    if clave not in grupos:
        raise ValueError(f"partición {clave!r} sin conversaciones.")
    return grupos


def ids_validacion_conversaciones(particiones: dict) -> list[str]:
    """IDs de validación en orden (helper val: solo para la decisión #99)."""
    grupos = grupos_por_particion(particiones, "validacion")
    ids = sorted(grupos["validacion"])
    rechazar_reserva(ids)
    vistos = {c.get("case_id") for c in particiones.get("conversaciones", [])
              if c.get("particion_preparacion") == "validacion"}
    if set(ids) != vistos:
        raise ValueError("validación inconsistente en particiones.")
    return ids


# ---------------------------------------------------------------------------
# Regla condicional exacta de CONFIG §fine_tuning_100
# ---------------------------------------------------------------------------

def decidir_fine_tuning(candidatos: list[dict], baseline_viejo: dict,
                        errores_observables: list[str]) -> dict:
    """¿Corresponde fine-tuning? Regla literal de la configuración.

    `candidatos`: TODOS los resultados congelados de validación con claves
    `config`, `omisiones_oportunas`, `legitimas_derivadas`.
    `baseline_viejo`: mismo par de conteos del Tito viejo en validación.
    `errores_observables`: errores visibles que justificarían ajustar
    (vacío => no hay qué justificar).

    FT solo si NINGUN candidato conserva o reduce A LA VEZ ambos conteos
    frente al viejo Y hay al menos un error observable. Igualar ambos
    conteos NO obliga a FT (conservar == no ajustar). Sin candidatos no
    hay decisión válida: se falla cerrado en vez de informar no-FT.
    """
    if not candidatos:
        raise ValueError("sin candidatos congelados de validación: no se "
                         "decide fine-tuning sin evidencia.")
    for c in candidatos:
        for k in ("config", "omisiones_oportunas", "legitimas_derivadas"):
            if k not in c:
                raise ValueError(f"candidato sin {k!r}: {c!r}.")
    base_om = baseline_viejo["omisiones_oportunas"]
    base_leg = baseline_viejo["legitimas_derivadas"]
    conserva = [c["config"] for c in candidatos
                if c["omisiones_oportunas"] <= base_om
                and c["legitimas_derivadas"] <= base_leg]
    if conserva:
        return {"corresponde": False,
                "motivo": ("al menos un candidato congelado conserva o reduce "
                           "a la vez ambas métricas frente al viejo en "
                           f"validación: {conserva}."),
                "conservan": conserva,
                "baseline_viejo": dict(baseline_viejo)}
    if not [e for e in errores_observables if str(e).strip()]:
        return {"corresponde": False,
                "motivo": ("ningún candidato conserva ambas métricas, pero no "
                           "hay error observable que justifique ajustar: sin "
                           "FT especulativo."),
                "conservan": [],
                "baseline_viejo": dict(baseline_viejo)}
    raise BloqueoFineTuning(
        "FT correspondería (ningún congelado conserva ambas métricas y hay "
        f"errores observables: {errores_observables}), pero la rama afinada "
        "no está implementada. Trabajo faltante: implementar ajuste del mismo "
        f"encoder (últimas 2 capas + cabeza, LR {FT_LRS}, {FT_EPOCHS_MAX} "
        f"epochs, batch {FT_BATCH}, acumulación {FT_ACUMULACION}, seed "
        f"{SEMILLA}, tope {FT_MAX_AJUSTES} ajustes / {FT_HORAS_MAX} h), "
        "loader tito-100-* acordado con el integrador #99, y comparación "
        "afinada vs congelada sobre la misma validación. No se finge skip.")


# ---------------------------------------------------------------------------
# Congelamiento: contrato mínimo idéntico a matriz_101.resolver_tito_nuevo
# ---------------------------------------------------------------------------

def validar_congelado(manifiesto: dict, sha_artefacto_real: str,
                      artefacto: dict) -> list[str]:
    """Contrato mínimo del manifiesto congelado. Vacío == válido.

    Espejo exacto de `matriz_101.resolver_tito_nuevo`: identidad del
    encoder (id/revisión de configuración), hashes (artefacto +
    tokenizador), entrada `historial_acumulado` en ambas caras, umbral
    seleccionado en (0, 1] y sin overrides. Además exige formato conocido
    (rechaza `tito-100-*` sin loader, como la matriz) y fuentes con
    hashes hex reales (informe99/supervisión/auditoría/particiones/
    config), no solo dicts presentes.
    """
    from entrenar_tito_99 import (ENCODER_ID, ENCODER_REVISION, FORMATO_99)
    errores = []
    if manifiesto.get("artefacto_sha256") != sha_artefacto_real:
        errores.append("artefacto_sha256 no coincide con el artefacto.")
    formato = artefacto.get("formato", "")
    if isinstance(formato, str) and formato.startswith("tito-100"):
        errores.append(f"formato {formato} sin loader acordado: pendiente, "
                       "no se congela como Tito99.")
    elif formato != FORMATO_99:
        errores.append(f"formato de candidato desconocido: {formato!r}.")
    if manifiesto.get("formato") != formato:
        errores.append("formato del manifiesto no coincide con el artefacto.")
    for fuente, entrada in (("artefacto", artefacto.get("entrada")),
                            ("manifiesto", manifiesto.get("entrada"))):
        if entrada != ENTRADA_NUEVA:
            errores.append(
                f"entrada en {fuente}: {entrada!r}; se exige {ENTRADA_NUEVA!r}.")
    umbral = manifiesto.get("umbral")
    if not isinstance(umbral, (int, float)) or not 0 < float(umbral) <= 1:
        errores.append("manifiesto sin umbral seleccionado en (0, 1].")
    enc_m, enc_a = manifiesto.get("encoder"), artefacto.get("encoder", {})
    if not isinstance(enc_m, dict) or enc_m != enc_a:
        errores.append("encoder del manifiesto no es idéntico al artefacto "
                       "(dict completo: id, revisión, resto).")
    if not enc_m.get("id") if isinstance(enc_m, dict) else True:
        errores.append("manifiesto sin id de encoder.")
    if isinstance(enc_m, dict) and (
            enc_m.get("id") != ENCODER_ID
            or enc_m.get("revision") != ENCODER_REVISION):
        errores.append("el encoder del candidato no es el fijado en "
                       "configuración.")
    tok = artefacto.get("tokenizador", {})
    if not (tok.get("tokenizer_sha256") and artefacto.get("pesos", {}).get("coef")):
        errores.append("candidato sin hash de tokenizador o sin pesos.")
    if not manifiesto.get("variante"):
        errores.append("manifiesto sin variante declarada.")
    fuentes = manifiesto.get("fuentes")
    esperadas = ("informe99", "supervision", "auditoria", "particiones",
                 "config")
    if not isinstance(fuentes, dict) or any(
            not isinstance(fuentes.get(k), dict)
            or not _es_hex64(fuentes[k].get("sha256")) for k in esperadas):
        errores.append("manifiesto sin fuentes con hashes sha256 reales "
                       "(informe99/supervision/auditoria/particiones/config).")
    part = manifiesto.get("particiones")
    if not isinstance(part, dict) \
            or not _es_hex64(part.get("particiones_sha256")) \
            or not part.get("ids_validacion") \
            or len(part.get("ids_comparacion_20", [])) != N_COMPARACION_20:
        errores.append("manifiesto sin bloque particiones "
                       "(particiones_sha256, ids_validacion, "
                       "ids_comparacion_20 exactas).")
    if not manifiesto.get("congelado_en"):
        errores.append("manifiesto sin congelado_en ISO (orden intradía).")
    return errores


def verificar_umbral_cli(umbral_congelado: float,
                         umbral_cli: float | None) -> None:
    """Rechazo explícito del override silencioso (contrato matriz_101)."""
    if umbral_cli is not None \
            and float(umbral_cli) != float(umbral_congelado):
        raise ValueError(
            f"--umbral {umbral_cli} no coincide con el umbral congelado "
            f"{umbral_congelado}: sin override silencioso.")


def verificar_puerta_revision(referencias: dict) -> str:
    """Las referencias siguen sin revisión humana: autorización separada."""
    malas = sorted(cid for cid, r in referencias.items()
                   if r.get("revision_humana") not in (False, None))
    if malas:
        raise ValueError(
            "puerta formal intacta: estas referencias figuran con "
            f"revision_humana y no pueden usarse como desarrollo: {malas}.")
    return AUTORIZACION_DESARROLLO


def ids_comparacion_20(particiones: dict) -> list[str]:
    """Las veinte aprobadas en orden exacto (helper independiente #100).

    Orden canónico: `evaluacion_ids` del manifiesto de particiones (el
    mismo que exige `matriz_101.casos_101`). Cada una con respaldo
    `comparacion_20`, fuera de la reserva y con huellas declaradas. No
    abre ni valida el resto de las particiones.
    """
    ev = particiones.get("evaluacion_ids")
    if not isinstance(ev, list) or len(ev) != N_COMPARACION_20:
        raise ValueError("evaluacion_ids debe traer exactamente las veinte "
                         f"aprobadas (orden de #101), no {ev!r}.")
    if len(set(ev)) != len(ev):
        raise ValueError("evaluacion_ids con duplicados: sin sustituir casos.")
    respaldo = {c.get("case_id"): c for c in particiones.get("conversaciones", [])
                if c.get("particion_preparacion") == "comparacion_20"}
    faltan = [c for c in ev if c not in respaldo]
    if faltan:
        raise ValueError(f"sin respaldo comparacion_20 para: {faltan}.")
    for cid in ev:
        if es_identificador_reserva(cid):
            raise ValueError(f"reserva en evaluacion_ids: {cid}.")
        esp = respaldo[cid]
        for clave in ("texto_sha256", "referencia_sha256"):
            if not _es_hex64(esp.get(clave)):
                raise ValueError(f"{cid}: particiones sin {clave} real.")
    return list(ev)


def _lector_casos_20(cid: str) -> tuple[bytes, bytes]:
    """Bytes crudos en disco de texto y referencia (ruta real, sin abrir más)."""
    try:
        crudo_texto = (DIR_CASOS_TEXTO / f"{cid}.txt").read_bytes()
    except OSError as e:
        raise ValueError(f"{cid}: texto en disco ilegible ({e}).")
    try:
        crudo_ref = (DIR_CASOS_REFERENCIA / f"{cid}.json").read_bytes()
    except OSError as e:
        raise ValueError(f"{cid}: referencia en disco ilegible ({e}).")
    return crudo_texto, crudo_ref


def verificar_comparacion_20(textos: dict, referencias: dict,
                             particiones: dict,
                             lector=None) -> list[str]:
    """Las EXACTAS veinte aprobadas: orden, IDs, textos, referencias y hashes.

    `textos[cid]`: líneas "A: ..."/"B: ...". `lector(cid)` devuelve
    `(texto_bytes, referencia_bytes)` en disco; por defecto lee
    `casos/texto|referencia` (solo las veinte, nada más). Comprueba cada
    hash contra el snapshot de PARTICIONES y que lo pasado coincida con
    el disco: sin sustituir casos ni reescribir historia. La reserva se
    rechaza ANTES de abrir nada.
    """
    ids = ids_comparacion_20(particiones)
    rechazar_reserva(sorted(set(textos) | set(ids)))
    faltan = [c for c in ids if c not in textos]
    if faltan:
        raise ValueError("comprobación incompleta: faltan casos de las "
                         f"veinte (sin sustituir): {faltan}.")
    fuera = sorted(set(textos) - set(ids))
    if fuera:
        raise ValueError("fuera de las veinte: la comprobación no abre "
                         f"otra partición ({fuera}).")
    sin_ref = [c for c in ids if c not in referencias]
    if sin_ref:
        raise ValueError(f"referencias faltantes de las veinte: {sin_ref}.")
    leer = lector or _lector_casos_20
    respaldo = {c.get("case_id"): c for c in particiones.get("conversaciones", [])}
    for cid in ids:
        try:
            crudo_texto, crudo_ref = leer(cid)
        except ValueError:
            raise
        except Exception as e:  # noqa: BLE001 - causa trazable, no silencio
            raise ValueError(f"{cid}: lector de casos falló "
                             f"({type(e).__name__}: {e}).")
        esp = respaldo[cid]
        if sha_bytes(crudo_texto) != esp.get("texto_sha256"):
            raise ValueError(f"{cid}: deriva de hash en texto "
                             "(no coincide con particiones).")
        if sha_bytes(crudo_ref) != esp.get("referencia_sha256"):
            raise ValueError(f"{cid}: deriva de hash en referencia "
                             "(no coincide con particiones).")
        try:
            lineas_disco = crudo_texto.decode("utf-8").splitlines()
        except UnicodeDecodeError as e:
            raise ValueError(f"{cid}: texto en disco no UTF-8 ({e}).")
        if [str(l) for l in textos[cid]] != lineas_disco:
            raise ValueError(f"{cid}: textos pasados no coinciden con el "
                             "disco congelado.")
        try:
            ref_disco = json.loads(crudo_ref.decode("utf-8"))
        except ValueError as e:
            raise ValueError(f"{cid}: referencia en disco ilegible ({e}).")
        if referencias[cid] != ref_disco:
            raise ValueError(f"{cid}: referencia pasada no coincide con el "
                             "disco congelado.")
        if not lineas_disco or not all(
                re.match(r"^[AB]: ", l) for l in lineas_disco):
            raise ValueError(f"{cid}: diálogo sin formato 'A: '/'B: '.")
    return ids


def construir_manifiesto_congelado(seleccion: dict, artefacto_ruta: Path,
                                   artefacto: dict, umbral: float,
                                   variante: str, fuentes: dict,
                                   codigo: dict, particiones_sha256: str,
                                   ids_validacion: list[str],
                                   ids_comparacion_20: list[str]) -> dict:
    """Manifiesto CANDIDATO-TITO-100: identidad, procedencia y orden temporal."""
    return {
        "issue": 100,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "congelado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estado": ESTADO_CONGELADO,
        "orden_temporal": ("selección y congelamiento SOLO con validación, "
                           "ANTES de abrir la evaluación independiente; la "
                           "comprobación registra su marca temporal posterior."),
        "artefacto": str(artefacto_ruta),
        "artefacto_sha256": sha_archivo(artefacto_ruta),
        "formato": artefacto.get("formato"),
        "variante": variante,
        "entrada": ENTRADA_NUEVA,
        "umbral": float(umbral),
        "umbral_viejo": UMBRAL_VIEJO,
        "entrada_vieja": ENTRADA_VIEJA,
        "encoder": dict(artefacto.get("encoder", {})),
        "tokenizer_sha256": artefacto.get("tokenizador", {}).get("tokenizer_sha256"),
        "seleccion_validacion": {
            "elegida": seleccion.get("elegida"),
            "criterio": seleccion.get("criterio"),
            "frontera": seleccion.get("frontera_pareto"),
        },
        "decision_fine_tuning": seleccion.get("decision_fine_tuning"),
        "particiones": {
            "particiones_sha256": particiones_sha256,
            "ids_validacion": list(ids_validacion),
            "ids_comparacion_20": list(ids_comparacion_20),
        },
        "fuentes": fuentes,
        "codigo": codigo,
        "runtime": info_runtime(),
        "semilla": SEMILLA,
        "autorizacion": AUTORIZACION_DESARROLLO,
    }


def construir_manifiesto_bloqueado_ft(decision_error: BloqueoFineTuning,
                                      codigo: dict, contexto: dict) -> dict:
    """Registro explícito de FT correspondiente sin rama afinada."""
    return {
        "issue": 100,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "congelado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estado": ESTADO_BLOQUEADO_FT,
        "motivo": str(decision_error),
        "contexto": contexto,
        "trabajo_faltante": [
            "implementar ajuste del mismo encoder (últimas 2 capas + cabeza, "
            f"LR {FT_LRS}, {FT_EPOCHS_MAX} epochs, batch {FT_BATCH}, "
            f"acumulación {FT_ACUMULACION}, seed {SEMILLA}, tope "
            f"{FT_MAX_AJUSTES} ajustes / {FT_HORAS_MAX} h), sin ampliar el "
            "presupuesto en silencio y solo con entrenamiento",
            "acordar loader tito-100-* con el integrador #99 (no cargar la "
            "afinada como Tito99)",
            "comparar afinada vs congelada sobre la misma validación, con "
            "entradas y revisiones trazables",
        ],
        "codigo": codigo,
        "runtime": info_runtime(),
        "semilla": SEMILLA,
    }


# ---------------------------------------------------------------------------
# Comprobación por replay (sin fit, sin cambio de ventana ni umbral)
# ---------------------------------------------------------------------------

def recorrer_conversacion_con_trazas(puntuar_prefijo, n_lineas: int,
                                     umbral: float) -> dict:
    """Replay prefijo a prefijo: posiciones y costos conservados.

    `puntuar_prefijo(k)` -> (puntaje|None, error, ms). Los None (fallos de
    inferencia) no se filtran: no derivan por sí mismos (fail-open) y se
    cuentan. La derivación es el primer k con puntaje no nulo >= umbral.
    """
    puntajes: list[float | None] = []
    errores: list[str] = []
    ms: list[float] = []
    fallos = 0
    for k in range(1, n_lineas + 1):
        p, err, m = puntuar_prefijo(k)
        puntajes.append(p)
        ms.append(round(float(m), 3))
        if p is None:
            fallos += 1
            if err:
                errores.append(f"k={k}:{err}")
    derivacion = None
    for k, p in enumerate(puntajes, start=1):
        if p is not None and p >= umbral:
            derivacion = k
            break
    return {"derivacion": derivacion, "puntajes": puntajes, "ms": ms,
            "fallos": fallos, "errores": errores}


def comparar_sobre_conjunto(textos: dict, referencias: dict,
                            etiquetas: dict, puntaje_nuevo,
                            puntaje_viejo, umbral_nuevo: float,
                            umbral_viejo: float = UMBRAL_VIEJO) -> dict:
    """Mismas conversaciones, dos comparadores recargados sin entrenar.

    `textos[cid]`: líneas "A: ..."/"B: ..." (historial con hablantes).
    `puntaje_nuevo(cid, k)` / `puntaje_viejo(cid, k)` -> (p|None, err, ms).
    Métricas conversacionales vía `entrenar_tito_99.evaluar_configuracion`
    y clasificación binaria SOLO sobre prefijos revisados (0/1): sin
    etiquetas revisadas no se inventa F1 (el evaluador devuelve None con
    motivo). Nunca se usa la clase final ni T_R como etiqueta de prefijo.
    """
    from entrenar_tito_99 import (evaluar_configuracion,
                                  metricas_prefijos_revisados)
    nuevo = evaluar_configuracion([], textos, referencias, puntaje_nuevo,
                                  umbral_nuevo)
    viejo = evaluar_configuracion([], textos, referencias, puntaje_viejo,
                                  umbral_viejo)
    puntajes_nuevo = {c["case_id"]: c["puntajes"] for c in nuevo["por_caso"]
                      for cid in [c["case_id"]]}
    puntajes_viejo = {c["case_id"]: c["puntajes"] for c in viejo["por_caso"]
                      for cid in [c["case_id"]]}
    return {
        "umbral_nuevo": umbral_nuevo,
        "umbral_viejo": umbral_viejo,
        "nuevo": nuevo,
        "viejo": viejo,
        "prefijos_nuevo": metricas_prefijos_revisados(
            puntajes_nuevo, etiquetas, umbral_nuevo),
        "prefijos_viejo": metricas_prefijos_revisados(
            puntajes_viejo, etiquetas, umbral_viejo),
        "nota": ("Derivación de Tito no es alerta; sin T_R el caso vishing "
                 "es no evaluable en oportunidad y conserva denominadores. "
                 "Clasificación binaria solo sobre prefijos revisados."),
    }


def evaluar_comprobacion(manifiesto_ruta: Path, artefacto_nuevo_ruta: Path,
                         artefacto_viejo_ruta: Path, textos: dict,
                         referencias: dict, etiquetas: dict,
                         tito_nuevo=None, tito_viejo=None, *,
                         umbral_cli: float | None = None,
                         politica_manifiesto: Path | None = None,
                         particiones: dict | None = None,
                         lector_20=None) -> dict:
    """Comprueba el candidato congelado sobre las EXACTAS veinte (sin fit).

    Recarga ambos comparadores desde disco (los dobles inyectados SOLO
    sirven a pruebas; en producción son Tito99 + TitoReal reales).
    Exige manifiesto en estado congelado, ligado a PARTICIONES vigente
    (sha + orden exacto de `ids_comparacion_20`), y comprueba las veinte
    aprobadas con `verificar_comparacion_20`: orden, IDs, textos,
    referencias y hashes; la reserva se rechaza antes de abrir nada y no
    se admite otra partición (validación incluida: no se sustituyen
    casos). `particiones`/`lector_20` solo existen para pruebas con
    fixtures explícitos; en producción son None (archivos reales).
    """
    try:
        manifiesto = json.loads(Path(manifiesto_ruta).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"manifiesto congelado ilegible ({manifiesto_ruta}): "
                         f"{type(e).__name__}: {e}.")
    if manifiesto.get("estado") == ESTADO_BLOQUEADO_FT:
        raise BloqueoFineTuning(
            "manifiesto bloqueado: FT corresponde pero la rama afinada no "
            "existe. Trabajo faltante en el propio manifiesto.")
    if manifiesto.get("estado") != ESTADO_CONGELADO:
        raise ValueError("sin candidato congelado: correr `congelar` primero "
                         "(congelar ANTES de comprobar).")
    if not Path(artefacto_nuevo_ruta).exists():
        raise ValueError(f"artefacto nuevo ausente: {artefacto_nuevo_ruta}.")
    if sha_archivo(artefacto_nuevo_ruta) != manifiesto.get("artefacto_sha256"):
        raise ValueError("el artefacto no coincide con el artefacto_sha256 "
                         "del manifiesto congelado.")
    try:
        artefacto = json.loads(Path(artefacto_nuevo_ruta).read_text(encoding="utf-8"))
    except ValueError as e:
        raise ValueError(f"artefacto nuevo ilegible: {e}.")
    errores_contrato = validar_congelado(
        manifiesto, manifiesto.get("artefacto_sha256"), artefacto)
    if errores_contrato:
        raise ValueError("manifiesto roto contra el contrato mínimo "
                         "(matriz_101.resolver_tito_nuevo): "
                         + "; ".join(errores_contrato))
    umbral_nuevo = manifiesto["umbral"]
    verificar_umbral_cli(umbral_nuevo, umbral_cli)
    if politica_manifiesto is not None:
        _verificar_politica_102(politica_manifiesto,
                                manifiesto.get("artefacto_sha256"))
    vigente = particiones if particiones is not None else cargar_particiones()
    if particiones is None:
        sha_vigente = sha_archivo(AQUI / PARTICIONES_NOMBRE)
    else:
        sha_vigente = vigente.get("particiones_sha256")
        if not _es_hex64(sha_vigente):
            raise ValueError("fixture de particiones sin "
                             "particiones_sha256 real.")
    part_man = manifiesto.get("particiones", {})
    if part_man.get("particiones_sha256") != sha_vigente:
        raise ValueError("manifiesto desligado de PARTICIONES vigente: "
                         "recongelar antes de comprobar.")
    ids_vigentes = ids_comparacion_20(vigente)
    if list(part_man.get("ids_comparacion_20", [])) != ids_vigentes:
        raise ValueError("ids_comparacion_20 del manifiesto no coinciden con "
                         "PARTICIONES vigente (orden exacto): recongelar.")
    verificar_comparacion_20(textos, referencias, vigente, lector_20)
    autorizacion = verificar_puerta_revision(referencias)
    # Recarga sin entrenar: los artefactos llegan congelados de #99/#100.
    if tito_nuevo is None:
        from entrenar_tito_99 import Tito99
        tito_nuevo = Tito99(artefacto_nuevo_ruta)
    if tito_viejo is None:
        from tito_real import TitoReal
        tito_viejo = TitoReal(artefacto_viejo_ruta)
    if getattr(tito_nuevo, "entrada", ENTRADA_NUEVA) != ENTRADA_NUEVA:
        raise ValueError("el candidato recargado no usa historial_acumulado.")
    from entrenar_tito_99 import construir_entrada

    def puntaje_nuevo(cid, k):
        visibles = textos[cid][:k]
        entrada = construir_entrada(visibles, ENTRADA_NUEVA)
        return tito_nuevo.puntuar_entrada(entrada)

    def puntaje_viejo(cid, k):
        frase = textos[cid][k - 1].split(": ", 1)[-1]
        return tito_viejo.puntuar(k, frase)

    # Preparación explícita una vez por proceso, fuera de las actualizaciones.
    try:
        import matriz_101 as _m101
        prep_nuevo = _m101.preparar_tito_99(tito_nuevo)
    except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
        prep_nuevo = {"error": f"preparacion_nuevo: {type(e).__name__}: {e}"}
    try:
        prep_viejo = tito_viejo.preparar() \
            if hasattr(tito_viejo, "preparar") else {"preparacion": "doble"}
    except Exception as e:  # noqa: BLE001
        prep_viejo = {"error": f"preparacion_viejo: {type(e).__name__}: {e}"}
    comparacion = comparar_sobre_conjunto(
        textos, referencias, etiquetas, puntaje_nuevo, puntaje_viejo,
        float(umbral_nuevo), UMBRAL_VIEJO)
    return {
        "manifiesto": str(manifiesto_ruta),
        "manifiesto_sha256": sha_archivo(manifiesto_ruta),
        "comprobado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "orden_temporal": "comprobación posterior al congelamiento, sobre "
                          "las veinte aprobadas; no se reentrena ni se "
                          "cambia ventana/umbral.",
        "autorizacion": autorizacion,
        "preparacion_nuevo": prep_nuevo,
        "preparacion_viejo": prep_viejo,
        "comparacion": comparacion,
        "limites": ("Ninguna mejora del sistema se infiere solo por Tito: "
                    "la derivación no es alerta y una conversación sin "
                    "derivación no prueba legitimidad."),
    }


def _verificar_politica_102(politica_ruta: Path,
                            artefacto_sha256: str | None) -> dict:
    """Puerta opcional de secuencia: política #102 ya congelada y ligada."""
    try:
        pol = json.loads(Path(politica_ruta).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"manifiesto de política #102 ilegible "
                         f"({politica_ruta}): {type(e).__name__}: {e}.")
    if pol.get("etapa") != "seleccion-102-congelada":
        raise ValueError("política #102 sin congelar "
                         "(etapa != seleccion-102-congelada): respetar la "
                         "secuencia congelar100 -> seleccionar/congelar102 "
                         "-> comprobar100.")
    tito_fijado = pol.get("tito_congelado", {})
    if tito_fijado.get("artefacto_sha256") != artefacto_sha256:
        raise ValueError("política #102 ligada a otro candidato: no mide "
                         "este congelado.")
    if tito_fijado.get("entrada") != ENTRADA_NUEVA:
        raise ValueError("política #102 sin historial_acumulado fijado.")
    return pol


# ---------------------------------------------------------------------------
# Reporte regenerable sin nueva inferencia
# ---------------------------------------------------------------------------

def armar_informe_md(comp: dict) -> str:
    """Markdown desde un JSON de comprobación (sin inferencia)."""
    c = comp["comparacion"]
    nuevo, viejo = c["nuevo"], c["viejo"]
    ln: list[str] = [
        "# Comprobación Tito #100 (comparación 20, sin fit)",
        "",
        f"- Manifiesto: `{comp['manifiesto']}` ({comp['manifiesto_sha256'][:12]}…)",
        f"- Comprobado en: {comp['comprobado_en']} (posterior al congelamiento)",
        f"- Umbrales: nuevo {c['umbral_nuevo']} / viejo {c['umbral_viejo']}",
        f"- Autorización: {comp['autorizacion'][:60]}…",
        "",
        "## Conversacional (comparación 20)",
        "",
        "| comparador | omisiones oportunas | legítimas derivadas | "
        "vishing (den.) | legítimas (den.) | sin T_R | fallos |",
        "|---|---|---|---|---|---|---|",
        f"| nuevo | {nuevo['omisiones_oportunas']} | {nuevo['legitimas_derivadas']} | "
        f"{nuevo['denominador_vishing']} | {nuevo['denominador_legitimas']} | "
        f"{nuevo['vishing_no_evaluable_sin_TR']} | {nuevo['prefijos_con_fallo']} |",
        f"| viejo | {viejo['omisiones_oportunas']} | {viejo['legitimas_derivadas']} | "
        f"{viejo['denominador_vishing']} | {viejo['denominador_legitimas']} | "
        f"{viejo['vishing_no_evaluable_sin_TR']} | {viejo['prefijos_con_fallo']} |",
        "",
        "## Prefijos revisados (0/1; inciertos y sin registro en cobertura)",
        "",
        "| comparador | revisados | tp | fp | tn | fn | exactitud | f1 |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for nombre in ("nuevo", "viejo"):
        p = c[f"prefijos_{nombre}"]
        ln.append(
            f"| {nombre} | {p['revisados']} | {p['tp']} | {p['fp']} | "
            f"{p['tn']} | {p['fn']} | {p['exactitud']} | {p['f1']} |")
    ln += ["",
           "## Por caso",
           "",
           "| caso | clase | T_R | T_C | der. nuevo | der. viejo | "
           "oportuna nuevo | oportuna viejo |",
           "|---|---|---|---|---|---|---|---|"]
    casos = {e["case_id"]: e for e in nuevo["por_caso"]}
    for e in viejo["por_caso"]:
        n = casos[e["case_id"]]
        ln.append(
            f"| {e['case_id']} | {e['clase']} | {e['t_r']} | {e['t_c']} | "
            f"{n['derivacion']} | {e['derivacion']} | {n['oportuna']} | "
            f"{e['oportuna']} |")
    ln += ["",
           "## Negativos, fallos y cobertura",
           "",
           f"- Fallos de inferencia (prefijos): nuevo "
           f"{nuevo['prefijos_con_fallo']}, viejo {viejo['prefijos_con_fallo']}.",
           "- Casos nunca derivados o sin T_R permanecen visibles arriba con "
           "su tratamiento explícito; no se fabrica cumplimiento.",
           f"- {comp['limites']}",
           f"- {c['nota']}"]
    return "\n".join(ln) + "\n"


def guardar_comprobacion(ruta: Path, contenido: dict) -> Path:
    _guardar_atomico(ruta, contenido)
    md = Path(ruta).with_suffix(".md")
    md.write_text(armar_informe_md(contenido), encoding="utf-8")
    return Path(ruta)


def regenerar_md(entrada_json: Path, salida_md: Path | None = None) -> Path:
    """Regenera el .md desde un JSON ya corrido (sin inferencia)."""
    try:
        comp = json.loads(Path(entrada_json).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise ValueError(f"comprobación ilegible ({entrada_json}): "
                         f"{type(e).__name__}: {e}.")
    for clave in ("comparacion", "manifiesto", "manifiesto_sha256",
                  "comprobado_en", "autorizacion", "limites"):
        if clave not in comp:
            raise ValueError(f"comprobación sin {clave!r}: no se regenera.")
    destino = salida_md or Path(entrada_json).with_suffix(".md")
    Path(destino).write_text(armar_informe_md(comp), encoding="utf-8")
    return Path(destino)


# ---------------------------------------------------------------------------
# Congelar: informe #99 real -> decisión condicional -> manifiesto
# ---------------------------------------------------------------------------

def _cargar_json(ruta: Path, que: str) -> dict:
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except OSError as e:
        raise ValueError(f"{que} ausente o ilegible ({ruta}): {e}.")
    except ValueError as e:
        raise ValueError(f"{que} con JSON inválido ({ruta}): {e}.")
    if not isinstance(datos, dict):
        raise ValueError(f"{que} sin objeto JSON ({ruta}).")
    return datos


def _guardar_atomico(ruta: Path, contenido: dict) -> Path:
    """Escritura atómica (tmp + rename); nunca deja medio manifiesto."""
    destino = Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(destino.parent), prefix=".tmp-",
                               suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(contenido, f, ensure_ascii=False, indent=1)
        os.replace(tmp, destino)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return destino


def _rechazar_sobreescritura_congelada(salida: Path) -> None:
    """La identidad congelada no se sobreescribe tras abrir la evaluación."""
    if not salida.exists():
        return
    try:
        previo = json.loads(salida.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if isinstance(previo, dict) and previo.get("estado") == ESTADO_CONGELADO:
        raise ValueError(f"{salida}: identidad ya congelada "
                         f"({previo.get('congelado_en', '?')}); no se "
                         "sobreescribe tras abrir la evaluación. Recongelar "
                         "exige un manifiesto nuevo con otra identidad.")


def _parse_config_nombre(config: str) -> tuple[str, float, float]:
    """`historial_acumulado/C=1.0/u=0.5` -> (entrada, C, umbral)."""
    m = re.fullmatch(r"([^/]+)/C=([^/]+)/u=([^/]+)", str(config))
    if not m:
        raise ValueError(f"config sin formato entrada/C/u: {config!r}.")
    try:
        return m.group(1), float(m.group(2)), float(m.group(3))
    except ValueError:
        raise ValueError(f"config con C/umbral no numéricos: {config!r}.")


def _validar_informe99(informe: dict) -> tuple[list[dict], dict, dict, dict]:
    """Esquema real del REPORTE #99: resultados, costos, selección, baseline."""
    resultados = informe.get("resultados_validacion")
    if not isinstance(resultados, list) or not resultados:
        raise ValueError("informe99 sin resultados_validacion no vacíos.")
    if len(resultados) > N_CONFIGS_MAX:
        raise ValueError(f"informe99 con {len(resultados)} configuraciones: "
                         f"máximo {N_CONFIGS_MAX}.")
    costos = informe.get("costos_p95_ms")
    seleccion = informe.get("seleccion")
    criterio_ft = informe.get("criterio_fine_tuning")
    if not isinstance(costos, dict) or not isinstance(seleccion, dict) \
            or not isinstance(criterio_ft, dict):
        raise ValueError("informe99 sin costos_p95_ms/seleccion/"
                         "criterio_fine_tuning.")
    for r in resultados:
        for k in ("config", "entrada", "C", "umbral", "omisiones_oportunas",
                  "legitimas_derivadas"):
            if k not in r:
                raise ValueError(f"resultado99 sin {k!r}: {r!r}.")
        if r["config"] not in costos:
            raise ValueError(f"resultado99 sin costo p95 real: {r['config']!r}.")
    elegida = seleccion.get("elegida")
    if elegida not in {r["config"] for r in resultados}:
        raise ValueError(f"selección99 con elegida fuera de resultados: {elegida!r}.")
    eleg = next(r for r in resultados if r["config"] == elegida)
    entrada_eleg, _c_eleg, u_eleg = _parse_config_nombre(elegida)
    if eleg.get("entrada") != ENTRADA_NUEVA or entrada_eleg != ENTRADA_NUEVA:
        raise ValueError("la elegida99 no usa historial_acumulado: no es "
                         "el candidato principal.")
    if not isinstance(u_eleg, float) or not 0 < u_eleg <= 1:
        raise ValueError(f"elegida99 sin umbral en (0, 1]: {elegida!r}.")
    if eleg.get("umbral") != u_eleg:
        raise ValueError("umbral del resultado distinto del declarado en "
                         f"su config: {elegida!r}.")
    baseline = criterio_ft.get("baseline_viejo")
    if not isinstance(baseline, dict) or any(
            k not in baseline for k in ("omisiones_oportunas",
                                        "legitimas_derivadas")):
        raise ValueError("informe99 sin baseline_viejo con ambos conteos.")
    return resultados, costos, seleccion, baseline


def _errores_observables_99(resultados: list[dict], baseline: dict) -> list[str]:
    """Conteos > 0 visibles en validación que justificarían ajustar."""
    errores = []
    base_suma = baseline["omisiones_oportunas"] + baseline["legitimas_derivadas"]
    if base_suma > 0:
        errores.append(f"viejo: omisiones_oportunas="
                       f"{baseline['omisiones_oportunas']} "
                       f"legitimas_derivadas={baseline['legitimas_derivadas']}")
    for r in resultados:
        if r["omisiones_oportunas"] + r["legitimas_derivadas"] > 0:
            errores.append(f"{r['config']}: omisiones_oportunas="
                           f"{r['omisiones_oportunas']} legitimas_derivadas="
                           f"{r['legitimas_derivadas']}")
    return errores


def _rutas_supervision_auditoria() -> tuple[Path, Path]:
    """Artefactos reales del supervisor (fail-closed si faltan)."""
    try:
        from supervision_tito_99 import AUDITORIA_RUTA, SUPERVISION_RUTA
        return Path(SUPERVISION_RUTA), Path(AUDITORIA_RUTA)
    except ImportError:
        from entrenar_tito_99 import (AUDITORIA_SEMANTICA_REAL_NOMBRE,
                                      SUPERVISION_REAL_NOMBRE)
        return (AQUI / SUPERVISION_REAL_NOMBRE,
                AQUI / AUDITORIA_SEMANTICA_REAL_NOMBRE)


def congelar_desde_informe99(resultados99_ruta: Path, artefacto_ruta: Path,
                             salida: Path,
                             umbral_cli: float | None = None, *,
                             rutas_sup_aud: tuple[Path, Path] | None = None) -> dict:
    """Decide FT con TODOS los congelados y congela el candidato elegido.

    Consume el informe REAL #99 (schema validado, elegida con historial,
    <= 18 configuraciones), verifica que el artefacto corresponda a la
    elegida (entrada y C), aplica la regla sobre todos los candidatos vs
    el viejo + errores observables, y guarda el manifiesto atómicamente
    (sin sobreescribir identidad congelada). Si FT corresponde sin rama
    afinada, guarda el bloqueo explícito y levanta BloqueoFineTuning.
    No implementa ni ejecuta FT ni ninguna inferencia. `rutas_sup_aud`
    solo existe para pruebas con fixtures explícitos.
    """
    if not Path(resultados99_ruta).exists():
        raise ValueError(f"resultados99 ausentes: {resultados99_ruta} "
                         "(sin resultados #99 reales no se congela nada).")
    if not Path(artefacto_ruta).exists():
        raise ValueError(f"artefacto candidato ausente: {artefacto_ruta}.")
    informe = _cargar_json(resultados99_ruta, "informe99")
    resultados, _costos, seleccion, baseline = _validar_informe99(informe)
    artefacto = _cargar_json(artefacto_ruta, "artefacto candidato")
    elegida = seleccion["elegida"]
    _entrada_eleg, c_eleg, u_eleg = _parse_config_nombre(elegida)
    verificar_umbral_cli(u_eleg, umbral_cli)
    if artefacto.get("entrada") != ENTRADA_NUEVA:
        raise ValueError("el artefacto no usa historial_acumulado: no es "
                         "el candidato principal.")
    try:
        c_arte = float(artefacto.get("config_regresion", {}).get("C"))
    except (TypeError, ValueError):
        raise ValueError("artefacto sin config_regresion.C numérico.")
    if c_arte != c_eleg:
        raise ValueError(f"artefacto C={c_arte} no corresponde a la elegida "
                         f"{elegida} (C={c_eleg}): sin sustitución.")
    candidatos = [{"config": r["config"],
                   "omisiones_oportunas": r["omisiones_oportunas"],
                   "legitimas_derivadas": r["legitimas_derivadas"]}
                  for r in resultados]
    errores_obs = _errores_observables_99(resultados, baseline)
    try:
        decision = decidir_fine_tuning(candidatos, baseline, errores_obs)
    except BloqueoFineTuning as e:
        _rechazar_sobreescritura_congelada(salida)
        contexto = {"informe99": str(resultados99_ruta),
                    "informe99_sha256": sha_archivo(resultados99_ruta),
                    "elegida": elegida,
                    "baseline_viejo": dict(baseline),
                    "errores_observables": errores_obs}
        bloqueado = construir_manifiesto_bloqueado_ft(e, info_codigo(),
                                                      contexto)
        _guardar_atomico(salida, bloqueado)
        raise
    particiones = cargar_particiones()
    sha_particiones = sha_archivo(AQUI / PARTICIONES_NOMBRE)
    sha_config = sha_archivo(AQUI / CONFIG_NOMBRE)
    ruta_sup, ruta_aud = rutas_sup_aud or _rutas_supervision_auditoria()
    for ruta, nombre in ((ruta_sup, "supervisión"), (ruta_aud, "auditoría")):
        if not ruta.exists():
            raise ValueError(f"artefacto de {nombre} ausente: {ruta} "
                             "(fail-closed: sin procedencia no se congela).")
    _rechazar_sobreescritura_congelada(salida)
    fuentes = {
        "informe99": {"ruta": Path(resultados99_ruta).name,
                      "sha256": sha_archivo(resultados99_ruta)},
        "supervision": {"ruta": ruta_sup.name,
                        "sha256": sha_archivo(ruta_sup)},
        "auditoria": {"ruta": ruta_aud.name,
                      "sha256": sha_archivo(ruta_aud)},
        "particiones": {"ruta": PARTICIONES_NOMBRE, "sha256": sha_particiones},
        "config": {"ruta": CONFIG_NOMBRE, "sha256": sha_config},
    }
    seleccion_con_decision = dict(seleccion)
    seleccion_con_decision["decision_fine_tuning"] = decision
    manifiesto = construir_manifiesto_congelado(
        seleccion_con_decision, artefacto_ruta, artefacto, u_eleg,
        "#99-congelada", fuentes, info_codigo(), sha_particiones,
        ids_validacion_conversaciones(particiones),
        ids_comparacion_20(particiones))
    errores_contrato = validar_congelado(
        manifiesto, sha_archivo(artefacto_ruta), artefacto)
    if errores_contrato:
        raise ValueError("manifiesto construido inválido contra el contrato "
                         "mínimo: " + "; ".join(errores_contrato))
    _guardar_atomico(salida, manifiesto)
    return manifiesto


# ---------------------------------------------------------------------------
# CLI por etapas: congelar / evaluar / regenerar
# ---------------------------------------------------------------------------

def _cargar_textos_20(ids: list[str], lector=None) -> tuple[dict, dict]:
    """Textos y referencias de las veinte desde disco (ejecución futura)."""
    leer = lector or _lector_casos_20
    textos, referencias = {}, {}
    for cid in ids:
        crudo_texto, crudo_ref = leer(cid)
        textos[cid] = crudo_texto.decode("utf-8").splitlines()
        referencias[cid] = json.loads(crudo_ref.decode("utf-8"))
    return textos, referencias


def _cargar_etiquetas(ruta: Path | None) -> dict:
    """`{"cid:k": 0/1/null}`; sin archivo no se inventa F1."""
    if ruta is None:
        return {}
    datos = _cargar_json(ruta, "etiquetas")
    etiquetas = {}
    for clave, valor in datos.items():
        if valor not in (0, 1, None):
            raise ValueError(f"etiqueta inválida {clave!r}={valor!r}: "
                             "solo 0/1/null.")
        try:
            cid, k = str(clave).rsplit(":", 1)
            etiquetas[(cid, int(k))] = valor
        except ValueError:
            raise ValueError(f"etiqueta sin formato 'cid:k': {clave!r}.")
    return etiquetas


def _cmd_congelar(args) -> int:
    if not args.resultados99:
        print("congelar exige --resultados99 (informe REAL #99).",
              file=sys.stderr)
        return RC_USO
    if not args.artefacto:
        print("congelar exige --artefacto (candidato #99).", file=sys.stderr)
        return RC_USO
    try:
        manifiesto = congelar_desde_informe99(
            args.resultados99, args.artefacto, args.salida, args.umbral)
    except BloqueoFineTuning as e:
        print(f"congelar: BLOQUEADO (guardado explícito en {args.salida}): "
              f"{e}", file=sys.stderr)
        return RC_BLOQUEADO_FT
    except ValueError as e:
        print(f"congelar: {e}", file=sys.stderr)
        return RC_USO
    print(f"congelado_en={manifiesto['congelado_en']} "
          f"elegida={manifiesto['seleccion_validacion']['elegida']} "
          f"umbral={manifiesto['umbral']} salida={args.salida}")
    return 0


def _cmd_evaluar(args) -> int:
    if not args.manifiesto or not Path(args.manifiesto).exists():
        print(f"evaluar exige --manifiesto congelado existente "
              f"({args.manifiesto}).", file=sys.stderr)
        return RC_USO
    manifiesto = _cargar_json(args.manifiesto, "manifiesto congelado")
    if manifiesto.get("estado") != ESTADO_CONGELADO:
        print("evaluar: sin candidato congelado (congelar ANTES de "
              "comprobar).", file=sys.stderr)
        return RC_USO
    artefacto_nuevo = args.artefacto_nuevo or manifiesto.get("artefacto")
    if not artefacto_nuevo or not Path(artefacto_nuevo).exists():
        print(f"evaluar exige artefacto nuevo existente ({artefacto_nuevo}).",
              file=sys.stderr)
        return RC_USO
    artefacto_viejo = args.artefacto_viejo or str(AQUI / "tito_logreg.json")
    if not Path(artefacto_viejo).exists():
        print(f"evaluar exige artefacto viejo existente ({artefacto_viejo}).",
              file=sys.stderr)
        return RC_USO
    try:
        particiones = cargar_particiones()
        ids = ids_comparacion_20(particiones)
        textos, referencias = _cargar_textos_20(ids)
        etiquetas = _cargar_etiquetas(args.etiquetas)
        comp = evaluar_comprobacion(
            args.manifiesto, artefacto_nuevo, artefacto_viejo, textos,
            referencias, etiquetas, umbral_cli=args.umbral,
            politica_manifiesto=args.politica_manifiesto)
        guardar_comprobacion(args.salida, comp)
    except BloqueoFineTuning as e:
        print(f"evaluar: BLOQUEADO: {e}", file=sys.stderr)
        return RC_BLOQUEADO_FT
    except ValueError as e:
        print(f"evaluar: {e}", file=sys.stderr)
        return RC_USO
    print(f"comprobado_en={comp['comprobado_en']} salida={args.salida}")
    return 0


def _cmd_regenerar(args) -> int:
    if args.entrada is None:
        print("regenerar exige --entrada JSON.", file=sys.stderr)
        return RC_USO
    try:
        destino = regenerar_md(args.entrada, args.salida)
    except ValueError as e:
        print(f"regenerar: {e}", file=sys.stderr)
        return RC_USO
    print(f"md={destino}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paso", choices=["congelar", "evaluar", "regenerar"],
                   required=True,
                   help="congelar: decide FT con el informe #99 y congela "
                        "SIN abrir las veinte; evaluar: comprueba el "
                        "congelado sobre las EXACTAS veinte; regenerar: "
                        ".md desde JSON sin inferencia.")
    p.add_argument("--resultados99", type=Path, default=None,
                   help="REPORTE #99 real (congelar).")
    p.add_argument("--artefacto", type=Path, default=None,
                   help="artefacto candidato #99 (congelar).")
    p.add_argument("--artefacto-nuevo", type=Path, default=None,
                   help="artefacto nuevo (evaluar; por defecto el del "
                        "manifiesto).")
    p.add_argument("--artefacto-viejo", type=Path, default=None,
                   help="artefacto viejo (evaluar; por defecto "
                        "tito_logreg.json).")
    p.add_argument("--manifiesto", type=Path,
                   default=AQUI / MANIFIESTO_CONGELADO_NOMBRE,
                   help="manifiesto congelado (evaluar).")
    p.add_argument("--politica-manifiesto", type=Path, default=None,
                   help="manifiesto de política #102 congelada (puerta "
                        "opcional de secuencia para evaluar).")
    p.add_argument("--etiquetas", type=Path, default=None,
                   help='JSON {"cid:k": 0/1/null} (evaluar; sin archivo no '
                        'se inventa F1).')
    p.add_argument("--salida", type=Path, default=None)
    p.add_argument("--entrada", type=Path, default=None,
                   help="JSON de comprobación (regenerar).")
    p.add_argument("--umbral", type=float, default=None,
                   help="solo para coincidir con el congelado; distinto "
                        "se rechaza.")
    args = p.parse_args(argv)
    if args.paso == "regenerar":
        return _cmd_regenerar(args)
    if args.paso == "congelar":
        if args.salida is None:
            args.salida = AQUI / MANIFIESTO_CONGELADO_NOMBRE
        return _cmd_congelar(args)
    if args.paso == "evaluar":
        if args.salida is None:
            args.salida = Path(args.manifiesto).with_name(
                "COMPROBACION-TITO-100-2026-10-29.json")
        return _cmd_evaluar(args)
    return RC_USO


if __name__ == "__main__":
    raise SystemExit(main())
