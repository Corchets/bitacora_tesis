"""Carga común: corridas por línea, referencias y textos de los 150 casos de desarrollo."""
import csv
import collections
import json
from pathlib import Path

csv.field_size_limit(10**9)
EXP = Path(__file__).resolve().parents[2]  # experiments/slm-directo
C = EXP / 'corridas'

CORRIDAS = {  # nombre: (carpeta dentro de corridas/, detector)
    'v1 solo': ('2026-11-04_sin-indicio-150/a/2026*', 'slm'),
    'v1 + Tito': ('2026-11-04_sin-indicio-150/b/2026*', 'tito-slm-sin-indicio'),
    'v4 solo': ('2026-11-05_tito-2-v4/b/2026*', 'slm'),
    'v4 + Tito': ('2026-11-04_tanda-roles-tito-sin-indicio/d/2026*', 'tito-slm-sin-indicio'),  # sigue tras el aviso
    'v4 + Tito 2.0': ('2026-11-05_tito-2-v4/a/2026*', 'tito-viejo-2'),
    'reglas v1': ('2026-10-21_200147_m1-reglas-150', 'reglas'),
}


def leer(patron, detector):
    """Filas de un actualizaciones.csv por caso, ordenadas por línea."""
    (p,) = C.glob(f'{patron}/actualizaciones.csv')
    filas = collections.defaultdict(list)
    with open(p, encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if r['detector'] == detector:
                filas[r['case_id']].append(r)
    for v in filas.values():
        v.sort(key=lambda r: int(r['linea']))
    return dict(filas)


F = {nombre: leer(*v) for nombre, v in CORRIDAS.items()}
IDS = sorted(F['v4 + Tito'])
assert len(IDS) == 150 and not any(i.startswith('CV2-T-') for i in IDS), 'solo desarrollo; la reserva no se lee'
REF = {i: json.loads((EXP / 'casos/referencia' / f'{i}.json').read_text(encoding='utf-8')) for i in IDS}
TXT = {i: [l for l in (EXP / 'casos/texto' / f'{i}.txt').read_text(encoding='utf-8').splitlines() if l.strip()]
       for i in IDS}


def estafa(i):
    return REF[i]['clase'] == 'vishing'


def activacion(filas):
    """Primera línea en que la compuerta dejó consultar al SLM; None si Tito nunca activó."""
    return next((int(r['linea']) for r in filas if r['consulta'] != 'omitida'), None)


def primer_aviso(filas):
    return next((int(r['linea']) for r in filas if r['aviso'].lower() == 'true'), None)


def linea_sensible(i, con_tr=True):
    """Primera línea sensible: la primera marcada como mención o pedido en la referencia, o T_R."""
    ls = [e['linea'] for e in REF[i].get('evidencia', []) if e['evento'] in ('mencion', 'pedido')]
    if con_tr and REF[i].get('t_r_linea'):
        ls.append(REF[i]['t_r_linea'])
    return min(ls, default=None)


ACT = {i: activacion(F['v4 + Tito'][i]) for i in IDS}
assert ACT == {i: activacion(F['v1 + Tito'][i]) for i in IDS}, 'Tito no depende del prompt'
TITO = {i: {int(r['linea']): float(r['tito_puntaje']) for r in F['v4 + Tito'][i] if r['tito_puntaje']} for i in IDS}
