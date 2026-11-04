# Resumen de la corrida `2026-11-04_193946_prompt-v3-a-solo-y-con-indicio`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --prompts v3 --hablantes ab --num-ctx 4096 --seed 42 --sin-reglas --filtro-tito --tito-real --etiqueta prompt-v3-a-solo-y-con-indicio --salida /content/resultados-prompt-v3/a`
- **Inicio / fin:** 2026-11-04T19:39:46 / 2026-11-04T20:10:59
- **Código:** `a42e1b5504`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|v3\|ab` | 65/75 | 43 | 20 | 1 | 0 | 47/75 | 0/1680 | 556 | 1.020 | 108/112 | 0 |
| `tito-slm\|gemma4:e2b-it-q4_K_M\|v3\|ab` | 63/75 | 36 | 23 | 3 | 0 | 30/75 | 0/2006 | 135 | 950 | 91/93 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|gemma4:e2b-it-q4_K_M\|v3\|ab` · **C2** `tito-slm\|gemma4:e2b-it-q4_K_M\|v3\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L12 | FA L12 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L7 | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | FA L6 | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L8 | FA L8 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L8 | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L6 | FA L9 |
| `CV2-D-L-BANCO-007` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | ok | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | FA L5 | ok |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L10 | FA L10 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | FA L17 | ok |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | ok | ok |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | ok | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | FA L6 | FA L8 |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L8 | FA L11 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | FA L7 | FA L10 |
| `CV2-D-L-MEDICO-001` | legítima | — | — | FA L19 | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L16 | FA L16 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | FA L4 | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | FA L7 | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L4 | FA L17 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | FA L19 | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | ok | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | FA L11 | FA L12 |
| `CV2-D-L-PREMIO-003` | legítima | — | — | FA L15 | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | FA L18 | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | FA L6 | ok |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | ok | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | FA L11 | FA L11 |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | FA L10 | FA L10 |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | FA L15 | FA L22 |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | FA L10 | FA L10 |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L3 | FA L16 |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | FA L2 | ok |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L29 | <R L29 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L10 | <R L10 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 | =R L19 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L8 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L2 | <R L5 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L8 | <R L10 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L6 | <R L11 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | <R L6 | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L9 | <R L10 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 | <R L7 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L5 | L12 |
| `CV2-D-V-BANCO-012` | vishing | — | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 | >R L17 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L7 | <R L14 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | =R L22 | =R L22 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | <R L18 | <R L18 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | <R L19 | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L2 | <R L11 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | =R L9 | =R L9 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | <R L8 | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L8 | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | <R L8 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L12 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | >R L15 | >R L16 |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L10 | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L10 | <R L12 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | =R L14 | =R L14 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L11 | <R L10 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L10 | <R L10 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | <R L7 | <R L7 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 | <R L8 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L9 | <R L9 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L11 | <R L10 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L24 | <R L24 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L1 | FA L5 |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L2 | FA L3 |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L3 | FA L3 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L3 | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 | FA L3 |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok | ok |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L2 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 | FA L6 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L2 | FA L9 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L11 | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L3 | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 | <R L4 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | <R L7 | <R L7 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L5 | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L23 | <R L21 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L13 | FA L14 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L4 | <R L5 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L5 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 12: «Te están pidiendo confirmar el nombre del titular para cargar un desconocimiento, lo cual podría ser para autorizar una transacción o acceder a información de tu cuenta.» — evidencia (cita textual): «12. B: entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo los últimos cuatro dígitos de la cuenta para identificarla, lo cual es información sensible que podría usarse para acceder a tus fondos.» — evidencia (cita textual): «A: Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-003` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «Te están pidiendo tu nombre completo y el mes de vencimiento de la tarjeta, datos que pueden ser usados para acceder a tu cuenta o realizar operaciones no autorizadas.» — evidencia (cita textual): «B: Para identificarte, ¿me confirmás tu nombre completo y el mes de vencimiento de esa tarjeta?»
- `CV2-D-L-BANCO-004` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo los últimos cuatro dígitos de tu cuenta para buscar ingresos, lo cual podría ser para acceder a tus fondos.» — evidencia (cita textual): «Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»
- `CV2-D-L-BANCO-005` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo los últimos cuatro dígitos de la cuenta para encontrarla, lo cual es información sensible que podría usarse para acceder a tus cuentas.» — evidencia (cita textual): «8. B: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «Te están pidiendo que confirmes el número de cuenta para poder revisar movimientos, lo cual podría ser un intento de acceder a tu información bancaria.» — evidencia (cita textual): «B: Podemos recorrer los últimos movimientos. ¿La cuenta termina en 2609?»
- `CV2-D-L-BANCO-009` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están pidiendo que confirmes o repitas un PIN que usaste, lo cual podría permitirles acceder a tus cuentas o realizar transacciones no autorizadas.» — evidencia (cita textual): «Uno pendiente por 27.900. Me acuerdo que marqué el PIN y después quedó cargando.»
- `CV2-D-L-BANCO-010` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo los últimos cuatro números de tu cuenta bancaria para ubicar un comprobante, lo cual podría ser para acceder a tus fondos.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-DELIVERY-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 17: «Te están pidiendo que firmes un recibo de una compra a nombre de otra persona, lo cual podría ser para autorizar la entrega de un paquete o transacción.» — evidencia (cita textual): «17. A: puede firmar con su nombre aunque la compra esté a nombre de ocampo»
- `CV2-D-L-ESCUELA-004` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «Te están pidiendo que actualices tu correo en la ficha de estudiante, lo cual podría ser para acceder a información personal o cuentas.» — evidencia (cita textual): «6. B: Gracias. ¿Querés actualizar el correo en la ficha de estudiante?»
- `CV2-D-L-FAMILIAR-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo que transfieras dinero ($11.700) bajo la excusa de dividir un gasto, lo cual es una táctica común de estafa.» — evidencia (cita textual): «8. B: Somos cuatro: transferime 11.700 por tu parte cuando puedas.»
- `CV2-D-L-FAMILIAR-005` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo que envíes una foto, lo cual podría ser una forma de obtener información visual o de validar datos para un posible fraude relacionado con los gastos de la casa.» — evidencia (cita textual): «7. A: Mandame la foto para guardarla con los gastos de la casa.»
- `CV2-D-L-MEDICO-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 19: «Te están pidiendo si vas a pagar el copago en el consultorio o por transferencia, lo cual podría implicar dar datos bancarios o realizar un pago no autorizado.» — evidencia (cita textual): «19. ¿Y el copago lo pago ahí o por transferencia?»
- `CV2-D-L-MEDICO-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 16: «Te están pidiendo confirmar tu nombre y fecha de nacimiento para abrir un registro, lo cual puede ser usado para suplantar tu identidad y acceder a tus datos o cuentas.» — evidencia (cita textual): «te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro»
- `CV2-D-L-MEDICO-004` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 4: «Te están pidiendo tu fecha de nacimiento para ubicar un estudio, lo cual puede ser un intento de obtener datos personales.» — evidencia (cita textual): «B: me confirmás tu fecha de nacimiento para ubicar el estudio»
- `CV2-D-L-MEDICO-005` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo que les dictes el número completo de tu teléfono, lo cual podría ser usado para fines fraudulentos.» — evidencia (cita textual): «7. A: Sí, lo mandé ayer. ¿Necesitás que te dicte el número completo?»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 4: «Te están pidiendo el número de trámite para buscar el estado de un cobro, lo cual podría ser un intento de obtener información sensible o acceder a cuentas.» — evidencia (cita textual): «B: ¿Me decís ese número, sin datos de acceso? Con eso busco el estado.»
- `CV2-D-L-ORGANISMO_PREVISIONAL-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 19: «Te están pidiendo que le pases un documento para confirmar una fecha, lo cual podría ser un intento de obtener información personal o credenciales para acceder a cuentas o realizar transacciones.» — evidencia (cita textual): «19. A: Voy a llamar ahora. ¿Necesitás que te pase el documento para confirmar la fecha?»
- `CV2-D-L-PREMIO-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «Te están pidiendo modificar el correo vinculado a una entrada para un sorteo, lo cual podría ser un intento de acceder a información o realizar alguna acción fraudulenta relacionada con esa entrada.» — evidencia (cita textual): «10. B: Puedo modificar el correo vinculado a esta entrada. ¿El evento es la feria del domingo en el galpón municipal?»
- `CV2-D-L-PREMIO-003` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 15: «No le pases tu documento personal a nadie por teléfono, ya que esto podría ser un intento de robo de identidad o suplantación de datos.» — evidencia (cita textual): «15. A: ¿Te paso mi documento ahora para dejarlo anotado?»
- `CV2-D-L-SOPORTE-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 18: «Te están pidiendo un número de teléfono de contacto para agendar una visita, lo cual puede ser usado para fines de suplantación o seguimiento de la situación.» — evidencia (cita textual): «Confirmame un teléfono de contacto, pero podés dar el que ya figura terminado en 31.»
- `CV2-D-L-SOPORTE-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «Te están pidiendo datos del consultorio y el correo para revisar la cuenta, lo cual podría ser para acceder a información sensible o realizar alguna acción no autorizada.» — evidencia (cita textual): «Para revisar la cuenta, ¿me confirmás el nombre del consultorio y las primeras letras del correo registrado?»
- `CV2-D-L-SOPORTE-004` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «No le des la clave del programa, ya que te están pidiendo que la compartas, lo cual podría comprometer la licencia o la cuenta asociada.» — evidencia (cita textual): «11. A: Ese debe ser. ¿Me vas a pedir que te pase la clave del programa?»
- `CV2-D-L-SOPORTE-005` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que le pidas una clave y la cargues directamente en la impresora, lo cual podría ser un intento de acceder a dispositivos o información.» — evidencia (cita textual): «10. B: Pedile esa clave y cargala directamente en la impresora.»
- `CV2-D-L-TRABAJO-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 15: «Te están pidiendo que no entregues la llave a nadie hasta que llegue alguien, lo cual podría ser una táctica para acceder a tu local sin tu consentimiento.» — evidencia (cita textual): «10. B: decile que estamos en el local y que nos confirme cuánto tarda no le entregues la llave a nadie hasta que llegue alguno de los dos»
- `CV2-D-L-TRABAJO-003` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que envíes una foto de un documento interno, lo cual podría ser un intento de obtener acceso a información sensible o credenciales.» — evidencia (cita textual): «10. B: Eso confirma el cambio de turno. Mandame una foto de esa página por el canal interno.»
- `CV2-D-L-WHATSAPP-001` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que confirmes un número y te están enviando un código, lo cual puede ser para acceder a una cuenta o información.» — evidencia (cita textual): «A: Le pide confirmar el número, pero después sale un aviso de que mandaron un código.»
- `CV2-D-L-WHATSAPP-002` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 2: «Te están pidiendo que salgas del grupo o cambies el número asociado a tu cuenta, lo cual podría ser para acceder a información o realizar alguna acción no autorizada.» — evidencia (cita textual): «B: Hola. ¿Querés salir del grupo o cambiar el número asociado a tu cuenta?»
- `LAB-anses-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 1: «Te están pidiendo datos personales bajo la promesa de un bono, lo cual es una táctica común para el robo de identidad o fraude.» — evidencia (cita textual): «A: me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 2: «Te están pidiendo que no abras un mensaje de deuda o embargo, lo cual es una táctica común para inducirte a hacer clic en un enlace malicioso o para obtener información personal.» — evidencia (cita textual): «A: me llego un mail de una deuda y un embargo
B: no abras ningun sitio del mensaje»
- `LAB-banco-app-parafrasis` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses con tu huella y revises movimientos en la app del banco, lo cual puede permitir el acceso no autorizado a tus cuentas.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos»
- `LAB-banco-gasto-sin-pedido` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses a una aplicación para revisar un gasto, lo cual puede ser un intento de phishing o robo de credenciales.» — evidencia (cita textual): «A: entra vos a la aplicacion cuando puedas y fijate»
- `LAB-banco-revisa-app` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que cortes la comunicación y que ingreses a una aplicación oficial, lo cual es una táctica común para robar tus credenciales o acceder a tus cuentas bancarias.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que llames a un número guardado, lo cual podría ser para acceder a información o realizar alguna acción no autorizada.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LAB-no-bajes-nada` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 1: «Te están pidiendo que descargues un programa y les muestres tu celular, lo cual puede permitirles acceder a tu dispositivo y robar información o controlar tu cuenta.» — evidencia (cita textual): «A: me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 2: «Te están pidiendo que cambies tu clave basándose en un aviso de ingreso sospechoso; no cambies ninguna clave ni hagas clic en nada.» — evidencia (cita textual): «B: Hola, Lucía. Llamo al número que está atrás de mi tarjeta. Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `LG-FAMILIAR-LLAMADO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo una transferencia de dinero para gastos médicos, lo cual es una táctica común de estafa.» — evidencia (cita textual): «A: ¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-ORG-TURNO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 4: «Te están pidiendo datos personales como domicilio y foto de documento, lo cual es una táctica común para suplantar identidad y robar tus cuentas.» — evidencia (cita textual): «Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-SUPPORT-INFO-01-e01` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 2: «Te están pidiendo que te identifiques o reveles información de acceso a tu cuenta para acceder a ella.» — evidencia (cita textual): «B: Hola, ¿qué tal? Los llamo porque no puedo entrar a mi cuenta desde la computadora: me dice que el usuario o la contraseña son incorrectos.»
- `LG-SUPPORT-INFO-01-e02` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «No le pases ningún dato a nadie, ya que te están pidiendo información para acceder a tus movimientos bancarios.» — evidencia (cita textual): «11. A: Entré, ya veo mis movimientos. ¿No hace falta que te pase algún dato?»
- `LG-WA-CONSULTA-01-e01` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que leas o compartas un código de activación de WhatsApp, lo cual podría permitir que accedan a tu cuenta o información personal.» — evidencia (cita NO textual): «1. A: Me llegó por SMS un código para activar WhatsApp y yo no lo pedí. 2. B: No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación. 3. A: ¿Necesitás verlo para ayudarme?»
- `TR-03-negacion-y-consejo` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están presionando para que transfieras dinero bajo la excusa de que te van a bloquear la cuenta.» — evidencia (cita textual): «A: ¿Y si me dicen que tengo que transferir para que no me bloqueen la cuenta?»
- `TR-05-asado-con-transferencia` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 13: «Te están pidiendo que realices una transferencia de dinero antes del viernes, lo cual podría ser una estafa para robarte fondos.» — evidencia (cita textual): «Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.»
- `TR-06-banco-alerta-legitima` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «No le pases el código que te llegó, ya que te están pidiendo que lo verifiques para frenar una supuesta compra.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo un código; no le des ningún código que te pidan por teléfono, ya que podría ser un código de verificación o activación para acceder a tus cuentas.» — evidencia (cita textual): «3. A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 4: «Te están pidiendo transferir veinte mil pesos bajo el pretexto de una boleta de luz, lo cual es una táctica común de estafa.» — evidencia (cita textual): «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento, datos personales que pueden ser usados para suplantar tu identidad.» — evidencia (cita textual): «5. A: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»
- `CV2-D-L-BANCO-001` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 12: «Te están pidiendo que confirmes el nombre del titular para cargar un desconocimiento, lo cual podría ser para acceder a tus cuentas o realizar una transacción no autorizada.» — evidencia (cita textual): «12. B: entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo los últimos cuatro dígitos de la cuenta para identificarla, lo cual es información sensible que podría usarse para acceder a tus fondos.» — evidencia (cita textual): «Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-004` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «No le pidas los últimos cuatro dígitos de tu cuenta bancaria, ya que esto podría ser para completar una transacción o clonar tus datos.» — evidencia (cita textual): «Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»
- `CV2-D-L-BANCO-005` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo los últimos cuatro dígitos de la cuenta para encontrarla, lo cual es información sensible que podría usarse para acceder a tus cuentas.» — evidencia (cita textual): «B: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 9: «Te están pidiendo confirmar el número de cuenta para acceder a tus movimientos, lo cual puede ser el primer paso para acceder a tu información bancaria.» — evidencia (cita textual): «Podemos recorrer los últimos movimientos. ¿La cuenta termina en 2609?»
- `CV2-D-L-BANCO-010` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo los últimos cuatro números de tu cuenta bancaria para ubicar un comprobante, lo cual puede ser para acceder a tus fondos.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-ESCUELA-004` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo que dictes un correo electrónico completo para actualizar tu ficha de estudiante, lo cual podría ser para acceder a tus datos o cuentas.» — evidencia (cita textual): «8. B: ¿Me lo podés dictar completo para evitar un error?»
- `CV2-D-L-FAMILIAR-002` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «No compartas ningún alias o dato personal por mensaje, ya que esto puede ser usado para acceder a tus cuentas o información.» — evidencia (cita textual): «Pasame el alias por mensaje así no lo tengo que copiar de memoria.»
- `CV2-D-L-FAMILIAR-005` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que transfieras dinero, lo cual es una acción que permite el robo de fondos.» — evidencia (cita textual): «8. B: Te la reenvío. ¿Podés transferir tu aporte esta semana?»
- `CV2-D-L-MEDICO-002` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 16: «Te están pidiendo confirmar tu nombre y fecha de nacimiento para abrir un registro, lo cual puede ser usado para suplantar tu identidad.» — evidencia (cita textual): «te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 17: «Te están pidiendo que dictes tu número de documento, lo cual es un dato personal sensible que podría ser usado para suplantar tu identidad o acceder a trámites.» — evidencia (cita textual): «17. A: ¿Te dicto el número de documento ahora?»
- `CV2-D-L-PREMIO-002` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 12: «Te están pidiendo que confirmen o modifiquen un correo electrónico asociado a una entrada de sorteo, lo cual podría ser un intento de acceder a información o realizar alguna acción no autorizada.» — evidencia (cita textual): «B: Listo. Te leo cómo quedó: cami punto neri arroba correo ejemplo.»
- `CV2-D-L-SOPORTE-004` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «No le des la clave del programa, ya que te están pidiendo que la compartas, lo cual podría comprometer el acceso a tu cuenta o información.» — evidencia (cita textual): «11. A: Ese debe ser. ¿Me vas a pedir que te pase la clave del programa?»
- `CV2-D-L-SOPORTE-005` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que le des una clave a alguien para cargarla en la impresora, lo cual podría ser un intento de acceso no autorizado o robo de información.» — evidencia (cita textual): «10. B: Pedile esa clave y cargala directamente en la impresora.»
- `CV2-D-L-TRABAJO-001` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 22: «Te están pidiendo que transfieras dinero ('te transfiero lo mío') bajo la excusa de pedir un café, lo cual es una táctica común en estafas.» — evidencia (cita textual): «20. B: sí uno chico sin azúcar después te transfiero lo mío»
- `CV2-D-L-TRABAJO-003` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «No envíes ninguna foto de documentos internos por canales no verificados, ya que esto podría ser un intento de obtener acceso a información sensible o credenciales.» — evidencia (cita textual): «10. B: Eso confirma el cambio de turno. Mandame una foto de esa página por el canal interno.»
- `CV2-D-L-WHATSAPP-001` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 16: «Te están pidiendo que ingreses seis números en la pantalla de la aplicación, lo cual podría ser para acceder a una cuenta o realizar alguna acción no autorizada.» — evidencia (cita textual): «16. B: Que los ingrese en la pantalla de la aplicación.»
- `LAB-anses-canal-oficial` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están pidiendo datos personales bajo la promesa de un bono, lo cual es una táctica común para robar tu información.» — evidencia (cita textual): «A: me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses a una página web para resolver un supuesto embargo, lo cual es una táctica común para robar tus datos o dinero.» — evidencia (cita textual): «1. A: me llego un mail de una deuda y un embargo
2. B: no abras ningun sitio del mensaje
3. B: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-app-parafrasis` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses tu huella y revises movimientos en la app del banco, lo cual puede permitir el acceso no autorizado a tus cuentas.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos»
- `LAB-banco-revisa-app` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación oficial, lo cual es una táctica común para robar tus datos o acceder a tu cuenta.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que llames a un número que te han proporcionado, lo cual puede ser para acceder a información o realizar alguna acción fraudulenta.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LAB-no-bajes-nada` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 4: «Te están pidiendo que bajes un programa y les muestres tu celular, y luego te dicen que llames al banco por un número de tarjeta, lo cual puede ser para acceder a tu cuenta o información financiera.» — evidencia (cita textual): «A: corto y llamo yo al banco por el numero de atras de la tarjeta»
- `LG-BANK-VERIF-01-e01` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «No le des los últimos números de tu tarjeta a nadie, ya que te están pidiendo datos sensibles para supuestamente identificarte.» — evidencia (cita textual): «B: ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `LG-SUPPORT-INFO-01-e01` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 9: «Te están pidiendo que les des tu usuario y contraseña para que los revisen, lo cual es una forma de robar el acceso a tu cuenta.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `TR-05-asado-con-transferencia` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 14: «Te están pidiendo un alias para realizar una transferencia de dinero, lo cual puede ser para acceder a cuentas o realizar transacciones no autorizadas.» — evidencia (cita textual): «Mandame el alias que ahora no lo tengo a mano.»
- `TR-06-banco-alerta-legitima` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «No le pidas ningún código que te llegó por mensaje, ya que esto es una táctica común para robar tu cuenta.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo un código; no lo compartas, podría ser un código de verificación o activación para acceder a tus cuentas.» — evidencia (cita textual): «A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 9: «Te están pidiendo transferir dinero a una cuenta, lo cual es una táctica común en estafas.» — evidencia (cita textual): «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento, datos personales que pueden ser usados para suplantar tu identidad o acceder a información sensible.» — evidencia (cita textual): «A: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-BANCO-012` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-005` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-007` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-007` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-BANCO-012` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-FAMILIAR-006` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.40
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-005` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-006` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-007` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-SOPORTE-008` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-007` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 167.077 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 5 ms; encoder: 32.222 ms (carga fresca); calentamiento Tito: 162 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|gemma4:e2b-it-q4_K_M|v3|ab`

Consultas al SLM hasta el aviso: 867; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 715.436 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | L12 | 12 | 0 | 0 | 10.020 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.942 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.677 |
| `CV2-D-L-BANCO-004` | 5 | L8 | 4 | 4 | 0 | 3.351 |
| `CV2-D-L-BANCO-005` | 8 | L8 | 1 | 7 | 0 | 2.154 |
| `CV2-D-L-BANCO-006` | 6 | L9 | 4 | 5 | 0 | 3.810 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.523 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.340 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.338 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 2.120 |
| `CV2-D-L-DELIVERY-001` | 6 | sin aviso | 19 | 5 | 0 | 11.947 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 2.630 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 13.195 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 2.716 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 3.140 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 3.006 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 12.461 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 3.047 |
| `CV2-D-L-ESCUELA-004` | 7 | L8 | 2 | 6 | 0 | 2.589 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 12.342 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 2.616 |
| `CV2-D-L-FAMILIAR-002` | 11 | L11 | 1 | 10 | 0 | 2.316 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 4.529 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 6.462 |
| `CV2-D-L-FAMILIAR-005` | 10 | L10 | 1 | 9 | 0 | 2.024 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 2.631 |
| `CV2-D-L-MEDICO-002` | 7 | L16 | 10 | 6 | 0 | 6.517 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 3.225 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.961 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 10.507 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | L17 | 12 | 5 | 0 | 9.089 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 2.605 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 11.480 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.565 |
| `CV2-D-L-PREMIO-002` | 5 | L12 | 8 | 4 | 0 | 6.384 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 3.106 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 2.764 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 12.273 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 16.813 |
| `CV2-D-L-SOPORTE-004` | 1 | L11 | 11 | 0 | 0 | 6.840 |
| `CV2-D-L-SOPORTE-005` | 10 | L10 | 1 | 9 | 0 | 2.475 |
| `CV2-D-L-TRABAJO-001` | 2 | L22 | 21 | 1 | 0 | 12.559 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 12.250 |
| `CV2-D-L-TRABAJO-003` | 10 | L10 | 1 | 9 | 0 | 2.268 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.880 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 14.325 |
| `CV2-D-L-WHATSAPP-001` | 16 | L16 | 1 | 15 | 0 | 3.380 |
| `CV2-D-L-WHATSAPP-002` | 10 | sin aviso | 14 | 9 | 0 | 9.259 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 10.009 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 12.607 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 12.542 |
| `CV2-D-V-BANCO-001` | 29 | L29 | 1 | 28 | 0 | 5.079 |
| `CV2-D-V-BANCO-002` | 6 | L10 | 5 | 5 | 0 | 4.205 |
| `CV2-D-V-BANCO-003` | 5 | L19 | 15 | 4 | 0 | 10.255 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 2.322 |
| `CV2-D-V-BANCO-005` | 1 | L5 | 5 | 0 | 0 | 3.959 |
| `CV2-D-V-BANCO-006` | 2 | L10 | 9 | 1 | 0 | 6.088 |
| `CV2-D-V-BANCO-007` | 11 | L11 | 1 | 10 | 0 | 3.279 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 3.490 |
| `CV2-D-V-BANCO-009` | 3 | L10 | 8 | 2 | 0 | 5.392 |
| `CV2-D-V-BANCO-010` | 1 | L7 | 7 | 0 | 0 | 4.819 |
| `CV2-D-V-BANCO-011` | 12 | L12 | 1 | 11 | 0 | 2.470 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 13.405 |
| `CV2-D-V-FAMILIAR-001` | 5 | L17 | 13 | 4 | 0 | 9.210 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 2.608 |
| `CV2-D-V-FAMILIAR-003` | 14 | L14 | 1 | 13 | 0 | 2.428 |
| `CV2-D-V-FAMILIAR-004` | 14 | L22 | 9 | 13 | 0 | 7.000 |
| `CV2-D-V-FAMILIAR-005` | 18 | L18 | 1 | 17 | 0 | 2.818 |
| `CV2-D-V-FAMILIAR-006` | 17 | sin aviso | 7 | 16 | 0 | 5.352 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L11 | 10 | 1 | 0 | 7.518 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L9 | 9 | 0 | 0 | 6.589 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | L13 | 1 | 12 | 0 | 2.819 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | L8 | 7 | 1 | 0 | 5.134 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 13.906 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 14.679 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.211 |
| `CV2-D-V-PREMIO-002` | 3 | L13 | 11 | 2 | 0 | 7.056 |
| `CV2-D-V-PREMIO-003` | 3 | L16 | 14 | 2 | 0 | 8.320 |
| `CV2-D-V-PREMIO-004` | 12 | L12 | 1 | 11 | 0 | 2.266 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 12.622 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 15.622 |
| `CV2-D-V-SOPORTE-001` | 12 | L12 | 1 | 11 | 0 | 2.243 |
| `CV2-D-V-SOPORTE-002` | 1 | L7 | 7 | 0 | 0 | 4.713 |
| `CV2-D-V-SOPORTE-003` | 1 | L10 | 10 | 0 | 0 | 6.188 |
| `CV2-D-V-SOPORTE-004` | 13 | L14 | 2 | 12 | 0 | 3.369 |
| `CV2-D-V-SOPORTE-005` | 10 | L10 | 1 | 9 | 0 | 2.049 |
| `CV2-D-V-SOPORTE-006` | 1 | L10 | 10 | 0 | 0 | 6.365 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 5.831 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 3.936 |
| `CV2-D-V-WHATSAPP-001` | 1 | L7 | 7 | 0 | 0 | 4.276 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 2.083 |
| `CV2-D-V-WHATSAPP-003` | 8 | L8 | 1 | 7 | 0 | 1.907 |
| `CV2-D-V-WHATSAPP-004` | 5 | L9 | 5 | 4 | 0 | 4.090 |
| `CV2-D-V-WHATSAPP-005` | 10 | L10 | 1 | 9 | 0 | 2.035 |
| `CV2-D-V-WHATSAPP-006` | 22 | L24 | 3 | 21 | 0 | 4.674 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 9.316 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 7.826 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 2.713 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.267 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 2.199 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.119 |
| `LAB-anses-canal-oficial` | 5 | L5 | 1 | 4 | 0 | 1.390 |
| `LAB-arca-canal-oficial` | 1 | L3 | 3 | 0 | 0 | 2.354 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 2.183 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.480 |
| `LAB-banco-app-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.561 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 2.393 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.449 |
| `LAB-banco-gasto-sin-pedido` | 1 | sin aviso | 3 | 0 | 0 | 1.660 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 694 |
| `LAB-banco-numeros-sin-clave` | 1 | L3 | 3 | 0 | 0 | 2.222 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 1.312 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 2.548 |
| `LAB-familiar-llama-vos` | 2 | L3 | 2 | 1 | 0 | 1.761 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 2.719 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 2.604 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 2.101 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 2.969 |
| `LAB-no-bajes-nada` | 4 | L4 | 1 | 3 | 0 | 1.534 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 2.320 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 867 |
| `LAB-whatsapp-codigo` | 1 | L1 | 1 | 0 | 0 | 1.017 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.191 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 1.756 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.426 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.504 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 4.616 |
| `LG-SUPPORT-INFO-01-e01` | 7 | L9 | 3 | 6 | 0 | 3.447 |
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 4.657 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 422 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L4 | 3 | 1 | 0 | 2.542 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 2.157 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 4.661 |
| `SC-PREMIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 4.499 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 3.590 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 2.498 |
| `SC-WA-CODE-01-e01` | 1 | L4 | 4 | 0 | 0 | 2.956 |
| `TR-01-pedido-indirecto-digitos` | 3 | L5 | 3 | 2 | 0 | 3.507 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 4.881 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.132 |
| `TR-04-pedido-tras-charla-larga` | 5 | L21 | 17 | 4 | 0 | 12.310 |
| `TR-05-asado-con-transferencia` | 14 | L14 | 1 | 13 | 0 | 2.508 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 6.399 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L5 | 1 | 4 | 0 | 1.996 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 1.056 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.537 |
| `TR-10-ofrecimiento-inducido` | 4 | L4 | 1 | 3 | 0 | 1.495 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 1.957 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 4.132 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.738 |

Nunca derivados (permanecen en sus denominadores):
- `CV2-D-V-PREMIO-001` · vishing sin aviso (falso negativo visible).
- `CV2-D-L-BANCO-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-BANCO-007` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-BANCO-008` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-BANCO-009` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-DELIVERY-002` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-DELIVERY-004` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-DELIVERY-005` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-ESCUELA-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-ESCUELA-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-FAMILIAR-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-MEDICO-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-MEDICO-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-MEDICO-004` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-ORGANISMO_PREVISIONAL-002` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-PREMIO-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-PREMIO-003` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-SOPORTE-001` · legítima sin aviso (verdadero negativo).
- `CV2-D-L-TRABAJO-004` · legítima sin aviso (verdadero negativo).
- `LG-ORG-TURNO-01-e01` · legítima sin aviso (verdadero negativo).
- `LG-WA-CONSULTA-01-e01` · legítima sin aviso (verdadero negativo).
- `TR-03-negacion-y-consejo` · legítima sin aviso (verdadero negativo).


## Costos por componente hasta el aviso

Modo de término: `operativo-hasta-aviso`.
Cada caso aporta sus actualizaciones evaluadas hasta el aviso incluido; una llamada sin aviso aporta la conversación completa. `ms` total = Tito + SLM por actualización, sin doble conteo.

| Configuración | ms hasta aviso | Tito ms | SLM ms | Tokens hasta aviso | Actualiz. | Runtime con dato/ausente |
|---|---|---|---|---|---|---|
| `slm\|gemma4:e2b-it-q4_K_M\|v3\|ab` | 988.906 | 0 | 988.906 | 1.80484e+06 | 1680 | 1680/0 |
| `tito-slm\|gemma4:e2b-it-q4_K_M\|v3\|ab` | 715.436 | 142.915 | 572.520 | 1.03852e+06 | 2006 | 867/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
