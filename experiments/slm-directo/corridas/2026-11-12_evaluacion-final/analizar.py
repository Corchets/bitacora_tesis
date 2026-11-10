"""#143, evaluación final: la configuración congelada y las referencias simples sobre desarrollo, el test reservado y
el set externo (#144), una sola vez.

No corre modelos; solo biblioteca estándar y el código del laboratorio. Uso, desde esta carpeta, con los ZIP de Colab
descomprimidos acá (conjuntos/, humo/, desarrollo/, test_reservado/ y, si corrió, externo/):
    python -I analizar.py                                     # todo
    python -I analizar.py --anotacion-legitimas RUTA.json     # además, las cifras con la anotación alternativa
    python -I analizar.py --motivos                           # además, los motivos de las FA (texto del modelo)
    python -I analizar.py --datos OTRA_CARPETA --conjuntos OTRA  # corridas y conjuntos en otro lado (pruebas)

Escrito el 2026-11-10, antes de correr. Los criterios son los de README.md («Criterios, escritos antes de correr»), que
es un borrador: decide Mateo, y los números de CRITERIOS se cambian antes del tag, nunca después.
- En cada conjunto, la vista principal es la de referencia.json (conjuntos.py): alcance-140 en desarrollo; las 100
  estafas CV2-T-V y las 56 legítimas ENT-T en el test; las estafas que la custodia deja en la vista en #144.
- La configuración avisa en la primera línea de OTRA con «riesgo ≥ 0,3» (solo OTRA, modo operativo); v4 sin alcance
  (`v4-corte`), en la primera línea con «riesgo ≥ 0,4 o alerta» (todas las líneas); las reglas, en la primera línea
  con un patrón. Las líneas inválidas no avisan.
- Cifras: estafas avisadas; antes del pedido (T_A < T_R); a tiempo, la detección útil (T_A ≤ T_R); antes del
  cumplimiento (T_A < T_C); FA, en total y por `tipo_legitima`. Intervalos de Wilson al 95 %. McNemar exacto con los
  pares discordantes, la configuración contra cada referencia, en los mismos casos.
- Con --anotacion-legitimas, todo lo de la vista principal se informa también con esa anotación, aparte.
"""

import argparse, collections, csv, importlib.util, json, math, sys
from pathlib import Path

csv.field_size_limit(10**9)
AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import casos  # noqa: E402
import conjuntos  # noqa: E402
from detectores import (ESQUEMA_MOTIVO, MAXIMO_TOKENS_CORTE, MAXIMO_TOKENS_CORTE_RIESGO, PROMPT_MOTIVO_C,  # noqa: E402
                        PROMPT_MOTIVO_CORTE, PROMPTS_CORTE, PROMPTS_CORTE_RIESGO, UMBRAL_C, UMBRAL_CORTE, cargar_prompt,
                        cargar_prompt_motivo, esquema_de, huella)


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# La humo trae la etapa 3 (tablas, Wilson, la regla de avisos, Ollama y digest); el diagnóstico de la etapa 3, el
# McNemar exacto. Se usan tal cual.
h = _cargar('analizar_humo', AQUI.parent / '2026-11-10_config-congelada-humo' / 'analizar.py')
e3 = h.e3
mcnemar = _cargar('diagnostico_etapa_3', AQUI.parent / '2026-11-09_pedido-critico-etapa-3' / 'diagnostico.py').mcnemar
num, tabla, wilson, p50_p95, celda = e3.num, e3.tabla, e3.wilson, e3.p50_p95, h.celda

CONFIG = 'c-premisa-corte-riesgo'  # la congelada (PR #171); --config si la revisión de producto elige otra antes del tag
V4 = 'v4-corte'                    # v4 sin alcance, cortado tras la alerta (ADR 0006), en todas las líneas
CONJUNTOS = ['desarrollo', 'test_reservado', 'externo']
NOMBRES = {'desarrollo': 'Desarrollo', 'test_reservado': 'Test reservado', 'externo': 'Set externo (#144)'}
CARPETAS = ['config', 'v4', 'reglas']
REGLAS = {'reglas v1': 'reglas', 'reglas v2': 'reglas_v2'}  # nombre → `config` en el CSV
REFERENCIAS = [V4, 'reglas v1']    # las de los criterios; reglas v2 se informa
PRINCIPAL = conjuntos.PRINCIPAL
TOLERANCIA = 2                     # ±2 es ruido (ADR 0005)
MAXIMO_INVALIDAS = 0.01
# Cada configuración candidata, sobre desarrollo (alcance-140), ya medida: el control de reproducibilidad del Colab
# antes de tocar el test. Una configuración nueva entra acá con sus cifras de desarrollo antes del tag.
CIFRAS_DESARROLLO = {
    'c-premisa-corte-riesgo': {'estafas': 40, 'antes del pedido': 19, 'a tiempo': 29, 'FA': 26},  # sensibilidad
    'c-json-corte-riesgo': {'estafas': 36, 'antes del pedido': 14, 'a tiempo': 26, 'FA': 25},     # humo
}
# Borrador de los criterios (README.md). Estado: propuesta sin discutir; decide Mateo antes del tag.
CRITERIOS = {
    'margen': 3,            # pares discordantes de más a favor de la configuración (ADR 0005)
    'p': 0.05,              # McNemar exacto, dos colas
    'piso_a_tiempo': 0.50,  # límite inferior de Wilson de la detección útil en el test
    'piso_estafas': 0.50,   # límite inferior de Wilson de las estafas avisadas en el test
    'caida_externo': 0.20,  # cuánto puede caer la detección del externo respecto de la del test
}
TIPOS = ['cotidiana', 'pedido_razonable', 'mencion_sin_pedido']
CIFRAS = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA', *(f'FA {t}' for t in TIPOS)]
COMPARADAS = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA']
VOLUMENES = [1, 3, 5, 10, 20]      # llamadas entrantes de números desconocidos por semana
SEMANAS_POR_MES = 52 / 12
CAMPOS_ANOTACION = {'clase', 'tipo_legitima', 'vista', 't_r_linea', 't_c_linea', 'pedido'}
# etiquetas-producto.json de la revisión de producto (corridas/2026-11-10_revision-producto/, rama
# exp/143-revision-producto): solo cuentan como FA las «no_avisar»; las otras dos pasan a una vista aparte.
ETIQUETAS_PRODUCTO = {'no_avisar': None, 'tolerable': 'aparte: tolerable (revisión de producto)',
                      'avisar': 'aparte: debería avisar (revisión de producto)'}


# --- Lectura ---
def leer(carpeta):
    """(filas por `config` y caso, manifiesto) de la única corrida en `carpeta`, o None si falta."""
    runs = [p for p in carpeta.glob('*') if (p / 'manifiesto.json').exists()] if carpeta.exists() else []
    if not runs:
        return None
    if len(runs) > 1:
        raise ValueError(f'{carpeta}: hay más de una corrida')
    filas = collections.defaultdict(dict)
    with open(runs[0] / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        for r in csv.DictReader(f):
            filas[r['config']].setdefault(r['case_id'], []).append(r)
    for por_caso in filas.values():
        for v in por_caso.values():
            v.sort(key=lambda r: int(r['linea']))
    return dict(filas), json.loads((runs[0] / 'manifiesto.json').read_text(encoding='utf-8'))


def avisos_config(filas, ids):
    return e3.avisos(filas, ids, u=UMBRAL_C, rol='OTRA', campo=False, alerta=False)


def avisos_v4(filas, ids):
    return e3.avisos(filas, ids, u=UMBRAL_CORTE, rol=None, campo=False, alerta=True)


def avisos_reglas(filas, ids):
    return {i: next((int(r['linea']) for r in filas.get(i, []) if r['valida'] == 'true' and r['alerta_sugerida'] == 'true'),
                    None) for i in ids}


def registrados(filas, ids):
    return {i: next((int(r['linea']) for r in filas.get(i, []) if r['aviso'] == 'true'), None) for i in ids}


def series(carpeta, config):
    """[(nombre, prompt, regla de aviso)] de cada detector que corre en la carpeta."""
    return {'config': [('config', config, avisos_config)], 'v4': [(V4, V4, avisos_v4)],
            'reglas': [(n, None, avisos_reglas) for n in REGLAS]}[carpeta]


def filas_de(por_config, man, nombre, prompt):
    """Las filas del detector `nombre` de una corrida, por caso ({} si no está)."""
    if prompt is None:
        return por_config.get(REGLAS[nombre], {})
    claves = [c['config'] for c in man.get('configs', []) if c['detector'] == 'slm' and c['prompt'] == prompt]
    return por_config.get(claves[0], {}) if len(claves) == 1 else {}


# --- Control ---
def controlar(carpeta, conj, por_config, man, config):
    """Problemas de una corrida (lista vacía si está bien): el conjunto entero, sin tocar, con la configuración pedida."""
    problemas, ids = [], conj.ids
    if sorted(man.get('casos', {})) != ids:
        problemas.append('no son los casos del conjunto')
    elif any(man['casos'][i] != huella(conj.crudo(i)) for i in ids):
        problemas.append('el texto de algún caso no es el del conjunto')
    datos_conj = man.get('conjunto') or {}
    if man.get('particion') != conj.particion or datos_conj.get('nombre') != conj.nombre \
            or datos_conj.get('conjunto_sha256') != conjuntos.sha256((conj.carpeta / 'conjunto.json').read_bytes()):
        problemas.append(f'no corrió sobre el conjunto {conj.nombre} armado')
    if man.get('modo_termino') != 'operativo-hasta-aviso' or man.get('interrumpida') or not man.get('fin'):
        problemas.append('no corrió entera en modo operativo')
    if man.get('codigo', {}).get('cambios_sin_commit_en_la_carpeta'):
        problemas.append('corrió con cambios sin commitear')
    slm = carpeta != 'reglas'
    esperadas = ([('slm', config if carpeta == 'config' else V4, 'rol')] if slm else
                 [('reglas', '', '')] * len(REGLAS))
    if sorted((c['detector'], c['prompt'], c['hablantes']) for c in man.get('configs', [])) != sorted(esperadas):
        problemas.append('los detectores no son los esperados')
    if not slm and sorted(c['config'] for c in man.get('configs', [])) != sorted(REGLAS.values()):
        problemas.append('no son las reglas v1 y v2')
    if man.get('solo_otra') is not (carpeta == 'config'):
        problemas.append('«solo OTRA» tiene que ir solo con la configuración')
    if slm:
        if man['ollama']['version'] != e3.OLLAMA or (man['ollama']['digests'].get(e3.MODELO) or '').removeprefix('sha256:') != e3.DIGEST:
            problemas.append('Ollama o digest distinto')
        ps = man['parametros_slm']
        if (ps['num_ctx'], ps['seed'], ps['temperatura']) != (4096, 42, 0.0):
            problemas.append('num_ctx, seed o temperatura distintos')
        prompt = config if carpeta == 'config' else V4
        motivo = PROMPT_MOTIVO_C if carpeta == 'config' else PROMPT_MOTIVO_CORTE
        corte = ('corte_riesgo', MAXIMO_TOKENS_CORTE_RIESGO) if carpeta == 'config' else ('json_cortado', MAXIMO_TOKENS_CORTE)
        p = man['prompts'].get(prompt, {})
        if list(man['prompts']) != [prompt] or (p.get('texto'), p.get('esquema')) != (cargar_prompt(prompt), esquema_de(prompt)):
            problemas.append(f'el prompt no es el de {prompt}')
        if (p.get('etapa2', {}).get('texto'), p.get('etapa2', {}).get('esquema')) != (cargar_prompt_motivo(motivo), ESQUEMA_MOTIVO):
            problemas.append(f'la segunda consulta no es {motivo}')
        if ps.get(corte[0], {}).get('num_predict') != corte[1]:
            problemas.append(f'el corte no es el de {prompt}')
    for nombre, prompt, regla in series(carpeta, config):
        filas = filas_de(por_config, man, nombre, prompt)
        if sorted(filas) != ids:
            problemas.append(f'{nombre}: faltan casos en el CSV')
            continue
        for i in ids:
            lineas, propias = conj.cargar_texto(i), filas[i]
            marcados = [int(r['linea']) for r in propias if r['aviso'] == 'true']
            fin = marcados[0] if marcados else len(lineas)
            if [int(r['linea']) for r in propias] != list(range(1, fin + 1)) or len(marcados) > 1:
                problemas.append(f'{nombre} {i}: las líneas no terminan en el aviso')
                break
            if slm and [r['hablante'] for r in propias] != [l.hablante for l in conj.con_roles(i, lineas)[:fin]]:
                problemas.append(f'{nombre} {i}: los hablantes no son los roles del conjunto')
                break
            if carpeta == 'config':
                if any(r['consulta'] != ('' if r['hablante'] == 'OTRA' else 'omitida') for r in propias):
                    problemas.append(f'{nombre} {i}: consultó en una línea de PROTEGIDA, o no consultó en una de OTRA')
                    break
                if [int(r['linea']) for r in propias if r['ms_etapa2']] != marcados:
                    problemas.append(f'{nombre} {i}: el motivo no se pidió solo en el aviso')
                    break
        if registrados(filas, ids) != regla(filas, ids):
            problemas.append(f'{nombre}: el aviso registrado no es el de su regla')
    return problemas


# --- Cifras ---
def exitos(av, ids, ref):
    """cifra → {caso: acierto}: los casos que cuentan en cada cifra, para Wilson y McNemar. En las FA, acierto = avisó."""
    est = [i for i in ids if ref[i]['clase'] == 'vishing']
    leg = [i for i in ids if ref[i]['clase'] in casos.LEGITIMAS]
    avisa = {i: av.get(i) is not None for i in ids}
    salida = {
        'estafas': {i: avisa[i] for i in est},
        'antes del pedido': {i: avisa[i] and av[i] < ref[i]['t_r_linea'] for i in est if ref[i]['t_r_linea']},
        'a tiempo': {i: avisa[i] and av[i] <= ref[i]['t_r_linea'] for i in est if ref[i]['t_r_linea']},
        'antes del cumplimiento': {i: avisa[i] and av[i] < ref[i]['t_c_linea'] for i in est if ref[i]['t_c_linea']},
        'FA': {i: avisa[i] for i in leg},
    }
    for t in TIPOS:
        salida[f'FA {t}'] = {i: avisa[i] for i in leg if ref[i].get('tipo_legitima') == t}
    sin_tipo = {i: avisa[i] for i in leg if ref[i].get('tipo_legitima') not in TIPOS}
    if sin_tipo:
        salida['FA sin tipo'] = sin_tipo
    return salida


def kn(e):
    return sum(e.values()), len(e)


def limites(k, n, z=1.96):
    """(inferior, superior) de Wilson al 95 %, en proporción; (None, None) sin casos."""
    if not n:
        return None, None
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    mitad = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centro - mitad, centro + mitad


def discordantes(a, b):
    """(solo a, solo b, p de McNemar) en los casos de una cifra."""
    solo_a = sum(a[i] and not b[i] for i in a)
    solo_b = sum(b[i] and not a[i] for i in a)
    return solo_a, solo_b, mcnemar(solo_a, solo_b)


def corto(e):
    return ' · '.join(f'{k}/{n}' for k, n in (kn(e[c]) for c in ('estafas', 'a tiempo', 'FA')) if n) or '—'


# --- Anotación alternativa ---
def leer_anotacion(ruta, conjs):
    """{conjunto: {caso: cambios}} de una anotación alternativa: {"_meta": {...}, "casos": {id: {campo: valor}}}.

    También acepta etiquetas-producto.json tal cual (cada caso con `etiqueta`): ver ETIQUETAS_PRODUCTO.
    """
    datos = json.loads(Path(ruta).read_text(encoding='utf-8'))
    casos_ = datos['casos']
    if casos_ and all(isinstance(v, dict) and 'etiqueta' in v for v in casos_.values()):
        desconocidas = {v['etiqueta'] for v in casos_.values()} - set(ETIQUETAS_PRODUCTO)
        if desconocidas:
            raise ValueError(f'anotación alternativa: etiquetas de producto desconocidas {sorted(desconocidas)}')
        casos_ = {i: {'vista': ETIQUETAS_PRODUCTO[v['etiqueta']]} for i, v in casos_.items() if ETIQUETAS_PRODUCTO[v['etiqueta']]}
    salida = collections.defaultdict(dict)
    for i, cambios in casos_.items():
        donde = [n for n, c in conjs.items() if i in c.ids]
        if len(donde) != 1:
            raise ValueError(f'anotación alternativa: {i} no está en ningún conjunto')
        sobran = set(cambios) - CAMPOS_ANOTACION
        if sobran:
            raise ValueError(f'anotación alternativa: {i} cambia campos no previstos {sorted(sobran)}')
        salida[donde[0]][i] = cambios
    for n, cambios in salida.items():
        errores = conjuntos.validar_referencia(aplicar(conjs[n].referencia(), cambios),
                                               {i: len(conjs[n].cargar_texto(i)) for i in conjs[n].ids}, n)
        if errores:
            raise ValueError('anotación alternativa inválida:\n' + '\n'.join(errores))
    return dict(salida)


def aplicar(ref, cambios):
    return {i: {**r, **cambios.get(i, {})} for i, r in ref.items()}


# --- Criterios (borrador) ---
DIMENSIONES = {'estafas': 'más', 'a tiempo': 'más', 'FA': 'menos'}  # qué es ganar en cada cifra del criterio 1


def contra(cfg, ref, c=CRITERIOS):
    """(gana, pierde, texto) de la configuración contra una referencia en las cifras de DIMENSIONES.

    En cada cifra, con los pares discordantes: gana si tiene `margen` o más a favor y p < `p` (McNemar exacto); pierde
    si los tiene en contra. En las FA, a favor es que la referencia avise y la configuración no.
    """
    gana, pierde, partes = [], [], []
    for cifra, mejor in DIMENSIONES.items():
        solo_cfg, solo_ref, p = discordantes(cfg[cifra], ref[cifra])
        a_favor, en_contra = (solo_cfg, solo_ref) if mejor == 'más' else (solo_ref, solo_cfg)
        if a_favor - en_contra >= c['margen'] and p < c['p']:
            gana.append(cifra)
        elif en_contra - a_favor >= c['margen'] and p < c['p']:
            pierde.append(cifra)
        partes.append(f'{cifra} {a_favor} a {en_contra} (p = {p:.3f})')
    return gana, pierde, '; '.join(partes)


def criterios(test, externo=None, c=CRITERIOS):
    """[(criterio, valor, cumple)] sobre la vista principal; cumple es None si falta el dato.

    `test` y `externo`: detector → exitos(); la configuración se llama 'config'.
    1. Contra cada referencia: gana con margen en alguna de las cifras de DIMENSIONES y no pierde en ninguna.
    2. Límite inferior de Wilson de la detección útil (a tiempo) y de las estafas avisadas, sobre un piso.
    3. #144: las estafas avisadas no caen más de `caida_externo` respecto del test.
    """
    salida = []
    if not test or 'config' not in test:
        return [('la configuración en el test', 'no corrió o tiene problemas', None)]
    cfg = test['config']
    for ref in REFERENCIAS:
        nombre = f'le gana a {ref} sin perder (estafas, a tiempo, FA)'
        if ref not in test:
            salida.append((nombre, 'falta la referencia', None))
            continue
        gana, pierde, texto = contra(cfg, test[ref], c)
        salida.append((nombre, f'a favor y en contra: {texto}', bool(gana) and not pierde))
    for cifra, piso in (('a tiempo', 'piso_a_tiempo'), ('estafas', 'piso_estafas')):
        k, n = kn(cfg[cifra])
        lo, _ = limites(k, n)
        salida.append((f'límite inferior de {cifra} ≥ {c[piso]:.0%}', wilson(k, n), None if lo is None else lo >= c[piso]))
    nombre = f'#144 cae como mucho {c["caida_externo"]:.0%} en estafas avisadas'
    if externo and 'config' in externo:
        kt, nt = kn(cfg['estafas'])
        ke, ne = kn(externo['config']['estafas'])
        salida.append((nombre, f'{ke}/{ne} en #144 contra {kt}/{nt} en el test',
                       None if not ne or not nt else ke / ne >= kt / nt - c['caida_externo']))
    else:
        salida.append((nombre, 'no corrió', None))
    return salida


# --- Informe ---
def etiqueta(d, config):
    return f'`{config}`' if d == 'config' else d


def cifras_tabla(ex, config):
    filas = []
    for nombre, e in ex.items():
        filas.append([etiqueta(nombre, config), *(wilson(*kn(e[c])) if c in e and kn(e[c])[1] else '—' for c in CIFRAS)])
    tabla(filas, ['detector', *CIFRAS])


def mcnemar_tabla(ex, config):
    if 'config' not in ex:
        return
    filas = []
    for ref in [r for r in ex if r != 'config']:
        for c in COMPARADAS:
            if kn(ex['config'][c])[1]:
                a, b, p = discordantes(ex['config'][c], ex[ref][c])
                filas.append([etiqueta(ref, config), c, a, b, f'{p:.3f}'])
    tabla(filas, ['referencia', 'cifra', 'solo la configuración', 'solo la referencia', 'p (McNemar exacto)'])


def volumen_tabla(k, n):
    p = k / n
    lo, hi = limites(k, n)
    tabla([[v, f'{p * v * SEMANAS_POR_MES:.1f} [{lo * v * SEMANAS_POR_MES:.1f}–{hi * v * SEMANAS_POR_MES:.1f}]']
           for v in VOLUMENES], ['llamadas de desconocidos legítimas por semana', 'FA por mes (Wilson 95 %)'])


def informe_conjunto(nombre, conj, ref, avs, leidas, config, motivos):
    """Imprime las cifras del conjunto y devuelve los éxitos de la vista principal por detector."""
    principal = [i for i in conj.ids if ref[i]['vista'] == PRINCIPAL]
    est = [i for i in principal if ref[i]['clase'] == 'vishing']
    print(f'## {NOMBRES[nombre]}\n')
    print(f'Vista principal: {len(est)} estafas ({sum(bool(ref[i]["t_r_linea"]) for i in est)} con pedido, '
          f'{sum(bool(ref[i]["t_c_linea"]) for i in est)} con cumplimiento) y {len(principal) - len(est)} legítimas '
          f'({", ".join(f"{t} {sum(ref[i].get("tipo_legitima") == t for i in principal)}" for t in TIPOS)}).\n')
    ex = {d: exitos(av, principal, ref) for d, av in avs.items()}
    print('### Cifras (Wilson 95 %)\n')
    cifras_tabla(ex, config)
    print('### McNemar: la configuración contra cada referencia, en los mismos casos\n')
    mcnemar_tabla(ex, config)
    apartes = sorted({ref[i]['vista'] for i in conj.ids} - {PRINCIPAL})
    if apartes:
        print('### Aparte (estafas · a tiempo · FA)\n')
        tabla([[v, sum(ref[i]['vista'] == v for i in conj.ids),
                *(corto(exitos(avs[d], [i for i in conj.ids if ref[i]['vista'] == v], ref)) if d in avs else '—'
                  for d in ['config', V4, *REGLAS])] for v in apartes], ['vista', 'casos', f'`{config}`', V4, *REGLAS])
    if 'config' in avs:
        print('### La configuración, caso por caso (vista principal)\n')
        av = avs['config']
        sin = [i for i in est if av[i] is None]
        print(f'- Estafas sin aviso ({len(sin)}): ' + (', '.join(sin) or 'ninguna') + '.')
        fa = [i for i in principal if ref[i]['clase'] in casos.LEGITIMAS and av[i] is not None]
        print(f'- FA ({len(fa)}): ' + (', '.join(f'{i} ({ref[i].get("tipo_legitima") or "sin tipo"}, L{av[i]})' for i in fa)
                                       or 'ninguna') + '.\n')
    if leidas:
        print('### Formato y latencia\n')
        filas_md = []
        for d, filas in leidas.items():
            if d in REGLAS:
                continue
            con = [r for v in filas.values() for r in v if r['consulta'] != 'omitida']
            malas = collections.Counter(r['error'].split(':')[0] for r in con if r['valida'] != 'true')
            filas_md.append([etiqueta(d, config), len(con), f'{sum(malas.values())} {dict(malas) or ""}'.strip(),
                             p50_p95([num(r['ms_etapa1'] or r['ms']) for r in con if num(r['ms_etapa1'] or r['ms']) is not None])])
        tabla(filas_md, ['detector', 'consultas', 'inválidas', 'ms por consulta (p50 / p95)'])
    if motivos and 'config' in avs:
        print('### Motivos de las FA de la configuración, para leer a mano\n')
        av = avs['config']
        fa = [i for i in principal if ref[i]['clase'] in casos.LEGITIMAS and av[i] is not None]
        tabla([[i, f'L{av[i]}', r['riesgo'], f'«{celda(r["motivo"])}»' if r['motivo'] else f'— ({r["error"] or "sin motivo"})']
               for i in fa for r in [next(x for x in leidas['config'][i] if int(x['linea']) == av[i])]],
              ['caso', 'aviso', 'riesgo', 'motivo'])
    return ex


def control_desarrollo(datos, conj, config):
    """(lista, texto): si la configuración reproduce en desarrollo sus cifras ya medidas, ±2, antes de tocar el test.
    Lo usa el Colab después de la corrida de desarrollo."""
    if config not in CIFRAS_DESARROLLO:
        return False, f'faltan las cifras de desarrollo de {config} en CIFRAS_DESARROLLO: no se corre el test'
    corrida = leer(datos / 'desarrollo' / 'config')
    if corrida is None:
        return False, 'falta la corrida de la configuración en desarrollo'
    por_config, man = corrida
    problemas = controlar('config', conj, por_config, man, config)
    if problemas:
        return False, 'la corrida de desarrollo tiene problemas: ' + '; '.join(problemas)
    filas = filas_de(por_config, man, 'config', config)
    ref = conj.referencia()
    principal = [i for i in conj.ids if ref[i]['vista'] == PRINCIPAL]
    con = [r for v in filas.values() for r in v if r['consulta'] != 'omitida']
    invalidas = sum(r['valida'] != 'true' for r in con)
    if not con or invalidas > MAXIMO_INVALIDAS * len(con):
        return False, f'{invalidas} líneas inválidas de {len(con)} consultadas: más del {MAXIMO_INVALIDAS:.0%}'
    ex = exitos(avisos_config(filas, principal), principal, ref)
    medidas = {c: kn(ex[c])[0] for c in CIFRAS_DESARROLLO[config]}
    fuera = {c: medidas[c] - v for c, v in CIFRAS_DESARROLLO[config].items() if abs(medidas[c] - v) > TOLERANCIA}
    texto = ', '.join(f'{c} {medidas[c]} (antes {v})' for c, v in CIFRAS_DESARROLLO[config].items())
    if fuera:
        return False, f'no reproduce desarrollo (±{TOLERANCIA}): {texto}'
    return True, f'reproduce desarrollo (±{TOLERANCIA}): {texto}'


def humo(datos):
    ruta = datos / 'humo' / 'humo.json'
    print('## Humo de formato\n')
    if not ruta.exists():
        print('> Falta humo/humo.json.\n')
        return
    d = json.loads(ruta.read_text(encoding='utf-8'))
    tabla([[f'`{p}`', f"{x['leidas']}/{x['lineas']}", ', '.join(x['errores']) or '—', 'PASA' if x['pasa'] else 'NO PASA']
           for p, x in d.items()], ['prompt', 'leídas', 'errores', 'resultado'])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    p.add_argument('--conjuntos', type=Path, help='carpeta con los conjuntos armados (por defecto, DATOS/conjuntos)')
    p.add_argument('--config', default=CONFIG, choices=sorted(PROMPTS_CORTE_RIESGO))
    p.add_argument('--anotacion-legitimas', type=Path, help='anotación alternativa: {"_meta": …, "casos": {id: {campo: valor}}}')
    p.add_argument('--motivos', action='store_true', help='mostrar los motivos de las FA (texto que escribió el modelo)')
    args = p.parse_args(argv)
    datos = args.datos.resolve()
    dir_conj = (args.conjuntos or datos / 'conjuntos').resolve()
    config = args.config
    assert V4 in PROMPTS_CORTE
    print('# #143, evaluación final — análisis offline\n')
    print(f'Configuración: `{config}` (solo OTRA, «riesgo ≥ 0,3», modo operativo). Referencias: `{V4}` (v4 sin alcance, '
          '«riesgo ≥ 0,4 o alerta», todas las líneas) y las reglas de palabras clave v1 y v2. Criterios: README.md, '
          'borrador.\n')
    humo(datos)
    conjs = {n: conjuntos.Conjunto(dir_conj / n) for n in CONJUNTOS if (dir_conj / n / 'conjunto.json').exists()}
    print('## Control de las corridas\n')
    filas_md, leidas, problemas_globales, commits = [], {}, [], set()
    for n, conj in conjs.items():
        errores = conj.validar()
        if errores:
            problemas_globales.append(f'el conjunto {n} no valida: ' + '; '.join(errores[:3]))
            continue
        leidas[n] = {}
        for carpeta in CARPETAS:
            corrida = leer(datos / n / carpeta)
            if corrida is None:
                filas_md.append([n, carpeta, '—', 'falta'])
                continue
            por_config, man = corrida
            prob = controlar(carpeta, conj, por_config, man, config)
            commits.add(man.get('codigo', {}).get('commit'))
            filas_md.append([n, carpeta, (man.get('codigo', {}).get('commit') or '')[:10], '; '.join(prob) or 'bien'])
            if not prob:
                for nombre, prompt, regla in series(carpeta, config):
                    leidas[n][nombre] = (filas_de(por_config, man, nombre, prompt), regla)
    tabla(filas_md, ['conjunto', 'corrida', 'commit', 'control'])
    if len(commits) > 1:
        problemas_globales.append('las corridas no son todas del mismo commit')
    if problemas_globales:
        print('\n'.join(f'- **{x}**' for x in problemas_globales) + '\n')

    if 'desarrollo' in leidas and 'config' in leidas['desarrollo']:
        ok, texto = control_desarrollo(datos, conjs['desarrollo'], config)
        print(f'**Control de reproducibilidad en desarrollo:** {texto}.\n')

    principales = {}
    for n in conjs:
        if n not in leidas:
            continue
        conj, ref = conjs[n], conjs[n].referencia()
        avs = {d: regla(filas, conj.ids) for d, (filas, regla) in leidas[n].items()}
        principales[n] = informe_conjunto(n, conj, ref, avs, {d: f for d, (f, _) in leidas[n].items()}, config,
                                          args.motivos)

    print('## Criterios (borrador de README.md: decide Mateo)\n')
    tabla([[c, v, '—' if ok is None else ('cumple' if ok else 'no cumple')]
           for c, v, ok in criterios(principales.get('test_reservado'), principales.get('externo'))],
          ['criterio', 'valor', 'resultado'])
    test = principales.get('test_reservado', {}).get('config')
    if test and kn(test['FA'])[1]:
        print('### FA por volumen de llamadas (test, vista principal; sin umbral)\n')
        volumen_tabla(*kn(test['FA']))
        k, n = kn(test['estafas'])
        kf, nf = kn(test['FA'])
        print(f'**80/15, solo como referencia:** estafas avisadas {100 * k / n:.0f} % (80 %), FA {100 * kf / nf:.0f} % '
              '(15 %).\n')

    if args.anotacion_legitimas:
        cambios = leer_anotacion(args.anotacion_legitimas, conjs)
        print(f'## Con la anotación alternativa (`{args.anotacion_legitimas.name}`)\n')
        print('Cambios: ' + '; '.join(f'{n}: {len(c)} con cambios ({", ".join(f"{k} {v}" for k, v in collections.Counter(k for x in c.values() for k in x).items())})'
                                      for n, c in cambios.items()) + '.\n')
        alternativas = dict(principales)
        for n, c in cambios.items():
            if n not in leidas:
                continue
            conj = conjs[n]
            ref = aplicar(conj.referencia(), c)
            avs = {d: regla(filas, conj.ids) for d, (filas, regla) in leidas[n].items()}
            principal = [i for i in conj.ids if ref[i]['vista'] == PRINCIPAL]
            ex = {d: exitos(av, principal, ref) for d, av in avs.items()}
            alternativas[n] = ex
            print(f'### {NOMBRES[n]}, vista principal con la anotación alternativa\n')
            cifras_tabla(ex, config)
            mcnemar_tabla(ex, config)
        print('### Criterios con la anotación alternativa\n')
        tabla([[c, v, '—' if ok is None else ('cumple' if ok else 'no cumple')]
               for c, v, ok in criterios(alternativas.get('test_reservado'), alternativas.get('externo'))],
              ['criterio', 'valor', 'resultado'])
    return 0


if __name__ == '__main__':
    sys.exit(main())
