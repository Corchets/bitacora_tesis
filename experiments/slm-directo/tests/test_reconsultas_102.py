"""Política de reconsultas Tito→SLM con cierre y reapertura (#102, parte de #95).

Demuestra el COMPORTAMIENTO de consulta con dobles deterministas (TitoGuion
+ SLM guionado de costo fijo) sobre el recorrido existente
(`correr.procesar_caso`, aviso único y fin operativo al primer aviso válido).
No mide calidad ni ahorro: los valores de `periodo_revision`,
`regla_nueva_evidencia` y `delta_minimo` usados acá son solo el mecanismo en
marcha, no una selección.

> **Estado: propuesta sin discutir.** Las reglas y frecuencias candidatas se
> acuerdan y eligen con validación antes de medir; ver
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> Nada de lo que sigue cierra D08 ni adopta 95/5.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import correr  # noqa: E402
from casos import Linea  # noqa: E402
from detectores import Respuesta  # noqa: E402
from filtro_tito import UMBRAL_TITO, TitoGuion  # noqa: E402
from politica_reconsultas import (  # noqa: E402
    REGLA_NUEVO_CRUCE_TRAS_BAJAR,
    PoliticaReconsultas,
    visibles_para_tito,
)

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta de WhatsApp."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Para cancelar esa activación tenemos que resolverlo ahora."),
    Linea("A", "Decime el código de activación que recibiste por SMS."),
    Linea("B", "Es cero, cero, cero, cero, cero, cero."),
]

LEGITIMA = [
    Linea("A", "Me llegó por SMS un código para activar WhatsApp y yo no lo pedí."),
    Linea("B", "No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación."),
    Linea("A", "¿Necesitás verlo para ayudarme?"),
    Linea("B", "No. No hace falta que me digas ningún código."),
]


class SLMGuion:
    """SLM simulado: responde lo indicado por línea, con costo fijo y trazable."""

    def __init__(self, alertas=frozenset(), invalidas=frozenset(), errores=frozenset(),
                 ms_fijo=7.0, hablantes="ab"):
        self.alertas, self.invalidas, self.errores = (
            set(alertas), set(invalidas), set(errores))
        self.ms_fijo = ms_fijo
        self.hablantes = hablantes
        self.recibido: list[tuple[str, tuple]] = []

    def evaluar_mensaje(self, usuario, lineas):
        self.recibido.append((usuario, tuple(lineas)))
        n = len(lineas)
        if n in self.errores:
            return Respuesta(valida=False, error="ollama_caido", ms=self.ms_fijo)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido", ms=self.ms_fijo)
        alerta = n in self.alertas
        return Respuesta(
            valida=True,
            riesgo=0.9 if alerta else 0.1,
            alerta_sugerida=alerta,
            motivo="m" if alerta else "",
            ms=self.ms_fijo,
        )


def politica(puntajes=None, fallos=None, alertas=frozenset(), invalidas=frozenset(),
             errores=frozenset(), umbral=UMBRAL_TITO, periodo_revision=None,
             regla=REGLA_NUEVO_CRUCE_TRAS_BAJAR, delta_minimo=0.0):
    return PoliticaReconsultas(
        TitoGuion(puntajes, fallos),
        SLMGuion(alertas, invalidas, errores),
        umbral,
        periodo_revision=periodo_revision,
        regla_nueva_evidencia=regla,
        delta_minimo=delta_minimo,
    )


class Tito99Guion:
    """Doble con la API real de `Tito99`: `puntuar_entrada/puntuar_prefijo`.

    Sin `.puntuar`: obliga a la política a usar el historial acumulado con
    hablantes A/B. Registra cada prefijo recibido para verificar que sea
    completo, sin futuro y sin truncamiento.
    """

    nombre = "tito-99-guion"

    def __init__(self, puntajes=None, fallos=None, ms_fijo=5.0):
        self.puntajes = dict(puntajes or {})
        self.fallos = set(fallos or ())
        self.ms_fijo = ms_fijo
        self.recibido: list[tuple[str, ...]] = []

    def puntuar_entrada(self, texto_entrada):
        if texto_entrada == "__fallo__":
            return None, "tito_caido", self.ms_fijo
        return 0.0, "", self.ms_fijo

    def puntuar_prefijo(self, visibles, sintetico=False):
        self.recibido.append(tuple(visibles))
        n = len(visibles)
        if n in self.fallos:
            return None, "tito_caido", self.ms_fijo
        return self.puntajes.get(n, 0.0), "", self.ms_fijo


def politica99(puntajes=None, fallos=None, alertas=frozenset(), invalidas=frozenset(),
               errores=frozenset(), umbral=UMBRAL_TITO, periodo_revision=None,
               regla=REGLA_NUEVO_CRUCE_TRAS_BAJAR, delta_minimo=0.0):
    return PoliticaReconsultas(
        Tito99Guion(puntajes, fallos),
        SLMGuion(alertas, invalidas, errores),
        umbral,
        periodo_revision=periodo_revision,
        regla_nueva_evidencia=regla,
        delta_minimo=delta_minimo,
    )


class TestActivacionYCierre(unittest.TestCase):
    def test_bajo_el_umbral_nunca_deriva(self):
        p = politica(puntajes={1: 0.1, 2: 0.4}, alertas={1, 2, 3, 4, 5})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual([r.consulta for _, _, r, _ in salidas], ["omitida"] * 5)
        self.assertEqual(p.slm.recibido, [])
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)
        self.assertEqual([m["motivo"] for m in p.traza], ["sin_derivar"] * 5)

    def test_negativa_valida_cierra_y_no_vuelve_sin_novedad(self):
        p = politica(puntajes={1: 0.9})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "omitida", "omitida", "omitida"],
        )
        self.assertEqual(len(p.slm.recibido), 1, "la negativa válida cerró")
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)

    def test_cierre_y_reapertura_por_nuevo_cruce_sin_alerta(self):
        p = politica(puntajes={2: 0.9, 4: 0.95})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["omitida", "slm_valida", "omitida", "slm_valida", "omitida"],
        )
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)
        self.assertEqual(
            [m["motivo"] for m in p.traza],
            ["sin_derivar", "activacion_inicial", "cerrada_sin_novedad",
             "reapertura_nueva_evidencia", "cerrada_sin_novedad"],
        )
        # La reapertura conserva el indicio de la primera activación.
        for _, _, r, _ in salidas[1:]:
            self.assertEqual((r.indicio_linea, r.indicio_puntaje), (2, 0.9))

    def test_sin_bajar_no_hay_reapertura_aunque_siga_alto(self):
        p = politica(puntajes={1: 0.9, 2: 0.9, 3: 0.9})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida"] + ["omitida"] * 4,
        )
        self.assertEqual(len(p.slm.recibido), 1)


class TestPedidoRepartidoYContexto(unittest.TestCase):
    def test_cada_consulta_lleva_todo_lo_disponible_sin_futuro(self):
        p = politica(puntajes={2: 0.9, 4: 0.95}, alertas={4})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual([aviso for *_, aviso in salidas], [False, False, False, True])
        tamanos = [len(lineas) for _, lineas in p.slm.recibido]
        self.assertEqual(tamanos, [2, 4], "el pedido repartido se evalúa con contexto completo")
        primera = p.slm.recibido[0][0]
        self.assertIn("Me acaba de llegar un SMS", primera, "falta la línea disparadora")
        self.assertNotIn("cero, cero", primera, "la primera consulta vio futuro")
        segunda = p.slm.recibido[1][0]
        self.assertIn("Decime el código", segunda)
        self.assertNotIn("cero, cero", segunda, "la reapertura también vio futuro")


class TestRevisionPeriodica(unittest.TestCase):
    def test_revisa_cada_periodo_tras_el_cierre(self):
        p = politica(puntajes={1: 0.9}, periodo_revision=2)
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "slm_valida", "omitida", "slm_valida"],
        )
        self.assertEqual(
            [m["motivo"] for m in p.traza],
            ["activacion_inicial", "cerrada_sin_novedad", "revision_periodica",
             "cerrada_sin_novedad", "revision_periodica"],
        )

    def test_sin_periodo_configurado_no_hay_revision(self):
        p = politica(puntajes={1: 0.9}, periodo_revision=None)
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(len(p.slm.recibido), 1)

    def test_la_revision_no_actua_antes_de_derivar(self):
        p = politica(puntajes={3: 0.9}, periodo_revision=2)
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["omitida", "omitida", "slm_valida", "omitida", "slm_valida"],
        )

    def test_invalido_en_revision_no_cierra_y_reintenta_en_bajo(self):
        p = politica(puntajes={1: 0.9}, periodo_revision=2, invalidas={3})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "slm_fallo", "slm_valida", "omitida"],
        )
        self.assertEqual(
            [m["motivo"] for m in p.traza],
            ["activacion_inicial", "cerrada_sin_novedad", "revision_periodica",
             "abierta_sin_veredicto", "cerrada_sin_novedad"],
        )
        self.assertEqual(p.estado.ultima_consulta_linea, 4)

    def test_fallo_inicial_recuperacion_baja_y_periodica_sin_indicio(self):
        # Fallo -> SLM negativa válida cierra; recuperación baja; la
        # revisión periódica consulta sin indicio ni error actual, sin
        # assert y sin reutilizar la causa histórica como error actual.
        p = politica(fallos={1}, periodo_revision=2)
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "slm_valida", "omitida", "slm_valida"],
        )
        primera, tercera = salidas[0][2], salidas[2][2]
        self.assertEqual(primera.tito_error, "tito_caido")
        self.assertIsNone(primera.tito_puntaje)
        self.assertEqual(tercera.tito_error, "")
        self.assertIsNone(tercera.indicio_linea)
        self.assertEqual(p.estado.fallo_tito, "tito_caido",
                         "la causa histórica se conserva para trazar el fail-open")
        primera_peticion, tercera_peticion = p.slm.recibido[0][0], p.slm.recibido[1][0]
        self.assertIn("falló técnicamente (tito_caido)", primera_peticion)
        self.assertIn("sin indicio", tercera_peticion.lower())
        self.assertNotIn("falló técnicamente", tercera_peticion)
        # Tito corre en cada actualización y el costo no se duplica.
        self.assertEqual([n for n, _ in p.tito.consultas], [1, 2, 3, 4, 5])
        for _, _, r, _ in salidas:
            self.assertAlmostEqual(r.ms, (r.tito_ms or 0.0) + (r.slm_ms or 0.0))


class TestAvisoUnicoYFinOperativo(unittest.TestCase):
    def test_primera_alerta_tras_reapertura_termina_ahi(self):
        p = politica(puntajes={1: 0.9, 3: 0.9}, alertas={3})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual([aviso for *_, aviso in salidas], [False, False, True])
        self.assertEqual(len(salidas), 3, "tras el aviso no se evalúa más")
        self.assertEqual(len(p.slm.recibido), 2)

    def test_falsa_alarma_en_legitima_tambien_termina(self):
        p = politica(puntajes={1: 0.9}, alertas={1})
        salidas = list(correr.procesar_caso(p, LEGITIMA))
        self.assertEqual([aviso for *_, aviso in salidas], [True])
        self.assertEqual(len(p.slm.recibido), 1)


class TestFallos(unittest.TestCase):
    def test_fallo_de_tito_deriva_sin_fabricar_sospecha(self):
        p = politica(fallos={1}, alertas={1})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        primera = salidas[0][2]
        self.assertEqual(primera.consulta, "slm_valida")
        self.assertEqual(primera.tito_error, "tito_caido")
        self.assertIsNone(primera.tito_puntaje)
        self.assertIsNone(primera.indicio_linea)
        self.assertIn("falló técnicamente (tito_caido)", p.slm.recibido[0][0])

    def test_si_tito_se_recupera_la_politica_vuelve_a_decidir(self):
        p = politica(fallos={1})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "omitida", "omitida", "omitida"],
        )

    def test_fallo_actual_tras_cierre_vuelve_a_derivar(self):
        p = politica(puntajes={1: 0.9}, fallos={3})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "slm_valida", "omitida", "omitida"],
        )
        self.assertEqual(p.traza[2]["motivo"], "fallo_tito_deriva")

    def test_invalido_del_slm_no_cierra_y_reintenta(self):
        p = politica(puntajes={1: 0.9}, invalidas={1})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        consultas = [r.consulta for _, _, r, _ in salidas]
        self.assertEqual(consultas[0], "slm_fallo")
        # Sin veredicto válido sigue abierta: reintenta en la línea 2.
        self.assertEqual(consultas[1], "slm_valida")
        self.assertTrue(all(r.valida or r.consulta == "slm_fallo" for _, _, r, _ in salidas))
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)

    def test_error_del_slm_no_cierra_y_reintenta(self):
        p = politica(puntajes={1: 0.9}, errores={1})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(salidas[0][2].consulta, "slm_fallo")
        self.assertEqual(salidas[0][2].error, "ollama_caido")
        self.assertEqual(salidas[1][2].consulta, "slm_valida")
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)

    def test_invalido_en_reapertura_no_cierra_y_reintenta_en_bajo(self):
        # L1 alto + SLM negativo válido cierra; L2 bajo arma evidencia;
        # L3 nuevo cruce + SLM inválido NO cierra; L4 bajo consulta igual.
        p = politica(puntajes={1: 0.9, 3: 0.9}, invalidas={3})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["slm_valida", "omitida", "slm_fallo", "slm_valida", "omitida"],
        )
        self.assertEqual(
            [m["motivo"] for m in p.traza],
            ["activacion_inicial", "cerrada_sin_novedad",
             "reapertura_nueva_evidencia", "abierta_sin_veredicto",
             "cerrada_sin_novedad"],
        )
        # El reloj no se resetea con la respuesta inválida: la válida de
        # L4 es la que vuelve a cerrar.
        self.assertEqual(p.estado.ultima_consulta_linea, 4)
        self.assertTrue(p.estado.cerrada)
        self.assertEqual(salidas[3][2].tito_error, "")

    def test_fallo_con_slm_invalido_queda_abierto_y_reintenta(self):
        p = politica(fallos={1}, invalidas={1})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(salidas[0][2].consulta, "slm_fallo")
        self.assertEqual(salidas[1][2].consulta, "slm_valida")
        self.assertFalse(p.traza[0]["cerrada"])


class TestAislamientoYTraza(unittest.TestCase):
    def test_reiniciar_entre_llamadas_via_procesar_caso(self):
        p = politica(puntajes={1: 0.9}, alertas={1})
        primera = list(correr.procesar_caso(p, DIALOGO))
        segunda = list(correr.procesar_caso(p, LEGITIMA))
        self.assertEqual([aviso for *_, aviso in primera].count(True), 1)
        self.assertEqual([aviso for *_, aviso in segunda].count(True), 1)
        self.assertEqual(segunda[0][2].consulta, "slm_valida")
        self.assertEqual(segunda[0][2].indicio_linea, 1)
        self.assertIn(LEGITIMA[0].texto, p.slm.recibido[len(primera)][0])
        self.assertEqual([m["linea"] for m in p.traza], [1], "la legítima avisó en L1 y terminó")

    def test_traza_cubre_cada_actualizacion_en_orden(self):
        p = politica(puntajes={2: 0.9, 4: 0.95})
        list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual([m["linea"] for m in p.traza], [1, 2, 3, 4, 5])
        self.assertEqual(
            [m["consulta"] for m in p.traza],
            ["omitida", "slm_valida", "omitida", "slm_valida", "omitida"],
        )
        self.assertEqual(p.ultimo_motivo, "cerrada_sin_novedad")


class TestConteoDeTito(unittest.TestCase):
    def test_tito_corre_en_cada_actualizacion_incluso_cerrada(self):
        p = politica(puntajes={1: 0.9})
        list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual([n for n, _ in p.tito.consultas], [1, 2, 3, 4, 5])
        self.assertIsNotNone(p.estado.ultima_consulta_linea)

    def test_costo_suma_sin_doble_conteo(self):
        p = politica(puntajes={1: 0.9})
        p.slm.ms_fijo = 7.0
        salidas = list(correr.procesar_caso(p, DIALOGO))
        filas = [r for _, _, r, _ in salidas]
        # L1: 5,0 + 7,0; L2–L5: solo Tito, 5,0 cada una (SLM cerrado).
        self.assertEqual([(r.tito_ms, r.slm_ms) for r in filas],
                         [(5.0, 7.0), (5.0, None), (5.0, None), (5.0, None), (5.0, None)])
        for r in filas:
            self.assertAlmostEqual(r.ms, (r.tito_ms or 0.0) + (r.slm_ms or 0.0))
        self.assertAlmostEqual(sum(r.ms for r in filas), 12.0 + 5.0 * 4)
        self.assertAlmostEqual(
            sum(r.ms for r in filas),
            sum(r.tito_ms or 0.0 for r in filas) + sum(r.slm_ms or 0.0 for r in filas),
        )

    def test_config_invalida_se_rechaza_en_texto_plano(self):
        with self.assertRaises(ValueError):
            politica(periodo_revision=0)
        with self.assertRaises(ValueError):
            politica(periodo_revision=True)
        with self.assertRaises(ValueError):
            politica(periodo_revision=2.0)
        with self.assertRaises(ValueError):
            politica(periodo_revision="2")
        with self.assertRaises(ValueError):
            politica(periodo_revision=2, regla="otra_regla")
        with self.assertRaises(ValueError):
            politica(periodo_revision=2, delta_minimo=-0.1)
        with self.assertRaises(ValueError):
            politica(periodo_revision=2, delta_minimo=True)
        with self.assertRaises(ValueError):
            politica(periodo_revision=2, delta_minimo=float("nan"))
        with self.assertRaises(ValueError):
            politica(periodo_revision=2, delta_minimo=float("inf"))
        with self.assertRaises(ValueError):
            politica(periodo_revision=2, delta_minimo="0.1")


class TestTitoHistorial(unittest.TestCase):
    def test_prefijo_completo_con_hablantes_y_sin_futuro(self):
        p = politica99(puntajes={2: 0.9})
        salidas = list(correr.procesar_caso(p, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["omitida", "slm_valida", "omitida", "omitida", "omitida"],
        )
        esperado_l1 = (f"A: {DIALOGO[0].texto}",)
        esperado_l2 = (f"A: {DIALOGO[0].texto}", f"B: {DIALOGO[1].texto}")
        self.assertEqual(p.tito.recibido[0], esperado_l1)
        self.assertEqual(p.tito.recibido[1], esperado_l2)
        self.assertNotIn(DIALOGO[2].texto, p.tito.recibido[1][0] + p.tito.recibido[1][1])
        self.assertEqual([len(v) for v in p.tito.recibido], [1, 2, 3, 4, 5])
        self.assertEqual(visibles_para_tito(DIALOGO[:2]), list(esperado_l2))

    def test_historial_reinicia_entre_llamadas(self):
        p = politica99(puntajes={1: 0.9}, alertas={1})
        primera = list(correr.procesar_caso(p, DIALOGO))
        base = len(p.tito.recibido)
        segunda = list(correr.procesar_caso(p, LEGITIMA))
        self.assertEqual([aviso for *_, aviso in primera].count(True), 1)
        self.assertEqual([aviso for *_, aviso in segunda].count(True), 1)
        self.assertEqual(len(p.tito.recibido), base + 1)
        self.assertEqual(p.tito.recibido[base], (f"A: {LEGITIMA[0].texto}",))
        self.assertNotIn(DIALOGO[0].texto, p.tito.recibido[base][0])

    def test_mismo_cierre_con_historial_y_frase(self):
        p99 = politica99(puntajes={1: 0.9})
        pfr = politica(puntajes={1: 0.9})
        s99 = list(correr.procesar_caso(p99, DIALOGO))
        sfr = list(correr.procesar_caso(pfr, DIALOGO))
        self.assertEqual([r.consulta for _, _, r, _ in s99],
                         [r.consulta for _, _, r, _ in sfr])


if __name__ == "__main__":
    unittest.main()
