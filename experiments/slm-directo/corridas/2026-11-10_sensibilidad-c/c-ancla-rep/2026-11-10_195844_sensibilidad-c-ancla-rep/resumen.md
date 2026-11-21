# Resumen de la corrida `2026-11-10_195844_sensibilidad-c-ancla-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-ancla-corte-riesgo --solo-otra --seguir-tras-aviso --lista alcance-140 --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta sensibilidad-c-ancla-rep --salida /content/resultados-sensibilidad/c-ancla-rep`
- **Inicio / fin:** 2026-11-10T19:58:44 / 2026-11-10T20:04:23
- **Código:** `ca4fab05d7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 140 (46 vishing, 94 legítimas); 140 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-ancla-corte-riesgo\|rol` | 40/46 | 18 | 11 | 2 | 0 | 27/94 | 0/2621 | 210 | 679 | 67/67 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-ancla-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L4 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L3 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L3 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L2 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L5 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L7 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | >R L24 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L10 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | <R L8 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L8 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | =R L15 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L5 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | =R L25 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L2 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L3 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L11 |
| `ENT-L-BANCO-004` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L2 |
| `ENT-L-DELIVERY-001` | legítima | — | — | FA L15 |
| `ENT-L-DELIVERY-002` | legítima | — | — | ok |
| `ENT-L-DELIVERY-003` | legítima | — | — | ok |
| `ENT-L-DELIVERY-004` | legítima | — | — | ok |
| `ENT-L-DELIVERY-005` | legítima | — | — | ok |
| `ENT-L-DELIVERY-006` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-001` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-002` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-003` | legítima | — | — | FA L11 |
| `ENT-L-ENCUESTA-004` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | ok |
| `ENT-L-MEDICO-001` | legítima | — | — | ok |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | ok |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | ok |
| `ENT-L-SELECCION-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L3 |
| `ENT-L-SOPORTE-002` | legítima | — | — | ok |
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L11 |
| `ENT-L-SOPORTE-006` | legítima | — | — | ok |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L13 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | ok |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L19 |
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
| `LEG2-BA-01` | legítima | — | — | FA L10 |
| `LEG2-BA-02` | legítima | — | — | FA L6 |
| `LEG2-BA-03` | legítima | — | — | ok |
| `LEG2-BA-05` | legítima | — | — | FA L6 |
| `LEG2-CC-01` | legítima | — | — | FA L8 |
| `LEG2-CC-04` | legítima | — | — | ok |
| `LEG2-CC-05` | legítima | — | — | FA L6 |
| `LEG2-CC-06` | legítima | — | — | FA L6 |
| `LEG2-CO-01` | legítima | — | — | ok |
| `LEG2-CO-02` | legítima | — | — | ok |
| `LEG2-CO-03` | legítima | — | — | ok |
| `LEG2-CO-06` | legítima | — | — | ok |
| `LEG2-EN-01` | legítima | — | — | ok |
| `LEG2-EN-03` | legítima | — | — | ok |
| `LEG2-EN-04` | legítima | — | — | ok |
| `LEG2-EN-05` | legítima | — | — | ok |
| `LEG2-ST-02` | legítima | — | — | ok |
| `LEG2-ST-03` | legítima | — | — | FA L4 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | FA L2 |
| `LEG2-TU-01` | legítima | — | — | ok |
| `LEG2-TU-02` | legítima | — | — | ok |
| `LEG2-TU-05` | legítima | — | — | ok |
| `LEG2-TU-06` | legítima | — | — | ok |
| `LEG2-VE-01` | legítima | — | — | ok |
| `LEG2-VE-04` | legítima | — | — | ok |
| `LEG2-VE-05` | legítima | — | — | ok |
| `LEG2-VE-06` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan datos sensibles como DNI y fecha de nacimiento de esta manera al inicio de una llamada no agendada.» — evidencia (cita textual): «antes de darte información necesito validar que hablo con el titular me me decís tu dni y tu fecha de nacimiento»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 2: «Aunque se presenta como el banco, no se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «Hola, buen día. Te llamo del banco, del sector de seguridad.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 11: «El llamante está presionando para que confirme información y liberar una transacción, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Si usted me confirma que la reconoce, la libero ahora.»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 4: «Desconfíe de que le pidan datos personales sensibles como el DNI por teléfono sin una previa verificación.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 1: «Las llamadas de prevención de fraudes suelen ser un inicio común para intentar robar datos personales o financieros.» — evidencia (cita textual): «Buen día, le hablo de prevención de fraudes del banco.»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 2: «Desconfía de que te contacten por un número no agendado y que te pidan acceder a tu app para algo urgente.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-DELIVERY-001` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 15: «No debes firmar documentos ni compartir datos personales por teléfono.» — evidencia (cita textual): «Sí, me firmás en el celular y me decís el documento de quien recibe.»
- `ENT-L-ENCUESTA-003` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 11: «Te están intentando convencerte de que eres parte de un panel de encuestas para luego intentar obtener información o instalar algo.» — evidencia (cita textual): «Si querés, te saco del panel y no te llamamos más.»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 3: «No es seguro confirmar datos personales por teléfono; desconfía de que te pidan tu DNI para validar un reclamo.» — evidencia (cita textual): «para validar que hablo con la titular me confirmás tu dni»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 1: «Desconocemos el contexto de esta llamada y no podemos verificar la legitimidad de la solicitud.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 11: «No se debe descargar software de fuentes no oficiales ni seguir instrucciones para instalar programas remotamente, ya que esto es una táctica común de estafa.» — evidencia (cita textual): «Abajo hay un botón que dice Asistencia remota. Descargá ese programa, solo desde ahí.»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 13: «No es normal que te pidan tu DNI por teléfono para validar una promoción de celular.» — evidencia (cita textual): «para cargarlo necesito validar que hablo con la titular me pasás tu dni»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 14: «Te están pidiendo datos personales sensibles (nombre completo y DNI) bajo el pretexto de ofrecer un servicio de internet.» — evidencia (cita textual): «si querés te dejo la solicitud cargada para eso necesito tu nombre completo y tu dni»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 19: «Te están pidiendo que realices una transferencia o pago para asegurar un trato, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 5: «Aunque la llamada menciona un intento de compra, es común que estafadores usen este tipo de pretextos para obtener información o hacer que la víctima revele datos.» — evidencia (cita textual): «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 3: «Desconfía de la urgencia y la solicitud de confirmar inicios de sesión, ya que los bancos legítimos rara vez solicitan confirmación de esta manera por teléfono.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmar transacciones de esta manera por teléfono; es una táctica común para obtener información sensible.» — evidencia (cita textual): «Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarjeta de débito, por ochenta y nueve dólares, en una aerolínea. Solo necesito que me digas si la reconocés o no.»
- `LEG-CC-03` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 7: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener acceso a información o realizar transacciones no deseadas.» — evidencia (cita textual): «Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo de deportes para clientes y te la activan ahí. Yo no te voy a pedir ningún dato ni pago por acá.»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 10: «Los bancos legítimos nunca te pedirán que compartas un código de reactivación por teléfono.» — evidencia (cita textual): «Te va a llegar un SMS con un código para reactivarla. Ese código lo ponés vos en la app y no se lo das a nadie, ni a mí ni a nadie que te llame del banco.»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 6: «Te están pidiendo que cortes la llamada y llames a un número, lo cual es una táctica común para robar tus datos.» — evidencia (cita textual): «Hagamos así: cortá y llamá vos al número del dorso de tu tarjeta. Pedí por seguridad y dales el número de caso siete tres cuatro cuatro cero.»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 6: «Los bancos legítimos rara vez solicitan datos sensibles como el DNI para validar una transacción de esta manera.» — evidencia (cita textual): «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?»
- `LEG2-CC-01` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 8: «Te están pidiendo tu DNI para validar la identidad, lo cual es una práctica común en intentos de fraude.» — evidencia (cita textual): «Para validar que hablo con la titular, ¿me confirmás tu número de DNI?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 6: «Desconfía de que le pidan datos personales como el DNI por teléfono sin un contexto claro.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 6: «Desconfía de la urgencia y de la forma en que se solicita la acción (llamar a un número específico) para activar una promoción.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 4: «Desconfía de que un local desconocido te contacte para pedirte datos personales bajo el pretexto de una reparación.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el DNI que dejaste?»
- `LEG2-ST-05` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · línea 2: «Desconfía porque no tiene agendado un ticket y no puede verificar la identidad de quien llama.» — evidencia (cita textual): «Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porque no podías entrar a tu cuenta. ¿Hablo con Andrés Romero?»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-ancla-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 405 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-ancla-corte-riesgo\|rol` | 240.834 | 338.215 | 0 | 240.834 | 721694 | 1697 | 874/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (823 en esta corrida) no consultan y no cuentan como ausencia.
