"""Tests focales de la selección de política #102 (con dobles, sin modelos).

Cubre: la selección usa SOLO validación (rechaza las veinte y la
reserva); el criterio provisional (detecciones, falsas alarmas,
oportunos) con desempate determinista; el congelado con identidad del
candidato #100; y la medición con dobles sin futuro ni red. Ningún doble
acá es una medición: los valores son mecanismo, no calidad real.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import correr  # noqa: E402
import matriz_101  # noqa: E402
import seleccionar_politica_102 as sel102  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import Respuesta  # noqa: E402
from filtro_tito import TitoGuion  # noqa: E402
from politica_reconsultas import REGLA_NUEVO_CRUCE_TRAS_BAJAR  # noqa: E402

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Decime el código de activación que recibiste."),
    Linea("B", "Es cero, cero, cero, cero."),
]


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


class TitoHistGuion:
    """Doble con la API real del Tito nuevo: historial acumulado, sin futuro."""

    entrada = "historial_acumulado"

    def __init__(self, puntajes=None, ms_fijo=5.0):
        self.puntajes, self.ms_fijo = dict(puntajes or {}), ms_fijo

    def puntuar_entrada(self, texto_entrada):
        return 0.0, "", self.ms_fijo

    def puntuar_prefijo(self, visibles, sintetico=False):
        n = len(visibles)
        return self.puntajes.get(n, 0.0), "", self.ms_fijo


def fabrica(nombre, puntajes=None, alertas=frozenset(), invalidas=frozenset(),
            umbral=0.5):
    def _fab():
        tito, slm = TitoHistGuion(puntajes), SLMGuion(alertas, invalidas)
        if nombre == sel102.BASELINE_102:
            return sel102.construir_permanente(tito, slm, umbral)
        cand = next(c for c in sel102.CANDIDATAS_102 if c["nombre"] == nombre)
        return sel102.construir_politica(tito, slm, cand, umbral)
    return _fab


def fila_resultado(cid, clase="vishing", tr=3, tc=None, aviso=None,
                   consultas=1, falsas=False):
    return {"case_id": cid, "clase": clase, "t_r_linea": tr, "t_c_linea": tc,
            "aviso": aviso, "deteccion": bool(aviso) and clase == "vishing",
            "falsa_alarma": falsas,
            "oportuno": (aviso is not None and aviso <= tr)
                        if clase == "vishing" and tr is not None else None,
            "margen_l_r": (tr - aviso) if (aviso is not None and tr is not None) else None,
            "margen_l_c": (tc - aviso) if (aviso is not None and tc is not None) else None,
            "consultas_slm": consultas, "evitadas_slm": 0,
            "fallos_tito": 0, "fallos_slm": 0, "tito_ms": 5.0, "slm_ms": 7.0}


class TestOrigenSoloValidacion(unittest.TestCase):
    def test_validacion_son_diez_fuera_de_las_veinte(self):
        ids = sel102.validacion_102()
        self.assertEqual(len(ids), 10)
        self.assertTrue(set(ids).isdisjoint(matriz_101.IDS_101))

    def test_rechaza_las_veinte_y_la_reserva(self):
        with self.assertRaises(ValueError):
            sel102.verificar_origen_solo_validacion([matriz_101.IDS_101[0]])
        with self.assertRaises(ValueError):
            sel102.verificar_origen_solo_validacion(["CV2-D-V-BANCO-001"])
        # Un subconjunto de validación sí pasa (no consume test ni veinte).
        ids = sel102.validacion_102()
        sel102.verificar_origen_solo_validacion(ids[:2])

    def test_medir_con_fabrica_rechaza_veinte_antes_de_medir(self):
        with self.assertRaises(ValueError):
            sel102.medir_con_fabrica({sel102.BASELINE_102: fabrica(sel102.BASELINE_102)},
                                     [matriz_101.IDS_101[0]])


class TestMedicionConDobles(unittest.TestCase):
    def test_mide_sin_futuro_y_cuenta_tito_siempre(self):
        ids = sel102.validacion_102()[:2]
        fabricas = {sel102.BASELINE_102: fabrica(sel102.BASELINE_102, {1: 0.9}),
                    "reconsultas-p3": fabrica("reconsultas-p3", {1: 0.9})}
        resultados = sel102.medir_con_fabrica(fabricas, ids)
        for nombre, filas in resultados.items():
            self.assertEqual([f["case_id"] for f in filas], ids)
            for f in filas:
                self.assertGreaterEqual(f["tito_ms"], 0.0)
                self.assertIn("margen_l_c", f)

    def test_referencia_predeclarada_es_la_primera_de_la_lista(self):
        self.assertEqual(sel102.MODELO_REFERENCIA_102, matriz_101.MODELOS_101[0])
        self.assertEqual(sel102.MODELO_REFERENCIA_102, "qwen3.5:4b")

    def test_busqueda_acotada_y_semilla(self):
        self.assertEqual(tuple(c["periodo_revision"] for c in sel102.CANDIDATAS_102), (1, 3, 5))
        self.assertTrue(all(c["delta_minimo"] == 0.0 for c in sel102.CANDIDATAS_102))
        self.assertTrue(all(c["regla_nueva_evidencia"] == REGLA_NUEVO_CRUCE_TRAS_BAJAR
                            for c in sel102.CANDIDATAS_102))
        self.assertEqual(sel102.SEMILLA_102, 42)

    def test_manifiesto_previo_sin_resultados(self):
        man = sel102.manifiesto_busqueda(sel102.validacion_102(), {"modelo_referencia": "qwen3.5:4b"})
        self.assertEqual(man["semilla"], 42)
        self.assertEqual(len(man["candidatas"]), 3)
        self.assertIn("qwen3.5:4b", man["modelo_referencia"])
        self.assertNotIn("resultados_validacion", man)


class TestCriterioProvisional(unittest.TestCase):
    def _resultados(self, base, p1, p5):
        return {sel102.BASELINE_102: base, "reconsultas-p1": p1, "reconsultas-p5": p5}

    def test_mas_detecciones_con_mas_falsas_no_es_elegible(self):
        base = [fila_resultado("a", aviso=3), fila_resultado("b", clase="legitima", tr=None)]
        p1 = [fila_resultado("a", aviso=3), fila_resultado("b", clase="legitima", tr=None,
                                                           aviso=1, falsas=True, consultas=2)]
        p5 = [fila_resultado("a", aviso=3), fila_resultado("b", clase="legitima", tr=None)]
        s = sel102.seleccionar(self._resultados(base, p1, p5))
        self.assertEqual(s["ganadora"], "reconsultas-p5")

    def test_desempata_por_menos_consultas_slm(self):
        base = [fila_resultado("a", aviso=4, consultas=4)]
        p1 = [fila_resultado("a", aviso=2, consultas=3)]
        p5 = [fila_resultado("a", aviso=2, consultas=1)]
        s = sel102.seleccionar(self._resultados(base, p1, p5))
        self.assertEqual(s["ganadora"], "reconsultas-p5")

    def test_sin_elegible_no_hay_ganadora_y_pide_propuesta(self):
        base = [fila_resultado("a", aviso=3)]
        peor = [fila_resultado("a", aviso=None, consultas=0)]
        s = sel102.seleccionar(self._resultados(base, peor, peor))
        self.assertIsNone(s["ganadora"])
        self.assertTrue(s["resultado_negativo"])
        self.assertEqual(s["estado"], sel102.ESTADO_NEGATIVO)
        self.assertFalse(s["apta_para_medir"])
        # Desempate ya escrito entre completas: menos consultas, luego periodo.
        self.assertEqual(s["candidata_exploratoria"], "reconsultas-p1")
        self.assertIn("NO_MEJORA_VALIDACION/no_adoptar", s["motivo"])
        self.assertIn("no se amplía la búsqueda en silencio", s["motivo"])

    def test_sin_mediciones_suficientes_bloquea_explicito(self):
        s = sel102.seleccionar({sel102.BASELINE_102: [fila_resultado("a", aviso=3)]})
        self.assertIsNone(s["ganadora"])
        self.assertIsNone(s["candidata_exploratoria"])
        self.assertEqual(s["estado"], sel102.ESTADO_BLOQUEADO_MEDICION)
        self.assertIn("bloqueo explícito", s["motivo"])

    def test_informa_margenes_lc_y_referencias_ausentes(self):
        base = [fila_resultado("a", aviso=2, tc=5),
                fila_resultado("b", aviso=3, tc=None, consultas=1)]
        s = sel102.seleccionar(self._resultados(base, base, base))
        self.assertEqual(s["resumen_baseline"]["margenes_l_c"], [3])
        self.assertEqual(s["resumen_baseline"]["sin_t_c"], 1)
        self.assertIn("D08", s["advertencia_d08"])

    def test_oportuno_tardio_no_desplaza_baseline(self):
        base = [fila_resultado("a", aviso=2, consultas=2)]  # oportuno (2<=3)
        tarde = [fila_resultado("a", aviso=4, consultas=1)]  # detecta pero tarde
        s = sel102.seleccionar(self._resultados(base, tarde, tarde))
        self.assertIsNone(s["ganadora"])


class TestCongelado(unittest.TestCase):
    def _seleccion(self, ganadora="reconsultas-p3"):
        base = [fila_resultado("a", aviso=3, consultas=2)]
        cand = [fila_resultado("a", aviso=2, consultas=1)]
        res = {sel102.BASELINE_102: base, "reconsultas-p1": base,
               "reconsultas-p3": cand, "reconsultas-p5": base}
        return sel102.seleccionar(res)

    def _tito_info(self, **cambios):
        info = {"artefacto_sha256": "abc123", "entrada": "historial_acumulado",
                "umbral": 0.5, "encoder": {"id": "e", "revision": "r"},
                "encoder_artefacto": {"id": "e", "revision": "r"},
                "variante": "#99-congelada"}
        info.update(cambios)
        return info

    def test_congela_con_identidad_del_candidato(self):
        s = self._seleccion()
        self.assertEqual(s["ganadora"], "reconsultas-p3")
        man = sel102.manifiesto_busqueda(["x"], {})
        fro = sel102.congelar_politica(man, s, "reconsultas-p3", self._tito_info())
        self.assertEqual(fro["politica_ganadora"]["periodo_revision"], 3)
        self.assertEqual(fro["tito_congelado"]["umbral"], 0.5)
        self.assertEqual(fro["tito_congelado"]["variante"], "#99-congelada")
        self.assertIn("congelado_en", fro)

    def test_rechaza_ganadora_fuera_de_la_busqueda(self):
        man = sel102.manifiesto_busqueda(["x"], {})
        with self.assertRaises(ValueError):
            sel102.congelar_politica(man, {"ganadora": "otra"}, "otra", self._tito_info())

    def test_rechaza_sin_identidad_del_tito(self):
        man = sel102.manifiesto_busqueda(["x"], {})
        s = self._seleccion()
        with self.assertRaises(ValueError):
            sel102.congelar_politica(man, s, "reconsultas-p3",
                                     self._tito_info(artefacto_sha256="", encoder={}))
        with self.assertRaises(ValueError):
            sel102.congelar_politica(man, s, "reconsultas-p3",
                                     self._tito_info(variante=""))
        with self.assertRaises(ValueError):
            sel102.congelar_politica(man, s, "reconsultas-p3",
                                     self._tito_info(
                                         encoder_artefacto={"id": "otro", "revision": "r"}))

    def test_congelado_expone_contrato_comun_con_100(self):
        man = sel102.manifiesto_busqueda(["x"], {})
        s = self._seleccion()
        fro = sel102.congelar_politica(man, s, "reconsultas-p3",
                                       self._tito_info(manifiesto100_sha256="f" * 64))
        self.assertTrue(fro["seleccion_solo_validacion"])
        self.assertEqual(fro["modo"], sel102.ESTADO_GANADORA)
        self.assertTrue(fro["apta_para_medir"])
        self.assertFalse(fro["resultado_negativo"])
        self.assertEqual(fro["tito"]["artefacto_sha256"], "abc123")
        self.assertEqual(fro["tito"]["manifiesto100_sha256"], "f" * 64)
        self.assertEqual(fro["tito"]["entrada"], "historial_acumulado")
        self.assertEqual(fro["politica"]["periodo_actualizaciones"], 3)
        self.assertEqual(fro["politica"]["regla_nueva_evidencia"],
                         "nuevo_cruce_tras_bajar")
        self.assertEqual(fro["politica"]["delta_score"], 0.0)
        from datetime import datetime
        momento = datetime.fromisoformat(fro["congelado_en"])
        self.assertIsNotNone(momento.tzinfo)

    def test_congela_exploratoria_negativa_no_ganadora(self):
        man = sel102.manifiesto_busqueda(["x"], {})
        base = [fila_resultado("a", aviso=3)]
        peor = [fila_resultado("a", aviso=None, consultas=0)]
        s = sel102.seleccionar({sel102.BASELINE_102: base,
                                "reconsultas-p1": peor,
                                "reconsultas-p3": peor,
                                "reconsultas-p5": peor})
        fro = sel102.congelar_politica(man, s, "reconsultas-p1",
                                       self._tito_info(manifiesto100_sha256="f" * 64))
        self.assertEqual(fro["modo"], sel102.ESTADO_NEGATIVO)
        self.assertFalse(fro["apta_para_medir"])
        self.assertTrue(fro["resultado_negativo"])
        with self.assertRaises(ValueError):
            sel102.congelar_politica(man, s, "reconsultas-p3",
                                     self._tito_info(manifiesto100_sha256="f" * 64))


class TestCoberturaMismaIDs(unittest.TestCase):
    def test_condicion_incompleta_no_es_elegible(self):
        base = [fila_resultado("a", aviso=3), fila_resultado("b", clase="legitima", tr=None)]
        incompleta = [fila_resultado("a", aviso=3)]
        s = sel102.seleccionar({sel102.BASELINE_102: base,
                                "reconsultas-p1": incompleta,
                                "reconsultas-p3": list(base),
                                "reconsultas-p5": list(base)})
        fila = next(f for f in s["tabla"] if f["candidata"] == "reconsultas-p1")
        self.assertEqual(fila["cobertura"], "incompleta")
        self.assertEqual(fila["estado"], "cobertura_incompleta")
        self.assertEqual(fila["faltantes_vs_baseline"], ["b"])
        self.assertFalse(fila["cumple_criterio"])
        # La incompleta no desplaza a las completas.
        self.assertEqual(s["ganadora"], "reconsultas-p3")

    def test_fallos_se_clasifican_sin_ocultar(self):
        base = [fila_resultado("a", aviso=3)]
        con_fallos = [dict(fila_resultado("a", aviso=3), fallos_tito=2, fallos_slm=1)]
        s = sel102.seleccionar({sel102.BASELINE_102: base,
                                "reconsultas-p1": con_fallos,
                                "reconsultas-p3": list(base),
                                "reconsultas-p5": list(base)})
        fila = next(f for f in s["tabla"] if f["candidata"] == "reconsultas-p1")
        self.assertEqual(fila["cobertura"], "completa")
        self.assertEqual(fila["fallos_tito"], 2)
        self.assertEqual(fila["fallos_slm"], 1)


class TestIdentidadPreinferencia(unittest.TestCase):
    def _identidad(self, sha="a" * 64):
        return {"artefacto_sha256": sha, "manifiesto100_sha256": "f" * 64,
                "entrada": "historial_acumulado", "umbral": 0.5,
                "encoder": {"id": "e", "revision": "r"}, "variante": "#99-congelada"}

    def test_manifiesto_cierra_busqueda_antes_de_medir(self):
        man = sel102.manifiesto_busqueda(["x"], {"identidad_tito": self._identidad(),
                                                "prompt": "tarea",
                                                "prompt_huella": "h",
                                                "opciones": {"seed": 42}})
        self.assertTrue(man["busqueda_cerrada"])
        self.assertEqual(man["identidad_tito"]["artefacto_sha256"], "a" * 64)
        self.assertEqual(man["prompt_huella"], "h")
        self.assertNotIn("resultados_validacion", man)

    def test_congelar_rechaza_candidato_cambiado(self):
        man = sel102.manifiesto_busqueda(["x"], {"identidad_tito": self._identidad()})
        base = [fila_resultado("a", aviso=3)]
        s = sel102.seleccionar({sel102.BASELINE_102: base,
                                "reconsultas-p1": list(base),
                                "reconsultas-p3": list(base),
                                "reconsultas-p5": list(base)})
        cambiado = dict(self._identidad(), artefacto_sha256="b" * 64,
                        encoder_artefacto={"id": "e", "revision": "r"})
        cambiado["encoder_artefacto"] = {"id": "e", "revision": "r"}
        with self.assertRaisesRegex(ValueError, "no se congela otro candidato"):
            sel102.congelar_politica(man, s, s["ganadora"], cambiado)


class TestTrazasYRegeneracion(unittest.TestCase):
    def test_trazas_reproducen_agregados(self):
        ids = sel102.validacion_102()[:2]
        fabricas = {sel102.BASELINE_102: fabrica(sel102.BASELINE_102, {1: 0.9}),
                    "reconsultas-p3": fabrica("reconsultas-p3", {1: 0.9})}
        resultados, trazas = sel102.medir_con_fabrica_y_trazas(fabricas, ids)
        for filas in trazas.values():
            self.assertTrue(filas)
            for f in filas:
                self.assertEqual(list(f)[:1], ["config"])
        regen = sel102.agregados_desde_trazas(trazas, ids)
        self.assertEqual(regen, resultados)
        self.assertEqual(sel102.seleccionar(regen)["ganadora"],
                         sel102.seleccionar(resultados)["ganadora"])

    def test_cli_congelar_y_regenerar_con_dobles(self):
        import json
        import tempfile
        ids = sel102.validacion_102()[:2]
        fabricas = {sel102.BASELINE_102: fabrica(sel102.BASELINE_102, {1: 0.9}),
                    "reconsultas-p1": fabrica("reconsultas-p1", {1: 0.9}),
                    "reconsultas-p3": fabrica("reconsultas-p3", {1: 0.9}),
                    "reconsultas-p5": fabrica("reconsultas-p5", {1: 0.9})}
        resultados, trazas = sel102.medir_con_fabrica_y_trazas(fabricas, ids)
        sel = sel102.seleccionar(resultados)
        with tempfile.TemporaryDirectory() as tmp:
            arte = Path(tmp) / "cand.json"
            arte.write_text(json.dumps({"entrada": "historial_acumulado",
                                        "encoder": {"id": "e", "revision": "r"}}),
                            encoding="utf-8")
            tito_sha = sel102._sha_archivo(arte)
            mansel = Path(tmp) / "sel.json"
            mansel.write_text(json.dumps({"encoder": {"id": "e", "revision": "r"}}),
                              encoding="utf-8")
            man = sel102.manifiesto_busqueda(ids, {"identidad_tito": {
                "artefacto_sha256": tito_sha,
                "manifiesto100_sha256": sel102._sha_archivo(mansel),
                "entrada": "historial_acumulado", "umbral": 0.5,
                "encoder": {"id": "e", "revision": "r"}, "variante": "v"}})
            man["preinferencia"] = {"prompt_huella": "h"}
            man["resultados_validacion"] = resultados
            man["seleccion"] = sel
            man["traza_actualizaciones"] = "m_actualizaciones.csv"
            man_path = Path(tmp) / "m_manifiesto.json"
            man_path.write_text(json.dumps(man), encoding="utf-8")
            sel102.guardar_trazas_csv(sel102.ruta_trazas_csv(man_path), trazas)
            elegida = sel["ganadora"] or sel["candidata_exploratoria"]
            rc = sel102.main(["congelar", str(man_path), elegida,
                              "--tito-artefacto", str(arte),
                              "--tito-manifest", str(mansel),
                              "--variante", "v", "--salida", tmp])
            self.assertEqual(rc, 0)
            # Candidato cambiado entre medición y freeze: rechazado.
            arte.write_text(json.dumps({"entrada": "historial_acumulado",
                                        "encoder": {"id": "otro", "revision": "r"}}),
                            encoding="utf-8")
            with self.assertRaises(SystemExit):
                sel102.main(["congelar", str(man_path), elegida,
                             "--tito-artefacto", str(arte),
                             "--tito-manifest", str(mansel),
                             "--variante", "v", "--salida", tmp])
            # Regenerar desde trazas sin nueva inferencia.
            rc = sel102.main(["regenerar", str(man_path)])
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
