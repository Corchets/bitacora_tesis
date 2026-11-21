"""Reglas de turno del ADR 0007, sin audio: cuándo se cierra un turno y cuándo se consulta."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

DIR_VOIP = Path(__file__).resolve().parent.parent
if str(DIR_VOIP) not in sys.path:
    sys.path.insert(0, str(DIR_VOIP))

from turnos import ReglasTurno, Turnos


def motivos(turnos: Turnos) -> list[tuple[str, str, bool]]:
    return [(c["rol"], c["motivo"], c["consulta"]) for c in turnos.cierres]


class TestTurnos(unittest.TestCase):
    def setUp(self) -> None:
        self.t = Turnos(ReglasTurno())

    def test_cambio_de_hablante_cierra_y_consulta_el_turno_de_otra(self):
        self.assertEqual(self.t.frase("otra", "final", "Te llamo del banco.", 0.0, 1.5), 0)
        self.assertEqual(self.t.frase("otra", "final", "Hubo un movimiento raro.", 2.0, 3.5), 0)
        self.assertEqual(self.t.frase("protegida", "final", "¿Qué movimiento raro?", 4.0, 4.9), 1)
        self.assertEqual(motivos(self.t), [("otra", "cambio", True)])
        self.assertEqual(self.t.cierres[0]["finales"], 2)

    def test_un_aja_no_cierra_pero_hablar_mas_de_un_segundo_si(self):
        self.t.frase("otra", "final", "Te llamo del banco.", 0.0, 1.5)
        self.assertEqual(self.t.frase("protegida", "final", "Ajá.", 2.0, 2.6), 0)
        self.assertEqual(self.t.frase("protegida", "final", "Sí, sí.", 3.0, 3.9), 0)
        self.assertEqual(self.t.cierres, [])
        # Dos palabras, pero el segmento dura más de 1 s: ya es hablar en serio.
        self.assertEqual(self.t.frase("protegida", "parcial", "Mirá, pará", 4.0, 5.2), 1)
        self.assertEqual(motivos(self.t), [("otra", "cambio", True)])

    def test_silencio_largo_cierra_el_turno(self):
        self.t.frase("otra", "final", "Te llamo del banco.", 0.0, 1.5)
        self.assertEqual(self.t.silencio("otra", 1.9, 3.4), 0)
        self.assertEqual(self.t.silencio("otra", 2.0, 3.5), 1)
        self.assertEqual(self.t.silencio("otra", 2.1, 3.6), 0)  # ya cerrado: no consulta dos veces
        self.assertEqual(self.t.cierres[0]["hasta_s"], 3.5)

    def test_protegida_no_consulta(self):
        self.t.frase("protegida", "final", "Hola, ¿quién habla?", 0.0, 1.5)
        self.assertEqual(self.t.silencio("protegida", 2.0, 3.5), 0)
        self.t.frase("protegida", "final", "¿Me escuchás?", 4.0, 5.0)
        self.assertEqual(self.t.frase("otra", "final", "Sí, te llamo del banco.", 5.5, 7.0), 0)
        self.assertEqual(motivos(self.t), [("protegida", "silencio", False), ("protegida", "cambio", False)])

    def test_tope_consulta_al_cerrar_frase_y_el_turno_sigue(self):
        t = Turnos(ReglasTurno(tope_s=10.0))
        self.assertEqual(t.frase("otra", "final", "Uno.", 0.0, 4.0), 0)
        self.assertEqual(t.frase("otra", "parcial", "Dos dos dos", 4.5, 11.0), 0)  # nunca a mitad de frase
        self.assertEqual(t.frase("otra", "final", "Dos dos dos.", 4.5, 12.0), 1)
        self.assertEqual(t.frase("otra", "final", "Tres.", 12.5, 15.0), 0)  # el tope cuenta desde la consulta
        self.assertEqual(t.silencio("otra", 2.0, 17.0), 1)
        self.assertEqual(motivos(t), [("otra", "tope", True), ("otra", "silencio", True)])
        self.assertEqual([c["finales"] for c in t.cierres], [2, 1])

    def test_si_otra_sigue_hablando_el_cambio_espera_su_frase(self):
        self.t.frase("otra", "parcial", "Necesito que me", 0.0, 1.2)
        self.assertEqual(self.t.frase("protegida", "final", "Pará, ¿quién sos?", 1.0, 2.0), 0)
        self.assertEqual(self.t.frase("otra", "final", "Necesito que me leas el código.", 0.0, 2.5), 1)
        self.assertEqual(motivos(self.t)[0], ("otra", "cambio", True))

    def test_un_turno_sin_frases_cerradas_no_consulta(self):
        self.t.frase("otra", "parcial", "Eh", 0.0, 1.2)
        self.assertEqual(self.t.silencio("otra", 2.0, 3.2), 0)
        self.assertEqual(motivos(self.t), [("otra", "silencio", False)])

    def test_al_terminar_consulta_el_turno_abierto_de_otra(self):
        self.t.frase("protegida", "final", "Hola.", 0.0, 0.5)
        self.t.frase("otra", "final", "Pasame el código.", 1.0, 2.0)
        self.assertEqual(self.t.cerrar_todo(2.2), 1)
        self.assertEqual(self.t.abiertos, {})

    def test_reglas_invalidas(self):
        for reglas in ({"palabras": 0}, {"voz_s": -1}, {"silencio_s": 0}, {"tope_s": 0}):
            with self.subTest(reglas=reglas), self.assertRaises(ValueError):
                ReglasTurno(**reglas)


if __name__ == "__main__":
    unittest.main()
