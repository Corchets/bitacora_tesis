"""#52, mejoras de Luciano sobre la configuración de la evaluación final: las cuatro combinadas, sobre los mismos
riesgos. Escrito el 2026-11-20, antes de correr (README.md).

No corre modelos. Uso, desde esta carpeta, con el ZIP de Colab descomprimido en una carpeta vacía:
    python3 -I analizar.py CARPETA_DEL_ZIP

Cada prompt corre una vez en todas las líneas de OTRA. Sobre esos riesgos se aplican, sin volver a correr:
- la política de aviso: el primer «riesgo ≥ 0,3» o la confirmación (dos 0,3, o un 0,5), las de la exploración de Mateo;
- con o sin la regla de pedido crítico (regla_pedido_critico.py): el aviso es el primero de los dos;
- el aviso en dos niveles: «atención» es el de la política; «cortá» es el primero entre la regla y un «riesgo ≥ 0,5».
"""

import collections, importlib.util, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
import conjuntos  # noqa: E402
import regla_pedido_critico as rpc  # noqa: E402


def _cargar(nombre, ruta):
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


ex = _cargar('analizar_exploracion', AQUI.parent / '2026-11-20_exploracion-reales' / 'analizar.py')
fin = ex.fin
BASE = ex.BASE
PROMPTS = {'base': BASE, 'p-niveles': 'p-niveles-corte-riesgo', 'p-lista': 'p-lista-corte-riesgo'}  # en este orden
TANDAS = ex.TANDAS  # externo, legitimas_reales, desarrollo, zona_gris, test_reservado
NUM_CTX = 16384
FUERTE = 0.5
REFERENCIA = ('base', 'primer aviso')

# La regla, escrita antes de correr (README.md). Contra la referencia, en la misma sesión:
PIERDE_COREANAS = 1   # en las coreanas puede perder a lo sumo una estafa avisada y una a tiempo
RUIDO_TEST = 3        # en el test, a tiempo puede bajar hasta 3 (lo que cambia entre corridas)
BAJA_FA_REALES = 7    # mejora en avisos falsos: bajar 7 o más los de las 33 legítimas reales
SUBE_A_TIEMPO = 5     # mejora en detección: subir 5 o más los avisos a tiempo del test…
SUBE_FA = 1           # …sin sumar más de 1 aviso falso en el test ni en las legítimas reales
# El nivel «cortá» sirve si molesta poco y llega a tiempo en las estafas reales:
CORTA_FA_REALES, CORTA_FA_TEST, CORTA_COREANAS = 7, 7, 20  # FA ≤ 7 de 33 y ≤ 7 de 56; ≥ 20 de 27 coreanas a tiempo


def politicas(riesgos, regla):
    """{política: línea del aviso o None} de un caso, con sus riesgos [(línea, riesgo)] y la línea de la regla."""
    def primero(*lineas):
        hay = [l for l in lineas if l is not None]
        return min(hay) if hay else None
    pa, co = ex.primer_aviso(riesgos), ex.confirmacion(riesgos)
    fuerte = next((n for n, r in riesgos if r >= FUERTE), None)
    return {'primer aviso': pa, 'confirmación': co, 'primer aviso + regla': primero(pa, regla),
            'confirmación + regla': primero(co, regla), 'cortá (regla o 0,5)': primero(fuerte, regla)}


def regla_de(conj, ids):
    salida = {}
    for i in ids:
        lineas = [(l.hablante, l.texto) for l in conj.con_roles(i, conj.cargar_texto(i))]
        r = rpc.primer_pedido(lineas)
        salida[i] = r[0] if r else None
    return salida


def calcular(datos):
    """(cifras[(prompt, política)][tanda] = exitos, control)."""
    cifras, control = collections.defaultdict(dict), []
    for tanda, (nombre_conj, _) in TANDAS.items():
        if not (datos / 'conjuntos' / nombre_conj / 'conjunto.json').exists():
            continue
        conj = conjuntos.Conjunto(datos / 'conjuntos' / nombre_conj)
        ids, ref = ex.casos_de(tanda, conj), conj.referencia()
        regla = regla_de(conj, ids)
        for carpeta, prompt in PROMPTS.items():
            corrida = fin.leer(datos / tanda / carpeta)
            if corrida is None:
                control.append([tanda, carpeta, '—', '—', 'falta'])
                continue
            por_config, man = corrida
            filas = fin.filas_de(por_config, man, carpeta, prompt)
            prob = ex.controlar(conj, prompt, filas, man, ids)
            ps = man.get('parametros_slm', {})
            if (ps.get('num_ctx') in (4096, NUM_CTX) and ps.get('seed') == 42 and ps.get('temperatura') == 0.0):
                prob = [p for p in prob if p != 'num_ctx, seed o temperatura distintos']  # acá van 16.384 (o 4096)
            consultas = [r for v in filas.values() for r in v if r['hablante'] == 'OTRA']
            invalidas = collections.Counter(r['error'].split(':')[0] for r in consultas if r['valida'] != 'true')
            control.append([tanda, carpeta, ps.get('num_ctx'), f'{sum(invalidas.values())}/{len(consultas)}'
                            + (f' {dict(invalidas)}' if invalidas else ''), '; '.join(prob) or 'bien'])
            if prob:
                continue
            avisos = collections.defaultdict(dict)
            for i in ids:
                for pol, linea in politicas(ex.riesgos(filas[i]), regla[i]).items():
                    avisos[pol][i] = linea
            for pol, av in avisos.items():
                cifras[(carpeta, pol)][tanda] = fin.exitos(av, ids, ref)
        cifras[('solo la regla', '—')][tanda] = fin.exitos(regla, ids, ref)
    return cifras, control


def kn(cifras, combo, tanda, cifra):
    e = cifras.get(combo, {}).get(tanda, {}).get(cifra)
    return fin.kn(e) if e is not None else (None, None)


def resumen(cifras, combo):
    k = lambda t, c: kn(cifras, combo, t, c)[0]  # noqa: E731
    return {'coreanas': k('externo', 'estafas'), 'coreanas a tiempo': k('externo', 'a tiempo'),
            'FA reales': k('legitimas_reales', 'FA'), 'zona gris': k('zona_gris', 'FA'),
            'desarrollo estafas': k('desarrollo', 'estafas'), 'desarrollo a tiempo': k('desarrollo', 'a tiempo'),
            'desarrollo FA': k('desarrollo', 'FA'), 'test estafas': k('test_reservado', 'estafas'),
            'test a tiempo': k('test_reservado', 'a tiempo'), 'test FA': k('test_reservado', 'FA')}


def veredicto(c, r):
    """Por qué no sirve (lista vacía si sirve), contra la referencia r."""
    if None in c.values() or None in r.values():
        return ['faltan corridas']
    motivos = []
    if r['coreanas'] - c['coreanas'] > PIERDE_COREANAS or r['coreanas a tiempo'] - c['coreanas a tiempo'] > PIERDE_COREANAS:
        motivos.append('pierde coreanas')
    if r['test a tiempo'] - c['test a tiempo'] > RUIDO_TEST:
        motivos.append(f'pierde {r["test a tiempo"] - c["test a tiempo"]} a tiempo en el test')
    baja_fa = r['FA reales'] - c['FA reales'] >= BAJA_FA_REALES
    sube_det = (c['test a tiempo'] - r['test a tiempo'] >= SUBE_A_TIEMPO and c['test FA'] - r['test FA'] <= SUBE_FA
                and c['FA reales'] - r['FA reales'] <= SUBE_FA)
    if not (baja_fa or sube_det):
        motivos.append('no mejora lo suficiente')
    return motivos


def veredicto_corta(c):
    if None in (c['FA reales'], c['test FA'], c['coreanas a tiempo']):
        return ['faltan corridas']
    motivos = []
    if c['FA reales'] > CORTA_FA_REALES:
        motivos.append(f'{c["FA reales"]} FA reales')
    if c['test FA'] > CORTA_FA_TEST:
        motivos.append(f'{c["test FA"]} FA en el test')
    if c['coreanas a tiempo'] < CORTA_COREANAS:
        motivos.append(f'{c["coreanas a tiempo"]} coreanas a tiempo')
    return motivos


COLUMNAS = [('coreanas', 33), ('coreanas a tiempo', 27), ('FA reales', 33), ('zona gris', 42), ('desarrollo estafas', 46),
            ('desarrollo a tiempo', 36), ('desarrollo FA', 94), ('test estafas', 100), ('test a tiempo', 80), ('test FA', 56)]


def main(argv=None):
    datos = Path((argv or sys.argv[1:])[0])
    cifras, control = calcular(datos)
    print('# Mejoras de Luciano: salida de analizar.py\n\n## Control\n')
    print('| tanda | prompt | num_ctx | consultas inválidas | control |\n|---|---|---|---|---|')
    for fila in control:
        print('| ' + ' | '.join(map(str, fila)) + ' |')
    ref = resumen(cifras, REFERENCIA)
    print('\n## Todas las combinaciones\n')
    print('| prompt · política | ' + ' | '.join(f'{c} (/{n})' for c, n in COLUMNAS) + ' | veredicto |')
    print('|' + '---|' * (len(COLUMNAS) + 2))
    for combo in [*((p, pol) for p in PROMPTS for pol in
                    ('primer aviso', 'confirmación', 'primer aviso + regla', 'confirmación + regla', 'cortá (regla o 0,5)')),
                  ('solo la regla', '—')]:
        c = resumen(cifras, combo)
        if combo == REFERENCIA:
            v = 'referencia'
        elif combo[1].startswith('cortá'):
            m = veredicto_corta(c)
            v = 'sirve como «cortá»' if not m else 'no sirve como «cortá»: ' + ', '.join(m)
        elif combo[0] == 'solo la regla':
            v = '—'
        else:
            m = veredicto(c, ref)
            v = '**sirve**' if not m else 'no sirve: ' + ', '.join(m)
        print(f'| {combo[0]} · {combo[1]} | ' + ' | '.join('—' if c[k] is None else str(c[k]) for k, _ in COLUMNAS)
              + f' | {v} |')


if __name__ == '__main__':
    main()
