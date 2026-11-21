"""Test para el alcance (#45): quién inicia cada llamada de la reserva y controles del lote nuevo.

Ver casos/TEST-ALCANCE.md. Ningún subcomando corre detectores ni imprime texto de las llamadas.

Uso:
    python -I test_alcance.py ciego DESTINO CLAVE
        Arma la entrada ciega: los 200 CV2-T-* renombrados llamada-001…200, mezclados con semilla 45, en 4 lotes de
        50 más los 10 primeros del lote siguiente. Cada archivo trae solo las líneas numeradas con A/B; la clave
        (llamada ↔ case_id) va a otra carpeta.
    python -I test_alcance.py unir SALIDAS CLAVE
        Junta las anotaciones finales (SALIDAS/lote-K-r2.json) en casos/alcance-reserva.json y aplica la regla.
    python -I test_alcance.py controles [--rev-desarrollo REV]
        Forma (largo, variantes de ASR, DNI, «usted», comienzo) y parecido del lote nuevo contra las 94 legítimas de
        desarrollo (PR #155), que se leen de Git en REV porque esta rama no las tiene.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import re
import statistics
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CASOS = RAIZ / "casos"
SALIDA_ALCANCE = CASOS / "alcance-reserva.json"
LOTE_NUEVO = CASOS / "legitimas-entrantes-test.jsonl"
# Rama corpus/legitimas-cotidianas (PR #155) al 2026-11-07: las 91 de Evaristo (LEG-*, LEG2-* y ENT-L-*, con el
# mismo texto que en claude/determined-wright-tsxh08) y las 3 ENT-L-SELECCION-*. Son las 94 legítimas de desarrollo.
REV_DESARROLLO = "ac8a81f3da9e1a55f05722562053c08601829cd5"
RUTA_CASOS_GIT = "experiments/slm-directo/casos"

SEMILLA, LOTES, POR_LOTE, SOLAPE = 45, 4, 50, 10


# --- Carga -------------------------------------------------------------------------------------------------------

def lineas_de(texto: str) -> list[str]:
    return [l for l in texto.splitlines() if l.strip()]


def reserva_ids() -> list[str]:
    return sorted(p.stem for p in (CASOS / "texto").glob("CV2-T-*.txt"))


def texto_local(case_id: str) -> list[str]:
    return lineas_de((CASOS / "texto" / f"{case_id}.txt").read_text(encoding="utf-8"))


def referencia_local(case_id: str) -> dict:
    return json.loads((CASOS / "referencia" / f"{case_id}.json").read_text(encoding="utf-8"))


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(RAIZ.parents[1]), *args], check=True, capture_output=True, text=True).stdout


def desarrollo_git(rev: str) -> dict[str, dict]:
    """Las 94 legítimas de desarrollo en `rev`: texto, referencia y rol de PROTEGIDA."""
    rutas = _git("ls-tree", "-r", "--name-only", rev, "--", f"{RUTA_CASOS_GIT}/referencia").splitlines()
    roles = json.loads(_git("show", f"{rev}:{RUTA_CASOS_GIT}/roles-protegida.json"))
    casos = {}
    for ruta in rutas:
        cid = ruta.rsplit("/", 1)[1][:-5]
        if re.match(r"^(LEG-|LEG2-|ENT-L-)", cid):
            casos[cid] = {
                "texto": lineas_de(_git("show", f"{rev}:{RUTA_CASOS_GIT}/texto/{cid}.txt")),
                "referencia": json.loads(_git("show", f"{rev}:{RUTA_CASOS_GIT}/referencia/{cid}.json")),
                "protegida": roles[cid]["protegida"],
            }
    return casos


def lote_nuevo() -> list[dict]:
    return [json.loads(l) for l in LOTE_NUEVO.read_text(encoding="utf-8").splitlines() if l.strip()]


# --- ciego -------------------------------------------------------------------------------------------------------

def ciego(destino: Path, clave_dir: Path) -> None:
    cids = reserva_ids()
    assert len(cids) == 200, len(cids)
    random.Random(SEMILLA).shuffle(cids)
    nombres = {f"llamada-{i:03d}": c for i, c in enumerate(cids, start=1)}
    orden = list(nombres)
    lotes = {}
    for k in range(LOTES):
        sig = (k + 1) % LOTES
        lotes[f"lote-{k + 1}"] = orden[k * POR_LOTE:(k + 1) * POR_LOTE] + orden[sig * POR_LOTE:sig * POR_LOTE + SOLAPE]
    for lote, miembros in lotes.items():
        carpeta = destino / lote
        carpeta.mkdir(parents=True, exist_ok=False)
        for nombre in miembros:
            ls = texto_local(nombres[nombre])
            assert all(l[:3] in ("A: ", "B: ") for l in ls), nombre
            (carpeta / f"{nombre}.txt").write_text("".join(f"L{n} {l}\n" for n, l in enumerate(ls, 1)), encoding="utf-8")
    (destino / "salida").mkdir()
    clave_dir.mkdir(parents=True, exist_ok=False)
    (clave_dir / "clave.json").write_text(
        json.dumps({"semilla": SEMILLA, "lotes": lotes, "llamadas": nombres}, ensure_ascii=False, indent=1), encoding="utf-8")
    for f in destino.glob("lote-*/*.txt"):
        t = f.read_text(encoding="utf-8")
        assert "CV2" not in t and "vishing" not in t.lower(), f.name
    print({k: len(v) for k, v in lotes.items()}, "llamadas distintas:", len(nombres))


# --- unir --------------------------------------------------------------------------------------------------------

REGLA = {
    "inicia": "otra si OTRA hizo esta llamada (PROTEGIDA atiende u OTRA se presenta como quien llama, aunque devuelva un llamado o llame por un trámite previo); protegida si la hizo PROTEGIDA (OTRA atiende con el saludo de una empresa u organismo, o PROTEGIDA dice que llama o devuelve el llamado); no_se_sabe si el texto no alcanza.",
    "numero": "agendado solo si el texto muestra que OTRA es un contacto que llama desde su teléfono de siempre (PROTEGIDA la reconoce y saluda por el nombre antes de que se presente, o dice que vio que era ella); si no, no_agendado.",
    "alcance": "dentro si inicia = otra y numero = no_agendado; fuera si inicia = protegida o numero = agendado; dudoso si inicia = no_se_sabe.",
    "origen": "Copiada de _meta.regla de alcance-desarrollo.json (rama exp/143-puntaje-token, 2026-11-06).",
}
ROLES = (
    "La reserva no tiene roles-protegida.json, así que el mismo agente marcó primero quién es PROTEGIDA, con esta regla "
    "escrita antes de anotar: 1) si una parte habla en nombre de una empresa, banco, organismo, comercio, servicio o "
    "institución, o dice hacerlo, PROTEGIDA es la otra; 2) si las dos hablan como particulares, PROTEGIDA es a quien le "
    "piden, le proponen o le aconsejan algo; 3) si con eso no alcanza, PROTEGIDA es quien atiende la llamada, con "
    "rol_dudoso = true (el mismo criterio de roles-protegida.json para desarrollo, 2026-11-04)."
)
PRECISION_R2 = (
    "Precisión de inicia, 2026-11-07. Decidir en este orden: 1) si alguien dice que llama o que devuelve un llamado, o "
    "si alguien atiende con el saludo de una empresa u organismo, eso decide, como en la regla; 2) si no, quien abre "
    "presentándose o con el motivo de la llamada («te habla…», «te llamo de…», «¿hablo con…?», «quería consultar…», "
    "«tengo un problema con…») es quien llamó, y quien responde con una fórmula de atender («hola», «¿sí?», «diga», "
    "«¿quién habla?», «¿en qué te puedo ayudar?») es quien atendió, aunque nadie diga literalmente «llamo»; "
    "3) no_se_sabe solo si con 1 y 2 no alcanza o si hay señales de los dos lados que se contradicen."
)


def alcance(inicia: str, numero: str) -> str:
    if numero == "agendado" or inicia == "protegida":
        return "fuera"
    return "dentro" if inicia == "otra" else "dudoso"


def unir(salidas: Path, clave_dir: Path, primera: Path | None) -> None:
    clave = json.loads((clave_dir / "clave.json").read_text(encoding="utf-8"))
    finales = {lote: json.loads((salidas / f"{lote}-r2.json").read_text(encoding="utf-8")) for lote in clave["lotes"]}
    for lote, d in finales.items():
        assert set(d) == set(clave["lotes"][lote]), lote

    por_llamada: dict[str, list[tuple[str, dict]]] = {}
    for lote, d in finales.items():
        for nombre, anot in d.items():
            por_llamada.setdefault(nombre, []).append((lote, anot))

    casos, desacuerdos = {}, 0
    solape_igual = solape = 0
    for nombre, anots in sorted(por_llamada.items()):
        lote, base = anots[0]
        fila = {
            "protegida": base["protegida"],
            "rol_dudoso": any(a["rol_dudoso"] for _, a in anots),
            "inicia": base["inicia"],
            "numero": base["numero"],
            "evidencia": base["evidencia"],
            "nota": base.get("nota", ""),
            "lotes": [l for l, _ in anots],
        }
        if len(anots) == 2:
            solape += 1
            (_, a), (_, b) = anots
            iguales = a["inicia"] == b["inicia"] and a["numero"] == b["numero"] and a["protegida"] == b["protegida"]
            solape_igual += iguales
            if not iguales:
                desacuerdos += 1
                fila["inicia"] = "no_se_sabe"
                fila["rol_dudoso"] = fila["rol_dudoso"] or a["protegida"] != b["protegida"]
                fila["nota"] = (f"Desacuerdo entre anotadores ({a['inicia']}/{a['numero']} contra "
                                f"{b['inicia']}/{b['numero']}): queda no_se_sabe. " + fila["nota"]).strip()
                fila["evidencia_segunda"] = b["evidencia"]
        fila["alcance"] = alcance(fila["inicia"], fila["numero"])
        casos[clave["llamadas"][nombre]] = fila

    conteo = Counter(f["alcance"] for f in casos.values())
    por_clase = {}
    for clase, prefijo in (("estafas", "CV2-T-V-"), ("legitimas", "CV2-T-L-")):
        filas = [f for c, f in casos.items() if c.startswith(prefijo)]
        por_clase[clase] = {
            "casos": len(filas),
            "alcance": dict(Counter(f["alcance"] for f in filas)),
            "inicia": dict(Counter(f["inicia"] for f in filas)),
            "agendado": sum(f["numero"] == "agendado" for f in filas),
            "rol_dudoso": sum(f["rol_dudoso"] for f in filas),
        }

    acuerdo_r1 = None
    if primera is not None:
        iniciales = {lote: json.loads((primera / f"{lote}.json").read_text(encoding="utf-8")) for lote in clave["lotes"]}
        iguales = total = 0
        for nombre, anots in por_llamada.items():
            if len(anots) == 2:
                (la, _), (lb, _) = anots
                total += 1
                iguales += iniciales[la][nombre]["inicia"] == iniciales[lb][nombre]["inicia"]
        acuerdo_r1 = f"{iguales}/{total}"

    meta = {
        "fecha": "2026-11-07",
        "para": "#45: quién inicia cada llamada de la reserva, para el alcance del ADR 0003 (entrantes de números no agendados)",
        "regla": REGLA,
        "roles": ROLES,
        "precision_r2": PRECISION_R2,
        "metodo": (
            "Anotación a ciegas por cuatro agentes que leyeron solo las transcripciones con A/B y líneas numeradas, "
            "renombradas llamada-001…200 y mezcladas (semilla 45): sin case_id, clase, referencia, prompts ni "
            "resultados. Cada uno anotó 60: un lote de 50 y los 10 primeros del lote siguiente, así que 40 llamadas "
            "tienen dos anotaciones. La sesión que preparó la entrada guardó la clave aparte y procesó la reserva con "
            "scripts, sin leer las transcripciones (test_alcance.py). En la primera pasada, inicia coincidió en "
            f"{acuerdo_r1} de las llamadas con dos anotaciones y los roles en todas: unos anotadores exigían que "
            "alguien dijera literalmente que llama y otros lo deducían de cómo empieza la conversación. Se escribió la "
            "precisión r2 sin mirar las llamadas ni la clase, y cada agente volvió a anotar su lote."
        ),
        "acuerdo": {"inicia_primera_pasada": acuerdo_r1, "todo_igual_r2": f"{solape_igual}/{solape}"},
        "desacuerdos": f"{desacuerdos}; regla escrita antes de unir: si las dos anotaciones no coinciden, inicia = no_se_sabe (alcance dudoso).",
        "conteo": dict(conteo),
        "por_clase": por_clase,
        "advertencia": (
            "Este archivo nombra casos de la reserva y cita frases cortas de sus transcripciones: no va a "
            "laboratorio-main. Nadie corrió detectores sobre la reserva para hacerlo."
        ),
    }
    SALIDA_ALCANCE.write_text(json.dumps({"_meta": meta, "casos": casos}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"acuerdo": meta["acuerdo"], "desacuerdos": desacuerdos, "conteo": meta["conteo"],
                      "por_clase": por_clase}, ensure_ascii=False, indent=1))


# --- controles ---------------------------------------------------------------------------------------------------

RX = {
    "DNI": re.compile(r"\bd\.?\s?n\.?\s?i\b", re.I),
    "fecha de nacimiento": re.compile(r"fecha de nacimiento|naciste|naci[oó]", re.I),
    "usted": re.compile(r"\busted(es)?\b", re.I),
}


def forma(nombre: str, casos: list[tuple[list[str], bool, str | None]]) -> dict:
    """casos: (líneas, variante_asr, quién es PROTEGIDA o None)."""
    n = len(casos)
    largos = [len(ls) for ls, _, _ in casos]
    fila = {
        "conjunto": nombre,
        "n": n,
        "lineas": f"{min(largos)}–{max(largos)} (mediana {statistics.median(largos):g})",
        "asr": sum(asr for _, asr, _ in casos),
    }
    for k, rx in RX.items():
        fila[k] = sum(bool(rx.search("\n".join(ls))) for ls, _, _ in casos)
    con_rol = [(ls, p) for ls, _, p in casos if p]
    fila["protegida_primero"] = f"{sum(ls[0][0] == p for ls, p in con_rol)}/{len(con_rol)}" if con_rol else "—"
    fila["palabras_primera_linea"] = statistics.median(len(ls[0].split()) - 1 for ls, _, _ in casos)
    return fila


def normalizar(lineas: list[str]) -> list[str]:
    t = " ".join(re.sub(r"^[AB]:\s*", "", l) for l in lineas).lower()
    t = "".join(ch for ch in unicodedata.normalize("NFD", t) if unicodedata.category(ch) != "Mn")
    return re.findall(r"[a-zñ0-9]+", t)


class Espacio:
    """Coseno TF-IDF de palabras (1 y 2) y cobertura de bigramas pesados por IDF."""

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


def controles(rev: str) -> None:
    dev = desarrollo_git(rev)
    nuevo = lote_nuevo()
    alc = json.loads(SALIDA_ALCANCE.read_text(encoding="utf-8"))["casos"] if SALIDA_ALCANCE.exists() else {}
    roles_dev = json.loads((CASOS / "roles-protegida.json").read_text(encoding="utf-8"))

    def locales(prefijo: str, roles: dict) -> list:
        ids = sorted(p.stem for p in (CASOS / "texto").glob(f"{prefijo}*.txt"))
        return [(texto_local(c), bool(referencia_local(c).get("variante_asr")),
                 (roles.get(c) or {}).get("protegida")) for c in ids]

    filas = [
        forma("estafas de desarrollo (corpus_v2)", locales("CV2-D-V-", roles_dev)),
        forma("estafas de la reserva", locales("CV2-T-V-", alc)),
        forma("legítimas viejas de la reserva", locales("CV2-T-L-", alc)),
    ]
    for etiqueta, patron in (("LEG", "LEG-"), ("LEG2", "LEG2-"), ("ENT-L, con las 3 de selección", "ENT-L-"), ("las 94 de desarrollo", "")):
        filas.append(forma(etiqueta, [(c["texto"], bool(c["referencia"].get("variante_asr")), c["protegida"])
                                      for cid, c in sorted(dev.items()) if cid.startswith(patron)]))
    filas.append(forma("lote nuevo de test (ENT-T)", [(c["texto"], bool(c["variante_asr"]), c["protegida"]) for c in nuevo]))
    print("| Conjunto | n | Líneas | ASR | DNI | Fecha de nac. | «usted» | PROTEGIDA habla primero | Palabras de la 1.ª línea (mediana) |")
    print("|---|---:|---|---:|---:|---:|---:|---:|---:|")
    for f in filas:
        print(f"| {f['conjunto']} | {f['n']} | {f['lineas']} | {f['asr']} | {f['DNI']} | {f['fecha de nacimiento']} | "
              f"{f['usted']} | {f['protegida_primero']} | {f['palabras_primera_linea']:g} |")

    comp = Counter((c["familia"], c["tipo_legitima"]) for c in nuevo)
    print("\nLote nuevo por familia y tipo:")
    for fam in sorted({f for f, _ in comp}):
        print(f"  {fam}: " + ", ".join(f"{t} {n}" for (f2, t), n in sorted(comp.items()) if f2 == fam))
    malos = [c["case_id"] for c in nuevo if not (20 <= len(c["texto"]) <= 38)
             or any(l[:3] not in ("A: ", "B: ") for l in c["texto"]) or c["texto"][0][0] != "A"]
    print("Fuera de formato o de 20–38 líneas:", malos or "ninguna")

    # Parecido: calibración con las 15 LEG2 que, según sus notas, reescriben una LEG.
    norm = {cid: normalizar(c["texto"]) for cid, c in dev.items()}
    esp = Espacio(list(norm.values()))
    pares = {}
    for cid, c in dev.items():
        r = c["referencia"]
        m = re.findall(r"LEG-[A-Z]{2}-\d{2}", f"{r.get('notas') or ''} {r.get('origen') or ''}")
        if cid.startswith("LEG2-") and m:
            pares[cid] = m[0]
    umbral_cos = min(esp.coseno(norm[a], norm[b]) for a, b in pares.items())
    umbral_cob = min(esp.cobertura(norm[b], norm[a]) for a, b in pares.items())
    print(f"\nParecido. {len(pares)} reescrituras declaradas: coseno mínimo {umbral_cos:.3f}, cobertura mínima {umbral_cob:.3f}.")

    nuevos = {c["case_id"]: normalizar(c["texto"]) for c in nuevo}
    marcadas, maximos_cos, maximos_cob = [], [], []
    for cid, pal in nuevos.items():
        cos, con = max((esp.coseno(pal, d), k) for k, d in norm.items())
        cob, con_cob = max((esp.cobertura(d, pal), k) for k, d in norm.items())
        maximos_cos.append(cos)
        maximos_cob.append(cob)
        if cos >= umbral_cos or cob >= umbral_cob:
            marcadas.append(f"{cid} (coseno {cos:.3f} con {con}; cobertura {cob:.3f} de {con_cob})")
    print(f"Contra las 94: coseno máximo {max(maximos_cos):.3f} (mediana de los máximos {statistics.median(maximos_cos):.3f}); "
          f"cobertura máxima {max(maximos_cob):.3f} (mediana {statistics.median(maximos_cob):.3f}).")
    print("Marcadas como posible reescritura:", marcadas or "ninguna")

    internos = []
    ids = sorted(nuevos)
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            internos.append((esp.coseno(nuevos[a], nuevos[b]), a, b))
    peor = max(internos)
    print(f"Dentro del lote: coseno máximo {peor[0]:.3f} ({peor[1]} y {peor[2]}); pares sobre {umbral_cos:.3f}: "
          f"{sum(c >= umbral_cos for c, _, _ in internos)}.")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("ciego"); a.add_argument("destino", type=Path); a.add_argument("clave", type=Path)
    b = sub.add_parser("unir"); b.add_argument("salidas", type=Path); b.add_argument("clave", type=Path)
    b.add_argument("--primera", type=Path, help="carpeta con lote-K.json de la primera pasada, para medir su acuerdo")
    c = sub.add_parser("controles"); c.add_argument("--rev-desarrollo", default=REV_DESARROLLO)
    args = ap.parse_args()
    if args.cmd == "ciego":
        ciego(args.destino, args.clave)
    elif args.cmd == "unir":
        unir(args.salidas, args.clave, args.primera)
    else:
        controles(args.rev_desarrollo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
