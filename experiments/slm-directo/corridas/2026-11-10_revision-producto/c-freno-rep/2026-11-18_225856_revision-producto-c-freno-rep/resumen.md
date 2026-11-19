# Resumen de la corrida `2026-11-18_225856_revision-producto-c-freno-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-freno-corte-riesgo --solo-otra --seguir-tras-aviso --lista alcance-140 --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta revision-producto-c-freno-rep --salida /content/resultados-revision-producto/c-freno-rep`
- **Inicio / fin:** 2026-11-18T22:58:56 / 2026-11-18T23:04:58
- **Código:** `30746d3f38`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 140 (46 vishing, 94 legítimas); 140 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-freno-corte-riesgo\|rol` | 42/46 | 24 | 6 | 2 | 0 | 35/94 | 0/2621 | 223 | 852 | 77/77 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-freno-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L4 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L3 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L4 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L2 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | <R L1 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L3 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | <R L14 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | =R L20 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | <R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | <R L8 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L11 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L8 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L1 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | >R L16 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L6 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | — |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L5 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L2 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L3 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L5 |
| `ENT-L-BANCO-004` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L2 |
| `ENT-L-DELIVERY-001` | legítima | — | — | ok |
| `ENT-L-DELIVERY-002` | legítima | — | — | ok |
| `ENT-L-DELIVERY-003` | legítima | — | — | ok |
| `ENT-L-DELIVERY-004` | legítima | — | — | ok |
| `ENT-L-DELIVERY-005` | legítima | — | — | ok |
| `ENT-L-DELIVERY-006` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-001` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-002` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-003` | legítima | — | — | FA L9 |
| `ENT-L-ENCUESTA-004` | legítima | — | — | FA L6 |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | ok |
| `ENT-L-MEDICO-001` | legítima | — | — | ok |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | ok |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | FA L13 |
| `ENT-L-SELECCION-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L3 |
| `ENT-L-SOPORTE-002` | legítima | — | — | FA L6 |
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L5 |
| `ENT-L-SOPORTE-006` | legítima | — | — | FA L8 |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L13 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-003` | legítima | — | — | FA L19 |
| `ENT-L-VENTAS-004` | legítima | — | — | FA L4 |
| `ENT-L-VENTAS-005` | legítima | — | — | FA L5 |
| `ENT-L-VENTAS-006` | legítima | — | — | ok |
| `ENT-L-VENTAS-007` | legítima | — | — | FA L11 |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | ok |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L5 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | FA L3 |
| `LEG-CC-01` | legítima | — | — | ok |
| `LEG-CC-02` | legítima | — | — | ok |
| `LEG-CC-03` | legítima | — | — | FA L7 |
| `LEG-CO-01` | legítima | — | — | ok |
| `LEG-CO-02` | legítima | — | — | ok |
| `LEG-CO-03` | legítima | — | — | ok |
| `LEG-EN-01` | legítima | — | — | ok |
| `LEG-EN-02` | legítima | — | — | ok |
| `LEG-EN-03` | legítima | — | — | ok |
| `LEG-ST-01` | legítima | — | — | ok |
| `LEG-ST-02` | legítima | — | — | ok |
| `LEG-ST-03` | legítima | — | — | FA L1 |
| `LEG-TU-01` | legítima | — | — | ok |
| `LEG-TU-02` | legítima | — | — | ok |
| `LEG-TU-03` | legítima | — | — | ok |
| `LEG-VE-01` | legítima | — | — | ok |
| `LEG-VE-02` | legítima | — | — | ok |
| `LEG-VE-03` | legítima | — | — | ok |
| `LEG2-BA-01` | legítima | — | — | FA L4 |
| `LEG2-BA-02` | legítima | — | — | FA L4 |
| `LEG2-BA-03` | legítima | — | — | FA L2 |
| `LEG2-BA-05` | legítima | — | — | FA L6 |
| `LEG2-CC-01` | legítima | — | — | ok |
| `LEG2-CC-04` | legítima | — | — | ok |
| `LEG2-CC-05` | legítima | — | — | FA L6 |
| `LEG2-CC-06` | legítima | — | — | FA L6 |
| `LEG2-CO-01` | legítima | — | — | ok |
| `LEG2-CO-02` | legítima | — | — | ok |
| `LEG2-CO-03` | legítima | — | — | ok |
| `LEG2-CO-06` | legítima | — | — | ok |
| `LEG2-EN-01` | legítima | — | — | ok |
| `LEG2-EN-03` | legítima | — | — | ok |
| `LEG2-EN-04` | legítima | — | — | FA L4 |
| `LEG2-EN-05` | legítima | — | — | ok |
| `LEG2-ST-02` | legítima | — | — | FA L6 |
| `LEG2-ST-03` | legítima | — | — | FA L4 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | ok |
| `LEG2-TU-01` | legítima | — | — | ok |
| `LEG2-TU-02` | legítima | — | — | ok |
| `LEG2-TU-05` | legítima | — | — | ok |
| `LEG2-TU-06` | legítima | — | — | ok |
| `LEG2-VE-01` | legítima | — | — | ok |
| `LEG2-VE-04` | legítima | — | — | FA L6 |
| `LEG2-VE-05` | legítima | — | — | ok |
| `LEG2-VE-06` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 1: «Aunque se presenta como del banco, es importante verificar la identidad y no compartir información sensible.» — evidencia (cita textual): «buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 2: «Los bancos legítimos rara vez inician llamadas sin una previa identificación o contexto claro.» — evidencia (cita textual): «Hola, buen día. Te llamo del banco, del sector de seguridad.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 5: «Los bancos legítimos rara vez solicitan los últimos tres números de documento por teléfono sin un contexto previo claro.» — evidencia (cita textual): «Gracias, señor Sosa. ¿Me confirma los últimos tres números de su documento?»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 4: «No es normal que un banco pida directamente el DNI por teléfono para validar la identidad de un cliente.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 1: «Las llamadas de prevención de fraudes suelen ser el inicio de estafas donde intentan obtener información sensible.» — evidencia (cita textual): «Buen día, le hablo de prevención de fraudes del banco.»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 2: «Los bancos generalmente no llaman de forma inesperada para pedir información por teléfono.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-ENCUESTA-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 9: «Te están pidiendo información personal bajo el pretexto de una encuesta, lo cual es una táctica común para obtener datos.» — evidencia (cita textual): «Los números se generan al azar dentro de la provincia. No tengo tu nombre en una lista, solo el que me dijiste vos.»
- `ENT-L-ENCUESTA-004` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Las entidades legítimas rara vez solicitan el DNI por teléfono de esta manera para una encuesta.» — evidencia (cita textual): «Para validar que sos afiliada, ¿me confirmás tu número de documento?»
- `ENT-L-SELECCION-002` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 13: «Te están pidiendo que les des un código de acceso que es tu clave para entrar a una evaluación, lo cual es una táctica común de estafa.» — evidencia (cita textual): «no no ese código no me lo pases ni a mí ni a nadie es tu clave para entrar a la evaluación la usás vos cuando la vayas a hacer»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 3: «No es normal que un soporte técnico te pida tu DNI por teléfono para validar tu identidad.» — evidencia (cita textual): «para validar que hablo con la titular me confirmás tu dni»
- `ENT-L-SOPORTE-002` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Te están pidiendo tu DNI para validar una garantía, lo cual puede ser un intento de robo de datos.» — evidencia (cita textual): «me imagino para validar la garantía necesito el dni del titular de la factura»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es una táctica común para intentar obtener información o instalar algo.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 5: «Te están pidiendo información personal o de acceso (mail) bajo el pretexto de un problema de facturación, lo cual es una táctica común de estafa.» — evidencia (cita textual): «En el ticket pusiste que no te deja emitir facturas desde ayer.»
- `ENT-L-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 8: «Te están pidiendo tu número de documento para un envío, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Para el envío, ¿me confirmás tu número de documento?»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 13: «Te están pidiendo tu DNI para realizar un cambio o una promoción, lo cual es una táctica común de estafa.» — evidencia (cita textual): «para cargarlo necesito validar que hablo con la titular me pasás tu dni»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 14: «Te están pidiendo datos personales sensibles como nombre completo y DNI bajo el pretexto de una oferta de servicio.» — evidencia (cita textual): «si querés te dejo la solicitud cargada para eso necesito tu nombre completo y tu dni»
- `ENT-L-VENTAS-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 19: «Aunque la conversación es sobre un seguro, la mención de depósitos en cuentas bancarias puede ser un intento de obtener información sensible o de simular una transacción.» — evidencia (cita textual): «el reintegro se deposita en tu cuenta banco figura la caja de ahorro terminada en dos doscientos treinta y uno es esa la que usás»
- `ENT-L-VENTAS-004` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 4: «Tené cuidado, porque te están ofreciendo un servicio sin que hayas solicitado nada.» — evidencia (cita textual): «Te quería ofrecer internet para tu casa, con...»
- `ENT-L-VENTAS-005` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 5: «Te están pidiendo tu DNI para validar tu identidad, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Por eso te llamo, te quedó a mitad de camino. Faltaba validar la identidad. ¿Me confirmás tu DNI?»
- `ENT-L-VENTAS-007` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 11: «Te están pidiendo datos personales sensibles como DNI y su sueldo, lo cual es una táctica común de estafa.» — evidencia (cita textual): «tu nombre completo el dni y más o menos cuánto ganás por mes en blanco»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 5: «Aunque la llamada menciona un intento de compra, es una táctica común para intentar obtener información o hacer que la víctima revele datos sensibles.» — evidencia (cita textual): «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmación de inicios de sesión por teléfono de esta manera; es una táctica común para robar credenciales.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 3: «Los bancos legítimos no suelen pedir confirmar transacciones por teléfono de esta manera.» — evidencia (cita textual): «Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarjeta de débito, por ochenta y nueve dólares, en una aerolínea. Solo necesito que me digas si la reconocés o no.»
- `LEG-CC-03` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 7: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener acceso a tus datos o realizar una transacción no deseada.» — evidencia (cita textual): «Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo de deportes para clientes y te la activan ahí. Yo no te voy a pedir ningún dato ni pago por acá.»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual puede ser un intento de estafa.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 4: «El banco no suele solicitar datos personales sensibles como DNI y fecha de nacimiento por teléfono sin un contexto previo claro.» — evidencia (cita textual): «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 4: «El banco no suele solicitar el DNI de forma tan directa al inicio de una llamada sin un contexto previo claro.» — evidencia (cita textual): «Antes de seguir, ¿me confirmás tu DNI?»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 2: «Aunque menciona un banco, es importante verificar la legitimidad de la llamada antes de compartir datos personales.» — evidencia (cita textual): «Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Te están pidiendo información sensible sobre tu tarjeta y ubicación, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Te están pidiendo tu DNI para validar tu identidad, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Te están ofreciendo un descuento inesperado y te piden que llames a un número específico para activarlo, lo cual es una táctica común de phishing.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-EN-04` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 4: «Los organismos legítimos no suelen pedir el DNI por teléfono para validar la afiliación de forma tan directa.» — evidencia (cita textual): «Valeria, estamos haciendo una encuesta corta a los afiliados que se atendieron este mes. Para validar que sos afiliada, ¿me confirmás tu DNI?»
- `LEG2-ST-02` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Te están pidiendo tu DNI para validar una garantía, lo cual puede ser un intento de robo de datos.» — evidencia (cita textual): «Para validar la garantía necesito el DNI del titular de la factura.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 4: «Te están pidiendo tu DNI para registrar un objeto que dejaste, lo cual es una táctica común para obtener tus datos personales.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el DNI que dejaste?»
- `LEG2-VE-04` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · línea 6: «Te están pidiendo tu DNI para un trámite que no esperabas, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Para hacer el patentamiento necesito confirmar unos datos.»

### Vishing sin aviso

- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-003` · `slm|gemma4:e2b-it-q4_K_M|c-freno-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 607 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-freno-corte-riesgo\|rol` | 231.381 | 361.002 | 0 | 231.381 | 710484 | 1459 | 756/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (703 en esta corrida) no consultan y no cuentan como ausencia.
