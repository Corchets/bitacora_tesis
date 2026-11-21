# #143, segunda vuelta, etapa 1: diagnóstico fuera de la regla

## 1. Latencia por línea (Colab T4, ms de la consulta al SLM)

| corrida | líneas | ms p50 / p95 | tokens escritos p50 / p95 | lectura del prompt p50 (ms) | escritura p50 (ms) |
|---|---|---|---|---|---|
| v4-L | 2773 | 237 / 326 | 12 / 12 | 96 | 119 |
| v4-L, repetición | 2773 | 237 / 323 | 12 / 12 | 95 | 118 |
| v4 JSON (línea base, b: hasta el aviso) | 2225 | 432 / 546 | 41 / 41 | 106 | 300 |
| v4 JSON (d: con Tito, tras activar) | 1634 | 429 / 1038 | 41 / 98 | 95 | 290 |

En las mismas 2225 líneas: v4-L 237 / 327 ms y v4 JSON 432 / 546 ms (p50 / p95). La mediana del cociente JSON / v4-L, línea a línea, es 1.82; v4-L es más rápida en 2216 de 2225.

Etapa 2 (motivo y evidencia): no se midió. Como cota, el JSON entero de v4 en las 73 líneas de aviso de la línea base tardó 911 / 1088 ms (p50 / p95).

## 2. De dónde sale la diferencia con la línea base (corpus_v2)

v4-L corta el JSON después del riesgo, así que no ve `alerta_sugerida`. El riesgo escrito de v4-L sale del mismo corte (los mismos 12 tokens).

| corrida | regla | estafas | antes del pedido | falsas alarmas |
|---|---|---|---|---|
| v4 JSON (línea base) | riesgo ≥ 0.3 o alerta | 41/46 | 23 | 21/51 |
| v4 JSON (línea base) | riesgo ≥ 0.4 o alerta | 29/46 | 11 | 7/51 |
| v4 JSON (línea base) | riesgo ≥ 0.5 o alerta | 28/46 | 11 | 7/51 |
| v4 JSON (línea base) | riesgo ≥ 0.3 | 40/46 | 23 | 21/51 |
| v4 JSON (línea base) | riesgo ≥ 0.4 | 27/46 | 11 | 7/51 |
| v4 JSON (línea base) | riesgo ≥ 0.5 | 26/46 | 11 | 7/51 |
| v4-L, riesgo escrito | riesgo ≥ 0.3 | 41/46 | 22 | 21/51 |
| v4-L, riesgo escrito | riesgo ≥ 0.4 | 26/46 | 11 | 7/51 |
| v4-L, riesgo escrito | riesgo ≥ 0.5 | 26/46 | 11 | 7/51 |
| v4-L repetición, riesgo escrito | riesgo ≥ 0.3 | 41/46 | 22 | 20/51 |
| v4-L repetición, riesgo escrito | riesgo ≥ 0.4 | 26/46 | 11 | 7/51 |
| v4-L repetición, riesgo escrito | riesgo ≥ 0.5 | 26/46 | 11 | 7/51 |

Punto elegido de v4-L: umbral, umbral 0.4. Casos de corpus_v2 en que difiere de la línea base (riesgo ≥ 0,4 o alerta), con el riesgo escrito y el esperado en la línea del aviso de cualquiera de las dos:

| caso | clase | aviso base | aviso v4-L | aviso rep | línea | base: riesgo escrito | v4-L: escrito / esperado | rep: escrito / esperado |
|---|---|---|---|---|---|---|---|---|
| CV2-D-L-BANCO-003 | legitima | – | – | L9 | L9 | 0.3, alerta false | 0.3 / 0.374 | 0.3 / 0.402 |
| CV2-D-V-ORGANISMO_PREVISIONAL-004 | vishing (T_R 14) | L14 | – | – | L14 | 0.4, alerta false | 0.3 / 0.374 | 0.3 / 0.374 |
| CV2-D-V-PREMIO-002 | vishing (T_R 13) | L13 | – | – | L13 | 0.3, alerta true | 0.3 / 0.364 | 0.3 / 0.364 |
| CV2-D-V-WHATSAPP-003 | vishing (T_R 12) | L12 | – | – | L12 | 0.2, alerta true | 0.2 / 0.301 | 0.2 / 0.301 |
| CV2-D-V-WHATSAPP-004 | vishing (T_R 13) | – | L13 | L13 | L13 | 0.3, alerta false | 0.3 / 0.401 | 0.3 / 0.401 |

## 3. ¿Qué tan continuo es el riesgo esperado?

Masa del dígito más probable entre los dígitos del primer decimal (normalizada), en las líneas con decimal. En la primera vuelta, entre el 90 y el 94 % de las líneas tenía P(SÍ) ≤ 0,01 o ≥ 0,99.

| corrida | líneas | dígito con P ≥ 0,99 | entre 0,9 y 0,99 | < 0,9 | mediana | |esperado − escrito| < 0,01 |
|---|---|---|---|---|---|---|
| v4-L | 2773 | 10.4 % | 19.6 % | 70.0 % | 0.74 | 41.6 % |
| v4-L, repetición | 2771 | 10.8 % | 19.6 % | 69.6 % | 0.74 | 41.7 % |

Curva de v4-L, SLM solo, umbral simple, cerca del punto elegido (corpus_v2):

| umbral | estafas | antes del pedido | falsas alarmas |
|---|---|---|---|
| 0.25 | 41/46 | 23 | 22/51 |
| 0.3 | 37/46 | 20 | 15/51 |
| 0.35 | 30/46 | 14 | 11/51 |
| 0.38 | 27/46 | 12 | 8/51 |
| 0.4 | 27/46 | 11 | 7/51 |
| 0.45 | 25/46 | 9 | 6/51 |
| 0.5 | 24/46 | 7 | 5/51 |

## 4. Riesgo escrito: coincidencia entre corridas

Mismas líneas, las dos con riesgo. b y d son dos corridas JSON de v4 en sesiones distintas de Colab.

| par | líneas | iguales | difieren en 0,1 | en más de 0,1 | media de la diferencia |
|---|---|---|---|---|---|
| v4-L y su repetición | 2773 | 2671 (96.3 %) | 95 | 7 | +0.001 |
| v4-L y v4 JSON b | 2225 | 2034 (91.4 %) | 188 | 3 | -0.004 |
| v4 JSON b y v4 JSON d | 1132 | 1034 (91.3 %) | 90 | 8 | +0.002 |

## 5. Líneas inválidas y legítimas con falsa alarma por datos

- v4-L: 0 inválidas.
- v4-L, repetición: 2 inválidas: CV2-D-L-BANCO-008 L18 (sin_decimal_de_riesgo, escribió '0,'); CV2-D-L-DELIVERY-005 L19 (sin_decimal_de_riesgo, escribió '0,').

Las 6 legítimas en que v4 avisaba por un dato pedido en una llamada que inició la persona, sin la máscara del alcance (vista principal, en el punto de cada configuración):

| caso | v4 JSON (riesgo ≥ 0,4 o alerta) | v4-L (umbral, 0.4) |
|---|---|---|
| CV2-D-L-BANCO-001 | L6 | L7 |
| CV2-D-L-BANCO-002 | L7 | L7 |
| CV2-D-L-BANCO-004 | L8 | L8 |
| CV2-D-L-BANCO-005 | L8 | L8 |
| CV2-D-L-BANCO-010 | L10 | L10 |
| TR-13-turno-medico-pide-dni | L5 | L5 |

