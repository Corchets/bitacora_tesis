# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T13:03:02
- **Entrada:** `experiments/replay/tests/datos/ejemplo_actualizaciones.jsonl` (sha256: `7e6083e7295c3132b18180b85a6862c27988f87b8b235c88443ad979596df10c`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `reglas`
- **Configuración:** modelo: `no-aplica`, prompt: `no-aplica`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `d975d25199` (cambios sin commit: True)

## Resultados por llamada

### Llamada `SC-WA-CODE-01-tts`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `8.1148 s` (disponible_s: `8.100 s` + detector: `14.8 ms`)
- **Motivo:** REQUEST_AUTH_CODE (patrón: codigo, verificacion)
- **Evidencia citada:** pasame el codigo de verificacion que te llego
- **Actualización desencadenante:**
  - **n:** 7
  - **Tipo:** `final`
  - **Segmento:** 2
  - **Canal:** `null`
  - **Texto de la actualización:** pasame el codigo de verificacion que te llego
  - **Intervalo de audio:** [5.00 s - 7.80 s] (disponible a los 8.100 s)
- **Información disponible al momento del aviso:**
  1. hola buenas tardes
  2. te llamo de soporte técnico
  3. pasame el codigo de verificacion que te llego
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 8 (parciales: 4, finales: 4)
- **Evaluaciones del detector:** 4 (válidas: 4, fallos: 0)
- **Tiempo de inferencia del detector:** total `254.9 ms`, promedio `63.7 ms` por evaluación

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
