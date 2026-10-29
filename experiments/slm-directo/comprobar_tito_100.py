"""Comprobación preparatoria del candidato de Tito (#100, sin pesos nuevos).

Lee los resultados reales de #99 cuando existan, aplica la regla
condicional exacta de `CONFIGURACION-TITO-2026-10-29.json` (fine-tuning
SOLO si NINGUN candidato congelado conserva o reduce a la vez omisiones
oportunas y legítimas derivadas frente al viejo en validación Y hay un
error observable que lo justifique; el empate en ambos NO fuerza FT) y,
si no corresponde, congela el candidato/umbral/entrada elegidos SOLO con
validación en `CANDIDATO-TITO-100-2026-10-29.json` para comprobarlos
después en la evaluación independiente.

Si corresponde FT pero la rama afinada no está implementada, el
congelamiento queda BLOQUEADO explícito con el trabajo faltante: no se
finge skip, ni fine-tuning, ni se mide un candidato sin resolver.

La comprobación usa las APIs existentes (`entrenar_tito_99`,
`matriz_101.resolver_tito_nuevo`, `datos_tito`, `casos`): viejo histórico
inmutable (frase aislada, umbral 0,5) y nuevo recargado sin entrenar
(`Tito99`, historial acumulado A/B hasta cada línea, sin futuro).
Recorre cada conversación prefijo por prefijo con la MISMA construcción
de entrada de entrenamiento, trazas/costos/preparación separados y
márgenes T_R/T_C. Sin T_R el caso es no evaluable en oportunidad pero
conserva denominadores; la clasificación binaria cubre SOLO prefijos
revisados (0/1), nunca F1 exhaustivo de las veinte sin etiquetas.

Etapas (CLI): `congelar` / `evaluar` / `regenerar`. `congelar` NUNCA abre
las veinte de comparación; `evaluar` exige manifiesto congelado previo
(congelamiento temporal: congelar ANTES de comprobar) y tampoco abre la
reserva. La rama afinada (`tito-100-*`) queda pendiente: sin loader
acordado con el integrador #99 no se carga como Tito99.

No inventa decisiones ni cierra D07/D08/D09. La revisión de referencia
sigue sin ser humana (`revision_humana: false`): es exploratoria de
desarrollo con autorización explícita separada de la puerta formal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]

CONFIG_NOMBRE = "CONFIGURACION-TITO-2026-10-29.json"
PARTICIONES_NOMBRE = "PARTICIONES-TITO-2026-10-29.json"
MANIFIESTO_CONGELADO_NOMBRE = "CANDIDATO-TITO-100-2026-10-29.json"

SEMILLA = 42
ENTRADA_NUEVA = "historial_acumulado"  # la que exige matriz_101
ENTRADA_VIEJA = "frase_actual_aislada"
UMBRAL_VIEJO = 0.5

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


class BloqueoFineTuning(Exception):
    """FT corresponde pero la rama afinada no existe: bloquear, no fingir."""


# ---------------------------------------------------------------------------
# Huellas e identidad
# ---------------------------------------------------------------------------

def sha_bytes(crudo: bytes) -> str:
    return hashlib.sha256(crudo).hexdigest()


def sha_archivo(ruta: Path) -> str:
    return sha_bytes(Path(ruta).read_bytes())


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


def cargar_config() -> dict:
    return json.loads((AQUI / CONFIG_NOMBRE).read_text(encoding="utf-8"))


def cargar_particiones() -> dict:
    particiones = json.loads((AQUI / PARTICIONES_NOMBRE).read_text(encoding="utf-8"))
    if particiones.get("semilla") != SEMILLA:
        raise ValueError("particiones con semilla inesperada.")
    return particiones


def grupos_por_particion(particiones: dict, clave: str) -> dict[str, list[str]]:
    """case_id por particion_preparacion (conversaciones de desarrollo)."""
    grupos: dict[str, list[str]] = {}
    for c in particiones.get("conversaciones", []):
        grupos.setdefault(c.get("particion_preparacion", "?"), []).append(c["case_id"])
    if clave not in grupos:
        raise ValueError(f"partición {clave!r} sin conversaciones.")
    return grupos


# ---------------------------------------------------------------------------
# Regla condicional exacta de CONFIG §fine_tuning_100
# ---------------------------------------------------------------------------

def decidir_fine_tuning(candidatos: list[dict], baseline_viejo: dict,
                        errores_observables: list[str]) -> dict:
    """¿Corresponde fine-tuning? Regla literal de la configuración.

    `candidatos`: resultados congelados de validación con claves
    `config`, `omisiones_oportunas`, `legitimas_derivadas`.
    `baseline_viejo`: mismo par de conteos del Tito viejo en validación.
    `errores_observables`: errores visibles que justificarían ajustar
    (vacío => no hay qué justificar).

    FT solo si NINGUN candidato conserva o reduce A LA VEZ ambos conteos
    frente al viejo Y hay al menos un error observable. Igualar ambos
    conteos NO obliga a FT (conservar == no ajustar).
    """
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
# Congelamiento: contrato mínimo que ya exige matriz_101
# ---------------------------------------------------------------------------

def validar_congelado(manifiesto: dict, sha_artefacto_real: str,
                      artefacto: dict) -> list[str]:
    """Contrato mínimo del manifiesto congelado. Vacío == válido."""
    errores = []
    if manifiesto.get("artefacto_sha256") != sha_artefacto_real:
        errores.append("artefacto_sha256 no coincide con el artefacto.")
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
    tok = artefacto.get("tokenizador", {})
    if not (tok.get("tokenizer_sha256") and artefacto.get("pesos", {}).get("coef")):
        errores.append("candidato sin hash de tokenizador o sin pesos.")
    if not manifiesto.get("variante"):
        errores.append("manifiesto sin variante declarada.")
    if not manifiesto.get("fuentes") or not all(
            isinstance(manifiesto["fuentes"].get(k), dict)
            for k in ("validacion", "supervision", "auditoria",
                      "particiones", "config")):
        errores.append("manifiesto sin fuentes con hashes "
                       "(validacion/supervision/auditoria/particiones/config).")
    return errores


def verificar_umbral_cli(umbral_congelado: float,
                         umbral_cli: float | None) -> None:
    """Rechazo explícito del override silencioso (contrato matriz_101)."""
    if umbral_cli is not None \
            and float(umbral_cli) != float(umbral_congelado):
        raise ValueError(
            f"--umbral {umbral_cli} no coincide con el umbral congelado "
            f"{umbral_congelado}: sin override silencioso.")


def ids_validacion_conversaciones(particiones: dict) -> list[str]:
    """IDs de validación en orden, con grupos juntos y sin reserva."""
    grupos = grupos_por_particion(particiones, "validacion")
    ids = sorted(grupos["validacion"])
    try:
        from datos_tito import rechazar_reserva
    except ImportError:  # pragma: no cover - respaldo sin el módulo
        def rechazar_reserva(case_ids, particiones=None):  # type: ignore
            mal = [c for c in case_ids if "CV2-T-" in c]
            if mal:
                raise ValueError(f"reserva: {mal}.")
    rechazar_reserva(ids)
    vistos = {c.get("case_id") for c in particiones.get("conversaciones", [])
              if c.get("particion_preparacion") == "validacion"}
    if set(ids) != vistos:
        raise ValueError("validación inconsistente en particiones.")
    return ids


def verificar_puerta_revision(referencias: dict) -> str:
    """Las referencias siguen sin revisión humana: autorización separada."""
    malas = sorted(cid for cid, r in referencias.items()
                   if r.get("revision_humana") not in (False, None))
    if malas:
        raise ValueError(
            "puerta formal intacta: estas referencias figuran con "
            f"revision_humana y no pueden usarse como desarrollo: {malas}.")
    return AUTORIZACION_DESARROLLO


def construir_manifiesto_congelado(seleccion: dict, artefacto_ruta: Path,
                                   artefacto: dict, umbral: float,
                                   variante: str, fuentes: dict,
                                   codigo: dict) -> dict:
    """Manifiesto CANDIDATO-TITO-100: identidad, procedencia y orden temporal."""
    return {
        "issue": 100,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
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
        "fuentes": fuentes,
        "codigo": codigo,
        "semilla": SEMILLA,
        "autorizacion": AUTORIZACION_DESARROLLO,
    }


def construir_manifiesto_bloqueado_ft(decision_error: BloqueoFineTuning,
                                      codigo: dict) -> dict:
    """Registro explícito de FT correspondiente sin rama afinada."""
    return {
        "issue": 100,
        "fecha": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "estado": ESTADO_BLOQUEADO_FT,
        "motivo": str(decision_error),
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


def comparar_sobre_validacion(textos: dict, referencias: dict,
                              etiquetas: dict, puntaje_nuevo,
                              puntaje_viejo, umbral_nuevo: float,
                              umbral_viejo: float = UMBRAL_VIEJO) -> dict:
    """Mismas conversaciones, dos comparadores recargados sin entrenar.

    `textos[cid]`: líneas "A: ..."/"B: ..." (historial con hablantes).
    `puntaje_nuevo(cid, k)` / `puntaje_viejo(cid, k)` -> (p|None, err, ms).
    Métricas conversacionales vía `entrenar_tito_99.evaluar_configuracion`
    y clasificación binaria SOLO sobre prefijos revisados (0/1).
    """
    from entrenar_tito_99 import (evaluar_configuracion,
                                  metricas_prefijos_revisados)
    nuevo = evaluar_configuracion([], textos, referencias, puntaje_nuevo,
                                  umbral_nuevo)
    viejo = evaluar_configuracion([], textos, referencias, puntaje_viejo,
                                  umbral_viejo)
    # evaluar_configuracion itera sorted(textos): textos_val == textos.
    puntajes_nuevo = {cid: c["puntajes"] for c in nuevo["por_caso"]
                      for cid in [c["case_id"]]}
    puntajes_viejo = {cid: c["puntajes"] for c in viejo["por_caso"]
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


def es_reserva(case_id: str) -> bool:
    try:
        from datos_tito import es_identificador_reserva
        return es_identificador_reserva(case_id)
    except ImportError:  # pragma: no cover - respaldo sin el módulo
        return "CV2-T-" in case_id


def evaluar_comprobacion(manifiesto_ruta: Path, artefacto_nuevo_ruta: Path,
                         artefacto_viejo_ruta: Path, textos: dict,
                         referencias: dict, etiquetas: dict,
                         tito_nuevo=None, tito_viejo=None) -> dict:
    """Comprueba el candidato congelado sobre validación (sin fit).

    Recarga ambos comparadores desde disco (los dobles inyectados SOLO
    sirven a pruebas; en producción son Tito99 + TitoReal reales).
    Exige manifiesto en estado congelado, ligado a PARTICIONES vigente,
    y rechaza reserva y conversaciones fuera de validación.
    """
    manifiesto = json.loads(Path(manifiesto_ruta).read_text(encoding="utf-8"))
    if manifiesto.get("estado") == ESTADO_BLOQUEADO_FT:
        raise BloqueoFineTuning(
            "manifiesto bloqueado: FT corresponde pero la rama afinada no "
            "existe. Trabajo faltante en el propio manifiesto.")
    if manifiesto.get("estado") != ESTADO_CONGELADO:
        raise ValueError("sin candidato congelado: correr `congelar` primero "
                         "(congelar ANTES de comprobar).")
    if sha_archivo(artefacto_nuevo_ruta) != manifiesto.get("artefacto_sha256"):
        raise ValueError("el artefacto no coincide con el artefacto_sha256 "
                         "del manifiesto congelado.")
    particiones = cargar_particiones()
    validacion_permitidos = set(ids_validacion_conversaciones(particiones))
    part_man = manifiesto.get("particiones", {})
    if part_man.get("particiones_sha256") != sha_archivo(AQUI / PARTICIONES_NOMBRE):
        raise ValueError("manifiesto desligado de PARTICIONES vigente: "
                         "recongelar antes de comprobar.")
    if set(part_man.get("ids_validacion", [])) != validacion_permitidos:
        raise ValueError("ids_validacion del manifiesto no coinciden con "
                         "PARTICIONES vigente: recongelar.")
    reserva_presente = [c for c in textos if es_reserva(c)]
    if reserva_presente:
        raise ValueError("reserva en comprobación: no se lee ni evalúa "
                         f"({sorted(set(reserva_presente))}).")
    fuera = sorted(set(textos) - validacion_permitidos)
    if fuera:
        raise ValueError("conversaciones fuera de validación: la comprobación "
                         f"no abre las veinte ni otra partición ({fuera}).")
    autorizacion = verificar_puerta_revision(referencias)
    umbral_nuevo = manifiesto["umbral"]
    verificar_umbral_cli(umbral_nuevo, None)
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
    comparacion = comparar_sobre_validacion(
        textos, referencias, etiquetas, puntaje_nuevo, puntaje_viejo,
        float(umbral_nuevo), UMBRAL_VIEJO)
    return {
        "manifiesto": str(manifiesto_ruta),
        "manifiesto_sha256": sha_archivo(manifiesto_ruta),
        "comprobado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "orden_temporal": "comprobación posterior al congelamiento; no se "
                          "reentrena ni se cambia ventana/umbral.",
        "autorizacion": autorizacion,
        "preparacion_nuevo": prep_nuevo,
        "preparacion_viejo": prep_viejo,
        "comparacion": comparacion,
        "limites": ("Ninguna mejora del sistema se infiere solo por Tito: "
                    "la derivación no es alerta y una conversación sin "
                    "derivación no prueba legitimidad."),
    }


# ---------------------------------------------------------------------------
# Reporte regenerable sin nueva inferencia
# ---------------------------------------------------------------------------

def armar_informe_md(comp: dict) -> str:
    """Markdown desde un JSON de comprobación (sin inferencia)."""
    c = comp["comparacion"]
    nuevo, viejo = c["nuevo"], c["viejo"]
    ln: list[str] = [
        "# Comprobación Tito #100 (validación, sin fit)",
        "",
        f"- Manifiesto: `{comp['manifiesto']}` ({comp['manifiesto_sha256'][:12]}…)",
        f"- Comprobado en: {comp['comprobado_en']} (posterior al congelamiento)",
        f"- Umbrales: nuevo {c['umbral_nuevo']} / viejo {c['umbral_viejo']}",
        f"- Autorización: {comp['autorizacion'][:60]}…",
        "",
        "## Conversacional (validación)",
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
    ruta.write_text(json.dumps(contenido, ensure_ascii=False, indent=1),
                    encoding="utf-8")
    md = ruta.with_suffix(".md")
    md.write_text(armar_informe_md(contenido), encoding="utf-8")
    return ruta


def regenerar_md(entrada_json: Path, salida_md: Path | None = None) -> Path:
    """Regenera el .md desde un JSON ya corrido (sin inferencia)."""
    comp = json.loads(Path(entrada_json).read_text(encoding="utf-8"))
    destino = salida_md or Path(entrada_json).with_suffix(".md")
    Path(destino).write_text(armar_informe_md(comp), encoding="utf-8")
    return Path(destino)


# ---------------------------------------------------------------------------
# CLI por etapas: congelar / evaluar / regenerar
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--paso", choices=["congelar", "evaluar", "regenerar"],
                   required=True,
                   help="congelar: decide FT y congela SIN abrir las veinte; "
                        "evaluar: comprueba el congelado sobre validación; "
                        "regenerar: .md desde JSON sin inferencia.")
    p.add_argument("--resultados99", type=Path, default=None,
                   help="evaluación #99 real (congelar).")
    p.add_argument("--artefacto", type=Path, default=None,
                   help="artefacto candidato #99 (congelar).")
    p.add_argument("--manifiesto", type=Path,
                   default=AQUI / MANIFIESTO_CONGELADO_NOMBRE,
                   help="manifiesto congelado (evaluar).")
    p.add_argument("--salida", type=Path, default=None)
    p.add_argument("--entrada", type=Path, default=None,
                   help="JSON de comprobación (regenerar).")
    p.add_argument("--umbral", type=float, default=None,
                   help="solo para coincidir con el congelado; distinto "
                        "se rechaza.")
    args = p.parse_args(argv)
    if args.paso == "regenerar":
        if args.entrada is None:
            print("regenerar exige --entrada JSON.", file=sys.stderr)
            return 2
        print(f"md={regenerar_md(args.entrada, args.salida)}")
        return 0
    if args.paso == "congelar":
        # Preparación: este dispatch NO ejecuta ajuste ni evaluación
        # independiente; el cableado real lo completa el dispatch que tenga
        # los resultados #99. Sin resultados no hay congelamiento que fingir.
        print("congelar: este dispatch es preparatorio (código + tests). "
              "Sin resultados #99 reales no se congela ni se evalúa nada; "
              "ver tests/test_comprobar_tito_100.py para el contrato.")
        return 0
    if args.paso == "evaluar":
        print("evaluar: este dispatch es preparatorio y no ejecuta la "
              "evaluación independiente (política #102 primero, y el "
              "candidato se congela tras la validación). Código listo, "
              "ejecución pendiente de resultados #99.")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())