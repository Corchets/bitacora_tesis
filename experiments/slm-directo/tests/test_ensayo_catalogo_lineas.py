import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ensayo_catalogo_lineas import ventanas_en


class VentanasTest(unittest.TestCase):
    def test_una_linea_y_pares_no_solapados(self):
        self.assertEqual(list(ventanas_en(1)), [("linea", 0)])
        self.assertEqual(list(ventanas_en(2)), [("linea", 1), ("par", 0)])
        self.assertEqual(list(ventanas_en(3)), [("linea", 2)])
        self.assertEqual(list(ventanas_en(4)), [("linea", 3), ("par", 2)])
        self.assertEqual(list(ventanas_en(5)), [("linea", 4)])


if __name__ == "__main__":
    unittest.main()
