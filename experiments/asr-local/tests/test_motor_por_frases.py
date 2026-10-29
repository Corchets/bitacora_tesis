"""Corte de frases de MotorPorFrases (Parakeet, Whisper) con un transcriptor falso."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from motores import MotorPorFrases, es_muletilla_final, parece_otro_idioma  # noqa: E402

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


if __name__ == "__main__":
    unittest.main()
