# Resumen de la corrida `2026-11-04_003715_e2b-tito-viejo-150`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --prompts tarea --hablantes ab --filtro-tito --tito-real --num-ctx 4096 --seed 42 --etiqueta e2b-tito-viejo-150`
- **Inicio / fin:** 2026-11-04T00:37:15 / 2026-11-04T00:46:04
- **Código:** `833a3fb5b2` con cambios sin commit en la carpeta
- **Máquina:** Windows-11-10.0.26300-SP0, 12 núcleos lógicos, 31.9 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 65/75 | 32 | 20 | 5 | 0 | 51/75 | 0/1319 | 7 | 14 | 116/116 | 0 |
| `tito-slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` | 51/75 | 17 | 29 | 4 | 1 | 13/75 | 0/2318 | 296 | 416 | 62/64 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas` · **C2** `tito-slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L6 | ok |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L2 | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | FA L1 | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L1 | ok |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L1 | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L8 | ok |
| `CV2-D-L-BANCO-007` | legítima | — | — | FA L1 | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | FA L3 | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L5 | ok |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L3 | FA L10 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | FA L3 | ok |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | FA L19 | ok |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | FA L1 | ok |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | FA L22 | ok |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | FA L17 | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L8 | FA L11 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | FA L13 | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | FA L2 | FA L10 |
| `CV2-D-L-MEDICO-001` | legítima | — | — | FA L19 | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L20 | ok |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | FA L13 | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | FA L23 | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | FA L8 | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | FA L3 | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | FA L7 | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | FA L15 | ok |
| `CV2-D-L-PREMIO-003` | legítima | — | — | FA L18 | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | FA L6 | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | FA L8 | ok |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | FA L2 | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | FA L1 | ok |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | FA L1 | ok |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | FA L3 | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L3 | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | FA L24 | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | FA L9 | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | FA L3 | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 | <R L29 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L5 | =R L18 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L1 | — |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 | <R L5 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | =R L14 | =R L14 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 | =R L17 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L5 | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L1 | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 | — |
| `CV2-D-V-BANCO-012` | vishing | — | — | L4 | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | <R L3 | >R L16 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L4 | >R L17 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | <R L14 | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | <R L8 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L3 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L7 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L12 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | >R L16 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L10 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L10 | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L12 | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L13 | — |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L11 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 | >R L14 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L2 | >R L17 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L4 | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L11 | <R L14 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L4 | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L8 | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 | <R L8 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L10 | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L14 | =R L25 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L10 | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | FA L3 |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | =R L5 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 | <R L4 |
| `LAB-banco-revisa-app` | legítima | — | — | ok | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | ok | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | FA L1 | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 | FA L6 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | FA L9 | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L2 | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L4 | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | — | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — | — |
| `TR-02-codigo-del-candado` | legítima | — | — | FA L3 | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L2 | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L6 | ≥C L27 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L5 | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 | =R L7 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | =R L5 | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 | <R L6 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok | FA L5 |

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
- `CV2-D-L-BANCO-002` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 7: «Te están pidiendo los últimos cuatro dígitos de tu cuenta para identificarla.» — evidencia (cita textual): «Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 8: «No compartas los últimos cuatro dígitos de tu cuenta, ya que te los están pidiendo para encontrarla.» — evidencia (cita textual): «B: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-010` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo los últimos cuatro números de una cuenta bancaria para ubicarla.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-FAMILIAR-002` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 11: «Te están pidiendo un alias por mensaje, lo cual puede ser una forma de obtener acceso a alguna cuenta o servicio.» — evidencia (cita textual): «Pasame el alias por mensaje así no lo tengo que copiar de memoria.»
- `CV2-D-L-FAMILIAR-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo que transfieras dinero.» — evidencia (cita textual): «Poné esos 15.000; yo pongo 19.000 y mamá completa los 4.000 que faltan.»
- `LAB-arca-canal-oficial` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están indicando que debes ingresar a una página web para resolver un supuesto embargo.» — evidencia (cita textual): «B: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-revisa-app` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación oficial, lo cual es una táctica común para engañarte.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-no-bajes-nada` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo que descargues un programa y muestres tu celular, lo cual es una táctica común para obtener acceso a tu dispositivo.» — evidencia (cita textual): «A: me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 6: «No le des los números de tu tarjeta a nadie por teléfono.» — evidencia (cita textual): «Dale. ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `TR-06-banco-alerta-legitima` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo que compartas un código que te llegó por mensaje para verificar algo.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código que te pertenece.» — evidencia (cita textual): «A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 9: «Te están pidiendo realizar una transferencia de dinero a una cuenta específica.» — evidencia (cita textual): «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento.» — evidencia (cita textual): «A: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

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
- `CV2-D-V-BANCO-003` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-BANCO-011` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.60
- `CV2-D-V-BANCO-012` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.40
- `CV2-D-V-FAMILIAR-004` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-006` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-PREMIO-001` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-002` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-003` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.10
- `CV2-D-V-PREMIO-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-006` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-SOPORTE-001` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-SOPORTE-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.40
- `CV2-D-V-SOPORTE-008` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-004` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-WHATSAPP-007` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-WHATSAPP-008` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.40
- `TR-01-pedido-indirecto-digitos` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `TR-12-corta-antes-del-pedido` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 86.204 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 6 ms; encoder: 65.513 ms (carga fresca); calentamiento Tito: 27 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab`

Consultas al SLM hasta el aviso: 1179; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 432.906 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | sin aviso | 22 | 0 | 0 | 7.113 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 823 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 614 |
| `CV2-D-L-BANCO-004` | 5 | sin aviso | 20 | 4 | 0 | 6.425 |
| `CV2-D-L-BANCO-005` | 8 | L8 | 1 | 7 | 0 | 938 |
| `CV2-D-L-BANCO-006` | 6 | sin aviso | 19 | 5 | 0 | 6.099 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 596 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 560 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 584 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 1.104 |
| `CV2-D-L-DELIVERY-001` | 6 | sin aviso | 19 | 5 | 0 | 6.020 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 682 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 7.440 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 655 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 683 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 615 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 7.829 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 619 |
| `CV2-D-L-ESCUELA-004` | 7 | sin aviso | 20 | 6 | 0 | 6.378 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 8.306 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 640 |
| `CV2-D-L-FAMILIAR-002` | 11 | L11 | 1 | 10 | 0 | 1.108 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 2.224 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 3.063 |
| `CV2-D-L-FAMILIAR-005` | 10 | L10 | 1 | 9 | 0 | 952 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 674 |
| `CV2-D-L-MEDICO-002` | 7 | sin aviso | 20 | 6 | 0 | 6.312 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 655 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 622 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 5.588 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | sin aviso | 19 | 5 | 0 | 6.082 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 646 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 4.831 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 657 |
| `CV2-D-L-PREMIO-002` | 5 | sin aviso | 21 | 4 | 0 | 6.667 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 689 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 665 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 5.681 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 6.486 |
| `CV2-D-L-SOPORTE-004` | 1 | sin aviso | 24 | 0 | 0 | 7.605 |
| `CV2-D-L-SOPORTE-005` | 10 | sin aviso | 15 | 9 | 0 | 5.061 |
| `CV2-D-L-TRABAJO-001` | 2 | sin aviso | 22 | 1 | 0 | 6.955 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 6.669 |
| `CV2-D-L-TRABAJO-003` | 10 | sin aviso | 16 | 9 | 0 | 5.333 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 658 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 8.651 |
| `CV2-D-L-WHATSAPP-001` | 16 | sin aviso | 8 | 15 | 0 | 3.116 |
| `CV2-D-L-WHATSAPP-002` | 10 | sin aviso | 14 | 9 | 0 | 4.692 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 4.838 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 6.076 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 7.684 |
| `CV2-D-V-BANCO-001` | 29 | L29 | 1 | 28 | 0 | 1.609 |
| `CV2-D-V-BANCO-002` | 6 | L18 | 13 | 5 | 0 | 4.421 |
| `CV2-D-V-BANCO-003` | 5 | sin aviso | 22 | 4 | 0 | 7.006 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 950 |
| `CV2-D-V-BANCO-005` | 1 | L5 | 5 | 0 | 0 | 1.995 |
| `CV2-D-V-BANCO-006` | 2 | L14 | 13 | 1 | 0 | 4.517 |
| `CV2-D-V-BANCO-007` | 11 | L17 | 7 | 10 | 0 | 2.787 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 1.183 |
| `CV2-D-V-BANCO-009` | 3 | L13 | 11 | 2 | 0 | 3.848 |
| `CV2-D-V-BANCO-010` | 1 | L1 | 1 | 0 | 0 | 722 |
| `CV2-D-V-BANCO-011` | 12 | sin aviso | 10 | 11 | 0 | 3.538 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 6.750 |
| `CV2-D-V-FAMILIAR-001` | 5 | L16 | 12 | 4 | 0 | 4.105 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 1.059 |
| `CV2-D-V-FAMILIAR-003` | 14 | L17 | 4 | 13 | 0 | 2.090 |
| `CV2-D-V-FAMILIAR-004` | 14 | sin aviso | 16 | 13 | 0 | 5.470 |
| `CV2-D-V-FAMILIAR-005` | 18 | sin aviso | 4 | 17 | 0 | 1.848 |
| `CV2-D-V-FAMILIAR-006` | 17 | sin aviso | 7 | 16 | 0 | 2.661 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L12 | 11 | 1 | 0 | 3.926 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L9 | 9 | 0 | 0 | 3.302 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | sin aviso | 8 | 12 | 0 | 2.856 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | sin aviso | 20 | 1 | 0 | 6.456 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 7.058 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 7.090 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 525 |
| `CV2-D-V-PREMIO-002` | 3 | sin aviso | 18 | 2 | 0 | 5.830 |
| `CV2-D-V-PREMIO-003` | 3 | sin aviso | 26 | 2 | 0 | 8.265 |
| `CV2-D-V-PREMIO-004` | 12 | L14 | 3 | 11 | 0 | 1.543 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 6.307 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 7.071 |
| `CV2-D-V-SOPORTE-001` | 12 | sin aviso | 10 | 11 | 0 | 3.490 |
| `CV2-D-V-SOPORTE-002` | 1 | L7 | 7 | 0 | 0 | 2.651 |
| `CV2-D-V-SOPORTE-003` | 1 | L14 | 14 | 0 | 0 | 4.842 |
| `CV2-D-V-SOPORTE-004` | 13 | L17 | 5 | 12 | 0 | 2.326 |
| `CV2-D-V-SOPORTE-005` | 10 | sin aviso | 12 | 9 | 0 | 4.040 |
| `CV2-D-V-SOPORTE-006` | 1 | L14 | 14 | 0 | 0 | 4.840 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 1.798 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 1.825 |
| `CV2-D-V-WHATSAPP-001` | 1 | L9 | 9 | 0 | 0 | 3.183 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 1.017 |
| `CV2-D-V-WHATSAPP-003` | 8 | L8 | 1 | 7 | 0 | 761 |
| `CV2-D-V-WHATSAPP-004` | 5 | sin aviso | 17 | 4 | 0 | 5.443 |
| `CV2-D-V-WHATSAPP-005` | 10 | L13 | 4 | 9 | 0 | 1.786 |
| `CV2-D-V-WHATSAPP-006` | 22 | L25 | 4 | 21 | 0 | 2.274 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 4.616 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 4.057 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 1.434 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.353 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 1.400 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.416 |
| `LAB-anses-canal-oficial` | 5 | sin aviso | 1 | 4 | 0 | 478 |
| `LAB-arca-canal-oficial` | 1 | L3 | 3 | 0 | 0 | 1.319 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 1.348 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 659 |
| `LAB-banco-app-parafrasis` | 1 | sin aviso | 5 | 0 | 0 | 1.825 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 1.268 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.314 |
| `LAB-banco-gasto-sin-pedido` | 1 | sin aviso | 3 | 0 | 0 | 1.115 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 411 |
| `LAB-banco-numeros-sin-clave` | 1 | L4 | 4 | 0 | 0 | 1.745 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 745 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 1.439 |
| `LAB-familiar-llama-vos` | 2 | sin aviso | 4 | 1 | 0 | 1.503 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 1.680 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 1.695 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 1.272 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 1.860 |
| `LAB-no-bajes-nada` | 4 | L4 | 1 | 3 | 0 | 785 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 1.363 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 419 |
| `LAB-whatsapp-codigo` | 1 | L3 | 3 | 0 | 0 | 1.270 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.314 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 851 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 1.061 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 405 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 1.894 |
| `LG-SUPPORT-INFO-01-e01` | 7 | sin aviso | 7 | 6 | 0 | 2.504 |
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 2.195 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 115 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L2 | 1 | 1 | 0 | 696 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 920 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 1.948 |
| `SC-PREMIO-01-e01` | 3 | L8 | 6 | 2 | 0 | 2.312 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 1.726 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.426 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.415 |
| `TR-01-pedido-indirecto-digitos` | 3 | sin aviso | 10 | 2 | 0 | 3.312 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 2.355 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 282 |
| `TR-04-pedido-tras-charla-larga` | 5 | L27 | 23 | 4 | 0 | 7.921 |
| `TR-05-asado-con-transferencia` | 14 | sin aviso | 14 | 13 | 0 | 4.950 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 3.011 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L7 | 3 | 4 | 0 | 1.331 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 536 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.005 |
| `TR-10-ofrecimiento-inducido` | 4 | L6 | 3 | 3 | 0 | 1.462 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 932 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 1.807 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 699 |

Nunca derivados (permanecen en sus denominadores):
- `CV2-D-V-PREMIO-001` · vishing sin aviso (falso negativo visible).
- `CV2-D-L-BANCO-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-BANCO-007` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-BANCO-008` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-BANCO-009` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-DELIVERY-002` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-DELIVERY-004` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-DELIVERY-005` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-ESCUELA-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-ESCUELA-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-FAMILIAR-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-MEDICO-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-MEDICO-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-MEDICO-004` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-ORGANISMO_PREVISIONAL-002` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-PREMIO-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-PREMIO-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-SOPORTE-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-TRABAJO-004` · legítima sin aviso (verdadero negativo).
- `LG-ORG-TURNO-01-e01` · legítima sin aviso (verdadero negativo).
- `LG-WA-CONSULTA-01-e01` · legítima sin aviso (verdadero negativo).
- `TR-03-negacion-y-consejo` · legítima sin aviso (verdadero negativo).


## Costos por componente hasta el aviso

Modo de término: `operativo-hasta-aviso`.
Cada caso aporta sus actualizaciones evaluadas hasta el aviso incluido; una llamada sin aviso aporta la conversación completa. `ms` total = Tito + SLM por actualización, sin doble conteo.

| Configuración | ms hasta aviso | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|
| `reglas` | 9.561 | — | — | 0 | 1319 | 0/1319 |
| `tito-slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` | 432.906 | 34.192 | 398.713 | 979823 | 2318 | 1179/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
