# Medición #84 — M1 de 8 GB, Qwen3.5 0.8B

Corrida del 2026-10-26 con código `6669b104f9c18fd170f9d57c78a13c4c98f9f8d7`
y árbol limpio. Ejemplo TTS `SC-WA-CODE-01`, fuera de corpus_v2: esta prueba
sirve para estimar el costo de la demo, no el rendimiento del detector en llamadas reales.

Desde `experiments/voip/` se ejecutó:

```bash
/Users/lucianogrosso/bitacora_tesis-voip/.venv/bin/python medir.py \
  --detector slm --modelo qwen3.5:0.8b-q8_0 \
  --audio /Users/lucianogrosso/bitacora_tesis-voip/experiments/asr-local/audio/SC-WA-CODE-01-tts-estereo.wav \
  --modelo-asr /Users/lucianogrosso/bitacora_tesis-voip/experiments/asr-local/modelos/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06 \
  --salida corridas/2026-10-26-medicion-84-m1-08b
```

Salida:

```text
CUMPLE (< 2 s/evaluación): mediana 1,312 s · evaluaciones: 4 · salteadas: 0 · fallos: 0 · aviso a 20.403 s (+2.803 s respecto del fin del pedido)
```

El criterio se aplica a la **mediana**: la evaluación más lenta duró 1,956 s.
La carga inicial del SLM tardó 0,483 s y quedó fuera de la mediana. Los dos
canales recibieron 22,217 s de audio al ritmo real. Disparo `final`, silencio de
0,8 s, prompt `tarea`, seed 42, hablantes A/B, Ollama local 0.40.5.

Evidencia observable (sin audio):

- [Manifiesto](2026-10-26_173220-376117/manifiesto.json): configuración, máquina, commit, hash del TTS y digest del modelo.
- [Evaluaciones](2026-10-26_173220-376117/detector.jsonl): cuatro respuestas y aviso único.
- [ASR](2026-10-26_173220-376117/actualizaciones.jsonl): transcripciones TTS por rol.

También se ejecutó `--detector reglas` en la M1 con el mismo TTS y ASR, con
salida descartable en `/tmp/voip-84-reglas-final`: mediana 0,009 s, cuatro evaluaciones,
cero salteadas y fallos, aviso a 18,455 s (+0,855 s respecto del fin del pedido).
No se versionó esa corrida.

**Pendiente humano:** repetir el comando en la M4 con 0.8B y 4B. No se probaron
en este ticket voz real, Meet ni otra notebook. No se ejecutó ni consultó la reserva CV2-T-*.
