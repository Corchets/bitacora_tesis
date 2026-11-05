# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T13:30:27
- **Entrada:** `../asr-local/corridas/2026-10-17_humo_sc_wa_code_01_zipformer/actualizaciones.jsonl` (sha256: `146d82c2a71a1a8106cd60f647346fc258e0fa54bbc81da63b684e285edc712f`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `reglas`
- **Configuración:** modelo: `no-aplica`, prompt: `no-aplica`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `00ebbdf7b5` (cambios sin commit: False)

## Resultados por llamada

### Llamada `SC-WA-CODE-01-tts`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `17.8214 s` (disponible_s: `17.810 s`, inicio_eval: `17.810 s`, espera_cola: `0.0 ms`, detector: `11.4 ms`)
- **Motivo:** REQUEST_AUTH_CODE (patrón: codigo)
- **Evidencia citada:** . Decime el código de activación que recibiste por sms
- **Actualización desencadenante:**
  - **n:** 17
  - **Tipo:** `final`
  - **Segmento:** 4
  - **Canal:** `null`
  - **Texto de la actualización:** . Decime el código de activación que recibiste por sms
  - **Intervalo de audio:** [13.00 s - 17.80 s] (disponible a los 17.810 s)
- **Información disponible al momento del aviso:**
  1. Te llamo de soporte por la activación de tu cuenta de WhatsApp
  2. . Me acaba de llegar un SMS, no pedí activa
  3. r nada. Para cancelar esa activación tenemos que resolverlo ahora
  4. . Decime el código de activación que recibiste por sms
- **Espera de cola máxima:** `0.0 ms`
- **Atraso respecto del audio:** No (procesamiento al día)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 20 (parciales: 15, finales: 5)
- **Evaluaciones del detector:** 5 (válidas: 5, fallos: 0)
- **Tiempo de inferencia del detector:** total `69.8 ms`, promedio `14.0 ms` por evaluación
- **Espera de cola máxima observada:** `0.0 ms`
- **Detector se atrasó respecto del audio:** No

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
