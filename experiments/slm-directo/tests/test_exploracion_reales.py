"""Exploración con los conjuntos reales de #52 (corridas/2026-11-20_exploracion-reales/): los prompts que se prueban
contra la configuración de la evaluación final (c-consejos-corte-riesgo), las dos políticas de aviso y la regla de su
analizar.py. Sin modelo: contra el Ollama falso de la humo.

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
from detectores import (DIR_PROMPTS, ESQUEMA_SALIDA, PROMPTS, PROMPTS_CORTE_RIESGO, PROMPTS_POR_PEDIDO, UMBRAL_C,  # noqa: E402
                        VARIANTES_EXPLORACION_REALES, cargar_prompt, esquema_de, usa_roles)
from test_config_congelada_143 import _ConServidor, correr_main  # noqa: E402

CARPETA = RAIZ / "corridas" / "2026-11-20_exploracion-reales"
_spec = importlib.util.spec_from_file_location("analizar_exploracion", CARPETA / "analizar.py")
ex = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ex)

BASE = "c-consejos-corte-riesgo"
POR_PEDIDO = ("p-lista", "p-escalera", "p-niveles", "p-sino", "p-minimo")
VARIANTES = tuple(f"{v}-corte-riesgo" for v in ex.VARIANTES)


def parrafos(texto: str) -> list[str]:
    return texto.strip().split("\n\n")


class TestRegistro(unittest.TestCase):
    def test_los_candidatos_son_la_base_c_rumbo_y_los_cinco_por_pedido(self):
        self.assertEqual(ex.BASE, BASE)
        self.assertEqual(set(ex.VARIANTES), {"c-rumbo", *POR_PEDIDO})
        self.assertEqual(VARIANTES_EXPLORACION_REALES, ("c-rumbo",))
        self.assertEqual(set(PROMPTS_POR_PEDIDO), set(POR_PEDIDO))
        self.assertEqual(ex.PROMPTS, {"base": BASE, **{v: f"{v}-corte-riesgo" for v in ex.VARIANTES}})
        self.assertLessEqual({BASE, *VARIANTES}, PROMPTS_CORTE_RIESGO)
        for v in VARIANTES:
            self.assertEqual(esquema_de(v), ESQUEMA_SALIDA, v)
            self.assertTrue(usa_roles(v), v)

    def test_c_comercial_quedo_afuera(self):
        self.assertNotIn("c-comercial", PROMPTS)
        self.assertFalse((DIR_PROMPTS / "tarea_c_comercial.txt").exists())


class TestCRumbo(unittest.TestCase):
    """La única variante que parte del prompt congelado: un solo párrafo cambiado."""

    def test_ata_el_aviso_anticipado_al_rumbo_hacia_un_pedido(self):
        base, otro = parrafos(cargar_prompt(BASE)), parrafos(cargar_prompt("c-rumbo-corte-riesgo"))
        self.assertEqual(len(otro), len(base))
        self.assertEqual([i for i, (x, y) in enumerate(zip(base, otro)) if x != y], [4])
        self.assertTrue(otro[4].startswith("Mirá la llamada entera y hacia dónde va, no solo la última frase."))
        self.assertIn("Si ya se parece a una estafa", base[4])
        self.assertNotIn("Si ya se parece a una estafa", otro[4])
        self.assertIn("hacia alguno de esos pedidos", otro[4])
        self.assertNotRegex(otro[4], r"\d")
        self.assertNotIn("«", otro[4])


class TestPorPedido(unittest.TestCase):
    """Los escritos desde cero: preguntan por el pedido, y el riesgo es una escala de pocos niveles."""

    def partes(self, v: str) -> tuple[str, str]:
        tarea, salida = [(DIR_PROMPTS / n).read_text(encoding="utf-8").strip() for n in PROMPTS[v]]
        return tarea, salida

    def test_no_preguntan_si_es_una_estafa(self):
        for v in POR_PEDIDO:
            tarea, salida = self.partes(v)
            self.assertNotIn("estafa", (tarea + salida).lower(), v)
            self.assertIn("PROTEGIDA", tarea, v)
            self.assertIn("OTRA", tarea, v)
            self.assertNotIn("«", tarea + salida, f"{v}: sin frases de ejemplo")

    def test_la_salida_conserva_los_cuatro_campos_en_orden(self):
        for v in POR_PEDIDO:
            _, salida = self.partes(v)
            campos = [linea for linea in salida.splitlines() if linea.startswith("- ")]
            self.assertEqual([c.split('"')[1] for c in campos], ["riesgo", "alerta_sugerida", "motivo", "evidencia"], v)

    def test_los_niveles_que_avisan_quedan_del_lado_del_umbral_del_codigo(self):
        self.assertEqual(UMBRAL_C, 0.3)
        niveles = {"p-lista": ([0.0], [0.5, 0.9]), "p-minimo": ([0.0], [0.5, 0.9]), "p-niveles": ([0.0, 0.1], [0.5, 0.9]),
                   "p-sino": ([0.1], [0.9]), "p-escalera": ([0.0, 0.1, 0.2], [0.3, 0.5, 0.8])}
        for v, (calla, avisa) in niveles.items():
            texto = "\n".join(self.partes(v))
            for n in calla + avisa:
                self.assertIn(f"{n}", texto, f"{v}: nombra el nivel {n}")
            self.assertTrue(all(n < UMBRAL_C for n in calla) and all(n >= UMBRAL_C for n in avisa), v)

    def test_p_lista_y_p_minimo_comparten_la_salida(self):
        self.assertEqual(PROMPTS["p-lista"][1], PROMPTS["p-minimo"][1])
        self.assertLess(len(self.partes("p-minimo")[0]), 500)
        self.assertLess(len(self.partes("p-lista")[0]), 1000)

    def test_cuatro_son_mas_cortos_que_el_congelado(self):
        largo = len(cargar_prompt(BASE))
        for v in ("p-lista", "p-minimo", "p-niveles", "p-sino"):
            self.assertLess(len(cargar_prompt(v)), largo, v)


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
    def test_los_candidatos_van_de_lo_que_cambia_menos_a_lo_que_cambia_mas(self):
        self.assertEqual(ex.CANDIDATOS[0], ("base", "confirmación"))
        self.assertEqual(ex.CANDIDATOS[1:7], [(v, "primer aviso") for v in ex.VARIANTES])
        self.assertEqual(ex.CANDIDATOS[7:], [(v, "confirmación") for v in ex.VARIANTES])

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

    def test_no_sirve_si_pierde_la_mitad_de_los_avisos_a_tiempo_en_desarrollo(self):
        v, por_que = ex.veredicto(cifras(**{"FA reales": 3, "desarrollo a tiempo": 13}), cifras())
        self.assertEqual(v, "no sirve")
        self.assertIn("la mitad", por_que)
        self.assertEqual(ex.veredicto(cifras(**{"FA reales": 3, "desarrollo a tiempo": 14}), cifras())[0], "sirve")

    def test_elige_el_que_menos_pierde_a_tiempo_en_desarrollo(self):
        res = {("base", "confirmación"): cifras(**{"FA reales": 8, "desarrollo a tiempo": 18}),
               ("c-rumbo", "primer aviso"): cifras(**{"FA reales": 13, "desarrollo a tiempo": 24}),
               ("p-lista", "primer aviso"): cifras(**{"FA reales": 20, "desarrollo a tiempo": 27})}  # no sirve
        self.assertEqual(ex.elegir(res, cifras()), ("c-rumbo", "primer aviso"))
        self.assertEqual(ex.ordenar(res, cifras()), [("c-rumbo", "primer aviso"), ("base", "confirmación")])

    def test_en_el_empate_gana_menos_fa_reales_y_despues_el_que_cambia_menos(self):
        res = {("p-lista", "primer aviso"): cifras(**{"FA reales": 12}),
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


class TestTandas(unittest.TestCase):
    def test_de_desarrollo_corre_solo_la_vista_principal(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            conj = conjuntos.preparar_desarrollo(tmp)
            ids = ex.casos_de("desarrollo", conj)
            self.assertEqual(len(ids), 140)
            self.assertLess(len(ids), len(conj.ids))
            self.assertEqual(ex.casos_de("externo", conj), list(conj.ids), "una tanda entera corre todos sus casos")
        finally:
            shutil.rmtree(tmp)

    def test_la_fase_1_es_lo_que_usa_la_regla_y_la_fase_2_el_resto(self):
        self.assertEqual(ex.FASE_1, ["externo", "legitimas_reales", "desarrollo"])
        self.assertEqual(ex.FASE_2, ["zona_gris", "test_reservado"])
        self.assertEqual(ex.TANDAS["legitimas_reales"], ("legitimas_reales", "principal"))
        self.assertEqual(ex.TANDAS["zona_gris"], ("legitimas_reales", "aparte"))
        self.assertEqual(set(ex.TANDAS), set(ex.FASE_1) | set(ex.FASE_2))


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
        self.assertIn("fase(ex.FASE_1, list(CARPETAS))", script, "la fase 1 corre con todos los prompts")
        self.assertIn("ex.para_fase_2(SALIDA)", script, "la regla decide qué prompts tocan el test")
        self.assertIn("fase(ex.FASE_2, siguen)", script)
        self.assertIn("necesita las legítimas reales", script, "sin las legítimas reales no corre nada")


if __name__ == "__main__":
    unittest.main()
