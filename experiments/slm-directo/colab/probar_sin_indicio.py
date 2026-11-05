#!/usr/bin/env python3
# Ejecutar en Google Colab: ver README-SIN-INDICIO.md.
# Estado: propuesta sin discutir. Prueba de desarrollo sobre las 150 conversaciones;
# no ejecuta el test reservado.
#
# Corre en la misma máquina:
#   a) SLM solo + Tito → SLM con indicio + reglas (correr.py --filtro-tito --tito-real)
#   b) Tito → SLM sin indicio (--sin-indicio --sin-reglas, con el wrapper que omite DetectorSLM)
#   c) opcional (REPETIR_SLM_SOLO): una segunda corrida de SLM solo, para medir el no determinismo
# Cada condición terminada se copia a Google Drive; si Colab se corta, al volver a
# ejecutar se recuperan desde Drive y no se repiten.

import os, sys, subprocess, pathlib, json, hashlib, time, shutil, datetime, urllib.request
REPO = pathlib.Path('/content/bitacora_tesis')
RAMA = 'refs/tags/archivo/slm-sin-indicio'  # antes rama slm-sin-indicio, archivada el 2026-11-05
COMMIT = '4916eada648c2f7c394ae82ed43c90df47ab6573'
if not REPO.exists():
    subprocess.run(['git', 'clone', 'https://github.com/Corchets/bitacora_tesis.git', str(REPO)], check=True)
subprocess.run(['git', '-C', str(REPO), 'fetch', 'origin', RAMA], check=True)
subprocess.run(['git', '-C', str(REPO), 'checkout', '--detach', COMMIT], check=True)
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')
subprocess.run(['nvidia-smi'], check=True)

# Opciones que fija el notebook (variables de entorno); por defecto, las del README.
IDS = os.environ.get('COLAB_IDS', '').strip()
REPETIR_SLM_SOLO = os.environ.get('COLAB_REPETIR_SLM_SOLO', '1') == '1'
GUARDAR_EN_DRIVE = os.environ.get('COLAB_GUARDAR_EN_DRIVE', '1') == '1'

# Drive primero: si falta la autorización, que se note antes de instalar nada.
SALIDA = pathlib.Path('/content/resultados-sin-indicio')
SALIDA.mkdir(exist_ok=True)
clave_ids = '150' if not IDS else 'ids-' + hashlib.sha256(IDS.encode()).hexdigest()[:8]
DRIVE_BASE = pathlib.Path('/content/drive/MyDrive/bitacora_tesis')
DRIVE_EN_CURSO = DRIVE_BASE / f'sin-indicio-en-curso-{COMMIT[:8]}-{clave_ids}'
if GUARDAR_EN_DRIVE:
    from google.colab import drive
    drive.mount('/content/drive')
    DRIVE_EN_CURSO.mkdir(parents=True, exist_ok=True)
    print('Resultados parciales en Drive:', DRIVE_EN_CURSO)


# El instalador de Ollama necesita zstd en el entorno temporal de Colab.
subprocess.run(['apt-get', 'install', '-y', 'zstd'], check=True)
# Las versiones efectivamente instaladas se exportan.
subprocess.run([sys.executable, '-m', 'pip', 'install', 'transformers<5', 'huggingface-hub', 'torch', 'numpy'], check=True)
subprocess.run('curl -fsSL https://ollama.com/install.sh | sh', shell=True, check=True)


# Iniciar Ollama y descargar el modelo exacto; se detiene si cambia el digest.
os.environ['OLLAMA_HOST'] = '127.0.0.1:11434'
ollama_log = open('/content/ollama-colab.log', 'a')
ollama_proc = subprocess.Popen(['ollama', 'serve'], stdout=ollama_log, stderr=subprocess.STDOUT)
for _ in range(60):
    if subprocess.run(['ollama', 'list'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0:
        break
    time.sleep(2)
else: raise RuntimeError('Ollama no inició; revisar /content/ollama-colab.log')
MODEL = 'gemma4:e2b-it-q4_K_M'
subprocess.run(['ollama', 'pull', MODEL], check=True)
with urllib.request.urlopen('http://127.0.0.1:11434/api/tags') as response:
    models = json.load(response)['models']
model = next(m for m in models if m['name'] == MODEL)
expected = 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2'
print('Digest:', model['digest'])
if model['digest'].removeprefix('sha256:') != expected:
    raise RuntimeError('Digest distinto al de la corrida original; detener y revisar.')


exp = REPO / 'experiments/slm-directo'
os.chdir(exp)
# Mismo wrapper que probar_tito_e2b.py: omite el SLM directo y deja Tito → SLM.
wrapper = pathlib.Path('/content/solo_tito_colab.py')
wrapper.write_text("""import sys
sys.path.insert(0, str(__import__('pathlib').Path.cwd()))
import correr
original = correr.procesar_caso
def procesar(detector, lineas, **kwargs):
    if isinstance(detector, correr.DetectorSLM):
        return []
    return original(detector, lineas, **kwargs)
correr.procesar_caso = procesar
correr.main()
""", encoding='utf-8')
COMUNES = ['--modelos', MODEL, '--prompts', 'tarea', '--hablantes', 'ab', '--num-ctx', '4096', '--seed', '42']
if IDS: COMUNES += ['--casos', IDS]
CONDICIONES = [
    # (clave, descripción, programa, argumentos propios, ¿wrapper?)
    ('a', 'SLM solo + Tito con indicio + reglas', 'correr.py',
     ['--filtro-tito', '--tito-real', '--etiqueta', 'sin-indicio-a-solo-y-con-indicio'], False),
    ('b', 'Tito sin indicio (wrapper sin SLM directo)', str(wrapper),
     ['--filtro-tito', '--tito-real', '--sin-indicio', '--sin-reglas', '--etiqueta', 'sin-indicio-b-tito-sin-indicio'], True),
]
if REPETIR_SLM_SOLO:
    CONDICIONES.append(('c', 'Repetición de SLM solo', 'correr.py',
                        ['--sin-reglas', '--etiqueta', 'sin-indicio-c-solo-repeticion'], False))


def terminada(carpeta):
    return (carpeta / 'TERMINADA.txt').exists()


for clave, descripcion, programa, propios, con_wrapper in CONDICIONES:
    destino = SALIDA / clave
    en_drive = DRIVE_EN_CURSO / clave
    if not terminada(destino) and GUARDAR_EN_DRIVE and terminada(en_drive):
        shutil.rmtree(destino, ignore_errors=True)
        shutil.copytree(en_drive, destino)
        print(f'[{clave}] {descripcion}: recuperada desde Drive, no se repite.', flush=True)
    if terminada(destino):
        continue
    shutil.rmtree(destino, ignore_errors=True)  # una corrida cortada se repite entera
    destino.mkdir(parents=True)
    args = [sys.executable, programa, *COMUNES, *propios, '--salida', str(destino)]
    print(f'[{clave}] {descripcion}\nEjecutando:', ' '.join(args), flush=True)
    inicio = time.time()
    subprocess.run(args, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
    if con_wrapper:
        # Corregir el manifiesto para reflejar que la condición directa fue omitida.
        manifest = run / 'manifiesto.json'
        data = json.loads(manifest.read_text(encoding='utf-8'))
        data['configs'] = [c for c in data['configs'] if c['detector'] != 'slm']
        data['nota_wrapper'] = 'Colab: procesar_caso omitió el SLM directo; solo se ejecutó Tito→SLM sin indicio.'
        manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    if GUARDAR_EN_DRIVE:
        shutil.rmtree(en_drive, ignore_errors=True)
        shutil.copytree(destino, en_drive)
        print(f'[{clave}] guardada en Drive: {en_drive}', flush=True)


# Comparación caso por caso, inventario de dependencias y empaquetado.
subprocess.run([sys.executable, 'comparar_sin_indicio.py', str(SALIDA), '--salida', str(SALIDA / 'comparacion.md')], check=True)
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
subprocess.run(['ollama', '--version'], stdout=(SALIDA / 'ollama-version.txt').open('w'), check=True)
(SALIDA / 'script-sha256.txt').write_text(hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(f'{RAMA} {COMMIT}\nIDS={IDS or "(los 150)"}\nREPETIR_SLM_SOLO={REPETIR_SLM_SOLO}\n', encoding='utf-8')
zip_local = shutil.make_archive('/content/resultados-sin-indicio', 'zip', SALIDA)
if GUARDAR_EN_DRIVE:
    fecha = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    final = DRIVE_BASE / f'resultados-sin-indicio-{fecha}.zip'
    shutil.copy(zip_local, final)
    print('ZIP guardado en Drive:', final)
from google.colab import files
files.download(zip_local)
