"""Carga y valida los casos de prueba del ensayo #50.

Cada caso tiene dos archivos con el mismo nombre (ver casos/README.md):
- casos/texto/<id>.txt: lo único que puede llegar al detector.
- casos/referencia/<id>.json: la referencia humana; el detector nunca la recibe.

Uso:
    python casos.py            valida todos los casos
    python casos.py --listar   valida y muestra la tabla de casos
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
DIR_TEXTO = RAIZ / "casos" / "texto"
DIR_REFERENCIA = RAIZ / "casos" / "referencia"
CATALOGO = RAIZ.parents[1] / "docs" / "corpus" / "CATALOGO-ESCENARIOS.csv"
MANIFIESTO = RAIZ / "casos" / "MANIFIESTO-CORPUS-V2.json"

LEGITIMAS = {"legitima", "legitima_dificil"}
CLASES = {"vishing"} | LEGITIMAS
GRUPOS = {"piloto_escrito", "trampa", "laboratorio", "corpus_v2"}
PARTICIONES = {"desarrollo", "test_reservado"}
FAMILIAS = {"banco", "whatsapp", "soporte", "organismo_previsional", "premio",
            "familiar", "trabajo", "delivery", "medico", "escuela"}
TIPOS_LEGITIMA = {"cotidiana", "pedido_razonable", "mencion_sin_pedido"}
CAMPOS_V2 = {"particion", "familia", "dificultad", "tipo_legitima", "variante_asr",
             "escenario_base", "situacion"}
EVENTOS = {"contexto", "pedido", "cumplimiento", "rechazo", "mencion"}
PEDIDOS = {
    "REQUEST_AUTH_CODE",
    "REQUEST_SECRET",
    "REQUEST_PERSONAL_DATA",
    "REQUEST_TRANSFER",
    "REQUEST_REMOTE_ACCESS",
    "REQUEST_SECURITY_ACTION",
}
ETIQUETAS = PEDIDOS | {
    "AUTHORITY_CLAIM",
    "URGENCY_PRESSURE",
    "THREAT_FEAR",
    "ISOLATION_SECRECY",
    "TRUST_BUILDING",
    "PERSISTENCE_DISTRACTION",
}
CAMPOS = (
    "case_id",
    "grupo",
    "semilla",
    "par",
    "clase",
    "t_r_linea",
    "t_c_linea",
    "pedido",
    "evidencia",
    "que_prueba",
    "origen",
    "revision_humana",
    "notas",
)
_LINEA = re.compile(r"^(A|B): (\S.*)$")


@dataclass(frozen=True)
class Linea:
    hablante: str
    texto: str


def ids_de_casos(particion: str | None = None) -> list[str]:
    """Sin filtro lista todos; para ejecutar o afinar, pedir desarrollo."""
    if particion is not None and particion not in PARTICIONES:
        raise ValueError(f"Partición desconocida: {particion!r}")
    ids = sorted(p.stem for p in DIR_TEXTO.glob("*.txt"))
    if particion is not None:
        ids = [c for c in ids if cargar_referencia(c).get("particion", "desarrollo") == particion]
    return ids


def cargar_texto(case_id: str) -> list[Linea]:
    """Diálogo del caso. Lanza ValueError si una línea no cumple el formato."""
    crudo = (DIR_TEXTO / f"{case_id}.txt").read_text(encoding="utf-8")
    lineas = []
    for n, renglon in enumerate(crudo.splitlines(), start=1):
        m = _LINEA.match(renglon.rstrip())
        if not m:
            raise ValueError(f"{case_id}.txt línea {n}: no empieza con 'A: ' o 'B: ' ({renglon!r})")
        lineas.append(Linea(m.group(1), m.group(2)))
    return lineas


def cargar_referencia(case_id: str) -> dict:
    return json.loads((DIR_REFERENCIA / f"{case_id}.json").read_text(encoding="utf-8"))


def _semillas_del_catalogo() -> set[str]:
    with CATALOGO.open(encoding="utf-8", newline="") as f:
        return {fila["scenario_id"] for fila in csv.DictReader(f) if fila["estado"] != "descartado"}


def _es_linea(valor, n: int) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and 1 <= valor <= n


def validar_caso(case_id: str, todos: set[str], semillas: set[str]) -> list[str]:
    errores = []
    try:
        lineas = cargar_texto(case_id)
    except ValueError as e:
        return [str(e)]
    n = len(lineas)
    if n < 2:
        errores.append(f"{case_id}: el diálogo necesita al menos 2 líneas")

    ruta_ref = DIR_REFERENCIA / f"{case_id}.json"
    if not ruta_ref.exists():
        return errores + [f"{case_id}: falta referencia/{case_id}.json"]
    try:
        ref = cargar_referencia(case_id)
    except json.JSONDecodeError as e:
        return errores + [f"{case_id}.json: JSON inválido ({e})"]

    faltan = [c for c in CAMPOS if c not in ref]
    sobran = [c for c in ref if c not in set(CAMPOS) | CAMPOS_V2]
    if faltan:
        errores.append(f"{case_id}.json: faltan campos {faltan}")
    if sobran:
        errores.append(f"{case_id}.json: campos no previstos {sobran}")
    if faltan:
        return errores

    def error(msg: str) -> None:
        errores.append(f"{case_id}.json: {msg}")

    if ref["case_id"] != case_id:
        error(f"case_id {ref['case_id']!r} no coincide con el nombre del archivo")
    if ref["grupo"] not in GRUPOS:
        error(f"grupo {ref['grupo']!r} no está en {sorted(GRUPOS)}")
    if ref["clase"] not in CLASES:
        error(f"clase {ref['clase']!r} no está en {sorted(CLASES)}")
    if ref.get("particion", "desarrollo") not in PARTICIONES:
        error("particion debe ser desarrollo o test_reservado")
    if lineas and lineas[0].hablante != "A":
        error("A debe ser quien habla primero")
    if ref["grupo"] == "corpus_v2":
        faltan_v2 = sorted(CAMPOS_V2 - ref.keys())
        if faltan_v2:
            error(f"faltan campos de corpus_v2: {faltan_v2}")
        if not 12 <= n <= 40:
            error("corpus_v2 requiere entre 12 y 40 líneas")
        if ref["semilla"] is None:
            error("corpus_v2 requiere una semilla registrada")
        if ref.get("familia") not in FAMILIAS:
            error("familia fuera del inventario de corpus_v2")
        if not isinstance(ref.get("variante_asr"), bool):
            error("variante_asr debe ser true o false")
        if not isinstance(ref.get("situacion"), str) or len(ref["situacion"].strip()) < 40:
            error("situacion debe describir la semilla concreta (al menos 40 caracteres)")
        if ref.get("escenario_base") is not None and ref["escenario_base"] not in semillas:
            error("escenario_base no es un escenario activo del catálogo")
        if ref["clase"] == "vishing":
            if ref.get("tipo_legitima") is not None:
                error("un vishing no tiene tipo_legitima")
            if ref.get("dificultad") not in {"directo", "indirecto", "sin_pedido"}:
                error("dificultad de vishing inválida")
            if ref.get("dificultad") == "sin_pedido" and any(ref[k] is not None for k in ("t_r_linea", "t_c_linea", "pedido")):
                error("sin_pedido no lleva pedido ni marcas críticas")
        elif ref.get("tipo_legitima") not in TIPOS_LEGITIMA or ref.get("dificultad") != ref.get("tipo_legitima"):
            error("tipo_legitima o dificultad de legítima inválidos")
    if ref["semilla"] is not None and ref["semilla"] not in semillas:
        error(f"semilla {ref['semilla']!r} no existe en el catálogo")
    if ref["par"] is not None and ref["par"] not in todos:
        error(f"par {ref['par']!r} no es un caso existente")
    if not isinstance(ref["revision_humana"], bool):
        error("revision_humana debe ser true o false")
    for campo in ("que_prueba", "origen"):
        if not isinstance(ref[campo], str) or not ref[campo].strip():
            error(f"{campo} no puede quedar vacío")
    if not isinstance(ref["notas"], str):
        error("notas debe ser texto (puede quedar vacío)")

    t_r, t_c, pedido = ref["t_r_linea"], ref["t_c_linea"], ref["pedido"]
    if t_r is not None and not _es_linea(t_r, n):
        error(f"t_r_linea {t_r!r} fuera del diálogo (1..{n})")
    if t_c is not None and not _es_linea(t_c, n):
        error(f"t_c_linea {t_c!r} fuera del diálogo (1..{n})")
    if t_c is not None and t_r is None:
        error("t_c_linea requiere t_r_linea: no hay cumplimiento sin pedido")
    if _es_linea(t_r, n) and _es_linea(t_c, n) and t_c <= t_r:
        error("t_c_linea debe ser posterior a t_r_linea")
    if (t_r is None) != (pedido is None):
        error("pedido y t_r_linea van juntos: los dos con valor o los dos null")
    if pedido is not None and pedido not in PEDIDOS:
        error(f"pedido {pedido!r} no es una etiqueta REQUEST_*")
    if ref["clase"] in LEGITIMAS and (t_r is not None or t_c is not None):
        error("una legítima no lleva t_r_linea ni t_c_linea")

    evidencia = ref["evidencia"]
    if not isinstance(evidencia, list) or not evidencia:
        error("evidencia debe ser una lista con al menos un elemento")
        return errores
    for i, ev in enumerate(evidencia):
        if not isinstance(ev, dict) or set(ev) != {"linea", "evento", "etiquetas"}:
            error(f"evidencia[{i}] debe tener exactamente linea, evento y etiquetas")
            continue
        if not _es_linea(ev["linea"], n):
            error(f"evidencia[{i}].linea {ev['linea']!r} fuera del diálogo (1..{n})")
        if ev["evento"] not in EVENTOS:
            error(f"evidencia[{i}].evento {ev['evento']!r} no está en {sorted(EVENTOS)}")
        if not isinstance(ev["etiquetas"], list) or not set(ev["etiquetas"]) <= ETIQUETAS:
            error(f"evidencia[{i}].etiquetas tiene valores fuera del vocabulario del manual")
    if t_r is not None and not any(
        ev.get("linea") == t_r and ev.get("evento") == "pedido" for ev in evidencia
    ):
        error(f"falta una evidencia 'pedido' en la línea t_r_linea={t_r}")
    if t_c is not None and not any(
        ev.get("linea") == t_c and ev.get("evento") == "cumplimiento" for ev in evidencia
    ):
        error(f"falta una evidencia 'cumplimiento' en la línea t_c_linea={t_c}")
    return errores


def huellas_de_casos() -> dict:
    return {
        c: {
            "particion": cargar_referencia(c).get("particion", "desarrollo"),
            "texto_sha256": hashlib.sha256((DIR_TEXTO / f"{c}.txt").read_bytes()).hexdigest(),
            "referencia_sha256": hashlib.sha256((DIR_REFERENCIA / f"{c}.json").read_bytes()).hexdigest(),
        }
        for c in ids_de_casos()
    }


def validar_manifiesto() -> list[str]:
    if not MANIFIESTO.exists():
        return []
    try:
        manifiesto = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        esperados = manifiesto["casos"]
        catalogo = manifiesto["catalogo_sha256"]
    except (ValueError, KeyError, TypeError) as e:
        return [f"Manifiesto de reserva inválido: {e}"]
    actuales = huellas_de_casos()
    errores = [f"{c}: no coincide con la reserva SHA-256 (alta, baja o modificación; revisar D08)"
               for c in sorted(esperados.keys() | actuales.keys()) if esperados.get(c) != actuales.get(c)]
    if catalogo != hashlib.sha256(CATALOGO.read_bytes()).hexdigest():
        errores.append("El catálogo cambió respecto de la reserva SHA-256; revisar D08")
    return errores


def validar_todos() -> list[str]:
    ids = ids_de_casos()
    todos = set(ids)
    semillas = _semillas_del_catalogo()
    errores = []
    for huerfano in sorted({p.stem for p in DIR_REFERENCIA.glob("*.json")} - todos):
        errores.append(f"{huerfano}: hay referencia pero falta texto/{huerfano}.txt")
    for case_id in ids:
        errores.extend(validar_caso(case_id, todos, semillas))
    if not errores:
        referencias = {c: cargar_referencia(c) for c in ids}
        particiones_por_semilla = {}
        for c, ref in referencias.items():
            particion = ref.get("particion", "desarrollo")
            semilla = ref["semilla"]
            if semilla is not None:
                anterior = particiones_por_semilla.setdefault(semilla, particion)
                if anterior != particion:
                    errores.append(f"{c}: la semilla {semilla} cruza particiones")
            if ref["par"] and referencias[ref["par"]].get("particion", "desarrollo") != particion:
                errores.append(f"{c}: el par {ref['par']} cruza particiones")
    if not errores:
        errores.extend(validar_manifiesto())
    return errores


def main(argv: list[str]) -> int:
    errores = validar_todos()
    for e in errores:
        print(f"ERROR {e}")
    ids = ids_de_casos()
    if "--listar" in argv and not errores:
        print(f"{'caso':42} {'grupo':15} {'partición':15} {'clase':17} {'lín.':>4} {'T_R':>4} {'T_C':>4}")
        for case_id in ids:
            ref = cargar_referencia(case_id)
            n = len(cargar_texto(case_id))
            t_r = ref["t_r_linea"] or "-"
            t_c = ref["t_c_linea"] or "-"
            print(f"{case_id:42} {ref['grupo']:15} {ref.get('particion', 'desarrollo'):15} {ref['clase']:17} {n:>4} {t_r:>4} {t_c:>4}")
    if errores:
        print(f"\n{len(errores)} errores en {len(ids)} casos.")
        return 1
    if "--congelar" in argv:
        if MANIFIESTO.exists():
            print("La reserva ya existe; no se sobrescribe. Revisar cambios y nueva versión en D08.")
            return 1
        manifiesto = {
            "fecha": "2026-10-21",
            "estado": "propuesta sin discutir; reserva técnica, no evaluación final aprobada",
            "decisiones_pendientes": ["D07", "D08"],
            "catalogo_sha256": hashlib.sha256(CATALOGO.read_bytes()).hexdigest(),
            "casos": huellas_de_casos(),
        }
        MANIFIESTO.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Reserva SHA-256: {MANIFIESTO}")
    grupos = Counter(cargar_referencia(c)["grupo"] for c in ids)
    clases = Counter(cargar_referencia(c)["clase"] for c in ids)
    print(f"OK: {len(ids)} casos válidos. Grupos: {dict(grupos)}. Clases: {dict(clases)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
