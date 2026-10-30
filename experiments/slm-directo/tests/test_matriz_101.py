"""Matriz #101 con dobles: tres condiciones, aviso único e inventario (#95).

Usa dobles deterministas (Tito guionado, Tito99 guionado, SLM guionado,
Ollama falso) al borde de `correr.procesar_caso` y `FlujoTitoSLM`. No toca
la red, no descarga modelos ni entrena nada: las 600 corridas reales las
ejecuta `matriz_101.py` en otro momento.
"""

from __future__ import annotations

import csv
import hashlib
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
                "casos": {c: {"texto_sha256": hashlib.sha256(
                                   (casos.DIR_TEXTO / f"{c}.txt").read_bytes()).hexdigest(),
                               "referencia_sha256": hashlib.sha256(
                                   (casos.DIR_REFERENCIA / f"{c}.json").read_bytes()).hexdigest()}
                           for c in ids},
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


class TestTrazaContigua(unittest.TestCase):
    """El triple solo está completo con una secuencia única y contigua (#101.2).

    Reproducción del coordinador: 22 copias de L1 de CV2-D-L-BANCO-001
    (22 líneas) marcaban el triple completo con una sola línea única.
    """

    def _csv_sin_header(self):
        return None

    def _escribir(self, carpeta: Path, filas: list[dict], con_header: bool = True) -> None:
        with (carpeta / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
            if con_header:
                w.writeheader()
            for fila in filas:
                base = {c: "" for c in correr.COLUMNAS}
                base.update(fila)
                w.writerow(base)

    def _fila(self, config: str, cid: str, n: int, aviso: bool = False) -> dict:
        return {"config": config, "case_id": cid, "linea": n,
                "aviso": "true" if aviso else "false"}

    def test_prefijo_duplicado_no_cuenta_como_completo(self):
        cid = "CV2-D-L-BANCO-001"
        total = len(casos.cargar_texto(cid))
        self.assertGreater(total, 1)
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            filas = [self._fila("directo|m|tarea|ab", cid, 1)
                     for _ in range(total)]
            self._escribir(carpeta, filas)
            vistos = matriz_101.leer_completados(carpeta)
            self.assertNotIn(("m", "directo", cid), vistos)

    def test_hueco_en_la_secuencia_no_cuenta_como_completo(self):
        cid = matriz_101.casos_101()[0]
        total = len(casos.cargar_texto(cid))
        self.assertGreater(total, 2)
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            filas = [self._fila("directo|m|tarea|ab", cid, n)
                     for n in range(1, total + 1) if n != 2]
            self._escribir(carpeta, filas)
            self.assertNotIn(("m", "directo", cid),
                             matriz_101.leer_completados(carpeta))

    def test_aviso_en_linea_uno_es_completo_sin_duplicados(self):
        cid = matriz_101.casos_101()[0]
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            self._escribir(carpeta, [self._fila("directo|m|tarea|ab", cid, 1, aviso=True)])
            self.assertIn(("m", "directo", cid), matriz_101.leer_completados(carpeta))

    def test_reanudar_descarta_parcial_sin_duplicar(self):
        """Interrumpir antes del primer caso completo y reanudar dos veces:
        sin header duplicado ni filas repetidas, costos intactos."""
        cid = matriz_101.casos_101()[0]
        total = len(casos.cargar_texto(cid))
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            parcial = [self._fila("directo|m|tarea|ab", cid, 1),
                       self._fila("directo|m|tarea|ab", cid, 1)]
            self._escribir(carpeta, parcial)
            # Primera reanudación: el parcial se retira para remedición.
            canonicas = matriz_101.normalizar_traza(carpeta, {cid: total})
            self.assertEqual(canonicas, [])
            # Se remide el triple completo y se agrega una sola vez.
            completas = [self._fila("directo|m|tarea|ab", cid, n)
                         for n in range(1, total + 1)]
            matriz_101.agregar_filas(carpeta, completas)
            # Segunda reanudación: idempotente, sin duplicados.
            canonicas2 = matriz_101.normalizar_traza(carpeta, {cid: total})
            self.assertEqual(len(canonicas2), total)
            self.assertIn(("m", "directo", cid), matriz_101.leer_completados(carpeta))
            with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
                contenido = f.read()
            self.assertEqual(contenido.count("config,detector"), 1)
            self.assertEqual(len(canonicas2), len({(r["config"], r["linea"]) for r in canonicas2}))

    def test_csv_vacio_al_reanudar_no_pierde_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            (carpeta / "actualizaciones.csv").write_text("", encoding="utf-8-sig")
            self.assertEqual(matriz_101.leer_completados(carpeta), set())
            matriz_101.agregar_filas(carpeta, [self._fila("directo|m|tarea|ab", "X", 1)])
            with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
                lineas = f.read().splitlines()
            self.assertTrue(lineas[0].startswith("config,"))
            self.assertEqual(len(lineas), 2)


class TestCasos101Estricto(unittest.TestCase):
    def test_ids_exactos_en_orden_sin_duplicados(self):
        ids = matriz_101.casos_101()
        self.assertEqual(ids, list(matriz_101.IDS_101))
        self.assertEqual(len(set(ids)), 20)
        refs = [casos.cargar_referencia(c) for c in ids]
        self.assertEqual([r["clase"] for r in refs[:10]],
                         ["vishing"] * 10)
        self.assertTrue(all(r["clase"] in casos.LEGITIMAS for r in refs[10:]))

    def test_particiones_respaldan_las_veinte_con_hashes(self):
        huellas = matriz_101.huellas_particiones_101()
        ids = matriz_101.casos_101()
        self.assertEqual(sorted(huellas), sorted(ids))
        for cid in ids:
            self.assertEqual(huellas[cid]["particion_preparacion"], "comparacion_20")

    def test_cobertura_global_declara_600_y_causas(self):
        triples = matriz_101.plan_triples(["m"], ["directo"], matriz_101.casos_101())
        cob = matriz_101.cobertura({"qwen3.5:4b": "bloqueo de ejemplo"}, "sin candidato",
                                   triples, set())
        self.assertEqual(cob["esperados_globales"], 600)
        self.assertEqual(len(cob["faltantes"]), 600)
        self.assertFalse(cob["matriz_completa"])
        self.assertTrue(all("causa" in f for f in cob["faltantes"]))
        causas = {(f["modelo"], f["condicion"]): f["causa"] for f in cob["faltantes"]}
        self.assertEqual(causas[("qwen3.5:4b", "directo")], "modelo_bloqueado")
        self.assertEqual(causas[("qwen3.5:4b", "tito-nuevo")], "modelo_bloqueado")
        self.assertEqual(causas[("qwen3.5:2b", "tito-nuevo")], "tito-nuevo-pendiente")
        self.assertEqual(causas[("qwen3.5:2b", "directo")], "no-planificado-subset")


class TestTitoNuevoCongelado(unittest.TestCase):
    def test_sin_artefacto_queda_pendiente_antes_de_medir(self):
        with self.assertRaises(matriz_101.TitoNuevoNoDisponible):
            matriz_101.resolver_tito_nuevo(Path("no-existe.json"), None, None)

    def test_artefacto_sin_manifest_congelado_queda_pendiente(self):
        with tempfile.TemporaryDirectory() as tmp:
            arte = Path(tmp) / "candidato.json"
            arte.write_text(json.dumps({"formato": "tito-99-logreg-v1"}), encoding="utf-8")
            with self.assertRaises(matriz_101.TitoNuevoNoDisponible):
                matriz_101.resolver_tito_nuevo(arte, None, None)

    def test_entrada_frase_se_rechaza_en_texto_plano(self):
        with tempfile.TemporaryDirectory() as tmp:
            arte = Path(tmp) / "candidato.json"
            arte.write_text(json.dumps({
                "formato": "tito-99-logreg-v1", "entrada": "frase_actual_control",
                "encoder": {"id": "x", "revision": "y"},
                "tokenizador": {"tokenizer_sha256": "z"},
                "pesos": {"coef": [0.1], "intercepto": 0.0}}), encoding="utf-8")
            mani = Path(tmp) / "sel.json"
            mani.write_text(json.dumps({
                "artefacto_sha256": "0" * 64, "entrada": "frase_actual_control",
                "umbral": 0.5, "variante": "#99-congelada",
                "encoder": {"id": "x", "revision": "y"}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                matriz_101.resolver_tito_nuevo(arte, mani, None)

    def test_override_silencioso_de_umbral_se_rechaza(self):
        with tempfile.TemporaryDirectory() as tmp:
            arte = Path(tmp) / "candidato.json"
            contenido = {"formato": "tito-99-logreg-v1", "entrada": "historial_acumulado",
                         "encoder": {"id": "e", "revision": "r"},
                         "tokenizador": {"tokenizer_sha256": "t"},
                         "pesos": {"coef": [0.1], "intercepto": 0.0}}
            arte.write_text(json.dumps(contenido), encoding="utf-8")
            import hashlib
            mani = Path(tmp) / "sel.json"
            mani.write_text(json.dumps({
                "artefacto_sha256": hashlib.sha256(arte.read_bytes()).hexdigest(),
                "entrada": "historial_acumulado", "umbral": 0.7,
                "variante": "#99-congelada", "encoder": {"id": "e", "revision": "r"}}),
                encoding="utf-8")
            with self.assertRaises(ValueError):
                matriz_101.resolver_tito_nuevo(arte, mani, 0.5)

    def test_preparar_marca_warmup_invalido_sin_excepcion(self):
        class TitoError:
            def _asegurar_encoder(self):
                return None

            def puntuar_entrada(self, texto):
                return None, "tito99_error: caido", 1.0

        informe = matriz_101.preparar_tito_99(TitoError())
        self.assertTrue(informe["error"])
        self.assertFalse(informe["encoder_listo"])

    def test_preparar_rechaza_puntaje_no_finito(self):
        class TitoNan:
            def _asegurar_encoder(self):
                return None

            def puntuar_entrada(self, texto):
                return float("nan"), "", 1.0

        informe = matriz_101.preparar_tito_99(TitoNan())
        self.assertTrue(informe["error"])
        self.assertFalse(informe["encoder_listo"])


class TestInformeComponentes(unittest.TestCase):
    def _manifiesto(self, ids):
        return {
            "matriz": "matriz-101", "modo_termino": "operativo-hasta-aviso",
            "configs": [{"config": c, "detector": "slm" if c.startswith("directo") else "tito-slm",
                         "modelo": "m1", "prompt": "tarea", "hablantes": "ab"} for c in
                        ["directo|m1|tarea|ab", "tito-viejo|m1|tarea|ab"]],
            "casos": {c: {"texto_sha256": "", "referencia_sha256": "",
                          "clase": "vishing", "particion_preparacion": "comparacion_20",
                          "grupo_preparacion": "g", "revision_humana": False} for c in ids},
            "funcionales": {"modelos": ["m1"],
                            "tito_viejo": {"entrada": "frase_actual", "umbral": 0.5, "sha256": "abc"},
                            "tito_nuevo": {"bloqueo": "sin artefacto"}},
            "cobertura": {"esperados_globales": 600, "planificados": 4,
                          "completados": 4, "pendientes": 596,
                          "matriz_completa": False, "faltantes": []},
            "ollama": {"version": "0.40.8", "url": "http://x", "modelos": {
                "m1": {"tag": "m1", "digest": "d", "cuantizacion": "Q8_0",
                       "familia": "f", "tamano_parametros": "1B", "calentamiento_ms": 10}}},
            "bloqueos_modelo": {}, "bloqueo_nuevo": "sin artefacto",
            "tito_viejo_preparacion": {"artefacto_ms": 1, "encoder_ms": 2,
                                       "calentamiento_ms": 3, "unidad": "ms", "error": ""},
            "tito_nuevo_preparacion": None,
            "comando": "cmd", "codigo": {"commit": "c", "cambios_sin_commit_en_la_carpeta": False},
        }

    def test_error_arrastrado_sin_tito_ms_no_es_fallo_nuevo(self):
        filas = [{"config": "tito-viejo|m1|tarea|ab", "case_id": "c",
                  "linea": 1, "valida": "true", "consulta": "omitida",
                  "tito_ms": "5", "slm_ms": "", "tito_error": "",
                  "ms": "5", "tokens_prompt": "", "tokens_salida": ""},
                 {"config": "tito-viejo|m1|tarea|ab", "case_id": "c",
                  "linea": 2, "valida": "true", "consulta": "slm_valida",
                  "tito_ms": "", "slm_ms": "7", "tito_error": "tito_caido",
                  "ms": "7", "tokens_prompt": "10", "tokens_salida": "2"}]
        analisis_cfg = {"c": {"aviso": None, "categoria": "x", "fin": "completo-sin-aviso"}}
        det = informe_101.detalle_condicion(filas, analisis_cfg, "tito-viejo|m1|tarea|ab")
        self.assertEqual(det["c"]["fallos_tito"], 0)

    def test_informe_muestra_desglose_y_denominadores_globales(self):
        import hashlib
        ids = matriz_101.casos_101()[:2]
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            manifiesto = self._manifiesto(ids)
            for c in ids:
                txt = (casos.DIR_TEXTO / f"{c}.txt").read_bytes()
                ref = (casos.DIR_REFERENCIA / f"{c}.json").read_bytes()
                manifiesto["casos"][c]["texto_sha256"] = hashlib.sha256(txt).hexdigest()
                manifiesto["casos"][c]["referencia_sha256"] = hashlib.sha256(ref).hexdigest()
            (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
            cfgs = ["directo|m1|tarea|ab", "tito-viejo|m1|tarea|ab"]
            with (carpeta / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
                w = csv.DictWriter(f, fieldnames=correr.COLUMNAS)
                w.writeheader()
                for cfg in cfgs:
                    for cid in ids:
                        consulta = "" if cfg.startswith("directo") else "omitida"
                        fila = {c: "" for c in correr.COLUMNAS}
                        fila.update({"config": cfg, "case_id": cid, "linea": 1, "valida": "true",
                                     "error": "", "riesgo": "0.1", "alerta_sugerida": "false",
                                     "aviso": "false", "consulta": consulta, "ms": "5",
                                     "tito_ms": "1", "slm_ms": "4" if consulta == "" else "",
                                     "tokens_prompt": "10", "tokens_salida": "2"})
                        w.writerow(fila)
            texto = informe_101.armar_informe(carpeta)
            self.assertIn("600", texto)
            self.assertIn("Tito ms", texto)
            self.assertIn("SLM ms", texto)
            for cid in ids:
                self.assertIn(f"`{cid}`", texto)


if __name__ == "__main__":
    unittest.main()
