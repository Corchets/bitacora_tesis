"""Tests unitarios para mezclar_canales.py (#19, #28).

Verifica:
1. Orden cronológico por disponible_s (y estabilidad en empates).
2. Renumeración secuencial de n (1 a N sin huecos).
3. Asignación y preservación de etiquetas de canal (A y B).
4. Preservación de segmentos únicos por canal.
5. Integración con archivos JSONL y cabeceras de metadatos.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

# Asegurar importación de mezclar_canales
CARPETA_ASR = Path(__file__).resolve().parent.parent
import sys

if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

from mezclar_canales import mezclar_archivos_jsonl, mezclar_flujos


class TestMezclarCanales(unittest.TestCase):

    def test_orden_y_renumeracion(self):
        """Los eventos deben quedar ordenados por disponible_s y renumerados con n=1..N."""
        canal_a = [
            {"llamada_id": "test", "n": 1, "tipo": "parcial", "segmento": 1, "texto": "hola", "disponible_s": 1.2, "fin_audio_s": 1.0},
            {"llamada_id": "test", "n": 2, "tipo": "final", "segmento": 1, "texto": "hola", "disponible_s": 2.0, "fin_audio_s": 1.8},
            {"llamada_id": "test", "n": 3, "tipo": "final", "segmento": 2, "texto": "segundo turno a", "disponible_s": 5.5, "fin_audio_s": 5.0},
        ]
        canal_b = [
            {"llamada_id": "test", "n": 1, "tipo": "parcial", "segmento": 1, "texto": "si decime", "disponible_s": 3.2, "fin_audio_s": 3.0},
            {"llamada_id": "test", "n": 2, "tipo": "final", "segmento": 1, "texto": "si decime", "disponible_s": 4.1, "fin_audio_s": 3.9},
        ]

        mezcla = mezclar_flujos(canal_a, canal_b)

        self.assertEqual(len(mezcla), 5)

        # Verificar n secuencial
        ns = [m["n"] for m in mezcla]
        self.assertEqual(ns, [1, 2, 3, 4, 5])

        # Verificar orden por disponible_s
        disponibles = [m["disponible_s"] for m in mezcla]
        self.assertEqual(disponibles, [1.2, 2.0, 3.2, 4.1, 5.5])

        # Verificar canales asignados
        canales = [m["canal"] for m in mezcla]
        self.assertEqual(canales, ["A", "A", "B", "B", "A"])

        # Verificar segmentos de cada canal
        # Canal A tiene segmentos 1 y 2
        segs_a = [m["segmento"] for m in mezcla if m["canal"] == "A"]
        self.assertEqual(segs_a, [1, 1, 2])
        # Canal B tiene segmento 1
        segs_b = [m["segmento"] for m in mezcla if m["canal"] == "B"]
        self.assertEqual(segs_b, [1, 1])

    def test_archivos_con_meta(self):
        """Verifica lectura y escritura de archivos JSONL con cabecera meta."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ruta_a = tmp / "canal_a.jsonl"
            ruta_b = tmp / "canal_b.jsonl"
            ruta_out = tmp / "mezcla.jsonl"

            with open(ruta_a, "w", encoding="utf-8") as f:
                f.write(json.dumps({"meta": {"motor": "sherpa-zipformer", "canal": "A"}}) + "\n")
                f.write(json.dumps({"llamada_id": "C01", "n": 1, "tipo": "final", "segmento": 1, "texto": "A1", "disponible_s": 2.5}) + "\n")

            with open(ruta_b, "w", encoding="utf-8") as f:
                f.write(json.dumps({"meta": {"motor": "sherpa-zipformer", "canal": "B"}}) + "\n")
                f.write(json.dumps({"llamada_id": "C01", "n": 1, "tipo": "final", "segmento": 1, "texto": "B1", "disponible_s": 1.5}) + "\n")

            mezclar_archivos_jsonl(ruta_a, ruta_b, ruta_out)

            lineas = [json.loads(l) for l in ruta_out.read_text(encoding="utf-8").splitlines() if l.strip()]
            self.assertEqual(len(lineas), 3)

            # Línea 1: meta combinada
            self.assertIn("meta", lineas[0])
            self.assertEqual(lineas[0]["meta"]["tipo"], "mezcla_canales_estereo")
            self.assertEqual(lineas[0]["meta"]["canales"], ["A", "B"])

            # Línea 2: debe ser B1 (disponible_s=1.5 < 2.5) y tener n=1
            self.assertEqual(lineas[1]["n"], 1)
            self.assertEqual(lineas[1]["canal"], "B")
            self.assertEqual(lineas[1]["texto"], "B1")

            # Línea 3: debe ser A1 y tener n=2
            self.assertEqual(lineas[2]["n"], 2)
            self.assertEqual(lineas[2]["canal"], "A")
            self.assertEqual(lineas[2]["texto"], "A1")


if __name__ == "__main__":
    unittest.main()
