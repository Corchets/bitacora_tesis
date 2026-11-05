# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T17:44:51
- **Entrada:** `/Users/lucianogrosso/orca/workspaces/bitacora_tesis/lab-luciano-corridas-m1/experiments/asr-local/corridas/2026-10-17_estereo_LG-WA-CONSULTA-01_zipformer_mezcla/actualizaciones.jsonl` (sha256: `5fbd07f19a86ebe762098cfb918b0d528badcc53cf7bc329faa998b2a7f750ba`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `slm`
- **Configuración:** modelo: `qwen3.5:2b-q8_0`, prompt: `tarea`, hablantes: `ab`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `b082b6df2a` (cambios sin commit: False)

## Resultados por llamada

### Llamada `LG-WA-CONSULTA-01-tts-estereo`

- **Aviso emitido:** No (la llamada finalizó sin generar alertas sugeridas válidas)
- **Espera de cola máxima:** `17377.3 ms`
- **Atraso respecto del audio:** Sí (el detector acumuló retraso respecto de la llegada del audio)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 19 (parciales: 12, finales: 7)
- **Evaluaciones del detector:** 7 (válidas: 7, fallos: 0)
- **Tiempo de inferencia del detector:** total `31016.1 ms`, promedio `4430.9 ms` por evaluación
- **Espera de cola máxima observada:** `17377.3 ms`
- **Detector se atrasó respecto del audio:** Sí

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
