"""Tests unitarios para la integración de replay incremental (#28).

Verifica:
1. Parcial que reemplaza (no duplica segmentos abiertos).
2. Final que acumula (mantiene líneas cerradas en orden).
3. Sin texto futuro (el detector jamás ve líneas con disponible_s posterior).
4. Aviso único (solo el primer alerta_sugerida=true válido emite aviso).
5. Fallo no cuenta como predicción (respuestas inválidas no emiten aviso ni bloquean alertas futuras).
6. Separación de sesiones (reinicio completo de contexto y de cola secuencial entre distintas llamadas).
7. T_A incluye demora del detector y espera en cola (reloj de audio: fin_eval = inicio_eval + ms/1000).
8. Cola secuencial del detector: actualización 2 espera a que termine la 1 (max(disponible_s, fin_eval_prev)).
9. Modo texto sin segundos (columnas de tiempo vacías en eventos.csv y sin T_A inventado).
10. Integración completa de ejemplo JSONL con DetectorReglas y llamada_id FICTICIO-01.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

# Configurar rutas para importar desde experiments/replay y experiments/slm-directo
DIR_TESTS = Path(__file__).resolve().parent
DIR_REPLAY = DIR_TESTS.parent
DIR_SLM_DIRECTO = DIR_REPLAY.parent / "slm-directo"

for p in (DIR_REPLAY, DIR_SLM_DIRECTO):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import detectores
import replay
from contexto import Actualizacion, ContextoLlamada
from replay import (
    cargar_actualizaciones_jsonl,
    cargar_caso_texto,
    correr_replay,
    guardar_eventos_csv,
    guardar_manifiesto,
    guardar_resumen,
)


@dataclass
class FakeRespuesta:
    valida: bool
    alerta_sugerida: bool | None = None
    motivo: str = ""
    evidencia: str = ""
    error: str = ""
    riesgo: float | None = None
    ms: float | None = 10.0


class FakeDetector:
    """Detector falso para pruebas sin Ollama; registra cada consulta efectuada."""

    def __init__(self, respuestas: list[FakeRespuesta] | None = None, respuesta_defecto: FakeRespuesta | None = None):
        self.respuestas = list(respuestas) if respuestas else []
        self.respuesta_defecto = respuesta_defecto or FakeRespuesta(valida=True, alerta_sugerida=False)
        self.consultas: list[tuple[detectores.Linea, ...]] = []

    def evaluar(self, lineas: list[detectores.Linea] | tuple[detectores.Linea, ...]) -> FakeRespuesta:
        # Guardar copia de lo que el detector recibió en esta evaluación
        self.consultas.append(tuple(lineas))
        if self.respuestas:
            return self.respuestas.pop(0)
        return self.respuesta_defecto


class TestReplay(unittest.TestCase):

    def test_calentamiento_configura_pensar_false_en_consulta_slm(self):
        """El calentamiento compartido desactiva el razonamiento para la consulta real."""
        class ClienteOllamaFalso:
            def __init__(self, _url):
                self.pensar_enviado = []

            def chat(self, modelo, mensajes, formato, opciones, pensar=None):
                self.pensar_enviado.append(pensar)
                if "ok" in formato.get("properties", {}):
                    contenido = json.dumps({"ok": True})
                else:
                    contenido = json.dumps({
                        "riesgo": 0.1,
                        "alerta_sugerida": False,
                        "motivo": "",
                        "evidencia": "",
                    })
                return {"message": {"content": contenido}, "eval_count": 3}

            def memoria_cargada(self, _modelo):
                return {"size_bytes": 123}

        cliente = ClienteOllamaFalso("http://ollama-falso")
        original = replay.cliente_ollama.ClienteOllama
        replay.cliente_ollama.ClienteOllama = lambda _url: cliente
        try:
            detector = replay.construir_detector(
                "slm", modelo="modelo-falso:1b", hablantes="sin"
            )
            detector.evaluar((detectores.Linea(None, "hola"),))
        finally:
            replay.cliente_ollama.ClienteOllama = original

        self.assertEqual(cliente.pensar_enviado, [False, False])
        self.assertFalse(detector.pensar)
        self.assertEqual(detector.carga["pensar"], False)

    def test_parcial_reemplaza(self):
        """Un parcial posterior del mismo segmento reemplaza al anterior sin duplicar líneas."""
        actualizaciones = [
            Actualizacion("call_1", 1, "parcial", 0, "hola", 0.0, 1.0, 1.2, 200.0),
            Actualizacion("call_1", 2, "parcial", 0, "hola juan", 0.0, 1.8, 2.0, 200.0),
            Actualizacion("call_1", 3, "parcial", 0, "hola juan carlos", 0.0, 2.5, 2.7, 200.0),
        ]
        detector = FakeDetector()
        filas, contextos = correr_replay(actualizaciones, detector, disparo="parcial")

        self.assertEqual(len(detector.consultas), 3)
        # En la primera evaluación: 1 línea con "hola"
        self.assertEqual(len(detector.consultas[0]), 1)
        self.assertEqual(detector.consultas[0][0].texto, "hola")
        # En la segunda: sigue habiendo 1 línea, reemplazada por "hola juan"
        self.assertEqual(len(detector.consultas[1]), 1)
        self.assertEqual(detector.consultas[1][0].texto, "hola juan")
        # En la tercera: 1 sola línea reemplazada por "hola juan carlos"
        self.assertEqual(len(detector.consultas[2]), 1)
        self.assertEqual(detector.consultas[2][0].texto, "hola juan carlos")

    def test_final_acumula(self):
        """Los finales acumulan líneas fijas y cierran los borradores parciales."""
        actualizaciones = [
            Actualizacion("call_1", 1, "parcial", 0, "buen", 0.0, 0.8, 1.0, 200.0),
            Actualizacion("call_1", 2, "final", 0, "buenos días", 0.0, 1.5, 1.7, 200.0),
            Actualizacion("call_1", 3, "parcial", 1, "como", 1.8, 2.2, 2.4, 200.0),
            Actualizacion("call_1", 4, "final", 1, "cómo le va", 1.8, 2.8, 3.0, 200.0),
            Actualizacion("call_1", 5, "final", 2, "le hablo del banco", 3.0, 4.5, 4.8, 300.0),
        ]
        detector = FakeDetector()
        # Con disparo="final", solo evalúa en los segmentos finales (3 veces)
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        self.assertEqual(len(detector.consultas), 3)
        # Primera evaluación (final seg 0): 1 línea
        self.assertEqual([l.texto for l in detector.consultas[0]], ["buenos días"])
        # Segunda evaluación (final seg 1): 2 líneas
        self.assertEqual([l.texto for l in detector.consultas[1]], ["buenos días", "cómo le va"])
        # Tercera evaluación (final seg 2): 3 líneas acumuladas
        self.assertEqual(
            [l.texto for l in detector.consultas[2]],
            ["buenos días", "cómo le va", "le hablo del banco"],
        )

    def test_sin_texto_futuro(self):
        """El detector jamás ve líneas correspondientes a actualizaciones con disponible_s posterior."""
        actualizaciones = [
            Actualizacion("call_1", 1, "final", 0, "frase_uno", 0.0, 1.0, 1.2),
            Actualizacion("call_1", 2, "final", 1, "frase_dos", 1.2, 2.0, 2.2),
            Actualizacion("call_1", 3, "final", 2, "frase_tres", 2.2, 3.0, 3.2),
            Actualizacion("call_1", 4, "final", 3, "frase_cuatro", 3.2, 4.0, 4.2),
        ]
        detector = FakeDetector()
        correr_replay(actualizaciones, detector, disparo="final")

        self.assertEqual(len(detector.consultas), 4)
        for idx, consulta in enumerate(detector.consultas, start=1):
            textos_en_consulta = [l.texto for l in consulta]
            # Solo deben estar las frases hasta idx
            frases_permitidas = [f"frase_{num}" for num in ["uno", "dos", "tres", "cuatro"][:idx]]
            self.assertEqual(textos_en_consulta, frases_permitidas)
            # Frases futuras no deben aparecer
            frases_futuras = [f"frase_{num}" for num in ["uno", "dos", "tres", "cuatro"][idx:]]
            for f_futura in frases_futuras:
                self.assertNotIn(f_futura, textos_en_consulta)

    def test_aviso_unico(self):
        """Solo la primera respuesta válida con alerta_sugerida=True produce aviso; posteriores no repiten."""
        actualizaciones = [
            Actualizacion("call_1", 1, "final", 0, "hola", 0.0, 1.0, 1.2),
            Actualizacion("call_1", 2, "final", 1, "pasame el codigo", 1.2, 2.5, 2.8),
            Actualizacion("call_1", 3, "final", 2, "dale rapido el token", 2.8, 4.0, 4.3),
            Actualizacion("call_1", 4, "final", 3, "por que no me lo das", 4.3, 5.5, 5.8),
        ]
        respuestas = [
            FakeRespuesta(valida=True, alerta_sugerida=False),
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_1", evidencia="codigo"),
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_2", evidencia="token"),
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_3", evidencia="urgencia"),
        ]
        detector = FakeDetector(respuestas=respuestas)
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        avisos = [f["aviso"] for f in filas]
        self.assertEqual(avisos, ["false", "true", "false", "false"])
        # Exactamente un aviso emitido
        self.assertEqual(sum(1 for a in avisos if a == "true"), 1)
        self.assertTrue(contextos[0].aviso_emitido)
        self.assertEqual(contextos[0].aviso_n, 2)

    def test_aviso_unico_con_reglas_reales(self):
        """Verifica la política de aviso único con el DetectorReglas real."""
        actualizaciones = [
            Actualizacion("call_1", 1, "final", 0, "hola buenas tardes", 0.0, 1.0, 1.2),
            Actualizacion("call_1", 2, "final", 1, "pasame el codigo de verificacion", 1.2, 3.0, 3.3),
            Actualizacion("call_1", 3, "final", 2, "y decime el token que te llego", 3.3, 5.0, 5.3),
        ]
        detector = detectores.DetectorReglas()
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        avisos = [f["aviso"] for f in filas]
        self.assertEqual(avisos, ["false", "true", "false"])
        self.assertTrue(contextos[0].aviso_emitido)
        self.assertEqual(contextos[0].aviso_n, 2)
        self.assertIn("REQUEST_AUTH_CODE", contextos[0].aviso_respuesta.motivo)

    def test_fallo_no_cuenta_como_prediccion(self):
        """Un fallo (respuesta inválida o timeout) no cuenta como predicción ni bloquea alertas futuras."""
        actualizaciones = [
            Actualizacion("call_1", 1, "final", 0, "hola", 0.0, 1.0, 1.2),
            Actualizacion("call_1", 2, "final", 1, "segmento_con_error", 1.2, 2.0, 2.3),
            Actualizacion("call_1", 3, "final", 2, "pasame el token", 2.3, 3.5, 3.8),
        ]
        respuestas = [
            FakeRespuesta(valida=True, alerta_sugerida=False),
            FakeRespuesta(valida=False, error="json_invalido", ms=15.0),  # Fallo
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_valida", ms=20.0),
        ]
        detector = FakeDetector(respuestas=respuestas)
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        # Fila 2 falló: valida=false, aviso=false
        self.assertEqual(filas[1]["valida"], "false")
        self.assertEqual(filas[1]["error"], "json_invalido")
        self.assertEqual(filas[1]["aviso"], "false")

        # Fila 3 tuvo respuesta válida y disparó el aviso correctamente
        self.assertEqual(filas[2]["valida"], "true")
        self.assertEqual(filas[2]["aviso"], "true")
        self.assertEqual(contextos[0].fallos, 1)
        self.assertEqual(contextos[0].aviso_n, 3)

    def test_separacion_sesiones_y_reinicio_de_cola(self):
        """Al cambiar de llamada_id se reinicia el contexto y la cola secuencial del detector."""
        actualizaciones = [
            # Llamada 1: termina en fin_eval = 2.5
            Actualizacion("call_A", 1, "final", 0, "llamada 1 linea 1", 0.0, 1.0, 1.0),
            Actualizacion("call_A", 2, "final", 1, "llamada 1 alerta", 1.0, 1.5, 1.5),
            # Llamada 2: empieza en disponible_s = 0.5 (no debe heredar fin_eval=2.5 de call_A)
            Actualizacion("call_B", 1, "final", 0, "llamada 2 linea 1", 0.0, 0.4, 0.5),
            Actualizacion("call_B", 2, "final", 1, "llamada 2 alerta", 0.5, 1.0, 1.2),
        ]
        respuestas = [
            FakeRespuesta(valida=True, alerta_sugerida=False, ms=1000.0),  # eval_1: 1.0 a 2.0
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_A", ms=500.0),  # eval_2: 2.0 a 2.5
            FakeRespuesta(valida=True, alerta_sugerida=False, ms=200.0),  # call_B eval_1: 0.5 a 0.7
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_B", ms=300.0),  # call_B eval_2: 1.2 a 1.5
        ]
        detector = FakeDetector(respuestas=respuestas)
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        self.assertEqual(len(contextos), 2)
        self.assertEqual(contextos[0].llamada_id, "call_A")
        self.assertEqual(contextos[1].llamada_id, "call_B")

        # La llamada 2 no ve las líneas de la llamada 1
        consulta_call_b_1 = [l.texto for l in detector.consultas[2]]
        self.assertEqual(consulta_call_b_1, ["llamada 2 linea 1"])
        self.assertNotIn("llamada 1 linea 1", consulta_call_b_1)

        # La llamada 2 inició su evaluación en 0.5, no arrastró el fin_eval=2.5 de call_A
        self.assertEqual(filas[2]["inicio_eval_s"], "0.500")
        self.assertEqual(filas[2]["fin_eval_s"], "0.700")
        self.assertEqual(filas[2]["espera_cola_ms"], "0.0")

        # Ambas llamadas emitieron su aviso de forma independiente
        self.assertTrue(contextos[0].aviso_emitido)
        self.assertEqual(contextos[0].aviso_n, 2)
        self.assertTrue(contextos[1].aviso_emitido)
        self.assertEqual(contextos[1].aviso_n, 2)

    def test_cola_secuencial_detector_y_t_a(self):
        """El detector es un recurso secuencial: actualización 2 espera a la 1 y T_A = fin_eval."""
        actualizaciones = [
            Actualizacion("call_1", 1, "final", 0, "primer mensaje", 0.0, 0.9, 1.0),
            Actualizacion("call_1", 2, "final", 1, "segundo mensaje con alerta", 0.9, 1.1, 1.1),
        ]
        respuestas = [
            FakeRespuesta(valida=True, alerta_sugerida=False, ms=500.0),
            FakeRespuesta(valida=True, alerta_sugerida=True, motivo="alerta_cola", ms=500.0),
        ]
        detector = FakeDetector(respuestas=respuestas)
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        # Fila 1: disponible_s=1.0, inicio_eval=1.0, fin_eval=1.5, espera=0.0
        self.assertEqual(filas[0]["disponible_s"], "1.000")
        self.assertEqual(filas[0]["inicio_eval_s"], "1.000")
        self.assertEqual(filas[0]["fin_eval_s"], "1.500")
        self.assertEqual(filas[0]["espera_cola_ms"], "0.0")

        # Fila 2: disponible_s=1.1, inicio_eval=1.5 (esperó fin de 1), fin_eval=2.0, espera=400.0
        self.assertEqual(filas[1]["disponible_s"], "1.100")
        self.assertEqual(filas[1]["inicio_eval_s"], "1.500")
        self.assertEqual(filas[1]["fin_eval_s"], "2.000")
        self.assertEqual(filas[1]["espera_cola_ms"], "400.0")

        # T_A de la alerta emitida en fila 2 es exactamente fin_eval = 2.0
        self.assertEqual(filas[1]["aviso"], "true")
        self.assertEqual(filas[1]["t_a"], "2.0000")
        self.assertAlmostEqual(contextos[0].aviso_t_a, 2.0, places=4)
        self.assertAlmostEqual(contextos[0].max_espera_cola_ms, 400.0, places=2)
        self.assertTrue(contextos[0].hubo_atraso)

    def test_t_a_incluye_demora_detector(self):
        """T_A en segundos del reloj de audio incluye disponible_s + (ms_detector / 1000)."""
        disponible_s = 14.350
        ms_detector = 250.0  # 0.25 s
        actualizaciones = [
            Actualizacion("call_1", 1, "final", 0, "pasame la clave", 12.0, 14.1, disponible_s),
        ]
        detector = FakeDetector(
            respuestas=[FakeRespuesta(valida=True, alerta_sugerida=True, motivo="clave", ms=ms_detector)]
        )
        filas, contextos = correr_replay(actualizaciones, detector, disparo="final")

        t_a_esperado = 14.350 + (250.0 / 1000.0)  # 14.6000
        self.assertAlmostEqual(contextos[0].aviso_t_a, t_a_esperado, places=4)
        self.assertEqual(filas[0]["aviso"], "true")
        self.assertEqual(filas[0]["t_a"], f"{t_a_esperado:.4f}")
        self.assertEqual(filas[0]["inicio_eval_s"], f"{disponible_s:.3f}")
        self.assertEqual(filas[0]["fin_eval_s"], f"{t_a_esperado:.3f}")
        self.assertEqual(filas[0]["espera_cola_ms"], "0.0")

    def test_modo_texto_sin_segundos(self):
        """El modo texto procesa líneas de slm-directo sin segundos (columnas de tiempo vacías)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_dir_path = Path(tmpdir)
            caso_txt = tmp_dir_path / "caso_prueba.txt"
            caso_txt.write_text(
                "A: hola soy del soporte tecnico\n"
                "B: que paso\n"
                "A: pasame el codigo de verificacion\n"
                "B: ahi te lo paso\n",
                encoding="utf-8",
            )

            actualizaciones = cargar_caso_texto(caso_txt)
            detector = detectores.DetectorReglas()

            salida = tmp_dir_path / "salida"
            filas, contextos = correr_replay(actualizaciones, detector, salida_dir=salida)

            guardar_resumen(
                salida / "resumen.md",
                caso_txt,
                "texto",
                "reglas",
                None,
                None,
                "sin",
                "final",
                contextos,
                filas,
            )

            # Verificar que en eventos.csv las columnas de tiempo estén vacías
            with open(salida / "eventos.csv", "r", encoding="utf-8") as f:
                lector = list(csv.DictReader(f))
                self.assertEqual(len(lector), 4)
                for fila in lector:
                    self.assertEqual(fila["inicio_audio_s"], "")
                    self.assertEqual(fila["fin_audio_s"], "")
                    self.assertEqual(fila["disponible_s"], "")
                    self.assertEqual(fila["inicio_eval_s"], "")
                    self.assertEqual(fila["fin_eval_s"], "")
                    self.assertEqual(fila["espera_cola_ms"], "")
                    self.assertEqual(fila["t_a"], "")
                    self.assertTrue(fila["n"].isdigit())
                    self.assertTrue(fila["segmento"].isdigit())

                # La línea 3 dispara la regla
                self.assertEqual(lector[2]["aviso"], "true")
                self.assertEqual(lector[3]["aviso"], "false")

            # Verificar que resumen.md indique modo texto sin segundos
            contenido_resumen = (salida / "resumen.md").read_text(encoding="utf-8")
            self.assertIn("Modo texto (sin audio)", contenido_resumen)
            self.assertIn("No aplica (modo texto sin audio", contenido_resumen)
            self.assertIn("Espera de cola máxima:** No aplica", contenido_resumen)

    def test_integracion_jsonl_ejemplo_con_reglas(self):
        """Prueba end-to-end con el JSONL de ejemplo (FICTICIO-01) y DetectorReglas."""
        ruta_ejemplo = DIR_TESTS / "datos" / "ejemplo_actualizaciones.jsonl"
        self.assertTrue(ruta_ejemplo.exists())

        with tempfile.TemporaryDirectory() as tmpdir:
            salida = Path(tmpdir) / "corrida_humo"
            cmd = [
                sys.executable,
                str(DIR_REPLAY / "replay.py"),
                "--actualizaciones",
                str(ruta_ejemplo),
                "--detector",
                "reglas",
                "--salida",
                str(salida),
            ]
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, f"Error en replay.py: {res.stderr}")

            # Archivos obligatorios
            self.assertTrue((salida / "eventos.csv").exists())
            self.assertTrue((salida / "manifiesto.json").exists())
            self.assertTrue((salida / "resumen.md").exists())

            # Validar manifiesto
            manifiesto = json.loads((salida / "manifiesto.json").read_text(encoding="utf-8"))
            self.assertEqual(manifiesto["config"]["detector"], "reglas")
            self.assertEqual(manifiesto["config"]["seed"], "no-aplica")
            self.assertEqual(manifiesto["config"]["politica"], "aviso_unico_primer_true_valido")
            self.assertIn("sha256", manifiesto["entradas"])
            self.assertIn("commit", manifiesto["codigo"])
            self.assertIn("sistema", manifiesto["hardware"])

            # Validar eventos.csv
            with open(salida / "eventos.csv", "r", encoding="utf-8") as f:
                filas = list(csv.DictReader(f))
                self.assertEqual(len(filas), 8)
                # Verifica que llamada_id sea FICTICIO-01
                for f_item in filas:
                    self.assertEqual(f_item["llamada_id"], "FICTICIO-01")

                # Fila 7 dispara el aviso (n=7, final, "pasame el codigo de verificacion que te llego")
                self.assertEqual(filas[6]["n"], "7")
                self.assertEqual(filas[6]["aviso"], "true")
                self.assertTrue(len(filas[6]["t_a"]) > 0)
                self.assertTrue(len(filas[6]["inicio_eval_s"]) > 0)
                self.assertTrue(len(filas[6]["fin_eval_s"]) > 0)
                self.assertTrue(len(filas[6]["espera_cola_ms"]) > 0)
                # Fila 8 posterior no debe avisar
                self.assertEqual(filas[7]["n"], "8")
                self.assertEqual(filas[7]["aviso"], "false")


if __name__ == "__main__":
    unittest.main()
