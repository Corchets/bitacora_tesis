"""Pruebas de los diálogos de voz real: que reglas.py dé las etiquetas anotadas y que la hoja esté al día."""

from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

import dialogos as D


class TestDialogosDelRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dialogos = D.cargar_dialogos()

    def test_reglas_da_las_etiquetas_anotadas(self):
        self.assertEqual(D.verificar_dialogos(self.dialogos), [])

    def test_hay_estafas_y_una_legitima_con_las_dos_voces(self):
        clases = [d.clase for d in self.dialogos.values()]
        self.assertGreaterEqual(clases.count("estafa"), 3)
        self.assertIn("legitima", clases)
        for d in self.dialogos.values():
            self.assertTrue(d.del_rol("otra") and d.del_rol("protegida"), d.id)

    def test_la_legitima_no_dispara_nada(self):
        for d in self.dialogos.values():
            if d.clase == "legitima":
                self.assertEqual([l.id for l in d.lineas if l.etiquetas], [], d.id)

    def test_la_hoja_esta_al_dia(self):
        self.assertEqual(D.HOJA_POR_DEFECTO.read_text(encoding="utf-8"), D.generar_hoja(self.dialogos))


class TestVerificar(unittest.TestCase):
    def test_una_negativa_con_etiquetas_es_un_problema(self):
        d = D.cargar_dialogos()["D3"]
        mala = replace(d.lineas[2], texto="Pasame el código que te llegó", etiquetas=("REQUEST_AUTH_CODE",))
        problemas = D.verificar_dialogos({"D3": replace(d, lineas=(mala, *d.lineas[3:]))})
        self.assertTrue(any("negativa dispara" in p for p in problemas), problemas)

    def test_etiquetas_anotadas_distintas_de_reglas(self):
        d = D.cargar_dialogos()["D1"]
        mala = replace(d.lineas[5], etiquetas=())
        problemas = D.verificar_dialogos({"D1": replace(d, lineas=(*d.lineas[:5], mala, *d.lineas[6:]))})
        self.assertTrue(any("anotadas [], reglas.py da" in p for p in problemas), problemas)


class TestReferenciaDelCanal(unittest.TestCase):
    def test_las_lineas_de_cada_canal_en_orden(self):
        d = D.cargar_dialogos()["D1"]
        otra, tipos = D.referencia_del_canal(d, "otra")
        protegida, _ = D.referencia_del_canal(d, "protegida")
        self.assertEqual(len(otra) + len(protegida), len(d.lineas))
        self.assertEqual(otra[0], d.lineas[0].texto)
        self.assertEqual(protegida[0], d.lineas[1].texto)
        self.assertEqual(len(tipos), len(otra))


if __name__ == "__main__":
    unittest.main()
