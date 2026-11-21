"""#143, segunda vuelta: alcance (llamadas entrantes de números no agendados), prompt C, v4-L y token al final.

No corre modelos ni lee la reserva; solo biblioteca estándar. Reusa las funciones de la primera vuelta
(../2026-11-05_puntaje-token-150/analizar.py) y reproduce sus líneas base antes de seguir. Uso, desde esta carpeta:
    python -I analizar.py                       # todo
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Decisiones escritas el 2026-11-06, antes de correr:
- Alcance (decisión del equipo): el detector corre solo en llamadas entrantes de números no agendados. Cada caso de
  desarrollo tiene `alcance` en casos/alcance-desarrollo.json, anotado a ciegas (sin clase ni resultados) con la regla
  escrita en ese archivo. En corpus_v2 las 46 estafas son entrantes y 44 de las 51 legítimas las inicia la persona:
  dentro del alcance quedan 7 legítimas (familiares y compañeros). Evaristo genera legítimas entrantes de números
  desconocidos (ventas, banco que avisa, correo, turnos, encuestas). Por eso la vuelta va en dos etapas:
  - Etapa 1 (este script, ya): v4-L contra v4 JSON sobre los 150, con la regla de la primera vuelta (FA ≤ 7/51). Es la
    prueba de la forma de leer: el mismo prompt y los mismos casos, así que el sesgo del corpus afecta a las dos por
    igual. La vista dentro del alcance se informa como dato.
  - Etapa 2 (cuando estén las legítimas nuevas; el código se agrega antes de correrlas): vista principal dentro del
    alcance = las 46 estafas de corpus_v2 + las legítimas nuevas de desarrollo, con FA ≤ 15 % de esas legítimas.
    Configuraciones: v4 JSON, v4-L, v4-premisa (v4 + la oración del alcance) y el prompt C con el alcance (c-json,
    c-sino, c-digito). Línea base: el mejor JSON entre v4, v4-premisa y c-json. Misma regla de adopción.
- Configuraciones de la etapa 1, con roles: v4-lectura (v4-L) y su repetición. La humo controla además el formato de
  c-sino y c-digito, sin mirar sus resultados.
- Puntaje por línea: P(SÍ) en c-sino; digito_esperado / 9 en c-digito; riesgo_esperado en v4-L (todos entre 0 y 1).
  Mismas políticas (umbral, dos seguidas y EMA α = 0,5), misma grilla y misma elección que en la primera vuelta:
  máximo de estafas con las FA permitidas (15 % de las legítimas de corpus_v2 de la vista, redondeado hacia abajo);
  desempates: más avisos antes de T_R, política más simple, menos FA y umbral del medio. Se elige en la primera corrida
  y la repetición se informa en el mismo punto.
- Línea base: el mejor JSON con roles del SLM solo, entre v4 (2026-11-05, b) y c-json, con las mismas reglas JSON
  (alerta sola, o riesgo ≥ 0,3 / 0,4 / 0,5 o alerta). Gana el de más estafas; si empatan, más avisos antes del pedido y
  después menos FA.
- Regla de #143: con 3 o más estafas que la base, se adopta (provisorio hasta la reserva); con 3 o más menos, no;
  dentro de ±2, decide la latencia (#141). Una configuración de token solo cuenta si su repetición, en el mismo punto,
  tampoco queda 3 o más estafas por debajo de la base (lo que no se repite no cuenta). Si cuenta más de una, se
  informa la de más estafas (después, más avisos antes y menos FA).
- Comparaciones con el mismo prompt, informativas: v4-L contra v4 JSON, y C SÍ/NO y C dígito contra C JSON. En v4-L
  también se informa en cuántas líneas el riesgo escrito coincide con el de la línea base v4.
- Aparte, solo para mirar: las estafas sin pedido de corpus_v2 (el prompt C apunta a ellas), las 6 estafas que piden
  un dato de identificación, las 6 falsas alarmas de v4 por datos en llamadas que inició la persona, los manuales y
  los controles de ventas.
"""
import argparse, csv, importlib.util, json, math, statistics, sys
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
_spec = importlib.util.spec_from_file_location('ronda1', AQUI.parent / '2026-11-05_puntaje-token-150' / 'analizar.py')
r1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(r1)
sys.path.insert(0, str(EXP))
from detectores import cargar_pregunta, cargar_prompt  # noqa: E402

MARGEN = r1.MARGEN
FRACCION_FA = 0.15
REGLAS_JSON = ['alerta_sugerida', 'riesgo ≥ 0.3 o alerta', 'riesgo ≥ 0.4 o alerta', 'riesgo ≥ 0.5 o alerta']
TOKEN = {  # nombre: (carpeta, prompt, JSON con el mismo prompt)
    'v4-L': ('v4-lectura', 'v4-lectura', 'v4 JSON'),
    'v4-L, repetición': ('v4-lectura-rep', 'v4-lectura', 'v4 JSON'),
    'C SÍ/NO': ('c-sino', 'c-sino', 'C JSON'),
    'C SÍ/NO, repetición': ('c-sino-rep', 'c-sino', 'C JSON'),
    'C dígito': ('c-digito', 'c-digito', 'C JSON'),
    'C dígito, repetición': ('c-digito-rep', 'c-digito', 'C JSON'),
}
JSON_NUEVOS = {'C JSON': ('c-json', 'c-json')}
MASA = {'c-sino': 'masa_si_no', 'c-digito': 'masa_digitos', 'v4-lectura': 'masa_digitos'}
ALCANCE = EXP / 'casos' / 'alcance-desarrollo.json'
DATOS_ESTAFAS = ['CV2-D-V-ORGANISMO_PREVISIONAL-001', 'CV2-D-V-ORGANISMO_PREVISIONAL-002', 'CV2-D-V-ORGANISMO_PREVISIONAL-003',
                 'CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-V-PREMIO-001', 'CV2-D-V-PREMIO-003']
DATOS_LEGITIMAS = ['CV2-D-L-BANCO-001', 'CV2-D-L-BANCO-002', 'CV2-D-L-BANCO-004', 'CV2-D-L-BANCO-005', 'CV2-D-L-BANCO-010',
                   'TR-13-turno-medico-pide-dni']


def puntaje(r):
    """P(SÍ), el riesgo esperado de v4-L o el dígito esperado llevado a 0–1. None si la línea no sirve."""
    if r['valida'].lower() != 'true':
        return None
    for columna, escala in (('p_si', 1), ('riesgo_esperado', 1), ('digito_esperado', 9)):
        if r.get(columna):
            return float(r[columna]) / escala
    return None


def serie(filas, activacion):
    p = [puntaje(r) for r in filas]
    if activacion is not False:  # False = sin compuerta
        p = [None if activacion is None or n < activacion else x for n, x in enumerate(p, 1)]
    return p


r1.serie = serie  # las políticas, la curva y la elección de la primera vuelta leen el puntaje con esta función


def aviso_json(filas, regla):
    """Primera línea en que dispara una regla JSON: `alerta_sugerida` o «riesgo ≥ u o alerta»."""
    u = None if regla == 'alerta_sugerida' else float(regla.split('≥ ')[1].split(' ')[0])
    for r in filas:
        riesgo = r1.num(r['riesgo'])
        if r['alerta_sugerida'] == 'true' or (u is not None and riesgo is not None and riesgo >= u - 1e-9):
            return int(r['linea'])
    return None


def una_corrida(datos, carpeta):
    runs = [p for p in (datos / carpeta).glob('*') if (p / 'manifiesto.json').exists()]
    if not runs:
        return None
    (run,) = runs
    return r1.leer_corrida(run, 'slm')


def controlar(nombre, filas, man, prompt, ids):
    assert sorted(filas) == ids and man['particion'] == 'desarrollo' and not [i for i in filas if 'CV2-T' in i], nombre
    assert man['ollama']['version'] == '0.40.14', nombre
    assert man['ollama']['digests']['gemma4:e2b-it-q4_K_M'].removeprefix('sha256:').startswith(r1.DIGEST[:12]), nombre
    assert man['prompts'][prompt]['texto'] == cargar_prompt(prompt), f'{nombre}: el prompt no es el registrado'
    assert man['prompts'][prompt].get('pregunta_final', {}).get('texto') == cargar_pregunta(prompt), f'{nombre}: pregunta final'
    assert man['modo_termino'] == 'diagnostico-completo' and not man['interrumpida'], nombre
    assert man['parametros_slm']['num_ctx'] == 4096 and man['parametros_slm']['seed'] == 42, nombre
    import casos
    for i in ids:
        assert [int(r['linea']) for r in filas[i]] == list(range(1, len(casos.cargar_texto(i)) + 1)), (nombre, i)
        assert all(r['hablantes'] == 'rol' for r in filas[i]), (nombre, i)
    todas = [r for i in ids for r in filas[i]]
    columna = MASA.get(prompt)
    masas = [r1.num(r[columna]) or 0.0 for r in todas] if columna else []
    ms = sorted(r1.num(r['ms']) for r in todas if r1.num(r['ms']) is not None)
    return [nombre, len(todas), sum(r['valida'].lower() != 'true' for r in todas),
            f'{min(masas):.4f}' if masas else '–', sum(m < 0.9 for m in masas) if masas else '–',
            f'{statistics.median(ms):.0f} / {ms[min(len(ms) - 1, math.ceil(0.95 * len(ms)) - 1)]:.0f}',
            man['codigo']['commit'][:10]]


def linea(m):
    return f"{m['det']}/{m['n_est']} estafas, {m['antes']} antes del pedido, {m['fa']}/{m['n_leg']} FA"


def mejor(puntos, fa_max):
    ok = [(k, m) for k, m in puntos.items() if m['fa'] <= fa_max]
    return max(ok, key=lambda km: (km[1]['det'], km[1]['antes'], -km[1]['fa'])) if ok else None


def sin_pedido(av, ids):
    """Estafas de corpus_v2 sin pedido (sin T_R): cuántas avisa."""
    est = [i for i in ids if r1.REF[i]['clase'] == 'vishing' and r1.REF[i]['grupo'] == 'corpus_v2' and not r1.REF[i].get('t_r_linea')]
    return sum(av.get(i) is not None for i in est), len(est)


def vista(titulo, ids_vista, json_filas, tokens, activacion, principal, datos):
    """Línea base JSON, curvas de token y regla de adopción sobre los casos de la vista."""
    v2 = r1.grupo(ids_vista, 'corpus_v2')
    n_leg = sum(r1.REF[i]['clase'] != 'vishing' for i in v2)
    fa_max = math.floor(FRACCION_FA * n_leg + 1e-9)
    print(f'## {titulo}\n')
    print(f'corpus_v2 en esta vista: {len(v2) - n_leg} estafas y {n_leg} legítimas; FA permitidas: {fa_max} (15 %).\n')

    puntos, filas_md = {}, []
    for nombre, filas in json_filas.items():
        for regla in REGLAS_JSON:
            m = r1.metricas({i: aviso_json(filas[i], regla) for i in ids_vista}, v2)
            puntos[(nombre, regla)] = m
            filas_md.append([nombre, regla, *r1.fmt(m)])
    r1.tabla(filas_md, ['JSON', 'regla', *r1.ENC])
    mejores_json = {n: mejor({k: m for k, m in puntos.items() if k[0] == n}, fa_max) for n in json_filas}
    for n, b in mejores_json.items():
        print(f'- {n}: ' + (f'{b[0][1]}: {linea(b[1])}.' if b else f'ninguna regla con FA ≤ {fa_max}.'))
    candidatos = [b for b in mejores_json.values() if b]
    if not candidatos:
        print(f'**Ningún JSON queda con FA ≤ {fa_max}: no hay línea base y no se aplica la regla.**\n')
        return {}, {}, {}
    base_k, base_m = max(candidatos, key=lambda km: (km[1]['det'], km[1]['antes'], -km[1]['fa']))
    print(f'\n**Línea base de la regla de adopción: {base_k[0]}, {base_k[1]} ({linea(base_m)}).**\n')

    r1.FA_MAX = fa_max  # elegir() y mejor_por_politica() leen este valor
    curvas = {n: r1.barrer(f, ids_vista, activacion) for n, f in tokens.items()}
    if principal and curvas:
        with open(datos / 'curva.csv', 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['corrida', 'compuerta', 'politica', 'umbral', 'estafas', 'antes', 'en', 'despues', 'lr_mediana',
                        'lr_media', 'lr_ge3', 'fa'])
            for nombre, curva in curvas.items():
                for c in curva:
                    w.writerow([nombre, c['compuerta'], c['politica'], c['u'], c['det'], c['antes'], c['en'], c['despues'],
                                c['lr_mediana'], '' if c['lr_media'] is None else round(c['lr_media'], 3), c['lr_3'], c['fa']])
        print('Curva completa de esta vista en `curva.csv`.\n')
        print(f'### Mejor punto por política con FA ≤ {fa_max}\n')
        filas_md = []
        for nombre, curva in curvas.items():
            for compuerta, politica, papel, e in r1.mejor_por_politica(curva):
                filas_md.append([nombre, compuerta, politica, papel] + (['ninguno'] * 6 if e is None else
                                [f"{e['u']:g} ({e['rango_u'][0]:g}–{e['rango_u'][1]:g})", *r1.fmt(e)]))
        r1.tabla(filas_md, ['corrida', 'compuerta', 'política', 'papel', 'umbral (rango empatado)', *r1.ENC])

    print('### Punto elegido y regla de adopción\n')
    elegidos, cuentan = {}, []
    for nombre in [n for n in TOKEN if 'repetición' not in n and n in curvas]:
        e = r1.elegir(curvas[nombre])
        elegidos[nombre] = e
        if e is None:
            print(f'- **{nombre}:** ningún punto del SLM solo con FA ≤ {fa_max}.')
            continue
        texto = (f'- **{nombre}:** {e["politica"]}, umbral {e["u"]:g} (empata entre {e["rango_u"][0]:g} y '
                 f'{e["rango_u"][1]:g}): {linea(e)}.')
        rep = f'{nombre}, repetición'
        if rep in curvas:
            texto += f' Repetición en el mismo punto: {linea(r1.en_punto(curvas[rep], e))}.'
        print(texto)
        dif = e['det'] - base_m['det']
        se_repite = rep not in curvas or r1.en_punto(curvas[rep], e)['det'] - base_m['det'] > -MARGEN
        veredicto = ('no se adopta (3 o más estafas menos)' if dif <= -MARGEN else
                     'no cuenta: la repetición queda 3 o más estafas por debajo de la base' if not se_repite else
                     'se adopta, provisorio hasta la reserva (3 o más estafas más)' if dif >= MARGEN else
                     'dentro de ±2: decide la latencia (#141)')
        print(f'  Contra la línea base ({base_k[0]}, {base_k[1]}: {base_m["det"]}/{base_m["n_est"]}): {dif:+d} estafas → {veredicto}.')
        mismo = mejores_json.get(TOKEN[nombre][2])
        if mismo:
            ref = mismo[1]
            print(f'  Con el mismo prompt ({TOKEN[nombre][2]}, {mismo[0][1]}: {ref["det"]}/{ref["n_est"]}, {ref["antes"]} antes, '
                  f'{ref["fa"]}/{ref["n_leg"]}): {e["det"] - ref["det"]:+d} estafas, {e["antes"] - ref["antes"]:+d} avisos antes '
                  'del pedido (dato).')
        if dif > -MARGEN and se_repite:
            cuentan.append((nombre, e))
    print()
    if cuentan:
        nombre, e = max(cuentan, key=lambda ne: (ne[1]['det'], ne[1]['antes'], -ne[1]['fa']))
        print(f'**Entre las de token que cuentan, la de más estafas es {nombre}** ({linea(e)}). Ver la latencia arriba.\n')
    else:
        print('**Ninguna configuración de token cuenta (dentro de ±2 o por encima, con la repetición): no se adopta.**\n')

    reglas = {n: b[0][1] for n, b in mejores_json.items() if b}
    avisos = {f'{n} ({regla})': {i: aviso_json(json_filas[n][i], regla) for i in ids_vista} for n, regla in reglas.items()}
    avisos.update({n: e['av'] for n, e in elegidos.items() if e is not None})
    print('Estafas sin pedido de corpus_v2 (sin T_R) que avisa cada configuración, en su punto: ' +
          '; '.join(f'{n} {sin_pedido(av, ids_vista)[0]}/{sin_pedido(av, ids_vista)[1]}' for n, av in avisos.items()) + '.\n')
    return avisos, reglas, elegidos


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    datos = p.parse_args().datos.resolve()
    print('# #143, segunda vuelta: alcance, prompt C, v4-L y token al final — análisis offline\n')
    ids, activacion, _ = r1.lineas_base()  # reproduce la tabla de la primera vuelta antes de seguir

    anotacion = json.loads(ALCANCE.read_text(encoding='utf-8'))
    alcance = {i: d['alcance'] for i, d in anotacion['casos'].items()}
    assert sorted(alcance) == ids, 'la anotación de alcance no cubre exactamente los 150'
    ids_dentro = [i for i in ids if alcance[i] != 'fuera']
    print('## Alcance\n')
    filas_md = []
    for g in ('corpus_v2', 'laboratorio', 'piloto_escrito', 'trampa'):
        for clase in ('vishing', 'legitima'):
            casos_g = [i for i in r1.grupo(ids, g) if (r1.REF[i]['clase'] == 'vishing') == (clase == 'vishing')]
            filas_md.append([g, clase, len(casos_g), *(sum(alcance[i] == a for i in casos_g) for a in ('dentro', 'dudoso', 'fuera'))])
    r1.tabla(filas_md, ['grupo', 'clase', 'casos', 'dentro', 'dudoso', 'fuera'])

    if (datos / 'humo' / 'humo.json').exists():
        h = json.loads((datos / 'humo' / 'humo.json').read_text(encoding='utf-8'))
        print('## Humo de formato\n')
        r1.tabla([[f'`{v}`', f"{d['masa_ge_09']}/48", f"{d['masa_min']:.4f}", f"{d['respuesta_limpia']}/48",
                   'PASA' if d['pasa'] else 'NO PASA'] for v, d in h.items()],
                 ['prompt', 'masa ≥ 0,9', 'masa mínima', 'respuesta limpia', 'resultado'])

    control = []
    v4_filas, _ = r1.leer_corrida(r1.uno(r1.BASES['v4 solo (2026-11-05, b)'][0]), 'slm')
    json_filas = {'v4 JSON': v4_filas}
    for nombre, (carpeta, prompt) in JSON_NUEVOS.items():
        leido = una_corrida(datos, carpeta)
        if leido is None:
            print(f'> Falta {carpeta}/: se omite «{nombre}».\n')
            continue
        control.append(controlar(nombre, *leido, prompt, ids))
        json_filas[nombre] = leido[0]
    tokens = {}
    for nombre, (carpeta, prompt, _) in TOKEN.items():
        leido = una_corrida(datos, carpeta)
        if leido is None:
            print(f'> Falta {carpeta}/: se omite «{nombre}».\n')
            continue
        control.append(controlar(nombre, *leido, prompt, ids))
        tokens[nombre] = leido[0]
    print('## Control de las corridas\n')
    r1.tabla(control, ['corrida', 'líneas', 'inválidas', 'masa mínima', 'líneas con masa < 0,9', 'ms SLM p50 / p95', 'commit'])
    if 'v4-L' in tokens:
        pares = [(r1.num(a['riesgo']), r1.num(b['riesgo'])) for i in ids for a, b in zip(tokens['v4-L'][i], v4_filas[i])
                 if r1.num(a['riesgo']) is not None and r1.num(b['riesgo']) is not None]
        print(f'v4-L escribe el mismo riesgo que la línea base v4 en {sum(abs(x - y) < 1e-9 for x, y in pares)} de {len(pares)} '
              'líneas comparables. Si no coinciden casi todas, el pedido no es el mismo: revisar antes de concluir.\n')

    avisos, reglas, elegidos = vista('Vista principal: todos los casos, como en la primera vuelta', ids, json_filas, tokens,
                                     activacion, True, datos)
    vista('Dato: dentro del alcance (en corpus_v2 quedan casi solo estafas; no sirve para decidir)', ids_dentro, json_filas,
          tokens, activacion, False, datos)

    print('## Aparte, solo para mirar (vista principal)\n')
    print('Las 6 estafas que piden un dato de identificación y las 6 legítimas en que v4 avisaba por un dato pedido en una '
          'llamada que inició la persona. «L» es la línea del primer aviso (– sin aviso, «fuera» si queda fuera del alcance).\n')
    filas_md = []
    for i in DATOS_ESTAFAS + DATOS_LEGITIMAS:
        tr = r1.REF[i].get('t_r_linea')
        filas_md.append([i, r1.REF[i]['clase'] + (f' (T_R {tr})' if tr else ''), alcance[i]] +
                        ['fuera' if alcance[i] == 'fuera' else ('L' + str(av[i])) if av.get(i) else '–' for av in avisos.values()])
    r1.tabla(filas_md, ['caso', 'clase', 'alcance', *avisos])
    print('Manuales en el punto elegido (vista principal):\n')
    filas_md = []
    for nombre, av in avisos.items():
        for g in ('laboratorio', 'piloto_escrito', 'trampa'):
            filas_md.append([nombre, g, *r1.fmt(r1.metricas(av, r1.grupo(ids, g)))])
    r1.tabla(filas_md, ['configuración', 'grupo', *r1.ENC])
    controles(datos, reglas, elegidos)


def controles(datos, reglas, elegidos):
    """Primer aviso en cada control, con la regla JSON y el punto de token elegidos en la vista principal."""
    print('## Controles de ventas y préstamos (solo para mirar)\n')
    run = [p for p in (datos / 'controles-ventas').glob('*') if (p / 'manifiesto.json').exists()]
    if not run:
        print('> Falta controles-ventas/.\n')
        return
    (run,) = run
    definicion = json.loads((EXP / 'casos' / 'controles-ventas.json').read_text(encoding='utf-8'))
    por_prompt = {}
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if r['detector'] == 'slm':
                por_prompt.setdefault(r['prompt'], {}).setdefault(r['case_id'], []).append(r)
    for casos_ in por_prompt.values():
        for v in casos_.values():
            v.sort(key=lambda r: int(r['linea']))
    columnas = {}
    for nombre, prompt in (('v4 JSON', 'v4'), ('C JSON', 'c-json')):
        if nombre in reglas and prompt in por_prompt:
            columnas[f'{nombre} ({reglas[nombre]})'] = {i: aviso_json(f, reglas[nombre]) for i, f in por_prompt[prompt].items()}
    for nombre, e in elegidos.items():
        prompt = TOKEN[nombre][1]
        if e is None or prompt not in por_prompt:
            continue
        columnas[f'{nombre} ({e["politica"]}, {e["u"]:g})'] = {
            i: r1.primer_aviso(r1.puntajes(serie(f, False), e['politica']), e['u']) for i, f in por_prompt[prompt].items()}
    r1.tabla([[i, c['clase'], c['alcance'], c['que_prueba']] + [('L' + str(av[i])) if av.get(i) else '–' for av in columnas.values()]
              for i, c in definicion.items()], ['control', 'clase', 'alcance', 'qué prueba', *columnas])


if __name__ == '__main__':
    main()
