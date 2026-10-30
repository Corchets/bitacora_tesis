# Resumen de la corrida `2026-10-26_135640_qwen08b-comparacion`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:0.8b --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen08b-comparacion`
- **Inicio / fin:** 2026-10-26T13:56:40 / 2026-10-26T13:57:45
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:0.8b\|tarea\|ab` | 4/4 | 2 | 1 | 0 | 1 | 2/4 | 0/105 | 172 | 540 | 3/6 | 0 |
| `tito-slm\|qwen3.5:0.8b\|tarea\|ab` | 4/4 | 3 | 1 | 0 | 0 | 2/4 | 0/105 | 468 | 712 | 2/6 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:0.8b\|tarea\|ab` · **C2** `tito-slm\|qwen3.5:0.8b\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | <R L8 | =R L9 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 | <R L4 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L20 | <R L6 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok | FA L3 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | ≥C L9 | <R L5 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L4 | ok |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L9 | FA L9 |

## Para revisar

### Falsas alarmas

- `TR-08-frase-cortada-candado` · `slm|qwen3.5:0.8b|tarea|ab` · línea 4: «Te están solicitando un código de acceso a una valija que me prestaste en el hotel para cerrarla sin pensar; esto es una acción directa de robo.» — evidencia (cita textual): «A: Pasame el código del candado de la valija que me prestaste. La cerré sin pensar y ahora, en el hotel, no la puedo abrir.»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando un código de verificación o activación para acceder a tu cuenta bancaria (cuenta de siempre) y pedirte transferir dinero.» — evidencia (cita NO textual): «B: ¿Me podrás transferir veinte mil pesos? A: Sí, mi amor. ¿A qué cuenta? B: A la mía de siempre, la que tenés agendada. No hay apuro, eh: hoy o mañana, cuando puedas. El viernes cobro y te los devuelvo.»
- `TR-06-banco-alerta-legitima` · `tito-slm|qwen3.5:0.8b|tarea|ab` · línea 3: «El mensaje indica que Gastón es del área de seguridad de tarjetas y te llama por un consumo en tu tarjeta de crédito. Esto sugiere una posible estafa para robar datos personales o dinero.» — evidencia (cita textual): «A: Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-11-familiar-real-pide-plata` · `tito-slm|qwen3.5:0.8b|tarea|ab` · línea 9: «Te están solicitando un código de verificación o activación que permitiría acceder a tu cuenta bancaria sin verificar la identidad del interlocutor.» — evidencia (cita NO textual): «B: ¿A qué cuenta? A: A la mía de siempre, la que tenés agendada. No hay apuro, eh: hoy o mañana, cuando puedas. El viernes cobro y te los devuelvo.»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:0.8b` | 2.471 | 512 | 512 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|qwen3.5:0.8b|tarea|ab`

Consultas al SLM: 70; evitadas por el filtro: 35; costo Tito+SLM: 38.419 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 1.726 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 4 | 8 | 0 | 2.962 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L4 | 11 | 0 | 0 | 5.698 |
| `TR-04-pedido-tras-charla-larga` | 5 | L6 | 26 | 4 | 0 | 17.012 |
| `TR-06-banco-alerta-legitima` | 3 | L3 | 10 | 2 | 0 | 5.301 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L5 | 6 | 4 | 0 | 3.341 |
| `TR-08-frase-cortada-candado` | 3 | sin aviso | 5 | 2 | 0 | 1.092 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 2 | 8 | 0 | 1.288 |

