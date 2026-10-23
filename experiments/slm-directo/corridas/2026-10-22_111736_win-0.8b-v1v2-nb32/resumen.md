# Resumen de la corrida `2026-10-22_111736_win-0.8b-v1v2-nb32`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:0.8b --prompts tarea,v2 --num-batch 32 --sin-reglas --etiqueta win-0.8b-v1v2-nb32 --url http://127.0.0.1:11435`
- **Inicio / fin:** 2026-10-22T11:17:36 / 2026-10-22T11:22:34
- **Código:** `886cff0633`
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:0.8b\|tarea\|ab` | 26/29 | 7 | 11 | 5 | 2 | 8/24 | 0/464 | 174 | 531 | 31/34 | 0 |
| `slm\|qwen3.5:0.8b\|v2\|ab` | 23/29 | 5 | 11 | 5 | 2 | 8/24 | 0/464 | 430 | 664 | 30/31 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:0.8b\|tarea\|ab` · **C2** `slm\|qwen3.5:0.8b\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | >R L4 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok | ok |
| `LAB-arca-deuda` | vishing | 3 | — | >R L5 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 | >R L5 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L5 | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 | <R L4 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L3 | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 | FA L3 |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | — | ≥C L4 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok | FA L11 |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L6 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L9 | FA L5 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L7 | >R L10 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L8 | >R L10 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | ≥C L9 | <R L4 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 | — |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 | >R L9 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | >R L9 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L20 | <R L21 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L20 | FA L13 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok | FA L9 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | ≥C L9 | ≥C L9 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L4 | FA L4 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | >R L9 | — |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok | FA L6 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L9 | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok | ok |

## Para revisar

### Falsas alarmas

- `LAB-banco-app-parafrasis` · `slm|qwen3.5:0.8b|tarea|ab` · línea 5: «Te están pidiendo un código de verificación o activación que permite acceder a tu cuenta bancaria.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos
B: no hay nada raro
A: buenisimo era mentira entonces»
- `LAB-banco-gasto-sin-pedido` · `slm|qwen3.5:0.8b|tarea|ab` · línea 3: «Te están solicitando un código de verificación o activación para acceder a tu cuenta bancaria.» — evidencia (cita textual): «A: te llama el banco porque vimos un gasto que no cierra
2. A: no hagas nada por telefono
3. A: entra vos a la aplicacion cuando puedas y fijate»
- `LAB-banco-revisa-app` · `slm|qwen3.5:0.8b|tarea|ab` · línea 3: «Te están pidiendo un código de verificación o activación que permite acceso a tu cuenta bancaria.» — evidencia (cita textual): «A: te aviso que hubo un consumo en la tarjeta
B: ok donde lo miro
A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `slm|qwen3.5:0.8b|tarea|ab` · línea 3: «Te están solicitando un número de teléfono que no tienes guardado y pidiendo que llames a alguien para verificar si hay una persona en peligro. Esto es una señal clara de estafas (vishing) diseñadas para robar datos personales o acceder a cuentas.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:0.8b|tarea|ab` · línea 6: «Te están solicitando datos personales (DNI) y una foto de un documento para verificar si estás en el listado de jubilados. Esto es una acción directa de seguridad guiada que podría permitirles robar tu información o acceder a tus cuentas.» — evidencia (cita textual): «B: ¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando explícitamente una clave nueva para ingresar a tu cuenta y mencionan que nadie de la mesa te la pedirá. Esto es un patrón clásico de estafas (vishing) diseñado para inducir al usuario a revelar información sensible.» — evidencia (cita textual): «A: En la pantalla de ingreso tocá «Olvidé mi contraseña». Te va a llegar un correo a la dirección que tenés registrada.
B: Ya me llegó. ¿Te leo lo que dice?»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:0.8b|tarea|ab` · línea 20: «Te están solicitando un código de verificación para confirmar que el pago de 'veintidós mil' es válido y que la persona (Nicolás Peralta) no está en otra cuenta. Esto permite robarle dinero o tomar sus cuentas.» — evidencia (cita textual): «A: Fijate que te aparezca mi nombre, Nicolás Peralta, antes de confirmar, no sea cosa que se lo mandes a otro.»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:0.8b|tarea|ab` · línea 4: «Te están solicitando un código de acceso a una valija que me prestaste en el hotel para cerrarla sin pensar; esto es una acción directa de robo.» — evidencia (cita textual): «A: Pasame el código del candado de la valija que me prestaste. La cerré sin pensar y ahora, en el hotel, no la puedo abrir.»
- `LAB-familiar-llama-vos` · `slm|qwen3.5:0.8b|v2|ab` · línea 3: «El usuario está solicitando explícitamente datos personales (DNI, CUIL) y instrucciones de seguridad para acceder a su cuenta bancaria o realizar pagos, lo cual constituye un pedido directo de robo de identidad.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LAB-no-bajes-nada` · `slm|qwen3.5:0.8b|v2|ab` · línea 4: «El usuario está solicitando explícitamente la descarga de un programa para mostrar su teléfono móvil a otra persona (B), lo cual es una acción directa que permite robar datos personales o acceso a cuentas bancarias.» — evidencia (cita textual): «A: me llamaron para que baje un programa y les muestre el celular»
- `LG-FAMILIAR-LLAMADO-01-e01` · `slm|qwen3.5:0.8b|v2|ab` · línea 11: «El solicitante está pidiendo dinero (plata) y sugiriendo transferirlo a terceros (remedios, taxi), lo cual es una clara indicación de robo o robaría.» — evidencia (cita textual): «A: ¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:0.8b|v2|ab` · línea 5: «El interlocutor A está solicitando explícitamente el usuario y la contraseña de su cuenta bancaria sin justificación previa o consentimiento, lo cual constituye un pedido directo para robar datos personales y financieros.» — evidencia (cita textual): «A: Bien, lo vemos. Antes que nada, no me digas ni tu usuario ni tu contraseña; para esto no los necesito.»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:0.8b|v2|ab` · línea 13: «El solicitante pide transferir dinero directamente al cliente (Lucho) mediante tarjeta de crédito sin intermediarios bancarios o autorización previa.» — evidencia (cita textual): «A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.»
- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:0.8b|v2|ab` · línea 9: «El interlocutor A explora explícitamente el riesgo de que un tercero solicite información crítica (código de verificación, clave, PIN) o datos personales para robarle dinero o acceder a sus cuentas bancarias.» — evidencia (cita textual): «A: Antes que nada: no te voy a pedir ningún código, ni la clave, ni los números de la tarjeta. Si en algún momento alguien te los pide, cortá.»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:0.8b|v2|ab` · línea 4: «El solicitante está pidiendo un código para abrir una caja de seguridad (candado) que el cliente le prestó anteriormente y ahora no puede acceder a por sí mismo en su hotel.» — evidencia (cita textual): «A: Pasame el código del candado de la valija que me prestaste.»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:0.8b|v2|ab` · línea 6: «El cliente está solicitando la transferencia de dinero a su cuenta bancaria (transferir veinte mil pesos) sin verificar su identidad o el origen del pago.» — evidencia (cita textual): «B: ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `LAB-digitos-sin-palabra` · `slm|qwen3.5:0.8b|tarea|ab` · riesgo máximo 0.00
- `LAB-pantalla-sin-programa` · `slm|qwen3.5:0.8b|tarea|ab` · riesgo máximo 0.00
- `LAB-whatsapp-codigo` · `slm|qwen3.5:0.8b|tarea|ab` · riesgo máximo 0.00
- `LAB-digitos-sin-palabra` · `slm|qwen3.5:0.8b|v2|ab` · riesgo máximo 0.80
- `LAB-pantalla-sin-programa` · `slm|qwen3.5:0.8b|v2|ab` · riesgo máximo 0.80
- `SC-PREMIO-01-e01` · `slm|qwen3.5:0.8b|v2|ab` · riesgo máximo 0.50
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:0.8b|v2|ab` · riesgo máximo 0.50
- `TR-10-ofrecimiento-inducido` · `slm|qwen3.5:0.8b|v2|ab` · riesgo máximo 0.50
- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:0.8b|v2|ab` · riesgo máximo 0.50

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:0.8b` | 4.903 | 512 | 512 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
