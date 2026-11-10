"""Etapa 2 de #143: la lista de los 140 dentro del alcance y la regla de corridas/2026-11-07_alcance-etapa-2/analizar.py,
sobre corridas sintéticas (sin modelo).

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_etapa2_143 -v
"""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import casos  # noqa: E402
import correr  # noqa: E402
from detectores import (CORTE_DE, ESQUEMA_MOTIVO, ESQUEMA_SALIDA, MAXIMO_TOKENS_CORTE, PROMPT_MOTIVO_CORTE,  # noqa: E402
                        cargar_prompt, cargar_prompt_motivo, huella)

_spec = importlib.util.spec_from_file_location("analizar_etapa2", RAIZ / "corridas" / "2026-11-07_alcance-etapa-2" / "analizar.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)


def escribir_corrida(destino: Path, prompt: str, lista: str | None, avisa: dict[str, int],
                     riesgos: dict[str, float] | None = None) -> None:
    """Una corrida cortada sintética: riesgo 0.6 (o `riesgos[caso]`) desde la línea `avisa[caso]` y 0.1 antes; la
    alerta escrita siempre es false."""
    riesgos = riesgos or {}
    ids = sorted(an.VISTA) if lista else an.IDS
    run = destino / "2026-11-08_000000_sintetica"
    run.mkdir(parents=True)
    textos = {i: casos.cargar_texto(i) for i in ids}
    manifiesto = {
        "codigo": {"commit": "f" * 40, "cambios_sin_commit_en_la_carpeta": False},
        "modo_termino": "diagnostico-completo", "interrumpida": False, "particion": "desarrollo",
        **({"lista": lista} if lista else {}),
        "ollama": {"version": an.OLLAMA, "digests": {"gemma4:e2b-it-q4_K_M": "sha256:" + an.DIGEST}},
        "parametros_slm": {"num_ctx": 4096, "seed": 42, "temperatura": 0.0, "json_cortado": {"num_predict": MAXIMO_TOKENS_CORTE}},
        "prompts": {prompt: {"texto": cargar_prompt(CORTE_DE[prompt]), "esquema": ESQUEMA_SALIDA,
                             "etapa2": {"texto": cargar_prompt_motivo(PROMPT_MOTIVO_CORTE), "esquema": ESQUEMA_MOTIVO}}},
        "casos": {i: huella((casos.DIR_TEXTO / f"{i}.txt").read_text(encoding="utf-8")) for i in ids},
    }
    (run / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False), encoding="utf-8")
    with (run / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS + correr.COLUMNAS_CORTE, extrasaction="ignore")
        w.writeheader()
        for i in ids:
            for n in range(1, len(textos[i]) + 1):
                primera = avisa.get(i) == n
                w.writerow({"detector": "slm", "prompt": prompt, "hablantes": "rol", "case_id": i, "linea": n,
                            "valida": "true", "error": "",
                            "riesgo": riesgos.get(i, 0.6) if avisa.get(i) and n >= avisa[i] else 0.1,
                            "alerta_escrita": "false", "ms_etapa1": 280, "tokens_prompt": 900,
                            "ms_etapa2": 650 if primera else ""})


def avisos_en_el_pedido(estafas: int, legitimas: int) -> dict[str, int]:
    """Avisa en la línea del pedido (o en la 1 si no hay) en las primeras `estafas` estafas y `legitimas` legítimas."""
    av = {i: an.REF[i].get("t_r_linea") or 1 for i in an.ESTAFAS[:estafas]}
    av.update({i: 1 for i in an.LEGITIMAS[:legitimas]})
    return av


class TestListaYVista(unittest.TestCase):
    def test_la_lista_de_los_140_es_la_vista(self):
        lista = correr.leer_lista("alcance-140")
        self.assertEqual(len(lista), 140)
        self.assertEqual(sorted(lista), sorted(an.VISTA))
        self.assertEqual((len(an.ESTAFAS), len(an.LEGITIMAS)), (46, 94))
        self.assertEqual(sum(1 for i in an.ESTAFAS if an.REF[i].get("t_r_linea")), 36)


class TestRegla(unittest.TestCase):
    def test_comparar(self):
        ref = {"det": 20, "antes": 10}
        self.assertEqual(an.comparar({"det": 23, "antes": 10}, ref)[:2], ("gana", ["estafas"]))
        self.assertEqual(an.comparar({"det": 20, "antes": 13}, ref)[:2], ("gana", ["antes"]))
        self.assertEqual(an.comparar({"det": 22, "antes": 12}, ref)[0], "ruido")
        self.assertEqual(an.comparar({"det": 17, "antes": 10}, ref)[0], "pierde")
        self.assertEqual(an.comparar({"det": 24, "antes": 7}, ref)[0], "mixto")

    def test_punto_respeta_el_limite_y_desempata_cerca_de_0_4(self):
        m = lambda det, antes, fa: {"det": det, "antes": antes, "fa": fa}  # noqa: E731
        curva = {"alerta sola": m(10, 2, 1), "riesgo ≥ 0.3 o alerta": m(20, 5, 9), "riesgo ≥ 0.4 o alerta": m(20, 5, 9),
                 "riesgo ≥ 0.5 o alerta": m(20, 5, 9), "riesgo ≥ 0.2 o alerta": m(30, 9, 30)}
        self.assertEqual(an.punto(curva, 9)[0], "riesgo ≥ 0.4 o alerta")
        self.assertEqual(an.punto(curva, 8)[0], "alerta sola")
        self.assertIsNone(an.punto(curva, 0))


class TestAnalisis(unittest.TestCase):
    def correr_analisis(self, corridas: dict[str, dict[str, int]], riesgos: dict[str, dict[str, float]] | None = None) -> str:
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida:
            for carpeta, avisa in corridas.items():
                prompt, lista = an.CORRIDAS[carpeta]
                escribir_corrida(Path(tmp) / carpeta, prompt, lista, avisa, (riesgos or {}).get(carpeta))
            codigo = an.main(["--datos", tmp])
            self.assertTrue((Path(tmp) / "curva.csv").exists())
        self.assertEqual(codigo, 0, salida.getvalue())
        return salida.getvalue()

    def test_c_gana_y_la_repeticion_lo_sostiene(self):
        texto = self.correr_analisis({
            "v4-corte": avisos_en_el_pedido(20, 10),
            "c-json-corte": avisos_en_el_pedido(25, 10),
            "c-json-corte-rep": avisos_en_el_pedido(24, 11),
            "v4-premisa-corte": avisos_en_el_pedido(21, 10),
            "v4-premisa-corte-rep": avisos_en_el_pedido(21, 10),
        })
        self.assertIn("Sin problemas de control", texto)
        self.assertIn("tiene F = 10/94 FA", texto)
        self.assertIn("| C | riesgo ≥ 0.4 o alerta | 25/46 |", texto)
        self.assertIn("y la repetición lo sostiene", texto)
        self.assertIn("| v4-premisa | riesgo ≥ 0.4 o alerta | 21/46 |", texto)
        self.assertIn("dentro de ±2: queda v4-corte", texto)
        self.assertIn("**Se adopta C, provisorio hasta la reserva.**", texto)

    def test_si_la_repeticion_no_lo_sostiene_no_cuenta(self):
        texto = self.correr_analisis({
            "v4-corte": avisos_en_el_pedido(20, 10),
            "c-json-corte": avisos_en_el_pedido(25, 10),
            "c-json-corte-rep": avisos_en_el_pedido(22, 10),
        })
        self.assertIn("pero la repetición no lo sostiene", texto)
        self.assertIn("> Falta v4-premisa-corte/.", texto)
        self.assertIn("**Ninguna candidata cuenta: queda v4-corte.**", texto)

    def test_la_repeticion_usa_el_umbral_de_la_primera_corrida(self):
        # C elige 0,4 en la primera corrida. En la repetición, 3 legítimas más escriben 0.45: con 0,4 tiene 13 FA
        # (> F + 2 = 12) y no cuenta, aunque con 0,5 le alcanzaría. El umbral no se vuelve a elegir (ADR 0005).
        rep = avisos_en_el_pedido(24, 13)
        texto = self.correr_analisis(
            {"v4-corte": avisos_en_el_pedido(20, 10), "c-json-corte": avisos_en_el_pedido(25, 10), "c-json-corte-rep": rep},
            {"c-json-corte-rep": {i: 0.45 for i in an.LEGITIMAS[10:13]}})
        self.assertIn("| C | riesgo ≥ 0.4 o alerta | 25/46 |", texto)
        self.assertIn("pero la repetición no lo sostiene (+4 estafas, +0 avisos antes del pedido, FA 13)", texto)
        self.assertIn("**Ninguna candidata cuenta: queda v4-corte.**", texto)

    def test_si_la_repeticion_pierde_en_la_otra_cifra_decide_el_equipo(self):
        # Mateo: la repetición cumple la misma condición completa que la primera corrida. Si sostiene +3 en una cifra
        # pero pierde 3 o más en la otra, no se adopta y decide el equipo.
        # v4-corte y la primera corrida de C avisan en la línea 1 en las primeras 20 estafas (antes del pedido);
        # la repetición avisa en el pedido: sigue con +5 estafas, pero con menos avisos antes.
        def antes(estafas):
            av = avisos_en_el_pedido(estafas, 10)
            av.update({i: 1 for i in an.ESTAFAS[:20]})
            return av
        n_antes = sum(1 for i in an.ESTAFAS[:20] if (an.REF[i].get("t_r_linea") or 0) > 1)
        self.assertGreaterEqual(n_antes, 3)
        texto = self.correr_analisis({"v4-corte": antes(20), "c-json-corte": antes(25),
                                      "c-json-corte-rep": avisos_en_el_pedido(25, 10)})
        self.assertIn(f"pero la repetición pierde 3 o más en una cifra (+5 estafas, {-n_antes:+d} avisos antes del pedido, "
                      "FA 10): no se adopta, decide el equipo", texto)
        self.assertIn("**Ninguna candidata cuenta: queda v4-corte.**", texto)

    def test_mas_fa_que_la_referencia_obliga_a_subir_el_umbral(self):
        # C escribe 0.6 en 20 legítimas: con FA ≤ 10 tiene que subir a 0,7, donde ya no avisa nada.
        texto = self.correr_analisis({
            "v4-corte": avisos_en_el_pedido(20, 10),
            "c-json-corte": avisos_en_el_pedido(30, 20),
            "c-json-corte-rep": avisos_en_el_pedido(30, 20),
        })
        self.assertIn("| C | riesgo ≥ 0.7 o alerta | 0/46 |", texto)
        self.assertIn("no se adopta (pierde 3 o más)", texto)

    def test_un_problema_de_control_frena_la_regla(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida:
            escribir_corrida(Path(tmp) / "v4-corte", "v4-corte", None, avisos_en_el_pedido(20, 10))
            escribir_corrida(Path(tmp) / "c-json-corte", "c-json-corte", "alcance-140", avisos_en_el_pedido(25, 10))
            self.assertEqual(an.main(["--datos", tmp]), 1)
        self.assertIn("no se aplica la regla", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
