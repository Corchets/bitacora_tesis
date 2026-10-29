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
    percentil_95,
    recorrer_conversacion,
    seleccionar_candidatos,
    sigmoide,
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


if __name__ == "__main__":
    unittest.main()
