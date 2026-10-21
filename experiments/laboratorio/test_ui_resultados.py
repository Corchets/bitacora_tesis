"""Verificaciones de lectura y prueba de texto de #44; no benchmark del detector."""

import json
import tempfile
import unittest
import csv
import io
from pathlib import Path
from unittest.mock import patch

import detector
import pipeline
import ui_resultados as ui


class EvidenciaTest(unittest.TestCase):
    def test_corridas_existentes_separan_resumen_y_conservan_turnos(self):
        archivos = list(ui.RESULTADOS.rglob("*.csv"))
        self.assertTrue(archivos)
        for archivo in archivos:
            with self.subTest(archivo=archivo.name):
                antes = archivo.read_bytes()
                casos, resumen = ui.leer_csv(archivo)
                self.assertTrue(all(f["caso"] != "_suite" for f in casos))
                self.assertTrue(all(f["caso"] == "_suite" for f in resumen))
                for fila in casos:
                    self.assertEqual(len(ui.puntos(fila)), int(fila["n_turnos"]))
                self.assertEqual(antes, archivo.read_bytes())

    def test_cero_es_distinto_de_sin_opinion(self):
        self.assertEqual(ui.puntos({"n_turnos": "3", "puntajes": "t1=0,t3=0.9"}),
                         [{"turno": 1, "puntaje": 0.0}, {"turno": 2, "puntaje": None},
                          {"turno": 3, "puntaje": 0.9}])

    def test_comparacion_no_colapsa_detectores_ni_incluye_suite(self):
        archivos = [ui.RESULTADOS / "2026-09-28/resultados-2026-09-28-transcripciones.csv",
                    ui.RESULTADOS / "2026-09-28/resultados-2026-09-28-robertuito-base-uncased.csv"]
        filas, resumenes = ui.combinar_corridas(archivos)
        self.assertEqual(len(filas), 35)
        self.assertEqual(len(resumenes), 1)
        grabaciones = [f for f in filas if ui.tipo_entrada(f) == "Grabaciones transcritas"]
        self.assertEqual(len(grabaciones), 8)
        self.assertEqual(len({f["caso"] for f in grabaciones}), 4)
        self.assertEqual(len({f["detector_goteo"] for f in grabaciones}), 2)
        self.assertTrue(all(f["caso"] != "_suite" for f in filas))
        exportadas = list(csv.DictReader(io.StringIO(ui.csv_comparacion(filas))))
        self.assertEqual(len(exportadas), 35)
        self.assertEqual(exportadas[0]["archivo_resultado"], str(archivos[0].relative_to(ui.RESULTADOS)))
        self.assertEqual(exportadas[-1]["corrida_visual"], "C2")

    def test_puntajes_corruptos_se_rechazan(self):
        for puntajes in ("t1=nan", "t1=inf", "t1=-0.1", "t3=0.2", "t1=0.1,t1=0.2", "otro"):
            with self.subTest(puntajes=puntajes), self.assertRaises(ValueError):
                ui.puntos({"n_turnos": 2, "puntajes": puntajes})

    def test_csv_no_puede_leer_texto_fuera_del_lab(self):
        self.assertIsNone(ui.texto_caso("../../../../AGENTS.md"))
        self.assertIn("portero", ui.texto_caso("dificiles/legitima/portero-codigo-puerta.txt"))

    def test_entrenamiento_rechaza_clase_vacia_y_contradiccion(self):
        for datos in ({"estafa": [], "legitima": ["hola"]},
                      {"estafa": ["hola"], "legitima": [" hola "]},
                      {"estafa": [5], "legitima": ["hola"]}):
            with self.subTest(datos=datos), self.assertRaises(ValueError):
                ui.validar_semillas(json.dumps(datos).encode())

    def test_csv_exportado_vuelve_al_visor_y_no_guarda_texto(self):
        with tempfile.TemporaryDirectory() as carpeta:
            entrada = Path(carpeta) / "entrada.txt"
            entrada.write_text("hola\ndecime el codigo que recibiste", encoding="utf-8")
            r = pipeline.correr_texto(entrada, det=detector.DetectorLlm(base_url=""))
            self.assertTrue(r["incendio"]["disparo"])
            self.assertFalse(r["goteo"]["disparo"])
            origen = {"fecha_utc": "2026-10-02T00:00:00Z", "commit": "verificacion"}
            fila = ui.fila_texto(r, "reglas", origen, "sin_etiquetar")
            self.assertIsNone(fila["falsa_alarma"])
            self.assertIsNone(fila["T_C_turno"])
            with patch.object(ui, "RESULTADOS", Path(carpeta)):
                uno = ui.guardar_csv(fila)
                dos = ui.guardar_csv(fila)
            self.assertNotEqual(uno, dos)
            self.assertNotIn("decime el codigo", uno.read_text())
            casos, _ = ui.leer_csv(uno)
            self.assertEqual(ui.puntos(casos[0]), [{"turno": 1, "puntaje": None},
                                                 {"turno": 2, "puntaje": None}])

    def test_inyeccion_conserva_historial_e_histeresis_del_spike(self):
        class Puntajes:
            def __init__(self):
                self.historiales = []

            def puntaje(self, texto, historial):
                self.historiales.append(list(historial))
                return 0.9 if texto == "primero" else 0.1

        with tempfile.TemporaryDirectory() as carpeta:
            entrada = Path(carpeta) / "entrada.txt"
            entrada.write_text("# comentario\nprimero\n\nsegundo", encoding="utf-8")
            det = Puntajes()
            resultado = pipeline.correr_texto(entrada, det=det)
        self.assertEqual(det.historiales, [[], ["primero"]])
        self.assertEqual(resultado["goteo"]["turno"], 2)

    def test_color_detector_consistente_y_determinista(self):
        color1 = ui.color_detector("RoBERTuito")
        color2 = ui.color_detector({"detector_goteo": "pysentimiento/robertuito-base-uncased"})
        self.assertEqual(color1, color2)
        self.assertEqual(color1, ui.PALETA_DETECTORES["RoBERTuito"])
        otro1 = ui.color_detector("ModeloNuevo123")
        otro2 = ui.color_detector("ModeloNuevo123")
        self.assertEqual(otro1, otro2)
        self.assertIn(otro1, ui.COLORES_RESERVA)

    def test_trazo_corrida_distingue_corridas(self):
        self.assertEqual(ui.trazo_corrida("C1"), "solid")
        self.assertEqual(ui.trazo_corrida("C2"), "dash")
        self.assertEqual(ui.trazo_corrida("C3"), "dot")
        self.assertEqual(ui.trazo_corrida(None), "solid")

    def test_datos_matriz_panorama_conserva_todos_los_ejemplos_y_marca_sin_datos(self):
        filas = [
            {"caso": "caso_a", "clase": "V", "detector_goteo": "det_a", "corrida_visual": "C1",
             "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": "t1=0.8,t2=0.4"},
            {"caso": "caso_b", "clase": "L", "detector_goteo": "det_a", "corrida_visual": "C1",
             "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": ""},  # Sin opinión
            {"caso": "caso_a", "clase": "V", "detector_goteo": "det_b", "corrida_visual": "C2",
             "archivo_resultado": "r2.csv", "n_turnos": "2", "puntajes": "t1=0.2"},
            # caso_b no está en det_b -> Sin datos
        ]
        matriz = ui.datos_matriz_panorama(filas, ["caso_a", "caso_b"])
        self.assertEqual(matriz["casos"], ["caso_a", "caso_b"])
        self.assertEqual(len(matriz["series"]), 2)
        self.assertEqual(matriz["sin_opinion"], 1)
        self.assertEqual(matriz["sin_datos"], 1)
        # caso_a en det_a: valor numérico
        self.assertEqual(matriz["z"][0][0], 0.8)
        # caso_b en det_a: sin opinión -> None (no cero)
        self.assertIsNone(matriz["z"][1][0])
        self.assertEqual(matriz["text"][1][0], "Sin opinión")
        # caso_b en det_b: sin corrida -> None (no cero)
        self.assertIsNone(matriz["z"][1][1])
        self.assertEqual(matriz["text"][1][1], "Sin datos")

    def test_leer_seccion_manual_extrae_seccion_ui_sin_requisitos(self):
        manual = ui.leer_seccion_manual()
        self.assertIn("## UI local para texto y resultados (#44)", manual)
        self.assertNotIn("## Requisitos", manual)
        self.assertIn("ui_laboratorio.py", manual)

    def test_limpiar_enlaces_relativos_normaliza_anchors_para_streamlit(self):
        entrada = (
            "- [Inicio rápido](#inicio-rápido-y-entorno-virtual)\n"
            "- [Web externa](https://example.com/info)\n"
            "- [Documento](../propuesta/PLAN-DE-TRABAJO.md)\n"
        )
        salida = ui.limpiar_enlaces_relativos_markdown(entrada)
        self.assertIn("[Inicio rápido](#inicio-rapido-y-entorno-virtual)", salida)
        self.assertIn("[Web externa](https://example.com/info)", salida)
        self.assertIn("**Documento** (`../propuesta/PLAN-DE-TRABAJO.md`)", salida)

    def test_dos_ids_crudos_mismo_nombre_visible_conservan_ambas_series_y_celdas(self):
        filas = [
            {"caso": "c1", "clase": "V", "detector_goteo": "pysentimiento/robertuito-base-uncased",
             "corrida_visual": "C1", "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": "t1=0.82"},
            {"caso": "c1", "clase": "V", "detector_goteo": "custom/robertuito-base-uncased-v2",
             "corrida_visual": "C1", "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": "t1=0.64"},
        ]
        series = ui.obtener_series_columnas(filas)
        self.assertEqual(len(series), 2)
        # Ambas series deben tener etiquetas distintas
        self.assertNotEqual(series[0]["etiqueta"], series[1]["etiqueta"])
        matriz = ui.datos_matriz_panorama(filas, ["c1"])
        self.assertEqual(len(matriz["series"]), 2)
        self.assertEqual(matriz["z"][0][0], 0.82)
        self.assertEqual(matriz["z"][0][1], 0.64)

    def test_dos_filas_mismo_caso_id_csv_conservan_ambas_series_y_celdas(self):
        filas = [
            {"caso": "c1", "clase": "V", "detector_goteo": "robertuito",
             "corrida_visual": "C1", "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": "t1=0.71"},
            {"caso": "c1", "clase": "V", "detector_goteo": "robertuito",
             "corrida_visual": "C1", "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": "t1=0.93"},
        ]
        series = ui.obtener_series_columnas(filas)
        self.assertEqual(len(series), 2)
        self.assertNotEqual(series[0]["etiqueta"], series[1]["etiqueta"])
        matriz = ui.datos_matriz_panorama(filas, ["c1"])
        self.assertEqual(len(matriz["series"]), 2)
        self.assertEqual(matriz["z"][0][0], 0.71)
        self.assertEqual(matriz["z"][0][1], 0.93)

    def test_series_columnas_asignan_alias_s_y_preservan_hover_completo(self):
        filas = [
            {"caso": "c1", "clase": "V", "detector_goteo": "pysentimiento/robertuito-base-uncased",
             "corrida_visual": "C1", "archivo_resultado": "r1.csv", "n_turnos": "2", "puntajes": "t1=0.82",
             "commit": "abc1234"},
            {"caso": "c1", "clase": "V", "detector_goteo": "custom/otro-modelo",
             "corrida_visual": "C2", "archivo_resultado": "r2.csv", "n_turnos": "2", "puntajes": "",
             "commit": "def5678"},
        ]
        series = ui.obtener_series_columnas(filas)
        self.assertEqual(len(series), 2)
        self.assertEqual(series[0]["codigo"], "S1")
        self.assertEqual(series[1]["codigo"], "S2")

        matriz = ui.datos_matriz_panorama(filas, ["c1", "c2"])
        self.assertEqual(matriz["x"], ["S1", "S2"])
        # Annotations deben mapear a S1 y S2, no a etiquetas largas
        self.assertTrue(all(a["x"] in {"S1", "S2"} for a in matriz["annotations"]))

        # Hover conserva detector crudo, CSV, commit y etiqueta
        hover_s1 = matriz["customdata"][0][0]
        self.assertIn("S1", hover_s1)
        self.assertIn("pysentimiento/robertuito-base-uncased", hover_s1)
        self.assertIn("r1.csv", hover_s1)
        self.assertIn("abc1234", hover_s1)
        self.assertIn("0.82", hover_s1)


if __name__ == "__main__":
    unittest.main()
