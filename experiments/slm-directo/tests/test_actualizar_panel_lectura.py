"""Conservación del panel suministrado; fixtures sintéticos sin corpus ni reserva."""
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "analisis/tablero/actualizar_panel_lectura.py"
spec = importlib.util.spec_from_file_location("actualizador_lectura", SCRIPT)
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)


class Contar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tabs = self.sections = 0

    def handle_starttag(self, tag, attrs):
        self.sections += tag == "section"
        self.tabs += tag == "button" and dict(attrs).get("role") == "tab"


class PanelLecturaTest(unittest.TestCase):
    def setUp(self):
        self.cid = "CV2-D-FIXTURE"
        self.historico = {"casos": [{"id": self.cid, "texto": ["A: Hola"]}]}
        self.datos = {"hasta": "2026-11-04T22:38:48", "corridas": [], "casos": {self.cid: {"texto": ["A: Hola"]}}}
        self.articulo = '<article class=c><header><code>'+self.cid+'</code></header><p class=why><b>Duda explícita.</b> Conservar esta lectura.</p></article>'
        self.base = '<html><meta charset=utf-8><title>Anterior</title><style>/* ESTETICA ORIGINAL */ body{font:14px system-ui}</style><body><div class=w><h1>Anterior</h1><p class=m style="margin:0">Anterior</p><div class=nav role=tablist><button role=tab id="cmp-tab">Comparar corridas</button><button role=tab>Pasos recomendados</button></div><section id="comparacion150">'+self.articulo+'<script id="cmp-data" type="application/json">'+json.dumps(self.historico)+'</script></section><section id="plan150"><h2>Pasos recomendados</h2><p>Antecedente que no se pierde.</p></section></div></body></html>'

    def test_conserva_estetica_articulos_antecedentes_y_navegacion(self):
        salida = panel.armar(self.base, self.datos)
        self.assertIn('<style>/* ESTETICA ORIGINAL */ body{font:14px system-ui}</style>', salida)
        self.assertIn(self.articulo, salida)
        self.assertIn('Antecedente que no se pierde.', salida)
        parser = Contar(); parser.feed(salida)
        self.assertEqual(parser.sections, 3)
        self.assertEqual(parser.tabs, 3)
        self.assertIn('Revisar los casos primero', salida)

    def test_actualizar_dos_veces_es_idempotente(self):
        self.base = self.base.replace('</body>', "<script>document.querySelectorAll('input[type=search]:not(#cmp-search)');</script></body>")
        salida = panel.armar(self.base, self.datos)
        self.assertEqual(salida, panel.armar(salida, self.datos))
        self.assertEqual(salida.count('id="lectura150"'), 1)

    def test_compresion_sin_perdida_y_sin_inyeccion(self):
        malicioso = '</script><script>NO EJECUTAR</script>'
        d = dict(self.datos, comentario=malicioso)
        salida = panel.armar(self.base, d)
        self.assertNotIn(malicioso, salida)
        crudo = re.search(r'<script id="rev-data" type="application/json">(.*?)</script>', salida, re.S)[1]
        paquete = panel.desempaquetar(crudo)
        self.assertEqual(paquete['actual']['comentario'], malicioso)
        # El navegador comparte el mismo texto entre ambas vistas, sin copiarlo ni cambiarlo.
        for c in paquete['historico']['casos']:
            c['texto'] = paquete['actual']['casos'][c['id']]['texto']
        self.assertEqual(paquete['historico'], self.historico)
        self.assertEqual(paquete['actual']['lecturas_previas'][self.cid], 'Duda explícita. Conservar esta lectura.')

    def test_rechaza_texto_diferente_o_articulo_ajeno(self):
        with self.assertRaisesRegex(ValueError, 'histórico'):
            panel.armar(self.base, dict(self.datos, casos={self.cid: {'texto': ['Cambió']}}))
        with self.assertRaisesRegex(ValueError, 'ajeno'):
            panel.armar(self.base.replace('<code>'+self.cid, '<code>CV2-T-SENTINELA'), self.datos)
        with self.assertRaises(ValueError):
            panel.armar('<html>Otro panel</html>', self.datos)


if __name__ == '__main__':
    unittest.main()
