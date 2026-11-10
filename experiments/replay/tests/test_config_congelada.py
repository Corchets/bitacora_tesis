"""replay.py con la configuración congelada de #143 (`c-json-corte-riesgo`): arma DetectorSLMCorteRiesgo igual que
correr.py y le reinicia el motivo en cada llamada. Sin modelo: contra el Ollama falso de
slm-directo/tests/test_config_congelada_143.py (`OllamaCongelada`).

Uso (desde experiments/replay):
    python -m unittest tests.test_config_congelada -v
"""

from __future__ import annotations

import sys
import threading
import unittest
from http.server import HTTPServer
from pathlib import Path

DIR_REPLAY = Path(__file__).resolve().parents[1]
DIR_SLM_DIRECTO = DIR_REPLAY.parent / "slm-directo"
for _p in (DIR_REPLAY, DIR_SLM_DIRECTO):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import replay  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from contexto import Actualizacion  # noqa: E402
from detectores import (  # noqa: E402
    ESQUEMA_MOTIVO,
    PROMPTS_CORTE_RIESGO,
    DetectorSLM,
    DetectorSLMCorteRiesgo,
    cargar_prompt,
    esquema_de,
)

sys.path.append(str(DIR_SLM_DIRECTO / "tests"))
from test_config_congelada_143 import OllamaCongelada  # noqa: E402

PROMPT = "c-json-corte-riesgo"
MODELO = OllamaCongelada.modelo


class TestConfigCongelada(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ollama = HTTPServer(("127.0.0.1", 0), OllamaCongelada)
        threading.Thread(target=cls.ollama.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.ollama.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.ollama.shutdown()
        cls.ollama.server_close()

    def setUp(self):
        OllamaCongelada.pedidos = []
        OllamaCongelada.motivo_roto = False

    def construir(self, prompt: str = PROMPT, nombre: str = "slm"):
        return replay.construir_detector(nombre, modelo=MODELO, prompt_nombre=prompt, hablantes="rol",
                                         ollama_url=self.url)

    def test_arma_el_mismo_detector_que_correr(self):
        for variante in sorted(PROMPTS_CORTE_RIESGO):
            with self.subTest(variante=variante):
                d = self.construir(variante)
                # Lo que arma correr.py para la misma variante (correr.main, rama PROMPTS_CORTE_RIESGO).
                esperado = DetectorSLMCorteRiesgo(ClienteOllama(self.url), MODELO, cargar_prompt(variante), "rol",
                                                  4096, 42, esquema=esquema_de(variante))
                self.assertIs(type(d), DetectorSLMCorteRiesgo)
                self.assertEqual((d.prompt, d.esquema, d.opciones(), d.umbral, d.pedido_motivo, d.hablantes),
                                 (esperado.prompt, esperado.esquema, esperado.opciones(), esperado.umbral,
                                  esperado.pedido_motivo, esperado.hablantes))
                self.assertIs(d.pensar, False)

    def test_los_otros_prompts_siguen_con_el_json_entero(self):
        self.assertIs(type(self.construir("v4")), DetectorSLM)

    def test_tito_no_admite_el_prompt_cortado(self):
        with self.assertRaisesRegex(ValueError, "tito-slm no admite"):
            self.construir(nombre="tito-slm")

    def test_cada_llamada_del_replay_pide_su_motivo(self):
        acts = []
        for llamada in ("LLAMADA-1", "LLAMADA-2"):
            acts += [Actualizacion(llamada, 1, "final", 1, "Hola, ¿hablo con Ana?", canal="otra"),
                     Actualizacion(llamada, 2, "final", 2, "Te llamo de soporte.", canal="otra"),
                     Actualizacion(llamada, 3, "final", 3, "Decime el código.", canal="otra")]
        filas, contextos = replay.correr_replay(acts, self.construir(), hablantes="rol")
        self.assertEqual([c.aviso_n for c in contextos], [2, 2])
        self.assertEqual([c.aviso_respuesta.motivo for c in contextos],
                         ["Dice ser de soporte sin que lo hayas pedido"] * 2)
        motivos = [p for p in OllamaCongelada.pedidos if p.get("format") == ESQUEMA_MOTIVO]
        self.assertEqual(len(motivos), 2, "uno por llamada, en su primer aviso")


if __name__ == "__main__":
    unittest.main()
