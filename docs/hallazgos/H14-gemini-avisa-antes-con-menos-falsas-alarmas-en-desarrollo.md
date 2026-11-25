# H14 — Gemini avisa más estafas antes del pedido y genera menos falsas alarmas en desarrollo

- **Fecha** 2026-11-23.
- **Tipo** resultado.
- **Estado** vigente.
- **Evidencia** [corrida y protocolo](../../experiments/slm-directo/corridas/2026-11-23_gemini-batch/README.md), [resultados pareados](../../experiments/slm-directo/corridas/2026-11-23_gemini-batch/analisis.md) y [#174](https://github.com/Corchets/bitacora_tesis/issues/174).
- **Afecta a** [capítulo 8](../tesis/CAP-08-RESULTADOS-EXPERIMENTALES.md#87-pendientes-del-capítulo).

## Qué encontramos

- En los pares completos, todos los casos avisados por Gemma también fueron avisados por Gemini dentro del grupo de estafas. Gemini sumó avisos y adelantó el primer aviso respecto del pedido en otros casos.
- Gemini tuvo menos falsas alarmas en total. También hubo legítimas en las que solo Gemini avisó.
- El tope de salida dejó sin puntaje algunas consultas de estafas. La comparación pareada excluye las llamadas afectadas para ambas configuraciones.

## Qué tan seguro es

Es una única pasada sobre conversaciones sintéticas de desarrollo. La anticipación usa las marcas del corpus, en líneas. Además del modelo difieren el runtime, el razonamiento y el formato de salida. El resultado describe las configuraciones comparadas sobre los casos completos.

## Qué cambia

El capítulo 8 incorpora el enlace como evidencia exploratoria complementaria de desarrollo.
