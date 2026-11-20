"""#174, referencia: el detector `c-consejos-corte-riesgo` con un modelo de frontera por API (OpenAI), sobre alcance-140.

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
CAMPOS = ['case_id', 'linea', 'hablante', 'valida', 'riesgo', 'error', 'ms', 'intentos', 'tokens_entrada',
          'tokens_cache', 'tokens_salida', 'estado', 'crudo']
# E2B con la misma configuración, corrida del 2026-11-20 (../2026-11-20_exploracion-reales/analisis-salida.md).
E2B = {'estafas': '43/46', 'antes del pedido': '18/36', 'a tiempo': '29/36', 'antes del cumplimiento': '14/15',
       'FA': '20/94', 'FA estrictas': '8/75'}
E2B_LATENCIA = 'teléfono (Samsung A56, CPU): 3,60 s de mediana y 4,90 s de p95 por línea de OTRA'
CIFRAS = ['estafas', 'antes del pedido', 'a tiempo', 'antes del cumplimiento', 'FA']


def esquema_estricto():
    """ESQUEMA_SALIDA como lo pide la salida estructurada estricta: mismos campos, mismo orden, sin otros."""
    return {**ESQUEMA_SALIDA, 'additionalProperties': False}


def desarrollo():
    """(conjunto, ids de alcance-140, referencia), armado en un directorio temporal fuera del repositorio."""
    tmp = Path(tempfile.mkdtemp(prefix='referencia-174-'))
    conj = conjuntos.preparar_desarrollo(tmp / 'desarrollo')
    ref = conj.referencia()
    ids = [i for i in conj.ids if ref[i]['vista'] == conjuntos.PRINCIPAL]
    assert len(ids) == 140, len(ids)
    return conj, ids, ref


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


def correr(args):
    clave = Path(args.clave).expanduser().read_text(encoding='utf-8').strip()
    assert PROMPT in PROMPTS_CORTE_RIESGO and esquema_de(PROMPT) == ESQUEMA_SALIDA
    sistema = cargar_prompt(PROMPT)
    conj, ids, _ = desarrollo()
    hechas = set()
    if RESULTADOS.exists():
        with open(RESULTADOS, encoding='utf-8', newline='') as f:
            hechas = {(r['case_id'], int(r['linea'])) for r in csv.DictReader(f)}
    man = json.loads(MANIFIESTO.read_text(encoding='utf-8')) if MANIFIESTO.exists() else None
    if man is None:
        primera = conj.con_roles(ids[0], conj.cargar_texto(ids[0]))
        usuario0 = armar_mensaje_usuario(primera[:next(k for k, l in enumerate(primera, 1) if l.hablante == 'OTRA')], 'rol')
        man = {'modelo': MODELO, 'url': URL, 'prompt': PROMPT, 'prompt_huella': huella(sistema),
               'esfuerzo': ESFUERZO, 'max_output_tokens': MAXIMO_TOKENS, 'esquema': esquema_estricto(),
               'temperatura': temperatura_admitida(clave, sistema, usuario0), 'hablantes': 'rol', 'solo_otra': True,
               'seguir_tras_aviso': True, 'precios_usd_por_millon': PRECIOS, 'red_antes': red(),
               'casos': {i: huella(conj.crudo(i)) for i in ids}, 'inicio': datetime.datetime.now().isoformat(),
               'codigo': commit()}
        MANIFIESTO.write_text(json.dumps(man, ensure_ascii=False, indent=1), encoding='utf-8')
    nuevo = not RESULTADOS.exists()
    with open(RESULTADOS, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        hechas_ahora = 0
        for i in ids:
            lineas = conj.con_roles(i, conj.cargar_texto(i))
            for n, l in enumerate(lineas, 1):
                if l.hablante != 'OTRA' or (i, n) in hechas:
                    continue
                usuario = armar_mensaje_usuario(lineas[:n], 'rol')
                fila = {'case_id': i, 'linea': n, 'hablante': 'OTRA', 'valida': 'false', 'riesgo': ''}
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
    conj, ids, ref = desarrollo()
    man = json.loads(MANIFIESTO.read_text(encoding='utf-8'))
    with open(RESULTADOS, encoding='utf-8', newline='') as f:
        filas = list(csv.DictReader(f))
    por_caso = {i: sorted((r for r in filas if r['case_id'] == i), key=lambda r: int(r['linea'])) for i in ids}
    esperadas = {i: [n for n, l in enumerate(conj.con_roles(i, conj.cargar_texto(i)), 1) if l.hablante == 'OTRA']
                 for i in ids}
    problemas = [i for i in ids if [int(r['linea']) for r in por_caso[i]] != esperadas[i]]
    if any(man['casos'].get(i) != huella(conj.crudo(i)) for i in ids):
        problemas.append('el texto de algún caso no es el del manifiesto')
    print('# #174, referencia con un modelo de frontera — salida de `referencia.py analizar`\n')
    print(f"Modelo `{man['modelo']}`, esfuerzo `{man['esfuerzo']}`, `max_output_tokens` {man['max_output_tokens']}, "
          f"temperatura {man['temperatura'] if man['temperatura'] is not None else 'por defecto (la API no acepta 0)'}; "
          f"prompt `{man['prompt']}` (huella {man['prompt_huella']}); commit `{man['codigo']['commit'][:10]}`"
          f"{' con cambios sin commitear' if man['codigo']['cambios_sin_commit_en_la_carpeta'] else ''}; "
          f"de {man['inicio'][:16]} a {man.get('fin', '?')[:16]}.\n")
    print(f"Control: {len(filas)} consultas de {sum(map(len, esperadas.values()))}; "
          f"{'bien' if not problemas else 'problemas: ' + ', '.join(problemas[:5])}.\n")
    invalidas = [r for r in filas if r['valida'] != 'true']
    errores = {}
    for r in invalidas:
        errores[r['error'].split(':')[0]] = errores.get(r['error'].split(':')[0], 0) + 1
    print(f'Inválidas: {len(invalidas)} {errores or ""}. Reintentos: '
          f"{sum(int(r['intentos'] or 1) > 1 for r in filas)} consultas.\n")

    riesgos = {i: expl.riesgos(por_caso[i]) for i in ids}
    etiquetas = json.loads(expl.ETIQUETAS.read_text(encoding='utf-8'))['casos']
    estrictas = [i for i in ids if etiquetas.get(i, {}).get('etiqueta') == 'no_avisar']

    def cifras(u):
        av = {i: next((n for n, r in l if r >= u), None) for i, l in riesgos.items()}
        e = fin.exitos(av, ids, ref)
        c = {k: '{}/{}'.format(*kn(e[k])) for k in CIFRAS}
        c['FA estrictas'] = f'{sum(av[i] is not None for i in estrictas)}/{len(estrictas)}'
        return c, av

    principal, av = cifras(expl.UMBRAL)
    assert av == {i: expl.primer_aviso(l) for i, l in riesgos.items()}
    columnas = CIFRAS + ['FA estrictas']
    print('## Detección (aviso en la primera línea de OTRA con riesgo ≥ 0,3)\n')
    print('| | ' + ' | '.join(columnas) + ' |\n|---|' + '---|' * len(columnas))
    print('| E2B, corrida del 2026-11-20 | ' + ' | '.join(E2B[c] for c in columnas) + ' |')
    print(f"| `{man['modelo']}` | " + ' | '.join(principal[c] for c in columnas) + ' |\n')
    print('## Otros cortes, solo para mirar\n')
    print('| riesgo ≥ | ' + ' | '.join(columnas) + ' |\n|---|' + '---|' * len(columnas))
    for u in (0.5, 0.7):
        c, _ = cifras(u)
        print(f'| {u:g} | ' + ' | '.join(c[k] for k in columnas) + ' |')
    print()
    validos = [float(r['riesgo']) for r in filas if r['valida'] == 'true']
    cuenta = {}
    for v in validos:
        cuenta[v] = cuenta.get(v, 0) + 1
    print('## Valores de riesgo que escribe\n')
    print(' · '.join(f'{v:g}: {100 * k / len(validos):.0f} %' for v, k in sorted(cuenta.items())
                     if 100 * k / len(validos) >= 0.5) + '\n')
    est = [i for i in ids if ref[i]['clase'] == 'vishing']
    linea_aviso = [av[i] for i in est if av[i] is not None]
    print(f'Línea del aviso en las estafas avisadas: mediana {statistics.median(linea_aviso):g}.\n')

    ms = [float(r['ms']) for r in filas if r['ms']]
    print('## Latencia por consulta (tiempo de pared desde esta Mac)\n')
    print(f'- Mediana {statistics.median(ms) / 1000:.2f} s, p95 {p95(ms) / 1000:.2f} s, máximo {max(ms) / 1000:.2f} s '
          f'({len(ms)} consultas que respondieron).')
    print(f'- E2B: {E2B_LATENCIA}.')
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
    entrada = sum(entero(r, 'tokens_entrada') for r in filas)
    cache = sum(entero(r, 'tokens_cache') for r in filas)
    salida = sum(entero(r, 'tokens_salida') for r in filas)
    costo = ((entrada - cache) * PRECIOS['entrada'] + cache * PRECIOS['entrada_cache'] + salida * PRECIOS['salida']) / 1e6
    llamadas = len(ids)
    print('## Costo estimado (precios del 2026-11-20)\n')
    print(f'- Tokens: {entrada:,} de entrada ({cache:,} en caché) y {salida:,} de salida.')
    print(f'- Total US$ {costo:.2f}: US$ {costo / len(filas):.5f} por consulta y US$ {costo / llamadas:.4f} por llamada '
          f'({len(filas) / llamadas:.1f} consultas por llamada).')
    sin_cache = (entrada * PRECIOS['entrada'] + salida * PRECIOS['salida']) / 1e6
    print(f'- Sin caché sería US$ {sin_cache:.2f}.')
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
