"""Pruebas propias de supervision_tito_99: prompts, acuerdo y puerta.

Con dobles deterministas, sin red ni modelos ni reserva: verifican que los
prompts solo llevan el prefijo visible con A/B, que el acuerdo entre
pasadas produce 0/1/null, que lo inválido va a null y que la puerta
bloquea entrenar sin cobertura completa o sin auditoría.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))

import supervision_tito_99 as st  # noqa: E402


class FakeCliente:
    def __init__(self, respuestas: list[str]):
        self.respuestas = list(respuestas)
        self.prompts: list[str] = []

    def chat(self, modelo, mensajes, formato, opciones, pensar=None):
        self.prompts.append(mensajes[0]["content"])
        return {"message": {"content": self.respuestas.pop(0)}}


def resp(etiqueta, fundamento="cita vista", soporte=(1,)):
    return json.dumps({"etiqueta": etiqueta, "fundamento": fundamento,
                       "lineas_soporte": list(soporte)}, ensure_ascii=False)


class TestPrompts(unittest.TestCase):
    def test_solo_visible_con_AB_y_sin_ids_reveladores(self):
        vis = ["A: hola", "B: decime el codigo"]
        p1, p2 = st.construir_prompt_pasada1(vis), st.construir_prompt_pasada2(vis)
        for p in (p1, p2):
            self.assertIn("A: hola", p)
            self.assertIn("B: decime el codigo", p)
            self.assertNotIn("LAB-", p)
            self.assertNotIn("vishing", p)
            self.assertNotIn("T_R", p)
        # Sin futuro: el segundo prompt de un prefijo corto no ve líneas 3+.
        corto = ["A: hola"]
        self.assertNotIn("decime", st.construir_prompt_pasada1(corto))
        self.assertNotIn("decime", st.construir_prompt_pasada2(corto))

    def test_pasadas_difieren_y_no_comparten_respuesta(self):
        vis = ["A: hola"]
        self.assertNotEqual(st.construir_prompt_pasada1(vis),
                            st.construir_prompt_pasada2(vis))


class TestValidacionAcuerdo(unittest.TestCase):
    def test_acuerdo_1_y_0(self):
        p1 = st.validar_respuesta({"etiqueta": 1, "fundamento": "f",
                                   "lineas_soporte": [2]}, 2)
        p2 = st.validar_respuesta({"etiqueta": 1, "fundamento": "g",
                                   "lineas_soporte": [2]}, 2)
        et, _, sop, mot = st.acordar(p1, p2)
        self.assertEqual((et, sop, mot), (1, [2], "acuerdo"))
        q1 = st.validar_respuesta({"etiqueta": 0, "fundamento": "f",
                                   "lineas_soporte": [1]}, 2)
        q2 = st.validar_respuesta({"etiqueta": 0, "fundamento": "g",
                                   "lineas_soporte": [1, 2]}, 2)
        et, _, sop, mot = st.acordar(q1, q2)
        self.assertEqual((et, sop, mot), (0, [1, 2], "acuerdo"))

    def test_desacuerdo_e_invalido_van_a_null(self):
        p1 = st.validar_respuesta({"etiqueta": 1, "fundamento": "f",
                                   "lineas_soporte": [1]}, 1)
        p2 = st.validar_respuesta({"etiqueta": 0, "fundamento": "g",
                                   "lineas_soporte": [1]}, 1)
        et, _, _, mot = st.acordar(p1, p2)
        self.assertIsNone(et)
        self.assertEqual(mot, "desacuerdo")
        mala = st.validar_respuesta({"etiqueta": 1, "fundamento": "f",
                                     "lineas_soporte": [9]}, 2)
        et, _, _, mot = st.acordar(mala, p2)
        self.assertIsNone(et)
        self.assertEqual(mot, "respuesta_invalida")

    def test_rechaza_soporte_fuera_de_rango_y_vacio_decidido(self):
        _, _, _, err = st.validar_respuesta(
            {"etiqueta": 1, "fundamento": "f", "lineas_soporte": [5]}, 2)
        self.assertTrue(err)
        _, _, _, err = st.validar_respuesta(
            {"etiqueta": 0, "fundamento": "f", "lineas_soporte": []}, 2)
        self.assertTrue(err)


class TestRevisionStateless(unittest.TestCase):
    def test_dos_llamadas_nuevas_sin_reutilizar_respuesta(self):
        cli = FakeCliente([resp(1, soporte=(2,)), resp(1, soporte=(2,))])
        out = st.revisar_prefijo(["A: hola", "B: decime el codigo"], cli, "m")
        self.assertEqual(out["etiqueta"], 1)
        self.assertEqual(len(cli.prompts), 2)
        self.assertNotEqual(cli.prompts[0], cli.prompts[1])
        self.assertIn("prompt", out["pasada1"])
        self.assertIn("respuesta_cruda", out["pasada2"])

    def test_error_de_modelo_va_a_null_con_motivo(self):
        class Roto:
            def chat(self, *a, **k):
                raise ValueError("caído")
        out = st.revisar_prefijo(["A: hola"], Roto(), "m")
        self.assertIsNone(out["etiqueta"])
        self.assertEqual(out["motivo"], "respuesta_invalida")


class TestCoberturaYPuerta(unittest.TestCase):
    def test_nulos_excluidos_de_ajuste_pero_en_cobertura(self):
        etiqueta_de = {("c1", 1): 1, ("c1", 2): None, ("c2", 1): 0}
        particion_de = {"c1": "entrenamiento", "c2": "entrenamiento"}
        incluidos, nulos = st.etiquetas_entrenamiento_para_ajuste(
            etiqueta_de, particion_de)
        self.assertEqual(len(incluidos), 2)
        self.assertEqual(len(nulos), 1)

    def test_puerta_bloquea_sin_cobertura_ni_auditoria(self):
        textos = {"c1": ["A: a", "B: b"]}
        particion_de = {"c1": "entrenamiento"}
        with tempfile.TemporaryDirectory() as tmp:
            sup = Path(tmp) / "sup.jsonl"
            aud = Path(tmp) / "aud.json"
            ok, motivos = st.puede_entrenar(textos, particion_de, sup, aud)
            self.assertFalse(ok)
            self.assertTrue(motivos)


class TestAuditoria(unittest.TestCase):
    def test_cruces_por_grupo_top_e_histograma_sin_excluir(self):
        banco = [{"id": "b1", "familia": "f1", "texto": "t1"},
                 {"id": "b2", "familia": "f2", "texto": "t2"}]
        grupos = {"entrenamiento": {"c1": ["A: x", "B: y"]},
                  "validacion": {"c2": ["A: z"]}}
        vec_banco = [[1.0, 0.0], [0.0, 1.0]]
        vec_lineas = {"c1#0": [1.0, 0.0], "c1#1": [1.0, 0.0],
                      "c2#0": [0.0, 1.0]}
        cruces = st.cruces_banco_grupos(banco, grupos, vec_banco,
                                        vec_lineas, 0.99)
        self.assertEqual(sorted(cruces), ["entrenamiento", "validacion"])
        self.assertEqual(cruces["entrenamiento"]["top15"][0]["familia"], "f1")
        self.assertEqual(cruces["validacion"]["top15"][0]["familia"], "f2")
        self.assertTrue(cruces["entrenamiento"]["histograma"])
        self.assertEqual(
            cruces["entrenamiento"]["n_familias_ge_umbral_referencia"], 1)
        self.assertEqual(
            cruces["validacion"]["n_familias_ge_umbral_referencia"], 1)

    def test_excluye_familia_relacionada_con_veinte(self):
        banco = [{"id": "b1", "familia": "f1", "texto": "t1"},
                 {"id": "b2", "familia": "f2", "texto": "t2"}]
        grupos = {"comparacion_20": {"c1": ["A: x"]},
                  "diagnostico": {"c2": ["A: y"]}}
        vec_banco = [[1.0, 0.0], [0.0, 1.0]]
        vec_lineas = {"c1#0": [1.0, 0.0], "c2#0": [0.0, 1.0]}
        aud = st.auditar_semantica(banco, grupos, vec_banco, vec_lineas, 0.99)
        self.assertEqual(aud["familias_excluidas_ajuste"], ["f1"])

    def test_calibracion_sin_pares_usa_reserva_declarada(self):
        cal = st.calibrar_umbral({"a": [1.0, 0.0], "b": [0.0, 1.0]})
        self.assertEqual(cal["metodo"], "reserva:sin_pares_declarados")

    def test_auditoria_informa_top_histograma_y_diagnostico(self):
        banco = [{"id": "b1", "familia": "f1", "texto": "t1"},
                 {"id": "b2", "familia": "f2", "texto": "t2"}]
        grupos = {"comparacion_20": {"c1": ["A: x"]},
                  "diagnostico": {"c2": ["A: y"]}}
        vec_banco = [[1.0, 0.0], [0.0, 1.0]]
        vec_lineas = {"c1#0": [1.0, 0.0], "c2#0": [0.0, 1.0]}
        aud = st.auditar_semantica(banco, grupos, vec_banco, vec_lineas, 0.99)
        self.assertTrue(aud["top_familias_vs_veinte"])
        self.assertTrue(aud["top_familias_vs_diagnostico"])
        self.assertTrue(aud["histograma_max_vs_veinte"])
        self.assertEqual(aud["top_familias_vs_veinte"][0]["familia"], "f1")

    def test_puerta_acepta_cero_exclusiones_con_resolucion(self):
        textos = {"c1": ["A: a", "B: b"]}
        particion_de = {"c1": "entrenamiento"}
        with tempfile.TemporaryDirectory() as tmp:
            sup = Path(tmp) / "sup.jsonl"
            sup.write_text("".join(json.dumps(
                {"case_id": "c1", "hasta_linea": k, "particion": "entrenamiento",
                 "etiqueta": et, "modelo": {"tag": "m"}}, ensure_ascii=False)
                + "\n" for k, et in ((1, 1), (2, 0))), encoding="utf-8")
            aud = Path(tmp) / "aud.json"
            aud.write_text(json.dumps(
                {"familias_excluidas_ajuste": [],
                 "resolucion_exclusiones": "cero con evidencia"}),
                encoding="utf-8")
            ok, _ = st.puede_entrenar(textos, particion_de, sup, aud)
            self.assertTrue(ok)


if __name__ == "__main__":
    unittest.main()
