# Resumen de la corrida `2026-11-05_142148_prompt-v5-b-v5-rol`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --filtro-tito --tito-real --sin-indicio --prompts v5 --hablantes rol --seguir-tras-aviso --etiqueta prompt-v5-b-v5-rol --salida /content/resultados-prompt-v5/b`
- **Inicio / fin:** 2026-11-05T14:21:48 / 2026-11-05T14:39:51
- **Código:** `26e1b173a4`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v5\|rol` | 57/75 | 26 | 24 | 5 | 0 | 13/75 | 0/2773 | 381 | 1.018 | 69/70 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v5\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L12 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-005` | legítima | — | — | ok |
| `CV2-D-L-BANCO-006` | legítima | — | — | ok |
| `CV2-D-L-BANCO-007` | legítima | — | — | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | ok |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L10 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-001` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | =R L32 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L17 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L13 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L12 |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L14 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | >R L21 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | >R L15 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L14 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | >R L13 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L2 |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L1 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L2 |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | <R L1 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | <R L1 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L6 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L6 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 |
| `TR-05-asado-con-transferencia` | legítima | — | — | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L6 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L6 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L7 |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 12: «OTRA te pide confirmar el nombre que figura como titular para cargar un desconocimiento, lo cual es una solicitud de información personal.» — evidencia (cita textual): «entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 7: «OTRA está pidiendo los últimos cuatro dígitos de la cuenta, lo cual es información sensible.» — evidencia (cita textual): «Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 8: «OTRA pide los últimos cuatro dígitos de la cuenta donde espera recibir dinero, lo cual es un dato sensible.» — evidencia (cita textual): «Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»
- `CV2-D-L-BANCO-010` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 10: «OTRA pide los últimos cuatro números de la cuenta bancaria para ubicar un comprobante, lo cual es una solicitud de datos sensibles.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `LAB-arca-canal-oficial` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 2: «La instrucción de no abrir un mensaje de deuda o embargo es una táctica común para generar pánico e inducir a la víctima a seguir instrucciones no verificadas.» — evidencia (cita textual): «OTRA: no abras ningun sitio del mensaje»
- `LAB-banco-app-parafrasis` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 1: «OTRA te está pidiendo que cortes la llamada y te fijes en la aplicación del banco, lo cual es una táctica común para redirigir la acción a un entorno controlado por el estafador.» — evidencia (cita textual): «OTRA: corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 2: «La instrucción de 'no hagas nada por teléfono' es una táctica común para evitar que la persona verifique la situación o tome medidas de seguridad.» — evidencia (cita textual): «OTRA: no hagas nada por telefono»
- `LAB-banco-revisa-app` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 3: «OTRA te pide cortar la comunicación y entrar a la aplicación oficial, lo cual es una táctica común para desviar la atención de una posible estafa.» — evidencia (cita textual): «OTRA: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LG-BANK-VERIF-01-e01` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 6: «No proporciones los últimos números de tu tarjeta a nadie, incluso si te piden que lo hagas para identificarte.» — evidencia (cita textual): «PROTEGIDA: ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `TR-06-banco-alerta-legitima` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 10: «OTRA te pide que le pases un código que te llegó para verificar algo, lo cual es una táctica común de vishing.» — evidencia (cita textual): «Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 3: «No le pidas un código de verificación, token o cualquier dato de acceso.» — evidencia (cita textual): «OTRA: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 9: «OTRA te pide transferir dinero bajo la excusa de un problema con la boleta y te presiona para que hagas la transferencia sin verificar.» — evidencia (cita textual): «OTRA: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · línea 5: «OTRA te pide directamente tu número de documento y fecha de nacimiento, datos personales sensibles.» — evidencia (cita textual): «OTRA: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-BANCO-012` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.40
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · sin riesgo registrado
- `CV2-D-V-PREMIO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol` · riesgo máximo 0.30

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 17.020 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Sin indicio (`--sin-indicio`): Tito solo decide cuándo consultar; el SLM recibe el mismo mensaje que el SLM solo, sin bloque de indicio ni de fallo técnico.
Modo de término: `diagnostico-completo`: cada llamada recorre la conversación completa aunque haya aviso; los costos de esta sección son el prefijo hasta el aviso (o el caso completo si nunca avisó), separados del costo de la conversación completa.
Arranque Tito (artefacto): 1 ms; encoder: 16.340 ms (carga fresca); calentamiento Tito: 102 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v5|rol`

Consultas al SLM hasta el aviso: 1130; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 653.419 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | L12 | 12 | 0 | 0 | 5.453 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.883 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.563 |
| `CV2-D-L-BANCO-004` | 5 | L8 | 4 | 4 | 0 | 2.824 |
| `CV2-D-L-BANCO-005` | 8 | sin aviso | 17 | 7 | 0 | 8.006 |
| `CV2-D-L-BANCO-006` | 6 | sin aviso | 19 | 5 | 0 | 8.821 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.512 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.411 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.769 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 2.421 |
| `CV2-D-L-DELIVERY-001` | 6 | sin aviso | 19 | 5 | 0 | 8.605 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 3.407 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 9.666 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 3.011 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 3.360 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 3.096 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 9.909 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 3.022 |
| `CV2-D-L-ESCUELA-004` | 7 | sin aviso | 20 | 6 | 0 | 9.124 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 11.385 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 2.680 |
| `CV2-D-L-FAMILIAR-002` | 11 | sin aviso | 10 | 10 | 0 | 5.444 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 5.254 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 5.720 |
| `CV2-D-L-FAMILIAR-005` | 10 | sin aviso | 14 | 9 | 0 | 6.646 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 3.182 |
| `CV2-D-L-MEDICO-002` | 7 | sin aviso | 20 | 6 | 0 | 9.239 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.904 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 3.010 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 8.569 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | sin aviso | 19 | 5 | 0 | 8.388 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 3.268 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 7.474 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.690 |
| `CV2-D-L-PREMIO-002` | 5 | sin aviso | 21 | 4 | 0 | 10.002 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.706 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 2.834 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 8.988 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 8.673 |
| `CV2-D-L-SOPORTE-004` | 1 | sin aviso | 24 | 0 | 0 | 10.822 |
| `CV2-D-L-SOPORTE-005` | 10 | sin aviso | 15 | 9 | 0 | 7.647 |
| `CV2-D-L-TRABAJO-001` | 2 | sin aviso | 22 | 1 | 0 | 9.877 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.642 |
| `CV2-D-L-TRABAJO-003` | 10 | sin aviso | 16 | 9 | 0 | 8.091 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.719 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 11.660 |
| `CV2-D-L-WHATSAPP-001` | 16 | sin aviso | 8 | 15 | 0 | 5.319 |
| `CV2-D-L-WHATSAPP-002` | 10 | sin aviso | 14 | 9 | 0 | 7.627 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 7.154 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 8.800 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 9.643 |
| `CV2-D-V-BANCO-001` | 29 | L32 | 4 | 28 | 0 | 6.150 |
| `CV2-D-V-BANCO-002` | 6 | L17 | 12 | 5 | 0 | 5.812 |
| `CV2-D-V-BANCO-003` | 5 | L14 | 10 | 4 | 0 | 4.889 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 1.975 |
| `CV2-D-V-BANCO-005` | 1 | L1 | 1 | 0 | 0 | 940 |
| `CV2-D-V-BANCO-006` | 2 | L10 | 9 | 1 | 0 | 4.184 |
| `CV2-D-V-BANCO-007` | 11 | L13 | 3 | 10 | 0 | 3.708 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 2.956 |
| `CV2-D-V-BANCO-009` | 3 | L13 | 11 | 2 | 0 | 5.022 |
| `CV2-D-V-BANCO-010` | 1 | L1 | 1 | 0 | 0 | 933 |
| `CV2-D-V-BANCO-011` | 12 | L12 | 1 | 11 | 0 | 2.262 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 8.169 |
| `CV2-D-V-FAMILIAR-001` | 5 | L15 | 11 | 4 | 0 | 6.055 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 2.549 |
| `CV2-D-V-FAMILIAR-003` | 14 | L14 | 1 | 13 | 0 | 2.431 |
| `CV2-D-V-FAMILIAR-004` | 14 | sin aviso | 16 | 13 | 0 | 8.268 |
| `CV2-D-V-FAMILIAR-005` | 18 | sin aviso | 4 | 17 | 0 | 3.546 |
| `CV2-D-V-FAMILIAR-006` | 17 | sin aviso | 7 | 16 | 0 | 4.887 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L12 | 11 | 1 | 0 | 5.365 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L9 | 9 | 0 | 0 | 3.871 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | L13 | 1 | 12 | 0 | 2.603 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | sin aviso | 20 | 1 | 0 | 8.558 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 8.808 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 9.085 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.116 |
| `CV2-D-V-PREMIO-002` | 3 | sin aviso | 18 | 2 | 0 | 8.191 |
| `CV2-D-V-PREMIO-003` | 3 | sin aviso | 26 | 2 | 0 | 10.730 |
| `CV2-D-V-PREMIO-004` | 12 | L14 | 3 | 11 | 0 | 3.129 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 7.873 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 9.524 |
| `CV2-D-V-SOPORTE-001` | 12 | L21 | 10 | 11 | 0 | 5.977 |
| `CV2-D-V-SOPORTE-002` | 1 | L13 | 13 | 0 | 0 | 5.755 |
| `CV2-D-V-SOPORTE-003` | 1 | L15 | 15 | 0 | 0 | 6.608 |
| `CV2-D-V-SOPORTE-004` | 13 | L14 | 2 | 12 | 0 | 2.924 |
| `CV2-D-V-SOPORTE-005` | 10 | sin aviso | 12 | 9 | 0 | 5.665 |
| `CV2-D-V-SOPORTE-006` | 1 | L14 | 14 | 0 | 0 | 6.458 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 3.506 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 3.788 |
| `CV2-D-V-WHATSAPP-001` | 1 | L9 | 9 | 0 | 0 | 4.623 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 2.149 |
| `CV2-D-V-WHATSAPP-003` | 8 | L13 | 6 | 7 | 0 | 3.549 |
| `CV2-D-V-WHATSAPP-004` | 5 | sin aviso | 17 | 4 | 0 | 7.965 |
| `CV2-D-V-WHATSAPP-005` | 10 | L13 | 4 | 9 | 0 | 3.320 |
| `CV2-D-V-WHATSAPP-006` | 22 | L26 | 5 | 21 | 0 | 5.586 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 6.479 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 6.057 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 1.655 |
| `LAB-acceso-remoto-parafrasis` | 1 | L1 | 1 | 0 | 0 | 870 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 1.826 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.856 |
| `LAB-anses-canal-oficial` | 5 | sin aviso | 1 | 4 | 0 | 834 |
| `LAB-arca-canal-oficial` | 1 | L2 | 2 | 0 | 0 | 1.288 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 1.619 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.149 |
| `LAB-banco-app-parafrasis` | 1 | L1 | 1 | 0 | 0 | 1.251 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 1.837 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.564 |
| `LAB-banco-gasto-sin-pedido` | 1 | L2 | 2 | 0 | 0 | 1.271 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 666 |
| `LAB-banco-numeros-sin-clave` | 1 | L3 | 3 | 0 | 0 | 1.845 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 1.112 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 1.622 |
| `LAB-familiar-llama-vos` | 2 | sin aviso | 4 | 1 | 0 | 1.632 |
| `LAB-familiar-peligro` | 1 | L1 | 1 | 0 | 0 | 822 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 2.169 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 1.558 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 1.962 |
| `LAB-no-bajes-nada` | 4 | sin aviso | 1 | 3 | 0 | 705 |
| `LAB-pantalla-sin-programa` | 1 | L1 | 1 | 0 | 0 | 775 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 643 |
| `LAB-whatsapp-codigo` | 1 | L1 | 1 | 0 | 0 | 1.122 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.738 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 1.608 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.030 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.583 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 3.653 |
| `LG-SUPPORT-INFO-01-e01` | 7 | sin aviso | 7 | 6 | 0 | 4.009 |
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 3.247 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 420 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L2 | 1 | 1 | 0 | 1.171 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 1.892 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L6 | 4 | 2 | 0 | 2.465 |
| `SC-PREMIO-01-e01` | 3 | L8 | 6 | 2 | 0 | 3.168 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 2.308 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.870 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.901 |
| `TR-01-pedido-indirecto-digitos` | 3 | L5 | 3 | 2 | 0 | 2.024 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 3.106 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.317 |
| `TR-04-pedido-tras-charla-larga` | 5 | L26 | 22 | 4 | 0 | 10.161 |
| `TR-05-asado-con-transferencia` | 14 | sin aviso | 14 | 13 | 0 | 8.165 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 3.846 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L6 | 2 | 4 | 0 | 1.731 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 1.058 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.214 |
| `TR-10-ofrecimiento-inducido` | 4 | L6 | 3 | 3 | 0 | 2.244 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 2.053 |
| `TR-12-corta-antes-del-pedido` | 6 | L7 | 2 | 5 | 0 | 2.346 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.520 |

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

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v5\|rol` | 653.419 | 1.064.539 | 147.597 | 505.822 | 1.45991e+06 | 2269 | 1130/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
