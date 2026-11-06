# #143: P(SÍ) del primer token en los 150 de desarrollo

> **Estado: propuesta sin discutir.** Prueba de desarrollo; la reserva no se tocó. Diseño y regla de elección en
> [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Las cifras salen de [`analizar.py`](analizar.py)
> (`python -I analizar.py`); la salida completa está en [`analisis-salida.md`](analisis-salida.md) y la curva entera
> en [`curva.csv`](curva.csv).

## Qué se corrió

- **Seis corridas en Colab T4**, el 2026-11-06 entre las 02:42 y las 03:09 UTC (23:42 a 00:09 en Argentina; 27
  minutos): A1 con v4 y roles, A2 con v4 y roles, y
  A1 con tarea y A/B, cada una con su repetición, en todas las líneas (`--seguir-tras-aviso`).
- **Mismo setup que las líneas base JSON:** commit `8f6c0a4` (tag `colab/143-150`), Ollama 0.40.14, digest
  `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, `--sin-reglas` y los mismos hablantes. Los prompts están
  en [`prompts/README.md`](../../prompts/README.md#a1-y-a2-tabla-variantes-de-143-actualizada-el-2026-11-05).
- **La lectura del token es limpia:**
  - 16.638 líneas, ninguna inválida, `masa_si_no` ≥ 0,999 en todas;
  - el diagnóstico confirma que «S» sigue como «SÍ» (`diagnostico-s.json`).
- **La tabla de referencia de las líneas base se reproduce exacta** (v1 28/13/4, v1 + Tito 27/12/4, v4 28/9/6). El
  «riesgo ≥ 0,3» del issue también se reproduce (v4 + Tito 37–38/46, 20 antes, 14/51).

## Resultado según la regla de #143

Se elige sobre el SLM solo, con falsas alarmas ≤ 7/51 en corpus_v2. Las decisiones que no estaban en #143 están
escritas en `analizar.py` y se fijaron antes de ver estas corridas.

| corpus_v2, FA ≤ 7/51 | punto | estafas (de 46) | antes del pedido (de 36) | FA (de 51) | repetición, mismo punto |
|---|---|---|---|---|---|
| **A1 v4** (token) | EMA α = 0,5, umbral 0,72 | 26 | 4 | 7 | 26 / 4 / 6 |
| línea base v4 JSON | riesgo ≥ 0,4 o alerta | 29 | 11 | 7 | — |
| v4 JSON, solo `alerta_sugerida` (dato) | primer aviso | 28 | 9 | 6 | — |
| **A2 v4** (token) | EMA α = 0,5, umbral 0,89 | 25 | 2 | 7 | 24 / 2 / 8 |
| **A1 tarea** (token) | dos seguidas, umbral 0,002 | 27 | 9 | 6 | 27 / 9 / 7 |
| línea base v1 JSON | riesgo ≥ 0,4 o alerta | 30 | 14 | 7 | — |
| v1 JSON, solo `alerta_sugerida` (dato) | primer aviso | 28 | 13 | 4 | — |

- **Adopción: no.**
  - A1 v4 detecta 3 estafas menos que su línea base JSON y A1 tarea, también 3 menos.
  - Contra `alerta_sugerida` sola quedan en −2 y −1, dentro del ruido.
  - En ningún caso el token mejora, y avisa antes del pedido menos veces (A1 v4: 4 contra 9–11).
- **A2 frente a A1: no se prefiere.** Detecta 1 estafa menos y 2 avisos antes del pedido menos, con las mismas falsas
  alarmas en trampa (3/7). Preguntar por la intención no hizo subir P(SÍ) antes del pedido sin sumar falsas alarmas.
- **La repetición confirma los puntos:** quedan a ±1 caso.

## Por qué: el puntaje no sale continuo

Con temperatura 0, el primer token de gemma4 E2B está casi decidido. Entre el 90 y el 94 % de las líneas tiene
P(SÍ) ≤ 0,01 o ≥ 0,99:

| corrida | P(SÍ) ≤ 0,01 | entre 0,01 y 0,99 | P(SÍ) ≥ 0,99 |
|---|---|---|---|
| A1 v4 | 79,0 % | 6,6 % | 14,4 % |
| A2 v4 | 74,0 % | 10,0 % | 16,0 % |
| A1 tarea | 85,4 % | 6,0 % | 8,6 % |

Así que la curva funciona casi como el SÍ/NO de cada pregunta:
- **A1 v4:** con umbral 0,5 da 31/46 con 15/51 falsas alarmas, más del doble que el JSON. Para bajar a ≤ 7 hay que
  subir el umbral a 0,995 o más, y se pierden estafas (25–26).
- **A1 tarea:** es al revés, muy conservadora. Con umbral simple, ni en 0,01 pasa de 25/46 (6 FA).

| A1 v4, SLM solo, umbral simple | 0,01 | 0,1 | 0,5 | 0,9 | 0,99 | 0,999 |
|---|---|---|---|---|---|---|
| estafas (de 46) | 33 | 32 | 31 | 27 | 25 | 21 |
| antes del pedido (de 36) | 15 | 13 | 12 | 8 | 6 | 4 |
| falsas alarmas (de 51) | 18 | 16 | 15 | 13 | 10 | 5 |

Una hipótesis, no probada: en el JSON el modelo escribe el `riesgo` antes de decidir `alerta_sugerida`, y con la
pregunta SÍ/NO decide sin ese paso. Según el criterio escrito en #143, que no mejore indica que el límite está en el
modelo y no en cómo se lee el puntaje.

## Aparte de la regla

- **Tito→SLM (informativo; no se usó para elegir ni como línea base):**
  - Con la compuerta simulada, el token llega a 26–29/46 con ≤ 7 FA. El mejor es A2 + Tito, dos seguidas, umbral
    0,07: 29/46, 7 antes, 7/51.
  - El JSON con Tito, en las mismas condiciones, da 28/46 (riesgo ≥ 0,4 o alerta). Es +1, dentro del ruido.
  - Tito baja las consultas al SLM hasta el aviso de unas 2.400 a unas 1.200 en los 150 casos (mediana: 5 por caso
    en lugar de 16–18).
  - **Nota del 2026-11-06:** la ventaja de la compuerta sale casi toda del punto ciego de Tito. Se probó con un Tito
    que además despierta en la primera mención o pedido marcados.
    - Con A2 v4 quedan +4 y +3 estafas sobre el SLM solo, que salen de dos llamadas médicas (`MEDICO-001` y
      `MEDICO-004`).
    - Con A1 v4 queda +1, y con `tarea`, 0.
    - Ver H08 en `docs/hallazgos/` y la tabla 2 del análisis `analisis/2026-11-06-tito-compuerta-sensible/`, que
      llegan a `laboratorio-main` con el [PR #150](https://github.com/Corchets/bitacora_tesis/pull/150).
- **α de la EMA (exploración):** ni 0,3 ni 0,7 le ganan a 0,5 por 3 o más estafas, ni en la corrida ni en la
  repetición. α no importa.
- **Manuales en el punto elegido:**
  - A1 v4 detecta 14/16 de laboratorio, 7/7 del piloto y 5/6 de trampa, con 3/7 falsas alarmas en trampa.
  - A2 v4 cae a 4/16 en laboratorio.
- **Latencia de la etapa 1** (ms del SLM por línea, p50 / p95):
  - v4 + rol: 72–74 / 87–92;
  - tarea + ab: 146–147 / 235–239.
  - La etapa 2 (motivo y evidencia) no se midió: #143 la pide después de elegir una política por token, y no se
    eligió ninguna.

## Propuesta para #51 y el ADR 0002

- No adoptar la lectura de P(SÍ): el detector sigue decidiendo con el JSON (`alerta_sugerida`), con el prompt que
  elija #51.
- No hace falta la corrida de la etapa 2 de #143.
- El resultado negativo se informa tal cual, con esta carpeta como respaldo.
