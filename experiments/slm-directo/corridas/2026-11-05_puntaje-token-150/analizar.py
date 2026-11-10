"""#143: P(SÍ) del primer token en los 150 de desarrollo. Políticas de aviso, compuerta de Tito simulada y curva.

No corre modelos ni lee la reserva; solo biblioteca estándar. Uso, desde esta carpeta:
    python -I analizar.py                     # todo: líneas base, corridas nuevas, elección y curva.csv
    python -I analizar.py --solo-referencia   # solo las líneas base JSON (no necesita las corridas nuevas)
    python -I analizar.py --datos OTRA_CARPETA  # corridas nuevas en otra carpeta (pruebas)

Definiciones (docs/evaluacion/METRICAS.md y #143):
- Se decide sobre corpus_v2 (46 estafas, 36 con pedido, 51 legítimas). Laboratorio, piloto y trampa van aparte.
- Línea de aviso T_A: la primera línea en que la política dispara. «Antes del pedido»: T_A < t_r_linea.
- L_R = t_r_linea − T_A, en líneas (positivo: avisa antes del pedido).
- Compuerta de Tito simulada: Tito viejo sin indicio (umbral 0,5) se engancha en su primera activación y
  desde ahí el SLM se consulta en todas las líneas; sin indicio, el mensaje al SLM es el mismo que en el
  SLM solo. Las activaciones salen de la corrida de v4 con Tito viejo en modo diagnóstico completo.

Decisiones de Mateo del 2026-11-06, antes de ver las corridas nuevas (no están en #143):
- Se elige sobre el SLM solo. Tito→SLM se informa aparte en la misma curva, con su costo, sin usarlo para
  elegir ni como línea base.
- EMA con α = 0,5 fijo en la regla. α = 0,3 y 0,7 se calculan como exploración, fuera de la regla: si alguno
  le gana a 0,5 por 3 o más estafas (con FA ≤ 7) en la corrida y en su repetición, queda anotado como
  candidato para validar en la reserva; si no, α no importa tanto.
- Línea base de la regla de adopción: el mejor punto JSON con FA ≤ 7 de las corridas SLM solo (alerta o
  «riesgo ≥ u o alerta»). La comparación contra `alerta_sugerida` sola se informa como dato.
- Se elige sobre la primera corrida y la repetición se informa en el mismo punto. Umbral en una grilla;
  entre umbrales empatados de la misma política: menos FA y, después, el del medio del rango.
"""
import argparse, collections, csv, io, json, math, statistics, sys
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
C = EXP / 'corridas'

# --- Regla de elección de #143, escrita antes de mirar resultados ---
FA_MAX = 7          # X = 15 % de 51 legítimas de corpus_v2
MARGEN = 3          # adopción: 3 o más estafas más que la línea base; dentro de ±2, decide la latencia
# Grilla de 0,01, más valores cerca de 0 y de 1, donde se amontona P(SÍ) a temperatura 0.
UMBRALES = sorted({round(x / 100, 2) for x in range(1, 100)}
                  | {0.0001, 0.0005, 0.001, 0.002, 0.005, 0.995, 0.998, 0.999, 0.9995, 0.9999})
POLITICAS = ['umbral', 'dos seguidas', 'EMA α=0.5']  # entran en la regla; el orden es el de simpleza
EXPLORACION = ['EMA α=0.3', 'EMA α=0.7']             # se calculan y se muestran, fuera de la regla
COMPUERTAS = ['SLM solo', 'Tito→SLM']                # se elige sobre SLM solo; Tito→SLM se informa aparte
TODAS = POLITICAS + EXPLORACION


# --- Líneas base JSON (ya corridas) ---
def uno(patron):
    (p,) = C.glob(patron)
    return p


BASES = {  # nombre: (carpeta de la corrida, detector, prompt). Comparador: las de detector `slm`, sin repetición.
    'v1 solo (2026-11-04, a)': ('2026-11-04_sin-indicio-150/a/2026*', 'slm', 'v1'),
    'v1 + Tito sin indicio (2026-11-04, b)': ('2026-11-04_sin-indicio-150/b/2026*', 'tito-slm-sin-indicio', 'v1'),
    'v1 solo, repetición (2026-11-04, c)': ('2026-11-04_sin-indicio-150/c/2026*', 'slm', 'v1'),
    'v4 solo (2026-11-05, b)': ('2026-11-05_tito-2-v4/b/2026*', 'slm', 'v4'),
    'v4 + Tito sin indicio (tanda de roles, d)': ('2026-11-04_tanda-roles-tito-sin-indicio/d/2026*', 'tito-slm-sin-indicio', 'v4'),
}
# Tabla de referencia que el script tiene que reproducir antes de seguir (estafas, antes del pedido, falsas alarmas).
REFERENCIA = {'v1 solo (2026-11-04, a)': (28, 13, 4), 'v1 + Tito sin indicio (2026-11-04, b)': (27, 12, 4),
              'v4 solo (2026-11-05, b)': (28, 9, 6)}
CORRIDA_TITO = 'v4 + Tito sin indicio (tanda de roles, d)'  # modo diagnóstico completo: activaciones de Tito

# --- Corridas nuevas (probar_puntaje_token.py, tag colab/143-150) ---
NUEVAS = {  # nombre: (carpeta, prompt, línea base JSON con la que se compara)
    'A1 v4': ('v4-a1', 'v4-a1', 'v4'),
    'A1 v4, repetición': ('v4-a1-rep', 'v4-a1', 'v4'),
    'A2 v4': ('v4-a2', 'v4-a2', 'v4'),
    'A2 v4, repetición': ('v4-a2-rep', 'v4-a2', 'v4'),
    'A1 tarea': ('tarea-a1', 'tarea-a1', 'v1'),
    'A1 tarea, repetición': ('tarea-a1-rep', 'tarea-a1', 'v1'),
}
COMMIT_150 = '8f6c0a460aa780e0d289ced2f9b03601f6949247'
DIGEST = 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2'

REF = {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in (EXP / 'casos/referencia').glob('*.json')}


def leer_corrida(run, detector):
    filas = collections.defaultdict(list)
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if r['detector'] == detector:
                filas[r['case_id']].append(r)
    for v in filas.values():
        v.sort(key=lambda r: int(r['linea']))
    return dict(filas), json.loads((run / 'manifiesto.json').read_text(encoding='utf-8'))


def num(x):
    return float(x) if x not in ('', None) else None


# --- Métricas ---
def metricas(avisos, ids):
    """avisos: case_id → línea de aviso o None. Cuenta sobre `ids` (un grupo)."""
    est = [i for i in ids if REF[i]['clase'] == 'vishing']
    leg = [i for i in ids if REF[i]['clase'] != 'vishing']
    conp = [i for i in est if REF[i].get('t_r_linea') and avisos.get(i) is not None]
    lr = sorted(REF[i]['t_r_linea'] - avisos[i] for i in conp)
    fa_tipo = collections.Counter(REF[i].get('tipo_legitima') or REF[i]['clase'] for i in leg if avisos.get(i) is not None)
    return {
        'det': sum(avisos.get(i) is not None for i in est), 'n_est': len(est),
        'fa': sum(avisos.get(i) is not None for i in leg), 'n_leg': len(leg), 'fa_tipo': dict(fa_tipo),
        'antes': sum(x > 0 for x in lr), 'en': sum(x == 0 for x in lr), 'despues': sum(x < 0 for x in lr),
        'n_conp': sum(1 for i in est if REF[i].get('t_r_linea')),
        'lr_mediana': statistics.median(lr) if lr else None, 'lr_media': statistics.fmean(lr) if lr else None,
        'lr_3': sum(x >= 3 for x in lr),
    }


def grupo(ids, g):
    return [i for i in ids if REF[i]['grupo'] == g]


# --- Políticas sobre p_si ---
def puntajes(p, politica):
    """p: lista de P(SÍ) por línea (None = SLM no consultado o lectura inválida) → puntaje por línea."""
    if politica == 'umbral':
        return list(p)
    if politica == 'dos seguidas':  # dispara en la segunda de dos líneas seguidas sobre el umbral
        return [None] + [min(a, b) if a is not None and b is not None else None for a, b in zip(p, p[1:])]
    alfa = float(politica.split('=')[1])
    s, salida = 0.0, []  # el puntaje acumulado arranca en 0 en la primera línea consultada
    for x in p:
        if x is None:
            salida.append(None if s == 0.0 else s)
        else:
            s = alfa * x + (1 - alfa) * s
            salida.append(s)
    return salida


def primer_aviso(q, u):
    return next((n for n, x in enumerate(q, 1) if x is not None and x >= u), None)


def serie(filas, activacion):
    """P(SÍ) por línea; con compuerta, None antes de la activación de Tito (o en toda la llamada si no activa)."""
    p = [num(r['p_si']) if r['valida'].lower() == 'true' else None for r in filas]
    if activacion is not False:  # False = sin compuerta
        p = [None if activacion is None or n < activacion else x for n, x in enumerate(p, 1)]
    return p


def tabla(filas_md, encabezado):
    print('| ' + ' | '.join(encabezado) + ' |')
    print('|' + '---|' * len(encabezado))
    for f in filas_md:
        print('| ' + ' | '.join(str(x) for x in f) + ' |')
    print()


def fmt(m):
    lr = '–' if m['lr_mediana'] is None else f"{m['lr_mediana']:g} / {m['lr_media']:.1f} / {m['lr_3']}"
    tipos = ', '.join(f'{k} {v}' for k, v in sorted(m['fa_tipo'].items())) or '–'
    return [f"{m['det']}/{m['n_est']}", f"{m['antes']}/{m['en']}/{m['despues']} (de {m['n_conp']})", lr,
            f"{m['fa']}/{m['n_leg']}", tipos]


ENC = ['estafas', 'antes/en/después de T_R', 'L_R mediana / media / ≥ 3', 'falsas alarmas', 'FA por tipo']


# =============================================================================================
def lineas_base():
    """Reproduce la tabla de referencia y arma los puntos JSON con el mismo formato."""
    print('## Líneas base JSON\n')
    datos = {}
    for nombre, (patron, det, _) in BASES.items():
        filas, man = leer_corrida(uno(patron), det)
        assert len(filas) == 150 and man['particion'] == 'desarrollo' and not [i for i in filas if 'CV2-T' in i], nombre
        assert man['ollama']['version'] == '0.40.14' and man['ollama']['digests']['gemma4:e2b-it-q4_K_M'].startswith(DIGEST[:12]), nombre
        datos[nombre] = filas
    ids = sorted(datos[CORRIDA_TITO])
    v2 = grupo(ids, 'corpus_v2')

    print('Primer aviso (`alerta_sugerida`), como corrieron. Tiene que reproducir la tabla de referencia de #143.\n')
    filas_md, puntos = [], {}
    for nombre, filas in datos.items():
        av = {i: next((int(r['linea']) for r in filas[i] if r['aviso'].lower() == 'true'), None) for i in ids}
        m = metricas(av, v2)
        if nombre in REFERENCIA:
            assert (m['det'], m['antes'], m['fa']) == REFERENCIA[nombre], (nombre, m)
        filas_md.append([nombre, *fmt(m)])
        puntos[(nombre, 'alerta_sugerida')] = m
    tabla(filas_md, ['corpus_v2', *ENC])
    print('La tabla de referencia se reproduce: v1 solo 28/13/4, v1 + Tito 27/12/4, v4 solo 28/9/6.\n')

    print('Umbral sobre el riesgo escrito: avisa en la primera línea con riesgo ≥ u o `alerta_sugerida`. Las corridas '
          'operativas cortan en el aviso, así que esta regla está observada entera.\n')
    filas_md = []
    for nombre, filas in datos.items():
        for u in (0.3, 0.4, 0.5):
            av = {i: next((int(r['linea']) for r in filas[i]
                           if (num(r['riesgo']) is not None and num(r['riesgo']) >= u - 1e-9) or r['alerta_sugerida'] == 'true'), None)
                  for i in ids}
            m = metricas(av, v2)
            puntos[(nombre, f'riesgo ≥ {u} o alerta')] = m
            filas_md.append([nombre, f'≥ {u}', *fmt(m)])
    tabla(filas_md, ['corpus_v2', 'riesgo', *ENC])

    print(f'Línea base de la regla de adopción: mejor punto JSON del SLM solo con falsas alarmas ≤ {FA_MAX}/51 en '
          'corpus_v2, por prompt. Como dato, también `alerta_sugerida` sola:\n')
    mejores = {}
    for prompt in ('v1', 'v4'):
        candidatos = [(k, m) for k, m in puntos.items() if BASES[k[0]][2] == prompt and BASES[k[0]][1] == 'slm'
                      and m['fa'] <= FA_MAX and 'repetición' not in k[0]]
        k, m = max(candidatos, key=lambda km: (km[1]['det'], km[1]['antes'], -km[1]['fa']))
        (ka, ma), = [(k2, m2) for k2, m2 in puntos.items() if BASES[k2[0]][2] == prompt and BASES[k2[0]][1] == 'slm'
                     and 'repetición' not in k2[0] and k2[1] == 'alerta_sugerida']
        mejores[prompt] = ((k, m), (ka, ma))
        print(f'- {prompt}: {k[0]}, {k[1]}: {m["det"]}/46 estafas, {m["antes"]} antes del pedido, {m["fa"]}/51 FA '
              f'(`alerta_sugerida` sola: {ma["det"]}/46, {ma["antes"]} antes, {ma["fa"]}/51).')
    print()

    activacion = {i: next((int(r['linea']) for r in datos[CORRIDA_TITO][i] if r['consulta'] != 'omitida'), None) for i in ids}
    otra = {i: next((int(r['linea']) for r in datos['v1 + Tito sin indicio (2026-11-04, b)'][i] if r['consulta'] != 'omitida'), None)
            for i in ids}
    assert activacion == otra, 'las activaciones de Tito difieren entre corridas: revisar'
    tito_ms = [num(r['tito_ms']) for i in ids for r in datos[CORRIDA_TITO][i] if r['consulta'] == 'omitida' and num(r['tito_ms'])]
    print(f'Activaciones de Tito viejo sin indicio: {sum(a is not None for a in activacion.values())} de 150 casos '
          f'(iguales con v1 y v4); Tito por línea antes de activar: mediana {statistics.median(tito_ms):.0f} ms.\n')
    return ids, activacion, mejores


# =============================================================================================
def controlar(nombre, filas, man, prompt):
    sys.path.insert(0, str(EXP))
    from detectores import cargar_prompt  # solo para comparar el texto del prompt
    ids = sorted(filas)
    assert len(ids) == 150 and man['particion'] == 'desarrollo' and not [i for i in ids if 'CV2-T' in i], nombre
    assert man['ollama']['version'] == '0.40.14' and man['ollama']['digests']['gemma4:e2b-it-q4_K_M'].startswith(DIGEST[:12]), nombre
    assert man['prompts'][prompt]['texto'] == cargar_prompt(prompt), f'{nombre}: el prompt de la corrida no es el registrado'
    assert man['modo_termino'] == 'diagnostico-completo' and not man['interrumpida'], nombre
    assert man['parametros_slm']['num_ctx'] == 4096 and man['parametros_slm']['seed'] == 42, nombre
    if man['codigo']['commit'] != COMMIT_150:
        print(f'> Aviso: {nombre} corrió en el commit {man["codigo"]["commit"]}, no en {COMMIT_150} (colab/143-150).\n')
    sys.path.insert(0, str(EXP))
    import casos
    for i in ids:
        assert [int(r['linea']) for r in filas[i]] == list(range(1, len(casos.cargar_texto(i)) + 1)), (nombre, i)
    todas = [r for i in ids for r in filas[i]]
    masas = [num(r['masa_si_no']) for r in todas if num(r['masa_si_no']) is not None]
    invalidas = sum(r['valida'].lower() != 'true' for r in todas)
    ms = sorted(num(r['ms']) for r in todas if num(r['ms']) is not None)
    return {'lineas': len(todas), 'invalidas': invalidas, 'masa_min': min(masas) if masas else None,
            'masa_baja': sum(m < 0.9 for m in masas), 'ms_p50': statistics.median(ms),
            'ms_p95': ms[min(len(ms) - 1, math.ceil(0.95 * len(ms)) - 1)]}


def barrer(filas, ids, activacion):
    """Curva completa sobre corpus_v2: compuerta × política × umbral."""
    v2 = grupo(ids, 'corpus_v2')
    curva = []
    for compuerta in COMPUERTAS:
        for politica in TODAS:
            q = {i: puntajes(serie(filas[i], False if compuerta == 'SLM solo' else activacion[i]), politica) for i in ids}
            for u in UMBRALES:
                av = {i: primer_aviso(q[i], u) for i in ids}
                curva.append({'compuerta': compuerta, 'politica': politica, 'u': u, 'av': av, **metricas(av, v2)})
    return curva


def elegir(curva, compuerta='SLM solo', politicas=POLITICAS):
    """Regla de #143: máx. estafas con FA ≤ FA_MAX; desempates: más avisos antes de T_R, política más simple.
    Dentro de una misma política, entre umbrales empatados: menos FA y, entre esos, el umbral del medio."""
    ok = [c for c in curva if c['fa'] <= FA_MAX and c['compuerta'] == compuerta and c['politica'] in politicas]
    if not ok:
        return None
    mejor = max(ok, key=lambda c: (c['det'], c['antes'], -TODAS.index(c['politica'])))
    empatados = [c for c in ok if (c['politica'], c['det'], c['antes']) == (mejor['politica'], mejor['det'], mejor['antes'])]
    fa_min = min(c['fa'] for c in empatados)
    empatados = sorted((c for c in empatados if c['fa'] == fa_min), key=lambda c: c['u'])
    return {**empatados[len(empatados) // 2], 'rango_u': (empatados[0]['u'], empatados[-1]['u'])}


def en_punto(curva, punto):
    return next(c for c in curva if (c['compuerta'], c['politica'], c['u']) == (punto['compuerta'], punto['politica'], punto['u']))


def mejor_por_politica(curva):
    salida = []
    for compuerta in COMPUERTAS:
        for politica in TODAS:
            papel = ('informativo' if compuerta != 'SLM solo' else 'regla' if politica in POLITICAS else 'exploración')
            salida.append((compuerta, politica, papel, elegir(curva, compuerta, [politica])))
    return salida


def costo(filas, ids, punto, activacion):
    """Consultas al SLM hasta el aviso (en operación el SLM deja de consultarse al avisar)."""
    consultas = []
    for i in ids:
        n = len(filas[i])
        fin = punto['av'][i] or n
        desde = 1 if punto['compuerta'] == 'SLM solo' else (activacion[i] or n + 1)
        consultas.append(max(0, fin - desde + 1))
    return sum(consultas), statistics.median(consultas)


def nuevas(datos_dir, ids, activacion, mejores):
    print('## Corridas nuevas: P(SÍ) del primer token\n')
    filas_md, curvas, filas_por = [], {}, {}
    for nombre, (carpeta, prompt, _) in NUEVAS.items():
        runs = [p for p in (datos_dir / carpeta).glob('*') if (p / 'manifiesto.json').exists()]
        if not runs:
            print(f'> Falta {carpeta}/: se omite «{nombre}».\n')
            continue
        (run,) = runs
        filas, man = leer_corrida(run, 'slm')
        assert sorted(filas) == ids, nombre
        k = controlar(nombre, filas, man, prompt)
        filas_md.append([nombre, k['lineas'], k['invalidas'], f"{k['masa_min']:.4f}", k['masa_baja'], f"{k['ms_p50']:.0f} / {k['ms_p95']:.0f}"])
        curvas[nombre], filas_por[nombre] = barrer(filas, ids, activacion), filas
    print('Control de la lectura (criterio de la humo: masa SÍ+NO ≥ 0,9 en casi todas las líneas):\n')
    tabla(filas_md, ['corrida', 'líneas', 'inválidas', 'masa mínima', 'líneas con masa < 0,9', 'ms SLM p50 / p95'])
    if not curvas:
        return

    with open(datos_dir / 'curva.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['corrida', 'compuerta', 'politica', 'umbral', 'estafas', 'antes', 'en', 'despues', 'lr_mediana',
                    'lr_media', 'lr_ge3', 'fa', 'fa_cotidiana', 'fa_pedido_razonable', 'fa_mencion_sin_pedido'])
        for nombre, curva in curvas.items():
            for c in curva:
                w.writerow([nombre, c['compuerta'], c['politica'], c['u'], c['det'], c['antes'], c['en'], c['despues'],
                            c['lr_mediana'], '' if c['lr_media'] is None else round(c['lr_media'], 3), c['lr_3'], c['fa'],
                            *(c['fa_tipo'].get(t, 0) for t in ('cotidiana', 'pedido_razonable', 'mencion_sin_pedido'))])
    print(f'Curva completa en `curva.csv` ({sum(len(c) for c in curvas.values())} filas: corrida × compuerta × política × umbral).\n')

    print(f'### Mejor punto por política con FA ≤ {FA_MAX}/51 en corpus_v2\n')
    filas_md = []
    for nombre, curva in curvas.items():
        for compuerta, politica, papel, e in mejor_por_politica(curva):
            filas_md.append([nombre, compuerta, politica, papel] + (['ninguno'] * 6 if e is None else
                            [f"{e['u']:g} ({e['rango_u'][0]:g}–{e['rango_u'][1]:g})", *fmt(e)]))
    tabla(filas_md, ['corrida', 'compuerta', 'política', 'papel', 'umbral (rango empatado)', *ENC])

    print('### Punto elegido y regla de adopción\n')
    elegidos = {}
    for nombre, curva in curvas.items():
        if 'repetición' in nombre:
            continue
        e = elegir(curva)
        elegidos[nombre] = e
        prompt_base = NUEVAS[nombre][2]
        (kb, mb), (ka, ma) = mejores[prompt_base]
        rep = f'{nombre}, repetición'
        if e is None:
            print(f'- **{nombre}:** ningún punto del SLM solo con FA ≤ {FA_MAX}/51.')
            continue
        linea = (f'- **{nombre}:** {e["compuerta"]}, {e["politica"]}, umbral {e["u"]:g} (empata entre {e["rango_u"][0]:g} y '
                 f'{e["rango_u"][1]:g}): {e["det"]}/46 estafas, {e["antes"]} antes del pedido, {e["fa"]}/51 FA.')
        if rep in curvas:
            r = en_punto(curvas[rep], e)
            linea += f' Repetición en el mismo punto: {r["det"]}/46, {r["antes"]} antes, {r["fa"]}/51 FA.'
        print(linea)
        dif = e['det'] - mb['det']
        veredicto = ('se adopta (3 o más estafas más)' if dif >= MARGEN else
                     'no se adopta (3 o más estafas menos)' if dif <= -MARGEN else 'dentro de ±2: decide la latencia (#141)')
        if 'A1' in nombre:
            print(f'  Contra la línea base JSON {prompt_base} ({kb[0]}, {kb[1]}: {mb["det"]}/46, {mb["fa"]}/51): '
                  f'{dif:+d} estafas → {veredicto}. Como dato, contra `alerta_sugerida` sola ({ma["det"]}/46, '
                  f'{ma["fa"]}/51): {e["det"] - ma["det"]:+d}.')
    print()

    if elegidos.get('A1 v4') and elegidos.get('A2 v4'):
        a1, a2 = elegidos['A1 v4'], elegidos['A2 v4']
        tr1 = metricas(a1['av'], grupo(ids, 'trampa'))['fa']
        tr2 = metricas(a2['av'], grupo(ids, 'trampa'))['fa']
        mejor = a2['det'] - a1['det'] >= MARGEN or a2['antes'] - a1['antes'] >= MARGEN
        print(f'**A2 frente a A1 (v4):** {a2["det"] - a1["det"]:+d} estafas, {a2["antes"] - a1["antes"]:+d} avisos antes del pedido, '
              f'FA en trampa {tr1} → {tr2}. '
              + ('A2 se prefiere según la regla; adoptarlo necesita el visto bueno de D08 (#33).' if mejor and tr2 <= tr1
                 else 'A2 no cumple la regla para preferirse.') + '\n')

    print('### Manuales en el punto elegido (aparte de la decisión)\n')
    filas_md = []
    for nombre, e in elegidos.items():
        if e is None:
            continue
        for g in ('laboratorio', 'piloto_escrito', 'trampa'):
            filas_md.append([nombre, g, *fmt(metricas(e['av'], grupo(ids, g)))])
    tabla(filas_md, ['corrida', 'grupo', *ENC])

    print('### Tito→SLM, aparte (no se usa para elegir), y costo\n')
    print('Mismo procedimiento de elección, restringido a Tito→SLM. Las consultas al SLM se cuentan hasta el aviso; '
          'con Tito, desde su activación (antes de activar corre solo Tito).\n')
    filas_md = []
    for nombre, e in elegidos.items():
        if e is None:
            continue
        ms = statistics.median(num(r['ms']) for i in ids for r in filas_por[nombre][i] if num(r['ms']) is not None)
        t = elegir(curvas[nombre], 'Tito→SLM')
        for punto in (e, t):
            if punto is None:
                filas_md.append([nombre, 'Tito→SLM', 'ninguno con FA ≤ 7', '', '', '', '', '', '', ''])
                continue
            total, mediana = costo(filas_por[nombre], ids, punto, activacion)
            filas_md.append([nombre, punto['compuerta'], f"{punto['politica']}, {punto['u']:g}", *fmt(punto)[:4],
                             f'{ms:.0f}', total, f'{mediana:g}'])
    tabla(filas_md, ['corrida', 'compuerta', 'política, umbral', *ENC[:4], 'ms SLM por línea (p50)',
                     'consultas al SLM hasta el aviso (150 casos)', 'por caso (mediana)'])

    print('### Exploración: α de la EMA (fuera de la regla)\n')
    print('Mejor punto del SLM solo con FA ≤ 7 para cada α. Un α queda como candidato para validar en la reserva solo '
          'si le gana a α = 0,5 por 3 o más estafas en la corrida y también en su repetición.\n')
    filas_md = []
    for nombre in elegidos:
        rep_ = f'{nombre}, repetición'
        res = {}
        for corrida in (nombre, rep_):
            if corrida not in curvas:
                continue
            for pol in ('EMA α=0.5', *EXPLORACION):
                p = elegir(curvas[corrida], 'SLM solo', [pol])
                res[(corrida, pol)] = p['det'] if p else None
        for pol in EXPLORACION:
            difs = [res.get((c, pol)) - res.get((c, 'EMA α=0.5')) for c in (nombre, rep_)
                    if res.get((c, pol)) is not None and res.get((c, 'EMA α=0.5')) is not None]
            candidato = len(difs) == 2 and all(d >= MARGEN for d in difs)
            filas_md.append([nombre, pol, res.get((nombre, 'EMA α=0.5')), res.get((nombre, pol)),
                             res.get((rep_, 'EMA α=0.5'), '–'), res.get((rep_, pol), '–'),
                             'candidato para la reserva' if candidato else 'no'])
    tabla(filas_md, ['corrida', 'α', 'estafas con α=0,5', 'estafas con este α', 'repetición α=0,5', 'repetición este α', '¿candidato?'])


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--solo-referencia', action='store_true')
    p.add_argument('--datos', type=Path, default=AQUI)
    args = p.parse_args()
    print('# #143: puntaje por P(SÍ) — análisis offline\n')
    ids, activacion, mejores = lineas_base()
    if not args.solo_referencia:
        nuevas(args.datos.resolve(), ids, activacion, mejores)


if __name__ == '__main__':
    main()
