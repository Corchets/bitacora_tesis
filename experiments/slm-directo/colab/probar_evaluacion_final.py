#!/usr/bin/env python3
# Ejecutar en Google Colab desde COLAB-EVALUACION-FINAL.ipynb: ver corridas/2026-11-12_evaluacion-final/README.md.
# Estado: propuesta sin discutir. #143, evaluación final: la configuración congelada y las referencias simples, una sola
# vez, sobre desarrollo, el test reservado, el set externo de #144 y, si se sube su carpeta, las legítimas reales.
#
# 1. Arma los conjuntos fuera del repositorio, con conjuntos.py:
#    - desarrollo, desde este commit;
#    - el test reservado, desde la rama reserva/test, traída por ruta (git worktree en /content/reserva-test), con las
#      huellas comprobadas: no entra al checkout del tag;
#    - #144: las estafas coreanas. Por defecto, las 9 de casos/externo/coreano (en el repo); con COLAB_EXTERNO, la
#      carpeta de la custodia con las 33. En los dos casos, con sus huellas comprobadas
#      contra docs/corpus/MANIFIESTO-144-SET-COREANO-2026-11-11.json.
#    - Legítimas reales de CallCenterEN: solo con COLAB_LEGITIMAS_REALES, la carpeta sets/ de la custodia (los textos
#      no están en el repo). 33 legítimas en la vista principal y 42 de zona gris aparte, con sus manifiestos.
# 2. Humo de formato en los 3 casos de siempre (48 líneas), con la configuración y v4-corte. Si no pasa la
#    configuración, no corre nada; si no pasa v4-corte, esa referencia no corre.
# 3. Desarrollo: la configuración (roles, solo OTRA), v4-corte (roles, todas las líneas) y las reglas v1 y v2, en modo
#    operativo. Antes de tocar el test, la configuración tiene que reproducir sus cifras de desarrollo (±2,
#    analizar.control_desarrollo). Si no, para y no corre el test.
# 4. El test reservado, después #144 y las legítimas reales, con lo mismo. Cada corrida terminada baja como ZIP; el análisis va después, con
#    corridas/2026-11-12_evaluacion-final/analizar.py.
# COLAB_REPO, COLAB_SALIDA, COLAB_RESERVA, COLAB_PRUEBA_RESERVA, COLAB_PRUEBA_EXTERNO y COLAB_PRUEBA_LEGITIMAS solo
# existen para la prueba en seco.

import csv, hashlib, importlib.util, json, os, pathlib, shutil, subprocess, sys, time, urllib.request

REPO = pathlib.Path(os.environ.get('COLAB_REPO', '/content/bitacora_tesis'))
COMMIT = os.environ['COLAB_COMMIT']
CONFIG = os.environ.get('COLAB_CONFIG', 'c-premisa-corte-riesgo')
EXTERNO = os.environ.get('COLAB_EXTERNO') or str(REPO / 'experiments/slm-directo/casos/externo/coreano')
LEGITIMAS = os.environ.get('COLAB_LEGITIMAS_REALES', '')
head = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', 'HEAD'], text=True).strip()
print('Commit:', head, '· configuración:', CONFIG)
if head != COMMIT:
    raise RuntimeError(f'El checkout quedó en {head}, no en {COMMIT}; detener y revisar.')

SALIDA = pathlib.Path(os.environ.get('COLAB_SALIDA', '/content/resultados-evaluacion-final'))
SALIDA.mkdir(exist_ok=True)
(SALIDA / 'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'], text=True), encoding='utf-8')
print((SALIDA / 'gpu.txt').read_text(encoding='utf-8'))

exp = REPO / 'experiments/slm-directo'
os.chdir(exp)
sys.path.insert(0, str(exp))
import conjuntos  # noqa: E402
from detectores import PROMPTS_CORTE_RIESGO  # noqa: E402

_spec = importlib.util.spec_from_file_location('analizar_final', exp / 'corridas/2026-11-12_evaluacion-final/analizar.py')
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
if CONFIG not in PROMPTS_CORTE_RIESGO:
    raise RuntimeError(f'{CONFIG} no es un prompt cortado tras el riesgo (PROMPTS_CORTE_RIESGO); detener y revisar.')
if CONFIG not in an.CIFRAS_DESARROLLO:
    raise RuntimeError(f'Faltan las cifras de desarrollo de {CONFIG} en analizar.CIFRAS_DESARROLLO: van antes del tag.')

# Misma versión de Ollama, modelo y digest que la humo y la sensibilidad: un cambio por vez.
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
print('Digest:', model['digest'])
if model['digest'].removeprefix('sha256:') != an.e3.DIGEST:
    raise RuntimeError('Digest distinto al de las líneas base; detener y revisar.')
(SALIDA / 'digest.txt').write_text(f"{MODEL} {model['digest']}\n", encoding='utf-8')


def descargar(carpeta, nombre):
    from google.colab import files
    archivo = shutil.make_archive(str(SALIDA.parent / nombre), 'zip', carpeta)
    print(f'Descargando {archivo}', flush=True)
    files.download(archivo)


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
if not (CONJ / 'desarrollo' / 'conjunto.json').exists():
    conjuntos.preparar_desarrollo(CONJ)
if not (CONJ / 'test_reservado' / 'conjunto.json').exists():
    conjuntos.preparar_test(RESERVA, CONJ, **PRUEBA)
if EXTERNO and not (CONJ / 'externo' / 'conjunto.json').exists():
    PRUEBA_EXT = {}
    if os.environ.get('COLAB_PRUEBA_EXTERNO'):  # solo la prueba en seco: un set sintético con su propio manifiesto
        PRUEBA_EXT = {'manifiesto': pathlib.Path(os.environ['COLAB_PRUEBA_EXTERNO'])}
    conjuntos.preparar_externo(pathlib.Path(EXTERNO), CONJ, **PRUEBA_EXT)
if LEGITIMAS and not (CONJ / 'legitimas_reales' / 'conjunto.json').exists():
    PRUEBA_LEG = {}
    if os.environ.get('COLAB_PRUEBA_LEGITIMAS'):  # solo la prueba en seco: 'manifiesto_legítimas,manifiesto_zona_gris'
        _ml, _mg = os.environ['COLAB_PRUEBA_LEGITIMAS'].split(',')
        PRUEBA_LEG = {'manifiesto_legitimas': pathlib.Path(_ml), 'manifiesto_zona_gris': pathlib.Path(_mg)}
    conjuntos.preparar_legitimas_reales(pathlib.Path(LEGITIMAS), CONJ, **PRUEBA_LEG)
ORDEN = ['desarrollo', 'test_reservado'] + (['externo'] if EXTERNO else []) + (['legitimas_reales'] if LEGITIMAS else [])
for nombre in ORDEN:
    print(conjuntos.resumen(conjuntos.Conjunto(CONJ / nombre)), flush=True)

COMUNES = ['--modelos', MODEL, '--num-ctx', '4096', '--seed', '42', '--hablantes', 'rol']
DETECTORES = {
    'config': ['--prompts', CONFIG, '--sin-reglas', '--solo-otra'],
    'v4': ['--prompts', an.V4, '--sin-reglas'],
    'reglas': ['--solo-reglas', '--reglas', 'v1,v2'],
}
HUMO_CASOS = ['CV2-D-V-ORGANISMO_PREVISIONAL-004', 'CV2-D-L-BANCO-001', 'SC-WA-CODE-01-e01']  # los de las humos de #143
LINEAS_HUMO = 48


def correr(destino, etiqueta, *args):
    shutil.rmtree(destino, ignore_errors=True)  # una corrida cortada se repite entera
    destino.mkdir(parents=True)
    orden = [sys.executable, 'correr.py', *args, *COMUNES, '--etiqueta', etiqueta, '--salida', str(destino)]
    print('Ejecutando:', ' '.join(orden), flush=True)
    subprocess.run(orden, check=True)
    (run,) = [p for p in destino.iterdir() if (p / 'manifiesto.json').exists()]
    return run


# 2. Humo de formato, en todas las líneas de los 3 casos.
humo_dir = SALIDA / 'humo'
if (humo_dir / 'humo.json').exists():
    humo = json.loads((humo_dir / 'humo.json').read_text(encoding='utf-8'))
    print('Humo ya hecha en esta sesión:', {p: 'PASA' if d['pasa'] else 'NO PASA' for p, d in humo.items()}, flush=True)
else:
    run = correr(humo_dir / 'corrida', 'final-humo', '--conjunto', str(CONJ / 'desarrollo'), '--casos', ','.join(HUMO_CASOS),
                 '--prompts', f'{CONFIG},{an.V4}', '--sin-reglas', '--seguir-tras-aviso')
    with open(run / 'actualizaciones.csv', encoding='utf-8-sig', newline='') as f:
        filas = [r for r in csv.DictReader(f) if r['detector'] == 'slm']
    humo = {}
    for prompt in (CONFIG, an.V4):
        propias = [r for r in filas if r['prompt'] == prompt]
        leidas = sum(r['valida'] == 'true' for r in propias)
        humo[prompt] = {'lineas': len(propias), 'leidas': leidas,
                        'errores': sorted({r['error'] for r in propias if r['valida'] != 'true'}),
                        'pasa': len(propias) == leidas == LINEAS_HUMO}
    (humo_dir / 'humo.json').write_text(json.dumps(humo, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(humo, ensure_ascii=False, indent=2), flush=True)
    descargar(humo_dir, 'parcial-final-humo')
if not humo[CONFIG]['pasa']:
    raise RuntimeError('La configuración no pasó la humo de formato: no se corre nada. Ver humo/humo.json.')
if not humo[an.V4]['pasa']:
    print(f'{an.V4} no pasó la humo: esa referencia no corre (avisar a Mateo).', flush=True)
    del DETECTORES['v4']

# 3 y 4. Desarrollo, el control de reproducibilidad, el test y #144.
for nombre in ORDEN:
    for carpeta, args in DETECTORES.items():
        destino = SALIDA / nombre / carpeta
        if (destino / 'TERMINADA.txt').exists():
            print(f'[{nombre}/{carpeta}] ya terminada en esta sesión; no se repite.', flush=True)
        else:
            inicio = time.time()
            correr(destino, f'final-{nombre}-{carpeta}', '--conjunto', str(CONJ / nombre), *args)
            (destino / 'TERMINADA.txt').write_text(
                f'{nombre} · {carpeta} · {" ".join(args)}\ncommit {COMMIT}\nminutos {(time.time() - inicio) / 60:.1f}\n',
                encoding='utf-8')
            print(f'[{nombre}/{carpeta}] terminada en {(time.time() - inicio) / 60:.1f} min', flush=True)
            descargar(destino, f'parcial-final-{nombre}-{carpeta}')
        if nombre == 'desarrollo' and carpeta == 'config':
            ok, texto = an.control_desarrollo(SALIDA, conjuntos.Conjunto(CONJ / 'desarrollo'), CONFIG)
            (SALIDA / 'control-desarrollo.txt').write_text(f'{"OK" if ok else "NO"}: {texto}\n', encoding='utf-8')
            print('Control de desarrollo:', texto, flush=True)
            if not ok:
                descargar(SALIDA, 'resultados-evaluacion-final-sin-test')
                raise RuntimeError('La configuración no reproduce desarrollo: no se corre el test. Avisar a Mateo; '
                                   'no se ajusta nada.')

# 5. Inventario y empaquetado. El análisis se hace después, desde los CSV.
subprocess.run([sys.executable, '-m', 'pip', 'freeze'], stdout=(SALIDA / 'pip-freeze.txt').open('w'), check=True)
(SALIDA / 'ollama-version.txt').write_text(version, encoding='utf-8')
(SALIDA / 'script-sha256.txt').write_text(
    hashlib.sha256((exp / 'colab/probar_evaluacion_final.py').read_bytes()).hexdigest() + '\n', encoding='utf-8')
(SALIDA / 'commit.txt').write_text(
    f'{COMMIT}\n#143, evaluación final: {CONFIG}, {", ".join(DETECTORES)} sobre {", ".join(ORDEN)}, en modo operativo\n'
    f'reserva/test {reserva_commit}{" (PRUEBA EN SECO)" if PRUEBA else ""}\n'
    + ''.join(f'{n} conjunto.json sha256 {conjuntos.sha256((CONJ / n / "conjunto.json").read_bytes())}\n' for n in ORDEN),
    encoding='utf-8')
zip_local = shutil.make_archive(str(SALIDA.parent / 'resultados-evaluacion-final'), 'zip', SALIDA)
print('TERMINADO: todo está en', zip_local, flush=True)
from google.colab import files  # noqa: E402
files.download(zip_local)
