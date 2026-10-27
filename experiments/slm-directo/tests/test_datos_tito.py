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
        ref_v = dt.Referencia(
            clase="vishing", t_r_linea=1, t_c_linea=2,
            pedido="REQUEST_AUTH_CODE",
            evidencia=({"linea": 1, "evento": "pedido",
                        "etiquetas": ["REQUEST_AUTH_CODE"]},
                       {"linea": 2, "evento": "cumplimiento",
                        "etiquetas": []}))
        ref_l = dt.Referencia(clase="legitima",
                              evidencia=({"linea": 1, "evento": "contexto",
                                          "etiquetas": []},))
        a = dt.Conversacion(case_id="D1",
                            lineas=dialogo("texto duplicado exacto", "cierre común"),
                            referencia=ref_v)
        b = dt.Conversacion(case_id="D2",
                            lineas=dialogo("texto duplicado exacto", "cierre común"),
                            referencia=ref_l)
        informe = dt.validar_particiones(
            [a, b], {"D1": "entrenamiento", "D2": "evaluacion_independiente"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("conversación completa duplicada" in e
                            for e in informe.errores))
        self.assertTrue(any("conflicto de referencia" in e
                            for e in informe.errores))

    def test_duplicada_completa_con_misma_clase_tambien_se_rechaza(self):
        a = conversacion("G1", "diálogo repetido entero", "segunda línea",
                         "decime el código", "ahí va")
        b = conversacion("G2", "diálogo repetido entero", "segunda línea",
                         "decime el código", "ahí va")
        informe = dt.validar_particiones(
            [a, b], {"G1": "entrenamiento", "G2": "evaluacion_independiente"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("conversación completa duplicada" in e
                            for e in informe.errores))

    def test_saludo_repetido_en_llamadas_distintas_no_es_duplicado(self):
        a = conversacion("S1", "hola", "llamo del banco alfa",
                         "decime el código", "cierre alfa")
        b = conversacion("S2", "hola", "consulta vecinal beta",
                         "respuesta beta", "cierre beta",
                         ref=dt.Referencia(
                             clase="legitima",
                             evidencia=({"linea": 1, "evento": "contexto",
                                         "etiquetas": []},)))
        informe = dt.validar_particiones(
            [a, b], {"S1": "entrenamiento", "S2": "evaluacion_independiente"})
        self.assertTrue(informe.es_evaluable, informe.errores)

    def test_identificadores_duplicados_se_rechazan_antes_del_diccionario(self):
        a = conversacion("X1", "diálogo único uno", "cierre uno",
                         "decime el código uno", "listo uno")
        b = conversacion("X1", "diálogo único dos", "cierre dos",
                         "decime el código dos", "listo dos")
        informe = dt.validar_particiones([a, b], {"X1": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("identificador duplicado" in e
                            for e in informe.errores))

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
        ok, motivos = dt.puede_habilitarse(salida, {}, {})
        self.assertFalse(ok)
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva={"revisores": ["equipo"]},
            acuerdo={"composicion": "acordada"})
        self.assertFalse(ok)

    def test_particion_invalida_tampoco_se_habilita_con_acuerdo(self):
        convs, _ = self.armar_recorrido()
        informe = dt.validar_particiones(convs, {"M1": "entrenamiento"})
        salida = dt.informe_validacion({}, informe, {})
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva={"revisores": ["equipo"]},
            acuerdo={"composicion": "acordada"})
        self.assertFalse(ok)
        self.assertTrue(any("inválidas" in m for m in motivos))


def revision_trazable(total=2):
    return {
        "revisores": ["Lucía Ferraro", "Marco Benítez"],
        "originales_conservados": True,
        "originales_referencia": "docs/corpus/PLANILLA-REVISION-TOMAS.csv",
        "desacuerdos": [{"caso": "M1", "punto": "alcance del pedido",
                         "posturas": ["amplia", "restringida"]}],
        "adjudicaciones": [{"caso": "M1", "decision": "restringida",
                            "quien": "Lucía Ferraro"}],
        "referencias_revisadas": {"revisadas": total, "total": total},
    }


def acuerdo_efectivo():
    return {
        "composicion": "entrenamiento cuatro, validación dos, resto a acordar",
        "tamano": {"entrenamiento": 4, "validacion": 2},
        "reglas_referencia": "MANUAL-ANOTACION.md versión de trabajo 2026-10-27",
        "proporciones": {"vishing": "una mitad", "legitima": "otra mitad"},
    }


class TestVocabularioYRangos(unittest.TestCase):
    def test_clase_inventada_rango_y_pedido_fuera_de_vocabulario(self):
        ref = dt.Referencia(
            clase="clase_inventada", t_r_linea=999, pedido="X",
            evidencia=({"linea": 999, "evento": "pedido",
                        "etiquetas": ["Y"]},))
        conv = dt.Conversacion(case_id="BUG1", lineas=dialogo("hola"),
                               referencia=ref)
        informe = dt.validar_particiones([conv], {"BUG1": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        texto = "\n".join(informe.errores)
        self.assertIn("fuera del vocabulario", texto)
        self.assertIn("fuera del diálogo", texto)
        self.assertIn("REQUEST_*", texto)

    def test_t_c_sin_pedido_orden_y_cumplimiento_se_rechazan(self):
        base = ("primera línea", "segunda línea", "tercera línea")
        sin_tr = dt.Referencia(
            clase="vishing", t_c_linea=2, pedido="REQUEST_AUTH_CODE",
            evidencia=({"linea": 2, "evento": "cumplimiento",
                        "etiquetas": []},))
        invertido = dt.Referencia(
            clase="vishing", t_r_linea=3, t_c_linea=2,
            pedido="REQUEST_AUTH_CODE",
            evidencia=({"linea": 3, "evento": "pedido",
                        "etiquetas": ["REQUEST_AUTH_CODE"]},
                       {"linea": 2, "evento": "cumplimiento",
                        "etiquetas": []}))
        sin_cumplimiento = dt.Referencia(
            clase="vishing", t_r_linea=2, t_c_linea=3,
            pedido="REQUEST_AUTH_CODE",
            evidencia=({"linea": 2, "evento": "pedido",
                        "etiquetas": ["REQUEST_AUTH_CODE"]},))
        for cid, ref in (("T1", sin_tr), ("T2", invertido), ("T3", sin_cumplimiento)):
            with self.subTest(cid=cid):
                conv = dt.Conversacion(case_id=cid, lineas=dialogo(*base),
                                       referencia=ref)
                informe = dt.validar_particiones([conv], {cid: "entrenamiento"})
                self.assertFalse(informe.es_evaluable, informe.errores)

    def test_tipos_hablante_y_evidencia_se_validan(self):
        ref = dt.Referencia(
            clase="vishing", t_r_linea=True, pedido="REQUEST_AUTH_CODE",
            evidencia=[{"linea": 1, "evento": "invento",
                        "etiquetas": ["REQUEST_AUTH_CODE"]}],
            revision_humana="si")
        conv = dt.Conversacion(
            case_id="TT", lineas=(dt.Linea("Z", "  "),),
            referencia=ref)
        informe = dt.validar_particiones([conv], {"TT": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        texto = "\n".join(informe.errores)
        self.assertIn("hablante", texto)
        self.assertIn("texto vacío", texto)
        self.assertIn("no es un entero de línea", texto)
        self.assertIn("no está en", texto)
        self.assertIn("revision_humana", texto)


def referencia_revisada(t_r=3, t_c=4):
    return dt.Referencia(
        clase="vishing", t_r_linea=t_r, t_c_linea=t_c,
        pedido="REQUEST_AUTH_CODE",
        evidencia=(
            {"linea": 1, "evento": "contexto", "etiquetas": ["AUTHORITY_CLAIM"]},
            {"linea": t_r, "evento": "pedido", "etiquetas": ["REQUEST_AUTH_CODE"]},
            {"linea": t_c, "evento": "cumplimiento", "etiquetas": []},
        ),
        revision_humana=True)


class TestPuertaFailClosed(unittest.TestCase):
    def armar_salida_valida(self):
        convs = [
            conversacion("M1", "banco m uno", "réplica m uno",
                         "pedido m uno código", "cierre m uno",
                         ref=referencia_revisada()),
            conversacion("M2", "banco m dos", "réplica m dos",
                         "pedido m dos código", "cierre m dos",
                         ref=referencia_revisada()),
        ]
        asignacion = {"M1": "entrenamiento", "M2": "validacion"}
        informe = dt.validar_particiones(convs, asignacion)
        self.assertTrue(informe.es_evaluable, informe.errores)
        man = dt.generar_manifiesto({"origen": "doble"}, {"ventana": 2},
                                    asignacion, convs)
        self.assertEqual(man["revision_humana"], {"revisadas": 2, "total": 2})
        return dt.informe_validacion(man, informe, {})

    def test_dicts_vacios_no_habilitan(self):
        salida = self.armar_salida_valida()
        for rev, acu in ((None, None), ({}, {}),
                         ({"revisores": ["equipo"]},
                          {"composicion": "acordada"})):
            with self.subTest(rev=rev, acu=acu):
                ok, _ = dt.puede_habilitarse(
                    salida, revision_efectiva=rev, acuerdo=acu)
                self.assertFalse(ok)

    def test_revision_exige_trazabilidad_completa(self):
        salida = self.armar_salida_valida()
        base = revision_trazable()
        casos = {
            "sin_campos": {},
            "revisores_vacios": {**base, "revisores": []},
            "revisores_en_blanco": {**base, "revisores": ["   "]},
            "sin_originales": {**base, "originales_conservados": False},
            "originales_sin_referencia": {**base, "originales_referencia": "  "},
            "desacuerdo_sin_adjudicar": {**base, "adjudicaciones": []},
            "desacuerdo_sin_caso": {**base, "desacuerdos": [
                {"punto": "alcance", "posturas": ["a", "b"]}]},
            "adjudicacion_sin_caso": {**base, "adjudicaciones": [
                {"decision": "restringida"}]},
            "revisadas_parciales": {
                **base,
                "referencias_revisadas": {"revisadas": 1, "total": 2}},
        }
        for nombre, rev in casos.items():
            with self.subTest(nombre=nombre):
                ok, _ = dt.puede_habilitarse(
                    salida, revision_efectiva=rev, acuerdo=acuerdo_efectivo())
                self.assertFalse(ok)

    def test_puerta_no_exige_cuotas(self):
        salida = self.armar_salida_valida()
        for revisores in (["Lucía Ferraro"], ["equipo"]):
            with self.subTest(revisores=revisores):
                rev = {**revision_trazable(), "revisores": revisores}
                ok, motivos = dt.puede_habilitarse(
                    salida, revision_efectiva=rev, acuerdo=acuerdo_efectivo())
                self.assertTrue(ok, motivos)

    def test_puerta_abre_solo_con_estructuras_trazables_sinteticas(self):
        salida = self.armar_salida_valida()
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva=revision_trazable(),
            acuerdo=acuerdo_efectivo())
        self.assertTrue(ok, motivos)


class TestRegresionOchoYDiagnostico(unittest.TestCase):
    def test_ocho_historicas_solo_entran_como_regresion(self):
        conv = conversacion(dt.REGRESION_OCHO[0], "histórica uno",
                            "réplica uno", "decime el código uno",
                            "cierre uno")
        for particion in ("evaluacion_independiente", "entrenamiento",
                          "validacion", "diagnostico"):
            with self.subTest(particion=particion):
                informe = dt.validar_particiones(
                    [conv], {conv.case_id: particion})
                self.assertFalse(informe.es_evaluable)
                self.assertTrue(any("solo entra como regresión" in e
                                    for e in informe.errores))
        informe = dt.validar_particiones([conv], {conv.case_id: "regresion"})
        self.assertTrue(informe.es_evaluable, informe.errores)

    def test_diagnostico_es_particion_disjunta_en_el_recorrido(self):
        d = conversacion("DG1", "diagnóstico alfa uno", "réplica alfa",
                         "decime el código alfa", "cierre alfa")
        e = conversacion("EV1", "evaluación beta uno", "réplica beta",
                         "decime el código beta", "cierre beta")
        informe = dt.validar_particiones(
            [d, e], {"DG1": "diagnostico", "EV1": "evaluacion_independiente"})
        self.assertTrue(informe.es_evaluable, informe.errores)
        informe = dt.validar_particiones(
            [d, e], {"DG1": "diagnostico", "EV1": "evaluacion_independiente"},
            ids_ajuste={"EV1"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("ajuste" in err for err in informe.errores))

    def test_grupos_semanticos_no_cruzan_particiones(self):
        a = conversacion("F1", "fuente común alfa uno", "réplica alfa",
                         "decime el código alfa", "cierre alfa")
        b = conversacion("F2", "fuente común alfa dos", "réplica beta",
                         "decime el código beta", "cierre beta")
        informe = dt.validar_particiones(
            [a, b], {"F1": "entrenamiento", "F2": "evaluacion_independiente"},
            grupos_semanticos={"F1": "fuente_F01", "F2": "fuente_F01"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("grupo semántico" in e for e in informe.errores))


class TestManifiestoYValidoSintetico(unittest.TestCase):
    def test_fecha_inyectable_hace_reproducible_el_manifiesto(self):
        convs = [conversacion("M1", "banco m uno", "réplica m uno",
                              "pedido m uno código", "cierre m uno")]
        asignacion = {"M1": "entrenamiento"}
        man1 = dt.generar_manifiesto({"origen": "doble"}, {}, asignacion,
                                     convs, fecha="2026-10-27")
        man2 = dt.generar_manifiesto({"origen": "doble"}, {}, asignacion,
                                     convs, fecha="2026-10-27")
        self.assertEqual(man1, man2)
        self.assertEqual(man1["fecha"], "2026-10-27")
        man3 = dt.generar_manifiesto({"origen": "doble"}, {}, asignacion,
                                     convs, fecha="2026-10-28")
        self.assertNotEqual(man1["manifiesto_sha256"] if "manifiesto_sha256" in man1 else man1["fecha"],
                            man3["fecha"])

    def test_caso_valido_sintetico_evaluable_pero_no_habilitado(self):
        convs = [
            conversacion("V1", "llamo del banco sintético", "dígame",
                         "decime el código", "ahí va",
                         semilla=None, familia=None, modalidad="banco",
                         dificultades=("pedido_indirecto",)),
        ]
        informe = dt.validar_particiones(convs, {"V1": "entrenamiento"})
        self.assertTrue(informe.es_evaluable, informe.errores)
        salida = dt.informe_validacion({}, informe, {})
        self.assertFalse(salida["habilitado"])
        ok, _ = dt.puede_habilitarse(salida)
        self.assertFalse(ok)

    def test_sufijo_futuro_no_altera_reglas_de_validacion(self):
        base = conversacion("C1", "hola", "qué tal", "decime el código", "listo")
        mutada = conversacion("C1", "hola", "qué tal", "decime el código",
                              "te transferí todo y te doy mi clave")
        for conv in (base, mutada):
            informe = dt.validar_particiones([conv], {"C1": "entrenamiento"})
            self.assertTrue(informe.es_evaluable, informe.errores)


class TestLegitimaSinEvidenciaInventada(unittest.TestCase):
    def test_legitima_con_evidencia_vacia_es_evaluable(self):
        conv = dt.Conversacion(
            case_id="L0", lineas=dialogo("hola vecina", "chau vecina"),
            referencia=dt.Referencia(clase="legitima", evidencia=()))
        informe = dt.validar_particiones([conv], {"L0": "entrenamiento"})
        self.assertTrue(informe.es_evaluable, informe.errores)

    def test_legitima_dificil_con_evidencia_vacia_es_evaluable(self):
        conv = dt.Conversacion(
            case_id="L1", lineas=dialogo("hola vecina", "chau vecina"),
            referencia=dt.Referencia(clase="legitima_dificil", evidencia=[]))
        informe = dt.validar_particiones([conv], {"L1": "validacion"})
        self.assertTrue(informe.es_evaluable, informe.errores)

    def test_legitima_con_evidencia_presente_se_valida_igual(self):
        conv = dt.Conversacion(
            case_id="L2", lineas=dialogo("hola vecina", "chau vecina"),
            referencia=dt.Referencia(
                clase="legitima",
                evidencia=[{"linea": 1, "evento": "contexto",
                            "etiquetas": ["XXX"]}],
                revision_humana=True))
        informe = dt.validar_particiones([conv], {"L2": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("etiquetas" in e for e in informe.errores))

    def test_vishing_sin_evidencia_sigue_sin_ser_evaluable(self):
        conv = dt.Conversacion(
            case_id="V0", lineas=dialogo("llamo del banco", "dígame"),
            referencia=dt.Referencia(
                clase="vishing", t_r_linea=1, pedido="REQUEST_AUTH_CODE",
                evidencia=()))
        informe = dt.validar_particiones([conv], {"V0": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)


class TestPedidoYCumplimientoEnLaMismaLinea(unittest.TestCase):
    def test_igualdad_de_linea_se_rechaza(self):
        conv = dt.Conversacion(
            case_id="I1", lineas=dialogo("llamo del banco", "tomo nota",
                                        "paso el código 123"),
            referencia=dt.Referencia(
                clase="vishing", t_r_linea=3, t_c_linea=3,
                pedido="REQUEST_AUTH_CODE",
                evidencia=(
                    {"linea": 3, "evento": "pedido",
                     "etiquetas": ["REQUEST_AUTH_CODE"]},
                    {"linea": 3, "evento": "cumplimiento",
                     "etiquetas": []}),
                revision_humana=True))
        informe = dt.validar_particiones([conv], {"I1": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("posterior a t_r_linea" in e
                            for e in informe.errores))

    def test_orden_invertido_sigue_sin_ser_evaluable(self):
        conv = dt.Conversacion(
            case_id="I2", lineas=dialogo("llamo del banco", "tomo nota",
                                        "paso el código 123"),
            referencia=dt.Referencia(
                clase="vishing", t_r_linea=3, t_c_linea=2,
                pedido="REQUEST_AUTH_CODE",
                evidencia=(
                    {"linea": 3, "evento": "pedido",
                     "etiquetas": ["REQUEST_AUTH_CODE"]},
                    {"linea": 2, "evento": "cumplimiento",
                     "etiquetas": []})))
        informe = dt.validar_particiones([conv], {"I2": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("posterior a t_r_linea" in e for e in informe.errores))


class TestEntradasInvalidasSinCrash(unittest.TestCase):
    def test_etiquetas_y_evento_invalidos_vuelven_informe_no_excepcion(self):
        for cid, ev in (("E1", {"linea": 1, "evento": "contexto",
                                "etiquetas": [{}]}),
                        ("E2", {"linea": 1, "evento": [],
                                "etiquetas": []}),
                        ("E3", {"linea": 1, "evento": "contexto",
                                "etiquetas": "REQUEST_AUTH_CODE"}),
                        ("E4", "no-es-un-dict")):
            with self.subTest(cid=cid):
                conv = dt.Conversacion(
                    case_id=cid, lineas=dialogo("hola", "chau"),
                    referencia=dt.Referencia(
                        clase="legitima", evidencia=[ev]))
                informe = dt.validar_particiones([conv], {cid: "entrenamiento"})
                self.assertFalse(informe.es_evaluable, cid)
                self.assertTrue(informe.errores, cid)

    def test_referencia_dict_valida_es_evaluable(self):
        conv = dt.Conversacion(
            case_id="D1", lineas=dialogo("llamo del banco", "dígame",
                                        "decime el código", "ahí va"),
            referencia={"clase": "vishing", "t_r_linea": 3, "t_c_linea": 4,
                        "pedido": "REQUEST_AUTH_CODE",
                        "evidencia": [
                            {"linea": 1, "evento": "contexto", "etiquetas": []},
                            {"linea": 3, "evento": "pedido",
                             "etiquetas": ["REQUEST_AUTH_CODE"]},
                            {"linea": 4, "evento": "cumplimiento",
                             "etiquetas": []}],
                        "revision_humana": False, "par": None})
        informe = dt.validar_particiones([conv], {"D1": "entrenamiento"})
        self.assertTrue(informe.es_evaluable, informe.errores)

    def test_referencia_con_otra_estructura_vuelve_informe(self):
        conv = dt.Conversacion(
            case_id="D2", lineas=dialogo("hola", "chau"),
            referencia="no-es-una-referencia")
        informe = dt.validar_particiones([conv], {"D2": "entrenamiento"})
        self.assertFalse(informe.es_evaluable)
        self.assertTrue(any("estructura no soportada" in e
                            for e in informe.errores))

    def test_etiquetar_prefijo_tolera_evidencia_no_lista(self):
        conv = dt.Conversacion(
            case_id="P1", lineas=dialogo("hola", "chau"),
            referencia=dt.Referencia(clase="legitima", evidencia="rota"))
        etiqueta = dt.etiquetar_prefijo(conv, 1)
        self.assertEqual(etiqueta["supervision"], "sin_evidencia_suficiente")


class TestPuertaCruzaManifiesto(unittest.TestCase):
    def armar(self, revisadas_dato=True):
        ref = referencia_revisada()
        if not revisadas_dato:
            ref = dt.Referencia(
                clase=ref.clase, t_r_linea=ref.t_r_linea,
                t_c_linea=ref.t_c_linea, pedido=ref.pedido,
                evidencia=ref.evidencia, revision_humana=False)
        convs = [conversacion("M1", "banco m uno", "réplica m uno",
                              "pedido m uno código", "cierre m uno", ref=ref),
                 conversacion("M2", "banco m dos", "réplica m dos",
                              "pedido m dos código", "cierre m dos", ref=ref)]
        asignacion = {"M1": "entrenamiento", "M2": "validacion"}
        informe = dt.validar_particiones(convs, asignacion)
        self.assertTrue(informe.es_evaluable, informe.errores)
        man = dt.generar_manifiesto({"origen": "doble"}, {}, asignacion, convs)
        return dt.informe_validacion(man, informe, {})

    def test_conteo_distinto_del_manifiesto_bloquea(self):
        salida = self.armar()
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva=revision_trazable(total=5),
            acuerdo=acuerdo_efectivo())
        self.assertFalse(ok)
        self.assertTrue(any("Discrepancia" in m for m in motivos))

    def test_manifiesto_con_revision_incompleta_bloquea(self):
        salida = self.armar(revisadas_dato=False)
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva=revision_trazable(total=2),
            acuerdo=acuerdo_efectivo())
        self.assertFalse(ok)
        self.assertTrue(any("manifiesto" in m for m in motivos))

    def test_informe_sin_manifiesto_bloquea_aunque_declare_todo_revisado(self):
        convs = [conversacion("M1", "banco m uno", "réplica m uno",
                              "pedido m uno código", "cierre m uno",
                              ref=referencia_revisada()),
                 conversacion("M2", "banco m dos", "réplica m dos",
                              "pedido m dos código", "cierre m dos",
                              ref=referencia_revisada())]
        asignacion = {"M1": "entrenamiento", "M2": "validacion"}
        informe = dt.validar_particiones(convs, asignacion)
        self.assertTrue(informe.es_evaluable, informe.errores)
        salida = dt.informe_validacion({}, informe, {})
        ok, motivos = dt.puede_habilitarse(
            salida, revision_efectiva=revision_trazable(total=2),
            acuerdo=acuerdo_efectivo())
        self.assertFalse(ok)
        self.assertTrue(any("manifiesto" in m for m in motivos))

    def test_informe_conserva_conteo_y_huellas_del_manifiesto(self):
        salida = self.armar()
        self.assertEqual(salida["revision_manifiesto"],
                         {"revisadas": 2, "total": 2})
        self.assertEqual(set(salida["huellas_conversaciones"]), {"M1", "M2"})
        self.assertTrue(salida["manifiesto_sha256"])


if __name__ == "__main__":
    unittest.main()
