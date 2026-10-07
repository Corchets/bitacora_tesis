"""Protecciones contra duplicados, etiquetas contradictorias y uso de familias excluidas."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from preparar import normalizar, preparar, validar_familias


class ValidacionTest(unittest.TestCase):
    def banco(self):
        return [
            {"id": f"banco_{n:03d}", "tema": "tema_de_fixture",
             "etiqueta": "estafa" if n < 50 else "legitima", "fuentes": ["fuente"],
             "textos": [f"Este texto de prueba tiene familia {n} y variante {v}." for v in range(20)]}
            for n in range(100)
        ]

    def validar(self, familias):
        errores = []
        filas = validar_familias(familias, {"fuente": {}}, "banco", set(), {}, errores)
        return filas, errores

    def test_normalizacion_ignora_tildes_puntuacion_y_caja(self):
        self.assertEqual(normalizar("¡PASÁ el código!"), normalizar("pasa el codigo"))

    def test_bloquea_duplicado_entre_clases(self):
        familias = self.banco()
        familias[50]["textos"][0] = familias[0]["textos"][0].upper()
        _, errores = self.validar(familias)
        self.assertTrue(any("contradicción entre clases" in e for e in errores), errores)

    def test_bloquea_variantes_de_puntuacion_como_volumen(self):
        familias = self.banco()
        familias[0]["textos"][1] = familias[0]["textos"][0].replace(".", "!")
        _, errores = self.validar(familias)
        self.assertTrue(any("duplicado" in e for e in errores), errores)

    def test_fuente_desconocida_no_pasa(self):
        familias = self.banco()
        familias[0]["fuentes"] = ["fuente_inventada"]
        _, errores = self.validar(familias)
        self.assertTrue(any("fuentes ausentes o desconocidas" in e for e in errores), errores)

    def test_no_admite_relato_que_da_la_respuesta(self):
        familias = self.banco()
        familias[0]["textos"][0] = "En una llamada un estafador pide dinero bajo control del atacante."
        _, errores = self.validar(familias)
        self.assertTrue(any("narración externa" in e for e in errores), errores)

    def test_validacion_no_muta_fuente(self):
        familias = self.banco()
        antes = copy.deepcopy(familias)
        filas, errores = self.validar(familias)
        self.assertEqual(errores, [])
        self.assertEqual(len(filas), 2000)
        self.assertEqual(familias, antes)

    def test_familia_excluida_no_alimenta_al_clasificador(self):
        with tempfile.TemporaryDirectory() as temp:
            carpeta = Path(temp)
            for lote in ("banco", "identidad", "cotidiano"):
                familias = self.banco()
                for familia in familias:
                    familia["id"] = familia["id"].replace("banco", lote)
                    familia["fuentes"] = [lote + "_F01"]
                    familia["textos"] = [t + f" Corresponde al lote {lote}." for t in familia["textos"]]
                (carpeta / f"familias_{lote}.json").write_text(json.dumps(familias))
                fuente = {"id": lote + "_F01", "url": "https://example.com/fixture",
                          "titulo": "Fuente de prueba", "consulta": "2026-10-02",
                          "uso": "fixture", "hallazgo": "fixture", "licencia_textos": "fixture"}
                (carpeta / f"fuentes_{lote}.json").write_text(json.dumps([fuente]))
            (carpeta / "exclusiones.json").write_text(json.dumps({"cotidiano_000": "Contexto insuficiente"}))
            salidas, cobertura = preparar(carpeta)
            semillas = json.loads(salidas["semillas.json"])
            pendientes = [json.loads(linea) for linea in salidas["pendientes_revision.jsonl"].splitlines()]
            self.assertEqual(cobertura["textos_generados"], 6000)
            self.assertEqual(cobertura["textos"], 5980)
            self.assertEqual(len(pendientes), 20)
            self.assertTrue(all(p["texto"] not in semillas[p["etiqueta"]] for p in pendientes))
            self.assertTrue(all(p["uso"] == "revision_pendiente" for p in pendientes))


if __name__ == "__main__":
    unittest.main()
