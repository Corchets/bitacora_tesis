# ¿Ollama reutiliza la transcripción ya procesada? Qwen 3.5 en Apple M1

> **Estado: propuesta sin discutir.** Medición de desarrollo del ensayo
> [#50](https://github.com/Corchets/bitacora_tesis/issues/50) en una MacBook Pro M1
> (8 GB) con Ollama 0.40.5 y `qwen3.5:0.8b-q8_0`. No elige modelo (D09).

## Pregunta

`detectores.py` arma el mensaje para que el comienzo sea igual entre una línea y la
siguiente: el número de línea va solo al final. Si Ollama reutilizara lo ya procesado,
cada actualización solo tendría que leer la línea nueva. En las corridas, `tokens_prompt`
crece de 474 a 1222 en `TR-04` mientras el tiempo sube poco, pero ese número no dice
cuánto se reutilizó: Ollama informa siempre el largo total del prompt.

## Método

`medir_cache.py` toma `TR-04-pedido-tras-charla-larga` y, en las líneas 5, 10, 15, 20 y
25, mide `prompt_eval_duration` con el prompt `tarea`, hablantes `ab` y las opciones de
`correr.py`, en tres situaciones:

- **secuencial:** justo después de evaluar la línea anterior, como en una corrida;
- **repetido:** el mismo pedido otra vez;
- **frío:** con una marca distinta al comienzo del mensaje de sistema, para que no se
  pueda reutilizar nada.

Además se leyó el registro del servidor (`/opt/homebrew/var/log/ollama.log`), que dice
desde qué posición retoma cada pedido.

```bash
python analisis/2026-10-21-cache-prefijo/medir_cache.py --modelo qwen3.5:0.8b-q8_0
python analisis/2026-10-21-cache-prefijo/medir_cache.py --modelo qwen3.5:0.8b-q8_0 --extra '{"num_batch": 32}'
```

Salidas: [`cache_qwen3.5_0.8b-q8_0.json`](cache_qwen3.5_0.8b-q8_0.json) y
[`cache_qwen3.5_0.8b-q8_0_num_batch32.json`](cache_qwen3.5_0.8b-q8_0_num_batch32.json).
Se midió con Docker abierto y el swap cerca de 6 GB: los tiempos absolutos tienen ruido;
lo que importa es la comparación entre situaciones y lo que dice el registro.

## Resultado

Tiempo de procesar el prompt, en ms:

| Línea | Tokens | Secuencial | Repetido | Frío | Secuencial con `num_batch` 32 | Frío con `num_batch` 32 |
|---|---|---|---|---|---|---|
| 5 | 588 | 484 | 90 | 748 | 175 | 630 |
| 10 | 744 | 477 | 39 | 1875 | 113 | 793 |
| 15 | 879 | 994 | 30 | 830 | 124 | 920 |
| 20 | 1012 | 1152 | 31 | 1048 | 97 | 1036 |
| 25 | 1152 | 492 | 30 | 957 | 107 | 1191 |

- **La caché existe, pero en una corrida normal casi no sirve.** Un pedido idéntico se
  resuelve en 30 ms. El de la línea siguiente vuelve a procesar entre 530 y 630 tokens
  (registro: `restored context checkpoint … n_past = 474` para un prompt de 1012).
- **Por qué.** Qwen 3.5 es un modelo híbrido: parte de su memoria es recurrente y no se
  puede «rebobinar» a una posición cualquiera. El servidor de Ollama 0.40.5 (llama.cpp)
  solo retoma desde puntos guardados, y en cada pedido guarda dos: 4 tokens antes del
  final y un lote (`num_batch`, 512 por defecto) antes del final. El primero cae en la
  instrucción del final, que cambia en la línea siguiente, así que se descarta. Queda el
  segundo: cada línea vuelve a leer los últimos ~512 tokens más la línea nueva. Por eso
  el tiempo crece poco con la llamada larga, pero nunca baja de ~500 ms en el M1.
- **Con `num_batch` 32** el punto útil queda 32 tokens antes del final y cada línea
  procesa entre 51 y 153 tokens: el tiempo de prompt baja de 480–1150 ms a 100–175 ms.
  El costo en frío no empeoró en esta medición (630–1190 ms contra 750–1875 ms).
- **Lo que queda es escribir la respuesta.** Con la caché funcionando, el 0.8B tarda
  ~0,8 s en escribir los 39 tokens del JSON sin alerta (~20 ms por token). Achicar la
  salida es la palanca siguiente.

## ¿`num_batch` 32 cambia las respuestas?

Se corrió el 0.8B con prompt `tarea` sobre los 53 casos con `--num-batch 32`
([`2026-10-21_182201_m1-0.8b-v1v2-nb32`](../../corridas/2026-10-21_182201_m1-0.8b-v1v2-nb32/resumen.md))
y se comparó con la misma configuración del 2026-10-17 en la misma máquina, sin la
opción ([`2026-10-17_150516_m1-gguf`](../../corridas/2026-10-17_150516_m1-gguf/resumen.md)):

```bash
python analisis/2026-10-21-cache-prefijo/comparar_num_batch.py corridas/2026-10-17_150516_m1-gguf \
    corridas/2026-10-21_182201_m1-0.8b-v1v2-nb32 --config "slm|qwen3.5:0.8b-q8_0|tarea|ab"
```

| | Sin `num_batch` (512) | `num_batch` 32 |
|---|---|---|
| Respuestas crudas idénticas | — | 453 de 464 |
| Misma alerta | — | 461 de 464 |
| Mismo aviso por caso | — | 52 de 53 (cambia `TR-01`: L9 → sin aviso) |
| ms por línea p50 / p95 / media | 1282 / 3465 / 1670 | 1017 / 2993 / 1355 |

Salida: [`comparacion_0.8b_nb32.json`](comparacion_0.8b_nb32.json). Las diferencias son
del orden de las que ya había entre dos corridas iguales o entre M1 y Windows
([2026-10-17](../2026-10-17-m1-vs-windows/README.md)): sumar lotes en otro orden cambia
los decimales. La mediana baja 21 %: la mayoría de los casos son cortos y en ellos la
caché ya cubría casi todo; lo que domina es escribir la respuesta. Falta repetirlo con 2B
y 4B (`cola_m1.sh`).

## Qué cambia

- `correr.py --num-batch 32` pasa la opción a Ollama y queda en el manifiesto
  (`parametros_slm.hardware`).
- El panel decía que «hoy se reenvía toda la transcripción en cada línea». Se reenvía,
  pero se reutiliza todo menos los últimos ~512 tokens; el panel se corrigió.

## Límites

- Un solo caso, un modelo y una máquina, con memoria bajo presión. Es un mecanismo
  observado en el registro, no una medición de rendimiento.
- Depende de la versión de Ollama y de llama.cpp: hay que volver a comprobarlo al
  actualizar. En un celular el motor será otro.
