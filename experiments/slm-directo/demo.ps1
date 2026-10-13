# Prepara esta PC y corre la demo del ensayo #50 (Windows).
#
# Uso, desde la raiz del repositorio, en PowerShell:
#   powershell -ExecutionPolicy Bypass -File experiments\slm-directo\demo.ps1
#   powershell -ExecutionPolicy Bypass -File experiments\slm-directo\demo.ps1 -Completo
#   powershell -ExecutionPolicy Bypass -File experiments\slm-directo\demo.ps1 -Modelo qwen3.5:0.8b
#   powershell -ExecutionPolicy Bypass -File experiments\slm-directo\demo.ps1 -Si
#
# Instala lo que falte (Python 3.10+ y Ollama con winget, preguntando antes), descarga
# el modelo, verifica el codigo, corre el detector mostrando cada linea y abre el visor.
# El archivo esta escrito sin tildes a proposito: Windows PowerShell 5.1 las lee mal.

param(
  [string]$Modelo = "qwen3.5:2b",
  [switch]$Completo,
  [switch]$Si
)

# "Continue" y no "Stop": en PowerShell 5.1, un programa que escribe en stderr
# (como ollama al descargar) cortaria el script. Los errores se revisan con $LASTEXITCODE.
$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
Set-Location -Path $PSScriptRoot
$env:PYTHONUTF8 = "1"
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$Url = "http://localhost:11434"
$CasosDemo = "SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01,SC-SOPORTE-CLAVE-01-e01,LG-SUPPORT-INFO-01-e01,TR-01-pedido-indirecto-digitos,TR-02-codigo-del-candado,TR-08-frase-cortada-candado,TR-12-corta-antes-del-pedido"
$script:PyExe = $null
$script:PyArgs = @()

function Paso([string]$Texto) { Write-Host ""; Write-Host "== $Texto" -ForegroundColor Cyan }

function Terminar([string]$Texto) {
  Write-Host $Texto -ForegroundColor Red
  exit 1
}

function Preguntar([string]$Texto) {
  if ($Si) { return $true }
  $respuesta = Read-Host "$Texto [S/n]"
  return ($respuesta -eq "" -or $respuesta -match "^[sSyY]")
}

function Refrescar-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

function Buscar-Python {
  $candidatos = @(
    @{ Exe = "py"; Args = @("-3") },
    @{ Exe = "python"; Args = @() },
    @{ Exe = "python3"; Args = @() }
  )
  foreach ($c in $candidatos) {
    # -CommandType Application: buscar solo programas instalados, nunca funciones de este script.
    $programa = Get-Command $c.Exe -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($programa) {
      # El "python" de Microsoft Store es un atajo que no ejecuta nada: devuelve un codigo distinto de 0.
      & $programa.Source @($c.Args) -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" 2>$null | Out-Null
      if ($LASTEXITCODE -eq 0) {
        $script:PyExe = $programa.Source
        $script:PyArgs = $c.Args
        return $true
      }
    }
  }
  return $false
}

function Ejecutar-Python {
  & $script:PyExe @($script:PyArgs) @args
  if ($LASTEXITCODE -ne 0) { Terminar "Fallo: python $($args -join ' ')" }
}

function Instalar-Con-Winget([string]$Id, [string]$Nombre, [string]$Pagina) {
  if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Terminar "No encuentro winget para instalar $Nombre. Instalalo desde $Pagina y volve a correr este script."
  }
  if (-not (Preguntar "Falta $Nombre. Lo instalo con winget?")) {
    Terminar "Instalalo desde $Pagina y volve a correr este script."
  }
  & winget install -e --id $Id --accept-source-agreements --accept-package-agreements
  Refrescar-Path
}

function Servidor-Listo {
  try {
    Invoke-RestMethod -Uri "$Url/api/version" -TimeoutSec 3 | Out-Null
    return $true
  } catch {
    return $false
  }
}

Paso "1/6 Python"
if (-not (Buscar-Python)) {
  Instalar-Con-Winget "Python.Python.3.12" "Python 3.12" "https://www.python.org/downloads/"
  if (-not (Buscar-Python)) {
    Terminar "Python quedo instalado pero esta ventana no lo ve. Cerra PowerShell, abri una nueva y volve a correr el script."
  }
}
$version = & $script:PyExe @($script:PyArgs) --version
Write-Host "Uso $version."

Paso "2/6 Ollama"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
  Instalar-Con-Winget "Ollama.Ollama" "Ollama" "https://ollama.com/download"
  $rutaHabitual = Join-Path $env:LOCALAPPDATA "Programs\Ollama"
  if (Test-Path (Join-Path $rutaHabitual "ollama.exe")) { $env:Path = "$rutaHabitual;$env:Path" }
  if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Terminar "Ollama quedo instalado pero esta ventana no lo ve. Cerra PowerShell, abri una nueva y volve a correr el script."
  }
}
if (-not (Servidor-Listo)) {
  Write-Host "Iniciando Ollama en segundo plano..."
  Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
  for ($i = 0; $i -lt 30; $i++) {
    if (Servidor-Listo) { break }
    Start-Sleep -Seconds 1
  }
  if (-not (Servidor-Listo)) {
    Terminar "Ollama no respondio en $Url. Abri la aplicacion de Ollama desde el menu Inicio y volve a correr el script."
  }
}
Write-Host "Ollama responde en $Url."

Paso "3/6 Modelo $Modelo"
Write-Host "La primera vez descarga el modelo (puede tardar varios minutos)."
& ollama pull $Modelo
if ($LASTEXITCODE -ne 0) { Terminar "No pude descargar $Modelo. Revisa el nombre en https://ollama.com/library y tu conexion." }

Paso "4/6 Verificar el codigo (sin modelo)"
Ejecutar-Python -m unittest discover -s tests

Paso "5/6 Correr el detector"
$base = Get-ChildItem -Path "corridas" -Directory -Filter "*linea-base-reglas" -ErrorAction SilentlyContinue | Sort-Object Name | Select-Object -Last 1
if (-not $base) {
  Ejecutar-Python correr.py --solo-reglas --etiqueta linea-base-reglas | Out-Null
  $base = Get-ChildItem -Path "corridas" -Directory -Filter "*linea-base-reglas" | Sort-Object Name | Select-Object -Last 1
}
$etiqueta = "demo-" + ($Modelo -replace "[:/\\]", "-")
if ($Completo) {
  Write-Host "Corre las 53 conversaciones: puede tardar bastante segun tu PC."
  Ejecutar-Python correr.py --modelos $Modelo --sin-reglas --detalle --etiqueta $etiqueta
} else {
  Write-Host "Corre 8 conversaciones. Vas a ver cada linea y lo que respondio el modelo."
  Ejecutar-Python correr.py --modelos $Modelo --sin-reglas --casos $CasosDemo --detalle --etiqueta $etiqueta
}
$corrida = Get-ChildItem -Path "corridas" -Directory -Filter "*$etiqueta" | Sort-Object Name | Select-Object -Last 1

Paso "6/6 Resumen y visor"
Ejecutar-Python resumen.py $corrida.FullName | Out-Null
Ejecutar-Python visor.py $corrida.FullName $base.FullName --abrir
Write-Host ""
Write-Host "Listo." -ForegroundColor Green
Write-Host "  Resumen: $(Join-Path $corrida.FullName 'resumen.md')"
Write-Host "  Visor:   $(Join-Path $corrida.FullName 'visor.html') (si no se abrio solo, abrilo con el navegador)"
