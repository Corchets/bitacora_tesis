# Resumen de la corrida `2026-10-22_103341_win-4b-v1v2-nb32`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:4b --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta win-4b-v1v2-nb32 --url http://127.0.0.1:11435`
- **Inicio / fin:** 2026-10-22T10:33:41 / 2026-10-22T11:17:16
- **Código:** `886cff0633`
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:4b\|tarea\|ab` | 29/29 | 17 | 11 | 0 | 0 | 15/24 | 0/464 | 2.472 | 4.897 | 43/44 | 0 |
| `slm\|qwen3.5:4b\|v2\|ab` | 24/29 | 0 | 20 | 2 | 2 | 3/24 | 0/464 | 2.167 | 4.199 | 27/27 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:4b\|tarea\|ab` · **C2** `slm\|qwen3.5:4b\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L1 | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 | >R L5 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L1 | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L3 | >R L6 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 | ok |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L6 | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L10 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L4 | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L4 | ≥C L10 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | <R L6 | — |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | — |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L2 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L3 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L5 | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L3 | =R L26 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L14 | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L4 | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L3 | =R L7 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 | ≥C L13 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | FA L5 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L10 | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 | ok |

## Para revisar

### Falsas alarmas

- `LAB-anses-canal-oficial` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo datos personales bajo amenaza de un bono» — evidencia (cita textual): «me ofrecieron un bono si les doy datos del organismo»
- `LAB-banco-app-parafrasis` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo que veas una aplicación bancaria para posiblemente robar tus datos o dinero» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-revisa-app` · `slm|qwen3.5:4b|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación para verificar un consumo en tu tarjeta.» — evidencia (cita textual): «corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-mensajeria-no-pases-nada` · `slm|qwen3.5:4b|tarea|ab` · línea 2: «Te están fingiendo ser soporte técnico para intentar engañarte» — evidencia (cita textual): «A: me llamo alguien que dice ser soporte de la aplicacion de mensajes»
- `LAB-no-bajes-nada` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo bajar un programa para que te muestren el celular» — evidencia (cita textual): «me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 6: «Te están pidiendo tu número de tarjeta para verificar tu identidad» — evidencia (cita textual): «¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 10: «Te están pidiendo tu número de documento para que te saquen un turno por teléfono» — evidencia (cita textual): «10: B: ¿Y el turno no me lo podés sacar vos? Te paso el número de documento, si querés.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 4: «Te están pidiendo que entregues tu usuario y contraseña para verificar si son incorrectos.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `LG-WA-CONSULTA-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo un código de activación que no pediste» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `TR-03-negacion-y-consejo` · `slm|qwen3.5:4b|tarea|ab` · línea 5: «Te están presionando para que hagas una transferencia por miedo a que te bloqueen la cuenta» — evidencia (cita textual): «¿Y si me dicen que tengo que transferir para que no me bloqueen la cuenta?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:4b|tarea|ab` · línea 14: «Te están pidiendo transferir dinero y enviarte un alias para acceder a tu cuenta» — evidencia (cita NO textual): «"Si podés, pasámelos por transferencia antes del viernes... Mandame el alias que ahora no lo tengo a mano."»
- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:4b|tarea|ab` · línea 4: «Te están simulando ser el banco para pedirte información sobre tu tarjeta de crédito» — evidencia (cita textual): «"Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito."»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:4b|tarea|ab` · línea 3: «Te están pidiendo un código de acceso a tu cuenta o servicio» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:4b|tarea|ab` · línea 4: «Te están pidiendo dinero bajo una excusa falsa sobre un pago de servicios.» — evidencia (cita textual): «¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `slm|qwen3.5:4b|tarea|ab` · línea 5: «Te están pidiendo datos personales (DNI y fecha de nacimiento) bajo el pretexto de un turno médico.» — evidencia (cita textual): «"Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema."»
- `LAB-banco-revisa-app` · `slm|qwen3.5:4b|v2|ab` · línea 3: «Te están pidiendo entrar a tu aplicación bancaria para acceder a tus cuentas.» — evidencia (cita textual): «corta esta comunicacion y entra vos a la aplicacion oficial»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:4b|v2|ab` · línea 3: «Te están pidiendo entregar un código de verificación o token que podría robar tu cuenta.» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:4b|v2|ab` · línea 5: «Te están pidiendo transferir dinero inmediatamente.» — evidencia (cita textual): «¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `LAB-digitos-sin-palabra` · `slm|qwen3.5:4b|v2|ab` · riesgo máximo 0.30
- `SC-PREMIO-01-e01` · `slm|qwen3.5:4b|v2|ab` · riesgo máximo 0.60
- `SC-SOPORTE-REMOTO-01-e01` · `slm|qwen3.5:4b|v2|ab` · riesgo máximo 0.75
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:4b|v2|ab` · riesgo máximo 0.60
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:4b|v2|ab` · riesgo máximo 0.30

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:4b` | 13.104 | 3.466 | 960 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
