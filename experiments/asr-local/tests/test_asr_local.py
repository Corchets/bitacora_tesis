"""Pruebas unitarias para asr_local, motores y wer.

Usa reconocedor falso (MotorFalso) para validar sin dependencias pesadas:
- Orden y forma del JSONL según el contrato compartido.
- Parcial que reemplaza en el mismo segmento y final que cierra.
- Invariante temporal: disponible_s >= fin_audio_s y monotonicidad.
- Cálculo de WER y CER sobre ejemplos conocidos y normalización.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

# Asegurar que el directorio de asr-local esté en sys.path
CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

from asr_local import transcribir_audio
from motores import MotorFalso
from wer import (
    analizar_errores_clave,
    calcular_cer,
    calcular_wer,
    normalizar_texto,
)


class TestWER(unittest.TestCase):
    """Pruebas de normalización y métricas de error WER/CER."""

    def test_normalizacion_basica(self):
        texto = "¡Hola! ¿Cómo estás? Tengo 123 códigos."
        norm = normalizar_texto(texto, sin_tildes=False)
        self.assertEqual(norm, "hola cómo estás tengo 123 códigos")

    def test_normalizacion_sin_tildes(self):
        texto = "¡Hola! ¿Cómo estás? Código número cero."
        norm = normalizar_texto(texto, sin_tildes=True)
        self.assertEqual(norm, "hola como estas codigo numero cero")

    def test_wer_identico(self):
        ref = "decime el código de activación que recibiste por sms"
        hyp = "decime el código de activación que recibiste por sms"
        res = calcular_wer(ref, hyp)
        self.assertEqual(res["wer"], 0.0)
        self.assertEqual(res["distancia"], 0)
        self.assertEqual(res["sustituciones"], 0)
        self.assertEqual(res["eliminaciones"], 0)
        self.assertEqual(res["inserciones"], 0)

    def test_wer_sustitucion_y_eliminacion(self):
        ref = "es cero cero cero"
        hyp = "es cero uno"  # sustitución de 'cero' por 'uno', eliminación de un 'cero'
        res = calcular_wer(ref, hyp)
        self.assertEqual(res["palabras_referencia"], 4)
        self.assertEqual(res["palabras_hipotesis"], 3)
        self.assertEqual(res["sustituciones"], 1)
        self.assertEqual(res["eliminaciones"], 1)
        self.assertEqual(res["inserciones"], 0)
        self.assertEqual(res["distancia"], 2)
        self.assertEqual(res["wer"], 0.5)

    def test_cer_conocido(self):
        ref = "hola"
        hyp = "holaa"  # 1 inserción sobre 4 chars = 0.25
        res = calcular_cer(ref, hyp)
        self.assertEqual(res["cer"], 0.25)
        self.assertEqual(res["inserciones"], 1)

    def test_analisis_errores_clave(self):
        ref = "Decime el código de activación por SMS."
        hyp = "Decime el número de activación por mensaje."
        reporte = analizar_errores_clave(ref, hyp)

        mapa = {r["palabra_clave"]: r["estado"] for r in reporte}
        self.assertIn("codigo", mapa)
        self.assertEqual(mapa["codigo"], "PERDIDA")
        self.assertIn("sms", mapa)
        self.assertEqual(mapa["sms"], "PERDIDA")
        self.assertIn("activacion", mapa)
        self.assertEqual(mapa["activacion"], "OK")


class TestContratoJSONL(unittest.TestCase):
    """Pruebas del formato JSONL y emisión con MotorFalso."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.salida_dir = Path(self.temp_dir.name)

        # Crear un archivo WAV sintético falso de 3 segundos a 16 kHz usando wave de la stdlib
        self.audio_wav = self.salida_dir / "prueba.wav"
        import wave
        sr = 16000
        duracion_s = 3.0
        n_muestras = int(sr * duracion_s)
        # Tono senoidal de 440 Hz en int16
        t = np.linspace(0, duracion_s, n_muestras, endpoint=False)
        muestras_i16 = (3276.0 * np.sin(2 * np.pi * 440 * t)).astype(np.int16)
        with wave.open(str(self.audio_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(muestras_i16.tobytes())

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_contrato_y_secuencia_actualizaciones(self):
        # Programar eventos en MotorFalso:
        # Segmento 1: dos parciales y un final
        # Segmento 2: un parcial y un final
        eventos = [
            {"tiempo_audio_s": 0.4, "tipo": "parcial", "segmento": 1, "texto": "te llamo"},
            {"tiempo_audio_s": 0.8, "tipo": "parcial", "segmento": 1, "texto": "te llamo de soporte"},
            {"tiempo_audio_s": 1.2, "tipo": "final", "segmento": 1, "texto": "Te llamo de soporte."},
            {"tiempo_audio_s": 1.8, "tipo": "parcial", "segmento": 2, "texto": "me llego"},
            {"tiempo_audio_s": 2.4, "tipo": "final", "segmento": 2, "texto": "Me llegó un SMS."},
        ]
        motor = MotorFalso(eventos_programados=eventos)

        manifiesto = transcribir_audio(
            audio_path=self.audio_wav,
            motor=motor,
            salida_dir=self.salida_dir,
            bloque_ms=100,
            simular_tiempo_real=False,
            llamada_id="TEST-CALL-01",
            canal=None,
        )

        # Verificar existencia de archivos
        ruta_jsonl = self.salida_dir / "actualizaciones.jsonl"
        ruta_man = self.salida_dir / "manifiesto.json"
        ruta_res = self.salida_dir / "resumen.md"

        self.assertTrue(ruta_jsonl.exists())
        self.assertTrue(ruta_man.exists())
        self.assertTrue(ruta_res.exists())

        # Leer JSONL línea por línea
        with open(ruta_jsonl, "r", encoding="utf-8") as f:
            lineas = [json.loads(line) for line in f if line.strip()]

        # Primera línea: metadatos
        self.assertIn("meta", lineas[0])
        self.assertEqual(lineas[0]["meta"]["motor"], "falso")
        self.assertEqual(lineas[0]["meta"]["sample_rate"], 16000)

        # Actualizaciones posteriores
        actualizaciones = lineas[1:]
        self.assertEqual(len(actualizaciones), 5)

        prev_disponible = -1.0
        n_esperado = 1

        for act in actualizaciones:
            # Campos obligatorios del contrato
            self.assertEqual(act["llamada_id"], "TEST-CALL-01")
            self.assertEqual(act["n"], n_esperado)
            self.assertIn(act["tipo"], ["parcial", "final"])
            self.assertIsInstance(act["segmento"], int)
            self.assertIsInstance(act["texto"], str)
            self.assertIsInstance(act["inicio_audio_s"], float)
            self.assertIsInstance(act["fin_audio_s"], float)
            self.assertIsInstance(act["disponible_s"], float)
            self.assertIsInstance(act["proceso_ms"], float)
            self.assertIsNone(act["canal"])

            # Invariante: disponible_s >= fin_audio_s
            self.assertGreaterEqual(act["disponible_s"], act["fin_audio_s"])

            # Monotonicidad del reloj del sistema: no retrocede
            self.assertGreaterEqual(act["disponible_s"], prev_disponible)
            prev_disponible = act["disponible_s"]

            n_esperado += 1

        # Verificar comportamiento de segmentos
        # Segmento 1 tiene 2 parciales que se expanden y 1 final que lo cierra
        seg1 = [a for a in actualizaciones if a["segmento"] == 1]
        self.assertEqual(len(seg1), 3)
        self.assertEqual(seg1[0]["tipo"], "parcial")
        self.assertEqual(seg1[0]["texto"], "te llamo")
        self.assertEqual(seg1[1]["tipo"], "parcial")
        self.assertEqual(seg1[1]["texto"], "te llamo de soporte")  # Reemplaza anterior
        self.assertEqual(seg1[2]["tipo"], "final")
        self.assertEqual(seg1[2]["texto"], "Te llamo de soporte.")  # Cierra

        # Segmento 2
        seg2 = [a for a in actualizaciones if a["segmento"] == 2]
        self.assertEqual(len(seg2), 2)
        self.assertEqual(seg2[0]["tipo"], "parcial")
        self.assertEqual(seg2[1]["tipo"], "final")

        # Verificar manifiesto
        self.assertEqual(manifiesto["total_actualizaciones"], 5)
        self.assertEqual(manifiesto["total_parciales"], 3)
        self.assertEqual(manifiesto["total_finales"], 2)
        self.assertEqual(manifiesto["total_segmentos"], 2)
        self.assertGreater(manifiesto["memoria_pico_mb"], 0.0)

        # Verificar advertencia obligatoria en resumen.md
        contenido_md = ruta_res.read_text(encoding="utf-8")
        self.assertIn(
            "audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09",
            contenido_md,
        )
        self.assertIn("Estado: propuesta sin discutir.", contenido_md)


if __name__ == "__main__":
    unittest.main()
