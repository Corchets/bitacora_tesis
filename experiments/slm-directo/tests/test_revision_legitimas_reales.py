"""preparar_revision_legitimas_reales.py: fichas ciegas de las legítimas reales y su paso a etiquetas de producto.
Con un set ficticio en el formato de la custodia: los textos reales no están en el repo.

Uso (desde experiments/slm-directo):
    python3 -B -m unittest tests.test_revision_legitimas_reales -v
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
import preparar_revision_legitimas_reales as rev  # noqa: E402

IDS = [f"EXT-{n}" for n in (1056, 1103, 1296)]


def armar_set(base: Path) -> Path:
    """set-legitimas con tres llamadas y su manifiesto."""
    carpeta = base / "sets/set-legitimas"
    (carpeta / "texto").mkdir(parents=True)
    (carpeta / "referencia").mkdir()
    roles, manifiesto = {}, {}
    for n, cid in enumerate(IDS):
        (carpeta / "texto" / f"{cid}.txt").write_text(f"A: Hola, le hablo de la empresa {n}.\nB: <b>Sí</b>, dígame.\n",
                                                     encoding="utf-8")
        (carpeta / "referencia" / f"{cid}.json").write_text(json.dumps({"case_id": cid, "tipo_legitima": "cotidiana"}),
                                                          encoding="utf-8")
        roles[cid] = {"protegida": "B" if n else "A"}
        for k in (f"texto/{cid}.txt", f"referencia/{cid}.json"):
            manifiesto[k] = hashlib.sha256((carpeta / k).read_bytes()).hexdigest()
    (carpeta / "roles-protegida.json").write_text(json.dumps(roles), encoding="utf-8")
    ruta = base / "manifiesto.json"
    ruta.write_text(json.dumps(manifiesto), encoding="utf-8")
    return ruta


def ficha(etiqueta: str, linea: str = "") -> dict:
    return {"roles": "si", "legitima": "si", "intencion": "vender", "etiqueta": etiqueta, "pide": ["nada"],
            "motivo_roles": "", "motivo_legitima": "", "razon": " Ofrece un plan (l. 1). ", "observaciones": "",
            "etiqueta_linea": linea, "conocido": False, "completa": True}


class FichasTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.manifiesto = armar_set(self.base)
        self.privado = self.base / "private"
        self.muestra = rev.fichas(self.base / "sets", self.manifiesto, self.privado)
        self.clave = json.loads((self.privado / rev.CLAVE.name).read_text(encoding="utf-8"))
        self.html = (self.privado / rev.FORMULARIO.name).read_text(encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def datos(self) -> dict:
        bloque = self.html.split('<script type="application/json" id="data">', 1)[1].split("</script>", 1)[0]
        return json.loads(bloque)

    def test_el_formulario_es_ciego(self):
        for cid in IDS:
            self.assertNotIn(cid, self.html)
        self.assertNotIn("cotidiana", self.html)
        self.assertNotIn("<b>Sí</b>", self.html)  # el texto no entra como HTML
        self.assertEqual([c["id"] for c in self.datos()["casos"]], ["Llamada 01", "Llamada 02", "Llamada 03"])
        self.assertEqual(sorted(v["case_id"] for v in self.clave["casos"].values()), IDS)

    def test_roles_desde_protegida(self):
        for alias, v in self.clave["casos"].items():
            caso = next(c for c in self.datos()["casos"] if c["id"] == alias)
            primero = "PROTEGIDA" if v["protegida_original"] == "A" else "OTRA"
            self.assertEqual(caso["turnos"][0]["hablante"], primero)

    def test_no_reemplaza_una_entrega_distinta(self):
        self.assertEqual(rev.fichas(self.base / "sets", self.manifiesto, self.privado), self.muestra)
        (self.privado / rev.CLAVE.name).write_text("{}", encoding="utf-8")
        with self.assertRaises(ValueError):
            rev.fichas(self.base / "sets", self.manifiesto, self.privado)

    def test_un_texto_cambiado_no_pasa_el_manifiesto(self):
        (self.base / "sets/set-legitimas/texto/EXT-1056.txt").write_text("A: otra cosa\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            rev.fichas(self.base / "sets", self.manifiesto, self.base / "otro")

    def respuestas(self, cambios: dict) -> Path:
        r = {a: ficha("no_avisar") for a in self.clave["casos"]} | cambios
        ruta = self.base / "respuestas.json"
        ruta.write_text(json.dumps({"issue": rev.ISSUE, "version": 1, "muestra": self.muestra, "revisor": "Prueba",
                                    "exportado": "2026-11-21T10:00:00Z", "respuestas": r, "actual": 0}),
                        encoding="utf-8")
        return ruta

    def test_etiquetas_en_el_formato_de_la_revision_de_producto(self):
        datos = rev.etiquetas(self.respuestas({"Llamada 02": ficha("avisar", "2")}), self.privado / rev.CLAVE.name)
        self.assertEqual(sorted(datos["casos"]), IDS)
        cid = self.clave["casos"]["Llamada 02"]["case_id"]
        self.assertEqual(datos["casos"][cid]["etiqueta"], "avisar")
        self.assertEqual(datos["casos"][cid]["linea"], 2)
        self.assertEqual(datos["casos"][cid]["razon"], "Ofrece un plan (l. 1).")
        self.assertEqual(sum(v["etiqueta"] == "no_avisar" for v in datos["casos"].values()), 2)

    def test_etiquetas_exige_todas_las_fichas_completas(self):
        with self.assertRaisesRegex(ValueError, "Faltan 1"):
            rev.etiquetas(self.respuestas({"Llamada 03": ficha("no_avisar") | {"completa": False}}),
                          self.privado / rev.CLAVE.name)


if __name__ == "__main__":
    unittest.main()
