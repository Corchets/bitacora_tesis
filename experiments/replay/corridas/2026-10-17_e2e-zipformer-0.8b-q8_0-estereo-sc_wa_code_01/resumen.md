# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T17:42:29
- **Entrada:** `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/lab-luciano-corridas-m1/experiments/asr-local/corridas/2026-10-17_estereo_SC-WA-CODE-01_zipformer_mezcla/actualizaciones.jsonl` (sha256: `74c0439af89bd7f32756a25feac5ccdc0445ed042e118b3a3cd74981cb9de616`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `slm`
- **Configuración:** modelo: `qwen3.5:0.8b-q8_0`, prompt: `tarea`, hablantes: `ab`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `b082b6df2a` (cambios sin commit: False)

## Resultados por llamada

### Llamada `SC-WA-CODE-01-tts-estereo`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `20.1847 s` (disponible_s: `17.800 s`, inicio_eval: `17.800 s`, espera_cola: `0.0 ms`, detector: `2384.7 ms`)
- **Motivo:** Te están solicitando un código de activación que permite acceder a tu cuenta de WhatsApp.
- **Evidencia citada:** A: Para cancelar esa activación tenemos que resolver lo ahora. decime el código de activación que recibiste por s
- **Actualización desencadenante:**
  - **n:** 17
  - **Tipo:** `final`
  - **Segmento:** 4
  - **Canal:** `A`
  - **Texto de la actualización:** lo ahora. decime el código de activación que recibiste por s
  - **Intervalo de audio:** [13.00 s - 17.80 s] (disponible a los 17.800 s)
- **Información disponible al momento del aviso:**
  1. A: Te llamo de soporte por la activación de tu cuenta de WhatsApp
  2. A: .
  3. B: Me acababa de llegar un SMS, no pedí activar nada.
  4. A: Para cancelar esa activación tenemos que resolver
  5. A: lo ahora. decime el código de activación que recibiste por s
- **Espera de cola máxima:** `1584.7 ms`
- **Atraso respecto del audio:** Sí (el detector acumuló retraso respecto de la llegada del audio)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 22 (parciales: 15, finales: 7)
- **Evaluaciones del detector:** 7 (válidas: 7, fallos: 0)
- **Tiempo de inferencia del detector:** total `11823.0 ms`, promedio `1689.0 ms` por evaluación
- **Espera de cola máxima observada:** `1584.7 ms`
- **Detector se atrasó respecto del audio:** Sí

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
