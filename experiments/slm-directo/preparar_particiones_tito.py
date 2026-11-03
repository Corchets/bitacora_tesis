"""Materializa la preparación delegada del 2026-10-29, sin entrenar ni leer reserva.

python experiments/slm-directo/preparar_particiones_tito.py --salida /tmp/particiones.json
Los IDs de evaluación se leen de la selección aprobada, no se sortean otra vez.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
SEED = 42


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def generar():
    fuente = BASE / 'SELECCION-TITO-2026-10-28.json'
    seleccion = json.loads(fuente.read_text())
    aprobada = BASE / 'PROPUESTA-20-CONVERSACIONES-TITO-2026-10-29.md'
    evaluacion = re.findall(r'\| \d+ \| \[(CV2-[^]]+)\]', aprobada.read_text())
    if len(evaluacion) != 20 or len(set(evaluacion)) != 20:
        raise ValueError('La selección aprobada debe contener exactamente 20 IDs únicos.')
    filas = [r for r in seleccion['conversaciones'] if r['seleccion'] != 'apartar']
    refs = {}
    textos = {}
    for r in filas:
        cid = r['case_id']
        if cid.startswith('CV2-T-'):
            raise ValueError('Reserva rechazada sin leerla.')
        for campo, subdir, ext in [('texto_sha256', 'texto', 'txt'),
                                   ('referencia_sha256', 'referencia', 'json')]:
            raw = (BASE / 'casos' / subdir / f'{cid}.{ext}').read_bytes()
            if sha(raw) != r[campo]:
                raise ValueError(f'{cid}: cambió {campo}; revisar antes de regenerar.')
            if ext == 'json':
                refs[cid] = json.loads(raw)
            else:
                textos[cid] = raw.decode()
    parent = {cid: cid for cid in refs}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        a, b = find(a), find(b)
        parent[max(a, b)] = min(a, b)
    indices = {}
    for cid, r in refs.items():
        # Escenario base y semilla comparten namespace para unir originales y variantes.
        claves = [('escenario', x) for x in [r.get('semilla'), r.get('escenario_base')] if x]
        claves.append(('texto', ' '.join(textos[cid].split()).casefold()))
        if cid.startswith('LAB-'):
            claves.append(('alias_lab', cid.removesuffix('-parafrasis')))
        for key in claves:
            if key in indices:
                union(cid, indices[key])
            indices[key] = cid
        if r.get('par') in refs:
            union(cid, r['par'])
    grupos = defaultdict(list)
    for cid in refs:
        grupos[find(cid)].append(cid)
    grupos = {g: sorted(ids) for g, ids in grupos.items()}
    grupo_por_id = {cid: g for g, ids in grupos.items() for cid in ids}
    retenidos = {grupo_por_id[cid] for cid in evaluacion}
    from datos_tito import REGRESION_OCHO
    regresiones = {grupo_por_id[cid] for cid in REGRESION_OCHO if cid in grupo_por_id}
    asignacion = {}
    for g in retenidos:
        for cid in grupos[g]:
            asignacion[cid] = 'comparacion_20' if cid in evaluacion else 'excluido_relacion_comparacion'
    for g in regresiones - retenidos:
        for cid in grupos[g]:
            asignacion[cid] = 'regresion'
    disponibles = set(grupos) - retenidos - regresiones
    # Diagnóstico: grupos CV2 no reservados para comparación ni regresión;
    # muestra pequeña, sin forzar 50/50 ni repartir un escenario para conseguirlo.
    diagnostico = []
    for g in sorted(disponibles, key=lambda g: (
            not any(refs[c]['clase'] == 'vishing' for c in grupos[g]),
            sha(f'{SEED}:diagnostico:{g}'.encode()))):
        if all(c.startswith('CV2-D-') for c in grupos[g]) and len(diagnostico) < 10:
            diagnostico += grupos[g]
            disponibles.remove(g)
            for cid in grupos[g]:
                asignacion[cid] = 'diagnostico'
    # 80/20 aproximado por grupos, estratificado según las clases presentes.
    estratos = defaultdict(list)
    for g in disponibles:
        clase = tuple(sorted({refs[c]['clase'] == 'vishing' for c in grupos[g]}))
        estratos[clase].append(g)
    for gs in estratos.values():
        gs.sort(key=lambda g: sha(f'{SEED}:conversacion:{g}'.encode()))
        nv = max(1, round(len(gs) * .2)) if len(gs) > 1 else 0
        for i, g in enumerate(gs):
            for cid in grupos[g]:
                asignacion[cid] = 'validacion' if i < nv else 'entrenamiento'
    conversaciones = [{**r, 'grupo_preparacion': grupo_por_id[r['case_id']],
                       'particion_preparacion': asignacion[r['case_id']]}
                      for r in filas]
    # Las variantes del banco nunca cruzan entrenamiento y validación.
    familias = defaultdict(list)
    for r in seleccion['banco']:
        if r['seleccion'] == 'conservar':
            familias[r['familia']].append(r)
    por_clase = defaultdict(list)
    for f, rs in familias.items():
        por_clase[rs[0]['clase_autoral']].append(f)
    banco_asignacion = {}
    for fs in por_clase.values():
        fs.sort(key=lambda f: sha(f'{SEED}:banco:{f}'.encode()))
        nv = max(1, round(len(fs) * .2))
        for i, f in enumerate(fs):
            banco_asignacion[f] = 'validacion' if i < nv else 'entrenamiento'
    banco = [{**r, 'particion_preparacion': banco_asignacion[r['familia']]}
             for r in seleccion['banco'] if r['seleccion'] == 'conservar']
    resumen = {}
    for nombre, rs, campo in [('conversaciones', conversaciones, 'clase_autoral'),
                              ('banco', banco, 'clase_autoral')]:
        resumen[nombre] = {p: dict(Counter(r[campo] for r in rs if r['particion_preparacion'] == p))
                           for p in sorted({r['particion_preparacion'] for r in rs})}
    # Invariantes ejecutables; no equivalen a una auditoría semántica humana.
    assert set(asignacion) == set(refs)
    assert {c for c,p in asignacion.items() if p == 'comparacion_20'} == set(evaluacion)
    assert Counter(refs[c]['clase'] for c in evaluacion) == {'vishing': 10, 'legitima': 10}
    for ids in grupos.values():
        partes = {asignacion[c] for c in ids}
        assert len(partes) == 1 or partes <= {'comparacion_20', 'excluido_relacion_comparacion'}
    for parte in ['entrenamiento', 'validacion']:
        assert {r['clase_autoral'] for r in banco if r['particion_preparacion'] == parte} == {'estafa', 'legitima'}
    return {'fecha': '2026-10-29', 'semilla': SEED,
            'estado': 'preparacion materializada; no entrenamiento ni evaluación ejecutados',
            'seleccion_sha256': sha(fuente.read_bytes()), 'script_sha256': sha(Path(__file__).read_bytes()),
            'evaluacion_ids': evaluacion, 'resumen': resumen,
            'limites': ['Sin reserva final ni cambios de pesos o revision_humana.',
                       'Sin supervisión binaria de prefijos creada: producirla y auditarla antes de entrenar.',
                       'Grupos de escenario/semilla/par/alias y duplicados exactos comprobados; relaciones semánticas entre fuentes banco/conversaciones requieren auditoría técnica antes de entrenar.',
                       'El banco fue visto por Tito viejo: su validación nueva no es independiente de ese artefacto.',
                       'No declara habilitada la puerta de datos_tito.py ni cierra D07/D08/D09.'],
            'conversaciones': conversaciones, 'banco': banco}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    args.salida.write_text(json.dumps(generar(), ensure_ascii=False, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
