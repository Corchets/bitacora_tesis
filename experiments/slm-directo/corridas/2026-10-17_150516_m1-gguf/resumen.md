# Resumen de la corrida `2026-10-17_150516_m1-gguf`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:0.8b-q8_0,qwen3.5:2b-q8_0,qwen3.5:4b-q4_K_M --sin-reglas --etiqueta m1-gguf`
- **Inicio / fin:** 2026-10-17T15:05:16 / 2026-10-17T16:21:26 — **interrumpida**
- **Código:** `ffe9343421`
- **Máquina:** macOS-26.6.2-arm64-arm-64bit-Mach-O, 8 núcleos lógicos, 8.0 GB de RAM
- **Ollama:** 0.40.5 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | 27/29 | 8 | 12 | 4 | 2 | 9/24 | 0/464 | 1.282 | 3.462 | 32/36 | 0 |
| `slm\|qwen3.5:2b-q8_0\|tarea\|ab` | 20/29 | 2 | 15 | 2 | 1 | 2/24 | 0/464 | 2.646 | 6.036 | 21/22 | 0 |
| `slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | 24/24 | 13 | 11 | 0 | 0 | 9/18 | 0/314 | 6.606 | 10.172 | 32/33 | 1 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` · **C2** `slm\|qwen3.5:2b-q8_0\|tarea\|ab` · **C3** `slm\|qwen3.5:4b-q4_K_M\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 | C3 |
|---|---|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok | ok | FA L1 |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | ok | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L5 | ok | FA L1 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 | =R L5 | <R L1 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L3 | ok | FA L1 |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 | =R L5 | <R L2 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 | ok | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 | ok | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 | — | <R L3 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok | FA L2 |
| `LAB-no-bajes-nada` | legítima | — | — | ok | ok | FA L1 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | — | <R L1 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok | ok | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok | ok | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L6 | ok | FA L6 |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L9 | ok | FA L4 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok | ok | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L7 | =R L9 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L8 | =R L9 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | ≥C L9 | — | <R L4 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 | =R L8 | <R L6 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 | =R L6 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 | =R L6 | <R L1 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | =R L4 | <R L2 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | >R L9 | — | <R L3 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok | ok | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok | FA L7 | … |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L20 | =R L26 |  |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L20 | FA L14 |  |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok | ok |  |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | ≥C L9 | >R L8 |  |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L4 | ok |  |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 | >R L6 |  |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | >R L9 | ≥C L14 |  |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 | ok |  |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L9 | — |  |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok | ok |  |

## Para revisar

### Falsas alarmas

- `LAB-banco-app-parafrasis` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 5: «Te están pidiendo un código de verificación o activación que permite acceder a tu cuenta bancaria.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos
B: no hay nada raro
A: buenisimo era mentira entonces»
- `LAB-banco-gasto-sin-pedido` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 3: «Te están solicitando un código de verificación o activación que permitiría acceder a tu cuenta bancaria.» — evidencia (cita textual): «A: te llama el banco porque vimos un gasto que no cierra
2. A: no hagas nada por telefono
3. A: entra vos a la aplicacion cuando puedas y fijate»
- `LAB-banco-revisa-app` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 3: «Te están pidiendo un código de verificación o activación que permite acceso a tu cuenta bancaria.» — evidencia (cita textual): «A: te aviso que hubo un consumo en la tarjeta
B: ok donde lo miro
A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 3: «Te están solicitando un número de teléfono que no tienes guardado y pidiendo que llames a alguien para verificar tu identidad o acceder a tus datos personales.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 6: «Te están solicitando datos personales (DNI) y una foto de un documento para verificar si estás en el listado de jubilados. Esto es una acción directa de seguridad guiada que podría permitirles robar tu información o acceder a tus cuentas.» — evidencia (cita textual): «B: ¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 9: «Te están solicitando explícitamente una clave nueva para ingresar a tu cuenta y mencionan que nadie de la mesa te la pedirá. Esto es un patrón clásico de estafas (vishing) diseñado para inducir al usuario a revelar información sensible.» — evidencia (cita textual): «A: En la pantalla de ingreso tocá «Olvidé mi contraseña». Te va a llegar un correo a la dirección que tenés registrada.
B: Ya me llegó. ¿Te leo lo que dice?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 20: «Te están solicitando un código de verificación para confirmar que el pago de 'veintidós mil' es válido y que la persona (Nicolás Peralta) tiene los fondos suficientes para pagarlo antes del viernes.» — evidencia (cita textual): «13. A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.
14. B: Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.
15. A: Te lo mando por el grupo. Es el mismo de la vaquita del cumple de Lucho.»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 4: «Te están solicitando un código de acceso a una valija que me prestaste en el hotel para cerrarla sin pensar; esto es una acción directa de robo.» — evidencia (cita textual): «A: Pasame el código del candado de la valija que me prestaste. La cerré sin pensar y ahora, en el hotel, no la puedo abrir.»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · línea 9: «Te están solicitando un código de verificación o activación para acceder a tu cuenta bancaria y transferir dinero.» — evidencia (cita NO textual): «B: ¿Me podrás transferir veinte mil pesos? A: Sí, mi amor. ¿A qué cuenta? B: A la mía de siempre, la que tenés agendada. No hay apuro, eh: hoy o mañana, cuando puedas. El viernes cobro y te los devuelvo.»
- `TR-03-negacion-y-consejo` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 7: «Te están pidiendo compartir la pantalla para ayudarte con una aplicación» — evidencia (cita textual): «7. A: ¿Y si me piden que comparta la pantalla para ayudarme con la aplicación?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:2b-q8_0|tarea|ab` · línea 14: «Te están pidiendo un código de verificación para una transferencia antes del viernes» — evidencia (cita textual): «13. A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.
14. B: Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.»
- `LAB-anses-canal-oficial` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo datos personales bajo amenaza de un bono» — evidencia (cita textual): «me ofrecieron un bono si les doy datos del organismo»
- `LAB-banco-app-parafrasis` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo que veas una aplicación bancaria para posiblemente robar tus datos o dinero» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 1: «Te están simulando ser el banco para pedirte un código o datos por un gasto falso» — evidencia (cita textual): «te llama el banco porque vimos un gasto que no cierra»
- `LAB-banco-revisa-app` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación para verificar un consumo en tu tarjeta.» — evidencia (cita textual): «corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-mensajeria-no-pases-nada` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 2: «Te están fingiendo ser soporte técnico para intentar engañarte» — evidencia (cita textual): «A: me llamo alguien que dice ser soporte de la aplicacion de mensajes»
- `LAB-no-bajes-nada` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo que bajes un programa y les muestres el celular para acceder a tus datos» — evidencia (cita textual): «me llamaron para que baje un programa y les muestre el celular»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 6: «Te están presionando para que des tus datos personales (DNI, domicilio) y una foto del documento.» — evidencia (cita textual): «A: Eso no lo hacemos nosotros. Por teléfono no pedimos fotos del documento, claves ni datos del banco.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo que entregues tu usuario y contraseña para verificar si son incorrectos.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `LG-WA-CONSULTA-01-e01` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo un código de activación que no pediste» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»

### Vishing sin aviso

- `LAB-pantalla-sin-programa` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · riesgo máximo 0.00
- `LAB-whatsapp-codigo` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · riesgo máximo 0.00
- `LAB-arca-deuda` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-arca-deuda-parafrasis` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-digitos-sin-palabra` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-familiar-peligro-parafrasis` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.80
- `LAB-giro-sin-plata` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.30
- `LAB-pantalla-sin-programa` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.80
- `SC-ORG-BENEFICIO-01-e01` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.85
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.65
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:2b-q8_0|tarea|ab` · riesgo máximo 0.20

### Sin evaluar

- `TR-03-negacion-y-consejo` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · la corrida se cortó antes de terminarlo

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:0.8b-q8_0` | 5.097 | 1.018 | 1.018 |
| `qwen3.5:2b-q8_0` | 28.224 | 2.237 | 2.237 |
| `qwen3.5:4b-q4_K_M` | 12.343 | 2.954 | 2.954 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
