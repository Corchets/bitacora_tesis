# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T17:42:40
- **Entrada:** `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/lab-luciano-corridas-m1/experiments/asr-local/corridas/2026-10-17_estereo_LG-WA-CONSULTA-01_zipformer_mezcla/actualizaciones.jsonl` (sha256: `5fbd07f19a86ebe762098cfb918b0d528badcc53cf7bc329faa998b2a7f750ba`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `slm`
- **Configuración:** modelo: `qwen3.5:0.8b-q8_0`, prompt: `tarea`, hablantes: `ab`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `b082b6df2a` (cambios sin commit: False)

## Resultados por llamada

### Llamada `LG-WA-CONSULTA-01-tts-estereo`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `18.1051 s` (disponible_s: `13.800 s`, inicio_eval: `15.427 s`, espera_cola: `1627.0 ms`, detector: `2678.1 ms`)
- **Motivo:** Te están solicitando un código de verificación para activar WhatsApp y pediendo que lo compartas o leas directamente desde la aplicación. Esto es una acción directa de seguridad guiada que podría permitirte robar datos personales o acceder a cuentas.
- **Evidencia citada:** A: Me llegó por SMS un código para activar WhatsApp y yo no lo pedí
- **Actualización desencadenante:**
  - **n:** 16
  - **Tipo:** `final`
  - **Segmento:** 4
  - **Canal:** `A`
  - **Texto de la actualización:** rme?
  - **Intervalo de audio:** [13.00 s - 13.80 s] (disponible a los 13.800 s)
- **Información disponible al momento del aviso:**
  1. A: Me llegó por SMS un código para activar WhatsApp y yo no lo pedí
  2. A: .
  3. B: No me lo leas ni lo compartas, revisa la seguridad desde la aplicación
  4. A: Necesitas verlo para ayuda
  5. B: .
  6. A: rme?
- **Espera de cola máxima:** `2497.1 ms`
- **Atraso respecto del audio:** Sí (el detector acumuló retraso respecto de la llegada del audio)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 19 (parciales: 12, finales: 7)
- **Evaluaciones del detector:** 7 (válidas: 7, fallos: 0)
- **Tiempo de inferencia del detector:** total `9961.4 ms`, promedio `1423.1 ms` por evaluación
- **Espera de cola máxima observada:** `2497.1 ms`
- **Detector se atrasó respecto del audio:** Sí

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
