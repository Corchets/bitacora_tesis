# Humo de la prueba de sensibilidad de #143

Commit `ca4fab05d7e67b221ce42c6497980ab8fa7758e4`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas), en todas las líneas. Todas cortan con `num_predict` 14.

Criterio, fijado antes de correr: cada una lee el riesgo, con su coma, en las 48 líneas. La que no pasa no corre; si no pasa la base, no corre nada.

| prompt | riesgo leído | errores | mismo riesgo que la base (dato) | riesgo ≥ 0,3 (dato) | riesgo ≥ 0,6 (dato) | resultado |
|---|---|---|---|---|---|---|
| `c-json-corte-riesgo` | 48/48 | — | 48/48 | 43 | 13 | PASA |
| `c-ancla-corte-riesgo` | 48/48 | — | 32/48 | 45 | 3 | PASA |
| `c-premisa-corte-riesgo` | 48/48 | — | 37/48 | 42 | 7 | PASA |
| `c-sin-freno-corte-riesgo` | 48/48 | — | 33/48 | 43 | 8 | PASA |
