"""El análisis de desarrollo no debe recorrer ni abrir la reserva."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "corridas" / "2026-11-04_132229_e2b-directo-150" / "comparar_directo_vs_tito.py"
spec = importlib.util.spec_from_file_location("comparacion_segura", SCRIPT)
comparacion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(comparacion)


class ComparacionSeguraTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)
        self.directo, self.tito = self.raiz / "directo", self.raiz / "tito"
        self.cid = "CV2-D-V-BANCO-003"
        for nombre in ("texto", "referencia"):
            (self.raiz / "casos" / nombre).mkdir(parents=True)
        texto = "A: Entregá el sobre.\nB: No.\n"
        (self.raiz / "casos/texto" / f"{self.cid}.txt").write_text(texto)
        ref = {"case_id": self.cid, "particion": "desarrollo", "clase": "vishing"}
        (self.raiz / "casos/referencia" / f"{self.cid}.json").write_text(json.dumps(ref))
        self.manifiesto = {"particion": "desarrollo", "interrumpida": False,
                           "casos": {self.cid: hashlib.sha256(texto.encode()).hexdigest()[:16]}}
        for carpeta, detector in ((self.directo, "slm"), (self.tito, "tito-slm")):
            carpeta.mkdir()
            (carpeta / "manifiesto.json").write_text(json.dumps(self.manifiesto))
            with (carpeta / "actualizaciones.csv").open("w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=["detector", "case_id", "linea"])
                w.writeheader()
                w.writerow({"detector": detector, "case_id": self.cid, "linea": 1})

    def leer(self):
        return comparacion.datos(self.directo, self.tito, self.raiz)

    def test_lee_solo_ids_explicitamente_permitidos_sin_enumerar(self):
        lecturas = []
        original = Path.read_text

        def leer(ruta, *args, **kwargs):
            lecturas.append(ruta)
            return original(ruta, *args, **kwargs)

        with patch.object(Path, "read_text", leer), \
             patch.object(Path, "glob", side_effect=AssertionError("No enumerar")), \
             patch.object(Path, "iterdir", side_effect=AssertionError("No enumerar")):
            d, t, refs = self.leer()
        self.assertEqual(set(d), {self.cid})
        self.assertEqual(set(t), {self.cid})
        self.assertEqual(set(refs), {self.cid})
        self.assertEqual(len(lecturas), 4)  # dos manifiestos, un texto, una referencia

    def test_rechaza_reserva_en_cualquiera_de_los_manifiestos_antes_de_casos(self):
        for carpeta in (self.directo, self.tito):
            with self.subTest(carpeta=carpeta):
                m = dict(self.manifiesto, casos={"CV2-T-SENTINELA": "no-abrir"})
                (carpeta / "manifiesto.json").write_text(json.dumps(m))
                with self.assertRaisesRegex(ValueError, "reserva"):
                    self.leer()
                (carpeta / "manifiesto.json").write_text(json.dumps(self.manifiesto))

    def test_rechaza_id_con_traversal(self):
        m = dict(self.manifiesto, casos={"../../otro": "no-abrir"})
        (self.directo / "manifiesto.json").write_text(json.dumps(m))
        with self.assertRaisesRegex(ValueError, "inseguro"):
            self.leer()

    def test_rechaza_csv_con_reserva_aunque_sea_de_otro_detector(self):
        with (self.directo / "actualizaciones.csv").open("a") as f:
            f.write("reglas,CV2-T-SENTINELA,1\n")
        with self.assertRaisesRegex(ValueError, "ajeno"):
            self.leer()

    def test_rechaza_texto_modificado(self):
        (self.raiz / "casos/texto" / f"{self.cid}.txt").write_text("A: Otro texto.\n")
        with self.assertRaisesRegex(ValueError, "Texto distinto"):
            self.leer()

    def test_rechaza_corrida_interrumpida_y_huellas_distintas(self):
        for cambio, mensaje in (({"interrumpida": True}, "completas"),
                                ({"casos": {self.cid: "otra-huella"}}, "huellas")):
            with self.subTest(cambio=cambio):
                (self.tito / "manifiesto.json").write_text(json.dumps(dict(self.manifiesto, **cambio)))
                with self.assertRaisesRegex(ValueError, mensaje):
                    self.leer()


if __name__ == "__main__":
    unittest.main()
