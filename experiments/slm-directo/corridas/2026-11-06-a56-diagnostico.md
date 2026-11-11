# Ensayo exploratorio de texto en Samsung Galaxy A56 — 2026-11-06

Relacionado: [#141](https://github.com/Corchets/bitacora_tesis/issues/141). Una pasada de 20 conversaciones de desarrollo; no selecciona definitivamente el stack ni cierra D08. No se utilizó audio. Las referencias de estos casos no están revisadas por humanos.

## Configuración y datos

- Samsung SM-A566E, Android 16 (compilación `BP2A.250605.031.A3.A566EXXS8BZA1`), ARM64, 11.669.384 KiB de RAM física; conectado por USB, pantalla encendida y cargando. Una muestra, seleccionada por familia y dificultad entre los casos de desarrollo del corpus v2: diez vishing y diez legítimos. IDs y hashes de textos en el [manifiesto](2026-11-06-a56-manifiesto.json). Sin aleatoriedad en la selección: se eligieron casos concretos; no se usó test reservado.
- Tito viejo 2.0, umbral 0,5, sin indicio, `v4`, roles, Gemma 4 E2B `Q4_K_M`, contexto 4096, temperatura 0, seed 42, máximo 512 tokens, inferencia CPU, cuatro hilos para cada proceso. RoBERTuito `pysentimiento/robertuito-base-uncased` revisión `20cb399e4b93f270c0cd6b6f533bcb0ada3cb658`; `model.safetensors` SHA-256 `14092d0fa1eeaf8582f81ac2eb42e5fa8e23533aa142a6aa9eb9d2b92c2b143b`, tokenizador `9465c3d57686e6b117d7c8f0e65b2b7d3a6bfb1d3c5154b52b175b3e37f2047c`, regresión `fb601eaa8ecb8d51e0d37f1d5af00ec4ca41706ef638fe2780ae276e5098eccd`.
- GGUF de Ollama `gemma4:e2b-it-q4_K_M`, capa de modelo SHA-256 `6dd7ac24fe13a238898e16e253ebc7a72fa27fb83f2658c2f6c241df3af5937d`. Solo texto, sin proyector ni modelo auxiliar. `llama.cpp` compilado con Android NDK 28.2.13676358, commit `6c01da6278ab6c69ed67d9124806b50d2b299ba7`; `llama-server` con un slot y caché activa. PyTorch 2.15.0, Python 3.14.10, Transformers 4.57.6 y tokenizers 0.22.2 en Termux.
- Código base `794e3d5764efae6646dd726978aab70be6cdcb22` más [ejecutor Android](../correr_android.py), no incluido en ese commit: el hash del archivo figura en el manifiesto. Este adaptador usa API compatible con OpenAI de `llama-server`, no Ollama; cambia el runtime respecto de las corridas anteriores y no se probó equivalencia numérica. Desactiva razonamiento y usa un esquema JSON. Es una adaptación exploratoria, no una selección de arquitectura.
- Se procesaron todos los turnos, aun después del primer aviso, para observar tiempos. Las salidas se guardaron por turno y no modelan llegadas en tiempo real ni cola de procesamiento.

## Integridad y tiempos

La primera pasada completó **475/475 turnos**, 20/20 conversaciones y cero respuestas inválidas: 54 turnos omitieron Gemma y 421 lo consultaron. Se pidió detenerla después de una pasada; comenzó un turno de una segunda antes de interrumpir el proceso. El JSONL conserva ese turno adicional, identificado como `pasada: 2`; todos los valores de este diagnóstico filtran `pasada: 1`. El manifiesto mantiene `pasadas: 3`, configuración original, no el número finalmente completado. El `KeyboardInterrupt` del [log](2026-11-06-a56-ejecucion.log) corresponde al corte solicitado durante ese turno adicional.

| Medición | n | Mediana | p95 | Máximo |
|---|---:|---:|---:|---:|
| Actualización completa | 475 | 7,85 s | 14,63 s | 22,02 s |
| Tito, cuando se ejecuta | 74 | 0,201 s | 0,340 s | 0,498 s |
| Consulta a Gemma | 421 | 7,94 s | 14,76 s | 21,85 s |
| Procesar prompt, tiempo del runtime | 421 | 1,49 s | 2,08 s | 15,65 s |
| Generar respuesta, tiempo del runtime | 421 | 6,33 s | 13,25 s | 18,18 s |

El p95 es el valor por rango más próximo superior. Los componentes se reportan separadamente y sus percentiles no se suman. La suma de los tiempos de las 475 actualizaciones fue 3.739,7 s; no representa la latencia de una llamada en tiempo real. Mediana de salida: 46 tokens; mediana de tokens de prefijo reutilizados: 1.098 según el runtime. No se comparó caché encendida contra apagada, por lo que no se puede cuantificar su beneficio.

El proceso de Gemma informó modelo cargado a los 3,56 s de iniciar, con archivos potencialmente en caché del sistema; no es arranque tras reinicio del teléfono. El calentamiento de Gemma tardó 26,99 s; la carga del encoder 0,48 s y su calentamiento 0,93 s. Los tiempos de preparación no están incluidos en los turnos.

Tito solo se ejecuta hasta que se activa la compuerta, que permanece activa hasta reiniciar la conversación. Por eso se invocó Gemma en 421/475 turnos (88,6 %), aun después de avisos. Esto explica en parte el tiempo total y no equivale al costo de la política operativa de detenerse al primer aviso.

## Respuestas y límites

Según las referencias provisionales, hubo al menos un aviso en 5/10 casos vishing y 2/10 legítimos. En `CV2-D-V-BANCO-006` el primer aviso precedió a `T_R` (línea 10 frente a línea 14); eso no prueba anticipación correcta sin revisar el diálogo y la referencia. En los legítimos `CV2-D-L-BANCO-006` y `CV2-D-L-ORGANISMO_PREVISIONAL-001` avisó en las líneas 15 y 4. Son recuentos descriptivos de una selección pequeña, sin adjudicación humana ni estimación poblacional. Las salidas válidas solo demuestran que cumplen la validación estructural, no que el juicio sea correcto. No se calcula anticipación temporal en segundos ni el efecto del ASR.

La memoria observada como `VmHWM` llegó a 3,39 GiB para el proceso de Gemma y 0,70 GiB para el proceso Python/Tito; son picos separados, no una medición de memoria agregada sin duplicaciones. La temperatura de batería en 61 muestras fue 33,9–36,5 °C; al inicio marcó 33,6 °C y al final 36,6 °C. El teléfono cargó de 87 % a 92 %, por lo que no se mide consumo. No se midieron temperatura de CPU, consumo energético ni throttling y una sola pasada no permite estimar variabilidad entre repeticiones.

## Evidencia y reproducción

[Turnos crudos](2026-11-06-a56-turnos.jsonl), [resumen generado](2026-11-06-a56-resumen.json), [telemetría](2026-11-06-a56-recursos.log) y [log del runtime](2026-11-06-a56-runtime.log). El resumen descarta la segunda pasada parcial. La temperatura es la informada por Android para la batería, en décimas de grado.

Para repetir en este teléfono, con los artefactos todavía en las rutas usadas y el código copiado a Termux, arrancar `llama-server` en el dispositivo y luego el ejecutor, usando una ruta de salida nueva. El primero se cargó antes de la preparación y calentamiento del segundo:

```sh
adb shell 'cd /data/local/tmp/a56-lab/llama && LD_LIBRARY_PATH=. ./llama-server -m /data/local/tmp/a56-lab/gemma.gguf --host 127.0.0.1 --port 18080 -c 4096 -t 4 -ngl 0 -np 1 --no-webui'
adb shell 'run-as com.termux env HOME=/data/data/com.termux/files/home PREFIX=/data/data/com.termux/files/usr PATH=/data/data/com.termux/files/usr/bin:/system/bin python /data/data/com.termux/files/home/a56-lab/correr_android.py --encoder /data/local/tmp/a56-lab/robertuito --salida /data/data/com.termux/files/home/a56-nueva --pasadas 1 --hilos 4'
```

Los comandos requieren el runtime, archivos, dependencias y selección copiados durante este ensayo; no constituyen todavía un instalador desde cero. El servidor se detiene aparte. El ajuste temporal que mantenía la pantalla encendida por USB se restauró a `0`. Queda pendiente validar la equivalencia de la adaptación, repetir condiciones y completar la comparación de caché solicitada por #141.
