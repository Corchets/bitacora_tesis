"""Pruebas de medir_voz_real.py y variantes_voz_real.py sin modelos ni descargas.

Los motores se reemplazan por MotorFalso o por un ejecutor falso que devuelve textos armados a mano;
todo lo demás (CSV, pruebas guardadas, alineado, etiquetas, regla, salida) corre de verdad.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

import guion as G
import medir_voz_real as R
import variantes_voz_real as V
from motores import MotorFalso

GUION = G.cargar_guion()


def referencia_del_bloque(n: int) -> str:
    return "\n".join(f.texto for f in GUION.bloques()[n])


def escribir_prueba(carpeta: Path, id_: str, referencia: str | None, guardada: bool | None = True,
                    con_wav: bool = True, canales: dict | None = None) -> Path:
    destino = carpeta / id_
    destino.mkdir(parents=True)
    manifiesto: dict = {"llamada_id": "VIVO-test", "inicio_panel": {"modo": "asr"},
                        "canales": canales if canales is not None else {"protegida": {"inicio_s": 0.0, "duracion_s": 2.0}}}
    if guardada is not None:
        manifiesto["guardada"] = guardada
    if referencia is not None:
        manifiesto["referencia"] = referencia
    (destino / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False), encoding="utf-8")
    if con_wav:
        import soundfile as sf

        sf.write(destino / "estereo.wav", np.zeros((32000, 2), dtype=np.int16), 16000, subtype="PCM_16")
    return destino


class TestCSV(unittest.TestCase):
    def leer(self, contenido: str):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "pruebas.csv"
            ruta.write_text(contenido, encoding="utf-8")
            return R.leer_csv(ruta)

    def test_lee_filas_ignorando_comentarios_y_vacias(self):
        filas = self.leer("# nota\nid,toma,voz,condicion,canal,nota\n\n# comentada,1,luciano,meet,,\nA,1,luciano,microfono,,hola\nB,2,otra,meet,otra,\n")
        self.assertEqual([f["id"] for f in filas], ["A", "B"])
        self.assertEqual(filas[1]["canal"], "otra")

    def test_el_csv_del_repo_es_valido(self):
        self.assertIsInstance(R.leer_csv(R.CSV_POR_DEFECTO), list)

    def test_bloque_opcional_de_1_a_6(self):
        filas = self.leer("id,toma,voz,condicion,bloque\nA,1,luciano,voz-baja,3\nB,1,luciano,microfono,\n")
        self.assertEqual([f["bloque"] for f in filas], ["3", ""])
        with self.assertRaises(ValueError) as ctx:
            self.leer("id,toma,voz,condicion,bloque\nA,1,luciano,microfono,7\n")
        self.assertIn("bloque", str(ctx.exception))

    def test_errores_dicen_la_fila(self):
        for contenido, texto in [
            ("id,toma,voz,condicion\nA,5,luciano,meet\n", "toma debe ser una de 1, 2, 3, 4"),
            ("id,toma,voz,condicion\nA,1,pepe,meet\n", "voz debe ser"),
            ("id,toma,voz,condicion\nA,1,luciano,zoom\n", "condicion debe ser"),
            ("id,toma,voz,condicion,canal\nA,1,luciano,meet,C\n", "canal debe ser"),
            ("id,toma,voz,condicion\nA,1,luciano,meet\nA,2,luciano,meet\n", "repetido"),
        ]:
            with self.assertRaises(ValueError) as ctx:
                self.leer(contenido)
            self.assertIn(texto, str(ctx.exception))

    def test_faltan_columnas(self):
        with self.assertRaises(ValueError):
            self.leer("id,toma\nA,1\n")


class TestElegirCanal(unittest.TestCase):
    def test_el_csv_manda(self):
        self.assertEqual(R.elegir_canal({"canales": {"protegida": {}}}, "otra"), ("otra", 1))

    def test_segun_el_manifiesto(self):
        self.assertEqual(R.elegir_canal({"canales": {"protegida": {}}}), ("protegida", 0))
        self.assertEqual(R.elegir_canal({"canales": {"otra": {}}}), ("otra", 1))
        self.assertEqual(R.elegir_canal({"canales": {"protegida": {}, "otra": {}}}), ("protegida", 0))

    def test_sin_datos_es_protegida(self):
        self.assertEqual(R.elegir_canal({}), ("protegida", 0))


class TestCargarPruebas(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def fila(self, id_, toma="2", voz="luciano", condicion="microfono", canal="", bloque=""):
        return {"id": id_, "toma": toma, "voz": voz, "condicion": condicion, "canal": canal, "nota": "", "bloque": bloque}

    def test_sin_referencia_usa_el_bloque_del_csv(self):
        carpeta = escribir_prueba(self.dir, "p", "")
        archivo = carpeta / "manifiesto.json"
        m = json.loads(archivo.read_text())
        m["referencias_por_segmento"] = {"1": "", "2": ""}  # guardada sin tocar «Lo que dije en realidad»
        archivo.write_text(json.dumps(m))
        pruebas, omitidas = R.cargar_pruebas([self.fila("p", bloque="4")], self.dir, GUION)
        self.assertEqual(omitidas, [])
        self.assertEqual(pruebas[0]["referencia"], referencia_del_bloque(4))
        self.assertEqual((pruebas[0]["referencia_de"], pruebas[0]["bloque"]["bloque"]), ("guion", 4))

    def test_la_referencia_escrita_manda_sobre_el_bloque(self):
        escribir_prueba(self.dir, "p", referencia_del_bloque(1))
        pruebas, _ = R.cargar_pruebas([self.fila("p", bloque="4")], self.dir, GUION)
        self.assertEqual((pruebas[0]["referencia_de"], pruebas[0]["bloque"]["bloque"]), ("manifiesto", 1))

    def test_toma_solo_las_guardadas_con_referencia(self):
        escribir_prueba(self.dir, "ok", referencia_del_bloque(1))
        escribir_prueba(self.dir, "sin-guardar", referencia_del_bloque(1), guardada=False)
        escribir_prueba(self.dir, "vieja", referencia_del_bloque(1), guardada=None)
        escribir_prueba(self.dir, "sin-ref", "   ")
        escribir_prueba(self.dir, "sin-wav", referencia_del_bloque(1), con_wav=False)
        filas = [self.fila(i) for i in ("ok", "sin-guardar", "vieja", "sin-ref", "sin-wav", "no-existe")]
        pruebas, omitidas = R.cargar_pruebas(filas, self.dir, GUION)
        self.assertEqual([p["id"] for p in pruebas], ["ok"])
        self.assertEqual({o["id"] for o in omitidas}, {"sin-guardar", "vieja", "sin-ref", "sin-wav", "no-existe"})

    def test_identifica_el_bloque_y_los_tipos_por_frase(self):
        escribir_prueba(self.dir, "p", referencia_del_bloque(4))
        pruebas, _ = R.cargar_pruebas([self.fila("p")], self.dir, GUION)
        p = pruebas[0]
        self.assertEqual(p["bloque"]["bloque"], 4)
        self.assertTrue(p["bloque"]["exacto"])
        self.assertEqual(p["tipos"], ["negativa", "critica", "bancos", "numeros", "critica"])
        self.assertEqual(len(p["lineas"]), 5)
        self.assertEqual(p["grupo"], "luciano-microfono")

    def test_omite_referencias_por_frase_incompletas(self):
        carpeta = escribir_prueba(self.dir, "p", referencia_del_bloque(1))
        archivo = carpeta / "manifiesto.json"
        m = json.loads(archivo.read_text())
        m["referencias_por_segmento"] = {"1": "una frase corregida", "2": ""}
        archivo.write_text(json.dumps(m))
        pruebas, omitidas = R.cargar_pruebas([self.fila("p")], self.dir, GUION)
        self.assertEqual(pruebas, [])
        self.assertIn("alguna frase", omitidas[0]["motivo"])
        m["referencias_por_segmento"]["2"] = "otra frase corregida"
        archivo.write_text(json.dumps(m))
        pruebas, omitidas = R.cargar_pruebas([self.fila("p")], self.dir, GUION)
        self.assertEqual(len(pruebas), 1)
        self.assertEqual(omitidas, [])

    def test_el_canal_sale_del_manifiesto_o_del_csv(self):
        escribir_prueba(self.dir, "a", referencia_del_bloque(1), canales={"otra": {"inicio_s": 0.0, "duracion_s": 2.0}})
        escribir_prueba(self.dir, "b", referencia_del_bloque(1))
        pruebas, _ = R.cargar_pruebas([self.fila("a"), self.fila("b", canal="otra")], self.dir, GUION)
        self.assertEqual([(p["canal"], p["columna"]) for p in pruebas], [("otra", 1), ("otra", 1)])


class TestSeleccionDeVariantes(unittest.TestCase):
    def test_sin_opciones_son_todas(self):
        self.assertIsNone(R.seleccion_de_variantes(None, False))

    def test_sin_whisper_las_saca(self):
        s = R.seleccion_de_variantes(None, True)
        self.assertIn("beam+hotwords", s)
        self.assertFalse(any(n.startswith("whisper") for n in s))

    def test_lista_y_nombre_desconocido(self):
        self.assertEqual(R.seleccion_de_variantes("beam, whisper-small", False), {"beam", "whisper-small"})
        with self.assertRaises(ValueError) as ctx:
            R.seleccion_de_variantes("beam,otra", False)
        self.assertIn("otra", str(ctx.exception))

    def test_el_catalogo_tiene_lo_que_pide_el_plan(self):
        nombres = V.nombres_de_variantes()
        for esperado in ("greedy", "corte-0.6", "rule2-0.5", "rms-0.01", "norm", "beam", "beam+hotwords", "+diccionario",
                         "whisper-small", "whisper-small+hotwords", "whisper-large-v3-turbo", "whisper-large-v3-turbo+hotwords"):
            self.assertIn(esperado, nombres)
        self.assertEqual(len(nombres), len(set(nombres)))

    def test_parakeet_arranca_por_la_del_panel(self):
        self.assertEqual(V.PARAKEET_PANEL, "parakeet-0.9-rms-0.003")
        self.assertIn("parakeet-0.5-rms-0.008", V.nombres_de_variantes())

    def test_silero_con_los_cortes_del_issue_y_el_fin_de_voz_de_la_referencia(self):
        configs = dict(V.VARIANTES_PARAKEET)
        self.assertIn(V.PARAKEET_LABORATORIO, configs)
        for corte in (0.8, 0.5, 0.3):
            c = configs[f"parakeet-{corte}-silero-0.5"]
            self.assertEqual((c.corte, c.vad, c.umbral_silero), (corte, "silero", 0.5))
            self.assertEqual(c.umbral_rms, configs[V.PARAKEET_LABORATORIO].umbral_rms)
        self.assertEqual(configs[V.PARAKEET_PANEL].vad, "rms")


class TestVariantes(unittest.TestCase):
    def test_los_candidatos_se_arman_sobre_lo_que_se_quedo(self):
        base = V.ConfigKroko()
        beam = V.aplicar(base, V.PASOS[5].candidatos[0])
        self.assertTrue(beam.beam)
        hot = V.aplicar(beam, V.PASOS[6].candidatos[0])
        self.assertTrue(hot.beam and hot.hotwords)
        self.assertEqual(hot.bpe_puntaje, "log")

    def test_rule2_no_aplica_con_corte_fijo(self):
        rule2 = V.PASOS[2].candidatos[0]
        self.assertIsNotNone(V.aplicar(V.ConfigKroko(), rule2))
        self.assertIsNone(V.aplicar(V.ConfigKroko(corte=0.6), rule2))

    def test_el_motor_de_la_linea_base_es_el_del_panel(self):
        motor = V.crear_motor_kroko(V.ConfigKroko(), {})
        self.assertEqual((motor.decoding_method, motor.enable_endpoint, motor.corte_silencio_s, motor.umbral_rms_silencio, motor.hilos),
                         ("greedy_search", True, 0.8, 0.005, 2))

    def test_parakeet_con_el_corte_y_el_umbral_de_la_variante(self):
        motor = V.crear_motor({"motor": "parakeet", "config": {"corte": 0.5, "umbral_rms": 0.008}})
        self.assertEqual((motor.nombre, motor.corte_silencio_s, motor.umbral_rms_silencio, motor.hilos, motor.parciales_cada_s),
                         ("sherpa-parakeet", 0.5, 0.008, 2, 0.5))
        self.assertEqual(Path(motor.modelo_id), V.DIR_MODELO_PARAKEET)
        self.assertIsNone(motor.detector_voz)

    def test_parakeet_con_silero_cambia_solo_quien_decide_la_voz(self):
        motor = V.crear_motor({"motor": "parakeet", "config": {"corte": 0.5, "umbral_rms": 0.008, "vad": "silero",
                                                                "umbral_silero": 0.4}})
        self.assertEqual((motor.corte_silencio_s, motor.parciales_cada_s, motor.filtrar_idioma), (0.5, 0.5, True))
        self.assertEqual((motor.detector_voz.ruta_modelo, motor.detector_voz.umbral), (V.MODELO_SILERO, 0.4))
        with self.assertRaises(ValueError):
            V.crear_motor({"motor": "parakeet", "config": {"vad": "webrtc"}})

    def test_corte_fijo_apaga_el_endpoint_nativo(self):
        motor = V.crear_motor_kroko(V.ConfigKroko(corte=1.2, umbral_rms=0.01, rule2=0.5), {})
        self.assertFalse(motor.enable_endpoint)
        self.assertEqual((motor.corte_silencio_s, motor.umbral_rms_silencio, motor.rule2_silence), (1.2, 0.01, 0.5))

    def test_beam_con_hotwords_y_diccionario(self):
        with tempfile.TemporaryDirectory() as tmp:
            dic = Path(tmp) / "d.csv"
            dic.write_text("error,correccion\ncodego,código\n", encoding="utf-8")
            config = V.ConfigKroko(beam=True, hotwords=True, hotwords_score=2.5, diccionario=True)
            motor = V.crear_motor_kroko(config, {"hotwords_file": str(V.DIR_ASR / "voz-real" / "hotwords.txt"),
                                                 "diccionario_file": str(dic)})
        self.assertEqual(motor.motor.decoding_method, "modified_beam_search")
        self.assertEqual(motor.motor.hotwords_score, 2.5)
        self.assertEqual(motor.diccionario.corregir("el codego"), "el código")

    def test_whisper_con_ayudas_lleva_hotwords_criticos_y_jerga_en_el_prompt(self):
        motor = V.crear_motor_whisper(V.ConfigWhisper("small", ayudas=True),
                                      {"hotwords_file": str(V.DIR_ASR / "voz-real" / "hotwords.txt"),
                                       "jerga_file": str(V.DIR_ASR / "voz-real" / "jerga.txt")})
        self.assertIn("Mercado Pago", motor.hotwords)
        self.assertIn("código", motor.hotwords)
        self.assertNotIn("chango", motor.hotwords)
        self.assertIn("chango", motor.initial_prompt)
        sin = V.crear_motor_whisper(V.ConfigWhisper("small"), {})
        self.assertEqual((sin.hotwords, sin.initial_prompt), (None, None))

    def test_normalizar_nivel(self):
        x = np.array([0.0, 0.1, -0.2, 0.05], dtype=np.float32)
        y = V.normalizar_nivel(x)
        self.assertAlmostEqual(float(np.max(np.abs(y))), V.PICO_NORMALIZADO, places=5)
        mudo = np.zeros(10, dtype=np.float32)
        self.assertTrue(np.array_equal(V.normalizar_nivel(mudo), mudo))
        casi_mudo = np.full(10, 1e-6, dtype=np.float32)
        self.assertLessEqual(float(np.max(V.normalizar_nivel(casi_mudo))), 1e-6 * V.GANANCIA_MAXIMA * 1.01)


class TestCorrerPorBloques(unittest.TestCase):
    def audio(self):
        a = np.zeros(16000 * 4, dtype=np.float32)
        a[:16000] = 0.1 * np.sin(2 * np.pi * 220 * np.arange(16000) / 16000)  # voz el primer segundo
        return a

    def test_demora_desde_el_fin_de_la_voz_y_cierre_aparte(self):
        motor = MotorFalso([
            {"tiempo_audio_s": 0.5, "tipo": "parcial", "segmento": 1, "texto": "hola"},
            {"tiempo_audio_s": 1.8, "tipo": "final", "segmento": 1, "texto": "Hola."},
            {"tiempo_audio_s": 3.5, "tipo": "final", "segmento": 2, "texto": "Chau."},
        ])
        motor.inicializar()
        r = V.correr_por_bloques(motor, self.audio(), 100, 0.005)
        primera, ultima = r["finales"]
        self.assertAlmostEqual(primera["demora_s"], 0.8, delta=0.06)  # la voz termina en 1,0 s y la final sale a 1,8 s
        self.assertFalse(primera["cierre"])
        self.assertEqual(r["parciales"], 1)
        self.assertEqual(len(r["bloques_ms"]), 40)
        self.assertGreaterEqual(primera["disponible_s"], primera["fin_audio_s"])

    def test_lo_que_sale_de_vaciar_final_es_cierre_y_no_tiene_demora(self):
        motor = MotorFalso([{"tiempo_audio_s": 99.0, "tipo": "final", "segmento": 1, "texto": "Tarde."}])
        motor.inicializar()
        r = V.correr_por_bloques(motor, self.audio(), 100, 0.005)
        self.assertEqual(len(r["finales"]), 1)
        self.assertTrue(r["finales"][0]["cierre"])
        self.assertIsNone(r["finales"][0]["demora_s"])

    def test_ignora_eventos_sin_letras(self):
        motor = MotorFalso([{"tiempo_audio_s": 0.5, "tipo": "final", "segmento": 1, "texto": " , . "}])
        motor.inicializar()
        self.assertEqual(V.correr_por_bloques(motor, self.audio(), 100, 0.005)["finales"], [])

    def test_ejecutar_variante_corre_todas_las_pruebas_con_un_solo_motor(self):
        import soundfile as sf

        with tempfile.TemporaryDirectory() as tmp:
            wavs = []
            for i in range(2):
                ruta = Path(tmp) / f"{i}.wav"
                est = np.zeros((16000 * 2, 2), dtype=np.float32)
                est[:8000, 0] = 0.1
                sf.write(ruta, est, 16000, subtype="PCM_16")
                wavs.append(str(ruta))
            motores = []

            def crear(spec):
                motores.append(MotorFalso([{"tiempo_audio_s": 1.2, "tipo": "final", "segmento": 1, "texto": "Hola."}]))
                return motores[-1]

            spec = {"motor": "kroko", "config": {"umbral_rms": 0.005}, "bloque_ms": 100,
                    "pruebas": [{"id": "a", "wav": wavs[0], "canal": 0}, {"id": "b", "wav": wavs[1], "canal": 0}]}
            r = V.ejecutar_variante(spec, crear)
        self.assertEqual(len(motores), 1)
        self.assertEqual([p["id"] for p in r["pruebas"]], ["a", "b"])
        self.assertTrue(all(p["finales"] for p in r["pruebas"]))
        self.assertEqual(r["pruebas"][0]["audio_s"], 2.0)
        self.assertEqual(r["pruebas"][0]["bloques"]["n"], 20)


def hipotesis(referencia: str, cambios: dict[str, str]) -> str:
    texto = referencia
    for viejo, nuevo in cambios.items():
        texto = texto.replace(viejo, nuevo)
    return " ".join(texto.split("\n"))


class EjecutorFalso:
    """Devuelve, por variante, la referencia con los errores que se le pidan. Registra las especificaciones recibidas."""

    def __init__(self, errores: dict[str, dict[str, str]], demoras: dict[str, float] | None = None):
        self.errores, self.demoras, self.specs = errores, demoras or {}, []

    def __call__(self, spec):
        self.specs.append(spec)
        nombre = spec["nombre"]
        pruebas = []
        for p in spec["pruebas"]:
            ref = self.referencias[p["id"]]
            pruebas.append({"id": p["id"], "audio_s": 20.0, "parciales": 0, "proceso_s": 1.0, "bloques": {"n": 500, "p95_ms": 0.2, "max_ms": 30.0, "mediana_ms": 0.1},
                            "finales": [{"segmento": 1, "texto": hipotesis(ref, self.errores.get(nombre, {})), "inicio_audio_s": 0.0,
                                         "fin_audio_s": 20.0, "disponible_s": 20.5, "demora_s": self.demoras.get(nombre, 0.8), "cierre": False}]})
        return {"carga_s": 0.5, "metadatos_motor": {"motor": "falso", "nombre": nombre}, "pruebas": pruebas}, 450.0, "falso"


class TestMedicionDeExtremoAExtremo(unittest.TestCase):
    """La cadena del plan con un ejecutor falso: qué se queda, qué no y qué escribe."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.llamadas = self.dir / "llamadas"
        self.llamadas.mkdir()
        filas = ["id,toma,voz,condicion,canal,nota"]
        self.referencias = {}
        for i, (toma, bloque) in enumerate([(1, 1), (2, 1), (2, 2), (2, 3)]):
            id_ = f"2026-10-27_10000{i}-00000{i}"
            self.referencias[id_] = referencia_del_bloque(bloque)
            escribir_prueba(self.llamadas, id_, referencia_del_bloque(bloque))
            filas.append(f"{id_},{toma},luciano,microfono,,")
        self.csv = self.dir / "pruebas.csv"
        self.csv.write_text("\n".join(filas) + "\n", encoding="utf-8")
        self.diccionario = self.dir / "diccionario.csv"
        self.diccionario.write_text("error,correccion\n", encoding="utf-8")

    def medir(self, ejecutor, *opciones):
        ejecutor.referencias = self.referencias
        args = R.parsear(["--pruebas", str(self.llamadas), "--csv", str(self.csv), "--diccionario", str(self.diccionario),
                          "--salida", str(self.dir / "salida"), "--sin-whisper", *opciones])
        return R.medir(args, ejecutor=ejecutor)

    def manifiesto(self):
        return json.loads((self.dir / "salida" / "manifiesto.json").read_text(encoding="utf-8"))

    def test_un_paso_que_mejora_tres_frases_sin_costo_se_queda_y_el_siguiente_se_arma_encima(self):
        errores = {"greedy": {"código": "codego", "la clave": "la clabe", "DNI": "de ni"},
                   "beam": {}, "beam+hotwords": {}, "beam+hotwords-id": {}}
        ejecutor = EjecutorFalso(errores)
        self.medir(ejecutor, "--variantes", "beam,beam+hotwords")
        m = self.manifiesto()
        pasos = {p["paso"]: p for p in m["decision"]["pasos"]}
        self.assertEqual(pasos["beam"]["se_queda"], "beam")
        self.assertTrue(pasos["beam"]["candidatos"][0]["regla"]["pasa"])
        self.assertGreaterEqual(pasos["beam"]["candidatos"][0]["regla"]["criterios"]["etiquetas"]["frases_mas"], 2)
        # beam+hotwords se compara contra beam (no contra greedy) y no mejora nada más
        self.assertEqual(pasos["hotwords"]["contra"], "beam")
        self.assertIsNone(pasos["hotwords"]["se_queda"])
        self.assertEqual(m["decision"]["configuracion_final"], "beam")
        spec_hot = next(s for s in ejecutor.specs if s["nombre"] == "beam+hotwords")
        self.assertTrue(spec_hot["config"]["beam"] and spec_hot["config"]["hotwords"])
        # solo se corrieron las pedidas más la línea base
        self.assertEqual([s["nombre"] for s in ejecutor.specs], ["greedy", "beam", "beam+hotwords"])

    def test_una_etiqueta_nueva_en_una_negativa_descarta_el_paso_aunque_mejore_otras(self):
        negativa = "Me duele el codo"
        errores = {"greedy": {"código": "codego", "la clave": "la clabe", "DNI": "de ni"},
                   "beam": {negativa: "Me duele el código"}}
        self.medir(EjecutorFalso(errores), "--variantes", "beam")
        paso = next(p for p in self.manifiesto()["decision"]["pasos"] if p["paso"] == "beam")
        regla = paso["candidatos"][0]["regla"]
        self.assertFalse(regla["pasa"])
        self.assertFalse(regla["criterios"]["negativas"]["cumple"])
        self.assertIsNone(paso["se_queda"])

    def test_la_demora_extra_descarta_el_paso(self):
        errores = {"greedy": {"código": "codego", "la clave": "la clabe", "DNI": "de ni"}, "beam": {}}
        self.medir(EjecutorFalso(errores, demoras={"greedy": 0.8, "beam": 1.2}), "--variantes", "beam")
        paso = next(p for p in self.manifiesto()["decision"]["pasos"] if p["paso"] == "beam")
        self.assertFalse(paso["candidatos"][0]["regla"]["criterios"]["demora"]["cumple"])

    def test_la_regla_se_mide_solo_en_la_toma_2(self):
        # los errores de la línea base están solo en la toma 1: en la toma 2 no hay nada que mejorar
        id_toma1 = next(iter(self.referencias))
        ejecutor = EjecutorFalso({})
        base = ejecutor.__call__
        errores_en_toma1 = {"código": "codego", "la clave": "la clabe", "DNI": "de ni"}

        def con_errores_en_toma1(spec):
            resultado, memoria, alcance = base(spec)
            if spec["nombre"] == "greedy":
                for p in resultado["pruebas"]:
                    if p["id"] == id_toma1:
                        p["finales"][0]["texto"] = hipotesis(self.referencias[p["id"]], errores_en_toma1)
            return resultado, memoria, alcance

        ejecutor.referencias = self.referencias
        args = R.parsear(["--pruebas", str(self.llamadas), "--csv", str(self.csv), "--diccionario", str(self.diccionario),
                          "--salida", str(self.dir / "salida"), "--sin-whisper", "--variantes", "beam"])
        R.medir(args, ejecutor=con_errores_en_toma1)
        paso = next(p for p in self.manifiesto()["decision"]["pasos"] if p["paso"] == "beam")
        self.assertEqual(paso["candidatos"][0]["regla"]["criterios"]["etiquetas"]["frases_mas"], 0)
        self.assertIsNone(paso["se_queda"])

    def test_diccionario_vacio_no_corre_y_con_pares_si(self):
        ejecutor = EjecutorFalso({})
        self.medir(ejecutor, "--variantes", "+diccionario")
        paso = next(p for p in self.manifiesto()["decision"]["pasos"] if p["paso"] == "diccionario")
        self.assertFalse(paso["candidatos"][0]["aplica"])
        self.assertEqual([s["nombre"] for s in ejecutor.specs], ["greedy"])
        self.diccionario.write_text("error,correccion\ncodego,código\n", encoding="utf-8")
        self.medir(EjecutorFalso({}), "--variantes", "+diccionario")
        paso = next(p for p in self.manifiesto()["decision"]["pasos"] if p["paso"] == "diccionario")
        self.assertTrue(paso["candidatos"][0]["aplica"])

    def test_sin_toma_2_no_se_decide_nada(self):
        self.csv.write_text(self.csv.read_text(encoding="utf-8").replace(",2,luciano", ",1,luciano"), encoding="utf-8")
        self.medir(EjecutorFalso({"greedy": {"código": "codego"}}), "--variantes", "beam")
        m = self.manifiesto()
        self.assertEqual(m["decision"]["configuracion_final"], "greedy")
        resumen = (self.dir / "salida" / "resumen.md").read_text(encoding="utf-8")
        self.assertIn("no se aplicó la regla", resumen)

    def test_salida_con_manifiesto_resumen_y_frases_y_sin_audio(self):
        errores = {"greedy": {"código": "codego"}, "beam": {}}
        self.medir(EjecutorFalso(errores), "--variantes", "beam", "--nota", "prueba")
        salida = self.dir / "salida"
        self.assertEqual(sorted(p.name for p in salida.iterdir()), ["frases.jsonl", "manifiesto.json", "resumen.md"])
        m = self.manifiesto()
        for clave in ("fecha", "comando", "datos", "configuracion", "codigo", "versiones", "hardware", "decision", "variantes"):
            self.assertIn(clave, m)
        self.assertEqual(m["configuracion"]["regla"]["min_frases_mas"], 2)
        self.assertEqual(len(m["datos"]["pruebas"]), 4)
        self.assertNotIn("estereo.wav", json.dumps(m))
        greedy = m["variantes"]["greedy"]
        self.assertEqual(greedy["memoria_pico_mb"], 450.0)
        self.assertIn("toma2/luciano-microfono", greedy["por_grupo"])
        self.assertEqual(set(greedy["por_toma"]), {"1", "2"})
        lineas = [json.loads(l) for l in (salida / "frases.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(lineas), 2 * 4 * 5)  # 2 variantes × 4 pruebas × 5 frases
        self.assertEqual({"variante", "prueba", "referencia", "hipotesis", "etiquetas_ref", "etiquetas_hip", "correcta"} - set(lineas[0]), set())
        resumen = (salida / "resumen.md").read_text(encoding="utf-8")
        for texto in ("ADVERTENCIA", "ni cierra D09", "Regla del plan §2", "Nota de esta corrida", "Sustituciones frecuentes"):
            self.assertIn(texto, resumen)
        for enlace in re.findall(r"\]\(([^)]+)\)", resumen):
            self.assertTrue((salida / enlace.split("#")[0]).exists(), enlace)

    def test_solo_parakeet_no_corre_zipformer_y_compara_con_el_panel(self):
        errores = {V.PARAKEET_PANEL: {"código": "codego", "la clave": "la clabe", "DNI": "de ni"}}
        ejecutor = EjecutorFalso(errores)
        self.medir(ejecutor, "--solo-parakeet")
        self.assertEqual({s["motor"] for s in ejecutor.specs}, {"parakeet"})
        self.assertEqual(ejecutor.specs[0]["nombre"], V.PARAKEET_PANEL)
        self.assertEqual(len(ejecutor.specs), len(V.VARIANTES_PARAKEET))
        m = self.manifiesto()
        self.assertEqual(m["decision"]["configuracion_final"], V.PARAKEET_PANEL)
        self.assertTrue(all(c["contra"] == V.PARAKEET_PANEL for c in m["decision"]["parakeet"]))
        self.assertTrue(any(c["regla"]["pasa"] for c in m["decision"]["parakeet"]))
        resumen = (self.dir / "salida" / "resumen.md").read_text(encoding="utf-8")
        self.assertIn(f"contra `{V.PARAKEET_PANEL}`", resumen)

    def test_solo_parakeet_contra_otra_referencia(self):
        errores = {V.PARAKEET_LABORATORIO: {"código": "codego", "la clave": "la clabe", "DNI": "de ni"}}
        ejecutor = EjecutorFalso(errores)
        self.medir(ejecutor, "--solo-parakeet", "--contra-parakeet", V.PARAKEET_LABORATORIO,
                   "--variantes", "parakeet-0.8-silero-0.5,parakeet-0.5-silero-0.5")
        self.assertEqual([s["nombre"] for s in ejecutor.specs],
                         [V.PARAKEET_LABORATORIO, "parakeet-0.8-silero-0.5", "parakeet-0.5-silero-0.5"])
        m = self.manifiesto()
        self.assertEqual(m["decision"]["configuracion_final"], V.PARAKEET_LABORATORIO)
        self.assertEqual(m["configuracion"]["contra_parakeet"], V.PARAKEET_LABORATORIO)
        self.assertEqual({c["contra"] for c in m["decision"]["parakeet"]}, {V.PARAKEET_LABORATORIO})
        self.assertEqual(len(m["decision"]["parakeet"]), 2)
        resumen = (self.dir / "salida" / "resumen.md").read_text(encoding="utf-8")
        self.assertIn(f"contra `{V.PARAKEET_LABORATORIO}` (la referencia de esta corrida)", resumen)

    def test_sin_pruebas_medibles_avisa(self):
        for carpeta in self.llamadas.iterdir():
            (carpeta / "manifiesto.json").write_text(json.dumps({"guardada": False}), encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.medir(EjecutorFalso({}), "--variantes", "beam")


class TestParametros(unittest.TestCase):
    def test_valores_por_defecto(self):
        args = R.parsear([])
        self.assertEqual((args.toma_decision, args.bloque_ms, args.hilos, args.hotwords_score, args.max_caminos), (2, 40, 2, 1.5, 4))
        self.assertFalse(args.sin_whisper)

    def test_la_carpeta_de_pruebas_por_defecto_es_la_del_servidor(self):
        self.assertEqual(R.carpeta_de_pruebas_por_defecto().name, "llamadas")

    def test_la_memoria_pico_cambia_de_unidad_segun_el_sistema(self):
        self.assertEqual(R.memoria_pico_de(2 * 1024 * 1024 if sys.platform == "darwin" else 2 * 1024), 2.0)


if __name__ == "__main__":
    unittest.main()
