# Resumen de la corrida `2026-11-04_220639_prompt-v4-b-v3-rol`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos gemma4:e2b-it-q4_K_M --num-ctx 4096 --seed 42 --sin-reglas --filtro-tito --tito-real --sin-indicio --prompts v3 --hablantes rol --etiqueta prompt-v4-b-v3-rol --salida /content/resultados-prompt-v4/b`
- **Inicio / fin:** 2026-11-04T22:06:39 / 2026-11-04T22:16:55
- **Código:** `55fe977545`
- **Máquina:** Linux-6.6.159+-x86_64-with-glibc2.39, 2 núcleos lógicos, 12.7 GB de RAM
- **Ollama:** 0.40.14 · **Política:** aviso_unico_hasta_aviso · **Modo:** `operativo-hasta-aviso`
- **Casos:** 150 (75 vishing, 75 legítimas); 150 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v3\|rol` | 67/75 | 41 | 20 | 2 | 0 | 34/75 | 0/1899 | 134 | 896 | 100/101 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v3\|rol`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | legítima | — | — | FA L2 |
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
| `CV2-D-L-ESCUELA-002` | legítima | — | — | FA L21 |
| `CV2-D-L-ESCUELA-003` | legítima | — | — | ok |
| `CV2-D-L-ESCUELA-004` | legítima | — | — | FA L8 |
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
| `CV2-D-L-TRABAJO-001` | legítima | — | — | FA L20 |
| `CV2-D-L-TRABAJO-002` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-003` | legítima | — | — | FA L11 |
| `CV2-D-L-TRABAJO-004` | legítima | — | — | ok |
| `CV2-D-L-TRABAJO-005` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-001` | legítima | — | — | FA L16 |
| `CV2-D-L-WHATSAPP-002` | legítima | — | — | FA L14 |
| `CV2-D-L-WHATSAPP-003` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-004` | legítima | — | — | ok |
| `CV2-D-L-WHATSAPP-005` | legítima | — | — | ok |
| `CV2-D-V-BANCO-001` | vishing | 32 | — | <R L29 |
| `CV2-D-V-BANCO-002` | vishing | 18 | 27 | <R L10 |
| `CV2-D-V-BANCO-003` | vishing | 19 | 26 | <R L11 |
| `CV2-D-V-BANCO-004` | vishing | 16 | 21 | <R L10 |
| `CV2-D-V-BANCO-005` | vishing | 19 | — | <R L2 |
| `CV2-D-V-BANCO-006` | vishing | 14 | — | <R L8 |
| `CV2-D-V-BANCO-007` | vishing | 17 | 26 | <R L11 |
| `CV2-D-V-BANCO-008` | vishing | 16 | — | =R L16 |
| `CV2-D-V-BANCO-009` | vishing | 13 | — | <R L9 |
| `CV2-D-V-BANCO-010` | vishing | 13 | — | <R L1 |
| `CV2-D-V-BANCO-011` | vishing | — | — | L12 |
| `CV2-D-V-BANCO-012` | vishing | — | — | L5 |
| `CV2-D-V-FAMILIAR-001` | vishing | 15 | 20 | =R L15 |
| `CV2-D-V-FAMILIAR-002` | vishing | 16 | 27 | =R L16 |
| `CV2-D-V-FAMILIAR-003` | vishing | 15 | — | <R L14 |
| `CV2-D-V-FAMILIAR-004` | vishing | 22 | — | =R L22 |
| `CV2-D-V-FAMILIAR-005` | vishing | 20 | — | <R L18 |
| `CV2-D-V-FAMILIAR-006` | vishing | 22 | — | <R L19 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | vishing | 12 | 19 | <R L2 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | vishing | 9 | 10 | <R L7 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | vishing | 11 | — | >R L13 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | vishing | 14 | — | <R L8 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | vishing | — | — | — |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | vishing | — | — | — |
| `CV2-D-V-PREMIO-001` | vishing | 10 | 13 | — |
| `CV2-D-V-PREMIO-002` | vishing | 13 | 16 | =R L13 |
| `CV2-D-V-PREMIO-003` | vishing | 13 | — | >R L19 |
| `CV2-D-V-PREMIO-004` | vishing | 14 | — | <R L12 |
| `CV2-D-V-PREMIO-005` | vishing | — | — | — |
| `CV2-D-V-PREMIO-006` | vishing | — | — | L17 |
| `CV2-D-V-SOPORTE-001` | vishing | 14 | — | <R L12 |
| `CV2-D-V-SOPORTE-002` | vishing | 13 | 20 | <R L7 |
| `CV2-D-V-SOPORTE-003` | vishing | 11 | 18 | <R L10 |
| `CV2-D-V-SOPORTE-004` | vishing | 14 | — | <R L13 |
| `CV2-D-V-SOPORTE-005` | vishing | 16 | — | <R L14 |
| `CV2-D-V-SOPORTE-006` | vishing | 15 | — | <R L10 |
| `CV2-D-V-SOPORTE-007` | vishing | — | — | — |
| `CV2-D-V-SOPORTE-008` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-001` | vishing | 9 | 20 | <R L7 |
| `CV2-D-V-WHATSAPP-002` | vishing | 10 | — | =R L10 |
| `CV2-D-V-WHATSAPP-003` | vishing | 12 | 19 | <R L8 |
| `CV2-D-V-WHATSAPP-004` | vishing | 13 | — | <R L9 |
| `CV2-D-V-WHATSAPP-005` | vishing | 14 | — | <R L10 |
| `CV2-D-V-WHATSAPP-006` | vishing | 25 | 31 | <R L24 |
| `CV2-D-V-WHATSAPP-007` | vishing | — | — | — |
| `CV2-D-V-WHATSAPP-008` | vishing | — | — | L9 |
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L5 |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L3 |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L2 |
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
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L6 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L11 |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L2 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | <R L5 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L3 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L5 |
| `TR-02-codigo-del-candado` | legítima | — | — | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L21 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L14 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L4 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L5 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L5 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 |

## Para revisar

### Falsas alarmas

- `CV2-D-L-BANCO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 2: «Te están pidiendo que verifiques información de tu cuenta bancaria, lo cual puede ser un intento de fraude para acceder a tus fondos.» — evidencia (cita textual): «OTRA: te atiendo soy mara del sector de movimientos lo ves en la cuenta sueldo o en la caja de ahorro»
- `CV2-D-L-BANCO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 7: «Te están pidiendo los últimos cuatro dígitos de tu cuenta para identificarla, lo cual podría permitirles acceder a tus operaciones bancarias.» — evidencia (cita textual): «OTRA: Con ese rango y la fecha puedo buscar las últimas operaciones. Para identificar la cuenta, decime los últimos cuatro dígitos.»
- `CV2-D-L-BANCO-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 8: «Te están pidiendo los últimos cuatro dígitos de tu cuenta para buscar ingresos, lo cual puede ser usado para acceder a tus fondos.» — evidencia (cita textual): «Para buscar ingresos pendientes, decime los últimos cuatro de la cuenta donde esperás recibirla.»
- `CV2-D-L-BANCO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 8: «La otra persona está pidiendo los últimos cuatro dígitos de la cuenta, lo cual es información sensible que podría usarse para acceder a la cuenta o realizar transacciones.» — evidencia (cita textual): «8. OTRA: Para encontrar la cuenta, me confirmás los últimos cuatro dígitos, por favor.»
- `CV2-D-L-BANCO-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 6: «La persona está pidiendo confirmar el número de cuenta para acceder a los movimientos, lo cual es un paso previo para intentar acceder o manipular la cuenta bancaria.» — evidencia (cita textual): «OTRA: Podemos recorrer los últimos movimientos. ¿La cuenta termina en 2609?»
- `CV2-D-L-BANCO-010` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 10: «Te están pidiendo los últimos cuatro números de tu cuenta bancaria para ubicar un comprobante de transferencia, lo cual podría permitirles acceder a tus fondos.» — evidencia (cita textual): «para ubicarla confirmame los últimos cuatro números de esa cuenta»
- `CV2-D-L-DELIVERY-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 17: «Te están pidiendo que firmes un recibo de una compra a nombre de otra persona, lo cual podría ser usado para tomar posesión de un bien o realizar una transacción no autorizada.» — evidencia (cita textual): «puede firmar con su nombre aunque la compra esté a nombre de ocampo»
- `CV2-D-L-ESCUELA-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 21: «Te están pidiendo firmar algo al dejar un objeto, lo cual podría ser un intento de obtener información o datos personales bajo un pretexto de entrega.» — evidencia (cita textual): «hay que firmar algo al dejarlo»
- `CV2-D-L-ESCUELA-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 8: «La otra persona está pidiendo que dictes el correo electrónico completo para actualizar la ficha de estudiante, lo cual podría ser un intento de obtener credenciales o acceder a cuentas.» — evidencia (cita textual): «8. OTRA: ¿Me lo podés dictar completo para evitar un error?»
- `CV2-D-L-FAMILIAR-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 11: «Te están pidiendo que envíes un alias por mensaje, lo cual podría ser para acceder a alguna cuenta o servicio.» — evidencia (cita textual): «11. Pasame el alias por mensaje así no lo tengo que copiar de memoria.»
- `CV2-D-L-FAMILIAR-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 10: «Te están pidiendo que envíes una foto y luego te inducen a transferir dinero, lo cual podría ser un intento de fraude.» — evidencia (cita textual): «7. PROTEGIDA: Mandame la foto para guardarla con los gastos de la casa.»
- `CV2-D-L-MEDICO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 16: «Te están pidiendo confirmar tu nombre y fecha de nacimiento para abrir un registro, lo cual puede ser usado para suplantar tu identidad.» — evidencia (cita textual): «te pueden pedir confirmar nombre y fecha de nacimiento para abrir el registro»
- `CV2-D-L-ORGANISMO_PREVISIONAL-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 17: «Te están pidiendo que dictes el número de documento, lo cual es un dato personal que puede ser usado para suplantación o fraude.» — evidencia (cita textual): «17. PROTEGIDA: ¿Te dicto el número de documento ahora?»
- `CV2-D-L-PREMIO-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 11: «La otra persona está pidiendo modificar el correo vinculado a una entrada, lo cual podría ser un intento de tomar control de la información o el sorteo.» — evidencia (cita textual): «10. OTRA: Puedo modificar el correo vinculado a esta entrada. ¿El evento es la feria del domingo en el galpón municipal?»
- `CV2-D-L-SOPORTE-004` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 11: «No le des la clave del programa, ya que te están pidiendo que la compartas, lo cual podría comprometer la licencia o la cuenta asociada.» — evidencia (cita textual): «11. PROTEGIDA: Ese debe ser. ¿Me vas a pedir que te pase la clave del programa?»
- `CV2-D-L-SOPORTE-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 10: «Te están pidiendo que le des una clave a la impresora para cargarla, lo cual podría ser un intento de acceder a dispositivos o información.» — evidencia (cita textual): «10. OTRA: Pedile esa clave y cargala directamente en la impresora.»
- `CV2-D-L-TRABAJO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 20: «Te están pidiendo que transfieras dinero, lo cual es una solicitud directa de transferencia de fondos.» — evidencia (cita textual): «sí uno chico sin azúcar después te transfiero lo mío»
- `CV2-D-L-TRABAJO-003` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 11: «Te están pidiendo que envíes una foto de una página interna, lo cual podría ser un intento de obtener acceso a información sensible o credenciales.» — evidencia (cita textual): «10. OTRA: Eso confirma el cambio de turno. Mandame una foto de esa página por el canal interno.»
- `CV2-D-L-WHATSAPP-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 16: «Te están pidiendo que ingreses seis números en la pantalla de la aplicación, lo cual podría ser para acceder a una cuenta o realizar alguna acción no autorizada.» — evidencia (cita textual): «16. OTRA: Que los ingrese en la pantalla de la aplicación.»
- `CV2-D-L-WHATSAPP-002` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 14: «Te están pidiendo que elimines un historial de chat para ocultar información, lo cual podría ser para ocultar actividades o información sensible de la cuenta.» — evidencia (cita textual): «Entonces ya no recibís novedades. Para ocultar ese historial, mantené apretado el chat y tocá eliminar.»
- `LAB-anses-canal-oficial` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 5: «Te están pidiendo datos personales bajo la promesa de un bono, lo cual es una táctica común para el robo de identidad o fraude.» — evidencia (cita textual): «PROTEGIDA: me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 3: «Te están pidiendo que ingreses a una página web para resolver un supuesto embargo, lo cual es una táctica común para robar tus datos o dinero.» — evidencia (cita textual): «OTRA: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-app-parafrasis` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 2: «Te están pidiendo que cortes la llamada y revises la aplicación del banco, lo cual puede ser un intento de redirigirte a un enlace malicioso o pedirte credenciales.» — evidencia (cita textual): «OTRA: corta aca y fijate vos en la app del banco»
- `LAB-banco-gasto-sin-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 3: «Te están pidiendo que ingreses a una aplicación para revisar un gasto, lo cual puede ser un intento de phishing o robo de credenciales.» — evidencia (cita textual): «OTRA: entra vos a la aplicacion cuando puedas y fijate»
- `LAB-banco-revisa-app` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 3: «Te están pidiendo que cortes la comunicación y accedas a una aplicación oficial, lo cual es una táctica común para robar tus credenciales o acceder a tus cuentas bancarias.» — evidencia (cita textual): «OTRA: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 3: «Te están pidiendo que llames a un número guardado, lo cual podría ser para acceder a una cuenta o realizar alguna acción no autorizada.» — evidencia (cita textual): «OTRA: llama vos al numero que tenes guardado»
- `LAB-no-bajes-nada` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 4: «Te están pidiendo que descargues un programa y les muestres tu celular, lo cual puede permitirles acceder a tu dispositivo y robar tus cuentas.» — evidencia (cita textual): «PROTEGIDA: me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 6: «No le des los últimos números de tu tarjeta a nadie, ya que podrían intentar clonar tu tarjeta o acceder a tu cuenta.» — evidencia (cita textual): «PROTEGIDA: ¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `LG-SUPPORT-INFO-01-e02` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 11: «La persona te está preguntando si necesita pasarle algún dato después de ingresar a la aplicación del banco, lo cual podría ser una solicitud para obtener credenciales o información de acceso.» — evidencia (cita textual): «11. PROTEGIDA: Entré, ya veo mis movimientos. ¿No hace falta que te pase algún dato?»
- `TR-05-asado-con-transferencia` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 14: «Te están pidiendo un alias para realizar una transferencia de dinero, lo cual podría ser para robar tus cuentas.» — evidencia (cita textual): «Mandame el alias que ahora no lo tengo a mano.»
- `TR-06-banco-alerta-legitima` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 4: «Te están llamando haciéndose pasar por el banco para obtener información sobre un consumo sospechoso en tu tarjeta de crédito, lo cual puede llevar a un fraude.» — evidencia (cita textual): «OTRA: Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 3: «Te están pidiendo un código; no le des nada a nadie, ya que podría ser un código de verificación o activación para acceder a tus cuentas.» — evidencia (cita textual): «OTRA: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 9: «Te están pidiendo transferir veinte mil pesos a una cuenta, lo cual es una solicitud de dinero que puede ser una estafa.» — evidencia (cita textual): «OTRA: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento, datos personales que pueden ser usados para suplantar tu identidad.» — evidencia (cita textual): «OTRA: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `CV2-D-V-ORGANISMO_PREVISIONAL-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.30
- `CV2-D-V-ORGANISMO_PREVISIONAL-006` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.30
- `CV2-D-V-PREMIO-001` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · sin riesgo registrado
- `CV2-D-V-PREMIO-005` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.20
- `CV2-D-V-SOPORTE-008` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.20
- `CV2-D-V-WHATSAPP-007` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.30
- `TR-12-corta-antes-del-pedido` · `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol` · riesgo máximo 0.20

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `gemma4:e2b-it-q4_K_M` | 15.153 | 315 | 315 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Sin indicio (`--sin-indicio`): Tito solo decide cuándo consultar; el SLM recibe el mismo mensaje que el SLM solo, sin bloque de indicio ni de fallo técnico.
Modo de término: `operativo-hasta-aviso`: cada llamada termina en su primer aviso válido.
Arranque Tito (artefacto): 0 ms; encoder: 13.824 ms (carga fresca); calentamiento Tito: 88 ms (unidad: ms)
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm-sin-indicio|gemma4:e2b-it-q4_K_M|v3|rol`

Consultas al SLM hasta el aviso: 760; evitadas por el filtro: 1139; costo Tito+SLM hasta el aviso: 600.620 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms hasta aviso |
|---|---|---|---|---|---|---|
| `CV2-D-L-BANCO-001` | 1 | L2 | 2 | 0 | 0 | 1.977 |
| `CV2-D-L-BANCO-002` | 7 | L7 | 1 | 6 | 0 | 1.667 |
| `CV2-D-L-BANCO-003` | nunca | sin aviso | 0 | 22 | 0 | 2.542 |
| `CV2-D-L-BANCO-004` | 5 | L8 | 4 | 4 | 0 | 3.589 |
| `CV2-D-L-BANCO-005` | 8 | L8 | 1 | 7 | 0 | 1.901 |
| `CV2-D-L-BANCO-006` | 6 | L6 | 1 | 5 | 0 | 1.634 |
| `CV2-D-L-BANCO-007` | nunca | sin aviso | 0 | 23 | 0 | 2.424 |
| `CV2-D-L-BANCO-008` | nunca | sin aviso | 0 | 21 | 0 | 2.305 |
| `CV2-D-L-BANCO-009` | nunca | sin aviso | 0 | 22 | 0 | 2.418 |
| `CV2-D-L-BANCO-010` | 10 | L10 | 1 | 9 | 0 | 2.268 |
| `CV2-D-L-DELIVERY-001` | 6 | L17 | 12 | 5 | 0 | 7.929 |
| `CV2-D-L-DELIVERY-002` | nunca | sin aviso | 0 | 25 | 0 | 2.640 |
| `CV2-D-L-DELIVERY-003` | 3 | sin aviso | 23 | 2 | 0 | 11.324 |
| `CV2-D-L-DELIVERY-004` | nunca | sin aviso | 0 | 24 | 0 | 2.659 |
| `CV2-D-L-DELIVERY-005` | nunca | sin aviso | 0 | 25 | 0 | 2.926 |
| `CV2-D-L-ESCUELA-001` | nunca | sin aviso | 0 | 24 | 0 | 3.052 |
| `CV2-D-L-ESCUELA-002` | 3 | L21 | 19 | 2 | 0 | 10.052 |
| `CV2-D-L-ESCUELA-003` | nunca | sin aviso | 0 | 24 | 0 | 2.883 |
| `CV2-D-L-ESCUELA-004` | 7 | L8 | 2 | 6 | 0 | 2.726 |
| `CV2-D-L-ESCUELA-005` | 1 | sin aviso | 26 | 0 | 0 | 10.692 |
| `CV2-D-L-FAMILIAR-001` | nunca | sin aviso | 0 | 24 | 0 | 3.013 |
| `CV2-D-L-FAMILIAR-002` | 11 | L11 | 1 | 10 | 0 | 2.627 |
| `CV2-D-L-FAMILIAR-003` | 20 | sin aviso | 5 | 19 | 0 | 4.323 |
| `CV2-D-L-FAMILIAR-004` | 17 | sin aviso | 8 | 16 | 0 | 5.264 |
| `CV2-D-L-FAMILIAR-005` | 10 | L10 | 1 | 9 | 0 | 2.251 |
| `CV2-D-L-MEDICO-001` | nunca | sin aviso | 0 | 25 | 0 | 3.240 |
| `CV2-D-L-MEDICO-002` | 7 | L16 | 10 | 6 | 0 | 6.484 |
| `CV2-D-L-MEDICO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.879 |
| `CV2-D-L-MEDICO-004` | nunca | sin aviso | 0 | 25 | 0 | 2.762 |
| `CV2-D-L-MEDICO-005` | 10 | sin aviso | 17 | 9 | 0 | 9.261 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-001` | 6 | L17 | 12 | 5 | 0 | 7.905 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-002` | nunca | sin aviso | 0 | 24 | 0 | 3.200 |
| `CV2-D-L-ORGANISMO_PREVISIONAL-003` | 14 | sin aviso | 14 | 13 | 0 | 8.444 |
| `CV2-D-L-PREMIO-001` | nunca | sin aviso | 0 | 24 | 0 | 2.642 |
| `CV2-D-L-PREMIO-002` | 5 | L11 | 7 | 4 | 0 | 5.454 |
| `CV2-D-L-PREMIO-003` | nunca | sin aviso | 0 | 25 | 0 | 2.674 |
| `CV2-D-L-SOPORTE-001` | nunca | sin aviso | 0 | 25 | 0 | 2.762 |
| `CV2-D-L-SOPORTE-002` | 10 | sin aviso | 17 | 9 | 0 | 10.409 |
| `CV2-D-L-SOPORTE-003` | 6 | sin aviso | 20 | 5 | 0 | 10.352 |
| `CV2-D-L-SOPORTE-004` | 1 | L11 | 11 | 0 | 0 | 6.961 |
| `CV2-D-L-SOPORTE-005` | 10 | L10 | 1 | 9 | 0 | 2.082 |
| `CV2-D-L-TRABAJO-001` | 2 | L20 | 19 | 1 | 0 | 11.035 |
| `CV2-D-L-TRABAJO-002` | 5 | sin aviso | 21 | 4 | 0 | 9.852 |
| `CV2-D-L-TRABAJO-003` | 10 | L11 | 2 | 9 | 0 | 2.973 |
| `CV2-D-L-TRABAJO-004` | nunca | sin aviso | 0 | 25 | 0 | 3.459 |
| `CV2-D-L-TRABAJO-005` | 1 | sin aviso | 27 | 0 | 0 | 12.774 |
| `CV2-D-L-WHATSAPP-001` | 16 | L16 | 1 | 15 | 0 | 3.467 |
| `CV2-D-L-WHATSAPP-002` | 10 | L14 | 5 | 9 | 0 | 4.062 |
| `CV2-D-L-WHATSAPP-003` | 12 | sin aviso | 14 | 11 | 0 | 8.950 |
| `CV2-D-L-WHATSAPP-004` | 8 | sin aviso | 18 | 7 | 0 | 11.024 |
| `CV2-D-L-WHATSAPP-005` | 2 | sin aviso | 23 | 1 | 0 | 15.789 |
| `CV2-D-V-BANCO-001` | 29 | L29 | 1 | 28 | 0 | 4.639 |
| `CV2-D-V-BANCO-002` | 6 | L10 | 5 | 5 | 0 | 4.324 |
| `CV2-D-V-BANCO-003` | 5 | L11 | 7 | 4 | 0 | 4.817 |
| `CV2-D-V-BANCO-004` | 10 | L10 | 1 | 9 | 0 | 2.154 |
| `CV2-D-V-BANCO-005` | 1 | L2 | 2 | 0 | 0 | 1.591 |
| `CV2-D-V-BANCO-006` | 2 | L8 | 7 | 1 | 0 | 4.940 |
| `CV2-D-V-BANCO-007` | 11 | L11 | 1 | 10 | 0 | 2.480 |
| `CV2-D-V-BANCO-008` | 16 | L16 | 1 | 15 | 0 | 2.768 |
| `CV2-D-V-BANCO-009` | 3 | L9 | 7 | 2 | 0 | 4.211 |
| `CV2-D-V-BANCO-010` | 1 | L1 | 1 | 0 | 0 | 1.130 |
| `CV2-D-V-BANCO-011` | 12 | L12 | 1 | 11 | 0 | 2.330 |
| `CV2-D-V-BANCO-012` | 1 | L5 | 5 | 0 | 0 | 3.356 |
| `CV2-D-V-FAMILIAR-001` | 5 | L15 | 11 | 4 | 0 | 6.228 |
| `CV2-D-V-FAMILIAR-002` | 16 | L16 | 1 | 15 | 0 | 2.756 |
| `CV2-D-V-FAMILIAR-003` | 14 | L14 | 1 | 13 | 0 | 2.463 |
| `CV2-D-V-FAMILIAR-004` | 14 | L22 | 9 | 13 | 0 | 6.565 |
| `CV2-D-V-FAMILIAR-005` | 18 | L18 | 1 | 17 | 0 | 2.936 |
| `CV2-D-V-FAMILIAR-006` | 17 | L19 | 3 | 16 | 0 | 3.536 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-001` | 2 | L2 | 1 | 1 | 0 | 1.071 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-002` | 1 | L7 | 7 | 0 | 0 | 5.006 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-003` | 13 | L13 | 1 | 12 | 0 | 3.120 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-004` | 2 | L8 | 7 | 1 | 0 | 4.267 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-005` | 2 | sin aviso | 22 | 1 | 0 | 12.557 |
| `CV2-D-V-ORGANISMO_PREVISIONAL-006` | 1 | sin aviso | 22 | 0 | 0 | 12.902 |
| `CV2-D-V-PREMIO-001` | nunca | sin aviso | 0 | 21 | 0 | 2.080 |
| `CV2-D-V-PREMIO-002` | 3 | L13 | 11 | 2 | 0 | 6.676 |
| `CV2-D-V-PREMIO-003` | 3 | L19 | 17 | 2 | 0 | 10.081 |
| `CV2-D-V-PREMIO-004` | 12 | L12 | 1 | 11 | 0 | 2.152 |
| `CV2-D-V-PREMIO-005` | 4 | sin aviso | 20 | 3 | 0 | 11.857 |
| `CV2-D-V-PREMIO-006` | 1 | L17 | 17 | 0 | 0 | 9.688 |
| `CV2-D-V-SOPORTE-001` | 12 | L12 | 1 | 11 | 0 | 2.664 |
| `CV2-D-V-SOPORTE-002` | 1 | L7 | 7 | 0 | 0 | 4.159 |
| `CV2-D-V-SOPORTE-003` | 1 | L10 | 10 | 0 | 0 | 5.282 |
| `CV2-D-V-SOPORTE-004` | 13 | L13 | 1 | 12 | 0 | 2.578 |
| `CV2-D-V-SOPORTE-005` | 10 | L14 | 5 | 9 | 0 | 5.501 |
| `CV2-D-V-SOPORTE-006` | 1 | L10 | 10 | 0 | 0 | 5.134 |
| `CV2-D-V-SOPORTE-007` | 18 | sin aviso | 4 | 17 | 0 | 5.462 |
| `CV2-D-V-SOPORTE-008` | 19 | sin aviso | 4 | 18 | 0 | 4.824 |
| `CV2-D-V-WHATSAPP-001` | 1 | L7 | 7 | 0 | 0 | 3.837 |
| `CV2-D-V-WHATSAPP-002` | 10 | L10 | 1 | 9 | 0 | 2.082 |
| `CV2-D-V-WHATSAPP-003` | 8 | L8 | 1 | 7 | 0 | 1.785 |
| `CV2-D-V-WHATSAPP-004` | 5 | L9 | 5 | 4 | 0 | 3.779 |
| `CV2-D-V-WHATSAPP-005` | 10 | L10 | 1 | 9 | 0 | 2.274 |
| `CV2-D-V-WHATSAPP-006` | 22 | L24 | 3 | 21 | 0 | 4.746 |
| `CV2-D-V-WHATSAPP-007` | 8 | sin aviso | 14 | 7 | 0 | 8.845 |
| `CV2-D-V-WHATSAPP-008` | 9 | L9 | 1 | 8 | 0 | 2.173 |
| `LAB-acceso-remoto` | 1 | L3 | 3 | 0 | 0 | 2.083 |
| `LAB-acceso-remoto-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.928 |
| `LAB-anses-beneficio` | 1 | L3 | 3 | 0 | 0 | 2.058 |
| `LAB-anses-beneficio-parafrasis` | 1 | L3 | 3 | 0 | 0 | 2.004 |
| `LAB-anses-canal-oficial` | 5 | L5 | 1 | 4 | 0 | 1.395 |
| `LAB-arca-canal-oficial` | 1 | L3 | 3 | 0 | 0 | 2.243 |
| `LAB-arca-deuda` | 1 | L3 | 3 | 0 | 0 | 2.175 |
| `LAB-arca-deuda-parafrasis` | 3 | L3 | 1 | 2 | 0 | 1.565 |
| `LAB-banco-app-parafrasis` | 1 | L2 | 2 | 0 | 0 | 1.557 |
| `LAB-banco-codigo` | 1 | L3 | 3 | 0 | 0 | 1.938 |
| `LAB-banco-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.876 |
| `LAB-banco-gasto-sin-pedido` | 1 | L3 | 3 | 0 | 0 | 1.861 |
| `LAB-banco-niega-el-codigo` | 2 | sin aviso | 1 | 1 | 0 | 662 |
| `LAB-banco-numeros-sin-clave` | 1 | L3 | 3 | 0 | 0 | 1.878 |
| `LAB-banco-revisa-app` | 3 | L3 | 1 | 2 | 0 | 1.384 |
| `LAB-digitos-sin-palabra` | 1 | L3 | 3 | 0 | 0 | 2.271 |
| `LAB-familiar-llama-vos` | 2 | L3 | 2 | 1 | 0 | 1.742 |
| `LAB-familiar-peligro` | 1 | L4 | 4 | 0 | 0 | 2.520 |
| `LAB-familiar-peligro-parafrasis` | 1 | L4 | 4 | 0 | 0 | 2.594 |
| `LAB-giro-sin-plata` | 1 | L3 | 3 | 0 | 0 | 1.758 |
| `LAB-mensajeria-no-pases-nada` | 1 | sin aviso | 5 | 0 | 0 | 2.860 |
| `LAB-no-bajes-nada` | 4 | L4 | 1 | 3 | 0 | 1.459 |
| `LAB-pantalla-sin-programa` | 1 | L3 | 3 | 0 | 0 | 2.076 |
| `LAB-portero-codigo-puerta` | 2 | sin aviso | 1 | 1 | 0 | 983 |
| `LAB-whatsapp-codigo` | 1 | L1 | 1 | 0 | 0 | 1.002 |
| `LAB-whatsapp-codigo-parafrasis` | 1 | L3 | 3 | 0 | 0 | 1.979 |
| `LG-BANK-VERIF-01-e01` | 6 | L6 | 1 | 5 | 0 | 1.608 |
| `LG-FAMILIAR-LLAMADO-01-e01` | 11 | sin aviso | 2 | 10 | 0 | 2.402 |
| `LG-ORG-TURNO-01-e01` | nunca | sin aviso | 0 | 13 | 0 | 1.524 |
| `LG-PREMIO-CONSULTA-01-e01` | 8 | sin aviso | 5 | 7 | 0 | 4.747 |
| `LG-SUPPORT-INFO-01-e01` | 7 | sin aviso | 7 | 6 | 0 | 5.276 |
| `LG-SUPPORT-INFO-01-e02` | 8 | L11 | 4 | 7 | 0 | 3.732 |
| `LG-WA-CONSULTA-01-e01` | nunca | sin aviso | 0 | 4 | 0 | 413 |
| `SC-CLAVE-CAMBIO-01-e01` | 2 | L2 | 1 | 1 | 0 | 1.123 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 1 | 8 | 0 | 2.174 |
| `SC-ORG-BENEFICIO-01-e01` | 3 | L5 | 3 | 2 | 0 | 3.288 |
| `SC-PREMIO-01-e01` | 3 | L8 | 6 | 2 | 0 | 4.780 |
| `SC-SOPORTE-CLAVE-01-e01` | 3 | L6 | 4 | 2 | 0 | 3.358 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 3 | 0 | 0 | 2.430 |
| `SC-WA-CODE-01-e01` | 1 | L3 | 3 | 0 | 0 | 1.919 |
| `TR-01-pedido-indirecto-digitos` | 3 | L5 | 3 | 2 | 0 | 3.078 |
| `TR-02-codigo-del-candado` | 2 | sin aviso | 7 | 1 | 0 | 4.333 |
| `TR-03-negacion-y-consejo` | nunca | sin aviso | 0 | 10 | 0 | 1.136 |
| `TR-04-pedido-tras-charla-larga` | 5 | L21 | 17 | 4 | 0 | 8.780 |
| `TR-05-asado-con-transferencia` | 14 | L14 | 1 | 13 | 0 | 2.962 |
| `TR-06-banco-alerta-legitima` | 3 | L4 | 2 | 2 | 0 | 1.992 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L5 | 1 | 4 | 0 | 1.464 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 1 | 2 | 0 | 1.071 |
| `TR-09-victima-se-niega` | 3 | L3 | 1 | 2 | 0 | 1.647 |
| `TR-10-ofrecimiento-inducido` | 4 | L5 | 2 | 3 | 0 | 2.041 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 1 | 8 | 0 | 1.911 |
| `TR-12-corta-antes-del-pedido` | 6 | sin aviso | 5 | 5 | 0 | 4.120 |
| `TR-13-turno-medico-pide-dni` | 5 | L5 | 1 | 4 | 0 | 1.668 |

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
| `tito-slm-sin-indicio\|gemma4:e2b-it-q4_K_M\|v3\|rol` | 600.620 | 146.075 | 454.546 | 851795 | 1899 | 760/0 |

Tito ms cuenta solo las líneas donde Tito puntuó (hasta la activación); SLM ms, solo las consultas al SLM. `Actualiz.` cuenta las actualizaciones evaluadas hasta el aviso en el mismo alcance que los costos, fallos incluidos. `Runtime` cuenta solo actualizaciones que consultaron al SLM: con dato o ausente explícito; las omitidas por el filtro (1139 en esta corrida) no consultan y no cuentan como ausencia.
