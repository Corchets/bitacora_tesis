# Resumen de la corrida `2026-10-21_201914_m1-reglas-v2-150`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --solo-reglas --reglas v2 --etiqueta m1-reglas-v2-150`
- **Inicio / fin:** 2026-10-21T20:19:14 / 2026-10-21T20:19:15
- **Código:** `fc21b37684` con cambios sin commit en la carpeta
- **Máquina:** macOS-27.0.1-arm64-arm-64bit, 8 núcleos lógicos, 8.0 GB de RAM
- **Ollama:** no usado · **Política:** aviso_unico_primer_true_valido
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas_v2` | 32/75 | 4 | 23 | 3 | 2 | 8/75 | 0/2773 | 0 | 1 | 40/40 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas_v2`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | ok |
| `CV2-D-L-BANCO-002` | legítima | — | — | ok |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | ok |
| `CV2-D-L-BANCO-005` | legítima | — | — | ok |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L9 |
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
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L8 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-001` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L20 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | FA L6 |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | FA L22 |
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
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L15 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | =R L18 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | — |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | — |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | — |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | =R L14 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L15 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | — |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | — |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | — |
| `CV2-D-V-BANCO-011` | vishing | — | — | — |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | ≥C L20 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | ≥C L27 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | — |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L10 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | — |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | — |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | — |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | — |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | — |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 |
| `LAB-giro-sin-plata` | vishing | 3 | — | — |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | — |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | >R L8 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L21 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L13 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | — |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | — |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-006` · `reglas_v2` · línea 9: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Eso explica una parte. También me apareció un mensaje con un código cuando abrí la app, pero yo no estaba entrando.»
- `CV2-D-L-BANCO-010` · `reglas_v2` · línea 10: «REQUEST_AUTH_CODE (patrón: numeros)» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-FAMILIAR-002` · `reglas_v2` · línea 8: «REQUEST_TRANSFER (patrón: transferi)» — evidencia (cita textual): «Somos cuatro: transferime 11.700 por tu parte cuando puedas.»
- `CV2-D-L-MEDICO-002` · `reglas_v2` · línea 20: «REQUEST_SECURITY_ACTION (patrón: autoriza)» — evidencia (cita textual): «si autorizaste el portal suele aparecer ahí el laboratorio te confirma el estado»
- `CV2-D-L-SOPORTE-001` · `reglas_v2` · línea 6: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «Voy a revisar la línea. ¿Me confirmás la calle y la altura donde está instalado?»
- `CV2-D-L-SOPORTE-002` · `reglas_v2` · línea 22: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Está bien. La clave no necesito que me la digas.»
- `TR-05-asado-con-transferencia` · `reglas_v2` · línea 13: «REQUEST_TRANSFER (patrón: pago, transferencia, transferi)» — evidencia (cita textual): «Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.»
- `TR-08-frase-cortada-candado` · `reglas_v2` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Pasame el código»

### Vishing sin aviso

- `CV2-D-V-BANCO-003` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-004` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-005` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-008` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-009` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-010` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-011` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-BANCO-012` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-003` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-004` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-005` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-006` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-001` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-002` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-PREMIO-001` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-PREMIO-002` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-PREMIO-003` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-PREMIO-005` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-PREMIO-006` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-001` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-003` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-004` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-005` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-006` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-007` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-SOPORTE-008` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-004` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-005` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-006` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-007` · `reglas_v2` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-008` · `reglas_v2` · sin riesgo registrado
- `LAB-digitos-sin-palabra` · `reglas_v2` · sin riesgo registrado
- `LAB-giro-sin-plata` · `reglas_v2` · sin riesgo registrado
- `LAB-pantalla-sin-programa` · `reglas_v2` · sin riesgo registrado
- `SC-PREMIO-01-e01` · `reglas_v2` · sin riesgo registrado
- `TR-01-pedido-indirecto-digitos` · `reglas_v2` · sin riesgo registrado
- `TR-07-pedido-partido-en-dos-lineas` · `reglas_v2` · sin riesgo registrado
- `TR-10-ofrecimiento-inducido` · `reglas_v2` · sin riesgo registrado
- `TR-12-corta-antes-del-pedido` · `reglas_v2` · sin riesgo registrado

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.
