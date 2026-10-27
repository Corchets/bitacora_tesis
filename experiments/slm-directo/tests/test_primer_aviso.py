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
from casos import Linea  # noqa: E402
from detectores import Respuesta  # noqa: E402
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


if __name__ == "__main__":
    unittest.main()
