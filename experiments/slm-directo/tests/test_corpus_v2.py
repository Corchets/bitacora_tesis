"""La reserva no entra por accidente a desarrollo ni cambia sin detectarse."""

import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import casos
import correr
import resumen


class TestReserva(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.raiz = Path(self.temporal.name)
        self.texto = self.raiz / "texto"
        self.referencia = self.raiz / "referencia"
        self.texto.mkdir()
        self.referencia.mkdir()
        self.catalogo = self.raiz / "catalogo.csv"
        self.catalogo.write_text("scenario_id,estado\nS-D,borrador\nS-T,borrador\n", encoding="utf-8")
        self.manifiesto = self.raiz / "manifiesto.json"
        for nombre, valor in (("DIR_TEXTO", self.texto), ("DIR_REFERENCIA", self.referencia),
                              ("CATALOGO", self.catalogo), ("MANIFIESTO", self.manifiesto)):
            parche = patch.object(casos, nombre, valor)
            parche.start()
            self.addCleanup(parche.stop)
        self.escribir("D", "desarrollo", "S-D")
        self.escribir("T", "test_reservado", "S-T")

    def escribir(self, cid, particion, semilla, **cambios):
        (self.texto / f"{cid}.txt").write_text("A: ¿Quedamos mañana?\nB: Sí, a las cuatro.\n", encoding="utf-8")
        ref = dict(case_id=cid, grupo="trampa", semilla=semilla, par=None, clase="legitima",
                   t_r_linea=None, t_c_linea=None, pedido=None, evidencia=[
                       dict(linea=1, evento="contexto", etiquetas=[])],
                   que_prueba="Coordinación cotidiana.", origen="Diseño ficticio para prueba.",
                   revision_humana=False, notas="", particion=particion)
        ref.update(cambios)
        (self.referencia / f"{cid}.json").write_text(json.dumps(ref), encoding="utf-8")

    def args(self, **cambios):
        return SimpleNamespace(**(dict(casos="", grupo=None, particion="desarrollo") | cambios))

    def test_ejecucion_por_defecto_y_seleccion_explicita(self):
        self.assertEqual(correr.elegir_casos(self.args()), ["D"])
        with self.assertRaisesRegex(SystemExit, "fuera de desarrollo"):
            correr.elegir_casos(self.args(casos="T"))
        self.assertEqual(correr.elegir_casos(self.args(particion="test_reservado")), ["T"])

    def test_panel_no_incluye_textos_ni_referencias_reservadas(self):
        ruta = Path(correr.__file__).parent / "analisis" / "tablero" / "armar_panel.py"
        spec = importlib.util.spec_from_file_location("panel_corpus", ruta)
        panel = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(panel)
        self.assertEqual([c["id"] for c in panel._casos({})], ["D"])

    def test_semilla_y_par_no_pueden_cruzar_particiones(self):
        self.assertEqual(casos.validar_todos(), [])
        self.escribir("T", "test_reservado", "S-D", par="D")
        errores = casos.validar_todos()
        self.assertTrue(any("semilla S-D cruza" in e for e in errores), errores)
        self.assertTrue(any("el par D cruza" in e for e in errores), errores)

    def test_huella_detecta_modificacion_alta_y_baja(self):
        self.assertEqual(casos.main(["--congelar"]), 0)
        self.assertEqual(casos.validar_todos(), [])
        (self.texto / "T.txt").write_text("A: ¿Venís el jueves?\nB: Sí, a las cuatro.\n", encoding="utf-8")
        self.assertTrue(any("T: no coincide" in e for e in casos.validar_todos()))
        self.escribir("N", "desarrollo", "S-D")
        self.assertTrue(any("N: no coincide" in e for e in casos.validar_todos()))
        (self.texto / "T.txt").unlink()
        (self.referencia / "T.json").unlink()
        self.assertTrue(any("T: no coincide" in e for e in casos.validar_todos()))

    def test_reserva_existente_no_se_sobrescribe(self):
        self.assertEqual(casos.main(["--congelar"]), 0)
        original = self.manifiesto.read_bytes()
        self.assertEqual(casos.main(["--congelar"]), 1)
        self.assertEqual(self.manifiesto.read_bytes(), original)

    def test_una_legitima_nueva_sigue_contando_como_legitima(self):
        self.assertEqual(resumen.categoria(dict(clase="legitima"), 1), "falsa_alarma")
        self.assertEqual(resumen.categoria(dict(clase="legitima"), None), "sin_aviso_correcto")

    def test_v2_rechaza_miniguiones_y_metadatos_incompletos(self):
        self.escribir("D", "desarrollo", "S-D", grupo="corpus_v2")
        errores = casos.validar_todos()
        self.assertTrue(any("entre 12 y 40" in e for e in errores), errores)
        self.assertTrue(any("faltan campos de corpus_v2" in e for e in errores), errores)


if __name__ == "__main__":
    unittest.main()
