# Resumen de la corrida `2026-10-14_191429_cpu-2hilos`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:0.8b,qwen3.5:2b --grupo piloto_escrito --solo-cpu --hilos 2 --etiqueta cpu-2hilos`
- **Inicio / fin:** 2026-10-14T19:14:29 / 2026-10-14T19:48:42
- **Código:** `63e916a56b`
- **Máquina:** Windows-11-10.0.26300-SP0, 12 núcleos lógicos, 31.9 GB de RAM
- **Ollama:** 0.40.4 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 14 (7 vishing, 7 legítimas); 14 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `reglas` | 6/7 | 3 | 3 | 0 | 0 | 7/7 | 0/161 | 11 | 22 | 13/13 | 0 |
| `slm\|qwen3.5:0.8b\|tarea\|ab` | 7/7 | 3 | 3 | 0 | 1 | 2/7 | 0/161 | 3.913 | 7.331 | 6/9 | 0 |
| `slm\|qwen3.5:2b\|tarea\|ab` | 6/7 | 0 | 6 | 0 | 0 | 0/7 | 0/161 | 8.216 | 12.956 | 6/6 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `reglas` · **C2** `slm\|qwen3.5:0.8b\|tarea\|ab` · **C3** `slm\|qwen3.5:2b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 | C3 |
|---|---|---|---|---|---|---|
| `LG-BANK-VERIF-01-e01` | legítima | — | — | FA L2 | ok | ok |
| `LG-FAMILIAR-LLAMADO-01-e01` | legítima | — | — | FA L7 | ok | ok |
| `LG-ORG-TURNO-01-e01` | legítima | — | — | FA L4 | FA L9 | ok |
| `LG-PREMIO-CONSULTA-01-e01` | legítima | — | — | FA L9 | ok | ok |
| `LG-SUPPORT-INFO-01-e01` | legítima | — | — | FA L2 | FA L9 | ok |
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | FA L4 | ok | ok |
| `LG-WA-CONSULTA-01-e01` | legítima | — | — | FA L1 | ok | ok |
| `SC-CLAVE-CAMBIO-01-e01` | vishing | 9 | 12 | =R L9 | <R L7 | =R L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L6 | <R L8 | =R L9 |
| `SC-ORG-BENEFICIO-01-e01` | vishing | 7 | 8 | =R L7 | ≥C L9 | — |
| `SC-PREMIO-01-e01` | vishing | 8 | 13 | — | <R L6 | =R L8 |
| `SC-SOPORTE-CLAVE-01-e01` | vishing | 6 | 11 | <R L3 | =R L6 | =R L6 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | =R L6 | =R L6 |
| `SC-WA-CODE-01-e01` | vishing | 4 | 5 | =R L4 | =R L4 | =R L4 |

## Para revisar

### Falsas alarmas

- `LG-BANK-VERIF-01-e01` · `reglas` · línea 2: «REQUEST_SECRET (patrón: clave)» — evidencia (cita textual): «Hola, Lucía. Llamo al número que está atrás de mi tarjeta. Me llegó un aviso en la app de un ingreso desde un dispositivo nuevo y quiero cambiar la clave.»
- `LG-FAMILIAR-LLAMADO-01-e01` · `reglas` · línea 7: «REQUEST_TRANSFER (patrón: plata)» — evidencia (cita textual): «¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-ORG-TURNO-01-e01` · `reglas` · línea 4: «REQUEST_PERSONAL_DATA (patrón: domicilio)» — evidencia (cita textual): «¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo.»
- `LG-PREMIO-CONSULTA-01-e01` · `reglas` · línea 9: «REQUEST_TRANSFER (patrón: paga)» — evidencia (cita textual): «A ver... sí, acá lo dice. ¿Y hay que pagar algo para retirarlo? ¿Un gasto de envío, algo así?»
- `LG-SUPPORT-INFO-01-e01` · `reglas` · línea 2: «REQUEST_SECRET (patrón: contrasena)» — evidencia (cita textual): «Hola, ¿qué tal? Los llamo porque no puedo entrar a mi cuenta desde la computadora: me dice que el usuario o la contraseña son incorrectos.»
- `LG-SUPPORT-INFO-01-e02` · `reglas` · línea 4: «REQUEST_REMOTE_ACCESS (patrón: instala)» — evidencia (cita textual): «No, eso no. Nosotros no te vamos a pedir que compartas la pantalla ni que instales nada para que alguien entre a tu celular.»
- `LG-WA-CONSULTA-01-e01` · `reglas` · línea 1: «REQUEST_AUTH_CODE (patrón: codigo)» — evidencia (cita textual): «Me llegó por SMS un código para activar WhatsApp y yo no lo pedí.»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando datos personales (DNI) y una foto de un documento para verificar tu identidad en una oficina, además de pedir transferencias de dinero.» — evidencia (cita NO textual): «B: ¿Seguro? Porque a una vecina la llamaron diciendo que eran de acá, y le pidieron el domicilio y una foto con el documento en la mano para cargárselo. A: Eso no lo hacemos nosotros. Por teléfono no pedimos fotos del documento, claves ni datos del banco.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando explícitamente una clave nueva para ingresar a tu cuenta y mencionan que nadie de la mesa te la pedirá. Esto es un patrón clásico de estafas (vishing) diseñado para inducir al usuario a revelar información sensible.» — evidencia (cita textual): «A: En la pantalla de ingreso tocá «Olvidé mi contraseña». Te va a llegar un correo a la dirección que tenés registrada.
B: Ya me llegó. ¿Te leo lo que dice?»

### Vishing sin aviso

- `SC-PREMIO-01-e01` · `reglas` · sin riesgo registrado
- `SC-ORG-BENEFICIO-01-e01` · `slm|qwen3.5:2b|tarea|ab` · riesgo máximo 0.85

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:0.8b` | 7.625 | 547 | — |
| `qwen3.5:2b` | 10.055 | 2.260 | — |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
