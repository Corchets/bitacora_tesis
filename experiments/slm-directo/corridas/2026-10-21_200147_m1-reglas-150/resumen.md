# Resumen de la corrida `2026-10-21_200147_m1-reglas-150`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --solo-reglas --etiqueta m1-reglas-150`
- **Inicio / fin:** 2026-10-21T20:01:47 / 2026-10-21T20:02:10
- **Código:** `d1a09db2bc` con cambios sin commit en la carpeta
- **Máquina:** macOS-27.0.1-arm64-arm-64bit, 8 núcleos lógicos, 8.0 GB de RAM
- **Ollama:** no usado · **Política:** aviso_unico_primer_true_valido
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 65/75 | 32 | 20 | 5 | 0 | 51/75 | 0/2773 | 8 | 16 | 116/116 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L6 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-003` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-007` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-008` | legítima | — | — | FA L3 |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L5 |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L3 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | FA L3 |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | FA L19 |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | FA L1 |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | FA L22 |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | FA L17 |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L8 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | FA L13 |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | FA L2 |
| `CV2-D-L-MEDICO-001` | legítima | — | — | FA L19 |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L20 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | FA L13 |
| `CV2-D-L-MEDICO-005` | legítima | — | — | FA L23 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | FA L8 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | FA L3 |
| `CV2-D-L-PREMIO-001` | legítima | — | — | FA L7 |
| `CV2-D-L-PREMIO-002` | legítima | — | — | FA L15 |
| `CV2-D-L-PREMIO-003` | legítima | — | — | FA L18 |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | FA L6 |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | FA L8 |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | FA L2 |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | FA L1 |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | FA L1 |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | FA L3 |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L3 |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | FA L24 |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | FA L9 |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | FA L3 |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L5 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L1 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | =R L14 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L5 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L4 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | <R L3 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L4 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | <R L14 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L3 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L7 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | >R L16 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L10 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L10 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L12 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L13 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L11 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L2 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L4 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L11 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L4 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L8 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L10 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L14 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L10 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 |
| `LAB-giro-sin-plata` | vishing | 3 | — | — |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | FA L1 |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | FA L9 |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L2 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L4 |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | — |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | FA L3 |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L2 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L6 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L5 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `reglas` · línea 6: «REQUEST_TRANSFER (patrón: transferencia, transferi)» — evidencia (cita textual): «puede ser una compra con tarjeta o una transferencia te figura como débito automático o consumo»
- `CV2-D-L-BANCO-002` · `reglas` · línea 2: «REQUEST_TRANSFER (patrón: transferencia, transferi)» — evidencia (cita textual): «Hola, llamo porque hice una transferencia ayer y no encuentro el comprobante.»
- `CV2-D-L-BANCO-003` · `reglas` · línea 1: «REQUEST_TRANSFER (patrón: paga)» — evidencia (cita textual): «Te llamo por el límite de la tarjeta. El viernes me voy unos días y tengo que pagar el hospedaje.»
- `CV2-D-L-BANCO-004` · `reglas` · línea 1: «REQUEST_TRANSFER (patrón: paga)» — evidencia (cita textual): «Hola, estoy llamando yo. Me pagaron un trabajo ayer y todavía no lo veo acreditado.»
- `CV2-D-L-BANCO-005` · `reglas` · línea 1: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «Buenas tardes, llamo yo porque veo dos veces el mismo pago del alquiler.»
- `CV2-D-L-BANCO-006` · `reglas` · línea 8: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «Veo un pago de farmacia por 12.800 y uno de servicios por 21.340.»
- `CV2-D-L-BANCO-007` · `reglas` · línea 1: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Llamo por el resumen de la tarjeta. Hay una línea que dice “clave de comercio” y no entiendo qué significa.»
- `CV2-D-L-BANCO-008` · `reglas` · línea 3: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Rechazó dos. En casa me dijeron que capaz tenían una clave marcada, pero no sé qué significa eso.»
- `CV2-D-L-BANCO-009` · `reglas` · línea 5: «REQUEST_SECRET (patrón: pin)» — evidencia (cita textual): «Uno pendiente por 27.900. Me acuerdo que marqué el PIN y después quedó cargando.»
- `CV2-D-L-BANCO-010` · `reglas` · línea 3: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «de un trámite impositivo creo que para justificar un pago yo con esas cosas me pierdo»
- `CV2-D-L-DELIVERY-001` · `reglas` · línea 3: «REQUEST_PERSONAL_DATA (patrón: domicilio)» — evidencia (cita textual): «es 63018 lo hice con el correo de mi pareja pero el domicilio es el mío»
- `CV2-D-L-DELIVERY-002` · `reglas` · línea 19: «REQUEST_TRANSFER (patrón: paga)» — evidencia (cita textual): «Perfecto. ¿Puedo pagar la diferencia del reemplazo cuando llegue?»
- `CV2-D-L-DELIVERY-004` · `reglas` · línea 1: «REQUEST_SECRET (patrón: pin)» — evidencia (cita textual): «Buen día, necesito cambiar la entrega de la mesa que compré. Están pintando el pasillo.»
- `CV2-D-L-ESCUELA-001` · `reglas` · línea 22: «REQUEST_SECURITY_ACTION (patrón: autoriza)» — evidencia (cita textual): «Sí, su tía figura autorizada para retirarla.»
- `CV2-D-L-ESCUELA-003` · `reglas` · línea 17: «REQUEST_SECURITY_ACTION (patrón: autoriza)» — evidencia (cita textual): «¿Necesita una autorización especial para entrar el martes?»
- `CV2-D-L-FAMILIAR-002` · `reglas` · línea 8: «REQUEST_TRANSFER (patrón: transferi)» — evidencia (cita textual): «Somos cuatro: transferime 11.700 por tu parte cuando puedas.»
- `CV2-D-L-FAMILIAR-003` · `reglas` · línea 13: «REQUEST_SECRET (patrón: pin)» — evidencia (cita textual): «Si está pinchada, la llevo al taller el viernes. No quiero que se quede sin entrenar.»
- `CV2-D-L-FAMILIAR-005` · `reglas` · línea 2: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «El baño ya está pago. Falta la visita de la cocina, que fue ayer.»
- `CV2-D-L-MEDICO-001` · `reglas` · línea 19: «REQUEST_TRANSFER (patrón: pago, transferencia, transferi)» — evidencia (cita textual): «¿Y el copago lo pago ahí o por transferencia?»
- `CV2-D-L-MEDICO-002` · `reglas` · línea 20: «REQUEST_SECURITY_ACTION (patrón: autoriza)» — evidencia (cita textual): «si autorizaste el portal suele aparecer ahí el laboratorio te confirma el estado»
- `CV2-D-L-MEDICO-004` · `reglas` · línea 13: «REQUEST_SECURITY_ACTION (patrón: autoriza)» — evidencia (cita textual): «tengo que volver a pedir autorización a la obra social»
- `CV2-D-L-MEDICO-005` · `reglas` · línea 23: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «Bueno. ¿El pago es al salir?»
- `CV2-D-L-ORGANISMO_PREVISIONAL-002` · `reglas` · línea 8: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «Según el cronograma publicado, para esa terminación el pago es el lunes 14.»
- `CV2-D-L-ORGANISMO_PREVISIONAL-003` · `reglas` · línea 3: «REQUEST_PERSONAL_DATA (patrón: domicilio)» — evidencia (cita textual): «en la de la terminal vieja por un cambio de domicilio»
- `CV2-D-L-PREMIO-001` · `reglas` · línea 7: «REQUEST_TRANSFER (patrón: cripto)» — evidencia (cita textual): «Julián Paredes. Está escrito medio torcido, pero se entiende.»
- `CV2-D-L-PREMIO-002` · `reglas` · línea 15: «REQUEST_TRANSFER (patrón: transferi)» — evidencia (cita textual): «¿Puedo transferirla a mi hermana si al final no voy?»
- `CV2-D-L-PREMIO-003` · `reglas` · línea 18: «REQUEST_SECURITY_ACTION (patrón: autoriza)» — evidencia (cita textual): «Consulto las bases. Dice que puede retirarlo otra persona con una autorización simple.»
- `CV2-D-L-SOPORTE-001` · `reglas` · línea 6: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «Voy a revisar la línea. ¿Me confirmás la calle y la altura donde está instalado?»
- `CV2-D-L-SOPORTE-002` · `reglas` · línea 8: «REQUEST_SECRET (patrón: contrasena)» — evidencia (cita textual): «Gracias. Encontré el usuario. ¿Ayer te pidieron cambiar la contraseña al vencer?»
- `CV2-D-L-SOPORTE-003` · `reglas` · línea 2: «REQUEST_TRANSFER (patrón: pago)» — evidencia (cita textual): «Hola. ¿Se apagó alguna luz del router o está todo encendido?»
- `CV2-D-L-SOPORTE-004` · `reglas` · línea 1: «REQUEST_REMOTE_ACCESS, REQUEST_SECRET (patrón: clave, instala)» — evidencia (cita textual): «Hola, reinstalé el programa de dibujo y me pide una clave que no encuentro.»
- `CV2-D-L-SOPORTE-005` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Buenas, la impresora dejó de conectarse y muestra el código E-14.»
- `CV2-D-L-TRABAJO-005` · `reglas` · línea 3: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «A las cuatro. Me preguntaron si tiene instalado el programa de edición.»
- `CV2-D-L-WHATSAPP-001` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Le pide confirmar el número, pero después sale un aviso de que mandaron un código.»
- `CV2-D-L-WHATSAPP-003` · `reglas` · línea 24: «REQUEST_TRANSFER (patrón: transferencia, transferi)» — evidencia (cita textual): «Sí, al registrar tu cuenta en el nuevo, el grupo debería aparecer si la transferencia de chats se completa.»
- `CV2-D-L-WHATSAPP-004` · `reglas` · línea 9: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Lo puedo hacer. El año pasado me apareció un código de registro cuando cambié el chip y pensé que era por eso.»
- `CV2-D-L-WHATSAPP-005` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «dice código 17 pero no sé si eso sirve no es un mensaje de texto aparece en la pantalla»
- `LAB-portero-codigo-puerta` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «el portero me paso el codigo de la puerta»
- `LG-BANK-VERIF-01-e01` · `reglas` · línea 2: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Hola, Lucía. Llamo al número que está atrás de mi tarjeta. Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `LG-FAMILIAR-LLAMADO-01-e01` · `reglas` · línea 7: «REQUEST_TRANSFER (patrón: plata)» — evidencia (cita textual): «¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-ORG-TURNO-01-e01` · `reglas` · línea 4: «REQUEST_PERSONAL_DATA (patrón: domicilio)» — evidencia (cita textual): «¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-PREMIO-CONSULTA-01-e01` · `reglas` · línea 9: «REQUEST_TRANSFER (patrón: paga)» — evidencia (cita textual): «A ver... sí, acá lo dice. ¿Y hay que pagar algo para retirarlo? ¿Un gasto de envío, algo así?»
- `LG-SUPPORT-INFO-01-e01` · `reglas` · línea 2: «REQUEST_SECRET (patrón: contrasena)» — evidencia (cita textual): «Hola, ¿qué tal? Los llamo porque no puedo entrar a mi cuenta desde la computadora: me dice que el usuario o la contraseña son incorrectos.»
- `LG-SUPPORT-INFO-01-e02` · `reglas` · línea 4: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «No, eso no. Nosotros no te vamos a pedir que compartas la pantalla ni que instales nada para que alguien entre a tu celular.»
- `LG-WA-CONSULTA-01-e01` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `TR-02-codigo-del-candado` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Dale. ¿Cuál era el código del candado? Me lo dijiste el otro día y no me acuerdo.»
- `TR-03-negacion-y-consejo` · `reglas` · línea 2: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Bien que me llames, ma. Escuchame una cosa: nunca le pases la clave del banco a nadie, ni a mí.»
- `TR-05-asado-con-transferencia` · `reglas` · línea 5: «REQUEST_TRANSFER (patrón: plata)» — evidencia (cita textual): «No, el carbón ya lo compró él. Escuchá, te llamaba por la plata, que la estoy juntando yo.»
- `TR-06-banco-alerta-legitima` · `reglas` · línea 10: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `reglas` · línea 4: «REQUEST_TRANSFER (patrón: transferi)» — evidencia (cita textual): «Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-005` · `reglas` · sin riesgo registrado
- `CV2-D-V-PREMIO-003` · `reglas` · sin riesgo registrado
- `CV2-D-V-PREMIO-005` · `reglas` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-008` · `reglas` · sin riesgo registrado
- `LAB-digitos-sin-palabra` · `reglas` · sin riesgo registrado
- `LAB-giro-sin-plata` · `reglas` · sin riesgo registrado
- `LAB-pantalla-sin-programa` · `reglas` · sin riesgo registrado
- `SC-PREMIO-01-e01` · `reglas` · sin riesgo registrado
- `TR-01-pedido-indirecto-digitos` · `reglas` · sin riesgo registrado
- `TR-12-corta-antes-del-pedido` · `reglas` · sin riesgo registrado

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.
