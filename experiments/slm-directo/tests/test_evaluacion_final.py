"""Evaluación final de #143: los conjuntos (conjuntos.py), `correr.py --conjunto` y el análisis
(corridas/2026-11-12_evaluacion-final/analizar.py). Sin modelo y sin la reserva: con una reserva sintética, el Ollama
falso de test_config_congelada_143.py y corridas sintéticas.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_evaluacion_final -v
"""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import shutil
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path
from unittest import mock

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import casos  # noqa: E402
import conjuntos  # noqa: E402
import correr  # noqa: E402
from cliente_ollama import ClienteOllama  # noqa: E402
from detectores import (ESQUEMA_MOTIVO, ESQUEMA_SALIDA, MAXIMO_TOKENS_CORTE, MAXIMO_TOKENS_CORTE_RIESGO,  # noqa: E402
                        PROMPT_MOTIVO_C, PROMPT_MOTIVO_CORTE, cargar_prompt, cargar_prompt_motivo, esquema_de, huella)
from test_config_congelada_143 import SALIDAS, OllamaCongelada, cortado  # noqa: E402

_spec = importlib.util.spec_from_file_location("analizar_final", RAIZ / "corridas/2026-11-12_evaluacion-final/analizar.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)

CONFIG = an.CONFIG
LIMPIO = {"commit": "f" * 40, "cambios_sin_commit_en_la_carpeta": False}

# Reserva sintética: id → (protegida, alcance, referencia, líneas). OTRA es la letra que no es PROTEGIDA.
ESTAFAS = {
    "CV2-T-V-SINT-001": ("B", "dentro", {"t_r_linea": 3, "t_c_linea": 4, "pedido": "REQUEST_AUTH_CODE", "dificultad": "directo"},
                         ["A: Hola, te llamo de soporte del banco.", "B: Ah, hola.", "A: Decime el código que te llegó.",
                          "B: Es 1234."]),
    "CV2-T-V-SINT-002": ("A", "dentro", {"t_r_linea": 4, "t_c_linea": 5, "pedido": "REQUEST_AUTH_CODE", "dificultad": "directo"},
                         ["A: Hola, ¿quién habla?", "B: Hola, soy tu sobrino.", "A: ¿Qué necesitás?",
                          "B: Decime el código que te llegó.", "A: Bueno, es 5678."]),
    "CV2-T-V-SINT-003": ("A", "dentro", {"t_r_linea": 4, "t_c_linea": None, "pedido": "REQUEST_PERSONAL_DATA",
                                         "dificultad": "indirecto"},
                         ["A: Hola.", "B: Hola, ganaste un premio.", "A: ¿En serio?", "B: Pasame tu número de documento."]),
    "CV2-T-V-SINT-004": ("A", "dentro", {"t_r_linea": None, "t_c_linea": None, "pedido": None, "dificultad": "sin_pedido"},
                         ["A: Hola.", "B: Llamo de soporte técnico."]),
}
VIEJAS = {
    "CV2-T-L-SINT-001": ("A", "dentro", "cotidiana", ["A: Hola.", "B: Hola, soy del delivery, estoy en la puerta."]),
    "CV2-T-L-SINT-002": ("B", "fuera", "pedido_razonable", ["A: Hola, llamo a soporte.", "B: Sí, ¿en qué te ayudo?"]),
}
NUEVAS = {
    "ENT-T-SINT-001": ("A", "cotidiana", ["A: Hola.", "B: Hola, te llamo por el turno del médico."]),
    "ENT-T-SINT-002": ("B", "pedido_razonable", ["A: Buen día, le hablo de soporte de la empresa.", "B: Ah, sí."]),
    "ENT-T-SINT-003": ("A", "mencion_sin_pedido", ["A: Hola.", "B: Nunca te vamos a pedir el código.", "A: Bien."]),
}


def armar_reserva(base: Path) -> tuple[Path, dict]:
    """Un checkout falso de reserva/test y los parámetros de preparar_test que apuntan a sus huellas."""
    origen = base / "reserva" / conjuntos.RESERVA_CASOS
    (origen / "texto").mkdir(parents=True)
    (origen / "referencia").mkdir()
    manifiesto, alcance = {"casos": {}}, {"_meta": {}, "casos": {}}
    filas = [(c, p, a, "vishing", None, ref, ls) for c, (p, a, ref, ls) in ESTAFAS.items()]
    filas += [(c, p, a, "legitima", t, {"t_r_linea": None, "t_c_linea": None, "pedido": None, "dificultad": t}, ls)
              for c, (p, a, t, ls) in VIEJAS.items()]
    for c, protegida, alc, clase, tipo, ref, lineas in filas:
        texto = "\n".join(lineas) + "\n"
        referencia = {"case_id": c, "grupo": "corpus_v2", "clase": clase, "particion": "test_reservado",
                      "tipo_legitima": tipo, "familia": "banco", **ref}
        (origen / "texto" / f"{c}.txt").write_text(texto, encoding="utf-8")
        (origen / "referencia" / f"{c}.json").write_text(json.dumps(referencia, ensure_ascii=False), encoding="utf-8")
        manifiesto["casos"][c] = {"particion": "test_reservado",
                                  "texto_sha256": conjuntos.sha256((origen / "texto" / f"{c}.txt").read_bytes()),
                                  "referencia_sha256": conjuntos.sha256((origen / "referencia" / f"{c}.json").read_bytes())}
        alcance["casos"][c] = {"protegida": protegida, "alcance": alc}
    jsonl = "".join(json.dumps({"case_id": c, "familia": "banco", "tipo_legitima": t, "variante_asr": False,
                                "protegida": p, "texto": ls}, ensure_ascii=False) + "\n" for c, (p, t, ls) in NUEVAS.items())
    (origen / "legitimas-entrantes-test.jsonl").write_text(jsonl, encoding="utf-8")
    (origen / "alcance-reserva.json").write_text(json.dumps(alcance), encoding="utf-8")
    (base / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
    return base / "reserva", {"manifiesto": base / "manifiesto.json",
                              "sha_legitimas": conjuntos.sha256(jsonl.encode("utf-8")),
                              "sha_alcance": conjuntos.sha256((origen / "alcance-reserva.json").read_bytes())}


class OllamaFinal(OllamaCongelada):
    """El Ollama falso de la configuración congelada, con la versión y el digest de las corridas reales, y que además
    responde a v4-corte: el JSON de v4 cortado tras `alerta_sugerida` (alerta escrita si el riesgo es ≥ 0,5)."""

    def do_GET(self):
        respuestas = {
            "/api/version": {"version": an.e3.OLLAMA},
            "/api/tags": {"models": [{"name": an.e3.MODELO, "digest": "sha256:" + an.e3.DIGEST}]},
            "/api/ps": {"models": [{"name": an.e3.MODELO, "size": 600 * 1024**2, "size_vram": 0}]},
        }
        self._responder(respuestas.get(self.path, {}), 200 if self.path in respuestas else 404)

    def do_POST(self):
        pedido = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        formato = pedido.get("format") or {}
        if "ok" in formato.get("properties", {}):
            self._responder({"message": {"content": json.dumps({"ok": True})}, "eval_count": 3})
            return
        if formato == ESQUEMA_MOTIVO:
            contenido = json.dumps({"evidencia": "soporte", "motivo": "Dice ser de soporte"}, ensure_ascii=False)
            self._responder({"message": {"content": contenido}, "done_reason": "stop", "eval_count": 30})
            return
        riesgo = "0.1"
        for palabra, valor in SALIDAS:
            if palabra in pedido["messages"][1]["content"]:
                riesgo = valor
        if pedido["options"]["num_predict"] == MAXIMO_TOKENS_CORTE:
            alerta = "true" if float(riesgo) >= 0.5 else "false"
            contenido = f'{{\n  "riesgo": {riesgo},\n  "alerta_sugerida": {alerta}'
        else:
            contenido = cortado(riesgo)
        self._responder({"message": {"content": contenido}, "done_reason": "length", "prompt_eval_count": 300,
                         "eval_count": pedido["options"]["num_predict"]})


def correr_main(*args: str) -> Path:
    """Corre correr.main y devuelve la carpeta de la corrida (con un commit limpio, como en Colab)."""
    with mock.patch.object(correr, "info_codigo", return_value=dict(LIMPIO)), redirect_stdout(io.StringIO()):
        correr.main(list(args))
    salida = Path(args[args.index("--salida") + 1])
    (run,) = [p for p in salida.iterdir() if (p / "manifiesto.json").exists()]
    return run


DETECTORES = {
    "config": ["--prompts", CONFIG, "--sin-reglas", "--solo-otra"],
    "v4": ["--prompts", an.V4, "--sin-reglas"],
    "reglas": ["--solo-reglas", "--reglas", "v1,v2"],
}


class _ConReserva(unittest.TestCase):
    """Una reserva sintética armada como conjunto en un directorio temporal."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.reserva, self.prueba = armar_reserva(self.tmp)
        self.conj = conjuntos.preparar_test(self.reserva, self.tmp / "conjuntos", **self.prueba)


class TestConjuntos(_ConReserva):
    def test_el_test_reservado_trae_los_cv2_t_y_las_ent_t_con_roles_y_vistas(self):
        self.assertEqual(self.conj.particion, "test_reservado")
        self.assertEqual(self.conj.ids, sorted([*ESTAFAS, *VIEJAS, *NUEVAS]))
        self.assertEqual(self.conj.validar(), [])
        roles, ref = self.conj.roles(), self.conj.referencia()
        self.assertEqual(roles["CV2-T-V-SINT-001"], {"protegida": "B"})  # de alcance-reserva.json
        self.assertEqual(roles["ENT-T-SINT-002"], {"protegida": "B"})    # del JSONL
        principal = sorted(i for i in ref if ref[i]["vista"] == conjuntos.PRINCIPAL)
        self.assertEqual(principal, sorted([*ESTAFAS, *NUEVAS]))
        self.assertIn("dentro", ref["CV2-T-L-SINT-001"]["vista"])
        self.assertIn("fuera", ref["CV2-T-L-SINT-002"]["vista"])
        self.assertEqual(ref["ENT-T-SINT-003"]["tipo_legitima"], "mencion_sin_pedido")
        self.assertEqual((ref["CV2-T-V-SINT-001"]["t_r_linea"], ref["CV2-T-V-SINT-001"]["t_c_linea"]), (3, 4))
        self.assertEqual(self.conj.crudo("ENT-T-SINT-001"), "\n".join(NUEVAS["ENT-T-SINT-001"][2]) + "\n")
        self.assertEqual([l.hablante for l in self.conj.con_roles("CV2-T-V-SINT-001", self.conj.cargar_texto("CV2-T-V-SINT-001"))],
                         ["OTRA", "PROTEGIDA", "OTRA", "PROTEGIDA"])

    def test_la_reserva_tocada_no_se_arma(self):
        origen = self.reserva / conjuntos.RESERVA_CASOS
        (origen / "texto" / "CV2-T-V-SINT-003.txt").write_text("A: Hola.\nB: Otra cosa.\n", encoding="utf-8")
        with self.assertRaises(ValueError) as e:
            conjuntos.preparar_test(self.reserva, self.tmp / "otro", **self.prueba)
        self.assertIn("CV2-T-V-SINT-003", str(e.exception))
        self.assertNotIn("Otra cosa", str(e.exception), "el error no muestra textos")
        with self.assertRaises(ValueError):
            conjuntos.preparar_test(self.reserva, self.tmp / "otro2", **{**self.prueba, "sha_legitimas": "0" * 64})

    def test_las_huellas_reales_por_defecto(self):
        self.assertEqual(conjuntos.SHA_LEGITIMAS_TEST[:12], "94dc3a7f084c")  # TEST-ALCANCE.md
        with self.assertRaises(ValueError):  # la reserva sintética no es la congelada
            conjuntos.preparar_test(self.reserva, self.tmp / "otro")

    def test_validar_encuentra_textos_roles_y_marcas_rotos(self):
        carpeta = self.conj.carpeta
        (carpeta / "texto" / "ENT-T-SINT-001.txt").write_text("hola sin hablante\n", encoding="utf-8")
        self.assertTrue(any("ENT-T-SINT-001" in e and "huella" in e for e in self.conj.validar()))
        roles = self.conj.roles()
        del roles["ENT-T-SINT-002"]
        (carpeta / "roles.json").write_text(json.dumps(roles), encoding="utf-8")
        self.assertTrue(any("ENT-T-SINT-002" in e for e in self.conj.validar()))
        ref = self.conj.referencia()
        ref["CV2-T-V-SINT-001"]["t_c_linea"] = 2
        self.assertTrue(any("t_c_linea" in e for e in conjuntos.validar_referencia(ref, {i: 5 for i in ref}, "x")))
        ref["CV2-T-V-SINT-001"]["t_c_linea"] = 4
        ref["ENT-T-SINT-001"]["t_r_linea"] = 1
        self.assertTrue(any("legítima" in e for e in conjuntos.validar_referencia(ref, {i: 5 for i in ref}, "x")))

    def test_desarrollo_son_los_244_con_alcance_140_de_vista(self):
        conj = conjuntos.preparar_desarrollo(self.tmp / "dev")
        ref = conj.referencia()
        self.assertEqual(conj.ids, casos.ids_de_casos(particion="desarrollo"))
        self.assertFalse([i for i in conj.ids if i.startswith(("CV2-T", "ENT-T"))])
        principal = [i for i in conj.ids if ref[i]["vista"] == conjuntos.PRINCIPAL]
        self.assertEqual(sorted(principal), sorted(an.e3.VISTA))
        self.assertEqual(sum(ref[i]["clase"] == "vishing" for i in principal), 46)
        self.assertEqual(json.loads(casos.ROLES.read_text(encoding="utf-8"))["CV2-D-L-BANCO-001"]["protegida"],
                         conj.roles()["CV2-D-L-BANCO-001"]["protegida"])
        self.assertTrue(all(conj.crudo(i) == (casos.DIR_TEXTO / f"{i}.txt").read_text(encoding="utf-8") for i in conj.ids))

    def test_el_externo_es_el_set_congelado_de_144(self):
        custodia = self.tmp / "custodia"
        (custodia / "texto").mkdir(parents=True)
        (custodia / "referencia").mkdir()
        (custodia / "texto" / "EXT-001.txt").write_text("A: Hola.\nB: Decime el código que te llegó.\n", encoding="utf-8")
        (custodia / "roles-protegida.json").write_text(json.dumps({"EXT-001": {"protegida": "A", "origen": "externo"}}),
                                                       encoding="utf-8")
        (custodia / "referencia" / "EXT-001.json").write_text(json.dumps({
            "case_id": "EXT-001", "grupo": "externo", "clase": "vishing", "t_r_linea": 2, "t_c_linea": None,
            "notas": "x"}), encoding="utf-8")
        manifiesto = self.tmp / "manifiesto-144.json"
        archivos = ["texto/EXT-001.txt", "roles-protegida.json", "referencia/EXT-001.json"]
        huellas = {a: conjuntos.sha256((custodia / a).read_bytes()) for a in archivos}
        manifiesto.write_text(json.dumps({**huellas, "correspondencia.json": "0" * 64}), encoding="utf-8")
        conj = conjuntos.preparar_externo(custodia, self.tmp / "ext", manifiesto=manifiesto)
        self.assertEqual((conj.nombre, conj.particion, conj.ids), ("externo", "externo", ["EXT-001"]))
        self.assertEqual(conj.roles(), {"EXT-001": {"protegida": "A"}})
        self.assertEqual(conj.referencia()["EXT-001"]["vista"], conjuntos.PRINCIPAL)
        self.assertEqual(conj.referencia()["EXT-001"]["t_r_linea"], 2)
        (custodia / "texto" / "EXT-001.txt").write_text("A: Hola.\nB: Otra cosa.\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            conjuntos.preparar_externo(custodia, self.tmp / "ext2", manifiesto=manifiesto)
        with self.assertRaises(ValueError):  # la carpeta sintética no es el set congelado real
            conjuntos.preparar_externo(custodia, self.tmp / "ext3")
        self.assertEqual(len([k for k in json.loads(conjuntos.MANIFIESTO_EXTERNO.read_text(encoding="utf-8"))
                              if k.startswith("texto/")]), 33)
        # Las 9 coreanas con ficha que están en el repo (PR #184) son parte del set congelado.
        repo = conjuntos.preparar_externo(RAIZ / "casos/externo/coreano", self.tmp / "ext-repo")
        self.assertEqual((len(repo.ids), repo.datos["fuentes"]["casos"]), (9, "9 de 33 del set congelado"))


class _ConServidor(_ConReserva):
    @classmethod
    def setUpClass(cls):
        cls.servidor = HTTPServer(("127.0.0.1", 0), OllamaFinal)
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.servidor.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()

    def correr(self, carpeta: str, conj=None, datos=None, *extra) -> Path:
        conj = conj or self.conj
        destino = (datos or self.tmp / "datos") / conj.nombre / carpeta
        destino.mkdir(parents=True, exist_ok=True)
        return correr_main("--conjunto", str(conj.carpeta), "--modelos", an.e3.MODELO, "--hablantes", "rol",
                           "--url", self.url, *DETECTORES[carpeta], *extra, "--salida", str(destino))


class TestCorrerConjunto(_ConServidor):
    def test_la_configuracion_corre_sobre_el_conjunto_sin_tocar_casos(self):
        run = self.correr("config")
        man = json.loads((run / "manifiesto.json").read_text(encoding="utf-8"))
        self.assertEqual(man["particion"], "test_reservado")
        self.assertEqual(man["conjunto"]["nombre"], "test_reservado")
        self.assertEqual(man["casos"], {i: huella(self.conj.crudo(i)) for i in self.conj.ids})
        self.assertEqual(man["roles_protegida"], huella(self.conj.ruta_roles.read_text(encoding="utf-8")))
        self.assertTrue(man["solo_otra"])
        por_config, _ = an.leer(run.parent)
        self.assertEqual(an.controlar("config", self.conj, por_config, man, CONFIG), [])
        filas = an.filas_de(por_config, man, "config", CONFIG)
        self.assertEqual(an.avisos_config(filas, ["CV2-T-V-SINT-001", "CV2-T-V-SINT-002", "CV2-T-V-SINT-003"]),
                         {"CV2-T-V-SINT-001": 1, "CV2-T-V-SINT-002": 4, "CV2-T-V-SINT-003": None})

    def test_v4_y_las_reglas_tambien(self):
        for carpeta in ("v4", "reglas"):
            run = self.correr(carpeta)
            man = json.loads((run / "manifiesto.json").read_text(encoding="utf-8"))
            por_config, _ = an.leer(run.parent)
            with self.subTest(carpeta=carpeta):
                self.assertEqual(an.controlar(carpeta, self.conj, por_config, man, CONFIG), [])
                self.assertFalse(man["solo_otra"])
        por_config, man = an.leer(self.tmp / "datos" / "test_reservado" / "reglas")
        self.assertEqual(an.avisos_reglas(an.filas_de(por_config, man, "reglas v1", None), ["ENT-T-SINT-003"]),
                         {"ENT-T-SINT-003": 2}, "v1 no entiende la negación")

    def test_conjunto_no_se_combina_con_particion_lista_ni_otros_casos(self):
        comunes = ["--conjunto", str(self.conj.carpeta), "--solo-reglas", "--salida", str(self.tmp / "x")]
        for extra in (["--particion", "test_reservado"], ["--lista", "alcance-140"], ["--casos", "CV2-D-V-BANCO-001"]):
            with self.subTest(extra=extra), self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
                correr.main([*comunes, *extra])

    def test_un_conjunto_tocado_no_corre(self):
        (self.conj.carpeta / "texto" / "ENT-T-SINT-001.txt").write_text("A: Hola.\nB: Cambiado.\n", encoding="utf-8")
        with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
            correr.main(["--conjunto", str(self.conj.carpeta), "--solo-reglas", "--salida", str(self.tmp / "x")])
        self.assertFalse((self.tmp / "x").exists() and any((self.tmp / "x").iterdir()))

    def test_el_control_detecta_corridas_que_no_son_la_evaluacion(self):
        run = self.correr("config")
        man = json.loads((run / "manifiesto.json").read_text(encoding="utf-8"))
        por_config, _ = an.leer(run.parent)
        casos_ = {
            "otro prompt": {"prompts": {"c-json-corte-riesgo": man["prompts"][CONFIG]}},
            "sin solo OTRA": {"solo_otra": False},
            "texto cambiado": {"casos": {**man["casos"], "ENT-T-SINT-001": "0" * 16}},
            "otro conjunto": {"conjunto": {**man["conjunto"], "nombre": "desarrollo"}},
            "cambios sin commitear": {"codigo": {**man["codigo"], "cambios_sin_commit_en_la_carpeta": True}},
            "diagnóstico": {"modo_termino": "diagnostico-completo"},
            "otro digest": {"ollama": {**man["ollama"], "digests": {an.e3.MODELO: "sha256:abc"}}},
        }
        for nombre, cambio in casos_.items():
            with self.subTest(nombre):
                self.assertNotEqual(an.controlar("config", self.conj, por_config, {**man, **cambio}, CONFIG), [])
        # Un aviso que no es el de la regla.
        filas = an.filas_de(por_config, man, "config", CONFIG)
        filas["CV2-T-V-SINT-001"][0]["riesgo"] = "0.2"
        self.assertTrue(any("regla" in p for p in an.controlar("config", self.conj, por_config, man, CONFIG)))


class TestCifras(unittest.TestCase):
    REF = {
        "e1": {"clase": "vishing", "t_r_linea": 5, "t_c_linea": 7},
        "e2": {"clase": "vishing", "t_r_linea": 5, "t_c_linea": 7},
        "e3": {"clase": "vishing", "t_r_linea": 5, "t_c_linea": None},
        "e4": {"clase": "vishing", "t_r_linea": None, "t_c_linea": None},
        "l1": {"clase": "legitima", "t_r_linea": None, "t_c_linea": None, "tipo_legitima": "cotidiana"},
        "l2": {"clase": "legitima", "t_r_linea": None, "t_c_linea": None, "tipo_legitima": "pedido_razonable"},
        "l3": {"clase": "legitima_dificil", "t_r_linea": None, "t_c_linea": None, "tipo_legitima": None},
    }

    def test_las_cifras_de_cada_caso(self):
        av = {"e1": 4, "e2": 5, "e3": 6, "e4": 2, "l1": None, "l2": 3, "l3": 1}
        ex = an.exitos(av, list(self.REF), self.REF)
        self.assertEqual(an.kn(ex["estafas"]), (4, 4))
        self.assertEqual(an.kn(ex["antes del pedido"]), (1, 3))   # T_A < T_R
        self.assertEqual(an.kn(ex["a tiempo"]), (2, 3))           # T_A ≤ T_R
        self.assertEqual(an.kn(ex["antes del cumplimiento"]), (2, 2))  # T_A < T_C, solo con T_C
        self.assertEqual(an.kn(ex["FA"]), (2, 3))
        self.assertEqual(an.kn(ex["FA cotidiana"]), (0, 1))
        self.assertEqual(an.kn(ex["FA pedido_razonable"]), (1, 1))
        self.assertEqual(an.kn(ex["FA sin tipo"]), (1, 1))

    def test_wilson_numerico_coincide_con_el_de_la_etapa_3(self):
        for k, n in ((29, 36), (40, 46), (26, 94), (0, 14), (14, 14)):
            lo, hi = an.limites(k, n)
            self.assertIn(f"[{100 * lo:.0f}–{100 * hi:.0f}]", an.wilson(k, n))
        self.assertEqual(an.limites(0, 0), (None, None))

    def test_mcnemar_con_los_pares_discordantes(self):
        a = {i: True for i in range(10)}
        b = {i: i >= 7 for i in range(10)}
        self.assertEqual(an.discordantes(a, b)[:2], (7, 0))
        self.assertAlmostEqual(an.discordantes(a, b)[2], 2 / 2 ** 7)
        self.assertEqual(an.discordantes(a, a)[2], 1.0)


class TestAnalisis(_ConServidor):
    def test_informe_entero_con_la_anotacion_alternativa(self):
        datos = self.tmp / "datos"
        for carpeta in DETECTORES:
            self.correr(carpeta)
        shutil.copytree(self.conj.carpeta, datos / "conjuntos" / "test_reservado")
        anotacion = self.tmp / "anotacion.json"
        anotacion.write_text(json.dumps({"_meta": {"motivo": "prueba"}, "casos": {
            "ENT-T-SINT-002": {"tipo_legitima": "cotidiana"}, "ENT-T-SINT-003": {"vista": "excluida"}}}), encoding="utf-8")
        salida = io.StringIO()
        with redirect_stdout(salida):
            an.main(["--datos", str(datos), "--anotacion-legitimas", str(anotacion), "--motivos"])
        texto = salida.getvalue()
        self.assertIn("## Test reservado", texto)
        self.assertIn("| test_reservado | config |", texto)
        self.assertNotIn("falta", texto.split("## Test reservado")[0].split("| test_reservado |", 1)[1].split("\n")[0])
        # La configuración: 3 de 4 estafas (SINT-003 no avisa), a tiempo 2/3, antes del cumplimiento 2/2, FA 1/3.
        fila = next(l for l in texto.splitlines() if l.startswith(f"| `{CONFIG}` |"))
        self.assertIn("3/4", fila)
        self.assertIn("2/3", fila)
        self.assertIn("1/3", fila)
        self.assertNotIn("## Criterios", texto)
        self.assertIn("## Con la anotación alternativa", texto)
        alternativa = texto.split("## Con la anotación alternativa")[1]
        fila_alt = next(l for l in alternativa.splitlines() if l.startswith(f"| `{CONFIG}` |"))
        self.assertIn("1/2", fila_alt, "ENT-T-SINT-003 sale de la vista: quedan 2 legítimas, 1 FA")
        for linea in sum((NUEVAS[i][2] for i in NUEVAS), []) + sum((ESTAFAS[i][3] for i in ESTAFAS), []):
            self.assertNotIn(linea.split(": ", 1)[1], texto, "el informe no muestra textos de los casos")

    def test_acepta_las_etiquetas_de_la_revision_de_producto_tal_cual(self):
        ruta = self.tmp / "etiquetas-producto.json"
        ruta.write_text(json.dumps({"_meta": {}, "casos": {
            "ENT-T-SINT-001": {"etiqueta": "no_avisar", "intencion": "informar", "pide": []},
            "ENT-T-SINT-002": {"etiqueta": "tolerable", "intencion": "verificar", "pide": ["dni"]},
            "ENT-T-SINT-003": {"etiqueta": "avisar", "intencion": "x", "pide": []}}}), encoding="utf-8")
        cambios = an.leer_anotacion(ruta, {"test_reservado": self.conj})["test_reservado"]
        self.assertEqual(cambios, {"ENT-T-SINT-002": {"vista": an.ETIQUETAS_PRODUCTO["tolerable"]},
                                   "ENT-T-SINT-003": {"vista": an.ETIQUETAS_PRODUCTO["avisar"]}})
        ref = an.aplicar(self.conj.referencia(), cambios)
        principal = [i for i in self.conj.ids if ref[i]["vista"] == conjuntos.PRINCIPAL]
        self.assertEqual([i for i in principal if ref[i]["clase"] == "legitima"], ["ENT-T-SINT-001"], "FA: solo «no avisar»")
        ruta.write_text(json.dumps({"casos": {"ENT-T-SINT-001": {"etiqueta": "quizas"}}}), encoding="utf-8")
        with self.assertRaises(ValueError):
            an.leer_anotacion(ruta, {"test_reservado": self.conj})

    def test_anotacion_invalida(self):
        conjs = {"test_reservado": self.conj}
        for casos_ in ({"NO-EXISTE": {"tipo_legitima": "cotidiana"}}, {"ENT-T-SINT-001": {"texto": "x"}},
                       {"ENT-T-SINT-001": {"t_r_linea": 1}}, {"ENT-T-SINT-001": {"tipo_legitima": "otra"}}):
            ruta = self.tmp / "a.json"
            ruta.write_text(json.dumps({"casos": casos_}), encoding="utf-8")
            with self.subTest(casos_), self.assertRaises(ValueError):
                an.leer_anotacion(ruta, conjs)


def escribir_corrida_config(destino: Path, conj, avisa: dict, config=CONFIG) -> None:
    """Una corrida de la configuración sobre un conjunto, como la registraría correr.py (solo OTRA, operativo)."""
    run = destino / "desarrollo" / "config" / "2026-11-12_000000_sintetica"
    run.mkdir(parents=True)
    clave = f"slm|{an.e3.MODELO}|{config}|rol"
    man = {"codigo": dict(LIMPIO), "modo_termino": "operativo-hasta-aviso", "interrumpida": False, "fin": "x",
           "particion": conj.particion, "solo_otra": True,
           "conjunto": {"nombre": conj.nombre, "conjunto_sha256": conjuntos.sha256((conj.carpeta / "conjunto.json").read_bytes())},
           "configs": [{"config": clave, "detector": "slm", "modelo": an.e3.MODELO, "prompt": config, "hablantes": "rol"}],
           "ollama": {"version": an.e3.OLLAMA, "digests": {an.e3.MODELO: "sha256:" + an.e3.DIGEST}},
           "parametros_slm": {"num_ctx": 4096, "seed": 42, "temperatura": 0.0,
                              "corte_riesgo": {"num_predict": MAXIMO_TOKENS_CORTE_RIESGO}},
           "prompts": {config: {"texto": cargar_prompt(config), "esquema": esquema_de(config),
                                "etapa2": {"texto": cargar_prompt_motivo(PROMPT_MOTIVO_C), "esquema": ESQUEMA_MOTIVO}}},
           "casos": {i: huella(conj.crudo(i)) for i in conj.ids}}
    (run / "manifiesto.json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
    with (run / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS, extrasaction="ignore")
        w.writeheader()
        for i in conj.ids:
            for n, linea in enumerate(conj.con_roles(i, conj.cargar_texto(i)), start=1):
                otra, aviso = linea.hablante == "OTRA", n == avisa.get(i)
                w.writerow({"config": clave, "detector": "slm", "prompt": config, "hablantes": "rol", "case_id": i,
                            "linea": n, "hablante": linea.hablante, "valida": "true", "consulta": "" if otra else "omitida",
                            "riesgo": (0.3 if aviso else 0.1) if otra else "", "alerta_sugerida": str(aviso).lower(),
                            "aviso": str(aviso).lower(), "ms_etapa1": 240 if otra else "", "ms_etapa2": 800 if aviso else ""})
                if aviso:
                    break


class TestControlDesarrollo(unittest.TestCase):
    """El control del Colab antes del test: la configuración reproduce sus cifras de desarrollo (±2)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.conj = conjuntos.preparar_desarrollo(cls.tmp / "conjuntos")
        # Los avisos de c-premisa en la prueba de sensibilidad (2026-11-10), leídos de su corrida.
        filas, _ = an.e3.leer(RAIZ / "corridas/2026-11-10_sensibilidad-c", "c-premisa")
        cls.avisa = an.avisos_config(filas, cls.conj.ids)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def control(self, avisa, config=CONFIG):
        datos = Path(tempfile.mkdtemp(dir=self.tmp))
        escribir_corrida_config(datos, self.conj, avisa, config)
        return an.control_desarrollo(datos, self.conj, config)

    def test_la_corrida_de_la_sensibilidad_reproduce_sus_cifras(self):
        ok, texto = self.control(self.avisa)
        self.assertTrue(ok, texto)
        self.assertIn("estafas 40 (antes 40)", texto)
        self.assertIn("FA 26 (antes 26)", texto)

    def test_tres_estafas_menos_no_reproduce(self):
        ref = self.conj.referencia()
        perdidas = [i for i in self.conj.ids if ref[i]["vista"] == "principal" and ref[i]["clase"] == "vishing"
                    and self.avisa[i] is not None][:3]
        ok, texto = self.control({**self.avisa, **dict.fromkeys(perdidas)})
        self.assertFalse(ok)
        self.assertIn("no reproduce", texto)

    def test_una_configuracion_sin_cifras_de_desarrollo_no_corre_el_test(self):
        ok, texto = self.control(self.avisa, config="c-ancla-corte-riesgo")
        self.assertFalse(ok)
        self.assertIn("CIFRAS_DESARROLLO", texto)


class TestColab(unittest.TestCase):
    def test_el_notebook_y_el_script(self):
        nb = json.loads((RAIZ / "colab/COLAB-EVALUACION-FINAL.ipynb").read_text(encoding="utf-8"))
        codigo = "".join(nb["cells"][1]["source"])
        self.assertIn("TAG = 'colab/143-evaluacion-final'", codigo)
        self.assertIn(f"CONFIG = '{CONFIG}'", codigo)
        self.assertIn("probar_evaluacion_final.py", codigo)
        script = (RAIZ / "colab/probar_evaluacion_final.py").read_text(encoding="utf-8")
        self.assertIn(f"os.environ.get('COLAB_CONFIG', '{CONFIG}')", script)
        humo = ["CV2-D-V-ORGANISMO_PREVISIONAL-004", "CV2-D-L-BANCO-001", "SC-WA-CODE-01-e01"]
        self.assertTrue(all(c in casos.ids_de_casos(particion="desarrollo") for c in humo))
        self.assertEqual(sum(len(casos.cargar_texto(c)) for c in humo), 48)
        self.assertIn(CONFIG, an.CIFRAS_DESARROLLO)


if __name__ == "__main__":
    unittest.main()
