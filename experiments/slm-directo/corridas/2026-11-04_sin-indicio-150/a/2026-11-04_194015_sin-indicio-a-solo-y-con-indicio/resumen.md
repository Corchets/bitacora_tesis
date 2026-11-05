# Resumen de la corrida `2026-11-04_194015_sin-indicio-a-solo-y-con-indicio`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --prompts tarea --hablantes ab --num-ctx 4096 --seed 42 --filtro-tito --tito-real --etiqueta sin-indicio-a-solo-y-con-indicio --salida /content/resultados-sin-indicio/a`
- **Inicio / fin:** 2026-11-04T19:40:15 / 2026-11-04T20:11:54
- **Código:** `4916eada64`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 65/75 | 32 | 20 | 5 | 0 | 51/75 | 0/1319 | 10 | 27 | 116/116 | 0 |
| `slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` | 55/75 | 25 | 26 | 3 | 0 | 19/75 | 0/2214 | 422 | 608 | 69/74 | 0 |
| `tito-slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` | 50/75 | 18 | 28 | 3 | 1 | 12/75 | 0/2328 | 388 | 648 | 61/62 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas` · **C2** `slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` · **C3** `tito-slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 | C3 |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L6 | FA L12 | ok |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L2 | FA L7 | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | FA L1 | ok | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L1 | ok | ok |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L1 | ok | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L8 | ok | ok |
| `CV2-D-L-BANCO-007` | legítima | — | — | FA L1 | ok | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | FA L3 | ok | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L5 | ok | ok |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L3 | FA L10 | FA L10 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | FA L3 | ok | ok |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | FA L19 | ok | ok |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | FA L1 | ok | ok |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | FA L22 | ok | ok |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | FA L17 | ok | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L8 | ok | FA L11 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | FA L13 | ok | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | FA L2 | FA L14 | FA L10 |
| `CV2-D-L-MEDICO-001` | legítima | — | — | FA L19 | ok | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L20 | ok | ok |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | FA L13 | ok | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | FA L23 | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | FA L8 | ok | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | FA L3 | ok | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | FA L7 | ok | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | FA L15 | ok | ok |
| `CV2-D-L-PREMIO-003` | legítima | — | — | FA L18 | ok | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | FA L6 | ok | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | FA L8 | ok | ok |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | FA L2 | ok | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | FA L1 | ok | ok |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | FA L1 | ok | ok |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | FA L3 | ok | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L3 | ok | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok | ok | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | FA L24 | ok | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | FA L9 | ok | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | FA L3 | ok | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 | <R L29 | <R L29 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L5 | <R L10 | =R L18 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L1 | <R L14 | — |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 | <R L8 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 | <R L5 | <R L11 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | =R L14 | <R L10 | =R L14 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 | <R L6 | =R L17 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L5 | <R L14 | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L1 | =R L13 | >R L14 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 | <R L7 | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 | L17 | — |
| `CV2-D-V-BANCO-012` | vishing | — | — | L4 | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | <R L3 | >R L16 | >R L16 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 | =R L16 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L4 | >R L17 | — |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | <R L14 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | <R L8 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L3 | =R L12 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L7 | =R L9 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L12 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | >R L16 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 | =R L10 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L10 | =R L13 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L10 | >R L15 | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L12 | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L13 | — | — |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L11 | <R L7 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 | <R L10 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L2 | =R L14 | >R L17 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L4 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L11 | <R L14 | <R L14 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L4 | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L8 | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 | =R L9 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 | =R L10 | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 | =R L12 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L10 | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 | <R L13 | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L14 | =R L25 | =R L25 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L10 | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok | FA L1 | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | FA L3 | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 | =R L3 | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok | FA L3 | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | =R L5 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 | <R L3 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok | ok | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 | <R L3 | <R L4 |
| `LAB-banco-revisa-app` | legítima | — | — | ok | FA L3 | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — | <R L3 | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | ok | ok | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 | =R L4 | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | — | =R L3 | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok | FA L1 | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — | =R L3 | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | FA L1 | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | =R L3 | <R L2 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 | FA L2 | FA L6 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 | ok | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 | FA L4 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | FA L9 | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L2 | FA L4 | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L4 | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 | FA L1 | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 | <R L2 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 | =R L9 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 | =R L7 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | — | =R L8 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 | =R L6 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | <R L3 | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | <R L3 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — | <R L5 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | FA L3 | ok | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L2 | FA L5 | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L6 | — | ≥C L27 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L5 | FA L14 | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 | FA L10 | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 | <R L6 | =R L7 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | =R L5 | <R L3 | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 | <R L4 | <R L6 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | FA L4 | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok | FA L5 | FA L5 |

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
- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 12: «Te están pidiendo que confirmes el nombre que figura como titular para cargar un desconocimiento.» — evidencia (cita textual): «12. entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 7: «Te están pidiendo los últimos cuatro dígitos de tu cuenta bancaria.» — evidencia (cita textual): «A: Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo los últimos cuatro números de una cuenta para ubicarla.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 14: «Te están pidiendo que transfieras dinero para completar un pago.» — evidencia (cita NO textual): «8. B: Te la reenvío. ¿Podés transferir tu aporte esta semana? 10. B: Poné esos 15.000; yo pongo 19.000 y mamá completa los 4.000 que faltan.»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo datos personales bajo la promesa de un bono» — evidencia (cita textual): «A: me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están indicando que debes entrar a una página web para resolver un tema de deuda o embargo.» — evidencia (cita textual): «B: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que accedas a la aplicación del banco y uses tu huella para revisar movimientos» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación oficial.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo que descargues un programa y les muestres tu celular» — evidencia (cita textual): «A: me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 2: «Te están pidiendo cambiar una clave basándose en un aviso de ingreso sospechoso.» — evidencia (cita textual): «B: Hola, Lucía. Llamo al número que está atrás de mi tarjeta. Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `LG-ORG-TURNO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 4: «No compartas nunca datos personales como DNI o fotos de documentos por teléfono.» — evidencia (cita textual): «Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-SUPPORT-INFO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo que le des tu usuario y contraseña a un tercero.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 1: «No compartas ningún código que te llegue por SMS, especialmente si no lo solicitaste.» — evidencia (cita textual): «A: Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `TR-03-negacion-y-consejo` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 5: «Te están presionando para que realices una transferencia bajo amenaza de bloqueo de cuenta.» — evidencia (cita textual): «A: ¿Y si me dicen que tengo que transferir para que no me bloqueen la cuenta?»
- `TR-05-asado-con-transferencia` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 14: «Te están pidiendo un alias para realizar una transferencia de dinero» — evidencia (cita textual): «14. B: Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo que compartas un código que te llegó por mensaje para verificar algo.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código que podría ser un código de verificación o de activación.» — evidencia (cita textual): «3. A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo realizar una transferencia de dinero.» — evidencia (cita textual): «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento, datos personales sensibles.» — evidencia (cita textual): «5. Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»
- `CV2-D-L-BANCO-002` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 7: «Te están pidiendo los últimos cuatro dígitos de tu cuenta para identificarla.» — evidencia (cita textual): «Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 8: «No compartas los últimos cuatro dígitos de tu cuenta, ya que te los están pidiendo para encontrarla.» — evidencia (cita textual): «B: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-010` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «No le des los últimos cuatro números de tu cuenta bancaria a nadie por teléfono.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-FAMILIAR-002` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 11: «Te están pidiendo un alias por mensaje, lo cual puede ser una forma de intentar acceder a alguna cuenta o perfil.» — evidencia (cita textual): «Pasame el alias por mensaje así no lo tengo que copiar de memoria.»
- `CV2-D-L-FAMILIAR-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo que transfieras dinero.» — evidencia (cita textual): «Poné esos 15.000; yo pongo 19.000 y mamá completa los 4.000 que faltan.»
- `LAB-banco-revisa-app` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación oficial, lo cual es una táctica común en estafas.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-no-bajes-nada` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo que bajes un programa y muestres tu celular, lo cual es una táctica común para obtener acceso a tu dispositivo.» — evidencia (cita textual): «1. A: me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 6: «No compartas nunca los números de tu tarjeta por teléfono, incluso si te piden que los des.» — evidencia (cita textual): «Dale. ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `TR-06-banco-alerta-legitima` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 10: «Te están pidiendo que compartas un código que te llegó por mensaje para verificar algo.» — evidencia (cita textual): «10. Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código que podrían usar para acceder a algo.» — evidencia (cita textual): «A: Pasame el código»
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
- `CV2-D-V-BANCO-012` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-004` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-004` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-WHATSAPP-007` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `TR-04-pedido-tras-charla-larga` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.20
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-BANCO-003` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-BANCO-011` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.70
- `CV2-D-V-BANCO-012` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.40
- `CV2-D-V-FAMILIAR-003` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `CV2-D-V-FAMILIAR-004` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab` · riesgo máximo 0.50
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
| `gemma4:e2b-it-q4_K_M` | 181.140 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 2 ms; encoder: 27.173 ms (carga fresca); calentamiento Tito: 156 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|gemma4:e2b-it-q4_K_M|tarea|ab`

Consultas al SLM hasta el aviso: 1189; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 692.488 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | sin aviso | 22 | 0 | 0 | 10.759 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.912 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.987 |
| `CV2-D-L-BANCO-004` | 5 | sin aviso | 20 | 4 | 0 | 9.047 |
| `CV2-D-L-BANCO-005` | 8 | L8 | 1 | 7 | 0 | 1.821 |
| `CV2-D-L-BANCO-006` | 6 | sin aviso | 19 | 5 | 0 | 9.176 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.397 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.262 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.315 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 2.081 |
| `CV2-D-L-DELIVERY-001` | 6 | sin aviso | 19 | 5 | 0 | 9.008 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 2.545 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 10.744 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 2.667 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 2.632 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 2.376 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 11.007 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 2.519 |
| `CV2-D-L-ESCUELA-004` | 7 | sin aviso | 20 | 6 | 0 | 9.594 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 11.633 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 2.924 |
| `CV2-D-L-FAMILIAR-002` | 11 | L11 | 1 | 10 | 0 | 2.639 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 4.787 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 5.151 |
| `CV2-D-L-FAMILIAR-005` | 10 | L10 | 1 | 9 | 0 | 2.028 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 2.913 |
| `CV2-D-L-MEDICO-002` | 7 | sin aviso | 20 | 6 | 0 | 9.199 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.759 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.670 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 8.939 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | sin aviso | 19 | 5 | 0 | 8.756 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 2.982 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 7.866 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.483 |
| `CV2-D-L-PREMIO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.984 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.543 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 2.650 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 8.815 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 9.281 |
| `CV2-D-L-SOPORTE-004` | 1 | sin aviso | 24 | 0 | 0 | 11.158 |
| `CV2-D-L-SOPORTE-005` | 10 | sin aviso | 15 | 9 | 0 | 7.398 |
| `CV2-D-L-TRABAJO-001` | 2 | sin aviso | 22 | 1 | 0 | 10.253 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.221 |
| `CV2-D-L-TRABAJO-003` | 10 | sin aviso | 16 | 9 | 0 | 8.176 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.587 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 12.408 |
| `CV2-D-L-WHATSAPP-001` | 16 | sin aviso | 8 | 15 | 0 | 5.037 |
| `CV2-D-L-WHATSAPP-002` | 10 | sin aviso | 14 | 9 | 0 | 7.194 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 7.622 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 8.547 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 10.252 |
| `CV2-D-V-BANCO-001` | 29 | L29 | 1 | 28 | 0 | 3.978 |
| `CV2-D-V-BANCO-002` | 6 | L18 | 13 | 5 | 0 | 6.914 |
| `CV2-D-V-BANCO-003` | 5 | sin aviso | 22 | 4 | 0 | 9.533 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 2.047 |
| `CV2-D-V-BANCO-005` | 1 | L11 | 11 | 0 | 0 | 5.824 |
| `CV2-D-V-BANCO-006` | 2 | L14 | 13 | 1 | 0 | 6.068 |
| `CV2-D-V-BANCO-007` | 11 | L17 | 7 | 10 | 0 | 4.595 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 2.933 |
| `CV2-D-V-BANCO-009` | 3 | L14 | 12 | 2 | 0 | 6.056 |
| `CV2-D-V-BANCO-010` | 1 | L1 | 1 | 0 | 0 | 870 |
| `CV2-D-V-BANCO-011` | 12 | sin aviso | 10 | 11 | 0 | 5.234 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 9.668 |
| `CV2-D-V-FAMILIAR-001` | 5 | L16 | 12 | 4 | 0 | 5.688 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 2.482 |
| `CV2-D-V-FAMILIAR-003` | 14 | sin aviso | 7 | 13 | 0 | 4.858 |
| `CV2-D-V-FAMILIAR-004` | 14 | sin aviso | 16 | 13 | 0 | 8.186 |
| `CV2-D-V-FAMILIAR-005` | 18 | sin aviso | 4 | 17 | 0 | 3.601 |
| `CV2-D-V-FAMILIAR-006` | 17 | sin aviso | 7 | 16 | 0 | 5.031 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L12 | 11 | 1 | 0 | 5.560 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L9 | 9 | 0 | 0 | 4.423 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | sin aviso | 8 | 12 | 0 | 4.763 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | sin aviso | 20 | 1 | 0 | 9.026 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 9.679 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 9.548 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.061 |
| `CV2-D-V-PREMIO-002` | 3 | sin aviso | 18 | 2 | 0 | 8.582 |
| `CV2-D-V-PREMIO-003` | 3 | sin aviso | 26 | 2 | 0 | 11.135 |
| `CV2-D-V-PREMIO-004` | 12 | L14 | 3 | 11 | 0 | 3.236 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 8.729 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 10.119 |
| `CV2-D-V-SOPORTE-001` | 12 | sin aviso | 10 | 11 | 0 | 5.542 |
| `CV2-D-V-SOPORTE-002` | 1 | L7 | 7 | 0 | 0 | 3.369 |
| `CV2-D-V-SOPORTE-003` | 1 | L10 | 10 | 0 | 0 | 4.799 |
| `CV2-D-V-SOPORTE-004` | 13 | L17 | 5 | 12 | 0 | 4.554 |
| `CV2-D-V-SOPORTE-005` | 10 | sin aviso | 12 | 9 | 0 | 5.983 |
| `CV2-D-V-SOPORTE-006` | 1 | L14 | 14 | 0 | 0 | 6.612 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 4.166 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 3.982 |
| `CV2-D-V-WHATSAPP-001` | 1 | L9 | 9 | 0 | 0 | 4.216 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 1.968 |
| `CV2-D-V-WHATSAPP-003` | 8 | L12 | 5 | 7 | 0 | 3.710 |
| `CV2-D-V-WHATSAPP-004` | 5 | sin aviso | 17 | 4 | 0 | 7.903 |
| `CV2-D-V-WHATSAPP-005` | 10 | L13 | 4 | 9 | 0 | 2.924 |
| `CV2-D-V-WHATSAPP-006` | 22 | L25 | 4 | 21 | 0 | 4.711 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 7.035 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 5.770 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 2.001 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.048 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 1.947 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.192 |
| `LAB-anses-canal-oficial` | 5 | sin aviso | 1 | 4 | 0 | 1.032 |
| `LAB-arca-canal-oficial` | 1 | sin aviso | 5 | 0 | 0 | 2.461 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 1.938 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.103 |
| `LAB-banco-app-parafrasis` | 1 | sin aviso | 5 | 0 | 0 | 2.515 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 1.795 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.150 |
| `LAB-banco-gasto-sin-pedido` | 1 | sin aviso | 3 | 0 | 0 | 1.706 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 745 |
| `LAB-banco-numeros-sin-clave` | 1 | L4 | 4 | 0 | 0 | 2.597 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 1.234 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 2.003 |
| `LAB-familiar-llama-vos` | 2 | sin aviso | 4 | 1 | 0 | 2.066 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 2.320 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 2.361 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 1.947 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 2.884 |
| `LAB-no-bajes-nada` | 4 | L4 | 1 | 3 | 0 | 1.380 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 1.830 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 729 |
| `LAB-whatsapp-codigo` | 1 | L1 | 1 | 0 | 0 | 850 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.820 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 1.686 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.042 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.607 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 3.465 |
| `LG-SUPPORT-INFO-01-e01` | 7 | sin aviso | 7 | 6 | 0 | 4.145 |
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 3.355 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 401 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L2 | 1 | 1 | 0 | 1.064 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 1.836 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 2.865 |
| `SC-PREMIO-01-e01` | 3 | L8 | 6 | 2 | 0 | 3.518 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 2.613 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.896 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.997 |
| `TR-01-pedido-indirecto-digitos` | 3 | sin aviso | 10 | 2 | 0 | 4.488 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 3.471 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.326 |
| `TR-04-pedido-tras-charla-larga` | 5 | L27 | 23 | 4 | 0 | 11.041 |
| `TR-05-asado-con-transferencia` | 14 | sin aviso | 14 | 13 | 0 | 8.108 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 4.195 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L7 | 3 | 4 | 0 | 2.089 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 917 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.474 |
| `TR-10-ofrecimiento-inducido` | 4 | L6 | 3 | 3 | 0 | 2.182 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 2.041 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 3.157 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.482 |

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
| `reglas` | 15.009 | — | — | 0 | 1319 | 0/1319 |
| `slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` | 1.009.706 | 0 | 1.009.706 | 1.5658e+06 | 2214 | 2214/0 |
| `tito-slm\|gemma4:e2b-it-q4_K_M\|tarea\|ab` | 692.488 | 140.605 | 551.882 | 987477 | 2328 | 1189/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
