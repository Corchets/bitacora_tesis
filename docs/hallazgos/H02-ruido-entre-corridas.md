# H02 — Repetir una corrida mueve 1 o 2 casos: ±2 sobre 150 es ruido

- **Fecha:** 2026-11-04
- **Tipo:** método
- **Estado:** vigente
- **Evidencia:** [conclusiones de `2026-11-04_sin-indicio-150`](../../experiments/slm-directo/corridas/2026-11-04_sin-indicio-150/conclusiones.md#conclusiones), conclusión 1.
- **Afecta a:** la regla de decisión de [#51](https://github.com/Corchets/bitacora_tesis/issues/51) y la de adopción de [#143](https://github.com/Corchets/bitacora_tesis/issues/143).

## Qué encontramos

- Repetida tal cual en Colab, la corrida de SLM solo cambió la respuesta en 2 de 2.213 líneas.
- Esas 2 líneas le costaron una estafa y le sumaron una falsa alarma: 55/19 la primera vez y 54/20 la segunda.

## Qué tan seguro es

Es una sola repetición, con E2B, `tarea` y GPU T4. Otro modelo u otro hardware pueden tener más variación.

## Qué cambia

- Una diferencia de 1 o 2 casos entre configuraciones no se atribuye a la configuración.
- Una corrida nueva que define algo lleva su repetición, como hizo #143.
