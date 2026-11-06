# H06 — v4 detecta lo mismo que v1 en corpus_v2, pero avisa más tarde y cita mejor

- **Fecha:** 2026-11-05
- **Tipo:** resultado
- **Estado:** en revisión. La segunda vuelta de [#143](https://github.com/Corchets/bitacora_tesis/issues/143) prueba prompts nuevos.
- **Evidencia:**
  - [Cuadro de `2026-11-05_tito-2-v4`](../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/analisis.md#resultados).
  - [Comentario de Mateo en #51](https://github.com/Corchets/bitacora_tesis/issues/51) del 2026-11-05.
- **Afecta a:** la elección de prompt en [#51](https://github.com/Corchets/bitacora_tesis/issues/51).

## Qué encontramos

| corpus_v2, SLM solo | Estafas (de 46) | Antes del pedido (de 36) | Falsas alarmas (de 51) |
|---|---:|---:|---:|
| v1 (`tarea`, hablantes A/B) | 28 | 13 | 4 |
| v4 (roles PROTEGIDA/OTRA) | 28 | 9 | 6 |

- v4 avisa más tarde y suma 2 falsas alarmas, dentro del ruido ([H02](H02-ruido-entre-corridas.md)).
- v4 cita mejor. En los 150 casos, el aviso cita el pedido real en 34 a 36 estafas, contra 27 con v1. Cita solo a la víctima en 1 o 2, contra 8 o 9.

## Qué tan seguro es

Es un empate en detección y un intercambio real entre anticipación y calidad del aviso. La causa del atraso es una hipótesis: no serían los roles, sino dos reglas del prompt.

- «que alguien apure o diga ser de una entidad no alcanza por sí solo para alertar»;
- «si tenés que suponer algo que no se dijo, no alertes».

## Qué cambia

La elección de prompt en #51 es un intercambio, no un empate. Hay que esperar la segunda vuelta de #143.
