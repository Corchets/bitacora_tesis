# Resumen de la corrida `2026-10-14_173532_demo-qwen3.5-0.8b`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:0.8b --sin-reglas --detalle --etiqueta demo-qwen3.5-0.8b`
- **Inicio / fin:** 2026-10-14T17:35:32 / 2026-10-14T17:38:15
- **Código:** `76fafa2ea6` con cambios sin commit en la carpeta
- **Máquina:** Windows-11-10.0.26300-SP0, 12 núcleos lógicos, 31.9 GB de RAM
- **Ollama:** 0.40.4 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:0.8b\|tarea\|ab` | 26/29 | 7 | 12 | 4 | 2 | 8/24 | 0/464 | 276 | 706 | 30/34 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:0.8b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | >R L5 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L5 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L3 |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | — |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L9 |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L9 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L7 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | ≥C L9 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L20 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L20 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | ≥C L9 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L4 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | >R L9 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L9 |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `LAB-banco-app-parafrasis` · `slm|qwen3.5:0.8b|tarea|ab` · línea 5: «Te están pidiendo un código de verificación o activación que permite acceder a tu cuenta bancaria.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos
B: no hay nada raro
A: buenisimo era mentira entonces»
- `LAB-banco-gasto-sin-pedido` · `slm|qwen3.5:0.8b|tarea|ab` · línea 3: «Te están solicitando un código de verificación o activación que permitiría acceder a tu cuenta bancaria.» — evidencia (cita textual): «A: te llama el banco porque vimos un gasto que no cierra»
- `LAB-banco-revisa-app` · `slm|qwen3.5:0.8b|tarea|ab` · línea 3: «Te están pidiendo un código de verificación o activación que permite acceso a tu cuenta bancaria.» — evidencia (cita textual): «A: te aviso que hubo un consumo en la tarjeta
B: ok donde lo miro
A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `slm|qwen3.5:0.8b|tarea|ab` · línea 3: «Te están solicitando un número de teléfono que no tienes guardado y pidiendo que llames a alguien para verificar si hay una persona en peligro. Esto es una señal clara de estafas telefónicas (vishing) diseñadas para robar datos personales o acceder a cuentas.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando datos personales (DNI) y una foto de un documento para realizar una transferencia o pago, lo cual es una acción directa de robo de dinero.» — evidencia (cita textual): «B: ¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando una clave nueva para ingresar a tu cuenta sin pedirte nada más.» — evidencia (cita NO textual): «A: En la pantalla de ingreso tocá «Olvidé mi contraseña». Te va a llegar un correo a la dirección que tenés registrada. B: Ya me llegó. ¿Te leo lo que dice? A: No, ese correo es para vos. Seguí los pasos ahí mismo y elegí una clave nueva que no uses en otro lado.»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:0.8b|tarea|ab` · línea 20: «Te están solicitando un código de verificación para confirmar que el pago de 'veintidós mil' es válido y que la persona (Nicolás Peralta) tiene los fondos suficientes para pagarlo antes del viernes.» — evidencia (cita textual): «13. A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.
14. B: Dale, no hay drama. Mandame el alias que ahora no lo tengo a mano.
15. A: Te lo mando por el grupo. Es el mismo de la vaquita del cumple de Lucho.»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:0.8b|tarea|ab` · línea 4: «Te están solicitando un código de acceso a una valija que me prestaste en el hotel para cerrarla sin pensar; esto es una acción directa de robo.» — evidencia (cita textual): «A: Pasame el código del candado de la valija que me prestaste. La cerré sin pensar y ahora, en el hotel, no la puedo abrir.»

### Vishing sin aviso

- `LAB-pantalla-sin-programa` · `slm|qwen3.5:0.8b|tarea|ab` · riesgo máximo 0.00
- `LAB-whatsapp-codigo` · `slm|qwen3.5:0.8b|tarea|ab` · riesgo máximo 0.00
- `TR-01-pedido-indirecto-digitos` · `slm|qwen3.5:0.8b|tarea|ab` · riesgo máximo 0.00

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:0.8b` | 4.478 | 545 | 545 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
