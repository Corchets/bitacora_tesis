#!/usr/bin/env bash
# Generador de audio sintético de humo para el par H1
# Ejecuta sintetizar_par.py utilizando el Python del entorno virtual o del sistema.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/../.."

PYTHON_BIN="python3"
if [ -f ".venv/bin/python3" ]; then
    PYTHON_BIN=".venv/bin/python3"
fi

"${PYTHON_BIN}" experiments/asr-local/sintetizar_par.py "$@"
