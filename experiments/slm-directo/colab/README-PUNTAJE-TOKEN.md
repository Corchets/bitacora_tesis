# #143: puntaje por probabilidad del token «SÍ», en Google Colab

> **Estado: propuesta sin discutir.** Prueba de desarrollo; la rama no contiene el test reservado.
> Diseño, regla de elección y definición de terminado en
> [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Prompts en
> [`prompts/README.md`](../prompts/README.md#pregunta-síno-143--2026-11-05).

## 1. Prueba de humo (antes de los 150)

Verifica que el primer token de `gemma4:e2b-it-q4_K_M` sea un SÍ/NO limpio antes de gastar la corrida grande.

**Humo 1 (2026-11-05, tag `colab/143-humo`): no pasó.** Con los prompts `*-sino`, `masa_si_no` ≥ 0,9 en solo 35,
31 y 38 de 48 líneas: cuando el modelo quería avisar, empezaba a escribir «al…» en vez de «SÍ».
[Resultado](../corridas/2026-11-05_humo-puntaje-token-1/humo.md) y causa en
[`prompts/README.md`](../prompts/README.md#prueba-de-humo-1-descartada-tarea-sino-v4-sino-v4-sin-reglas-sino).

**Humo 2 (tag `colab/143-humo-2`): A1 y A2 como los define #143.** Corre
[`humo_puntaje_token.py`](humo_puntaje_token.py) con Ollama 0.40.14 (el de las líneas base), el mismo digest del
modelo, `num_ctx` 4096, seed 42, temperatura 0 y `think` false:

1. Un pedido directo a `/api/chat` con `logprobs` y `top_logprobs` 20 (`v4-a1`), guardado entero en
   `respuesta-cruda.json`: es el formato real de Ollama, sin pasar por nuestro parser.
2. Diagnóstico de la humo 1 (`diagnostico-al.json`): con el prompt viejo `v4-sino`, 8 tokens en SC-WA-CODE-01-e01
   hasta L3 y CV2-D-L-BANCO-001 hasta L12, para dejar escrita la palabra que empezaba con «al».
3. A1 (`tarea-a1` + `ab`, `v4-a1` + `rol`) y A2 (`v4-a2` + `rol`), todas las líneas (`--seguir-tras-aviso`), sobre
   3 casos de desarrollo:
   - `CV2-D-V-ORGANISMO_PREVISIONAL-004`: estafa de corpus_v2, pedido en la línea 14 (21 líneas);
   - `CV2-D-L-BANCO-001`: legítima de corpus_v2 con pedido razonable (22 líneas);
   - `SC-WA-CODE-01-e01`: estafa corta del laboratorio, pedido del código en la línea 4 (5 líneas).
4. `humo.md`: por variante, PASA o NO PASA, `masa_si_no` (mínimo, mediana y cuántas líneas dan ≥ 0,9), los tokens
   elegidos, las líneas con masa baja y sus alternativas, y `p_si` línea por línea.

**Criterio, fijado antes de correr (Mateo, 2026-11-05):** `masa_si_no` ≥ 0,9 en al menos el 90 % de las líneas
(44 de 48) en cada variante. Si no se cumple, se ajusta solo la pregunta final, se registra en `prompts/README.md`
y se repite. `p_si` en estos 3 casos no se usa para elegir nada.

**Pasos:**

1. Abrir [`COLAB-HUMO-PUNTAJE-TOKEN.ipynb`](COLAB-HUMO-PUNTAJE-TOKEN.ipynb) en Colab (Archivo → Abrir notebook →
   GitHub, o subiendo el archivo) y elegir Entorno de ejecución → Cambiar tipo → **GPU T4**.
2. Ejecutar la única celda. El notebook clona el repositorio, trae el tag `colab/143-humo-2`, comprueba que apunte
   al commit fijado y corre el script desde ese commit, no desde una rama.
3. Al terminar baja `humo-puntaje-token-2.zip` (unos 10 minutos, casi todo instalación y descarga del modelo).
   Trae `humo.md`, `respuesta-cruda.json`, `diagnostico-al.json`, las tres corridas con `manifiesto.json` y
   `actualizaciones.csv`, `pip-freeze.txt`, `ollama-version.txt`, `script-sha256.txt` y `commit.txt`.

Sin Drive: el ZIP baja a la máquina local.

## 2. Corrida de los 150

Se prepara después de revisar la prueba de humo.
