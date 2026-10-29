"""Selección de la política de reconsultas #102 (parte de #95, H4).

Busca y congela la política de reconsultas ANTES de medir las veinte:
candidatas `nuevo_cruce_tras_bajar` con revisión periódica y búsqueda
acotada (periodos 1/3/5, delta 0), seleccionadas SOLO con las diez
conversaciones de validación y `qwen3.5:4b` como modelo de referencia
predeclarado (primero de la lista del issue; no se elige modelo mirando
las veinte). La comparación real posterior (10 modelos × 2 políticas × 20
= 400, en `matriz_102.py`) usa la ganadora congelada sin reajustar.

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
no reducidos. Se informan los márgenes `L_C = T_C - T_A` y cuántas
conversaciones carecen de cada referencia. Si ninguna candidata cumple,
no hay ganadora: se propone otra configuración en un artefacto ANTES de
medir, nunca se elige en silencio ni se atribuye aprobación formal.

La selección NUNCA consume resultados de las veinte (`comparacion_20`)
ni de #101: `verificar_origen_solo_validacion` rechaza esos IDs antes de
medir. La ganadora y su configuración quedan congeladas ANTES de evaluar
las veinte (`congelar`), junto a la identidad del candidato #100
principal (artefacto, entrada A/B, umbral); solo varía la política.

CLI separados (sin inferencia salvo `seleccionar`, que mide SOLO
validación con el modelo de referencia):

    python seleccionar_politica_102.py preparar [--salida DIR] [--etiqueta TXT]
    python seleccionar_politica_102.py seleccionar <manifiesto_busqueda> [...]
    python seleccionar_politica_102.py congelar <manifiesto_busqueda> <ganadora>
        --tito-artefacto JSON --tito-manifest JSON [--salida DIR]

`seleccionar` exige el Tito #100 congelado y Ollama con el modelo de
referencia; no abre la reserva ni las veinte. Los tests usan
`medir_con_fabrica` con dobles, sin modelos ni red.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime
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


def medir_con_fabrica(fabricas: dict[str, object], ids: list[str]) -> dict[str, list[dict]]:
    """Mide baseline y candidatas con detectores frescos por condición.

    `fabricas` mapea nombre → fábrica cero-arg de detector compatible con
    `correr.procesar_caso` (real o doble con `reiniciar`). No abre red ni
    modelos: la fábrica decide. Devuelve un resultado por caso con aviso,
    oportunidad respecto de `T_R`/`T_C`, consultas, evitadas, fallos y
    costos Tito/SLM por separado (sin doble conteo).
    """
    verificar_origen_solo_validacion(ids)
    resultados: dict[str, list[dict]] = {}
    for nombre, fabrica in fabricas.items():
        por_caso: list[dict] = []
        for cid in ids:
            detector = fabrica()
            lineas = casos.cargar_texto(cid)
            ref = casos.cargar_referencia(cid)
            salidas = list(correr.procesar_caso(detector, lineas, detener_en_aviso=True))
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

    Elegible = detecciones >= baseline, falsas alarmas <= baseline y
    oportunos >= baseline, todo sobre validación. Desempate: menos
    consultas SLM, luego menor periodo, luego nombre (determinista).
    Sin elegible no hay ganadora: se informa el motivo y la próxima
    configuración a proponer ANTES de medir, sin elegir en silencio.
    """
    if baseline not in resultados:
        raise ValueError(f"falta el baseline {baseline!r} en los resultados.")
    base = _resumen_condicion(resultados[baseline])
    tabla: list[dict] = []
    elegibles: list[tuple[int, int, str]] = []
    for cand in candidatas:
        nombre = cand["nombre"]
        if nombre not in resultados:
            tabla.append({"candidata": nombre, "estado": "sin_medicion"})
            continue
        r = _resumen_condicion(resultados[nombre])
        cumple = (r["detecciones"] >= base["detecciones"]
                  and r["falsas_alarmas"] <= base["falsas_alarmas"]
                  and r["oportunos"] >= base["oportunos"])
        fila = {"candidata": nombre, **r,
                "cumple_criterio": cumple,
                "periodo_revision": cand["periodo_revision"],
                "delta_minimo": cand["delta_minimo"],
                "regla": cand["regla_nueva_evidencia"]}
        tabla.append(fila)
        if cumple:
            elegibles.append((r["consultas_slm"], cand["periodo_revision"], nombre))
    elegibles.sort()
    if elegibles:
        ganadora = elegibles[0][2]
        motivo = (f"{ganadora} conserva detecciones ({base['detecciones']}), "
                  f"no aumenta falsas alarmas ({base['falsas_alarmas']}) ni reduce "
                  f"oportunos ({base['oportunos']}), con menos consultas SLM.")
    else:
        ganadora = None
        motivo = ("Ninguna candidata cumple el criterio provisional sobre validación: "
                  "proponer otra configuración en un artefacto ANTES de medir "
                  "(no se elige en silencio ni se mide con la mejor parcial).")
    return {
        "baseline": baseline,
        "resumen_baseline": base,
        "tabla": tabla,
        "ganadora": ganadora,
        "motivo": motivo,
        "advertencia_d08": ("Criterio provisional de desarrollo; el margen preventivo "
                            "final y la meta 95/5 siguen abiertos en D08. No afirma "
                            "mejora definitiva."),
    }


def manifiesto_busqueda(ids: list[str], funcionales: dict) -> dict:
    """Manifiesto de búsqueda ANTES de inferir: qué se va a medir y con qué."""
    return {
        "etapa": "seleccion-102-busqueda",
        "issue": 102,
        "semilla": SEMILLA_102,
        "modelo_referencia": MODELO_REFERENCIA_102,
        "modelo_referencia_razon": "primero de la lista del issue #102 (predeclarado, no elegido mirando datos)",
        "candidatas": [dict(c) for c in CANDIDATAS_102],
        "baseline": BASELINE_102,
        "criterio_provisional": ("detecciones conservadas, falsas alarmas no aumentadas, "
                                "oportunos (T_A <= T_R donde exista) no reducidos; "
                                "informa márgenes L_C y referencias ausentes; D08 sigue abierta"),
        "casos_validacion": list(ids),
        "funcionales": funcionales,
        "particiones_sha256": _sha_archivo(PARTICIONES),
        "configuracion_sha256": _sha_archivo(CONFIG_102),
        "codigo": correr.info_codigo(),
        "maquina": correr.info_maquina(),
        "inicio": datetime.now().isoformat(timespec="seconds"),
    }


def _guardar_json(ruta: Path, contenido: dict) -> None:
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(json.dumps(contenido, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, ruta)


def congelar_politica(manifiesto: dict, seleccion: dict, ganadora: str,
                      tito_info: dict) -> dict:
    """Congela la ganadora junto al candidato #100 principal.

    Solo varía la política: el Tito (artefacto, entrada A/B, umbral,
    identidad del encoder), el prompt y el runtime quedan fijados acá y
    `matriz_102.py` los exige idénticos antes de medir las veinte.
    """
    nombres = [c["nombre"] for c in manifiesto.get("candidatas", [])]
    if ganadora not in nombres:
        raise ValueError(f"{ganadora!r} no es una candidata de la búsqueda {nombres}.")
    if seleccion.get("ganadora") != ganadora:
        raise ValueError("la ganadora a congelar no coincide con la selección medida.")
    for clave in ("artefacto_sha256", "entrada", "umbral", "encoder", "variante"):
        if not tito_info.get(clave):
            raise ValueError(f"tito_info sin {clave!r}: no se congela sin identidad del candidato #100.")
    if tito_info.get("entrada") != matriz_101.ENTRADA_NUEVO_EXIGIDA:
        raise ValueError("el candidato a congelar no usa historial_acumulado.")
    if tito_info["encoder"] != tito_info.get("encoder_artefacto"):
        raise ValueError("el encoder del manifiesto difiere del encoder del artefacto.")
    cand = next(c for c in manifiesto["candidatas"] if c["nombre"] == ganadora)
    return {
        "etapa": "seleccion-102-congelada",
        "issue": 102,
        "semilla": SEMILLA_102,
        "politica_ganadora": dict(cand),
        "motivo": seleccion.get("motivo", ""),
        "tabla_seleccion": seleccion.get("tabla", []),
        "resumen_baseline": seleccion.get("resumen_baseline", {}),
        "tito_congelado": dict(tito_info),
        "busqueda_sha256": hashlib.sha256(
            json.dumps(manifiesto, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
        "advertencia_d08": seleccion.get("advertencia_d08", ""),
        "congelado_en": datetime.now().isoformat(timespec="seconds"),
    }


def verificar_congelado(congelado: dict, tito_artefacto: Path,
                        tito_manifest: Path) -> dict:
    """Verifica el congelado contra el artefacto #100 real antes de medir."""
    sel = matriz_101.resolver_tito_nuevo(tito_artefacto, tito_manifest, None)
    _tito, _prep, umbral, _variante = sel
    fr = congelado.get("tito_congelado", {})
    if abs(float(fr.get("umbral", -1)) - float(umbral)) > 1e-12:
        raise ValueError("el umbral del artefacto difiere del congelado.")
    if _sha_archivo(tito_artefacto) != fr.get("artefacto_sha256"):
        raise ValueError("el artefacto #100 difiere del congelado.")
    if not fr.get("variante") or not congelado.get("congelado_en"):
        raise ValueError("el congelado no trae variante ni congelado_en ISO (interfaz estable #100).")
    pol = congelado.get("politica_ganadora", {})
    PoliticaReconsultas.__new__(PoliticaReconsultas)  # la clase existe y es importable
    if pol.get("regla_nueva_evidencia") not in ("nuevo_cruce_tras_bajar",):
        raise ValueError(f"regla congelada desconocida: {pol.get('regla_nueva_evidencia')!r}.")
    return {"ok": True, "umbral": umbral, "politica": pol.get("nombre", pol)}


def _etiqueta_segura(texto: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_-]", "_", texto).strip("_")[:40]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    pp = sub.add_parser("preparar", help="manifiesto de búsqueda (sin inferencia)")
    pp.add_argument("--salida", type=Path, default=DIR_CORRIDAS)
    pp.add_argument("--etiqueta", default="")
    ps = sub.add_parser("seleccionar", help="mide SOLO validación con el modelo de referencia y elige")
    ps.add_argument("busqueda", type=Path)
    ps.add_argument("--url", default=URL_102)
    ps.add_argument("--prompt", default="tarea")
    ps.add_argument("--hablantes", default="ab")
    ps.add_argument("--num-ctx", type=int, default=4096)
    ps.add_argument("--seed", type=int, default=SEMILLA_102)
    ps.add_argument("--tito-nuevo-modelo", type=Path, default=None, required=True)
    ps.add_argument("--tito-nuevo-manifest", type=Path, default=None, required=True)
    ps.add_argument("--tito-nuevo-umbral", type=float, default=None)
    pc = sub.add_parser("congelar", help="congela la ganadora con el candidato #100")
    pc.add_argument("busqueda", type=Path)
    pc.add_argument("ganadora", type=str)
    pc.add_argument("--tito-artefacto", type=Path, required=True)
    pc.add_argument("--tito-manifest", type=Path, required=True)
    pc.add_argument("--variante", type=str, required=True,
                    help="variante del candidato #100 (p. ej. #99-congelada)")
    pc.add_argument("--salida", type=Path, default=DIR_CORRIDAS)
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    if args.comando == "preparar":
        ids = validacion_102()
        if not args.salida.is_dir():
            sys.exit(f"--salida debe ser una carpeta existente (no se crean dirs): {args.salida}.")
        nombre = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if args.etiqueta:
            nombre += f"_{_etiqueta_segura(args.etiqueta)}"
        prefijo = f"{nombre}_102-seleccion"
        funcionales = {"modelo_referencia": MODELO_REFERENCIA_102,
                       "casos": ids, "semilla": SEMILLA_102}
        man = manifiesto_busqueda(ids, funcionales)
        _guardar_json(args.salida / f"{prefijo}_manifiesto.json", man)
        print(f"Búsqueda preparada (sin inferencia): {prefijo} "
              f"({len(ids)} validación, {len(CANDIDATAS_102)} candidatas, ref {MODELO_REFERENCIA_102}).")
        return 0

    if args.comando == "seleccionar":
        from cliente_ollama import ClienteOllama, ErrorOllama
        from detectores import DetectorSLM, cargar_prompt, esquema_de, huella as huella_texto
        man = json.loads(args.busqueda.read_text(encoding="utf-8"))
        if man.get("etapa") != "seleccion-102-busqueda":
            sys.exit("el manifiesto no es una búsqueda de selección-102.")
        ids = validacion_102()
        if list(man.get("casos_validacion", [])) != ids:
            sys.exit("la validación actual difiere de la preparada: no se mezclan búsquedas.")
        try:
            tito, _prep, umbral, _var = matriz_101.resolver_tito_nuevo(
                args.tito_nuevo_modelo, args.tito_nuevo_manifest, args.tito_nuevo_umbral)
        except (matriz_101.TitoNuevoNoDisponible, ValueError) as e:
            sys.exit(f"Candidato nuevo rechazado: {e}")
        cliente = ClienteOllama(args.url, 120.0)
        try:
            inv = matriz_101.inventario_modelo(cliente, MODELO_REFERENCIA_102)
        except (ErrorOllama, LookupError) as e:
            sys.exit(f"Sin modelo de referencia no hay selección ({e}).")
        prompt_txt, esquema = cargar_prompt(args.prompt), esquema_de(args.prompt)
        extra = None
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
        resultados = medir_con_fabrica(fabricas, ids)
        sel = seleccionar(resultados)
        man["medicion"] = {"inventario_referencia": inv,
                           "prompt": args.prompt, "prompt_huella": huella_texto(prompt_txt),
                           "hablantes": args.hablantes, "num_ctx": args.num_ctx,
                           "umbral": umbral,
                           "duracion_s": round(time.perf_counter() - t0, 1)}
        man["resultados_validacion"] = resultados
        man["seleccion"] = sel
        _guardar_json(args.busqueda, man)
        print(f"Selección sobre validación (ref {MODELO_REFERENCIA_102}): "
              f"ganadora={sel['ganadora']}. {sel['motivo']}")
        return 0

    if args.comando == "congelar":
        man = json.loads(args.busqueda.read_text(encoding="utf-8"))
        if "seleccion" not in man:
            sys.exit("la búsqueda aún no tiene selección medida: corré `seleccionar` antes.")
        try:
            tito_json = json.loads(args.tito_artefacto.read_text(encoding="utf-8"))
            sel_json = json.loads(args.tito_manifest.read_text(encoding="utf-8"))
        except (ValueError, OSError) as e:
            sys.exit(f"artefacto o manifiesto ilegible: {e}.")
        tito_info = {"artefacto_sha256": _sha_archivo(args.tito_artefacto),
                     "entrada": tito_json.get("entrada"),
                     "umbral": man["medicion"]["umbral"],
                     "encoder": sel_json.get("encoder", {}),
                     "encoder_artefacto": tito_json.get("encoder", {}),
                     "variante": args.variante}
        fro = congelar_politica(man, man["seleccion"], args.ganadora, tito_info)
        if not args.salida.is_dir():
            sys.exit(f"--salida debe ser una carpeta existente: {args.salida}.")
        _guardar_json(args.salida / f"{args.busqueda.stem}_congelada.json", fro)
        print(f"Política congelada: {args.ganadora} (busqueda {man.get('inicio', '?')}).")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
