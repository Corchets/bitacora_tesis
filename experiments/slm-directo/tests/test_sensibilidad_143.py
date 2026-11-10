"""Prueba de sensibilidad de #143 (corridas/2026-11-10_sensibilidad-c/): tres variantes de C, con un solo cambio cada
una, cortadas tras el riesgo como la configuración congelada. Sin modelo: contra el Ollama falso de la humo.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_sensibilidad_143 -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from detectores import DIR_PROMPTS, ESQUEMA_SALIDA, PROMPTS_CORTE_RIESGO, cargar_prompt, esquema_de  # noqa: E402
from test_config_congelada_143 import _ConServidor, correr_main  # noqa: E402

VARIANTES = ("c-ancla-corte-riesgo", "c-premisa-corte-riesgo", "c-sin-freno-corte-riesgo")


def parrafos(texto: str) -> list[str]:
    return texto.strip().split("\n\n")


class TestUnSoloCambio(unittest.TestCase):
    def setUp(self):
        self.tarea = parrafos((DIR_PROMPTS / "tarea_c.txt").read_text(encoding="utf-8"))
        self.salida = (DIR_PROMPTS / "salida_json_c.txt").read_text(encoding="utf-8").strip()
        self.base = cargar_prompt("c-json-corte-riesgo")

    def test_registradas_como_la_configuracion_congelada(self):
        self.assertEqual(PROMPTS_CORTE_RIESGO, {"c-json-corte-riesgo", *VARIANTES})
        for v in VARIANTES:
            self.assertEqual(esquema_de(v), ESQUEMA_SALIDA, v)

    def test_c_ancla_solo_ancla_la_definicion_del_riesgo(self):
        ancla = (DIR_PROMPTS / "salida_json_c_ancla.txt").read_text(encoding="utf-8").strip().split("\n")
        original = self.salida.split("\n")
        self.assertEqual([i for i, (x, y) in enumerate(zip(original, ancla)) if x != y], [1], "solo la línea del riesgo")
        self.assertEqual(len(ancla), len(original))
        self.assertTrue(ancla[1].startswith(original[1] + " Si OTRA ya está llevando a PROTEGIDA"))
        self.assertIn("el riesgo es 0.7 o más", ancla[1])
        self.assertEqual(cargar_prompt("c-ancla-corte-riesgo"), self.base.replace(original[1], ancla[1]))

    def test_c_premisa_agrega_un_parrafo_despues_del_armado_de_la_estafa(self):
        premisa = parrafos(cargar_prompt("c-premisa-corte-riesgo"))
        base = parrafos(self.base)
        self.assertEqual(premisa[:3] + premisa[4:], base)
        self.assertTrue(premisa[2].startswith("Una estafa telefónica suele armarse así"))
        self.assertTrue(premisa[3].startswith("Que el número no esté agendado pesa"))
        self.assertNotRegex(premisa[3], r"\d", "sin números: no fuerza un valor")

    def test_c_sin_freno_saca_solo_el_parrafo_de_lo_que_puede_pedir_una_legitima(self):
        sin_freno = parrafos(cargar_prompt("c-sin-freno-corte-riesgo"))
        base = parrafos(self.base)
        (quitado,) = [p for p in base if p not in sin_freno]
        self.assertTrue(quitado.startswith("Una llamada legítima también puede pedir el nombre, el DNI"))
        self.assertEqual([p for p in base if p != quitado], sin_freno)


class TestCorren(_ConServidor):
    def test_cada_variante_corre_solo_otra_con_el_corte_y_el_motivo(self):
        for v in VARIANTES:
            with self.subTest(v):
                manifiesto, filas = correr_main("--modelos", "modelo-falso:1b", "--prompts", v, "--hablantes", "rol",
                                                "--casos", "SC-WA-CODE-01-e01", "--url", self.url, "--sin-reglas",
                                                "--solo-otra", "--seguir-tras-aviso")
                self.assertEqual(manifiesto["prompts"][v]["texto"], cargar_prompt(v))
                self.assertEqual(manifiesto["parametros_slm"]["corte_riesgo"]["num_predict"], 14)
                self.assertTrue(all(r["consulta"] == ("omitida" if r["hablante"] == "PROTEGIDA" else "") for r in filas))
                self.assertEqual(sum(bool(r["ms_etapa2"]) for r in filas), sum(r["aviso"] == "true" for r in filas))
