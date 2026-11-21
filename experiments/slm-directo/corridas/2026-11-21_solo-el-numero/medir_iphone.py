"""Una corrida en el iPhone por Wi-Fi: relanza la app (un `llama-server` nuevo) y corre el ejecutor desde la Mac.

Como `medir.py` del 2026-11-20, pero sin cable (`--host 0.0.0.0` y la IP del teléfono, como el 2026-11-21) y con
`--consulta` para elegir la variante. La app es la misma: `llama-server` ya trae `/apply-template` y `/completion`.

    python3 medir_iphone.py iphone-hoy-1 --consulta chat --ip IP --dispositivo UDID --bundle ID.DE.LA.APP
    python3 medir_iphone.py iphone-numero --consulta numero --ip IP --dispositivo UDID --bundle ID.DE.LA.APP
"""
import argparse
import importlib.util
import json
import statistics
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SLM = AQUI.parents[1]
_spec = importlib.util.spec_from_file_location(
    "medir_anterior", AQUI.parent / "2026-11-20_iphone-15-pro-max-latencia" / "medir.py")
anterior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(anterior)
devicectl, PUERTO, CONVERSACIONES = anterior.devicectl, anterior.PUERTO, anterior.CONVERSACIONES
# El ejecutor tiene la dirección fija en `BASE`: se la cambia este arranque, sin tocar el archivo.
ARRANQUE = "import sys; sys.path.insert(0, sys.argv[1]); import correr_android_latencia as c; c.BASE = sys.argv[2]; " \
           "sys.argv = sys.argv[2:]; c.main()"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("etiqueta")
    p.add_argument("--consulta", choices=("chat", "numero"), required=True)
    p.add_argument("--ip", required=True)
    p.add_argument("--dispositivo", required=True)
    p.add_argument("--bundle", required=True)
    a = p.parse_args()
    destino = AQUI / a.etiqueta
    if destino.exists():
        raise SystemExit(f"{destino} ya existe")
    servidor = ["-m", "gemma.gguf", "--host", "0.0.0.0", "--port", str(PUERTO), "-c", "4096", "-np", "1", "--no-webui",
                "-ngl", "99"]
    base = f"http://{a.ip}:{PUERTO}"
    medir = {"servidor": " ".join(["llama-server", *servidor]), "consulta": a.consulta, "conexion": "wifi"}

    def get(ruta):
        with urllib.request.urlopen(base + ruta, timeout=5) as r:
            return json.load(r)

    lanzada = devicectl("device", "process", "launch", "--device", a.dispositivo, "--terminate-existing",
                        "--", a.bundle, *servidor, salida_json=True)
    medir["pid"] = lanzada["result"]["process"]["processIdentifier"]
    t = time.time()
    while True:
        try:
            if get("/health").get("status") == "ok":
                break
        except (OSError, ValueError):
            pass
        if time.time() - t > 120:
            raise SystemExit("llama-server no respondió en 120 s")
        time.sleep(1)
    medir["carga_hasta_health_s"] = round(time.time() - t, 2)
    ida_y_vuelta = []
    for _ in range(20):
        t = time.perf_counter()
        get("/health")
        ida_y_vuelta.append((time.perf_counter() - t) * 1000)
        time.sleep(0.2)
    medir["health_ida_y_vuelta_ms"] = {"mediana": round(statistics.median(ida_y_vuelta), 1),
                                       "max": round(max(ida_y_vuelta), 1)}
    log = AQUI / f".{a.etiqueta}-ejecucion.log"
    with log.open("w", encoding="utf-8") as f:
        r = subprocess.run([sys.executable, "-c", ARRANQUE, str(SLM), base, "--conversaciones", str(CONVERSACIONES),
                            "--salida", str(destino), "--prompt", "c-consejos-corte-riesgo", "--consulta", a.consulta,
                            "--prefijo", "salto", "--servidor", medir["servidor"] + " (iPhone 15 Pro Max, Wi-Fi)"],
                           cwd=SLM, stdout=f, stderr=subprocess.STDOUT)
    medir["salida_ejecutor"] = r.returncode
    destino.mkdir(exist_ok=True)
    log.rename(destino / "ejecucion.log")
    time.sleep(6)  # la app anota recursos cada 5 s
    for nombre in ("recursos.log", "runtime.log"):
        devicectl("device", "copy", "from", "--device", a.dispositivo, "--domain-type", "appDataContainer",
                  "--domain-identifier", a.bundle, "--source", f"Documents/{nombre}",
                  "--destination", str(destino / nombre))
    try:
        devicectl("device", "process", "terminate", "--device", a.dispositivo, "--pid", str(medir["pid"]))
        medir["app_viva_al_final"] = True
    except SystemExit as e:
        medir["app_viva_al_final"], medir["terminate"] = False, str(e)
    (destino / "medir.json").write_text(json.dumps(medir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(a.etiqueta, "listo:", medir["salida_ejecutor"])


if __name__ == "__main__":
    main()
