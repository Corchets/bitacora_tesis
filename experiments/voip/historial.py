"""Carpetas de salida del servidor: qué es una llamada, qué es una prueba y cuáles se descartan.

Cada llamada o prueba vive en `<salida>/<fecha>_<hora>_<microsegundos>/` con su manifiesto,
sus JSONL y el estéreo. Este módulo no sabe nada de la red ni de los motores: recibe la carpeta
de salida y devuelve lo que encuentra, para probarlo con carpetas armadas en un directorio temporal.

> Estado: propuesta sin discutir. Spike del frente 1; no cierra D08 ni D09.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path

LARGO_MAXIMO_REFERENCIA = 2000
FORMATO_FECHA = "%Y-%m-%d_%H%M%S-%f"

# El mismo formato con que servidor.py nombra cada carpeta: es lo único que se acepta como id.
FORMATO_ID = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{6}-\d{6}$")


def leer_manifiesto(carpeta: Path) -> dict | None:
    """El manifiesto de la carpeta, o None si falta o no se puede leer."""
    try:
        manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return manifiesto if isinstance(manifiesto, dict) else None


def carpetas_de_salida(salida: Path) -> list[Path]:
    """Carpetas con nombre de llamada, de la más vieja a la más nueva."""
    try:
        return sorted(d for d in Path(salida).iterdir() if d.is_dir() and FORMATO_ID.match(d.name))
    except OSError:
        return []


def es_prueba(manifiesto: dict) -> bool:
    inicio = manifiesto.get("inicio_panel")
    return isinstance(inicio, dict) and inicio.get("modo") == "asr"


def descartar_pruebas_no_guardadas(salida: Path, conservar: Path | None = None) -> list[str]:
    """Borra las pruebas cuyo manifiesto dice `guardada: false`; devuelve los ids borrados.

    Las llamadas, las pruebas guardadas, las anteriores a esta marca y las carpetas sin
    manifiesto legible no se tocan: borrar solo cuando hay una marca explícita.
    """
    borradas = []
    for carpeta in carpetas_de_salida(salida):
        if conservar is not None and carpeta == Path(conservar):
            continue
        manifiesto = leer_manifiesto(carpeta)
        if manifiesto is not None and es_prueba(manifiesto) and manifiesto.get("guardada") is False:
            shutil.rmtree(carpeta, ignore_errors=True)
            borradas.append(carpeta.name)
    return borradas


def escribir_manifiesto(carpeta: Path, manifiesto: dict) -> None:
    """Reemplaza el manifiesto de una vez: nunca queda a medio escribir."""
    temporal = carpeta / "manifiesto.json.tmp"
    temporal.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    temporal.replace(carpeta / "manifiesto.json")


def validar_referencia(referencia) -> str:
    if not isinstance(referencia, str) or len(referencia) > LARGO_MAXIMO_REFERENCIA:
        raise ValueError(f"«Lo que dije en realidad» debe ser texto de hasta {LARGO_MAXIMO_REFERENCIA} caracteres.")
    return referencia.strip()


def datos_referencia(carpeta: Path, referencia="", por_segmento=None) -> dict:
    """Valida cada referencia contra los segmentos finales reales; el texto global es derivado."""
    if por_segmento is None:
        return {"referencia": validar_referencia(referencia)}
    segmentos = list(dict.fromkeys(str(a["segmento"]) for a in _leer_jsonl(carpeta / "actualizaciones.jsonl")
                                  if a.get("tipo") == "final" and isinstance(a.get("segmento"), int)))
    if not isinstance(por_segmento, dict) or set(por_segmento) != set(segmentos):
        raise ValueError("Agregá una referencia por frase final de esta prueba; puede quedar vacía.")
    referencias = {s: validar_referencia(por_segmento[s]) for s in segmentos}
    return {"referencia": "\n".join(referencias.values()), "referencias_por_segmento": referencias}


def carpeta_de(salida: Path, id_carpeta) -> Path:
    """La carpeta de un id, o ValueError. Rutas, `..` y enlaces simbólicos no son ids."""
    if not isinstance(id_carpeta, str) or not FORMATO_ID.fullmatch(id_carpeta):
        raise ValueError("Elegí una llamada o prueba de la lista.")
    carpeta = Path(salida) / id_carpeta
    if carpeta.is_symlink() or not carpeta.is_dir():
        raise ValueError("Esa llamada o prueba ya no existe.")
    return carpeta


def _leer_jsonl(ruta: Path) -> list[dict]:
    """Las líneas legibles de un JSONL; las rotas se saltean."""
    lineas = []
    try:
        with open(ruta, encoding="utf-8") as archivo:
            for texto in archivo:
                try:
                    dato = json.loads(texto)
                except ValueError:
                    continue
                if isinstance(dato, dict):
                    lineas.append(dato)
    except OSError:
        pass
    return lineas


def _fuente(manifiesto: dict) -> str:
    inicio = manifiesto.get("inicio_panel") if isinstance(manifiesto.get("inicio_panel"), dict) else {}
    if inicio.get("modo") == "asr":
        return "Micrófono"
    fuentes = inicio.get("fuentes") if isinstance(inicio.get("fuentes"), dict) else {}
    otra = fuentes.get("otra") if isinstance(fuentes.get("otra"), dict) else {}
    if otra.get("tipo") == "ejemplo":
        return f"Ejemplo {otra.get('escenario', '')}".strip()
    if otra.get("tipo") == "navegador":
        return {"meet": "Meet", "blackhole": "WhatsApp / BlackHole"}.get(otra.get("origen"), "Navegador")
    return "Segunda notebook · cliente.py"


def _riesgo(evaluacion: dict) -> float | None:
    if not evaluacion.get("valida"):
        return None
    riesgo = evaluacion.get("riesgo")
    return riesgo if isinstance(riesgo, (int, float)) else (1.0 if evaluacion.get("alerta_sugerida") else 0.0)


def _resumen(carpeta: Path, manifiesto: dict | None, actualizaciones: list[dict], detector: list[dict]) -> dict:
    fecha = None
    try:
        fecha = datetime.strptime(carpeta.name, FORMATO_FECHA).isoformat(timespec="seconds")
    except ValueError:
        pass
    m = manifiesto or {}
    config = m.get("config") if isinstance(m.get("config"), dict) else {}
    canales = m.get("canales") if isinstance(m.get("canales"), dict) else {}
    duraciones = [c["inicio_s"] + c["duracion_s"] for c in canales.values()
                  if isinstance(c, dict) and isinstance(c.get("inicio_s"), (int, float))
                  and isinstance(c.get("duracion_s"), (int, float))]
    if not duraciones:
        fines = [a["fin_audio_s"] for a in actualizaciones if isinstance(a.get("fin_audio_s"), (int, float))]
        duraciones = fines[-1:] if fines else []
    corte = config.get("corte_silencio_s")
    if config.get("endpoint_nativo") is True:
        corte = "auto"  # las llamadas anteriores a la opción «Automático» guardaban 0,8 con el endpoint activo
    aviso = (m.get("detector") or {}).get("aviso") if isinstance(m.get("detector"), dict) else None
    if aviso is None:
        aviso = next((e for e in detector if e.get("aviso")), None)
    riesgos = [r for r in map(_riesgo, detector) if r is not None]
    prueba = manifiesto is not None and es_prueba(manifiesto)
    resumen = {
        "id": carpeta.name,
        "fecha": fecha,
        "tipo": "prueba" if prueba else "llamada",
        "incompleta": manifiesto is None,
        "fuente": _fuente(m) if manifiesto is not None else "Sin manifiesto",
        "duracion_s": round(max(duraciones), 3) if duraciones else None,
        "detector": config.get("detector"),
        "modelo": config.get("modelo"),
        "corte_silencio_s": corte,
        "umbral_rms_silencio": config.get("umbral_rms_silencio"),
        "riesgo_maximo": max(riesgos) if riesgos else None,
        "aviso": aviso is not None,
        "aviso_s": aviso.get("t_a") if aviso else None,
    }
    if prueba:
        resumen["referencia"] = m.get("referencia", "")
        if "referencias_por_segmento" in m:
            resumen["referencias_por_segmento"] = m["referencias_por_segmento"]
    return resumen


def _leer_carpeta(carpeta: Path) -> tuple[dict | None, list[dict], list[dict]]:
    return (leer_manifiesto(carpeta), _leer_jsonl(carpeta / "actualizaciones.jsonl"),
            _leer_jsonl(carpeta / "detector.jsonl"))


def listar(salida: Path, excluir: Path | None = None) -> dict:
    """Llamadas y pruebas guardadas, de la más nueva a la más vieja.

    Sin manifiesto (llamada cortada) se lista como incompleta con lo que se pueda leer,
    o se omite si no hay nada legible. `excluir` es la carpeta de la llamada en curso.
    """
    llamadas, pruebas = [], []
    for carpeta in reversed(carpetas_de_salida(salida)):
        if excluir is not None and carpeta == Path(excluir):
            continue
        manifiesto, actualizaciones, detector = _leer_carpeta(carpeta)
        if manifiesto is None:
            if not any(a.get("texto") for a in actualizaciones):
                continue
        elif es_prueba(manifiesto) and manifiesto.get("guardada") is not True:
            continue  # sin marca de guardado no se lista
        resumen = _resumen(carpeta, manifiesto, actualizaciones, detector)
        (pruebas if resumen["tipo"] == "prueba" else llamadas).append(resumen)
    return {"llamadas": llamadas, "pruebas": pruebas}


def detalle(salida: Path, id_carpeta) -> dict:
    """Resumen, conversación por rol (finales del ASR) y aviso del detector de un elemento."""
    carpeta = carpeta_de(salida, id_carpeta)
    manifiesto, actualizaciones, detector = _leer_carpeta(carpeta)
    resumen = _resumen(carpeta, manifiesto, actualizaciones, detector)
    finales: dict[int, dict] = {}
    provisorios: dict[int, dict] = {}
    for a in actualizaciones:
        if not isinstance(a.get("texto"), str) or not isinstance(a.get("segmento"), int):
            continue
        destino = finales if a.get("tipo") == "final" else provisorios
        destino[a["segmento"]] = a
    lineas = []
    for segmento in sorted(set(finales) | set(provisorios), key=lambda s: (finales.get(s) or provisorios[s]).get("n", 0)):
        act = finales.get(segmento) or provisorios[segmento]
        lineas.append({
            "segmento": segmento, "n": act.get("n"), "rol": act.get("canal"), "texto": act["texto"],
            "fin_audio_s": act.get("fin_audio_s"), "disponible_s": act.get("disponible_s"),
            "provisorio": segmento not in finales, "aviso": False,
        })
    aviso = next((e for e in detector if e.get("aviso")), None)
    aviso_resumen = None
    if aviso is not None:
        aviso_resumen = {"t_a": aviso.get("t_a"), "motivo": aviso.get("motivo", ""),
                         "evidencia": aviso.get("evidencia", ""), "riesgo": _riesgo(aviso)}
        # El aviso queda en la última frase cerrada que el detector ya había visto.
        vistas = [l for l in lineas if not l["provisorio"] and isinstance(l["n"], int) and l["n"] <= aviso.get("n", 0)]
        if vistas:
            vistas[-1]["aviso"] = True
    return {"item": resumen, "conversacion": lineas, "aviso": aviso_resumen}


def editar_referencia(salida: Path, id_carpeta, referencia="", por_segmento=None) -> dict:
    """Cambia «Lo que dije en realidad» de una prueba ya guardada y devuelve su resumen."""
    carpeta = carpeta_de(salida, id_carpeta)
    manifiesto = leer_manifiesto(carpeta)
    if manifiesto is None or not es_prueba(manifiesto) or manifiesto.get("guardada") is not True:
        raise ValueError("Solo se edita la referencia de una prueba guardada.")
    datos = datos_referencia(carpeta, referencia, por_segmento)
    manifiesto.pop("referencias_por_segmento", None)
    manifiesto.update(datos)
    escribir_manifiesto(carpeta, manifiesto)
    return _resumen(carpeta, manifiesto, [], _leer_jsonl(carpeta / "detector.jsonl"))


def borrar(salida: Path, ids, excluir: Path | None = None) -> list[str]:
    """Borra las carpetas enteras (audio incluido) de los ids; devuelve los borrados, sin repetir.

    Valida todos antes de tocar nada: un id inválido, o la carpeta en curso, cancela todo el pedido.
    """
    if not isinstance(ids, list) or not ids:
        raise ValueError("Elegí al menos una llamada o prueba para borrar.")
    unicos = list(dict.fromkeys(ids))
    carpetas = [carpeta_de(salida, id_carpeta) for id_carpeta in unicos]
    if excluir is not None and Path(excluir) in carpetas:
        raise ValueError("No se puede borrar una llamada en curso.")
    for carpeta in carpetas:
        shutil.rmtree(carpeta)
    return unicos


def borrar_pruebas_guardadas(salida: Path) -> list[str]:
    """Borra todas las pruebas con `guardada: true`; las llamadas y las pruebas sin guardar no se tocan."""
    ids = []
    for carpeta in carpetas_de_salida(salida):
        manifiesto = leer_manifiesto(carpeta)
        if manifiesto is not None and es_prueba(manifiesto) and manifiesto.get("guardada") is True:
            shutil.rmtree(carpeta)
            ids.append(carpeta.name)
    return ids
