"""Lo que un script de Colab necesita antes de correr modelos, y que conviene que no falle a mitad de camino:

- ubicar las legítimas reales que se subieron a la sesión, sea la carpeta `sets/` o un ZIP que la traiga, y dejar una
  copia limpia (sin `.DS_Store`, `__MACOSX` ni archivos `._*`, que rompen el control contra el manifiesto);
- tener `zstd`, que el instalador de Ollama usa para descomprimir: si ya está no se toca; si no, `apt-get` con
  reintentos; y si `apt-get` no puede, un reemplazo mínimo en Python;
- instalar Ollama en una versión fija y bajar el modelo, con reintentos;
- descargar un ZIP sin que un problema del navegador corte la corrida.

Solo biblioteca estándar. Lo usa colab/probar_exploracion_reales.py; las funciones reciben `correr` y `which` para
poder probarlas sin Colab (tests/test_preparar_colab.py).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

SUBCARPETAS = ("set-legitimas", "set-zona-gris")
# Carpetas de /content que no son una subida del usuario, y basura que dejan macOS y los ZIP armados en una Mac.
NO_MIRAR = {"bitacora_tesis", "reserva-test", "sample_data", "drive", "__MACOSX", "__pycache__"}
ZIPS_PROPIOS = ("parcial-", "resultados-")
PROFUNDIDAD = 4

REEMPLAZO_ZSTD = '''#!/usr/bin/env python3
# Reemplazo mínimo de `zstd` para descomprimir (lo dejó colab/preparar_colab.py porque apt-get no pudo instalarlo).
import sys
import zstandard
args = [a for a in sys.argv[1:] if not a.startswith("-")]
banderas = "".join(a.lstrip("-") for a in sys.argv[1:] if a.startswith("-") and not a.startswith("--"))
if "--version" in sys.argv[1:] or "V" in banderas:
    print("zstd (reemplazo en Python, solo descomprime)")
    sys.exit(0)
descompresor = zstandard.ZstdDecompressor()
if not args:
    descompresor.copy_stream(sys.stdin.buffer, sys.stdout.buffer)
else:
    for ruta in args:
        with open(ruta, "rb") as entrada:
            if "c" in banderas:
                descompresor.copy_stream(entrada, sys.stdout.buffer)
            else:
                with open(ruta[:-4] if ruta.endswith(".zst") else ruta + ".out", "wb") as salida:
                    descompresor.copy_stream(entrada, salida)
'''


# --- Legítimas reales ---
def es_sets(carpeta: Path) -> bool:
    """True si `carpeta` trae los dos sets, cada uno con sus textos."""
    return all((carpeta / sub / "texto").is_dir() for sub in SUBCARPETAS)


def _carpetas_con_sets(raiz: Path, omitir: set[Path]) -> list[Path]:
    """Las carpetas bajo `raiz` (hasta PROFUNDIDAD niveles) que traen los dos sets, de la menos profunda a la más."""
    encontradas, nivel = [], [raiz]
    for _ in range(PROFUNDIDAD + 1):
        siguiente = []
        for carpeta in nivel:
            if es_sets(carpeta):
                encontradas.append(carpeta)
                continue
            try:
                hijas = sorted(p for p in carpeta.iterdir() if p.is_dir() and not p.is_symlink())
            except OSError:
                continue
            siguiente += [p for p in hijas if p.name not in NO_MIRAR and not p.name.startswith(".")
                          and not p.name.startswith(ZIPS_PROPIOS) and p.resolve() not in omitir]
        nivel = siguiente
    return encontradas


def _zips_con_sets(raiz: Path) -> list[Path]:
    """Los ZIP bajo `raiz` (hasta dos niveles) que traen los dos sets adentro."""
    candidatos = [p for patron in ("*.zip", "*/*.zip", "*/*/*.zip") for p in raiz.glob(patron)
                  if not p.name.startswith(ZIPS_PROPIOS) and not (set(p.relative_to(raiz).parts[:-1]) & NO_MIRAR)]
    buenos = []
    for ruta in sorted(candidatos):
        try:
            with zipfile.ZipFile(ruta) as z:
                nombres = [n for n in z.namelist() if "__MACOSX" not in n]
        except (zipfile.BadZipFile, OSError):
            continue
        if all(any(f"{sub}/texto/" in n for n in nombres) for sub in SUBCARPETAS):
            buenos.append(ruta)
    return buenos


def _extraer(ruta_zip: Path, destino: Path) -> None:
    """Extrae un ZIP en `destino` (vacío), sin dejar que ningún archivo caiga afuera."""
    shutil.rmtree(destino, ignore_errors=True)
    destino.mkdir(parents=True)
    base = destino.resolve()
    with zipfile.ZipFile(ruta_zip) as z:
        for info in z.infolist():
            final = (base / info.filename).resolve()
            if "__MACOSX" in info.filename or (final != base and base not in final.parents):
                continue
            z.extract(info, base)


def _copia_limpia(origen: Path, destino: Path) -> dict[str, int]:
    """Copia a `destino` solo lo que usa conjuntos.preparar_legitimas_reales: los textos, las referencias y los roles de
    cada set. Devuelve cuántos textos tiene cada uno."""
    shutil.rmtree(destino, ignore_errors=True)
    cuenta = {}
    for sub in SUBCARPETAS:
        for carpeta, patron in (("texto", "*.txt"), ("referencia", "*.json")):
            (destino / sub / carpeta).mkdir(parents=True)
            for archivo in sorted((origen / sub / carpeta).glob(patron)):
                if archivo.is_file() and not archivo.name.startswith("."):
                    shutil.copy2(archivo, destino / sub / carpeta / archivo.name)
        for suelto in ("roles-protegida.json", "correspondencia.json"):
            if (origen / sub / suelto).is_file():
                shutil.copy2(origen / sub / suelto, destino / sub / suelto)
        cuenta[sub] = len(list((destino / sub / "texto").glob("*.txt")))
    return cuenta


def ubicar_legitimas_reales(raiz: Path, trabajo: Path, indicada: str = "") -> Path:
    """La carpeta con `set-legitimas/` y `set-zona-gris/`, lista para conjuntos.preparar_legitimas_reales.

    Busca primero en `indicada` (una carpeta o un ZIP; puede estar vacía o no existir) y después en `raiz`: una carpeta
    que traiga los dos sets, o un ZIP que la traiga adentro, que se descomprime en `trabajo/extraidas`. Devuelve
    `trabajo/limpias`, una copia sin archivos de más. Si no encuentra nada, explica qué hay que subir.
    """
    raiz, trabajo = Path(raiz), Path(trabajo)
    omitir = {trabajo.resolve()}
    lugares, avisos = [], []
    if indicada:
        ruta = Path(indicada).expanduser()
        if ruta.exists():
            lugares.append(ruta)
        else:
            avisos.append(f"LEGITIMAS_REALES apunta a {indicada}, que no existe: se busca en {raiz}.")
    lugares.append(raiz)
    origen = None
    for lugar in lugares:
        if lugar.is_file():
            zips = [lugar] if lugar.suffix.lower() == ".zip" else []
            carpetas = []
        else:
            carpetas = _carpetas_con_sets(lugar, omitir)
            zips = [] if carpetas else _zips_con_sets(lugar)
        if carpetas:
            origen = carpetas[0]
            if len(carpetas) > 1:
                avisos.append("Hay más de una carpeta con los sets; se usa la primera: " + ", ".join(map(str, carpetas)))
            break
        if zips:
            if len(zips) > 1:
                avisos.append("Hay más de un ZIP con los sets; se usa el primero: " + ", ".join(map(str, zips)))
            _extraer(zips[0], trabajo / "extraidas")
            dentro = _carpetas_con_sets(trabajo / "extraidas", set())
            if dentro:
                origen = dentro[0]
                avisos.append(f"Se descomprimió {zips[0]}.")
                break
            avisos.append(f"{zips[0]} no trae set-legitimas/ y set-zona-gris/ con sus textos.")
    for aviso in avisos:
        print(aviso, flush=True)
    if origen is None:
        try:
            hay = ", ".join(sorted(p.name for p in raiz.iterdir())) or "nada"
        except OSError:
            hay = "no se pudo listar"
        raise RuntimeError(
            "No encontré las legítimas reales. Subí a Colab el ZIP de la custodia (legitimas-reales-sets.zip) o la carpeta "
            f"sets/, con set-legitimas/ y set-zona-gris/ adentro, y volvé a ejecutar la celda. En {raiz} hay: {hay}.")
    cuenta = _copia_limpia(origen, trabajo / "limpias")
    print(f"Legítimas reales: {origen} → {trabajo / 'limpias'} ({', '.join(f'{k} {v} textos' for k, v in cuenta.items())})",
          flush=True)
    return trabajo / "limpias"


# --- zstd y Ollama ---
def asegurar_zstd(correr=subprocess.run, which=shutil.which, dormir=time.sleep, carpeta_bin: Path = Path("/usr/local/bin"),
                  intentos: int = 3) -> str:
    """Deja `zstd` disponible y devuelve cómo: 'ya estaba', 'apt-get' o 'reemplazo en Python'."""
    if which("zstd"):
        return "ya estaba"
    entorno = {**os.environ, "DEBIAN_FRONTEND": "noninteractive"}
    apt = ["apt-get", "-o", "DPkg::Lock::Timeout=180", "-o", "Acquire::Retries=3"]
    for intento in range(1, intentos + 1):
        correr([*apt, "update", "-qq"], env=entorno)          # si falla, igual se prueba instalar
        correr([*apt, "install", "-y", "-qq", "zstd"], env=entorno)
        if which("zstd"):
            return "apt-get"
        print(f"apt-get no instaló zstd (intento {intento} de {intentos}).", flush=True)
        dormir(5 * intento)
    # Sin apt-get: el instalador de Ollama solo necesita descomprimir, y eso lo hace el módulo zstandard.
    correr([sys.executable, "-m", "pip", "install", "-q", "zstandard"])
    if correr([sys.executable, "-c", "import zstandard"]).returncode == 0:
        carpeta_bin.mkdir(parents=True, exist_ok=True)
        destino = carpeta_bin / "zstd"
        destino.write_text(REEMPLAZO_ZSTD, encoding="utf-8")
        destino.chmod(0o755)
        if which("zstd"):
            return "reemplazo en Python"
    raise RuntimeError("No se pudo instalar zstd, ni con apt-get ni con el módulo zstandard. Reiniciá el entorno de "
                       "ejecución (Entorno de ejecución → Desconectar y borrar) y volvé a ejecutar la celda.")


def instalar_ollama(version: str, correr=subprocess.run, which=shutil.which, dormir=time.sleep, intentos: int = 3) -> None:
    """Instala Ollama en `version` con su instalador oficial. Reintenta si la descarga se corta."""
    orden = f"set -o pipefail; curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION={version} sh"
    for intento in range(1, intentos + 1):
        resultado = correr(["bash", "-c", orden])
        if resultado.returncode == 0 and which("ollama"):
            return
        print(f"El instalador de Ollama falló (intento {intento} de {intentos}).", flush=True)
        dormir(10 * intento)
    raise RuntimeError("No se pudo instalar Ollama. Revisá la conexión de Colab y volvé a ejecutar la celda.")


def reintentar(orden: list[str], que: str, correr=subprocess.run, dormir=time.sleep, intentos: int = 3) -> None:
    """Corre `orden` hasta que salga bien, con una pausa creciente; si no, avisa qué falló."""
    for intento in range(1, intentos + 1):
        if correr(orden).returncode == 0:
            return
        print(f"{que} falló (intento {intento} de {intentos}).", flush=True)
        dormir(10 * intento)
    raise RuntimeError(f"{que} falló {intentos} veces. Volvé a ejecutar la celda: lo que ya terminó no se repite.")


# --- Descargas ---
def descargar(carpeta: Path, nombre: str, donde: Path) -> Path:
    """Arma `donde/nombre.zip` con `carpeta` y lo manda a descargar. Si el navegador no deja, sigue: el ZIP queda en
    Colab, en el panel Archivos."""
    archivo = Path(shutil.make_archive(str(Path(donde) / nombre), "zip", carpeta))
    print(f"Descargando {archivo}", flush=True)
    try:
        from google.colab import files
        files.download(str(archivo))
    except Exception as error:  # la corrida no se corta por una descarga
        print(f"No se pudo descargar {archivo.name} ({error!r}): queda en {archivo}, en el panel Archivos.", flush=True)
    return archivo
