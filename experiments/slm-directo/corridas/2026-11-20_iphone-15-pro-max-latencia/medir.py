"""Corre una configuración en el iPhone desde la Mac, por USB, y deja los resultados en `<etiqueta>/`.

Por cada corrida: relanza la app (un `llama-server` nuevo con los parámetros pedidos), reenvía el puerto 18080 del
teléfono a la Mac con `iproxy`, espera `/health` y corre `correr_android_latencia.py` en la Mac, sin cambios, contra
`127.0.0.1:18080`. Al terminar trae del teléfono `recursos.log` (memoria y estado térmico cada 5 s, los escribe la app)
y `runtime.log` (el log de `llama-server`).

    python3 -I medir.py metal --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99
    python3 -I medir.py cpu-t4 --prompt c-premisa-corte-riesgo --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 0 -t 4

Con `--base http://127.0.0.1:18080 --local` no toca el teléfono: usa un `llama-server` que ya esté corriendo en la Mac
(prueba en seco del recorrido).
"""
import argparse
import json
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parent.parent
CONVERSACIONES = AQUI.parent / "2026-11-11_a56-latencia-172" / "conversaciones-sub-6.json"
PUERTO = 18080
BASE_SERVIDOR = ["-m", "gemma.gguf", "--host", "127.0.0.1", "--port", str(PUERTO), "-c", "4096", "-np", "1",
                 "--no-webui"]


def devicectl(*args, salida_json=False):
    """`xcrun devicectl ...`; con salida_json devuelve el JSON que escribe devicectl."""
    with tempfile.NamedTemporaryFile(suffix=".json") as tmp:
        extra = ["--json-output", tmp.name] if salida_json else []
        r = subprocess.run(["xcrun", "devicectl", *args, *extra], text=True, capture_output=True)
        if r.returncode:
            raise SystemExit(f"devicectl {' '.join(args)}: {r.stdout}{r.stderr}")
        return json.loads(Path(tmp.name).read_text()) if salida_json else r.stdout


def get(ruta, espera=5):
    with urllib.request.urlopen(f"http://127.0.0.1:{PUERTO}{ruta}", timeout=espera) as r:
        return json.load(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("etiqueta")
    p.add_argument("--prompt", default="c-consejos-corte-riesgo")
    p.add_argument("--dispositivo", help="UDID del iPhone (xcrun devicectl list devices)")
    p.add_argument("--bundle", help="identificador de la app instalada")
    p.add_argument("--local", action="store_true", help="usar un llama-server ya levantado en la Mac")
    argv = sys.argv[1:]
    corte = argv.index("--") if "--" in argv else len(argv)
    a = p.parse_args(argv[:corte])
    extra = argv[corte + 1:]  # después de --: parámetros extra de llama-server
    destino = AQUI / a.etiqueta
    if destino.exists():
        raise SystemExit(f"{destino} ya existe")
    linea = " ".join(["llama-server", *BASE_SERVIDOR, *extra])
    medir = {"servidor": linea, "prompt": a.prompt, "conversaciones": CONVERSACIONES.name}

    proxy = None
    if not a.local:
        lanzada = devicectl("device", "process", "launch", "--device", a.dispositivo, "--terminate-existing",
                            a.bundle, *BASE_SERVIDOR, *extra, salida_json=True)
        medir["pid"] = lanzada["result"]["process"]["processIdentifier"]
        proxy = subprocess.Popen(["iproxy", "-u", a.dispositivo, f"{PUERTO}:{PUERTO}"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        inicio = time.time()
        while True:
            try:
                if get("/health").get("status") == "ok":
                    break
            except (OSError, ValueError):
                pass
            if time.time() - inicio > 300:
                raise SystemExit("llama-server no respondió en 300 s")
            time.sleep(1)
        medir["carga_hasta_health_s"] = round(time.time() - inicio, 2)
        medir["modelos"] = get("/v1/models").get("data")

        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "ejecucion.log"
            with log.open("w", encoding="utf-8") as f:
                r = subprocess.run([sys.executable, str(SLM / "correr_android_latencia.py"),
                                    "--conversaciones", str(CONVERSACIONES), "--salida", str(destino),
                                    "--prompt", a.prompt, "--servidor", linea],
                                   cwd=SLM, stdout=f, stderr=subprocess.STDOUT)
            medir["salida_ejecutor"] = r.returncode
            destino.mkdir(exist_ok=True)
            (destino / "ejecucion.log").write_text(log.read_text(encoding="utf-8"), encoding="utf-8")
    finally:
        if proxy:
            proxy.terminate()

    if not a.local:
        # La app sigue viva (y el pico de memoria, en recursos.log) hasta acá; después se cierra.
        time.sleep(6)
        for nombre in ("recursos.log", "runtime.log"):
            devicectl("device", "copy", "from", "--device", a.dispositivo, "--domain-type", "appDataContainer",
                      "--domain-identifier", a.bundle, "--source", f"Documents/{nombre}",
                      "--destination", str(destino / nombre))
        detalles = devicectl("device", "info", "details", "--device", a.dispositivo, salida_json=True)["result"]
        medir["dispositivo"] = {
            "modelo": detalles.get("hardwareProperties", {}).get("marketingName"),
            "tipo": detalles.get("hardwareProperties", {}).get("productType"),
            "sistema": detalles.get("deviceProperties", {}).get("osVersionNumber"),
            "compilacion": detalles.get("deviceProperties", {}).get("osBuildUpdate"),
            "memoria_bytes": detalles.get("hardwareProperties", {}).get("physicalMemory"),
        }
        devicectl("device", "process", "terminate", "--device", a.dispositivo, "--pid", str(medir["pid"]))

    # El ejecutor es el del A56: corrige en el manifiesto lo que es de esta corrida.
    ruta = destino / "manifiesto.json"
    if ruta.exists():
        manifiesto = json.loads(ruta.read_text(encoding="utf-8"))
        manifiesto["experimento"] = "iphone-15-pro-max-latencia"
        manifiesto["ejecutor_en"] = manifiesto.pop("sistema") + (" (Mac, llama-server local)" if a.local
                                                                 else " (Mac; llama-server en el iPhone, por iproxy)")
        ruta.write_text(json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8")
    (destino / "medir.json").write_text(json.dumps(medir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(a.etiqueta, "listo:", medir.get("salida_ejecutor"))


if __name__ == "__main__":
    main()
