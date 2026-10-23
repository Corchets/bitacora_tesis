# Resumen de la corrida `2026-10-22_102514_win-9b-piloto-nb32`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:9b-q4_K_M --prompts tarea,v2 --grupo piloto_escrito --num-batch 32 --sin-reglas --timeout 300 --etiqueta win-9b-piloto-nb32 --url http://127.0.0.1:11435`
- **Inicio / fin:** 2026-10-22T10:25:14 / 2026-10-22T10:33:05
- **Código:** `886cff0633`
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 14 (7 vishing, 7 legítimas); 14 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` | 7/7 | 5 | 2 | 0 | 0 | 4/7 | 0/161 | 956 | 3.322 | 11/11 | 0 |
| `slm\|qwen3.5:9b-q4_K_M\|v2\|ab` | 7/7 | 0 | 7 | 0 | 0 | 1/7 | 0/161 | 944 | 2.083 | 8/8 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` · **C2** `slm\|qwen3.5:9b-q4_K_M\|v2\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
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

## Para revisar

### Falsas alarmas

- `LG-BANK-VERIF-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 6: «Te están pidiendo que digas los últimos números de tu tarjeta para identificarte, lo cual es un dato sensible que no debés compartir por teléfono.» — evidencia (cita textual): «¿Querés que te diga los últimos números de la tarjeta para que me identifiques?»
- `LG-FAMILIAR-LLAMADO-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 7: «Te están pidiendo que transfieras dinero bajo una emergencia falsa; nunca des datos bancarios ni hagas transferencias por teléfono.» — evidencia (cita textual): «A: ¿Necesitan plata para algo? ¿Te transfiero para los remedios o para el taxi?»
- `LG-ORG-TURNO-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 6: «Te están intentando convencer para que les des tus datos personales (DNI) y claves bancarias bajo la excusa de verificar si estás en un listado.» — evidencia (cita textual): «B: ¿Y vos no necesitás mis datos para fijarte si estoy en el listado?»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 4: «Te están intentando convencer para que les digas tu usuario y contraseña, datos que nunca debés compartir con nadie.» — evidencia (cita textual): «B: Ah, yo te los iba a pasar para que te fijes vos si están bien.»
- `LG-SUPPORT-INFO-01-e01` · `slm|qwen3.5:9b-q4_K_M|v2|ab` · línea 4: «Te están pidiendo que le des tus claves o usuario para que verifiquen tu cuenta.» — evidencia (cita textual): «Ah, yo te los iba a pasar para que te fijes vos si están bien.»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:9b-q4_K_M` | 36.143 | 5.247 | 5.247 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.
