"""#143, prueba de sensibilidad: tres cambios chicos a C contra la configuración congelada.

No corre modelos ni lee la reserva; solo biblioteca estándar y el código del laboratorio. Uso, desde esta carpeta, con
los ZIP de Colab descomprimidos acá (humo/, base/, c-ancla/, c-premisa/, c-sin-freno/ y sus -rep/):
    python -I analizar.py                       # todo
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Escrito el 2026-11-10, mientras corría la prueba y antes de bajar los resultados. Aplica tal cual la regla de README.md
(«Regla, escrita antes de correr»), que está en el tag colab/143-sensibilidad:
- vista alcance-140; cifras de detección: estafas (/46), antes del pedido (/36), a tiempo (/36) y antes del
  cumplimiento (T_A < T_C, /15); FA en cotidianas (/29) y en total (/94). El aviso es la primera línea de OTRA con
  «riesgo ≥ 0,3»; las inválidas no avisan;
- cada variante pasa contra la base de la misma sesión si (1) suma 3 o más en una cifra de detección, (2) no pierde 3 o
  más en ninguna, (3) tiene FA en cotidianas ≤ base + 2, y (4) su repetición, contra la de la base, suma 3 o más en una
  cifra en que ganó la primera corrida, sin perder 3 o más y con FA en cotidianas ≤ base + 2;
- si una que pasa suma más de 10 FA en las legítimas con pedido o mención, en la corrida o en la repetición, decide
  Mateo;
- si pasan varias, la que más suma en estafas y a tiempo, juntas, en la primera corrida; si empatan, la de menos FA en
  total. Si no pasa ninguna, queda la base.
"""

import argparse, collections, importlib.util, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import casos  # noqa: E402
from detectores import (ESQUEMA_MOTIVO, MAXIMO_TOKENS_CORTE_RIESGO, PROMPT_MOTIVO_C, cargar_prompt,  # noqa: E402
                        cargar_prompt_motivo, esquema_de, huella)

# La humo ya trae la vista, la referencia y las cifras de la etapa 3: se usan tal cual.
_spec = importlib.util.spec_from_file_location('analizar_humo', AQUI.parent / '2026-11-10_config-congelada-humo' / 'analizar.py')
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)
e3 = h.e3
IDS, REF, VISTA, num, tabla, p50_p95 = h.IDS, h.REF, h.VISTA, h.num, h.tabla, h.p50_p95

BASE = 'c-json-corte-riesgo'
VARIANTES = {'c-ancla': 'c-ancla-corte-riesgo', 'c-premisa': 'c-premisa-corte-riesgo', 'c-sin-freno': 'c-sin-freno-corte-riesgo'}
CORRIDAS = {'base': (BASE, None), **{c: (p, None) for c, p in VARIANTES.items()},
            'base-rep': (BASE, 'alcance-140'), **{f'{c}-rep': (p, 'alcance-140') for c, p in VARIANTES.items()}}
UMBRAL, ROL, MARGEN, TOPE_COTIDIANAS, TOPE_DUDOSAS = 0.3, 'OTRA', 3, 2, 10
LINEAS_HUMO = 48
DETECCION = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento']
COTIDIANAS = [i for i in e3.LEGITIMAS if REF[i].get('tipo_legitima') == 'cotidiana']
DUDOSAS = [i for i in e3.LEGITIMAS if REF[i].get('tipo_legitima') in ('pedido_razonable', 'mencion_sin_pedido')]
CON_TC = [i for i in e3.ESTAFAS if REF[i].get('t_c_linea')]
assert len(COTIDIANAS) == 29 and len(DUDOSAS) == 65 and len(CON_TC) == 15, 'la vista no es la anotada'


def avisos(filas, ids, u=UMBRAL):
    """case_id → primera línea válida de OTRA con «riesgo ≥ u» (None si no avisa)."""
    return e3.avisos(filas, ids, u=u, rol=ROL, campo=False, alerta=False)


def cifras(av):
    """Las cifras de la regla, dentro de la vista."""
    m = e3.metricas(av, VISTA)
    return {'estafas': m['det'], 'antes del pedido': m['antes'], 'a tiempo': m['antes'] + m['en'],
            'antes del cumplimiento': sum(av.get(i) is not None and av[i] < REF[i]['t_c_linea'] for i in CON_TC),
            'FA cotidianas': sum(av.get(i) is not None for i in COTIDIANAS),
            'FA dudosas': sum(av.get(i) is not None for i in DUDOSAS),
            'FA': m['fa']}


DENOMINADORES = {'estafas': 46, 'antes del pedido': 36, 'a tiempo': 36, 'antes del cumplimiento': 15,
                 'FA cotidianas': 29, 'FA dudosas': 65, 'FA': 94}


def fmt(c):
    return [f'{c[k]}/{DENOMINADORES[k]}' for k in DENOMINADORES]


def controlar(carpeta, filas, man):
    """Problemas de la corrida (lista vacía si está bien)."""
    prompt, lista = CORRIDAS[carpeta]
    esperados = sorted(VISTA) if lista else IDS
    problemas = []
    if sorted(filas) != esperados or sorted(man['casos']) != esperados:
        problemas.append(f'casos distintos de {lista or "los 244"}')
    if man.get('lista') != lista:
        problemas.append(f'lista {man.get("lista")!r} en vez de {lista!r}')
    if man.get('particion') != 'desarrollo' or [i for i in man['casos'] if i.startswith(h.PREFIJOS_TEST)]:
        problemas.append('no es la partición de desarrollo')
    if any(i in IDS and v != huella((casos.DIR_TEXTO / f'{i}.txt').read_text(encoding='utf-8')) for i, v in man['casos'].items()):
        problemas.append('el texto de algún caso cambió')
    if man['ollama']['version'] != e3.OLLAMA or (man['ollama']['digests'].get(e3.MODELO) or '').removeprefix('sha256:') != e3.DIGEST:
        problemas.append('Ollama o digest distinto')
    ps = man['parametros_slm']
    if (ps['num_ctx'], ps['seed'], ps['temperatura']) != (4096, 42, 0.0):
        problemas.append('num_ctx, seed o temperatura distintos')
    if ps.get('corte_riesgo', {}).get('num_predict') != MAXIMO_TOKENS_CORTE_RIESGO:
        problemas.append('no es el corte tras el riesgo')
    p = man['prompts'].get(prompt, {})
    if list(man['prompts']) != [prompt] or (p.get('texto'), p.get('esquema')) != (cargar_prompt(prompt), esquema_de(prompt)):
        problemas.append(f'el prompt no es el de {prompt}')
    if (p.get('etapa2', {}).get('texto'), p.get('etapa2', {}).get('esquema')) != (cargar_prompt_motivo(PROMPT_MOTIVO_C), ESQUEMA_MOTIVO):
        problemas.append('la segunda consulta no es motivo_c_corte.txt')
    if man.get('solo_otra') is not True:
        problemas.append('no corrió con --solo-otra')
    if man['modo_termino'] != 'diagnostico-completo' or man['interrumpida']:
        problemas.append('no corrió entera en todas las líneas')
    if man['codigo'].get('cambios_sin_commit_en_la_carpeta'):
        problemas.append('corrió con cambios sin commitear')
    for i in sorted(filas):
        lineas, propias = e3.con_roles(i), filas[i]
        if [int(r['linea']) for r in propias] != list(range(1, len(lineas) + 1)) \
                or {r['prompt'] for r in propias} != {prompt} or {r['hablantes'] for r in propias} != {'rol'} \
                or [r['hablante'] for r in propias] != [l.hablante for l in lineas]:
            problemas.append(f'{i}: líneas, prompt o hablantes distintos')
            break
        if any(r['consulta'] != ('' if r['hablante'] == ROL else 'omitida') for r in propias):
            problemas.append(f'{i}: consultó en una línea de PROTEGIDA, o no consultó en una de OTRA')
            break
        if [int(r['linea']) for r in propias if r['ms_etapa2']] != [int(r['linea']) for r in propias if r['aviso'] == 'true']:
            problemas.append(f'{i}: el motivo no se pidió solo en el aviso')
            break
    registrado = {i: next((int(r['linea']) for r in filas[i] if r['aviso'] == 'true'), None) for i in filas}
    if registrado != avisos(filas, list(filas)):
        problemas.append('el aviso registrado no es el de «riesgo ≥ 0,3» en una línea de OTRA')
    return problemas


def diferencias(c, ref):
    return {k: c[k] - ref[k] for k in DETECCION}


def veredicto(c, base, cr, base_r):
    """('pasa' / 'decide Mateo' / 'no pasa', razón) de una variante contra la base, con la repetición."""
    d = diferencias(c, base)
    gana = [k for k, x in d.items() if x >= MARGEN]
    pierde = [k for k, x in d.items() if x <= -MARGEN]
    texto = ', '.join(f'{x:+d} {k}' for k, x in d.items()) + f', FA cotidianas {c["FA cotidianas"] - base["FA cotidianas"]:+d}'
    if not gana:
        return 'no pasa', f'no suma 3 o más en ninguna cifra ({texto})'
    if pierde:
        return 'no pasa', f'pierde 3 o más en {", ".join(pierde)} ({texto})'
    if c['FA cotidianas'] > base['FA cotidianas'] + TOPE_COTIDIANAS:
        return 'no pasa', f'suma más de {TOPE_COTIDIANAS} FA en cotidianas ({texto})'
    if cr is None or base_r is None:
        return 'no pasa', 'falta la repetición (de la variante o de la base)'
    dr = diferencias(cr, base_r)
    if not any(dr[k] >= MARGEN for k in gana):
        return 'no pasa', f'la repetición no sostiene la ganancia ({", ".join(f"{x:+d} {k}" for k, x in dr.items())})'
    if any(x <= -MARGEN for x in dr.values()):
        return 'no pasa', 'la repetición pierde 3 o más en alguna cifra'
    if cr['FA cotidianas'] > base_r['FA cotidianas'] + TOPE_COTIDIANAS:
        return 'no pasa', f'la repetición suma más de {TOPE_COTIDIANAS} FA en cotidianas'
    if c['FA dudosas'] - base['FA dudosas'] > TOPE_DUDOSAS or cr['FA dudosas'] - base_r['FA dudosas'] > TOPE_DUDOSAS:
        return 'decide Mateo', f'pasa, pero suma más de {TOPE_DUDOSAS} FA en las legítimas dudosas ({texto})'
    return 'pasa', f'pasa ({texto})'


def elegir(resultados, cs, base):
    """La variante que queda, según la regla, o None si queda la base."""
    pasan = [v for v, (estado, _) in resultados.items() if estado == 'pasa']
    if not pasan:
        return None
    return min(pasan, key=lambda v: (-(cs[v]['estafas'] - base['estafas'] + cs[v]['a tiempo'] - base['a tiempo']), cs[v]['FA']))


def humo(datos):
    ruta = datos / 'humo' / 'humo.json'
    print('## Humo de formato\n')
    if not ruta.exists():
        print('> Falta humo/humo.json.\n')
        return {}
    d = json.loads(ruta.read_text(encoding='utf-8'))
    tabla([[f'`{p}`', f"{x['leidas']}/{x['lineas']}", ', '.join(x['errores']) or '—', f"{x['igual_a_la_base']}/{x['lineas']}",
            x['altos_03'], x['altos_06'], 'PASA' if x['pasa'] else 'NO PASA'] for p, x in d.items()],
          ['prompt', 'riesgo leído', 'errores', 'mismo riesgo que la base (dato)', 'riesgo ≥ 0,3 (dato)', 'riesgo ≥ 0,6 (dato)',
           'resultado'])
    return {p: x['pasa'] is True and x['leidas'] == x['lineas'] == LINEAS_HUMO for p, x in d.items()}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    args = p.parse_args(argv)
    datos = args.datos.resolve()
    print('# #143, prueba de sensibilidad — análisis offline\n')
    print('Vista: alcance-140, 46 estafas (36 con pedido, 15 con cumplimiento) y 94 legítimas (29 cotidianas y 65 con '
          'pedido o mención). El aviso es la primera línea de OTRA con «riesgo ≥ 0,3».\n')
    pasa_humo = humo(datos)
    print('## Control de las corridas\n')
    leidas, problemas, cs, avs = {}, {}, {}, {}
    filas_md = []
    for carpeta in CORRIDAS:
        corrida = e3.leer(datos, carpeta)
        if corrida is None:
            filas_md.append([carpeta, '—', '—', 'falta'])
            continue
        filas, man = corrida
        prob = controlar(carpeta, filas, man)
        problemas[carpeta] = prob
        consultadas = [r for v in filas.values() for r in v if r['consulta'] != 'omitida']
        invalidas = sum(r['valida'] != 'true' for r in consultadas)
        filas_md.append([carpeta, man['codigo']['commit'][:10], f'{invalidas}/{len(consultadas)}', '; '.join(prob) or 'bien'])
        if not prob:
            leidas[carpeta] = filas
            avs[carpeta] = avisos(filas, sorted(filas))
            cs[carpeta] = cifras(avs[carpeta])
    tabla(filas_md, ['corrida', 'commit', 'líneas inválidas', 'control'])

    print('## Cifras\n')
    tabla([[c, *fmt(x)] for c, x in cs.items()], ['corrida', *DENOMINADORES])

    print('## La regla\n')
    if 'base' not in cs:
        print('**No se aplica:** falta la corrida de la base o tiene problemas. Queda la base.\n')
        return 0
    resultados = {}
    for v in VARIANTES:
        if not pasa_humo.get(VARIANTES[v]):
            resultados[v] = ('no pasa', 'no pasó la humo de formato o falta')
        elif v not in cs:
            resultados[v] = ('no pasa', 'falta la corrida o tiene problemas')
        else:
            resultados[v] = veredicto(cs[v], cs['base'], cs.get(f'{v}-rep'), cs.get('base-rep'))
    tabla([[f'`{v}`', estado, razon] for v, (estado, razon) in resultados.items()], ['variante', 'resultado', 'por qué'])
    elegida = elegir(resultados, cs, cs['base'])
    decide = [v for v, (estado, _) in resultados.items() if estado == 'decide Mateo']
    print(f'**Resultado: {"queda la base" if elegida is None else f"queda `{elegida}`"}.**'
          + (f' Además, decide Mateo sobre {", ".join(f"`{v}`" for v in decide)}.' if decide else '') + '\n')

    print('## Aparte, solo para mirar\n')
    aparte(leidas, avs, cs)
    return 0


def aparte(leidas, avs, cs):
    if 'base' not in avs:
        return
    base = avs['base']
    print('### Estafas que la base no avisa, y en qué línea las avisa cada variante\n')
    perdidas = [i for i in e3.ESTAFAS if base[i] is None]
    tabla([[i, REF[i].get('pedido') or 'sin pedido', REF[i].get('t_r_linea') or '—',
            *(f'L{avs[v][i]}' if v in avs and avs[v][i] else '–' for v in VARIANTES)] for i in perdidas],
          ['caso', 'pedido', 'T_R', *VARIANTES])
    print('### FA por tipo de legítima\n')
    tipos = ['cotidiana', 'pedido_razonable', 'mencion_sin_pedido']
    n = collections.Counter(REF[i].get('tipo_legitima') for i in e3.LEGITIMAS)
    tabla([[c, *(f"{sum(avs[c][i] is not None for i in e3.LEGITIMAS if REF[i].get('tipo_legitima') == t)}/{n[t]}" for t in tipos)]
           for c in avs if not c.endswith('-rep')], ['corrida', *tipos])
    print('### Curva en todas las líneas de OTRA (estafas · a tiempo · FA cotidianas · FA total)\n')
    us = [round(x / 10, 1) for x in range(1, 10)]
    filas_md = []
    for c in avs:
        if c.endswith('-rep'):
            continue
        fila = [c]
        for u in us:
            x = cifras(avisos(leidas[c], IDS, u))
            fila.append(f"{x['estafas']} · {x['a tiempo']} · {x['FA cotidianas']} · {x['FA']}")
        filas_md.append(fila)
    tabla(filas_md, ['corrida', *(f'u={u}' for u in us)])
    print('### Avisos de un 0,3 exacto, latencia y motivo (dentro del alcance)\n')
    filas_md = []
    for c in avs:
        if c.endswith('-rep'):
            continue
        fila_aviso = {i: next(r for r in leidas[c][i] if int(r['linea']) == avs[c][i]) for i in VISTA if avs[c].get(i)}
        exactos = sum(num(r['riesgo']) == UMBRAL for r in fila_aviso.values())
        con = [r for i in VISTA for r in leidas[c].get(i, []) if r['consulta'] != 'omitida']
        validos = [r for r in fila_aviso.values() if not r['error'].startswith('etapa2_') and r['motivo'].strip()]
        filas_md.append([c, f'{exactos}/{len(fila_aviso)}', p50_p95([num(r['ms_etapa1']) for r in con if num(r['ms_etapa1']) is not None]),
                         p50_p95([num(r['ms_etapa2']) for r in fila_aviso.values() if num(r['ms_etapa2']) is not None]),
                         f'{len(validos)}/{len(fila_aviso)}'])
    tabla(filas_md, ['corrida', 'avisos de 0,3 exacto', 'primera consulta (ms)', 'motivo (ms)', 'motivo válido'])
    print('### FA nuevas de cada variante, con su motivo, para leer a mano\n')
    for v in VARIANTES:
        if v not in avs:
            continue
        nuevas = sorted(i for i in e3.LEGITIMAS if avs[v][i] is not None and base[i] is None)
        print(f'**`{v}`:** {len(nuevas)} FA que la base no tiene.\n')
        if nuevas:
            tabla([[i, REF[i].get('tipo_legitima'), f'L{avs[v][i]}',
                    *(lambda r: [r['riesgo'], f'«{h.celda(r["motivo"])}»' if r['motivo'] else '—'])(
                        next(r for r in leidas[v][i] if int(r['linea']) == avs[v][i]))] for i in nuevas],
                  ['caso', 'tipo', 'aviso', 'riesgo', 'motivo'])
    print('### alcance-91\n')
    tabla([[c, *e3.fmt(e3.metricas(avs[c], e3.VISTA_91))] for c in avs if not c.endswith('-rep')], ['corrida', *e3.ENC])


if __name__ == '__main__':
    sys.exit(main())
