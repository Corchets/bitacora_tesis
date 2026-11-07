# ADR 0006 — Cortamos la salida del SLM después de la alerta y pedimos el motivo solo al avisar

- **Fecha:** 2026-11-07
- **Estado:** Aceptada
- **Participantes de la discusión:** Mateo Antenucci, por el equipo, al cerrar la etapa 1 de la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143).
- **Ámbito:** arquitectura

## Contexto

El SLM responde cada línea de la llamada con un JSON de cuatro campos, en este orden: riesgo, alerta, motivo y
evidencia. Motivo y evidencia solo sirven en la línea del aviso, pero el modelo los escribe siempre: en 2.152 de 2.225
líneas de desarrollo, 17 de los 41 tokens son `"motivo": ""` y `"evidencia": ""`. Cada token suma latencia por línea,
y en el teléfono eso es lo que más pesa ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)).

## Decisión

1. La consulta de cada línea usa el mismo prompt y el mismo esquema, pero corta la salida a los 24 tokens, justo
   después de `alerta_sugerida`. La app decide si avisa con esa consulta.
2. Motivo y evidencia salen de una segunda consulta
   ([`motivo_v4_corte.txt`](../../../experiments/slm-directo/prompts/motivo_v4_corte.txt)), solo en la línea del aviso.
3. Vale para todas las pruebas con prompts JSON que escriben riesgo y alerta antes que motivo y evidencia.

No cambia el prompt ni la política de aviso: eso lo fija el ADR 0002.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| JSON completo en cada línea | El motivo llega en la misma consulta | Escribe tokens vacíos en casi todas las líneas | Detecta lo mismo y es más lento |
| Leer la probabilidad del token del riesgo (v4-L) | Es lo más rápido | Pierde `alerta_sugerida`: 27/46 estafas contra 29/46 | La ganancia venía del corte, no de la lectura. Queda para después de un ajuste fino |
| Streaming, cortando al leer la alerta | El mismo ahorro, sin fijar un largo | Depende del cliente y de leer un JSON a medias | Equivale al corte y es más frágil |
| JSON solo con la alerta | Más corto todavía | Cambia el prompt y no se probó | Un cambio por vez ([ADR 0005](0005-reglas-de-evaluacion-escritas-antes-de-correr.md)) |

## Consecuencias

- En T4, antes del aviso, cada línea tarda 288 ms en vez de 393 (−27 %), y la regla avisa en la misma línea en los 150
  casos de desarrollo.
- El aviso sale con la primera consulta. El motivo llega unos 660 ms después.
- Algunos avisos vuelven sin motivo (4 de 78 en desarrollo). La app tiene que mostrar un texto fijo.
- Cada prompt JSON nuevo pasa una prueba de humo: la alerta tiene que terminar dentro de los 24 tokens.
- Falta medirlo en el teléfono.

**Para reconsiderarla:** que en el teléfono la segunda consulta no reutilice la transcripción ya procesada y el motivo
llegue demasiado tarde, o que en otro prompt el corte cambie la línea del aviso.

## Referencias

- [Etapa 1 de #143, «Decisión del equipo»](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analisis.md#decisión-del-equipo-2026-11-07):
  por qué se corta el JSON en vez de leer el token.
- [Medición del JSON cortado](../../../experiments/slm-directo/corridas/2026-11-07_json-cortado/analisis.md): criterio
  escrito antes de correr, latencia y segunda consulta.
