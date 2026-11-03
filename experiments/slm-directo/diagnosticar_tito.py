"""Diagnóstico del Tito histórico sobre la partición de diagnóstico (#98).

Recorre material de conversaciones no usado en el ajuste del artefacto con el
Tito viejo inalterado (RoBERTuito congelado + única regresión logística seed
42 sobre 5.520 frases aceptadas del banco histórico, entrada aislada de frase
actual, umbral de derivación 0,5) y registra puntajes por línea, derivaciones,
oportunidad respecto de las marcas disponibles y costo de arranque/ejecución
por separado.

No entrena, no ajusta pesos, no usa la reserva final (`CV2-T-*`), no usa las
veinte de comparación y no ejecuta SLM: la derivación de Tito no es una alerta
y una conversación sin derivación no es una prueba de legitimidad. Las marcas
`T_R`/`T_C` y clases provienen de referencias sin revisión humana
(`revision_humana: false`): son provisionales y no habilitan la puerta formal
de `datos_tito.py`; el diagnóstico es exploratorio de desarrollo.

Uso desde `experiments/slm-directo/`:

    .venv/bin/python diagnosticar_tito.py --salida DIAGNOSTICO-TITO-2026-10-29.json

Escribe el JSON (manifiesto + trazas + auditoría, comparador recargable) y un
`.md` con el mismo basename (reporte por conversación y dificultad).
La recarga del comparador para #101 se verifica reinstanciando el artefacto
y re-puntuando los textos guardados en el propio JSON: los puntajes deben
coincidir dentro de la tolerancia declarada (`TOLERANCIA_RECARGA`, mitad del
último dígito exhibido), con al menos una inferencia válida y sin fallos; no
se afirma exactitud bit a bit.

Regenerar solo el `.md` desde un JSON ya corrido (sin inferencia, sin modelos):

    .venv/bin/python diagnosticar_tito.py --regenerar-md DIAGNOSTICO-TITO-2026-10-29.json
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
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import casos  # noqa: E402
import tito_real  # noqa: E402
from datos_tito import es_identificador_reserva  # noqa: E402

ARTEFACTO = tito_real.ARTEFACTO_POR_DEFECTO
PARTICIONES = AQUI / "PARTICIONES-TITO-2026-10-29.json"
SELECCION = AQUI / "SELECCION-TITO-2026-10-28.json"
CONFIG = AQUI / "CONFIGURACION-TITO-2026-10-29.json"
UMBRAL = 0.5
ENTRADA = "frase_actual_aislada"
BANCO_COMMIT = "bb542e130e7a67a82e376a75a0438a15de32f4a6"
SEMILLA = 42
# Mitad del último dígito exhibido (puntajes a 4 decimales): la recarga del
# comparador afirma acuerdo dentro de esta tolerancia, no exactitud bit a bit.
TOLERANCIA_RECARGA = 5e-5


def sha_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_archivo(ruta: Path) -> str:
    return sha_bytes(ruta.read_bytes())


def _normalizar(texto: str) -> str:
    texto = texto.casefold()
    texto = re.sub(r"[^\w\s]", " ", texto, flags=re.UNICODE)
    return re.sub(r"\s+", " ", texto).strip()


def _tokens(texto: str) -> frozenset:
    return frozenset(t for t in _normalizar(texto).split() if len(t) > 2)


def _modelo_cpu() -> str:
    """Modelo real de CPU (no solo arquitectura): lscpu, /proc/cpuinfo o fallback."""
    for ruta in ("/proc/cpuinfo",):
        try:
            for renglon in Path(ruta).read_text().splitlines():
                if renglon.startswith("model name"):
                    return renglon.split(":", 1)[1].strip()
        except OSError:
            pass
    try:
        proc = subprocess.run(["lscpu"], capture_output=True, text=True,
                              timeout=10)
        for renglon in (proc.stdout or "").splitlines():
            if "Model name" in renglon:
                return renglon.split(":", 1)[1].strip()
    except Exception:  # noqa: BLE001 - solo informativo
        pass
    return platform.processor() or "no informado"


def _ram_total_gb() -> float | None:
    try:
        for renglon in Path("/proc/meminfo").read_text().splitlines():
            if renglon.startswith("MemTotal:"):
                return round(int(renglon.split()[1]) / 1024 ** 2, 1)
    except OSError:
        pass
    return None


def info_runtime() -> dict:
    return {
        "python": platform.python_version(),
        "sistema": platform.system(),
        "release": platform.release(),
        "maquina_cpu": platform.machine(),
        "procesador": platform.processor() or "no informado",
        "cpu_modelo": _modelo_cpu(),
        "nucleos": os.cpu_count(),
        "ram_total_gb": _ram_total_gb(),
        "ejecutable_python": sys.executable,
    }


def info_librerias() -> dict:
    info: dict = {}
    for nombre, atributo in (("torch", "__version__"),
                             ("transformers", "__version__"),
                             ("huggingface_hub", "__version__"),
                             ("tokenizers", "__version__")):
        try:
            modulo = __import__(nombre)
            info[nombre] = getattr(modulo, atributo, "?")
        except Exception as e:  # noqa: BLE001 - se registra, no se interrumpe
            info[nombre] = f"no_disponible: {type(e).__name__}"
    try:
        proc = subprocess.run(["ollama", "--version"], capture_output=True,
                              text=True, timeout=30)
        info["ollama_cli"] = (proc.stdout or proc.stderr).strip() or "sin_salida"
    except Exception as e:  # noqa: BLE001
        info["ollama_cli"] = f"no_disponible: {type(e).__name__}"
    return info


def git_head() -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, timeout=30, cwd=AQUI)
        return proc.stdout.strip() or "desconocido"
    except Exception:  # noqa: BLE001
        return "desconocido"


def cargar_particion_diagnostico() -> tuple[list[str], dict, dict]:
    """IDs de diagnóstico verificados, fail-closed.

    Rechaza identificadores de reserva, particiones reservadas, cualquier
    intersección con las veinte de comparación y grupos partidos (una parte
    en diagnóstico y otra en otra partición, salvo el par
    comparación/excluida que declara la preparación).
    """
    particiones = json.loads(PARTICIONES.read_text(encoding="utf-8"))
    filas = particiones["conversaciones"]
    diagnostico = sorted(c["case_id"] for c in filas
                         if c["particion_preparacion"] == "diagnostico")
    if not diagnostico:
        raise ValueError("partición de diagnóstico vacía: nada que diagnosticar.")
    for cid in diagnostico:
        if es_identificador_reserva(cid):
            raise ValueError(f"{cid}: reserva final rechazada sin leerla.")
    evaluacion = set(particiones.get("evaluacion_ids", []))
    interseccion = set(diagnostico) & evaluacion
    if interseccion:
        raise ValueError(f"diagnóstico intersecta comparación: {sorted(interseccion)}.")
    grupos: dict[str, set[str]] = {}
    for c in filas:
        grupos.setdefault(c["grupo_preparacion"], set()).add(
            c["particion_preparacion"])
    for cid in diagnostico:
        grupo = next(c["grupo_preparacion"] for c in filas if c["case_id"] == cid)
        partes = grupos[grupo]
        if partes != {"diagnostico"}:
            raise ValueError(f"{cid}: grupo {grupo} partido en {sorted(partes)}.")
    seleccion = json.loads(SELECCION.read_text(encoding="utf-8"))
    huellas_sel = {r["case_id"]: r for r in seleccion["conversaciones"]}
    huellas_part = {c["case_id"]: c for c in filas}
    for cid in diagnostico:
        if cid not in huellas_sel:
            raise ValueError(f"{cid}: sin huella en la selección aprobada.")
        if huellas_sel[cid]["texto_sha256"] != huellas_part[cid]["texto_sha256"]:
            raise ValueError(f"{cid}: deriva entre particiones y selección "
                             f"(texto_sha256).")
        if (huellas_sel[cid]["referencia_sha256"]
                != huellas_part[cid]["referencia_sha256"]):
            raise ValueError(f"{cid}: deriva entre particiones y selección "
                             f"(referencia_sha256).")
        for campo, subdir, ext in (("texto_sha256", "texto", "txt"),
                                   ("referencia_sha256", "referencia", "json")):
            crudo = (AQUI / "casos" / subdir / f"{cid}.{ext}").read_bytes()
            if sha_bytes(crudo) != huellas_sel[cid][campo]:
                raise ValueError(f"{cid}: cambió {campo}; revisar antes de usar.")
            if sha_bytes(crudo) != huellas_part[cid][campo]:
                raise ValueError(f"{cid}: {campo} no coincide con particiones; "
                                 f"revisar antes de usar.")
    return diagnostico, particiones, seleccion


def huellas_diagnostico(ids: list[str]) -> dict:
    """Huellas de las fuentes y de cada conversación del diagnóstico.

    Manifiesto verificable: sha256 de particiones/configuración/selección más
    texto/referencia por conversación. Permite detectar deriva entre archivos
    sin releer el banco ni re-ejecutar el encoder.
    """
    detalle = []
    for cid in ids:
        texto = (AQUI / "casos" / "texto" / f"{cid}.txt").read_bytes()
        ref = (AQUI / "casos" / "referencia" / f"{cid}.json").read_bytes()
        detalle.append({"case_id": cid,
                        "texto_sha256": sha_bytes(texto),
                        "referencia_sha256": sha_bytes(ref)})
    return {
        "fuentes": {
            "particiones": str(PARTICIONES),
            "particiones_sha256": sha_archivo(PARTICIONES),
            "configuracion": str(CONFIG),
            "configuracion_sha256": sha_archivo(CONFIG),
            "seleccion": str(SELECCION),
            "seleccion_sha256": sha_archivo(SELECCION),
        },
        "conversaciones": detalle,
    }


def cargar_banco_historico() -> tuple[list[str], dict]:
    """Frases que vio el Tito viejo, con la auditoría de `entrenar_tito`.

    Reutiliza `entrenar_tito.cargar_banco` (verifica hashes de
    `ejemplos.jsonl`/`exclusiones.json` y conteos 5.520 aceptadas / 480
    apartadas / 276 familias): lo que el ajuste vio son las aceptadas, no el
    inventario total. Distingue inventario (`inventario_total`, todo lo
    listado en el commit) de realmente visto en ajuste (`aceptadas`).
    """
    import entrenar_tito as e
    if e.BANCO_COMMIT != BANCO_COMMIT:
        raise ValueError("commit del banco distinto entre diagnosticar y "
                         "entrenar_tito; revisar antes de usar.")
    try:
        aceptadas, _exclusiones, datos = e.cargar_banco()
    except SystemExit as exc:
        raise ValueError(f"auditoría del banco rechazada: {exc}") from exc
    textos = [f["texto"] for f in aceptadas]
    return textos, {"banco_commit": datos["banco_commit"],
                    "ejemplos_sha256": datos["ejemplos_sha256"],
                    "exclusiones_sha256": datos["exclusiones_sha256"],
                    "inventario_total": datos["aceptadas"] + datos["apartadas"],
                    "aceptadas": datos["aceptadas"],
                    "apartadas": datos["apartadas"],
                    "familias": datos["familias"],
                    "por_clase": datos["por_clase"],
                    "nota": ("el ajuste vio solo las aceptadas (excluidas 480 "
                             "por familias apartadas); el inventario total no "
                             "equivale a material de ajuste.")}


def auditar_solapamiento_semantico(ids: list[str],
                                   frases_banco: list[str]) -> dict:
    """Solapamiento léxico (Jaccard sobre tokens) banco ↔ diagnóstico.

    No prueba independencia semántica: es una cota inferior observable. Un
    valor alto indica exposición temática del Tito viejo a ese contenido;
    un valor bajo no acredita independencia.
    """
    conjuntos_banco = [_tokens(f) for f in frases_banco]
    por_linea: list[dict] = []
    for cid in ids:
        for n, linea in enumerate(casos.cargar_texto(cid), start=1):
            toks = _tokens(linea.texto)
            mejor = 0.0
            if toks:
                for base in conjuntos_banco:
                    if not base:
                        continue
                    inter = len(toks & base)
                    if inter:
                        jacc = inter / len(toks | base)
                        if jacc > mejor:
                            mejor = jacc
            por_linea.append({"case_id": cid, "linea": n,
                              "jaccard_max": round(mejor, 3)})
    valores = [p["jaccard_max"] for p in por_linea]
    altos = [p for p in por_linea if p["jaccard_max"] >= 0.7]
    return {
        "metodo": "jaccard_tokens_minusculas_sin_puntuacion_palabras_mayores_2",
        "n_lineas_diagnostico": len(por_linea),
        "n_frases_banco": len(conjuntos_banco),
        "jaccard_maximo": max(valores) if valores else 0.0,
        "jaccard_mediano": round(sorted(valores)[len(valores) // 2], 3) if valores else 0.0,
        "lineas_con_jaccard_alto_ge_07": altos,
        "advertencia": ("valores altos = exposición temática probable; valores bajos "
                        "no acreditan independencia semántica."),
    }


def identificar_artefacto(sha_antes: str, sha_despues: str) -> dict:
    """Identidad del artefacto histórico y prueba de que no se modificó."""
    arte = tito_real.cargar_artefacto(ARTEFACTO)
    if sha_antes != sha_despues:
        raise ValueError("el artefacto cambió durante el diagnóstico.")
    return {
        "ruta": str(ARTEFACTO),
        "sha256": sha_antes,
        "formato": arte.get("formato"),
        "encoder": arte["encoder"],
        "tokenizador": arte["tokenizador"],
        "clasificador": {"tipo": "regresion_logistica",
                         **arte["config_regresion"]},
        "entrada": ENTRADA,
        "umbral_derivacion": float(arte.get("umbral_derivacion", UMBRAL)),
        "pesos_modificados": False,
        "nota": ("cargar_artefacto solo lee y valida; puntuar no ajusta. "
                 "sha idéntico antes y después del recorrido."),
    }


def recorrer_conversacion(tito, cid: str, lineas=None, ref=None) -> dict:
    """Puntaje por línea con entrada aislada; primera derivación >= umbral."""
    if lineas is None:
        lineas = casos.cargar_texto(cid)
    if ref is None:
        ref = casos.cargar_referencia(cid)
    filas = []
    derivacion = None
    for n, linea in enumerate(lineas, start=1):
        puntaje, error, ms = tito.puntuar(n, linea.texto)
        if puntaje is not None and derivacion is None and puntaje >= UMBRAL:
            derivacion = n
        filas.append({"linea": n, "hablante": linea.hablante,
                      "texto": linea.texto,
                      "puntaje": None if puntaje is None else round(puntaje, 4),
                      "tito_error": error, "tito_ms": round(ms, 1),
                      "deriva": puntaje is not None and puntaje >= UMBRAL})
    t_r = ref.get("t_r_linea")
    t_c = ref.get("t_c_linea")
    if derivacion is not None and t_r is not None:
        oportunidad = ("antes_del_pedido" if derivacion < t_r
                       else "en_el_pedido" if derivacion == t_r
                       else "despues_del_pedido")
    elif derivacion is not None:
        oportunidad = "sin_marca_T_R"
    else:
        oportunidad = "sin_derivacion"
    return {
        "case_id": cid,
        "clase": ref.get("clase"),
        "n_lineas": len(lineas),
        "revision_humana": ref.get("revision_humana", False),
        "provisional": not ref.get("revision_humana", False),
        "t_r_linea": t_r, "t_c_linea": t_c, "pedido": ref.get("pedido"),
        "n_evidencia": len(ref.get("evidencia", [])),
        "derivacion_linea": derivacion,
        "oportunidad_vs_T_R": oportunidad,
        "legitima_derivada": ref.get("clase") != "vishing" and derivacion is not None,
        "omision_oportuna": (ref.get("clase") == "vishing" and t_r is not None
                             and (derivacion is None or derivacion > t_r)),
        "puntajes": filas,
    }


def resumir(recorridos: list[dict]) -> dict:
    vishing = [r for r in recorridos if r["clase"] == "vishing"]
    legitimas = [r for r in recorridos if r["clase"] != "vishing"]
    derivadas_leg = [r["case_id"] for r in legitimas if r["derivacion_linea"]]
    return {
        "n_conversaciones": len(recorridos),
        "n_vishing": len(vishing),
        "n_legitimas": len(legitimas),
        "vishing_con_derivacion": sum(1 for r in vishing if r["derivacion_linea"]),
        "vishing_sin_derivacion": [r["case_id"] for r in vishing
                                   if not r["derivacion_linea"]],
        "omisiones_oportunas_vs_T_R": [
            {"case_id": r["case_id"], "derivacion": r["derivacion_linea"],
             "t_r": r["t_r_linea"]} for r in vishing if r["omision_oportuna"]],
        "legitimas_derivadas": derivadas_leg,
        "tasa_derivacion_legitimas": (round(len(derivadas_leg) / len(legitimas), 3)
                                      if legitimas else None),
        "denominadores": {
            "vishing_total": len(vishing),
            "vishing_con_T_R": sum(1 for r in vishing if r["t_r_linea"]),
            "vishing_con_T_C": sum(1 for r in vishing if r["t_c_linea"]),
            "legitimas_total": len(legitimas),
        },
    }


def costos_actualizaciones(recorridos: list[dict], truncamientos=None) -> dict:
    mss = [f["tito_ms"] for r in recorridos for f in r["puntajes"]]
    mss_ord = sorted(mss)
    fallos = [(r["case_id"], f["linea"], f["tito_error"]) for r in recorridos
              for f in r["puntajes"] if f["tito_error"]]
    return {
        "n_actualizaciones": len(mss),
        "ms_min": min(mss) if mss else None,
        "ms_p50": mss_ord[len(mss_ord) // 2] if mss else None,
        "ms_p95": mss_ord[int(len(mss_ord) * 0.95)] if mss else None,
        "ms_max": max(mss) if mss else None,
        "fallos_tecnicos": fallos,
        "truncamientos_mayores_128": truncamientos,
        "unidad": "ms",
        "nota": ("cómputo en ms por actualización de frase aislada; sin "
                 "latencia de audio ni RTF: no hubo audio en este diagnóstico."),
    }


def verificar_recarga(ids: list[str], recorridos: list[dict]) -> dict:
    """El comparador recargable reproduce los puntajes dentro de tolerancia.

    Reinstancia el artefacto y re-puntúa los textos guardados en el propio
    informe (no relee archivos). Cuenta comparaciones, inferencias válidas,
    fallos (puntaje `None` en la corrida o en la recarga: un `None == None`
    nunca cuenta como reproducción) y distintos fuera de `TOLERANCIA_RECARGA`.
    `reproduce` exige al menos una inferencia válida, cero fallos y cero
    distintos: sin inferencias válidas el comparador no se acepta.
    """
    por_cid = {r["case_id"]: r for r in recorridos}
    tito2, _ = tito_real.preparar_tito_real(ARTEFACTO)
    total = 0
    validas = 0
    fallos: list[dict] = []
    distintos: list[dict] = []
    for cid in ids:
        for f in por_cid[cid]["puntajes"]:
            total += 1
            puntaje, error, _ = tito2.puntuar(f["linea"], f["texto"])
            esperado = f["puntaje"]
            if puntaje is None or esperado is None:
                fallos.append({"case_id": cid, "linea": f["linea"],
                               "recarga_error": error,
                               "corrida_error": f.get("tito_error", "")})
                continue
            validas += 1
            if abs(puntaje - esperado) > TOLERANCIA_RECARGA:
                distintos.append({"case_id": cid, "linea": f["linea"],
                                  "corrida": esperado, "recarga": puntaje})
    reproduce = validas > 0 and not fallos and not distintos
    if validas == 0:
        nota = ("sin inferencias válidas: comparador no aceptado "
                "(None == None no es reproducción).")
    elif fallos:
        nota = (f"{len(fallos)} fallos técnicos: comparador no aceptado.")
    elif distintos:
        nota = (f"{len(distintos)} puntajes fuera de tolerancia "
                f"{TOLERANCIA_RECARGA}: comparador no aceptado.")
    else:
        nota = (f"acuerdo dentro de tolerancia_abs {TOLERANCIA_RECARGA} "
                f"(mitad del último dígito exhibido); no exactitud bit a bit.")
    return {"reinstancias": 2, "comparaciones": total,
            "validas": validas, "fallos_n": len(fallos), "fallos": fallos,
            "distintos_n": len(distintos), "distintos": distintos,
            "tolerancia_abs": TOLERANCIA_RECARGA,
            "reproduce": reproduce, "nota": nota}


def diagnosticar(tito=None) -> dict:
    sha_antes = sha_archivo(ARTEFACTO)
    ids, particiones, _seleccion = cargar_particion_diagnostico()
    frases_banco, info_banco = cargar_banco_historico()
    solapamiento = auditar_solapamiento_semantico(ids, frases_banco)
    if tito is None:
        tito, preparacion = tito_real.preparar_tito_real(ARTEFACTO)
    else:
        preparacion = {"artefacto_ms": None, "encoder_ms": None,
                       "calentamiento_ms": None, "doble": True,
                       "nota": "doble inyectado para pruebas; no mide costo real."}
    recorridos = [recorrer_conversacion(tito, cid) for cid in ids]
    truncamientos = getattr(tito, "truncamientos", None)
    sha_despues = sha_archivo(ARTEFACTO)
    informe = {
        "issue": 98,
        "fecha": "2026-10-29",
        "semilla": SEMILLA,
        "artefacto_historico": identificar_artefacto(sha_antes, sha_despues),
        "particion": {"nombre": "diagnostico", "ids": ids,
                      "fuente": str(PARTICIONES),
                      "configuracion": str(CONFIG),
                      "comparacion_20_excluida": True,
                      "reserva_rechazada": True,
                      "verificacion_fuentes": huellas_diagnostico(ids)},
        "exposicion_historica": {
            **info_banco,
            "conversaciones_diagnostico_en_ajuste": False,
            "banco_visto_por_tito_viejo_en_validacion_nueva": True,
            "nota": ("el ajuste usó solo las aceptadas del banco; ninguna "
                     "conversación entera estuvo en el ajuste. La validación "
                     "del banco no es independiente del Tito viejo."),
        },
        "auditoria_semantica": solapamiento,
        "puerta_formal_datos_tito": {
            "habilitada": False,
            "motivo": ("referencias sin revisión humana "
                       "(revision_humana: false en las 10): diagnóstico "
                       "exploratorio de desarrollo, no evaluación independiente."),
        },
        "preparacion_costos": preparacion,
        "recorridos": recorridos,
        "resumen": resumir(recorridos),
        "costos_actualizaciones": costos_actualizaciones(recorridos,
                                                         truncamientos),
        "recarga_comparador": (verificar_recarga(ids, recorridos)
                               if tito is not None and not preparacion.get("doble")
                               else {"reproduce": None,
                                     "nota": "solo con Tito real en la corrida."}),
        "runtime": info_runtime(),
        "librerias": info_librerias(),
        "codigo": {"git_head": git_head(),
                   "scripts_sha256": {n: sha_archivo(AQUI / n) for n in
                                      ("diagnosticar_tito.py", "tito_real.py",
                                       "filtro_tito.py", "casos.py",
                                       "datos_tito.py", "entrenar_tito.py")}},
        "reproducir": {
            "corrida": ("../../.venv/bin/python diagnosticar_tito.py --salida "
                        "DIAGNOSTICO-TITO-2026-10-29.json"),
            "regenerar_md": ("../../.venv/bin/python diagnosticar_tito.py "
                             "--regenerar-md DIAGNOSTICO-TITO-2026-10-29.json"),
            "nota": "regenerar_md reescribe el .md desde el JSON sin inferencia.",
        },
        "limites": [
            "La auditoría semántica completa banco↔conversaciones es ownership "
            "de #99 (worker paralelo); acá solo cota inferior léxica (Jaccard), "
            "documentada honestamente sin presumir independencia.",
            "Sin revisión humana: marcas T_R/T_C provisionales; no cierra D07.",
            "Sin SLM en este diagnóstico: la derivación no es alerta; no cierra D08.",
            "Sin selección de modelos ni fine-tuning: no cierra D09.",
            "Diagnóstico con n=10 (2 vishing del mismo grupo): describe, no generaliza.",
            "La auditoría Jaccard es cota inferior de solapamiento, no prueba de independencia.",
        ],
    }
    return informe


def _linea_exposicion(informe: dict) -> str:
    exp = informe["exposicion_historica"]
    if "aceptadas" in exp:
        return (
            f"- Exposición histórica: ajuste con {exp['aceptadas']} frases "
            f"aceptadas del banco (inventario {exp['inventario_total']}, "
            f"excluidas {exp['apartadas']}) commit "
            f"`{exp['banco_commit'][:7]}` "
            f"(ejemplos `{exp['ejemplos_sha256'][:12]}…`, "
            f"exclusiones `{exp['exclusiones_sha256'][:12]}…`); "
            "ninguna conversación entera estuvo en el ajuste.")
    return (
        f"- Exposición histórica: ajuste con {exp.get('n_registros')} frases "
        f"del banco commit `{exp.get('banco_commit', '')[:7]}` (inventario sin "
        "distinguir aceptadas; regenerar con la versión que reutiliza la "
        "auditoría de `entrenar_tito`); ninguna conversación entera estuvo "
        "en el ajuste.")


def _linea_fuentes(informe: dict) -> str:
    verif = informe["particion"].get("verificacion_fuentes")
    if not verif:
        return ("- Fuentes: sin huellas de particiones/configuración/selección "
                "(JSON de corrida anterior; regenerar).")
    f = verif["fuentes"]
    return (
        f"- Fuentes: particiones `{f['particiones_sha256'][:12]}…`, "
        f"configuración `{f['configuracion_sha256'][:12]}…`, "
        f"selección `{f['seleccion_sha256'][:12]}…` "
        "(verificadas contra archivos y entre sí, sin deriva).")


def _linea_reproducir(informe: dict) -> str:
    rep = informe["reproducir"]
    if isinstance(rep, dict):
        return (f"- Corrida: `{rep['corrida']}` desde `experiments/slm-directo/`.\n"
                f"- Solo MD (sin inferencia): `{rep['regenerar_md']}`.")
    return f"- Comando: `{rep}` desde `experiments/slm-directo/`."


def a_markdown(informe: dict) -> str:
    a = informe["artefacto_historico"]
    r = informe["resumen"]
    c = informe["costos_actualizaciones"]
    p = informe["preparacion_costos"]
    sol = informe["auditoria_semantica"]
    lineas = [
        "# Diagnóstico del Tito histórico sobre la partición de diagnóstico (#98)",
        "",
        f"Fecha: {informe['fecha']}. Semilla: {informe['semilla']}. "
        f"Código: `{informe['codigo']['git_head']}`.",
        "",
        "> Referencias sin revisión humana: marcas provisionales. Diagnóstico "
        "exploratorio de desarrollo; no evaluación independiente, no cierra "
        "D07/D08/D09.",
        "",
        "## Artefacto histórico (sin modificar)",
        "",
        f"- Ruta: `{a['ruta']}`; sha256: `{a['sha256']}` (idéntico antes/después).",
        f"- Encoder: `{a['encoder']['id']}` revisión `{a['encoder']['revision']}` "
        f"congelado, {a['encoder']['representacion']}, hidden {a['encoder']['hidden']}.",
        f"- Tokenizador límite {a['tokenizador']['limite_tokens']} tokens, "
        f"truncados en ajuste: {a['tokenizador']['truncados_en_128']}.",
        f"- Clasificador: regresión logística {a['clasificador']}.",
        f"- Entrada: {a['entrada']}. Umbral de derivación: "
        f"{informe['artefacto_historico']['umbral_derivacion']} "
        "(igualdad incluida).",
        "",
        "## Partición usada",
        "",
        f"- Diagnóstico: {len(informe['particion']['ids'])} conversaciones "
        f"({', '.join(informe['particion']['ids'])}).",
        "- Reserva final rechazada sin leer; veinte de comparación excluidas; "
        "grupos verificados sin partir.",
        _linea_exposicion(informe),
        _linea_fuentes(informe),
        f"- Solapamiento léxico banco↔diagnóstico: Jaccard máximo {sol['jaccard_maximo']}, "
        f"mediano {sol['jaccard_mediano']} sobre {sol['n_lineas_diagnostico']} líneas; "
        f"{len(sol['lineas_con_jaccard_alto_ge_07'])} líneas ≥ 0,7.",
        "",
        "## Recorrido por conversación",
        "",
        "| Conversación | Clase | Líneas | T_R | T_C | Derivación | Oportunidad |",
        "|---|---|---:|---|---|---|---|",
    ]
    for rec in informe["recorridos"]:
        lineas.append(
            f"| {rec['case_id']} | {rec['clase']} | {rec['n_lineas']} | "
            f"{rec['t_r_linea']} | {rec['t_c_linea']} | {rec['derivacion_linea']} | "
            f"{rec['oportunidad_vs_T_R']} |")
    lineas += [
        "",
        "Posiciones en líneas, no en segundos: el texto no trae timestamps.",
        "",
        "### Detalle por conversación (fragmento que deriva o puntajes máximos)",
        "",
    ]
    for rec in informe["recorridos"]:
        if rec["derivacion_linea"] is not None:
            f = next(x for x in rec["puntajes"]
                     if x["linea"] == rec["derivacion_linea"])
            lineas.append(
                f"- {rec['case_id']} ({rec['clase']}): deriva en línea "
                f"{f['linea']} con puntaje {f['puntaje']}: «{f['texto']}».")
        else:
            top = sorted((x for x in rec["puntajes"] if x["puntaje"] is not None),
                         key=lambda x: -x["puntaje"])[:2]
            txt = "; ".join(f"L{x['linea']}={x['puntaje']}: «{x['texto']}»"
                            for x in top)
            lineas.append(
                f"- {rec['case_id']} ({rec['clase']}): sin derivación; máximos {txt}.")
    lineas += [
        "",
        "Dificultad: las 8 legítimas son comunes (ninguna `legitima_dificil`); "
        "los 2 vishing pertenecen al mismo grupo de escenario "
        "(CV2-D-V-BANCO-003). Muestra pequeña: describe, no generaliza.",
        "",
        "## Resumen",
        "",
        f"- Vishing con derivación: {r['vishing_con_derivacion']}/{r['denominadores']['vishing_total']} "
        f"(con T_R: {r['denominadores']['vishing_con_T_R']}, con T_C: "
        f"{r['denominadores']['vishing_con_T_C']}).",
        f"- Sin derivación: {r['vishing_sin_derivacion'] or 'ninguno'}.",
        f"- Omisiones oportunas vs T_R: {r['omisiones_oportunas_vs_T_R'] or 'ninguna'}.",
        f"- Legítimas derivadas: {r['legitimas_derivadas'] or 'ninguna'} "
        f"(tasa {r['tasa_derivacion_legitimas']}).",
        "- Derivación ≠ alerta; omisión ≠ legitimidad: Tito solo deriva al SLM.",
        "",
        "## Costos (ms, separados)",
        "",
        f"- Arranque: artefacto {p.get('artefacto_ms')} ms, encoder {p.get('encoder_ms')} ms, "
        f"calentamiento {p.get('calentamiento_ms')} ms.",
        f"- Ejecución: {c['n_actualizaciones']} actualizaciones, p50 {c['ms_p50']} ms, "
        f"p95 {c['ms_p95']} ms, máx {c['ms_max']} ms; fallos: {len(c['fallos_tecnicos'])}; "
        f"truncadas >128 tokens: {c['truncamientos_mayores_128']}.",
        "- Sin latencia de audio ni RTF: no hubo audio en este diagnóstico.",
        "",
        "## Interpretación",
        "",
        "- Falta de validación: sin revisión humana no hay verdad de referencia "
        "formal; los conteos son descriptivos de desarrollo.",
        "- Errores observados: ver tabla y JSON por línea (puntaje, derivación, "
        "oportunidad, legítimas derivadas).",
        "- Causas no aisladas: puntajes altos o banco grande no prueban por sí "
        "solos buen o mal ajuste; el ajuste se juzga en #99 contra validación.",
        "",
        "## Comparador recargable para #101",
        "",
        f"- Recarga: `tito_real.cargar_artefacto` + `TitoReal` + `puntuar(n, frase)` "
        f"con umbral {informe['artefacto_historico']['umbral_derivacion']}; "
        f"reproduce puntajes: {informe['recarga_comparador'].get('reproduce')} "
        f"({informe['recarga_comparador'].get('validas')}/"
        f"{informe['recarga_comparador'].get('comparaciones')} válidas, "
        f"fallos {informe['recarga_comparador'].get('fallos_n')}, "
        f"distintos {informe['recarga_comparador'].get('distintos_n')}, "
        f"tolerancia {informe['recarga_comparador'].get('tolerancia_abs')}).",
        "- Diagnóstico no sustituye la corrida Tito viejo→SLM con los diez "
        "modelos de #101.",
        "",
        "## Reproducir",
        "",
        _linea_reproducir(informe),
        f"- Hardware/runtime en el JSON (`runtime`, `librerias`, `codigo`): "
        f"{informe['runtime'].get('cpu_modelo', 'no informado')} con "
        f"{informe['runtime'].get('ram_total_gb')} GB RAM.",
    ]
    return "\n".join(lineas) + "\n"


def escribir_md_desde_json(ruta_json: Path) -> Path:
    """Reescribe el `.md` desde un JSON ya corrido, sin inferencia ni modelos."""
    informe = json.loads(ruta_json.read_text(encoding="utf-8"))
    destino = ruta_json.with_suffix(".md")
    destino.write_text(a_markdown(informe), encoding="utf-8")
    return destino


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida", type=Path, default=None,
                        help="ruta del JSON (el .md se escribe al lado)")
    parser.add_argument("--regenerar-md", type=Path, default=None,
                        help="ruta de un JSON ya corrido: reescribe solo el "
                             ".md sin inferencia ni modelos")
    args = parser.parse_args(argv)
    if args.regenerar_md is not None:
        destino = escribir_md_desde_json(args.regenerar_md)
        print(f"md_regenerado={destino}")
        return 0
    if args.salida is None:
        parser.error("--salida es obligatorio sin --regenerar-md.")
    informe = diagnosticar()
    args.salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2,
                                      sort_keys=True) + "\n", encoding="utf-8")
    args.salida.with_suffix(".md").write_text(a_markdown(informe),
                                             encoding="utf-8")
    rec = informe["recarga_comparador"]
    print(f"conversaciones={informe['resumen']['n_conversaciones']} "
          f"vishing_derivan={informe['resumen']['vishing_con_derivacion']}/"
          f"{informe['resumen']['denominadores']['vishing_total']} "
          f"legitimas_derivadas={len(informe['resumen']['legitimas_derivadas'])} "
          f"recarga_reproduce={rec.get('reproduce')}")
    if rec.get("reproduce") is False:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
