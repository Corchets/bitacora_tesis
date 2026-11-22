"""Arma el set de legítimas reales (CallCenterEN) en el formato del set externo y genera su manifiesto.

Uso:
    python3 -I armar_set_legitimas_reales.py anotacion <trabajo> <tanda 1|2>
    python3 -I armar_set_legitimas_reales.py acuerdo <trabajo>        (antes y después del adjudicador)
    python3 -I armar_set_legitimas_reales.py armar <trabajo> <salida> <manifiesto legítimas> <manifiesto zona gris>

<trabajo> es la carpeta privada de seleccionar_legitimas_reales.py, con `traduccion/CAND-NN.json` de los
subagentes (docs/corpus/PROMPTS-LEGITIMAS-REALES-2026-11-18.md §1).

`anotacion` valida las traducciones de una tanda, deja fuera las que no son conversación o son entrantes, arma
el texto final (una línea por turno, `A` es quien habla primero, marcadores reemplazados por datos ficticios
fijos por caso) y prepara la anotación ciega con alias nuevos en otro orden (`anotar/` o `anotar-2/`).

`acuerdo` mide el acuerdo entre anotadores y decide: si ninguno de los dos marca una llamada como legítima, va a
la zona gris; si alguno la marca legítima y difieren, va al adjudicador (§3 de los prompts).

`armar` escribe en <salida> dos sets con el formato del set externo (`texto/EXT-NNNN.txt`,
`referencia/EXT-NNNN.json`, `roles-protegida.json` y `correspondencia.json`): `set-legitimas`, las legítimas
dentro del alcance, y `set-zona-gris`, que no se cuenta como falsa alarma. `correspondencia.json` trae los
nombres de archivo de la fuente, con el teléfono de la persona: queda en la custodia. Los manifiestos llevan el
SHA-256 de cada archivo y son lo único que se versiona. Nunca imprime texto de las llamadas.
"""

import hashlib
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

SEMILLA = 20261118
# Un valor fijo por tipo de marcador y por caso. Contexto de EE. UU. sin adaptar, como en el set coreano.
FICTICIOS = {
    "PERSON_NAME": ["John Miller", "Mary Johnson", "Robert Davis", "Linda Wilson", "James Moore", "Patricia Taylor",
                    "Michael Anderson", "Barbara Thomas", "David Jackson", "Susan White"],
    "LOCATION": ["Springfield", "Columbus, Ohio", "Tulsa", "Fresno", "Albany", "Mesa, Arizona"],
    "ORGANIZATION": ["Northwind Health", "Summit Insurance", "BlueRiver Medical", "Contoso Telecom", "Lakeside Group"],
    "OCCUPATION": ["maestra", "enfermero", "contador", "camionero", "cajera"],
    "DURATION": ["dos años", "seis meses", "unos diez minutos", "tres semanas"],
    "DATE_OF_BIRTH": ["12 de marzo de 1954", "3 de julio de 1949", "21 de octubre de 1958"],
    "DATE": ["el 14 de mayo", "el 2 de septiembre", "el 20 de enero"],
    "DATE_INTERVAL": ["entre marzo y junio", "de enero a abril"],
    "TIME": ["las tres de la tarde", "las diez de la mañana"],
    "MONEY_AMOUNT": ["45 dólares", "120 dólares", "1.500 dólares", "89 dólares"],
    "PERSON_AGE": ["67", "72", "64", "58"],
    "HEALTHCARE_NUMBER": ["1EG4-TE5-MK72", "5KQ9-RT2-WN41"],
    "PHONE_NUMBER": ["(555) 013-2741", "(555) 018-6620"],
    "MEDICAL_CONDITION": ["diabetes", "artritis", "presión alta"],
    "MEDICAL_PROCESS": ["una cirugía de rodilla", "un control anual"],
    "DRUG": ["metformina", "lisinopril"],
    "EMAIL_ADDRESS": ["usuario@example.com"],
    "NUMBER_SEQUENCE": ["4821", "7730"],
    "VEHICLE_ID": ["X7K-29P"],
    "ACCOUNT_NUMBER": ["000123456"],
    "BANKING_INFORMATION": ["la cuenta terminada en 0042"],
    "CREDIT_CARD_NUMBER": ["4111 1111 1111 1111"],
    "CREDIT_CARD_EXPIRATION": ["08/29"],
    "CREDIT_CARD_CVV": ["123"],
    "US_SOCIAL_SECURITY_NUMBER": ["000-12-3456"],
    "DRIVERS_LICENSE": ["D1234567"],
    "PASSWORD": ["clave1234"],
    "USERNAME": ["usuario42"],
    "URL": ["www.example.com"],
    "MARITAL_STATUS": ["casada", "viudo"],
    "EVENT": ["la feria del condado"],
    "PHYSICAL_ATTRIBUTE": ["unos 75 kilos"],
    "NATIONALITY": ["estadounidense"],
    "GENDER_SEXUALITY": ["mujer"],
}
MARCADOR = re.compile(r"\[([A-Z_]+)\]")
GENERICO = "ese dato"


def cargar_traducciones(trabajo: Path) -> dict:
    cand = json.loads((trabajo / "candidatos.json").read_text(encoding="utf-8"))["candidatos"]
    tr, problemas = {}, []
    for alias in sorted(cand):
        ruta = trabajo / "traduccion" / f"{alias}.json"
        if not ruta.exists():
            problemas.append(f"{alias}: falta la traducción")
            continue
        t = json.loads(ruta.read_text(encoding="utf-8"))
        if t.get("alias") != alias or not isinstance(t.get("turnos"), list):
            problemas.append(f"{alias}: formato inválido")
            continue
        malos = [i for i, x in enumerate(t["turnos"])
                 if x.get("lado") not in ("EMPRESA", "PERSONA") or not str(x.get("es", "")).strip()]
        if malos:
            problemas.append(f"{alias}: turnos sin lado o sin texto {malos[:5]}")
        tr[alias] = t
    return cand, tr, problemas


def texto_final(alias: str, turnos: list[dict]) -> tuple[list[str], str, Counter]:
    """Líneas «A: …»/«B: …» (una por turno; turnos seguidos del mismo lado se juntan) y quién es PROTEGIDA."""
    rng = random.Random(f"{SEMILLA}-{alias}")
    valores = {k: rng.choice(v) for k, v in FICTICIOS.items()}
    sin_valor = Counter()

    def reemplazar(m):
        if m.group(1) in valores:
            return valores[m.group(1)]
        sin_valor[m.group(1)] += 1
        return GENERICO

    juntos = []
    for x in turnos:
        es = re.sub(r"\s+", " ", MARCADOR.sub(reemplazar, x["es"])).strip()
        if juntos and juntos[-1][0] == x["lado"]:
            juntos[-1][1] += " " + es
        else:
            juntos.append([x["lado"], es])
    primero = juntos[0][0]
    lineas = [f"{'A' if lado == primero else 'B'}: {es}" for lado, es in juntos]
    return lineas, ("A" if primero == "PERSONA" else "B"), sin_valor


TANDAS = {
    1: {"anotar": "anotar", "anotadores": ("a1", "a2"), "prefijo": 0},
    2: {"anotar": "anotar-2", "anotadores": ("b1", "b2"), "prefijo": 50},
}


def anotacion(trabajo: Path, tanda: int) -> None:
    cand, tr, problemas = cargar_traducciones(trabajo)
    segunda = set(json.loads((trabajo / "candidatos.json").read_text(encoding="utf-8"))
                  .get("segunda_tanda", {}).get("alias", []))
    tr = {a: t for a, t in tr.items() if (a in segunda) == (tanda == 2)}
    problemas = [p for p in problemas if (p.split(":")[0] in segunda) == (tanda == 2)]
    for p in problemas:
        print("PROBLEMA", p)
    fuera = {a: (t.get("direccion"), t.get("motivo_si_no_sirve", "")[:80]) for a, t in tr.items()
             if not t.get("conversacion") or t.get("direccion") == "entrante"}
    usables = sorted(a for a in tr if a not in fuera)
    conf = TANDAS[tanda]
    carpeta = trabajo / conf["anotar"]
    if carpeta.exists():
        sys.exit(f"{carpeta} ya existe: la anotación de esta tanda ya se preparó")
    (trabajo / "final").mkdir(exist_ok=True)
    carpeta.mkdir()
    ruta_roles = trabajo / "final" / "roles.json"
    roles = json.loads(ruta_roles.read_text(encoding="utf-8")) if ruta_roles.exists() else {}
    sin_valor, largos, dudas = Counter(), {}, 0
    for a in usables:
        lineas, protegida, sv = texto_final(a, tr[a]["turnos"])
        sin_valor += sv
        dudas += sum(1 for x in tr[a]["turnos"] if x.get("duda"))
        (trabajo / "final" / f"{a}.txt").write_text("\n".join(lineas) + "\n", encoding="utf-8")
        roles[a] = protegida
        largos[a] = len(lineas)
    ruta_roles.write_text(json.dumps(dict(sorted(roles.items())), indent=1) + "\n", encoding="utf-8")
    orden = usables[:]
    random.Random(SEMILLA + tanda).shuffle(orden)
    clave = {}
    for i, a in enumerate(orden, conf["prefijo"] + 1):
        ll = f"LL-{i:02d}"
        clave[ll] = a
        lineas = (trabajo / "final" / f"{a}.txt").read_text(encoding="utf-8").splitlines()
        cuerpo = [f"# {ll}", "", f"PROTEGIDA (la persona llamada) es {roles[a]}; el otro lado es OTRA.", ""]
        cuerpo += [f"{n}. {l}" for n, l in enumerate(lineas, 1)]
        (carpeta / f"{ll}.md").write_text("\n".join(cuerpo) + "\n", encoding="utf-8")
    (carpeta / "clave.json").write_text(json.dumps(clave, indent=1) + "\n", encoding="utf-8")
    print(f"tanda {tanda}: traducciones {len(tr)}; fuera del filtro {len(fuera)}; para anotar {len(usables)} "
          f"({min(clave)}–{max(clave)})")
    for a, (d, m) in sorted(fuera.items()):
        print(f"  fuera {a} ({cand[a]['estrato']}): direccion={d}; {m}")
    print(f"líneas por llamada: min {min(largos.values())}, mediana {sorted(largos.values())[len(largos)//2]}, "
          f"max {max(largos.values())}; turnos con duda: {dudas}")
    print("marcadores sin valor ficticio:", dict(sin_valor) or "ninguno")


CAMPOS_ANOTACION = ("inicia", "numero", "legitimidad", "motivo", "tipo_legitima", "completa")
LEGITIMA = {"legitima", "legitima_agresiva"}


def kappa(pares: list[tuple]) -> float | None:
    """Kappa de Cohen para dos anotadores sobre una variable categórica."""
    n = len(pares)
    po = sum(a == b for a, b in pares) / n
    c1, c2 = Counter(a for a, _ in pares), Counter(b for _, b in pares)
    pe = sum(c1[k] * c2[k] for k in c1) / (n * n)
    return None if pe == 1 else (po - pe) / (1 - pe)


def leer_anotaciones(trabajo: Path) -> dict:
    """alias CAND → (alias LL, anotación 1, anotación 2), para las tandas ya anotadas."""
    salida = {}
    for tanda, conf in TANDAS.items():
        ruta = trabajo / conf["anotar"] / "clave.json"
        if not ruta.exists():
            continue
        clave = json.loads(ruta.read_text(encoding="utf-8"))
        x, y = conf["anotadores"]
        for ll, cand in clave.items():
            salida[cand] = (ll, json.loads((trabajo / f"anotacion-{x}" / f"{ll}.json").read_text(encoding="utf-8")),
                            json.loads((trabajo / f"anotacion-{y}" / f"{ll}.json").read_text(encoding="utf-8")))
    return salida


def acuerdo(trabajo: Path) -> None:
    """Acuerdo por campo y decisión de cada llamada.

    - Ninguno de los dos anotadores la marca legítima: zona gris (no se adjudica).
    - Algún anotador la marca legítima y difieren en algo de CAMPOS_ANOTACION o en si hay pedido sensible: va al
      adjudicador (desacuerdos.json). Con adjudicador.json presente, escribe adjudicacion.json.
    """
    anot = leer_anotaciones(trabajo)
    for campo in CAMPOS_ANOTACION + ("pedido_si", "es_legitima"):
        if campo == "pedido_si":
            pares = [(bool(x["pedido_sensible"]), bool(y["pedido_sensible"])) for _, x, y in anot.values()]
        elif campo == "es_legitima":
            pares = [(x["legitimidad"] in LEGITIMA, y["legitimidad"] in LEGITIMA) for _, x, y in anot.values()]
        else:
            pares = [(x[campo], y[campo]) for _, x, y in anot.values()]
        k = kappa(pares)
        print(f"{campo:15} acuerdo {sum(a == b for a, b in pares)}/{len(pares)}  kappa "
              f"{'—' if k is None else f'{k:.2f}'}")
    desacuerdos, gris = {}, []
    for cand, (ll, x, y) in sorted(anot.items()):
        if x["legitimidad"] not in LEGITIMA and y["legitimidad"] not in LEGITIMA:
            gris.append(cand)
            continue
        campos = [c for c in CAMPOS_ANOTACION if x[c] != y[c]]
        if bool(x["pedido_sensible"]) != bool(y["pedido_sensible"]):
            campos.append("pedido_sensible")
        if campos:
            desacuerdos[ll] = {"campos": campos, "a1": x, "a2": y}
    print(f"zona gris (ninguno la marca legítima): {len(gris)}; con algún anotador que la marca legítima: "
          f"{len(anot) - len(gris)}, de ellas {len(desacuerdos)} con desacuerdo: "
          f"{dict(Counter(c for d in desacuerdos.values() for c in d['campos']))}")
    ruta_adj = trabajo / "adjudicador.json"
    if not ruta_adj.exists():
        (trabajo / "desacuerdos.json").write_text(json.dumps(desacuerdos, indent=1, ensure_ascii=False) + "\n",
                                                  encoding="utf-8")
        print("escrito desacuerdos.json; falta adjudicador.json")
        return
    resuelto = json.loads(ruta_adj.read_text(encoding="utf-8"))
    faltan = [f"{ll}.{c}" for ll, d in desacuerdos.items() for c in d["campos"] if c not in resuelto.get(ll, {})]
    if faltan:
        sys.exit(f"adjudicador.json no resuelve: {faltan}")
    adj = {}
    for cand, (ll, x, y) in anot.items():
        final = {c: (x[c] if x[c] == y[c] else None) for c in CAMPOS_ANOTACION}
        lineas = [v for v in (x["primer_pedido_linea"], y["primer_pedido_linea"]) if v]
        final["pedido_sensible"] = sorted(set(x["pedido_sensible"]) | set(y["pedido_sensible"]))
        final["primer_pedido_linea"] = min(lineas) if lineas else None
        for c, v in resuelto.get(ll, {}).items():
            if c == "pedido_sensible":
                final["pedido_sensible"] = v["valor"]
                final["primer_pedido_linea"] = v.get("primer_pedido_linea")
            elif c in CAMPOS_ANOTACION:
                final[c] = v["valor"]
        final["zona_gris"] = cand in gris
        final["anotacion"] = {"alias_anotacion": ll, "anotador_1": x, "anotador_2": y,
                              "adjudicado": resuelto.get(ll, {})}
        adj[cand] = final
    (trabajo / "adjudicacion.json").write_text(json.dumps(adj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("escrito adjudicacion.json")


def sha(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def escribir_set(trabajo: Path, carpeta: Path, manifiesto: Path, casos: dict, cand: dict, adj: dict,
                 roles_finales: dict, gris: bool) -> None:
    (carpeta / "texto").mkdir(parents=True)
    (carpeta / "referencia").mkdir()
    roles, corresp = {}, {}
    for a, ext in sorted(casos.items()):
        x, c = adj[a], cand[a]
        (carpeta / "texto" / f"{ext}.txt").write_bytes((trabajo / "final" / f"{a}.txt").read_bytes())
        roles[ext] = {"protegida": roles_finales[a], "origen": "externo"}
        ref = {
            "case_id": ext,
            "grupo": "externo_zona_gris_medicare" if gris else "externo_legitimas_reales",
            "clase": "legitima_dificil" if gris else "legitima",
            "clase_fuente": "zona_gris" if gris else "legitima_real",
            "t_r_linea": None, "t_c_linea": None, "pedido": None,
            "tipo_legitima": None if gris else x["tipo_legitima"], "dificultad": None if gris else x["tipo_legitima"],
            "familia": "medico" if c["estrato"] == "equipamiento_medico" else "comercial",
            "estrato": c["estrato"], "motivo": x["motivo"],
            "legitimidad": None if gris else x["legitimidad"],
            "pedido_sensible": x["pedido_sensible"], "primer_pedido_linea": x["primer_pedido_linea"],
            "completa": x["completa"], "alcance": "dentro", "revision_humana": False,
            "anotacion": x["anotacion"],
            "marcado_por": {"turnos_y_traduccion": "subagente Claude Sonnet 5.5 (PROMPTS-LEGITIMAS-REALES §1)",
                            "anotacion": "dos subagentes Claude Sonnet 5.5 a ciegas y adjudicación (§2 y §3)"},
            "origen": "CallCenterEN (AIxBlock), revisión 9d40ca13, CC BY-NC 4.0; llamada saliente real de un BPO",
            "notas": ("ZONA GRIS: ninguno de los dos anotadores la marcó legítima (captación de Medicare o esquema "
                      "que el OIG describe como fraude). No se cuenta como falsa alarma ni como estafa: se informa "
                      "aparte. " if gris else "")
                     + "Traducción fiel al español neutro, sin adaptar al rioplatense; contexto de EE. UU. Una línea "
                       "por turno. Datos personales: marcadores de la fuente reemplazados por valores ficticios.",
        }
        (carpeta / "referencia" / f"{ext}.json").write_text(json.dumps(ref, indent=1, ensure_ascii=False) + "\n",
                                                            encoding="utf-8")
        corresp[ext] = {"candidato": a, "zip": c["zip"], "archivo": c["archivo"], "sha256_fuente": c["sha256_fuente"]}
    (carpeta / "roles-protegida.json").write_text(json.dumps(dict(sorted(roles.items())), indent=1) + "\n")
    (carpeta / "correspondencia.json").write_text(json.dumps(
        {"semilla_ids": SEMILLA, "casos": dict(sorted(corresp.items()))}, indent=1, ensure_ascii=False) + "\n")
    man = {str(p.relative_to(carpeta)): sha(p) for p in sorted(carpeta.rglob("*")) if p.is_file()}
    manifiesto.write_text(json.dumps(man, indent=1) + "\n", encoding="utf-8")
    print(f"{carpeta.name}: {len(casos)} casos; SHA-256 del manifiesto {sha(manifiesto)}")


def armar(trabajo: Path, salida: Path, man_legitimas: Path, man_gris: Path) -> None:
    cand = json.loads((trabajo / "candidatos.json").read_text(encoding="utf-8"))["candidatos"]
    adj = json.loads((trabajo / "adjudicacion.json").read_text(encoding="utf-8"))
    roles_finales = json.loads((trabajo / "final" / "roles.json").read_text(encoding="utf-8"))
    if salida.exists():
        sys.exit(f"{salida} ya existe")
    alcance = {a for a, x in adj.items() if x["inicia"] == "otra" and x["numero"] == "no_agendado"}
    legitimas = sorted(a for a in alcance if not adj[a]["zona_gris"] and adj[a]["legitimidad"] in LEGITIMA)
    gris = sorted(a for a in alcance if adj[a]["zona_gris"])
    afuera = sorted(set(adj) - set(legitimas) - set(gris))
    numeros = random.Random(SEMILLA).sample(range(1000, 10000), len(legitimas) + len(gris))
    ids = {a: f"EXT-{n}" for a, n in zip(legitimas + gris, numeros)}
    escribir_set(trabajo, salida / "set-legitimas", man_legitimas, {a: ids[a] for a in legitimas}, cand, adj,
                 roles_finales, gris=False)
    escribir_set(trabajo, salida / "set-zona-gris", man_gris, {a: ids[a] for a in gris}, cand, adj,
                 roles_finales, gris=True)
    print("legítimas por estrato y tipo:",
          dict(Counter((cand[a]["estrato"], adj[a]["tipo_legitima"]) for a in legitimas)))
    print("legítimas con pedido sensible:", sum(1 for a in legitimas if adj[a]["pedido_sensible"]))
    print("zona gris por estrato:", dict(Counter(cand[a]["estrato"] for a in gris)))
    for a in afuera:
        x = adj[a]
        print(f"  afuera {a} ({cand[a]['estrato']}): inicia={x['inicia']} numero={x['numero']} "
              f"legitimidad={x['legitimidad']}")


if __name__ == "__main__":
    if sys.argv[1] == "anotacion":
        anotacion(Path(sys.argv[2]), int(sys.argv[3]))
    elif sys.argv[1] == "acuerdo":
        acuerdo(Path(sys.argv[2]))
    elif sys.argv[1] == "armar":
        armar(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5]))
    else:
        sys.exit(__doc__)
