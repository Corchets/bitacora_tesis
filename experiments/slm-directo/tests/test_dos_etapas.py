"""Tests de «riesgo primero» (DetectorSLMDosEtapas) contra un Ollama falso. No necesitan modelo."""

from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analisis" / "2026-10-29-riesgo-primero"))

import acumular  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (  # noqa: E402
    ESQUEMA_MOTIVO,
    ESQUEMA_RIESGO,
    MAXIMO_TOKENS_RIESGO,
    DetectorSLMDosEtapas,
    cargar_prompt,
    validar_riesgo,
)

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta de WhatsApp."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Decime el código de activación que recibiste por SMS."),
]


class OllamaDosEtapas(BaseHTTPRequestHandler):
    """Etapa 1: riesgo según palabras de la transcripción. Etapa 2: evidencia y motivo."""

    pedidos: list[dict] = []
    riesgo_por_palabra = {"Decime el código": 0.9, "EMPATE": 0.6, "ROMPER": None}
    etapa2_rota = False

    def log_message(self, *args):
        pass

    def _responder(self, cuerpo: dict, codigo: int = 200):
        datos = json.dumps(cuerpo).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(datos)))
        self.end_headers()
        self.wfile.write(datos)

    def do_GET(self):
        respuestas = {
            "/api/version": {"version": "0.0-falso"},
            "/api/tags": {"models": [{"name": "modelo-falso:1b", "digest": "abc123"}]},
            "/api/ps": {"models": [{"name": "modelo-falso:1b", "size": 600 * 1024**2, "size_vram": 0}]},
        }
        self._responder(respuestas.get(self.path, {}), 200 if self.path in respuestas else 404)

    def do_POST(self):
        pedido = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        OllamaDosEtapas.pedidos.append(pedido)
        propiedades = pedido["format"].get("properties", {})
        transcripcion = pedido["messages"][1]["content"] if len(pedido["messages"]) > 1 else ""
        if "ok" in propiedades:  # calentamiento de correr.py
            contenido, tokens = json.dumps({"ok": True}), 3
        elif "motivo" in propiedades:
            contenido = "roto" if OllamaDosEtapas.etapa2_rota else json.dumps(
                {"evidencia": "Decime el código de activación", "motivo": "Te piden el código del SMS"})
            tokens = 30
        else:
            riesgo = 0.1
            for palabra, valor in OllamaDosEtapas.riesgo_por_palabra.items():
                if palabra in transcripcion:
                    riesgo = valor
            contenido, tokens = ("no es json" if riesgo is None else json.dumps({"riesgo": riesgo})), 8
        self._responder({"message": {"role": "assistant", "content": contenido}, "prompt_eval_count": 300, "eval_count": tokens})


class ConServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaDosEtapas)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"
        cls.cliente = ClienteOllama(cls.url, timeout_s=5)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        OllamaDosEtapas.pedidos.clear()
        OllamaDosEtapas.etapa2_rota = False

    def detector(self, **kw) -> DetectorSLMDosEtapas:
        return DetectorSLMDosEtapas(self.cliente, "modelo-falso:1b", cargar_prompt("riesgo"), **kw)


class TestDetectorDosEtapas(ConServidor):
    def test_riesgo_bajo_hace_un_solo_pedido_corto(self):
        r = self.detector().evaluar(DIALOGO[:1])
        self.assertEqual(len(OllamaDosEtapas.pedidos), 1)
        pedido = OllamaDosEtapas.pedidos[0]
        self.assertEqual(pedido["format"], ESQUEMA_RIESGO)
        self.assertEqual(pedido["options"]["num_predict"], MAXIMO_TOKENS_RIESGO)
        self.assertTrue(r.valida)
        self.assertFalse(r.alerta_sugerida)
        self.assertEqual((r.riesgo, r.tokens_salida), (0.1, 8))
        self.assertIsNone(r.ms_etapa2)
        self.assertEqual(r.ms, r.ms_etapa1)

    def test_riesgo_alto_pide_motivo_reutilizando_el_prefijo(self):
        r = self.detector().evaluar(DIALOGO)
        self.assertEqual(len(OllamaDosEtapas.pedidos), 2)
        p1, p2 = OllamaDosEtapas.pedidos
        self.assertEqual(p2["format"], ESQUEMA_MOTIVO)
        self.assertEqual(p2["messages"][:2], p1["messages"], "la etapa 2 empieza igual que la 1")
        self.assertEqual(p2["messages"][2], {"role": "assistant", "content": json.dumps({"riesgo": 0.9})})
        self.assertEqual(p2["messages"][3]["role"], "user")
        self.assertTrue(r.valida and r.alerta_sugerida)
        self.assertEqual(r.motivo, "Te piden el código del SMS")
        self.assertTrue(r.evidencia_en_texto)
        self.assertEqual(r.tokens_salida_etapa2, 30)
        self.assertAlmostEqual(r.ms, r.ms_etapa1 + r.ms_etapa2)

    def test_la_etapa2_corre_una_vez_por_llamada(self):
        d = self.detector()
        r1 = d.evaluar(DIALOGO)
        r2 = d.evaluar(DIALOGO + [Linea("B", "Es cero, cero, cero.")])
        self.assertEqual(len(OllamaDosEtapas.pedidos), 3, "etapa 1 + etapa 2, y después solo etapa 1")
        self.assertIsNotNone(r1.ms_etapa2)
        self.assertTrue(r2.alerta_sugerida)
        self.assertIsNone(r2.ms_etapa2)
        self.assertEqual(r2.motivo, "")
        d.reiniciar()
        d.evaluar(DIALOGO)
        self.assertEqual(len(OllamaDosEtapas.pedidos), 5, "una llamada nueva vuelve a pedir el motivo")

    def test_el_umbral_es_estricto(self):
        r = self.detector(umbral=0.6).evaluar((Linea("A", "EMPATE"),))
        self.assertFalse(r.alerta_sugerida, "0.6 no supera 0.6")
        self.assertEqual(len(OllamaDosEtapas.pedidos), 1)
        r = self.detector(umbral=0.5).evaluar((Linea("A", "EMPATE"),))
        self.assertTrue(r.alerta_sugerida)

    def test_etapa1_invalida_es_fallo(self):
        r = self.detector().evaluar((Linea("A", "ROMPER"),))
        self.assertFalse(r.valida)
        self.assertEqual(r.error, "json_invalido")
        self.assertEqual(len(OllamaDosEtapas.pedidos), 1)

    def test_etapa2_invalida_mantiene_la_alerta(self):
        OllamaDosEtapas.etapa2_rota = True
        r = self.detector().evaluar(DIALOGO)
        self.assertTrue(r.valida and r.alerta_sugerida)
        self.assertEqual(r.error, "etapa2_json_invalido")
        self.assertEqual((r.motivo, r.crudo_etapa2), ("", "roto"))

    def test_validar_riesgo(self):
        self.assertEqual(validar_riesgo('{"riesgo": 0.42}'), (0.42, ""))
        self.assertEqual(validar_riesgo('{"riesgo": 1.5}')[1], "riesgo_fuera_de_rango")
        self.assertEqual(validar_riesgo('{"riesgo": true}')[1], "riesgo_no_numerico")
        self.assertEqual(validar_riesgo('{"otro": 1}')[1], "faltan_campos: riesgo")


class TestCorridaRiesgo(ConServidor):
    def test_corrida_registra_las_dos_etapas_y_el_resumen_funciona(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            correr.main([
                "--modelos", "modelo-falso:1b",
                "--prompts", "riesgo",
                "--sin-reglas",
                "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                "--url", self.url,
                "--salida", tmp,
            ])
            (carpeta,) = Path(tmp).iterdir()
            manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
            with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
                filas = list(csv.DictReader(f))
            texto = resumen.armar_resumen(carpeta)
            analisis = acumular.analizar([carpeta])
        self.assertEqual(manifiesto["parametros_slm"]["umbral_etapa2"], 0.6)
        self.assertIn("motivo", manifiesto["prompts"]["riesgo"]["etapa2"]["esquema"]["properties"])
        con_etapa2 = [f for f in filas if f["ms_etapa2"]]
        self.assertEqual([(f["case_id"], f["linea"]) for f in con_etapa2], [("SC-WA-CODE-01-e01", "4")],
                         "la etapa 2 corre solo en la línea del aviso")
        self.assertTrue(all(f["alerta_sugerida"] == "true" for f in con_etapa2))
        self.assertTrue(all(f["ms_etapa2"] == "" for f in filas if f["case_id"].startswith("LG-")))
        self.assertIn("slm\\|modelo-falso:1b\\|riesgo\\|ab", texto)
        # La estafa pide el código (riesgo 0.9) y la legítima queda en 0.1: umbral > 0.6 da 1/1 y 0/1.
        self.assertRegex(analisis, r"\| umbral > 0\.6 \| 1/1 \(100 %\) \| 0/1 \(0 %\) \| 1 \| \d+ \| ✔ \|")
        self.assertNotIn("alerta del modelo", analisis, "con riesgo no hay alerta_sugerida del modelo")


class TestPoliticasAcumuladas(unittest.TestCase):
    def aviso(self, nombre: str, riesgos: list[float]) -> int | None:
        (f,) = [f for n, f in acumular.politicas(un_paso=False) if n == nombre]
        return f(riesgos, [False] * len(riesgos))

    def test_una_linea_sola_no_alcanza_si_se_acumula(self):
        riesgos = [0.1, 0.7, 0.2, 0.7, 0.8]
        self.assertEqual(self.aviso("umbral > 0.6", riesgos), 2)
        self.assertEqual(self.aviso("2 seguidas > 0.6", riesgos), 5)
        self.assertEqual(self.aviso("media 2 > 0.6", riesgos), 5)

    def test_ema_suma_con_olvido(self):
        self.assertEqual([round(x, 3) for x in acumular._ema([1.0, 1.0, 0.0], 0.5)], [0.5, 0.75, 0.375])
        self.assertEqual(self.aviso("ema 0.5 > 0.6", [0.9, 0.9, 0.9]), 2)


if __name__ == "__main__":
    unittest.main()
