"""Matriz #101: SLM directo vs Tito viejo→SLM vs Tito nuevo→SLM (#95, H4).

Diez modelos × tres condiciones × veinte conversaciones = 600 recorridos
operativos. Reutiliza el runner existente (`correr.procesar_caso`,
`FlujoTitoSLM`, `DetectorSLM`, `calentar`, `_fila`) sin un pipeline
experimental paralelo y sin cambiar la CLI histórica de `correr.py`.

Condiciones por modelo (misma muestra, mismo runtime, mismo prompt):
  directo    SLM solo, sin filtro.
  tito-viejo Tito histórico inmutable (`tito_logreg.json`, frase aislada,
             umbral 0,5) → SLM. Misma política permanente que el nuevo.
  tito-nuevo Candidato #99/#100 (`tito_99_historial_C*.json`, historial
             acumulado A/B hasta la línea actual) → SLM. Entrada y umbral
             desde el manifiesto congelado de selección; las veinte nunca
             se usan para entrenar ni seleccionar (el artefacto llega
             congelado de #99/#100).

Las tres condiciones terminan al primer aviso válido (incluso en
legítimas); sin aviso llegan hasta el final. Solo el SLM avisa; un error
técnico de Tito deriva por fail-open sin fabricar sospecha.

Inventario antes de medir: tag exacto, digest (`/api/tags`), cuantización
(`/api/show`) y versión de Ollama (`/api/version`) por modelo. Sin
`latest`, sin alias, sin sustituciones, sin descargas: lo ausente se
registra como bloqueo con cobertura pendiente explícita.

Sin candidato nuevo congelado la condición tito-nuevo queda pendiente
ANTES de medir (no se improvisa otro Tito ni se usa el umbral 0,5 por
defecto). Un subconjunto (`--modelos`/`--casos`) nunca es la matriz
completa: el manifiesto declara 600 esperados globales siempre.

Archivos planos con prefijo de corrida dentro de `corridas/` (carpeta ya
existente, nunca se crea nada): `<pref>_manifiesto.json`,
`<pref>_actualizaciones.csv`. Reanudar por prefijo o por carpeta legada;
la traza parcial se retira y se remide sin duplicar filas ni costos.

Uso:
    python matriz_101.py --url http://127.0.0.1:11435 \\
        --tito-nuevo-modelo candidato.json --tito-nuevo-manifest sel.json
    python matriz_101.py --modelos qwen3.5:2b --casos CV2-D-V-BANCO-001
    python matriz_101.py --reanudar corridas/2026-10-29_HHMMSS_101

Después: python informe_101.py <prefijo|carpeta> regenera el reporte sin inferencia.

No declara éxito ni adopta metas (95/5 sigue abierta en D08): informa
conteos, denominadores, costos y pendientes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import casos
import correr
from cliente_ollama import URL_POR_DEFECTO, ClienteOllama, ErrorOllama
from detectores import DetectorSLM, cargar_prompt, esquema_de
from filtro_tito import UMBRAL_TITO, FlujoTitoSLM
from tito_real import ARTEFACTO_POR_DEFECTO, preparar_tito_real

AQUI = Path(__file__).resolve().parent
PARTICIONES = AQUI / "PARTICIONES-TITO-2026-10-29.json"
CONFIG_101 = AQUI / "CONFIGURACION-TITO-2026-10-29.json"
DIR_CORRIDAS = AQUI / "corridas"
URL_101 = "http://127.0.0.1:11435"

# Acuerdo del usuario 2026-10-29 (#101): exactamente estos, en este orden.
MODELOS_101 = (
    "qwen3.5:4b",
    "qwen3.5:2b",
    "gemma:2b",
    "gemma3:270m",
    "gemma3:1b",
    "gemma3:4b",
    "gemma3n:e2b",
    "gemma3n:e4b",
    "gemma4:e2b",
    "gemma4:e4b",
)

# Aprobación del usuario 2026-10-29 (#101): 10 vishing + 10 legítimas, en orden.
IDS_101 = (
    "CV2-D-V-BANCO-001",
    "CV2-D-V-BANCO-002",
    "CV2-D-V-BANCO-007",
    "CV2-D-V-WHATSAPP-002",
    "CV2-D-V-WHATSAPP-006",
    "CV2-D-V-SOPORTE-003",
    "CV2-D-V-SOPORTE-004",
    "CV2-D-V-FAMILIAR-002",
    "CV2-D-V-ORGANISMO_PREVISIONAL-001",
    "CV2-D-V-PREMIO-004",
    "CV2-D-L-BANCO-001",
    "CV2-D-L-BANCO-007",
    "CV2-D-L-DELIVERY-001",
    "CV2-D-L-ESCUELA-001",
    "CV2-D-L-FAMILIAR-001",
    "CV2-D-L-MEDICO-001",
    "CV2-D-L-ORGANISMO_PREVISIONAL-001",
    "CV2-D-L-PREMIO-001",
    "CV2-D-L-SOPORTE-002",
    "CV2-D-L-WHATSAPP-001",
)

CONDICIONES = ("directo", "tito-viejo", "tito-nuevo")

ESPERADOS_GLOBALES = len(MODELOS_101) * len(CONDICIONES) * len(IDS_101)
assert ESPERADOS_GLOBALES == 600

ENTRADA_NUEVO_EXIGIDA = "historial_acumulado"
FORMATOS_NUEVO_CONOCIDOS = ("tito-99-logreg-v1",)


def huellas_particiones_101() -> dict[str, dict]:
    """Las veinte de `comparacion_20` según el manifiesto de particiones."""
    datos = json.loads(PARTICIONES.read_text(encoding="utf-8"))
    return {c["case_id"]: c for c in datos.get("conversaciones", [])
            if c.get("particion_preparacion") == "comparacion_20"
            and c.get("case_id") in IDS_101}


def _sha_archivo(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def casos_101() -> list[str]:
    """Las veinte conversaciones aprobadas, verificadas contra particiones.

    Exige IDs exactos en orden, sin duplicados, 10 vishing + 10 legítimas;
    cada una con `particion_preparacion == comparacion_20`, fuera de la
    reserva, con texto y referencia íntegros respecto de los hashes del
    manifiesto de particiones. Solo valida estas veinte (no abre el resto).
    """
    datos = json.loads(PARTICIONES.read_text(encoding="utf-8"))
    if list(datos.get("evaluacion_ids", [])) != list(IDS_101):
        raise ValueError("evaluacion_ids de particiones no coincide con IDS_101 "
                         "(orden exacto de las veinte aprobadas).")
    respaldo = huellas_particiones_101()
    if sorted(respaldo) != sorted(IDS_101):
        faltan = sorted(set(IDS_101) - set(respaldo))
        raise ValueError(f"particiones sin respaldo comparacion_20 para: {faltan}.")
    todos = {p.stem for p in casos.DIR_TEXTO.glob("*.txt")}
    try:
        import csv as _csv
        with (casos.CATALOGO).open(encoding="utf-8", newline="") as _f:
            semillas = {f["scenario_id"] for f in _csv.DictReader(_f)
                        if f["estado"] != "descartado"}
    except FileNotFoundError:
        semillas = set()
    errores: list[str] = []
    for cid in IDS_101:
        errores.extend(casos.validar_caso(cid, todos, semillas))
        ref = casos.cargar_referencia(cid)
        if ref.get("particion") == "test_reservado":
            errores.append(f"{cid}: pertenece a la reserva, no a la comparación.")
        esp = respaldo[cid]
        for clave, ruta in (("texto_sha256", casos.DIR_TEXTO / f"{cid}.txt"),
                            ("referencia_sha256", casos.DIR_REFERENCIA / f"{cid}.json")):
            if _sha_archivo(ruta) != esp.get(clave):
                errores.append(f"{cid}: deriva de hash en {ruta.name} "
                               f"(no coincide con particiones).")
    if errores:
        raise ValueError("casos_101 inválidos:\n- " + "\n- ".join(errores))
    refs = [casos.cargar_referencia(c) for c in IDS_101]
    if [r["clase"] for r in refs[:10]] != ["vishing"] * 10:
        raise ValueError("las primeras diez deben ser vishing (orden del issue).")
    if not all(r["clase"] in casos.LEGITIMAS for r in refs[10:]):
        raise ValueError("las últimas diez deben ser legítimas (orden del issue).")
    return list(IDS_101)


def huellas_procedimiento() -> dict:
    """Huellas explícitas de las fuentes comunes del procedimiento.

    Lo que dos corridas deben compartir para que una celda medida en
    una valga en la otra (#101 tito-nuevo -> #102 permanente): política
    de aviso único, modo de término al primer aviso, columnas de la
    traza cruda y código que las escribe. Sin cambiar el runner: solo
    se lee y se declara en el manifiesto ANTES de medir.
    """
    columnas = list(correr.COLUMNAS)
    return {
        "politica_aviso": correr.POLITICA,
        "modo_termino": correr.MODO_OPERATIVO,
        "columnas_traza": columnas,
        "columnas_traza_sha256": hashlib.sha256(
            json.dumps(columnas).encode("utf-8")).hexdigest(),
        "codigo": correr.info_codigo(),
    }


def huellas_casos_101(ids: list[str]) -> dict[str, dict]:
    """Snapshot de textos y referencias para la huella funcional."""
    respaldo = huellas_particiones_101()
    huellas = {}
    for cid in ids:
        ref = casos.cargar_referencia(cid)
        huellas[cid] = {
            "texto_sha256": _sha_archivo(casos.DIR_TEXTO / f"{cid}.txt"),
            "referencia_sha256": _sha_archivo(casos.DIR_REFERENCIA / f"{cid}.json"),
            "clase": ref["clase"],
            "particion_preparacion": respaldo[cid]["particion_preparacion"],
            "grupo_preparacion": respaldo[cid]["grupo_preparacion"],
            "revision_humana": ref.get("revision_humana", False),
        }
    return huellas


def inventario_modelo(cliente: ClienteOllama, modelo: str) -> dict:
    """Tag exacto, digest, cuantización y runtime del artefacto instalado.

    Sin sustituciones: si el tag exacto no está en `/api/tags`, bloqueo
    explícito (no se prueba `:latest` ni otro nombre con igual digest).
    Nunca descarga nada.
    """
    instalados = cliente.modelos_instalados()
    if modelo not in instalados:
        parecidos = sorted(m for m in instalados if m.split(":")[0] == modelo.split(":")[0])
        raise LookupError(
            f"modelo ausente en Ollama ({cliente.url}): {modelo!r}. "
            f"Instalados con la misma familia: {parecidos or 'ninguno'}. "
            "No se descarga ni se sustituye: registralo como bloqueo."
        )
    ficha = cliente.mostrar(modelo)
    detalles = ficha.get("details") or {}
    return {
        "tag": modelo,
        "digest": instalados[modelo],
        "cuantizacion": detalles.get("quantization_level", ""),
        "familia": detalles.get("family", ""),
        "tamano_parametros": detalles.get("parameter_size", ""),
        "formato": detalles.get("format", ""),
        "show_modified_at": ficha.get("modified_at", ""),
    }


class TitoNuevoNoDisponible(Exception):
    """El candidato #99/#100 aún no existe: la condición queda pendiente."""


def cargar_tito_viejo(ruta: Path):
    """Tito histórico inmutable, una vez por proceso (artefacto + encoder + calentamiento)."""
    return preparar_tito_real(ruta)


def resolver_tito_nuevo(artefacto: Path | None, manifest: Path | None,
                        umbral_cli: float | None):
    """Candidato #99/#100 congelado, validado ANTES de medir.

    Contrato provisional con el integrador #99 (ctx_21184cb827b1, sin pesos
    nuevos ni #100 ejecutado): exige el manifiesto congelado de selección
    con identidad (encoder id/revisión), hashes (artefacto + tokenizador),
    entrada `historial_acumulado` y umbral seleccionado solo en validación.
    Sin manifiesto la condición queda pendiente (no se improvisa otro Tito
    ni se usa el umbral 0,5 por defecto). Un `umbral_cli` distinto del
    manifiesto se rechaza en texto plano (sin override silencioso); un
    artefacto de frase se rechaza aunque el manifiesto lo acompañe.
    El loader es modular: la variante #99 congelada usa `Tito99`; un
    formato `tito-100-*` futuro queda pendiente (no se asume Tito99).
    """
    if artefacto is None or not Path(artefacto).exists():
        raise TitoNuevoNoDisponible(f"sin artefacto del candidato nuevo: {artefacto}.")
    if manifest is None or not Path(manifest).exists():
        raise TitoNuevoNoDisponible(
            f"sin manifiesto congelado #100 para {artefacto}: la condición "
            "tito-nuevo queda pendiente (no se entrena ni se selecciona acá).")
    try:
        arte = json.loads(Path(artefacto).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise ValueError(f"candidato nuevo ilegible ({artefacto}): {e}.")
    formato = arte.get("formato", "")
    if isinstance(formato, str) and formato.startswith("tito-100"):
        raise TitoNuevoNoDisponible(
            f"formato {formato} sin loader acordado con el integrador #99: "
            "pendiente, no se carga como Tito99.")
    if formato not in FORMATOS_NUEVO_CONOCIDOS:
        raise ValueError(f"formato de candidato desconocido: {formato!r}; "
                         "no se mide con un loader no acordado.")
    try:
        sel = json.loads(Path(manifest).read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        raise ValueError(f"manifiesto de selección ilegible ({manifest}): {e}.")
    if _sha_archivo(Path(artefacto)) != sel.get("artefacto_sha256"):
        raise ValueError("el artefacto no coincide con el artefacto_sha256 "
                         "del manifiesto congelado.")
    for fuente, entrada in (("artefacto", arte.get("entrada")),
                            ("manifiesto", sel.get("entrada"))):
        if entrada != ENTRADA_NUEVO_EXIGIDA:
            raise ValueError(
                f"entrada del candidato en {fuente}: {entrada!r}; se exige "
                f"{ENTRADA_NUEVO_EXIGIDA!r} (un artefacto de frase no pasa).")
    umbral = sel.get("umbral")
    if not isinstance(umbral, (int, float)) or not 0 < float(umbral) <= 1:
        raise ValueError("el manifiesto no trae un umbral seleccionado en (0, 1].")
    if umbral_cli is not None and float(umbral_cli) != float(umbral):
        raise ValueError(f"--tito-nuevo-umbral {umbral_cli} no coincide con el "
                         f"umbral congelado {umbral}: sin override silencioso.")
    enc_arte = arte.get("encoder", {})
    enc_sel = sel.get("encoder", {})
    if enc_arte != enc_sel or not enc_sel.get("id") or not enc_sel.get("revision"):
        raise ValueError("identidad del encoder sin fijar entre artefacto y manifiesto.")
    if not (arte.get("tokenizador", {}).get("tokenizer_sha256")
            and arte.get("pesos", {}).get("coef")):
        raise ValueError("candidato sin hashes de tokenizador o sin pesos.")
    import entrenar_tito_99

    if (enc_sel.get("id") != entrenar_tito_99.ENCODER_ID
            or enc_sel.get("revision") != entrenar_tito_99.ENCODER_REVISION):
        raise ValueError("el encoder del candidato no es el fijado en configuración.")
    tito = entrenar_tito_99.Tito99(artefacto)
    informe = preparar_tito_99(tito)
    return tito, informe, float(umbral), sel.get("variante", "#99-congelada")


def preparar_tito_99(tito) -> dict:
    """Preparación explícita del candidato nuevo, fuera de las actualizaciones.

    Carga el encoder y corre un calentamiento (una incrustación del texto
    de ejemplo). Devuelve costos separados sin doble conteo con `puntuar`.
    Un error no levanta: el flujo deriva por fail-open y cada `puntuar`
    registrará su propia causa. El error devuelto por `puntuar_entrada`
    (no solo la excepción) marca el warmup inválido: `encoder_listo` en
    falso y nunca se declara el encoder listo con None/error/NaN.
    """
    import math as _math

    inicio_enc = time.perf_counter()
    try:
        tito._asegurar_encoder()
    except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
        return {"encoder_ms": round((time.perf_counter() - inicio_enc) * 1000, 1),
                "encoder_desde_cache": False, "encoder_listo": False,
                "calentamiento_ms": None,
                "error": f"tito99_preparar_error: {type(e).__name__}: {e}",
                "unidad": "ms"}
    encoder_ms = round((time.perf_counter() - inicio_enc) * 1000, 1)
    inicio_cal = time.perf_counter()
    try:
        puntaje, error, _ms = tito.puntuar_entrada("hola mundo")
    except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
        return {"encoder_ms": encoder_ms, "encoder_desde_cache": False,
                "encoder_listo": False,
                "calentamiento_ms": round((time.perf_counter() - inicio_cal) * 1000, 1),
                "error": f"tito99_calentar_error: {type(e).__name__}: {e}",
                "unidad": "ms"}
    calentamiento_ms = round((time.perf_counter() - inicio_cal) * 1000, 1)
    if error or puntaje is None or not _math.isfinite(puntaje):
        return {"encoder_ms": encoder_ms, "encoder_desde_cache": False,
                "encoder_listo": False, "calentamiento_ms": calentamiento_ms,
                "error": f"tito99_calentar_invalido: puntaje={puntaje!r} error={error!r}",
                "unidad": "ms"}
    return {"encoder_ms": encoder_ms, "encoder_desde_cache": False,
            "encoder_listo": True,
            "calentamiento_ms": calentamiento_ms,
            "error": "", "unidad": "ms"}


class FlujoTitoHistorialSLM(FlujoTitoSLM):
    """Tito nuevo → SLM con historial acumulado A/B hasta la línea actual.

    Reutiliza la política permanente del flujo (`FlujoTitoSLM.evaluar`:
    activación al primer puntaje >= umbral, indicio falible declarado,
    fail-open ante error técnico, solo el SLM avisa). Solo cambia la
    entrada de Tito: el historial visible con hablantes, construido con
    `entrenar_tito_99.construir_entrada` (la misma que en entrenamiento).
    """

    def _puntuar(self, lineas) -> tuple[float | None, str, float]:
        import entrenar_tito_99

        visibles = [f"{l.hablante}: {l.texto}" for l in lineas]
        return self.tito.puntuar_entrada(
            entrenar_tito_99.construir_entrada(visibles, self.tito.entrada))


def nombre_config(condicion: str, modelo: str, prompt: str, hablantes: str) -> str:
    return f"{condicion}|{modelo}|{prompt}|{hablantes}"


def construir_detectores(modelo: str, prompt_txt: str, variante: str, hablantes: str,
                         cliente: ClienteOllama, num_ctx: int, seed: int,
                         extra: dict | None, esquema: dict,
                         tito_viejo, umbral_viejo: float,
                         tito_nuevo, umbral_nuevo: float) -> list[tuple[dict, object]]:
    """Las condiciones de un modelo sobre la misma base SLM."""
    detectores = []
    slm = DetectorSLM(cliente, modelo, prompt_txt, hablantes, num_ctx, seed, extra=extra, esquema=esquema)
    detectores.append(
        ({"config": nombre_config("directo", modelo, variante, hablantes),
          "detector": "slm", "modelo": modelo, "prompt": variante, "hablantes": hablantes}, slm))
    if tito_viejo is not None:
        f_viejo = FlujoTitoSLM(tito_viejo, slm, umbral_viejo)
        detectores.append(
            ({"config": nombre_config("tito-viejo", modelo, variante, hablantes),
              "detector": "tito-slm", "modelo": modelo, "prompt": variante, "hablantes": hablantes}, f_viejo))
    if tito_nuevo is not None:
        f_nuevo = FlujoTitoHistorialSLM(tito_nuevo, slm, umbral_nuevo)
        detectores.append(
            ({"config": nombre_config("tito-nuevo", modelo, variante, hablantes),
              "detector": "tito-slm", "modelo": modelo, "prompt": variante, "hablantes": hablantes}, f_nuevo))
    return detectores


def huella_funcional(parametros: dict) -> str:
    """Huella de lo que define una corrida comparable (para reanudar sin mezclar)."""
    return hashlib.sha256(
        json.dumps(parametros, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def plan_triples(modelos: list[str], condiciones: list[str], ids: list[str]) -> list[tuple[str, str, str]]:
    """Un recorrido por (modelo, condición, caso). Con los diez, tres y veinte: 600."""
    return [(m, c, i) for m in modelos for c in condiciones for i in ids]


def _ruta_csv(base: Path) -> Path:
    """Acepta la carpeta legada o la ruta directa del CSV."""
    base = Path(base)
    if base.is_dir():
        return base / "actualizaciones.csv"
    return base


def _leer_filas_csv(ruta: Path) -> list[dict]:
    """Lee la traza tolerando archivo ausente, vacío o sin header (bug previo)."""
    if not ruta.exists() or ruta.stat().st_size == 0:
        return []
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        primera = f.readline()
        if not primera.startswith("config,"):
            # Headerless de una interrupción vieja: la primera fila es dato.
            resto = f.read().splitlines()
            lector = csv.DictReader([primera, *resto], fieldnames=correr.COLUMNAS)
            return [r for r in lector if r.get("config")]
        lector = csv.DictReader([primera, *f.read().splitlines()])
        if lector.fieldnames != list(correr.COLUMNAS):
            return []
        return [r for r in lector if r.get("config")]


def _triple_de_config(config: str, case_id: str) -> tuple[str, str, str] | None:
    partes = config.split("|")
    if len(partes) != 4:
        return None
    return (partes[1], partes[0], case_id)


def estado_traza(filas: list[dict], totales: dict[str, int]) -> tuple[set, list[dict]]:
    """Completa solo con secuencia única y contigua 1..k por triple.

    Un triple está completo si sus líneas son únicas y contiguas desde 1 y
    (a) llegan al total del caso, o (b) terminan en su único aviso (modo
    operativo). Prefijos duplicados, huecos o filas tras el aviso quedan
    parciales: se retiran para remedición, nunca cuentan como completos.
    Devuelve (completados, filas_canónicas_de_completos).
    """
    por_triple: dict[tuple[str, str, str], list[dict]] = {}
    for fila in filas:
        clave = _triple_de_config(fila.get("config", ""), fila.get("case_id", ""))
        if clave is None:
            continue
        por_triple.setdefault(clave, []).append(fila)
    completados: set[tuple[str, str, str]] = set()
    canonicas: list[dict] = []
    for clave, fs in por_triple.items():
        lineas: list[int] = []
        avisos: list[int] = []
        valido = True
        for f in fs:
            try:
                n = int(f["linea"])
            except (TypeError, ValueError):
                valido = False
                break
            lineas.append(n)
            if f.get("aviso") == "true":
                avisos.append(n)
        if not valido or not lineas:
            continue
        if len(set(lineas)) != len(lineas):
            continue  # filas repetidas: parcial
        unicas = sorted(set(lineas))
        if unicas != list(range(1, unicas[-1] + 1)):
            continue  # hueco o no empieza en 1: parcial
        total = totales.get(clave[2])
        if total is None:
            try:
                total = len(casos.cargar_texto(clave[2]))
            except ValueError:
                continue
        if len(avisos) > 1:
            continue
        if avisos:
            if avisos[0] == unicas[-1]:
                completados.add(clave)
                canonicas.extend(sorted(fs, key=lambda f: int(f["linea"])))
            # Aviso con filas posteriores o anteriores faltantes: parcial.
        elif unicas[-1] == total and len(unicas) == total:
            completados.add(clave)
            canonicas.extend(sorted(fs, key=lambda f: int(f["linea"])))
    return completados, canonicas


def leer_completados(base: Path) -> set[tuple[str, str, str]]:
    """Triples completos guardados en la traza (secuencia única y contigua)."""
    filas = _leer_filas_csv(_ruta_csv(Path(base)))
    completados, _ = estado_traza(filas, {})
    return completados


def normalizar_traza(base: Path, totales: dict[str, int] | None = None,
                     orden: list[tuple[str, str, str]] | None = None) -> list[dict]:
    """Cierre transaccional por triple: conserva solo triples completos.

    Reescribe el CSV con header único y filas canónicas (sin duplicados ni
    parciales, que se remiden desde cero). Escritura atómica (tmp + replace)
    en la misma carpeta. Devuelve las filas canónicas.
    """
    ruta = _ruta_csv(Path(base))
    filas = _leer_filas_csv(ruta)
    _, canonicas = estado_traza(filas, totales or {})
    if orden is not None:
        posicion = {t: k for k, t in enumerate(orden)}
        canonicas.sort(key=lambda f: (posicion.get(
            _triple_de_config(f["config"], f["case_id"]), 10 ** 9), int(f["linea"])))
    tmp = ruta.with_name(ruta.name + ".tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
        w.writeheader()
        for fila in canonicas:
            w.writerow({c: fila.get(c, "") for c in correr.COLUMNAS})
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, ruta)
    return canonicas


def agregar_filas(base: Path, filas: list[dict]) -> None:
    """Agrega filas a la traza con un solo header y descarga durable."""
    ruta = _ruta_csv(Path(base))
    necesita_header = (not ruta.exists() or ruta.stat().st_size == 0
                       or not _leer_filas_csv(ruta))
    if necesita_header and ruta.exists() and ruta.stat().st_size > 0:
        # Headerless previo: normalizar antes de agregar.
        normalizar_traza(ruta)
        necesita_header = False
    with ruta.open("a", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
        if necesita_header:
            w.writeheader()
        for fila in filas:
            w.writerow({c: fila.get(c, "") for c in correr.COLUMNAS})
        f.flush()
        os.fsync(f.fileno())


def cobertura(bloqueos_modelo: dict, bloqueo_nuevo: str,
              triples_planificados: list[tuple[str, str, str]],
              completados: set[tuple[str, str, str]]) -> dict:
    """Cobertura contra el denominador global 10×3×20 = 600, con causas.

    Los esperados nunca se achican al subconjunto medido: un smoke o un
    bloqueo dejan faltantes explícitos. `matriz_completa` solo con 600.
    """
    planificados = set(triples_planificados)
    globales = set(plan_triples(list(MODELOS_101), list(CONDICIONES), list(IDS_101)))
    faltantes = []
    for m, c, i in sorted(globales):
        if (m, c, i) in completados:
            continue
        if m in bloqueos_modelo:
            causa = "modelo_bloqueado"
        elif c == "tito-nuevo" and bloqueo_nuevo:
            causa = "tito-nuevo-pendiente"
        elif (m, c, i) not in planificados:
            causa = "no-planificado-subset"
        else:
            causa = "pendiente-medicion"
        faltantes.append({"modelo": m, "condicion": c, "caso": i, "causa": causa})
    return {"esperados_globales": ESPERADOS_GLOBALES,
            "planificados": len(planificados),
            "completados": len(completados),
            "pendientes": ESPERADOS_GLOBALES - len(completados),
            "matriz_completa": len(completados) == ESPERADOS_GLOBALES,
            "faltantes": faltantes}


def resolver_corrida(ruta: Path) -> dict:
    """Resuelve una corrida legada (carpeta) o nueva (prefijo de archivos).

    Nuevo: `<pref>_manifiesto.json` + `<pref>_actualizaciones.csv` en una
    carpeta existente. Legado: carpeta con `manifiesto.json`.
    """
    ruta = Path(ruta)
    if ruta.is_dir() and (ruta / "manifiesto.json").exists():
        return {"modo": "legado", "base": ruta, "prefijo": None,
                "manifiesto": ruta / "manifiesto.json",
                "csv": ruta / "actualizaciones.csv"}
    texto = str(ruta)
    for sufijo in ("_manifiesto.json", "_actualizaciones.csv", "_informe_101.md",
                   "_grafico_avisos.svg", "_grafico_costos.svg"):
        if texto.endswith(sufijo):
            texto = texto[: -len(sufijo)]
            break
    base = Path(texto)
    manifiesto = base.parent / (base.name + "_manifiesto.json")
    if not manifiesto.exists():
        raise FileNotFoundError(f"sin manifiesto para la corrida: {manifiesto}.")
    return {"modo": "prefijo", "base": base.parent, "prefijo": base.name,
            "manifiesto": manifiesto,
            "csv": base.parent / (base.name + "_actualizaciones.csv")}


def _guardar_manifiesto(ruta: Path, manifiesto: dict) -> None:
    tmp = ruta.with_name(ruta.name + ".tmp")
    tmp.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, ruta)


def _etiqueta_segura(texto: str) -> str:
    import re

    limpio = re.sub(r"[^A-Za-z0-9_-]", "_", texto).strip("_")
    return limpio[:40]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--modelos", default=",".join(MODELOS_101),
                   help="subconjunto en el orden de la matriz, separado por coma (por defecto, los diez)")
    p.add_argument("--casos", default="",
                   help="case_id separados por coma (por defecto, las veinte aprobadas)")
    p.add_argument("--url", default=URL_101, help="Ollama de la matriz (por defecto, el runtime 11435)")
    p.add_argument("--prompt", default="tarea", help="variante de prompt (por defecto, tarea)")
    p.add_argument("--hablantes", default="ab", help="ab o sin (por defecto, ab)")
    p.add_argument("--num-ctx", type=int, default=4096)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--timeout", type=float, default=120.0, help="segundos máximos por actualización")
    p.add_argument("--solo-cpu", action="store_true")
    p.add_argument("--hilos", type=int)
    p.add_argument("--num-batch", type=int)
    p.add_argument("--tito-viejo-modelo", type=Path, default=ARTEFACTO_POR_DEFECTO,
                   help="artefacto histórico inmutable (por defecto, tito_logreg.json)")
    p.add_argument("--tito-nuevo-modelo", type=Path, default=None,
                   help="artefacto del candidato #99/#100; ausente o sin manifiesto → condición pendiente")
    p.add_argument("--tito-nuevo-manifest", type=Path, default=None,
                   help="manifiesto congelado de selección #100 (identidad, hashes, entrada, umbral)")
    p.add_argument("--tito-nuevo-umbral", type=float, default=None,
                   help="solo para coincidir con el umbral congelado; distinto → rechazo")
    p.add_argument("--salida", type=Path, default=DIR_CORRIDAS,
                   help="carpeta EXISTENTE para los archivos con prefijo (por defecto, corridas/)")
    p.add_argument("--etiqueta", default="", help="texto corto para el prefijo de la corrida")
    p.add_argument("--reanudar", type=Path, default=None,
                   help="prefijo o carpeta legada de una corrida 101 para continuar")
    p.add_argument("--detalle", action="store_true")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    try:
        ids = casos_101()
    except ValueError as e:
        sys.exit(f"{e}\nLas veinte no se miden.")
    if args.casos:
        pedidos = [c.strip() for c in args.casos.split(",") if c.strip()]
        faltan = [c for c in pedidos if c not in ids]
        if faltan:
            sys.exit(f"Casos fuera de las veinte aprobadas: {faltan}. No se sustituyen.")
        ids = pedidos

    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    if [m for m in modelos if m not in MODELOS_101] or len(set(modelos)) != len(modelos):
        sys.exit(f"--modelos debe ser un subconjunto ordenado de la matriz: {','.join(MODELOS_101)}.")
    if modelos != [m for m in MODELOS_101 if m in modelos]:
        sys.exit("Los modelos deben mantener el orden exacto de la matriz #101.")
    alcance = ("completa" if modelos == list(MODELOS_101) and ids == list(IDS_101)
               else "parcial-subset")

    cliente = ClienteOllama(args.url, args.timeout)
    cliente_carga = ClienteOllama(args.url, max(args.timeout, 600.0))
    try:
        version = cliente.version()
    except ErrorOllama as e:
        sys.exit(f"No pude hablar con Ollama en {args.url} ({e}). Sin runtime no hay medición.")
    arranque = {"url": args.url, "version": version}

    inventario: dict[str, dict] = {}
    bloqueos_modelo: dict[str, str] = {}
    for m in modelos:
        try:
            inventario[m] = inventario_modelo(cliente, m)
        except (ErrorOllama, LookupError) as e:
            bloqueos_modelo[m] = str(e)
    modelos_ok = [m for m in modelos if m not in bloqueos_modelo]
    if not modelos_ok:
        sys.exit("Ningún modelo disponible en el runtime: nada para medir (sin descargas ni sustituciones).")

    # Tito viejo y nuevo: una carga por proceso y condición, encoder preparado
    # fuera de las latencias. Las veinte nunca ajustan ni seleccionan: los
    # artefactos llegan persistidos de #98 (viejo) y #99/#100 (nuevo).
    if not Path(args.tito_viejo_modelo).exists():
        sys.exit(f"No existe el artefacto del Tito viejo {args.tito_viejo_modelo}: inmutable, no se regenera acá.")
    tito_viejo, prep_viejo = cargar_tito_viejo(args.tito_viejo_modelo)
    umbral_viejo = float(json.loads(Path(args.tito_viejo_modelo).read_text(encoding="utf-8"))
                         .get("umbral_derivacion", UMBRAL_TITO))
    try:
        tito_nuevo, prep_nuevo, umbral_nuevo, variante_nueva = resolver_tito_nuevo(
            args.tito_nuevo_modelo, args.tito_nuevo_manifest, args.tito_nuevo_umbral)
        bloqueo_nuevo = ""
    except TitoNuevoNoDisponible as e:
        tito_nuevo, prep_nuevo, umbral_nuevo, variante_nueva = None, None, None, ""
        bloqueo_nuevo = str(e)
    except ValueError as e:
        sys.exit(f"Candidato nuevo rechazado: {e}")
    condiciones = ["directo", "tito-viejo"] + ([] if tito_nuevo is None else ["tito-nuevo"])

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
        "modelos": modelos, "casos": ids, "condiciones": condiciones,
        "alcance": alcance,
        "prompt": args.prompt, "prompt_huella": huella_texto(prompt_txt),
        "hablantes": args.hablantes, "num_ctx": args.num_ctx, "seed": args.seed,
        "timeout": args.timeout, "hardware": extra, "url": args.url,
        "ollama_version": version,
        "procedimiento": huellas_procedimiento(),
        "inventario": inventario,
        "casos_huellas": huellas_casos_101(ids),
        "particiones_sha256": _sha_archivo(PARTICIONES),
        "configuracion_sha256": _sha_archivo(CONFIG_101),
        "tito_viejo": {"artefacto": str(args.tito_viejo_modelo),
                       "sha256": correr.sha_archivo(args.tito_viejo_modelo),
                       "entrada": "frase_actual", "umbral": umbral_viejo},
        "tito_nuevo": ({"artefacto": str(args.tito_nuevo_modelo),
                        "manifest": str(args.tito_nuevo_manifest),
                        "variante": variante_nueva,
                        "sha256": correr.sha_archivo(args.tito_nuevo_modelo),
                        "entrada": ENTRADA_NUEVO_EXIGIDA, "umbral": umbral_nuevo}
                       if tito_nuevo is not None else {"bloqueo": bloqueo_nuevo}),
    }
    huella = huella_funcional(funcionales)
    triples = plan_triples(modelos_ok, condiciones, ids)

    if args.reanudar is not None:
        try:
            corrida = resolver_corrida(args.reanudar)
        except FileNotFoundError as e:
            sys.exit(str(e))
        manifiesto = json.loads(corrida["manifiesto"].read_text(encoding="utf-8"))
        if manifiesto.get("matriz") != "matriz-101":
            sys.exit("La corrida a reanudar no es una matriz-101.")
        if huella_funcional(manifiesto["funcionales"]) != huella:
            sys.exit("La configuración actual difiere de la corrida a reanudar: "
                     "no se mezclan configuraciones (usá un prefijo nuevo).")
        totales = {cid: len(casos.cargar_texto(cid)) for cid in ids}
        normalizar_traza(corrida["csv"], totales, orden=triples)
        completados = leer_completados(corrida["csv"])
        manifiesto_path, csv_path = corrida["manifiesto"], corrida["csv"]
        etiqueta_corrida = corrida["prefijo"] or corrida["base"].name
    else:
        salida = args.salida
        if not salida.is_dir():
            sys.exit(f"--salida debe ser una carpeta existente (no se crean dirs): {salida}.")
        nombre = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        if args.etiqueta:
            nombre += f"_{_etiqueta_segura(args.etiqueta)}"
        prefijo = f"{nombre}_101"
        manifiesto_path = salida / f"{prefijo}_manifiesto.json"
        csv_path = salida / f"{prefijo}_actualizaciones.csv"
        if manifiesto_path.exists() or csv_path.exists():
            sys.exit(f"El prefijo ya existe, usá otra etiqueta: {prefijo}.")
        manifiesto = {
            "matriz": "matriz-101",
            "issue": 101,
            "inicio": datetime.now().isoformat(timespec="seconds"),
            "comando": "python matriz_101.py " + " ".join(argv if argv is not None else sys.argv[1:]),
            "codigo": correr.info_codigo(),
            "maquina": correr.info_maquina(),
            "politica": correr.POLITICA,
            "modo_termino": correr.MODO_OPERATIVO,
            "particion": "evaluacion_101",
            "particiones_sha256": _sha_archivo(PARTICIONES),
            "configuracion_sha256": _sha_archivo(CONFIG_101),
            "ollama": {**arranque, "arranque_ms": None, "modelos": {}},
            "funcionales": funcionales,
            "huella_funcional": huella,
            "tito_viejo_preparacion": prep_viejo,
            "tito_nuevo_preparacion": prep_nuevo,
            "bloqueos_modelo": bloqueos_modelo,
            "bloqueo_nuevo": bloqueo_nuevo,
            "configs": [],
            "casos": huellas_casos_101(ids),
            "interrumpida": False,
            "fin": None,
        }
        csv_path.write_text("", encoding="utf-8-sig")
        completados = set()
        etiqueta_corrida = prefijo

    manifiesto["cobertura"] = cobertura(bloqueos_modelo, bloqueo_nuevo, triples, completados)
    _guardar_manifiesto(manifiesto_path, manifiesto)
    cob = manifiesto["cobertura"]
    print(f"Matriz #101: {etiqueta_corrida} ({cob['planificados']} recorridos planificados, "
          f"{cob['completados']} hechos, {cob['pendientes']} pendientes de 600 globales)")
    if alcance != "completa" or bloqueos_modelo or bloqueo_nuevo:
        print("Alcance parcial: esto NO es la matriz completa "
              f"(alcance={alcance}, bloqueos_modelo={sorted(bloqueos_modelo) or 'ninguno'}, "
              f"tito-nuevo={'pendiente' if bloqueo_nuevo else 'incluido'}).")

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
                ds = construir_detectores(modelo, prompt_txt, args.prompt, args.hablantes,
                                          cliente, args.num_ctx, args.seed, extra, esquema,
                                          tito_viejo, umbral_viejo, tito_nuevo, umbral_nuevo or 0.0)
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
            agregar_filas(csv_path, filas_triple)
            completados.add((modelo, cond, case_id))
            manifiesto["cobertura"] = cobertura(bloqueos_modelo, bloqueo_nuevo, triples, completados)
            _guardar_manifiesto(manifiesto_path, manifiesto)
            print(f"   {modelo:14} {cond:10} {case_id}")
    except KeyboardInterrupt:
        manifiesto["interrumpida"] = True
        _guardar_manifiesto(manifiesto_path, manifiesto)
        print("\nCorrida interrumpida: lo procesado hasta acá quedó guardado (reanudá con --reanudar).")
        return 0
    manifiesto["fin"] = datetime.now().isoformat(timespec="seconds")
    _guardar_manifiesto(manifiesto_path, manifiesto)
    print(f"\nListo. Informe: python informe_101.py {manifiesto_path}")
    return 0


def _mostrar(carpeta: Path) -> str:
    try:
        return carpeta.relative_to(AQUI).as_posix()
    except ValueError:
        return str(carpeta)


if __name__ == "__main__":
    sys.exit(main())
