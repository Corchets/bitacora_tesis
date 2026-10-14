"""Verificaciones del ensayo #50 que no necesitan un modelo real.

Uso (desde experiments/slm-directo):
    python -m unittest discover -s tests -v

Cubren lo que pide #50: prefijos sin texto futuro, estado separado entre llamadas,
salida inválida como fallo, aviso único y contexto excedido informado. Un servidor
falso imita la API de Ollama para probar el código HTTP real.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import threading
from contextlib import redirect_stdout
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import casos  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
import visor  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (  # noqa: E402
    DetectorReglas,
    DetectorSLM,
    Respuesta,
    armar_mensaje_usuario,
    cargar_prompt,
    evidencia_en_texto,
    validar_salida,
)

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta de WhatsApp."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Para cancelar esa activación tenemos que resolverlo ahora."),
    Linea("A", "Decime el código de activación que recibiste por SMS."),
    Linea("B", "Es cero, cero, cero, cero, cero, cero."),
]


class DetectorGuion:
    """Detector falso: anota lo que recibe y responde lo que se le indique por línea."""

    nombre = "guion"

    def __init__(self, alertas: set[int] = frozenset(), invalidas: set[int] = frozenset()):
        self.alertas, self.invalidas = alertas, invalidas
        self.recibido: list[tuple[Linea, ...]] = []

    def evaluar(self, lineas):
        self.recibido.append(lineas)
        n = len(lineas)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido")
        return Respuesta(valida=True, riesgo=0.9 if n in self.alertas else 0.1, alerta_sugerida=n in self.alertas, motivo="m" if n in self.alertas else "")


class TestPrefijosYEstado(unittest.TestCase):
    def test_cada_actualizacion_recibe_solo_el_prefijo(self):
        d = DetectorGuion()
        list(correr.procesar_caso(d, DIALOGO))
        self.assertEqual(len(d.recibido), len(DIALOGO))
        for n, recibido in enumerate(d.recibido, start=1):
            self.assertEqual(list(recibido), DIALOGO[:n], f"la actualización {n} vio texto futuro o le faltó texto")

    def test_el_detector_no_puede_modificar_lo_disponible(self):
        d = DetectorGuion()
        list(correr.procesar_caso(d, DIALOGO))
        self.assertIsInstance(d.recibido[0], tuple)

    def test_el_estado_se_reinicia_entre_llamadas(self):
        d = DetectorGuion(alertas={2})
        primera = list(correr.procesar_caso(d, DIALOGO))
        segunda = list(correr.procesar_caso(d, DIALOGO[:3]))
        self.assertEqual(len(d.recibido[len(DIALOGO)]), 1, "la segunda llamada arrancó con texto de la primera")
        self.assertEqual([aviso for *_, aviso in primera].count(True), 1)
        self.assertEqual([aviso for *_, aviso in segunda].count(True), 1, "el aviso de una llamada bloqueó el de la otra")


class TestPoliticaAvisoUnico(unittest.TestCase):
    def test_un_solo_aviso_en_el_primer_true(self):
        avisos = [aviso for *_, aviso in correr.procesar_caso(DetectorGuion(alertas={2, 4}), DIALOGO)]
        self.assertEqual(avisos, [False, True, False, False, False])

    def test_las_alertas_posteriores_se_conservan(self):
        respuestas = [r for _, _, r, _ in correr.procesar_caso(DetectorGuion(alertas={2, 4}), DIALOGO)]
        self.assertTrue(respuestas[3].alerta_sugerida)

    def test_una_respuesta_invalida_no_avisa(self):
        avisos = [aviso for *_, aviso in correr.procesar_caso(DetectorGuion(alertas={4}, invalidas={2, 3}), DIALOGO)]
        self.assertEqual(avisos, [False, False, False, True, False])


class TestValidacionDeSalida(unittest.TestCase):
    def ok(self, **cambios):
        base = {"riesgo": 0.5, "alerta_sugerida": False, "motivo": "", "evidencia": ""}
        base.update(cambios)
        return json.dumps(base)

    def test_salida_correcta(self):
        salida, error = validar_salida(self.ok(alerta_sugerida=True, motivo="Te piden un código"))
        self.assertEqual(error, "")
        self.assertTrue(salida["alerta_sugerida"])

    def test_salidas_invalidas_son_fallos(self):
        casos_invalidos = {
            "no es json": "json_invalido",
            "[1, 2]": "json_no_es_objeto",
            json.dumps({"riesgo": 0.5}): "faltan_campos",
            self.ok(riesgo=1.5): "riesgo_fuera_de_rango",
            self.ok(riesgo="0.5"): "riesgo_no_numerico",
            self.ok(riesgo=True): "riesgo_no_numerico",
            self.ok(alerta_sugerida="true"): "alerta_no_booleana",
            self.ok(alerta_sugerida=True, motivo="  "): "alerta_sin_motivo",
        }
        for crudo, esperado in casos_invalidos.items():
            with self.subTest(crudo=crudo):
                salida, error = validar_salida(crudo)
                self.assertIsNone(salida)
                self.assertTrue(error.startswith(esperado), error)


class TestMensajeYEvidencia(unittest.TestCase):
    def test_con_hablantes_el_modelo_ve_las_letras(self):
        mensaje = armar_mensaje_usuario(DIALOGO[:2], "ab")
        self.assertIn("1. A: Te llamo", mensaje)
        self.assertIn("2. B: Me acaba", mensaje)

    def test_sin_hablantes_no_llegan_las_letras(self):
        mensaje = armar_mensaje_usuario(DIALOGO[:2], "sin")
        self.assertIn("1. Te llamo", mensaje)
        self.assertNotIn("A:", mensaje)
        self.assertNotIn("B:", mensaje)

    def test_el_mensaje_no_incluye_lineas_futuras(self):
        mensaje = armar_mensaje_usuario(DIALOGO[:3], "ab")
        self.assertNotIn("Decime el código", mensaje)
        self.assertIn("hasta la línea 3", mensaje)

    def test_evidencia_textual_tolera_formato(self):
        self.assertTrue(evidencia_en_texto("4. A: Decime el codigo de activacion", DIALOGO))
        self.assertTrue(evidencia_en_texto("«decime el código de activación que recibiste»", DIALOGO))

    def test_evidencia_de_varias_lineas_numeradas(self):
        # Forma real en que citó qwen3.5:2b en la primera corrida (2026-10-14).
        cita = "A: Te llamo de soporte por la activación de tu cuenta de WhatsApp.\n2. B: Me acaba de llegar un SMS. No pedí activar nada."
        self.assertTrue(evidencia_en_texto(cita, DIALOGO))
        self.assertFalse(evidencia_en_texto(cita + "\n3. A: Pasame la clave del banco.", DIALOGO))

    def test_evidencia_inventada_o_futura_no_es_textual(self):
        self.assertFalse(evidencia_en_texto("Pasame la clave del banco", DIALOGO))
        self.assertFalse(evidencia_en_texto("Decime el código", DIALOGO[:3]))
        self.assertFalse(evidencia_en_texto("", DIALOGO))

    def test_las_dos_variantes_de_prompt_existen(self):
        tarea, con_base = cargar_prompt("tarea"), cargar_prompt("tarea+base")
        self.assertTrue(con_base.startswith(tarea))
        self.assertIn("ANSES", con_base)
        self.assertNotIn("ANSES", tarea)


class TestReglas(unittest.TestCase):
    def evaluar(self, texto: str) -> Respuesta:
        return DetectorReglas().evaluar((Linea("A", texto),))

    def test_pedido_directo_dispara(self):
        r = self.evaluar("Decime el código de activación que recibiste por SMS.")
        self.assertTrue(r.alerta_sugerida)
        self.assertIn("REQUEST_AUTH_CODE", r.motivo)

    def test_negacion_no_dispara(self):
        self.assertFalse(self.evaluar("No. No hace falta que me digas ningún código.").alerta_sugerida)

    def test_mencion_inocente_dispara_como_en_el_laboratorio(self):
        # Falsa alarma conocida de las reglas (portero-codigo-puerta): se conserva para comparar.
        self.assertTrue(self.evaluar("el portero me paso el codigo de la puerta").alerta_sugerida)

    def test_las_reglas_solo_miran_la_linea_nueva(self):
        r = DetectorReglas().evaluar((Linea("A", "Decime el código."), Linea("B", "Bueno.")))
        self.assertFalse(r.alerta_sugerida)


class OllamaFalso(BaseHTTPRequestHandler):
    """Imita /api/chat de Ollama. La respuesta depende de una palabra en el mensaje."""

    pedidos: list[dict] = []
    ignorar_esquema = False  # imita versiones de Ollama que no respetan `format`

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
        OllamaFalso.pedidos.append(pedido)
        usuario = pedido["messages"][-1]["content"]
        if "ok" in pedido["format"].get("properties", {}):  # calentamiento de correr.py
            contenido = "Hola" if OllamaFalso.ignorar_esquema else json.dumps({"ok": True})
        elif "ROMPER" in usuario:
            contenido = "esto no es json"
        elif "Decime el código" in usuario:
            contenido = json.dumps({"riesgo": 0.95, "alerta_sugerida": True, "motivo": "Te piden un código", "evidencia": "Decime el código de activación"})
        else:
            contenido = json.dumps({"riesgo": 0.1, "alerta_sugerida": False, "motivo": "", "evidencia": ""})
        self._responder({"message": {"role": "assistant", "content": contenido}, "prompt_eval_count": 300, "eval_count": 30})


class TestClienteYDetectorContraOllamaFalso(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.cliente = ClienteOllama(f"http://127.0.0.1:{cls.servidor.server_port}", timeout_s=5)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        OllamaFalso.pedidos.clear()

    def detector(self, **kw) -> DetectorSLM:
        return DetectorSLM(self.cliente, "modelo-falso", cargar_prompt("tarea"), **kw)

    def test_el_pedido_lleva_esquema_temperatura_y_contexto(self):
        self.detector(num_ctx=2048, seed=7).evaluar(DIALOGO[:1])
        pedido = OllamaFalso.pedidos[0]
        self.assertEqual(pedido["format"]["required"], ["riesgo", "alerta_sugerida", "motivo", "evidencia"])
        self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 7, "num_ctx": 2048, "num_predict": 512})
        self.assertFalse(pedido["stream"])
        self.assertEqual(pedido["messages"][0]["role"], "system")

    def test_recorrido_completo_con_aviso_unico(self):
        resultados = list(correr.procesar_caso(self.detector(), DIALOGO))
        avisos = [n for n, _, _, aviso in resultados if aviso]
        self.assertEqual(avisos, [4])
        r4 = resultados[3][2]
        self.assertTrue(r4.valida)
        self.assertTrue(r4.evidencia_en_texto)
        self.assertEqual((r4.tokens_prompt, r4.tokens_salida), (300, 30))
        self.assertTrue(resultados[4][2].alerta_sugerida, "la línea 5 conserva la alerta aunque no vuelve a avisar")

    def test_respuesta_rota_queda_como_fallo(self):
        r = self.detector().evaluar((Linea("A", "ROMPER"),))
        self.assertFalse(r.valida)
        self.assertEqual(r.error, "json_invalido")
        self.assertEqual(r.crudo, "esto no es json")

    def test_contexto_excedido_se_informa_sin_llamar_al_modelo(self):
        r = self.detector(num_ctx=64).evaluar(DIALOGO)
        self.assertFalse(r.valida)
        self.assertTrue(r.error.startswith("contexto_excedido"))
        self.assertEqual(OllamaFalso.pedidos, [])

    def test_servidor_caido_queda_como_fallo(self):
        caido = DetectorSLM(ClienteOllama("http://127.0.0.1:9", timeout_s=2), "m", cargar_prompt("tarea"))
        r = caido.evaluar(DIALOGO[:1])
        self.assertFalse(r.valida)
        # Linux y macOS rechazan la conexión enseguida (sin_conexion); Windows la reintenta
        # unos segundos y puede llegar antes el timeout. Las dos quedan como fallo.
        self.assertTrue(r.error.startswith(("sin_conexion", "timeout")), r.error)


class TestCorridaDePuntaAPunta(unittest.TestCase):
    """correr.py y resumen.py completos contra el Ollama falso, en una carpeta temporal."""

    def test_corrida_y_resumen(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--prompts", "tarea,tarea+base",
                    "--hablantes", "ab,sin",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp,
                ])
                (carpeta,) = Path(tmp).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                texto = resumen.armar_resumen(carpeta, con_trayectorias=True)
        finally:
            servidor.shutdown()
            servidor.server_close()
        self.assertEqual(len(manifiesto["configs"]), 5, "reglas + 1 modelo × 2 prompts × 2 hablantes")
        self.assertIsNotNone(manifiesto["fin"])
        self.assertFalse(manifiesto["modelos"]["modelo-falso:1b"]["pensar"])
        self.assertIn("ANSES", manifiesto["prompts"]["tarea+base"]["texto"])
        self.assertIn("| `slm\\|modelo-falso:1b\\|tarea\\|ab` | 1/1 | 0 | 1 | 0 | 0 | 0/1 |", texto)
        self.assertIn("=R L4", texto)
        self.assertIn("[0.95]", texto)

    def test_visor_embebe_datos_que_se_pueden_leer(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp,
                ])
                (carpeta,) = Path(tmp).iterdir()
                pagina = visor.armar_html(visor.datos_de_corridas([carpeta]))
        finally:
            servidor.shutdown()
            servidor.server_close()
        inicio = pagina.index('<script type="application/json" id="datos">') + len('<script type="application/json" id="datos">')
        crudo = pagina[inicio:pagina.index("</script>", inicio)]
        self.assertNotIn("/*__DATOS__*/", pagina)
        datos = json.loads(crudo)
        self.assertEqual([c["id"] for c in datos["configs"]], ["reglas", "slm|modelo-falso:1b|tarea|ab"])
        wa = datos["resultados"]["slm|modelo-falso:1b|tarea|ab"]["SC-WA-CODE-01-e01"]
        self.assertEqual((wa["aviso"], wa["categoria"]), (4, "en_el_pedido"))
        self.assertEqual(datos["resultados"]["reglas"]["LG-WA-CONSULTA-01-e01"]["categoria"], "falsa_alarma")
        self.assertEqual(datos["metricas"]["reglas"]["falsas_alarmas"], 1)


class TestCalentamiento(unittest.TestCase):
    def test_frena_si_ollama_ignora_el_esquema(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        OllamaFalso.ignorar_esquema = True
        try:
            with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                with self.assertRaises(SystemExit) as salida:
                    correr.main([
                        "--modelos", "modelo-falso:1b", "--sin-reglas",
                        "--casos", "SC-WA-CODE-01-e01",
                        "--url", f"http://127.0.0.1:{servidor.server_port}",
                        "--salida", tmp,
                    ])
                (carpeta,) = Path(tmp).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        finally:
            OllamaFalso.ignorar_esquema = False
            servidor.shutdown()
            servidor.server_close()
        self.assertIn("ignoró el formato JSON", str(salida.exception.code))
        self.assertTrue(manifiesto["interrumpida"])
        self.assertIn("error", manifiesto["modelos"]["modelo-falso:1b"])


class TestCasos(unittest.TestCase):
    def test_todos_los_casos_cumplen_el_formato(self):
        self.assertEqual(casos.validar_todos(), [])

    def test_la_referencia_no_esta_en_el_texto(self):
        for case_id in casos.ids_de_casos():
            crudo = (casos.DIR_TEXTO / f"{case_id}.txt").read_text(encoding="utf-8").lower()
            for prohibido in ("vishing", "legitima_dificil", "request_", "t_r", "t_c", "case_id"):
                self.assertNotIn(prohibido, crudo, f"{case_id}.txt contiene {prohibido!r}")


if __name__ == "__main__":
    unittest.main()
