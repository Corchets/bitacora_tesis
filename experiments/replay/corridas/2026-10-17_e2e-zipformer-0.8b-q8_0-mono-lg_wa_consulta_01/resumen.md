# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T17:42:14
- **Entrada:** `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/lab-luciano-corridas-m1/experiments/asr-local/corridas/2026-10-17_humo_lg_wa_consulta_01_zipformer/actualizaciones.jsonl` (sha256: `b5ddcbc4c2c2ec5137ca78a02092960677276af76fa663e7120b4bc53db8a21c`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `slm`
- **Configuración:** modelo: `qwen3.5:0.8b-q8_0`, prompt: `tarea`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `b082b6df2a` (cambios sin commit: False)

## Resultados por llamada

### Llamada `LG-WA-CONSULTA-01-tts`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `12.9233 s` (disponible_s: `10.058 s`, inicio_eval: `10.058 s`, espera_cola: `0.0 ms`, detector: `2865.3 ms`)
- **Motivo:** Te están solicitando un código de activación para WhatsApp que no pediste y que podría permitirte acceder a tu cuenta o datos personales.
- **Evidencia citada:** Me llegó por SMS un código para activar WhatsApp y yo no lo pedí. . No me lo leas ni lo compartas, revisa la seguridad desde la aplicación
- **Actualización desencadenante:**
  - **n:** 8
  - **Tipo:** `final`
  - **Segmento:** 2
  - **Canal:** `null`
  - **Texto de la actualización:** . No me lo leas ni lo compartas, revisa la seguridad desde la aplicación
  - **Intervalo de audio:** [5.20 s - 10.00 s] (disponible a los 10.058 s)
- **Información disponible al momento del aviso:**
  1. Me llegó por SMS un código para activar WhatsApp y yo no lo pedí
  2. . No me lo leas ni lo compartas, revisa la seguridad desde la aplicación
- **Espera de cola máxima:** `1461.2 ms`
- **Atraso respecto del audio:** Sí (el detector acumuló retraso respecto de la llegada del audio)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 14 (parciales: 10, finales: 4)
- **Evaluaciones del detector:** 4 (válidas: 4, fallos: 0)
- **Tiempo de inferencia del detector:** total `17061.1 ms`, promedio `4265.3 ms` por evaluación
- **Espera de cola máxima observada:** `1461.2 ms`
- **Detector se atrasó respecto del audio:** Sí

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
