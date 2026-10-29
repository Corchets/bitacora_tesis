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


class TitoCaido:
    """Doble que simula encoder caído: ninguna inferencia válida."""

    def puntuar(self, n, texto):
        return None, "tito_error: encoder_caido", 1.0


class TitoCorrido:
    """Doble que devuelve puntajes fijos distintos de los almacenados."""

    def puntuar(self, n, texto):
        return 0.99, "", 1.0


def _recorridos_falsos(puntaje=0.1):
    return [{"case_id": "C", "puntajes": [
        {"linea": 1, "texto": "hola", "puntaje": puntaje, "tito_error": ""},
        {"linea": 2, "texto": "mundo", "puntaje": puntaje,
         "tito_error": ""}]}]


class TestRecargaComportamental(unittest.TestCase):
    def _parchar_preparar(self, doble):
        real = d.tito_real.preparar_tito_real
        d.tito_real.preparar_tito_real = lambda *_a, **_k: (doble, {})
        self.addCleanup(setattr, d.tito_real, "preparar_tito_real", real)

    def test_recarga_fallida_no_reproduce_aunque_nada_difiera(self):
        self._parchar_preparar(TitoCaido())
        rec = d.verificar_recarga(["C"], _recorridos_falsos())
        self.assertFalse(rec["reproduce"])
        self.assertEqual(rec["validas"], 0)
        self.assertGreater(rec["fallos_n"], 0)
        self.assertEqual(rec["comparaciones"], 2)

    def test_recarga_sin_inferencias_validas_no_acepta_comparador(self):
        self._parchar_preparar(TitoCaido())
        rec = d.verificar_recarga(["C"], _recorridos_falsos())
        self.assertIs(rec["reproduce"], False)
        self.assertIn("sin inferencias válidas", rec["nota"])

    def test_recarga_con_puntajes_distintos_no_reproduce(self):
        self._parchar_preparar(TitoCorrido())
        rec = d.verificar_recarga(["C"], _recorridos_falsos(puntaje=0.1))
        self.assertFalse(rec["reproduce"])
        self.assertEqual(rec["distintos_n"], 2)
        self.assertEqual(rec["validas"], 2)
        self.assertEqual(rec["fallos_n"], 0)

    def test_recarga_valida_reproduce_con_tolerancia_declarada(self):
        self._parchar_preparar(TitoDoble({"hola": 0.12344, "mundo": 0.12344}))
        rec = d.verificar_recarga(
            ["C"], [{"case_id": "C", "puntajes": [
                {"linea": 1, "texto": "hola", "puntaje": 0.1234,
                 "tito_error": ""},
                {"linea": 2, "texto": "mundo", "puntaje": 0.1234,
                 "tito_error": ""}]}])
        self.assertTrue(rec["reproduce"])
        self.assertEqual(rec["validas"], 2)
        self.assertIn("tolerancia_abs", rec)
        self.assertGreater(rec["tolerancia_abs"], 0)


class TestBancoYFuentes(unittest.TestCase):
    def test_banco_distinque_inventario_de_visto_en_ajuste(self):
        textos, info = d.cargar_banco_historico()
        self.assertEqual(len(textos), info["aceptadas"])
        self.assertEqual(info["aceptadas"] + info["apartadas"],
                         info["inventario_total"])
        self.assertGreater(info["apartadas"], 0)
        self.assertIn("ejemplos_sha256", info)
        self.assertIn("exclusiones_sha256", info)

    def test_banco_reutiliza_auditoria_de_entrenar_tito(self):
        import entrenar_tito as e
        _, info = d.cargar_banco_historico()
        self.assertEqual(info["aceptadas"], e.ESPERADO_ACEPTADAS)
        self.assertEqual(info["apartadas"], e.ESPERADO_APARTADAS)
        self.assertEqual(info["banco_commit"], e.BANCO_COMMIT)
        self.assertEqual(info["ejemplos_sha256"], e.EJEMPLOS_SHA_DECLARADO)
        self.assertEqual(info["exclusiones_sha256"],
                         e.EXCLUSIONES_SHA_DECLARADA)

    def test_huellas_cubren_particiones_config_seleccion_y_textos(self):
        ids, _, _ = d.cargar_particion_diagnostico()
        huellas = d.huellas_diagnostico(ids)
        for clave, ruta in (("particiones_sha256", d.PARTICIONES),
                            ("seleccion_sha256", d.SELECCION),
                            ("configuracion_sha256", d.CONFIG)):
            self.assertEqual(huellas["fuentes"][clave], d.sha_archivo(ruta))
        por_cid = {h["case_id"]: h for h in huellas["conversaciones"]}
        self.assertEqual(set(por_cid), set(ids))
        for cid in ids:
            crudo_txt = (d.AQUI / "casos" / "texto" / f"{cid}.txt").read_bytes()
            self.assertEqual(por_cid[cid]["texto_sha256"],
                             d.sha_bytes(crudo_txt))

    def test_particion_rechaza_deriva_entre_particiones_y_seleccion(self):
        import json as j
        import tempfile
        sel = j.loads(d.SELECCION.read_text(encoding="utf-8"))
        ids, _, _ = d.cargar_particion_diagnostico()
        huellas_reales = {r["case_id"]: r for r in sel["conversaciones"]}
        primera = ids[0]
        manipulada = dict(huellas_reales[primera])
        manipulada["texto_sha256"] = "0" * 64
        sel["conversaciones"] = [
            manipulada if r["case_id"] == primera else r
            for r in sel["conversaciones"]]
        with tempfile.TemporaryDirectory() as tmp:
            falsa = d.Path(tmp) / "SELECCION-falsa.json"
            falsa.write_text(j.dumps(sel), encoding="utf-8")
            real_seleccion = d.SELECCION
            d.SELECCION = falsa
            try:
                with self.assertRaises(ValueError):
                    d.cargar_particion_diagnostico()
            finally:
                d.SELECCION = real_seleccion

    def test_regenerar_md_no_requiere_inferencia(self):
        import json as j
        import tempfile
        informe = j.loads((d.AQUI / "DIAGNOSTICO-TITO-2026-10-29.json")
                            .read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            destino = d.Path(tmp) / "DIAG.json"
            destino.write_text(j.dumps(informe), encoding="utf-8")
            rc = d.main(["--regenerar-md", str(destino)])
            self.assertEqual(rc, 0)
            md = destino.with_suffix(".md")
            self.assertTrue(md.exists())
            texto = md.read_text(encoding="utf-8")
            self.assertIn("# Diagnóstico del Tito histórico", texto)


def json_claves(obj) -> str:
    import json as j
    return j.dumps(obj, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
