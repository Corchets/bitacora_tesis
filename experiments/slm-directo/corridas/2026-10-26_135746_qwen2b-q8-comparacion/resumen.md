# Resumen de la corrida `2026-10-26_135746_qwen2b-q8-comparacion`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:2b-q8_0 --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen2b-q8-comparacion`
- **Inicio / fin:** 2026-10-26T13:57:46 / 2026-10-26T13:59:30
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:2b-q8_0\|tarea\|ab` | 4/4 | 0 | 3 | 1 | 0 | 0/4 | 0/105 | 410 | 1.008 | 4/4 | 0 |
| `tito-slm\|qwen3.5:2b-q8_0\|tarea\|ab` | 4/4 | 0 | 3 | 1 | 0 | 1/4 | 0/105 | 504 | 1.068 | 5/5 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:2b-q8_0\|tarea\|ab` · **C2** `tito-slm\|qwen3.5:2b-q8_0\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | FA L12 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | =R L6 | =R L6 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | =R L26 | =R L26 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | >R L8 | >R L8 |
| `TR-08-frase-cortada-candado` | legítima | — | — | ok | ok |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok | ok |

## Para revisar

### Falsas alarmas

- `LG-SUPPORT-INFO-01-e02` · `tito-slm|qwen3.5:2b-q8_0|tarea|ab` · línea 12: «Te están pidiendo que compartas la pantalla para ver una actualización del banco» — evidencia (cita textual): «"Bien. Cuando termine, abrila y contame qué te aparece en la pantalla. Todavía no pongas la clave."»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:2b-q8_0` | 1.820 | 2.204 | 2.204 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|qwen3.5:2b-q8_0|tarea|ab`

Consultas al SLM: 70; evitadas por el filtro: 35; costo Tito+SLM: 46.954 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | 8 | L12 | 6 | 7 | 0 | 4.374 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 4 | 8 | 0 | 3.948 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L6 | 11 | 0 | 0 | 6.922 |
| `TR-04-pedido-tras-charla-larga` | 5 | L26 | 26 | 4 | 0 | 19.159 |
| `TR-06-banco-alerta-legitima` | 3 | sin aviso | 10 | 2 | 0 | 5.088 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L8 | 6 | 4 | 0 | 3.928 |
| `TR-08-frase-cortada-candado` | 3 | sin aviso | 5 | 2 | 0 | 2.354 |
| `TR-11-familiar-real-pide-plata` | 9 | sin aviso | 2 | 8 | 0 | 1.180 |

