# Resumen de corrida ASR local

> **ADVERTENCIA: audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09; la corrida de entrega espera las grabaciones de #39.**

> **Estado: propuesta sin discutir.** Motor propuesto como procedimiento repetible; no cierra D09 (ver [MAPA-DECISIONES.md](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)).

## 1. Identificación y Hardware

- **Llamada ID:** `SC-WA-CODE-01-tts`
- **Audio fuente:** `experiments/asr-local/audio/SC-WA-CODE-01-tts.wav`
- **Duración audio:** 20.476 s (16000 Hz)
- **Canal:** `None`
- **Motor:** `whisper` (modelo: `faster-whisper-base`)
- **Streaming:** `False` | **Entrega:** `finales_por_segmento`
- **Modo de ejecución:** `rapido` (bloque: 100 ms)
- **Hardware medido:** Darwin 25.6.0 (arm64) | 8 núcleos | 8.0 GB RAM
- **Git commit:** `d975d2519961494c578769f5be6ec46b1870c9d3` (con cambios sin commit)

## 2. Rendimiento y Cómputo

- **Tiempo de proceso acumulado:** 3.167 s
- **RTF (Real-Time Factor):** **0.1546** (un RTF < 1.0 indica procesamiento más rápido que tiempo real)
- **Memoria pico (RSS):** **459.78 MB**
- **Actualizaciones totales:** 5 (0 parciales, 5 finales)
- **Segmentos cerrados:** 5

## 3. Transcripción Final

```text
Te llamo de soporte por la activación de tu cuenta de WhatsApp. Me acaba de llegar un smdc, no pedí activar nada. Para cancelar esa activación tenemos que resolverlo ahora. Decime el código de activación que recibiste por SMS. Es 0, 0, 0, 0, 0, 0.
```

## 4. Comparación con Texto de Referencia

- **Texto de referencia:** `experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt`
- **WER:** **15.22%** (distancia=7, sub=7, del=0, ins=0)
- **CER:** **10.28%** (distancia=26, sub=7, del=18, ins=1)

### Análisis de palabras clave críticas

| Palabra clave | En referencia | Encontrada en hipótesis | Estado |
|---|---|---|---|
| `codigo` | 1 | Sí | **OK** |
| `cero` | 6 | No | **PERDIDA** |
| `whatsapp` | 1 | Sí | **OK** |
| `sms` | 2 | Sí | **OK** |
| `activacion` | 3 | Sí | **OK** |
| `soporte` | 1 | Sí | **OK** |
| `cuenta` | 1 | Sí | **OK** |

