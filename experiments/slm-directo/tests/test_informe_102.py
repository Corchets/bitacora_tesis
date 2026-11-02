"""Tests focales del informe #102 (fixtures sintéticos, sin inferencia).

Arma corridas mínimas marcadas `"sintetico": true` con dos casos reales
(solo para que el snapshot verifique) y verifica: denominadores íntegros
contra 400, márgenes `L_C` y referencias ausentes, sección consolidada
pendiente y con #101, figuras regeneradas desde CSV, y rechazo ante
deriva del snapshot. Las fixtures nunca se presentan como medición real.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import casos  # noqa: E402
import correr  # noqa: E402
import informe_102  # noqa: E402

MODELO = "qwen3.5:4b"
CASOS = ["LAB-arca-deuda", "CV2-D-L-DELIVERY-004"]  # vishing (TR 3, sin TC) + legítima


def _sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _huellas(ids):
    huellas = {}
    for cid in ids:
        huellas[cid] = {"texto_sha256": _sha(casos.DIR_TEXTO / f"{cid}.txt"),
                        "referencia_sha256": _sha(casos.DIR_REFERENCIA / f"{cid}.json"),
                        "clase": casos.cargar_referencia(cid)["clase"],
                        "particion_preparacion": "validacion",
                        "grupo_preparacion": "g",
                        "revision_humana": False}
    return huellas


def _filas(config, cid, aviso_en):
    total = len(casos.cargar_texto(cid))
    fin = aviso_en or total
    filas = []
    for n in range(1, fin + 1):
        es_aviso = (aviso_en is not None and n == aviso_en)
        filas.append({
            "config": config, "detector": "tito-slm", "modelo": MODELO,
            "prompt": "tarea", "hablantes": "ab", "case_id": cid, "linea": n,
            "hablante": "A", "texto": "t", "valida": "true", "error": "",
            "riesgo": 0.9 if es_aviso else 0.1,
            "alerta_sugerida": "true" if es_aviso else "false",
            "aviso": "true" if es_aviso else "false",
            "motivo": "m", "evidencia": "", "evidencia_en_texto": "",
            "ms": 12.0, "tokens_prompt": 10, "tokens_salida": 2, "crudo": "",
            "consulta": "slm_valida",
            "tito_puntaje": 0.9, "tito_error": "",
            "indicio_linea": 1, "indicio_texto": "t", "indicio_puntaje": 0.9,
            "tito_ms": 5.0, "slm_ms": 7.0,
            "runtime_ns": "", "runtime_unidad": "",
            "runtime_load_ns": "", "runtime_prompt_eval_ns": "", "runtime_eval_ns": "",
        })
    return filas


def escribir_corrida_102(tmp: str, aviso_perm=2, aviso_recon=2):
    base = Path(tmp)
    pref = "2026-10-29_000000_102"
    cfgs = [{"config": f"{c}|{MODELO}|tarea|ab", "detector": "tito-slm",
             "modelo": MODELO, "prompt": "tarea", "hablantes": "ab"}
            for c in ("permanente", "reconsultas")]
    manifiesto = {
        "matriz": "matriz-102", "issue": 102,
        "comando": "fixture sintética", "codigo": {"commit": "sintetico",
                    "cambios_sin_commit_en_la_carpeta": "fixture"},
        "maquina": {}, "politica_aviso": correr.POLITICA,
        "modo_termino": correr.MODO_OPERATIVO, "particion": "evaluacion_102",
        "ollama": {"url": "http://127.0.0.1:11435", "version": "sintetica",
                   "modelos": {MODELO: {"tag": MODELO, "digest": "d"}}},
        "funcionales": {"modelos": [MODELO], "casos": CASOS},
        "tito_nuevo_preparacion": {"artefacto_ms": 1, "encoder_ms": 2,
                                   "calentamiento_ms": 3, "error": ""},
        "politica_congelada": {"ganadora": "reconsultas-p3", "periodo_revision": 3,
                               "regla_nueva_evidencia": "nuevo_cruce_tras_bajar",
                               "delta_minimo": 0.0},
        "bloqueos_modelo": {}, "bloqueo_politica": "", "configs": cfgs,
        "casos": _huellas(CASOS),
        "cobertura": {"esperados_globales": 400, "planificados": 4, "completados": 4,
                      "pendientes": 396, "matriz_completa": False,
                      "faltantes": [{"modelo": MODELO, "condicion": "permanente",
                                     "caso": "OTRO", "causa": "pendiente-medicion"}]},
        "reutilizacion_101": {}, "interrumpida": False, "fin": None,
        "sintetico": True,
    }
    (base / f"{pref}_manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
    filas = (_filas(cfgs[0]["config"], CASOS[0], aviso_perm)
             + _filas(cfgs[1]["config"], CASOS[0], aviso_recon)
             + _filas(cfgs[0]["config"], CASOS[1], None)
             + _filas(cfgs[1]["config"], CASOS[1], None))
    with (base / f"{pref}_actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
        w.writeheader()
        for r in filas:
            w.writerow({c: r.get(c, "") for c in correr.COLUMNAS})
    return base / f"{pref}_manifiesto.json"


def escribir_corrida_101(tmp: str):
    base = Path(tmp)
    pref = "2026-10-29_000000_101"
    cfgs = [{"config": f"{c}|{MODELO}|tarea|ab", "detector": "tito-slm",
             "modelo": MODELO, "prompt": "tarea", "hablantes": "ab"}
            for c in ("directo", "tito-viejo", "tito-nuevo")]
    manifiesto = {
        "matriz": "matriz-101", "issue": 101,
        "comando": "fixture sintética", "codigo": {"commit": "sintetico",
                    "cambios_sin_commit_en_la_carpeta": "fixture"},
        "maquina": {}, "politica": correr.POLITICA,
        "modo_termino": correr.MODO_OPERATIVO,
        "ollama": {"url": "u", "version": "sintetica", "modelos": {}},
        "funcionales": {"modelos": [MODELO], "casos": CASOS},
        "configs": cfgs, "casos": _huellas(CASOS),
        "cobertura": {"esperados_globales": 600, "planificados": 6, "completados": 6,
                      "pendientes": 594, "matriz_completa": False, "faltantes": []},
        "sintetico": True,
    }
    (base / f"{pref}_manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
    filas = []
    for cfg, av in ((cfgs[0]["config"], 3), (cfgs[1]["config"], 3), (cfgs[2]["config"], 2)):
        filas += _filas(cfg, CASOS[0], av)
        filas += _filas(cfg, CASOS[1], None)
    with (base / f"{pref}_actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
        w.writeheader()
        for r in filas:
            w.writerow({c: r.get(c, "") for c in correr.COLUMNAS})
    return base / f"{pref}_manifiesto.json"


class TestInforme102(unittest.TestCase):
    def test_marca_sintetico_denominadores_y_lc(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            man_path = escribir_corrida_102(tmp)
            texto = informe_102.armar_informe(man_path)
            self.assertIn("DATOS SINTÉTICOS", texto)
            self.assertIn("/400 globales", texto)
            self.assertIn("reconsultas-p3", texto)
            # Vishing con TR 3 y aviso en L2: oportuno; sin TC: L_C ausente.
            self.assertIn("T_C ausente", texto)
            self.assertIn("L_C", texto)
            self.assertIn("Comparación con #101 pendiente", texto)

    def test_consolidado_separa_efecto_tito_y_politica(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            man102 = escribir_corrida_102(tmp)
            man101 = escribir_corrida_101(tmp)
            texto = informe_102.armar_informe(man102, man101)
            self.assertIn("Efecto Tito", texto)
            self.assertIn("Política (#102)", texto)
            self.assertIn("No se atribuye al entrenamiento", texto)

    def test_rechaza_deriva_del_snapshot(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            man_path = escribir_corrida_102(tmp)
            man = json.loads(man_path.read_text(encoding="utf-8"))
            man["casos"][CASOS[0]]["texto_sha256"] = "0" * 64
            man_path.write_text(json.dumps(man), encoding="utf-8")
            with self.assertRaises(ValueError):
                informe_102.armar_informe(man_path)

    def test_regenerar_escribe_informe_y_figuras(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            man_path = escribir_corrida_102(tmp)
            rc = informe_102.main(["regenerar", str(man_path)])
            self.assertEqual(rc, 0)
            base = Path(tmp)
            self.assertTrue((base / "2026-10-29_000000_102_informe_102.md").exists())
            for suf in ("_grafico102_avisos.svg", "_grafico102_avisos.png",
                        "_grafico102_costos.svg", "_grafico102_costos.png"):
                self.assertTrue((base / ("2026-10-29_000000_102" + suf)).exists(),
                                f"falta figura {suf}")


if __name__ == "__main__":
    unittest.main()
