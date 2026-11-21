# #143, evaluación final — análisis offline

Configuración: `c-consejos-corte-riesgo` (solo OTRA, «riesgo ≥ 0,3», modo operativo). Referencias: `v4-corte` (v4 sin alcance, «riesgo ≥ 0,4 o alerta», todas las líneas) y las reglas de palabras clave v1 y v2. Sin criterios de aprobación: cifras con intervalo y comparación pareada.

## Humo de formato

| prompt | leídas | errores | resultado |
|---|---|---|---|
| `c-consejos-corte-riesgo` | 48/48 | — | PASA |
| `v4-corte` | 48/48 | — | PASA |

## Control de las corridas

| conjunto | corrida | commit | control |
|---|---|---|---|
| desarrollo | config | 87bb7459f5 | bien |
| desarrollo | v4 | 87bb7459f5 | bien |
| desarrollo | reglas | 87bb7459f5 | bien |
| test_reservado | config | 87bb7459f5 | bien |
| test_reservado | v4 | 87bb7459f5 | bien |
| test_reservado | reglas | 87bb7459f5 | bien |
| externo | config | 87bb7459f5 | bien |
| externo | v4 | 87bb7459f5 | bien |
| externo | reglas | 87bb7459f5 | bien |
| legitimas_reales | config | 87bb7459f5 | bien |
| legitimas_reales | v4 | 87bb7459f5 | bien |
| legitimas_reales | reglas | 87bb7459f5 | bien |

**Control de reproducibilidad en desarrollo:** reproduce desarrollo (±2): estafas 40 (antes 40–42), antes del pedido 16 (antes 16–19), a tiempo 26 (antes 26–28), FA 20 (antes 18–22).

## Desarrollo

Vista principal: 46 estafas (36 con pedido, 15 con cumplimiento) y 94 legítimas (cotidiana 29, pedido_razonable 38, mencion_sin_pedido 27).

### Cifras (Wilson 95 %)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-consejos-corte-riesgo` | 40/46, 87 % [74–94] | 16/36, 44 % [30–60] | 26/36, 72 % [56–84] | 13/15, 87 % [62–96] | 20/94, 21 % [14–31] | 1/29, 3 % [1–17] | 10/38, 26 % [15–42] | 9/27, 33 % [19–52] |
| v4-corte | 28/46, 61 % [46–74] | 10/36, 28 % [16–44] | 25/36, 69 % [53–82] | 14/15, 93 % [70–99] | 42/94, 45 % [35–55] | 1/29, 3 % [1–17] | 23/38, 61 % [45–74] | 18/27, 67 % [48–81] |
| reglas v1 | 42/46, 91 % [80–97] | 27/36, 75 % [59–86] | 32/36, 89 % [75–96] | 15/15, 100 % [80–100] | 69/94, 73 % [64–81] | 13/29, 45 % [28–62] | 33/38, 87 % [73–94] | 23/27, 85 % [68–94] |
| reglas v2 | 11/46, 24 % [14–38] | 3/36, 8 % [3–22] | 9/36, 25 % [14–41] | 5/15, 33 % [15–58] | 36/94, 38 % [29–48] | 2/29, 7 % [2–22] | 18/38, 47 % [32–63] | 16/27, 59 % [41–75] |

### McNemar: la configuración contra cada referencia, en los mismos casos

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | estafas | 13 | 1 | 0.002 |
| v4-corte | antes del pedido | 7 | 1 | 0.070 |
| v4-corte | a tiempo | 3 | 2 | 1.000 |
| v4-corte | antes del cumplimiento | 0 | 1 | 1.000 |
| v4-corte | FA | 4 | 26 | 0.000 |
| reglas v1 | estafas | 3 | 5 | 0.727 |
| reglas v1 | antes del pedido | 2 | 13 | 0.007 |
| reglas v1 | a tiempo | 2 | 8 | 0.109 |
| reglas v1 | antes del cumplimiento | 0 | 2 | 0.500 |
| reglas v1 | FA | 4 | 53 | 0.000 |
| reglas v2 | estafas | 30 | 1 | 0.000 |
| reglas v2 | antes del pedido | 13 | 0 | 0.000 |
| reglas v2 | a tiempo | 18 | 1 | 0.000 |
| reglas v2 | antes del cumplimiento | 9 | 1 | 0.021 |
| reglas v2 | FA | 8 | 24 | 0.007 |

### Aparte (estafas · a tiempo · FA)

| vista | casos | `c-consejos-corte-riesgo` | v4-corte | reglas v1 | reglas v2 |
|---|---|---|---|---|---|
| aparte: corpus_v2 | 51 | 6/51 | 7/51 | 37/51 | 6/51 |
| aparte: laboratorio | 26 | 16/16 · 16/16 · 6/10 | 16/16 · 16/16 · 6/10 | 13/16 · 11/16 · 1/10 | 13/16 · 11/16 · 0/10 |
| aparte: piloto_escrito | 14 | 7/7 · 7/7 · 1/7 | 7/7 · 7/7 · 3/7 | 6/7 · 6/7 · 7/7 | 6/7 · 5/7 · 0/7 |
| aparte: trampa | 13 | 5/6 · 5/5 · 3/7 | 5/6 · 5/5 · 5/7 | 4/6 · 3/5 · 6/7 | 2/6 · 2/5 · 2/7 |

### La configuración, caso por caso (vista principal)

- Estafas sin aviso (6): CV2-D-V-FAMILIAR-006, CV2-D-V-PREMIO-003, CV2-D-V-SOPORTE-003, CV2-D-V-SOPORTE-005, CV2-D-V-SOPORTE-006, CV2-D-V-WHATSAPP-003.
- FA (20): ENT-L-BANCO-001 (pedido_razonable, L3), ENT-L-BANCO-002 (pedido_razonable, L4), ENT-L-BANCO-003 (pedido_razonable, L11), ENT-L-BANCO-004 (pedido_razonable, L6), ENT-L-BANCO-005 (pedido_razonable, L3), ENT-L-BANCO-006 (mencion_sin_pedido, L2), ENT-L-SOPORTE-001 (mencion_sin_pedido, L3), ENT-L-SOPORTE-003 (pedido_razonable, L15), ENT-L-SOPORTE-005 (pedido_razonable, L11), ENT-L-VENTAS-001 (pedido_razonable, L13), ENT-L-VENTAS-006 (mencion_sin_pedido, L12), ENT-L-VENTAS-009 (pedido_razonable, L19), LEG-BA-01 (mencion_sin_pedido, L7), LEG-BA-02 (mencion_sin_pedido, L3), LEG-CC-03 (cotidiana, L11), LEG2-BA-02 (mencion_sin_pedido, L6), LEG2-BA-05 (pedido_razonable, L8), LEG2-CC-05 (mencion_sin_pedido, L6), LEG2-CC-06 (mencion_sin_pedido, L6), LEG2-ST-03 (mencion_sin_pedido, L4).

### Formato y latencia

| detector | consultas | inválidas | ms por consulta (p50 / p95) |
|---|---|---|---|
| `c-consejos-corte-riesgo` | 1628 | 0 | 211 / 269 |
| v4-corte | 3187 | 0 | 284 / 348 |

## Test reservado

Vista principal: 100 estafas (80 con pedido, 32 con cumplimiento) y 56 legítimas (cotidiana 14, pedido_razonable 26, mencion_sin_pedido 16).

### Cifras (Wilson 95 %)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-consejos-corte-riesgo` | 73/100, 73 % [64–81] | 37/80, 46 % [36–57] | 53/80, 66 % [55–76] | 24/32, 75 % [58–87] | 15/56, 27 % [17–40] | 0/14, 0 % [0–22] | 7/26, 27 % [14–46] | 8/16, 50 % [28–72] |
| v4-corte | 64/100, 64 % [54–73] | 15/80, 19 % [12–29] | 50/80, 62 % [52–72] | 23/32, 72 % [55–84] | 15/56, 27 % [17–40] | 0/14, 0 % [0–22] | 8/26, 31 % [17–50] | 7/16, 44 % [23–67] |
| reglas v1 | 87/100, 87 % [79–92] | 55/80, 69 % [58–78] | 72/80, 90 % [81–95] | 30/32, 94 % [80–98] | 48/56, 86 % [74–93] | 10/14, 71 % [45–88] | 24/26, 92 % [76–98] | 14/16, 88 % [64–97] |
| reglas v2 | 33/100, 33 % [25–43] | 8/80, 10 % [5–19] | 30/80, 38 % [28–48] | 11/32, 34 % [20–52] | 8/56, 14 % [7–26] | 1/14, 7 % [1–31] | 6/26, 23 % [11–42] | 1/16, 6 % [1–28] |

### McNemar: la configuración contra cada referencia, en los mismos casos

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | estafas | 15 | 6 | 0.078 |
| v4-corte | antes del pedido | 22 | 0 | 0.000 |
| v4-corte | a tiempo | 12 | 9 | 0.664 |
| v4-corte | antes del cumplimiento | 3 | 2 | 1.000 |
| v4-corte | FA | 3 | 3 | 1.000 |
| reglas v1 | estafas | 6 | 20 | 0.009 |
| reglas v1 | antes del pedido | 8 | 26 | 0.003 |
| reglas v1 | a tiempo | 3 | 22 | 0.000 |
| reglas v1 | antes del cumplimiento | 2 | 8 | 0.109 |
| reglas v1 | FA | 0 | 33 | 0.000 |
| reglas v2 | estafas | 46 | 6 | 0.000 |
| reglas v2 | antes del pedido | 32 | 3 | 0.000 |
| reglas v2 | a tiempo | 32 | 9 | 0.000 |
| reglas v2 | antes del cumplimiento | 15 | 2 | 0.002 |
| reglas v2 | FA | 13 | 6 | 0.167 |

### Aparte (estafas · a tiempo · FA)

| vista | casos | `c-consejos-corte-riesgo` | v4-corte | reglas v1 | reglas v2 |
|---|---|---|---|---|---|
| aparte: legítimas viejas de la reserva, dentro del alcance | 26 | 2/26 | 1/26 | 15/26 | 4/26 |
| aparte: legítimas viejas de la reserva, fuera del alcance | 74 | 12/74 | 10/74 | 52/74 | 10/74 |

### La configuración, caso por caso (vista principal)

- Estafas sin aviso (27): CV2-T-V-BANCO-015, CV2-T-V-FAMILIAR-005, CV2-T-V-FAMILIAR-013, CV2-T-V-FAMILIAR-014, CV2-T-V-ORGANISMO_PREVISIONAL-006, CV2-T-V-ORGANISMO_PREVISIONAL-009, CV2-T-V-PREMIO-001, CV2-T-V-PREMIO-005, CV2-T-V-PREMIO-012, CV2-T-V-PREMIO-013, CV2-T-V-PREMIO-014, CV2-T-V-PREMIO-015, CV2-T-V-SOPORTE-001, CV2-T-V-SOPORTE-006, CV2-T-V-SOPORTE-008, CV2-T-V-SOPORTE-009, CV2-T-V-SOPORTE-011, CV2-T-V-SOPORTE-013, CV2-T-V-SOPORTE-018, CV2-T-V-SOPORTE-019, CV2-T-V-SOPORTE-020, CV2-T-V-WHATSAPP-005, CV2-T-V-WHATSAPP-006, CV2-T-V-WHATSAPP-009, CV2-T-V-WHATSAPP-011, CV2-T-V-WHATSAPP-012, CV2-T-V-WHATSAPP-014.
- FA (15): ENT-T-BANCO-001 (pedido_razonable, L3), ENT-T-BANCO-003 (mencion_sin_pedido, L5), ENT-T-BANCO-004 (mencion_sin_pedido, L20), ENT-T-BANCO-006 (pedido_razonable, L5), ENT-T-BANCO-007 (pedido_razonable, L6), ENT-T-COMERCIAL-002 (pedido_razonable, L2), ENT-T-COMERCIAL-006 (mencion_sin_pedido, L4), ENT-T-COMPRAVENTA-002 (pedido_razonable, L13), ENT-T-COMPRAVENTA-004 (mencion_sin_pedido, L16), ENT-T-DELIVERY-005 (mencion_sin_pedido, L4), ENT-T-MEDICO-002 (mencion_sin_pedido, L13), ENT-T-SOPORTE-002 (mencion_sin_pedido, L10), ENT-T-SOPORTE-006 (pedido_razonable, L3), ENT-T-TRAMITE-002 (pedido_razonable, L3), ENT-T-TRAMITE-003 (mencion_sin_pedido, L2).

### Formato y latencia

| detector | consultas | inválidas | ms por consulta (p50 / p95) |
|---|---|---|---|
| `c-consejos-corte-riesgo` | 2416 | 0 | 210 / 266 |
| v4-corte | 5153 | 0 | 284 / 352 |

## Set externo (#144)

Vista principal: 33 estafas (27 con pedido, 16 con cumplimiento) y 0 legítimas (cotidiana 0, pedido_razonable 0, mencion_sin_pedido 0).

### Cifras (Wilson 95 %)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-consejos-corte-riesgo` | 33/33, 100 % [90–100] | 25/27, 93 % [77–98] | 27/27, 100 % [88–100] | 16/16, 100 % [81–100] | — | — | — | — |
| v4-corte | 33/33, 100 % [90–100] | 23/27, 85 % [68–94] | 23/27, 85 % [68–94] | 16/16, 100 % [81–100] | — | — | — | — |
| reglas v1 | 33/33, 100 % [90–100] | 24/27, 89 % [72–96] | 25/27, 93 % [77–98] | 16/16, 100 % [81–100] | — | — | — | — |
| reglas v2 | 17/33, 52 % [35–67] | 3/27, 11 % [4–28] | 4/27, 15 % [6–32] | 2/16, 12 % [3–36] | — | — | — | — |

### McNemar: la configuración contra cada referencia, en los mismos casos

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | estafas | 0 | 0 | 1.000 |
| v4-corte | antes del pedido | 3 | 1 | 0.625 |
| v4-corte | a tiempo | 4 | 0 | 0.125 |
| v4-corte | antes del cumplimiento | 0 | 0 | 1.000 |
| reglas v1 | estafas | 0 | 0 | 1.000 |
| reglas v1 | antes del pedido | 2 | 1 | 1.000 |
| reglas v1 | a tiempo | 2 | 0 | 0.500 |
| reglas v1 | antes del cumplimiento | 0 | 0 | 1.000 |
| reglas v2 | estafas | 16 | 0 | 0.000 |
| reglas v2 | antes del pedido | 22 | 0 | 0.000 |
| reglas v2 | a tiempo | 23 | 0 | 0.000 |
| reglas v2 | antes del cumplimiento | 14 | 0 | 0.000 |

### La configuración, caso por caso (vista principal)

- Estafas sin aviso (0): ninguna.
- FA (0): ninguna.

### Formato y latencia

| detector | consultas | inválidas | ms por consulta (p50 / p95) |
|---|---|---|---|
| `c-consejos-corte-riesgo` | 205 | 0 | 213 / 286 |
| v4-corte | 651 | 0 | 299 / 381 |

## Legítimas reales (CallCenterEN)

Vista principal: 0 estafas (0 con pedido, 0 con cumplimiento) y 33 legítimas (cotidiana 19, pedido_razonable 4, mencion_sin_pedido 10).

### Cifras (Wilson 95 %)

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-consejos-corte-riesgo` | — | — | — | — | 21/33, 64 % [47–78] | 9/19, 47 % [27–68] | 4/4, 100 % [51–100] | 8/10, 80 % [49–94] |
| v4-corte | — | — | — | — | 10/33, 30 % [17–47] | 1/19, 5 % [1–25] | 3/4, 75 % [30–95] | 6/10, 60 % [31–83] |
| reglas v1 | — | — | — | — | 30/33, 91 % [76–97] | 17/19, 89 % [69–97] | 4/4, 100 % [51–100] | 9/10, 90 % [60–98] |
| reglas v2 | — | — | — | — | 4/33, 12 % [5–27] | 3/19, 16 % [6–38] | 0/4, 0 % [0–49] | 1/10, 10 % [2–40] |

### McNemar: la configuración contra cada referencia, en los mismos casos

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | FA | 12 | 1 | 0.003 |
| reglas v1 | FA | 2 | 11 | 0.022 |
| reglas v2 | FA | 19 | 2 | 0.000 |

### Aparte (estafas · a tiempo · FA)

| vista | casos | `c-consejos-corte-riesgo` | v4-corte | reglas v1 | reglas v2 |
|---|---|---|---|---|---|
| aparte: zona gris de Medicare (avisos, no son FA) | 42 | 32/42 | 20/42 | 41/42 | 6/42 |

### La configuración, caso por caso (vista principal)

- Estafas sin aviso (0): ninguna.
- FA (21): EXT-1056 (cotidiana, L8), EXT-1103 (cotidiana, L5), EXT-1296 (cotidiana, L18), EXT-1839 (mencion_sin_pedido, L20), EXT-1876 (pedido_razonable, L4), EXT-2219 (cotidiana, L17), EXT-2580 (pedido_razonable, L9), EXT-3706 (mencion_sin_pedido, L26), EXT-4338 (cotidiana, L13), EXT-4412 (mencion_sin_pedido, L5), EXT-4514 (cotidiana, L6), EXT-4541 (mencion_sin_pedido, L10), EXT-4688 (cotidiana, L12), EXT-4755 (cotidiana, L20), EXT-4798 (mencion_sin_pedido, L5), EXT-5512 (mencion_sin_pedido, L11), EXT-6178 (mencion_sin_pedido, L19), EXT-7938 (mencion_sin_pedido, L4), EXT-9104 (pedido_razonable, L10), EXT-9491 (cotidiana, L10), EXT-9907 (pedido_razonable, L12).

### Formato y latencia

| detector | consultas | inválidas | ms por consulta (p50 / p95) |
|---|---|---|---|
| `c-consejos-corte-riesgo` | 799 | 19 {'contexto_excedido': 19} | 236 / 310 |
| v4-corte | 2257 | 48 {'contexto_excedido': 48} | 292 / 374 |

### FA por volumen de llamadas (test, vista principal; sin umbral)

| llamadas de desconocidos legítimas por semana | FA por mes (Wilson 95 %) |
|---|---|
| 1 | 1.2 [0.7–1.7] |
| 3 | 3.5 [2.2–5.1] |
| 5 | 5.8 [3.7–8.6] |
| 10 | 11.6 [7.3–17.2] |
| 20 | 23.2 [14.7–34.3] |

**80/15, solo como referencia:** estafas avisadas 73 % (80 %), FA 27 % (15 %).

## Con la anotación alternativa (`etiquetas-producto.json`)

Cambios: desarrollo: 19 con cambios (vista 19).

### Desarrollo, vista principal con la anotación alternativa

| detector | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA cotidiana | FA pedido_razonable | FA mencion_sin_pedido |
|---|---|---|---|---|---|---|---|---|
| `c-consejos-corte-riesgo` | 40/46, 87 % [74–94] | 16/36, 44 % [30–60] | 26/36, 72 % [56–84] | 13/15, 87 % [62–96] | 8/75, 11 % [6–20] | 1/29, 3 % [1–17] | 2/27, 7 % [2–23] | 5/19, 26 % [12–49] |
| v4-corte | 28/46, 61 % [46–74] | 10/36, 28 % [16–44] | 25/36, 69 % [53–82] | 14/15, 93 % [70–99] | 25/75, 33 % [24–45] | 1/29, 3 % [1–17] | 14/27, 52 % [34–69] | 10/19, 53 % [32–73] |
| reglas v1 | 42/46, 91 % [80–97] | 27/36, 75 % [59–86] | 32/36, 89 % [75–96] | 15/15, 100 % [80–100] | 52/75, 69 % [58–79] | 13/29, 45 % [28–62] | 22/27, 81 % [63–92] | 17/19, 89 % [69–97] |
| reglas v2 | 11/46, 24 % [14–38] | 3/36, 8 % [3–22] | 9/36, 25 % [14–41] | 5/15, 33 % [15–58] | 22/75, 29 % [20–40] | 2/29, 7 % [2–22] | 10/27, 37 % [22–56] | 10/19, 53 % [32–73] |

| referencia | cifra | solo la configuración | solo la referencia | p (McNemar exacto) |
|---|---|---|---|---|
| v4-corte | estafas | 13 | 1 | 0.002 |
| v4-corte | antes del pedido | 7 | 1 | 0.070 |
| v4-corte | a tiempo | 3 | 2 | 1.000 |
| v4-corte | antes del cumplimiento | 0 | 1 | 1.000 |
| v4-corte | FA | 3 | 20 | 0.000 |
| reglas v1 | estafas | 3 | 5 | 0.727 |
| reglas v1 | antes del pedido | 2 | 13 | 0.007 |
| reglas v1 | a tiempo | 2 | 8 | 0.109 |
| reglas v1 | antes del cumplimiento | 0 | 2 | 0.500 |
| reglas v1 | FA | 3 | 47 | 0.000 |
| reglas v2 | estafas | 30 | 1 | 0.000 |
| reglas v2 | antes del pedido | 13 | 0 | 0.000 |
| reglas v2 | a tiempo | 18 | 1 | 0.000 |
| reglas v2 | antes del cumplimiento | 9 | 1 | 0.021 |
| reglas v2 | FA | 4 | 18 | 0.004 |

