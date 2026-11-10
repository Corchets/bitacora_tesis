"""Revisión de producto de #143 (corridas/2026-11-10_revision-producto/): tres variantes de la configuración congelada
(c-premisa-corte-riesgo), con un solo párrafo cambiado cada una, y la regla de su analizar.py en dos versiones (con las
etiquetas de producto y con la anotación original). Sin modelo: contra el Ollama falso de la humo.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_revision_producto_143 -v
"""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

import casos  # noqa: E402
import correr  # noqa: E402
from detectores import (ESQUEMA_MOTIVO, ESQUEMA_SALIDA, MAXIMO_TOKENS_CORTE_RIESGO, PROMPT_MOTIVO_C,  # noqa: E402
                        PROMPTS_CORTE_RIESGO, VARIANTES_REVISION_PRODUCTO, cargar_prompt, cargar_prompt_motivo,
                        esquema_de, huella)
from test_config_congelada_143 import _ConServidor, correr_main  # noqa: E402

BASE = "c-premisa-corte-riesgo"
VARIANTES = ("c-codigo-corte-riesgo", "c-consejos-corte-riesgo", "c-freno-corte-riesgo")
CARPETA = RAIZ / "corridas" / "2026-11-10_revision-producto"

_spec = importlib.util.spec_from_file_location("analizar_revision_producto", CARPETA / "analizar.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)


def parrafos(texto: str) -> list[str]:
    return texto.strip().split("\n\n")


class TestUnSoloParrafo(unittest.TestCase):
    def setUp(self):
        self.base = parrafos(cargar_prompt(BASE))

    def cambiados(self, variante: str) -> list[int]:
        otro = parrafos(cargar_prompt(variante))
        self.assertEqual(len(otro), len(self.base), "los mismos párrafos, en el mismo orden")
        return [i for i, (x, y) in enumerate(zip(self.base, otro)) if x != y]

    def test_registradas_como_la_configuracion_congelada(self):
        self.assertEqual(tuple(f"{v}-corte-riesgo" for v in VARIANTES_REVISION_PRODUCTO), VARIANTES)
        self.assertLessEqual({BASE, *VARIANTES}, PROMPTS_CORTE_RIESGO)
        for v in VARIANTES:
            self.assertEqual(esquema_de(v), ESQUEMA_SALIDA, v)

    def test_la_base_es_la_congelada(self):
        self.assertTrue(self.base[3].startswith("Que el número no esté agendado pesa"))
        self.assertTrue(self.base[5].startswith("Una llamada legítima también puede pedir el nombre, el DNI"))
        self.assertTrue(self.base[6].startswith("Respondé solo con un objeto JSON"))

    def test_c_codigo_cambia_solo_la_regla_del_codigo(self):
        self.assertEqual(self.cambiados("c-codigo-corte-riesgo"), [3])
        nuevo = parrafos(cargar_prompt("c-codigo-corte-riesgo"))[3]
        self.assertTrue(nuevo.startswith("Que el número no esté agendado pesa: un código que le llegó a PROTEGIDA"))
        self.assertNotIn("un banco, una empresa o un organismo", nuevo, "la regla ya no depende de quién dice ser OTRA")
        self.assertIn("no es pedirlo", nuevo, "dar un código no es pedirlo")
        # Lo demás del párrafo queda igual: el falso familiar y el cierre.
        for frase in ("familiar o un conocido que llama desde un número desconocido para pedir plata es una de las estafas más comunes.",
                      "Si OTRA va hacia alguno de esos pedidos, tenelo en cuenta en el riesgo, aunque la charla sea amable."):
            self.assertIn(frase, self.base[3])
            self.assertIn(frase, nuevo)

    def test_c_consejos_cambia_solo_ese_parrafo_por_los_consejos(self):
        self.assertEqual(self.cambiados("c-consejos-corte-riesgo"), [3])
        nuevo = parrafos(cargar_prompt("c-consejos-corte-riesgo"))[3]
        self.assertTrue(nuevo.startswith("Que el número no esté agendado pesa. Valen los consejos de siempre"))
        self.assertIn("cortar y llamar uno mismo al número oficial", nuevo)
        self.assertTrue(nuevo.endswith("Si OTRA va hacia alguno de esos pedidos, tenelo en cuenta en el riesgo, aunque la charla sea amable."))
        self.assertNotRegex(nuevo, r"\bDNI\b|nombre|dirección", "solo credenciales y actos sin vuelta atrás")

    def test_c_freno_cambia_solo_el_parrafo_de_lo_que_puede_pedir_una_legitima(self):
        self.assertEqual(self.cambiados("c-freno-corte-riesgo"), [5])
        nuevo = parrafos(cargar_prompt("c-freno-corte-riesgo"))[5]
        self.assertTrue(nuevo.startswith("El nombre, el DNI, la fecha de nacimiento, una dirección o un correo se juzgan por para qué los piden."))
        self.assertIn("eso solo no la vuelve una estafa", nuevo, "conserva el freno")

    def test_ninguna_pone_numeros_ni_ejemplos_de_los_casos(self):
        for v in VARIANTES:
            (i,) = self.cambiados(v)
            nuevo = parrafos(cargar_prompt(v))[i]
            self.assertNotRegex(nuevo, r"\d", f"{v}: sin números, no fuerza un valor")
            self.assertNotIn("«", nuevo, f"{v}: sin frases de ejemplo")


class TestCorren(_ConServidor):
    def test_cada_variante_corre_solo_otra_con_el_corte_y_el_motivo(self):
        for v in VARIANTES:
            with self.subTest(v):
                manifiesto, filas = correr_main("--modelos", "modelo-falso:1b", "--prompts", v, "--hablantes", "rol",
                                                "--casos", "SC-WA-CODE-01-e01", "--url", self.url, "--sin-reglas",
                                                "--solo-otra", "--seguir-tras-aviso")
                self.assertEqual(manifiesto["prompts"][v]["texto"], cargar_prompt(v))
                self.assertEqual(manifiesto["parametros_slm"]["corte_riesgo"]["num_predict"], 14)
                self.assertTrue(all(r["consulta"] == ("omitida" if r["hablante"] == "PROTEGIDA" else "") for r in filas))
                self.assertEqual(sum(bool(r["ms_etapa2"]) for r in filas), sum(r["aviso"] == "true" for r in filas))


# --- La regla de corridas/2026-11-10_revision-producto/analizar.py, sobre corridas sintéticas ---

def primera_de_otra(i: str, desde: int = 1) -> int | None:
    return next((n for n, l in enumerate(casos.con_roles(i, casos.cargar_texto(i)), 1) if n >= desde and l.hablante == "OTRA"), None)


ESTAFAS, LEGITIMAS = an.e3.ESTAFAS, an.e3.LEGITIMAS
# La base sintética avisa 30 estafas, 10 «no debería avisar» y 10 tolerables.
BASE_AV = {i: (primera_de_otra(i, an.REF[i].get("t_r_linea") or 1) if i in ESTAFAS[:30] else
               primera_de_otra(i) if i in an.NO_AVISAR[:10] or i in an.TOLERABLES[:10] else None) for i in an.IDS}


def escribir(datos: Path, carpeta: str, avisa: dict, **cambios) -> None:
    """Una corrida sintética en todas las líneas, solo OTRA: riesgo 0.3 desde la línea `avisa[caso]` y 0.1 antes."""
    prompt, lista = an.CORRIDAS[carpeta]
    ids = sorted(an.VISTA) if lista else an.IDS
    run = datos / carpeta / "2026-11-11_000000_sintetica"
    run.mkdir(parents=True)
    manifiesto = {
        "codigo": {"commit": "f" * 40, "cambios_sin_commit_en_la_carpeta": False}, "solo_otra": True,
        "modo_termino": "diagnostico-completo", "interrumpida": False, "particion": "desarrollo",
        **({"lista": lista} if lista else {}),
        "ollama": {"version": an.e3.OLLAMA, "digests": {an.e3.MODELO: "sha256:" + an.e3.DIGEST}},
        "parametros_slm": {"num_ctx": 4096, "seed": 42, "temperatura": 0.0, "corte_riesgo": {"num_predict": MAXIMO_TOKENS_CORTE_RIESGO}},
        "prompts": {prompt: {"texto": cargar_prompt(prompt), "esquema": esquema_de(prompt),
                             "etapa2": {"texto": cargar_prompt_motivo(PROMPT_MOTIVO_C), "esquema": ESQUEMA_MOTIVO}}},
        "casos": {i: huella((casos.DIR_TEXTO / f"{i}.txt").read_text(encoding="utf-8")) for i in ids},
    }
    manifiesto.update(cambios)
    (run / "manifiesto.json").write_text(json.dumps(manifiesto, ensure_ascii=False), encoding="utf-8")
    with (run / "actualizaciones.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=correr.COLUMNAS, extrasaction="ignore")
        w.writeheader()
        for i in ids:
            desde = avisa.get(i)
            for n, l in enumerate(casos.con_roles(i, casos.cargar_texto(i)), 1):
                otra, primera = l.hablante == "OTRA", n == desde
                alto = otra and desde is not None and n >= desde
                w.writerow({"detector": "slm", "prompt": prompt, "hablantes": "rol", "case_id": i, "linea": n,
                            "hablante": l.hablante, "texto": l.texto, "valida": "true", "consulta": "" if otra else "omitida",
                            "riesgo": (0.3 if alto else 0.1) if otra else "", "alerta_sugerida": str(alto).lower(),
                            "aviso": str(primera).lower(), "ms_etapa1": 210 if otra else "", "ms_etapa2": 680 if primera else "",
                            "motivo": "Puede ser una estafa" if primera else "", "evidencia": l.texto if primera else ""})


def escribir_todo(datos: Path, por_variante: dict[str, dict]) -> None:
    (datos / "humo").mkdir(parents=True)
    (datos / "humo" / "humo.json").write_text(json.dumps({p: {"lineas": 48, "leidas": 48, "igual_a_la_base": 45, "altos_03": 5,
                                                              "altos_06": 2, "errores": [], "pasa": True}
                                                          for p in [an.BASE, *an.VARIANTES.values()]}), encoding="utf-8")
    for carpeta in an.CORRIDAS:
        escribir(datos, carpeta, por_variante.get(carpeta.removesuffix("-rep"), BASE_AV))


def salida(datos: Path) -> str:
    texto = io.StringIO()
    with redirect_stdout(texto):
        an.main(["--datos", str(datos)])
    return texto.getvalue()


def con_mas(k: int, de: list[str], sobre: dict | None = None) -> dict:
    av = dict(sobre or BASE_AV)
    for i in [i for i in de if av[i] is None][:k]:
        av[i] = primera_de_otra(i)
    return av


def con_menos(k: int, de: list[str]) -> dict:
    av = dict(BASE_AV)
    for i in [i for i in de if av[i] is not None][:k]:
        av[i] = None
    return av


class TestRegla(unittest.TestCase):
    BASE = {"estafas": 30, "antes del pedido": 10, "a tiempo": 20, "antes del cumplimiento": 10, "FA estrictas": 10,
            "FA tolerables": 10, "FA cotidianas": 1, "FA dudosas": 19, "FA": 20}

    def con(self, **d):
        return {**self.BASE, **d}

    def test_veredicto_con_las_etiquetas_de_producto(self):
        b = self.BASE
        casos_ = [
            (self.con(estafas=33), self.con(estafas=33), "pasa por detección"),
            (self.con(**{"antes del cumplimiento": 13}), self.con(**{"antes del cumplimiento": 13}), "pasa por detección"),
            (self.con(estafas=32), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"a tiempo": 17}), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"FA estrictas": 13}), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"FA estrictas": 12}), self.con(estafas=33, **{"FA estrictas": 12}), "pasa por detección"),
            (self.con(estafas=33), self.con(estafas=32), "no pasa"),
            (self.con(estafas=33), self.con(estafas=33, **{"antes del pedido": 7}), "no pasa"),
            (self.con(estafas=33), self.con(estafas=33, **{"FA estrictas": 13}), "no pasa"),
            # Las tolerables no tienen tope, y las cotidianas de la anotación original no deciden en esta versión.
            (self.con(estafas=33, **{"FA tolerables": 18, "FA cotidianas": 9, "FA": 40}), self.con(estafas=33), "pasa por detección"),
            # Sin ganar en detección, pasa por FA si baja 3 o más las estrictas, también en la repetición.
            (self.con(**{"FA estrictas": 7}), self.con(**{"FA estrictas": 7}), "pasa por FA"),
            (self.con(**{"FA estrictas": 8}), self.con(**{"FA estrictas": 7}), "no pasa"),
            (self.con(**{"FA estrictas": 7}), self.con(**{"FA estrictas": 8}), "no pasa"),
            (self.con(**{"FA estrictas": 7, "estafas": 27}), self.con(**{"FA estrictas": 7}), "no pasa"),
        ]
        for c, cr, esperado in casos_:
            with self.subTest(c=c, cr=cr):
                self.assertEqual(an.veredicto(c, b, cr, b, "producto")[0], esperado)
        self.assertEqual(an.veredicto(self.con(estafas=33), b, None, b, "producto")[0], "no pasa", "sin repetición no pasa")

    def test_veredicto_con_la_anotacion_original(self):
        b = self.BASE
        casos_ = [
            (self.con(estafas=33, **{"FA estrictas": 30}), self.con(estafas=33), "pasa por detección"),
            (self.con(estafas=33, **{"FA cotidianas": 4}), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"FA cotidianas": 3}), self.con(estafas=33, **{"FA cotidianas": 3}), "pasa por detección"),
            (self.con(FA=17), self.con(FA=17), "pasa por FA"),
            (self.con(FA=18), self.con(FA=17), "no pasa"),
        ]
        for c, cr, esperado in casos_:
            with self.subTest(c=c, cr=cr):
                self.assertEqual(an.veredicto(c, b, cr, b, "original")[0], esperado)

    def test_si_pasan_varias(self):
        b = self.BASE
        cs = {"c-codigo": self.con(estafas=34, **{"FA estrictas": 12}), "c-consejos": self.con(estafas=33),  # +3, menos que +4
              "c-freno": self.con(estafas=34, **{"FA estrictas": 11})}
        todas = {v: ("pasa por detección", "") for v in cs}
        self.assertEqual(an.elegir(todas, cs, b, "producto"), "c-freno", "empatan en +4: la de menos FA estrictas")
        self.assertIsNone(an.elegir({v: ("no pasa", "") for v in cs}, cs, b, "producto"))
        # La detección va antes que las FA: una que pasa por FA no le gana a una que pasa por detección.
        self.assertEqual(an.elegir({"c-codigo": ("no pasa", ""), "c-consejos": ("pasa por detección", ""), "c-freno": ("pasa por FA", "")},
                                   cs, b, "producto"), "c-consejos")
        fa = {"c-codigo": self.con(**{"FA estrictas": 7}), "c-consejos": self.con(**{"FA estrictas": 6}), "c-freno": self.con(**{"FA estrictas": 6}, estafas=31)}
        self.assertEqual(an.elegir({v: ("pasa por FA", "") for v in fa}, fa, b, "producto"), "c-freno", "la que más baja; si empatan, la que más suma")

    def test_la_vista_las_etiquetas_y_las_cifras(self):
        self.assertEqual((len(an.NO_AVISAR), len(an.TOLERABLES), len(an.AVISAR)), (75, 18, 1))
        self.assertEqual((len(an.CODIGO_O_CLAVE), len(an.DATOS_PERSONALES)), (17, 6))
        self.assertEqual(an.DECIDE, "producto")
        c = an.cifras({i: primera_de_otra(i) for i in an.IDS})
        self.assertEqual((c["estafas"], c["FA estrictas"], c["FA tolerables"], c["debería avisar"], c["FA"], c["código o clave"]),
                         (46, 75, 18, 1, 94, 17))
        c = an.cifras(BASE_AV)
        self.assertEqual((c["estafas"], c["FA estrictas"], c["FA tolerables"], c["debería avisar"], c["FA"]), (30, 10, 10, 0, 20))

    def test_las_etiquetas_dicen_la_razon_y_cubren_las_94(self):
        self.assertEqual(sorted(an.ETIQUETAS), sorted(LEGITIMAS))
        for i, e in an.ETIQUETAS.items():
            self.assertIn(e["etiqueta"], ("no_avisar", "tolerable", "avisar"), i)
            self.assertTrue(e["razon"].strip() and e["intencion"], i)

    def test_de_punta_a_punta(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_todo(Path(tmp), {"c-codigo": con_mas(4, ESTAFAS)})
            texto = salida(Path(tmp))
        self.assertIn("### Versión «producto» (decide)", texto)
        self.assertIn("**Resultado: queda `c-codigo`.**", texto)
        self.assertIn("| `c-consejos` | no pasa |", texto)
        self.assertIn("Con esta versión: queda `c-codigo`.", texto)
        self.assertIn("### Estafas con pedido de código o clave (/17)", texto)

    def test_las_dos_versiones_pueden_decir_distinto(self):
        cotidianas = [i for i in an.NO_AVISAR if an.REF[i].get("tipo_legitima") == "cotidiana"]
        with tempfile.TemporaryDirectory() as tmp:
            # +4 estafas y +3 FA en tolerables: pasa con las etiquetas de producto; con la original también (no son cotidianas).
            escribir_todo(Path(tmp), {"c-codigo": con_mas(3, an.TOLERABLES, con_mas(4, ESTAFAS)),
                                      # +4 estafas y +3 FA en cotidianas «no debería avisar»: no pasa en ninguna versión.
                                      "c-consejos": con_mas(3, cotidianas, con_mas(4, ESTAFAS)),
                                      # sin ganar en detección, baja 3 FA estrictas: pasa por FA.
                                      "c-freno": con_menos(3, an.NO_AVISAR)})
            texto = salida(Path(tmp))
        self.assertIn("| `c-codigo` | pasa por detección |", texto)
        self.assertIn("| `c-consejos` | no pasa | suma 3 o más en FA estrictas", texto)
        self.assertIn("| `c-freno` | pasa por FA |", texto)
        self.assertIn("**Resultado: queda `c-codigo`.**", texto)

    def test_sin_ganancia_queda_la_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_todo(Path(tmp), {"c-codigo": con_mas(2, ESTAFAS), "c-freno": con_menos(2, an.NO_AVISAR)})
            self.assertIn("**Resultado: queda la base.**", salida(Path(tmp)))

    def test_el_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir(Path(tmp), "c-codigo", BASE_AV, solo_otra=False)
            self.assertIn("no corrió con --solo-otra", an.s.controlar("c-codigo", *an.e3.leer(Path(tmp), "c-codigo")))
        with tempfile.TemporaryDirectory() as tmp:
            escribir(Path(tmp), "base", BASE_AV, prompts={"c-json-corte-riesgo": {}})
            self.assertIn("el prompt no es el de c-premisa-corte-riesgo", an.s.controlar("base", *an.e3.leer(Path(tmp), "base")))


if __name__ == "__main__":
    unittest.main()
