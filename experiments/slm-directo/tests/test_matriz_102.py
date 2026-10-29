"""Tests focales de la matriz #102 (con dobles, sin modelos ni red).

Cubre: denominador global 400 y causas de faltantes; verificación del
reuso de celdas #101 (compatible e incompatible); importación solo de
triples completos con renombre de config; reanudación transaccional sin
duplicados ni alteración de costos; Tito contado en cada actualización;
reapertura ante inválido del SLM; y rechazo de corrida ajena. Ningún
doble acá es una medición.
"""

from __future__ import annotations

import csv
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import correr  # noqa: E402
import matriz_101  # noqa: E402
import matriz_102  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import Respuesta  # noqa: E402
from filtro_tito import TitoGuion  # noqa: E402
from politica_reconsultas import PoliticaReconsultas  # noqa: E402

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Decime el código de activación que recibiste."),
]

POL_P3 = {"nombre": "reconsultas-p3", "periodo_revision": 3,
          "regla_nueva_evidencia": "nuevo_cruce_tras_bajar", "delta_minimo": 0.0}


class SLMGuion:
    def __init__(self, alertas=frozenset(), invalidas=frozenset(), ms_fijo=7.0):
        self.alertas, self.invalidas = set(alertas), set(invalidas)
        self.ms_fijo = ms_fijo
        self.hablantes = "ab"

    def evaluar_mensaje(self, usuario, lineas):
        n = len(lineas)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido", ms=self.ms_fijo)
        alerta = n in self.alertas
        return Respuesta(valida=True, riesgo=0.9 if alerta else 0.1,
                         alerta_sugerida=alerta, ms=self.ms_fijo)


class TestDenominadorYCobertura(unittest.TestCase):
    def test_global_400_diez_por_dos_por_veinte(self):
        self.assertEqual(matriz_102.ESPERADOS_GLOBALES_102, 400)
        triples = matriz_102.plan_pares(list(matriz_102.MODELOS_102),
                                        list(matriz_102.CONDICIONES_102),
                                        list(matriz_102.IDS_102))
        self.assertEqual(len(triples), 400)
        self.assertEqual(len(set(triples)), 400)

    def test_cobertura_con_causas_y_sin_achicar(self):
        triples = matriz_102.plan_pares(["qwen3.5:4b"], ["permanente", "reconsultas"],
                                        ["CV2-D-V-BANCO-001"])
        cob = matriz_102.cobertura_102({}, "", triples, set())
        self.assertEqual(cob["esperados_globales"], 400)
        self.assertEqual(cob["pendientes"], 400)
        self.assertFalse(cob["matriz_completa"])
        causas = {f["causa"] for f in cob["faltantes"]}
        self.assertIn("pendiente-medicion", causas)
        self.assertIn("no-planificado-subset", causas)

    def test_politica_pendiente_y_modelo_bloqueado(self):
        triples = matriz_102.plan_pares(list(matriz_102.MODELOS_102),
                                        list(matriz_102.CONDICIONES_102),
                                        list(matriz_102.IDS_102))
        cob = matriz_102.cobertura_102({"gemma:2b": "ausente"}, "sin congelado",
                                        triples, set())
        causas = {(f["modelo"], f["condicion"], f["causa"]) for f in cob["faltantes"]}
        self.assertTrue(any(m == "gemma:2b" and k == "modelo_bloqueado"
                            for m, c, k in causas))
        self.assertTrue(any(m == "qwen3.5:4b" and c == "reconsultas" and k == "politica-pendiente"
                            for m, c, k in causas))


class TestPoliticaCongelada(unittest.TestCase):
    def _frozen(self, tmp, **cambios):
        pol = dict(POL_P3)
        pol.update(cambios)
        fro = {"etapa": "seleccion-102-congelada", "politica_ganadora": pol}
        ruta = Path(tmp) / "frozen.json"
        ruta.write_text(json.dumps(fro), encoding="utf-8")
        return ruta

    def test_acepta_la_buscada(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            fro = matriz_102.politica_congelada_valida(self._frozen(tmp))
            self.assertEqual(fro["politica_ganadora"]["periodo_revision"], 3)

    def test_rechaza_regla_periodo_y_delta_fuera_de_busqueda(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                matriz_102.politica_congelada_valida(
                    self._frozen(tmp, regla_nueva_evidencia="otra"))
            with self.assertRaises(ValueError):
                matriz_102.politica_congelada_valida(
                    self._frozen(tmp, periodo_revision=2))
            with self.assertRaises(ValueError):
                matriz_102.politica_congelada_valida(
                    self._frozen(tmp, delta_minimo=0.5))


class TestReuso101(unittest.TestCase):
    def _funcionales(self, digest="d1", umbral=0.5):
        return {"modelos": ["qwen3.5:4b"], "casos": ["c1"],
                "prompt": "tarea", "prompt_huella": "h", "hablantes": "ab",
                "num_ctx": 4096, "seed": 42, "url": "http://127.0.0.1:11435",
                "ollama_version": "v", "particiones_sha256": "p", "configuracion_sha256": "c",
                "inventario": {"qwen3.5:4b": {"digest": digest, "cuantizacion": "q",
                                             "tag": "qwen3.5:4b"}},
                "tito_nuevo": {"sha256": "t", "entrada": "historial_acumulado",
                               "umbral": umbral}}

    def _man101(self, digest="d1", umbral=0.5):
        return {"politica": correr.POLITICA, "modo_termino": correr.MODO_OPERATIVO,
                "funcionales": self._funcionales(digest, umbral),
                "ollama": {"version": "v",
                           "modelos": {"qwen3.5:4b": {"digest": digest, "cuantizacion": "q",
                                                      "tag": "qwen3.5:4b"}}},
                "codigo": {"commit": "x"}}

    def test_compatible_pasa(self):
        ok, motivos = matriz_102.verificar_reuso_101(self._man101(), self._funcionales())
        self.assertTrue(ok, motivos)

    def test_digest_distinto_bloquea(self):
        ok, motivos = matriz_102.verificar_reuso_101(self._man101(digest="otro"),
                                                     self._funcionales())
        self.assertFalse(ok)
        self.assertTrue(any("digest" in m for m in motivos))

    def test_umbral_distinto_bloquea(self):
        ok, motivos = matriz_102.verificar_reuso_101(self._man101(umbral=0.7),
                                                     self._funcionales())
        self.assertFalse(ok)

    def test_importa_solo_triples_completos_y_renombra(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            csv101 = Path(tmp) / "a_actualizaciones.csv"
            csv102 = Path(tmp) / "b_actualizaciones.csv"
            csv102.write_text("", encoding="utf-8-sig")
            cfg = {"config": "tito-nuevo|m|tarea|ab", "detector": "tito-slm",
                   "modelo": "m", "prompt": "tarea", "hablantes": "ab"}
            # Triple completo: 3 líneas contiguas, aviso en L2.
            filas = []
            for n, aviso in ((1, "false"), (2, "true")):
                filas.append({**cfg, "case_id": "CID", "linea": n, "aviso": aviso,
                              "valida": "true", "ms": 1.0, "consulta": "slm_valida",
                              "tito_ms": 5.0, "slm_ms": 7.0, "hablante": "A",
                              "texto": "t", "tito_error": ""})
            # Triple parcial: hueco en L2.
            for n in (1, 3):
                filas.append({**cfg, "case_id": "PARCIAL", "linea": n, "aviso": "false",
                              "valida": "true", "ms": 1.0, "consulta": "slm_valida",
                              "tito_ms": 5.0, "slm_ms": 7.0, "hablante": "A",
                              "texto": "t", "tito_error": ""})
            with csv101.open("w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
                w.writeheader()
                for r in filas:
                    w.writerow({c: r.get(c, "") for c in correr.COLUMNAS})
            import unittest.mock as mock
            with mock.patch.object(matriz_102.casos, "cargar_texto",
                                   return_value=[Linea("A", "x")] * 3):
                got = matriz_102.importar_permanente_desde_101(
                    csv101, csv102, ["m"], ["CID", "PARCIAL"])
            self.assertEqual(got, {("m", "permanente", "CID")})
            leidas = matriz_101._leer_filas_csv(csv102)
            self.assertEqual(len(leidas), 2)
            self.assertTrue(all(r["config"] == "permanente|m|tarea|ab" for r in leidas))

    def test_reanudar_retira_parcial_y_no_duplica_completo(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "c.csv"
            cfg = {"config": "permanente|m|tarea|ab", "detector": "tito-slm",
                   "modelo": "m", "prompt": "tarea", "hablantes": "ab"}

            def _fila(cid, n):
                return {**cfg, "case_id": cid, "linea": n, "aviso": "false",
                        "valida": "true", "ms": 5.0, "consulta": "omitida",
                        "tito_ms": 5.0, "slm_ms": "", "hablante": "A",
                        "texto": "t", "tito_error": ""}

            # CID completo + PARCIAL con hueco: la normalización conserva
            # solo el triple contiguo y retira el parcial para remedición.
            # IDs ficticios: se aísla cargar_texto para no tocar casos reales.
            import unittest.mock as mock
            with mock.patch.object(matriz_102.casos, "cargar_texto",
                                   return_value=[Linea("A", "x")] * 2):
                matriz_101.agregar_filas(base, [_fila("CID", 1), _fila("CID", 2),
                                                _fila("PARCIAL", 1)])
                totales = {"CID": 2, "PARCIAL": 2}
                canon = matriz_101.normalizar_traza(base, totales)
                self.assertEqual(len(canon), 2)
                self.assertAlmostEqual(sum(float(r["ms"]) for r in canon), 10.0)
                self.assertEqual(matriz_101.leer_completados(base),
                                 {("m", "permanente", "CID")})
                # Reanudar remide el parcial desde cero: queda contiguo y único.
                matriz_101.agregar_filas(base, [_fila("PARCIAL", 1), _fila("PARCIAL", 2)])
                canon = matriz_101.normalizar_traza(base, totales)
                self.assertEqual(len(canon), 4)
                self.assertEqual(matriz_101.leer_completados(base),
                                 {("m", "permanente", "CID"), ("m", "permanente", "PARCIAL")})


class TestComportamientoConDobles(unittest.TestCase):
    def test_tito_corre_en_cada_actualizacion_incluso_cerrada(self):
        p = PoliticaReconsultas(TitoGuion({1: 0.9}), SLMGuion(), 0.5,
                                periodo_revision=None,
                                regla_nueva_evidencia="nuevo_cruce_tras_bajar",
                                delta_minimo=0.0)
        salidas = list(correr.procesar_caso(p, DIALOGO))
        filas = [correr._fila({"config": "reconsultas|m|t|ab", "detector": "tito-slm",
                               "modelo": "m", "prompt": "t", "hablantes": "ab"},
                              "CID", n, linea, r, aviso)
                 for n, linea, r, aviso in salidas]
        self.assertTrue(all(f["tito_ms"] not in ("", None) for f in filas))
        for f in filas:
            self.assertAlmostEqual(float(f["ms"]), float(f["tito_ms"] or 0)
                                   + float(f["slm_ms"] or 0))

    def test_invalido_no_cierra_y_reintenta(self):
        p = PoliticaReconsultas(TitoGuion({1: 0.9}), SLMGuion(invalidas={1}), 0.5,
                                periodo_revision=None,
                                regla_nueva_evidencia="nuevo_cruce_tras_bajar",
                                delta_minimo=0.0)
        salidas = list(correr.procesar_caso(p, DIALOGO))
        consultas = [r.consulta for _, _, r, _ in salidas]
        self.assertEqual(consultas[0], "slm_fallo")
        self.assertEqual(consultas[1], "slm_valida")

    def test_resolver_rechaza_corrida_ajena(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            man = {"matriz": "matriz-101"}
            ruta = Path(tmp) / "x_manifiesto.json"
            ruta.write_text(json.dumps(man), encoding="utf-8")
            with self.assertRaises(ValueError):
                matriz_102.resolver_corrida_102(ruta)


if __name__ == "__main__":
    unittest.main()
