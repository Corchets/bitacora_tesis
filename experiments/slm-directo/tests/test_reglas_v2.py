"""Reglas v2: filtros nuevos y v1 intacta (las corridas viejas se reproducen)."""

import csv
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import correr  # noqa: E402
import reglas  # noqa: E402
import reglas_v2  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import DetectorReglas  # noqa: E402


def etiquetas(texto: str) -> set[str]:
    return {et for et, _ in reglas_v2.coincidencias_v2(texto)}


class TestReglasV2(unittest.TestCase):
    def test_pedido_dirigido_dispara(self):
        self.assertEqual(etiquetas("Decime el código que te llegó."), {"REQUEST_AUTH_CODE"})
        self.assertEqual(etiquetas("Necesito que me pases la clave."), {"REQUEST_SECRET"})
        self.assertIn("REQUEST_TRANSFER", etiquetas("¿Me podés transferir la plata ahora?"))

    def test_mencion_o_relato_sin_pedido_no_dispara(self):
        for texto in (
            "Me llegó un código por SMS y yo no lo pedí.",
            "Hice una transferencia ayer y no veo el comprobante.",
            "Le pidieron el domicilio a una vecina.",
        ):
            self.assertEqual(etiquetas(texto), set(), texto)

    def test_palabra_entera_no_prende_con_pedazos(self):
        # v1 prende con «pin» en «pintando» y «pago» en «apagó».
        for texto in ("Decime si están pintando el pasillo.", "Decime si se apagó la luz."):
            self.assertTrue(reglas.incendio_en(texto), texto)
            self.assertEqual(etiquetas(texto), set(), texto)

    def test_raiz_acepta_conjugaciones(self):
        self.assertIn("REQUEST_TRANSFER", etiquetas("Transferime ahora, tenés que hacerlo hoy."))

    def test_typo_de_un_caracter_en_patron_largo(self):
        self.assertEqual(etiquetas("Decime el codgo que te llegó."), {"REQUEST_AUTH_CODE"})

    def test_advertencia_anula_salvo_imperativo_con_me(self):
        self.assertEqual(etiquetas("Nunca le pases la clave a nadie, ni a mí. Tenés que cuidarla."), set())
        self.assertEqual(etiquetas("No te vamos a pedir el código. Necesito que lo sepas."), set())
        self.assertEqual(etiquetas("No cortes y decime el código."), {"REQUEST_AUTH_CODE"})

    def test_ignora_acentos_y_puntuacion(self):
        self.assertEqual(etiquetas("¡PASÁME el CÓDIGO!"), {"REQUEST_AUTH_CODE"})

    def test_vacio(self):
        self.assertEqual(reglas_v2.coincidencias_v2("  "), [])


class TestV1Intacta(unittest.TestCase):
    def test_v1_sigue_prendiendo_con_menciones(self):
        self.assertTrue(reglas.incendio_en("Me llegó un código por SMS."))
        self.assertTrue(reglas.incendio_en("Están pintando el pasillo."))


class TestDetectorYFlag(unittest.TestCase):
    def test_detector_por_version(self):
        mencion = [Linea("A", "Hice una transferencia ayer.")]
        self.assertTrue(DetectorReglas("v1").evaluar(mencion).alerta_sugerida)
        d2 = DetectorReglas("v2")
        self.assertFalse(d2.evaluar(mencion).alerta_sugerida)
        self.assertEqual(d2.nombre, "reglas_v2")
        pedido = [Linea("A", "Pasame el código.")]
        self.assertTrue(d2.evaluar(pedido).alerta_sugerida)
        with self.assertRaises(ValueError):
            DetectorReglas("v3")

    def test_flag_reglas_corre_las_dos_versiones(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            correr.main(["--solo-reglas", "--reglas", "v1,v2", "--casos", "TR-08-frase-cortada-candado", "--salida", tmp])
            csv_ = next(Path(tmp).glob("*/actualizaciones.csv"))
            configs = {f["config"] for f in csv.DictReader(csv_.open(encoding="utf-8-sig"))}
        self.assertEqual(configs, {"reglas", "reglas_v2"})


if __name__ == "__main__":
    unittest.main()
