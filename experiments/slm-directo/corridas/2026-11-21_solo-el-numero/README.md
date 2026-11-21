# solo-el-numero — 2026-11-21

Prueba rápida del punto 2 de [#172](https://github.com/Corchets/bitacora_tesis/issues/172) con la configuración final
([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)).

## Qué cuenta como «anda bien» (escrito antes de correr la comparación)

> **Estado: propuesta sin discutir.** La decisión de adoptar el cambio es de Mateo.

Con el mismo servidor y el mismo runtime para las dos variantes:

1. Todas las consultas válidas en las dos.
2. Cada conversación avisa o no avisa igual, y el primer aviso cae en la misma línea, en todas.
3. Las líneas en que cambia el riesgo sin mover el punto 2 se informan aparte, separando las que cruzan 0,3 de las
   que no. Como piso de comparación va la misma configuración de hoy corrida dos veces en el mismo servidor.

## Resultado en una línea

En la Mac, generar solo el número baja la línea de 0,34 a 0,20 s (generar: de 14 tokens a 6) y **cumple el criterio**:
las 150 conversaciones de desarrollo avisan igual y en la misma línea. El riesgo no es idéntico: cambia en 11 a 20 de
1.392 líneas, lo mismo que cambia la configuración de hoy cuando se corre dos veces (11 de 1.392). **En el iPhone
15 Pro Max la línea baja de 0,93–0,98 a 0,54 s** (generar: de 0,65–0,69 a 0,28 s), con el mismo aviso en las seis
conversaciones.

## Qué se probó

- **Hoy (`chat`):** `/v1/chat/completions` con la gramática del JSON entero y 14 tokens. El modelo escribe
  `{\n  "riesgo": 0.3,\n  `.
- **Solo el número (`numero`):** el mismo prompt armado con `/apply-template`, más `{\n  "riesgo":` escrito por
  nosotros en el turno del modelo, a `/completion`, con una gramática que solo deja `espacio número ","`. El modelo
  genera 6 tokens: el espacio, el número (`0`, `.`, `3`), la coma y el fin. Con dos decimales (`0.05`) son 7.
- Es el modo `--consulta numero --prefijo salto` que
  [`correr_android_latencia.py`](../../correr_android_latencia.py) ya tenía desde la
  [corrida del A56](../2026-11-11_a56-latencia-172/README.md) con `c-premisa` (ahí: 8/83 líneas distintas, −0,9 s).
  Acá va con la configuración final (`c-consejos-corte-riesgo`,
  [ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)); el resto no cambia: aviso con
  riesgo ≥ 0,3, motivo solo en el primer aviso, solo OTRA, `--hablantes rol`, contexto 4096, temperatura 0, seed 42.
- **Runtime, el mismo para las dos:** `llama-server` de llama.cpp `6c01da62` para macOS con Metal (`-ngl 99`), Mac M4,
  GGUF `6dd7ac24…5937d`. Un solo servidor para cada serie, sin reiniciarlo entre corridas.

## 1. Si se puede: sí, por `/completion`

Sale de [`probar_prefijo.py`](probar_prefijo.py) → [`prefijo.json`](prefijo.json), sobre las 15 consultas de
CV2-D-V-BANCO-002:

- **Los tokens son los mismos.** `/tokenize` parte `{\n  "riesgo":` en 7 tokens (`{`, `\n`, dos espacios, `"`, `ries`,
  `go`, `":`), y son los 7 primeros que hoy genera el modelo, en las 15 consultas. Los 5 que siguen (espacio, número,
  coma) también coinciden.
- **La caché del prefijo sigue sirviendo.** Repetida la misma consulta, hoy da `cache_n` 749 y `prompt_n` 1; solo el
  número, `cache_n` 756 y `prompt_n` 1 (los 7 del prefijo entran en la caché). En las corridas, la mediana de tokens
  reusados es la misma en las dos variantes (968 en las seis conversaciones), y los tokens nuevos por consulta pasan
  de 63 a 70: los 7 del prefijo se procesan con el texto nuevo en vez de generarse.
- **El mensaje `assistant` final no sirve.** `/v1/chat/completions` acepta un último mensaje del asistente y lo
  continúa, pero la plantilla de Gemma le antepone `<|channel>thought\n<channel|>`: es otro prompt, y el riesgo cambió
  en 4 de las 15 consultas.

## 2. Si el riesgo es el mismo: no idéntico, pero dentro de lo que varía hoy

Tres corridas seguidas en el mismo servidor: hoy, solo el número y hoy otra vez (`serie.sh`). Todo contra la primera.

| Conjunto | Corrida | Válidas | Riesgo distinto | …que cruza 0,3 | Conversaciones que avisan | Primer aviso en otra línea |
|---|---|---:|---:|---:|---:|---:|
| 6 conversaciones | `s6-hoy-1` | 83/83 | — | — | 5/6 | — |
| | `s6-numero` | 83/83 | 2/83 | 0 | 5/6 | 0/6 |
| | `s6-hoy-2` | 83/83 | 0/83 | 0 | 5/6 | 0/6 |
| `desarrollo-150` | `d150-hoy-1` | 1392/1392 | — | — | 91/150 | — |
| | `d150-numero` | 1392/1392 | 20/1392 | 2 | 91/150 | 0/150 |
| | `d150-hoy-2` | 1392/1392 | 11/1392 | 1 | 91/150 | 0/150 |

- **Criterio: cumplido.** Todas válidas; las 150 conversaciones avisan o no avisan igual, y el primer aviso cae en la
  misma línea.
- **El riesgo cambia en 20 de 1.392 líneas (1,4 %)** contra `d150-hoy-1` y en 11 contra `d150-hoy-2`, siempre por 0,2 o menos. Las dos que cruzan 0,3 están después del primer aviso de su conversación, por eso no lo
  mueven: CV2-D-L-BANCO-006 línea 8 (0,3 → 0,2) y CV2-D-V-WHATSAPP-004 línea 15
  (0,2 → 0,3).
- **La configuración de hoy tampoco se repite del todo.** `d150-hoy-2` difiere de `d150-hoy-1` en 11 líneas, todas en
  las primeras 44 conversaciones de la lista; en las 106 restantes y en las seis de `s6` las dos corridas de hoy son
  idénticas. En esas 11 líneas, `d150-numero` da lo mismo que `d150-hoy-2`. No se averiguó la causa.
- **En 3 de 1.392 consultas el prefijo no es el que el modelo escribe hoy.** Son primeras líneas de conversaciones
  que abre OTRA (CV2-D-L-BANCO-002, CV2-D-V-BANCO-003 y TR-08-frase-cortada-candado): ahí hoy sale el JSON compacto
  (`{"riesgo": 0.1, "alerta_s`) y con el cambio le imponemos el del salto. El riesgo dio lo mismo en las tres.
- Las líneas, una por una, están en [`resumen-s6.json`](resumen-s6.json) y [`resumen-d150.json`](resumen-d150.json).

## 3. Cuánto baja la latencia

### En la Mac

Segundos. «Por línea» es la actualización de una línea de OTRA sin motivo; procesar y generar, lo que informa el
servidor.

| Conjunto | Corrida | Por línea: mediana / p95 / máx. | Procesar: mediana / p95 | Generar: mediana / p95 (tokens) | Primer aviso sin esperar el motivo: mediana / máx. |
|---|---|---:|---:|---:|---:|
| 6 conversaciones (n=78) | `s6-hoy-1` | 0,34 / 0,35 / 0,36 | 0,08 / 0,10 | 0,25 / 0,25 (14) | 0,33 / 0,35 |
| | `s6-numero` | 0,20 / 0,20 / 0,20 | 0,08 / 0,08 | 0,11 / 0,12 (6) | 0,19 / 0,20 |
| | `s6-hoy-2` | 0,34 / 0,36 / 0,36 | 0,08 / 0,10 | 0,25 / 0,26 (14) | 0,33 / 0,36 |
| `desarrollo-150` (n=1301) | `d150-hoy-1` | 0,43 / 0,53 / 0,67 | 0,11 / 0,15 | 0,32 / 0,38 (14) | 0,44 / 0,61 |
| | `d150-numero` | 0,26 / 0,35 / 0,55 | 0,11 / 0,15 | 0,15 / 0,20 (6) | 0,27 / 0,36 |
| | `d150-hoy-2` | 0,52 / 0,61 / 0,93 | 0,14 / 0,18 | 0,37 / 0,43 (14) | 0,50 / 0,64 |

- **Baja unos 0,14 s por línea en la Mac (41 %), todo en generar:** de 0,25 a 0,11 s. Procesar no cambia, aunque
  entran 7 tokens más.
- Las corridas de `desarrollo-150` son más lentas y más dispersas que las de `s6` (0,43 y 0,52 s para la misma
  configuración): la Mac tenía otros procesos durante esos 36 minutos. Para tiempos, la comparación limpia es `s6`.
- El motivo del primer aviso no cambia: es la misma segunda consulta.

### En el iPhone 15 Pro Max

Las seis conversaciones, por Wi-Fi, con [`medir_iphone.py`](medir_iphone.py): la app de siempre (`llama-server`
`6c01da62` con Metal, `-ngl 99`), relanzada en cada pasada. Cuatro pasadas seguidas entre las 16:16 y las 16:24 del
2026-11-21, en este orden. Teléfono desenchufado, batería 50–45 %, sin modo de bajo consumo; ida y vuelta de
`/health`, 17 ms de mediana.

| Corrida | Estado térmico | Por línea: mediana / p95 / máx. | Procesar: mediana / p95 | Generar: mediana / p95 (tokens) | Primer aviso sin esperar el motivo: mediana / máx. | Riesgo distinto | Primer aviso en otra línea |
|---|---|---:|---:|---:|---:|---:|---:|
| `iphone-hoy-1` | `nominal` → `serious` | 0,74 / 1,05 / 1,17 | 0,18 / 0,27 | 0,52 / 0,68 (14) | 0,73 / 0,77 | — | — |
| `iphone-hoy-2` | `serious` | 0,93 / 1,02 / 1,07 | 0,24 / 0,29 | 0,65 / 0,69 (14) | 0,91 / 1,00 | 0/83 | 0/6 |
| `iphone-numero` | `serious` | 0,54 / 0,64 / 0,72 | 0,22 / 0,25 | 0,28 / 0,31 (6) | 0,51 / 0,55 | 1/83 | 0/6 |
| `iphone-hoy-3` | `serious` | 0,98 / 1,10 / 1,27 | 0,25 / 0,30 | 0,69 / 0,75 (14) | 0,99 / 1,03 | 0/83 | 0/6 |

- **Con el teléfono en el mismo estado térmico, la línea baja de 0,93–0,98 a 0,54 s** (unos 0,4 s, 43 %), y el p95 de
  1,02–1,10 a 0,64 s. `iphone-numero` corrió entre `iphone-hoy-2` e `iphone-hoy-3`, las tres enteras en `serious`.
- `iphone-hoy-1` arrancó con el teléfono frío y por eso es más rápida (0,74 s); no hay pasada del número en frío.
- **Riesgo:** una línea distinta de 83 (CV2-D-L-BANCO-001 línea 22, 0,5 → 0,6, la misma que en la Mac), sin cruzar 0,3;
  mismo aviso y misma línea en las seis. Las tres pasadas de hoy dan el mismo riesgo en las 83 líneas.
- Las 83 consultas válidas en las cuatro. Pico de `footprint`: 0,53 a 0,58 GiB, igual con y sin el cambio.
- La primera vez, `iphone-numero` no arrancó: `devicectl` no pudo relanzar la app (error 10004). Se repitió y por eso
  hay una tercera pasada de hoy. En `medir.json` y en los registros no queda la IP del teléfono.

Repetir, con el teléfono desbloqueado, la app en pantalla y en la misma Wi-Fi que la Mac:

```sh
python3 medir_iphone.py iphone-hoy-2 --consulta chat --ip IP --dispositivo UDID --bundle ID.DE.LA.APP
python3 medir_iphone.py iphone-numero --consulta numero --ip IP --dispositivo UDID --bundle ID.DE.LA.APP
python3 medir_iphone.py iphone-hoy-3 --consulta chat --ip IP --dispositivo UDID --bundle ID.DE.LA.APP
python3 -I resumir.py --base iphone-hoy-1 iphone-hoy-2 iphone-numero iphone-hoy-3 --salida resumen-iphone.json
```

## 4. Qué habría que tocar para adoptarlo (no se tocó nada)

- **Con `llama-server` (teléfono):** el cliente ya existe, `Cliente` con `consulta="numero"` en
  `correr_android_latencia.py`. Habría que hacerlo el valor por defecto ahí y en lo que mida de acá en adelante.
- **`detectores.py`:** `DetectorSLMCorteRiesgo` no necesita cambios para leer la respuesta (el cliente le devuelve el
  prefijo más lo generado, y `leer_riesgo_cortado` lee igual). El prefijo fijo `{\n  "riesgo":` depende del prompt:
  con `c-consejos` el modelo lo escribió así en 1.389 de las 1.392 consultas de `desarrollo-150`, pero otro prompt
  puede escribir más seguido el JSON compacto ([nota del 2026-11-11](../2026-11-11_a56-latencia-172/README.md)).
- **Con Ollama (la demo `experiments/voip/servidor.py`, `correr.py` y la evaluación final):** hoy usan
  `ClienteOllama.chat` contra `/api/chat` con `format`. **No se probó si Ollama permite el prellenado con la misma
  plantilla y una gramática solo para el número** (acá no hay Ollama). Habría que probarlo antes; si no se puede, la
  demo queda como está y el cambio es solo del teléfono.
- **La evaluación final no se repite por esto,** pero corrió con la salida de 14 tokens en Ollama: adoptar el cambio
  en el teléfono agrega otra diferencia entre lo evaluado y lo que corre en el dispositivo, del mismo tipo que
  [H11](../../../../docs/hallazgos/H11-el-riesgo-cambia-con-el-runtime.md) y
  [H13](../../../../docs/hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md).
- **Documentos:** un ADR corto que cambie la fila «salida cortada tras el riesgo, 14 tokens» del
  [ADR 0006](../../../../docs/ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md),
  `prompts/README.md`, la tabla de latencia de las corridas del iPhone y el punto 2 de #172.

## Recomendación

> **Estado: propuesta sin discutir.** Adoptarlo en el teléfono: baja la línea unos 0,4 s en el iPhone, cumple el
> criterio en 150 conversaciones y no mueve más el riesgo que repetir la corrida de hoy. Dejar la demo con Ollama como
> está hasta probar si Ollama lo permite. Toca D09 en
> [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

## Límites

- **En el iPhone, una pasada del número y seis conversaciones,** con el teléfono caliente (`serious`). Las 150 solo
  corrieron en la Mac.
- Una serie por conjunto (hoy, número, hoy), en un solo runtime: `llama-server` con Metal en macOS. En CPU o en
  Ollama puede dar otra cosa (en el A56, con `c-premisa`, cambió 8 de 83 líneas).
- 150 conversaciones de desarrollo (`desarrollo-150`: 1.392 consultas), que incluyen las seis de `s6`. Nada de la
  reserva de test ni de los conjuntos reales.
- Mide si el aviso es el mismo, no si es correcto: no se comparó contra la referencia.
- No se explicó por qué cambian las líneas que cambian, ni por qué la configuración de hoy no se repite en las
  primeras 44 conversaciones. Lo probable, sin comprobar, es que el estado de la caché cambie cómo se agrupan los
  tokens al procesarlos y eso mueva los decimales.
- El recorrido sigue después del primer aviso (modo diagnóstico), como en las corridas anteriores.

## Archivos

- [`probar_prefijo.py`](probar_prefijo.py) y [`prefijo.json`](prefijo.json): el paso 1.
- [`serie.sh`](serie.sh): las tres corridas de cada conjunto. [`armar.py`](armar.py) arma
  [`conversaciones-desarrollo-150.json`](conversaciones-desarrollo-150.json).
- `s6-*/` y `d150-*/`: `turnos.jsonl`, `manifiesto.json` y `ejecucion.log` de cada corrida.
- [`resumir.py`](resumir.py) → [`resumen-s6.json`](resumen-s6.json) y [`resumen-d150.json`](resumen-d150.json).
- [`medir_iphone.py`](medir_iphone.py) → `iphone-*/` (además `medir.json`, `recursos.log` y `runtime.log`) y
  [`resumen-iphone.json`](resumen-iphone.json).

## Repetir

Con el `llama-server` de `6c01da62` para macOS (opciones de build en el
[README del 2026-11-20](../2026-11-20_iphone-15-pro-max-latencia/README.md)) levantado en el puerto 18080:

```sh
python3 -I probar_prefijo.py > prefijo.json
python3 armar.py
sh serie.sh s6 && sh serie.sh d150
python3 -I resumir.py --base s6-hoy-1 s6-numero s6-hoy-2 --salida resumen-s6.json
python3 -I resumir.py --base d150-hoy-1 d150-numero d150-hoy-2 --salida resumen-d150.json
```
