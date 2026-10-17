# Resumen de corrida ASR local

> **ADVERTENCIA: audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09; la corrida de entrega espera las grabaciones de #39.**

> **Estado: propuesta sin discutir.** Motor propuesto como procedimiento repetible; no cierra D09 (ver [MAPA-DECISIONES.md](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)).

## 1. Identificación y Hardware

- **Llamada ID:** `LG-WA-CONSULTA-01-tts`
- **Audio fuente:** `experiments/asr-local/audio/LG-WA-CONSULTA-01-tts.wav`
- **Duración audio:** 14.972 s (16000 Hz)
- **Canal:** `None`
- **Motor:** `sherpa-zipformer` (modelo: `csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`)
- **Streaming:** `True` | **Entrega:** `parciales_y_finales`
- **Modo de ejecución:** `rapido` (bloque: 100 ms)
- **Hardware medido:** Darwin 25.6.0 (arm64) | 8 núcleos | 8.0 GB RAM
- **Git commit:** `d975d2519961494c578769f5be6ec46b1870c9d3` (con cambios sin commit)

## 2. Rendimiento y Cómputo

- **Tiempo de proceso acumulado:** 1.973 s
- **RTF (Real-Time Factor):** **0.1318** (un RTF < 1.0 indica procesamiento más rápido que tiempo real)
- **Memoria pico (RSS):** **401.78 MB**
- **Actualizaciones totales:** 12 (11 parciales, 1 finales)
- **Segmentos cerrados:** 1

## 3. Transcripción Final

```text
Me llegó por SMS un código para activar WhatsApp y yo no lo pedí. No me lo leas ni lo compartas, revisa la seguridad desde la aplicación. Necesitas verlo para ayudarme? No, no hace falta que
```

## 4. Comparación con Texto de Referencia

- **Texto de referencia:** `experiments/slm-directo/casos/texto/LG-WA-CONSULTA-01-e01.txt`
- **WER:** **10.00%** (distancia=4, sub=0, del=4, ins=0)
- **CER:** **11.06%** (distancia=23, sub=0, del=23, ins=0)

### Análisis de palabras clave críticas

| Palabra clave | En referencia | Encontrada en hipótesis | Estado |
|---|---|---|---|
| `codigo` | 2 | Sí | **OK** |
| `whatsapp` | 1 | Sí | **OK** |
| `sms` | 1 | Sí | **OK** |
| `seguridad` | 1 | Sí | **OK** |

