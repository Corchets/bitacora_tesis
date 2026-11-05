"""Colab de v4 con Tito viejo 2.0 y SLM solo: script y notebook, sin modelo."""
from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import casos  # noqa: E402
from detectores import PROMPTS  # noqa: E402


class Colab(unittest.TestCase):
    SCRIPT = RAIZ / "colab" / "probar_tito_2_v4.py"

    def constante(self, nombre):
        for n in ast.parse(self.SCRIPT.read_text(encoding="utf-8")).body:
            if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == nombre:
                return ast.literal_eval(n.value)
        self.fail(f"Falta {nombre}")

    def test_compara_v4_con_roles_en_primer_aviso(self):
        comunes = [c for c in ast.parse(self.SCRIPT.read_text(encoding="utf-8")).body
                   if isinstance(c, ast.Assign) and getattr(c.targets[0], "id", "") == "COMUNES"]
        fuente = ast.get_source_segment(self.SCRIPT.read_text(encoding="utf-8"), comunes[0])
        self.assertIn("'--prompts', 'v4', '--hablantes', 'rol'", fuente)
        self.assertIn("v4", PROMPTS)
        condiciones = self.constante("CONDICIONES")
        self.assertEqual([c[2] for c in condiciones], ["tito-viejo-2", "slm"])
        for _, _, _, opciones in condiciones:
            self.assertNotIn("--seguir-tras-aviso", opciones)
        self.assertIn("--tito-viejo-2", condiciones[0][3])
        self.assertEqual(condiciones[1][3], [])

    def test_el_notebook_baja_el_script_de_su_rama(self):
        rama = self.constante("RAMA")
        cuaderno = json.loads((RAIZ / "colab" / "COLAB-TITO-2-V4.ipynb").read_text(encoding="utf-8"))
        fuente = "".join("".join(c["source"]) for c in cuaderno["cells"])
        self.assertEqual(rama, "tito-2-v4-colab")
        self.assertIn(f"RAMA = '{rama}'", fuente)
        self.assertIn("probar_tito_2_v4.py", fuente)
        self.assertIn("COLAB_GUARDAR_EN_DRIVE'] = '0'", fuente)

    @unittest.skipUnless((RAIZ / "casos" / "RESERVA-FUERA-DEL-REPO.md").exists(), "la reserva está en esta rama")
    def test_el_colab_corre_sin_la_reserva(self):
        self.assertFalse([c for c in casos.ids_de_casos() if "CV2-T" in c])


if __name__ == "__main__":
    unittest.main()
