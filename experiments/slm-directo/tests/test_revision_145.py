"""Muestreo y conservación de la clave; fixtures sin reserva ni modelos."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import preparar_revision_145 as revision


class Revision145Test(unittest.TestCase):
    def test_muestra_reproducible_con_perdidas_controles_y_legitimas(self):
        refs = {f"CV2-D-V-FICTICIO-{i:03d}": {"clase": "vishing", "t_r_linea": None if i < 9 else 2}
                for i in range(40)}
        # Ni el test ni las legítimas viejas pueden entrar al muestreo de estafas.
        refs["CV2-T-V-SENTINELA"] = {"clase": "vishing", "t_r_linea": None}
        refs["CV2-D-L-SENTINELA"] = {"clase": "legitima", "t_r_linea": None}
        detectadas = {f"CV2-D-V-FICTICIO-{i:03d}" for i in range(16, 40)}
        nuevas = {f"LEG-FICTICIA-{i:03d}": {} for i in range(20)}
        muestra = revision.seleccionar(refs, [detectadas] * 5, nuevas)
        self.assertEqual(muestra, revision.seleccionar(dict(reversed(list(refs.items()))), [detectadas] * 5, nuevas))
        self.assertEqual(len(muestra), 42)
        self.assertEqual(len(set(i for i, _ in muestra)), 42)
        self.assertEqual([sum(g == grupo for _, g in muestra) for grupo in ("sin_aviso", "con_aviso", "legitima_nueva")], [16, 16, 10])
        self.assertFalse(any("SENTINELA" in i for i, _ in muestra))
        with self.assertRaises(ValueError):
            revision.seleccionar(refs, [set()] * 5, nuevas)

    def test_no_pisa_una_clave_anterior_diferente(self):
        with tempfile.TemporaryDirectory() as tmp:
            archivo = Path(tmp) / "clave.json"
            revision.conservar(archivo, "original")
            revision.conservar(archivo, "original")
            with self.assertRaises(ValueError):
                revision.conservar(archivo, "otro")
            self.assertEqual(archivo.read_text(), "original")

    def test_el_dialogo_no_puede_cerrar_el_bloque_json(self):
        salida = revision.renderizar({"casos": [{"id": "Llamada 01", "turnos": [{"texto": "</script><script>alert(1)</script>"}]}]})
        self.assertNotIn("</script><script>alert(1)", salida)
        self.assertIn("\\u003c/script>", salida)

    def test_entrega_publica_solo_contiene_alias_y_dialogos(self):
        import re
        html = (revision.TABLERO / "revision-145.html").read_text()
        datos = json.loads(re.search(r'<script type="application/json" id="data">(.*?)</script>', html, re.S)[1])
        self.assertEqual(len(datos["casos"]), 42)
        self.assertEqual(set(datos), {"version", "muestra", "casos"})
        for c in datos["casos"]:
            self.assertEqual(set(c), {"id", "turnos"})
            self.assertTrue(c["id"].startswith("Llamada "))
            for turno in c["turnos"]:
                self.assertEqual(set(turno), {"hablante", "texto"})
        for secreto in ("CV2-D-", "CV2-T-", "LEG2-", "LEG-", "grupo_muestreo", "referencia_anterior", "CLAVE-REVISION"):
            self.assertNotIn(secreto, html)


if __name__ == "__main__":
    unittest.main()
