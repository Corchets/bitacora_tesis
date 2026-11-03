#!/usr/bin/env bash
# Regeneración del consolidado Tito→SLM (#74, parte de #68).
#
# Re-genera los seis `comparacion.md` desde las salidas crudas con
# `comparar.py` (sin nueva inferencia), re-ejecuta `consolidar.py` y
# verifica que los artefactos queden idénticos (byte a byte).
#
# Uso, desde la raíz del repositorio:
#   bash experiments/slm-directo/analisis/2026-10-26-tito-slm-consolidado/regenerar.sh
#
# Requisitos para repetir el experimento real (con inferencia): Ollama
# 0.40.8 con los seis tags de la matriz, Tito (`tito_logreg.json`) y:
#   python correr.py --modelos <tag> --url http://127.0.0.1:11435 \
#     --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata \
#     --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta <nombre> --detalle
# Después: `python resumen.py corridas/<carpeta>` y `python comparar.py corridas/<carpeta>`.
set -euo pipefail

AQUI="$(cd "$(dirname "$0")" && pwd)"
SLM="$(cd "$AQUI/../.." && pwd)"
cd "$SLM"

CORRIDAS=(
  2026-10-26_133838_qwen4b-comparacion
  2026-10-26_135518_qwen08b-q8-comparacion
  2026-10-26_135640_qwen08b-comparacion
  2026-10-26_135746_qwen2b-q8-comparacion
  2026-10-26_135930_qwen9b-comparacion
  2026-10-26_141023_llama1b-comparacion
)

ANTES="$(mktemp)"
for c in "${CORRIDAS[@]}"; do
  sha256sum "corridas/$c/comparacion.md" >> "$ANTES"
done
sha256sum "$AQUI/cobertura.json" "$AQUI/TABLAS.md" >> "$ANTES"

for c in "${CORRIDAS[@]}"; do
  python3 comparar.py "corridas/$c" >/dev/null
  echo "OK comparar: $c"
done

python3 "$AQUI/consolidar.py"

DESPUES="$(mktemp)"
for c in "${CORRIDAS[@]}"; do
  sha256sum "corridas/$c/comparacion.md" >> "$DESPUES"
done
sha256sum "$AQUI/cobertura.json" "$AQUI/TABLAS.md" >> "$DESPUES"

if diff -q "$ANTES" "$DESPUES" >/dev/null; then
  echo "OK regenerar: todo idéntico byte a byte, sin nueva inferencia"
else
  echo "DIFIERE: la regeneración cambió salidas; revisar antes de informar"
  diff "$ANTES" "$DESPUES" || true
  exit 1
fi
rm -f "$ANTES" "$DESPUES"
