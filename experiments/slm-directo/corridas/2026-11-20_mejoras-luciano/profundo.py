"""Lectura de los ZIP parciales de la base (2026-11-21): escalado de los dos niveles, riesgos por conjunto, demora y
16.384 contra 4096. Uso: python3 -I profundo.py CARPETA [DEV_FINAL TEST_FINAL], con los ZIP descomprimidos como los
arma analizar.py; las dos últimas son las carpetas `config` de desarrollo y del test de la evaluación final."""
import sys, importlib.util, collections, statistics, csv, glob
from pathlib import Path
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parents[1]))
spec = importlib.util.spec_from_file_location('m', AQUI / 'analizar.py'); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
import conjuntos
D = Path(sys.argv[1]); ex, fin = m.ex, m.fin
def cargar(tanda, carpeta='base'):
    conj = conjuntos.Conjunto(D / 'conjuntos' / m.TANDAS[tanda][0]); ids = ex.casos_de(tanda, conj)
    por, man = fin.leer(D / tanda / carpeta); f = fin.filas_de(por, man, carpeta, m.PROMPTS[carpeta])
    return conj, ids, conj.referencia(), f
print('== 1. Dos niveles, base: estafas')
for tanda in ('externo', 'desarrollo', 'test_reservado'):
    conj, ids, ref, f = cargar(tanda); regla = m.regla_de(conj, ids)
    at = {i: m.politicas(ex.riesgos(f[i]), regla[i])['primer aviso + regla'] for i in ids}
    co = {i: m.politicas(ex.riesgos(f[i]), regla[i])['cortá (regla o 0,5)'] for i in ids}
    est = [i for i in ids if ref[i]['clase'] == 'vishing']
    tc = [i for i in est if ref[i]['t_c_linea']]
    def c(av, cond): return sum(1 for i in est if cond(i, av[i]))
    print(tanda, len(est), 'estafas | atención:', c(at, lambda i,a: a is not None), '| cortá alguna vez:', c(co, lambda i,a: a is not None),
          '| cortá antes de que cumpla:', sum(1 for i in tc if co[i] and co[i] < ref[i]['t_c_linea']), '/', len(tc),
          '| atención antes de que cumpla:', sum(1 for i in tc if at[i] and at[i] < ref[i]['t_c_linea']), '/', len(tc),
          '| líneas entre atención y cortá (mediana):', statistics.median([co[i]-at[i] for i in est if co[i] and at[i]] or [0]))
    if tanda == 'externo':
        sin = [(i, max((r for _, r in ex.riesgos(f[i])), default=None), ref[i]['t_r_linea']) for i in est if ref[i]['t_r_linea'] and not (co[i] and co[i] <= ref[i]['t_r_linea'])]
        print('  coreanas con pedido donde cortá no llega a tiempo:', len(sin), 'riesgo máximo:', collections.Counter(r for _, r, _ in sin))
print('== 2. Riesgos que da la base en cada conjunto (consultas de OTRA)')
for tanda in ('externo', 'legitimas_reales', 'zona_gris', 'desarrollo', 'test_reservado'):
    conj, ids, ref, f = cargar(tanda)
    cl = {'externo': lambda i: 'estafa', 'legitimas_reales': lambda i: 'legítima', 'zona_gris': lambda i: 'zona gris'}.get(tanda, lambda i: 'estafa' if ref[i]['clase']=='vishing' else 'legítima')
    cnt = collections.defaultdict(collections.Counter)
    for i in ids:
        for _, r in ex.riesgos(f[i]): cnt[cl(i)][round(r,1)] += 1
    for k, c in cnt.items():
        n = sum(c.values()); print(f'  {tanda}/{k}: n={n} ' + ' '.join(f'{v}:{c[v]*100/n:.0f}%' for v in sorted(c)))
print('== 3. Latencia por consulta (ms), base')
for tanda in ('externo', 'legitimas_reales', 'desarrollo', 'test_reservado'):
    conj, ids, ref, f = cargar(tanda)
    ms = [float(r['ms']) for i in ids for r in f[i] if r['hablante']=='OTRA' and r['valida']=='true' and r['ms']]
    q = statistics.quantiles(ms, n=20); print(f'  {tanda}: p50 {statistics.median(ms):.0f} p95 {q[18]:.0f} máx {max(ms):.0f}')
print('== 4. 16384 (esta corrida) contra 4096 (evaluación final), misma consulta')
csv.field_size_limit(10**9)
for tanda, viejo in list(zip(('desarrollo', 'test_reservado'), sys.argv[2:4])):
    conj, ids, ref, f = cargar(tanda)
    nuevo = {(i, int(r['linea'])): r['riesgo'] for i in ids for r in f[i] if r['hablante']=='OTRA' and r['valida']=='true'}
    archivo = glob.glob(viejo + '/*/actualizaciones.csv')[0]
    old = {(r['case_id'], int(r['linea'])): r['riesgo'] for r in csv.DictReader(open(archivo, encoding='utf-8-sig')) if r['hablante']=='OTRA' and r['valida']=='true' and r['riesgo']}
    comunes = [k for k in old if k in nuevo]
    print(f'  {tanda}: {len(comunes)} consultas en las dos; mismo riesgo en {sum(old[k]==nuevo[k] for k in comunes)} ({sum(old[k]==nuevo[k] for k in comunes)*100/len(comunes):.1f} %)')
