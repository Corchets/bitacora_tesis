# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T17:43:40
- **Entrada:** `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/lab-luciano-corridas-m1/experiments/asr-local/corridas/2026-10-17_humo_lg_wa_consulta_01_zipformer/actualizaciones.jsonl` (sha256: `b5ddcbc4c2c2ec5137ca78a02092960677276af76fa663e7120b4bc53db8a21c`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `slm`
- **Configuración:** modelo: `qwen3.5:2b-q8_0`, prompt: `tarea`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `b082b6df2a` (cambios sin commit: False)

## Resultados por llamada

### Llamada `LG-WA-CONSULTA-01-tts`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `9.4415 s` (disponible_s: `5.281 s`, inicio_eval: `5.281 s`, espera_cola: `0.0 ms`, detector: `4160.5 ms`)
- **Motivo:** Te están pidiendo un código que da acceso a tu cuenta
- **Evidencia citada:** Me llegó por SMS un código para activar WhatsApp y yo no lo pedí
- **Actualización desencadenante:**
  - **n:** 4
  - **Tipo:** `final`
  - **Segmento:** 1
  - **Canal:** `null`
  - **Texto de la actualización:** Me llegó por SMS un código para activar WhatsApp y yo no lo pedí
  - **Intervalo de audio:** [0.00 s - 5.20 s] (disponible a los 5.281 s)
- **Información disponible al momento del aviso:**
  1. Me llegó por SMS un código para activar WhatsApp y yo no lo pedí
- **Espera de cola máxima:** `4634.9 ms`
- **Atraso respecto del audio:** Sí (el detector acumuló retraso respecto de la llegada del audio)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 14 (parciales: 10, finales: 4)
- **Evaluaciones del detector:** 4 (válidas: 4, fallos: 0)
- **Tiempo de inferencia del detector:** total `20665.8 ms`, promedio `5166.4 ms` por evaluación
- **Espera de cola máxima observada:** `4634.9 ms`
- **Detector se atrasó respecto del audio:** Sí

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
