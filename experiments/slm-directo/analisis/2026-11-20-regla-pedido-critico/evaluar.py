"""Exploración: el modelo de la evaluación final más la regla de pedido crítico, sin correr el modelo.

El aviso del modelo sale de las corridas de la evaluación final (primer aviso, la regla de analizar.py); la regla se
aplica sobre los textos. El híbrido avisa en la primera de las dos líneas. Uso desde la raíz:
    git archive origin/reserva/test experiments/slm-directo/corridas/2026-11-12_evaluacion-final/desarrollo \
        | tar -x -C /tmp/eval-final-dev --strip-components=4
    git archive origin/reserva/test experiments/slm-directo/corridas/2026-11-12_evaluacion-final/test_reservado \
        experiments/slm-directo/casos/legitimas-entrantes-test.jsonl experiments/slm-directo/casos/alcance-reserva.json \
        experiments/slm-directo/casos/texto experiments/slm-directo/casos/referencia | tar -x -C /tmp/eval-final-test
    python3 -I experiments/slm-directo/analisis/2026-11-20-regla-pedido-critico/evaluar.py /tmp/eval-final-dev /tmp/eval-final-test

Las legítimas reales no tienen corrida publicada: el aviso del modelo sale de la lista de FA de
corridas/2026-11-12_evaluacion-final/analisis-salida.md (las otras 12 no avisaron).
"""

import importlib.util, json, re, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import regla_pedido_critico as rpc  # noqa: E402

EVAL = EXP / 'corridas/2026-11-12_evaluacion-final'
spec = importlib.util.spec_from_file_location('analizar_final', EVAL / 'analizar.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def avisos_modelo(carpeta):
    filas, man = a.leer(carpeta / 'config')
    (nombre, prompt, regla), = a.series('config', a.CONFIG)
    por_caso = a.filas_de(filas, man, nombre, prompt)
    return regla(por_caso, list(por_caso))


def con_roles(texto, protegida):
    salida = []
    for linea in texto:
        hablante, t = linea.split(': ', 1)
        salida.append(('PROTEGIDA' if hablante == protegida else 'OTRA', t))
    return salida


def casos_desarrollo(datos):
    ids = [l for l in (EXP / 'casos/listas/alcance-140.txt').read_text().split() if re.match(r'[A-Z]', l) and '-' in l]
    roles = json.loads((EXP / 'casos/roles-protegida.json').read_text())
    for i in ids:
        ref = json.loads((EXP / 'casos/referencia' / f'{i}.json').read_text())
        texto = (EXP / 'casos/texto' / f'{i}.txt').read_text().splitlines()
        yield i, ref['clase'] == 'vishing', ref.get('t_r_linea'), con_roles(texto, roles[i]['protegida'])


def casos_test(raiz):
    casos = raiz / 'experiments/slm-directo/casos'
    roles = json.loads((casos / 'alcance-reserva.json').read_text())['casos']
    for t in sorted((casos / 'texto').glob('CV2-T-V-*.txt')):
        ref = json.loads((casos / 'referencia' / f'{t.stem}.json').read_text())
        yield t.stem, True, ref.get('t_r_linea'), con_roles(t.read_text().splitlines(), roles[t.stem]['protegida'])
    for j in map(json.loads, open(casos / 'legitimas-entrantes-test.jsonl', encoding='utf-8')):
        yield j['case_id'], False, None, con_roles(j['texto'], j['protegida'])


def casos_reales():
    base = EXP / 'casos/externo/legitimas-reales/set-legitimas'
    roles = json.loads((base / 'roles-protegida.json').read_text())
    for t in sorted((base / 'texto').glob('*.txt')):
        yield t.stem, False, None, con_roles(t.read_text().splitlines(), roles[t.stem]['protegida'])


def avisos_reales():
    salida = (EVAL / 'analisis-salida.md').read_text()
    bloque = salida[salida.index('## Legítimas reales'):]
    fa = bloque[bloque.index('- FA (21):'):].splitlines()[0]
    return {m[0]: int(m[1]) for m in re.findall(r'(EXT-\d+) \([a-z_]+, L(\d+)\)', fa)}


def cifras(casos, modelo):
    tabla, cambios = {}, []
    for nombre in ('modelo', 'regla', 'híbrido'):
        tabla[nombre] = dict(estafas=[0, 0], a_tiempo=[0, 0], fa=[0, 0])
    for cid, estafa, tr, lineas in casos:
        r = rpc.primer_pedido(lineas)
        lineas_aviso = {'modelo': modelo.get(cid), 'regla': r[0] if r else None}
        h = [x for x in lineas_aviso.values() if x]
        lineas_aviso['híbrido'] = min(h) if h else None
        for nombre, l in lineas_aviso.items():
            t = tabla[nombre]
            if estafa:
                t['estafas'][0] += l is not None
                t['estafas'][1] += 1
                if tr:
                    t['a_tiempo'][0] += l is not None and l <= tr
                    t['a_tiempo'][1] += 1
            else:
                t['fa'][0] += l is not None
                t['fa'][1] += 1
        m, hy = lineas_aviso['modelo'], lineas_aviso['híbrido']
        if r and hy != m:
            texto = lineas[r[0] - 1][1]
            if estafa:
                antes = 'no avisaba' if m is None else f'avisaba en la l. {m}'
                cambios.append(f'- estafa `{cid}`: {antes}, la regla avisa en la l. {r[0]} (pedido en la {tr}) '
                               f'por {", ".join(r[1])}: «{texto[:110]}»')
            elif m is None:
                cambios.append(f'- **FA nueva** `{cid}`, l. {r[0]}, por {", ".join(r[1])}: «{texto[:110]}»')
            else:
                cambios.append(f'- FA que ya estaba, adelantada de la l. {m} a la {r[0]}: `{cid}`, por '
                               f'{", ".join(r[1])}: «{texto[:110]}»')
    return tabla, cambios


def main(argv=None):
    dev, test = map(Path, (argv or sys.argv[1:])[:2])
    conjuntos = [
        ('Desarrollo (alcance-140)', casos_desarrollo(dev), avisos_modelo(dev / 'desarrollo')),
        ('Test reservado (100 estafas, 56 legítimas ENT-T)', casos_test(test),
         avisos_modelo(test / 'experiments/slm-directo/corridas/2026-11-12_evaluacion-final/test_reservado')),
        ('Legítimas reales (33)', casos_reales(), avisos_reales()),
    ]
    for titulo, casos, modelo in conjuntos:
        tabla, cambios = cifras(list(casos), modelo)
        print(f'## {titulo}\n\n| detector | estafas avisadas | a tiempo | FA |\n|---|---|---|---|')
        for nombre, t in tabla.items():
            celdas = [f'{k}/{n}' if n else '—' for k, n in (t['estafas'], t['a_tiempo'], t['fa'])]
            print(f'| {nombre} | ' + ' | '.join(celdas) + ' |')
        print('\nLo que cambia la regla:\n')
        print('\n'.join(cambios) or '- nada')
        print()


if __name__ == '__main__':
    main()
