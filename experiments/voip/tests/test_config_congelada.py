"""El panel con la configuración congelada de #143: C cortado tras el riesgo, «riesgo ≥ 0,3», el motivo solo en el
primer aviso y solo OTRA (ADR 0006 y 0007). Sin modelo: contra el Ollama falso de
slm-directo/tests/test_config_congelada_143.py (`OllamaCongelada`), con el MotorFalso y un reloj controlado.

Uso (desde experiments/voip):
    python -m unittest tests.test_config_congelada -v
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import tempfile
import threading
import unittest
from argparse import Namespace
from http.server import HTTPServer
from pathlib import Path
from unittest.mock import patch

DIR_TESTS = Path(__file__).resolve().parent
DIR_VOIP = DIR_TESTS.parent
for _p in (DIR_TESTS, DIR_VOIP):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from llamada import Llamada  # noqa: E402  (agrega las rutas de asr-local, replay y slm-directo)
from servidor import Servidor, parse_args  # noqa: E402
from test_llamada import Reloj, final, pcm, programas  # noqa: E402
import medir  # noqa: E402
import replay  # noqa: E402
from detectores import ESQUEMA_MOTIVO, MAXIMO_TOKENS_CORTE_RIESGO, DetectorSLMCorteRiesgo  # noqa: E402

sys.path.append(str(DIR_VOIP.parent / "slm-directo" / "tests"))
from test_config_congelada_143 import OllamaCongelada  # noqa: E402

PROMPT = "c-premisa-corte-riesgo"  # la configuración congelada desde la prueba de sensibilidad
MODELO = OllamaCongelada.modelo

# OTRA saluda (0,1), PROTEGIDA menciona el soporte y OTRA sigue: con «soporte» en la transcripción el falso escribe
# 0,3 (avisa). Después OTRA pide el código (0,9), ya con el aviso hecho.
PROTEGIDA = [final(2.0, 1, "Sí, ¿es por lo del soporte?")]
OTRA = [final(1.0, 1, "Hola, ¿hablo con Ana?"), final(3.0, 2, "Sí, te llamo por eso."),
        final(4.0, 3, "Decime el código.")]


def ultima_linea(pedido: dict) -> str:
    """La última línea numerada de la transcripción que recibió el modelo."""
    return [l for l in pedido["messages"][1]["content"].splitlines() if re.match(r"\d+\. ", l)][-1]


def args_servidor(*extra: str) -> Namespace:
    with patch("sys.argv", ["servidor.py", *extra]):
        return parse_args()


class TestFlags(unittest.TestCase):
    def rechaza(self, *extra: str) -> None:
        with patch("sys.stderr"), self.assertRaises(SystemExit):
            args_servidor(*extra)

    def test_por_defecto_es_la_configuracion_congelada(self):
        a = args_servidor()
        self.assertEqual((a.detector, a.modelo, a.prompt, a.hablantes, a.disparo, a.solo_otra),
                         ("slm", "gemma4:e2b-it-q4_K_M", PROMPT, "rol", "turno", True))

    def test_la_variante_de_la_prueba_de_sensibilidad_es_un_flag(self):
        for variante in ("c-ancla-corte-riesgo", "c-premisa-corte-riesgo", "c-sin-freno-corte-riesgo"):
            with self.subTest(variante=variante):
                a = args_servidor("--prompt", variante)
                self.assertEqual((a.detector, a.prompt, a.solo_otra), ("slm", variante, True))
        self.rechaza("--prompt", "no-existe")

    def test_reglas_y_tito_siguen_andando_sin_solo_otra(self):
        a = args_servidor("--detector", "reglas")
        self.assertEqual((a.detector, a.solo_otra), ("reglas", False))
        a = args_servidor("--detector", "tito-slm", "--prompt", "v4")
        self.assertEqual((a.detector, a.prompt, a.solo_otra), ("tito-slm", "v4", False))
        a = args_servidor("--prompt", "tarea", "--hablantes", "ab")
        self.assertEqual((a.detector, a.solo_otra), ("slm", False))

    def test_tito_no_admite_el_prompt_cortado(self):
        self.rechaza("--detector", "tito-slm")
        with self.assertRaisesRegex(ValueError, "tito-slm no admite"):
            replay.construir_detector("tito-slm", prompt_nombre=PROMPT)

    def test_solo_otra_requiere_el_slm_y_los_roles(self):
        self.rechaza("--solo-otra", "--detector", "reglas")
        self.rechaza("--solo-otra", "--detector", "tito-slm", "--prompt", "v4")
        self.rechaza("--solo-otra", "--prompt", "tarea", "--hablantes", "ab")
        self.assertFalse(args_servidor("--no-solo-otra").solo_otra)
        with self.assertRaisesRegex(ValueError, "solo OTRA requiere hablantes rol"):
            Llamada(crear_motor=programas([], []), hablantes="ab", solo_otra=True)

    def test_medir_usa_la_misma_configuracion(self):
        a = medir.parse_args([])
        self.assertEqual((a.detector, a.prompt, a.hablantes, a.solo_otra), ("slm", PROMPT, "rol", True))
        self.assertEqual(medir.parse_args(["--prompt", "c-ancla-corte-riesgo"]).prompt, "c-ancla-corte-riesgo")
        self.assertFalse(medir.parse_args(["--detector", "reglas"]).solo_otra)
        with patch("sys.stderr"), self.assertRaises(SystemExit):
            medir.parse_args(["--detector", "tito-slm"])


class _ConOllama(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ollama = HTTPServer(("127.0.0.1", 0), OllamaCongelada)
        threading.Thread(target=cls.ollama.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.ollama.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.ollama.shutdown()
        cls.ollama.server_close()

    def setUp(self):
        OllamaCongelada.pedidos = []
        OllamaCongelada.motivo_roto = False
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.reloj = Reloj()

    def detector(self, prompt: str = PROMPT):
        return replay.construir_detector("slm", modelo=MODELO, prompt_nombre=prompt, hablantes="rol",
                                         ollama_url=self.url)

    def consultas(self) -> list[dict]:
        return [p for p in OllamaCongelada.pedidos if p.get("format") != ESQUEMA_MOTIVO]

    def motivos(self) -> list[dict]:
        return [p for p in OllamaCongelada.pedidos if p.get("format") == ESQUEMA_MOTIVO]


class TestConstruccion(_ConOllama):
    def test_replay_arma_el_detector_cortado_tras_el_riesgo(self):
        d = self.detector()
        self.assertIs(type(d), DetectorSLMCorteRiesgo)
        self.assertEqual((d.umbral, d.opciones()["num_predict"], d.hablantes), (0.3, MAXIMO_TOKENS_CORTE_RIESGO, "rol"))
        self.assertIs(d.pensar, False)  # el calentamiento negoció `think`, como correr.py
        self.assertEqual(d.pedido_motivo, replay.detectores.cargar_prompt_motivo(replay.detectores.PROMPT_MOTIVO_C))

    def test_el_panel_elige_gemma_directo_con_el_prompt_del_servidor(self):
        args = args_servidor("--detector", "reglas", "--ollama-url", self.url, "--salida", self.tmp.name, "--asr", "zipformer")
        servidor = Servidor(args, replay.detectores.DetectorReglas())
        asyncio.run(servidor.configurar_detector(MODELO))
        self.assertIs(type(servidor.detector), DetectorSLMCorteRiesgo)
        self.assertEqual((args.detector, args.modelo, servidor.detector.prompt),
                         ("slm", MODELO, replay.detectores.cargar_prompt(PROMPT)))


class TestLlamadaCongelada(_ConOllama):
    """El ciclo de `Servidor.trabajar_detector`, sincrónico: cada disparo consulta la foto más reciente."""

    def llamar(self, detector, *, disparo: str, solo_otra: bool, segundos: float = 7.0) -> Llamada:
        llamada = Llamada(crear_motor=programas(PROTEGIDA, OTRA), disparo=disparo, hablantes="rol",
                          ahora=self.reloj, solo_otra=solo_otra)
        llamada.abrir("VIVO-TEST", Path(self.tmp.name) / "llamada")
        detector.reiniciar()
        for _ in range(int(segundos * 10)):
            self.reloj.t += 0.1
            t = round(llamada.reloj() + 0.1, 1)  # fin del bloque que llega
            for rol in ("otra", "protegida"):
                # Cada uno habla el medio segundo antes de su frase y después se calla: el silencio cierra el turno.
                habla = any(f["tiempo_audio_s"] - 0.5 < t <= f["tiempo_audio_s"] for f in (OTRA if rol == "otra" else PROTEGIDA))
                for act in llamada.recibir(rol, pcm(0.1, 0.1 if habla else 0.0)):
                    llamada.marcar_disparo(act)
            n, foto, disparos = llamada.tomar_foto()
            if llamada.aviso is None and foto and disparos:
                llamada.registrar_evaluacion(n, disparos, detector.evaluar(foto), llamada.reloj(), llamada.reloj())
        llamada.cerrar(guardar_audio=False)
        return llamada

    def test_solo_otra_consulta_en_otra_y_protegida_entra_al_contexto(self):
        llamada = self.llamar(self.detector(), disparo="final", solo_otra=True)
        consultas = self.consultas()
        self.assertEqual(len(consultas), 2, "OTRA 1 y OTRA 2; ni la línea de PROTEGIDA ni la que sigue al aviso")
        self.assertTrue(all(c["options"]["num_predict"] == MAXIMO_TOKENS_CORTE_RIESGO for c in consultas))
        segunda = consultas[1]["messages"][1]["content"]
        self.assertIn("2. PROTEGIDA: Sí, ¿es por lo del soporte?", segunda)
        self.assertEqual(ultima_linea(consultas[1]), "3. OTRA: Sí, te llamo por eso.")
        self.assertNotIn("Decime el código", segunda)
        aviso = llamada.aviso
        self.assertIsNotNone(aviso)
        self.assertEqual((aviso.respuesta.riesgo, aviso.respuesta.motivo),
                         (0.3, "Dice ser de soporte sin que lo hayas pedido"))
        self.assertEqual(len(self.motivos()), 1, "el motivo se pide una vez, en el primer aviso")
        eventos = [json.loads(l) for l in (llamada.dir_salida / "detector.jsonl").read_text().splitlines()]
        self.assertEqual([e["aviso"] for e in eventos], [False, True])
        manifiesto = json.loads((llamada.dir_salida / "manifiesto.json").read_text())
        self.assertTrue(manifiesto["solo_otra"])

    def test_sin_solo_otra_la_linea_de_protegida_consulta_y_avisa(self):
        llamada = self.llamar(self.detector(), disparo="final", solo_otra=False)
        self.assertEqual(len(self.consultas()), 2)
        self.assertEqual(ultima_linea(self.consultas()[1]), "2. PROTEGIDA: Sí, ¿es por lo del soporte?")
        self.assertEqual(llamada.aviso.respuesta.riesgo, 0.3)

    def test_por_turnos_la_consulta_termina_en_la_ultima_linea_de_otra(self):
        llamada = self.llamar(self.detector(), disparo="turno", solo_otra=True, segundos=9.0)
        # El turno de OTRA lo cierra la frase de PROTEGIDA (cambio), pero esa frase espera a la consulta siguiente,
        # que llega al cerrarse el segundo turno de OTRA por silencio.
        self.assertEqual([ultima_linea(c) for c in self.consultas()], ["1. OTRA: Hola, ¿hablo con Ana?",
                                                                       "4. OTRA: Decime el código."])
        self.assertNotIn("PROTEGIDA", self.consultas()[0]["messages"][1]["content"].split("\n\n")[1])
        self.assertIn("2. PROTEGIDA: Sí, ¿es por lo del soporte?", self.consultas()[1]["messages"][1]["content"])
        self.assertEqual([e.n for e in llamada.evaluaciones], [1, 4], "la evaluación se pega a la frase de OTRA")
        self.assertEqual(llamada.aviso.respuesta.riesgo, 0.9)
        self.assertEqual(len(self.motivos()), 1)
        cierres = [(c["rol"], c["motivo"], c["consulta"]) for c in llamada.turnos.cierres]
        self.assertEqual(cierres[:2], [("otra", "cambio", True), ("protegida", "cambio", False)])

    def test_por_turnos_sin_solo_otra_la_frase_que_cierra_el_turno_entra_en_la_consulta(self):
        llamada = self.llamar(self.detector(), disparo="turno", solo_otra=False, segundos=9.0)
        self.assertEqual(ultima_linea(self.consultas()[0]), "2. PROTEGIDA: Sí, ¿es por lo del soporte?")
        self.assertEqual((llamada.aviso.n, llamada.aviso.respuesta.riesgo), (2, 0.3))

    def test_cada_llamada_del_servidor_vuelve_a_pedir_el_motivo(self):
        detector = self.detector()
        args = Namespace(salida=self.tmp.name, disparo="final", detector="slm", hilos=2, corte_silencio="auto",
                         asr="zipformer", hablantes="rol", solo_otra=True, prompt=PROMPT, modelo=MODELO, seed=42,
                         ollama_url=self.url, sin_indicio=True)

        class ServidorFalso(Servidor):
            def crear_motor(self):
                from motores import MotorFalso
                return MotorFalso([])

        async def dos_llamadas():
            servidor = ServidorFalso(args, detector, ahora=self.reloj)
            servidor.preparar()
            for _ in range(2):
                servidor.config_llamada = {"modo": "llamada"}
                servidor.llamada = await servidor.abrir_llamada()
                self.assertTrue(servidor.llamada.solo_otra)
                self.assertFalse(detector._aviso_hecho)
                detector._aviso_hecho = True  # como si la llamada hubiera avisado
                await servidor.cerrar_llamada()
            await servidor.preparada

        asyncio.run(dos_llamadas())


if __name__ == "__main__":
    unittest.main()
