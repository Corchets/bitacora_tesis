"""Prueba de sensibilidad de #143 (corridas/2026-11-10_sensibilidad-c/): tres variantes de C, con un solo cambio cada
una, cortadas tras el riesgo como la configuración congelada. Sin modelo: contra el Ollama falso de la humo.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_sensibilidad_143 -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tests"))

from detectores import DIR_PROMPTS, ESQUEMA_SALIDA, PROMPTS_CORTE_RIESGO, cargar_prompt, esquema_de  # noqa: E402
from test_config_congelada_143 import _ConServidor, correr_main  # noqa: E402

VARIANTES = ("c-ancla-corte-riesgo", "c-premisa-corte-riesgo", "c-sin-freno-corte-riesgo")


def parrafos(texto: str) -> list[str]:
    return texto.strip().split("\n\n")


class TestUnSoloCambio(unittest.TestCase):
    def setUp(self):
        self.tarea = parrafos((DIR_PROMPTS / "tarea_c.txt").read_text(encoding="utf-8"))
        self.salida = (DIR_PROMPTS / "salida_json_c.txt").read_text(encoding="utf-8").strip()
        self.base = cargar_prompt("c-json-corte-riesgo")

    def test_registradas_como_la_configuracion_congelada(self):
        self.assertEqual(PROMPTS_CORTE_RIESGO, {"c-json-corte-riesgo", *VARIANTES})
        for v in VARIANTES:
            self.assertEqual(esquema_de(v), ESQUEMA_SALIDA, v)

    def test_c_ancla_solo_ancla_la_definicion_del_riesgo(self):
        ancla = (DIR_PROMPTS / "salida_json_c_ancla.txt").read_text(encoding="utf-8").strip().split("\n")
        original = self.salida.split("\n")
        self.assertEqual([i for i, (x, y) in enumerate(zip(original, ancla)) if x != y], [1], "solo la línea del riesgo")
        self.assertEqual(len(ancla), len(original))
        self.assertTrue(ancla[1].startswith(original[1] + " Si OTRA ya está llevando a PROTEGIDA"))
        self.assertIn("el riesgo es 0.7 o más", ancla[1])
        self.assertEqual(cargar_prompt("c-ancla-corte-riesgo"), self.base.replace(original[1], ancla[1]))

    def test_c_premisa_agrega_un_parrafo_despues_del_armado_de_la_estafa(self):
        premisa = parrafos(cargar_prompt("c-premisa-corte-riesgo"))
        base = parrafos(self.base)
        self.assertEqual(premisa[:3] + premisa[4:], base)
        self.assertTrue(premisa[2].startswith("Una estafa telefónica suele armarse así"))
        self.assertTrue(premisa[3].startswith("Que el número no esté agendado pesa"))
        self.assertNotRegex(premisa[3], r"\d", "sin números: no fuerza un valor")

    def test_c_sin_freno_saca_solo_el_parrafo_de_lo_que_puede_pedir_una_legitima(self):
        sin_freno = parrafos(cargar_prompt("c-sin-freno-corte-riesgo"))
        base = parrafos(self.base)
        (quitado,) = [p for p in base if p not in sin_freno]
        self.assertTrue(quitado.startswith("Una llamada legítima también puede pedir el nombre, el DNI"))
        self.assertEqual([p for p in base if p != quitado], sin_freno)


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


# --- La regla de corridas/2026-11-10_sensibilidad-c/analizar.py, sobre corridas sintéticas ---
import csv  # noqa: E402
import importlib.util  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import tempfile  # noqa: E402
from contextlib import redirect_stdout  # noqa: E402

import casos  # noqa: E402
import correr  # noqa: E402
from detectores import ESQUEMA_MOTIVO, MAXIMO_TOKENS_CORTE_RIESGO, PROMPT_MOTIVO_C, cargar_prompt_motivo, huella  # noqa: E402

_spec = importlib.util.spec_from_file_location("analizar_sensibilidad", RAIZ / "corridas" / "2026-11-10_sensibilidad-c" / "analizar.py")
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)


def primera_de_otra(i: str, desde: int = 1) -> int | None:
    return next((n for n, l in enumerate(casos.con_roles(i, casos.cargar_texto(i)), 1) if n >= desde and l.hablante == "OTRA"), None)


BASE_AV = {i: (primera_de_otra(i, an.REF[i].get("t_r_linea") or 1) if i in an.e3.ESTAFAS[:30] else
               primera_de_otra(i) if i in an.DUDOSAS[:20] else None) for i in an.IDS}


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


def mas_estafas(k: int) -> dict:
    av = dict(BASE_AV)
    for i in [i for i in an.e3.ESTAFAS if BASE_AV[i] is None][:k]:
        av[i] = primera_de_otra(i)
    return av


class TestRegla(unittest.TestCase):
    BASE = {"estafas": 30, "antes del pedido": 10, "a tiempo": 20, "antes del cumplimiento": 10, "FA cotidianas": 0,
            "FA dudosas": 20, "FA": 20}

    def con(self, **d):
        return {**self.BASE, **d}

    def test_veredicto(self):
        b = self.BASE
        casos_ = [
            (self.con(estafas=33), self.con(estafas=33), "pasa"),
            (self.con(**{"antes del cumplimiento": 13}), self.con(**{"antes del cumplimiento": 13}), "pasa"),
            (self.con(estafas=32), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"a tiempo": 17}), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"FA cotidianas": 3}), self.con(estafas=33), "no pasa"),
            (self.con(estafas=33, **{"FA cotidianas": 2}), self.con(estafas=33, **{"FA cotidianas": 2}), "pasa"),
            (self.con(estafas=33), self.con(estafas=32), "no pasa"),
            (self.con(estafas=33), self.con(estafas=33, **{"antes del pedido": 7}), "no pasa"),
            (self.con(estafas=33), self.con(estafas=33, **{"FA cotidianas": 3}), "no pasa"),
            (self.con(estafas=33, **{"FA dudosas": 31}), self.con(estafas=33), "decide Mateo"),
            (self.con(estafas=33), self.con(estafas=33, **{"FA dudosas": 31}), "decide Mateo"),
            (self.con(estafas=33, **{"FA dudosas": 30}), self.con(estafas=33, **{"FA dudosas": 30}), "pasa"),
        ]
        for c, cr, esperado in casos_:
            with self.subTest(c=c, cr=cr):
                self.assertEqual(an.veredicto(c, b, cr, b)[0], esperado)
        self.assertEqual(an.veredicto(self.con(estafas=33), b, None, b)[0], "no pasa", "sin repetición no pasa")

    def test_si_pasan_varias_la_que_mas_suma_y_despues_la_de_menos_fa(self):
        b = self.BASE
        cs = {"c-ancla": self.con(estafas=34, FA=30), "c-premisa": self.con(estafas=33),  # +3, menos que +4
              "c-sin-freno": self.con(estafas=34, FA=25)}
        res = {v: ("pasa", "") for v in cs}
        self.assertEqual(an.elegir(res, cs, b), "c-sin-freno")
        self.assertIsNone(an.elegir({v: ("no pasa", "") for v in cs}, cs, b))
        self.assertEqual(an.elegir({**res, "c-sin-freno": ("decide Mateo", "")}, cs, b), "c-ancla")

    def test_la_vista_y_las_cifras(self):
        self.assertEqual((len(an.COTIDIANAS), len(an.DUDOSAS), len(an.CON_TC)), (29, 65, 15))
        c = an.cifras({i: primera_de_otra(i) for i in an.IDS})
        self.assertEqual((c["estafas"], c["FA cotidianas"], c["FA dudosas"], c["FA"]), (46, 29, 65, 94))

    def test_de_punta_a_punta(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_todo(Path(tmp), {"c-ancla": mas_estafas(4)})
            texto = salida(Path(tmp))
        self.assertIn("**Resultado: queda `c-ancla`.**", texto)
        self.assertIn("| `c-premisa` | no pasa |", texto)

    def test_sin_ganancia_queda_la_base(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir_todo(Path(tmp), {"c-ancla": mas_estafas(2)})
            self.assertIn("**Resultado: queda la base.**", salida(Path(tmp)))

    def test_el_control(self):
        with tempfile.TemporaryDirectory() as tmp:
            escribir(Path(tmp), "c-ancla", BASE_AV, solo_otra=False)
            self.assertIn("no corrió con --solo-otra", an.controlar("c-ancla", *an.e3.leer(Path(tmp), "c-ancla")))
        with tempfile.TemporaryDirectory() as tmp:
            escribir(Path(tmp), "c-ancla", BASE_AV, prompts={an.BASE: {}})
            self.assertIn("el prompt no es el de c-ancla-corte-riesgo", an.controlar("c-ancla", *an.e3.leer(Path(tmp), "c-ancla")))
        with tempfile.TemporaryDirectory() as tmp:
            escribir(Path(tmp), "base-rep", BASE_AV, lista=None)
            problemas = an.controlar("base-rep", *an.e3.leer(Path(tmp), "base-rep"))
            self.assertTrue(any("lista" in p for p in problemas), problemas)
