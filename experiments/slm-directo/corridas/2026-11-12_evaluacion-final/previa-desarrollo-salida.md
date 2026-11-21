# #143, evaluación final: las tablas sobre desarrollo (no decide)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-consejos-corte-riesgo` | 41/46, 89 % [77–95] | 19/36, 53 % [37–68] | 28/36, 78 % [62–88] | 14/15, 93 % [70–99] | 22/94, 23 % [16–33] | 1/29, 3 % [1–17] | 10/38, 26 % [15–42] | 11/27, 41 % [25–59] |
| config (repetición) | 42/46, 91 % [80–97] | 18/36, 50 % [34–66] | 28/36, 78 % [62–88] | 14/15, 93 % [70–99] | 18/94, 19 % [12–28] | 0/29, 0 % [0–12] | 9/38, 24 % [13–39] | 9/27, 33 % [19–52] |
| v4-corte | 28/46, 61 % [46–74] | 10/36, 28 % [16–44] | 25/36, 69 % [53–82] | 14/15, 93 % [70–99] | 42/94, 45 % [35–55] | 1/29, 3 % [1–17] | 23/38, 61 % [45–74] | 18/27, 67 % [48–81] |
| reglas v1 | 42/46, 91 % [80–97] | 27/36, 75 % [59–86] | 32/36, 89 % [75–96] | 15/15, 100 % [80–100] | 69/94, 73 % [64–81] | 13/29, 45 % [28–62] | 33/38, 87 % [73–94] | 23/27, 85 % [68–94] |
| reglas v2 | 11/46, 24 % [14–38] | 3/36, 8 % [3–22] | 9/36, 25 % [14–41] | 5/15, 33 % [15–58] | 36/94, 38 % [29–48] | 2/29, 7 % [2–22] | 18/38, 47 % [32–63] | 16/27, 59 % [41–75] |

## Comparación pareada (McNemar exacto), la configuración contra cada referencia

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | estafas | 13 | 0 | 0.000 |
| v4-corte | antes del pedido | 9 | 0 | 0.004 |
| v4-corte | a tiempo | 4 | 1 | 0.375 |
| v4-corte | antes del cumplimiento | 0 | 0 | 1.000 |
| v4-corte | FA | 5 | 25 | 0.000 |
| reglas v1 | estafas | 2 | 3 | 1.000 |
| reglas v1 | antes del pedido | 3 | 11 | 0.057 |
| reglas v1 | a tiempo | 1 | 5 | 0.219 |
| reglas v1 | antes del cumplimiento | 0 | 1 | 1.000 |
| reglas v1 | FA | 4 | 51 | 0.000 |
| reglas v2 | estafas | 30 | 0 | 0.000 |
| reglas v2 | antes del pedido | 16 | 0 | 0.000 |
| reglas v2 | a tiempo | 19 | 0 | 0.000 |
| reglas v2 | antes del cumplimiento | 9 | 0 | 0.004 |
| reglas v2 | FA | 10 | 24 | 0.024 |

