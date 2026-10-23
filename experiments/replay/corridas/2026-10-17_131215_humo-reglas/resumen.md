# Resumen de corrida replay

- **Fecha/hora:** 2026-10-17T13:12:22
- **Entrada:** `experiments/replay/tests/datos/ejemplo_actualizaciones.jsonl` (sha256: `3c0b384c6deeca25b2923bc73f29efa8f613dfaeb39b64aee8f34b296275b43a`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `reglas`
- **Configuración:** modelo: `no-aplica`, prompt: `no-aplica`, hablantes: `sin`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `5776460818` (cambios sin commit: False)

## Resultados por llamada

### Llamada `FICTICIO-01`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `8.1050 s` (disponible_s: `8.100 s`, inicio_eval: `8.100 s`, espera_cola: `0.0 ms`, detector: `5.0 ms`)
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
- **Espera de cola máxima:** `0.0 ms`
- **Atraso respecto del audio:** No (procesamiento al día)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 8 (parciales: 4, finales: 4)
- **Evaluaciones del detector:** 4 (válidas: 4, fallos: 0)
- **Tiempo de inferencia del detector:** total `12.5 ms`, promedio `3.1 ms` por evaluación
- **Espera de cola máxima observada:** `0.0 ms`
- **Detector se atrasó respecto del audio:** No

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
