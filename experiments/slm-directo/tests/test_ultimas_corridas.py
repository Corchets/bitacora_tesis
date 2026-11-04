"""Guardas con fixtures sintéticos; no enumeran ni abren el corpus real."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "analisis/tablero/ultimas_corridas.py"
spec = importlib.util.spec_from_file_location("ultimas", SCRIPT)
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)


def fila(linea, aviso="false", consulta="slm_valida", valida="true", error=""):
    return {"linea": str(linea), "aviso": aviso, "consulta": consulta, "valida": valida,
            "riesgo": "" if consulta == "omitida" else "0.7", "error": error,
            "motivo": "Pedido" if aviso == "true" else "", "evidencia": "Cita" if aviso == "true" else ""}


class UltimasCorridasTest(unittest.TestCase):
    def test_distingue_omision_error_y_corte_tras_aviso(self):
        r = panel.resumir([fila(1, consulta="omitida", valida="false"), fila(2, aviso="true")], 4)
        self.assertTrue(r["completo"])
        self.assertEqual(r["aviso"], 2)
        self.assertEqual(r["filas"][0], [None, "omitida", ""])
        self.assertFalse(panel.resumir([fila(1)], 4)["completo"])
        self.assertFalse(panel.resumir([fila(1, valida="false", error="timeout")], 1)["completo"])

    def test_rechaza_lineas_repetidas_o_fuera_de_texto(self):
        for filas in ([fila(2)], [fila(1), fila(1)], [fila(1), fila(2)]):
            with self.assertRaises(ValueError):
                panel.resumir(filas, 1)

    def test_rechaza_reserva_y_rutas_antes_de_abrir_casos(self):
        for cid in ("CV2-T-SENTINELA", "../secreto", ""):
            with self.assertRaises(ValueError):
                panel.manifiesto_completo({"particion": "desarrollo", "casos": {cid: "huella"}})
        with self.assertRaises(ValueError):
            panel.manifiesto_completo({"particion": "test_reservado"})

    def preparar(self, root):
        corrida = root / "corridas/2026-11-04_120000_fixture"
        corrida.mkdir(parents=True)
        for carpeta in ("texto", "referencia"):
            (root / "casos" / carpeta).mkdir(parents=True)
        cid = "CV2-D-FIXTURE"
        texto = "A: Hola\nB: Pasame el código\n"
        (root / "casos/texto" / f"{cid}.txt").write_text(texto)
        (root / "casos/referencia" / f"{cid}.json").write_text(json.dumps({"case_id": cid, "clase": "vishing", "grupo": "fixture", "t_r_linea": 2}))
        m = {"particion": "desarrollo", "casos": {cid: hashlib.sha256(texto.encode()).hexdigest()[:16]},
             "inicio": "2026-11-04T12:00:00", "fin": "2026-11-04T12:01:00", "interrumpida": False,
             "codigo": {"commit": "abc123"}, "configs": [{"config": "fixture", "detector": "slm", "modelo": "modelo", "prompt": "tarea", "hablantes": "ab"}]}
        (corrida / "manifiesto.json").write_text(json.dumps(m))
        rows = [dict(fila(1), config="fixture", case_id=cid), dict(fila(2, aviso="true"), config="fixture", case_id=cid)]
        with (corrida / "actualizaciones.csv").open("w") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader(); writer.writerows(rows)
        return corrida, m

    def test_carga_solo_ids_del_manifiesto_y_excluye_corrida_en_curso(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corrida, m = self.preparar(root)
            # Si enumerara referencias o intentara leer la reserva, este JSON rompería.
            (root / "casos/referencia/CV2-T-SENTINELA.json").write_text("NO ABRIR")
            pendiente = root / "corridas/2026-11-04_130000_pendiente"
            pendiente.mkdir()
            (pendiente / "manifiesto.json").write_text(json.dumps(dict(m, fin=None)))
            datos = panel.cargar_datos(root)
            self.assertEqual(len(datos["corridas"]), 1)
            self.assertEqual(len(datos["pendientes"]), 1)
            self.assertNotIn("CV2-T-SENTINELA", datos["casos"])
            (root / "casos/texto/CV2-D-FIXTURE.txt").write_text("cambió")
            with self.assertRaisesRegex(ValueError, "distinto"):
                panel.cargar_datos(root)

    def test_csv_ajeno_no_se_convierte_en_resultado(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            corrida, _ = self.preparar(root)
            p = corrida / "actualizaciones.csv"
            p.write_text(p.read_text().replace("CV2-D-FIXTURE", "CV2-T-SENTINELA"))
            with self.assertRaisesRegex(ValueError, "ajeno"):
                panel.cargar_datos(root)

    def test_actualizacion_idempotente_y_datos_no_ejecutables(self):
        base = "<main>\n<section>Anterior</section></main><script>const IDS = {resumen:'s-resumen'}; const h=location.hash || '#resumen';</script>"
        datos = {"texto": "</script><script>no ejecutar</script>"}
        primera = panel.incorporar(base, datos)
        self.assertEqual(primera, panel.incorporar(primera, datos))
        self.assertEqual(primera.count('id="s-ultimas"'), 1)
        self.assertEqual(primera.count("ultimas:'s-ultimas'"), 1)
        self.assertNotIn("</script><script>no ejecutar", primera)


if __name__ == "__main__":
    unittest.main()
