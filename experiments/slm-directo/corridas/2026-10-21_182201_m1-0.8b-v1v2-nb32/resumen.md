# Resumen de la corrida `2026-10-21_182201_m1-0.8b-v1v2-nb32`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:0.8b-q8_0 --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta m1-0.8b-v1v2-nb32`
- **Inicio / fin:** 2026-10-21T18:22:01 / 2026-10-21T18:36:31 — **interrumpida**
- **Código:** `ece8ef46b4` con cambios sin commit en la carpeta
- **Máquina:** macOS-27.0.1-arm64-arm-64bit, 8 núcleos lógicos, 8.0 GB de RAM
- **Ollama:** 0.40.5 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | 26/29 | 8 | 12 | 3 | 2 | 9/24 | 0/464 | 1.017 | 2.990 | 32/35 | 0 |
| `slm\|qwen3.5:0.8b-q8_0\|v2\|ab` | 11/14 | 2 | 8 | 1 | 0 | 2/10 | 0/120 | 2.139 | 3.195 | 13/13 | 1 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` · **C2** `slm\|qwen3.5:0.8b-q8_0\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | >R L4 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 | — |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L5 | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 | <R L4 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L3 | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 | — |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 | FA L3 |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | — | … |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |  |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |  |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |  |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L6 |  |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |  |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L9 |  |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |  |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |  |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L7 |  |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L8 |  |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | ≥C L9 |  |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |  |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |  |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 |  |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |  |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |  |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |  |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |  |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L20 |  |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L20 |  |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok |  |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | ≥C L9 |  |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L4 |  |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |  |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | >R L9 |  |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 |  |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L9 |  |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |  |

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
- `LAB-familiar-llama-vos` · `slm|qwen3.5:0.8b-q8_0|v2|ab` · línea 3: «El usuario está solicitando explícitamente datos personales (DNI, CUIL) y instrucciones de seguridad para acceder a su cuenta bancaria o realizar pagos, lo cual constituye un pedido directo de robo de identidad.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LAB-no-bajes-nada` · `slm|qwen3.5:0.8b-q8_0|v2|ab` · línea 4: «El usuario está solicitando explícitamente la descarga de un programa para mostrar su teléfono móvil a otra persona (B), lo cual es una acción directa que permite robar datos personales o acceso a cuentas bancarias.» — evidencia (cita textual): «A: me llamaron para que baje un programa y les muestre el celular»

### Vishing sin aviso

- `LAB-pantalla-sin-programa` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · riesgo máximo 0.00
- `LAB-whatsapp-codigo` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · riesgo máximo 0.00
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:0.8b-q8_0|tarea|ab` · riesgo máximo 0.00
- `LAB-arca-deuda-parafrasis` · `slm|qwen3.5:0.8b-q8_0|v2|ab` · riesgo máximo 0.80
- `LAB-digitos-sin-palabra` · `slm|qwen3.5:0.8b-q8_0|v2|ab` · riesgo máximo 0.50
- `LAB-pantalla-sin-programa` · `slm|qwen3.5:0.8b-q8_0|v2|ab` · riesgo máximo 0.80

### Sin evaluar

- `LAB-whatsapp-codigo` · `slm|qwen3.5:0.8b-q8_0|v2|ab` · la corrida se cortó antes de terminarlo

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:0.8b-q8_0` | 2.006 | 988 | 988 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
