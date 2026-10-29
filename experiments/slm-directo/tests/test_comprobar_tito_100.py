"""Tests preparatorios del worker #100: congelar-primero, regla FT, recarga.

No tocan entrenador/supervisor/matriz/informe, no descargan modelos, no
abren las veinte ni la reserva: dobles deterministas y fixtures literales.
"""

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
    comparar_sobre_validacion,
    construir_manifiesto_congelado,
    decidir_fine_tuning,
    evaluar_comprobacion,
    recorrer_conversacion_con_trazas,
    regenerar_md,
    validar_congelado,
    verificar_puerta_revision,
    verificar_umbral_cli,
)

ENCODER = {"id": "pysentimiento/robertuito-base-uncased",
           "revision": "20cb399e4b93f270c0cd6b6f533bcb0ada3cb658",
           "congelado": True,
           "representacion": "promedio_ponderado_bloques_128_ultima_capa",
           "hidden": 2}


def _artefacto(entrada="historial_acumulado"):
    return {"formato": "tito-99-logreg-v1", "entrada": entrada,
            "encoder": dict(ENCODER),
            "tokenizador": {"tokenizer_sha256": "tok" * 21 + "t"},
            "pesos": {"coef": [0.5, -0.25], "intercepto": 0.0}}


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

    def test_candidato_malformado_falla_cerrado(self):
        with self.assertRaises(ValueError):
            decidir_fine_tuning([{"config": "h"}], {}, [])


class TestCongelado(unittest.TestCase):
    def test_manifiesto_construido_pasa_contrato(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            arte = _artefacto()
            ap = tmp / "cand.json"
            ap.write_text(json.dumps(arte), encoding="utf-8")
            fuentes = {k: {"sha256": "0" * 64}
                       for k in ("validacion", "supervision", "auditoria",
                                 "particiones", "config")}
            man = construir_manifiesto_congelado(
                {"elegida": "h_C1.0_u0.5", "criterio": "c",
                 "frontera_pareto": ["h_C1.0_u0.5"],
                 "decision_fine_tuning": {"corresponde": False}},
                ap, arte, 0.5, "#99-congelada", fuentes,
                {"commit": "x"})
            self.assertEqual(man["estado"], ESTADO_CONGELADO)
            self.assertEqual(man["entrada"], "historial_acumulado")
            self.assertEqual(man["encoder"], arte["encoder"])
            self.assertIn("ANTES", man["orden_temporal"])
            import hashlib
            self.assertEqual(validar_congelado(
                man, hashlib.sha256(ap.read_bytes()).hexdigest(),
                arte), [])

    def test_sha_distinto_se_rechaza(self):
        man = {"artefacto_sha256": "1" * 64, "entrada": "historial_acumulado",
               "umbral": 0.5, "encoder": dict(ENCODER), "variante": "v",
               "fuentes": {k: {"sha256": "0" * 64}
                           for k in ("validacion", "supervision", "auditoria",
                                     "particiones", "config")}}
        errs = validar_congelado(man, "2" * 64, _artefacto())
        self.assertTrue(any("sha256" in e for e in errs))

    def test_entrada_frase_se_rechaza(self):
        arte = _artefacto(entrada="frase_actual_control")
        man = {"artefacto_sha256": "x", "entrada": "frase_actual_control",
               "umbral": 0.5, "encoder": dict(ENCODER), "variante": "v",
               "fuentes": {k: {"sha256": "0" * 64}
                           for k in ("validacion", "supervision", "auditoria",
                                     "particiones", "config")}}
        errs = validar_congelado(man, "x", arte)
        self.assertTrue(any("historial_acumulado" in e for e in errs))

    def test_encoder_no_identico_se_rechaza(self):
        otro = dict(ENCODER, revision="otra")
        man = {"artefacto_sha256": "x", "entrada": "historial_acumulado",
               "umbral": 0.5, "encoder": otro, "variante": "v",
               "fuentes": {k: {"sha256": "0" * 64}
                           for k in ("validacion", "supervision", "auditoria",
                                     "particiones", "config")}}
        self.assertTrue(validar_congelado(man, "x", _artefacto()))

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

        comp = comparar_sobre_validacion(textos, referencias, etiquetas,
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

    def test_fallo_nuevo_cuenta_y_no_deriva_solo(self):
        textos, referencias = _textos_referencias()
        nuevo = DobleTito("historial_acumulado", {3: 0.9},
                          fallos={1, 2, 3} & {1})
        viejo = DobleTito("frase_actual_aislada", {3: 0.9})

        def pn(cid, k):
            if cid == "V-1":
                return nuevo.puntuar_entrada("\n".join(textos[cid][:k]))
            return 0.0, "", 1.0

        comp = comparar_sobre_validacion(
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
    def _manifiesto_valido(self, tmp):
        import hashlib
        arte = _artefacto()
        ap = tmp / "cand.json"
        ap.write_text(json.dumps(arte), encoding="utf-8")
        partes = json.loads(
            (AQUI / "PARTICIONES-TITO-2026-10-29.json").read_text(
                encoding="utf-8"))
        validacion = sorted(
            c["case_id"] for c in partes["conversaciones"]
            if c.get("particion_preparacion") == "validacion")
        fuentes = {k: {"sha256": "0" * 64}
                   for k in ("validacion", "supervision", "auditoria",
                             "particiones", "config")}
        man = construir_manifiesto_congelado(
            {"elegida": "h", "criterio": "c", "frontera_pareto": ["h"],
             "decision_fine_tuning": {"corresponde": False}},
            ap, arte, 0.5, "#99-congelada", fuentes, {"commit": "t"})
        man["particiones"] = {
            "particiones_sha256": hashlib.sha256(
                (AQUI / "PARTICIONES-TITO-2026-10-29.json").read_bytes()
            ).hexdigest(),
            "ids_validacion": validacion,
        }
        mp = tmp / "man.json"
        mp.write_text(json.dumps(man), encoding="utf-8")
        return mp, ap, arte, validacion

    def test_evaluar_sin_congelar_falla_cerrado(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mp = tmp / "man.json"
            mp.write_text(json.dumps({"estado": "inexistente"}),
                          encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "congelar.*primero"):
                evaluar_comprobacion(mp, tmp / "a.json", tmp / "v.json",
                                     {}, {}, {})

    def test_evaluar_bloqueado_ft_no_mide(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mp = tmp / "man.json"
            mp.write_text(json.dumps({"estado": ESTADO_BLOQUEADO_FT}),
                          encoding="utf-8")
            with self.assertRaises(BloqueoFineTuning):
                evaluar_comprobacion(mp, tmp / "a.json", tmp / "v.json",
                                     {}, {}, {})

    def test_evaluar_rechaza_reserva_y_fuera_de_validacion(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mp, ap, arte, validacion = self._manifiesto_valido(tmp)
            textos = {validacion[0]: ["A: hola"]}
            refs = {validacion[0]: {"clase": "legitima", "t_r_linea": None,
                                    "t_c_linea": None,
                                    "revision_humana": False}}
            dob = DobleTito("historial_acumulado", {})
            # Reserva: ni se lee ni se evalúa.
            with self.assertRaisesRegex(ValueError, "reserva"):
                evaluar_comprobacion(
                    mp, ap, ap, {"CV2-T-RES-001": ["A: x"]},
                    {"CV2-T-RES-001": refs[validacion[0]]}, {},
                    tito_nuevo=dob, tito_viejo=dob)
            # Fuera de validación (p. ej. una de las veinte): no se abre.
            with self.assertRaisesRegex(ValueError, "fuera de validación"):
                evaluar_comprobacion(
                    mp, ap, ap, {"CV2-D-V-BANCO-001": ["A: x"]},
                    {"CV2-D-V-BANCO-001": refs[validacion[0]]}, {},
                    tito_nuevo=dob, tito_viejo=dob)

    def test_evaluar_ok_sin_fit_y_regenera_md(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            mp, ap, arte, validacion = self._manifiesto_valido(tmp)
            cid = validacion[0]
            textos = {cid: ["A: hola", "B: qué tal"]}
            refs = {cid: {"clase": "legitima", "t_r_linea": None,
                          "t_c_linea": None, "revision_humana": False}}
            dob = DobleTito("historial_acumulado", {})
            comp = evaluar_comprobacion(mp, ap, ap, textos, refs, {},
                                        tito_nuevo=dob, tito_viejo=dob)
            self.assertIn("posterior al congelamiento",
                          comp["orden_temporal"])
            # El nuevo recibió historial acumulado (2 líneas en k=2).
            self.assertIn("A: hola\nB: qué tal", dob.visto)
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


if __name__ == "__main__":
    unittest.main()