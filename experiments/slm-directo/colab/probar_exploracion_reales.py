#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-EXPLORACION-REALES.ipynb: ver corridas/2026-11-20_exploracion-reales/README.md.
# Estado: propuesta sin discutir. #52, exploración con los conjuntos reales, posterior a la evaluación final: no la
# reemplaza. La configuración de la evaluación final (c-consejos-corte-riesgo) y los prompts de analizar.VARIANTES, solo
# en las líneas de OTRA y en todas ellas (--seguir-tras-aviso), para aplicar después las dos políticas de aviso sobre
# los mismos riesgos.
#
# 1. Ubica las legítimas reales de CallCenterEN que se subieron a la sesión (la carpeta sets/ o un ZIP que la traiga,
#    en cualquier lugar de /content) y arma los conjuntos fuera del repositorio, con conjuntos.py, igual que la
#    evaluación final: desarrollo, el test reservado (rama reserva/test, traída por ruta), las 33 coreanas de #144 y
#    las legítimas reales. Si faltan las legítimas reales, para ahí, antes de instalar nada.
# 2. Instala zstd y Ollama con reintentos (colab/preparar_colab.py) y baja el modelo.
# 3. Humo de formato en los 3 casos de siempre (48 líneas), con todos los prompts. Si no pasa la base, no corre nada;
#    el prompt que no pasa no corre.
# 4. Fase 1, con todos: las coreanas, las 33 legítimas reales y desarrollo (alcance-140). Es lo que usa la regla.
# 5. La regla (analizar.para_fase_2) dice qué prompts sirven. Fase 2, solo con la base y con esos: la zona gris de
#    Medicare y la vista principal del test. Así el test lo toca solo lo que ya se eligió sin mirarlo.
# Cada corrida terminada baja como ZIP; el análisis va después, con corridas/2026-11-20_exploracion-reales/analizar.py.
# Si se vuelve a ejecutar la celda en la misma sesión, lo que ya terminó no se repite.
# COLAB_REPO, COLAB_SALIDA, COLAB_RAIZ, COLAB_RESERVA, COLAB_PRUEBA_RESERVA, COLAB_PRUEBA_EXTERNO y
# COLAB_PRUEBA_LEGITIMAS solo existen para la prueba en seco.

import csv, hashlib, importlib.util, json, os, pathlib, shutil, subprocess, sys, time, urllib.request

REPO = pathlib.Path(os.environ.get('COLAB_REPO', '/content/bitacora_tesis'))
COMMIT = os.environ['COLAB_COMMIT']
EXTERNO = os.environ.get('COLAB_EXTERNO') or str(REPO / 'experiments/slm-directo/casos/externo/coreano')
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path(os.environ.get('COLAB_SALIDA', '/content/resultados-exploracion-reales'))
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


ex = _modulo('analizar_exploracion', exp / 'corridas/2026-11-20_exploracion-reales/analizar.py')
prep = _modulo('preparar_colab', exp / 'colab/preparar_colab.py')
an = ex.fin  # el análisis de la evaluación final: la humo, Ollama y el digest
BASE, CARPETAS = ex.BASE, ex.PROMPTS  # carpeta → prompt: la base y las variantes
TODAS = list(CARPETAS.values())
if not set(TODAS) <= PROMPTS_CORTE_RIESGO:
    raise RuntimeError('Algún prompt no está cortado tras el riesgo (PROMPTS_CORTE_RIESGO); detener y revisar.')

# Las legítimas reales, antes que nada: si falta la subida, que falle en segundos y no después de instalar todo.
# Sirve la carpeta sets/ o un ZIP que la traiga, en cualquier lugar de /content; COLAB_LEGITIMAS_REALES es opcional.
LEGITIMAS = str(prep.ubicar_legitimas_reales(pathlib.Path(os.environ.get('COLAB_RAIZ', str(SALIDA.parent))),
                                             SALIDA.parent / 'legitimas-reales',
                                             os.environ.get('COLAB_LEGITIMAS_REALES', '')))


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
        raise RuntimeError('Las legítimas reales que subiste no son el set congelado del 2026-11-18 (no coinciden con su '
                           f'manifiesto). Subí de nuevo legitimas-reales-sets.zip, sin modificar. Detalle: {error}') from error
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
for nombre in ORDEN:
    print(conjuntos.resumen(conjuntos.Conjunto(CONJ / nombre)), flush=True)
if not (CONJ / 'DESCARGADOS.txt').exists():  # el análisis los necesita: si Colab se corta, alcanzan los parciales
    descargar(CONJ, 'parcial-exploracion-conjuntos')
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

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--sin-reglas', '--hablantes', 'rol']
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
    run = correr(humo_dir / 'corrida', 'exploracion-humo', '--conjunto', str(CONJ / 'desarrollo'), '--casos', ','.join(HUMO_CASOS),
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
    descargar(humo_dir, 'parcial-exploracion-humo')
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
            correr(destino, f'exploracion-{nombre}-{carpeta}', '--conjunto', str(CONJ / conj_nombre), '--casos', ','.join(ids),
                   '--prompts', prompt, *CORRIDA)
            (destino / 'TERMINADA.txt').write_text(
                f'{nombre} ({len(ids)} casos de {conj_nombre}) · {prompt} · {" ".join(CORRIDA)}\ncommit {COMMIT}\n'
                f'minutos {(time.time() - inicio) / 60:.1f}\n', encoding='utf-8')
            print(f'[{nombre}/{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
            descargar(destino, f'parcial-exploracion-{nombre}-{carpeta}')


# 4. Fase 1: todos los prompts sobre lo que usa la regla (en cada uno, primero los reales).
fase(ex.FASE_1, list(CARPETAS))

# 5. La regla dice qué prompts siguen. Fase 2: la zona gris y el test, solo con la base y con esos.
fase_2 = SALIDA / 'fase-2.json'
if fase_2.exists():
    siguen = json.loads(fase_2.read_text(encoding='utf-8'))['carpetas']
else:
    try:
        siguen, orden = ex.para_fase_2(SALIDA)
        nota = 'sirven, en orden: ' + (', '.join(f'{c} · {p}' for c, p in orden) or 'ninguno')
    except Exception as error:  # si la regla no se puede aplicar acá, corren todos y se decide en el análisis
        siguen, nota = list(CARPETAS), f'no se pudo aplicar la regla en Colab ({error!r}): corren todos'
    fase_2.write_text(json.dumps({'carpetas': siguen, 'nota': nota}, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Fase 2 con:', siguen, '·', nota, flush=True)
fase(ex.FASE_2, siguen)

# 6. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_exploracion_reales.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#52, exploración con los conjuntos reales: {", ".join(TODAS)} en la fase 1 ({", ".join(ex.FASE_1)}) y '
    f'{", ".join(siguen)} en la fase 2 ({", ".join(ex.FASE_2)}), solo OTRA, en todas las líneas\nreserva/test {reserva_commit}{" (PRUEBA EN SECO)" if PRUEBA else ""}\n'
    + ''.join(f'{n} conjunto.json sha256 {conjuntos.sha256((CONJ / n / "conjunto.json").read_bytes())}\n' for n in ORDEN),
    encoding='utf-8')
zip_local = descargar(SALIDA, 'resultados-exploracion-reales')
print('TERMINADO: todo está en', zip_local, flush=True)
