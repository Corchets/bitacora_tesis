#!/usr/bin/env python3
"""Ejecuta los ocho controles de #99 sin supervisar datos ni entrenar.

Uso: python3 validar_ollama_pendiente_99.py --modelo TAG
Requiere Ollama iniciado y el modelo descargado. Solo usa biblioteca estándar.
Estos controles del supervisor no ejecutan la matriz comparativa de #101/#102.
"""

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

from cliente_ollama import ClienteOllama
import prompts_supervision_tito_99 as prompts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--modelo', required=True, choices=[
        'qwen3.5:4b', 'qwen3.5:2b', 'gemma:2b', 'gemma3:270m',
        'gemma3:1b', 'gemma3:4b', 'gemma3n:e2b', 'gemma3n:e4b',
        'gemma4:e2b', 'gemma4:e4b',
    ])
    parser.add_argument('--url', default=os.environ.get('OLLAMA_URL', 'http://127.0.0.1:11434'))
    parser.add_argument('--timeout', type=float, default=600)
    parser.add_argument('--salida', type=Path)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout debe ser positivo')
    aqui = Path(__file__).resolve().parent
    fuente = aqui / 'VALIDACION-PROMPTS-SUPERVISION-TITO-99-V4-THINK-4B-16K-2026-10-29.json'
    controles = json.loads(fuente.read_text(encoding='utf-8'))['controles']
    cliente = ClienteOllama(url=args.url, timeout_s=args.timeout)
    meta = prompts.info_modelo(cliente, args.modelo)
    if meta['digest'] == 'desconocido':
        parser.error(f'Modelo no instalado: {args.modelo}. Ejecutá ollama pull {args.modelo}')
    inicio = dt.datetime.now(dt.timezone.utc)
    salida = args.salida or aqui / f'VALIDACION-PENDIENTE-99-{inicio:%Y%m%dT%H%M%S%fZ}.json'
    if salida.exists():
        parser.error(f'La salida ya existe: {salida}; elegí otro nombre')

    def git(*argumentos):
        return subprocess.check_output(['git', *argumentos], cwd=aqui)

    informe = {
        'fecha': inicio.isoformat(), 'modelo': meta, 'url': args.url,
        'timeout_s': args.timeout, 'firma_prompts': prompts.firma_prompts(),
        'prompts_version': prompts.PROMPT_VERSION,
        'codigo_commit': git('rev-parse', 'HEAD').decode().strip(),
        'codigo_diff_sha256': hashlib.sha256(git('diff', 'HEAD', '--')).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'hardware': platform.platform(), 'semilla': prompts.SEMILLA,
        'fuente_controles': fuente.name,
        'fuente_controles_sha256': hashlib.sha256(fuente.read_bytes()).hexdigest(),
        'revision_humana': False, 'controles': [], 'conformidad': 0,
        'total': len(controles), 'completo': False,
        'nota': 'Validación técnica del anotador de desarrollo; no ejecuta supervisión, entrenamiento ni habilita D07/D08/D09.',
    }

    def guardar():
        salida.write_text(json.dumps(informe, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    guardar()
    print(f"Modelo: {args.modelo}; opciones: {meta['opciones']}; think={meta['think']}", flush=True)
    print(f'Resultados incrementales: {salida}', flush=True)
    for i, control in enumerate(controles, 1):
        print(f"[{i}/{len(controles)}] {control['control']} (dos pasadas)...", flush=True)
        t = time.monotonic()
        registro = prompts.revisar_prefijo(control['lineas'], cliente, args.modelo)
        conforme = prompts.control_conforme(registro, control['esperado'])
        informe['controles'].append({
            'control': control['control'], 'lineas': control['lineas'],
            'esperado': control['esperado'], 'observado': registro['etiqueta'],
            'conforme': conforme, 'segundos': round(time.monotonic() - t, 3),
            'registro': registro,
        })
        informe['conformidad'] += int(conforme)
        guardar()
        print(f"  {'OK' if conforme else 'FALLÓ'}: esperado={control['esperado']}, observado={registro['etiqueta']}", flush=True)
    informe['completo'] = True
    informe['segundos_total'] = sum(c['segundos'] for c in informe['controles'])
    guardar()
    print(f"Resultado: {informe['conformidad']}/{informe['total']}. Archivo: {salida}")
    return 0 if informe['conformidad'] == informe['total'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
