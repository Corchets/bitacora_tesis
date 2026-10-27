"""Recorrido Tito→SLM con modelos simulados (#69, parte de #68).

Usa dobles deterministas (TitoGuion + SLM guionado de ms fijo) y, de punta a
punta, el Ollama falso de `test_ensayo` con `correr`/`resumen` reales. No
descarga ni entrena modelos.
"""

from __future__ import annotations

import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import casos  # noqa: E402
import correr  # noqa: E402
import resumen  # noqa: E402
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


class SLMGuion:
    """SLM simulado: responde lo indicado por línea, con costo fijo y trazable."""

    def __init__(self, alertas=frozenset(), invalidas=frozenset(), ms_fijo=7.0, hablantes="ab"):
        self.alertas, self.invalidas = set(alertas), set(invalidas)
        self.ms_fijo = ms_fijo
        self.hablantes = hablantes
        self.recibido: list[tuple[str, tuple]] = []

    def evaluar_mensaje(self, usuario, lineas):
        self.recibido.append((usuario, tuple(lineas)))
        n = len(lineas)
        if n in self.invalidas:
            return Respuesta(valida=False, error="json_invalido", ms=self.ms_fijo)
        alerta = n in self.alertas
        return Respuesta(
            valida=True,
            riesgo=0.9 if alerta else 0.1,
            alerta_sugerida=alerta,
            motivo="m" if alerta else "",
            ms=self.ms_fijo,
        )


def flujo(puntajes=None, fallos=None, alertas=frozenset(), invalidas=frozenset(), umbral=UMBRAL_TITO):
    return FlujoTitoSLM(TitoGuion(puntajes, fallos), SLMGuion(alertas, invalidas), umbral)


class TestUmbralYOmitidas(unittest.TestCase):
    def test_bajo_el_umbral_no_consulta_al_slm(self):
        f = flujo(puntajes={1: 0.1, 2: 0.4}, alertas={1, 2, 3, 4, 5})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual([r.consulta for _, _, r, _ in salidas], ["omitida"] * 5)
        self.assertEqual(f.slm.recibido, [])
        self.assertEqual([n for n, _ in f.tito.consultas], [1, 2, 3, 4, 5])
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)

    def test_igualdad_al_umbral_activa_en_esa_misma_linea(self):
        f = flujo(puntajes={2: 0.5}, alertas={2})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["omitida", "slm_valida", "slm_valida", "slm_valida", "slm_valida"],
        )
        self.assertEqual([aviso for *_, aviso in salidas], [False, True, False, False, False])

    def test_la_activacion_persiste_aunque_el_puntaje_caiga(self):
        f = flujo(puntajes={1: 0.9}, alertas={3})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual(f.tito.consultas, [(1, DIALOGO[0].texto)], "Tito deja de decidir tras activar")
        self.assertEqual(len(f.slm.recibido), 5)
        self.assertEqual([aviso for *_, aviso in salidas], [False, False, True, False, False])

    def test_omitir_no_simula_legitimidad_ni_fallo(self):
        f = flujo()
        (r,) = [r for _, _, r, _ in correr.procesar_caso(f, DIALOGO[:1])]
        self.assertTrue(r.valida)
        self.assertFalse(r.alerta_sugerida)
        self.assertEqual(r.consulta, "omitida")
        self.assertEqual(r.error, "")


class TestHistorialEIndicio(unittest.TestCase):
    def test_cada_consulta_lleva_todo_lo_disponible_incluida_la_disparadora(self):
        f = flujo(puntajes={2: 0.8})
        list(correr.procesar_caso(f, DIALOGO))
        tamanos = [len(lineas) for _, lineas in f.slm.recibido]
        self.assertEqual(tamanos, [2, 3, 4, 5])
        for usuario, lineas in f.slm.recibido:
            self.assertIn("Me acaba de llegar un SMS", usuario, "falta la línea disparadora")
        primero = f.slm.recibido[0][0]
        self.assertNotIn("cero, cero", primero, "la primera consulta vio futuro")

    def test_el_indicio_es_falible_y_se_conserva_el_inicial(self):
        f = flujo(puntajes={2: 0.6, 4: 0.9}, alertas={4})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        for _, _, r, _ in salidas[1:]:
            self.assertEqual((r.indicio_linea, r.indicio_puntaje), (2, 0.6))
        usuario = f.slm.recibido[0][0]
        self.assertIn("Me acaba de llegar un SMS. No pedí activar nada.", usuario)
        self.assertIn("línea 2", usuario)
        self.assertIn("0.60", usuario)
        self.assertIn("puede ser incorrecta", usuario)
        self.assertIn("podés descartarlo", usuario)


class TestFallos(unittest.TestCase):
    def test_fallo_de_tito_activa_sin_fabricar_sospecha(self):
        f = flujo(fallos={1}, alertas={1})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        primera = salidas[0][2]
        self.assertEqual(primera.consulta, "slm_valida")
        self.assertEqual(primera.tito_error, "tito_caido")
        self.assertIsNone(primera.tito_puntaje)
        self.assertIsNone(primera.indicio_linea)
        self.assertIn("falló técnicamente (tito_caido)", f.slm.recibido[0][0])
        self.assertNotIn("puntaje", f.slm.recibido[0][0].split("falló técnicamente")[1].split(".")[0])

    def test_fallo_del_slm_no_avisa_y_queda_como_fallo(self):
        f = flujo(puntajes={2: 0.9}, invalidas={2, 3, 4, 5})
        salidas = list(correr.procesar_caso(f, DIALOGO))
        self.assertEqual(
            [r.consulta for _, _, r, _ in salidas],
            ["omitida", "slm_fallo", "slm_fallo", "slm_fallo", "slm_fallo"],
        )
        self.assertEqual([aviso for *_, aviso in salidas], [False] * 5)
        self.assertTrue(all(not r.valida for _, _, r, _ in salidas[1:]))

    def test_contexto_excedido_del_slm_queda_como_fallo_explicito(self):
        slm = DetectorSLM(ClienteOllama("http://127.0.0.1:9", timeout_s=2), "m", cargar_prompt("tarea"), num_ctx=64)
        f = FlujoTitoSLM(TitoGuion({1: 0.9}), slm)
        salidas = list(correr.procesar_caso(f, DIALOGO[:2]))
        r = salidas[0][2]
        self.assertEqual(r.consulta, "slm_fallo")
        self.assertTrue(r.error.startswith("contexto_excedido"))


class TestAvisoUnicoYReinicio(unittest.TestCase):
    def test_un_solo_aviso_en_el_primer_true_valido(self):
        f = flujo(puntajes={1: 0.7}, alertas={2, 4})
        avisos = [aviso for *_, aviso in correr.procesar_caso(f, DIALOGO)]
        self.assertEqual(avisos, [False, True, False, False, False])

    def test_contexto_activacion_e_indicio_se_reinician_entre_llamadas(self):
        f = flujo(puntajes={1: 0.9}, alertas={1})
        primera = list(correr.procesar_caso(f, DIALOGO))
        segunda = list(correr.procesar_caso(f, LEGITIMA))
        self.assertEqual([aviso for *_, aviso in primera].count(True), 1)
        self.assertEqual([aviso for *_, aviso in segunda].count(True), 1, "el aviso anterior bloqueó la otra llamada")
        self.assertEqual(segunda[0][2].consulta, "slm_valida", "la segunda llamada no arrancó activada")
        self.assertEqual(segunda[0][2].indicio_linea, 1)
        # La segunda llamada activó por su propia línea 1, no por la anterior.
        self.assertIn(LEGITIMA[0].texto, f.slm.recibido[len(primera)][0])


class TestCostoDeterminista(unittest.TestCase):
    def test_el_total_suma_tito_mas_slm_y_omite_sin_costo_slm(self):
        f = flujo(puntajes={2: 0.9})
        f.slm.ms_fijo = 7.0
        salidas = list(correr.procesar_caso(f, DIALOGO))
        total = sum(r.ms for _, _, r, _ in salidas)
        # L1 omitida: 5,0 solo Tito; L2: 5,0 + 7,0; L3–L5: 7,0 (Tito ya no decide).
        self.assertAlmostEqual(total, 5.0 + 12.0 + 7.0 * 3)
        self.assertEqual(salidas[0][2].tokens_prompt, None)
        self.assertIsNone(salidas[0][2].tokens_salida)


class TestPuntaAPuntaConOllamaFalso(unittest.TestCase):
    def _correr(self, tito_puntajes: str, tito_fallo_en: str = ""):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        tmp = tempfile.TemporaryDirectory()
        try:
            with redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--filtro-tito", "--tito-puntajes", tito_puntajes,
                    "--tito-fallo-en", tito_fallo_en,
                    "--url", f"http://127.0.0.1:{servidor.server_port}",
                    "--salida", tmp.name,
                ])
                (carpeta,) = Path(tmp.name).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                analisis = resumen.analizar(manifiesto, resumen.leer_corrida(carpeta)[1])
                texto = resumen.armar_resumen(carpeta)
            return manifiesto, analisis, texto
        finally:
            servidor.shutdown()
            servidor.server_close()
            tmp.cleanup()

    def test_sin_derivacion_ambos_conservan_denominador(self):
        manifiesto, analisis, texto = self._correr("")
        filtrada = "tito-slm|modelo-falso:1b|tarea|ab"
        self.assertIn(filtrada, analisis)
        self.assertIn("slm|modelo-falso:1b|tarea|ab", analisis, "el comparador directo sigue corriendo")
        cs = analisis[filtrada]
        # Vishing nunca derivado: falso negativo visible, no corrida incompleta.
        self.assertEqual(cs["SC-WA-CODE-01-e01"]["categoria"], "sin_aviso")
        self.assertIsNone(cs["SC-WA-CODE-01-e01"]["aviso"])
        # Legítima nunca derivada: verdadero negativo.
        self.assertEqual(cs["LG-WA-CONSULTA-01-e01"]["categoria"], "sin_aviso_correcto")
        m = resumen.metricas(cs)
        self.assertEqual(m["sin_evaluar"], 0)
        self.assertEqual((m["vishing"], m["legitimas"]), (1, 1))
        self.assertEqual(manifiesto["filtro_tito"]["umbral"], 0.5)
        self.assertIn("## Filtro Tito→SLM", texto)
        self.assertIn("Nunca derivados", texto)
        self.assertIn("Consultas al SLM: 0; evitadas por el filtro: 9", texto)

    def test_fallo_tecnico_de_tito_deriva_y_se_informa(self):
        # Tito caído en L1/L2: deriva por fallo, sin puntaje ni sospecha, y el
        # resumen lo distingue de una decisión del filtro.
        manifiesto, analisis, texto = self._correr("", "1,2")
        filtrada = "tito-slm|modelo-falso:1b|tarea|ab"
        self.assertIn(filtrada, analisis)
        self.assertIn("Fallos técnicos de Tito:", texto)
        # El SLM igual fue consultado (activación por fallo), no omitido.
        self.assertIn("Consultas al SLM: 9; evitadas por el filtro: 0", texto)

    def test_con_derivacion_hay_primera_derivacion_primer_aviso_y_costo(self):
        _, analisis, texto = self._correr("4=0.9")
        cs = analisis["tito-slm|modelo-falso:1b|tarea|ab"]
        # Vishing: deriva en L4 (igualdad/inclusión) y avisa ahí mismo.
        self.assertEqual(cs["SC-WA-CODE-01-e01"]["aviso"], 4)
        self.assertIn("1.ª derivación", texto)
        self.assertIn("`SC-WA-CODE-01-e01` | 4 | L4 | 2 | 3 | 0 |", texto)
        # Legítima: deriva en L4 por el número de línea, pero el SLM no avisa.
        self.assertEqual(cs["LG-WA-CONSULTA-01-e01"]["categoria"], "sin_aviso_correcto")


if __name__ == "__main__":
    unittest.main()
