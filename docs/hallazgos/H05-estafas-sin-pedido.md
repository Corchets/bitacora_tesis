# H05 — Un detector de pedidos no avisa las estafas sin pedido

- **Fecha:** 2026-11-05
- **Tipo:** resultado
- **Estado:** vigente
- **Evidencia:**
  - [Descripción de #145](https://github.com/Corchets/bitacora_tesis/issues/145).
  - [Conclusiones de `2026-11-04_sin-indicio-150`](../../experiments/slm-directo/corridas/2026-11-04_sin-indicio-150/conclusiones.md#conclusiones), conclusión 5.
- **Afecta a:** [#33](https://github.com/Corchets/bitacora_tesis/issues/33), por cómo se cuentan las estafas sin pedido, y los capítulos 8 y 9.

## Qué encontramos

- En corpus_v2 hay 16 estafas que no avisó ninguna de las 5 corridas de Colab, y 9 de esas 16 no tienen pedido.
- En los 150 casos hay 19 estafas que ninguna configuración detecta, siempre las mismas. Ese techo no depende de Tito sino del SLM o del prompt.

## Qué tan seguro es

Que una estafa «no tiene pedido» depende de la referencia, que no tiene revisión humana. #145 propone revisarlas a ciegas.

## Qué cambia

> **Estado: propuesta sin discutir.** Informar siempre dos denominadores, todas las estafas y las que tienen pedido, como propone #145 para #33.
