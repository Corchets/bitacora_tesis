# H11 — Con la misma configuración el riesgo se repite, pero cualquier cambio del runtime lo mueve en una de cada diez líneas

- **Fecha:** 2026-11-11
- **Tipo:** método
- **Estado:** vigente
- **Evidencia:** [`a56-latencia-172`](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md),
  [#172](https://github.com/Corchets/bitacora_tesis/issues/172)
- **Afecta a:** [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector), la evaluación final
  ([#52](https://github.com/Corchets/bitacora_tesis/issues/52)), el
  [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) y cualquier optimización de
  latencia en el A56

## Qué encontramos

Todo sale de `a56-latencia-172`: 6 conversaciones de desarrollo, 83 consultas, Gemma 4 E2B con
`c-premisa-corte-riesgo` en `llama-server` en el A56.

- **Mismo binario, mismos hilos, mismo lote:** el riesgo se repite en las 83 líneas. La corrida con el modo de
  rendimiento de Android solo cambia el reloj de la CPU y da 0/83 diferencias contra la base.
- **Cualquier cambio de cómo se calcula lo mueve.** Ninguno de estos cambios toca el prompt ni el modelo:

  | Cambio | Líneas con otro riesgo |
  |---|---:|
  | 6 hilos | 5/83 |
  | 8 hilos | 6/83 |
  | `-ub 128` | 8/83 |
  | Escribir el comienzo del JSON nosotros (propuesta 2 de #172) | 8/83 |
  | Build con dotprod+i8mm | 10/83 |
  | Vulkan | 16/83 |
  | Caché q8 | 2/50 |

- El cambio es de ±0,1 en la gran mayoría y nunca pasa de ±0,3. Cae sobre todo en riesgos de 0,2 a 0,5, alrededor del
  umbral de 0,3.
- En 1 o 2 de las 6 conversaciones, el primer aviso cae en otra línea o desaparece. En CV2-D-L-BANCO-007, una legítima,
  la base da un aviso falso que desaparece con 8 hilos, i8mm, Vulkan y `-ub 128`.

## Qué tan seguro es

- Seis conversaciones y una pasada por configuración. Los porcentajes son de 83 líneas, no de un corpus.
- La repetición exacta se vio en una sola pareja de corridas: la base y el modo de rendimiento.
- La causa (otro orden de las sumas en punto flotante) es la explicación habitual, pero no se aisló.
- No se comprobó si escribir el prefijo cambia además cómo se parte el texto en tokens.
- No se midió si estos cambios mejoran o empeoran la detección: con 6 conversaciones no se puede.

## Qué cambia

- **La condición «verificar que da lo mismo» de #172** no la cumple ninguna optimización que cambie el cálculo. Solo la
  cumple el aviso sin esperar el motivo, que no toca al modelo.
- **Las cifras de desarrollo y el A56 no son el mismo cálculo.** Las cifras se midieron con Ollama en PC y Colab, y el
  A56 corre `llama-server`. Es el caso del [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md)
  y de la tesis. Que coincidan línea por línea no está garantizado, igual que entre dos builds de `llama-server`.
- **El ruido de [H02](H02-ruido-entre-corridas.md)** (2 de 2.213 líneas al repetir en Colab) es el de repetir. Cambiar
  el runtime mueve bastante más.

> **Estado: propuesta sin discutir.** Si se adopta una optimización del A56 (la propuesta 2, el build con
> dotprod+i8mm o Vulkan), conviene fijar el stack del teléfono y medir sus avisos con más conversaciones de
> desarrollo antes de la evaluación final, en vez de suponer que reproduce las cifras de desarrollo. Ver
> [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).
