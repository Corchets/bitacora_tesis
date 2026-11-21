"""#152, opción B: ¿Gemma 4 E2B puede reemplazar a Parakeet como ASR?

Transcribe los mismos clips con los dos y mide calidad (WER), demora por clip y memoria.
Cada clip es un turno de un caso de desarrollo, sintetizado con `say` de macOS: dura menos
de 30 s, que es el máximo de audio por entrada de E2B. Así la segmentación es la misma para
los dos y la diferencia sale solo del reconocedor.

Pasos (cada uno se puede repetir solo):

    python comparar_e2b_transcribe.py sintetizar --audio <dir fuera de Git>
    python comparar_e2b_transcribe.py parakeet   --audio <dir> --modelo <dir parakeet> --salida <corrida>
    python comparar_e2b_transcribe.py e2b        --audio <dir> --servidor http://127.0.0.1:8090 --pid <pid> --salida <corrida>
    python comparar_e2b_transcribe.py resumir    --salida <corrida>

`e2b` necesita un `llama-server` ya levantado con el GGUF y el `--mmproj` de audio.
"""

from __future__ import annotations

import argparse
import base64
import json
import platform
import re
import resource
import subprocess
import sys
import threading
import time
from pathlib import Path
from statistics import median

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ))
from wer import calcular_wer  # noqa: E402

TEXTO = RAIZ.parent / "slm-directo" / "casos" / "texto"

# 3 estafas y 3 legítimas de la lista para ASR (slm-directo/casos/GRABACIONES-ASR.md), con cifras dictadas.
CASOS = [
    "CV2-D-V-WHATSAPP-006",
    "CV2-D-V-ORGANISMO_PREVISIONAL-001",
    "CV2-D-V-SOPORTE-002",
    "CV2-D-L-BANCO-002",
    "CV2-D-L-DELIVERY-004",
    "CV2-D-L-FAMILIAR-002",
]
VOCES = {"A": "Paulina", "B": "Eddy (Spanish (Mexico))"}
CONDICIONES = ("16k", "8k")  # 8k: se baja a 8 kHz y se vuelve a 16 kHz, como una línea telefónica
PROMPT_E2B = "Transcribí textualmente este audio en español. Respondé solo con la transcripción, sin comentarios."


# ---------- audio ----------

def turnos(caso: str) -> list[tuple[str, str]]:
    salida = []
    for linea in (TEXTO / f"{caso}.txt").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^([AB]):\s*(.+)$", linea.strip())
        if m:
            salida.append((m.group(1), m.group(2)))
    return salida


def clips(audio: Path, condicion: str):
    for caso in CASOS:
        for i, (hablante, texto) in enumerate(turnos(caso), 1):
            yield caso, i, hablante, texto, audio / condicion / caso / f"{i:03d}.wav"


def sintetizar(args) -> None:
    audio = Path(args.audio)
    for caso, i, hablante, texto, _ in clips(audio, "16k"):
        tmp = audio / "aiff" / caso / f"{i:03d}.aiff"
        tmp.parent.mkdir(parents=True, exist_ok=True)
        if not tmp.exists():
            subprocess.run(["say", "-v", VOCES[hablante], "-o", str(tmp), texto], check=True)
        for cond in CONDICIONES:
            wav = audio / cond / caso / f"{i:03d}.wav"
            wav.parent.mkdir(parents=True, exist_ok=True)
            if wav.exists():
                continue
            if cond == "16k":
                subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", str(tmp), str(wav)], check=True)
            else:
                ocho = wav.with_suffix(".8k.wav")
                subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@8000", "-c", "1", str(tmp), str(ocho)], check=True)
                subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@16000", "-c", "1", str(ocho), str(wav)], check=True)
                ocho.unlink()
            agregar_margen(wav)
    print(f"listo: {sum(1 for _ in clips(audio, '16k'))} clips por condición en {audio}")


def agregar_margen(wav: Path) -> None:
    """Silencio antes y después, como la frase que arma el corte real (MotorPorFrases):
    0,3 s de preaudio (PREVIO_S) y los 0,8 s de silencio que la cierran."""
    import numpy as np
    import soundfile as sf

    audio, sr = sf.read(str(wav), dtype="int16")
    sf.write(str(wav), np.concatenate([np.zeros(int(0.3 * sr), np.int16), audio, np.zeros(int(0.8 * sr), np.int16)]),
             sr, subtype="PCM_16")


def duracion_s(wav: Path) -> float:
    import soundfile as sf

    info = sf.info(str(wav))
    return info.frames / info.samplerate


# ---------- motores ----------

def correr_parakeet(args) -> None:
    import numpy as np  # noqa: F401
    import sherpa_onnx
    import soundfile as sf

    base_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024
    d = Path(args.modelo)
    t0 = time.perf_counter()
    rec = sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / "encoder.int8.onnx"), decoder=str(d / "decoder.int8.onnx"),
        joiner=str(d / "joiner.int8.onnx"), tokens=str(d / "tokens.txt"),
        num_threads=args.hilos, sample_rate=16000, feature_dim=80,
        decoding_method="greedy_search", model_type="nemo_transducer",
    )
    carga_ms = (time.perf_counter() - t0) * 1000
    filas = []
    for cond in CONDICIONES:
        for caso, i, hablante, texto, wav in clips(Path(args.audio), cond):
            audio, sr = sf.read(str(wav), dtype="float32")
            t = time.perf_counter()
            s = rec.create_stream()
            s.accept_waveform(sr, audio)
            rec.decode_stream(s)
            ms = (time.perf_counter() - t) * 1000
            filas.append(fila("parakeet", cond, caso, i, hablante, texto, s.result.text, ms, len(audio) / sr))
    pico_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # macOS: bytes -> KB
    guardar(args, "parakeet", filas, {
        "modelo": "csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8", "hilos": args.hilos,
        "sherpa_onnx": sherpa_onnx.__version__, "carga_ms": round(carga_ms),
        "rss_pico_mb": round(pico_kb / 1024), "rss_antes_de_cargar_mb": round(base_kb / 1024),
    })


def rss_mb(pid: int) -> float:
    out = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True).stdout.strip()
    return int(out) / 1024 if out else 0.0


def footprint_mb(pid: int) -> float | None:
    """Huella física según macOS (incluye memoria de Metal, que el RSS no cuenta)."""
    out = subprocess.run(["footprint", "-p", str(pid)], capture_output=True, text=True).stdout
    m = re.search(r"phys_footprint:\s*([\d.]+)\s*([KMG]B)", out) or re.search(r"Footprint:\s*([\d.]+)\s*([KMG]B)", out)
    if not m:
        return None
    return float(m.group(1)) * {"KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)]


def footprint_pico(pid: int) -> float | None:
    """Pico de la huella física desde que arrancó el proceso, según macOS."""
    out = subprocess.run(["footprint", "-p", str(pid)], capture_output=True, text=True).stdout
    m = re.search(r"phys_footprint_peak:\s*([\d.]+)\s*([KMG]B)", out)
    return float(m.group(1)) * {"KB": 1 / 1024, "MB": 1, "GB": 1024}[m.group(2)] if m else None


def correr_e2b(args) -> None:
    import urllib.request

    # `footprint` es pesado: solo al principio y al final, para no robarle CPU a la medición de demoras.
    inicio = {"rss": rss_mb(args.pid), "footprint": footprint_mb(args.pid) or 0.0}
    pico = {"rss": inicio["rss"]}
    seguir = True

    def muestrear():
        while seguir:
            pico["rss"] = max(pico["rss"], rss_mb(args.pid))
            time.sleep(1.0)

    hilo = threading.Thread(target=muestrear, daemon=True)
    hilo.start()
    filas = []
    for cond in CONDICIONES:
        for caso, i, hablante, texto, wav in clips(Path(args.audio), cond):
            cuerpo = {
                "messages": [{"role": "user", "content": [
                    {"type": "input_audio", "input_audio": {"data": base64.b64encode(wav.read_bytes()).decode(), "format": "wav"}},
                    {"type": "text", "text": PROMPT_E2B},
                ]}],
                "temperature": 0, "seed": 42, "max_tokens": 256,
                "chat_template_kwargs": {"enable_thinking": False},
            }
            req = urllib.request.Request(f"{args.servidor}/v1/chat/completions", data=json.dumps(cuerpo).encode(),
                                         headers={"Content-Type": "application/json"})
            t = time.perf_counter()
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.load(r)
            ms = (time.perf_counter() - t) * 1000
            f = fila("e2b", cond, caso, i, hablante, texto, resp["choices"][0]["message"]["content"].strip(), ms, duracion_s(wav))
            tm = resp.get("timings", {})
            f.update({"lectura_ms": tm.get("prompt_ms"), "escritura_ms": tm.get("predicted_ms"),
                      "tokens_entrada": tm.get("prompt_n"), "tokens_salida": tm.get("predicted_n")})
            filas.append(f)
            print(f"{cond} {caso} {i:03d} {ms:6.0f} ms  wer {f['wer']:.2f}", flush=True)
    seguir = False
    hilo.join()
    props = json.load(urllib.request.urlopen(f"{args.servidor}/props"))
    final = footprint_pico(args.pid)
    guardar(args, "e2b", filas, {
        "servidor": props.get("build_info"), "modelo": props.get("model_path"), "prompt": PROMPT_E2B,
        "rss_pico_mb": round(pico["rss"]), "footprint_pico_mb": round(final) if final else None,
        "rss_inicio_mb": round(inicio["rss"]), "footprint_inicio_mb": round(inicio["footprint"]),
        "nota": args.nota,
    })


# ---------- métricas ----------

def normalizar_cifras(texto: str) -> str:
    """Pasa cifras a palabras para que «6047» y «seis mil cuarenta y siete» cuenten igual."""
    from num2words import num2words

    texto = re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", texto)  # 39.714.286 y 39,714,286 -> 39714286
    return re.sub(r"\d+", lambda m: f" {num2words(int(m.group()), lang='es')} ", texto)


def fila(motor, cond, caso, i, hablante, ref, hyp, ms, dur):
    w = calcular_wer(normalizar_cifras(ref), normalizar_cifras(hyp), sin_tildes=True)
    return {"motor": motor, "condicion": cond, "caso": caso, "turno": i, "hablante": hablante,
            "referencia": ref, "hipotesis": hyp, "wer": w["wer"], "errores": w["distancia"],
            "palabras": w["palabras_referencia"], "proceso_ms": round(ms, 1), "audio_s": round(dur, 2)}


def guardar(args, motor, filas, meta) -> None:
    salida = Path(args.salida)
    salida.mkdir(parents=True, exist_ok=True)
    with (salida / f"{motor}.jsonl").open("w", encoding="utf-8") as f:
        for r in filas:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    git = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=RAIZ).stdout.strip()
    meta.update({"casos": CASOS, "voces": VOCES, "condiciones": CONDICIONES, "git": git,
                 "maquina": {"sistema": platform.platform(), "cpu": platform.processor(),
                             "chip": subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True).stdout.strip()},
                 "fecha": time.strftime("%Y-%m-%d %H:%M")})
    (salida / f"{motor}.manifiesto.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"guardado {salida / motor}.jsonl ({len(filas)} clips)")


def cifras_bien(fs) -> tuple[int, int]:
    """Cifras de la referencia que aparecen enteras en la transcripción («6047» y no «2047»)."""
    from wer import normalizar_texto

    ok = tot = 0
    for f in fs:
        hyp = f" {normalizar_texto(normalizar_cifras(f['hipotesis']), sin_tildes=True)} "
        for num in re.findall(r"\d+", re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", f["referencia"])):
            tot += 1
            ok += f" {normalizar_texto(normalizar_cifras(num), sin_tildes=True)} " in hyp
    return ok, tot


def claves_bien(fs) -> tuple[int, int]:
    """Palabras críticas de `wer.PALABRAS_CLAVE_DEFECTO` («código», «cuenta», «clave»...) que se conservan."""
    from wer import analizar_errores_clave

    r = [x for f in fs for x in analizar_errores_clave(f["referencia"], f["hipotesis"])]
    return sum(x["detectada_en_hipotesis"] for x in r), len(r)


def resumir(args) -> None:
    salida = Path(args.salida)
    lineas = ["| Motor | Condición | WER | Clips sin error | Cifras enteras | Palabras críticas | Demora por clip, mediana (ms) | p90 (ms) | Tiempo / audio |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
    for motor in ("parakeet", "e2b"):
        p = salida / f"{motor}.jsonl"
        if not p.exists():
            continue
        filas = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines()]
        for f in filas:  # se recalcula con la normalización actual, sin volver a transcribir
            f.update({k: v for k, v in fila(motor, f["condicion"], f["caso"], f["turno"], f["hablante"],
                                             f["referencia"], f["hipotesis"], f["proceso_ms"], f["audio_s"]).items()
                      if k in ("wer", "errores", "palabras")})
        for cond in CONDICIONES:
            fs = [f for f in filas if f["condicion"] == cond]
            wer = sum(f["errores"] for f in fs) / sum(f["palabras"] for f in fs)
            ms = sorted(f["proceso_ms"] for f in fs)
            rtf = sum(f["proceso_ms"] for f in fs) / 1000 / sum(f["audio_s"] for f in fs)
            c, k = cifras_bien(fs), claves_bien(fs)
            lineas.append(f"| {motor} | {cond} | {wer:.1%} | {sum(f['errores'] == 0 for f in fs)}/{len(fs)} | "
                          f"{c[0]}/{c[1]} | {k[0]}/{k[1]} | "
                          f"{median(ms):.0f} | {ms[int(len(ms) * 0.9)]:.0f} | {rtf:.3f} |")
    print("\n".join(lineas))
    (salida / "tabla.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="paso", required=True)
    s = sub.add_parser("sintetizar"); s.add_argument("--audio", required=True)
    p = sub.add_parser("parakeet"); p.add_argument("--audio", required=True); p.add_argument("--modelo", required=True)
    p.add_argument("--hilos", type=int, default=2); p.add_argument("--salida", required=True)
    e = sub.add_parser("e2b"); e.add_argument("--audio", required=True); e.add_argument("--servidor", required=True)
    e.add_argument("--pid", type=int, required=True); e.add_argument("--salida", required=True); e.add_argument("--nota", default="")
    r = sub.add_parser("resumir"); r.add_argument("--salida", required=True)
    args = ap.parse_args()
    {"sintetizar": sintetizar, "parakeet": correr_parakeet, "e2b": correr_e2b, "resumir": resumir}[args.paso](args)


if __name__ == "__main__":
    main()
