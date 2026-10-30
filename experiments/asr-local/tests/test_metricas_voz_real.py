"""Pruebas de las métricas de la medición con voz real: alineado por frase, etiquetas, agregados y regla de paso."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

import metricas_voz_real as M


class TestAlinear(unittest.TestCase):
    def test_iguales(self):
        self.assertEqual(M.alinear(["a", "b"], ["a", "b"]), [(0, 0), (1, 1)])

    def test_sustitucion_borrado_e_insercion(self):
        self.assertEqual(M.alinear(["a", "b", "c"], ["a", "x", "c"]), [(0, 0), (1, 1), (2, 2)])
        self.assertEqual(M.alinear(["a", "b", "c"], ["a", "c"]), [(0, 0), (1, None), (2, 1)])
        self.assertEqual(M.alinear(["a", "c"], ["a", "b", "c"]), [(0, 0), (None, 1), (1, 2)])

    def test_vacios(self):
        self.assertEqual(M.alinear([], ["a"]), [(None, 0)])
        self.assertEqual(M.alinear(["a"], []), [(0, None)])
        self.assertEqual(M.alinear([], []), [])


class TestPartirPorFrases(unittest.TestCase):
    REF = ["pasame el código", "transferí la plata ahora", "estoy cómodo"]

    def test_hipotesis_perfecta_vuelve_en_las_mismas_frases(self):
        hip = "Pasame el código. Transferí la plata ahora. Estoy cómodo."
        self.assertEqual(M.partir_por_frases(self.REF, hip),
                         ["Pasame el código.", "Transferí la plata ahora.", "Estoy cómodo."])

    def test_las_sustituciones_quedan_en_su_frase(self):
        hip = "pasame el codego transferí la plata ahora estoy cómodo"
        self.assertEqual(M.partir_por_frases(self.REF, hip)[0], "pasame el codego")

    def test_una_palabra_perdida_no_corre_los_limites(self):
        hip = "pasame código transferí la plata ahora estoy cómodo"
        partes = M.partir_por_frases(self.REF, hip)
        self.assertEqual(partes, ["pasame código", "transferí la plata ahora", "estoy cómodo"])

    def test_una_frase_entera_perdida_queda_vacia(self):
        hip = "pasame el código estoy cómodo"
        self.assertEqual(M.partir_por_frases(self.REF, hip), ["pasame el código", "", "estoy cómodo"])

    def test_insercion_al_principio_va_a_la_primera_frase(self):
        hip = "hola hola pasame el código transferí la plata ahora estoy cómodo"
        self.assertEqual(M.partir_por_frases(self.REF, hip)[0], "hola hola pasame el código")

    def test_insercion_entre_frases_va_a_la_frase_anterior(self):
        hip = "pasame el código eh transferí la plata ahora estoy cómodo"
        partes = M.partir_por_frases(self.REF, hip)
        self.assertEqual(partes[0], "pasame el código eh")
        self.assertEqual(partes[1], "transferí la plata ahora")

    def test_ignora_tildes_mayusculas_y_signos_al_alinear(self):
        hip = "PASAME EL CODIGO!!! transferi la plata ahora, estoy comodo"
        partes = M.partir_por_frases(self.REF, hip)
        self.assertEqual(partes[0], "PASAME EL CODIGO!!!")

    def test_sin_hipotesis_o_sin_referencia(self):
        self.assertEqual(M.partir_por_frases(self.REF, ""), ["", "", ""])
        self.assertEqual(M.partir_por_frases([], "algo"), [])

    def test_todas_las_palabras_de_la_hipotesis_quedan_en_alguna_frase(self):
        hip = "eh pasame el cosa transferi la plata estoy muy cómodo che"
        partes = M.partir_por_frases(self.REF, hip)
        self.assertEqual(" ".join(partes).split(), hip.split())


class TestSustituciones(unittest.TestCase):
    def test_devuelve_lo_que_salio_y_lo_que_se_dijo(self):
        pares = M.sustituciones(["Pasame el código, dale."], "pasame el codego dale")
        self.assertEqual(pares, [("codego", "código")])

    def test_ignora_aciertos_borrados_e_inserciones(self):
        self.assertEqual(M.sustituciones(["uno dos tres"], "uno dos tres"), [])
        self.assertEqual(M.sustituciones(["uno dos tres"], "uno tres"), [])
        self.assertEqual(M.sustituciones(["uno tres"], "uno dos tres"), [])

    def test_varias_lineas(self):
        pares = M.sustituciones(["pasame la clave", "decime el código"], "pasame la clabe decime el cosigo")
        self.assertEqual(pares, [("clabe", "clave"), ("cosigo", "código")])


class TestEtiquetasYTerminos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terminos = M.cargar_terminos()

    def test_etiquetas_usan_reglas_py(self):
        self.assertEqual(M.etiquetas("Pasame el código ahora"), {"REQUEST_AUTH_CODE"})
        self.assertEqual(M.etiquetas("Estoy cómodo"), set())

    def test_los_terminos_criticos_incluyen_patrones_imperativos_y_plata(self):
        t = self.terminos
        self.assertIn("codigo", t.patrones)
        self.assertIn("pasame", t.imperativos)
        self.assertEqual(sorted(t.plata), ["luca", "mango"])
        self.assertIn("mercado pago", t.entidades)
        self.assertIn("ñaño", t.jerga)

    def test_terminos_en_busca_con_la_tolerancia_de_reglas(self):
        grupos = M.terminos_en("Pasame el códgo y treinta lucas", self.terminos)
        self.assertIn("codigo", grupos["criticos"])  # reglas tolera un typo en palabras de 6+ letras
        self.assertIn("pasame", grupos["criticos"])
        self.assertIn("luca", grupos["criticos"])

    def test_entidades_y_jerga_por_palabra_entera(self):
        grupos = M.terminos_en("Entrá a Mercado Pago, chango, no seas sonso y vos sabés", self.terminos)
        self.assertEqual(grupos["entidades"], {"mercado pago"})
        self.assertEqual(grupos["jerga"], {"chango", "sonso"})  # «vos» no es «vo»

    def test_la_n_con_tilde_no_es_una_n(self):
        self.assertIn("ñaño", M.terminos_en("Ñaño, mirá", self.terminos)["jerga"])
        self.assertEqual(M.terminos_en("el nano, mirá", self.terminos)["jerga"], set())
        self.assertIn("al ñudo", M.terminos_en("lo hizo al ñudo", self.terminos)["jerga"])

    def test_jerga_vo_solo_si_esta_sola(self):
        self.assertIn("vo", M.terminos_en("Vo' sabés", self.terminos)["jerga"])
        self.assertNotIn("vo", M.terminos_en("voy a ir", self.terminos)["jerga"])

    def test_frase_negativa_no_tiene_terminos_criticos_de_plata(self):
        self.assertEqual(M.terminos_en("Me duele el codo", self.terminos)["criticos"], set())


class TestEvaluarFrases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terminos = M.cargar_terminos()

    def evaluar(self, ref, hip, tipos=None):
        return M.evaluar_frases(ref, hip, self.terminos, tipos)

    def test_etiquetas_correctas_perdidas_y_nuevas(self):
        ref = ["Pasame el código", "Pasame la clave", "Me duele el codo", "Estoy cómodo"]
        hip = ["Pasame el código", "Pasame la clave", "Me duele el codigo", "Estoy cómodo"]
        r = self.evaluar(ref, hip)
        self.assertEqual(r["frases_correctas"], 3)
        self.assertEqual(r["frases_con_etiquetas_ref"], 2)
        self.assertEqual(r["positivas_correctas"], 2)
        self.assertEqual(r["negativas"], 2)
        self.assertEqual(r["negativas_correctas"], 1)
        self.assertEqual(r["etiquetas_nuevas_en_negativas"], 1)
        self.assertEqual(r["frases"][2]["nuevas"], ["REQUEST_AUTH_CODE"])

    def test_etiqueta_perdida(self):
        r = self.evaluar(["Pasame el código"], ["Pasame el cosa"])
        self.assertEqual(r["etiquetas_perdidas"], 1)
        self.assertFalse(r["frases"][0]["correcta"])
        self.assertEqual(r["frases"][0]["perdidas"], ["REQUEST_AUTH_CODE"])

    def test_etiqueta_distinta_en_una_positiva_cuenta_como_nueva_en_positivas(self):
        r = self.evaluar(["Pasame el código"], ["Pasame la clave"])
        self.assertEqual(r["etiquetas_nuevas_en_positivas"], 1)
        self.assertEqual(r["etiquetas_nuevas_en_negativas"], 0)

    def test_recall_por_termino(self):
        ref = ["Pasame el código", "Pasame el código y la clave"]
        hip = ["Pasame el codigo", "Pasame el cosa y la clave"]
        r = self.evaluar(ref, hip)["recall"]["criticos"]
        self.assertEqual(r["codigo"], {"ref": 2, "ok": 1})
        self.assertEqual(r["clave"], {"ref": 1, "ok": 1})
        self.assertEqual(r["pasame"], {"ref": 2, "ok": 2})

    def test_recall_de_entidades_y_jerga(self):
        r = self.evaluar(["Entrá a Mercado Pago, chango"], ["Entra a Mercado Pago chango"])["recall"]
        self.assertEqual(r["entidades"]["mercado pago"], {"ref": 1, "ok": 1})
        self.assertEqual(r["jerga"]["chango"], {"ref": 1, "ok": 1})

    def test_el_tipo_viaja_con_la_frase(self):
        r = self.evaluar(["Estoy cómodo"], ["Estoy cómodo"], ["negativa"])
        self.assertEqual(r["frases"][0]["tipo"], "negativa")


class TestErrorYEstadisticos(unittest.TestCase):
    def test_error_de_texto_trae_las_cuentas_para_agregar(self):
        e = M.error_de_texto("pasame el código", "pasame el cosa")
        self.assertEqual(e["palabras_ref"], 3)
        self.assertEqual(e["wer_distancia"], 1)
        self.assertEqual(e["wer"], round(1 / 3, 4))

    def test_percentil_por_rango_mas_cercano(self):
        self.assertIsNone(M.percentil([], 95))
        self.assertEqual(M.percentil([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 95), 10)
        self.assertEqual(M.percentil([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 50), 5)
        self.assertEqual(M.percentil([7], 95), 7)

    def test_resumen_de_demoras(self):
        r = M.resumen_demoras([0.8, 1.0, 1.2])
        self.assertEqual((r["n"], r["mediana_s"], r["max_s"]), (3, 1.0, 1.2))
        self.assertEqual(M.resumen_demoras([])["mediana_s"], None)


def resultado(frases_correctas=3, nuevas_neg=0, wer_dist=1, palabras=10, demoras=(1.0,), segmentos=4,
              n_frases=4, proceso=1.0, audio=20.0, p95=30.0):
    return {
        "etiquetas": {"n_frases": n_frases, "frases_correctas": frases_correctas, "frases_con_etiquetas_ref": 3,
                      "positivas_correctas": frases_correctas, "negativas": 1, "negativas_correctas": 1,
                      "etiquetas_nuevas_en_negativas": nuevas_neg, "etiquetas_perdidas": 0,
                      "etiquetas_nuevas_en_positivas": 0,
                      "recall": {"criticos": {"codigo": {"ref": 2, "ok": 1}}, "entidades": {}, "jerga": {}}},
        "error": {"palabras_ref": palabras, "wer_distancia": wer_dist, "caracteres_ref": 50, "cer_distancia": 5},
        "demoras_s": list(demoras), "segmentos": segmentos, "proceso_s": proceso, "audio_s": audio,
        "p95_bloque_ms": p95,
    }


class TestAgregar(unittest.TestCase):
    def test_suma_cuentas_y_calcula_el_wer_sobre_las_sumas(self):
        a = M.agregar([resultado(wer_dist=1, palabras=10), resultado(wer_dist=3, palabras=30)])
        self.assertEqual(a["wer"], round(4 / 40, 4))  # no el promedio de 0,1 y 0,1
        self.assertEqual(a["cer"], round(10 / 100, 4))
        self.assertEqual(a["pruebas"], 2)
        self.assertEqual(a["frases"], 8)
        self.assertEqual(a["frases_correctas"], 6)
        self.assertEqual(a["segmentos_finales"], 8)
        self.assertEqual(a["segmentos_por_frase"], 1.0)

    def test_recall_se_suma_por_termino(self):
        a = M.agregar([resultado(), resultado()])
        self.assertEqual(a["recall_criticos"]["por_termino"]["codigo"]["ref"], 4)
        self.assertEqual(a["recall_criticos"]["recall"], 0.5)
        self.assertIsNone(a["recall_jerga"]["recall"])

    def test_demora_mediana_y_p95_de_todas_las_frases(self):
        a = M.agregar([resultado(demoras=(0.8, 1.0)), resultado(demoras=(1.2, 3.0))])
        self.assertEqual(a["demora_final"]["n"], 4)
        self.assertEqual(a["demora_final"]["mediana_s"], 1.1)
        self.assertEqual(a["demora_final"]["max_s"], 3.0)

    def test_rtf_y_p95_por_bloque(self):
        a = M.agregar([resultado(proceso=1.0, audio=20.0, p95=30.0), resultado(proceso=3.0, audio=20.0, p95=50.0)])
        self.assertEqual(a["rtf"], 0.1)
        self.assertEqual(a["p95_bloque_ms"], {"mediana": 40.0, "max": 50.0})

    def test_sin_p95_por_bloque_para_motores_por_lotes(self):
        a = M.agregar([resultado(p95=None)])
        self.assertIsNone(a["p95_bloque_ms"])


class TestReglaDePaso(unittest.TestCase):
    def agregado(self, correctas=10, nuevas=0, wer=0.20, demora=1.0):
        return {"frases_correctas": correctas, "etiquetas_nuevas_en_negativas": nuevas, "wer": wer,
                "demora_final": {"mediana_s": demora}}

    def test_pasa_si_cumple_las_cuatro(self):
        r = M.regla_de_paso(self.agregado(12, 0, 0.21, 1.2), self.agregado(10, 0, 0.20, 1.0))
        self.assertTrue(r["pasa"])
        self.assertEqual(r["criterios"]["etiquetas"]["frases_mas"], 2)

    def test_una_sola_frase_mas_no_alcanza(self):
        r = M.regla_de_paso(self.agregado(11), self.agregado(10))
        self.assertFalse(r["pasa"])
        self.assertFalse(r["criterios"]["etiquetas"]["cumple"])

    def test_una_etiqueta_nueva_en_negativas_lo_descarta(self):
        r = M.regla_de_paso(self.agregado(15, nuevas=1), self.agregado(10, nuevas=0))
        self.assertFalse(r["pasa"])
        self.assertFalse(r["criterios"]["negativas"]["cumple"])

    def test_si_el_paso_anterior_ya_tenia_la_etiqueta_nueva_no_cuenta_otra_vez(self):
        r = M.regla_de_paso(self.agregado(15, nuevas=1), self.agregado(10, nuevas=1))
        self.assertTrue(r["criterios"]["negativas"]["cumple"])

    def test_la_demora_extra_tiene_tope_de_tres_decimas(self):
        self.assertTrue(M.regla_de_paso(self.agregado(15, demora=1.3), self.agregado(10, demora=1.0))["pasa"])
        r = M.regla_de_paso(self.agregado(15, demora=1.31), self.agregado(10, demora=1.0))
        self.assertFalse(r["pasa"])
        self.assertFalse(r["criterios"]["demora"]["cumple"])

    def test_el_wer_puede_empeorar_hasta_dos_puntos(self):
        self.assertTrue(M.regla_de_paso(self.agregado(15, wer=0.22), self.agregado(10, wer=0.20))["pasa"])
        r = M.regla_de_paso(self.agregado(15, wer=0.221), self.agregado(10, wer=0.20))
        self.assertFalse(r["criterios"]["wer"]["cumple"])

    def test_mejorar_la_demora_o_el_wer_no_molesta(self):
        r = M.regla_de_paso(self.agregado(15, wer=0.10, demora=0.5), self.agregado(10, wer=0.20, demora=1.0))
        self.assertTrue(r["pasa"])

    def test_sin_demora_la_regla_no_se_puede_evaluar_y_no_pasa(self):
        sin = self.agregado(15)
        sin["demora_final"] = {"mediana_s": None}
        r = M.regla_de_paso(sin, self.agregado(10))
        self.assertFalse(r["pasa"])
        self.assertIsNone(r["criterios"]["demora"]["extra_s"])


if __name__ == "__main__":
    unittest.main()
