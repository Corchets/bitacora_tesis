# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T13:30:27
- **Entrada:** `../asr-local/corridas/2026-10-17_humo_lg_wa_consulta_01_zipformer/actualizaciones.jsonl` (sha256: `b5ddcbc4c2c2ec5137ca78a02092960677276af76fa663e7120b4bc53db8a21c`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `reglas`
- **Configuración:** modelo: `no-aplica`, prompt: `no-aplica`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `00ebbdf7b5` (cambios sin commit: False)

## Resultados por llamada

### Llamada `LG-WA-CONSULTA-01-tts`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `5.2915 s` (disponible_s: `5.281 s`, inicio_eval: `5.281 s`, espera_cola: `0.0 ms`, detector: `10.5 ms`)
- **Motivo:** REQUEST_AUTH_CODE (patrón: codigo)
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
- **Espera de cola máxima:** `0.0 ms`
- **Atraso respecto del audio:** No (procesamiento al día)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 14 (parciales: 10, finales: 4)
- **Evaluaciones del detector:** 4 (válidas: 4, fallos: 0)
- **Tiempo de inferencia del detector:** total `28.7 ms`, promedio `7.2 ms` por evaluación
- **Espera de cola máxima observada:** `0.0 ms`
- **Detector se atrasó respecto del audio:** No

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
