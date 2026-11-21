# Resumen de la corrida `2026-11-08_000115_etapa-2-c-json-corte`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --prompts c-json-corte --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --seguir-tras-aviso --hablantes rol --etiqueta etapa-2-c-json-corte --salida /content/resultados-etapa-2/c-json-corte`
- **Inicio / fin:** 2026-11-08T00:01:15 / 2026-11-08T00:23:04
- **Código:** `d127953fcc`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `diagnostico-completo`
- **Casos:** 244 (75 vishing, 169 legítimas); 244 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-json-corte\|rol` | 42/75 | 26 | 10 | 5 | 0 | 23/169 | 0/4325 | 277 | 340 | 65/65 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|c-json-corte\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L7 |
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
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | ok |
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
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L29 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | =R L18 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | — |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L11 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L3 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | >R L17 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | =R L13 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L4 |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | >R L17 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | >R L17 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | — |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | — |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | — |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | — |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | — |
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
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | — |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | — |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | — |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | — |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | — |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | — |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | <R L1 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | <R L1 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
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
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | <R L1 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | <R L1 |
| `ENT-L-BANCO-001` | legítima | — | — | FA L3 |
| `ENT-L-BANCO-002` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-003` | legítima | — | — | ok |
| `ENT-L-BANCO-004` | legítima | — | — | FA L6 |
| `ENT-L-BANCO-005` | legítima | — | — | FA L4 |
| `ENT-L-BANCO-006` | legítima | — | — | FA L8 |
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
| `ENT-L-SOPORTE-001` | legítima | — | — | ok |
| `ENT-L-SOPORTE-002` | legítima | — | — | ok |
| `ENT-L-SOPORTE-003` | legítima | — | — | ok |
| `ENT-L-SOPORTE-004` | legítima | — | — | ok |
| `ENT-L-SOPORTE-005` | legítima | — | — | ok |
| `ENT-L-SOPORTE-006` | legítima | — | — | ok |
| `ENT-L-TRAMITE-001` | legítima | — | — | ok |
| `ENT-L-TRAMITE-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-001` | legítima | — | — | ok |
| `ENT-L-VENTAS-002` | legítima | — | — | ok |
| `ENT-L-VENTAS-003` | legítima | — | — | ok |
| `ENT-L-VENTAS-004` | legítima | — | — | ok |
| `ENT-L-VENTAS-005` | legítima | — | — | ok |
| `ENT-L-VENTAS-006` | legítima | — | — | ok |
| `ENT-L-VENTAS-007` | legítima | — | — | ok |
| `ENT-L-VENTAS-008` | legítima | — | — | ok |
| `ENT-L-VENTAS-009` | legítima | — | — | ok |
| `ENT-L-VENTAS-010` | legítima | — | — | ok |
| `ENT-L-VENTAS-011` | legítima | — | — | ok |
| `ENT-L-VENTAS-012` | legítima | — | — | ok |
| `LEG-BA-01` | legítima | — | — | ok |
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
| `LEG2-BA-02` | legítima | — | — | FA L6 |
| `LEG2-BA-03` | legítima | — | — | ok |
| `LEG2-BA-05` | legítima | — | — | ok |
| `LEG2-CC-01` | legítima | — | — | ok |
| `LEG2-CC-04` | legítima | — | — | ok |
| `LEG2-CC-05` | legítima | — | — | ok |
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
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L6 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | — |
| `TR-05-asado-con-transferencia` | legítima | — | — | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L4 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L6 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L7 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 7: «Te están pidiendo que les digas un código que aparece en un débito para verificar la transacción.» — evidencia (cita textual): «dice débito tarjeta pero abajo aparece un código que no entiendo»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 10: «Cuidado, te están pidiendo los últimos cuatro números de tu cuenta bancaria. No des esa información.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `ENT-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 3: «Tené cuidado, te están pidiendo tu DNI y fecha de nacimiento, datos sensibles que no debes compartir por teléfono.» — evidencia (cita textual): «antes de darte información necesito validar que hablo con el titular me me decís tu dni y tu fecha de nacimiento»
- `ENT-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 4: «Desconfía de la llamada porque menciona movimientos inusuales en su cuenta bancaria.» — evidencia (cita textual): «Registramos dos ingresos a tu home banking desde un celular que no tenías registrado, esta madrugada.»
- `ENT-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 6: «Te están pidiendo tu DNI para validar tu identidad, lo cual es una táctica común de estafa.» — evidencia (cita textual): «valeria valeria para validar su identidad me dice su dni»
- `ENT-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 4: «Te están pidiendo confirmar tu documento para validar la información, lo cual es una táctica común de estafa.» — evidencia (cita textual): «¿Me confirma su documento para validar?»
- `ENT-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 8: «Te están pidiendo que leas un código que te llegó, lo cual es una táctica común para robar tus datos.» — evidencia (cita textual): «No, no, pará. No me lo leas. Ese código es solo para cargarlo en tu teléfono.»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Desconfía de ofertas inesperadas que piden datos personales, ya que es una táctica común de estafa.» — evidencia (cita textual): «me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Tené cuidado, porque las llamadas que mencionan deudas o embargos suelen ser intentos de estafa.» — evidencia (cita textual): «me llego un mail de una deuda y un embargo»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Te están pidiendo que cierres la llamada y revises la aplicación del banco, lo cual es una táctica común para intentar que hagas clic en un enlace o ingreses datos.» — evidencia (cita textual): «corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Tené cuidado, te están llamando diciendo que hay un gasto que no cierra, lo cual es una táctica común para robarte información.» — evidencia (cita textual): «te llama el banco porque vimos un gasto que no cierra»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Te están avisando sobre un consumo en tu tarjeta, lo cual es una táctica común para intentar obtener información sensible.» — evidencia (cita textual): «te aviso que hubo un consumo en la tarjeta»
- `LAB-familiar-llama-vos` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Tené cuidado, las estafas suelen usar el miedo o la urgencia para pedirte información o dinero.» — evidencia (cita textual): «me llamaron y dijeron que un familiar estaba en peligro»
- `LAB-mensajeria-no-pases-nada` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 2: «Te están pidiendo que no contestes la llamada, lo cual es una táctica común para evitar que verifiques la llamada.» — evidencia (cita textual): «no le contestes»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Desconfía, ya que te están pidiendo que descargues un programa y les muestres la pantalla de tu celular, lo cual es una táctica común para robar información o instalar malware.» — evidencia (cita textual): «me llamaron para que baje un programa y les muestre el celular»
- `LEG-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 3: «Desconfía de la urgencia y la solicitud de confirmación de inicios de sesión, ya que esto es una táctica común de phishing.» — evidencia (cita textual): «Registramos dos inicios de sesión en tu home banking desde un dispositivo nuevo esta madrugada y queríamos confirmar si fuiste vos.»
- `LEG2-BA-01` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 4: «Te están pidiendo tu DNI y fecha de nacimiento, lo cual es información sensible que no debes compartir por teléfono.» — evidencia (cita textual): «Gonzalo, necesito validar tu identidad antes de darte información. ¿Me decís tu DNI y tu fecha de nacimiento?»
- `LEG2-BA-02` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 6: «Te están pidiendo que cortes la llamada y llames a un número para que te den datos de tu tarjeta, lo cual es una táctica de estafa.» — evidencia (cita textual): «Hagamos así: cortá y llamá vos al número del dorso de tu tarjeta. Pedí por seguridad y dales el número de caso siete tres cuatro cuatro cero.»
- `LEG2-ST-03` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 4: «Tené cuidado, te están pidiendo tu DNI para registrar una notebook que dejaste en un local.» — evidencia (cita textual): «Para dejarla registrada a tu nombre, ¿me confirmás el DNI que dejaste?»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 1: «Desconfía del código recibido por SMS, ya que no lo solicitó.» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 4: «Desconfía de la llamada porque el banco generalmente no llama de forma inesperada para preguntar por consumos de tarjeta.» — evidencia (cita textual): «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 3: «Te están pidiendo un código, lo cual es una señal de alerta común en estafas.» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · línea 7: «Desconfía de la solicitud de transferencia de dinero por teléfono, ya que es una táctica común en estafas.» — evidencia (cita textual): «Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `CV2-D-V-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-BANCO-012` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-FAMILIAR-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-001` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-002` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-003` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-004` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-005` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-006` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-007` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `TR-04-pedido-tras-charla-larga` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|c-json-corte|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 430 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Costos por componente hasta el aviso

Modo de término: `diagnostico-completo`.
Diagnóstico de conversación completa: cada caso aporta el prefijo hasta el aviso y, por separado, la conversación completa; ninguno de los dos se mezcla con el costo operativo hasta el aviso.

| Configuración | ms hasta aviso | ms conversación completa | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|c-json-corte\|rol` | 1.158.176 | 1.307.524 | 0 | 1.158.176 | 3.16252e+06 | 3813 | 3813/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (0 en esta corrida) no consultan y no cuentan como ausencia.
