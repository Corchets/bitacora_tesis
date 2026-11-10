#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-HUMO-PUNTAJE-TOKEN.ipynb: ver README-PUNTAJE-TOKEN.md.
# Estado: propuesta sin discutir. Prueba de humo 2 de #143 sobre 3 casos de desarrollo;
# esta rama no contiene el test reservado.
#
# Antes de correr los 150: ¿el primer token de gemma4 E2B es un SÍ/NO limpio con A1 y A2?
# (La humo 1, con los prompts `*-sino`, no pasó: el modelo respondía «al…» cuando quería avisar.)
#   1. Guarda una respuesta cruda de /api/chat con logprobs (respuesta-cruda.json), para ver
#      el formato real de Ollama en vez de suponerlo.
#   2. Diagnóstico de la humo 1: con el prompt viejo `v4-sino`, deja generar 8 tokens en dos
#      líneas donde salía «al», para dejar escrita la palabra (diagnostico-al.json).
#   3. Corre A1 (`tarea-a1` + ab, `v4-a1` + rol) y A2 (`v4-a2` + rol) sobre 3 casos, todas las líneas.
#   4. Resume masa_si_no y los tokens leídos. Criterio, fijado antes de correr: masa ≥ 0,9 en
#      al menos el 90 % de las líneas (44 de 48) en cada variante.
# El notebook deja el repositorio en el commit fijado y lo pasa en COLAB_COMMIT.

import collections, csv, hashlib, json, math, os, pathlib, shutil, statistics, subprocess, sys, time, urllib.request

REPO = pathlib.Path('/content/bitacora_tesis')
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')
subprocess.run(['nvidia-smi'], check=True)

SALIDA = pathlib.Path('/content/humo-puntaje-token-2')
shutil.rmtree(SALIDA, ignore_errors=True)
SALIDA.mkdir()

# Misma versión de Ollama que las líneas base (2026-11-04 y 2026-11-05): un cambio por vez.
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
from detectores import DetectorSLMSiNo, armar_mensaje_usuario, cargar_prompt  # noqa: E402

CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']
CONFIGS = [('tarea-a1', 'ab'), ('v4-a1', 'rol'), ('v4-a2', 'rol')]

def pedir_chat(variante, hablantes, case_id, n_lineas, num_predict, top):
    """El mismo pedido que hace DetectorSLMSiNo, sin pasar por el parser."""
    detector = DetectorSLMSiNo(None, MODEL, cargar_prompt(variante), hablantes)
    lineas = casos.cargar_texto(case_id)[:n_lineas]
    if hablantes == 'rol':  # como correr.py: A/B → PROTEGIDA/OTRA
        lineas = casos.con_roles(case_id, lineas)
    mensajes, _ = detector.mensajes(lineas)
    cuerpo = {'model': MODEL, 'messages': mensajes, 'options': {**detector.opciones(), 'num_predict': num_predict},
              'stream': False, 'think': False, 'logprobs': True, 'top_logprobs': top}
    pedido = urllib.request.Request('http://127.0.0.1:11434/api/chat', data=json.dumps(cuerpo).encode(),
                                    headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(pedido, timeout=600) as r:
        return cuerpo, json.load(r)


# 1. Respuesta cruda con A1: SC-WA-CODE-01-e01 hasta la línea del pedido del código.
cuerpo, cruda = pedir_chat('v4-a1', 'rol', 'SC-WA-CODE-01-e01', 4, 1, 20)
(SALIDA / 'respuesta-cruda.json').write_text(
    json.dumps({'pedido': cuerpo, 'respuesta': cruda}, ensure_ascii=False, indent=2), encoding='utf-8')
print('Respuesta cruda (sin mensajes):')
print(json.dumps({k: v for k, v in cruda.items() if k != 'message'} | {'content': cruda.get('message', {}).get('content')},
                 ensure_ascii=False, indent=1)[:3000], flush=True)

# 2. Diagnóstico de la humo 1: qué palabra empezaba con «al». No se usa para elegir nada.
diagnostico = []
for case_id, n_lineas in (('SC-WA-CODE-01-e01', 3), ('CV2-D-L-BANCO-001', 12)):
    _, r = pedir_chat('v4-sino', 'rol', case_id, n_lineas, 8, 5)
    tokens = [x.get('token') for x in r.get('logprobs') or []]
    diagnostico.append({'prompt': 'v4-sino', 'hablantes': 'rol', 'case_id': case_id, 'hasta_linea': n_lineas,
                        'num_predict': 8, 'texto': r.get('message', {}).get('content'), 'tokens': tokens,
                        'logprobs': r.get('logprobs')})
    print(f'Diagnóstico {case_id} L{n_lineas}:', repr(r.get('message', {}).get('content')), tokens, flush=True)
(SALIDA / 'diagnostico-al.json').write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding='utf-8')

# 3. A1 y A2, todas las líneas (como la corrida de los 150).
for variante, hablantes in CONFIGS:
    destino = SALIDA / variante
    destino.mkdir()
    args = [sys.executable, 'correr.py', '--modelos', MODEL, '--prompts', variante, '--hablantes', hablantes,
            '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--seguir-tras-aviso',
            '--casos', ','.join(CASOS), '--etiqueta', f'humo-{variante}', '--salida', str(destino)]
    print('Ejecutando:', ' '.join(args), flush=True)
    subprocess.run(args, check=True)


# 4. Resumen de la lectura del token.
def resumir() -> str:
    salida = ['# Prueba de humo 2 de #143: lectura del token SÍ/NO con A1 y A2', '',
              f'Commit `{COMMIT}`, {version.strip()}, `{MODEL}`. Casos: {", ".join(CASOS)}.', '',
              'Criterio, fijado antes de correr: masa_si_no ≥ 0,9 en al menos el 90 % de las líneas de cada variante.', '']
    for d in diagnostico:
        salida.append(f'- Diagnóstico humo 1 (`v4-sino`, {d["case_id"]} hasta L{d["hasta_linea"]}, 8 tokens): '
                      f'{d["texto"]!r}, tokens {d["tokens"]}')
    salida.append('')
    for variante, hablantes in CONFIGS:
        (run,) = [p for p in (SALIDA / variante).iterdir() if (p / 'actualizaciones.csv').exists()]
        with (run / 'actualizaciones.csv').open(encoding='utf-8-sig', newline='') as f:
            filas = list(csv.DictReader(f))
        validas = [f for f in filas if f['valida'] == 'true']
        masas = sorted(float(f['masa_si_no']) for f in filas if f['masa_si_no'])
        bajas = [f for f in filas if not f['masa_si_no'] or float(f['masa_si_no']) < 0.9]
        elegidos = collections.Counter(f['crudo'] for f in filas)
        minimo = math.ceil(0.9 * len(filas))
        pasa = sum(m >= 0.9 for m in masas) >= minimo
        ms = [float(f['ms']) for f in validas if f['ms']]
        salida += [f'## {variante} + {hablantes}: {"PASA" if pasa else "NO PASA"}', '',
                   f'- Líneas: {len(filas)}; válidas: {len(validas)}; errores: '
                   f'{dict(collections.Counter(f["error"] for f in filas if f["error"]))}.',
                   f'- masa_si_no: mínimo {masas[0]:.4f}, mediana {statistics.median(masas):.4f}; '
                   f'≥ 0,9 en {sum(m >= 0.9 for m in masas)} de {len(filas)} líneas (mínimo {minimo}).' if masas else '- masa_si_no: sin datos.',
                   f'- Token elegido: {dict(elegidos.most_common(8))}.',
                   f'- ms por línea: mediana {statistics.median(ms):.0f}.' if ms else '- ms: sin datos.', '']
        if bajas:
            salida += ['Líneas con masa < 0,9 (las cinco alternativas más probables):', '']
            for f in bajas[:15]:
                top = json.loads(f['top_logprobs'])[:5] if f['top_logprobs'] else []
                salida.append(f'- {f["case_id"]} L{f["linea"]}: masa {f["masa_si_no"] or "-"}, top {top}')
            salida.append('')
        salida += ['p_si por línea (la `*` marca la línea de T_R de la referencia):', '', '```text']
        for case_id in CASOS:
            t_r = casos.cargar_referencia(case_id).get('t_r_linea')
            valores = [('*' if int(f['linea']) == t_r else '') + (f'{float(f["p_si"]):.2f}' if f['p_si'] else 'x')
                       for f in filas if f['case_id'] == case_id]
            salida.append(f'{case_id:36} {" ".join(valores)}')
        salida += ['```', '', 'Alternativas de la primera línea de cada caso:', '']
        for case_id in CASOS:
            f = next(f for f in filas if f['case_id'] == case_id)
            salida.append(f'- {case_id} L1: {f["top_logprobs"]}')
        salida.append('')
    return '\n'.join(salida)


texto = resumir()
(SALIDA / 'humo.md').write_text(texto + '\n', encoding='utf-8')
print(texto, flush=True)

subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/humo_puntaje_token.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(f'{COMMIT}\nprueba de humo 2 #143: A1 (tarea-a1, v4-a1) y A2 (v4-a2), 3 casos de desarrollo\n',
                                   encoding='utf-8')
zip_local = shutil.make_archive('/content/humo-puntaje-token-2', 'zip', SALIDA)
print('TERMINADO:', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
