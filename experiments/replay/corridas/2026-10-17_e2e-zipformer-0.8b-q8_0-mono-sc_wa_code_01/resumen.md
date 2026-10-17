# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T17:41:56
- **Entrada:** `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/lab-luciano-corridas-m1/experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_zipformer/actualizaciones.jsonl` (sha256: `146d82c2a71a1a8106cd60f647346fc258e0fa54bbc81da63b684e285edc712f`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `slm`
- **Configuración:** modelo: `qwen3.5:0.8b-q8_0`, prompt: `tarea`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `b082b6df2a` (cambios sin commit: False)

## Resultados por llamada

### Llamada `SC-WA-CODE-01-tts`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `14.9559 s` (disponible_s: `13.003 s`, inicio_eval: `13.003 s`, espera_cola: `0.0 ms`, detector: `1952.9 ms`)
- **Motivo:** Te están solicitando un código de activación que permite acceder a tu cuenta de WhatsApp.
- **Evidencia citada:** Me acaba de llegar un SMS, no pedí activa
- **Actualización desencadenante:**
  - **n:** 13
  - **Tipo:** `final`
  - **Segmento:** 3
  - **Canal:** `null`
  - **Texto de la actualización:** r nada. Para cancelar esa activación tenemos que resolverlo ahora
  - **Intervalo de audio:** [8.40 s - 13.00 s] (disponible a los 13.003 s)
- **Información disponible al momento del aviso:**
  1. Te llamo de soporte por la activación de tu cuenta de WhatsApp
  2. . Me acaba de llegar un SMS, no pedí activa
  3. r nada. Para cancelar esa activación tenemos que resolverlo ahora
- **Espera de cola máxima:** `0.0 ms`
- **Atraso respecto del audio:** No (procesamiento al día)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 20 (parciales: 15, finales: 5)
- **Evaluaciones del detector:** 5 (válidas: 5, fallos: 0)
- **Tiempo de inferencia del detector:** total `10548.5 ms`, promedio `2109.7 ms` por evaluación
- **Espera de cola máxima observada:** `0.0 ms`
- **Detector se atrasó respecto del audio:** No

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
