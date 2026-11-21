"""Corre los controles de maniobras con correr.py, sin sumarlos a los 150 de desarrollo.

Los casos viven en casos/controles-maniobras.json y se escriben en una carpeta temporal solo
durante la corrida: las métricas de desarrollo, los manifiestos y la reserva no cambian.
Estado: propuesta sin discutir. Redacción asistida y sin revisión humana.

Uso, desde experiments/slm-directo:
    python correr_controles.py --modelos gemma4:e2b-it-q4_K_M --prompts v4,v5-maniobras,v5 --hablantes rol --sin-reglas
    python correr_controles.py --controles casos/controles-ventas.json --modelos ... --prompts v4,s-json --hablantes rol

Con `--controles` se corre otro archivo con el mismo formato (por defecto, los de maniobras). Cada control
puede traer su `grupo`; si no, queda `control_maniobras`.
"""

from __future__ import annotations

import json
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

import casos
import correr

CONTROLES = Path(__file__).resolve().parent / "casos" / "controles-maniobras.json"


def materializar(destino: Path, archivo: Path = CONTROLES) -> list[str]:
    """Escribe texto, referencia y roles de cada control en `destino`, con el formato de los casos."""
    datos = json.loads(archivo.read_text(encoding="utf-8"))
    (destino / "texto").mkdir()
    (destino / "referencia").mkdir()
    for caso, c in datos.items():
        (destino / "texto" / f"{caso}.txt").write_text("\n".join(c["lineas"]) + "\n", encoding="utf-8")
        referencia = {"case_id": caso, "grupo": c.get("grupo", "control_maniobras"), "clase": c["clase"], "que_prueba": c["que_prueba"],
                      "t_r_linea": None, "t_c_linea": None, "pedido": None, "evidencia": [], "particion": "desarrollo",
                      "revision_humana": c["revision_humana"]}
        (destino / "referencia" / f"{caso}.json").write_text(json.dumps(referencia, ensure_ascii=False), encoding="utf-8")
    roles = {caso: {"protegida": c["protegida"], "origen": "control"} for caso, c in datos.items()}
    (destino / "roles.json").write_text(json.dumps(roles, ensure_ascii=False), encoding="utf-8")
    return list(datos)


@contextmanager
def casos_de(carpeta: Path):
    """Hace que `casos` lea la carpeta de controles y lo restaura al salir, también si la corrida falla."""
    originales = casos.DIR_TEXTO, casos.DIR_REFERENCIA, casos.ROLES, casos.validar_todos
    casos.DIR_TEXTO, casos.DIR_REFERENCIA, casos.ROLES = carpeta / "texto", carpeta / "referencia", carpeta / "roles.json"
    casos.validar_todos = lambda: []  # el formato de los controles lo cubren sus pruebas, no el del catálogo
    try:
        yield
    finally:
        casos.DIR_TEXTO, casos.DIR_REFERENCIA, casos.ROLES, casos.validar_todos = originales


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    archivo = CONTROLES
    if "--controles" in argv:
        i = argv.index("--controles")
        archivo = Path(argv[i + 1])
        del argv[i:i + 2]
    with tempfile.TemporaryDirectory() as tmp:
        carpeta = Path(tmp)
        materializar(carpeta, archivo)
        with casos_de(carpeta):
            return correr.main(argv)


if __name__ == "__main__":
    sys.exit(main())
