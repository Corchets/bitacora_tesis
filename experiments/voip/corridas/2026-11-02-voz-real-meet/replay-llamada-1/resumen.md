# Resumen de corrida replay

- **Fecha/hora:** 2026-11-02T20:29:45
- **Entrada:** `../voip/llamadas/2026-11-02_191055-519549/actualizaciones.jsonl` (sha256: `b6c08f8246bdffd729274f00c09c545b6c261b7f888db11f0d490ac70707bad8`)
- **Modo:** Audio ASR incremental (JSONL)
- **Detector:** `tito-slm`
- **Configuración:** modelo: `gemma4:e2b-it-q4_K_M`, prompt: `tarea`, hablantes: `ab`, disparo: `final`
- **Política de aviso:** `aviso_unico_primer_true_valido`
- **Código git:** commit `f3a047cded` (cambios sin commit: False)

## Resultados por llamada

### Llamada `VIVO-20261102-191055-519549`

- **Aviso emitido:** Sí
- **T_A (reloj de audio):** `26.5898 s` (disponible_s: `22.887 s`, inicio_eval: `22.887 s`, espera_cola: `0.0 ms`, detector: `3702.8 ms`)
- **Motivo:** Te están informando sobre un débito no reconocido y te están presionando para que verifiques o actúes sobre él.
- **Evidencia citada:** Detectamos un débito de 85 mil pesos que usted no le conoce.
- **Actualización desencadenante:**
  - **n:** 14
  - **Tipo:** `final`
  - **Segmento:** 4
  - **Canal:** `otra`
  - **Texto de la actualización:** Detectamos un débito de 85 mil pesos que usted no le conoce.
  - **Intervalo de audio:** [17.96 s - 22.60 s] (disponible a los 22.887 s)
- **Información disponible al momento del aviso:**
  1. A: Hola, buenas tardes. Hablo con el titular de la cuenta.
  2. B: Sí, soy yo, ¿quién habla?
  3. A: Le hablo del banco macro de Tucumán, del área de seguridad.
  4. A: Detectamos un débito de 85 mil pesos que usted no le conoce.
- **Espera de cola máxima:** `0.0 ms`
- **Atraso respecto del audio:** No (procesamiento al día)
- **Fallos del detector:** 0

## Métricas generales de ejecución

- **Llamadas procesadas:** 1
- **Actualizaciones totales:** 60 (parciales: 45, finales: 15)
- **Evaluaciones del detector:** 15 (válidas: 15, fallos: 0)
- **Tiempo de inferencia del detector:** total `29389.0 ms`, promedio `1959.3 ms` por evaluación
- **Espera de cola máxima observada:** `0.0 ms`
- **Detector se atrasó respecto del audio:** No

> **Nota metodológica:** Este reporte refleja la ejecución técnica incremental sin acceso a etiquetas de clase, roles ni marcas humanas.
