"""#52, exploración con los conjuntos reales: cuentas aparte, para leer el resultado. No cambian la regla ni la aplican.

Uso, desde esta carpeta:
    python -I aparte.py --datos CARPETA [--final CARPETA_DE_LA_EVALUACION_FINAL]

CARPETA es la misma que recibe analizar.py. Con --final (el ZIP de la evaluación final descomprimido, fuera del
repositorio) compara las dos pasadas de la misma configuración (`c-consejos-corte-riesgo`): la de la evaluación final,
del 2026-11-19, y la `base` de esta exploración, del 2026-11-20. Solo escribe cifras e identificadores.
"""

import argparse, collections, hashlib, importlib.util, statistics, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('analizar_exploracion', AQUI / 'analizar.py')
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)
fin = ex.fin

CORTES = [3, 5, 8, 12, 20]  # primeras consultas válidas de OTRA de cada llamada
REALES = ('externo', 'legitimas_reales')


def tabla(encabezado, filas):
    return (['| ' + ' | '.join(encabezado) + ' |', '|' + '---|' * len(encabezado)]
            + ['| ' + ' | '.join(str(x) for x in f) + ' |' for f in filas])


def grupos(tanda, conj):
    """{grupo: [casos]} de una tanda: estafas y legítimas."""
    ref = conj.referencia()
    ids = ex.casos_de(tanda, conj)
    return {'estafas': [i for i in ids if ref[i]['clase'] == 'vishing'],
            'legítimas': [i for i in ids if ref[i]['clase'] != 'vishing']}


def avisa_en(l, k=None, u=ex.UMBRAL):
    """¿Hay un riesgo ≥ u en las primeras k consultas válidas (todas si k es None)?"""
    return any(r >= u for _, r in (l if k is None else l[:k]))


def auc(positivos, negativos):
    """Probabilidad de que una estafa tenga más puntaje que una legítima (los empates valen medio)."""
    if not positivos or not negativos:
        return None
    gana = sum((p > n) + 0.5 * (p == n) for p in positivos for n in negativos)
    return gana / (len(positivos) * len(negativos))


def pct(k, n):
    return f'{k}/{n} ({100 * k / n:.0f} %)' if n else '—'


def repeticion(conjs, leidas, final):
    """Las dos pasadas de la base: cifras, consultas y llamadas que cambian."""
    out = ['## La misma configuración, dos sesiones de Colab', '',
           'Evaluación final (2026-11-19) y `base` de la exploración (2026-11-20): mismo prompt, modelo, semilla, Ollama y '
           'conjuntos. Cambia cómo se corrió: la evaluación final pasó cada conjunto entero y cortó cada llamada en su primer '
           'aviso; la exploración pasó solo la vista principal y todas las líneas. La cifra que vale es la de la evaluación '
           'final; la diferencia mide cuánto se mueve el resultado al repetir.', '']
    cifras, consultas, llamadas = [], [], []
    for tanda, conj in conjs.items():
        if 'base' not in leidas[tanda]:
            continue
        nombre_conj = ex.TANDAS[tanda][0]
        igual = (hashlib.sha256((final / 'conjuntos' / nombre_conj / 'conjunto.json').read_bytes()).hexdigest()
                 == hashlib.sha256((conj.carpeta / 'conjunto.json').read_bytes()).hexdigest()) if hasattr(conj, 'carpeta') else None
        corrida = fin.leer(final / nombre_conj / 'config')
        if corrida is None:
            continue
        por_config, man = corrida
        filas = fin.filas_de(por_config, man, 'config', ex.BASE)
        ids = ex.casos_de(tanda, conj)
        antes = {i: ex.riesgos(filas.get(i, [])) for i in ids}
        ahora = leidas[tanda]['base']
        ref = conj.referencia()
        av_a = {i: ex.primer_aviso(antes[i]) for i in ids}
        av_b = {i: ex.primer_aviso(ahora[i]) for i in ids}
        ea, eb = fin.exitos(av_a, ids, ref), fin.exitos(av_b, ids, ref)
        for c in fin.COMPARADAS:
            if ea[c]:
                ka, kb = sum(ea[c].values()), sum(eb[c].values())
                cifras.append([ex.NOMBRES[tanda], c, f'{ka}/{len(ea[c])}', f'{kb}/{len(eb[c])}', f'{kb - ka:+d}',
                               sum(ea[c][i] != eb[c][i] for i in ea[c])])
        comunes = iguales = cruzan = suben = bajan = chicas = 0
        for i in ids:
            a, b = dict(antes[i]), dict(ahora[i])
            for n in a.keys() & b.keys():
                comunes += 1
                iguales += a[n] == b[n]
                cruzan += (a[n] >= ex.UMBRAL) != (b[n] >= ex.UMBRAL)
                suben += b[n] > a[n]
                bajan += b[n] < a[n]
                chicas += 0 < abs(b[n] - a[n]) < 0.15
        consultas.append([ex.NOMBRES[tanda], sum(len(v) for v in antes.values()), sum(len(v) for v in ahora.values()),
                          comunes, pct(iguales, comunes), pct(cruzan, comunes), suben, bajan, chicas,
                          {True: 'sí', False: 'NO', None: '—'}[igual]])
        cambia = [i for i in ids if (av_a[i] is None) != (av_b[i] is None)]
        otra_linea = [i for i in ids if av_a[i] is not None and av_b[i] is not None and av_a[i] != av_b[i]]
        llamadas.append([ex.NOMBRES[tanda], len(ids), len(cambia), len(otra_linea)])
    out += tabla(['conjunto', 'cifra', 'evaluación final', 'exploración', 'diferencia', 'llamadas que cambian'], cifras)
    out += ['', 'Consulta por consulta (las líneas de OTRA válidas en las dos pasadas):', '']
    out += tabla(['conjunto', 'consultas válidas, final', 'consultas válidas, exploración', 'en las dos', 'mismo riesgo',
                  'cruzan el 0,3', 'sube en la exploración', 'baja en la exploración', 'cambios de 0,1 o menos',
                  'mismo conjunto'], consultas)
    out += ['', 'Llamada por llamada (primer aviso):', '']
    out += tabla(['conjunto', 'llamadas', 'avisa en una pasada y en la otra no', 'avisa en las dos, en otra línea'], llamadas)
    return out


def largo(conjs, leidas):
    filas = []
    for tanda, conj in conjs.items():
        if 'base' not in leidas[tanda]:
            continue
        for g, ids in grupos(tanda, conj).items():
            if ids:
                n = sorted(len(leidas[tanda]['base'][i]) for i in ids)
                filas.append([ex.NOMBRES[tanda], g, len(ids), n[0], int(statistics.median(n)), n[-1]])
    return (['## Cuántas consultas válidas de OTRA tiene cada llamada (base)', '',
             'Con el primer aviso, una llamada con más consultas tiene más oportunidades de avisar.', '']
            + tabla(['conjunto', 'grupo', 'llamadas', 'mínimo', 'mediana', 'máximo'], filas))


def por_cortes(conjs, leidas, u=ex.UMBRAL):
    filas = []
    for tanda in ('externo', 'legitimas_reales', 'desarrollo'):
        if tanda not in conjs:
            continue
        for g, ids in grupos(tanda, conjs[tanda]).items():
            if not ids:
                continue
            for carpeta in ex.PROMPTS:
                if carpeta in leidas[tanda]:
                    l = leidas[tanda][carpeta]
                    filas.append([ex.NOMBRES[tanda], g, carpeta]
                                 + [f'{sum(avisa_en(l[i], k, u) for i in ids)}/{len(ids)}' for k in [*CORTES, None]])
    corte = str(u).replace('.', ',')
    return ([f'## Llamadas que ya avisaron en las primeras consultas (riesgo ≥ {corte})', '',
             'Iguala el largo: compara estafas y legítimas con la misma cantidad de consultas.', '']
            + tabla(['conjunto', 'grupo', 'prompt', *(f'en {k}' for k in CORTES), 'en todas'], filas))


def por_cortes_fuerte(conjs, leidas):
    return por_cortes(conjs, leidas, ex.FUERTE)


def separacion(conjs, leidas):
    """Por consulta y por llamada, sin depender del corte: reales (coreanas contra las 33) y desarrollo."""
    filas = []
    pares = [('reales', 'externo', 'estafas', 'legitimas_reales', 'legítimas'),
             ('desarrollo', 'desarrollo', 'estafas', 'desarrollo', 'legítimas')]
    for nombre, t_e, g_e, t_l, g_l in pares:
        if t_e not in conjs or t_l not in conjs:
            continue
        est, leg = grupos(t_e, conjs[t_e])[g_e], grupos(t_l, conjs[t_l])[g_l]
        for carpeta in ex.PROMPTS:
            if carpeta not in leidas[t_e] or carpeta not in leidas[t_l]:
                continue
            le, ll = leidas[t_e][carpeta], leidas[t_l][carpeta]

            def tasa(l, ids, k=None):
                rs = [r for i in ids for _, r in (l[i] if k is None else l[i][:k])]
                return sum(r >= ex.UMBRAL for r in rs), len(rs)

            (ke, ne), (kl, nl) = tasa(le, est), tasa(ll, leg)
            (ke12, ne12), (kl12, nl12) = tasa(le, est, 12), tasa(ll, leg, 12)

            def maximo(l, ids, k=None):
                return [max((r for _, r in (l[i] if k is None else l[i][:k])), default=0.0) for i in ids]

            def media(l, ids, k=None):
                return [statistics.fmean([r for _, r in (l[i] if k is None else l[i][:k])] or [0.0]) for i in ids]

            filas.append([nombre, carpeta, f'{100 * ke / ne:.0f} %', f'{100 * kl / nl:.0f} %',
                          f'{100 * ke12 / ne12:.0f} %', f'{100 * kl12 / nl12:.0f} %',
                          f'{auc(maximo(le, est), maximo(ll, leg)):.2f}', f'{auc(maximo(le, est, 12), maximo(ll, leg, 12)):.2f}',
                          f'{auc(media(le, est, 12), media(ll, leg, 12)):.2f}'])
    return (['## Cuánto separa cada prompt', '',
             'Consultas con riesgo ≥ 0,3 en estafas y en legítimas, y probabilidad de que una estafa puntúe más que una '
             'legítima (0,50 es no separar; 1,00, separar siempre). «12» es con las primeras 12 consultas de cada llamada.', '']
            + tabla(['conjuntos', 'prompt', 'consultas ≥ 0,3, estafas', 'consultas ≥ 0,3, legítimas',
                     'ídem, primeras 12, estafas', 'ídem, primeras 12, legítimas', 'separa (máximo)',
                     'separa (máximo, 12)', 'separa (promedio, 12)'], filas))


def falsas_reales(conjs, leidas):
    out = ['## Las 33 legítimas reales: ¿avisan siempre las mismas?', '']
    if 'legitimas_reales' not in conjs:
        return out
    ids = grupos('legitimas_reales', conjs['legitimas_reales'])['legítimas']
    carpetas = [c for c in ex.PROMPTS if c in leidas['legitimas_reales']]
    avisa = {c: {i for i in ids if avisa_en(leidas['legitimas_reales'][c][i])} for c in carpetas}
    cuantos = collections.Counter(sum(i in avisa[c] for c in carpetas) for i in ids)
    out += tabla(['prompts que avisan (de %d)' % len(carpetas), 'llamadas'], [[k, cuantos[k]] for k in range(len(carpetas) + 1)])
    out += ['', 'Contra la base:', '']
    out += tabla(['prompt', 'avisa', 'también avisa la base', 'solo este prompt', 'la base avisa y este no'],
                 [[c, len(avisa[c]), len(avisa[c] & avisa['base']), len(avisa[c] - avisa['base']), len(avisa['base'] - avisa[c])]
                  for c in carpetas if c != 'base'])
    siempre = sorted(i for i in ids if all(i in avisa[c] for c in carpetas))
    nunca = sorted(i for i in ids if not any(i in avisa[c] for c in carpetas))
    out += ['', f'Avisan con los {len(carpetas)} prompts ({len(siempre)}): {", ".join(siempre) or "—"}.',
            '', f'No avisan con ninguno ({len(nunca)}): {", ".join(nunca) or "—"}.']
    return out


def perdidas(conjs, leidas):
    out = ['## Coreanas que cada prompt no avisa o no avisa a tiempo', '']
    if 'externo' not in conjs:
        return out
    conj = conjs['externo']
    ref, ids = conj.referencia(), ex.casos_de('externo', conj)
    filas = []
    for c in ex.PROMPTS:
        if c not in leidas['externo']:
            continue
        av = {i: ex.primer_aviso(leidas['externo'][c][i]) for i in ids}
        e = fin.exitos(av, ids, ref)
        filas.append([c, ', '.join(sorted(i for i, v in e['estafas'].items() if not v)) or '—',
                      ', '.join(sorted(i for i, v in e['a tiempo'].items() if not v and e['estafas'][i])) or '—'])
    return out + tabla(['prompt', 'sin aviso', 'con aviso, pero tarde'], filas)


def sin_pedido(conjs, leidas):
    """Estafas de desarrollo con y sin línea de pedido: los prompts «por pedido» podrían perder las segundas."""
    out = ['## Desarrollo: estafas con y sin línea de pedido', '']
    if 'desarrollo' not in conjs:
        return out
    conj = conjs['desarrollo']
    ref = conj.referencia()
    est = grupos('desarrollo', conj)['estafas']
    con = [i for i in est if ref[i]['t_r_linea']]
    sin = [i for i in est if not ref[i]['t_r_linea']]
    filas = []
    for c in ex.PROMPTS:
        if c in leidas['desarrollo']:
            l = leidas['desarrollo'][c]
            filas.append([c, f'{sum(avisa_en(l[i]) for i in con)}/{len(con)}', f'{sum(avisa_en(l[i]) for i in sin)}/{len(sin)}'])
    return out + tabla(['prompt', 'avisadas, con pedido', 'avisadas, sin pedido'], filas)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--datos', type=Path, required=True)
    ap.add_argument('--final', type=Path, help='la evaluación final descomprimida, para comparar las dos pasadas de la base')
    a = ap.parse_args(argv)
    conjs, leidas, _ = ex.cargar(a.datos)
    out = ['# #52, exploración con los conjuntos reales — cuentas aparte', '',
           'Para leer el resultado; no cambian la regla. Aviso = riesgo ≥ 0,3 salvo que se diga otra cosa.', '']
    if a.final:
        out += repeticion(conjs, leidas, a.final) + ['']
    for parte in (largo, por_cortes, por_cortes_fuerte, separacion, falsas_reales, perdidas, sin_pedido):
        out += parte(conjs, leidas) + ['']
    sys.stdout.write('\n'.join(out))


if __name__ == '__main__':
    main()
