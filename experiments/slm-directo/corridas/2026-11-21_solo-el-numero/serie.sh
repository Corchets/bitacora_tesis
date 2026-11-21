#!/bin/sh
# Las corridas de esta carpeta, en orden, contra un llama-server 6c01da62 ya levantado en la Mac (127.0.0.1:18080):
#   llama-server -m gemma.gguf --host 127.0.0.1 --port 18080 -c 4096 -np 1 --no-webui -ngl 99
# Uso, desde esta carpeta: sh serie.sh s6   o   sh serie.sh d150
set -e
AQUI=$(cd "$(dirname "$0")" && pwd)
SV="llama-server -m gemma.gguf --host 127.0.0.1 --port 18080 -c 4096 -np 1 --no-webui -ngl 99 (Mac M4, Metal, 6c01da62)"
case "$1" in
  s6) C="$AQUI/../2026-11-11_a56-latencia-172/conversaciones-sub-6.json" ;;
  d150) C="$AQUI/conversaciones-desarrollo-150.json" ;;
  *) echo "s6 o d150"; exit 1 ;;
esac
cd "$AQUI/../.."
for v in "hoy-1 chat" "numero numero" "hoy-2 chat"; do
  set -- $1 $v
  python3 correr_android_latencia.py --conversaciones "$C" --salida "$AQUI/$1-$2" --prompt c-consejos-corte-riesgo \
    --consulta "$3" --prefijo salto --servidor "$SV" > "$AQUI/$1-$2.log"
  mv "$AQUI/$1-$2.log" "$AQUI/$1-$2/ejecucion.log"
done
