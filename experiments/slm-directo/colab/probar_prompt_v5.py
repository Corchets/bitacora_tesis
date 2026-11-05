#!/usr/bin/env python3
# Ejecutar en Google Colab: ver README-PROMPT-V5.md.
# Estado: propuesta sin discutir. Prueba de desarrollo sobre las 150 conversaciones;
# esta rama no contiene el test reservado.
#
# Corre en la misma máquina cuatro condiciones de Tito viejo → SLM sin indicio
# (--sin-indicio, con el wrapper que omite DetectorSLM), todas siguiendo después del aviso, y
# los controles de maniobras aparte de los 150. Ver CONDICIONES y PROMPTS_CONTROLES.
# Cada corrida terminada baja como ZIP a la máquina local. Drive es opcional
# (COLAB_GUARDAR_EN_DRIVE=1): da acceso de escritura a todo Drive, así que no es el predeterminado.

import os, sys, subprocess, pathlib, json, hashlib, time, shutil, datetime, urllib.request
REPO = pathlib.Path('/content/bitacora_tesis')
RAMA = 'prompt-v5-colab'
COMMIT = 'PENDIENTE'
if not REPO.exists():
    subprocess.run(['git', 'clone', 'https://github.com/Corchets/bitacora_tesis.git', str(REPO)], check=True)
subprocess.run(['git', '-C', str(REPO), 'fetch', 'origin', RAMA], check=True)
subprocess.run(['git', '-C', str(REPO), 'checkout', '--detach', COMMIT], check=True)
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')
subprocess.run(['nvidia-smi'], check=True)

GUARDAR_EN_DRIVE = os.environ.get('COLAB_GUARDAR_EN_DRIVE', '0') == '1'

# Drive primero: si falta la autorización, que se note antes de instalar nada.
SALIDA = pathlib.Path('/content/resultados-prompt-v5')
SALIDA.mkdir(exist_ok=True)
DRIVE_BASE = pathlib.Path('/content/drive/MyDrive/bitacora_tesis')
DRIVE_EN_CURSO = DRIVE_BASE / f'prompt-v5-en-curso-{COMMIT[:8]}-150'
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
COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--filtro-tito', '--tito-real', '--sin-indicio']
CONDICIONES = [
    # (clave, descripción, prompt, hablantes, opciones). Lo más valioso primero, por si Colab se corta.
    # Todas siguen tras el aviso: dan el primer aviso y además permiten simular persistencia.
    ('a', 'v4 con la regla de maniobras', 'v5-maniobras', 'rol', ['--seguir-tras-aviso']),
    ('b', 'los tres cambios juntos', 'v5', 'rol', ['--seguir-tras-aviso']),
    ('c', 'v4 con pedidos indirectos ampliados', 'v5-indirectos', 'rol', ['--seguir-tras-aviso']),
    ('d', 'v4 sin la excepción de datos comunes', 'v5-sin-excepcion', 'rol', ['--seguir-tras-aviso']),
]
# Controles de maniobras: SLM solo y Tito → SLM, para ver la regla también donde Tito no activa.
PROMPTS_CONTROLES = ['v4', 'v5-maniobras', 'v5']


def terminada(carpeta):
    return (carpeta / 'TERMINADA.txt').exists()


for clave, descripcion, prompt, hablantes, opciones in CONDICIONES:
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
    args = [sys.executable, str(wrapper), *COMUNES, '--prompts', prompt, '--hablantes', hablantes, *opciones,
            '--etiqueta', f'prompt-v5-{clave}-{prompt}-{hablantes}', '--salida', str(destino)]
    print(f'[{clave}] {descripcion}\nEjecutando:', ' '.join(args), flush=True)
    inicio = time.time()
    subprocess.run(args, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
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
    else:
        # Sin Drive: cada corrida terminada baja a la máquina local por si Colab se corta.
        from google.colab import files
        parcial = shutil.make_archive(f'/content/parcial-prompt-v5-{clave}', 'zip', destino)
        print(f'[{clave}] terminada; descargando {parcial}', flush=True)
        files.download(parcial)


# Controles: fuera de los 150, sin wrapper para registrar también el SLM solo.
controles = SALIDA / 'controles'
if not terminada(controles):
    shutil.rmtree(controles, ignore_errors=True)
    controles.mkdir(parents=True)
    inicio = time.time()
    subprocess.run([sys.executable, 'correr_controles.py', *COMUNES, '--prompts', ','.join(PROMPTS_CONTROLES), '--hablantes', 'rol',
                    '--seguir-tras-aviso', '--etiqueta', 'prompt-v5-controles', '--salida', str(controles)], check=True)
    (controles / 'TERMINADA.txt').write_text(
        f'controles de maniobras\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')

# Inventario de dependencias y empaquetado. La comparación se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
subprocess.run(['ollama', '--version'], stdout=(SALIDA / 'ollama-version.txt').open('w'), check=True)
(SALIDA / 'script-sha256.txt').write_text(hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(f'{RAMA} {COMMIT}\nv5-maniobras, v5, v5-indirectos y v5-sin-excepcion tras el aviso, y controles de maniobras\nIDS=(los 150 y los 18 controles)\n', encoding='utf-8')
zip_local = shutil.make_archive('/content/resultados-prompt-v5', 'zip', SALIDA)
if GUARDAR_EN_DRIVE:
    fecha = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
    final = DRIVE_BASE / f'resultados-prompt-v5-{fecha}.zip'
    shutil.copy(zip_local, final)
    print('ZIP guardado en Drive:', final)
print('TERMINADO: las cuatro condiciones y los controles están en', zip_local, flush=True)
from google.colab import files
files.download(zip_local)
