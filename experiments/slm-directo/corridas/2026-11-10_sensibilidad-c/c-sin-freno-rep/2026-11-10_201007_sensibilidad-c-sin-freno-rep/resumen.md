# Resumen de la corrida `2026-11-10_201007_sensibilidad-c-sin-freno-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-sin-freno-corte-riesgo --solo-otra --seguir-tras-aviso --lista alcance-140 --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta sensibilidad-c-sin-freno-rep --salida /content/resultados-sensibilidad/c-sin-freno-rep`
- **Inicio / fin:** 2026-11-10T20:10:07 / 2026-11-10T20:15:54
- **Código:** `ca4fab05d7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 140 (46 vishing, 94 legítimas); 140 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-sin-freno-corte-riesgo\|rol` | 41/46 | 20 | 8 | 3 | 0 | 38/94 | 0/2621 | 210 | 844 | 79/79 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-sin-freno-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L2 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L1 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L6 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L2 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L2 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L7 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | >R L24 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | =R L20 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L10 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L6 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | <R L8 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L11 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L8 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L1 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L2 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | =R L15 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | >R L13 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L1 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L2 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L3 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L1 |
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
| `ENT-L-ENCUESTA-004` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | FA L12 |
| `ENT-L-MEDICO-001` | legítima | — | — | ok |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | FA L1 |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | FA L13 |
| `ENT-L-SELECCION-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-002` | legítima | — | — | FA L6 |
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-006` | legítima | — | — | FA L8 |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L9 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L10 |
| `ENT-L-VENTAS-003` | legítima | — | — | FA L5 |
| `ENT-L-VENTAS-004` | legítima | — | — | FA L4 |
| `ENT-L-VENTAS-005` | legítima | — | — | FA L5 |
| `ENT-L-VENTAS-006` | legítima | — | — | FA L16 |
| `ENT-L-VENTAS-007` | legítima | — | — | FA L11 |
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
| `LEG2-BA-01` | legítima | — | — | FA L4 |
| `LEG2-BA-02` | legítima | — | — | FA L4 |
| `LEG2-BA-03` | legítima | — | — | FA L2 |
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
| `LEG2-ST-03` | legítima | — | — | FA L2 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | FA L2 |
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

- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Los bancos legítimos rara vez inician llamadas sin un contexto previo o sin pedir información sensible de inmediato.» — evidencia (cita textual): «buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Aunque se presenta como el banco, es necesario verificar la identidad antes de compartir cualquier información.» — evidencia (cita textual): «Hola, buen día. Te llamo del banco, del sector de seguridad.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Aunque suena legítimo, tené cuidado, ya que las estafas suelen empezar haciéndose pasar por entidades bancarias.» — evidencia (cita textual): «Buenas tardes, le habla Lorena, de prevención de fraudes del banco.»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Desconfía de que te pidan datos personales sensibles como el DNI por teléfono, especialmente si no esperabas una llamada del banco.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Las llamadas de prevención de fraudes suelen ser el inicio de estafas donde intentan obtener información sensible.» — evidencia (cita textual): «Buen día, le hablo de prevención de fraudes del banco.»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Desconfía de que te contacten por un número no agendado y que te pidan acceder a tu app para algo urgente.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-ENCUESTA-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 9: «Te están llamando con un número aleatorio y te están presionando para que aceptes participar en una encuesta, lo cual es una táctica común de phishing.» — evidencia (cita textual): «Los números se generan al azar dentro de la provincia. No tengo tu nombre en una lista, solo el que me dijiste vos.»
- `ENT-L-ENCUESTA-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 12: «Aunque la llamada se centra en una encuesta, la mención de problemas con la tarjeta y la entrega de información sensible es una táctica común para generar confianza y luego intentar obtener datos.» — evidencia (cita textual): «lamento lo de la tarjeta te dieron toda la información del reintegro»
- `ENT-L-MEDICO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «No se puede verificar la legitimidad de la llamada, por lo que es prudente tener precaución.» — evidencia (cita textual): «Buenas tardes, te llamo del laboratorio Bioanálisis.»
- `ENT-L-SELECCION-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 13: «Te están pidiendo que les des un código de acceso, lo cual es una táctica común para obtener información o intentar engañarte.» — evidencia (cita textual): «no no ese código no me lo pases ni a mí ni a nadie es tu clave para entrar a la evaluación la usás vos cuando la vayas a hacer»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Desconfíe de llamadas no solicitadas de soporte técnico y reclamos, ya que pueden intentar obtener información personal o instalar software malicioso.» — evidencia (cita textual): «hola buen día te habla leonel de soporte técnico de fibrasur te llamo por el reclamo 3349 de falta de serbicio»
- `ENT-L-SOPORTE-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Desconfía de que una empresa legítima pida datos sensibles como el DNI por teléfono sin una verificación previa.» — evidencia (cita textual): «me imagino para validar la garantía necesito el dni del titular de la factura»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas de suplantación o cobro.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Aunque suena a soporte, es una táctica común para iniciar una estafa pidiendo información o acceso a cuentas.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo de soporte de Factura Simple, por el ticket que abriste esta mañana.»
- `ENT-L-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 8: «Te están pidiendo datos personales sensibles como el número de documento para un envío, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Para el envío, ¿me confirmás tu número de documento?»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 9: «Las ofertas de planes de telefonía con cambios de cuotas y precios inesperados son comunes en intentos de venta o estafas.» — evidencia (cita textual): «tenés el plan de cinco gigas y te podemos pasar a quince por la misma cuota durante seis meses»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 10: «Es una táctica común de ventas no solicitadas que busca obtener datos personales bajo el pretexto de una oferta de servicio.» — evidencia (cita textual): «llamamos a los numeros fijos y celulares de la zona de cobertura si no querés que te llamemos te saco de lista»
- `ENT-L-VENTAS-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 5: «Las llamadas que inician con información genérica sobre seguros o beneficios suelen ser el primer paso para intentar obtener datos personales o instalar algo.» — evidencia (cita textual): «te llamo porque como clienta tenés un seguro de hogar con el primer mes bonificado cubre incendio robo y daños por agua te cuento dos minutos»
- `ENT-L-VENTAS-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Tené cuidado, porque te están ofreciendo un servicio sin que hayas solicitado nada.» — evidencia (cita textual): «Te quería ofrecer internet para tu casa, con...»
- `ENT-L-VENTAS-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 5: «Desconfía de que le pidan datos personales como el DNI por teléfono, especialmente si la comunicación no es totalmente verificable.» — evidencia (cita textual): «Por eso te llamo, te quedó a mitad de camino. Faltaba validar la identidad. ¿Me confirmás tu DNI?»
- `ENT-L-VENTAS-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 16: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para intentar obtener datos o redirigirte a otro servicio.» — evidencia (cita textual): «Llamá al 0800 que está en tu factura, decí ese número y te activan la promo ellos.»
- `ENT-L-VENTAS-007` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 11: «Te están pidiendo datos personales sensibles como DNI y su sueldo, lo cual es una táctica común en intentos de fraude.» — evidencia (cita textual): «tu nombre completo el dni y más o menos cuánto ganás por mes en blanco»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 19: «Te están pidiendo realizar un pago (seña) a una cuenta bancaria para asegurar una operación, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 5: «Aunque la llamada menciona un intento de compra, es una táctica común para generar urgencia y obtener información. No se debe confirmar ninguna información ni hacer clic en enlaces.» — evidencia (cita textual): «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 3: «Los bancos rara vez solicitan confirmación de inicios de sesión por teléfono de esta manera; es una táctica común para robar credenciales.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmar transacciones de esta manera por teléfono; es una táctica común para obtener datos de la tarjeta.» — evidencia (cita textual): «Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarjeta de débito, por ochenta y nueve dólares, en una aerolínea. Solo necesito que me digas si la reconocés o no.»
- `LEG-CC-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 7: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener acceso a información o realizar transacciones no deseadas.» — evidencia (cita textual): «Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo de deportes para clientes y te la activan ahí. Yo no te voy a pedir ningún dato ni pago por acá.»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas de suplantación o cobro.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Los bancos legítimos rara vez solicitan datos personales sensibles como DNI y fecha de nacimiento por teléfono sin una previa verificación o contexto claro.» — evidencia (cita textual): «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Los bancos rara vez solicitan el DNI por teléfono de esta manera para confirmar transacciones; es una táctica común para obtener datos personales.» — evidencia (cita textual): «Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, ¿me confirmás tu DNI?»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Aunque el nombre de la entidad suena legítimo, es importante verificar la identidad de quien llama antes de proporcionar datos personales.» — evidencia (cita textual): «Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Los bancos legítimos rara vez llaman para preguntar sobre transacciones recientes de esta manera para validar datos personales.» — evidencia (cita textual): «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?»
- `LEG2-CC-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 8: «Los ofrecimientos de planes con cambios de cuota y la solicitud de datos personales deben ser verificados con cautela.» — evidencia (cita textual): «Para validar que hablo con la titular, ¿me confirmás tu número de DNI?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Desconfía de que le pidan datos personales como el DNI por teléfono, especialmente si no tiene agendada ninguna gestión reciente.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Las ofertas repentinas y urgentes, especialmente cuando no se tiene un contexto previo, son una táctica común para intentar conseguir información o datos.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Te están contactando sobre un objeto que dejaste, lo cual es una táctica común para intentar obtener información o pedir dinero.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-ST-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Desconfía porque no tiene agendado un ticket y no puede verificar la identidad de quien llama.» — evidencia (cita textual): «Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porque no podías entrar a tu cuenta. ¿Hablo con Andrés Romero?»
- `LEG2-VE-04` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Te están pidiendo datos personales bajo el pretexto de un trámite, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Para hacer el patentamiento necesito confirmar unos datos.»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 578 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-sin-freno-corte-riesgo\|rol` | 219.405 | 345.451 | 0 | 219.405 | 534226 | 1431 | 742/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (689 en esta corrida) no consultan y no cuentan como ausencia.
