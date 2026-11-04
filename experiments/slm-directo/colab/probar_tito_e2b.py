#!/usr/bin/env python3
# Ejecutar en Google Colab: ver README.md.

import os, sys, subprocess, pathlib, json, hashlib, time, shutil
REPO = pathlib.Path('/content/bitacora_tesis')
COMMIT = '833a3fb5b2330ea3755b60880006a7d49b1e2e1b'
if not REPO.exists():
    subprocess.run(['git', 'clone', 'https://github.com/Corchets/bitacora_tesis.git', str(REPO)], check=True)
subprocess.run(['git', '-C', str(REPO), 'checkout', '--detach', COMMIT], check=True)
print('Commit:', subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip())
subprocess.run(['nvidia-smi'], check=True)


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
import urllib.request
with urllib.request.urlopen('http://127.0.0.1:11434/api/tags') as response:
    models = json.load(response)['models']
model = next(m for m in models if m['name'] == MODEL)
expected = 'b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2'
print('Digest:', model['digest'])
if model['digest'].removeprefix('sha256:') != expected:
    raise RuntimeError('Digest distinto al de la corrida original; detener y revisar.')


# IDs de desarrollo separados por coma. Vacío: los 150.
IDS = os.environ.get('COLAB_IDS', '')
exp = REPO / 'experiments/slm-directo'
os.chdir(exp)
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
args = [sys.executable, str(wrapper), '--modelos', MODEL, '--prompts', 'tarea', '--hablantes', 'ab', '--filtro-tito', '--tito-real', '--num-ctx', '4096', '--seed', '42', '--etiqueta', 'colab-e2b-tito-viejo', '--salida', '/content/resultados-colab']
if IDS.strip(): args += ['--casos', IDS.strip()]
pathlib.Path('/content/resultados-colab').mkdir(exist_ok=True)
print('Ejecutando:', ' '.join(args), flush=True)
subprocess.run(args, check=True)


# Corregir el manifiesto para reflejar que la condición directa fue omitida;
# generar resumen, inventariar dependencias y empaquetar resultados para descargar.
base = pathlib.Path('/content/resultados-colab')
for run in sorted(base.iterdir()):
    manifest = run / 'manifiesto.json'
    if not manifest.exists(): continue
    data = json.loads(manifest.read_text(encoding='utf-8'))
    data['configs'] = [c for c in data['configs'] if c['detector'] != 'slm']
    data['nota_wrapper'] = 'Colab: procesar_caso omitió el SLM directo; Tito→SLM y reglas se ejecutaron.'
    manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(base / 'pip-freeze.txt').open('w'), check=True)
subprocess.run(['ollama', '--version'], stdout=(base / 'ollama-version.txt').open('w'), check=True)
(base / 'script-sha256.txt').write_text(hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest() + '\n', encoding='utf-8')
shutil.make_archive('/content/resultados-colab', 'zip', base)
from google.colab import files
files.download('/content/resultados-colab.zip')
