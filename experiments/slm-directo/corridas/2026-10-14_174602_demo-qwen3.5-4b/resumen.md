# Resumen de la corrida `2026-10-14_174602_demo-qwen3.5-4b`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:4b --sin-reglas --detalle --etiqueta demo-qwen3.5-4b`
- **Inicio / fin:** 2026-10-14T17:46:02 / 2026-10-14T17:54:44
- **Código:** `76fafa2ea6` con cambios sin commit en la carpeta
- **Máquina:** Windows-11-10.0.26300-SP0, 12 núcleos lógicos, 31.9 GB de RAM
- **Ollama:** 0.40.4 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:4b\|tarea\|ab` | 29/29 | 17 | 11 | 0 | 0 | 15/24 | 0/464 | 901 | 1.646 | 44/44 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:4b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L1 |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L1 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L2 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L2 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L3 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L10 |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L4 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L4 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | <R L6 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L1 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L1 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L3 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L7 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L3 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L13 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L3 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L3 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L10 |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 |

## Para revisar

### Falsas alarmas

- `LAB-anses-canal-oficial` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo datos personales bajo amenaza de un bono» — evidencia (cita textual): «me ofrecieron un bono si les doy datos del organismo»
- `LAB-banco-app-parafrasis` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo que veas una aplicación bancaria para posiblemente robar tus datos o dinero» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-revisa-app` · `slm|qwen3.5:4b|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación para verificar un consumo en tu tarjeta.» — evidencia (cita textual): «corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-mensajeria-no-pases-nada` · `slm|qwen3.5:4b|tarea|ab` · línea 2: «Te están fingiendo ser soporte técnico para intentar engañarte» — evidencia (cita textual): «A: me llamo alguien que dice ser soporte de la aplicacion de mensajes»
- `LAB-no-bajes-nada` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo que bajes un programa y les muestres el celular para acceder a tus datos» — evidencia (cita textual): «me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 2: «Te están pidiendo que cambies tu clave por un aviso de ingreso sospechoso» — evidencia (cita textual): «Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 10: «Te están pidiendo tu número de documento para que te saquen un turno por teléfono.» — evidencia (cita textual): «10: B: ¿Y el turno no me lo podés sacar vos? Te paso el número de documento, si querés.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 4: «Te están pidiendo que entregues tu usuario y contraseña para verificar si son correctos.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `LG-WA-CONSULTA-01-e01` · `slm|qwen3.5:4b|tarea|ab` · línea 1: «Te están pidiendo un código de activación que no solicitaste» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `TR-03-negacion-y-consejo` · `slm|qwen3.5:4b|tarea|ab` · línea 7: «Te están pidiendo compartir tu pantalla para acceder a tus cuentas» — evidencia (cita textual): «¿Y si me piden que comparta la pantalla para ayudarme con la aplicación?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:4b|tarea|ab` · línea 13: «Te están pidiendo transferir dinero antes del viernes para pagar a un tercero.» — evidencia (cita textual): «"Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta."»
- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:4b|tarea|ab` · línea 3: «Te están simulando ser del banco para pedirte información sobre tu tarjeta de crédito» — evidencia (cita textual): «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:4b|tarea|ab` · línea 3: «Te están pidiendo un código de acceso a tu cuenta o servicio» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:4b|tarea|ab` · línea 4: «Te están pidiendo dinero bajo una excusa falsa sobre un recibo de luz.» — evidencia (cita textual): «Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `slm|qwen3.5:4b|tarea|ab` · línea 5: «Te están pidiendo datos personales (DNI y fecha de nacimiento) bajo el pretexto de un centro de salud.» — evidencia (cita textual): «"Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema."»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:4b` | 17.913 | 2.995 | 2.995 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
