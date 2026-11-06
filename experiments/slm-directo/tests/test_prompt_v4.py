"""Prompt v4 y hablantes por rol: texto, esquema y mensaje que recibe el SLM, sin modelo."""

from __future__ import annotations

import csv
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
from detectores import DetectorSLM, armar_mensaje_usuario, cargar_prompt, esquema_de, evidencia_en_texto, huella  # noqa: E402
from filtro_tito import FlujoTitoSLM, TitoGuion  # noqa: E402
from test_ensayo import OllamaFalso  # noqa: E402
from test_sin_indicio import ClienteGrabador  # noqa: E402

ORDEN_V1 = ["riesgo", "alerta_sugerida", "motivo", "evidencia"]


class Prompts(unittest.TestCase):
    def test_los_anteriores_no_cambian(self):
        self.assertEqual(huella(cargar_prompt("tarea")), "bf4284996898c45d")
        self.assertEqual(huella(cargar_prompt("v3")), "a944aadc550480b3")

    def test_v3_orden_v1_solo_reordena_los_campos(self):
        v3, orden = cargar_prompt("v3").splitlines(), cargar_prompt("v3-orden-v1").splitlines()
        self.assertEqual(sorted(v3), sorted(orden))
        self.assertEqual(v3[:-4], orden[:-4])
        self.assertEqual([l.split('"')[1] for l in orden[-4:]], ORDEN_V1)
        self.assertEqual(esquema_de("v3-orden-v1")["required"], ORDEN_V1)

    def test_v4_usa_el_orden_de_v1_y_nombra_los_roles(self):
        texto = cargar_prompt("v4")
        self.assertEqual([l.split('"')[1] for l in texto.splitlines()[-4:]], ORDEN_V1)
        self.assertEqual(esquema_de("v4")["required"], ORDEN_V1)
        for frase in ("PROTEGIDA (la persona que cuidás)", "OTRA le pide", "entre por su cuenta", "nunca entran en esta excepción"):
            self.assertIn(frase, texto)
        self.assertNotIn("peligro concreto", texto)

    def test_v4_cita_libre_solo_cambia_la_instruccion_de_la_cita(self):
        v4, libre = cargar_prompt("v4").splitlines(), cargar_prompt("v4-cita-libre").splitlines()
        self.assertEqual(v4[:-1], libre[:-1])
        self.assertIn("donde OTRA lo pide", v4[-1])
        self.assertIn("de la transcripción que lo justifica", libre[-1])
        self.assertEqual(esquema_de("v4-cita-libre"), esquema_de("v4"))
        self.assertEqual(huella(cargar_prompt("v4")), "92df75a22c2746fb")


class Roles(unittest.TestCase):
    def test_cubre_los_199_de_desarrollo_y_ningun_reservado(self):
        roles = json.loads(casos.ROLES.read_text(encoding="utf-8"))
        self.assertEqual(sorted(roles), casos.ids_de_casos(particion="desarrollo"))
        self.assertEqual(len(roles), 199)
        self.assertFalse([c for c in roles if "CV2-T" in c])
        self.assertEqual({r["protegida"] for r in roles.values()}, {"A", "B"})

    def test_en_estafas_con_pedido_la_protegida_no_formula_el_pedido(self):
        for c, r in json.loads(casos.ROLES.read_text(encoding="utf-8")).items():
            tr = casos.cargar_referencia(c).get("t_r_linea")
            if tr:
                self.assertEqual(r["origen"], "t_r")
                self.assertNotEqual(casos.cargar_texto(c)[tr - 1].hablante, r["protegida"], c)

    def test_con_roles_no_cambia_el_texto(self):
        c = "TR-10-ofrecimiento-inducido"
        crudas = casos.cargar_texto(c)
        conv = casos.con_roles(c, crudas)
        self.assertEqual([l.texto for l in conv], [l.texto for l in crudas])
        self.assertEqual({l.hablante for l in conv}, {"PROTEGIDA", "OTRA"})
        self.assertEqual({l.hablante for l in crudas if l.hablante == "A"}, {"A"})
        self.assertEqual([l.hablante == "A" for l in crudas], [l.hablante == "PROTEGIDA" for l in conv])


DIALOGO_ROL = (Linea("OTRA", "Te llamo del banco."), Linea("PROTEGIDA", "Decime."), Linea("OTRA", "Pasame el código."))


class MensajeConRol(unittest.TestCase):
    def test_ab_no_cambia(self):
        m = armar_mensaje_usuario((Linea("A", "Hola"),), "ab")
        self.assertIn("las letras no indican quién llamó ni quién es sospechoso", m)
        self.assertIn("1. A: Hola", m)

    def test_rol_nombra_a_cada_persona(self):
        m = armar_mensaje_usuario(DIALOGO_ROL, "rol")
        self.assertIn("PROTEGIDA es la persona que protegés", m)
        self.assertIn("1. OTRA: Te llamo del banco.", m)
        self.assertIn("2. PROTEGIDA: Decime.", m)
        self.assertNotIn("A:", m.replace("OTRA:", "").replace("PROTEGIDA:", ""))

    def test_rol_rechaza_letras_para_no_engañar_en_silencio(self):
        with self.assertRaises(ValueError):
            armar_mensaje_usuario((Linea("A", "Hola"),), "rol")

    def test_la_cita_con_el_rol_adelante_se_reconoce(self):
        self.assertTrue(evidencia_en_texto("3. OTRA: Pasame el código.", DIALOGO_ROL))
        self.assertTrue(evidencia_en_texto("PROTEGIDA: Decime.", DIALOGO_ROL))
        self.assertFalse(evidencia_en_texto("OTRA: Pasame la clave.", DIALOGO_ROL))

    def test_tito_sin_indicio_pasa_los_roles_al_slm_y_a_tito_solo_el_texto(self):
        cliente = ClienteGrabador()
        slm = DetectorSLM(cliente, "falso", cargar_prompt("v4"), "rol", esquema=esquema_de("v4"))
        vistos = []

        class Tito(TitoGuion):
            def puntuar(self, n, texto):
                vistos.append(texto)
                return super().puntuar(n, texto)

        flujo = FlujoTitoSLM(Tito({3: 0.9}, set()), slm, 0.5, indicio=False)
        flujo.reiniciar()
        for n in range(1, 4):
            flujo.evaluar(DIALOGO_ROL[:n])
        self.assertEqual(len(cliente.pedidos), 1)
        self.assertEqual(cliente.pedidos[0]["mensajes"][0]["content"], cargar_prompt("v4"))
        self.assertEqual(cliente.pedidos[0]["mensajes"][1]["content"], armar_mensaje_usuario(DIALOGO_ROL, "rol"))
        self.assertEqual(vistos, [l.texto for l in DIALOGO_ROL])


class CorridaConRoles(unittest.TestCase):
    def test_correr_registra_los_roles_y_el_resumen_funciona(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b", "--prompts", "v4", "--hablantes", "rol", "--sin-reglas",
                    "--casos", "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01",
                    "--filtro-tito", "--tito-puntajes", "4=0.9", "--sin-indicio",
                    "--url", f"http://127.0.0.1:{servidor.server_port}", "--salida", tmp,
                ])
                (carpeta,) = Path(tmp).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
                    filas = list(csv.DictReader(f))
                texto = resumen.armar_resumen(carpeta)
        finally:
            servidor.shutdown()
            servidor.server_close()
        self.assertEqual(manifiesto["roles_protegida"], huella(casos.ROLES.read_text(encoding="utf-8")))
        self.assertEqual({f["hablante"] for f in filas}, {"PROTEGIDA", "OTRA"})
        self.assertIn("tito-slm-sin-indicio\\|modelo-falso:1b\\|v4\\|rol", texto)

    def test_v4_sigue_tras_el_aviso_con_tito_y_roles(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                correr.main([
                    "--modelos", "modelo-falso:1b", "--prompts", "v4-cita-libre", "--hablantes", "rol", "--sin-reglas",
                    "--casos", "SC-WA-CODE-01-e01", "--filtro-tito", "--tito-puntajes", "1=0.9", "--sin-indicio",
                    "--seguir-tras-aviso", "--url", f"http://127.0.0.1:{servidor.server_port}", "--salida", tmp,
                ])
                (carpeta,) = Path(tmp).iterdir()
                manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
                texto = resumen.armar_resumen(carpeta)
        finally:
            servidor.shutdown()
            servidor.server_close()
        self.assertEqual(manifiesto["modo_termino"], correr.MODO_DIAGNOSTICO)
        self.assertIn("v4-cita-libre\\|rol", texto)


if __name__ == "__main__":
    unittest.main()
