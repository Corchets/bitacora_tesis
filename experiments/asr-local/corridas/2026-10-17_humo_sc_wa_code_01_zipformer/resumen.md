# Resumen de corrida ASR local

> **ADVERTENCIA: audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09; la corrida de entrega espera las grabaciones de #39.**

> **Estado: propuesta sin discutir.** Motor propuesto como procedimiento repetible; no cierra D09 (ver [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)).

## 1. Identificación y Hardware

- **Llamada ID:** `SC-WA-CODE-01-tts`
- **Audio fuente:** `experiments/asr-local/audio/SC-WA-CODE-01-tts.wav`
- **Duración audio:** 21.276 s (16000 Hz)
- **Canal:** `None`
- **Motor:** `sherpa-zipformer` (modelo: `csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`)
- **Streaming:** `True` | **Entrega:** `parciales_y_finales`
- **Modo de ejecución:** `rapido` (bloque: 100 ms)
- **Hardware medido:** Darwin 25.6.0 (arm64) | 8 núcleos | 8.0 GB RAM
- **Git commit:** `b29ff73e863e388904703e0181a2d6f6d773c7f1` (limpio)

## 2. Rendimiento y Cómputo

- **Tiempo de proceso acumulado:** 3.638 s
- **RTF (Real-Time Factor):** **0.171** (un RTF < 1.0 indica procesamiento más rápido que tiempo real)
- **Memoria pico (RSS):** **357.0 MB**
- **Actualizaciones totales:** 20 (15 parciales, 5 finales)
- **Segmentos cerrados:** 5

## 3. Transcripción Final

```text
Te llamo de soporte por la activación de tu cuenta de WhatsApp . Me acaba de llegar un SMS, no pedí activa r nada. Para cancelar esa activación tenemos que resolverlo ahora . Decime el código de activación que recibiste por sms . Es cero, cero, cero, cero, cero, cero
```

## 4. Comparación con Texto de Referencia

- **Texto de referencia:** `experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt`
- **WER:** **4.35%** (distancia=2, sub=1, del=0, ins=1)
- **CER:** **0.40%** (distancia=1, sub=0, del=0, ins=1)

### Análisis de palabras clave críticas

| Palabra clave | En referencia | Encontrada en hipótesis | Estado |
|---|---|---|---|
| `codigo` | 1 | Sí | **OK** |
| `cero` | 6 | Sí | **OK** |
| `whatsapp` | 1 | Sí | **OK** |
| `sms` | 2 | Sí | **OK** |
| `activacion` | 3 | Sí | **OK** |
| `soporte` | 1 | Sí | **OK** |
| `cuenta` | 1 | Sí | **OK** |

