"""Matriz #102: activación permanente vs reconsultas congeladas (#95, H4).

Diez modelos × dos políticas × veinte conversaciones = 400 recorridos
operativos. Reutiliza el runner existente (`correr.procesar_caso`,
detectores, `ClienteOllama`, `calentar`, `_fila`) y los ayudantes de
`matriz_101` (casos, inventario, traza transaccional, cobertura), sin un
pipeline experimental paralelo y sin cambiar la CLI histórica.

Condiciones por modelo (misma muestra, mismo runtime, mismo prompt):
  permanente   Tito nuevo → SLM con activación permanente (idéntica a la
               condición `tito-nuevo` de #101: mismo candidato #100,
               misma entrada historial A/B, mismo umbral).
  reconsultas  Mismo Tito, entrada, umbral, prompt e indicio, con la
               política ganadora congelada en `seleccionar_politica_102.py`
               (cierre tras negativa válida + reapertura configurada).

Solo varía la política: la variación observada corresponde a la consulta,
no al Tito. Ambas terminan al primer aviso válido (incluso en legítimas);
sin aviso llegan hasta el final. Solo el SLM avisa; un error técnico de
Tito deriva por fail-open sin fabricar sospecha; error o salida inválida
del SLM no cierra y se reintenta en la actualización siguiente.

Reuso de #101: las 200 celdas `tito-nuevo` de una corrida #101 pueden
reutilizarse como `permanente` SOLO si artefactos, datos, prompt,
runtime, configuración y procedimiento coinciden
(`verificar_reuso_101`); con procedencia explícita en el manifiesto. Si
algo difiere, se miden ambas condiciones. Nunca se achica el denominador
global 400; lo reutilizado y lo medido quedan distinguidos.

Inventario antes de medir: tag exacto, digest, cuantización y versión de
Ollama por modelo; sin `latest`, alias ni sustituciones. Archivos planos
con prefijo de corrida dentro de `corridas/` (ya existente):
`<pref>_manifiesto.json`, `<pref>_actualizaciones.csv`. Reanudar por
prefijo; la traza parcial se retira y se remide sin duplicar filas ni
costos.

Uso:
    python matriz_102.py medir --politica-congelada <frozen.json> \\
        --tito-nuevo-modelo candidato.json --tito-nuevo-manifest sel.json
    python matriz_102.py medir --modelos qwen3.5:4b --casos CV2-D-V-BANCO-001
    python matriz_102.py medir --reanudar corridas/2026-10-29_HHMMSS_102
        --politica-congelada <frozen.json> [...iguales flags...]

Después: python informe_102.py regenerar <prefijo|carpeta>.
"""

from __future__ import annotations

import argparse
import csv
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
from cliente_ollama import ClienteOllama, ErrorOllama
from detectores import DetectorSLM, cargar_prompt, esquema_de
from filtro_tito import FlujoTitoSLM
from politica_reconsultas import PoliticaReconsultas
from seleccionar_politica_102 import SEMILLA_102

AQUI = Path(__file__).resolve().parent
DIR_CORRIDAS = AQUI / "corridas"

MODELOS_102 = matriz_101.MODELOS_101
IDS_102 = matriz_101.IDS_101
URL_102 = matriz_101.URL_101

CONDICIONES_102 = ("permanente", "reconsultas")
ESPERADOS_GLOBALES_102 = len(MODELOS_102) * len(CONDICIONES_102) * len(IDS_102)
assert ESPERADOS_GLOBALES_102 == 400


def casos_102() -> list[str]:
    """Las mismas veinte aprobadas de #101, verificadas contra particiones."""
    return matriz_101.casos_101()


def nombre_config(condicion: str, modelo: str, prompt: str, hablantes: str) -> str:
    return f"{condicion}|{modelo}|{prompt}|{hablantes}"


def plan_pares(modelos: list[str], condiciones: list[str],
               ids: list[str]) -> list[tuple[str, str, str]]:
    """Un recorrido por (modelo, política, caso). Completa: 400."""
    return [(m, c, i) for m in modelos for c in condiciones for i in ids]


def politica_congelada_valida(ruta: Path) -> dict:
    """La congelada de la selección, con parámetros explícitos.

    Acepta el bloque canónico `politica` (contrato común con #100) y el
    alias histórico `politica_ganadora`; si traen ambos deben coincidir.
    Exige `seleccion_solo_validacion=true` y `congelado_en` UTC con zona.
    Una congelada `NO_MEJORA_VALIDACION` también es válida acá: mide las
    400 como evidencia negativa (nunca como ganadora apta).
    """
    try:
        fro = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise ValueError(f"política congelada ilegible ({ruta}): {e}.")
    if fro.get("etapa") != "seleccion-102-congelada":
        raise ValueError(f"{ruta} no es un congelado de selección-102.")
    if fro.get("seleccion_solo_validacion") is not True:
        raise ValueError("política sin seleccion_solo_validacion=true: "
                         "solo se mide lo elegido con validación.")
    try:
        momento = datetime.fromisoformat(str(fro.get("congelado_en", "")))
    except (ValueError, TypeError):
        raise ValueError("política sin congelado_en ISO válido.")
    if momento.tzinfo is None:
        raise ValueError("política sin congelado_en con zona UTC.")
    canon = fro.get("politica", {})
    legado = fro.get("politica_ganadora", {})
    periodo = canon.get("periodo_actualizaciones", legado.get("periodo_revision"))
    regla = canon.get("regla_nueva_evidencia", legado.get("regla_nueva_evidencia"))
    delta = canon.get("delta_score", legado.get("delta_minimo", -1))
    if regla not in ("nuevo_cruce_tras_bajar",):
        raise ValueError(f"regla congelada desconocida: {regla!r}.")
    if periodo not in (1, 3, 5):
        raise ValueError(f"periodo congelado fuera de la búsqueda acotada: {periodo!r}.")
    if float(delta) != 0.0:
        raise ValueError(f"delta congelado distinto de 0: {delta!r}.")
    if canon and legado and (
            legado.get("periodo_revision") != canon.get("periodo_actualizaciones")
            or legado.get("delta_minimo") != canon.get("delta_score")
            or legado.get("regla_nueva_evidencia") != canon.get("regla_nueva_evidencia")):
        raise ValueError("politica_ganadora difiere del bloque politica canónico.")
    return fro


def construir_detectores(modelo: str, prompt_txt: str, variante: str, hablantes: str,
                         cliente: ClienteOllama, num_ctx: int, seed: int,
                         extra: dict | None, esquema: dict,
                         tito_nuevo, umbral_nuevo: float, politica: dict,
                         ) -> list[tuple[dict, object]]:
    """Las dos políticas de un modelo sobre la misma base SLM."""
    slm = DetectorSLM(cliente, modelo, prompt_txt, hablantes, num_ctx, seed,
                      extra=extra, esquema=esquema)
    detectores = [({"config": nombre_config("permanente", modelo, variante, hablantes),
                    "detector": "tito-slm", "modelo": modelo, "prompt": variante,
                    "hablantes": hablantes},
                   matriz_101.FlujoTitoHistorialSLM(tito_nuevo, slm, umbral_nuevo))]
    recon = PoliticaReconsultas(
        tito_nuevo, slm, umbral_nuevo,
        periodo_revision=politica["periodo_revision"],
        regla_nueva_evidencia=politica["regla_nueva_evidencia"],
        delta_minimo=politica["delta_minimo"])
    detectores.append(
        ({"config": nombre_config("reconsultas", modelo, variante, hablantes),
          "detector": "tito-slm", "modelo": modelo, "prompt": variante,
          "hablantes": hablantes}, recon))
    return detectores


def huella_funcional(parametros: dict) -> str:
    return hashlib.sha256(
        json.dumps(parametros, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def cobertura_102(bloqueos_modelo: dict, bloqueo_politica: str,
                  triples_planificados: list[tuple[str, str, str]],
                  completados: set[tuple[str, str, str]]) -> dict:
    """Cobertura contra el denominador global 10×2×20 = 400, con causas."""
    planificados = set(triples_planificados)
    globales = set(plan_pares(list(MODELOS_102), list(CONDICIONES_102), list(IDS_102)))
    faltantes = []
    for m, c, i in sorted(globales):
        if (m, c, i) in completados:
            continue
        if m in bloqueos_modelo:
            causa = "modelo_bloqueado"
        elif c == "reconsultas" and bloqueo_politica:
            causa = "politica-pendiente"
        elif (m, c, i) not in planificados:
            causa = "no-planificado-subset"
        else:
            causa = "pendiente-medicion"
        faltantes.append({"modelo": m, "condicion": c, "caso": i, "causa": causa})
    return {"esperados_globales": ESPERADOS_GLOBALES_102,
            "planificados": len(planificados),
            "completados": len(completados),
            "pendientes": ESPERADOS_GLOBALES_102 - len(completados),
            "matriz_completa": len(completados) == ESPERADOS_GLOBALES_102,
            "faltantes": faltantes}


CAMPOS_REUSO = ("modelos", "casos", "prompt", "prompt_huella", "hablantes",
                "num_ctx", "seed", "url", "timeout", "hardware",
                "ollama_version", "particiones_sha256",
                "configuracion_sha256")

CAMPOS_PROCEDIMIENTO = ("politica_aviso", "modo_termino",
                        "columnas_traza_sha256")


def verificar_reuso_101(manifiesto_101: dict, funcionales_102: dict) -> tuple[bool, list[str]]:
    """¿Pueden reusarse las celdas `tito-nuevo` de #101 como `permanente`?

    Exige igualdad en modelos (orden incluido), casos y sus huellas,
    prompt y su huella, hablantes, num_ctx, seed, URL y versión de Ollama,
    inventario por modelo (digest, cuantización) y bloque tito-nuevo
    (artefacto sha, entrada historial, umbral). El procedimiento se
    compara con las huellas explícitas de
    `matriz_101.huellas_procedimiento` (la misma función en ambas
    corridas): hardware (CPU/GPU), timeout, columnas de la traza y código
    distintos bloquean el reuso. Devuelve (ok, motivos); si algo difiere
    hay que medir ambas condiciones.
    """
    motivos: list[str] = []
    f101 = manifiesto_101.get("funcionales", {})
    for campo in CAMPOS_REUSO:
        if f101.get(campo) != funcionales_102.get(campo):
            motivos.append(f"funcionales.{campo} difiere "
                           f"({f101.get(campo)!r} vs {funcionales_102.get(campo)!r}).")
    if list(f101.get("modelos", [])) != list(funcionales_102.get("modelos", [])):
        motivos.append("el orden o conjunto de modelos difiere.")
    tn101 = f101.get("tito_nuevo", {})
    tn102 = funcionales_102.get("tito_nuevo", {})
    for campo in ("sha256", "entrada", "umbral"):
        if tn101.get(campo) != tn102.get(campo):
            motivos.append(f"tito_nuevo.{campo} difiere "
                            f"({tn101.get(campo)!r} vs {tn102.get(campo)!r}).")
    inv101 = manifiesto_101.get("ollama", {}).get("modelos", {})
    inv102 = funcionales_102.get("inventario", {})
    for modelo in funcionales_102.get("modelos", []):
        a, b = inv101.get(modelo, {}), inv102.get(modelo, {})
        for campo in ("digest", "cuantizacion", "tag"):
            if a.get(campo) != b.get(campo):
                motivos.append(f"inventario {modelo}.{campo} difiere.")
        if a.get("version", manifiesto_101.get("ollama", {}).get("version")) != \
                funcionales_102.get("ollama_version"):
            motivos.append(f"versión de Ollama para {modelo} difiere.")
    p101 = f101.get("procedimiento", {})
    p102 = funcionales_102.get("procedimiento", {})
    if not p101 or not p102:
        motivos.append("procedimiento sin huellas explícitas en una de las corridas.")
    else:
        for campo in CAMPOS_PROCEDIMIENTO:
            if p101.get(campo) != p102.get(campo):
                motivos.append(f"procedimiento.{campo} difiere "
                               f"({p101.get(campo)!r} vs {p102.get(campo)!r}).")
        if (p101.get("codigo") or {}).get("commit") != \
                (p102.get("codigo") or {}).get("commit"):
            motivos.append("procedimiento.codigo.commit difiere entre corridas.")
    if manifiesto_101.get("politica") != correr.POLITICA:
        motivos.append("la corrida 101 no usó aviso único hasta el aviso.")
    if manifiesto_101.get("modo_termino") != correr.MODO_OPERATIVO:
        motivos.append("la corrida 101 no terminó al primer aviso.")
    return (not motivos), motivos


def resolver_reuso_101(ruta_manifiesto_101: Path, funcionales_102: dict,
                       csv_102: Path, modelos_ok: list[str],
                       ids: list[str]) -> tuple[set, dict]:
    """Reuso 101 verificado o rechazo explícito para medir ambas.

    Devuelve (importados, registro). Si las huellas no coinciden, no se
    importa nada y el registro documenta los motivos: la matriz mide
    ambas condiciones sin reducir el global 400 ni ocultar procedencia.
    """
    try:
        man101 = json.loads(Path(ruta_manifiesto_101).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise ValueError(f"Manifiesto 101 ilegible: {e}.")
    ok, motivos = verificar_reuso_101(man101, funcionales_102)
    if not ok:
        return set(), {
            "desde": str(ruta_manifiesto_101),
            "reusado": False,
            "triples_importados": 0,
            "motivos": motivos,
            "codigo_101": man101.get("codigo", {}),
            "nota": ("procedencia incompatible: NO se reusa; se miden "
                     "ambas condiciones sin reducir el global 400 ni "
                     "ocultar la procedencia."),
        }
    base101 = Path(ruta_manifiesto_101)
    for suf in ("_manifiesto.json",):
        if base101.name.endswith(suf):
            csv101 = base101.parent / (base101.name[: -len(suf)] + "_actualizaciones.csv")
            break
    else:
        csv101 = base101.parent / "actualizaciones.csv"
    importados = importar_permanente_desde_101(csv101, csv_102, modelos_ok, ids)
    return importados, {
        "desde": str(ruta_manifiesto_101),
        "reusado": True,
        "triples_importados": len(importados),
        "codigo_101": man101.get("codigo", {}),
        "nota": "celdas permanente reusadas de tito-nuevo #101 con huellas coincidentes",
    }


def importar_permanente_desde_101(csv_101: Path, csv_102: Path,
                                  modelos: list[str], ids: list[str]) -> set[tuple[str, str, str]]:
    """Copia celdas `tito-nuevo` completas de #101 como `permanente`.

    Solo triples con secuencia única y contigua (vía `estado_traza`);
    reescribe el prefijo de config `tito-nuevo|` → `permanente|` y agrega
    con un solo header y descarga durable. Devuelve los triples
    importados. La procedencia queda en el manifiesto, no en las filas.
    """
    filas_101 = matriz_101._leer_filas_csv(csv_101)
    totales = {cid: len(casos.cargar_texto(cid)) for cid in ids}
    por_triple: dict[tuple[str, str, str], list[dict]] = {}
    for f in filas_101:
        if (f.get("config", "")).startswith("tito-nuevo|"):
            por_triple.setdefault(
                (f["config"].split("|")[1], "tito-nuevo", f["case_id"]), []).append(f)
    importados: set[tuple[str, str, str]] = set()
    nuevas: list[dict] = []
    for (modelo, _cond, cid), fs in sorted(por_triple.items()):
        if modelo not in modelos or cid not in ids:
            continue
        completados, canonicas = matriz_101.estado_traza(fs, totales)
        clave = (modelo, "tito-nuevo", cid)
        if clave not in completados:
            continue
        for f in sorted(canonicas, key=lambda f: int(f["linea"])):
            g = dict(f)
            g["config"] = "permanente|" + f["config"].split("|", 1)[1]
            nuevas.append(g)
        importados.add((modelo, "permanente", cid))
    if nuevas:
        matriz_101.agregar_filas(csv_102, nuevas)
    return importados


def resolver_corrida_102(ruta: Path) -> dict:
    """Resuelve una corrida 102 por prefijo (布局 igual que #101)."""
    corrida = matriz_101.resolver_corrida(ruta)
    manifiesto = json.loads(corrida["manifiesto"].read_text(encoding="utf-8"))
    if manifiesto.get("matriz") != "matriz-102":
        raise ValueError(f"{ruta} no es una corrida matriz-102.")
    return corrida


def _guardar_manifiesto(ruta: Path, manifiesto: dict) -> None:
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, ruta)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="comando", required=True)
    m = sub.add_parser("medir", help="mide la matriz 10×2×20 (o un subconjunto declarado parcial)")
    m.add_argument("--modelos", default=",".join(MODELOS_102))
    m.add_argument("--casos", default="")
    m.add_argument("--url", default=URL_102)
    m.add_argument("--prompt", default="tarea")
    m.add_argument("--hablantes", default="ab")
    m.add_argument("--num-ctx", type=int, default=4096)
    m.add_argument("--seed", type=int, default=SEMILLA_102)
    m.add_argument("--timeout", type=float, default=120.0)
    m.add_argument("--solo-cpu", action="store_true")
    m.add_argument("--hilos", type=int)
    m.add_argument("--num-batch", type=int)
    m.add_argument("--tito-nuevo-modelo", type=Path, default=None)
    m.add_argument("--tito-nuevo-manifest", type=Path, default=None)
    m.add_argument("--tito-nuevo-umbral", type=float, default=None)
    m.add_argument("--politica-congelada", type=Path, default=None)
    m.add_argument("--reutilizar-101", type=Path, default=None,
                   help="manifiesto de una corrida matriz-101 para reusar celdas permanente (verificado)")
    m.add_argument("--salida", type=Path, default=DIR_CORRIDAS)
    m.add_argument("--etiqueta", default="")
    m.add_argument("--reanudar", type=Path, default=None)
    m.add_argument("--detalle", action="store_true")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    try:
        ids = casos_102()
    except ValueError as e:
        sys.exit(f"{e}\nLas veinte no se miden.")
    if args.casos:
        pedidos = [c.strip() for c in args.casos.split(",") if c.strip()]
        faltan = [c for c in pedidos if c not in ids]
        if faltan:
            sys.exit(f"Casos fuera de las veinte aprobadas: {faltan}. No se sustituyen.")
        ids = pedidos
    modelos = [mm.strip() for mm in args.modelos.split(",") if mm.strip()]
    if [x for x in modelos if x not in MODELOS_102] or len(set(modelos)) != len(modelos):
        sys.exit(f"--modelos debe ser un subconjunto ordenado de la matriz: {','.join(MODELOS_102)}.")
    if modelos != [x for x in MODELOS_102 if x in modelos]:
        sys.exit("Los modelos deben mantener el orden exacto de la matriz #102.")
    alcance = ("completa" if modelos == list(MODELOS_102) and ids == list(IDS_102)
               else "parcial-subset")

    try:
        fro = politica_congelada_valida(args.politica_congelada) if args.politica_congelada else None
    except ValueError as e:
        sys.exit(f"Política congelada rechazada: {e}")
    bloqueo_politica = "" if fro else (
        "sin política congelada: la condición reconsultas queda pendiente "
        "(no se improvisa otra política ni se mide sin congelado)")
    politica = dict(fro["politica_ganadora"]) if fro else None
    if politica is not None and fro is not None:
        politica["modo_congelado"] = fro.get("modo", "?")
        politica["resultado_negativo"] = bool(fro.get("resultado_negativo", False))
    if fro is not None and fro.get("resultado_negativo"):
        print("Congelado NO_MEJORA_VALIDACION/no_adoptar: se miden los 400 "
              "como evidencia negativa (no es ganadora apta).")

    cliente = ClienteOllama(args.url, args.timeout)
    cliente_carga = ClienteOllama(args.url, max(args.timeout, 600.0))
    try:
        version = cliente.version()
    except ErrorOllama as e:
        sys.exit(f"No pude hablar con Ollama en {args.url} ({e}). Sin runtime no hay medición.")
    arranque = {"url": args.url, "version": version}

    inventario: dict[str, dict] = {}
    bloqueos_modelo: dict[str, dict] = {}
    for mod in modelos:
        try:
            inventario[mod] = matriz_101.inventario_modelo(cliente, mod)
        except (ErrorOllama, LookupError) as e:
            bloqueos_modelo[mod] = str(e)
    modelos_ok = [mod for mod in modelos if mod not in bloqueos_modelo]
    if not modelos_ok:
        sys.exit("Ningún modelo disponible en el runtime: nada para medir (sin descargas ni sustituciones).")

    try:
        tito_nuevo, prep_nuevo, umbral_nuevo, variante_nueva = matriz_101.resolver_tito_nuevo(
            args.tito_nuevo_modelo, args.tito_nuevo_manifest, args.tito_nuevo_umbral)
        bloqueo_nuevo = ""
    except matriz_101.TitoNuevoNoDisponible as e:
        tito_nuevo, prep_nuevo, umbral_nuevo, variante_nueva = None, None, None, ""
        bloqueo_nuevo = str(e)
    except ValueError as e:
        sys.exit(f"Candidato nuevo rechazado: {e}")
    if tito_nuevo is None:
        sys.exit(f"Sin Tito nuevo no hay matriz 102 (ambas condiciones lo usan): {bloqueo_nuevo}")
    if fro is not None:
        try:
            from seleccionar_politica_102 import verificar_congelado
            verificar_congelado(fro, Path(args.tito_nuevo_modelo), Path(args.tito_nuevo_manifest))
        except ValueError as e:
            sys.exit(f"El congelado no coincide con el candidato a medir: {e}")

    extra: dict = {}
    if args.solo_cpu:
        extra["num_gpu"] = 0
    if args.hilos:
        extra["num_thread"] = args.hilos
    if args.num_batch:
        extra["num_batch"] = args.num_batch
    extra = extra or None
    prompt_txt, esquema = cargar_prompt(args.prompt), esquema_de(args.prompt)
    from detectores import huella as huella_texto
    funcionales = {
        "modelos": modelos, "casos": ids,
        "condiciones": ["permanente"] + ([] if bloqueo_politica else ["reconsultas"]),
        "alcance": alcance,
        "prompt": args.prompt, "prompt_huella": huella_texto(prompt_txt),
        "hablantes": args.hablantes, "num_ctx": args.num_ctx, "seed": args.seed,
        "timeout": args.timeout, "hardware": extra, "url": args.url,
        "ollama_version": version,
        "procedimiento": matriz_101.huellas_procedimiento(),
        "inventario": inventario,
        "casos_huellas": matriz_101.huellas_casos_101(ids),
        "particiones_sha256": matriz_101._sha_archivo(matriz_101.PARTICIONES),
        "configuracion_sha256": matriz_101._sha_archivo(matriz_101.CONFIG_101),
        "tito_nuevo": {"artefacto": str(args.tito_nuevo_modelo),
                       "manifest": str(args.tito_nuevo_manifest),
                       "variante": variante_nueva,
                       "sha256": correr.sha_archivo(args.tito_nuevo_modelo),
                       "entrada": matriz_101.ENTRADA_NUEVO_EXIGIDA, "umbral": umbral_nuevo,
                       "encoder": json.loads(Path(args.tito_nuevo_manifest).read_text(
                           encoding="utf-8")).get("encoder", {})},
        "politica": dict(politica) if politica else {"bloqueo": bloqueo_politica},
    }
    huella = huella_funcional(funcionales)
    condiciones = ["permanente"] + ([] if bloqueo_politica else ["reconsultas"])
    triples = plan_pares(modelos_ok, condiciones, ids)

    procedencia_reuso: dict = {}
    if args.reanudar is not None:
        try:
            corrida = resolver_corrida_102(args.reanudar)
        except (FileNotFoundError, ValueError) as e:
            sys.exit(str(e))
        manifiesto = json.loads(corrida["manifiesto"].read_text(encoding="utf-8"))
        if huella_funcional(manifiesto["funcionales"]) != huella:
            sys.exit("La configuración actual difiere de la corrida a reanudar: "
                     "no se mezclan configuraciones (usá un prefijo nuevo).")
        totales = {cid: len(casos.cargar_texto(cid)) for cid in ids}
        matriz_101.normalizar_traza(corrida["csv"], totales, orden=triples)
        completados = matriz_101.leer_completados(corrida["csv"])
        manifiesto_path, csv_path = corrida["manifiesto"], corrida["csv"]
        etiqueta_corrida = corrida["prefijo"] or corrida["base"].name
    else:
        salida = args.salida
        if not salida.is_dir():
            sys.exit(f"--salida debe ser una carpeta existente (no se crean dirs): {salida}.")
        nombre = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if args.etiqueta:
            nombre += f"_{matriz_101._etiqueta_segura(args.etiqueta)}"
        prefijo = f"{nombre}_102"
        manifiesto_path = salida / f"{prefijo}_manifiesto.json"
        csv_path = salida / f"{prefijo}_actualizaciones.csv"
        if manifiesto_path.exists() or csv_path.exists():
            sys.exit(f"El prefijo ya existe, usá otra etiqueta: {prefijo}.")
        manifiesto = {
            "matriz": "matriz-102",
            "issue": 102,
            "inicio": datetime.now().isoformat(timespec="seconds"),
            "comando": "python matriz_102.py " + " ".join(argv if argv is not None else sys.argv[1:]),
            "codigo": correr.info_codigo(),
            "maquina": correr.info_maquina(),
            "politica_aviso": correr.POLITICA,
            "modo_termino": correr.MODO_OPERATIVO,
            "particion": "evaluacion_102",
            "particiones_sha256": matriz_101._sha_archivo(matriz_101.PARTICIONES),
            "configuracion_sha256": matriz_101._sha_archivo(matriz_101.CONFIG_101),
            "ollama": {**arranque, "arranque_ms": None, "modelos": {}},
            "funcionales": funcionales,
            "huella_funcional": huella,
            "tito_nuevo_preparacion": prep_nuevo,
            "politica_congelada": ({"archivo": str(args.politica_congelada),
                                    "ganadora": politica.get("nombre") if politica else None,
                                    **(politica or {})} if politica else None),
            "bloqueos_modelo": bloqueos_modelo,
            "bloqueo_politica": bloqueo_politica,
            "configs": [],
            "casos": matriz_101.huellas_casos_101(ids),
            "reutilizacion_101": procedencia_reuso,
            "interrumpida": False,
            "fin": None,
        }
        csv_path.write_text("", encoding="utf-8-sig")
        completados = set()
        etiqueta_corrida = prefijo
        if args.reutilizar_101 is not None:
            try:
                importados, registro = resolver_reuso_101(
                    Path(args.reutilizar_101), funcionales, csv_path,
                    modelos_ok, ids)
            except ValueError as e:
                sys.exit(str(e))
            completados |= importados
            manifiesto["reutilizacion_101"] = registro
            if not registro["reusado"]:
                print("Reuso 101 rechazado: se miden ambas condiciones "
                      "(global 400 intacto):\n- " + "\n- ".join(registro["motivos"]))

    manifiesto["cobertura"] = cobertura_102(bloqueos_modelo, bloqueo_politica, triples, completados)
    _guardar_manifiesto(manifiesto_path, manifiesto)
    cob = manifiesto["cobertura"]
    print(f"Matriz #102: {etiqueta_corrida} ({cob['planificados']} recorridos planificados, "
          f"{cob['completados']} hechos, {cob['pendientes']} pendientes de 400 globales)")
    if alcance != "completa" or bloqueos_modelo or bloqueo_politica:
        print(f"Alcance parcial: esto NO es la matriz completa "
              f"(alcance={alcance}, bloqueos_modelo={sorted(bloqueos_modelo) or 'ninguno'}, "
              f"reconsultas={'pendiente' if bloqueo_politica else 'incluida'}).")

    try:
        detectores_cache: dict[tuple[str, str], tuple[dict, object]] = {}
        modelo_actual: str | None = None
        for modelo, cond, case_id in triples:
            if (modelo, cond, case_id) in completados:
                continue
            if modelo != modelo_actual:
                modelo_actual = modelo
                print(f"Cargando {modelo}...", end=" ", flush=True)
                try:
                    carga = correr.calentar(cliente_carga, modelo, args.num_ctx, extra)
                except correr.FalloAlCalentar as e:
                    manifiesto["ollama"]["modelos"][modelo] = {"error": str(e)}
                    _guardar_manifiesto(manifiesto_path, manifiesto)
                    print("no quedó listo.")
                    sys.exit(f"\n{e}\nLo procesado hasta acá quedó en {etiqueta_corrida}.")
                manifiesto["ollama"]["modelos"][modelo] = {**inventario[modelo], **carga}
                _guardar_manifiesto(manifiesto_path, manifiesto)
                print(f"listo ({carga['carga_ms'] / 1000:.1f} s).")
            clave = (modelo, cond)
            if clave not in detectores_cache:
                assert politica is not None
                ds = construir_detectores(modelo, prompt_txt, args.prompt, args.hablantes,
                                          cliente, args.num_ctx, args.seed, extra, esquema,
                                          tito_nuevo, umbral_nuevo, politica)
                for cfg, det in ds:
                    if isinstance(det, DetectorSLM):
                        det.pensar = manifiesto["ollama"]["modelos"][modelo].get("pensar")
                    elif isinstance(det, FlujoTitoSLM):
                        det.slm.pensar = manifiesto["ollama"]["modelos"][modelo].get("pensar")
                    detectores_cache[(modelo, cfg["config"].split("|")[0])] = (cfg, det)
                    if cfg not in manifiesto["configs"]:
                        manifiesto["configs"].append(cfg)
                _guardar_manifiesto(manifiesto_path, manifiesto)
            config, detector = detectores_cache[clave]
            lineas = casos.cargar_texto(case_id)
            filas_triple = []
            for n, linea, r, aviso in correr.procesar_caso(detector, lineas, detener_en_aviso=True):
                filas_triple.append(correr._fila(config, case_id, n, linea, r, aviso))
            matriz_101.agregar_filas(csv_path, filas_triple)
            completados.add((modelo, cond, case_id))
            manifiesto["cobertura"] = cobertura_102(bloqueos_modelo, bloqueo_politica,
                                                    triples, completados)
            _guardar_manifiesto(manifiesto_path, manifiesto)
            print(f"   {modelo:14} {cond:12} {case_id}")
    except KeyboardInterrupt:
        manifiesto["interrumpida"] = True
        _guardar_manifiesto(manifiesto_path, manifiesto)
        print("\nCorrida interrumpida: lo procesado hasta acá quedó guardado (reanudá con medir --reanudar).")
        return 0
    manifiesto["fin"] = datetime.now().isoformat(timespec="seconds")
    _guardar_manifiesto(manifiesto_path, manifiesto)
    print(f"\nListo. Informe: python informe_102.py regenerar {manifiesto_path}")
    return 0


def _mostrar(carpeta: Path) -> str:
    try:
        return carpeta.relative_to(AQUI).as_posix()
    except ValueError:
        return str(carpeta)


if __name__ == "__main__":
    sys.exit(main())