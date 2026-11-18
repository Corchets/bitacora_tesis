# Humo de la revisión de producto de #143

Commit `30746d3f3889cb047e9639b1fc9cde50cad2f3ec`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas), en todas las líneas. Todas cortan con `num_predict` 14.

Criterio, fijado antes de correr: cada una lee el riesgo, con su coma, en las 48 líneas. La que no pasa no corre; si no pasa la base, no corre nada.

| prompt | riesgo leído | errores | mismo riesgo que la base (dato) | riesgo ≥ 0,3 (dato) | riesgo ≥ 0,6 (dato) | resultado |
|---|---|---|---|---|---|---|
| `c-premisa-corte-riesgo` | 48/48 | — | 48/48 | 43 | 7 | PASA |
| `c-codigo-corte-riesgo` | 48/48 | — | 23/48 | 35 | 3 | PASA |
| `c-consejos-corte-riesgo` | 48/48 | — | 40/48 | 41 | 11 | PASA |
| `c-freno-corte-riesgo` | 48/48 | — | 32/48 | 45 | 3 | PASA |
