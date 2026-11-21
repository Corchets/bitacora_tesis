# H07 — El indicio de Tito le hace perder estafas al SLM

- **Fecha:** 2026-11-04
- **Tipo:** resultado
- **Estado:** vigente
- **Evidencia:** [conclusiones de `2026-11-04_sin-indicio-150`](../../experiments/slm-directo/corridas/2026-11-04_sin-indicio-150/conclusiones.md#conclusiones), conclusión 3.
- **Afecta a:**
  - el [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md), que registra la configuración con indicio;
  - [#51](https://github.com/Corchets/bitacora_tesis/issues/51);
  - [CAP-05 §5.5.1](../tesis/CAP-05-DISENO-Y-ARQUITECTURA.md#551-detector).

## Qué encontramos

- El indicio es el bloque del prompt que le muestra al SLM la frase que activó a Tito.
- Con indicio se pierden 5 estafas que sin indicio se detectan:
  - `CV2-D-V-BANCO-003`;
  - `CV2-D-V-BANCO-011`;
  - `CV2-D-V-FAMILIAR-003`;
  - `CV2-D-V-PREMIO-002`;
  - `TR-01-pedido-indirecto-digitos`.
- Además, los avisos antes del pedido bajan de 24 a 18. Con indicio: 50/75 estafas y 12/75 falsas alarmas; sin indicio, 54/14.
- La activación de Tito es la misma en las dos condiciones: la diferencia la produce el bloque del prompt.
- La mejora de Tito viejo 2.0 con v1 también vino de sacar el indicio, no de sus frases.

## Qué tan seguro es

Una corrida por condición, en los 150 casos de desarrollo. 4 estafas son más que el ruido de ±2 ([H02](H02-ruido-entre-corridas.md)).

## Qué cambia

La demo ya corre sin indicio desde el 2026-11-05. El ADR 0002 de #51 y el capítulo 5 tienen que registrarlo.

> **Nota del 2026-11-11:** registrado en el [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) y en el capítulo 5: el detector no usa Tito ni indicio.
