# Resumen de la corrida `2026-11-10_191406_sensibilidad-base`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-json-corte-riesgo --solo-otra --seguir-tras-aviso --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta sensibilidad-base --salida /content/resultados-sensibilidad/base`
- **Inicio / fin:** 2026-11-10T19:14:06 / 2026-11-10T19:23:50
- **Código:** `ca4fab05d7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 244 (75 vishing, 169 legítimas); 244 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-json-corte-riesgo\|rol` | 65/75 | 39 | 14 | 3 | 0 | 48/169 | 0/4325 | 221 | 733 | 113/113 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-json-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-002` | legítima | — | — | ok |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-007` | legítima | — | — | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L2 |
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
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L16 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L2 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | FA L18 |
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
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | FA L2 |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L4 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L3 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L2 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L5 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | =R L15 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L10 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L6 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | =R L10 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L22 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | >R L16 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | >R L24 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | =R L15 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | =R L9 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L5 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | >R L20 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | — |
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
| `LAB-familiar-llama-vos` | legítima | — | — | FA L2 |
| `LAB-familiar-peligro` | vishing | 4 | — | <R L1 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L1 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 |
| `LAB-no-bajes-nada` | legítima | — | — | FA L2 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | <R L1 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | <R L1 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L5 |
| `ENT-L-BANCO-004` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L1 |
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
| `ENT-L-VENTAS-002` | legítima | — | — | FA L16 |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | ok |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L21 |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L5 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | FA L3 |
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
| `LEG2-BA-01` | legítima | — | — | FA L4 |
| `LEG2-BA-02` | legítima | — | — | FA L4 |
| `LEG2-BA-03` | legítima | — | — | FA L2 |
| `LEG2-BA-05` | legítima | — | — | FA L6 |
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
| `LEG2-ST-03` | legítima | — | — | FA L2 |
| `LEG2-ST-04` | legítima | — | — | ok |
| `LEG2-ST-05` | legítima | — | — | FA L2 |
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
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L3 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L1 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L1 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L3 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 |
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

- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «No es seguro que un banco o entidad te contacte de esta manera para confirmar un débito; tené cuidado con compartir información de tu cuenta.» — evidencia (cita textual): «te atiendo soy mara del sector de movimientos lo ves en la cuenta sueldo o en la caja de ahorro»
- `CV2-D-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Tené cuidado, te están pidiendo información sensible sobre una transacción sin verificar la identidad de quien te llama.» — evidencia (cita textual): «Buenas, vemos qué puede haber pasado. ¿Te dijeron desde qué banco salió?»
- `CV2-D-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 8: «No debe proporcionar datos sensibles como los últimos cuatro dígitos de su cuenta por teléfono.» — evidencia (cita textual): «Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «Buen día. ¿Qué importe esperabas ver?»
- `CV2-D-L-BANCO-009` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Los estafadores suelen preguntar por los detalles de la tarjeta para intentar obtener información sensible.» — evidencia (cita textual): «Hola, ¿fue con tarjeta de débito o crédito?»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 10: «No debe confirmar nunca datos sensibles como números de cuenta por teléfono, ya que esto es una táctica común para robar información bancaria.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-MEDICO-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 16: «Aunque la conversación parece sobre un resultado de análisis, la solicitud de confirmar datos personales puede ser un intento de obtener información sensible.» — evidencia (cita textual): «te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución con la información personal solicitada.» — evidencia (cita textual): «Hola. ¿Tenés el comprobante de la atención o la fecha aproximada?»
- `CV2-D-L-ORGANISMO_PREVISIONAL-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 18: «Te están pidiendo que uses un acceso diferente al que tienes, lo cual es una táctica común para intentar obtener tus credenciales o datos.» — evidencia (cita textual): «esa credencial corresponde a otro sistema para este trámite usá el acceso que aparece en la página de turnos»
- `CV2-D-L-WHATSAPP-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Los mensajes sobre grupos y cambios de números pueden ser usados para intentar obtener información personal o acceder a cuentas.» — evidencia (cita textual): «Hola. ¿Querés salir del grupo o cambiar el número asociado a tu cuenta?»
- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Los bancos legítimos rara vez inician llamadas sin un contexto previo o sin pedir información sensible de inmediato.» — evidencia (cita textual): «buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Aunque suena a un banco, no podemos confirmar la identidad de quien llama, así que mantente alerta.» — evidencia (cita textual): «Hola, buen día. Te llamo del banco, del sector de seguridad.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 5: «Los bancos legítimos rara vez solicitan datos sensibles como los últimos tres números de DNI por teléfono sin un contexto previo claro.» — evidencia (cita textual): «Gracias, señor Sosa. ¿Me confirma los últimos tres números de su documento?»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 4: «Desconfíe de que le pidan datos personales como el DNI por teléfono sin una previa confirmación.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Las llamadas de prevención de fraudes suelen ser el inicio de estafas donde intentan obtener información sensible.» — evidencia (cita textual): «Buen día, le hablo de prevención de fraudes del banco.»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Desconfía de que te contacten por un número no agendado y que te pidan información sensible a través de una app.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-DELIVERY-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 8: «Te están pidiendo tu número de documento de forma inesperada, lo cual es una táctica común para robar datos personales.» — evidencia (cita textual): «El cartero dejó constancia de que no atendió nadie. ¿Puede ser que el timbre no ande?»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 3: «Desconfía de que te pidan datos personales como el DNI por teléfono, ya que las empresas legítimas rara vez lo solicitan de esa manera inicial.» — evidencia (cita textual): «para validar que hablo con la titular me confirmás tu dni»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es una táctica común para intentar obtener información o pedir dinero.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 11: «No se debe descargar software de fuentes no oficiales ni seguir instrucciones para instalar programas remotamente.» — evidencia (cita textual): «Abajo hay un botón que dice Asistencia remota. Descargá ese programa, solo desde ahí.»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 13: «Te están pidiendo tu DNI para realizar un cambio o promoción, lo cual es una práctica común en intentos de fraude.» — evidencia (cita textual): «para cargarlo necesito validar que hablo con la titular me pasás tu dni»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 16: «Te están pidiendo tu DNI por teléfono para completar una solicitud de servicio, lo cual es una práctica sospechosa.» — evidencia (cita textual): «si querés te dejo la solicitud cargada para eso necesito tu nombre completo y tu dni»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 21: «Te están pidiendo que realices un pago (seña) a una cuenta bancaria para asegurar una tasación, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Quinientos mil pesos. Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Los organismos legítimos no suelen pedir datos personales sensibles por teléfono.» — evidencia (cita textual): «el organismo no pide eso por telefono»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Te están pidiendo que no hagas clic en un enlace o abras un mensaje sospechoso, lo cual es una táctica común de phishing.» — evidencia (cita textual): «no abras ningun sitio del mensaje»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Te están pidiendo que cierres la llamada y te concentres en una aplicación bancaria, lo cual es una táctica común para intentar distraerte y acceder a tus datos.» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Los bancos rara vez llaman de forma inesperada para reportar gastos sin previo aviso; es una táctica común para obtener información sensible.» — evidencia (cita textual): «te llama el banco porque vimos un gasto que no cierra»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Los mensajes sobre consumo de tarjeta son un gancho común para estafas que buscan obtener datos sensibles.» — evidencia (cita textual): «te aviso que hubo un consumo en la tarjeta»
- `LAB-familiar-llama-vos` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «La instrucción de 'corta' de manera abrupta y sin contexto es una táctica común utilizada por estafadores para cortar la comunicación antes de que se pueda verificar la identidad o el motivo real de la llamada.» — evidencia (cita textual): «corta»
- `LAB-mensajeria-no-pases-nada` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Las llamadas que te piden que no contestes suelen ser una táctica para evitar que verifiques la llamada y te presionen a seguir instrucciones fraudulentas.» — evidencia (cita textual): «no le contestes»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Te están pidiendo que instales un programa en tu celular, lo cual es una táctica común para robar tus datos o instalar malware.» — evidencia (cita textual): «no bajes nada»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 5: «Aunque la llamada menciona un intento de compra, es una táctica común para generar urgencia y obtener información. No se debe proporcionar información sensible por teléfono.» — evidencia (cita textual): «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 3: «Desconfía de la urgencia y la solicitud de confirmación de inicios de sesión, ya que los bancos legítimos suelen tener protocolos diferentes.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmar transacciones de esta manera por teléfono; es una táctica común de phishing.» — evidencia (cita textual): «Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarjeta de débito, por ochenta y nueve dólares, en una aerolínea. Solo necesito que me digas si la reconocés o no.»
- `LEG-CC-03` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 11: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener acceso a información o realizar transacciones no deseadas.» — evidencia (cita textual): «Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo de deportes para clientes y te la activan ahí. Yo no te voy a pedir ningún dato ni pago por acá.»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas de suplantación o cobro.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 4: «Los bancos legítimos rara vez solicitan datos sensibles como DNI y fecha de nacimiento por teléfono sin un contexto previo claro y verificado.» — evidencia (cita textual): «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 4: «Desconfía de que un banco solicite el DNI de forma tan directa al inicio de la llamada.» — evidencia (cita textual): «Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, ¿me confirmás tu DNI?»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Aunque el nombre de la entidad suena legítimo, es importante verificar la identidad antes de compartir datos personales.» — evidencia (cita textual): «Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 6: «Los bancos legítimos rara vez solicitan datos sensibles como el DNI de forma tan directa para validar una transacción, y esta pregunta es una táctica común para obtener información personal.» — evidencia (cita textual): «Tu tarjeta de débito se usó ayer a la noche en un cajero de Córdoba. ¿Estuviste allá?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 6: «Desconfía de que le pidan datos personales como el DNI por teléfono sin un contexto claro.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 6: «Descuentos inesperados y urgencias con promociones limitadas son tácticas comunes para intentar obtener información o datos personales.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para intentar obtener información o pedir dinero.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-ST-05` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Desconfía porque no tiene agendado un ticket y no puede verificar la identidad de quien llama.» — evidencia (cita textual): «Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porque no podías entrar a tu cuenta. ¿Hablo con Andrés Romero?»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 2: «Te están pidiendo que leas o compartas un código que recibiste por SMS, lo cual es una táctica común de estafa.» — evidencia (cita textual): «No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación.»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez llaman de forma inesperada para discutir consumos de tarjetas; es una táctica común para obtener información sensible.» — evidencia (cita textual): «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 3: «Te están pidiendo un código, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · línea 4: «Desconfía de solicitudes urgentes de dinero por teléfono, especialmente si no tiene un contexto previo.» — evidencia (cita textual): «Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 599 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-json-corte-riesgo\|rol` | 443.937 | 582.090 | 0 | 443.937 | 1.26724e+06 | 3067 | 1569/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1498 en esta corrida) no consultan y no cuentan como ausencia.
