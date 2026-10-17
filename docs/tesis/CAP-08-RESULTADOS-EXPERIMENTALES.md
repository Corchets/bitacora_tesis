> **Estado: borrador.** Redactado el 2026-10-17 con resultados de DESARROLLO; el capítulo final se reescribe con piloto y test reservado.

# Capítulo 8: Resultados experimentales

Este capítulo reúne las mediciones disponibles para orientar la preparación del piloto. El material consiste en 53 casos escritos por el equipo, sin revisión humana de las referencias para este análisis, y dos conversaciones sintetizadas con TTS para el humo de ASR y replay. No constituye el corpus final ni un test reservado. Las decisiones [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico), [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) permanecen abiertas.

## 8.1. Material de desarrollo

El conjunto escrito contiene 29 casos etiquetados como vishing y 24 negativos difíciles. Se compararon reglas y Qwen3.5 0.8B, 2B y 4B bajo un prompt de tarea y con hablantes A/B. Los casos pertenecen a grupos `laboratorio`, `piloto_escrito` y `trampa`; no se incluyen legítimas cotidianas. La tabla maestra de conteos, porcentajes e intervalos Wilson está en [la salida de métricas de desarrollo](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md).

Las corridas principales sobre los 53 casos son del 2026-10-13 y 2026-10-14. Usaron seed 42 para los modelos; reglas no tienen aleatoriedad. La corrida CPU de dos hilos del 2026-10-14 cubrió un subconjunto distinto de 14 casos (7 vishing y 7 legítimas), también con seed 42; no se combina con las tasas de 53 casos. El manifiesto de cada corrida conserva hardware, modelo/runtime y configuración. Por ejemplo: [reglas](../../experiments/slm-directo/corridas/2026-10-13_224418_linea-base-reglas/manifiesto.json), [0.8B](../../experiments/slm-directo/corridas/2026-10-14_173532_demo-qwen3.5-0.8b/manifiesto.json), [2B primera repetición](../../experiments/slm-directo/corridas/2026-10-14_172930_demo-qwen3.5-2b/manifiesto.json), [2B segunda repetición](../../experiments/slm-directo/corridas/2026-10-14_175451_demo-qwen3.5-2b/manifiesto.json) y [4B](../../experiments/slm-directo/corridas/2026-10-14_174602_demo-qwen3.5-4b/manifiesto.json). Los hashes y el estado de limpieza se registran allí; los modelos 0.8B/4B y varias corridas aparecen con cambios locales en la carpeta en el momento de captura.

La corrida M1 se efectuó el 2026-10-17 con seed 42, Apple M1, 8 GB, Ollama/Metal y GGUF. Su manifiesto identifica commit `ffe934342173adbca438d9b7d711ecccee77e757` y árbol limpio. El 4B se interrumpió tras 42 de 53 casos; el motivo registrado fue presión de memoria (swap de 15 GB y 3,5 GB libres en disco, con otra VM activa). Los detalles se conservan en [manifiesto M1](../../experiments/slm-directo/corridas/2026-10-17_150516_m1-gguf/manifiesto.json) y [comparación M1–Windows](../../experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/README.md). Por eso no se trata su resultado M1 como medición completa.

## 8.2. Benchmark de humo de ASR

Se ejecutaron Zipformer y Whisper sobre el audio TTS de SC-WA-CODE-01, y Zipformer sobre LG-WA-CONSULTA-01. El [resumen comparativo de desarrollo](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md#asr-sobre-audio-tts) presenta RTF, memoria, WER y manifiestos. En SC, Zipformer obtuvo WER 4,35% (2 errores de 46 palabras) y RTF 0,171; Whisper obtuvo WER 17,39% (8/46) y RTF 0,2745. En LG, Zipformer registró WER 5% (2/40) y RTF 0,1032. Los manifiestos detallan los errores por término crítico.

La corrida de humo se hizo el 2026-10-17, con commit `b29ff73e863e388904703e0181a2d6f6d773c7f1`, según los [resúmenes Zipformer](../../experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_zipformer/resumen.md) y [Whisper](../../experiments/asr-local/corridas/2026-10-17_humo_sc_wa_code_01_whisper/resumen.md). Se trata de síntesis por TTS, con dos voces y pausas artificiales; no estima WER en voces humanas ni basta para elegir ASR.

## 8.3. Comparación de detectores sobre texto escrito

En las dos corridas completas de Windows, las reglas detectaron 23/29 casos de vishing (79,3%) y alertaron en 14/24 negativos difíciles (58,3%). Qwen3.5 0.8B detectó 26/29 (89,7%) y alertó en 8/24 (33,3%). El 2B detectó 20/29 y 21/29 en sus dos repeticiones (69,0% y 72,4%), con 2/24 falsas alarmas en ambas. El 4B detectó 29/29 (100%), con 15/24 falsas alarmas (62,5%). Los intervalos Wilson y resultados restantes constan en [metricas.md](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md).

El subconjunto de negativos difíciles expone diferencias entre grupos. En `piloto_escrito`, reglas alertaron en 7/7 legítimas, frente a 0/7 en cada repetición 2B; en `trampa`, 2B alertó en 2/7. El 4B alertó en 6/7 casos `trampa`. La clasificación automática de motivos halló 12/34 avisos 0.8B con pedidos inventados; para 2B, 13/22 avisos describieron bien un pedido real y 6/22 lo describieron mal; 21/44 avisos 4B se clasificaron como sospecha sin pedido. Esta lectura proviene de dos revisores automáticos, no de revisión humana, como explicita el [análisis de fundamento de avisos](../../experiments/slm-directo/analisis/2026-10-14-fundamento-de-avisos/README.md).

La repetición 2B en Windows, con igual configuración y seed 42, no produjo resultados idénticos: 2/53 casos cambiaron la decisión final y 60/464 líneas difirieron en riesgo numérico. En el cotejo M1–Windows el acuerdo de decisión final fue 51/53 para 0.8B y 52/53 para 2B. Son señales de variación entre ejecuciones/plataformas en este conjunto; no estiman una tasa general de reproducibilidad. Los datos caso por caso están en el [análisis M1–Windows](../../experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/README.md).

## 8.4. Texto escrito frente a ASR

El contraste disponible es exploratorio y se limita al par TTS de WhatsApp. En el texto escrito con hablantes A/B, la corrida 2B no disparó falsa alarma en LG-WA-CONSULTA-01. En el replay mono con Zipformer, donde el detector no recibe los hablantes (`--hablantes sin`), 2B sí alertó sobre «Me llegó por SMS un código…». Por tanto, la salida del pipeline cambió de no alerta a alerta para esta legítima concreta. En el replay, 2B también detectó SC-WA-CODE-01, pero después del pedido y del cumplimiento simulados (márgenes negativos). Se informan estos resultados como una observación del par, no como efecto atribuible solo al ASR: también cambiaron el canal de entrada, la segmentación y el contexto de hablantes. Fuente: [resumen E2E](../../experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md) y sus [manifiestos/eventos](../../experiments/replay/corridas/2026-10-17_e2e-zipformer-2b-q8_0-mono-lg_wa_consulta_01/).

## 8.5. Detección temprana y latencia

En texto, los avisos se registran por línea, no se convierten a segundos. Para el 2B, la mediana de margen al pedido fue cero líneas en las corridas de desarrollo; con el criterio candidato de una línea de anticipación, 2/28 casos evaluables cumplieron ese margen. Para reglas fueron 5/28 y para 4B 17/28. Los límites temporales y el denominador están en [métricas](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md); la marca de pedido falta para un caso vishing.

En el replay E2E la latencia incluye ASR, evaluación y cola secuencial. El 2B mono sobre SC emitió aviso en `T_A=21,813 s`, con `L_R=−8,600 s` y `L_C=−3,783 s`. En estéreo emitió a `T_A=29,068 s`, con `L_R=−15,855 s` y `L_C=−11,038 s`; su espera máxima de cola fue 12.908,1 ms, posterior al fin del audio. La variante mono 0.8B sobre SC dio `T_A=14,956 s`, `L_R=−1,743 s` y `L_C=+3,074 s`. Estas marcas `T_R/T_C` provienen del guion TTS y no de anotación humana. La [tabla E2E](../../experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md) incluye configuraciones, p50 y cola de las demás variantes.

Durante la verificación de la integración se detectaron y corrigieron dos defectos: replay no pasaba `pensar=False` y una comparación incluía casos no evaluados. Las corridas inválidas se descartaron y no están en el repositorio; los cambios correctivos se identifican con commit `b082b6d`. Las cifras presentadas corresponden a las corridas conservadas posteriores a esa corrección, según manifiestos y resumen E2E.

## 8.6. Falsas alarmas en negativos difíciles

Sobre los 24 negativos difíciles, la tasa observada fue 14/24 (58,3%) para reglas, 8/24 (33,3%) para 0.8B, 2/24 (8,3%) para ambas repeticiones del 2B y 15/24 (62,5%) para 4B en Windows. Son proporciones de una muestra construida y balanceada; no representan la frecuencia de llamadas legítimas en uso. Entre ejemplos concretos, reglas alertaron en los 7 casos del grupo `piloto_escrito`; 2B evitó alertar esos siete, pero dio falsas alarmas en 2/7 `trampa`. El desglose completo y los IC Wilson están en [métricas de desarrollo](../../experiments/metricas/salidas/2026-10-17-desarrollo/metricas.md).

En la única legítima TTS de replay, LG-WA-CONSULTA-01, el 0.8B dio alerta en mono y estéreo; 2B alertó en mono, pero no en estéreo. Esta diferencia acompaña el problema observado de segmentación por canal y cola, y no debe extrapolarse a llamadas reales ([resumen E2E](../../experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md)).

## 8.7. Rendimiento por hardware

En Windows GPU, los p95 de latencia por línea fueron 706 ms para 0.8B, 1.118 y 1.133 ms en las dos corridas 2B y 1.646 ms para 4B. La regla quedó en 18 ms. En el equipo Apple M1, los p95 fueron 3.462 ms para 0.8B, 6.036 ms para 2B y 10.186 ms para el subconjunto incompleto 4B. Las medianas/p95 y los denominadores de comparación están en [análisis M1–Windows](../../experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/README.md); la fuente de métricas para M1 es [metricas.md](../../experiments/metricas/salidas/2026-10-17-m1/metricas.md).

En Windows CPU forzado a dos hilos y sobre 14 casos (7 vishing y 7 legítimas), el resumen registra para 0.8B p50/p95 de 3.913/7.331 ms y para 2B 8.216/12.956 ms. Ambos exceden el objetivo p95 de 1,5 s de [prefactibilidad](../investigacion/PREFACTIBILIDAD-TECNICA.md). Las corridas son de PC, no del perfil Android objetivo. En M1, solo reglas quedó por debajo de 1,5 s p95; los modelos 0.8B, 2B y el subconjunto 4B lo excedieron. El replay E2E también muestra colas acumuladas para los SLM, particularmente 2B estéreo. No se hizo una corrida de estabilidad de 30 minutos ni se midió el perfil conjunto dentro de los límites de memoria por perfil.

## 8.8. Pendientes del capítulo

La **descripción final del corpus** queda pendiente porque las 53 conversaciones son material de desarrollo, sus referencias no tuvieron revisión humana en esta comparación y todavía faltan piloto, adjudicación, composición final y particiones sin fuga. En consecuencia, estos resultados tampoco describen desempeño de test reservado.

Las **ablations y el rendimiento móvil** quedan pendientes porque no hay ablaciones controladas sobre el corpus piloto ni mediciones en Android de RTF conjunto, latencia, memoria, batería y temperatura. El 4B M1 incompleto no reemplaza una medición móvil. Una vez ejecutados piloto y test con el protocolo congelado, este capítulo deberá reconstruir tablas desde las salidas versionadas, añadir incertidumbre adecuada y revisar la interpretación con el equipo.
