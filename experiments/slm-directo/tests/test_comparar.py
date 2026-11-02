"""Reporte comparativo directo vs Tito→SLM (#71, parte de #68).

Corre `correr`+`resumen` con dobles (TitoGuion + Ollama falso) y comprueba que
`comparar.py` genera `comparacion.md` con las secciones exigidas, sin descargar
ni entrenar modelos.
"""

from __future__ import annotations

import io
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import comparar  # noqa: E402
import correr  # noqa: E402
from test_ensayo import OllamaFalso  # noqa: E402


class TestComparacion(unittest.TestCase):
    def test_comparacion_regenerable_con_secciones(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--filtro-tito", "--tito-puntajes", "4=0.9",
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp.name,
                ])
                (carpeta,) = Path(tmp.name).iterdir()
                self.assertEqual(comparar.main([str(carpeta)]), 0)
                texto = (carpeta / "comparacion.md").read_text(encoding="utf-8")
            for seccion in ("## Por conversación", "## Cambios de aviso entre variantes",
                            "## Doble lectura de marcas", "## Runtime común y hardware",
                            "## Carga, calentamiento y ajuste", "## Límites de interpretación"):
                self.assertIn(seccion, texto)
            # Regenerable: segunda pasada idéntica.
            with redirect_stdout(io.StringIO()):
                comparar.main([str(carpeta)])
                texto2 = (carpeta / "comparacion.md").read_text(encoding="utf-8")
            self.assertEqual(texto, texto2)
        finally:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
