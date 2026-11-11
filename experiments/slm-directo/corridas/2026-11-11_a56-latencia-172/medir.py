"""Corre una configuración de #172 en el A56 desde la PC, por adb, y trae los resultados a `<etiqueta>/`.

Por cada corrida: cierra las apps en segundo plano y cualquier `llama-server`, arranca uno nuevo con los parámetros
pedidos, espera `/health`, corre `correr_android_latencia.py` en Termux y, mientras tanto, cada 15 s anota memoria
(`VmHWM`, `VmRSS`) de los dos procesos y la temperatura de batería en `recursos.log`. El código ya tiene que estar en
`~/a56-172` de Termux (ver README).

    python -I medir.py base-t4 --lista rapida-20 --consulta chat -- -t 4
    python -I medir.py t6 --lista sub-6 --consulta chat -- -t 6
    python -I medir.py grande-t4 --lista sub-6 --taskset f0 -- -t 4
"""
import argparse
import io
import json
import subprocess
import sys
import tarfile
import threading
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
LAB = "/data/local/tmp/a56-lab"
TERMUX = "/data/data/com.termux/files"
HOME = f"{TERMUX}/home/a56-172"
BASE_SERVIDOR = ["-m", f"{LAB}/gemma.gguf", "--host", "127.0.0.1", "--port", "18080", "-c", "4096",
                 "-np", "1", "--no-webui"]


def adb(*args, check=True, **kw):
    return subprocess.run(["adb", *args], check=check, text=True, capture_output=True, **kw)


def termux(comando: str, **kw):
    env = f"HOME={TERMUX}/home PREFIX={TERMUX}/usr PATH={TERMUX}/usr/bin:/system/bin"
    return subprocess.run(["adb", "shell", f"run-as com.termux env {env} sh -c '{comando}'"], text=True, **kw)


def muestrear(destino: Path, parar: threading.Event) -> None:
    with destino.open("w", encoding="utf-8") as f:
        while not parar.is_set():
            salida = adb("shell", "date -Iseconds; for p in $(pgrep -f llama-server) $(pgrep -f correr_android_latencia); "
                         "do echo PID=$p $(tr '\\0' ' ' < /proc/$p/cmdline | cut -c1-70); "
                         "grep -E 'VmHWM|VmRSS' /proc/$p/status; done; "
                         "dumpsys battery | grep -E '^  (level|temperature|AC powered|USB powered)'", check=False).stdout
            f.write(salida)
            f.flush()
            parar.wait(15)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("etiqueta")
    p.add_argument("--lista", choices=("rapida-20", "sub-6"), required=True)
    p.add_argument("--consulta", choices=("chat", "coma", "numero"), default="chat")
    p.add_argument("--prefijo", choices=("compacto", "salto"), default="compacto")
    p.add_argument("--binarios", default=f"{LAB}/llama", help="carpeta de llama-server en el teléfono")
    p.add_argument("--taskset", default="", help="máscara de CPU en hexadecimal para llama-server (p. ej. f0)")
    p.add_argument("--antes", default="", help="comando adb shell a correr antes (p. ej. el modo de rendimiento)")
    argv = sys.argv[1:]
    corte = argv.index("--") if "--" in argv else len(argv)
    a = p.parse_args(argv[:corte])
    extra = argv[corte + 1:]  # después de --: parámetros extra de llama-server
    destino = AQUI / a.etiqueta
    destino.mkdir(exist_ok=False)

    # El llama-server de Vulkan no siempre termina con SIGTERM (quedó uno vivo tras s6-vk): se fuerza y se comprueba.
    adb("shell", "pkill -9 -f llama-server; am kill-all", check=False)
    time.sleep(2)
    vivos = adb("shell", "pgrep -f llama-server | while read p; do grep -q llama-server /proc/$p/cmdline && "
                "case $(tr '\\0' ' ' < /proc/$p/cmdline) in ./llama-server*) echo $p;; esac; done", check=False).stdout
    if vivos.strip():
        raise SystemExit(f"quedó un llama-server vivo: {vivos.split()}")
    if a.antes:
        print(adb("shell", a.antes, check=False).stdout)
    prefijo = f"taskset {a.taskset} " if a.taskset else ""
    linea = " ".join([f"{prefijo}./llama-server", *BASE_SERVIDOR, *extra])
    adb("shell", f"cd {a.binarios} && (LD_LIBRARY_PATH=. nohup {linea} > {LAB}/srv-172.log 2>&1 &)")
    adb("forward", "tcp:18080", "tcp:18080")
    inicio = time.time()
    while True:
        try:
            with urllib.request.urlopen("http://127.0.0.1:18080/health", timeout=5) as r:
                if json.load(r).get("status") == "ok":
                    break
        except OSError:
            pass
        if time.time() - inicio > 180:
            raise SystemExit("llama-server no arrancó: " + adb("shell", f"tail -20 {LAB}/srv-172.log").stdout)
        time.sleep(1)
    carga_s = time.time() - inicio

    parar = threading.Event()
    hilo = threading.Thread(target=muestrear, args=(destino / "recursos.log", parar))
    hilo.start()
    salida = f"salidas/{a.etiqueta}"
    with (destino / "ejecucion.log").open("w", encoding="utf-8") as log:
        r = termux(f"cd {HOME} && python correr_android_latencia.py --conversaciones conversaciones-{a.lista}.json "
                   f"--salida {salida} --consulta {a.consulta} --prefijo {a.prefijo} --servidor \"{linea}\"",
                   stdout=log, stderr=subprocess.STDOUT)
    parar.set()
    hilo.join()
    (destino / "runtime.log").write_text(adb("shell", f"cat {LAB}/srv-172.log").stdout, encoding="utf-8")
    tar = subprocess.run(["adb", "exec-out", f"run-as com.termux sh -c 'cd {HOME}/{salida} && tar cf - .'"],
                         capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(tar)).extractall(destino)
    adb("shell", "pkill -f llama-server", check=False)
    (destino / "medir.json").write_text(json.dumps({"lista": a.lista, "servidor": linea, "binarios": a.binarios,
                                                    "antes": a.antes, "carga_hasta_health_s": round(carga_s, 2),
                                                    "salida_ejecutor": r.returncode}, indent=2) + "\n")
    print(a.etiqueta, "listo:", r.returncode)


if __name__ == "__main__":
    main()
