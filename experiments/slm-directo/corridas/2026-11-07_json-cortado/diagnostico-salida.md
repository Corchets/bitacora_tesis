# JSON de v4 cortado: diagnóstico fuera del criterio

La línea de aviso es la misma en las dos corridas en los 150 casos; avisan 78. Modo operativo: 2134 líneas hasta el aviso inclusive, 2056 antes del aviso; 639 líneas después del aviso (solo en modo diagnóstico).

## 1. Latencia por línea antes del aviso (ms de pared en T4, p50 / p95)

| consulta | líneas | ms | tokens escritos | lectura del prompt | escritura | resto | ms por token escrito (p50) |
|---|---|---|---|---|---|---|---|
| primera consulta (cortado) | 2056 | 288 / 362 | 24 / 24 | 96 / 140 | 166 / 193 | 21 / 35 | 6.9 |
| JSON completo | 2056 | 393 / 482 | 41 / 41 | 95 / 142 | 277 / 307 | 21 / 36 | 6.8 |

## 2. La línea del aviso, según qué dispara la regla

La decisión de avisar se conoce al terminar la primera consulta; motivo y evidencia, al terminar la segunda. El JSON completo, sin streaming, da todo junto al final.

| disparo | líneas | cortado: decisión (1.ª) | motivo (2.ª) | cortado: total | completo | tokens del completo | motivo en el completo | motivo en el cortado |
|---|---|---|---|---|---|---|---|---|
| alerta escrita en true | 59 | 272 / 348 | 667 / 810 | 962 / 1121 | 832 / 1079 | 82 / 113 | 59/59 | 59/59 |
| solo riesgo ≥ 0,4 (alerta en false) | 19 | 264 / 328 | 607 / 939 | 899 / 1268 | 370 / 599 | 41 / 41 | 0/19 | 15/19 |
| todas | 78 | 269 / 336 | 661 / 811 | 938 / 1121 | 783 / 1032 | 80 / 110 | 59/78 | 74/78 |

Segunda consulta: 56 / 73 tokens escritos y 1092 / 1277 de prompt, contra 974 / 1159 de la primera. El CSV no guarda el desglose de Ollama de la segunda consulta.

## 3. Fallos de la segunda consulta y evidencias fuera del texto

- `CV2-D-L-BANCO-006` L9 (legitima, corpus_v2): riesgo 0.5, alerta escrita false, error `etapa2_alerta_sin_motivo`, evidencia en el texto —. Respuesta: `{ "evidencia": "", "motivo": "" }`
- `CV2-D-V-BANCO-007` L3 (vishing, corpus_v2): riesgo 0.4, alerta escrita false, error `etapa2_alerta_sin_motivo`, evidencia en el texto —. Respuesta: `{ "evidencia": "No hay un pedido explícito de datos, claves o acciones que cumplan los criterios de alerta.", "motivo": "" }`
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` L13 (vishing, corpus_v2): riesgo 0.5, alerta escrita true, error `—`, evidencia en el texto false. Respuesta: `{ "evidencia": "En la ficha aparece un número de documento que termina en 6. Para que el sistema abra el detalle, me faltan los dígitos del medio.", "motivo": "No le des los dígitos faltantes del DNI, ya que te están pidiendo información personal para acceder a tu historial." }`
- `SC-ORG-BENEFICIO-01-e01` L5 (vishing, piloto_escrito): riesgo 0.4, alerta escrita false, error `etapa2_alerta_sin_motivo`, evidencia en el texto —. Respuesta: `{ "evidencia": "", "motivo": "" }`
- `TR-06-banco-alerta-legitima` L4 (legitima_dificil, trampa): riesgo 0.4, alerta escrita false, error `etapa2_alerta_sin_motivo`, evidencia en el texto —. Respuesta: `{ "evidencia": "", "motivo": "" }`

## 4. Riesgo escrito igual, antes y después del aviso

«Hasta el aviso» incluye la línea del aviso; «después» son las líneas que solo corren en modo diagnóstico. La línea de aviso es la de esta corrida en los dos casos, también para las corridas de la etapa 1.

| corridas | sesión | hasta el aviso | después del aviso |
|---|---|---|---|
| v4-corte / v4 completo | misma sesión (hoy) | 95.0% (2027/2134) | 88.3% (564/639) |
| v4-L / su repetición | misma sesión (etapa 1) | 96.4% (2055/2132) | 96.2% (615/639) |
| v4-L / v4-corte | sesiones distintas | 94.5% (2017/2134) | 86.1% (550/639) |
| v4-L / v4 completo | sesiones distintas | 94.3% (2012/2134) | 85.3% (545/639) |

Riesgo distinto en 182 líneas: el cortado escribe más en 103 y menos en 79; 25 cruzan 0,4. Pares más comunes (cortado, completo): [((0.1, 0.2), 26), ((0.2, 0.1), 26), ((0.1, 0.0), 18), ((0.2, 0.3), 16), ((0.3, 0.2), 15), ((0.0, 0.1), 14)].

