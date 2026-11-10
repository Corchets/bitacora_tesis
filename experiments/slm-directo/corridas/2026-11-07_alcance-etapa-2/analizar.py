"""#143, segunda vuelta, etapa 2: el prompt C y v4-premisa contra v4 dentro del alcance, con el JSON cortado.

No corre modelos ni lee la reserva; solo biblioteca estándar y el código del laboratorio (casos, reglas). Uso, desde
esta carpeta, con los ZIP de Colab descomprimidos acá (humo/, v4-corte/, c-json-corte/, c-json-corte-rep/,
v4-premisa-corte/, v4-premisa-corte-rep/ y controles-ventas/):
    python -I analizar.py                       # todo
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Escrito el 2026-11-07, antes de correr. Decisiones de Mateo (2026-11-07):
- Configuraciones, todas con el JSON cortado después de `alerta_sugerida` y el motivo aparte (ADR 0006):
  `v4-corte` de referencia, y `c-json-corte` y `v4-premisa-corte` como candidatas.
- Repetición (ADR 0005): dos corridas por candidata; la primera sobre los 244 de desarrollo y la repetición solo sobre
  los 140 dentro del alcance (casos/listas/alcance-140.txt).
- Límite de FA: no hay uno fijo; se informa la curva. La meta 80/15 no es criterio.

Cómo decide la curva (README.md de esta carpeta; confirmado por Mateo el 2026-11-07, antes de correr):
- Vista: dentro del alcance, las 46 estafas de corpus_v2 (36 con pedido) y las 94 legítimas entrantes de #155.
- Curva de cada configuración: «alerta sola» y «riesgo ≥ u o alerta» con u = 0,1…1,0, sobre el riesgo y la alerta
  que escribe el modelo (columna `alerta_escrita`). Cada regla da estafas avisadas, avisos antes del pedido
  (T_A < T_R) y FA.
- Punto de comparación: F = FA de v4-corte (primera corrida) con «riesgo ≥ 0,4 o alerta», su regla adoptada. Cada
  configuración, v4-corte incluida, toma la regla con FA ≤ F que avisa más estafas; desempates: más avisos antes del
  pedido, menos FA y el umbral más cercano a 0,4.
- Regla de #143 contra v4-corte en ese punto: la candidata se prefiere con 3 estafas más o 3 avisos más antes del
  pedido, sin perder 3 o más en la otra cifra. Si gana en una y pierde 3 o más en la otra, no se adopta y decide el
  equipo. Dentro de ±2 en las dos, queda v4-corte; la latencia se informa.
- Repetición (aclaraciones de Mateo, 2026-11-07): no vuelve a elegir el umbral. Usa la misma regla (el mismo u) que
  eligió la candidata en su primera corrida, porque el punto elegido tiene que sostenerse (ADR 0005). Con esa regla
  cumple la misma condición completa que la primera corrida: +3 contra v4-corte en una cifra en que ganó la primera
  (si ganó en las dos, alcanza con una), sin perder 3 o más en la otra, y con FA ≤ F + 2. Si gana en una y pierde 3 o
  más en la otra, no se adopta y decide el equipo. Si no, no cuenta.
- Si cuentan las dos: la de más estafas, después más avisos antes y menos FA; si entre ellas quedan dentro de ±2 en las
  dos cifras, v4-premisa, que es el cambio más chico.
Aparte, solo para mirar: la misma comparación con FA = 0, 4, 9 y 14 (0, 5, 10 y 15 % de las 94); la detección útil
(T_A ≤ T_R) e intervalos de Wilson; las estafas sin pedido y las 6 que piden un dato; las 7 legítimas de corpus_v2
dentro del alcance; corpus_v2 sin alcance; los manuales; las legítimas por lote (sesgo del DNI, R29, #154); las reglas
v1 y v2; los controles de ventas; la latencia y la diferencia entre corrida y repetición.
"""
import argparse, collections, csv, functools, json, math, statistics, sys
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import casos  # noqa: E402
from detectores import (CORTE_DE, ESQUEMA_MOTIVO, ESQUEMA_SALIDA, MAXIMO_TOKENS_CORTE, PROMPT_MOTIVO_CORTE,  # noqa: E402
                        DetectorReglas, cargar_prompt, cargar_prompt_motivo, huella)

MARGEN = 3          # +3 estafas o +3 avisos antes del pedido; ±2 es ruido (ADR 0005)
RUIDO_FA = 2        # la repetición puede tener hasta F + 2 FA
UMBRAL_REFERENCIA = 0.4  # la regla adoptada de v4-corte: «riesgo ≥ 0,4 o alerta» (ADR 0006)
UMBRALES = [round(x / 10, 1) for x in range(1, 11)]
REGLAS = ['alerta sola'] + [f'riesgo ≥ {u:g} o alerta' for u in UMBRALES]
NIVELES_MIRAR = (0, 4, 9, 14)  # 0, 5, 10 y 15 % de las 94, solo para mirar
OLLAMA = '0.40.14'
DIGEST = 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2'
CORRIDAS = {  # carpeta: (prompt, lista; None = los 244)
    'v4-corte': ('v4-corte', None),
    'c-json-corte': ('c-json-corte', None),
    'c-json-corte-rep': ('c-json-corte', 'alcance-140'),
    'v4-premisa-corte': ('v4-premisa-corte', None),
    'v4-premisa-corte-rep': ('v4-premisa-corte', 'alcance-140'),
}
REFERENCIA = 'v4-corte'
CANDIDATAS = {'C': ('c-json-corte', 'c-json-corte-rep'), 'v4-premisa': ('v4-premisa-corte', 'v4-premisa-corte-rep')}
CAMBIO_MAS_CHICO = 'v4-premisa'
ALCANCES = [EXP / 'casos' / 'alcance-desarrollo.json', EXP / 'casos' / 'alcance-legitimas-cotidianas.json']
LOTES = {'LEG (21)': 'legitimas-leg-21', 'LEG2 (28)': 'legitimas-leg2-28', 'ENT-L (42)': 'legitimas-ent-l-42',
         'selección (3)': 'legitimas-seleccion-3'}
DATOS_ESTAFAS = ['CV2-D-V-ORGANISMO_PREVISIONAL-001', 'CV2-D-V-ORGANISMO_PREVISIONAL-002', 'CV2-D-V-ORGANISMO_PREVISIONAL-003',
                 'CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-V-PREMIO-001', 'CV2-D-V-PREMIO-003']


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


# --- Corridas ---
def leer(datos, carpeta):
    """(filas por caso, manifiesto) de la única corrida en datos/carpeta, o None si falta."""
    runs = [p for p in (datos / carpeta).glob('*') if (p / 'manifiesto.json').exists()] if (datos / carpeta).exists() else []
    if not runs:
        return None
    (run,) = runs
    filas = collections.defaultdict(list)
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            if r['detector'] == 'slm':
                filas[r['case_id']].append(r)
    for v in filas.values():
        v.sort(key=lambda r: int(r['linea']))
    return dict(filas), json.loads((run / 'manifiesto.json').read_text(encoding='utf-8'))


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
    if man['ollama']['version'] != OLLAMA or man['ollama']['digests'].get('gemma4:e2b-it-q4_K_M', '').removeprefix('sha256:') != DIGEST:
        problemas.append('Ollama o digest distinto')
    ps = man['parametros_slm']
    if (ps['num_ctx'], ps['seed'], ps['temperatura']) != (4096, 42, 0.0):
        problemas.append('num_ctx, seed o temperatura distintos')
    if ps.get('json_cortado', {}).get('num_predict') != MAXIMO_TOKENS_CORTE:
        problemas.append('no es el JSON cortado')
    p = man['prompts'].get(prompt, {})
    if (p.get('texto'), p.get('esquema')) != (cargar_prompt(CORTE_DE[prompt]), ESQUEMA_SALIDA):
        problemas.append(f'el prompt no es el de {CORTE_DE[prompt]}')
    if (p.get('etapa2', {}).get('texto'), p.get('etapa2', {}).get('esquema')) != (cargar_prompt_motivo(PROMPT_MOTIVO_CORTE), ESQUEMA_MOTIVO):
        problemas.append('la segunda consulta no es motivo_v4_corte.txt')
    if man['modo_termino'] != 'diagnostico-completo' or man['interrumpida']:
        problemas.append('no corrió entera en todas las líneas')
    for i in filas:
        if [int(r['linea']) for r in filas[i]] != list(range(1, len(casos.cargar_texto(i)) + 1)) \
                or {r['prompt'] for r in filas[i]} != {prompt} or {r['hablantes'] for r in filas[i]} != {'rol'}:
            problemas.append(f'{i}: líneas, prompt o hablantes distintos')
            break
    todas = [r for v in filas.values() for r in v]
    invalidas = collections.Counter(r['error'] for r in todas if r['valida'] != 'true')
    ms = [num(r['ms_etapa1']) for r in todas if num(r['ms_etapa1']) is not None]
    fila = [carpeta, len(filas), len(todas), f'{sum(invalidas.values())} {dict(invalidas) or ""}'.strip(), p50_p95(ms),
            man['codigo']['commit'][:10] + (' (con cambios)' if man['codigo'].get('cambios_sin_commit_en_la_carpeta') else '')]
    if man['codigo'].get('cambios_sin_commit_en_la_carpeta'):
        problemas.append('corrió con cambios sin commitear')
    return problemas, fila


# --- Reglas y métricas ---
def umbral_de(regla):
    return None if regla == 'alerta sola' else float(regla.split('≥ ')[1].split(' ')[0])


def avisos(filas, regla, ids):
    """case_id → primera línea en que dispara la regla (None si no dispara). Las líneas inválidas no avisan."""
    u = umbral_de(regla)
    salida = {}
    for i in ids:
        salida[i] = next((int(r['linea']) for r in filas.get(i, []) if r['valida'] == 'true' and (
            r['alerta_escrita'] == 'true' or (u is not None and num(r['riesgo']) is not None and num(r['riesgo']) >= u - 1e-9))), None)
    return salida


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


ENC = ['estafas', 'antes del pedido', 'antes o en el pedido', 'FA']


def corto(m):
    """«estafas · antes · FA», sin las partes que no tienen casos."""
    partes = []
    if m['n_est']:
        partes.append(f"{m['det']}/{m['n_est']}")
        partes.append(f"{m['antes']}/{m['n_conp']}" if m['n_conp'] else '–')
    if m['n_leg']:
        partes.append(f"FA {m['fa']}/{m['n_leg']}")
    return ' · '.join(partes)


@functools.cache
def avisos_de_reglas():
    """Primer aviso de las reglas v1 y v2 del laboratorio en los 244. Miran solo la línea nueva y corren sin modelo."""
    textos, salida = {i: casos.cargar_texto(i) for i in IDS}, {}
    for version in ('v1', 'v2'):
        d = DetectorReglas(version)
        salida[d.nombre] = {i: next((n for n in range(1, len(t) + 1) if d.evaluar(t[:n]).alerta_sugerida), None)
                            for i, t in textos.items()}
    return salida


def curva(filas):
    return {regla: metricas(avisos(filas, regla, VISTA), VISTA) for regla in REGLAS}


def punto(cur, fa_max):
    """La regla con FA ≤ fa_max que avisa más estafas; desempates: más antes, menos FA, umbral más cerca de 0,4."""
    ok = [(regla, m) for regla, m in cur.items() if m['fa'] <= fa_max]
    if not ok:
        return None
    return max(ok, key=lambda rm: (rm[1]['det'], rm[1]['antes'], -rm[1]['fa'],
                                   -abs((umbral_de(rm[0]) if umbral_de(rm[0]) is not None else 1.1) - UMBRAL_REFERENCIA)))


def comparar(m, ref):
    """Regla de #143: 'gana' / 'pierde' / 'mixto' / 'ruido', y las cifras en que gana."""
    d = {'estafas': m['det'] - ref['det'], 'antes': m['antes'] - ref['antes']}
    gana = [c for c, x in d.items() if x >= MARGEN]
    pierde = [c for c, x in d.items() if x <= -MARGEN]
    estado = 'mixto' if gana and pierde else 'gana' if gana else 'pierde' if pierde else 'ruido'
    return estado, gana, d


def texto_dif(d):
    return f"{d['estafas']:+d} estafas, {d['antes']:+d} avisos antes del pedido"


# --- Informe ---
def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    datos = p.parse_args(argv).datos.resolve()
    print('# #143, segunda vuelta, etapa 2: C y v4-premisa contra v4 dentro del alcance — análisis offline\n')
    print(f'Vista dentro del alcance: {len(ESTAFAS)} estafas de corpus_v2 '
          f'({sum(1 for i in ESTAFAS if REF[i].get("t_r_linea"))} con pedido) y {len(LEGITIMAS)} legítimas entrantes.\n')

    if (datos / 'humo' / 'humo.json').exists():
        h = json.loads((datos / 'humo' / 'humo.json').read_text(encoding='utf-8'))
        print('## Humo de formato\n')
        tabla([[f'`{prompt}`', f"{d['tokens_hasta_alerta']['min']} / {d['tokens_hasta_alerta']['mediana']} / "
                f"{d['tokens_hasta_alerta']['max']}", f"{d['alcanzan']}/{d['lineas']}",
                f"{d['cortado_leidas']}/{d['cortado_lineas']}", f"{d['iguales_al_completo']}/{d['lineas']}",
                'PASA' if d['pasa'] else 'NO PASA'] for prompt, d in h.items()],
              ['prompt', 'tokens hasta la alerta (mín / mediana / máx)', 'alcanzan', 'cortado leídas',
               'mismo riesgo y alerta que el completo (dato)', 'resultado'])

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
    malos = {c: x for c, x in problemas.items() if x}
    if malos:
        for c, x in malos.items():
            print(f'- **{c}:** {"; ".join(x)}')
        print('\n**Hay problemas de control: no se aplica la regla.**\n')
        return 1
    print('Sin problemas de control: mismo commit, digest, Ollama, parámetros, prompts y casos.\n')
    if REFERENCIA not in leidas:
        print('**Falta la referencia (v4-corte): no se aplica la regla.**\n')
        return 1

    filas = {c: f for c, (f, _) in leidas.items()}
    curvas = {c: curva(f) for c, f in filas.items()}
    print('## Curva dentro del alcance\n')
    reglas_fijas = avisos_de_reglas()
    print('Cada celda: estafas (/46) · avisos antes del pedido (/36) · FA (/94).\n')
    tabla([[regla, *(corto(cur[regla]) for cur in curvas.values())] for regla in REGLAS], ['regla', *curvas])
    print('Reglas del laboratorio, sin modelo: ' +
          '; '.join(f'{nombre} {corto(metricas(av, VISTA))}' for nombre, av in reglas_fijas.items()) + '.\n')
    with open(datos / 'curva.csv', 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['corrida', 'regla', 'umbral', 'estafas', 'antes', 'en', 'fa', 'n_estafas', 'n_con_pedido', 'n_legitimas'])
        for c, cur in curvas.items():
            for regla, m in cur.items():
                w.writerow([c, regla, umbral_de(regla) if umbral_de(regla) is not None else '', m['det'], m['antes'], m['en'],
                            m['fa'], m['n_est'], m['n_conp'], m['n_leg']])
    print('La curva completa también está en `curva.csv`.\n')

    # Punto de comparación y regla de #143.
    ref_adoptada = curvas[REFERENCIA][f'riesgo ≥ {UMBRAL_REFERENCIA:g} o alerta']
    F = ref_adoptada['fa']
    print('## Regla de #143\n')
    print(f'Punto de comparación: v4-corte con su regla adoptada («riesgo ≥ 0,4 o alerta») tiene F = {F}/94 FA. '
          f'Cada configuración usa su regla con FA ≤ {F} que avisa más estafas.\n')
    regla_ref, ref = punto(curvas[REFERENCIA], F)
    puntos = {REFERENCIA: (regla_ref, ref)}
    filas_md = [['v4-corte (referencia)', regla_ref, *fmt(ref), '—', '—']]
    cuentan = []
    for nombre, (carpeta, rep) in CANDIDATAS.items():
        if carpeta not in curvas:
            filas_md.append([nombre, 'falta la corrida', '', '', '', '', '', 'no cuenta'])
            continue
        elegido = punto(curvas[carpeta], F)
        if elegido is None:
            filas_md.append([nombre, f'ninguna regla con FA ≤ {F}', '', '', '', '', '', 'no se adopta'])
            continue
        regla, m = elegido
        puntos[carpeta] = elegido
        estado, gana, d = comparar(m, ref)
        if estado == 'mixto':
            veredicto = 'gana en una cifra y pierde 3 o más en la otra: no se adopta, decide el equipo'
        elif estado == 'pierde':
            veredicto = 'no se adopta (pierde 3 o más)'
        elif estado == 'ruido':
            veredicto = 'dentro de ±2: queda v4-corte'
        elif rep not in curvas:
            veredicto = 'gana, pero falta la repetición: no cuenta'
        else:
            mr = curvas[rep][regla]
            estado_r, gana_r, d_r = comparar(mr, ref)
            # La misma regla de la primera corrida y la misma condición completa: +3 en una cifra en que ganó la
            # primera, sin perder 3 o más en la otra, y FA ≤ F + 2.
            se_sostiene = estado_r == 'gana' and bool(set(gana) & set(gana_r)) and mr['fa'] <= F + RUIDO_FA
            rep_txt = f'{texto_dif(d_r)}, FA {mr["fa"]}'
            if se_sostiene:
                veredicto = f'gana ({", ".join(gana)}) y la repetición lo sostiene ({rep_txt}): cuenta'
            elif estado_r == 'mixto':
                veredicto = (f'gana ({", ".join(gana)}), pero la repetición pierde 3 o más en una cifra ({rep_txt}): '
                             'no se adopta, decide el equipo')
            else:
                veredicto = f'gana ({", ".join(gana)}), pero la repetición no lo sostiene ({rep_txt}): no cuenta'
            if se_sostiene:
                cuentan.append((nombre, m))
        filas_md.append([nombre, regla, *fmt(m), texto_dif(d), veredicto])
    tabla(filas_md, ['configuración', 'regla', *ENC, 'contra v4-corte', 'veredicto'])

    if not cuentan:
        print('**Ninguna candidata cuenta: queda v4-corte.**\n')
    else:
        cuentan.sort(key=lambda nm: (nm[1]['det'], nm[1]['antes'], -nm[1]['fa']), reverse=True)
        ganadora = cuentan[0][0]
        if len(cuentan) == 2:
            a, b = (m for _, m in cuentan)
            if abs(a['det'] - b['det']) < MARGEN and abs(a['antes'] - b['antes']) < MARGEN:
                ganadora = CAMBIO_MAS_CHICO
                print('Cuentan las dos y quedan dentro de ±2 entre ellas: se elige v4-premisa, el cambio más chico.\n')
        print(f'**Se adopta {ganadora}, provisorio hasta la reserva.**\n')

    aparte(filas, curvas, puntos, F, reglas_fijas, datos)
    return 0


def aparte(filas, curvas, puntos, F, reglas_fijas, datos):
    print('## Aparte, solo para mirar\n')
    print('### La misma comparación con otros niveles de FA (no decide)\n')
    filas_md = []
    for nivel in NIVELES_MIRAR:
        ref = punto(curvas[REFERENCIA], nivel)
        for c in curvas:
            if c.endswith('-rep'):
                continue
            e = punto(curvas[c], nivel)
            if e is None:
                filas_md.append([nivel, c, 'ninguna', '', '', '', '', ''])
                continue
            dif = '—' if c == REFERENCIA or ref is None else texto_dif(comparar(e[1], ref[1])[2])
            filas_md.append([nivel, c, e[0], *fmt(e[1]), dif])
    tabla(filas_md, ['FA máx.', 'corrida', 'regla', *ENC, 'contra v4-corte'])

    print('### Intervalos de Wilson en el punto de comparación\n')
    filas_md = []
    for c, (regla, m) in puntos.items():
        filas_md.append([c, regla, wilson(m['det'], m['n_est']), wilson(m['antes'], m['n_conp']),
                         wilson(m['antes'] + m['en'], m['n_conp']), wilson(m['fa'], m['n_leg'])])
    tabla(filas_md, ['corrida', 'regla', 'estafas', 'antes del pedido', 'detección útil (antes o en el pedido)', 'FA'])

    av_punto = {c: avisos(filas[c], regla, IDS) for c, (regla, _) in puntos.items()}
    av_punto.update(reglas_fijas)
    av_04 = {c: avisos(f, f'riesgo ≥ {UMBRAL_REFERENCIA:g} o alerta', IDS) for c, f in filas.items() if not c.endswith('-rep')}

    print('### Estafas sin pedido y estafas que piden un dato (L = línea del primer aviso; – sin aviso)\n')
    sin_pedido = [i for i in ESTAFAS if not REF[i].get('t_r_linea')]
    print('Estafas sin pedido avisadas en el punto de comparación: ' +
          '; '.join(f'{c} {sum(av[i] is not None for i in sin_pedido)}/{len(sin_pedido)}' for c, av in av_punto.items()) + '.\n')
    tabla([[i, f"T_R {REF[i].get('t_r_linea') or '–'}", *[('L' + str(av[i])) if av[i] else '–' for av in av_punto.values()]]
           for i in DATOS_ESTAFAS], ['caso', 'pedido', *av_punto])

    print('### Otros grupos, en el punto de comparación y con «riesgo ≥ 0,4 o alerta»\n')
    v2_todo = [i for i in IDS if REF[i]['grupo'] == 'corpus_v2']
    leg_v2_dentro = [i for i in v2_todo if REF[i]['clase'] != 'vishing' and ALCANCE[i] == 'dentro']
    grupos = {'corpus_v2 entero, sin alcance (46 + 51)': v2_todo,
              'las 7 legítimas de corpus_v2 dentro del alcance': leg_v2_dentro}
    for g in ('laboratorio', 'piloto_escrito', 'trampa'):
        grupos[f'manuales: {g}'] = [i for i in IDS if REF[i]['grupo'] == g]
    for etiqueta, lista in LOTES.items():
        grupos[f'legítimas por lote: {etiqueta}'] = leer_lista(lista)
    print('Cada celda: estafas · avisos antes del pedido · FA. Las reglas del laboratorio no tienen umbral.\n')
    filas_md = []
    for nombre_g, ids_g in grupos.items():
        for c, av in av_punto.items():
            filas_md.append([nombre_g, c, corto(metricas(av, ids_g)), corto(metricas(av_04[c], ids_g)) if c in av_04 else '—'])
    tabla(filas_md, ['grupo', 'corrida', 'en el punto de comparación', 'con «riesgo ≥ 0,4 o alerta»'])

    print('### Corrida y repetición, dentro del alcance (ADR 0005: «para reconsiderarla, más de 2 casos»)\n')
    filas_md = []
    for nombre, (carpeta, rep) in CANDIDATAS.items():
        if carpeta not in filas or rep not in filas:
            continue
        regla = puntos[carpeta][0] if carpeta in puntos else f'riesgo ≥ {UMBRAL_REFERENCIA:g} o alerta'
        a, b = avisos(filas[carpeta], regla, VISTA), avisos(filas[rep], regla, VISTA)
        pares = [(num(x['riesgo']), num(y['riesgo'])) for i in VISTA for x, y in zip(filas[carpeta][i], filas[rep][i])]
        iguales = sum(x is not None and x == y for x, y in pares)
        filas_md.append([nombre, regla, *fmt(metricas(a, VISTA)), *fmt(metricas(b, VISTA)),
                         sum(a[i] != b[i] for i in VISTA), f'{iguales}/{len(pares)} ({100 * iguales / len(pares):.1f} %)'])
    tabla(filas_md, ['candidata', 'regla', *[f'{e} (corrida)' for e in ENC], *[f'{e} (repetición)' for e in ENC],
                     'casos con otra línea de aviso', 'riesgo escrito igual'])

    print('### Latencia en T4 (ms de pared; p50 / p95)\n')
    filas_md = []
    for c, f in filas.items():
        todas = [r for i in VISTA for r in f[i]]
        aviso = [r for r in todas if r['ms_etapa2']]
        filas_md.append([c, p50_p95([num(r['ms_etapa1']) for r in todas if num(r['ms_etapa1']) is not None]),
                         p50_p95([num(r['tokens_prompt']) for r in todas if num(r['tokens_prompt']) is not None]),
                         p50_p95([num(r['ms_etapa2']) for r in aviso]), len(aviso),
                         sum(1 for r in aviso if r['error'].startswith('etapa2_'))])
    tabla(filas_md, ['corrida', 'primera consulta (ms)', 'tokens del prompt', 'segunda consulta (ms)',
                     'líneas con segunda consulta', 'fallos de la segunda'])

    controles(datos, puntos)


def controles(datos, puntos):
    print('### Controles de ventas y préstamos (solo para mirar)\n')
    runs = [p for p in (datos / 'controles-ventas').glob('*') if (p / 'manifiesto.json').exists()]
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
    for carpeta, (regla, _) in puntos.items():
        prompt = CORRIDAS[carpeta][0]
        if prompt in por_prompt:
            columnas[f'{carpeta} ({regla})'] = avisos(por_prompt[prompt], regla, list(definicion))
    tabla([[i, c['clase'], c['alcance'], c['que_prueba']] + [('L' + str(av[i])) if av[i] else '–' for av in columnas.values()]
           for i, c in definicion.items()], ['control', 'clase', 'alcance', 'qué prueba', *columnas])


if __name__ == '__main__':
    sys.exit(main())
