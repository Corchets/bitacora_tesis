# Resumen de la corrida `2026-11-18_225308_revision-producto-c-consejos-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-consejos-corte-riesgo --solo-otra --seguir-tras-aviso --lista alcance-140 --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta revision-producto-c-consejos-rep --salida /content/resultados-revision-producto/c-consejos-rep`
- **Inicio / fin:** 2026-11-18T22:53:08 / 2026-11-18T22:58:55
- **Código:** `30746d3f38`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 140 (46 vishing, 94 legítimas); 140 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-consejos-corte-riesgo\|rol` | 42/46 | 18 | 10 | 4 | 0 | 18/94 | 0/2621 | 222 | 288 | 60/60 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-consejos-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L6 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L15 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L5 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L4 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L5 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | <R L1 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L7 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | >R L24 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | =R L20 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L11 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L16 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L17 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | >R L16 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L14 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | — |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L4 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L9 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L4 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L9 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-003` | legítima | — | — | ok |
| `ENT-L-BANCO-004` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L2 |
| `ENT-L-DELIVERY-001` | legítima | — | — | ok |
| `ENT-L-DELIVERY-002` | legítima | — | — | ok |
| `ENT-L-DELIVERY-003` | legítima | — | — | ok |
| `ENT-L-DELIVERY-004` | legítima | — | — | ok |
| `ENT-L-DELIVERY-005` | legítima | — | — | ok |
| `ENT-L-DELIVERY-006` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-001` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-002` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-003` | legítima | — | — | ok |
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
| `ENT-L-VENTAS-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L19 |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L7 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | ok |
| `LEG-CC-01` | legítima | — | — | ok |
| `LEG-CC-02` | legítima | — | — | ok |
| `LEG-CC-03` | legítima | — | — | ok |
| `LEG-CO-01` | legítima | — | — | ok |
| `LEG-CO-02` | legítima | — | — | ok |
| `LEG-CO-03` | legítima | — | — | ok |
| `LEG-EN-01` | legítima | — | — | ok |
| `LEG-EN-02` | legítima | — | — | ok |
| `LEG-EN-03` | legítima | — | — | ok |
| `LEG-ST-01` | legítima | — | — | ok |
| `LEG-ST-02` | legítima | — | — | ok |
| `LEG-ST-03` | legítima | — | — | ok |
| `LEG-TU-01` | legítima | — | — | ok |
| `LEG-TU-02` | legítima | — | — | ok |
| `LEG-TU-03` | legítima | — | — | ok |
| `LEG-VE-01` | legítima | — | — | ok |
| `LEG-VE-02` | legítima | — | — | ok |
| `LEG-VE-03` | legítima | — | — | ok |
| `LEG2-BA-01` | legítima | — | — | ok |
| `LEG2-BA-02` | legítima | — | — | FA L4 |
| `LEG2-BA-03` | legítima | — | — | ok |
| `LEG2-BA-05` | legítima | — | — | FA L8 |
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
| `LEG2-EN-04` | legítima | — | — | ok |
| `LEG2-EN-05` | legítima | — | — | ok |
| `LEG2-ST-02` | legítima | — | — | ok |
| `LEG2-ST-03` | legítima | — | — | FA L4 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | ok |
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

- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los bancos y organismos legítimos no suelen solicitar el DNI y la fecha de nacimiento por teléfono para validar la identidad.» — evidencia (cita textual): «antes de darte información necesito validar que hablo con el titular me me decís tu dni y tu fecha de nacimiento»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Los bancos legítimos no suelen contactar por teléfono para notificar ingresos no registrados de esa manera.» — evidencia (cita textual): «Registramos dos ingresos a tu home banking desde un celular que no tenías registrado, esta madrugada.»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Los bancos o organismos legítimos rara vez solicitan el DNI por teléfono de esta manera sin un contexto previo claro.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los bancos y organismos legítimos no suelen solicitar documentos personales completos por teléfono para validar información.» — evidencia (cita textual): «¿Me confirma su documento para validar?»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Tené cuidado, porque las estafas suelen empezar diciendo que te van a contactar por tu app para generar urgencia.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los organismos legítimos rara vez solicitan el DNI por teléfono de esta manera para validar la titularidad.» — evidencia (cita textual): «para validar que hablo con la titular me confirmás tu dni»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 1: «Si no esperabas una llamada sobre un objeto que dejaste, es mejor verificar la identidad de TecnoFix por otros medios antes de dar cualquier información.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 11: «No se debe descargar software por instrucciones de un proveedor de servicios o entidad oficial por teléfono.» — evidencia (cita textual): «Abajo hay un botón que dice Asistencia remota. Descargá ese programa, solo desde ahí.»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 13: «No se debe proporcionar el DNI por teléfono a una compañía de celular bajo estas circunstancias.» — evidencia (cita textual): «para cargarlo necesito validar que hablo con la titular me pasás tu dni»
- `ENT-L-VENTAS-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 14: «Aunque la llamada no pide datos sensibles, las ofertas urgentes y la instrucción de llamar a un número específico para activar una promoción son comunes en llamadas de marketing o intentos de fraude.» — evidencia (cita textual): «Llamá al 0800 que está en tu factura, decí ese número y te activan la promo ellos. Yo no te pido nada por acá.»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 19: «No se debe realizar ninguna transferencia o pago a cuentas desconocidas por teléfono.» — evidencia (cita textual): «Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 7: «Aunque la llamada menciona no pedir claves ni códigos, el intento de generar urgencia para bloquear la tarjeta y reemplazarla es una táctica común de estafa.» — evidencia (cita textual): «Lo que te propongo es bloquear la tarjeta ahora y te enviamos una nueva a tu domicilio en siete a diez días hábiles. ¿Estás de acuerdo?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmación de inicios de sesión por teléfono de esta manera; es una táctica común de phishing.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Los bancos legítimos rara vez solicitan el DNI por teléfono de esta manera sin un contexto previo claro.» — evidencia (cita textual): «Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, ¿me confirmás tu DNI?»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 8: «Los bancos legítimos no suelen solicitar datos sensibles o hacer afirmaciones alarmantes de esta manera para pedir información personal.» — evidencia (cita textual): «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 6: «Desconfía de que le pidan datos personales como el DNI por teléfono sin un contexto claro.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 6: «Te están presionando con una oferta de compra y te piden que llames a un número específico para activar algo, lo cual es una táctica común.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Desconfía de que te pidan datos personales como el DNI para un servicio que no esperabas.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el DNI que dejaste?»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 647 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-consejos-corte-riesgo\|rol` | 254.071 | 346.745 | 0 | 254.071 | 839037 | 1782 | 915/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (867 en esta corrida) no consultan y no cuentan como ausencia.
