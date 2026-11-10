# Resumen de la corrida `2026-11-10_001612_etapa-3-c-sin-alerta`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-sin-alerta --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --seguir-tras-aviso --hablantes rol --etiqueta etapa-3-c-sin-alerta --salida /content/resultados-etapa-3/c-sin-alerta`
- **Inicio / fin:** 2026-11-10T00:16:12 / 2026-11-10T00:34:26
- **Código:** `c3c1ffa9b7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 244 (75 vishing, 169 legítimas); 244 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-sin-alerta\|rol` | 66/75 | 43 | 9 | 4 | 0 | 63/169 | 0/4325 | 240 | 402 | 0/129 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-sin-alerta\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-002` | legítima | — | — | ok |
| `CV2-D-L-BANCO-003` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-007` | legítima | — | — | FA L1 |
| `CV2-D-L-BANCO-008` | legítima | — | — | FA L3 |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L3 |
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
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L1 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | FA L1 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | FA L4 |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L2 |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | FA L2 |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | FA L3 |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L2 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L3 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L2 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L2 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L5 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L6 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | >R L23 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L15 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L3 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L10 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | >R L20 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L7 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L6 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L3 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | >R L16 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L14 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L1 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | — |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L2 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L4 |
| `LAB-acceso-remoto` | vishing | 3 | — | <R L1 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-anses-beneficio` | vishing | 3 | — | <R L1 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L1 |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L1 |
| `LAB-arca-deuda` | vishing | 3 | — | <R L1 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L1 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L1 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L1 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L1 |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L1 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L1 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L1 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L1 |
| `LAB-familiar-peligro` | vishing | 4 | — | <R L1 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L1 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L1 |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | <R L1 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | <R L1 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L5 |
| `ENT-L-BANCO-004` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L2 |
| `ENT-L-DELIVERY-001` | legítima | — | — | ok |
| `ENT-L-DELIVERY-002` | legítima | — | — | ok |
| `ENT-L-DELIVERY-003` | legítima | — | — | ok |
| `ENT-L-DELIVERY-004` | legítima | — | — | ok |
| `ENT-L-DELIVERY-005` | legítima | — | — | ok |
| `ENT-L-DELIVERY-006` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-001` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-002` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-003` | legítima | — | — | FA L11 |
| `ENT-L-ENCUESTA-004` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | FA L3 |
| `ENT-L-MEDICO-001` | legítima | — | — | ok |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | ok |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | ok |
| `ENT-L-SELECCION-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-002` | legítima | — | — | ok |
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L11 |
| `ENT-L-SOPORTE-006` | legítima | — | — | FA L8 |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L9 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L16 |
| `ENT-L-VENTAS-003` | legítima | — | — | FA L16 |
| `ENT-L-VENTAS-004` | legítima | — | — | FA L4 |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | FA L18 |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L18 |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L6 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | FA L3 |
| `LEG-CC-01` | legítima | — | — | ok |
| `LEG-CC-02` | legítima | — | — | ok |
| `LEG-CC-03` | legítima | — | — | ok |
| `LEG-CO-01` | legítima | — | — | ok |
| `LEG-CO-02` | legítima | — | — | ok |
| `LEG-CO-03` | legítima | — | — | ok |
| `LEG-EN-01` | legítima | — | — | ok |
| `LEG-EN-02` | legítima | — | — | ok |
| `LEG-EN-03` | legítima | — | — | ok |
| `LEG-ST-01` | legítima | — | — | ok |
| `LEG-ST-02` | legítima | — | — | ok |
| `LEG-ST-03` | legítima | — | — | FA L1 |
| `LEG-TU-01` | legítima | — | — | ok |
| `LEG-TU-02` | legítima | — | — | ok |
| `LEG-TU-03` | legítima | — | — | ok |
| `LEG-VE-01` | legítima | — | — | ok |
| `LEG-VE-02` | legítima | — | — | ok |
| `LEG-VE-03` | legítima | — | — | ok |
| `LEG2-BA-01` | legítima | — | — | FA L4 |
| `LEG2-BA-02` | legítima | — | — | FA L5 |
| `LEG2-BA-03` | legítima | — | — | FA L2 |
| `LEG2-BA-05` | legítima | — | — | FA L6 |
| `LEG2-CC-01` | legítima | — | — | FA L8 |
| `LEG2-CC-04` | legítima | — | — | ok |
| `LEG2-CC-05` | legítima | — | — | FA L6 |
| `LEG2-CC-06` | legítima | — | — | FA L6 |
| `LEG2-CO-01` | legítima | — | — | ok |
| `LEG2-CO-02` | legítima | — | — | ok |
| `LEG2-CO-03` | legítima | — | — | ok |
| `LEG2-CO-06` | legítima | — | — | ok |
| `LEG2-EN-01` | legítima | — | — | ok |
| `LEG2-EN-03` | legítima | — | — | ok |
| `LEG2-EN-04` | legítima | — | — | ok |
| `LEG2-EN-05` | legítima | — | — | ok |
| `LEG2-ST-02` | legítima | — | — | ok |
| `LEG2-ST-03` | legítima | — | — | FA L2 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | FA L2 |
| `LEG2-TU-01` | legítima | — | — | ok |
| `LEG2-TU-02` | legítima | — | — | ok |
| `LEG2-TU-05` | legítima | — | — | ok |
| `LEG2-TU-06` | legítima | — | — | ok |
| `LEG2-VE-01` | legítima | — | — | ok |
| `LEG2-VE-04` | legítima | — | — | FA L6 |
| `LEG2-VE-05` | legítima | — | — | ok |
| `LEG2-VE-06` | legítima | — | — | ok |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L1 |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L5 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L3 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L1 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L1 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L5 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | — |
| `TR-05-asado-con-transferencia` | legítima | — | — | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L3 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L3 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 8: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-007` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-008` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-009` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `CV2-D-L-ORGANISMO_PREVISIONAL-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `CV2-D-L-SOPORTE-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `CV2-D-L-WHATSAPP-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `CV2-D-L-WHATSAPP-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `CV2-D-L-WHATSAPP-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 5: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `ENT-L-ENCUESTA-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 11: «» — evidencia (cita NO textual): «»
- `ENT-L-ENCUESTA-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 11: «» — evidencia (cita NO textual): «»
- `ENT-L-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 8: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 9: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 16: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 16: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 18: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 18: «» — evidencia (cita NO textual): «»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-banco-gasto-sin-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-familiar-llama-vos` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-mensajeria-no-pases-nada` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 5: «» — evidencia (cita NO textual): «»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `LEG2-CC-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 8: «» — evidencia (cita NO textual): «»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `LEG2-ST-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `LEG2-VE-04` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `LG-BANK-VERIF-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `LG-ORG-TURNO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `LG-SUPPORT-INFO-01-e02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `TR-03-negacion-y-consejo` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 5: «» — evidencia (cita NO textual): «»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · línea 4: «» — evidencia (cita NO textual): «»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `TR-04-pedido-tras-charla-larga` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-sin-alerta|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 411 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-sin-alerta\|rol` | 712.732 | 1.092.986 | 0 | 712.732 | 1.8965e+06 | 2730 | 2730/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (0 en esta corrida) no consultan y no cuentan como ausencia.
