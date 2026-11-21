"""catalogo.py: el catálogo de conversaciones sale de las referencias, las listas y los manifiestos, y no cuenta la
reserva. Con datos ficticios, salvo el último test, que revisa el catálogo de la rama.

Uso (desde experiments/slm-directo):
    python -B -m unittest tests.test_catalogo -v
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import catalogo  # noqa: E402

REFS = {
    "CV2-D-V-A-001": {"grupo": "corpus_v2", "clase": "vishing"},
    "CV2-D-L-A-001": {"grupo": "corpus_v2", "clase": "legitima"},
    "LEG-A-01": {"grupo": "legitimas_cotidianas", "clase": "legitima"},
    "TRAMPA-01": {"grupo": "trampa", "clase": "legitima_dificil"},
}


class TestCatalogo(unittest.TestCase):
    def test_la_descripcion_de_una_lista_son_sus_comentarios_de_arriba(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "prueba-2.txt"
            ruta.write_text("# Dos casos para probar:\n# una estafa y una legítima.\nCV2-D-V-A-001\n\n# otro\nLEG-A-01\n")
            ids, descripcion = catalogo.leer_lista(ruta)
        self.assertEqual(ids, ["CV2-D-V-A-001", "LEG-A-01"])
        self.assertEqual(descripcion, "Dos casos para probar: una estafa y una legítima.")

    def test_reconoce_el_conjunto_de_una_corrida(self):
        listas = {"dos": ["CV2-D-V-A-001", "LEG-A-01"]}
        estados = {"TRAMPA-01": "historico", "LEG-A-01": "cuenta"}
        nombres = catalogo.conjuntos_con_nombre(listas, REFS, estados)
        de = lambda ids: catalogo.conjunto_de(ids, nombres, REFS)  # noqa: E731
        self.assertEqual(de(["LEG-A-01", "CV2-D-V-A-001"]), "lista dos")
        self.assertEqual(de(list(REFS)), "todo el desarrollo (4)")
        self.assertEqual(de(["CV2-D-V-A-001", "CV2-D-L-A-001"]), "grupo corpus_v2")
        self.assertEqual(de(["TRAMPA-01"]), "grupo trampa", "el grupo gana al estado")
        self.assertEqual(de(["LEG-A-01", "TRAMPA-01"]), "2 casos sin lista")
        self.assertEqual(de(["VIEJO-01", "LEG-A-01"]), "2 casos sin lista (1 ya no están en desarrollo)")
        self.assertEqual(de(["CV2-T-V-X-001", "LEG-A-01"]), "incluye la reserva")

    def test_lee_los_manifiestos_de_las_corridas_aunque_esten_anidados(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "a").mkdir()
            (base / "a" / "manifiesto.json").write_text(json.dumps(
                {"inicio": "2026-11-10T15:29:54", "casos": {"LEG-A-01": "h", "TRAMPA-01": "h"},
                 "configs": [{"detector": "slm", "prompt": "c-json-corte-riesgo"}, {"detector": "reglas", "prompt": ""},
                             {"detector": "tito-slm", "prompt": "v4"}]}))
            (base / "b" / "corrida").mkdir(parents=True)
            (base / "b" / "corrida" / "manifiesto.json").write_text(json.dumps({"casos": {}}))
            (base / "c").mkdir()
            (base / "c" / "manifiesto.json").write_text("roto")
            filas = catalogo.corridas(base)
        self.assertEqual([(c, f, ids) for c, f, ids, _ in filas], [("a", "2026-11-10", ["LEG-A-01", "TRAMPA-01"])])
        self.assertEqual(catalogo.resumen_configs(filas[0][3]), "`c-json-corte-riesgo`, `reglas`, `tito-slm v4`")

    def test_cuenta_el_desarrollo_por_grupo_y_no_la_reserva(self):
        md = catalogo.armar(REFS, {"dos": (["CV2-D-V-A-001", "LEG-A-01"], "Dos casos.")}, [])
        self.assertIn("| `corpus_v2` | 2 | 1 | 1 |", md)
        self.assertIn("| **Total** | **4** | **1** | **3** |", md)
        self.assertIn("| `dos` | 2 | 1 | 1 | Dos casos. |", md)
        self.assertIn("rama `reserva/test`", md)
        self.assertIn("| Legítimas de test de #45 | 56 |", md)

    def test_el_catalogo_de_la_rama_no_nombra_casos_de_la_reserva(self):
        texto = catalogo.SALIDA.read_text(encoding="utf-8")
        self.assertEqual(re.findall(r"CV2-T-[A-Z0-9]", texto), [])
        self.assertIn("## 3. Qué usó cada corrida", texto)


if __name__ == "__main__":
    unittest.main()
