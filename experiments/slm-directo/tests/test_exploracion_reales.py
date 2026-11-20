"""Exploración con los conjuntos reales de #52 (corridas/2026-11-20_exploracion-reales/): dos variantes de la
configuración de la evaluación final (c-consejos-corte-riesgo), con un solo párrafo cambiado cada una, las dos políticas
de aviso y la regla de su analizar.py. Sin modelo: contra el Ollama falso de la humo.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_exploracion_reales -v
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import conjuntos  # noqa: E402
from detectores import ESQUEMA_SALIDA, PROMPTS_CORTE_RIESGO, VARIANTES_EXPLORACION_REALES, cargar_prompt, esquema_de  # noqa: E402
from test_config_congelada_143 import _ConServidor, correr_main  # noqa: E402

CARPETA = RAIZ / "corridas" / "2026-11-20_exploracion-reales"
_spec = importlib.util.spec_from_file_location("analizar_exploracion", CARPETA / "analizar.py")
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)

BASE = "c-consejos-corte-riesgo"
VARIANTES = ("c-comercial-corte-riesgo", "c-rumbo-corte-riesgo")


def parrafos(texto: str) -> list[str]:
    return texto.strip().split("\n\n")


class TestUnSoloParrafo(unittest.TestCase):
    def setUp(self):
        self.base = parrafos(cargar_prompt(BASE))

    def cambiados(self, variante: str) -> list[int]:
        otro = parrafos(cargar_prompt(variante))
        self.assertEqual(len(otro), len(self.base), "los mismos párrafos, en el mismo orden")
        return [i for i, (x, y) in enumerate(zip(self.base, otro)) if x != y]

    def test_registradas_sobre_la_configuracion_de_la_evaluacion_final(self):
        self.assertEqual(ex.BASE, BASE)
        self.assertEqual(tuple(f"{v}-corte-riesgo" for v in VARIANTES_EXPLORACION_REALES), VARIANTES)
        self.assertEqual(ex.PROMPTS, {"base": BASE, "c-comercial": VARIANTES[0], "c-rumbo": VARIANTES[1]})
        self.assertLessEqual({BASE, *VARIANTES}, PROMPTS_CORTE_RIESGO)
        for v in VARIANTES:
            self.assertEqual(esquema_de(v), ESQUEMA_SALIDA, v)

    def test_c_comercial_suma_la_llamada_comercial_al_parrafo_final(self):
        self.assertEqual(self.cambiados("c-comercial-corte-riesgo"), [5])
        nuevo = parrafos(cargar_prompt("c-comercial-corte-riesgo"))[5]
        self.assertTrue(nuevo.startswith(self.base[5]), "conserva el freno tal cual y agrega")
        self.assertIn("llamada comercial", nuevo)
        self.assertTrue(nuevo.endswith("Lo que cuenta es qué le pide a PROTEGIDA, no que quiera venderle algo."))

    def test_c_rumbo_ata_el_aviso_anticipado_al_rumbo_hacia_un_pedido(self):
        self.assertEqual(self.cambiados("c-rumbo-corte-riesgo"), [4])
        nuevo = parrafos(cargar_prompt("c-rumbo-corte-riesgo"))[4]
        self.assertTrue(nuevo.startswith("Mirá la llamada entera y hacia dónde va, no solo la última frase."))
        self.assertIn("Si ya se parece a una estafa", self.base[4])
        self.assertNotIn("Si ya se parece a una estafa", nuevo)
        self.assertIn("hacia alguno de esos pedidos", nuevo)

    def test_ninguna_pone_numeros_ni_ejemplos_de_los_casos(self):
        for v in VARIANTES:
            (i,) = self.cambiados(v)
            nuevo = parrafos(cargar_prompt(v))[i]
            self.assertNotRegex(nuevo, r"\d", f"{v}: sin números, no fuerza un valor")
            self.assertNotIn("«", nuevo, f"{v}: sin frases de ejemplo")


class TestCorren(_ConServidor):
    def test_cada_variante_corre_solo_otra_en_todas_las_lineas(self):
        for v in VARIANTES:
            with self.subTest(v):
                manifiesto, filas = correr_main("--modelos", "modelo-falso:1b", "--prompts", v, "--hablantes", "rol",
                                                "--casos", "SC-WA-CODE-01-e01", "--url", self.url, "--sin-reglas",
                                                "--solo-otra", "--seguir-tras-aviso")
                self.assertEqual(manifiesto["prompts"][v]["texto"], cargar_prompt(v))
                self.assertEqual(manifiesto["modo_termino"], "diagnostico-completo")
                self.assertEqual(manifiesto["parametros_slm"]["corte_riesgo"]["num_predict"], 14)
                self.assertTrue(all(r["consulta"] == ("omitida" if r["hablante"] == "PROTEGIDA" else "") for r in filas))
                self.assertGreater(len(ex.riesgos(filas)), 0)


class TestPoliticas(unittest.TestCase):
    def test_riesgos_son_las_consultas_validas_de_otra(self):
        filas = [{"linea": "1", "hablante": "OTRA", "valida": "true", "riesgo": "0.2"},
                 {"linea": "2", "hablante": "PROTEGIDA", "valida": "true", "riesgo": ""},
                 {"linea": "3", "hablante": "OTRA", "valida": "false", "riesgo": ""},
                 {"linea": "4", "hablante": "OTRA", "valida": "true", "riesgo": "0.3"}]
        self.assertEqual(ex.riesgos(filas), [(1, 0.2), (4, 0.3)])

    def test_primer_aviso_es_el_de_la_configuracion(self):
        self.assertEqual(ex.primer_aviso([(1, 0.2), (3, 0.3), (5, 0.3)]), 3)
        self.assertIsNone(ex.primer_aviso([(1, 0.2), (3, 0.2)]))

    def test_confirmacion_espera_el_segundo_aviso_debil(self):
        self.assertEqual(ex.confirmacion([(1, 0.3), (3, 0.2), (5, 0.3)]), 5, "no hace falta que sean seguidas")
        self.assertIsNone(ex.confirmacion([(1, 0.2), (3, 0.3), (5, 0.2)]), "un 0,3 suelto no avisa")

    def test_confirmacion_avisa_ya_con_una_senal_fuerte(self):
        self.assertEqual(ex.confirmacion([(1, 0.2), (3, 0.5)]), 3)
        self.assertEqual(ex.confirmacion([(1, 0.3), (3, 0.8), (5, 0.3)]), 3)

    def test_la_confirmacion_nunca_avisa_antes_que_el_primer_aviso(self):
        for l in ([(1, 0.3), (3, 0.3)], [(1, 0.5)], [(2, 0.2), (4, 0.3), (6, 0.9)], []):
            a, b = ex.primer_aviso(l), ex.confirmacion(l)
            self.assertTrue(b is None or (a is not None and a <= b), l)


def cifras(**cambios):
    """Las cifras de la referencia de la evaluación final, con los cambios pedidos."""
    return {"coreanas": 33, "coreanas a tiempo": 27, "FA reales": 21, "desarrollo estafas": 40, "desarrollo a tiempo": 26,
            "desarrollo FA": 20, "test estafas": 73, "test a tiempo": 53, "test FA": 15} | cambios


class TestRegla(unittest.TestCase):
    def test_sirve_si_mantiene_las_coreanas_y_baja_siete_fa_reales(self):
        self.assertEqual(ex.veredicto(cifras(**{"FA reales": 14}), cifras())[0], "sirve")
        self.assertEqual(ex.veredicto(cifras(coreanas=32, **{"coreanas a tiempo": 26, "FA reales": 10}), cifras())[0], "sirve")

    def test_no_sirve_si_baja_menos_de_siete(self):
        v, por_que = ex.veredicto(cifras(**{"FA reales": 15}), cifras())
        self.assertEqual(v, "no sirve")
        self.assertIn("tienen que bajar 7", por_que)

    def test_no_sirve_si_pierde_dos_coreanas_o_dos_a_tiempo(self):
        self.assertEqual(ex.veredicto(cifras(coreanas=31, **{"FA reales": 5}), cifras())[0], "no sirve")
        self.assertEqual(ex.veredicto(cifras(**{"coreanas a tiempo": 25, "FA reales": 5}), cifras())[0], "no sirve")

    def test_elige_el_que_menos_pierde_a_tiempo_en_desarrollo(self):
        res = {("base", "confirmación"): cifras(**{"FA reales": 8, "desarrollo a tiempo": 18}),
               ("c-rumbo", "primer aviso"): cifras(**{"FA reales": 13, "desarrollo a tiempo": 24}),
               ("c-comercial", "primer aviso"): cifras(**{"FA reales": 20, "desarrollo a tiempo": 27})}  # no sirve
        self.assertEqual(ex.elegir(res, cifras()), ("c-rumbo", "primer aviso"))

    def test_en_el_empate_gana_menos_fa_reales_y_despues_el_que_cambia_menos(self):
        res = {("c-comercial", "primer aviso"): cifras(**{"FA reales": 12}),
               ("c-rumbo", "primer aviso"): cifras(**{"FA reales": 10})}
        self.assertEqual(ex.elegir(res, cifras()), ("c-rumbo", "primer aviso"))
        res = {c: cifras(**{"FA reales": 10}) for c in ex.CANDIDATOS}
        self.assertEqual(ex.elegir(res, cifras()), ("base", "confirmación"))

    def test_si_no_sirve_ninguno_no_elige(self):
        self.assertIsNone(ex.elegir({c: cifras() for c in ex.CANDIDATOS}, cifras()))

    def test_el_test_no_elige_pero_marca_el_costo_alto(self):
        self.assertEqual(ex.costo_alto(cifras(**{"test a tiempo": 46}), cifras()), [])
        self.assertEqual(ex.costo_alto(cifras(**{"test a tiempo": 45, "test estafas": 63}), cifras()),
                         ["test a tiempo -8", "test estafas -10"])
        caro = {("base", "confirmación"): cifras(**{"FA reales": 5, "test a tiempo": 20})}
        self.assertEqual(ex.elegir(caro, cifras()), ("base", "confirmación"), "el costo en el test se informa, no descarta")
        self.assertEqual(ex.costo_alto(cifras(**{"test a tiempo": None, "test estafas": None}), cifras()), [], "sin test no marca")


class TestCasos(unittest.TestCase):
    def test_de_desarrollo_corre_solo_la_vista_principal(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            conj = conjuntos.preparar_desarrollo(tmp)
            ids = ex.casos_de(conj)
            self.assertEqual(len(ids), 140)
            self.assertLess(len(ids), len(conj.ids))
        finally:
            shutil.rmtree(tmp)

    def test_los_reales_corren_enteros_y_primero(self):
        self.assertEqual(ex.CONJUNTOS[:2], ["externo", "legitimas_reales"])
        self.assertEqual(ex.ENTEROS, {"externo", "legitimas_reales"})


class TestColab(unittest.TestCase):
    def test_el_notebook_y_el_script(self):
        nb = json.loads((RAIZ / "colab/COLAB-EXPLORACION-REALES.ipynb").read_text(encoding="utf-8"))
        codigo = "".join(nb["cells"][1]["source"])
        self.assertIn("TAG = 'colab/52-exploracion-reales'", codigo)
        self.assertIn("probar_exploracion_reales.py", codigo)
        self.assertNotIn("COLAB_CONFIG", codigo)
        script = (RAIZ / "colab/probar_exploracion_reales.py").read_text(encoding="utf-8")
        self.assertIn("CORRIDA = ['--solo-otra', '--seguir-tras-aviso']", script)
        self.assertIn("ex.casos_de(", script)
        self.assertIn("necesita las legítimas reales", script, "sin las legítimas reales no corre nada")


if __name__ == "__main__":
    unittest.main()
