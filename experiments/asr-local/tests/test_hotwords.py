"""Pruebas de hotwords.py y de la configuración de decodificación del motor Zipformer.

Casi todo corre sin descargar nada: la partición de hotwords usa un tokens.txt chico armado acá y
la configuración del motor se valida en el constructor. Solo la prueba de humo carga el modelo
real y se salta si no está en disco.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

import hotwords as H
from motores import MotorFasterWhisper, MotorSherpaZipformer

MODELO = CARPETA_ASR / "modelos" / "sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06"

# Vocabulario de juguete con la forma del de Kroko: faltan las piezas intermedias («▁q» no existe).
TOKENS_CHICOS = """<blk> 0
<sos/eos> 1
<unk> 2
▁que 3
q 4
u 5
e 6
▁c 7
ó 8
di 9
go 10
d 11
i 12
g 13
o 14
c 15
▁ 16
▁C 17
"""


def tokens_chicos() -> dict[str, int]:
    with tempfile.TemporaryDirectory() as tmp:
        ruta = Path(tmp) / "tokens.txt"
        ruta.write_text(TOKENS_CHICOS, encoding="utf-8")
        return H.leer_tokens(ruta)


class TestVocabularioSintetico(unittest.TestCase):
    def test_leer_tokens_devuelve_pieza_e_id(self):
        tokens = tokens_chicos()
        self.assertEqual(tokens["▁que"], 3)
        self.assertEqual(tokens["go"], 10)
        self.assertEqual(len(tokens), 18)

    def test_modo_id_escribe_pieza_tab_menos_id(self):
        texto = H.texto_bpe_vocab(tokens_chicos(), "id")
        lineas = texto.splitlines()
        self.assertEqual(lineas[0], "<blk>\t0")
        self.assertEqual(lineas[3], "▁que\t-3")
        self.assertEqual(len(lineas), 18)

    def test_modo_log_penaliza_cada_pieza_y_prefiere_ids_bajos(self):
        self.assertLess(H.puntaje_pieza(5), H.puntaje_pieza(1))
        # Una pieza larga de id alto sigue ganando a dos piezas cortas de id bajo.
        self.assertGreater(H.puntaje_pieza(400), H.puntaje_pieza(5) + H.puntaje_pieza(6))
        with self.assertRaises(ValueError):
            H.puntaje_pieza(1, "otro")

    def test_leer_hotwords_ignora_comentarios_y_vacias(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "h.txt"
            ruta.write_text("# comentario\n\ncódigo\n  Mercado Pago  \n# [bancos]\nUalá\n", encoding="utf-8")
            self.assertEqual(H.leer_hotwords(ruta), ["código", "Mercado Pago", "Ualá"])

    def test_leer_secciones_agrupa_por_marca(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "h.txt"
            ruta.write_text("# nota\n# [criticos]\ncódigo\nclave\n# [bancos_y_apps]\nUalá\n", encoding="utf-8")
            self.assertEqual(H.leer_secciones(ruta), {"criticos": ["código", "clave"], "bancos_y_apps": ["Ualá"]})

    def test_la_lista_del_repo_tiene_las_dos_secciones_y_no_jerga(self):
        secciones = H.leer_secciones(H.HOTWORDS_POR_DEFECTO)
        self.assertEqual(set(secciones), {"criticos", "bancos_y_apps"})
        self.assertIn("Mercado Pago", secciones["bancos_y_apps"])
        self.assertIn("Ualá", secciones["bancos_y_apps"])
        jerga = {l.strip().lower() for l in (H.HOTWORDS_POR_DEFECTO.parent / "jerga.txt").read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")}
        todas = {h.lower() for lista in secciones.values() for h in lista}
        # luca y mango son plata: están en la lista crítica a propósito (PLAN-VOZ-REAL.md §2).
        self.assertEqual((todas & jerga) - {"luca", "lucas", "mango", "mangos"}, set())


class TestParticionDeHotwords(unittest.TestCase):
    def test_prefiere_pocas_piezas_largas(self):
        self.assertEqual(H.tokenizar_hotword("que", tokens_chicos()), ["▁que"])

    def test_parte_con_las_piezas_que_hay(self):
        tokens = tokens_chicos()
        # En este vocabulario solo hay un camino de piezas para «código».
        self.assertEqual(H.tokenizar_hotword("código", tokens), ["▁c", "ó", "di", "go"])
        self.assertEqual(H.tokenizar_hotword("go", tokens), ["▁", "go"])

    def test_cada_palabra_va_con_su_marca_de_palabra(self):
        piezas = H.tokenizar_hotword("que que", tokens_chicos())
        self.assertEqual(piezas, ["▁que", "▁que"])

    def test_caracter_fuera_del_vocabulario_se_marca(self):
        piezas = H.tokenizar_hotword("qñ", tokens_chicos())
        self.assertIn("<fuera:ñ>", piezas)

    def test_puntaje_opcional_al_final_no_cuenta(self):
        self.assertEqual(H.tokenizar_hotword("que :2.5", tokens_chicos()), ["▁que"])

    def test_la_revision_avisa_de_caracteres_fuera_y_de_letras_sueltas(self):
        revision = {r["hotword"]: r for r in H.revisar_hotwords(["que", "qñ", "dcg", "DCG"], tokens_chicos())}
        self.assertTrue(revision["que"]["ok"])
        self.assertFalse(revision["qñ"]["ok"])
        self.assertTrue(any("fuera del vocabulario" in a for a in revision["qñ"]["avisos"]))
        self.assertFalse(revision["dcg"]["ok"])  # d c g: tres letras sueltas
        self.assertTrue(any("letras sueltas" in a for a in revision["dcg"]["avisos"]))

    def test_las_siglas_no_se_marcan_por_letras_sueltas(self):
        tokens = {**tokens_chicos(), "D": 20, "N": 21, "I": 22}
        revision = H.revisar_hotwords(["DNI"], tokens)
        self.assertEqual(revision[0]["piezas"], ["▁", "D", "N", "I"])
        self.assertTrue(revision[0]["ok"])

    def test_tabla_markdown_tiene_una_fila_por_hotword(self):
        tabla = H.tabla_revision_markdown(H.revisar_hotwords(["que", "qñ"], tokens_chicos()))
        self.assertEqual(len(tabla.splitlines()), 4)
        self.assertIn("`▁que`", tabla)

    @unittest.skipUnless((MODELO / "tokens.txt").exists(), "falta el modelo Kroko en disco")
    def test_con_el_modelo_real_las_palabras_comunes_se_parten_como_las_emite_el_modelo(self):
        # Piezas observadas al reconocer estas palabras con voz TTS (ver el docstring de hotwords.py).
        tokens = H.leer_tokens(MODELO / "tokens.txt")
        esperado = {
            "código": ["▁c", "ó", "di", "go"],
            "clave": ["▁cla", "ve"],
            "transferencia": ["▁trans", "fe", "r", "encia"],
            "token": ["▁to", "k", "en"],
            "domicilio": ["▁do", "mi", "ci", "li", "o"],
        }
        for palabra, piezas in esperado.items():
            self.assertEqual(H.tokenizar_hotword(palabra, tokens), piezas, palabra)


class TestPrepararHotwords(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.modelo = self.dir / "modelo"
        self.modelo.mkdir()
        (self.modelo / "tokens.txt").write_text(TOKENS_CHICOS, encoding="utf-8")
        self.lista = self.dir / "hotwords.txt"
        self.lista.write_text("# nota\nque\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_escribe_vocab_y_lista_limpia_fuera_del_repo(self):
        res = H.preparar_hotwords(self.modelo, self.lista, self.dir / "trabajo")
        self.assertEqual(res["hotwords"], ["que"])
        self.assertEqual(res["hotwords_file"].read_text(encoding="utf-8"), "que\n")
        self.assertTrue(res["bpe_vocab"].read_text(encoding="utf-8").startswith("<blk>\t"))
        self.assertEqual(res["bpe_vocab"].parent, self.dir / "trabajo")

    def test_el_nombre_lleva_la_huella_del_contenido(self):
        a = H.preparar_hotwords(self.modelo, self.lista, self.dir / "trabajo")
        self.lista.write_text("que\nq\n", encoding="utf-8")
        b = H.preparar_hotwords(self.modelo, self.lista, self.dir / "trabajo")
        self.assertNotEqual(a["hotwords_file"], b["hotwords_file"])
        c = H.preparar_hotwords(self.modelo, self.lista, self.dir / "trabajo", puntaje="id")
        self.assertNotEqual(b["bpe_vocab"], c["bpe_vocab"])

    def test_lista_vacia_es_un_error(self):
        self.lista.write_text("# nada\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            H.preparar_hotwords(self.modelo, self.lista, self.dir / "trabajo")


class TestConfiguracionDelMotor(unittest.TestCase):
    """Sin cargar el modelo: lo que importa es lo que valida y lo que registra."""

    def test_los_valores_por_defecto_son_los_del_panel(self):
        motor = MotorSherpaZipformer("cualquiera")
        self.assertEqual(motor.decoding_method, "greedy_search")
        self.assertIsNone(motor.hotwords_file)
        self.assertEqual(motor.max_active_paths, 4)
        self.assertEqual(motor.hotwords_score, 1.5)

    def test_metadatos_registran_la_decodificacion_por_defecto(self):
        deco = MotorSherpaZipformer("cualquiera").metadatos()["decodificacion"]
        self.assertEqual(deco["decoding_method"], "greedy_search")
        self.assertIsNone(deco["hotwords"])
        self.assertIsNone(deco["modeling_unit"])
        self.assertIsNone(deco["bpe_vocab"])

    def test_metadatos_conservan_las_claves_de_siempre(self):
        meta = MotorSherpaZipformer("cualquiera").metadatos()
        for clave in ("motor", "modelo_id", "ruta_modelo", "es_streaming", "tipo_entrega",
                      "version_sherpa", "hilos", "sample_rate", "segmentacion"):
            self.assertIn(clave, meta)

    def test_hotwords_sin_beam_es_un_error(self):
        with self.assertRaises(ValueError):
            MotorSherpaZipformer("cualquiera", hotwords_file="h.txt")

    def test_metodo_o_caminos_invalidos(self):
        with self.assertRaises(ValueError):
            MotorSherpaZipformer("cualquiera", decoding_method="otro")
        with self.assertRaises(ValueError):
            MotorSherpaZipformer("cualquiera", decoding_method="modified_beam_search", max_active_paths=0)
        with self.assertRaises(ValueError):
            MotorSherpaZipformer("cualquiera", bpe_puntaje="otro")

    def test_beam_con_hotwords_guarda_la_configuracion(self):
        motor = MotorSherpaZipformer("cualquiera", decoding_method="modified_beam_search", max_active_paths=8,
                                     hotwords_file="h.txt", hotwords_score=2.0)
        deco = motor.metadatos()["decodificacion"]
        self.assertEqual(deco["decoding_method"], "modified_beam_search")
        self.assertEqual(deco["max_active_paths"], 8)
        self.assertEqual(deco["hotwords_score"], 2.0)
        self.assertEqual(deco["modeling_unit"], "bpe")
        self.assertEqual(deco["bpe_puntaje"], "log")

    def test_whisper_registra_hotwords_y_prompt_y_por_defecto_no_usa_ninguno(self):
        self.assertIsNone(MotorFasterWhisper("small").hotwords)
        motor = MotorFasterWhisper("small", hotwords="código clave", initial_prompt="chango, ñaño")
        self.assertEqual((motor.hotwords, motor.initial_prompt), ("código clave", "chango, ñaño"))


@unittest.skipUnless((MODELO / "encoder.onnx").exists(), "falta el modelo Kroko en disco")
class TestHumoConElModeloReal(unittest.TestCase):
    """Con el wav de prueba del modelo: la lista de hotwords llega al decodificador y sube lo que pide."""

    @classmethod
    def setUpClass(cls):
        import soundfile as sf

        audio, hz = sf.read(MODELO / "test_wavs" / "0.wav", dtype="float32")
        destino = int(len(audio) * 16000 / hz)
        cls.audio = np.interp(np.linspace(0, len(audio) - 1, destino), np.arange(len(audio)), audio).astype(np.float32)

    def reconocer(self, **opciones) -> str:
        motor = MotorSherpaZipformer(str(MODELO), hilos=2, **opciones)
        motor.inicializar()
        eventos = []
        for i in range(0, len(self.audio), 1600):
            eventos += motor.procesar_bloque(self.audio[i:i + 1600], i / 16000, min(i + 1600, len(self.audio)) / 16000)
        eventos += motor.vaciar_final(len(self.audio) / 16000)
        return " ".join(e.texto for e in eventos if e.tipo == "final")

    def test_beam_sin_hotwords_funciona(self):
        self.assertIn("país", self.reconocer(decoding_method="modified_beam_search"))

    def test_un_hotword_con_puntaje_alto_se_nota_en_la_salida(self):
        with tempfile.TemporaryDirectory() as tmp:
            lista = Path(tmp) / "h.txt"
            lista.write_text("país\n", encoding="utf-8")
            base = self.reconocer(decoding_method="modified_beam_search")
            con = self.reconocer(decoding_method="modified_beam_search", hotwords_file=lista, hotwords_score=20.0)
        self.assertGreater(con.count("país"), base.count("país"))


if __name__ == "__main__":
    unittest.main()
