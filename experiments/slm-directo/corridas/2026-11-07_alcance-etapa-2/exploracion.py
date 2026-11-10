"""#143, etapa 2: exploración para decidir cómo seguir, escrita el 2026-11-09 después de ver los resultados.

No cambia el criterio ni su resultado (analizar.py) ni el diagnóstico (diagnostico.py). Responde preguntas de Mateo
para la propuesta de cómo seguir; lo que sale de acá son hipótesis (ADR 0005).
1. alerta_sugerida en C: ¿suma algo con «riesgo ≥ 0,3»? ¿Cuánto cuesta generar después del riesgo?
2. ¿El riesgo de C sube y baja dentro de una llamada? ¿Qué lo hace bajar?
3. Frases tranquilizadoras de OTRA («no te preocupes», «no te voy a pedir…»).
4. Consultar solo en las líneas de OTRA: simulación con las mismas salidas.
5. Aperturas: avisos de C en L1–L3 y riesgo de la primera línea de OTRA por familia.
6. Legítimas: FA según si piden datos personales y escenarios repetidos entre lotes.
Solo biblioteca estándar; no corre modelos ni lee la reserva. Uso, desde esta carpeta:
    python -I exploracion.py
"""
import collections, importlib.util, math, re, statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('analizar_etapa2', AQUI / 'analizar.py')
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
num, REF, tabla = an.num, an.REF, an.tabla
EST, LEG, VISTA = an.ESTAFAS, an.LEGITIMAS, an.VISTA
LOTE = {i: n for n, l in an.LOTES.items() for i in an.leer_lista(l)}
REGLA_C, REGLA_V4, U = 'riesgo ≥ 0.3 o alerta', 'riesgo ≥ 0.4 o alerta', 0.3


def piso(x):
    """El riesgo al decimal de abajo (0,85 → 0,8)."""
    return math.floor(x * 10 + 1e-9) / 10


def validas(filas, i):
    return [r for r in filas.get(i, []) if r['valida'] == 'true' and num(r['riesgo']) is not None]


def dispara(r):
    return num(r['riesgo']) >= U - 1e-9 or r['alerta_escrita'] == 'true'


def recorte(t, n=120):
    t = ' '.join(t.split())
    return t if len(t) <= n else t[:n - 1] + '…'


def paso(a, b, i):
    return (f"{i} L{b['linea']} {num(a['riesgo']):g}→{num(b['riesgo']):g} (T_R {REF[i].get('t_r_linea') or '–'}): "
            f"{recorte(b['texto'])}")


def main():
    filas = {c: an.leer(AQUI, c)[0] for c in ('c-json-corte', 'c-json-corte-rep', 'v4-corte')}
    C = filas['c-json-corte']
    print('# #143, etapa 2: exploración para decidir cómo seguir (escrita después de ver los resultados)\n')
    print(f'C con «{REGLA_C}», primera corrida, dentro del alcance (46 estafas y 94 legítimas), salvo donde se dice.\n')

    print('## 1. alerta_sugerida en C y lo que cuesta generar después del riesgo\n')
    filas_md = []
    for carpeta, f in filas.items():
        al = [r for i in VISTA for r in validas(f, i) if r['alerta_escrita'] == 'true']
        rs = [num(r['riesgo']) for r in al]
        filas_md.append([carpeta, len(al), len({r['case_id'] for r in al}), f'{min(rs):g}',
                         sum(x < 0.3 - 1e-9 for x in rs), sum(x < 0.4 - 1e-9 for x in rs)])
    tabla(filas_md, ['corrida', 'líneas con alerta escrita', 'llamadas', 'riesgo mínimo', 'con riesgo < 0,3',
                     'con riesgo < 0,4'])
    for carpeta in ('c-json-corte', 'c-json-corte-rep'):
        f = filas[carpeta]
        con = an.avisos(f, REGLA_C, VISTA)
        sin = {i: next((int(r['linea']) for r in validas(f, i) if num(r['riesgo']) >= U - 1e-9), None) for i in VISTA}
        print(f'- {carpeta}: con «riesgo ≥ 0,3» sola cambia la línea de aviso en {sum(con[i] != sin[i] for i in VISTA)} '
              f'de {len(VISTA)} llamadas.')
    comienzos = collections.Counter(r['crudo'].split('"alerta_sugerida"')[0] for i in VISTA for r in validas(C, i))
    print('\nCómo empieza la salida de C (hasta alerta_sugerida), lo más común:\n')
    for t, n in comienzos.most_common(4):
        print(f'- {n} líneas: `{t!r}`')
    por_token = [num(r['runtime_eval_ns']) / num(r['tokens_salida']) / 1e6 for i in VISTA for r in validas(C, i)
                 if num(r['runtime_eval_ns']) and num(r['tokens_salida'])]
    prompt = [num(r['runtime_prompt_eval_ns']) / 1e6 for i in VISTA for r in validas(C, i) if num(r['runtime_prompt_eval_ns'])]
    total = [num(r['ms']) for i in VISTA for r in validas(C, i) if num(r['ms'])]
    print(f'\nEn T4, medianas por línea: {statistics.median(total):.0f} ms en total, {statistics.median(prompt):.0f} ms de '
          f'lectura del prompt y {statistics.median(por_token):.1f} ms por token generado (24 tokens).\n')

    print('## 2. ¿El riesgo de C sube y baja?\n')
    print('Cambio del riesgo respecto de la línea anterior, según quién habla en la línea.\n')
    filas_md = []
    for clase, ids in (('estafas', EST), ('legítimas', LEG)):
        deltas = collections.defaultdict(list)
        for i in ids:
            v = validas(C, i)
            for a, b in zip(v, v[1:]):
                deltas[b['hablante']].append(round(num(b['riesgo']) - num(a['riesgo']), 3))
        for h in ('OTRA', 'PROTEGIDA'):
            d = deltas[h]
            sube, baja = sum(x > 0 for x in d), sum(x < 0 for x in d)
            filas_md.append([clase, h, len(d), f'{sube} ({100 * sube / len(d):.0f} %)', f'{baja} ({100 * baja / len(d):.0f} %)',
                             f'{statistics.mean(d):+.3f}'])
    tabla(filas_md, ['clase', 'línea de', 'líneas', 'sube', 'baja', 'cambio medio'])
    filas_md = []
    for clase, ids in (('estafas', EST), ('legítimas', LEG)):
        cruza = caen = vuelve = termina_bajo = 0
        for i in ids:
            v = validas(C, i)
            k = next((n for n, r in enumerate(v) if num(r['riesgo']) >= U - 1e-9), None)
            if k is None:
                continue
            cruza += 1
            resto = v[k + 1:]
            j = next((n for n, r in enumerate(resto) if num(r['riesgo']) < U - 1e-9), None)
            if j is not None:
                caen += 1
                vuelve += any(num(r['riesgo']) >= U - 1e-9 for r in resto[j:])
            termina_bajo += num(v[-1]['riesgo']) < U - 1e-9
        filas_md.append([clase, cruza, caen, vuelve, termina_bajo])
    tabla(filas_md, ['clase', 'llegan a 0,3', 'después bajan de 0,3', 'y vuelven a 0,3', 'terminan debajo de 0,3'])
    print('Bajadas de 0,2 o más en una línea, por quién habla:\n')
    grandes = collections.defaultdict(list)
    for clase, ids in (('estafa', EST), ('legítima', LEG)):
        for i in ids:
            v = validas(C, i)
            for a, b in zip(v, v[1:]):
                if num(b['riesgo']) - num(a['riesgo']) <= -0.2 + 1e-9:
                    grandes[(clase, b['hablante'])].append(paso(a, b, i))
    for (clase, h), ej in sorted(grandes.items()):
        print(f'### {clase}, línea de {h}: {len(ej)}\n')
        for e in ej:
            print(f'- {e}')
        print()

    print('## 3. Frases tranquilizadoras de OTRA\n')
    tranq = re.compile(r'tranquil|no (es|se trata de) (una|ninguna) estafa|no te preocup|no se preocup|'
                       r'no (te|le) (voy|vamos) a pedir|nunca (te|le) (vamos a |va a )?pedi|no compart|'
                       r'no (le|se lo|te lo) (des|dé|digas|diga)|por (tu|su) seguridad|para (tu|su) (seguridad|tranquilidad)|'
                       r'es (todo )?(seguro|oficial)|no soy (un |ningún )?estafador|cuento|verso', re.I)
    print(f'Búsqueda por expresión regular: `{tranq.pattern}`.\n')
    for clase, ids in (('estafas', EST), ('legítimas', LEG)):
        con, resto, ej = [], [], []
        for i in ids:
            v = validas(C, i)
            for a, b in zip(v, v[1:]):
                if b['hablante'] != 'OTRA':
                    continue
                d = round(num(b['riesgo']) - num(a['riesgo']), 3)
                if tranq.search(b['texto']):
                    con.append(d)
                    ej.append(paso(a, b, i))
                else:
                    resto.append(d)
        print(f'- **{clase}:** {len(con)} líneas de OTRA; sube {sum(x > 0 for x in con)}, baja {sum(x < 0 for x in con)}, '
              f'igual {sum(x == 0 for x in con)} (cambio medio {statistics.mean(con):+.3f}; resto de las líneas de OTRA '
              f'{statistics.mean(resto):+.3f}).')
        for e in ej:
            print(f'  - {e}')
    print()

    print('## 4. Consultar solo en las líneas de OTRA\n')
    print('Cada consulta lleva la transcripción entera hasta esa línea, con las dos voces. Si no se consulta en las líneas '
          'de PROTEGIDA, la salida en las de OTRA no cambia: el aviso pasa a la primera línea de OTRA que dispara.\n')
    filas_md = []
    for carpeta in ('c-json-corte', 'c-json-corte-rep'):
        f = filas[carpeta]
        todas = an.avisos(f, REGLA_C, VISTA)
        otra = {i: next((int(r['linea']) for r in validas(f, i) if r['hablante'] == 'OTRA' and dispara(r)), None)
                for i in VISTA}
        n_lin = sum(len(validas(f, i)) for i in VISTA)
        n_otra = sum(r['hablante'] == 'OTRA' for i in VISTA for r in validas(f, i))
        for nombre, av, n in (('todas las líneas', todas, n_lin), ('solo OTRA', otra, n_otra)):
            filas_md.append([carpeta, nombre, *an.fmt(an.metricas(av, VISTA)), f'{n} ({100 * n / n_lin:.0f} %)'])
        cambios = collections.Counter()
        for i in VISTA:
            if todas[i] != otra[i]:
                clase = 'estafa' if i in EST else 'legítima'
                cambios[f'{clase}: ' + ('se pierde' if otra[i] is None else f'se atrasa {otra[i] - todas[i]}')] += 1
        print(f'- {carpeta}: ' + '; '.join(f'{k} ×{v}' for k, v in sorted(cambios.items())))
    print()
    tabla(filas_md, ['corrida', 'consultas en', *an.ENC, 'consultas'])

    print('## 5. Aperturas\n')
    av = an.avisos(C, REGLA_C, VISTA)
    for clase, ids in (('Legítimas con FA', [i for i in LEG if av[i] is not None]),
                       ('Estafas avisadas', [i for i in EST if av[i] is not None])):
        temprano = [i for i in ids if av[i] <= 3]
        print(f'### {clase}: {len(temprano)} de {len(ids)} avisan en L1–L3\n')
        for i in temprano:
            v = validas(C, i)
            r0 = next((r for r in v if r['hablante'] == 'OTRA'), None)
            print(f"- {i} ({LOTE.get(i, 'corpus_v2')}), aviso en L{av[i]}, riesgo L1–L6 "
                  f"{' '.join(f'{num(r['riesgo']):g}' for r in v[:6])}: {recorte(r0['texto'], 150) if r0 else '—'}")
        print()
    print('Riesgo de C en la primera línea de OTRA, por familia (cantidad de llamadas por valor):\n')
    filas_md = []
    for clase, ids, familia in (('legítima', LEG, lambda i: i.split('-')[2] if i.startswith('ENT') else i.split('-')[1]),
                                ('estafa', EST, lambda i: i.split('-')[3])):
        fam = collections.defaultdict(list)
        for i in ids:
            r0 = next((r for r in validas(C, i) if r['hablante'] == 'OTRA'), None)
            if r0:
                fam[familia(i)].append(piso(num(r0['riesgo'])))
        for nombre, xs in sorted(fam.items()):
            cuenta = collections.Counter(xs)
            filas_md.append([clase, nombre, len(xs), *[cuenta.get(x, '') for x in (0.1, 0.2, 0.3)],
                             sum(n for x, n in cuenta.items() if x >= 0.4) or ''])
    tabla(filas_md, ['clase', 'familia', 'llamadas', '0,1', '0,2', '0,3', '0,4 o más'])

    print('## 6. Legítimas: FA según el pedido de datos y escenarios repetidos\n')
    v4 = an.avisos(filas['v4-corte'], REGLA_V4, LEG)

    def pide_datos(i):
        return any(e['evento'] == 'pedido' and 'REQUEST_PERSONAL_DATA' in e['etiquetas'] for e in REF[i].get('evidencia') or [])
    filas_md = []
    for nombre, ids in (('piden datos personales', [i for i in LEG if pide_datos(i)]),
                        ('no piden datos personales', [i for i in LEG if not pide_datos(i)])):
        filas_md.append([nombre, len(ids), sum(v4[i] is not None for i in ids), sum(av[i] is not None for i in ids)])
    tabla(filas_md, ['legítimas', 'llamadas', 'FA v4 (≥ 0,4 o alerta)', 'FA C (≥ 0,3 o alerta)'])
    print('Escenarios: las legítimas se agrupan por parecido de palabras (coseno de bolsa de palabras sin palabras vacías, '
          'enlace simple). Es una aproximación: el umbral no está calibrado con reescrituras declaradas, como en #45.\n')
    vacias = set('de la el en y a que te tu se lo los las un una por con para es no si me mi le del al ya sí o como pero '
                 'bueno hola buen día buenas tardes ok dale gracias vos usted su sus muy más'.split())
    bolsa = {i: collections.Counter(w for w in re.findall(r'[a-záéíóúñü0-9]+', ' '.join(
        l.texto for l in an.casos.con_roles(i, an.casos.cargar_texto(i))).lower()) if w not in vacias and len(w) > 2)
        for i in LEG}

    def coseno(a, b):
        return sum(a[w] * b[w] for w in a.keys() & b.keys()) / math.sqrt(
            sum(x * x for x in a.values()) * sum(x * x for x in b.values()))
    pares = sorted(((coseno(bolsa[a], bolsa[b]), a, b) for n, a in enumerate(LEG) for b in LEG[n + 1:]), reverse=True)
    filas_md, grupos_05 = [], None
    for umbral in (0.6, 0.5, 0.4):
        padre = {i: i for i in LEG}

        def raiz(x):
            while padre[x] != x:
                padre[x] = padre[padre[x]]
                x = padre[x]
            return x
        for s, a, b in pares:
            if s >= umbral:
                padre[raiz(a)] = raiz(b)
        grupos = collections.defaultdict(list)
        for i in LEG:
            grupos[raiz(i)].append(i)
        tam = collections.Counter(len(g) for g in grupos.values())
        filas_md.append([f'≥ {umbral:g}', len(grupos), ', '.join(f'{n}×{t}' for t, n in sorted(tam.items())),
                         sum(any(v4[i] is not None for i in g) for g in grupos.values()),
                         sum(any(av[i] is not None for i in g) for g in grupos.values())])
        if umbral == 0.5:
            grupos_05 = grupos
    tabla(filas_md, ['coseno', 'grupos', 'tamaños (cantidad × tamaño)', 'grupos con FA de v4', 'grupos con FA de C'])
    print('Grupos de más de una llamada con coseno ≥ 0,5 (* = FA de C):\n')
    for g in sorted(grupos_05.values(), key=lambda g: (-len(g), sorted(g))):
        if len(g) > 1:
            print('- ' + ', '.join(f"{i}{'*' if av[i] is not None else ''}" for i in sorted(g)))
    print()


if __name__ == '__main__':
    main()
