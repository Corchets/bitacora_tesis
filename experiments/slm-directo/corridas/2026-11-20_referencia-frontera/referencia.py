"""#174, referencia: el detector `c-consejos-corte-riesgo` con un modelo de frontera por API (OpenAI).

Tandas, en este orden: desarrollo (alcance-140), las 33 legítimas reales de CallCenterEN, las 33 estafas coreanas de
#144 y la zona gris de Medicare. Nunca la reserva de test.

Solo biblioteca estándar y el código del laboratorio, como cliente_ollama.py. No toca el detector ni su valor por
defecto: arma el mismo pedido (prompt, mensaje con roles, ESQUEMA_SALIDA) y lee el riesgo con leer_riesgo_cortado.
Uso, desde esta carpeta (README.md):
    python3 -I referencia.py correr --clave ARCHIVO_FUERA_DEL_REPO   # escribe resultados.csv y manifiesto.json
    python3 -I referencia.py analizar                                 # sin API; imprime el análisis en Markdown
"""

import argparse, csv, datetime, importlib.util, json, statistics, subprocess, sys, tempfile, time
import urllib.error, urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


# La exploración carga la evaluación final, que deja el laboratorio en sys.path: de ahí salen las cifras y la regla.
expl = _cargar('analizar_exploracion', AQUI.parent / '2026-11-20_exploracion-reales' / 'analizar.py')
fin, kn = expl.fin, expl.kn
import conjuntos  # noqa: E402
from detectores import (ESQUEMA_SALIDA, PROMPTS_CORTE_RIESGO, armar_mensaje_usuario, cargar_prompt,  # noqa: E402
                        esquema_de, huella, leer_riesgo_cortado)

PROMPT = 'c-consejos-corte-riesgo'
MODELO = 'gpt-6.1-terra'
URL = 'https://api.openai.com/v1/responses'
ESFUERZO = 'none'
MAXIMO_TOKENS = 16  # la API no deja cortar por tokens exactos como Ollama; 16 alcanza para `{"riesgo":0.35,`
# US$ por millón de tokens, developers.openai.com/api/docs/pricing, 2026-11-20.
PRECIOS = {'entrada': 1.00, 'entrada_cache': 0.05, 'salida': 5.00}
RESULTADOS = AQUI / 'resultados.csv'
MANIFIESTO = AQUI / 'manifiesto.json'
CAMPOS = ['tanda', 'case_id', 'linea', 'hablante', 'valida', 'riesgo', 'error', 'ms', 'intentos', 'tokens_entrada',
          'tokens_cache', 'tokens_salida', 'estado', 'crudo']
# Tanda → (conjunto, qué casos): la vista principal o la aparte.
TANDAS = {'desarrollo': ('desarrollo', 'principal'), 'legitimas_reales': ('legitimas_reales', 'principal'),
          'externo': ('externo', 'principal'), 'zona_gris': ('legitimas_reales', 'aparte')}
NOMBRES = {'desarrollo': 'Desarrollo (alcance-140)', 'legitimas_reales': 'Legítimas reales (CallCenterEN, las 33)',
           'externo': 'Estafas reales coreanas (#144)', 'zona_gris': 'Zona gris de Medicare (avisos, no son FA)'}
# E2B con la misma configuración, corrida del 2026-11-20 (../2026-11-20_exploracion-reales/analisis-salida.md). En
# las coreanas, 2.359 de sus 4.193 líneas de OTRA fueron inválidas por contexto excedido (num_ctx 4096) y no avisaron.
E2B = {'desarrollo': {'estafas': '43/46', 'antes del pedido': '18/36', 'a tiempo': '29/36',
                      'antes del cumplimiento': '14/15', 'FA': '20/94', 'FA estrictas': '8/75'},
       'legitimas_reales': {'FA': '23/33'},
       'externo': {'estafas': '33/33', 'antes del pedido': '25/27', 'a tiempo': '27/27', 'antes del cumplimiento': '16/16'},
       'zona_gris': {'FA': '30/42'}}
E2B_LATENCIA = 'en el teléfono (Samsung A56, CPU): 3,60 s de mediana y 4,90 s de p95 por línea de OTRA'
CIFRAS = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA']


def esquema_estricto():
    """ESQUEMA_SALIDA como lo pide la salida estructurada estricta: mismos campos, mismo orden, sin otros."""
    return {**ESQUEMA_SALIDA, 'additionalProperties': False}


def tandas():
    """tanda → (conjunto, ids, referencia), armados en un directorio temporal fuera del repositorio desde lo que ya
    está en el repo: desarrollo, casos/externo/coreano y casos/externo/legitimas-reales. Nunca la reserva de test."""
    tmp = Path(tempfile.mkdtemp(prefix='referencia-174-'))
    externo = AQUI.parents[1] / 'casos' / 'externo'
    conjs = {'desarrollo': conjuntos.preparar_desarrollo(tmp / 'desarrollo'),
             'externo': conjuntos.preparar_externo(externo / 'coreano', tmp / 'externo'),
             'legitimas_reales': conjuntos.preparar_legitimas_reales(externo / 'legitimas-reales', tmp / 'legitimas_reales')}
    salida = {}
    for tanda, (nombre, cuales) in TANDAS.items():
        conj = conjs[nombre]
        ref = conj.referencia()
        ids = [i for i in conj.ids if (ref[i]['vista'] == conjuntos.PRINCIPAL) == (cuales == 'principal')]
        salida[tanda] = (conj, ids, ref)
    assert [len(v[1]) for v in salida.values()] == [140, 33, 33, 42], [len(v[1]) for v in salida.values()]
    return salida


# --- La API ---
class ErrorAPI(Exception):
    def __init__(self, mensaje, reintentar):
        super().__init__(mensaje)
        self.reintentar = reintentar


def pedir(clave, cuerpo, timeout=60):
    pedido = urllib.request.Request(URL, data=json.dumps(cuerpo).encode('utf-8'), method='POST',
                                    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {clave}'})
    try:
        with urllib.request.urlopen(pedido, timeout=timeout) as r:
            return json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode('utf-8', errors='replace')[:400]
        raise ErrorAPI(f'http_{e.code}: {detalle}', e.code == 429 or e.code >= 500) from e
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        raise ErrorAPI(f'red: {e}', True) from e


def cuerpo_de(sistema, usuario, temperatura):
    cuerpo = {'model': MODELO, 'input': [{'role': 'system', 'content': sistema}, {'role': 'user', 'content': usuario}],
              'reasoning': {'effort': ESFUERZO}, 'max_output_tokens': MAXIMO_TOKENS, 'store': False,
              'text': {'format': {'type': 'json_schema', 'name': 'salida', 'schema': esquema_estricto(), 'strict': True}}}
    if temperatura is not None:
        cuerpo['temperature'] = temperatura
    return cuerpo


def texto_de(r):
    return ''.join(c.get('text', '') for o in r.get('output', []) if o.get('type') == 'message'
                   for c in o.get('content', []) if c.get('type') == 'output_text')


def consultar(clave, sistema, usuario, temperatura, reintentos=6):
    """(respuesta, ms del intento que respondió, intentos)."""
    for intento in range(1, reintentos + 1):
        inicio = time.perf_counter()
        try:
            r = pedir(clave, cuerpo_de(sistema, usuario, temperatura))
            return r, (time.perf_counter() - inicio) * 1000, intento
        except ErrorAPI as e:
            if not e.reintentar or intento == reintentos:
                raise
            time.sleep(min(2 ** intento, 60))


def temperatura_admitida(clave, sistema, usuario):
    """0.0 si la API acepta temperatura 0 con este modelo y este esfuerzo; None si la rechaza (400 por el parámetro)."""
    try:
        consultar(clave, sistema, usuario, 0.0)
        return 0.0
    except ErrorAPI as e:
        if str(e).startswith('http_400') and 'temperature' in str(e):
            return None
        raise


def red():
    """Resumen de `networkQuality` de macOS (o por qué no se pudo medir)."""
    try:
        s = subprocess.run(['networkQuality', '-s', '-c'], capture_output=True, text=True, timeout=120)
        d = json.loads(s.stdout)
        return {k: d.get(k) for k in ('dl_throughput', 'ul_throughput', 'base_rtt', 'responsiveness', 'interface_name',
                                      'start_date', 'end_date')}
    except Exception as e:  # noqa: BLE001 — es una anotación, no corta la corrida
        return {'error': str(e)}


def commit():
    s = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, cwd=AQUI)
    d = subprocess.run(['git', 'status', '--porcelain', '--', str(AQUI.parents[1])], capture_output=True, text=True,
                       cwd=AQUI)
    return {'commit': s.stdout.strip(), 'cambios_sin_commit_en_la_carpeta': bool(d.stdout.strip())}


def pendientes(todas, hechas):
    """(tanda, caso, línea, líneas con roles) de cada línea de OTRA que falta, en el orden de TANDAS."""
    for tanda, (conj, ids, _) in todas.items():
        for i in ids:
            lineas = conj.con_roles(i, conj.cargar_texto(i))
            for n, l in enumerate(lineas, 1):
                if l.hablante == 'OTRA' and (tanda, i, n) not in hechas:
                    yield tanda, i, n, lineas


def correr(args):
    clave = Path(args.clave).expanduser().read_text(encoding='utf-8').strip()
    assert PROMPT in PROMPTS_CORTE_RIESGO and esquema_de(PROMPT) == ESQUEMA_SALIDA
    sistema = cargar_prompt(PROMPT)
    todas = tandas()
    conj, ids, _ = todas['desarrollo']
    hechas = set()
    if RESULTADOS.exists():
        with open(RESULTADOS, encoding='utf-8', newline='') as f:
            hechas = {(r['tanda'], r['case_id'], int(r['linea'])) for r in csv.DictReader(f)}
    man = json.loads(MANIFIESTO.read_text(encoding='utf-8')) if MANIFIESTO.exists() else None
    if man is None:
        primera = conj.con_roles(ids[0], conj.cargar_texto(ids[0]))
        usuario0 = armar_mensaje_usuario(primera[:next(k for k, l in enumerate(primera, 1) if l.hablante == 'OTRA')], 'rol')
        man = {'modelo': MODELO, 'url': URL, 'prompt': PROMPT, 'prompt_huella': huella(sistema),
               'esfuerzo': ESFUERZO, 'max_output_tokens': MAXIMO_TOKENS, 'esquema': esquema_estricto(),
               'temperatura': temperatura_admitida(clave, sistema, usuario0), 'hablantes': 'rol', 'solo_otra': True,
               'seguir_tras_aviso': True, 'precios_usd_por_millon': PRECIOS, 'red_antes': red(),
               'casos': {t: {i: huella(c.crudo(i)) for i in ii} for t, (c, ii, _) in todas.items()},
               'inicio': datetime.datetime.now().isoformat(), 'codigo': commit()}
        MANIFIESTO.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
    nuevo = not RESULTADOS.exists()
    with open(RESULTADOS, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        hechas_ahora = 0
        for tanda, i, n, lineas in pendientes(todas, hechas):
            usuario = armar_mensaje_usuario(lineas[:n], 'rol')
            fila = {'tanda': tanda, 'case_id': i, 'linea': n, 'hablante': 'OTRA', 'valida': 'false', 'riesgo': ''}
            try:
                r, ms, intentos = consultar(clave, sistema, usuario, man['temperatura'])
            except ErrorAPI as e:
                fila.update(error=str(e)[:200])
            else:
                crudo = texto_de(r)
                riesgo, _, error = leer_riesgo_cortado(crudo)
                u = r.get('usage') or {}
                fila.update(valida='true' if not error else 'false', riesgo='' if riesgo is None else riesgo,
                            error=error, ms=f'{ms:.0f}', intentos=intentos, tokens_entrada=u.get('input_tokens'),
                            tokens_cache=(u.get('input_tokens_details') or {}).get('cached_tokens'),
                            tokens_salida=u.get('output_tokens'), estado=r.get('status'), crudo=crudo)
            w.writerow(fila)
            f.flush()
            hechas_ahora += 1
            if hechas_ahora % 50 == 0:
                print(f'{hechas_ahora} consultas', file=sys.stderr, flush=True)
    man['fin'] = datetime.datetime.now().isoformat()
    man['red_despues'] = red()
    MANIFIESTO.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
    return 0


# --- Análisis ---
def p95(v):
    return statistics.quantiles(v, n=20, method='inclusive')[-1]


def analizar(args):
    todas = tandas()
    man = json.loads(MANIFIESTO.read_text(encoding='utf-8'))
    with open(RESULTADOS, encoding='utf-8', newline='') as f:
        filas = list(csv.DictReader(f))
    etiquetas = json.loads(expl.ETIQUETAS.read_text(encoding='utf-8'))['casos']
    print('# #174, referencia con un modelo de frontera — salida de `referencia.py analizar`\n')
    print(f"Modelo `{man['modelo']}`, esfuerzo `{man['esfuerzo']}`, `max_output_tokens` {man['max_output_tokens']}, "
          f"temperatura {man['temperatura'] if man['temperatura'] is not None else 'por defecto (la API no acepta 0)'}; "
          f"prompt `{man['prompt']}` (huella {man['prompt_huella']}); commit `{man['codigo']['commit'][:10]}`"
          f"{' con cambios sin commitear' if man['codigo']['cambios_sin_commit_en_la_carpeta'] else ''}; "
          f"de {man['inicio'][:16]} a {man.get('fin', '?')[:16]}. Aviso en la primera línea de OTRA con riesgo ≥ 0,3; "
          'las líneas inválidas no avisan.\n')

    print('## Control\n')
    print('| tanda | consultas | inválidas | reintentadas | control |\n|---|---|---|---|---|')
    datos = {}
    for tanda, (conj, ids, ref) in todas.items():
        propias = [r for r in filas if r['tanda'] == tanda]
        por_caso = {i: sorted((r for r in propias if r['case_id'] == i), key=lambda r: int(r['linea'])) for i in ids}
        esperadas = {i: [n for n, l in enumerate(conj.con_roles(i, conj.cargar_texto(i)), 1) if l.hablante == 'OTRA']
                     for i in ids}
        problemas = []
        if any(man['casos'].get(tanda, {}).get(i) != huella(conj.crudo(i)) for i in ids):
            problemas.append('el texto de algún caso no es el del manifiesto')
        faltan = [i for i in ids if [int(r['linea']) for r in por_caso[i]] != esperadas[i]]
        if faltan:
            problemas.append(f'{len(faltan)} casos sin todas sus líneas')
        errores = {}
        for r in propias:
            if r['valida'] != 'true':
                errores[r['error'].split(':')[0]] = errores.get(r['error'].split(':')[0], 0) + 1
        print(f"| {NOMBRES[tanda]} | {len(propias)} de {sum(map(len, esperadas.values()))} | "
              f"{sum(errores.values())} {errores or ''} | {sum(int(r['intentos'] or 1) > 1 for r in propias)} | "
              f"{'; '.join(problemas) or 'bien'} |")
        datos[tanda] = (ids, ref, propias, {i: expl.riesgos(por_caso[i]) for i in ids})
    print()

    def cifras(tanda, u, primeras=None):
        ids, ref, _, riesgos = datos[tanda]
        av = {i: next((n for n, r in l[:primeras] if r >= u), None) for i, l in riesgos.items()}
        e = fin.exitos(av, ids, ref)
        c = {k: '{}/{}'.format(*kn(e[k])) for k in CIFRAS if kn(e[k])[1]}
        if tanda == 'desarrollo':
            estrictas = [i for i in ids if etiquetas.get(i, {}).get('etiqueta') == 'no_avisar']
            c['FA estrictas'] = f'{sum(av[i] is not None for i in estrictas)}/{len(estrictas)}'
        return c, av

    print('## Detección: E2B contra el modelo de la API\n')
    for tanda in todas:
        c, av = cifras(tanda, expl.UMBRAL)
        assert av == {i: expl.primer_aviso(l) for i, l in datos[tanda][3].items()}
        columnas = list(c)
        print(f'### {NOMBRES[tanda]}\n')
        print('| | ' + ' | '.join('avisos' if tanda == 'zona_gris' else k for k in columnas) + ' |\n|---|'
              + '---|' * len(columnas))
        print('| E2B, corrida del 2026-11-20 | ' + ' | '.join(E2B[tanda].get(k, '—') for k in columnas) + ' |')
        print(f"| `{man['modelo']}` | " + ' | '.join(c[k] for k in columnas) + ' |\n')
        ids, ref = datos[tanda][:2]
        est = [av[i] for i in ids if ref[i]['clase'] == 'vishing' and av[i] is not None]
        if est:
            print(f'Línea del aviso en las estafas avisadas: mediana {statistics.median(est):g}.\n')

    print('## Solo para mirar\n')
    print('**Otros cortes** (todas las cifras de la tanda, en el orden de arriba):\n')
    print('| tanda | riesgo ≥ 0,3 | riesgo ≥ 0,5 | riesgo ≥ 0,7 |\n|---|---|---|---|')
    for tanda in todas:
        print(f'| {NOMBRES[tanda]} | ' + ' | '.join(' · '.join(cifras(tanda, u)[0].values()) for u in (0.3, 0.5, 0.7)) + ' |')
    print('\n**Igualando el largo a las primeras 12 consultas de cada llamada** (E2B en la exploración: coreanas 28/33, '
          'legítimas reales 22/33):\n')
    for tanda in ('externo', 'legitimas_reales'):
        c, _ = cifras(tanda, expl.UMBRAL, primeras=12)
        print(f"- {NOMBRES[tanda]}: {c.get('estafas') or c.get('FA')}.")
    print('\n**Valores de riesgo que escribe** (porcentaje de las consultas válidas):\n')
    for tanda in todas:
        validos = [r for l in datos[tanda][3].values() for _, r in l]
        cuenta = {}
        for v in validos:
            cuenta[v] = cuenta.get(v, 0) + 1
        print(f'- {NOMBRES[tanda]} ({len(validos)}): ' + ' · '.join(
            f'{v:g}: {100 * k / len(validos):.0f} %' for v, k in sorted(cuenta.items()) if 100 * k / len(validos) >= 0.5))
    print()

    print('## Latencia por consulta (tiempo de pared desde esta Mac, una consulta por vez)\n')
    print('| tanda | consultas | mediana | p95 | máximo | tokens de entrada, mediana |\n|---|---|---|---|---|---|')
    for tanda in [*todas, None]:
        propias = filas if tanda is None else datos[tanda][2]
        ms = [float(r['ms']) for r in propias if r['ms']]
        tok = [int(r['tokens_entrada']) for r in propias if r['tokens_entrada'] not in ('', 'None')]
        print(f"| {'**todas**' if tanda is None else NOMBRES[tanda]} | {len(ms)} | {statistics.median(ms) / 1000:.2f} s | "
              f'{p95(ms) / 1000:.2f} s | {max(ms) / 1000:.2f} s | {statistics.median(tok):,.0f} |')
    print(f'\nE2B: {E2B_LATENCIA}.\n')
    for cuando in ('red_antes', 'red_despues'):
        d = man.get(cuando) or {}
        if 'error' in d or not d:
            print(f'- Conexión ({cuando}): no se pudo medir ({d.get("error", "falta")}).')
        else:
            print(f"- Conexión ({cuando}, {d.get('interface_name')}): bajada {d['dl_throughput'] / 1e6:.0f} Mbit/s, "
                  f"subida {d['ul_throughput'] / 1e6:.0f} Mbit/s, RTT base {d.get('base_rtt')} ms.")
    print()

    def entero(r, c):
        return int(r[c]) if r[c] not in ('', 'None', None) else 0

    print('## Costo estimado (precios del 2026-11-20)\n')
    print('| tanda | tokens de entrada | en caché | de salida | US$ total | US$ por consulta | US$ por llamada | '
          'sin caché, US$ |\n|---|---|---|---|---|---|---|---|')
    for tanda in [*todas, None]:
        propias = filas if tanda is None else datos[tanda][2]
        llamadas = len({(r['tanda'], r['case_id']) for r in propias})
        entrada, cache, salida = (sum(entero(r, c) for r in propias) for c in ('tokens_entrada', 'tokens_cache', 'tokens_salida'))
        costo = ((entrada - cache) * PRECIOS['entrada'] + cache * PRECIOS['entrada_cache'] + salida * PRECIOS['salida']) / 1e6
        sin_cache = (entrada * PRECIOS['entrada'] + salida * PRECIOS['salida']) / 1e6
        print(f"| {'**todas**' if tanda is None else NOMBRES[tanda]} | {entrada:,} | {cache:,} | {salida:,} | {costo:.2f} | "
              f'{costo / len(propias):.5f} | {costo / llamadas:.4f} | {sin_cache:.2f} |')
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest='orden', required=True)
    c = sub.add_parser('correr')
    c.add_argument('--clave', required=True, help='archivo con la clave de OpenAI, fuera del repositorio')
    sub.add_parser('analizar')
    args = p.parse_args(argv)
    return correr(args) if args.orden == 'correr' else analizar(args)


if __name__ == '__main__':
    sys.exit(main())
