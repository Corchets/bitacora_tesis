"""Prueba que el comparador excluye casos no evaluados en las dos máquinas."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comparar_m1_windows as comparador  # noqa: E402


class TestComparacionCompleta(unittest.TestCase):
    def test_solo_compara_casos_completos_y_validos_en_ambas_maquinas(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            m1 = base / "m1"
            m1.mkdir()
            manifiesto = {"inicio": "inicio", "fin": "fin"}
            (m1 / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")

            modelos = {
                "0.8b": "qwen3.5:0.8b-q8_0",
                "2b": "qwen3.5:2b-q8_0",
                "4b": "qwen3.5:4b-q4_K_M",
            }
            campos = ["modelo", "case_id", "linea", "valida", "aviso", "ms", "motivo"]
            with (m1 / "actualizaciones.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=campos)
                w.writeheader()
                for modelo in modelos.values():
                    for case_id, lineas in (("COMPLETO", (1, 2)), ("TR-03", (1,))):
                        for linea in lineas:
                            w.writerow({"modelo": modelo, "case_id": case_id, "linea": linea,
                                        "valida": "true", "aviso": "false", "ms": 10, "motivo": ""})

            windows = {}
            for clave in modelos:
                carpeta = base / f"windows-{clave}"
                carpeta.mkdir()
                (carpeta / "manifiesto.json").write_text(json.dumps({"comando": "win"}), encoding="utf-8")
                with (carpeta / "actualizaciones.csv").open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=campos)
                    w.writeheader()
                    for case_id in ("COMPLETO", "TR-03"):
                        for linea in (1, 2):
                            w.writerow({"modelo": "win", "case_id": case_id, "linea": linea,
                                        "valida": "true", "aviso": "false", "ms": 20, "motivo": ""})
                windows[clave] = carpeta

            resultado = comparador.comparar_modelos(m1, windows)
            for info in resultado["modelos"].values():
                self.assertEqual(info["casos_incluidos"], ["COMPLETO"])
                self.assertEqual(info["total_casos"], 1)
                self.assertEqual(info["casos_excluidos"], [
                    {"case_id": "TR-03", "motivo": "m1_sin_lineas:2"}
                ])


if __name__ == "__main__":
    unittest.main()
