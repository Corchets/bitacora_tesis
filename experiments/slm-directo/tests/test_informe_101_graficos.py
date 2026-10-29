"""Gráficos de informe_101.py: comportamiento desde fixture conocida.

Verifica que `generar_graficos` produzca figuras Matplotlib regenerables
(SVG + PNG) que expresen categorías, unidades y cobertura — no tautologías
de constantes ni snapshots de implementación.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import casos  # noqa: E402
import correr  # noqa: E402
import informe_101  # noqa: E402
import matriz_101  # noqa: E402
import resumen  # noqa: E402


def _ids():
    vishing = matriz_101.casos_101()[0]
    legitima = matriz_101.casos_101()[10]
    assert casos.cargar_referencia(vishing)["clase"] == "vishing"
    assert casos.cargar_referencia(legitima)["clase"] in casos.LEGITIMAS
    return vishing, legitima


def _manifiesto(ids, configs):
    manifest = {
        "matriz": "matriz-101", "modo_termino": "operativo-hasta-aviso",
        "configs": [{"config": c} for c in configs],
        "casos": {c: {"texto_sha256": "", "referencia_sha256": ""} for c in ids},
        "funcionales": {"modelos": ["m1"],
                        "tito_viejo": {"entrada": "frase_actual", "umbral": 0.5, "sha256": "abc"},
                        "tito_nuevo": {"bloqueo": "sin artefacto"}},
        "cobertura": {"esperados_globales": 600, "planificados": 1,
                      "completados": 1, "pendientes": 599,
                      "matriz_completa": False, "faltantes": []},
        "tito_viejo_preparacion": {"artefacto_ms": 11, "encoder_ms": 22,
                                   "calentamiento_ms": 33, "unidad": "ms", "error": ""},
        "tito_nuevo_preparacion": None,
    }
    for c in ids:
        manifest["casos"][c]["texto_sha256"] = hashlib.sha256(
            (casos.DIR_TEXTO / f"{c}.txt").read_bytes()).hexdigest()
        manifest["casos"][c]["referencia_sha256"] = hashlib.sha256(
            (casos.DIR_REFERENCIA / f"{c}.json").read_bytes()).hexdigest()
    return manifest


def _filas(ids, configs, con_aviso_vishing=True):
    vishing, legitima = ids
    filas = []
    for cfg in configs:
        for cid in ids:
            total = len(casos.cargar_texto(cid))
            for n in range(1, total + 1):
                avisa = con_aviso_vishing and cid == vishing and n == 1
                es_directo = cfg.startswith("directo")
                fila = {c: "" for c in correr.COLUMNAS}
                fila.update({
                    "config": cfg, "case_id": cid, "linea": n,
                    "valida": "true", "aviso": "true" if avisa else "false",
                    "consulta": "slm_valida",
                    "ms": "7", "tito_ms": "" if es_directo else "5",
                    "slm_ms": "7", "tokens_prompt": "10", "tokens_salida": "2",
                })
                filas.append(fila)
    return filas


class TestGraficosInforme(unittest.TestCase):
    def _corrida(self, tmp, con_tito_nuevo=False):
        ids = _ids()
        configs = ["directo|m1|tarea|ab", "tito-viejo|m1|tarea|ab"]
        if con_tito_nuevo:
            # Tito-nuevo con traza pero sin ningún aviso: cero observado.
            configs.append("tito-nuevo|m1|tarea|ab")
        manifiesto = _manifiesto(ids, configs)
        filas = _filas(ids, configs,
                       con_aviso_vishing=True)
        if con_tito_nuevo:
            # Quita los avisos solo de tito-nuevo: cero observado real.
            for f in filas:
                if f["config"].startswith("tito-nuevo"):
                    f["aviso"] = "false"
        analisis = resumen.analizar(manifiesto, filas)
        return manifiesto, filas, analisis

    def test_genera_svg_y_png_no_vacios_y_regenerables(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifiesto, filas, analisis = self._corrida(tmp)
            base = Path(tmp) / "informe_101.md"
            nombres = informe_101.generar_graficos(base, manifiesto, analisis, filas)
            self.assertEqual(len(nombres), 4)
            for nombre in nombres:
                ruta = Path(tmp) / nombre
                self.assertTrue(ruta.exists(), nombre)
                self.assertGreater(ruta.stat().st_size, 500, nombre)
            svg = (Path(tmp) / nombres[0]).read_text(encoding="utf-8")
            self.assertIn("<svg", svg)
            png = (Path(tmp) / nombres[1]).read_bytes()
            self.assertTrue(png.startswith(b"\x89PNG"), "PNG sin firma válida")
            # Regenerar no falla y pisa los mismos archivos.
            nombres2 = informe_101.generar_graficos(base, manifiesto, analisis, filas)
            self.assertEqual(nombres, nombres2)

    def test_calidad_expresa_denominadores_y_sin_datos(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifiesto, filas, analisis = self._corrida(tmp)
            base = Path(tmp) / "informe_101.md"
            nombres = informe_101.generar_graficos(base, manifiesto, analisis, filas)
            svg = (Path(tmp) / nombres[0]).read_text(encoding="utf-8")
            self.assertIn("m1", svg)
            # Vishing con aviso 1/1 y falsas alarmas 0/1: denominadores correctos.
            self.assertIn("1/1", svg)
            self.assertIn("0/1", svg)
            self.assertNotIn("0/0", svg)
            # tito-nuevo no tiene traza: se señala, no se dibuja como cero.
            self.assertIn("sin datos", svg)

    def test_faltante_no_se_confunde_con_cero_observado(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifiesto, filas, analisis = self._corrida(tmp, con_tito_nuevo=True)
            base = Path(tmp) / "informe_101.md"
            nombres = informe_101.generar_graficos(base, manifiesto, analisis, filas)
            svg = (Path(tmp) / nombres[0]).read_text(encoding="utf-8")
            # tito-nuevo con traza y sin avisos muestra cero observado…
            self.assertIn("0/1", svg)
            # …y ya no hay condición sin datos.
            self.assertNotIn("sin datos", svg)

    def test_leyenda_colores_consistentes_y_notas_exportadas(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifiesto, filas, analisis = self._corrida(tmp)
            base = Path(tmp) / "informe_101.md"
            nombres = informe_101.generar_graficos(base, manifiesto, analisis, filas)
            svg_calidad = (Path(tmp) / nombres[0]).read_text(encoding="utf-8")
            svg_costos = (Path(tmp) / nombres[2]).read_text(encoding="utf-8")
            # Colores literales de cada condición en barras y leyenda.
            for color in ("#4a7c59", "#b07d2b", "#5b6abf"):
                self.assertIn(color, svg_calidad)
                self.assertIn(color, svg_costos)
            for cond in ("directo", "tito-viejo", "tito-nuevo"):
                self.assertIn(cond, svg_calidad)
                self.assertIn(cond, svg_costos)
            # Notas completas dentro del artefacto, sin depender de tooltip.
            self.assertIn("Sin datos", svg_calidad)
            self.assertIn("Denominadores excluyen sin evaluar", svg_calidad)
            self.assertIn("artefacto", svg_costos)
            self.assertIn("pendiente", svg_costos)

    def test_costos_expresa_unidades_y_preparacion_separada(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifiesto, filas, analisis = self._corrida(tmp)
            base = Path(tmp) / "informe_101.md"
            nombres = informe_101.generar_graficos(base, manifiesto, analisis, filas)
            svg = (Path(tmp) / nombres[2]).read_text(encoding="utf-8")
            self.assertIn("ms", svg)
            self.assertIn("m1", svg)
            self.assertIn("sin datos", svg)
            # Preparación fuera del costo por línea, explícita por componente.
            self.assertIn("Tito viejo", svg)
            self.assertIn("artefacto", svg)
            self.assertIn("Tito nuevo", svg)
            self.assertIn("pendiente", svg)


if __name__ == "__main__":
    unittest.main()
