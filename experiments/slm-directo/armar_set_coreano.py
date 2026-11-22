"""Pasa las traducciones coreanas de #144 al formato de casos y genera el manifiesto de hashes.

Uso: python3 -I armar_set_coreano.py <data/private/issue-144> <salida>
Lee las tres traducciones privadas, las fichas de Luciano (KO-01 a KO-09) y la propuesta de
marcas confirmada (tanda3/premarcado/PROPUESTA.json, KO-10 a KO-33). Nada de eso se versiona;
el manifiesto que genera está en docs/corpus/MANIFIESTO-144-SET-COREANO-2026-11-11.json.
Una línea por segmento de la fuente. Se quitan las notas de traducción y los huecos;
los marcadores de anonimización se reemplazan por datos ficticios fijos por caso.
"""
import hashlib, json, random, re, sys
from pathlib import Path

base, out = Path(sys.argv[1]), Path(sys.argv[2])
TRAD = ["ISSUE-144-COREANO-TRADUCCION-2026-11-07.md", "ISSUE-144-COREANO-TRADUCCION-2-2026-11-10.md",
        "ISSUE-144-COREANO-TRADUCCION-3-2026-11-11.md"]
INGLES = json.loads((base / "set-ingles/roles-protegida.json").read_text()).keys()
SEMILLA = 20261111
TODOS = [f"KO-{i:02d}" for i in range(1, 34)]
# Quién es la persona protegida (etiqueta de la fuente). Las demás etiquetas son OTRA.
# KO-05: la ficha aclara que atiende A. En el resto llama el estafador (A) y atiende B.
PROTEGIDA = {"KO-05": "A"}
NOMBRES = ["Park Ji-hoon", "Choi Eun-ji", "Jung Min-su", "Kang Hye-jin", "Yoon Sung-ho",
           "Lim Ji-won", "Han Dong-hyun", "Shin Mi-rae", "Oh Jae-won", "Seo Yu-na"]

def secciones():
    for f in TRAD:
        t = (base / f).read_text()
        for m in re.finditer(r"^## (KO-\d+) · `(vishing_\d+)`.*?\n(.*?)(?=^## KO-|\Z)", t, re.S | re.M):
            yield m.group(1), m.group(2), m.group(3)

SEG = re.compile(r"^(\d+)\. \[([\d,]+) s\] (.*)$")
ROT = re.compile(r"^(?:`\[sin texto[^]]*\]` )?\*\*([A-E])(?::\*\*|\*\* `\[([^]]*)\]`\*\*:\*\*) ?(.*)$")

def segmentos(cuerpo):
    for linea in cuerpo.split("### Ficha")[0].splitlines():
        m = SEG.match(linea)
        if not m:
            continue
        r = ROT.match(m.group(3))
        if not r:
            raise ValueError(f"rótulo raro: {linea[:80]}")
        hab, nota, texto = r.groups()
        # «[en la fuente: B — probable A]» y «probablemente lo dice B» corrigen el hablante
        c = re.search(r"en la fuente: [A-E] — probable ([A-E])", texto) or \
            re.search(r"(?:probablemente lo dice|probable continuación de) ([A-E])", nota or "")
        yield int(m.group(1)), float(m.group(2).replace(",", ".")), (c.group(1) if c else hab), texto, hab

def limpiar(texto, ficticios):
    for k, v in ficticios.items():
        texto = texto.replace(f"[{k}]", v)
    texto = re.sub(r"\s*`?\[[^]]*\]`?", "", texto)        # notas de traducción
    texto = texto.replace("*", "").strip()
    return re.sub(r"\s{2,}", " ", texto)

def ficha(cuerpo):
    m = re.search(r"### Ficha KO-\d+\n(.*?)(?=\n---|\Z)", cuerpo, re.S)
    campos = {}
    for l in (m.group(1) if m else "").splitlines():
        if l.startswith("- ") and ":" in l:
            sep = "?:" if "?:" in l else ("):" if "):" in l else ":")
            k, v = l[2:].split(sep, 1)
            campos[k.strip()] = v.strip()
    return campos

def campo(f, clave):
    return next((v for k, v in f.items() if clave in k), "")

def primer_segmento(valor):
    m = re.match(r"\s*(\d+)\b", valor)
    return int(m.group(1)) if m else None

def segmentos_marcados(valor):
    """Todos los números al comienzo del campo: «46 81 83» o «57 y 59» son varios pedidos."""
    m = re.match(r"\s*(\d+(?:\s*(?:,|y)?\s*\d+)*)", valor)
    return [int(n) for n in re.findall(r"\d+", m.group(1))] if m else []

libres = [n for n in range(1, 1000) if f"EXT-{n:03d}" not in INGLES]
ids = dict(zip(TODOS, (f"EXT-{n:03d}" for n in random.Random(SEMILLA).sample(libres, len(TODOS)))))

(out / "texto").mkdir(parents=True, exist_ok=True)
(out / "referencia").mkdir(exist_ok=True)
roles, corresp = {}, {}
PROP = json.loads((base / "tanda3/premarcado/PROPUESTA.json").read_text())
# KO-02: la ficha no trae número de T_R; lo marcó Claude con el mismo criterio que el pre-marcado.
AJUSTES = {"KO-02": {"t_r": 29, "pedidos": [29]}}
NOTA_IDIOMA = ("Traducción fiel al español neutro, sin adaptar al rioplatense, con wones y nombres coreanos: "
               "se decidió no adaptarla para que la IA no sesgara el texto; se conserva la estructura de la llamada real.")

for ko, fuente, cuerpo in secciones():
    f = ficha(cuerpo)
    de_ficha = campo(f, "Conservar").lower().startswith("conser")
    if not de_ficha and ko not in PROP:
        continue
    ext = ids[ko]
    rng = random.Random(f"{SEMILLA}-{ko}")
    ficticios = {"NOMBRE": rng.choice(NOMBRES), "TELÉFONO": f"010-{rng.randint(1000,9999)}-{rng.randint(1000,9999)}",
                 "NÚMERO": str(rng.randint(100000, 999999)), "ID": f"usuario{rng.randint(10,99)}"}
    segs = list(segmentos(cuerpo))
    if de_ficha:
        prot = PROTEGIDA.get(ko, "B")
        es_victima = lambda n, h, crudo: h == prot
    else:
        pr = PROP[ko]
        corr = {c["segmento"]: c["es"] for c in pr["correcciones_hablante"]}
        hab = pr["hablantes"]
        es_victima = lambda n, h, crudo: (corr.get(n) or hab.get(h) or hab.get(crudo)) == "victima"
    rol = {n: ("PROTEGIDA" if es_victima(n, h, crudo) else "OTRA") for n, _, h, _, crudo in segs}
    # Los segmentos que quedan vacíos al quitar las notas (ininteligibles en la fuente) no van al texto.
    segs = [x for x in segs if limpiar(x[3], ficticios)]
    primero = rol[segs[0][0]]
    lineas = [f"{'A' if rol[n] == primero else 'B'}: {limpiar(t, ficticios)}" for n, _, _, t, _ in segs]
    (out / "texto" / f"{ext}.txt").write_text("\n".join(lineas) + "\n")
    roles[ext] = {"protegida": "A" if primero == "PROTEGIDA" else "B", "origen": "externo"}
    seg_a_linea = {n: i for i, (n, *_ ) in enumerate(segs, 1)}
    L = lambda n: seg_a_linea.get(n)
    if de_ficha:
        t_r, t_c = primer_segmento(campo(f, "T_R")), primer_segmento(campo(f, "T_C"))
        pedidos, cumpl = segmentos_marcados(campo(f, "T_R")), segmentos_marcados(campo(f, "T_C"))
        if ko in AJUSTES:
            t_r, pedidos = AJUSTES[ko]["t_r"], AJUSTES[ko]["pedidos"]
        marcado = {"t_r": "Luciano Grosso (ficha)", "t_c": "Luciano Grosso (ficha)", "roles": "Luciano Grosso (ficha)"}
        if ko in AJUSTES:
            marcado["t_r"] = "Claude (Opus 5.5), con los criterios del pre-marcado; la ficha no traía un número"
        extra = {"ficha_original": {
            "conservar": campo(f, "Conservar"), "creible": campo(f, "creíble"), "es_estafa": campo(f, "es estafa"),
            "sospecha": campo(f, "sospechar"), "t_r": campo(f, "T_R"), "t_c": campo(f, "T_C"),
            "comienzo_final": campo(f, "Comienzo"), "hablantes": campo(f, "hablantes"),
            "direccion": campo(f, "Dirección"), "dudas": campo(f, "Dudas"), "decision": campo(f, "Decisión")}}
        revision = True
        sospecha = L(primer_segmento(campo(f, "sospechar")))
    else:
        t_r, t_c, pedidos = pr["t_r"], pr["t_c"], pr["pedidos"]
        cumpl = [t_c] if t_c else []
        quien = "pre-marcado de IA (gpt-6.1-sol, esfuerzo medio, con Orca)"
        marcado = {"t_r": quien, "t_c": quien, "roles": quien,
                   "confirmacion": "Luciano Grosso aprobó la lista de marcas el 2026-11-11, sin leer la conversación completa"}
        if pr["cambio"]:
            marcado["ajuste"] = ("Ajustado con los criterios de Luciano del 2026-11-11 (pedir nombre, ciudad o fecha de "
                                 "nacimiento no es T_R; el pedido de sitio es el sitio falso, no el portal): " + pr["cambio"])
        extra, revision, sospecha = {"premarcado": f"tanda3/premarcado/{ko}.json"}, False, None
    ref = {
        "case_id": ext, "grupo": "externo", "clase": "vishing", "clase_fuente": "vishing",
        "t_r_linea": L(t_r), "t_c_linea": L(t_c),
        "pedidos_lineas": [L(n) for n in pedidos if L(n)],
        "cumplimientos_lineas": [L(n) for n in cumpl if L(n)],
        "sospecha_linea": sospecha, "con_pedido": t_r is not None,
        "revision_humana": revision, "marcado_por": marcado, **extra,
        "notas": "T_R y T_C son el primer pedido y el primer cumplimiento; pedidos_lineas y cumplimientos_lineas "
                 "guardan todos los marcados (una línea por segmento de la fuente). " + NOTA_IDIOMA,
    }
    (out / "referencia" / f"{ext}.json").write_text(json.dumps(ref, indent=1, ensure_ascii=False) + "\n")
    corresp[ext] = {"caso": ko, "fuente": f"{fuente}.json", "segmento_a_linea": seg_a_linea}

(out / "roles-protegida.json").write_text(json.dumps(dict(sorted(roles.items())), indent=1) + "\n")
(out / "correspondencia.json").write_text(json.dumps(
    {"semilla_ids": SEMILLA, "ids_reservados": ids, "casos": dict(sorted(corresp.items()))}, indent=1, ensure_ascii=False) + "\n")
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
man = {str(p.relative_to(out)): sha(p) for p in sorted(out.rglob("*")) if p.is_file() and p.name != "MANIFIESTO.json"}
(out / "MANIFIESTO.json").write_text(json.dumps(man, indent=1) + "\n")
print(f"{len(roles)} casos:", ", ".join(f"{corresp[e]['caso']}→{e}" for e in sorted(corresp, key=lambda e: corresp[e]['caso'])))
