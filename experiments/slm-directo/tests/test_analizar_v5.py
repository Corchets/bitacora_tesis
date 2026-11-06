"""Simulación de persistencia y lectura de las corridas de v5, sin modelo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import analizar_v5 as a  # noqa: E402


def filas(*alertas):
    return [{"alerta_sugerida": "true" if x else "false"} for x in alertas]


class Persistencia(unittest.TestCase):
    def test_primer_aviso_alcanza_con_una_alerta(self):
        self.assertTrue(a.avisa(filas(0, 1, 0), 1, False))
        self.assertFalse(a.avisa(filas(0, 0, 0), 1, False))

    def test_dos_en_la_llamada_no_exige_que_sean_seguidas(self):
        self.assertTrue(a.avisa(filas(1, 0, 1), 2, False))
        self.assertFalse(a.avisa(filas(1, 0, 0), 2, False))

    def test_dos_seguidas_se_corta_con_una_linea_sin_alerta(self):
        self.assertFalse(a.avisa(filas(1, 0, 1), 2, True))
        self.assertTrue(a.avisa(filas(0, 1, 1), 2, True))


class Corridas(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corridas = a.leer_corridas()
        cls.ids = sorted(cls.corridas["v4"])
        cls.ref = a.referencias(cls.ids)

    def test_son_los_150_de_desarrollo_sin_reserva(self):
        self.assertEqual(len(self.ids), 150)
        self.assertFalse([c for c in self.ids if "CV2-T" in c])
        for nombre, c in self.corridas.items():
            self.assertEqual(sorted(c), self.ids, nombre)

    def test_las_cifras_del_analisis(self):
        esperadas = {"v4": (55, 13), "v5-maniobras": (57, 16), "v5": (57, 13), "v5-indirectos": (55, 12), "v5-sin-excepcion": (56, 13)}
        for nombre, cifras in esperadas.items():
            self.assertEqual(a.contar(self.corridas[nombre], self.ref, 1, False), cifras, nombre)

    def test_la_persistencia_de_v4_coincide_con_lo_ya_informado(self):
        self.assertEqual(a.contar(self.corridas["v4"], self.ref, 2, False), (51, 11))
        self.assertEqual(a.contar(self.corridas["v4"], self.ref, 2, True), (49, 8))

    def test_ningun_prompt_nuevo_avisa_las_sin_pedido_del_corpus_v2_salvo_banco_011(self):
        for nombre, c in self.corridas.items():
            sin_pedido = [i for i in self.ids if self.ref[i].get("dificultad") == "sin_pedido" and a.avisa(c[i], 1, False)]
            self.assertEqual(sin_pedido, ["CV2-D-V-BANCO-011"], nombre)


if __name__ == "__main__":
    unittest.main()
