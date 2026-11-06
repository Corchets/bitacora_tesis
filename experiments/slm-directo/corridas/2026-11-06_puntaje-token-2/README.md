# #143, segunda vuelta: lectura del token y prompt C

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre. Preparada el 2026-11-06; el Colab todavía no
> se corrió.

| Archivo | Qué es |
|---|---|
| [`analizar.py`](analizar.py) | Análisis y regla de elección, escritos antes de correr (las decisiones están en el docstring). |
| [`FUENTES.md`](FUENTES.md) | Bibliografía de esta vuelta: estafas reales en Argentina, detectores, lectura de tokens, prompts y sobreajuste. |
| [`IDEAS-PENDIENTES.md`](IDEAS-PENDIENTES.md) | Lo que no se prueba antes del ADR 0002: legítimas entrantes, preguntas cortas, sondeo activo, ajuste fino y más. |
| [`NOTA-GEMMA4-Y-CACHE.md`](NOTA-GEMMA4-Y-CACHE.md) | Cómo usa Gemma 4 los turnos y cómo se reutiliza el prefijo, para la defensa. |
| [`BORRADOR-COMENTARIO-143.md`](BORRADOR-COMENTARIO-143.md) | Comentario para #143 que deja escrita la regla antes de correr. Se publica con el OK de Mateo. |

**Dos etapas.**
- **Etapa 1 (lista para correr):** v4-L, el JSON de v4 tal cual leyendo el primer decimal del riesgo, contra v4 JSON
  sobre los 150 casos.
- **Etapa 2 (cuando estén las legítimas entrantes que genera Evaristo):** el prompt C con el alcance, en JSON, SÍ/NO y
  dígito, y `v4-premisa`. Se decide dentro del alcance: las 46 estafas de corpus_v2 más las legítimas nuevas.

**Dónde está cada cosa:**
- los textos, en [`prompts/README.md`](../../prompts/README.md);
- el Colab, en [`colab/README-PUNTAJE-TOKEN.md`](../../colab/README-PUNTAJE-TOKEN.md);
- el alcance anotado, en [`casos/alcance-desarrollo.json`](../../casos/alcance-desarrollo.json);
- los controles, en [`casos/controles-ventas.json`](../../casos/controles-ventas.json).

Cuando lleguen los ZIP de Colab, se descomprimen acá (una carpeta por corrida) y se corre `python -I analizar.py`.
