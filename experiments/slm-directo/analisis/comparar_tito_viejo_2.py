"""Reconstruye la comparación de desarrollo #140 desde las salidas originales."""
from __future__ import annotations

import collections
import csv
import io
import json
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ANTERIOR = RAIZ / 'corridas/2026-11-04_003715_e2b-tito-viejo-150'
NUEVA = RAIZ / 'corridas/2026-11-05_TITO-VIEJO-2-COLAB.zip'


def agrupar(filas, detector):
    salida = collections.defaultdict(list)
    for fila in filas:
        if fila['detector'] == detector:
            salida[fila['case_id']].append(fila)
    return salida


def aviso(filas):
    return next((int(f['linea']) for f in filas if f['aviso'].lower() == 'true'), None)


def main():
    anterior = json.loads((ANTERIOR / 'manifiesto.json').read_text(encoding='utf-8'))
    with (ANTERIOR / 'actualizaciones.csv').open(encoding='utf-8-sig', newline='') as f:
        vieja = agrupar(csv.DictReader(f), 'tito-slm')
    with zipfile.ZipFile(NUEVA) as z:
        archivo = next(n for n in z.namelist() if n.endswith('/manifiesto.json'))
        nueva = json.loads(z.read(archivo))
        archivo = next(n for n in z.namelist() if n.endswith('/actualizaciones.csv'))
        actual = agrupar(csv.DictReader(io.StringIO(z.read(archivo).decode('utf-8-sig'))), 'tito-viejo-2')
    if anterior['casos'] != nueva['casos'] or anterior['prompts'] != nueva['prompts']:
        raise ValueError('Las huellas de textos o prompts difieren.')
    if set(vieja) != set(actual) or set(actual) != set(nueva['casos']) or nueva['interrumpida']:
        raise ValueError('Los casos no coinciden o la corrida fue interrumpida.')
    refs = {k: json.loads((RAIZ / 'casos/referencia' / f'{k}.json').read_text(encoding='utf-8')) for k in actual}
    for nombre, datos in [('viejo', vieja), ('viejo 2.0', actual)]:
        print(nombre)
        for grupo in ('53 antecedentes', 'corpus_v2', 'total'):
            for clase in ('vishing', 'legitimas'):
                ids = [k for k in datos if (grupo == 'total' or (refs[k]['grupo'] == 'corpus_v2') == (grupo == 'corpus_v2'))
                       and (refs[k]['clase'] == 'vishing') == (clase == 'vishing')]
                print(f'  {grupo}, {clase}: {sum(aviso(datos[k]) is not None for k in ids)}/{len(ids)}')
        filas = [f for conjunto in datos.values() for f in conjunto]
        print('  respuestas inválidas:', sum(f['valida'].lower() != 'true' for f in filas))
        print('  consultas al SLM:', sum(f['consulta'].startswith('slm') for f in filas))
    print('Cambios de resultado (caso, clase, línea anterior, línea nueva, T_R, T_C):')
    for caso in sorted(actual):
        antes, despues = aviso(vieja[caso]), aviso(actual[caso])
        if (antes is None) != (despues is None):
            r = refs[caso]
            print(caso, r['clase'], antes, despues, r['t_r_linea'], r['t_c_linea'])


if __name__ == '__main__':
    main()
