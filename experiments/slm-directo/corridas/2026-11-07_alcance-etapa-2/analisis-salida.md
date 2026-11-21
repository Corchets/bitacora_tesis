# #143, segunda vuelta, etapa 2: C y v4-premisa contra v4 dentro del alcance — análisis offline

Vista dentro del alcance: 46 estafas de corpus_v2 (36 con pedido) y 94 legítimas entrantes.

## Humo de formato

| prompt | tokens hasta la alerta (mín / mediana / máx) | alcanzan | cortado leídas | mismo riesgo y alerta que el completo (dato) | resultado |
|---|---|---|---|---|---|
| `c-json-corte` | 23 / 23.0 / 23 | 48/48 | 48/48 | 43/48 | PASA |
| `v4-premisa-corte` | 23 / 23.0 / 23 | 48/48 | 48/48 | 43/48 | PASA |

## Control de las corridas

| corrida | casos | líneas | inválidas | ms primera consulta p50 / p95 | commit |
|---|---|---|---|---|---|
| v4-corte | 244 | 4325 | 0 | 297 / 359 | d127953fcc |
| c-json-corte | 244 | 4325 | 0 | 277 / 336 | d127953fcc |
| c-json-corte-rep | 140 | 2621 | 0 | 275 / 334 | d127953fcc |
| v4-premisa-corte | 244 | 4325 | 0 | 293 / 359 | d127953fcc |
| v4-premisa-corte-rep | 140 | 2621 | 0 | 288 / 352 | d127953fcc |

Sin problemas de control: mismo commit, digest, Ollama, parámetros, prompts y casos.

## Curva dentro del alcance

Cada celda: estafas (/46) · avisos antes del pedido (/36) · FA (/94).

| regla | v4-corte | c-json-corte | c-json-corte-rep | v4-premisa-corte | v4-premisa-corte-rep |
|---|---|---|---|---|---|
| alerta sola | 28/46 · 10/36 · FA 42/94 | 10/46 · 4/36 · FA 9/94 | 12/46 · 5/36 · FA 9/94 | 27/46 · 9/36 · FA 41/94 | 27/46 · 9/36 · FA 41/94 |
| riesgo ≥ 0.1 o alerta | 46/46 · 36/36 · FA 94/94 | 46/46 · 36/36 · FA 94/94 | 46/46 · 36/36 · FA 94/94 | 46/46 · 36/36 · FA 94/94 | 46/46 · 36/36 · FA 94/94 |
| riesgo ≥ 0.2 o alerta | 46/46 · 32/36 · FA 77/94 | 46/46 · 36/36 · FA 72/94 | 46/46 · 36/36 · FA 69/94 | 46/46 · 32/36 · FA 75/94 | 46/46 · 32/36 · FA 74/94 |
| riesgo ≥ 0.3 o alerta | 39/46 · 22/36 · FA 52/94 | 36/46 · 17/36 · FA 27/94 | 36/46 · 16/36 · FA 26/94 | 39/46 · 20/36 · FA 46/94 | 39/46 · 20/36 · FA 47/94 |
| riesgo ≥ 0.4 o alerta | 28/46 · 10/36 · FA 42/94 | 15/46 · 6/36 · FA 9/94 | 15/46 · 6/36 · FA 9/94 | 27/46 · 11/36 · FA 41/94 | 27/46 · 11/36 · FA 42/94 |
| riesgo ≥ 0.5 o alerta | 28/46 · 10/36 · FA 42/94 | 15/46 · 5/36 · FA 9/94 | 15/46 · 5/36 · FA 9/94 | 27/46 · 11/36 · FA 41/94 | 27/46 · 11/36 · FA 42/94 |
| riesgo ≥ 0.6 o alerta | 28/46 · 10/36 · FA 42/94 | 14/46 · 5/36 · FA 9/94 | 14/46 · 5/36 · FA 9/94 | 27/46 · 9/36 · FA 41/94 | 27/46 · 9/36 · FA 41/94 |
| riesgo ≥ 0.7 o alerta | 28/46 · 10/36 · FA 42/94 | 10/46 · 4/36 · FA 9/94 | 12/46 · 5/36 · FA 9/94 | 27/46 · 9/36 · FA 41/94 | 27/46 · 9/36 · FA 41/94 |
| riesgo ≥ 0.8 o alerta | 28/46 · 10/36 · FA 42/94 | 10/46 · 4/36 · FA 9/94 | 12/46 · 5/36 · FA 9/94 | 27/46 · 9/36 · FA 41/94 | 27/46 · 9/36 · FA 41/94 |
| riesgo ≥ 0.9 o alerta | 28/46 · 10/36 · FA 42/94 | 10/46 · 4/36 · FA 9/94 | 12/46 · 5/36 · FA 9/94 | 27/46 · 9/36 · FA 41/94 | 27/46 · 9/36 · FA 41/94 |
| riesgo ≥ 1 o alerta | 28/46 · 10/36 · FA 42/94 | 10/46 · 4/36 · FA 9/94 | 12/46 · 5/36 · FA 9/94 | 27/46 · 9/36 · FA 41/94 | 27/46 · 9/36 · FA 41/94 |

Reglas del laboratorio, sin modelo: reglas 42/46 · 27/36 · FA 69/94; reglas_v2 11/46 · 3/36 · FA 36/94.

La curva completa también está en `curva.csv`.

## Regla de #143

Punto de comparación: v4-corte con su regla adoptada («riesgo ≥ 0,4 o alerta») tiene F = 42/94 FA. Cada configuración usa su regla con FA ≤ 42 que avisa más estafas.

| configuración | regla | estafas | antes del pedido | antes o en el pedido | FA | contra v4-corte | veredicto |
|---|---|---|---|---|---|---|---|
| v4-corte (referencia) | riesgo ≥ 0.4 o alerta | 28/46 | 10/36 | 25/36 | 42/94 | — | — |
| C | riesgo ≥ 0.3 o alerta | 36/46 | 17/36 | 25/36 | 27/94 | +8 estafas, +7 avisos antes del pedido | gana (estafas, antes) y la repetición lo sostiene (+8 estafas, +6 avisos antes del pedido, FA 26): cuenta |
| v4-premisa | riesgo ≥ 0.4 o alerta | 27/46 | 11/36 | 25/36 | 41/94 | -1 estafas, +1 avisos antes del pedido | dentro de ±2: queda v4-corte |

**Se adopta C, provisorio hasta la reserva.**

## Aparte, solo para mirar

### La misma comparación con otros niveles de FA (no decide)

| FA máx. | corrida | regla | estafas | antes del pedido | antes o en el pedido | FA | contra v4-corte |
|---|---|---|---|---|---|---|---|
| 0 | v4-corte | ninguna |  |  |  |  |  |
| 0 | c-json-corte | ninguna |  |  |  |  |  |
| 0 | v4-premisa-corte | ninguna |  |  |  |  |  |
| 4 | v4-corte | ninguna |  |  |  |  |  |
| 4 | c-json-corte | ninguna |  |  |  |  |  |
| 4 | v4-premisa-corte | ninguna |  |  |  |  |  |
| 9 | v4-corte | ninguna |  |  |  |  |  |
| 9 | c-json-corte | riesgo ≥ 0.4 o alerta | 15/46 | 6/36 | 10/36 | 9/94 | — |
| 9 | v4-premisa-corte | ninguna |  |  |  |  |  |
| 14 | v4-corte | ninguna |  |  |  |  |  |
| 14 | c-json-corte | riesgo ≥ 0.4 o alerta | 15/46 | 6/36 | 10/36 | 9/94 | — |
| 14 | v4-premisa-corte | ninguna |  |  |  |  |  |

### Intervalos de Wilson en el punto de comparación

| corrida | regla | estafas | antes del pedido | detección útil (antes o en el pedido) | FA |
|---|---|---|---|---|---|
| v4-corte | riesgo ≥ 0.4 o alerta | 28/46, 61 % [46–74] | 10/36, 28 % [16–44] | 25/36, 69 % [53–82] | 42/94, 45 % [35–55] |
| c-json-corte | riesgo ≥ 0.3 o alerta | 36/46, 78 % [64–88] | 17/36, 47 % [32–63] | 25/36, 69 % [53–82] | 27/94, 29 % [21–39] |
| v4-premisa-corte | riesgo ≥ 0.4 o alerta | 27/46, 59 % [44–72] | 11/36, 31 % [18–47] | 25/36, 69 % [53–82] | 41/94, 44 % [34–54] |

### Estafas sin pedido y estafas que piden un dato (L = línea del primer aviso; – sin aviso)

Estafas sin pedido avisadas en el punto de comparación: v4-corte 1/10; c-json-corte 9/10; v4-premisa-corte 1/10; reglas 8/10; reglas_v2 0/10.

| caso | pedido | v4-corte | c-json-corte | v4-premisa-corte | reglas | reglas_v2 |
|---|---|---|---|---|---|---|
| CV2-D-V-ORGANISMO_PREVISIONAL-001 | T_R 12 | L12 | L10 | L12 | L3 | – |
| CV2-D-V-ORGANISMO_PREVISIONAL-002 | T_R 9 | L9 | L9 | L9 | L7 | – |
| CV2-D-V-ORGANISMO_PREVISIONAL-003 | T_R 11 | L13 | L1 | – | L12 | – |
| CV2-D-V-ORGANISMO_PREVISIONAL-004 | T_R 14 | – | L5 | – | L16 | – |
| CV2-D-V-PREMIO-001 | T_R 10 | L10 | L10 | L10 | L10 | – |
| CV2-D-V-PREMIO-003 | T_R 13 | – | – | – | – | – |

### Otros grupos, en el punto de comparación y con «riesgo ≥ 0,4 o alerta»

Cada celda: estafas · avisos antes del pedido · FA. Las reglas del laboratorio no tienen umbral.

| grupo | corrida | en el punto de comparación | con «riesgo ≥ 0,4 o alerta» |
|---|---|---|---|
| corpus_v2 entero, sin alcance (46 + 51) | v4-corte | 28/46 · 10/36 · FA 7/51 | 28/46 · 10/36 · FA 7/51 |
| corpus_v2 entero, sin alcance (46 + 51) | c-json-corte | 36/46 · 17/36 · FA 13/51 | 15/46 · 6/36 · FA 2/51 |
| corpus_v2 entero, sin alcance (46 + 51) | v4-premisa-corte | 27/46 · 11/36 · FA 8/51 | 27/46 · 11/36 · FA 8/51 |
| corpus_v2 entero, sin alcance (46 + 51) | reglas | 42/46 · 27/36 · FA 37/51 | — |
| corpus_v2 entero, sin alcance (46 + 51) | reglas_v2 | 11/46 · 3/36 · FA 6/51 | — |
| las 7 legítimas de corpus_v2 dentro del alcance | v4-corte | FA 0/7 | FA 0/7 |
| las 7 legítimas de corpus_v2 dentro del alcance | c-json-corte | FA 0/7 | FA 0/7 |
| las 7 legítimas de corpus_v2 dentro del alcance | v4-premisa-corte | FA 0/7 | FA 0/7 |
| las 7 legítimas de corpus_v2 dentro del alcance | reglas | FA 3/7 | — |
| las 7 legítimas de corpus_v2 dentro del alcance | reglas_v2 | FA 1/7 | — |
| manuales: laboratorio | v4-corte | 16/16 · 8/16 · FA 5/10 | 16/16 · 8/16 · FA 5/10 |
| manuales: laboratorio | c-json-corte | 16/16 · 15/16 · FA 8/10 | 16/16 · 13/16 · FA 8/10 |
| manuales: laboratorio | v4-premisa-corte | 16/16 · 7/16 · FA 4/10 | 16/16 · 7/16 · FA 4/10 |
| manuales: laboratorio | reglas | 13/16 · 0/16 · FA 1/10 | — |
| manuales: laboratorio | reglas_v2 | 13/16 · 0/16 · FA 0/10 | — |
| manuales: piloto_escrito | v4-corte | 7/7 · 4/7 · FA 3/7 | 7/7 · 4/7 · FA 3/7 |
| manuales: piloto_escrito | c-json-corte | 7/7 · 6/7 · FA 3/7 | 7/7 · 4/7 · FA 1/7 |
| manuales: piloto_escrito | v4-premisa-corte | 7/7 · 3/7 · FA 3/7 | 7/7 · 3/7 · FA 3/7 |
| manuales: piloto_escrito | reglas | 6/7 · 3/7 · FA 7/7 | — |
| manuales: piloto_escrito | reglas_v2 | 6/7 · 0/7 · FA 0/7 | — |
| manuales: trampa | v4-corte | 5/6 · 3/5 · FA 5/7 | 5/6 · 3/5 · FA 5/7 |
| manuales: trampa | c-json-corte | 5/6 · 4/5 · FA 4/7 | 4/6 · 3/5 · FA 3/7 |
| manuales: trampa | v4-premisa-corte | 5/6 · 2/5 · FA 5/7 | 5/6 · 2/5 · FA 5/7 |
| manuales: trampa | reglas | 4/6 · 2/5 · FA 6/7 | — |
| manuales: trampa | reglas_v2 | 2/6 · 1/5 · FA 2/7 | — |
| legítimas por lote: LEG (21) | v4-corte | FA 3/21 | FA 3/21 |
| legítimas por lote: LEG (21) | c-json-corte | FA 5/21 | FA 1/21 |
| legítimas por lote: LEG (21) | v4-premisa-corte | FA 3/21 | FA 3/21 |
| legítimas por lote: LEG (21) | reglas | FA 11/21 | — |
| legítimas por lote: LEG (21) | reglas_v2 | FA 3/21 | — |
| legítimas por lote: LEG2 (28) | v4-corte | FA 15/28 | FA 15/28 |
| legítimas por lote: LEG2 (28) | c-json-corte | FA 8/28 | FA 3/28 |
| legítimas por lote: LEG2 (28) | v4-premisa-corte | FA 14/28 | FA 14/28 |
| legítimas por lote: LEG2 (28) | reglas | FA 19/28 | — |
| legítimas por lote: LEG2 (28) | reglas_v2 | FA 15/28 | — |
| legítimas por lote: ENT-L (42) | v4-corte | FA 23/42 | FA 23/42 |
| legítimas por lote: ENT-L (42) | c-json-corte | FA 14/42 | FA 5/42 |
| legítimas por lote: ENT-L (42) | v4-premisa-corte | FA 23/42 | FA 23/42 |
| legítimas por lote: ENT-L (42) | reglas | FA 36/42 | — |
| legítimas por lote: ENT-L (42) | reglas_v2 | FA 16/42 | — |
| legítimas por lote: selección (3) | v4-corte | FA 1/3 | FA 1/3 |
| legítimas por lote: selección (3) | c-json-corte | FA 0/3 | FA 0/3 |
| legítimas por lote: selección (3) | v4-premisa-corte | FA 1/3 | FA 1/3 |
| legítimas por lote: selección (3) | reglas | FA 3/3 | — |
| legítimas por lote: selección (3) | reglas_v2 | FA 2/3 | — |

### Corrida y repetición, dentro del alcance (ADR 0005: «para reconsiderarla, más de 2 casos»)

| candidata | regla | estafas (corrida) | antes del pedido (corrida) | antes o en el pedido (corrida) | FA (corrida) | estafas (repetición) | antes del pedido (repetición) | antes o en el pedido (repetición) | FA (repetición) | casos con otra línea de aviso | riesgo escrito igual |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C | riesgo ≥ 0.3 o alerta | 36/46 | 17/36 | 25/36 | 27/94 | 36/46 | 16/36 | 25/36 | 26/94 | 3 | 2513/2621 (95.9 %) |
| v4-premisa | riesgo ≥ 0.4 o alerta | 27/46 | 11/36 | 25/36 | 41/94 | 27/46 | 11/36 | 25/36 | 42/94 | 1 | 2586/2621 (98.7 %) |

### Latencia en T4 (ms de pared; p50 / p95)

| corrida | primera consulta (ms) | tokens del prompt | segunda consulta (ms) | líneas con segunda consulta | fallos de la segunda |
|---|---|---|---|---|---|
| v4-corte | 290 / 350 | 1052 / 1369 | 704 / 909 | 70 | 2 |
| c-json-corte | 276 / 335 | 777 / 1094 | 690 / 847 | 24 | 0 |
| c-json-corte-rep | 275 / 334 | 777 / 1094 | 691 / 872 | 24 | 0 |
| v4-premisa-corte | 285 / 350 | 1073 / 1390 | 718 / 934 | 68 | 1 |
| v4-premisa-corte-rep | 288 / 352 | 1073 / 1390 | 721 / 935 | 69 | 1 |

### Controles de ventas y préstamos (solo para mirar)

| control | clase | alcance | qué prueba | v4-corte (riesgo ≥ 0.4 o alerta) | c-json-corte (riesgo ≥ 0.3 o alerta) | v4-premisa-corte (riesgo ≥ 0.4 o alerta) |
|---|---|---|---|---|---|---|
| CTRL-L-VENTA-PORTABILIDAD | legitima_dificil | dentro | Venta telefónica de portabilidad que pide DNI, número de trámite, fecha de nacimiento, domicilio y correo, y anuncia un código por SMS que la persona carga sola, sin dictarlo. | L4 | L4 | L4 |
| CTRL-V-OPERADOR-SMS | vishing | dentro | Falso operador de telefonía que inventa un problema de titularidad, suma un descuento para jubilados y pide leer o reenviar el código del SMS para quedarse con el WhatsApp. | L6 | L4 | L6 |
| CTRL-L-BANCO-OFRECE-PRESTAMO | legitima_dificil | dentro | El banco llama con un préstamo preaprobado, confirma nombre y DNI y deja la aceptación en la app o el home banking, con acreditación a las 48 horas hábiles y sin pedir token ni claves. | L4 | L4 | L4 |
| CTRL-V-BANCO-PRESTAMO-TOKEN | vishing | dentro | Falso empleado del banco que ofrece un préstamo preaprobado con acreditación inmediata y, para «confirmarlo», pide generar el código del token y dictarlo. | L4 | L4 | L4 |
| CTRL-L-PIDE-PRESTAMO | legitima_dificil | fuera | La persona llama a su banco a pedir un préstamo y el operador le pide DNI, fecha de nacimiento, ingresos, empleador, domicilio y correo, pero deja la confirmación en el home banking y no pide códigos. | L3 | L3 | L3 |
| CTRL-V-PRESTAMO-REDES | vishing | fuera | La persona llama a un número de préstamos visto en redes, se lo aprueban al instante y le piden transferir por adelantado una comisión a una billetera virtual. | L5 | L4 | L5 |

