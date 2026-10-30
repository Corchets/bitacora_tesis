"""Cuentas de comparar_vad.py (Silero contra RMS) con un transcriptor falso, sin modelos."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import comparar_vad as C  # noqa: E402
from test_motor_por_frases import BLOQUE, MotorEco  # noqa: E402


def audio(tramos):
    """Tramos alternados de voz (0,1) y silencio, en segundos."""
    return np.concatenate([np.full(round(d * 16000), 0.1 if i % 2 == 0 else 0.0, dtype=np.float32)
                           for i, d in enumerate(tramos)])


class TestCompararVad(unittest.TestCase):
    def test_cuenta_segmentos_cierres_y_llamadas(self):
        motor = MotorEco(parciales_cada_s=0.5)
        muestras = audio([0.12, 1.0, 2.0, 1.0, 10.5])
        registro, eventos = C.correr(motor, muestras, 40)
        r = C.resumen_prueba(registro, eventos, C.decisiones_rms(muestras, 40, 0.008), 0.04)
        # Golpe descartado sin ASR, una frase cerrada por silencio y una por el tope que sigue hasta el fin.
        self.assertEqual(r["segmentos_abiertos"], 4)
        self.assertEqual(r["segmentos_transcriptos"], 3)
        self.assertEqual(r["cierres"], {"silencio": 2, "tope": 1, "fin_del_audio": 1})
        self.assertEqual(r["llamadas_asr"], motor.llamadas)
        self.assertGreater(r["llamadas_asr_borrador"], 0)
        self.assertEqual((r["desfase_inicio_s"], r["desfase_fin_s"]), ([0.0, 0.0, 0.0], [0.0, 0.0]))  # RMS contra RMS

    def test_instrumentar_dos_veces_no_anida(self):
        motor = MotorEco()
        for _ in range(2):
            registro, _ = C.correr(motor, audio([1.0, 1.0]), 40)
        self.assertEqual(len(registro["decisiones"]), 50)
        self.assertEqual(len(registro["asr"]), 1)

    def test_desfase_contra_el_flanco_rms_mas_cercano(self):
        sube, baja = C.flancos([False, True, True, False, False, True], 0.04)
        self.assertEqual((sube, baja), ([0.08, 0.24], [0.16]))
        self.assertEqual(C.desfases([1.0, 3.0, 9.0], [0.9, 3.2]), [0.1, -0.2])  # 9,0 no tiene pareja

    def test_primera_palabra_perdida(self):
        self.assertTrue(C.primera_palabra_perdida("Compartí pantalla y entrá", "la pantalla y entra"))
        self.assertFalse(C.primera_palabra_perdida("Compartí pantalla", "Comparti la pantalla"))
        self.assertFalse(C.primera_palabra_perdida("Hola, che", "Y hola che"))

    def test_retranscribe_con_mas_audio_previo(self):
        motor = MotorEco()
        filas = C.retranscribir_pantalla(motor, audio([2.0, 1.0]), [{"inicio_s": 0.5, "fin_s": 2.0, "texto": "la pantalla"}])
        self.assertEqual([f["previo_extra_s"] for f in filas], [0.0, *C.PREVIO_EXTRA_S])
        self.assertEqual([f["texto"] for f in filas], ["voz 37", "voz 45", "voz 50"])  # bloques de voz en cada recorte
        self.assertEqual(motor.llamadas, 3)


if __name__ == "__main__":
    unittest.main()
