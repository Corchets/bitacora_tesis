# Resumen de la corrida `2026-11-04_201116_prompt-v3-b-tito-sin-indicio`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --prompts v3 --hablantes ab --num-ctx 4096 --seed 42 --sin-reglas --filtro-tito --tito-real --sin-indicio --etiqueta prompt-v3-b-tito-sin-indicio --salida /content/resultados-prompt-v3/b`
- **Inicio / fin:** 2026-11-04T20:11:16 / 2026-11-04T20:22:21
- **Código:** `a42e1b5504`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v3\|ab` | 64/75 | 42 | 18 | 3 | 0 | 35/75 | 0/1930 | 133 | 950 | 95/99 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v3\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L12 |
| `CV2-D-L-BANCO-002` | legítima | — | — | FA L7 |
| `CV2-D-L-BANCO-003` | legítima | — | — | ok |
| `CV2-D-L-BANCO-004` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-005` | legítima | — | — | FA L8 |
| `CV2-D-L-BANCO-006` | legítima | — | — | FA L6 |
| `CV2-D-L-BANCO-007` | legítima | — | — | ok |
| `CV2-D-L-BANCO-008` | legítima | — | — | ok |
| `CV2-D-L-BANCO-009` | legítima | — | — | ok |
| `CV2-D-L-BANCO-010` | legítima | — | — | FA L10 |
| `CV2-D-L-DELIVERY-001` | legítima | — | — | FA L17 |
| `CV2-D-L-DELIVERY-002` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-003` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-004` | legítima | — | — | ok |
| `CV2-D-L-DELIVERY-005` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-001` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-002` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | FA L7 |
| `CV2-D-L-ESCUELA-005` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-001` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-002` | legítima | — | — | FA L11 |
| `CV2-D-L-FAMILIAR-003` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-004` | legítima | — | — | ok |
| `CV2-D-L-FAMILIAR-005` | legítima | — | — | FA L10 |
| `CV2-D-L-MEDICO-001` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-002` | legítima | — | — | FA L16 |
| `CV2-D-L-MEDICO-003` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-004` | legítima | — | — | ok |
| `CV2-D-L-MEDICO-005` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | legítima | — | — | FA L17 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | legítima | — | — | ok |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-001` | legítima | — | — | ok |
| `CV2-D-L-PREMIO-002` | legítima | — | — | FA L11 |
| `CV2-D-L-PREMIO-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-001` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-002` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-003` | legítima | — | — | ok |
| `CV2-D-L-SOPORTE-004` | legítima | — | — | FA L11 |
| `CV2-D-L-SOPORTE-005` | legítima | — | — | FA L10 |
| `CV2-D-L-TRABAJO-001` | legítima | — | — | FA L15 |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | FA L10 |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L16 |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | FA L20 |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | FA L12 |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L29 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L10 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L14 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L2 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L8 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L11 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L9 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L12 |
| `CV2-D-V-BANCO-012` | vishing | — | — | — |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L14 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | <R L15 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | <R L18 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | >R L23 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | <R L12 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | >R L15 |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | =R L14 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L11 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L10 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | <R L7 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L9 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L11 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L24 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | — |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L5 |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L3 |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L3 |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | FA L3 |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | FA L4 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L2 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L6 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L7 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L11 |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L5 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | <R L7 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L23 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L14 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L5 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L5 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 12: «Te están pidiendo confirmar el nombre que figura como titular para cargar un desconocimiento, lo cual podría ser para autorizar un cargo no reconocido en tu cuenta.» — evidencia (cita textual): «12. B: entonces cargo el desconocimiento por el importe completo te voy a pedir que confirmes el nombre que figura como titular»
- `CV2-D-L-BANCO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo los últimos cuatro dígitos de la cuenta para identificarla, lo cual es información sensible que podría usarse para acceder a tus fondos.» — evidencia (cita textual): «A: Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo los últimos cuatro dígitos de tu cuenta para buscar ingresos, lo cual podría ser para acceder a tus fondos.» — evidencia (cita textual): «Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»
- `CV2-D-L-BANCO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 8: «Te están pidiendo los últimos cuatro dígitos de la cuenta para encontrarla, lo cual es información sensible que podría usarse para acceder a tus cuentas.» — evidencia (cita textual): «8. B: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «Te están pidiendo que confirmes el número de tu cuenta para poder revisar movimientos, lo cual podría ser un intento de obtener información sensible para acceder a tus cuentas.» — evidencia (cita textual): «B: Podemos recorrer los últimos movimientos. ¿La cuenta termina en 2609?»
- `CV2-D-L-BANCO-010` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo los últimos cuatro números de una cuenta bancaria para ubicar un comprobante de transferencia, lo cual podría permitirles acceder a tus datos bancarios.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-DELIVERY-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 17: «Te están pidiendo que firmes un recibo de una compra a nombre de otra persona, lo cual podría ser para autorizar la entrega de un paquete o transacción.» — evidencia (cita textual): «17. A: puede firmar con su nombre aunque la compra esté a nombre de ocampo»
- `CV2-D-L-ESCUELA-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «Te están pidiendo que actualices tu correo en la ficha de estudiante, lo cual podría ser para acceder a información personal o cuentas.» — evidencia (cita textual): «7. A: Sí. Ahora uso uno que empieza por nadia punto p y termina en correo ejemplo.»
- `CV2-D-L-FAMILIAR-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «Te están pidiendo que envíes un alias por mensaje, lo cual podría ser para acceder a cuentas o información sensible.» — evidencia (cita textual): «11. A: Pasame el alias por mensaje así no lo tengo que copiar de memoria.»
- `CV2-D-L-FAMILIAR-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que envíes una foto y luego te están pidiendo que transfieras dinero, lo cual podría ser un intento de fraude financiero.» — evidencia (cita textual): «7. A: Mandame la foto para guardarla con los gastos de la casa.»
- `CV2-D-L-MEDICO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 16: «Te están pidiendo confirmar tu nombre y fecha de nacimiento para abrir un registro, lo cual puede ser usado para suplantar tu identidad y acceder a tus datos o cuentas.» — evidencia (cita textual): «te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 17: «Te están pidiendo que dictes el número de documento, lo cual es un dato personal que puede ser usado para suplantar tu identidad.» — evidencia (cita textual): «17. A: ¿Te dicto el número de documento ahora?»
- `CV2-D-L-PREMIO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «Te están pidiendo modificar el correo vinculado a una entrada para un sorteo, lo cual podría ser un intento de acceder a información o realizar alguna acción fraudulenta relacionada con esa entrada.» — evidencia (cita textual): «10. B: Puedo modificar el correo vinculado a esta entrada. ¿El evento es la feria del domingo en el galpón municipal?»
- `CV2-D-L-SOPORTE-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «No le des la clave del programa, ya que te están pidiendo que la compartas, lo cual podría comprometer la licencia o la cuenta asociada.» — evidencia (cita textual): «11. A: Ese debe ser. ¿Me vas a pedir que te pase la clave del programa?»
- `CV2-D-L-SOPORTE-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que le pidas una clave y la cargues directamente en la impresora, lo cual podría ser un intento de acceder a dispositivos o información.» — evidencia (cita textual): «10. B: Pedile esa clave y cargala directamente en la impresora.»
- `CV2-D-L-TRABAJO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 15: «Te están pidiendo que no entregues la llave a nadie hasta que llegue alguien, lo cual podría ser una táctica para acceder a tu local sin tu consentimiento.» — evidencia (cita textual): «10. B: decile que estamos en el local y que nos confirme cuánto tarda no le entregues la llave a nadie hasta que llegue alguno de los dos»
- `CV2-D-L-TRABAJO-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «Te están pidiendo que envíes una foto de una página interna, lo cual podría ser para obtener acceso a información sensible o para validar tu identidad en un contexto de trabajo, lo cual es un riesgo.» — evidencia (cita textual): «10. B: Eso confirma el cambio de turno. Mandame una foto de esa página por el canal interno.»
- `CV2-D-L-WHATSAPP-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 16: «Te están pidiendo que ingreses seis números en la pantalla de la aplicación, lo cual podría ser para acceder a una cuenta o realizar alguna acción no autorizada.» — evidencia (cita textual): «16. B: Que los ingrese en la pantalla de la aplicación.»
- `CV2-D-L-WHATSAPP-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 20: «Te están pidiendo cerrar la sesión de una computadora vieja, lo cual podría permitir que accedan a tu cuenta o información guardada.» — evidencia (cita textual): «En dispositivos vinculados podés cerrar la sesión de la computadora vieja.»
- `CV2-D-L-WHATSAPP-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 12: «Te están pidiendo que compartas un código de registro que aparece al verificar la cuenta, lo cual podría ser para acceder a tu cuenta o realizar alguna acción no autorizada.» — evidencia (cita textual): «12. B: El código puede aparecer cuando se verifica la cuenta. No hace falta que me lo compartas para revisar notificaciones.»
- `LAB-anses-canal-oficial` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están pidiendo datos personales bajo la promesa de un bono, lo cual es una táctica común para el robo de identidad o fraude.» — evidencia (cita textual): «A: me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses a una página web para resolver un supuesto embargo, lo cual es una táctica común para robar tus datos o dinero.» — evidencia (cita textual): «B: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-app-parafrasis` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses con tu huella y revises movimientos en la app del banco, lo cual puede permitir el acceso a tus cuentas.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
B: dale a ver
A: entra con tu huella y revisa los movimientos»
- `LAB-banco-gasto-sin-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que ingreses a una aplicación para revisar un gasto, lo cual puede ser un intento de phishing o robo de credenciales.» — evidencia (cita textual): «A: entra vos a la aplicacion cuando puedas y fijate»
- `LAB-banco-revisa-app` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que cortes la comunicación y que ingreses a una aplicación oficial, lo cual es una táctica común para robar tus credenciales o acceder a tus cuentas bancarias.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo que llames a un número guardado, lo cual podría ser para acceder a información o realizar alguna acción no autorizada.» — evidencia (cita textual): «B: llama vos al numero que tenes guardado»
- `LAB-no-bajes-nada` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 4: «Te están pidiendo que descargues un programa y les muestres tu celular, lo cual puede permitirles acceder a tu información o controlar tu dispositivo.» — evidencia (cita textual): «1. A: me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 6: «No le des los últimos números de tu tarjeta a nadie, ya que podrían intentar clonar tu tarjeta o acceder a tu cuenta.» — evidencia (cita textual): «6. B: ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `LG-SUPPORT-INFO-01-e01` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 7: «La persona B está ofreciendo entregar su usuario y contraseña, lo cual es un riesgo directo para el acceso a su cuenta.» — evidencia (cita textual): «4. B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `LG-SUPPORT-INFO-01-e02` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 11: «La persona te está preguntando si necesita pasar datos después de acceder a sus movimientos bancarios, lo cual es una táctica común para obtener credenciales o información sensible.» — evidencia (cita textual): «11. A: Entré, ya veo mis movimientos. ¿No hace falta que te pase algún dato?»
- `TR-05-asado-con-transferencia` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 14: «Te están pidiendo un alias para realizar una transferencia de dinero, lo cual podría ser para robar tus cuentas.» — evidencia (cita textual): «Mandame el alias que ahora no lo tengo a mano.»
- `TR-06-banco-alerta-legitima` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 10: «No le pases el código que te llegó, ya que te están pidiendo que lo verifiques para detener una supuesta compra fraudulenta.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 3: «Te están pidiendo un código; no le des nada a nadie, podría ser un código de verificación o activación para acceder a tus cuentas.» — evidencia (cita textual): «3. A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 9: «Te están pidiendo transferir veinte mil pesos a una cuenta, lo cual es una solicitud de dinero que puede ser un intento de estafa.» — evidencia (cita textual): «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento, datos personales que pueden ser usados para suplantar tu identidad.» — evidencia (cita textual): «5. A: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-BANCO-012` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · sin riesgo registrado
- `CV2-D-V-PREMIO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-PREMIO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `CV2-D-V-WHATSAPP-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 15.132 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Sin indicio (`--sin-indicio`): Tito solo decide cuándo consultar; el SLM recibe el mismo mensaje que el SLM solo, sin bloque de indicio ni de fallo técnico.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 0 ms; encoder: 12.294 ms (carga fresca); calentamiento Tito: 106 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|ab`

Consultas al SLM hasta el aviso: 791; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 649.386 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | L12 | 12 | 0 | 0 | 8.555 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.952 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.899 |
| `CV2-D-L-BANCO-004` | 5 | L8 | 4 | 4 | 0 | 3.325 |
| `CV2-D-L-BANCO-005` | 8 | L8 | 1 | 7 | 0 | 1.851 |
| `CV2-D-L-BANCO-006` | 6 | L6 | 1 | 5 | 0 | 1.707 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.378 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.518 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.693 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 2.337 |
| `CV2-D-L-DELIVERY-001` | 6 | L17 | 12 | 5 | 0 | 8.197 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 2.957 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 12.381 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 2.949 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 3.196 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 2.439 |
| `CV2-D-L-ESCUELA-002` | 3 | sin aviso | 24 | 2 | 0 | 12.183 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 2.517 |
| `CV2-D-L-ESCUELA-004` | 7 | L7 | 1 | 6 | 0 | 1.802 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 11.520 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 2.514 |
| `CV2-D-L-FAMILIAR-002` | 11 | L11 | 1 | 10 | 0 | 2.216 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 4.278 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 6.087 |
| `CV2-D-L-FAMILIAR-005` | 10 | L10 | 1 | 9 | 0 | 2.147 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 2.592 |
| `CV2-D-L-MEDICO-002` | 7 | L16 | 10 | 6 | 0 | 6.822 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 3.350 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.815 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 10.913 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | L17 | 12 | 5 | 0 | 8.555 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 2.541 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 9.465 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.568 |
| `CV2-D-L-PREMIO-002` | 5 | L11 | 7 | 4 | 0 | 5.253 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 3.090 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 3.103 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 9.397 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 11.068 |
| `CV2-D-L-SOPORTE-004` | 1 | L11 | 11 | 0 | 0 | 7.162 |
| `CV2-D-L-SOPORTE-005` | 10 | L10 | 1 | 9 | 0 | 2.543 |
| `CV2-D-L-TRABAJO-001` | 2 | L15 | 14 | 1 | 0 | 9.421 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 15.894 |
| `CV2-D-L-TRABAJO-003` | 10 | L10 | 1 | 9 | 0 | 2.612 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 3.294 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 13.137 |
| `CV2-D-L-WHATSAPP-001` | 16 | L16 | 1 | 15 | 0 | 3.492 |
| `CV2-D-L-WHATSAPP-002` | 10 | L20 | 11 | 9 | 0 | 7.551 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 8.764 |
| `CV2-D-L-WHATSAPP-004` | 8 | L12 | 5 | 7 | 0 | 4.450 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 14.571 |
| `CV2-D-V-BANCO-001` | 29 | L29 | 1 | 28 | 0 | 4.330 |
| `CV2-D-V-BANCO-002` | 6 | L10 | 5 | 5 | 0 | 4.302 |
| `CV2-D-V-BANCO-003` | 5 | L14 | 10 | 4 | 0 | 7.006 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 2.290 |
| `CV2-D-V-BANCO-005` | 1 | L2 | 2 | 0 | 0 | 1.710 |
| `CV2-D-V-BANCO-006` | 2 | L8 | 7 | 1 | 0 | 5.038 |
| `CV2-D-V-BANCO-007` | 11 | L11 | 1 | 10 | 0 | 3.298 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 2.952 |
| `CV2-D-V-BANCO-009` | 3 | L9 | 7 | 2 | 0 | 5.023 |
| `CV2-D-V-BANCO-010` | 1 | L1 | 1 | 0 | 0 | 1.197 |
| `CV2-D-V-BANCO-011` | 12 | L12 | 1 | 11 | 0 | 2.593 |
| `CV2-D-V-BANCO-012` | 1 | sin aviso | 21 | 0 | 0 | 16.227 |
| `CV2-D-V-FAMILIAR-001` | 5 | L15 | 11 | 4 | 0 | 6.429 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 2.638 |
| `CV2-D-V-FAMILIAR-003` | 14 | L14 | 1 | 13 | 0 | 2.604 |
| `CV2-D-V-FAMILIAR-004` | 14 | L15 | 2 | 13 | 0 | 3.208 |
| `CV2-D-V-FAMILIAR-005` | 18 | L18 | 1 | 17 | 0 | 3.349 |
| `CV2-D-V-FAMILIAR-006` | 17 | L23 | 7 | 16 | 0 | 5.593 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L2 | 1 | 1 | 0 | 1.112 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L8 | 8 | 0 | 0 | 5.858 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | L13 | 1 | 12 | 0 | 3.106 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | L8 | 7 | 1 | 0 | 4.508 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 13.307 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 14.615 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.059 |
| `CV2-D-V-PREMIO-002` | 3 | L12 | 10 | 2 | 0 | 6.433 |
| `CV2-D-V-PREMIO-003` | 3 | L15 | 13 | 2 | 0 | 8.278 |
| `CV2-D-V-PREMIO-004` | 12 | L12 | 1 | 11 | 0 | 2.168 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 11.657 |
| `CV2-D-V-PREMIO-006` | 1 | sin aviso | 22 | 0 | 0 | 12.698 |
| `CV2-D-V-SOPORTE-001` | 12 | L12 | 1 | 11 | 0 | 2.276 |
| `CV2-D-V-SOPORTE-002` | 1 | L7 | 7 | 0 | 0 | 4.577 |
| `CV2-D-V-SOPORTE-003` | 1 | L10 | 10 | 0 | 0 | 6.244 |
| `CV2-D-V-SOPORTE-004` | 13 | L14 | 2 | 12 | 0 | 3.297 |
| `CV2-D-V-SOPORTE-005` | 10 | L11 | 2 | 9 | 0 | 2.604 |
| `CV2-D-V-SOPORTE-006` | 1 | L10 | 10 | 0 | 0 | 5.964 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 4.722 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 3.828 |
| `CV2-D-V-WHATSAPP-001` | 1 | L7 | 7 | 0 | 0 | 4.929 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 2.110 |
| `CV2-D-V-WHATSAPP-003` | 8 | L8 | 1 | 7 | 0 | 2.059 |
| `CV2-D-V-WHATSAPP-004` | 5 | L9 | 5 | 4 | 0 | 4.077 |
| `CV2-D-V-WHATSAPP-005` | 10 | L11 | 2 | 9 | 0 | 2.736 |
| `CV2-D-V-WHATSAPP-006` | 22 | L24 | 3 | 21 | 0 | 4.593 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 9.285 |
| `CV2-D-V-WHATSAPP-008` | 9 | sin aviso | 12 | 8 | 0 | 7.620 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 2.430 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.328 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 2.076 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.045 |
| `LAB-anses-canal-oficial` | 5 | L5 | 1 | 4 | 0 | 1.424 |
| `LAB-arca-canal-oficial` | 1 | L3 | 3 | 0 | 0 | 2.184 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 2.191 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.476 |
| `LAB-banco-app-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.446 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 2.088 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.298 |
| `LAB-banco-gasto-sin-pedido` | 1 | L3 | 3 | 0 | 0 | 2.141 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 699 |
| `LAB-banco-numeros-sin-clave` | 1 | L3 | 3 | 0 | 0 | 1.922 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 1.303 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 2.270 |
| `LAB-familiar-llama-vos` | 2 | L3 | 2 | 1 | 0 | 1.776 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 2.861 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 2.809 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 2.081 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 3.589 |
| `LAB-no-bajes-nada` | 4 | L4 | 1 | 3 | 0 | 1.388 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 2.228 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 959 |
| `LAB-whatsapp-codigo` | 1 | L2 | 2 | 0 | 0 | 1.581 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.932 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 1.695 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.444 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.465 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 4.926 |
| `LG-SUPPORT-INFO-01-e01` | 7 | L7 | 1 | 6 | 0 | 2.133 |
| `LG-SUPPORT-INFO-01-e02` | 8 | L11 | 4 | 7 | 0 | 3.861 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 414 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L2 | 1 | 1 | 0 | 1.182 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 2.101 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L5 | 3 | 2 | 0 | 3.438 |
| `SC-PREMIO-01-e01` | 3 | L7 | 5 | 2 | 0 | 4.408 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 3.317 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 2.591 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 2.334 |
| `TR-01-pedido-indirecto-digitos` | 3 | L5 | 3 | 2 | 0 | 3.282 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 5.199 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.108 |
| `TR-04-pedido-tras-charla-larga` | 5 | L23 | 19 | 4 | 0 | 9.991 |
| `TR-05-asado-con-transferencia` | 14 | L14 | 1 | 13 | 0 | 2.674 |
| `TR-06-banco-alerta-legitima` | 3 | L10 | 8 | 2 | 0 | 6.036 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L5 | 1 | 4 | 0 | 1.478 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 1.091 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.664 |
| `TR-10-ofrecimiento-inducido` | 4 | L5 | 2 | 3 | 0 | 2.208 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 2.232 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 3.590 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.470 |

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
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v3\|ab` | 649.386 | 142.190 | 507.197 | 878145 | 1930 | 791/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
