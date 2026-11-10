"""#143, JSON de v4 cortado: diagnóstico fuera del criterio, escrito el 2026-11-07 después de ver los resultados.

No cambia el criterio ni su resultado: eso está en analizar.py, escrito antes de correr. Este script mira:
1. la latencia por línea en modo operativo, en las líneas anteriores al aviso;
2. la línea del aviso, según qué dispara la regla, y cuándo se sabe que hay que avisar;
3. los fallos de la segunda consulta;
4. dónde están las diferencias de riesgo escrito, con las dos corridas de la etapa 1 (v4-L y su repetición) como
   referencia de ruido.
Solo biblioteca estándar; no corre modelos ni lee la reserva. Uso, desde esta carpeta:
    python -I diagnostico.py
"""
import collections, importlib.util, statistics
from pathlib import Path

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('json_cortado', AQUI / 'analizar.py')
an = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(an)
num, p50_p95, tabla, casos = an.num, an.p50_p95, an.tabla, an.casos
ETAPA1 = AQUI.parent / '2026-11-06_puntaje-token-2'


def partes(filas, total):
    """ms de pared, lectura del prompt y escritura según Ollama, y el resto."""
    lectura = [num(r['runtime_prompt_eval_ns']) / 1e6 for r in filas]
    escritura = [num(r['runtime_eval_ns']) / 1e6 for r in filas]
    pared = [num(r[total]) for r in filas]
    return pared, lectura, escritura, [p - a - b for p, a, b in zip(pared, lectura, escritura)]


def coincidencia(a, b, claves):
    ks = [k for k in claves if a[k]['valida'] == 'true' and b[k]['valida'] == 'true']
    iguales = sum(num(a[k]['riesgo']) == num(b[k]['riesgo']) for k in ks)
    return f'{iguales / len(ks):.1%} ({iguales}/{len(ks)})'


def main():
    _, corte = an.cargar(AQUI, 'v4-corte')
    _, completo = an.cargar(AQUI, 'v4')
    _, lect = an.cargar(ETAPA1, 'v4-lectura')
    _, lect_rep = an.cargar(ETAPA1, 'v4-lectura-rep')
    aviso = an.avisos(corte, 'alerta_escrita')
    assert aviso == an.avisos(completo, 'alerta_sugerida'), 'la línea de aviso difiere entre las corridas'
    hasta = [k for k in sorted(corte) if aviso[k[0]] is None or k[1] <= aviso[k[0]]]
    antes = [k for k in hasta if aviso[k[0]] is None or k[1] < aviso[k[0]]]
    despues = [k for k in sorted(corte) if aviso[k[0]] is not None and k[1] > aviso[k[0]]]
    en_aviso = sorted((i, n) for i, n in aviso.items() if n is not None)

    print('# JSON de v4 cortado: diagnóstico fuera del criterio\n')
    print(f'La línea de aviso es la misma en las dos corridas en los {len(aviso)} casos; avisan {len(en_aviso)}. '
          f'Modo operativo: {len(hasta)} líneas hasta el aviso inclusive, {len(antes)} antes del aviso; '
          f'{len(despues)} líneas después del aviso (solo en modo diagnóstico).\n')

    print('## 1. Latencia por línea antes del aviso (ms de pared en T4, p50 / p95)\n')
    filas = []
    for nombre, datos, total in (('primera consulta (cortado)', corte, 'ms_etapa1'), ('JSON completo', completo, 'ms')):
        fs = [datos[k] for k in antes]
        pared, lectura, escritura, resto = partes(fs, total)
        tokens = [num(r['tokens_salida']) for r in fs]
        filas.append([nombre, len(fs), p50_p95(pared), p50_p95(tokens), p50_p95(lectura), p50_p95(escritura),
                      p50_p95(resto), f'{statistics.median(e / t for e, t in zip(escritura, tokens)):.1f}'])
    tabla(filas, ['consulta', 'líneas', 'ms', 'tokens escritos', 'lectura del prompt', 'escritura', 'resto',
                  'ms por token escrito (p50)'])

    print('## 2. La línea del aviso, según qué dispara la regla\n')
    print('La decisión de avisar se conoce al terminar la primera consulta; motivo y evidencia, al terminar la segunda. '
          'El JSON completo, sin streaming, da todo junto al final.\n')
    grupos = (('alerta escrita en true', [k for k in en_aviso if corte[k]['alerta_escrita'] == 'true']),
              ('solo riesgo ≥ 0,4 (alerta en false)', [k for k in en_aviso if corte[k]['alerta_escrita'] != 'true']),
              ('todas', en_aviso))
    filas = []
    for nombre, ks in grupos:
        filas.append([nombre, len(ks), p50_p95([num(corte[k]['ms_etapa1']) for k in ks]),
                      p50_p95([num(corte[k]['ms_etapa2']) for k in ks]), p50_p95([num(corte[k]['ms']) for k in ks]),
                      p50_p95([num(completo[k]['ms']) for k in ks]), p50_p95([num(completo[k]['tokens_salida']) for k in ks]),
                      f"{sum(completo[k]['motivo'] != '' for k in ks)}/{len(ks)}",
                      f"{sum(corte[k]['motivo'] != '' for k in ks)}/{len(ks)}"])
    tabla(filas, ['disparo', 'líneas', 'cortado: decisión (1.ª)', 'motivo (2.ª)', 'cortado: total', 'completo',
                  'tokens del completo', 'motivo en el completo', 'motivo en el cortado'])
    print(f"Segunda consulta: {p50_p95([num(corte[k]['tokens_salida_etapa2']) for k in en_aviso])} tokens escritos y "
          f"{p50_p95([num(corte[k]['tokens_prompt_etapa2']) for k in en_aviso])} de prompt, contra "
          f"{p50_p95([num(corte[k]['tokens_prompt']) for k in en_aviso])} de la primera. El CSV no guarda el desglose "
          f"de Ollama de la segunda consulta.\n")

    print('## 3. Fallos de la segunda consulta y evidencias fuera del texto\n')
    for k in en_aviso:
        r = corte[k]
        if r['error'] or r['evidencia_en_texto'] != 'true':
            ref = casos.cargar_referencia(k[0])
            print(f"- `{k[0]}` L{k[1]} ({ref['clase']}, {ref['grupo']}): riesgo {r['riesgo']}, alerta escrita "
                  f"{r['alerta_escrita']}, error `{r['error'] or '—'}`, evidencia en el texto {r['evidencia_en_texto'] or '—'}. "
                  f"Respuesta: `{' '.join(r['crudo_etapa2'].split())}`")
    print()

    print('## 4. Riesgo escrito igual, antes y después del aviso\n')
    print('«Hasta el aviso» incluye la línea del aviso; «después» son las líneas que solo corren en modo diagnóstico. '
          'La línea de aviso es la de esta corrida en los dos casos, también para las corridas de la etapa 1.\n')
    tabla([['v4-corte / v4 completo', 'misma sesión (hoy)', coincidencia(corte, completo, hasta), coincidencia(corte, completo, despues)],
           ['v4-L / su repetición', 'misma sesión (etapa 1)', coincidencia(lect, lect_rep, hasta), coincidencia(lect, lect_rep, despues)],
           ['v4-L / v4-corte', 'sesiones distintas', coincidencia(lect, corte, hasta), coincidencia(lect, corte, despues)],
           ['v4-L / v4 completo', 'sesiones distintas', coincidencia(lect, completo, hasta), coincidencia(lect, completo, despues)]],
          ['corridas', 'sesión', 'hasta el aviso', 'después del aviso'])
    dif = [(num(corte[k]['riesgo']), num(completo[k]['riesgo'])) for k in sorted(corte)
           if num(corte[k]['riesgo']) != num(completo[k]['riesgo'])]
    print(f"Riesgo distinto en {len(dif)} líneas: el cortado escribe más en {sum(a > b for a, b in dif)} y menos en "
          f"{sum(a < b for a, b in dif)}; {sum((a >= an.UMBRAL - 1e-9) != (b >= an.UMBRAL - 1e-9) for a, b in dif)} "
          f"cruzan 0,4. Pares más comunes (cortado, completo): {collections.Counter(dif).most_common(6)}.\n")


if __name__ == '__main__':
    main()
