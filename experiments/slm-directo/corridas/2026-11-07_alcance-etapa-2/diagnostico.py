"""#143, segunda vuelta, etapa 2: diagnóstico fuera del criterio, escrito el 2026-11-09 después de ver los resultados.

No cambia el criterio ni su resultado: eso está en analizar.py, escrito antes de correr. Este script mira dónde y por
qué C le gana a v4 dentro del alcance, qué errores le quedan a C y cómo se comportan reglas que no se probaron. Lo que
sale de acá son hipótesis: una regla nueva se escribe antes y se prueba en otros casos (ADR 0005).
1. Estafas: de dónde salen las +8 estafas y los +7 avisos antes del pedido, por tipo de pedido.
2. Legítimas: dónde baja la FA, por lote y según lo que pasó en la llamada hasta el aviso.
3. Cómo usa cada prompt el riesgo escrito.
4. Lo que le queda a C: estafas sin aviso a tiempo y FA, con la línea que dispara.
5. La segunda consulta (motivo) con la regla de C.
6. Exploración: avisar con el riesgo sostenido en líneas seguidas.
7. Los controles de ventas, línea por línea.
Solo biblioteca estándar; no corre modelos ni lee la reserva. Uso, desde esta carpeta:
    python -I diagnostico.py
"""
import collections, csv, importlib.util, json, math, statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('analizar_etapa2', AQUI / 'analizar.py')
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
casos, num, tabla, REF = an.casos, an.num, an.tabla, an.REF
REGLA_V4 = f'riesgo ≥ {an.UMBRAL_REFERENCIA:g} o alerta'
PROMPTS = {'v4-corte': 'v4', 'c-json-corte': 'C', 'v4-premisa-corte': 'v4-premisa'}
LOTE = {i: nombre for nombre, lista in an.LOTES.items() for i in an.leer_lista(lista)}
PEDIDOS = ['sin pedido', 'REQUEST_AUTH_CODE', 'REQUEST_SECRET', 'REQUEST_TRANSFER', 'REQUEST_PERSONAL_DATA',
           'REQUEST_SECURITY_ACTION', 'REQUEST_REMOTE_ACCESS']
# Pedidos que ni un banco ni un organismo legítimo hacen por teléfono: códigos, claves, plata, acceso remoto y acciones
# de seguridad. Los datos personales (DNI, fecha de nacimiento) quedan afuera, como en C.
CRITICOS = {'REQUEST_AUTH_CODE', 'REQUEST_SECRET', 'REQUEST_TRANSFER', 'REQUEST_REMOTE_ACCESS', 'REQUEST_SECURITY_ACTION'}


def piso(x):
    """El riesgo al decimal de abajo (0,85 → 0,8), para las tablas."""
    return math.floor(x * 10 + 1e-9) / 10


def mcnemar(solo_a, solo_b):
    """p de McNemar exacto (binomial, dos colas) con los pares discordantes."""
    n = solo_a + solo_b
    if not n:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, k) for k in range(min(solo_a, solo_b) + 1)) / 2 ** n)


def momento(i, linea):
    """Cuándo avisa en una estafa: antes, en o después del pedido; avisa / – si no tiene pedido."""
    t_r = REF[i].get('t_r_linea')
    if linea is None:
        return '–'
    if not t_r:
        return 'avisa'
    return 'antes' if linea < t_r else 'en' if linea == t_r else 'después'


def con_roles(i):
    return casos.con_roles(i, casos.cargar_texto(i))


def ultima_de_otra(i, hasta):
    """La última línea de OTRA hasta `hasta` (inclusive), con su número."""
    lineas = con_roles(i)
    for n in range(hasta, 0, -1):
        if lineas[n - 1].hablante == 'OTRA':
            return n, lineas[n - 1].texto
    return None, ''


def recorte(texto, largo=110):
    return texto if len(texto) <= largo else texto[:largo - 1] + '…'


def eventos_hasta(i, hasta):
    """Eventos de la referencia hasta la línea `hasta`: 'pedido:DATOS', 'mención', etc."""
    nombres = {'REQUEST_PERSONAL_DATA': 'DATOS', 'REQUEST_AUTH_CODE': 'CÓDIGO', 'REQUEST_SECRET': 'CLAVE',
               'REQUEST_TRANSFER': 'PLATA', 'REQUEST_REMOTE_ACCESS': 'ACCESO', 'REQUEST_SECURITY_ACTION': 'ACCIÓN'}
    salida = []
    for e in REF[i].get('evidencia') or []:
        if e['linea'] <= hasta and e['evento'] in ('pedido', 'mencion'):
            etiqueta = '+'.join(nombres.get(t, t) for t in e['etiquetas'] if t.startswith('REQUEST')) or 'otro'
            salida.append(f"L{e['linea']} {'pedido ' + etiqueta if e['evento'] == 'pedido' else 'mención'}")
    return ', '.join(salida) or '—'


def primera(filas_caso, condicion):
    return next((int(r['linea']) for r in filas_caso if r['valida'] == 'true' and condicion(r)), None)


def sostenido(filas, u, k, ids):
    """Exploración: avisa con alerta escrita, o con riesgo ≥ u en k líneas seguidas."""
    salida = {}
    for i in ids:
        racha, salida[i] = 0, None
        for r in filas.get(i, []):
            alto = r['valida'] == 'true' and num(r['riesgo']) is not None and num(r['riesgo']) >= u - 1e-9
            racha = racha + 1 if alto else 0
            if r['valida'] == 'true' and (r['alerta_escrita'] == 'true' or racha >= k):
                salida[i] = int(r['linea'])
                break
    return salida


def main():
    filas = {c: an.leer(AQUI, c)[0] for c in an.CORRIDAS}
    curvas = {c: an.curva(f) for c, f in filas.items()}
    F = curvas['v4-corte'][REGLA_V4]['fa']
    regla_c = an.punto(curvas['c-json-corte'], F)[0]
    v4, c = filas['v4-corte'], filas['c-json-corte']
    av_v4, av_c = an.avisos(v4, REGLA_V4, an.IDS), an.avisos(c, regla_c, an.IDS)
    av_c_rep = an.avisos(filas['c-json-corte-rep'], regla_c, an.VISTA)
    av_prem = an.avisos(filas['v4-premisa-corte'], REGLA_V4, an.IDS)
    print('# #143, etapa 2: diagnóstico fuera del criterio (escrito después de ver los resultados)\n')
    print(f'v4 con «{REGLA_V4}» (su regla adoptada) y C con «{regla_c}» (la que eligió analizar.py con FA ≤ {F}). '
          'Primera corrida de cada una, salvo donde se dice.\n')

    # 1. Estafas
    print('## 1. Estafas: de dónde sale la diferencia\n')
    print('Por tipo del primer pedido crítico de la referencia. «antes / en / después» es la línea del primer aviso '
          'contra la del pedido (T_R).\n')
    filas_md = []
    for p in PEDIDOS:
        ids = [i for i in an.ESTAFAS if (REF[i].get('pedido') or 'sin pedido') == p]
        if not ids:
            continue
        cuenta = lambda av: collections.Counter(momento(i, av[i]) for i in ids)  # noqa: E731
        a, b = cuenta(av_v4), cuenta(av_c)
        if p == 'sin pedido':
            filas_md.append([p, len(ids), f"{a['avisa']}", f"{b['avisa']}", '—', '—'])
        else:
            filas_md.append([p, len(ids), len(ids) - a['–'], len(ids) - b['–'],
                             f"{a['antes']} / {a['en']} / {a['después']}", f"{b['antes']} / {b['en']} / {b['después']}"])
    tabla(filas_md, ['pedido', 'estafas', 'v4 avisa', 'C avisa', 'v4 antes / en / después', 'C antes / en / después'])

    conp = [i for i in an.ESTAFAS if REF[i].get('t_r_linea')]
    cruce = collections.Counter((momento(i, av_v4[i]), momento(i, av_c[i])) for i in conp)
    orden = ['antes', 'en', 'después', '–']
    print('Estafas con pedido (36): momento del aviso de v4 (filas) contra el de C (columnas).\n')
    tabla([[f'v4 {x}', *[cruce[(x, y)] for y in orden], sum(cruce[(x, y)] for y in orden)] for x in orden],
          ['', *[f'C {y}' for y in orden], 'total'])
    adelanto = lambda av: [REF[i]['t_r_linea'] - av[i] for i in conp if av[i] is not None and av[i] <= REF[i]['t_r_linea']]  # noqa: E731
    for nombre, av in (('v4', av_v4), ('C', av_c)):
        ad = adelanto(av)
        print(f'- {nombre}: adelanto T_R − T_A en sus avisos a tiempo, mediana {statistics.median(ad):g} líneas '
              f'(n = {len(ad)}; 3 o más líneas antes: {sum(x >= 3 for x in ad)}).')
    print()
    print('Pares discordantes en los mismos casos (McNemar exacto, dos colas; solo para mirar: el umbral de C se eligió '
          'sobre estos mismos casos, así que el p es optimista):\n')
    filas_md = []
    for nombre, ids, prueba in (
            ('estafas avisadas (/46)', an.ESTAFAS, lambda av, i: av[i] is not None),
            ('avisos antes del pedido (/36)', conp, lambda av, i: av[i] is not None and av[i] < REF[i]['t_r_linea']),
            ('detección útil, antes o en el pedido (/36)', conp,
             lambda av, i: av[i] is not None and av[i] <= REF[i]['t_r_linea']),
            ('FA (/94)', an.LEGITIMAS, lambda av, i: av[i] is not None)):
        solo_c = sum(prueba(av_c, i) and not prueba(av_v4, i) for i in ids)
        solo_v4 = sum(prueba(av_v4, i) and not prueba(av_c, i) for i in ids)
        filas_md.append([nombre, solo_c, solo_v4, f'{mcnemar(solo_c, solo_v4):.3f}'])
    tabla(filas_md, ['cifra', 'solo C', 'solo v4', 'p'])
    print('Estafas en que v4 y C difieren (L = línea del primer aviso; – sin aviso):\n')
    filas_md = []
    for i in an.ESTAFAS:
        if (av_v4[i] is None) != (av_c[i] is None) or momento(i, av_v4[i]) != momento(i, av_c[i]):
            filas_md.append([i.removeprefix('CV2-D-V-'), REF[i].get('pedido') or 'sin pedido', REF[i].get('t_r_linea') or '–',
                             len(c[i]), f"L{av_v4[i]}" if av_v4[i] else '–', f"L{av_c[i]}" if av_c[i] else '–',
                             f"L{av_c_rep[i]}" if av_c_rep[i] else '–'])
    tabla(filas_md, ['estafa', 'pedido', 'T_R', 'líneas', 'v4', 'C', 'C (repetición)'])

    # 2. Legítimas
    print('## 2. Legítimas entrantes: dónde baja la FA\n')
    cruce = collections.Counter((av_v4[i] is not None, av_c[i] is not None) for i in an.LEGITIMAS)
    print(f'De las 94: FA con las dos {cruce[(True, True)]}; solo v4 {cruce[(True, False)]}; solo C {cruce[(False, True)]}; '
          f'ninguna {cruce[(False, False)]}.\n')
    filas_md = []
    for lote in an.LOTES:
        ids = [i for i in an.LEGITIMAS if LOTE.get(i) == lote]
        filas_md.append([lote, sum(av_v4[i] is not None for i in ids), sum(av_c[i] is not None for i in ids),
                         sum(av_v4[i] is not None and av_c[i] is None for i in ids),
                         sum(av_c[i] is not None and av_v4[i] is None for i in ids)])
    tabla(filas_md, ['lote', 'FA v4', 'FA C', 'solo v4', 'solo C'])

    def contexto_fa(av):
        """Qué pasó en la legítima hasta la FA, según la referencia."""
        salida = collections.Counter()
        for i in an.LEGITIMAS:
            if av[i] is None:
                continue
            pedidos = [e for e in REF[i].get('evidencia') or [] if e['evento'] == 'pedido' and e['linea'] <= av[i]]
            datos = [e for e in pedidos if 'REQUEST_PERSONAL_DATA' in e['etiquetas']]
            if not pedidos:
                salida['antes de cualquier pedido'] += 1
            elif datos and av[i] == max(e['linea'] for e in datos):
                salida['en la línea de un pedido de datos personales'] += 1
            elif datos:
                salida['después de un pedido de datos personales'] += 1
            else:
                salida['después de otro pedido'] += 1
        return salida
    a, b = contexto_fa(av_v4), contexto_fa(av_c)
    claves = ['antes de cualquier pedido', 'en la línea de un pedido de datos personales',
              'después de un pedido de datos personales', 'después de otro pedido']
    print('Cuándo cae la FA, según los eventos de la referencia de cada legítima:\n')
    tabla([[k, a[k], b[k]] for k in claves] + [['total', sum(a.values()), sum(b.values())]], ['la FA cae…', 'v4', 'C'])
    con_datos = [i for i in an.LEGITIMAS if any(e['evento'] == 'pedido' and 'REQUEST_PERSONAL_DATA' in e['etiquetas']
                                              for e in REF[i].get('evidencia') or [])]
    print(f'Legítimas con algún pedido de datos personales en la referencia: {len(con_datos)}/94. FA en ellas: '
          f'v4 {sum(av_v4[i] is not None for i in con_datos)}, C {sum(av_c[i] is not None for i in con_datos)}; '
          f'en las otras {94 - len(con_datos)}: v4 {sum(av_v4[i] is not None for i in an.LEGITIMAS if i not in con_datos)}, '
          f'C {sum(av_c[i] is not None for i in an.LEGITIMAS if i not in con_datos)}.\n')

    # 3. Riesgo escrito
    print('## 3. Cómo usa cada prompt el riesgo escrito (dentro del alcance, todas las líneas)\n')
    valores = [round(x / 10, 1) for x in range(0, 11)]
    filas_md = []
    for carpeta, nombre in PROMPTS.items():
        f = filas[carpeta]
        for clase, ids in (('estafas', an.ESTAFAS), ('legítimas', an.LEGITIMAS)):
            cuenta = collections.Counter(piso(num(r['riesgo'])) for i in ids for r in f[i] if r['valida'] == 'true')
            total = sum(cuenta.values())
            filas_md.append([nombre, clase, total, *[f'{100 * cuenta[v] / total:.0f}' if cuenta[v] else '·' for v in valores]])
    tabla(filas_md, ['prompt', 'líneas de', 'n', *[f'{v:g}' for v in valores]])
    print('Cada celda: % de líneas con ese riesgo escrito, al decimal de abajo (0,85 cuenta como 0,8; · = ninguna).\n')
    filas_md = []
    for carpeta, nombre in PROMPTS.items():
        f = filas[carpeta]
        altas = [r for i in an.VISTA for r in f[i] if r['valida'] == 'true' and num(r['riesgo']) >= 0.4 - 1e-9]
        alerta = [r for i in an.VISTA for r in f[i] if r['alerta_escrita'] == 'true']
        filas_md.append([nombre, len(altas), sum(r['alerta_escrita'] == 'true' for r in altas), len(alerta),
                         sum(num(r['riesgo']) < 0.4 - 1e-9 for r in alerta)])
    tabla(filas_md, ['prompt', 'líneas con riesgo ≥ 0,4', 'de esas, con alerta escrita', 'líneas con alerta escrita',
                     'de esas, con riesgo < 0,4'])
    print('Máximo riesgo escrito por llamada (cuántas llamadas llegan a cada valor como máximo):\n')
    filas_md = []
    for carpeta, nombre in PROMPTS.items():
        f = filas[carpeta]
        for clase, ids in (('estafas', an.ESTAFAS), ('legítimas', an.LEGITIMAS)):
            maximos = collections.Counter(piso(max(num(r['riesgo']) for r in f[i] if r['valida'] == 'true')) for i in ids)
            filas_md.append([nombre, clase, *[maximos[v] or '·' for v in valores]])
    tabla(filas_md, ['prompt', 'llamadas', *[f'{v:g}' for v in valores]])

    # 4. Lo que le queda a C
    print(f'## 4. Lo que le queda a C con «{regla_c}»\n')
    print('### En qué línea cae el primer aviso\n')
    tramos = [(1, 2), (3, 5), (6, 10), (11, 99)]
    filas_md = []
    for nombre, av in (('v4', av_v4), ('C', av_c)):
        for clase, ids in (('estafas', an.ESTAFAS), ('legítimas (FA)', an.LEGITIMAS)):
            filas_md.append([nombre, clase, *[sum(1 for i in ids if av[i] is not None and a <= av[i] <= b) for a, b in tramos],
                             sum(av[i] is not None for i in ids)])
    tabla(filas_md, ['prompt', 'avisos a', *[f'L{a}–{b}' if b < 99 else f'L{a}+' for a, b in tramos], 'total'])
    print('### Estafas sin aviso o con aviso después del pedido\n')
    filas_md = []
    for i in an.ESTAFAS:
        if momento(i, av_c[i]) in ('–', 'después'):
            maximo = max(num(r['riesgo']) for r in c[i])
            t_r = REF[i].get('t_r_linea')
            en_tr = num(c[i][t_r - 1]['riesgo']) if t_r else None
            filas_md.append([i.removeprefix('CV2-D-V-'), REF[i].get('pedido') or 'sin pedido', t_r or '–', len(c[i]),
                             f"L{av_c[i]}" if av_c[i] else '–', f'{maximo:g}', '–' if en_tr is None else f'{en_tr:g}',
                             f"L{av_v4[i]}" if av_v4[i] else '–'])
    tabla(filas_md, ['estafa', 'pedido', 'T_R', 'líneas', 'C avisa', 'riesgo máx. de C', 'riesgo de C en T_R', 'v4 avisa'])

    print('### Las FA de C, con la última línea de OTRA hasta el aviso\n')
    filas_md = []
    for i in an.LEGITIMAS:
        if av_c[i] is None:
            continue
        r = c[i][av_c[i] - 1]
        n_otra, texto = ultima_de_otra(i, av_c[i])
        filas_md.append([i, LOTE.get(i, '?').split(' ')[0], f"L{av_c[i]}/{len(c[i])}", f"{num(r['riesgo']):g}",
                         'sí' if r['alerta_escrita'] == 'true' else 'no', f"L{av_v4[i]}" if av_v4[i] else '–',
                         eventos_hasta(i, av_c[i]), f'L{n_otra}: {recorte(texto)}'])
    tabla(filas_md, ['legítima', 'lote', 'aviso / líneas', 'riesgo', 'alerta escrita', 'v4', 'eventos hasta el aviso',
                     'última línea de OTRA'])

    print('### Las FA que C saca y v4 tiene (muestra de las primeras 12), con la línea que dispara a v4\n')
    filas_md = []
    for i in [i for i in an.LEGITIMAS if av_v4[i] is not None and av_c[i] is None][:12]:
        n_otra, texto = ultima_de_otra(i, av_v4[i])
        filas_md.append([i, f"L{av_v4[i]}", eventos_hasta(i, av_v4[i]),
                         f"{max(num(r['riesgo']) for r in c[i]):g}", f'L{n_otra}: {recorte(texto)}'])
    tabla(filas_md, ['legítima', 'v4 avisa', 'eventos hasta el aviso', 'riesgo máx. de C', 'última línea de OTRA'])

    print('### Los casos en que la repetición de C avisa en otra línea\n')
    filas_md = []
    for i in an.VISTA:
        if av_c[i] != av_c_rep[i]:
            filas_md.append([i, REF[i]['clase'], REF[i].get('t_r_linea') or '–', f"L{av_c[i]}" if av_c[i] else '–',
                             f"L{av_c_rep[i]}" if av_c_rep[i] else '–'])
    tabla(filas_md, ['caso', 'clase', 'T_R', 'C', 'C (repetición)'])

    # 5. Segunda consulta
    print('## 5. La segunda consulta (motivo) con la regla de C\n')
    print('En Colab la segunda consulta se pidió con la regla de la corrida («riesgo ≥ 0,4 o alerta», `UMBRAL_CORTE`), '
          f'no con «{regla_c}».\n')
    con_motivo = {i: next((int(r['linea']) for r in c[i] if r['ms_etapa2']), None) for i in an.VISTA}
    avisa_c = [i for i in an.VISTA if av_c[i] is not None]
    misma = [i for i in avisa_c if con_motivo[i] == av_c[i]]
    print(f'- C avisa en {len(avisa_c)} llamadas de la vista; la segunda consulta corrió en la línea de ese aviso en '
          f'{len(misma)}, y en {sum(1 for i in avisa_c if con_motivo[i] is None)} no corrió nunca (el riesgo no llegó a 0,4 '
          'ni hubo alerta escrita).')
    solo_riesgo = [i for i in avisa_c if c[i][av_c[i] - 1]['alerta_escrita'] != 'true']
    print(f'- En {len(solo_riesgo)} de esos {len(avisa_c)} avisos el modelo no escribió alerta: avisa solo el riesgo. '
          'Con v4, en la corrida del JSON cortado, 19 de 78 avisos eran solo por riesgo, y ahí estaban los 4 fallos de '
          'la segunda consulta.')
    antes = [i for i in avisa_c if REF[i]['clase'] == 'vishing' and momento(i, av_c[i]) in ('antes', 'avisa')]
    print(f'- {len(antes)} avisos de C a estafas llegan antes del pedido o en llamadas sin pedido. `motivo_v4_corte.txt` '
          'pide «lo que le están pidiendo»: en esas líneas todavía no hay pedido.\n')
    print('Motivos que escribió la segunda consulta en las estafas de la vista, cuando corrió antes del pedido o sin '
          'pedido (primeros 8):\n')
    filas_md = []
    for i in an.ESTAFAS:
        n = con_motivo[i]
        if n is None or momento(i, n) not in ('antes', 'avisa'):
            continue
        r = c[i][n - 1]
        filas_md.append([i.removeprefix('CV2-D-V-'), f"L{n}", REF[i].get('t_r_linea') or '–', recorte(r['motivo'], 90),
                         r['evidencia_en_texto']])
    tabla(filas_md[:8], ['estafa', 'línea', 'T_R', 'motivo', 'evidencia en el texto'])

    # 6. Exploración
    print('## 6. Exploración: riesgo sostenido en líneas seguidas (no decide; genera hipótesis)\n')
    print('Avisa con alerta escrita, o con riesgo ≥ u en k líneas seguidas. Elegir u y k mirando esta tabla sería '
          'ajustar sobre desarrollo: si se quiere usar, se escribe antes y se prueba en otros casos.\n')
    filas_md = []
    for carpeta in ('v4-corte', 'c-json-corte', 'c-json-corte-rep'):
        for u in (0.3, 0.4):
            for k in (1, 2, 3):
                m = an.metricas(sostenido(filas[carpeta], u, k, an.VISTA), an.VISTA)
                filas_md.append([carpeta, f'{u:g}', k, *an.fmt(m)])
    tabla(filas_md, ['corrida', 'u', 'k', *an.ENC])

    print('### Techo de sumarle a C un detector literal de pedidos críticos (la referencia hace de oráculo)\n')
    print('Pedido crítico: el primer evento `pedido` de la referencia con código, clave, plata, acceso remoto o acción de '
          'seguridad; los datos personales no cuentan. Es un techo: supone un detector que nunca falla, y las marcas de '
          'la referencia no tienen revisión humana.\n')
    oraculo = {i: min((e['linea'] for e in REF[i].get('evidencia') or []
                       if e['evento'] == 'pedido' and CRITICOS & set(e['etiquetas'])), default=None) for i in an.VISTA}
    juntar = lambda a, b: {i: min((x for x in (a[i], b[i]) if x is not None), default=None) for i in an.VISTA}  # noqa: E731
    filas_md = [[nombre, *an.fmt(an.metricas(av, an.VISTA))] for nombre, av in (
        (f'v4 «{REGLA_V4}»', av_v4), (f'C «{regla_c}»', av_c), ('pedido crítico (oráculo) solo', oraculo),
        (f'C «{regla_c}» o pedido crítico (oráculo)', juntar(av_c, oraculo)))]
    tabla(filas_md, ['regla', *an.ENC])
    print('Legítimas con un pedido crítico en la referencia: ' +
          (', '.join(i for i in an.LEGITIMAS if oraculo[i]) or 'ninguna') + '.\n')

    # 7. Controles
    print('## 7. Controles de ventas, línea por línea\n')
    (run,) = [p for p in (AQUI / 'controles-ventas').glob('*') if (p / 'manifiesto.json').exists()]
    por = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as fh:
        for r in csv.DictReader(fh):
            if r['detector'] == 'slm':
                por[r['prompt']][r['case_id']].append(r)
    definicion = json.loads((an.EXP / 'casos' / 'controles-ventas.json').read_text(encoding='utf-8'))
    filas_md = []
    for i, d in definicion.items():
        for prompt in PROMPTS:
            fc = sorted(por[prompt][i], key=lambda r: int(r['linea']))
            riesgos = ' '.join(f"{num(r['riesgo']):g}" + ('!' if r['alerta_escrita'] == 'true' else '') for r in fc)
            filas_md.append([i, d['clase'], PROMPTS[prompt], riesgos])
    tabla(filas_md, ['control', 'clase', 'prompt', 'riesgo escrito por línea (! = alerta escrita)'])


if __name__ == '__main__':
    main()
