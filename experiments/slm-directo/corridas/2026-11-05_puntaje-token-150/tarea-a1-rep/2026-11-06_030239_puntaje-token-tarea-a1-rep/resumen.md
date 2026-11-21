# Resumen de la corrida `2026-11-06_030239_puntaje-token-tarea-a1-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --seguir-tras-aviso --prompts tarea-a1 --hablantes ab --etiqueta puntaje-token-tarea-a1-rep --salida /content/resultados-puntaje-token/tarea-a1-rep`
- **Inicio / fin:** 2026-11-06T03:02:39 / 2026-11-06T03:08:50
- **Código:** `8f6c0a460a`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|tarea-a1\|ab` | 49/75 | 12 | 33 | 3 | 1 | 13/75 | 0/2773 | 146 | 235 | 0/62 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|tarea-a1\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | ok |
| `CV2-D-L-BANCO-002` | legítima | — | — | ok |
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
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L8 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | FA L15 |
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
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L16 |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | =R L32 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L11 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | — |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L11 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | =R L17 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | — |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L12 |
| `CV2-D-V-BANCO-011` | vishing | — | — | — |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | >R L16 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | — |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | — |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | — |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | >R L17 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L10 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L10 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L24 |
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
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L4 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | FA L1 |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | ≥C L30 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L14 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | =R L7 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | =R L8 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 10: «» — evidencia (cita NO textual): «»
- `CV2-D-L-FAMILIAR-002` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 8: «» — evidencia (cita NO textual): «»
- `CV2-D-L-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 15: «» — evidencia (cita NO textual): «»
- `CV2-D-L-WHATSAPP-001` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 16: «» — evidencia (cita NO textual): «»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 4: «» — evidencia (cita NO textual): «»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-portero-codigo-puerta` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 1: «» — evidencia (cita NO textual): «»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 1: «» — evidencia (cita NO textual): «»
- `TR-05-asado-con-transferencia` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 14: «» — evidencia (cita NO textual): «»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 10: «» — evidencia (cita NO textual): «»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 3: «» — evidencia (cita NO textual): «»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 4: «» — evidencia (cita NO textual): «»
- `TR-13-turno-medico-pide-dni` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · línea 5: «» — evidencia (cita NO textual): «»

### Vishing sin aviso

- `CV2-D-V-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-BANCO-008` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-BANCO-011` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-BANCO-012` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-003` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-004` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-002` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-004` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-005` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-SOPORTE-007` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-SOPORTE-008` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-007` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `CV2-D-V-WHATSAPP-008` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `LAB-digitos-sin-palabra` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `TR-01-pedido-indirecto-digitos` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|tarea-a1|ab` · sin riesgo registrado

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 594 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|tarea-a1\|ab` | 328.769 | 368.660 | 0 | 328.769 | 1.30123e+06 | 2357 | 2357/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (0 en esta corrida) no consultan y no cuentan como ausencia.
