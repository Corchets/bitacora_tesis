"""#143: el JSON de v4 cortado después de `alerta_sugerida` (v4-corte) contra el JSON completo de v4.

Escrito el 2026-11-07, antes de correr; el criterio está en README.md de esta carpeta. No corre modelos ni lee la
reserva; solo biblioteca estándar. Uso, desde esta carpeta, con los ZIP de Colab descomprimidos acá:
    python -I analizar.py                       # lee v4-corte/ y v4/
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Informa:
1. Control: mismo commit, digest, casos y parámetros en las dos corridas, modo diagnóstico, y el mismo prompt.
2. Coincidencia línea a línea en el riesgo escrito y la alerta escrita, y las líneas inválidas.
3. Latencia (ms de pared en T4, p50 / p95 por rango más cercano): la primera consulta contra el JSON completo en las
   mismas líneas, la segunda consulta, y el total en la línea de aviso.
4. Solo para mirar: avisos con «riesgo ≥ 0,4 o alerta» en las dos corridas (la decisión ya está tomada).
"""
import argparse, collections, csv, json, math, statistics, sys
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import casos  # noqa: E402

UMBRAL = 0.4  # «riesgo ≥ 0,4 o alerta», el mismo de detectores.UMBRAL_CORTE
COINCIDENCIA_MINIMA = 0.93  # riesgo escrito igual; dos corridas iguales en una sesión dan ~96 %
INVALIDAS_MAXIMAS = 0.01  # del cortado: más que esto, el num_predict no alcanza


def num(x):
    return float(x) if x not in ('', None) else None


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, math.ceil(q * len(v)) - 1)]


def p50_p95(v):
    return f'{statistics.median(v):.0f} / {pct(v, .95):.0f}' if v else '—'


def tabla(filas, encabezado):
    print('| ' + ' | '.join(encabezado) + ' |')
    print('|' + '---|' * len(encabezado))
    for f in filas:
        print('| ' + ' | '.join(str(x) for x in f) + ' |')
    print()


def cargar(datos, carpeta):
    (run,) = [p for p in (datos / carpeta).iterdir() if (p / 'manifiesto.json').exists()]
    man = json.loads((run / 'manifiesto.json').read_text(encoding='utf-8'))
    with (run / 'actualizaciones.csv').open(encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    return man, {(r['case_id'], int(r['linea'])): r for r in filas}


def controlar(mc, mv):
    problemas = []
    for clave in ('codigo', 'casos', 'particion', 'modo_termino', 'roles_protegida'):
        if mc.get(clave) != mv.get(clave):
            problemas.append(f'{clave} distinto')
    if mc['ollama']['digests'] != mv['ollama']['digests'] or mc['ollama']['version'] != mv['ollama']['version']:
        problemas.append('Ollama o digest distinto')
    for clave in ('num_ctx', 'seed', 'temperatura'):
        if mc['parametros_slm'][clave] != mv['parametros_slm'][clave]:
            problemas.append(f'{clave} distinto')
    if mc['prompts']['v4-corte']['huella'] != mv['prompts']['v4']['huella']:
        problemas.append('el prompt de v4-corte no es el de v4')
    if mc['modo_termino'] != 'diagnostico-completo':
        problemas.append('no corrió en todas las líneas (--seguir-tras-aviso)')
    if mc['particion'] != 'desarrollo':
        problemas.append('no es la partición de desarrollo')
    return problemas


def avisos(filas, alerta):
    """case_id → primera línea con «riesgo ≥ 0,4 o alerta» (o None)."""
    salida = collections.defaultdict(lambda: None)
    for (case_id, n), r in sorted(filas.items()):
        salida.setdefault(case_id, None)
        riesgo = num(r['riesgo'])
        dispara = r['valida'] == 'true' and (r[alerta] == 'true' or (riesgo is not None and riesgo >= UMBRAL - 1e-9))
        if dispara and salida[case_id] is None:
            salida[case_id] = n
    return dict(salida)


def metricas(av, ids):
    ref = {i: casos.cargar_referencia(i) for i in ids}
    est = [i for i in ids if ref[i]['clase'] == 'vishing']
    leg = [i for i in ids if ref[i]['clase'] != 'vishing']
    conp = [i for i in est if ref[i].get('t_r_linea')]
    return (f"{sum(av.get(i) is not None for i in est)}/{len(est)}",
            f"{sum(av.get(i) is not None and av[i] < ref[i]['t_r_linea'] for i in conp)}/{len(conp)}",
            f"{sum(av.get(i) is not None for i in leg)}/{len(leg)}")


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--datos', type=Path, default=AQUI)
    args = p.parse_args(argv)
    mc, corte = cargar(args.datos, 'v4-corte')
    mv, completo = cargar(args.datos, 'v4')

    print('# v4-corte contra v4 JSON completo, misma sesión de Colab\n')
    print('## 1. Control\n')
    problemas = controlar(mc, mv)
    print(f"Commit `{mc['codigo'].get('commit', '?')}`, Ollama {mc['ollama']['version']}, "
          f"digest `{next(iter(mc['ollama']['digests'].values()))}`, {len(mc['casos'])} casos. "
          f"num_predict de la primera consulta: {mc['parametros_slm']['json_cortado']['num_predict']}.\n")
    print('Sin problemas.\n' if not problemas else 'PROBLEMAS: ' + '; '.join(problemas) + '\n')

    print('## 2. Coincidencia línea a línea\n')
    comunes = sorted(set(corte) & set(completo))
    ambas = [k for k in comunes if corte[k]['valida'] == 'true' and completo[k]['valida'] == 'true']
    riesgo_igual = sum(num(corte[k]['riesgo']) == num(completo[k]['riesgo']) for k in ambas)
    alerta_igual = sum(corte[k]['alerta_escrita'] == completo[k]['alerta_sugerida'] for k in ambas)
    invalidas_c = collections.Counter(r['error'] for r in corte.values() if r['valida'] != 'true')
    invalidas_v = collections.Counter(r['error'] for r in completo.values() if r['valida'] != 'true')
    tabla([[len(corte), len(completo), len(comunes), len(ambas),
            f'{riesgo_igual} ({riesgo_igual / len(ambas):.1%})', f'{alerta_igual} ({alerta_igual / len(ambas):.1%})',
            f'{sum(invalidas_c.values())} {dict(invalidas_c)}', f'{sum(invalidas_v.values())} {dict(invalidas_v)}']],
          ['líneas cortado', 'líneas completo', 'en las dos', 'válidas en las dos', 'riesgo igual', 'alerta igual',
           'inválidas cortado', 'inválidas completo'])
    pares = collections.Counter((corte[k]['alerta_escrita'], completo[k]['alerta_sugerida']) for k in ambas)
    print(f"Alerta escrita (cortado, completo): {dict(sorted(pares.items()))}.\n")
    distintas = [k for k in ambas if corte[k]['alerta_escrita'] != completo[k]['alerta_sugerida']]
    for k in distintas[:30]:
        print(f"- {k[0]} L{k[1]}: cortado {corte[k]['riesgo']} / {corte[k]['alerta_escrita']}, "
              f"completo {completo[k]['riesgo']} / {completo[k]['alerta_sugerida']}")
    if distintas:
        print()
    coincide = ambas and riesgo_igual / len(ambas) >= COINCIDENCIA_MINIMA
    pocas_invalidas = sum(invalidas_c.values()) <= INVALIDAS_MAXIMAS * len(corte)
    print(f"**Criterio:** riesgo igual en ≥ {COINCIDENCIA_MINIMA:.0%} de las líneas válidas en las dos: "
          f"{'SÍ' if coincide else 'NO'}; inválidas del cortado ≤ {INVALIDAS_MAXIMAS:.0%}: "
          f"{'SÍ' if pocas_invalidas else 'NO'}. "
          + ('El corte no cambia la primera consulta.\n' if coincide and pocas_invalidas and not problemas else
             'Revisar con Mateo antes de usar la latencia.\n'))

    print('## 3. Latencia (ms de pared en T4, p50 / p95)\n')
    rt = lambda filas, c: [num(r[c]) / 1e6 for r in filas if num(r[c]) is not None]  # noqa: E731
    fc, fv = [corte[k] for k in ambas], [completo[k] for k in ambas]
    e1, comp = [num(r['ms_etapa1']) for r in fc], [num(r['ms']) for r in fv]
    tabla([['primera consulta (cortado)', len(fc), p50_p95(e1), p50_p95([num(r['tokens_salida']) for r in fc]),
            p50_p95(rt(fc, 'runtime_prompt_eval_ns')), p50_p95(rt(fc, 'runtime_eval_ns'))],
           ['JSON completo', len(fv), p50_p95(comp), p50_p95([num(r['tokens_salida']) for r in fv]),
            p50_p95(rt(fv, 'runtime_prompt_eval_ns')), p50_p95(rt(fv, 'runtime_eval_ns'))]],
          ['consulta, mismas líneas', 'líneas', 'ms', 'tokens escritos', 'lectura del prompt (ms)', 'escritura (ms)'])
    if e1:
        print(f"El cortado es más rápido en {sum(a < b for a, b in zip(e1, comp))} de {len(e1)} líneas; mediana del "
              f"cociente completo / cortado, línea a línea: {statistics.median(b / a for a, b in zip(e1, comp) if a):.2f}.\n")
    aviso = [k for k in comunes if corte[k]['ms_etapa2']]
    e2 = [num(corte[k]['ms_etapa2']) for k in aviso]
    fallos2 = collections.Counter(corte[k]['error'] for k in aviso if corte[k]['error'].startswith('etapa2_'))
    print(f"**Segunda consulta** (motivo y evidencia), en {len(aviso)} líneas de aviso: {p50_p95(e2)} ms; tokens escritos "
          f"{p50_p95([num(corte[k]['tokens_salida_etapa2']) for k in aviso])}, tokens de prompt (prompt_eval_count) "
          f"{p50_p95([num(corte[k]['tokens_prompt_etapa2']) for k in aviso])}; fallos: {sum(fallos2.values())} {dict(fallos2)}; "
          f"evidencia en el texto: {sum(corte[k]['evidencia_en_texto'] == 'true' for k in aviso)}/{len(aviso)}.\n")
    alerta_completo = [k for k in comunes if completo[k]['alerta_sugerida'] == 'true']
    tabla([['cortado: primera + segunda', len(aviso), p50_p95([num(corte[k]['ms']) for k in aviso])],
           ['JSON completo, mismas líneas', len(aviso), p50_p95([num(completo[k]['ms']) for k in aviso if completo[k]['ms']])],
           ['JSON completo, líneas con alerta escrita', len(alerta_completo),
            p50_p95([num(completo[k]['ms']) for k in alerta_completo])]],
          ['línea de aviso', 'líneas', 'ms'])

    print('## 4. Solo para mirar: avisos con «riesgo ≥ 0,4 o alerta»\n')
    ac, av = avisos(corte, 'alerta_escrita'), avisos(completo, 'alerta_sugerida')
    ids = sorted(set(ac) | set(av))
    print(f"Misma línea de aviso en {sum(ac.get(i) == av.get(i) for i in ids)} de {len(ids)} casos.\n")
    cv2 = [i for i in ids if casos.cargar_referencia(i)['grupo'] == 'corpus_v2']
    tabla([['v4-corte', *metricas(ac, cv2)], ['v4 JSON completo', *metricas(av, cv2)],
           ['línea base v4 JSON (2026-11-05, b, otra sesión)', '29/46', '11/36', '7/51']],
          ['corpus_v2', 'estafas', 'antes del pedido', 'falsas alarmas'])


if __name__ == '__main__':
    main()
