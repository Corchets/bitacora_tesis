#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-CONFIG-CONGELADA.ipynb: ver README-PUNTAJE-TOKEN.md (sección 7).
# Estado: propuesta sin discutir. #143, configuración congelada, prueba de humo sobre los 244 casos de desarrollo; esta
# rama no contiene el test reservado ni las legítimas de test.
#
# La configuración (Mateo, 2026-11-09): C de la etapa 2 (`c-json`) cortado justo después del riesgo
# (`c-json-corte-riesgo`, num_predict 14), «riesgo ≥ 0,3», el motivo de C (prompts/motivo_c_corte.txt) en una segunda
# consulta solo en el primer aviso, y consulta solo en las líneas de OTRA (correr.py --solo-otra, ADR 0007). Hasta acá el
# corte tras el riesgo solo se leyó de c-json-corte, «solo OTRA» se simuló y el motivo de C nunca se pidió en el primer
# aviso. La regla de lectura está escrita antes de correr en corridas/2026-11-10_config-congelada-humo/ (README.md y
# analizar.py). Mismo modelo, digest, Ollama, num_ctx, seed y temperatura que las etapas 2 y 3.
#
# 1. Humo de formato en los 3 casos de las humos anteriores (48 líneas), en todas las líneas (--seguir-tras-aviso, sin
#    --solo-otra), con c-json-corte y c-json-corte-riesgo en una corrida. Criterio, fijado antes de correr:
#    c-json-corte-riesgo lee el riesgo, con su coma, en las 48 líneas. Datos, sin criterio: el riesgo contra el de
#    c-json-corte, los tokens, los riesgos con dos decimales y los motivos. Si no pasa, no corre nada más (ADR 0005).
# 2. La configuración congelada sobre los 244, con --solo-otra y en modo operativo (la llamada termina en el aviso).
# Cada etapa terminada baja como ZIP. El análisis va después, con analizar.py.
# COLAB_REPO y COLAB_SALIDA solo existen para la prueba en seco; en Colab quedan los valores por defecto.

import csv, hashlib, json, os, pathlib, re, shutil, statistics, subprocess, sys, time, urllib.request

REPO = pathlib.Path(os.environ.get('COLAB_REPO', '/content/bitacora_tesis'))
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path(os.environ.get('COLAB_SALIDA', '/content/resultados-config-congelada'))
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base y las etapas 1 a 3: un cambio por vez.
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
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48
CONGELADA = 'c-json-corte-riesgo'
RIESGO = re.compile(r'"riesgo"\s*:\s*(-?[0-9]+(?:\.[0-9]+)?)\s*,')


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


def resumen_tokens(valores):
    return f'{min(valores)} / {statistics.median(valores):g} / {max(valores)}' if valores else '—'


# 1. Humo de formato.
humo_dir = SALIDA / 'humo'
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', 'PASA' if humo['pasa'] else 'NO PASA', flush=True)
else:
    run = correr(humo_dir / 'corrida', 'config-congelada-humo', '--casos', ','.join(HUMO_CASOS),
                 '--prompts', f'c-json-corte,{CONGELADA}', '--seguir-tras-aviso')
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    por = {p: {(r['case_id'], int(r['linea'])): r for r in filas if r['prompt'] == p} for p in ['c-json-corte', CONGELADA]}
    propias = por[CONGELADA]
    leidas = sum(r['valida'] == 'true' for r in propias.values())
    iguales = sum(r['riesgo'] != '' and k in por['c-json-corte'] and r['riesgo'] == por['c-json-corte'][k]['riesgo']
                  for k, r in propias.items())
    escritos = [RIESGO.search(r['crudo']) for r in propias.values()]
    humo = {
        'lineas': len(propias), 'leidas': leidas, 'igual_a_c_json_corte': iguales,
        'tokens_salida': resumen_tokens([int(r['tokens_salida']) for r in propias.values() if r['tokens_salida']]),
        'dos_decimales': sum(bool(m) and len(m.group(1).partition('.')[2]) >= 2 for m in escritos),
        'errores': sorted({r['error'] for r in propias.values() if r['valida'] != 'true'}),
        'segunda_consulta': [{'case_id': k[0], 'linea': k[1], 'riesgo': r['riesgo'], 'ms_etapa2': r['ms_etapa2'],
                              'error': r['error'], 'motivo': r['motivo'], 'evidencia': r['evidencia']}
                             for k, r in sorted(propias.items()) if r['ms_etapa2']],
    }
    humo['pasa'] = len(propias) == leidas == LINEAS_HUMO
    salida = ['# Humo de la configuración congelada de #143', '',
              f'Commit `{COMMIT}`. Casos: {", ".join(HUMO_CASOS)} ({LINEAS_HUMO} líneas), en todas las líneas. '
              f'`{CONGELADA}` corta con `num_predict` 14.', '',
              f'Criterio, fijado antes de correr: `{CONGELADA}` lee el riesgo, con su coma, en las {LINEAS_HUMO} líneas. Si '
              'no pasa, no corre nada más.', '',
              '| riesgo leído | errores | tokens generados (mín / mediana / máx) | mismo riesgo que c-json-corte (dato) | '
              'riesgos con dos decimales (dato) | resultado |', '|---|---|---|---|---|---|',
              f"| {leidas}/{len(propias)} | {', '.join(humo['errores']) or '—'} | {humo['tokens_salida']} | "
              f"{iguales}/{len(propias)} | {humo['dos_decimales']} | {'PASA' if humo['pasa'] else 'NO PASA'} |", '',
              f'Segunda consulta (motivo_c_corte.txt) en {len(humo["segunda_consulta"])} primeros avisos:', '']
    salida += [f'- {s["case_id"]} L{s["linea"]} (riesgo {s["riesgo"]}): {s["ms_etapa2"]} ms {s["error"]} — '
               f'{s["motivo"]!r} / {s["evidencia"]!r}' for s in humo['segunda_consulta']]
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.md').write_text('\n'.join(salida) + '\n', encoding='utf-8')
    print('\n'.join(salida), flush=True)
    descargar(humo_dir, 'parcial-config-congelada-humo')

if not humo['pasa']:
    raise RuntimeError('La humo de formato no pasó: no se corre nada más. Ver humo/humo.md.')

# 2. La configuración congelada sobre los 244, solo OTRA, en modo operativo.
destino = SALIDA / 'desarrollo'
if (destino / 'TERMINADA.txt').exists():
    print('[desarrollo] ya terminada en esta sesión; no se repite.', flush=True)
else:
    descripcion = f'Configuración congelada ({CONGELADA}, «riesgo ≥ 0,3», motivo en el primer aviso), solo OTRA, sobre los 244'
    print(f'[desarrollo] {descripcion}', flush=True)
    inicio = time.time()
    run = correr(destino, 'config-congelada-desarrollo', '--prompts', CONGELADA, '--solo-otra')
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    print(f'[desarrollo] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
    descargar(destino, 'parcial-config-congelada-desarrollo')

# 3. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_config_congelada.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143, configuración congelada: humo de formato y {CONGELADA} con --solo-otra sobre los 244\n'
    f'IDS=(los 244)\n', encoding='utf-8')
zip_local = shutil.make_archive(str(SALIDA.parent / 'resultados-config-congelada'), 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
