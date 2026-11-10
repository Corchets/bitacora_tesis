# Humo del JSON de v4 cortado después de `alerta_sugerida`

Commit `decdff12d482760da8be893a7d94f4e59d19b3a2`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas). num_predict: 24.

Criterio, fijado antes de correr: con el JSON completo, la alerta termina a más tardar en el token 24 en las 48 líneas, y v4-corte lee riesgo y alerta en las 48. Si no pasa, no corre en los 150.

| tokens hasta la alerta (mín / mediana / máx) | líneas que alcanzan | v4-corte, líneas leídas | resultado |
|---|---|---|---|
| 23 / 23.0 / 23 (sin alerta: 0) | 48/48 | 48/48 | PASA |

Segunda consulta en 2 líneas de aviso:

- CV2-D-L-BANCO-001 L6: 597.6 ms  — 'No proporciones los últimos cuatro dígitos de tu cuenta, ya que esto puede ser usado para acceder a tus movimientos.' / 'bien con esos últimos cuatro dígitos ya ubico cuál mirar el movimiento figura hoy o ayer'
- SC-WA-CODE-01-e01 L3: 739.8 ms  — 'No debes resolver la activación de tu cuenta por teléfono; no compartas información ni realices acciones solicitadas por un desconocido.' / 'Para cancelar esa activación tenemos que resolverlo ahora.'

Líneas que no alcanzan:

