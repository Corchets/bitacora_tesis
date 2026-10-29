"""Matriz #101 con dobles: tres condiciones, aviso único e inventario (#95).

Usa dobles deterministas (Tito guionado, Tito99 guionado, SLM guionado,
Ollama falso) al borde de `correr.procesar_caso` y `FlujoTitoSLM`. No toca
la red, no descarga modelos ni entrena nada: las 600 corridas reales las
ejecuta `matriz_101.py` en otro momento.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import casos  # noqa: E402
import correr  # noqa: E402
import informe_101  # noqa: E402
import matriz_101  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import Respuesta  # noqa: E402
from filtro_tito import UMBRAL_TITO, FlujoTitoSLM  # noqa: E402

DIALOGO = [
    Linea("A", "Te llamo del banco por un movimiento sospechoso."),
    Linea("B", "¿Qué movimiento? No reconozco nada."),
    Linea("A", "Pasame el código que te llegó por SMS para bloquearlo."),
    Linea("B", "Es uno dos tres cuatro."),
]

LEGITIMO = [
    Linea("A", "El delivery llega entre las seis y las siete."),
    Linea("B", "Perfecto, lo espero en la puerta."),
    Linea("A", "Trae cambio de diez mil por las dudas."),
]


class TitoDoble:
    """Tito frase-aislada guionado: puntaje por línea y fallos programados."""

    def __init__(self, puntajes=None, fallos=frozenset(), ms_fijo=5.0):
        self.puntajes = dict(puntajes or {})
        self.fallos = set(fallos)
        self.ms_fijo = ms_fijo
        self.llamadas: list[tuple[int, str]] = []

    def puntuar(self, n, texto):
        self.llamadas.append((n, texto))
        if n in self.fallos:
            return None, "tito_caido", self.ms_fijo
        return self.puntajes.get(n, 0.0), "", self.ms_fijo


class Tito99Doble:
    """Candidato nuevo guionado: puntúa el historial acumulado recibido."""

    entrada = "historial_acumulado"

    def __init__(self, puntajes=None, ms_fijo=6.0):
        self.puntajes = dict(puntajes or {})
        self.ms_fijo = ms_fijo
        self.entradas: list[str] = []

    def puntuar_entrada(self, texto_entrada):
        self.entradas.append(texto_entrada)
        n = len(texto_entrada.splitlines())
        for linea, puntaje in self.puntajes.items():
            if n >= linea:
                return puntaje, "", self.ms_fijo
        return 0.0, "", self.ms_fijo


class SLMDoble:
    """SLM guionado: alerta en las líneas indicadas, con costo fijo."""

    def __init__(self, alertas=frozenset(), invalidas=frozenset(), ms_fijo=7.0, hablantes="ab"):
        self.alertas, self.invalidas = set(alertas), set(invalidas)
        self.ms_fijo = ms_fijo
        self.hablantes = hablantes
        self.recibido: list[tuple[str, tuple]] = []

    def evaluar_mensaje(self, usuario, lineas):
        self.recibido.append((usuario, tuple(lineas)))
        n = len(lineas)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido", ms=self.ms_fijo, slm_ms=self.ms_fijo)
        if n in self.alertas:
            return Respuesta(valida=True, alerta_sugerida=True, riesgo=0.9, motivo="pide código",
                             evidencia=lineas[-1].texto, evidencia_en_texto=True,
                             ms=self.ms_fijo, slm_ms=self.ms_fijo,
                             tokens_prompt=100, tokens_salida=20,
                             runtime_ns=1_000_000, runtime_unidad="ns", crudo="{}")
        return Respuesta(valida=True, alerta_sugerida=False, riesgo=0.1, ms=self.ms_fijo,
                         slm_ms=self.ms_fijo, tokens_prompt=100, tokens_salida=10,
                         runtime_ns=1_000_000, runtime_unidad="ns", crudo="{}")


class OllamaFalso(ClienteOllama):
    """Inventario fijo: tags exactos, digests, cuantización y versión."""

    def __init__(self):
        super().__init__("http://127.0.0.1:11435", 5.0)

    def _pedir(self, ruta, cuerpo=None):
        if ruta == "/api/version":
            return {"version": "0.40.8-falso"}
        if ruta == "/api/tags":
            return {"models": [
                {"name": "qwen3.5:4b", "digest": "d8b0falso"},
                {"name": "gemma3:270m", "digest": "e7d36falso"},
            ]}
        if ruta == "/api/show":
            return {"details": {"quantization_level": "Q8_0", "family": "gemma3",
                                "parameter_size": "270M", "format": "gguf"},
                    "modified_at": "2026-10-01T00:00:00Z"}
        raise AssertionError(f"ruta inesperada: {ruta}")


class TestMatrizDefinicion(unittest.TestCase):
    def test_modelos_exactos_en_orden(self):
        self.assertEqual(list(matriz_101.MODELOS_101), [
            "qwen3.5:4b", "qwen3.5:2b", "gemma:2b", "gemma3:270m", "gemma3:1b",
            "gemma3:4b", "gemma3n:e2b", "gemma3n:e4b", "gemma4:e2b", "gemma4:e4b",
        ])

    def test_casos_son_las_veinte_aprobadas(self):
        ids = matriz_101.casos_101()
        self.assertEqual(len(ids), 20)
        refs = [casos.cargar_referencia(c) for c in ids]
        clases = [r["clase"] for r in refs]
        self.assertEqual(clases.count("vishing"), 10)
        self.assertEqual(sum(1 for c in clases if c in casos.LEGITIMAS), 10)

    def test_plan_es_600_recorridos(self):
        triples = matriz_101.plan_triples(list(matriz_101.MODELOS_101),
                                          list(matriz_101.CONDICIONES),
                                          matriz_101.casos_101())
        self.assertEqual(len(triples), 600)
        self.assertEqual(len(set(triples)), 600)


class TestTresCondiciones(unittest.TestCase):
    def test_misma_base_slm_y_politica_compartida(self):
        slm = SLMDoble()
        cfgs = matriz_101.construir_detectores(
            "qwen3.5:2b", "prompt", "tarea", "ab", None, 4096, 42, None, {},
            TitoDoble(), 0.5, Tito99Doble(), 0.5)
        self.assertEqual([c["config"] for c, _ in cfgs],
                         ["directo|qwen3.5:2b|tarea|ab",
                          "tito-viejo|qwen3.5:2b|tarea|ab",
                          "tito-nuevo|qwen3.5:2b|tarea|ab"])
        directo = cfgs[0][1]
        self.assertIs(cfgs[1][1].slm, directo)
        self.assertIs(cfgs[2][1].slm, directo)
        self.assertIsInstance(cfgs[1][1], FlujoTitoSLM)
        self.assertIsInstance(cfgs[2][1], matriz_101.FlujoTitoHistorialSLM)
        self.assertEqual(cfgs[1][1].umbral, cfgs[2][1].umbral)

    def test_aviso_unico_incluso_en_legitima(self):
        slm = SLMDoble(alertas={2})
        flujo = FlujoTitoSLM(TitoDoble(puntajes={1: 0.9}), slm, UMBRAL_TITO)
        vistas = list(correr.procesar_caso(flujo, LEGITIMO, detener_en_aviso=True))
        self.assertEqual([n for n, _, _, _ in vistas], [1, 2])
        avisos = [a for _, _, _, a in vistas]
        self.assertEqual(avisos, [False, True])

    def test_fallo_tecnico_deriva_sin_fabricar_sospecha(self):
        slm = SLMDoble()
        flujo = FlujoTitoSLM(TitoDoble(fallos={1}), slm, UMBRAL_TITO)
        vistas = list(correr.procesar_caso(flujo, DIALOGO, detener_en_aviso=True))
        n, _, r, aviso = vistas[0]
        self.assertEqual(n, 1)
        self.assertTrue(r.valida)
        self.assertFalse(aviso)
        self.assertEqual(r.consulta, "slm_valida")
        self.assertEqual(r.tito_error, "tito_caido")
        self.assertIsNone(r.tito_puntaje)
        self.assertIsNone(r.indicio_linea)
        self.assertEqual(r.indicio_texto, "")
        self.assertIn("falló técnicamente", slm.recibido[0][0])
        self.assertNotIn("puntaje", slm.recibido[0][0].split("No hay puntaje")[0].split("filtro previo")[-1])

    def test_historial_acumulado_sin_lineas_futuras(self):
        tito99 = Tito99Doble(puntajes={3: 0.8})
        slm = SLMDoble(alertas={3})
        flujo = matriz_101.FlujoTitoHistorialSLM(tito99, slm, 0.5)
        vistas = list(correr.procesar_caso(flujo, DIALOGO, detener_en_aviso=True))
        self.assertEqual(vistas[-1][0], 3)
        self.assertTrue(vistas[-1][3])
        import entrenar_tito_99

        esperado = entrenar_tito_99.construir_entrada(
            ["A: " + DIALOGO[0].texto, "B: " + DIALOGO[1].texto, "A: " + DIALOGO[2].texto],
            "historial_acumulado")
        self.assertEqual(tito99.entradas[-1], esperado)
        self.assertNotIn(DIALOGO[3].texto, tito99.entradas[-1])
        self.assertEqual(flujo.estado.indicio_linea, 3)

    def test_flujo_por_defecto_sigue_puntuando_el_fragmento(self):
        tito = TitoDoble(puntajes={2: 0.9})
        flujo = FlujoTitoSLM(tito, SLMDoble(), UMBRAL_TITO)
        list(correr.procesar_caso(flujo, DIALOGO, detener_en_aviso=True))
        self.assertEqual(tito.llamadas[0], (1, DIALOGO[0].texto))
        self.assertEqual(tito.llamadas[1], (2, DIALOGO[1].texto))


class TestInventario(unittest.TestCase):
    def test_registra_tag_digest_cuantizacion_y_runtime(self):
        ficha = matriz_101.inventario_modelo(OllamaFalso(), "qwen3.5:4b")
        self.assertEqual(ficha, {"tag": "qwen3.5:4b", "digest": "d8b0falso",
                                 "cuantizacion": "Q8_0", "familia": "gemma3",
                                 "tamano_parametros": "270M", "formato": "gguf",
                                 "show_modified_at": "2026-10-01T00:00:00Z"})

    def test_tag_inexacto_no_se_sustituye(self):
        with self.assertRaises(LookupError):
            matriz_101.inventario_modelo(OllamaFalso(), "qwen3.5:4b-q4_K_M")


class TestCoberturaYReanudacion(unittest.TestCase):
    def _csv(self, carpeta: Path, filas: list[dict]) -> None:
        with (carpeta / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
            w.writeheader()
            for fila in filas:
                base = {c: "" for c in correr.COLUMNAS}
                base.update(fila)
                w.writerow(base)

    def test_completados_aviso_o_caso_entero(self):
        cid = matriz_101.casos_101()[0]
        total = len(casos.cargar_texto(cid))
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            filas = [{"config": "directo|m|tarea|ab", "case_id": cid, "linea": 1, "aviso": "true"}]
            filas += [{"config": "tito-viejo|m|tarea|ab", "case_id": cid,
                       "linea": n, "aviso": "false"} for n in range(1, total + 1)]
            filas += [{"config": "tito-nuevo|m|tarea|ab", "case_id": cid,
                       "linea": n, "aviso": "false"} for n in range(1, total)]
            self._csv(carpeta, filas)
            vistos = matriz_101.leer_completados(carpeta)
            self.assertIn(("m", "directo", cid), vistos)
            self.assertIn(("m", "tito-viejo", cid), vistos)
            self.assertNotIn(("m", "tito-nuevo", cid), vistos)

    def test_huella_cambia_si_cambia_la_configuracion(self):
        a = {"modelos": ["m"], "umbral": 0.5}
        b = {"modelos": ["m"], "umbral": 0.7}
        self.assertNotEqual(matriz_101.huella_funcional(a), matriz_101.huella_funcional(b))
        self.assertEqual(matriz_101.huella_funcional(a), matriz_101.huella_funcional(dict(a)))


class TestInformeRegenerable(unittest.TestCase):
    def test_tablas_por_modelo_y_caso_sin_inferencia(self):
        ids = matriz_101.casos_101()[:2]
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            cfgs = ["directo|m1|tarea|ab", "tito-viejo|m1|tarea|ab"]
            manifiesto = {
                "matriz": "matriz-101", "modo_termino": "operativo-hasta-aviso",
                "configs": [{"config": c, "detector": "slm" if c.startswith("directo") else "tito-slm",
                             "modelo": "m1", "prompt": "tarea", "hablantes": "ab"} for c in cfgs],
                "casos": {c: "sha" for c in ids},
                "funcionales": {"modelos": ["m1"],
                                "tito_viejo": {"entrada": "frase_actual", "umbral": 0.5, "sha256": "abc"},
                                "tito_nuevo": {"bloqueo": "sin artefacto"}},
                "cobertura": {"esperados": 4, "completados": 4, "pendientes": 0},
                "ollama": {"version": "0.40.8", "url": "http://x", "modelos": {
                    "m1": {"tag": "m1", "digest": "d", "cuantizacion": "Q8_0",
                           "familia": "f", "tamano_parametros": "1B", "calentamiento_ms": 10}}},
                "bloqueos_modelo": {}, "bloqueo_nuevo": "sin artefacto",
                "tito_viejo_preparacion": {"artefacto_ms": 1, "encoder_ms": 2,
                                           "calentamiento_ms": 3, "unidad": "ms", "error": ""},
                "tito_nuevo_preparacion": None,
                "comando": "cmd", "codigo": {"commit": "c", "cambios_sin_commit_en_la_carpeta": False},
            }
            (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
            filas = []
            for cfg in cfgs:
                for cid in ids:
                    consulta = "" if cfg.startswith("directo") else "omitida"
                    filas.append({"config": cfg, "case_id": cid, "linea": 1, "valida": "true",
                                  "error": "", "riesgo": "0.1", "alerta_sugerida": "false",
                                  "aviso": "false", "consulta": consulta, "ms": "5",
                                  "tito_ms": "1", "slm_ms": "4" if consulta == "" else "",
                                  "tokens_prompt": "10", "tokens_salida": "2"})
            with (carpeta / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
                w.writeheader()
                for fila in filas:
                    base = {c: "" for c in correr.COLUMNAS}
                    base.update(fila)
                    w.writerow(base)
            texto = informe_101.armar_informe(carpeta)
            self.assertIn("## `m1`", texto)
            for cid in ids:
                self.assertIn(f"`{cid}`", texto)
            self.assertIn("tito-nuevo pendiente", texto)
            self.assertIn("Sin criterio de aceptación", texto)


if __name__ == "__main__":
    unittest.main()
