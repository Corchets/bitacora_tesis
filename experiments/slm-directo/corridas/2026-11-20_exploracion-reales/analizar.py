"""#52, exploración con los conjuntos reales, posterior a la evaluación final: no la reemplaza.

Busca una configuración que siga avisando las estafas reales coreanas y avise menos en las legítimas reales de call
center. Prueba dos cosas, solas y juntas: un párrafo del prompt (`c-comercial`, `c-rumbo`) y la política de aviso
(«confirmación»). La regla está en README.md, escrita antes de correr, y es la de este archivo.

No corre modelos; solo biblioteca estándar y el código del laboratorio. Uso, desde esta carpeta:
    python -I analizar.py --datos CARPETA    # el ZIP de Colab descomprimido en CARPETA, fuera del repositorio

CARPETA trae conjuntos/, humo/ y una corrida por conjunto y prompt: <conjunto>/<base|c-comercial|c-rumbo>/. Todas
corren solo en las líneas de OTRA y en todas ellas (--seguir-tras-aviso), para poder aplicar las dos políticas sobre
los mismos riesgos:
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
PROMPTS = {'base': BASE, 'c-comercial': 'c-comercial-corte-riesgo', 'c-rumbo': 'c-rumbo-corte-riesgo'}  # carpeta → prompt
CONJUNTOS = ['externo', 'legitimas_reales', 'desarrollo', 'test_reservado']  # el orden en que corren: primero los reales
NOMBRES = {'externo': 'Estafas reales coreanas (#144)', 'legitimas_reales': 'Legítimas reales (CallCenterEN)',
           'desarrollo': 'Desarrollo (alcance-140)', 'test_reservado': 'Test reservado (vista principal)'}
ENTEROS = {'externo', 'legitimas_reales'}  # corren todos sus casos; de desarrollo y del test, solo la vista principal
UMBRAL, FUERTE = 0.3, 0.5
REFERENCIA = ('base', 'primer aviso')
# En este orden se desempata: primero lo que cambia menos.
CANDIDATOS = [('base', 'confirmación'), ('c-comercial', 'primer aviso'), ('c-rumbo', 'primer aviso'),
              ('c-comercial', 'confirmación'), ('c-rumbo', 'confirmación')]
PIERDE = 1       # en las coreanas puede perder a lo sumo una, en avisadas y en a tiempo
BAJA_FA = 7      # y tiene que bajar 7 o más las FA de las 33 legítimas reales (un tercio de las 21 de la evaluación final)
COSTO_ALTO = {'test a tiempo': 8, 'test estafas': 10}  # lo que se marca como costo alto en las estafas generadas
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


def casos_de(conj):
    """Los casos de un conjunto que corren en la exploración (lo usa también el script de Colab)."""
    if conj.nombre in ENTEROS:
        return list(conj.ids)
    ref = conj.referencia()
    return [i for i in conj.ids if ref[i]['vista'] == conjuntos.PRINCIPAL]


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
    return ('no sirve', '; '.join(faltas)) if faltas else ('sirve', f"coreanas {c['coreanas'] - r['coreanas']:+d}, a tiempo "
                                                         f"{c['coreanas a tiempo'] - r['coreanas a tiempo']:+d}, FA reales "
                                                         f"{c['FA reales'] - r['FA reales']:+d}")


def elegir(res, ref):
    """El candidato que sirve y menos pierde a tiempo en desarrollo; empate, menos FA reales; empate, el que cambia menos."""
    sirven = [c for c in CANDIDATOS if c in res and veredicto(res[c], ref)[0] == 'sirve']
    if not sirven:
        return None
    return min(sirven, key=lambda c: (ref['desarrollo a tiempo'] - res[c]['desarrollo a tiempo'], res[c]['FA reales'],
                                      CANDIDATOS.index(c)))


def costo_alto(c, r):
    """Las cifras del test en que el candidato pierde tanto o más que el tope ([] si ninguna o si el test no corrió)."""
    return [f"{cifra} {c[cifra] - r[cifra]:+d}" for cifra, tope in COSTO_ALTO.items()
            if c[cifra] is not None and r[cifra] is not None and r[cifra] - c[cifra] >= tope]


def nombre(c):
    return f'`{c[0]}` · {c[1]}'


def celda(e):
    k, n = kn(e)
    return f'{k}/{n}' if n else '—'


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

    conjs = {n: conjuntos.Conjunto(datos / 'conjuntos' / n) for n in CONJUNTOS if (datos / 'conjuntos' / n / 'conjunto.json').exists()}
    print('## Control de las corridas\n')
    filas_md, leidas = [], collections.defaultdict(dict)
    for n, conj in conjs.items():
        ids = casos_de(conj)
        for carpeta, prompt in PROMPTS.items():
            corrida = fin.leer(datos / n / carpeta)
            if corrida is None:
                filas_md.append([n, carpeta, '—', '—', 'falta'])
                continue
            por_config, man = corrida
            filas = fin.filas_de(por_config, man, carpeta, prompt)
            prob = controlar(conj, prompt, filas, man, ids)
            consultas = [r for v in filas.values() for r in v if r['hablante'] == 'OTRA']
            invalidas = collections.Counter(r['error'].split(':')[0] for r in consultas if r['valida'] != 'true')
            filas_md.append([n, carpeta, (man.get('codigo', {}).get('commit') or '')[:10],
                             f'{sum(invalidas.values())}/{len(consultas)}' + (f' {dict(invalidas)}' if invalidas else ''),
                             '; '.join(prob) or 'bien'])
            if not prob:
                leidas[n][carpeta] = {i: riesgos(filas[i]) for i in ids}
    tabla(filas_md, ['conjunto', 'corrida', 'commit', 'líneas de OTRA inválidas', 'control'])

    # Cifras de cada combinación de prompt y política, por conjunto.
    combos = [REFERENCIA, *CANDIDATOS]
    ex = collections.defaultdict(dict)  # combinación → conjunto → exitos
    avs = collections.defaultdict(dict)  # combinación → conjunto → {caso: línea del aviso}
    refs = {n: conj.referencia() for n, conj in conjs.items()}
    principal = {n: [i for i in conj.ids if refs[n][i]['vista'] == conjuntos.PRINCIPAL] for n, conj in conjs.items()}
    for carpeta, politica in combos:
        for n in conjs:
            if carpeta in leidas[n]:
                av = {i: POLITICAS[politica](l) for i, l in leidas[n][carpeta].items()}
                avs[(carpeta, politica)][n] = av
                ex[(carpeta, politica)][n] = fin.exitos(av, principal[n], refs[n])
    for n in conjs:
        print(f'## {NOMBRES[n]}\n')
        cifras = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA']
        tabla([[nombre(c)] + [celda(ex[c][n][cifra]) for cifra in cifras] for c in combos if n in ex[c]], ['prompt · política', *cifras])

    # La regla.
    print('## La regla\n')
    necesarios = {'externo', 'legitimas_reales', 'desarrollo'}
    res = {c: resumen(ex[c]) for c in combos if necesarios <= set(ex[c])}
    if REFERENCIA not in res:
        print('> Falta la referencia en los conjuntos reales o en desarrollo: la regla no se puede aplicar.\n')
        return 0
    ref = res[REFERENCIA]
    print(f"Referencia: coreanas {ref['coreanas']}, a tiempo {ref['coreanas a tiempo']}, FA reales {ref['FA reales']}; "
          f"en desarrollo, a tiempo {ref['desarrollo a tiempo']}.\n")
    filas_md = []
    for c in CANDIDATOS:
        if c not in res:
            filas_md.append([nombre(c), 'no corrió', '—', '—', '—'])
            continue
        v, por_que = veredicto(res[c], ref)
        alto = costo_alto(res[c], ref)
        filas_md.append([nombre(c), v, por_que, f"{res[c]['desarrollo a tiempo'] - ref['desarrollo a tiempo']:+d}",
                         ('alto: ' + ', '.join(alto)) if alto else ('—' if res[c]['test a tiempo'] is None else 'no')])
    tabla(filas_md, ['candidato', 'resultado', 'por qué', 'a tiempo en desarrollo', 'costo alto en el test'])
    elegido = elegir(res, ref)
    if elegido is None:
        print('**Resultado: no sirve ninguno. Queda la configuración de la evaluación final.**\n')
    else:
        print(f'**Resultado: {nombre(elegido)}.** Integrarlo o no lo decide Mateo, con el costo a la vista.\n')

    # Aparte, solo para mirar.
    print('## Aparte, solo para mirar\n')
    if 'legitimas_reales' in conjs:
        gris = [i for i in conjs['legitimas_reales'].ids if refs['legitimas_reales'][i]['vista'] != conjuntos.PRINCIPAL]
        print(f'### Zona gris de Medicare ({len(gris)}): avisos, no son FA\n')
        tabla([[nombre(c), f"{sum(avs[c]['legitimas_reales'][i] is not None for i in gris)}/{len(gris)}"]
               for c in combos if 'legitimas_reales' in avs[c]], ['prompt · política', 'avisos'])
    if 'desarrollo' in conjs and ETIQUETAS.exists():
        et = json.loads(ETIQUETAS.read_text(encoding='utf-8'))['casos']
        estrictas = [i for i in principal['desarrollo'] if et.get(i, {}).get('etiqueta') == 'no_avisar']
        print(f'### Desarrollo: FA en las {len(estrictas)} que no deberían avisar (etiquetas de producto)\n')
        tabla([[nombre(c), f"{sum(avs[c]['desarrollo'][i] is not None for i in estrictas)}/{len(estrictas)}"]
               for c in combos if 'desarrollo' in avs[c]], ['prompt · política', 'FA estrictas'])
    print('### Cuántas consultas con riesgo ≥ 0,3 tiene cada llamada (0, 1, 2, 3, 4, 5 o más)\n')
    filas_md = []
    for n in conjs:
        for grupo, ids in (('estafas', [i for i in principal[n] if refs[n][i]['clase'] == 'vishing']),
                           ('legítimas', [i for i in principal[n] if refs[n][i]['clase'] != 'vishing'])):
            for carpeta in PROMPTS:
                if ids and carpeta in leidas[n]:
                    cuenta = collections.Counter(min(sum(r >= UMBRAL for _, r in leidas[n][carpeta][i]), 5) for i in ids)
                    filas_md.append([NOMBRES[n], grupo, carpeta, ' · '.join(str(cuenta[k]) for k in range(6))])
    tabla(filas_md, ['conjunto', 'grupo', 'prompt', 'llamadas con 0 · 1 · 2 · 3 · 4 · 5+'])
    if elegido is not None:
        print(f'### Con {nombre(elegido)}, caso por caso en los reales\n')
        for n in ('externo', 'legitimas_reales'):
            antes, ahora = avs[REFERENCIA][n], avs[elegido][n]
            dejan = sorted(i for i in principal[n] if antes[i] is not None and ahora[i] is None)
            suman = sorted(i for i in principal[n] if antes[i] is None and ahora[i] is not None)
            print(f"- {NOMBRES[n]}: deja de avisar en {len(dejan)} ({', '.join(dejan) or 'ninguna'}) y suma {len(suman)} "
                  f"({', '.join(suman) or 'ninguna'}).")
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
