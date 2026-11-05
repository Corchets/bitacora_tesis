# Resumen de la corrida `2026-11-04_233513_tanda-roles-a-tarea-rol`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --filtro-tito --tito-real --sin-indicio --prompts tarea --hablantes rol --etiqueta tanda-roles-a-tarea-rol --salida /content/resultados-tanda-roles/a`
- **Inicio / fin:** 2026-11-04T23:35:13 / 2026-11-04T23:49:26
- **Código:** `7db9cc38a7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|tarea\|rol` | 53/75 | 21 | 29 | 2 | 0 | 12/75 | 0/2320 | 344 | 665 | 62/65 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|tarea\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L12 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | ok |
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
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L11 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | =R L14 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L15 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L17 |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | >R L16 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L14 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | >R L15 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | — |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | — |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | =R L25 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L3 |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L3 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L2 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L4 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L14 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | =R L7 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L6 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 12: «Te están pidiendo que confirmes el nombre que figura como titular para cargar un desconocimiento.» — evidencia (cita textual): «12. entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 7: «Te están pidiendo los últimos cuatro dígitos de tu cuenta bancaria.» — evidencia (cita NO textual): «TRA: Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-010` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 10: «Te están pidiendo los últimos cuatro números de una cuenta para ubicar un comprobante de transferencia» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `LAB-arca-canal-oficial` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 3: «Te están indicando que debes ingresar a una página web para resolver un problema de deuda.» — evidencia (cita textual): «OTRA: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-app-parafrasis` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 3: «Te están pidiendo que ingreses tu huella para revisar movimientos bancarios» — evidencia (cita textual): «OTRA: entra con tu huella y revisa los movimientos»
- `LAB-banco-revisa-app` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación para verificar un consumo en tu tarjeta.» — evidencia (cita textual): «OTRA: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-no-bajes-nada` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 4: «Te están pidiendo que descargues un programa y les muestres tu celular, lo cual es una táctica común para obtener acceso remoto.» — evidencia (cita textual): «PROTEGIDA: me llamaron para que baje un programa y les muestre el celular»
- `TR-05-asado-con-transferencia` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 14: «Te están pidiendo un alias para realizar una transferencia de dinero» — evidencia (cita textual): «Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.»
- `TR-06-banco-alerta-legitima` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 10: «Te están pidiendo que le des un código que te llegó por mensaje para verificar algo.» — evidencia (cita textual): «10. PROTEGIDA: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 3: «Te están pidiendo un código que probablemente es un código de verificación o de acceso.» — evidencia (cita textual): «OTRA: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 9: «Te están pidiendo realizar una transferencia de dinero.» — evidencia (cita textual): «OTRA: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento.» — evidencia (cita textual): «OTRA: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-BANCO-012` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · sin riesgo registrado
- `CV2-D-V-PREMIO-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.40
- `CV2-D-V-SOPORTE-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 178.248 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Sin indicio (`--sin-indicio`): Tito solo decide cuándo consultar; el SLM recibe el mismo mensaje que el SLM solo, sin bloque de indicio ni de fallo técnico.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 2 ms; encoder: 27.050 ms (carga fresca); calentamiento Tito: 155 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|tarea|rol`

Consultas al SLM hasta el aviso: 1181; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 673.529 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | L12 | 12 | 0 | 0 | 6.562 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.912 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.870 |
| `CV2-D-L-BANCO-004` | 5 | sin aviso | 20 | 4 | 0 | 7.760 |
| `CV2-D-L-BANCO-005` | 8 | sin aviso | 17 | 7 | 0 | 7.692 |
| `CV2-D-L-BANCO-006` | 6 | sin aviso | 19 | 5 | 0 | 7.492 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.939 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.971 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.416 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 2.021 |
| `CV2-D-L-DELIVERY-001` | 6 | sin aviso | 19 | 5 | 0 | 7.690 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 3.208 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 9.264 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 2.808 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 3.169 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 3.119 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 9.244 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 2.792 |
| `CV2-D-L-ESCUELA-004` | 7 | sin aviso | 20 | 6 | 0 | 8.678 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 10.938 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 2.617 |
| `CV2-D-L-FAMILIAR-002` | 11 | sin aviso | 10 | 10 | 0 | 5.424 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 4.682 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 5.665 |
| `CV2-D-L-FAMILIAR-005` | 10 | sin aviso | 14 | 9 | 0 | 6.528 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 2.977 |
| `CV2-D-L-MEDICO-002` | 7 | sin aviso | 20 | 6 | 0 | 8.874 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.813 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.692 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 8.450 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | sin aviso | 19 | 5 | 0 | 8.094 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 3.098 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 7.519 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.464 |
| `CV2-D-L-PREMIO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.583 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.639 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 2.753 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 8.868 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 8.553 |
| `CV2-D-L-SOPORTE-004` | 1 | sin aviso | 24 | 0 | 0 | 10.753 |
| `CV2-D-L-SOPORTE-005` | 10 | sin aviso | 15 | 9 | 0 | 7.355 |
| `CV2-D-L-TRABAJO-001` | 2 | sin aviso | 22 | 1 | 0 | 9.773 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.549 |
| `CV2-D-L-TRABAJO-003` | 10 | sin aviso | 16 | 9 | 0 | 7.922 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.724 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 11.646 |
| `CV2-D-L-WHATSAPP-001` | 16 | sin aviso | 8 | 15 | 0 | 5.487 |
| `CV2-D-L-WHATSAPP-002` | 10 | sin aviso | 14 | 9 | 0 | 7.483 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 6.941 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 8.972 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 9.964 |
| `CV2-D-V-BANCO-001` | 29 | L32 | 4 | 28 | 0 | 6.612 |
| `CV2-D-V-BANCO-002` | 6 | L17 | 12 | 5 | 0 | 5.710 |
| `CV2-D-V-BANCO-003` | 5 | L14 | 10 | 4 | 0 | 4.977 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 2.188 |
| `CV2-D-V-BANCO-005` | 1 | L11 | 11 | 0 | 0 | 5.547 |
| `CV2-D-V-BANCO-006` | 2 | L14 | 13 | 1 | 0 | 5.952 |
| `CV2-D-V-BANCO-007` | 11 | L15 | 5 | 10 | 0 | 3.937 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 3.179 |
| `CV2-D-V-BANCO-009` | 3 | L13 | 11 | 2 | 0 | 5.228 |
| `CV2-D-V-BANCO-010` | 1 | L1 | 1 | 0 | 0 | 945 |
| `CV2-D-V-BANCO-011` | 12 | L17 | 6 | 11 | 0 | 4.071 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 9.228 |
| `CV2-D-V-FAMILIAR-001` | 5 | L16 | 12 | 4 | 0 | 5.779 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 2.963 |
| `CV2-D-V-FAMILIAR-003` | 14 | L14 | 1 | 13 | 0 | 2.876 |
| `CV2-D-V-FAMILIAR-004` | 14 | sin aviso | 16 | 13 | 0 | 8.039 |
| `CV2-D-V-FAMILIAR-005` | 18 | sin aviso | 4 | 17 | 0 | 3.667 |
| `CV2-D-V-FAMILIAR-006` | 17 | sin aviso | 7 | 16 | 0 | 5.278 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L12 | 11 | 1 | 0 | 5.216 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L9 | 9 | 0 | 0 | 4.258 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | sin aviso | 8 | 12 | 0 | 5.093 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | sin aviso | 20 | 1 | 0 | 8.457 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 9.664 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 8.997 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.354 |
| `CV2-D-V-PREMIO-002` | 3 | L13 | 11 | 2 | 0 | 5.675 |
| `CV2-D-V-PREMIO-003` | 3 | sin aviso | 26 | 2 | 0 | 11.078 |
| `CV2-D-V-PREMIO-004` | 12 | L15 | 4 | 11 | 0 | 3.940 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 8.258 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 9.789 |
| `CV2-D-V-SOPORTE-001` | 12 | sin aviso | 10 | 11 | 0 | 5.306 |
| `CV2-D-V-SOPORTE-002` | 1 | L7 | 7 | 0 | 0 | 3.628 |
| `CV2-D-V-SOPORTE-003` | 1 | sin aviso | 21 | 0 | 0 | 9.194 |
| `CV2-D-V-SOPORTE-004` | 13 | L14 | 2 | 12 | 0 | 2.891 |
| `CV2-D-V-SOPORTE-005` | 10 | sin aviso | 12 | 9 | 0 | 6.041 |
| `CV2-D-V-SOPORTE-006` | 1 | sin aviso | 20 | 0 | 0 | 8.812 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 3.532 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 4.260 |
| `CV2-D-V-WHATSAPP-001` | 1 | L9 | 9 | 0 | 0 | 4.502 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 1.817 |
| `CV2-D-V-WHATSAPP-003` | 8 | L8 | 1 | 7 | 0 | 1.493 |
| `CV2-D-V-WHATSAPP-004` | 5 | sin aviso | 17 | 4 | 0 | 7.393 |
| `CV2-D-V-WHATSAPP-005` | 10 | L13 | 4 | 9 | 0 | 3.462 |
| `CV2-D-V-WHATSAPP-006` | 22 | L25 | 4 | 21 | 0 | 4.715 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 6.366 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 6.187 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 1.808 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.864 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 1.890 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.928 |
| `LAB-anses-canal-oficial` | 5 | sin aviso | 1 | 4 | 0 | 910 |
| `LAB-arca-canal-oficial` | 1 | L3 | 3 | 0 | 0 | 1.927 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 1.929 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.321 |
| `LAB-banco-app-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.833 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 1.779 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.712 |
| `LAB-banco-gasto-sin-pedido` | 1 | sin aviso | 3 | 0 | 0 | 1.484 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 645 |
| `LAB-banco-numeros-sin-clave` | 1 | L3 | 3 | 0 | 0 | 1.820 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 1.170 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 1.987 |
| `LAB-familiar-llama-vos` | 2 | sin aviso | 4 | 1 | 0 | 2.273 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 2.493 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 2.253 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 1.786 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 2.460 |
| `LAB-no-bajes-nada` | 4 | L4 | 1 | 3 | 0 | 1.325 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 1.856 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 805 |
| `LAB-whatsapp-codigo` | 1 | L2 | 2 | 0 | 0 | 1.590 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.029 |
| `LG-BANK-VERIF-01-e01` | 6 | sin aviso | 7 | 5 | 0 | 3.585 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.138 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.474 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 3.056 |
| `LG-SUPPORT-INFO-01-e01` | 7 | sin aviso | 7 | 6 | 0 | 4.198 |
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 3.777 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 423 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L4 | 3 | 1 | 0 | 2.020 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 1.925 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 2.757 |
| `SC-PREMIO-01-e01` | 3 | L8 | 6 | 2 | 0 | 3.459 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 2.727 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.973 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.753 |
| `TR-01-pedido-indirecto-digitos` | 3 | L5 | 3 | 2 | 0 | 2.319 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 3.214 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.148 |
| `TR-04-pedido-tras-charla-larga` | 5 | L26 | 22 | 4 | 0 | 10.426 |
| `TR-05-asado-con-transferencia` | 14 | L14 | 1 | 13 | 0 | 2.384 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 4.212 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L7 | 3 | 4 | 0 | 2.356 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 1.117 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.564 |
| `TR-10-ofrecimiento-inducido` | 4 | L6 | 3 | 3 | 0 | 1.967 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 1.757 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 2.670 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.294 |

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
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|tarea\|rol` | 673.529 | 147.229 | 526.301 | 896701 | 2320 | 1181/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
