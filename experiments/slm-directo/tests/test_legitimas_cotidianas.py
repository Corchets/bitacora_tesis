"""Legítimas cotidianas: listas por lote para la etapa 2 de #143, roles y anotación a ciegas del alcance."""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import casos  # noqa: E402
import correr  # noqa: E402

ALCANCE = casos.RAIZ / "casos" / "alcance-legitimas-cotidianas.json"
# Lista: (prefijo de los case_id, cantidad). La etapa 2 de #143 informa por lote.
LOTES = {
    "legitimas-leg-21": ("LEG-", 21),
    "legitimas-leg2-28": ("LEG2-", 28),
    "legitimas-ent-l-42": ("ENT-L-", 42),
    "legitimas-seleccion-3": ("ENT-L-SELECCION-", 3),
}


def elegir(**opciones) -> list[str]:
    """Los casos que correría `correr.py` con esas opciones, sin correr nada."""
    args = argparse.Namespace(casos="", lista="", grupo=None, particion="desarrollo")
    vars(args).update(opciones)
    return correr.elegir_casos(args)


class Listas(unittest.TestCase):
    def test_cada_lote_tiene_su_prefijo_y_su_cantidad(self):
        for nombre, (prefijo, cantidad) in LOTES.items():
            ids = elegir(lista=nombre)
            self.assertEqual(len(ids), cantidad, nombre)
            self.assertTrue(all(c.startswith(prefijo) for c in ids), nombre)
        self.assertFalse([c for c in elegir(lista="legitimas-ent-l-42") if c.startswith("ENT-L-SELECCION-")])

    def test_las_91_son_los_tres_lotes_de_evaristo(self):
        tres = elegir(lista="legitimas-leg-21,legitimas-leg2-28,legitimas-ent-l-42")
        self.assertEqual(len(tres), 91)
        self.assertEqual(sorted(elegir(lista="legitimas-91")), sorted(tres))

    def test_las_listas_cubren_el_grupo_sin_repetir(self):
        todas = [c for nombre in LOTES for c in elegir(lista=nombre)]
        self.assertEqual(len(todas), len(set(todas)))
        self.assertEqual(sorted(todas), sorted(elegir(grupo="legitimas_cotidianas")))

    def test_todas_tienen_roles(self):
        for c in elegir(grupo="legitimas_cotidianas"):
            self.assertEqual({l.hablante for l in casos.con_roles(c, casos.cargar_texto(c))}, {"PROTEGIDA", "OTRA"}, c)


class Alcance(unittest.TestCase):
    def setUp(self):
        self.datos = json.loads(ALCANCE.read_text(encoding="utf-8"))

    def test_cubre_exactamente_el_grupo(self):
        self.assertEqual(sorted(self.datos["casos"]), sorted(elegir(grupo="legitimas_cotidianas")))

    def test_sigue_la_regla_y_el_conteo(self):
        for c, a in self.datos["casos"].items():
            self.assertIn(a["inicia"], {"otra", "protegida", "no_se_sabe"}, c)
            self.assertIn(a["numero"], {"agendado", "no_agendado"}, c)
            if a["inicia"] == "no_se_sabe":
                esperado = "dudoso"
            elif a["inicia"] == "protegida" or a["numero"] == "agendado":
                esperado = "fuera"
            else:
                esperado = "dentro"
            self.assertEqual(a["alcance"], esperado, c)
            self.assertTrue(a["evidencia"].startswith("L"), c)
        conteo = Counter(a["alcance"] for a in self.datos["casos"].values())
        self.assertEqual(self.datos["_meta"]["conteo"], dict(sorted(conteo.items())))


if __name__ == "__main__":
    unittest.main()
