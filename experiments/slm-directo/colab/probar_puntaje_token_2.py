#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-PUNTAJE-TOKEN-2.ipynb: ver README-PUNTAJE-TOKEN.md (sección 3).
# Estado: propuesta sin discutir. Segunda vuelta de #143 sobre las 150 conversaciones de desarrollo;
# esta rama no contiene el test reservado.
#
# Alcance (decidido por el equipo el 2026-11-06): el detector corre solo en llamadas entrantes de números
# no agendados. En corpus_v2 casi todas las legítimas las inicia la persona, así que la vuelta va en dos etapas:
#   Etapa 1 (este script): v4-lectura (v4-L), el JSON de v4 tal cual cortado después del primer decimal del
#     riesgo, leyendo la distribución de ese dígito, con su repetición, sobre los 150. Prueba solo la forma de
#     leer, con el mismo prompt y los mismos casos que la línea base v4 JSON. La humo también controla el
#     formato de c-sino y c-digito (prompt C con el alcance), para no descubrir un problema en la etapa 2.
#   Etapa 2 (otro script, cuando estén las legítimas entrantes que genera Evaristo): el prompt C con el alcance
#     (c-json, c-sino, c-digito), v4-premisa y v4 / v4-L sobre las legítimas nuevas; la decisión dentro del
#     alcance sale de las 46 estafas de corpus_v2 y esas legítimas.
# Mismo modelo, digest, Ollama, num_ctx, seed y temperatura que las líneas base.
#
# 1. Humo de formato en 3 casos (48 líneas) para los tres prompts de token. Criterio, fijado antes de
#    correr: en cada variante, masa ≥ 0,9 en al menos 44 de 48 líneas y, dejando generar 3 tokens, la
#    respuesta empieza con SÍ/NO o con un solo dígito (no «10») en al menos 44 de 48; en v4-L, que se
#    encuentre el decimal del riesgo (línea válida) en al menos 44 de 48. La variante que no pasa no
#    corre en los 150 y queda anotada; no se ajusta nada en esta sesión.
# 2. v4-L sobre los 150 en todas las líneas (--seguir-tras-aviso) y su repetición.
# 3. Los controles de ventas y préstamos (casos/controles-ventas.json), solo para mirar, con v4-L y v4 JSON.
# Cada etapa terminada baja como ZIP a la máquina local.

import hashlib, json, os, pathlib, re, shutil, statistics, subprocess, sys, time, unicodedata, urllib.request

REPO = pathlib.Path('/content/bitacora_tesis')
COMMIT = os.environ['COLAB_COMMIT']
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path('/content/resultados-puntaje-token-2')
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

# Misma versión de Ollama que las líneas base y la primera vuelta: un cambio por vez.
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
from detectores import (DetectorSLMDigito, DetectorSLMSiNo, PROMPTS_DIGITO, PROMPTS_LECTURA,  # noqa: E402
                        cargar_pregunta, cargar_prompt)

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--seguir-tras-aviso',
           '--hablantes', 'rol']
TOKEN = ['v4-lectura', 'c-sino', 'c-digito']
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de la humo 2
MINIMO = 44  # de 48 líneas: el 90 %


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


def sin_tildes(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


def respuesta_limpia(variante, texto):
    """¿Los primeros tokens son la respuesta pedida? SÍ/NO, o un solo dígito que no sigue con otro."""
    t = sin_tildes(texto).strip().lstrip('*_"\'«').strip()
    if variante in PROMPTS_DIGITO:
        return re.match(r'[0-9](?![0-9])', t) is not None
    palabra = re.split(r'[\s.,;:!?*]', t, maxsplit=1)[0].upper() if t else ''
    return palabra in ('SI', 'NO')


# 1. Humo de formato.
humo_dir = SALIDA / 'humo'
humo = {}
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', {v: d['pasa'] for v, d in humo.items()}, flush=True)
else:
    run = correr(humo_dir / 'corrida', 'puntaje-token-2-humo', 'correr.py', '--casos', ','.join(HUMO_CASOS),
                 '--prompts', ','.join(TOKEN))
    import csv
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    diagnostico = []
    for variante in TOKEN:
        columna = 'masa_si_no' if variante not in PROMPTS_DIGITO | PROMPTS_LECTURA else 'masa_digitos'
        propias = [r for r in filas if r['prompt'] == variante]
        masas = [float(r[columna]) if r[columna] else 0.0 for r in propias]
        altas = sum(m >= 0.9 for m in masas)
        if variante in PROMPTS_LECTURA:  # el JSON ya trae el texto: alcanza con que se encuentre el decimal
            limpias = sum(r['valida'] == 'true' for r in propias)
            humo[variante] = {'lineas': len(propias), 'masa_ge_09': altas, 'masa_min': min(masas), 'masa_mediana': statistics.median(masas),
                              'respuesta_limpia': limpias, 'pasa': len(propias) == 48 and altas >= MINIMO and limpias >= MINIMO}
            print(f'Humo {variante}: {humo[variante]}', flush=True)
            continue
        clase = DetectorSLMDigito if variante in PROMPTS_DIGITO else DetectorSLMSiNo
        detector = clase(None, MODEL, cargar_prompt(variante), 'rol', cierre=cargar_pregunta(variante))
        limpias = 0
        for case_id in HUMO_CASOS:
            lineas = casos.con_roles(case_id, casos.cargar_texto(case_id))
            for n in range(1, len(lineas) + 1):
                mensajes, _ = detector.mensajes(lineas[:n])
                cuerpo = {'model': MODEL, 'messages': mensajes, 'options': {**detector.opciones(), 'num_predict': 3},
                          'stream': False, 'think': False, 'logprobs': True, 'top_logprobs': 5}
                pedido = urllib.request.Request('http://127.0.0.1:11434/api/chat', data=json.dumps(cuerpo).encode(),
                                                headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(pedido, timeout=600) as r:
                    respuesta = json.load(r)
                texto = respuesta.get('message', {}).get('content', '')
                ok = respuesta_limpia(variante, texto)
                limpias += ok
                diagnostico.append({'prompt': variante, 'case_id': case_id, 'linea': n, 'texto': texto, 'limpia': ok,
                                    'tokens': [x.get('token') for x in respuesta.get('logprobs') or []]})
        humo[variante] = {'lineas': len(propias), 'masa_ge_09': altas, 'masa_min': min(masas), 'masa_mediana': statistics.median(masas),
                          'respuesta_limpia': limpias, 'pasa': len(propias) == 48 and altas >= MINIMO and limpias >= MINIMO}
        print(f'Humo {variante}: {humo[variante]}', flush=True)
    (humo_dir / 'diagnostico-3-tokens.json').write_text(json.dumps(diagnostico, ensure_ascii=False, indent=2), encoding='utf-8')
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    salida = ['# Humo de la segunda vuelta de #143', '', f'Commit `{COMMIT}`. Casos: {", ".join(HUMO_CASOS)} (48 líneas).', '',
              f'Criterio, fijado antes de correr: masa ≥ 0,9 en al menos {MINIMO} de 48 líneas y, con 3 tokens, la respuesta '
              f'empieza con SÍ/NO o con un solo dígito en al menos {MINIMO} de 48 (en v4-L: líneas en que se encontró el '
              f'decimal del riesgo). Si no pasa, no corre en los 150.', '',
              '| prompt | pregunta final | masa ≥ 0,9 | masa mínima / mediana | respuesta limpia | resultado |', '|---|---|---|---|---|---|']
    for variante, d in humo.items():
        salida.append(f'| `{variante}` | {cargar_pregunta(variante) or "(el JSON de v4, cortado después del riesgo)"} | {d["masa_ge_09"]}/48 | {d["masa_min"]:.4f} / '
                      f'{d["masa_mediana"]:.4f} | {d["respuesta_limpia"]}/48 | {"PASA" if d["pasa"] else "NO PASA"} |')
    sucias = [d for d in diagnostico if not d['limpia']]
    salida += ['', f'Respuestas no limpias con 3 tokens: {len(sucias)}.', '']
    salida += [f'- `{d["prompt"]}` {d["case_id"]} L{d["linea"]}: {d["texto"]!r} {d["tokens"]}' for d in sucias[:40]]
    (humo_dir / 'humo.md').write_text('\n'.join(salida) + '\n', encoding='utf-8')
    descargar(humo_dir, 'parcial-puntaje-token-2-humo')

pasan = [v for v in TOKEN if humo[v]['pasa']]
print('Pasan la humo:', pasan, '| no corren en los 150:', [v for v in TOKEN if v not in pasan], flush=True)

# 2. Los 150. Primero cada configuración y después las repeticiones.
CORRIDAS = [
    # (carpeta, descripción, prompt). Etapa 1: solo v4-L; C y v4-premisa esperan las legítimas entrantes.
    ('v4-lectura', 'v4 JSON tal cual, leyendo el primer decimal del riesgo (v4-L)', 'v4-lectura'),
    ('v4-lectura-rep', 'Repetición de v4-L', 'v4-lectura'),
]
for carpeta, descripcion, prompt in CORRIDAS:
    destino = SALIDA / carpeta
    if prompt in TOKEN and prompt not in pasan:
        print(f'[{carpeta}] no corre: {prompt} no pasó la humo.', flush=True)
        continue
    if (destino / 'TERMINADA.txt').exists():
        print(f'[{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
        continue
    print(f'[{carpeta}] {descripcion}', flush=True)
    inicio = time.time()
    run = correr(destino, f'puntaje-token-2-{carpeta}', 'correr.py', '--prompts', prompt)
    subprocess.run([sys.executable, 'resumen.py', str(run)], check=True)
    (destino / 'TERMINADA.txt').write_text(
        f'{descripcion}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    print(f'[{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
    descargar(destino, f'parcial-puntaje-token-2-{carpeta}')

# 3. Controles de ventas y préstamos, solo para mirar.
destino = SALIDA / 'controles-ventas'
if not (destino / 'TERMINADA.txt').exists():
    prompts = ['v4', *[p for p in pasan if p == 'v4-lectura']]
    inicio = time.time()
    correr(destino, 'puntaje-token-2-controles-ventas', 'correr_controles.py', '--controles',
           'casos/controles-ventas.json', '--prompts', ','.join(prompts))
    (destino / 'TERMINADA.txt').write_text(f'Controles de ventas con {", ".join(prompts)}\ncommit {COMMIT}\n'
                                           f'minutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
    descargar(destino, 'parcial-puntaje-token-2-controles-ventas')

# 4. Inventario y empaquetado. El análisis se hace después, desde los CSV (analizar.py de la carpeta de la corrida).
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_puntaje_token_2.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143, segunda vuelta, etapa 1: v4-lectura con repetición (humo también de c-sino y c-digito); '
    f'más los controles de ventas\nIDS=(los 150)\n', encoding='utf-8')
zip_local = shutil.make_archive('/content/resultados-puntaje-token-2', 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
