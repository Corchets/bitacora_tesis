"""Primer aviso e instrumentación separada Tito/SLM (#97, parte de #95).

Recorrido operativo con dobles deterministas, sin modelos ni descargas:
directo y filtrado terminan al primer aviso válido (incluida una falsa
alarma), solo el SLM emite, el fin normal se distingue de interrupción y
fallo, y la traza separa arranque/calentamiento/actualización con costos
Tito/SLM sin doble conteo.

Estos dobles verifican software, no calidad aprendida: el SLM guionado
avisa ante pedido explícito y TitoGuion puntúa por línea programada.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import comparar  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
import tito_real  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import DetectorSLM, Respuesta, cargar_prompt  # noqa: E402
from filtro_tito import UMBRAL_TITO, FlujoTitoSLM, TitoGuion  # noqa: E402
from test_ensayo import OllamaFalso  # noqa: E402

DIALOGO = [
    Linea("A", "Te llamo de soporte por la activación de tu cuenta de WhatsApp."),
    Linea("B", "Me acaba de llegar un SMS. No pedí activar nada."),
    Linea("A", "Para cancelar esa activación tenemos que resolverlo ahora."),
    Linea("A", "Decime el código de activación que recibiste por SMS."),
    Linea("B", "Es cero, cero, cero, cero, cero, cero."),
]

LEGITIMA = [
    Linea("A", "Me llegó por SMS un código para activar WhatsApp y yo no lo pedí."),
    Linea("B", "No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación."),
    Linea("A", "¿Necesitás verlo para ayudarme?"),
    Linea("B", "No. No hace falta que me digas ningún código."),
]


class DetectorGuion:
    """Directo falso: alerta en las líneas indicadas, inválido en otras."""

    nombre = "guion"

    def __init__(self, alertas=frozenset(), invalidas=frozenset()):
        self.alertas, self.invalidas = set(alertas), set(invalidas)
        self.recibido = []

    def evaluar(self, lineas):
        self.recibido.append(tuple(lineas))
        n = len(lineas)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido")
        alerta = n in self.alertas
        return Respuesta(valida=True, riesgo=0.9 if alerta else 0.1,
                         alerta_sugerida=alerta, motivo="m" if alerta else "")


class SLMGuion:
    """SLM falso con costo fijo por componente trazable."""

    def __init__(self, alertas=frozenset(), invalidas=frozenset(), ms_fijo=7.0, hablantes="ab"):
        self.alertas, self.invalidas = set(alertas), set(invalidas)
        self.ms_fijo, self.hablantes = ms_fijo, hablantes
        self.recibido = []

    def evaluar_mensaje(self, usuario, lineas):
        self.recibido.append((usuario, tuple(lineas)))
        n = len(lineas)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido", ms=self.ms_fijo)
        alerta = n in self.alertas
        return Respuesta(valida=True, riesgo=0.9 if alerta else 0.1,
                         alerta_sugerida=alerta, motivo="m" if alerta else "",
                         ms=self.ms_fijo)


def flujo(puntajes=None, fallos=None, alertas=frozenset(), invalidas=frozenset()):
    return FlujoTitoSLM(TitoGuion(puntajes, fallos, ms_fijo=5.0),
                        SLMGuion(alertas, invalidas), UMBRAL_TITO)


class TestFrenoAlPrimerAviso(unittest.TestCase):
    def test_directo_termina_en_el_primer_aviso_y_no_evalua_despues(self):
        salidas = list(correr.procesar_caso(DetectorGuion(alertas={2, 4}), DIALOGO))
        self.assertEqual([aviso for *_, aviso in salidas], [False, True])
        self.assertEqual([n for n, _, _, _ in salidas], [1, 2])

    def test_falsa_alarma_tambien_termina_la_llamada(self):
        salidas = list(correr.procesar_caso(DetectorGuion(alertas={3}), LEGITIMA))
        self.assertEqual([aviso for *_, aviso in salidas], [False, False, True])

    def test_filtrado_termina_en_el_primer_aviso_valido(self):
        f = flujo(puntajes={1: 0.7}, alertas={2, 4})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual([aviso for *_, aviso in salidas], [False, True])
        self.assertEqual(len(f.slm.recibido), 2, "el SLM no se consulta tras el aviso")

    def test_sin_aviso_llega_hasta_el_final(self):
        salidas = list(correr.procesar_caso(DetectorGuion(), DIALOGO))
        self.assertEqual(len(salidas), len(DIALOGO))
        self.assertTrue(all(av is False for *_, av in salidas))

    def test_modo_diagnostico_conserva_la_conversacion_completa(self):
        salidas = list(correr.procesar_caso(DetectorGuion(alertas={2, 4}), DIALOGO,
                                            detener_en_aviso=False))
        self.assertEqual([aviso for *_, aviso in salidas],
                         [False, True, False, False, False])
        self.assertTrue(salidas[3][2].alerta_sugerida)


class TestSoloElSLMEmite(unittest.TestCase):
    def test_puntaje_alto_de_tito_no_avisa_sin_el_slm(self):
        f = flujo(puntajes={1: 0.99})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual(len(salidas), len(DIALOGO))
        self.assertTrue(all(av is False for *_, av in salidas))
        self.assertTrue(all(r.consulta != "omitida" or not r.alerta_sugerida
                            for _, _, r, _ in salidas))

    def test_omitida_nunca_es_alerta_ni_fallo(self):
        f = flujo()
        (r,) = [r for _, _, r, _ in correr.procesar_caso(f, DIALOGO[:1])]
        self.assertTrue(r.valida)
        self.assertFalse(r.alerta_sugerida)
        self.assertEqual(r.consulta, "omitida")
        self.assertEqual(r.error, "")


class TestCostosSeparados(unittest.TestCase):
    def test_tito_y_slm_se_suman_sin_doble_conteo(self):
        f = flujo(puntajes={2: 0.9}, alertas={2})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual(len(salidas), 2)
        omitida, aviso = (r for _, _, r, _ in salidas)
        self.assertEqual((omitida.tito_ms, omitida.slm_ms), (5.0, None))
        self.assertEqual(omitida.ms, 5.0)
        self.assertEqual((aviso.tito_ms, aviso.slm_ms), (5.0, 7.0))
        self.assertEqual(aviso.ms, 12.0)
        total = sum(r.ms for _, _, r, _ in salidas)
        componentes = sum((r.tito_ms or 0.0) + (r.slm_ms or 0.0) for _, _, r, _ in salidas)
        self.assertEqual(total, 17.0)
        self.assertEqual(total, componentes)

    def test_tras_activar_tito_no_vuelve_a_puntuar(self):
        f = flujo(puntajes={1: 0.9}, alertas={2})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual([r.consulta for _, _, r, _ in salidas], ["slm_valida"] * 2)
        segunda = salidas[1][2]
        self.assertIsNone(segunda.tito_ms, "Tito no corre tras activar: ausencia explícita")
        self.assertEqual(segunda.ms, segunda.slm_ms)


class TestEstadoYFallos(unittest.TestCase):
    def test_estado_limpio_entre_llamadas(self):
        f = flujo(puntajes={1: 0.9}, alertas={1})
        primera = list(correr.procesar_caso(f, DIALOGO))
        segunda = list(correr.procesar_caso(f, LEGITIMA))
        self.assertEqual([av for *_, av in primera].count(True), 1)
        self.assertEqual(segunda[0][2].consulta, "slm_valida")
        self.assertEqual(segunda[0][2].indicio_linea, 1)
        self.assertIn(LEGITIMA[0].texto, f.slm.recibido[len(primera)][0])

    def test_fallo_de_tito_deriva_sin_sospecha_inventada(self):
        f = flujo(fallos={1}, alertas={1})
        (r,) = [r for _, _, r, _ in correr.procesar_caso(f, DIALOGO[:1])]
        self.assertEqual(r.consulta, "slm_valida")
        self.assertIsNone(r.tito_puntaje)
        self.assertIsNone(r.indicio_linea)
        self.assertEqual(r.tito_error, "tito_caido")
        self.assertIn("falló técnicamente (tito_caido)", f.slm.recibido[0][0])
        self.assertNotIn("puntaje", f.slm.recibido[0][0].split("falló técnicamente")[1].split(".")[0])

    def test_salida_invalida_del_slm_no_avisa(self):
        f = flujo(puntajes={2: 0.9}, invalidas={2})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual(len(salidas), len(DIALOGO))
        segunda = salidas[1][2]
        self.assertFalse(segunda.valida)
        self.assertEqual(segunda.consulta, "slm_fallo")
        self.assertTrue(all(av is False for *_, av in salidas))


class TestCompatibilidadHistorica(unittest.TestCase):
    """Trazas viejas (sin tito_ms/slm_ms/runtime ni modo) se leen sin romper.

    Los parciales por componente se muestran como ausencia (—), no como cero.
    """

    def _corrida_vieja(self, tmp):
        import casos
        manifiesto = {
            "comando": "python correr.py --modelos m",
            "inicio": "2026-10-26T00:00:00", "fin": "2026-10-26T00:01:00",
            "interrumpida": False,
            "codigo": {"commit": "abc", "cambios_sin_commit_en_la_carpeta": False},
            "maquina": {"sistema": "x", "nucleos_logicos": 1, "ram_total_gb": 1.0},
            "politica": "aviso_unico_primer_true_valido",
            "particion": "desarrollo",
            "ollama": {"url": "u", "version": "0.0", "digests": {}},
            "parametros_slm": {}, "prompts": {},
            "configs": [
                {"config": "slm|m|tarea|ab", "detector": "slm", "modelo": "m",
                 "prompt": "tarea", "hablantes": "ab"},
                {"config": "tito-slm|m|tarea|ab", "detector": "tito-slm", "modelo": "m",
                 "prompt": "tarea", "hablantes": "ab"},
            ],
            "casos": {"SC-WA-CODE-01-e01": "x", "LG-WA-CONSULTA-01-e01": "x"},
            "modelos": {}, "filtro_tito": {"tito": "guion-simulado", "umbral": 0.5},
        }
        lineas = {c: casos.cargar_texto(c) for c in ("SC-WA-CODE-01-e01", "LG-WA-CONSULTA-01-e01")}
        filas = []
        for cfg in ("slm|m|tarea|ab", "tito-slm|m|tarea|ab"):
            for cid, ls in lineas.items():
                for n, l in enumerate(ls, start=1):
                    avisa = cid == "SC-WA-CODE-01-e01" and n == 4
                    filas.append({
                        "config": cfg, "case_id": cid, "linea": str(n),
                        "hablante": l.hablante, "texto": l.texto,
                        "valida": "true", "error": "", "riesgo": "0.9" if avisa else "0.1",
                        "alerta_sugerida": "true" if avisa else "false",
                        "aviso": "true" if avisa else "false",
                        "motivo": "m" if avisa else "", "evidencia": "", "evidencia_en_texto": "",
                        "ms": "3.0", "tokens_prompt": "10", "tokens_salida": "2",
                        "crudo": "{}", "consulta": "slm_valida" if cfg.startswith("tito") and n >= 4 else "",
                        "tito_puntaje": "", "tito_error": "", "indicio_linea": "",
                        "indicio_texto": "", "indicio_puntaje": "",
                    })
        carpeta = Path(tmp) / "corrida-vieja"
        carpeta.mkdir()
        (carpeta / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
        import csv as _csv
        with (carpeta / "actualizaciones.csv").open("w", newline="",
                                                    encoding="utf-8-sig") as fh:
            w = _csv.DictWriter(fh, fieldnames=list(filas[0]))
            w.writeheader()
            w.writerows(filas)
        return carpeta

    def test_fallbacks_explicitos(self):
        import tempfile as _tmp
        with _tmp.TemporaryDirectory() as tmp:
            carpeta = self._corrida_vieja(tmp)
            manifiesto, filas = resumen.leer_corrida(carpeta)
            analisis = resumen.analizar(manifiesto, filas)
            for cfg in ("slm|m|tarea|ab", "tito-slm|m|tarea|ab"):
                self.assertEqual(analisis[cfg]["SC-WA-CODE-01-e01"]["fin"], "aviso")
                self.assertEqual(analisis[cfg]["LG-WA-CONSULTA-01-e01"]["fin"],
                                 "completo-sin-aviso")
                self.assertFalse(analisis[cfg]["SC-WA-CODE-01-e01"]["tiene_costos_split"])
            with redirect_stdout(io.StringIO()):
                texto_res = resumen.armar_resumen(carpeta)
                comparar.main([str(carpeta)])
                texto_comp = (carpeta / "comparacion.md").read_text(encoding="utf-8")
            self.assertIn("no informado (corrida histórica, conversación completa)", texto_res)
            self.assertIn("no están disponibles y se muestran como —", texto_res)
            self.assertIn("componentes Tito/SLM no informados en esta traza histórica", texto_comp)
            for texto in (texto_res, texto_comp):
                self.assertIn("reconstrucción descriptiva del prefijo", texto.lower())
                self.assertIn("ni el costo completo", texto)
                self.assertNotIn("cubren todas las líneas", texto)
            detalle = resumen.analisis_filtro(manifiesto, filas, analisis)
            for cs in detalle.values():
                for c in cs.values():
                    self.assertNotIn("consultas_completa", c)


class OllamaConDuracion(OllamaFalso):
    """Variante que sí informa duraciones del runtime (nanosegundos)."""

    def do_POST(self):
        longitud = int(self.headers["Content-Length"])
        pedido = json.loads(self.rfile.read(longitud))
        OllamaFalso.pedidos.append(pedido)
        if "ok" in pedido.get("format", {}).get("properties", {}):  # calentamiento
            self._responder({"message": {"role": "assistant",
                                         "content": json.dumps({"ok": True})},
                             "total_duration": 999}, 200)
            return
        usuario = pedido["messages"][-1]["content"]
        contenido = json.dumps({"riesgo": 0.1, "alerta_sugerida": False,
                                "motivo": "", "evidencia": ""})
        if "Decime el código" in usuario:
            contenido = json.dumps({"riesgo": 0.95, "alerta_sugerida": True,
                                    "motivo": "Te piden un código",
                                    "evidencia": "Decime el código de activación"})
        self._responder({"message": {"role": "assistant", "content": contenido},
                         "prompt_eval_count": 100, "eval_count": 10,
                         "total_duration": 123456789, "load_duration": 1000},
                        200)


class TestPuntaAPunta(unittest.TestCase):
    def _correr(self, tito_puntajes="", tito_fallo_en="", casos=None, servidor_cls=OllamaFalso,
                extra_args=()):
        servidor = HTTPServer(("127.0.0.1", 0), servidor_cls)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                rc = correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--casos", casos or "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--filtro-tito", "--tito-puntajes", tito_puntajes,
                    "--tito-fallo-en", tito_fallo_en,
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp.name, *extra_args,
                ])
                self.assertEqual(rc, 0)
                (carpeta,) = Path(tmp.name).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                filas = resumen.leer_corrida(carpeta)[1]
                analisis = resumen.analizar(manifiesto, filas)
            return manifiesto, filas, analisis, carpeta, tmp
        except Exception:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()
            raise

    def test_aviso_corta_y_sin_aviso_conserva_denominador(self):
        servidor_cls = OllamaFalso
        servidor = HTTPServer(("127.0.0.1", 0), servidor_cls)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                # Tito deriva en L4 de cada caso; el SLM avisa ante pedido explícito.
                correr.main(["--modelos", "modelo-falso:1b",
                             "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                             "--filtro-tito", "--tito-puntajes", "4=0.9",
                             "--url", f"http://127.0.0.1:{servidor.server_port}",
                             "--salida", tmp.name])
                (carpeta,) = Path(tmp.name).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                filas = resumen.leer_corrida(carpeta)[1]
                analisis = resumen.analizar(manifiesto, filas)
            directa = "slm|modelo-falso:1b|tarea|ab"
            filtrada = "tito-slm|modelo-falso:1b|tarea|ab"
            # Ambas variantes cortan al avisar; ninguna fila posterior al aviso.
            for cfg in (directa, filtrada):
                avisos = [int(r["linea"]) for r in filas if r["config"] == cfg and r["aviso"] == "true"]
                self.assertEqual(len(avisos), 1)
                posteriores = [r for r in filas if r["config"] == cfg and r["case_id"] == "SC-WA-CODE-01-e01"
                               and int(r["linea"]) > avisos[0]]
                self.assertEqual(posteriores, [])
            # La legítima llega hasta el final y conserva su denominador.
            self.assertEqual(analisis[filtrada]["LG-WA-CONSULTA-01-e01"]["categoria"],
                             "sin_aviso_correcto")
            self.assertEqual(analisis[filtrada]["LG-WA-CONSULTA-01-e01"]["fin"], "completo-sin-aviso")
            self.assertEqual(analisis[filtrada]["SC-WA-CODE-01-e01"]["fin"], "aviso")
            m = resumen.metricas(analisis[filtrada])
            self.assertEqual(m["sin_evaluar"], 0)
            self.assertEqual((m["vishing"], m["legitimas"]), (1, 1))
            # Modo operativo declarado en el manifiesto.
            self.assertEqual(manifiesto["modo_termino"], "operativo-hasta-aviso")
            # Sin doble conteo: el total por caso reconstruye Tito+SLM.
            detalle = resumen.analisis_filtro(manifiesto, filas, analisis)[filtrada]
            for cid, c in detalle.items():
                self.assertAlmostEqual(c["ms_total"], c["tito_ms_total"] + c["slm_ms_total"])
            # Costos hasta el aviso y reporte comparativo regenerable.
            with redirect_stdout(io.StringIO()):
                resumen.main([str(carpeta)])
                comparar.main([str(carpeta)])
                texto = (carpeta / "comparacion.md").read_text(encoding="utf-8")
                resumen_txt = (carpeta / "resumen.md").read_text(encoding="utf-8")
            self.assertIn("hasta el aviso", resumen_txt)
            self.assertIn("hasta el aviso", texto)
        finally:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()

    def test_diagnostico_completo_se_identifica_y_no_mezcla_costos(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                correr.main(["--modelos", "modelo-falso:1b",
                             "--casos", "SC-WA-CODE-01-e01",
                             "--filtro-tito", "--tito-puntajes", "4=0.9",
                             "--seguir-tras-aviso",
                             "--url", f"http://127.0.0.1:{servidor.server_port}",
                             "--salida", tmp.name])
                (carpeta,) = Path(tmp.name).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                filas = resumen.leer_corrida(carpeta)[1]
            self.assertEqual(manifiesto["modo_termino"], "diagnostico-completo")
            directas = [r for r in filas if r["config"] == "slm|modelo-falso:1b|tarea|ab"]
            self.assertEqual(len(directas), 5, "el diagnóstico recorre la conversación completa")
            with redirect_stdout(io.StringIO()):
                resumen.main([str(carpeta)])
                texto = (carpeta / "resumen.md").read_text(encoding="utf-8")
            self.assertIn("diagnostico-completo", texto)
        finally:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()

    def test_runtime_ausente_explicito_y_presente_con_unidad(self):
        for servidor_cls, esperado_ns, esperado_unidad in ((OllamaFalso, "", ""),
                                                           (OllamaConDuracion, "123456789", "ns")):
            servidor = HTTPServer(("127.0.0.1", 0), servidor_cls)
            threading.Thread(target=servidor.serve_forever, daemon=True).start()
            tmp = tempfile.TemporaryDirectory()
            try:
                with redirect_stdout(io.StringIO()):
                    correr.main(["--modelos", "modelo-falso:1b",
                                 "--casos", "SC-WA-CODE-01-e01",
                                 "--url", f"http://127.0.0.1:{servidor.server_port}",
                                 "--salida", tmp.name])
                    (carpeta,) = Path(tmp.name).iterdir()
                    filas = [r for r in resumen.leer_corrida(carpeta)[1]
                             if r["config"] == "slm|modelo-falso:1b|tarea|ab"]
                consultadas = [r for r in filas if r["valida"] == "true"]
                self.assertTrue(consultadas)
                for r in consultadas:
                    self.assertEqual(r["runtime_ns"], esperado_ns)
                    self.assertEqual(r["runtime_unidad"], esperado_unidad)
            finally:
                servidor.shutdown()
                servidor.server_close()
                tmp.cleanup()


class TitoDoblePreparacion(tito_real.TitoReal):
    """TitoReal sin modelos: embeddings fijos y carga de encoder simulada."""

    def __init__(self, artefacto=tito_real.ARTEFACTO_POR_DEFECTO, falla=False):
        super().__init__(artefacto)
        self.falla = falla
        self.vec_cero = [0.0] * len(self.coef)
        self.vec_alto = [c * 0.5 for c in self.coef]

    def _asegurar_encoder(self):
        if self.falla:
            raise RuntimeError("encoder caído")
        self.encoder = object()
        return None, self.encoder, None, True

    def _embed(self, textos):
        if self.falla:
            raise RuntimeError("encoder caído")
        return [self.vec_alto if t == "sospechoso" else self.vec_cero for t in textos]


class TestPreparacionTitoReal(unittest.TestCase):
    def test_preparar_separa_costos_y_no_cambia_puntajes(self):
        tito = TitoDoblePreparacion()
        p_antes, _, _ = tito.puntuar(1, "sospechoso")
        informe = tito.preparar()
        self.assertEqual(informe["error"], "")
        self.assertEqual(informe["unidad"], "ms")
        self.assertGreaterEqual(informe["encoder_ms"], 0.0)
        self.assertGreaterEqual(informe["calentamiento_ms"], 0.0)
        self.assertIs(tito.preparacion, informe)
        # El calentamiento no cambia el estado: mismo texto, mismo puntaje.
        p_despues, _, ms = tito.puntuar(1, "sospechoso")
        self.assertEqual(p_antes, p_despues)
        self.assertGreaterEqual(p_despues, 0.5)
        self.assertGreaterEqual(ms, 0.0)

    def test_preparar_una_vez_por_proceso_y_diferencia_cache(self):
        original = tito_real.TitoReal
        tito_real.TitoReal = TitoDoblePreparacion
        try:
            _, primero = tito_real.preparar_tito_real()
            _, segundo = tito_real.preparar_tito_real()
        finally:
            tito_real.TitoReal = original
        for informe in (primero, segundo):
            self.assertEqual(informe["error"], "")
            for clave in ("artefacto_ms", "encoder_ms", "calentamiento_ms"):
                self.assertGreaterEqual(informe[clave], 0.0)
        # El artefacto ya estaba en caché del proceso: se informa, no se mide dos veces.
        self.assertTrue(segundo["artefacto_desde_cache"])

    def test_preparar_fallo_no_levanta_y_puntuar_es_fail_open(self):
        tito = TitoDoblePreparacion(falla=True)
        informe = tito.preparar()
        self.assertTrue(informe["error"])
        self.assertIsNone(informe["calentamiento_ms"])
        puntaje, error, ms = tito.puntuar(1, "hola")
        self.assertIsNone(puntaje)
        self.assertTrue(error)
        self.assertGreaterEqual(ms, 0.0)


class ClienteFalsoDuraciones:
    """Chat falso con duraciones del runtime configurables."""

    def __init__(self, duraciones=None):
        self.duraciones = dict(duraciones or {})

    def chat(self, modelo, mensajes, formato, opciones, pensar=None):
        if "ok" in (formato or {}).get("properties", {}):  # calentamiento de correr.py
            contenido = json.dumps({"ok": True})
        else:
            contenido = json.dumps({"riesgo": 0.1, "alerta_sugerida": False,
                                    "motivo": "", "evidencia": ""})
        cuerpo = {"message": {"role": "assistant", "content": contenido},
                  "prompt_eval_count": 100, "eval_count": 10}
        cuerpo.update(self.duraciones)
        return cuerpo

    def memoria_cargada(self, modelo):
        return None


class TestRuntimeSLMSeparado(unittest.TestCase):
    DURACIONES = {"total_duration": 123456789, "load_duration": 1000,
                  "prompt_eval_duration": 2000, "eval_duration": 3000}

    def test_evaluar_registra_cada_duracion_y_su_ausencia(self):
        d = DetectorSLM(ClienteFalsoDuraciones(self.DURACIONES), "m", cargar_prompt("tarea"))
        r = d.evaluar(DIALOGO[:1])
        self.assertTrue(r.valida)
        self.assertEqual((r.runtime_ns, r.runtime_unidad), (123456789, "ns"))
        self.assertEqual(r.runtime_load_ns, 1000)
        self.assertEqual(r.runtime_prompt_eval_ns, 2000)
        self.assertEqual(r.runtime_eval_ns, 3000)

    def test_sin_duraciones_todo_es_ausencia_explicita(self):
        d = DetectorSLM(ClienteFalsoDuraciones(), "m", cargar_prompt("tarea"))
        r = d.evaluar(DIALOGO[:1])
        self.assertTrue(r.valida)
        self.assertIsNone(r.runtime_ns)
        self.assertEqual(r.runtime_unidad, "")
        self.assertIsNone(r.runtime_load_ns)
        self.assertIsNone(r.runtime_prompt_eval_ns)
        self.assertIsNone(r.runtime_eval_ns)

    def test_calentar_no_finge_separacion(self):
        cal = correr.calentar(ClienteFalsoDuraciones(self.DURACIONES), "m", 4096)
        self.assertEqual(cal["carga_ms"], cal["calentamiento_ms"], "alias histórico del mismo valor")
        self.assertEqual(cal["runtime_load_ns"], 1000, "el runtime informa la carga, no la pared")
        self.assertEqual(cal["runtime_total_ns"], 123456789)
        ausente = correr.calentar(ClienteFalsoDuraciones(), "m", 4096)
        self.assertIsNone(ausente["runtime_load_ns"])
        self.assertIsNone(ausente["runtime_total_ns"])


def _fila_modo(config, case_id, n, *, aviso=False, valida=True, consulta="slm_valida",
               runtime="123", ms="3.0"):
    return {"config": config, "case_id": case_id, "linea": str(n),
            "valida": "true" if valida else "false", "error": "" if valida else "x",
            "riesgo": "0.9" if aviso else "0.1",
            "alerta_sugerida": "true" if aviso else "false",
            "aviso": "true" if aviso else "false",
            "motivo": "m" if aviso else "", "evidencia": "", "evidencia_en_texto": "",
            "ms": ms if valida else "", "tokens_prompt": "10", "tokens_salida": "2",
            "crudo": "{}", "consulta": consulta if valida else "slm_fallo",
            "tito_puntaje": "", "tito_error": "", "indicio_linea": "",
            "indicio_texto": "", "indicio_puntaje": "",
            "tito_ms": "", "slm_ms": ms if valida else "",
            "runtime_ns": runtime if valida and consulta != "omitida" else "",
            "runtime_unidad": "ns" if valida and consulta != "omitida" else ""}


def _manifiesto_modo(config, case_id, modo="operativo-hasta-aviso"):
    manifiesto = {"comando": "test", "inicio": "2026-10-27T00:00:00", "fin": "2026-10-27T00:01:00",
                  "interrumpida": False,
                  "codigo": {"commit": "abc", "cambios_sin_commit_en_la_carpeta": False},
                  "maquina": {"sistema": "x", "nucleos_logicos": 1, "ram_total_gb": 1.0},
                  "politica": "aviso_unico_hasta_aviso", "particion": "desarrollo",
                  "ollama": {"url": "u", "version": "0.0", "digests": {}},
                  "parametros_slm": {}, "prompts": {},
                  "configs": [{"config": config, "detector": "slm", "modelo": "m",
                               "prompt": "tarea", "hablantes": "ab"}],
                  "casos": {case_id: "x"}, "modelos": {}}
    if modo is not None:
        manifiesto["modo_termino"] = modo
    return manifiesto


class TestModoDeTermino(unittest.TestCase):
    CONFIG = "slm|m|tarea|ab"
    CASO = "SC-WA-CODE-01-e01"  # T_R L4

    def _analizar(self, modo, lineas_hasta, aviso_en=4):
        filas = [_fila_modo(self.CONFIG, self.CASO, n, aviso=(n == aviso_en))
                 for n in range(1, lineas_hasta + 1)]
        return resumen.analizar(_manifiesto_modo(self.CONFIG, self.CASO, modo), filas)

    def test_operativo_permite_fin_por_aviso_temprano(self):
        c = self._analizar("operativo-hasta-aviso", 4)[self.CONFIG][self.CASO]
        self.assertTrue(c["completo"])
        self.assertEqual(c["fin"], "aviso")
        self.assertEqual(c["aviso"], 4)

    def test_diagnostico_truncado_es_interrumpido_aunque_haya_aviso(self):
        c = self._analizar("diagnostico-completo", 4)[self.CONFIG][self.CASO]
        self.assertFalse(c["completo"])
        self.assertEqual(c["categoria"], "incompleto")
        self.assertEqual(c["fin"], "interrumpido")

    def test_diagnostico_completo_con_aviso_no_es_interrumpido(self):
        import casos
        total = len(casos.cargar_texto(self.CASO))
        c = self._analizar("diagnostico-completo", total)[self.CONFIG][self.CASO]
        self.assertTrue(c["completo"])
        self.assertEqual(c["fin"], "aviso")

    def test_historico_truncado_es_interrumpido_aunque_haya_aviso(self):
        c = self._analizar(None, 4)[self.CONFIG][self.CASO]
        self.assertEqual(c["categoria"], "incompleto")
        self.assertEqual(c["fin"], "interrumpido")

    def test_textos_por_modo_no_prometen_fin_operativo(self):
        filas_op = [_fila_modo(self.CONFIG, self.CASO, n, aviso=(n == 4)) for n in range(1, 5)]
        a_op = resumen.analizar(_manifiesto_modo(self.CONFIG, self.CASO, "operativo-hasta-aviso"), filas_op)
        a_diag = resumen.analizar(_manifiesto_modo(self.CONFIG, self.CASO, "diagnostico-completo"), filas_op)
        t_op = "\n".join(resumen.seccion_costos_hasta_aviso(
            _manifiesto_modo(self.CONFIG, self.CASO, "operativo-hasta-aviso"), a_op))
        t_diag = "\n".join(resumen.seccion_costos_hasta_aviso(
            _manifiesto_modo(self.CONFIG, self.CASO, "diagnostico-completo"), a_diag))
        t_hist = "\n".join(resumen.seccion_costos_hasta_aviso(
            _manifiesto_modo(self.CONFIG, self.CASO, None), a_diag))
        self.assertIn("hasta el aviso incluido", t_op)
        self.assertNotIn("termina en su primer aviso válido", t_diag)
        self.assertIn("por separado, la conversación completa", t_diag)
        for t in (t_hist,):
            self.assertIn("reconstrucción descriptiva del prefijo", t.lower())
            self.assertIn("no es una nueva medición operativa", t)
            self.assertIn("ni el costo completo", t)
            self.assertNotIn("cubren todas las líneas", t)
        # La sección del filtro tampoco promete fin operativo en otros modos.
        base = {"filtro_tito": {"tito": "guion-simulado", "umbral": 0.5}}
        f_op = "\n".join(resumen.seccion_filtro({**base, "modo_termino": "operativo-hasta-aviso"}, {}, {}))
        f_diag = "\n".join(resumen.seccion_filtro({**base, "modo_termino": "diagnostico-completo"}, {}, {}))
        f_hist = "\n".join(resumen.seccion_filtro(dict(base), {}, {}))
        self.assertIn("termina en su primer aviso válido", f_op)
        self.assertNotIn("termina en su primer aviso válido", f_diag)
        self.assertNotIn("termina en su primer aviso válido", f_hist)
        self.assertIn("reconstrucción descriptiva del prefijo", f_hist.lower())
        self.assertIn("no es una nueva medición operativa", f_hist)
        self.assertIn("ni el costo completo", f_hist)
        self.assertNotIn("cubren todas las líneas", f_hist)


class TestCostosMismoAlcance(unittest.TestCase):
    CONFIG = "slm|m|tarea|ab"
    CASO = "SC-WA-CODE-01-e01"

    def test_actualizaciones_cuentan_fallos_del_mismo_alcance(self):
        filas = [_fila_modo(self.CONFIG, self.CASO, 1),
                 _fila_modo(self.CONFIG, self.CASO, 2, valida=False),
                 _fila_modo(self.CONFIG, self.CASO, 3),
                 _fila_modo(self.CONFIG, self.CASO, 4, aviso=True)]
        manifiesto = _manifiesto_modo(self.CONFIG, self.CASO, "operativo-hasta-aviso")
        c = resumen.analizar(manifiesto, filas)[self.CONFIG][self.CASO]
        self.assertEqual(c["n_actualizaciones"], 4)
        self.assertEqual(c["n_fallos_hasta_aviso"], 1)
        texto = "\n".join(resumen.seccion_costos_hasta_aviso(manifiesto, {self.CONFIG: {self.CASO: c}}))
        self.assertIn("(1 fallo)", texto)

    def test_omitidas_no_cuentan_como_runtime_ausente(self):
        filas = [_fila_modo(self.CONFIG, self.CASO, 1, consulta="omitida", runtime=""),
                 _fila_modo(self.CONFIG, self.CASO, 2, consulta="omitida", runtime=""),
                 _fila_modo(self.CONFIG, self.CASO, 3, aviso=True)]
        manifiesto = _manifiesto_modo(self.CONFIG, self.CASO, "operativo-hasta-aviso")
        c = resumen.analizar(manifiesto, filas)[self.CONFIG][self.CASO]
        self.assertEqual(c["runtime_omitidas"], 2)
        self.assertEqual(c["runtime_ausente"], 0)
        self.assertEqual(c["runtime_con_dato"], 1)


class TestArranqueGlobalYComparar(unittest.TestCase):
    def _corrida_operativa(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                rc = correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--filtro-tito", "--tito-puntajes", "4=0.9",
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp.name,
                ])
                self.assertEqual(rc, 0)
                (carpeta,) = Path(tmp.name).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                filas = resumen.leer_corrida(carpeta)[1]
                analisis = resumen.analizar(manifiesto, filas)
                with redirect_stdout(io.StringIO()):
                    comparar.main([str(carpeta)])
                texto = (carpeta / "comparacion.md").read_text(encoding="utf-8")
            return manifiesto, filas, analisis, texto
        finally:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()

    def test_arranque_global_no_se_duplica_por_modelo(self):
        manifiesto, _, _, texto = self._corrida_operativa()
        self.assertIsNotNone(manifiesto["ollama"].get("arranque_ms"))
        for modelo, info in manifiesto["modelos"].items():
            self.assertNotIn("arranque_ms", info,
                             f"el arranque global no es arranque de {modelo}")
        self.assertIn("alcance global", texto)

    def test_comparar_usa_el_mismo_alcance_en_costos_y_conteos(self):
        manifiesto, filas, analisis, texto = self._corrida_operativa()
        detalle = resumen.analisis_filtro(manifiesto, filas, analisis)
        directa = "slm|modelo-falso:1b|tarea|ab"
        filtrada = "tito-slm|modelo-falso:1b|tarea|ab"
        for cid in ("SC-WA-CODE-01-e01", "LG-WA-CONSULTA-01-e01"):
            self.assertAlmostEqual(detalle[filtrada][cid]["ms_total"],
                                   detalle[filtrada][cid]["ms_hasta_aviso"])
            linea = next(l for l in texto.splitlines() if l.startswith(f"| `{cid}`"))
            self.assertIn(f"{analisis[directa][cid]['ms_hasta_aviso']:.0f}/"
                          f"{detalle[filtrada][cid]['ms_hasta_aviso']:.0f}", linea)
        self.assertIn("mismo alcance", texto)


if __name__ == "__main__":
    unittest.main()
