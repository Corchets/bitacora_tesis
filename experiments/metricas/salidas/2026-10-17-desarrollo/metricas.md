# Evaluación de Métricas

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `2026-10-13_224418_linea-base-reglas \| reglas` | lineas | 23/29 (79.3 %) [61.6 %, 90.2 %] | 14/24 (58.3 %) [38.8 %, 75.5 %] | 23/37 (62.2 %) [46.1 %, 75.9 %] | 0.697 | 0 [IQR 0, n=23] | 1 [IQR 3.2, n=12] | 7 / 18 |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | lineas | 26/29 (89.7 %) [73.6 %, 96.4 %] | 8/24 (33.3 %) [18.0 %, 53.3 %] | 26/34 (76.5 %) [60.0 %, 87.6 %] | 0.825 | 0 [IQR 2, n=25] | 3 [IQR 4, n=12] | 276 / 706 |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | lineas | 20/29 (69.0 %) [50.8 %, 82.7 %] | 2/24 (8.3 %) [2.3 %, 25.8 %] | 20/22 (90.9 %) [72.2 %, 97.5 %] | 0.784 | 0 [IQR 0, n=20] | 1 [IQR 2, n=12] | 523 / 1133 |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | lineas | 21/29 (72.4 %) [54.3 %, 85.3 %] | 2/24 (8.3 %) [2.3 %, 25.8 %] | 21/23 (91.3 %) [73.2 %, 97.6 %] | 0.808 | 0 [IQR 0, n=21] | 1 [IQR 2, n=12] | 532 / 1118 |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | lineas | 29/29 (100.0 %) [88.3 %, 100.0 %] | 15/24 (62.5 %) [42.7 %, 78.8 %] | 29/44 (65.9 %) [51.1 %, 78.1 %] | 0.795 | 2 [IQR 3, n=28] | 5 [IQR 4, n=14] | 901 / 1646 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `2026-10-13_224418_linea-base-reglas \| reglas` | $T_R$ (pedido) | 0 lineas | 20/28 (71.4 %) | [52.9 %, 84.7 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | $T_R$ (pedido) | 1 lineas | 5/28 (17.9 %) | [7.9 %, 35.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | $T_R$ (pedido) | 2 lineas | 5/28 (17.9 %) | [7.9 %, 35.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | $T_C$ (cumplimiento) | 0 lineas | 12/14 (85.7 %) | [60.1 %, 96.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | $T_C$ (cumplimiento) | 1 lineas | 12/14 (85.7 %) | [60.1 %, 96.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | $T_C$ (cumplimiento) | 2 lineas | 4/14 (28.6 %) | [11.7 %, 54.6 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 19/28 (67.9 %) | [49.3 %, 82.1 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 7/28 (25.0 %) | [12.7 %, 43.4 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 7/28 (25.0 %) | [12.7 %, 43.4 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 10/14 (71.4 %) | [45.4 %, 88.3 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 8/14 (57.1 %) | [32.6 %, 78.6 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 17/28 (60.7 %) | [42.4 %, 76.4 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 2/28 (7.1 %) | [2.0 %, 22.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 2/28 (7.1 %) | [2.0 %, 22.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 5/14 (35.7 %) | [16.3 %, 61.2 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 18/28 (64.3 %) | [45.8 %, 79.3 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 2/28 (7.1 %) | [2.0 %, 22.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 2/28 (7.1 %) | [2.0 %, 22.6 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 11/14 (78.6 %) | [52.4 %, 92.4 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 5/14 (35.7 %) | [16.3 %, 61.2 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | $T_R$ (pedido) | 0 lineas | 28/28 (100.0 %) | [87.9 %, 100.0 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | $T_R$ (pedido) | 1 lineas | 17/28 (60.7 %) | [42.4 %, 76.4 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | $T_R$ (pedido) | 2 lineas | 16/28 (57.1 %) | [39.1 %, 73.5 %] | 1 (llamadas de vishing sin marca T_R en la referencia humana) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | $T_C$ (cumplimiento) | 0 lineas | 14/14 (100.0 %) | [78.5 %, 100.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | $T_C$ (cumplimiento) | 1 lineas | 14/14 (100.0 %) | [78.5 %, 100.0 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | $T_C$ (cumplimiento) | 2 lineas | 13/14 (92.9 %) | [68.5 %, 98.7 %] | 15 (llamadas de vishing sin marca T_C en la referencia humana) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `2026-10-13_224418_linea-base-reglas \| reglas` | `laboratorio` | 13/16 (81.2 %) | 1/10 (10.0 %) | 0 (n=13) | 1 (n=5) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | `piloto_escrito` | 6/7 (85.7 %) | 7/7 (100.0 %) | 1.5 (n=6) | 2 (n=4) |
| `2026-10-13_224418_linea-base-reglas \| reglas` | `trampa` | 4/6 (66.7 %) | 6/7 (85.7 %) | 2 (n=4) | 9 (n=3) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | `laboratorio` | 14/16 (87.5 %) | 4/10 (40.0 %) | 0 (n=14) | 3 (n=4) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | `piloto_escrito` | 7/7 (100.0 %) | 2/7 (28.6 %) | 0 (n=7) | 5 (n=5) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | `trampa` | 5/6 (83.3 %) | 2/7 (28.6 %) | 0.5 (n=4) | 4 (n=3) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `laboratorio` | 10/16 (62.5 %) | 0/10 (0.0 %) | 0 (n=10) | 1 (n=5) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `piloto_escrito` | 6/7 (85.7 %) | 0/7 (0.0 %) | 0 (n=6) | 4 (n=4) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `trampa` | 4/6 (66.7 %) | 2/7 (28.6 %) | -1.5 (n=4) | 1 (n=3) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `laboratorio` | 11/16 (68.8 %) | 0/10 (0.0 %) | 0 (n=11) | 1 (n=5) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `piloto_escrito` | 6/7 (85.7 %) | 0/7 (0.0 %) | 0 (n=6) | 4 (n=4) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `trampa` | 4/6 (66.7 %) | 2/7 (28.6 %) | -1 (n=4) | 1 (n=3) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | `laboratorio` | 16/16 (100.0 %) | 5/10 (50.0 %) | 0 (n=16) | 3 (n=5) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | `piloto_escrito` | 7/7 (100.0 %) | 4/7 (57.1 %) | 3 (n=7) | 7 (n=5) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | `trampa` | 6/6 (100.0 %) | 6/7 (85.7 %) | 4 (n=5) | 8.5 (n=4) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `2026-10-13_224418_linea-base-reglas \| reglas` | `negativo_dificil` | 24 | 14 | 58.3 % | [38.8 %, 75.5 %] |
| `2026-10-13_224418_linea-base-reglas \| reglas` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | `negativo_dificil` | 24 | 8 | 33.3 % | [18.0 %, 53.3 %] |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `negativo_dificil` | 24 | 2 | 8.3 % | [2.3 %, 25.8 %] |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `negativo_dificil` | 24 | 2 | 8.3 % | [2.3 %, 25.8 %] |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | `negativo_dificil` | 24 | 15 | 62.5 % | [42.7 %, 78.8 %] |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `2026-10-13_224418_linea-base-reglas \| reglas` | 79.3 % | 58.3 % | 0.1 % | 1.4 % | 6.7 % | 13.1 % | 57.6 % |
| `2026-10-14_173532_demo-qwen3.5-0.8b \| slm\|qwen3.5:0.8b\|tarea\|ab` | 89.7 % | 33.3 % | 0.3 % | 2.6 % | 12.4 % | 23.0 % | 72.9 % |
| `2026-10-14_172930_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | 69.0 % | 8.3 % | 0.8 % | 7.7 % | 30.3 % | 47.9 % | 89.2 % |
| `2026-10-14_175451_demo-qwen3.5-2b \| slm\|qwen3.5:2b\|tarea\|ab` | 72.4 % | 8.3 % | 0.9 % | 8.1 % | 31.4 % | 49.1 % | 89.7 % |
| `2026-10-14_174602_demo-qwen3.5-4b \| slm\|qwen3.5:4b\|tarea\|ab` | 100.0 % | 62.5 % | 0.2 % | 1.6 % | 7.8 % | 15.1 % | 61.5 % |
