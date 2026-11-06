# #143: puntaje por probabilidad del token «SÍ», en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo; la rama no contiene el test reservado.
> Diseño, regla de elección y definición de terminado en
> [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Prompts en
> [`prompts/README.md`](../prompts/README.md#pregunta-síno-143--2026-11-05).

## 1. Prueba de humo (antes de los 150)

Verifica que el primer token de `gemma4:e2b-it-q4_K_M` sea un SÍ/NO limpio antes de gastar la corrida grande.

**Qué corre** ([`humo_puntaje_token.py`](humo_puntaje_token.py)), con Ollama 0.40.14 (el de las líneas base), el
mismo digest del modelo, `num_ctx` 4096, seed 42, temperatura 0 y `think` false:

1. Un pedido directo a `/api/chat` con `logprobs` y `top_logprobs` 20, guardado entero en `respuesta-cruda.json`:
   es el formato real de Ollama, sin pasar por nuestro parser.
2. Los tres prompts con sus hablantes (`tarea-sino` + `ab`, `v4-sino` + `rol`, `v4-sin-reglas-sino` + `rol`),
   todas las líneas (`--seguir-tras-aviso`), sobre 3 casos de desarrollo:
   - `CV2-D-V-ORGANISMO_PREVISIONAL-004`: estafa de corpus_v2, pedido en la línea 14 (21 líneas);
   - `CV2-D-L-BANCO-001`: legítima de corpus_v2 con pedido razonable (22 líneas);
   - `SC-WA-CODE-01-e01`: estafa corta del laboratorio, pedido del código en la línea 4 (5 líneas).
3. `humo.md`: por prompt, `masa_si_no` (mínimo, mediana y cuántas líneas dan ≥ 0,9), los tokens elegidos, las
   líneas con masa baja y sus alternativas, y `p_si` línea por línea.

**Criterio, escrito antes de correr:** `masa_si_no` ≥ 0,9 en casi todas las líneas. Si no da, se ajusta solo la
instrucción de respuesta (la última línea del prompt), se registra en `prompts/README.md` y se repite la humo.
`p_si` en estos 3 casos no se usa para elegir nada.

**Pasos:**

1. Abrir [`COLAB-HUMO-PUNTAJE-TOKEN.ipynb`](COLAB-HUMO-PUNTAJE-TOKEN.ipynb) en Colab (Archivo → Abrir notebook →
   GitHub, o subiendo el archivo) y elegir Entorno de ejecución → Cambiar tipo → **GPU T4**.
2. Ejecutar la única celda. El notebook clona el repositorio, trae el tag `colab/143-humo`, comprueba que apunte al
   commit fijado (`9a2692e`) y corre el script desde ese commit, no desde una rama.
3. Al terminar baja `humo-puntaje-token.zip` (unos 10 minutos, casi todo instalación y descarga del modelo).
   Trae `humo.md`, `respuesta-cruda.json`, las tres corridas con `manifiesto.json` y `actualizaciones.csv`,
   `pip-freeze.txt`, `ollama-version.txt`, `script-sha256.txt` y `commit.txt`.

Sin Drive: el ZIP baja a la máquina local.

## 2. Corrida de los 150

Se prepara después de revisar la prueba de humo.
