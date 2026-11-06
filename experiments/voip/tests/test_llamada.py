"""Tests de la llamada en vivo sin micrófonos ni modelos (MotorFalso y reloj controlado).

Verifica:
1. Cada canal numera sus segmentos desde 1; la llamada los renumera sin choques.
2. A es quien habló primero; cada línea trae su rol.
3. El JSONL lo lee replay.py y cumple disponible_s >= fin_audio_s.
4. Un segmento que es solo puntuación no se registra.
5. Un canal que llega tarde queda en su lugar en el estéreo.
6. El detector junta los disparos acumulados y el aviso es único.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import patch

import numpy as np

DIR_VOIP = Path(__file__).resolve().parent.parent
if str(DIR_VOIP) not in sys.path:
    sys.path.insert(0, str(DIR_VOIP))

from llamada import SAMPLE_RATE, Llamada
from detectores import armar_mensaje_usuario
from motores import MotorFalso
from replay import FlujoTitoEnVivo, cargar_actualizaciones_jsonl, correr_replay

BLOQUE = SAMPLE_RATE // 10  # 100 ms


class Reloj:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


@dataclass
class RespuestaFalsa:
    valida: bool = True
    alerta_sugerida: bool = False
    riesgo: float | None = None
    motivo: str = ""
    evidencia: str = ""
    error: str = ""
    ms: float | None = 5.0
    tito_ms: float | None = None


def programas(*eventos_por_rol):
    """crear_motor que devuelve un MotorFalso por rol, en el orden protegida, otra."""
    pendientes = list(eventos_por_rol)
    return lambda: MotorFalso(pendientes.pop(0))


def pcm(segundos: float, amplitud: float = 0.1) -> bytes:
    return (np.full(int(segundos * SAMPLE_RATE), amplitud * 32767)).astype("<i2").tobytes()


class TestLlamada(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name) / "llamada"
        self.reloj = Reloj()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def armar(self, protegida, otra, disparo="final", hablantes="ab") -> Llamada:
        llamada = Llamada(crear_motor=programas(protegida, otra), disparo=disparo, hablantes=hablantes, ahora=self.reloj)
        llamada.abrir("VIVO-TEST", self.dir)
        return llamada

    def mandar(self, llamada: Llamada, rol: str, segundos: float) -> list[dict]:
        """Manda bloques de 100 ms avanzando el reloj como si llegaran en vivo."""
        acts = []
        for _ in range(int(round(segundos * 10))):
            self.reloj.t += 0.1
            acts += llamada.recibir(rol, pcm(0.1))
        return acts

    def test_segmentos_letras_y_contrato(self):
        otra = [
            {"tiempo_audio_s": 0.5, "tipo": "parcial", "segmento": 1, "texto": "hola"},
            {"tiempo_audio_s": 1.0, "tipo": "final", "segmento": 1, "texto": "Hola, te llamo del banco."},
            {"tiempo_audio_s": 1.2, "tipo": "final", "segmento": 2, "texto": "."},
            {"tiempo_audio_s": 2.0, "tipo": "final", "segmento": 3, "texto": "Pasame el código."},
        ]
        protegida = [{"tiempo_audio_s": 1.5, "tipo": "final", "segmento": 1, "texto": "¿Qué código?"}]
        llamada = self.armar(protegida, otra)
        for _ in range(20):
            self.reloj.t += 0.1
            llamada.recibir("otra", pcm(0.1))
            llamada.recibir("protegida", pcm(0.1))
        llamada.cerrar()

        meta, acts = cargar_actualizaciones_jsonl(self.dir / "actualizaciones.jsonl")
        self.assertEqual(meta["modo"], "en_vivo")
        finales = [a for a in acts if a.tipo == "final"]
        self.assertEqual([a.texto for a in finales], ["Hola, te llamo del banco.", "¿Qué código?", "Pasame el código."])
        self.assertEqual([a.canal for a in finales], ["otra", "protegida", "otra"])
        self.assertEqual(len({a.segmento for a in finales}), 3)
        for a in acts:
            self.assertGreaterEqual(a.disponible_s, a.fin_audio_s)
        registros = [json.loads(l) for l in (self.dir / "actualizaciones.jsonl").read_text().splitlines()[1:]]
        self.assertTrue(all("rol" not in a for a in registros))
        self.assertEqual([l.hablante for l in llamada.foto], ["A", "B", "A"])

    def test_detector_y_replay_conservan_letras_por_primer_texto(self):
        for primera, segunda in (("protegida", "otra"), ("otra", "protegida")):
            with self.subTest(primera=primera):
                eventos = {
                    primera: [
                        {"tiempo_audio_s": 0.5, "tipo": "parcial", "segmento": 1, "texto": "Hola"},
                        {"tiempo_audio_s": 1.5, "tipo": "final", "segmento": 1, "texto": "Hola, ¿quién habla?"},
                    ],
                    segunda: [
                        {"tiempo_audio_s": 0.2, "tipo": "final", "segmento": 1, "texto": "."},
                        {"tiempo_audio_s": 1.0, "tipo": "final", "segmento": 2, "texto": "Del banco."},
                    ],
                }
                llamada = self.armar(eventos["protegida"], eventos["otra"])
                fotos = []
                mensajes = []
                for _ in range(15):
                    self.reloj.t += 0.1
                    for rol in (primera, segunda):
                        for act in llamada.recibir(rol, pcm(0.1)):
                            mensajes.append((act["canal"], act["rol"]))
                            if llamada.marcar_disparo(act):
                                _, foto, _ = llamada.tomar_foto()
                                fotos.append([(l.hablante, l.texto) for l in foto])
                llamada.cerrar()
                esperado = [
                    [("B", "Del banco."), ("A", "Hola")],
                    [("B", "Del banco."), ("A", "Hola, ¿quién habla?")],
                ]
                self.assertEqual(fotos, esperado)
                self.assertEqual(mensajes, [("A", primera), ("B", segunda), ("A", primera)])

                class DetectorFalso:
                    hablantes = "ab"

                    def __init__(self):
                        self.fotos = []

                    def evaluar(self, lineas):
                        self.fotos.append([(l.hablante, l.texto) for l in lineas])
                        return RespuestaFalsa()

                _, acts = cargar_actualizaciones_jsonl(self.dir / "actualizaciones.jsonl")
                detector = DetectorFalso()
                filas, _ = correr_replay(acts, detector)
                self.assertEqual(detector.fotos, esperado)
                self.assertEqual(detector.hablantes, "ab")
                self.assertIn("A: Hola", filas[-1]["texto_disponible_resumido"])

    def test_canal_tardio_alineado_en_estereo(self):
        import soundfile as sf

        llamada = self.armar([], [])
        self.mandar(llamada, "otra", 1.0)
        # La protegida empieza a mandar 1 s después: su audio va desde el segundo 1.
        self.mandar(llamada, "protegida", 0.5)
        llamada.cerrar()
        audio, hz = sf.read(self.dir / "estereo.wav", dtype="int16")
        self.assertEqual(hz, SAMPLE_RATE)
        izq, der = audio[:, 0], audio[:, 1]
        self.assertTrue(np.all(izq[: SAMPLE_RATE] == 0))
        self.assertTrue(np.all(izq[SAMPLE_RATE + 10 : int(1.5 * SAMPLE_RATE) - 10] != 0))
        self.assertTrue(np.all(der[: SAMPLE_RATE - 10] != 0))
        manifiesto = json.loads((self.dir / "manifiesto.json").read_text())
        self.assertAlmostEqual(manifiesto["canales"]["protegida"]["inicio_s"], 1.0, places=2)

    def test_disparos_acumulados_y_aviso_unico(self):
        otra = [
            {"tiempo_audio_s": 0.5, "tipo": "parcial", "segmento": 1, "texto": "te llamo"},
            {"tiempo_audio_s": 1.0, "tipo": "final", "segmento": 1, "texto": "Te llamo del banco."},
            {"tiempo_audio_s": 2.0, "tipo": "final", "segmento": 2, "texto": "Necesito validar tu cuenta."},
            {"tiempo_audio_s": 3.0, "tipo": "final", "segmento": 3, "texto": "Pasame el código."},
        ]
        llamada = self.armar([], otra)
        disparos = [a for a in self.mandar(llamada, "otra", 2.0) if llamada.marcar_disparo(a)]
        self.assertEqual(len(disparos), 2)  # el parcial no dispara con --disparo final
        n, foto, juntos = llamada.tomar_foto()
        ev = llamada.registrar_evaluacion(n, juntos, RespuestaFalsa(), 2.0, 2.5)
        self.assertEqual((ev.saltadas, ev.aviso, len(foto)), (1, False, 2))

        for a in self.mandar(llamada, "otra", 1.0):
            llamada.marcar_disparo(a)
        n, foto, juntos = llamada.tomar_foto()
        ev = llamada.registrar_evaluacion(n, juntos, RespuestaFalsa(alerta_sugerida=True, motivo="pide código"), 3.0, 3.4)
        self.assertTrue(ev.aviso)
        self.assertAlmostEqual(ev.fin_s - ev.fin_voz_s, 0.4, places=3)
        otra_alerta = llamada.registrar_evaluacion(n, 0, RespuestaFalsa(alerta_sugerida=True), 3.5, 3.6)
        self.assertFalse(otra_alerta.aviso)
        self.assertFalse(llamada.marcar_disparo({"tipo": "final"}))

        llamada.cerrar()
        manifiesto = json.loads((self.dir / "manifiesto.json").read_text())
        self.assertEqual(manifiesto["detector"]["aviso"]["t_a"], 3.4)

    def test_validacion_hablantes(self):
        with self.assertRaises(ValueError):
            Llamada(crear_motor=programas([], []), hablantes="invalido")

    def test_hablantes_ab_mensaje_exacto(self):
        otra = [{"tiempo_audio_s": 0.05, "tipo": "final", "segmento": 1, "texto": "Hola, te llamo del banco."}]
        protegida = [{"tiempo_audio_s": 0.05, "tipo": "final", "segmento": 1, "texto": "¿Qué código?"}]
        llamada = self.armar(protegida, otra, hablantes="ab")
        self.reloj.t += 0.1
        llamada.recibir("otra", pcm(0.1))
        self.reloj.t += 0.1
        llamada.recibir("protegida", pcm(0.1))
        llamada.cerrar()

        self.assertEqual([l.hablante for l in llamada.foto], ["A", "B"])
        mensaje = armar_mensaje_usuario(llamada.foto, "ab")
        esperado = (
            "Transcripción disponible hasta ahora; la llamada sigue. "
            "Cada línea indica quién habla con A o B. A es quien habló primero; "
            "las letras no indican quién llamó ni quién es sospechoso.\n\n"
            "1. A: Hola, te llamo del banco.\n"
            "2. B: ¿Qué código?\n\n"
            "Evaluá la llamada con lo disponible hasta la línea 2."
        )
        self.assertEqual(mensaje, esperado)

    def test_hablantes_rol_foto_mensajes_y_tito(self):
        otra = [
            {"tiempo_audio_s": 0.05, "tipo": "parcial", "segmento": 1, "texto": "hola"},
            {"tiempo_audio_s": 0.15, "tipo": "final", "segmento": 1, "texto": "Hola, te llamo del banco."},
        ]
        protegida = [
            {"tiempo_audio_s": 0.15, "tipo": "parcial", "segmento": 1, "texto": "que"},
            {"tiempo_audio_s": 0.25, "tipo": "final", "segmento": 1, "texto": "¿Qué código?"},
        ]
        llamada = self.armar(protegida, otra, hablantes="rol")

        # Primer parcial de 'otra': hablantes ya es OTRA
        self.reloj.t += 0.1
        acts_otra = llamada.recibir("otra", pcm(0.1))
        self.assertEqual(len(acts_otra), 1)
        self.assertEqual([l.hablante for l in llamada.foto], ["OTRA"])
        self.assertEqual(acts_otra[0]["canal"], "A")
        self.assertEqual(acts_otra[0]["rol"], "otra")

        # Primer parcial de 'protegida': hablantes incluye PROTEGIDA
        self.reloj.t += 0.1
        acts_prot = llamada.recibir("protegida", pcm(0.1))
        self.assertEqual(len(acts_prot), 1)
        self.assertEqual([l.hablante for l in llamada.foto], ["OTRA", "PROTEGIDA"])
        self.assertEqual(acts_prot[0]["canal"], "B")
        self.assertEqual(acts_prot[0]["rol"], "protegida")

        # Cierre final de ambas
        self.reloj.t += 0.1
        acts_otra_final = llamada.recibir("otra", pcm(0.1))
        self.assertEqual(len(acts_otra_final), 1)
        self.assertEqual(acts_otra_final[0]["canal"], "A")
        self.assertEqual(acts_otra_final[0]["rol"], "otra")
        self.reloj.t += 0.1
        acts_prot_final = llamada.recibir("protegida", pcm(0.1))
        self.assertEqual(len(acts_prot_final), 1)
        self.assertEqual(acts_prot_final[0]["canal"], "B")
        self.assertEqual(acts_prot_final[0]["rol"], "protegida")

        self.assertEqual(
            [(l.hablante, l.texto) for l in llamada.foto],
            [("OTRA", "Hola, te llamo del banco."), ("PROTEGIDA", "¿Qué código?")],
        )

        mensaje = armar_mensaje_usuario(llamada.foto, "rol")
        esperado = (
            "Transcripción disponible hasta ahora; la llamada sigue. "
            "Cada línea indica quién habla: PROTEGIDA es la persona que protegés y OTRA es con quien habla.\n\n"
            "1. OTRA: Hola, te llamo del banco.\n"
            "2. PROTEGIDA: ¿Qué código?\n\n"
            "Evaluá la llamada con lo disponible hasta la línea 2."
        )
        self.assertEqual(mensaje, esperado)

        # Tito recibe solo el texto de cada línea (sin prefijo de hablante)
        tito_evaluados = []
        class TitoMock:
            def puntuar(self, n, texto):
                tito_evaluados.append(texto)
                return 0.1, None, 1.0

        detector_tito = FlujoTitoEnVivo(TitoMock(), slm=None, indicio=False)
        with patch("filtro_tito.FlujoTitoSLM.evaluar", return_value=RespuestaFalsa()):
            detector_tito.evaluar(llamada.foto)
        self.assertEqual(tito_evaluados, ["Hola, te llamo del banco."])

        llamada.cerrar()


if __name__ == "__main__":
    unittest.main()
