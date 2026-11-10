"""#143, configuración congelada: lectura de la prueba de humo en desarrollo.

No corre modelos ni lee la reserva; solo biblioteca estándar y el código del laboratorio. Uso, desde esta carpeta, con
los ZIP de Colab descomprimidos acá (humo/ y desarrollo/) y las corridas de la etapa 2 en ../2026-11-07_alcance-etapa-2/:
    python -I analizar.py                       # todo
    python -I analizar.py --datos OTRA_CARPETA  # corridas en otra carpeta (pruebas)

Escrito el 2026-11-10, antes de correr. La configuración es la que congeló Mateo el 2026-11-09: C de la etapa 2
(`c-json`) cortado tras el riesgo (`c-json-corte-riesgo`, num_predict 14), «riesgo ≥ 0,3», el motivo de C
(prompts/motivo_c_corte.txt) en una segunda consulta solo en el primer aviso, y consulta solo en las líneas de OTRA
(`correr.py --solo-otra`), en modo operativo.

La regla (README.md, «Regla de lectura, escrita antes de correr»), dentro del alcance (46 estafas, 36 con pedido, y 94
legítimas):
0. La humo de formato pasa: `c-json-corte-riesgo` lee el riesgo, con su coma, en las 48 líneas. Si no pasa, no corre
   nada más.
1. La corrida es la configuración congelada sobre los 244 de desarrollo (control de abajo, en `controlar`).
2. Las líneas inválidas son como mucho el 1 % de las consultadas.
3. Las cuatro cifras quedan dentro de ±2 de la lectura simulada de la etapa 3: `c-json-corte` de la etapa 2 con
   «riesgo ≥ 0,3», solo en las líneas de OTRA (35/46 · 15/36 · 25/36 · FA 24/94).
Si se cumple todo, la configuración queda lista para la evaluación final. Si no, se le avisa a Mateo y no se ajusta nada.
Aparte, solo para mirar: alcance-91 y los intervalos, los casos con otra línea de aviso, los avisos de un 0,3 exacto, la
latencia, el costo por llamada, el motivo con la medición de la etapa 3 y los motivos de todas las FA, para leer a mano.
"""

import argparse, collections, importlib.util, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import casos  # noqa: E402
from detectores import (ESQUEMA_MOTIVO, MAXIMO_TOKENS_CORTE_RIESGO, PROMPT_MOTIVO_C, cargar_prompt,  # noqa: E402
                        cargar_prompt_motivo, esquema_de, evidencia_en_texto, huella)

# La etapa 3 ya define la vista, la referencia, las cifras y la medición del motivo: se usan tal cual. Al importarla
# comprueba que desarrollo son los 244, sin la reserva.
_spec = importlib.util.spec_from_file_location('analizar_etapa_3', AQUI.parent / '2026-11-09_pedido-critico-etapa-3' / 'analizar.py')
e3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(e3)

VARIANTE = 'c-json-corte-riesgo'
UMBRAL = 0.3
ROL = 'OTRA'
TOLERANCIA = 2           # ±2 es ruido (ADR 0005)
MAXIMO_INVALIDAS = 0.01  # como en el JSON cortado de v4 (corridas/2026-11-07_json-cortado)
LINEAS_HUMO = 48
ETAPA_2 = AQUI.parent / '2026-11-07_alcance-etapa-2'
# Los 56 de test de laboratorio-luciano (ENT-T) y la reserva (CV2-T) no pueden aparecer.
PREFIJOS_TEST = ('CV2-T', 'ENT-T')
num, tabla, p50_p95, wilson, metricas, fmt, corto = e3.num, e3.tabla, e3.p50_p95, e3.wilson, e3.metricas, e3.fmt, e3.corto
VISTA, IDS, REF = e3.VISTA, e3.IDS, e3.REF


def celda(texto):
    """Texto libre del modelo dentro de una tabla Markdown: sin barras ni saltos de línea sueltos."""
    return ' '.join(texto.split()).replace('|', '\\|')


def avisos(filas, ids):
    """case_id → primera línea válida de OTRA con «riesgo ≥ 0,3» (None si no avisa)."""
    return e3.avisos(filas, ids, u=UMBRAL, rol=ROL, campo=False, alerta=False)


def referencia(etapa_2=ETAPA_2):
    """Las cifras de la lectura simulada de la etapa 3: `c-json-corte` de la etapa 2, «riesgo ≥ 0,3», solo OTRA."""
    datos = e3.leer(Path(etapa_2), 'c-json-corte')
    if datos is None:
        return None, None
    filas, _ = datos
    av = avisos(filas, IDS)
    return metricas(av, VISTA), av


def controlar(filas, man):
    """Problemas de la corrida (lista vacía si está bien): tiene que ser la configuración congelada sobre los 244."""
    problemas = []
    if sorted(filas) != IDS or sorted(man['casos']) != IDS:
        problemas.append('no son los 244 de desarrollo')
    if man.get('particion') != 'desarrollo' or man.get('lista') or [i for i in man['casos'] if i.startswith(PREFIJOS_TEST)]:
        problemas.append('no es la partición de desarrollo entera')
    if any(i in IDS and h != huella((casos.DIR_TEXTO / f'{i}.txt').read_text(encoding='utf-8')) for i, h in man['casos'].items()):
        problemas.append('el texto de algún caso cambió')
    if man['ollama']['version'] != e3.OLLAMA or (man['ollama']['digests'].get(e3.MODELO) or '').removeprefix('sha256:') != e3.DIGEST:
        problemas.append('Ollama o digest distinto')
    ps = man['parametros_slm']
    if (ps['num_ctx'], ps['seed'], ps['temperatura']) != (4096, 42, 0.0):
        problemas.append('num_ctx, seed o temperatura distintos')
    if ps.get('corte_riesgo', {}).get('num_predict') != MAXIMO_TOKENS_CORTE_RIESGO:
        problemas.append('no es el corte tras el riesgo')
    p = man['prompts'].get(VARIANTE, {})
    if list(man['prompts']) != [VARIANTE] or (p.get('texto'), p.get('esquema')) != (cargar_prompt(VARIANTE), esquema_de(VARIANTE)):
        problemas.append(f'el prompt no es el de {VARIANTE}')
    if (p.get('etapa2', {}).get('texto'), p.get('etapa2', {}).get('esquema')) != (cargar_prompt_motivo(PROMPT_MOTIVO_C), ESQUEMA_MOTIVO):
        problemas.append('la segunda consulta no es motivo_c_corte.txt')
    if man.get('solo_otra') is not True:
        problemas.append('no corrió con --solo-otra')
    if man['modo_termino'] != 'operativo-hasta-aviso' or man['interrumpida']:
        problemas.append('no corrió entera en modo operativo')
    if man['codigo'].get('cambios_sin_commit_en_la_carpeta'):
        problemas.append('corrió con cambios sin commitear')
    for i in sorted(filas):
        if i not in IDS:
            continue
        lineas, propias = e3.con_roles(i), filas[i]
        marcados = [int(r['linea']) for r in propias if r['aviso'] == 'true']
        fin = marcados[0] if marcados else len(lineas)
        if [int(r['linea']) for r in propias] != list(range(1, fin + 1)) or len(marcados) > 1:
            problemas.append(f'{i}: las líneas no terminan en el aviso')
            break
        if {r['prompt'] for r in propias} != {VARIANTE} or {r['hablantes'] for r in propias} != {'rol'} \
                or [r['hablante'] for r in propias] != [l.hablante for l in lineas[:fin]]:
            problemas.append(f'{i}: prompt o hablantes distintos')
            break
        if any(r['consulta'] != ('' if r['hablante'] == ROL else 'omitida') for r in propias):
            problemas.append(f'{i}: consultó en una línea de PROTEGIDA, o no consultó en una de OTRA')
            break
        if [int(r['linea']) for r in propias if r['ms_etapa2']] != marcados:
            problemas.append(f'{i}: el motivo no se pidió solo en el aviso')
            break
    # El aviso que registró correr.py tiene que ser el de la regla, recalculado acá.
    registrado = {i: next((int(r['linea']) for r in filas[i] if r['aviso'] == 'true'), None) for i in filas}
    if registrado != avisos(filas, list(filas)):
        problemas.append('el aviso registrado no es el de «riesgo ≥ 0,3» en una línea de OTRA')
    return problemas


def consultadas(filas, ids=None):
    return [r for i in (ids or filas) for r in filas.get(i, []) if r['consulta'] != 'omitida']


def veredicto(humo_pasa, problemas, invalidas, n_consultadas, m, ref):
    """('lista' / 'avisar a Mateo', razones) según la regla."""
    razones = []
    if humo_pasa is not True:
        razones.append('la humo de formato no pasó o falta')
    if problemas:
        razones.append('la corrida no es la configuración congelada: ' + '; '.join(problemas))
    if not n_consultadas:
        razones.append('no hay líneas consultadas')
    elif invalidas > MAXIMO_INVALIDAS * n_consultadas:
        razones.append(f'{invalidas} líneas inválidas de {n_consultadas} consultadas: más del {MAXIMO_INVALIDAS:.0%}')
    if m is None or ref is None:
        razones.append('falta la corrida o la lectura de la etapa 3')
    else:
        fuera = {c: x for c, x in e3.diferencias(m, ref, e3.TODAS).items() if abs(x) > TOLERANCIA}
        if fuera:
            razones.append('se aparta más de ±2 de la etapa 3: ' + e3.texto_dif(fuera))
    return ('avisar a Mateo', razones) if razones else ('lista', ['se cumplen las tres condiciones'])


def humo(datos):
    """True si pasa, False si no, None si falta. Imprime la tabla."""
    ruta = datos / 'humo' / 'humo.json'
    print('## Humo de formato\n')
    if not ruta.exists():
        print('> Falta humo/humo.json.\n')
        return None
    h = json.loads(ruta.read_text(encoding='utf-8'))
    tabla([[f"{h['leidas']}/{h['lineas']}", ', '.join(h['errores']) or '—', h['tokens_salida'],
            f"{h['igual_a_c_json_corte']}/{h['lineas']}", h['dos_decimales'], 'PASA' if h['pasa'] else 'NO PASA']],
          ['riesgo leído', 'errores', 'tokens generados (mín / mediana / máx)', 'mismo riesgo que c-json-corte (dato)',
           'riesgos con dos decimales (dato)', 'resultado'])
    return h['pasa'] is True and h['lineas'] == h['leidas'] == LINEAS_HUMO


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument('--datos', type=Path, default=AQUI)
    p.add_argument('--etapa-2', type=Path, default=ETAPA_2, help='carpeta con c-json-corte/')
    args = p.parse_args(argv)
    datos = args.datos.resolve()
    print('# #143, configuración congelada: humo en desarrollo — análisis offline\n')
    print(f'Vista dentro del alcance: {len(e3.ESTAFAS)} estafas de corpus_v2 '
          f'({sum(1 for i in e3.ESTAFAS if REF[i].get("t_r_linea"))} con pedido) y {len(e3.LEGITIMAS)} legítimas entrantes. '
          'Cifras: estafas avisadas, avisos antes del pedido (T_A < T_R), a tiempo (T_A ≤ T_R) y FA. Las líneas inválidas '
          'no avisan.\n')
    humo_pasa = humo(datos)
    ref, av_ref = referencia(args.etapa_2)
    corrida = e3.leer(datos, 'desarrollo')
    print('## Control de la corrida\n')
    if corrida is None:
        print('> Falta desarrollo/.\n')
        filas, problemas, m, av = {}, ['falta la corrida'], None, {}
    else:
        filas, man = corrida
        problemas = controlar(filas, man)
        av = avisos(filas, IDS)
        m = metricas(av, VISTA)
        todas = consultadas(filas)
        print(f"Commit `{man['codigo']['commit'][:10]}`, {len(filas)} casos, {sum(len(v) for v in filas.values())} líneas "
              f"registradas, {len(todas)} consultadas.\n")
        print('Sin problemas.\n' if not problemas else '\n'.join(f'- {x}' for x in problemas) + '\n')
    todas = consultadas(filas)
    invalidas = collections.Counter(r['error'] for r in todas if r['valida'] != 'true')

    print('## La regla\n')
    print(f'**0. Humo de formato:** {"pasa" if humo_pasa else "falta" if humo_pasa is None else "no pasa"}.\n')
    print(f'**1. Control:** {"sin problemas" if not problemas else "con problemas (arriba)"}.\n')
    print(f'**2. Líneas inválidas:** {sum(invalidas.values())} de {len(todas)} consultadas'
          f'{" " + str(dict(invalidas)) if invalidas else ""}; el máximo es el {MAXIMO_INVALIDAS:.0%}.\n')
    print('**3. Contra la lectura simulada de la etapa 3** (`c-json-corte` de la etapa 2, «riesgo ≥ 0,3», solo OTRA):\n')
    filas_md = [['lectura simulada de la etapa 3', *(fmt(ref) if ref else ['—'] * 4)],
                ['esta corrida', *(fmt(m) if m else ['—'] * 4)]]
    tabla(filas_md, ['configuración', *e3.ENC])
    if m and ref:
        print(f'Diferencias: {e3.texto_dif(e3.diferencias(m, ref, e3.TODAS))}.\n')
    estado, razones = veredicto(humo_pasa, problemas, sum(invalidas.values()), len(todas), m, ref)
    print(f'**Resultado: {"la configuración queda lista para la evaluación final" if estado == "lista" else "avisar a Mateo antes de la evaluación final; no se ajusta nada"}.**\n')
    print('\n'.join(f'- {x}' for x in razones) + '\n')

    if corrida is None:
        return 0
    print('## Aparte, solo para mirar\n')
    aparte(filas, av, av_ref)
    return 0


def aparte(filas, av, av_ref):
    print('### alcance-91 e intervalos de Wilson\n')
    tabla([['alcance-140', *fmt(metricas(av, VISTA))], ['alcance-91', *fmt(metricas(av, e3.VISTA_91))]], ['vista', *e3.ENC])
    m = metricas(av, VISTA)
    print(f"Wilson (95 %): estafas {wilson(m['det'], m['n_est'])}; a tiempo {wilson(m['antes'] + m['en'], m['n_conp'])}; "
          f"FA {wilson(m['fa'], m['n_leg'])}.\n")

    print('### Casos con otra línea de aviso que la lectura simulada (dentro del alcance)\n')
    distintos = [(i, av_ref.get(i), av.get(i)) for i in VISTA if av_ref is not None and av_ref.get(i) != av.get(i)]
    if av_ref is None:
        print('> Falta la etapa 2.\n')
    else:
        print(f'{len(distintos)} de {len(VISTA)}.\n')
        if distintos:
            tabla([[i, REF[i]['clase'], f'L{a}' if a else '–', f'L{b}' if b else '–'] for i, a, b in distintos],
                  ['caso', 'clase', 'simulada', 'esta corrida'])

    print('### Avisos que salen de un 0,3 exacto (dentro del alcance)\n')
    fila_aviso = {i: next(r for r in filas[i] if int(r['linea']) == av[i]) for i in VISTA if av.get(i)}
    for clase, nombre in (('vishing', 'estafas'), (None, 'FA')):
        ids = [i for i in fila_aviso if (REF[i]['clase'] == 'vishing') == (clase == 'vishing')]
        exactos = sum(num(fila_aviso[i]['riesgo']) == UMBRAL for i in ids)
        print(f'- {nombre}: {exactos} de {len(ids)} avisos.')
    print()

    print('### Latencia en T4 (ms de pared; p50 / p95, dentro del alcance)\n')
    con = consultadas(filas, VISTA)
    en_aviso = [fila_aviso[i] for i in fila_aviso]
    tabla([[p50_p95([num(r['ms_etapa1']) for r in con if num(r['ms_etapa1']) is not None]), len(con),
            p50_p95([num(r['tokens_salida']) for r in con if num(r['tokens_salida']) is not None]),
            p50_p95([num(r['ms_etapa2']) for r in en_aviso if num(r['ms_etapa2']) is not None]),
            p50_p95([num(r['ms']) for r in en_aviso if num(r['ms']) is not None]), len(en_aviso)]],
          ['primera consulta (ms)', 'consultas', 'tokens generados', 'motivo (ms)', 'total en la línea del aviso (ms)',
           'avisos'])
    print('En la etapa 3: C sin alerta, 239 ms (p50) con 14 tokens; el motivo de C con campo, unos 800 ms.\n')

    print('### Costo por llamada, hasta el aviso o el final (mediana / p95)\n')
    filas_md = []
    for nombre, ids in (('estafas', e3.ESTAFAS), ('legítimas', e3.LEGITIMAS)):
        k = [len(consultadas(filas, [i])) for i in ids]
        ms = [sum(num(r['ms']) or 0.0 for r in filas.get(i, [])) for i in ids]
        filas_md.append([nombre, p50_p95(k), p50_p95(ms)])
    tabla(filas_md, ['llamadas', 'consultas', 'ms'])

    print('### Motivo de C (la medición de la etapa 3, escrita antes de correr)\n')
    print('En cada aviso dentro del alcance: JSON válido con motivo; evidencia textual de OTRA hasta esa línea; evidencia '
          'textual en cualquier voz; y motivos que nombran un pedido cuando la referencia todavía no marca un pedido crítico '
          '(por palabras; se leen a mano).\n')
    pedidos = [(i, fila_aviso[i]) for i in fila_aviso if fila_aviso[i]['ms_etapa2']]
    validos = [(i, r) for i, r in pedidos if not r['error'].startswith('etapa2_') and r['motivo'].strip()]
    de_otra = sum(evidencia_en_texto(r['evidencia'], [l for l in e3.con_roles(i)[:int(r['linea'])] if l.hablante == ROL])
                  for i, r in validos)
    cualquiera = sum(r['evidencia_en_texto'] == 'true' for _, r in validos)
    antes = [(i, r) for i, r in validos if not (e3.linea_critica(i) and e3.linea_critica(i) <= int(r['linea']))]
    marcados = {i for i, r in antes if e3.PALABRAS_PEDIDO.search(r['motivo'])}
    tabla([[len(pedidos), f'{len(validos)}/{len(pedidos)}', f'{de_otra}/{len(validos)}', f'{cualquiera}/{len(validos)}',
            f'{len(marcados)}/{len(antes)}']],
          ['motivos pedidos', 'JSON válido con motivo', 'evidencia de OTRA', 'evidencia en cualquier voz',
           'nombran un pedido antes de que ocurra (marcados)'])
    fallos = [(i, r) for i, r in pedidos if (i, r) not in validos]
    if fallos:
        print('Motivos que fallaron (la app muestra el texto fijo): '
              + ', '.join(f'{i} L{r["linea"]} ({r["error"] or "motivo vacío"})' for i, r in fallos) + '.\n')
    print('Marcados en estafas: ' + (', '.join(sorted(i for i in marcados if REF[i]['clase'] == 'vishing')) or 'ninguno') + '.\n')

    print('### Los motivos de las FA, para leer a mano\n')
    print('Todas las legítimas de la vista que avisan. «Marcado»: nombra un pedido por palabras. Se leen todos: si alguno '
          'engaña, decide Mateo si el aviso muestra el motivo o el texto fijo. El prompt del motivo no se cambia.\n')
    fa = sorted(i for i in fila_aviso if REF[i]['clase'] != 'vishing')
    tabla([[i, f'L{av[i]}', fila_aviso[i]['riesgo'], 'sí' if i in marcados else '',
            f'«{celda(fila_aviso[i]["evidencia"])}»' if fila_aviso[i]['evidencia'] else '—',
            f'«{celda(fila_aviso[i]["motivo"])}»' if fila_aviso[i]['motivo'] else f'— ({fila_aviso[i]["error"] or "sin motivo"})']
           for i in fa], ['caso', 'aviso', 'riesgo', 'marcado', 'evidencia', 'motivo'])


if __name__ == '__main__':
    sys.exit(main())
