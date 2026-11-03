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
        canon = {"nombre": pol.get("nombre", "reconsultas-p3"),
                 "periodo_actualizaciones": pol.get("periodo_revision", 3),
                 "regla_nueva_evidencia": pol.get(
                     "regla_nueva_evidencia", "nuevo_cruce_tras_bajar"),
                 "delta_score": pol.get("delta_minimo", 0.0)}
        fro = {"etapa": "seleccion-102-congelada",
               "seleccion_solo_validacion": True,
               "congelado_en": "2026-10-29T00:00:01+00:00",
               "tito": {"artefacto_sha256": "t", "manifiesto100_sha256": "f",
                        "entrada": "historial_acumulado", "umbral": 0.5,
                        "encoder": {"id": "e", "revision": "r"}},
               "politica": canon,
               "modo": "ganadora_para_medir",
               "politica_ganadora": pol}
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

    def test_rechaza_sin_contrato_comun(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._frozen(tmp)
            fro = json.loads(Path(ruta).read_text(encoding="utf-8"))
            fro.pop("seleccion_solo_validacion")
            ruta.write_text(json.dumps(fro), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "seleccion_solo_validacion"):
                matriz_102.politica_congelada_valida(ruta)
            ruta = self._frozen(tmp)
            fro = json.loads(Path(ruta).read_text(encoding="utf-8"))
            fro["congelado_en"] = "2026-10-29T00:00:01"
            ruta.write_text(json.dumps(fro), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "zona UTC"):
                matriz_102.politica_congelada_valida(ruta)

    def test_rechaza_alias_incompatible_con_canonico(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            ruta = self._frozen(tmp)
            fro = json.loads(Path(ruta).read_text(encoding="utf-8"))
            fro["politica_ganadora"]["periodo_revision"] = 5
            ruta.write_text(json.dumps(fro), encoding="utf-8")
            with self.assertRaises(ValueError):
                matriz_102.politica_congelada_valida(ruta)


class TestReuso101(unittest.TestCase):
    def _procedimiento(self, commit="x"):
        proc = matriz_101.huellas_procedimiento()
        proc["codigo"] = {"commit": commit,
                          "cambios_sin_commit_en_la_carpeta": False}
        return proc

    def _funcionales(self, digest="d1", umbral=0.5, hardware=None,
                     timeout=120.0, commit="x"):
        return {"modelos": ["qwen3.5:4b"], "casos": ["c1"],
                "prompt": "tarea", "prompt_huella": "h", "hablantes": "ab",
                "num_ctx": 4096, "seed": 42, "url": "http://127.0.0.1:11435",
                "timeout": timeout, "hardware": hardware,
                "ollama_version": "v", "particiones_sha256": "p",
                "configuracion_sha256": "c",
                "procedimiento": self._procedimiento(commit),
                "inventario": {"qwen3.5:4b": {"digest": digest, "cuantizacion": "q",
                                             "tag": "qwen3.5:4b"}},
                "tito_nuevo": {"sha256": "t", "entrada": "historial_acumulado",
                               "umbral": umbral}}

    def _man101(self, digest="d1", umbral=0.5, hardware=None,
                timeout=120.0, commit="x"):
        return {"politica": correr.POLITICA, "modo_termino": correr.MODO_OPERATIVO,
                "funcionales": self._funcionales(digest, umbral, hardware,
                                                 timeout, commit),
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

    def test_hardware_distinto_bloquea(self):
        ok, motivos = matriz_102.verificar_reuso_101(
            self._man101(hardware=None),
            self._funcionales(hardware={"num_gpu": 0}))
        self.assertFalse(ok)
        self.assertTrue(any("hardware" in m for m in motivos))

    def test_timeout_distinto_bloquea(self):
        ok, motivos = matriz_102.verificar_reuso_101(
            self._man101(timeout=120.0),
            self._funcionales(timeout=60.0))
        self.assertFalse(ok)
        self.assertTrue(any("timeout" in m for m in motivos))

    def test_codigo_distinto_bloquea(self):
        ok, motivos = matriz_102.verificar_reuso_101(
            self._man101(commit="x"),
            self._funcionales(commit="y"))
        self.assertFalse(ok)
        self.assertTrue(any("commit" in m for m in motivos))

    def test_procedimiento_incompatible_mide_ambas(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            man101 = self._man101(hardware=None)
            ruta101 = Path(tmp) / "a_manifiesto.json"
            ruta101.write_text(json.dumps(man101), encoding="utf-8")
            csv102 = Path(tmp) / "b_actualizaciones.csv"
            csv102.write_text("", encoding="utf-8-sig")
            funcionales = self._funcionales(hardware={"num_gpu": 0})
            importados, registro = matriz_102.resolver_reuso_101(
                ruta101, funcionales, csv102, ["qwen3.5:4b"], ["c1"])
            self.assertEqual(importados, set())
            self.assertFalse(registro["reusado"])
            self.assertEqual(registro["triples_importados"], 0)
            self.assertTrue(any("hardware" in m for m in registro["motivos"]))
            self.assertIn("ambas condiciones", registro["nota"])

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
