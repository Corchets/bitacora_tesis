# Resumen de la corrida `2026-10-26_132916_qwen4b-comparacion`

> Material de **desarrollo** del ensayo [#50](https://github.com/Corchets/bitacora_tesis/issues/50):
> casos escritos, no grabaciones ni test final. Las posiciones son líneas, no segundos.
> El riesgo del SLM no está calibrado y no es una probabilidad. No elige modelo (D09) ni política (D08).

- **Comando:** `python correr.py --modelos qwen3.5:4b-q4_K_M --url http://127.0.0.1:11435 --casos TR-04-pedido-tras-charla-larga,TR-06-banco-alerta-legitima,TR-07-pedido-partido-en-dos-lineas,TR-08-frase-cortada-candado,SC-SOPORTE-REMOTO-01-e01,LG-SUPPORT-INFO-01-e02,SC-FAMILIAR-DINERO-01-e01,TR-11-familiar-real-pide-plata --filtro-tito --tito-real --sin-reglas --num-batch 32 --etiqueta qwen4b-comparacion --detalle`
- **Inicio / fin:** 2026-10-26T13:29:16 / 2026-10-26T13:32:39
- **Código:** `d53bbc1858` con cambios sin commit en la carpeta
- **Máquina:** Linux-7.2.5-3-omarchy-x86_64-with-glibc2.44, 16 núcleos lógicos, 30.5 GB de RAM
- **Ollama:** 0.40.8 · **Política:** aviso_unico_primer_true_valido
- **Casos:** 8 (4 vishing, 4 legítimas); 8 todavía sin revisión humana

## Resultados por configuración

| Configuración | Vishing con aviso | Antes del pedido | En el pedido | Después del pedido | En/después del cumplimiento | Falsas alarmas | Fallos | ms p50 | ms p95 | Evidencia textual | Sin evaluar |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | 4/4 | 3 | 1 | 0 | 0 | 3/4 | 0/105 | 879 | 1.421 | 7/7 | 0 |
| `tito-slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | 4/4 | 3 | 1 | 0 | 0 | 2/4 | 0/105 | 826 | 1.648 | 6/6 | 0 |

«Sin evaluar» son casos cortados o sin ninguna respuesta válida: no se cuentan en las demás columnas. «Antes del pedido» cuenta avisos previos a `T_R`; en vishing sin pedido de referencia el aviso se cuenta solo en «Vishing con aviso». «Evidencia textual» cuenta avisos cuya cita aparece en el texto disponible.

## Caso por caso

Configuraciones: **C1** `slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` · **C2** `tito-slm\|qwen3.5:4b-q4_K_M\|tarea\|ab`

`=R` aviso en la línea del pedido (`T_R`) · `<R` antes del pedido · `>R` después del pedido y antes del cumplimiento · `≥C` en o después del cumplimiento (`T_C`) · `FA` falsa alarma en una legítima · `ok` legítima sin aviso · `—` vishing sin aviso · `…` sin evaluar: la corrida se cortó antes de terminar el caso · `x` sin evaluar: ninguna respuesta válida · `(xN)` N actualizaciones fallidas en el caso.

| Caso | Clase | T_R | T_C | C1 | C2 |
|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | legítima | — | — | ok | ok |
| `SC-FAMILIAR-DINERO-01-e01` | vishing | 9 | — | =R L9 | =R L9 |
| `SC-SOPORTE-REMOTO-01-e01` | vishing | 6 | — | <R L1 | <R L3 |
| `TR-04-pedido-tras-charla-larga` | vishing | 26 | 27 | <R L3 | <R L25 |
| `TR-06-banco-alerta-legitima` | legítima | — | — | FA L3 | ok |
| `TR-07-pedido-partido-en-dos-lineas` | vishing | 7 | 9 | <R L3 | <R L3 |
| `TR-08-frase-cortada-candado` | legítima | — | — | FA L3 | FA L3 |
| `TR-11-familiar-real-pide-plata` | legítima | — | — | FA L4 | FA L4 |

## Para revisar

### Falsas alarmas

- `TR-06-banco-alerta-legitima` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 3: «Te están simulando ser del banco para pedirte datos de tu tarjeta por un consumo sospechoso» — evidencia (cita textual): «Te habla Gastón, del área de seguridad de tarjetas del banco. Te llamo por un consumo que nos llamó la atención en tu tarjeta de crédito.»
- `TR-08-frase-cortada-candado` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código de acceso a tu cuenta o servicio» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo dinero bajo una excusa falsa sobre un recibo de luz.» — evidencia (cita textual): «Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?»
- `TR-08-frase-cortada-candado` · `tito-slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 3: «Te están pidiendo un código que da acceso a tu cuenta» — evidencia (cita textual): «Pasame el código»
- `TR-11-familiar-real-pide-plata` · `tito-slm|qwen3.5:4b-q4_K_M|tarea|ab` · línea 4: «Te están pidiendo dinero bajo la excusa de un problema con tu luz.» — evidencia (cita textual): «"Me vino más alta la boleta de la luz y no llego hasta el viernes. ¿Me podrás transferir veinte mil pesos?"»

### Vishing sin aviso

Ninguno.

### Sin evaluar

Ninguno.

### Fallos por tipo

Ninguno.

## Carga y memoria informadas por Ollama

| Modelo | Carga (ms) | Memoria (MB) | En GPU (MB) |
|---|---|---|---|
| `qwen3.5:4b-q4_K_M` | 206 | 2.925 | 2.925 |

La memoria es la que informa Ollama (pesos + caché de contexto) en esta PC; no es una medición en Android.

## Filtro Tito→SLM (derivación y ahorro)

Tito real (`real-robertuito-logreg`), umbral 0.5: el primer puntaje ≥ umbral deriva al SLM en esa misma línea y lo mantiene activo; un fallo técnico de Tito también deriva, sin fabricar sospecha.
Una conversación completa nunca derivada **conserva su denominador**: vishing sin aviso cuenta como falso negativo y legítima sin aviso como verdadero negativo.

**Fallos técnicos de Tito: 105** (esas actualizaciones derivaron por fallo, sin puntaje ni sospecha; no son decisiones del filtro).
### `tito-slm|qwen3.5:4b-q4_K_M|tarea|ab`

Consultas al SLM: 105; evitadas por el filtro: 0; costo Tito+SLM: 104.401 ms (omitidas: solo Tito; consultadas: Tito+SLM).

| Caso | 1.ª derivación | Aviso | Consultas SLM | Evitadas | Fallos SLM | Costo ms |
|---|---|---|---|---|---|---|
| `LG-SUPPORT-INFO-01-e02` | 1 | sin aviso | 13 | 0 | 0 | 9.892 |
| `SC-FAMILIAR-DINERO-01-e01` | 1 | L9 | 12 | 0 | 0 | 11.666 |
| `SC-SOPORTE-REMOTO-01-e01` | 1 | L3 | 11 | 0 | 0 | 15.875 |
| `TR-04-pedido-tras-charla-larga` | 1 | L25 | 30 | 0 | 0 | 30.773 |
| `TR-06-banco-alerta-legitima` | 1 | sin aviso | 12 | 0 | 0 | 8.752 |
| `TR-07-pedido-partido-en-dos-lineas` | 1 | L3 | 10 | 0 | 0 | 11.944 |
| `TR-08-frase-cortada-candado` | 1 | L3 | 7 | 0 | 0 | 6.030 |
| `TR-11-familiar-real-pide-plata` | 1 | L4 | 10 | 0 | 0 | 9.469 |

