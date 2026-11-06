"""Tito como compuerta (2026-11-06): tablas del README, con controles de los números que cita.

Uso, desde esta carpeta:
    python revisar.py              # todas las tablas
    python revisar.py CASO [...]   # detalle línea por línea de esos casos
"""
import json
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict

from cargar import ACT, C, EXP, F, IDS, REF, TITO, TXT, activacion, estafa, linea_sensible, primer_aviso


def veredicto(aviso, act, sensible):
    """Por qué una falsa alarma del SLM solo no aparece con Tito."""
    if act is not None and act <= aviso:
        return 'no filtró'  # el SLM ya estaba despierto en esa línea: cambió su respuesta, no la compuerta
    if sensible is not None and sensible <= aviso:
        return 'punto ciego'  # la compuerta tapó una línea con algo sensible
    return 'filtrado honesto'


def falsas_alarmas_json():
    print('## 1. Falsas alarmas que desaparecen con Tito (lectura JSON)\n')
    unicas = {}
    for prompt in ('v1', 'v4'):
        solo, tito = F[f'{prompt} solo'], F[f'{prompt} + Tito']
        leg = [i for i in IDS if not estafa(i)]
        s = {i: primer_aviso(solo[i]) for i in leg}
        t = {i: primer_aviso(tito[i]) for i in leg}
        print(f'{prompt}: {sum(v is not None for v in s.values())} falsas alarmas solo, '
              f'{sum(v is not None for v in t.values())} con Tito')
        for i in leg:
            if s[i] and not t[i]:
                v = veredicto(s[i], ACT[i], linea_sensible(i))
                unicas[i] = v
                print(f'  saca  {i:34s} aviso solo L{s[i]:<3} Tito activa {ACT[i]}  1.ª sensible {linea_sensible(i)}  → {v}')
            if t[i] and not s[i]:
                print(f'  suma  {i:34s} aviso con Tito L{t[i]}')
    print(f'\nLegítimas distintas: {len(unicas)} → {dict(Counter(unicas.values()))}\n')
    return unicas


def cobertura():
    print('## 2. ¿Está despierto el SLM en la primera línea sensible? Y cuántas líneas no consulta\n')
    reglas = {i: next((int(r['linea']) for r in F['reglas v1'][i] if r['alerta_sugerida'] == 'true'), None) for i in IDS}
    compuertas = {
        'Tito viejo': ACT,
        'Tito viejo 2.0': {i: activacion(F['v4 + Tito 2.0'][i]) for i in IDS},
        'Reglas v1': reglas,
        'Tito o reglas v1': {i: min([x for x in (ACT[i], reglas[i]) if x], default=None) for i in IDS},
        'Tito sin punto ciego (oráculo)': {i: min([x for x in (ACT[i], linea_sensible(i)) if x], default=None) for i in IDS},
    }
    salida = {}
    for grupo, ids in (('150 casos', IDS), ('corpus_v2', [i for i in IDS if REF[i]['grupo'] == 'corpus_v2'])):
        print(f'{grupo}:')
        print('| Compuerta | Estafas | Legítimas | Líneas sin consultar | En legítimas |')
        print('|---|---:|---:|---:|---:|')
        for nombre, A in compuertas.items():
            fila = []
            for clase in (True, False):
                cs = [i for i in ids if estafa(i) == clase and linea_sensible(i)]
                fila.append((sum(1 for i in cs if A[i] and A[i] <= linea_sensible(i)), len(cs)))
            sin = lambda xs: sum(A[i] - 1 if A[i] else len(TXT[i]) for i in xs)
            tot = lambda xs: sum(len(TXT[i]) for i in xs)
            leg = [i for i in ids if not estafa(i)]
            print(f'| {nombre} | {fila[0][0]}/{fila[0][1]} | {fila[1][0]}/{fila[1][1]} | '
                  f'{sin(ids)}/{tot(ids)} ({sin(ids) / tot(ids):.0%}) | {sin(leg) / tot(leg):.0%} |')
            salida[grupo, nombre] = (fila[0], fila[1], sin(ids))
        print()
    return salida


def lineas_cortas():
    print('## 3. Puntaje de Tito en líneas de una o dos palabras (solo hasta su activación)\n')
    altas, n = [], 0
    for i in IDS:
        for l, p in TITO[i].items():
            texto = re.sub(r'^\s*[A-ZÁÉÍÓÚ]+\s*:\s*', '', TXT[i][l - 1]).strip()
            if len(texto.split()) <= 2:
                n += 1
                if p >= 0.5:
                    altas.append((p, i, texto))
    print(f'{n} líneas cortas puntuadas; {len(altas)} pasan de 0,5:')
    for p, i, texto in sorted(altas, reverse=True):
        print(f'  {p:.3f}  {i}  «{texto}»')
    print()
    return n, sorted(t for _, _, t in altas)


def banco():
    print('## 4. Banco con que se entrenó Tito (tag archivo/tito-banco)\n')
    crudo = subprocess.run(['git', 'show', 'archivo/tito-banco:experiments/laboratorio/entrenamiento_tito/ejemplos.jsonl'],
                           capture_output=True, text=True, check=True, cwd=EXP).stdout
    filas = [json.loads(l) for l in crudo.splitlines() if l.strip()]
    filas = [r for r in filas if r['uso'] == 'entrenamiento_desarrollo']
    patrones = {
        'clave, código, contraseña, PIN, token, CVV, DNI, documento o tarjeta':
            r'\b(clave|c[oó]digo|contrase[nñ]a|pin|token|cvv|dni|documento|tarjeta)\b',
        'la víctima cuenta lo que le pasó («me llamaron», «me llegó»…)':
            r'\b(me llamaron|me lleg[oó]|me pidieron|me dijeron|me ofrecieron|me escribieron)\b',
        'gracias': r'\bgracias\b',
    }
    res = {}
    for clase in ('estafa', 'legitima'):
        rs = [r for r in filas if r['etiqueta'] == clase]
        palabras = [len(r['texto'].split()) for r in rs]
        print(f'{clase}: {len(rs)} textos, de {min(palabras)} a {max(palabras)} palabras '
              f'(mediana {statistics.median(palabras):g})')
        for nombre, p in patrones.items():
            k = sum(bool(re.search(p, r['texto'].lower())) for r in rs)
            print(f'  {nombre}: {k}')
            res[clase, nombre] = k
        res[clase] = (len(rs), min(palabras))
    print()
    return res


def matriz_101():
    print('## 5. Matriz #101: de dónde sale la baja de falsas alarmas con Tito viejo en los 10 modelos\n')
    modelo, res, deriv, aviso = None, defaultdict(dict), {}, defaultdict(dict)
    for l in (C / '2026-10-30_112956_101_informe_101.md').read_text(encoding='utf-8').splitlines():
        if m := re.match(r'^## `(.+)`', l):
            modelo = m.group(1)
        # columnas: caso | clase | T_R/T_C | aviso directo | aviso viejo | aviso nuevo | derivación viejo/nuevo | ...
        elif m := re.match(r'^\| `(CV2-D-L-[^`]+)` \| legitima \| [^|]+ \| ([^|]+) \|[^|]*\|[^|]*\| ([^/|]+)/', l):
            v = m.group(2).strip()
            aviso[modelo].setdefault(m.group(1), int(v[1:]) if v.startswith('L') else None)
            d = m.group(3).strip()
            deriv[m.group(1)] = None if d == 'nunca' else int(d)
        elif m := re.match(r'^- `([^`]+)` \(legitima\): directo: ([^;]+); tito-nuevo: [^;]+; tito-viejo: (.+)\.$', l):
            res[modelo][m.group(1)] = (m.group(2).startswith('falsa'), m.group(3).startswith('falsa'))
    fa = Counter()
    clases = defaultdict(list)
    for mo in res:
        for c, (d, v) in res[mo].items():
            fa['directo'] += d
            fa['tito'] += v
            if d and not v:
                clases[veredicto(aviso[mo][c], deriv[c], linea_sensible(c))].append(f'{c} ({mo}, L{aviso[mo][c]})')
    print(f'{len(res)} modelos: {fa["directo"]} falsas alarmas en directo y {fa["tito"]} con Tito viejo')
    for k, v in clases.items():
        print(f'  {len(v):2d} {k}: {", ".join(sorted(v))}')
    print()
    return fa, {k: len(v) for k, v in clases.items()}


def detalle(casos):
    def celda(filas, l):
        r = next((r for r in filas if int(r['linea']) == l), None)
        if r is None:
            return '·'
        if r.get('consulta') == 'omitida':
            return 'om'
        return f"{r['riesgo']}{'!' if r['alerta_sugerida'].lower() == 'true' else ''}"
    for i in casos:
        ev = defaultdict(list)
        for e in REF[i].get('evidencia', []):
            ev[e['linea']].append(e['evento'])
        print(f"\n### {i} ({REF[i]['grupo']}, {REF[i]['clase']}) — Tito activa en {ACT[i]}")
        print('L | Tito | v1 solo | v1 + Tito | v4 solo | v4 + Tito | referencia | texto')
        for l, texto in enumerate(TXT[i], 1):
            t = TITO[i].get(l)
            cols = [celda(F[k][i], l) for k in ('v1 solo', 'v1 + Tito', 'v4 solo', 'v4 + Tito')]
            print(f"{'>>' if ACT[i] == l else '  '}{l} | {'—' if t is None else f'{t:.3f}'} | {' | '.join(cols)} | "
                  f"{','.join(ev.get(l, []))} | {texto}")


if __name__ == '__main__':
    if sys.argv[1:]:
        detalle(sys.argv[1:])
        sys.exit()
    # Controles: si cambian las corridas o las referencias, estos números del README dejan de valer.
    unicas = falsas_alarmas_json()
    assert len(unicas) == 7 and set(unicas.values()) == {'punto ciego'}
    cob = cobertura()
    assert cob['150 casos', 'Tito viejo'] == ((62, 64), (14, 43), 1139)
    assert cob['150 casos', 'Tito o reglas v1'][:2] == ((63, 64), (30, 43))
    assert cob['150 casos', 'Tito sin punto ciego (oráculo)'][2] == 900
    assert lineas_cortas() == (38, ['bien', 'corta', 'gracias'])
    b = banco()
    assert b['estafa'] == (2620, 18) and b['legitima'][0] == 2900
    assert b['estafa', 'la víctima cuenta lo que le pasó («me llamaron», «me llegó»…)'] == 0
    assert matriz_101() == (Counter(directo=48, tito=27), {'filtrado honesto': 13, 'punto ciego': 6, 'no filtró': 5})
    print('Controles OK: los números coinciden con el README.')
