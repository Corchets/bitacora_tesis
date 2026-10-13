#!/usr/bin/env bash
# Prepara esta PC y corre la demo del ensayo #50 (macOS o Linux).
#
# Uso, desde la raíz del repositorio:
#   bash experiments/slm-directo/demo.sh                 demo con 8 conversaciones
#   bash experiments/slm-directo/demo.sh --completo      las 53 conversaciones
#   bash experiments/slm-directo/demo.sh --modelo qwen3.5:0.8b
#   bash experiments/slm-directo/demo.sh --si            no pregunta antes de instalar
#
# Instala lo que falte (Python 3.10+ y Ollama, preguntando antes), descarga el modelo,
# verifica el código, corre el detector mostrando cada línea y abre el visor.

set -euo pipefail

MODELO="qwen3.5:2b"
COMPLETO=0
SI=0
URL="http://localhost:11434"
CASOS_DEMO="SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01,SC-SOPORTE-CLAVE-01-e01,LG-SUPPORT-INFO-01-e01,TR-01-pedido-indirecto-digitos,TR-02-codigo-del-candado,TR-08-frase-cortada-candado,TR-12-corta-antes-del-pedido"

while [ $# -gt 0 ]; do
  case "$1" in
    --modelo) MODELO="${2:?Falta el nombre del modelo después de --modelo}"; shift 2 ;;
    --completo) COMPLETO=1; shift ;;
    --si) SI=1; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "Opción desconocida: $1 (usá --help)"; exit 2 ;;
  esac
done

cd "$(dirname "$0")"

paso() { printf '\n== %s\n' "$1"; }
# Última carpeta de corridas/ que termina en $1 (los nombres empiezan con fecha y hora).
ultima_corrida() {
  local ultima="" carpeta
  for carpeta in corridas/*"$1"; do
    [ -d "$carpeta" ] && ultima="$carpeta"
  done
  printf '%s' "$ultima"
}
preguntar() {
  [ "$SI" = 1 ] && return 0
  local respuesta
  read -r -p "$1 [S/n] " respuesta
  [[ -z "$respuesta" || "$respuesta" =~ ^[sSyY] ]]
}

paso "1/6 Python"
PY=""
for candidato in python3 python; do
  if command -v "$candidato" >/dev/null 2>&1 &&
     "$candidato" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
    PY="$candidato"
    break
  fi
done
if [ -z "$PY" ]; then
  echo "Falta Python 3.10 o posterior."
  if [ "$(uname)" = "Darwin" ] && command -v brew >/dev/null 2>&1 && preguntar "¿Lo instalo con Homebrew?"; then
    brew install python && PY=python3
  elif command -v apt-get >/dev/null 2>&1 && preguntar "¿Lo instalo con apt (pide tu contraseña)?"; then
    sudo apt-get update && sudo apt-get install -y python3 && PY=python3
  fi
  if [ -z "$PY" ]; then
    echo "Instalalo desde https://www.python.org/downloads/ y volvé a correr este script."
    exit 1
  fi
fi
echo "Uso $("$PY" --version)."

paso "2/6 Ollama"
if ! command -v ollama >/dev/null 2>&1; then
  echo "Falta Ollama, el programa que corre los modelos en tu PC."
  if [ "$(uname)" = "Darwin" ]; then
    if command -v brew >/dev/null 2>&1 && preguntar "¿Lo instalo con Homebrew?"; then
      brew install ollama
    else
      echo "Descargalo de https://ollama.com/download, abrilo una vez y volvé a correr este script."
      exit 1
    fi
  else
    preguntar "¿Lo instalo con el instalador oficial (https://ollama.com/install.sh)?" || exit 1
    curl -fsSL https://ollama.com/install.sh | sh
  fi
fi
echo "Uso $(ollama --version 2>/dev/null | tail -n 1)."

servidor_listo() {
  "$PY" - "$URL" <<'FIN' >/dev/null 2>&1
import sys, urllib.request
urllib.request.urlopen(sys.argv[1] + "/api/version", timeout=3)
FIN
}
if ! servidor_listo; then
  echo "Iniciando Ollama en segundo plano (registro en ${TMPDIR:-/tmp}/ollama-demo.log)..."
  nohup ollama serve >"${TMPDIR:-/tmp}/ollama-demo.log" 2>&1 &
  for _ in $(seq 1 30); do
    servidor_listo && break
    sleep 1
  done
  if ! servidor_listo; then
    echo "Ollama no respondió en $URL. Revisá ${TMPDIR:-/tmp}/ollama-demo.log o abrí la aplicación de Ollama."
    exit 1
  fi
fi

paso "3/6 Modelo $MODELO"
echo "La primera vez descarga el modelo (puede tardar varios minutos)."
ollama pull "$MODELO"

paso "4/6 Verificar el código (sin modelo)"
"$PY" -m unittest discover -s tests

paso "5/6 Correr el detector"
BASE="$(ultima_corrida linea-base-reglas)"
if [ -z "$BASE" ]; then
  "$PY" correr.py --solo-reglas --etiqueta linea-base-reglas >/dev/null
  BASE="$(ultima_corrida linea-base-reglas)"
fi
ETIQUETA="demo-${MODELO//[:\/]/-}"
if [ "$COMPLETO" = 1 ]; then
  echo "Corre las 53 conversaciones: puede tardar bastante según tu PC."
  "$PY" correr.py --modelos "$MODELO" --sin-reglas --detalle --etiqueta "$ETIQUETA"
else
  echo "Corre 8 conversaciones. Vas a ver cada línea y lo que respondió el modelo."
  "$PY" correr.py --modelos "$MODELO" --sin-reglas --casos "$CASOS_DEMO" --detalle --etiqueta "$ETIQUETA"
fi
CORRIDA="$(ultima_corrida "$ETIQUETA")"

paso "6/6 Resumen y visor"
"$PY" resumen.py "$CORRIDA" >/dev/null
"$PY" visor.py "$CORRIDA" "$BASE" --abrir
echo
echo "Listo."
echo "  Resumen: experiments/slm-directo/$CORRIDA/resumen.md"
echo "  Visor:   experiments/slm-directo/$CORRIDA/visor.html (si no se abrió solo, abrilo con el navegador)"
