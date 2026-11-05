"""Módulo de historial: carpetas de salida armadas a mano en un directorio temporal."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

DIR_VOIP = Path(__file__).resolve().parent.parent
if str(DIR_VOIP) not in sys.path:
    sys.path.insert(0, str(DIR_VOIP))

import historial


def carpeta(salida: Path, nombre: str, manifiesto: dict | None):
    d = salida / nombre
    d.mkdir()
    (d / "estereo.wav").write_bytes(b"RIFF")
    if manifiesto is not None:
        (d / "manifiesto.json").write_text(json.dumps(manifiesto), encoding="utf-8")
    return d


class TestDescartarPruebasNoGuardadas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.salida = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_borra_solo_pruebas_con_guardada_falsa(self):
        no_guardada = carpeta(self.salida, "2026-10-26_100000-000001",
                              {"inicio_panel": {"modo": "asr"}, "guardada": False})
        guardada = carpeta(self.salida, "2026-10-26_100000-000002",
                           {"inicio_panel": {"modo": "asr"}, "guardada": True, "referencia": "hola"})
        antigua = carpeta(self.salida, "2026-10-26_100000-000003", {"inicio_panel": {"modo": "asr"}})
        llamada = carpeta(self.salida, "2026-10-26_100000-000004", {"inicio_panel": {"modo": "llamada"}})
        sin_manifiesto = carpeta(self.salida, "2026-10-26_100000-000005", None)
        roto = carpeta(self.salida, "2026-10-26_100000-000006", None)
        (roto / "manifiesto.json").write_text("{", encoding="utf-8")
        ajena = self.salida / "otra-cosa"
        ajena.mkdir()
        (ajena / "manifiesto.json").write_text(json.dumps({"inicio_panel": {"modo": "asr"}, "guardada": False}))
        archivo = self.salida / "2026-10-26_100000-000007"
        archivo.write_text("no es carpeta")

        borradas = historial.descartar_pruebas_no_guardadas(self.salida)

        self.assertEqual(borradas, [no_guardada.name])
        self.assertFalse(no_guardada.exists())
        for d in (guardada, antigua, llamada, sin_manifiesto, roto, ajena):
            self.assertTrue(d.exists(), d.name)
        self.assertTrue(archivo.exists())

    def test_excepcion_para_la_carpeta_en_curso(self):
        d = carpeta(self.salida, "2026-10-26_100000-000001",
                    {"inicio_panel": {"modo": "asr"}, "guardada": False})
        self.assertEqual(historial.descartar_pruebas_no_guardadas(self.salida, conservar=d), [])
        self.assertTrue(d.exists())

    def test_salida_inexistente_no_rompe(self):
        self.assertEqual(historial.descartar_pruebas_no_guardadas(self.salida / "no-existe"), [])


def jsonl(carpeta: Path, nombre: str, lineas: list[dict]):
    (carpeta / nombre).write_text("\n".join(json.dumps(l, ensure_ascii=False) for l in lineas) + "\n", encoding="utf-8")


def final(n, rol, segmento, texto, fin, disp=None):
    return {"n": n, "tipo": "final", "segmento": segmento, "texto": texto, "inicio_audio_s": fin - 1,
            "fin_audio_s": fin, "disponible_s": disp or fin + 0.1, "canal": rol, "fin_voz_s": fin - 0.2}


def llamada_completa(salida: Path, nombre="2026-10-26_202337-443368", corte="auto"):
    d = carpeta(salida, nombre, {
        "llamada_id": "VIVO-20261026-202337-443368",
        "canales": {"protegida": {"inicio_s": 0.0, "duracion_s": 25.2}, "otra": {"inicio_s": 0.0, "duracion_s": 25.3}},
        "config": {"detector": "slm", "modelo": "qwen3.5:0.8b-q8_0", "corte_silencio_s": corte,
                   "endpoint_nativo": corte == "auto", "umbral_rms_silencio": 0.005},
        "inicio_panel": {"tipo": "iniciar", "modo": "llamada", "corte_silencio_s": corte, "umbral_rms_silencio": None,
                         "fuentes": {"otra": {"tipo": "ejemplo", "escenario": "SC-WA-CODE-01", "canal": "izq"},
                                     "protegida": {"tipo": "ejemplo", "escenario": "SC-WA-CODE-01", "canal": "der"}}},
        "detector": {"aviso": {"t_a": 18.4, "motivo": "Pedido de código", "evidencia": ". decime el código"}},
    })
    jsonl(d, "actualizaciones.jsonl", [
        {"meta": {"modo": "en_vivo"}},
        {"n": 1, "tipo": "parcial", "segmento": 1, "texto": "te llamo", "inicio_audio_s": 0, "fin_audio_s": 1.0,
         "disponible_s": 1.1, "canal": "otra"},
        final(2, "otra", 1, "Te llamo de soporte.", 4.3),
        final(3, "protegida", 2, "No pedí nada.", 8.7),
        final(4, "otra", 3, ". decime el código de activación", 18.4, 18.5),
        final(5, "protegida", 4, "Ahora no puedo.", 22.0),
    ])
    jsonl(d, "detector.jsonl", [
        {"n": 2, "valida": True, "riesgo": 0.0, "alerta_sugerida": False, "aviso": False, "motivo": "saludo",
         "evidencia": "", "fin_eval_s": 4.5, "t_a": None},
        {"n": 4, "valida": True, "riesgo": 1.0, "alerta_sugerida": True, "aviso": True,
         "motivo": "Pedido de código", "evidencia": ". decime el código", "fin_eval_s": 18.4, "t_a": 18.4},
        {"n": 5, "valida": False, "riesgo": None, "alerta_sugerida": False, "aviso": False, "motivo": "",
         "evidencia": "", "fin_eval_s": 22.5, "t_a": None, "error": "timeout"},
    ])
    return d


def prueba_guardada(salida: Path, nombre="2026-10-26_210000-000001", referencia="hola mundo", corte=1.2):
    d = carpeta(salida, nombre, {
        "llamada_id": "VIVO-prueba",
        "canales": {"protegida": {"inicio_s": 0.0, "duracion_s": 6.0}},
        "config": {"detector": None, "modelo": None, "corte_silencio_s": corte, "endpoint_nativo": False,
                   "umbral_rms_silencio": 0.02},
        "inicio_panel": {"tipo": "iniciar", "modo": "asr", "fuentes": {"protegida": {"tipo": "navegador"}},
                         "corte_silencio_s": corte, "umbral_rms_silencio": 0.02},
        "detector": {"evaluaciones": 0, "aviso": None},
        "guardada": True, "referencia": referencia,
    })
    jsonl(d, "actualizaciones.jsonl", [{"meta": {}}, final(1, "protegida", 1, "Hola mundo.", 3.0)])
    jsonl(d, "detector.jsonl", [])
    return d


class TestListar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.salida = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_separa_llamadas_de_pruebas_guardadas_y_ordena_de_nueva_a_vieja(self):
        llamada_completa(self.salida, "2026-10-26_100000-000001")
        llamada_completa(self.salida, "2026-10-27_100000-000001")
        prueba_guardada(self.salida, "2026-10-26_110000-000001")
        carpeta(self.salida, "2026-10-26_120000-000001", {"inicio_panel": {"modo": "asr"}, "guardada": False})
        carpeta(self.salida, "2026-10-26_130000-000001", {"inicio_panel": {"modo": "asr"}})  # anterior a la marca
        lista = historial.listar(self.salida)
        self.assertEqual([i["id"] for i in lista["llamadas"]], ["2026-10-27_100000-000001", "2026-10-26_100000-000001"])
        self.assertEqual([i["id"] for i in lista["pruebas"]], ["2026-10-26_110000-000001"])

    def test_campos_de_una_llamada(self):
        llamada_completa(self.salida)
        item = historial.listar(self.salida)["llamadas"][0]
        self.assertEqual(item["id"], "2026-10-26_202337-443368")
        self.assertEqual(item["fecha"], "2026-10-26T20:23:37")
        self.assertEqual(item["tipo"], "llamada")
        self.assertEqual(item["fuente"], "Ejemplo SC-WA-CODE-01")
        self.assertEqual(item["duracion_s"], 25.3)
        self.assertEqual(item["detector"], "slm")
        self.assertEqual(item["modelo"], "qwen3.5:0.8b-q8_0")
        self.assertEqual(item["corte_silencio_s"], "auto")
        self.assertEqual(item["riesgo_maximo"], 1.0)
        self.assertIs(item["aviso"], True)
        self.assertEqual(item["aviso_s"], 18.4)
        self.assertIs(item["incompleta"], False)

    def test_campos_de_una_prueba(self):
        prueba_guardada(self.salida)
        item = historial.listar(self.salida)["pruebas"][0]
        self.assertEqual(item["tipo"], "prueba")
        self.assertEqual(item["fuente"], "Micrófono")
        self.assertEqual(item["corte_silencio_s"], 1.2)
        self.assertEqual(item["umbral_rms_silencio"], 0.02)
        self.assertEqual(item["referencia"], "hola mundo")
        self.assertIsNone(item["detector"])
        self.assertIsNone(item["riesgo_maximo"])
        self.assertIs(item["aviso"], False)

    def test_llamadas_anteriores_a_esta_funcion_tambien_aparecen(self):
        # Sin `origen` en las fuentes, corte 0,8 con endpoint nativo (el «automático» de antes) y sin detector.jsonl.
        d = carpeta(self.salida, "2026-10-25_090000-000001", {
            "canales": {"protegida": {"inicio_s": 0.0, "duracion_s": 10.0}, "otra": {"inicio_s": 0.12, "duracion_s": 9.9}},
            "config": {"detector": "reglas", "modelo": None, "corte_silencio_s": 0.8, "endpoint_nativo": True},
            "inicio_panel": {"modo": "llamada", "fuentes": {"otra": {"tipo": "navegador"}, "protegida": {"tipo": "navegador"}}},
            "detector": {"aviso": None}})
        item = historial.listar(self.salida)["llamadas"][0]
        self.assertEqual(item["corte_silencio_s"], "auto")
        self.assertEqual(item["fuente"], "Navegador")
        self.assertEqual(item["duracion_s"], 10.02)
        self.assertIsNone(item["riesgo_maximo"])
        self.assertIs(item["aviso"], False)

    def test_origen_de_la_otra_persona_y_cliente(self):
        for i, (otra, esperado) in enumerate((({"tipo": "navegador", "origen": "meet"}, "Meet"),
                                              ({"tipo": "navegador", "origen": "blackhole"}, "WhatsApp / BlackHole"),
                                              ({"tipo": "cliente"}, "Segunda notebook · cliente.py"))):
            carpeta(self.salida, f"2026-10-26_10000{i}-000001", {
                "config": {"corte_silencio_s": 0.8, "endpoint_nativo": True},
                "inicio_panel": {"modo": "llamada", "fuentes": {"otra": otra, "protegida": {"tipo": "navegador"}}}})
        fuentes = {i["id"]: i["fuente"] for i in historial.listar(self.salida)["llamadas"]}
        self.assertEqual(fuentes["2026-10-26_100000-000001"], "Meet")
        self.assertEqual(fuentes["2026-10-26_100001-000001"], "WhatsApp / BlackHole")
        self.assertEqual(fuentes["2026-10-26_100002-000001"], "Segunda notebook · cliente.py")

    def test_llamada_abierta_por_cliente_sin_inicio_panel(self):
        carpeta(self.salida, "2026-10-26_100000-000001", {"inicio_panel": {}, "config": {"corte_silencio_s": 0.8, "endpoint_nativo": True}})
        self.assertEqual(historial.listar(self.salida)["llamadas"][0]["fuente"], "Segunda notebook · cliente.py")

    def test_carpeta_sin_manifiesto_se_marca_incompleta_o_se_omite(self):
        cortada = carpeta(self.salida, "2026-10-26_100000-000001", None)
        jsonl(cortada, "actualizaciones.jsonl", [{"meta": {}}, final(1, "otra", 1, "Hola.", 2.0)])
        vacia = carpeta(self.salida, "2026-10-26_100001-000001", None)
        (vacia / "actualizaciones.jsonl").write_text("")
        carpeta(self.salida, "2026-10-26_100002-000001", None)
        rota = carpeta(self.salida, "2026-10-26_100003-000001", None)
        (rota / "manifiesto.json").write_text("{")
        (rota / "actualizaciones.jsonl").write_text("{basura\n")
        lista = historial.listar(self.salida)
        self.assertEqual([i["id"] for i in lista["llamadas"]], ["2026-10-26_100000-000001"])
        item = lista["llamadas"][0]
        self.assertIs(item["incompleta"], True)
        self.assertEqual(item["duracion_s"], 2.0)
        self.assertEqual(lista["pruebas"], [])

    def test_carpeta_en_curso_se_excluye(self):
        d = llamada_completa(self.salida)
        self.assertEqual(historial.listar(self.salida, excluir=d)["llamadas"], [])

    def test_salida_inexistente(self):
        self.assertEqual(historial.listar(self.salida / "nada"), {"llamadas": [], "pruebas": []})


class TestDetalle(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.salida = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_conversacion_por_rol_con_los_finales_y_el_aviso_ubicado(self):
        llamada_completa(self.salida)
        d = historial.detalle(self.salida, "2026-10-26_202337-443368")
        self.assertEqual([(l["rol"], l["texto"]) for l in d["conversacion"]], [
            ("otra", "Te llamo de soporte."), ("protegida", "No pedí nada."),
            ("otra", ". decime el código de activación"), ("protegida", "Ahora no puedo.")])
        self.assertEqual(d["conversacion"][2]["fin_audio_s"], 18.4)
        self.assertEqual([l["aviso"] for l in d["conversacion"]], [False, False, True, False])
        self.assertEqual(d["aviso"], {"t_a": 18.4, "motivo": "Pedido de código", "evidencia": ". decime el código", "riesgo": 1.0})
        self.assertEqual(d["item"]["id"], "2026-10-26_202337-443368")
        self.assertEqual(d["item"]["riesgo_maximo"], 1.0)

    def test_prueba_con_referencia_y_sin_aviso(self):
        prueba_guardada(self.salida)
        d = historial.detalle(self.salida, "2026-10-26_210000-000001")
        self.assertEqual(d["item"]["referencia"], "hola mundo")
        self.assertIsNone(d["aviso"])
        self.assertEqual([l["texto"] for l in d["conversacion"]], ["Hola mundo."])

    def test_segmento_sin_final_en_carpeta_incompleta_muestra_su_ultimo_provisorio(self):
        d = carpeta(self.salida, "2026-10-26_100000-000001", None)
        jsonl(d, "actualizaciones.jsonl", [{"meta": {}}, final(1, "otra", 1, "Hola.", 2.0),
               {"n": 2, "tipo": "parcial", "segmento": 2, "texto": "como", "fin_audio_s": 2.5, "disponible_s": 2.6, "canal": "otra"},
               {"n": 3, "tipo": "parcial", "segmento": 2, "texto": "como estas", "fin_audio_s": 3.0, "disponible_s": 3.1, "canal": "otra"}])
        det = historial.detalle(self.salida, "2026-10-26_100000-000001")
        self.assertEqual([(l["texto"], l["provisorio"]) for l in det["conversacion"]], [("Hola.", False), ("como estas", True)])

    def test_lineas_ilegibles_se_saltean(self):
        d = llamada_completa(self.salida)
        with open(d / "actualizaciones.jsonl", "a") as f:
            f.write("{no es json\n")
        self.assertEqual(len(historial.detalle(self.salida, d.name)["conversacion"]), 4)

    def test_ids_invalidos(self):
        llamada_completa(self.salida)
        (self.salida.parent / "2026-10-26_202337-443368").mkdir(exist_ok=True)
        try:
            for malo in ("../" + self.salida.name, "..", ".", "", "otra-cosa", "2026-10-26_202337-443368/..",
                         "2026-10-26_202337-443368/", "/etc", "2026-10-26_999999-443368", None, 5, ["x"],
                         "2026-10-26_202337-000000"):
                with self.assertRaises(ValueError, msg=repr(malo)):
                    historial.detalle(self.salida, malo)
        finally:
            (self.salida.parent / "2026-10-26_202337-443368").rmdir()

    def test_id_que_es_un_enlace_simbolico_se_rechaza(self):
        afuera = Path(tempfile.mkdtemp())
        try:
            (self.salida / "2026-10-26_202337-443368").symlink_to(afuera, target_is_directory=True)
            with self.assertRaises(ValueError):
                historial.detalle(self.salida, "2026-10-26_202337-443368")
        finally:
            afuera.rmdir()


class TestReferencia(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.salida = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_editar_referencia_se_persiste(self):
        d = prueba_guardada(self.salida)
        item = historial.editar_referencia(self.salida, d.name, "  otra frase  ")
        self.assertEqual(item["referencia"], "otra frase")
        self.assertEqual(json.loads((d / "manifiesto.json").read_text())["referencia"], "otra frase")
        self.assertEqual(historial.listar(self.salida)["pruebas"][0]["referencia"], "otra frase")

    def test_solo_pruebas_guardadas_y_texto_valido(self):
        llamada = llamada_completa(self.salida)
        no_guardada = carpeta(self.salida, "2026-10-26_120000-000001", {"inicio_panel": {"modo": "asr"}, "guardada": False})
        guardada = prueba_guardada(self.salida)
        for id_ in (llamada.name, no_guardada.name):
            with self.assertRaises(ValueError):
                historial.editar_referencia(self.salida, id_, "x")
        for malo in (5, None, ["a"], "x" * 2001):
            with self.assertRaises(ValueError):
                historial.editar_referencia(self.salida, guardada.name, malo)
        self.assertEqual(json.loads((guardada / "manifiesto.json").read_text())["referencia"], "hola mundo")


class TestBorrar(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.salida = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_borra_la_carpeta_entera_con_su_audio(self):
        a = llamada_completa(self.salida, "2026-10-26_100000-000001")
        b = llamada_completa(self.salida, "2026-10-26_100001-000001")
        self.assertEqual(historial.borrar(self.salida, [a.name]), [a.name])
        self.assertFalse(a.exists())
        self.assertTrue((b / "estereo.wav").exists())

    def test_borra_varios_y_ignora_repetidos(self):
        a = llamada_completa(self.salida, "2026-10-26_100000-000001")
        b = prueba_guardada(self.salida, "2026-10-26_100001-000001")
        c = llamada_completa(self.salida, "2026-10-26_100002-000001")
        self.assertEqual(historial.borrar(self.salida, [a.name, b.name, a.name]), [a.name, b.name])
        self.assertFalse(a.exists() or b.exists())
        self.assertTrue(c.exists())

    def test_un_id_invalido_no_borra_nada(self):
        a = llamada_completa(self.salida)
        for malo in ([a.name, "../x"], [a.name, "2026-10-26_000000-000000"], [a.name, 5], [], "2026-10-26_202337-443368", None):
            with self.assertRaises(ValueError, msg=repr(malo)):
                historial.borrar(self.salida, malo)
            self.assertTrue(a.exists())

    def test_no_borra_la_carpeta_en_curso(self):
        a = llamada_completa(self.salida)
        with self.assertRaises(ValueError):
            historial.borrar(self.salida, [a.name], excluir=a)
        self.assertTrue(a.exists())

    def test_borrar_pruebas_toca_solo_las_guardadas(self):
        guardada1 = prueba_guardada(self.salida, "2026-10-26_100000-000001")
        guardada2 = prueba_guardada(self.salida, "2026-10-26_100001-000001")
        llamada = llamada_completa(self.salida, "2026-10-26_100002-000001")
        sin_guardar = carpeta(self.salida, "2026-10-26_100003-000001", {"inicio_panel": {"modo": "asr"}, "guardada": False})
        antigua = carpeta(self.salida, "2026-10-26_100004-000001", {"inicio_panel": {"modo": "asr"}})
        borradas = historial.borrar_pruebas_guardadas(self.salida)
        self.assertEqual(sorted(borradas), [guardada1.name, guardada2.name])
        self.assertFalse(guardada1.exists() or guardada2.exists())
        for d in (llamada, sin_guardar, antigua):
            self.assertTrue(d.exists())
