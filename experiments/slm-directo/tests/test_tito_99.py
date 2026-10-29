"""Tests propios del worker #99: entradas, pooling, persistencia y seleccion.

No tocan supervision (ownership del corrector, task_3f7393a2dbf3), no
descargan modelos ni leen la reserva: usan fakes deterministas.
"""

import json
import math
import sys
import unittest
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AQUI))

from entrenar_tito_99 import (  # noqa: E402
    FORMATO_99,
    cargar_artefacto_99,
    construir_entrada,
    evaluar_configuracion,
    guardar_artefacto,
    incrustar_bloques,
    metricas_prefijos_revisados,
    percentil_95,
    recorrer_conversacion,
    seleccionar_candidatos,
    sha,
    sigmoide,
    validar_auditoria_semantica,
    validar_registros_supervision,
)


class FakeTokenizer:
    cls_token_id = 101
    sep_token_id = 102

    def __call__(self, texto, add_special_tokens=False, padding=False,
                 truncation=False):
        # tokenizacion determinista por palabra: un id por palabra.
        ids = [(abs(hash(w)) % 1000) + 1000 for w in texto.split()]
        return {"input_ids": ids}


class FakeVec(list):
    def __add__(self, other):
        return FakeVec([a + b for a, b in zip(self, other)])

    def __mul__(self, k):
        return FakeVec([a * k for a in self])

    def __truediv__(self, k):
        return FakeVec([a / k for a in self])

    def tolist(self):
        return list(self)


class FakeSeq(list):
    def __getitem__(self, idx):
        item = super().__getitem__(idx)
        return FakeSeq(item) if isinstance(idx, slice) else item

    def mean(self, dim=0):
        n, m = len(self), len(self[0])
        return FakeVec(sum(r[j] for r in self) / n for j in range(m))


class FakeModel:
    class config:
        hidden_size = 8


class FakeTorch:
    class _Ctx:
        def __enter__(self):
            return None

        def __exit__(self, *a):
            return False

    def no_grad(self):
        return self._Ctx()

    def tensor(self, rows):
        return rows

    def ones_like(self, rows, dtype=None):
        return rows


def _fake_modelo():
    class M(FakeModel):
        def __call__(self, input_ids=None, attention_mask=None):
            seq = input_ids[0] if not isinstance(input_ids, FakeSeq) else input_ids
            hidden = FakeSeq([FakeVec([float(x % 7)] * 8) for x in seq])
            return type("H", (), {"last_hidden_state": [hidden]})()

    return M()


class TestEntradas(unittest.TestCase):
    def test_control_solo_linea_nueva_sin_futuro(self):
        vis = ["A: hola", "B: decime el codigo"]
        entrada = construir_entrada(vis, "frase_actual_control")
        self.assertNotIn("hola", entrada)
        self.assertIn("codigo", entrada)

    def test_historial_acumulado_con_hablantes(self):
        vis = ["A: hola", "B: chau"]
        entrada = construir_entrada(vis, "historial_acumulado")
        self.assertEqual(entrada, "A: hola\nB: chau")

    def test_banco_sintetico_no_es_conversacion(self):
        entrada = construir_entrada(["un texto"], "historial_acumulado",
                                    sintetico=True)
        self.assertIn("FRASE SINTETICA", entrada)


class TestPooling(unittest.TestCase):
    def test_sin_truncamiento_y_tres_bloques(self):
        tok = FakeTokenizer()
        # 300 palabras -> 3 bloques de 126 con contenido completo.
        texto = " ".join(f"palabra{i}" for i in range(300))
        vecs, info = incrustar_bloques([texto], tok, _fake_modelo(), FakeTorch())
        self.assertEqual(len(vecs), 1)
        self.assertEqual(info["truncamientos"], 0)
        self.assertEqual(info["bloques"], 3)
        self.assertEqual(info["tokens_contenido"], 300)

    def test_entrada_vacia_no_rompe(self):
        vecs, _ = incrustar_bloques([""], FakeTokenizer(), _fake_modelo(),
                                     FakeTorch())
        self.assertEqual(vecs[0], [0.0] * 8)


class IdTokenizer:
    """IDs deterministas 1..n por palabra; excluye especiales del promedio."""

    cls_token_id = 101
    sep_token_id = 102

    def __call__(self, texto, add_special_tokens=False, padding=False,
                 truncation=False):
        n = len(texto.split())
        return {"input_ids": list(range(1, n + 1))}


def _modelo_identidad():
    class M(FakeModel):
        def __call__(self, input_ids=None, attention_mask=None):
            seq = input_ids[0]
            hidden = FakeSeq([FakeVec([float(x)] * 8) for x in seq])
            return type("H", (), {"last_hidden_state": [hidden]})()

    return M()


class TestPoolingLiteral(unittest.TestCase):
    def test_un_bloque_promedio_exactos_especiales_excluidos(self):
        # 3 tokens de contenido (ids 1,2,3); CLS=101/SEP=102 no promedian.
        vecs, info = incrustar_bloques(["a b c"], IdTokenizer(),
                                       _modelo_identidad(), FakeTorch())
        self.assertEqual(info["bloques"], 1)
        self.assertEqual(info["tokens_contenido"], 3)
        for v in vecs[0]:
            self.assertAlmostEqual(v, 2.0, places=9)

    def test_varios_bloques_promedio_ponderado_por_tokens(self):
        # 130 tokens: bloques de 126 y 4; media ponderada = 65.5.
        texto = " ".join(f"w{i}" for i in range(130))
        vecs, info = incrustar_bloques([texto], IdTokenizer(),
                                       _modelo_identidad(), FakeTorch())
        self.assertEqual(info["bloques"], 2)
        self.assertEqual(info["tokens_contenido"], 130)
        esperado = (63.5 * 126 + 128.5 * 4) / 130
        for v in vecs[0]:
            self.assertAlmostEqual(v, esperado, places=9)


class TestSigmoideFinitud(unittest.TestCase):
    def test_overflow_no_rompe_y_es_finito(self):
        self.assertEqual(sigmoide(1000.0), 1.0)
        self.assertEqual(sigmoide(-1000.0), 0.0)
        self.assertEqual(sigmoide(float("inf")), 1.0)
        self.assertEqual(sigmoide(float("-inf")), 0.0)
        for z in (-1000.0, -10.0, 0.0, 10.0, 1000.0):
            self.assertTrue(math.isfinite(sigmoide(z)))

    def test_nan_falla_cerrado(self):
        with self.assertRaises(ValueError):
            sigmoide(float("nan"))

    def test_percentil_95_no_es_media(self):
        xs = list(range(1, 101))
        self.assertEqual(percentil_95(xs), 95.0)
        self.assertEqual(percentil_95([2.0]), 2.0)
        self.assertEqual(percentil_95([]), 0.0)

    def test_hash_tokenizer_identico_a_entrenar_tito(self):
        from entrenar_tito import TOKENIZER_SHA_DECLARADO as esperado
        from entrenar_tito_99 import TOKENIZER_SHA_DECLARADO as real
        self.assertEqual(real, esperado)


class TestPersistencia(unittest.TestCase):
    def test_roundtrip_y_rechazo_de_formato(self):
        import tempfile
        pesos = {"coef": [0.1] * 8, "intercepto": 0.0, "n_iter": [5],
                 "ms_ajuste": 1.0}
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "arte.json"
            guardar_artefacto(ruta, "historial_acumulado", 1.0, pesos,
                              "abc123", {"split": "x"}, {"commit": "y"},
                              {"sistema": "z"}, {"torch": "t"})
            arte = cargar_artefacto_99(ruta)
            self.assertEqual(arte["formato"], FORMATO_99)
            self.assertEqual(arte["entrada"], "historial_acumulado")
            ruta.write_text(json.dumps({"formato": "otro"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                cargar_artefacto_99(ruta)


class TestReplay(unittest.TestCase):
    def test_derivacion_primera_sobre_umbral_con_igualdad(self):
        self.assertEqual(recorrer_conversacion([0.1, 0.5, 0.9], 0.5), 2)
        self.assertIsNone(recorrer_conversacion([0.1, 0.2], 0.5))

    def test_omision_y_legitima_derivada(self):
        textos = {"V1": ["A: a", "B: b"], "L1": ["A: c"]}
        refs = {"V1": {"clase": "vishing", "t_r_linea": 2, "t_c_linea": None},
                "L1": {"clase": "legitima", "t_r_linea": None, "t_c_linea": None}}

        def puntaje(cid, k):
            return (0.9 if cid == "L1" else 0.1, "", 0.0)

        ev = evaluar_configuracion([], textos, refs, puntaje, 0.5)
        self.assertEqual(ev["omisiones_oportunas"], 1)
        self.assertEqual(ev["legitimas_derivadas"], 1)

    def test_seleccion_prefiere_historial_y_desempata(self):
        res = [
            {"config": "frase_actual_control/C=1.0/u=0.5", "entrada": "frase_actual_control",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 1,
             "legitimas_derivadas": 1, "consultas_media": 2.0},
            {"config": "historial_acumulado/C=1.0/u=0.5", "entrada": "historial_acumulado",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 1,
             "legitimas_derivadas": 1, "consultas_media": 2.0},
        ]
        sel = seleccionar_candidatos(res, {r["config"]: 1.0 for r in res})
        self.assertEqual(sel["elegida"], "historial_acumulado/C=1.0/u=0.5")

    def test_fallo_none_conserva_posicion_y_se_diagnostica(self):
        textos = {"C1": ["A: hola", "B: pasame el codigo"]}
        refs = {"C1": {"clase": "vishing", "t_r_linea": 2, "t_c_linea": None}}

        def puntaje(cid, k):
            if k == 1:
                return None, "tito99_error: boom", 0.5
            return 0.9, "", 0.5

        ev = evaluar_configuracion([], textos, refs, puntaje, 0.5)
        caso = ev["por_caso"][0]
        # Sin comprimir: la derivacion es k=2, no k=1.
        self.assertEqual(caso["derivacion"], 2)
        self.assertEqual(caso["fallos"], 1)
        self.assertEqual(caso["puntajes"], [None, 0.9])
        self.assertEqual(ev["prefijos_con_fallo"], 1)
        self.assertTrue(any("k=1" in e for e in caso["errores"]))

    def test_todos_fallos_no_derivan_fail_open(self):
        textos = {"C1": ["A: hola", "B: chau"]}
        refs = {"C1": {"clase": "vishing", "t_r_linea": 1, "t_c_linea": None}}

        def puntaje(cid, k):
            return None, "tito99_error: caido", 0.1

        ev = evaluar_configuracion([], textos, refs, puntaje, 0.5)
        self.assertIsNone(ev["por_caso"][0]["derivacion"])
        self.assertEqual(ev["omisiones_oportunas"], 1)
        self.assertEqual(ev["prefijos_con_fallo"], 2)

    def test_desempate_por_costo_p95(self):
        res = [
            {"config": "historial_acumulado/C=0.1/u=0.5", "entrada": "historial_acumulado",
             "C": 0.1, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 1, "consultas_media": 2.0},
            {"config": "historial_acumulado/C=1.0/u=0.5", "entrada": "historial_acumulado",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 1, "consultas_media": 2.0},
        ]
        costos = {"historial_acumulado/C=0.1/u=0.5": 5.0,
                  "historial_acumulado/C=1.0/u=0.5": 1.0}
        sel = seleccionar_candidatos(res, costos)
        self.assertEqual(sel["elegida"], "historial_acumulado/C=1.0/u=0.5")


def _prompt(visibles):
    return "revisa:\n" + "\n".join(f"L{i} {t}" for i, t in enumerate(visibles, 1))


def _registro(cid, hasta, visibles_total, etiqueta, motivo="acuerdo",
              soporte=None, tag="qwen3.5:4b", digest="abc123",
              opciones=None, con_futuro_en_prompt=False, firma=None):
    from prompts_supervision_tito_99 import firma_prompts
    visibles = visibles_total[:hasta]
    prompt = _prompt(visibles)
    if con_futuro_en_prompt:
        prompt += "\n" + visibles_total[hasta]
    pasadas = {"prompt": prompt, "respuesta_cruda": "{}"}
    return {
        "case_id": cid, "hasta_linea": hasta, "particion": "entrenamiento",
        "firma_prompts": firma_prompts() if firma is None else firma,
        "texto_hash": sha("\n".join(visibles).encode("utf-8")),
        "modelo": {"tag": tag, "digest": digest, "ollama_version": "0.40.8",
                   "opciones": {"temperature": 0, "seed": 42, "num_predict": 200}
                   if opciones is None else opciones,
                   "formato": "json-schema etiqueta/fundamento/lineas_soporte"},
        "etiqueta": etiqueta, "fundamento": "cita textual vista",
        "lineas_soporte": [1] if soporte is None else list(soporte),
        "motivo": motivo, "pasada1": dict(pasadas), "pasada2": dict(pasadas),
    }


TEXTOS_SUP = {"C1": ["A: hola", "B: pasame el codigo"],
              "C2": ["A: buen dia"]}
PART_SUP = {"C1": "entrenamiento", "C2": "entrenamiento"}


def _sup_valida():
    return [
        _registro("C1", 1, TEXTOS_SUP["C1"], 0),
        _registro("C1", 2, TEXTOS_SUP["C1"], 1, soporte=[2]),
        _registro("C2", 1, TEXTOS_SUP["C2"], 0),
    ]


class TestSupervisionReal(unittest.TestCase):
    def test_artefacto_literal_valido_con_ambas_clases(self):
        cob = validar_registros_supervision(_sup_valida(), TEXTOS_SUP, PART_SUP)
        self.assertEqual(cob["prefijos"], 3)
        self.assertEqual(cob["nulos"], 0)
        self.assertEqual(cob["por_particion_etiqueta"],
                         {"entrenamiento/0": 2, "entrenamiento/1": 1})

    def test_rechaza_etiqueta_fuera_de_0_1_null(self):
        for mala in (2, "1", True, 1.0):
            regs = _sup_valida()
            regs[0] = _registro("C1", 1, TEXTOS_SUP["C1"], mala)
            with self.assertRaises(ValueError, msg=f"etiqueta {mala!r}"):
                validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)

    def test_rechaza_hash_que_no_es_prefijo_visible(self):
        regs = _sup_valida()
        # Hash de dos lineas en el prefijo de una: posible futuro/manipulado.
        regs[0] = _registro("C1", 1, TEXTOS_SUP["C1"], 0)
        regs[0]["texto_hash"] = sha("\n".join(TEXTOS_SUP["C1"]).encode("utf-8"))
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)

    def test_rechaza_pasada_con_sufijo_futuro_y_sin_segunda_pasada(self):
        regs = _sup_valida()
        regs[0] = _registro("C1", 1, TEXTOS_SUP["C1"], 0,
                            con_futuro_en_prompt=True)
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)
        regs = _sup_valida()
        del regs[1]["pasada2"]
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)

    def test_rechaza_motivo_incoherente_y_modelo_sin_identidad(self):
        regs = _sup_valida()
        regs[2] = _registro("C2", 1, TEXTOS_SUP["C2"], None, motivo="acuerdo")
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)
        regs = _sup_valida()
        regs[0] = _registro("C1", 1, TEXTOS_SUP["C1"], 0, digest="desconocido")
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)
        regs = _sup_valida()
        regs[0] = _registro("C1", 1, TEXTOS_SUP["C1"], 0,
                            opciones={"temperature": 0.7, "seed": 42})
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)

    def test_rechaza_cobertura_incompleta_y_sin_ambas_clases(self):
        with self.assertRaises(ValueError):
            validar_registros_supervision(_sup_valida()[:2], TEXTOS_SUP, PART_SUP)
        solo_ceros = [_registro("C1", 1, TEXTOS_SUP["C1"], 0),
                      _registro("C1", 2, TEXTOS_SUP["C1"], 0, soporte=[2]),
                      _registro("C2", 1, TEXTOS_SUP["C2"], 0)]
        with self.assertRaises(ValueError):
            validar_registros_supervision(solo_ceros, TEXTOS_SUP, PART_SUP)


def _aud_valida(n_banco=4811):
    return {"semilla": 42, "frases_auditadas": n_banco,
            "grupos": ["entrenamiento", "validacion", "comparacion_20",
                       "diagnostico"],
            "familias_excluidas_ajuste": ["f1"],
            "detalle_excluidas": {"f1": {"max_vs_veinte": 0.95, "frases": 3}},
            "umbral_usado": 0.9,
            "calibracion": {"umbral": 0.9, "metodo": "punto_medio:min_par_max_azar",
                            "pares_declarados": 4, "contrastes_azar": 20,
                            "sims_par": [0.91], "sims_azar": [0.5]}}


class TestAuditoriaSemantica(unittest.TestCase):
    def test_acepta_auditoria_enlazada(self):
        part = {"banco": [{"id": f"b{i}"} for i in range(4811)]}
        res = validar_auditoria_semantica(_aud_valida(), part)
        self.assertEqual(res["excluidas"], ["f1"])
        self.assertEqual(res["umbral"], 0.9)

    def test_rechaza_parcial_y_no_enlazada(self):
        part = {"banco": [{"id": f"b{i}"} for i in range(4811)]}
        sin_veinte = _aud_valida()
        sin_veinte["grupos"] = ["entrenamiento", "validacion"]
        with self.assertRaises(ValueError):
            validar_auditoria_semantica(sin_veinte, part)
        otro_banco = _aud_valida(n_banco=10)
        with self.assertRaises(ValueError):
            validar_auditoria_semantica(otro_banco, part)
        sin_umbral = _aud_valida()
        sin_umbral["umbral_usado"] = 0
        with self.assertRaises(ValueError):
            validar_auditoria_semantica(sin_umbral, part)

    def test_metodo_reserva_advierte_sin_rechazar(self):
        part = {"banco": [{"id": f"b{i}"} for i in range(2)]}
        aud = _aud_valida(n_banco=2)
        aud["calibracion"]["metodo"] = "reserva:sin_pares_declarados"
        res = validar_auditoria_semantica(aud, part)
        self.assertTrue(res["advertencias"])


class TestOportunaTR(unittest.TestCase):
    def test_sin_TR_no_evaluable_y_se_mantiene_en_denominador(self):
        textos = {"V1": ["A: hola", "B: pasame el codigo"]}
        refs = {"V1": {"clase": "vishing", "t_r_linea": None, "t_c_linea": None}}

        def puntaje(cid, k):
            return 0.9, "", 0.0

        ev = evaluar_configuracion([], textos, refs, puntaje, 0.5)
        caso = ev["por_caso"][0]
        self.assertIsNone(caso["oportuna"])
        self.assertEqual(caso["posicion"], "sin_T_R_no_evaluable")
        self.assertEqual(ev["omisiones_oportunas"], 0)
        self.assertEqual(ev["vishing_no_evaluable_sin_TR"], 1)
        self.assertEqual(ev["denominador_vishing"], 1)

    def test_TC_no_fabrica_oportunidad_derivacion_tardia_es_omision(self):
        textos = {"V1": ["A: a", "B: b", "B: c", "B: d"]}
        refs = {"V1": {"clase": "vishing", "t_r_linea": 2, "t_c_linea": 4}}

        def puntaje(cid, k):
            return (0.9 if k >= 4 else 0.1), "", 0.0

        ev = evaluar_configuracion([], textos, refs, puntaje, 0.5)
        caso = ev["por_caso"][0]
        self.assertEqual(caso["derivacion"], 4)
        self.assertFalse(caso["oportuna"])
        self.assertFalse(caso["margen_TR"])
        self.assertTrue(caso["margen_TC"])
        self.assertEqual(ev["omisiones_oportunas"], 1)

    def test_derivacion_en_TR_es_oportuna_con_ambos_margenes(self):
        textos = {"V1": ["A: a", "B: codigo ya"]}
        refs = {"V1": {"clase": "vishing", "t_r_linea": 2, "t_c_linea": 2}}

        def puntaje(cid, k):
            return (0.9 if k >= 2 else 0.1), "", 0.0

        ev = evaluar_configuracion([], textos, refs, puntaje, 0.5)
        caso = ev["por_caso"][0]
        self.assertTrue(caso["oportuna"])
        self.assertTrue(caso["margen_TR"])
        self.assertTrue(caso["margen_TC"])


class TestSeleccionHistorial(unittest.TestCase):
    def test_frase_estrictamente_mejor_no_sustituye_principal(self):
        res = [
            {"config": "frase_actual_control/C=1.0/u=0.5",
             "entrada": "frase_actual_control",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 0, "consultas_media": 1.0},
            {"config": "historial_acumulado/C=1.0/u=0.5",
             "entrada": "historial_acumulado",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 1,
             "legitimas_derivadas": 1, "consultas_media": 9.0},
        ]
        costos = {"frase_actual_control/C=1.0/u=0.5": 0.1,
                  "historial_acumulado/C=1.0/u=0.5": 1.0}
        sel = seleccionar_candidatos(res, costos)
        self.assertEqual(sel["elegida"], "historial_acumulado/C=1.0/u=0.5")
        self.assertIn("frase_actual_control/C=1.0/u=0.5",
                      sel["controles_frase"])
        self.assertIn("frase_actual_control/C=1.0/u=0.5",
                      sel["frontera_global_informativa"])

    def test_costo_p95_real_decide_no_consultas_media(self):
        res = [
            {"config": "historial_acumulado/C=0.1/u=0.5",
             "entrada": "historial_acumulado",
             "C": 0.1, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 1, "consultas_media": 1.0},
            {"config": "historial_acumulado/C=1.0/u=0.5",
             "entrada": "historial_acumulado",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 1, "consultas_media": 9.0},
        ]
        costos = {"historial_acumulado/C=0.1/u=0.5": 5.0,
                  "historial_acumulado/C=1.0/u=0.5": 1.0}
        sel = seleccionar_candidatos(res, costos)
        self.assertEqual(sel["elegida"], "historial_acumulado/C=1.0/u=0.5")

    def test_sin_costo_p95_o_sin_historial_falla_cerrado(self):
        res = [
            {"config": "historial_acumulado/C=1.0/u=0.5",
             "entrada": "historial_acumulado",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 0, "consultas_media": 2.0},
        ]
        with self.assertRaises(ValueError):
            seleccionar_candidatos(res, {})
        solo_frase = [
            {"config": "frase_actual_control/C=1.0/u=0.5",
             "entrada": "frase_actual_control",
             "C": 1.0, "umbral": 0.5, "omisiones_oportunas": 0,
             "legitimas_derivadas": 0, "consultas_media": 2.0},
        ]
        with self.assertRaises(ValueError):
            seleccionar_candidatos(
                solo_frase, {"frase_actual_control/C=1.0/u=0.5": 1.0})


class TestMetricasRevisados(unittest.TestCase):
    def test_f1_solo_revisados_inciertos_en_cobertura(self):
        puntajes = {"V1": [0.9, 0.9, 0.9]}
        etiquetas = {("V1", 1): 1, ("V1", 2): None, ("V1", 3): 0}
        m = metricas_prefijos_revisados(puntajes, etiquetas, 0.5)
        self.assertEqual(m["revisados"], 2)
        self.assertEqual(m["inciertos_null"], 1)
        self.assertEqual((m["tp"], m["fp"], m["tn"], m["fn"]), (1, 1, 0, 0))
        self.assertAlmostEqual(m["f1"], 2 * 0.5 * 1.0 / 1.5, places=4)

    def test_sin_revisados_no_inventa_f1(self):
        m = metricas_prefijos_revisados({"V1": [0.9]}, {("V1", 1): None}, 0.5)
        self.assertEqual(m["revisados"], 0)
        self.assertIsNone(m["f1"])
        self.assertEqual(m["inciertos_null"], 1)

    def test_etiqueta_invalida_falla_cerrado(self):
        with self.assertRaises(ValueError):
            metricas_prefijos_revisados({"V1": [0.9]}, {("V1", 1): 2}, 0.5)


def _recibo(ruta, firma, conformidad, total, tag="qwen3.5:4b"):
    recibo = {"fecha": "2026-10-29", "prompts_version": "v2-test",
              "firma_prompts": firma,
              "modelo": {"tag": tag, "digest": "d8b0f5e9760cd168",
                         "ollama_version": "0.40.8",
                         "opciones": {"temperature": 0, "seed": 42}},
              "controles": [{"control": f"c{i}", "esperado": 0, "observado": 0,
                             "conforme": True} for i in range(total)],
              "conformidad": conformidad, "total": total}
    ruta.write_text(json.dumps(recibo), encoding="utf-8")


class TestPuertaFirmaRecibo(unittest.TestCase):
    def test_rechaza_firma_ausente(self):
        regs = _sup_valida()
        del regs[0]["firma_prompts"]
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)

    def test_rechaza_firma_distinta_a_vigente(self):
        import prompts_supervision_tito_99 as ps
        regs = _sup_valida()
        regs[0]["firma_prompts"] = "0" * 64
        self.assertNotEqual(regs[0]["firma_prompts"], ps.firma_prompts())
        with self.assertRaises(ValueError):
            validar_registros_supervision(regs, TEXTOS_SUP, PART_SUP)

    def test_recibo_ausente_bloquea(self):
        import tempfile
        from entrenar_tito_99 import validar_recibo_controles
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                validar_recibo_controles(Path(tmp) / "no-existe.json")

    def test_recibo_no_coincidente_o_no_conforme_bloquea(self):
        import tempfile
        import prompts_supervision_tito_99 as ps
        from entrenar_tito_99 import validar_recibo_controles
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp) / "recibo.json"
            _recibo(r, "0" * 64, 1, 1)
            with self.assertRaises(ValueError):
                validar_recibo_controles(r)
            _recibo(r, ps.firma_prompts(), 0, 1)
            with self.assertRaises(ValueError):
                validar_recibo_controles(r)

    def test_recibo_conforme_vigente_pasa(self):
        import tempfile
        import prompts_supervision_tito_99 as ps
        from entrenar_tito_99 import validar_recibo_controles
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp) / "recibo.json"
            _recibo(r, ps.firma_prompts(), 2, 2)
            resumen = validar_recibo_controles(r)
            self.assertEqual(resumen["conformidad"], 2)
            self.assertEqual(resumen["firma"], ps.firma_prompts())


if __name__ == "__main__":
    unittest.main()
