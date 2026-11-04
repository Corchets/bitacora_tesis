# Resumen de la corrida `2026-11-04_215231_prompt-v4-a-v4-rol`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --filtro-tito --tito-real --sin-indicio --prompts v4 --hablantes rol --etiqueta prompt-v4-a-v4-rol --salida /content/resultados-prompt-v4/a`
- **Inicio / fin:** 2026-11-04T21:52:31 / 2026-11-04T22:06:21
- **Código:** `55fe977545`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v4\|rol` | 55/75 | 19 | 33 | 2 | 0 | 13/75 | 0/2271 | 178 | 579 | 68/68 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v4\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L12 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L15 |
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
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | =R L18 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L10 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L13 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L3 |
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
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L10 |
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
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L1 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L4 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 |
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
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L4 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L6 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 |
| `TR-05-asado-con-transferencia` | legítima | — | — | ok |
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

- `CV2-D-L-BANCO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 12: «No confirmes el nombre que figura como titular, ya que te están pidiendo un dato para confirmar un cargo.» — evidencia (cita textual): «entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 7: «No proporciones los últimos cuatro dígitos de tu cuenta bancaria a nadie por teléfono.» — evidencia (cita textual): «Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 8: «OTRA te pide los últimos cuatro dígitos de la cuenta para buscar ingresos pendientes, lo cual es un dato sensible.» — evidencia (cita textual): «Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»
- `CV2-D-L-BANCO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 8: «No proporciones los últimos cuatro dígitos de tu cuenta, ya que esto puede ser usado para acceder a tus datos bancarios.» — evidencia (cita textual): «Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 15: «OTRA está induciendo a PROTEGIDA a realizar una acción en el dispositivo (cerrar sesión) bajo la apariencia de resolver un problema de seguridad, lo cual puede ser un intento de tomar control de la cuenta.» — evidencia (cita textual): «Podés cerrar esa sesión desde el menú de seguridad cuando tengas la tablet a mano.»
- `CV2-D-L-BANCO-010` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 10: «OTRA le pide los últimos cuatro números de una cuenta bancaria para ubicar un comprobante de transferencia.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `LAB-banco-app-parafrasis` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 1: «No hagas clic en enlaces ni accedas a aplicaciones por instrucciones de un desconocido.» — evidencia (cita textual): «OTRA: corta aca y fijate vos en la app del banco»
- `LAB-banco-revisa-app` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 4: «No confíes en que te pidan que cortes la comunicación y entres a una aplicación oficial; siempre verifica por tu cuenta.» — evidencia (cita textual): «OTRA: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LG-BANK-VERIF-01-e01` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 6: «No proporciones los últimos números de tu tarjeta a nadie por teléfono.» — evidencia (cita textual): «PROTEGIDA: ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `TR-06-banco-alerta-legitima` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 10: «No le des ningún código que te llegó, ya que te lo están pidiendo para verificar algo.» — evidencia (cita textual): «Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 3: «No le des ningún código, no importa lo que te pidan, es una estafa.» — evidencia (cita textual): «OTRA: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 9: «No transfieras dinero a una cuenta, aunque se justifique por un problema de boleta, es una solicitud de transferencia de fondos.» — evidencia (cita textual): «Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · línea 5: «No debe proporcionar su número de documento y fecha de nacimiento a nadie por teléfono.» — evidencia (cita textual): «OTRA: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-BANCO-012` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.40
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · sin riesgo registrado
- `CV2-D-V-PREMIO-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol` · riesgo máximo 0.30

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 176.167 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Sin indicio (`--sin-indicio`): Tito solo decide cuándo consultar; el SLM recibe el mismo mensaje que el SLM solo, sin bloque de indicio ni de fallo técnico.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 2 ms; encoder: 35.841 ms (carga fresca); calentamiento Tito: 161 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v4|rol`

Consultas al SLM hasta el aviso: 1132; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 652.908 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | L12 | 12 | 0 | 0 | 7.114 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.625 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.687 |
| `CV2-D-L-BANCO-004` | 5 | L8 | 4 | 4 | 0 | 2.509 |
| `CV2-D-L-BANCO-005` | 8 | L8 | 1 | 7 | 0 | 1.643 |
| `CV2-D-L-BANCO-006` | 6 | L15 | 10 | 5 | 0 | 5.559 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.561 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.403 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.456 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 1.960 |
| `CV2-D-L-DELIVERY-001` | 6 | sin aviso | 19 | 5 | 0 | 8.245 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 2.762 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 9.823 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 2.663 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 2.786 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 2.636 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 9.934 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 2.696 |
| `CV2-D-L-ESCUELA-004` | 7 | sin aviso | 20 | 6 | 0 | 9.246 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 9.978 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 3.221 |
| `CV2-D-L-FAMILIAR-002` | 11 | sin aviso | 10 | 10 | 0 | 5.742 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 4.366 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 5.690 |
| `CV2-D-L-FAMILIAR-005` | 10 | sin aviso | 14 | 9 | 0 | 7.245 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 2.701 |
| `CV2-D-L-MEDICO-002` | 7 | sin aviso | 20 | 6 | 0 | 9.428 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.815 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.713 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 8.452 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | sin aviso | 19 | 5 | 0 | 8.532 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 2.626 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 8.074 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.697 |
| `CV2-D-L-PREMIO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.724 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 3.161 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 2.862 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 8.505 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 9.141 |
| `CV2-D-L-SOPORTE-004` | 1 | sin aviso | 24 | 0 | 0 | 10.596 |
| `CV2-D-L-SOPORTE-005` | 10 | sin aviso | 15 | 9 | 0 | 7.246 |
| `CV2-D-L-TRABAJO-001` | 2 | sin aviso | 22 | 1 | 0 | 9.807 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 8.664 |
| `CV2-D-L-TRABAJO-003` | 10 | sin aviso | 16 | 9 | 0 | 8.625 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.725 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 11.200 |
| `CV2-D-L-WHATSAPP-001` | 16 | sin aviso | 8 | 15 | 0 | 5.862 |
| `CV2-D-L-WHATSAPP-002` | 10 | sin aviso | 14 | 9 | 0 | 6.821 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 7.922 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 8.064 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 10.119 |
| `CV2-D-V-BANCO-001` | 29 | L32 | 4 | 28 | 0 | 5.807 |
| `CV2-D-V-BANCO-002` | 6 | L18 | 13 | 5 | 0 | 7.078 |
| `CV2-D-V-BANCO-003` | 5 | L14 | 10 | 4 | 0 | 4.992 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 1.988 |
| `CV2-D-V-BANCO-005` | 1 | L10 | 10 | 0 | 0 | 4.735 |
| `CV2-D-V-BANCO-006` | 2 | L10 | 9 | 1 | 0 | 4.716 |
| `CV2-D-V-BANCO-007` | 11 | L13 | 3 | 10 | 0 | 3.056 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 2.772 |
| `CV2-D-V-BANCO-009` | 3 | L13 | 11 | 2 | 0 | 5.258 |
| `CV2-D-V-BANCO-010` | 1 | L3 | 3 | 0 | 0 | 1.961 |
| `CV2-D-V-BANCO-011` | 12 | L12 | 1 | 11 | 0 | 2.508 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 8.461 |
| `CV2-D-V-FAMILIAR-001` | 5 | L15 | 11 | 4 | 0 | 5.791 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 3.146 |
| `CV2-D-V-FAMILIAR-003` | 14 | L14 | 1 | 13 | 0 | 2.438 |
| `CV2-D-V-FAMILIAR-004` | 14 | sin aviso | 16 | 13 | 0 | 7.868 |
| `CV2-D-V-FAMILIAR-005` | 18 | sin aviso | 4 | 17 | 0 | 4.199 |
| `CV2-D-V-FAMILIAR-006` | 17 | sin aviso | 7 | 16 | 0 | 5.012 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L12 | 11 | 1 | 0 | 5.033 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L9 | 9 | 0 | 0 | 4.359 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | L13 | 1 | 12 | 0 | 3.328 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | sin aviso | 20 | 1 | 0 | 8.062 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 9.581 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 8.623 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.452 |
| `CV2-D-V-PREMIO-002` | 3 | L13 | 11 | 2 | 0 | 5.688 |
| `CV2-D-V-PREMIO-003` | 3 | sin aviso | 26 | 2 | 0 | 10.927 |
| `CV2-D-V-PREMIO-004` | 12 | L14 | 3 | 11 | 0 | 3.345 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 8.195 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 9.464 |
| `CV2-D-V-SOPORTE-001` | 12 | L14 | 3 | 11 | 0 | 2.924 |
| `CV2-D-V-SOPORTE-002` | 1 | L10 | 10 | 0 | 0 | 4.428 |
| `CV2-D-V-SOPORTE-003` | 1 | sin aviso | 21 | 0 | 0 | 9.032 |
| `CV2-D-V-SOPORTE-004` | 13 | L14 | 2 | 12 | 0 | 3.081 |
| `CV2-D-V-SOPORTE-005` | 10 | sin aviso | 12 | 9 | 0 | 5.796 |
| `CV2-D-V-SOPORTE-006` | 1 | sin aviso | 20 | 0 | 0 | 8.732 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 3.613 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 3.843 |
| `CV2-D-V-WHATSAPP-001` | 1 | L9 | 9 | 0 | 0 | 4.093 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 2.160 |
| `CV2-D-V-WHATSAPP-003` | 8 | L12 | 5 | 7 | 0 | 3.708 |
| `CV2-D-V-WHATSAPP-004` | 5 | sin aviso | 17 | 4 | 0 | 7.102 |
| `CV2-D-V-WHATSAPP-005` | 10 | L14 | 5 | 9 | 0 | 3.401 |
| `CV2-D-V-WHATSAPP-006` | 22 | L26 | 5 | 21 | 0 | 5.945 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 6.220 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 5.993 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 1.856 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.849 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 1.766 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.628 |
| `LAB-anses-canal-oficial` | 5 | sin aviso | 1 | 4 | 0 | 842 |
| `LAB-arca-canal-oficial` | 1 | sin aviso | 5 | 0 | 0 | 1.980 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 1.605 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.115 |
| `LAB-banco-app-parafrasis` | 1 | L1 | 1 | 0 | 0 | 863 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 1.792 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.972 |
| `LAB-banco-gasto-sin-pedido` | 1 | sin aviso | 3 | 0 | 0 | 1.442 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 684 |
| `LAB-banco-numeros-sin-clave` | 1 | L3 | 3 | 0 | 0 | 1.775 |
| `LAB-banco-revisa-app` | 3 | L4 | 2 | 2 | 0 | 1.527 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 1.584 |
| `LAB-familiar-llama-vos` | 2 | sin aviso | 4 | 1 | 0 | 1.605 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 2.092 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 1.926 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 1.835 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 2.260 |
| `LAB-no-bajes-nada` | 4 | sin aviso | 1 | 3 | 0 | 856 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 1.664 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 621 |
| `LAB-whatsapp-codigo` | 1 | L1 | 1 | 0 | 0 | 856 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.649 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 1.559 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.083 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.638 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 3.353 |
| `LG-SUPPORT-INFO-01-e01` | 7 | sin aviso | 7 | 6 | 0 | 4.209 |
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 3.361 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 425 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L4 | 3 | 1 | 0 | 1.970 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 2.030 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 2.848 |
| `SC-PREMIO-01-e01` | 3 | L8 | 6 | 2 | 0 | 3.724 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 2.484 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.843 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.659 |
| `TR-01-pedido-indirecto-digitos` | 3 | L6 | 4 | 2 | 0 | 2.412 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 3.172 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.456 |
| `TR-04-pedido-tras-charla-larga` | 5 | L26 | 22 | 4 | 0 | 10.259 |
| `TR-05-asado-con-transferencia` | 14 | sin aviso | 14 | 13 | 0 | 7.919 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 4.015 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L7 | 3 | 4 | 0 | 2.164 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 1.022 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.282 |
| `TR-10-ofrecimiento-inducido` | 4 | L6 | 3 | 3 | 0 | 2.059 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 2.144 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 3.034 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.591 |

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
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v4\|rol` | 652.908 | 149.713 | 503.195 | 1.31204e+06 | 2271 | 1132/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
