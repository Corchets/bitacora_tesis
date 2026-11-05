"""Pruebas del diccionario de corrección (#94): reemplazos sobre la frase final, nunca sobre parciales."""

from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

CARPETA_ASR = Path(__file__).resolve().parent.parent
if str(CARPETA_ASR) not in sys.path:
    sys.path.insert(0, str(CARPETA_ASR))

from diccionario import Diccionario, MotorConDiccionario
from motores import EventoASR, MotorFalso


def dic(*pares, **opciones) -> Diccionario:
    return Diccionario(list(pares), **opciones)


class TestReemplazoExacto(unittest.TestCase):
    def test_reemplaza_la_palabra_y_conserva_la_puntuacion(self):
        d = dic(("codego", "código"))
        self.assertEqual(d.corregir("Decime el codego, dale."), "Decime el código, dale.")

    def test_conserva_la_mayuscula_inicial(self):
        d = dic(("codego", "código"))
        self.assertEqual(d.corregir("Codego de seis dígitos"), "Código de seis dígitos")
        self.assertEqual(d.corregir("CODEGO ya"), "Código ya")

    def test_no_distingue_mayusculas_ni_tildes_al_buscar(self):
        d = dic(("cosdigo", "código"))
        self.assertEqual(d.corregir("el cosDIGO ya"), "el código ya")
        d2 = dic(("codigó", "código"))
        self.assertEqual(d2.corregir("el codigo ya"), "el código ya")

    def test_error_de_varias_palabras(self):
        d = dic(("cos digo", "código"))
        self.assertEqual(d.corregir("pasame el cos digo ahora"), "pasame el código ahora")

    def test_error_de_varias_palabras_no_cruza_una_coma(self):
        d = dic(("cos digo", "código"))
        self.assertEqual(d.corregir("no sé cos, digo que sí"), "no sé cos, digo que sí")

    def test_gana_el_error_mas_largo(self):
        d = dic(("cos", "cosa"), ("cos digo", "código"))
        self.assertEqual(d.corregir("el cos digo y el cos"), "el código y el cosa")

    def test_no_toca_palabras_que_no_estan_en_el_archivo(self):
        d = dic(("codego", "código"))
        texto = "Hola, ¿cómo andás? Pasame la clave del banco."
        self.assertEqual(d.corregir(texto), texto)

    def test_no_reemplaza_pedazos_de_palabras(self):
        d = dic(("cod", "código"))
        self.assertEqual(d.corregir("el codo y el cod"), "el codo y el código")

    def test_conserva_los_signos_de_apertura_y_cierre(self):
        d = dic(("vo", "vos"))
        self.assertEqual(d.corregir("¿Vo sabés? ¡Vo!"), "¿Vos sabés? ¡Vos!")

    def test_conserva_la_ñ_al_comparar(self):
        d = dic(("nano", "ñaño"))
        self.assertEqual(d.corregir("el año y el nano"), "el año y el ñaño")

    def test_texto_vacio_o_sin_cambios(self):
        d = dic(("a", "b"))
        self.assertEqual(d.corregir(""), "")
        self.assertEqual(d.corregir("sin cambios acá"), "sin cambios acá")

    def test_es_idempotente(self):
        d = dic(("codego", "código"), ("cos digo", "código"))
        una_vez = d.corregir("el codego y el cos digo")
        self.assertEqual(d.corregir(una_vez), una_vez)

    def test_detalle_informa_cada_cambio(self):
        d = dic(("codego", "código"))
        texto, cambios = d.corregir_con_detalle("el Codego y el codego")
        self.assertEqual(texto, "el Código y el código")
        self.assertEqual([c["original"] for c in cambios], ["Codego", "codego"])
        self.assertTrue(all(c["tipo"] == "exacto" for c in cambios))


class TestReemplazoAproximado(unittest.TestCase):
    def test_corrige_un_typo_de_una_palabra_larga(self):
        d = dic(("trasferencia", "transferencia"))
        self.assertEqual(d.corregir("hacé la trasferenci ahora"), "hacé la transferencia ahora")
        _, cambios = d.corregir_con_detalle("la trasferenci")
        self.assertEqual(cambios[0]["tipo"], "aproximado")

    def test_no_aplica_a_claves_cortas(self):
        d = dic(("clavo", "clave"))
        self.assertEqual(d.corregir("el clavs"), "el clavs")

    def test_se_puede_apagar(self):
        d = dic(("trasferencia", "transferencia"), aproximado=False)
        self.assertEqual(d.corregir("la trasferenci"), "la trasferenci")

    def test_no_toca_una_palabra_que_ya_es_la_correccion(self):
        d = dic(("trasferencia", "transferencia"))
        self.assertEqual(d.corregir("la transferencia"), "la transferencia")

    def test_ambiguo_no_se_toca(self):
        d = dic(("trasferencia", "transferencia"), ("trasferensia", "otra"))
        # «trasferenzia» está a un cambio de las dos claves: no se elige ninguna.
        self.assertEqual(d.corregir("la trasferenzia"), "la trasferenzia")

    def test_lo_exacto_tiene_prioridad(self):
        d = dic(("trasferencia", "transferencia"), ("trasferenciaa", "otra"))
        self.assertEqual(d.corregir("la trasferenciaa"), "la otra")

    def test_no_cambia_palabras_lejanas(self):
        d = dic(("trasferencia", "transferencia"))
        self.assertEqual(d.corregir("la preferencia"), "la preferencia")


class TestArchivoDeParesCSV(unittest.TestCase):
    def escribir(self, contenido: str) -> Path:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        ruta = Path(self.tmp.name) / "diccionario.csv"
        ruta.write_text(contenido, encoding="utf-8")
        return ruta

    def test_lee_pares_ignorando_comentarios_y_encabezado(self):
        ruta = self.escribir("error,correccion\n# nota\n\ncodego,código\ncos digo,código\n")
        d = Diccionario.desde_archivo(ruta)
        self.assertEqual(len(d), 2)
        self.assertEqual(d.corregir("el codego"), "el código")

    def test_archivo_solo_con_encabezado_queda_vacio_y_no_cambia_nada(self):
        d = Diccionario.desde_archivo(self.escribir("error,correccion\n# ejemplo,de comentario\n"))
        self.assertEqual(len(d), 0)
        self.assertEqual(d.corregir("cualquier cosa"), "cualquier cosa")

    def test_linea_incompleta_dice_cual_es(self):
        with self.assertRaises(ValueError) as ctx:
            Diccionario.desde_archivo(self.escribir("error,correccion\ncodego\n"))
        self.assertIn("línea 2", str(ctx.exception))

    def test_error_repetido_con_otra_correccion_es_un_error(self):
        with self.assertRaises(ValueError):
            Diccionario.desde_archivo(self.escribir("error,correccion\ncodego,código\nCodego,codigo\n"))

    def test_error_igual_a_correccion_es_un_error(self):
        with self.assertRaises(ValueError):
            dic(("código", "código"))

    def test_los_valores_con_coma_van_entre_comillas(self):
        d = Diccionario.desde_archivo(self.escribir('error,correccion\nhola,"hola, che"\n'))
        self.assertEqual(d.corregir("hola"), "hola, che")


class TestSoloFinales(unittest.TestCase):
    def evento(self, tipo: str, texto: str) -> EventoASR:
        return EventoASR(tipo=tipo, segmento=1, texto=texto, inicio_audio_s=0.0, fin_audio_s=1.0, proceso_ms=5.0)

    def test_corrige_el_final_y_no_toca_el_original(self):
        d = dic(("codego", "código"))
        original = self.evento("final", "el codego")
        corregido = d.aplicar_a_evento(original)
        self.assertEqual(corregido.texto, "el código")
        self.assertEqual(original.texto, "el codego")
        self.assertEqual(replace(corregido, texto=original.texto), original)

    def test_nunca_toca_un_parcial(self):
        d = dic(("codego", "código"))
        parcial = self.evento("parcial", "el codego")
        self.assertIs(d.aplicar_a_evento(parcial), parcial)

    def test_el_motor_con_diccionario_corrige_solo_los_finales(self):
        programados = [
            {"tiempo_audio_s": 0.2, "tipo": "parcial", "segmento": 1, "texto": "el codego"},
            {"tiempo_audio_s": 0.4, "tipo": "final", "segmento": 1, "texto": "el codego"},
            {"tiempo_audio_s": 0.6, "tipo": "parcial", "segmento": 2, "texto": "dale codego"},
        ]
        motor = MotorConDiccionario(MotorFalso(programados), dic(("codego", "código")))
        motor.inicializar()
        eventos = motor.procesar_bloque(np.zeros(1600, dtype=np.float32), 0.0, 1.0)
        eventos += motor.vaciar_final(1.0)
        self.assertEqual([(e.tipo, e.texto) for e in eventos],
                         [("parcial", "el codego"), ("final", "el código"), ("parcial", "dale codego")])

    def test_el_motor_con_diccionario_delega_y_registra_la_configuracion(self):
        motor = MotorConDiccionario(MotorFalso(), dic(("codego", "código")))
        self.assertEqual(motor.nombre, "falso")
        self.assertTrue(motor.es_streaming)
        meta = motor.metadatos()
        self.assertEqual(meta["motor"], "falso")
        self.assertEqual(meta["diccionario"]["pares"], 1)
        self.assertTrue(meta["diccionario"]["aproximado"])
        self.assertEqual(meta["diccionario"]["solo_finales"], True)


if __name__ == "__main__":
    unittest.main()
