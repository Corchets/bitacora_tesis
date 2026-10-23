#!/usr/bin/env bash
# Prepara esta PC y corre la demo del ensayo #50 (macOS o Linux).
#
# Uso, desde la raíz del repositorio:
#   bash experiments/slm-directo/demo.sh                 demo con 8 conversaciones
#   bash experiments/slm-directo/demo.sh --completo      las 53 conversaciones
#   bash experiments/slm-directo/demo.sh --modelo qwen3.5:0.8b
#   bash experiments/slm-directo/demo.sh --si            no pregunta antes de instalar
#
# Instala lo que falte (Python 3.9+ y Ollama, preguntando antes), descarga el modelo,
# verifica el código, corre el detector mostrando cada línea y abre el visor.

set -euo pipefail

if [ "$(uname)" = "Darwin" ]; then
  MODELO="qwen3.5:2b-q8_0"
else
  MODELO="qwen3.5:2b"
fi
COMPLETO=0
SI=0
URL="http://127.0.0.1:11434"  # Ollama escucha en IPv4
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
buscar_python() {
  PY=""
  hash -r  # olvidar rutas viejas: después de instalar, python3 puede ser otro
  local candidato
  for candidato in python3 python; do
    if command -v "$candidato" >/dev/null 2>&1 &&
       "$candidato" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' 2>/dev/null; then
      PY="$candidato"
      return 0
    fi
  done
  return 1
}
if ! buscar_python; then
  echo "Falta Python 3.9 o posterior."
  if [ "$(uname)" = "Darwin" ] && command -v brew >/dev/null 2>&1 && preguntar "¿Lo instalo con Homebrew?"; then
    brew install python || true
  elif command -v apt-get >/dev/null 2>&1 && preguntar "¿Lo instalo con apt (pide tu contraseña)?"; then
    { sudo apt-get update && sudo apt-get install -y python3; } || true
  fi
  if ! buscar_python; then
    echo "No encuentro Python 3.9 o posterior. Instalalo desde https://www.python.org/downloads/,"
    echo "cerrá y abrí la terminal, y volvé a correr este script."
    exit 1
  fi
fi
echo "Uso $("$PY" --version)."

paso "2/6 Ollama"
OLLAMA=""
APP_OLLAMA=""
buscar_ollama() {
  if command -v ollama >/dev/null 2>&1; then
    OLLAMA="ollama"
  fi
  if [ "$(uname)" = "Darwin" ]; then
    local app
    for app in "/Applications/Ollama.app" "$HOME/Applications/Ollama.app"; do
      if [ -d "$app" ]; then
        APP_OLLAMA="$app"
        [ -z "$OLLAMA" ] && [ -x "$app/Contents/Resources/ollama" ] && OLLAMA="$app/Contents/Resources/ollama"
        break
      fi
    done
  fi
  [ -n "$OLLAMA" ]
}
if ! buscar_ollama; then
  echo "Falta Ollama, el programa que corre los modelos en tu PC."
  if [ "$(uname)" = "Darwin" ]; then
    # La app oficial trae todo compilado; la fórmula "ollama" de Homebrew puede compilar desde el código.
    if command -v brew >/dev/null 2>&1 && preguntar "¿Instalo la app de Ollama con Homebrew?"; then
      brew install --cask ollama-app || brew install --cask ollama || true
    fi
    if ! buscar_ollama; then
      echo "Descargá la app de https://ollama.com/download, arrastrala a Aplicaciones, abrila una vez"
      echo "y volvé a correr este script."
      exit 1
    fi
  else
    if ! command -v curl >/dev/null 2>&1; then
      if command -v apt-get >/dev/null 2>&1 && preguntar "Para instalar Ollama hace falta curl. ¿Lo instalo con apt (pide tu contraseña)?"; then
        sudo apt-get update && sudo apt-get install -y curl
      else
        echo "Falta curl: instalalo con el gestor de paquetes de tu sistema (en Ubuntu: sudo apt install curl)"
        echo "y volvé a correr este script."
        exit 1
      fi
    fi
    preguntar "¿Instalo Ollama con el instalador oficial (https://ollama.com/install.sh)?" || exit 1
    curl -fsSL https://ollama.com/install.sh | sh
    if ! buscar_ollama; then
      echo "Ollama no quedó instalado. Revisá los mensajes de arriba o seguí https://ollama.com/download/linux."
      exit 1
    fi
  fi
fi

servidor_listo() {
  "$PY" - "$URL" <<'FIN' >/dev/null 2>&1
import sys, urllib.request
abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))
abridor.open(sys.argv[1] + "/api/version", timeout=3)
FIN
}
version_ollama() {
  "$PY" - "$URL" <<'FIN' 2>/dev/null
import json, sys, urllib.request
abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))
print(json.load(abridor.open(sys.argv[1] + "/api/version", timeout=3)).get("version", "?"))
FIN
}
if ! servidor_listo; then
  if [ -n "$APP_OLLAMA" ]; then
    echo "Abriendo la app de Ollama..."
    open -a "$APP_OLLAMA"
  else
    echo "Iniciando Ollama en segundo plano (registro en ${TMPDIR:-/tmp}/ollama-demo.log)..."
    nohup "$OLLAMA" serve >"${TMPDIR:-/tmp}/ollama-demo.log" 2>&1 &
  fi
  for _ in $(seq 1 45); do
    servidor_listo && break
    sleep 1
  done
  if ! servidor_listo; then
    echo "Ollama no respondió en $URL. Abrí la aplicación de Ollama (o revisá ${TMPDIR:-/tmp}/ollama-demo.log)"
    echo "y volvé a correr este script."
    exit 1
  fi
fi
echo "Ollama $(version_ollama) responde en $URL."

paso "3/6 Modelo $MODELO"
echo "La primera vez descarga el modelo (puede tardar varios minutos)."
if ! "$OLLAMA" pull "$MODELO"; then
  echo "No pude descargar $MODELO. Revisá el nombre en https://ollama.com/library y tu conexión."
  exit 1
fi
if [ "$(uname)" = "Darwin" ]; then
  RUNNER=$("$PY" - "$URL" "$MODELO" <<'FIN' 2>/dev/null || true
import json, sys, urllib.request
abridor = urllib.request.build_opener(urllib.request.ProxyHandler({}))
req = urllib.request.Request(sys.argv[1] + "/api/show", data=json.dumps({"name": sys.argv[2]}).encode("utf-8"), headers={"Content-Type": "application/json"})
try:
    resp = json.load(abridor.open(req, timeout=3))
    print(resp.get("details", {}).get("runner", "") or "")
except Exception:
    pass
FIN
)
  if [ "$RUNNER" = "mlx" ]; then
    echo "Advertencia: $MODELO usa el runner MLX en macOS, que no soporta salida estructurada en este Ollama. Si falla, usá una variante GGUF (ej. $MODELO-q8_0)."
  fi
fi

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
