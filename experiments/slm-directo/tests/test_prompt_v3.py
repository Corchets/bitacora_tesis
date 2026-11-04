"""Prompt v3 en el ejecutor: texto, esquema y mensaje de cada condición, sin modelo."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from detectores import PROMPTS, DetectorSLM, armar_mensaje_usuario, cargar_prompt, esquema_de, huella  # noqa: E402
from filtro_tito import FlujoTitoSLM, TitoGuion  # noqa: E402
from test_sin_indicio import DIALOGO, ClienteGrabador  # noqa: E402


class PromptV3(unittest.TestCase):
    def test_texto_y_esquema(self):
        self.assertEqual(PROMPTS["v3"], ("tarea_v3.txt",))
        texto = cargar_prompt("v3")
        self.assertNotIn("al menos 0.5", texto)
        self.assertIn("Si no se sabe qué es lo que piden", texto)
        self.assertIn("(una deuda, un accidente, un beneficio, la seguridad de la cuenta)", texto)
        self.assertEqual(esquema_de("v3")["required"], ["evidencia", "alerta_sugerida", "riesgo", "motivo"])

    def test_v1_y_v2_no_cambian(self):
        self.assertEqual(huella(cargar_prompt("tarea")), "bf4284996898c45d")
        self.assertEqual(huella(cargar_prompt("v2")), "ce3db487d550210c")

    def _pedidos(self, indicio: bool) -> list[dict]:
        cliente = ClienteGrabador()
        slm = DetectorSLM(cliente, "falso", cargar_prompt("v3"), "ab", esquema=esquema_de("v3"))
        flujo = FlujoTitoSLM(TitoGuion({3: 0.9}, set()), slm, 0.5, indicio=indicio)
        flujo.reiniciar()
        for n in range(1, 4):
            flujo.evaluar(DIALOGO[:n])
        return cliente.pedidos

    def test_las_dos_variantes_de_tito_usan_v3_y_solo_difieren_en_el_indicio(self):
        base = armar_mensaje_usuario(DIALOGO[:3], "ab")
        sin, con = self._pedidos(False), self._pedidos(True)
        self.assertEqual(len(sin), 1)
        self.assertEqual(len(con), 1)
        for pedido in (sin[0], con[0]):
            self.assertEqual(pedido["mensajes"][0]["content"], cargar_prompt("v3"))
            self.assertEqual(pedido["esquema"], esquema_de("v3"))
        self.assertEqual(sin[0]["mensajes"][1]["content"], base)
        self.assertTrue(con[0]["mensajes"][1]["content"].startswith(base + "\n\n"))
        self.assertIn("filtro previo", con[0]["mensajes"][1]["content"])


if __name__ == "__main__":
    unittest.main()
