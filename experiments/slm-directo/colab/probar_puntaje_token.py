#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-PUNTAJE-TOKEN.ipynb: ver README-PUNTAJE-TOKEN.md.
# Estado: propuesta sin discutir. Prueba de desarrollo de #143 sobre las 150 conversaciones;
# esta rama no contiene el test reservado.
#
# Lee P(SÍ) del primer token en todas las líneas (--seguir-tras-aviso), para simular las políticas
# de aviso offline: A1 (`v4-a1` + rol, `tarea-a1` + ab) y A2 (`v4-a2` + rol), cada una con una
# repetición para medir el ruido. Mismo modelo, digest, Ollama, num_ctx, seed y hablantes que las
# líneas base JSON (2026-11-04_sin-indicio-150 y 2026-11-05_tito-2-v4).
# El notebook deja el repositorio en el commit fijado y lo pasa en COLAB_COMMIT. Cada corrida
# terminada baja como ZIP a la máquina local, por si Colab se corta.

import hashlib, json, os, pathlib, shutil, subprocess, sys, time, unicodedata, urllib.request

REPO = pathlib.Path('/content/bitacora_tesis')
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path('/content/resultados-puntaje-token')
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base y las dos pruebas de humo: un cambio por vez.
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

exp = REPO / 'experiments/slm-directo'
os.chdir(exp)
sys.path.insert(0, str(exp))
import casos  # noqa: E402
from detectores import DetectorSLMSiNo, cargar_prompt  # noqa: E402


# 1. ¿«S» es el comienzo de «SÍ»? En la humo 2 el token elegido para SÍ fue siempre «S». Se deja
#    generar 3 tokens en líneas donde salió «S»; si sigue otra palabra, la lectura está mal y se
#    detiene antes de gastar la corrida.
def sin_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


diagnostico = []
for variante, hablantes, case_id, n_lineas in (('tarea-a1', 'ab', 'SC-WA-CODE-01-e01', 4),
                                                ('v4-a1', 'rol', 'SC-WA-CODE-01-e01', 4),
                                                ('v4-a2', 'rol', 'CV2-D-L-BANCO-001', 12)):
    detector = DetectorSLMSiNo(None, MODEL, cargar_prompt(variante), hablantes)
    lineas = casos.cargar_texto(case_id)[:n_lineas]
    if hablantes == 'rol':  # como correr.py: A/B → PROTEGIDA/OTRA
        lineas = casos.con_roles(case_id, lineas)
    mensajes, _ = detector.mensajes(lineas)
    cuerpo = {'model': MODEL, 'messages': mensajes, 'options': {**detector.opciones(), 'num_predict': 3},
              'stream': False, 'think': False, 'logprobs': True, 'top_logprobs': 5}
    pedido = urllib.request.Request('http://127.0.0.1:11434/api/chat', data=json.dumps(cuerpo).encode(),
                                    headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(pedido, timeout=600) as r:
        respuesta = json.load(r)
    texto = respuesta.get('message', {}).get('content', '')
    tokens = [x.get('token') for x in respuesta.get('logprobs') or []]
    palabra = sin_tildes(texto).strip().split()[0].strip('.,;:!¡?¿"\'*').upper() if texto.strip() else ''
    diagnostico.append({'prompt': variante, 'hablantes': hablantes, 'case_id': case_id, 'hasta_linea': n_lineas,
                        'num_predict': 3, 'texto': texto, 'tokens': tokens, 'logprobs': respuesta.get('logprobs')})
    print(f'Diagnóstico «S» {variante} {case_id} L{n_lineas}: {texto!r} {tokens}', flush=True)
    if tokens[:1] == ['S'] and palabra != 'SI':
        (SALIDA / 'diagnostico-s.json').write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding='utf-8')
        raise RuntimeError(f'«S» no siguió como «SÍ» sino como {texto!r}: la lectura del token está mal; detener y revisar.')
(SALIDA / 'diagnostico-s.json').write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding='utf-8')

# 2. Las seis corridas. Lo que pide #143 primero (A1 v4 con repetición y A2), por si Colab se corta.
COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--seguir-tras-aviso']
CORRIDAS = [
    # (carpeta, descripción, prompt, hablantes)
    ('v4-a1', 'A1 con v4 y roles', 'v4-a1', 'rol'),
    ('v4-a2', 'A2 con v4 y roles', 'v4-a2', 'rol'),
    ('v4-a1-rep', 'Repetición de A1 con v4 y roles', 'v4-a1', 'rol'),
    ('tarea-a1', 'A1 con tarea y A/B (#51 sigue abierto)', 'tarea-a1', 'ab'),
    ('v4-a2-rep', 'Repetición de A2 con v4 y roles', 'v4-a2', 'rol'),
    ('tarea-a1-rep', 'Repetición de A1 con tarea y A/B', 'tarea-a1', 'ab'),
]
for carpeta, descripcion, prompt, hablantes in CORRIDAS:
    destino = SALIDA / carpeta
    if (destino / 'TERMINADA.txt').exists():
        print(f'[{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
        continue
    shutil.rmtree(destino, ignore_errors=True)  # una corrida cortada se repite entera
    destino.mkdir(parents=True)
    args = [sys.executable, 'correr.py', *COMUNES, '--prompts', prompt, '--hablantes', hablantes,
            '--etiqueta', f'puntaje-token-{carpeta}', '--salida', str(destino)]
    print(f'[{carpeta}] {descripcion}\nEjecutando:', ' '.join(args), flush=True)
    inicio = time.time()
    subprocess.run(args, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    from google.colab import files
    parcial = shutil.make_archive(f'/content/parcial-puntaje-token-{carpeta}', 'zip', destino)
    print(f'[{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min; descargando {parcial}', flush=True)
    files.download(parcial)

# 3. Inventario y empaquetado. El análisis se hace después, desde los CSV (analizar.py).
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_puntaje_token.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143: P(SÍ) del primer token en todas las líneas; A1 (v4-a1, tarea-a1) y A2 (v4-a2), '
    f'cada una con repetición\nIDS=(los 150)\n', encoding='utf-8')
zip_local = shutil.make_archive('/content/resultados-puntaje-token', 'zip', SALIDA)
print('TERMINADO: las seis corridas están en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
