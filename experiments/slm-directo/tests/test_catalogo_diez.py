import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from slm_catalogo_diez import CATALOGO, elegir_opcion


class CatalogoDiezTest(unittest.TestCase):
    def test_no_hay_posible_engano(self):
        categorias = json.loads(CATALOGO.read_text(encoding="utf-8"))["categorias"]
        ids = [x["id"] for x in categorias]
        self.assertEqual(len(ids), 10)
        self.assertEqual(len(set(ids)), 10)
        self.assertNotIn("POSSIBLE_DECEPTION", ids)

    def test_sin_umbral_se_envia_tambien_informacion_insuficiente(self):
        textos = {"REQUEST_AUTH_CODE": "código", "INSUFFICIENT_INFORMATION": "insuficiente"}
        self.assertEqual(elegir_opcion({"REQUEST_AUTH_CODE": 0.0001,
                                        "INSUFFICIENT_INFORMATION": 0.0002}, textos),
                         "INSUFFICIENT_INFORMATION")

    def test_rechaza_opciones_faltantes(self):
        with self.assertRaises(ValueError):
            elegir_opcion({"A": 0.2}, {"A": "uno", "B": "dos"})


if __name__ == "__main__":
    unittest.main()
