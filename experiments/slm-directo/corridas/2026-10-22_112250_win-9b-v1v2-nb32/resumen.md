# Resumen de la corrida `2026-10-22_112250_win-9b-v1v2-nb32`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:9b-q4_K_M --prompts tarea,v2 --num-batch 32 --sin-reglas --timeout 300 --etiqueta win-9b-v1v2-nb32 --url http://127.0.0.1:11435`
- **Inicio / fin:** 2026-10-22T11:22:50 / 2026-10-22T11:44:38
- **Código:** `886cff0633`
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` | 29/29 | 17 | 11 | 0 | 0 | 17/24 | 0/464 | 978 | 2.919 | 46/46 | 0 |
| `slm\|qwen3.5:9b-q4_K_M\|v2\|ab` | 28/29 | 3 | 25 | 0 | 0 | 8/24 | 0/464 | 929 | 1.999 | 36/36 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` · **C2** `slm\|qwen3.5:9b-q4_K_M\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | <R L1 | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | FA L1 | FA L1 |
| `LAB-arca-canal-oficial` | legítima | — | — | FA L3 | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-banco-app-parafrasis` | legítima | — | — | FA L3 | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | <R L3 | <R L3 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | <R L3 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | FA L3 | FA L3 |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | <R L3 | <R L3 |
| `LAB-familiar-llama-vos` | legítima | — | — | FA L3 | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | <R L3 | =R L4 |
| `LAB-giro-sin-plata` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | FA L2 | ok |
| `LAB-no-bajes-nada` | legítima | — | — | FA L1 | FA L1 |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | =R L3 | =R L3 |
| `LAB-portero-codigo-puerta` | legítima | — | — | ok | ok |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | <R L1 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L6 | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L6 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L4 | FA L4 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | ok | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | <R L4 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | <R L5 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L5 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | =R L6 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | <R L2 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | <R L3 | =R L8 |
| `TR-02-codigo-del-candado` | legítima | — | — | FA L6 | ok |
| `TR-03-negacion-y-consejo` | legítima | — | — | ok | ok |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L23 | <R L25 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L13 | ok |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L4 | =R L7 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | <R L3 | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 | =R L8 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | L6 | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | FA L5 | FA L5 |

## Para revisar

### Falsas alarmas

- `LAB-anses-canal-oficial` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo datos sensibles de un organismo público, lo cual es una forma común de estafa para robar tu identidad o acceder a fondos.» — evidencia (cita textual): «me ofrecieron un bono si les doy datos del organismo»
- `LAB-arca-canal-oficial` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están indicando que no abras enlaces ni entres a sitios desde el correo, pero te piden ir a la página oficial para resolver una deuda o embargo, lo cual es una táctica clásica de estafa para llevarte a un sitio falso donde robarán tus datos.» — evidencia (cita textual): «A: me llego un mail de una deuda y un embargo
B: no abras ningun sitio del mensaje
B: la unica via es entrar vos a la pagina oficial»
- `LAB-banco-app-parafrasis` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que ingreses a tu app bancaria y revises movimientos usando tu huella, lo cual implica compartir tu dispositivo o validar acciones fraudulentas.» — evidencia (cita textual): «A: corta aca y fijate vos en la app del banco
2. B: dale a ver
3. A: entra con tu huella y revisa los movimientos»
- `LAB-banco-revisa-app` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo que cortes la comunicación para entrar a tu aplicación y validar un consumo falso.» — evidencia (cita textual): «A: corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-familiar-llama-vos` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están presionando para que ignores a quien te llamó y llames a un número guardado, lo cual es una táctica común para desviarte de la línea segura y evitar que verifiques su identidad o pidas ayuda real.» — evidencia (cita textual): «B: corta
B: llama vos al numero que tenes guardado»
- `LAB-mensajeria-no-pases-nada` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 2: «Te están intentando suplantar identidad para acceder a tu cuenta de mensajes; no compartas códigos ni datos personales.» — evidencia (cita textual): «A: me llamo alguien que dice ser soporte de la aplicacion de mensajes»
- `LAB-no-bajes-nada` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 1: «Te están pidiendo instalar un programa para acceder a tu celular y robar tus datos o dinero.» — evidencia (cita textual): «me llamaron para que baje un programa y les muestre el celular»
- `LG-BANK-VERIF-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 6: «Te están pidiendo datos sensibles de tu tarjeta (números) para intentar acceder a tu cuenta o validar una supuesta identidad.» — evidencia (cita textual): «¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `LG-FAMILIAR-LLAMADO-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 7: «Te están pidiendo que transfieras dinero bajo una emergencia falsa; no des datos bancarios ni envíes plata hasta confirmar la situación por otro medio.» — evidencia (cita textual): «7. A: ¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 6: «El interlocutor está intentando obtener tus datos personales (DNI) para verificar tu situación, lo cual es una táctica común de estafa.» — evidencia (cita textual): «B: ¿Y vos no necesitás mis datos para fijarte si estoy en el listado?»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 4: «Te están intentando convencer para que les des tu usuario y contraseña porque dicen que no podés entrar a tu cuenta.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `TR-02-codigo-del-candado` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 6: «Te están pidiendo el código de acceso a una puerta física para entrar a tu propiedad y tomar objetos.» — evidencia (cita textual): «3. A: Dale. ¿Cuál era el código del candado? Me lo dijiste el otro día y no me acuerdo.
4. B: Cero, cero, cero, cero. Nunca lo cambié, ya sé que es un desastre.»
- `TR-05-asado-con-transferencia` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 13: «Te están pidiendo que hagas una transferencia antes del viernes para pagar tu parte de un asado.» — evidencia (cita textual): «A: Si podés, pasámelos por transferencia antes del viernes, así le devuelvo a Lucho, que pagó todo él con la tarjeta.»
- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 10: «El estafador intenta recuperar tu confianza tras advertirte para luego pedirte un código de verificación que él mismo dice no necesitar, con el fin de acceder a tus cuentas.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código de verificación o acceso a tu cuenta sin haber establecido una identidad confiable.» — evidencia (cita textual): «3. A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo que hagas una transferencia de dinero directamente.» — evidencia (cita textual): «¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 5: «Te están pidiendo tu número de documento y fecha de nacimiento para buscar tus datos en el sistema.» — evidencia (cita textual): «A: Bien. Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»
- `LAB-anses-canal-oficial` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 1: «Te están pidiendo que entregues datos personales a cambio de un beneficio.» — evidencia (cita textual): «me ofrecieron un bono si les doy datos del organismo»
- `LAB-banco-revisa-app` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 3: «Te están pidiendo que abandones la llamada segura para acceder a tu aplicación bancaria desde un dispositivo no verificado, lo cual es una táctica común para instalar malware o robar tus credenciales.» — evidencia (cita textual): «corta esta comunicacion y entra vos a la aplicacion oficial»
- `LAB-no-bajes-nada` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 1: «Te están pidiendo instalar un programa y compartir tu pantalla o dejar que te vean manejar tu celular, lo cual permite robar tus datos o dinero.» — evidencia (cita textual): «me llamaron para que baje un programa y les muestre el celular»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 4: «Te están pidiendo que le des tus claves o usuario para que verifiquen tu cuenta.» — evidencia (cita textual): «Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 10: «No compartas ese código ni se lo dictes; es para validar tu identidad y robar tu cuenta.» — evidencia (cita textual): «Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 3: «Te están pidiendo que le dictes un código de verificación o SMS, lo cual es una estafa para robar tus cuentas.» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 4: «Te están pidiendo que transfieras dinero directamente por la llamada.» — evidencia (cita textual): «¿Me podrás transferir veinte mil pesos?»
- `TR-13-turno-medico-pide-dni` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 5: «Te están pidiendo datos personales sensibles (DNI y fecha de nacimiento) para acceder a tu información médica o financiera.» — evidencia (cita textual): «Decime tu número de documento y la fecha de nacimiento, así te busco en el sistema.»

### Vishing sin aviso

- `TR-12-corta-antes-del-pedido` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · riesgo máximo 0.30

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:9b-q4_K_M` | 22.081 | 5.247 | 5.247 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
