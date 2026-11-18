# #143, evaluación final: las tablas sobre desarrollo (no decide)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-premisa-corte-riesgo` | 40/46, 87 % [74–94] | 19/36, 53 % [37–68] | 29/36, 81 % [65–90] | 12/15, 80 % [55–93] | 26/94, 28 % [20–37] | 2/29, 7 % [2–22] | 12/38, 32 % [19–47] | 12/27, 44 % [28–63] |
| config (repetición) | 39/46, 85 % [72–92] | 18/36, 50 % [34–66] | 28/36, 78 % [62–88] | 12/15, 80 % [55–93] | 28/94, 30 % [21–40] | 2/29, 7 % [2–22] | 12/38, 32 % [19–47] | 14/27, 52 % [34–69] |
| v4-corte | 28/46, 61 % [46–74] | 10/36, 28 % [16–44] | 25/36, 69 % [53–82] | 14/15, 93 % [70–99] | 42/94, 45 % [35–55] | 1/29, 3 % [1–17] | 23/38, 61 % [45–74] | 18/27, 67 % [48–81] |
| reglas v1 | 42/46, 91 % [80–97] | 27/36, 75 % [59–86] | 32/36, 89 % [75–96] | 15/15, 100 % [80–100] | 69/94, 73 % [64–81] | 13/29, 45 % [28–62] | 33/38, 87 % [73–94] | 23/27, 85 % [68–94] |
| reglas v2 | 11/46, 24 % [14–38] | 3/36, 8 % [3–22] | 9/36, 25 % [14–41] | 5/15, 33 % [15–58] | 36/94, 38 % [29–48] | 2/29, 7 % [2–22] | 18/38, 47 % [32–63] | 16/27, 59 % [41–75] |

## Comparación pareada (McNemar exacto), la configuración contra cada referencia

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | estafas | 14 | 2 | 0.004 |
| v4-corte | antes del pedido | 10 | 1 | 0.012 |
| v4-corte | a tiempo | 7 | 3 | 0.344 |
| v4-corte | antes del cumplimiento | 0 | 2 | 0.500 |
| v4-corte | FA | 8 | 24 | 0.007 |
| reglas v1 | estafas | 2 | 4 | 0.688 |
| reglas v1 | antes del pedido | 4 | 12 | 0.077 |
| reglas v1 | a tiempo | 2 | 5 | 0.453 |
| reglas v1 | antes del cumplimiento | 0 | 3 | 0.250 |
| reglas v1 | FA | 4 | 47 | 0.000 |
| reglas v2 | estafas | 30 | 1 | 0.000 |
| reglas v2 | antes del pedido | 16 | 0 | 0.000 |
| reglas v2 | a tiempo | 21 | 1 | 0.000 |
| reglas v2 | antes del cumplimiento | 8 | 1 | 0.039 |
| reglas v2 | FA | 13 | 23 | 0.132 |

