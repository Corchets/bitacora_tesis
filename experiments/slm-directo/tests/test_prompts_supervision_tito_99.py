"""Pruebas propias de prompts_supervision_tito_99 (corrección v4, #99).

Con dobles deterministas, sin red ni modelos ni reserva: verifican que
ambas pasadas comparten el mismo objetivo contextual y solo llevan el
prefijo visible con A/B (sin IDs, clase, T_R ni futuro, sin respuesta de
la pasada 1 en la 2), que el acuerdo produce 0/1/null, que lo inválido va
a null, que la firma versiona los prompts y que los registros viejos
(borrador sin firma) se rechazan y no se heredan como verdad.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))

import prompts_supervision_tito_99 as ps  # noqa: E402


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


class TestPromptsContextuales(unittest.TestCase):
    def test_solo_visible_con_AB_y_sin_reveladores(self):
        vis = ["A: hola", "B: decime el codigo"]
        p1, p2 = ps.construir_prompt_pasada1(vis), ps.construir_prompt_pasada2(vis)
        for p in (p1, p2):
            self.assertIn("A: hola", p)
            self.assertIn("B: decime el codigo", p)
            self.assertNotIn("LAB-", p)
            self.assertNotIn("vishing", p)
            self.assertNotIn("T_R", p)
            self.assertNotIn("clase", p.lower().replace("claramente", ""))
        corto = ["A: hola"]
        self.assertNotIn("decime", ps.construir_prompt_pasada1(corto))
        self.assertNotIn("decime", ps.construir_prompt_pasada2(corto))

    def test_pasadas_difieren_pero_comparten_regla(self):
        vis = ["A: hola"]
        p1, p2 = ps.construir_prompt_pasada1(vis), ps.construir_prompt_pasada2(vis)
        self.assertNotEqual(p1, p2)
        # Misma regla de decisión en ambas: el núcleo normativo es idéntico.
        self.assertIn(ps.REGLA_DECISION, p1)
        self.assertIn(ps.REGLA_DECISION, p2)
        # La regla contextual distingue legítimo de riesgoso y no exige
        # petición directa en una sola línea.
        self.assertIn("legítimo", ps.REGLA_DECISION)
        self.assertIn("repartido en varias líneas", ps.REGLA_DECISION)
        self.assertIn("NO alcanza por sí solo", ps.REGLA_DECISION)
        self.assertNotIn("DIRECTAMENTE", p1 + p2)
        # Regla triestado breve (root): pregunta explícita de asignar UNA
        # etiqueta, no binaria; orden 1-evidencia / null-incomprensible /
        # 0-legítimo; el indicio vale aunque nadie haya pedido nada.
        self.assertIn("asigná UNA etiqueta", ps.REGLA_DECISION)
        self.assertIn("(1, 0 o null)", ps.REGLA_DECISION)
        self.assertIn("No es una pregunta de sí/no", ps.REGLA_DECISION)
        self.assertIn("aunque nadie haya pedido nada todavía", ps.REGLA_DECISION)
        # Anti-alucinación: cada afirmación del fundamento exige cita
        # literal; lo implícito no cuenta.
        self.assertIn("PROHIBIDO inventar", ps.REGLA_DECISION)
        self.assertIn("entrecomillad", ps.REGLA_DECISION)
        self.assertIn("implícito", ps.REGLA_DECISION)
        # Incomprensible o cortado va a null, no a 0.
        self.assertIn("Lo incompleto o no identificado no es 0", ps.REGLA_DECISION)
        self.assertIn("cortado a mitad", ps.REGLA_DECISION)
        self.assertIn("'eso'", ps.REGLA_DECISION)

    def test_sin_respuesta_de_pasada1_en_pasada2(self):
        vis = ["A: hola", "B: pasame el codigo ya"]
        p2 = ps.construir_prompt_pasada2(vis)
        self.assertNotIn("pasada1", p2.lower().replace("pasada 1", ""))
        self.assertNotIn("respuesta_cruda", p2)


class TestFirma(unittest.TestCase):
    def test_firma_estable_y_versionada(self):
        self.assertEqual(ps.firma_prompts(), ps.firma_prompts())
        self.assertEqual(len(ps.firma_prompts()), 64)
        self.assertTrue(ps.PROMPT_VERSION.startswith("v4-"))

    def test_registro_viejo_sin_firma_se_rechaza(self):
        viejo = {"case_id": "X", "hasta_linea": 1, "etiqueta": 0}
        self.assertFalse(ps.es_registro_vigente(viejo))
        self.assertFalse(ps.es_registro_vigente(
            {"firma_prompts": "0" * 64}))
        vigente = {"firma_prompts": ps.firma_prompts()}
        self.assertTrue(ps.es_registro_vigente(vigente))


class TestValidacionAcuerdo(unittest.TestCase):
    def test_acuerdo_1_y_0(self):
        p1 = ps.validar_respuesta({"etiqueta": 1, "fundamento": "f",
                                   "lineas_soporte": [2]}, 2)
        p2 = ps.validar_respuesta({"etiqueta": 1, "fundamento": "g",
                                   "lineas_soporte": [2]}, 2)
        et, _, sop, mot = ps.acordar(p1, p2)
        self.assertEqual((et, sop, mot), (1, [2], "acuerdo"))
        q1 = ps.validar_respuesta({"etiqueta": 0, "fundamento": "f",
                                   "lineas_soporte": [1]}, 2)
        q2 = ps.validar_respuesta({"etiqueta": 0, "fundamento": "g",
                                   "lineas_soporte": [1, 2]}, 2)
        et, _, sop, mot = ps.acordar(q1, q2)
        self.assertEqual((et, sop, mot), (0, [1, 2], "acuerdo"))

    def test_desacuerdo_e_invalido_van_a_null(self):
        p1 = ps.validar_respuesta({"etiqueta": 1, "fundamento": "f",
                                   "lineas_soporte": [1]}, 1)
        p2 = ps.validar_respuesta({"etiqueta": 0, "fundamento": "g",
                                   "lineas_soporte": [1]}, 1)
        et, _, _, mot = ps.acordar(p1, p2)
        self.assertIsNone(et)
        self.assertEqual(mot, "desacuerdo")
        mala = ps.validar_respuesta({"etiqueta": 1, "fundamento": "f",
                                     "lineas_soporte": [9]}, 2)
        et, _, _, mot = ps.acordar(mala, p2)
        self.assertIsNone(et)
        self.assertEqual(mot, "respuesta_invalida")

    def test_rechaza_soporte_fuera_de_rango_y_vacio_decidido(self):
        _, _, _, err = ps.validar_respuesta(
            {"etiqueta": 1, "fundamento": "f", "lineas_soporte": [5]}, 2)
        self.assertTrue(err)
        _, _, _, err = ps.validar_respuesta(
            {"etiqueta": 0, "fundamento": "f", "lineas_soporte": []}, 2)
        self.assertTrue(err)
        # Booleanos no son etiquetas válidas.
        _, _, _, err = ps.validar_respuesta(
            {"etiqueta": True, "fundamento": "f", "lineas_soporte": [1]}, 2)
        self.assertTrue(err)


class TestRevisionStateless(unittest.TestCase):
    def test_dos_llamadas_nuevas_con_firma_y_recibos(self):
        cli = FakeCliente([resp(1, soporte=(2,)), resp(1, soporte=(2,))])
        out = ps.revisar_prefijo(["A: hola", "B: decime el codigo"], cli, "m")
        self.assertEqual(out["etiqueta"], 1)
        self.assertEqual(len(cli.prompts), 2)
        self.assertNotEqual(cli.prompts[0], cli.prompts[1])
        self.assertEqual(out["firma_prompts"], ps.firma_prompts())
        self.assertIn("prompt", out["pasada1"])
        self.assertIn("respuesta_cruda", out["pasada2"])

    def test_error_de_modelo_va_a_null_con_motivo(self):
        class Roto:
            def chat(self, *a, **k):
                raise ValueError("caído")
        out = ps.revisar_prefijo(["A: hola"], Roto(), "m")
        self.assertIsNone(out["etiqueta"])
        self.assertEqual(out["motivo"], "respuesta_invalida")


OPCIONES_VIGENTES = {
    "temperature": 1, "seed": 42, "num_predict": 8192, "num_ctx": 16384,
    "top_p": 0.95, "top_k": 20, "min_p": 0.0, "presence_penalty": 1.5,
    "repeat_penalty": 1.0,
}


class TestIdentidadCache(unittest.TestCase):
    def _meta(self, tag="gemma4:e4b", digest="d1", version="0.40.8",
              opciones=None, think=True):
        return {
            "tag": tag, "digest": digest, "ollama_version": version,
            "opciones": dict(opciones) if opciones is not None else dict(
                OPCIONES_VIGENTES),
            "think": think,
            "formato": "json-schema etiqueta/fundamento/lineas_soporte",
        }

    def _reg(self, meta, firma="FIRMA"):
        return {"firma_prompts": firma, "modelo": meta}

    def test_vigente_de_exige_firma_y_misma_identidad(self):
        m = self._meta()
        self.assertTrue(ps.es_registro_vigente_de(self._reg(m), "FIRMA", m))

    def test_rechaza_mezcla_otro_modelo_digest_opciones_version(self):
        m = self._meta()
        # Otro tag (qwen) con la misma plantilla no se hereda.
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(tag="qwen3.5:4b", digest="d2")), "FIRMA", m))
        # Mismo tag pero otro digest tampoco.
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(digest="otro")), "FIRMA", m))
        # Ni otras opciones (aunque sean deterministas entre sí).
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(opciones={"temperature": 0.5, "seed": 42,
                                           "num_predict": 300})),
            "FIRMA", m))
        # Ni otra versión de Ollama con igual tag/digest/opciones.
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(version="0.21.1")), "FIRMA", m))
        # Ni think distinto (hipótesis think: pensar=True vs False no se mezcla).
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(think=False)), "FIRMA", m))
        # Ni presupuesto/muestreo distinto (2048/temp0 fallida no se mezcla
        # con la variante 4096/ficha-Qwen, ni 300 con ninguna).
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(opciones={"temperature": 0, "seed": 42,
                                           "num_predict": 2048})),
            "FIRMA", m))
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(opciones={"temperature": 0, "seed": 42,
                                           "num_predict": 300})),
            "FIRMA", m))
        # Ni la variante 4k sin num_ctx (agotó el contexto total con
        # done_reason=length): distinto contexto, distinta identidad.
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(opciones={
                "temperature": 1, "seed": 42, "num_predict": 4096,
                "top_p": 0.95, "top_k": 20, "min_p": 0.0,
                "presence_penalty": 1.5, "repeat_penalty": 1.0})),
            "FIRMA", m))
        # Ni el lote 4b-8k preservado (5/8, 3 desvíos por generación con
        # num_predict=4096 y num_ctx=8192): cambió el presupuesto y el
        # contexto, así que no se hereda ni se refirma.
        self.assertFalse(ps.es_registro_vigente_de(
            self._reg(self._meta(opciones={
                "temperature": 1, "seed": 42, "num_predict": 4096,
                "num_ctx": 8192, "top_p": 0.95, "top_k": 20, "min_p": 0.0,
                "presence_penalty": 1.5, "repeat_penalty": 1.0})),
            "FIRMA", m))
        # Las filas anteriores a la identidad think (sin clave think) se rechazan.
        sin_think = {"firma_prompts": "FIRMA", "modelo": {
            "tag": m["tag"], "digest": m["digest"],
            "ollama_version": m["ollama_version"],
            "opciones": dict(m["opciones"]),
            "formato": m["formato"]}}
        self.assertFalse(ps.es_registro_vigente_de(sin_think, "FIRMA", m))
        # Ni la misma identidad con otra firma de prompts.
        self.assertFalse(
            ps.es_registro_vigente_de(self._reg(m), "OTRA_FIRMA", m))
        # Sin identidad del anotador no hay vigencia total.
        self.assertFalse(ps.es_registro_vigente_de(
            {"firma_prompts": "FIRMA"}, "FIRMA", m))
        self.assertFalse(ps.es_registro_vigente_de(None, "FIRMA", m))
        self.assertFalse(ps.es_registro_vigente_de(self._reg(m), "FIRMA", None))


class TestThinkPlumbing(unittest.TestCase):
    def test_llamar_pasada_envia_pensar_true_y_presupuesto(self):
        vistos = {}

        class Cli:
            def chat(self, modelo, mensajes, formato, opciones, pensar=None):
                vistos["pensar"] = pensar
                vistos["opciones"] = dict(opciones)
                return {"message": {"content": resp(0), "thinking": "t-razón"}}

        cruda, thinking, stats, err = ps.llamar_pasada(Cli(), "m", "hola")
        self.assertEqual(err, "")
        self.assertTrue(json.loads(cruda)["etiqueta"] == 0)
        self.assertEqual(thinking, "t-razón")
        self.assertIs(ps.PENSAR, True)
        self.assertTrue(vistos["pensar"] is True)
        self.assertEqual(vistos["opciones"]["num_predict"], 8192)
        self.assertLessEqual(vistos["opciones"]["num_predict"], 8192)
        self.assertEqual(vistos["opciones"]["num_ctx"], 16384)
        self.assertEqual(vistos["opciones"]["temperature"], 1)
        self.assertEqual(vistos["opciones"]["top_p"], 0.95)
        self.assertEqual(vistos["opciones"]["top_k"], 20)
        self.assertEqual(vistos["opciones"]["presence_penalty"], 1.5)
        self.assertEqual(vistos["opciones"]["repeat_penalty"], 1.0)
        self.assertIn("done_reason", stats)
        self.assertIn("eval_count", stats)

    def test_thinking_no_alimenta_a_la_otra_pasada(self):
        class Cli:
            def __init__(self):
                self.prompts = []

            def chat(self, modelo, mensajes, formato, opciones, pensar=None):
                self.prompts.append(mensajes[0]["content"])
                n = len(self.prompts)
                return {"message": {
                    "content": resp(0), "thinking": f"secreto-{n}"}}

        cli = Cli()
        out = ps.revisar_prefijo(["A: hola"], cli, "m")
        self.assertEqual(out["etiqueta"], 0)
        self.assertEqual(out["pasada1"]["thinking"], "secreto-1")
        self.assertEqual(out["pasada2"]["thinking"], "secreto-2")
        self.assertNotIn("secreto-1", cli.prompts[1])
        self.assertNotIn("secreto-2", cli.prompts[0])
        self.assertTrue(out["think"] is True)
        self.assertEqual(out["opciones"]["num_predict"], 8192)
        self.assertEqual(out["opciones"]["num_ctx"], 16384)
        self.assertIn("done_reason", out["pasada1"])
        self.assertIn("eval_count", out["pasada2"])

    def test_info_modelo_incluye_think(self):
        class Cli:
            def modelos_instalados(self):
                return {"m": "digest-x"}

            def version(self):
                return "0.40.8"

        meta = ps.info_modelo(Cli(), "m")
        self.assertEqual(meta["think"], True)
        self.assertEqual(meta["opciones"]["num_predict"], 8192)
        self.assertEqual(meta["opciones"]["num_ctx"], 16384)
        self.assertEqual(meta["opciones"]["temperature"], 1)
        self.assertEqual(meta["digest"], "digest-x")


class TestControlConforme(unittest.TestCase):
    def _reg(self, etiqueta, err1="", err2=""):
        return {
            "etiqueta": etiqueta,
            "pasada1": {"etiqueta": etiqueta, "error": err1},
            "pasada2": {"etiqueta": etiqueta, "error": err2},
        }

    def test_acierto_binario(self):
        self.assertTrue(ps.control_conforme(self._reg(1), 1))
        self.assertTrue(ps.control_conforme(self._reg(0), 0))
        self.assertFalse(ps.control_conforme(self._reg(1), 0))

    def test_null_por_error_no_es_acierto(self):
        # Ambas pasadas con error que caen a null: NO cuenta para null esperado.
        self.assertFalse(ps.control_conforme(self._reg(None, "e1", "e2"), None))
        self.assertFalse(ps.control_conforme(self._reg(None, "", "e2"), None))
        self.assertFalse(ps.control_conforme(self._reg(None, "e1", ""), None))

    def test_null_con_ambas_validas_si_es_acierto(self):
        self.assertTrue(ps.control_conforme(self._reg(None), None))


if __name__ == "__main__":
    unittest.main()
