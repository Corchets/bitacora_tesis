"""Escenarios y legítimas dudosas del corpus de desarrollo, y sus cifras en la etapa 2 de #143.

> **Estado: propuesta sin discutir.** Prepara material para que el equipo decida antes de la próxima corrida de #143
> cómo se cuentan las legítimas repetidas o poco creíbles y las estafas sin pedido. No juzga: el juicio es humano (#145).

Solo lee la partición de desarrollo. Nunca abre la reserva (`CV2-T-*`) ni el lote de test de #45.

Uso (siempre con `python -I`):
    python -I corpus_desarrollo.py escenarios
    python -I corpus_desarrollo.py ciego-dudosas DESTINO          # paquete ciego para los anotadores
    python -I corpus_desarrollo.py unir-dudosas ANOTACIONES...     # une las anotaciones con la clave
    python -I corpus_desarrollo.py cifras CARPETA_DE_LA_ETAPA_2
    python -I corpus_desarrollo.py manifiesto                      # lista representativa y manifiesto
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import statistics
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CASOS = RAIZ / "casos"
LISTAS = ("legitimas-91", "legitimas-seleccion-3")
SALIDA_ESCENARIOS = CASOS / "escenarios-legitimas.json"
SALIDA_DUDOSAS = CASOS / "legitimas-dudosas.json"
PROPUESTA = "> **Estado: propuesta sin discutir.**"


# --- Carga -------------------------------------------------------------------------------------------------------

def ids_de_lista(nombre: str) -> list[str]:
    lineas = (CASOS / "listas" / f"{nombre}.txt").read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lineas if l.strip() and not l.startswith("#")]


def legitimas() -> list[str]:
    ids = [c for n in LISTAS for c in ids_de_lista(n)]
    assert len(ids) == len(set(ids)) == 94, len(ids)
    assert not any(c.startswith("CV2-T-") for c in ids)
    return ids


def texto(case_id: str) -> list[str]:
    assert not case_id.startswith("CV2-T-"), "la reserva no se abre"
    return [l for l in (CASOS / "texto" / f"{case_id}.txt").read_text(encoding="utf-8").splitlines() if l.strip()]


def referencia(case_id: str) -> dict:
    assert not case_id.startswith("CV2-T-"), "la reserva no se abre"
    return json.loads((CASOS / "referencia" / f"{case_id}.json").read_text(encoding="utf-8"))


def roles() -> dict:
    return json.loads((CASOS / "roles-protegida.json").read_text(encoding="utf-8"))


# --- Parecido: el método de #45 (test_alcance.py, rama laboratorio-luciano) ----------------------------------------

def normalizar(lineas: list[str]) -> list[str]:
    t = " ".join(re.sub(r"^[AB]:\s*", "", l) for l in lineas).lower()
    t = "".join(ch for ch in unicodedata.normalize("NFD", t) if unicodedata.category(ch) != "Mn")
    return re.findall(r"[a-zñ0-9]+", t)


class Espacio:
    """Coseno TF-IDF de palabras (1 y 2) y cobertura de bigramas pesados por IDF. Copia de test_alcance.py (#45)."""

    def __init__(self, documentos: list[list[str]]):
        df = Counter()
        for d in documentos:
            df.update(set(self.gramas(d)))
        self.n = len(documentos)
        self.idf = {g: math.log((1 + self.n) / (1 + c)) + 1 for g, c in df.items()}

    @staticmethod
    def gramas(pal: list[str]) -> list[str]:
        return pal + [f"{a}_{b}" for a, b in zip(pal, pal[1:])]

    def _idf(self, g: str) -> float:
        return self.idf.get(g, math.log(1 + self.n) + 1)

    def vector(self, pal: list[str]) -> dict[str, float]:
        v = {g: (1 + math.log(c)) * self._idf(g) for g, c in Counter(self.gramas(pal)).items()}
        norma = math.sqrt(sum(x * x for x in v.values()))
        return {g: x / norma for g, x in v.items()}

    def coseno(self, a: list[str], b: list[str]) -> float:
        va, vb = self.vector(a), self.vector(b)
        return sum(x * vb.get(g, 0.0) for g, x in va.items())

    def cobertura(self, origen: list[str], nueva: list[str]) -> float:
        """Parte de los bigramas de `origen`, pesados por IDF, que reaparecen en `nueva`."""
        bo = {f"{a}_{b}" for a, b in zip(origen, origen[1:])}
        bn = {f"{a}_{b}" for a, b in zip(nueva, nueva[1:])}
        total = sum(self._idf(g) for g in bo)
        return sum(self._idf(g) for g in bo & bn) / total if total else 0.0


def reescrituras_declaradas(ids: list[str]) -> dict[str, str]:
    """LEG2 cuyas notas u origen nombran una LEG: la reescritura declarada (#45)."""
    pares = {}
    for cid in ids:
        r = referencia(cid)
        m = re.findall(r"LEG-[A-Z]{2}-\d{2}", f"{r.get('notas') or ''} {r.get('origen') or ''}")
        if cid.startswith("LEG2-") and m:
            pares[cid] = m[0]
    return pares


def componentes(ids: list[str], enlazados) -> list[list[str]]:
    padre = {c: c for c in ids}

    def raiz(c):
        while padre[c] != c:
            padre[c] = padre[padre[c]]
            c = padre[c]
        return c

    for a, b in enlazados:
        padre[raiz(a)] = raiz(b)
    grupos = defaultdict(list)
    for c in ids:
        grupos[raiz(c)].append(c)
    return sorted((sorted(g) for g in grupos.values()), key=lambda g: (-len(g), g[0]))


def matrices(ids: list[str]):
    norm = {c: normalizar(texto(c)) for c in ids}
    esp = Espacio(list(norm.values()))
    cos, cob = {}, {}
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            cos[a, b] = cos[b, a] = esp.coseno(norm[a], norm[b])
            cob[a, b] = esp.cobertura(norm[a], norm[b])  # parte de a que reaparece en b
            cob[b, a] = esp.cobertura(norm[b], norm[a])
    return norm, esp, cos, cob


def enlaces(ids, cos, cob, u_cos, u_cob):
    return [(a, b) for i, a in enumerate(ids) for b in ids[i + 1:]
            if cos[a, b] >= u_cos or max(cob[a, b], cob[b, a]) >= u_cob]


# Número de LEG/LEG2 que reaparece en una ENT-L (#45: ENT-L-ENCUESTA-004 y LEG2-EN-04).
CODIGO_FAMILIA = {"BA": "BANCO", "CC": "VENTAS", "CO": "DELIVERY", "EN": "ENCUESTA", "ST": "SOPORTE",
                  "TU": "MEDICO", "VE": "VENTAS"}


def mismo_numero(a: str, b: str) -> bool:
    def clave(c):
        m = re.match(r"^(LEG2?)-([A-Z]{2})-(\d+)$", c)
        if m:
            return CODIGO_FAMILIA.get(m[2]), int(m[3])
        m = re.match(r"^ENT-L-([A-Z_]+)-(\d+)$", c)
        return (m[1], int(m[2])) if m else (None, None)
    ka, kb = clave(a), clave(b)
    return ka[0] is not None and ka == kb and a.split("-")[0] != b.split("-")[0]


def cmd_escenarios(_args) -> int:
    ids = legitimas()
    norm, esp, cos, cob = matrices(ids)
    pares = reescrituras_declaradas(ids)
    u_cos = min(cos[a, b] for a, b in pares.items())
    u_cob = min(cob[b, a] for a, b in pares.items())  # parte de la LEG que reaparece en la LEG2
    grupos = componentes(ids, enlaces(ids, cos, cob, u_cos, u_cob))

    # Sensibilidad: cuántos escenarios con umbrales más exigentes o con una sola medida.
    sens = []
    for etiqueta, uc, ub in (("calibrados (mínimo de las reescrituras)", u_cos, u_cob),
                             ("solo coseno", u_cos, 9), ("solo cobertura", 9, u_cob),
                             ("percentil 25 de las reescrituras", *_percentil(pares, cos, cob, 0.25)),
                             ("mediana de las reescrituras", *_percentil(pares, cos, cob, 0.5))):
        sens.append({"umbrales": etiqueta, "coseno": round(uc, 3) if uc < 9 else None,
                     "cobertura": round(ub, 3) if ub < 9 else None,
                     "escenarios": len(componentes(ids, enlaces(ids, cos, cob, uc, ub)))})

    salida, numero = [], {}
    for k, g in enumerate(grupos, start=1):
        nombre = f"E{k:02d}"
        # Encadenado: algún par del grupo no llega a ninguno de los dos umbrales (single linkage).
        flojos = [(a, b) for i, a in enumerate(g) for b in g[i + 1:]
                  if cos[a, b] < u_cos and max(cob[a, b], cob[b, a]) < u_cob]
        for c in g:
            numero[c] = nombre
            otros = [o for o in ids if o != c]
            vec_cos = max(otros, key=lambda o: cos[c, o])
            vec_cob = max(otros, key=lambda o: max(cob[c, o], cob[o, c]))
            r = referencia(c)
            salida.append({
                "case_id": c, "escenario": nombre, "tamano": len(g), "familia": r.get("familia"),
                "tipo_legitima": r.get("tipo_legitima"), "lineas": len(texto(c)), "situacion": r.get("situacion"),
                "vecino_coseno": vec_cos, "coseno": round(cos[c, vec_cos], 3),
                "vecino_cobertura": vec_cob, "cobertura": round(max(cob[c, vec_cob], cob[vec_cob, c]), 3),
                "reescritura_declarada": pares.get(c) or next((a for a, b in pares.items() if b == c), None),
                "mismo_numero_en_grupo": sorted(o for o in g if o != c and mismo_numero(c, o)),
                "grupo_encadenado": bool(flojos),
                "familias_del_grupo": sorted({referencia(o).get("familia") for o in g}),
            })
    variante = escenarios_del_control(salida)
    for f in salida:
        f["escenario_control"] = variante.get(f["case_id"])
    meta = {
        "estado": "propuesta sin discutir; lo decide el método de #45; control a ciegas en escenarios-control.json",
        "escenarios_control": len(set(variante.values())) if variante else None,
        "metodo": "coseno TF-IDF de palabras 1-2 y cobertura de bigramas pesados por IDF (test_alcance.py, #45); "
                  "enlace si coseno >= umbral o cobertura en cualquier sentido >= umbral; escenario = componente conexa",
        "listas": list(LISTAS),
        "reescrituras_declaradas": len(pares), "umbral_coseno": round(u_cos, 3), "umbral_cobertura": round(u_cob, 3),
        "escenarios": len(grupos), "unitarios": sum(len(g) == 1 for g in grupos),
        "sensibilidad": sens,
        "huella_textos": hashlib.sha256("".join(c + "\n" + "\n".join(texto(c)) for c in ids).encode()).hexdigest(),
    }
    SALIDA_ESCENARIOS.write_text(json.dumps({"_meta": meta, "casos": salida}, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    reemplazar_bloque(DOC_ESCENARIOS, "tabla", tabla_escenarios(salida, control_por_escenario()))
    reemplazar_bloque(DOC_ESCENARIOS, "sensibilidad", "\n".join(
        ["| Umbrales | Coseno | Cobertura | Escenarios |", "|---|---:|---:|---:|"]
        + [f"| {s['umbrales']} | {coma(s['coseno'])} | {coma(s['cobertura'])} | {s['escenarios']} |" for s in sens]))
    print(json.dumps(meta, ensure_ascii=False, indent=2))
    return 0


DOC_ESCENARIOS = CASOS / "ESCENARIOS-LEGITIMAS-DESARROLLO.md"


def coma(x, d: int = 3) -> str:
    return "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def reemplazar_bloque(doc: Path, nombre: str, contenido: str) -> None:
    """Reemplaza lo que está entre `<!-- nombre:inicio -->` y `<!-- nombre:fin -->` (generado, no se edita a mano)."""
    t = doc.read_text(encoding="utf-8")
    ini, fin = f"<!-- {nombre}:inicio -->", f"<!-- {nombre}:fin -->"
    assert t.count(ini) == t.count(fin) == 1, f"faltan las marcas {nombre} en {doc.name}"
    a, resto = t.split(ini)
    _, b = resto.split(fin)
    doc.write_text(f"{a}{ini}\n{contenido}\n{fin}{b}", encoding="utf-8")


CONTROL_ESCENARIOS = CASOS / "escenarios-control.json"


def escenarios_del_control(filas: list[dict]) -> dict[str, str]:
    """Variante de sensibilidad: los escenarios del método, separados y unidos como dijo el control a ciegas."""
    if not CONTROL_ESCENARIOS.exists():
        return {}
    c = json.loads(CONTROL_ESCENARIOS.read_text(encoding="utf-8"))
    v = {f["case_id"]: f["escenario"] for f in filas}
    for g in c["grupos"]:
        for k, parte in enumerate(g.get("separar") or []):
            for cid in parte:
                assert v[cid] == g["escenario"], (cid, g["escenario"])
                v[cid] = f"{g['escenario']}{'abc'[k]}"
    for u in c.get("unir", []):
        destino = u["escenarios"][0]
        for cid, e in v.items():
            if e.rstrip("abc") in u["escenarios"]:
                v[cid] = destino
    return v


def control_por_escenario() -> dict[str, str]:
    """Lo que dijo el control a ciegas de cada escenario (vacío si todavía no hay control)."""
    if not CONTROL_ESCENARIOS.exists():
        return {}
    c = json.loads(CONTROL_ESCENARIOS.read_text(encoding="utf-8"))
    out = {g["escenario"]: "misma situación" if g["misma_situacion"] == "si" else
           "separar: " + " / ".join(", ".join(f"`{x}`" for x in parte) for parte in (g.get("separar") or []))
           for g in c["grupos"]}
    for u in c.get("unir", []):
        for e in u["escenarios"]:
            otros = ", ".join(x for x in u["escenarios"] if x != e)
            out[e] = (out[e] + "; " if e in out else "") + f"unir con {otros}"
    return out


def tabla_escenarios(filas: list[dict], control: dict[str, str]) -> str:
    out = ["| Escenario | Caso | Familia | Tipo | Líneas | Más parecido (coseno · cobertura) | Marcas | Situación (referencia) "
           "| Control |", "|---|---|---|---|---:|---|---|---|---|"]
    for f in filas:
        marcas = []
        if f["reescritura_declarada"]:
            marcas.append(f"reescritura declarada de/por `{f['reescritura_declarada']}`")
        if f["mismo_numero_en_grupo"]:
            marcas.append("mismo número que " + ", ".join(f"`{o}`" for o in f["mismo_numero_en_grupo"]))
        if f["grupo_encadenado"]:
            marcas.append("**grupo encadenado**")
        if len(f["familias_del_grupo"]) > 1:
            marcas.append("**mezcla familias**")
        if f["vecino_coseno"] == f["vecino_cobertura"]:
            vecino = f"`{f['vecino_coseno']}` {coma(f['coseno'])} · {coma(f['cobertura'])}"
        else:
            vecino = f"`{f['vecino_coseno']}` {coma(f['coseno'])} · `{f['vecino_cobertura']}` {coma(f['cobertura'])}"
        sit = (f["situacion"] or "").replace("|", "/")
        out.append(f"| {f['escenario']} ({f['tamano']}) | `{f['case_id']}` | {f['familia']} | {f['tipo_legitima']} | "
                   f"{f['lineas']} | {vecino} | {'; '.join(marcas)} | {sit} | {control.get(f['escenario'], '—')} |")
    return "\n".join(out)


def _percentil(pares, cos, cob, q):
    cs = sorted(cos[a, b] for a, b in pares.items())
    bs = sorted(cob[b, a] for a, b in pares.items())
    i = max(0, min(len(cs) - 1, round(q * (len(cs) - 1))))
    return cs[i], bs[i]


# --- Legítimas dudosas ---------------------------------------------------------------------------------------------

DOC_CRITERIO = CASOS / "CRITERIO-LEGITIMAS-DUDOSAS.md"
DOC_DUDOSAS = CASOS / "LEGITIMAS-DUDOSAS.md"
SEMILLA_DUDOSAS = 2026_11_09
FINANCIERAS = {"banco", "tarjeta_o_billetera", "organismo_publico"}
ENTIDADES = FINANCIERAS | {"soporte_tecnico", "otra_empresa", "particular", "no_se_sabe"}
SENALES = ("s1", "s2", "s3", "s4")

INSTRUCCIONES_ANOTADOR = """\
# Anotación de llamadas legítimas

Estas {n} llamadas están marcadas como **legítimas** en un corpus de prueba. Tu tarea es marcar, en cada una, si quien
habla por una entidad hace alguna de cuatro cosas. No juzgues si la llamada es creíble ni si es una estafa: solo
anotá lo que pasa. Leé solo este archivo. No abras otros archivos, no uses git ni la web.

Cada línea lleva su número, quién habla (PROTEGIDA es la persona que recibe la llamada; OTRA es la otra parte) y el
texto. Puede haber errores de transcripción.

## Qué anotar en cada llamada

- `entidad`: por quién dice hablar OTRA. Una de `banco`, `tarjeta_o_billetera`, `organismo_publico` (ANSES, ARCA,
  registro, municipio, licencias, etc.), `soporte_tecnico`, `otra_empresa` (comercio, consultorio, correo,
  encuestadora, selección de personal, telefonía, etc.), `particular` o `no_se_sabe`.
- `contacto_pedido`: `si` si en la llamada consta que responde a algo que PROTEGIDA hizo y lo reconoce (una
  solicitud, un reclamo, un turno, un ticket, una compra, un trámite suyo); `no` si no consta, por ejemplo un aviso de
  fraude por una operación que PROTEGIDA no hizo, una oferta o una encuesta que nadie pidió; `no_se_sabe` si no se
  puede decidir.
- Cuatro señales. En cada una, el **número de la primera línea** donde OTRA lo hace, o `null` si no lo hace. Cuenta
  aunque PROTEGIDA no lo haga y aunque OTRA se corrija después. Si es PROTEGIDA la que ofrece algo y OTRA la frena, no
  cuenta. Anotá la señal sea cual sea la entidad.
  - `s1`: OTRA pide que PROTEGIDA diga, dicte, lea o tipee una clave, contraseña, PIN, token, usuario de home banking,
    un código de verificación o de vinculación recibido por SMS, app o correo, el código de seguridad de una tarjeta o
    su número completo.
  - `s2`: OTRA pide que PROTEGIDA opere en el cajero, el home banking o una app de pagos o del banco mientras sigue en
    la llamada, o la guía para hacerlo; que transfiera o pague a una cuenta o enlace que da OTRA; o que mueva dinero a
    otra cuenta para protegerlo.
  - `s3`: OTRA pide que PROTEGIDA instale una aplicación o un programa, o que le dé acceso remoto al equipo o al
    celular.
  - `s4`: OTRA pide que PROTEGIDA diga datos de identidad o de cuenta: DNI, fecha de nacimiento, CUIL o CUIT, número
    de cuenta o CBU, o datos de una tarjeta. Pedir que confirme el nombre, o mencionar un dato sin pedirlo, no cuenta.
- `s4_antes_del_motivo`: si hay `s4`, `true` si el pedido llega antes de que OTRA diga para qué llama, `false` si
  llega después; `null` si no hay `s4`.
- `motivo`: hasta 40 palabras, con los números de línea que justifican lo que marcaste.

## Formato de salida

Un archivo JSONL con una línea por llamada, en el orden de este archivo, sin texto fuera del JSON:

{{"llamada": "llamada-001", "entidad": "banco", "contacto_pedido": "no", "s1": null, "s2": null, "s3": null, "s4": 3, "s4_antes_del_motivo": true, "motivo": "..."}}

## Llamadas
"""


def lineas_con_roles(case_id: str, rol: dict) -> list[str]:
    protegida = rol["protegida"]
    out = []
    for n, l in enumerate(texto(case_id), start=1):
        quien, _, dicho = l.partition(": ")
        out.append(f"{n:02d} {'PROTEGIDA' if quien == protegida else 'OTRA'}: {dicho}")
    return out


def cmd_ciego_dudosas(args) -> int:
    ids = legitimas()
    rol = roles()
    orden = ids[:]
    random.Random(SEMILLA_DUDOSAS).shuffle(orden)
    destino, clave = Path(args.destino), Path(args.clave)
    assert not clave.resolve().is_relative_to(destino.resolve()), "la clave va fuera del paquete"
    destino.mkdir(parents=True, exist_ok=True)
    partes, mapa = [INSTRUCCIONES_ANOTADOR.format(n=len(orden))], {}
    for k, cid in enumerate(orden, start=1):
        alias = f"llamada-{k:03d}"
        mapa[alias] = cid
        partes += [f"\n### {alias}\n", *lineas_con_roles(cid, rol[cid])]
    paquete = destino / "paquete.md"
    paquete.write_text("\n".join(partes) + "\n", encoding="utf-8")
    clave.write_text(json.dumps({"semilla": SEMILLA_DUDOSAS, "paquete_sha256": _sha(paquete), "clave": mapa},
                                ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{paquete} ({len(orden)} llamadas, sha256 {_sha(paquete)[:12]}); clave en {clave}")
    return 0


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def marca(a: dict, estricta: bool = False) -> tuple[str, list[str]]:
    """Marca de una anotación según el criterio: (si | no | no_se_sabe, señales que cuentan)."""
    fin = a["entidad"] in FINANCIERAS
    dudas, cuentan = False, []
    for s in SENALES:
        if a.get(s) is None:
            continue
        if s == "s1":
            cuentan.append(s)
        elif s == "s2" and fin:
            cuentan.append(s)
        elif s == "s3":
            if fin or a["contacto_pedido"] == "no":
                cuentan.append(s)
            elif a["contacto_pedido"] == "no_se_sabe" or a["entidad"] == "no_se_sabe":
                dudas = True
        elif s == "s4" and fin:
            if estricta or a["contacto_pedido"] == "no":
                cuentan.append(s)
            elif a["contacto_pedido"] == "no_se_sabe":
                dudas = True
        elif a["entidad"] == "no_se_sabe":
            dudas = True
    return ("si" if cuentan else "no_se_sabe" if dudas else "no"), cuentan


def cmd_unir_dudosas(args) -> int:
    clave = json.loads(Path(args.clave).read_text(encoding="utf-8"))
    mapa = clave["clave"]
    anot = []
    for ruta in args.anotaciones:
        filas = [json.loads(l) for l in Path(ruta).read_text(encoding="utf-8").splitlines() if l.strip()]
        d = {f["llamada"]: f for f in filas}
        assert set(d) == set(mapa), f"{ruta}: faltan o sobran llamadas"
        for f in filas:
            assert f["entidad"] in ENTIDADES and f["contacto_pedido"] in {"si", "no", "no_se_sabe"}, f
        anot.append({mapa[k]: v for k, v in d.items()})
    assert len(anot) == 2
    esc = {c["case_id"]: c["escenario"] for c in json.loads(SALIDA_ESCENARIOS.read_text(encoding="utf-8"))["casos"]}
    filas, acuerdo = [], Counter()
    for cid in legitimas():
        a, b = anot[0][cid], anot[1][cid]
        ma, mb = marca(a), marca(b)
        ea, eb = marca(a, estricta=True), marca(b, estricta=True)
        prop = ma[0] if ma[0] == mb[0] and ma[0] != "no_se_sabe" else "a_revisar"
        prop_e = ea[0] if ea[0] == eb[0] and ea[0] != "no_se_sabe" else "a_revisar"
        for campo in ("entidad", "contacto_pedido", *SENALES):
            acuerdo[campo] += (a.get(campo) is None) == (b.get(campo) is None) if campo in SENALES else a[campo] == b[campo]
        acuerdo["marca"] += ma[0] == mb[0]
        r = referencia(cid)
        filas.append({
            "case_id": cid, "escenario": esc[cid], "familia": r.get("familia"), "tipo_legitima": r.get("tipo_legitima"),
            "propuesta": prop, "propuesta_estricta": prop_e,
            "anotador_1": {**{k: a.get(k) for k in ("entidad", "contacto_pedido", *SENALES, "s4_antes_del_motivo",
                                                    "motivo")}, "marca": ma[0], "cuentan": ma[1]},
            "anotador_2": {**{k: b.get(k) for k in ("entidad", "contacto_pedido", *SENALES, "s4_antes_del_motivo",
                                                    "motivo")}, "marca": mb[0], "cuentan": mb[1]},
        })
    resumen = {
        "estado": "propuesta sin discutir; criterio aplicado a ciegas por dos agentes; el juicio es humano (#145)",
        "criterio": DOC_CRITERIO.name, "semilla": clave["semilla"], "paquete_sha256": clave["paquete_sha256"],
        "anotaciones_sha256": [_sha(Path(r)) for r in args.anotaciones],
        "acuerdo": {k: f"{v}/94" for k, v in acuerdo.items()},
        "propuesta": dict(Counter(f["propuesta"] for f in filas)),
        "propuesta_estricta": dict(Counter(f["propuesta_estricta"] for f in filas)),
    }
    SALIDA_DUDOSAS.write_text(json.dumps({"_meta": resumen, "casos": filas}, ensure_ascii=False, indent=2) + "\n",
                              encoding="utf-8")
    reemplazar_bloque(DOC_DUDOSAS, "tabla", tabla_dudosas(filas))
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0


def tabla_dudosas(filas: list[dict]) -> str:
    def senales(x):
        partes = [f"{s.upper()} l.{x[s]}{'' if s in x['cuentan'] else ' (no cuenta)'}" for s in SENALES
                  if x.get(s) is not None]
        return ", ".join(partes) or "—"

    def resumen(x):
        return f"{x['entidad']}, pedido: {x['contacto_pedido']}; {senales(x)}"

    orden = {"si": 0, "a_revisar": 1, "no": 2}
    out = ["| Caso | Escenario | Familia | Propuesta | Estricta | Anotador 1 | Anotador 2 |",
           "|---|---|---|---|---|---|---|"]
    for f in sorted(filas, key=lambda f: (orden[f["propuesta"]], orden[f["propuesta_estricta"]], f["case_id"])):
        out.append(f"| `{f['case_id']}` | {f['escenario']} | {f['familia']} | **{f['propuesta']}** | "
                   f"{f['propuesta_estricta']} | {resumen(f['anotador_1'])} | {resumen(f['anotador_2'])} |")
    return "\n".join(out)


# --- Cifras de la etapa 2 con y sin limpieza (exploración) --------------------------------------------------------

DOC_CIFRAS = CASOS / "CIFRAS-LIMPIEZA-DESARROLLO.md"
SALIDA_CIFRAS = CASOS / "cifras-limpieza.json"
CONFIGURACIONES = (("v4", "v4-corte", 0.4), ("C", "c-json-corte", 0.3), ("C rep.", "c-json-corte-rep", 0.3))


def leer_corrida(carpeta: Path) -> tuple[dict[str, list[dict]], dict]:
    """Filas del SLM por caso, ordenadas por línea, y el manifiesto. Como `leer` de analizar.py (etapa 2)."""
    import csv
    csv.field_size_limit(10**9)
    (run,) = [p for p in carpeta.glob("*") if (p / "manifiesto.json").exists()]
    man = json.loads((run / "manifiesto.json").read_text(encoding="utf-8"))
    assert man["particion"] == "desarrollo" and not any(c.startswith("CV2-T-") for c in man["casos"])
    filas = defaultdict(list)
    with open(run / "actualizaciones.csv", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["detector"] == "slm":
                filas[r["case_id"]].append(r)
    for v in filas.values():
        v.sort(key=lambda r: int(r["linea"]))
    return dict(filas), man


def primer_aviso(filas: list[dict], umbral: float) -> int | None:
    """Primera línea válida con alerta escrita o riesgo ≥ umbral (`avisos` de analizar.py, etapa 2)."""
    for r in filas:
        riesgo = float(r["riesgo"]) if r["riesgo"] not in ("", None) else None
        if r["valida"] == "true" and (r["alerta_escrita"] == "true" or (riesgo is not None and riesgo >= umbral - 1e-9)):
            return int(r["linea"])
    return None


def cmd_cifras(args) -> int:
    base = Path(args.corridas)
    leg = legitimas()
    est = sorted(p.stem for p in (CASOS / "referencia").glob("CV2-D-V-*.json"))
    tr = {c: referencia(c)["t_r_linea"] for c in est}
    conp = [c for c in est if tr[c] is not None]
    sinp = [c for c in est if tr[c] is None]
    filas_esc = json.loads(SALIDA_ESCENARIOS.read_text(encoding="utf-8"))["casos"]
    esc = {c["case_id"]: c["escenario"] for c in filas_esc}
    esc_control = {c["case_id"]: c["escenario_control"] for c in filas_esc}
    dud = {c["case_id"]: c for c in json.loads(SALIDA_DUDOSAS.read_text(encoding="utf-8"))["casos"]}
    fuera = {"L2": {c for c in leg if dud[c]["propuesta"] == "si"},
             "L2r": {c for c in leg if dud[c]["propuesta"] in ("si", "a_revisar")},
             "L2e": {c for c in leg if dud[c]["propuesta_estricta"] == "si"}}

    def por_escenario(fa: dict, ids: list[str], grupos: dict | None = None) -> tuple[int, int, float]:
        g = defaultdict(list)
        for c in ids:
            g[(grupos or esc)[c]].append(fa[c])
        con = sum(any(v) for v in g.values())
        pond = sum(sum(v) / len(v) for v in g.values())
        return con, len(g), pond

    res, avisos_por_config = {}, {}
    for nombre, carpeta, umbral in CONFIGURACIONES:
        filas, man = leer_corrida(base / carpeta)
        faltan = [c for c in leg + est if c not in filas]
        assert not faltan, f"{carpeta}: faltan {faltan[:3]}"
        av = {c: primer_aviso(filas[c], umbral) for c in leg + est}
        avisos_por_config[nombre] = av
        fa = {c: av[c] is not None for c in leg}
        l1 = por_escenario(fa, leg)
        sin = [c for c in leg if c not in fuera["L2"]]
        l3 = por_escenario(fa, sin)
        res[nombre] = {
            "corrida": f"{carpeta}/{man.get('carpeta') or ''}".rstrip("/"), "regla": f"riesgo ≥ {coma(umbral, 1)} o alerta",
            "L0": (sum(fa.values()), len(leg)),
            "L1": (l1[0], l1[1]), "L1p": (l1[2], l1[1]),
            "L1c": por_escenario(fa, leg, esc_control)[:2],
            "L2": (sum(fa[c] for c in sin), len(sin)),
            "L3": (l3[0], l3[1]),
            "L2r": (sum(fa[c] for c in leg if c not in fuera["L2r"]), len(leg) - len(fuera["L2r"])),
            "L2e": (sum(fa[c] for c in leg if c not in fuera["L2e"]), len(leg) - len(fuera["L2e"])),
            "dudosas_con_fa": (sum(fa[c] for c in fuera["L2"]), len(fuera["L2"])),
            "a_revisar_con_fa": (sum(fa[c] for c in fuera["L2r"] - fuera["L2"]), len(fuera["L2r"] - fuera["L2"])),
            "E46": (sum(av[c] is not None for c in est), len(est)),
            "E36": (sum(av[c] is not None for c in conp), len(conp)),
            "antes36": (sum(av[c] is not None and av[c] < tr[c] for c in conp), len(conp)),
            "E10": (sum(av[c] is not None for c in sinp), len(sinp)),
            "escenarios_con_fa": sorted({esc[c] for c in leg if fa[c]}),
        }
    nombres = [n for n, _, _ in CONFIGURACIONES]

    def celda(v):
        k, n = v
        return f"{coma(k, 2)}/{n}" if isinstance(k, float) else f"{k}/{n}"

    def dif(clave):
        a, b = res["C"][clave][0], res["v4"][clave][0]
        return f"{a - b:+.2f}".replace(".", ",") if isinstance(a, float) else f"{a - b:+d}"

    vistas_leg = (("L0. Por llamada", "L0"), ("L1. Por escenario (al menos una FA)", "L1"),
                  ("L1p. Por escenario, ponderada", "L1p"), ("L2. Sin dudosas", "L2"),
                  ("L3. Por escenario y sin dudosas", "L3"),
                  ("Sensibilidad: sin dudosas ni «a revisar»", "L2r"), ("Sensibilidad: sin dudosas, S4 estricta", "L2e"),
                  ("Sensibilidad agregada después de mirar: por escenario del control a ciegas", "L1c"))
    vistas_est = (("Estafas avisadas, todas", "E46"), ("Estafas avisadas, con pedido", "E36"),
                  ("Avisos antes del pedido", "antes36"), ("Estafas avisadas, sin pedido", "E10"))
    out = [f"Corridas: " + "; ".join(f"**{n}** `{res[n]['corrida']}`, {res[n]['regla']}" for n in nombres) + ".", "",
           "**Falsas alarmas en las legítimas**", "",
           "| Vista | " + " | ".join(nombres) + " | C − v4 |", "|---|" + "---:|" * (len(nombres) + 1)]
    for etiqueta, k in vistas_leg:
        out.append(f"| {etiqueta} | " + " | ".join(celda(res[n][k]) for n in nombres) + f" | {dif(k)} |")
    out += ["", "En L1p la cifra es la suma, sobre los escenarios, de la parte de sus llamadas con FA: son «escenarios "
            "con FA» contando fracciones.", "", "**Las legítimas que salen de la cifra**", "",
            "| | " + " | ".join(nombres) + " |", "|---|" + "---:|" * len(nombres),
            "| Dudosas con FA | " + " | ".join(celda(res[n]["dudosas_con_fa"]) for n in nombres) + " |",
            "| «A revisar» con FA | " + " | ".join(celda(res[n]["a_revisar_con_fa"]) for n in nombres) + " |",
            "", "**Estafas**", "", "| Vista | " + " | ".join(nombres) + " | C − v4 |",
            "|---|" + "---:|" * (len(nombres) + 1)]
    for etiqueta, k in vistas_est:
        out.append(f"| {etiqueta} | " + " | ".join(celda(res[n][k]) for n in nombres) + f" | {dif(k)} |")
    out += ["", "**Dudosas, una por una**", "", "| Caso | Escenario | Señales (anotador 1 / 2) | " +
            " | ".join(f"FA {n}" for n in nombres) + " |", "|---|---|---|" + "---|" * len(nombres)]
    for c in sorted(fuera["L2"]):
        s = " / ".join(", ".join(x.upper() for x in dud[c][k]["cuentan"]) for k in ("anotador_1", "anotador_2"))
        out.append(f"| `{c}` | {esc[c]} | {s} | " +
                   " | ".join("sí" if avisos_por_config[n][c] is not None else "no" for n in nombres) + " |")
    reemplazar_bloque(DOC_CIFRAS, "cifras", "\n".join(out))
    SALIDA_CIFRAS.write_text(json.dumps({"_meta": {
        "estado": "exploración; propuesta sin discutir; no decide nada (ADR 0005)",
        "corridas": {n: res[n]["corrida"] for n in nombres},
        "escenarios": SALIDA_ESCENARIOS.name, "dudosas": SALIDA_DUDOSAS.name}, "cifras": res},
        ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("\n".join(out))
    return 0


# --- Lista representativa y manifiesto de desarrollo ---------------------------------------------------------------

DOC_MANIFIESTO = CASOS / "MANIFIESTO-DESARROLLO.md"
SALIDA_MANIFIESTO = CASOS / "MANIFIESTO-DESARROLLO.json"
LISTA_REPRESENTANTES = "legitimas-escenarios-45"
LISTA_VISTA = "alcance-91"
# alcance-desarrollo.json (#151) vive en exp/143-puntaje-token; se lee de este commit, como hace test_alcance.py (#45).
REV_ALCANCE = "29a4790"
RUTA_ALCANCE = "experiments/slm-directo/casos/alcance-desarrollo.json"
HISTORICOS = {"piloto_escrito", "trampa", "laboratorio"}


def representante(llamadas: list[str], dudosas: set[str]) -> str | None:
    """Regla de Mateo (2026-11-09), fijada antes de la etapa 3 y sin mirar resultados: la `ENT-L` del escenario; si no
    hay una que no sea dudosa, la llamada no dudosa más larga (desempate por `case_id`); sin ninguna, el escenario sale."""
    candidatas = [c for c in llamadas if c not in dudosas]
    if not candidatas:
        return None
    ent = [c for c in candidatas if c.startswith("ENT-L-")]
    assert len(ent) <= 1, llamadas
    return ent[0] if ent else min(candidatas, key=lambda c: (-len(texto(c)), c))


def _escribir_lista(nombre: str, comentario: list[str], ids: list[str]) -> None:
    (CASOS / "listas" / f"{nombre}.txt").write_text(
        "".join(f"# {l}\n" for l in comentario) + "".join(f"{c}\n" for c in ids), encoding="utf-8")


def cmd_manifiesto(_args) -> int:
    import subprocess
    alcance = json.loads(subprocess.run(["git", "-C", str(RAIZ), "show", f"{REV_ALCANCE}:{RUTA_ALCANCE}"], check=True,
                                        capture_output=True, text=True).stdout)["casos"]
    alcance.update(json.loads((CASOS / "alcance-legitimas-cotidianas.json").read_text(encoding="utf-8"))["casos"])
    esc = {c["case_id"]: c["escenario"] for c in json.loads(SALIDA_ESCENARIOS.read_text(encoding="utf-8"))["casos"]}
    dud = {c["case_id"]: c for c in json.loads(SALIDA_DUDOSAS.read_text(encoding="utf-8"))["casos"]}
    dudosas = {c for c, f in dud.items() if f["propuesta"] == "si"}
    grupos = defaultdict(list)
    for c, e in esc.items():
        grupos[e].append(c)
    rep = {e: representante(sorted(v), dudosas) for e, v in sorted(grupos.items())}
    representantes = sorted(r for r in rep.values() if r)

    ids = sorted(p.stem for p in (CASOS / "referencia").glob("*.json"))
    ids = [c for c in ids if referencia(c).get("particion", "desarrollo") == "desarrollo"]
    assert len(ids) == 244 and not any(c.startswith("CV2-T-") for c in ids), len(ids)
    estafas = [c for c in ids if referencia(c)["grupo"] == "corpus_v2" and referencia(c)["clase"] == "vishing"]
    casos_m = {}
    for c in ids:
        r = referencia(c)
        al = (alcance.get(c) or {}).get("alcance")
        if r["grupo"] in HISTORICOS:
            estado, motivo = "historico", "material anterior a corpus_v2 (AUDITORIA-53-HISTORICOS.md); no entra en la vista"
        elif c in estafas:
            estado = "cuenta"
            motivo = ("estafa de corpus_v2 dentro del alcance" + ("; sin pedido: falta la pregunta 5 de #145"
                                                                  if r["t_r_linea"] is None else ""))
        elif r["grupo"] == "corpus_v2":
            estado, motivo = (("fuera_del_alcance", "la llamada la inicia la persona o el número está agendado (#151)")
                              if al == "fuera" else
                              ("aparte", "legítima de corpus_v2 dentro del alcance, de familia o trabajo: contacto que "
                                         "estaría agendado (#45); se informa aparte, como en la etapa 2"))
        elif c in dudosas:
            estado, motivo = "dudosa", "señales " + ", ".join(dud[c]["anotador_1"]["cuentan"]).upper() + \
                " del criterio (LEGITIMAS-DUDOSAS.md); se informa aparte"
        elif c in representantes:
            estado, motivo = "cuenta", f"representa al escenario {esc[c]}"
        else:
            estado, motivo = "misma_situacion", f"escenario {esc[c]}, representado por {rep[esc[c]]}"
        casos_m[c] = {
            "grupo": r["grupo"], "clase": r["clase"], "familia": r.get("familia"), "alcance": al, "estado": estado,
            "escenario": esc.get(c), "motivo": motivo,
            "texto_sha256": hashlib.sha256((CASOS / "texto" / f"{c}.txt").read_bytes()).hexdigest(),
            "referencia_sha256": hashlib.sha256((CASOS / "referencia" / f"{c}.json").read_bytes()).hexdigest(),
        }
    cuenta = Counter(m["estado"] for m in casos_m.values())
    vista = [c for c in ids if casos_m[c]["estado"] == "cuenta"]
    assert sorted(vista) == sorted(estafas + representantes)
    _escribir_lista(LISTA_REPRESENTANTES, [
        f"Una legítima por escenario (corpus_desarrollo.py manifiesto, {len(representantes)} de 94), para la etapa 3 de #143.",
        "Regla de Mateo (2026-11-09), fijada antes de correr: la ENT-L del escenario (método de #45, 47 escenarios),",
        "sin las 7 dudosas; si no hay una ENT-L que no sea dudosa, la llamada no dudosa más larga. E16 y E42 salen: todas",
        "sus llamadas son dudosas. No reemplaza a legitimas-91 ni borra casos. Ver MANIFIESTO-DESARROLLO.md.",
        f"Uso: python correr.py --lista {LISTA_REPRESENTANTES} ..."], representantes)
    _escribir_lista(LISTA_VISTA, [
        f"Vista principal de desarrollo para la etapa 3 de #143: las {len(estafas)} estafas de corpus_v2 (todas dentro del",
        f"alcance) y las {len(representantes)} legítimas representativas de {LISTA_REPRESENTANTES}. Ver MANIFIESTO-DESARROLLO.md.",
        f"Uso: python correr.py --lista {LISTA_VISTA} ..."], estafas + representantes)
    meta = {
        "fecha": "2026-11-09",
        "estado": "propuesta sin discutir; ordena el corpus de desarrollo, no cambia texto/ ni referencia/",
        "decisiones": "Mateo, 2026-11-09: una legítima por escenario (la ENT-L), sin las 7 dudosas; un solo manifiesto de "
                      "desarrollo que diga qué cuenta y qué queda como histórico",
        "fuentes": {"escenarios": SALIDA_ESCENARIOS.name, "dudosas": SALIDA_DUDOSAS.name,
                    "alcance": f"{RUTA_ALCANCE} en {REV_ALCANCE} (exp/143-puntaje-token) y alcance-legitimas-cotidianas.json"},
        "estados": dict(sorted(cuenta.items())),
        "vista_principal": {"lista": f"listas/{LISTA_VISTA}.txt", "estafas": len(estafas),
                            "legitimas": len(representantes)},
        "representantes": {e: r for e, r in rep.items()},
    }
    SALIDA_MANIFIESTO.write_text(json.dumps({"_meta": meta, "casos": casos_m}, ensure_ascii=False, indent=2) + "\n",
                                 encoding="utf-8")
    reemplazar_bloque(DOC_MANIFIESTO, "estados", "\n".join(
        ["| Estado | Casos | Qué son |", "|---|---:|---|"] +
        [f"| `{e}` | {cuenta[e]} | {d} |" for e, d in (
            ("cuenta", f"la vista principal: {len(estafas)} estafas y {len(representantes)} legítimas representativas"),
            ("misma_situacion", "legítimas cotidianas que repiten un escenario ya representado"),
            ("dudosa", "legítimas cotidianas que chocan con las fuentes (criterio de dudosas)"),
            ("aparte", "legítimas de corpus_v2 dentro del alcance, de familia o trabajo"),
            ("fuera_del_alcance", "legítimas de corpus_v2 que inicia la persona o de un número agendado"),
            ("historico", "piloto escrito, trampas y laboratorio"))] + [f"| **total** | **{len(ids)}** | |"]))
    reemplazar_bloque(DOC_MANIFIESTO, "representantes", "\n".join(
        ["| Escenario | Llamadas | Representante | Por qué |", "|---|---|---|---|"] +
        [f"| {e} | {', '.join(f'`{c}`' + (' (dudosa)' if c in dudosas else '') for c in sorted(grupos[e]))} | "
         f"{f'`{r}`' if r else '—'} | "
         f"{'sale: todas sus llamadas son dudosas' if not r else 'la ENT-L' if r.startswith('ENT-L-') else 'no hay ENT-L no dudosa: la más larga'} |"
         for e, r in rep.items() if not (r and r.startswith("ENT-L-") and len(grupos[e]) == 1)]))
    print(json.dumps(meta["estados"], ensure_ascii=False), len(representantes))
    return 0


# --- main ----------------------------------------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("escenarios")
    p = sub.add_parser("ciego-dudosas")
    p.add_argument("destino", help="carpeta del paquete para los anotadores")
    p.add_argument("--clave", required=True, help="archivo de la clave, fuera de la carpeta del paquete")
    p = sub.add_parser("unir-dudosas")
    p.add_argument("anotaciones", nargs=2, help="los dos JSONL de los anotadores")
    p.add_argument("--clave", required=True)
    p = sub.add_parser("cifras")
    p.add_argument("corridas", help="carpeta de la etapa 2 (corridas/2026-11-07_alcance-etapa-2), solo lectura")
    sub.add_parser("manifiesto")
    args = ap.parse_args()
    return {"escenarios": cmd_escenarios, "ciego-dudosas": cmd_ciego_dudosas,
            "unir-dudosas": cmd_unir_dudosas, "cifras": cmd_cifras, "manifiesto": cmd_manifiesto}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
