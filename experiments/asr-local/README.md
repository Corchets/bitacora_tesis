# Procedimiento repetible de ASR local (#19)

Procedimiento estandarizado y repetible para la transcripción local de audio en streaming
y por segmentos, orientado a la evaluación de detección incremental de vishing.

> **ADVERTENCIA: audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09; la corrida de entrega espera las grabaciones de #39.**

> **Estado: propuesta sin discutir.** La selección de Zipformer Kroko ONNX (`sherpa-onnx`) como motor principal de streaming y `faster-whisper` como comparador secundario segmentado es una propuesta técnica de laboratorio para hacer repetible el procedimiento; no cierra [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector). La corrida definitiva de entrega requiere el primer par grabado con voz humana ([#39](https://github.com/Corchets/bitacora_tesis/issues/39)).

---

## 1. Contrato de Salida: Actualizaciones de ASR (`actualizaciones.jsonl`)

Este componente produce el flujo incremental que consume el módulo de reproducción y detección ([#28](https://github.com/Corchets/bitacora_tesis/issues/28) en `experiments/replay/`).

El archivo `actualizaciones.jsonl` contiene:
1. Una primera línea de metadatos del sistema y motor:
   ```json
   {"meta": {"motor": "sherpa-zipformer", "modelo": "csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06", "tipo_entrega": "parciales_y_finales", "es_streaming": true, "sample_rate": 16000, "bloque_ms": 100, "hardware": {...}, "git": {...}, "versiones": {...}}}
   ```
2. Una línea por cada actualización emitida en orden cronológico:
   ```json
   {"llamada_id": "SC-WA-CODE-01-tts", "n": 7, "tipo": "parcial", "segmento": 2, "texto": "pasame el código", "inicio_audio_s": 8.40, "fin_audio_s": 10.12, "disponible_s": 10.31, "proceso_ms": 190.0, "canal": null}
   ```

### Definición de campos
- `tipo`:
  - `"parcial"`: borrador revisable del segmento abierto. Una actualización parcial posterior con el mismo `segmento` **reemplaza** a la anterior.
  - `"final"`: segmento cerrado definitivamente tras detección de silencio/endpoint. No se modifica con posterioridad.
- `segmento`: índice entero incremental del segmento de habla (turno detectado).
- `inicio_audio_s` / `fin_audio_s`: intervalo temporal en segundos dentro del audio de origen.
- `disponible_s`: instante temporal en el reloj del audio en que el sistema dispone de la transcripción (incluye la latencia de procesamiento medida; satisface estrictamente `disponible_s >= fin_audio_s` y nunca retrocede).
- `proceso_ms`: tiempo de procesamiento en milisegundos medido para generar esa actualización.
- `canal`: `"A"` o `"B"` en audio estéreo (por ejemplo VoIP con un interlocutor por canal), o `null` si es audio monoaural/mezcla.

---

## 2. Motores Implementados

| Motor | Modelo | Modo | Tipo de entrega | Endpoint / Segmentación |
|---|---|---|---|---|
| `sherpa-zipformer` (principal) | [`csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06) | Streaming en tiempo real | Parciales y finales | Segmentación por silencio (`corte_silencio_s=0.8s`, `umbral_rms=0.005`) y endpoint nativo con purga de lookahead (0.3s) y cola de vaciado final (2.0s) |
| `whisper` (secundario) | `faster-whisper-base` (int8 CPU) | NO streaming (por lotes/segmentos) | Finales por segmento | Filtro VAD integrado de Whisper (`min_silence_duration_ms=500ms`) |

---

## 3. Instalación Paso a Paso

### Requisitos previos
- macOS (Apple Silicon M1/M2/M3) o Linux x86_64/arm64.
- Python 3.10 o superior (verificado en Python 3.14).
- `ffmpeg` instalado en el sistema (`brew install ffmpeg` o `apt install ffmpeg`).

### Paso 1: Crear entorno virtual e instalar dependencias
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r experiments/asr-local/requirements.txt
```

### Paso 2: Descargar el modelo de Zipformer (opcional, se auto-descarga si falta)
El script descarga automáticamente el modelo desde Hugging Face la primera vez si no se encuentra en disco, pero puede pre-descargarse con:
```bash
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06',
    local_dir='experiments/asr-local/modelos/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06'
)
"
```

---

## 4. Generación de Audio Sintético de Humo

Para verificar la cadena de procesamiento antes de contar con las grabaciones humanas de [#39](https://github.com/Corchets/bitacora_tesis/issues/39):

```bash
./experiments/asr-local/sintetizar_par.sh
```

Esto toma los diálogos del par H1 en `experiments/slm-directo/casos/texto/` (`SC-WA-CODE-01-e01.txt` y `LG-WA-CONSULTA-01-e01.txt`), genera voces TTS con `say` (Paulina para A, Mónica para B) y genera en `experiments/asr-local/audio/` (carpeta ignorada por Git):
- `SC-WA-CODE-01-tts.wav` (mono 16 kHz)
- `SC-WA-CODE-01-tts-estereo.wav` (estéreo 16 kHz: canal izquierdo=A, canal derecho=B)
- `LG-WA-CONSULTA-01-tts.wav` (mono 16 kHz)
- `LG-WA-CONSULTA-01-tts-estereo.wav` (estéreo 16 kHz)

> **Nota sobre pausas en audio sintético:** Se inserta un silencio de 1,0 s entre turnos como convención de audio de humo sintético para permitir ejercitar la segmentación automática por turnos; no representa una propiedad de una llamada real donde los interlocutores pueden solaparse o pausar con tiempos variables.

---

## 5. Ejecución del Procedimiento

### Corrida básica (modo rápido)
```bash
python3 experiments/asr-local/asr_local.py experiments/asr-local/audio/SC-WA-CODE-01-tts.wav \
    --salida experiments/asr-local/corridas/mi_corrida \
    --motor sherpa-zipformer \
    --referencia experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt
```

### Corrida simulando tiempo real
```bash
python3 experiments/asr-local/asr_local.py experiments/asr-local/audio/SC-WA-CODE-01-tts.wav \
    --salida experiments/asr-local/corridas/corrida_tiempo_real \
    --motor sherpa-zipformer \
    --simular-tiempo-real \
    --bloque-ms 100
```

### Corrida con canal específico (en audio estéreo)
```bash
python3 experiments/asr-local/asr_local.py experiments/asr-local/audio/SC-WA-CODE-01-tts-estereo.wav \
    --salida experiments/asr-local/corridas/corrida_canal_a \
    --canal A
```

### Corrida con segundo motor (Whisper)
```bash
python3 experiments/asr-local/asr_local.py experiments/asr-local/audio/SC-WA-CODE-01-tts.wav \
    --salida experiments/asr-local/corridas/corrida_whisper \
    --motor whisper
```

### Cómo correr cuando exista la grabación del primer par (#39)
Cuando las grabaciones con voz humana estén disponibles fuera de Git (ej. en `data/audio/primer_par_sc.wav`), simplemente se ejecuta:
```bash
python3 experiments/asr-local/asr_local.py /ruta/a/primer_par_sc.wav \
    --salida experiments/asr-local/corridas/entrega_primer_par_sc \
    --motor sherpa-zipformer \
    --referencia /ruta/a/transcripcion_revisada.txt
```

---

## 6. Salidas Generadas por Cada Corrida

Cada ejecución en `--salida <dir>` genera tres archivos:

1. `actualizaciones.jsonl`: Flujo estructurado de actualizaciones según el contrato de ASR.
2. `manifiesto.json`: Registro completo y reproducible de:
   - Hardware: sistema operativo, arquitectura, núcleos de CPU, memoria RAM total.
   - Versiones de paquetes y hash de commit de Git.
   - Parámetros de ejecución: hilos, tamaño de bloque en ms, motor, modelo.
   - Métricas de cómputo: duración de audio, tiempo total de proceso, **RTF** (`tiempo_proceso / duracion_audio`), **memoria pico (RSS)** en MB (`resource.getrusage`).
   - Métricas de error: **WER**, **CER**, sustituciones, eliminaciones, inserciones y análisis de presencia de palabras clave críticas (`codigo`, `cero`, `sms`, `whatsapp`).
3. `resumen.md`: Informe sintético en Markdown con la advertencia metodológica en cabecera, tablas de rendimiento y comparación con el texto de referencia.

---

## 7. Ejecución de Pruebas Unitarias

El conjunto de pruebas valida el contrato JSONL, la secuencia de parciales y finales, la invariante temporal `disponible_s >= fin_audio_s` y el cálculo de WER sin depender de modelos externos pesados:

```bash
python3 -m unittest discover -s experiments/asr-local/tests -v
```

---

## 8. Limitaciones y Declaraciones Metodológicas

1. **Audio sintético vs. voz humana:** El audio producido por `sintetizar_par.sh` es voz sintetizada (TTS) sin ruido de canal telefónico, respiración ni solapamiento real. La tasa de error medida sobre este audio es únicamente una prueba de humo y **no** constituye evidencia de desempeño en condiciones reales.
2. **Dialecto y modelo:** El modelo Zipformer Kroko está entrenado principalmente en español general; su comportamiento frente al voseo rioplatense y términos locales debe validarse con las grabaciones humanas del piloto.
3. **Medición en PC:** Las mediciones de RTF y memoria en esta máquina (Apple M1, 8 GB RAM) son mediciones de laboratorio en PC de desarrollo y **no** equivalen al desempeño en dispositivos móviles Android (ver [PREFACTIBILIDAD-TECNICA.md](../../docs/investigacion/PREFACTIBILIDAD-TECNICA.md)).
