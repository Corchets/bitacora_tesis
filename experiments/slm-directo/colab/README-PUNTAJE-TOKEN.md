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

**Humo 2 (2026-11-05, tag `colab/143-humo-2`): pasa.** `masa_si_no` ≥ 0,9 en 48 de 48 líneas en las tres variantes
([resultado](../corridas/2026-11-05_humo-puntaje-token-2/humo.md)). A1 y A2 como los define #143. Corre
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

## 2. Corrida de los 150 (tag `colab/143-150`)

Lee P(SÍ) del primer token en **todas las líneas** de los 150 casos de desarrollo (`--seguir-tras-aviso`), para
simular las políticas de aviso offline sin volver a correr el modelo. Usa
[`probar_puntaje_token.py`](probar_puntaje_token.py) con lo mismo que las líneas base JSON
(`2026-11-04_sin-indicio-150` y `2026-11-05_tito-2-v4`): Ollama 0.40.14, el mismo digest, `num_ctx` 4096, seed 42,
temperatura 0, `--sin-reglas` y los mismos hablantes (`ab` para tarea, `rol` para v4).

1. **Diagnóstico de «S»** (`diagnostico-s.json`). En la humo 2 el token elegido para SÍ fue siempre «S». Se generan
   3 tokens en tres líneas donde salió «S». Si no sigue como «SÍ», la lectura está mal y el script se detiene antes
   de gastar la corrida.
2. **Seis corridas, cada una en su carpeta.** Primero va lo que pide #143, por si Colab se corta:

   | Carpeta | Variante | Prompt | Hablantes |
   |---|---|---|---|
   | `v4-a1` | A1 | `v4-a1` | `rol` |
   | `v4-a2` | A2 | `v4-a2` | `rol` |
   | `v4-a1-rep` | repetición de A1 | `v4-a1` | `rol` |
   | `tarea-a1` | A1 con tarea (#51 sigue abierto) | `tarea-a1` | `ab` |
   | `v4-a2-rep` | repetición de A2 | `v4-a2` | `rol` |
   | `tarea-a1-rep` | repetición de A1 con tarea | `tarea-a1` | `ab` |

   Cada corrida guarda `actualizaciones.csv` (con `p_si`, `masa_si_no` y `top_logprobs`), `manifiesto.json`,
   `resumen.md` y `TERMINADA.txt` con los minutos.
3. **Registro:** `commit.txt`, `pip-freeze.txt`, `ollama-version.txt`, `script-sha256.txt` y `gpu.txt`.

Son 2.773 líneas por corrida, 16.638 consultas en total. Se calcula una hora en T4, más unos 5 minutos de
instalación.

**Pasos:**

1. Abrir [`COLAB-PUNTAJE-TOKEN.ipynb`](COLAB-PUNTAJE-TOKEN.ipynb) en Colab y elegir Entorno de ejecución → Cambiar
   tipo → **GPU T4**.
2. Ejecutar la única celda. El notebook trae el tag `colab/143-150`, comprueba que apunte al commit fijado y corre
   el script desde ese commit.
3. Dejar la pestaña abierta. Cada corrida terminada baja como `parcial-puntaje-token-<carpeta>.zip`, y al final
   baja `resultados-puntaje-token.zip` con todo. La primera vez el navegador pregunta si permite varias descargas:
   aceptar.
4. Si Colab se corta, los parciales ya descargados sirven. Si se vuelve a ejecutar la celda en la misma sesión,
   saltea las corridas terminadas. En una sesión nueva, empieza de cero.

El análisis (políticas, compuerta de Tito simulada y curva) se hace después, desde los CSV, con `analizar.py` en la
carpeta de la corrida.

## 3. Segunda vuelta, etapa 1 (tag `colab/143-ronda-2`)

> **Estado: propuesta sin discutir.** La lista se cerró el 2026-11-06, antes de correr. La regla y el análisis están en
> [`analizar.py`](../corridas/2026-11-06_puntaje-token-2/analizar.py); los prompts, en
> [`prompts/README.md`](../prompts/README.md#segunda-vuelta-2026-11-06-alcance-prompt-c-pregunta-al-final-y-lectura-del-token).

La primera vuelta no fue una prueba justa para el token. A1 preguntaba algo literal, y la pregunta quedaba antes de la
transcripción. Además, el equipo fijó el **alcance**: el detector corre solo en llamadas entrantes de números no
agendados. Como en corpus_v2 casi todas las legítimas las inicia la persona, la vuelta va en dos etapas:

- **Etapa 1 (este Colab):** **v4-L** contra v4 JSON sobre los 150. v4-L es el JSON de v4 tal cual, cortado después del
  primer decimal del riesgo, leyendo la distribución de ese dígito. Prueba la forma de leer con el mismo prompt y los
  mismos casos que la línea base. La humo controla además el formato de `c-sino` y `c-digito`, sin mirar sus
  resultados.
- **Etapa 2 (otro Colab, cuando estén las legítimas entrantes que genera Evaristo):** el prompt C con el alcance
  (`c-json`, `c-sino`, `c-digito`), `v4-premisa`, y v4 y v4-L sobre las legítimas nuevas.

[`probar_puntaje_token_2.py`](probar_puntaje_token_2.py) hace la etapa 1 en una sesión:

1. **Humo de formato** en los mismos 3 casos de la humo 2 (48 líneas), para `v4-lectura`, `c-sino` y `c-digito`.
   Criterio fijado antes de correr, en cada variante:
   - `masa` ≥ 0,9 en al menos 44 de 48 líneas;
   - con 3 tokens, la respuesta empieza con SÍ/NO o con un solo dígito (no «10») en al menos 44 de 48;
   - en v4-L, en vez de eso, que se encuentre el decimal del riesgo en al menos 44 de 48 líneas.
2. **v4-L sobre los 150** en todas las líneas (`--seguir-tras-aviso`) y su repetición. Cada corrida baja como
   `parcial-puntaje-token-2-<carpeta>.zip`.
3. **Controles de ventas** ([`casos/controles-ventas.json`](../casos/controles-ventas.json)) con v4-L y v4 JSON, solo para
   mirar.
4. Al final baja `resultados-puntaje-token-2.zip` con todo, más `commit.txt`, `pip-freeze.txt`,
   `ollama-version.txt`, `script-sha256.txt` y `gpu.txt`.

Se calcula alrededor de 35 minutos en T4: unos 8 minutos por corrida de v4-L, más la instalación, la humo y los
controles.

**Pasos:** abrir [`COLAB-PUNTAJE-TOKEN-2.ipynb`](COLAB-PUNTAJE-TOKEN-2.ipynb) en Colab con **GPU T4**, ejecutar la única
celda y dejar la pestaña abierta, aceptando las descargas múltiples. Si Colab se corta, los parciales ya descargados
sirven, y si se vuelve a ejecutar la celda en la misma sesión, saltea lo terminado.

## 4. JSON de v4 cortado después de la alerta (tag `colab/143-json-cortado`)

> **Estado: propuesta sin discutir.** Mide una decisión ya tomada; no elige nada. El criterio está escrito antes de
> correr en [`corridas/2026-11-07_json-cortado/README.md`](../corridas/2026-11-07_json-cortado/README.md), y el
> análisis, en [`analizar.py`](../corridas/2026-11-07_json-cortado/analizar.py). Se corrió el 2026-11-07 y pasa: ver
> [`analisis.md`](../corridas/2026-11-07_json-cortado/analisis.md).

**Decisión de Mateo (2026-11-07),** después de la etapa 1
([`analisis.md`](../corridas/2026-11-06_puntaje-token-2/analisis.md)):
- el detector sigue con el JSON de v4 y «riesgo ≥ 0,4 o alerta» (29/46 estafas de corpus_v2, 11 antes del pedido,
  7/51 FA);
- la lectura del token (v4-L) queda para después de un ajuste fino.

Para bajar la latencia:

- **Primera consulta (`v4-corte`):**
  - el mismo prompt (`tarea_v4.txt`), el mismo mensaje y el mismo esquema que v4 JSON, sin logprobs;
  - solo cambia `num_predict`: 24 tokens (`MAXIMO_TOKENS_CORTE`) en vez de los 41 del JSON entero, que cortan el JSON
    justo después del valor de `alerta_sugerida`;
  - el riesgo y la alerta se leen del texto cortado, también `"riesgo": 0`, sin decimal.
- **Segunda consulta, solo en la línea de aviso,** que es la primera línea de la llamada en que dispara «riesgo ≥ 0,4 o
  alerta»:
  - repite los mensajes y agrega lo que escribió el modelo, cerrado como JSON, como turno `assistant`;
  - pide evidencia y motivo con [`motivo_v4_corte.txt`](../prompts/motivo_v4_corte.txt) y `ESQUEMA_MOTIVO`. Es el pedido de
    `riesgo_motivo.txt` (diseño «riesgo primero») sin «El riesgo superó el umbral», que es falso cuando el aviso sale por
    la alerta escrita con riesgo < 0,4;
  - no repite el JSON de v4: cuando avisa por el riesgo con la alerta en false, v4 deja motivo y evidencia vacíos;
  - como empieza igual que la primera, Ollama reutiliza la transcripción ya procesada.

[`probar_json_cortado.py`](probar_json_cortado.py) hace todo en una sesión. Usa Ollama 0.40.14, el digest
`b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, `--sin-reglas` y roles:

1. **Humo de formato** en los 3 casos de las humos anteriores (48 líneas). Criterio fijado antes de correr:
   - con el JSON completo de v4 y logprobs, el valor de `alerta_sugerida` termina a más tardar en el token 24 en las
     48 líneas (`humo/tokens-hasta-alerta.json`);
   - `v4-corte` lee riesgo y alerta en las 48 líneas.

   Si no pasa, el script se detiene antes de los 150. Se corrige `MAXIMO_TOKENS_CORTE` en `detectores.py` según los
   tokens medidos, con un tag nuevo, y se repite.
2. **`v4-corte` sobre los 150** en todas las líneas (`--seguir-tras-aviso`), con la segunda consulta en la línea de
   aviso de cada llamada. Registra `ms_etapa1`, `ms_etapa2`, los tokens de cada consulta y `alerta_escrita`.
3. **El JSON completo de v4** sobre los 150 en las mismas condiciones, para comparar línea a línea riesgo, alerta y
   ms. Va en la misma sesión porque dos corridas iguales coinciden ~96 % en el riesgo escrito si son de la misma
   sesión, y ~91 % si no.
4. Al final baja `resultados-json-cortado.zip` con todo, más `commit.txt`, `script-sha256.txt`, `ollama-version.txt`,
   `digest.txt`, `pip-freeze.txt` y `gpu.txt`. La humo y cada corrida bajan antes como
   `parcial-json-cortado-<carpeta>.zip`.

Se calcula alrededor de 45 minutos en T4: unos 15 minutos para `v4-corte` y unos 20 para v4 JSON, más la instalación y
la humo.

**Pasos:**
1. Abrir [`COLAB-JSON-CORTADO.ipynb`](COLAB-JSON-CORTADO.ipynb) en Colab con **GPU T4**. El notebook no corre hasta
   tener el hash del commit del tag.
2. Ejecutar la única celda y dejar la pestaña abierta, aceptando las descargas múltiples. Si Colab se corta, los
   parciales ya descargados sirven, y si se vuelve a ejecutar la celda en la misma sesión, saltea lo terminado.
3. Descomprimir los ZIP en `corridas/2026-11-07_json-cortado/` y correr `python -I analizar.py` desde esa carpeta.

## 5. Segunda vuelta, etapa 2 (tag `colab/143-etapa-2`)

> **Estado: propuesta sin discutir.** Elige entre prompts dentro del alcance. El criterio está escrito antes de correr
> en [`corridas/2026-11-07_alcance-etapa-2/README.md`](../corridas/2026-11-07_alcance-etapa-2/README.md), y el
> análisis, en [`analizar.py`](../corridas/2026-11-07_alcance-etapa-2/analizar.py).

**Qué pregunta:** ¿el prompt C o `v4-premisa` le ganan a v4 dentro del alcance? La vista son las 46 estafas de
corpus_v2 y las 94 legítimas entrantes de #155.

**Decisión de Mateo (2026-11-07):**
- todos los prompts usan el JSON cortado (ADR 0006): `v4-corte` es la referencia, y `c-json-corte` y
  `v4-premisa-corte` son las candidatas;
- cada candidata corre dos veces: la primera sobre los 244 y la repetición sobre los 140 dentro del alcance.

Los prompts cortados son su prompt base tal cual (`CORTE_DE` en `detectores.py`), con `num_predict` 24 y la segunda
consulta de [`motivo_v4_corte.txt`](../prompts/motivo_v4_corte.txt).

[`probar_etapa_2.py`](probar_etapa_2.py) hace todo en una sesión. Usa Ollama 0.40.14, el digest `b37049369adf…`,
`num_ctx` 4096, seed 42, temperatura 0, `--sin-reglas`, roles y todas las líneas (`--seguir-tras-aviso`):

1. **Humo de formato** de `c-json-corte` y `v4-premisa-corte`, en los 3 casos de las humos anteriores (48 líneas).
   Criterio fijado antes de correr, para cada uno:
   - con el JSON completo del prompt base y logprobs, el valor de `alerta_sugerida` termina a más tardar en el token
     24 en las 48 líneas;
   - el cortado lee riesgo y alerta en las 48.

   Se informa también, como dato, en cuántas de las 48 el cortado escribe lo mismo que el completo. El prompt que no
   pasa no corre, y no se ajusta nada en esa sesión.
2. **Corridas**, en este orden. Cada candidata va entera antes de la siguiente, así un corte de Colab deja una
   respuesta:
   1. `v4-corte` sobre los 244;
   2. `c-json-corte` sobre los 244, y su repetición sobre [`alcance-140`](../casos/listas/alcance-140.txt);
   3. `v4-premisa-corte` sobre los 244, y su repetición sobre `alcance-140`.
3. **Controles de ventas y préstamos** con los tres prompts, solo para mirar.
4. **Al final** baja `resultados-etapa-2.zip` con todo, más `commit.txt`, `script-sha256.txt`, `ollama-version.txt`,
   `digest.txt`, `pip-freeze.txt` y `gpu.txt`. La humo y cada corrida bajan antes como `parcial-etapa-2-<carpeta>.zip`.

**Duración estimada:** unas 2 horas en T4. Cada corrida sobre los 244 (4.325 líneas) lleva unos 23 minutos, y cada
repetición sobre los 140 (2.621 líneas), unos 14.

**Pasos:**
1. Abrir [`COLAB-ETAPA-2.ipynb`](COLAB-ETAPA-2.ipynb) en Colab con **GPU T4**. El notebook no corre hasta tener el hash
   del commit del tag.
2. Ejecutar la única celda y dejar la pestaña abierta, aceptando las descargas múltiples.
   - Si Colab se corta, los parciales ya descargados sirven.
   - Si se vuelve a ejecutar la celda en la misma sesión, saltea lo terminado.
3. Descomprimir cada ZIP en un directorio vacío nuevo, verificarlo y copiarlo a `corridas/2026-11-07_alcance-etapa-2/`.
   Después, correr `python -I analizar.py` desde esa carpeta.

## 6. Segunda vuelta, etapa 3 (tag `colab/143-etapa-3`)

> **Estado: propuesta sin discutir.** Elige entre dos versiones de C dentro del alcance. La regla está escrita antes de
> correr en [`corridas/2026-11-09_pedido-critico-etapa-3/README.md`](../corridas/2026-11-09_pedido-critico-etapa-3/README.md),
> y el análisis, en [`analizar.py`](../corridas/2026-11-09_pedido-critico-etapa-3/analizar.py).

**Qué pregunta:** ¿un campo `pedido_critico` en el JSON de C le suma avisos a C sin sumar más de 5 FA? La vista son las
46 estafas de corpus_v2 y las 94 legítimas entrantes.

**Decisiones de Mateo (2026-11-09):**
- dos versiones con el texto de tarea de C y una sola consulta por línea:
  - «C sin alerta» (`c-sin-alerta`), la base, pide solo el riesgo;
  - «C con campo» (`c-con-campo`) pide `pedido_critico` y después el riesgo;
- avisan con «riesgo ≥ 0,3», o `pedido_critico` en C con campo, en cualquier línea. «Solo OTRA» se simula después;
- el primer aviso muestra un texto fijo. El motivo propio de C ([`motivo_c_corte.txt`](../prompts/motivo_c_corte.txt))
  se pide solo en la primera alerta fuerte, una vez por llamada;
- cada versión corre dos veces: sobre los 244 y sobre los 140 dentro del alcance.

**El JSON es corto y el modelo lo cierra solo.** `num_predict` 48 (`MAXIMO_TOKENS_C_CORTO`) es solo un tope, y llegar
a él cuenta como fallo.

[`probar_etapa_3.py`](probar_etapa_3.py) hace todo en una sesión. Usa Ollama 0.40.14, el digest `b37049369adf…`,
`num_ctx` 4096, seed 42, temperatura 0, `--sin-reglas`, roles y todas las líneas (`--seguir-tras-aviso`):

1. **Humo de formato** en los 3 casos de siempre (48 líneas), con `c-json-corte`, `c-sin-alerta` y `c-con-campo` en una
   corrida. Criterio fijado antes de correr: cada versión lee el JSON en las 48 líneas, sin llegar al tope.

   **Si una versión no pasa:**
   - la que no pasa no corre;
   - si no pasa ninguna, no corre nada.

   No se ajusta nada en esa sesión.
2. **Corridas**, en este orden:
   1. `c-sin-alerta` y `c-con-campo` sobre los 244;
   2. sus repeticiones sobre [`alcance-140`](../casos/listas/alcance-140.txt).
3. **Controles de ventas y préstamos** con las dos, solo para mirar.
4. **Al final** baja `resultados-etapa-3.zip` con todo, más `commit.txt`, `script-sha256.txt`, `ollama-version.txt`,
   `digest.txt`, `pip-freeze.txt` y `gpu.txt`. La humo y cada corrida bajan antes como `parcial-etapa-3-<carpeta>.zip`.

**Duración estimada:** alrededor de 1 h en T4.

**Pasos:**
1. Abrir [`COLAB-ETAPA-3.ipynb`](COLAB-ETAPA-3.ipynb) en Colab con **GPU T4**. El notebook no corre hasta tener el hash
   del commit del tag.
2. Ejecutar la única celda y dejar la pestaña abierta, aceptando las descargas múltiples.
   - Si Colab se corta, los parciales ya descargados sirven.
   - Si se vuelve a ejecutar la celda en la misma sesión, saltea lo terminado.
3. Descomprimir cada ZIP en un directorio vacío nuevo, verificarlo y copiarlo a
   `corridas/2026-11-09_pedido-critico-etapa-3/`. Después, correr `python -I analizar.py` desde esa carpeta. Necesita las
   corridas de C de la etapa 2 en `corridas/2026-11-07_alcance-etapa-2/`.
