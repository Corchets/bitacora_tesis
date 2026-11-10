# Humo de los prompts cortados nuevos (etapa 2 de #143)

Commit `d127953fcc05389b54b26415fc047ad6f1865a35`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas). num_predict: 24.

Criterio, fijado antes de correr: con el JSON completo del prompt base, la alerta termina a más tardar en el token 24 en las 48 líneas, y el cortado lee riesgo y alerta en las 48. El que no pasa no corre.

| prompt | tokens hasta la alerta (mín / mediana / máx) | líneas que alcanzan | cortado, líneas leídas | mismo riesgo y alerta que el completo (dato) | resultado |
|---|---|---|---|---|---|
| `c-json-corte` | 23 / 23.0 / 23 (sin alerta: 0) | 48/48 | 48/48 | 43/48 | PASA |
| `v4-premisa-corte` | 23 / 23.0 / 23 (sin alerta: 0) | 48/48 | 48/48 | 43/48 | PASA |

`c-json-corte`: segunda consulta en 2 líneas de aviso:

- CV2-D-L-BANCO-001 L7: 567.7 ms  — 'Te están pidiendo que les digas un código que aparece en un débito para intentar acceder a tu cuenta.' / 'dice débito tarjeta pero abajo aparece un código que no entiendo'
- SC-WA-CODE-01-e01 L3: 575.5 ms  — 'Te están presionando para resolver un problema de activación de WhatsApp de forma inmediata, lo cual es una táctica común de estafa.' / 'Para cancelar esa activación tenemos que resolverlo ahora.'

`c-json-corte`: líneas que no alcanzan:


`v4-premisa-corte`: segunda consulta en 2 líneas de aviso:

- CV2-D-L-BANCO-001 L7: 606.7 ms  — 'No proporciones los últimos cuatro dígitos de tu cuenta, ya que esto puede ser usado para acceder a tus movimientos.' / 'bien con esos últimos cuatro dígitos ya ubico cuál mirar el movimiento figura hoy o ayer'
- SC-WA-CODE-01-e01 L3: 589.3 ms  — "No compartas ningún código o acción que te pidan para 'resolver' la activación de tu cuenta." / 'Para cancelar esa activación tenemos que resolverlo ahora.'

`v4-premisa-corte`: líneas que no alcanzan:

