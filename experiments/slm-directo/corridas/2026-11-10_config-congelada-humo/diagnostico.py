"""#143, configuración congelada: diagnóstico de la humo, fuera de la regla.

Escrito el 2026-11-10, después de ver los resultados, a pedido de Mateo: dónde flaquea el detector. No decide nada.
Uso, desde esta carpeta: python -I diagnostico.py > diagnostico-salida.md

- avisos antes del cumplimiento (T_A < T_C), con «riesgo ≥ 0,3» y con 0,2;
- las estafas sin aviso y las tardías, con los riesgos que escribió el modelo;
- el umbral 0,2, exacto desde la corrida operativa (la corrida tiene todas las líneas hasta el primer 0,3);
- las FA según `tipo_legitima`, la anotación previa de cada legítima;
- los valores del riesgo escrito;
- una capa de reglas (v1 y v2 del laboratorio) sobre las líneas de OTRA, unida al SLM.
"""
import collections, importlib.util, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
sys.path.insert(0, str(EXP))
spec = importlib.util.spec_from_file_location('analizar_humo', AQUI / 'analizar.py')
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
e3 = a.e3
filas, man = e3.leer(AQUI, 'desarrollo')
REF = a.REF
num = a.num


def aviso_u(i, u):
    return next((int(r['linea']) for r in filas[i] if r['consulta'] != 'omitida' and r['valida'] == 'true'
                 and num(r['riesgo']) is not None and num(r['riesgo']) >= u - 1e-9), None)


av = {i: aviso_u(i, 0.3) for i in a.IDS}
est = e3.ESTAFAS
leg = e3.LEGITIMAS

print('# Diagnóstico de la humo (después de ver los resultados; no decide)\n')
print('## Avisos antes del cumplimiento (T_A < T_C)')
conc = [i for i in est if REF[i].get('t_c_linea')]
for u in (0.3, 0.2):
    avu = {i: aviso_u(i, u) for i in a.IDS}
    antes = [i for i in conc if avu[i] and avu[i] < REF[i]['t_c_linea']]
    print(f'u={u}: {len(antes)}/{len(conc)} antes de T_C; sin aviso o tarde: '
          f'{[(i, avu[i], REF[i]["t_c_linea"]) for i in conc if i not in antes]}')

print('\n## Estafas sin aviso (u=0.3)')
for i in est:
    if av[i] is None:
        otra = [r for r in filas[i] if r['consulta'] != 'omitida']
        riesgos = [num(r['riesgo']) for r in otra if num(r['riesgo']) is not None]
        pedidos = [(e['linea'], '/'.join(e['etiquetas'])) for e in REF[i].get('evidencia') or [] if e['evento'] == 'pedido']
        print(f'- {i}: t_r={REF[i].get("t_r_linea")} t_c={REF[i].get("t_c_linea")} pedido={REF[i].get("pedido")} '
              f'max={max(riesgos)} valores={dict(collections.Counter(riesgos))} pedidos={pedidos} | {REF[i].get("que_prueba", "")[:110]}')

print('\n## Estafas con aviso tardío (después de T_R)')
for i in est:
    tr = REF[i].get('t_r_linea')
    if av[i] and tr and av[i] > tr:
        print(f'- {i}: aviso L{av[i]} t_r={tr} t_c={REF[i].get("t_c_linea")} pedido={REF[i].get("pedido")}')

print('\n## Umbral 0,2 (exacto desde la corrida operativa)')
for u in (0.3, 0.2):
    avu = {i: aviso_u(i, u) for i in a.IDS}
    print(u, a.fmt(a.metricas(avu, a.VISTA)))

print('\n## FA por tipo de legítima (anotación previa), u=0.3 y u=0.2')
for u in (0.3, 0.2):
    avu = {i: aviso_u(i, u) for i in a.IDS}
    c = collections.Counter(REF[i].get('tipo_legitima') for i in leg if avu[i])
    n = collections.Counter(REF[i].get('tipo_legitima') for i in leg)
    print(u, {k: f'{c[k]}/{n[k]}' for k in n})
print('\nFA (u=0.3) por tipo:')
for i in sorted(leg):
    if av[i]:
        print(f'  {REF[i].get("tipo_legitima"):20} {i:22} pedido={REF[i].get("pedido")} t_r={REF[i].get("t_r_linea")}')

print('\n## Valores de riesgo en las líneas de OTRA (legítimas y estafas, hasta el aviso o el final)')
for nombre, ids in (('estafas', est), ('legítimas', leg)):
    c = collections.Counter(num(r['riesgo']) for i in ids for r in filas[i] if r['consulta'] != 'omitida')
    print(nombre, sorted(c.items()))

print('\n## Capa de reglas sobre las líneas de OTRA, unida al SLM (u=0.3)')
import reglas, reglas_v2
CRIT = {'REQUEST_AUTH_CODE', 'REQUEST_SECRET', 'REQUEST_TRANSFER', 'REQUEST_REMOTE_ACCESS'}
def regla_en(i, version, etiquetas):
    for n, l in enumerate(e3.con_roles(i), 1):
        if l.hablante != 'OTRA':
            continue
        hits = reglas_v2.coincidencias_v2(l.texto) if version == 'v2' else reglas.coincidencias(l.texto)
        if {et for et, _ in hits} & etiquetas:
            return n
    return None
for version in ('v1', 'v2'):
    for nombre, etq in (('críticos', CRIT), ('todos', set(reglas.PATRONES))):
        rg = {i: regla_en(i, version, etq) for i in a.IDS}
        union = {i: min([x for x in (av[i], rg[i]) if x], default=None) for i in a.IDS}
        print(f'{version} {nombre:9} solo reglas {a.fmt(a.metricas(rg, a.VISTA))} | SLM o reglas {a.fmt(a.metricas(union, a.VISTA))}')
        if version == 'v2' and nombre == 'críticos':
            nuevas = [i for i in est if av[i] is None and union[i]]
            fa_nuevas = [i for i in leg if av[i] is None and union[i]]
            print('   estafas que suma:', nuevas)
            print('   FA que suma:', [(i, REF[i].get('tipo_legitima')) for i in fa_nuevas])
            c = collections.Counter(REF[i].get('tipo_legitima') for i in leg if union[i])
            print('   FA por tipo (unión):', dict(c))
            antes_tc = [i for i in conc if union[i] and union[i] < REF[i]['t_c_linea']]
            print(f'   antes de T_C: {len(antes_tc)}/{len(conc)}')
