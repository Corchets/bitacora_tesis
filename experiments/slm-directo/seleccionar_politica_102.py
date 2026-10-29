"""Selección de la política de reconsultas #102 (parte de #95, H4).

Busca y congela la política de reconsultas ANTES de medir las veinte:
candidatas `nuevo_cruce_tras_bajar` con revisión periódica y búsqueda
acotada (periodos 1/3/5, delta 0), seleccionadas SOLO con las diez
conversaciones de validación y `qwen3.5:4b` como modelo de referencia
predeclarado (primero de la lista del issue; no se elige modelo mirando
las veinte). La comparación real posterior (10 modelos × 2 políticas × 20
= 400, en `matriz_102.py`) usa la congelada sin reajustar.

> **Estado: propuesta sin discutir.** La política operativa
> (`nuevo_cruce_tras_bajar` con revisión periódica), la búsqueda acotada
> y el criterio provisional de desarrollo son candidatos vinculados a
> [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental):
> nada de lo que sigue cierra D08 ni adopta 95/5 como meta. El margen
> preventivo final sigue pendiente; este módulo no afirma mejora
> definitiva, solo elige una candidata para medir.

Criterio provisional de desarrollo (para ELEGIR, no para declarar éxito):
detecciones conservadas respecto de la activación permanente, falsas
alarmas no aumentadas y avisos oportunos (`T_A <= T_R` donde exista)
no reducidos, TODO sobre la misma validación con los mismos IDs y
cobertura completa por condición. Se informan los márgenes `L_C` y
cuántas conversaciones carecen de cada referencia. Si ninguna candidata
cumple, no hay ganadora: se congela la exploratoria del desempate ya
escrito como `NO_MEJORA_VALIDACION` (`apta_para_medir=false`, nunca
"ganadora apta") para permitir los 400 como evidencia negativa; sin
mediciones suficientes se bloquea explícito, no se extrapola.

La selección NUNCA consume resultados de las veinte (`comparacion_20`)
ni de #101: `verificar_origen_solo_validacion` rechaza esos IDs antes de
medir. La identidad del candidato #100 (artefacto, manifiesto100,
entrada, umbral, encoder), el prompt, las opciones, el inventario y los
datos de validación quedan predeclarados en el manifiesto de búsqueda
ANTES de la primera inferencia; el congelado verifica identidad exacta
contra lo medido, nunca contra otro candidato.

CLI (medir/congelar/regenerar; medir es la única que infiere, SOLO en
validación con el modelo de referencia):

    python seleccionar_politica_102.py preparar --tito-nuevo-modelo CAND --tito-nuevo-manifest SEL [--salida DIR]
    python seleccionar_politica_102.py medir <manifiesto_busqueda> --tito-nuevo-modelo CAND ...
    python seleccionar_politica_102.py congelar <manifiesto_medida> <candidata> --tito-artefacto CAND --tito-manifest SEL --variante TXT [--salida DIR]
    python seleccionar_politica_102.py regenerar <manifiesto_medida>

Los tests usan `medir_con_fabrica` con dobles, sin modelos ni red.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import casos
import correr
import matriz_101
from filtro_tito import UMBRAL_TITO
from politica_reconsultas import (
    REGLA_NUEVO_CRUCE_TRAS_BAJAR,
    PoliticaReconsultas,
)

AQUI = Path(__file__).resolve().parent
PARTICIONES = AQUI / "PARTICIONES-TITO-2026-10-29.json"
CONFIG_102 = AQUI / "CONFIGURACION-TITO-2026-10-29.json"
DIR_CORRIDAS = AQUI / "corridas"
URL_102 = "http://127.0.0.1:11435"

SEMILLA_102 = 42
# Modelo de referencia predeclarado: primero de la lista del issue #102.
# No se elige mirando las veinte ni mirando resultados de validación.
MODELO_REFERENCIA_102 = "qwen3.5:4b"
REGLA_102 = REGLA_NUEVO_CRUCE_TRAS_BAJAR
DELTA_102 = 0.0
# Búsqueda acotada propuesta (D08 abierta): solo estos periodos.
PERIODOS_CANDIDATOS = (1, 3, 5)

CANDIDATAS_102 = tuple(
    {"nombre": f"reconsultas-p{p}",
     "periodo_revision": p,
     "regla_nueva_evidencia": REGLA_102,
     "delta_minimo": DELTA_102}
    for p in PERIODOS_CANDIDATOS
)
BASELINE_102 = "permanente"

ESTADO_GANADORA = "ganadora_para_medir"
ESTADO_NEGATIVO = "NO_MEJORA_VALIDACION"
ESTADO_BLOQUEADO_MEDICION = "BLOQUEADO_SIN_MEDICION_SUFICIENTE"


def _utc_ahora_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha_archivo(ruta: Path) -> str:
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def validacion_102() -> list[str]:
    """Las diez conversaciones de validación, en orden del manifiesto.

    Solo `particion_preparacion == "validacion"`: nunca las veinte de
    comparación ni la reserva. Cada una con texto y referencia íntegros.
    """
    datos = json.loads(PARTICIONES.read_text(encoding="utf-8"))
    ids = [c["case_id"] for c in datos.get("conversaciones", [])
           if c.get("particion_preparacion") == "validacion"]
    if len(ids) != 10:
        raise ValueError(f"validación incompleta en particiones: {len(ids)} IDs, se exigen 10.")
    respaldo = {c["case_id"]: c for c in datos.get("conversaciones", [])}
    errores: list[str] = []
    for cid in ids:
        ref = casos.cargar_referencia(cid)
        if ref.get("particion") == "test_reservado":
            errores.append(f"{cid}: pertenece a la reserva, no a validación.")
        esp = respaldo[cid]
        for clave, ruta in (("texto_sha256", casos.DIR_TEXTO / f"{cid}.txt"),
                            ("referencia_sha256", casos.DIR_REFERENCIA / f"{cid}.json")):
            if _sha_archivo(ruta) != esp.get(clave):
                errores.append(f"{cid}: deriva de hash en {ruta.name}.")
    if errores:
        raise ValueError("validacion_102 inválida:\n- " + "\n- ".join(errores))
    return ids


def verificar_origen_solo_validacion(ids: list[str]) -> None:
    """Rechaza IDs de comparación (#101/#102) o reserva antes de medir.

    La selección no consume resultados de las veinte ni de #101: cualquier
    mezcla levanta en texto plano en lugar de medirse en silencio.
    """
    validos = set(validacion_102())
    mal: list[str] = []
    for cid in ids:
        if cid in matriz_101.IDS_101:
            mal.append(f"{cid}: pertenece a las veinte de comparación (no se usa para seleccionar).")
        elif cid not in validos:
            try:
                ref = casos.cargar_referencia(cid)
            except ValueError:
                mal.append(f"{cid}: ID desconocido.")
                continue
            if ref.get("particion") == "test_reservado":
                mal.append(f"{cid}: pertenece a la reserva.")
            else:
                mal.append(f"{cid}: fuera de la validación de diez.")
    if mal:
        raise ValueError("origen inválido para la selección:\n- " + "\n- ".join(mal))


def construir_politica(tito, slm, candidata: dict, umbral: float) -> PoliticaReconsultas:
    """Instancia una candidata con la API compatible `evaluar`/`reiniciar`."""
    return PoliticaReconsultas(
        tito, slm, umbral,
        periodo_revision=candidata["periodo_revision"],
        regla_nueva_evidencia=candidata["regla_nueva_evidencia"],
        delta_minimo=candidata["delta_minimo"],
    )


def construir_permanente(tito, slm, umbral: float):
    """Baseline: mismo Tito historial + activación permanente (#101)."""
    return matriz_101.FlujoTitoHistorialSLM(tito, slm, umbral)


def _config_traza(nombre: str, modelo: str, prompt: str, hablantes: str) -> dict:
    return {"config": f"{nombre}|{modelo}|{prompt}|{hablantes}",
            "detector": "tito-slm", "modelo": modelo,
            "prompt": prompt, "hablantes": hablantes}


def medir_con_fabrica_y_trazas(fabricas: dict[str, object], ids: list[str],
                               *, modelo: str = MODELO_REFERENCIA_102,
                               prompt: str = "tarea",
                               hablantes: str = "ab") -> tuple[dict, dict]:
    """Mide baseline y candidatas con detectores frescos por condición.

    `fabricas` mapea nombre → fábrica cero-arg de detector compatible con
    `correr.procesar_caso` (real o doble con `reiniciar`). Devuelve
    `(agregados, trazas)`: un resultado por caso con aviso, oportunidad
    respecto de `T_R`/`T_C`, consultas, evitadas, fallos y costos
    Tito/SLM por separado (sin doble conteo), más las filas crudas por
    actualización con el mismo runner y `correr._fila` (para guardar en
    CSV y regenerar agregados sin nueva inferencia).
    """
    verificar_origen_solo_validacion(ids)
    resultados: dict[str, list[dict]] = {}
    trazas: dict[str, list[dict]] = {}
    for nombre, fabrica in fabricas.items():
        por_caso: list[dict] = []
        filas: list[dict] = []
        cfg = _config_traza(nombre, modelo, prompt, hablantes)
        for cid in ids:
            detector = fabrica()
            lineas = casos.cargar_texto(cid)
            ref = casos.cargar_referencia(cid)
            salidas = list(correr.procesar_caso(detector, lineas, detener_en_aviso=True))
            for n, linea, r, aviso in salidas:
                filas.append(correr._fila(cfg, cid, n, linea, r, aviso))
            aviso = next((n for n, _, _, a in salidas if a), None)
            consultas = sum(1 for _, _, r, _ in salidas
                            if (r.consulta or "") in ("slm_valida", "slm_fallo"))
            evitadas = sum(1 for _, _, r, _ in salidas if (r.consulta or "") == "omitida")
            tr, tc = ref.get("t_r_linea"), ref.get("t_c_linea")
            por_caso.append({
                "case_id": cid,
                "clase": ref["clase"],
                "t_r_linea": tr,
                "t_c_linea": tc,
                "aviso": aviso,
                "deteccion": bool(aviso) and ref["clase"] == "vishing",
                "falsa_alarma": bool(aviso) and ref["clase"] in casos.LEGITIMAS,
                "oportuno": (aviso is not None and tr is not None and aviso <= tr)
                            if ref["clase"] == "vishing" and tr is not None else None,
                "margen_l_r": (tr - aviso) if (aviso is not None and tr is not None) else None,
                "margen_l_c": (tc - aviso) if (aviso is not None and tc is not None) else None,
                "consultas_slm": consultas,
                "evitadas_slm": evitadas,
                "fallos_tito": sum(1 for _, _, r, _ in salidas if (r.tito_error or "").strip()),
                "fallos_slm": sum(1 for _, _, r, _ in salidas if r.consulta == "slm_fallo"),
                "tito_ms": round(sum(r.tito_ms or 0.0 for _, _, r, _ in salidas), 1),
                "slm_ms": round(sum(r.slm_ms or 0.0 for _, _, r, _ in salidas), 1),
            })
        resultados[nombre] = por_caso
        trazas[nombre] = filas
    return resultados, trazas


def medir_con_fabrica(fabricas: dict[str, object], ids: list[str]) -> dict[str, list[dict]]:
    """Agregados por conversación (envoltorio sin trazas; ver `..._y_trazas`)."""
    resultados, _ = medir_con_fabrica_y_trazas(fabricas, ids)
    return resultados


def _resumen_condicion(filas: list[dict]) -> dict:
    det = sum(1 for f in filas if f["deteccion"])
    fa = sum(1 for f in filas if f["falsa_alarma"])
    oport = [f for f in filas if f["oportuno"] is True]
    return {
        "detecciones": det,
        "falsas_alarmas": fa,
        "oportunos": len(oport),
        "oportunos_evaluables": sum(1 for f in filas if f["oportuno"] is not None),
        "consultas_slm": sum(f["consultas_slm"] for f in filas),
        "fallos_tito": sum(f["fallos_tito"] for f in filas),
        "fallos_slm": sum(f["fallos_slm"] for f in filas),
        "margenes_l_c": [f["margen_l_c"] for f in filas if f["margen_l_c"] is not None],
        "sin_t_c": sum(1 for f in filas
                       if f["aviso"] is not None and f["t_c_linea"] is None),
        "sin_t_r_vishing": sum(1 for f in filas
                               if f["clase"] == "vishing" and f["t_r_linea"] is None),
    }


def seleccionar(resultados: dict[str, list[dict]],
                candidatas: tuple[dict, ...] = CANDIDATAS_102,
                baseline: str = BASELINE_102) -> dict:
    """Aplica el criterio provisional y elige la ganadora (o ninguna).

    Elegible = cobertura completa con los mismos IDs del baseline,
    detecciones >= baseline, falsas alarmas <= baseline y oportunos >=
    baseline, todo sobre validación. Desempate: menos consultas SLM,
    luego menor periodo, luego nombre (determinista). La tabla clasifica
    explícitamente cada candidata: `elegible`, `no_elegible`,
    `cobertura_incompleta` (con faltantes/sobrantes) o `sin_medicion`;
    los fallos Tito/SLM se informan por fila sin ocultar.

    Sin elegible no hay ganadora: se congela la exploratoria del mismo
    desempate ya escrito como `NO_MEJORA_VALIDACION` (`apta_para_medir`
    en falso, nunca "ganadora apta") para permitir los 400 como evidencia
    negativa. Sin mediciones suficientes se bloquea explícito, sin
    extrapolar ni ampliar la búsqueda en silencio.
    """
    if baseline not in resultados:
        raise ValueError(f"falta el baseline {baseline!r} en los resultados.")
    base_filas = resultados[baseline]
    base_ids = [f["case_id"] for f in base_filas]
    base = _resumen_condicion(base_filas)
    tabla: list[dict] = []
    elegibles: list[tuple[int, int, str]] = []
    for cand in candidatas:
        nombre = cand["nombre"]
        if nombre not in resultados:
            tabla.append({"candidata": nombre, "cobertura": "sin_medicion",
                          "estado": "sin_medicion"})
            continue
        filas = resultados[nombre]
        ids_c = [f["case_id"] for f in filas]
        en_base, en_cand = set(base_ids), set(ids_c)
        faltantes = sorted(en_base - en_cand)
        sobrantes = sorted(en_cand - en_base)
        fila = {"candidata": nombre, **_resumen_condicion(filas),
                "cobertura": ("completa" if not faltantes and not sobrantes
                              and len(ids_c) == len(base_ids)
                              else "incompleta"),
                "faltantes_vs_baseline": faltantes,
                "sobrantes_vs_baseline": sobrantes,
                "cumple_criterio": False,
                "periodo_revision": cand["periodo_revision"],
                "delta_minimo": cand["delta_minimo"],
                "regla": cand["regla_nueva_evidencia"]}
        if fila["cobertura"] != "completa":
            fila["estado"] = "cobertura_incompleta"
            fila["motivo_estado"] = (
                f"cobertura incompleta vs baseline "
                f"({len(ids_c)}/{len(base_ids)} casos; "
                f"faltantes={faltantes or 'ninguno'}; "
                f"sobrantes={sobrantes or 'ninguno'}): una candidata "
                "incompleta no puede aparentar conservación ni menor costo.")
            tabla.append(fila)
            continue
        r = fila
        cumple = (r["detecciones"] >= base["detecciones"]
                  and r["falsas_alarmas"] <= base["falsas_alarmas"]
                  and r["oportunos"] >= base["oportunos"])
        fila["cumple_criterio"] = cumple
        fila["estado"] = "elegible" if cumple else "no_elegible"
        tabla.append(fila)
        if cumple:
            elegibles.append((r["consultas_slm"], cand["periodo_revision"], nombre))
    elegibles.sort()
    comun = {
        "baseline": baseline,
        "resumen_baseline": base,
        "ids_baseline": list(base_ids),
        "tabla": tabla,
        "advertencia_d08": ("Criterio provisional de desarrollo; el margen preventivo "
                            "final y la meta 95/5 siguen abiertos en D08. No afirma "
                            "mejora definitiva."),
    }
    if elegibles:
        ganadora = elegibles[0][2]
        motivo = (f"{ganadora} conserva detecciones ({base['detecciones']}), "
                  f"no aumenta falsas alarmas ({base['falsas_alarmas']}) ni reduce "
                  f"oportunos ({base['oportunos']}), con menos consultas SLM, "
                  f"sobre los mismos {len(base_ids)} IDs de validación.")
        return {**comun, "ganadora": ganadora, "motivo": motivo,
                "resultado_negativo": False, "estado": ESTADO_GANADORA,
                "apta_para_medir": True, "candidata_exploratoria": None}
    completas = [f for f in tabla if f.get("cobertura") == "completa"]
    if not completas:
        return {**comun, "ganadora": None, "candidata_exploratoria": None,
                "resultado_negativo": True, "estado": ESTADO_BLOQUEADO_MEDICION,
                "apta_para_medir": False,
                "motivo": ("Sin mediciones suficientes sobre la misma validación "
                           "con cobertura completa: bloqueo explícito, no se "
                           "extrapola ni se amplía la búsqueda en silencio.")}
    completas.sort(key=lambda f: (f["consultas_slm"], f["periodo_revision"],
                                  f["candidata"]))
    exploratoria = completas[0]["candidata"]
    return {**comun, "ganadora": None, "candidata_exploratoria": exploratoria,
            "resultado_negativo": True, "estado": ESTADO_NEGATIVO,
            "apta_para_medir": False,
            "motivo": ("Ninguna candidata cumple el criterio provisional sobre "
                       f"validación con cobertura completa. Se congela la exploratoria "
                       f"{exploratoria} (mismo desempate ya escrito) como "
                       "NO_MEJORA_VALIDACION/no_adoptar para permitir los 400 "
                       "como evidencia negativa: nunca es ganadora apta ni se "
                       "cambia el criterio, y no se amplía la búsqueda en silencio.")}


def identidad_tito_desde_archivos(artefacto_ruta: Path,
                                  manifest_ruta: Path) -> dict:
    """Identidad file-based del candidato #100 (sin cargar el encoder).

    Lee artefacto + manifiesto congelado y exige el contrato mínimo
    (formato conocido, entrada `historial_acumulado`, umbral en (0, 1],
    encoder idéntico en ambas caras). No infiere ni calienta nada.
    """
    try:
        arte = json.loads(Path(artefacto_ruta).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise ValueError(f"candidato nuevo ilegible ({artefacto_ruta}): {e}.")
    formato = arte.get("formato", "")
    if isinstance(formato, str) and formato.startswith("tito-100"):
        raise ValueError(f"formato {formato} sin loader acordado: pendiente.")
    if formato not in matriz_101.FORMATOS_NUEVO_CONOCIDOS:
        raise ValueError(f"formato de candidato desconocido: {formato!r}.")
    try:
        sel = json.loads(Path(manifest_ruta).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise ValueError(f"manifiesto de selección ilegible ({manifest_ruta}): {e}.")
    if _sha_archivo(Path(artefacto_ruta)) != sel.get("artefacto_sha256"):
        raise ValueError("el artefacto no coincide con el artefacto_sha256 "
                         "del manifiesto congelado #100.")
    for fuente, entrada in (("artefacto", arte.get("entrada")),
                            ("manifiesto", sel.get("entrada"))):
        if entrada != matriz_101.ENTRADA_NUEVO_EXIGIDA:
            raise ValueError(f"entrada del candidato en {fuente}: {entrada!r}; "
                             f"se exige {matriz_101.ENTRADA_NUEVO_EXIGIDA!r}.")
    umbral = sel.get("umbral")
    if not isinstance(umbral, (int, float)) or not 0 < float(umbral) <= 1:
        raise ValueError("el manifiesto no trae un umbral seleccionado en (0, 1].")
    if arte.get("encoder", {}) != sel.get("encoder", {}) or not sel.get("encoder", {}).get("id"):
        raise ValueError("identidad del encoder sin fijar entre artefacto y manifiesto.")
    return {
        "artefacto": str(artefacto_ruta),
        "artefacto_sha256": _sha_archivo(Path(artefacto_ruta)),
        "manifiesto100": str(manifest_ruta),
        "manifiesto100_sha256": _sha_archivo(Path(manifest_ruta)),
        "entrada": matriz_101.ENTRADA_NUEVO_EXIGIDA,
        "umbral": float(umbral),
        "encoder": dict(sel.get("encoder", {})),
        "variante": sel.get("variante", ""),
    }


def manifiesto_busqueda(ids: list[str], funcionales: dict) -> dict:
    """Manifiesto de búsqueda ANTES de inferir: qué se va a medir y con qué.

    `funcionales` trae la predeclaración fijada antes de la primera
    inferencia: identidad del Tito (`identidad_tito`), prompt y huella,
    opciones (hablantes, num_ctx, seed, timeout, hardware), modelo de
    referencia y su razón. La búsqueda queda cerrada acá: no se amplía
    en silencio después de medir.
    """
    ident = dict(funcionales.get("identidad_tito", {}))
    return {
        "etapa": "seleccion-102-busqueda",
        "issue": 102,
        "semilla": SEMILLA_102,
        "modelo_referencia": MODELO_REFERENCIA_102,
        "modelo_referencia_razon": "primero de la lista del issue #102 (predeclarado, no elegido mirando datos)",
        "candidatas": [dict(c) for c in CANDIDATAS_102],
        "baseline": BASELINE_102,
        "busqueda_cerrada": True,
        "criterio_provisional": ("detecciones conservadas, falsas alarmas no aumentadas, "
                                "oportunos (T_A <= T_R donde exista) no reducidos, "
                                "cobertura completa con los mismos IDs; "
                                "informa márgenes L_C y referencias ausentes; D08 sigue abierta"),
        "casos_validacion": list(ids),
        "identidad_tito": ident,
        "prompt": funcionales.get("prompt", "tarea"),
        "prompt_huella": funcionales.get("prompt_huella", ""),
        "opciones": funcionales.get("opciones", {}),
        "inventario_referencia_previsto": funcionales.get("inventario_referencia", {}),
        "funcionales": {"modelo_referencia": MODELO_REFERENCIA_102,
                        "casos": list(ids), "semilla": SEMILLA_102,
                        **{k: v for k, v in funcionales.items()
                           if k not in ("identidad_tito",)}},
        "particiones_sha256": _sha_archivo(PARTICIONES),
        "configuracion_sha256": _sha_archivo(CONFIG_102),
        "codigo": correr.info_codigo(),
        "maquina": correr.info_maquina(),
        "inicio": _utc_ahora_iso(),
    }


def _guardar_json(ruta: Path, contenido: dict) -> None:
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, ruta)


def ruta_trazas_csv(manifiesto_ruta: Path) -> Path:
    """CSV de trazas crudas hermano del manifiesto (`_actualizaciones.csv`)."""
    texto = str(manifiesto_ruta)
    if texto.endswith("_manifiesto.json"):
        texto = texto[: -len("_manifiesto.json")]
    return Path(texto + "_actualizaciones.csv")


def guardar_trazas_csv(ruta: Path, trazas: dict[str, list[dict]]) -> int:
    """Trazas crudas por actualización (transaccional: tmp + replace)."""
    filas = [f for nombre in sorted(trazas) for f in trazas[nombre]]
    tmp = ruta.with_name(ruta.name + ".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
        w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in correr.COLUMNAS})
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, ruta)
    return len(filas)


def leer_trazas_csv(ruta: Path) -> dict[str, list[dict]]:
    """Trazas crudas agrupadas por condición (nombre de fábrica)."""
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        lector = csv.DictReader(f)
        if lector.fieldnames != list(correr.COLUMNAS):
            raise ValueError(f"traza con columnas inesperadas: {ruta}.")
        trazas: dict[str, list[dict]] = {}
        for fila in lector:
            cfg = fila.get("config", "")
            nombre = cfg.split("|")[0] if cfg else ""
            trazas.setdefault(nombre, []).append(dict(fila))
    return trazas


def _verificar_identidad_con_medicion(manifiesto: dict, tito_info: dict) -> None:
    """El freeze congela EXACTAMENTE lo medido, no otro candidato.

    Si el manifiesto trae `identidad_tito` predeclarada (flujo CLI real),
    cada campo debe coincidir: artefacto, manifiesto100, entrada, umbral,
    encoder, prompt y opciones. Un candidato distinto con igual encoder y
    umbral se rechaza acá, no se le atribuyen las mediciones.
    """
    ident = manifiesto.get("identidad_tito") or {}
    if not ident:
        return  # Manifiesto legado sin predeclaración: chequeo mínimo abajo.
    for clave in ("artefacto_sha256", "manifiesto100_sha256", "entrada",
                  "umbral", "encoder"):
        esperado, real = ident.get(clave), tito_info.get(clave)
        if clave == "umbral":
            if abs(float(esperado or -1) - float(real or -2)) > 1e-12:
                raise ValueError("el umbral a congelar difiere del predeclarado "
                                 "antes de medir: no se congela otro candidato.")
        elif esperado != real:
            raise ValueError(f"{clave} a congelar difiere del predeclarado antes "
                             "de medir: no se congela otro candidato.")
    if ident.get("variante") != tito_info.get("variante"):
        raise ValueError("la variante a congelar difiere de la predeclarada.")
    pre = manifiesto.get("preinferencia") or {}
    if pre.get("prompt_huella") and tito_info.get("prompt_huella") is not None \
            and pre["prompt_huella"] != tito_info["prompt_huella"]:
        raise ValueError("el prompt a congelar difiere del medido.")


def congelar_politica(manifiesto: dict, seleccion: dict, nombre: str,
                      tito_info: dict) -> dict:
    """Congela la candidata junto al candidato #100 y el contrato común.

    Solo congela la ganadora medida o la exploratoria del resultado
    negativo (`NO_MEJORA_VALIDACION`): jamás otra candidata ni un
    criterio cambiado. Expone el contrato común con #100 (`tito`,
    `politica`, `congelado_en` UTC con zona, `seleccion_solo_validacion`)
    y conserva los alias históricos `tito_congelado`/`politica_ganadora`.
    """
    nombres = [c["nombre"] for c in manifiesto.get("candidatas", [])]
    if nombre not in nombres:
        raise ValueError(f"{nombre!r} no es una candidata de la búsqueda {nombres}.")
    if seleccion.get("ganadora") == nombre:
        modo, apta, negativo = ESTADO_GANADORA, True, False
    elif seleccion.get("resultado_negativo") and \
            seleccion.get("candidata_exploratoria") == nombre:
        modo, apta, negativo = ESTADO_NEGATIVO, False, True
    else:
        raise ValueError(f"{nombre!r} no es la ganadora ni la exploratoria "
                         "del resultado negativo: no se congela otra candidata "
                         "ni se cambia el criterio.")
    for clave in ("artefacto_sha256", "entrada", "umbral", "encoder", "variante"):
        if not tito_info.get(clave):
            raise ValueError(f"tito_info sin {clave!r}: no se congela sin identidad del candidato #100.")
    if tito_info.get("entrada") != matriz_101.ENTRADA_NUEVO_EXIGIDA:
        raise ValueError("el candidato a congelar no usa historial_acumulado.")
    if tito_info["encoder"] != tito_info.get("encoder_artefacto"):
        raise ValueError("el encoder del manifiesto difiere del encoder del artefacto.")
    _verificar_identidad_con_medicion(manifiesto, tito_info)
    cand = next(c for c in manifiesto["candidatas"] if c["nombre"] == nombre)
    politica_canonica = {
        "nombre": nombre,
        "periodo_actualizaciones": cand["periodo_revision"],
        "regla_nueva_evidencia": cand["regla_nueva_evidencia"],
        "delta_score": cand["delta_minimo"],
    }
    tito_canonico = {
        "artefacto_sha256": tito_info["artefacto_sha256"],
        "manifiesto100_sha256": tito_info.get("manifiesto100_sha256", ""),
        "entrada": tito_info["entrada"],
        "umbral": tito_info["umbral"],
        "encoder": dict(tito_info["encoder"]),
    }
    return {
        "etapa": "seleccion-102-congelada",
        "issue": 102,
        "semilla": SEMILLA_102,
        "seleccion_solo_validacion": True,
        "congelado_en": _utc_ahora_iso(),
        "tito": tito_canonico,
        "politica": politica_canonica,
        "modo": modo,
        "apta_para_medir": apta,
        "resultado_negativo": negativo,
        "motivo": seleccion.get("motivo", ""),
        "tabla_seleccion": seleccion.get("tabla", []),
        "resumen_baseline": seleccion.get("resumen_baseline", {}),
        "politica_ganadora": {"nombre": nombre,
                              "periodo_revision": cand["periodo_revision"],
                              "regla_nueva_evidencia": cand["regla_nueva_evidencia"],
                              "delta_minimo": cand["delta_minimo"]},
        "tito_congelado": {**dict(tito_info),
                           "manifiesto100_sha256": tito_info.get("manifiesto100_sha256", "")},
        "busqueda_sha256": hashlib.sha256(
            json.dumps(manifiesto, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "traza_actualizaciones": manifiesto.get("traza_actualizaciones", ""),
        "casos_validacion": list(manifiesto.get("casos_validacion", [])),
        "prompt_congelado": manifiesto.get("prompt", ""),
        "advertencia_d08": seleccion.get("advertencia_d08", ""),
    }


def verificar_congelado(congelado: dict, tito_artefacto: Path,
                        tito_manifest: Path) -> dict:
    """Verifica el congelado contra el artefacto #100 real antes de medir.

    Exige el contrato común canónico (`tito`, `politica`,
    `seleccion_solo_validacion`, `congelado_en` UTC con zona) además de
    la identidad histórica. Acepta los alias legados cuando el canónico
    está presente y coincide.
    """
    sel = matriz_101.resolver_tito_nuevo(tito_artefacto, tito_manifest, None)
    _tito, _prep, umbral, _variante = sel
    if congelado.get("seleccion_solo_validacion") is not True:
        raise ValueError("el congelado no declara seleccion_solo_validacion=true.")
    momento = congelado.get("congelado_en", "")
    try:
        instante = datetime.fromisoformat(str(momento))
    except (ValueError, TypeError):
        raise ValueError("el congelado no trae congelado_en ISO válido.")
    if instante.tzinfo is None:
        raise ValueError("el congelado no trae congelado_en con zona UTC.")
    fr = congelado.get("tito_congelado", {})
    if abs(float(fr.get("umbral", -1)) - float(umbral)) > 1e-12:
        raise ValueError("el umbral del artefacto difiere del congelado.")
    if _sha_archivo(tito_artefacto) != fr.get("artefacto_sha256"):
        raise ValueError("el artefacto #100 difiere del congelado.")
    if not fr.get("variante") or not congelado.get("congelado_en"):
        raise ValueError("el congelado no trae variante ni congelado_en ISO (interfaz estable #100).")
    tito_c = congelado.get("tito", {})
    if tito_c.get("artefacto_sha256") != fr.get("artefacto_sha256"):
        raise ValueError("el bloque tito canónico difiere del tito_congelado.")
    if tito_c.get("manifiesto100_sha256") != _sha_archivo(tito_manifest):
        raise ValueError("el manifiesto100_sha256 no coincide con el manifiesto #100 a medir.")
    pol = congelado.get("politica", {})
    for clave in ("periodo_actualizaciones", "regla_nueva_evidencia", "delta_score"):
        if clave not in pol:
            raise ValueError(f"el congelado no trae politica.{clave} (contrato común #100).")
    if pol.get("regla_nueva_evidencia") not in ("nuevo_cruce_tras_bajar",):
        raise ValueError(f"regla congelada desconocida: {pol.get('regla_nueva_evidencia')!r}.")
    if pol.get("periodo_actualizaciones") not in (1, 3, 5):
        raise ValueError("periodo congelado fuera de la búsqueda acotada.")
    if float(pol.get("delta_score", -1)) != 0.0:
        raise ValueError("delta congelado distinto de 0.")
    legado = congelado.get("politica_ganadora", {})
    if legado and (legado.get("periodo_revision") != pol["periodo_actualizaciones"]
                   or legado.get("delta_minimo") != pol["delta_score"]
                   or legado.get("regla_nueva_evidencia") != pol["regla_nueva_evidencia"]):
        raise ValueError("el alias politica_ganadora difiere del bloque politica canónico.")
    PoliticaReconsultas.__new__(PoliticaReconsultas)  # la clase existe y es importable
    return {"ok": True, "umbral": umbral,
            "politica": pol.get("nombre", legado.get("nombre", "?")),
            "modo": congelado.get("modo", "?")}


def _etiqueta_segura(texto: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_-]", "_", texto).strip("_")[:40]


def _opciones_cli(args) -> dict:
    extra: dict = {}
    if getattr(args, "solo_cpu", False):
        extra["num_gpu"] = 0
    if getattr(args, "hilos", None):
        extra["num_thread"] = args.hilos
    if getattr(args, "num_batch", None):
        extra["num_batch"] = args.num_batch
    return {
        "hablantes": args.hablantes,
        "num_ctx": args.num_ctx,
        "seed": args.seed,
        "timeout": args.timeout,
        "hardware": extra or None,
        "url": args.url,
    }


def _cmd_preparar(args) -> int:
    try:
        ids = validacion_102()
    except ValueError as e:
        sys.exit(f"{e}\nSin validación no hay predeclaración.")
    if not args.salida.is_dir():
        sys.exit(f"--salida debe ser una carpeta existente (no se crean dirs): {args.salida}.")
    try:
        ident = identidad_tito_desde_archivos(args.tito_nuevo_modelo,
                                              args.tito_nuevo_manifest)
    except ValueError as e:
        sys.exit(f"Candidato nuevo rechazado (sin inferencia): {e}")
    import detectores
    try:
        prompt_txt = detectores.cargar_prompt(args.prompt)
        prompt_huella = detectores.huella(prompt_txt)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"Prompt rechazado: {e}.")
    nombre = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H%M%S")
    if args.etiqueta:
        nombre += f"_{_etiqueta_segura(args.etiqueta)}"
    man = manifiesto_busqueda(ids, {
        "identidad_tito": ident,
        "prompt": args.prompt,
        "prompt_huella": prompt_huella,
        "opciones": _opciones_cli(args),
        "modelo_referencia": MODELO_REFERENCIA_102,
    })
    _guardar_json(args.salida / f"{nombre}_102-seleccion_manifiesto.json", man)
    print(f"Búsqueda predeclarada (sin inferencia): {nombre}_102-seleccion "
          f"({len(ids)} validación, {len(CANDIDATAS_102)} candidatas, "
          f"ref {MODELO_REFERENCIA_102}, tito {ident['artefacto_sha256'][:12]}…).")
    return 0


def _cmd_medir(args) -> int:
    from cliente_ollama import ClienteOllama, ErrorOllama
    from detectores import DetectorSLM, cargar_prompt, esquema_de
    from detectores import huella as huella_texto
    man = json.loads(args.busqueda.read_text(encoding="utf-8"))
    if man.get("etapa") != "seleccion-102-busqueda":
        sys.exit("el manifiesto no es una búsqueda de selección-102.")
    if not man.get("busqueda_cerrada"):
        sys.exit("búsqueda no cerrada: no se mide sin predeclaración.")
    try:
        ids = validacion_102()
    except ValueError as e:
        sys.exit(str(e))
    if list(man.get("casos_validacion", [])) != ids:
        sys.exit("la validación actual difiere de la preparada: no se mezclan búsquedas.")
    # Identidad file-based ANTES de abrir runtime: otro candidato no mide.
    try:
        ident_actual = identidad_tito_desde_archivos(args.tito_nuevo_modelo,
                                                     args.tito_nuevo_manifest)
    except ValueError as e:
        sys.exit(f"Candidato nuevo rechazado: {e}")
    ident_pre = man.get("identidad_tito", {})
    for clave in ("artefacto_sha256", "manifiesto100_sha256", "entrada",
                  "umbral", "encoder"):
        if ident_actual.get(clave) != ident_pre.get(clave):
            sys.exit(f"Candidato cambiado desde la predeclaración ({clave}): "
                     "no se mide otro candidato con esta búsqueda.")
    try:
        prompt_txt = cargar_prompt(args.prompt)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"Prompt rechazado: {e}.")
    if huella_texto(prompt_txt) != man.get("prompt_huella"):
        sys.exit("el prompt actual difiere del predeclarado: no se mide con otro prompt.")
    if _opciones_cli(args) != man.get("opciones"):
        sys.exit("las opciones actuales difieren de las predeclaradas: no se mide con otras.")
    try:
        tito, prep_nuevo, umbral, _var = matriz_101.resolver_tito_nuevo(
            args.tito_nuevo_modelo, args.tito_nuevo_manifest, None)
    except (matriz_101.TitoNuevoNoDisponible, ValueError) as e:
        sys.exit(f"Candidato nuevo rechazado: {e}")
    if abs(float(umbral) - float(ident_pre.get("umbral", -1))) > 1e-12:
        sys.exit("el umbral resuelto difiere del predeclarado.")
    cliente = ClienteOllama(args.url, args.timeout)
    try:
        inv = matriz_101.inventario_modelo(cliente, MODELO_REFERENCIA_102)
    except (ErrorOllama, LookupError) as e:
        sys.exit(f"Sin modelo de referencia no hay selección ({e}).")
    try:
        version = cliente.version()
    except ErrorOllama as e:
        sys.exit(f"Sin runtime no hay medición ({e}).")
    # Predeclaración persistida ANTES de la primera inferencia.
    esquema = esquema_de(args.prompt)
    man["preinferencia"] = {
        "inventario_referencia": inv,
        "ollama_version": version,
        "prompt": args.prompt,
        "prompt_huella": huella_texto(prompt_txt),
        "opciones": _opciones_cli(args),
        "umbral": umbral,
        "preparacion_tito": prep_nuevo,
        "codigo": correr.info_codigo(),
        "maquina": correr.info_maquina(),
        "persistido_en": _utc_ahora_iso(),
    }
    _guardar_json(args.busqueda, man)
    extra = man["preinferencia"]["opciones"]["hardware"]
    tito_ref = [tito]

    def fabrica_permanente():
        slm = DetectorSLM(cliente, MODELO_REFERENCIA_102, prompt_txt,
                          args.hablantes, args.num_ctx, args.seed,
                          extra=extra, esquema=esquema)
        return construir_permanente(tito_ref[0], slm, umbral)

    fabricas: dict[str, object] = {BASELINE_102: fabrica_permanente}
    for cand in man.get("candidatas", CANDIDATAS_102):
        def _fab(c=cand):
            slm = DetectorSLM(cliente, MODELO_REFERENCIA_102, prompt_txt,
                              args.hablantes, args.num_ctx, args.seed,
                              extra=extra, esquema=esquema)
            return construir_politica(tito_ref[0], slm, c, umbral)
        fabricas[cand["nombre"]] = _fab
    t0 = time.perf_counter()
    resultados, trazas = medir_con_fabrica_y_trazas(
        fabricas, ids, modelo=MODELO_REFERENCIA_102,
        prompt=args.prompt, hablantes=args.hablantes)
    csv_ruta = ruta_trazas_csv(args.busqueda)
    n_filas = guardar_trazas_csv(csv_ruta, trazas)
    sel = seleccionar(resultados)
    man = json.loads(args.busqueda.read_text(encoding="utf-8"))
    man["medicion"] = {"duracion_s": round(time.perf_counter() - t0, 1),
                       "filas_trazas": n_filas,
                       "traza_csv": csv_ruta.name}
    man["resultados_validacion"] = resultados
    man["seleccion"] = sel
    man["traza_actualizaciones"] = csv_ruta.name
    _guardar_json(args.busqueda, man)
    elegida = sel.get("ganadora") or sel.get("candidata_exploratoria")
    print(f"Selección sobre validación (ref {MODELO_REFERENCIA_102}): "
          f"estado={sel['estado']} elegida={elegida}. {sel['motivo']}")
    return 0


def _cmd_congelar(args) -> int:
    man = json.loads(args.busqueda.read_text(encoding="utf-8"))
    if man.get("etapa") != "seleccion-102-busqueda":
        sys.exit("el manifiesto no es una búsqueda de selección-102.")
    if "seleccion" not in man or "resultados_validacion" not in man:
        sys.exit("la búsqueda aún no tiene medición: corré `medir` antes.")
    if not man.get("traza_actualizaciones"):
        sys.exit("la búsqueda no trae trazas crudas: no se congela sin traza.")
    try:
        tito_json = json.loads(args.tito_artefacto.read_text(encoding="utf-8"))
        sel_json = json.loads(args.tito_manifest.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        sys.exit(f"artefacto o manifiesto ilegible: {e}.")
    try:
        medido_umbral = float(man["identidad_tito"]["umbral"])
    except (KeyError, TypeError, ValueError):
        sys.exit("la búsqueda no trae identidad predeclarada: no se congela.")
    tito_info = {"artefacto_sha256": _sha_archivo(args.tito_artefacto),
                 "manifiesto100_sha256": _sha_archivo(args.tito_manifest),
                 "entrada": tito_json.get("entrada"),
                 "umbral": medido_umbral,
                 "encoder": sel_json.get("encoder", {}),
                 "encoder_artefacto": tito_json.get("encoder", {}),
                 "variante": args.variante,
                 "prompt_huella": (man.get("preinferencia") or {}).get("prompt_huella")}
    try:
        fro = congelar_politica(man, man["seleccion"], args.candidata, tito_info)
    except ValueError as e:
        sys.exit(f"Congelado rechazado: {e}")
    if not args.salida.is_dir():
        sys.exit(f"--salida debe ser una carpeta existente: {args.salida}.")
    _guardar_json(args.salida / f"{args.busqueda.stem}_congelada.json", fro)
    print(f"Política congelada: {args.candidata} modo={fro['modo']} "
          f"(busqueda {man.get('inicio', '?')}).")
    return 0


def _cmd_regenerar(args) -> int:
    man = json.loads(args.busqueda.read_text(encoding="utf-8"))
    if man.get("etapa") != "seleccion-102-busqueda":
        sys.exit("el manifiesto no es una búsqueda de selección-102.")
    if "resultados_validacion" not in man or "seleccion" not in man:
        sys.exit("la búsqueda aún no tiene medición: nada que regenerar.")
    csv_ruta = ruta_trazas_csv(args.busqueda)
    if not csv_ruta.exists():
        sys.exit(f"sin trazas crudas ({csv_ruta.name}): no se regenera sin traza.")
    trazas = leer_trazas_csv(csv_ruta)
    ids = list(man.get("casos_validacion", []))
    if not ids:
        sys.exit("la búsqueda no trae casos_validacion.")
    verificar_origen_solo_validacion(ids)
    regen = agregados_desde_trazas(trazas, ids)
    if set(regen) != set(man["resultados_validacion"]):
        sys.exit("la traza no cubre las mismas condiciones medidas: no se regenera.")
    for nombre, filas in regen.items():
        viejas = {f["case_id"]: f for f in man["resultados_validacion"][nombre]}
        for f in filas:
            v = viejas.get(f["case_id"])
            if v is None or any(f.get(k) != v.get(k) for k in f):
                sys.exit(f"la traza no reproduce los agregados de {nombre}: "
                         "no se regenera sobre una medición distinta.")
    sel = seleccionar(regen, tuple(man.get("candidatas", CANDIDATAS_102)))
    vieja = man["seleccion"]
    if (sel.get("ganadora"), sel.get("candidata_exploratoria")) != \
            (vieja.get("ganadora"), vieja.get("candidata_exploratoria")):
        sys.exit("la traza reproduce otra selección: no se regenera en silencio.")
    man["resultados_validacion"] = regen
    man["seleccion"] = sel
    _guardar_json(args.busqueda, man)
    elegida = sel.get("ganadora") or sel.get("candidata_exploratoria")
    print(f"Selección regenerada desde trazas (sin inferencia): "
          f"estado={sel['estado']} elegida={elegida}.")
    return 0


def _agregar_flags_medicion(p) -> None:
    p.add_argument("--prompt", default="tarea")
    p.add_argument("--hablantes", default="ab")
    p.add_argument("--num-ctx", type=int, default=4096)
    p.add_argument("--seed", type=int, default=SEMILLA_102)
    p.add_argument("--timeout", type=float, default=120.0)
    p.add_argument("--solo-cpu", action="store_true")
    p.add_argument("--hilos", type=int, default=None)
    p.add_argument("--num-batch", type=int, default=None)
    p.add_argument("--url", default=URL_102)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    pp = sub.add_parser("preparar", help="predeclaración de búsqueda (sin inferencia)")
    pp.add_argument("--salida", type=Path, default=DIR_CORRIDAS)
    pp.add_argument("--etiqueta", default="")
    pp.add_argument("--tito-nuevo-modelo", type=Path, default=None, required=True)
    pp.add_argument("--tito-nuevo-manifest", type=Path, default=None, required=True)
    _agregar_flags_medicion(pp)
    ps = sub.add_parser("medir", aliases=["seleccionar"],
                        help="mide SOLO validación con el modelo de referencia y elige")
    ps.add_argument("busqueda", type=Path)
    ps.add_argument("--tito-nuevo-modelo", type=Path, default=None, required=True)
    ps.add_argument("--tito-nuevo-manifest", type=Path, default=None, required=True)
    _agregar_flags_medicion(ps)
    pc = sub.add_parser("congelar", help="congela la candidata medida con el candidato #100")
    pc.add_argument("busqueda", type=Path)
    pc.add_argument("candidata", type=str)
    pc.add_argument("--tito-artefacto", type=Path, required=True)
    pc.add_argument("--tito-manifest", type=Path, required=True)
    pc.add_argument("--variante", type=str, required=True,
                    help="variante del candidato #100 (p. ej. #99-congelada)")
    pc.add_argument("--salida", type=Path, default=DIR_CORRIDAS)
    pr = sub.add_parser("regenerar", help="recalcula agregados+selección desde trazas (sin inferencia)")
    pr.add_argument("busqueda", type=Path)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    if args.comando == "preparar":
        return _cmd_preparar(args)
    if args.comando in ("medir", "seleccionar"):
        return _cmd_medir(args)
    if args.comando == "congelar":
        return _cmd_congelar(args)
    if args.comando == "regenerar":
        return _cmd_regenerar(args)
    return 2


if __name__ == "__main__":
    sys.exit(main())


def agregados_desde_trazas(trazas: dict[str, list[dict]],
                           ids: list[str]) -> dict[str, list[dict]]:
    """Regenera los agregados por caso desde filas crudas (sin inferencia).

    Misma aritmética que `medir_con_fabrica_y_trazas`; la referencia
    (clase, `T_R`/`T_C`) se relee de disco. Si la traza no reproduce los
    agregados medidos, la regeneración debe rechazar, no ajustar.
    """
    resultados: dict[str, list[dict]] = {}
    for nombre, filas in trazas.items():
        por_caso: list[dict] = []
        por_id: dict[str, list[dict]] = {}
        for f in filas:
            por_id.setdefault(f.get("case_id", ""), []).append(f)
        for cid in ids:
            fs = sorted(por_id.get(cid, []), key=lambda f: int(f.get("linea", 0)))
            if not fs:
                continue
            ref = casos.cargar_referencia(cid)
            aviso = next((int(f["linea"]) for f in fs if f.get("aviso") == "true"), None)
            consultas = sum(1 for f in fs if (f.get("consulta") or "") in ("slm_valida", "slm_fallo"))
            evitadas = sum(1 for f in fs if (f.get("consulta") or "") == "omitida")

            def _num(f, clave):
                try:
                    return float(f.get(clave) or 0.0)
                except (TypeError, ValueError):
                    return 0.0

            tr, tc = ref.get("t_r_linea"), ref.get("t_c_linea")
            por_caso.append({
                "case_id": cid,
                "clase": ref["clase"],
                "t_r_linea": tr,
                "t_c_linea": tc,
                "aviso": aviso,
                "deteccion": bool(aviso) and ref["clase"] == "vishing",
                "falsa_alarma": bool(aviso) and ref["clase"] in casos.LEGITIMAS,
                "oportuno": (aviso is not None and tr is not None and aviso <= tr)
                            if ref["clase"] == "vishing" and tr is not None else None,
                "margen_l_r": (tr - aviso) if (aviso is not None and tr is not None) else None,
                "margen_l_c": (tc - aviso) if (aviso is not None and tc is not None) else None,
                "consultas_slm": consultas,
                "evitadas_slm": evitadas,
                "fallos_tito": sum(1 for f in fs if (f.get("tito_error") or "").strip()),
                "fallos_slm": sum(1 for f in fs if f.get("consulta") == "slm_fallo"),
                "tito_ms": round(sum(_num(f, "tito_ms") for f in fs), 1),
                "slm_ms": round(sum(_num(f, "slm_ms") for f in fs), 1),
            })
        resultados[nombre] = por_caso
    return resultados
