"""Corte de frases de MotorPorFrases (Parakeet, Whisper) con un transcriptor falso."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motores import DetectorSilero, MotorPorFrases, es_muletilla_final, parece_otro_idioma  # noqa: E402

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


class MotorGuion(MotorPorFrases):
    """Devuelve los textos del guion en orden, uno por cada llamada a `_transcribir`."""

    def __init__(self, textos, parciales_cada_s=None):
        super().__init__(sample_rate=HZ, parciales_cada_s=parciales_cada_s)
        self.textos = list(textos)

    def _transcribir(self, audio):
        return self.textos.pop(0) if len(self.textos) > 1 else self.textos[0]

    def inicializar(self):
        pass

    def metadatos(self):
        return {}


class VadFalso:
    """Hace de `VadModel` de sherpa: dice voz si la ventana tiene amplitud por encima de `nivel`."""

    def __init__(self, nivel=0.05):
        self.nivel = nivel
        self.ventanas = []  # tamaño de cada ventana recibida
        self.reinicios = 0

    def is_speech(self, ventana):
        self.ventanas.append(len(ventana))
        return bool(np.max(np.abs(ventana)) > self.nivel)

    def reset(self):
        self.reinicios += 1


def con_silero(motor, nivel=0.05):
    motor.detector_voz = DetectorSilero("no-hace-falta.onnx", vad=VadFalso(nivel))
    return motor


def alimentar(motor, segundos_por_tramo, valor_voz=0.1, valor_silencio=0.0):
    """Tramos alternados de voz y silencio; devuelve los eventos y el fin del audio."""
    eventos, t = [], 0.0
    for i, dur in enumerate(segundos_por_tramo):
        valor = valor_voz if i % 2 == 0 else valor_silencio
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
        self.assertEqual([e.tipo for e in eventos], ["parcial"] * 2 + ["final"])
        self.assertTrue(all(e.segmento == 1 for e in eventos))
        self.assertAlmostEqual(eventos[-1].fin_audio_s, fin)

    def test_primer_borrador_recien_con_un_segundo_de_voz(self):
        motor = MotorEco(parciales_cada_s=0.5)
        eventos, _ = alimentar(motor, [0.9])
        self.assertEqual([e.tipo for e in eventos], ["final"])  # sin borradores
        motor = MotorEco(parciales_cada_s=0.5)
        parciales = [e for e in alimentar(motor, [1.2])[0] if e.tipo == "parcial"]
        self.assertEqual(len(parciales), 1)
        self.assertGreaterEqual(parciales[0].fin_audio_s, MotorPorFrases.MIN_VOZ_PARCIAL_S)

    def test_borrador_en_ingles_no_se_emite_y_queda_el_anterior(self):
        motor = MotorGuion(["Hola, buenas", "Yeah, what's up", "Hola, buenas tardes", "Hola, buenas tardes."],
                           parciales_cada_s=0.5)
        eventos, _ = alimentar(motor, [2.5])
        parciales = [e.texto for e in eventos if e.tipo == "parcial"]
        self.assertEqual(parciales, ["Hola, buenas", "Hola, buenas tardes"])
        self.assertNotIn("Yeah, what's up", [e.texto for e in eventos])

    def test_ok_y_okay_se_emiten(self):
        for texto in ("Okay.", "ok"):
            motor = MotorGuion([texto], parciales_cada_s=0.5)
            eventos, _ = alimentar(motor, [1.2])
            self.assertEqual([e.texto for e in eventos], [texto, texto])  # borrador y final

    def test_final_muletilla_se_descarta_y_no_avanza_el_segmento(self):
        motor = MotorGuion(["Thank you.", "Hola, qué tal"])
        eventos, _ = alimentar(motor, [1.0, 1.5, 1.0])
        self.assertEqual([(e.texto, e.segmento) for e in eventos], [("Hola, qué tal", 1)])

    def test_final_en_ingles_que_no_es_muletilla_se_conserva(self):
        for texto in ("Dang say what's up, boy.", "No one."):
            motor = MotorGuion([texto])
            eventos, _ = alimentar(motor, [1.0])
            self.assertEqual([e.texto for e in eventos], [texto])

    def test_filtro_de_idioma_por_palabras(self):
        self.assertTrue(parece_otro_idioma("Uh but it's good"))
        self.assertTrue(parece_otro_idioma("Yeah."))
        self.assertTrue(parece_otro_idioma("Olá, obrigado"))
        self.assertFalse(parece_otro_idioma("Okay."))
        self.assertFalse(parece_otro_idioma("ok"))
        self.assertFalse(parece_otro_idioma("Mandame el link por mail"))
        self.assertFalse(parece_otro_idioma("Entrá al home banking con el token"))
        self.assertFalse(parece_otro_idioma("Prueba one."))  # «prueba» es español
        self.assertFalse(parece_otro_idioma("Sí, es la app de WhatsApp"))
        self.assertTrue(es_muletilla_final("Thank you."))
        self.assertTrue(es_muletilla_final("Yeah. Yes."))
        self.assertFalse(es_muletilla_final("Thank you, Laura."))
        self.assertFalse(es_muletilla_final(""))

    def test_segmentacion_registra_el_filtro(self):
        seg = MotorEco(parciales_cada_s=0.5)._segmentacion()
        self.assertEqual(seg["min_voz_parcial_s"], 1.0)
        self.assertEqual(seg["filtro_idioma"], "parciales_y_muletillas_finales")

    def test_frase_sin_pausa_se_corta_en_el_maximo(self):
        motor = MotorEco()
        eventos, _ = alimentar(motor, [MotorPorFrases.MAX_FRASE_S + 2.0])
        self.assertEqual(len([e for e in eventos if e.tipo == "final"]), 2)



class TestDetectorSilero(unittest.TestCase):
    def test_por_defecto_decide_el_rms(self):
        motor = MotorEco()
        self.assertIsNone(motor.detector_voz)
        seg = motor._segmentacion()
        self.assertEqual(seg["tipo"], "corte_por_silencio_rms")
        self.assertNotIn("vad", seg)

    def test_mismo_corte_preaudio_y_tope_que_con_rms(self):
        # Si Silero ve voz donde el RMS ve voz, las frases son las mismas: solo cambia quién decide. Los tiempos
        # pueden correrse un bloque: la ventana de 512 que cruza al primer bloque de silencio todavía tiene voz,
        # así que el cierre llega 40 ms después y el preaudio de la frase siguiente puede empezar 40 ms más tarde.
        for tramos in ([1.0, 1.5, 0.8, 1.0], [0.12, 1.0, 1.0], [MotorPorFrases.MAX_FRASE_S + 2.0]):
            rms, _ = alimentar(MotorEco(parciales_cada_s=0.5), tramos)
            silero, _ = alimentar(con_silero(MotorEco(parciales_cada_s=0.5)), tramos)
            self.assertEqual([(e.tipo, e.texto, e.segmento) for e in silero], [(e.tipo, e.texto, e.segmento) for e in rms])
            for e_s, e_r in zip(silero, rms):
                self.assertIn(round(e_s.fin_audio_s - e_r.fin_audio_s, 3), (0.0, 0.04))
                self.assertIn(round(e_s.inicio_audio_s - e_r.inicio_audio_s, 3), (0.0, 0.04))

    def test_ruido_fuerte_que_no_es_voz_no_llama_al_asr(self):
        # 0,03 de amplitud pasa el RMS de 0,005, pero el VAD (falso) lo toma como silencio.
        rms = MotorEco()
        alimentar(rms, [1.0, 1.0], valor_voz=0.03)
        self.assertEqual(rms.llamadas, 1)
        silero = con_silero(MotorEco())
        eventos, _ = alimentar(silero, [1.0, 1.0], valor_voz=0.03)
        self.assertEqual((eventos, silero.llamadas), ([], 0))

    def test_voz_debil_bajo_el_umbral_rms_la_decide_el_vad(self):
        motor = con_silero(MotorEco(), nivel=0.001)
        motor.umbral_rms_silencio = 0.5  # con RMS no habría ninguna frase
        eventos, _ = alimentar(motor, [1.0, 1.0], valor_voz=0.002)
        self.assertEqual(len([e for e in eventos if e.tipo == "final"]), 1)

    def test_ventanas_de_512_con_el_resto_para_el_bloque_siguiente(self):
        vad = VadFalso()
        detector = DetectorSilero("x.onnx", vad=vad)
        decisiones = [detector.es_voz(np.full(BLOQUE, 0.1 if i < 5 else 0.0, dtype=np.float32)) for i in range(10)]
        self.assertEqual(vad.ventanas, [512] * 12)  # 6400 muestras: 12 ventanas y sobran 256
        self.assertEqual(len(detector.pendiente), 256)
        # El bloque 6 (índice 5) todavía cierra una ventana con 384 muestras de voz del bloque 5.
        self.assertEqual(decisiones, [True] * 6 + [False] * 4)

    def test_bloque_que_no_cierra_ventana_repite_la_decision_anterior(self):
        detector = DetectorSilero("x.onnx", vad=VadFalso())
        self.assertTrue(detector.es_voz(np.full(600, 0.1, dtype=np.float32)))
        self.assertTrue(detector.es_voz(np.zeros(100, dtype=np.float32)))  # 188 pendientes: ninguna ventana nueva
        self.assertEqual(len(detector.vad.ventanas), 1)

    def test_nueva_sesion_reinicia_el_vad(self):
        motor = con_silero(MotorEco())
        motor.procesar_bloque(np.full(300, 0.1, dtype=np.float32), 0.0, 0.02)
        motor.nueva_sesion()
        self.assertEqual(motor.detector_voz.vad.reinicios, 2)  # al crearlo y al cambiar de prueba
        self.assertEqual(len(motor.detector_voz.pendiente), 0)
        self.assertFalse(motor.detector_voz.ultima)

    def test_segmentacion_y_costo_del_vad(self):
        motor = con_silero(MotorEco())
        alimentar(motor, [0.4])
        seg = motor._segmentacion()
        self.assertEqual(seg["tipo"], "corte_por_silencio_silero")
        self.assertIsNone(seg["umbral_rms_silencio"])
        self.assertEqual((seg["corte_silencio_s"], seg["previo_s"], seg["max_frase_s"], seg["min_voz_s"]),
                         (0.8, MotorPorFrases.PREVIO_S, MotorPorFrases.MAX_FRASE_S, MotorPorFrases.MIN_VOZ_S))
        vad = seg["vad"]
        self.assertEqual((vad["umbral"], vad["umbral_para_seguir"], vad["ventana"]), (0.5, 0.35, 512))
        self.assertEqual(vad["costo_por_bloque"]["bloques"], 10)

    def test_sin_modelo_avisa(self):
        detector = DetectorSilero("/no/existe/silero_vad.onnx")
        with self.assertRaises(RuntimeError):
            detector.es_voz(np.zeros(BLOQUE, dtype=np.float32))


if __name__ == "__main__":
    unittest.main()
