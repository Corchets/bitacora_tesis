"""Compuerta de #143 con un Tito sin punto ciego: la de siempre, pero que además despierta al SLM en la primera
línea marcada como mención o pedido. Necesita las corridas de #143 (rama exp/143-puntaje-token hasta su merge)."""
import importlib.util
import sys

from cargar import ACT, C, IDS, REF, estafa, linea_sensible

CARPETA = C / '2026-11-05_puntaje-token-150'
if not (CARPETA / 'analizar.py').exists():
    sys.exit(f'Falta {CARPETA}: está en la rama exp/143-puntaje-token.')
spec = importlib.util.spec_from_file_location('analizar_143', CARPETA / 'analizar.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

CORRIDAS = {'A1 v4': 'v4-a1', 'A1 v4 rep': 'v4-a1-rep', 'A2 v4': 'v4-a2', 'A2 v4 rep': 'v4-a2-rep',
            'A1 tarea': 'tarea-a1', 'A1 tarea rep': 'tarea-a1-rep'}
v2 = [i for i in IDS if REF[i]['grupo'] == 'corpus_v2']
est, leg = [i for i in v2 if estafa(i)], [i for i in v2 if not estafa(i)]
honesto = {i: min([x for x in (ACT[i], linea_sensible(i, con_tr=False)) if x], default=None) for i in IDS}


def mejor(filas, compuerta):
    """Mejor punto con FA ≤ FA_MAX: más estafas, después más avisos antes del pedido, después la política más simple."""
    best = None
    for p in a.POLITICAS:
        q = {i: a.puntajes(a.serie(filas[i], compuerta[i] if compuerta else False), p) for i in v2}
        for u in a.UMBRALES:
            av = {i: a.primer_aviso(q[i], u) for i in v2}
            fa = sum(av[i] is not None for i in leg)
            if fa > a.FA_MAX:
                continue
            d = sum(av[i] is not None for i in est)
            antes = sum(1 for i in est if REF[i].get('t_r_linea') and av[i] and av[i] < REF[i]['t_r_linea'])
            k = (d, antes, -a.POLITICAS.index(p))
            if best is None or k > best[0]:
                best = (k, f'{d}/46, {antes} antes, {fa} FA ({p} {u:g})')
    return best[1]


print('| Corrida | SLM solo | Tito→SLM | Tito sin punto ciego→SLM |\n|---|---|---|---|')
for nombre, carpeta in CORRIDAS.items():
    filas, _ = a.leer_corrida(next(CARPETA.glob(f'{carpeta}/2026*')), 'slm')
    print(f'| {nombre} | {mejor(filas, None)} | {mejor(filas, ACT)} | {mejor(filas, honesto)} |')
