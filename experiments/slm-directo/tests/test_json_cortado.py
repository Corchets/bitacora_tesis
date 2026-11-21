"""v4-corte (#143, decisión del 2026-11-07): el JSON de v4 cortado después de `alerta_sugerida`, con la
segunda consulta de motivo y evidencia solo en la línea del aviso. Contra un Ollama falso; no necesita modelo.
TestOtrosPromptsCortados: lo mismo con `v4-premisa-corte` y `c-json-corte` (etapa 2 de #143).

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_json_cortado -v
"""

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

import casos  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (  # noqa: E402
    CORTE_DE,
    ESQUEMA_MOTIVO,
    ESQUEMA_SALIDA,
    MAXIMO_TOKENS_CORTE,
    MAXIMO_TOKENS_RESPUESTA,
    PROMPTS,
    PROMPTS_CORTE,
    DetectorSLM,
    DetectorSLMJSONCortado,
    cargar_pregunta,
    cargar_prompt,
    cargar_prompt_motivo,
    PROMPT_MOTIVO_CORTE,
    esquema_de,
    huella,
    leer_json_cortado,
    usa_roles,
)

CASOS = "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01"
# Palabra en la transcripción → (riesgo como lo escribe el modelo, alerta). Lo demás: 0.1 y false.
SALIDAS = {
    "Decime el código": ("0.9", "true"),
    "RIESGO_SIN_ALERTA": ("0.5", "false"),
    "ALERTA_SIN_RIESGO": ("0.3", "true"),
    "JUSTO": ("0.4", "false"),
    "CERO": ("0", "false"),
}


def json_v4(riesgo: str, alerta: str) -> str:
    """El JSON de v4 como lo escribe Gemma 4 (con saltos y sangría), con motivo y evidencia vacíos."""
    return f'{{\n  "riesgo": {riesgo},\n  "alerta_sugerida": {alerta},\n  "motivo": "",\n  "evidencia": ""\n}}'


def cortado(riesgo: str, alerta: str) -> str:
    """Lo que queda con num_predict: hasta el valor de la alerta y un token de más (la coma)."""
    texto = json_v4(riesgo, alerta)
    return texto[:texto.index(f": {alerta}") + len(alerta) + 3]


class OllamaCorte(BaseHTTPRequestHandler):
    pedidos: list[dict] = []
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
        propiedades = pedido["format"].get("properties", {})
        if "ok" in propiedades:  # calentamiento de correr.py
            self._responder({"message": {"content": json.dumps({"ok": True})}, "eval_count": 3})
            return
        OllamaCorte.pedidos.append(pedido)
        if pedido["format"] == ESQUEMA_MOTIVO:
            contenido = "roto" if OllamaCorte.etapa2_rota else json.dumps(
                {"evidencia": "Decime el código de activación", "motivo": "Te piden el código del SMS"})
            self._responder({"message": {"content": contenido}, "done_reason": "stop",
                             "prompt_eval_count": 40, "eval_count": 30})
            return
        transcripcion = pedido["messages"][1]["content"]
        riesgo, alerta = "0.1", "false"
        for palabra, salida in SALIDAS.items():
            if palabra in transcripcion:
                riesgo, alerta = salida
        contenido = cortado(riesgo, alerta)
        if pedido["options"]["num_predict"] != MAXIMO_TOKENS_CORTE:  # v4 JSON completo
            motivo = ("Te piden el código", "Decime el código") if alerta == "true" else ("", "")
            contenido = json.dumps({"riesgo": float(riesgo), "alerta_sugerida": alerta == "true",
                                    "motivo": motivo[0], "evidencia": motivo[1]}, ensure_ascii=False, indent=2)
            self._responder({"message": {"content": contenido}, "done_reason": "stop", "prompt_eval_count": 300,
                             "eval_count": 41, "total_duration": 9_000_000})
            return
        if "CORTO" in transcripcion:  # el corte llegó antes del valor de la alerta
            contenido = contenido[:contenido.index('"alerta_sugerida"') + 9]
        self._responder({"message": {"content": contenido}, "done_reason": "length", "prompt_eval_count": 300,
                         "eval_count": pedido["options"]["num_predict"], "total_duration": 7_000_000})


class _ConServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaCorte)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"
        cls.cliente = ClienteOllama(cls.url, timeout_s=5)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        OllamaCorte.pedidos.clear()
        OllamaCorte.etapa2_rota = False

    def detector(self) -> DetectorSLMJSONCortado:
        return DetectorSLMJSONCortado(self.cliente, "modelo-falso:1b", cargar_prompt("v4-corte"), "rol",
                                      esquema=esquema_de("v4-corte"))


def roles(*textos: str) -> tuple[Linea, ...]:
    return tuple(Linea("OTRA" if i % 2 == 0 else "PROTEGIDA", t) for i, t in enumerate(textos))


class TestLeerJsonCortado(unittest.TestCase):
    def test_lee_riesgo_y_alerta_del_texto_cortado(self):
        texto = cortado("0.3", "false")
        self.assertEqual(texto, '{\n  "riesgo": 0.3,\n  "alerta_sugerida": false,')
        riesgo, alerta, fin, error = leer_json_cortado(texto)
        self.assertEqual((riesgo, alerta, error), (0.3, False, ""))
        self.assertEqual(texto[:fin], '{\n  "riesgo": 0.3,\n  "alerta_sugerida": false')
        self.assertEqual(leer_json_cortado(cortado("0.8", "true"))[:2], (0.8, True))

    def test_tolera_riesgo_sin_decimal_y_con_dos(self):
        self.assertEqual(leer_json_cortado(cortado("0", "false"))[:2], (0.0, False))
        self.assertEqual(leer_json_cortado(cortado("1", "true"))[:2], (1.0, True))
        self.assertEqual(leer_json_cortado(cortado("1.0", "true"))[:2], (1.0, True))
        self.assertEqual(leer_json_cortado(cortado("0.35", "false"))[:2], (0.35, False))

    def test_el_json_entero_tambien_se_lee(self):
        self.assertEqual(leer_json_cortado(json_v4("0.6", "true"))[:2], (0.6, True))
        self.assertEqual(leer_json_cortado('{"riesgo":0.2,"alerta_sugerida":false}')[:2], (0.2, False))

    def test_si_el_corte_llega_antes_de_la_alerta_es_fallo_con_el_riesgo(self):
        for texto in ('{\n  "riesgo": 0.5,\n  "alerta_sug', '{\n  "riesgo": 0.5,\n  "alerta_sugerida": fals',
                      '{\n  "riesgo": 0.5,'):
            self.assertEqual(leer_json_cortado(texto), (0.5, None, None, "sin_alerta"), texto)

    def test_sin_riesgo_o_fuera_de_rango(self):
        self.assertEqual(leer_json_cortado('{\n  "riesgo": 0.'), (None, None, None, "sin_riesgo"))
        self.assertEqual(leer_json_cortado(""), (None, None, None, "sin_riesgo"))
        self.assertEqual(leer_json_cortado(cortado("1.5", "true"))[3], "riesgo_fuera_de_rango")
        self.assertEqual(leer_json_cortado(cortado("-0.1", "true"))[3], "riesgo_fuera_de_rango")


class TestPrimeraConsulta(_ConServidor):
    def test_mismo_pedido_que_v4_salvo_num_predict(self):
        self.detector().evaluar(roles("Hola, ¿qué tal?", "Bien"))
        (pedido,) = OllamaCorte.pedidos
        mensajes_v4, _ = DetectorSLM(self.cliente, "m", cargar_prompt("v4"), "rol").mensajes(roles("Hola, ¿qué tal?", "Bien"))
        self.assertEqual(pedido["messages"], mensajes_v4)
        self.assertEqual(cargar_prompt("v4-corte"), cargar_prompt("v4"))
        self.assertEqual(pedido["format"], ESQUEMA_SALIDA)
        self.assertNotIn("think", pedido, "como en la línea base v4 JSON, no se envía")
        self.assertNotIn("logprobs", pedido, "sin logprobs: la latencia se compara con v4 JSON")
        self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096,
                                             "num_predict": MAXIMO_TOKENS_CORTE})

    def test_sin_aviso_hay_una_sola_consulta(self):
        r = self.detector().evaluar(roles("Hola, ¿qué tal?"))
        self.assertEqual(len(OllamaCorte.pedidos), 1)
        self.assertTrue(r.valida, r.error)
        self.assertEqual((r.riesgo, r.alerta_escrita, r.alerta_sugerida), (0.1, False, False))
        self.assertEqual((r.motivo, r.evidencia, r.crudo_etapa2), ("", "", ""))
        self.assertEqual(r.tokens_salida, MAXIMO_TOKENS_CORTE)
        self.assertEqual(r.ms, r.ms_etapa1)
        self.assertIsNone(r.ms_etapa2)
        self.assertEqual(r.runtime_ns, 7_000_000)

    def test_riesgo_cero_sin_decimal(self):
        r = self.detector().evaluar(roles("CERO"))
        self.assertTrue(r.valida, r.error)
        self.assertEqual((r.riesgo, r.alerta_sugerida), (0.0, False))

    def test_el_corte_antes_de_la_alerta_es_fallo_sin_segunda_consulta(self):
        r = self.detector().evaluar(roles("RIESGO_SIN_ALERTA CORTO"))
        self.assertFalse(r.valida)
        self.assertEqual((r.error, r.riesgo), ("sin_alerta", 0.5))
        self.assertEqual(len(OllamaCorte.pedidos), 1)


class TestSegundaConsulta(_ConServidor):
    def test_riesgo_alto_con_alerta_false_pide_motivo_sin_repetir_el_json(self):
        r = self.detector().evaluar(roles("RIESGO_SIN_ALERTA"))
        self.assertEqual(len(OllamaCorte.pedidos), 2)
        p1, p2 = OllamaCorte.pedidos
        self.assertEqual(p2["format"], ESQUEMA_MOTIVO)
        self.assertEqual(p2["messages"][:2], p1["messages"], "empieza igual que la primera: reutiliza el prefijo")
        self.assertEqual(p2["messages"][2], {"role": "assistant",
                                             "content": '{\n  "riesgo": 0.5,\n  "alerta_sugerida": false\n}'})
        self.assertEqual(p2["messages"][3], {"role": "user", "content": cargar_prompt_motivo(PROMPT_MOTIVO_CORTE)})
        self.assertEqual(len(p2["messages"]), 4)
        self.assertEqual(p2["options"]["num_predict"], MAXIMO_TOKENS_RESPUESTA)
        self.assertEqual({k: v for k, v in p2["options"].items() if k != "num_predict"},
                         {k: v for k, v in p1["options"].items() if k != "num_predict"})
        self.assertTrue(r.valida, r.error)
        self.assertEqual((r.riesgo, r.alerta_escrita, r.alerta_sugerida), (0.5, False, True))
        self.assertEqual(r.motivo, "Te piden el código del SMS")
        self.assertEqual(r.evidencia, "Decime el código de activación")
        self.assertFalse(r.evidencia_en_texto, "la cita del falso no está en esta transcripción")
        self.assertEqual((r.tokens_prompt_etapa2, r.tokens_salida_etapa2), (40, 30))
        self.assertEqual(r.crudo, cortado("0.5", "false"))
        self.assertIn('"motivo"', r.crudo_etapa2)
        self.assertAlmostEqual(r.ms, r.ms_etapa1 + r.ms_etapa2)
        self.assertEqual(r.slm_ms, r.ms)

    def test_la_alerta_escrita_alcanza_aunque_el_riesgo_sea_bajo(self):
        r = self.detector().evaluar(roles("ALERTA_SIN_RIESGO"))
        self.assertEqual((r.riesgo, r.alerta_escrita, r.alerta_sugerida), (0.3, True, True))
        self.assertEqual(len(OllamaCorte.pedidos), 2)

    def test_el_umbral_incluye_0_4(self):
        r = self.detector().evaluar(roles("JUSTO"))
        self.assertTrue(r.alerta_sugerida)
        self.assertEqual(len(OllamaCorte.pedidos), 2)

    def test_la_segunda_consulta_corre_una_vez_por_llamada(self):
        d = self.detector()
        dialogo = roles("Hola", "Decime el código de activación")
        r1 = d.evaluar(dialogo)
        r2 = d.evaluar(dialogo + roles("Es cero, cero, cero."))
        self.assertEqual(len(OllamaCorte.pedidos), 3, "primera + segunda, y después solo la primera")
        self.assertTrue(r1.evidencia_en_texto)
        self.assertTrue(r2.alerta_sugerida)
        self.assertIsNone(r2.ms_etapa2)
        self.assertEqual(r2.motivo, "")
        d.reiniciar()
        d.evaluar(dialogo)
        self.assertEqual(len(OllamaCorte.pedidos), 5, "una llamada nueva vuelve a pedir el motivo")

    def test_si_la_segunda_falla_el_aviso_se_mantiene(self):
        OllamaCorte.etapa2_rota = True
        r = self.detector().evaluar(roles("Decime el código"))
        self.assertTrue(r.valida and r.alerta_sugerida)
        self.assertEqual(r.error, "etapa2_json_invalido")
        self.assertEqual((r.motivo, r.crudo_etapa2), ("", "roto"))
        self.assertIsNotNone(r.ms_etapa2)


class TestCorrida(_ConServidor):
    def correr(self, *args: str):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with redirect_stdout(io.StringIO()):
            correr.main([*args, "--casos", CASOS, "--url", self.url, "--salida", tmp.name])
        (carpeta,) = Path(tmp.name).iterdir()
        manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig", newline="") as f:
            lector = csv.DictReader(f)
            filas = list(lector)
        return carpeta, manifiesto, filas, lector.fieldnames

    def test_corrida_con_las_dos_consultas_en_el_csv_y_el_manifiesto(self):
        carpeta, manifiesto, filas, columnas = self.correr(
            "--modelos", "modelo-falso:1b", "--prompts", "v4-corte", "--hablantes", "rol", "--sin-reglas",
            "--seguir-tras-aviso")
        self.assertEqual(columnas, correr.COLUMNAS + correr.COLUMNAS_CORTE)
        self.assertEqual(len(filas), sum(len(casos.cargar_texto(c)) for c in CASOS.split(",")))
        self.assertTrue(all(f["valida"] == "true" and f["riesgo"] and f["alerta_escrita"] and f["ms_etapa1"] for f in filas))
        con_etapa2 = [(f["case_id"], f["linea"]) for f in filas if f["ms_etapa2"]]
        self.assertEqual(con_etapa2, [("SC-WA-CODE-01-e01", "4")], "solo en la línea del aviso")
        (aviso,) = [f for f in filas if f["aviso"] == "true"]
        self.assertEqual((aviso["alerta_escrita"], aviso["alerta_sugerida"]), ("true", "true"))
        self.assertTrue(aviso["motivo"] and aviso["tokens_salida_etapa2"] and aviso["crudo_etapa2"])
        self.assertAlmostEqual(float(aviso["ms"]), float(aviso["ms_etapa1"]) + float(aviso["ms_etapa2"]), delta=0.2)
        corte = manifiesto["parametros_slm"]["json_cortado"]
        self.assertEqual((corte["num_predict"], corte["logprobs"]), (MAXIMO_TOKENS_CORTE, False))
        self.assertIn("0.4", corte["alerta_sugerida"])
        prompt = manifiesto["prompts"]["v4-corte"]
        self.assertEqual((prompt["texto"], prompt["esquema"]), (cargar_prompt("v4"), ESQUEMA_SALIDA))
        self.assertEqual((prompt["etapa2"]["texto"], prompt["etapa2"]["esquema"]), (cargar_prompt_motivo(PROMPT_MOTIVO_CORTE), ESQUEMA_MOTIVO))
        resumen.armar_resumen(carpeta)

    def test_en_modo_operativo_la_llamada_termina_en_el_aviso(self):
        _, _, filas, _ = self.correr("--modelos", "modelo-falso:1b", "--prompts", "v4-corte", "--hablantes", "rol",
                                     "--sin-reglas")
        self.assertEqual([f["linea"] for f in filas if f["case_id"] == "SC-WA-CODE-01-e01"], ["1", "2", "3", "4"])

    def test_v4_sin_corte_no_cambia_de_columnas(self):
        _, manifiesto, _, columnas = self.correr("--modelos", "modelo-falso:1b", "--prompts", "v4", "--hablantes",
                                                 "rol", "--sin-reglas")
        self.assertEqual(columnas, correr.COLUMNAS)
        self.assertNotIn("json_cortado", manifiesto["parametros_slm"])

    def test_el_analisis_compara_las_dos_corridas(self):
        import importlib.util
        from contextlib import redirect_stdout
        ruta = Path(__file__).resolve().parents[1] / "corridas" / "2026-11-07_json-cortado" / "analizar.py"
        spec = importlib.util.spec_from_file_location("analizar_json_cortado", ruta)
        analizar = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(analizar)
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida:
            for carpeta, prompt in (("v4-corte", "v4-corte"), ("v4", "v4")):
                (Path(tmp) / carpeta).mkdir()
                correr.main(["--modelos", "modelo-falso:1b", "--prompts", prompt, "--hablantes", "rol", "--sin-reglas",
                             "--seguir-tras-aviso", "--casos", CASOS, "--url", self.url, "--salida", str(Path(tmp) / carpeta)])
            salida.truncate(0)
            analizar.main(["--datos", tmp])
        texto = salida.getvalue()
        self.assertIn("Sin problemas.", texto)
        total = sum(len(casos.cargar_texto(c)) for c in CASOS.split(","))
        self.assertIn(f"| {total} | {total} | {total} | {total} | {total} (100.0%) | {total} (100.0%) | 0 {{}} | 0 {{}} |", texto)
        self.assertIn("riesgo igual en ≥ 93% de las líneas válidas en las dos: SÍ", texto)
        self.assertIn("El corte no cambia la primera consulta.", texto)
        self.assertIn("**Segunda consulta** (motivo y evidencia), en 1 líneas de aviso", texto)
        self.assertIn("Misma línea de aviso en 2 de 2 casos.", texto)

    def test_filtro_tito_no_se_combina_con_el_corte(self):
        for prompt in sorted(PROMPTS_CORTE):
            with self.subTest(prompt), redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as salida:
                correr.main(["--modelos", "modelo-falso:1b", "--prompts", prompt, "--hablantes", "rol",
                             "--filtro-tito", "--casos", CASOS, "--url", self.url])
            self.assertIn(prompt, str(salida.exception))


class TestOtrosPromptsCortados(_ConServidor):
    """Etapa 2 de #143 (Mateo, 2026-11-07): el corte vale para todos los prompts JSON con ESQUEMA_SALIDA."""

    NUEVOS = {"v4-premisa-corte": "v4-premisa", "c-json-corte": "c-json"}

    def detector(self, prompt: str) -> DetectorSLMJSONCortado:
        return DetectorSLMJSONCortado(self.cliente, "modelo-falso:1b", cargar_prompt(prompt), "rol",
                                      esquema=esquema_de(prompt))

    def test_cada_corte_es_su_prompt_base_tal_cual(self):
        self.assertEqual(CORTE_DE, {"v4-corte": "v4", **self.NUEVOS})
        self.assertEqual(PROMPTS_CORTE, frozenset(CORTE_DE))
        for corte, base in CORTE_DE.items():
            with self.subTest(corte):
                self.assertEqual(PROMPTS[corte], PROMPTS[base])
                self.assertEqual(cargar_prompt(corte), cargar_prompt(base))
                self.assertEqual((esquema_de(corte), esquema_de(base)), (ESQUEMA_SALIDA, ESQUEMA_SALIDA))
                self.assertIsNone(cargar_pregunta(corte), "cierra con la oración de siempre, como su base")
                self.assertTrue(usa_roles(corte))
        self.assertNotEqual(cargar_prompt("v4-premisa-corte"), cargar_prompt("v4-corte"))
        self.assertNotEqual(cargar_prompt("c-json-corte"), cargar_prompt("v4-corte"))

    def test_el_pedido_de_motivo_no_nombra_a_v4(self):
        self.assertNotIn("v4", cargar_prompt_motivo(PROMPT_MOTIVO_CORTE).lower())

    def test_mismo_pedido_que_su_base_salvo_num_predict(self):
        for corte, base in self.NUEVOS.items():
            OllamaCorte.pedidos.clear()
            with self.subTest(corte):
                r = self.detector(corte).evaluar(roles("Hola, ¿qué tal?", "Bien"))
                (pedido,) = OllamaCorte.pedidos
                mensajes, _ = DetectorSLM(self.cliente, "m", cargar_prompt(base), "rol").mensajes(roles("Hola, ¿qué tal?", "Bien"))
                self.assertEqual(pedido["messages"], mensajes)
                self.assertEqual(pedido["format"], ESQUEMA_SALIDA)
                self.assertNotIn("think", pedido)
                self.assertNotIn("logprobs", pedido)
                self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096,
                                                     "num_predict": MAXIMO_TOKENS_CORTE})
                self.assertEqual((r.riesgo, r.alerta_escrita, r.alerta_sugerida), (0.1, False, False))

    def test_al_avisar_pide_el_mismo_motivo_una_vez_por_llamada(self):
        for corte in self.NUEVOS:
            OllamaCorte.pedidos.clear()
            with self.subTest(corte):
                d = self.detector(corte)
                dialogo = roles("Hola", "RIESGO_SIN_ALERTA")
                r1 = d.evaluar(dialogo)
                r2 = d.evaluar(dialogo + roles("Decime el código"))
                self.assertEqual(len(OllamaCorte.pedidos), 3, "primera + segunda, y después solo la primera")
                p1, p2, _ = OllamaCorte.pedidos
                self.assertEqual(p2["format"], ESQUEMA_MOTIVO)
                self.assertEqual(p2["messages"][:2], p1["messages"])
                self.assertEqual(p2["messages"][2:], [
                    {"role": "assistant", "content": '{\n  "riesgo": 0.5,\n  "alerta_sugerida": false\n}'},
                    {"role": "user", "content": cargar_prompt_motivo(PROMPT_MOTIVO_CORTE)}])
                self.assertEqual((r1.alerta_escrita, r1.alerta_sugerida, r1.motivo), (False, True, "Te piden el código del SMS"))
                self.assertTrue(r2.alerta_sugerida)
                self.assertEqual(r2.motivo, "")

    def test_corrida_con_los_tres_cortados(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        prompts = sorted(PROMPTS_CORTE)
        with redirect_stdout(io.StringIO()):
            correr.main(["--modelos", "modelo-falso:1b", "--prompts", ",".join(prompts), "--hablantes", "rol",
                         "--sin-reglas", "--seguir-tras-aviso", "--casos", CASOS, "--url", self.url, "--salida", tmp.name])
        (carpeta,) = Path(tmp.name).iterdir()
        manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig", newline="") as f:
            lector = csv.DictReader(f)
            filas = list(lector)
        self.assertEqual(lector.fieldnames, correr.COLUMNAS + correr.COLUMNAS_CORTE)
        lineas = sum(len(casos.cargar_texto(c)) for c in CASOS.split(","))
        for prompt in prompts:
            with self.subTest(prompt):
                propias = [f for f in filas if f["config"] == f"slm|modelo-falso:1b|{prompt}|rol"]
                self.assertEqual(len(propias), lineas)
                self.assertTrue(all(f["valida"] == "true" and f["alerta_escrita"] for f in propias))
                self.assertEqual([(f["case_id"], f["linea"]) for f in propias if f["ms_etapa2"]],
                                 [("SC-WA-CODE-01-e01", "4")])
                datos = manifiesto["prompts"][prompt]
                self.assertEqual((datos["texto"], datos["esquema"]), (cargar_prompt(CORTE_DE[prompt]), ESQUEMA_SALIDA))
                self.assertEqual(datos["huella"], huella(cargar_prompt(CORTE_DE[prompt])))
                self.assertEqual(datos["etapa2"]["texto"], cargar_prompt_motivo(PROMPT_MOTIVO_CORTE))
        self.assertEqual(manifiesto["parametros_slm"]["json_cortado"]["num_predict"], MAXIMO_TOKENS_CORTE)
        resumen.armar_resumen(carpeta)


if __name__ == "__main__":
    unittest.main()
