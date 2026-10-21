# Evaluación de Métricas

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | lineas | 27/29 (93.1 %) [78.0 %, 98.1 %] | 9/24 (37.5 %) [21.2 %, 57.3 %] | 27/36 (75.0 %) [58.9 %, 86.2 %] | 0.831 | 0 [IQR 1.8, n=26] | 3 [IQR 4, n=13] | 1282 / 3462 |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | lineas | 20/29 (69.0 %) [50.8 %, 82.7 %] | 2/24 (8.3 %) [2.3 %, 25.8 %] | 20/22 (90.9 %) [72.2 %, 97.5 %] | 0.784 | 0 [IQR 0, n=20] | 1 [IQR 2, n=12] | 2646 / 6036 |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | lineas | 24/24 (100.0 %) [86.2 %, 100.0 %] | 9/18 (50.0 %) [29.0 %, 71.0 %] | 24/33 (72.7 %) [55.8 %, 84.9 %] | 0.842 | 1.5 [IQR 3, n=24] | 4 [IQR 4.5, n=11] | 6628 / 10186 |
| `2026-10-17_150455_m1-reglas \| reglas` | lineas | 23/29 (79.3 %) [61.6 %, 90.2 %] | 14/24 (58.3 %) [38.8 %, 75.5 %] | 23/37 (62.2 %) [46.1 %, 75.9 %] | 0.697 | 0 [IQR 0, n=23] | 1 [IQR 3.2, n=12] | 5 / 13 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 20/28 (71.4 %) | [52.9 %, 84.7 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 8/28 (28.6 %) | [15.3 %, 47.1 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 7/28 (25.0 %) | [12.7 %, 43.4 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 12/14 (85.7 %) | [60.1 %, 96.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 9/14 (64.3 %) | [38.8 %, 83.7 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 17/28 (60.7 %) | [42.4 %, 76.4 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 2/28 (7.1 %) | [2.0 %, 22.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 2/28 (7.1 %) | [2.0 %, 22.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 5/14 (35.7 %) | [16.3 %, 61.2 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 24/24 (100.0 %) | [86.2 %, 100.0 %] | 0 (ninguna) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 13/24 (54.2 %) | [35.1 %, 72.1 %] | 0 (ninguna) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 12/24 (50.0 %) | [31.4 %, 68.6 %] | 0 (ninguna) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 11/11 (100.0 %) | [74.1 %, 100.0 %] | 13 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 11/11 (100.0 %) | [74.1 %, 100.0 %] | 13 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 10/11 (90.9 %) | [62.3 %, 98.4 %] | 13 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150455_m1-reglas \| reglas` | $T_R$ (pedido) | 0 lineas | 20/28 (71.4 %) | [52.9 %, 84.7 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150455_m1-reglas \| reglas` | $T_R$ (pedido) | 1 lineas | 5/28 (17.9 %) | [7.9 %, 35.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150455_m1-reglas \| reglas` | $T_R$ (pedido) | 2 lineas | 5/28 (17.9 %) | [7.9 %, 35.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-17_150455_m1-reglas \| reglas` | $T_C$ (cumplimiento) | 0 lineas | 12/14 (85.7 %) | [60.1 %, 96.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150455_m1-reglas \| reglas` | $T_C$ (cumplimiento) | 1 lineas | 12/14 (85.7 %) | [60.1 %, 96.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-17_150455_m1-reglas \| reglas` | $T_C$ (cumplimiento) | 2 lineas | 4/14 (28.6 %) | [11.7 %, 54.6 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | `laboratorio` | 14/16 (87.5 %) | 4/10 (40.0 %) | 0 (n=14) | 3 (n=4) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | `piloto_escrito` | 7/7 (100.0 %) | 2/7 (28.6 %) | 0 (n=7) | 5 (n=5) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | `trampa` | 6/6 (100.0 %) | 3/7 (42.9 %) | -1 (n=5) | 3 (n=4) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | `laboratorio` | 10/16 (62.5 %) | 0/10 (0.0 %) | 0 (n=10) | 1 (n=5) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | `piloto_escrito` | 6/7 (85.7 %) | 0/7 (0.0 %) | 0 (n=6) | 4 (n=4) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | `trampa` | 4/6 (66.7 %) | 2/7 (28.6 %) | -1 (n=4) | 1 (n=3) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | `laboratorio` | 16/16 (100.0 %) | 6/10 (60.0 %) | 0 (n=16) | 3 (n=5) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | `piloto_escrito` | 7/7 (100.0 %) | 3/7 (42.9 %) | 3 (n=7) | 7 (n=5) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | `trampa` | 1/1 (100.0 %) | 0/1 (0.0 %) | 5 (n=1) | 8 (n=1) |
| `2026-10-17_150455_m1-reglas \| reglas` | `laboratorio` | 13/16 (81.2 %) | 1/10 (10.0 %) | 0 (n=13) | 1 (n=5) |
| `2026-10-17_150455_m1-reglas \| reglas` | `piloto_escrito` | 6/7 (85.7 %) | 7/7 (100.0 %) | 1.5 (n=6) | 2 (n=4) |
| `2026-10-17_150455_m1-reglas \| reglas` | `trampa` | 4/6 (66.7 %) | 6/7 (85.7 %) | 2 (n=4) | 9 (n=3) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | `negativo_dificil` | 24 | 9 | 37.5 % | [21.2 %, 57.3 %] |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | `negativo_dificil` | 24 | 2 | 8.3 % | [2.3 %, 25.8 %] |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | `negativo_dificil` | 18 | 9 | 50.0 % | [29.0 %, 71.0 %] |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-17_150455_m1-reglas \| reglas` | `negativo_dificil` | 24 | 14 | 58.3 % | [38.8 %, 75.5 %] |
| `2026-10-17_150455_m1-reglas \| reglas` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:0.8b-q8_0\|tarea\|ab` | 93.1 % | 37.5 % | 0.2 % | 2.4 % | 11.6 % | 21.6 % | 71.3 % |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:2b-q8_0\|tarea\|ab` | 69.0 % | 8.3 % | 0.8 % | 7.7 % | 30.3 % | 47.9 % | 89.2 % |
| `2026-10-17_150516_m1-gguf \| slm\|qwen3.5:4b-q4_K_M\|tarea\|ab` | 100.0 % | 50.0 % | 0.2 % | 2.0 % | 9.5 % | 18.2 % | 66.7 % |
| `2026-10-17_150455_m1-reglas \| reglas` | 79.3 % | 58.3 % | 0.1 % | 1.4 % | 6.7 % | 13.1 % | 57.6 % |
