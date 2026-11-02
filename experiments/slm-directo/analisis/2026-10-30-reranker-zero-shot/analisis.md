# Reranker zero-shot: roles × políticas acumuladas

> **Estado: propuesta sin discutir.** Desarrollo sin revisión humana. No elige detector (D09)
> ni política (D08). Las posiciones son líneas, no segundos.

Corridas: `2026-10-30_200421_r1-bge`, `2026-10-31_021253_r1-bge-resto`, `2026-10-29_182016_rapida-gemma3n-e2b`, `2026-10-21_201914_m1-reglas-v2-150`, `2026-10-21_201039_m1-2b-v1v2-nb32`, `2026-10-23_144554_linux-4b-v1v2-cv2-nb32`, `2026-10-23_115920_linux-9b-v1v2-cv2-nb32`

- **Selección** (se elige acá): 57 casos, 19 estafas y 38 legítimas.
- **Informe** (`comparacion_20`, no se elige acá): 20 casos, 10 estafas y 10 legítimas.
- **Meta del tutor:** ≥ 80% de estafas con aviso (sobre todas) y ≤ 15% de FA.
- **FA R07:** legítimas difíciles o con `tipo_legitima` mención sin pedido / pedido razonable.
- **Momento:** avisos antes o en el pedido (`T_R`) · avisos en o después del cumplimiento (`≥C`, ya no protegen).
- Cada configuración usa solo los casos que cubren todas sus corridas; la cobertura figura en la sección de costo.

## Costo por línea

| Config | Líneas | ms p50 | ms p95 | Etapa 1 p50 | Etapa 2 p50 |
|---|---|---|---|---|---|
| `reglas_v2` | 1338 | 0 | 1 | — | — |
| `reranker\|BAAI/bge-reranker-v2-m3\|pedidos\|v4` | 1338 | 4642 | 9003 | — | — |
| `slm\|gemma3n:e2b\|riesgo\|ab` | 524 | 1918 | 2297 | 1913 | 6598 |
| `slm\|gemma3n:e2b\|v2\|ab` | 524 | 10036 | 13576 | — | — |
| `slm\|qwen3.5:2b-q8_0\|tarea\|ab` | 1338 | 1892 | 4673 | — | — |
| `slm\|qwen3.5:2b-q8_0\|v2\|ab` | 1338 | 1787 | 4426 | — | — |
| `slm\|qwen3.5:4b\|tarea\|ab` | 1088 | 609 | 1363 | — | — |
| `slm\|qwen3.5:4b\|v2\|ab` | 1088 | 560 | 624 | — | — |
| `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab` | 1088 | 944 | 2778 | — | — |
| `slm\|qwen3.5:9b-q4_K_M\|v2\|ab` | 1088 | 944 | 2514 | — | — |

## Reranker: orden y tipo de pedido

| Config | AUROC sel. | AUROC inf. | Pedido correcto en `T_R` (sel.) | (inf.) |
|---|---|---|---|---|
| `reranker\|BAAI/bge-reranker-v2-m3\|pedidos\|v4` | 0.639 | 0.795 | 18/19 (95 %) | 6/10 (60 %) |

## Rol A — cada detector solo, con políticas acumuladas

Una fila por detector. Incluye SLM y reglas como comparadores sobre los mismos casos.

### `reglas_v2`

Elegida en selección: **alerta del modelo**.
En el informe: estafas 6/10 (60 %) (IC 95 % 31–83 %), FA 1/10 (10 %) (IC 95 % 2–40 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo | 14/19 (74 %) | 4/38 (11 %) | 2/18 (11 %) | 12 antes/en · 0 ≥C | 6/10 (60 %) | 1/10 (10 %) | 1/6 (17 %) | 5 antes/en · 1 ≥C |

### `reranker\|BAAI/bge-reranker-v2-m3\|pedidos\|v4`

Elegida en selección: **ema 0.5 > 0.02**.
En el informe: estafas 4/10 (40 %) (IC 95 % 17–69 %), FA 1/10 (10 %) (IC 95 % 2–40 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| ema 0.5 > 0.02 | 6/19 (32 %) | 4/38 (11 %) | 4/18 (22 %) | 4 antes/en · 1 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| ema 0.3 > 0.01 | 6/19 (32 %) | 5/38 (13 %) | 4/18 (22 %) | 4 antes/en · 1 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| 2 seguidas > 0.01 | 5/19 (26 %) | 5/38 (13 %) | 3/18 (17 %) | 2 antes/en · 2 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| media 3 > 0.02 | 5/19 (26 %) | 5/38 (13 %) | 5/18 (28 %) | 2 antes/en · 2 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| 2 seguidas > 0.02 | 4/19 (21 %) | 2/38 (5 %) | 2/18 (11 %) | 2 antes/en · 2 ≥C | 3/10 (30 %) | 1/10 (10 %) | 1/6 (17 %) | 1 antes/en · 0 ≥C |

### `slm\|gemma3n:e2b\|riesgo\|ab`

Sin casos de selección en estas corridas: no se elige nada. Para elegir, correr `--lista seleccion-57 --seguir-tras-aviso` con esta configuración.

### `slm\|gemma3n:e2b\|v2\|ab`

Sin casos de selección en estas corridas: no se elige nada. Para elegir, correr `--lista seleccion-57 --seguir-tras-aviso` con esta configuración.

### `slm\|qwen3.5:2b-q8_0\|tarea\|ab`

Elegida en selección: **ema 0.5 > 0.4**.
En el informe: estafas 9/10 (90 %) (IC 95 % 60–98 %), FA 2/10 (20 %) (IC 95 % 6–51 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| ema 0.5 > 0.4 | 15/19 (79 %) | 5/38 (13 %) | 3/18 (17 %) | 13 antes/en · 0 ≥C | 9/10 (90 %) | 2/10 (20 %) | 2/6 (33 %) | 7 antes/en · 0 ≥C |
| ema 0.3 > 0.3 | 14/19 (74 %) | 5/38 (13 %) | 3/18 (17 %) | 7 antes/en · 1 ≥C | 9/10 (90 %) | 2/10 (20 %) | 2/6 (33 %) | 6 antes/en · 0 ≥C |
| alerta del modelo | 13/19 (68 %) | 4/38 (11 %) | 2/18 (11 %) | 12 antes/en · 0 ≥C | 8/10 (80 %) | 1/10 (10 %) | 1/6 (17 %) | 5 antes/en · 0 ≥C |
| ema 0.3 > 0.4 | 13/19 (68 %) | 5/38 (13 %) | 3/18 (17 %) | 5 antes/en · 3 ≥C | 9/10 (90 %) | 2/10 (20 %) | 2/6 (33 %) | 5 antes/en · 1 ≥C |
| ema 0.5 > 0.5 | 13/19 (68 %) | 5/38 (13 %) | 3/18 (17 %) | 5 antes/en · 3 ≥C | 8/10 (80 %) | 1/10 (10 %) | 1/6 (17 %) | 4 antes/en · 0 ≥C |

### `slm\|qwen3.5:2b-q8_0\|v2\|ab`

Elegida en selección: **media 3 > 0.5**.
En el informe: estafas 9/10 (90 %) (IC 95 % 60–98 %), FA 1/10 (10 %) (IC 95 % 2–40 %) · cumple la meta.

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| media 3 > 0.5 | 11/19 (58 %) | 5/38 (13 %) | 2/18 (11 %) | 2 antes/en · 5 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| media 3 > 0.6 | 9/19 (47 %) | 5/38 (13 %) | 2/18 (11 %) | 2 antes/en · 5 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 1 antes/en · 0 ≥C |
| 2 seguidas > 0.3 | 8/19 (42 %) | 5/38 (13 %) | 2/18 (11 %) | 2 antes/en · 4 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| 2 seguidas > 0.4 | 8/19 (42 %) | 5/38 (13 %) | 2/18 (11 %) | 2 antes/en · 4 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| 2 seguidas > 0.5 | 8/19 (42 %) | 5/38 (13 %) | 2/18 (11 %) | 2 antes/en · 4 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |

### `slm\|qwen3.5:4b\|tarea\|ab`

Elegida en selección: **alerta del modelo**.
En el informe: estafas 10/10 (100 %) (IC 95 % 72–100 %), FA 2/10 (20 %) (IC 95 % 6–51 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo | 2/2 (100 %) | 1/21 (5 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 2/10 (20 %) | 2/6 (33 %) | 9 antes/en · 0 ≥C |
| 2 seguidas > 0.3 | 2/2 (100 %) | 1/21 (5 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 3/10 (30 %) | 3/6 (50 %) | 7 antes/en · 0 ≥C |
| media 3 > 0.3 | 2/2 (100 %) | 1/21 (5 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 3/10 (30 %) | 3/6 (50 %) | 9 antes/en · 0 ≥C |
| ema 0.3 > 0.3 | 2/2 (100 %) | 1/21 (5 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 3/10 (30 %) | 3/6 (50 %) | 9 antes/en · 0 ≥C |
| ema 0.5 > 0.3 | 2/2 (100 %) | 1/21 (5 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 3/10 (30 %) | 3/6 (50 %) | 9 antes/en · 0 ≥C |

### `slm\|qwen3.5:4b\|v2\|ab`

Elegida en selección: **alerta del modelo**.
En el informe: estafas 4/10 (40 %) (IC 95 % 17–69 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 3 antes/en · 0 ≥C |
| umbral > 0.3 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 8/10 (80 %) | 2/10 (20 %) | 2/6 (33 %) | 6 antes/en · 0 ≥C |
| 2 seguidas > 0.3 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 6/10 (60 %) | 2/10 (20 %) | 2/6 (33 %) | 2 antes/en · 0 ≥C |
| media 3 > 0.3 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 8/10 (80 %) | 2/10 (20 %) | 2/6 (33 %) | 6 antes/en · 0 ≥C |
| ema 0.3 > 0.3 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 8/10 (80 %) | 2/10 (20 %) | 2/6 (33 %) | 6 antes/en · 0 ≥C |

### `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab`

Elegida en selección: **2 seguidas > 0.3**.
En el informe: estafas 10/10 (100 %) (IC 95 % 72–100 %), FA 1/10 (10 %) (IC 95 % 2–40 %) · cumple la meta.

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| 2 seguidas > 0.3 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 8 antes/en · 0 ≥C |
| media 3 > 0.5 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 8 antes/en · 0 ≥C |
| ema 0.3 > 0.5 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 6 antes/en · 0 ≥C |
| media 3 > 0.6 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 6 antes/en · 0 ≥C |
| ema 0.5 > 0.6 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 8 antes/en · 0 ≥C |

### `slm\|qwen3.5:9b-q4_K_M\|v2\|ab`

Elegida en selección: **umbral > 0.7**.
En el informe: estafas 10/10 (100 %) (IC 95 % 72–100 %), FA 1/10 (10 %) (IC 95 % 2–40 %) · cumple la meta.

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| umbral > 0.7 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 9 antes/en · 0 ≥C |
| umbral > 0.8 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 10/10 (100 %) | 1/10 (10 %) | 1/6 (17 %) | 8 antes/en · 0 ≥C |
| 2 seguidas > 0.7 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 0 antes/en · 0 ≥C |
| ema 0.3 > 0.6 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 9/10 (90 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| media 3 > 0.7 | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 9/10 (90 %) | 1/10 (10 %) | 1/6 (17 %) | 0 antes/en · 0 ≥C |

## Rol C y H5 — verificador: SLM ∧ reranker en la misma línea

El SLM decide con su política y el reranker tiene que superar τ en esa línea. Con `riesgo` (riesgo primero) es la H5: el reranker reemplaza la etapa 2.

### `slm\|qwen3.5:2b-q8_0\|tarea\|ab`

Elegida en selección: **alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02**.
En el informe: estafas 2/10 (20 %) (IC 95 % 6–51 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02 | 5/19 (26 %) | 0/38 (0 %) | 0/18 (0 %) | 4 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01 | 5/19 (26 %) | 3/38 (8 %) | 2/18 (11 %) | 5 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.05 | 2/19 (11 %) | 0/38 (0 %) | 0/18 (0 %) | 1 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.1 | 1/19 (5 %) | 0/38 (0 %) | 0/18 (0 %) | 0 antes/en · 1 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.2 | 0/19 (0 %) | 0/38 (0 %) | 0/18 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

### `slm\|qwen3.5:2b-q8_0\|v2\|ab`

Elegida en selección: **alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02**.
En el informe: estafas 3/10 (30 %) (IC 95 % 11–60 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02 | 5/19 (26 %) | 1/38 (3 %) | 1/18 (6 %) | 4 antes/en · 0 ≥C | 3/10 (30 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01 | 5/19 (26 %) | 5/38 (13 %) | 3/18 (17 %) | 5 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.05 | 2/19 (11 %) | 1/38 (3 %) | 1/18 (6 %) | 1 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.1 | 1/19 (5 %) | 1/38 (3 %) | 1/18 (6 %) | 0 antes/en · 1 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.2 | 0/19 (0 %) | 0/38 (0 %) | 0/18 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

### `slm\|qwen3.5:4b\|tarea\|ab`

Elegida en selección: **alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01**.
En el informe: estafas 5/10 (50 %) (IC 95 % 24–76 %), FA 1/10 (10 %) (IC 95 % 2–40 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 5/10 (50 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 3/10 (30 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.05 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 3/10 (30 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.1 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.2 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |

### `slm\|qwen3.5:4b\|v2\|ab`

Elegida en selección: **alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01**.
En el informe: estafas 2/10 (20 %) (IC 95 % 6–51 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.05 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.1 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.2 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

### `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab`

Elegida en selección: **alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01**.
En el informe: estafas 6/10 (60 %) (IC 95 % 31–83 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.01 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 6/10 (60 %) | 0/10 (0 %) | 0/6 (0 %) | 4 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02 | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.05 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.1 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.2 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |

### `slm\|qwen3.5:9b-q4_K_M\|v2\|ab`

Elegida en selección: **alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02**.
En el informe: estafas 4/10 (40 %) (IC 95 % 17–69 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.02 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.05 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 2 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.1 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.2 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| alerta del modelo ∧ BAAI/bge-reranker-v2-m3 > 0.3 | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

## Rol B — filtro: reranker deriva, después decide el SLM

Aproximación por compuerta sobre corridas completas del SLM: no incluye el bloque de indicio de #68, que cambiaría las respuestas del SLM.

### `slm\|qwen3.5:2b-q8_0\|tarea\|ab`

Elegida en selección: **BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo**.
En el informe: estafas 2/10 (20 %) (IC 95 % 6–51 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo (evita 92 % de consultas) | 5/19 (26 %) | 1/38 (3 %) | 1/18 (6 %) | 4 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo (evita 84 % de consultas) | 5/19 (26 %) | 3/38 (8 %) | 2/18 (11 %) | 5 antes/en · 0 ≥C | 4/10 (40 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.05 → alerta del modelo (evita 98 % de consultas) | 2/19 (11 %) | 0/38 (0 %) | 0/18 (0 %) | 1 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.1 → alerta del modelo (evita 99 % de consultas) | 1/19 (5 %) | 0/38 (0 %) | 0/18 (0 %) | 0 antes/en · 1 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.2 → alerta del modelo (evita 100 % de consultas) | 0/19 (0 %) | 0/38 (0 %) | 0/18 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

### `slm\|qwen3.5:2b-q8_0\|v2\|ab`

Elegida en selección: **BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo**.
En el informe: estafas 3/10 (30 %) (IC 95 % 11–60 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo (evita 92 % de consultas) | 5/19 (26 %) | 1/38 (3 %) | 1/18 (6 %) | 4 antes/en · 0 ≥C | 3/10 (30 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo (evita 84 % de consultas) | 5/19 (26 %) | 5/38 (13 %) | 3/18 (17 %) | 5 antes/en · 0 ≥C | 5/10 (50 %) | 0/10 (0 %) | 0/6 (0 %) | 3 antes/en · 1 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.05 → alerta del modelo (evita 98 % de consultas) | 2/19 (11 %) | 1/38 (3 %) | 1/18 (6 %) | 1 antes/en · 0 ≥C | 3/10 (30 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.1 → alerta del modelo (evita 99 % de consultas) | 1/19 (5 %) | 1/38 (3 %) | 1/18 (6 %) | 0 antes/en · 1 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.2 → alerta del modelo (evita 100 % de consultas) | 0/19 (0 %) | 0/38 (0 %) | 0/18 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

### `slm\|qwen3.5:4b\|tarea\|ab`

Elegida en selección: **BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo**.
En el informe: estafas 6/10 (60 %) (IC 95 % 31–83 %), FA 1/10 (10 %) (IC 95 % 2–40 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo (evita 90 % de consultas) | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 6/10 (60 %) | 1/10 (10 %) | 1/6 (17 %) | 3 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo (evita 96 % de consultas) | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.05 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.1 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 1/10 (10 %) | 1/6 (17 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.2 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |

### `slm\|qwen3.5:4b\|v2\|ab`

Elegida en selección: **BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo**.
En el informe: estafas 2/10 (20 %) (IC 95 % 6–51 %), FA 0/10 (0 %) (IC 95 % 0–28 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo (evita 90 % de consultas) | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 2/10 (20 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo (evita 96 % de consultas) | 1/2 (50 %) | 0/21 (0 %) | 0/1 (0 %) | 1 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.05 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.1 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.2 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 0/10 (0 %) | 0/10 (0 %) | 0/6 (0 %) | 0 antes/en · 0 ≥C |

### `slm\|qwen3.5:9b-q4_K_M\|tarea\|ab`

Elegida en selección: **BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo**.
En el informe: estafas 6/10 (60 %) (IC 95 % 31–83 %), FA 1/10 (10 %) (IC 95 % 2–40 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo (evita 90 % de consultas) | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 6/10 (60 %) | 1/10 (10 %) | 1/6 (17 %) | 4 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo (evita 96 % de consultas) | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.05 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.1 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 1/10 (10 %) | 1/6 (17 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.2 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |

### `slm\|qwen3.5:9b-q4_K_M\|v2\|ab`

Elegida en selección: **BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo**.
En el informe: estafas 4/10 (40 %) (IC 95 % 17–69 %), FA 1/10 (10 %) (IC 95 % 2–40 %).

| Configuración | Sel.: estafas | Sel.: FA | Sel.: FA R07 | Sel.: momento | Inf.: estafas | Inf.: FA | Inf.: FA R07 | Inf.: momento |
|---|---|---|---|---|---|---|---|---|
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.02 → alerta del modelo (evita 96 % de consultas) | 2/2 (100 %) | 0/21 (0 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.01 → alerta del modelo (evita 90 % de consultas) | 2/2 (100 %) | 1/21 (5 %) | 0/1 (0 %) | 2 antes/en · 0 ≥C | 6/10 (60 %) | 1/10 (10 %) | 1/6 (17 %) | 4 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.05 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 4/10 (40 %) | 1/10 (10 %) | 1/6 (17 %) | 2 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.1 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 2/10 (20 %) | 1/10 (10 %) | 1/6 (17 %) | 1 antes/en · 0 ≥C |
| BAAI/bge-reranker-v2-m3 (pedidos) > 0.2 → alerta del modelo (evita 100 % de consultas) | 0/2 (0 %) | 0/21 (0 %) | 0/1 (0 %) | 0 antes/en · 0 ≥C | 1/10 (10 %) | 0/10 (0 %) | 0/6 (0 %) | 1 antes/en · 0 ≥C |
