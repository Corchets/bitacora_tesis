# Resumen de la corrida `2026-11-10_194311_sensibilidad-c-sin-freno`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-sin-freno-corte-riesgo --solo-otra --seguir-tras-aviso --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --hablantes rol --etiqueta sensibilidad-c-sin-freno --salida /content/resultados-sensibilidad/c-sin-freno`
- **Inicio / fin:** 2026-11-10T19:43:11 / 2026-11-10T19:53:07
- **Código:** `ca4fab05d7`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 244 (75 vishing, 169 legítimas); 244 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-sin-freno-corte-riesgo\|rol` | 68/75 | 45 | 10 | 3 | 0 | 65/169 | 0/4325 | 221 | 844 | 133/133 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-sin-freno-corte-riesgo\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-007` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-008` | legítima | — | — | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L2 |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L2 |
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
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | FA L1 |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-001` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L14 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L2 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | FA L10 |
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
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | FA L2 |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | FA L4 |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L2 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L2 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L1 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L2 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L1 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L2 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L1 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L2 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L1 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L7 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | >R L26 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | =R L20 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L10 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | <R L1 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L6 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | L1 |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | <R L8 |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | L8 |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L1 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L2 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | =R L13 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | — |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | — |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | =R L15 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | L2 |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | L1 |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | >R L13 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L1 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | =R L14 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | >R L26 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | L2 |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L3 |
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
| `LAB-banco-niega-el-codigo` | legítima | — | — | FA L2 |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L1 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L1 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L1 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L2 |
| `LAB-familiar-peligro` | vishing | 4 | — | <R L1 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L1 |
| `LAB-giro-sin-plata` | vishing | 3 | — | <R L1 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 |
| `LAB-no-bajes-nada` | legítima | — | — | FA L2 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | <R L1 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | <R L1 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L1 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L2 |
| `ENT-L-BANCO-003` | legítima | — | — | FA L1 |
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
| `ENT-L-ENCUESTA-003` | legítima | — | — | FA L9 |
| `ENT-L-ENCUESTA-004` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-005` | legítima | — | — | ok |
| `ENT-L-ENCUESTA-006` | legítima | — | — | FA L12 |
| `ENT-L-MEDICO-001` | legítima | — | — | ok |
| `ENT-L-MEDICO-002` | legítima | — | — | ok |
| `ENT-L-MEDICO-003` | legítima | — | — | FA L1 |
| `ENT-L-MEDICO-004` | legítima | — | — | ok |
| `ENT-L-SELECCION-001` | legítima | — | — | ok |
| `ENT-L-SELECCION-002` | legítima | — | — | FA L13 |
| `ENT-L-SELECCION-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-001` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-002` | legítima | — | — | FA L6 |
| `ENT-L-SOPORTE-003` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | FA L1 |
| `ENT-L-SOPORTE-006` | legítima | — | — | FA L8 |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | FA L9 |
| `ENT-L-VENTAS-002` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-003` | legítima | — | — | FA L5 |
| `ENT-L-VENTAS-004` | legítima | — | — | FA L4 |
| `ENT-L-VENTAS-005` | legítima | — | — | FA L5 |
| `ENT-L-VENTAS-006` | legítima | — | — | FA L14 |
| `ENT-L-VENTAS-007` | legítima | — | — | FA L13 |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | FA L19 |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | FA L5 |
| `LEG-BA-02` | legítima | — | — | FA L3 |
| `LEG-BA-03` | legítima | — | — | FA L3 |
| `LEG-CC-01` | legítima | — | — | ok |
| `LEG-CC-02` | legítima | — | — | ok |
| `LEG-CC-03` | legítima | — | — | FA L7 |
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
| `LEG2-BA-05` | legítima | — | — | FA L2 |
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
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L9 |
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

- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Los bancos o entidades legítimas rara vez llaman de forma inesperada para confirmar movimientos de débito de esta manera; es una táctica común para obtener información sensible.» — evidencia (cita textual): «te atiendo soy mara del sector de movimientos lo ves en la cuenta sueldo o en la caja de ahorro»
- `CV2-D-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 7: «El banco o entidad legítima rara vez solicita datos sensibles como los últimos cuatro dígitos de una cuenta por teléfono sin una verificación previa más robusta.» — evidencia (cita textual): «Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Los bancos o entidades legítimas rara vez inician una conversación así sin una identificación previa o contexto claro.» — evidencia (cita textual): «Hola, ¿querés consultar el límite disponible o pedir un aumento temporal?»
- `CV2-D-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Los estafadores suelen empezar con preguntas genéricas para intentar obtener información sensible sobre tus cuentas bancarias.» — evidencia (cita textual): «Buenas, vemos qué puede haber pasado. ¿Te dijeron desde qué banco salió?»
- `CV2-D-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 8: «Te están pidiendo información sensible (últimos cuatro dígitos de una cuenta) bajo el pretexto de revisar un pago, lo cual es una táctica común de estafa.» — evidencia (cita textual): «Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Los estafadores suelen empezar preguntando por montos o información para generar urgencia o confusión.» — evidencia (cita textual): «Buen día. ¿Qué importe esperabas ver?»
- `CV2-D-L-BANCO-007` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Los bancos o entidades legítimas rara vez piden información sensible como claves de comercio de esta manera en una llamada inesperada.» — evidencia (cita textual): «Buenas, ¿la ves dentro del detalle de un consumo?»
- `CV2-D-L-BANCO-009` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Los estafadores suelen empezar preguntando por detalles de la tarjeta para intentar obtener información sensible.» — evidencia (cita textual): «Hola, ¿fue con tarjeta de débito o crédito?»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «buenas tardes la constancia es de una cuenta bancaria o de un trámite impositivo»
- `CV2-D-L-FAMILIAR-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Esta pregunta es muy vaga y podría ser un intento de obtener información personal o iniciar una conversación para un posible fraude.» — evidencia (cita textual): «¿Tenés todavía la camioneta el sábado o la usa tu hermano?»
- `CV2-D-L-MEDICO-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 14: «La llamada termina ofreciendo una solución que requiere que PROTEGIDA llame a un número interno, lo cual es una táctica común para obtener acceso a información o realizar acciones no deseadas.» — evidencia (cita textual): «no tengo el detalle técnico desde este teléfono puedo comunicarte con el laboratorio para que revisen la demora»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «No se puede verificar la identidad de quien llama, por lo que es prudente tener precaución.» — evidencia (cita textual): «Hola. ¿Tenés el comprobante de la atención o la fecha aproximada?»
- `CV2-D-L-ORGANISMO_PREVISIONAL-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 10: «La persona que llama no puede verificar información bancaria, lo cual es una señal de alerta en llamadas relacionadas con dinero o cuentas.» — evidencia (cita textual): «No puedo ver saldos ni movimientos bancarios desde esta línea. Solo puedo confirmar la fecha asignada.»
- `CV2-D-L-WHATSAPP-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «No se tiene contexto sobre qué grupo de feria ni por qué se le pide cambiar el número asociado a la cuenta, lo cual es una táctica común de phishing.» — evidencia (cita textual): «Hola. ¿Querés salir del grupo o cambiar el número asociado a tu cuenta?»
- `CV2-D-L-WHATSAPP-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Te están pidiendo que sigas instrucciones con un código que te llega, lo cual es una táctica común para obtener acceso a tu dispositivo o información.» — evidencia (cita textual): «sí esa referencia nos ayuda a buscar el tipo de problema qué teléfono usás»
- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Los bancos legítimos rara vez inician llamadas sin un contexto previo o sin pedir información sensible de inmediato.» — evidencia (cita textual): «buenas tardes te llamo del área de de prevención fraudes del banco me llamo veronica»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Aunque se presenta como el banco, es necesario verificar la identidad antes de compartir cualquier información.» — evidencia (cita textual): «Hola, buen día. Te llamo del banco, del sector de seguridad.»
- `ENT-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Aunque suena legítimo, tené cuidado, ya que las estafas suelen empezar haciéndose pasar por entidades bancarias.» — evidencia (cita textual): «Buenas tardes, le habla Lorena, de prevención de fraudes del banco.»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Desconfíe de que le pidan datos personales sensibles como el DNI por teléfono, ya que las instituciones legítimas rara vez lo solicitan de esa manera inicial.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Las llamadas de prevención de fraudes suelen ser el inicio de estafas donde intentan obtener información sensible.» — evidencia (cita textual): «Buen día, le hablo de prevención de fraudes del banco.»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Es común que los estafadores intenten hacerse pasar por el banco para obtener información sensible.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo del banco, por tu app.»
- `ENT-L-ENCUESTA-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 9: «Te están llamando con un número aleatorio y te están presionando para que aceptes participar en una encuesta, lo cual es una táctica común de phishing.» — evidencia (cita textual): «Los números se generan al azar dentro de la provincia. No tengo tu nombre en una lista, solo el que me dijiste vos.»
- `ENT-L-ENCUESTA-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 12: «Aunque la llamada se centra en una encuesta, la mención de problemas con la tarjeta y la entrega de información sensible es una táctica común para generar confianza y luego intentar obtener datos.» — evidencia (cita textual): «lamento lo de la tarjeta te dieron toda la información del reintegro»
- `ENT-L-MEDICO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «No se puede verificar la legitimidad de la llamada, es necesario seguir escuchando para determinar si es una estafa.» — evidencia (cita textual): «Buenas tardes, te llamo del laboratorio Bioanálisis.»
- `ENT-L-SELECCION-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 13: «Te están pidiendo un código de acceso para una evaluación, lo cual es una táctica común para obtener información o intentar engañarte.» — evidencia (cita textual): «no no ese código no me lo pases ni a mí ni a nadie es tu clave para entrar a la evaluación la usás vos cuando la vayas a hacer»
- `ENT-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Desconfía de llamadas no solicitadas de soporte técnico y que mencionan reclamos para intentar obtener información personal o instalar software.» — evidencia (cita textual): «hola buen día te habla leonel de soporte técnico de fibrasur te llamo por el reclamo 3349 de falta de serbicio»
- `ENT-L-SOPORTE-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Desconfía de que una empresa legítima pida datos sensibles como el DNI por teléfono sin una verificación previa.» — evidencia (cita textual): «me imagino para validar la garantía necesito el dni del titular de la factura»
- `ENT-L-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas de suplantación o cobro.» — evidencia (cita textual): «Hola, ¿Tobías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `ENT-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Aunque suena a soporte, es una táctica común para iniciar una estafa pidiendo información o acceso a cuentas.» — evidencia (cita textual): «Hola, buenas tardes. Te hablo de soporte de Factura Simple, por el ticket que abriste esta mañana.»
- `ENT-L-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 8: «Te están pidiendo datos personales sensibles como el número de documento para un envío, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Para el envío, ¿me confirmás tu número de documento?»
- `ENT-L-VENTAS-001` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 9: «Las ofertas de planes de telefonía con cambios de cuotas y precios inesperados son comunes en intentos de venta o estafas.» — evidencia (cita textual): «tenés el plan de cinco gigas y te podemos pasar a quince por la misma cuota durante seis meses»
- `ENT-L-VENTAS-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 14: «Te están pidiendo datos personales sensibles (nombre completo y DNI) bajo el pretexto de ofrecer un servicio de internet.» — evidencia (cita textual): «si querés te dejo la solicitud cargada para eso necesito tu nombre completo y tu dni»
- `ENT-L-VENTAS-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 5: «Las llamadas que inician con información genérica sobre seguros o beneficios suelen ser el primer paso para intentar obtener datos personales o instalar software malicioso.» — evidencia (cita textual): «te llamo porque como clienta tenés un seguro de hogar con el primer mes bonificado cubre incendio robo y daños por agua te cuento dos minutos»
- `ENT-L-VENTAS-004` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Tené cuidado, porque te están ofreciendo un servicio sin que hayas solicitado nada.» — evidencia (cita textual): «Te quería ofrecer internet para tu casa, con...»
- `ENT-L-VENTAS-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 5: «Desconfía de que le pidan datos personales como el DNI por teléfono, especialmente si la comunicación no es totalmente verificable.» — evidencia (cita textual): «Por eso te llamo, te quedó a mitad de camino. Faltaba validar la identidad. ¿Me confirmás tu DNI?»
- `ENT-L-VENTAS-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 14: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener datos o redirigirte a otra llamada.» — evidencia (cita textual): «Llamá al 0800 que está en tu factura, decí ese número y te activan la promo ellos. Yo no te pido nada por acá.»
- `ENT-L-VENTAS-007` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 13: «Es común que estafadores soliciten datos personales sensibles como DNI y su sueldo bajo el pretexto de una oferta comercial.» — evidencia (cita textual): «tu nombre completo el dni y más o menos cuánto ganás por mes en blanco»
- `ENT-L-VENTAS-009` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 19: «Te están pidiendo realizar un pago (seña) a una cuenta bancaria para asegurar una operación, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Podés venir y pagarla en caja, o transferirla a la cuenta de la concesionaria.»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Es una señal de alerta que las entidades legítimas no solicitan datos sensibles por teléfono.» — evidencia (cita textual): «el organismo no pide eso por telefono»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Te están pidiendo que no hagas clic en un enlace o abras un mensaje sospechoso, lo cual es una táctica común de phishing.» — evidencia (cita textual): «no abras ningun sitio del mensaje»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Te están pidiendo que cierres la llamada y que revises una aplicación del banco, lo cual es una táctica común para intentar que hagas clic en un enlace o compartas información sensible.» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Los bancos rara vez contactan por llamada para pedirte que hagas clic en algo o reveles información sensible de inmediato.» — evidencia (cita textual): «te llama el banco porque vimos un gasto que no cierra»
- `LAB-banco-niega-el-codigo` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Te están pidiendo que cortes la llamada y revises una aplicación, lo cual es una táctica común para intentar distraerte y obtener acceso a tus cuentas.» — evidencia (cita textual): «corta y revisa la aplicacion oficial»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Los mensajes sobre consumo de tarjeta son un método común para intentar obtener datos sensibles o hacer que la persona realice una acción inmediata.» — evidencia (cita textual): «te aviso que hubo un consumo en la tarjeta»
- `LAB-familiar-llama-vos` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «La instrucción de 'corta' de manera abrupta y sin contexto es una táctica común utilizada en llamadas de estafa para presionar a la víctima a actuar sin pensar.» — evidencia (cita textual): «corta»
- `LAB-mensajeria-no-pases-nada` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «La instrucción de no contestar una llamada no solicitada es una táctica común utilizada por estafadores.» — evidencia (cita textual): «no le contestes»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Te están pidiendo que instales un programa en tu celular, lo cual es una táctica común para robar tus datos o instalar malware.» — evidencia (cita textual): «no bajes nada»
- `LEG-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 5: «Aunque la llamada menciona un intento de compra, es una táctica común para generar urgencia y obtener información. No se debe proporcionar información sensible por teléfono.» — evidencia (cita textual): «Detectamos un intento de compra con tu tarjeta de crédito terminada en cuatro cuatro uno siete, por ciento ochenta y siete mil quinientos pesos, en un comercio online, hoy a las dos y media de la tarde. ¿La reconocés?»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 3: «Los bancos rara vez solicitan confirmación de inicios de sesión por teléfono de esta manera; es una táctica común para robar credenciales.» — evidencia (cita textual): «Carla, te llamo de Banco Andino, de seguridad. Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 3: «Los bancos legítimos rara vez solicitan confirmar transacciones de esta manera por teléfono; es una táctica común para obtener datos de la tarjeta.» — evidencia (cita textual): «Juan Pablo, te llamo de Banco Andino, de prevención de fraudes. Tenemos una compra en el exterior con tu tarjeta de débito, por ochenta y nueve dólares, en una aerolínea. Solo necesito que me digas si la reconocés o no.»
- `LEG-CC-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 7: «Te están pidiendo que llames a un número específico para activar una promoción, lo cual es una táctica común para obtener acceso a información o realizar transacciones no deseadas.» — evidencia (cita textual): «Hacé una cosa: llamá al cero ochocientos que figura en tu factura, pedí por la promo de deportes para clientes y te la activan ahí. Yo no te voy a pedir ningún dato ni pago por acá.»
- `LEG-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 1: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas de suplantación o cobro.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Los bancos legítimos rara vez solicitan datos personales sensibles como DNI y fecha de nacimiento por teléfono sin una previa verificación o contexto claro.» — evidencia (cita textual): «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Los bancos rara vez solicitan el DNI por teléfono de esta manera para confirmar transacciones; es una táctica común para obtener datos personales.» — evidencia (cita textual): «Carla, registramos dos ingresos a tu homebanking desde un dispositivo nuevo esta madrugada. Antes de seguir, ¿me confirmás tu DNI?»
- `LEG2-BA-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Aunque menciona un banco, es necesario verificar la legitimidad de la llamada antes de compartir información personal.» — evidencia (cita textual): «Buenas tardes, te habla Lorena, de prevención de fraudes de Banco Andino. ¿Me decís tu nombre completo, por favor?»
- `LEG2-BA-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Aunque el nombre del banco es legítimo, las llamadas de prevención de fraudes suelen ser una táctica común para obtener información sensible.» — evidencia (cita textual): «Buen día, te habla Silvina, de Banco Andino, de prevención de fraudes. ¿Me comunico con Diego Herrera?»
- `LEG2-CC-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Desconfía de que le pidan datos personales como el DNI por teléfono, especialmente si no tiene un contexto claro de qué es Telnor.» — evidencia (cita textual): «Por eso te llamaba. Te faltó validar la identidad. ¿Me confirmás tu DNI?»
- `LEG2-CC-06` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 6: «Las ofertas repentinas y urgentes, especialmente cuando se pide llamar a un número específico para activar algo, son una táctica común de estafa.» — evidencia (cita textual): «Sofía, te ofrezco el pack de deportes con cuarenta por ciento de descuento por tres meses. Entra todo el fútbol y la promo es hasta el viernes nomás.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Te están contactando sobre un objeto que dejaste, lo cual es un inicio común para estafas de suplantación o cobro.» — evidencia (cita textual): «Hola, ¿Matías? Te hablo de TecnoFix, el local de la calle Muñecas. Dejaste una notebook la semana pasada.»
- `LEG2-ST-05` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Desconfía porque no tiene agendado un ticket y no puede verificar la identidad de quien llama.» — evidencia (cita textual): «Hola, buenas tardes, te habla Julieta, de soporte de Tiendita Online. Te llamo por el ticket que abriste porque no podías entrar a tu cuenta. ¿Hablo con Andrés Romero?»
- `LG-SUPPORT-INFO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 9: «La entidad te pide que sigas instrucciones en un correo electrónico para cambiar tu clave, lo cual es una táctica común para obtener acceso a tus cuentas.» — evidencia (cita textual): «No hace falta. Nosotros no vemos tu clave y nadie de la mesa de ayuda te la va a pedir.»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 2: «Te están pidiendo que leas o compartas un código que recibiste por SMS, lo cual es una táctica común de estafa.» — evidencia (cita textual): «No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación.»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 3: «Los bancos rara vez llaman por un consumo sospechoso de esta manera; es una táctica común para obtener información sensible.» — evidencia (cita textual): «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 3: «Te están pidiendo un código, lo cual es una táctica común de estafa para obtener acceso a tus cuentas.» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · línea 4: «Te están pidiendo transferir dinero bajo un pretexto de urgencia, lo cual es una táctica común en estafas.» — evidencia (cita textual): «Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-002` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-003` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-sin-freno-corte-riesgo|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 442 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-sin-freno-corte-riesgo\|rol` | 410.287 | 595.178 | 0 | 410.287 | 1.02381e+06 | 2644 | 1360/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1284 en esta corrida) no consultan y no cuentan como ausencia.
