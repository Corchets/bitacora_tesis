"""Tabla de gamas del spike #29. Un programa, tres configs."""

import json
import os
from dataclasses import dataclass
from pathlib import Path

AQUI = Path(__file__).resolve().parent
GAMAS_JSON = AQUI / "gamas.json"


@dataclass(frozen=True)
class Gama:
    nombre: str
    asr: str
    detector: str
    techo_mb: int
    hilos_total: int
    hilos_asr: int
    hilos_detector: int
    gpu: bool


def cargar_gama(nombre: str | None = None) -> Gama:
    """Lee la fila de la gama pedida. En #29 se corre `alta`."""
    nombre = (nombre or os.environ.get("GAMA", "alta")).lower()
    tabla = json.loads(GAMAS_JSON.read_text(encoding="utf-8"))
    if nombre not in tabla:
        raise ValueError(f"Gama desconocida: {nombre}. Esperaba: {sorted(tabla)}")
    g = tabla[nombre]
    return Gama(
        nombre=nombre,
        asr=g["asr"],
        detector=g["detector"],
        techo_mb=g["techo_mb"],
        hilos_total=g["hilos_total"],
        hilos_asr=g["hilos_asr"],
        hilos_detector=g["hilos_detector"],
        gpu=g["gpu"],
    )
