"""Reranker zero-shot (rama reranker-prueba): contrato del detector y análisis, sin modelos ni red."""

import csv
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analisis" / "2026-10-30-reranker-zero-shot"))

import analizar  # noqa: E402
import casos  # noqa: E402
import correr  # noqa: E402
from casos import Linea  # noqa: E402
from reranker import (  # noqa: E402
    DetectorReranker,
    PuntuadorFalso,
    armar_ventana,
    backend_de,
    cargar_hipotesis,
)

HIPOTESIS = {
    "REQUEST_AUTH_CODE": ["pide codigo", "solicita codigo"],
    "REQUEST_TRANSFER": ["pide plata"],
    "AUTHORITY_CLAIM": ["dice ser banco"],
}


class PuntuadorGuion:
    """Puntaje fijo por hipótesis; registra cada ventana que recibe."""

    def __init__(self, puntajes: dict[str, float], fallar: bool = False) -> None:
        self.puntajes, self.fallar, self.ventanas = puntajes, fallar, []

    def preparar(self) -> dict:
        return {"backend": "guion", "modelo": "guion", "revision": "", "carga_ms": 0.0}

    def contar_tokens(self, texto: str) -> int:
        return len(texto.split())

    def puntuar(self, pares):
        if self.fallar:
            raise RuntimeError("se cayó")
        self.ventanas += [v for _, v in pares]
        return [self.puntajes.get(h, 0.0) for h, _ in pares]

    def liberar(self) -> None:
        pass


LINEAS = [Linea("A", f"linea {i} palabra palabra palabra") for i in range(1, 8)]


class TestVentana(unittest.TestCase):
    def test_toma_solo_las_ultimas_lineas_disponibles(self):
        texto, info = armar_ventana(LINEAS[:5], 3, 1000)
        self.assertEqual(texto.splitlines(), [f"A: {LINEAS[i].texto}" for i in (2, 3, 4)])
        self.assertEqual(info, {"lineas": 3, "lineas_recortadas": 0, "palabras_recortadas": 0})

    def test_recorta_por_la_izquierda_y_conserva_lo_reciente(self):
        texto, info = armar_ventana(LINEAS, 4, 12)
        self.assertTrue(texto.endswith(LINEAS[-1].texto.strip()))
        self.assertGreater(info["lineas_recortadas"], 0)
        self.assertNotIn("linea 4", texto)

    def test_una_linea_larga_pierde_el_comienzo_no_el_final(self):
        larga = [Linea("B", "uno dos tres cuatro cinco seis siete ocho dígame el código")]
        texto, info = armar_ventana(larga, 4, 5)
        self.assertTrue(texto.startswith("… "))
        self.assertTrue(texto.endswith("dígame el código"))
        self.assertGreater(info["palabras_recortadas"], 0)


class TestDetector(unittest.TestCase):
    def test_riesgo_es_el_maximo_de_los_pedidos_promediando_parafrasis(self):
        p = PuntuadorGuion({"pide codigo": 0.9, "solicita codigo": 0.5, "pide plata": 0.6, "dice ser banco": 0.99})
        r = DetectorReranker(p, HIPOTESIS, umbral=0.65).evaluar(LINEAS[:2])
        self.assertTrue(r.valida)
        self.assertAlmostEqual(r.riesgo, 0.7)  # (0.9 + 0.5) / 2; la maniobra 0.99 no cuenta
        self.assertTrue(r.alerta_sugerida)
        self.assertTrue(r.motivo.startswith("REQUEST_AUTH_CODE"))
        crudo = json.loads(r.crudo)
        self.assertEqual(crudo["puntajes"]["AUTHORITY_CLAIM"], 0.99)
        self.assertEqual(r.evidencia, LINEAS[1].texto)

    def test_umbral_estricto(self):
        p = PuntuadorGuion({"pide plata": 0.5})
        r = DetectorReranker(p, {"REQUEST_TRANSFER": ["pide plata"]}, umbral=0.5).evaluar(LINEAS[:1])
        self.assertFalse(r.alerta_sugerida, "0.5 no supera 0.5, igual que acumular.py")

    def test_fallo_del_modelo_es_fallo_no_legitimidad(self):
        r = DetectorReranker(PuntuadorGuion({}, fallar=True), HIPOTESIS).evaluar(LINEAS[:1])
        self.assertFalse(r.valida)
        self.assertIn("se cayó", r.error)
        self.assertIsNone(r.riesgo)

    def test_puntaje_no_finito_es_fallo(self):
        r = DetectorReranker(PuntuadorGuion({"pide plata": float("nan")}), {"REQUEST_TRANSFER": ["pide plata"]}).evaluar(LINEAS[:1])
        self.assertFalse(r.valida)

    def test_nunca_ve_lineas_futuras(self):
        p = PuntuadorGuion({})
        d = DetectorReranker(p, {"REQUEST_TRANSFER": ["pide plata"]}, ventana=10, max_tokens=1000)
        filas = list(correr.procesar_caso(d, LINEAS, detener_en_aviso=False))
        self.assertEqual(len(filas), len(LINEAS))
        for n, ventana in enumerate(p.ventanas, start=1):
            self.assertIn(LINEAS[n - 1].texto.strip(), ventana)
            for futura in LINEAS[n:]:
                self.assertNotIn(futura.texto.strip(), ventana)

    def test_puntuador_falso_es_determinista(self):
        pares = [("Una de las personas le pide el código de verificación", "B: dictame el codigo de verificacion")]
        self.assertEqual(PuntuadorFalso().puntuar(pares), PuntuadorFalso().puntuar(pares))
        self.assertGreater(PuntuadorFalso().puntuar(pares)[0], 0)


class TestHipotesisYBackends(unittest.TestCase):
    def test_archivo_tiene_seis_pedidos_y_seis_maniobras(self):
        pedidos, _ = cargar_hipotesis("pedidos")
        todas, _ = cargar_hipotesis("todas")
        self.assertEqual(sorted(pedidos), sorted(casos.PEDIDOS))
        self.assertEqual(len(todas), 12)
        self.assertTrue(all(len(p) == 2 for p in todas.values()))

    def test_backend_por_nombre(self):
        self.assertEqual(backend_de("MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7"), "nli")
        self.assertEqual(backend_de("BAAI/bge-reranker-v2-m3"), "cross-encoder")
        self.assertEqual(backend_de("Qwen/Qwen3-Reranker-0.6B"), "qwen3-reranker")
        self.assertEqual(backend_de("otro/modelo", "nli"), "nli")
        with self.assertRaises(ValueError):
            backend_de("otro/modelo")


class TestCorrida(unittest.TestCase):
    def test_solo_reranker_registra_cada_linea_y_el_manifiesto(self):
        caso = "SC-WA-CODE-01-e01"
        with tempfile.TemporaryDirectory() as tmp, redirect_stdout(io.StringIO()):
            correr.main(["--solo-reranker", "--reranker", "falso", "--seguir-tras-aviso", "--casos", caso, "--salida", tmp])
            (carpeta,) = Path(tmp).iterdir()
            manifiesto = json.loads((carpeta / "manifiesto.json").read_text(encoding="utf-8"))
            with (carpeta / "actualizaciones.csv").open(encoding="utf-8-sig") as f:
                filas = list(csv.DictReader(f))
        self.assertEqual(len(filas), len(casos.cargar_texto(caso)))
        self.assertEqual({f["detector"] for f in filas}, {"reranker"})
        self.assertEqual(manifiesto["modo_termino"], correr.MODO_DIAGNOSTICO)
        self.assertEqual(manifiesto["reranker"]["etiquetas"], "pedidos")
        self.assertIn("falso", manifiesto["reranker"]["modelos"])
        self.assertIsNone(manifiesto["ollama"])
        self.assertTrue(all(json.loads(f["crudo"])["puntajes"] for f in filas))

    def test_solo_reranker_sin_modelo_se_rechaza(self):
        with self.assertRaises(SystemExit):
            correr.main(["--solo-reranker"])


def _ref(clase, t_r=None, t_c=None, tipo=None):
    return {"clase": clase, "t_r_linea": t_r, "t_c_linea": t_c, "tipo_legitima": tipo, "pedido": "REQUEST_AUTH_CODE"}


def _filas(detector, riesgos, alertas=None):
    alertas = alertas or [False] * len(riesgos)
    return [{"detector": detector, "valida": "true", "riesgo": str(r), "alerta_sugerida": "true" if a else "false",
             "crudo": json.dumps({"puntajes": {"REQUEST_AUTH_CODE": r, "AUTHORITY_CLAIM": 0.95}})}
            for r, a in zip(riesgos, alertas)]


class TestAnalisis(unittest.TestCase):
    def test_la_seleccion_nunca_toca_el_informe_ni_sus_relacionados(self):
        seleccion, informe = analizar.splits()
        datos = json.loads(analizar.PARTICIONES.read_text(encoding="utf-8"))
        relacionados = {c["case_id"] for c in datos["conversaciones"] if c["particion_preparacion"] == "excluido_relacion_comparacion"}
        self.assertEqual(len(seleccion), 57)
        self.assertEqual(len(informe), 20)
        self.assertFalse(set(seleccion) & (set(informe) | relacionados))
        lista = correr.leer_lista("seleccion-57")
        self.assertEqual(sorted(lista), seleccion, "la lista para correr es la misma selección")
        self.assertEqual(sorted(correr.leer_lista("rapida-20")), informe)

    def test_un_archivo_que_cruza_selección_e_informe_se_rechaza(self):
        with tempfile.TemporaryDirectory() as tmp:
            ruta = Path(tmp) / "p.json"
            ruta.write_text(json.dumps({"evaluacion_ids": ["X"], "conversaciones": [
                {"case_id": "X", "particion_preparacion": "validacion"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                analizar.splits(ruta)

    def test_politicas_acumuladas(self):
        r = [0.9, 0.1, 0.9, 0.9]
        self.assertEqual(analizar.primero(analizar.estados("umbral > 0.5", r, [])), 1)
        self.assertEqual(analizar.primero(analizar.estados("2 seguidas > 0.5", r, [])), 4)
        self.assertEqual(analizar.primero(analizar.estados("ema 0.5 > 0.6", r, [])), 4)

    def test_verificador_y_filtro(self):
        refs = {"V": _ref("vishing", t_r=3, t_c=5), "L": _ref("legitima", tipo="mencion_sin_pedido")}
        datos = {
            "slm|m|tarea|ab": {"V": _filas("slm", [0.2, 0.9, 0.9, 0.9], [False, True, True, True]),
                                "L": _filas("slm", [0.9, 0.1, 0.1, 0.1], [True, False, False, False])},
            "reranker|r|pedidos|v4": {"V": _filas("reranker", [0.1, 0.2, 0.95, 0.95]),
                                      "L": _filas("reranker", [0.2, 0.1, 0.1, 0.1])},
        }
        ver = analizar.rol_verificador(datos, ["V", "L"], [], refs)["slm|m|tarea|ab"][2]
        nombre, sel, _, avisos = next(x for x in ver if x[0] == "alerta del modelo ∧ r > 0.9")
        self.assertEqual(avisos, {"V": 3, "L": None}, "el veto saca la FA y espera a que el reranker confirme")
        self.assertEqual((sel["tp"], sel["fp"], sel["temprano"]), (1, 0, 1))
        fil = analizar.rol_filtro(datos, ["V", "L"], [], refs)["slm|m|tarea|ab"][2]
        _, sel, _, avisos = next(x for x in fil if x[0] == "r (pedidos) > 0.9 → alerta del modelo")
        self.assertEqual(avisos, {"V": 3, "L": None}, "antes de derivar el SLM no se consulta")
        self.assertEqual(sel["evitadas"], (2 + 4, 8))


if __name__ == "__main__":
    unittest.main()
