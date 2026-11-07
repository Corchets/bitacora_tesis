# #143: JSON de v4 cortado después de `alerta_sugerida`

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre. Se preparó el 2026-11-07 y todavía no se
> corrió. El criterio de abajo se escribió antes de correr. El Colab está en
> [`colab/README-PUNTAJE-TOKEN.md` §4](../../colab/README-PUNTAJE-TOKEN.md#4-json-de-v4-cortado-después-de-la-alerta-tag-colab143-json-cortado).

## Qué se mide

**Decisión de Mateo (2026-11-07):** el detector sigue con el JSON de v4 y «riesgo ≥ 0,4 o alerta». Para bajar la
latencia, el JSON se corta después de `alerta_sugerida`, y motivo y evidencia se piden en una segunda consulta, solo
al avisar. Esta corrida no elige nada; mide esa latencia y comprueba que el corte no cambia lo que escribe el modelo.

- **Primera consulta (`v4-corte`):** el pedido de v4 JSON con `num_predict` 24, sin logprobs. Riesgo y alerta salen
  del texto cortado.
- **Segunda consulta:** solo en la primera línea de la llamada en que dispara la regla. Usa `riesgo_motivo.txt` y
  `ESQUEMA_MOTIVO`, después de lo que escribió el modelo.
- **Comparación:** el JSON completo de v4 en la misma sesión, sobre las mismas 2.773 líneas.

Referencias de T4 de otras sesiones:
- v4 JSON entero, 432 / 546 ms (p50 / p95);
- en sus líneas con alerta, que escriben motivo y evidencia, 911 / 1.088 ms;
- v4-L, cortado a 12 tokens, 237 / 327 ms.

La estimación para la primera consulta es de unos 270–320 ms (p50).

## Criterio, escrito antes de correr

**Coincidencia esperada entre el cortado y el completo.**
- La primera consulta es el mismo pedido que v4 JSON, salvo `num_predict`. Con temperatura 0 y seed 42, cortar no
  cambia los tokens anteriores al corte. Lo que separa las dos corridas es el ruido de la GPU: dos corridas iguales en
  una sesión coinciden ~96 % en el riesgo escrito.
- **Se espera el riesgo escrito igual en al menos el 93 % de las líneas válidas en las dos**, es decir, el 96 % con 3
  puntos de margen.
- La alerta escrita se informa igual (tabla de 2×2 y las líneas que difieren), sin umbral propio: casi todas las
  líneas dicen false, así que su porcentaje no informa.
- **Las líneas inválidas del cortado tienen que ser como mucho el 1 %.** Una línea inválida es casi siempre un corte
  antes del valor de la alerta. Más que eso quiere decir que `num_predict` no alcanza.
- Si se cumplen las dos condiciones, el corte no cambia la primera consulta, y las cifras de detección de v4 JSON
  valen para el cortado. Si no, se le avisa a Mateo antes de usar la latencia.
- **Solo para mirar:**
  - en cuántos de los 150 casos la regla avisa en la misma línea;
  - estafas, avisos antes del pedido y falsas alarmas en corpus_v2 con las dos corridas, junto a la línea base
    (29/46, 11/36 y 7/51, de otra sesión).

  Muestran el ruido; no reabren la decisión.

**Cómo se informa la latencia.** Son ms de pared del cliente en T4, p50 / p95 por rango más cercano, en las líneas
válidas en las dos corridas.
1. **Primera consulta:**
   - `ms_etapa1` del cortado contra `ms` del completo, en las mismas líneas;
   - con los tokens escritos y la lectura del prompt y la escritura según Ollama (p50 / p95);
   - en cuántas líneas el cortado es más rápido, y la mediana del cociente completo / cortado, línea a línea.
2. **Segunda consulta:**
   - `ms_etapa2` en las líneas de aviso, una por llamada que avisa;
   - sus tokens escritos y `prompt_eval_count`;
   - los fallos (`etapa2_*`) y cuántas evidencias aparecen en el texto.
3. **Total en la línea de aviso:**
   - `ms` del cortado, la primera consulta más la segunda;
   - al lado, el completo en esas mismas líneas, y el completo en sus líneas con alerta escrita (la referencia de
     911 ms).

No se suma por llamada: el costo de una llamada sin aviso es el de la primera consulta por línea.

## Archivos

| Archivo | Qué es |
|---|---|
| [`analizar.py`](analizar.py) | El criterio de arriba en código, escrito antes de correr: `python -I analizar.py` desde esta carpeta, con los ZIP descomprimidos acá (`humo/`, `v4-corte/` y `v4/`). |
