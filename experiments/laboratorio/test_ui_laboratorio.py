"""Recorridos reales de UI; modelo diminuto aleatorio solo para verificar integración."""

import importlib.util
import io
import json
import tempfile
import unittest
import sys
import types
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

AQUI = Path(__file__).resolve().parent


class InterfazTest(unittest.TestCase):
    def nueva_app(self):
        app = AppTest.from_file(str(AQUI / "ui_laboratorio.py")).run(timeout=60)
        self.assertFalse(app.exception)
        return app

    def test_arranque_con_modulo_de_resultados_anterior_en_memoria(self):
        import ui_resultados

        anterior = types.ModuleType("ui_resultados")
        anterior.__dict__.update({k: v for k, v in vars(ui_resultados).items()
                                 if k not in {"combinar_corridas", "csv_comparacion", "tipo_entrada", "FUENTE_MTIME_NS"}})
        original = sys.modules["ui_resultados"]
        sys.modules["ui_resultados"] = anterior
        try:
            app = AppTest.from_file(str(AQUI / "ui_laboratorio.py")).run(timeout=30)
            self.assertFalse(app.exception, [e.message for e in app.exception])
            charts = app.get("plotly_chart")
            self.assertTrue(len(charts) >= 1)
            panorama = json.loads(charts[0].proto.spec)
            self.assertEqual(panorama["data"][0]["type"], "heatmap")
            self.assertEqual(len(panorama["data"][0]["y"]), 4)
            self.assertEqual(len(charts), 5)  # 1 panorama + 4 paneles individuales
        finally:
            # Restituir solo este módulo: otros imports perezosos de Plotly deben conservarse.
            sys.modules["ui_resultados"] = original

    def test_resultados_filtro_vacio_y_caso_dificil(self):
        app = self.nueva_app()
        next(w for w in app.radio if w.label == "Vista de resultados").set_value("Detalle de un ejemplo").run()
        path = AQUI / "resultados/2026-09-28/resultados-2026-09-28-robertuito-base-uncased.csv"
        app.selectbox[0].set_value(path).run()
        indice = app.selectbox[1].options.index("dificiles/legitima/portero-codigo-puerta.txt")
        app.selectbox[1].set_value(indice).run()
        self.assertFalse(app.exception)
        self.assertIn("portero", app.code[0].value)
        app.multiselect[0].set_value([]).run()
        self.assertFalse(app.exception)

    def test_comparacion_superpone_grabaciones_y_permite_varios_ejemplos(self):
        app = self.nueva_app()
        ejemplos = next(w for w in app.multiselect if w.label == "Ejemplos a comparar")
        self.assertEqual(len(ejemplos.value), 4)
        charts = app.get("plotly_chart")
        self.assertEqual(len(charts), 5)  # 1 panorama + 4 paneles
        panorama = json.loads(charts[0].proto.spec)
        self.assertEqual(panorama["data"][0]["type"], "heatmap")
        self.assertEqual(len(panorama["data"][0]["y"]), 4)
        self.assertEqual(panorama["data"][0]["x"], ["S1", "S2"])
        self.assertEqual(panorama["layout"]["xaxis"]["tickangle"], 0)
        self.assertEqual(panorama["layout"]["xaxis"]["side"], "top")

        # Comprobar que existe la línea de mapeo de series y columna Serie en Procedencia
        self.assertTrue(any("Series en columnas:" in c.value for c in app.caption))
        self.assertTrue(any("Serie" in df.value.columns for df in app.dataframe if hasattr(df.value, "columns")))

        panel1 = json.loads(charts[1].proto.spec)
        self.assertEqual(len(panel1["data"]), 2)  # 2 detectores sobre la misma entrada
        self.assertTrue(all(not t["connectgaps"] for t in panel1["data"]))

        ejemplos.set_value(ejemplos.value[:2]).run()
        self.assertFalse(app.exception)
        charts_filtradas = app.get("plotly_chart")
        self.assertEqual(len(charts_filtradas), 3)  # 1 panorama (2 casos) + 2 paneles
        self.assertEqual(len(json.loads(charts_filtradas[0].proto.spec)["data"][0]["y"]), 2)

        next(w for w in app.radio if w.label == "Eje horizontal").set_value("Avance por cantidad de turnos (%)").run()
        fig_rel = json.loads(app.get("plotly_chart")[1].proto.spec)
        self.assertEqual(fig_rel["layout"]["xaxis"]["range"], [0, 100])
        self.assertTrue(all(t["x"][-1] == 100 for t in fig_rel["data"]))

    def test_comparacion_todos_los_guiones_y_sin_corridas(self):
        app = self.nueva_app()
        next(w for w in app.multiselect if w.label == "Origen de los ejemplos").set_value(["Guiones del laboratorio"]).run()
        self.assertFalse(app.exception)
        charts = app.get("plotly_chart")
        # Panorama conserva todos los 27 guiones seleccionados y sus 7 series breves horizontales
        panorama = json.loads(charts[0].proto.spec)
        self.assertEqual(len(panorama["data"][0]["y"]), 27)
        self.assertEqual(panorama["data"][0]["x"], ["S1", "S2", "S3", "S4", "S5", "S6", "S7"])
        self.assertEqual(panorama["layout"]["xaxis"]["tickangle"], 0)
        # Paneles están paginados (por defecto 4 por página + 1 panorama = 5 charts)
        self.assertEqual(len(charts), 5)
        # Ningún gráfico satura con 189 curvas superpuestas por defecto
        self.assertTrue(all(len(json.loads(c.proto.spec)["data"]) < 189 for c in charts))

        next(w for w in app.multiselect if w.label == "Corridas a comparar").set_value([]).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.get("plotly_chart"))

    def test_recorrido_ayuda_muestra_manual_vigente(self):
        app = self.nueva_app()
        app.sidebar.radio[0].set_value("Ayuda").run()
        self.assertFalse(app.exception)
        self.assertTrue(any("UI local para texto y resultados" in m.value for m in app.markdown))

    def test_superposicion_enfocada_opcional_acotada(self):
        app = self.nueva_app()
        next(w for w in app.checkbox if "superposición enfocada" in w.label.lower()).set_value(True).run()
        self.assertFalse(app.exception)
        charts = app.get("plotly_chart")
        # Gráficos: 1 panorama + 4 paneles + 1 superposición enfocada = 6
        self.assertEqual(len(charts), 6)
        foco_spec = json.loads(charts[-1].proto.spec)
        self.assertTrue(len(foco_spec["data"]) <= 10)
        # Multiselect para selección explícita de series
        ms_series = next(w for w in app.multiselect if "Series a superponer" in w.label)
        self.assertTrue(len(ms_series.options) >= 2)
        # Seleccionar explícitamente 1 sola serie
        ms_series.set_value([ms_series.options[0]]).run()
        self.assertFalse(app.exception)
        charts_act = app.get("plotly_chart")
        foco_act = json.loads(charts_act[-1].proto.spec)
        self.assertEqual(len(foco_act["data"]), 1)

    def test_comparacion_resumen_metricas_y_panel_sin_anotaciones_duplicadas(self):
        app = self.nueva_app()
        # Verificar presencia de los 3 métricas de resumen
        metricas = app.metric
        self.assertTrue(len(metricas) >= 3)
        labels = [m.label for m in metricas]
        self.assertIn("Ejemplos", labels)
        self.assertIn("Series", labels)
        self.assertIn("Archivos CSV", labels)

        # Verificar que figura_panel_ejemplo agrupe anotaciones verticales idénticas
        import ui_laboratorio
        filas_sinteticas = [
            {"caso": "c_test", "detector_goteo": "det1", "corrida_visual": "C1",
             "archivo_resultado": "r1.csv", "n_turnos": "3", "puntajes": "t1=0.2,t2=0.5",
             "T_R_turno": "2", "T_A_turno": "2"},
            {"caso": "c_test", "detector_goteo": "det2", "corrida_visual": "C2",
             "archivo_resultado": "r2.csv", "n_turnos": "3", "puntajes": "t1=0.3,t2=0.8",
             "T_R_turno": "2", "T_A_turno": "2"},
        ]
        fig = ui_laboratorio.figura_panel_ejemplo(filas_sinteticas, "c_test")
        spec = fig.to_plotly_json()
        anns = [a.get("text") for a in spec.get("layout", {}).get("annotations", [])]
        # Debe haber exactamente 1 anotación para Reglas y 1 para Goteo agrupando C1 y C2, no 4
        self.assertEqual(sum(1 for a in anns if "Reglas" in a), 1)
        self.assertEqual(sum(1 for a in anns if "Goteo" in a), 1)
        self.assertIn("Reglas [C1, C2]", anns)
        self.assertIn("Goteo [C1, C2]", anns)

    def test_reglas_sin_entrenamiento_y_encoder_sin_cabeza(self):
        app = self.nueva_app()
        app.sidebar.radio[0].set_value("Probar texto").run()
        app.button[0].click().run(timeout=30)
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertTrue(app.session_state["prueba"]["resultado"]["incendio"]["disparo"])
        self.assertFalse(app.session_state["prueba"]["resultado"]["goteo"]["disparo"])
        app.selectbox[1].set_value("Encoder entrenado").run()
        app.button[0].click().run()
        self.assertTrue(app.error)
        self.assertFalse(app.exception)

    @unittest.skipUnless(all(importlib.util.find_spec(p) for p in ("torch", "transformers", "sklearn")),
                         "Requiere requirements-ui-encoder.txt")
    def test_entrenar_encoder_y_procesar_texto_en_misma_sesion(self):
        import torch
        from transformers import BertConfig, BertModel, BertTokenizerFast

        # Sin descargas ni datos reales. No mide calidad del detector.
        torch.manual_seed(42)
        with tempfile.TemporaryDirectory() as carpeta:
            modelo = Path(carpeta)
            vocab = modelo / "vocab.txt"
            vocab.write_text("[PAD]\n[UNK]\n[CLS]\n[SEP]\n[MASK]\nhola\ncodigo\nbanco\nclave\n", encoding="utf-8")
            BertTokenizerFast(vocab_file=str(vocab)).save_pretrained(modelo)
            BertModel(BertConfig(vocab_size=9, hidden_size=16, num_hidden_layers=1,
                                 num_attention_heads=2, intermediate_size=32)).save_pretrained(modelo)
            app = self.nueva_app()
            app.sidebar.radio[0].set_value("Entrenar").run()
            raw = json.dumps({"estafa": ["codigo banco", "clave codigo"],
                              "legitima": ["hola hola", "hola banco"]}).encode()
            with patch("streamlit.file_uploader", return_value=io.BytesIO(raw)):
                app.run()
                app.text_input[0].set_value(str(modelo)).run()
                app.button[0].click().run(timeout=60)
            self.assertFalse(app.exception)
            self.assertFalse(app.error, [e.value for e in app.error])
            self.assertEqual(app.session_state["entrenamiento"]["seed"], 42)
            app.sidebar.radio[0].set_value("Probar texto").run()
            app.selectbox[1].set_value("Encoder entrenado").run()
            app.button[0].click().run(timeout=60)
            self.assertFalse(app.exception)
            self.assertFalse(app.error)
            resultado = app.session_state["prueba"]["resultado"]
            self.assertTrue(all(0 <= t["puntaje"] <= 1 for t in resultado["turnos"]))


if __name__ == "__main__":
    unittest.main()
