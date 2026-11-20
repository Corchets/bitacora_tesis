"""#52, exploración con los conjuntos reales, posterior a la evaluación final: no la reemplaza.

Busca una configuración que siga avisando las estafas reales coreanas y avise menos en las legítimas reales de call
center. Prueba dos cosas, solas y juntas: el prompt (los de VARIANTES) y la política de aviso («confirmación»). La regla
está en README.md, escrita antes de correr, y es la de este archivo.

No corre modelos; solo biblioteca estándar y el código del laboratorio. Uso, desde esta carpeta:
    python -I analizar.py --datos CARPETA    # el ZIP de Colab descomprimido en CARPETA, fuera del repositorio

CARPETA trae conjuntos/, humo/ y una corrida por tanda y prompt: <tanda>/<base|variante>/. Las tandas de la fase 1
(coreanas, legítimas reales y desarrollo) corren con todos los prompts; las de la fase 2 (zona gris y test), solo con la
base y con los prompts que la regla dejó pasar. Todas corren solo en las líneas de OTRA y en todas ellas
(--seguir-tras-aviso), para aplicar las dos políticas sobre los mismos riesgos:
- «primer aviso», la de hoy: la primera línea de OTRA con riesgo ≥ 0,3;
- «confirmación»: la primera línea de OTRA con riesgo ≥ 0,5, o la segunda con riesgo ≥ 0,3 (no hace falta que sean
  seguidas).
Las líneas inválidas no avisan. Las cifras son las de la evaluación final (analizar.exitos).
"""

import argparse, collections, importlib.util, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


fin = _cargar('analizar_final', AQUI.parent / '2026-11-12_evaluacion-final' / 'analizar.py')  # deja el laboratorio en sys.path
conjuntos, e3, tabla, kn = fin.conjuntos, fin.e3, fin.tabla, fin.kn
from detectores import PROMPTS_CORTE_RIESGO, cargar_prompt, huella  # noqa: E402

BASE = 'c-consejos-corte-riesgo'  # la configuración de la evaluación final (ADR 0008)
# Los prompts que se prueban, por su nombre corto y en el orden en que corren: si Colab se corta, quedan los primeros.
VARIANTES = ['p-lista', 'p-escalera', 'p-niveles', 'c-rumbo', 'p-sino', 'p-minimo']
PROMPTS = {'base': BASE, **{v: f'{v}-corte-riesgo' for v in VARIANTES}}  # carpeta → prompt
# Tanda → (conjunto, qué casos corren). De las legítimas reales salen dos tandas: las 33 y la zona gris.
TANDAS = {'externo': ('externo', 'todos'), 'legitimas_reales': ('legitimas_reales', 'principal'),
          'desarrollo': ('desarrollo', 'principal'),
          'zona_gris': ('legitimas_reales', 'aparte'), 'test_reservado': ('test_reservado', 'principal')}
FASE_1 = ['externo', 'legitimas_reales', 'desarrollo']  # con todos los prompts: lo que usa la regla
FASE_2 = ['zona_gris', 'test_reservado']                # solo con la base y los prompts de los que sirven
PASAN_A_FASE_2 = 2  # cuántos candidatos que sirven llevan su prompt a la fase 2, en el orden de la regla
NOMBRES = {'externo': 'Estafas reales coreanas (#144)', 'legitimas_reales': 'Legítimas reales (CallCenterEN, las 33)',
           'desarrollo': 'Desarrollo (alcance-140)', 'zona_gris': 'Zona gris de Medicare (avisos, no son FA)',
           'test_reservado': 'Test reservado (vista principal)'}
UMBRAL, FUERTE = 0.3, 0.5
REFERENCIA = ('base', 'primer aviso')
# En este orden se desempata: primero lo que cambia menos.
CANDIDATOS = ([('base', 'confirmación')] + [(v, 'primer aviso') for v in VARIANTES]
              + [(v, 'confirmación') for v in VARIANTES])
PIERDE = 1       # en las coreanas puede perder a lo sumo una, en avisadas y en a tiempo
BAJA_FA = 7      # y tiene que bajar 7 o más las FA de las 33 legítimas reales (un tercio de las 21 de la evaluación final)
COSTO_ALTO = {'test a tiempo': 8, 'test estafas': 10}  # lo que se marca como costo alto en las estafas generadas
# La vara: `v4-corte` en la evaluación final (modo operativo, todas las líneas, de los dos lados). No vuelve a correr.
V4_EN_LA_FINAL = ('coreanas 33/33, a tiempo 23/27; FA reales 10/33; zona gris 20/42; desarrollo 28/46, a tiempo 25/36 y '
                  'FA 42/94; test 64/100, a tiempo 50/80 y FA 15/56')
ETIQUETAS = AQUI.parent / '2026-11-10_revision-producto' / 'etiquetas-producto.json'


# --- Las dos políticas, sobre los riesgos de un caso ---
def riesgos(filas):
    """[(línea, riesgo)] de las consultas válidas de OTRA de un caso, en orden."""
    return [(int(r['linea']), float(r['riesgo'])) for r in filas
            if r['hablante'] == 'OTRA' and r['valida'] == 'true' and r['riesgo'] != '']


def primer_aviso(l):
    return next((n for n, r in l if r >= UMBRAL), None)


def confirmacion(l):
    vistos = 0
    for n, r in l:
        if r >= FUERTE:
            return n
        if r >= UMBRAL:
            vistos += 1
            if vistos == 2:
                return n
    return None


POLITICAS = {'primer aviso': primer_aviso, 'confirmación': confirmacion}


def casos_de(tanda, conj):
    """Los casos de un conjunto que corren en una tanda (lo usa también el script de Colab)."""
    cuales = TANDAS[tanda][1]
    if cuales == 'todos':
        return list(conj.ids)
    ref = conj.referencia()
    return [i for i in conj.ids if (ref[i]['vista'] == conjuntos.PRINCIPAL) == (cuales == 'principal')]


# --- Control de una corrida ---
def controlar(conj, prompt, filas, man, ids):
    problemas = []
    if sorted(man.get('casos', {})) != sorted(ids):
        problemas.append('no son los casos esperados')
    elif any(man['casos'][i] != huella(conj.crudo(i)) for i in ids):
        problemas.append('el texto de algún caso no es el del conjunto')
    datos = man.get('conjunto') or {}
    if datos.get('nombre') != conj.nombre or datos.get('conjunto_sha256') != conjuntos.sha256((conj.carpeta / 'conjunto.json').read_bytes()):
        problemas.append(f'no corrió sobre el conjunto {conj.nombre} armado')
    if man.get('modo_termino') != 'diagnostico-completo' or man.get('interrumpida') or not man.get('fin'):
        problemas.append('no corrió entera en todas las líneas')
    if man.get('codigo', {}).get('cambios_sin_commit_en_la_carpeta'):
        problemas.append('corrió con cambios sin commitear')
    if [(c['detector'], c['prompt'], c['hablantes']) for c in man.get('configs', [])] != [('slm', prompt, 'rol')] or man.get('solo_otra') is not True:
        problemas.append('no es el prompt esperado, con roles y solo OTRA')
    if man['ollama']['version'] != e3.OLLAMA or (man['ollama']['digests'].get(e3.MODELO) or '').removeprefix('sha256:') != e3.DIGEST:
        problemas.append('Ollama o digest distinto')
    ps = man['parametros_slm']
    if (ps['num_ctx'], ps['seed'], ps['temperatura']) != (4096, 42, 0.0):
        problemas.append('num_ctx, seed o temperatura distintos')
    if list(man['prompts']) != [prompt] or man['prompts'][prompt].get('texto') != cargar_prompt(prompt):
        problemas.append(f'el prompt no es el de {prompt}')
    if sorted(filas) != sorted(ids):
        problemas.append('faltan casos en el CSV')
    elif any([int(r['linea']) for r in filas[i]] != list(range(1, len(conj.cargar_texto(i)) + 1)) for i in ids):
        problemas.append('algún caso no tiene todas sus líneas')
    return problemas


# --- La regla ---
def resumen(ex):
    """Las cifras de un candidato que usa la regla, de {conjunto: exitos}. Lo que no corrió queda en None."""
    def k(conjunto, cifra):
        return kn(ex[conjunto][cifra])[0] if conjunto in ex else None
    return {'coreanas': k('externo', 'estafas'), 'coreanas a tiempo': k('externo', 'a tiempo'),
            'FA reales': k('legitimas_reales', 'FA'),
            'desarrollo estafas': k('desarrollo', 'estafas'), 'desarrollo a tiempo': k('desarrollo', 'a tiempo'),
            'desarrollo FA': k('desarrollo', 'FA'),
            'test estafas': k('test_reservado', 'estafas'), 'test a tiempo': k('test_reservado', 'a tiempo'),
            'test FA': k('test_reservado', 'FA')}


def veredicto(c, r):
    """('sirve' | 'no sirve', por qué): el candidato `c` contra la referencia `r` de la misma sesión, en los reales."""
    faltas = []
    if c['coreanas'] < r['coreanas'] - PIERDE:
        faltas.append(f"pierde {r['coreanas'] - c['coreanas']} coreanas")
    if c['coreanas a tiempo'] < r['coreanas a tiempo'] - PIERDE:
        faltas.append(f"pierde {r['coreanas a tiempo'] - c['coreanas a tiempo']} coreanas a tiempo")
    if c['FA reales'] > r['FA reales'] - BAJA_FA:
        faltas.append(f"las FA reales cambian {c['FA reales'] - r['FA reales']:+d}, y tienen que bajar {BAJA_FA} o más")
    if c['desarrollo a tiempo'] * 2 <= r['desarrollo a tiempo']:
        faltas.append(f"en desarrollo pierde la mitad o más de los avisos a tiempo ({c['desarrollo a tiempo']} de "
                      f"{r['desarrollo a tiempo']})")
    return ('no sirve', '; '.join(faltas)) if faltas else ('sirve', f"coreanas {c['coreanas'] - r['coreanas']:+d}, a tiempo "
                                                         f"{c['coreanas a tiempo'] - r['coreanas a tiempo']:+d}, FA reales "
                                                         f"{c['FA reales'] - r['FA reales']:+d}")


def ordenar(res, ref):
    """Los candidatos que sirven, del mejor al peor: el que menos pierde a tiempo en desarrollo; empate, menos FA
    reales; empate, el que cambia menos."""
    sirven = [c for c in CANDIDATOS if c in res and veredicto(res[c], ref)[0] == 'sirve']
    return sorted(sirven, key=lambda c: (ref['desarrollo a tiempo'] - res[c]['desarrollo a tiempo'], res[c]['FA reales'],
                                         CANDIDATOS.index(c)))


def elegir(res, ref):
    return next(iter(ordenar(res, ref)), None)


def costo_alto(c, r):
    """Las cifras del test en que el candidato pierde tanto o más que el tope ([] si ninguna o si el test no corrió)."""
    return [f"{cifra} {c[cifra] - r[cifra]:+d}" for cifra, tope in COSTO_ALTO.items()
            if c[cifra] is not None and r[cifra] is not None and r[cifra] - c[cifra] >= tope]


def nombre(c):
    return f'`{c[0]}` · {c[1]}'


def celda(e):
    k, n = kn(e)
    return f'{k}/{n}' if n else '—'


# --- Lectura y cifras ---
def cargar(datos):
    """(conjuntos por tanda, riesgos leídos por tanda y carpeta, filas del control): solo entran las corridas sin problemas."""
    conjs, leidas, control = {}, collections.defaultdict(dict), []
    for tanda, (nombre_conj, _) in TANDAS.items():
        if not (datos / 'conjuntos' / nombre_conj / 'conjunto.json').exists():
            continue
        conj = conjs[tanda] = conjuntos.Conjunto(datos / 'conjuntos' / nombre_conj)
        ids = casos_de(tanda, conj)
        for carpeta, prompt in PROMPTS.items():
            corrida = fin.leer(datos / tanda / carpeta)
            if corrida is None:
                if tanda in FASE_1:
                    control.append([tanda, carpeta, '—', '—', 'falta'])
                continue
            por_config, man = corrida
            filas = fin.filas_de(por_config, man, carpeta, prompt)
            prob = controlar(conj, prompt, filas, man, ids)
            consultas = [r for v in filas.values() for r in v if r['hablante'] == 'OTRA']
            invalidas = collections.Counter(r['error'].split(':')[0] for r in consultas if r['valida'] != 'true')
            control.append([tanda, carpeta, (man.get('codigo', {}).get('commit') or '')[:10],
                            f'{sum(invalidas.values())}/{len(consultas)}' + (f' {dict(invalidas)}' if invalidas else ''),
                            '; '.join(prob) or 'bien'])
            if not prob:
                leidas[tanda][carpeta] = {i: riesgos(filas[i]) for i in ids}
    return conjs, leidas, control


def calcular(conjs, leidas):
    """(avisos, cifras): combinación de prompt y política → tanda → {caso: línea del aviso} y sus exitos."""
    avs, ex = collections.defaultdict(dict), collections.defaultdict(dict)
    refs = {tanda: conj.referencia() for tanda, conj in conjs.items()}
    for carpeta, politica in [REFERENCIA, *CANDIDATOS]:
        for tanda in conjs:
            if carpeta in leidas[tanda]:
                av = {i: POLITICAS[politica](l) for i, l in leidas[tanda][carpeta].items()}
                avs[(carpeta, politica)][tanda] = av
                ex[(carpeta, politica)][tanda] = fin.exitos(av, list(av), refs[tanda])
    return avs, ex


def aplicar(ex):
    """(cifras por candidato, cifras de la referencia, candidatos que sirven en orden), o (None, None, []) sin referencia."""
    res = {c: resumen(ex[c]) for c in [REFERENCIA, *CANDIDATOS] if set(FASE_1) <= set(ex[c])}
    if REFERENCIA not in res:
        return None, None, []
    return res, res[REFERENCIA], ordenar(res, res[REFERENCIA])


def carpetas_fase_2(orden):
    """La base y los prompts de los primeros PASAN_A_FASE_2 candidatos que sirven, sin repetir."""
    carpetas = ['base']
    for carpeta, _ in orden[:PASAN_A_FASE_2]:
        if carpeta not in carpetas:
            carpetas.append(carpeta)
    return carpetas


def para_fase_2(datos):
    """(carpetas que corren la fase 2, candidatos que sirven en orden). Lo usa el script de Colab al terminar la fase 1."""
    conjs, leidas, _ = cargar(datos)
    _, ex = calcular(conjs, leidas)
    _, _, orden = aplicar(ex)
    return carpetas_fase_2(orden), orden


# --- Informe ---
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, required=True, help='el ZIP de Colab descomprimido, fuera del repositorio')
    args = p.parse_args(argv)
    datos = args.datos.resolve()
    assert set(PROMPTS.values()) <= PROMPTS_CORTE_RIESGO
    print('# #52, exploración con los conjuntos reales — análisis offline\n')
    print('Posterior a la evaluación final: no la reemplaza. Referencia: `base` (`c-consejos-corte-riesgo`) con el primer '
          'aviso, corrida en esta misma sesión. «Confirmación» es riesgo ≥ 0,5, o el segundo riesgo ≥ 0,3.\n')
    fin.humo(datos)
    conjs, leidas, control = cargar(datos)
    print('## Control de las corridas\n')
    tabla(control, ['tanda', 'corrida', 'commit', 'líneas de OTRA inválidas', 'control'])
    avs, ex = calcular(conjs, leidas)
    combos = [REFERENCIA, *CANDIDATOS]
    cifras = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA']

    def cuadro(tanda):
        con = [c for c in combos if tanda in ex[c]]
        if not con:
            print('> No corrió.\n')
        elif tanda == 'zona_gris':
            tabla([[nombre(c), celda(ex[c][tanda]['FA'])] for c in con], ['prompt · política', 'avisos'])
        else:
            tabla([[nombre(c)] + [celda(ex[c][tanda][cifra]) for cifra in cifras] for c in con], ['prompt · política', *cifras])

    print('# Fase 1: lo que usa la regla\n')
    for tanda in FASE_1:
        print(f'## {NOMBRES[tanda]}\n')
        cuadro(tanda)

    print('## La regla\n')
    res, ref, orden = aplicar(ex)
    if res is None:
        print('> Falta la referencia en alguna tanda de la fase 1: la regla no se puede aplicar.\n')
        return 0
    print(f"Referencia: coreanas {ref['coreanas']}, a tiempo {ref['coreanas a tiempo']}, FA reales {ref['FA reales']}; "
          f"en desarrollo, a tiempo {ref['desarrollo a tiempo']} y FA {ref['desarrollo FA']}.\n")
    filas_md = []
    for c in CANDIDATOS:
        if c not in res:
            filas_md.append([nombre(c), 'no corrió', '—', '—', '—', '—'])
            continue
        v, por_que = veredicto(res[c], ref)
        alto = costo_alto(res[c], ref)
        filas_md.append([nombre(c), v + (f' ({orden.index(c) + 1}.º)' if c in orden else ''), por_que,
                         f"{res[c]['desarrollo a tiempo'] - ref['desarrollo a tiempo']:+d}",
                         f"{res[c]['desarrollo FA'] - ref['desarrollo FA']:+d}",
                         ('alto: ' + ', '.join(alto)) if alto else ('—' if res[c]['test a tiempo'] is None else 'no')])
    tabla(filas_md, ['candidato', 'resultado', 'por qué', 'a tiempo en desarrollo', 'FA en desarrollo', 'costo alto en el test'])
    elegido = orden[0] if orden else None
    if elegido is None:
        print('**Resultado: no sirve ninguno. Queda la configuración de la evaluación final.**\n')
    else:
        print(f'**Resultado: {nombre(elegido)}.** Integrarlo o no lo decide Mateo, con el costo a la vista.\n')
    print(f'**La vara que ya existe, `v4-corte` en la evaluación final:** {V4_EN_LA_FINAL}.\n')

    print('# Fase 2: solo para la base y los prompts que sirven\n')
    for tanda in FASE_2:
        print(f'## {NOMBRES[tanda]}\n')
        cuadro(tanda)

    print('# Aparte, solo para mirar\n')
    if 'desarrollo' in conjs and ETIQUETAS.exists():
        et = json.loads(ETIQUETAS.read_text(encoding='utf-8'))['casos']
        estrictas = [i for i in casos_de('desarrollo', conjs['desarrollo']) if et.get(i, {}).get('etiqueta') == 'no_avisar']
        print(f'## Desarrollo: FA en las {len(estrictas)} que no deberían avisar (etiquetas de producto)\n')
        tabla([[nombre(c), f"{sum(avs[c]['desarrollo'][i] is not None for i in estrictas)}/{len(estrictas)}"]
               for c in combos if 'desarrollo' in avs[c]], ['prompt · política', 'FA estrictas'])
    print('## Qué valores escribe cada prompt (porcentaje de las consultas válidas)\n')
    filas_md = []
    for tanda in conjs:
        for carpeta in PROMPTS:
            if carpeta in leidas[tanda]:
                rs = collections.Counter(r for l in leidas[tanda][carpeta].values() for _, r in l)
                total = sum(rs.values())
                if total:
                    filas_md.append([NOMBRES[tanda], carpeta, total,
                                     ' · '.join(f'{v:g}: {100 * k / total:.0f} %' for v, k in sorted(rs.items()) if 100 * k / total >= 0.5)])
    tabla(filas_md, ['tanda', 'prompt', 'consultas', 'valores'])
    print('## Otros cortes, sin esperar confirmación (estafas avisadas · a tiempo · FA o avisos)\n')
    filas_md = []
    for tanda, conj in conjs.items():
        ref_t = conj.referencia()
        for carpeta in PROMPTS:
            if carpeta in leidas[tanda]:
                celdas = []
                for u in (0.3, 0.5, 0.7):
                    av = {i: next((n for n, r in l if r >= u), None) for i, l in leidas[tanda][carpeta].items()}
                    e = fin.exitos(av, list(av), ref_t)
                    celdas.append(' · '.join(celda(e[c]) for c in ('estafas', 'a tiempo', 'FA') if kn(e[c])[1]))
                filas_md.append([NOMBRES[tanda], carpeta, *celdas])
    tabla(filas_md, ['tanda', 'prompt', 'riesgo ≥ 0,3', 'riesgo ≥ 0,5', 'riesgo ≥ 0,7'])
    print('## Cuántas veces baja el riesgo de una consulta a la siguiente (ruido, si la escala es acumulada)\n')
    filas_md = []
    for tanda in conjs:
        for carpeta in PROMPTS:
            if carpeta in leidas[tanda]:
                pares = [(a, b) for l in leidas[tanda][carpeta].values() for (_, a), (_, b) in zip(l, l[1:])]
                if pares:
                    filas_md.append([NOMBRES[tanda], carpeta, f'{sum(b < a for a, b in pares)}/{len(pares)}',
                                     f'{sum(a >= UMBRAL > b for a, b in pares)}'])
    tabla(filas_md, ['tanda', 'prompt', 'bajadas', 'de ≥ 0,3 a menos'])
    print('## Cuántas consultas con riesgo ≥ 0,3 tiene cada llamada (0, 1, 2, 3, 4, 5 o más)\n')
    filas_md = []
    for tanda, conj in conjs.items():
        ref_t = conj.referencia()
        for carpeta in PROMPTS:
            if carpeta not in leidas[tanda]:
                continue
            for grupo, ids in (('estafas', [i for i in leidas[tanda][carpeta] if ref_t[i]['clase'] == 'vishing']),
                               ('legítimas', [i for i in leidas[tanda][carpeta] if ref_t[i]['clase'] != 'vishing'])):
                if ids:
                    cuenta = collections.Counter(min(sum(r >= UMBRAL for _, r in leidas[tanda][carpeta][i]), 5) for i in ids)
                    filas_md.append([NOMBRES[tanda], grupo, carpeta, ' · '.join(str(cuenta[k]) for k in range(6))])
    tabla(filas_md, ['tanda', 'grupo', 'prompt', 'llamadas con 0 · 1 · 2 · 3 · 4 · 5+'])
    if elegido is not None:
        print(f'## Con {nombre(elegido)}, caso por caso en los reales\n')
        for tanda in ('externo', 'legitimas_reales'):
            antes, ahora = avs[REFERENCIA][tanda], avs[elegido][tanda]
            dejan = sorted(i for i in antes if antes[i] is not None and ahora[i] is None)
            suman = sorted(i for i in antes if antes[i] is None and ahora[i] is not None)
            print(f"- {NOMBRES[tanda]}: deja de avisar en {len(dejan)} ({', '.join(dejan) or 'ninguna'}) y suma {len(suman)} "
                  f"({', '.join(suman) or 'ninguna'}).")
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
