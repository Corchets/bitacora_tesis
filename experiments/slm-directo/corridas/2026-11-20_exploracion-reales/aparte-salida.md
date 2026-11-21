# #52, exploración con los conjuntos reales — cuentas aparte

Para leer el resultado; no cambian la regla. Aviso = riesgo ≥ 0,3 salvo que se diga otra cosa.

## La misma configuración, dos sesiones de Colab

Evaluación final (2026-11-19) y `base` de la exploración (2026-11-20): mismo prompt, modelo, semilla, Ollama y conjuntos. Cambia cómo se corrió: la evaluación final pasó cada conjunto entero y cortó cada llamada en su primer aviso; la exploración pasó solo la vista principal y todas las líneas. La cifra que vale es la de la evaluación final; la diferencia mide cuánto se mueve el resultado al repetir.

| conjunto | cifra | evaluación final | exploración | diferencia | llamadas que cambian |
|---|---|---|---|---|---|
| Estafas reales coreanas (#144) | estafas | 33/33 | 33/33 | +0 | 0 |
| Estafas reales coreanas (#144) | antes del pedido | 25/27 | 25/27 | +0 | 0 |
| Estafas reales coreanas (#144) | a tiempo | 27/27 | 27/27 | +0 | 0 |
| Estafas reales coreanas (#144) | antes del cumplimiento | 16/16 | 16/16 | +0 | 0 |
| Legítimas reales (CallCenterEN, las 33) | FA | 21/33 | 23/33 | +2 | 4 |
| Desarrollo (alcance-140) | estafas | 40/46 | 43/46 | +3 | 3 |
| Desarrollo (alcance-140) | antes del pedido | 16/36 | 18/36 | +2 | 2 |
| Desarrollo (alcance-140) | a tiempo | 26/36 | 29/36 | +3 | 3 |
| Desarrollo (alcance-140) | antes del cumplimiento | 13/15 | 14/15 | +1 | 1 |
| Desarrollo (alcance-140) | FA | 20/94 | 20/94 | +0 | 0 |
| Zona gris de Medicare (avisos, no son FA) | FA | 32/42 | 30/42 | -2 | 2 |
| Test reservado (vista principal) | estafas | 73/100 | 76/100 | +3 | 3 |
| Test reservado (vista principal) | antes del pedido | 37/80 | 43/80 | +6 | 6 |
| Test reservado (vista principal) | a tiempo | 53/80 | 56/80 | +3 | 5 |
| Test reservado (vista principal) | antes del cumplimiento | 24/32 | 25/32 | +1 | 1 |
| Test reservado (vista principal) | FA | 15/56 | 15/56 | +0 | 0 |

Consulta por consulta (las líneas de OTRA válidas en las dos pasadas):

| conjunto | consultas válidas, final | consultas válidas, exploración | en las dos | mismo riesgo | cruzan el 0,3 | sube en la exploración | baja en la exploración | cambios de 0,1 o menos | mismo conjunto |
|---|---|---|---|---|---|---|---|---|---|
| Estafas reales coreanas (#144) | 205 | 1834 | 205 | 187/205 (91 %) | 15/205 (7 %) | 12 | 6 | 16 | sí |
| Legítimas reales (CallCenterEN, las 33) | 254 | 387 | 254 | 232/254 (91 %) | 11/254 (4 %) | 20 | 2 | 21 | sí |
| Desarrollo (alcance-140) | 925 | 1313 | 925 | 853/925 (92 %) | 15/925 (2 %) | 59 | 13 | 71 | sí |
| Zona gris de Medicare (avisos, no son FA) | 526 | 1095 | 526 | 490/526 (93 %) | 10/526 (2 %) | 9 | 27 | 34 | sí |
| Test reservado (vista principal) | 1150 | 1786 | 1150 | 1060/1150 (92 %) | 24/1150 (2 %) | 68 | 22 | 86 | sí |

Llamada por llamada (primer aviso):

| conjunto | llamadas | avisa en una pasada y en la otra no | avisa en las dos, en otra línea |
|---|---|---|---|
| Estafas reales coreanas (#144) | 33 | 0 | 9 |
| Legítimas reales (CallCenterEN, las 33) | 33 | 4 | 5 |
| Desarrollo (alcance-140) | 140 | 3 | 7 |
| Zona gris de Medicare (avisos, no son FA) | 42 | 2 | 8 |
| Test reservado (vista principal) | 156 | 3 | 18 |

## Cuántas consultas válidas de OTRA tiene cada llamada (base)

Con el primer aviso, una llamada con más consultas tiene más oportunidades de avisar.

| conjunto | grupo | llamadas | mínimo | mediana | máximo |
|---|---|---|---|---|---|
| Estafas reales coreanas (#144) | estafas | 33 | 33 | 56 | 77 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | 33 | 6 | 11 | 19 |
| Desarrollo (alcance-140) | estafas | 46 | 10 | 11 | 19 |
| Desarrollo (alcance-140) | legítimas | 94 | 3 | 7 | 18 |
| Zona gris de Medicare (avisos, no son FA) | legítimas | 42 | 10 | 24 | 48 |
| Test reservado (vista principal) | estafas | 100 | 8 | 10 | 15 |
| Test reservado (vista principal) | legítimas | 56 | 10 | 12 | 19 |

## Llamadas que ya avisaron en las primeras consultas (riesgo ≥ 0,3)

Iguala el largo: compara estafas y legítimas con la misma cantidad de consultas.

| conjunto | grupo | prompt | en 3 | en 5 | en 8 | en 12 | en 20 | en todas |
|---|---|---|---|---|---|---|---|---|
| Estafas reales coreanas (#144) | estafas | base | 11/33 | 16/33 | 24/33 | 28/33 | 33/33 | 33/33 |
| Estafas reales coreanas (#144) | estafas | p-lista | 7/33 | 10/33 | 12/33 | 17/33 | 20/33 | 30/33 |
| Estafas reales coreanas (#144) | estafas | p-escalera | 2/33 | 4/33 | 5/33 | 11/33 | 17/33 | 32/33 |
| Estafas reales coreanas (#144) | estafas | p-niveles | 8/33 | 14/33 | 23/33 | 24/33 | 27/33 | 32/33 |
| Estafas reales coreanas (#144) | estafas | c-rumbo | 15/33 | 22/33 | 30/33 | 33/33 | 33/33 | 33/33 |
| Estafas reales coreanas (#144) | estafas | p-sino | 4/33 | 5/33 | 7/33 | 9/33 | 11/33 | 17/33 |
| Estafas reales coreanas (#144) | estafas | p-minimo | 12/33 | 17/33 | 19/33 | 22/33 | 23/33 | 32/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | base | 6/33 | 15/33 | 18/33 | 22/33 | 23/33 | 23/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-lista | 2/33 | 5/33 | 13/33 | 15/33 | 17/33 | 17/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-escalera | 0/33 | 2/33 | 13/33 | 19/33 | 21/33 | 21/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-niveles | 4/33 | 8/33 | 10/33 | 11/33 | 12/33 | 12/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | c-rumbo | 6/33 | 16/33 | 22/33 | 25/33 | 26/33 | 26/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-sino | 0/33 | 0/33 | 4/33 | 5/33 | 8/33 | 8/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-minimo | 4/33 | 8/33 | 14/33 | 16/33 | 19/33 | 19/33 |
| Desarrollo (alcance-140) | estafas | base | 16/46 | 27/46 | 39/46 | 42/46 | 43/46 | 43/46 |
| Desarrollo (alcance-140) | estafas | p-lista | 5/46 | 17/46 | 31/46 | 34/46 | 36/46 | 36/46 |
| Desarrollo (alcance-140) | estafas | p-escalera | 1/46 | 12/46 | 26/46 | 30/46 | 32/46 | 32/46 |
| Desarrollo (alcance-140) | estafas | p-niveles | 16/46 | 20/46 | 24/46 | 25/46 | 25/46 | 25/46 |
| Desarrollo (alcance-140) | estafas | c-rumbo | 19/46 | 29/46 | 39/46 | 43/46 | 44/46 | 44/46 |
| Desarrollo (alcance-140) | estafas | p-sino | 1/46 | 6/46 | 15/46 | 20/46 | 22/46 | 22/46 |
| Desarrollo (alcance-140) | estafas | p-minimo | 12/46 | 25/46 | 33/46 | 37/46 | 39/46 | 39/46 |
| Desarrollo (alcance-140) | legítimas | base | 12/94 | 14/94 | 19/94 | 20/94 | 20/94 | 20/94 |
| Desarrollo (alcance-140) | legítimas | p-lista | 25/94 | 27/94 | 33/94 | 34/94 | 34/94 | 34/94 |
| Desarrollo (alcance-140) | legítimas | p-escalera | 14/94 | 19/94 | 27/94 | 28/94 | 28/94 | 28/94 |
| Desarrollo (alcance-140) | legítimas | p-niveles | 12/94 | 12/94 | 15/94 | 16/94 | 16/94 | 16/94 |
| Desarrollo (alcance-140) | legítimas | c-rumbo | 19/94 | 24/94 | 27/94 | 28/94 | 28/94 | 28/94 |
| Desarrollo (alcance-140) | legítimas | p-sino | 1/94 | 5/94 | 10/94 | 14/94 | 14/94 | 14/94 |
| Desarrollo (alcance-140) | legítimas | p-minimo | 32/94 | 40/94 | 46/94 | 48/94 | 48/94 | 48/94 |

## Llamadas que ya avisaron en las primeras consultas (riesgo ≥ 0,5)

Iguala el largo: compara estafas y legítimas con la misma cantidad de consultas.

| conjunto | grupo | prompt | en 3 | en 5 | en 8 | en 12 | en 20 | en todas |
|---|---|---|---|---|---|---|---|---|
| Estafas reales coreanas (#144) | estafas | base | 4/33 | 7/33 | 10/33 | 14/33 | 19/33 | 28/33 |
| Estafas reales coreanas (#144) | estafas | p-lista | 7/33 | 10/33 | 12/33 | 17/33 | 20/33 | 30/33 |
| Estafas reales coreanas (#144) | estafas | p-escalera | 0/33 | 0/33 | 1/33 | 1/33 | 1/33 | 2/33 |
| Estafas reales coreanas (#144) | estafas | p-niveles | 8/33 | 14/33 | 23/33 | 24/33 | 27/33 | 32/33 |
| Estafas reales coreanas (#144) | estafas | c-rumbo | 7/33 | 10/33 | 15/33 | 21/33 | 23/33 | 29/33 |
| Estafas reales coreanas (#144) | estafas | p-sino | 4/33 | 5/33 | 7/33 | 9/33 | 11/33 | 17/33 |
| Estafas reales coreanas (#144) | estafas | p-minimo | 12/33 | 17/33 | 19/33 | 22/33 | 23/33 | 32/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | base | 1/33 | 2/33 | 4/33 | 4/33 | 5/33 | 5/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-lista | 2/33 | 5/33 | 13/33 | 15/33 | 17/33 | 17/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-escalera | 0/33 | 0/33 | 0/33 | 3/33 | 4/33 | 4/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-niveles | 4/33 | 8/33 | 10/33 | 11/33 | 12/33 | 12/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | c-rumbo | 2/33 | 2/33 | 5/33 | 8/33 | 9/33 | 9/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-sino | 0/33 | 0/33 | 4/33 | 5/33 | 8/33 | 8/33 |
| Legítimas reales (CallCenterEN, las 33) | legítimas | p-minimo | 4/33 | 8/33 | 14/33 | 16/33 | 19/33 | 19/33 |
| Desarrollo (alcance-140) | estafas | base | 2/46 | 6/46 | 12/46 | 14/46 | 15/46 | 15/46 |
| Desarrollo (alcance-140) | estafas | p-lista | 5/46 | 17/46 | 31/46 | 34/46 | 36/46 | 36/46 |
| Desarrollo (alcance-140) | estafas | p-escalera | 0/46 | 0/46 | 1/46 | 3/46 | 3/46 | 3/46 |
| Desarrollo (alcance-140) | estafas | p-niveles | 16/46 | 20/46 | 24/46 | 25/46 | 25/46 | 25/46 |
| Desarrollo (alcance-140) | estafas | c-rumbo | 2/46 | 9/46 | 13/46 | 20/46 | 22/46 | 22/46 |
| Desarrollo (alcance-140) | estafas | p-sino | 1/46 | 6/46 | 15/46 | 20/46 | 22/46 | 22/46 |
| Desarrollo (alcance-140) | estafas | p-minimo | 12/46 | 25/46 | 33/46 | 37/46 | 39/46 | 39/46 |
| Desarrollo (alcance-140) | legítimas | base | 5/94 | 7/94 | 7/94 | 8/94 | 8/94 | 8/94 |
| Desarrollo (alcance-140) | legítimas | p-lista | 25/94 | 27/94 | 33/94 | 34/94 | 34/94 | 34/94 |
| Desarrollo (alcance-140) | legítimas | p-escalera | 0/94 | 0/94 | 0/94 | 0/94 | 0/94 | 0/94 |
| Desarrollo (alcance-140) | legítimas | p-niveles | 12/94 | 12/94 | 15/94 | 16/94 | 16/94 | 16/94 |
| Desarrollo (alcance-140) | legítimas | c-rumbo | 8/94 | 11/94 | 12/94 | 13/94 | 13/94 | 13/94 |
| Desarrollo (alcance-140) | legítimas | p-sino | 1/94 | 5/94 | 10/94 | 14/94 | 14/94 | 14/94 |
| Desarrollo (alcance-140) | legítimas | p-minimo | 32/94 | 40/94 | 46/94 | 48/94 | 48/94 | 48/94 |

## Cuánto separa cada prompt

Consultas con riesgo ≥ 0,3 en estafas y en legítimas, y probabilidad de que una estafa puntúe más que una legítima (0,50 es no separar; 1,00, separar siempre). «12» es con las primeras 12 consultas de cada llamada.

| conjuntos | prompt | consultas ≥ 0,3, estafas | consultas ≥ 0,3, legítimas | ídem, primeras 12, estafas | ídem, primeras 12, legítimas | separa (máximo) | separa (máximo, 12) | separa (promedio, 12) |
|---|---|---|---|---|---|---|---|---|
| reales | base | 69 % | 30 % | 45 % | 28 % | 0.90 | 0.69 | 0.73 |
| reales | p-lista | 49 % | 14 % | 26 % | 13 % | 0.66 | 0.51 | 0.57 |
| reales | p-escalera | 57 % | 19 % | 12 % | 17 % | 0.63 | 0.43 | 0.49 |
| reales | p-niveles | 58 % | 12 % | 43 % | 11 % | 0.79 | 0.62 | 0.73 |
| reales | c-rumbo | 74 % | 39 % | 56 % | 37 % | 0.88 | 0.75 | 0.74 |
| reales | p-sino | 9 % | 4 % | 10 % | 3 % | 0.64 | 0.56 | 0.71 |
| reales | p-minimo | 61 % | 16 % | 38 % | 15 % | 0.75 | 0.58 | 0.64 |
| desarrollo | base | 51 % | 12 % | 50 % | 11 % | 0.86 | 0.85 | 0.86 |
| desarrollo | p-lista | 38 % | 13 % | 37 % | 13 % | 0.74 | 0.72 | 0.74 |
| desarrollo | p-escalera | 32 % | 12 % | 29 % | 12 % | 0.71 | 0.68 | 0.66 |
| desarrollo | p-niveles | 31 % | 12 % | 30 % | 11 % | 0.70 | 0.69 | 0.73 |
| desarrollo | c-rumbo | 59 % | 15 % | 58 % | 14 % | 0.84 | 0.82 | 0.84 |
| desarrollo | p-sino | 15 % | 2 % | 15 % | 3 % | 0.66 | 0.64 | 0.63 |
| desarrollo | p-minimo | 45 % | 26 % | 44 % | 26 % | 0.69 | 0.66 | 0.69 |

## Las 33 legítimas reales: ¿avisan siempre las mismas?

| prompts que avisan (de 7) | llamadas |
|---|---|
| 0 | 2 |
| 1 | 4 |
| 2 | 5 |
| 3 | 5 |
| 4 | 2 |
| 5 | 6 |
| 6 | 4 |
| 7 | 5 |

Contra la base:

| prompt | avisa | también avisa la base | solo este prompt | la base avisa y este no |
|---|---|---|---|---|
| p-lista | 17 | 15 | 2 | 8 |
| p-escalera | 21 | 16 | 5 | 7 |
| p-niveles | 12 | 9 | 3 | 14 |
| c-rumbo | 26 | 23 | 3 | 0 |
| p-sino | 8 | 7 | 1 | 16 |
| p-minimo | 19 | 16 | 3 | 7 |

Avisan con los 7 prompts (5): EXT-1839, EXT-2580, EXT-4412, EXT-4798, EXT-9907.

No avisan con ninguno (2): EXT-7393, EXT-9095.

## Coreanas que cada prompt no avisa o no avisa a tiempo

| prompt | sin aviso | con aviso, pero tarde |
|---|---|---|
| base | — | — |
| p-lista | EXT-122, EXT-640, EXT-711 | EXT-280, EXT-300, EXT-580, EXT-919 |
| p-escalera | EXT-640 | EXT-300, EXT-499, EXT-580, EXT-919, EXT-922 |
| p-niveles | EXT-329 | EXT-580, EXT-837, EXT-922 |
| c-rumbo | — | — |
| p-sino | EXT-045, EXT-122, EXT-147, EXT-189, EXT-207, EXT-284, EXT-300, EXT-329, EXT-465, EXT-580, EXT-640, EXT-662, EXT-680, EXT-767, EXT-787, EXT-922 | EXT-608, EXT-837, EXT-900, EXT-919 |
| p-minimo | EXT-640 | EXT-280, EXT-580, EXT-919, EXT-922 |

## Desarrollo: estafas con y sin línea de pedido

| prompt | avisadas, con pedido | avisadas, sin pedido |
|---|---|---|
| base | 33/36 | 10/10 |
| p-lista | 33/36 | 3/10 |
| p-escalera | 31/36 | 1/10 |
| p-niveles | 21/36 | 4/10 |
| c-rumbo | 34/36 | 10/10 |
| p-sino | 22/36 | 0/10 |
| p-minimo | 34/36 | 5/10 |
