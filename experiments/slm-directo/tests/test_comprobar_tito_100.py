"""Tests del worker #100: congelar-primero, regla FT, check de las 20.

No tocan entrenador/supervisor/matriz/informe, no descargan modelos, no
abren las veinte reales ni la reserva: dobles deterministas y fixtures
literales con hashes autoconsistentes.
"""

import hashlib
import json
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))

from comprobar_tito_100 import (  # noqa: E402
    ESTADO_BLOQUEADO_FT,
    ESTADO_CONGELADO,
    BloqueoFineTuning,
    comparar_sobre_conjunto,
    congelar_desde_informe99,
    construir_manifiesto_congelado,
    decidir_fine_tuning,
    evaluar_comprobacion,
    ids_comparacion_20,
    ids_validacion_conversaciones,
    main,
    recorrer_conversacion_con_trazas,
    regenerar_md,
    validar_congelado,
    verificar_comparacion_20,
    verificar_puerta_revision,
    verificar_umbral_cli,
    _validar_identidad_99,
)

ENCODER = {"id": "pysentimiento/robertuito-base-uncased",
           "revision": "20cb399e4b93f270c0cd6b6f533bcb0ada3cb658",
           "congelado": True,
           "representacion": "promedio_ponderado_bloques_128_ultima_capa",
           "hidden": 2}

IDS_20 = [f"FIX-{'V' if i < 10 else 'L'}-{i:03d}" for i in range(20)]
IDS_VAL = ["FIX-VAL-001", "FIX-VAL-002"]


def _artefacto(entrada="historial_acumulado", c=1.0, datos=None):
    arte = {"formato": "tito-99-logreg-v1", "entrada": entrada,
            "config_regresion": {"semilla": 42, "C": c},
            "encoder": dict(ENCODER),
            "tokenizador": {"tokenizer_sha256": "tok" * 21 + "t"},
            "pesos": {"coef": [0.5, -0.25], "intercepto": 0.0}}
    if datos is not None:
        arte["datos"] = dict(datos)
    return arte


def _datos_identidad(sup_sha, aud_sha, part_sha, cfg_sha):
    return {"supervision_identidad": {"sha256": sup_sha},
            "auditoria_identidad": {"sha256": aud_sha},
            "particiones_sha256": part_sha,
            "configuracion_sha256": cfg_sha,
            "split": "train=PARTICIONES-TITO-2026-10-29/entrenamiento",
            "semilla": 42}


def _shas_fuentes_actuales(sup, aud):
    import hashlib as _hl
    part_ruta = AQUI / "PARTICIONES-TITO-2026-10-29.json"
    cfg_ruta = AQUI / "CONFIGURACION-TITO-2026-10-29.json"
    return (_hl.sha256(sup.read_bytes()).hexdigest(),
            _hl.sha256(aud.read_bytes()).hexdigest(),
            _hl.sha256(part_ruta.read_bytes()).hexdigest(),
            _hl.sha256(cfg_ruta.read_bytes()).hexdigest())


def _escribir_candidato(tmp, nombre="cand.json", c=1.0, sup=None, aud=None):
    import hashlib as _hl
    datos = _datos_identidad(*_shas_fuentes_actuales(sup, aud))
    arte = _artefacto(c=c, datos=datos)
    ruta = tmp / nombre
    ruta.write_text(json.dumps(arte), encoding="utf-8")
    sha = _hl.sha256(ruta.read_bytes()).hexdigest()
    return ruta, arte, sha


def _identidad_para(arte, sha):
    return {"sha256": sha, "entrada": arte["entrada"],
            "C": arte["config_regresion"]["C"],
            "encoder": dict(arte["encoder"]),
            "tokenizador": dict(arte["tokenizador"]),
            "datos": dict(arte["datos"])}


def _particiones_fixture():
    convs = []
    for cid in IDS_20 + IDS_VAL:
        part = "comparacion_20" if cid in IDS_20 else "validacion"
        convs.append({"case_id": cid, "particion_preparacion": part,
                      "grupo_preparacion": cid,
                      "texto_sha256": "c" * 64, "referencia_sha256": "d" * 64})
    return {"semilla": 42, "evaluacion_ids": list(IDS_20),
            "conversaciones": convs, "particiones_sha256": "a" * 64}


def _casos_20_fixture():
    """Textos, referencias, lector y particiones autoconsistentes."""
    textos, referencias, crudos = {}, {}, {}
    for i, cid in enumerate(IDS_20):
        vishing = i < 10
        lineas = [f"A: hola {cid}", "B: qué tal",
                  "A: pasame el código" if vishing else "A: gracias"]
        ref = {"case_id": cid, "clase": "vishing" if vishing else "legitima",
               "t_r_linea": 3 if vishing else None, "t_c_linea": None,
               "revision_humana": False}
        textos[cid] = list(lineas)
        referencias[cid] = dict(ref)
        crudos[cid] = ("\n".join(lineas).encode("utf-8"),
                       json.dumps(ref, ensure_ascii=False).encode("utf-8"))
    particiones = _particiones_fixture()
    for c in particiones["conversaciones"]:
        if c["case_id"] in crudos:
            t, r = crudos[c["case_id"]]
            c["texto_sha256"] = hashlib.sha256(t).hexdigest()
            c["referencia_sha256"] = hashlib.sha256(r).hexdigest()

    def lector(cid):
        return crudos[cid]

    return textos, referencias, particiones, lector


def _manifiesto_valido(tmp, particiones=None, ids_20=None):
    arte = _artefacto()
    ap = tmp / "cand.json"
    ap.write_text(json.dumps(arte), encoding="utf-8")
    part = particiones or _particiones_fixture()
    fuentes = {k: {"ruta": f"{k}.json", "sha256": "0" * 64}
               for k in ("informe99", "supervision", "auditoria",
                         "particiones", "config")}
    man = construir_manifiesto_congelado(
        {"elegida": "h", "criterio": "c", "frontera_pareto": ["h"],
         "decision_fine_tuning": {"corresponde": False}},
        ap, arte, 0.5, "#99-congelada", fuentes, {"commit": "t"},
        part["particiones_sha256"],
        [c["case_id"] for c in part["conversaciones"]
         if c["particion_preparacion"] == "validacion"],
        list(ids_20 or part["evaluacion_ids"]))
    mp = tmp / "man.json"
    mp.write_text(json.dumps(man), encoding="utf-8")
    return mp, ap, arte


class DobleTito:
    """Doble con la superficie usada por evaluar (sin fit, sin red)."""

    def __init__(self, entrada, puntajes=None, fallos=frozenset()):
        self.entrada = entrada
        self.puntajes = dict(puntajes or {})
        self.fallos = set(fallos)
        self.visto = []

    def puntuar_entrada(self, texto):
        self.visto.append(texto)
        n = len(texto.splitlines())
        if n in self.fallos:
            return None, "doble_caido", 1.0
        return self.puntajes.get(n, 0.0), "", 1.0

    def puntuar(self, n, texto):
        self.visto.append((n, texto))
        if n in self.fallos:
            return None, "doble_caido", 1.0
        return self.puntajes.get(n, 0.0), "", 1.0

    def preparar(self):
        return {"encoder_ms": 0.0, "calentamiento_ms": 0.0, "error": ""}


def _textos_referencias():
    textos = {
        "V-1": ["A: hola", "B: qué tal", "A: pasame el código"],
        "L-1": ["A: el delivery llega", "B: lo espero"],
        "V-SINTR": ["A: hola", "B: decime"],
    }
    referencias = {
        "V-1": {"clase": "vishing", "t_r_linea": 3, "t_c_linea": None,
                "revision_humana": False},
        "L-1": {"clase": "legitima", "t_r_linea": None, "t_c_linea": None,
                "revision_humana": False},
        "V-SINTR": {"clase": "vishing", "t_r_linea": None, "t_c_linea": None,
                    "revision_humana": False},
    }
    return textos, referencias


class TestReglaFineTuning(unittest.TestCase):
    def test_conserva_ambas_no_fuerza_ft(self):
        r = decidir_fine_tuning(
            [{"config": "h", "omisiones_oportunas": 1,
              "legitimas_derivadas": 1}],
            {"omisiones_oportunas": 2, "legitimas_derivadas": 2},
            ["error visible"])
        self.assertFalse(r["corresponde"])

    def test_empate_ambos_no_fuerza_ft(self):
        r = decidir_fine_tuning(
            [{"config": "h", "omisiones_oportunas": 2,
              "legitimas_derivadas": 2}],
            {"omisiones_oportunas": 2, "legitimas_derivadas": 2},
            ["error visible"])
        self.assertFalse(r["corresponde"])
        self.assertIn("h", r["conservan"])

    def test_supera_sin_error_observable_no_hay_ft(self):
        r = decidir_fine_tuning(
            [{"config": "h", "omisiones_oportunas": 3,
              "legitimas_derivadas": 3}],
            {"omisiones_oportunas": 2, "legitimas_derivadas": 2}, [])
        self.assertFalse(r["corresponde"])

    def test_supera_con_error_bloquea_explicito(self):
        with self.assertRaises(BloqueoFineTuning) as ctx:
            decidir_fine_tuning(
                [{"config": "h", "omisiones_oportunas": 3,
                  "legitimas_derivadas": 3}],
                {"omisiones_oportunas": 2, "legitimas_derivadas": 2},
                ["deriva tarde en V-7"])
        self.assertIn("rama afinada", str(ctx.exception))

    def test_supera_uno_solo_bloquea_con_error(self):
        with self.assertRaises(BloqueoFineTuning):
            decidir_fine_tuning(
                [{"config": "h", "omisiones_oportunas": 1,
                  "legitimas_derivadas": 9}],
                {"omisiones_oportunas": 2, "legitimas_derivadas": 2},
                ["falsas en legítimas"])

    def test_lista_vacia_falla_cerrado_con_y_sin_errores(self):
        with self.assertRaises(ValueError):
            decidir_fine_tuning([], {"omisiones_oportunas": 0,
                                     "legitimas_derivadas": 0}, [])
        with self.assertRaises(ValueError):
            decidir_fine_tuning([], {"omisiones_oportunas": 0,
                                     "legitimas_derivadas": 0},
                                ["error visible"])

    def test_candidato_malformado_falla_cerrado(self):
        with self.assertRaises(ValueError):
            decidir_fine_tuning([{"config": "h"}], {}, [])

    def test_todos_los_congelados_cuando_uno_conserva(self):
        r = decidir_fine_tuning(
            [{"config": f"h{i}", "omisiones_oportunas": 5,
              "legitimas_derivadas": 5} for i in range(5)] + [
             {"config": "buena", "omisiones_oportunas": 0,
              "legitimas_derivadas": 0}],
            {"omisiones_oportunas": 1, "legitimas_derivadas": 1},
            ["errores varios"])
        self.assertFalse(r["corresponde"])
        self.assertEqual(r["conservan"], ["buena"])


class TestCongelado(unittest.TestCase):
    def _fuentes(self):
        return {k: {"ruta": f"{k}.json", "sha256": "0" * 64}
                for k in ("informe99", "supervision", "auditoria",
                          "particiones", "config")}

    def _base(self, arte, sha="x", part_sha="0" * 64, frozen="2026-10-29T01:02:03+00:00"):
        return {"artefacto_sha256": sha, "formato": arte.get("formato"),
                "entrada": "historial_acumulado",
                "umbral": 0.5, "encoder": dict(ENCODER), "variante": "v",
                "fuentes": self._fuentes(), "congelado_en": frozen,
                "particiones": {"particiones_sha256": part_sha,
                                "ids_validacion": ["FIX-VAL-001"],
                                "ids_comparacion_20": list(IDS_20)}}

    def test_manifiesto_construido_pasa_contrato_y_emite_bloque(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            arte = _artefacto()
            ap = tmp / "cand.json"
            ap.write_text(json.dumps(arte), encoding="utf-8")
            part = _particiones_fixture()
            man = construir_manifiesto_congelado(
                {"elegida": "h_C1.0_u0.5", "criterio": "c",
                 "frontera_pareto": ["h_C1.0_u0.5"],
                 "decision_fine_tuning": {"corresponde": False}},
                ap, arte, 0.5, "#99-congelada", self._fuentes(),
                {"commit": "x"}, part["particiones_sha256"], IDS_VAL,
                part["evaluacion_ids"])
            self.assertEqual(man["estado"], ESTADO_CONGELADO)
            self.assertEqual(man["entrada"], "historial_acumulado")
            self.assertEqual(man["formato"], "tito-99-logreg-v1")
            self.assertEqual(man["encoder"], arte["encoder"])
            self.assertIn("ANTES", man["orden_temporal"])
            # congelado_en ISO con hora: orden intradía trazable.
            self.assertRegex(man["congelado_en"], r"T\d{2}:\d{2}:\d{2}")
            self.assertEqual(man["particiones"]["ids_validacion"], IDS_VAL)
            self.assertEqual(man["particiones"]["ids_comparacion_20"],
                             part["evaluacion_ids"])
            self.assertEqual(man["particiones"]["particiones_sha256"],
                             part["particiones_sha256"])
            import hashlib
            self.assertEqual(validar_congelado(
                man, hashlib.sha256(ap.read_bytes()).hexdigest(),
                arte), [])

    def test_sha_distinto_se_rechaza(self):
        man = self._base(_artefacto())
        errs = validar_congelado(man, "2" * 64, _artefacto())
        self.assertTrue(any("sha256" in e for e in errs))

    def test_entrada_frase_se_rechaza(self):
        arte = _artefacto(entrada="frase_actual_control")
        man = self._base(arte)
        man["entrada"] = "frase_actual_control"
        errs = validar_congelado(man, "x", arte)
        self.assertTrue(any("historial_acumulado" in e for e in errs))

    def test_encoder_no_identico_se_rechaza(self):
        otro = dict(ENCODER, revision="otra")
        arte = _artefacto()
        man = self._base(arte)
        man["encoder"] = otro
        self.assertTrue(validar_congelado(man, "x", arte))

    def test_formato_afinado_y_desconocido_se_rechazan(self):
        for formato in ("tito-100-lora-v1", "otro-formato"):
            arte = dict(_artefacto(), formato=formato)
            man = self._base(arte)
            self.assertTrue(validar_congelado(man, "x", arte),
                            formato)

    def test_fuentes_sin_hash_real_se_rechazan(self):
        man = self._base(_artefacto())
        man["fuentes"] = {"informe99": {"ruta": "r"}}
        self.assertTrue(any("fuentes" in e
                            for e in validar_congelado(man, "x",
                                                       _artefacto())))

    def test_sin_bloque_particiones_o_congelado_en_se_rechaza(self):
        man = self._base(_artefacto())
        del man["particiones"]
        del man["congelado_en"]
        errs = validar_congelado(man, "x", _artefacto())
        self.assertEqual(len(errs), 2)

    def test_umbral_cli_distinto_se_rechaza(self):
        verificar_umbral_cli(0.5, 0.5)
        verificar_umbral_cli(0.5, None)
        with self.assertRaises(ValueError):
            verificar_umbral_cli(0.5, 0.7)

    def test_revision_humana_no_se_falsifica(self):
        with self.assertRaises(ValueError):
            verificar_puerta_revision({"C": {"revision_humana": True}})
        self.assertTrue(verificar_puerta_revision(
            {"C": {"revision_humana": False}}))


class TestSplit20VsVal(unittest.TestCase):
    def test_orden_exacta_y_sin_reserva(self):
        part = _particiones_fixture()
        self.assertEqual(ids_comparacion_20(part), IDS_20)
        self.assertEqual(len(set(IDS_20)), 20)

    def test_validacion_y_20_no_se_mezclan(self):
        reales = json.loads(
            (AQUI / "PARTICIONES-TITO-2026-10-29.json").read_text(
                encoding="utf-8"))
        val = set(ids_validacion_conversaciones(reales))
        veinte = set(ids_comparacion_20(reales))
        self.assertTrue(val.isdisjoint(veinte))
        self.assertEqual(len(veinte), 20)

    def test_evaluacion_ids_tocadas_se_rechazan(self):
        part = _particiones_fixture()
        # Duplicado en vez de un caso: sin sustituir casos.
        part["evaluacion_ids"][-1] = part["evaluacion_ids"][0]
        textos, referencias, _p2, lector = _casos_20_fixture()
        with self.assertRaisesRegex(ValueError, "duplicados"):
            verificar_comparacion_20(textos, referencias, part, lector)
        # Longitud distinta de veinte: no es la comparación aprobada.
        part2 = _particiones_fixture()
        part2["evaluacion_ids"] = part2["evaluacion_ids"][:19]
        with self.assertRaisesRegex(ValueError, "veinte"):
            verificar_comparacion_20(textos, referencias, part2, lector)


class TestReplay(unittest.TestCase):
    def test_deriva_en_primera_igualdad_incluida(self):
        r = recorrer_conversacion_con_trazas(
            lambda k: (0.5 if k == 2 else 0.1, "", 1.0), 3, 0.5)
        self.assertEqual(r["derivacion"], 2)
        self.assertEqual(r["fallos"], 0)

    def test_fallos_no_derivan_y_se_cuentan(self):
        r = recorrer_conversacion_con_trazas(
            lambda k: (None, "caido", 1.0) if k == 1 else (0.9, "", 1.0),
            2, 0.5)
        self.assertEqual(r["derivacion"], 2)
        self.assertEqual(r["fallos"], 1)
        self.assertIn("k=1:caido", r["errores"])

    def test_comparar_dos_comparadores_misma_validacion(self):
        textos, referencias = _textos_referencias()
        etiquetas = {("V-1", 3): 1, ("V-1", 1): 0, ("V-1", 2): None,
                     ("L-1", 1): 0, ("L-1", 2): 0}
        nuevo = DobleTito("historial_acumulado", {1: 0.1, 2: 0.2, 3: 0.9})
        viejo = DobleTito("frase_actual_aislada", {3: 0.9})

        def pn(cid, k):
            entrada = "\n".join(textos[cid][:k])  # historial A/B acumulado
            return nuevo.puntuar_entrada(entrada)

        def pv(cid, k):
            return viejo.puntuar(k, textos[cid][k - 1].split(": ", 1)[-1])

        comp = comparar_sobre_conjunto(textos, referencias, etiquetas,
                                      pn, pv, 0.5, 0.5)
        # El nuevo ve el historial acumulado completo, sin futuro.
        self.assertIn("A: hola\nB: qué tal\nA: pasame el código", nuevo.visto)
        # Ambos derivan oportuno en V-1; el sin T_R no es evaluable en
        # oportunidad pero conserva denominadores.
        self.assertEqual(comp["nuevo"]["omisiones_oportunas"], 0)
        self.assertEqual(comp["viejo"]["omisiones_oportunas"], 0)
        self.assertEqual(comp["nuevo"]["vishing_no_evaluable_sin_TR"], 1)
        self.assertEqual(comp["nuevo"]["denominador_vishing"], 2)
        self.assertEqual(comp["nuevo"]["denominador_legitimas"], 1)
        # Solo prefijos revisados (0/1): 4 revisados, 1 incierto, resto fuera.
        self.assertEqual(comp["prefijos_nuevo"]["revisados"], 4)
        self.assertEqual(comp["prefijos_nuevo"]["inciertos_null"], 1)
        # El viejo recibe la frase aislada, no el historial.
        self.assertIn((3, "pasame el código"), viejo.visto)
        self.assertTrue(all(isinstance(v[1], str) and "\n" not in v[1]
                            for v in viejo.visto))

    def test_metricas_las_mueven_etiquetas_no_la_clase_final(self):
        # Etiqueta 1 en un prefijo legítimo cuenta fp: la clase final
        # nunca se usa como etiqueta de prefijo.
        textos = {"L-1": ["A: el delivery llega", "B: lo espero"]}
        referencias = {"L-1": {"clase": "legitima", "t_r_linea": None,
                               "t_c_linea": None, "revision_humana": False}}
        nuevo = DobleTito("historial_acumulado", {1: 0.9, 2: 0.9})
        viejo = DobleTito("frase_actual_aislada", {1: 0.1, 2: 0.1})

        def pn(cid, k):
            return nuevo.puntuar_entrada("\n".join(textos[cid][:k]))

        def pv(cid, k):
            return viejo.puntuar(k, "x")

        comp = comparar_sobre_conjunto(textos, referencias,
                                      {("L-1", 1): 1, ("L-1", 2): 0},
                                      pn, pv, 0.5, 0.5)
        self.assertEqual(comp["prefijos_nuevo"]["tp"], 1)
        self.assertEqual(comp["prefijos_nuevo"]["fp"], 1)
        self.assertEqual(comp["prefijos_nuevo"]["tn"], 0)
        # Sin etiquetas revisadas no se inventa F1 ni exactitud.
        comp2 = comparar_sobre_conjunto(textos, referencias, {}, pn, pv,
                                       0.5, 0.5)
        self.assertIsNone(comp2["prefijos_nuevo"]["f1"])
        self.assertIsNone(comp2["prefijos_nuevo"]["exactitud"])
        self.assertEqual(comp2["prefijos_nuevo"]["motivo"],
                         "sin prefijos revisados; no se inventa F1.")

    def test_fallo_nuevo_cuenta_y_no_deriva_solo(self):
        textos, referencias = _textos_referencias()
        nuevo = DobleTito("historial_acumulado", {3: 0.9},
                          fallos={1, 2, 3} & {1})
        viejo = DobleTito("frase_actual_aislada", {3: 0.9})

        def pn(cid, k):
            if cid == "V-1":
                return nuevo.puntuar_entrada("\n".join(textos[cid][:k]))
            return 0.0, "", 1.0

        comp = comparar_sobre_conjunto(
            textos, referencias, {},
            pn, lambda cid, k: viejo.puntuar(k, "x"), 0.5, 0.5)
        # Sin etiquetas revisadas no se inventa F1.
        self.assertIsNone(comp["prefijos_nuevo"]["f1"])
        self.assertEqual(comp["prefijos_nuevo"]["motivo"],
                         "sin prefijos revisados; no se inventa F1.")


class TestRecargaSinFit(unittest.TestCase):
    def test_artefacto_99_carga_sin_entrenar(self):
        # Recarga real del formato #99: valida semilla, revisión y
        # dimensión sin ajustar nada (sin torch, sin red).
        from entrenar_tito_99 import (ENCODER_REVISION, SEMILLA,
                                      cargar_artefacto_99)
        arte = {"formato": "tito-99-logreg-v1",
                "config_regresion": {"semilla": SEMILLA},
                "encoder": {"revision": ENCODER_REVISION, "hidden": 2},
                "pesos": {"coef": [0.1, 0.2], "intercepto": 0.0}}
        self.assertEqual(cargar_artefacto_99.__name__, "cargar_artefacto_99")
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "a.json"
            ruta.write_text(json.dumps(arte), encoding="utf-8")
            cargado = cargar_artefacto_99(ruta)
        self.assertEqual(cargado["pesos"]["coef"], [0.1, 0.2])

    def test_artefacto_afinado_no_pasa_por_tito99(self):
        # Un formato tito-100-* futuro no se asume Tito99 (matriz_101 lo
        # deja pendiente): el congelado exige variante declarada y el
        # loader acordado aún no existe.
        from entrenar_tito_99 import cargar_artefacto_99
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ruta = Path(d) / "b.json"
            ruta.write_text(json.dumps({"formato": "tito-100-lora-v1"}),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                cargar_artefacto_99(ruta)


class TestEvaluarGuards(unittest.TestCase):
    def _manifiesto_20(self, tmp, part):
        mp, ap, _arte = _manifiesto_valido(tmp, part, part["evaluacion_ids"])
        return mp, ap

    def test_evaluar_sin_congelar_falla_cerrado(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mp = tmp / "man.json"
            mp.write_text(json.dumps({"estado": "inexistente"}),
                          encoding="utf-8")
            textos, referencias, part, lector = _casos_20_fixture()
            with self.assertRaisesRegex(ValueError, "congelar.*primero"):
                evaluar_comprobacion(mp, tmp / "a.json", tmp / "v.json",
                                     textos, referencias, {},
                                     particiones=part, lector_20=lector)

    def test_evaluar_bloqueado_ft_no_mide(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mp = tmp / "man.json"
            mp.write_text(json.dumps({"estado": ESTADO_BLOQUEADO_FT}),
                          encoding="utf-8")
            textos, referencias, part, lector = _casos_20_fixture()
            with self.assertRaises(BloqueoFineTuning):
                evaluar_comprobacion(mp, tmp / "a.json", tmp / "v.json",
                                     textos, referencias, {},
                                     particiones=part, lector_20=lector)

    def test_evaluar_rechaza_reserva_y_fuera_de_las_veinte(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            dob = DobleTito("historial_acumulado", {})
            # Reserva: ni se lee ni se evalúa, antes de abrir nada.
            with self.assertRaisesRegex(ValueError, "eserva"):
                evaluar_comprobacion(
                    mp, ap, ap, {"CV2-T-RES-001": ["A: x"]},
                    {"CV2-T-RES-001": referencias[IDS_20[0]]}, {},
                    tito_nuevo=dob, tito_viejo=dob,
                    particiones=part, lector_20=lector)
            # Validación en vez de las veinte: no se sustituyen casos.
            textos_val = {"FIX-VAL-001": ["A: hola"]}
            refs_val = {"FIX-VAL-001": {"clase": "legitima",
                                        "t_r_linea": None, "t_c_linea": None,
                                        "revision_humana": False}}
            with self.assertRaisesRegex(ValueError, "veinte"):
                evaluar_comprobacion(
                    mp, ap, ap, textos_val, refs_val, {},
                    tito_nuevo=dob, tito_viejo=dob,
                    particiones=part, lector_20=lector)

    def test_evaluar_exige_orden_exacto_del_manifiesto(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            man = json.loads(mp.read_text(encoding="utf-8"))
            man["particiones"]["ids_comparacion_20"] = list(
                reversed(man["particiones"]["ids_comparacion_20"]))
            mp.write_text(json.dumps(man), encoding="utf-8")
            dob = DobleTito("historial_acumulado", {})
            with self.assertRaisesRegex(ValueError, "orden exacto"):
                evaluar_comprobacion(
                    mp, ap, ap, textos, referencias, {},
                    tito_nuevo=dob, tito_viejo=dob,
                    particiones=part, lector_20=lector)

    def test_evaluar_detecta_deriva_de_hash(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()

            def lector_roto(cid):
                t, r = lector(cid)
                return t + b" ", r

            mp, ap = self._manifiesto_20(tmp, part)
            dob = DobleTito("historial_acumulado", {})
            with self.assertRaisesRegex(ValueError, "deriva de hash"):
                evaluar_comprobacion(
                    mp, ap, ap, textos, referencias, {},
                    tito_nuevo=dob, tito_viejo=dob,
                    particiones=part, lector_20=lector_roto)

    def test_evaluar_rechaza_override_de_umbral(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            dob = DobleTito("historial_acumulado", {})
            with self.assertRaisesRegex(ValueError, "sin override"):
                evaluar_comprobacion(
                    mp, ap, ap, textos, referencias, {},
                    tito_nuevo=dob, tito_viejo=dob, umbral_cli=0.7,
                    particiones=part, lector_20=lector)

    def test_evaluar_ok_sin_fit_y_regenera_md(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            dob = DobleTito("historial_acumulado", {})
            comp = evaluar_comprobacion(
                mp, ap, ap, textos, referencias, {},
                tito_nuevo=dob, tito_viejo=dob,
                particiones=part, lector_20=lector)
            self.assertIn("posterior al congelamiento",
                          comp["orden_temporal"])
            # El nuevo recibió historial acumulado (2-3 líneas por k).
            self.assertTrue(any("\n" in v for v in dob.visto))
            # Las veinte no traen etiquetas de prefijo: sin F1 inventado.
            self.assertIsNone(comp["comparacion"]["prefijos_nuevo"]["f1"])
            self.assertEqual(
                comp["comparacion"]["prefijos_nuevo"]["motivo"],
                "sin prefijos revisados; no se inventa F1.")
            self.assertEqual(
                comp["comparacion"]["nuevo"]["denominador_vishing"]
                + comp["comparacion"]["nuevo"]["denominador_legitimas"], 20)
            destino = tmp / "comp.json"
            destino.write_text(json.dumps(comp), encoding="utf-8")
            md = regenerar_md(destino)
            texto = md.read_text(encoding="utf-8")
            self.assertIn("Comprobación Tito #100", texto)
            self.assertIn("Ninguna mejora del sistema", texto)
            # Regenerar no reinfere: el doble no recibe más llamadas.
            n = len(dob.visto)
            regenerar_md(destino)
            self.assertEqual(len(dob.visto), n)

    def test_evaluar_con_etiquetas_revisadas_mide_sin_fit(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            nuevo = DobleTito("historial_acumulado", {1: 0.9, 2: 0.9,
                                                      3: 0.9})
            viejo = DobleTito("frase_actual_aislada", {1: 0.1, 2: 0.1,
                                                       3: 0.1})
            etiquetas = {(IDS_20[0], 3): 1, (IDS_20[0], 1): 0,
                         (IDS_20[10], 1): 0}
            comp = evaluar_comprobacion(
                mp, ap, ap, textos, referencias, etiquetas,
                tito_nuevo=nuevo, tito_viejo=viejo,
                particiones=part, lector_20=lector)
            self.assertEqual(comp["comparacion"]["prefijos_nuevo"]["tp"], 1)
            self.assertEqual(comp["comparacion"]["nuevo"]["denominador_vishing"],
                             10)

    def test_puerta_politica_102_opcional(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            man = json.loads(mp.read_text(encoding="utf-8"))
            import hashlib
            pol = tmp / "pol.json"
            pol.write_text(json.dumps({
                "seleccion_solo_validacion": True,
                "congelado_en": "2026-10-29T00:00:01+00:00",
                "politica": {"periodo_actualizaciones": 1,
                             "regla_nueva_evidencia": "nueva",
                             "delta_score": 0.1},
                "tito": {
                    "artefacto_sha256": man["artefacto_sha256"],
                    "manifiesto100_sha256": hashlib.sha256(
                        mp.read_bytes()).hexdigest(),
                    "entrada": "historial_acumulado",
                    "umbral": man["umbral"],
                    "encoder": man["encoder"]}}),
                encoding="utf-8")
            dob = DobleTito("historial_acumulado", {})
            comp = evaluar_comprobacion(
                mp, ap, ap, textos, referencias, {},
                tito_nuevo=dob, tito_viejo=dob,
                politica_manifiesto=pol,
                particiones=part, lector_20=lector)
            self.assertIn("posterior al congelamiento",
                          comp["orden_temporal"])
            pol_mala = tmp / "pol_mala.json"
            pol_mala.write_text(json.dumps(
                {"seleccion_solo_validacion": True,
                 "congelado_en": "2026-10-29T00:00:01",  # sin zona UTC
                 "politica": {"periodo_actualizaciones": 1,
                              "regla_nueva_evidencia": "nueva",
                              "delta_score": 0.1},
                 "tito": {"artefacto_sha256": man["artefacto_sha256"],
                          "manifiesto100_sha256": "0" * 64,
                          "entrada": "historial_acumulado",
                          "umbral": man["umbral"],
                          "encoder": man["encoder"]}}),
                encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "zona UTC"):
                evaluar_comprobacion(
                    mp, ap, ap, textos, referencias, {},
                    tito_nuevo=dob, tito_viejo=dob,
                    politica_manifiesto=pol_mala,
                    particiones=part, lector_20=lector)

    def test_politica_invalida_no_abre_lecturas_20(self):
        # Secuencia f0a2106: política inválida ANTES de cualquier lectura
        # de textos/referencias de las veinte; el lector no se llama.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, _lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            man = json.loads(mp.read_text(encoding="utf-8"))
            llamadas = []
            import hashlib as _hl

            def lector_contador(cid):
                llamadas.append(cid)
                return _lector(cid)

            pol_mala = tmp / "pol_mala.json"
            pol_mala.write_text(json.dumps(
                {"seleccion_solo_validacion": True,
                 "congelado_en": "2026-10-29T00:00:01",  # sin zona UTC
                 "politica": {"periodo_actualizaciones": 1,
                              "regla_nueva_evidencia": "nueva",
                              "delta_score": 0.1},
                 "tito": {"artefacto_sha256": man["artefacto_sha256"],
                          "manifiesto100_sha256": _hl.sha256(
                              mp.read_bytes()).hexdigest(),
                          "entrada": "historial_acumulado",
                          "umbral": man["umbral"],
                          "encoder": man["encoder"]}}),
                encoding="utf-8")
            dob = DobleTito("historial_acumulado", {})
            with self.assertRaisesRegex(ValueError, "zona UTC"):
                evaluar_comprobacion(
                    mp, ap, ap, textos, referencias, {},
                    tito_nuevo=dob, tito_viejo=dob,
                    politica_manifiesto=pol_mala,
                    particiones=part, lector_20=lector_contador)
            self.assertEqual(llamadas, [])

    def test_cmd_evaluar_politica_invalida_no_lee_las_veinte(self):
        # _cmd_evaluar valida la puerta ANTES de abrir las veinte en disco.
        import tempfile
        import comprobar_tito_100 as _c100
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = self._manifiesto_20(tmp, part)
            man = json.loads(mp.read_text(encoding="utf-8"))
            import hashlib as _hl
            pol_mala = tmp / "pol_mala.json"
            pol_mala.write_text(json.dumps(
                {"seleccion_solo_validacion": True,
                 "congelado_en": "2026-10-29T00:00:01",
                 "politica": {"periodo_actualizaciones": 1,
                              "regla_nueva_evidencia": "nueva",
                              "delta_score": 0.1},
                 "tito": {"artefacto_sha256": man["artefacto_sha256"],
                          "manifiesto100_sha256": _hl.sha256(
                              mp.read_bytes()).hexdigest(),
                          "entrada": "historial_acumulado",
                          "umbral": man["umbral"],
                          "encoder": man["encoder"]}}),
                encoding="utf-8")
            tocado = []
            real_cargar = _c100._cargar_textos_20
            real_evaluar = _c100.evaluar_comprobacion

            def espiar(ids, lector=None):
                tocado.append(tuple(ids))
                return real_cargar(ids, lector)

            def prohibir(*a, **k):
                raise AssertionError("evaluar no debe correrse")

            _c100._cargar_textos_20 = espiar
            _c100.evaluar_comprobacion = prohibir
            try:
                args = type("A", (), {})()
                args.manifiesto = mp
                args.artefacto_nuevo = str(ap)
                args.artefacto_viejo = str(ap)
                args.politica_manifiesto = pol_mala
                args.etiquetas = None
                args.umbral = None
                args.salida = tmp / "comp.json"
                rc = _c100._cmd_evaluar(args)
            finally:
                _c100._cargar_textos_20 = real_cargar
                _c100.evaluar_comprobacion = real_evaluar
            self.assertEqual(rc, 2)
            self.assertEqual(tocado, [])


def _base_informe_dict(modo="conserva"):
    if modo == "conserva":
        base = {"omisiones_oportunas": 1, "legitimas_derivadas": 1,
                "denominador_vishing": 4, "denominador_legitimas": 6}
        res = [
            {"config": "historial_acumulado/C=1.0/u=0.5",
             "entrada": "historial_acumulado", "C": 1.0, "umbral": 0.5,
             "omisiones_oportunas": 0, "legitimas_derivadas": 0,
             "denominador_vishing": 4, "denominador_legitimas": 6},
            {"config": "historial_acumulado/C=0.1/u=0.3",
             "entrada": "historial_acumulado", "C": 0.1, "umbral": 0.3,
             "omisiones_oportunas": 2, "legitimas_derivadas": 2,
             "denominador_vishing": 4, "denominador_legitimas": 6},
            {"config": "frase_actual_control/C=1.0/u=0.5",
             "entrada": "frase_actual_control", "C": 1.0, "umbral": 0.5,
             "omisiones_oportunas": 3, "legitimas_derivadas": 3,
             "denominador_vishing": 4, "denominador_legitimas": 6},
        ]
    else:
        base = {"omisiones_oportunas": 0, "legitimas_derivadas": 0,
                "denominador_vishing": 4, "denominador_legitimas": 6}
        res = [
            {"config": "historial_acumulado/C=1.0/u=0.5",
             "entrada": "historial_acumulado", "C": 1.0, "umbral": 0.5,
             "omisiones_oportunas": 2, "legitimas_derivadas": 1,
             "denominador_vishing": 4, "denominador_legitimas": 6},
        ]
    return {
        "resultados_validacion": res,
        "costos_p95_ms": {r["config"]: 1.0 for r in res},
        "seleccion": {"elegida": "historial_acumulado/C=1.0/u=0.5",
                      "criterio": "pareto historial",
                      "frontera_pareto": ["historial_acumulado/C=1.0/u=0.5"]},
        "criterio_fine_tuning": {"baseline_viejo": base},
    }


def _informe99_fixture(tmp, modo="conserva"):
    # Contrato nuevo: informe válido SIEMPRE trae identidad del peso medido.
    # Sin artefacto no hay hash real: este fixture queda como informe
    # viejo/rotó (se rechaza); los caminos válidos usan
    # _informe99_con_identidad con el candidato ya escrito en disco.
    informe = _base_informe_dict(modo)
    ruta = tmp / "informe99.json"
    ruta.write_text(json.dumps(informe), encoding="utf-8")
    return ruta


def _informe99_con_identidad(tmp, arte, arte_sha, nombre_arte="cand.json",
                             modo="conserva", nombre_informe="informe99.json"):
    informe = _base_informe_dict(modo)
    informe["artefactos_identidad"] = {
        nombre_arte: _identidad_para(arte, arte_sha)}
    informe["artefacto_seleccionado"] = {"nombre": nombre_arte,
                                         "sha256": arte_sha}
    ruta = tmp / nombre_informe
    ruta.write_text(json.dumps(informe), encoding="utf-8")
    return ruta


def _informe99_con_identidad_desde(tmp, sup, aud, ap, arte, sha,
                                  modo="conserva",
                                  nombre_informe="informe99.json"):
    return _informe99_con_identidad(tmp, arte, sha, ap.name, modo,
                                    nombre_informe)


class TestCongelarInforme99(unittest.TestCase):
    def _sup_aud(self, tmp):
        sup = tmp / "sup.jsonl"
        sup.write_text("{}\n", encoding="utf-8")
        aud = tmp / "aud.json"
        aud.write_text("{}", encoding="utf-8")
        return sup, aud

    def _valido(self, tmp, modo="conserva", nombre="cand.json"):
        sup, aud = self._sup_aud(tmp)
        ap, arte, sha = _escribir_candidato(tmp, nombre, 1.0, sup, aud)
        informe = _informe99_con_identidad(tmp, arte, sha, ap.name, modo)
        return informe, ap, arte, (sup, aud)

    def test_congelar_valido_guarda_manifiesto_consumible(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap, arte, (sup, aud) = self._valido(tmp)
            salida = tmp / "man.json"
            man = congelar_desde_informe99(
                informe, ap, salida, rutas_sup_aud=(sup, aud))
            self.assertEqual(man["estado"], ESTADO_CONGELADO)
            self.assertFalse(
                man["decision_fine_tuning"]["corresponde"])
            self.assertEqual(
                man["seleccion_validacion"]["elegida"],
                "historial_acumulado/C=1.0/u=0.5")
            self.assertRegex(man["congelado_en"], r"T\d{2}:\d{2}:\d{2}")
            for clave in ("informe99", "supervision", "auditoria",
                          "particiones", "config"):
                self.assertRegex(man["fuentes"][clave]["sha256"],
                                 r"^[0-9a-f]{64}$")
            import hashlib
            self.assertEqual(
                validar_congelado(
                    man, hashlib.sha256(ap.read_bytes()).hexdigest(),
                    arte), [])
            # El manifiesto construido lo consume el evaluador (20 fixture).
            textos, referencias, part, lector = _casos_20_fixture()
            man["particiones"]["particiones_sha256"] = \
                part["particiones_sha256"]
            man["particiones"]["ids_comparacion_20"] = list(
                part["evaluacion_ids"])
            man["particiones"]["ids_validacion"] = IDS_VAL
            (tmp / "man2.json").write_text(json.dumps(man), encoding="utf-8")
            dob = DobleTito("historial_acumulado", {})
            comp = evaluar_comprobacion(
                tmp / "man2.json", ap, ap, textos, referencias, {},
                tito_nuevo=dob, tito_viejo=dob,
                particiones=part, lector_20=lector)
            self.assertIn("posterior al congelamiento",
                          comp["orden_temporal"])

    def test_congelar_no_sobreescribe_identidad(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap, _arte, (sup, aud) = self._valido(tmp)
            salida = tmp / "man.json"
            congelar_desde_informe99(
                informe, ap, salida, rutas_sup_aud=(sup, aud))
            with self.assertRaisesRegex(ValueError, "ya congelada"):
                congelar_desde_informe99(
                    informe, ap, salida, rutas_sup_aud=(sup, aud))

    def test_congelar_ft_correspondiente_guarda_bloqueo(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap, _arte, (sup, aud) = self._valido(tmp, modo="bloqueo")
            salida = tmp / "man.json"
            with self.assertRaises(BloqueoFineTuning):
                congelar_desde_informe99(
                    informe, ap, salida, rutas_sup_aud=(sup, aud))
            bloqueado = json.loads(salida.read_text(encoding="utf-8"))
            self.assertEqual(bloqueado["estado"], ESTADO_BLOQUEADO_FT)
            self.assertTrue(bloqueado["trabajo_faltante"])

    def test_congelar_sin_identidad_se_rechaza(self):
        # Informe viejo sin artefactos_identidad/artefacto_seleccionado:
        # no se compatibiliza, se rechaza.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            sup, aud = self._sup_aud(tmp)
            _ap, _arte, _sha = _escribir_candidato(tmp, "cand.json", 1.0,
                                                  sup, aud)
            informe = _informe99_fixture(tmp)
            with self.assertRaisesRegex(ValueError, "artefactos_identidad"):
                congelar_desde_informe99(
                    informe, _ap, tmp / "man.json",
                    rutas_sup_aud=(sup, aud))

    def test_congelar_peso_mutado_mismo_c_encoder_se_rechaza(self):
        # Mismo C/encoder pero pesos distintos: el hash en disco ya no es
        # el realmente medido.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap, arte, (sup, aud) = self._valido(tmp)
            mutado = dict(arte)
            mutado["pesos"] = {"coef": [0.9, -0.1], "intercepto": 0.0}
            ap.write_text(json.dumps(mutado), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "realmente medido"):
                congelar_desde_informe99(
                    informe, ap, tmp / "man.json",
                    rutas_sup_aud=(sup, aud))

    def test_congelar_encoder_y_tokenizador_divergentes_se_rechazan(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            sup, aud = self._sup_aud(tmp)
            ap, arte, _sha_viejo = _escribir_candidato(tmp, "cand.json", 1.0,
                                                      sup, aud)
            # Informe que dice medir un encoder/tokenizador distintos pero
            # declara el sha del archivo actual: el bloque debe rechazarse
            # aunque el hash coincida.
            import hashlib as _hl
            sha = _hl.sha256(ap.read_bytes()).hexdigest()
            otro_enc = dict(arte)
            otro_enc["encoder"] = dict(arte["encoder"], revision="otra")
            informe = _informe99_con_identidad(tmp, otro_enc, sha, ap.name)
            with self.assertRaisesRegex(ValueError, "encoder"):
                congelar_desde_informe99(
                    informe, ap, tmp / "man.json",
                    rutas_sup_aud=(sup, aud))
            otro_tok = dict(arte)
            otro_tok["tokenizador"] = {"tokenizer_sha256": "f" * 64}
            informe2 = _informe99_con_identidad(tmp, otro_tok, sha, ap.name,
                                                nombre_informe="inf2.json")
            with self.assertRaisesRegex(ValueError, "tokenizador"):
                congelar_desde_informe99(
                    informe2, ap, tmp / "man2.json",
                    rutas_sup_aud=(sup, aud))

    def test_congelar_fuente_cambiada_se_rechaza(self):
        # La supervisión cambió tras la medición: sus hashes ya no coinciden
        # con la identidad informada ni con el artefacto.
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap, _arte, (sup, aud) = self._valido(tmp)
            sup.write_text("{}\n{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "supervision"):
                congelar_desde_informe99(
                    informe, ap, tmp / "man.json",
                    rutas_sup_aud=(sup, aud))

    def test_congelar_informe_invalido_falla_cerrado(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            sup, aud = self._sup_aud(tmp)
            ap, arte, _sha = _escribir_candidato(tmp, "cand.json", 1.0,
                                                sup, aud)
            # Elegida con frase: no es el candidato principal.
            informe = _informe99_con_identidad(tmp, arte, _sha, ap.name)
            datos = json.loads(informe.read_text(encoding="utf-8"))
            datos["seleccion"]["elegida"] = "frase_actual_control/C=1.0/u=0.5"
            informe.write_text(json.dumps(datos), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "historial"):
                congelar_desde_informe99(
                    informe, ap, tmp / "man.json",
                    rutas_sup_aud=(sup, aud))
            # Artefacto que no corresponde a la elegida (C distinto): la
            # identidad informa C=1.0 pero el archivo trae C=10.0.
            sup2 = tmp / "sup2.jsonl"
            sup2.write_text("{}\n", encoding="utf-8")
            aud2 = tmp / "aud2.json"
            aud2.write_text("{}", encoding="utf-8")
            ap2, arte2, sha2 = _escribir_candidato(tmp, "otro.json", 10.0,
                                                   sup2, aud2)
            informe2 = _informe99_con_identidad(
                tmp, arte2, sha2, ap2.name,
                nombre_informe="informe99_b.json")
            # Reescribo la elegida/identidad a C=1.0 para forzar el desvío.
            d2 = json.loads(informe2.read_text(encoding="utf-8"))
            d2["artefactos_identidad"][ap2.name]["C"] = 1.0
            informe2.write_text(json.dumps(d2), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no corresponde"):
                congelar_desde_informe99(
                    informe2, ap2, tmp / "man2.json",
                    rutas_sup_aud=(sup2, aud2))


def _rutas_reales_sup_aud():
    try:
        import supervision_tito_99 as _sup
        return Path(_sup.SUPERVISION_RUTA), Path(_sup.AUDITORIA_RUTA)
    except ImportError:
        return (AQUI / "SUPERVISION-CONTEXTUAL-TITO-99-2026-10-29.jsonl",
                AQUI / "AUDITORIA-SEMANTICA-CONTEXTUAL-TITO-99-2026-10-29.json")


def _candidato_cli(tmp, c=1.0, modo="conserva", nombre="cand.json",
                   nombre_informe="informe99.json"):
    sup, aud = _rutas_reales_sup_aud()
    ap, arte, sha = _escribir_candidato(tmp, nombre, c, sup, aud)
    informe = _informe99_con_identidad(tmp, arte, sha, ap.name, modo,
                                       nombre_informe)
    return informe, ap


class TestCLI(unittest.TestCase):
    def test_congelar_sin_args_y_faltantes_no_cero(self):
        self.assertEqual(main(["--paso", "congelar"]), 2)
        self.assertEqual(main(["--paso", "congelar", "--resultados99",
                               "/tmp/no-existe-100", "--artefacto",
                               "/tmp/no-existe-100",
                               "--salida", "/tmp/no-existe-100.json"]), 2)

    def test_congelar_valido_y_segundo_intento_no_sobreescribe(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap = _candidato_cli(tmp)
            salida = tmp / "man.json"
            rc = main(["--paso", "congelar", "--resultados99", str(informe),
                       "--artefacto", str(ap), "--salida", str(salida)])
            self.assertEqual(rc, 0)
            man = json.loads(salida.read_text(encoding="utf-8"))
            self.assertEqual(man["estado"], ESTADO_CONGELADO)
            import hashlib
            self.assertEqual(
                man["artefacto_sha256"],
                hashlib.sha256(ap.read_bytes()).hexdigest())
            # Segunda corrida a la misma salida: no sobreescribe.
            rc2 = main(["--paso", "congelar", "--resultados99", str(informe),
                        "--artefacto", str(ap), "--salida", str(salida)])
            self.assertEqual(rc2, 2)

    def test_congelar_bloqueo_devuelve_no_cero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap = _candidato_cli(tmp, modo="bloqueo",
                                         nombre_informe="inf_bloq.json")
            salida = tmp / "man.json"
            rc = main(["--paso", "congelar", "--resultados99", str(informe),
                       "--artefacto", str(ap), "--salida", str(salida)])
            # FT correspondiente sin rama afinada: bloqueo explícito, no
            # falso skip ni falso success.
            self.assertEqual(rc, 3)
            bloqueado = json.loads(salida.read_text(encoding="utf-8"))
            self.assertEqual(bloqueado["estado"], ESTADO_BLOQUEADO_FT)

    def test_congelar_umbral_distinto_se_rechaza(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            informe, ap = _candidato_cli(tmp, nombre_informe="inf_u.json")
            rc = main(["--paso", "congelar", "--resultados99", str(informe),
                       "--artefacto", str(ap),
                       "--salida", str(tmp / "man.json"), "--umbral", "0.7"])
            self.assertEqual(rc, 2)

    def test_evaluar_faltantes_no_cero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            self.assertEqual(
                main(["--paso", "evaluar", "--manifiesto",
                      str(tmp / "no-existe.json")]), 2)
            mp = tmp / "man.json"
            mp.write_text(json.dumps({"estado": "inexistente"}),
                          encoding="utf-8")
            self.assertEqual(
                main(["--paso", "evaluar", "--manifiesto", str(mp)]), 2)

    def test_regenerar_sin_entrada_no_cero_y_valido_cero(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            self.assertEqual(main(["--paso", "regenerar"]), 2)
            self.assertEqual(main(["--paso", "regenerar", "--entrada",
                                   str(tmp / "no-existe.json"),
                                   "--salida", str(tmp / "x.md")]), 2)
            textos, referencias, part, lector = _casos_20_fixture()
            mp, ap = _manifiesto_valido(tmp, part, part["evaluacion_ids"])[:2]
            dob = DobleTito("historial_acumulado", {})
            comp = evaluar_comprobacion(
                mp, ap, ap, textos, referencias, {},
                tito_nuevo=dob, tito_viejo=dob,
                particiones=part, lector_20=lector)
            destino = tmp / "comp.json"
            destino.write_text(json.dumps(comp), encoding="utf-8")
            self.assertEqual(
                main(["--paso", "regenerar", "--entrada", str(destino)]), 0)
            self.assertTrue(destino.with_suffix(".md").exists())


if __name__ == "__main__":
    unittest.main()
