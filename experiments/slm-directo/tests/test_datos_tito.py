"""Recorrido datos -> validación para Tito (#96, parte de #95).

Pruebas de comportamiento con dobles deterministas: verifican qué acepta o
rechaza el recorrido, qué etiqueta ve cada actualización y qué informe sale.
No descargan modelos, no leen la reserva ni tocan git.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import datos_tito as dt  # noqa: E402


def dialogo(*textos):
    return tuple(dt.Linea("A" if i % 2 == 0 else "B", t)
                 for i, t in enumerate(textos))


def referencia_vishing(t_r=3, t_c=4):
    return dt.Referencia(
        clase="vishing", t_r_linea=t_r, t_c_linea=t_c,
        pedido="REQUEST_AUTH_CODE",
        evidencia=(
            {"linea": 1, "evento": "contexto", "etiquetas": ["AUTHORITY_CLAIM"]},
            {"linea": t_r, "evento": "pedido", "etiquetas": ["REQUEST_AUTH_CODE"]},
            {"linea": t_c, "evento": "cumplimiento", "etiquetas": []},
        ),
        revision_humana=False)


def conversacion(cid, *textos, semilla=None, familia=None, modalidad=None,
                 dificultades=(), ref=None):
    return dt.Conversacion(
        case_id=cid, lineas=dialogo(*textos),
        referencia=ref if ref is not None else referencia_vishing(),
        semilla=semilla, familia_variante=familia, modalidad=modalidad,
        dificultades=tuple(dificultades))


class TestInventario(unittest.TestCase):
    def test_distingue_familias_de_variantes_de_modalidades_amplias(self):
        registros = [
            {"id": "b1", "familia": "banco_001", "lote": "banco",
             "etiqueta": "estafa", "fuentes": ["banco_F01"]},
            {"id": "b2", "familia": "banco_001", "lote": "banco",
             "etiqueta": "estafa", "fuentes": ["banco_F01", "banco_F02"]},
            {"id": "c1", "familia": "cotidiano_002", "lote": "cotidiano",
             "etiqueta": "legitima", "fuentes": ["cot_F01"]},
        ]
        inv = dt.inventariar_banco(registros, {"cotidiano_002": "ambiguo"},
                                   {"banco_commit": "abc"})
        self.assertEqual(inv["versiones"]["aceptados"], 2)
        self.assertEqual(inv["versiones"]["apartados"], 1)
        self.assertEqual(inv["familias_variante"], ["banco_001"])
        self.assertEqual(inv["modalidades"], ["banco"])
        self.assertEqual(inv["exclusiones"], {"cotidiano_002": "ambiguo"})
        self.assertEqual(inv["relaciones_sematicas"]["fuente_a_familias"]["banco_F01"],
                         ["banco_001"])


class TestPrefijos(unittest.TestCase):
    def test_un_sufijo_futuro_no_altera_la_etiqueta_del_prefijo(self):
        base = conversacion("C1", "hola", "qué tal", "decime el código", "listo")
        etiqueta_antes = dt.etiquetar_prefijo(base, 2)
        mutada = conversacion("C1", "hola", "qué tal", "decime el código",
                              "te transferí todo y te doy mi clave")
        etiqueta_despues = dt.etiquetar_prefijo(mutada, 2)
        self.assertEqual(etiqueta_antes["supervision"], "indicio_parcial")
        self.assertEqual(etiqueta_antes, etiqueta_despues)

    def test_no_copia_la_clase_final_a_los_fragmentos(self):
        conv = conversacion("V1", "llamo del banco", "dígame",
                            "decime el código", "ahí va")
        previa = dt.etiquetar_prefijo(conv, 2)
        self.assertEqual(previa["clase_conversacion"], "vishing")
        self.assertEqual(previa["supervision"], "indicio_parcial")
        self.assertIsNone(previa["marcas"]["pedido"])
        sin_nada = dt.Conversacion(
            case_id="V0", lineas=dialogo("hola", "qué tal", "decime el código"),
            referencia=dt.Referencia(
                clase="vishing", t_r_linea=3, pedido="REQUEST_AUTH_CODE",
                evidencia=({"linea": 3, "evento": "pedido",
                            "etiquetas": ["REQUEST_AUTH_CODE"]},)))
        self.assertEqual(dt.etiquetar_prefijo(sin_nada, 1)["supervision"],
                         "sin_evidencia_suficiente")
        en_pedido = dt.etiquetar_prefijo(conv, 3)
        self.assertEqual(en_pedido["supervision"], "pedido_visible")
        self.assertEqual(en_pedido["marcas"]["pedido"], "REQUEST_AUTH_CODE")
        cumplida = dt.etiquetar_prefijo(conv, 4)
        self.assertEqual(cumplida["supervision"], "cumplimiento_visible")

    def test_sin_referencia_no_hay_supervision_utilizable(self):
        conv = dt.Conversacion(case_id="S1", lineas=dialogo("hola", "chau"),
                               referencia=None)
        etiqueta = dt.etiquetar_prefijo(conv, 1)
        self.assertEqual(etiqueta["supervision"], "sin_evidencia_suficiente")
        self.assertTrue(etiqueta["provisional"])

    def test_ventana_reciente_no_arrastra_otra_conversacion(self):
        a = conversacion("A", "secreto bancario", "dato", "otro", "más")
        b = conversacion("B", "hola", "chau")
        prefijos = dt.construir_prefijos(a, ventana=2)
        self.assertEqual(len(prefijos), 4)
        self.assertEqual([len(p.visible) for p in prefijos], [1, 2, 2, 2])
        self.assertTrue(all(p.case_id == "A" for p in prefijos))
        textos = [l.texto for p in prefijos for l in p.visible]
        self.assertNotIn("hola", textos)
        completos = dt.construir_prefijos(b)
        self.assertEqual(len(completos[1].visible), 2)

    def test_truncamiento_se_registra_no_se_recorta_en_silencio(self):
        conv = conversacion("T", "x" * 100, "y" * 100)
        sin_limite = dt.construir_prefijos(conv)
        self.assertFalse(any(p.truncado for p in sin_limite))
        con_limite = dt.construir_prefijos(conv, limite_tokens=10)
        self.assertTrue(all(p.truncado for p in con_limite))

    def test_ventana_invalida_se_rechaza(self):
        with self.assertRaises(ValueError):
            dt.construir_prefijos(conversacion("V", "hola"), ventana=0)


class TestParticiones(unittest.TestCase):
    def test_semilla_familia_y_par_no_cruzan_particiones(self):
        convs = [
            conversacion("E1", "llamo del banco uno", "dígame uno",
                         "decime el código uno", "ahí va uno",
                         semilla="S-1", familia="banco_001", modalidad="banco"),
            conversacion("E2", "llamo del banco dos", "dígame dos",
                         "decime el código dos", "ahí va dos",
                         semilla="S-1", familia="banco_001", modalidad="banco"),
        ]
        informe = dt.validar_particiones(
            convs, {"E1": "entrenamiento", "E2": "evaluacion_independiente"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("semilla 'S-1' cruza" in e for e in informe.errores))
        self.assertTrue(any("familia_variante 'banco_001' cruza" in e
                            for e in informe.errores))

    def test_par_cruzado_se_rechaza(self):
        ref_a = dt.Referencia(clase="vishing", t_r_linea=2, t_c_linea=None,
                              pedido="REQUEST_AUTH_CODE",
                              evidencia=({"linea": 1, "evento": "contexto",
                                          "etiquetas": []},
                                         {"linea": 2, "evento": "pedido",
                                          "etiquetas": ["REQUEST_AUTH_CODE"]}),
                              par="B1")
        a = conversacion("A1", "ataque telefónico alfa", "respuesta alfa", ref=ref_a)
        b = conversacion("B1", "consulta cotidiana beta", "respuesta beta",
                         ref=dt.Referencia(clase="legitima",
                                           evidencia=({"linea": 1, "evento": "contexto",
                                                       "etiquetas": []},)))
        informe = dt.validar_particiones(
            [a, b], {"A1": "entrenamiento", "B1": "validacion"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("par 'B1' cruza" in e or 'par' in e and 'cruza' in e
                            for e in informe.errores))

    def test_referencia_faltante_y_ambigua_no_son_evaluables(self):
        sin_ref = dt.Conversacion(case_id="R0", lineas=dialogo("hola mundo", "chau mundo"),
                                  referencia=None)
        ambigua = conversacion(
            "R1", "consulta legítima gama", "respuesta gama",
            ref=dt.Referencia(clase="legitima", t_r_linea=2,
                              evidencia=({"linea": 1, "evento": "contexto",
                                          "etiquetas": []},)))
        informe = dt.validar_particiones(
            [sin_ref, ambigua], {"R0": "entrenamiento", "R1": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("R0" in e and "falta referencia" in e for e in informe.errores))
        self.assertTrue(any("R1" in e and "ambigua" in e for e in informe.errores))

    def test_duplicado_incompatible_entre_particiones_se_rechaza(self):
        ref_v = referencia_vishing()
        ref_l = dt.Referencia(clase="legitima",
                              evidencia=({"linea": 1, "evento": "contexto",
                                          "etiquetas": []},))
        a = conversacion("D1", "texto duplicado exacto", "cierre uno", ref=ref_v)
        b = dt.Conversacion(case_id="D2",
                            lineas=dialogo("texto duplicado exacto", "cierre dos"),
                            referencia=ref_l)
        informe = dt.validar_particiones(
            [a, b], {"D1": "entrenamiento", "D2": "evaluacion_independiente"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("duplicado incompatible" in e for e in informe.errores))

    def test_banco_del_artefacto_actual_no_se_recicla_como_evaluacion(self):
        a = conversacion("H1", "banco histórico alfa", "réplica alfa",
                         "pedido alfa código", "cierre alfa",
                         familia="banco_001", modalidad="banco")
        b = conversacion("H2", "banco histórico beta", "réplica beta",
                         "pedido beta código", "cierre beta",
                         familia="banco_001", modalidad="banco")
        informe = dt.validar_particiones(
            [a, b], {"H1": "entrenamiento", "H2": "evaluacion_independiente"},
            familias_artefacto={"banco_001"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("retrospectivamente" in e for e in informe.errores))


class TestReserva(unittest.TestCase):
    def test_rechaza_identificadores_y_particion_de_reserva_sin_leerla(self):
        with self.assertRaisesRegex(ValueError, "Reserva del proyecto"):
            dt.rechazar_reserva(["CV2-D-algo-001", "CV2-T-algo-001"])
        with self.assertRaisesRegex(ValueError, "Reserva del proyecto"):
            dt.rechazar_reserva(["D1"], {"D1": "test_reservado"})
        dt.rechazar_reserva(["CV2-D-algo-001"], {"CV2-D-algo-001": "desarrollo"})

    def test_validar_particiones_tampoco_acepta_reserva(self):
        conv = conversacion("CV2-T-X-001", "hola reserva", "chau reserva")
        informe = dt.validar_particiones(
            [conv], {"CV2-T-X-001": "evaluacion_independiente"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("reserva" in e for e in informe.errores))


class TestRegresionYSeparacion(unittest.TestCase):
    def test_las_ocho_historicas_se_marcan_como_regresion(self):
        marcas = dt.marcar_regresiones(list(dt.REGRESION_OCHO) + ["NUEVO-01"])
        self.assertEqual(len(dt.REGRESION_OCHO), 8)
        self.assertTrue(all(v == "regresion" for k, v in marcas.items()
                            if k != "NUEVO-01"))
        self.assertEqual(marcas["NUEVO-01"], "no_regresion")

    def test_evaluacion_separada_de_diagnostico_y_ajuste(self):
        self.assertEqual(dt.verificar_separacion_diagnostico(
            {"A"}, {"B"}, {"C"}), [])
        errores = dt.verificar_separacion_diagnostico({"A"}, {"A"}, {"C"})
        self.assertTrue(any("diagnóstico" in e for e in errores))
        errores = dt.verificar_separacion_diagnostico({"X"}, {"C"}, {"C"})
        self.assertTrue(any("ajuste" in e for e in errores))


class TestCobertura(unittest.TestCase):
    def test_informa_presentes_y_ausentes_sin_inventar(self):
        convs = [conversacion("C1", "negación firme uno", "cierre uno",
                              dificultades=("negacion", "cita"))]
        cob = dt.cobertura_muestra(convs)
        self.assertEqual(cob["presentes"]["negacion"], ["C1"])
        self.assertIn("pedido_indirecto", cob["ausentes"])
        self.assertTrue(any("no se infiere" in l for l in cob["limites"]))


class TestManifiestoEHabilitacion(unittest.TestCase):
    def armar_recorrido(self):
        convs = [
            conversacion("M1", "banco m uno", "réplica m uno",
                         "pedido m uno código", "cierre m uno",
                         semilla="SM-1", familia="f_m1", modalidad="banco",
                         dificultades=("pedido_indirecto",)),
            conversacion("M2", "banco m dos", "réplica m dos",
                         "pedido m dos código", "cierre m dos",
                         semilla="SM-2", familia="f_m2", modalidad="banco",
                         dificultades=("negacion",)),
        ]
        asignacion = {"M1": "entrenamiento", "M2": "validacion"}
        return convs, asignacion

    def test_recorrido_valido_genera_manifiesto_reproducible_pero_no_habilitado(self):
        convs, asignacion = self.armar_recorrido()
        prefijos = [p for c in convs for p in dt.construir_prefijos(c, ventana=2)]
        self.assertTrue(all(p.visible for p in prefijos))
        informe = dt.validar_particiones(convs, asignacion)
        self.assertTrue(informe.es_evaluable, informe.errores)
        man1 = dt.generar_manifiesto({"origen": "doble"}, {"ventana": 2},
                                     asignacion, convs)
        man2 = dt.generar_manifiesto({"origen": "doble"}, {"ventana": 2},
                                     asignacion, convs)
        self.assertEqual(man1, man2)
        self.assertEqual(man1["estado"], "propuesta sin discutir")
        self.assertEqual(man1["decisiones_pendientes"], ["D07", "D08"])
        self.assertIn("M1", man1["huellas_conversaciones"])
        salida = dt.informe_validacion(man1, informe, dt.cobertura_muestra(convs))
        self.assertTrue(salida["es_evaluable"])
        self.assertFalse(salida["habilitado"])
        self.assertIn("bloqueo", salida)

    def test_habilitacion_bloqueada_sin_revision_ni_acuerdo(self):
        convs, asignacion = self.armar_recorrido()
        informe = dt.validar_particiones(convs, asignacion)
        man = dt.generar_manifiesto({"origen": "doble"}, {}, asignacion, convs)
        salida = dt.informe_validacion(man, informe, dt.cobertura_muestra(convs))
        ok, motivos = dt.puede_habilitarse(salida)
        self.assertFalse(ok)
        self.assertTrue(any("revisión humana" in m for m in motivos))
        self.assertTrue(any("acuerdo" in m for m in motivos))
        ok, _ = dt.puede_habilitarse(
            salida, revision_efectiva={"revisores": ["equipo"]},
            acuerdo={"composicion": "acordada"})
        self.assertTrue(ok)

    def test_particion_invalida_tampoco_se_habilita_con_acuerdo(self):
        convs, _ = self.armar_recorrido()
        informe = dt.validar_particiones(convs, {"M1": "entrenamiento"})
        salida = dt.informe_validacion({}, informe, {})
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva={"revisores": ["equipo"]},
            acuerdo={"composicion": "acordada"})
        self.assertFalse(ok)
        self.assertTrue(any("inválidas" in m for m in motivos))


if __name__ == "__main__":
    unittest.main()
