"""Aplica la revisión IA completa, sin entrenar ni habilitar experimentos.

python curar_datos_tito.py > SELECCION-TITO-2026-10-28.json
python curar_datos_tito.py --mostrar-banco 0 15
Las decisiones semánticas viven en CURACION-TITO-2026-10-28.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

from datos_tito import REGRESION_OCHO, rechazar_reserva
from entrenar_tito import (
    BANCO_BASE, BANCO_COMMIT, EJEMPLOS_SHA_DECLARADO, EXCLUSIONES_SHA_DECLARADA,
)

AQUI = Path(__file__).resolve().parent
REVISION = AQUI / 'CURACION-TITO-2026-10-28.json'

# Commit fijado cuyo código audita CURACION-TITO-2026-10-28.json.
# La revisión semántica solo aprueba este antecedente; no reetiquetarla
# como aprobación del código actual.
REVISION_CODIGO_COMMIT = '0a95968b7de9ed1a689cecb4a88a3e8e9f373f8e'

# Único subconjunto resoluble por commit comprobado: código versionado.
# Pesos, textos, referencias y revisiones previas no rastreadas siempre
# se verifican estrictamente en disco, también en modo histórico.
CODIGO_HISTORICO_RUTAS = frozenset({
    'datos_tito.py',
    'entrenar_tito.py',
    'tito_real.py',
    'filtro_tito.py',
})


def sha(crudo: bytes) -> str:
    return hashlib.sha256(crudo).hexdigest()


def canonico(dato) -> bytes:
    return json.dumps(dato, ensure_ascii=False, sort_keys=True).encode()


def objeto_git(nombre: str) -> bytes:
    return subprocess.check_output(
        ['git', 'show', f'{BANCO_COMMIT}:{BANCO_BASE}/{nombre}'], cwd=AQUI)


def codigo_git(commit: str, ruta: str) -> bytes:
    """Contenido versionado de un archivo de código en un commit comprobado.

    Falla cerrado si el origen no puede verificarse.
    """
    try:
        subprocess.check_output(
            ['git', 'cat-file', '-e', f'{commit}^{{commit}}'], cwd=AQUI,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise ValueError(f'Origen del código histórico no verificable: {commit}') from e
    try:
        return subprocess.check_output(
            ['git', 'show', f'{commit}:./{ruta}'], cwd=AQUI,
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise ValueError(
            f'Origen del código histórico no verificable: {commit}:{ruta}') from e


def indices_unicos(filas: list[dict], campo: str) -> dict:
    indice = {f[campo]: f for f in filas}
    if len(indice) != len(filas):
        raise ValueError(f'Identificadores repetidos: {campo}')
    return indice


def leer_banco() -> tuple[list[dict], list[dict], dict, dict]:
    manifiesto = json.loads(objeto_git('manifest.json'))
    huellas, familias, fuentes = {}, [], []
    for lote in ('banco', 'identidad', 'cotidiano'):
        for tipo, destino in (('familias', familias), ('fuentes', fuentes)):
            nombre = f'{tipo}_{lote}.json'
            crudo = objeto_git(nombre)
            if sha(crudo) != manifiesto['entrada_sha256'][nombre]:
                raise ValueError(f'Fuente histórica alterada: {nombre}')
            huellas[nombre] = sha(crudo)
            destino.extend(json.loads(crudo))
    crudo = objeto_git('ejemplos.jsonl')
    if sha(crudo) != EJEMPLOS_SHA_DECLARADO:
        raise ValueError('Banco distinto del usado por Tito.')
    huellas['ejemplos.jsonl'] = sha(crudo)
    filas = [json.loads(linea) for linea in crudo.splitlines()]
    crudo = objeto_git('exclusiones.json')
    if sha(crudo) != EXCLUSIONES_SHA_DECLARADA:
        raise ValueError('Exclusiones históricas alteradas.')
    huellas['exclusiones.json'] = sha(crudo)
    exclusiones = json.loads(crudo)
    fuentes_ids = {f['id'] for f in fuentes}
    if len(familias) != 300 or len(filas) != 6000:
        raise ValueError('Inventario histórico incompleto.')
    por_id = indices_unicos(filas, 'id')
    indices_unicos(familias, 'id')
    for f in familias:
        if len(f['textos']) != 20 or not set(f['fuentes']) <= fuentes_ids:
            raise ValueError(f'Familia incompleta o fuentes desconocidas: {f["id"]}')
        for i, texto in enumerate(f['textos'], 1):
            fila = por_id.get(f'{f["id"]}_{i:02d}')
            if (fila is None or fila['texto'] != texto
                    or fila['etiqueta'] != f['etiqueta'] or fila['familia'] != f['id']):
                raise ValueError(f'Exportación divergente: {f["id"]}, variante {i}')
    return familias, filas, exclusiones, huellas


def lectura_sin_perdida(f: dict) -> str:
    """Representa las veinte cadenas completas por composición, nunca muestrea."""
    textos = f['textos']
    filas = [textos[i:i + 4] for i in range(0, 20, 4)]
    prefijo = os.path.commonprefix(filas[1])
    prefijo = prefijo[:prefijo.rfind(' ') + 1]
    cierres = [t[len(prefijo):] for t in filas[1]]
    aperturas, excepciones = [], {}
    for i, fila in enumerate(filas):
        posibles = [t[:-len(cierres[j])] for j, t in enumerate(fila)
                    if cierres[j] and t.endswith(cierres[j])]
        apertura = Counter(posibles).most_common(1)[0][0] if posibles else ''
        aperturas.append(apertura)
        for j, t in enumerate(fila):
            if t != apertura + cierres[j]:
                excepciones[i * 4 + j + 1] = t
    salida = [f'{f["id"]} | {f["etiqueta"]} | tema autoral: {f["tema"]}']
    if len(excepciones) < 8:
        salida.append('Apertura i + cierre j, variante (i-1)*4+j; excepciones reemplazan cadena completa.')
        salida += [f'A{i}: {a}' for i, a in enumerate(aperturas, 1)]
        salida += [f'C{j}: {c}' for j, c in enumerate(cierres, 1)]
        salida += [f'EXCEPCION {n}: {t}' for n, t in excepciones.items()]
        reconstruidos = [excepciones.get(i * 4 + j + 1, aperturas[i] + cierres[j])
                         for i in range(5) for j in range(4)]
    else:
        piezas, combinaciones = [], []
        for t in textos:
            combinacion = []
            for parte in re.split(r'(?<=[.!?]) ', t):
                if parte not in piezas:
                    piezas.append(parte)
                combinacion.append(piezas.index(parte))
            combinaciones.append(combinacion)
        salida.append('Unir piezas con un espacio; se enumeran las veinte combinaciones.')
        salida += [f'P{i}: {p}' for i, p in enumerate(piezas, 1)]
        salida += [f'V{n}: '+','.join(str(i+1) for i in c)
                   for n, c in enumerate(combinaciones, 1)]
        reconstruidos = [' '.join(piezas[i] for i in c) for c in combinaciones]
    if reconstruidos != textos:
        raise ValueError(f'La lectura pierde información: {f["id"]}')
    return '\n'.join(salida)


def generar_seleccion(revision: dict | None = None,
                      codigo_historico: str | None = None) -> dict:
    """Reproduce la selección auditada.

    Por defecto (codigo_historico=None) verifica cada artefacto
    estrictamente en disco y rechaza cualquier deriva, incluido el
    hook `_puntuar` de #101 en filtro_tito.py.

    Con codigo_historico=REVISION_CODIGO_COMMIT resuelve solo el
    código versionado por `git show` del commit fijado, con sha
    verificado contra la revisión; pesos, textos, referencias y
    archivos no rastreados siguen verificándose en disco y la
    deriva del código actual se reporta sin presentarla como
    aprobada. Cualquier otro commit se rechaza: sin fallback
    silencioso ni hash ignorado.
    """
    revision = json.loads(REVISION.read_text(encoding='utf-8')) if revision is None else revision
    if codigo_historico is not None and codigo_historico != REVISION_CODIGO_COMMIT:
        raise ValueError(
            f'Commit de código histórico no autorizado: {codigo_historico}')
    if revision.get('habilitado') is not False or revision.get('banco_commit') != BANCO_COMMIT:
        raise ValueError('La curación IA no habilita uso ni cambia el banco histórico.')
    familias, filas, exclusiones, huellas = leer_banco()
    opiniones = indices_unicos(revision['familias_banco'], 'familia')
    if set(opiniones) != {f['id'] for f in familias}:
        raise ValueError('Faltan/sobran familias en la revisión semántica.')
    for f in familias:
        op = opiniones[f['id']]
        if sha(canonico(f)) != op['familia_sha256']:
            raise ValueError(f'Familia distinta de la leída: {f["id"]}')
        vs = op['variantes_apartadas']
        if (not isinstance(vs, list) or len(set(vs)) != len(vs)
                or any(type(i) is not int or not 1 <= i <= 20 for i in vs)):
            raise ValueError(f'Variantes excluidas inválidas: {f["id"]}')
        if not op['motivo'].strip() or op.get('revision_humana') is not False:
            raise ValueError('Juicio IA sin motivo o presentado como humano.')
        if f['id'] in exclusiones and set(vs) != set(range(1, 21)):
            raise ValueError(f'Reintroducción de exclusión histórica: {f["id"]}')
    banco = []
    for f in filas:
        n = int(f['id'].rsplit('_', 1)[1])
        banco.append({'id': f['id'], 'familia': f['familia'], 'clase_autoral': f['etiqueta'],
                      'texto_sha256': sha(f['texto'].encode()),
                      'seleccion': 'apartar' if n in opiniones[f['familia']]['variantes_apartadas'] else 'conservar',
                      'exclusion_historica': f['familia'] in exclusiones})
    # Rechazar por ID antes de abrir referencias de cualquier caso reservado.
    ids = sorted(p.stem for p in (AQUI / 'casos/texto').glob('*.txt'))
    ids_ref = sorted(p.stem for p in (AQUI / 'casos/referencia').glob('*.json'))
    rechazar_reserva(ids + ids_ref)
    opiniones_casos = indices_unicos(revision['conversaciones'], 'case_id')
    if set(ids) != set(ids_ref) or set(ids) != set(opiniones_casos):
        raise ValueError('Faltan/sobran conversaciones o referencias revisadas.')
    casos = []
    for cid in ids:
        op = opiniones_casos[cid]
        texto = (AQUI / 'casos/texto' / f'{cid}.txt').read_bytes()
        ref = (AQUI / 'casos/referencia' / f'{cid}.json').read_bytes()
        referencia = json.loads(ref)
        rechazar_reserva([cid], {cid: referencia.get('particion', 'desarrollo')})
        if sha(texto) != op['texto_sha256'] or sha(ref) != op['referencia_sha256']:
            raise ValueError(f'Cambió el caso revisado: {cid}')
        if op['seleccion'] not in ('conservar', 'conservar_con_observaciones', 'apartar'):
            raise ValueError(f'Selección desconocida: {cid}')
        if op.get('revision_humana') is not False or not op['motivo'].strip():
            raise ValueError(f'Revisión IA inválida: {cid}')
        lineas = texto.decode().splitlines()
        for soporte in op['soporte']:
            if lineas[soporte['linea'] - 1] != soporte['texto']:
                raise ValueError(f'Soporte ajeno al texto: {cid}')
        casos.append({'case_id': cid, 'seleccion': op['seleccion'],
                      'texto_sha256': sha(texto), 'referencia_sha256': sha(ref),
                      'clase_autoral': referencia['clase'],
                      'uso': ('regresion_historica' if referencia['grupo'] != 'corpus_v2'
                              else 'desarrollo_sin_independencia_acreditada'),
                      'ajustes_referencia_ia': op.get('ajustes_referencia_ia', {})})
    codigo_verificado: dict[str, str] = {}
    deriva_actual: dict[str, dict[str, str | None]] = {}
    for arte in revision['artefactos']:
        ruta = arte['ruta']
        if codigo_historico is not None and ruta in CODIGO_HISTORICO_RUTAS:
            crudo = codigo_git(codigo_historico, ruta)
            if sha(crudo) != arte['sha256']:
                raise ValueError(
                    f'Código histórico no coincide con la revisión: {ruta}')
            codigo_verificado[ruta] = arte['sha256']
            disco = AQUI / ruta
            actual = sha(disco.read_bytes()) if disco.is_file() else None
            if actual != arte['sha256']:
                deriva_actual[ruta] = {'auditado': arte['sha256'], 'actual': actual}
        elif sha((AQUI / ruta).read_bytes()) != arte['sha256']:
            raise ValueError(f'Artefacto cambiado: {ruta}')
    codigo_bloque = (None if codigo_historico is None else {
        'commit': codigo_historico,
        'alcance': ('solo código versionado por commit comprobado; '
                    'pesos, textos, referencias y archivos no rastreados '
                    'siempre verificados en disco'),
        'advertencia': ('la revisión aprueba el código de este commit, '
                        'no el código actual en disco'),
        'artefactos_codigo_sha256': codigo_verificado,
        'deriva_codigo_actual': deriva_actual})
    return {'fecha': revision['fecha'], 'habilitado': False,
            'tipo': 'seleccion IA de desarrollo, sin nuevos splits ni revisión humana',
            'banco_commit': BANCO_COMMIT, 'fuentes_historicas_sha256': huellas,
            'codigo_historico': codigo_bloque,
            'curacion_sha256': sha(canonico(revision)), 'script_sha256': sha(Path(__file__).read_bytes()),
            'resumen': {'banco_total': len(filas),
                        'banco_seleccion': dict(Counter(f['seleccion'] for f in banco)),
                        'banco_conservado_por_clase': dict(Counter(f['clase_autoral'] for f in banco if f['seleccion']=='conservar')),
                        'excluidas_previamente': sum(f['exclusion_historica'] for f in banco),
                        'familias_revisadas': len(familias),
                        'familias_lectura_sin_perdida_sha256': {f['id']: sha(lectura_sin_perdida(f).encode()) for f in familias},
                        'conversaciones_total': len(ids),
                        'conversaciones_seleccion': dict(Counter(c['seleccion'] for c in casos))},
            'banco': banco, 'conversaciones': casos,
            'regresiones_obligatorias_preservadas': list(REGRESION_OCHO), 'limites': revision['limites']}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mostrar-banco', nargs=2, type=int, metavar=('DESDE', 'HASTA'))
    p.add_argument('--listar-casos', choices=('conservar', 'apartar'))
    p.add_argument('--codigo-historico', metavar='COMMIT', default=None,
                   help=('Reproduce la curación con el código del commit '
                         'auditado; solo acepta el commit fijado.'))
    args = p.parse_args()
    if args.listar_casos:
        seleccion = generar_seleccion(codigo_historico=args.codigo_historico)
        revision = json.loads(REVISION.read_text(encoding='utf-8'))
        motivos = {r['case_id']: r['motivo'] for r in revision['conversaciones']}
        for caso in seleccion['conversaciones']:
            conservar = caso['seleccion'] != 'apartar'
            if conservar == (args.listar_casos == 'conservar'):
                print(f"{caso['case_id']}\t{caso['uso']}\t{motivos[caso['case_id']]}")
        return
    if args.mostrar_banco is not None:
        desde, hasta = args.mostrar_banco
        if not 0 <= desde < hasta <= 300:
            p.error('Rango debe cumplir 0 <= DESDE < HASTA <= 300.')
        familias, _, _, _ = leer_banco()
        for f in familias[desde:hasta]:
            print(lectura_sin_perdida(f), end='\n\n')
    else:
        print(json.dumps(generar_seleccion(codigo_historico=args.codigo_historico),
                         ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
