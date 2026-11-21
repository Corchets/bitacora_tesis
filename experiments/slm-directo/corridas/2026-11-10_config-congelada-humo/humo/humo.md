# Humo de la configuración congelada de #143

Commit `58b09975fea15303ce61d5537dcd64a8f98757bd`. Casos: CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-L-BANCO-001, SC-WA-CODE-01-e01 (48 líneas), en todas las líneas. `c-json-corte-riesgo` corta con `num_predict` 14.

Criterio, fijado antes de correr: `c-json-corte-riesgo` lee el riesgo, con su coma, en las 48 líneas. Si no pasa, no corre nada más.

| riesgo leído | errores | tokens generados (mín / mediana / máx) | mismo riesgo que c-json-corte (dato) | riesgos con dos decimales (dato) | resultado |
|---|---|---|---|---|---|
| 48/48 | — | 14 / 14 / 14 | 43/48 | 1 | PASA |

Segunda consulta (motivo_c_corte.txt) en 3 primeros avisos:

- CV2-D-L-BANCO-001 L2 (riesgo 0.3): 744.7 ms  — 'No se debe compartir información sensible de la cuenta por teléfono sin verificar la identidad del llamante.' / 'te atiendo soy mara del sector de movimientos lo ves en la cuenta sueldo o en la caja de ahorro'
- CV2-D-V-ORGANISMO_PREVISIONAL-004 L5 (riesgo 0.3): 594.6 ms  — 'Desconfía de llamadas no solicitadas que prometen devoluciones o beneficios, ya que suelen ser intentos de phishing.' / 'Buenas te contacto de la oficina de regularización de pensiones por una devolución de aportes'
- SC-WA-CODE-01-e01 L1 (riesgo 0.3): 688.9 ms  — 'Los bancos y servicios legítimos rara vez inician llamadas sin previo aviso o sin verificar la identidad de manera más exhaustiva.' / 'Te llamo de soporte por la activación de tu cuenta de WhatsApp.'
