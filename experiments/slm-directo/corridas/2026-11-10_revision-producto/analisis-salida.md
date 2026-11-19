# #143, revisión de producto — análisis offline

Vista: alcance-140, 46 estafas (36 con pedido, 15 con cumplimiento) y 94 legítimas. Por etiqueta de producto: 75 «no debería avisar», 18 tolerables y 1 «debería avisar». Por la anotación original: 29 cotidianas y 65 con pedido o mención. El aviso es la primera línea de OTRA con «riesgo ≥ 0,3».

## Humo de formato

| prompt | riesgo leído | errores | mismo riesgo que la base (dato) | riesgo ≥ 0,3 (dato) | riesgo ≥ 0,6 (dato) | resultado |
|---|---|---|---|---|---|---|
| `c-premisa-corte-riesgo` | 48/48 | — | 48/48 | 43 | 7 | PASA |
| `c-codigo-corte-riesgo` | 48/48 | — | 23/48 | 35 | 3 | PASA |
| `c-consejos-corte-riesgo` | 48/48 | — | 40/48 | 41 | 11 | PASA |
| `c-freno-corte-riesgo` | 48/48 | — | 32/48 | 45 | 3 | PASA |

## Control de las corridas

| corrida | commit | líneas inválidas | control |
|---|---|---|---|
| base | 30746d3f38 | 0/2177 | bien |
| c-codigo | 30746d3f38 | 0/2177 | bien |
| c-consejos | 30746d3f38 | 0/2177 | bien |
| c-freno | 30746d3f38 | 0/2177 | bien |
| base-rep | 30746d3f38 | 0/1313 | bien |
| c-codigo-rep | 30746d3f38 | 0/1313 | bien |
| c-consejos-rep | 30746d3f38 | 0/1313 | bien |
| c-freno-rep | 30746d3f38 | 0/1313 | bien |

## Cifras

| corrida | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA estrictas | FA tolerables | debería avisar | FA cotidianas | FA dudosas | FA | código o clave | código o clave, a tiempo |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 41/46 | 20/36 | 29/36 | 13/15 | 11/75 | 12/18 | 1/1 | 2/29 | 22/65 | 24/94 | 15/17 | 13/17 |
| c-codigo | 39/46 | 15/36 | 26/36 | 13/15 | 10/75 | 12/18 | 1/1 | 2/29 | 21/65 | 23/94 | 15/17 | 12/17 |
| c-consejos | 41/46 | 19/36 | 28/36 | 14/15 | 10/75 | 11/18 | 1/1 | 1/29 | 21/65 | 22/94 | 16/17 | 14/17 |
| c-freno | 42/46 | 24/36 | 30/36 | 13/15 | 20/75 | 15/18 | 1/1 | 3/29 | 33/65 | 36/94 | 14/17 | 12/17 |
| base-rep | 40/46 | 20/36 | 29/36 | 12/15 | 13/75 | 11/18 | 1/1 | 2/29 | 23/65 | 25/94 | 14/17 | 13/17 |
| c-codigo-rep | 41/46 | 15/36 | 27/36 | 15/15 | 7/75 | 12/18 | 1/1 | 2/29 | 18/65 | 20/94 | 16/17 | 12/17 |
| c-consejos-rep | 42/46 | 18/36 | 28/36 | 14/15 | 7/75 | 10/18 | 1/1 | 0/29 | 18/65 | 18/94 | 15/17 | 13/17 |
| c-freno-rep | 42/46 | 24/36 | 30/36 | 13/15 | 19/75 | 15/18 | 1/1 | 3/29 | 32/65 | 35/94 | 14/17 | 12/17 |

«FA estrictas» son los avisos en las 75 «no debería avisar». «Código o clave» se informa aparte y no decide.

## La regla

### Versión «producto» (decide)

| variante | resultado | por qué |
|---|---|---|
| `c-codigo` | no pasa | no suma 3 o más en ninguna cifra de detección (-2 estafas, -5 antes del pedido, -3 a tiempo, +0 antes del cumplimiento, FA estrictas -1) |
| `c-consejos` | no pasa | no suma 3 o más en ninguna cifra de detección (+0 estafas, -1 antes del pedido, -1 a tiempo, +1 antes del cumplimiento, FA estrictas -1) |
| `c-freno` | no pasa | suma 3 o más en FA estrictas (+1 estafas, +4 antes del pedido, +1 a tiempo, +0 antes del cumplimiento, FA estrictas +9) |

**Resultado: queda la base.**

### Versión «original» (se informa, no decide)

| variante | resultado | por qué |
|---|---|---|
| `c-codigo` | no pasa | no suma 3 o más en ninguna cifra de detección (-2 estafas, -5 antes del pedido, -3 a tiempo, +0 antes del cumplimiento, FA cotidianas +0) |
| `c-consejos` | no pasa | no suma 3 o más en ninguna cifra de detección (+0 estafas, -1 antes del pedido, -1 a tiempo, +1 antes del cumplimiento, FA cotidianas -1) |
| `c-freno` | pasa | +1 estafas, +4 antes del pedido, +1 a tiempo, +0 antes del cumplimiento, FA cotidianas +1; repetición: +2 estafas, +4 antes del pedido, +1 a tiempo, +1 antes del cumplimiento, FA cotidianas +1 |

Con esta versión: queda `c-freno`.

## Aparte, solo para mirar

### Estafas con pedido de código o clave (/17)

| caso | pedido | T_R | base | c-codigo | c-consejos | c-freno |
|---|---|---|---|---|---|---|
| CV2-D-V-BANCO-001 | REQUEST_AUTH_CODE | 32 | L2 | L2 | L2 | L2 |
| CV2-D-V-BANCO-004 | REQUEST_AUTH_CODE | 16 | L8 | L8 | L8 | L6 |
| CV2-D-V-BANCO-005 | REQUEST_SECRET | 19 | L1 | L3 | L5 | L1 |
| CV2-D-V-BANCO-006 | REQUEST_AUTH_CODE | 14 | L10 | L10 | L10 | L2 |
| CV2-D-V-BANCO-009 | REQUEST_SECRET | 13 | L5 | L5 | L5 | L1 |
| CV2-D-V-BANCO-010 | REQUEST_AUTH_CODE | 13 | L1 | L1 | L1 | L1 |
| CV2-D-V-PREMIO-004 | REQUEST_SECRET | 14 | L12 | L12 | L12 | L10 |
| CV2-D-V-SOPORTE-001 | REQUEST_SECRET | 14 | L16 | L16 | L16 | L18 |
| CV2-D-V-SOPORTE-003 | REQUEST_SECRET | 11 | – | L17 | – | – |
| CV2-D-V-SOPORTE-005 | REQUEST_SECRET | 16 | L14 | – | L14 | L6 |
| CV2-D-V-SOPORTE-006 | REQUEST_SECRET | 15 | L15 | L15 | L15 | – |
| CV2-D-V-WHATSAPP-001 | REQUEST_AUTH_CODE | 9 | L9 | L9 | L9 | L9 |
| CV2-D-V-WHATSAPP-002 | REQUEST_AUTH_CODE | 10 | L10 | L10 | L10 | L10 |
| CV2-D-V-WHATSAPP-003 | REQUEST_AUTH_CODE | 12 | – | L16 | L12 | – |
| CV2-D-V-WHATSAPP-004 | REQUEST_AUTH_CODE | 13 | L5 | L5 | L9 | L5 |
| CV2-D-V-WHATSAPP-005 | REQUEST_AUTH_CODE | 14 | L14 | L14 | L14 | L14 |
| CV2-D-V-WHATSAPP-006 | REQUEST_AUTH_CODE | 25 | L26 | – | L26 | L26 |

### Estafas con pedido de datos personales (/6)

| caso | T_R | base | c-codigo | c-consejos | c-freno |
|---|---|---|---|---|---|
| CV2-D-V-ORGANISMO_PREVISIONAL-001 | 12 | L12 | L12 | L12 | L2 |
| CV2-D-V-ORGANISMO_PREVISIONAL-002 | 9 | L9 | L9 | L9 | L1 |
| CV2-D-V-ORGANISMO_PREVISIONAL-003 | 11 | L1 | L13 | L13 | L1 |
| CV2-D-V-ORGANISMO_PREVISIONAL-004 | 14 | L6 | L14 | L8 | L2 |
| CV2-D-V-PREMIO-001 | 10 | L8 | L10 | L8 | L8 |
| CV2-D-V-PREMIO-003 | 13 | – | – | – | – |

### Estafas que la base no avisa, y en qué línea las avisa cada variante

| caso | pedido | T_R | c-codigo | c-consejos | c-freno |
|---|---|---|---|---|---|
| CV2-D-V-FAMILIAR-005 | REQUEST_TRANSFER | 20 | L20 | – | L20 |
| CV2-D-V-PREMIO-003 | REQUEST_PERSONAL_DATA | 13 | – | – | – |
| CV2-D-V-PREMIO-006 | sin pedido | — | – | L17 | L1 |
| CV2-D-V-SOPORTE-003 | REQUEST_SECRET | 11 | L17 | – | – |
| CV2-D-V-WHATSAPP-003 | REQUEST_AUTH_CODE | 12 | L16 | L12 | – |

### Estafas que la base avisa y alguna variante pierde

| caso | pedido | base | c-codigo | c-consejos | c-freno |
|---|---|---|---|---|---|
| CV2-D-V-FAMILIAR-004 | REQUEST_TRANSFER | L26 | L24 | – | L10 |
| CV2-D-V-FAMILIAR-006 | REQUEST_TRANSFER | L14 | – | – | L12 |
| CV2-D-V-PREMIO-002 | REQUEST_TRANSFER | L11 | – | L13 | L11 |
| CV2-D-V-PREMIO-005 | sin pedido | L8 | – | L16 | L8 |
| CV2-D-V-SOPORTE-005 | REQUEST_SECRET | L14 | – | L14 | L6 |
| CV2-D-V-SOPORTE-006 | REQUEST_SECRET | L15 | L15 | L15 | – |
| CV2-D-V-WHATSAPP-006 | REQUEST_AUTH_CODE | L26 | – | L26 | L26 |

### FA por intención de la llamada (etiqueta de producto)

| corrida | acto_riesgo | advertir | encuesta | gestion_propia | informar_coordinar | tomar_datos | vender |
|---|---|---|---|---|---|---|---|
| base | 1/1 | 12/13 | 2/13 | 3/12 | 1/28 | 0/1 | 5/26 |
| c-codigo | 1/1 | 11/13 | 1/13 | 3/12 | 1/28 | 0/1 | 6/26 |
| c-consejos | 1/1 | 10/13 | 0/13 | 4/12 | 1/28 | 0/1 | 6/26 |
| c-freno | 1/1 | 13/13 | 3/13 | 8/12 | 1/28 | 0/1 | 10/26 |

### FA estrictas por escenario, y en las legítimas «ejemplares» y las que piden el DNI

| corrida | escenarios con alguna FA estricta | FA en ejemplares | FA en las que piden el DNI |
|---|---|---|---|
| base | 9/38 | 6/14 | 6/21 |
| c-codigo | 8/38 | 5/14 | 6/21 |
| c-consejos | 6/38 | 6/14 | 6/21 |
| c-freno | 15/38 | 8/14 | 12/21 |

### Tolerables y «debería avisar», caso por caso

| caso | etiqueta | base | c-codigo | c-consejos | c-freno |
|---|---|---|---|---|---|
| ENT-L-SOPORTE-005 | avisar | L11 | L11 | L11 | L5 |
| ENT-L-BANCO-001 | tolerable | L1 | L3 | L3 | L1 |
| ENT-L-BANCO-002 | tolerable | L4 | L4 | L4 | L2 |
| ENT-L-BANCO-003 | tolerable | L11 | L11 | L11 | L5 |
| ENT-L-BANCO-004 | tolerable | L6 | L4 | L6 | L4 |
| ENT-L-BANCO-005 | tolerable | L1 | L1 | L3 | L1 |
| ENT-L-BANCO-006 | tolerable | L2 | L2 | L2 | L2 |
| ENT-L-ENCUESTA-004 | tolerable | – | – | – | L6 |
| ENT-L-SELECCION-003 | tolerable | – | – | – | – |
| ENT-L-VENTAS-008 | tolerable | – | – | – | – |
| ENT-L-VENTAS-009 | tolerable | – | L19 | L19 | – |
| LEG-BA-01 | tolerable | L5 | L7 | L7 | L5 |
| LEG-BA-02 | tolerable | L3 | L3 | L3 | L3 |
| LEG-BA-03 | tolerable | L3 | L3 | – | L3 |
| LEG2-BA-01 | tolerable | L4 | – | – | L4 |
| LEG2-BA-02 | tolerable | L6 | L4 | L6 | L4 |
| LEG2-BA-03 | tolerable | – | – | – | L2 |
| LEG2-BA-05 | tolerable | L8 | L8 | L8 | L6 |
| LEG2-EN-04 | tolerable | – | – | – | L4 |

### Curva en todas las líneas de OTRA (estafas · a tiempo · FA estrictas · FA total)

| corrida | u=0.1 | u=0.2 | u=0.3 | u=0.4 | u=0.5 | u=0.6 | u=0.7 | u=0.8 | u=0.9 |
|---|---|---|---|---|---|---|---|---|---|
| base | 46 · 36 · 75 · 94 | 46 · 36 · 58 · 77 | 41 · 29 · 11 · 24 | 16 · 13 · 0 · 9 | 15 · 12 · 0 · 9 | 12 · 11 · 0 · 7 | 7 · 5 · 0 · 5 | 2 · 2 · 0 · 3 | 1 · 1 · 0 · 1 |
| c-codigo | 46 · 36 · 75 · 94 | 46 · 36 · 54 · 73 | 39 · 26 · 10 · 23 | 14 · 11 · 0 · 6 | 13 · 11 · 0 · 6 | 9 · 8 · 0 · 4 | 4 · 3 · 0 · 3 | 2 · 2 · 0 · 2 | 1 · 1 · 0 · 0 |
| c-consejos | 46 · 36 · 75 · 94 | 46 · 35 · 54 · 73 | 41 · 28 · 10 · 22 | 16 · 14 · 0 · 8 | 14 · 13 · 0 · 8 | 12 · 11 · 0 · 5 | 6 · 4 · 0 · 3 | 5 · 3 · 0 · 2 | 1 · 1 · 0 · 1 |
| c-freno | 46 · 36 · 75 · 94 | 46 · 36 · 63 · 82 | 42 · 30 · 20 · 36 | 17 · 15 · 1 · 11 | 16 · 15 · 1 · 11 | 14 · 11 · 0 · 8 | 6 · 4 · 0 · 6 | 1 · 1 · 0 · 4 | 1 · 1 · 0 · 1 |

### Avisos de un 0,3 exacto, latencia y motivo (dentro del alcance)

| corrida | avisos de 0,3 exacto | primera consulta (ms) | motivo (ms) | motivo válido |
|---|---|---|---|---|
| base | 55/65 | 214 / 269 | 696 / 948 | 65/65 |
| c-codigo | 56/62 | 218 / 270 | 743 / 972 | 62/62 |
| c-consejos | 53/63 | 219 / 272 | 712 / 950 | 63/63 |
| c-freno | 70/78 | 222 / 282 | 728 / 966 | 78/78 |

### FA estrictas que cambian contra la base, con su motivo, para leer a mano

**`c-codigo`:** 0 FA estrictas que la base no tiene; deja de avisar en 1 (ENT-L-ENCUESTA-006).

**`c-consejos`:** 3 FA estrictas que la base no tiene; deja de avisar en 4 (ENT-L-ENCUESTA-003, ENT-L-ENCUESTA-006, ENT-L-SELECCION-002, ENT-L-VENTAS-002).

| caso | intención | aviso | riesgo | motivo |
|---|---|---|---|---|
| ENT-L-DELIVERY-004 | informar_coordinar | L8 | 0.3 | «Los organismos oficiales no suelen solicitar el DNI por teléfono de esta manera.» |
| ENT-L-VENTAS-006 | vender | L14 | 0.3 | «Las promociones inesperadas y la indicación de llamar a un número externo para activar algo son comunes en intentos de fraude.» |
| LEG-ST-03 | gestion_propia | L1 | 0.3 | «Si no esperabas una llamada sobre un objeto que dejaste, es mejor verificar la identidad de TecnoFix por otros medios.» |

**`c-freno`:** 10 FA estrictas que la base no tiene; deja de avisar en 1 (ENT-L-ENCUESTA-006).

| caso | intención | aviso | riesgo | motivo |
|---|---|---|---|---|
| ENT-L-SOPORTE-002 | gestion_propia | L6 | 0.3 | «Te están pidiendo tu DNI para validar una garantía, lo cual puede ser un intento de robo de datos.» |
| ENT-L-SOPORTE-006 | gestion_propia | L8 | 0.3 | «Te están pidiendo tu número de documento para un envío, lo cual es una táctica común en estafas.» |
| ENT-L-VENTAS-003 | vender | L19 | 0.3 | «Aunque la llamada habla de un seguro, la forma en que te piden confirmar datos bancarios puede ser un intento de obtener información sensible.» |
| ENT-L-VENTAS-004 | vender | L4 | 0.3 | «Las ofertas no solicitadas por teléfono son una táctica común para intentar vender servicios o robar información.» |
| ENT-L-VENTAS-005 | vender | L5 | 0.3 | «Te están pidiendo tu DNI de forma inesperada para validar un formulario, lo cual es una táctica común de estafa.» |
| ENT-L-VENTAS-007 | vender | L11 | 0.3 | «Te están pidiendo datos personales sensibles como DNI y su sueldo, lo cual es una táctica común para robar información.» |
| LEG-ST-03 | gestion_propia | L1 | 0.3 | «Te están contactando sobre un objeto que dejaste, lo cual puede ser un intento de estafa.» |
| LEG2-ST-02 | gestion_propia | L6 | 0.3 | «Te están pidiendo tu DNI para validar una garantía, lo cual puede ser un intento de robo de datos.» |
| LEG2-ST-05 | gestion_propia | L2 | 0.3 | «Tené cuidado, porque te están pidiendo información sobre un problema de cuenta para intentar acceder a tus datos.» |
| LEG2-VE-04 | vender | L6 | 0.3 | «Te están pidiendo tu DNI de forma inesperada para un trámite, lo cual es una táctica común de estafa.» |

### alcance-91

| corrida | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA |
|---|---|---|---|---|
| base | 41/46 | 20/36 | 29/36 | 12/45 |
| c-codigo | 39/46 | 15/36 | 26/36 | 12/45 |
| c-consejos | 41/46 | 19/36 | 28/36 | 11/45 |
| c-freno | 42/46 | 24/36 | 30/36 | 19/45 |

