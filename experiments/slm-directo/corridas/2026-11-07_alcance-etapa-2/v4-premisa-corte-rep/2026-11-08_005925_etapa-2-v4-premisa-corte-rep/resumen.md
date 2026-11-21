# Resumen de la corrida `2026-11-08_005925_etapa-2-v4-premisa-corte-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts v4-premisa-corte --lista alcance-140 --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --seguir-tras-aviso --hablantes rol --etiqueta etapa-2-v4-premisa-corte-rep --salida /content/resultados-etapa-2/v4-premisa-corte-rep`
- **Inicio / fin:** 2026-11-08T00:59:25 / 2026-11-08T01:13:28
- **Código:** `d127953fcc`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 140 (46 vishing, 94 legítimas); 140 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|v4-premisa-corte\|rol` | 27/46 | 11 | 14 | 1 | 0 | 42/94 | 0/2621 | 291 | 362 | 67/69 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|v4-premisa-corte\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-V-BANCO-001` | vishing | 32 | — | =R L32 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L13 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L11 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L3 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L6 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L12 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L12 |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L13 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | — |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `ENT-L-BANCO-001` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L5 |
| `ENT-L-BANCO-004` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L4 |
| `ENT-L-DELIVERY-001` | legítima | — | — | FA L15 |
| `ENT-L-DELIVERY-002` | legítima | — | — | FA L8 |
| `ENT-L-DELIVERY-003` | legítima | — | — | ok |
| `ENT-L-DELIVERY-004` | legítima | — | — | FA L8 |
| `ENT-L-DELIVERY-005` | legítima | — | — | ok |
| `ENT-L-DELIVERY-006` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-001` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-002` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-003` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-004` | legítima | — | — | FA L6 |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | ok |
| `ENT-L-MEDICO-001` | legítima | — | — | FA L5 |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | FA L3 |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | ok |
| `ENT-L-SELECCION-003` | legítima | — | — | FA L10 |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L3 |
| `ENT-L-SOPORTE-002` | legítima | — | — | FA L6 |
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L18 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L5 |
| `ENT-L-SOPORTE-006` | legítima | — | — | FA L8 |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | FA L4 |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L13 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | FA L5 |
| `ENT-L-VENTAS-006` | legítima | — | — | ok |
| `ENT-L-VENTAS-007` | legítima | — | — | FA L11 |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | ok |
| `ENT-L-VENTAS-010` | legítima | — | — | FA L8 |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L5 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | FA L3 |
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
| `LEG2-BA-01` | legítima | — | — | FA L4 |
| `LEG2-BA-02` | legítima | — | — | FA L4 |
| `LEG2-BA-03` | legítima | — | — | FA L2 |
| `LEG2-BA-05` | legítima | — | — | FA L4 |
| `LEG2-CC-01` | legítima | — | — | FA L8 |
| `LEG2-CC-04` | legítima | — | — | ok |
| `LEG2-CC-05` | legítima | — | — | FA L6 |
| `LEG2-CC-06` | legítima | — | — | ok |
| `LEG2-CO-01` | legítima | — | — | ok |
| `LEG2-CO-02` | legítima | — | — | FA L8 |
| `LEG2-CO-03` | legítima | — | — | ok |
| `LEG2-CO-06` | legítima | — | — | FA L10 |
| `LEG2-EN-01` | legítima | — | — | ok |
| `LEG2-EN-03` | legítima | — | — | ok |
| `LEG2-EN-04` | legítima | — | — | FA L4 |
| `LEG2-EN-05` | legítima | — | — | ok |
| `LEG2-ST-02` | legítima | — | — | FA L6 |
| `LEG2-ST-03` | legítima | — | — | FA L4 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | ok |
| `LEG2-TU-01` | legítima | — | — | FA L6 |
| `LEG2-TU-02` | legítima | — | — | ok |
| `LEG2-TU-05` | legítima | — | — | ok |
| `LEG2-TU-06` | legítima | — | — | FA L4 |
| `LEG2-VE-01` | legítima | — | — | FA L6 |
| `LEG2-VE-04` | legítima | — | — | FA L6 |
| `LEG2-VE-05` | legítima | — | — | ok |
| `LEG2-VE-06` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 3: «No le des tu DNI ni fecha de nacimiento, ya que te lo están pidiendo para validar tu identidad.» — evidencia (cita textual): «antes de darte información necesito validar que hablo con el titular me me decís tu dni y tu fecha de nacimiento»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No compartas información sobre transacciones bancarias ni detalles de seguridad de tu cuenta.» — evidencia (cita textual): «Registramos dos ingresos a tu home banking desde un celular que no tenías registrado, esta madrugada.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 5: «No debe confirmar los últimos tres números de su documento, ya que esto es información sensible que los estafadores buscan para acceder a sus cuentas.» — evidencia (cita textual): «Gracias, señor Sosa. ¿Me confirma los últimos tres números de su documento?»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No le entregues tu DNI, ya que te lo están pidiendo para validar tu identidad.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 3: «No confirme su documento, ya que esto es una táctica común para robar información personal.» — evidencia (cita textual): «¿Me confirma su documento para validar?»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No confirmes tu DNI, ya que te lo están pidiendo para acceder a tu aplicación del banco.» — evidencia (cita textual): «Marcos, ¿me confirmás tu DNI?»
- `ENT-L-DELIVERY-001` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 15: «No firmes documentos ni reveles información personal por teléfono.» — evidencia (cita textual): «Sí, me firmás en el celular y me decís el documento de quien recibe.»
- `ENT-L-DELIVERY-002` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 8: «No proporciones tu nombre y DNI, ya que esto es información personal sensible que no debes compartir por teléfono.» — evidencia (cita textual): «para el remito necesito el nombre y el dni de quien lo recibe»
- `ENT-L-DELIVERY-004` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 8: «No compartas tu número de documento, ya que te lo están pidiendo para dejar un paquete a tu nombre.» — evidencia (cita textual): «OTRA: ¿Me confirmás tu número de documento para dejarlo asentado a tu nombre?»
- `ENT-L-ENCUESTA-004` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No confirmes tu número de documento, ya que te lo están pidiendo para validar tu afiliación.» — evidencia (cita textual): «Para validar que sos afiliada, ¿me confirmás tu número de documento?»
- `ENT-L-MEDICO-001` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 5: «No confirmes tu DNI, ya que te lo están pidiendo para confirmar un turno médico.» — evidencia (cita textual): «Para dejar cargada la admisión, ¿me confirmás tu DNI?»
- `ENT-L-MEDICO-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 3: «No le des tu número de documento, ya que te lo están pidiendo para confirmar un turno.» — evidencia (cita textual): «Santiago, tenés turno mañana a las siete y media para extracción. Para confirmarlo, ¿me decís tu número de documento?»
- `ENT-L-SELECCION-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 10: «No proporciones tu CUIL, ya que te están pidiendo datos personales sensibles.» — evidencia (cita textual): «Perfecto. ¿Y su número de CUIL?»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 3: «No le des tu DNI a nadie por teléfono, es información personal sensible.» — evidencia (cita textual): «para validar que hablo con la titular me confirmás tu dni»
- `ENT-L-SOPORTE-002` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No proporciones tu DNI, ya que te lo están pidiendo bajo el pretexto de validar una garantía.» — evidencia (cita textual): «me imagino para validar la garantía necesito el dni del titular de la factura»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 18: «No confirmes documentos personales, ya que esto puede ser usado para suplantación de identidad.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el documento que dejaste?»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 5: «No confirmes tu correo electrónico, ya que te están pidiendo un dato personal para supuestamente resolver un problema de facturación.» — evidencia (cita textual): «OTRA: ¿Me confirmás el mail con el que estás registrado?»
- `ENT-L-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 8: «No confirmes tu número de documento, ya que te lo están pidiendo para proceder con el envío del chip.» — evidencia (cita textual): «Para el envío, ¿me confirmás tu número de documento?»
- `ENT-L-TRAMITE-002` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No le des tu DNI ni tu fecha de nacimiento, ya que te los están pidiendo para confirmar un turno.» — evidencia (cita textual): «Lourdes, sacaste un turno para la renovación de la licencia. ¿Me confirmás tu DNI y tu fecha de nacimiento?»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 13: «No le des tu DNI a nadie, ya que esto es una solicitud común en estafas para validar tu identidad.» — evidencia (cita textual): «para cargarlo necesito validar que hablo con la titular me pasás tu dni»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 14: «No entregues tu nombre completo y DNI, ya que esto puede ser usado para suplantar tu identidad.» — evidencia (cita textual): «si querés te dejo la solicitud cargada para eso necesito tu nombre completo y tu dni»
- `ENT-L-VENTAS-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 5: «No confirmes tu DNI, ya que te están pidiendo un dato personal para validar tu identidad.» — evidencia (cita textual): «Faltaba validar la identidad. ¿Me confirmás tu DNI?»
- `ENT-L-VENTAS-007` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 11: «No compartas tu nombre completo, DNI y salario con personas que no hayas contactado previamente para verificar la legitimidad de la oferta.» — evidencia (cita textual): «tu nombre completo el dni y más o menos cuánto ganás por mes en blanco»
- `ENT-L-VENTAS-010` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 8: «No confirmes tu DNI, ya que te lo están pidiendo para un proceso de entrega de un producto.» — evidencia (cita textual): «¿Me confirmás tu DNI?»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 5: «Aunque mencionan un intento de compra, no están pidiendo ninguna acción inmediata o dato personal que comprometa tu seguridad.» — evidencia (cita textual): «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 3: «No proporciones ninguna información ni confirmación sobre los inicios de sesión, ya que esto es una táctica de phishing.» — evidencia (cita textual): «Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 3: «No debe confirmar ni negar la transacción, ya que esto puede ser una técnica para obtener información o validar datos de la tarjeta.» — evidencia (cita textual): «Solo necesito que me digas si la reconocés o no.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No le des tu DNI ni fecha de nacimiento, ya que te lo están pidiendo para validar tu identidad.» — evidencia (cita textual): «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No confirmes tu DNI, ya que te están pidiendo datos personales bajo el pretexto de una actividad sospechosa en tu cuenta.» — evidencia (cita textual): «Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, ¿me confirmás tu DNI?»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 2: «No proporciones tu nombre completo, ya que te están pidiendo datos personales bajo el pretexto de ser del banco.» — evidencia (cita textual): «Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No proporciones tu DNI, ya que te lo están pidiendo para validar la identidad.» — evidencia (cita textual): «Diego, ¿me confirmás tu DNI para validar?»
- `LEG2-CC-01` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 8: «No confirmes tu número de DNI, ya que te lo están pidiendo para validar la identidad.» — evidencia (cita textual): «Para validar que hablo con la titular, ¿me confirmás tu número de DNI?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No confirmes tu DNI, ya que te están pidiendo un dato personal para validar tu identidad.» — evidencia (cita NO textual): «Gonzalo, te habla Micaela, de Telnor. Te llamo porque el viernes completaste el formulario en la web para pasarte con nosotros manteniendo tu número. Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CO-02` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 8: «No le des el nombre y DNI del encargado, ya que esto puede ser usado para suplantar la identidad.» — evidencia (cita textual): «Para el remito necesito el nombre y el DNI de quien lo recibe.»
- `LEG2-CO-06` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 10: «No le des el DNI de tu hermano, ya que es información personal sensible.» — evidencia (cita textual): «¿Me pasás el DNI de él para el remito?»
- `LEG2-EN-04` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No confirmes tu DNI, ya que te lo están pidiendo para validar tu afiliación.» — evidencia (cita textual): «Valeria, estamos haciendo una encuesta corta a los afiliados que se atendieron este mes. Para validar que sos afiliada, ¿me confirmás tu DNI?»
- `LEG2-ST-02` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No proporciones tu DNI, ya que te lo están pidiendo para validar una garantía.» — evidencia (cita textual): «Para validar la garantía necesito el DNI del titular de la factura.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No confirmes tu DNI, ya que te están pidiendo un dato personal para registrar un dispositivo.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el DNI que dejaste?»
- `LEG2-TU-01` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No confirmes tu DNI, ya que te lo están pidiendo para 'cargar la admisión'.» — evidencia (cita textual): «Para dejar cargada la admisión, ¿me confirmás tu DNI?»
- `LEG2-TU-06` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 4: «No le des tu DNI ni tu fecha de nacimiento a nadie por teléfono.» — evidencia (cita textual): «Florencia, sacaste un turno para la renovación de la licencia. ¿Me confirmás tu DNI y tu fecha de nacimiento?»
- `LEG2-VE-01` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No le des tu nombre completo y DNI a nadie por teléfono, especialmente si te ofrecen precalificación de crédito.» — evidencia (cita textual): «Tu nombre completo y el DNI, nada más. Consulto con la financiera y te digo.»
- `LEG2-VE-04` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · línea 6: «No le des tu DNI a nadie por teléfono, ya que esto es una solicitud de datos personales que puede ser usada para suplantación.» — evidencia (cita textual): «¿Me confirmás tu DNI?»

### Vishing sin aviso

- `CV2-D-V-BANCO-012` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-004` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-007` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-004` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-007` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `slm|gemma4:e2b-it-q4_K_M|v4-premisa-corte|rol` · riesgo máximo 0.30

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 448 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|v4-premisa-corte\|rol` | 596.356 | 841.400 | 0 | 596.356 | 1.93045e+06 | 1798 | 1798/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (0 en esta corrida) no consultan y no cuentan como ausencia.
