"""Verificaciones del HTML offline; fixtures sintéticos, sin recorrer el corpus."""
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "analisis/tablero/comparar_corridas_150.py"
spec = importlib.util.spec_from_file_location("panel_comparativo", SCRIPT)
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)


class Scripts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.json = ""
        self.datos = False
        self.tabs = self.sections = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "section":
            self.sections += 1
        if tag == "button" and attrs.get("role") == "tab":
            self.tabs += 1
        if tag == "script":
            self.datos = attrs.get("id") == "cmp-data"

    def handle_endtag(self, tag):
        if tag == "script":
            self.datos = False

    def handle_data(self, data):
        if self.datos:
            self.json += data


class PanelComparacionTest(unittest.TestCase):
    def setUp(self):
        self.cid = "CV2-D-V-BANCO-003"
        self.base = '''<!doctype html><html lang=es><meta charset=utf-8><title>Anterior</title>
<body><div class=w><h1>Anterior</h1><div class=nav role=tablist><button role=tab>Resumen</button><button role=tab>Corrida y cómo seguir</button></div>
<section><article class=c><header><code>CV2-D-V-BANCO-003</code></header><details><summary>Ver conversación</summary><div class=dw><table class=dl><tr><td>Viejo</td></tr></table></div></details></article></section>
<section><h2>Corrida de diagnóstico</h2><p>Pendiente</p></section></div><script>throw Error('Script viejo');</script></body></html>'''
        self.datos = {"casos": [{"id": self.cid, "texto": ["</script><script>no ejecutar</script>"]}]}

    def test_reemplaza_script_y_conserva_correspondencia_de_tabs(self):
        salida = panel.armar(self.base, self.datos)
        parser = Scripts()
        parser.feed(salida)
        self.assertEqual(parser.tabs, 3)
        self.assertEqual(parser.sections, 3)
        self.assertNotIn("Script viejo", salida)
        self.assertIn('data-comparar="' + self.cid + '"', salida)
        self.assertNotIn("<td>Viejo</td>", salida)
        self.assertEqual(json.loads(parser.json), self.datos)
        self.assertNotIn("<script>no ejecutar", salida)

    def test_regenerar_no_duplica_panel_pasos_ni_enlaces(self):
        primera = panel.armar(self.base, self.datos)
        segunda = panel.armar(primera, self.datos)
        self.assertEqual(primera, segunda)
        self.assertEqual(segunda.count('id="comparacion150"'), 1)
        self.assertEqual(segunda.count('id="plan150"'), 1)

    def test_rechaza_caso_ajeno_y_base_incompatible(self):
        with self.assertRaisesRegex(ValueError, "ajeno"):
            panel.armar(self.base.replace(self.cid, "CV2-T-SENTINELA"), self.datos)
        with self.assertRaisesRegex(ValueError, "sección de pasos"):
            panel.armar("<html>Sin estructura</html>", self.datos)

    def test_omision_respuesta_y_corte_permanecen_distintos(self):
        def fila(linea, riesgo, consulta, valida="true", aviso="false", error=""):
            return {"linea": str(linea), "riesgo": riesgo, "consulta": consulta,
                    "valida": valida, "aviso": aviso, "error": error,
                    "motivo": "Pedido" if aviso == "true" else "",
                    "evidencia": "Entregá" if aviso == "true" else ""}
        datos = panel.resultado([fila(1, "", "omitida"), fila(2, "0.3", "slm_valida"),
                                fila(3, "", "slm_error", "false", error="timeout"),
                                fila(4, "0.7", "slm_valida", aviso="true")])
        self.assertEqual(datos["filas"], [[None, 0], [0.3, 1], [None, 2], [0.7, 1]])
        self.assertEqual(datos["aviso"], 4)
        self.assertEqual(datos["errores"], {"3": "timeout"})
        self.assertEqual(len(datos["filas"]), 4)  # no inventa negativos tras el corte

    def test_diferencias_solo_compara_respuestas_observadas(self):
        solo = {"aviso": 3, "motivo": "Pedido", "evidencia": "Dame",
                "filas": [[0.2, 1], [0.3, 1], [0.5, 1]]}
        tito = {"aviso": 4, "motivo": "Otro pedido", "evidencia": "Pasame",
                "filas": [[None, 0], [0.4, 1], [0.5, 1], [0.8, 1]]}
        self.assertEqual(panel.diferencias(solo, tito),
                         {"riesgo": [2], "alerta": [3], "fundamento": True})
        # Un error y una respuesta ausente no son una diferencia de riesgo.
        tito["filas"] = [[None, 2]]
        tito["aviso"] = None
        self.assertEqual(panel.diferencias(solo, tito),
                         {"riesgo": [], "alerta": [], "fundamento": False})


if __name__ == "__main__":
    unittest.main()
