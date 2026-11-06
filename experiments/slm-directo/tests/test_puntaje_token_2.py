"""Segunda vuelta de #143 (2026-11-06): prompt S, pregunta al final y dígito del 0 al 9, sin modelo real.

Uso (desde experiments/slm-directo):
    python -m unittest tests.test_puntaje_token_2 -v

Cubre que S-JSON, S-SÍ/NO y S-dígito compartan el cuerpo, que v4-D sea A1 sin su pregunta,
que la pregunta cierre el mensaje del usuario sin tocar el resto, la lectura del dígito
esperado y las columnas y el manifiesto de una corrida. Usa el Ollama falso de test_puntaje_token.
"""

from __future__ import annotations

import io
import json
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import casos  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import (  # noqa: E402
    CIERRE_POR_DEFECTO,
    DIR_PROMPTS,
    ESQUEMA_SALIDA,
    PROMPTS_DIGITO,
    PROMPTS_SINO,
    PROMPTS_TOKEN,
    DetectorSLM,
    DetectorSLMDigito,
    DetectorSLMLecturaJSON,
    DetectorSLMSiNo,
    armar_mensaje_usuario,
    cargar_pregunta,
    cargar_prompt,
    esquema_de,
    leer_digito,
    leer_riesgo_json,
    usa_roles,
)
from test_ensayo import DIALOGO, OllamaFalso  # noqa: E402
from test_puntaje_token import CASOS, OllamaLogprobs, _ConServidor, _logprobs, _top  # noqa: E402

PREGUNTA_S_SINO = "Con lo dicho hasta la línea {n}, ¿hay que avisarle a PROTEGIDA que puede ser una estafa? Respondé solo SÍ o NO."
PREGUNTA_S_DIGITO = ("Con lo dicho hasta la línea {n}, ¿qué tan probable es que esta llamada sea una estafa? "
                     "Respondé solo con un número del 0 (nada probable) al 9 (casi seguro).")
PREGUNTA_V4_DIGITO = ("Con lo dicho hasta la línea {n}, ¿qué tan riesgosa te parece la llamada? "
                      "Respondé solo con un número del 0 (nada riesgosa) al 9 (máximo riesgo).")
ROLES = tuple(Linea("OTRA" if l.hablante == "A" else "PROTEGIDA", l.texto) for l in DIALOGO)


def leer(nombre: str) -> str:
    return (DIR_PROMPTS / nombre).read_text(encoding="utf-8")


def _json_con_logprobs(alto: bool) -> list[dict]:
    """Logprobs de `{"riesgo": 0.8` (o 0.1): el entero y el primer decimal traen alternativas."""
    pasos = []
    for token in ['{"', "ries", "go", '":', " ", "0", ".", "8" if alto else "1"]:
        if token == "0":
            pares = [("0", 0.95), ("1", 0.05)]
        elif token in ("8", "1"):
            pares = [("8", 0.6), ("9", 0.3), ("7", 0.1)] if alto else [("1", 0.7), ("0", 0.2), ("2", 0.1)]
        else:
            pares = [(token, 1.0)]
        top = _top(*pares)
        pasos.append({**top[0], "top_logprobs": top})
    return pasos


class OllamaDigitos(OllamaLogprobs):
    """Como OllamaLogprobs, pero responde dígitos cuando la pregunta final pide un número y el
    comienzo del JSON con logprobs cuando el pedido trae esquema (v4-L)."""

    def do_POST(self):
        datos = self.rfile.read(int(self.headers["Content-Length"]))
        pedido = json.loads(datos)
        ultimo = pedido["messages"][-1]["content"]
        if "logprobs" in pedido and "format" in pedido:
            OllamaFalso.pedidos.append(pedido)
            pasos = _json_con_logprobs("Decime el código" in ultimo)
            self._responder({"message": {"role": "assistant", "content": "".join(p["token"] for p in pasos)},
                             "done_reason": "length", "prompt_eval_count": 300, "eval_count": len(pasos),
                             "total_duration": 9_000_000, "logprobs": pasos})
            return
        if "logprobs" not in pedido or "un número del 0" not in ultimo:
            self.rfile = io.BytesIO(datos)
            return super().do_POST()
        OllamaFalso.pedidos.append(pedido)
        if "Decime el código" in ultimo:
            pares = [("8", 0.5), (" 9", 0.3), ("7", 0.1), ("**", 0.1)]
        else:
            pares = [("1", 0.6), ("0", 0.2), ("2.", 0.1), ("El", 0.1)]
        self._responder({"message": {"role": "assistant", "content": pares[0][0]}, "done_reason": "length",
                         "prompt_eval_count": 300, "eval_count": 1, "total_duration": 5_000_000,
                         "logprobs": _logprobs(*pares)})


class _ConServidorDigitos(_ConServidor):
    @classmethod
    def setUpClass(cls):
        from http.server import HTTPServer
        import threading
        from cliente_ollama import ClienteOllama

        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaDigitos)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"
        cls.cliente = ClienteOllama(cls.url, timeout_s=5)


class TestPromptsS(unittest.TestCase):
    def test_las_tres_salidas_de_s_comparten_el_cuerpo(self):
        cuerpo = leer("tarea_s.txt").strip()
        self.assertEqual(cargar_prompt("s-sino"), cuerpo)
        self.assertEqual(cargar_prompt("s-digito"), cuerpo)
        self.assertEqual(cargar_prompt("s-json"), cuerpo + "\n\n" + leer("salida_json_s.txt").strip())

    def test_s_json_cambia_solo_riesgo_y_alerta_respecto_de_v4(self):
        salida_v4 = leer("tarea_v4.txt").split("Respondé solo con un objeto JSON")[1].splitlines()
        salida_s = leer("salida_json_s.txt").split("Respondé solo con un objeto JSON")[1].splitlines()
        self.assertEqual(len(salida_v4), len(salida_s))
        distintas = [(v, s) for v, s in zip(salida_v4, salida_s) if v != s]
        self.assertEqual([s.split(":")[0] for _, s in distintas], ['- "riesgo"', '- "alerta_sugerida"'])
        self.assertEqual(esquema_de("s-json"), ESQUEMA_SALIDA)

    def test_s_es_la_opcion_a_sin_lista_de_datos_personales(self):
        cuerpo = cargar_prompt("s-sino")
        self.assertIn("que le pidan su nombre, su DNI, su fecha de nacimiento, una dirección o un correo para "
                      "identificarla, darle un turno, mandarle algo u ofrecerle un servicio;", cuerpo)
        self.assertNotIn("salvo", cuerpo, "la opción (b) no entra")
        self.assertIn("- mandar una foto de su documento o de su cara;", cuerpo)
        for palabra in ("JSON", "alerta", "SÍ o NO", "número del 0"):
            self.assertNotIn(palabra, cuerpo, "la salida no va en el cuerpo común")

    def test_v4_d_es_a1_sin_su_pregunta(self):
        a1 = leer("tarea_v4_a1.txt").rstrip("\n").split("\n")
        self.assertTrue(a1[-1].startswith("¿OTRA le está pidiendo"))
        self.assertEqual(cargar_prompt("v4-digito"), "\n".join(a1[:-1]).strip())

    def test_preguntas_finales(self):
        for variante, pregunta in (("s-sino", PREGUNTA_S_SINO), ("s-digito", PREGUNTA_S_DIGITO),
                                   ("v4-digito", PREGUNTA_V4_DIGITO)):
            with self.subTest(variante):
                self.assertEqual(cargar_pregunta(variante), pregunta)
                self.assertEqual(pregunta.count("{n}"), 1)
        for variante in ("tarea", "v4", "v4-a1", "v4-a2", "tarea-sino", "s-json"):
            with self.subTest(variante):
                self.assertIsNone(cargar_pregunta(variante))
        with self.assertRaises(ValueError):
            cargar_pregunta("no-existe")

    def test_registro(self):
        self.assertEqual(PROMPTS_DIGITO, {"s-digito", "v4-digito", "c-digito"})
        self.assertIn("s-sino", PROMPTS_SINO)
        self.assertEqual(PROMPTS_TOKEN, PROMPTS_SINO | PROMPTS_DIGITO | {"v4-lectura"})
        for variante in ("s-sino", "s-digito", "v4-digito", "c-sino", "c-digito"):
            self.assertIsNone(esquema_de(variante))
        for variante in ("s-json", "s-sino", "s-digito", "v4-digito", "v4-premisa", "c-json", "c-sino", "c-digito"):
            self.assertTrue(usa_roles(variante))
        self.assertEqual(esquema_de("c-json"), ESQUEMA_SALIDA)
        self.assertEqual(esquema_de("v4-premisa"), ESQUEMA_SALIDA)


PREMISA = "Recibió esta llamada de un número que no tiene agendado."


class TestPromptsAlcance(unittest.TestCase):
    """Prompts con el alcance (llamadas entrantes de números no agendados): v4-premisa y C. Se evalúan en la etapa 2,
    con las legítimas entrantes nuevas; en corpus_v2 casi todas las legítimas las inicia la persona."""

    def test_v4_premisa_es_v4_con_una_sola_oracion_mas(self):
        v4, premisa = leer("tarea_v4.txt"), leer("tarea_v4_premisa.txt")
        agregado = "PROTEGIDA recibió esta llamada de un número que no tiene agendado: la llamó OTRA. "
        self.assertEqual(premisa.count(agregado), 1)
        self.assertEqual(premisa.replace(agregado, ""), v4)
        self.assertIsNone(cargar_pregunta("v4-premisa"))

    def test_las_tres_salidas_de_c_comparten_el_cuerpo(self):
        cuerpo = leer("tarea_c.txt").strip()
        self.assertEqual(cargar_prompt("c-sino"), cuerpo)
        self.assertEqual(cargar_prompt("c-digito"), cuerpo)
        self.assertEqual(cargar_prompt("c-json"), cuerpo + "\n\n" + leer("salida_json_c.txt").strip())
        self.assertEqual(cargar_pregunta("c-digito"), cargar_pregunta("s-digito"), "la misma pregunta del dígito que S")
        self.assertTrue(cargar_pregunta("c-sino").endswith("Respondé solo SÍ o NO."))

    def test_c_dice_el_alcance_y_no_ata_el_aviso_al_pedido(self):
        cuerpo = cargar_prompt("c-sino")
        self.assertIn(PREMISA, cuerpo)
        self.assertIn("OTRA es quien la llamó", cuerpo)
        self.assertIn("conviene avisar aunque todavía no haya un pedido", cuerpo)
        self.assertIn("Eso solo no la vuelve una estafa.", cuerpo, "la opción (a) se mantiene")
        for frase in ("Marcá", "solo si", "le pide, induce o presiona", "JSON", "SÍ o NO"):
            self.assertNotIn(frase, cuerpo)
        salida = leer("salida_json_c.txt")
        self.assertNotIn("le está pidiendo", salida, "el motivo ya no se ata al pedido")


class TestMensajeUsuario(unittest.TestCase):
    def test_sin_cierre_queda_igual_que_antes(self):
        mensaje = armar_mensaje_usuario(ROLES[:3], "rol")
        self.assertTrue(mensaje.endswith("\n\nEvaluá la llamada con lo disponible hasta la línea 3."))
        self.assertEqual(mensaje, armar_mensaje_usuario(ROLES[:3], "rol", CIERRE_POR_DEFECTO))

    def test_la_pregunta_reemplaza_solo_la_ultima_oracion(self):
        for n in (1, 4):
            with self.subTest(n=n):
                base = armar_mensaje_usuario(ROLES[:n], "rol")
                con_pregunta = armar_mensaje_usuario(ROLES[:n], "rol", PREGUNTA_S_DIGITO)
                antes, _, ultima = con_pregunta.rpartition("\n\n")
                self.assertEqual(antes, base.rpartition("\n\n")[0])
                self.assertEqual(ultima, PREGUNTA_S_DIGITO.replace("{n}", str(n)))


class TestLeerDigito(unittest.TestCase):
    def test_promedio_ponderado_de_los_digitos(self):
        esperado, masa, top, error = leer_digito(_logprobs(("7", 0.5), (" 7", 0.1), ("8.", 0.2), ("**", 0.1), ("10", 0.05)))
        self.assertEqual(error, "")
        self.assertAlmostEqual(masa, 0.8, places=9)
        self.assertAlmostEqual(esperado, (7 * 0.6 + 8 * 0.2) / 0.8, places=9)
        self.assertEqual(len(top), 5, "se guardan todas las alternativas, también las que no son dígitos")

    def test_sin_digitos_es_fallo_con_masa_cero(self):
        esperado, masa, top, error = leer_digito(_logprobs(("SÍ", 0.7), ("Un", 0.3)))
        self.assertIsNone(esperado)
        self.assertEqual((masa, error, len(top)), (0.0, "sin_digitos", 2))

    def test_respuestas_sin_logprobs_utilizables(self):
        for logprobs, error in ((None, "sin_logprobs"), ([{"token": "7", "logprob": -0.1}], "sin_top_logprobs"),
                                ([{"token": "7", "logprob": -0.1, "top_logprobs": [{"token": "7", "logprob": 0.3}]}],
                                 "logprobs_malformados")):
            with self.subTest(error):
                self.assertEqual(leer_digito(logprobs), (None, None, [], error))


class TestLeerRiesgoJson(unittest.TestCase):
    def pasos(self, *tokens, alternativas=None):
        alternativas = alternativas or {}
        salida = []
        for t in tokens:
            top = _top(*alternativas.get(t, [(t, 1.0)]))
            salida.append({**top[0], "top_logprobs": top})
        return salida

    def test_entero_y_decimal_en_tokens_propios(self):
        pasos = self.pasos('{"', "ries", "go", '":', " ", "0", ".", "3",
                           alternativas={"0": [("0", 0.9), ("1", 0.1)], "3": [("3", 0.5), ("2", 0.3), ("4", 0.2)]})
        riesgo, digito, masa, alternativas, escrito, error = leer_riesgo_json(pasos)
        self.assertEqual(error, "")
        self.assertAlmostEqual(digito, 2.9, places=9)
        self.assertAlmostEqual(masa, 1.0, places=9)
        self.assertAlmostEqual(riesgo, 0.1 + 0.9 * 0.29, places=9)
        self.assertEqual(escrito, 0.3)
        self.assertEqual(set(alternativas), {"entero", "decimal"})

    def test_entero_pegado_al_punto(self):
        pasos = self.pasos('{"riesgo": ', "0.", "1", alternativas={"1": [("1", 0.6), ("2", 0.4)]})
        riesgo, digito, _, _, escrito, error = leer_riesgo_json(pasos)
        self.assertEqual((error, escrito), ("", 0.1))
        self.assertAlmostEqual(digito, 1.4, places=9)
        self.assertAlmostEqual(riesgo, 0.14, places=9)

    def test_sin_entero_propio_usa_solo_el_decimal(self):
        pasos = self.pasos('{"riesgo', '":0', ".", "2", alternativas={"2": [("2", 1.0)]})
        riesgo, digito, _, alternativas, _, error = leer_riesgo_json(pasos)
        self.assertEqual(error, "")
        self.assertNotIn("entero", alternativas)
        self.assertAlmostEqual(riesgo, 0.2, places=9)

    def test_si_escribio_1_el_riesgo_es_1(self):
        riesgo, digito, masa, _, escrito, error = leer_riesgo_json(self.pasos('{"riesgo": ', "1", ","))
        self.assertEqual((riesgo, digito, masa, escrito, error), (1.0, None, None, 1.0, ""))

    def test_fallos(self):
        self.assertEqual(leer_riesgo_json(None)[-1], "sin_logprobs")
        self.assertEqual(leer_riesgo_json(self.pasos('{"', "ries", "go"))[-1], "sin_decimal_de_riesgo")
        self.assertEqual(leer_riesgo_json([{"token": None}])[-1], "logprobs_malformados")


class TestDetectoresConPreguntaFinal(_ConServidorDigitos):
    def test_s_sino_y_s_digito_cambian_solo_la_ultima_oracion_respecto_de_s_json(self):
        json_, _ = DetectorSLM(self.cliente, "m", cargar_prompt("s-json"), "rol").mensajes(ROLES[:3])
        for clase, variante in ((DetectorSLMSiNo, "s-sino"), (DetectorSLMDigito, "s-digito")):
            with self.subTest(variante):
                d = clase(self.cliente, "m", cargar_prompt(variante), "rol", cierre=cargar_pregunta(variante))
                mensajes, _ = d.mensajes(ROLES[:3])
                self.assertEqual(mensajes[0]["content"], cargar_prompt(variante))
                self.assertEqual(mensajes[1]["content"].rpartition("\n\n")[0], json_[1]["content"].rpartition("\n\n")[0])
                self.assertEqual(mensajes[1]["content"].rpartition("\n\n")[2],
                                 cargar_pregunta(variante).replace("{n}", "3"))

    def test_el_pedido_del_digito_lee_un_token(self):
        DetectorSLMDigito(self.cliente, "m", cargar_prompt("s-digito"), "rol",
                          cierre=cargar_pregunta("s-digito")).evaluar(ROLES[:2])
        (pedido,) = OllamaFalso.pedidos
        self.assertNotIn("format", pedido)
        self.assertEqual((pedido["logprobs"], pedido["top_logprobs"], pedido["think"]), (True, 20, False))
        self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096, "num_predict": 1})
        self.assertTrue(pedido["messages"][-1]["content"].endswith("al 9 (casi seguro)."))

    def test_respuesta_con_digito_esperado(self):
        d = DetectorSLMDigito(self.cliente, "m", cargar_prompt("v4-digito"), "rol", cierre=cargar_pregunta("v4-digito"))
        r = d.evaluar(ROLES[:4])  # la línea 4 pide el código
        self.assertTrue(r.valida, r.error)
        self.assertAlmostEqual(r.digito_esperado, (8 * 0.5 + 9 * 0.3 + 7 * 0.1) / 0.9, places=6)
        self.assertAlmostEqual(r.masa_digitos, 0.9, places=6)
        self.assertTrue(r.alerta_sugerida)
        self.assertIsNone(r.p_si)
        self.assertIsNone(r.riesgo)
        r1 = d.evaluar(ROLES[:1])
        self.assertAlmostEqual(r1.digito_esperado, (1 * 0.6 + 2 * 0.1) / 0.9, places=6)
        self.assertFalse(r1.alerta_sugerida)


class TestDetectorLecturaJson(_ConServidorDigitos):
    def test_mismo_pedido_que_v4_salvo_logprobs_y_tokens(self):
        DetectorSLMLecturaJSON(self.cliente, "m", cargar_prompt("v4-lectura"), "rol", esquema=esquema_de("v4-lectura")).evaluar(ROLES[:2])
        (pedido,) = OllamaFalso.pedidos
        json_, _ = DetectorSLM(self.cliente, "m", cargar_prompt("v4"), "rol").mensajes(ROLES[:2])
        self.assertEqual(pedido["messages"], json_)
        self.assertEqual(pedido["format"], ESQUEMA_SALIDA)
        self.assertNotIn("think", pedido, "como en las líneas base JSON, no se envía")
        self.assertEqual((pedido["logprobs"], pedido["top_logprobs"]), (True, 20))
        self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096, "num_predict": 12})

    def test_respuesta_con_riesgo_esperado_y_escrito(self):
        d = DetectorSLMLecturaJSON(self.cliente, "m", cargar_prompt("v4-lectura"), "rol", esquema=esquema_de("v4-lectura"))
        r = d.evaluar(ROLES[:4])
        self.assertTrue(r.valida, r.error)
        self.assertAlmostEqual(r.digito_esperado, 8.2, places=6)
        self.assertAlmostEqual(r.riesgo_esperado, 0.05 + 0.95 * 0.82, places=6)
        self.assertEqual(r.riesgo, 0.8)
        self.assertTrue(r.alerta_sugerida)
        r1 = d.evaluar(ROLES[:1])
        self.assertAlmostEqual(r1.riesgo_esperado, 0.05 + 0.95 * 0.09, places=6)
        self.assertFalse(r1.alerta_sugerida)


class TestCorridaDigito(_ConServidorDigitos):
    def test_corrida_completa_con_columnas_y_pregunta_en_el_manifiesto(self):
        carpeta, manifiesto, filas, columnas = self.correr(
            "--modelos", "modelo-falso:1b", "--prompts", "s-digito", "--hablantes", "rol",
            "--sin-reglas", "--seguir-tras-aviso", "--seed", "42", "--num-ctx", "4096",
        )
        self.assertEqual(columnas, correr.COLUMNAS + correr.COLUMNAS_SINO + correr.COLUMNAS_DIGITO)
        total = sum(len(casos.cargar_texto(c)) for c in CASOS.split(","))
        self.assertEqual(len(filas), total)
        self.assertTrue(all(f["valida"] == "true" and f["digito_esperado"] and f["masa_digitos"] and f["top_logprobs"]
                            for f in filas))
        self.assertTrue(all(f["p_si"] == f["masa_si_no"] == f["riesgo"] == "" for f in filas))
        lectura = manifiesto["parametros_slm"]["lectura_digito"]
        self.assertEqual((lectura["num_predict"], lectura["top_logprobs"]), (1, 20))
        self.assertNotIn("lectura_token", manifiesto["parametros_slm"])
        prompt = manifiesto["prompts"]["s-digito"]
        self.assertEqual(prompt["texto"], cargar_prompt("s-digito"))
        self.assertEqual(prompt["pregunta_final"]["texto"], PREGUNTA_S_DIGITO)
        self.assertEqual(manifiesto["modelos"]["modelo-falso:1b"]["logprobs"]["chequeo"], "ok")
        resumen.armar_resumen(carpeta, con_trayectorias=True)

    def test_corrida_de_v4_lectura(self):
        _, manifiesto, filas, columnas = self.correr("--modelos", "modelo-falso:1b", "--prompts", "v4-lectura",
                                                     "--hablantes", "rol", "--sin-reglas", "--seguir-tras-aviso")
        self.assertEqual(columnas, correr.COLUMNAS + correr.COLUMNAS_SINO + correr.COLUMNAS_DIGITO)
        self.assertTrue(all(f["valida"] == "true" and f["riesgo_esperado"] and f["riesgo"] for f in filas))
        self.assertEqual(manifiesto["parametros_slm"]["lectura_json"]["num_predict"], 12)
        self.assertEqual(manifiesto["prompts"]["v4-lectura"]["texto"], cargar_prompt("v4"))
        self.assertEqual(manifiesto["prompts"]["v4-lectura"]["esquema"], ESQUEMA_SALIDA)

    def test_s_json_corre_como_cualquier_json(self):
        _, manifiesto, filas, columnas = self.correr("--modelos", "modelo-falso:1b", "--prompts", "s-json",
                                                     "--hablantes", "rol", "--sin-reglas")
        self.assertEqual(columnas, correr.COLUMNAS)
        self.assertNotIn("pregunta_final", manifiesto["prompts"]["s-json"])
        self.assertTrue(all(f["riesgo"] for f in filas))

    def test_filtro_tito_no_se_combina_con_el_digito(self):
        from contextlib import redirect_stdout
        with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as salida:
            correr.main(["--modelos", "modelo-falso:1b", "--prompts", "s-digito", "--hablantes", "rol",
                         "--filtro-tito", "--casos", CASOS, "--url", self.url])
        self.assertIn("offline", str(salida.exception))



class TestControlesVentas(unittest.TestCase):
    """Controles de ventas y préstamos: solo para mirar, fuera de los 150 y con fuentes externas."""

    ARCHIVO = Path(__file__).resolve().parents[1] / "casos" / "controles-ventas.json"

    def setUp(self):
        self.datos = json.loads(self.ARCHIVO.read_text(encoding="utf-8"))

    def test_tres_pares_con_fuentes_y_formato_de_los_controles(self):
        clases = [c["clase"] for c in self.datos.values()]
        self.assertEqual((clases.count("legitima_dificil"), clases.count("vishing")), (3, 3))
        for caso, c in self.datos.items():
            self.assertEqual(c["grupo"], "control_ventas", caso)
            self.assertIn(c["protegida"], {"A", "B"}, caso)
            self.assertIs(c["revision_humana"], False, caso)
            self.assertTrue(c["fuentes"] and all(f.startswith("https://") for f in c["fuentes"]), caso)
            self.assertGreaterEqual(len(c["lineas"]), 10, caso)
            self.assertEqual({l[:3] for l in c["lineas"]}, {"A: ", "B: "}, caso)

    def test_no_tocan_los_150_ni_copian_sus_frases(self):
        import correr_controles
        self.assertFalse(set(self.datos) & set(casos.ids_de_casos()))
        vistas = {l.texto.lower() for c in casos.ids_de_casos(particion="desarrollo") for l in casos.cargar_texto(c)}
        for caso, c in self.datos.items():
            for linea in c["lineas"]:
                # 6 palabras o más: «Sí, soy yo. ¿Qué pasó?» (5) es un saludo de cualquier llamada, no un caso copiado
                if len(linea[3:].split()) >= 6:
                    self.assertNotIn(linea[3:].lower(), vistas, caso)
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ids = correr_controles.materializar(Path(tmp), self.ARCHIVO)
            with correr_controles.casos_de(Path(tmp)):
                self.assertEqual(casos.ids_de_casos(particion="desarrollo"), sorted(ids))
                for c in ids:
                    self.assertEqual(casos.cargar_referencia(c)["grupo"], "control_ventas")
                    self.assertEqual({l.hablante for l in casos.con_roles(c, casos.cargar_texto(c))}, {"PROTEGIDA", "OTRA"})
        self.assertEqual(len(casos.ids_de_casos(particion="desarrollo")), 150)


if __name__ == "__main__":
    unittest.main()
