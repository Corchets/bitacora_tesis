"""Control de fuentes originales, cruces y unidades; no lee test ni datos privados."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import consolidar_revisiones_luciano as revision


class ConsolidacionTest(unittest.TestCase):
    def test_no_convierte_dudas_ni_pendientes_en_confirmaciones(self):
        original = (revision.CORPUS / revision.ORIGINAL_145).read_bytes()
        mapa = json.loads((revision.CORPUS / revision.MAPA_145).read_text())
        filas = revision.filas_145(original, mapa)
        self.assertEqual(len(filas), 20)
        self.assertEqual(sum(f["confirmada_en_formulario"] for f in filas), 17)
        self.assertEqual({f["alias_revision"] for f in filas if not f["confirmada_en_formulario"]}, {"Llamada 09", "Llamada 10", "Llamada 14"})
        originales = json.loads(original)["respuestas"]
        for f in filas:
            self.assertEqual(f["juicio_estafa"], originales[f["alias_revision"]]["estafa"])
            self.assertEqual(f["unidad_marcas"], "linea_dialogo")
        mapa["archivo_original_sha256"] = "modificado"
        with self.assertRaises(ValueError):
            revision.filas_145(original, mapa)

    def test_fichas_externas_conservan_descartes_y_marcas_textuales(self):
        original = (revision.CORPUS / revision.ORIGINAL_144).read_text()
        filas = revision.filas_144(original)
        self.assertEqual(len(filas), 20)
        self.assertEqual(sum(f["descartada_del_set"] for f in filas), 4)
        self.assertEqual(filas[2]["pedido_marca"], "13 17")
        self.assertEqual(filas[3]["juicio_estafa"], None)
        self.assertEqual(filas[8]["juicio_estafa"], "re dudosa, yo si avisaria cuando te dicen que estas ganando un premio pero bueno")
        self.assertTrue(all(f["unidad_marcas"] == "turno_lectura" for f in filas))
        self.assertTrue(all(f["estado_revision"] == "anotacion_individual_sin_adjudicar" for f in filas))
        with self.assertRaises(ValueError):
            revision.filas_144(original.replace("## Fila 0 ·", "## Ausente 0 ·"))


if __name__ == "__main__":
    unittest.main()
