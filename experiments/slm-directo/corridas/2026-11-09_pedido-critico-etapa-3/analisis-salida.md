# #143, segunda vuelta, etapa 3: C con campo contra C sin alerta — análisis offline

Vista dentro del alcance: 46 estafas de corpus_v2 (36 con pedido) y 94 legítimas entrantes. «Cualquier aviso»: riesgo ≥ 0.3, o `pedido_critico` en C con campo, en cualquier línea.

## Humo de formato

| prompt | JSON leído | llegan al tope | tokens generados (mín / mediana / máx) | mismo riesgo que c-json-corte (dato) | pedido_critico en true (dato) | resultado |
|---|---|---|---|---|---|---|
| `c-sin-alerta` | 48/48 | 0 | 14 / 14 / 14 | 36/48 | — | PASA |
| `c-con-campo` | 48/48 | 0 | 24 / 24 / 24 | 23/48 | 3 | PASA |

## Control de las corridas

| corrida | casos | líneas | inválidas | ms primera consulta p50 / p95 | commit |
|---|---|---|---|---|---|
| c-sin-alerta | 244 | 4325 | 0 | 240 / 402 | c3c1ffa9b7 |
| c-con-campo | 244 | 4325 | 0 | 288 / 352 | c3c1ffa9b7 |
| c-sin-alerta-rep | 140 | 2621 | 0 | 238 / 399 | c3c1ffa9b7 |
| c-con-campo-rep | 140 | 2621 | 0 | 284 / 342 | c3c1ffa9b7 |

Sin problemas de control: mismo commit, digest, Ollama, parámetros, prompts, casos y avisos, y están las corridas de C de la etapa 2.

## Regla de la etapa 3

### 1. La base contra C de la etapa 2

| configuración | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA | contra la etapa 2 |
|---|---|---|---|---|---|
| C de la etapa 2, «riesgo ≥ 0,3 o alerta» | 36/46 | 17/36 | 25/36 | 27/94 | — |
| C sin alerta, «riesgo ≥ 0,3» | 39/46 | 18/36 | 25/36 | 32/94 | +3 estafas, +1 antes del pedido, +0 a tiempo, +5 FA |

Alguna cifra se mueve más de ±2: **la base es el prompt de C de la etapa 2, cortado tras el riesgo** (c-json-corte y su repetición, con «riesgo ≥ 0,3» y sin la alerta).

### 2. C con campo contra la base, en «cualquier aviso»

La base (C de la etapa 2, cortado tras el riesgo) tiene 27/94 FA, así que C con campo puede tener hasta 32.

| configuración | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA | contra la base | veredicto |
|---|---|---|---|---|---|---|
| base: C de la etapa 2, cortado tras el riesgo | 36/46 | 17/36 | 25/36 | 27/94 | — | — |
| base, repetición (los 140) | 36/46 | 16/36 | 25/36 | 26/94 | — | — |
| C con campo (`c-con-campo`) | 37/46 | 15/36 | 21/36 | 18/94 | +1 estafas, -2 antes del pedido, -4 a tiempo | pierde 3 o más: no se adopta |
| C con campo, repetición (los 140) | 36/46 | 16/36 | 22/36 | 17/94 | +0 estafas, +0 antes del pedido, -3 a tiempo | contra la repetición de la base |

### 3. alcance-91: las 46 estafas y una legítima por escenario, sin dudosas

| configuración | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA | veredicto en alcance-91 |
|---|---|---|---|---|---|
| base | 36/46 | 17/36 | 25/36 | 13/45 | — |
| C con campo | 37/46 | 15/36 | 21/36 | 9/45 | pierde 3 o más: no se adopta |

En alcance-91 el resultado no se invierte.

**Queda la base, C de la etapa 2, cortado tras el riesgo, provisorio hasta la reserva.**

### 4. «Solo OTRA» contra todas las líneas

| configuración | corrida | todas las líneas | solo OTRA | solo OTRA contra todas |
|---|---|---|---|---|
| base | corrida | 36/46 · 17/36 · 25/36 · FA 27/94 | 35/46 · 15/36 · 25/36 · FA 24/94 | -1 estafas, -2 antes del pedido, +0 a tiempo, -3 FA |
| base | repetición | 36/46 · 16/36 · 25/36 · FA 26/94 | 36/46 · 15/36 · 25/36 · FA 25/94 | +0 estafas, -1 antes del pedido, +0 a tiempo, -1 FA |
| C con campo | corrida | 37/46 · 15/36 · 21/36 · FA 18/94 | 33/46 · 13/36 · 20/36 · FA 18/94 | -4 estafas, -2 antes del pedido, -1 a tiempo, +0 FA |
| C con campo | repetición | 36/46 · 16/36 · 22/36 · FA 17/94 | 34/46 · 13/36 · 20/36 · FA 17/94 | -2 estafas, -3 antes del pedido, -2 a tiempo, +0 FA |

**«Solo OTRA» se adopta** para la configuración que queda (base).

## Aparte, solo para mirar

### Alerta fuerte (`pedido_critico`), en C con campo

Pedido crítico de la referencia: el primero con código, clave, plata, acceso remoto o acción de seguridad; los datos personales no cuentan. A tiempo: en esa línea o antes.

| corrida | estafas con pedido crítico, a tiempo | tarde | estafas sin pedido crítico | legítimas (los 140) | legítimas (alcance-91) |
|---|---|---|---|---|---|
| C con campo | 12/30 | 3 | 2/16 | 5/94 | 2/45 |
| C con campo, repetición | 12/30 | 3 | 2/16 | 5/94 | 2/45 |

Legítimas con alerta fuerte: ENT-L-BANCO-002 L12, ENT-L-BANCO-006 L7, ENT-L-SOPORTE-005 L13, ENT-L-VENTAS-009 L20, LEG2-BA-02 L7.

### Estafas sin pedido

Avisadas: base: C de la etapa 2, cortado tras el riesgo 9/10; C con campo 8/10.

### Curva dentro del alcance, en todas las líneas

Cada celda: estafas (/46) · antes del pedido (/36) · a tiempo (/36) · FA (/94). C con campo suma siempre `pedido_critico`.

| regla | base: C de la etapa 2, cortado tras el riesgo | base, repetición | C con campo | C con campo, repetición |
|---|---|---|---|---|
| riesgo ≥ 0.1 | 46/46 · 36/36 · 36/36 · FA 94/94 | 46/46 · 36/36 · 36/36 · FA 94/94 | 46/46 · 36/36 · 36/36 · FA 94/94 | 46/46 · 36/36 · 36/36 · FA 94/94 |
| riesgo ≥ 0.2 | 46/46 · 36/36 · 36/36 · FA 72/94 | 46/46 · 36/36 · 36/36 · FA 69/94 | 45/46 · 34/36 · 34/36 · FA 63/94 | 46/46 · 34/36 · 35/36 · FA 64/94 |
| riesgo ≥ 0.3 | 36/46 · 17/36 · 25/36 · FA 27/94 | 36/46 · 16/36 · 25/36 · FA 26/94 | 37/46 · 15/36 · 21/36 · FA 18/94 | 36/46 · 16/36 · 22/36 · FA 17/94 |
| riesgo ≥ 0.4 | 15/46 · 6/36 · 10/36 · FA 9/94 | 15/46 · 6/36 · 11/36 · FA 9/94 | 17/46 · 3/36 · 14/36 · FA 6/94 | 17/46 · 4/36 · 14/36 · FA 6/94 |
| riesgo ≥ 0.5 | 15/46 · 5/36 · 10/36 · FA 9/94 | 15/46 · 5/36 · 11/36 · FA 9/94 | 17/46 · 3/36 · 14/36 · FA 5/94 | 17/46 · 4/36 · 14/36 · FA 5/94 |
| riesgo ≥ 0.6 | 14/46 · 5/36 · 10/36 · FA 9/94 | 14/46 · 5/36 · 11/36 · FA 9/94 | 17/46 · 3/36 · 14/36 · FA 5/94 | 17/46 · 4/36 · 14/36 · FA 5/94 |
| riesgo ≥ 0.7 | 6/46 · 0/36 · 4/36 · FA 6/94 | 5/46 · 0/36 · 4/36 · FA 6/94 | 17/46 · 3/36 · 14/36 · FA 5/94 | 17/46 · 4/36 · 14/36 · FA 5/94 |
| riesgo ≥ 0.8 | 5/46 · 0/36 · 4/36 · FA 4/94 | 5/46 · 0/36 · 4/36 · FA 3/94 | 17/46 · 3/36 · 14/36 · FA 5/94 | 17/46 · 4/36 · 14/36 · FA 5/94 |
| riesgo ≥ 0.9 | 1/46 · 0/36 · 1/36 · FA 0/94 | 1/46 · 0/36 · 1/36 · FA 0/94 | 17/46 · 3/36 · 14/36 · FA 5/94 | 17/46 · 4/36 · 14/36 · FA 5/94 |
| riesgo ≥ 1 | 0/46 · 0/36 · 0/36 · FA 0/94 | 0/46 · 0/36 · 0/36 · FA 0/94 | 17/46 · 3/36 · 14/36 · FA 5/94 | 17/46 · 4/36 · 14/36 · FA 5/94 |

La curva completa, con las dos lecturas, también está en `curva.csv`.

### Intervalos de Wilson en la regla

| serie | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA |
|---|---|---|---|---|
| base: C de la etapa 2, cortado tras el riesgo | 36/46, 78 % [64–88] | 17/36, 47 % [32–63] | 25/36, 69 % [53–82] | 27/94, 29 % [21–39] |
| base, repetición | 36/46, 78 % [64–88] | 16/36, 44 % [30–60] | 25/36, 69 % [53–82] | 26/94, 28 % [20–37] |
| C con campo | 37/46, 80 % [67–89] | 15/36, 42 % [27–58] | 21/36, 58 % [42–73] | 18/94, 19 % [12–28] |
| C con campo, repetición | 36/46, 78 % [64–88] | 16/36, 44 % [30–60] | 22/36, 61 % [45–75] | 17/94, 18 % [12–27] |

### Estafas por primer pedido de la referencia (avisadas; antes / en / después del pedido)

| primer pedido | estafas | base: C de la etapa 2, cortado tras el riesgo | C con campo |
|---|---|---|---|
| sin pedido | 10 | 9 | 8 |
| REQUEST_AUTH_CODE | 10 | 7 (5 / 2 / 0) | 9 (6 / 1 / 2) |
| REQUEST_SECRET | 7 | 5 (4 / 0 / 1) | 5 (3 / 0 / 2) |
| REQUEST_TRANSFER | 9 | 6 (3 / 3 / 0) | 6 (3 / 1 / 2) |
| REQUEST_PERSONAL_DATA | 6 | 5 (3 / 2 / 0) | 5 (1 / 3 / 1) |
| REQUEST_SECURITY_ACTION | 2 | 2 (2 / 0 / 0) | 2 (2 / 0 / 0) |
| REQUEST_REMOTE_ACCESS | 2 | 2 (0 / 1 / 1) | 2 (0 / 1 / 1) |

### Pares discordantes entre la base y C con campo, dentro del alcance

| cifra | solo la base | solo C con campo |
|---|---|---|
| estafas avisadas | CV2-D-V-PREMIO-002, CV2-D-V-WHATSAPP-008 | CV2-D-V-FAMILIAR-004, CV2-D-V-WHATSAPP-003, CV2-D-V-WHATSAPP-005 |
| avisos a tiempo | CV2-D-V-FAMILIAR-001, CV2-D-V-ORGANISMO_PREVISIONAL-003, CV2-D-V-PREMIO-002, CV2-D-V-PREMIO-004, CV2-D-V-WHATSAPP-001 | CV2-D-V-WHATSAPP-005 |
| FA | ENT-L-DELIVERY-004, ENT-L-ENCUESTA-006, ENT-L-SOPORTE-003, ENT-L-VENTAS-003, LEG-BA-03, LEG-CC-03, LEG-ST-03, LEG2-CC-06, LEG2-ST-03, LEG2-ST-05 | ENT-L-BANCO-003 |

### FA por lote, por pedido de datos y al comienzo

| legítimas | llamadas | base: C de la etapa 2, cortado tras el riesgo | C con campo |
|---|---|---|---|
| LEG (21) | 21 | 5 | 2 |
| LEG2 (28) | 28 | 8 | 5 |
| ENT-L (42) | 42 | 14 | 11 |
| selección (3) | 3 | 0 | 0 |
| piden datos personales | 64 | 21 | 16 |
| no piden datos personales | 30 | 6 | 2 |
| una por escenario, sin dudosas (alcance-91) | 45 | 13 | 9 |
| FA en L1–L3 | 94 | 13 | 5 |

### Otros grupos (estafas · antes · a tiempo · FA)

| grupo | base: C de la etapa 2, cortado tras el riesgo | C con campo | reglas (sin modelo) | reglas_v2 (sin modelo) |
|---|---|---|---|---|
| dentro del alcance (los 140) | 36/46 · 17/36 · 25/36 · FA 27/94 | 37/46 · 15/36 · 21/36 · FA 18/94 | 42/46 · 27/36 · 32/36 · FA 69/94 | 11/46 · 3/36 · 9/36 · FA 36/94 |
| alcance-91 | 36/46 · 17/36 · 25/36 · FA 13/45 | 37/46 · 15/36 · 21/36 · FA 9/45 | 42/46 · 27/36 · 32/36 · FA 37/45 | 11/46 · 3/36 · 9/36 · FA 17/45 |
| corpus_v2 entero, sin alcance (46 + 51) | 36/46 · 17/36 · 25/36 · FA 13/51 | 37/46 · 15/36 · 21/36 · FA 5/51 | 42/46 · 27/36 · 32/36 · FA 37/51 | 11/46 · 3/36 · 9/36 · FA 6/51 |
| las 7 legítimas de corpus_v2 dentro del alcance | FA 0/7 | FA 0/7 | FA 3/7 | FA 1/7 |
| manuales: laboratorio | 16/16 · 15/16 · 16/16 · FA 8/10 | 16/16 · 15/16 · 16/16 · FA 8/10 | 13/16 · 0/16 · 11/16 · FA 1/10 | 13/16 · 0/16 · 11/16 · FA 0/10 |
| manuales: piloto_escrito | 7/7 · 6/7 · 7/7 · FA 3/7 | 7/7 · 6/7 · 7/7 · FA 1/7 | 6/7 · 3/7 · 6/7 · FA 7/7 | 6/7 · 0/7 · 5/7 · FA 0/7 |
| manuales: trampa | 5/6 · 4/5 · 5/5 · FA 4/7 | 6/6 · 4/5 · 5/5 · FA 3/7 | 4/6 · 2/5 · 3/5 · FA 6/7 | 2/6 · 1/5 · 2/5 · FA 2/7 |

### Corrida y repetición, dentro del alcance (ADR 0005: «para reconsiderarla, más de 2 casos»)

| versión | casos con otra línea de aviso | de esos, cambian una cifra | riesgo escrito igual | `pedido_critico` igual |
|---|---|---|---|---|
| C sin alerta | 16 (CV2-D-V-BANCO-002, CV2-D-V-BANCO-009, CV2-D-V-FAMILIAR-004, CV2-D-V-ORGANISMO_PREVISIONAL-002, CV2-D-V-ORGANISMO_PREVISIONAL-003, CV2-D-V-ORGANISMO_PREVISIONAL-004, CV2-D-V-PREMIO-004, CV2-D-V-SOPORTE-001, CV2-D-V-SOPORTE-004, CV2-D-V-WHATSAPP-007, ENT-L-BANCO-001, ENT-L-ENCUESTA-006, ENT-L-VENTAS-002, ENT-L-VENTAS-003, ENT-L-VENTAS-006, LEG2-CC-06) | 5 (CV2-D-V-ORGANISMO_PREVISIONAL-002, CV2-D-V-PREMIO-004, CV2-D-V-SOPORTE-001, CV2-D-V-SOPORTE-004, ENT-L-ENCUESTA-006) | 2429/2621 (92.7 %) | — |
| C con campo | 8 (CV2-D-V-BANCO-005, CV2-D-V-BANCO-012, CV2-D-V-FAMILIAR-003, CV2-D-V-FAMILIAR-004, CV2-D-V-PREMIO-005, CV2-D-V-SOPORTE-001, ENT-L-BANCO-003, ENT-L-BANCO-004) | 3 (CV2-D-V-PREMIO-005, CV2-D-V-SOPORTE-001, ENT-L-BANCO-003) | 2524/2621 (96.3 %) | 2615/2621 |

### C sin alerta contra C de la etapa 2, línea por línea

Riesgo escrito igual en 3345/4325 líneas de los 244 (77.3 %). Entre dos corridas iguales de la etapa 2 coincidía en el 95,9 %.

### Latencia en T4 por tipo de consulta (ms de pared; p50 / p95, dentro del alcance)

| corrida | consulta de C (ms) | solo en líneas de OTRA (ms) | líneas de OTRA | tokens generados | tokens del prompt | motivo (ms) | motivos pedidos |
|---|---|---|---|---|---|---|---|
| C sin alerta | 239 / 400 | 240 / 402 | 1313 | 14 / 14 | 670 / 987 | — | 0 |
| C con campo | 288 / 346 | 289 / 347 | 1313 | 24 / 24 | 860 / 1177 | 800 / 943 | 22 |
| C sin alerta, repetición | 238 / 399 | 240 / 403 | 1313 | 14 / 14 | 670 / 987 | — | 0 |
| C con campo, repetición | 284 / 342 | 286 / 342 | 1313 | 24 / 24 | 860 / 1177 | 765 / 929 | 22 |
| C de la etapa 2 (`c-json-corte`, cortado tras la alerta) | 276 / 335 | 277 / 337 | 1313 | 24 / 24 | 777 / 1094 | 690 / 847 | 24 |

### Costo por llamada de la política (simulado con las mismas salidas)

La política: consultar en cada línea (o solo en las de OTRA), seguir después del primer aviso, que no se apaga y muestra un texto fijo, y cortar después de la alerta fuerte, con su motivo. No cambia la detección. Cada celda: mediana / p95 de consultas y de ms por llamada; el motivo se suma si la llamada tiene alerta fuerte.

| serie | líneas consultadas | llamadas | consultas | ms |
|---|---|---|---|---|
| base: C de la etapa 2, cortado tras el riesgo | todas | estafas | 21 / 31 | 6807 / 9689 |
| base: C de la etapa 2, cortado tras el riesgo | todas | legítimas | 14 / 32 | 4324 / 8918 |
| base: C de la etapa 2, cortado tras el riesgo | solo OTRA | estafas | 11 / 15 | 3415 / 4992 |
| base: C de la etapa 2, cortado tras el riesgo | solo OTRA | legítimas | 7 / 16 | 2391 / 4512 |
| C con campo | todas | estafas | 21 / 30 | 6192 / 8631 |
| C con campo | todas | legítimas | 12 / 27 | 4196 / 8592 |
| C con campo | solo OTRA | estafas | 10 / 15 | 3185 / 4493 |
| C con campo | solo OTRA | legítimas | 6 / 14 | 2189 / 4446 |

### Motivo de C (medición escrita antes de correr)

En cada línea en que se pidió el motivo (la primera alerta fuerte de la llamada; la base no lo pide), dentro del alcance: JSON válido con motivo; evidencia textual de OTRA hasta esa línea; evidencia textual en cualquier voz; y motivos que nombran un pedido cuando la referencia todavía no marca un pedido crítico (por palabras; se leen a mano abajo).

| corrida | motivos pedidos | JSON válido con motivo | evidencia de OTRA | evidencia en cualquier voz | nombran un pedido antes de que ocurra (marcados) |
|---|---|---|---|---|---|
| C sin alerta | 0 | 0/0 | 0/0 | 0/0 | 0/0 |
| C con campo | 22 | 22/22 | 21/22 | 22/22 | 6/8 |
| C sin alerta, repetición | 0 | 0/0 | 0/0 | 0/0 | 0/0 |
| C con campo, repetición | 22 | 22/22 | 21/22 | 22/22 | 6/9 |

Marcados para leer:

- C con campo, CV2-D-V-BANCO-004 L10 (vishing): «Te están pidiendo que confirmes algo enviándote un código, lo cual es una táctica común para robar tus datos.»
- C con campo, CV2-D-V-BANCO-005 L11 (vishing): «Te están pidiendo que ingreses tu clave de seis dígitos, lo cual es una táctica común para robar tus credenciales.»
- C con campo, CV2-D-V-ORGANISMO_PREVISIONAL-001 L12 (vishing): «Te están pidiendo datos sensibles como DNI y fotos de documentos, lo cual es una táctica común de estafa.»
- C con campo, CV2-D-V-PREMIO-001 L10 (vishing): «Te están pidiendo datos personales sensibles como tu DNI y una foto, lo cual es una táctica común para robar tu identidad.»
- C con campo, CV2-D-V-WHATSAPP-005 L13 (vishing): «Te están pidiendo un código de seis cifras que te enviaron por WhatsApp, lo cual es una táctica común para robar contraseñas o códigos de verificación.»
- C con campo, ENT-L-BANCO-006 L7 (legitima): «Te están pidiendo un código que te llegó por mensaje, lo cual es una táctica común de estafa.»
- C con campo, repetición, CV2-D-V-BANCO-004 L10 (vishing): «Te están pidiendo que confirmes algo enviándote un código, lo cual es una táctica común para robar tus datos.»
- C con campo, repetición, CV2-D-V-BANCO-005 L11 (vishing): «Te están pidiendo que ingreses tu clave de seis dígitos, lo cual es una táctica común para robar tus credenciales.»
- C con campo, repetición, CV2-D-V-ORGANISMO_PREVISIONAL-001 L12 (vishing): «Te están pidiendo datos sensibles como DNI y fotos de documentos, lo cual es una táctica común de estafa.»
- C con campo, repetición, CV2-D-V-PREMIO-001 L10 (vishing): «Te están pidiendo datos personales sensibles como tu DNI y una foto, lo cual es una táctica común para robar tu identidad.»
- C con campo, repetición, CV2-D-V-WHATSAPP-005 L13 (vishing): «Te están pidiendo un código de seis cifras que te enviaron por WhatsApp, lo cual es una táctica común para robar contraseñas o códigos de verificación.»
- C con campo, repetición, ENT-L-BANCO-006 L7 (legitima): «Te están pidiendo un código que te llegó por mensaje, lo cual es una táctica común de estafa.»

### Controles de ventas y préstamos (solo para mirar; L = primer aviso; F = primera alerta fuerte)

| control | clase | alcance | qué prueba | c-con-campo | c-sin-alerta |
|---|---|---|---|---|---|
| CTRL-L-VENTA-PORTABILIDAD | legitima_dificil | dentro | Venta telefónica de portabilidad que pide DNI, número de trámite, fecha de nacimiento, domicilio y correo, y anuncia un código por SMS que la persona carga sola, sin dictarlo. | L4 | L3 |
| CTRL-V-OPERADOR-SMS | vishing | dentro | Falso operador de telefonía que inventa un problema de titularidad, suma un descuento para jubilados y pide leer o reenviar el código del SMS para quedarse con el WhatsApp. | L5 F10 | L4 |
| CTRL-L-BANCO-OFRECE-PRESTAMO | legitima_dificil | dentro | El banco llama con un préstamo preaprobado, confirma nombre y DNI y deja la aceptación en la app o el home banking, con acreditación a las 48 horas hábiles y sin pedir token ni claves. | L5 | L4 |
| CTRL-V-BANCO-PRESTAMO-TOKEN | vishing | dentro | Falso empleado del banco que ofrece un préstamo preaprobado con acreditación inmediata y, para «confirmarlo», pide generar el código del token y dictarlo. | L4 F10 | L2 |
| CTRL-L-PIDE-PRESTAMO | legitima_dificil | fuera | La persona llama a su banco a pedir un préstamo y el operador le pide DNI, fecha de nacimiento, ingresos, empleador, domicilio y correo, pero deja la confirmación en el home banking y no pide códigos. | – | L3 |
| CTRL-V-PRESTAMO-REDES | vishing | fuera | La persona llama a un número de préstamos visto en redes, se lo aprueban al instante y le piden transferir por adelantado una comisión a una billetera virtual. | L5 F13 | L3 |

