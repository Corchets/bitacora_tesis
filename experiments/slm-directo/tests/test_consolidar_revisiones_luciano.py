"""Control de fuentes originales, cruces y unidades; no lee test ni datos privados."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import consolidar_revisiones_luciano as revision


class ConsolidacionTest(unittest.TestCase):
    def test_no_convierte_dudas_ni_pendientes_en_confirmaciones(self):
        archivo = "REVISION-145-LUCIANO-2026-11-07.json"
        original = (revision.CORPUS / archivo).read_bytes()
        mapa = json.loads((revision.CORPUS / "CORRESPONDENCIA-145-LUCIANO-2026-11-07.json").read_text())
        filas = revision.filas_145(original, mapa, archivo, "2026-11-07")
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

    def test_captura_vigente_conserva_casilla_y_aviso_previo(self):
        original = (revision.CORPUS / revision.ORIGINAL_145).read_bytes()
        mapa = json.loads((revision.CORPUS / revision.MAPA_145).read_text())
        filas = {f["alias_revision"]: f for f in revision.filas_145(original, mapa)}
        self.assertEqual(len(filas), 26)
        self.assertTrue(all(f["confirmada_en_formulario"] for f in filas.values()))
        avisadas = {a for a, f in filas.items() if f["aviso_previo"]}
        self.assertEqual(avisadas, {"Llamada 14", "Llamada 23", "Llamada 31", "Llamada 39", "Llamada 41", "Llamada 42"})
        self.assertFalse(any(filas[a]["conocido_en_formulario"] for a in avisadas))
        self.assertEqual(filas["Llamada 16"]["pedido"], "dudoso")
        self.assertIsNone(filas["Llamada 16"]["pedido_marca"])

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

    def test_fichas_coreanas_conservan_segmentos_textuales(self):
        texto = (revision.CORPUS / revision.COREANO_144).read_text()
        filas = revision.filas_144_coreano(texto)
        self.assertEqual([f["fuente_id"] for f in filas], ["vishing_540", "vishing_281"])
        self.assertEqual(filas[0]["pedido_marca"], "57 y 59")
        self.assertTrue(filas[1]["pedido_marca"].startswith("que pida que instale"))
        self.assertTrue(all(f["unidad_marcas"] == "segmento_fuente" for f in filas))
        with self.assertRaises(ValueError):
            revision.filas_144_coreano(texto.replace("### Ficha KO-02", "### Otra"))


if __name__ == "__main__":
    unittest.main()
