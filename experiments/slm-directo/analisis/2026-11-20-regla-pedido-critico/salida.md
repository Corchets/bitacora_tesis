## Desarrollo (alcance-140)

| detector | estafas avisadas | a tiempo | FA |
|---|---|---|---|
| modelo | 40/46 | 26/36 | 20/94 |
| regla | 14/46 | 10/36 | 0/94 |
| híbrido | 44/46 | 28/36 | 20/94 |

Lo que cambia la regla:

- estafa `CV2-D-V-SOPORTE-003`: no avisaba, la regla avisa en la l. 15 (pedido en la 11) por secreto: «ingresala en la ficha que te envié por mensaje así queda asociada al usuario»
- estafa `CV2-D-V-SOPORTE-005`: no avisaba, la regla avisa en la l. 18 (pedido en la 16) por secreto: «No la vas a decir, solo ingresala en la ventana de recuperación.»
- estafa `CV2-D-V-SOPORTE-006`: no avisaba, la regla avisa en la l. 15 (pedido en la 15) por secreto: «No ingresala en el campo y avisame si desaparece el botón gris»
- estafa `CV2-D-V-WHATSAPP-003`: no avisaba, la regla avisa en la l. 12 (pedido en la 12) por secreto: «Leeme los seis dígitos y te incorporo al grupo»

## Test reservado (100 estafas, 56 legítimas ENT-T)

| detector | estafas avisadas | a tiempo | FA |
|---|---|---|---|
| modelo | 73/100 | 53/80 | 15/56 |
| regla | 30/100 | 27/80 | 0/56 |
| híbrido | 80/100 | 63/80 | 15/56 |

Lo que cambia la regla: no se publica acá (son textos de `reserva/test`). Diez estafas pasan a avisar a tiempo y ninguna legítima suma aviso.

## Legítimas reales (33)

| detector | estafas avisadas | a tiempo | FA |
|---|---|---|---|
| modelo | — | — | 21/33 |
| regla | — | — | 0/33 |
| híbrido | — | — | 21/33 |

Lo que cambia la regla:

- nada

