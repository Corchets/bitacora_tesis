# Resumen de corrida ASR local

> **ADVERTENCIA: audio sintético TTS, no es evidencia de rendimiento sobre voz humana ni cierra D09; la corrida de entrega espera las grabaciones de #39.**

> **Estado: propuesta sin discutir.** Motor propuesto como procedimiento repetible; no cierra D09 (ver [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)).

## 1. Identificación y Hardware

- **Llamada ID:** `LG-WA-CONSULTA-01-tts`
- **Audio fuente:** `experiments/asr-local/audio/LG-WA-CONSULTA-01-tts.wav`
- **Duración audio:** 15.572 s (16000 Hz)
- **Canal:** `None`
- **Motor:** `sherpa-zipformer` (modelo: `csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`)
- **Streaming:** `True` | **Entrega:** `parciales_y_finales`
- **Modo de ejecución:** `rapido` (bloque: 100 ms)
- **Hardware medido:** Darwin 25.6.0 (arm64) | 8 núcleos | 8.0 GB RAM
- **Git commit:** `b29ff73e863e388904703e0181a2d6f6d773c7f1` (limpio)

## 2. Rendimiento y Cómputo

- **Tiempo de proceso acumulado:** 1.608 s
- **RTF (Real-Time Factor):** **0.1032** (un RTF < 1.0 indica procesamiento más rápido que tiempo real)
- **Memoria pico (RSS):** **422.7 MB**
- **Actualizaciones totales:** 14 (10 parciales, 4 finales)
- **Segmentos cerrados:** 4

## 3. Transcripción Final

```text
Me llegó por SMS un código para activar WhatsApp y yo no lo pedí . No me lo leas ni lo compartas, revisa la seguridad desde la aplicación . Necesitas verlo para ayudar me? No, no hace falta que me digas ningún código.
```

## 4. Comparación con Texto de Referencia

- **Texto de referencia:** `experiments/slm-directo/casos/texto/LG-WA-CONSULTA-01-e01.txt`
- **WER:** **5.00%** (distancia=2, sub=1, del=0, ins=1)
- **CER:** **0.48%** (distancia=1, sub=0, del=0, ins=1)

### Análisis de palabras clave críticas

| Palabra clave | En referencia | Encontrada en hipótesis | Estado |
|---|---|---|---|
| `codigo` | 2 | Sí | **OK** |
| `whatsapp` | 1 | Sí | **OK** |
| `sms` | 1 | Sí | **OK** |
| `seguridad` | 1 | Sí | **OK** |

