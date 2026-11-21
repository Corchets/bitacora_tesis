"""Arma el audio sintético de las seis conversaciones y la agenda con el inicio y el fin de cada línea.

Cada línea se sintetiza con `say` (Paulina para OTRA, Mónica para PROTEGIDA, las voces de
`asr-local/sintetizar_par.py`) y `afconvert` la pasa a 16 kHz, 16 bits, mono. Se recorta el silencio que `say` deja
al principio y al final, así la agenda marca la voz. Las líneas van una detrás de otra con `PAUSA_S` entre ellas, y
las conversaciones, con `ENTRE_CASOS_S`. El WAV es estéreo, como los ejemplos de la demo VoIP: izquierdo (canal 0)
OTRA, derecho (canal 1) PROTEGIDA. Un solo archivo con las seis conversaciones seguidas.

    python3 -I sintetizar.py RUTA/audio.wav

El WAV no va al repo (`*.wav` está en `.gitignore`); `agenda.json` sí, con el SHA-256 del WAV.
"""
import array
import hashlib
import json
import platform
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CONVERSACIONES = AQUI.parent / "2026-11-11_a56-latencia-172" / "conversaciones-sub-6.json"
VOCES = {"OTRA": "Paulina", "PROTEGIDA": "Mónica"}
CANAL = {"OTRA": 0, "PROTEGIDA": 1}
TASA = 16000
PAUSA_S = 0.6  # entre una línea y la siguiente: menos que el corte de 0,8 s, así dos líneas seguidas de OTRA
               # pueden quedar en una frase, como en una llamada
ENTRE_CASOS_S = 4.0
INICIO_S = 1.0
UMBRAL_RECORTE = 100  # |muestra| de 16 bits por debajo de esto, al principio o al final, es silencio de `say`


def sintetizar(texto, voz, tmp):
    aiff, wav = Path(tmp) / "l.aiff", Path(tmp) / "l.wav"
    subprocess.run(["say", "-v", voz, "-o", str(aiff), texto], check=True)
    subprocess.run(["afconvert", "-f", "WAVE", "-d", f"LEI16@{TASA}", "-c", "1", str(aiff), str(wav)], check=True)
    with wave.open(str(wav)) as w:
        assert (w.getframerate(), w.getnchannels(), w.getsampwidth()) == (TASA, 1, 2)
        m = array.array("h", w.readframes(w.getnframes()))
    voz_en = [i for i, x in enumerate(m) if abs(x) >= UMBRAL_RECORTE]
    return m[voz_en[0]:voz_en[-1] + 1] if voz_en else array.array("h")


def main():
    salida = Path(sys.argv[1])
    datos = json.loads(CONVERSACIONES.read_text(encoding="utf-8"))
    canales = [array.array("h"), array.array("h")]
    agenda = []

    def hasta(n):  # los dos canales con n muestras
        for c in canales:
            c.extend([0] * (n - len(c)))

    cursor = round(INICIO_S * TASA)
    with tempfile.TemporaryDirectory() as tmp:
        for caso, lineas in datos["casos"].items():
            filas = []
            for r in lineas:
                m = sintetizar(r["texto"], VOCES[r["hablante"]], tmp)
                hasta(cursor)
                canales[CANAL[r["hablante"]]].extend(m)
                filas.append({"n": r["n"], "hablante": r["hablante"], "inicio_s": round(cursor / TASA, 3),
                              "fin_s": round((cursor + len(m)) / TASA, 3)})
                cursor += len(m) + round(PAUSA_S * TASA)
                print(caso, r["n"], r["hablante"], filas[-1]["fin_s"], flush=True)
            agenda.append({"caso": caso, "inicio_s": filas[0]["inicio_s"], "fin_s": filas[-1]["fin_s"],
                           "lineas": filas})
            cursor += round((ENTRE_CASOS_S - PAUSA_S) * TASA)
    hasta(cursor)
    estereo = array.array("h", [0]) * (2 * cursor)
    estereo[0::2], estereo[1::2] = canales[0], canales[1]
    with wave.open(str(salida), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(TASA)
        w.writeframes(estereo.tobytes())
    (AQUI / "agenda.json").write_text(json.dumps({
        "conversaciones": CONVERSACIONES.name,
        "conversaciones_sha256": hashlib.sha256(CONVERSACIONES.read_bytes()).hexdigest(),
        "wav_sha256": hashlib.sha256(salida.read_bytes()).hexdigest(),
        "sample_rate": TASA, "canales": {"0": "OTRA", "1": "PROTEGIDA"}, "voces": VOCES,
        "pausa_s": PAUSA_S, "entre_casos_s": ENTRE_CASOS_S, "duracion_s": round(cursor / TASA, 3),
        "sistema": f"macOS {platform.mac_ver()[0]}", "casos": agenda,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
