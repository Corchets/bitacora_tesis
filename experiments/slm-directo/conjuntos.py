"""Conjuntos de la evaluación final de #143: desarrollo, el test reservado, el set externo (#144) y las legítimas reales.

Un conjunto es una carpeta, fuera de casos/, con:
    conjunto.json     nombre, partición, de dónde sale cada parte (con su SHA-256) y la huella de cada texto
    texto/<id>.txt    solo los turnos «A: …» y «B: …», uno por línea: lo único que llega al detector
    roles.json        {id: {"protegida": "A" | "B"}}, para --hablantes rol; lo usa el circuito, no el detector
    referencia.json   {id: {clase, t_r_linea, t_c_linea, tipo_legitima, vista, …}}: la lee el análisis, nunca correr.py

`correr.py --conjunto CARPETA` corre sobre los textos y los roles sin abrir la referencia. Así el test reservado no
tiene que entrar en casos/ (en laboratorio-main, `casos.py` lo prohíbe) y el set externo usa el formato del
relevamiento (docs/corpus/RELEVAMIENTO-CORPUS-EXTERNO.md, §5.4).

Uso (desde experiments/slm-directo):
    python conjuntos.py preparar --destino DIR [--reserva CHECKOUT_DE_RESERVA_TEST] [--externo CARPETA]
                                 [--legitimas-reales CARPETA_SETS]
    python conjuntos.py validar DIR/test_reservado

`preparar` comprueba las huellas de cada fuente y escribe solo conteos: no imprime textos ni referencias.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import casos

RAIZ = Path(__file__).resolve().parent
# Dentro de un checkout con la reserva: desde el 2026-11-21, la raíz de este repo (ver casos/RESERVA-EN-ESTA-RAMA.md).
RESERVA_CASOS = Path("experiments") / "slm-directo" / "casos"
# SHA-256 de las fuentes de la reserva que no están en MANIFIESTO-CORPUS-V2.json. El del JSONL es el de
# TEST-ALCANCE.md (2026-11-07); el de alcance-reserva.json, el del commit 9089b19 de reserva/test.
SHA_LEGITIMAS_TEST = "94dc3a7f084c0aa9a9b2f17c586fbac3b5a1ed813d87697b5096f93eefc8bf34"
SHA_ALCANCE_RESERVA = "ce2101553c8ee6bafc9c87fcccd01c91b740cd995c49fb967f1dd58b001203b2"
PRINCIPAL = "principal"
# Huellas del set externo congelado de #144 (PR #181); los textos quedan en custodia, fuera de Git.
MANIFIESTO_EXTERNO = RAIZ.parents[1] / "docs" / "corpus" / "MANIFIESTO-144-SET-COREANO-2026-11-11.json"
# Legítimas reales de CallCenterEN (docs/investigacion/FUENTES-LEGITIMAS-REALES.md §8); desde el 2026-11-20, también en
# casos/externo/legitimas-reales.
MANIFIESTO_LEGITIMAS = RAIZ.parents[1] / "docs" / "corpus" / "MANIFIESTO-LEGITIMAS-REALES-2026-11-18.json"
MANIFIESTO_ZONA_GRIS = RAIZ.parents[1] / "docs" / "corpus" / "MANIFIESTO-ZONA-GRIS-MEDICARE-2026-11-18.json"
VISTA_ZONA_GRIS = "aparte: zona gris de Medicare (avisos, no son FA)"
CLASES = casos.CLASES
TIPOS_LEGITIMA = casos.TIPOS_LEGITIMA
# Lo que el análisis usa de cada referencia. El resto de la referencia original no se copia.
CAMPOS_REFERENCIA = ("clase", "t_r_linea", "t_c_linea", "pedido", "tipo_legitima", "dificultad", "familia", "grupo",
                     "alcance", "vista")
_LINEA = re.compile(r"^(A|B): (\S.*)$")


def sha256(datos: bytes) -> str:
    return hashlib.sha256(datos).hexdigest()


class Conjunto:
    """Un conjunto ya armado. Lee textos y roles; la referencia, solo si se la pide."""

    def __init__(self, carpeta: Path | str) -> None:
        self.carpeta = Path(carpeta).resolve()
        self.datos = json.loads((self.carpeta / "conjunto.json").read_text(encoding="utf-8"))
        self.nombre: str = self.datos["nombre"]
        self.particion: str = self.datos["particion"]
        self.ids: list[str] = sorted(self.datos["casos"])

    @property
    def ruta_roles(self) -> Path:
        return self.carpeta / "roles.json"

    def crudo(self, case_id: str) -> str:
        return (self.carpeta / "texto" / f"{case_id}.txt").read_text(encoding="utf-8")

    def cargar_texto(self, case_id: str) -> list[casos.Linea]:
        lineas = []
        for n, renglon in enumerate(self.crudo(case_id).splitlines(), start=1):
            m = _LINEA.match(renglon.rstrip())
            if not m:
                raise ValueError(f"{self.nombre}/{case_id}.txt línea {n}: no empieza con 'A: ' o 'B: '")
            lineas.append(casos.Linea(m.group(1), m.group(2)))
        return lineas

    def roles(self) -> dict:
        return json.loads(self.ruta_roles.read_text(encoding="utf-8"))

    def con_roles(self, case_id: str, lineas: list[casos.Linea]) -> list[casos.Linea]:
        protegida = self.roles()[case_id]["protegida"]
        return [casos.Linea("PROTEGIDA" if l.hablante == protegida else "OTRA", l.texto) for l in lineas]

    def referencia(self) -> dict:
        return json.loads((self.carpeta / "referencia.json").read_text(encoding="utf-8"))

    def validar(self, con_referencia: bool = True) -> list[str]:
        """Errores de formato, huellas o roles (lista vacía si está bien). Nunca incluye texto de los casos."""
        errores = []
        en_texto = sorted(p.stem for p in (self.carpeta / "texto").glob("*.txt"))
        if en_texto != self.ids:
            errores.append(f"{self.nombre}: texto/ no tiene exactamente los casos de conjunto.json")
        if self.particion not in casos.PARTICIONES | {"externo"}:
            errores.append(f"{self.nombre}: partición desconocida {self.particion!r}")
        try:
            roles = self.roles()
        except (OSError, ValueError) as e:
            return errores + [f"{self.nombre}: roles.json ilegible ({e})"]
        largos = {}
        for c in self.ids:
            ruta = self.carpeta / "texto" / f"{c}.txt"
            if not ruta.exists():
                continue
            if sha256(ruta.read_bytes()) != self.datos["casos"][c]:
                errores.append(f"{self.nombre}/{c}: el texto no coincide con su huella")
                continue
            try:
                largos[c] = len(self.cargar_texto(c))
            except ValueError as e:
                errores.append(str(e))
                continue
            if largos[c] < 2:
                errores.append(f"{self.nombre}/{c}: el diálogo necesita al menos 2 líneas")
            if (roles.get(c) or {}).get("protegida") not in ("A", "B"):
                errores.append(f"{self.nombre}/{c}: falta quién es PROTEGIDA en roles.json")
        if sorted(roles) != self.ids:
            errores.append(f"{self.nombre}: roles.json no tiene exactamente los casos del conjunto")
        if con_referencia and not errores:
            errores += validar_referencia(self.referencia(), largos, self.nombre)
        return errores


def validar_referencia(ref: dict, largos: dict[str, int], nombre: str) -> list[str]:
    """Errores de una referencia de conjunto; `largos` es id → cantidad de líneas."""
    errores = []
    if sorted(ref) != sorted(largos):
        return [f"{nombre}: referencia.json no tiene exactamente los casos del conjunto"]
    for c, r in sorted(ref.items()):
        n = largos[c]
        if r.get("clase") not in CLASES:
            errores.append(f"{nombre}/{c}: clase inválida")
            continue
        if not r.get("vista"):
            errores.append(f"{nombre}/{c}: falta la vista")
        t_r, t_c = r.get("t_r_linea"), r.get("t_c_linea")
        for campo, valor in (("t_r_linea", t_r), ("t_c_linea", t_c)):
            if valor is not None and not casos._es_linea(valor, n):
                errores.append(f"{nombre}/{c}: {campo} fuera del diálogo (1..{n})")
        if t_c is not None and (t_r is None or (casos._es_linea(t_r, n) and t_c <= t_r)):
            errores.append(f"{nombre}/{c}: t_c_linea requiere un t_r_linea anterior")
        if r["clase"] in casos.LEGITIMAS:
            if t_r is not None or t_c is not None:
                errores.append(f"{nombre}/{c}: una legítima no lleva t_r_linea ni t_c_linea")
            if r.get("tipo_legitima") is not None and r["tipo_legitima"] not in TIPOS_LEGITIMA:
                errores.append(f"{nombre}/{c}: tipo_legitima inválido")
    return errores


def _escribir(destino: Path, nombre: str, particion: str, textos: dict[str, str], roles: dict, referencia: dict,
              fuentes: dict) -> Conjunto:
    """Escribe el conjunto en destino/nombre (que no puede existir) y lo devuelve validado."""
    carpeta = destino / nombre
    if carpeta.exists():
        sys.exit(f"{carpeta} ya existe: borrala o elegí otro destino.")
    (carpeta / "texto").mkdir(parents=True)
    for c, texto in textos.items():
        (carpeta / "texto" / f"{c}.txt").write_text(texto, encoding="utf-8")
    datos = {"nombre": nombre, "particion": particion, "fuentes": fuentes,
             "casos": {c: sha256(t.encode("utf-8")) for c, t in sorted(textos.items())}}
    for archivo, contenido in (("conjunto.json", datos), ("roles.json", roles), ("referencia.json", referencia)):
        (carpeta / archivo).write_text(json.dumps(contenido, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                                       encoding="utf-8")
    conjunto = Conjunto(carpeta)
    errores = conjunto.validar()
    if errores:
        raise ValueError(f"{nombre} quedó mal armado:\n" + "\n".join(errores))
    return conjunto


def _ref(original: dict, **extra) -> dict:
    """Los campos de CAMPOS_REFERENCIA de una referencia de casos/, más los de `extra`."""
    salida = {k: original.get(k) for k in CAMPOS_REFERENCIA if k in original}
    salida.update(extra)
    return {k: salida.get(k) for k in CAMPOS_REFERENCIA}


def preparar_desarrollo(destino: Path) -> Conjunto:
    """Los 244 de desarrollo, con sus roles. Vista principal: alcance-140 (46 estafas de corpus_v2 y 94 legítimas
    entrantes); el resto, aparte por grupo."""
    ids = casos.ids_de_casos(particion="desarrollo")
    roles_todos = json.loads(casos.ROLES.read_text(encoding="utf-8"))
    alcance = {}
    for ruta in ("alcance-desarrollo.json", "alcance-legitimas-cotidianas.json"):
        datos = json.loads((RAIZ / "casos" / ruta).read_text(encoding="utf-8"))["casos"]
        alcance.update({c: d["alcance"] for c, d in datos.items()})
    vista_140 = set(_lista("alcance-140"))
    if not vista_140 <= set(ids):
        raise ValueError("alcance-140 tiene casos fuera de desarrollo")
    referencia = {}
    for c in ids:
        ref = casos.cargar_referencia(c)
        vista = PRINCIPAL if c in vista_140 else f"aparte: {ref['grupo']}"
        referencia[c] = _ref(ref, alcance=alcance.get(c), vista=vista)
    fuentes = {"casos": "experiments/slm-directo/casos (partición desarrollo)",
               "roles-protegida.json": sha256(casos.ROLES.read_bytes()),
               "alcance-140.txt": sha256((RAIZ / "casos" / "listas" / "alcance-140.txt").read_bytes())}
    return _escribir(destino, "desarrollo", "desarrollo",
                     {c: (casos.DIR_TEXTO / f"{c}.txt").read_text(encoding="utf-8") for c in ids},
                     {c: {"protegida": roles_todos[c]["protegida"]} for c in ids}, referencia, fuentes)


def _lista(nombre: str) -> list[str]:
    texto = (RAIZ / "casos" / "listas" / f"{nombre}.txt").read_text(encoding="utf-8")
    return [l.strip() for l in texto.splitlines() if l.strip() and not l.startswith("#")]


def preparar_test(reserva: Path, destino: Path, *, manifiesto: Path | None = None,
                  sha_legitimas: str = SHA_LEGITIMAS_TEST, sha_alcance: str = SHA_ALCANCE_RESERVA) -> Conjunto:
    """El test reservado desde un checkout con la reserva (la raíz del repo; antes, la rama reserva/test): los 200 CV2-T y las 56 legítimas entrantes (ENT-T).

    - Comprueba cada CV2-T contra las huellas de MANIFIESTO-CORPUS-V2.json de esta rama, y el JSONL de las 56 y
      alcance-reserva.json contra sus SHA-256.
    - Roles: los CV2-T, de alcance-reserva.json (anotado a ciegas, TEST-ALCANCE.md §1); las ENT-T, del JSONL.
    - Vista principal: las estafas CV2-T-V dentro del alcance y las 56 ENT-T. Aparte: las legítimas viejas CV2-T-L,
      dentro y fuera del alcance (TEST-ALCANCE.md, «Qué es»).
    Nunca entra a casos/ ni queda como desarrollo.
    """
    origen = Path(reserva).resolve() / RESERVA_CASOS
    man = json.loads((manifiesto or casos.MANIFIESTO).read_text(encoding="utf-8"))
    esperados = {c: h for c, h in man["casos"].items() if h.get("particion") == "test_reservado"}
    if not esperados:
        raise ValueError("el manifiesto no tiene casos de test_reservado")
    crudo_jsonl = (origen / "legitimas-entrantes-test.jsonl").read_bytes()
    crudo_alcance = (origen / "alcance-reserva.json").read_bytes()
    problemas = []
    if sha256(crudo_jsonl) != sha_legitimas:
        problemas.append("legitimas-entrantes-test.jsonl no coincide con su SHA-256")
    if sha256(crudo_alcance) != sha_alcance:
        problemas.append("alcance-reserva.json no coincide con su SHA-256")
    textos, referencias = {}, {}
    for c, h in sorted(esperados.items()):
        t, r = origen / "texto" / f"{c}.txt", origen / "referencia" / f"{c}.json"
        if not (t.exists() and r.exists()):
            problemas.append(f"{c}: falta en la reserva")
        elif sha256(t.read_bytes()) != h["texto_sha256"] or sha256(r.read_bytes()) != h["referencia_sha256"]:
            problemas.append(f"{c}: no coincide con MANIFIESTO-CORPUS-V2.json")
        else:
            textos[c], referencias[c] = t.read_text(encoding="utf-8"), json.loads(r.read_text(encoding="utf-8"))
    if problemas:
        raise ValueError("La reserva no es la congelada:\n" + "\n".join(problemas))
    alcance = json.loads(crudo_alcance)["casos"]
    if sorted(alcance) != sorted(textos):
        raise ValueError("alcance-reserva.json no cubre exactamente los casos del manifiesto")
    roles, referencia = {}, {}
    for c, ref in referencias.items():
        if ref.get("particion") != "test_reservado":
            raise ValueError(f"{c}: la referencia no dice test_reservado")
        dentro = alcance[c]["alcance"] == "dentro"
        if ref["clase"] == "vishing":
            vista = PRINCIPAL if dentro else "aparte: estafas de la reserva fuera del alcance"
        else:
            vista = f"aparte: legítimas viejas de la reserva, {'dentro' if dentro else 'fuera'} del alcance"
        roles[c] = {"protegida": alcance[c]["protegida"]}
        referencia[c] = _ref(ref, alcance=alcance[c]["alcance"], vista=vista)
    for renglon in crudo_jsonl.decode("utf-8").splitlines():
        if not renglon.strip():
            continue
        f = json.loads(renglon)
        c = f["case_id"]
        if c in textos:
            raise ValueError(f"{c} está repetido")
        if not isinstance(f["texto"], list) or not all(isinstance(x, str) for x in f["texto"]):
            raise ValueError(f"{c}: el texto del JSONL no es una lista de turnos")
        textos[c] = "\n".join(f["texto"]) + "\n"
        roles[c] = {"protegida": f["protegida"]}
        referencia[c] = {k: None for k in CAMPOS_REFERENCIA} | {
            "clase": "legitima", "tipo_legitima": f["tipo_legitima"], "dificultad": f["tipo_legitima"],
            "familia": f["familia"], "grupo": "legitimas_entrantes_test", "alcance": "dentro", "vista": PRINCIPAL}
    fuentes = {"MANIFIESTO-CORPUS-V2.json": sha256((manifiesto or casos.MANIFIESTO).read_bytes()),
               "legitimas-entrantes-test.jsonl": sha_legitimas, "alcance-reserva.json": sha_alcance}
    return _escribir(destino, "test_reservado", "test_reservado", textos, roles, referencia, fuentes)


def _leer_congelado(origen: Path, manifiesto: Path, que: str) -> tuple[list[str], dict, dict, dict, int]:
    """Lee una carpeta en el formato del set congelado (texto/, referencia/, roles-protegida.json) y comprueba cada
    texto y cada referencia contra el manifiesto. Sirve una parte del set: roles-protegida.json tiene que cubrir
    exactamente los textos presentes. Devuelve ids, textos, roles, referencias crudas y el total del manifiesto."""
    origen = Path(origen).resolve()
    man = json.loads(manifiesto.read_text(encoding="utf-8"))
    presentes = sorted(str(q.relative_to(origen)) for d in ("texto", "referencia") for q in (origen / d).glob("*"))
    ids = sorted(Path(k).stem for k in presentes if k.startswith("texto/"))
    roles_todos = json.loads((origen / "roles-protegida.json").read_text(encoding="utf-8"))
    problemas = [f"{k} no está en el manifiesto o no coincide" for k in presentes
                 if k not in man or sha256((origen / k).read_bytes()) != man[k]]
    problemas += [f"falta referencia/{c}.json" for c in ids if f"referencia/{c}.json" not in presentes]
    if sorted(roles_todos) != ids:
        problemas.append("roles-protegida.json no cubre exactamente los textos")
    if not ids or problemas:
        raise ValueError(f"{que} no es el congelado: " + ("; ".join(problemas) or "no hay textos"))
    textos = {c: (origen / "texto" / f"{c}.txt").read_text(encoding="utf-8") for c in ids}
    roles = {c: {"protegida": roles_todos[c]["protegida"]} for c in ids}
    crudas = {c: json.loads((origen / "referencia" / f"{c}.json").read_text(encoding="utf-8")) for c in ids}
    return ids, textos, roles, crudas, sum(k.startswith("texto/") for k in man)


def preparar_externo(origen: Path, destino: Path, *, manifiesto: Path | None = None) -> Conjunto:
    """El set externo de #144: estafas coreanas de KorCCVi, traducidas y marcadas.

    Formato del set congelado (experiments/laboratorio/armar_set_coreano.py): texto/EXT-NNN.txt,
    roles-protegida.json y referencia/EXT-NNN.json. Las 33 están en el repo desde el 2026-11-18
    (casos/externo/coreano); también sirve la carpeta de la custodia:
    cada texto y cada referencia se comprueban contra docs/corpus/MANIFIESTO-144-SET-COREANO-2026-11-11.json,
    y roles-protegida.json tiene que cubrir exactamente esos casos (en el repo es un recorte, con otro hash).
    Todo es estafa y va a la vista principal.
    """
    ids, textos, roles, crudas, total = _leer_congelado(origen, manifiesto or MANIFIESTO_EXTERNO, "El set externo")
    referencia = {c: {k: crudas[c].get(k) for k in CAMPOS_REFERENCIA} | {"alcance": "dentro", "vista": PRINCIPAL}
                  for c in ids}
    fuentes = {"MANIFIESTO-144-SET-COREANO": sha256((manifiesto or MANIFIESTO_EXTERNO).read_bytes()),
               "casos": f"{len(ids)} de {total} del set congelado"}
    return _escribir(destino, "externo", "externo", textos, roles, referencia, fuentes)


def preparar_legitimas_reales(origen: Path, destino: Path, *, manifiesto_legitimas: Path | None = None,
                              manifiesto_zona_gris: Path | None = None) -> Conjunto:
    """Las llamadas salientes reales de CallCenterEN, desde la carpeta `sets/` de la custodia o desde
    casos/externo/legitimas-reales (publicadas el 2026-11-20 aunque la fuente prohíbe redistribuir). Ver docs/investigacion/FUENTES-LEGITIMAS-REALES.md §8.

    - `set-legitimas`: 33 legítimas de telecomunicaciones; vista principal, cuentan como FA.
    - `set-zona-gris`: 42 de Medicare (seguros y equipamiento médico) que ningún anotador marcó legítimas; van a una
      vista aparte y no cuentan como FA ni como estafa. `legitima_dificil` es solo para que el formato valide.
    Cada archivo se comprueba contra su manifiesto en docs/corpus/.
    """
    origen = Path(origen).resolve()
    textos, roles, referencia, fuentes = {}, {}, {}, {}
    for sub, man, vista, etiqueta in (
            ("set-legitimas", manifiesto_legitimas or MANIFIESTO_LEGITIMAS, PRINCIPAL, "MANIFIESTO-LEGITIMAS-REALES"),
            ("set-zona-gris", manifiesto_zona_gris or MANIFIESTO_ZONA_GRIS, VISTA_ZONA_GRIS,
             "MANIFIESTO-ZONA-GRIS-MEDICARE")):
        ids, t, r, crudas, total = _leer_congelado(origen / sub, man, sub)
        if set(ids) & set(textos):
            raise ValueError("set-legitimas y set-zona-gris repiten casos")
        textos.update(t)
        roles.update(r)
        for c in ids:
            referencia[c] = {k: crudas[c].get(k) for k in CAMPOS_REFERENCIA} | {"alcance": "dentro", "vista": vista}
        fuentes[etiqueta] = sha256(man.read_bytes())
        fuentes[sub] = f"{len(ids)} de {total}"
    return _escribir(destino, "legitimas_reales", "externo", textos, roles, referencia, fuentes)


def resumen(conjunto: Conjunto) -> str:
    """Conteos por vista y clase: nada de texto."""
    ref = conjunto.referencia()
    conteo = Counter((r["vista"], r["clase"]) for r in ref.values())
    partes = [f"{conjunto.nombre}: {len(conjunto.ids)} casos"]
    partes += [f"  {vista} · {clase}: {n}" for (vista, clase), n in sorted(conteo.items())]
    return "\n".join(partes)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="orden", required=True)
    pp = sub.add_parser("preparar", help="arma los conjuntos en --destino")
    pp.add_argument("--destino", type=Path, required=True)
    pp.add_argument("--reserva", type=Path, help="raíz de un checkout con la reserva, hoy este repo (sin esto, no arma el test)")
    pp.add_argument("--externo", type=Path, help="carpeta de la custodia de #144 (sin esto, no arma el externo)")
    pp.add_argument("--legitimas-reales", type=Path,
                    help="casos/externo/legitimas-reales o la carpeta sets/ de la custodia (sin esto, no arma ese conjunto)")
    pv = sub.add_parser("validar", help="valida un conjunto ya armado")
    pv.add_argument("carpeta", type=Path)
    args = p.parse_args(argv)
    if args.orden == "validar":
        errores = Conjunto(args.carpeta).validar()
        print("\n".join(errores) or f"OK: {resumen(Conjunto(args.carpeta))}")
        return 1 if errores else 0
    args.destino.mkdir(parents=True, exist_ok=True)
    armados = [preparar_desarrollo(args.destino)]
    if args.reserva:
        armados.append(preparar_test(args.reserva, args.destino))
    if args.externo:
        armados.append(preparar_externo(args.externo, args.destino))
    if args.legitimas_reales:
        armados.append(preparar_legitimas_reales(args.legitimas_reales, args.destino))
    for c in armados:
        print(resumen(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
