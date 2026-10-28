"""Corte de frases de MotorPorFrases (Parakeet, Whisper) con un transcriptor falso."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motores import MotorPorFrases  # noqa: E402

HZ = 16000
BLOQUE = 640  # 40 ms, como el panel


class MotorEco(MotorPorFrases):
    """Devuelve cuántos bloques de voz tiene la frase, para saber qué audio recibió."""

    def __init__(self, parciales_cada_s=None):
        super().__init__(sample_rate=HZ, parciales_cada_s=parciales_cada_s)
        self.llamadas = 0

    def _transcribir(self, audio):
        self.llamadas += 1
        return f"voz {int(np.sum(np.abs(audio) > 0.05) // BLOQUE)}"

    def inicializar(self):
        pass

    def metadatos(self):
        return {}


def alimentar(motor, segundos_por_tramo):
    """Tramos alternados de voz y silencio; devuelve los eventos y el fin del audio."""
    eventos, t = [], 0.0
    for i, dur in enumerate(segundos_por_tramo):
        valor = 0.1 if i % 2 == 0 else 0.0
        for _ in range(round(dur / 0.04)):
            eventos += motor.procesar_bloque(np.full(BLOQUE, valor, dtype=np.float32), t, t + 0.04)
            t = round(t + 0.04, 3)
    return eventos + motor.vaciar_final(t), t


class TestMotorPorFrases(unittest.TestCase):
    def test_corta_por_silencio_y_numera_segmentos(self):
        motor = MotorEco()
        eventos, _ = alimentar(motor, [1.0, 1.5, 0.8, 1.0])
        finales = [e for e in eventos if e.tipo == "final"]
        self.assertEqual([e.texto for e in finales], ["voz 25", "voz 20"])
        self.assertEqual([e.segmento for e in finales], [1, 2])
        # La primera cierra a 1,8 s; la segunda arranca 0,3 s antes de su voz (2,5 s), no en 1,8 s.
        self.assertAlmostEqual(finales[0].fin_audio_s, 1.8, places=2)
        self.assertAlmostEqual(finales[1].inicio_audio_s, 2.2, delta=0.05)  # bloques de 40 ms

    def test_descarta_golpes_cortos_sin_transcribir(self):
        motor = MotorEco()
        eventos, _ = alimentar(motor, [0.12, 1.0, 1.0])
        self.assertEqual([e.texto for e in eventos], ["voz 25"])
        self.assertEqual(motor.llamadas, 1)

    def test_borradores_mientras_habla_y_final_al_terminar_el_audio(self):
        motor = MotorEco(parciales_cada_s=0.5)
        eventos, fin = alimentar(motor, [2.0])
        self.assertEqual([e.tipo for e in eventos], ["parcial"] * 3 + ["final"])
        self.assertTrue(all(e.segmento == 1 for e in eventos))
        self.assertAlmostEqual(eventos[-1].fin_audio_s, fin)

    def test_frase_sin_pausa_se_corta_en_el_maximo(self):
        motor = MotorEco()
        eventos, _ = alimentar(motor, [MotorPorFrases.MAX_FRASE_S + 2.0])
        self.assertEqual(len([e for e in eventos if e.tipo == "final"]), 2)


if __name__ == "__main__":
    unittest.main()
