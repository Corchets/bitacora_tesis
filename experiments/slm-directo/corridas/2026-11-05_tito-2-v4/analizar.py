"""v4 con roles: Tito viejo 2.0 y SLM solo, contra v4 con Tito viejo y contra v1. No corre modelos ni lee la reserva.

Sostiene las cifras de analisis.md. Uso, desde esta carpeta:
    python -I analizar.py
"""
import collections, csv, difflib, io, json, re, unicodedata, zipfile
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
W = AQUI.parents[1]
C = W / 'corridas'
def uno(patron): (p,) = C.glob(patron); return p
RUNS = {  # nombre: (carpeta o ZIP, detector)
    'v4 Tito viejo': (uno('2026-11-04_prompt-v4-tito-sin-indicio/a/2026*'), 'tito-slm-sin-indicio'),
    'v4 Tito viejo rep': (uno('2026-11-04_tanda-roles-tito-sin-indicio/d/2026*'), 'tito-slm-sin-indicio'),
    'v4 Tito 2.0': (uno('2026-11-05_tito-2-v4/a/2026*'), 'tito-viejo-2'),
    'v4 SLM solo': (uno('2026-11-05_tito-2-v4/b/2026*'), 'slm'),
    'v1 Tito viejo': (uno('2026-11-04_sin-indicio-150/b/2026*'), 'tito-slm-sin-indicio'),
    'v1 SLM solo': (uno('2026-11-04_sin-indicio-150/a/2026*'), 'slm'),
    'v1 Tito 2.0 (Nacho)': (C / '2026-11-05_TITO-VIEJO-2-COLAB.zip', 'tito-viejo-2'),
}
def leer(fuente, nombre):
    if fuente.suffix == '.zip':
        with zipfile.ZipFile(fuente) as z:
            (n,) = [x for x in z.namelist() if x.endswith('/' + nombre)]
            return z.read(n).decode('utf-8-sig')
    return (fuente / nombre).read_text(encoding='utf-8-sig')
R, M = {}, {}
for k, (fuente, det) in RUNS.items():
    d = collections.defaultdict(list)
    for f in csv.DictReader(io.StringIO(leer(fuente, 'actualizaciones.csv'))):
        if f['detector'] == det: d[f['case_id']].append(f)
    R[k], M[k] = d, json.loads(leer(fuente, 'manifiesto.json'))
ids = sorted(R['v4 Tito 2.0'])
assert len(ids) == 150 and not [i for i in ids if 'CV2-T' in i]
for k, m in M.items():
    assert sorted(R[k]) == ids and m['casos'] == M['v4 Tito viejo']['casos'] and m['particion'] == 'desarrollo', k
    assert m['ollama']['version'] == '0.40.14' and m['ollama']['digests']['gemma4:e2b-it-q4_K_M'].startswith('b37049369adf'), k
    if m.get('filtro_tito'): assert m['filtro_tito']['artefacto_sha256'].startswith('fb601eaa') and m['filtro_tito']['umbral'] == 0.5, k
for k in ('v4 Tito viejo', 'v4 Tito viejo rep', 'v4 Tito 2.0', 'v4 SLM solo'):
    assert '92df75a22c2746fb' in json.dumps(M[k]['prompts']), k
for k in ('v4 Tito 2.0', 'v4 SLM solo'):
    assert M[k]['codigo']['commit'] == '2136a9f1c71bd94fc585f544d3a1a5470f6eee06' and not M[k]['codigo']['cambios_sin_commit_en_la_carpeta'] and not M[k]['interrumpida']

ref = {i: json.loads((W / f'casos/referencia/{i}.json').read_text(encoding='utf-8')) for i in ids}
vis = [i for i in ids if ref[i]['clase'] == 'vishing']; leg = [i for i in ids if ref[i]['clase'] != 'vishing']
com = [i for i in leg if ref[i]['clase'] == 'legitima']; dif = [i for i in leg if ref[i]['clase'] == 'legitima_dificil']
tr = lambda i: ref[i].get('t_r_linea')
fila = lambda c, i: next((r for r in c[i] if r['aviso'].lower() == 'true'), None)
def av(c, i): f = fila(c, i); return int(f['linea']) if f else None
act = lambda c, i: next((int(f['linea']) for f in c[i] if f['consulta'] != 'omitida'), None)
S = {k: {i for i in ids if av(R[k], i)} for k in R}

# «Cita el pedido» y «cita solo a la víctima», con la definición de comparar_con_v1_colab.py.
def norm(s):
    s = unicodedata.normalize('NFKD', s.lower()); return ' '.join(''.join(x for x in s if x.isalnum() or x == ' ').split())
def turnos(i): return [m.groups() for l in (W / f'casos/texto/{i}.txt').read_text(encoding='utf-8').splitlines() if (m := re.match(r'^([AB]):\s*(.*)$', l))]
def citadas(f, i):
    T = turnos(i)[:int(f['linea'])]; res = set()
    for frag in f['evidencia'].split('\n'):
        x = norm(re.sub(r'^(?:[AB]|PROTEGIDA|OTRA):\s*', '', re.sub(r'^\s*\d+[.)]\s*', '', frag)))
        if len(x) < 4: continue
        hit = [n + 1 for n, (_, t) in enumerate(T) if x in norm(t) or norm(t) in x]
        if not hit:
            s, n = max((difflib.SequenceMatcher(None, x, norm(t)).ratio(), n + 1) for n, (_, t) in enumerate(T))
            if s > .6: hit = [n]
        if hit: res.add(hit[-1])
    return res

print('condición | estafas | corpus v2 | FA | comunes | difíciles | FA corpus v2 | antes/en/después | cita el pedido | solo víctima | consultas | fallos')
for k, c in R.items():
    conp = [i for i in vis if tr(i) and av(c, i)]
    t = lambda f: sum(1 for i in conp if f(av(c, i), tr(i)))
    ped = vict = 0
    for i in conp:
        cit = citadas(fila(c, i), i); T = turnos(i)
        ped += bool(cit & ({e['linea'] for e in ref[i]['evidencia'] if e['evento'] == 'pedido'} | {tr(i)}))
        vict += bool(cit) and all(T[x - 1][0] != T[tr(i) - 1][0] for x in cit)
    fs = [f for i in ids for f in c[i]]
    v2 = lambda g: sum(1 for i in g if i in S[k] and ref[i]['grupo'] == 'corpus_v2')
    print(f"{k} | {len(S[k] & set(vis))} | {v2(vis)}/46 | {len(S[k] & set(leg))} | {len(S[k] & set(com))} | {len(S[k] & set(dif))} | {v2(leg)}/51 | "
          f"{t(lambda a, b: a < b)}/{t(lambda a, b: a == b)}/{t(lambda a, b: a > b)} | {ped} | {vict} | {sum(f['consulta'] != 'omitida' for f in fs)} | {sum(f['valida'].lower() != 'true' for f in fs)}")

print()
for x, y in (('v4 Tito viejo', 'v4 Tito viejo rep'), ('v4 Tito viejo', 'v4 Tito 2.0'), ('v4 Tito viejo', 'v4 SLM solo'), ('v1 Tito viejo', 'v1 Tito 2.0 (Nacho)'), ('v1 Tito viejo', 'v1 SLM solo')):
    print(f"{x} -> {y}: estafas gana {sorted(S[y] - S[x] & set(vis))} pierde {sorted(S[x] - S[y] & set(vis))}; "
          f"FA agrega {sorted(S[y] - S[x] & set(leg))} saca {sorted(S[x] - S[y] & set(leg))}")
a, b = R['v4 Tito viejo'], R['v4 Tito 2.0']
print('\nTito 2.0 contra Tito viejo, con v4: activación distinta', [(i, act(a, i), act(b, i)) for i in ids if act(a, i) != act(b, i)],
      '; línea de aviso distinta', [(i, av(a, i), av(b, i)) for i in ids if av(a, i) != av(b, i)])
s = R['v4 SLM solo']
antes = [(i, ref[i]['clase'], av(s, i), act(a, i)) for i in sorted(S['v4 SLM solo']) if act(a, i) is None or av(s, i) < act(a, i)]
print('SLM solo avisa antes de que Tito viejo active, o donde no activa:', len(antes), antes)
