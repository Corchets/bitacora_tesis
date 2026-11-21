# #143, prueba de sensibilidad — análisis offline

Vista: alcance-140, 46 estafas (36 con pedido, 15 con cumplimiento) y 94 legítimas (29 cotidianas y 65 con pedido o mención). El aviso es la primera línea de OTRA con «riesgo ≥ 0,3».

## Humo de formato

| prompt | riesgo leído | errores | mismo riesgo que la base (dato) | riesgo ≥ 0,3 (dato) | riesgo ≥ 0,6 (dato) | resultado |
|---|---|---|---|---|---|---|
| `c-json-corte-riesgo` | 48/48 | — | 48/48 | 43 | 13 | PASA |
| `c-ancla-corte-riesgo` | 48/48 | — | 32/48 | 45 | 3 | PASA |
| `c-premisa-corte-riesgo` | 48/48 | — | 37/48 | 42 | 7 | PASA |
| `c-sin-freno-corte-riesgo` | 48/48 | — | 33/48 | 43 | 8 | PASA |

## Control de las corridas

| corrida | commit | líneas inválidas | control |
|---|---|---|---|
| base | ca4fab05d7 | 0/2177 | bien |
| c-ancla | ca4fab05d7 | 0/2177 | bien |
| c-premisa | ca4fab05d7 | 0/2177 | bien |
| c-sin-freno | ca4fab05d7 | 0/2177 | bien |
| base-rep | ca4fab05d7 | 0/1313 | bien |
| c-ancla-rep | ca4fab05d7 | 0/1313 | bien |
| c-premisa-rep | ca4fab05d7 | 0/1313 | bien |
| c-sin-freno-rep | ca4fab05d7 | 0/1313 | bien |

## Cifras

| corrida | estafas | antes del pedido | a tiempo | antes del cumplimiento | FA cotidianas | FA dudosas | FA |
|---|---|---|---|---|---|---|---|
| base | 37/46 | 15/36 | 25/36 | 12/15 | 1/29 | 25/65 | 26/94 |
| c-ancla | 39/46 | 15/36 | 28/36 | 13/15 | 3/29 | 24/65 | 27/94 |
| c-premisa | 40/46 | 19/36 | 29/36 | 12/15 | 2/29 | 24/65 | 26/94 |
| c-sin-freno | 40/46 | 20/36 | 27/36 | 12/15 | 3/29 | 33/65 | 36/94 |
| base-rep | 36/46 | 14/36 | 25/36 | 12/15 | 1/29 | 25/65 | 26/94 |
| c-ancla-rep | 40/46 | 18/36 | 29/36 | 14/15 | 3/29 | 24/65 | 27/94 |
| c-premisa-rep | 39/46 | 18/36 | 28/36 | 12/15 | 2/29 | 26/65 | 28/94 |
| c-sin-freno-rep | 41/46 | 20/36 | 28/36 | 13/15 | 3/29 | 35/65 | 38/94 |

## La regla

| variante | resultado | por qué |
|---|---|---|
| `c-ancla` | pasa | pasa (+2 estafas, +0 antes del pedido, +3 a tiempo, +1 antes del cumplimiento, FA cotidianas +2) |
| `c-premisa` | pasa | pasa (+3 estafas, +4 antes del pedido, +4 a tiempo, +0 antes del cumplimiento, FA cotidianas +1) |
| `c-sin-freno` | pasa | pasa (+3 estafas, +5 antes del pedido, +2 a tiempo, +0 antes del cumplimiento, FA cotidianas +2) |

**Resultado: queda `c-premisa`.**

## Aparte, solo para mirar

### Estafas que la base no avisa, y en qué línea las avisa cada variante

| caso | pedido | T_R | c-ancla | c-premisa | c-sin-freno |
|---|---|---|---|---|---|
| CV2-D-V-FAMILIAR-004 | REQUEST_TRANSFER | 22 | L24 | L10 | L26 |
| CV2-D-V-FAMILIAR-005 | REQUEST_TRANSFER | 20 | – | – | L20 |
| CV2-D-V-FAMILIAR-006 | REQUEST_TRANSFER | 22 | – | L14 | – |
| CV2-D-V-PREMIO-003 | REQUEST_PERSONAL_DATA | 13 | – | – | – |
| CV2-D-V-PREMIO-006 | sin pedido | — | – | – | L1 |
| CV2-D-V-SOPORTE-003 | REQUEST_SECRET | 11 | – | – | – |
| CV2-D-V-SOPORTE-005 | REQUEST_SECRET | 16 | – | L14 | – |
| CV2-D-V-WHATSAPP-003 | REQUEST_AUTH_CODE | 12 | – | – | – |
| CV2-D-V-WHATSAPP-006 | REQUEST_AUTH_CODE | 25 | L25 | – | L26 |

### FA por tipo de legítima

| corrida | cotidiana | pedido_razonable | mencion_sin_pedido |
|---|---|---|---|
| base | 1/29 | 12/38 | 13/27 |
| c-ancla | 3/29 | 11/38 | 13/27 |
| c-premisa | 2/29 | 12/38 | 12/27 |
| c-sin-freno | 3/29 | 15/38 | 18/27 |

### Curva en todas las líneas de OTRA (estafas · a tiempo · FA cotidianas · FA total)

| corrida | u=0.1 | u=0.2 | u=0.3 | u=0.4 | u=0.5 | u=0.6 | u=0.7 | u=0.8 | u=0.9 |
|---|---|---|---|---|---|---|---|---|---|
| base | 46 · 36 · 29 · 94 | 46 · 35 · 14 · 68 | 37 · 25 · 1 · 26 | 15 · 10 · 0 · 11 | 15 · 10 · 0 · 10 | 14 · 9 · 0 · 10 | 5 · 4 · 0 · 8 | 4 · 4 · 0 · 3 | 1 · 1 · 0 · 0 |
| c-ancla | 46 · 36 · 29 · 94 | 46 · 34 · 12 · 62 | 39 · 28 · 3 · 27 | 23 · 21 · 1 · 15 | 23 · 21 · 1 · 15 | 11 · 10 · 0 · 7 | 5 · 5 · 0 · 3 | 5 · 4 · 0 · 3 | 1 · 1 · 0 · 0 |
| c-premisa | 46 · 36 · 29 · 94 | 46 · 36 · 20 · 74 | 40 · 29 · 2 · 26 | 15 · 13 · 0 · 8 | 14 · 12 · 0 · 8 | 11 · 11 · 0 · 7 | 8 · 7 · 0 · 6 | 4 · 3 · 0 · 3 | 1 · 1 · 0 · 1 |
| c-sin-freno | 46 · 36 · 29 · 94 | 46 · 36 · 21 · 79 | 40 · 27 · 3 · 36 | 17 · 10 · 0 · 14 | 14 · 10 · 0 · 13 | 14 · 10 · 0 · 11 | 5 · 4 · 0 · 8 | 4 · 4 · 0 · 3 | 1 · 1 · 0 · 0 |

### Avisos de un 0,3 exacto, latencia y motivo (dentro del alcance)

| corrida | avisos de 0,3 exacto | primera consulta (ms) | motivo (ms) | motivo válido |
|---|---|---|---|---|
| base | 56/63 | 214 / 268 | 702 / 976 | 63/63 |
| c-ancla | 45/66 | 210 / 266 | 694 / 869 | 66/66 |
| c-premisa | 57/66 | 213 / 273 | 691 / 953 | 66/66 |
| c-sin-freno | 69/76 | 214 / 271 | 727 / 923 | 76/76 |

### FA nuevas de cada variante, con su motivo, para leer a mano

**`c-ancla`:** 4 FA que la base no tiene.

| caso | tipo | aviso | riesgo | motivo |
|---|---|---|---|---|
| ENT-L-DELIVERY-001 | cotidiana | L15 | 0.5 | «No debes firmar documentos ni compartir datos personales por teléfono, especialmente si no esperabas un paquete.» |
| ENT-L-ENCUESTA-003 | cotidiana | L11 | 0.3 | «Aunque la llamada comienza con una excusa legítima, la insistencia en la posibilidad de» |
| ENT-L-SOPORTE-006 | mencion_sin_pedido | L8 | 0.3 | «Es sospechoso que te pidan tu número de documento para un envío, ya que esto puede ser un intento de robo de identidad.» |
| ENT-L-VENTAS-006 | mencion_sin_pedido | L12 | 0.3 | «Tené cuidado, ya que te llaman de todos lados y te están ofreciendo promociones que pueden ser intentos de venta no deseados.» |

**`c-premisa`:** 4 FA que la base no tiene.

| caso | tipo | aviso | riesgo | motivo |
|---|---|---|---|---|
| ENT-L-ENCUESTA-003 | cotidiana | L9 | 0.3 | «Es sospechoso que te llamen con un número desconocido y que te mencionen un panel de encuestas sin tener tu información de forma verificable.» |
| ENT-L-ENCUESTA-006 | mencion_sin_pedido | L12 | 0.3 | «Aunque la llamada se centra en una encuesta, la mención de información sensible como la tarjeta y el reintegro es una táctica común para generar confianza y luego intentar obtener más datos.» |
| ENT-L-SELECCION-002 | mencion_sin_pedido | L13 | 0.3 | «Te están pidiendo que les des un código de acceso que es tu clave para entrar a una evaluación, lo cual es una táctica común de estafa.» |
| ENT-L-VENTAS-003 | pedido_razonable | L17 | 0.3 | «Aunque la información sobre el seguro es específica, es importante verificar la legitimidad de la aseguradora antes de dar cualquier dato o compromiso.» |

**`c-sin-freno`:** 11 FA que la base no tiene.

| caso | tipo | aviso | riesgo | motivo |
|---|---|---|---|---|
| ENT-L-ENCUESTA-003 | cotidiana | L9 | 0.3 | «Te están llamando con un número aleatorio y te están presionando para que aceptes participar en una encuesta, lo cual es una táctica común de phishing.» |
| ENT-L-ENCUESTA-006 | mencion_sin_pedido | L12 | 0.3 | «Aunque la llamada se centra en una encuesta, la mención de problemas con la tarjeta y la entrega de información sensible es una táctica común para generar confianza y luego intentar obtener datos.» |
| ENT-L-MEDICO-003 | mencion_sin_pedido | L1 | 0.3 | «No se puede verificar la legitimidad de la llamada, es necesario seguir escuchando para determinar si es una estafa.» |
| ENT-L-SELECCION-002 | mencion_sin_pedido | L13 | 0.3 | «Te están pidiendo un código de acceso para una evaluación, lo cual es una táctica común para obtener información o intentar engañarte.» |
| ENT-L-SOPORTE-002 | pedido_razonable | L6 | 0.3 | «Desconfía de que una empresa legítima pida datos sensibles como el DNI por teléfono sin una verificación previa.» |
| ENT-L-SOPORTE-006 | mencion_sin_pedido | L8 | 0.3 | «Te están pidiendo datos personales sensibles como el número de documento para un envío, lo cual es una táctica común en estafas.» |
| ENT-L-VENTAS-003 | pedido_razonable | L5 | 0.3 | «Las llamadas que inician con información genérica sobre seguros o beneficios suelen ser el primer paso para intentar obtener datos personales o instalar software malicioso.» |
| ENT-L-VENTAS-004 | cotidiana | L4 | 0.3 | «Tené cuidado, porque te están ofreciendo un servicio sin que hayas solicitado nada.» |
| ENT-L-VENTAS-005 | mencion_sin_pedido | L5 | 0.3 | «Desconfía de que le pidan datos personales como el DNI por teléfono, especialmente si la comunicación no es totalmente verificable.» |
| ENT-L-VENTAS-006 | mencion_sin_pedido | L14 | 0.3 | «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener datos o redirigirte a otra llamada.» |
| ENT-L-VENTAS-007 | pedido_razonable | L13 | 0.3 | «Es común que estafadores soliciten datos personales sensibles como DNI y su sueldo bajo el pretexto de una oferta comercial.» |

### alcance-91

| corrida | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA |
|---|---|---|---|---|
| base | 37/46 | 15/36 | 25/36 | 12/45 |
| c-ancla | 39/46 | 15/36 | 28/36 | 15/45 |
| c-premisa | 40/46 | 19/36 | 29/36 | 14/45 |
| c-sin-freno | 40/46 | 20/36 | 27/36 | 22/45 |

