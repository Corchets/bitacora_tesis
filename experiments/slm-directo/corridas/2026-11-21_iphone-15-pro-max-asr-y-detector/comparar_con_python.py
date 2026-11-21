"""Verifica que el ASR en C++ (app/asr.cpp) da lo mismo que `MotorSherpaParakeet` de Python con `parakeet-filtro`.

Corre el motor de `experiments/asr-local/motores.py` sobre el mismo WAV, bloque por bloque y sin esperar el tiempo
real, con la configuración de la demo (corte 0,8 s, RMS 0,008, Silero 0,5 en modo «filtro», 2 hilos) y sin los
filtros de texto, como asr.cpp. Compara tipo, canal, segmento, inicio, fin y texto de cada evento con un `asr.jsonl`.
Necesita `sherpa-onnx==1.13.8` y `numpy` (Python 3.13: no hay rueda para 3.15).

    python -I comparar_con_python.py AUDIO.wav CARPETA_MODELOS asr.jsonl
"""
import json
import sys
import wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "asr-local"))
from motores import DetectorSilero, MotorSherpaParakeet  # noqa: E402

ROLES = ("OTRA", "PROTEGIDA")
CLAVES = ("tipo", "canal", "segmento", "inicio_audio_s", "fin_audio_s", "texto")


def main():
    wav, modelos, cpp = sys.argv[1:4]
    with wave.open(wav) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2)
    motores = []
    for _ in ROLES:
        m = MotorSherpaParakeet(f"{modelos}/parakeet", hilos=2)
        m.inicializar()
        m.corte_silencio_s, m.umbral_rms_silencio, m.filtrar_idioma = 0.8, 0.008, False
        m.modo_vad, m.detector_voz = "filtro", DetectorSilero(f"{modelos}/silero_vad.onnx", 0.5)
        motores.append(m)
    python = []
    for k in range(0, len(x), 640):
        b = x[k:k + 640]
        for c, rol in enumerate(ROLES):
            for e in motores[c].procesar_bloque(b[:, c].astype(np.float32) / 32768.0, k / 16000, (k + len(b)) / 16000):
                python.append((e.tipo, rol, e.segmento, e.inicio_audio_s, e.fin_audio_s, e.texto))
    for c, rol in enumerate(ROLES):
        python += [(e.tipo, rol, e.segmento, e.inicio_audio_s, e.fin_audio_s, e.texto)
                   for e in motores[c].vaciar_final(len(x) / 16000)]
    eventos = [json.loads(l) for l in Path(cpp).read_text(encoding="utf-8").splitlines()]
    cpp_ev = [tuple(round(e[k], 3) if isinstance(e[k], float) else e[k] for k in CLAVES)
              for e in eventos if e["tipo"] in ("parcial", "final")]
    python = [tuple(round(v, 3) if isinstance(v, float) else v for v in t) for t in python]
    iguales = sum(a == b for a, b in zip(sorted(cpp_ev), sorted(python)))
    print(json.dumps({"eventos_cpp": len(cpp_ev), "eventos_python": len(python), "iguales": iguales,
                      "finales": sum(t[0] == "final" for t in python)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
