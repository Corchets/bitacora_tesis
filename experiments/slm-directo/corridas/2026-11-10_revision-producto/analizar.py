"""#143, revisión de producto: tres cambios de un párrafo a la configuración congelada (c-premisa-corte-riesgo).

No corre modelos ni lee la reserva; solo biblioteca estándar y el código del laboratorio. Uso, desde esta carpeta, con
los ZIP de Colab descomprimidos acá (humo/, base/, c-codigo/, c-consejos/, c-freno/ y sus -rep/):
    python -I analizar.py                       # todo
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Escrito el 2026-11-10, antes de correr la prueba. Aplica tal cual la regla de README.md («Regla, escrita antes de
correr»). La regla se calcula en dos versiones y decide una sola (DECIDE):
- «producto»: las FA que cuentan son los avisos en las 75 legítimas «no debería avisar» de etiquetas-producto.json;
- «original»: las FA que cuentan son las de las 29 cotidianas, y el total es sobre las 94, como en la sensibilidad.
En las dos, una variante pasa por detección si (1) suma 3 o más en una cifra de detección, (2) no pierde 3 o más en
ninguna, (3) no suma 3 o más FA de las que cuentan, y (4) su repetición, contra la de la base, suma 3 o más en una cifra
en que ganó la primera corrida, sin perder 3 o más en ninguna y sin sumar 3 o más FA. Si ninguna pasa por detección,
pasa por FA la que baja 3 o más el total de FA de su versión (/75 o /94) sin perder 3 o más en ninguna cifra de
detección, en la corrida y en la repetición. Si pasan varias por detección, la que más suma en estafas y a tiempo,
juntas, en la primera corrida, y si empatan, la de menos FA; si pasan varias por FA, la que más baja, y si empatan, la
que más suma en estafas y a tiempo. Si no pasa ninguna, queda la base.
"""

import argparse, collections, importlib.util, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# La sensibilidad ya trae la vista, la referencia, el control de una corrida y las cifras de detección: se usan tal cual.
s = _cargar('analizar_sensibilidad_para_revision', AQUI.parent / '2026-11-10_sensibilidad-c' / 'analizar.py')
e3, IDS, REF, VISTA, num, tabla, p50_p95, celda = s.e3, s.IDS, s.REF, s.VISTA, s.num, s.tabla, s.p50_p95, s.h.celda

# 'producto' si Mateo acepta las etiquetas de etiquetas-producto.json; 'original' si no. Se fija en el commit del tag.
DECIDE = 'producto'
BASE = 'c-premisa-corte-riesgo'
VARIANTES = {'c-codigo': 'c-codigo-corte-riesgo', 'c-consejos': 'c-consejos-corte-riesgo', 'c-freno': 'c-freno-corte-riesgo'}
CORRIDAS = {'base': (BASE, None), **{c: (p, None) for c, p in VARIANTES.items()},
            'base-rep': (BASE, 'alcance-140'), **{f'{c}-rep': (p, 'alcance-140') for c, p in VARIANTES.items()}}
s.CORRIDAS = CORRIDAS  # el control de la sensibilidad, con las corridas de esta prueba
UMBRAL, MARGEN = s.UMBRAL, s.MARGEN
DETECCION = s.DETECCION

ETIQUETAS = json.loads((AQUI / 'etiquetas-producto.json').read_text(encoding='utf-8'))['casos']
assert sorted(ETIQUETAS) == sorted(e3.LEGITIMAS), 'las etiquetas no son las de las 94 legítimas de alcance-140'
NO_AVISAR = [i for i in e3.LEGITIMAS if ETIQUETAS[i]['etiqueta'] == 'no_avisar']
TOLERABLES = [i for i in e3.LEGITIMAS if ETIQUETAS[i]['etiqueta'] == 'tolerable']
AVISAR = [i for i in e3.LEGITIMAS if ETIQUETAS[i]['etiqueta'] == 'avisar']
assert (len(NO_AVISAR), len(TOLERABLES), len(AVISAR)) == (75, 18, 1), 'las etiquetas no son las anotadas'
CODIGO_O_CLAVE = [i for i in e3.ESTAFAS if REF[i].get('pedido') in ('REQUEST_AUTH_CODE', 'REQUEST_SECRET')]
DATOS_PERSONALES = [i for i in e3.ESTAFAS if REF[i].get('pedido') == 'REQUEST_PERSONAL_DATA']
assert (len(CODIGO_O_CLAVE), len(DATOS_PERSONALES)) == (17, 6), 'la vista no es la anotada'

# Por versión de la regla: la FA con tope (no puede sumar 3 o más) y la FA total (para pasar por FA y desempatar).
VERSIONES = {'producto': ('FA estrictas', 'FA estrictas'), 'original': ('FA cotidianas', 'FA')}
DENOMINADORES = {**s.DENOMINADORES, 'FA estrictas': 75, 'FA tolerables': 18, 'debería avisar': 1, 'código o clave': 17,
                 'código o clave, a tiempo': 17}
COLUMNAS = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA estrictas', 'FA tolerables',
            'debería avisar', 'FA cotidianas', 'FA dudosas', 'FA', 'código o clave', 'código o clave, a tiempo']


def avisos(filas, ids, u=UMBRAL):
    return s.avisos(filas, ids, u)


def cifras(av):
    """Las cifras de la sensibilidad, más las de producto y, aparte, las estafas con pedido de código o clave."""
    c = s.cifras(av)
    c['FA estrictas'] = sum(av.get(i) is not None for i in NO_AVISAR)
    c['FA tolerables'] = sum(av.get(i) is not None for i in TOLERABLES)
    c['debería avisar'] = sum(av.get(i) is not None for i in AVISAR)
    c['código o clave'] = sum(av.get(i) is not None for i in CODIGO_O_CLAVE)
    c['código o clave, a tiempo'] = sum(av.get(i) is not None and av[i] <= REF[i]['t_r_linea'] for i in CODIGO_O_CLAVE)
    return c


def fmt(c):
    return [f'{c[k]}/{DENOMINADORES[k]}' for k in COLUMNAS]


def diferencias(c, ref):
    return {k: c[k] - ref[k] for k in DETECCION}


def veredicto(c, base, cr, base_r, version):
    """('pasa por detección' / 'pasa por FA' / 'no pasa', razón) de una variante contra la base, con la repetición."""
    tope, total = VERSIONES[version]
    d = diferencias(c, base)
    gana = [k for k, x in d.items() if x >= MARGEN]
    pierde = [k for k, x in d.items() if x <= -MARGEN]
    texto = ', '.join(f'{x:+d} {k}' for k, x in d.items()) + f', {tope} {c[tope] - base[tope]:+d}' \
        + (f', {total} {c[total] - base[total]:+d}' if total != tope else '')
    if pierde:
        return 'no pasa', f'pierde 3 o más en {", ".join(pierde)} ({texto})'
    if cr is None or base_r is None:
        return 'no pasa', 'falta la repetición (de la variante o de la base)'
    dr = diferencias(cr, base_r)
    texto_r = ', '.join(f'{x:+d} {k}' for k, x in dr.items()) + f', {tope} {cr[tope] - base_r[tope]:+d}'
    if any(x <= -MARGEN for x in dr.values()):
        return 'no pasa', f'la repetición pierde 3 o más en alguna cifra ({texto_r})'
    if gana:
        if c[tope] - base[tope] >= MARGEN:
            return 'no pasa', f'suma 3 o más en {tope} ({texto})'
        if not any(dr[k] >= MARGEN for k in gana):
            return 'no pasa', f'la repetición no sostiene la ganancia ({texto_r})'
        if cr[tope] - base_r[tope] >= MARGEN:
            return 'no pasa', f'la repetición suma 3 o más en {tope} ({texto_r})'
        return 'pasa por detección', f'{texto}; repetición: {texto_r}'
    if base[total] - c[total] >= MARGEN and base_r[total] - cr[total] >= MARGEN:
        return 'pasa por FA', f'{texto}; repetición: {texto_r}, {total} {cr[total] - base_r[total]:+d}'
    return 'no pasa', f'no suma 3 o más en ninguna cifra de detección ni baja 3 o más en {total} ({texto})'


def elegir(resultados, cs, base, version):
    """La variante que queda, según la regla, o None si queda la base."""
    _, total = VERSIONES[version]

    def suma(v):
        return cs[v]['estafas'] - base['estafas'] + cs[v]['a tiempo'] - base['a tiempo']

    por_deteccion = [v for v, (estado, _) in resultados.items() if estado == 'pasa por detección']
    if por_deteccion:
        return min(por_deteccion, key=lambda v: (-suma(v), cs[v][total]))
    por_fa = [v for v, (estado, _) in resultados.items() if estado == 'pasa por FA']
    if por_fa:
        return min(por_fa, key=lambda v: (cs[v][total], -suma(v)))
    return None


def aplicar(cs, pasa_humo, version):
    resultados = {}
    for v in VARIANTES:
        if not pasa_humo.get(VARIANTES[v]):
            resultados[v] = ('no pasa', 'no pasó la humo de formato o falta')
        elif v not in cs:
            resultados[v] = ('no pasa', 'falta la corrida o tiene problemas')
        else:
            resultados[v] = veredicto(cs[v], cs['base'], cs.get(f'{v}-rep'), cs.get('base-rep'), version)
    return resultados, elegir(resultados, cs, cs['base'], version)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    args = p.parse_args(argv)
    datos = args.datos.resolve()
    print('# #143, revisión de producto — análisis offline\n')
    print('Vista: alcance-140, 46 estafas (36 con pedido, 15 con cumplimiento) y 94 legítimas. Por etiqueta de producto: '
          '75 «no debería avisar», 18 tolerables y 1 «debería avisar». Por la anotación original: 29 cotidianas y 65 con '
          'pedido o mención. El aviso es la primera línea de OTRA con «riesgo ≥ 0,3».\n')
    pasa_humo = s.humo(datos)
    print('## Control de las corridas\n')
    leidas, cs, avs = {}, {}, {}
    filas_md = []
    for carpeta in CORRIDAS:
        corrida = e3.leer(datos, carpeta)
        if corrida is None:
            filas_md.append([carpeta, '—', '—', 'falta'])
            continue
        filas, man = corrida
        prob = s.controlar(carpeta, filas, man)
        consultadas = [r for v in filas.values() for r in v if r['consulta'] != 'omitida']
        invalidas = sum(r['valida'] != 'true' for r in consultadas)
        filas_md.append([carpeta, man['codigo']['commit'][:10], f'{invalidas}/{len(consultadas)}', '; '.join(prob) or 'bien'])
        if not prob:
            leidas[carpeta] = filas
            avs[carpeta] = avisos(filas, sorted(filas))
            cs[carpeta] = cifras(avs[carpeta])
    tabla(filas_md, ['corrida', 'commit', 'líneas inválidas', 'control'])

    print('## Cifras\n')
    tabla([[c, *fmt(x)] for c, x in cs.items()], ['corrida', *COLUMNAS])
    print('«FA estrictas» son los avisos en las 75 «no debería avisar». «Código o clave» se informa aparte y no decide.\n')

    print('## La regla\n')
    if 'base' not in cs:
        print('**No se aplica:** falta la corrida de la base o tiene problemas. Queda la base.\n')
        return 0
    for version in sorted(VERSIONES, key=lambda v: v != DECIDE):
        resultados, elegida = aplicar(cs, pasa_humo, version)
        print(f'### Versión «{version}»' + (' (decide)' if version == DECIDE else ' (se informa, no decide)') + '\n')
        tabla([[f'`{v}`', estado, razon] for v, (estado, razon) in resultados.items()], ['variante', 'resultado', 'por qué'])
        texto = 'queda la base' if elegida is None else f'queda `{elegida}`'
        print(f'**Resultado: {texto}.**\n' if version == DECIDE else f'Con esta versión: {texto}.\n')

    print('## Aparte, solo para mirar\n')
    aparte(leidas, avs)
    return 0


def aparte(leidas, avs):
    if 'base' not in avs:
        return
    base = avs['base']
    primeras = [c for c in avs if not c.endswith('-rep')]
    variantes = [v for v in VARIANTES if v in avs]

    def linea(c, i):
        return f'L{avs[c][i]}' if avs[c].get(i) else '–'

    print('### Estafas con pedido de código o clave (/17)\n')
    tabla([[i, REF[i]['pedido'], REF[i]['t_r_linea'], *(linea(c, i) for c in primeras)] for i in CODIGO_O_CLAVE],
          ['caso', 'pedido', 'T_R', *primeras])
    print('### Estafas con pedido de datos personales (/6)\n')
    tabla([[i, REF[i]['t_r_linea'], *(linea(c, i) for c in primeras)] for i in DATOS_PERSONALES], ['caso', 'T_R', *primeras])
    print('### Estafas que la base no avisa, y en qué línea las avisa cada variante\n')
    tabla([[i, REF[i].get('pedido') or 'sin pedido', REF[i].get('t_r_linea') or '—', *(linea(v, i) for v in variantes)]
           for i in e3.ESTAFAS if base[i] is None], ['caso', 'pedido', 'T_R', *variantes])
    print('### Estafas que la base avisa y alguna variante pierde\n')
    tabla([[i, REF[i].get('pedido') or 'sin pedido', linea('base', i), *(linea(v, i) for v in variantes)]
           for i in e3.ESTAFAS if base[i] is not None and any(avs[v][i] is None for v in variantes)],
          ['caso', 'pedido', 'base', *variantes])

    print('### FA por intención de la llamada (etiqueta de producto)\n')
    intenciones = sorted({ETIQUETAS[i]['intencion'] for i in e3.LEGITIMAS})
    n = collections.Counter(ETIQUETAS[i]['intencion'] for i in e3.LEGITIMAS)
    tabla([[c, *(f"{sum(avs[c][i] is not None for i in e3.LEGITIMAS if ETIQUETAS[i]['intencion'] == t)}/{n[t]}"
                 for t in intenciones)] for c in primeras], ['corrida', *intenciones])
    print('### FA estrictas por escenario, y en las legítimas «ejemplares» y las que piden el DNI\n')
    escenarios = collections.defaultdict(list)
    for i in NO_AVISAR:
        escenarios[ETIQUETAS[i]['escenario']].append(i)
    ejemplares = [i for i in NO_AVISAR if ETIQUETAS[i]['ejemplar']]
    con_dni = [i for i in NO_AVISAR if 'dni' in ETIQUETAS[i]['pide']]
    tabla([[c, f'{sum(any(avs[c][i] is not None for i in v) for v in escenarios.values())}/{len(escenarios)}',
            f'{sum(avs[c][i] is not None for i in ejemplares)}/{len(ejemplares)}',
            f'{sum(avs[c][i] is not None for i in con_dni)}/{len(con_dni)}'] for c in primeras],
          ['corrida', 'escenarios con alguna FA estricta', 'FA en ejemplares', 'FA en las que piden el DNI'])
    print('### Tolerables y «debería avisar», caso por caso\n')
    tabla([[i, ETIQUETAS[i]['etiqueta'], *(linea(c, i) for c in primeras)] for i in [*AVISAR, *TOLERABLES]],
          ['caso', 'etiqueta', *primeras])

    print('### Curva en todas las líneas de OTRA (estafas · a tiempo · FA estrictas · FA total)\n')
    us = [round(x / 10, 1) for x in range(1, 10)]
    filas_md = []
    for c in primeras:
        fila = [c]
        for u in us:
            x = cifras(avisos(leidas[c], IDS, u))
            fila.append(f"{x['estafas']} · {x['a tiempo']} · {x['FA estrictas']} · {x['FA']}")
        filas_md.append(fila)
    tabla(filas_md, ['corrida', *(f'u={u}' for u in us)])
    print('### Avisos de un 0,3 exacto, latencia y motivo (dentro del alcance)\n')
    filas_md = []
    for c in primeras:
        fila_aviso = {i: next(r for r in leidas[c][i] if int(r['linea']) == avs[c][i]) for i in VISTA if avs[c].get(i)}
        exactos = sum(num(r['riesgo']) == UMBRAL for r in fila_aviso.values())
        con = [r for i in VISTA for r in leidas[c].get(i, []) if r['consulta'] != 'omitida']
        validos = [r for r in fila_aviso.values() if not r['error'].startswith('etapa2_') and r['motivo'].strip()]
        filas_md.append([c, f'{exactos}/{len(fila_aviso)}', p50_p95([num(r['ms_etapa1']) for r in con if num(r['ms_etapa1']) is not None]),
                         p50_p95([num(r['ms_etapa2']) for r in fila_aviso.values() if num(r['ms_etapa2']) is not None]),
                         f'{len(validos)}/{len(fila_aviso)}'])
    tabla(filas_md, ['corrida', 'avisos de 0,3 exacto', 'primera consulta (ms)', 'motivo (ms)', 'motivo válido'])
    print('### FA estrictas que cambian contra la base, con su motivo, para leer a mano\n')
    for v in variantes:
        nuevas = sorted(i for i in NO_AVISAR if avs[v][i] is not None and base[i] is None)
        quitadas = sorted(i for i in NO_AVISAR if avs[v][i] is None and base[i] is not None)
        print(f'**`{v}`:** {len(nuevas)} FA estrictas que la base no tiene; deja de avisar en {len(quitadas)}'
              + (f' ({", ".join(quitadas)})' if quitadas else '') + '.\n')
        if nuevas:
            tabla([[i, ETIQUETAS[i]['intencion'], f'L{avs[v][i]}',
                    *(lambda r: [r['riesgo'], f'«{celda(r["motivo"])}»' if r['motivo'] else '—'])(
                        next(r for r in leidas[v][i] if int(r['linea']) == avs[v][i]))] for i in nuevas],
                  ['caso', 'intención', 'aviso', 'riesgo', 'motivo'])
    print('### alcance-91\n')
    tabla([[c, *e3.fmt(e3.metricas(avs[c], e3.VISTA_91))] for c in primeras], ['corrida', *e3.ENC])


if __name__ == '__main__':
    sys.exit(main())
