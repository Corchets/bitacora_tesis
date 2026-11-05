# Resumen de la corrida `2026-10-26_141023_llama1b-comparacion`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos llama3.2:1b-instruct-q4_K_M --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta llama1b-comparacion`
- **Inicio / fin:** 2026-10-26T14:10:23 / 2026-10-26T14:11:37
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|llama3.2:1b-instruct-q4_K_M\|tarea\|ab` | 0/4 | 0 | 0 | 0 | 0 | 0/4 | 5/105 | 294 | 394 | 0/0 | 0 |
| `tito-slm\|llama3.2:1b-instruct-q4_K_M\|tarea\|ab` | 2/4 | 2 | 0 | 0 | 0 | 3/4 | 0/105 | 382 | 609 | 1/5 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|llama3.2:1b-instruct-q4_K_M\|tarea\|ab` · **C2** `tito-slm\|llama3.2:1b-instruct-q4_K_M\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | FA L9 |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | — | — |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | — | — |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | — (x4) | <R L10 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | ok | FA L5 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | — | <R L5 |
| `TR-08-frase-cortada-candado` | legítima | — | — | ok | ok |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | ok (x1) | FA L9 |

## Para revisar

### Falsas alarmas

- `TR-06-banco-alerta-legitima` · `tito-slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · línea 5: «Te están pidiendo un código que da acceso a tu cuenta» — evidencia (cita textual): «¿Qué consumo? Una compra de sesenta y dos mil pesos en una tienda en línea, hoy a las once y cuarto.»
- `LG-SUPPORT-INFO-01-e02` · `tito-slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · línea 9: «La llamada sigue después de la línea 8, donde se solicita la clave y se menciona la pantalla de la aplicación del banco. Podría ser una estafa para obtener la clave y acceder a la cuenta del destinatario.» — evidencia (cita NO textual): «La línea 8 de la transcripción es la que menciona la clave y la pantalla de la aplicación del banco, lo que sugiere una estafa.»
- `TR-11-familiar-real-pide-plata` · `tito-slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · línea 9: «La sospecha preliminar no confirma una estafa.» — evidencia (cita NO textual): «La línea 9: "Dale, te corto y te llamo"»

### Vishing sin aviso

- `TR-04-pedido-tras-charla-larga` · `slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `TR-07-pedido-partido-en-dos-lineas` · `slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `SC-SOPORTE-REMOTO-01-e01` · `slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `SC-FAMILIAR-DINERO-01-e01` · `slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · riesgo máximo 0.50
- `SC-SOPORTE-REMOTO-01-e01` · `tito-slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · riesgo máximo 0.56
- `SC-FAMILIAR-DINERO-01-e01` · `tito-slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · riesgo máximo 0.58

### Sin evaluar

Ninguno.

### Fallos por tipo

- `slm|llama3.2:1b-instruct-q4_K_M|tarea|ab` · salida_cortada: 5

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `llama3.2:1b-instruct-q4_K_M` | 1.235 | 895 | 895 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|llama3.2:1b-instruct-q4_K_M|tarea|ab`

Consultas al SLM: 70; evitadas por el filtro: 35; costo Tito+SLM: 33.464 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | 8 | L9 | 6 | 7 | 0 | 3.690 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | sin aviso | 4 | 8 | 0 | 2.128 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | sin aviso | 11 | 0 | 0 | 4.141 |
| `TR-04-pedido-tras-charla-larga` | 5 | L10 | 26 | 4 | 0 | 14.643 |
| `TR-06-banco-alerta-legitima` | 3 | L5 | 10 | 2 | 0 | 4.065 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L5 | 6 | 4 | 0 | 2.500 |
| `TR-08-frase-cortada-candado` | 3 | sin aviso | 5 | 2 | 0 | 1.512 |
| `TR-11-familiar-real-pide-plata` | 9 | L9 | 2 | 8 | 0 | 785 |

