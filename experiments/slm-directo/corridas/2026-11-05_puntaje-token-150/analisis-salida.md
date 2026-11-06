# #143: puntaje por P(SÍ) — análisis offline

## Líneas base JSON

Primer aviso (`alerta_sugerida`), como corrieron. Tiene que reproducir la tabla de referencia de #143.

| corpus_v2 | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|
| v1 solo (2026-11-04, a) | 28/46 | 13/11/3 (de 36) | 0 / 2.4 / 9 | 4/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 2 |
| v1 + Tito sin indicio (2026-11-04, b) | 27/46 | 12/10/4 (de 36) | 0 / 2.1 / 8 | 4/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 2 |
| v1 solo, repetición (2026-11-04, c) | 27/46 | 12/11/3 (de 36) | 0 / 2.3 / 8 | 4/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 2 |
| v4 solo (2026-11-05, b) | 28/46 | 9/16/2 (de 36) | 0 / 1.9 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |
| v4 + Tito sin indicio (tanda de roles, d) | 27/46 | 7/17/2 (de 36) | 0 / 1.3 / 5 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |

La tabla de referencia se reproduce: v1 solo 28/13/4, v1 + Tito 27/12/4, v4 solo 28/9/6.

Umbral sobre el riesgo escrito: avisa en la primera línea con riesgo ≥ u o `alerta_sugerida`. Las corridas operativas cortan en el aviso, así que esta regla está observada entera.

| corpus_v2 | riesgo | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|
| v1 solo (2026-11-04, a) | ≥ 0.3 | 42/46 | 25/6/2 (de 36) | 5 / 7.1 / 19 | 21/51 | cotidiana 4, mencion_sin_pedido 7, pedido_razonable 10 |
| v1 solo (2026-11-04, a) | ≥ 0.4 | 30/46 | 14/11/4 (de 36) | 0 / 2.6 / 11 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v1 solo (2026-11-04, a) | ≥ 0.5 | 30/46 | 14/11/4 (de 36) | 0 / 2.6 / 11 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v1 + Tito sin indicio (2026-11-04, b) | ≥ 0.3 | 41/46 | 23/7/2 (de 36) | 2 / 4.4 / 15 | 16/51 | cotidiana 3, mencion_sin_pedido 5, pedido_razonable 8 |
| v1 + Tito sin indicio (2026-11-04, b) | ≥ 0.4 | 28/46 | 13/9/5 (de 36) | 0 / 2.3 / 10 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| v1 + Tito sin indicio (2026-11-04, b) | ≥ 0.5 | 28/46 | 13/9/5 (de 36) | 0 / 2.2 / 10 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| v1 solo, repetición (2026-11-04, c) | ≥ 0.3 | 42/46 | 25/6/2 (de 36) | 5 / 7.1 / 19 | 21/51 | cotidiana 3, mencion_sin_pedido 7, pedido_razonable 11 |
| v1 solo, repetición (2026-11-04, c) | ≥ 0.4 | 30/46 | 13/11/5 (de 36) | 0 / 2.3 / 10 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v1 solo, repetición (2026-11-04, c) | ≥ 0.5 | 30/46 | 13/11/5 (de 36) | 0 / 2.3 / 10 | 7/51 | cotidiana 1, mencion_sin_pedido 3, pedido_razonable 3 |
| v4 solo (2026-11-05, b) | ≥ 0.3 | 41/46 | 23/8/2 (de 36) | 8 / 7.2 / 19 | 21/51 | cotidiana 8, mencion_sin_pedido 3, pedido_razonable 10 |
| v4 solo (2026-11-05, b) | ≥ 0.4 | 29/46 | 11/15/2 (de 36) | 0 / 2.9 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4 solo (2026-11-05, b) | ≥ 0.5 | 28/46 | 11/14/2 (de 36) | 0 / 2.5 / 9 | 7/51 | mencion_sin_pedido 3, pedido_razonable 4 |
| v4 + Tito sin indicio (tanda de roles, d) | ≥ 0.3 | 38/46 | 20/8/3 (de 36) | 2 / 4.3 / 14 | 14/51 | cotidiana 5, mencion_sin_pedido 2, pedido_razonable 7 |
| v4 + Tito sin indicio (tanda de roles, d) | ≥ 0.4 | 28/46 | 8/17/2 (de 36) | 0 / 1.8 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |
| v4 + Tito sin indicio (tanda de roles, d) | ≥ 0.5 | 27/46 | 8/16/2 (de 36) | 0 / 1.7 / 7 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |

Línea base de la regla de adopción: mejor punto JSON del SLM solo con falsas alarmas ≤ 7/51 en corpus_v2, por prompt. Como dato, también `alerta_sugerida` sola:

- v1: v1 solo (2026-11-04, a), riesgo ≥ 0.4 o alerta: 30/46 estafas, 14 antes del pedido, 7/51 FA (`alerta_sugerida` sola: 28/46, 13 antes, 4/51).
- v4: v4 solo (2026-11-05, b), riesgo ≥ 0.4 o alerta: 29/46 estafas, 11 antes del pedido, 7/51 FA (`alerta_sugerida` sola: 28/46, 9 antes, 6/51).

Activaciones de Tito viejo sin indicio: 128 de 150 casos (iguales con v1 y v4); Tito por línea antes de activar: mediana 111 ms.

## Corridas nuevas: P(SÍ) del primer token

Control de la lectura (criterio de la humo: masa SÍ+NO ≥ 0,9 en casi todas las líneas):

| corrida | líneas | inválidas | masa mínima | líneas con masa < 0,9 | ms SLM p50 / p95 |
|---|---|---|---|---|---|
| A1 v4 | 2773 | 0 | 0.9997 | 0 | 74 / 92 |
| A1 v4, repetición | 2773 | 0 | 0.9992 | 0 | 73 / 89 |
| A2 v4 | 2773 | 0 | 1.0000 | 0 | 72 / 87 |
| A2 v4, repetición | 2773 | 0 | 1.0000 | 0 | 74 / 90 |
| A1 tarea | 2773 | 0 | 1.0000 | 0 | 147 / 239 |
| A1 tarea, repetición | 2773 | 0 | 1.0000 | 0 | 146 / 235 |

Curva completa en `curva.csv` (6540 filas: corrida × compuerta × política × umbral).

### Mejor punto por política con FA ≤ 7/51 en corpus_v2

| corrida | compuerta | política | papel | umbral (rango empatado) | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|---|---|---|
| A1 v4 | SLM solo | umbral | regla | 0.995 (0.995–0.995) | 25/46 | 5/16/4 (de 36) | 0 / 0.4 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4 | SLM solo | dos seguidas | regla | 0.95 (0.93–0.97) | 25/46 | 4/3/18 (de 36) | -1 / -0.3 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4 | SLM solo | EMA α=0.5 | regla | 0.72 (0.71–0.73) | 26/46 | 4/3/19 (de 36) | -1 / -0.3 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4 | SLM solo | EMA α=0.3 | exploración | 0.5 (0.49–0.5) | 26/46 | 4/3/19 (de 36) | -1 / -0.3 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4 | SLM solo | EMA α=0.7 | exploración | 0.86 (0.86–0.86) | 26/46 | 4/3/19 (de 36) | -1 / -0.3 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4 | Tito→SLM | umbral | informativo | 0.96 (0.95–0.97) | 26/46 | 8/15/3 (de 36) | 0 / 0.8 / 4 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4 | Tito→SLM | dos seguidas | informativo | 0.07 (0.02–0.11) | 26/46 | 6/3/17 (de 36) | -1 / -0.1 / 3 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A1 v4 | Tito→SLM | EMA α=0.5 | informativo | 0.5 (0.5–0.5) | 25/46 | 7/10/8 (de 36) | 0 / 0.2 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A1 v4 | Tito→SLM | EMA α=0.3 | informativo | 0.3 (0.3–0.3) | 26/46 | 8/9/9 (de 36) | 0 / 0.2 / 3 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A1 v4 | Tito→SLM | EMA α=0.7 | informativo | 0.68 (0.68–0.68) | 26/46 | 8/14/4 (de 36) | 0 / 0.7 / 4 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4, repetición | SLM solo | umbral | regla | 0.995 (0.995–0.995) | 24/46 | 4/18/2 (de 36) | 0 / 0.5 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4, repetición | SLM solo | dos seguidas | regla | 0.92 (0.92–0.92) | 25/46 | 4/3/18 (de 36) | -1 / -0.3 / 2 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4, repetición | SLM solo | EMA α=0.5 | regla | 0.73 (0.72–0.73) | 26/46 | 4/3/19 (de 36) | -1 / -0.5 / 2 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| A1 v4, repetición | SLM solo | EMA α=0.3 | exploración | 0.53 (0.53–0.53) | 26/46 | 4/1/21 (de 36) | -2 / -1.2 / 2 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| A1 v4, repetición | SLM solo | EMA α=0.7 | exploración | 0.87 (0.86–0.88) | 25/46 | 4/3/18 (de 36) | -1 / -0.3 / 2 | 6/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 3 |
| A1 v4, repetición | Tito→SLM | umbral | informativo | 0.79 (0.7–0.87) | 28/46 | 9/16/3 (de 36) | 0 / 1.0 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4, repetición | Tito→SLM | dos seguidas | informativo | 0.19 (0.12–0.26) | 26/46 | 5/3/18 (de 36) | -1 / -0.3 / 3 | 6/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 4 |
| A1 v4, repetición | Tito→SLM | EMA α=0.5 | informativo | 0.39 (0.35–0.43) | 28/46 | 9/16/3 (de 36) | 0 / 1.0 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4, repetición | Tito→SLM | EMA α=0.3 | informativo | 0.24 (0.21–0.26) | 28/46 | 9/16/3 (de 36) | 0 / 1.0 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A1 v4, repetición | Tito→SLM | EMA α=0.7 | informativo | 0.55 (0.49–0.6) | 28/46 | 9/16/3 (de 36) | 0 / 1.0 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A2 v4 | SLM solo | umbral | regla | 0.9995 (0.9995–0.9995) | 18/46 | 4/11/3 (de 36) | 0 / 1.0 / 3 | 7/51 | cotidiana 1, mencion_sin_pedido 2, pedido_razonable 4 |
| A2 v4 | SLM solo | dos seguidas | regla | 0.98 (0.98–0.98) | 24/46 | 3/2/19 (de 36) | -1 / -0.3 / 3 | 7/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 3 |
| A2 v4 | SLM solo | EMA α=0.5 | regla | 0.89 (0.88–0.9) | 25/46 | 2/1/21 (de 36) | -3 / -2.0 / 2 | 7/51 | cotidiana 3, mencion_sin_pedido 2, pedido_razonable 2 |
| A2 v4 | SLM solo | EMA α=0.3 | exploración | 0.72 (0.71–0.73) | 26/46 | 2/1/22 (de 36) | -3 / -2.1 / 2 | 7/51 | cotidiana 3, mencion_sin_pedido 2, pedido_razonable 2 |
| A2 v4 | SLM solo | EMA α=0.7 | exploración | 0.98 (0.97–0.98) | 24/46 | 2/0/22 (de 36) | -3 / -2.2 / 2 | 6/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 2 |
| A2 v4 | Tito→SLM | umbral | informativo | 0.995 (0.995–0.995) | 26/46 | 6/17/3 (de 36) | 0 / 0.6 / 3 | 6/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 4 |
| A2 v4 | Tito→SLM | dos seguidas | informativo | 0.07 (0.06–0.08) | 29/46 | 7/2/19 (de 36) | -1 / 0.2 / 6 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4 | Tito→SLM | EMA α=0.5 | informativo | 0.5 (0.5–0.5) | 28/46 | 7/10/10 (de 36) | 0 / 0.5 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4 | Tito→SLM | EMA α=0.3 | informativo | 0.3 (0.3–0.3) | 28/46 | 8/9/10 (de 36) | 0 / 0.5 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4 | Tito→SLM | EMA α=0.7 | informativo | 0.7 (0.7–0.7) | 28/46 | 7/10/10 (de 36) | 0 / 0.4 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4, repetición | SLM solo | umbral | regla | 0.9999 (0.9999–0.9999) | 15/46 | 2/11/2 (de 36) | 0 / 0.9 / 2 | 6/51 | mencion_sin_pedido 2, pedido_razonable 4 |
| A2 v4, repetición | SLM solo | dos seguidas | regla | 0.99 (0.99–0.99) | 24/46 | 2/2/20 (de 36) | -1 / -0.5 / 2 | 7/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 3 |
| A2 v4, repetición | SLM solo | EMA α=0.5 | regla | 0.92 (0.91–0.93) | 24/46 | 2/0/22 (de 36) | -3 / -2.2 / 2 | 6/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 2 |
| A2 v4, repetición | SLM solo | EMA α=0.3 | exploración | 0.75 (0.74–0.76) | 25/46 | 2/0/23 (de 36) | -3 / -2.3 / 2 | 6/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 2 |
| A2 v4, repetición | SLM solo | EMA α=0.7 | exploración | 0.97 (0.97–0.97) | 24/46 | 2/0/22 (de 36) | -2 / -1.5 / 2 | 6/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 2 |
| A2 v4, repetición | Tito→SLM | umbral | informativo | 0.995 (0.995–0.995) | 26/46 | 7/17/2 (de 36) | 0 / 0.8 / 3 | 6/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 4 |
| A2 v4, repetición | Tito→SLM | dos seguidas | informativo | 0.34 (0.34–0.34) | 28/46 | 5/3/19 (de 36) | -1 / -0.3 / 3 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4, repetición | Tito→SLM | EMA α=0.5 | informativo | 0.5 (0.5–0.5) | 28/46 | 7/10/10 (de 36) | 0 / 0.4 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4, repetición | Tito→SLM | EMA α=0.3 | informativo | 0.35 (0.31–0.39) | 28/46 | 6/3/18 (de 36) | -1 / -0.1 / 4 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A2 v4, repetición | Tito→SLM | EMA α=0.7 | informativo | 0.7 (0.7–0.7) | 28/46 | 7/10/10 (de 36) | 0 / 0.4 / 5 | 7/51 | cotidiana 1, mencion_sin_pedido 1, pedido_razonable 5 |
| A1 tarea | SLM solo | umbral | regla | 0.02 (0.02–0.02) | 25/46 | 13/10/2 (de 36) | 1 / 2.3 / 9 | 5/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 2 |
| A1 tarea | SLM solo | dos seguidas | regla | 0.002 (0.002–0.002) | 27/46 | 9/4/14 (de 36) | -1 / 0.3 / 6 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | SLM solo | EMA α=0.5 | regla | 0.005 (0.005–0.005) | 26/46 | 14/9/3 (de 36) | 1 / 2.2 / 9 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | SLM solo | EMA α=0.3 | exploración | 0.005 (0.005–0.005) | 25/46 | 13/10/2 (de 36) | 1 / 2.3 / 9 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | SLM solo | EMA α=0.7 | exploración | 0.005 (0.005–0.005) | 27/46 | 14/9/4 (de 36) | 1 / 2.0 / 9 | 7/51 | cotidiana 3, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | Tito→SLM | umbral | informativo | 0.02 (0.02–0.02) | 24/46 | 12/10/2 (de 36) | 0.5 / 1.8 / 8 | 5/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 2 |
| A1 tarea | Tito→SLM | dos seguidas | informativo | 0.002 (0.002–0.002) | 26/46 | 8/4/14 (de 36) | -1 / 0.1 / 6 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | Tito→SLM | EMA α=0.5 | informativo | 0.005 (0.005–0.005) | 25/46 | 13/9/3 (de 36) | 1 / 1.7 / 8 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | Tito→SLM | EMA α=0.3 | informativo | 0.005 (0.005–0.005) | 24/46 | 12/10/2 (de 36) | 0.5 / 1.8 / 8 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea | Tito→SLM | EMA α=0.7 | informativo | 0.005 (0.005–0.005) | 26/46 | 13/9/4 (de 36) | 0.5 / 1.5 / 8 | 7/51 | cotidiana 3, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | SLM solo | umbral | regla | 0.01 (0.01–0.01) | 27/46 | 14/10/3 (de 36) | 1 / 2.1 / 9 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | SLM solo | dos seguidas | regla | 0.002 (0.002–0.002) | 27/46 | 9/4/14 (de 36) | -1 / 0.4 / 6 | 7/51 | cotidiana 2, mencion_sin_pedido 2, pedido_razonable 3 |
| A1 tarea, repetición | SLM solo | EMA α=0.5 | regla | 0.005 (0.005–0.005) | 27/46 | 14/10/3 (de 36) | 1 / 2.1 / 9 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | SLM solo | EMA α=0.3 | exploración | 0.01 (0.005–0.01) | 27/46 | 13/10/4 (de 36) | 0 / 1.7 / 9 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | SLM solo | EMA α=0.7 | exploración | 0.005 (0.005–0.005) | 27/46 | 14/10/3 (de 36) | 1 / 2.1 / 9 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | Tito→SLM | umbral | informativo | 0.01 (0.01–0.01) | 26/46 | 12/10/4 (de 36) | 0 / 1.5 / 8 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | Tito→SLM | dos seguidas | informativo | 0.002 (0.002–0.002) | 26/46 | 8/4/14 (de 36) | -1 / 0.2 / 6 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | Tito→SLM | EMA α=0.5 | informativo | 0.01 (0.005–0.01) | 26/46 | 12/10/4 (de 36) | 0 / 1.5 / 8 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | Tito→SLM | EMA α=0.3 | informativo | 0.01 (0.005–0.01) | 26/46 | 12/10/4 (de 36) | 0 / 1.3 / 8 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |
| A1 tarea, repetición | Tito→SLM | EMA α=0.7 | informativo | 0.01 (0.005–0.01) | 26/46 | 12/10/4 (de 36) | 0 / 1.5 / 8 | 6/51 | cotidiana 2, mencion_sin_pedido 1, pedido_razonable 3 |

### Punto elegido y regla de adopción

- **A1 v4:** SLM solo, EMA α=0.5, umbral 0.72 (empata entre 0.71 y 0.73): 26/46 estafas, 4 antes del pedido, 7/51 FA. Repetición en el mismo punto: 26/46, 4 antes, 6/51 FA.
  Contra la línea base JSON v4 (v4 solo (2026-11-05, b), riesgo ≥ 0.4 o alerta: 29/46, 7/51): -3 estafas → no se adopta (3 o más estafas menos). Como dato, contra `alerta_sugerida` sola (28/46, 6/51): -2.
- **A2 v4:** SLM solo, EMA α=0.5, umbral 0.89 (empata entre 0.88 y 0.9): 25/46 estafas, 2 antes del pedido, 7/51 FA. Repetición en el mismo punto: 24/46, 2 antes, 8/51 FA.
- **A1 tarea:** SLM solo, dos seguidas, umbral 0.002 (empata entre 0.002 y 0.002): 27/46 estafas, 9 antes del pedido, 6/51 FA. Repetición en el mismo punto: 27/46, 9 antes, 7/51 FA.
  Contra la línea base JSON v1 (v1 solo (2026-11-04, a), riesgo ≥ 0.4 o alerta: 30/46, 7/51): -3 estafas → no se adopta (3 o más estafas menos). Como dato, contra `alerta_sugerida` sola (28/46, 4/51): -1.

**A2 frente a A1 (v4):** -1 estafas, -2 avisos antes del pedido, FA en trampa 3 → 3. A2 no cumple la regla para preferirse.

### Manuales en el punto elegido (aparte de la decisión)

| corrida | grupo | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | FA por tipo |
|---|---|---|---|---|---|---|
| A1 v4 | laboratorio | 14/16 | 1/0/13 (de 16) | -1 / -0.9 / 0 | 1/10 | legitima_dificil 1 |
| A1 v4 | piloto_escrito | 7/7 | 0/1/6 (de 7) | -1 / -0.9 / 0 | 0/7 | – |
| A1 v4 | trampa | 5/6 | 0/1/4 (de 5) | -1 / -0.8 / 0 | 3/7 | legitima_dificil 3 |
| A2 v4 | laboratorio | 4/16 | 0/1/3 (de 16) | -1 / -0.8 / 0 | 1/10 | legitima_dificil 1 |
| A2 v4 | piloto_escrito | 6/7 | 1/1/4 (de 7) | -3 / -1.8 / 0 | 0/7 | – |
| A2 v4 | trampa | 5/6 | 0/0/5 (de 5) | -3 / -2.8 / 0 | 3/7 | legitima_dificil 3 |
| A1 tarea | laboratorio | 14/16 | 1/2/11 (de 16) | -1 / -0.7 / 0 | 3/10 | legitima_dificil 3 |
| A1 tarea | piloto_escrito | 7/7 | 0/1/6 (de 7) | -1 / -1.1 / 0 | 1/7 | legitima_dificil 1 |
| A1 tarea | trampa | 5/6 | 1/1/3 (de 5) | -1 / -0.4 / 0 | 4/7 | legitima_dificil 4 |

### Tito→SLM, aparte (no se usa para elegir), y costo

Mismo procedimiento de elección, restringido a Tito→SLM. Las consultas al SLM se cuentan hasta el aviso; con Tito, desde su activación (antes de activar corre solo Tito).

| corrida | compuerta | política, umbral | estafas | antes/en/después de T_R | L_R mediana / media / ≥ 3 | falsas alarmas | ms SLM por línea (p50) | consultas al SLM hasta el aviso (150 casos) | por caso (mediana) |
|---|---|---|---|---|---|---|---|---|---|
| A1 v4 | SLM solo | EMA α=0.5, 0.72 | 26/46 | 4/3/19 (de 36) | -1 / -0.3 / 2 | 7/51 | 74 | 2368 | 16.5 |
| A1 v4 | Tito→SLM | umbral, 0.96 | 26/46 | 8/15/3 (de 36) | 0 / 0.8 / 4 | 7/51 | 74 | 1173 | 5 |
| A2 v4 | SLM solo | EMA α=0.5, 0.89 | 25/46 | 2/1/21 (de 36) | -3 / -2.0 / 2 | 7/51 | 72 | 2447 | 18 |
| A2 v4 | Tito→SLM | dos seguidas, 0.07 | 29/46 | 7/2/19 (de 36) | -1 / 0.2 / 6 | 7/51 | 72 | 1185 | 5 |
| A1 tarea | SLM solo | dos seguidas, 0.002 | 27/46 | 9/4/14 (de 36) | -1 / 0.3 / 6 | 6/51 | 147 | 2349 | 16 |
| A1 tarea | Tito→SLM | dos seguidas, 0.002 | 26/46 | 8/4/14 (de 36) | -1 / 0.1 / 6 | 6/51 | 147 | 1239 | 5 |

### Exploración: α de la EMA (fuera de la regla)

Mejor punto del SLM solo con FA ≤ 7 para cada α. Un α queda como candidato para validar en la reserva solo si le gana a α = 0,5 por 3 o más estafas en la corrida y también en su repetición.

| corrida | α | estafas con α=0,5 | estafas con este α | repetición α=0,5 | repetición este α | ¿candidato? |
|---|---|---|---|---|---|---|
| A1 v4 | EMA α=0.3 | 26 | 26 | 26 | 26 | no |
| A1 v4 | EMA α=0.7 | 26 | 26 | 26 | 25 | no |
| A2 v4 | EMA α=0.3 | 25 | 26 | 24 | 25 | no |
| A2 v4 | EMA α=0.7 | 25 | 24 | 24 | 24 | no |
| A1 tarea | EMA α=0.3 | 26 | 25 | 27 | 27 | no |
| A1 tarea | EMA α=0.7 | 26 | 27 | 27 | 27 | no |

