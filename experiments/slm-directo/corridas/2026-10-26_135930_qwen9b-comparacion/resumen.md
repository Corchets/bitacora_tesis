# Resumen de la corrida `2026-10-26_135930_qwen9b-comparacion`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:9b-q4_K_M --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen9b-comparacion`
- **Inicio / fin:** 2026-10-26T13:59:30 / 2026-10-26T14:04:40
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` | 4/4 | 3 | 1 | 0 | 0 | 3/4 | 0/105 | 947 | 2.600 | 7/7 | 0 |
| `tito-slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` | 4/4 | 3 | 1 | 0 | 0 | 2/4 | 0/105 | 1.231 | 3.456 | 6/6 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` · **C2** `tito-slm\|qwen3.5:9b-q4_K_M\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L3 | <R L3 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L23 | <R L23 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L10 | FA L9 |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L4 | <R L5 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | ok |

## Para revisar

### Falsas alarmas

- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 10: «El estafador intenta recuperar tu confianza tras advertirte para luego pedirte un código de verificación que él mismo dice haber recibido, lo cual es una táctica clásica para obtener tus datos.» — evidencia (cita textual): «10. B: Hace un rato me llegó un mensaje con un código. ¿Te lo paso así lo verificás?»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código de verificación o acceso a tu cuenta sin haber establecido una identidad confiable.» — evidencia (cita textual): «3. A: Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo que hagas una transferencia de dinero directamente por teléfono.» — evidencia (cita textual): «B: Nada grave. Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-06-banco-alerta-legitima` · `tito-slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 9: «Te están indicando una acción específica (entrar a la app y tocar Pausar) para frenar el consumo sin verificar tu identidad primero, lo cual es una táctica común para presionarte a actuar bajo estrés antes de que te den más datos o intenten robarlos después.» — evidencia (cita textual): «A: Antes que nada: no te voy a pedir ningún código, ni la clave, ni los números de la tarjeta. Si en algún momento alguien te los pide, cortá.
B: Bueno. ¿Y entonces cómo la freno?
A: Entrá a la aplicación del banco, en Tarjetas, y tocá Pausar. Eso la frena al instante.»
- `TR-08-frase-cortada-candado` · `tito-slm|qwen3.5:9b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo directamente un código de verificación o acceso a tu cuenta bancaria.» — evidencia (cita textual): «3. A: Pasame el código»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:9b-q4_K_M` | 15.151 | 5.247 | 5.247 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

### `tito-slm|qwen3.5:9b-q4_K_M|tarea|ab`

Consultas al SLM: 70; evitadas por el filtro: 35; costo Tito+SLM: 141.504 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | 8 | sin aviso | 6 | 7 | 0 | 7.716 |
| `SC-FAMILIAR-DINERO-01-e01` | 9 | L9 | 4 | 8 | 0 | 9.319 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 11 | 0 | 0 | 27.408 |
| `TR-04-pedido-tras-charla-larga` | 5 | L23 | 26 | 4 | 0 | 58.786 |
| `TR-06-banco-alerta-legitima` | 3 | L9 | 10 | 2 | 0 | 16.112 |
| `TR-07-pedido-partido-en-dos-lineas` | 5 | L5 | 6 | 4 | 0 | 13.131 |
| `TR-08-frase-cortada-candado` | 3 | L3 | 5 | 2 | 0 | 6.173 |
| `TR-11-familiar-real-pide-plata` | 9 | sin aviso | 2 | 8 | 0 | 2.858 |

