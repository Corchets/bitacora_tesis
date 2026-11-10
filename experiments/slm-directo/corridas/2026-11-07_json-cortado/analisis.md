# #143: JSON de v4 cortado después de `alerta_sugerida`, en los 150 de desarrollo

> **Estado: propuesta sin discutir.** Prueba de desarrollo; la reserva no se tocó. El criterio está en
> [`README.md`](README.md) y en [`analizar.py`](analizar.py), escritos antes de correr (`python -I analizar.py`). La
> salida completa está en [`analisis-salida.md`](analisis-salida.md). Las cifras de «Aparte» salen de
> [`diagnostico.py`](diagnostico.py), que se escribió después de ver los resultados y no cambia el criterio
> ([`diagnostico-salida.md`](diagnostico-salida.md)).

## Qué se corrió

- **Colab T4, el 2026-11-07 entre las 20:05 y las 20:48 UTC** (17:05 a 17:48 en Argentina; 43 minutos):
  1. la humo de formato en los 3 casos de siempre (48 líneas);
  2. `v4-corte` sobre los 150 en todas las líneas (`--seguir-tras-aviso`), en 14,7 minutos;
  3. el JSON completo de v4 en las mismas condiciones, en 22,7 minutos.
- **`v4-corte`** es el pedido de v4 JSON tal cual (misma huella, `92df75a2…`) con `num_predict` 24 y sin logprobs. En la
  primera línea de cada llamada en que dispara «riesgo ≥ 0,4 o alerta», una segunda consulta pide evidencia y motivo
  con `motivo_v4_corte.txt`.
- **Mismo setup que la línea base:** commit `decdff1` (tag `colab/143-json-cortado`), sha256 del script `24e52510…`,
  Ollama 0.40.14, digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, `--sin-reglas` y roles.
- **Los ZIP están verificados:**
  - cada uno se descomprimió en un directorio vacío, y los parciales coinciden byte a byte con el final;
  - `commit.txt`, `digest.txt`, los dos `TERMINADA.txt` y los tres manifiestos dan lo esperado, sin cambios sin
    commitear;
  - el texto de la segunda consulta es el de `motivo_v4_corte.txt`;
  - no hay casos de la reserva.
- **La humo pasa, y no se ajustó nada:**
  - con el JSON completo, el valor de `alerta_sugerida` termina en el token 23 en las 48 líneas;
  - `v4-corte` lee riesgo y alerta en las 48.

  El token 24 es la coma que sigue a la alerta, así que sobra un solo token. En los 150, las 2.773 líneas terminan en
  esa coma y ninguna es inválida.

## Resultado según el criterio

**Pasa: el corte no cambia la primera consulta.** Las cifras de detección de v4 JSON valen para `v4-corte`.

| líneas válidas en las dos | riesgo escrito igual | alerta escrita igual | inválidas del cortado | criterio |
|---|---|---|---|---|
| 2.773 | 2.591 (93,4 %) | 2.756 (99,4 %) | 0 | ≥ 93 % y ≤ 1 %: pasa |

- **Pasa justo:** 93,4 % contra un mínimo de 93 %, por debajo del ~96 % de dos corridas iguales en una sesión.
  - La diferencia está sobre todo en las líneas que siguen al aviso, que solo corren en modo diagnóstico.
  - Hasta el aviso, las dos corridas coinciden en el 95,0 %, cerca del 96,4 % de dos corridas iguales (ver «Aparte»).
- **La alerta escrita difiere en 17 líneas:** en 11 solo el cortado la escribe en true, y en 6 solo el completo.
- **Solo para mirar:**
  - la regla avisa en la misma línea en los 150 casos;
  - en corpus_v2, las dos corridas dan 29/46 estafas, 12/36 antes del pedido y 7/51 FA, y la línea base de otra
    sesión, 29/46, 11/36 y 7/51.

## Latencia (ms de pared en T4, p50 / p95)

| consulta, en las 2.773 líneas | ms | tokens escritos | lectura del prompt | escritura |
|---|---|---|---|---|
| primera consulta del cortado | 286 / 360 | 24 / 24 | 96 / 139 | 162 / 192 |
| JSON completo | 406 / 974 | 41 / 95 | 95 / 140 | 281 / 834 |

- **El cortado es más rápido en 2.772 de las 2.773 líneas**, y la mediana del cociente completo / cortado es 1,41. Se
  estimaban 270–320 ms.
- **Antes del aviso, que es lo que corre en modo operativo:**
  - 288 / 362 ms contra 393 / 482 ms: 105 ms menos por línea (−27 %);
  - es más o menos lo que cuestan los 17 tokens que no se escriben, a ~6,9 ms cada uno.

  El p95 del completo en la tabla incluye las líneas que siguen al aviso, donde escribe motivo y evidencia.
- **Segunda consulta, en las 78 líneas de aviso:** 661 / 811 ms, con 56 / 73 tokens escritos.
  - 4 vuelven sin motivo (`etapa2_alerta_sin_motivo`): el aviso se mantiene, pero sin texto.
  - La evidencia aparece textual en 73 de las 78.
- **Total en la línea de aviso:** 938 / 1.121 ms.
  - Contra 783 / 1.032 ms del completo en esas mismas líneas.
  - Contra 905 / 1.212 ms en las 431 líneas en que el completo escribe la alerta en true (la referencia de 911 ms).

## Aparte, fuera del criterio

Las cifras salen de `diagnostico.py`.

- **La decisión de avisar se conoce antes.**
  - La primera consulta la da a los 269 / 336 ms.
  - El JSON completo, sin streaming, la da recién con todo el texto: 832 / 1.079 ms cuando la alerta viene en true.
  - Si la app espera el motivo para avisar, la línea del aviso con la alerta en true tarda 962 ms, unos 130 ms más que
    el completo en esas líneas.
  - Si avisa con la primera consulta y agrega el motivo cuando llega, el aviso sale a los ~270 ms.
- **El cortado da motivo en más avisos: 74 de 78, contra 59 de 78 del completo.**
  - 19 avisos disparan solo por riesgo ≥ 0,4, con la alerta en false. Ahí el JSON completo deja motivo y evidencia
    vacíos, y la segunda consulta los completa en 15.
  - Los 4 fallos son de ese grupo:
    - después de leer su propia alerta en false, el modelo devuelve los campos vacíos, y una vez escribe en la
      evidencia que no hay pedido;
    - son 2 estafas (`CV2-D-V-BANCO-007` y `SC-ORG-BENEFICIO-01-e01`) y 2 legítimas (`CV2-D-L-BANCO-006` y `TR-06`).
  - La evidencia que no aparece textual (`CV2-D-V-ORGANISMO_PREVISIONAL-003`) junta dos frases de la transcripción.
- **El ruido se concentra después del aviso.**

  | riesgo escrito igual | hasta el aviso | después del aviso |
  |---|---|---|
  | v4-corte / v4 completo, misma sesión | 95,0 % | 88,3 % |
  | v4-L / su repetición, misma sesión (etapa 1) | 96,4 % | 96,2 % |
  | v4-L / v4-corte, sesiones distintas | 94,5 % | 86,1 % |
  | v4-L / v4 completo, sesiones distintas | 94,3 % | 85,3 % |

  - Hasta el aviso, el cortado y el completo coinciden como dos corridas iguales.
  - Después del aviso, las dos corridas de hoy se separan entre sí y de las de la etapa 1, y las de la etapa 1 entre sí
    no.
    - Las de hoy generan más en esa zona: el completo escribe motivo y evidencia, y el cortado hace la segunda consulta.
    - Una explicación posible es que esa generación de más deja la caché de Ollama de otra forma y cambia el decimal en
      las líneas que siguen. No se verificó.
  - No cambia la primera línea de aviso, que es lo que usa el detector.
  - Las cifras que miran después del primer aviso dependen de lo que se generó antes, no solo del prompt.
  - Las diferencias van para los dos lados (el cortado escribe más riesgo en 103 líneas y menos en 79), y 25 cruzan
    0,4, todas después de la línea del aviso.

## Para seguir (propuesta; lo decide el equipo)

- **`v4-corte` queda como la forma de correr v4 JSON**, como decidió el equipo: la misma detección y 105 ms menos por
  línea en T4.
- **En la app:**
  - avisar con la primera consulta y agregar el motivo cuando llegue;
  - usar un texto fijo para los avisos que vuelven sin motivo: 4 de 78 acá, contra 19 de 78 con el JSON completo.
- **Teléfono (#141):** medir las dos consultas. En el teléfono puede cambiar cuánto pesan la lectura del prompt y la
  escritura, así que conviene registrar el desglose de la segunda consulta, que este CSV no guarda.
- **No achicar `num_predict` a 23:** ahorraría ~7 ms por línea y dejaría el corte sin margen.
