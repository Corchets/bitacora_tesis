"""Tests unitarios para calcular_audio_referencia.py (#19, #28).

Verifica:
1. Parseo correcto de turnos con hablantes A/B.
2. Derivación exacta de T_R y T_C basada en duraciones y pausas de 1,0 s.
3. Asignación de T_R=None y T_C=None para llamadas legítimas (LG).
4. Formato de metadatos con origen explícito: "derivado de la construcción del audio TTS, no anotación humana".
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

CARPETA_ASR = Path(__file__).resolve().parent.parent
import sys

if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

from calcular_audio_referencia import calcular_referencia_caso, parsear_dialogo


class TestCalcularAudioReferencia(unittest.TestCase):

    def test_parsear_dialogo(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write("A: Hola, te llamo de soporte.\n\nB: Hola, no pedí nada.\n")
            tmp_path = Path(f.name)

        try:
            turnos = parsear_dialogo(tmp_path)
            self.assertEqual(len(turnos), 2)
            self.assertEqual(turnos[0], ("A", "Hola, te llamo de soporte."))
            self.assertEqual(turnos[1], ("B", "Hola, no pedí nada."))
        finally:
            tmp_path.unlink()

    def test_derivacion_tiempos_vishing(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            # 5 turnos simulados
            f.write("A: Linea 1\nB: Linea 2\nA: Linea 3\nA: Linea 4 pedido\nB: Linea 5 cumplimiento\n")
            tmp_path = Path(f.name)

        # Medidor simulado: cada turno dura 2.0 segundos
        def medidor_falso(texto: str, voz: str) -> float:
            return 2.0

        caso_def = {
            "id": "SC-TEST-01-tts",
            "texto": tmp_path,
            "clase": "vishing",
            "grupo": "piloto",
            "linea_tr": 4,
            "linea_tc": 5,
        }

        try:
            # Pausa de 1.0s entre turnos:
            # Turno 1 (L1): [0.0, 2.0]
            # Pausa 1s -> Turno 2 (L2): [3.0, 5.0]
            # Pausa 1s -> Turno 3 (L3): [6.0, 8.0]
            # Pausa 1s -> Turno 4 (L4): [9.0, 11.0] -> T_R = 9.0
            # Pausa 1s -> Turno 5 (L5): [12.0, 14.0] -> T_C = 12.0
            ref = calcular_referencia_caso(caso_def, pausa_s=1.0, medidor_duracion=medidor_falso)

            self.assertEqual(ref["case_id"], "SC-TEST-01-tts")
            self.assertEqual(ref["clase"], "vishing")
            self.assertEqual(ref["t_r"], 9.0)
            self.assertEqual(ref["t_c"], 12.0)
            self.assertEqual(ref["duracion_s"], 14.0)
            self.assertEqual(ref["origen"], "derivado de la construcción del audio TTS, no anotación humana")
            self.assertEqual(len(ref["turnos"]), 5)
            self.assertEqual(ref["turnos"][3]["inicio_s"], 9.0)
            self.assertEqual(ref["turnos"][4]["inicio_s"], 12.0)
        finally:
            tmp_path.unlink()

    def test_legitima_sin_tr_tc(self):
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as f:
            f.write("A: Consulta legitima 1\nB: Respuesta legitima 2\n")
            tmp_path = Path(f.name)

        def medidor_falso(texto: str, voz: str) -> float:
            return 1.5

        caso_def = {
            "id": "LG-TEST-01-tts",
            "texto": tmp_path,
            "clase": "legitima_dificil",
            "grupo": "piloto",
            "linea_tr": None,
            "linea_tc": None,
        }

        try:
            ref = calcular_referencia_caso(caso_def, pausa_s=1.0, medidor_duracion=medidor_falso)
            self.assertIsNone(ref["t_r"])
            self.assertIsNone(ref["t_c"])
            self.assertEqual(ref["duracion_s"], 4.0)  # 1.5 + 1.0 + 1.5
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
