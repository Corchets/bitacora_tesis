"""#143, segunda vuelta, etapa 1: diagnóstico fuera de la regla, escrito el 2026-11-07 después de ver los resultados.

No cambia la regla ni el punto elegido: eso está en analizar.py, escrito antes de correr. Este script explica el
resultado y mide la latencia en las mismas líneas. Solo biblioteca estándar; no corre modelos ni lee la reserva.
Uso, desde esta carpeta:
    python -I diagnostico.py
"""
import contextlib, importlib.util, io, json, math, statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('ronda2', AQUI / 'analizar.py')
r2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r2)
r1, num = r2.r1, r2.r1.num


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, math.ceil(q * len(v)) - 1)]


def ms(r):
    return num(r['slm_ms']) if num(r['slm_ms']) is not None else num(r['ms'])


def por_linea(filas):
    return {(i, int(r['linea'])): r for i, f in filas.items() for r in f}


def aviso_escrito(filas, u, con_alerta):
    """Primera línea con riesgo escrito ≥ u (o `alerta_sugerida`, si se pide)."""
    for r in filas:
        x = num(r['riesgo'])
        if (x is not None and x >= u - 1e-9) or (con_alerta and r['alerta_sugerida'] == 'true'):
            return int(r['linea'])
    return None


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        ids, activacion, _ = r1.lineas_base()
    v2 = r1.grupo(ids, 'corpus_v2')
    base, _ = r1.leer_corrida(r1.uno(r1.BASES['v4 solo (2026-11-05, b)'][0]), 'slm')
    con_tito, _ = r1.leer_corrida(r1.uno(r1.BASES[r1.CORRIDA_TITO][0]), 'tito-slm-sin-indicio')
    con_tito = {i: [r for r in f if r['consulta'] != 'omitida'] for i, f in con_tito.items()}
    lect, _ = r2.una_corrida(AQUI, 'v4-lectura')
    rep, _ = r2.una_corrida(AQUI, 'v4-lectura-rep')
    corridas = {'v4-L': lect, 'v4-L, repetición': rep, 'v4 JSON (línea base, b: hasta el aviso)': base,
                'v4 JSON (d: con Tito, tras activar)': con_tito}
    print('# #143, segunda vuelta, etapa 1: diagnóstico fuera de la regla\n')

    print('## 1. Latencia por línea (Colab T4, ms de la consulta al SLM)\n')
    filas_md = []
    for nombre, filas in corridas.items():
        todas = [r for f in filas.values() for r in f]
        t, sal = [ms(r) for r in todas if ms(r) is not None], [num(r['tokens_salida']) for r in todas if num(r['tokens_salida'])]
        lectura = [num(r['runtime_prompt_eval_ns']) / 1e6 for r in todas if num(r['runtime_prompt_eval_ns']) is not None]
        escritura = [num(r['runtime_eval_ns']) / 1e6 for r in todas if num(r['runtime_eval_ns']) is not None]
        filas_md.append([nombre, len(t), f'{statistics.median(t):.0f} / {pct(t, .95):.0f}', f'{statistics.median(sal):.0f} / {pct(sal, .95):.0f}',
                         f'{statistics.median(lectura):.0f}', f'{statistics.median(escritura):.0f}'])
    r1.tabla(filas_md, ['corrida', 'líneas', 'ms p50 / p95', 'tokens escritos p50 / p95', 'lectura del prompt p50 (ms)', 'escritura p50 (ms)'])
    pl, pb = por_linea(lect), por_linea(base)
    comunes = sorted(set(pl) & set(pb))
    a, b = [ms(pl[k]) for k in comunes], [ms(pb[k]) for k in comunes]
    print(f'En las mismas {len(comunes)} líneas: v4-L {statistics.median(a):.0f} / {pct(a, .95):.0f} ms y v4 JSON '
          f'{statistics.median(b):.0f} / {pct(b, .95):.0f} ms (p50 / p95). La mediana del cociente JSON / v4-L, línea a línea, es '
          f'{statistics.median(y / x for x, y in zip(a, b)):.2f}; v4-L es más rápida en {sum(y > x for x, y in zip(a, b))} de {len(a)}.\n')
    aviso = [ms(r) for f in base.values() for r in f if r['aviso'].lower() == 'true']
    print(f'Etapa 2 (motivo y evidencia): no se midió. Como cota, el JSON entero de v4 en las {len(aviso)} líneas de aviso de la '
          f'línea base tardó {statistics.median(aviso):.0f} / {pct(aviso, .95):.0f} ms (p50 / p95).\n')

    print('## 2. De dónde sale la diferencia con la línea base (corpus_v2)\n')
    print('v4-L corta el JSON después del riesgo, así que no ve `alerta_sugerida`. El riesgo escrito de v4-L sale del mismo '
          'corte (los mismos 12 tokens).\n')
    filas_md = []
    for nombre, filas, con in (('v4 JSON (línea base)', base, True), ('v4 JSON (línea base)', base, False),
                               ('v4-L, riesgo escrito', lect, False), ('v4-L repetición, riesgo escrito', rep, False)):
        for u in (0.3, 0.4, 0.5):
            m = r1.metricas({i: aviso_escrito(filas[i], u, con) for i in ids}, v2)
            filas_md.append([nombre, f'riesgo ≥ {u}' + (' o alerta' if con else ''), *r1.fmt(m)[:1], m['antes'], f"{m['fa']}/{m['n_leg']}"])
    r1.tabla(filas_md, ['corrida', 'regla', 'estafas', 'antes del pedido', 'falsas alarmas'])
    curvas = {n: r1.barrer(f, ids, activacion) for n, f in (('v4-L', lect), ('rep', rep))}
    e = r1.elegir(curvas['v4-L'])
    en_rep = r1.en_punto(curvas['rep'], e)
    av_base = {i: r2.aviso_json(base[i], 'riesgo ≥ 0.4 o alerta') for i in ids}
    print(f"Punto elegido de v4-L: {e['politica']}, umbral {e['u']:g}. Casos de corpus_v2 en que difiere de la línea base "
          '(riesgo ≥ 0,4 o alerta), con el riesgo escrito y el esperado en la línea del aviso de cualquiera de las dos:\n')
    filas_md = []
    for i in v2:
        lineas = {'base': av_base[i], 'v4-L': e['av'][i], 'rep': en_rep['av'][i]}
        if len({x is None for x in lineas.values()}) == 1:
            continue
        n = next(x for x in lineas.values() if x)
        rb = next((r for r in base[i] if int(r['linea']) == n), None)
        rl, rr = lect[i][n - 1], rep[i][n - 1]
        filas_md.append([i, r1.REF[i]['clase'] + (f" (T_R {r1.REF[i]['t_r_linea']})" if r1.REF[i].get('t_r_linea') else ''),
                         *(('L' + str(x)) if x else '–' for x in lineas.values()), f'L{n}',
                         f"{rb['riesgo']}, alerta {rb['alerta_sugerida']}" if rb else '(no consultada)',
                         f"{rl['riesgo']} / {num(rl['riesgo_esperado']):.3f}", f"{rr['riesgo']} / {num(rr['riesgo_esperado']):.3f}"])
    r1.tabla(filas_md, ['caso', 'clase', 'aviso base', 'aviso v4-L', 'aviso rep', 'línea', 'base: riesgo escrito',
                        'v4-L: escrito / esperado', 'rep: escrito / esperado'])

    print('## 3. ¿Qué tan continuo es el riesgo esperado?\n')
    print('Masa del dígito más probable entre los dígitos del primer decimal (normalizada), en las líneas con decimal. '
          'En la primera vuelta, entre el 90 y el 94 % de las líneas tenía P(SÍ) ≤ 0,01 o ≥ 0,99.\n')
    filas_md = []
    for nombre, filas in (('v4-L', lect), ('v4-L, repetición', rep)):
        tops, cerca, n_ok = [], 0, 0
        for r in (r for f in filas.values() for r in f if r['valida'] == 'true'):
            n_ok += 1
            cerca += abs(num(r['riesgo_esperado']) - num(r['riesgo'])) < 0.01
            p = {}
            for t, lp in json.loads(r['top_logprobs'] or '{}').get('decimal', []):
                if len(t.strip()) == 1 and t.strip().isdigit():
                    p[t.strip()] = p.get(t.strip(), 0.0) + math.exp(lp)
            if p:
                tops.append(max(p.values()) / sum(p.values()))
        filas_md.append([nombre, len(tops), f'{100 * sum(t >= .99 for t in tops) / len(tops):.1f} %',
                         f'{100 * sum(.9 <= t < .99 for t in tops) / len(tops):.1f} %', f'{100 * sum(t < .9 for t in tops) / len(tops):.1f} %',
                         f'{statistics.median(tops):.2f}', f'{100 * cerca / n_ok:.1f} %'])
    r1.tabla(filas_md, ['corrida', 'líneas', 'dígito con P ≥ 0,99', 'entre 0,9 y 0,99', '< 0,9', 'mediana',
                        '|esperado − escrito| < 0,01'])
    print('Curva de v4-L, SLM solo, umbral simple, cerca del punto elegido (corpus_v2):\n')
    filas_md = []
    for u in (0.25, 0.3, 0.35, 0.38, 0.4, 0.45, 0.5):
        c = next(c for c in curvas['v4-L'] if (c['compuerta'], c['politica'], c['u']) == ('SLM solo', 'umbral', u))
        filas_md.append([f'{u:g}', f"{c['det']}/46", c['antes'], f"{c['fa']}/51"])
    r1.tabla(filas_md, ['umbral', 'estafas', 'antes del pedido', 'falsas alarmas'])

    print('## 4. Riesgo escrito: coincidencia entre corridas\n')
    print('Mismas líneas, las dos con riesgo. b y d son dos corridas JSON de v4 en sesiones distintas de Colab.\n')
    filas_md = []
    for nombre, x, y in (('v4-L y su repetición', lect, rep), ('v4-L y v4 JSON b', lect, base),
                         ('v4 JSON b y v4 JSON d', base, con_tito)):
        px, py = por_linea(x), por_linea(y)
        pares = [(num(px[k]['riesgo']), num(py[k]['riesgo'])) for k in sorted(set(px) & set(py))
                 if num(px[k]['riesgo']) is not None and num(py[k]['riesgo']) is not None]
        dif = [round(p - q, 2) for p, q in pares]
        iguales = sum(abs(d) < 1e-9 for d in dif)
        filas_md.append([nombre, len(pares), f'{iguales} ({100 * iguales / len(pares):.1f} %)',
                         sum(abs(abs(d) - 0.1) < 1e-9 for d in dif), sum(abs(d) > 0.1 + 1e-9 for d in dif), f'{statistics.fmean(dif):+.3f}'])
    r1.tabla(filas_md, ['par', 'líneas', 'iguales', 'difieren en 0,1', 'en más de 0,1', 'media de la diferencia'])

    print('## 5. Líneas inválidas y legítimas con falsa alarma por datos\n')
    for nombre, filas in (('v4-L', lect), ('v4-L, repetición', rep)):
        malas = [(i, r) for i, f in filas.items() for r in f if r['valida'] != 'true']
        print(f'- {nombre}: {len(malas)} inválidas' + (': ' + '; '.join(
            f"{i} L{r['linea']} ({r['error']}, escribió {r['crudo'].split(':', 1)[-1].strip()!r})" for i, r in malas) if malas else '') + '.')
    print('\nLas 6 legítimas en que v4 avisaba por un dato pedido en una llamada que inició la persona, sin la máscara del '
          'alcance (vista principal, en el punto de cada configuración):\n')
    r1.tabla([[i, f"L{av_base[i]}" if av_base[i] else '–', f"L{e['av'][i]}" if e['av'][i] else '–'] for i in r2.DATOS_LEGITIMAS],
             ['caso', 'v4 JSON (riesgo ≥ 0,4 o alerta)', f"v4-L ({e['politica']}, {e['u']:g})"])


if __name__ == '__main__':
    main()
