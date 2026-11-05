"""Controles del contrato del ensayo nuevo, sin dependencias de modelos."""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analizar_catalogo_qwen import primer_aviso  # noqa: E402
from ensayo_catalogo_qwen import CATALOGO, SUFFIX, preparar_pares  # noqa: E402


class TokenizadorSimple:
    def encode(self, texto, add_special_tokens=False):
        return list(texto.encode())


class EnsayoCatalogoTests(unittest.TestCase):
    def test_catalogo_aprobado_conserva_once_opciones(self):
        catalogo = json.loads(CATALOGO.read_text(encoding="utf-8"))
        ids = [c["id"] for c in catalogo["categorias"]]
        self.assertEqual(len(ids), 11)
        self.assertEqual(len(set(ids)), 11)
        self.assertIn("POSSIBLE_DECEPTION", ids)
        self.assertIn("INSUFFICIENT_INFORMATION", ids)

    def test_recorte_preserva_sufijo_y_final_de_entrada(self):
        tok = TokenizadorSimple()
        pares, recortes = preparar_pares(tok, "instrucción", [{"texto": "consulta"}],
                                         "inicio " * 100 + "ULTIMO", 400)
        self.assertGreater(recortes[0], 0)
        self.assertLessEqual(len(pares[0]), 400)
        self.assertTrue(bytes(pares[0]).endswith(("ULTIMO" + SUFFIX).encode()))

    def test_compuerta_tito_se_evalua_en_cada_linea_y_umbral_es_estricto(self):
        def fila(n, activa, score):
            return {"case_id": "a", "linea": n, "ventana": "cuatro", "tito_activa": activa,
                    "puntajes": {"POSSIBLE_DECEPTION": score, "WARNING_REFUSAL": 0.1,
                                  "AUTHORITY_CLAIM": 0.99}}
        filas = [fila(1, False, 0.9), fila(2, True, 0.6), fila(3, False, 0.8)]
        self.assertEqual(primer_aviso(filas, ["a"], "cuatro", False, 0.7)["a"], 1)
        self.assertIsNone(primer_aviso(filas, ["a"], "cuatro", True, 0.7)["a"])
        self.assertIsNone(primer_aviso(filas, ["a"], "cuatro", True, 0.6)["a"])
        self.assertEqual(primer_aviso(filas, ["a"], "cuatro", True, 0.5)["a"], 2)


if __name__ == "__main__":
    unittest.main()
