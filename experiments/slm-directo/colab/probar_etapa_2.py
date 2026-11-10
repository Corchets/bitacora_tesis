#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-ETAPA-2.ipynb: ver README-PUNTAJE-TOKEN.md (sección 5).
# Estado: propuesta sin discutir. #143, segunda vuelta, etapa 2, sobre los 244 casos de desarrollo (los 150 de antes
# y las 94 legítimas entrantes de #155); esta rama no contiene el test reservado.
#
# Pregunta: ¿el prompt C (intención y alcance) o v4-premisa (v4 + una oración de alcance) le ganan a v4 dentro del
# alcance (las 46 estafas de corpus_v2 y las 94 legítimas entrantes)? Todos con el JSON cortado después de
# `alerta_sugerida` y el motivo aparte, solo al avisar (ADR 0006). La regla y las vistas están escritas antes de correr
# en corridas/2026-11-07_alcance-etapa-2/analizar.py. Mismo modelo, digest, Ollama, num_ctx, seed y temperatura que
# las líneas base.
#
# 1. Humo de formato de los dos prompts cortados nuevos, en los 3 casos de las humos anteriores (48 líneas). Criterio,
#    fijado antes de correr, para cada uno:
#    a) con el JSON completo del prompt base y logprobs, el valor de `alerta_sugerida` termina a más tardar en el
#       token MAXIMO_TOKENS_CORTE en las 48 líneas;
#    b) el prompt cortado lee riesgo y alerta en las 48 líneas.
#    Dato, sin criterio: en cuántas de las 48 el cortado escribe el mismo riesgo y la misma alerta que el completo.
#    El prompt que no pasa no corre y queda anotado; no se ajusta nada en esta sesión (ADR 0005).
# 2. Corridas en todas las líneas (--seguir-tras-aviso), una candidata entera antes de la siguiente: v4-corte sobre
#    los 244 (referencia); c-json-corte sobre los 244 y su repetición sobre los 140 dentro del alcance
#    (casos/listas/alcance-140.txt); lo mismo con v4-premisa-corte.
# 3. Los controles de ventas y préstamos (casos/controles-ventas.json), solo para mirar, con los tres.
# Cada etapa terminada baja como ZIP. El análisis va después, con analizar.py.

import csv, hashlib, json, os, pathlib, shutil, statistics, subprocess, sys, time, urllib.request

REPO = pathlib.Path('/content/bitacora_tesis')
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path('/content/resultados-etapa-2')
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base, la etapa 1 y el JSON cortado: un cambio por vez.
OLLAMA_VERSION = '0.40.14'
subprocess.run(['apt-get', 'install', '-y', 'zstd'], check=True)
subprocess.run(f'curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION={OLLAMA_VERSION} sh', shell=True, check=True)

os.environ['OLLAMA_HOST'] = '127.0.0.1:11434'
ollama_log = open('/content/ollama-colab.log', 'a')
ollama_proc = subprocess.Popen(['ollama', 'serve'], stdout=ollama_log, stderr=subprocess.STDOUT)
for _ in range(60):
    if subprocess.run(['ollama', 'list'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        break
    time.sleep(2)
else:
    raise RuntimeError('Ollama no inició; revisar /content/ollama-colab.log')
version = subprocess.check_output(['ollama', '--version'], text=True)
print(version)
if OLLAMA_VERSION not in version:
    raise RuntimeError(f'Ollama quedó en otra versión ({version.strip()}); detener y revisar.')
MODEL = 'gemma4:e2b-it-q4_K_M'
subprocess.run(['ollama', 'pull', MODEL], check=True)
with urllib.request.urlopen('http://127.0.0.1:11434/api/tags') as response:
    models = json.load(response)['models']
model = next(m for m in models if m['name'] == MODEL)
expected = 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2'
print('Digest:', model['digest'])
if model['digest'].removeprefix('sha256:') != expected:
    raise RuntimeError('Digest distinto al de las líneas base; detener y revisar.')
(SALIDA / 'digest.txt').write_text(f"{MODEL} {model['digest']}\n", encoding='utf-8')

exp = REPO / 'experiments/slm-directo'
os.chdir(exp)
sys.path.insert(0, str(exp))
import casos  # noqa: E402
from detectores import (CORTE_DE, ESQUEMA_SALIDA, MAXIMO_TOKENS_CORTE, DetectorSLM, cargar_prompt,  # noqa: E402
                        leer_json_cortado)

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--seguir-tras-aviso',
           '--hablantes', 'rol']
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48
NUEVOS = ['c-json-corte', 'v4-premisa-corte']  # v4-corte ya pasó su humo (colab/143-json-cortado: 23 tokens en las 48)


def descargar(carpeta, nombre):
    from google.colab import files
    archivo = shutil.make_archive(f'/content/{nombre}', 'zip', carpeta)
    print(f'Descargando {archivo}', flush=True)
    files.download(archivo)


def correr(destino, etiqueta, *args):
    shutil.rmtree(destino, ignore_errors=True)  # una corrida cortada se repite entera
    destino.mkdir(parents=True)
    orden = [sys.executable, *args, *COMUNES, '--etiqueta', etiqueta, '--salida', str(destino)]
    print('Ejecutando:', ' '.join(orden), flush=True)
    subprocess.run(orden, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
    return run


def tokens_hasta_alerta(pasos):
    """Cuántos tokens del JSON completo hacen falta para que se lea el valor de `alerta_sugerida` (None si nunca)."""
    texto = ''
    for i, paso in enumerate(pasos, start=1):
        texto += paso.get('token', '')
        if not leer_json_cortado(texto)[3]:
            return i
    return None


# 1. Humo de formato.
humo_dir = SALIDA / 'humo'
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', {p: 'PASA' if d['pasa'] else 'NO PASA' for p, d in humo.items()}, flush=True)
else:
    # b) Los dos cortados en las 48 líneas, por correr.py (con la segunda consulta en las líneas de aviso).
    run = correr(humo_dir / 'corrida', 'etapa-2-humo', 'correr.py', '--casos', ','.join(HUMO_CASOS),
                 '--prompts', ','.join(NUEVOS))
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        cortadas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    humo, diagnostico, salida = {}, {}, ['# Humo de los prompts cortados nuevos (etapa 2 de #143)', '',
                                         f'Commit `{COMMIT}`. Casos: {", ".join(HUMO_CASOS)} ({LINEAS_HUMO} líneas). '
                                         f'num_predict: {MAXIMO_TOKENS_CORTE}.', '',
                                         f'Criterio, fijado antes de correr: con el JSON completo del prompt base, la alerta '
                                         f'termina a más tardar en el token {MAXIMO_TOKENS_CORTE} en las {LINEAS_HUMO} líneas, '
                                         f'y el cortado lee riesgo y alerta en las {LINEAS_HUMO}. El que no pasa no corre.', '',
                                         '| prompt | tokens hasta la alerta (mín / mediana / máx) | líneas que alcanzan | '
                                         'cortado, líneas leídas | mismo riesgo y alerta que el completo (dato) | resultado |',
                                         '|---|---|---|---|---|---|']
    for prompt in NUEVOS:
        # a) Tokens hasta la alerta con el JSON completo del prompt base: el mismo pedido que correr.py (think false,
        #    como en las líneas base), con logprobs solo para ver los tokens.
        detector = DetectorSLM(None, MODEL, cargar_prompt(CORTE_DE[prompt]), 'rol')
        filas_prompt = {(r['case_id'], int(r['linea'])): r for r in cortadas if r['prompt'] == prompt}
        diag = []
        for case_id in HUMO_CASOS:
            lineas = casos.con_roles(case_id, casos.cargar_texto(case_id))
            for n in range(1, len(lineas) + 1):
                mensajes, _ = detector.mensajes(lineas[:n])
                cuerpo = {'model': MODEL, 'messages': mensajes, 'format': ESQUEMA_SALIDA, 'options': detector.opciones(),
                          'stream': False, 'think': False, 'logprobs': True, 'top_logprobs': 1}
                pedido = urllib.request.Request('http://127.0.0.1:11434/api/chat', data=json.dumps(cuerpo).encode(),
                                                headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(pedido, timeout=600) as r:
                    respuesta = json.load(r)
                pasos = respuesta.get('logprobs') or []
                texto = respuesta.get('message', {}).get('content', '')
                completo = leer_json_cortado(texto)[:2]
                fila = filas_prompt.get((case_id, n))
                cortado = (float(fila['riesgo']) if fila and fila['riesgo'] else None,
                           None if not fila or not fila['alerta_escrita'] else fila['alerta_escrita'] == 'true')
                diag.append({'case_id': case_id, 'linea': n, 'texto': texto, 'tokens_hasta_alerta': tokens_hasta_alerta(pasos),
                             'tokens': [p.get('token') for p in pasos], 'completo': completo, 'cortado': cortado})
        necesarios = [d['tokens_hasta_alerta'] for d in diag]
        validos = [t for t in necesarios if t is not None]
        alcanzan = sum(t is not None and t <= MAXIMO_TOKENS_CORTE for t in necesarios)
        leidas = sum(r['valida'] == 'true' for r in filas_prompt.values())
        iguales = sum(d['completo'] == d['cortado'] for d in diag)
        humo[prompt] = {
            'base': CORTE_DE[prompt], 'num_predict': MAXIMO_TOKENS_CORTE, 'lineas': len(diag), 'alcanzan': alcanzan,
            'tokens_hasta_alerta': {'min': min(validos, default=None), 'mediana': statistics.median(validos) if validos else None,
                                    'max': max(validos, default=None), 'sin_alerta': necesarios.count(None)},
            'cortado_lineas': len(filas_prompt), 'cortado_leidas': leidas, 'iguales_al_completo': iguales,
            'cortado_errores': sorted({r['error'] for r in filas_prompt.values() if r['valida'] != 'true'}),
            'segunda_consulta': [{'case_id': r['case_id'], 'linea': r['linea'], 'ms_etapa2': r['ms_etapa2'], 'error': r['error'],
                                  'motivo': r['motivo'], 'evidencia': r['evidencia']}
                                 for r in filas_prompt.values() if r['ms_etapa2']],
        }
        humo[prompt]['pasa'] = len(diag) == len(filas_prompt) == LINEAS_HUMO and alcanzan == leidas == LINEAS_HUMO
        diagnostico[prompt] = diag
        t = humo[prompt]['tokens_hasta_alerta']
        salida.append(f'| `{prompt}` | {t["min"]} / {t["mediana"]} / {t["max"]} (sin alerta: {t["sin_alerta"]}) | '
                      f'{alcanzan}/{len(diag)} | {leidas}/{len(filas_prompt)} | {iguales}/{len(diag)} | '
                      f'{"PASA" if humo[prompt]["pasa"] else "NO PASA"} |')
    for prompt in NUEVOS:
        h = humo[prompt]
        salida += ['', f'`{prompt}`: segunda consulta en {len(h["segunda_consulta"])} líneas de aviso:', '']
        salida += [f'- {s["case_id"]} L{s["linea"]}: {s["ms_etapa2"]} ms {s["error"]} — {s["motivo"]!r} / {s["evidencia"]!r}'
                   for s in h['segunda_consulta']]
        salida += ['', f'`{prompt}`: líneas que no alcanzan:', '']
        salida += [f'- {d["case_id"]} L{d["linea"]}: {d["tokens_hasta_alerta"]} tokens; {d["tokens"][:30]}'
                   for d in diagnostico[prompt]
                   if d['tokens_hasta_alerta'] is None or d['tokens_hasta_alerta'] > MAXIMO_TOKENS_CORTE]
    (humo_dir / 'tokens-hasta-alerta.json').write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.md').write_text('\n'.join(salida) + '\n', encoding='utf-8')
    print('\n'.join(salida), flush=True)
    descargar(humo_dir, 'parcial-etapa-2-humo')

pasan = {'v4-corte'} | {p for p, d in humo.items() if d['pasa']}
if pasan == {'v4-corte'}:
    raise RuntimeError('Ningún prompt nuevo pasó la humo: no se corre nada. Ver humo/humo.md.')

# 2. Una candidata entera (corrida y repetición) antes de la siguiente, para que un corte de Colab deje una respuesta.
CORRIDAS = [
    # (carpeta, descripción, prompt, lista; None = los 244)
    ('v4-corte', 'Referencia: el JSON de v4 cortado (ADR 0006), sobre los 244', 'v4-corte', None),
    ('c-json-corte', 'Candidata: el prompt C con el JSON cortado, sobre los 244', 'c-json-corte', None),
    ('c-json-corte-rep', 'Repetición de c-json-corte, sobre los 140 dentro del alcance', 'c-json-corte', 'alcance-140'),
    ('v4-premisa-corte', 'Candidata: v4 con la oración del alcance, cortado, sobre los 244', 'v4-premisa-corte', None),
    ('v4-premisa-corte-rep', 'Repetición de v4-premisa-corte, sobre los 140 dentro del alcance', 'v4-premisa-corte',
     'alcance-140'),
]
for carpeta, descripcion, prompt, lista in CORRIDAS:
    destino = SALIDA / carpeta
    if prompt not in pasan:
        print(f'[{carpeta}] no corre: {prompt} no pasó la humo.', flush=True)
        continue
    if (destino / 'TERMINADA.txt').exists():
        print(f'[{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
        continue
    print(f'[{carpeta}] {descripcion}', flush=True)
    inicio = time.time()
    run = correr(destino, f'etapa-2-{carpeta}', 'correr.py', '--prompts', prompt, *(['--lista', lista] if lista else []))
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    print(f'[{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
    descargar(destino, f'parcial-etapa-2-{carpeta}')

# 3. Controles de ventas y préstamos, solo para mirar.
destino = SALIDA / 'controles-ventas'
if not (destino / 'TERMINADA.txt').exists():
    prompts = [p for p in ('v4-corte', *NUEVOS) if p in pasan]
    inicio = time.time()
    correr(destino, 'etapa-2-controles-ventas', 'correr_controles.py', '--controles', 'casos/controles-ventas.json',
           '--prompts', ','.join(prompts))
    (destino / 'TERMINADA.txt').write_text(f'Controles de ventas con {", ".join(prompts)}\ncommit {COMMIT}\n'
                                           f'minutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    descargar(destino, 'parcial-etapa-2-controles-ventas')

# 4. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_etapa_2.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143, segunda vuelta, etapa 2: v4-corte, c-json-corte y v4-premisa-corte sobre los 244, con las '
    f'repeticiones de las candidatas sobre alcance-140, y los controles de ventas\nIDS=(los 244)\n', encoding='utf-8')
zip_local = shutil.make_archive('/content/resultados-etapa-2', 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
