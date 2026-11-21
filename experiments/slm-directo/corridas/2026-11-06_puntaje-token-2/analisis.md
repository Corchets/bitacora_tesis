# #143, segunda vuelta, etapa 1: v4-L en los 150 de desarrollo

> **Estado: propuesta sin discutir.** Prueba de desarrollo; la reserva no se tocó. La regla está en
> [`analizar.py`](analizar.py), escrito antes de correr (`python -I analizar.py`). La salida completa está en
> [`analisis-salida.md`](analisis-salida.md) y la curva, en [`curva.csv`](curva.csv). Las cifras de «Por qué» y la
> latencia en las mismas líneas salen de [`diagnostico.py`](diagnostico.py), que se escribió después de ver los
> resultados y no cambia la regla ([`diagnostico-salida.md`](diagnostico-salida.md)). **Decisión del equipo
> (2026-11-07):** se queda el JSON de v4 con «riesgo ≥ 0,4 o alerta», cortado después de `alerta_sugerida`.

## Qué se corrió

- **Colab T4, el 2026-11-06 entre las 23:21 y las 23:50 UTC** (20:21 a 20:50 en Argentina; 29 minutos):
  - la humo de formato de `v4-lectura`, `c-sino` y `c-digito`;
  - v4-L sobre los 150 en todas las líneas (`--seguir-tras-aviso`), y su repetición;
  - los 6 controles de ventas, con v4 JSON y v4-L.
- **v4-L** es el JSON de v4 tal cual: el mismo prompt (misma huella, `92df75a2…`), el mismo mensaje y el mismo esquema.
  Se corta a los 12 tokens, justo después del primer decimal del riesgo, y el puntaje es el riesgo esperado según la
  distribución de ese dígito.
- **Mismo setup que la línea base:** commit `b9fd09a` (tag `colab/143-ronda-2`), sha256 del script `ab47d073…`, Ollama
  0.40.14, digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, `--sin-reglas` y roles. Los ZIP parciales
  coinciden byte a byte con el final.
- **La humo de formato pasa en las tres variantes**, con el criterio fijado antes de correr (44 de 48 líneas). No se
  ajustó nada. De `c-sino` y `c-digito` solo se miró el formato.

  | prompt | masa ≥ 0,9 | masa mínima | respuesta limpia |
  |---|---|---|---|
  | `v4-lectura` | 48/48 | 1,0000 | 48/48 |
  | `c-sino` | 48/48 | 1,0000 | 48/48 |
  | `c-digito` | 48/48 | 0,9997 | 48/48 |

- **La lectura es limpia:**
  - 2.773 líneas por corrida;
  - ninguna inválida en v4-L y 2 en la repetición: dos legítimas en que el modelo escribió `"riesgo": 0`, sin
    decimal.
- **Las líneas base se reproducen exactas.** v4-L escribe el mismo riesgo que la base v4 en el 91,4 % de las líneas
  comparables (2.034 de 2.225). Dos corridas JSON de v4 en sesiones distintas de Colab coinciden lo mismo (91,3 %), así
  que el pedido es el mismo.

## Resultado según la regla de #143

Se elige sobre el SLM solo, con FA ≤ 7/51 en corpus_v2 y las mismas políticas y grilla que en la primera vuelta.

| corpus_v2, FA ≤ 7/51 | punto | estafas (de 46) | antes del pedido (de 36) | FA (de 51) | repetición, mismo punto |
|---|---|---|---|---|---|
| **v4-L** (token) | umbral 0,4 sobre el riesgo esperado | 27 | 11 | 7 | 27 / 11 / 8 |
| línea base v4 JSON | riesgo ≥ 0,4 o alerta | 29 | 11 | 7 | — |

- **Detección: −2, dentro de ±2, así que decide la latencia.**
  - La repetición queda en el mismo −2, así que v4-L cuenta.
  - En la repetición hay 8 FA en vez de 7: el riesgo esperado de `CV2-D-L-BANCO-003` da 0,402 en vez de 0,374.
- **Latencia de la etapa 1** (ms del SLM por línea en T4, en las mismas 2.225 líneas):

  | | ms, p50 / p95 | tokens escritos | lectura del prompt, p50 | escritura, p50 |
  |---|---|---|---|---|
  | v4-L | 237 / 327 | 12 | 96 ms | 119 ms |
  | v4 JSON | 432 / 546 | 41 | 106 ms | 300 ms |

  v4-L es 1,8 veces más rápida, y lo es en 2.216 de las 2.225 líneas. La lectura y la escritura son medianas de cada
  corrida.
- **Adopción, según la regla: sí, por latencia.** El equipo decidió otra cosa: se queda el JSON de v4, cortado
  después de `alerta_sugerida` (ver «Decisión del equipo», al final).
- **Falta medir:**
  - **La consulta de motivo y evidencia** (la etapa 2 de #143), que v4-L tiene que hacer aparte cuando avisa. #143 la
    mide en una corrida chica sobre las líneas de aviso. Como cota, el JSON entero de v4 tardó 911 / 1.088 ms
    (p50 / p95) en las líneas de aviso de la base.
  - **El teléfono** (#141). v4-L achica la escritura. Sin caché del prefijo, la lectura del prompt pesaría más y la
    diferencia sería menor.

## Por qué: la ganancia es el corte, no la lectura

Fuera de la regla; las cifras salen de `diagnostico.py`.

- **v4-L corta el JSON antes de `alerta_sugerida`.** Sin ese campo, la base da exactamente lo mismo que v4-L: «riesgo ≥
  0,4» solo da 27/46, 11 antes y 7/51.
  - Las 2 estafas de más de la base salen de `alerta_sugerida`: `CV2-D-V-PREMIO-002` (riesgo escrito 0,3) y
    `CV2-D-V-WHATSAPP-003` (0,2).
  - Además hay ruido entre corridas, que se compensa:
    - en `CV2-D-V-ORGANISMO_PREVISIONAL-004`, la base escribió 0,4 y v4-L 0,3 (esperado 0,374);
    - en `CV2-D-V-WHATSAPP-004`, con 0,3 escrito, el esperado de v4-L llega a 0,401.
- **Con el mismo corte, el riesgo escrito da casi lo mismo.** En la misma corrida, «riesgo escrito ≥ 0,4» da 26/46, 11
  antes y 7/51: una estafa menos que el esperado, con la misma latencia, porque son los mismos 12 tokens.
  - La latencia favorece cortar el JSON, no leer el token.
  - La pregunta de #143, si leer la distribución le gana al número escrito, da empate: +1.
- **Esta vez el puntaje sí sale continuo:**
  - el dígito más probable tiene P ≥ 0,99 en el 10 % de las líneas, y menos de 0,9 en el 70 %;
  - en la primera vuelta, entre el 90 y el 94 % de las líneas tenía P(SÍ) ≤ 0,01 o ≥ 0,99.
- **Pero con FA ≤ 7 no aparece un punto mejor:** entre 0,30 y 0,40, las estafas y las legítimas se mezclan.

  | v4-L, umbral simple | 0,25 | 0,3 | 0,35 | 0,38 | 0,4 | 0,45 | 0,5 |
  |---|---|---|---|---|---|---|---|
  | estafas (de 46) | 41 | 37 | 30 | 27 | 27 | 25 | 24 |
  | antes del pedido (de 36) | 23 | 20 | 14 | 12 | 11 | 9 | 7 |
  | falsas alarmas (de 51) | 22 | 15 | 11 | 8 | 7 | 6 | 5 |

  Según el criterio de #143, que no mejore indica que el límite está en el modelo y el prompt, no en cómo se lee el
  puntaje. Es lo mismo que en la primera vuelta, ahora con una lectura justa.

## Aparte, solo para mirar

- **Dentro del alcance** (las 46 estafas de corpus_v2 y sus 7 legítimas entrantes, con FA ≤ 1). No sirve para decidir.
  - La base es «riesgo ≥ 0,3 o alerta»: 41/46, 23 antes del pedido y 1/7 FA.
  - v4-L, con dos seguidas y umbral 0,11, da 46/46, 33 antes y 1/7, y la repetición da lo mismo.
  - Avisa las 10 estafas sin pedido, contra 8 de la base. En la vista principal, las dos avisan 1 de 10.
  - Ese umbral sale de 7 legítimas fáciles, de familiares y compañeros, y sobre las 51 legítimas de corpus_v2 avisaría
    en 36. Es una pista para la etapa 2 de esta vuelta, no un resultado: la prueba son las legítimas entrantes nuevas.
- **Las 6 estafas que piden un dato de identificación:** v4-L avisa 4 y la base, 5.
  - Ninguna de las dos se anticipa: avisan en la línea del pedido o después.
  - La que pierde v4-L, `ORGANISMO_PREVISIONAL-004`, es la del ruido de arriba.
  - `PREMIO-003` no la avisa ninguna.
- **Las 6 legítimas en que v4 avisaba por datos** (BANCO-001, 002, 004, 005 y 010, y TR-13) quedan fuera del alcance.
  Sin esa máscara, v4-L también avisa en las 6, en la misma línea o una después.
- **Controles de ventas y préstamos:** v4 JSON y v4-L avisan en los 6, en la misma línea.
  - Detectan las 3 estafas.
  - También avisan en las 3 legítimas: la venta de portabilidad (L4), el banco que ofrece un préstamo (L4) y la persona
    que pide un préstamo (L3).
  - Las dos primeras están dentro del alcance. Es justo lo que tiene que medir la etapa 2 de esta vuelta con las
    legítimas nuevas.
- **Manuales en el punto elegido:** sin diferencias. Las dos dan 16/16 en laboratorio, 7/7 en el piloto y 5/6 en trampa,
  con 6/10, 3/7 y 5/7 FA.
- **α de la EMA (exploración):**
  - α = 0,3 da 28/46 en la corrida y 25/46 en la repetición, contra 27/46 y 26/46 de α = 0,5;
  - α = 0,7 da 27/46 y 26/46.

  Ninguno le gana por 3: α no importa.
- **Tito→SLM** da 30–31/46 con 7/51, pero no se interpreta: Tito salió de la configuración principal (#51) y su ventaja
  sale del punto ciego (H08).

## Decisión del equipo (2026-11-07)

Mateo, por el equipo, se aparta del veredicto literal de la regla.

- **Se queda el JSON de v4 con «riesgo ≥ 0,4 o alerta»** (29/46, 11 antes del pedido, 7/51 FA), en lugar de v4-L
  (27/46).
  - La regla favorecía a v4-L por latencia, pero la ganancia venía de cortar el JSON, no de leer el token.
  - v4-L perdía las 2 estafas que aporta `alerta_sugerida`.
  - La regla se escribió para un SÍ/NO de un token, donde leer el token y cortar la respuesta eran lo mismo.
- **Para bajar la latencia, el JSON se corta después de `alerta_sugerida`:** riesgo y alerta, unos 20 tokens en vez de
  41.
  - En la línea base, 2.152 de las 2.225 líneas escriben 41 tokens con `"motivo": ""` y `"evidencia": ""`: el corte se
    ahorra eso.
  - Con el mismo prompt, el mismo esquema y temperatura 0, el riesgo y la alerta salen del mismo cálculo que en el JSON
    completo. La detección no cambia más que por el ruido entre corridas: el riesgo escrito coincide en el 96 % de las
    líneas entre dos corridas de la misma sesión y en el 91 % entre sesiones. No hay detección que validar con otros
    casos, solo latencia que medir.
  - `motivo` y `evidencia` se piden en una segunda consulta, solo al avisar. No puede repetir el JSON completo: si avisa
    por riesgo ≥ 0,4 con `alerta_sugerida` en false, el JSON trae motivo y evidencia vacíos. Se reusa el pedido de
    `riesgo_motivo.txt`.
  - Interpolando entre v4-L y el JSON entero, se estiman 270 a 320 ms por línea, contra 432. Falta medir las dos
    consultas en Colab y después en el teléfono (#141).
- **La lectura del token queda como propuesta a futuro.**
  - Hipótesis: un modelo instruido y sin ajuste fino da probabilidades poco calibradas, que separan mal las estafas de
    las legítimas (en v4-L se mezclan entre 0,30 y 0,40), y el JSON aprovecha que el modelo escribe el riesgo antes de
    decidir la alerta.
  - Respaldo: en Open-Jev (arXiv 2609.23959, ver [`FUENTES.md`](FUENTES.md)), leer el token dio un AUROC de 0,69 sin
    ajustar y ~0,97 con LoRA. En el modelo ajustado, leer la probabilidad dentro del JSON (0,95) le ganó a la etiqueta
    escrita (0,875).
  - Con LoRA, el token vuelve a ser una opción (sondeo en [`IDEAS-PENDIENTES.md`](IDEAS-PENDIENTES.md) §3).
- **Idea sin probar: reducir el JSON a solo la alerta.** Sin el riesgo cambia el prompt, y en desarrollo la alerta sola
  dio 28/46 con 9 antes y 6/51 FA, contra 29/46 con 11 antes y 7/51.
- **La etapa 2 de esta vuelta** sigue con las legítimas nuevas. Qué configuraciones quedan se decide antes de armar su
  Colab.
