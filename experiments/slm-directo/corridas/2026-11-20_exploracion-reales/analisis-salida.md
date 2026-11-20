# #52, exploración con los conjuntos reales — análisis offline

Posterior a la evaluación final: no la reemplaza. Referencia: `base` (`c-consejos-corte-riesgo`) con el primer aviso, corrida en esta misma sesión. «Confirmación» es riesgo ≥ 0,5, o el segundo riesgo ≥ 0,3.

## Humo de formato

| prompt | leídas | errores | resultado |
|---|---|---|---|
| `c-consejos-corte-riesgo` | 48/48 | — | PASA |
| `p-lista-corte-riesgo` | 48/48 | — | PASA |
| `p-escalera-corte-riesgo` | 48/48 | — | PASA |
| `p-niveles-corte-riesgo` | 48/48 | — | PASA |
| `c-rumbo-corte-riesgo` | 48/48 | — | PASA |
| `p-sino-corte-riesgo` | 48/48 | — | PASA |
| `p-minimo-corte-riesgo` | 48/48 | — | PASA |

## Control de las corridas

| tanda | corrida | commit | líneas de OTRA inválidas | control |
|---|---|---|---|---|
| externo | base | 7c52850c7d | 2359/4193 {'contexto_excedido': 2359} | bien |
| externo | p-lista | 7c52850c7d | 2148/4193 {'contexto_excedido': 2148} | bien |
| externo | p-escalera | 7c52850c7d | 2379/4193 {'contexto_excedido': 2379} | bien |
| externo | p-niveles | 7c52850c7d | 2232/4193 {'contexto_excedido': 2232} | bien |
| externo | c-rumbo | 7c52850c7d | 2384/4193 {'contexto_excedido': 2384} | bien |
| externo | p-sino | 7c52850c7d | 2225/4193 {'contexto_excedido': 2225} | bien |
| externo | p-minimo | 7c52850c7d | 2089/4193 {'contexto_excedido': 2089} | bien |
| legitimas_reales | base | 7c52850c7d | 0/387 | bien |
| legitimas_reales | p-lista | 7c52850c7d | 0/387 | bien |
| legitimas_reales | p-escalera | 7c52850c7d | 0/387 | bien |
| legitimas_reales | p-niveles | 7c52850c7d | 0/387 | bien |
| legitimas_reales | c-rumbo | 7c52850c7d | 0/387 | bien |
| legitimas_reales | p-sino | 7c52850c7d | 0/387 | bien |
| legitimas_reales | p-minimo | 7c52850c7d | 0/387 | bien |
| desarrollo | base | 7c52850c7d | 0/1313 | bien |
| desarrollo | p-lista | 7c52850c7d | 0/1313 | bien |
| desarrollo | p-escalera | 7c52850c7d | 0/1313 | bien |
| desarrollo | p-niveles | 7c52850c7d | 0/1313 | bien |
| desarrollo | c-rumbo | 7c52850c7d | 0/1313 | bien |
| desarrollo | p-sino | 7c52850c7d | 0/1313 | bien |
| desarrollo | p-minimo | 7c52850c7d | 0/1313 | bien |
| zona_gris | base | 7c52850c7d | 44/1139 {'contexto_excedido': 44} | bien |
| test_reservado | base | 7c52850c7d | 0/1786 | bien |

# Fase 1: lo que usa la regla

## Estafas reales coreanas (#144)

| prompt · política | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA |
|---|---|---|---|---|---|
| `base` · primer aviso | 33/33 | 25/27 | 27/27 | 16/16 | — |
| `base` · confirmación | 33/33 | 25/27 | 26/27 | 16/16 | — |
| `p-lista` · primer aviso | 30/33 | 18/27 | 21/27 | 15/16 | — |
| `p-escalera` · primer aviso | 32/33 | 20/27 | 22/27 | 16/16 | — |
| `p-niveles` · primer aviso | 32/33 | 22/27 | 24/27 | 15/16 | — |
| `c-rumbo` · primer aviso | 33/33 | 25/27 | 27/27 | 16/16 | — |
| `p-sino` · primer aviso | 17/33 | 11/27 | 11/27 | 8/16 | — |
| `p-minimo` · primer aviso | 32/33 | 21/27 | 23/27 | 16/16 | — |
| `p-lista` · confirmación | 30/33 | 18/27 | 21/27 | 15/16 | — |
| `p-escalera` · confirmación | 32/33 | 19/27 | 20/27 | 16/16 | — |
| `p-niveles` · confirmación | 32/33 | 22/27 | 24/27 | 15/16 | — |
| `c-rumbo` · confirmación | 33/33 | 25/27 | 26/27 | 16/16 | — |
| `p-sino` · confirmación | 17/33 | 11/27 | 11/27 | 8/16 | — |
| `p-minimo` · confirmación | 32/33 | 21/27 | 23/27 | 16/16 | — |

## Legítimas reales (CallCenterEN, las 33)

| prompt · política | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA |
|---|---|---|---|---|---|
| `base` · primer aviso | — | — | — | — | 23/33 |
| `base` · confirmación | — | — | — | — | 21/33 |
| `p-lista` · primer aviso | — | — | — | — | 17/33 |
| `p-escalera` · primer aviso | — | — | — | — | 21/33 |
| `p-niveles` · primer aviso | — | — | — | — | 12/33 |
| `c-rumbo` · primer aviso | — | — | — | — | 26/33 |
| `p-sino` · primer aviso | — | — | — | — | 8/33 |
| `p-minimo` · primer aviso | — | — | — | — | 19/33 |
| `p-lista` · confirmación | — | — | — | — | 17/33 |
| `p-escalera` · confirmación | — | — | — | — | 18/33 |
| `p-niveles` · confirmación | — | — | — | — | 12/33 |
| `c-rumbo` · confirmación | — | — | — | — | 23/33 |
| `p-sino` · confirmación | — | — | — | — | 8/33 |
| `p-minimo` · confirmación | — | — | — | — | 19/33 |

## Desarrollo (alcance-140)

| prompt · política | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA |
|---|---|---|---|---|---|
| `base` · primer aviso | 43/46 | 18/36 | 29/36 | 14/15 | 20/94 |
| `base` · confirmación | 38/46 | 15/36 | 18/36 | 13/15 | 14/94 |
| `p-lista` · primer aviso | 36/46 | 19/36 | 31/36 | 15/15 | 34/94 |
| `p-escalera` · primer aviso | 32/46 | 17/36 | 28/36 | 14/15 | 28/94 |
| `p-niveles` · primer aviso | 25/46 | 15/36 | 20/36 | 8/15 | 16/94 |
| `c-rumbo` · primer aviso | 44/46 | 22/36 | 29/36 | 15/15 | 28/94 |
| `p-sino` · primer aviso | 22/46 | 7/36 | 17/36 | 12/15 | 14/94 |
| `p-minimo` · primer aviso | 39/46 | 21/36 | 31/36 | 15/15 | 48/94 |
| `p-lista` · confirmación | 36/46 | 19/36 | 31/36 | 15/15 | 34/94 |
| `p-escalera` · confirmación | 30/46 | 7/36 | 17/36 | 13/15 | 19/94 |
| `p-niveles` · confirmación | 25/46 | 15/36 | 20/36 | 8/15 | 16/94 |
| `c-rumbo` · confirmación | 41/46 | 15/36 | 22/36 | 12/15 | 21/94 |
| `p-sino` · confirmación | 22/46 | 7/36 | 17/36 | 12/15 | 14/94 |
| `p-minimo` · confirmación | 39/46 | 21/36 | 31/36 | 15/15 | 48/94 |

## La regla

Referencia: coreanas 33, a tiempo 27, FA reales 23; en desarrollo, a tiempo 29 y FA 20.

| candidato | resultado | por qué | a tiempo en desarrollo | FA en desarrollo | costo alto en el test |
|---|---|---|---|---|---|
| `base` · confirmación | no sirve | las FA reales cambian -2, y tienen que bajar 7 o más | -11 | -6 | alto: test a tiempo -12 |
| `p-lista` · primer aviso | no sirve | pierde 3 coreanas; pierde 6 coreanas a tiempo; las FA reales cambian -6, y tienen que bajar 7 o más | +2 | +14 | — |
| `p-escalera` · primer aviso | no sirve | pierde 5 coreanas a tiempo; las FA reales cambian -2, y tienen que bajar 7 o más | -1 | +8 | — |
| `p-niveles` · primer aviso | no sirve | pierde 3 coreanas a tiempo | -9 | -4 | — |
| `c-rumbo` · primer aviso | no sirve | las FA reales cambian +3, y tienen que bajar 7 o más | +0 | +8 | — |
| `p-sino` · primer aviso | no sirve | pierde 16 coreanas; pierde 16 coreanas a tiempo | -12 | -6 | — |
| `p-minimo` · primer aviso | no sirve | pierde 4 coreanas a tiempo; las FA reales cambian -4, y tienen que bajar 7 o más | +2 | +28 | — |
| `p-lista` · confirmación | no sirve | pierde 3 coreanas; pierde 6 coreanas a tiempo; las FA reales cambian -6, y tienen que bajar 7 o más | +2 | +14 | — |
| `p-escalera` · confirmación | no sirve | pierde 7 coreanas a tiempo; las FA reales cambian -5, y tienen que bajar 7 o más | -12 | -1 | — |
| `p-niveles` · confirmación | no sirve | pierde 3 coreanas a tiempo | -9 | -4 | — |
| `c-rumbo` · confirmación | no sirve | las FA reales cambian +0, y tienen que bajar 7 o más | -7 | +1 | — |
| `p-sino` · confirmación | no sirve | pierde 16 coreanas; pierde 16 coreanas a tiempo | -12 | -6 | — |
| `p-minimo` · confirmación | no sirve | pierde 4 coreanas a tiempo; las FA reales cambian -4, y tienen que bajar 7 o más | +2 | +28 | — |

**Resultado: no sirve ninguno. Queda la configuración de la evaluación final.**

**La vara que ya existe, `v4-corte` en la evaluación final:** coreanas 33/33, a tiempo 23/27; FA reales 10/33; zona gris 20/42; desarrollo 28/46, a tiempo 25/36 y FA 42/94; test 64/100, a tiempo 50/80 y FA 15/56.

# Fase 2: solo para la base y los prompts que sirven

## Zona gris de Medicare (avisos, no son FA)

| prompt · política | avisos |
|---|---|
| `base` · primer aviso | 30/42 |
| `base` · confirmación | 28/42 |

## Test reservado (vista principal)

| prompt · política | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA |
|---|---|---|---|---|---|
| `base` · primer aviso | 76/100 | 43/80 | 56/80 | 25/32 | 15/56 |
| `base` · confirmación | 71/100 | 30/80 | 44/80 | 22/32 | 15/56 |

# Aparte, solo para mirar

## Desarrollo: FA en las 75 que no deberían avisar (etiquetas de producto)

| prompt · política | FA estrictas |
|---|---|
| `base` · primer aviso | 8/75 |
| `base` · confirmación | 3/75 |
| `p-lista` · primer aviso | 18/75 |
| `p-escalera` · primer aviso | 13/75 |
| `p-niveles` · primer aviso | 1/75 |
| `c-rumbo` · primer aviso | 13/75 |
| `p-sino` · primer aviso | 7/75 |
| `p-minimo` · primer aviso | 30/75 |
| `p-lista` · confirmación | 18/75 |
| `p-escalera` · confirmación | 9/75 |
| `p-niveles` · confirmación | 1/75 |
| `c-rumbo` · confirmación | 9/75 |
| `p-sino` · confirmación | 7/75 |
| `p-minimo` · confirmación | 30/75 |

## Qué valores escribe cada prompt (porcentaje de las consultas válidas)

| tanda | prompt | consultas | valores |
|---|---|---|---|
| Estafas reales coreanas (#144) | base | 1834 | 0.1: 1 % · 0.2: 30 % · 0.3: 26 % · 0.4: 2 % · 0.5: 5 % · 0.6: 2 % · 0.7: 11 % · 0.8: 12 % · 0.85: 6 % · 0.9: 4 % · 0.95: 1 % |
| Estafas reales coreanas (#144) | p-lista | 2045 | 0: 51 % · 0.5: 46 % · 0.9: 3 % |
| Estafas reales coreanas (#144) | p-escalera | 1814 | 0: 7 % · 0.1: 29 % · 0.2: 7 % · 0.3: 56 % · 0.5: 2 % |
| Estafas reales coreanas (#144) | p-niveles | 1961 | 0: 3 % · 0.1: 39 % · 0.5: 43 % · 0.9: 16 % |
| Estafas reales coreanas (#144) | c-rumbo | 1809 | 0.1: 1 % · 0.2: 25 % · 0.3: 25 % · 0.4: 1 % · 0.5: 13 % · 0.6: 1 % · 0.7: 12 % · 0.8: 12 % · 0.85: 4 % · 0.9: 4 % · 0.95: 1 % |
| Estafas reales coreanas (#144) | p-sino | 1968 | 0.1: 91 % · 0.9: 9 % |
| Estafas reales coreanas (#144) | p-minimo | 2104 | 0: 39 % · 0.5: 54 % · 0.9: 7 % |
| Legítimas reales (CallCenterEN, las 33) | base | 387 | 0.1: 15 % · 0.2: 55 % · 0.3: 26 % · 0.5: 1 % · 0.6: 2 % · 0.7: 1 % · 0.8: 1 % |
| Legítimas reales (CallCenterEN, las 33) | p-lista | 387 | 0: 86 % · 0.5: 11 % · 0.9: 4 % |
| Legítimas reales (CallCenterEN, las 33) | p-escalera | 387 | 0: 16 % · 0.1: 63 % · 0.2: 2 % · 0.3: 17 % · 0.5: 3 % |
| Legítimas reales (CallCenterEN, las 33) | p-niveles | 387 | 0: 13 % · 0.1: 75 % · 0.5: 4 % · 0.9: 8 % |
| Legítimas reales (CallCenterEN, las 33) | c-rumbo | 387 | 0.1: 12 % · 0.2: 50 % · 0.3: 31 % · 0.5: 3 % · 0.6: 1 % · 0.7: 3 % · 0.8: 1 % |
| Legítimas reales (CallCenterEN, las 33) | p-sino | 387 | 0.1: 96 % · 0.9: 4 % |
| Legítimas reales (CallCenterEN, las 33) | p-minimo | 387 | 0: 84 % · 0.5: 9 % · 0.9: 7 % |
| Desarrollo (alcance-140) | base | 1313 | 0: 1 % · 0.1: 34 % · 0.2: 37 % · 0.3: 20 % · 0.5: 2 % · 0.6: 3 % · 0.7: 1 % · 0.8: 1 % |
| Desarrollo (alcance-140) | p-lista | 1313 | 0: 77 % · 0.5: 21 % · 0.9: 2 % |
| Desarrollo (alcance-140) | p-escalera | 1313 | 0: 20 % · 0.1: 54 % · 0.2: 6 % · 0.3: 19 % · 0.5: 1 % |
| Desarrollo (alcance-140) | p-niveles | 1313 | 0: 9 % · 0.1: 72 % · 0.5: 16 % · 0.9: 4 % |
| Desarrollo (alcance-140) | c-rumbo | 1313 | 0: 1 % · 0.1: 29 % · 0.2: 37 % · 0.3: 22 % · 0.5: 4 % · 0.6: 3 % · 0.7: 2 % · 0.8: 1 % · 0.9: 1 % |
| Desarrollo (alcance-140) | p-sino | 1313 | 0.1: 93 % · 0.9: 7 % |
| Desarrollo (alcance-140) | p-minimo | 1313 | 0: 66 % · 0.5: 29 % · 0.9: 5 % |
| Zona gris de Medicare (avisos, no son FA) | base | 1095 | 0.1: 12 % · 0.2: 51 % · 0.3: 29 % · 0.5: 1 % · 0.6: 1 % · 0.7: 4 % · 0.8: 1 % |
| Test reservado (vista principal) | base | 1786 | 0: 1 % · 0.05: 1 % · 0.1: 28 % · 0.2: 38 % · 0.3: 24 % · 0.5: 2 % · 0.6: 3 % · 0.7: 2 % · 0.8: 1 % |

## Otros cortes, sin esperar confirmación (estafas avisadas · a tiempo · FA o avisos)

| tanda | prompt | riesgo ≥ 0,3 | riesgo ≥ 0,5 | riesgo ≥ 0,7 |
|---|---|---|---|---|
| Estafas reales coreanas (#144) | base | 33/33 · 27/27 | 28/33 · 17/27 | 26/33 · 15/27 |
| Estafas reales coreanas (#144) | p-lista | 30/33 · 21/27 | 30/33 · 21/27 | 6/33 · 4/27 |
| Estafas reales coreanas (#144) | p-escalera | 32/33 · 22/27 | 2/33 · 0/27 | 0/33 · 0/27 |
| Estafas reales coreanas (#144) | p-niveles | 32/33 · 24/27 | 32/33 · 24/27 | 22/33 · 12/27 |
| Estafas reales coreanas (#144) | c-rumbo | 33/33 · 27/27 | 29/33 · 20/27 | 25/33 · 16/27 |
| Estafas reales coreanas (#144) | p-sino | 17/33 · 11/27 | 17/33 · 11/27 | 17/33 · 11/27 |
| Estafas reales coreanas (#144) | p-minimo | 32/33 · 23/27 | 32/33 · 23/27 | 14/33 · 9/27 |
| Legítimas reales (CallCenterEN, las 33) | base | 23/33 | 5/33 | 3/33 |
| Legítimas reales (CallCenterEN, las 33) | p-lista | 17/33 | 17/33 | 6/33 |
| Legítimas reales (CallCenterEN, las 33) | p-escalera | 21/33 | 4/33 | 0/33 |
| Legítimas reales (CallCenterEN, las 33) | p-niveles | 12/33 | 12/33 | 9/33 |
| Legítimas reales (CallCenterEN, las 33) | c-rumbo | 26/33 | 9/33 | 6/33 |
| Legítimas reales (CallCenterEN, las 33) | p-sino | 8/33 | 8/33 | 8/33 |
| Legítimas reales (CallCenterEN, las 33) | p-minimo | 19/33 | 19/33 | 5/33 |
| Desarrollo (alcance-140) | base | 43/46 · 29/36 · 20/94 | 15/46 · 12/36 · 8/94 | 6/46 · 3/36 · 4/94 |
| Desarrollo (alcance-140) | p-lista | 36/46 · 31/36 · 34/94 | 36/46 · 31/36 · 34/94 | 10/46 · 5/36 · 3/94 |
| Desarrollo (alcance-140) | p-escalera | 32/46 · 28/36 · 28/94 | 3/46 · 1/36 · 0/94 | 0/46 · 0/36 · 0/94 |
| Desarrollo (alcance-140) | p-niveles | 25/46 · 20/36 · 16/94 | 25/46 · 20/36 · 16/94 | 11/46 · 7/36 · 4/94 |
| Desarrollo (alcance-140) | c-rumbo | 44/46 · 29/36 · 28/94 | 22/46 · 15/36 · 13/94 | 11/46 · 8/36 · 7/94 |
| Desarrollo (alcance-140) | p-sino | 22/46 · 17/36 · 14/94 | 22/46 · 17/36 · 14/94 | 22/46 · 17/36 · 14/94 |
| Desarrollo (alcance-140) | p-minimo | 39/46 · 31/36 · 48/94 | 39/46 · 31/36 · 48/94 | 13/46 · 10/36 · 12/94 |
| Zona gris de Medicare (avisos, no son FA) | base | 30/42 | 12/42 | 8/42 |
| Test reservado (vista principal) | base | 76/100 · 56/80 · 15/56 | 37/100 · 26/80 · 6/56 | 13/100 · 10/80 · 2/56 |

## Cuántas veces baja el riesgo de una consulta a la siguiente (ruido, si la escala es acumulada)

| tanda | prompt | bajadas | de ≥ 0,3 a menos |
|---|---|---|---|
| Estafas reales coreanas (#144) | base | 247/1801 | 86 |
| Estafas reales coreanas (#144) | p-lista | 153/2012 | 144 |
| Estafas reales coreanas (#144) | p-escalera | 96/1781 | 48 |
| Estafas reales coreanas (#144) | p-niveles | 112/1928 | 82 |
| Estafas reales coreanas (#144) | c-rumbo | 275/1776 | 93 |
| Estafas reales coreanas (#144) | p-sino | 41/1935 | 41 |
| Estafas reales coreanas (#144) | p-minimo | 152/2071 | 125 |
| Legítimas reales (CallCenterEN, las 33) | base | 45/354 | 26 |
| Legítimas reales (CallCenterEN, las 33) | p-lista | 18/354 | 15 |
| Legítimas reales (CallCenterEN, las 33) | p-escalera | 18/354 | 6 |
| Legítimas reales (CallCenterEN, las 33) | p-niveles | 21/354 | 11 |
| Legítimas reales (CallCenterEN, las 33) | c-rumbo | 45/354 | 19 |
| Legítimas reales (CallCenterEN, las 33) | p-sino | 7/354 | 7 |
| Legítimas reales (CallCenterEN, las 33) | p-minimo | 20/354 | 20 |
| Desarrollo (alcance-140) | base | 154/1173 | 40 |
| Desarrollo (alcance-140) | p-lista | 62/1173 | 52 |
| Desarrollo (alcance-140) | p-escalera | 100/1173 | 41 |
| Desarrollo (alcance-140) | p-niveles | 44/1173 | 26 |
| Desarrollo (alcance-140) | c-rumbo | 164/1173 | 45 |
| Desarrollo (alcance-140) | p-sino | 33/1173 | 33 |
| Desarrollo (alcance-140) | p-minimo | 76/1173 | 60 |
| Zona gris de Medicare (avisos, no son FA) | base | 87/1053 | 43 |
| Test reservado (vista principal) | base | 229/1630 | 76 |

## Cuántas consultas con riesgo ≥ 0,3 tiene cada llamada (0, 1, 2, 3, 4, 5 o más)

| tanda | grupo | prompt | llamadas con 0 · 1 · 2 · 3 · 4 · 5+ |
|---|---|---|---|
| Estafas reales coreanas (#144) | estafas | base | 0 · 0 · 0 · 1 · 0 · 32 |
| Estafas reales coreanas (#144) | estafas | p-lista | 3 · 0 · 0 · 1 · 1 · 28 |
| Estafas reales coreanas (#144) | estafas | p-escalera | 1 · 0 · 0 · 0 · 0 · 32 |
| Estafas reales coreanas (#144) | estafas | p-niveles | 1 · 1 · 1 · 2 · 0 · 28 |
| Estafas reales coreanas (#144) | estafas | c-rumbo | 0 · 0 · 0 · 0 · 0 · 33 |
| Estafas reales coreanas (#144) | estafas | p-sino | 16 · 5 · 1 · 1 · 0 · 10 |
| Estafas reales coreanas (#144) | estafas | p-minimo | 1 · 0 · 0 · 1 · 0 · 31 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | base | 10 · 2 · 4 · 1 · 2 · 14 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-lista | 16 · 5 · 1 · 4 · 2 · 5 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-escalera | 12 · 3 · 5 · 4 · 3 · 6 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-niveles | 21 · 1 · 4 · 2 · 1 · 4 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | c-rumbo | 7 · 3 · 3 · 3 · 0 · 17 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-sino | 25 · 5 · 1 · 1 · 0 · 1 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-minimo | 14 · 6 · 4 · 2 · 3 · 4 |
| Desarrollo (alcance-140) | estafas | base | 3 · 5 · 1 · 4 · 3 · 30 |
| Desarrollo (alcance-140) | legítimas | base | 74 · 6 · 4 · 2 · 1 · 7 |
| Desarrollo (alcance-140) | estafas | p-lista | 10 · 2 · 2 · 6 · 4 · 22 |
| Desarrollo (alcance-140) | legítimas | p-lista | 60 · 14 · 3 · 5 · 6 · 6 |
| Desarrollo (alcance-140) | estafas | p-escalera | 14 · 2 · 3 · 2 · 4 · 21 |
| Desarrollo (alcance-140) | legítimas | p-escalera | 66 · 9 · 3 · 6 · 3 · 7 |
| Desarrollo (alcance-140) | estafas | p-niveles | 21 · 1 · 4 · 3 · 2 · 15 |
| Desarrollo (alcance-140) | legítimas | p-niveles | 78 · 2 · 2 · 0 · 5 · 7 |
| Desarrollo (alcance-140) | estafas | c-rumbo | 2 · 3 · 2 · 5 · 2 · 32 |
| Desarrollo (alcance-140) | legítimas | c-rumbo | 66 · 8 · 3 · 7 · 2 · 8 |
| Desarrollo (alcance-140) | estafas | p-sino | 24 · 4 · 5 · 1 · 4 · 8 |
| Desarrollo (alcance-140) | legítimas | p-sino | 80 · 10 · 3 · 1 · 0 · 0 |
| Desarrollo (alcance-140) | estafas | p-minimo | 7 · 0 · 4 · 4 · 4 · 27 |
| Desarrollo (alcance-140) | legítimas | p-minimo | 46 · 8 · 5 · 8 · 8 · 19 |
| Zona gris de Medicare (avisos, no son FA) | legítimas | base | 12 · 2 · 0 · 3 · 1 · 24 |
| Test reservado (vista principal) | estafas | base | 24 · 5 · 5 · 5 · 4 · 57 |
| Test reservado (vista principal) | legítimas | base | 41 · 0 · 3 · 1 · 1 · 10 |

