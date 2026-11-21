# Resumen de la corrida `2026-11-18_222108_revision-producto-c-consejos`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-consejos-corte-riesgo --solo-otra --seguir-tras-aviso --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta revision-producto-c-consejos --salida /content/resultados-revision-producto/c-consejos`
- **Inicio / fin:** 2026-11-18T22:21:08 / 2026-11-18T22:30:58
- **Código:** `30746d3f38`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 244 (75 vishing, 169 legítimas); 244 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-consejos-corte-riesgo\|rol` | 69/75 | 45 | 10 | 3 | 0 | 41/169 | 0/4325 | 223 | 699 | 110/110 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-consejos-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-002` | legítima | — | — | ok |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | ok |
| `CV2-D-L-BANCO-005` | legítima | — | — | ok |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-007` | legítima | — | — | FA L2 |
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
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-001` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L2 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | ok |
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
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L6 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L3 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L5 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L4 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L5 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | <R L1 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L7 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | <R L8 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L16 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L17 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | >R L16 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L14 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | =R L15 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L4 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | =R L12 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L9 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L4 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L9 |
| `LAB-acceso-remoto` | vishing | 3 | — | <R L1 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-anses-beneficio` | vishing | 3 | — | <R L1 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L2 |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L2 |
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
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | <R L1 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L1 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 |
| `LAB-no-bajes-nada` | legítima | — | — | FA L2 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | <R L1 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | <R L1 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L11 |
| `ENT-L-BANCO-004` | legítima | — | — | FA L6 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L2 |
| `ENT-L-DELIVERY-001` | legítima | — | — | ok |
| `ENT-L-DELIVERY-002` | legítima | — | — | ok |
| `ENT-L-DELIVERY-003` | legítima | — | — | ok |
| `ENT-L-DELIVERY-004` | legítima | — | — | FA L8 |
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
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L11 |
| `ENT-L-SOPORTE-006` | legítima | — | — | ok |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L13 |
| `ENT-L-VENTAS-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L19 |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L7 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | ok |
| `LEG-CC-01` | legítima | — | — | ok |
| `LEG-CC-02` | legítima | — | — | ok |
| `LEG-CC-03` | legítima | — | — | FA L11 |
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
| `LEG2-BA-01` | legítima | — | — | ok |
| `LEG2-BA-02` | legítima | — | — | FA L6 |
| `LEG2-BA-03` | legítima | — | — | ok |
| `LEG2-BA-05` | legítima | — | — | FA L8 |
| `LEG2-CC-01` | legítima | — | — | ok |
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
| `LEG2-ST-03` | legítima | — | — | FA L4 |
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
| `LG-BANK-VERIF-01-e01` | legítima | — | — | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L2 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L3 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | <R L7 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L1 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L1 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | — |
| `TR-05-asado-con-transferencia` | legítima | — | — | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L3 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L3 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L9 |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «No se debe proporcionar información sensible de la cuenta por teléfono; los bancos y organismos legítimos no solicitan datos de esa manera.» — evidencia (cita textual): «te atiendo soy mara del sector de movimientos lo ves en la cuenta sueldo o en la caja de ahorro»
- `CV2-D-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «Buen día. ¿Qué importe esperabas ver?»
- `CV2-D-L-BANCO-007` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Tené cuidado, no compartas claves ni información sensible por teléfono, aunque parezca que es de un banco.» — evidencia (cita textual): «Buenas, ¿la ves dentro del detalle de un consumo?»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 10: «No se debe proporcionar datos sensibles como los últimos cuatro números de una cuenta bancaria por teléfono.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «Hola. ¿Tenés el comprobante de la atención o la fecha aproximada?»
- `CV2-D-L-SOPORTE-004` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Te están pidiendo información personal o de acceso a una compra antigua, lo cual puede ser un intento de obtener datos sensibles.» — evidencia (cita textual): «¿Tenés el correo de confirmación de esa compra?»
- `CV2-D-L-WHATSAPP-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Las preguntas sobre acceso a cuentas o pantallas son comunes en intentos de phishing para obtener información o acceso a dispositivos.» — evidencia (cita textual): «¿Puede entrar a WhatsApp o le quedó la pantalla de registro?»
- `CV2-D-L-WHATSAPP-002` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «No se tiene contexto sobre qué grupo o cuenta se esté mencionando, lo que abre la posibilidad de un intento de suplantación o phishing.» — evidencia (cita textual): «Hola. ¿Querés salir del grupo o cambiar el número asociado a tu cuenta?»
- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los bancos y organismos legítimos no suelen solicitar el DNI y la fecha de nacimiento por teléfono para validar la identidad.» — evidencia (cita textual): «antes de darte información necesito validar que hablo con el titular me me decís tu dni y tu fecha de nacimiento»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Los bancos legítimos no suelen contactar por teléfono para informar sobre movimientos inusuales de esta manera.» — evidencia (cita textual): «Registramos dos ingresos a tu home banking desde un celular que no tenías registrado, esta madrugada.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 11: «El solicitante pide confirmación para liberar una transacción, lo cual es una táctica común para obtener información sensible.» — evidencia (cita textual): «Si usted me confirma que la reconoce, la libero ahora.»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 6: «Te están pidiendo información y te están presionando sobre una transferencia no autorizada, lo cual es una táctica común de estafa.» — evidencia (cita textual): «justamente por eso la llamo inició una una transferencia de un millón doscientos mil pesos a un cbu que no tenía agendado»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los bancos y organismos legítimos no suelen solicitar documentos personales completos por teléfono de esta manera.» — evidencia (cita textual): «¿Me confirma su documento para validar?»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-DELIVERY-004` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 8: «Los organismos oficiales no suelen solicitar el DNI por teléfono de esta manera.» — evidencia (cita textual): «OTRA: ¿Me confirmás tu número de documento para dejarlo asentado a tu nombre?»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los organismos legítimos rara vez solicitan el DNI por teléfono de esta manera para validar la titularidad.» — evidencia (cita textual): «para validar que hablo con la titular me confirmás tu dni»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 1: «Si no esperabas una llamada sobre un objeto que dejaste, es mejor verificar la identidad de TecnoFix por otros medios antes de dar cualquier información.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 11: «No se debe descargar software por instrucciones de un proveedor de servicios o entidad oficial por teléfono.» — evidencia (cita textual): «Abajo hay un botón que dice Asistencia remota. Descargá ese programa, solo desde ahí.»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 13: «No se debe proporcionar el DNI por teléfono a una compañía de celular bajo estas circunstancias.» — evidencia (cita textual): «para cargarlo necesito validar que hablo con la titular me pasás tu dni»
- `ENT-L-VENTAS-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 14: «Las promociones inesperadas y la indicación de llamar a un número externo para activar algo son comunes en intentos de fraude.» — evidencia (cita textual): «Llamá al 0800 que está en tu factura, decí ese número y te activan la promo ellos. Yo no te pido nada por acá.»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 19: «No se debe realizar ninguna transferencia o pago a cuentas desconocidas por teléfono.» — evidencia (cita textual): «Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «El organismo legítimo no solicita datos personales sensibles por teléfono.» — evidencia (cita textual): «el organismo no pide eso por telefono»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Te están pidiendo que no hagas clic en un enlace o accedas a algo por mensaje, lo cual es una táctica común de estafa.» — evidencia (cita textual): «no abras ningun sitio del mensaje»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 1: «Te están pidiendo que cortes la llamada y te fijes en una aplicación, lo cual es una táctica común para intentar acceder a tus cuentas.» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 1: «Los bancos rara vez llaman de forma inesperada para informar sobre gastos sin previo aviso, y es mejor verificar la identidad por otros medios.» — evidencia (cita textual): «te llama el banco porque vimos un gasto que no cierra»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 1: «Los bancos y organismos legítimos rara vez inician llamadas así sin una verificación previa.» — evidencia (cita textual): «te aviso que hubo un consumo en la tarjeta»
- `LAB-mensajeria-no-pases-nada` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Si alguien te pide que no contestes a una llamada inesperada, es una señal de alerta, ya que las estafas a menudo intentan evitar que verifiques la llamada.» — evidencia (cita textual): «no le contestes»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Te están pidiendo que instales un programa en tu celular, lo cual es una táctica común de estafa.» — evidencia (cita textual): «no bajes nada»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 7: «Aunque la llamada menciona no pedir claves ni códigos, el intento de generar urgencia para bloquear la tarjeta y reemplazarla es una táctica común de estafa.» — evidencia (cita textual): «Lo que te propongo es bloquear la tarjeta ahora y te enviamos una nueva a tu domicilio en siete a diez días hábiles. ¿Estás de acuerdo?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmación de inicios de sesión por teléfono de esta manera; es una táctica común de phishing.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-CC-03` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 11: «Aunque la llamada sugiere una acción, es necesario verificar la legitimidad del número al que se le pide llamar antes de seguir los pasos.» — evidencia (cita textual): «Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo de deportes para clientes y te la activan ahí.»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 1: «Si no esperabas una llamada sobre un objeto que dejaste, es mejor verificar la identidad de TecnoFix por otros medios.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 6: «El operador le pide que corte la llamada y llame a un número, lo cual es una táctica común para obtener información sensible.» — evidencia (cita textual): «Hagamos así: cortá y llamá vos al número del dorso de tu tarjeta. Pedí por seguridad y dales el número de caso siete tres cuatro cuatro cero.»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 8: «Los bancos o organismos legítimos no suelen solicitar información sensible o hacer afirmaciones alarmantes de esta manera para pedir datos de la tarjeta.» — evidencia (cita textual): «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 6: «Desconfía de que le pidan datos personales como el DNI por teléfono sin un contexto claro.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 6: «Te están ofreciendo una promoción que suena muy atractiva y urgente, pero te piden que llames a un número que ellos te dan, lo cual es una táctica común.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Desconfía de que te pidan datos personales como el DNI para un servicio que no esperabas.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el DNI que dejaste?»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 2: «Te están pidiendo que leas o compartas un código que recibiste por SMS, lo cual es una táctica común de estafa.» — evidencia (cita textual): «No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación.»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «Aunque se presente como un banco, es importante verificar la identidad y no proporcionar información sensible por teléfono.» — evidencia (cita textual): «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 3: «No se debe compartir códigos por teléfono, ya que esto es una táctica común de estafa.» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · línea 4: «Te están pidiendo transferir dinero por una supuesta emergencia con la luz, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-004` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20
- `TR-04-pedido-tras-charla-larga` · `slm|gemma4:e2b-it-q4_K_M|c-consejos-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 418 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-consejos-corte-riesgo\|rol` | 450.098 | 589.059 | 0 | 450.098 | 1.49043e+06 | 3079 | 1576/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1503 en esta corrida) no consultan y no cuentan como ausencia.
