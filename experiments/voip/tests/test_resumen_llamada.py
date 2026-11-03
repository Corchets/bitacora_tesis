import json
import sys
import tempfile
import unittest
from pathlib import Path

DIR_VOIP = Path(__file__).resolve().parent.parent
if str(DIR_VOIP) not in sys.path:
    sys.path.insert(0, str(DIR_VOIP))

import resumen_llamada as R


def jsonl(ruta: Path, filas: list[dict]) -> None:
    ruta.write_text("\n".join(json.dumps(f) for f in filas) + "\n", encoding="utf-8")


class TestFicha(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dialogos = R.cargar_dialogos()
        self.carpeta = Path(self.tmp.name) / "2026-11-02_190000-000001"
        self.carpeta.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def escribir(self, dialogo: str, detector: list[dict], *, segmentacion: dict | None = None, aviso=None):
        d = self.dialogos[dialogo]
        finales = [{"tipo": "final", "canal": l.rol, "texto": l.texto} for l in d.lineas]
        jsonl(self.carpeta / "actualizaciones.jsonl", [{"meta": {}}, {"tipo": "parcial", "canal": "otra", "texto": "ruido"}, *finales])
        jsonl(self.carpeta / "detector.jsonl", detector)
        (self.carpeta / "manifiesto.json").write_text(json.dumps({
            "config": {"asr": "parakeet-silero", "corte_silencio_s": 0.3, "umbral_rms_silencio": 0.003,
                       "detector": "tito-slm", "modelo": "gemma4:e2b-it-q4_K_M"},
            "asr": {"segmentacion": segmentacion or {"umbral_rms_silencio": None, "vad": {"umbral": 0.9}}},
            "detector": {"aviso": aviso, "actualizaciones_salteadas": 1, "fallos": 0},
        }), encoding="utf-8")

    def test_separa_las_consultas_al_modelo_de_las_frases_sin_consulta(self):
        self.escribir("D1", [
            {"ms_detector": 30, "consulta": "omitida"},
            {"ms_detector": 3000, "consulta": "activacion", "indicio_linea": 6, "indicio_puntaje": 0.71},
            {"ms_detector": 1000, "consulta": "seguimiento"},
            {"ms_detector": None, "consulta": "seguimiento"},
        ], aviso={"t_a": 42.5, "motivo": "pide el código", "evidencia": "pasámelo"})
        f = R.ficha(self.carpeta, self.dialogos)
        self.assertEqual((f["dialogo"], f["sin_consulta"], f["consultas"]), ("D1", 1, 2))
        self.assertEqual((f["primera_s"], f["mediana_s"], f["maximo_s"]), (3.0, 2.0, 3.0))
        self.assertEqual((f["tito_linea"], f["tito_puntaje"], f["salteadas"]), (6, 0.71, 1))
        self.assertEqual((f["aviso"], f["t_a"]), (True, 42.5))
        self.assertIn("«pasámelo»", R.tabla([f]))

    def test_informa_el_umbral_que_uso_el_motor_y_no_el_de_la_llamada(self):
        self.escribir("D3", [])
        f = R.ficha(self.carpeta, self.dialogos)
        self.assertEqual((f["umbral_rms"], f["umbral_silero"]), (None, 0.9))
        self.assertEqual(f["sin_consulta"], None)
        self.assertEqual((f["aviso"], f["t_a"]), (False, None))

    def test_una_llamada_que_no_sigue_un_dialogo_no_se_reconoce_ni_va_al_csv(self):
        self.escribir("D1", [])
        jsonl(self.carpeta / "actualizaciones.jsonl", [{"tipo": "final", "canal": "otra", "texto": "mesa de ayuda"}])
        f = R.ficha(self.carpeta, self.dialogos)
        self.assertIsNone(f["dialogo"])
        self.assertEqual(R.filas_de_pruebas([f], "luciano", "otra", set()), [])

    def test_filas_por_canal_con_la_condicion_de_la_tele(self):
        filas = R.filas_de_pruebas([{"id": "a", "dialogo": "D1"}, {"id": "b", "dialogo": "D1"}], "luciano", "mateo", {"b"})
        self.assertEqual(filas, ["a,5,luciano,dialogo,D1,protegida,", "a,5,mateo,dialogo,D1,otra,",
                                 "b,5,luciano,dialogo-tv,D1,protegida,", "b,5,mateo,dialogo-tv,D1,otra,"])


if __name__ == "__main__":
    unittest.main()
