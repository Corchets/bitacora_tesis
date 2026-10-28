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

from test_llamada import Reloj, RespuestaFalsa, pcm
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
                         corte_silencio="auto")
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

    def inicio(self, escenario=None, corte="auto"):
        fuentes = {r: {"tipo": "cliente"} for r in ("otra", "protegida")}
        if escenario:
            fuentes = {r: {"tipo": "ejemplo", "escenario": escenario, "canal": c}
                       for r, c in (("otra", "izq"), ("protegida", "der"))}
        return json.dumps({"tipo": "iniciar", "modo": "llamada", "fuentes": fuentes,
                           "corte_silencio_s": corte, "umbral_rms_silencio": None})

    async def test_ejemplo_ausente_explicita_como_prepararlo_sin_abrir_llamada(self):
        with patch("servidor.EJEMPLOS", {"LG-WA-CONSULTA-01": self.dir / "ausente.wav"}):
            async with connect(self.url + "/panel") as panel:
                await panel.send(self.inicio("LG-WA-CONSULTA-01"))
                error = await self.evento(panel, "error")
        self.assertIn("Falta el audio de ejemplo", error["mensaje"])
        self.assertIn("sintetizar_par.py", error["mensaje"])
        self.assertIsNone(self.servidor.llamada)
        self.assertEqual(list(self.dir.iterdir()), [])

    async def test_inicio_informa_detector_fijo_del_servidor(self):
        from servidor import servir_panel
        resp = servir_panel(None, Namespace(path="/detector"), self.servidor.args)
        self.assertEqual(json.loads(resp.body.decode("utf-8")), {"tipo": "reglas", "modelo": None})
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            inicio = await self.evento(panel, "inicio")
            self.assertEqual(inicio["detector"], {"tipo": "reglas", "modelo": None})
            await panel.send(json.dumps({"tipo": "terminar"}))
            await self.evento(panel, "fin")
            self.servidor.args.detector = "slm"
            self.servidor.args.modelo = "modelo-local-de-prueba"
            resp_slm = servir_panel(None, Namespace(path="/detector"), self.servidor.args)
            self.assertEqual(json.loads(resp_slm.body.decode("utf-8")),
                             {"tipo": "slm", "modelo": "modelo-local-de-prueba"})
            await panel.send(self.inicio())
            inicio = await self.evento(panel, "inicio")
            self.assertEqual(inicio["detector"], {"tipo": "slm", "modelo": "modelo-local-de-prueba"})
            self.servidor.args.detector = "reglas"

    async def test_guia_de_meet_y_whatsapp_se_sirve_desde_el_panel(self):
        from servidor import servir_panel
        resp = servir_panel(None, Namespace(path="/guia"), self.servidor.args)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/html", resp.headers["Content-Type"])
        texto = resp.body.decode("utf-8")
        self.assertIn('<span class="num">Receta 1</span>Meet', texto)
        self.assertIn('<span class="num">Receta 2</span>WhatsApp', texto)
        self.assertIn('<ol class="pasos">', texto)
        self.assertIn("<code>sudo killall coreaudiod</code>", texto)
        self.assertNotIn("**", texto)

    async def test_prueba_asr_dos_cortes_umbral_manifiesto_y_sin_detector(self):
        class MotorSilencio(MotorFalso):
            def inicializar(motor):
                motor.silencio_acum_s = 0.0
                motor.hablo = False

            def procesar_bloque(motor, muestras, inicio, fin):
                from motores import EventoASR
                if float(np.sqrt(np.mean(muestras ** 2))) >= motor.umbral_rms_silencio:
                    motor.hablo = True
                    motor.silencio_acum_s = 0.0
                    return [EventoASR("parcial", 1, "hola", inicio, fin, 0)]
                motor.silencio_acum_s += fin - inicio
                if motor.hablo and motor.silencio_acum_s + 1e-8 >= motor.corte_silencio_s:
                    motor.hablo = False
                    return [EventoASR("final", 1, "Hola.", 0, fin, 0)]
                return []

            def vaciar_final(motor, fin):
                return []

        with patch.object(self.servidor, "crear_motor", side_effect=MotorSilencio):
            async with connect(self.url + "/panel") as panel:
                for corte, umbral in ((0.5, 0.02), (1.2, 0.04)):
                    mensaje = {"tipo": "iniciar", "modo": "asr",
                               "fuentes": {"protegida": {"tipo": "navegador"}},
                               "corte_silencio_s": corte, "umbral_rms_silencio": umbral}
                    await panel.send(json.dumps(mensaje))
                    inicio = await self.evento(panel, "inicio")
                    self.assertEqual(inicio["modo"], "asr")
                    self.reloj.t += 0.1
                    self.servidor.recibir_audio("protegida", pcm(0.1, 0.1))
                    self.assertEqual((await self.evento(panel, "asr"))["entrega"], "parcial")
                    # Ruido bajo el umbral elegido (pero mayor al predeterminado).
                    for _ in range(round(corte / 0.1) - 1):
                        self.reloj.t += 0.1
                        self.servidor.recibir_audio("protegida", pcm(0.1, 0.01))
                    nivel = (await self.evento(panel, "niveles"))["canales"]["protegida"]
                    self.assertAlmostEqual(nivel["silencio_acum_s"], corte - 0.1)
                    self.assertEqual(nivel["corte_silencio_s"], corte)
                    self.assertEqual(nivel["umbral_rms_silencio"], umbral)
                    self.assertFalse(any(m.get("entrega") == "final" for m in self.servidor.historial))
                    self.reloj.t += 0.1
                    self.servidor.recibir_audio("protegida", pcm(0.1, 0.01))
                    final = await self.evento(panel, "asr")
                    self.assertEqual(final["entrega"], "final")
                    self.assertAlmostEqual(final["disponible_s"] - final["fin_voz_s"], corte)
                    nivel = (await self.evento(panel, "niveles"))["canales"]["protegida"]
                    self.assertAlmostEqual(nivel["silencio_acum_s"], corte)
                    await panel.send(json.dumps({"tipo": "terminar"}))
                    fin = await self.evento(panel, "fin")
                    m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
                    self.assertEqual(m["config"]["corte_silencio_s"], corte)
                    self.assertEqual(m["config"]["umbral_rms_silencio"], umbral)
                    self.assertIsNone(m["config"]["detector"])
                    self.assertEqual(m["detector"]["evaluaciones"], 0)
                    self.assertEqual(m["inicio_panel"], mensaje)

    def prueba(self, corte=0.8):
        return {"tipo": "iniciar", "modo": "asr", "fuentes": {"protegida": {"tipo": "navegador"}},
                "corte_silencio_s": corte, "umbral_rms_silencio": 0.005}

    async def terminar(self, panel):
        await panel.send(json.dumps({"tipo": "terminar"}))
        fin = await self.evento(panel, "fin")
        return Path(fin["dir"])

    def manifiesto(self, carpeta):
        return json.loads((carpeta / "manifiesto.json").read_text())

    async def test_terminar_tras_confirmar_audio_conserva_la_cola_y_emite_finales_antes_de_fin(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            async with connect(self.url + "/audio?rol=protegida") as audio:
                completo = np.full(640, 1000, dtype="<i2")
                cola = np.full(123, 2000, dtype="<i2")
                await audio.send(completo.tobytes())
                await audio.send(cola.tobytes())
                await audio.send("fin_audio")
                self.assertEqual(await asyncio.wait_for(audio.recv(), 3), "audio_recibido")
                await panel.send(json.dumps({"tipo": "terminar"}))
                mensajes = []
                async with asyncio.timeout(3):
                    while True:
                        m = json.loads(await panel.recv())
                        mensajes.append(m)
                        if m["tipo"] == "fin":
                            carpeta = Path(m["dir"])
                            break
            self.assertTrue(any(m["tipo"] == "asr" and m["entrega"] == "final" for m in mensajes[:-1]))
            muestras, hz = sf.read(carpeta / "estereo.wav", dtype="int16", always_2d=True)
            self.assertEqual(hz, 16000)
            np.testing.assert_array_equal(muestras[:, 0], np.concatenate([completo, cola]))

    async def test_prueba_cierra_sin_guardar_y_se_descarta_al_iniciar_otra(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            llamada = await self.terminar(panel)
            self.assertNotIn("guardada", self.manifiesto(llamada))
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            primera = await self.terminar(panel)
            self.assertIs(self.manifiesto(primera)["guardada"], False)
            await panel.send(json.dumps(self.prueba(1.2)))
            await self.evento(panel, "inicio")
            self.assertFalse(primera.exists())
            segunda = await self.terminar(panel)
            self.assertTrue(segunda.exists())
            # Las llamadas nunca se eliminan solas.
            self.assertTrue(llamada.exists())

    async def test_guardar_prueba_persiste_con_referencia_y_sobrevive_a_otra_prueba(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            carpeta = await self.terminar(panel)
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": "  hola, esto es una prueba  "}))
            guardada = await self.evento(panel, "prueba_guardada")
            self.assertEqual(guardada["dir"], str(carpeta))
            m = self.manifiesto(carpeta)
            self.assertIs(m["guardada"], True)
            self.assertEqual(m["referencia"], "hola, esto es una prueba")
            self.assertEqual(m["inicio_panel"]["modo"], "asr")
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            self.assertTrue(carpeta.exists())
            await self.terminar(panel)

    async def test_referencias_por_frase_se_validan_guardan_consultan_y_editan(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            self.reloj.t += 3
            self.servidor.recibir_audio("protegida", pcm(3))
            carpeta = await self.terminar(panel)
            for referencias in ({"1": "falta otra"}, {"1": "a", "9": "ajena"},
                                {"1": 8, "2": "b"}, {"1": "x" * 2001, "2": "b"}, []):
                await panel.send(json.dumps({"tipo": "guardar_prueba", "referencias_por_segmento": referencias}))
                await self.evento(panel, "error")
                self.assertIs(self.manifiesto(carpeta)["guardada"], False)
            referencias = {"2": " Segunda frase. ", "1": " Primera frase. "}
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencias_por_segmento": referencias}))
            guardada = await self.evento(panel, "prueba_guardada")
            self.assertEqual(guardada["referencia"], "Primera frase.\nSegunda frase.")
            self.assertEqual(self.manifiesto(carpeta)["referencias_por_segmento"],
                             {"1": "Primera frase.", "2": "Segunda frase."})
            await panel.send(json.dumps({"tipo": "ver", "id": carpeta.name}))
            detalle = await self.evento(panel, "detalle")
            self.assertEqual(detalle["item"]["referencias_por_segmento"], guardada["referencias_por_segmento"])
            self.assertEqual([l["segmento"] for l in detalle["conversacion"]], [1, 2])
            nuevas = {"1": "Primera corregida.", "2": ""}
            await panel.send(json.dumps({"tipo": "referencia", "id": carpeta.name, "referencias_por_segmento": nuevas}))
            editada = await self.evento(panel, "referencia_guardada")
            self.assertEqual(editada["item"]["referencias_por_segmento"], nuevas)
            self.assertEqual(self.manifiesto(carpeta)["referencia"], "Primera corregida.\n")

    async def test_guardar_prueba_sin_referencia_la_deja_vacia(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            carpeta = await self.terminar(panel)
            await panel.send(json.dumps({"tipo": "guardar_prueba"}))
            await self.evento(panel, "prueba_guardada")
            self.assertEqual(self.manifiesto(carpeta)["referencia"], "")

    async def test_guardar_prueba_invalido(self):
        async with connect(self.url + "/panel") as panel:
            # Nada para guardar todavía.
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": ""}))
            await self.evento(panel, "error")
            # Una llamada no es una prueba.
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            await self.terminar(panel)
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": ""}))
            await self.evento(panel, "error")
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            # Todavía en curso: hay que terminarla antes.
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": ""}))
            await self.evento(panel, "error")
            carpeta = await self.terminar(panel)
            for referencia in (5, None, ["a"], "x" * 2001):
                await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": referencia}))
                await self.evento(panel, "error")
            self.assertIs(self.manifiesto(carpeta)["guardada"], False)
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": "ok"}))
            await self.evento(panel, "prueba_guardada")
            # Ya guardada: no se vuelve a guardar desde acá.
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": "otra"}))
            await self.evento(panel, "error")
            self.assertEqual(self.manifiesto(carpeta)["referencia"], "ok")

    async def test_borrar_durante_la_prueba_reinicia_sin_cortar_el_audio_ni_abrir_llamada_por_defecto(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(self.prueba(1.2)))
            primera = await self.evento(panel, "inicio")
            async with connect(self.url + "/audio?rol=protegida") as micro:
                self.reloj.t += 0.5
                await micro.send(pcm(0.5))
                self.assertEqual((await self.evento(panel, "asr"))["entrega"], "parcial")
                carpeta_vieja = next(self.dir.iterdir())
                # El audio llega pegado al pedido de Borrar: tiene que caer en la prueba nueva.
                await panel.send(json.dumps({"tipo": "reiniciar_prueba"}))
                self.reloj.t += 0.5
                await micro.send(pcm(0.5))
                nueva = await self.evento(panel, "inicio")
                self.assertNotEqual(nueva["llamada_id"], primera["llamada_id"])
                self.assertEqual((nueva["modo"], nueva["corte_silencio_s"]), ("asr", 1.2))
                self.assertEqual((await self.evento(panel, "asr"))["llamada_id"], nueva["llamada_id"])
                self.assertFalse(carpeta_vieja.exists())
                self.assertEqual(len(list(self.dir.iterdir())), 1)
                self.assertFalse(micro.close_code)
                carpeta = await self.terminar(panel)
            m = self.manifiesto(carpeta)
            self.assertEqual(m["llamada_id"], nueva["llamada_id"])
            self.assertEqual(m["inicio_panel"]["modo"], "asr")
            self.assertEqual(m["config"]["corte_silencio_s"], 1.2)
            self.assertEqual(m["canales"]["protegida"]["duracion_s"], 0.5)
            self.assertEqual(len(list(self.dir.iterdir())), 1)

    async def test_borrar_solo_vale_durante_una_prueba(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps({"tipo": "reiniciar_prueba"}))
            await self.evento(panel, "error")
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            await panel.send(json.dumps({"tipo": "reiniciar_prueba"}))
            await self.evento(panel, "error")
            await self.terminar(panel)
            self.assertEqual(len(list(self.dir.iterdir())), 1)

    async def test_borrar_repetido_deja_una_sola_carpeta_y_niveles_vigentes(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            for _ in range(3):
                await panel.send(json.dumps({"tipo": "reiniciar_prueba"}))
                await self.evento(panel, "inicio")
            self.assertEqual(len(list(self.dir.iterdir())), 1)
            nivel = (await self.evento(panel, "niveles"))["canales"]["protegida"]
            self.assertEqual(nivel["fin_audio_s"], None)
            await self.terminar(panel)

    async def responder(self, panel, mensaje, tipo):
        await panel.send(json.dumps(mensaje))
        return await self.evento(panel, tipo)

    async def test_historial_por_websocket_lista_detalle_y_edita_la_referencia(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            llamada = await self.terminar(panel)
            await panel.send(json.dumps(self.prueba(1.2)))
            await self.evento(panel, "inicio")
            await self.terminar(panel)
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": "hola"}))
            guardada = await self.evento(panel, "prueba_guardada")
            prueba = Path(guardada["dir"])
            # Una prueba sin guardar no aparece.
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            await self.terminar(panel)

            lista = await self.responder(panel, {"tipo": "historial"}, "historial")
            self.assertEqual([i["id"] for i in lista["llamadas"]], [llamada.name])
            self.assertEqual([i["id"] for i in lista["pruebas"]], [prueba.name])
            self.assertEqual(lista["llamadas"][0]["corte_silencio_s"], "auto")
            self.assertEqual(lista["pruebas"][0]["referencia"], "hola")

            det = await self.responder(panel, {"tipo": "ver", "id": llamada.name}, "detalle")
            self.assertEqual(det["item"]["id"], llamada.name)
            self.assertIn("conversacion", det)

            nueva = await self.responder(panel, {"tipo": "referencia", "id": prueba.name, "referencia": "chau"},
                                         "referencia_guardada")
            self.assertEqual(nueva["item"]["referencia"], "chau")
            self.assertEqual(self.manifiesto(prueba)["referencia"], "chau")

            for malo in ({"tipo": "ver", "id": "../x"}, {"tipo": "ver", "id": 5}, {"tipo": "ver"},
                         {"tipo": "ver", "id": "2026-10-26_000000-000000"},
                         {"tipo": "referencia", "id": llamada.name, "referencia": "x"},
                         {"tipo": "referencia", "id": prueba.name, "referencia": 5}):
                await panel.send(json.dumps(malo))
                await self.evento(panel, "error")

    async def test_historial_no_lista_la_llamada_en_curso_y_sobrevive_al_reinicio(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            lista = await self.responder(panel, {"tipo": "historial"}, "historial")
            self.assertEqual(lista, {"tipo": "historial", "llamadas": [], "pruebas": []})
            await self.terminar(panel)
        # Un servidor nuevo sobre la misma carpeta de salida ve lo anterior.
        args = Namespace(salida=self.tmp.name, disparo="final", detector="reglas", hilos=2, corte_silencio="auto")
        otro = ServidorFalso(args, DetectorFalso(), ahora=self.reloj)
        red = await serve(otro.atender, "127.0.0.1", 0)
        try:
            async with connect(f"ws://127.0.0.1:{red.sockets[0].getsockname()[1]}/panel") as panel:
                lista = await self.responder(panel, {"tipo": "historial"}, "historial")
                self.assertEqual(len(lista["llamadas"]), 1)
        finally:
            red.close()
            await red.wait_closed()

    async def test_historial_responde_solo_a_quien_pregunta(self):
        async with connect(self.url + "/panel") as uno, connect(self.url + "/panel") as otro:
            await uno.send(json.dumps({"tipo": "historial"}))
            await self.evento(uno, "historial")
            await otro.send(self.inicio())
            await self.evento(otro, "inicio")
            visto = []
            try:
                async with asyncio.timeout(0.3):
                    while True:
                        visto.append(json.loads(await uno.recv())["tipo"])
            except TimeoutError:
                pass
            self.assertNotIn("historial", visto)
            await otro.send(json.dumps({"tipo": "terminar"}))
            await self.evento(otro, "fin")

    async def preparar_historial(self, panel):
        """Una llamada y dos pruebas guardadas; devuelve sus carpetas."""
        await panel.send(self.inicio())
        await self.evento(panel, "inicio")
        llamada = await self.terminar(panel)
        pruebas = []
        for referencia in ("uno", "dos"):
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            pruebas.append(await self.terminar(panel))
            await panel.send(json.dumps({"tipo": "guardar_prueba", "referencia": referencia}))
            await self.evento(panel, "prueba_guardada")
        return llamada, pruebas

    async def test_borrar_uno_o_varios_elimina_las_carpetas_y_avisa_a_todos_los_paneles(self):
        async with connect(self.url + "/panel") as panel, connect(self.url + "/panel") as espectador:
            llamada, (p1, p2) = await self.preparar_historial(panel)
            await panel.send(json.dumps({"tipo": "borrar", "ids": [p1.name]}))
            for quien in (panel, espectador):
                aviso = await self.evento(quien, "borrado")
                self.assertEqual(aviso["ids"], [p1.name])
            self.assertFalse(p1.exists())
            await panel.send(json.dumps({"tipo": "borrar", "ids": [llamada.name, p2.name]}))
            self.assertEqual((await self.evento(espectador, "borrado"))["ids"], [llamada.name, p2.name])
            self.assertEqual(list(self.dir.iterdir()), [])

    async def test_borrar_todas_las_pruebas_no_toca_las_llamadas(self):
        async with connect(self.url + "/panel") as panel:
            llamada, (p1, p2) = await self.preparar_historial(panel)
            await panel.send(json.dumps(self.prueba()))
            await self.evento(panel, "inicio")
            sin_guardar = await self.terminar(panel)
            aviso = await self.responder(panel, {"tipo": "borrar_pruebas"}, "borrado")
            self.assertEqual(sorted(aviso["ids"]), [p1.name, p2.name])
            self.assertTrue(llamada.exists())
            self.assertTrue(sin_guardar.exists())
            self.assertFalse(p1.exists() or p2.exists())
            # Sin pruebas guardadas no hay nada que borrar, y no es un error.
            self.assertEqual((await self.responder(panel, {"tipo": "borrar_pruebas"}, "borrado"))["ids"], [])

    async def test_borrar_rechaza_ids_invalidos_sin_borrar_nada(self):
        async with connect(self.url + "/panel") as panel:
            llamada, (p1, p2) = await self.preparar_historial(panel)
            for malo in ({"tipo": "borrar"}, {"tipo": "borrar", "ids": []}, {"tipo": "borrar", "ids": "x"},
                         {"tipo": "borrar", "ids": [p1.name, "../x"]}, {"tipo": "borrar", "ids": [p1.name, 5]},
                         {"tipo": "borrar", "ids": [p1.name, "2026-10-26_000000-000000"]},
                         {"tipo": "borrar", "ids": [".."]}):
                await panel.send(json.dumps(malo))
                await self.evento(panel, "error")
            self.assertTrue(all(d.exists() for d in (llamada, p1, p2)))

    async def test_no_se_borra_durante_una_llamada_ni_una_prueba(self):
        async with connect(self.url + "/panel") as panel:
            llamada, (p1, p2) = await self.preparar_historial(panel)
            for mensaje in (self.inicio(), json.dumps(self.prueba())):
                await panel.send(mensaje)
                await self.evento(panel, "inicio")
                for borrar in ({"tipo": "borrar", "ids": [llamada.name]}, {"tipo": "borrar_pruebas"}):
                    await panel.send(json.dumps(borrar))
                    self.assertIn("en curso", (await self.evento(panel, "error"))["mensaje"])
                self.assertTrue(all(d.exists() for d in (llamada, p1, p2)))
                await self.terminar(panel)

    async def test_corte_valido_en_llamada_y_prueba_y_manifiesto_conserva_lo_elegido(self):
        async with connect(self.url + "/panel") as panel:
            for modo, corte in (("llamada", "auto"), ("llamada", 0.1), ("llamada", 3.0), ("llamada", 1),
                                ("asr", "auto"), ("asr", 0.1), ("asr", 3.0), ("asr", 0.8)):
                if modo == "llamada":
                    mensaje = json.loads(self.inicio(corte=corte))
                else:
                    mensaje = {"tipo": "iniciar", "modo": "asr", "fuentes": {"protegida": {"tipo": "navegador"}},
                               "corte_silencio_s": corte, "umbral_rms_silencio": 0.005}
                await panel.send(json.dumps(mensaje))
                inicio = await self.evento(panel, "inicio")
                self.assertEqual(inicio["corte_silencio_s"], corte)
                nivel = (await self.evento(panel, "niveles"))["canales"]
                # El panel dibuja la barra de silencio contra el corte numérico del motor.
                esperado = 0.8 if corte == "auto" else corte
                self.assertTrue(all(c["corte_silencio_s"] == esperado for c in nivel.values()))
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")
                m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
                self.assertEqual(m["config"]["corte_silencio_s"], corte)
                self.assertEqual(m["config"]["endpoint_nativo"], corte == "auto")
                self.assertEqual(m["inicio_panel"], mensaje)

    async def test_corte_invalido_se_rechaza_sin_abrir_carpeta(self):
        llamada = json.loads(self.inicio())
        prueba = {"tipo": "iniciar", "modo": "asr", "fuentes": {"protegida": {"tipo": "navegador"}},
                  "corte_silencio_s": 1.2, "umbral_rms_silencio": 0.03}
        async with connect(self.url + "/panel") as panel:
            for base in (llamada, prueba):
                for corte in (0, 0.0, 0.05, 3.1, 0.15, 1.25, -1, True, False, "0.5", "Auto", "", None, [], {},
                              float("nan"), float("inf")):
                    await panel.send(json.dumps({**base, "corte_silencio_s": corte}))
                    error = await self.evento(panel, "error")
                    self.assertIn("corte", error["mensaje"].lower())
                mensaje = dict(base)
                del mensaje["corte_silencio_s"]
                await panel.send(json.dumps(mensaje))
                await self.evento(panel, "error")
            for campo, valor in (("umbral_rms_silencio", 0), ("umbral_rms_silencio", True),
                                 ("umbral_rms_silencio", float("nan")), ("umbral_rms_silencio", "0.01")):
                await panel.send(json.dumps({**prueba, campo: valor}))
                await self.evento(panel, "error")
            # En la llamada el umbral queda fijo.
            await panel.send(json.dumps({**llamada, "umbral_rms_silencio": 0.01}))
            await self.evento(panel, "error")
            self.assertEqual(list(self.dir.iterdir()), [])

    async def test_modelo_de_asr_elegido_en_el_panel(self):
        async with connect(self.url + "/panel") as panel:
            for asr in ("whisper-turbo", "", None, 3):
                await panel.send(json.dumps({**json.loads(self.inicio()), "asr": asr}))
                self.assertIn("modelo de asr", (await self.evento(panel, "error"))["mensaje"].lower())
            self.assertEqual(list(self.dir.iterdir()), [])
            await panel.send(json.dumps({**json.loads(self.inicio()), "asr": "parakeet"}))
            self.assertEqual((await self.evento(panel, "inicio"))["asr"], "parakeet")
            await panel.send(json.dumps({"tipo": "terminar"}))
            fin = await self.evento(panel, "fin")
            m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
            self.assertEqual(m["config"]["asr"], "parakeet")
            # Sin «asr» en el mensaje se mantiene el último elegido.
            await panel.send(self.inicio())
            self.assertEqual((await self.evento(panel, "inicio"))["asr"], "parakeet")

    async def test_llamada_vuelve_al_umbral_fijo_despues_de_una_prueba(self):
        prueba = {"tipo": "iniciar", "modo": "asr", "fuentes": {"protegida": {"tipo": "navegador"}},
                  "corte_silencio_s": 1.2, "umbral_rms_silencio": 0.03}
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(prueba))
            await self.evento(panel, "inicio")
            async with connect(self.url + "/audio?rol=otra") as otra:
                await asyncio.wait_for(otra.wait_closed(), 3)
                self.assertEqual(otra.close_code, 1008)
            await panel.send(json.dumps({"tipo": "terminar"}))
            await self.evento(panel, "fin")
            await panel.send(self.inicio())
            inicio = await self.evento(panel, "inicio")
            self.assertEqual(inicio["corte_silencio_s"], "auto")
            self.assertEqual(inicio["umbral_rms_silencio"], 0.005)
            nivel = (await self.evento(panel, "niveles"))["canales"]
            self.assertTrue(all(c["umbral_rms_silencio"] == 0.005 for c in nivel.values()))
            await panel.send(json.dumps({"tipo": "terminar"}))
            fin = await self.evento(panel, "fin")
            m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
            self.assertEqual(m["config"]["umbral_rms_silencio"], 0.005)
            self.assertTrue(m["config"]["endpoint_nativo"])

    async def test_reintentar_tras_fallo_transitorio_de_precarga_con_otro_corte(self):
        mensaje = {"tipo": "iniciar", "modo": "asr", "fuentes": {"protegida": {"tipo": "navegador"}},
                   "corte_silencio_s": 0.5, "umbral_rms_silencio": 0.02}
        async with connect(self.url + "/panel") as panel:
            with patch.object(self.servidor, "crear_motor", side_effect=RuntimeError("carga transitoria")):
                await panel.send(json.dumps(mensaje))
                self.assertIn("carga transitoria", (await self.evento(panel, "error"))["mensaje"])
            await panel.send(json.dumps({**mensaje, "corte_silencio_s": 1.2}))
            inicio = await self.evento(panel, "inicio")
            self.assertEqual(inicio["corte_silencio_s"], 1.2)
            await panel.send(json.dumps({"tipo": "terminar"}))
            await self.evento(panel, "fin")

    async def test_cliente_directo_usa_el_corte_de_la_linea_de_comandos(self):
        async with connect(self.url + "/panel") as panel:
            for opcion, esperado in (("auto", "auto"), (1.2, 1.2)):
                self.servidor.args.corte_silencio = opcion
                async with connect(self.url + "/audio?rol=protegida") as audio:
                    await audio.send(pcm(0.1))
                    inicio = await self.evento(panel, "inicio")
                    self.assertEqual(inicio["modo"], "llamada")
                    self.assertEqual(inicio["corte_silencio_s"], esperado)
                await self.evento(panel, "fin")

    def test_opcion_de_linea_de_comandos_acepta_auto_o_un_corte_valido(self):
        from servidor import corte_de_linea_de_comandos
        import argparse
        self.assertEqual(corte_de_linea_de_comandos("auto"), "auto")
        self.assertEqual(corte_de_linea_de_comandos("0.1"), 0.1)
        self.assertEqual(corte_de_linea_de_comandos("3"), 3.0)
        for malo in ("0", "3.1", "0.15", "rapido", "nan"):
            with self.assertRaises(argparse.ArgumentTypeError):
                corte_de_linea_de_comandos(malo)

    async def test_asr_conserva_tipo_y_entrega_en_vivo_y_al_cerrar(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            # MotorFalso entrega un parcial a 0,5 s y vacía lo restante al cerrar.
            self.reloj.t += 0.5
            self.servidor.recibir_audio("protegida", pcm(0.5))
            parcial = await self.evento(panel, "asr")
            self.assertEqual((parcial["tipo"], parcial["entrega"], parcial["rol"]),
                             ("asr", "parcial", "protegida"))
            await panel.send(json.dumps({"tipo": "terminar"}))
            mensajes = []
            while True:
                m = json.loads(await panel.recv())
                if m["tipo"] == "fin":
                    break
                if "texto" in m:
                    mensajes.append(m)
            self.assertEqual([m["tipo"] for m in mensajes], ["asr"] * 4)
            self.assertEqual([m["entrega"] for m in mensajes],
                             ["parcial", "final", "parcial", "final"])

    async def test_niveles_agrupados_por_rol_efimeros_y_sin_audio_obsoleto(self):
        async with connect(self.url + "/panel") as panel:
            await panel.send(self.inicio())
            await self.evento(panel, "inicio")
            for otra, protegida in ((0.25, 0.0), (0.0, 0.5)):
                self.reloj.t += 0.1
                self.servidor.recibir_audio("otra", pcm(0.1, otra))
                self.servidor.recibir_audio("protegida", pcm(0.1, protegida))
                niveles = await self.evento(panel, "niveles")
                self.assertEqual(set(niveles["canales"]), {"otra", "protegida"})
                self.assertAlmostEqual(niveles["canales"]["otra"]["rms"], otra, places=4)
                self.assertAlmostEqual(niveles["canales"]["protegida"]["rms"], protegida, places=4)
                self.assertEqual(niveles["canales"]["otra"]["fin_audio_s"],
                                 niveles["canales"]["protegida"]["fin_audio_s"])
            # Un canal deja de mandar: no mostrar su último volumen indefinidamente.
            self.reloj.t += 0.3
            niveles = await self.evento(panel, "niveles")
            self.assertTrue(all(c["rms"] == 0 for c in niveles["canales"].values()))
            await panel.send(json.dumps({"tipo": "terminar"}))
            fin = await self.evento(panel, "fin")
            for nombre in ("actualizaciones.jsonl", "manifiesto.json"):
                contenido = (Path(fin["dir"]) / nombre).read_text()
                self.assertNotIn('"niveles"', contenido)
                self.assertNotIn('"rms"', contenido)
        # Al reconectar se repone la charla, nunca una cola de volúmenes viejos.
        async with connect(self.url + "/panel") as panel:
            while True:
                m = json.loads(await panel.recv())
                self.assertNotEqual(m["tipo"], "niveles")
                if m["tipo"] == "fin":
                    break

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

    async def test_microfono_y_ejemplo_un_canal_admite_solo_audio_del_otro_rol(self):
        ruta = self.dir / "ejemplo.wav"
        sf.write(ruta, np.column_stack([np.full(16000, 0.25), np.full(16000, -0.5)]), 16000)
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
        mensaje = json.loads(self.inicio("SC-WA-CODE-01"))
        mensaje["fuentes"]["protegida"] = {"tipo": "navegador"}
        with patch.dict("servidor.EJEMPLOS", {"SC-WA-CODE-01": ruta}):
            async with connect(self.url + "/panel") as panel:
                await panel.send(json.dumps(mensaje))
                await self.evento(panel, "inicio")
                await asyncio.wait_for(esperando.wait(), 3)
                async with connect(self.url + "/audio?rol=otra") as ajeno:
                    await asyncio.wait_for(ajeno.wait_closed(), 3)
                    self.assertEqual(ajeno.close_code, 1008)
                async with connect(self.url + "/audio?rol=protegida") as micro:
                    await micro.send(np.full(8000, 8192, dtype="int16").tobytes())
                    parcial = await self.evento(panel, "asr")
                    self.assertEqual(parcial["rol"], "protegida")
                    await panel.send(json.dumps({"tipo": "terminar"}))
                    fin = await self.evento(panel, "fin")
                    await asyncio.wait_for(micro.wait_closed(), 3)
                m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
                self.assertEqual(m["inicio_panel"], mensaje)
                self.assertEqual(m["canales"]["otra"]["duracion_s"], 0.04)
                self.assertEqual(m["canales"]["protegida"]["duracion_s"], 0.5)
                guardado, _ = sf.read(Path(fin["dir"]) / "estereo.wav")
                np.testing.assert_allclose(guardado[:8000, 0], 0.25, atol=0.0001)

    async def test_dos_fuentes_navegador_conservan_canales_y_desfase(self):
        mensaje = json.loads(self.inicio())
        mensaje["fuentes"] = {r: {"tipo": "navegador"} for r in ("protegida", "otra")}
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(mensaje))
            respuesta = json.loads(await panel.recv())
            self.assertEqual(respuesta["tipo"], "inicio", respuesta)
            async with connect(self.url + "/audio?rol=protegida") as micro, \
                    connect(self.url + "/audio?rol=otra") as otra:
                self.reloj.t += 0.5
                await micro.send(pcm(0.5, 0.25))
                self.assertEqual((await self.evento(panel, "asr"))["rol"], "protegida")
                self.reloj.t += 0.12
                await otra.send(pcm(0.5, -0.5))
                self.assertEqual((await self.evento(panel, "asr"))["rol"], "otra")
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")
            m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
            self.assertEqual(m["inicio_panel"], mensaje)
            for rol in ("protegida", "otra"):
                self.assertEqual(m["canales"][rol]["duracion_s"], 0.5)
                self.assertLessEqual(m["canales"][rol]["desfase_llegada_s"]["max"], 0.3)
            self.assertEqual(m["canales"]["protegida"]["inicio_s"], 0.0)
            self.assertEqual(m["canales"]["otra"]["inicio_s"], 0.12)
            guardado, _ = sf.read(Path(fin["dir"]) / "estereo.wav")
            np.testing.assert_allclose(guardado[:8000, 0], 0.25, atol=0.0001)
            np.testing.assert_allclose(guardado[1920:9920, 1], -0.5, atol=0.0001)

    async def test_microfono_y_cliente_comparten_entrada_y_roles(self):
        mensaje = json.loads(self.inicio())
        mensaje["fuentes"]["protegida"] = {"tipo": "navegador"}
        async with connect(self.url + "/panel") as panel:
            await panel.send(json.dumps(mensaje))
            await self.evento(panel, "inicio")
            async with connect(self.url + "/audio?rol=otra") as otra, \
                    connect(self.url + "/audio?rol=protegida") as micro:
                for rol, audio in (("otra", otra), ("protegida", micro)):
                    await audio.send(pcm(0.5))
                    parcial = await self.evento(panel, "asr")
                    self.assertEqual(parcial["rol"], rol)
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")
            m = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
            self.assertEqual(set(m["canales"]), {"otra", "protegida"})

    async def test_aviso_unico_en_panel_con_motivo_evidencia_y_ta(self):
        respuestas = [
            RespuestaFalsa(riesgo=0.0, alerta_sugerida=False, motivo="Saludo inicial"),
            RespuestaFalsa(
                riesgo=1.0,
                alerta_sugerida=True,
                motivo="Pedido de código de activación",
                evidencia=". decime el código de activación que recibiste por sms",
            ),
        ]
        llamadas_detector = []

        class DetectorGuionado:
            def evaluar(self, foto):
                llamadas_detector.append([(l.hablante, l.texto) for l in foto])
                return respuestas[min(len(llamadas_detector) - 1, len(respuestas) - 1)]

        eventos_otra = [
            {"tiempo_audio_s": 0.4, "tipo": "final", "segmento": 1, "texto": "Te llamo de soporte."},
            {"tiempo_audio_s": 0.8, "tipo": "final", "segmento": 2, "texto": ". decime el código de activación que recibiste por sms"},
            {"tiempo_audio_s": 1.2, "tipo": "final", "segmento": 3, "texto": "Pasámelo rápido."},
        ]
        motores = [[], eventos_otra]
        self.servidor.detector = DetectorGuionado()
        with patch.object(self.servidor, "crear_motor", side_effect=lambda: MotorFalso(motores.pop(0) if motores else [])):
            self.servidor.preparar()
            await self.servidor.preparada
            async with connect(self.url + "/panel") as panel:
                await panel.send(self.inicio())
                await self.evento(panel, "inicio")

                def avanzar_bloque_otra():
                    for _ in range(4):
                        self.reloj.t += 0.1
                        self.servidor.recibir_audio("otra", pcm(0.1))

                avanzar_bloque_otra()
                ev1 = await self.evento(panel, "detector")
                self.assertFalse(ev1["aviso"])
                self.assertEqual(ev1["riesgo"], 0.0)

                avanzar_bloque_otra()
                ev2 = await self.evento(panel, "detector")
                self.assertTrue(ev2["aviso"])
                self.assertEqual(ev2["motivo"], "Pedido de código de activación")
                self.assertIn("decime el código de activación", ev2["evidencia"])
                self.assertIsNotNone(ev2["t_a"])
                self.assertIsNotNone(ev2["fin_voz_s"])

                # Frase posterior al aviso: se transcribe pero el detector no vuelve a evaluar ni avisar.
                avanzar_bloque_otra()
                asr_post = await self.evento(panel, "asr")
                self.assertEqual(asr_post["entrega"], "final")
                await panel.send(json.dumps({"tipo": "terminar"}))
                fin = await self.evento(panel, "fin")

        self.assertEqual(len(llamadas_detector), 2)
        det_eventos = [m for m in self.servidor.historial if m.get("tipo") == "detector"]
        self.assertEqual([m["aviso"] for m in det_eventos], [False, True])
        manifiesto = json.loads((Path(fin["dir"]) / "manifiesto.json").read_text())
        self.assertEqual(manifiesto["detector"]["aviso"]["t_a"], ev2["t_a"])
