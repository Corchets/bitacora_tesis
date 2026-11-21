"""regla_pedido_critico.py: qué pedidos de OTRA disparan y qué menciones no.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_regla_pedido_critico -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import regla_pedido_critico as rpc  # noqa: E402


def otra(texto: str, previas: tuple[tuple[str, str], ...] = ()) -> list[str]:
    lineas = [*previas, ("OTRA", texto)]
    return rpc.dispara(lineas, len(lineas) - 1)


class ReglaPedidoCriticoTest(unittest.TestCase):
    def test_dictar_un_codigo_o_una_clave(self):
        for texto in ("Leeme los seis dígitos y te incorporo al grupo", "Decime el código que te llegó",
                      "¿Me pasás la clave del home banking?", "Necesito que me digas el PIN"):
            self.assertEqual(otra(texto), ["secreto"], texto)

    def test_el_pronombre_retoma_el_codigo_de_las_lineas_anteriores(self):
        previas = (("PROTEGIDA", "Me llegó un código por SMS"),)
        self.assertEqual(otra("Sí, decímelo y te agrego", previas), ["secreto"])
        self.assertEqual(otra("Sí, decímelo y te agrego"), [])

    def test_escribir_la_clave_donde_dice_otra(self):
        self.assertEqual(otra("Sí, ingresá la clave que usás en la cuenta"), ["secreto"])

    def test_transferir_y_acceso_remoto(self):
        self.assertEqual(otra("Si me transferís a mí, se lo alcanzo"), ["transferencia"])
        self.assertEqual(otra("Descargá la aplicación que te mando por mensaje"), ["acceso_remoto"])

    def test_menciones_y_advertencias_no_disparan(self):
        for texto in ("No compartas el código con nadie", "Ese código lo cargás vos en la app",
                      "La instalación ya está paga con la compra", "No se paga nada por adelantado",
                      "Si un día ponés mal el PIN tres veces, el PUK te desbloquea el chip",
                      "La mejora la hace nuestro departamento técnico por acceso remoto",
                      "¿Me confirmás los últimos tres números de tu DNI?",
                      "no nosotros vemos en el sistema cuando la terminaste no tenés que mandarnos nada"):
            self.assertEqual(otra(texto), [], texto)

    def test_solo_otra(self):
        self.assertEqual(rpc.dispara([("PROTEGIDA", "Decime el código")], 0), [])

    def test_primer_pedido(self):
        lineas = [("OTRA", "Hola, te llamo del soporte"), ("PROTEGIDA", "Hola"), ("OTRA", "Leeme el código")]
        self.assertEqual(rpc.primer_pedido(lineas), (3, ["secreto"]))
        self.assertIsNone(rpc.primer_pedido(lineas[:2]))


if __name__ == "__main__":
    unittest.main()
