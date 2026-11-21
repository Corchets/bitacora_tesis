# #143, configuración congelada: humo en desarrollo — análisis offline

Vista dentro del alcance: 46 estafas de corpus_v2 (36 con pedido) y 94 legítimas entrantes. Cifras: estafas avisadas, avisos antes del pedido (T_A < T_R), a tiempo (T_A ≤ T_R) y FA. Las líneas inválidas no avisan.

## Humo de formato

| riesgo leído | errores | tokens generados (mín / mediana / máx) | mismo riesgo que c-json-corte (dato) | riesgos con dos decimales (dato) | resultado |
|---|---|---|---|---|---|
| 48/48 | — | 14 / 14 / 14 | 43/48 | 1 | PASA |

## Control de la corrida

Commit `58b09975fe`, 244 casos, 3026 líneas registradas, 1548 consultadas.

Sin problemas.

## La regla

**0. Humo de formato:** pasa.

**1. Control:** sin problemas.

**2. Líneas inválidas:** 0 de 1548 consultadas; el máximo es el 1%.

**3. Contra la lectura simulada de la etapa 3** (`c-json-corte` de la etapa 2, «riesgo ≥ 0,3», solo OTRA):

| configuración | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA |
|---|---|---|---|---|
| lectura simulada de la etapa 3 | 35/46 | 15/36 | 25/36 | 24/94 |
| esta corrida | 36/46 | 14/36 | 26/36 | 25/94 |

Diferencias: +1 estafas, -1 antes del pedido, +1 a tiempo, +1 FA.

**Resultado: la configuración queda lista para la evaluación final.**

- se cumplen las tres condiciones

## Aparte, solo para mirar

### alcance-91 e intervalos de Wilson

| vista | estafas | antes del pedido | a tiempo (antes o en el pedido) | FA |
|---|---|---|---|---|
| alcance-140 | 36/46 | 14/36 | 26/36 | 25/94 |
| alcance-91 | 36/46 | 14/36 | 26/36 | 12/45 |

Wilson (95 %): estafas 36/46, 78 % [64–88]; a tiempo 26/36, 72 % [56–84]; FA 25/94, 27 % [19–36].

### Casos con otra línea de aviso que la lectura simulada (dentro del alcance)

10 de 140.

| caso | clase | simulada | esta corrida |
|---|---|---|---|
| CV2-D-V-BANCO-003 | vishing | L3 | L1 |
| CV2-D-V-BANCO-006 | vishing | L10 | L2 |
| CV2-D-V-ORGANISMO_PREVISIONAL-001 | vishing | L10 | L12 |
| CV2-D-V-SOPORTE-004 | vishing | L18 | L24 |
| CV2-D-V-WHATSAPP-004 | vishing | L1 | L5 |
| CV2-D-V-WHATSAPP-005 | vishing | – | L14 |
| ENT-L-BANCO-003 | legitima | – | L5 |
| ENT-L-BANCO-004 | legitima | L6 | L4 |
| ENT-L-VENTAS-003 | legitima | L19 | – |
| LEG2-CC-06 | legitima | – | L6 |

### Avisos que salen de un 0,3 exacto (dentro del alcance)

- estafas: 31 de 36 avisos.
- FA: 23 de 25 avisos.

### Latencia en T4 (ms de pared; p50 / p95, dentro del alcance)

| primera consulta (ms) | consultas | tokens generados | motivo (ms) | total en la línea del aviso (ms) | avisos |
|---|---|---|---|---|---|
| 206 / 267 | 892 | 14 / 14 | 678 / 835 | 900 / 1081 | 61 |

En la etapa 3: C sin alerta, 239 ms (p50) con 14 tokens; el motivo de C con campo, unos 800 ms.

### Costo por llamada, hasta el aviso o el final (mediana / p95)

| llamadas | consultas | ms |
|---|---|---|
| estafas | 5 / 14 | 1728 / 3227 |
| legítimas | 6 / 13 | 1442 / 3084 |

### Motivo de C (la medición de la etapa 3, escrita antes de correr)

En cada aviso dentro del alcance: JSON válido con motivo; evidencia textual de OTRA hasta esa línea; evidencia textual en cualquier voz; y motivos que nombran un pedido cuando la referencia todavía no marca un pedido crítico (por palabras; se leen a mano).

| motivos pedidos | JSON válido con motivo | evidencia de OTRA | evidencia en cualquier voz | nombran un pedido antes de que ocurra (marcados) |
|---|---|---|---|---|
| 61 | 61/61 | 60/61 | 61/61 | 8/49 |

Marcados en estafas: CV2-D-V-BANCO-005, CV2-D-V-ORGANISMO_PREVISIONAL-001, CV2-D-V-ORGANISMO_PREVISIONAL-006, CV2-D-V-PREMIO-001, CV2-D-V-PREMIO-004, CV2-D-V-WHATSAPP-008.

### Los motivos de las FA, para leer a mano

Todas las legítimas de la vista que avisan. «Marcado»: nombra un pedido por palabras. Se leen todos: si alguno engaña, decide Mateo si el aviso muestra el motivo o el texto fijo. El prompt del motivo no se cambia.

| caso | aviso | riesgo | marcado | evidencia | motivo |
|---|---|---|---|---|---|
| ENT-L-BANCO-001 | L1 | 0.3 |  | «buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica» | «Aunque suena a un banco, siempre es mejor verificar la identidad antes de compartir cualquier dato.» |
| ENT-L-BANCO-002 | L2 | 0.3 |  | «Hola, buen día. Te llamo del banco, del sector de seguridad.» | «Aunque suena a un banco, no podemos confirmar la identidad de quien llama, así que mantente alerta.» |
| ENT-L-BANCO-003 | L5 | 0.3 |  | «Gracias, señor Sosa. ¿Me confirma los últimos tres números de su documento?» | «Los bancos legítimos rara vez solicitan datos sensibles como los últimos tres números de DNI por teléfono sin un contexto previo claro.» |
| ENT-L-BANCO-004 | L4 | 0.3 |  | «valeria valeria para validar su identidad me dice su dni» | «Desconfíe de que le pidan datos personales como el DNI por teléfono sin una previa confirmación de identidad.» |
| ENT-L-BANCO-005 | L1 | 0.3 |  | «Buen día, le hablo de prevención de fraudes del banco.» | «Las llamadas de prevención de fraudes suelen ser el inicio de estafas donde intentan obtener información sensible.» |
| ENT-L-BANCO-006 | L2 | 0.3 | sí | «Hola, buenas tardes. Te hablo del banco, por tu app.» | «Desconfía de que te contacten por un número no agendado y que te pidan información sensible a través de una app.» |
| ENT-L-DELIVERY-004 | L8 | 0.3 |  | «El cartero dejó constancia de que no atendió nadie. ¿Puede ser que el timbre no ande?» | «Te están pidiendo tu número de documento de forma inesperada, lo cual es una táctica común para obtener datos personales.» |
| ENT-L-SOPORTE-001 | L3 | 0.3 |  | «para validar que hablo con la titular me confirmás tu dni» | «No es seguro confirmar datos personales como el DNI por teléfono sin verificar la identidad de la empresa.» |
| ENT-L-SOPORTE-003 | L1 | 0.3 |  | «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.» | «Te están contactando sobre un objeto que dejaste, lo cual es una táctica común para intentar obtener información o pedir dinero.» |
| ENT-L-SOPORTE-005 | L11 | 0.3 | sí | «Abajo hay un botón que dice Asistencia remota. Descargá ese programa, solo desde ahí.» | «No se debe descargar software de fuentes no oficiales ni seguir instrucciones para instalar programas remotos, ya que esto es una táctica común de estafa.» |
| ENT-L-VENTAS-001 | L13 | 0.3 |  | «para cargarlo necesito validar que hablo con la titular me pasás tu dni» | «Te están pidiendo tu DNI para realizar un cambio o promoción, lo cual es una práctica común en intentos de fraude.» |
| ENT-L-VENTAS-002 | L16 | 0.3 |  | «si querés te dejo la solicitud cargada para eso necesito tu nombre completo y tu dni» | «Te están pidiendo tu DNI por teléfono para completar una solicitud de servicio, lo cual es una práctica sospechosa.» |
| ENT-L-VENTAS-009 | L21 | 0.3 |  | «Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.» | «Te están pidiendo que realices una transferencia o pago para asegurar una tasación, lo cual es una táctica común en estafas.» |
| LEG-BA-01 | L5 | 0.3 |  | «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?» | «Aunque la llamada menciona un intento de compra, es una táctica común para generar urgencia y obtener información. No se debe proporcionar información sensible ni hacer clic en enlaces.» |
| LEG-BA-02 | L3 | 0.5 |  | «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.» | «Desconfía de la urgencia y la solicitud de confirmar inicios de sesión, ya que los bancos legítimos suelen tener protocolos diferentes.» |
| LEG-BA-03 | L3 | 0.3 |  | «Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarjeta de débito, por ochenta y nueve dólares, en una aerolínea. Solo necesito que me digas si la reconocés o no.» | «Los bancos legítimos rara vez solicitan confirmar transacciones de esta manera por teléfono; es una táctica común de phishing.» |
| LEG-ST-03 | L1 | 0.3 |  | «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.» | «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para intentar obtener información o pedir dinero.» |
| LEG2-BA-01 | L4 | 0.7 |  | «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?» | «Los bancos legítimos rara vez solicitan datos sensibles como DNI y fecha de nacimiento por teléfono sin una previa verificación o contexto claro.» |
| LEG2-BA-02 | L4 | 0.3 |  | «Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, ¿me confirmás tu DNI?» | «Los bancos legítimos rara vez solicitan el DNI de forma tan directa al inicio de una llamada sin un contexto previo claro.» |
| LEG2-BA-03 | L2 | 0.3 |  | «Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?» | «Tené cuidado, porque te están pidiendo datos personales por teléfono, lo cual es una táctica común de estafas.» |
| LEG2-BA-05 | L6 | 0.3 |  | «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?» | «Los bancos legítimos rara vez solicitan datos sensibles como el DNI para validar una transacción de esta manera.» |
| LEG2-CC-05 | L6 | 0.3 |  | «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?» | «Desconfía de que le pidan datos personales como el DNI por teléfono sin un contexto claro.» |
| LEG2-CC-06 | L6 | 0.3 |  | «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.» | «Las ofertas repentinas y urgentes, especialmente cuando se pide hacer una llamada a un número específico, son una táctica común de estafa.» |
| LEG2-ST-03 | L2 | 0.3 |  | «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.» | «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para intentar obtener información o pedir dinero.» |
| LEG2-ST-05 | L2 | 0.3 |  | «Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porque no podías entrar a tu cuenta. ¿Hablo con Andrés Romero?» | «Desconfía porque no tiene agendado un ticket y no puede verificar la identidad de quien llama.» |

