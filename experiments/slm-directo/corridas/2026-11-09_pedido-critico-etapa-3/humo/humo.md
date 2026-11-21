# Humo de la etapa 3 de #143: C sin alerta y C con campo

Commit `c3c1ffa9b795ae0018d3e6d98d1cef91ae88ac59`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas). Tope: `num_predict` 48; el modelo cierra el JSON solo.

Criterio, fijado antes de correr: cada versión lee el JSON en las 48 líneas, sin llegar al tope. La que no pasa no corre; si no pasa ninguna, no corre nada.

| prompt | JSON leído | llegan al tope | tokens generados (mín / mediana / máx) | mismo riesgo que c-json-corte (dato) | pedido_critico en true (dato) | resultado |
|---|---|---|---|---|---|---|
| `c-sin-alerta` | 48/48 | 0 | 14 / 14 / 14 | 36/48 | — | PASA |
| `c-con-campo` | 48/48 | 0 | 24 / 24 / 24 | 23/48 | 3 | PASA |

`c-sin-alerta`: segunda consulta (motivo_c_corte.txt) en 0 alertas fuertes:


`c-con-campo`: segunda consulta (motivo_c_corte.txt) en 1 alertas fuertes:

- SC-WA-CODE-01-e01 L3: 623.4 ms  — 'Te están presionando para resolver algo de forma inmediata, lo cual es una táctica común en estafas.' / 'Para cancelar esa activación tenemos que resolverlo ahora.'
