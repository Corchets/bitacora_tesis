# ADR 0006 — Cortamos la salida del SLM después del campo que decide y pedimos el motivo solo al avisar

- **Fecha:** 2026-11-07, reescrita el 2026-11-09 para la configuración de la etapa 3
- **Estado:** Aceptada
- **Participantes de la discusión:** Mateo Antenucci, por el equipo, en la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143).
- **Ámbito:** arquitectura

## Contexto

El SLM responde cada consulta con un JSON: primero el campo con el que se decide (el riesgo y, en v4, la alerta) y
después el motivo y la evidencia. Motivo y evidencia solo sirven en el aviso, pero el modelo los escribe siempre: en
v4, 17 de los 41 tokens por línea eran `"motivo": ""` y `"evidencia": ""`. Cada token suma latencia en cada consulta,
y en el teléfono eso es lo que más pesa ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)).

## Decisión

1. Cada consulta usa el mismo prompt y el mismo esquema, pero corta la salida justo después del campo con el que se
   decide. Con C, que es la configuración elegida en la etapa 3, ese campo es el riesgo, el primero del JSON.
2. La app avisa con esa consulta. Motivo y evidencia salen de una segunda consulta, solo en el primer aviso de la
   llamada ([`motivo_c_corte.txt`](../../../experiments/slm-directo/prompts/motivo_c_corte.txt)). El aviso se muestra
   enseguida y el motivo se agrega cuando llega.
3. Vale para todos los prompts JSON que escriben primero el campo con el que se decide.

No cambia el prompt ni la política de aviso: eso lo fija el [ADR 0002](0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md).

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| JSON completo en cada consulta | El motivo llega en la misma consulta | Escribe campos vacíos en casi todas | Detecta lo mismo y es más lento |
| Aviso sin motivo, con un texto fijo | No hay segunda consulta | La persona no sabe por qué se la avisa | El equipo quiere que el aviso explique el motivo |
| Leer la probabilidad del token del riesgo (v4-L) | Es lo más rápido | En v4 pierde `alerta_sugerida`: 27/46 estafas contra 29/46 | La ganancia venía del corte. Queda para después de un ajuste fino |
| Streaming, cortando al leer el campo | El mismo ahorro, sin fijar un largo | Depende del cliente y de leer un JSON a medias | Equivale al corte y es más frágil |

## Consecuencias

- En T4, con v4, cada línea tardó 288 ms en vez de 393 antes del aviso, y la regla avisó en la misma línea en los 150
  casos de desarrollo.
- En la etapa 3, el motivo de C tardó unos 800 ms, una vez por llamada, y dio JSON válido en 22 de 22 avisos. Se
  midió con la variante que no se adoptó; con la configuración elegida falta medirlo.
- Si el motivo no llega, la app muestra un texto fijo.
- Cada prompt nuevo pasa una prueba de humo: el campo que decide tiene que terminar antes del corte.
- El corte de C tras el riesgo no se corrió como tal: el riesgo se leyó del JSON cortado tras la alerta, que escribe los
  mismos tokens antes. La evaluación final tiene que correrlo o declarar esa lectura.
- Falta medirlo en el teléfono.

**Para reconsiderarla:** que en el teléfono la segunda consulta no reutilice la transcripción ya procesada y el motivo
llegue demasiado tarde, o que en otro prompt el corte cambie el momento del aviso.

## Referencias

- [Etapa 1 de #143, «Decisión del equipo»](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analisis.md#decisión-del-equipo-2026-11-07):
  por qué se corta el JSON en vez de leer el token.
- [Medición del JSON cortado](../../../experiments/slm-directo/corridas/2026-11-07_json-cortado/analisis.md): v4,
  latencia y segunda consulta.
- [Etapa 3 de #143](../../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/analisis.md): la
  configuración elegida, el motivo de C y su latencia.
