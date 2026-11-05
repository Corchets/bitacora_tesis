# Métricas E2E sobre audio TTS

> Material de desarrollo: audio TTS, referencias temporales derivadas de los guiones y casos escritos sin revisión humana. Las referencias se cargaron desde `experiments/asr-local/audio-referencia/*.json`; para estéreo se agregó `-estereo` al `case_id` de una copia temporal para coincidir con el replay. No es evidencia de rendimiento sobre voz humana ni evaluación final.

Las métricas temporales y falsas alarmas siguen las definiciones de `docs/evaluacion/METRICAS.md`; T_R y T_C están en segundos.

## 2026-10-17_e2e-zipformer-reglas-sc_wa_code_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 1 | -4.6 [IQR 0, n=1] | 0.2 [IQR 0, n=1] | 11 / 20 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 1/1 (100.0 %) | 0/0 | -4.6 (n=1) | 0.2 (n=1) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | 100.0 % | — | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-reglas-lg_wa_consulta_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/1 (0.0 %) [0.0 %, 79.3 %] | — | — | — | 7 / 14 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | — | — | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 0/0 | 1/1 (100.0 %) | — | — |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `negativo_dificil` | 1 | 1 | 100.0 % | [20.7 %, 100.0 %] |
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | — | 100.0 % | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-0.8b-q8_0-mono-sc_wa_code_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 1 | -1.7 [IQR 0, n=1] | 3.1 [IQR 0, n=1] | 1953 / 3206 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 1/1 (100.0 %) | 0/0 | -1.7 (n=1) | 3.1 (n=1) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | 100.0 % | — | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-0.8b-q8_0-mono-lg_wa_consulta_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/1 (0.0 %) [0.0 %, 79.3 %] | — | — | — | 3663 / 7947 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | — | — | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 0/0 | 1/1 (100.0 %) | — | — |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `negativo_dificil` | 1 | 1 | 100.0 % | [20.7 %, 100.0 %] |
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | — | 100.0 % | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-0.8b-q8_0-estereo-sc_wa_code_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 1 | -7.0 [IQR 0, n=1] | -2.2 [IQR 0, n=1] | 1299 / 2339 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 1/1 (100.0 %) | 0/0 | -7.0 (n=1) | -2.2 (n=1) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | 100.0 % | — | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-0.8b-q8_0-estereo-lg_wa_consulta_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/1 (0.0 %) [0.0 %, 79.3 %] | — | — | — | 1215 / 2255 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | — | — | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 0/0 | 1/1 (100.0 %) | — | — |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `negativo_dificil` | 1 | 1 | 100.0 % | [20.7 %, 100.0 %] |
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | — | 100.0 % | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-2b-q8_0-mono-sc_wa_code_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 1 | -8.6 [IQR 0, n=1] | -3.8 [IQR 0, n=1] | 4003 / 4302 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 1/1 (100.0 %) | 0/0 | -8.6 (n=1) | -3.8 (n=1) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | 100.0 % | — | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-2b-q8_0-mono-lg_wa_consulta_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/1 (0.0 %) [0.0 %, 79.3 %] | — | — | — | 5227 / 6032 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | — | — | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 0/0 | 1/1 (100.0 %) | — | — |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `negativo_dificil` | 1 | 1 | 100.0 % | [20.7 %, 100.0 %] |
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | — | 100.0 % | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-2b-q8_0-estereo-sc_wa_code_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 1/1 (100.0 %) [20.7 %, 100.0 %] | 0/0 (—) — | 1/1 (100.0 %) [20.7 %, 100.0 %] | 1 | -15.9 [IQR 0, n=1] | -11.0 [IQR 0, n=1] | 5151 / 6920 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | 0/1 (0.0 %) | [0.0 %, 79.3 %] | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 1/1 (100.0 %) | 0/0 | -15.9 (n=1) | -11.0 (n=1) |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | 100.0 % | — | — | — | — | — | — |

## 2026-10-17_e2e-zipformer-2b-q8_0-estereo-lg_wa_consulta_01

> **Advertencia de validez metodológica:** Material de **desarrollo**: casos escritos sin revisión humana; no es test reservado ni evidencia de rendimiento final. Las decisiones D07 (taxonomía y marcas de referencia) y D08 (política de alerta y protocolo experimental) continúan ABIERTAS en [docs/gestion/MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md).

> **Parámetros candidatos:** Los umbrales $\delta$ evaluados son candidatos de trabajo (5, 10, 20 s para audio; 0, 1, 2 líneas para texto). Las marcas temporales y referencias principales permanecen sujetas a acuerdo en [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

## 1. Resumen General de Detección y Clasificación por Configuración

| Configuración | Unidad | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Precision | F1 | Mediana $L_R$ [IQR, n] | Mediana $L_C$ [IQR, n] | ms p50 / p95 |
|---|---|---|---|---|---|---|---|---|
| `replay \| replay` | segundos | 0/0 (—) — | 0/1 (0.0 %) [0.0 %, 79.3 %] | 0/0 (—) — | — | — | — | 4442 / 5086 |

## 2. Alertas con Margen Suficiente (Preventive@δ)

Medición según METRICAS.md §3: `(llamadas con T_A ≤ X − δ) / (evaluables para X)`.
Las llamadas sin alerta permanecen en el denominador. Casos sin marca $X$ en la referencia quedan excluidos.

| Configuración | Ref ($X$) | δ | Proporción con margen | IC 95 % (Wilson) | Excluidas sin marca |
|---|---|---|---|---|---|
| `replay \| replay` | $T_R$ (pedido) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_R$ (pedido) | 20.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 5.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 10.0 segundos | — | — | 0 (ninguna) |
| `replay \| replay` | $T_C$ (cumplimiento) | 20.0 segundos | — | — | 0 (ninguna) |

## 3. Desglose por Grupo de Casos

| Configuración | Grupo | Vishing con aviso (Recall) | Falsas alarmas (Legítimas) | Mediana $L_R$ | Mediana $L_C$ |
|---|---|---|---|---|---|
| `replay \| replay` | `piloto_escrito` | 0/0 | 0/1 (0.0 %) | — | — |

## 4. Desglose de Legítimas: Cotidianas vs Negativos Difíciles

| Configuración | Subtipo de Legítima | Casos | Falsas alarmas | Tasa de FA | IC 95 % (Wilson) |
|---|---|---|---|---|---|
| `replay \| replay` | `negativo_dificil` | 1 | 0 | 0.0 % | [0.0 %, 79.3 %] |
| `replay \| replay` | `cotidiana` | 0 | 0 | — | — (no disponible en este set) |

## 5. Análisis de Sensibilidad: Precisión ante Prevalencia Hipotética de Fraude

Calculado según METRICAS.md §4: `precision(p) = (p × r) / (p × r + (1 − p) × f)`.
*Nota:* Supone que las tasas de detección ($r$) y falsas alarmas ($f$) se mantienen constantes. Es un análisis de sensibilidad, no evidencia de rendimiento real en despliegue.

| Configuración | Recall ($r$) | Tasa FA ($f$) | $p = 0.1\%$ | $p = 1.0\%$ | $p = 5.0\%$ | $p = 10.0\%$ | $p = 50.0\%$ |
|---|---|---|---|---|---|---|---|
| `replay \| replay` | — | 0.0 % | — | — | — | — | — |
