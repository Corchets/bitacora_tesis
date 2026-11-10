#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-SENSIBILIDAD.ipynb: ver README-PUNTAJE-TOKEN.md (sección 8).
# Estado: propuesta sin discutir. #143, prueba de sensibilidad sobre los 244 casos de desarrollo; esta rama no contiene
# el test reservado ni las legítimas de test.
#
# Tres variantes de C, con un solo cambio cada una, contra la configuración congelada (c-json-corte-riesgo): c-ancla
# (ancla la punta alta del riesgo), c-premisa (un párrafo sobre el número no agendado) y c-sin-freno (sin el párrafo de lo
# que una llamada legítima también puede pedir). Todas cortan tras el riesgo (num_predict 14), avisan con «riesgo ≥ 0,3»,
# piden el motivo de C en el primer aviso y consultan solo en las líneas de OTRA. La regla está escrita antes de correr
# en corridas/2026-11-10_sensibilidad-c/README.md. Mismo modelo, digest, Ollama, num_ctx, seed y temperatura que antes.
#
# 1. Humo de formato en los 3 casos de siempre (48 líneas), en todas las líneas, con las cuatro. Criterio, fijado antes
#    de correr: cada una lee el riesgo, con su coma, en las 48 líneas. La que no pasa no corre; si no pasa la base, no
#    corre nada. No se ajusta nada en esta sesión (ADR 0005).
# 2. Las cuatro sobre los 244 y después sus repeticiones sobre alcance-140, con --solo-otra y --seguir-tras-aviso.
# Cada etapa terminada baja como ZIP. El análisis va después, con analizar.py.
# COLAB_REPO y COLAB_SALIDA solo existen para la prueba en seco; en Colab quedan los valores por defecto.

import csv, hashlib, json, os, pathlib, shutil, subprocess, sys, time, urllib.request

REPO = pathlib.Path(os.environ.get('COLAB_REPO', '/content/bitacora_tesis'))
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path(os.environ.get('COLAB_SALIDA', '/content/resultados-sensibilidad'))
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base, las etapas 1 a 3 y la humo: un cambio por vez.
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

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--hablantes', 'rol']
CORRIDA = ['--solo-otra', '--seguir-tras-aviso']  # todas las líneas de OTRA, para mirar la curva
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48
BASE = 'c-json-corte-riesgo'
VARIANTES = ['c-ancla-corte-riesgo', 'c-premisa-corte-riesgo', 'c-sin-freno-corte-riesgo']
TODAS = [BASE, *VARIANTES]


def descargar(carpeta, nombre):
    from google.colab import files
    archivo = shutil.make_archive(str(SALIDA.parent / nombre), 'zip', carpeta)
    print(f'Descargando {archivo}', flush=True)
    files.download(archivo)


def correr(destino, etiqueta, *args):
    shutil.rmtree(destino, ignore_errors=True)  # una corrida cortada se repite entera
    destino.mkdir(parents=True)
    orden = [sys.executable, 'correr.py', *args, *COMUNES, '--etiqueta', etiqueta, '--salida', str(destino)]
    print('Ejecutando:', ' '.join(orden), flush=True)
    subprocess.run(orden, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
    return run


# 1. Humo de formato.
humo_dir = SALIDA / 'humo'
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', {p: 'PASA' if d['pasa'] else 'NO PASA' for p, d in humo.items()}, flush=True)
else:
    run = correr(humo_dir / 'corrida', 'sensibilidad-humo', '--casos', ','.join(HUMO_CASOS), '--prompts', ','.join(TODAS),
                 '--seguir-tras-aviso')
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    por = {p: {(r['case_id'], int(r['linea'])): r for r in filas if r['prompt'] == p} for p in TODAS}
    humo, salida = {}, ['# Humo de la prueba de sensibilidad de #143', '',
                        f'Commit `{COMMIT}`. Casos: {", ".join(HUMO_CASOS)} ({LINEAS_HUMO} líneas), en todas las líneas. '
                        'Todas cortan con `num_predict` 14.', '',
                        f'Criterio, fijado antes de correr: cada una lee el riesgo, con su coma, en las {LINEAS_HUMO} '
                        'líneas. La que no pasa no corre; si no pasa la base, no corre nada.', '',
                        '| prompt | riesgo leído | errores | mismo riesgo que la base (dato) | riesgo ≥ 0,3 (dato) | '
                        'riesgo ≥ 0,6 (dato) | resultado |', '|---|---|---|---|---|---|---|']
    for prompt in TODAS:
        propias = por[prompt]
        leidas = sum(r['valida'] == 'true' for r in propias.values())
        riesgos = [float(r['riesgo']) for r in propias.values() if r['riesgo'] != '']
        iguales = sum(r['riesgo'] != '' and r['riesgo'] == por[BASE].get(k, {}).get('riesgo') for k, r in propias.items())
        humo[prompt] = {'lineas': len(propias), 'leidas': leidas, 'igual_a_la_base': iguales,
                        'altos_03': sum(x >= 0.3 - 1e-9 for x in riesgos), 'altos_06': sum(x >= 0.6 - 1e-9 for x in riesgos),
                        'errores': sorted({r['error'] for r in propias.values() if r['valida'] != 'true'})}
        humo[prompt]['pasa'] = len(propias) == leidas == LINEAS_HUMO
        h = humo[prompt]
        salida.append(f"| `{prompt}` | {leidas}/{len(propias)} | {', '.join(h['errores']) or '—'} | {iguales}/{len(propias)} | "
                      f"{h['altos_03']} | {h['altos_06']} | {'PASA' if h['pasa'] else 'NO PASA'} |")
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.md').write_text('\n'.join(salida) + '\n', encoding='utf-8')
    print('\n'.join(salida), flush=True)
    descargar(humo_dir, 'parcial-sensibilidad-humo')

if not humo[BASE]['pasa']:
    raise RuntimeError('La base no pasó la humo de formato: no se corre nada. Ver humo/humo.md.')
pasan = [p for p in TODAS if humo[p]['pasa']]

# 2. Las cuatro sobre los 244 y después las repeticiones sobre alcance-140, así un corte de Colab deja la comparación.
CARPETAS = {BASE: 'base', **{p: p.removesuffix('-corte-riesgo') for p in VARIANTES}}  # base, c-ancla, c-premisa, c-sin-freno
CORRIDAS = [(CARPETAS[p], p, None) for p in TODAS] + [(CARPETAS[p] + '-rep', p, 'alcance-140') for p in TODAS]
for carpeta, prompt, lista in CORRIDAS:
    destino = SALIDA / carpeta
    if prompt not in pasan:
        print(f'[{carpeta}] no corre: {prompt} no pasó la humo.', flush=True)
        continue
    if (destino / 'TERMINADA.txt').exists():
        print(f'[{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
        continue
    descripcion = f'{prompt}, solo OTRA, todas las líneas, sobre {lista or "los 244"}'
    print(f'[{carpeta}] {descripcion}', flush=True)
    inicio = time.time()
    run = correr(destino, f'sensibilidad-{carpeta}', '--prompts', prompt, *CORRIDA, *(['--lista', lista] if lista else []))
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    print(f'[{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
    descargar(destino, f'parcial-sensibilidad-{carpeta}')

# 3. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_sensibilidad.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143, prueba de sensibilidad: humo de formato, {", ".join(TODAS)} sobre los 244 y sus repeticiones '
    f'sobre alcance-140, con --solo-otra y --seguir-tras-aviso\nIDS=(los 244)\n', encoding='utf-8')
zip_local = shutil.make_archive(str(SALIDA.parent / 'resultados-sensibilidad'), 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
