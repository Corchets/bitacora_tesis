"""Etapa 3 de #143: C sin alerta (`c-sin-alerta`) y C con campo (`c-con-campo`), en una consulta por línea, con el motivo
propio de C, y la regla de corridas/2026-11-09_pedido-critico-etapa-3/analizar.py. Sin modelo: contra el Ollama falso de
test_ensayo.py, extendido con el JSON corto y el motivo, y sobre corridas sintéticas.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_etapa3_143 -v
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
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import casos  # noqa: E402
import correr  # noqa: E402
from casos import Linea  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (  # noqa: E402
    CORTE_DE,
    DIR_PROMPTS,
    ESQUEMA_CON_CAMPO,
    ESQUEMA_MOTIVO,
    ESQUEMA_RIESGO,
    ESQUEMA_SALIDA,
    MAXIMO_TOKENS_C_CORTO,
    MAXIMO_TOKENS_CORTE,
    MAXIMO_TOKENS_RESPUESTA,
    PROMPT_MOTIVO_C,
    PROMPT_MOTIVO_CORTE,
    PROMPTS_C_CORTO,
    DetectorSLM,
    DetectorSLMCCorto,
    cargar_prompt,
    cargar_prompt_motivo,
    esquema_de,
    huella,
    leer_c_corto,
)
from test_ensayo import OllamaFalso  # noqa: E402

CARPETA = RAIZ / "corridas" / "2026-11-09_pedido-critico-etapa-3"
_spec = importlib.util.spec_from_file_location("analizar_etapa3", CARPETA / "analizar.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)

# La definición de pedido crítico de Mateo (2026-11-09), tal como la aprobó.
EJEMPLOS = ("Por ejemplo: dictar un código que le llegó, decir una clave o un PIN, dar los datos completos de la tarjeta, "
            "mandar una foto del DNI o de su cara, transferir, pagar o entregar plata o la tarjeta, instalar un programa o "
            "compartir la pantalla, seguir pasos en el cajero o en la app, o cortar y llamar a otro número. Dar el número "
            "de DNI, la fecha de nacimiento, el nombre o la dirección no cuenta. Cuenta también si la frase la dice "
            "PROTEGIDA porque OTRA la llevó a eso, como «¿te leo el código?». No cuentan las advertencias, como «nunca te "
            "vamos a pedir el código».")
PROPOSITO = ("OTRA ya está llevando a PROTEGIDA a dar o hacer algo que le permita a alguien sacarle plata, tomar sus "
             "cuentas o hacerse pasar por ella")
# Palabra en la transcripción → (riesgo, pedido_critico) que escribe el modelo falso (gana la última que aparezca).
SALIDAS = [("soporte", ("0.3", False)), ("CAMPO_SOLO", ("0.1", True)), ("Decime el código", ("0.9", True)),
           ("FUERA", ("1.5", False))]


def json_c(riesgo: str, campo: bool | None) -> str:
    """El JSON corto de C como lo escribe Gemma 4: con `pedido_critico` adelante si el esquema lo pide."""
    if campo is None:
        return f'{{\n  "riesgo": {riesgo}\n}}'
    return f'{{\n  "pedido_critico": {str(campo).lower()},\n  "riesgo": {riesgo}\n}}'


class OllamaEtapa3(OllamaFalso):
    """El Ollama falso de test_ensayo.py, con lo que usa la etapa 3.

    - JSON corto de C (`c-sin-alerta`, `c-con-campo`): el riesgo y el campo de SALIDAS, según la transcripción, con
      done_reason "stop". Con «BUCLE» en la transcripción llega al tope (done_reason "length").
    - JSON de la etapa 2 (ESQUEMA_SALIDA, `c-json-corte`): cortado después de la alerta, como con num_predict 24.
    - Segunda consulta (ESQUEMA_MOTIVO): evidencia y motivo, o un texto roto con `motivo_roto`.
    - `/api/version` y `/api/tags` dicen lo que se les configure: el Colab en seco pide la versión y el digest reales.
    """

    pedidos: list[dict] = []
    motivo_roto = False
    version = "0.0-falso"
    modelo = "modelo-falso:1b"
    digest = "abc123"

    def do_GET(self):
        respuestas = {
            "/api/version": {"version": OllamaEtapa3.version},
            "/api/tags": {"models": [{"name": OllamaEtapa3.modelo, "digest": OllamaEtapa3.digest}]},
            "/api/ps": {"models": [{"name": OllamaEtapa3.modelo, "size": 600 * 1024**2, "size_vram": 0}]},
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
        OllamaEtapa3.pedidos.append(pedido)
        if formato == ESQUEMA_MOTIVO:
            contenido = "roto" if OllamaEtapa3.motivo_roto else json.dumps(
                {"evidencia": "Decime el código de activación", "motivo": "Te piden el código que te llegó"},
                ensure_ascii=False)
            self._responder({"message": {"content": contenido}, "done_reason": "stop", "prompt_eval_count": 40,
                             "eval_count": 30, "total_duration": 600_000_000})
            return
        transcripcion = pedido["messages"][1]["content"]
        riesgo, campo = "0.1", False
        for palabra, salida in SALIDAS:
            if palabra in transcripcion:
                riesgo, campo = salida
        if "alerta_sugerida" in formato.get("properties", {}):  # C de la etapa 2, cortado tras la alerta
            contenido = f'{{\n  "riesgo": {riesgo},\n  "alerta_sugerida": false,'
            self._responder({"message": {"content": contenido}, "done_reason": "length", "prompt_eval_count": 300,
                             "eval_count": MAXIMO_TOKENS_CORTE, "total_duration": 280_000_000})
            return
        contenido = json_c(riesgo, campo if "pedido_critico" in formato.get("properties", {}) else None)
        if "BUCLE" in transcripcion:
            self._responder({"message": {"content": contenido[:-4]}, "done_reason": "length", "prompt_eval_count": 300,
                             "eval_count": pedido["options"]["num_predict"], "total_duration": 400_000_000})
            return
        self._responder({"message": {"content": contenido}, "done_reason": "stop", "prompt_eval_count": 300,
                         "eval_count": 13 if "pedido_critico" not in contenido else 25, "total_duration": 200_000_000})


class _ConServidor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaEtapa3)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"
        cls.cliente = ClienteOllama(cls.url, timeout_s=5)

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def setUp(self):
        OllamaEtapa3.pedidos.clear()
        OllamaEtapa3.motivo_roto = False

    def detector(self, prompt: str = "c-sin-alerta") -> DetectorSLMCCorto:
        return DetectorSLMCCorto(self.cliente, "modelo-falso:1b", cargar_prompt(prompt), "rol", esquema=esquema_de(prompt))


def roles(*pares: tuple[str, str]) -> tuple[Linea, ...]:
    return tuple(Linea("OTRA" if quien == "O" else "PROTEGIDA", texto) for quien, texto in pares)


class TestPrompts(unittest.TestCase):
    def leer(self, nombre: str) -> str:
        return (DIR_PROMPTS / nombre).read_text(encoding="utf-8").strip()

    def test_las_dos_versiones_son_la_tarea_de_c_con_otro_json(self):
        tarea = self.leer("tarea_c.txt")
        self.assertEqual(cargar_prompt("c-sin-alerta"), f'{tarea}\n\n{self.leer("salida_json_c_sin_alerta.txt")}')
        self.assertEqual(cargar_prompt("c-con-campo"), f'{tarea}\n\n{self.leer("salida_json_c_con_campo.txt")}')
        self.assertEqual(PROMPTS_C_CORTO, {"c-sin-alerta", "c-con-campo"})

    def test_el_riesgo_se_define_igual_que_en_c(self):
        riesgo = next(l for l in self.leer("salida_json_c.txt").splitlines() if l.startswith('- "riesgo"'))
        for nombre in ("salida_json_c_sin_alerta.txt", "salida_json_c_con_campo.txt"):
            self.assertEqual(self.leer(nombre).splitlines()[-1], riesgo, nombre)

    def test_c_con_campo_usa_la_definicion_de_mateo(self):
        texto = self.leer("salida_json_c_con_campo.txt")
        self.assertIn(f'- "pedido_critico": true si {PROPOSITO}; si no, false. {EJEMPLOS}', texto)
        self.assertLess(texto.index('"pedido_critico"'), texto.index('"riesgo"'))

    def test_los_esquemas(self):
        self.assertEqual(esquema_de("c-sin-alerta"), ESQUEMA_RIESGO)
        self.assertEqual(esquema_de("c-con-campo"), ESQUEMA_CON_CAMPO)
        self.assertEqual(list(ESQUEMA_CON_CAMPO["properties"]), ["pedido_critico", "riesgo"])
        self.assertEqual(ESQUEMA_CON_CAMPO["properties"]["riesgo"], ESQUEMA_SALIDA["properties"]["riesgo"])

    def test_el_motivo_de_c_pide_evidencia_y_despues_motivo(self):
        texto = cargar_prompt_motivo(PROMPT_MOTIVO_C)
        self.assertLess(texto.index('"evidencia"'), texto.index('"motivo"'))
        self.assertIn("frase de OTRA", texto)
        self.assertIn("Nombrá un pedido solo si ya ocurrió", texto)


class TestLeerCCorto(unittest.TestCase):
    def test_c_sin_alerta(self):
        self.assertEqual(leer_c_corto(json_c("0.3", None), ESQUEMA_RIESGO), (0.3, None, ""))
        self.assertEqual(leer_c_corto('{"riesgo": 1}', ESQUEMA_RIESGO), (1.0, None, ""))

    def test_c_con_campo(self):
        self.assertEqual(leer_c_corto(json_c("0.1", True), ESQUEMA_CON_CAMPO), (0.1, True, ""))
        self.assertEqual(leer_c_corto(json_c("0.6", False), ESQUEMA_CON_CAMPO), (0.6, False, ""))

    def test_fallos(self):
        self.assertEqual(leer_c_corto("roto", ESQUEMA_RIESGO)[2], "json_invalido")
        self.assertEqual(leer_c_corto("[1]", ESQUEMA_RIESGO)[2], "json_no_es_objeto")
        self.assertEqual(leer_c_corto('{"riesgo": 0.3}', ESQUEMA_CON_CAMPO)[2], "faltan_campos: pedido_critico")
        self.assertEqual(leer_c_corto('{"pedido_critico": "si", "riesgo": 0.3}', ESQUEMA_CON_CAMPO)[2],
                         "pedido_critico_no_booleano")
        self.assertEqual(leer_c_corto('{"riesgo": true}', ESQUEMA_RIESGO)[2], "riesgo_no_numerico")
        self.assertEqual(leer_c_corto('{"riesgo": 1.5}', ESQUEMA_RIESGO), (1.5, None, "riesgo_fuera_de_rango"))


class TestDetector(_ConServidor):
    def test_mismo_pedido_que_c_con_su_prompt_y_esquema(self):
        lineas = roles(("O", "Hola, ¿qué tal?"), ("P", "Bien"))
        for prompt, esquema in (("c-sin-alerta", ESQUEMA_RIESGO), ("c-con-campo", ESQUEMA_CON_CAMPO)):
            OllamaEtapa3.pedidos.clear()
            self.detector(prompt).evaluar(lineas)
            (pedido,) = OllamaEtapa3.pedidos
            mensajes, _ = DetectorSLM(self.cliente, "m", cargar_prompt(prompt), "rol").mensajes(lineas)
            self.assertEqual(pedido["messages"], mensajes)
            self.assertEqual(pedido["format"], esquema)
            self.assertNotIn("think", pedido)
            self.assertNotIn("logprobs", pedido)
            self.assertEqual(pedido["options"], {"temperature": 0.0, "seed": 42, "num_ctx": 4096,
                                                 "num_predict": MAXIMO_TOKENS_C_CORTO})

    def test_sin_aviso_una_sola_consulta(self):
        r = self.detector("c-con-campo").evaluar(roles(("O", "Hola")))
        self.assertTrue(r.valida, r.error)
        self.assertEqual((r.riesgo, r.pedido_critico, r.alerta_sugerida, r.alerta_escrita), (0.1, False, False, None))
        self.assertEqual(len(OllamaEtapa3.pedidos), 1)

    def test_avisa_con_0_3_en_cualquier_linea_sin_pedir_el_motivo(self):
        lineas = roles(("P", "Hola, soporte"), ("O", "Te llamo de soporte"), ("O", "Decime el código"))
        resultados = list(correr.procesar_caso(self.detector(), lineas, detener_en_aviso=False))
        self.assertEqual([aviso for *_, aviso in resultados], [True, False, False])
        self.assertEqual((resultados[0][2].riesgo, resultados[0][2].motivo), (0.3, ""))
        self.assertEqual(len(OllamaEtapa3.pedidos), 3, "C sin alerta no tiene alerta fuerte: nunca pide el motivo")

    def test_el_motivo_va_solo_en_la_primera_alerta_fuerte(self):
        lineas = roles(("O", "Te llamo de soporte"), ("P", "Ah"), ("O", "Decime el código"), ("P", "Bueno"))
        resultados = list(correr.procesar_caso(self.detector("c-con-campo"), lineas, detener_en_aviso=False))
        self.assertEqual([aviso for *_, aviso in resultados], [True, False, False, False])
        self.assertEqual([r.pedido_critico for _, _, r, _ in resultados], [False, False, True, True])
        self.assertEqual([r.motivo for _, _, r, _ in resultados], ["", "", "Te piden el código que te llegó", ""])
        motivos = [p for p in OllamaEtapa3.pedidos if p["format"] == ESQUEMA_MOTIVO]
        self.assertEqual(len(motivos), 1, "una vez por llamada")
        (motivo,) = motivos
        primera_de_l3 = next(p for p in OllamaEtapa3.pedidos if p["format"] == ESQUEMA_CON_CAMPO
                             and "Decime el código" in p["messages"][1]["content"])
        self.assertEqual(motivo["options"]["num_predict"], MAXIMO_TOKENS_RESPUESTA)
        self.assertEqual(motivo["messages"][:2], primera_de_l3["messages"], "empieza igual: reutiliza la caché")
        self.assertEqual(motivo["messages"][2], {"role": "assistant", "content": json_c("0.9", True)})
        self.assertEqual(motivo["messages"][3], {"role": "user", "content": cargar_prompt_motivo(PROMPT_MOTIVO_C)})

    def test_el_campo_solo_tambien_avisa(self):
        r = self.detector("c-con-campo").evaluar(roles(("O", "CAMPO_SOLO")))
        self.assertTrue(r.valida and r.alerta_sugerida)
        self.assertEqual((r.riesgo, r.pedido_critico), (0.1, True))
        motivo = OllamaEtapa3.pedidos[1]
        self.assertEqual(motivo["messages"][2]["content"], json_c("0.1", True))

    def test_sin_campo_el_detector_de_c_sin_alerta_lo_ignora(self):
        r = self.detector("c-sin-alerta").evaluar(roles(("O", "CAMPO_SOLO")))
        self.assertEqual((r.riesgo, r.pedido_critico, r.alerta_sugerida), (0.1, None, False))

    def test_llegar_al_tope_es_fallo(self):
        r = self.detector().evaluar(roles(("O", "BUCLE")))
        self.assertFalse(r.valida)
        self.assertEqual(r.error, "salida_cortada")

    def test_riesgo_fuera_de_rango_es_fallo(self):
        r = self.detector().evaluar(roles(("O", "FUERA")))
        self.assertEqual((r.valida, r.error, r.riesgo), (False, "riesgo_fuera_de_rango", 1.5))

    def test_si_falla_el_motivo_el_aviso_queda(self):
        OllamaEtapa3.motivo_roto = True
        r = self.detector("c-con-campo").evaluar(roles(("O", "Decime el código")))
        self.assertTrue(r.valida and r.alerta_sugerida)
        self.assertEqual(r.error, "etapa2_json_invalido")

    def test_el_motivo_se_reinicia_entre_llamadas(self):
        d = self.detector("c-con-campo")
        for _ in range(2):
            self.assertEqual([aviso for *_, aviso in correr.procesar_caso(d, roles(("O", "Decime el código")))], [True])
        self.assertEqual(sum(p["format"] == ESQUEMA_MOTIVO for p in OllamaEtapa3.pedidos), 2)


class TestCorrer(_ConServidor):
    def test_corrida_en_todas_las_lineas(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            correr.main(["--modelos", "modelo-falso:1b", "--prompts", "c-json-corte,c-sin-alerta,c-con-campo",
                         "--hablantes", "rol", "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01", "--sin-reglas",
                         "--seguir-tras-aviso", "--url", self.url, "--salida", tmp])
            (carpeta,) = Path(tmp).iterdir()
            manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
            with open(carpeta / "actualizaciones.csv", encoding="utf-8-sig", newline="") as f:
                filas = list(csv.DictReader(f))
        corto = manifiesto["parametros_slm"]["c_corto"]
        self.assertEqual(corto["num_predict"], MAXIMO_TOKENS_C_CORTO)
        self.assertIn("riesgo >= 0.3 o pedido_critico", corto["alerta_sugerida"])
        self.assertEqual(manifiesto["parametros_slm"]["json_cortado"]["num_predict"], MAXIMO_TOKENS_CORTE)
        self.assertEqual(manifiesto["prompts"]["c-json-corte"]["etapa2"]["texto"], cargar_prompt_motivo(PROMPT_MOTIVO_CORTE))
        for prompt in ("c-sin-alerta", "c-con-campo"):
            datos = manifiesto["prompts"][prompt]
            self.assertEqual((datos["texto"], datos["esquema"]), (cargar_prompt(prompt), esquema_de(prompt)))
            self.assertEqual(datos["etapa2"]["huella"], huella(cargar_prompt_motivo(PROMPT_MOTIVO_C)))
            propias = [r for r in filas if r["prompt"] == prompt]
            self.assertEqual(len(propias), 9, "5 + 4 líneas")
            self.assertTrue(all(r["valida"] == "true" for r in propias))
            sc = [r for r in propias if r["case_id"] == "SC-WA-CODE-01-e01"]
            self.assertEqual([r["aviso"] for r in sc], ["true", "false", "false", "false", "false"])
            self.assertEqual((sc[0]["riesgo"], sc[3]["riesgo"]), ("0.3", "0.9"))
            self.assertEqual(sc[3]["pedido_critico"], "true" if prompt == "c-con-campo" else "")
            self.assertEqual([bool(r["ms_etapa2"]) for r in sc],
                             [False, False, False, prompt == "c-con-campo", False], "el motivo, en la alerta fuerte")
        self.assertEqual({r["pedido_critico"] for r in filas if r["prompt"] == "c-json-corte"}, {""})


# --- La regla de analizar.py, sobre corridas sintéticas ---
def escribir_corrida(destino: Path, prompt: str, lista: str | None, avisa: dict[str, int],
                     campo: dict[str, int] | None = None, motivos: dict[str, str] | None = None, **cambios) -> None:
    """Una corrida sintética: riesgo 0.6 desde la línea `avisa[caso]` y 0.1 antes; con C con campo, `pedido_critico` en
    true desde `campo[caso]`. El aviso registrado es el de la regla, en cualquier línea, como lo registraría correr.py, y
    el motivo va en la primera alerta fuerte. `c-json-corte` imita la corrida de C de la etapa 2 (alerta escrita en
    false; el motivo, en el aviso)."""
    campo, motivos = campo or {}, motivos or {}
    ids = sorted(an.VISTA) if lista else an.IDS
    run = destino / "2026-11-10_000000_sintetica"
    run.mkdir(parents=True)
    etapa_2 = prompt == "c-json-corte"
    manifiesto = {
        "codigo": {"commit": "f" * 40, "cambios_sin_commit_en_la_carpeta": False},
        "modo_termino": "diagnostico-completo", "interrumpida": False, "particion": "desarrollo",
        **({"lista": lista} if lista else {}),
        "ollama": {"version": an.OLLAMA, "digests": {an.MODELO: "sha256:" + an.DIGEST}},
        "parametros_slm": {"num_ctx": 4096, "seed": 42, "temperatura": 0.0, "c_corto": {"num_predict": MAXIMO_TOKENS_C_CORTO}},
        "prompts": {prompt: {"texto": cargar_prompt(CORTE_DE.get(prompt, prompt)), "esquema": esquema_de(prompt),
                             "etapa2": {"texto": cargar_prompt_motivo(PROMPT_MOTIVO_C), "esquema": ESQUEMA_MOTIVO}}},
        "casos": {i: huella((casos.DIR_TEXTO / f"{i}.txt").read_text(encoding="utf-8")) for i in ids},
    }
    manifiesto.update(cambios)
    (run / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False), encoding="utf-8")
    columnas = correr.COLUMNAS + (correr.COLUMNAS_CORTE if etapa_2 else correr.COLUMNAS_CAMPO)
    with (run / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        for i in ids:
            lineas = casos.con_roles(i, casos.cargar_texto(i))
            desde, fuerte = avisa.get(i), campo.get(i)
            riesgo = [0.6 if desde and n >= desde else 0.1 for n in range(1, len(lineas) + 1)]
            pedido = [bool(fuerte and n >= fuerte) for n in range(1, len(lineas) + 1)]
            aviso_en = next((n for n in range(1, len(lineas) + 1) if riesgo[n - 1] >= 0.3 or pedido[n - 1]), None)
            motivo_en = aviso_en if etapa_2 else next((n for n in range(1, len(lineas) + 1) if pedido[n - 1]), None)
            otra = next(l.texto for l in lineas if l.hablante == "OTRA")
            for n, linea in enumerate(lineas, start=1):
                primera, con_motivo = n == aviso_en, n == motivo_en
                w.writerow({"detector": "slm", "prompt": prompt, "hablantes": "rol", "case_id": i, "linea": n,
                            "hablante": linea.hablante, "texto": linea.texto, "valida": "true", "error": "",
                            "riesgo": riesgo[n - 1], "alerta_sugerida": str(riesgo[n - 1] >= 0.3 or pedido[n - 1]).lower(),
                            "aviso": str(primera).lower(), "alerta_escrita": "false",
                            "pedido_critico": str(pedido[n - 1]).lower() if prompt == "c-con-campo" else "",
                            "ms_etapa1": 200, "tokens_prompt": 900, "tokens_salida": 13,
                            "ms_etapa2": 650 if con_motivo else "",
                            "motivo": motivos.get(i, "Puede ser una estafa") if con_motivo else "",
                            "evidencia": otra if con_motivo else "", "evidencia_en_texto": "true" if con_motivo else ""})


def avisos_desde(estafas: int, legitimas, linea: str = "pedido") -> dict[str, int]:
    """Avisa desde la línea del pedido (o la 1 si no hay; o siempre la 1) en las primeras `estafas` estafas, y desde
    la 1 en las primeras `legitimas` legítimas (o en las de la lista)."""
    av = {i: (an.REF[i].get("t_r_linea") or 1) if linea == "pedido" else 1 for i in an.ESTAFAS[:estafas]}
    av.update({i: 1 for i in (an.LEGITIMAS[:legitimas] if isinstance(legitimas, int) else legitimas)})
    return av


ETAPA_2 = {"c-json-corte": None, "c-json-corte-rep": "alcance-140"}


class TestRegla(unittest.TestCase):
    def test_comparar(self):
        ref = {"det": 20, "antes": 10, "en": 5}
        self.assertEqual(an.comparar({"det": 23, "antes": 10, "en": 5}, ref)[:2], ("gana", ["estafas"]))
        self.assertEqual(an.comparar({"det": 20, "antes": 10, "en": 8}, ref)[:2], ("gana", ["a tiempo"]))
        self.assertEqual(an.comparar({"det": 22, "antes": 12, "en": 5}, ref)[0], "ruido")
        self.assertEqual(an.comparar({"det": 24, "antes": 6, "en": 9}, ref)[0], "mixto")

    def test_dentro_de_2_en_las_cuatro_cifras(self):
        ref = {"det": 20, "antes": 10, "en": 5, "fa": 10}
        self.assertTrue(an.dentro({"det": 22, "antes": 8, "en": 7, "fa": 12}, ref))
        self.assertFalse(an.dentro({"det": 20, "antes": 10, "en": 5, "fa": 13}, ref))

    def test_solo_otra_no_puede_empeorar_mas_de_2(self):
        todas = {"det": 36, "antes": 17, "en": 8, "fa": 27}
        self.assertTrue(an.no_empeora({"det": 35, "antes": 15, "en": 10, "fa": 24}, todas), "las cifras de la etapa 2")
        self.assertTrue(an.no_empeora({"det": 34, "antes": 15, "en": 10, "fa": 29}, todas))
        self.assertFalse(an.no_empeora({"det": 33, "antes": 17, "en": 8, "fa": 27}, todas))
        self.assertFalse(an.no_empeora({"det": 36, "antes": 17, "en": 8, "fa": 30}, todas))
        self.assertFalse(an.no_empeora({"det": 36, "antes": 14, "en": 11, "fa": 27}, todas), "antes del pedido baja 3")

    def test_el_tope_de_fa_es_la_base_mas_5_en_las_dos_corridas(self):
        ref = {"det": 20, "antes": 10, "en": 5, "fa": 10}
        m = {"det": 25, "antes": 10, "en": 5, "fa": 15}
        self.assertEqual(an.veredicto(m, ref, dict(m, det=24), ref)[0], "adopta")
        self.assertEqual(an.veredicto(dict(m, fa=16), ref, m, ref)[0], "queda la base")
        self.assertEqual(an.veredicto(m, ref, dict(m, fa=16), ref)[0], "queda la base")
        self.assertEqual(an.veredicto(m, ref, dict(m, fa=16), dict(ref, fa=11))[0], "adopta",
                         "la repetición se compara con la repetición de la base")

    def test_la_lectura_y_la_alerta_fuerte(self):
        filas = {"x": [{"linea": "1", "hablante": "PROTEGIDA", "valida": "true", "riesgo": "0.6", "pedido_critico": ""},
                       {"linea": "2", "hablante": "OTRA", "valida": "true", "riesgo": "0.1", "pedido_critico": "true"},
                       {"linea": "3", "hablante": "OTRA", "valida": "true", "riesgo": "0.3", "pedido_critico": "false"}]}
        self.assertEqual(an.avisos(filas, ["x"]), {"x": 1})
        self.assertEqual(an.avisos(filas, ["x"], rol="OTRA"), {"x": 2})
        self.assertEqual(an.avisos(filas, ["x"], rol="OTRA", campo=False), {"x": 3})
        self.assertEqual(an.avisos(filas, ["x"], solo_campo=True), {"x": 2})


class TestAnalisis(unittest.TestCase):
    def correr_analisis(self, corridas: dict, etapa_2=None, motivos=None, humo=None, codigo_esperado=0,
                        sin_etapa_2=False) -> str:
        etapa_2 = etapa_2 or {"c-json-corte": avisos_desde(20, 10), "c-json-corte-rep": avisos_desde(20, 10)}
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida:
            datos, e2 = Path(tmp) / "etapa-3", Path(tmp) / "etapa-2"
            for carpeta, (avisa, campo) in corridas.items():
                prompt, lista = an.CORRIDAS[carpeta]
                escribir_corrida(datos / carpeta, prompt, lista, avisa, campo, motivos)
            if not sin_etapa_2:
                for carpeta, avisa in etapa_2.items():
                    escribir_corrida(e2 / carpeta, "c-json-corte", ETAPA_2[carpeta], avisa)
            if humo:
                (datos / "humo").mkdir(parents=True)
                (datos / "humo" / "humo.json").write_text(json.dumps(humo), encoding="utf-8")
            codigo = an.main(["--datos", str(datos), "--etapa-2", str(e2)])
        self.assertEqual(codigo, codigo_esperado, salida.getvalue())
        return salida.getvalue()

    def todas(self, base, campo, base_rep=None, campo_rep=None) -> dict:
        return {"c-sin-alerta": base, "c-con-campo": campo, "c-sin-alerta-rep": base_rep or base,
                "c-con-campo-rep": campo_rep or campo}

    def test_c_con_campo_gana_y_la_repeticion_lo_sostiene(self):
        texto = self.correr_analisis(self.todas((avisos_desde(21, 10), None), (avisos_desde(25, 12), None),
                                                campo_rep=(avisos_desde(24, 12), None)))
        self.assertIn("Sin problemas de control", texto)
        self.assertIn("**la base es C sin alerta.**", texto)
        self.assertIn("La base (C sin alerta (`c-sin-alerta`)) tiene 10/94 FA, así que C con campo puede tener hasta 15.", texto)
        self.assertIn("y la repetición lo sostiene", texto)
        self.assertIn("En alcance-91 el resultado no se invierte.", texto)
        self.assertIn("**Se adopta C con campo (`c-con-campo`), provisorio hasta la reserva.**", texto)
        self.assertIn("### 4. «Solo OTRA» contra todas las líneas", texto)
        self.assertIn("para la configuración que queda (C con campo)", texto)
        for seccion in ("### Alerta fuerte", "### Costo por llamada de la política", "### Motivo de C",
                        "### C sin alerta contra C de la etapa 2, línea por línea", "### Latencia en T4 por tipo de consulta"):
            self.assertIn(seccion, texto)

    def test_el_campo_solo_suma_avisos(self):
        # La base avisa 20 estafas por el riesgo; C con campo, las mismas más 5 por `pedido_critico`, en el pedido.
        extra = {i: an.REF[i].get("t_r_linea") or 1 for i in an.ESTAFAS[20:25]}
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10), None), (avisos_desde(20, 10), extra)))
        self.assertIn("| C con campo (`c-con-campo`) | 25/46 |", texto)
        self.assertIn("**Se adopta C con campo", texto)

    def test_si_la_base_se_aparta_de_la_etapa_2_la_base_es_la_etapa_2(self):
        texto = self.correr_analisis(self.todas((avisos_desde(30, 10), None), (avisos_desde(30, 10), None)))
        self.assertIn("Alguna cifra se mueve más de ±2", texto)
        self.assertIn("**la base es el prompt de C de la etapa 2, cortado tras el riesgo**", texto)
        self.assertIn("| base: C de la etapa 2, cortado tras el riesgo | 20/46 |", texto)
        self.assertIn("**Se adopta C con campo", texto, "contra la etapa 2, C con campo suma 10 estafas")

    def test_con_mas_de_5_fa_queda_la_base(self):
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10), None), (avisos_desde(25, 16), None)))
        self.assertIn("pero suma más de 5 FA (16 > 15): no se adopta", texto)
        self.assertIn("**Queda la base, C sin alerta (`c-sin-alerta`), provisorio hasta la reserva.**", texto)

    def test_dentro_del_ruido_queda_la_base(self):
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10), None), (avisos_desde(22, 10), None)))
        self.assertIn("dentro de ±2 en las tres cifras: queda la base", texto)

    def test_si_gana_en_una_y_pierde_en_otra_decide_el_equipo(self):
        n_antes = sum(1 for i in an.ESTAFAS[:20] if (an.REF[i].get("t_r_linea") or 0) > 2)
        self.assertGreaterEqual(n_antes, 3)
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10, linea="1"), None), (avisos_desde(25, 10), None)),
                                     etapa_2={"c-json-corte": avisos_desde(20, 10, linea="1"),
                                              "c-json-corte-rep": avisos_desde(20, 10, linea="1")})
        self.assertIn("gana en una cifra y pierde 3 o más en otra: no se adopta, decide el equipo", texto)
        self.assertIn("**No se adopta C con campo por la regla: decide el equipo.**", texto)

    def test_si_se_invierte_en_alcance_91_decide_el_equipo(self):
        # La base tiene 3 FA en legítimas fuera de alcance-91; C con campo, 8 adentro. En los 140 suma 5 FA (pasa), y en
        # alcance-91 suma 8 (no pasa).
        afuera = [i for i in an.LEGITIMAS if i not in an.VISTA_91][:3]
        adentro = [i for i in an.LEGITIMAS if i in an.VISTA_91][:8]
        texto = self.correr_analisis(
            self.todas((avisos_desde(20, afuera), None), (avisos_desde(25, adentro), None)),
            etapa_2={"c-json-corte": avisos_desde(20, afuera), "c-json-corte-rep": avisos_desde(20, afuera)})
        self.assertIn("**En alcance-91 el resultado se invierte: decide el equipo.**", texto)
        self.assertIn("**No se adopta C con campo por la regla: decide el equipo.**", texto)

    def test_sin_c_con_campo_queda_la_base(self):
        texto = self.correr_analisis({"c-sin-alerta": (avisos_desde(20, 10), None)})
        self.assertIn("> Falta c-con-campo/.", texto)
        self.assertIn("falta la corrida: no cuenta", texto)
        self.assertIn("**Queda la base", texto)

    def test_el_motivo_que_nombra_un_pedido_antes_de_tiempo_se_marca(self):
        # Una alerta fuerte en la línea 1 de una legítima: el motivo nombra un código que nadie pidió.
        legitima = an.LEGITIMAS[0]
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10), None), (avisos_desde(20, 10), {legitima: 1})),
                                     motivos={legitima: "Te van a pedir el código que te llegó"})
        self.assertIn(f"- C con campo, {legitima} L1 (legitima): «Te van a pedir el código que te llegó»", texto)
        self.assertIn("| C sin alerta | 0 |", texto, "la base no pide el motivo")

    def test_la_humo_se_informa(self):
        humo = {p: {"lineas": 48, "leidas": 48, "al_tope": 0, "tokens_salida": "13 / 13 / 14",
                    "igual_a_c_json_corte": 46, "campo_true": 5 if p == "c-con-campo" else None, "pasa": True}
                for p in ("c-sin-alerta", "c-con-campo")}
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10), None), (avisos_desde(20, 10), None)), humo=humo)
        self.assertIn("| `c-sin-alerta` | 48/48 | 0 | 13 / 13 / 14 | 46/48 | — | PASA |", texto)
        self.assertIn("| `c-con-campo` | 48/48 | 0 | 13 / 13 / 14 | 46/48 | 5 | PASA |", texto)

    def test_sin_la_etapa_2_no_se_aplica_la_regla(self):
        texto = self.correr_analisis(self.todas((avisos_desde(20, 10), None), (avisos_desde(20, 10), None)),
                                     sin_etapa_2=True, codigo_esperado=1)
        self.assertIn("faltan c-json-corte/ o c-json-corte-rep/", texto)

    def test_un_problema_de_control_frena_la_regla(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida:
            escribir_corrida(Path(tmp) / "c-sin-alerta", "c-sin-alerta", None, avisos_desde(20, 10),
                             parametros_slm={"num_ctx": 4096, "seed": 42, "temperatura": 0.0})
            escribir_corrida(Path(tmp) / "c-con-campo", "c-con-campo", "alcance-140", avisos_desde(25, 10))
            self.assertEqual(an.main(["--datos", tmp, "--etapa-2", tmp]), 1)
        self.assertIn("no es el JSON corto de C", salida.getvalue())
        self.assertIn("casos distintos de los 244", salida.getvalue())
        self.assertIn("no se aplica la regla", salida.getvalue())

    def test_un_aviso_registrado_que_no_es_el_de_la_regla_frena(self):
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()) as salida:
            escribir_corrida(Path(tmp) / "c-sin-alerta", "c-sin-alerta", None, avisos_desde(20, 10))
            (run,) = (Path(tmp) / "c-sin-alerta").iterdir()
            texto = (run / "actualizaciones.csv").read_text(encoding="utf-8-sig")
            # Se borra un aviso registrado: el recalculado sigue ahí.
            (run / "actualizaciones.csv").write_text(texto.replace(",0.6,true,true,", ",0.6,true,false,", 1),
                                                     encoding="utf-8-sig")
            self.assertEqual(an.main(["--datos", tmp, "--etapa-2", tmp]), 1)
        self.assertIn("el aviso registrado no es el de «riesgo ≥ 0,3 o pedido_critico»", salida.getvalue())


if __name__ == "__main__":
    unittest.main()
