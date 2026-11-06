"""Prompt v5 y controles de maniobras: texto, casos y Colab, sin modelo."""

from __future__ import annotations

import ast
import csv
import io
import json
import re
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import HTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import casos  # noqa: E402
import correr_controles  # noqa: E402
from detectores import PROMPTS, cargar_prompt, esquema_de, huella, usa_roles  # noqa: E402
from test_ensayo import OllamaFalso  # noqa: E402

ORDEN_V1 = ["riesgo", "alerta_sugerida", "motivo", "evidencia"]
VARIANTES = ("v5-maniobras", "v5-indirectos", "v5-sin-excepcion")


def agregadas(prompt: str) -> list[str]:
    v4 = set(cargar_prompt("v4").splitlines())
    return [l for l in cargar_prompt(prompt).splitlines() if l not in v4]


def quitadas(prompt: str) -> list[str]:
    actuales = set(cargar_prompt(prompt).splitlines())
    return [l for l in cargar_prompt("v4").splitlines() if l not in actuales]


class Prompts(unittest.TestCase):
    def test_v4_y_los_anteriores_no_cambian(self):
        self.assertEqual(huella(cargar_prompt("tarea")), "bf4284996898c45d")
        self.assertEqual(huella(cargar_prompt("v4")), "92df75a22c2746fb")
        self.assertEqual(huella(cargar_prompt("v4-cita-libre")), "5b216792ce0bb9c6")

    def test_todas_conservan_el_orden_de_campos_de_v1(self):
        for p in (*VARIANTES, "v5"):
            self.assertEqual([l.split('"')[1] for l in cargar_prompt(p).splitlines()[-4:]], ORDEN_V1, p)
            self.assertEqual(esquema_de(p)["required"], ORDEN_V1, p)

    def test_maniobras_solo_agrega_la_regla_y_su_limite(self):
        self.assertEqual(quitadas("v5-maniobras"), [])
        regla, limite = agregadas("v5-maniobras")
        self.assertIn("todavía no haya un pedido", regla)
        self.assertIn("sin ayuda ni forma de comprobarlo", regla)
        self.assertTrue(limite.startswith("- "))
        self.assertIn("gestión que PROTEGIDA pidió", limite)

    def test_el_apuro_solo_sigue_sin_alcanzar(self):
        for p in (*VARIANTES, "v5"):
            self.assertIn("Que alguien apure", cargar_prompt(p), p)
            self.assertIn("no alcanza por sí solo para alertar", cargar_prompt(p), p)

    def test_indirectos_solo_toca_la_lista_de_claves_y_los_pedidos_indirectos(self):
        self.assertEqual(len(quitadas("v5-indirectos")), 2)
        self.assertEqual(len(agregadas("v5-indirectos")), 2)
        texto = cargar_prompt("v5-indirectos")
        self.assertIn("decir o escribir claves", texto)
        self.assertIn("en condicional", texto)
        self.assertIn("Reconocé también los pedidos indirectos", texto)

    def test_sin_excepcion_solo_saca_la_excepcion(self):
        (ultima, excepcion) = quitadas("v5-sin-excepcion")
        self.assertIn("nunca entran en esta excepción", excepcion)
        self.assertNotIn("excepción", cargar_prompt("v5-sin-excepcion"))
        self.assertEqual(agregadas("v5-sin-excepcion"), [ultima.rstrip(";") + "."])

    def test_v5_suma_exactamente_los_tres_cambios(self):
        def sin_cierre(lineas):  # la lista de «no alcanza» cierra con punto en otro ítem según el prompt
            return {l.rstrip(";.") for l in lineas}

        v5 = sin_cierre(cargar_prompt("v5").splitlines())
        esperadas = sin_cierre(agregadas("v5-maniobras") + agregadas("v5-indirectos"))
        self.assertLessEqual(esperadas, v5)
        self.assertEqual(v5 - sin_cierre(cargar_prompt("v4").splitlines()), esperadas)
        self.assertNotIn("excepción", cargar_prompt("v5"))
        for linea in quitadas("v5-indirectos"):
            self.assertNotIn(linea.rstrip(";."), v5)

    def test_las_reglas_nuevas_no_copian_frases_de_los_casos(self):
        """Cinco palabras seguidas iguales a un caso de desarrollo serían ajustar el prompt a esos casos."""
        def palabras(t):
            return re.findall(r"\w+", t.lower())

        corpus = set()
        for c in casos.ids_de_casos(particion="desarrollo"):
            for l in casos.cargar_texto(c):
                p = palabras(l.texto)
                corpus |= {tuple(p[i:i + 5]) for i in range(len(p) - 4)}
        for prompt in ("v5-maniobras", "v5-indirectos"):
            for linea in agregadas(prompt):
                p = palabras(linea)
                self.assertFalse(corpus & {tuple(p[i:i + 5]) for i in range(len(p) - 4)}, linea)


class PromptsConRoles(unittest.TestCase):
    def test_solo_los_que_nombran_a_protegida_y_otra_exigen_roles(self):
        for p in PROMPTS:
            self.assertEqual(usa_roles(p), "PROTEGIDA" in cargar_prompt(p), p)


class Controles(unittest.TestCase):
    def setUp(self):
        self.datos = json.loads(correr_controles.CONTROLES.read_text(encoding="utf-8"))

    def test_no_tocan_los_199_de_desarrollo(self):
        self.assertEqual(len(casos.ids_de_casos(particion="desarrollo")), 199)
        self.assertFalse(set(self.datos) & set(casos.ids_de_casos()))
        self.assertFalse(list((RAIZ / "casos" / "texto").glob("CTRL-*")))

    def test_hay_legitimas_y_estafas_sin_pedido_con_protegida_valida(self):
        clases = [c["clase"] for c in self.datos.values()]
        self.assertEqual(clases.count("legitima_dificil"), 12)
        self.assertEqual(clases.count("vishing"), 6)
        for caso, c in self.datos.items():
            self.assertIn(c["protegida"], {"A", "B"}, caso)
            self.assertGreaterEqual(len(c["lineas"]), 8, caso)
            self.assertIs(c["revision_humana"], False, caso)
            self.assertEqual({l[:3] for l in c["lineas"]}, {"A: ", "B: "}, caso)

    def test_no_copian_frases_de_los_casos_de_desarrollo(self):
        """Si repitieran los casos, no dirían nada sobre si la regla generaliza."""
        vistas = {l.texto.lower() for c in casos.ids_de_casos(particion="desarrollo") for l in casos.cargar_texto(c)}
        for caso, c in self.datos.items():
            for linea in c["lineas"]:
                if len(linea[3:].split()) >= 5:  # «Perfecto, gracias» no dice nada del caso
                    self.assertNotIn(linea[3:].lower(), vistas, caso)

    def test_se_materializan_en_el_formato_de_los_casos(self):
        with tempfile.TemporaryDirectory() as tmp:
            ids = correr_controles.materializar(Path(tmp))
            self.assertEqual(sorted(ids), sorted(self.datos))
            with correr_controles.casos_de(Path(tmp)):
                self.assertEqual(casos.ids_de_casos(particion="desarrollo"), sorted(ids))
                for c in ids:
                    roles = casos.con_roles(c, casos.cargar_texto(c))
                    self.assertEqual({l.hablante for l in roles}, {"PROTEGIDA", "OTRA"})
                    self.assertEqual(casos.cargar_referencia(c)["clase"], self.datos[c]["clase"])
            self.assertEqual(len(casos.ids_de_casos(particion="desarrollo")), 199)

    def test_corre_de_punta_a_punta_con_modelo_falso(self):
        servidor = HTTPServer(("127.0.0.1", 0), OllamaFalso)
        threading.Thread(target=servidor.serve_forever, daemon=True).start()
        try:
            with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
                correr_controles.main([
                    "--modelos", "modelo-falso:1b", "--prompts", "v5-maniobras", "--hablantes", "rol", "--sin-reglas",
                    "--url", f"http://127.0.0.1:{servidor.server_port}", "--salida", tmp,
                ])
                (carpeta,) = Path(tmp).iterdir()
                with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
                    filas = list(csv.DictReader(f))
        finally:
            servidor.shutdown()
            servidor.server_close()
        self.assertEqual({f["case_id"] for f in filas}, set(self.datos))
        self.assertEqual({f["hablante"] for f in filas}, {"PROTEGIDA", "OTRA"})


class Colab(unittest.TestCase):
    SCRIPT = RAIZ / "colab" / "probar_prompt_v5.py"

    def constante(self, nombre):
        for n in ast.parse(self.SCRIPT.read_text(encoding="utf-8")).body:
            if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", None) == nombre:
                return ast.literal_eval(n.value)
        self.fail(f"Falta {nombre}")

    def test_las_condiciones_usan_prompts_existentes_y_siguen_tras_el_aviso(self):
        condiciones = self.constante("CONDICIONES")
        self.assertEqual({c[2] for c in condiciones}, {*VARIANTES, "v5"})
        for clave, _, prompt, hablantes, opciones in condiciones:
            self.assertIn(prompt, PROMPTS)
            self.assertEqual(hablantes, "rol", clave)
            self.assertIn("--seguir-tras-aviso", opciones, clave)

    def test_los_controles_incluyen_a_v4_como_referencia(self):
        prompts = self.constante("PROMPTS_CONTROLES")
        self.assertIn("v4", prompts)
        for p in prompts:
            self.assertIn(p, PROMPTS)

    def test_el_notebook_baja_el_script_de_su_rama(self):
        rama = self.constante("RAMA")
        cuaderno = json.loads((RAIZ / "colab" / "COLAB-PROMPT-V5.ipynb").read_text(encoding="utf-8"))
        fuente = "".join("".join(c["source"]) for c in cuaderno["cells"])
        self.assertEqual(rama, "prompt-v5-colab")
        self.assertIn(f"RAMA = '{rama}'", fuente)
        self.assertIn("probar_prompt_v5.py", fuente)
        self.assertIn("COLAB_GUARDAR_EN_DRIVE'] = '0'", fuente)

    @unittest.skipUnless((RAIZ / "casos" / "RESERVA-FUERA-DEL-REPO.md").exists(), "la reserva está en esta rama")
    def test_el_colab_corre_sin_la_reserva(self):
        self.assertFalse([c for c in casos.ids_de_casos() if "CV2-T" in c])


if __name__ == "__main__":
    unittest.main()
