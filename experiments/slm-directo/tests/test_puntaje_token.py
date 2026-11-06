"""Puntaje por probabilidad del token «SÍ» (#143), sin modelo real.

Uso (desde experiments/slm-directo):
    python -m unittest tests.test_puntaje_token -v

Cubre la lectura de logprobs (variantes de tokenización, masa SÍ+NO, respuestas sin
logprobs), el pedido que llega a Ollama, las columnas nuevas del CSV y que las
corridas con los prompts de antes no cambien. Usa el Ollama falso de test_ensayo.
"""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import casos  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (  # noqa: E402
    DIR_PROMPTS,
    PROMPTS_SINO,
    DetectorSLM,
    DetectorSLMSiNo,
    armar_mensaje_usuario,
    cargar_prompt,
    esquema_de,
    leer_si_no,
    usa_roles,
)
from test_ensayo import DIALOGO, OllamaFalso  # noqa: E402

CASOS = "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01"
PREGUNTA = "Con lo disponible hasta ahora, ¿corresponde marcar la alerta según estas reglas? Respondé solo SÍ o NO."


def _top(*pares: tuple[str, float]) -> list[dict]:
    """[(token, probabilidad)] → formato de Ollama: [{token, logprob, bytes}]."""
    return [{"token": t, "logprob": math.log(p), "bytes": list(t.encode("utf-8"))} for t, p in pares]


def _logprobs(*pares: tuple[str, float]) -> list[dict]:
    """Campo `logprobs` de /api/chat con num_predict 1: un elemento, el token elegido y sus alternativas."""
    top = _top(*pares)
    return [{**top[0], "top_logprobs": top}]


class OllamaLogprobs(OllamaFalso):
    """El Ollama falso de test_ensayo, más pedidos con `logprobs` (#143).

    Sin `logprobs` en el pedido, responde exactamente como OllamaFalso.
    """

    sin_logprobs = False  # imita un Ollama anterior a 0.12.11, que ignora el campo

    def do_POST(self):
        datos = self.rfile.read(int(self.headers["Content-Length"]))
        pedido = json.loads(datos)
        if "logprobs" not in pedido:
            self.rfile = io.BytesIO(datos)  # OllamaFalso vuelve a leer el cuerpo
            return super().do_POST()
        OllamaFalso.pedidos.append(pedido)
        if "Decime el código" in pedido["messages"][-1]["content"]:
            pares = [("SÍ", 0.80), ("Sí", 0.10), ("NO", 0.06), ("**", 0.04)]
        else:
            pares = [("NO", 0.70), ("No", 0.20), ("SÍ", 0.05), ("La", 0.05)]
        respuesta = {
            "message": {"role": "assistant", "content": pares[0][0]},
            "done_reason": "length",
            "prompt_eval_count": 300,
            "eval_count": 1,
            "total_duration": 5_000_000,
        }
        if not OllamaLogprobs.sin_logprobs:
            respuesta["logprobs"] = _logprobs(*pares)
        self._responder(respuesta)


class _ConServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaLogprobs)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"
        cls.cliente = ClienteOllama(cls.url, timeout_s=5)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        OllamaFalso.pedidos.clear()
        OllamaLogprobs.sin_logprobs = False

    def correr(self, *args: str) -> tuple[Path, dict, list[dict], list[str]]:
        """correr.main contra el falso; devuelve carpeta, manifiesto, filas y encabezado."""
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        with redirect_stdout(io.StringIO()):
            correr.main([*args, "--casos", CASOS, "--url", self.url, "--salida", tmp.name])
        (carpeta,) = Path(tmp.name).iterdir()
        manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig", newline="") as f:
            lector = csv.DictReader(f)
            filas = list(lector)
        return carpeta, manifiesto, filas, list(lector.fieldnames)


class TestLeerSiNo(unittest.TestCase):
    def test_suma_las_variantes_de_si_y_de_no(self):
        p_si, masa, top, error = leer_si_no(_logprobs(
            ("SÍ", 0.40), (" Sí", 0.15), ("sí", 0.05), ("SI", 0.04), ("S", 0.03), ("▁Si", 0.02),
            ("NO", 0.15), (" No", 0.05), ("no.", 0.03), ("N", 0.02),
            ("**", 0.03), ("La", 0.03),
        ))
        self.assertEqual(error, "")
        self.assertAlmostEqual(masa, 0.94, places=9)
        self.assertAlmostEqual(p_si, 0.69 / 0.94, places=9)
        self.assertEqual(len(top), 12)
        self.assertEqual(top[0], ["SÍ", round(math.log(0.40), 4)])

    def test_palabras_que_empiezan_con_s_o_n_no_cuentan(self):
        p_si, masa, _, _ = leer_si_no(_logprobs(("Sin", 0.3), ("Según", 0.2), ("Nada", 0.2), ("Sí", 0.2), ("No", 0.1)))
        self.assertAlmostEqual(masa, 0.3, places=9)
        self.assertAlmostEqual(p_si, 0.2 / 0.3, places=9)

    def test_el_token_elegido_no_se_suma_dos_veces(self):
        # Ollama repite el token elegido entre las alternativas: se suman solo las alternativas.
        logprobs = [{"token": "SÍ", "logprob": math.log(0.6), "top_logprobs": _top(("SÍ", 0.6), ("NO", 0.2))}]
        p_si, masa, _, _ = leer_si_no(logprobs)
        self.assertAlmostEqual(masa, 0.8, places=9)
        self.assertAlmostEqual(p_si, 0.75, places=9)

    def test_sin_si_ni_no_es_fallo_con_masa_cero(self):
        p_si, masa, top, error = leer_si_no(_logprobs(("**", 0.6), ("La", 0.3)))
        self.assertIsNone(p_si)
        self.assertEqual((masa, error), (0.0, "sin_si_no"))
        self.assertEqual(len(top), 2, "las alternativas se conservan para revisar el fallo")

    def test_respuestas_sin_logprobs_utilizables(self):
        casos = {
            "sin campo": (None, "sin_logprobs"),
            "lista vacía": ([], "sin_logprobs"),
            "sin alternativas": ([{"token": "SÍ", "logprob": -0.1}], "sin_top_logprobs"),
            "logprob no numérico": ([{"token": "SÍ", "logprob": -0.1, "top_logprobs": [{"token": "SÍ", "logprob": "x"}]}], "logprobs_malformados"),
            "logprob positivo": ([{"token": "SÍ", "logprob": 0.5, "top_logprobs": [{"token": "SÍ", "logprob": 0.5}]}], "logprobs_malformados"),
            "token no texto": ([{"token": "SÍ", "logprob": -0.1, "top_logprobs": [{"token": None, "logprob": -0.1}]}], "logprobs_malformados"),
        }
        for nombre, (logprobs, esperado) in casos.items():
            with self.subTest(nombre):
                p_si, masa, _, error = leer_si_no(logprobs)
                self.assertIsNone(p_si)
                self.assertIsNone(masa)
                self.assertEqual(error, esperado)


class TestPromptsSiNo(unittest.TestCase):
    CORTE = "Respondé solo con un objeto JSON"
    REGLAS = ("Si para explicar el peligro tenés que suponer algo que no se dijo, no alertes. "
              "Que alguien apure, diga ser de una entidad o hable de un problema puede aumentar el riesgo, "
              "pero no alcanza por sí solo para alertar.\n\n")

    def leer(self, nombre: str) -> str:
        return (DIR_PROMPTS / nombre).read_text(encoding="utf-8")

    def test_solo_cambia_la_instruccion_de_salida(self):
        for original, sino in (("tarea.txt", "tarea_sino.txt"), ("tarea_v4.txt", "tarea_v4_sino.txt")):
            with self.subTest(sino):
                cuerpo = self.leer(original).split(self.CORTE)[0]
                self.assertEqual(self.leer(sino), cuerpo + PREGUNTA + "\n")

    def test_v4_sin_reglas_solo_quita_las_dos_reglas(self):
        v4_sino = self.leer("tarea_v4_sino.txt")
        self.assertEqual(v4_sino.count(self.REGLAS), 1)
        self.assertEqual(self.leer("tarea_v4_sin_reglas_sino.txt"), v4_sino.replace(self.REGLAS, ""))

    # A1 y A2 (#143, tabla «Variantes»): la oración que definía alerta_sugerida pasa a
    # «Lo que importa es si,» (sin «solo si»: la restricción queda en la pregunta).
    MARCA = 'Marcá "alerta_sugerida": true solo si,'
    IMPORTA = "Lo que importa es si,"
    PREGUNTA_A1_V4 = "¿OTRA le está pidiendo o induciendo a PROTEGIDA algo de la lista? Respondé solo SÍ o NO."
    PREGUNTA_A1_TAREA = "¿Alguien le está pidiendo o induciendo a la otra persona algo de la lista? Respondé solo SÍ o NO."
    PREGUNTA_A2 = ("Hasta acá, ¿OTRA está intentando estafar a PROTEGIDA, aunque todavía no haya pedido nada? "
                   "Respondé solo SÍ o NO.")

    def cuerpo_a1(self, original: str) -> str:
        cuerpo = self.leer(original).split(self.CORTE)[0]
        self.assertEqual(cuerpo.count(self.MARCA), 1)
        return cuerpo.replace(self.MARCA, self.IMPORTA)

    def test_a1_solo_cambia_la_oracion_de_alerta_sugerida_y_la_pregunta(self):
        for original, a1, pregunta in (("tarea_v4.txt", "tarea_v4_a1.txt", self.PREGUNTA_A1_V4),
                                       ("tarea.txt", "tarea_a1.txt", self.PREGUNTA_A1_TAREA)):
            with self.subTest(a1):
                self.assertEqual(self.leer(a1), self.cuerpo_a1(original) + pregunta + "\n")

    def test_a2_es_a1_sin_las_dos_reglas_y_con_la_pregunta_de_intencion(self):
        cuerpo = self.cuerpo_a1("tarea_v4.txt")
        self.assertEqual(cuerpo.count(self.REGLAS), 1)
        self.assertEqual(self.leer("tarea_v4_a2.txt"), cuerpo.replace(self.REGLAS, "") + self.PREGUNTA_A2 + "\n")

    def test_a1_y_a2_no_nombran_el_campo_ni_la_alerta_en_la_pregunta(self):
        for variante in ("tarea-a1", "v4-a1", "v4-a2"):
            with self.subTest(variante):
                self.assertNotIn("alerta_sugerida", cargar_prompt(variante))
                self.assertNotIn("alerta", cargar_prompt(variante).splitlines()[-1])

    def test_variantes_registradas_sin_esquema(self):
        self.assertEqual(PROMPTS_SINO, {"tarea-sino", "v4-sino", "v4-sin-reglas-sino", "tarea-a1", "v4-a1", "v4-a2"})
        for variante in PROMPTS_SINO:
            with self.subTest(variante):
                self.assertTrue(cargar_prompt(variante).endswith("Respondé solo SÍ o NO."))
                self.assertNotIn("JSON", cargar_prompt(variante))
                self.assertIsNone(esquema_de(variante))
        for variante in ("tarea-sino", "tarea-a1"):
            self.assertFalse(usa_roles(variante))
        for variante in ("v4-sino", "v4-sin-reglas-sino", "v4-a1", "v4-a2"):
            self.assertTrue(usa_roles(variante))


class TestDetectorSiNo(_ConServidor):
    def test_el_pedido_lee_un_token_con_sus_logprobs(self):
        DetectorSLMSiNo(self.cliente, "modelo-falso:1b", cargar_prompt("tarea-sino")).evaluar(DIALOGO[:2])
        (pedido,) = OllamaFalso.pedidos
        self.assertNotIn("format", pedido, "sin esquema: la respuesta es libre")
        self.assertEqual((pedido["logprobs"], pedido["top_logprobs"]), (True, 20))
        self.assertIs(pedido["think"], False)
        self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096, "num_predict": 1})
        self.assertFalse(pedido["stream"])

    def test_solo_cambia_el_mensaje_de_sistema(self):
        """Un cambio por vez: mismo mensaje de usuario que DetectorSLM con los mismos hablantes."""
        for variante, base, h in (("tarea-sino", "tarea", "ab"), ("v4-sino", "v4", "rol"),
                                  ("tarea-a1", "tarea", "ab"), ("v4-a1", "v4", "rol"), ("v4-a2", "v4", "rol")):
            with self.subTest(variante):
                lineas = DIALOGO[:3] if h == "ab" else tuple(Linea("OTRA" if l.hablante == "A" else "PROTEGIDA", l.texto) for l in DIALOGO[:3])
                sino, _ = DetectorSLMSiNo(self.cliente, "m", cargar_prompt(variante), h).mensajes(lineas)
                json_, _ = DetectorSLM(self.cliente, "m", cargar_prompt(base), h).mensajes(lineas)
                self.assertEqual(sino[1], json_[1])
                self.assertEqual(sino[1]["content"], armar_mensaje_usuario(lineas, h))
                self.assertEqual(sino[0]["content"], cargar_prompt(variante))

    def test_respuesta_con_p_si_masa_y_alternativas(self):
        d = DetectorSLMSiNo(self.cliente, "modelo-falso:1b", cargar_prompt("tarea-sino"))
        r = d.evaluar(DIALOGO[:4])  # la línea 4 es el pedido del código
        self.assertTrue(r.valida, r.error)
        self.assertAlmostEqual(r.masa_si_no, 0.96, places=6)
        self.assertAlmostEqual(r.p_si, 0.90 / 0.96, places=6)
        self.assertTrue(r.alerta_sugerida)
        self.assertIsNone(r.riesgo, "el puntaje va en p_si, no en riesgo")
        self.assertEqual(json.loads(r.top_logprobs)[0][0], "SÍ")
        self.assertEqual((r.crudo, r.tokens_prompt, r.tokens_salida, r.runtime_ns), ("SÍ", 300, 1, 5_000_000))
        self.assertIsNotNone(r.ms)
        r1 = d.evaluar(DIALOGO[:1])
        self.assertAlmostEqual(r1.p_si, 0.05 / 0.95, places=6)
        self.assertFalse(r1.alerta_sugerida)

    def test_ollama_sin_logprobs_es_fallo(self):
        OllamaLogprobs.sin_logprobs = True
        r = DetectorSLMSiNo(self.cliente, "modelo-falso:1b", cargar_prompt("tarea-sino")).evaluar(DIALOGO[:1])
        self.assertFalse(r.valida)
        self.assertEqual(r.error, "sin_logprobs")
        self.assertIsNone(r.p_si)

    def test_contexto_excedido_no_llama_al_modelo(self):
        r = DetectorSLMSiNo(self.cliente, "m", cargar_prompt("tarea-sino"), num_ctx=64).evaluar(DIALOGO)
        self.assertFalse(r.valida)
        self.assertTrue(r.error.startswith("contexto_excedido"))
        self.assertEqual(OllamaFalso.pedidos, [])


class TestCorridaSiNo(_ConServidor):
    def test_corrida_completa_con_columnas_nuevas(self):
        carpeta, manifiesto, filas, columnas = self.correr(
            "--modelos", "modelo-falso:1b", "--prompts", "tarea-sino", "--hablantes", "ab",
            "--sin-reglas", "--seguir-tras-aviso", "--seed", "42", "--num-ctx", "4096",
        )
        self.assertEqual(columnas, correr.COLUMNAS + correr.COLUMNAS_SINO)
        total = sum(len(casos.cargar_texto(c)) for c in CASOS.split(","))
        self.assertEqual(len(filas), total, "sigue tras el aviso: todas las líneas de los dos casos")
        self.assertTrue(all(f["valida"] == "true" and f["p_si"] and f["masa_si_no"] and f["top_logprobs"] for f in filas))
        self.assertTrue(all(f["riesgo"] == "" for f in filas))
        codigo = [f for f in filas if f["case_id"] == "SC-WA-CODE-01-e01"]
        self.assertEqual([f["aviso"] for f in codigo], ["false", "false", "false", "true", "false"])
        self.assertAlmostEqual(float(codigo[3]["p_si"]), 0.90 / 0.96, places=5)
        lectura = manifiesto["parametros_slm"]["lectura_token"]
        self.assertEqual((lectura["num_predict"], lectura["top_logprobs"]), (1, 20))
        self.assertEqual(manifiesto["modo_termino"], correr.MODO_DIAGNOSTICO)
        self.assertEqual(manifiesto["modelos"]["modelo-falso:1b"]["logprobs"]["chequeo"], "ok")
        self.assertEqual(manifiesto["prompts"]["tarea-sino"]["texto"], cargar_prompt("tarea-sino"))
        self.assertIsNone(manifiesto["prompts"]["tarea-sino"]["esquema"])
        resumen.armar_resumen(carpeta, con_trayectorias=True)  # el resumen de siempre no se rompe

    def test_ollama_sin_logprobs_corta_antes_de_medir(self):
        OllamaLogprobs.sin_logprobs = True
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            with self.assertRaises(SystemExit) as salida:
                correr.main(["--modelos", "modelo-falso:1b", "--prompts", "tarea-sino", "--sin-reglas",
                             "--casos", CASOS, "--url", self.url, "--salida", tmp])
            (carpeta,) = Path(tmp).iterdir()
            manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        self.assertIn("0.12.11", str(salida.exception))
        self.assertTrue(manifiesto["interrumpida"])
        self.assertIn("error", manifiesto["modelos"]["modelo-falso:1b"])

    def test_filtro_tito_no_se_combina_con_si_no(self):
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as salida:
            correr.main(["--modelos", "modelo-falso:1b", "--prompts", "v4-sino", "--hablantes", "rol",
                         "--filtro-tito", "--casos", CASOS, "--url", self.url])
        self.assertIn("offline", str(salida.exception))


class TestCorridasViejasNoCambian(_ConServidor):
    def test_tarea_conserva_columnas_pedido_y_manifiesto(self):
        _, manifiesto, filas, columnas = self.correr("--modelos", "modelo-falso:1b", "--prompts", "tarea", "--hablantes", "ab")
        self.assertEqual(columnas, correr.COLUMNAS, "sin prompts SÍ/NO el CSV tiene exactamente las columnas de antes")
        self.assertNotIn("lectura_token", manifiesto["parametros_slm"])
        self.assertNotIn("logprobs", manifiesto["modelos"]["modelo-falso:1b"])
        consultas = [p for p in OllamaFalso.pedidos if "ok" not in p["format"].get("properties", {})]
        self.assertTrue(consultas)
        for pedido in consultas:
            self.assertEqual(set(pedido), {"model", "messages", "format", "options", "stream", "keep_alive", "think"})
            self.assertEqual(pedido["format"]["required"], ["riesgo", "alerta_sugerida", "motivo", "evidencia"])
            self.assertEqual(pedido["options"]["num_predict"], 512)
        slm = [f for f in filas if f["detector"] == "slm"]
        self.assertEqual([f["aviso"] for f in slm if f["case_id"] == "SC-WA-CODE-01-e01"], ["false", "false", "false", "true"])
        self.assertTrue(all(f["riesgo"] for f in slm))

    def test_cliente_sin_logprobs_manda_el_mismo_cuerpo(self):
        self.cliente.chat("modelo-falso:1b", [{"role": "user", "content": "x"}], {"type": "object"}, {"temperature": 0})
        (pedido,) = OllamaFalso.pedidos
        self.assertEqual(list(pedido), ["model", "messages", "format", "options", "stream", "keep_alive"])

    def test_corrida_mixta_deja_vacias_las_columnas_nuevas_del_json(self):
        _, _, filas, columnas = self.correr("--modelos", "modelo-falso:1b", "--prompts", "tarea,tarea-sino", "--sin-reglas")
        self.assertEqual(columnas, correr.COLUMNAS + correr.COLUMNAS_SINO)
        json_ = [f for f in filas if f["prompt"] == "tarea"]
        sino = [f for f in filas if f["prompt"] == "tarea-sino"]
        self.assertTrue(json_ and sino)
        self.assertTrue(all(f["p_si"] == f["masa_si_no"] == f["top_logprobs"] == "" for f in json_))
        self.assertTrue(all(f["p_si"] for f in sino))


if __name__ == "__main__":
    unittest.main()
