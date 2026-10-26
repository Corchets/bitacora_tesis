"""Control por /panel y ejemplo sin modelos ni espera real."""
import asyncio
import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import numpy as np
import soundfile as sf
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from test_llamada import Reloj, RespuestaFalsa
from motores import MotorFalso
from servidor import Servidor


class DetectorFalso:
    def evaluar(self, foto):
        return RespuestaFalsa()


class ServidorFalso(Servidor):
    def crear_motor(self):
        return MotorFalso()


class TestServidor(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.reloj = Reloj()
        args = Namespace(salida=self.tmp.name, disparo="final", detector="reglas", hilos=2,
                         corte_silencio=0.8)
        self.servidor = ServidorFalso(args, DetectorFalso(), ahora=self.reloj)
        self.servidor.preparar()
        await self.servidor.preparada
        self.red = await serve(self.servidor.atender, "127.0.0.1", 0)
        self.url = f"ws://127.0.0.1:{self.red.sockets[0].getsockname()[1]}"

    async def asyncTearDown(self):
        self.red.close()
        await self.red.wait_closed()
        await self.servidor.cerrar_llamada()
        if self.servidor.preparada:
            await self.servidor.preparada
        self.tmp.cleanup()

    async def evento(self, panel, tipo):
        async with asyncio.timeout(3):
            while True:
                m = json.loads(await panel.recv())
                if m["tipo"] == tipo:
                    return m

    def inicio(self, escenario=None):
        fuentes = {r: {"tipo": "cliente"} for r in ("otra", "protegida")}
        if escenario:
            fuentes = {r: {"tipo": "ejemplo", "escenario": escenario, "canal": c}
                       for r, c in (("otra", "izq"), ("protegida", "der"))}
        return json.dumps({"tipo": "iniciar", "modo": "llamada", "fuentes": fuentes,
                           "corte_silencio_s": None, "umbral_rms_silencio": None})

    async def test_inicio_y_fin_explicitos_sin_audio_y_carpetas_propias(self):
        async with connect(self.url + "/panel") as panel:
            carpetas = []
            ids = []
            for _ in range(2):
                await panel.send(self.inicio())
                ids.append((await self.evento(panel, "inicio"))["llamada_id"])
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")
                carpetas.append(fin["dir"])
                m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
                self.assertEqual(m["llamada_id"], ids[-1])
            self.assertNotEqual(carpetas[0], carpetas[1])
            self.assertNotEqual(ids[0], ids[1])

    async def test_cliente_sigue_abriendo_y_ultimo_cliente_cierra(self):
        async with connect(self.url + "/panel") as panel:
            otra = await connect(self.url + "/audio?rol=otra")
            protegida = await connect(self.url + "/audio?rol=protegida")
            self.reloj.t += 0.04
            await otra.send(np.full(640, 1000, dtype="int16").tobytes())
            await self.evento(panel, "inicio")
            await otra.close()
            await protegida.send(np.full(640, 2000, dtype="int16").tobytes())
            await protegida.close()
            fin = await self.evento(panel, "fin")
            m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
            self.assertEqual(set(m["canales"]), {"otra", "protegida"})

    async def test_fin_explicito_cierra_clientes_y_no_reabre_por_audio_pendiente(self):
        async with connect(self.url + "/panel") as panel:
            async with connect(self.url + "/audio?rol=otra") as audio:
                await audio.send(np.full(640, 1000, dtype="int16").tobytes())
                await self.evento(panel, "inicio")
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")
                await asyncio.wait_for(audio.wait_closed(), 3)
                self.assertEqual(audio.close_code, 1000)
                self.assertTrue((Path(fin["dir"]) / "estereo.wav").exists())
            await panel.send(self.inicio())
            nuevo = await self.evento(panel, "inicio")
            self.assertNotEqual(nuevo["llamada_id"], fin["llamada_id"])

    async def test_ejemplo_reloj_real_canales_alineados_y_ultimo_bloque_corto(self):
        ruta = self.dir / "ejemplo.wav"
        # 100 ms: dos bloques de 40 ms y uno de 20 ms, con canales distinguibles.
        sf.write(ruta, np.column_stack([np.full(1600, 0.25), np.full(1600, -0.5)]), 16000)

        async def avanzar(segundos):
            self.reloj.t += segundos
            await asyncio.sleep(0)

        self.servidor.dormir = avanzar
        original = MotorFalso.procesar_bloque

        def procesar(motor, *args):
            # Simula que el primer ASR consume 10 ms antes de entrar al segundo.
            self.reloj.t += 0.01
            return original(motor, *args)

        with patch.dict("servidor.EJEMPLOS", {"SC-WA-CODE-01": ruta}), \
                patch.object(MotorFalso, "procesar_bloque", procesar):
            async with connect(self.url + "/panel") as panel:
                await panel.send(self.inicio("SC-WA-CODE-01"))
                await self.evento(panel, "inicio")
                fin = await self.evento(panel, "fin")
        m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
        for canal in m["canales"].values():
            self.assertEqual(canal["inicio_s"], 0.0)
            self.assertEqual(canal["duracion_s"], 0.1)
            self.assertEqual(canal["desfase_llegada_s"]["n"], 3)
            self.assertEqual(canal["desfase_llegada_s"]["max"], 0.0)
        guardado, hz = sf.read(Path(fin["dir"]) / "estereo.wav")
        self.assertEqual(guardado.shape, (1600, 2))
        self.assertEqual(hz, 16000)
        # El formato guardado conserva su contrato: protegida izquierda, otra derecha.
        np.testing.assert_allclose(guardado[:, 0], -0.5, atol=0.0001)
        np.testing.assert_allclose(guardado[:, 1], 0.25, atol=0.0001)

    async def test_control_invalido_no_abre_y_panel_sigue_disponible(self):
        async with connect(self.url + "/panel") as panel:
            for mensaje in ('{"tipo":"iniciar"}', '[]', '{',
                            '{"tipo":"iniciar","modo":"llamada","fuentes":{"otra":{"tipo":[]},"protegida":{"tipo":"cliente"}}}'):
                await panel.send(mensaje)
                error = await self.evento(panel, "error")
                self.assertTrue(error["mensaje"])
            self.assertEqual(list(self.dir.iterdir()), [])
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")

    async def test_terminar_interrumpe_ejemplo_y_guarda_solo_audio_recibido(self):
        ruta = self.dir / "ejemplo.wav"
        sf.write(ruta, np.full((16000, 2), 0.25), 16000)
        esperando = asyncio.Event()
        bloqueada = asyncio.Event()
        bloques = 0

        async def avanzar(segundos):
            nonlocal bloques
            bloques += 1
            if bloques > 1:
                esperando.set()
                await bloqueada.wait()
            self.reloj.t += segundos
            await asyncio.sleep(0)

        self.servidor.dormir = avanzar
        with patch.dict("servidor.EJEMPLOS", {"SC-WA-CODE-01": ruta}):
            async with connect(self.url + "/panel") as panel:
                await panel.send(self.inicio("SC-WA-CODE-01"))
                await self.evento(panel, "inicio")
                await asyncio.wait_for(esperando.wait(), 3)
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")
                audio, hz = sf.read(Path(fin["dir"]) / "estereo.wav")
                self.assertEqual(audio.shape, (640, 2))
                self.assertEqual(hz, 16000)
                await panel.send(self.inicio())
                nuevo = await self.evento(panel, "inicio")
                self.assertNotEqual(nuevo["llamada_id"], fin["llamada_id"])

    async def test_desconectar_ultimo_cliente_sin_bloques_cierra_inicio_panel(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            async with connect(self.url + "/audio?rol=otra"):
                pass
            fin = await self.evento(panel, "fin")
            m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
            self.assertEqual(m["canales"], {})

    async def test_cliente_durante_precarga_no_se_mezcla_con_ejemplo(self):
        ruta = self.dir / "ejemplo.wav"
        sf.write(ruta, np.full((3200, 2), 0.25), 16000)
        lista = await self.servidor.preparada
        # Costura del cargador: la siguiente precarga todavía no terminó.
        precarga = asyncio.get_running_loop().create_future()
        self.servidor.preparada = precarga
        with patch.dict("servidor.EJEMPLOS", {"SC-WA-CODE-01": ruta}):
            inicio = asyncio.create_task(self.servidor.iniciar(json.loads(self.inicio("SC-WA-CODE-01"))))
            await asyncio.sleep(0)
            async with connect(self.url + "/audio?rol=otra") as audio:
                await audio.send(np.full(640, -2000, dtype="int16").tobytes())
                precarga.set_result(lista)
                await inicio
                await asyncio.wait_for(audio.wait_closed(), 3)
                self.assertEqual(audio.close_code, 1008)
