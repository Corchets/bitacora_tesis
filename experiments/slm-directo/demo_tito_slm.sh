#!/usr/bin/env bash
# Demo Tito→SLM de punta a punta con modelos simulados (#69, parte de #68).
#
# Uso, desde la raíz del repositorio:
#   bash experiments/slm-directo/demo_tito_slm.sh
#
# Levanta el SLM falso, corre el par de WhatsApp en modo directo y filtrado
# (Tito simulado deriva en la línea 4) y escribe el resumen. No descarga ni
# entrena modelos; la corrida queda en corridas/*_demo-tito-slm-simulado/.
# Para regenerar el reporte de una corrida existente:
#   python experiments/slm-directo/resumen.py experiments/slm-directo/corridas/<carpeta>

set -euo pipefail

cd "$(dirname "$0")"

PUERTO="${PUERTO:-11439}"
python3 slm_falso.py --puerto "$PUERTO" & SERVIDOR=$!
trap 'kill $SERVIDOR 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$PUERTO/api/version', timeout=2)" 2>/dev/null; then
    break
  fi
  sleep 0.5
done

python3 correr.py --modelos falso-demo:1b --url "http://127.0.0.1:$PUERTO" \
  --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01 \
  --filtro-tito --tito-puntajes "4=0.9" \
  --etiqueta demo-tito-slm-simulado --detalle

CORRIDA="$(ls -dt corridas/*_demo-tito-slm-simulado | head -n 1)"
python3 resumen.py "$CORRIDA" --trayectorias >/dev/null
echo "Listo. Traza: $CORRIDA/actualizaciones.csv — Reporte: $CORRIDA/resumen.md"
