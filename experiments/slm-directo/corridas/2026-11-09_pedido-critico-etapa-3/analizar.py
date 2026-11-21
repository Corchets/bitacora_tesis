"""#143, segunda vuelta, etapa 3: C con campo (`pedido_critico`) contra C sin alerta, una consulta por línea.

No corre modelos ni lee la reserva; solo biblioteca estándar y el código del laboratorio (casos, reglas). Uso, desde
esta carpeta, con los ZIP de Colab descomprimidos acá (humo/, c-sin-alerta/, c-con-campo/, c-sin-alerta-rep/,
c-con-campo-rep/ y controles-ventas/) y las corridas de la etapa 2 en ../2026-11-07_alcance-etapa-2/:
    python -I analizar.py                       # todo
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Escrito el 2026-11-09, antes de correr. Decisiones de Mateo (2026-11-09), en README.md de esta carpeta:
- Se prueban dos versiones de C, con el mismo texto de tarea y una sola consulta por línea. «C sin alerta», la base,
  pide en el JSON solo el riesgo. «C con campo» pide `pedido_critico` y después el riesgo, con la definición de Mateo
  (prompts/salida_json_c_con_campo.txt). Cada una corre dos veces: sobre los 244 y sobre los 140.
- «Cualquier aviso» es «riesgo ≥ 0,3» en la base y «riesgo ≥ 0,3 o pedido_critico» en C con campo. La alerta fuerte
  (`pedido_critico`) se informa aparte y no decide.
- El tope de FA es el de la base + 5.
- La regla usa todas las líneas. «Solo OTRA» se adopta si no empeora más de 2 ninguna cifra, en las dos corridas.
- El primer aviso (riesgo ≥ 0,3) muestra un texto fijo en la app. El motivo propio de C (prompts/motivo_c_corte.txt)
  se pide solo en la primera alerta fuerte (`pedido_critico` en true), una vez por llamada; la base nunca lo pide.

La regla (README.md, «Regla, escrita antes de correr»), dentro del alcance (46 estafas, 36 con pedido, y 94 legítimas):
1. Base contra C de la etapa 2 («riesgo ≥ 0,3 o alerta» en c-json-corte): si alguna cifra se mueve más de ±2 (estafas,
   antes del pedido, a tiempo o FA), la base pasa a ser el prompt de la etapa 2 cortado tras el riesgo, leído de
   c-json-corte y c-json-corte-rep con «riesgo ≥ 0,3», sin la alerta.
2. C con campo se adopta contra la base si suma 3 o más en estafas, antes del pedido o a tiempo, sin perder 3 o más en
   ninguna y con FA ≤ FA(base) + 5, y si la repetición, contra la repetición de la base, cumple lo mismo: +3 en una
   cifra en que ganó la primera corrida, sin perder 3 o más y con FA ≤ FA(base) + 5. Si gana en una y pierde 3 o más
   en otra, decide el equipo. Si no, queda la base.
3. alcance-91 (las 46 estafas y una legítima por escenario, sin dudosas): si ahí el resultado se invierte, decide el
   equipo (propuesta de la sesión del corpus, confirmada por Mateo).
4. «Solo OTRA»: se adopta para la configuración que queda si, en la corrida y en la repetición, contra la lectura en
   todas las líneas, ninguna cifra de detección baja más de 2 y las FA no suben más de 2 (Mateo: «que no empeore más
   de 2»; con C de la etapa 2, ±2 literal rechazaba una baja de 3 FA).
Aparte, solo para mirar: la alerta fuerte, las estafas sin pedido, la curva, los intervalos de Wilson, las estafas por
tipo de pedido, los pares discordantes, las FA por lote, por pedido de datos y al comienzo, otros grupos, las reglas
del laboratorio, la repetición, la base contra la etapa 2 línea por línea, la latencia, el costo de la política, el
motivo de C y los controles de ventas.
"""
import argparse, collections, csv, functools, json, math, re, statistics, sys
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import casos  # noqa: E402
from detectores import (ESQUEMA_MOTIVO, MAXIMO_TOKENS_C_CORTO, PROMPT_MOTIVO_C, DetectorReglas,  # noqa: E402
                        cargar_prompt, cargar_prompt_motivo, esquema_de, evidencia_en_texto, huella)

UMBRAL = 0.3        # la regla de C adoptada en la etapa 2, sin la alerta escrita
ROL = 'OTRA'
MARGEN = 3          # +3 en una cifra; ±2 es ruido (ADR 0005)
TOPE_FA = 5         # C con campo puede sumar hasta 5 FA respecto de la base (Mateo, 2026-11-09)
TOLERANCIA = 2      # la base contra la etapa 2 (±2), y «solo OTRA» contra todas las líneas (que no empeore más de 2)
UMBRALES = [round(x / 10, 1) for x in range(1, 11)]
OLLAMA = '0.40.14'
MODELO = 'gemma4:e2b-it-q4_K_M'
DIGEST = 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2'
CORRIDAS = {  # carpeta: (prompt, lista; None = los 244)
    'c-sin-alerta': ('c-sin-alerta', None),
    'c-con-campo': ('c-con-campo', None),
    'c-sin-alerta-rep': ('c-sin-alerta', 'alcance-140'),
    'c-con-campo-rep': ('c-con-campo', 'alcance-140'),
}
BASE, CAMPO, BASE_REP, CAMPO_REP = CORRIDAS
ETAPA_2 = AQUI.parent / '2026-11-07_alcance-etapa-2'
NOMBRES = {'c-sin-alerta': 'C sin alerta', 'c-con-campo': 'C con campo', 'c-sin-alerta-rep': 'C sin alerta, repetición',
           'c-con-campo-rep': 'C con campo, repetición', 'etapa-2': 'C de la etapa 2, cortado tras el riesgo',
           'etapa-2-rep': 'C de la etapa 2, repetición'}
ALCANCES = [EXP / 'casos' / 'alcance-desarrollo.json', EXP / 'casos' / 'alcance-legitimas-cotidianas.json']
LOTES = {'LEG (21)': 'legitimas-leg-21', 'LEG2 (28)': 'legitimas-leg2-28', 'ENT-L (42)': 'legitimas-ent-l-42',
         'selección (3)': 'legitimas-seleccion-3'}
PEDIDOS = ['sin pedido', 'REQUEST_AUTH_CODE', 'REQUEST_SECRET', 'REQUEST_TRANSFER', 'REQUEST_PERSONAL_DATA',
           'REQUEST_SECURITY_ACTION', 'REQUEST_REMOTE_ACCESS']
# Pedidos críticos de la referencia, como en diagnostico.py de la etapa 2: los datos personales no cuentan.
CRITICOS = {'REQUEST_AUTH_CODE', 'REQUEST_SECRET', 'REQUEST_TRANSFER', 'REQUEST_REMOTE_ACCESS', 'REQUEST_SECURITY_ACTION'}
# Medición del motivo, escrita antes de correr: un motivo nombra un pedido si tiene alguna de estas palabras. Se marca
# cuando la referencia todavía no tiene un pedido crítico, y esos motivos se leen a mano.
PALABRAS_PEDIDO = re.compile(r'\b(c[oó]digos?|claves?|contrase[ñn]as?|pin|token|tarjetas?|transfer\w*|pag(?:o|ar|ue)\w*|'
                             r'cbu|alias|instal\w*|aplicaci[oó]n|app|pantalla|cajero|fotos?|selfie|d[ií]gitos)\b',
                             re.IGNORECASE)
CIFRAS = {'estafas': lambda m: m['det'], 'antes del pedido': lambda m: m['antes'],
          'a tiempo': lambda m: m['antes'] + m['en']}
TODAS = dict(CIFRAS, FA=lambda m: m['fa'])


def leer_lista(nombre):
    texto = (EXP / 'casos' / 'listas' / f'{nombre}.txt').read_text(encoding='utf-8')
    return [l.strip() for l in texto.splitlines() if l.strip() and not l.startswith('#')]


IDS = casos.ids_de_casos(particion='desarrollo')
assert len(IDS) == 244 and not [i for i in IDS if i.startswith('CV2-T')], 'no son los 244 de desarrollo'
REF = {i: casos.cargar_referencia(i) for i in IDS}
ALCANCE = {}
for ruta in ALCANCES:
    ALCANCE.update({i: d['alcance'] for i, d in json.loads(ruta.read_text(encoding='utf-8'))['casos'].items()})
assert sorted(ALCANCE) == IDS, 'el alcance anotado no cubre exactamente los 244'
ESTAFAS = [i for i in IDS if REF[i]['grupo'] == 'corpus_v2' and REF[i]['clase'] == 'vishing']
LEGITIMAS = [i for i in IDS if REF[i]['grupo'] == 'legitimas_cotidianas']
VISTA = ESTAFAS + LEGITIMAS
assert len(ESTAFAS) == 46 and len(LEGITIMAS) == 94 and all(ALCANCE[i] == 'dentro' for i in VISTA)
assert sorted(leer_lista('alcance-140')) == sorted(VISTA), 'alcance-140.txt no es la vista'
# Vista limpia de la sesión del corpus (rama corpus/escenarios-y-dudosas, 45e3037): una legítima por escenario, sin
# dudosas. Es un subconjunto de los 140.
VISTA_91 = leer_lista('alcance-91')
assert set(VISTA_91) <= set(VISTA) and sorted(i for i in VISTA_91 if i in ESTAFAS) == sorted(ESTAFAS) \
    and len(VISTA_91) == 91, 'alcance-91 no son las 46 estafas y 45 de las 94 legítimas'


def num(x):
    return float(x) if x not in ('', None) else None


def tabla(filas, encabezado):
    print('| ' + ' | '.join(encabezado) + ' |')
    print('|' + '---|' * len(encabezado))
    for f in filas:
        print('| ' + ' | '.join(str(x) for x in f) + ' |')
    print()


def p50_p95(v):
    v = sorted(v)
    return f'{statistics.median(v):.0f} / {v[min(len(v) - 1, math.ceil(0.95 * len(v)) - 1)]:.0f}' if v else '—'


def wilson(k, n, z=1.96):
    if not n:
        return '—'
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return f'{k}/{n}, {100 * p:.0f} % [{100 * (centro - mitad):.0f}–{100 * (centro + mitad):.0f}]'


@functools.cache
def con_roles(i):
    return tuple(casos.con_roles(i, casos.cargar_texto(i)))


def linea_critica(i):
    """Primera línea con un pedido crítico en la referencia (sin datos personales), o None."""
    return min((e['linea'] for e in REF[i].get('evidencia') or [] if e['evento'] == 'pedido' and CRITICOS & set(e['etiquetas'])),
               default=None)


# --- Corridas ---
def leer_run(run):
    filas = collections.defaultdict(list)
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if r['detector'] == 'slm':
                filas[r['case_id']].append(r)
    for v in filas.values():
        v.sort(key=lambda r: int(r['linea']))
    return dict(filas), json.loads((run / 'manifiesto.json').read_text(encoding='utf-8'))


def leer(datos, carpeta):
    """(filas por caso, manifiesto) de la única corrida en datos/carpeta, o None si falta."""
    runs = [p for p in (datos / carpeta).glob('*') if (p / 'manifiesto.json').exists()] if (datos / carpeta).exists() else []
    if not runs:
        return None
    (run,) = runs
    return leer_run(run)


def avisos(filas, ids, u=UMBRAL, rol=None, campo=True, alerta=False, solo_campo=False):
    """case_id → primera línea válida en que dispara la regla (None si no dispara).

    La regla es «riesgo ≥ u», más `pedido_critico` (si `campo`) o la alerta escrita (si `alerta`, para C de la etapa 2).
    `solo_campo`: solo `pedido_critico` (la alerta fuerte). `rol`: solo las líneas de ese hablante (None: todas).
    """
    def dispara(r):
        fuerte = campo and r.get('pedido_critico') == 'true'
        if solo_campo:
            return fuerte
        return (num(r['riesgo']) is not None and num(r['riesgo']) >= u - 1e-9) or fuerte \
            or (alerta and r.get('alerta_escrita') == 'true')
    return {i: next((int(r['linea']) for r in filas.get(i, []) if r['valida'] == 'true'
                     and (rol is None or r['hablante'] == rol) and dispara(r)), None) for i in ids}


def controlar(carpeta, filas, man):
    """Problemas de la corrida (lista vacía si está bien) y su fila para la tabla de control."""
    prompt, lista = CORRIDAS[carpeta]
    esperados = sorted(VISTA) if lista else IDS
    problemas = []
    if sorted(filas) != esperados or sorted(man['casos']) != esperados:
        problemas.append(f'casos distintos de {lista or "los 244"}')
    if man.get('lista') != lista:
        problemas.append(f'lista {man.get("lista")!r} en vez de {lista!r}')
    if [i for i in man['casos'] if i.startswith('CV2-T')] or man['particion'] != 'desarrollo':
        problemas.append('no es la partición de desarrollo')
    if any(h != huella((casos.DIR_TEXTO / f'{i}.txt').read_text(encoding='utf-8')) for i, h in man['casos'].items()):
        problemas.append('el texto de algún caso cambió')
    if man['ollama']['version'] != OLLAMA or (man['ollama']['digests'].get(MODELO) or '').removeprefix('sha256:') != DIGEST:
        problemas.append('Ollama o digest distinto')
    ps = man['parametros_slm']
    if (ps['num_ctx'], ps['seed'], ps['temperatura']) != (4096, 42, 0.0):
        problemas.append('num_ctx, seed o temperatura distintos')
    if ps.get('c_corto', {}).get('num_predict') != MAXIMO_TOKENS_C_CORTO:
        problemas.append('no es el JSON corto de C')
    p = man['prompts'].get(prompt, {})
    if (p.get('texto'), p.get('esquema')) != (cargar_prompt(prompt), esquema_de(prompt)):
        problemas.append(f'el prompt no es el de {prompt}')
    if (p.get('etapa2', {}).get('texto'), p.get('etapa2', {}).get('esquema')) != (cargar_prompt_motivo(PROMPT_MOTIVO_C), ESQUEMA_MOTIVO):
        problemas.append('la segunda consulta no es motivo_c_corte.txt')
    if man['modo_termino'] != 'diagnostico-completo' or man['interrumpida']:
        problemas.append('no corrió entera en todas las líneas')
    for i in filas:
        if [int(r['linea']) for r in filas[i]] != list(range(1, len(casos.cargar_texto(i)) + 1)) \
                or {r['prompt'] for r in filas[i]} != {prompt} or {r['hablantes'] for r in filas[i]} != {'rol'} \
                or [r['hablante'] for r in filas[i]] != [l.hablante for l in con_roles(i)]:
            problemas.append(f'{i}: líneas, prompt o hablantes distintos')
            break
    # El aviso que registró correr.py tiene que ser el de la regla, recalculado acá.
    registrado = {i: next((int(r['linea']) for r in filas[i] if r['aviso'] == 'true'), None) for i in filas}
    if registrado != avisos(filas, list(filas)):
        problemas.append('el aviso registrado no es el de «riesgo ≥ 0,3 o pedido_critico»')
    todas = [r for v in filas.values() for r in v]
    invalidas = collections.Counter(r['error'] for r in todas if r['valida'] != 'true')
    ms = [num(r['ms_etapa1']) for r in todas if num(r['ms_etapa1']) is not None]
    fila = [carpeta, len(filas), len(todas), f'{sum(invalidas.values())} {dict(invalidas) or ""}'.strip(), p50_p95(ms),
            man['codigo']['commit'][:10] + (' (con cambios)' if man['codigo'].get('cambios_sin_commit_en_la_carpeta') else '')]
    if man['codigo'].get('cambios_sin_commit_en_la_carpeta'):
        problemas.append('corrió con cambios sin commitear')
    return problemas, fila


# --- Métricas y regla ---
def metricas(av, ids):
    est = [i for i in ids if REF[i]['clase'] == 'vishing']
    leg = [i for i in ids if REF[i]['clase'] != 'vishing']
    conp = [i for i in est if REF[i].get('t_r_linea')]
    return {'det': sum(av.get(i) is not None for i in est), 'n_est': len(est),
            'antes': sum(av.get(i) is not None and av[i] < REF[i]['t_r_linea'] for i in conp),
            'en': sum(av.get(i) is not None and av[i] == REF[i]['t_r_linea'] for i in conp), 'n_conp': len(conp),
            'fa': sum(av.get(i) is not None for i in leg), 'n_leg': len(leg)}


def fmt(m):
    return [f"{m['det']}/{m['n_est']}", f"{m['antes']}/{m['n_conp']}", f"{m['antes'] + m['en']}/{m['n_conp']}",
            f"{m['fa']}/{m['n_leg']}"]


ENC = ['estafas', 'antes del pedido', 'a tiempo (antes o en el pedido)', 'FA']


def corto(m):
    """«estafas · antes · a tiempo · FA», sin las partes que no tienen casos."""
    partes = []
    if m['n_est']:
        partes.append(f"{m['det']}/{m['n_est']}")
        partes.append(f"{m['antes']}/{m['n_conp']} · {m['antes'] + m['en']}/{m['n_conp']}" if m['n_conp'] else '–')
    if m['n_leg']:
        partes.append(f"FA {m['fa']}/{m['n_leg']}")
    return ' · '.join(partes)


def diferencias(m, ref, cifras=CIFRAS):
    return {c: f(m) - f(ref) for c, f in cifras.items()}


def comparar(m, ref):
    """'gana' / 'pierde' / 'mixto' / 'ruido', las cifras en que gana y las diferencias."""
    d = diferencias(m, ref)
    gana = [c for c, x in d.items() if x >= MARGEN]
    pierde = [c for c, x in d.items() if x <= -MARGEN]
    estado = 'mixto' if gana and pierde else 'gana' if gana else 'pierde' if pierde else 'ruido'
    return estado, gana, d


def texto_dif(d, fa=None):
    return ', '.join(f'{x:+d} {c}' for c, x in d.items()) + ('' if fa is None else f', FA {fa}')


def dentro(m, ref):
    """True si las cuatro cifras quedan dentro de ±TOLERANCIA."""
    return all(abs(x) <= TOLERANCIA for x in diferencias(m, ref, TODAS).values())


def no_empeora(m, ref):
    """True si ninguna cifra de detección baja más de TOLERANCIA y las FA no suben más de TOLERANCIA."""
    d = diferencias(m, ref, TODAS)
    return all(d[c] >= -TOLERANCIA for c in CIFRAS) and d['FA'] <= TOLERANCIA


def veredicto(m, ref, mr, ref_r):
    """('adopta' / 'queda la base' / 'decide el equipo', texto) de C con campo contra la base, con la repetición."""
    estado, gana, _ = comparar(m, ref)
    if estado == 'mixto':
        return 'decide el equipo', 'gana en una cifra y pierde 3 o más en otra: no se adopta, decide el equipo'
    if estado == 'pierde':
        return 'queda la base', 'pierde 3 o más: no se adopta'
    if estado == 'ruido':
        return 'queda la base', 'dentro de ±2 en las tres cifras: queda la base'
    if m['fa'] > ref['fa'] + TOPE_FA:
        return 'queda la base', f'gana ({", ".join(gana)}), pero suma más de {TOPE_FA} FA ({m["fa"]} > {ref["fa"] + TOPE_FA}): no se adopta'
    if mr is None or ref_r is None:
        return 'queda la base', f'gana ({", ".join(gana)}), pero falta una repetición: no cuenta'
    estado_r, gana_r, d_r = comparar(mr, ref_r)
    rep = texto_dif(d_r, f'{mr["fa"]} contra {ref_r["fa"]}')
    if estado_r == 'mixto':
        return 'decide el equipo', (f'gana ({", ".join(gana)}), pero la repetición pierde 3 o más en una cifra ({rep}): '
                                    'no se adopta, decide el equipo')
    if estado_r == 'gana' and set(gana) & set(gana_r) and mr['fa'] <= ref_r['fa'] + TOPE_FA:
        return 'adopta', f'gana ({", ".join(gana)}) y la repetición lo sostiene ({rep}): se adopta'
    return 'queda la base', f'gana ({", ".join(gana)}), pero la repetición no lo sostiene ({rep}): no cuenta'


@functools.cache
def avisos_de_reglas():
    """Primer aviso de las reglas v1 y v2 del laboratorio en los 244. Miran solo la línea nueva y corren sin modelo."""
    textos, salida = {i: casos.cargar_texto(i) for i in IDS}, {}
    for version in ('v1', 'v2'):
        d = DetectorReglas(version)
        salida[d.nombre] = {i: next((n for n in range(1, len(t) + 1) if d.evaluar(t[:n]).alerta_sugerida), None)
                            for i, t in textos.items()}
    return salida


# --- Informe ---
def humo(datos):
    if not (datos / 'humo' / 'humo.json').exists():
        print('> Falta humo/humo.json.\n')
        return
    h = json.loads((datos / 'humo' / 'humo.json').read_text(encoding='utf-8'))
    print('## Humo de formato\n')
    tabla([[f'`{prompt}`', f"{d['leidas']}/{d['lineas']}", f"{d['al_tope']}", d['tokens_salida'],
            f"{d['igual_a_c_json_corte']}/{d['lineas']}", '—' if d.get('campo_true') is None else d['campo_true'],
            'PASA' if d['pasa'] else 'NO PASA'] for prompt, d in h.items()],
          ['prompt', 'JSON leído', 'llegan al tope', 'tokens generados (mín / mediana / máx)',
           'mismo riesgo que c-json-corte (dato)', 'pedido_critico en true (dato)', 'resultado'])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    p.add_argument('--etapa-2', type=Path, default=ETAPA_2, help='carpeta con c-json-corte/ y c-json-corte-rep/')
    args = p.parse_args(argv)
    datos, etapa_2 = args.datos.resolve(), args.etapa_2.resolve()
    print('# #143, segunda vuelta, etapa 3: C con campo contra C sin alerta — análisis offline\n')
    print(f'Vista dentro del alcance: {len(ESTAFAS)} estafas de corpus_v2 '
          f'({sum(1 for i in ESTAFAS if REF[i].get("t_r_linea"))} con pedido) y {len(LEGITIMAS)} legítimas entrantes. '
          f'«Cualquier aviso»: riesgo ≥ {UMBRAL:g}, o `pedido_critico` en C con campo, en cualquier línea.\n')
    humo(datos)

    leidas, problemas, control = {}, {}, []
    for carpeta in CORRIDAS:
        leido = leer(datos, carpeta)
        if leido is None:
            print(f'> Falta {carpeta}/.\n')
            continue
        problemas[carpeta], fila = controlar(carpeta, *leido)
        control.append(fila)
        leidas[carpeta] = leido
    print('## Control de las corridas\n')
    tabla(control, ['corrida', 'casos', 'líneas', 'inválidas', 'ms primera consulta p50 / p95', 'commit'])
    commits = {m['codigo']['commit'] for _, m in leidas.values()}
    if len(commits) > 1:
        problemas.setdefault('todas', []).append(f'commits distintos: {sorted(commits)}')
    e2 = {c: leer(etapa_2, c) for c in ('c-json-corte', 'c-json-corte-rep')}
    if any(x is None for x in e2.values()):
        problemas.setdefault('etapa 2', []).append(f'faltan c-json-corte/ o c-json-corte-rep/ en {etapa_2}')
    elif sorted(e2['c-json-corte'][0]) != IDS or sorted(e2['c-json-corte-rep'][0]) != sorted(VISTA):
        problemas.setdefault('etapa 2', []).append('las corridas de C de la etapa 2 no tienen los casos esperados')
    malos = {c: x for c, x in problemas.items() if x}
    if malos:
        for c, x in malos.items():
            print(f'- **{c}:** {"; ".join(x)}')
        print('\n**Hay problemas de control: no se aplica la regla.**\n')
        return 1
    print('Sin problemas de control: mismo commit, digest, Ollama, parámetros, prompts, casos y avisos, y están las '
          'corridas de C de la etapa 2.\n')

    filas = {c: f for c, (f, _) in leidas.items()}
    e2_filas, e2_rep = e2['c-json-corte'][0], e2['c-json-corte-rep'][0]

    # 1. La base contra C de la etapa 2.
    print('## Regla de la etapa 3\n')
    print('### 1. La base contra C de la etapa 2\n')
    m_e2 = metricas(avisos(e2_filas, VISTA, campo=False, alerta=True), VISTA)
    filas_md = [['C de la etapa 2, «riesgo ≥ 0,3 o alerta»', *fmt(m_e2), '—']]
    if BASE in filas:
        m_b = metricas(avisos(filas[BASE], VISTA), VISTA)
        se_mantiene = dentro(m_b, m_e2)
        filas_md.append(['C sin alerta, «riesgo ≥ 0,3»', *fmt(m_b), texto_dif(diferencias(m_b, m_e2, TODAS))])
    else:
        se_mantiene = False
    tabla(filas_md, ['configuración', *ENC, 'contra la etapa 2'])
    if se_mantiene:
        base, base_rep, nombre_base = filas[BASE], filas.get(BASE_REP), 'C sin alerta (`c-sin-alerta`)'
        print('Las cuatro cifras quedan dentro de ±2: **la base es C sin alerta.**\n')
    else:
        base, base_rep, nombre_base = e2_filas, e2_rep, 'C de la etapa 2, cortado tras el riesgo'
        print(('Falta C sin alerta' if BASE not in filas else 'Alguna cifra se mueve más de ±2') +
              ': **la base es el prompt de C de la etapa 2, cortado tras el riesgo** (c-json-corte y su repetición, '
              'con «riesgo ≥ 0,3» y sin la alerta).\n')
    base_campo = False  # la base no tiene `pedido_critico`

    # 2. C con campo contra la base.
    print('### 2. C con campo contra la base, en «cualquier aviso»\n')

    def resultado(ids):
        ref = metricas(avisos(base, ids, campo=base_campo), ids)
        ref_r = metricas(avisos(base_rep, ids, campo=base_campo), ids) if base_rep is not None else None
        if CAMPO not in filas:
            return 'queda la base', ref, None, None, ref_r, 'falta la corrida: no cuenta'
        m = metricas(avisos(filas[CAMPO], ids), ids)
        mr = metricas(avisos(filas[CAMPO_REP], ids), ids) if CAMPO_REP in filas else None
        r, texto = veredicto(m, ref, mr, ref_r)
        return r, ref, m, mr, ref_r, texto

    r140, ref, m, mr, ref_r, texto = resultado(VISTA)
    print(f'La base ({nombre_base}) tiene {ref["fa"]}/94 FA, así que C con campo puede tener hasta {ref["fa"] + TOPE_FA}.\n')
    filas_md = [[f'base: {nombre_base}', *fmt(ref), '—', '—']]
    if ref_r is not None:
        filas_md.append(['base, repetición (los 140)', *fmt(ref_r), '—', '—'])
    if m is not None:
        filas_md.append(['C con campo (`c-con-campo`)', *fmt(m), texto_dif(comparar(m, ref)[2]), texto])
    else:
        filas_md.append(['C con campo (`c-con-campo`)', '', '', '', '', '', texto])
    if mr is not None and ref_r is not None:
        filas_md.append(['C con campo, repetición (los 140)', *fmt(mr), texto_dif(comparar(mr, ref_r)[2]), 'contra la repetición de la base'])
    tabla(filas_md, ['configuración', *ENC, 'contra la base', 'veredicto'])

    # 3. alcance-91.
    print('### 3. alcance-91: las 46 estafas y una legítima por escenario, sin dudosas\n')
    r91, ref91, m91, mr91, ref91_r, texto91 = resultado(VISTA_91)
    filas_md = [['base', *fmt(ref91), '—']]
    if m91 is not None:
        filas_md.append(['C con campo', *fmt(m91), texto91])
    tabla(filas_md, ['configuración', *ENC, 'veredicto en alcance-91'])
    final = r140
    if r140 != 'decide el equipo' and (r140 == 'adopta') != (r91 == 'adopta'):
        final = 'decide el equipo'
        print('**En alcance-91 el resultado se invierte: decide el equipo.**\n')
    else:
        print('En alcance-91 el resultado no se invierte.\n')
    print({'adopta': '**Se adopta C con campo (`c-con-campo`), provisorio hasta la reserva.**',
           'queda la base': f'**Queda la base, {nombre_base}, provisorio hasta la reserva.**',
           'decide el equipo': '**No se adopta C con campo por la regla: decide el equipo.**'}[final] + '\n')

    # 4. «Solo OTRA».
    print('### 4. «Solo OTRA» contra todas las líneas\n')
    configs = {'base': (base, base_rep, base_campo)}
    if CAMPO in filas:
        configs['C con campo'] = (filas[CAMPO], filas.get(CAMPO_REP), True)
    filas_md, se_adopta = [], {}
    for nombre, (f1, f2, campo) in configs.items():
        ok = []
        for etiqueta, f in (('corrida', f1), ('repetición', f2)):
            if f is None:
                ok.append(False)
                filas_md.append([nombre, etiqueta, 'falta', '', ''])
                continue
            todas_l = metricas(avisos(f, VISTA, campo=campo), VISTA)
            otra = metricas(avisos(f, VISTA, campo=campo, rol=ROL), VISTA)
            ok.append(no_empeora(otra, todas_l))
            filas_md.append([nombre, etiqueta, corto(todas_l), corto(otra), texto_dif(diferencias(otra, todas_l, TODAS))])
        se_adopta[nombre] = all(ok)
    tabla(filas_md, ['configuración', 'corrida', 'todas las líneas', 'solo OTRA', 'solo OTRA contra todas'])
    queda = 'C con campo' if final == 'adopta' else 'base' if final == 'queda la base' else None
    if queda is None:
        print('Decide el equipo, así que «solo OTRA» se informa para las dos: ' +
              '; '.join(f'{n}: {"no empeora más de 2" if v else "empeora más de 2"}' for n, v in se_adopta.items()) + '.\n')
    else:
        print(f'**«Solo OTRA» {"se adopta" if se_adopta.get(queda) else "no se adopta"}** para la configuración que '
              f'queda ({queda}).\n')

    aparte(filas, base, base_rep, nombre_base, datos, e2_filas)
    return 0


def aparte(filas, base, base_rep, nombre_base, datos, e2_filas):
    print('## Aparte, solo para mirar\n')
    series = {f'base: {nombre_base}': (base, False)}
    if base_rep is not None:
        series['base, repetición'] = (base_rep, False)
    for c in (CAMPO, CAMPO_REP):
        if c in filas:
            series[NOMBRES[c]] = (filas[c], True)
    primeras = {n: s for n, s in series.items() if 'repetición' not in n}

    if CAMPO in filas:
        print('### Alerta fuerte (`pedido_critico`), en C con campo\n')
        print('Pedido crítico de la referencia: el primero con código, clave, plata, acceso remoto o acción de seguridad; '
              'los datos personales no cuentan. A tiempo: en esa línea o antes.\n')
        filas_md = []
        for c in (CAMPO, CAMPO_REP):
            if c not in filas:
                continue
            ids = IDS if c == CAMPO else VISTA
            fuerte = avisos(filas[c], ids, solo_campo=True)
            con = [i for i in ESTAFAS if linea_critica(i)]
            sin = [i for i in ESTAFAS if not linea_critica(i)]
            filas_md.append([NOMBRES[c], f'{sum(fuerte[i] is not None and fuerte[i] <= linea_critica(i) for i in con)}/{len(con)}',
                             f'{sum(fuerte[i] is not None and fuerte[i] > linea_critica(i) for i in con)}',
                             f'{sum(fuerte[i] is not None for i in sin)}/{len(sin)}',
                             f'{sum(fuerte[i] is not None for i in LEGITIMAS)}/{len(LEGITIMAS)}',
                             f'{sum(fuerte[i] is not None for i in VISTA_91 if i in LEGITIMAS)}/45'])
        tabla(filas_md, ['corrida', 'estafas con pedido crítico, a tiempo', 'tarde', 'estafas sin pedido crítico',
                         'legítimas (los 140)', 'legítimas (alcance-91)'])
        fuerte = avisos(filas[CAMPO], IDS, solo_campo=True)
        print('Legítimas con alerta fuerte: ' + (', '.join(f'{i} L{fuerte[i]}' for i in LEGITIMAS if fuerte[i]) or 'ninguna') + '.\n')

    print('### Estafas sin pedido\n')
    sin_pedido = [i for i in ESTAFAS if not REF[i].get('t_r_linea')]
    print('Avisadas: ' + '; '.join(f'{n} {sum(a is not None for a in avisos(f, sin_pedido, campo=c).values())}/{len(sin_pedido)}'
                                   for n, (f, c) in primeras.items()) + '.\n')

    print('### Curva dentro del alcance, en todas las líneas\n')
    print('Cada celda: estafas (/46) · antes del pedido (/36) · a tiempo (/36) · FA (/94). C con campo suma siempre '
          '`pedido_critico`.\n')
    curvas = {n: {u: metricas(avisos(f, VISTA, u, campo=c), VISTA) for u in UMBRALES} for n, (f, c) in series.items()}
    tabla([[f'riesgo ≥ {u:g}', *(corto(cur[u]) for cur in curvas.values())] for u in UMBRALES], ['regla', *curvas])
    with open(datos / 'curva.csv', 'w', encoding='utf-8', newline='') as fcsv:
        w = csv.writer(fcsv)
        w.writerow(['serie', 'lectura', 'umbral', 'estafas', 'antes', 'en', 'fa', 'n_estafas', 'n_con_pedido', 'n_legitimas'])
        for n, (f, c) in series.items():
            for rol, lectura in ((None, 'todas'), (ROL, 'OTRA')):
                for u in UMBRALES:
                    mm = metricas(avisos(f, VISTA, u, rol=rol, campo=c), VISTA)
                    w.writerow([n, lectura, u, mm['det'], mm['antes'], mm['en'], mm['fa'], mm['n_est'], mm['n_conp'], mm['n_leg']])
    print('La curva completa, con las dos lecturas, también está en `curva.csv`.\n')

    print('### Intervalos de Wilson en la regla\n')
    filas_md = []
    for n, (f, c) in series.items():
        mm = metricas(avisos(f, VISTA, campo=c), VISTA)
        filas_md.append([n, wilson(mm['det'], mm['n_est']), wilson(mm['antes'], mm['n_conp']),
                         wilson(mm['antes'] + mm['en'], mm['n_conp']), wilson(mm['fa'], mm['n_leg'])])
    tabla(filas_md, ['serie', *ENC])

    av = {n: avisos(f, IDS, campo=c) for n, (f, c) in primeras.items()}
    print('### Estafas por primer pedido de la referencia (avisadas; antes / en / después del pedido)\n')
    filas_md = []
    for pedido in PEDIDOS:
        ids = [i for i in ESTAFAS if (REF[i].get('pedido') or 'sin pedido') == pedido]
        if not ids:
            continue
        celdas = []
        for a in av.values():
            t_r = [(a[i], REF[i]['t_r_linea']) for i in ids if a[i] is not None and REF[i].get('t_r_linea')]
            celdas.append(f'{sum(a[i] is not None for i in ids)}' + (
                f' ({sum(x < t for x, t in t_r)} / {sum(x == t for x, t in t_r)} / {sum(x > t for x, t in t_r)})'
                if pedido != 'sin pedido' else ''))
        filas_md.append([pedido, len(ids), *celdas])
    tabla(filas_md, ['primer pedido', 'estafas', *av])

    if len(av) == 2:
        a, b = av.values()
        conp = [i for i in ESTAFAS if REF[i].get('t_r_linea')]
        a_tiempo = lambda x, i: x[i] is not None and x[i] <= REF[i]['t_r_linea']  # noqa: E731
        print('### Pares discordantes entre la base y C con campo, dentro del alcance\n')
        tabla([['estafas avisadas', ', '.join(i for i in ESTAFAS if a[i] is not None and b[i] is None) or '—',
                ', '.join(i for i in ESTAFAS if b[i] is not None and a[i] is None) or '—'],
               ['avisos a tiempo', ', '.join(i for i in conp if a_tiempo(a, i) and not a_tiempo(b, i)) or '—',
                ', '.join(i for i in conp if a_tiempo(b, i) and not a_tiempo(a, i)) or '—'],
               ['FA', ', '.join(i for i in LEGITIMAS if a[i] is not None and b[i] is None) or '—',
                ', '.join(i for i in LEGITIMAS if b[i] is not None and a[i] is None) or '—']],
              ['cifra', 'solo la base', 'solo C con campo'])

    print('### FA por lote, por pedido de datos y al comienzo\n')

    def pide_datos(i):
        return any(e['evento'] == 'pedido' and 'REQUEST_PERSONAL_DATA' in e['etiquetas'] for e in REF[i].get('evidencia') or [])
    grupos = {etiqueta: leer_lista(lista) for etiqueta, lista in LOTES.items()}
    grupos['piden datos personales'] = [i for i in LEGITIMAS if pide_datos(i)]
    grupos['no piden datos personales'] = [i for i in LEGITIMAS if not pide_datos(i)]
    grupos['una por escenario, sin dudosas (alcance-91)'] = [i for i in VISTA_91 if i in LEGITIMAS]
    filas_md = [[g, len(ids), *(sum(a[i] is not None for i in ids) for a in av.values())] for g, ids in grupos.items()]
    filas_md.append(['FA en L1–L3', len(LEGITIMAS), *(sum(a[i] is not None and a[i] <= 3 for i in LEGITIMAS) for a in av.values())])
    tabla(filas_md, ['legítimas', 'llamadas', *av])

    print('### Otros grupos (estafas · antes · a tiempo · FA)\n')
    v2_todo = [i for i in IDS if REF[i]['grupo'] == 'corpus_v2']
    otros = {'dentro del alcance (los 140)': VISTA, 'alcance-91': VISTA_91,
             'corpus_v2 entero, sin alcance (46 + 51)': v2_todo,
             'las 7 legítimas de corpus_v2 dentro del alcance':
                 [i for i in v2_todo if REF[i]['clase'] != 'vishing' and ALCANCE[i] == 'dentro']}
    for g in ('laboratorio', 'piloto_escrito', 'trampa'):
        otros[f'manuales: {g}'] = [i for i in IDS if REF[i]['grupo'] == g]
    reglas = avisos_de_reglas()
    tabla([[g, *(corto(metricas(a, ids)) for a in av.values()), *(corto(metricas(r, ids)) for r in reglas.values())]
           for g, ids in otros.items()], ['grupo', *av, *(f'{n} (sin modelo)' for n in reglas)])

    print('### Corrida y repetición, dentro del alcance (ADR 0005: «para reconsiderarla, más de 2 casos»)\n')
    filas_md = []
    for nombre, c1, c2, campo in (('C sin alerta', BASE, BASE_REP, False), ('C con campo', CAMPO, CAMPO_REP, True)):
        if c1 not in filas or c2 not in filas:
            continue
        a, b = avisos(filas[c1], VISTA, campo=campo), avisos(filas[c2], VISTA, campo=campo)
        distintos = [i for i in VISTA if a[i] != b[i]]
        mueven = [i for i in distintos if fmt(metricas({i: a[i]}, [i])) != fmt(metricas({i: b[i]}, [i]))]
        pares = [(x, y) for i in VISTA for x, y in zip(filas[c1][i], filas[c2][i])]
        riesgo = sum(num(x['riesgo']) is not None and x['riesgo'] == y['riesgo'] for x, y in pares)
        campo_igual = sum(x.get('pedido_critico') == y.get('pedido_critico') for x, y in pares)
        filas_md.append([nombre, f'{len(distintos)} ({", ".join(distintos) or "—"})', f'{len(mueven)} ({", ".join(mueven) or "—"})',
                         f'{riesgo}/{len(pares)} ({100 * riesgo / len(pares):.1f} %)',
                         f'{campo_igual}/{len(pares)}' if campo else '—'])
    tabla(filas_md, ['versión', 'casos con otra línea de aviso', 'de esos, cambian una cifra', 'riesgo escrito igual',
                     '`pedido_critico` igual'])

    if BASE in filas:
        print('### C sin alerta contra C de la etapa 2, línea por línea\n')
        pares = [(x, y) for i in IDS for x, y in zip(e2_filas.get(i, []), filas[BASE].get(i, []))]
        iguales = sum(num(x['riesgo']) is not None and x['riesgo'] == y['riesgo'] for x, y in pares)
        print(f'Riesgo escrito igual en {iguales}/{len(pares)} líneas de los 244 ({100 * iguales / max(len(pares), 1):.1f} %). '
              'Entre dos corridas iguales de la etapa 2 coincidía en el 95,9 %.\n')

    latencia(filas, e2_filas)
    politica(series)
    motivo(filas)
    controles(datos)


def latencia(filas, e2_filas):
    print('### Latencia en T4 por tipo de consulta (ms de pared; p50 / p95, dentro del alcance)\n')
    fuentes = {NOMBRES[c]: f for c, f in filas.items()}
    fuentes['C de la etapa 2 (`c-json-corte`, cortado tras la alerta)'] = e2_filas
    filas_md = []
    for n, f in fuentes.items():
        todas = [r for i in VISTA for r in f.get(i, [])]
        otra = [r for r in todas if r['hablante'] == ROL]
        aviso = [r for r in todas if r['ms_etapa2']]
        filas_md.append([n, p50_p95([num(r['ms_etapa1']) for r in todas if num(r['ms_etapa1']) is not None]),
                         p50_p95([num(r['ms_etapa1']) for r in otra if num(r['ms_etapa1']) is not None]), len(otra),
                         p50_p95([num(r['tokens_salida']) for r in todas if num(r['tokens_salida']) is not None]),
                         p50_p95([num(r['tokens_prompt']) for r in todas if num(r['tokens_prompt']) is not None]),
                         p50_p95([num(r['ms_etapa2']) for r in aviso]), len(aviso)])
    tabla(filas_md, ['corrida', 'consulta de C (ms)', 'solo en líneas de OTRA (ms)', 'líneas de OTRA', 'tokens generados',
                     'tokens del prompt', 'motivo (ms)', 'motivos pedidos'])


def politica(series):
    print('### Costo por llamada de la política (simulado con las mismas salidas)\n')
    print('La política: consultar en cada línea (o solo en las de OTRA), seguir después del primer aviso, que no se '
          'apaga y muestra un texto fijo, y cortar después de la alerta fuerte, con su motivo. No cambia la detección. '
          'Cada celda: mediana / p95 de consultas y de ms por llamada; el motivo se suma si la llamada tiene alerta '
          'fuerte.\n')
    filas_md = []
    for n, (f, campo) in series.items():
        if 'repetición' in n:
            continue
        for lectura, rol in (('todas', None), ('solo OTRA', ROL)):
            for clase, ids in (('estafas', ESTAFAS), ('legítimas', LEGITIMAS)):
                consultas, ms = [], []
                for i in ids:
                    k, t = 0, 0.0
                    for r in f.get(i, []):
                        if rol is not None and r['hablante'] != rol:
                            continue
                        k += 1
                        t += num(r['ms_etapa1']) or 0.0
                        if campo and r['valida'] == 'true' and r.get('pedido_critico') == 'true':
                            break
                    t += sum(num(r['ms_etapa2']) or 0.0 for r in f.get(i, []))
                    consultas.append(k)
                    ms.append(t)
                filas_md.append([n, lectura, clase, p50_p95(consultas), p50_p95(ms)])
    tabla(filas_md, ['serie', 'líneas consultadas', 'llamadas', 'consultas', 'ms'])


def motivo(filas):
    print('### Motivo de C (medición escrita antes de correr)\n')
    print('En cada línea en que se pidió el motivo (la primera alerta fuerte de la llamada; la base no lo pide), dentro '
          'del alcance: JSON válido con motivo; evidencia textual de OTRA hasta esa línea; evidencia textual en cualquier '
          'voz; y motivos que nombran un pedido cuando la referencia todavía no marca un pedido crítico (por palabras; se '
          'leen a mano abajo).\n')
    filas_md, marcados = [], []
    for c, f in filas.items():
        aviso = [(i, r) for i in VISTA for r in f.get(i, []) if r['ms_etapa2']]
        validos = [(i, r) for i, r in aviso if not r['error'].startswith('etapa2_')]
        de_otra = sum(evidencia_en_texto(r['evidencia'], [l for l in con_roles(i)[:int(r['linea'])] if l.hablante == ROL])
                      for i, r in validos)
        cualquiera = sum(r['evidencia_en_texto'] == 'true' for _, r in validos)
        antes = [(i, r) for i, r in validos if not (linea_critica(i) and linea_critica(i) <= int(r['linea']))]
        nombran = [(i, r) for i, r in antes if PALABRAS_PEDIDO.search(r['motivo'])]
        marcados += [(c, i, r) for i, r in nombran]
        filas_md.append([NOMBRES[c], len(aviso), f'{len(validos)}/{len(aviso)}', f'{de_otra}/{len(validos)}',
                         f'{cualquiera}/{len(validos)}', f'{len(nombran)}/{len(antes)}'])
    tabla(filas_md, ['corrida', 'motivos pedidos', 'JSON válido con motivo', 'evidencia de OTRA', 'evidencia en cualquier voz',
                     'nombran un pedido antes de que ocurra (marcados)'])
    if marcados:
        print('Marcados para leer:\n')
        for c, i, r in marcados:
            print(f'- {NOMBRES[c]}, {i} L{r["linea"]} ({REF[i]["clase"]}): «{r["motivo"]}»')
        print()


def controles(datos):
    print('### Controles de ventas y préstamos (solo para mirar; L = primer aviso; F = primera alerta fuerte)\n')
    runs = [p for p in (datos / 'controles-ventas').glob('*') if (p / 'manifiesto.json').exists()] \
        if (datos / 'controles-ventas').exists() else []
    if not runs:
        print('> Falta controles-ventas/.\n')
        return
    (run,) = runs
    por_prompt = collections.defaultdict(lambda: collections.defaultdict(list))
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if r['detector'] == 'slm':
                por_prompt[r['prompt']][r['case_id']].append(r)
    for por_caso in por_prompt.values():
        for v in por_caso.values():
            v.sort(key=lambda r: int(r['linea']))
    definicion = json.loads((EXP / 'casos' / 'controles-ventas.json').read_text(encoding='utf-8'))
    columnas = {}
    for prompt, por_caso in sorted(por_prompt.items()):
        a = avisos(dict(por_caso), list(definicion))
        fuerte = avisos(dict(por_caso), list(definicion), solo_campo=True)
        columnas[prompt] = {i: ' '.join(x for x in (f'L{a[i]}' if a[i] else '–', f'F{fuerte[i]}' if fuerte[i] else '') if x)
                            for i in definicion}
    tabla([[i, c['clase'], c['alcance'], c['que_prueba'], *(col[i] for col in columnas.values())]
           for i, c in definicion.items()], ['control', 'clase', 'alcance', 'qué prueba', *columnas])


if __name__ == '__main__':
    sys.exit(main())
