# #143, segunda vuelta: lectura del token y prompt C

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre. Se preparó el 2026-11-06. La etapa 1 se corrió
> en Colab el 2026-11-06 y se analizó el 2026-11-07 ([`analisis.md`](analisis.md)). La etapa 2 espera las legítimas
> entrantes nuevas.

| Archivo | Qué es |
|---|---|
| [`analizar.py`](analizar.py) | Análisis y regla de elección, escritos antes de correr (las decisiones están en el docstring). |
| [`analisis.md`](analisis.md) | Resultado de la etapa 1: el veredicto según la regla, la latencia y lo que es solo para mirar. |
| [`analisis-salida.md`](analisis-salida.md), [`curva.csv`](curva.csv) | Salida completa de `python -I analizar.py` y la curva de la vista principal. |
| [`diagnostico.py`](diagnostico.py), [`diagnostico-salida.md`](diagnostico-salida.md) | Diagnóstico fuera de la regla, escrito después de ver los resultados: latencia en las mismas líneas y de dónde sale la diferencia con la base. |
| `humo/`, `v4-lectura/`, `v4-lectura-rep/`, `controles-ventas/` | Corridas de Colab, una carpeta por corrida, tal como bajaron. |
| `commit.txt`, `script-sha256.txt`, `ollama-version.txt`, `pip-freeze.txt`, `gpu.txt` | Registro de la corrida. |
| [`FUENTES.md`](FUENTES.md) | Bibliografía de esta vuelta: estafas reales en Argentina, detectores, lectura de tokens, prompts y sobreajuste. |
| [`IDEAS-PENDIENTES.md`](IDEAS-PENDIENTES.md) | Lo que no se prueba antes del ADR 0002: legítimas entrantes, preguntas cortas, sondeo activo, ajuste fino y más. |
| [`NOTA-GEMMA4-Y-CACHE.md`](NOTA-GEMMA4-Y-CACHE.md) | Cómo usa Gemma 4 los turnos y cómo se reutiliza el prefijo, para la defensa. |
| [`BORRADOR-COMENTARIO-143.md`](BORRADOR-COMENTARIO-143.md) | Comentario para #143 con la regla escrita antes de correr y el resultado de la etapa 1. Se publica con el OK de Mateo. |

**Dos etapas.**
- **Etapa 1 (corrida y analizada):** v4-L, el JSON de v4 tal cual leyendo el primer decimal del riesgo, contra v4 JSON
  sobre los 150 casos.
  - v4-L detecta 2 estafas menos (27/46 contra 29/46, con 7/51 FA), dentro de ±2, así que decide la latencia.
  - Por línea, v4-L es 1,8 veces más rápida en T4.
  - La ganancia sale de cortar el JSON, no de leer el token. Ver [`analisis.md`](analisis.md).
  - **Decisión del equipo (2026-11-07):** se queda el JSON de v4 con «riesgo ≥ 0,4 o alerta», cortado después de
    `alerta_sugerida`, con motivo y evidencia en una segunda consulta solo al avisar. Falta medir esa latencia en Colab.
- **Etapa 2 (cuando estén las legítimas entrantes que genera Evaristo):** el prompt C con el alcance, en JSON, SÍ/NO y
  dígito, y `v4-premisa`. Se decide dentro del alcance: las 46 estafas de corpus_v2 más las legítimas nuevas.

**Dónde está cada cosa:**
- los textos, en [`prompts/README.md`](../../prompts/README.md);
- el Colab, en [`colab/README-PUNTAJE-TOKEN.md`](../../colab/README-PUNTAJE-TOKEN.md);
- el alcance anotado, en [`casos/alcance-desarrollo.json`](../../casos/alcance-desarrollo.json);
- los controles, en [`casos/controles-ventas.json`](../../casos/controles-ventas.json).

## Humo de formato de la etapa 1

Se corrió en Colab T4 el 2026-11-06 a las 23:21 UTC, con el commit `b9fd09a`, sobre los 3 casos de la humo 2 (48
líneas).

**Criterio, fijado antes de correr:**
- masa ≥ 0,9 en al menos 44 de 48 líneas;
- con 3 tokens, una respuesta limpia en al menos 44 de 48: SÍ/NO, o un solo dígito;
- en v4-L, en cambio, que se encuentre el decimal del riesgo.

**Pasan las tres variantes, así que no se ajustó ninguna pregunta final.**

| prompt | masa ≥ 0,9 | masa mínima / mediana | respuesta limpia | resultado |
|---|---|---|---|---|
| `v4-lectura` | 48/48 | 1,0000 / 1,0000 | 48/48 | PASA |
| `c-sino` | 48/48 | 1,0000 / 1,0000 | 48/48 | PASA |
| `c-digito` | 48/48 | 0,9997 / 1,0000 | 48/48 | PASA |

- De `c-sino` y `c-digito` solo se miró el formato.
- La humo vale para `prompts/tarea_c.txt` tal como está en `b9fd09a`: si C cambia antes de la etapa 2, se repite.
- El detalle está en [`humo/humo.md`](humo/humo.md).

**Verificación de los ZIP (2026-11-07):**
- cada ZIP se descomprimió en un directorio vacío;
- `commit.txt` y los cuatro manifiestos dan `b9fd09a`;
- el sha256 de `probar_puntaje_token_2.py` coincide con el del tag (`ab47d073…`);
- el digest del modelo coincide con el de las líneas base (`b37049369adf…`);
- los parciales coinciden byte a byte con el ZIP final.
