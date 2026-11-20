#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-MEJORAS-LUCIANO.ipynb: ver corridas/2026-11-20_mejoras-luciano/README.md.
# Estado: propuesta sin discutir. #52, mejoras de Luciano sobre la configuración de la evaluación final, posterior a
# ella: no la reemplaza. Corre la base (c-consejos-corte-riesgo), p-niveles y p-lista en todas las líneas de OTRA
# (--seguir-tras-aviso), con 16.384 tokens de contexto, sobre los cinco conjuntos. La regla de pedido crítico, la
# confirmación y el aviso en dos niveles se aplican después sobre los mismos riesgos (analizar.py de esa carpeta).
#
# 1. Arma los conjuntos fuera del repositorio, con conjuntos.py: desarrollo, el test reservado (rama reserva/test,
#    traída por ruta), las 33 coreanas de #144 y las legítimas reales de CallCenterEN, las dos del repo.
# 2. Instala zstd y Ollama con reintentos (colab/preparar_colab.py) y baja el modelo.
# 3. Humo de formato en los 3 casos de siempre (48 líneas), con los tres prompts. Si no pasa la base, no corre nada.
# 4. Prompt por prompt, en el orden de PROMPTS, sobre cada conjunto: si Colab se corta, los primeros quedan completos.
# Cada corrida terminada baja como ZIP. Si se vuelve a ejecutar la celda en la misma sesión, lo terminado no se repite.

import csv, hashlib, importlib.util, json, os, pathlib, shutil, subprocess, sys, time, urllib.request

REPO = pathlib.Path(os.environ.get('COLAB_REPO', '/content/bitacora_tesis'))
COMMIT = os.environ['COLAB_COMMIT']
EXTERNO = os.environ.get('COLAB_EXTERNO') or str(REPO / 'experiments/slm-directo/casos/externo/coreano')
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path(os.environ.get('COLAB_SALIDA', '/content/resultados-mejoras-luciano'))
SALIDA.mkdir(exist_ok=True)
try:
    gpu = subprocess.check_output(['nvidia-smi'], text=True)
except (OSError, subprocess.CalledProcessError) as error:
    raise RuntimeError('No hay GPU en esta sesión: elegí T4 en Entorno de ejecución → Cambiar tipo de entorno de ejecución '
                       'y volvé a ejecutar la celda.') from error
(SALIDA / 'gpu.txt').write_text(gpu, encoding='utf-8')
print(gpu)

exp = REPO / 'experiments/slm-directo'
os.chdir(exp)
sys.path.insert(0, str(exp))
import conjuntos  # noqa: E402
from detectores import PROMPTS_CORTE_RIESGO  # noqa: E402


def _modulo(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


me = _modulo('analizar_mejoras', exp / 'corridas/2026-11-20_mejoras-luciano/analizar.py')
ex = me.ex
prep = _modulo('preparar_colab', exp / 'colab/preparar_colab.py')
an = ex.fin  # el análisis de la evaluación final: la humo, Ollama y el digest
BASE, CARPETAS = me.BASE, me.PROMPTS  # carpeta → prompt: la base, p-niveles y p-lista
TODAS = list(CARPETAS.values())
if not set(TODAS) <= PROMPTS_CORTE_RIESGO:
    raise RuntimeError('Algún prompt no está cortado tras el riesgo (PROMPTS_CORTE_RIESGO); detener y revisar.')

LEGITIMAS = str(REPO / 'experiments/slm-directo/casos/externo/legitimas-reales')


def descargar(carpeta, nombre):
    return prep.descargar(carpeta, nombre, SALIDA.parent)


# 1. Conjuntos, fuera del checkout del tag (así correr.py no ve cambios sin commitear).
RESERVA = pathlib.Path(os.environ.get('COLAB_RESERVA', '/content/reserva-test'))
if not RESERVA.exists():
    subprocess.run(['git', '-C', str(REPO), 'fetch', 'origin', 'reserva/test'], check=True)
    subprocess.run(['git', '-C', str(REPO), 'worktree', 'add', '--detach', str(RESERVA), 'FETCH_HEAD'], check=True)
reserva_commit = subprocess.check_output(['git', '-C', str(RESERVA), 'rev-parse', 'HEAD'], text=True).strip()
print('reserva/test:', reserva_commit)
PRUEBA = {}
if os.environ.get('COLAB_PRUEBA_RESERVA'):  # solo la prueba en seco: una reserva sintética con sus propias huellas
    PRUEBA = json.loads(pathlib.Path(os.environ['COLAB_PRUEBA_RESERVA']).read_text(encoding='utf-8'))
    PRUEBA['manifiesto'] = pathlib.Path(PRUEBA['manifiesto'])
    print('PRUEBA EN SECO: reserva sintética, no es el test.', flush=True)
CONJ = SALIDA / 'conjuntos'
CONJ.mkdir(exist_ok=True)


def falta(nombre):
    """True si hay que armar el conjunto. Un armado que quedó a medias se borra, para rehacerlo."""
    if (CONJ / nombre / 'conjunto.json').exists():
        return False
    shutil.rmtree(CONJ / nombre, ignore_errors=True)
    return True


if falta('legitimas_reales'):  # primero: es lo único que depende de lo que se subió
    PRUEBA_LEG = {}
    if os.environ.get('COLAB_PRUEBA_LEGITIMAS'):  # solo la prueba en seco: 'manifiesto_legítimas,manifiesto_zona_gris'
        _ml, _mg = os.environ['COLAB_PRUEBA_LEGITIMAS'].split(',')
        PRUEBA_LEG = {'manifiesto_legitimas': pathlib.Path(_ml), 'manifiesto_zona_gris': pathlib.Path(_mg)}
    try:
        conjuntos.preparar_legitimas_reales(pathlib.Path(LEGITIMAS), CONJ, **PRUEBA_LEG)
    except ValueError as error:
        raise RuntimeError(f'Las legítimas reales del repo no coinciden con su manifiesto: {error}') from error
if falta('desarrollo'):
    conjuntos.preparar_desarrollo(CONJ)
if falta('test_reservado'):
    conjuntos.preparar_test(RESERVA, CONJ, **PRUEBA)
if falta('externo'):
    PRUEBA_EXT = {}
    if os.environ.get('COLAB_PRUEBA_EXTERNO'):  # solo la prueba en seco: un set sintético con su propio manifiesto
        PRUEBA_EXT = {'manifiesto': pathlib.Path(os.environ['COLAB_PRUEBA_EXTERNO'])}
    conjuntos.preparar_externo(pathlib.Path(EXTERNO), CONJ, **PRUEBA_EXT)
ORDEN = ['externo', 'legitimas_reales', 'desarrollo', 'test_reservado']  # los cuatro conjuntos armados
TANDAS_ORDEN = ['externo', 'legitimas_reales', 'zona_gris', 'desarrollo', 'test_reservado']
for nombre in ORDEN:
    print(conjuntos.resumen(conjuntos.Conjunto(CONJ / nombre)), flush=True)
if not (CONJ / 'DESCARGADOS.txt').exists():  # el análisis los necesita: si Colab se corta, alcanzan los parciales
    descargar(CONJ, 'parcial-mejoras-conjuntos')
    (CONJ / 'DESCARGADOS.txt').write_text('ok\n', encoding='utf-8')

# 2. Ollama: la misma versión, el mismo modelo y el mismo digest que la evaluación final.
OLLAMA_VERSION = '0.40.14'
print('zstd:', prep.asegurar_zstd(), flush=True)
prep.instalar_ollama(OLLAMA_VERSION)
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
prep.reintentar(['ollama', 'pull', MODEL], 'La descarga del modelo')
with urllib.request.urlopen('http://127.0.0.1:11434/api/tags') as response:
    models = json.load(response)['models']
model = next(m for m in models if m['name'] == MODEL)
print('Digest:', model['digest'])
if model['digest'].removeprefix('sha256:') != an.e3.DIGEST:
    raise RuntimeError('Digest distinto al de las líneas base; detener y revisar.')
(SALIDA / 'digest.txt').write_text(f"{MODEL} {model['digest']}\n", encoding='utf-8')

COMUNES = ['--modelos', MODEL, '--num-ctx', str(me.NUM_CTX), '--seed', '42', '--sin-reglas', '--hablantes', 'rol']
CORRIDA = ['--solo-otra', '--seguir-tras-aviso']  # todas las líneas de OTRA: las dos políticas salen de los mismos riesgos
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48


def correr(destino, etiqueta, *args):
    shutil.rmtree(destino, ignore_errors=True)  # una corrida cortada se repite entera
    destino.mkdir(parents=True)
    orden = [sys.executable, 'correr.py', *args, *COMUNES, '--etiqueta', etiqueta, '--salida', str(destino)]
    print('Ejecutando:', ' '.join(orden)[:600], flush=True)
    subprocess.run(orden, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
    return run


# 3. Humo de formato, en todas las líneas de los 3 casos.
humo_dir = SALIDA / 'humo'
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', {p: 'PASA' if d['pasa'] else 'NO PASA' for p, d in humo.items()}, flush=True)
else:
    run = correr(humo_dir / 'corrida', 'mejoras-humo', '--conjunto', str(CONJ / 'desarrollo'), '--casos', ','.join(HUMO_CASOS),
                 '--prompts', ','.join(TODAS), '--seguir-tras-aviso')
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    humo = {}
    for prompt in TODAS:
        propias = [r for r in filas if r['prompt'] == prompt]
        leidas = sum(r['valida'] == 'true' for r in propias)
        humo[prompt] = {'lineas': len(propias), 'leidas': leidas,
                        'errores': sorted({r['error'] for r in propias if r['valida'] != 'true'}),
                        'pasa': len(propias) == leidas == LINEAS_HUMO}
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(humo, ensure_ascii=False, indent=2), flush=True)
    descargar(humo_dir, 'parcial-mejoras-humo')
if not humo[BASE]['pasa']:
    raise RuntimeError('La base no pasó la humo de formato: no se corre nada. Ver humo/humo.json.')
pasan = [p for p in TODAS if humo[p]['pasa']]



def fase(tandas, carpetas):
    """Corre cada prompt de `carpetas` sobre cada tanda (un conjunto y sus casos), prompt por prompt: si Colab se
    corta, los primeros quedan completos. Lo terminado en la sesión no se repite."""
    for carpeta in carpetas:
        prompt = CARPETAS[carpeta]
        if prompt not in pasan:
            print(f'[{carpeta}] no corre: {prompt} no pasó la humo.', flush=True)
            continue
        for nombre in tandas:
            conj_nombre, destino = ex.TANDAS[nombre][0], SALIDA / nombre / carpeta
            if (destino / 'TERMINADA.txt').exists():
                print(f'[{nombre}/{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
                continue
            ids = ex.casos_de(nombre, conjuntos.Conjunto(CONJ / conj_nombre))
            inicio = time.time()
            correr(destino, f'mejoras-{nombre}-{carpeta}', '--conjunto', str(CONJ / conj_nombre), '--casos', ','.join(ids),
                   '--prompts', prompt, *CORRIDA)
            (destino / 'TERMINADA.txt').write_text(
                f'{nombre} ({len(ids)} casos de {conj_nombre}) · {prompt} · {" ".join(CORRIDA)}\ncommit {COMMIT}\n'
                f'minutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
            print(f'[{nombre}/{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
            descargar(destino, f'parcial-mejoras-{nombre}-{carpeta}')


# 4. Todos los prompts sobre todos los conjuntos, prompt por prompt: primero la base entera.
fase(TANDAS_ORDEN, list(CARPETAS))

# 6. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_mejoras_luciano.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#52, mejoras de Luciano: {", ".join(TODAS)} en {", ".join(TANDAS_ORDEN)}, solo OTRA, en todas las '
    f'líneas, num_ctx {me.NUM_CTX}\nreserva/test {reserva_commit}{" (PRUEBA EN SECO)" if PRUEBA else ""}\n'
    + ''.join(f'{n} conjunto.json sha256 {conjuntos.sha256((CONJ / n / "conjunto.json").read_bytes())}\n' for n in ORDEN),
    encoding='utf-8')
zip_local = descargar(SALIDA, 'resultados-mejoras-luciano')
print('TERMINADO: todo está en', zip_local, flush=True)
