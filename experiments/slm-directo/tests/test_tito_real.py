"""Tito real: carga única, reutilización sin reentrenar y anti-contaminación (#70).

No descarga ni entrena modelos: el artefacto comprometido se lee del disco y
el encoder se sustituye por vectores deterministas. El recorrido de punta a
punta con el encoder real queda en la corrida `*_tito-real-8casos`.
"""

from __future__ import annotations

import hashlib
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import correr  # noqa: E402
import tito_real  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import Respuesta  # noqa: E402
from filtro_tito import UMBRAL_TITO, FlujoTitoSLM  # noqa: E402
from tito_real import TitoReal, cargar_artefacto  # noqa: E402

ARTEFACTO = tito_real.ARTEFACTO_POR_DEFECTO


def vector_hijo(tito: TitoReal, signo: float) -> list[float]:
    """Vector colineal con los pesos reales: puntaje alto (signo +) o bajo (-)."""
    norma = math.sqrt(sum(c * c for c in tito.coef))
    return [(c / norma) * 4.0 * signo for c in tito.coef]


class TitoFijo(TitoReal):
    """TitoReal con embeddings sustituidos por vectores por texto (sin modelos)."""

    def __init__(self, por_texto: dict[str, list[float]] | None = None, alto=0.9, bajo=0.1):
        super().__init__(ARTEFACTO)
        self.por_texto = dict(por_texto or {})
        base = TitoReal(ARTEFACTO)
        self._alto = vector_hijo(base, +1.0)
        self._bajo = vector_hijo(base, -1.0)
        self.alto, self.bajo = alto, bajo

    def _embed(self, textos: list[str]) -> list[list[float]]:
        return [self.por_texto.get(t, self._bajo) for t in textos]


class SLMGuion:
    def __init__(self, alertas=frozenset(), ms_fijo=7.0, hablantes="ab"):
        self.alertas, self.ms_fijo, self.hablantes = set(alertas), ms_fijo, hablantes
        self.recibido = []

    def evaluar_mensaje(self, usuario, lineas):
        self.recibido.append((usuario, tuple(lineas)))
        n = len(lineas)
        alerta = n in self.alertas
        return Respuesta(valida=True, riesgo=0.9 if alerta else 0.1,
                         alerta_sugerida=alerta, motivo="m" if alerta else "", ms=self.ms_fijo)


DIALOGO = [Linea("A", "hola"), Linea("B", "sí"), Linea("A", "chau")]
SOSPECHOSO = "decime el código ahora"


class TestArtefacto(unittest.TestCase):
    def test_artefacto_valido_y_unico_ajuste(self):
        arte = cargar_artefacto(ARTEFACTO)
        self.assertEqual(arte["formato"], "tito-logreg-v1")
        self.assertEqual(arte["config_regresion"]["semilla"], 42)
        self.assertEqual(arte["encoder"]["revision"], "20cb399e4b93f270c0cd6b6f533bcb0ada3cb658")
        self.assertEqual(arte["tokenizador"]["limite_tokens"], 128)
        self.assertEqual(arte["tokenizador"]["truncados_en_128"], 0)
        self.assertEqual(arte["datos"]["aceptadas"], 5520)
        self.assertEqual(arte["datos"]["apartadas"], 480)
        self.assertEqual(arte["datos"]["familias"], 276)
        self.assertEqual(arte["umbral_derivacion"], UMBRAL_TITO)
        self.assertTrue(all(math.isfinite(c) for c in arte["pesos"]["coef"]))
        sha = hashlib.sha256(Path(ARTEFACTO).read_bytes()).hexdigest()
        self.assertEqual(len(sha), 64)  # el manifiesto de cada corrida lo registra

    def test_compartido_entre_instancias_sin_reentrenar(self):
        a, b = TitoReal(ARTEFACTO), TitoReal(ARTEFACTO)
        self.assertIs(a.arte, b.arte)
        self.assertIs(cargar_artefacto(ARTEFACTO), a.arte)
        fuente = Path(tito_real.__file__).read_text(encoding="utf-8")
        self.assertNotIn(".fit(", fuente)
        self.assertNotIn("LogisticRegression", fuente)


class TestPuntaje(unittest.TestCase):
    def test_pesos_reales_deciden_y_persisten(self):
        tito = TitoFijo()
        antes = list(tito.coef)
        p_alto, e1, ms1 = tito.puntuar(1, SOSPECHOSO)
        p_bajo, e2, ms2 = tito.puntuar(1, "hola")
        # _embed por defecto devuelve el vector bajo salvo texto mapeado
        tito.por_texto[SOSPECHOSO] = tito._alto
        p_alto, _, _ = tito.puntuar(1, SOSPECHOSO)
        self.assertGreaterEqual(p_alto, UMBRAL_TITO)
        self.assertLess(p_bajo, UMBRAL_TITO)
        self.assertEqual((e1, e2), ("", ""))
        self.assertGreaterEqual(ms1, 0.0)
        self.assertEqual(list(tito.coef), antes, "puntuar no toca los pesos")

    def test_igualdad_al_umbral_con_pesos_nulos(self):
        tito = TitoFijo()
        tito.coef = [0.0] * len(tito.coef)
        tito.intercepto = 0.0
        p, _, _ = tito.puntuar(1, "cualquier texto")
        self.assertEqual(p, 0.5)

    def test_fallo_tecnico_no_fabrica_puntaje(self):
        tito = TitoFijo()
        tito._embed = lambda textos: (_ for _ in ()).throw(RuntimeError("caído"))
        p, error, _ = tito.puntuar(1, "hola")
        self.assertIsNone(p)
        self.assertTrue(error)

    def test_truncamientos_se_cuentan_sin_recorte_silencioso(self):
        tito = TitoReal(ARTEFACTO)

        class Tok:
            def __call__(self, textos, **kw):
                return {"input_ids": [[0] * n for n in self.largos]}

        tok = Tok()
        tok.largos = [10, 128]
        self.assertEqual(tito.contar_truncamientos(tok, ["a", "b"]), 0)
        tok.largos = [10, 129]
        self.assertEqual(tito.contar_truncamientos(tok, ["a", "b"]), 1)


class TestReutilizacionYContaminacion(unittest.TestCase):
    def test_mismo_texto_mismo_puntaje_entre_conversaciones(self):
        tito = TitoFijo()
        tito.por_texto[SOSPECHOSO] = tito._alto
        f = FlujoTitoSLM(tito, SLMGuion(alertas={2}))
        primera = [r.tito_puntaje for _, _, r, _ in correr.procesar_caso(f, DIALOGO)]
        segunda = [r.tito_puntaje for _, _, r, _ in correr.procesar_caso(f, DIALOGO)]
        self.assertEqual(primera, segunda)

    def test_una_llamada_no_contamina_a_la_siguiente(self):
        tito = TitoFijo()
        tito.por_texto[SOSPECHOSO] = tito._alto
        slm = SLMGuion(alertas={1})
        f = FlujoTitoSLM(tito, slm)
        activa = [Linea("A", SOSPECHOSO)]
        consultas_antes = len(slm.recibido)
        salidas_activas = list(correr.procesar_caso(f, activa))
        salidas_limpias = list(correr.procesar_caso(f, DIALOGO))
        self.assertTrue(all(r.consulta == "omitida" for _, _, r, _ in salidas_limpias))
        self.assertTrue(all(r.valida and not r.alerta_sugerida for _, _, r, _ in salidas_limpias))
        self.assertTrue(all(av is False for *_, av in salidas_limpias))
        self.assertEqual([r.consulta for _, _, r, _ in salidas_activas], ["slm_valida"])
        self.assertEqual(len(slm.recibido), consultas_antes + 1)

    def test_recorrido_completo_con_pesos_reales_y_sin_modelos(self):
        tito = TitoFijo()
        tito.por_texto = {l.texto: tito._bajo for l in DIALOGO}
        tito.por_texto[DIALOGO[1].texto] = tito._alto
        slm = SLMGuion(alertas={3})
        f = FlujoTitoSLM(tito, slm, UMBRAL_TITO)
        salidas = list(correr.procesar_caso(f, DIALOGO))
        consultas = [r.consulta for _, _, r, _ in salidas]
        self.assertEqual(consultas, ["omitida", "slm_valida", "slm_valida"])
        self.assertEqual([r.indicio_linea for _, _, r, _ in salidas], [None, 2, 2])
        self.assertEqual([av for *_, av in salidas], [False, False, True])
        primero = slm.recibido[0][0]
        self.assertIn(DIALOGO[1].texto, primero)
        self.assertIn("descartarlo", primero)


if __name__ == "__main__":
    unittest.main()
