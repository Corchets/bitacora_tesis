#!/bin/bash
# Corridas pendientes en la MacBook M1 de 8 GB (#50), una por vez, cortando por memoria.
#
#   bash experiments/slm-directo/cola_m1.sh            # toda la cola
#   bash experiments/slm-directo/cola_m1.sh 2b 4b      # solo esas etapas
#   GRUPO=corpus_v2 bash experiments/slm-directo/cola_m1.sh 2b   # solo un grupo de casos
#
# Por defecto corre toda la partición de desarrollo (150 casos, 2773 líneas por config).
#
# Antes: cerrar Docker y las apps pesadas, y enchufar la Mac. No arranca si Docker está
# abierto, si está a batería (el 2026-10-21 hibernó al 1 % en plena corrida) o si el swap
# ya pasa del límite. Mientras corre, caffeinate evita que se duerma. Cada corrida se corta
# con SIGINT (lo procesado queda guardado y el manifiesto dice «interrumpida») si la
# memoria libre baja de MIN_LIBRE % (8) o el swap usado pasa de LIMITE_SWAP_MB (16384).
# El swap de macOS crece y no baja hasta reiniciar aunque sobre memoria (llegó a 12 GB con
# 23 % libre): por eso el corte principal es la memoria libre y el swap es el último límite.
#
# > Estado: propuesta sin discutir. Material de desarrollo; no elige modelo (D09).
set -u
LIMITE_SWAP_MB=${LIMITE_SWAP_MB:-16384}
MIN_LIBRE=${MIN_LIBRE:-8}
DIR="$(cd "$(dirname "$0")" && pwd)"
LOGS="${TMPDIR:-/tmp}/cola_m1"; mkdir -p "$LOGS"
GRUPO_ARGS=(); [ -n "${GRUPO:-}" ] && GRUPO_ARGS=(--grupo "$GRUPO")

swap() { sysctl -n vm.swapusage | sed -E 's/.*used = ([0-9.]+)M.*/\1/' | cut -d. -f1; }
libre() { memory_pressure | tail -1 | sed -E 's/.*: ([0-9]+)%/\1/'; }

if pgrep -q -f "Docker.app/Contents/MacOS/com.docker.virtualization"; then
  echo "Docker está abierto: cerralo antes de correr la cola."; exit 1
fi
if ! pmset -g batt | grep -q "AC Power"; then
  echo "La Mac está a batería: enchufala antes de correr la cola."; exit 1
fi
caffeinate -is -w $$ &
if [ "$(swap)" -gt "$LIMITE_SWAP_MB" ]; then
  echo "El swap ya está en $(swap) MB (límite $LIMITE_SWAP_MB). Reiniciá o subí LIMITE_SWAP_MB."; exit 1
fi

vigilada() {  # vigilada <nombre> <args de correr.py...>
  local nombre=$1; shift
  local log="$LOGS/$(date +%Y-%m-%d_%H%M%S)_$nombre.log"
  echo "== $nombre  (log: $log)"
  echo "inicio $(date +%T) swap $(swap) MB libre $(libre)%" > "$log"
  (cd "$DIR" && exec python3 -u correr.py "$@" ${GRUPO_ARGS[@]+"${GRUPO_ARGS[@]}"}) >> "$log" 2>&1 &
  local pid=$! max=0 s l
  while kill -0 "$pid" 2>/dev/null; do
    s=$(swap); l=$(libre); [ "$s" -gt "$max" ] && max=$s
    if [ "$s" -gt "$LIMITE_SWAP_MB" ] || [ "$l" -lt "$MIN_LIBRE" ]; then
      echo "CORTE $(date +%T): swap $s MB, libre $l%" | tee -a "$log"
      kill -INT "$pid"; wait "$pid"; echo "fin swap_max $max MB" >> "$log"; return 1
    fi
    sleep 5
  done
  wait "$pid"; local rc=$?
  echo "fin $(date +%T) rc $rc swap_max $max MB" | tee -a "$log"
  return $rc
}

etapas=${*:-"2b 0.8b 4b 9b"}
for e in $etapas; do
  case $e in
    # Lo central: ¿el v2 corrige al 2B? Los 97 casos de corpus_v2 son su primera prueba honesta.
    2b) vigilada 2b-v1v2 --modelos qwen3.5:2b-q8_0 --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta m1-2b-v1v2-nb32 ;;
    # v1 y v2 completos (la corrida 2026-10-21_182201 tenía 53 casos y el v2 se cortó en 120 líneas).
    0.8b) vigilada 0.8b-v1v2 --modelos qwen3.5:0.8b-q8_0 --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta m1-0.8b-v1v2-nb32 ;;
    # 4B completo: en 2026-10-17 quedó en 42/53 por memoria.
    4b) vigilada 4b-v1v2 --modelos qwen3.5:4b-q4_K_M --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta m1-4b-v1v2-nb32 ;;
    # Techo local: primero el piloto escrito; si entra en memoria, todos los casos.
    9b) vigilada 9b-piloto --modelos qwen3.5:9b-q4_K_M --prompts tarea,v2 --num-batch 32 --sin-reglas --grupo piloto_escrito --timeout 300 --etiqueta m1-9b-piloto-nb32 \
          && vigilada 9b-todo --modelos qwen3.5:9b-q4_K_M --prompts v2 --num-batch 32 --sin-reglas --timeout 300 --etiqueta m1-9b-v2-nb32 ;;
    *) echo "Etapa desconocida: $e (opciones: 2b 0.8b 4b 9b)"; exit 1 ;;
  esac || { echo "La etapa $e se cortó o falló; frena la cola."; exit 1; }
done
ollama stop qwen3.5:9b-q4_K_M >/dev/null 2>&1
echo "Cola terminada. Resumen de cada corrida: python3 resumen.py corridas/<carpeta>"
