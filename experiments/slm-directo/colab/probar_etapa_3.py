#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-ETAPA-3.ipynb: ver README-PUNTAJE-TOKEN.md (sección 6).
# Estado: propuesta sin discutir. #143, segunda vuelta, etapa 3, sobre los 244 casos de desarrollo; esta rama no
# contiene el test reservado.
#
# Pregunta: ¿C con campo le gana a C sin alerta dentro del alcance? Las dos usan el texto de tarea de C con un JSON
# corto, en una sola consulta por línea: «C sin alerta» (la base) pide solo el riesgo, y «C con campo» pide
# `pedido_critico` y después el riesgo (prompts/salida_json_c_con_campo.txt, con la definición de Mateo). Avisan con
# «riesgo ≥ 0,3», o `pedido_critico` en C con campo. El motivo propio de C (prompts/motivo_c_corte.txt) se pide solo en
# la primera alerta fuerte (`pedido_critico` en true): el primer aviso muestra un texto fijo. La regla y las vistas están escritas antes de correr en
# corridas/2026-11-09_pedido-critico-etapa-3/analizar.py. Mismo modelo, digest, Ollama, num_ctx, seed y temperatura que
# la etapa 2.
#
# 1. Humo de formato en los 3 casos de las humos anteriores (48 líneas), en una sola corrida: c-json-corte (C como
#    corrió en la etapa 2), c-sin-alerta y c-con-campo. Criterio, fijado antes de correr: cada versión lee el JSON en las
#    48 líneas, sin llegar al tope de MAXIMO_TOKENS_C_CORTO. Datos, sin criterio: los tokens generados, el riesgo contra
#    el de c-json-corte, cuántas veces escribe `pedido_critico` en true y el motivo de la alerta fuerte. La versión que
#    no pasa no corre; si no pasa ninguna, no corre nada. No se ajusta nada en esta sesión (ADR 0005).
# 2. Corridas en todas las líneas (--seguir-tras-aviso), en este orden: c-sin-alerta y c-con-campo sobre los 244, y
#    después sus repeticiones sobre los 140 dentro del alcance (casos/listas/alcance-140.txt).
# 3. Los controles de ventas y préstamos (casos/controles-ventas.json), solo para mirar, con las dos.
# Cada etapa terminada baja como ZIP. El análisis va después, con analizar.py.
# COLAB_REPO y COLAB_SALIDA solo existen para la prueba en seco; en Colab quedan los valores por defecto.

import csv, hashlib, json, os, pathlib, shutil, statistics, subprocess, sys, time, urllib.request

REPO = pathlib.Path(os.environ.get('COLAB_REPO', '/content/bitacora_tesis'))
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path(os.environ.get('COLAB_SALIDA', '/content/resultados-etapa-3'))
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base y las etapas 1 y 2: un cambio por vez.
OLLAMA_VERSION = '0.40.14'
subprocess.run(['apt-get', 'install', '-y', 'zstd'], check=True)
subprocess.run(f'curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION={OLLAMA_VERSION} sh', shell=True, check=True)

os.environ['OLLAMA_HOST'] = '127.0.0.1:11434'
ollama_log = open(SALIDA.parent / 'ollama-colab.log', 'a')
ollama_proc = subprocess.Popen(['ollama', 'serve'], stdout=ollama_log, stderr=subprocess.STDOUT)
for _ in range(60):
    if subprocess.run(['ollama', 'list'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        break
    time.sleep(2)
else:
    raise RuntimeError(f'Ollama no inició; revisar {SALIDA.parent / "ollama-colab.log"}')
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

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--seguir-tras-aviso',
           '--hablantes', 'rol']
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48
NUEVOS = ['c-sin-alerta', 'c-con-campo']


def descargar(carpeta, nombre):
    from google.colab import files
    archivo = shutil.make_archive(str(SALIDA.parent / nombre), 'zip', carpeta)
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


def resumen_tokens(valores):
    return f'{min(valores)} / {statistics.median(valores):g} / {max(valores)}' if valores else '—'


# 1. Humo de formato.
humo_dir = SALIDA / 'humo'
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', {p: 'PASA' if d['pasa'] else 'NO PASA' for p, d in humo.items()}, flush=True)
else:
    run = correr(humo_dir / 'corrida', 'etapa-3-humo', 'correr.py', '--casos', ','.join(HUMO_CASOS),
                 '--prompts', ','.join(['c-json-corte', *NUEVOS]))
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    por = {p: {(r['case_id'], int(r['linea'])): r for r in filas if r['prompt'] == p} for p in ['c-json-corte', *NUEVOS]}
    humo, salida = {}, ['# Humo de la etapa 3 de #143: C sin alerta y C con campo', '',
                        f'Commit `{COMMIT}`. Casos: {", ".join(HUMO_CASOS)} ({LINEAS_HUMO} líneas). Tope: '
                        '`num_predict` 48; el modelo cierra el JSON solo.', '',
                        f'Criterio, fijado antes de correr: cada versión lee el JSON en las {LINEAS_HUMO} líneas, sin '
                        'llegar al tope. La que no pasa no corre; si no pasa ninguna, no corre nada.', '',
                        '| prompt | JSON leído | llegan al tope | tokens generados (mín / mediana / máx) | mismo riesgo que '
                        'c-json-corte (dato) | pedido_critico en true (dato) | resultado |', '|---|---|---|---|---|---|---|']
    for prompt in NUEVOS:
        propias = por[prompt]
        leidas = sum(r['valida'] == 'true' for r in propias.values())
        al_tope = sum(r['error'] == 'salida_cortada' for r in propias.values())
        tokens = [int(r['tokens_salida']) for r in propias.values() if r['tokens_salida']]
        iguales = sum(r['riesgo'] != '' and k in por['c-json-corte'] and r['riesgo'] == por['c-json-corte'][k]['riesgo']
                      for k, r in propias.items())
        campo = sum(r['pedido_critico'] == 'true' for r in propias.values()) if prompt == 'c-con-campo' else None
        humo[prompt] = {
            'lineas': len(propias), 'leidas': leidas, 'al_tope': al_tope, 'tokens_salida': resumen_tokens(tokens),
            'igual_a_c_json_corte': iguales, 'campo_true': campo,
            'errores': sorted({r['error'] for r in propias.values() if r['valida'] != 'true'}),
            'segunda_consulta': [{'case_id': k[0], 'linea': k[1], 'ms_etapa2': r['ms_etapa2'], 'error': r['error'],
                                  'motivo': r['motivo'], 'evidencia': r['evidencia']}
                                 for k, r in sorted(propias.items()) if r['ms_etapa2']],
        }
        humo[prompt]['pasa'] = len(propias) == leidas == LINEAS_HUMO
        h = humo[prompt]
        salida.append(f'| `{prompt}` | {leidas}/{len(propias)} | {al_tope} | {h["tokens_salida"]} | {iguales}/{len(propias)} | '
                      f'{"—" if campo is None else campo} | {"PASA" if h["pasa"] else "NO PASA"} |')
    for prompt in NUEVOS:
        h = humo[prompt]
        salida += ['', f'`{prompt}`: segunda consulta (motivo_c_corte.txt) en {len(h["segunda_consulta"])} alertas fuertes:', '']
        salida += [f'- {s["case_id"]} L{s["linea"]}: {s["ms_etapa2"]} ms {s["error"]} — {s["motivo"]!r} / {s["evidencia"]!r}'
                   for s in h['segunda_consulta']]
        if h['errores']:
            salida += ['', f'`{prompt}`: errores {h["errores"]}']
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.md').write_text('\n'.join(salida) + '\n', encoding='utf-8')
    print('\n'.join(salida), flush=True)
    descargar(humo_dir, 'parcial-etapa-3-humo')

pasan = {p for p, d in humo.items() if d['pasa']}
if not pasan:
    raise RuntimeError('Ninguna versión pasó la humo: no se corre nada. Ver humo/humo.md.')

# 2. Primero las dos versiones sobre los 244, así un corte de Colab deja la comparación; después las repeticiones.
CORRIDAS = [
    # (carpeta, descripción, prompt, lista; None = los 244)
    ('c-sin-alerta', 'Base: C sin alerta (el JSON pide solo el riesgo), sobre los 244', 'c-sin-alerta', None),
    ('c-con-campo', 'Candidata: C con campo (pedido_critico y riesgo), sobre los 244', 'c-con-campo', None),
    ('c-sin-alerta-rep', 'Repetición de c-sin-alerta, sobre los 140 dentro del alcance', 'c-sin-alerta', 'alcance-140'),
    ('c-con-campo-rep', 'Repetición de c-con-campo, sobre los 140 dentro del alcance', 'c-con-campo', 'alcance-140'),
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
    run = correr(destino, f'etapa-3-{carpeta}', 'correr.py', '--prompts', prompt, *(['--lista', lista] if lista else []))
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    print(f'[{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
    descargar(destino, f'parcial-etapa-3-{carpeta}')

# 3. Controles de ventas y préstamos, solo para mirar.
destino = SALIDA / 'controles-ventas'
if not (destino / 'TERMINADA.txt').exists():
    prompts = [p for p in NUEVOS if p in pasan]
    inicio = time.time()
    correr(destino, 'etapa-3-controles-ventas', 'correr_controles.py', '--controles', 'casos/controles-ventas.json',
           '--prompts', ','.join(prompts))
    (destino / 'TERMINADA.txt').write_text(f'Controles de ventas con {", ".join(prompts)}\ncommit {COMMIT}\n'
                                           f'minutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    descargar(destino, 'parcial-etapa-3-controles-ventas')

# 4. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_etapa_3.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143, segunda vuelta, etapa 3: c-sin-alerta y c-con-campo sobre los 244, con sus repeticiones sobre '
    f'alcance-140, y los controles de ventas\nIDS=(los 244)\n', encoding='utf-8')
zip_local = shutil.make_archive(str(SALIDA.parent / 'resultados-etapa-3'), 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
