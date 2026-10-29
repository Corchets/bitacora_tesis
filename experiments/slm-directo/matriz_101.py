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
             desde el manifiesto; las veinte nunca se usan para entrenar
             ni seleccionar (el artefacto llega congelado de #99/#100).

Las tres condiciones terminan al primer aviso válido (incluso en
legítimas); sin aviso llegan hasta el final. Solo el SLM avisa; un error
técnico de Tito deriva por fail-open sin fabricar sospecha.

Inventario antes de medir: tag exacto, digest (`/api/tags`), cuantización
(`/api/show`) y versión de Ollama (`/api/version`) por modelo. Sin
`latest`, sin alias, sin sustituciones, sin descargas: lo ausente se
registra como bloqueo con cobertura pendiente explícita.

Uso:
    python matriz_101.py --url http://127.0.0.1:11435 \\
        --tito-nuevo-modelo tito_99_historial_C1.0.json
    python matriz_101.py --modelos qwen3.5:2b --casos CV2-D-V-BANCO-001
    python matriz_101.py --reanudar corridas/2026-10-29_HHMMSS_101

Después: python informe_101.py <carpeta> regenera el reporte sin inferencia.

No declara éxito ni adopta metas (95/5 sigue abierta en D08): informa
conteos, denominadores, costos y pendientes.
"""

from __future__ import annotations

import argparse
import csv
import json
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

CONDICIONES = ("directo", "tito-viejo", "tito-nuevo")


def casos_101() -> list[str]:
    """Las veinte conversaciones aprobadas (fuente: particiones, `evaluacion_ids`)."""
    ids = json.loads(PARTICIONES.read_text(encoding="utf-8"))["evaluacion_ids"]
    if len(ids) != 20:
        raise ValueError(f"evaluacion_ids debe tener 20 casos, tiene {len(ids)}.")
    return list(ids)


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


def cargar_tito_nuevo(ruta: Path | None):
    """Candidato #99/#100 congelado, una vez por proceso.

    Importa `entrenar_tito_99` solo para recargar el artefacto (sin
    reentrenar) y prepara el encoder fuera de las latencias. Si la ruta
    falta, levanta `TitoNuevoNoDisponible`: la condición se registra
    como pendiente, no se improvisa otro Tito.
    """
    if ruta is None or not Path(ruta).exists():
        raise TitoNuevoNoDisponible(f"sin artefacto del candidato nuevo: {ruta}.")
    import entrenar_tito_99

    tito = entrenar_tito_99.Tito99(ruta)
    informe = preparar_tito_99(tito)
    return tito, informe


def preparar_tito_99(tito) -> dict:
    """Preparación explícita del candidato nuevo, fuera de las actualizaciones.

    Carga el encoder y corre un calentamiento (una incrustación del texto
    de ejemplo). Devuelve costos separados sin doble conteo con `puntuar`.
    Un error no levanta: el flujo deriva por fail-open y cada `puntuar`
    registrará su propia causa.
    """
    inicio_enc = time.perf_counter()
    try:
        tito._asegurar_encoder()
    except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
        return {"encoder_ms": round((time.perf_counter() - inicio_enc) * 1000, 1),
                "encoder_desde_cache": False, "calentamiento_ms": None,
                "error": f"tito99_preparar_error: {type(e).__name__}: {e}",
                "unidad": "ms"}
    encoder_ms = round((time.perf_counter() - inicio_enc) * 1000, 1)
    inicio_cal = time.perf_counter()
    try:
        tito.puntuar_entrada("hola mundo")
    except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
        return {"encoder_ms": encoder_ms, "encoder_desde_cache": False,
                "calentamiento_ms": round((time.perf_counter() - inicio_cal) * 1000, 1),
                "error": f"tito99_calentar_error: {type(e).__name__}: {e}",
                "unidad": "ms"}
    return {"encoder_ms": encoder_ms, "encoder_desde_cache": False,
            "calentamiento_ms": round((time.perf_counter() - inicio_cal) * 1000, 1),
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
    """Las tres condiciones de un modelo sobre la misma base SLM."""
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
    import hashlib

    return hashlib.sha256(
        json.dumps(parametros, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]


def plan_triples(modelos: list[str], condiciones: list[str], ids: list[str]) -> list[tuple[str, str, str]]:
    """Un recorrido por (modelo, condición, caso). Con los diez, tres y veinte: 600."""
    return [(m, c, i) for m in modelos for c in condiciones for i in ids]


def leer_completados(carpeta: Path) -> set[tuple[str, str, str]]:
    """Triples ya guardados en la traza (config → modelo, condición, caso)."""
    ruta = carpeta / "actualizaciones.csv"
    if not ruta.exists():
        return set()
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        filas = list(csv.DictReader(f))
    # Un triple está completo si avisó (columna aviso) o recorrió el caso.
    por_triple: dict[tuple[str, str, str], list] = {}
    for fila in filas:
        partes = fila["config"].split("|")
        if len(partes) != 4:
            continue
        por_triple.setdefault((partes[1], partes[0], fila["case_id"]), []).append(fila)
    completados: set[tuple[str, str, str]] = set()
    for triple, fs in por_triple.items():
        if any(f["aviso"] == "true" for f in fs):
            completados.add(triple)
            continue
        try:
            if len(fs) >= len(casos.cargar_texto(triple[2])):
                completados.add(triple)
        except ValueError:
            continue
    return completados


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
                   help="artefacto del candidato #99/#100; ausente → condición pendiente")
    p.add_argument("--tito-nuevo-umbral", type=float, default=UMBRAL_TITO,
                   help="umbral del candidato nuevo (convención exploratoria 0,5 si #99 no fijó otro)")
    p.add_argument("--salida", type=Path, default=AQUI / "corridas")
    p.add_argument("--etiqueta", default="", help="texto corto para el nombre de la carpeta")
    p.add_argument("--reanudar", type=Path, default=None, help="carpeta de una corrida 101 para continuar")
    p.add_argument("--detalle", action="store_true")
    args = p.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    errores = casos.validar_todos()
    if errores:
        print("\n".join(errores))
        sys.exit("Hay casos con errores de formato.")

    modelos = [m.strip() for m in args.modelos.split(",") if m.strip()]
    if [m for m in modelos if m not in MODELOS_101] or len(set(modelos)) != len(modelos):
        sys.exit(f"--modelos debe ser un subconjunto ordenado de la matriz: {','.join(MODELOS_101)}.")
    if modelos != [m for m in MODELOS_101 if m in modelos]:
        sys.exit("Los modelos deben mantener el orden exacto de la matriz #101.")
    ids = casos_101()
    if args.casos:
        pedidos = [c.strip() for c in args.casos.split(",") if c.strip()]
        faltan = [c for c in pedidos if c not in ids]
        if faltan:
            sys.exit(f"Casos fuera de las veinte aprobadas: {faltan}. No se sustituyen.")
        ids = pedidos

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
        tito_nuevo, prep_nuevo = cargar_tito_nuevo(args.tito_nuevo_modelo)
        umbral_nuevo = float(args.tito_nuevo_umbral)
        bloqueo_nuevo = ""
    except TitoNuevoNoDisponible as e:
        tito_nuevo, prep_nuevo, umbral_nuevo, bloqueo_nuevo = None, None, float(args.tito_nuevo_umbral), str(e)
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
        "prompt": args.prompt, "prompt_huella": huella_texto(prompt_txt),
        "hablantes": args.hablantes, "num_ctx": args.num_ctx, "seed": args.seed,
        "timeout": args.timeout, "hardware": extra, "url": args.url,
        "inventario": inventario,
        "tito_viejo": {"artefacto": str(args.tito_viejo_modelo),
                       "sha256": correr.sha_archivo(args.tito_viejo_modelo),
                       "entrada": "frase_actual", "umbral": umbral_viejo},
        "tito_nuevo": ({"artefacto": str(args.tito_nuevo_modelo),
                        "sha256": correr.sha_archivo(args.tito_nuevo_modelo),
                        "entrada": "historial_acumulado", "umbral": umbral_nuevo}
                       if tito_nuevo is not None else {"bloqueo": bloqueo_nuevo}),
    }
    huella = huella_funcional(funcionales)

    if args.reanudar is not None:
        carpeta = args.reanudar.resolve()
        manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        if manifiesto.get("matriz") != "matriz-101":
            sys.exit("La carpeta a reanudar no es una corrida matriz-101.")
        if huella_funcional(manifiesto["funcionales"]) != huella:
            sys.exit("La configuración actual difiere de la corrida a reanudar: "
                     "no se mezclan configuraciones (usá una carpeta nueva).")
        completados = leer_completados(carpeta)
    else:
        nombre = datetime.now().strftime("%Y-%m-%d_%H%M%S") + (f"_{args.etiqueta}" if args.etiqueta else "")
        carpeta = args.salida.resolve() / f"{nombre}_101"
        carpeta.mkdir(parents=True)
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
            "particiones_sha256": correr.sha_archivo(PARTICIONES),
            "configuracion_sha256": correr.sha_archivo(CONFIG_101),
            "ollama": {**arranque, "arranque_ms": None, "modelos": {}},
            "funcionales": funcionales,
            "huella_funcional": huella,
            "tito_viejo_preparacion": prep_viejo,
            "tito_nuevo_preparacion": prep_nuevo,
            "bloqueos_modelo": bloqueos_modelo,
            "bloqueo_nuevo": bloqueo_nuevo,
            "configs": [],
            "casos": {},
            "interrumpida": False,
            "fin": None,
        }
        (carpeta / "actualizaciones.csv").write_text("", encoding="utf-8-sig")
        completados = set()

    def guardar() -> None:
        (carpeta / "manifiesto.json").write_text(
            json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")

    triples = plan_triples(modelos_ok, condiciones, ids)
    pendientes = [t for t in triples if t not in completados]
    manifiesto["cobertura"] = {"esperados": len(triples), "completados": len(completados),
                               "pendientes": len(pendientes)}
    guardar()
    print(f"Matriz #101: {_mostrar(carpeta)} ({len(triples)} recorridos, "
          f"{len(completados)} hechos, {len(pendientes)} pendientes)")

    try:
        with (carpeta / "actualizaciones.csv").open("a", encoding="utf-8-sig", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
            if not completados:
                escritor.writeheader()
            detectores_cache: dict[str, tuple[dict, object]] = {}
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
                        guardar()
                        print("no quedó listo.")
                        sys.exit(f"\n{e}\nLo procesado hasta acá quedó en {_mostrar(carpeta)}.")
                    manifiesto["ollama"]["modelos"][modelo] = {**inventario[modelo], **carga}
                    guardar()
                    print(f"listo ({carga['carga_ms'] / 1000:.1f} s).")
                clave = (modelo, cond)
                if clave not in detectores_cache:
                    ds = construir_detectores(modelo, prompt_txt, args.prompt, args.hablantes,
                                              cliente, args.num_ctx, args.seed, extra, esquema,
                                              tito_viejo, umbral_viejo, tito_nuevo, umbral_nuevo)
                    for cfg, det in ds:
                        if isinstance(det, DetectorSLM):
                            det.pensar = manifiesto["ollama"]["modelos"][modelo].get("pensar")
                        elif isinstance(det, FlujoTitoSLM):
                            det.slm.pensar = manifiesto["ollama"]["modelos"][modelo].get("pensar")
                        detectores_cache[(modelo, cfg["config"].split("|")[0])] = (cfg, det)
                        if cfg not in manifiesto["configs"]:
                            manifiesto["configs"].append(cfg)
                    guardar()
                config, detector = detectores_cache[clave]
                if case_id not in manifiesto["casos"]:
                    manifiesto["casos"][case_id] = correr.sha_archivo(
                        casos.DIR_TEXTO / f"{case_id}.txt")
                lineas = casos.cargar_texto(case_id)
                for n, linea, r, aviso in correr.procesar_caso(detector, lineas, detener_en_aviso=True):
                    escritor.writerow(correr._fila(config, case_id, n, linea, r, aviso))
                    f.flush()
                completados.add((modelo, cond, case_id))
                manifiesto["cobertura"] = {"esperados": len(triples), "completados": len(completados),
                                           "pendientes": len(triples) - len(completados)}
                guardar()
                print(f"   {modelo:14} {cond:10} {case_id}")
    except KeyboardInterrupt:
        manifiesto["interrumpida"] = True
        guardar()
        print("\nCorrida interrumpida: lo procesado hasta acá quedó guardado (reanudá con --reanudar).")
        return 0
    manifiesto["fin"] = datetime.now().isoformat(timespec="seconds")
    guardar()
    print(f"\nListo. Informe: python informe_101.py {_mostrar(carpeta)}")
    return 0


def _mostrar(carpeta: Path) -> str:
    try:
        return carpeta.relative_to(AQUI).as_posix()
    except ValueError:
        return str(carpeta)


if __name__ == "__main__":
    sys.exit(main())
