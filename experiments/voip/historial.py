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
from pathlib import Path

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
