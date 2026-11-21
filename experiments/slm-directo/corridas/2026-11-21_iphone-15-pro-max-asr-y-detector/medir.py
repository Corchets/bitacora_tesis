"""Corre una pasada en el iPhone desde la Mac y deja los resultados en `<etiqueta>/`.

Fija la hora de inicio del audio (`--margen` segundos desde ahora), lanza la app con `llama-server` y, con `--asr`,
el ASR sobre `audio.wav` desde esa hora; espera `/health`, mide el ida y vuelta de la red y corre
`ejecutar_agenda.py` con la misma hora. Al terminar el audio trae `recursos.log`, `runtime.log` y `asr.jsonl`.

Sin cable (`--ip`): `llama-server` escucha en 0.0.0.0 y la Mac le pega a la IP del teléfono por Wi-Fi; `devicectl`
lanza la app y copia los archivos por la red. Con cable (sin `--ip`): 127.0.0.1 y `iproxy`, como la corrida anterior.

    python3 -I medir.py asr-y-detector --asr --ip IP --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99
    python3 -I medir.py solo-detector --ip IP --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99

Con `--local ASR_MAC` no toca el teléfono: prueba en seco con un `llama-server` ya levantado en la Mac en el puerto
18080 y el binario `asr-mac` (app/asr_mac.cpp) corriendo el ASR en la Mac.
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
ANTERIOR = AQUI.parent / "2026-11-20_iphone-15-pro-max-latencia"
_spec = importlib.util.spec_from_file_location("medir_anterior", ANTERIOR / "medir.py")
anterior = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(anterior)
devicectl, PUERTO = anterior.devicectl, anterior.PUERTO
AGENDA = json.loads((AQUI / "agenda.json").read_text(encoding="utf-8"))


def get(base, ruta, espera=5):
    with urllib.request.urlopen(base + ruta, timeout=espera) as r:
        return json.load(r)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("etiqueta")
    p.add_argument("--asr", action="store_true", help="correr también el ASR sobre audio.wav")
    p.add_argument("--ip", help="IP del teléfono en la Wi-Fi; sin esto, por cable con iproxy")
    p.add_argument("--dispositivo")
    p.add_argument("--bundle")
    p.add_argument("--margen", type=float, default=150, help="segundos desde ahora hasta el inicio del audio")
    p.add_argument("--local", metavar="ASR_MAC", help="prueba en seco en la Mac con este binario de asr-mac")
    p.add_argument("--audio", help="con --local: el WAV")
    p.add_argument("--modelos", help="con --local: la carpeta de modelos del ASR")
    argv = sys.argv[1:]
    corte = argv.index("--") if "--" in argv else len(argv)
    a = p.parse_args(argv[:corte])
    extra = argv[corte + 1:]
    destino = AQUI / a.etiqueta
    if destino.exists():
        raise SystemExit(f"{destino} ya existe")
    host = "0.0.0.0" if a.ip else "127.0.0.1"
    servidor = ["-m", "gemma.gguf", "--host", host, "--port", str(PUERTO), "-c", "4096", "-np", "1", "--no-webui",
                *extra]
    base = f"http://{a.ip or '127.0.0.1'}:{PUERTO}"
    inicio = round(time.time() + a.margen, 3)
    medir = {"servidor": " ".join(["llama-server", *servidor]), "asr": a.asr, "inicio_audio": inicio,
             "inicio_audio_reloj": time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(inicio)),
             "conexion": "local" if a.local else ("wifi" if a.ip else "cable")}
    procesos = []
    if a.local:
        if a.asr:
            procesos.append(subprocess.Popen([a.local, a.audio, a.modelos, str(inicio), str(AQUI / f".{a.etiqueta}-asr.jsonl")]))
    else:
        entorno = {"ASR_WAV": "audio.wav", "ASR_MODELOS": "asr", "ASR_INICIO": str(inicio)} if a.asr else {}
        lanzada = devicectl("device", "process", "launch", "--device", a.dispositivo, "--terminate-existing",
                            *(["--environment-variables", json.dumps(entorno)] if entorno else []),
                            "--", a.bundle, *servidor, salida_json=True)
        medir["pid"] = lanzada["result"]["process"]["processIdentifier"]
        if not a.ip:
            procesos.append(subprocess.Popen(["iproxy", "-u", a.dispositivo, f"{PUERTO}:{PUERTO}"],
                                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
    try:
        t = time.time()
        while True:
            try:
                if get(base, "/health").get("status") == "ok":
                    break
            except (OSError, ValueError):
                pass
            if time.time() - t > a.margen - 20:
                raise SystemExit("llama-server no respondió a tiempo")
            time.sleep(1)
        medir["carga_hasta_health_s"] = round(time.time() - t, 2)
        ida_y_vuelta = []
        for _ in range(20):
            t = time.perf_counter()
            get(base, "/health")
            ida_y_vuelta.append((time.perf_counter() - t) * 1000)
            time.sleep(0.2)
        medir["health_ida_y_vuelta_ms"] = {"mediana": round(statistics.median(ida_y_vuelta), 1),
                                           "max": round(max(ida_y_vuelta), 1)}
        log = AQUI / f".{a.etiqueta}-ejecucion.log"
        with log.open("w", encoding="utf-8") as f:
            r = subprocess.run([sys.executable, "-I", str(AQUI / "ejecutar_agenda.py"), "--inicio", str(inicio),
                                "--salida", str(destino), "--base", base, "--servidor", medir["servidor"]],
                               stdout=f, stderr=subprocess.STDOUT)
        medir["salida_ejecutor"] = r.returncode
        destino.mkdir(exist_ok=True)
        log.rename(destino / "ejecucion.log")
        # El ASR termina con el audio: esperar el final más un margen para las últimas frases.
        time.sleep(max(0.0, inicio + AGENDA["duracion_s"] + 15 - time.time()))
    finally:
        for proceso in procesos:
            if proceso.args[0] == "iproxy":
                proceso.terminate()
            else:
                proceso.wait()
    if a.local and a.asr:
        (AQUI / f".{a.etiqueta}-asr.jsonl").rename(destino / "asr.jsonl")
    if not a.local:
        for nombre in ("recursos.log", "runtime.log", *(["asr.jsonl"] if a.asr else [])):
            devicectl("device", "copy", "from", "--device", a.dispositivo, "--domain-type", "appDataContainer",
                      "--domain-identifier", a.bundle, "--source", f"Documents/{nombre}",
                      "--destination", str(destino / nombre))
        detalles = devicectl("device", "info", "details", "--device", a.dispositivo, salida_json=True)["result"]
        medir["dispositivo"] = {
            "modelo": detalles.get("hardwareProperties", {}).get("marketingName"),
            "tipo": detalles.get("hardwareProperties", {}).get("productType"),
            "sistema": detalles.get("deviceProperties", {}).get("osVersionNumber"),
            "compilacion": detalles.get("deviceProperties", {}).get("osBuildUpdate"),
        }
        try:  # si iOS cerró la app, ya no hay proceso: eso también es un resultado
            devicectl("device", "process", "terminate", "--device", a.dispositivo, "--pid", str(medir["pid"]))
            medir["app_viva_al_final"] = True
        except SystemExit as e:
            medir["app_viva_al_final"], medir["terminate"] = False, str(e)
    manifiesto = destino / "manifiesto.json"
    medir["agenda_sha256"] = json.loads(manifiesto.read_text())["agenda_sha256"] if manifiesto.exists() else None
    (destino / "medir.json").write_text(json.dumps(medir, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(a.etiqueta, "listo:", medir.get("salida_ejecutor"))


if __name__ == "__main__":
    main()
