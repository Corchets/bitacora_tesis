# #143, evaluación final: los criterios sobre desarrollo (no decide)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-premisa-corte-riesgo` | 40/46, 87 % [74–94] | 19/36, 53 % [37–68] | 29/36, 81 % [65–90] | 12/15, 80 % [55–93] | 26/94, 28 % [20–37] | 2/29, 7 % [2–22] | 12/38, 32 % [19–47] | 12/27, 44 % [28–63] |
| config (repetición) | 39/46, 85 % [72–92] | 18/36, 50 % [34–66] | 28/36, 78 % [62–88] | 12/15, 80 % [55–93] | 28/94, 30 % [21–40] | 2/29, 7 % [2–22] | 12/38, 32 % [19–47] | 14/27, 52 % [34–69] |
| v4-corte | 28/46, 61 % [46–74] | 10/36, 28 % [16–44] | 25/36, 69 % [53–82] | 14/15, 93 % [70–99] | 42/94, 45 % [35–55] | 1/29, 3 % [1–17] | 23/38, 61 % [45–74] | 18/27, 67 % [48–81] |
| reglas v1 | 42/46, 91 % [80–97] | 27/36, 75 % [59–86] | 32/36, 89 % [75–96] | 15/15, 100 % [80–100] | 69/94, 73 % [64–81] | 13/29, 45 % [28–62] | 33/38, 87 % [73–94] | 23/27, 85 % [68–94] |
| reglas v2 | 11/46, 24 % [14–38] | 3/36, 8 % [3–22] | 9/36, 25 % [14–41] | 5/15, 33 % [15–58] | 36/94, 38 % [29–48] | 2/29, 7 % [2–22] | 18/38, 47 % [32–63] | 16/27, 59 % [41–75] |

## Criterios, con `c-premisa-corte-riesgo` como configuración

| criterio | valor | resultado |
|---|---|---|
| le gana a v4-corte sin perder (estafas, a tiempo, FA) | a favor y en contra: estafas 14 a 2 (p = 0.004); a tiempo 7 a 3 (p = 0.344); FA 24 a 8 (p = 0.007) | cumple |
| le gana a reglas v1 sin perder (estafas, a tiempo, FA) | a favor y en contra: estafas 2 a 4 (p = 0.688); a tiempo 2 a 5 (p = 0.453); FA 47 a 4 (p = 0.000) | cumple |
| límite inferior de a tiempo ≥ 50% | 29/36, 81 % [65–90] | cumple |
| límite inferior de estafas ≥ 50% | 40/46, 87 % [74–94] | cumple |
| #144 cae como mucho 20% en estafas avisadas | no corrió | — |

## Criterios, con `c-premisa-corte-riesgo` (repetición) como configuración

| criterio | valor | resultado |
|---|---|---|
| le gana a v4-corte sin perder (estafas, a tiempo, FA) | a favor y en contra: estafas 14 a 3 (p = 0.013); a tiempo 6 a 3 (p = 0.508); FA 23 a 9 (p = 0.020) | cumple |
| le gana a reglas v1 sin perder (estafas, a tiempo, FA) | a favor y en contra: estafas 2 a 5 (p = 0.453); a tiempo 2 a 6 (p = 0.289); FA 46 a 5 (p = 0.000) | cumple |
| límite inferior de a tiempo ≥ 50% | 28/36, 78 % [62–88] | cumple |
| límite inferior de estafas ≥ 50% | 39/46, 85 % [72–92] | cumple |
| #144 cae como mucho 20% en estafas avisadas | no corrió | — |

Contra reglas v2 (se informa, no es criterio): estafas 30 a 1 (p = 0.000); a tiempo 21 a 1 (p = 0.000); FA 23 a 13 (p = 0.132).

