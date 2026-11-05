"""Regresiones del contrato del anotador de desarrollo, sin inferencia."""
import sys
import tempfile
import unittest
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import prompts_supervision_tito_99 as ps
import supervision_tito_99 as st


class TestAnotadorSemantico(unittest.TestCase):
    def test_decisiones_se_convierten_sin_reinterpretar_el_texto(self):
        for decision, etiqueta in (("CONSULTAR", 1), ("NO_CONSULTAR", 0),
                                   ("INCIERTO", None)):
            observado, _, _, error = ps.validar_respuesta({
                "decision": decision, "fundamento": "cita visible",
                "lineas_soporte": [1]}, 1)
            self.assertEqual(error, "")
            self.assertEqual(observado, etiqueta)

    def test_decision_desconocida_o_contradictoria_es_fallo(self):
        for objeto in ({"decision": "OTRA"},
                       {"decision": "CONSULTAR", "etiqueta": 0}):
            _, _, _, error = ps.validar_respuesta({
                **objeto, "fundamento": "cita", "lineas_soporte": [1]}, 1)
            self.assertTrue(error)

    def test_el_esquema_acota_soporte_al_prefijo_sin_mutar_la_base(self):
        recibidos = []
        class Cliente:
            def chat(self, modelo, mensajes, formato, opciones, pensar=None):
                recibidos.append(formato)
                return {"message": {"content": '{"decision":"NO_CONSULTAR",'
                    '"fundamento":"hola","lineas_soporte":[1]}'}}
        resultado = ps.revisar_prefijo(["A: hola", "B: hola"], Cliente(), "m")
        self.assertEqual(resultado["etiqueta"], 0)
        for esquema in recibidos:
            soporte = esquema["properties"]["lineas_soporte"]
            self.assertEqual(soporte["minItems"], 1)
            self.assertEqual(soporte["items"]["minimum"], 1)
            self.assertEqual(soporte["items"]["maximum"], 2)
        self.assertNotIn("maximum", ps.FORMATO_RESPUESTA["properties"]
                         ["lineas_soporte"]["items"])

    def test_recorrido_y_validacion_comparten_implementacion(self):
        self.assertIs(st.revisar_prefijo, ps.revisar_prefijo)
        self.assertIs(st.OPCIONES_MODELO, ps.OPCIONES_MODELO)

    def test_concurrencia_conserva_prefijos_orden_y_reanudado(self):
        class Cliente:
            def chat(self, modelo, mensajes, formato, opciones, pensar=None):
                return {"message": {"content": json.dumps({
                    "decision": "NO_CONSULTAR", "fundamento": "saludo",
                    "lineas_soporte": [1]})}}
        textos = {"A": ["A: saludo alfa", "B: saludo beta"],
                  "B": ["A: saludo gamma"]}
        partes = {"A": "entrenamiento", "B": "validacion"}
        meta = {"tag": "m", "digest": "d", "ollama_version": "v",
                "opciones": ps.OPCIONES_MODELO, "think": ps.PENSAR}
        with tempfile.TemporaryDirectory() as directorio:
            ruta = Path(directorio) / "sup.jsonl"
            resultado = st.recorrer_y_guardar(textos, partes, Cliente(), "m", meta,
                                               ruta=ruta, trabajadores=2)
            self.assertEqual(resultado["nuevos"], 3)
            registros = [json.loads(linea) for linea in ruta.read_text().splitlines()]
            self.assertEqual([(r["case_id"], r["hasta_linea"]) for r in registros],
                             [("A", 1), ("A", 2), ("B", 1)])
            for registro in registros:
                for pasada in ("pasada1", "pasada2"):
                    dialogo = registro[pasada]["prompt"].split("<dialogo>\n")[1].split("\n</dialogo>")[0]
                    self.assertEqual(len(dialogo.splitlines()), registro["hasta_linea"])
            self.assertEqual(st.recorrer_y_guardar(textos, partes, Cliente(), "m", meta,
                                                   ruta=ruta, trabajadores=2)["nuevos"], 0)


if __name__ == "__main__":
    unittest.main()
