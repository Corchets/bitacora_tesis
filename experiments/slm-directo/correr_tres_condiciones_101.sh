#!/usr/bin/env bash
# #101: diez modelos × tres condiciones × veinte conversaciones = 600 recorridos.
# Uso: bash correr_tres_condiciones_101.sh TITO_NUEVO.json SELECCION.json [opciones matriz_101.py]
# Los modelos deben estar instalados en el servidor OLLAMA_URL.
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo 'Uso: bash experiments/slm-directo/correr_tres_condiciones_101.sh TITO_NUEVO.json SELECCION.json [--reanudar PREFIJO]' >&2
  echo 'Requiere el candidato y manifiesto congelados de #99/#100.' >&2
  exit 2
fi

# Resolver los argumentos antes de cambiar de directorio.
python_bin="${PYTHON:-python3}"
tito_nuevo="$($python_bin -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$1")"
seleccion="$($python_bin -c 'import pathlib,sys; print(pathlib.Path(sys.argv[1]).resolve())' "$2")"
shift 2
[[ -f "$tito_nuevo" ]] || { echo "Falta el candidato: $tito_nuevo" >&2; exit 2; }
[[ -f "$seleccion" ]] || { echo "Falta el manifiesto: $seleccion" >&2; exit 2; }

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

# Evitar que opciones adicionales cambien la matriz acordada.
for opcion in "$@"; do
  case "$opcion" in
    --modelos|--modelos=*|--casos|--casos=*|--tito-nuevo-modelo|--tito-nuevo-modelo=*|--tito-nuevo-manifest|--tito-nuevo-manifest=*)
      echo "Esta opción alteraría la matriz o el candidato: $opcion" >&2
      exit 2
      ;;
  esac
done

exec "$python_bin" -u matriz_101.py \
  --url "${OLLAMA_URL:-http://127.0.0.1:11434}" \
  --modelos 'qwen3.5:4b,qwen3.5:2b,gemma:2b,gemma3:270m,gemma3:1b,gemma3:4b,gemma3n:e2b,gemma3n:e4b,gemma4:e2b,gemma4:e4b' \
  --tito-nuevo-modelo "$tito_nuevo" \
  --tito-nuevo-manifest "$seleccion" \
  "$@"
