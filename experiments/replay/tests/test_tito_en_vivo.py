"""Tito→SLM en vivo: frases cerradas, sin saltear ninguna y sin modelos reales."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

DIR_REPLAY = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(DIR_REPLAY))

import replay
from casos import Linea
from contexto import Actualizacion
from detectores import Respuesta
from filtro_tito import TitoGuion


class SlmFalso:
    hablantes = "ab"

    def __init__(self):
        self.mensajes = []

    def evaluar_mensaje(self, usuario, lineas):
        self.mensajes.append((usuario, tuple(lineas)))
        return Respuesta(valida=True, alerta_sugerida=False, riesgo=0.2, motivo="revisado", ms=100.0)


def lineas(*textos):
    return tuple(Linea(hablante="A", texto=t) for t in textos)


class TestFlujoEnVivo(unittest.TestCase):
    def flujo(self, **tito):
        self.tito, self.slm = TitoGuion(**tito), SlmFalso()
        return replay.FlujoTitoEnVivo(self.tito, self.slm)

    def test_sin_sospecha_no_consulta_y_suma_el_costo_de_cada_frase(self):
        r = self.flujo().evaluar(lineas("uno", "dos", "tres"))
        self.assertEqual(self.tito.consultas, [(1, "uno"), (2, "dos"), (3, "tres")])
        self.assertEqual(r.consulta, "omitida")
        self.assertEqual((r.ms, r.tito_ms), (15.0, 15.0))
        self.assertEqual(self.slm.mensajes, [])

    def test_una_frase_intermedia_activa_con_su_propio_indicio(self):
        flujo = self.flujo(puntajes={2: 0.9})
        r = flujo.evaluar(lineas("uno", "pasame el código", "tres"))
        self.assertEqual(r.consulta, "slm_valida")
        self.assertEqual((r.indicio_linea, r.indicio_texto, r.indicio_puntaje), (2, "pasame el código", 0.9))
        self.assertEqual(self.tito.consultas, [(1, "uno"), (2, "pasame el código")], "tras activar, Tito no vuelve a correr")
        self.assertEqual(len(self.slm.mensajes), 1)
        self.assertIn("«pasame el código»", self.slm.mensajes[0][0])
        self.assertEqual(r.ms, 110.0)

    def test_no_repuntua_lo_que_ya_vio(self):
        flujo = self.flujo()
        flujo.evaluar(lineas("uno"))
        flujo.evaluar(lineas("uno", "dos"))
        self.assertEqual(self.tito.consultas, [(1, "uno"), (2, "dos")])

    def test_el_fallo_de_una_frase_intermedia_activa_sin_inventar_puntaje(self):
        r = self.flujo(fallos={1}).evaluar(lineas("uno", "dos"))
        self.assertEqual(r.tito_error, "tito_caido")
        self.assertIsNone(r.indicio_puntaje)
        self.assertEqual(len(self.slm.mensajes), 1)

    def test_reiniciar_olvida_la_llamada_anterior(self):
        flujo = self.flujo(puntajes={1: 0.9})
        flujo.evaluar(lineas("uno"))
        flujo.reiniciar()
        flujo.tito.puntajes = {}
        r = flujo.evaluar(lineas("otra"))
        self.assertEqual(r.consulta, "omitida")
        self.assertEqual(flujo.tito.consultas[-1], (1, "otra"))

    def test_flujo_sin_indicio_pasa_mensaje_base_al_slm(self):
        self.tito, self.slm = TitoGuion(puntajes={1: 0.9}), SlmFalso()
        flujo = replay.FlujoTitoEnVivo(self.tito, self.slm, indicio=False)
        r = flujo.evaluar(lineas("pasame el token"))
        self.assertEqual(r.consulta, "slm_valida")
        self.assertEqual(len(self.slm.mensajes), 1)
        mensaje_enviado = self.slm.mensajes[0][0]
        # El SLM recibe solo el mensaje base, sin mención a indicio, sospecha ni puntaje
        self.assertNotIn("filtro previo", mensaje_enviado)
        self.assertNotIn("sospecha preliminar", mensaje_enviado)
        self.assertNotIn("«pasame el token»", mensaje_enviado)
        self.assertIn("1. A: pasame el token", mensaje_enviado)


class TestCorrerReplay(unittest.TestCase):
    def act(self, n, tipo, segmento, texto, canal="otra", llamada="L1"):
        return Actualizacion(llamada_id=llamada, n=n, tipo=tipo, segmento=segmento, texto=texto, canal=canal)

    def test_en_replay_tito_no_ve_borradores_y_se_reinicia_por_llamada(self):
        tito, slm = TitoGuion(), SlmFalso()
        acts = [self.act(1, "parcial", 2, "borrador", canal="protegida"),
                self.act(2, "final", 1, "cerrada"),
                self.act(3, "final", 1, "otra llamada", llamada="L2")]
        filas, _ = replay.correr_replay(acts, replay.FlujoTitoEnVivo(tito, slm), hablantes="ab")
        self.assertEqual(tito.consultas, [(1, "cerrada"), (1, "otra llamada")])
        self.assertEqual(len(filas), 3)

    def test_correr_replay_rol_con_tito_slm_tito_ve_solo_texto_y_slm_ve_roles(self):
        tito, slm = TitoGuion(puntajes={1: 0.9}), SlmFalso()
        acts = [
            self.act(1, "final", 1, "Hola del banco", canal="otra"),
            self.act(2, "final", 2, "Buenos días", canal="protegida"),
        ]
        detector = replay.FlujoTitoEnVivo(tito, slm)
        filas, contextos = replay.correr_replay(acts, detector, hablantes="rol")
        # Tito recibe únicamente el texto de la línea, sin prefijo OTRA/PROTEGIDA
        self.assertEqual(tito.consultas, [(1, "Hola del banco")])
        # SLM recibe mensaje con roles
        self.assertEqual(len(slm.mensajes), 2)
        self.assertIn("1. OTRA: Hola del banco", slm.mensajes[0][0])
        self.assertIn("1. OTRA: Hola del banco\n2. PROTEGIDA: Buenos días", slm.mensajes[1][0])


class TestConstruirDetector(unittest.TestCase):
    def test_tito_slm_usa_el_tito_viejo_y_registra_su_huella(self):
        slm = SlmFalso()
        slm.carga = {"pensar": False}
        tito = TitoGuion()
        informe = {"encoder_ms": 1.0, "error": ""}
        with patch.object(replay, "construir_slm", return_value=slm) as construir, \
                patch.object(replay.tito_real, "preparar_tito_real", return_value=(tito, informe)):
            d = replay.construir_detector("tito-slm", modelo="gemma4:e2b-it-q4_K_M")
        self.assertEqual(construir.call_args.kwargs["modelo"], "gemma4:e2b-it-q4_K_M")
        self.assertIsInstance(d, replay.FlujoTitoEnVivo)
        self.assertEqual(d.umbral, 0.5)
        self.assertEqual(d.carga["pensar"], False)
        self.assertEqual(d.carga["tito"]["artefacto"], "tito_logreg.json")
        self.assertTrue(d.carga["tito"]["sha256"].startswith("fb601eaa"))
        self.assertTrue(d.carga["tito"]["indicio"])

    def test_construir_detector_con_indicio_true_y_false(self):
        slm = SlmFalso()
        slm.carga = {"pensar": False}
        tito = TitoGuion()
        informe = {"encoder_ms": 1.0, "error": ""}
        with patch.object(replay, "construir_slm", return_value=slm), \
                patch.object(replay.tito_real, "preparar_tito_real", return_value=(tito, informe)):
            d_con = replay.construir_detector("tito-slm", indicio=True)
            self.assertTrue(d_con.indicio)
            self.assertTrue(d_con.carga["tito"]["indicio"])

            d_sin = replay.construir_detector("tito-slm", indicio=False)
            self.assertFalse(d_sin.indicio)
            self.assertFalse(d_sin.carga["tito"]["indicio"])

    def test_el_manifiesto_de_tito_slm_registra_modelo_prompt_seed_y_huella(self):
        with tempfile.TemporaryDirectory() as tmp:
            entrada, salida = Path(tmp) / "entrada.jsonl", Path(tmp) / "manifiesto.json"
            entrada.write_text("", encoding="utf-8")
            replay.guardar_manifiesto(salida, entrada, "audio", "tito-slm", "gemma4:e2b-it-q4_K_M", "tarea", "ab",
                                      "final", 42, carga={"tito": {"sha256": "fb601eaa"}})
            manifiesto = json.loads(salida.read_text(encoding="utf-8"))
        self.assertEqual(manifiesto["config"]["modelo"], "gemma4:e2b-it-q4_K_M")
        self.assertEqual(manifiesto["config"]["prompt"], "tarea")
        self.assertEqual(manifiesto["config"]["seed"], 42)
        self.assertEqual(manifiesto["carga"]["tito"]["sha256"], "fb601eaa")

    def test_sin_torch_falla_al_arrancar_y_no_a_mitad_de_la_llamada(self):
        with patch.object(replay, "construir_slm", return_value=SlmFalso()), \
                patch.object(replay.tito_real, "preparar_tito_real",
                             return_value=(TitoGuion(), {"error": "tito_preparar_error: sin torch"})):
            with self.assertRaisesRegex(RuntimeError, "sin torch"):
                replay.construir_detector("tito-slm", modelo="gemma4:e2b-it-q4_K_M")


if __name__ == "__main__":
    unittest.main()
