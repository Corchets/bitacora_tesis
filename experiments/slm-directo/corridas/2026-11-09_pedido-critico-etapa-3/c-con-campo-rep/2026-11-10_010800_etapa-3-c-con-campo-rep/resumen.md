# Resumen de la corrida `2026-11-10_010800_etapa-3-c-con-campo-rep`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-con-campo --lista alcance-140 --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --seguir-tras-aviso --hablantes rol --etiqueta etapa-3-c-con-campo-rep --salida /content/resultados-etapa-3/c-con-campo-rep`
- **Inicio / fin:** 2026-11-10T01:08:00 / 2026-11-10T01:21:22
- **Código:** `c3c1ffa9b7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 140 (46 vishing, 94 legítimas); 140 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-con-campo\|rol` | 36/46 | 16 | 6 | 7 | 0 | 17/94 | 0/2621 | 285 | 343 | 12/53 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-con-campo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L4 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L8 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L3 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L6 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L7 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | >R L17 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L8 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | >R L26 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L5 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | >R L15 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L13 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | >R L24 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L14 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | >R L10 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | >R L13 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L9 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L13 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | — |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L4 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `ENT-L-BANCO-001` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-003` | legítima | — | — | ok |
| `ENT-L-BANCO-004` | legítima | — | — | FA L6 |
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
| `ENT-L-ENCUESTA-003` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-004` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | ok |
| `ENT-L-MEDICO-001` | legítima | — | — | ok |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | ok |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | ok |
| `ENT-L-SELECCION-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L3 |
| `ENT-L-SOPORTE-002` | legítima | — | — | ok |
| `ENT-L-SOPORTE-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L13 |
| `ENT-L-SOPORTE-006` | legítima | — | — | ok |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L27 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L16 |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | ok |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L20 |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L5 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | ok |
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
| `LEG-ST-03` | legítima | — | — | ok |
| `LEG-TU-01` | legítima | — | — | ok |
| `LEG-TU-02` | legítima | — | — | ok |
| `LEG-TU-03` | legítima | — | — | ok |
| `LEG-VE-01` | legítima | — | — | ok |
| `LEG-VE-02` | legítima | — | — | ok |
| `LEG-VE-03` | legítima | — | — | ok |
| `LEG2-BA-01` | legítima | — | — | FA L4 |
| `LEG2-BA-02` | legítima | — | — | FA L5 |
| `LEG2-BA-03` | legítima | — | — | FA L4 |
| `LEG2-BA-05` | legítima | — | — | FA L6 |
| `LEG2-CC-01` | legítima | — | — | ok |
| `LEG2-CC-04` | legítima | — | — | ok |
| `LEG2-CC-05` | legítima | — | — | FA L6 |
| `LEG2-CC-06` | legítima | — | — | ok |
| `LEG2-CO-01` | legítima | — | — | ok |
| `LEG2-CO-02` | legítima | — | — | ok |
| `LEG2-CO-03` | legítima | — | — | ok |
| `LEG2-CO-06` | legítima | — | — | ok |
| `LEG2-EN-01` | legítima | — | — | ok |
| `LEG2-EN-03` | legítima | — | — | ok |
| `LEG2-EN-04` | legítima | — | — | ok |
| `LEG2-EN-05` | legítima | — | — | ok |
| `LEG2-ST-02` | legítima | — | — | ok |
| `LEG2-ST-03` | legítima | — | — | ok |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | ok |
| `LEG2-TU-01` | legítima | — | — | ok |
| `LEG2-TU-02` | legítima | — | — | ok |
| `LEG2-TU-05` | legítima | — | — | ok |
| `LEG2-TU-06` | legítima | — | — | ok |
| `LEG2-VE-01` | legítima | — | — | ok |
| `LEG2-VE-04` | legítima | — | — | ok |
| `LEG2-VE-05` | legítima | — | — | ok |
| `LEG2-VE-06` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 1: «» — evidencia (cita NO textual): «»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 2: «» — evidencia (cita NO textual): «»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 13: «Te están pidiendo que leas un número de conexión, lo cual es una táctica común para obtener acceso remoto a tu dispositivo o información.» — evidencia (cita textual): «Sí. Te va a mostrar un número de conexión de nueve cifras. ¿Me lo leés?»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 27: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 16: «» — evidencia (cita NO textual): «»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 20: «La solicitud de un pago mediante transferencia a una cuenta de empresa, especialmente cuando se menciona la posibilidad de dejar una seña, es una táctica común en estafas.» — evidencia (cita textual): «Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 5: «» — evidencia (cita NO textual): «»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 3: «» — evidencia (cita NO textual): «»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 5: «» — evidencia (cita NO textual): «»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 4: «» — evidencia (cita NO textual): «»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 6: «» — evidencia (cita NO textual): «»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · línea 6: «» — evidencia (cita NO textual): «»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-002` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-005` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-006` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-008` · `slm|gemma4:e2b-it-q4_K_M|c-con-campo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 571 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-con-campo\|rol` | 576.091 | 800.157 | 0 | 576.091 | 1.65869e+06 | 1898 | 1898/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (0 en esta corrida) no consultan y no cuentan como ausencia.
