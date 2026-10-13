# Resumen de la corrida `2026-10-13_224418_linea-base-reglas`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --solo-reglas --etiqueta linea-base-reglas`
- **Inicio / fin:** 2026-10-13T22:44:18 / 2026-10-13T22:44:21
- **Código:** `96ded89a32`
- **Máquina:** Linux-6.18.44-fc-v114-x86_64-with-glibc2.39, 4 núcleos lógicos, 15.7 GB de RAM
- **Ollama:** no usado · **Política:** aviso_unico_primer_true_valido
- **Casos:** 53 (29 vishing, 24 legítimas); 53 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual |
|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 23/29 | 5 | 15 | 3 | 0 | 14/24 | 0/464 | 7 | 18 | 37/37 |

«Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 |
|---|---|---|---|---|
| `LAB-acceso-remoto` | vishing | 3 | — | =R L3 |
| `LAB-acceso-remoto-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio` | vishing | 3 | — | =R L3 |
| `LAB-anses-beneficio-parafrasis` | vishing | 3 | — | =R L3 |
| `LAB-anses-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-canal-oficial` | legítima | — | — | ok |
| `LAB-arca-deuda` | vishing | 3 | — | =R L3 |
| `LAB-arca-deuda-parafrasis` | vishing | 3 | — | >R L5 |
| `LAB-banco-app-parafrasis` | legítima | — | — | ok |
| `LAB-banco-codigo` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-codigo-parafrasis` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-gasto-sin-pedido` | legítima | — | — | ok |
| `LAB-banco-niega-el-codigo` | legítima | — | — | ok |
| `LAB-banco-numeros-sin-clave` | vishing | 5 | 6 | =R L5 |
| `LAB-banco-revisa-app` | legítima | — | — | ok |
| `LAB-digitos-sin-palabra` | vishing | 5 | — | — |
| `LAB-familiar-llama-vos` | legítima | — | — | ok |
| `LAB-familiar-peligro` | vishing | 4 | — | =R L4 |
| `LAB-familiar-peligro-parafrasis` | vishing | 4 | — | >R L6 |
| `LAB-giro-sin-plata` | vishing | 3 | — | — |
| `LAB-mensajeria-no-pases-nada` | legítima | — | — | ok |
| `LAB-no-bajes-nada` | legítima | — | — | ok |
| `LAB-pantalla-sin-programa` | vishing | 3 | — | — |
| `LAB-portero-codigo-puerta` | legítima | — | — | FA L1 |
| `LAB-whatsapp-codigo` | vishing | 3 | 4 | =R L3 |
| `LAB-whatsapp-codigo-parafrasis` | vishing | 3 | 4 | =R L3 |
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | FA L9 |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L2 |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L4 |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | — |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 |
| `TR-01-pedido-indirecto-digitos` | vishing | 8 | 11 | — |
| `TR-02-codigo-del-candado` | legítima | — | — | FA L3 |
| `TR-03-negacion-y-consejo` | legítima | — | — | FA L2 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L6 |
| `TR-05-asado-con-transferencia` | legítima | — | — | FA L5 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 |
| `TR-09-victima-se-niega` | vishing | 5 | — | =R L5 |
| `TR-10-ofrecimiento-inducido` | vishing | 8 | 13 | <R L4 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 |
| `TR-12-corta-antes-del-pedido` | vishing | — | — | — |
| `TR-13-turno-medico-pide-dni` | legítima | — | — | ok |

## Para revisar

### Falsas alarmas

- `LAB-portero-codigo-puerta` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «el portero me paso el codigo de la puerta»
- `LG-BANK-VERIF-01-e01` · `reglas` · línea 2: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Hola, Lucía. Llamo al número que está atrás de mi tarjeta. Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `LG-FAMILIAR-LLAMADO-01-e01` · `reglas` · línea 7: «REQUEST_TRANSFER (patrón: plata)» — evidencia (cita textual): «¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-ORG-TURNO-01-e01` · `reglas` · línea 4: «REQUEST_PERSONAL_DATA (patrón: domicilio)» — evidencia (cita textual): «¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-PREMIO-CONSULTA-01-e01` · `reglas` · línea 9: «REQUEST_TRANSFER (patrón: paga)» — evidencia (cita textual): «A ver... sí, acá lo dice. ¿Y hay que pagar algo para retirarlo? ¿Un gasto de envío, algo así?»
- `LG-SUPPORT-INFO-01-e01` · `reglas` · línea 2: «REQUEST_SECRET (patrón: contrasena)» — evidencia (cita textual): «Hola, ¿qué tal? Los llamo porque no puedo entrar a mi cuenta desde la computadora: me dice que el usuario o la contraseña son incorrectos.»
- `LG-SUPPORT-INFO-01-e02` · `reglas` · línea 4: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «No, eso no. Nosotros no te vamos a pedir que compartas la pantalla ni que instales nada para que alguien entre a tu celular.»
- `LG-WA-CONSULTA-01-e01` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `TR-02-codigo-del-candado` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Dale. ¿Cuál era el código del candado? Me lo dijiste el otro día y no me acuerdo.»
- `TR-03-negacion-y-consejo` · `reglas` · línea 2: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Bien que me llames, ma. Escuchame una cosa: nunca le pases la clave del banco a nadie, ni a mí.»
- `TR-05-asado-con-transferencia` · `reglas` · línea 5: «REQUEST_TRANSFER (patrón: plata)» — evidencia (cita textual): «No, el carbón ya lo compró él. Escuchá, te llamaba por la plata, que la estoy juntando yo.»
- `TR-06-banco-alerta-legitima` · `reglas` · línea 10: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `reglas` · línea 3: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `reglas` · línea 4: «REQUEST_TRANSFER (patrón: transferi)» — evidencia (cita textual): «Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»

### Vishing sin aviso

- `LAB-digitos-sin-palabra` · `reglas` · sin riesgo registrado
- `LAB-giro-sin-plata` · `reglas` · sin riesgo registrado
- `LAB-pantalla-sin-programa` · `reglas` · sin riesgo registrado
- `SC-PREMIO-01-e01` · `reglas` · sin riesgo registrado
- `TR-01-pedido-indirecto-digitos` · `reglas` · sin riesgo registrado
- `TR-12-corta-antes-del-pedido` · `reglas` · sin riesgo registrado

### Fallos por tipo

Ninguno.

## Trayectorias de riesgo

Riesgo por línea; entre corchetes, la línea del aviso; `x` = fallo.

```text
reglas
  LAB-acceso-remoto                          · · [·] · ·
  LAB-acceso-remoto-parafrasis               · · [·] · ·
  LAB-anses-beneficio                        · · [·] · ·
  LAB-anses-beneficio-parafrasis             · · [·] · ·
  LAB-anses-canal-oficial                    · · · · ·
  LAB-arca-canal-oficial                     · · · · ·
  LAB-arca-deuda                             · · [·] · ·
  LAB-arca-deuda-parafrasis                  · · · · [·]
  LAB-banco-app-parafrasis                   · · · · ·
  LAB-banco-codigo                           · · · · [·] · ·
  LAB-banco-codigo-parafrasis                · · · · [·] · ·
  LAB-banco-gasto-sin-pedido                 · · ·
  LAB-banco-niega-el-codigo                  · ·
  LAB-banco-numeros-sin-clave                · · · · [·] · ·
  LAB-banco-revisa-app                       · · · · ·
  LAB-digitos-sin-palabra                    · · · · ·
  LAB-familiar-llama-vos                     · · · · ·
  LAB-familiar-peligro                       · · · [·] · ·
  LAB-familiar-peligro-parafrasis            · · · · · [·]
  LAB-giro-sin-plata                         · · · · ·
  LAB-mensajeria-no-pases-nada               · · · · ·
  LAB-no-bajes-nada                          · · · ·
  LAB-pantalla-sin-programa                  · · · · ·
  LAB-portero-codigo-puerta                  [·] ·
  LAB-whatsapp-codigo                        · · [·] · ·
  LAB-whatsapp-codigo-parafrasis             · · [·] · ·
  LG-BANK-VERIF-01-e01                       · [·] · · · · · · · · · ·
  LG-FAMILIAR-LLAMADO-01-e01                 · · · · · · [·] · · · · ·
  LG-ORG-TURNO-01-e01                        · · · [·] · · · · · · · · ·
  LG-PREMIO-CONSULTA-01-e01                  · · · · · · · · [·] · · ·
  LG-SUPPORT-INFO-01-e01                     · [·] · · · · · · · · · · ·
  LG-SUPPORT-INFO-01-e02                     · · · [·] · · · · · · · · ·
  LG-WA-CONSULTA-01-e01                      [·] · · ·
  SC-CLAVE-CAMBIO-01-e01                     · · · · · · · · [·] · · · ·
  SC-FAMILIAR-DINERO-01-e01                  · · · · · [·] · · · · · ·
  SC-ORG-BENEFICIO-01-e01                    · · · · · · [·] · · · · · ·
  SC-PREMIO-01-e01                           · · · · · · · · · · · · · ·
  SC-SOPORTE-CLAVE-01-e01                    · · [·] · · · · · · · · · · ·
  SC-SOPORTE-REMOTO-01-e01                   · · [·] · · · · · · · ·
  SC-WA-CODE-01-e01                          · · · [·] ·
  TR-01-pedido-indirecto-digitos             · · · · · · · · · · · ·
  TR-02-codigo-del-candado                   · · [·] · · · · ·
  TR-03-negacion-y-consejo                   · [·] · · · · · · · ·
  TR-04-pedido-tras-charla-larga             · · · · · [·] · · · · · · · · · · · · · · · · · · · · · · · ·
  TR-05-asado-con-transferencia              · · · · [·] · · · · · · · · · · · · · · · · · · · · · ·
  TR-06-banco-alerta-legitima                · · · · · · · · · [·] · ·
  TR-07-pedido-partido-en-dos-lineas         · · · · · · · [·] · ·
  TR-08-frase-cortada-candado                · · [·] · · · ·
  TR-09-victima-se-niega                     · · · · [·] · · · · · · ·
  TR-10-ofrecimiento-inducido                · · · [·] · · · · · · · · · ·
  TR-11-familiar-real-pide-plata             · · · [·] · · · · · ·
  TR-12-corta-antes-del-pedido               · · · · · · · · · ·
  TR-13-turno-medico-pide-dni                · · · · · · · · · · · ·
```
