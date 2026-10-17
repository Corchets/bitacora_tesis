# Comparación de candidatos para desarrollo

> **Estado: propuesta sin discutir.** Comparación sobre material de desarrollo (casos escritos sin revisión humana y audio TTS); no elige candidato ([D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)) ni política ([D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)).

## Alcance y lectura

La comparación combina 53 casos escritos (29 vishing y 24 negativos difíciles), una repetición del 2B en Windows, corridas exploratorias de CPU y M1 y dos audios TTS en el replay punta a punta. No hay legítimas cotidianas, revisión humana de referencias, test reservado ni voz humana. Los porcentajes describen este material únicamente. Las fórmulas de detección e incertidumbre siguen [METRICAS.md](METRICAS.md); los gates, [PREFACTIBILIDAD-TECNICA.md](../investigacion/PREFACTIBILIDAD-TECNICA.md).

## Tabla maestra de detectores

En texto, las métricas son por caso/conversación, con detección de líneas utilizada por el reporte. La latencia es por línea. La memoria disponible en estas salidas es el tamaño de modelo comunicado por Ollama o la memoria Ollama del resumen CPU; no es una medición homogénea de pico RSS ni memoria conjunta del pipeline. Las rutas enlazadas contienen los manifiestos/salidas y las trazas subyacentes.

| Candidato y máquina | Vishing con aviso (IC Wilson 95 %) | Falsas alarmas (IC Wilson 95 %) | Posición respecto de T_R (líneas) | Latencia p50 / p95 | Memoria observada en manifiesto | RTF <1 | p95 ≤1,5 s* | memoria perfil | Fuente |
|---|---:|---:|---|---:|---:|---|---|---|---|
| Reglas, Windows GPU | 23/29 (79,3%; 61,6–90,2) | 14/24 (58,3%; 38,8–75,5) | T_A ≤ T_R: 20/28; después o sin aviso: 8/28* | 7/18 ms | no medido | no medido | cumple* | no medido‡ | [métricas desarrollo](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-13_224418_linea-base-reglas/manifiesto.json) |
| Qwen3.5 0.8B, Windows GPU | 26/29 (89,7%; 73,6–96,4) | 8/24 (33,3%; 18,0–53,3) | T_A ≤ T_R: 19/28; después o sin aviso: 9/28* | 276/706 ms | modelo 544,5 MiB | no medido | cumple* | no medido‡ | [métricas](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-14_173532_demo-qwen3.5-0.8b/manifiesto.json) |
| Qwen3.5 2B, Windows GPU (corrida 1) | 20/29 (69,0%; 50,8–82,7) | 2/24 (8,3%; 2,3–25,8) | T_A ≤ T_R: 17/28; después o sin aviso: 11/28* | 523/1.133 ms | modelo 2.254,9 MiB | no medido | cumple* | no medido‡ | [métricas](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-14_172930_demo-qwen3.5-2b/manifiesto.json) |
| Qwen3.5 2B, Windows GPU (corrida 2) | 21/29 (72,4%; 54,3–85,3) | 2/24 (8,3%; 2,3–25,8) | T_A ≤ T_R: 18/28; después o sin aviso: 10/28* | 532/1.118 ms | modelo 2.254,9 MiB | no medido | cumple* | no medido‡ | [métricas](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-14_175451_demo-qwen3.5-2b/manifiesto.json) |
| Qwen3.5 4B, Windows GPU | 29/29 (100%; 88,3–100) | 15/24 (62,5%; 42,7–78,8) | T_A ≤ T_R: 28/28; después o sin aviso: 0* | 901/1.646 ms | modelo 2.995,0 MiB | no medido | no cumple* | no medido‡ | [métricas](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-14_174602_demo-qwen3.5-4b/manifiesto.json) |
| Reglas, Windows CPU 2 hilos (7+7 casos) | 6/7 (85,7%; 48,7–97,4) | 7/7 (100%; 64,6–100) | antes: 3; en: 3; después: 0 | 11/22 ms | no medido | no medido | cumple* | no medido‡ | [resumen CPU](../../experiments/slm-directo/corridas/2026-10-14_191429_cpu-2hilos/resumen.md) |
| Qwen3.5 0.8B, Windows CPU 2 hilos (7+7 casos) | 7/7 (100%; 64,6–100) | 2/7 (28,6%; 8,2–64,1) | antes: 3; en: 3; después: 0 | 3.913/7.331 ms | modelo 547,5 MiB | no medido | no cumple* (p95 7,33 s) | no medido‡ | [métricas CPU](../../experiments/slm-directo/corridas/2026-10-14_191429_cpu-2hilos/resumen.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-14_191429_cpu-2hilos/manifiesto.json) |
| Qwen3.5 2B, Windows CPU 2 hilos (7+7 casos) | 6/7 (85,7%; 48,7–97,4) | 0/7 (0%; 0–35,4) | antes: 0; en: 6; después: 0 | 8.216/12.956 ms | modelo 2.259,9 MiB | no medido | no cumple* (p95 12,96 s) | no medido‡ | [métricas CPU](../../experiments/slm-directo/corridas/2026-10-14_191429_cpu-2hilos/resumen.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-14_191429_cpu-2hilos/manifiesto.json) |
| Reglas, Apple M1 | 23/29 (79,3%; 61,6–90,2) | 14/24 (58,3%; 38,8–75,5) | 20/28 antes; en: 0; después: 8/28* | 5/13 ms | no medido | no medido | cumple* | no medido‡ | [métricas M1](../../experiments/metricas/salidas/2026-10-17-m1/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-17_150455_m1-reglas/manifiesto.json) |
| Qwen3.5 0.8B GGUF, Apple M1 | 27/29 (93,1%; 78,0–98,1) | 9/24 (37,5%; 21,2–57,3) | 20/28 antes; en: 0; después: 8/28* | 1.282/3.462 ms | modelo 1.018,4 MiB | no medido | no cumple* | no medido‡ | [métricas M1](../../experiments/metricas/salidas/2026-10-17-m1/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-17_150516_m1-gguf/manifiesto.json) |
| Qwen3.5 2B GGUF, Apple M1 | 20/29 (69,0%; 50,8–82,7) | 2/24 (8,3%; 2,3–25,8) | T_A ≤ T_R: 17/28; después o sin aviso: 11/28* | 2.646/6.036 ms | modelo 2.236,7 MiB | no medido | no cumple* | no medido‡ | [métricas M1](../../experiments/metricas/salidas/2026-10-17-m1/metricas.md), [manifiesto](../../experiments/slm-directo/corridas/2026-10-17_150516_m1-gguf/manifiesto.json) |
| Qwen3.5 4B Q4_K_M, Apple M1 | 24/24†† | 9/18 (50,0%; 29,0–71,0)†† | incompleto†† | 6.628/10.186 ms†† | corrida interrumpida | no medido | no cumple*†† | no medido‡ | [métricas M1](../../experiments/metricas/salidas/2026-10-17-m1/metricas.md), [comparación](../../experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/README.md) |

\* La comparación del umbral de 1,5 s usa p95 de latencia por línea del ensayo de texto, no la métrica exacta de cierre de turno; sirve como indicador de cribado. El umbral por sí solo no prueba cumplimiento operativo. Los manifiestos del ensayo directo no registran RTF sostenido ni pico RSS del proceso: la memoria visible es tamaño de modelo cargado cuando está disponible, por lo que el gate de memoria del pipeline queda “no medido”. RTF integrado solo se informa en las pruebas de ASR/replay de esta comparación. Los perfiles de 256/512/1024 MB son presupuesto de pipeline; las corridas de detectores aisladas no se comparan directamente con esos techos. †† El 4B M1 se interrumpió tras 42/53 casos por presión de memoria. Las tasas y conteos de este subset no son una evaluación completa ni comparables con denominadores completos.

Las referencias a 53 casos no significan que cada corrida haya completado todas las actualizaciones válidas. La segunda ejecución 2B en Windows cambió el resultado en 2/53 casos respecto de la primera en decisión final (y 60/464 líneas en el puntaje de riesgo); no es repetición suficiente para estimar estabilidad. La medición Windows–M1 informa acuerdo de decisiones de 51/53 (96,2%) para 0.8B y 52/53 (98,1%) para 2B, aunque las latencias fueron mayores en M1. Véase [análisis de repetibilidad y diferencias](../../experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/README.md).

## ASR sobre audio TTS

| Motor / audio | RTF | Memoria pico | WER | Palabras críticas | Fuente |
|---|---:|---:|---:|---|---|
| Zipformer, SC-WA-CODE-01 mono | 0,1710 | 357,00 MB | 4,35% (2/46) | código, cero, SMS y demás claves OK | [resumen](../../experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_zipformer/resumen.md), [manifiesto](../../experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_zipformer/manifiesto.json) |
| Whisper, SC-WA-CODE-01 mono | 0,2745 | 276,91 MB | 17,39% (8/46) | código OK; `cero` perdida; demás claves listadas OK | [resumen](../../experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_whisper/resumen.md), [manifiesto](../../experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_whisper/manifiesto.json) |
| Zipformer, LG-WA-CONSULTA-01 mono | 0,1032 | 422,70 MB | 5,00% (2/40) | código, cero, SMS y demás claves OK | [resumen](../../experiments/asr-local/corridas/2026-10-17_humo_lg_wa_consulta_01_zipformer/resumen.md), [manifiesto](../../experiments/asr-local/corridas/2026-10-17_humo_lg_wa_consulta_01_zipformer/manifiesto.json) |

Son muestras de dos audios TTS breves, generados con voces de sistema; no miden reconocimiento de voz humana ni bastan para elegir ASR. Zipformer y Whisper solo se compararon sobre SC-WA-CODE-01 en este humo. Las claves particulares aparecen en `analisis_palabras_clave` de cada manifiesto; los dos reconocedores conservaron `código` en SC, mientras Whisper sustituyó “SMS” por “SMDG” y omitió las seis apariciones de “cero” en el texto reconocido; Zipformer conservó las palabras críticas listadas para ese audio. RTF/memoria no se trasladan al teléfono.

## Replay punta a punta (audio TTS)

Las métricas se toman del [resumen E2E](../../experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md); las trazas y manifiestos individuales están bajo [`corridas/`](../../experiments/replay/corridas/). `T_A`, `L_R` y `L_C` son segundos, salvo espera de cola en milisegundos.

| Detector | Variante | Vishing SC: `T_A / L_R / L_C` | Legítima LG: falsa alarma / `T_A` | p50 detector | espera cola máxima |
|---|---|---|---:|---:|---:|
| Reglas | mono | 17,821 / −4,608 / +0,209 | Sí / 5,292 | 11,4 ms | 0,0 ms |
| 0.8B | mono | 14,956 / −1,743 / +3,074 | Sí / 12,923 | 1.952,9 ms | 1.461,2 ms |
| 0.8B | estéreo | 20,185 / −6,972 / −2,155 | Sí / 18,105 | 1.299,3 ms | 2.497,1 ms |
| 2B | mono | 21,813 / −8,600 / −3,783 | Sí / 9,441 | 5.227,3 ms | 4.634,9 ms |
| 2B | estéreo | 29,068 / −15,855 / −11,038 | No / — | 5.150,9 ms | 17.377,3 ms |

En 3/4 configuraciones SLM hubo falsa alarma en la única legítima LG-WA-CONSULTA-01 TTS. En texto manual A/B el 2B no había alertado ese caso; en el replay mono, sin etiquetas de hablante, trató «Me llegó por SMS un código…» como solicitud. Esta es una observación de un par TTS, no un efecto demostrado. La segmentación estéreo partió frases y generó segmentos `.`; el 2B estéreo avisó a 29,1 s, después de terminar el audio, con una cola máxima de 12,9 s. Los resúmenes de ASR dan RTF mono 0,171/0,103 (SC/LG) y estéreo 0,063/0,066; referencias y detalle en [E2E](../../experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md).

## Diferencias observadas por candidato

- **Reglas:** comportamiento rápido en Windows GPU/M1 y recall de 23/29, pero 14/24 negativos difíciles recibieron alerta. En `piloto_escrito`, 7/7 legítimas dispararon en reglas; en `trampa`, 6/7. Véanse [desglose por grupo](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md) y casos completos en [corrida de reglas](../../experiments/slm-directo/corridas/2026-10-13_224418_linea-base-reglas/resumen.md).
- **0.8B:** recall alto en escrito Windows (26/29) y menos falsas alarmas que reglas, pero falsos avisos por contexto en casos como `TR-01-pedido-indirecto-digitos`; la revisión automática marcó 12/34 motivos de aviso como pedido inventado. En 2/4 corridas E2E TTS alarmó la legítima.
- **2B:** menos falsas alarmas en texto (2/24 en ambas corridas Windows; 2/24 en M1), pero recall escrito de 20–21/29 y avisos tardíos en varios casos; en `TR-05-asado-con-transferencia` Windows y M1 desplazaron el aviso entre líneas. La revisión de motivos halló 13/22 pedidos reales descritos correctamente y 6/22 mal descritos. El 2B cambió decisiones en 2/53 casos entre dos corridas Windows.
- **4B:** recall de 29/29 en Windows y falsas alarmas 15/24; los revisores automáticos describieron 21/44 avisos como sospecha sin pedido, compatible con avisos tempranos pero también con falsos positivos en relatos/escenarios legítimos. La corrida M1 quedó incompleta (42/53) por presión de memoria y no puede usarse para un total comparable.

Las clasificaciones de motivos son auxiliares automáticas sin revisión humana: [fundamento de avisos](../../experiments/slm-directo/analisis/2026-10-14-fundamento-de-avisos/README.md). Los casos se citan como ejemplos del material de desarrollo, no como evidencia generalizable.

## Qué falta para decidir D09

1. Completar el piloto con voces humanas y referencias revisadas/adjudicadas, manteniendo comparaciones pareadas texto manual frente a ASR.
2. Separar configuración en desarrollo de un test reservado y congelar el procedimiento antes de evaluarlo ([D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)).
3. Medir el pipeline en Android objetivo: RTF conjunto, latencia p95 por turno, memoria RSS conjunta, hilos, estabilidad, batería y temperatura. Los perfiles PC/M1 no sustituyen esa medición.
4. Acordar en equipo qué equilibrio entre pedidos perdidos, falsos avisos y oportunidad temporal es aceptable; estos resultados no seleccionan una política de alerta.
