# a56-congelada-latencia — 2026-11-10

Latencia A56 de la configuración congelada de [#143](../2026-11-10_config-congelada-humo/README.md), en el Samsung
Galaxy A56, sobre tres conversaciones traducidas por Luciano para #144. **Solo mide tiempos.** Una pasada, sin audio.
No selecciona stack ni cierra D08 ni D09.

> **Conversaciones de test de #144.** EN-07, EN-09 y EN-13 son del test de #144
> ([`ISSUE-144-INGLES-18-2026-11-07.md`](../../../../docs/corpus/ISSUE-144-INGLES-18-2026-11-07.md)). Se usaron con
> la configuración ya congelada y bajo una condición: no se miran ni se informan riesgo, avisos, motivos ni evidencia.
> [`turnos.jsonl`](turnos.jsonl) los guarda crudos para la evaluación final. [`resumir.py`](resumir.py) no los lee.
> El único dato que se filtra es inevitable: que hubo 3 consultas de motivo, una por conversación, sin línea ni contenido.

## Configuración

- **Stack:** Gemma 4 E2B `Q4_K_M`, sola (sin Tito), prompt `c-json-corte-riesgo`, `num_predict` 14, aviso con
  riesgo ≥ 0,3 y motivo de C solo en el primer aviso (ADR 0006). Consulta solo en las líneas de OTRA (ADR 0007),
  `--hablantes rol`, contexto 4096, temperatura 0, seed 42.
- **Recorrido:** todas las líneas, aunque ya haya avisado (modo diagnóstico, como `--seguir-tras-aviso`), para tener
  más mediciones. El motivo se pide una sola vez por llamada.
- **Dispositivo y runtime:** son los mismos de la [corrida del 2026-11-06](../2026-11-06-a56-diagnostico.md):
  - Samsung SM-A566E con Android 16, por USB y cargando, con las apps en segundo plano cerradas (`am kill-all`).
  - `llama-server` (llama.cpp `6c01da62`, un slot, caché activa, CPU con 4 hilos) y el mismo GGUF.
  - Python 3.14.10 en Termux.
- **Ejecutor:** [`correr_android_congelada.py`](../../correr_android_congelada.py). Usa `DetectorSLMCorteRiesgo` de
  [`detectores.py`](../../detectores.py) y el cliente de `llama-server` de `correr_android.py`. Los hashes del código,
  del prompt, del motivo y de las conversaciones están en el [manifiesto](manifiesto.json).

## Conversaciones

[`extraer.py`](extraer.py) arma [`conversaciones.json`](conversaciones.json) a partir del documento de Luciano:

- Toma solo los renglones numerados del diálogo, tal como están escritos.
- Deja afuera el encabezado, el canal, el contexto y la ficha.
- Saca las negritas, las cursivas y las marcas del traductor entre acentos graves.
- El hablante es la letra escrita: A = OTRA (estafador), B = PROTEGIDA.

Esto deja dos casos especiales en EN-07:

- El renglón 10 está escrito como B, aunque la marca dice «probable A». Por eso entra como PROTEGIDA y no consulta.
- El 29 es un turno pegado de A y B. Entra como una sola línea de OTRA.

| Caso | Renglones | Consultas (OTRA) |
|---|---:|---:|
| EN-07 | 30 | 16 |
| EN-09 | 20 | 10 |
| EN-13 | 26 | 14 |

## Resultado: 40/40 consultas válidas

| Medición | n | Mediana | p95 | Máximo |
|---|---:|---:|---:|---:|
| Actualización completa (todas las consultas) | 40 | 3,66 s | 12,31 s | 17,71 s |
| Actualización sin motivo | 37 | 3,60 s | 4,90 s | 4,91 s |
| Primera consulta (riesgo, 14 tokens) | 40 | 3,61 s | 4,90 s | 4,92 s |
| Segunda consulta (motivo, primer aviso) | 3 | 10,99 s | 12,78 s | 12,78 s |
| Procesar prompt, runtime (1.ª consulta) | 40 | 1,95 s | 3,05 s | 3,27 s |
| Generar, runtime (1.ª consulta) | 40 | 1,61 s | 1,76 s | 1,81 s |
| Tokens de prompt nuevos (1.ª consulta) | 40 | 63 | 114 | 132 |
| Tokens de prefijo reutilizados (sin motivo) | 37 | 813 | 1.241 | 1.313 |
| Tokens generados (1.ª consulta) | 40 | 14 | 14 | 14 |

- El p95 es el valor por rango más próximo superior. Los componentes van por separado y sus percentiles no se suman.
- La suma de las 40 actualizaciones es 181,3 s, y la corrida completa duró 3 min 1 s. Ese número no es la latencia de
  una llamada en tiempo real: no modela llegadas ni cola.
- El calentamiento con una línea neutra, fuera de las conversaciones, tardó 1,81 s. El modelo cargó en 4,25 s, con
  el GGUF posiblemente en la caché del sistema.
- Los picos de memoria (`VmHWM`) fueron 3,39 GiB en `llama-server` y unos 30 MiB en Python, que corre sin torch.
- La temperatura de batería quedó entre 33,3 y 33,9 °C en las 6 muestras de esta corrida, tomadas cada 30 s.
- No se midieron consumo, temperatura de CPU ni throttling. Una pasada no permite estimar la variabilidad.

## Primer intento: esquema ignorado por `llama-server`

El [primer intento](intento-1-esquema-ignorado/) dio 0/40 consultas válidas (`sin_riesgo`). La causa:

- `llama-server` recibía el esquema como `response_format`, y con la plantilla de Gemma lo aplica de forma perezosa.
- Por eso dejaba pasar un bloque ` ```json\n ` (3 tokens) antes del `{`, y la coma del riesgo quedaba fuera de los 14
  tokens.
- Con Ollama, `format` sí obliga a arrancar en `{`, y la coma llega en el token 12. En este teléfono, con gramática,
  también llega en el token 12.

Se verificó con una línea neutra, ajena a las conversaciones. El arreglo, en el ejecutor:

- El esquema se manda como gramática GBNF (`grammar`), con las mismas reglas primitivas que usa llama.cpp.
- Antes de repetir se probó en el teléfono, también con una línea neutra: la consulta de riesgo dio JSON válido con
  la coma en 14 tokens, y la de motivo dio JSON válido.

Las salidas del primer intento tampoco se miraron.

`correr_android.py` (la corrida del 2026-11-06) usa el mismo `response_format`. Ahí el JSON completo se leía igual
porque el lector tolera el bloque de código, pero cada consulta pagaba esos 3 tokens de más. No se midió cuánto.

## Archivos

- [`turnos.jsonl`](turnos.jsonl): crudo por línea.
- [`manifiesto.json`](manifiesto.json).
- [`resumen.json`](resumen.json), generado por `resumir.py`.
- [`ejecucion.log`](ejecucion.log).
- [`runtime.log`](runtime.log): log de `llama-server` de las dos corridas.
- [`recursos.log`](recursos.log): telemetría de las dos corridas, separadas por la marca `=== intento 2`.

## Repetir

Con los archivos en el teléfono, como en la corrida del 2026-11-06:

```sh
adb shell 'cd /data/local/tmp/a56-lab/llama && LD_LIBRARY_PATH=. ./llama-server -m /data/local/tmp/a56-lab/gemma.gguf --host 127.0.0.1 --port 18080 -c 4096 -t 4 -ngl 0 -np 1 --no-webui'
adb shell 'run-as com.termux env HOME=/data/data/com.termux/files/home PATH=/data/data/com.termux/files/usr/bin:/system/bin sh -c "cd ~/a56-congelada && python correr_android_congelada.py --conversaciones corridas/2026-11-10_a56-congelada-latencia/conversaciones.json --salida ~/a56-congelada/SALIDA_NUEVA"'
```
