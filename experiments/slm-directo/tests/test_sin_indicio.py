"""Tito→SLM sin indicio (`--sin-indicio`): Tito decide cuándo, el SLM recibe el mensaje base.

Con un cliente de Ollama falso que registra lo que llega al modelo, verifica que
con `indicio=False` cada consulta es byte a byte la misma que haría el
`DetectorSLM` solo para esas líneas, que no se consulta antes de que Tito active
y que el valor por defecto sigue mandando el bloque de indicio.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import correr  # noqa: E402
import resumen  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import DetectorSLM, cargar_prompt, esquema_de  # noqa: E402
from filtro_tito import FlujoTitoSLM, TitoGuion  # noqa: E402
from test_ensayo import OllamaFalso  # noqa: E402

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta de WhatsApp."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Para cancelar esa activación tenemos que resolverlo ahora."),
    Linea("A", "Decime el código de activación que recibiste por SMS."),
    Linea("B", "Es cero, cero, cero, cero, cero, cero."),
]

SIN_ALERTA = json.dumps({"riesgo": 0.1, "alerta_sugerida": False, "motivo": "", "evidencia": ""})


class ClienteGrabador:
    """Doble de `ClienteOllama.chat`: guarda cada pedido tal cual y nunca alerta."""

    def __init__(self) -> None:
        self.pedidos: list[dict] = []

    def chat(self, modelo, mensajes, esquema, opciones, pensar=None):
        self.pedidos.append({"modelo": modelo, "mensajes": json.loads(json.dumps(mensajes)),
                             "esquema": esquema, "opciones": dict(opciones), "pensar": pensar})
        return {"message": {"content": SIN_ALERTA}, "prompt_eval_count": 10, "eval_count": 5}


def slm(cliente: ClienteGrabador) -> DetectorSLM:
    return DetectorSLM(cliente, "modelo-falso:1b", cargar_prompt("tarea"), "ab", 4096, 42,
                       esquema=esquema_de("tarea"))


def recorrer(detector) -> list:
    """Recorre el diálogo completo (modo diagnóstico) y devuelve las respuestas."""
    if hasattr(detector, "reiniciar"):
        detector.reiniciar()
    return [r for _, _, r, _ in correr.procesar_caso(detector, DIALOGO, detener_en_aviso=False)]


class TestMensajeIdenticoAlSLMSolo(unittest.TestCase):
    def setUp(self):
        self.solo = ClienteGrabador()
        recorrer(slm(self.solo))

    def _filtrado(self, indicio: bool, puntajes=None, fallos=None):
        cliente = ClienteGrabador()
        f = FlujoTitoSLM(TitoGuion(puntajes, fallos), slm(cliente), indicio=indicio)
        return cliente, recorrer(f)

    def test_sin_indicio_cada_consulta_es_byte_a_byte_la_del_slm_solo(self):
        cliente, respuestas = self._filtrado(False, puntajes={3: 0.8})
        self.assertEqual([r.consulta for r in respuestas], ["omitida"] * 2 + ["slm_valida"] * 3)
        # Las consultas 3, 4 y 5 del SLM solo, idénticas (texto, prompt, esquema y opciones).
        self.assertEqual(cliente.pedidos, self.solo.pedidos[2:])
        for propio, solo in zip(cliente.pedidos, self.solo.pedidos[2:]):
            self.assertEqual(propio["mensajes"][-1]["content"].encode("utf-8"),
                             solo["mensajes"][-1]["content"].encode("utf-8"))
            self.assertNotIn("filtro previo", propio["mensajes"][-1]["content"])

    def test_sin_indicio_no_consulta_antes_de_que_tito_active(self):
        cliente, respuestas = self._filtrado(False, puntajes={1: 0.2, 2: 0.49, 4: 0.5})
        self.assertEqual([r.consulta for r in respuestas[:3]], ["omitida"] * 3)
        self.assertEqual(len(cliente.pedidos), 2)  # L4 (igualdad activa) y L5
        # La activación queda registrada en las filas aunque no se mande al SLM.
        self.assertEqual(respuestas[3].indicio_linea, 4)

    def test_sin_indicio_tampoco_manda_el_bloque_de_fallo_tecnico(self):
        cliente, _ = self._filtrado(False, fallos={2})
        self.assertEqual(cliente.pedidos, self.solo.pedidos[1:])

    def test_por_defecto_sigue_mandando_el_indicio(self):
        cliente, _ = self._filtrado(True, puntajes={3: 0.8})
        self.assertEqual(len(cliente.pedidos), 3)
        for propio, solo in zip(cliente.pedidos, self.solo.pedidos[2:]):
            texto = propio["mensajes"][-1]["content"]
            self.assertTrue(texto.startswith(solo["mensajes"][-1]["content"] + "\n\n"))
            self.assertIn("El filtro previo señaló para revisión la línea 3", texto)
        # Y el constructor sin argumento conserva el comportamiento con indicio.
        self.assertTrue(FlujoTitoSLM(TitoGuion(), slm(ClienteGrabador())).indicio)


class TestCorrerConSinIndicio(unittest.TestCase):
    def _correr(self, *extra: str):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--filtro-tito", "--tito-puntajes", "2=0.9", *extra,
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp.name,
                ])
                (carpeta,) = Path(tmp.name).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                analisis = resumen.analizar(manifiesto, resumen.leer_corrida(carpeta)[1])
                texto = resumen.armar_resumen(carpeta)
            return manifiesto, analisis, texto
        finally:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()

    def test_etiqueta_manifiesto_y_resumen(self):
        manifiesto, analisis, texto = self._correr("--sin-indicio", "--sin-reglas")
        cfg = "tito-slm-sin-indicio|modelo-falso:1b|tarea|ab"
        self.assertIn(cfg, analisis)
        self.assertIn({"config": cfg, "detector": "tito-slm-sin-indicio", "modelo": "modelo-falso:1b",
                       "prompt": "tarea", "hablantes": "ab"}, manifiesto["configs"])
        self.assertIs(manifiesto["filtro_tito"]["indicio"], False)
        self.assertEqual(analisis[cfg]["SC-WA-CODE-01-e01"]["aviso"], 4)
        self.assertIn("## Filtro Tito→SLM", texto)
        self.assertIn("Sin indicio (`--sin-indicio`)", texto)
        self.assertIn(f"`{cfg}`", texto)

    def test_por_defecto_conserva_etiqueta_y_registra_indicio(self):
        manifiesto, analisis, texto = self._correr("--sin-reglas")
        self.assertIn("tito-slm|modelo-falso:1b|tarea|ab", analisis)
        self.assertNotIn("tito-slm-sin-indicio|modelo-falso:1b|tarea|ab", analisis)
        self.assertIs(manifiesto["filtro_tito"]["indicio"], True)
        self.assertNotIn("Sin indicio", texto)

    def test_sin_indicio_exige_filtro_tito(self):
        with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
            correr.main(["--modelos", "modelo-falso:1b", "--sin-indicio"])


if __name__ == "__main__":
    unittest.main()
