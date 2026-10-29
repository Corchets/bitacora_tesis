"""Pruebas del guion de voz real: que cumpla el plan y que reglas.py dé las etiquetas anotadas."""

from __future__ import annotations

import re
import sys
import unittest
from dataclasses import replace
from pathlib import Path

CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

import guion as G
import hotwords as H


class TestGuionDelRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guion = G.cargar_guion()

    def test_cumple_el_plan_y_reglas_da_las_etiquetas_anotadas(self):
        self.assertEqual(G.verificar_guion(self.guion), [])

    def test_son_seis_bloques_de_cinco_con_diez_cinco_cinco_cinco_cinco(self):
        bloques = self.guion.bloques()
        self.assertEqual(sorted(bloques), [1, 2, 3, 4, 5, 6])
        self.assertTrue(all(len(fs) == 5 for fs in bloques.values()))
        for tipo, cantidad in G.CANTIDAD_POR_TIPO.items():
            self.assertEqual(sum(f.tipo == tipo for f in self.guion.frases), cantidad, tipo)

    def test_los_bloques_mezclan_tipos(self):
        for numero, frases in self.guion.bloques().items():
            self.assertGreaterEqual(len({f.tipo for f in frases}), 3, f"bloque {numero}")

    def test_las_negativas_no_disparan_ninguna_etiqueta(self):
        sys.path.insert(0, str(G.DIR_REGLAS))
        import reglas

        negativas = [f for f in self.guion.frases if f.tipo == "negativa"]
        self.assertEqual(len(negativas), 5)
        for f in negativas:
            self.assertEqual(reglas.incendio_en(f.texto), [], f.texto)

    def test_las_otras_veinticinco_dan_etiquetas(self):
        sys.path.insert(0, str(G.DIR_REGLAS))
        import reglas

        for f in self.guion.frases:
            if f.tipo != "negativa":
                self.assertTrue(reglas.incendio_en(f.texto), f.texto)

    def test_los_ejemplos_del_plan_que_reglas_dispara_no_estan_como_negativas(self):
        sys.path.insert(0, str(G.DIR_REGLAS))
        import reglas

        # «pagó la luz» y «el link del cumple» están en PLAN-VOZ-REAL.md §3 como negativas,
        # pero reglas.py los dispara: no pueden ser negativas del guion.
        self.assertTrue(reglas.incendio_en("Ayer pagó la luz mi vecino"))
        self.assertTrue(reglas.incendio_en("El link del cumple"))
        textos = " ".join(f.texto for f in self.guion.frases if f.tipo == "negativa").lower()
        self.assertNotIn("pagó la luz", textos)
        self.assertNotIn("link del cumple", textos)

    def test_cada_palabra_de_jerga_del_guion_esta_en_la_lista_de_jerga(self):
        jerga = [l.strip() for l in (G.DIR_VOZ_REAL / "jerga.txt").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")]
        textos = " ".join(f.texto.lower() for f in self.guion.frases if f.tipo == "jerga")
        for termino in ("chango", "ñaño", "guaso", "mishi", "al ñudo", "sonso", "zafo", "al vicio", "changa"):
            self.assertIn(termino, jerga)
            self.assertIn(termino, textos)

    def test_los_bancos_y_apps_de_las_frases_estan_en_los_hotwords(self):
        secciones = H.leer_secciones(H.HOTWORDS_POR_DEFECTO)["bancos_y_apps"]
        for entidad in ("Mercado Pago", "Naranja X", "Ualá", "Banco Macro", "Galicia", "Brubank", "WhatsApp"):
            self.assertIn(entidad, secciones)
            self.assertTrue(any(entidad in f.texto for f in self.guion.frases), entidad)

    def test_la_hoja_de_grabacion_esta_al_dia_con_el_guion(self):
        esperada = G.generar_hoja(self.guion)
        self.assertEqual(G.HOJA_POR_DEFECTO.read_text(encoding="utf-8"), esperada,
                         "correr: python guion.py --hoja")

    def test_cada_bloque_de_la_hoja_se_copia_con_una_frase_por_linea(self):
        hoja = G.HOJA_POR_DEFECTO.read_text(encoding="utf-8")
        bloques = re.findall(r"```text\n(.*?)\n```", hoja, flags=re.S)
        self.assertEqual(len(bloques), 6)
        for numero, texto in enumerate(bloques, start=1):
            self.assertEqual(texto.splitlines(), [f.texto for f in self.guion.bloques()[numero]])

    def test_los_enlaces_de_la_hoja_resuelven(self):
        hoja = G.HOJA_POR_DEFECTO.read_text(encoding="utf-8")
        for enlace in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", hoja):
            self.assertTrue((G.HOJA_POR_DEFECTO.parent / enlace).exists(), enlace)


class TestVerificarGuion(unittest.TestCase):
    def test_detecta_una_negativa_que_dispara_y_una_etiqueta_mal_anotada(self):
        guion = G.cargar_guion()
        frases = list(guion.frases)
        i = next(i for i, f in enumerate(frases) if f.tipo == "negativa")
        frases[i] = replace(frases[i], texto="Pasame el código ahora")
        j = next(j for j, f in enumerate(frases) if f.tipo == "critica")
        frases[j] = replace(frases[j], etiquetas=("REQUEST_PIN",))
        problemas = G.verificar_guion(G.Guion(tuple(frases)))
        self.assertTrue(any("la negativa dispara" in p for p in problemas))
        self.assertTrue(any("anotadas" in p for p in problemas))

    def test_detecta_la_cantidad_por_tipo(self):
        guion = G.cargar_guion()
        frases = [replace(f, tipo="critica") if f.id == "F03" else f for f in guion.frases]
        self.assertTrue(any("tipo negativa" in p for p in G.verificar_guion(G.Guion(tuple(frases)))))


class TestIdentificarBloque(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guion = G.cargar_guion()

    def referencia(self, bloque: int) -> str:
        return "\n".join(f.texto for f in self.guion.bloques()[bloque])

    def test_un_bloque_copiado_tal_cual_se_reconoce_exacto(self):
        for bloque in range(1, 7):
            r = G.identificar_bloque(self.referencia(bloque), self.guion)
            self.assertEqual(r["bloque"], bloque)
            self.assertTrue(r["exacto"])
            self.assertFalse(r["mezcla"])

    def test_si_dijo_algo_distinto_sigue_reconociendo_el_bloque_pero_no_exacto(self):
        texto = self.referencia(3).replace("Entrá a Mercado Pago", "Entrá a la app de Mercado Pago")
        r = G.identificar_bloque(texto, self.guion)
        self.assertEqual(r["bloque"], 3)
        self.assertFalse(r["exacto"])
        self.assertEqual(r["reconocidas"], 5)

    def test_cada_linea_trae_el_tipo_de_su_frase(self):
        r = G.identificar_bloque(self.referencia(1), self.guion)
        self.assertEqual([l["tipo"] for l in r["lineas"]], ["critica", "numeros", "negativa", "bancos", "critica"])

    def test_texto_que_no_es_del_guion_no_tiene_bloque(self):
        r = G.identificar_bloque("hola probando uno dos tres\nanda el micrófono", self.guion)
        self.assertIsNone(r["bloque"])
        self.assertTrue(all(l["frase"] is None for l in r["lineas"]))

    def test_lineas_de_dos_bloques_se_marcan_como_mezcla(self):
        mezcla = "\n".join([self.guion.bloques()[1][0].texto, self.guion.bloques()[1][1].texto,
                            self.guion.bloques()[2][0].texto])
        r = G.identificar_bloque(mezcla, self.guion)
        self.assertTrue(r["mezcla"])
        self.assertEqual(r["bloque"], 1)

    def test_lineas_vacias_no_cuentan(self):
        r = G.identificar_bloque("\n\n" + self.referencia(2) + "\n\n", self.guion)
        self.assertEqual(len(r["lineas"]), 5)


if __name__ == "__main__":
    unittest.main()
