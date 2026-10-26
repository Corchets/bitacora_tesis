"""Medición sin panel: fuente de #77, MotorFalso y reloj controlado."""
import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import soundfile as sf

from test_llamada import Reloj, RespuestaFalsa
from motores import MotorFalso
from medir import Medicion, parse_args, resumir


class DetectorFalso:
    def evaluar(self, foto):
        return RespuestaFalsa(ms=1250, alerta_sugerida=True, motivo="pide código")


class MedicionFalsa(Medicion):
    def crear_motor(self):
        return MotorFalso([{"tiempo_audio_s": 0.08, "tipo": "final", "segmento": 1,
                            "texto": "Pasame el código."}])


class TestMedir(unittest.IsolatedAsyncioTestCase):
    async def test_ejemplo_sin_panel_guarda_medicion_y_no_wav(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "entrada.wav"
            sf.write(ruta, np.full((1600, 2), 0.25), 16000)
            args = parse_args(["--detector", "reglas", "--salida", str(Path(tmp) / "salida")])
            reloj = Reloj()

            async def avanzar(segundos):
                reloj.t += segundos
                await asyncio.sleep(0)

            medicion = MedicionFalsa(args, DetectorFalso(), ahora=reloj, dormir=avanzar)
            with patch.dict("servidor.EJEMPLOS", {"SC-WA-CODE-01": ruta}):
                carpeta = await medicion.correr()
            m = json.loads((carpeta / "manifiesto.json").read_text())
            self.assertFalse(list(carpeta.glob("*.wav")))
            self.assertEqual(m["detector"]["evaluaciones"], 1)
            self.assertEqual(m["detector"]["segundos_detector"]["mediana"], 1.25)
            self.assertIsNone(m["estereo"])
            self.assertEqual(m["medicion"]["escenario"], "SC-WA-CODE-01")
            texto = resumir(m)
            self.assertIn("CUMPLE", texto)
            self.assertIn("1,250 s", texto)
            self.assertIn("evaluaciones: 1", texto)
            self.assertIn("salteadas: 1", texto)
            self.assertIn("fin del pedido", texto)
            self.assertEqual(m["canales"]["otra"]["duracion_s"], 0.1)

    async def test_detector_lento_toma_ultima_foto_y_no_pierde_evaluacion_al_final(self):
        import threading

        inicio = threading.Event()
        liberar = threading.Event()
        fotos = []

        class DetectorLento:
            def evaluar(self, foto):
                fotos.append([l.texto for l in foto])
                if len(fotos) == 1:
                    inicio.set()
                    if not liberar.wait(3):
                        raise RuntimeError("El reloj de prueba no liberó el detector")
                return RespuestaFalsa(ms=2100)

        class MedicionLenta(Medicion):
            def crear_motor(self):
                return MotorFalso([
                    {"tiempo_audio_s": t, "tipo": "final", "segmento": n, "texto": texto}
                    for n, (t, texto) in enumerate(((0.04, "Hola"), (0.08, "Del banco"),
                                                    (0.12, "Pasame el código")), 1)
                ])

        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "entrada.wav"
            sf.write(ruta, np.full((2560, 2), 0.25), 16000)
            args = parse_args(["--detector", "reglas", "--salida", str(Path(tmp) / "salida")])
            reloj = Reloj()
            bloques = 0

            async def avanzar(segundos):
                nonlocal bloques
                bloques += 1
                if bloques == 2:
                    self.assertTrue(await asyncio.to_thread(inicio.wait, 2))
                reloj.t += segundos
                await asyncio.sleep(0)
                if bloques == 4:
                    liberar.set()

            medicion = MedicionLenta(args, DetectorLento(), ahora=reloj, dormir=avanzar)
            try:
                with patch.dict("servidor.EJEMPLOS", {"SC-WA-CODE-01": ruta}):
                    carpeta = await medicion.correr()
            finally:
                liberar.set()
            m = json.loads((carpeta / "manifiesto.json").read_text())
            self.assertEqual(m["detector"]["evaluaciones"], 2)
            self.assertEqual(m["detector"]["actualizaciones_salteadas"], 4)
            self.assertIn("Pasame el código", fotos[-1])
            self.assertIn("NO CUMPLE", resumir(m))
            self.assertIn("sin aviso", resumir(m))
