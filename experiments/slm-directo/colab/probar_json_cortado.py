#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-JSON-CORTADO.ipynb: ver README-PUNTAJE-TOKEN.md (sección 4).
# Estado: propuesta sin discutir. #143, después de la etapa 1 de la segunda vuelta, sobre las 150 conversaciones de
# desarrollo; esta rama no contiene el test reservado.
#
# Decisión de Mateo (2026-11-07): el detector sigue con el JSON de v4 y «riesgo ≥ 0,4 o alerta». Para bajar la
# latencia, la primera consulta se corta con num_predict después del valor de `alerta_sugerida` (v4-corte) y el
# motivo y la evidencia se piden en una segunda consulta, solo en la línea del aviso. Este script mide eso en una
# sesión, con el mismo modelo, digest, Ollama, num_ctx, seed y temperatura que las líneas base:
# 1. Humo de formato en los 3 casos de las humos anteriores (48 líneas). Criterio, fijado antes de correr:
#    a) con el JSON completo de v4 y logprobs, el valor de `alerta_sugerida` termina a más tardar en el token
#       MAXIMO_TOKENS_CORTE en las 48 líneas;
#    b) v4-corte lee riesgo y alerta en las 48 líneas.
#    Si no pasa, el script se detiene antes de los 150: se corrige MAXIMO_TOKENS_CORTE en detectores.py según
#    `tokens_hasta_alerta`, se hace un tag nuevo y se repite. No se ajusta nada en esta sesión.
# 2. v4-corte sobre los 150 en todas las líneas (--seguir-tras-aviso). La segunda consulta corre en la primera
#    línea de cada llamada en que dispara «riesgo ≥ 0,4 o alerta».
# 3. El JSON completo de v4 en las mismas condiciones, para comparar línea a línea riesgo, alerta y ms.
# Cada etapa terminada baja como ZIP. El análisis va después, con corridas/2026-11-07_json-cortado/analizar.py.

import hashlib, json, os, pathlib, shutil, statistics, subprocess, sys, time, urllib.request

REPO = pathlib.Path('/content/bitacora_tesis')
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path('/content/resultados-json-cortado')
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base y la etapa 1: un cambio por vez.
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
from detectores import (ESQUEMA_SALIDA, MAXIMO_TOKENS_CORTE, DetectorSLM, cargar_prompt,  # noqa: E402
                        leer_json_cortado)

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--seguir-tras-aviso',
           '--hablantes', 'rol']
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48


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
    print('Humo ya hecha en esta sesión:', 'PASA' if humo['pasa'] else 'NO PASA', flush=True)
else:
    # a) Tokens hasta la alerta con el JSON completo de v4: el mismo pedido que correr.py (think false, como en las
    #    líneas base), con logprobs solo para ver los tokens.
    detector = DetectorSLM(None, MODEL, cargar_prompt('v4'), 'rol')
    diagnostico = []
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
            diagnostico.append({'case_id': case_id, 'linea': n, 'texto': respuesta.get('message', {}).get('content', ''),
                                'tokens_hasta_alerta': tokens_hasta_alerta(pasos), 'tokens': [p.get('token') for p in pasos]})
    necesarios = [d['tokens_hasta_alerta'] for d in diagnostico]
    alcanzan = sum(t is not None and t <= MAXIMO_TOKENS_CORTE for t in necesarios)
    # b) v4-corte en las mismas 48 líneas, por correr.py (con la segunda consulta en las líneas de aviso).
    run = correr(humo_dir / 'corrida', 'json-cortado-humo', 'correr.py', '--casos', ','.join(HUMO_CASOS),
                 '--prompts', 'v4-corte')
    import csv
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    leidas = sum(r['valida'] == 'true' for r in filas)
    validos = [t for t in necesarios if t is not None]
    humo = {
        'num_predict': MAXIMO_TOKENS_CORTE, 'lineas': len(diagnostico), 'alcanzan': alcanzan,
        'tokens_hasta_alerta': {'min': min(validos, default=None), 'mediana': statistics.median(validos) if validos else None,
                                'max': max(validos, default=None), 'sin_alerta': necesarios.count(None)},
        'cortado_lineas': len(filas), 'cortado_leidas': leidas,
        'cortado_errores': sorted({r['error'] for r in filas if r['valida'] != 'true'}),
        'segunda_consulta': [{'case_id': r['case_id'], 'linea': r['linea'], 'ms_etapa2': r['ms_etapa2'], 'error': r['error'],
                              'motivo': r['motivo'], 'evidencia': r['evidencia']} for r in filas if r['ms_etapa2']],
    }
    humo['pasa'] = len(diagnostico) == len(filas) == LINEAS_HUMO and alcanzan == leidas == LINEAS_HUMO
    humo_dir.mkdir(exist_ok=True)
    (humo_dir / 'tokens-hasta-alerta.json').write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    t = humo['tokens_hasta_alerta']
    salida = ['# Humo del JSON de v4 cortado después de `alerta_sugerida`', '',
              f'Commit `{COMMIT}`. Casos: {", ".join(HUMO_CASOS)} ({LINEAS_HUMO} líneas). num_predict: {MAXIMO_TOKENS_CORTE}.', '',
              f'Criterio, fijado antes de correr: con el JSON completo, la alerta termina a más tardar en el token '
              f'{MAXIMO_TOKENS_CORTE} en las {LINEAS_HUMO} líneas, y v4-corte lee riesgo y alerta en las {LINEAS_HUMO}. '
              f'Si no pasa, no corre en los 150.', '',
              '| tokens hasta la alerta (mín / mediana / máx) | líneas que alcanzan | v4-corte, líneas leídas | resultado |',
              '|---|---|---|---|',
              f'| {t["min"]} / {t["mediana"]} / {t["max"]} (sin alerta: {t["sin_alerta"]}) | {alcanzan}/{len(diagnostico)} | '
              f'{leidas}/{len(filas)} | {"PASA" if humo["pasa"] else "NO PASA"} |', '',
              f'Segunda consulta en {len(humo["segunda_consulta"])} líneas de aviso:', '']
    salida += [f'- {s["case_id"]} L{s["linea"]}: {s["ms_etapa2"]} ms {s["error"]} — {s["motivo"]!r} / {s["evidencia"]!r}'
               for s in humo['segunda_consulta']]
    salida += ['', 'Líneas que no alcanzan:', '']
    salida += [f'- {d["case_id"]} L{d["linea"]}: {d["tokens_hasta_alerta"]} tokens; {d["tokens"][:30]}' for d in diagnostico
               if d['tokens_hasta_alerta'] is None or d['tokens_hasta_alerta'] > MAXIMO_TOKENS_CORTE]
    (humo_dir / 'humo.md').write_text('\n'.join(salida) + '\n', encoding='utf-8')
    print('\n'.join(salida), flush=True)
    descargar(humo_dir, 'parcial-json-cortado-humo')

if not humo['pasa']:
    raise RuntimeError('La humo no pasó: no se corren los 150. Ver humo/humo.md y corregir MAXIMO_TOKENS_CORTE con un tag nuevo.')

# 2 y 3. Los 150: primero el cortado (lo nuevo), después el JSON completo en la misma sesión.
CORRIDAS = [
    ('v4-corte', 'JSON de v4 cortado después de alerta_sugerida, con la segunda consulta en la línea de aviso', 'v4-corte'),
    ('v4', 'JSON completo de v4 en la misma sesión, para comparar línea a línea', 'v4'),
]
for carpeta, descripcion, prompt in CORRIDAS:
    destino = SALIDA / carpeta
    if (destino / 'TERMINADA.txt').exists():
        print(f'[{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
        continue
    print(f'[{carpeta}] {descripcion}', flush=True)
    inicio = time.time()
    run = correr(destino, f'json-cortado-{carpeta}', 'correr.py', '--prompts', prompt)
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    print(f'[{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
    descargar(destino, f'parcial-json-cortado-{carpeta}')

# 4. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_json_cortado.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143: JSON de v4 cortado después de alerta_sugerida (v4-corte, num_predict {MAXIMO_TOKENS_CORTE}) con '
    f'la segunda consulta de motivo y evidencia, y el JSON completo de v4 en la misma sesión\nIDS=(los 150)\n',
    encoding='utf-8')
zip_local = shutil.make_archive('/content/resultados-json-cortado', 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
