"""Pruebas unitarias para el módulo de métricas de evaluación (METRICAS.md).

Uso:
    python3 -m unittest discover -s experiments/metricas/tests
"""

import sys
import unittest
from pathlib import Path

_DIR_METRICAS = Path(__file__).resolve().parents[1]
_DIR_REPO = Path(__file__).resolve().parents[3]
if str(_DIR_REPO) not in sys.path:
    sys.path.insert(0, str(_DIR_REPO))
if str(_DIR_METRICAS) not in sys.path:
    sys.path.insert(0, str(_DIR_METRICAS))

try:
    from metricas import (
        calcular_margen_lc,
        calcular_margen_lr,
        calcular_margenes,
        calcular_rtf,
        intervalo_wilson,
        metricas_clasificacion_conversacion,
        precision_con_prevalencia,
        preventive_at,
        resumen_distribucion,
        tasa_falsas_alarmas,
    )
except ImportError:
    from experiments.metricas.metricas import (  # type: ignore
        calcular_margen_lc,
        calcular_margen_lr,
        calcular_margenes,
        calcular_rtf,
        intervalo_wilson,
        metricas_clasificacion_conversacion,
        precision_con_prevalencia,
        preventive_at,
        resumen_distribucion,
        tasa_falsas_alarmas,
    )


class TestMargenes(unittest.TestCase):
    def test_ejemplo_metricas_md(self):
        """Ejemplo explícito de METRICAS.md §2:

        T_R = 58 s, T_A = 61 s, T_C = 64 s -> L_R = -3 s, L_C = 3 s.
        """
        t_r = 58
        t_a = 61
        t_c = 64
        lr = calcular_margen_lr(t_r=t_r, t_a=t_a)
        lc = calcular_margen_lc(t_c=t_c, t_a=t_a)
        self.assertEqual(lr, -3)
        self.assertEqual(lc, 3)

        lr_tuple, lc_tuple = calcular_margenes(t_a=t_a, t_r=t_r, t_c=t_c)
        self.assertEqual(lr_tuple, -3)
        self.assertEqual(lc_tuple, 3)

    def test_sin_alerta(self):
        """Sin alerta (T_A is None): llamada no detectada y margen sin dato (None)."""
        lr = calcular_margen_lr(t_r=50, t_a=None)
        lc = calcular_margen_lc(t_c=60, t_a=None)
        self.assertIsNone(lr)
        self.assertIsNone(lc)

    def test_sin_cumplimiento(self):
        """Sin T_C (t_c is None): L_C sin dato (None), no se infiere prevención."""
        lr = calcular_margen_lr(t_r=50, t_a=45)
        lc = calcular_margen_lc(t_c=None, t_a=45)
        self.assertEqual(lr, 5)
        self.assertIsNone(lc)

    def test_sin_pedido(self):
        """Sin T_R (t_r is None): L_R sin dato (None)."""
        lr = calcular_margen_lr(t_r=None, t_a=45)
        lc = calcular_margen_lc(t_c=70, t_a=45)
        self.assertIsNone(lr)
        self.assertEqual(lc, 25)

    def test_en_lineas(self):
        """En texto sin timestamps trabaja en LÍNEAS enteras."""
        # Alerta en la misma línea del pedido (L_R = 0)
        self.assertEqual(calcular_margen_lr(t_r=5, t_a=5), 0)
        # Alerta 2 líneas antes del pedido (L_R = 2)
        self.assertEqual(calcular_margen_lr(t_r=5, t_a=3), 2)
        # Alerta 1 línea después del pedido (L_R = -1)
        self.assertEqual(calcular_margen_lr(t_r=5, t_a=6), -1)


class TestIntervaloWilson(unittest.TestCase):
    def test_casos_extremos(self):
        # 0 de 24
        inf, sup = intervalo_wilson(0, 24)
        self.assertEqual(inf, 0.0)
        self.assertGreater(sup, 0.0)
        self.assertLess(sup, 0.20)

        # 24 de 24
        inf, sup = intervalo_wilson(24, 24)
        self.assertGreater(inf, 0.80)
        self.assertEqual(sup, 1.0)

    def test_caso_intermedio(self):
        # 10 de 20 (50%)
        inf, sup = intervalo_wilson(10, 20)
        self.assertAlmostEqual((inf + sup) / 2, 0.5, places=2)
        self.assertLess(inf, 0.5)
        self.assertGreater(sup, 0.5)

    def test_denominador_cero(self):
        self.assertIsNone(intervalo_wilson(0, 0))

    def test_valores_invalidos(self):
        with self.assertRaises(ValueError):
            intervalo_wilson(5, 4)
        with self.assertRaises(ValueError):
            intervalo_wilson(-1, 10)


class TestResumenDistribucion(unittest.TestCase):
    def test_vacio(self):
        res = resumen_distribucion([])
        self.assertEqual(res["n"], 0)
        self.assertIsNone(res["mediana"])
        self.assertIsNone(res["iqr"])

    def test_un_elemento(self):
        res = resumen_distribucion([5.0])
        self.assertEqual(res["n"], 1)
        self.assertEqual(res["mediana"], 5.0)
        self.assertEqual(res["q1"], 5.0)
        self.assertEqual(res["q3"], 5.0)
        self.assertEqual(res["iqr"], 0.0)

    def test_varios_elementos(self):
        res = resumen_distribucion([-3, 0, 3, 6, 9])
        self.assertEqual(res["n"], 5)
        self.assertEqual(res["mediana"], 3)
        self.assertEqual(res["min"], -3)
        self.assertEqual(res["max"], 9)
        self.assertIsNotNone(res["iqr"])
        self.assertGreater(res["iqr"], 0)


class TestPreventiveAt(unittest.TestCase):
    def test_preventive_tc_con_llamadas_sin_alerta(self):
        """Las llamadas sin alerta permanecen en el denominador.

        Las que no tienen la marca de referencia quedan excluidas con motivo informado.
        """
        casos = [
            {"case_id": "c1", "t_a": 50, "t_c": 65},  # T_A <= 65 - 10 = 55 (Cumple delta=10)
            {"case_id": "c2", "t_a": 58, "t_c": 65},  # T_A > 55 (No cumple)
            {"case_id": "c3", "t_a": None, "t_c": 70},  # Sin alerta (en denominador, no cumple)
            {"case_id": "c4", "t_a": 40, "t_c": None},  # Sin T_C (excluida)
            {"case_id": "c5", "t_a": None, "t_c": None},  # Sin alerta y sin T_C (excluida)
        ]
        res = preventive_at(delta=10, referencia="T_C", casos_vishing=casos)
        self.assertEqual(res["referencia"], "T_C")
        self.assertEqual(res["delta"], 10)
        self.assertEqual(res["numerador"], 1)  # Solo c1
        self.assertEqual(res["denominador"], 3)  # c1, c2, c3
        self.assertAlmostEqual(res["proporcion"], 1 / 3)
        self.assertEqual(res["excluidas"], 2)  # c4, c5
        self.assertIn("T_C", res["motivo_exclusion"])
        self.assertIsNotNone(res["ic95"])

    def test_preventive_tr_en_lineas(self):
        casos = [
            {"case_id": "c1", "t_a": 4, "t_r": 5},  # delta=1: T_A <= 5 - 1 = 4 (cumple)
            {"case_id": "c2", "t_a": 5, "t_r": 5},  # T_A > 4 (no cumple)
            {"case_id": "c3", "t_a": None, "t_r": 5},  # sin alerta (no cumple)
        ]
        res = preventive_at(delta=1, referencia="T_R", casos_vishing=casos)
        self.assertEqual(res["numerador"], 1)
        self.assertEqual(res["denominador"], 3)
        self.assertEqual(res["excluidas"], 0)

    def test_preventive_denominador_cero(self):
        """Sin casos evaluables: proporción None, sin error de división por cero."""
        casos = [{"case_id": "c1", "t_a": 10, "t_c": None}]
        res = preventive_at(delta=5, referencia="T_C", casos_vishing=casos)
        self.assertEqual(res["denominador"], 0)
        self.assertIsNone(res["proporcion"])
        self.assertIsNone(res["ic95"])
        self.assertEqual(res["excluidas"], 1)


class TestFalsasAlarmas(unittest.TestCase):
    def test_tasa_falsas_alarmas(self):
        casos = [
            {"case_id": "l1", "aviso": True},
            {"case_id": "l2", "aviso": False},
            {"case_id": "l3", "aviso": False},
            {"case_id": "l4", "aviso": True},
        ]
        res = tasa_falsas_alarmas(casos)
        self.assertEqual(res["falsas_alarmas"], 2)
        self.assertEqual(res["total_legitimas"], 4)
        self.assertEqual(res["tasa"], 0.5)
        self.assertIsNotNone(res["ic95"])

    def test_tasa_denominador_cero(self):
        res = tasa_falsas_alarmas([])
        self.assertEqual(res["total_legitimas"], 0)
        self.assertEqual(res["falsas_alarmas"], 0)
        self.assertIsNone(res["tasa"])
        self.assertIsNone(res["ic95"])


class TestClasificacionConversacion(unittest.TestCase):
    def test_metricas_completas(self):
        casos = [
            # Vishing
            {"clase": "vishing", "aviso": True},  # TP
            {"clase": "vishing", "aviso": True},  # TP
            {"clase": "vishing", "aviso": False},  # FN
            # Legítimas
            {"clase": "legitima_dificil", "aviso": True},  # FP
            {"clase": "legitima_dificil", "aviso": False},  # TN
            {"clase": "legitima_dificil", "aviso": False},  # TN
            {"clase": "legitima_dificil", "aviso": False},  # TN
        ]
        res = metricas_clasificacion_conversacion(casos)
        self.assertEqual(res["tp"], 2)
        self.assertEqual(res["fn"], 1)
        self.assertEqual(res["fp"], 1)
        self.assertEqual(res["tn"], 3)
        self.assertEqual(res["total_vishing"], 3)
        self.assertEqual(res["total_legitimas"], 4)
        self.assertEqual(res["total_conversaciones"], 7)

        # Precision = 2 / (2 + 1) = 2/3
        self.assertAlmostEqual(res["precision"], 2 / 3)
        # Recall = 2 / (2 + 1) = 2/3
        self.assertAlmostEqual(res["recall"], 2 / 3)
        # F1 = 2/3
        self.assertAlmostEqual(res["f1"], 2 / 3)
        self.assertIsNotNone(res["precision_ic95"])
        self.assertIsNotNone(res["recall_ic95"])

    def test_denominador_cero_en_precision(self):
        """Sin ninguna alarma (TP=0, FP=0): precision no divide por cero."""
        casos = [
            {"clase": "vishing", "aviso": False},
            {"clase": "legitima_dificil", "aviso": False},
        ]
        res = metricas_clasificacion_conversacion(casos)
        self.assertIsNone(res["precision"])
        self.assertEqual(res["recall"], 0.0)
        self.assertIsNone(res["f1"])


class TestPrecisionConPrevalencia(unittest.TestCase):
    def test_calculo_estandar(self):
        # p=0.01, r=0.8, f=0.05
        # num = 0.01 * 0.8 = 0.008
        # den = 0.008 + 0.99 * 0.05 = 0.008 + 0.0495 = 0.0575
        # prec = 0.008 / 0.0575 ≈ 0.13913043...
        p = 0.01
        r = 0.8
        f = 0.05
        prec = precision_con_prevalencia(p, r, f)
        self.assertAlmostEqual(prec, 0.008 / 0.0575, places=5)

    def test_denominador_cero(self):
        """p=0 y f=0 genera denominador cero: debe retornar None."""
        self.assertIsNone(precision_con_prevalencia(p=0.0, r=0.8, f=0.0))
        self.assertIsNone(precision_con_prevalencia(p=0.5, r=0.0, f=0.0))

    def test_valores_nulos_o_invalidos(self):
        self.assertIsNone(precision_con_prevalencia(p=0.1, r=None, f=0.05))
        self.assertIsNone(precision_con_prevalencia(p=0.1, r=0.8, f=None))
        with self.assertRaises(ValueError):
            precision_con_prevalencia(p=-0.1, r=0.8, f=0.05)
        with self.assertRaises(ValueError):
            precision_con_prevalencia(p=1.5, r=0.8, f=0.05)


class TestRTF(unittest.TestCase):
    def test_calculo_rtf(self):
        self.assertAlmostEqual(calcular_rtf(tiempo_computo_s=2.5, duracion_audio_s=10.0), 0.25)

    def test_duracion_invalida_o_nula(self):
        self.assertIsNone(calcular_rtf(tiempo_computo_s=2.5, duracion_audio_s=None))
        self.assertIsNone(calcular_rtf(tiempo_computo_s=2.5, duracion_audio_s=0.0))
        self.assertIsNone(calcular_rtf(tiempo_computo_s=None, duracion_audio_s=10.0))


class TestReplayAdapter(unittest.TestCase):
    def test_adaptador_replay_y_evaluacion(self):
        import csv
        import json
        import tempfile
        try:
            from evaluar import armar_reporte_md, cargar_salida_replay, evaluar_configuracion
        except ImportError:
            from experiments.metricas.evaluar import armar_reporte_md, cargar_salida_replay, evaluar_configuracion  # type: ignore

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            ref_path = tmp / "referencia.json"
            ref_data = {
                "call-01": {"case_id": "call-01", "clase": "vishing", "grupo": "laboratorio", "t_r": 50.0, "t_c": 65.0, "duracion_s": 100.0},
                "call-02": {"case_id": "call-02", "clase": "vishing", "grupo": "laboratorio", "t_r": 40.0, "t_c": None, "duracion_s": 80.0},
                "call-03": {"case_id": "call-03", "clase": "legitima_dificil", "grupo": "laboratorio", "duracion_s": 60.0},
            }
            ref_path.write_text(json.dumps(ref_data), encoding="utf-8")

            eventos_path = tmp / "eventos.csv"
            with eventos_path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["case_id", "aviso", "disponible_s", "config", "ms"])
                # call-01: aviso en 45.0 s (T_R=50 -> L_R=5 s; T_C=65 -> L_C=20 s)
                writer.writerow(["call-01", "false", "10.0", "cfg_replay", "50.0"])
                writer.writerow(["call-01", "true", "45.0", "cfg_replay", "120.0"])
                # call-02: sin aviso
                writer.writerow(["call-02", "false", "20.0", "cfg_replay", "80.0"])
                # call-03: falsa alarma en 30.0 s
                writer.writerow(["call-03", "true", "30.0", "cfg_replay", "90.0"])

            cargados = cargar_salida_replay(eventos_path, ref_path)
            self.assertIn("cfg_replay", cargados)
            casos_cfg = cargados["cfg_replay"]
            self.assertEqual(len(casos_cfg), 3)

            ev = evaluar_configuracion(
                nombre_config="cfg_replay",
                casos_evaluados=casos_cfg,
                unidad="segundos",
                deltas=[5.0, 10.0, 20.0],
            )
            self.assertEqual(ev["unidad"], "segundos")
            self.assertEqual(ev["clasificacion"]["tp"], 1)
            self.assertEqual(ev["clasificacion"]["fn"], 1)
            self.assertEqual(ev["clasificacion"]["fp"], 1)
            self.assertEqual(ev["falsas_alarmas"]["falsas_alarmas"], 1)
            self.assertEqual(ev["margenes"]["l_r"]["mediana"], 5.0)
            self.assertEqual(ev["margenes"]["l_c"]["mediana"], 20.0)

            # RTF: tiempos comp vs duraciones
            self.assertIsNotNone(ev["rendimiento"]["rtf"])
            self.assertGreater(ev["rendimiento"]["rtf"], 0.0)

            # Reporte markdown
            md = armar_reporte_md([ev])
            self.assertIn("cfg_replay", md)
            self.assertIn("segundos", md)


if __name__ == "__main__":
    unittest.main()

