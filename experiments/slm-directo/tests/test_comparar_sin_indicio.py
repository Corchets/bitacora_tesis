"""comparar_sin_indicio.py sobre las dos corridas de Windows del 2026-11-04 (ZIP y carpetas)."""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import comparar_sin_indicio as comp  # noqa: E402

SOLO = RAIZ / "corridas/2026-11-04_132229_e2b-directo-150"
TITO = RAIZ / "corridas/2026-11-04_003715_e2b-tito-viejo-150"


@unittest.skipUnless(SOLO.exists() and TITO.exists(), "faltan las corridas de Windows")
class TestCompararSinIndicio(unittest.TestCase):
    def test_reproduce_la_comparacion_documentada(self):
        texto = comp.armar([SOLO, TITO])
        self.assertIn("| Estafas con aviso | 55/75 (73 %) | 51/75 (68 %) |", texto)
        self.assertIn("| Falsas alarmas | 18/75 (24 %) | 13/75 (17 %) |", texto)
        self.assertIn("| · antes del pedido | 25 | 17 |", texto)
        self.assertIn("| Consultas al SLM | 2.218 | 1.179 |", texto)
        self.assertIn("primera consulta antes del pedido en 57", texto)
        self.assertIn("Líneas consultadas en común: 1083; cambia `alerta_sugerida` en 21", texto)
        self.assertIn("| estafa | 10 | 5 |", texto)

    def test_zip_con_tres_condiciones_y_repeticion(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "res"
            # Mismo SLM solo dos veces (nombre posterior = repetición) y el CSV de
            # Tito renombrado a la condición sin indicio para probar el reconocimiento.
            shutil.copytree(SOLO, base / "2026-01-01_000000_a")
            shutil.copytree(SOLO, base / "2026-01-01_000002_c")
            destino = base / "2026-01-01_000001_b"
            destino.mkdir(parents=True)
            texto_csv = (TITO / "actualizaciones.csv").read_text(encoding="utf-8-sig")
            (destino / "actualizaciones.csv").write_text(
                texto_csv.replace(",tito-slm,", ",tito-slm-sin-indicio,").replace(
                    "\ntito-slm|", "\ntito-slm-sin-indicio|"), encoding="utf-8")
            zip_ = Path(tmp) / "r.zip"
            with zipfile.ZipFile(zip_, "w") as z:
                for f in base.rglob("*.csv"):
                    z.write(f, f.relative_to(base))
            texto = comp.armar([zip_])
        self.assertIn("| | SLM solo | Tito → SLM sin indicio | SLM solo (repetición) |", texto)
        self.assertIn("### SLM solo contra SLM solo (repetición)", texto)
        self.assertIn("Líneas consultadas en común: 2218; cambia `alerta_sugerida` en 0", texto)
        self.assertIn("### SLM solo contra Tito → SLM sin indicio", texto)


if __name__ == "__main__":
    unittest.main()
