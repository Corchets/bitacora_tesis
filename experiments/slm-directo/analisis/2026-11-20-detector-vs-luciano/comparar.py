"""#52: dónde avisó el detector de la evaluación final y dónde marcó Luciano en sus fichas de #145.

No corre modelos ni usa nada del test. Uso desde la raíz, con las corridas de desarrollo de la evaluación final (desde
el 2026-11-21 están en el árbol; antes había que sacarlas de la rama reserva/test con git archive):
    python3 -I experiments/slm-directo/analisis/2026-11-20-detector-vs-luciano/comparar.py \
        experiments/slm-directo/corridas/2026-11-12_evaluacion-final

Fichas: docs/corpus/REVISION-145-LUCIANO-2026-11-10.json y su correspondencia (26 llamadas de desarrollo). El aviso de
cada detector sale con la misma regla que analizar.py de la evaluación final.
"""

import hashlib, importlib.util, json, sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EXP = AQUI.parents[1]
CORPUS = EXP.parents[1] / 'docs/corpus'
EVAL = EXP / 'corridas/2026-11-12_evaluacion-final'

spec = importlib.util.spec_from_file_location('analizar_final', EVAL / 'analizar.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)


def entero(v):
    return int(v) if v not in (None, '') else None


def avisos_por_detector(datos):
    """{detector: {caso: (línea del aviso o None, motivo)}} de las tres carpetas de desarrollo."""
    salida = {}
    for carpeta in a.CARPETAS:
        filas, man = a.leer(datos / 'desarrollo' / carpeta)
        for nombre, prompt, regla in a.series(carpeta, a.CONFIG):
            por_caso = a.filas_de(filas, man, nombre, prompt)
            lineas = regla(por_caso, list(por_caso))
            salida[nombre] = {i: (l, next((r.get('motivo') or '' for r in por_caso[i] if int(r['linea']) == l), ''))
                              for i, l in lineas.items()}
    return salida


def main(argv=None):
    datos = Path((argv or sys.argv[1:])[0])
    fichas = json.loads((CORPUS / 'REVISION-145-LUCIANO-2026-11-10.json').read_text(encoding='utf-8'))['respuestas']
    mapa = json.loads((CORPUS / 'CORRESPONDENCIA-145-LUCIANO-2026-11-10.json').read_text(encoding='utf-8'))['casos']
    avisos = avisos_por_detector(datos)
    filas = []
    for alias in sorted(fichas):
        f, m = fichas[alias], mapa[alias]
        cid = m['case_id']
        texto = (EXP / 'casos/texto' / f'{cid}.txt').read_text(encoding='utf-8')
        if hashlib.sha256('\n'.join(texto.splitlines()).encode()).hexdigest() != m['texto_sha256']:
            raise ValueError(f'{alias}: el texto de {cid} cambió desde la ficha')
        ref = json.loads((EXP / 'casos/referencia' / f'{cid}.json').read_text(encoding='utf-8'))
        if cid not in avisos['config']:
            raise ValueError(f'{cid} no está en la corrida de desarrollo')
        filas.append({
            'alias': alias, 'case_id': cid, 'clase': ref['clase'], 'lineas': len(texto.splitlines()),
            't_r_ref': ref.get('t_r_linea'), 't_c_ref': ref.get('t_c_linea'),
            'estafa': f['estafa'], 'sospecha': f['sospecha'], 'sospecha_linea': entero(f['sospecha_linea']),
            'pedido': f['pedido'], 'pedido_linea': entero(f['pedido_linea']),
            'cumplimiento': f['cumplimiento'], 'cumplimiento_linea': entero(f['cumplimiento_linea']),
            'motivo_sospecha': f['motivo_sospecha'].strip(), 'fundamento': f['fundamento'].strip(),
            'ciega': 'aviso_previo' not in m,
            **{f'aviso_{n}': avisos[n][cid][0] for n in ('config', a.V4, 'reglas v1')},
            'motivo_config': avisos['config'][cid][1],
        })
    print(json.dumps(filas, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
