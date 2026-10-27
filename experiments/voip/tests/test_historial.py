"""Módulo de historial: carpetas de salida armadas a mano en un directorio temporal."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

DIR_VOIP = Path(__file__).resolve().parent.parent
if str(DIR_VOIP) not in sys.path:
    sys.path.insert(0, str(DIR_VOIP))

import historial


def carpeta(salida: Path, nombre: str, manifiesto: dict | None):
    d = salida / nombre
    d.mkdir()
    (d / "estereo.wav").write_bytes(b"RIFF")
    if manifiesto is not None:
        (d / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
    return d


class TestDescartarPruebasNoGuardadas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.salida = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_borra_solo_pruebas_con_guardada_falsa(self):
        no_guardada = carpeta(self.salida, "2026-10-26_100000-000001",
                              {"inicio_panel": {"modo": "asr"}, "guardada": False})
        guardada = carpeta(self.salida, "2026-10-26_100000-000002",
                           {"inicio_panel": {"modo": "asr"}, "guardada": True, "referencia": "hola"})
        antigua = carpeta(self.salida, "2026-10-26_100000-000003", {"inicio_panel": {"modo": "asr"}})
        llamada = carpeta(self.salida, "2026-10-26_100000-000004", {"inicio_panel": {"modo": "llamada"}})
        sin_manifiesto = carpeta(self.salida, "2026-10-26_100000-000005", None)
        roto = carpeta(self.salida, "2026-10-26_100000-000006", None)
        (roto / "manifiesto.json").write_text("{", encoding="utf-8")
        ajena = self.salida / "otra-cosa"
        ajena.mkdir()
        (ajena / "manifiesto.json").write_text(json.dumps({"inicio_panel": {"modo": "asr"}, "guardada": False}))
        archivo = self.salida / "2026-10-26_100000-000007"
        archivo.write_text("no es carpeta")

        borradas = historial.descartar_pruebas_no_guardadas(self.salida)

        self.assertEqual(borradas, [no_guardada.name])
        self.assertFalse(no_guardada.exists())
        for d in (guardada, antigua, llamada, sin_manifiesto, roto, ajena):
            self.assertTrue(d.exists(), d.name)
        self.assertTrue(archivo.exists())

    def test_excepcion_para_la_carpeta_en_curso(self):
        d = carpeta(self.salida, "2026-10-26_100000-000001",
                    {"inicio_panel": {"modo": "asr"}, "guardada": False})
        self.assertEqual(historial.descartar_pruebas_no_guardadas(self.salida, conservar=d), [])
        self.assertTrue(d.exists())

    def test_salida_inexistente_no_rompe(self):
        self.assertEqual(historial.descartar_pruebas_no_guardadas(self.salida / "no-existe"), [])
