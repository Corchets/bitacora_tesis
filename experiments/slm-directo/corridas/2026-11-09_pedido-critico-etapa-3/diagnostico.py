"""#143, segunda vuelta, etapa 3: diagnóstico fuera de la regla, escrito el 2026-11-09 después de ver los resultados.

No cambia la regla ni su resultado: eso está en analizar.py, escrito antes de correr. Lo que sale de acá son hipótesis;
una regla nueva se escribe antes y se prueba en otros casos (ADR 0005).
1. Qué valores escribe el modelo en el riesgo, y con qué valor dispara el primer aviso.
2. Los pares discordantes de la regla, con McNemar exacto.
3. Los avisos a tiempo que pierde C con campo: el riesgo de cada versión en la línea del pedido.
4. La alerta fuerte en las legítimas: la línea que dispara y el motivo.
5. Los 22 motivos de C con campo, para leerlos a mano.
Solo biblioteca estándar; no corre modelos ni lee la reserva. Uso, desde esta carpeta:
    python -I diagnostico.py
"""
import collections, importlib.util, json, math
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('analizar_etapa3', AQUI / 'analizar.py')
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
REF, num, tabla = an.REF, an.num, an.tabla


def mcnemar(solo_a, solo_b):
    """p de McNemar exacto (binomial, dos colas) con los pares discordantes."""
    n, k = solo_a + solo_b, min(solo_a, solo_b)
    if not n:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, j) for j in range(k + 1)) / 2 ** n)


def corta(texto, n=110):
    texto = ' '.join(texto.split())
    return texto if len(texto) <= n else texto[:n - 1] + '…'


def motivo_de(r):
    try:
        d = json.loads(r.get('crudo_etapa2') or '')
        return d.get('evidencia', ''), d.get('motivo', '')
    except (ValueError, AttributeError):
        return '', ''


def main():
    e2 = {c: an.leer(an.ETAPA_2, c)[0] for c in ('c-json-corte', 'c-json-corte-rep')}
    d = {c: an.leer(AQUI, c)[0] for c in ('c-sin-alerta', 'c-con-campo', 'c-sin-alerta-rep', 'c-con-campo-rep')}
    series = {'base: C de la etapa 2, cortado tras el riesgo': (e2['c-json-corte'], False),
              'C sin alerta': (d['c-sin-alerta'], False), 'C con campo': (d['c-con-campo'], True)}
    print('# #143, etapa 3: diagnóstico fuera de la regla (escrito después de ver los resultados)\n')

    print('## 1. El riesgo escrito y el valor que dispara el primer aviso\n')
    print('Dentro del alcance, todas las líneas. «0,3 exacto»: el primer aviso de la llamada sale de un riesgo de 0,3, '
          'el escalón de la regla.\n')
    filas = []
    for nombre, (f, campo) in series.items():
        for grupo, ids in (('estafas', an.ESTAFAS), ('legítimas', an.LEGITIMAS)):
            valores, disparo = collections.Counter(), collections.Counter()
            for i in ids:
                validas = [r for r in f[i] if r['valida'] == 'true']
                valores.update(round(num(r['riesgo']), 2) for r in validas)
                for r in validas:
                    x, pc = num(r['riesgo']), campo and r.get('pedido_critico') == 'true'
                    if x >= an.UMBRAL - 1e-9 or pc:
                        disparo['0,3 exacto' if abs(x - 0.3) < 1e-9 else ('solo pedido_critico' if x < 0.3 else '> 0,3')] += 1
                        break
            tot = sum(valores.values())
            reparto = ', '.join(f'{k:g}: {100 * v / tot:.0f} %' for k, v in sorted(valores.items()) if v / tot >= 0.01)
            filas.append([nombre, grupo, reparto, disparo['0,3 exacto'], disparo['> 0,3'], disparo['solo pedido_critico'],
                          sum(disparo.values())])
    tabla(filas, ['serie', 'llamadas', 'valores del riesgo (≥ 1 % de las líneas)', 'avisos con 0,3 exacto',
                  'avisos con > 0,3', 'solo por pedido_critico', 'avisos'])

    print('## 2. Pares discordantes de la regla, con McNemar exacto\n')
    filas = []
    for etiqueta, base, campo in (('corrida', e2['c-json-corte'], d['c-con-campo']),
                                  ('repetición', e2['c-json-corte-rep'], d['c-con-campo-rep'])):
        ab, ac = an.avisos(base, an.VISTA, campo=False), an.avisos(campo, an.VISTA)
        conp = [i for i in an.ESTAFAS if REF[i].get('t_r_linea')]
        a_tiempo = lambda av, i: av[i] is not None and av[i] <= REF[i]['t_r_linea']  # noqa: E731
        pares = {
            'estafas avisadas': ([i for i in an.ESTAFAS if ab[i] is not None and ac[i] is None],
                                 [i for i in an.ESTAFAS if ac[i] is not None and ab[i] is None]),
            'avisos a tiempo': ([i for i in conp if a_tiempo(ab, i) and not a_tiempo(ac, i)],
                                [i for i in conp if a_tiempo(ac, i) and not a_tiempo(ab, i)]),
            'FA': ([i for i in an.LEGITIMAS if ab[i] is not None and ac[i] is None],
                   [i for i in an.LEGITIMAS if ac[i] is not None and ab[i] is None]),
        }
        for cifra, (a, c) in pares.items():
            filas.append([etiqueta, cifra, len(a), len(c), f'{mcnemar(len(a), len(c)):.3f}'])
    tabla(filas, ['corrida', 'cifra', 'solo la base', 'solo C con campo', 'p (McNemar exacto)'])

    print('## 3. Los avisos a tiempo que pierde C con campo\n')
    print('Riesgo en la línea del pedido de la referencia (y la línea en que cada versión avisa). «pc»: primera línea con '
          '`pedido_critico` en true.\n')
    base, campo = e2['c-json-corte'], d['c-con-campo']
    ab, ac = an.avisos(base, an.VISTA, campo=False), an.avisos(campo, an.VISTA)
    filas = []
    for i in an.ESTAFAS:
        t = REF[i].get('t_r_linea')
        if not t or not (ab[i] is not None and ab[i] <= t) or (ac[i] is not None and ac[i] <= t):
            continue
        rb = {int(r['linea']): r for r in base[i]}
        rc = {int(r['linea']): r for r in campo[i]}
        pc = next((int(r['linea']) for r in campo[i] if r.get('pedido_critico') == 'true'), None)
        filas.append([i, t, corta(rc[t]['texto'], 90), f"{rb[t]['riesgo']} (aviso L{ab[i]})",
                      f"{rc[t]['riesgo']} (aviso {'L' + str(ac[i]) if ac[i] else '—'})", f'L{pc}' if pc else '—'])
    tabla(filas, ['caso', 'línea del pedido', 'texto de esa línea', 'base', 'C con campo', 'pc'])

    print('## 4. La alerta fuerte en las legítimas\n')
    filas = []
    for i in an.LEGITIMAS:
        r = next((r for r in campo[i] if r.get('pedido_critico') == 'true'), None)
        if r is None:
            continue
        ev, mot = motivo_de(r)
        filas.append([i, f"L{r['linea']} {r['hablante']}", corta(r['texto']), corta(ev, 80), corta(mot, 110)])
    tabla(filas, ['caso', 'línea', 'texto', 'evidencia', 'motivo'])

    print('## 5. Los motivos de C con campo, dentro del alcance\n')
    print('«Pedido crítico de la referencia»: la primera línea con código, clave, plata, acceso remoto o acción de '
          'seguridad (sin datos personales); «pedido»: el primero de cualquier tipo.\n')
    filas = []
    for i in an.VISTA:
        for r in campo[i]:
            if not r.get('crudo_etapa2'):
                continue
            ev, mot = motivo_de(r)
            filas.append([i, REF[i]['clase'], f"L{r['linea']}", REF[i].get('t_r_linea') or '—',
                          an.linea_critica(i) or '—', corta(ev, 80), corta(mot, 120)])
    tabla(filas, ['caso', 'clase', 'línea', 'pedido', 'pedido crítico', 'evidencia', 'motivo'])


if __name__ == '__main__':
    main()
