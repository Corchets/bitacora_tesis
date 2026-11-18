"""Configuración congelada de #143: C de la etapa 2 cortado tras el riesgo (`c-json-corte-riesgo`), «riesgo ≥ 0,3», el
motivo de C en el primer aviso y el modo «solo OTRA» de correr.py (ADR 0007). También la regla de lectura de la humo,
corridas/2026-11-10_config-congelada-humo/analizar.py. Sin modelo: contra el Ollama falso de test_ensayo.py y sobre
corridas sintéticas.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_config_congelada_143 -v
"""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stderr, redirect_stdout
from http.server import HTTPServer
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import casos  # noqa: E402
import correr  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (  # noqa: E402
    ESQUEMA_MOTIVO,
    ESQUEMA_SALIDA,
    MAXIMO_TOKENS_CORTE_RIESGO,
    MAXIMO_TOKENS_RESPUESTA,
    PROMPT_MOTIVO_C,
    PROMPTS_CORTE_RIESGO,
    DetectorSLM,
    DetectorSLMCorteRiesgo,
    cargar_prompt,
    cargar_prompt_motivo,
    esquema_de,
    huella,
    leer_riesgo_cortado,
)
from test_ensayo import OllamaFalso  # noqa: E402

VARIANTE = "c-json-corte-riesgo"
# Palabra en la transcripción → riesgo que escribe el modelo falso (gana la última de la lista que aparezca).
SALIDAS = [("soporte", "0.3"), ("DOS_DECIMALES", "0.05"), ("Decime el código", "0.9"), ("FUERA", "1.5")]


def cortado(riesgo: str) -> str:
    """El JSON de C como lo escribe Gemma 4 en T4, cortado justo después de la coma del riesgo."""
    return f'{{\n  "riesgo": {riesgo},'


class OllamaCongelada(OllamaFalso):
    """El Ollama falso de test_ensayo.py, con lo que usa la configuración congelada.

    - Primera consulta (ESQUEMA_SALIDA): el JSON de C cortado tras la coma del riesgo, con done_reason "length". Con
      «SIN_COMA» en la transcripción, el corte llega antes de la coma.
    - Segunda consulta (ESQUEMA_MOTIVO): evidencia y motivo, o un texto roto con `motivo_roto`.
    - `/api/version` y `/api/tags` dicen lo que se les configure.
    """

    pedidos: list[dict] = []
    motivo_roto = False
    version = "0.0-falso"
    modelo = "modelo-falso:1b"
    digest = "abc123"

    def do_GET(self):
        respuestas = {
            "/api/version": {"version": OllamaCongelada.version},
            "/api/tags": {"models": [{"name": OllamaCongelada.modelo, "digest": OllamaCongelada.digest}]},
            "/api/ps": {"models": [{"name": OllamaCongelada.modelo, "size": 600 * 1024**2, "size_vram": 0}]},
        }
        self._responder(respuestas.get(self.path, {}), 200 if self.path in respuestas else 404)

    def do_POST(self):
        pedido = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if self.path != "/api/chat":
            self._responder({}, 404)
            return
        formato = pedido.get("format") or {}
        if "ok" in formato.get("properties", {}):  # calentamiento de correr.py
            self._responder({"message": {"content": json.dumps({"ok": True})}, "eval_count": 3})
            return
        OllamaCongelada.pedidos.append(pedido)
        if formato == ESQUEMA_MOTIVO:
            contenido = "roto" if OllamaCongelada.motivo_roto else json.dumps(
                {"evidencia": "Te llamo de soporte", "motivo": "Dice ser de soporte sin que lo hayas pedido"},
                ensure_ascii=False)
            self._responder({"message": {"content": contenido}, "done_reason": "stop", "prompt_eval_count": 40,
                             "eval_count": 30, "total_duration": 800_000_000})
            return
        transcripcion = pedido["messages"][1]["content"]
        riesgo = "0.1"
        for palabra, valor in SALIDAS:
            if palabra in transcripcion:
                riesgo = valor
        contenido = '{\n  "riesgo": 0.0' if "SIN_COMA" in transcripcion else cortado(riesgo)
        self._responder({"message": {"content": contenido}, "done_reason": "length", "prompt_eval_count": 300,
                         "eval_count": pedido["options"]["num_predict"], "total_duration": 240_000_000})


class _ConServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaCongelada)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"
        cls.cliente = ClienteOllama(cls.url, timeout_s=5)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        OllamaCongelada.pedidos.clear()
        OllamaCongelada.motivo_roto = False

    def detector(self) -> DetectorSLMCorteRiesgo:
        return DetectorSLMCorteRiesgo(self.cliente, "modelo-falso:1b", cargar_prompt(VARIANTE), "rol",
                                      esquema=esquema_de(VARIANTE))

    def motivos(self) -> list[dict]:
        return [p for p in OllamaCongelada.pedidos if p["format"] == ESQUEMA_MOTIVO]


def roles(*pares: tuple[str, str]) -> tuple[Linea, ...]:
    return tuple(Linea("OTRA" if quien == "O" else "PROTEGIDA", texto) for quien, texto in pares)


class TestConfiguracion(unittest.TestCase):
    def test_es_c_de_la_etapa_2_con_su_prompt_y_su_esquema(self):
        self.assertIn(VARIANTE, PROMPTS_CORTE_RIESGO)
        self.assertEqual(cargar_prompt(VARIANTE), cargar_prompt("c-json"))
        self.assertEqual(cargar_prompt(VARIANTE), cargar_prompt("c-json-corte"))
        self.assertEqual(esquema_de(VARIANTE), ESQUEMA_SALIDA)
        self.assertEqual(list(ESQUEMA_SALIDA["properties"])[0], "riesgo", "el riesgo es el primer campo")

    def test_el_corte_alcanza_un_riesgo_con_dos_decimales_y_su_coma(self):
        # 12 tokens hasta la coma con un decimal (etapa 1), uno más con dos decimales y uno de margen.
        self.assertEqual(MAXIMO_TOKENS_CORTE_RIESGO, 14)


class TestLeerRiesgoCortado(unittest.TestCase):
    def test_lee_el_riesgo_seguido_de_su_coma(self):
        crudo = cortado("0.3")
        riesgo, fin, error = leer_riesgo_cortado(crudo)
        self.assertEqual((riesgo, error), (0.3, ""))
        self.assertEqual(crudo[:fin], '{\n  "riesgo": 0.3', "el fin es el del número, sin la coma")

    def test_dos_decimales_compacto_y_entero(self):
        self.assertEqual(leer_riesgo_cortado(cortado("0.05"))[::2], (0.05, ""))
        self.assertEqual(leer_riesgo_cortado('{"riesgo": 0.2,')[::2], (0.2, ""))
        self.assertEqual(leer_riesgo_cortado(cortado("0"))[::2], (0.0, ""))
        self.assertEqual(leer_riesgo_cortado(cortado("1"))[::2], (1.0, ""))

    def test_sin_la_coma_el_numero_puede_estar_a_medias(self):
        self.assertEqual(leer_riesgo_cortado('{\n  "riesgo": 0.0'), (None, None, "sin_riesgo"))
        self.assertEqual(leer_riesgo_cortado('{\n  "ries'), (None, None, "sin_riesgo"))
        self.assertEqual(leer_riesgo_cortado(""), (None, None, "sin_riesgo"))

    def test_fuera_de_rango(self):
        self.assertEqual(leer_riesgo_cortado(cortado("1.5")), (1.5, None, "riesgo_fuera_de_rango"))
        self.assertEqual(leer_riesgo_cortado(cortado("-0.1"))[2], "riesgo_fuera_de_rango")


class TestDetector(_ConServidor):
    def test_mismo_pedido_que_c_json_corte_salvo_el_corte(self):
        lineas = roles(("O", "Hola, ¿qué tal?"), ("P", "Bien"))
        self.detector().evaluar(lineas)
        (pedido,) = OllamaCongelada.pedidos
        mensajes, _ = DetectorSLM(self.cliente, "m", cargar_prompt("c-json-corte"), "rol").mensajes(lineas)
        self.assertEqual(pedido["messages"], mensajes)
        self.assertEqual(pedido["format"], ESQUEMA_SALIDA)
        self.assertNotIn("think", pedido)
        self.assertNotIn("logprobs", pedido)
        self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096,
                                             "num_predict": MAXIMO_TOKENS_CORTE_RIESGO})

    def test_sin_aviso_una_sola_consulta(self):
        r = self.detector().evaluar(roles(("O", "Hola")))
        self.assertTrue(r.valida, r.error)
        self.assertEqual((r.riesgo, r.alerta_sugerida, r.alerta_escrita, r.pedido_critico), (0.1, False, None, None))
        self.assertEqual((r.ms_etapa2, r.motivo), (None, ""))
        self.assertEqual(len(OllamaCongelada.pedidos), 1)

    def test_avisa_con_0_3_y_no_con_0_05(self):
        self.assertTrue(self.detector().evaluar(roles(("O", "Te llamo de soporte"))).alerta_sugerida)
        r = self.detector().evaluar(roles(("O", "DOS_DECIMALES")))
        self.assertEqual((r.valida, r.riesgo, r.alerta_sugerida), (True, 0.05, False))

    def test_el_motivo_va_solo_en_el_primer_aviso(self):
        lineas = roles(("O", "Hola"), ("O", "Te llamo de soporte"), ("P", "Ah"), ("O", "Decime el código"))
        resultados = list(correr.procesar_caso(self.detector(), lineas, detener_en_aviso=False))
        self.assertEqual([aviso for *_, aviso in resultados], [False, True, False, False])
        self.assertEqual([r.alerta_sugerida for _, _, r, _ in resultados], [False, True, True, True])
        self.assertEqual([r.motivo for _, _, r, _ in resultados],
                         ["", "Dice ser de soporte sin que lo hayas pedido", "", ""])
        (motivo,) = self.motivos()
        primera_de_l2 = OllamaCongelada.pedidos[1]
        self.assertEqual(motivo["options"]["num_predict"], MAXIMO_TOKENS_RESPUESTA)
        self.assertEqual(motivo["messages"][:2], primera_de_l2["messages"], "empieza igual: reutiliza la caché")
        self.assertEqual(motivo["messages"][2], {"role": "assistant", "content": '{\n  "riesgo": 0.3\n}'})
        self.assertEqual(motivo["messages"][3], {"role": "user", "content": cargar_prompt_motivo(PROMPT_MOTIVO_C)})
        r = resultados[1][2]
        self.assertTrue(r.evidencia_en_texto)
        self.assertEqual((r.ms_etapa1 is not None, r.ms_etapa2 is not None), (True, True))

    def test_el_motivo_se_reinicia_entre_llamadas(self):
        d = self.detector()
        for _ in range(2):
            self.assertEqual([aviso for *_, aviso in correr.procesar_caso(d, roles(("O", "Decime el código")))], [True])
        self.assertEqual(len(self.motivos()), 2)

    def test_si_falla_el_motivo_el_aviso_queda(self):
        OllamaCongelada.motivo_roto = True
        r = self.detector().evaluar(roles(("O", "Decime el código")))
        self.assertTrue(r.valida and r.alerta_sugerida)
        self.assertEqual((r.error, r.motivo), ("etapa2_json_invalido", ""))

    def test_motivo_diferido_avisa_sin_esperar_y_completa_igual(self):
        # #172: el aviso sale con la primera consulta; el motivo, con la misma segunda consulta, después.
        lineas = roles(("O", "Te llamo de soporte"))
        r_junto = self.detector().evaluar(lineas)
        pedidos_junto = list(OllamaCongelada.pedidos)
        OllamaCongelada.pedidos.clear()
        d = self.detector()
        d.motivo_diferido = True
        r = d.evaluar(lineas)
        self.assertEqual((r.valida, r.alerta_sugerida, r.motivo_pendiente, r.motivo), (True, True, True, ""))
        self.assertEqual(self.motivos(), [], "la segunda consulta todavía no corrió")
        completa = d.completar_motivo(r)
        self.assertEqual(OllamaCongelada.pedidos, pedidos_junto, "los mismos pedidos, en el mismo orden")
        self.assertFalse(completa.motivo_pendiente)
        for campo in ("riesgo", "alerta_sugerida", "motivo", "evidencia", "evidencia_en_texto", "crudo", "error"):
            self.assertEqual(getattr(completa, campo), getattr(r_junto, campo), campo)
        self.assertEqual(completa.ms_etapa1, r.ms_etapa1)
        with self.assertRaises(ValueError):
            d.completar_motivo(r)

    def test_motivo_diferido_solo_en_el_primer_aviso(self):
        d = self.detector()
        d.motivo_diferido = True
        lineas = roles(("O", "Te llamo de soporte"), ("O", "Decime el código"))
        r1 = d.evaluar(lineas[:1])
        r2 = d.evaluar(lineas)
        self.assertEqual((r1.motivo_pendiente, r2.motivo_pendiente, r2.alerta_sugerida), (True, False, True))

    def test_sin_la_coma_es_fallo_y_no_avisa(self):
        r = self.detector().evaluar(roles(("O", "Decime el código SIN_COMA")))
        self.assertEqual((r.valida, r.error, r.alerta_sugerida), (False, "sin_riesgo", None))
        self.assertEqual(self.motivos(), [])

    def test_riesgo_fuera_de_rango_es_fallo(self):
        r = self.detector().evaluar(roles(("O", "FUERA")))
        self.assertEqual((r.valida, r.error, r.riesgo), (False, "riesgo_fuera_de_rango", 1.5))


class TestSoloOtra(_ConServidor):
    def test_las_lineas_de_protegida_no_consultan(self):
        lineas = roles(("O", "Hola"), ("P", "Hola"), ("O", "¿Cómo va?"), ("P", "Bien"))
        resultados = list(correr.procesar_caso(self.detector(), lineas, solo_otra=True))
        self.assertEqual(len(resultados), 4, "las cuatro líneas quedan registradas")
        self.assertEqual(len(OllamaCongelada.pedidos), 2, "solo las dos de OTRA consultan")
        for _, linea, r, aviso in resultados:
            if linea.hablante == "PROTEGIDA":
                self.assertEqual((r.valida, r.alerta_sugerida, r.consulta, r.ms, aviso), (True, False, "omitida", None, False))
            else:
                self.assertEqual(r.consulta, "")

    def test_la_linea_de_protegida_entra_al_contexto_de_la_consulta_siguiente(self):
        lineas = roles(("O", "Hola"), ("P", "¿Es por lo de soporte?"), ("O", "Sí"))
        resultados = list(correr.procesar_caso(self.detector(), lineas, solo_otra=True))
        self.assertEqual([aviso for *_, aviso in resultados], [False, False, True], "avisa en la de OTRA, no en la de PROTEGIDA")
        self.assertIn("2. PROTEGIDA: ¿Es por lo de soporte?", OllamaCongelada.pedidos[1]["messages"][1]["content"])
        (motivo,) = self.motivos()
        self.assertEqual(motivo["messages"][:2], OllamaCongelada.pedidos[1]["messages"], "el motivo, en la línea de OTRA")

    def test_es_la_lectura_simulada_de_la_etapa_3(self):
        """La primera línea de OTRA que dispara en todas las líneas es el aviso de «solo OTRA», en cada llamada."""
        llamadas = [
            roles(("P", "Hola, soporte"), ("O", "Sí, ¿quién habla?"), ("P", "Yo"), ("O", "Decime el código")),
            roles(("O", "Hola"), ("P", "Hola"), ("O", "Te llamo de soporte"), ("P", "Ah")),
            roles(("O", "Hola"), ("P", "Chau")),
            roles(("O", "Hola"), ("P", "Bueno"), ("O", "SIN_COMA"), ("O", "Te llamo de soporte")),
        ]
        for lineas in llamadas:
            todas = list(correr.procesar_caso(self.detector(), lineas, detener_en_aviso=False))
            simulado = next((n for n, l, r, _ in todas if l.hablante == "OTRA" and r.valida and r.alerta_sugerida), None)
            real = next((n for n, _, _, aviso in correr.procesar_caso(self.detector(), lineas, solo_otra=True) if aviso), None)
            self.assertEqual(real, simulado, lineas)

    def test_en_modo_operativo_termina_en_el_aviso(self):
        lineas = roles(("O", "Te llamo de soporte"), ("P", "Ah"), ("O", "Decime el código"))
        self.assertEqual([n for n, *_ in correr.procesar_caso(self.detector(), lineas, solo_otra=True)], [1])

    def test_sin_roles_no_corre(self):
        with self.assertRaises(ValueError):
            list(correr.procesar_caso(self.detector(), (Linea("A", "Hola"),), solo_otra=True))


def correr_main(*args: str) -> tuple[dict, list[dict]]:
    """(manifiesto, filas) de una corrida de correr.main con los argumentos dados."""
    with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
        correr.main([*args, "--salida", tmp])
        (carpeta,) = Path(tmp).iterdir()
        manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
        with open(carpeta / "actualizaciones.csv", encoding="utf-8-sig", newline="") as f:
            return manifiesto, list(csv.DictReader(f))


class TestCorrer(_ConServidor):
    CASOS = "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01"

    def comunes(self) -> list[str]:
        return ["--modelos", "modelo-falso:1b", "--prompts", VARIANTE, "--hablantes", "rol", "--casos", self.CASOS,
                "--url", self.url]

    def test_corrida_solo_otra(self):
        manifiesto, filas = correr_main(*self.comunes(), "--sin-reglas", "--solo-otra")
        self.assertTrue(manifiesto["solo_otra"])
        self.assertEqual(manifiesto["modo_termino"], correr.MODO_OPERATIVO)
        corte = manifiesto["parametros_slm"]["corte_riesgo"]
        self.assertEqual(corte["num_predict"], MAXIMO_TOKENS_CORTE_RIESGO)
        self.assertEqual(corte["alerta_sugerida"], "riesgo >= 0.3")
        datos = manifiesto["prompts"][VARIANTE]
        self.assertEqual((datos["texto"], datos["esquema"]), (cargar_prompt(VARIANTE), ESQUEMA_SALIDA))
        self.assertEqual((datos["etapa2"]["huella"], datos["etapa2"]["esquema"]),
                         (huella(cargar_prompt_motivo(PROMPT_MOTIVO_C)), ESQUEMA_MOTIVO))
        protegida = [r for r in filas if r["hablante"] == "PROTEGIDA"]
        otra = [r for r in filas if r["hablante"] == "OTRA"]
        self.assertTrue(protegida and otra)
        self.assertTrue(all(r["consulta"] == "omitida" and r["ms"] == "" and r["aviso"] == "false" for r in protegida))
        self.assertEqual(len([p for p in OllamaCongelada.pedidos if p["format"] == ESQUEMA_SALIDA]), len(otra))
        for case_id in self.CASOS.split(","):
            propias = [r for r in filas if r["case_id"] == case_id]
            lineas = casos.con_roles(case_id, casos.cargar_texto(case_id))
            self.assertEqual([r["hablante"] for r in propias], [l.hablante for l in lineas[:len(propias)]])
            avisos = [r for r in propias if r["aviso"] == "true"]
            self.assertLessEqual(len(avisos), 1)
            if avisos:
                self.assertIs(propias[-1], avisos[0], "en modo operativo la llamada termina en el aviso")
                self.assertEqual(avisos[0]["hablante"], "OTRA")
                self.assertNotEqual(avisos[0]["ms_etapa2"], "", "el motivo, en el aviso")
            self.assertEqual([r["linea"] for r in propias if r["ms_etapa2"]], [r["linea"] for r in avisos])

    def test_solo_otra_necesita_roles_y_solo_el_slm(self):
        for extra in (["--hablantes", "ab", "--sin-reglas"], ["--hablantes", "rol,ab", "--sin-reglas"], []):
            with self.subTest(extra=extra), self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
                args = self.comunes()
                if "--hablantes" in extra:
                    i = args.index("--hablantes")
                    del args[i:i + 2]
                correr.main([*args, *extra, "--solo-otra"])

    def test_un_caso_sin_roles_frena_antes_de_correr(self):
        roles_json = json.loads(casos.ROLES.read_text(encoding="utf-8"))
        del roles_json["SC-WA-CODE-01-e01"]
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "roles.json"
            ruta.write_text(json.dumps(roles_json), encoding="utf-8")
            with mock.patch.object(casos, "ROLES", ruta), self.assertRaises(SystemExit) as fin, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                correr.main([*self.comunes(), "--sin-reglas", "--solo-otra", "--salida", tmp])
            self.assertIn("SC-WA-CODE-01-e01", str(fin.exception.code))
            self.assertEqual([p.name for p in Path(tmp).iterdir()], ["roles.json"], "no creó la carpeta de la corrida")
        self.assertEqual(OllamaCongelada.pedidos, [])


class TestParticion(unittest.TestCase):
    def test_desarrollo_son_los_244_sin_test(self):
        """Las 56 legítimas de test (ENT-T) y la reserva (CV2-T) nunca entran a desarrollo: los analizar.py de las
        etapas 2 y 3 y el de la humo esperan exactamente estos 244."""
        ids = casos.ids_de_casos(particion="desarrollo")
        self.assertEqual(len(ids), 244)
        self.assertEqual([i for i in ids if i.startswith(("CV2-T", "ENT-T"))], [])


# --- La regla de lectura de la humo (analizar.py), sobre corridas sintéticas ---
CARPETA = RAIZ / "corridas" / "2026-11-10_config-congelada-humo"
_spec = importlib.util.spec_from_file_location("analizar_config_congelada", CARPETA / "analizar.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
REF_M, REF_AV = an.referencia()  # la lectura simulada de la etapa 3, de la corrida c-json-corte de la etapa 2


def escribir_corrida(destino: Path, avisa: dict[str, int | None], *, motivos: dict[str, str] | None = None,
                     invalidas: int = 0, filas_extra=None, **cambios) -> None:
    """Una corrida sintética de la configuración congelada, como la registraría correr.py con --solo-otra en modo
    operativo: riesgo 0.3 en la línea `avisa[caso]` (que tiene que ser de OTRA) y 0.1 antes; las de PROTEGIDA no
    consultan; la llamada termina en el aviso, que lleva el motivo. Las primeras `invalidas` líneas consultadas sin aviso
    son fallos. `filas_extra(fila)` puede cambiar cada fila."""
    motivos = motivos or {}
    run = destino / "desarrollo" / "2026-11-11_000000_sintetica"
    run.mkdir(parents=True)
    manifiesto = {
        "codigo": {"commit": "f" * 40, "cambios_sin_commit_en_la_carpeta": False},
        "modo_termino": "operativo-hasta-aviso", "interrumpida": False, "particion": "desarrollo", "solo_otra": True,
        "ollama": {"version": an.e3.OLLAMA, "digests": {an.e3.MODELO: "sha256:" + an.e3.DIGEST}},
        "parametros_slm": {"num_ctx": 4096, "seed": 42, "temperatura": 0.0,
                           "corte_riesgo": {"num_predict": MAXIMO_TOKENS_CORTE_RIESGO}},
        "prompts": {VARIANTE: {"texto": cargar_prompt(VARIANTE), "esquema": esquema_de(VARIANTE),
                               "etapa2": {"texto": cargar_prompt_motivo(PROMPT_MOTIVO_C), "esquema": ESQUEMA_MOTIVO}}},
        "casos": {i: huella((casos.DIR_TEXTO / f"{i}.txt").read_text(encoding="utf-8")) for i in an.IDS},
    }
    manifiesto.update(cambios)
    (run / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False), encoding="utf-8")
    faltan_invalidas = invalidas
    with (run / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS, extrasaction="ignore")
        w.writeheader()
        for i in an.IDS:
            lineas = casos.con_roles(i, casos.cargar_texto(i))
            aviso_en = avisa.get(i)
            for n, linea in enumerate(lineas, start=1):
                otra = linea.hablante == "OTRA"
                fila = {"detector": "slm", "prompt": VARIANTE, "hablantes": "rol", "case_id": i, "linea": n,
                        "hablante": linea.hablante, "texto": linea.texto, "valida": "true", "error": "",
                        "alerta_sugerida": "false", "aviso": "false", "consulta": "" if otra else "omitida"}
                if otra:
                    fila.update(riesgo=0.1, ms=240, ms_etapa1=240, tokens_salida=MAXIMO_TOKENS_CORTE_RIESGO)
                    if n == aviso_en:
                        fila.update(riesgo=0.3, alerta_sugerida="true", aviso="true", ms=1040, ms_etapa2=800,
                                    motivo=motivos.get(i, "Puede ser una estafa"), evidencia=linea.texto,
                                    evidencia_en_texto="true")
                    elif faltan_invalidas:
                        faltan_invalidas -= 1
                        fila.update(valida="false", error="sin_riesgo", riesgo="", alerta_sugerida="")
                if filas_extra:
                    filas_extra(fila)
                w.writerow(fila)
                if n == aviso_en:
                    break


def escribir_humo(destino: Path, pasa: bool = True) -> None:
    (destino / "humo").mkdir(parents=True, exist_ok=True)
    humo = {"lineas": 48, "leidas": 48 if pasa else 47, "igual_a_c_json_corte": 46, "tokens_salida": "14 / 14 / 14",
            "dos_decimales": 1, "errores": [] if pasa else ["sin_riesgo"], "segunda_consulta": [], "pasa": pasa}
    (destino / "humo" / "humo.json").write_text(json.dumps(humo), encoding="utf-8")


def salida_de(datos: Path) -> str:
    salida = io.StringIO()
    with redirect_stdout(salida):
        an.main(["--datos", str(datos)])
    return salida.getvalue()


def leer_corrida(datos: Path):
    return an.e3.leer(datos, "desarrollo")


class TestReglaHumo(unittest.TestCase):
    def test_la_referencia_es_la_lectura_simulada_de_la_etapa_3(self):
        self.assertEqual(an.fmt(REF_M), ["35/46", "15/36", "25/36", "24/94"])
        self.assertTrue(all(REF_AV[i] is None or casos.con_roles(i, casos.cargar_texto(i))[REF_AV[i] - 1].hablante == "OTRA"
                            for i in an.IDS), "los avisos simulados caen en líneas de OTRA")

    def test_si_reproduce_la_etapa_3_queda_lista(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), REF_AV)
            escribir_humo(Path(tmp))
            filas, man = leer_corrida(Path(tmp))
            self.assertEqual(an.controlar(filas, man), [])
            salida = salida_de(Path(tmp))
        self.assertIn("la configuración queda lista para la evaluación final", salida)
        self.assertIn("Puede ser una estafa", salida, "los motivos de las FA, para leer a mano")

    def test_veredicto(self):
        m = dict(REF_M)
        self.assertEqual(an.veredicto(True, [], 0, 1000, m, REF_M)[0], "lista")
        self.assertEqual(an.veredicto(True, [], 10, 1000, m, REF_M)[0], "lista", "el 1 % justo pasa")
        self.assertEqual(an.veredicto(True, [], 11, 1000, m, REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(False, [], 0, 1000, m, REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(None, [], 0, 1000, m, REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(True, ["algo"], 0, 1000, m, REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(True, [], 0, 0, m, REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(True, [], 0, 1000, None, REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(True, [], 0, 1000, dict(m, fa=m["fa"] + 2), REF_M)[0], "lista", "±2 es ruido")
        self.assertEqual(an.veredicto(True, [], 0, 1000, dict(m, fa=m["fa"] + 3), REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(True, [], 0, 1000, dict(m, det=m["det"] - 3), REF_M)[0], "avisar a Mateo")
        self.assertEqual(an.veredicto(True, [], 0, 1000, dict(m, antes=m["antes"] + 3), REF_M)[0], "avisar a Mateo",
                         "también si sube: no reproduce")

    def test_tres_fa_mas_no_reproduce(self):
        legitimas_sin_aviso = [i for i in an.e3.LEGITIMAS if REF_AV[i] is None]
        avisa = dict(REF_AV)
        for i in legitimas_sin_aviso[:3]:
            avisa[i] = next(n for n, l in enumerate(casos.con_roles(i, casos.cargar_texto(i)), 1) if l.hablante == "OTRA")
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), avisa)
            escribir_humo(Path(tmp))
            salida = salida_de(Path(tmp))
        self.assertIn("avisar a Mateo", salida)
        self.assertIn("+3 FA", salida)

    def test_sin_humo_o_si_no_pasa_no_queda_lista(self):
        for pasa in (None, False):
            with self.subTest(pasa=pasa), tempfile.TemporaryDirectory() as tmp:
                escribir_corrida(Path(tmp), REF_AV)
                if pasa is not None:
                    escribir_humo(Path(tmp), pasa=pasa)
                self.assertIn("la humo de formato no pasó o falta", salida_de(Path(tmp)))

    def test_mas_del_1_por_ciento_de_invalidas(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), REF_AV, invalidas=40)
            escribir_humo(Path(tmp))
            salida = salida_de(Path(tmp))
        self.assertIn("líneas inválidas", salida)
        self.assertIn("avisar a Mateo", salida)

    def test_el_control(self):
        casos_ = [
            ("una línea de PROTEGIDA consulta",
             dict(filas_extra=lambda f: f.update(consulta="") if f["hablante"] == "PROTEGIDA" else None),
             "consultó en una línea de PROTEGIDA"),
            ("una línea de OTRA no consulta",
             dict(filas_extra=lambda f: f.update(consulta="omitida") if f["hablante"] == "OTRA" else None),
             "consultó en una línea de PROTEGIDA, o no consultó en una de OTRA"),
            ("el motivo fuera del aviso",
             dict(filas_extra=lambda f: f.update(ms_etapa2=700) if f["hablante"] == "OTRA" and f["aviso"] == "false" else None),
             "el motivo no se pidió solo en el aviso"),
            ("sin --solo-otra", dict(solo_otra=False), "no corrió con --solo-otra"),
            ("en todas las líneas", dict(modo_termino="diagnostico-completo"), "no corrió entera en modo operativo"),
            ("otro corte", dict(parametros_slm={"num_ctx": 4096, "seed": 42, "temperatura": 0.0,
                                                "corte_riesgo": {"num_predict": 12}}), "no es el corte tras el riesgo"),
            ("con cambios", dict(codigo={"commit": "f" * 40, "cambios_sin_commit_en_la_carpeta": True}),
             "corrió con cambios sin commitear"),
            ("con una lista", dict(lista="alcance-140"), "no es la partición de desarrollo entera"),
        ]
        for nombre, kw, problema in casos_:
            with self.subTest(nombre), tempfile.TemporaryDirectory() as tmp:
                escribir_corrida(Path(tmp), REF_AV, **kw)
                filas, man = leer_corrida(Path(tmp))
                problemas = an.controlar(filas, man)
                self.assertTrue(any(problema in p for p in problemas), problemas)

    def test_el_aviso_registrado_tiene_que_ser_el_de_la_regla(self):
        def riesgo_bajo_en_el_aviso(f):
            if f["aviso"] == "true":
                f["riesgo"] = 0.2
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), REF_AV, filas_extra=riesgo_bajo_en_el_aviso)
            problemas = an.controlar(*leer_corrida(Path(tmp)))
        self.assertIn("el aviso registrado no es el de «riesgo ≥ 0,3» en una línea de OTRA", problemas)

    def test_lineas_despues_del_aviso(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), REF_AV)
            filas, man = leer_corrida(Path(tmp))
            caso = next(i for i in an.IDS if REF_AV[i] and REF_AV[i] < len(casos.cargar_texto(i)))
            filas[caso].append(dict(filas[caso][-1], linea=str(REF_AV[caso] + 1), aviso="false", ms_etapa2=""))
            problemas = an.controlar(filas, man)
        self.assertTrue(any("las líneas no terminan en el aviso" in p for p in problemas), problemas)

    def test_un_caso_de_test_no_puede_entrar(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), REF_AV)
            filas, man = leer_corrida(Path(tmp))
            man["casos"]["ENT-T-BANCO-001"] = "0" * 16
            problemas = an.controlar(filas, man)
        self.assertIn("no son los 244 de desarrollo", problemas)
        self.assertIn("no es la partición de desarrollo entera", problemas)

    def test_el_motivo_que_nombra_un_pedido_en_una_fa_se_marca(self):
        fa = next(i for i in an.e3.LEGITIMAS if REF_AV[i] and an.e3.linea_critica(i) is None)
        with tempfile.TemporaryDirectory() as tmp:
            escribir_corrida(Path(tmp), REF_AV, motivos={fa: "Te están pidiendo un código | ojo"})
            escribir_humo(Path(tmp))
            salida = salida_de(Path(tmp))
        (fila,) = [l for l in salida.splitlines() if l.startswith(f"| {fa} |")]
        self.assertIn("| sí |", fila)
        self.assertIn("«Te están pidiendo un código \\| ojo»", fila, "la barra no rompe la tabla")
