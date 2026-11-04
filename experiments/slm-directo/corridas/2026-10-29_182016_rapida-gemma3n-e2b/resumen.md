# Resumen de la corrida `2026-10-29_182016_rapida-gemma3n-e2b`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma3n:e2b --prompts riesgo,v2 --lista rapida-20 --solo-cpu --num-batch 32 --sin-reglas --etiqueta rapida-gemma3n-e2b`
- **Inicio / fin:** 2026-10-29T18:20:16 / 2026-10-29T20:03:16
- **Código:** `8c8be37be1`
- **Máquina:** Windows-11-10.0.26300-SP0, 8 núcleos lógicos, 15.7 GB de RAM
- **Ollama:** 0.40.13 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 20 (10 vishing, 10 legítimas); 20 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma3n:e2b\|riesgo\|ab` | 10/10 | 6 | 4 | 0 | 0 | 6/10 | 0/524 | 1.918 | 2.295 | 15/16 | 0 |
| `slm\|gemma3n:e2b\|v2\|ab` | 10/10 | 10 | 0 | 0 | 0 | 9/10 | 0/524 | 10.036 | 13.511 | 19/19 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma3n:e2b\|riesgo\|ab` · **C2** `slm\|gemma3n:e2b\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L7 | FA L4 |
| `CV2-D-L-BANCO-007` | legítima | — | — | ok | FA L1 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | FA L16 | FA L2 |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | ok | FA L7 |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok | ok |
| `CV2-D-L-MEDICO-001` | legítima | — | — | FA L17 | FA L5 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L5 | FA L4 |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok | FA L4 |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | FA L7 | FA L3 |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L16 | FA L2 |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L29 | <R L8 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | =R L18 | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L8 | <R L4 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 | <R L5 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L8 | <R L8 |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L10 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 | <R L8 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L13 | <R L8 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 | <R L8 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | =R L25 | <R L14 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `slm|gemma3n:e2b|riesgo|ab` · línea 7: «Le están pidiendo que verifique un código que aparece en la tarjeta, lo cual es un pedido de información sensible.» — evidencia (cita textual): «dice débito tarjeta pero abajo aparece un código que no entiendo»
- `CV2-D-L-DELIVERY-001` · `slm|gemma3n:e2b|riesgo|ab` · línea 16: «Se solicita una firma para recibir el paquete, lo cual puede ser un intento de obtener acceso a información personal o de cuentas.» — evidencia (cita textual): «queda indicado el paquete requiere firma de quien lo recibe»
- `CV2-D-L-MEDICO-001` · `slm|gemma3n:e2b|riesgo|ab` · línea 17: «Se le pide que proporcione un documento (informe de análisis de sangre) y se le indica cómo hacerlo (impreso o desde el teléfono). Esto podría ser un intento de obtener información sensible o acceso a datos médicos.» — evidencia (cita textual): «Traé el informe impreso o mostralo desde el teléfono si lo recibiste en PDF.»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma3n:e2b|riesgo|ab` · línea 5: «Se solicita el número de trámite sin datos de acceso, lo cual es una práctica común en estafas para obtener información sensible.» — evidencia (cita textual): «Me decís ese número, sin datos de acceso?»
- `CV2-D-L-SOPORTE-002` · `slm|gemma3n:e2b|riesgo|ab` · línea 7: «Se solicita información sensible (nombre del consultorio y parte del correo) para revisar una cuenta.» — evidencia (cita textual): «Para revisar la cuenta, ¿me confirmás el nombre del consultorio y las primeras letras del correo registrado?»
- `CV2-D-L-WHATSAPP-001` · `slm|gemma3n:e2b|riesgo|ab` · línea 16: «Se le pide ingresar un código en la aplicación.» — evidencia (cita textual): «Que los ingrese en la pantalla de la aplicación.»
- `CV2-D-L-BANCO-001` · `slm|gemma3n:e2b|v2|ab` · línea 4: «La persona está siendo solicitada a proporcionar información sobre su cuenta bancaria (caja de ahorro) para verificar un movimiento sospechoso. Esto podría ser un intento de obtener acceso a sus fondos o datos personales.» — evidencia (cita textual): «mirar el movimiento figura hoy o ayer»
- `CV2-D-L-BANCO-007` · `slm|gemma3n:e2b|v2|ab` · línea 1: «La solicitud de 'clave de comercio' es inusual y podría ser un intento de obtener información sensible. Es crucial no revelar esta información a nadie.» — evidencia (cita textual): «clave de comercio»
- `CV2-D-L-DELIVERY-001` · `slm|gemma3n:e2b|v2|ab` · línea 2: «Solicitan información personal (número de compra) que podría ser utilizada para acceder a una cuenta o realizar una transacción fraudulenta. Es crucial no proporcionar esta información.» — evidencia (cita textual): «tenés el número de compra»
- `CV2-D-L-ESCUELA-001` · `slm|gemma3n:e2b|v2|ab` · línea 7: «La persona está pidiendo información sobre dónde se encuentra Nina, lo cual podría ser un intento de acceder a su ubicación y, potencialmente, a sus cuentas o información personal. El hecho de que se haya ido a un banco sugiere que podría haber información sensible allí.» — evidencia (cita textual): «se fue a leer a un banco»
- `CV2-D-L-MEDICO-001` · `slm|gemma3n:e2b|v2|ab` · línea 5: «La persona está siendo presionada a cambiar su horario y se le está pidiendo información personal (nombre y fecha del turno) para confirmar su identidad. Esto podría ser un intento de acceder a sus datos de programación en el sistema de la empresa.» — evidencia (cita textual): «Querés pasarlo para otro día o buscar un horario más temprano»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma3n:e2b|v2|ab` · línea 4: «Solicitud de información sensible (número de trámite) sin datos de acceso, lo cual es un pedido de información personal que podría ser utilizado para fines fraudulentos.» — evidencia (cita textual): «Me decís ese número, sin datos de acceso?»
- `CV2-D-L-PREMIO-001` · `slm|gemma3n:e2b|v2|ab` · línea 4: «Solicitan información sobre el número que compró, lo cual podría ser un intento de acceder a datos personales o información relacionada con la rifa. Es una solicitud de información sensible.» — evidencia (cita textual): «¿Tenés el talonario o una foto del número?»
- `CV2-D-L-SOPORTE-002` · `slm|gemma3n:e2b|v2|ab` · línea 3: «La persona está indicando que ha entrado previamente con el mismo correo, pero ahora no puede. Esto podría ser un intento de acceder a la cuenta a través de un método diferente o de engañar al sistema. Es importante verificar la autenticidad del correo y la cuenta.» — evidencia (cita textual): «Dice que el correo no existe, pero ayer entré con el mismo.»
- `CV2-D-L-WHATSAPP-001` · `slm|gemma3n:e2b|v2|ab` · línea 2: «La pregunta sobre el acceso a WhatsApp implica que se está buscando acceder a información personal o a un grupo de contactos, lo cual podría ser un intento de obtener información sensible.» — evidencia (cita textual): «Puede entrar a WhatsApp o le quedó la pantalla de registro?»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma3n:e2b` | 1.645 | 6.426 | — |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
