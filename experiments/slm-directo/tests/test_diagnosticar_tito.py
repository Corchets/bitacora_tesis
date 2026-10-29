"""Diagnóstico del Tito histórico (#98): lógica sin modelos.

Usa dobles de `puntuar`/`preparar`; el recorrido real con el encoder vive en
la corrida `diagnosticar_tito.py --salida ...`, no acá.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import diagnosticar_tito as d  # noqa: E402


class TitoDoble:
    def __init__(self, puntajes, error_en=()):
        self.puntajes = dict(puntajes)
        self.error_en = set(error_en)

    def puntuar(self, n, texto):
        if n in self.error_en:
            return None, "tito_caido", 1.0
        return self.puntajes.get(texto, 0.0), "", 1.0


class TestLogica(unittest.TestCase):
    def test_derivacion_igualdad_incluida(self):
        from casos import Linea
        lineas = [Linea("A", "hola"), Linea("B", "sospechoso")]
        ref = {"clase": "vishing", "t_r_linea": 2, "t_c_linea": None,
               "pedido": "REQUEST_AUTH_CODE", "evidencia": [],
               "revision_humana": False}
        tito = TitoDoble({"sospechoso": 0.5})
        rec = d.recorrer_conversacion(tito, "DOBLE", lineas, ref)
        self.assertEqual(rec["derivacion_linea"], 2)
        self.assertEqual(rec["oportunidad_vs_T_R"], "en_el_pedido")
        rec2 = d.recorrer_conversacion(TitoDoble({"sospechoso": 0.49}),
                                       "DOBLE", lineas, ref)
        self.assertIsNone(rec2["derivacion_linea"])
        self.assertTrue(rec["provisional"])

    def test_umbral_constante(self):
        self.assertEqual(d.UMBRAL, 0.5)
        self.assertEqual(d.ENTRADA, "frase_actual_aislada")

    def test_resumen_denominadores_y_terminos(self):
        recorridos = [
            {"case_id": "V1", "clase": "vishing", "t_r_linea": 3,
             "t_c_linea": 5, "derivacion_linea": 2,
             "legitima_derivada": False, "omision_oportuna": False},
            {"case_id": "V2", "clase": "vishing", "t_r_linea": 3,
             "t_c_linea": None, "derivacion_linea": None,
             "legitima_derivada": False, "omision_oportuna": True},
            {"case_id": "L1", "clase": "legitima", "t_r_linea": None,
             "t_c_linea": None, "derivacion_linea": 1,
             "legitima_derivada": True, "omision_oportuna": False},
        ]
        r = d.resumir(recorridos)
        self.assertEqual(r["denominadores"]["vishing_total"], 2)
        self.assertEqual(r["denominadores"]["vishing_con_T_R"], 2)
        self.assertEqual(r["denominadores"]["vishing_con_T_C"], 1)
        self.assertEqual(r["legitimas_derivadas"], ["L1"])
        self.assertNotIn("falsa_alarma", json_claves(r))
        self.assertNotIn("alerta", json_claves(r))

    def test_costos_separan_fallos_y_unidad(self):
        recorridos = [{"case_id": "C", "puntajes": [
            {"linea": 1, "tito_ms": 2.0, "tito_error": ""},
            {"linea": 2, "tito_ms": 3.0, "tito_error": "tito_caido"}]}]
        c = d.costos_actualizaciones(recorridos, truncamientos=0)
        self.assertEqual(c["unidad"], "ms")
        self.assertEqual(c["truncamientos_mayores_128"], 0)
        self.assertEqual(len(c["fallos_tecnicos"]), 1)
        self.assertIn("RTF", c["nota"])
        self.assertIn("audio", c["nota"])

    def test_particion_real_sin_reserva_ni_comparacion(self):
        ids, _, _ = d.cargar_particion_diagnostico()
        self.assertEqual(len(ids), 10)
        for cid in ids:
            self.assertFalse(d.es_identificador_reserva(cid))
        import json as j
        part = j.loads(d.PARTICIONES.read_text(encoding="utf-8"))
        self.assertTrue(set(ids).isdisjoint(set(part.get("evaluacion_ids", []))))

    def test_jaccard_acota_sin_probar_independencia(self):
        from casos import cargar_texto
        sol = d.auditar_solapamiento_semantico(
            ["CV2-D-L-ESCUELA-002"], ["hola mundo", "chau"])
        self.assertIn("no acreditan independencia", sol["advertencia"])
        self.assertEqual(sol["n_lineas_diagnostico"],
                         len(cargar_texto("CV2-D-L-ESCUELA-002")))


def json_claves(obj) -> str:
    import json as j
    return j.dumps(obj, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
