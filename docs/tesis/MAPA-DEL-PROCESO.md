# Mapa del proceso

**Cómo usarlo.** Es el punto de entrada para quien redacte el informe final, persona o agente. Cuenta las etapas del
proyecto en orden: qué pregunta respondió cada una, qué evidencia la sostiene y qué dejó. Cada etapa enlaza la corrida
o el análisis que vale, con un nombre legible al lado de la carpeta. Las cifras de acá son solo las clave, para
ubicarse: las completas, con su contexto, están en las corridas y los [hallazgos](../hallazgos/README.md) enlazados.
Estado al 2026-11-21. Lo que salió en la poda del 2026-11-21 está en el tag `archivo/pre-informe`.

## 1. El proceso en una página

**Septiembre: del clasificador al SLM.** El laboratorio dejó TF-IDF por un LLM/SLM local y probó encoders (RoBERTuito)
y una cascada encoder → Llama 1B, que empeoró al encoder solo (E0). En octubre el SLM pasa a leer toda la
transcripción en cada línea.

**Octubre: qué modelo y a qué costo.** Las reglas de palabras clave son la vara: detectan casi todo, pero avisan en la
mayoría de las legítimas (E1). En la escalera de Qwen 3.5, más grande no fue mejor: el 0.8B inventa pedidos, el 4B
avisa por sospecha y el 2B avisa por la razón correcta, pero tarde. En CPU ninguno llega a tiempo (E2). Las decisiones
se reproducen entre máquinas; los tiempos no, y la caché del prefijo es la palanca de latencia (E3). La primera
integración con audio anda de punta a punta (E4). El prompt v2, escrito mirando los 53 casos, no generalizó al corpus
nuevo: es el primer sobreajuste al desarrollo y el origen de escribir las reglas antes de correr (E5). Combinar
detectores no alcanza la meta (E6). Para no consultar al SLM en cada línea se probó **Tito**, un clasificador liviano
que lo despierta, y la matriz #101 eligió Gemma 4 E2B con Tito viejo (E7). Pedirle al modelo menos salida bajaba el
tiempo; el reranker zero-shot mide tema, no intención, y se descartó (E8). Con voz real, Zipformer transcribía mal y
entró Parakeet con filtro Silero (ADR 0001); la demo por Meet anda, pero E2B tarda unos 3,7 s por consulta (E9).

**Noviembre: limpiar el detector.** En los 150 casos de desarrollo, E2B con Tito no llega a la meta del equipo;
repetir una corrida mueve 1 o 2 casos, y el indicio de Tito hace perder estafas (E10). Retocar el prompt (v3, v4, v5)
ya casi no mueve nada: el caso explica la variación, no la condición (E11). Las falsas alarmas que «evitaba» Tito eran
punto ciego, y Tito sale (E12). En el Samsung A56, el JSON completo tarda 7,85 s por actualización (E13). Leer la
probabilidad del primer token no sirve como puntaje (E14). La segunda vuelta de #143 fija lo que queda: el alcance
(entrantes de números no agendados), la salida cortada tras el riesgo, el prompt C que pregunta por la intención y avisa
antes del pedido, la consulta solo en los turnos de la otra persona y la configuración congelada (E15). En el A56 baja a
3,6 s por línea; mostrar el aviso sin esperar el motivo baja el primer aviso a 3,7 s, y cualquier cambio del runtime
mueve el riesgo (E16). E2B como ASR pierde contra Parakeet (E17). La revisión de producto no elige ninguna variante por
regla y Mateo adopta `c-consejos` (E18).

**Cierre: medir una vez y mirar afuera.** La evaluación final corre una sola vez: avisa a tiempo en dos de cada tres
estafas de test y avisa todas las coreanas reales, pero también avisa en el 27 % de las legítimas generadas y en el 64 % de las
reales. Los datos generados sobreestiman cuánto acierta con las legítimas (E19). Después, ningún prompt baja las
falsas alarmas reales sin perder estafas, la misma configuración corrida en otro orden mueve hasta 6 casos, y una regla
de pedido crítico sumada al modelo sube los avisos a tiempo como exploración (E20). En un iPhone 15 Pro Max el detector
tarda 0,79 s por línea, entra junto con el ASR, y generando solo el número baja a 0,54 s (E21).

## 2. Las etapas

Rutas: `corridas/` y `analisis/` son de `experiments/slm-directo/`. «Desarrollo» son casos generados que se usaron
para elegir; «test» es la reserva, que se miró una sola vez (E19).

### E0. Laboratorio de septiembre: encoders y cascada (2026-09-24 → 2026-09-28)

- **Pregunta:** ¿un encoder en español, solo o seguido de un SLM chico, distingue estafa de legítima?
- **Evidencia:** [contraste entre el marco NLP y el laboratorio](../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md)
  y los CSV de [`laboratorio/resultados/`](../../experiments/laboratorio/resultados/GLOSARIO-COLUMNAS.md)
  (2026-09-24 encoders, 2026-09-28 cascada RoBERTuito → Llama 3.2 1B).
- **Dejó:** la cascada empeoró al encoder solo (goteo 12/16 → 7/16, las mismas 5/10 falsas alarmas) y el SLM tardó
  ~3,9 s por turno. El 2026-09-25 el laboratorio había dejado TF-IDF por un LLM/SLM local
  ([bitácora 2026-09 semana 4](../gestion/bitacora/2026-09-semana-04.md)); en octubre nace `slm-directo` (E1, E2).
- **Registro:** CAP-06 (antecedente), [ARQUITECTURA](../ingenieria/ARQUITECTURA.md).

### E1. Línea base de reglas (2026-10-13 → 2026-10-21)

- **Pregunta:** ¿hasta dónde llegan las reglas de palabras clave del laboratorio?
- **Evidencia:** reglas en los 53 casos cortos,
  [`2026-10-13_224418_linea-base-reglas`](../../experiments/slm-directo/corridas/2026-10-13_224418_linea-base-reglas/resumen.md);
  en los 150, [`2026-10-21_200147_m1-reglas-150`](../../experiments/slm-directo/corridas/2026-10-21_200147_m1-reglas-150/resumen.md).
  La repetición en la M1 ([`2026-10-17_150455_m1-reglas`](../../experiments/slm-directo/corridas/2026-10-17_150455_m1-reglas/resumen.md))
  da lo mismo.
- **Dejó:** 23/29 estafas y 14/24 falsas alarmas en los 53; 65/75 y 51/75 en los 150; p95 de 18 ms. Avisan por
  palabra suelta, sin distinguir mención de pedido. Es la referencia simple que se corre también en la evaluación final.
- **Registro:** CAP-07 (RNF-03), CAP-08, [comparación de candidatos](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md).

### E2. Escalera Qwen 3.5: ¿más grande es mejor? (2026-10-14)

- **Pregunta:** ¿desde qué tamaño un SLM que lee la llamada línea por línea distingue el pedido de la sospecha, y
  cuánto cuesta?
- **Evidencia:** 53 casos, en Windows con GPU: 0.8B
  [`2026-10-14_173532_demo-qwen3.5-0.8b`](../../experiments/slm-directo/corridas/2026-10-14_173532_demo-qwen3.5-0.8b/resumen.md),
  2B [`2026-10-14_172930_demo-qwen3.5-2b`](../../experiments/slm-directo/corridas/2026-10-14_172930_demo-qwen3.5-2b/resumen.md)
  y su repetición [`2026-10-14_175451_demo-qwen3.5-2b`](../../experiments/slm-directo/corridas/2026-10-14_175451_demo-qwen3.5-2b/resumen.md),
  4B [`2026-10-14_174602_demo-qwen3.5-4b`](../../experiments/slm-directo/corridas/2026-10-14_174602_demo-qwen3.5-4b/resumen.md);
  [en qué se apoya cada aviso](../../experiments/slm-directo/analisis/2026-10-14-fundamento-de-avisos/README.md);
  latencia sin GPU, [`2026-10-14_191429_cpu-2hilos`](../../experiments/slm-directo/corridas/2026-10-14_191429_cpu-2hilos/resumen.md).
- **Dejó:** 0.8B 26/29 · 8/24 (inventa pedidos); 2B 20/29 · 2/24 (19 de 22 avisos por la razón correcta); 4B 29/29 ·
  15/24 (avisa por sospecha). En CPU con 2 hilos, p95 de 7,3 s (0.8B) y 13,0 s (2B). Las dos corridas del 2B valen:
  la repetición es la evidencia de que temperatura 0 no garantiza la misma salida (20/29 contra 21/29).
- **Registro:** CAP-06 (no determinismo), CAP-07 (latencia en CPU), antecedente de [H02](../hallazgos/H02-ruido-entre-corridas.md).

### E3. Reproducibilidad entre máquinas y caché del prefijo (2026-10-17 → 2026-10-21)

- **Pregunta:** ¿las cifras se sostienen en otra máquina? ¿Ollama reprocesa toda la transcripción en cada línea?
- **Evidencia:** escalera en la M1, [`2026-10-17_150516_m1-gguf`](../../experiments/slm-directo/corridas/2026-10-17_150516_m1-gguf/resumen.md)
  (el 4B se cortó por swap); [M1 contra Windows](../../experiments/slm-directo/analisis/2026-10-17-m1-vs-windows/README.md);
  [caché del prefijo](../../experiments/slm-directo/analisis/2026-10-21-cache-prefijo/README.md) con
  [`2026-10-21_182201_m1-0.8b-v1v2-nb32`](../../experiments/slm-directo/corridas/2026-10-21_182201_m1-0.8b-v1v2-nb32/resumen.md).
- **Dejó:** el aviso coincide entre máquinas en 51/53 (0.8B) y 52/53 (2B); el tiempo no (0.8B: p50 1282 ms en la M1
  contra 276 ms en Windows). Con `num_batch` 32 se reutiliza el prefijo y la mediana por línea baja de 1282 a 1017 ms.
- **Registro:** [MAPA-DECISIONES D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector), REGISTRO-RIESGOS (swap en la M1).

### E4. Primera integración con audio: ASR → replay → aviso (2026-10-17)

- **Pregunta:** ¿el recorrido completo anda con audio, y dónde se atrasa?
- **Evidencia:** [resumen de los replays de punta a punta](../../experiments/replay/corridas/2026-10-17_RESUMEN-E2E.md)
  (audio TTS, Zipformer, reglas y Qwen 0.8B/2B, en la M1), con las corridas de humo de
  [`asr-local/corridas/`](../../experiments/asr-local/corridas/) del mismo día.
- **Dejó:** el recorrido anda; con el 2B en estéreo el detector queda atrasado respecto del audio. Son una o dos
  llamadas TTS: muestran el mecanismo, no rendimiento.
- **Registro:** CAP-07 §7.4, [comparación de candidatos](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md).

### E5. Corpus v2 y prompt v2: el primer sobreajuste (2026-10-21 → 2026-10-23)

- **Pregunta:** ¿un prompt que corrige los errores vistos (v2) mejora? ¿Y en casos que no se miraron?
- **Evidencia:** [diseño del corpus v2](../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md) (97 de desarrollo y 200
  reservadas); [errores del v1 y diseño del v2](../../experiments/slm-directo/analisis/2026-10-21-errores-y-prompt-v2/README.md);
  en los 53, 4B [`2026-10-22_103341_win-4b-v1v2-nb32`](../../experiments/slm-directo/corridas/2026-10-22_103341_win-4b-v1v2-nb32/resumen.md);
  en corpus v2, [`2026-10-23_144554_linux-4b-v1v2-cv2-nb32`](../../experiments/slm-directo/corridas/2026-10-23_144554_linux-4b-v1v2-cv2-nb32/)
  y las de 9B, 2B y 0.8B que lista la tabla de [CAP-08 §8.3.2](CAP-08-RESULTADOS-EXPERIMENTALES.md).
- **Dejó:** en los 53, el 4B con v2 baja las falsas alarmas de 15/24 a 3/24. En corpus v2, el 4B con v2 cae a 14/46
  estafas (con v1, 39/46). v2 se escribió mirando los 53 y no generalizó. De ahí sale la práctica de escribir la regla
  antes de correr ([ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)).
- **Registro:** CAP-08 §8.3.2. Las carpetas `linux-*` no tienen `resumen.md`: las cifras están en CAP-08.

### E6. Pasada 0: combinar detectores guardados (2026-10-21 → 2026-10-23)

- **Pregunta:** ¿combinar reglas y SLM, con umbrales y persistencia, llega a la meta de entonces (95/5)?
- **Evidencia:** [pasada 0](../../experiments/slm-directo/analisis/2026-10-21-pasada-0/README.md).
- **Dejó:** ninguna de las 517 configuraciones llega a 95/5 en la selección. Combinar no reemplaza un mejor detector.
- **Registro:** CAP-08.

### E7. Tito como filtro y matriz #101: se elige Gemma 4 E2B (2026-10-26 → 2026-10-30)

- **Pregunta:** ¿un filtro liviano (Tito: RoBERTuito congelado más regresión logística) que solo despierta al SLM ante
  algo sensible baja consultas y falsas alarmas sin perder estafas? ¿Con qué modelo?
- **Evidencia:** primera vuelta, 6 modelos × 8 casos:
  [consolidado del 2026-10-26](../../experiments/slm-directo/analisis/2026-10-26-tito-slm-consolidado/CONSOLIDADO.md)
  (sus corridas están en el tag). **La que vale es la matriz #101**, que repite la pregunta con 10 modelos × 20
  conversaciones × 3 condiciones: [informe de la matriz #101](../../experiments/slm-directo/corridas/2026-10-30_112956_101_informe_101.md)
  (archivos sueltos `2026-10-30_112956_101_*`).
- **Dejó:** `gemma4:e2b` con Tito viejo, 10/10 estafas y 0/10 falsas alarmas (directo, 10/10 y 1/10). Es la elección
  del detector. Son 20 conversaciones de corpus v2: E10 muestra que no representan todo el desarrollo.
- **Registro:** CAP-08 §8.3.1, [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) (versión
  anterior), [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

### E8. «Riesgo primero» y reranker zero-shot (Evaristo, 2026-10-29 → 2026-10-31)

- **Pregunta:** ¿baja la latencia si el modelo escribe solo el riesgo? ¿Un cross-encoder o NLI sirve como detector,
  filtro o verificador?
- **Evidencia:** [riesgo primero](../../experiments/slm-directo/analisis/2026-10-29-riesgo-primero/README.md) con
  [`2026-10-29_182016_rapida-gemma3n-e2b`](../../experiments/slm-directo/corridas/2026-10-29_182016_rapida-gemma3n-e2b/resumen.md);
  [reranker zero-shot](../../experiments/slm-directo/analisis/2026-10-30-reranker-zero-shot/README.md), con hipótesis
  escritas antes (corridas `r1-bge`, `r1-bge-resto`, `r3-riesgo-seleccion`).
- **Dejó:** escribir solo el riesgo es 5,2× más rápido en CPU (p50 1918 contra 10 036 ms por línea), pero ese riesgo
  no alcanza como señal con gemma3n. El reranker mide tema, no intención: se descarta la familia cross-encoder/NLI. La
  idea de pedir menos salida vuelve en E15 y E21.
- **Registro:** CAP-08; antecedente de ADR 0006 y ADR 0009.

### E9. Voz real: elección del ASR y demo en vivo (2026-10-26 → 2026-11-03)

- **Pregunta:** ¿qué ASR transcribe bien la voz real, en el dispositivo y mientras se habla? ¿La demo anda con una
  llamada de verdad?
- **Evidencia:** [plan de voz real](../../experiments/asr-local/PLAN-VOZ-REAL.md) (Zipformer, cortes, Silero contra RMS);
  [A contra B con diálogos](../../experiments/asr-local/corridas/2026-11-02_voz-real_dialogos-a-contra-b/resumen.md);
  [corrida con voz real por Meet](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md), con la
  [demora de E2B](../../experiments/voip/corridas/2026-11-02-medicion-84-e2b/) (#84) y el
  [panel con E2B](../../experiments/voip/corridas/2026-11-02-tito-gemma4-panel.md).
- **Dejó:** Zipformer se retiró el 2026-10-29. Parakeet con corte RMS y Silero solo como filtro (opción B) gana a
  Silero solo: WER 25,6 % contra 32,8 %. Nueve llamadas guionadas con dos voces muestran que el recorrido anda; E2B tarda
  3,74 s de mediana por consulta en la M1 (p95 4,53 s). El audio original se perdió el 2026-11-02.
- **Registro:** [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) (hoy fija solo el
  ASR), CAP-05, CAP-06, CAP-07 §7.4.3.

### E10. E2B en los 150, el indicio de Tito y el ruido entre corridas (2026-11-04)

- **Pregunta:** ¿la configuración del ADR 0001 se sostiene en los 150 casos de desarrollo? ¿Cuánto mueve repetir?
- **Evidencia:** [`2026-11-04_003715_e2b-tito-viejo-150`](../../experiments/slm-directo/corridas/2026-11-04_003715_e2b-tito-viejo-150/analisis.md)
  y **la que vale para los hallazgos**,
  [`2026-11-04_sin-indicio-150`](../../experiments/slm-directo/corridas/2026-11-04_sin-indicio-150/conclusiones.md)
  (SLM solo, Tito con y sin indicio, y una repetición). `2026-11-04_132229_e2b-directo-150` es el SLM solo corrido
  antes, en otra sesión; para los hallazgos valen las condiciones a y c.
- **Dejó:** Tito viejo → E2B, 51/75 · 13/75, y 0/11 estafas sin pedido. Repetir mueve 1 o 2 casos. Con el indicio de
  Tito se pierden 5 estafas (50/75 contra 54/75 sin indicio). Aparecen las estafas sin pedido.
- **Registro:** [H01](../hallazgos/H01-corpus-v2-se-lee-aparte.md), [H02](../hallazgos/H02-ruido-entre-corridas.md),
  [H05](../hallazgos/H05-estafas-sin-pedido.md), [H07](../hallazgos/H07-indicio-de-tito-pierde-estafas.md);
  [revisión ciega de #145](../corpus/REVISION-CIEGA-145.md).

### E11. Prompts v3, v4 y v5: cuándo dejar de retocar (2026-11-04 → 2026-11-05)

- **Pregunta:** ¿un prompt mejor (cita al final, roles, maniobras) sube la detección sin sumar falsas alarmas?
- **Evidencia:** el análisis unificado vive en
  [`2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md`](../../experiments/slm-directo/corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md),
  con [`2026-11-04_201116_prompt-v3-b-tito-sin-indicio`](../../experiments/slm-directo/corridas/2026-11-04_201116_prompt-v3-b-tito-sin-indicio/resumen.md),
  `2026-11-04_prompt-v4-tito-sin-indicio`, `2026-11-04_tanda-roles-tito-sin-indicio` y
  [`2026-11-05_prompt-v5-tito-sin-indicio`](../../experiments/slm-directo/corridas/2026-11-05_prompt-v5-tito-sin-indicio/analisis.md).
- **Dejó:** v3 sube a 64/75 con 35/75 falsas alarmas, y la causa era el orden de los campos. v4 con roles da 55/75 ·
  13/75, y da lo mismo caso por caso cada vez que se repitió. v5 no supera a v4.
  Entre 14 condiciones, el caso explica el 82 % de la variación y la condición el 2 %.
- **Registro:** [propuesta de configuración](../evaluacion/PROPUESTA-CONFIGURACION-DETECTOR.md),
  [H06](../hallazgos/H06-v4-avisa-mas-tarde-y-cita-mejor.md) (superado por H10),
  [fallas y corpus](../../experiments/slm-directo/casos/FALLAS-Y-CORPUS-2026-11-05.md).

### E12. Tito sale del detector (2026-11-05 → 2026-11-06)

- **Pregunta:** ¿las falsas alarmas que Tito «evita» son filtrado o punto ciego?
- **Evidencia:** [Tito viejo 2.0 con v4](../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/analisis.md);
  [comparación de Tito viejo 2.0 con v1](../../experiments/slm-directo/analisis/2026-11-05-TITO-VIEJO-2-COMPARACION.md)
  (sale del ZIP de Colab `corridas/2026-11-05_TITO-VIEJO-2-COLAB.zip`);
  [Tito como compuerta de lo sensible](../../experiments/slm-directo/analisis/2026-11-06-tito-compuerta-sensible/README.md).
- **Dejó:** Tito 2.0 no cambia nada (55/13); sin Tito, 56/17. Las 7 legítimas cuya falsa alarma desaparece con Tito
  son punto ciego: el SLM avisaba en una línea sensible que Tito puntuó casi en cero. Cuando aparece la primera línea
  sensible, el SLM ya está despierto en 62 de 64 estafas y en 14 de 43 legítimas. Tito se entrenó como clasificador de
  estafas y tenía que ser una compuerta de lo sensible.
- **Registro:** [H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md),
  [H09](../hallazgos/H09-tito-clasificador-en-vez-de-compuerta.md), CAP-05 §5.5.1; trabajo futuro en #149.

### E13. Primera medición en teléfono: Samsung A56 (2026-11-06)

- **Pregunta:** ¿la configuración del ADR 0001 entra y llega a tiempo en un teléfono de gama media?
- **Evidencia:** [diagnóstico del A56](../../experiments/slm-directo/corridas/2026-11-06-a56-diagnostico.md) (archivos
  sueltos `2026-11-06-a56-*`; Tito viejo 2.0, v4, JSON completo, 20 conversaciones).
- **Dejó:** 7,85 s por actualización de mediana (p95 14,63 s) y 3,39 GiB de pico para Gemma. El JSON completo no entra
  en el presupuesto de tiempo: motiva E14 a E16.
- **Registro:** REGISTRO-RIESGOS, [bitácora 2026-11 semana 1](../gestion/bitacora/2026-11-semana-01.md).

### E14. #143, primera vuelta: el primer token como puntaje (2026-11-06)

- **Pregunta:** ¿leer la probabilidad del «SÍ» en el primer token da un puntaje continuo que avise antes y más rápido?
- **Evidencia:** [`2026-11-05_puntaje-token-150`](../../experiments/slm-directo/corridas/2026-11-05_puntaje-token-150/analisis.md)
  (corrió el 2026-11-06; trae repeticiones `-rep`).
- **Dejó:** el token detecta menos que el JSON en corpus v2 (26 contra 29 de 46, con 7 falsas alarmas). No se adopta.
- **Registro:** [H03](../hallazgos/H03-el-slm-avisa-en-el-pedido.md) (superado por H10),
  [H04](../hallazgos/H04-riesgo-escrito-no-es-puntaje.md).

### E15. #143, segunda vuelta: alcance, corte del JSON, prompt C y configuración congelada (2026-11-06 → 2026-11-10)

- **Pregunta:** ¿qué detector se congela para la evaluación final, decidiendo cada cosa con una regla escrita antes?
- **Alcance y corpus:** el detector corre solo en llamadas entrantes de números no agendados
  ([ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md)); se escriben legítimas entrantes
  nuevas, 94 de desarrollo y 56 de test ([ADR 0004](../ingenieria/adr/0004-legitimas-entrantes-nuevas-y-test-aparte.md)).
  Desde acá «desarrollo» es `alcance-140`: 46 estafas de corpus v2 y esas 94 legítimas.
- **Evidencia, en orden:**
  - etapa 1, [`2026-11-06_puntaje-token-2`](../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/README.md):
    la ganancia de tiempo sale de cortar el JSON, no de leer el token. Esta carpeta guarda también `FUENTES.md`,
    `IDEAS-PENDIENTES.md` y `NOTA-GEMMA4-Y-CACHE.md`, que citan los ADR;
  - [`2026-11-07_json-cortado`](../../experiments/slm-directo/corridas/2026-11-07_json-cortado/README.md): cortar tras
    la alerta deja el riesgo igual en el 93,4 % de las líneas y la consulta baja de 406 a 286 ms (p50);
  - etapa 2, [`2026-11-07_alcance-etapa-2`](../../experiments/slm-directo/corridas/2026-11-07_alcance-etapa-2/analisis.md):
    C contra v4 dentro del alcance, 36/46 contra 28/46 estafas y 27/94 contra 42/94 falsas alarmas; la repetición lo
    sostiene;
  - etapa 3, [`2026-11-09_pedido-critico-etapa-3`](../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/README.md):
    un campo de pedido crítico baja las falsas alarmas de 27 a 18 pero pierde 4 avisos a tiempo; no se adopta. Queda C
    cortado tras el riesgo, «riesgo ≥ 0,3», solo en las líneas de OTRA;
  - [`2026-11-10_config-congelada-humo`](../../experiments/slm-directo/corridas/2026-11-10_config-congelada-humo/README.md):
    la configuración congelada corrida completa por primera vez, 36/46 · 14/36 antes del pedido · 26/36 a tiempo ·
    25/94 falsas alarmas;
  - [`2026-11-10_sensibilidad-c`](../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md): tres
    cambios chicos a C; gana `c-premisa`, 40/46 · 19/36 · 29/36 · 26/94.
- **Dejó:** C pregunta por la intención y no por el pedido: avisa antes del pedido y suma las estafas sin pedido. La
  configuración: Gemma 4 E2B solo, `c-premisa-corte-riesgo`, aviso con «riesgo ≥ 0,3», motivo solo en el primer aviso,
  consulta al cerrar cada turno de OTRA.
- **Registro:** [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md),
  [ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md),
  [ADR 0006](../ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md),
  [ADR 0007](../ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md),
  [H10](../hallazgos/H10-c-avisa-antes-del-pedido.md), CAP-05, CAP-08 §8.3.3.

### E16. Latencia de la configuración congelada en el A56 (2026-11-10 → 2026-11-11)

- **Pregunta:** ¿cuánto tarda la configuración congelada en el teléfono, y qué la acelera sin cambiar lo que decide?
- **Evidencia:** [`2026-11-10_a56-congelada-latencia`](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md)
  (solo vale por los tiempos); [`2026-11-11_a56-latencia-172`](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md)
  (propuestas de #172, 6 conversaciones de desarrollo).
- **Dejó:** 3,60 s de mediana por línea de OTRA (p95 4,90 s) y unos 11 s para el motivo. Mostrar el aviso sin esperar
  el motivo baja el primer aviso de 13,8 a 3,7 s. Lo demás que acelera (hilos, lote, caché) mueve el riesgo en algunas
  líneas: con la misma configuración el riesgo se repite, cualquier cambio del runtime lo mueve.
- **Registro:** [H11](../hallazgos/H11-el-riesgo-cambia-con-el-runtime.md), CAP-03, CAP-07, CAP-09. El A56 corrió
  `c-premisa`; nunca corrió el prompt final.

### E17. ¿E2B puede ser también el ASR? (#152, 2026-11-10)

- **Pregunta:** si Gemma 4 E2B transcribe, ¿sobra Parakeet?
- **Evidencia:** [opción B de #152](../../experiments/asr-local/corridas/2026-11-10_152-opcion-b-e2b-transcribe/resumen.md)
  (audio TTS, 155 turnos de 6 casos).
- **Dejó:** E2B pierde: WER 8,5 % contra 4,9 %, pierde cifras dictadas y tarda 2,7 s por turno en CPU contra 0,18 s.
  La opción de que E2B escuche el audio directo no se midió (trabajo futuro).
- **Registro:** [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) (alternativas), CAP-05, CAP-11.

### E18. Revisión de producto: el prompt final (preparada 2026-11-10, corrida 2026-11-18)

- **Pregunta:** ¿cuándo le sirve un aviso a la persona, y alguna variante de C avisa mejor con ese criterio?
- **Evidencia:** [`2026-11-10_revision-producto`](../../experiments/slm-directo/corridas/2026-11-10_revision-producto/README.md):
  [política de avisos](../../experiments/slm-directo/corridas/2026-11-10_revision-producto/POLITICA.md), las 94 legítimas
  revisadas una por una, tres variantes y su [análisis](../../experiments/slm-directo/corridas/2026-11-10_revision-producto/analisis.md).
- **Dejó:** ninguna variante pasa la regla, que dejaba `c-premisa`. Mateo adopta igual `c-consejos-corte-riesgo`,
  por fuera de la regla y después de ver los resultados: en desarrollo queda igual en detección (41/46, 19/36, 28/36).
- **Registro:** [ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md), CAP-08, CAP-09.

### E19. Evaluación final (corrida el 2026-11-19)

- **Pregunta:** con la configuración fijada y la regla escrita antes, ¿qué hace el detector en casos que nunca se usaron
  para elegir, y en llamadas reales?
- **Evidencia:** [`2026-11-12_evaluacion-final`](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/README.md):
  [análisis](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md),
  [resultados](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/RESULTADOS.md) y los CSV en
  `test_reservado/`, `desarrollo/` y `humo/`. Vale la pasada con el tag `colab/143-evaluacion-final-2`: la primera
  cortó en el control de desarrollo, antes de tocar el test. Lectura de los fallos:
  [qué concluir de la evaluación final](../evaluacion/CONCLUSIONES-EVALUACION-FINAL.md) (Luciano, 2026-11-20).
- **Conjuntos:** test reservado (100 estafas y 56 legítimas generadas); 33 estafas reales coreanas (KorCCVi, #144); 33
  legítimas reales de call center (CallCenterEN) y 42 de zona gris que no cuentan como falsa alarma
  ([sets externos](../../experiments/slm-directo/casos/externo/README.md)).
- **Dejó:** test, 73/100 estafas avisadas, 53/80 a tiempo y 15/56 falsas alarmas (27 %); coreanas, 33/33; legítimas
  reales, 21/33 (64 %). Las referencias simples en los mismos casos: reglas v1, 48/56 falsas alarmas en el test; v4,
  15/56. Las reglas también avisan las 33 coreanas. La ventana de 4096 tokens casi no pesó (una sola llamada llegó al
  tope).
- **Registro:** CAP-08 §8.3.4, [MAPA-DECISIONES D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

### E20. Después de la evaluación: más pruebas con los conjuntos reales (2026-11-20)

- **Pregunta:** ¿algún cambio de prompt o de política avisa menos en las legítimas reales sin perder estafas?
- **Evidencia (exploración: no reemplaza a E19 y no cambió la configuración):**
  - Mateo, [`2026-11-20_exploracion-reales`](../../experiments/slm-directo/corridas/2026-11-20_exploracion-reales/analisis.md):
    13 candidatos, ninguno pasa la regla;
  - Luciano, [`2026-11-20_mejoras-luciano`](../../experiments/slm-directo/corridas/2026-11-20_mejoras-luciano/analisis.md),
    con [la regla de pedido crítico](../../experiments/slm-directo/analisis/2026-11-20-regla-pedido-critico/README.md) y
    [dónde avisó el detector contra las fichas de Luciano](../../experiments/slm-directo/analisis/2026-11-20-detector-vs-luciano/README.md).
- **Dejó:** cambiar el prompt mueve cuánto avisa, no a quién. La misma configuración corrida en otro orden cambia el
  riesgo en el 8 % de las consultas y hasta 6 casos de una cifra. Una regla que solo mira si OTRA pide dictar un código,
  transferir o instalar, sumada al modelo, sube los avisos a tiempo del test de 53 a 64 de 80 sin sumar falsas alarmas
  (la regla se escribió después de leer los fallos). Con 16 384 tokens de contexto las coreanas se leen enteras.
- **Registro:** [H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md),
  [H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md), CAP-08 §8.3.5.

### E21. iPhone y «solo el número» (2026-11-20 → 2026-11-21)

- **Pregunta:** ¿la configuración final llega a tiempo en un teléfono de gama alta, junto con el ASR? ¿Se puede
  generar menos?
- **Evidencia:** [`2026-11-20_iphone-15-pro-max-latencia`](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/README.md);
  [`2026-11-21_iphone-15-pro-max-asr-y-detector`](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md);
  [`2026-11-21_solo-el-numero`](../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md).
- **Dejó:** con Metal, 0,79 s por línea (p95 1,03 s). Con el ASR corriendo a la vez, 1,39 GiB de pico contado por iOS,
  y la latencia del detector no empeora. Generando solo el número, la línea baja de 0,93–0,98 a 0,54 s en el iPhone, y
  las 150 conversaciones de desarrollo avisan igual y en la misma línea (en la Mac).
- **Registro:** [ADR 0009](../ingenieria/adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md), CAP-03, CAP-07,
  CAP-08, CAP-09.

## 3. Nombres que engañan

- **`win-*` del 2026-10-22 corrieron en Linux.** El `resumen.md` y el manifiesto dicen `Linux-7.2.5-3-omarchy`. Las
  `demo-qwen3.5-*` del 2026-10-14 sí corrieron en Windows.
- **`demo-qwen3.5-*` no son demos:** son las corridas completas de 53 casos de la escalera (E2).
- **La fecha de la carpeta es la de preparación, no la de la corrida:** `2026-11-05_puntaje-token-150` corrió el
  2026-11-06; `2026-11-10_revision-producto`, el 2026-11-18; `2026-11-12_evaluacion-final`, el 2026-11-19.
- **`2026-11-10_config-congelada-humo` no es solo una humo:** trae la corrida completa de la configuración congelada
  en desarrollo (36/46 · 25/94), que cita el ADR 0002.
- **`2026-11-10_a56-congelada-latencia` solo vale por los tiempos.** Su `turnos.jsonl` guarda salidas crudas de tres
  conversaciones de test de #144; no se miran ni se informan.
- **`2026-11-04_193946_prompt-v3-a-solo-y-con-indicio`** aloja el análisis unificado de v3, v4 y v5, no solo v3.
- **`2026-11-06_puntaje-token-2`** es la etapa 1 de la segunda vuelta de #143, y guarda documentos que citan los ADR.
- **Los nombres de dos ADR quedaron viejos.** El archivo del ADR 0001 dice «gemma4-e2b-con-tito-viejo», pero hoy fija
  solo el ASR. El del ADR 0002 dice `c-premisa`, pero el prompt final es `c-consejos-corte-riesgo` (ADR 0008).
- **Tres Titos:** «Tito viejo» (el de #101 y el ADR 0001), «Tito nuevo» (perdía estafas en #101) y «Tito viejo 2.0»
  (con frases agregadas; E12). Ninguno está en la configuración final.
- **Archivos sueltos, sin carpeta:** los 7 de la matriz #101 (`2026-10-30_112956_101_*`), los 7 del A56
  (`2026-11-06-a56-*`, con guion en vez de `_`), `corridas/2026-11-05_TITO-VIEJO-2-COLAB.zip` y, en `analisis/`,
  `2026-11-05-TITO-VIEJO-2-COMPARACION.md` con `comparar_tito_viejo_2.py`.
- **Formato mezclado:** las de octubre llevan hora (`_HHMMSS_`); las de noviembre, solo fecha y tema, con subcarpetas
  `a/`, `b/`, `c/`, `d/` o una por variante (`c-premisa`, `c-premisa-rep`…), cada una con su propio sello de hora.
- **Las `linux-*` del 2026-10-23 no tienen `resumen.md`:** solo CSV y manifiesto. Sus cifras están en CAP-08 §8.3.2.
- **`2026-11-20_mejoras-luciano` y `analisis/2026-11-20-*`** son exploración posterior a la evaluación final. No cambian
  la configuración.
- **La reserva ya no está aparte.** Los documentos de la evaluación final y de la exploración hablan de la rama
  `reserva/test` (tienen nota): desde el 2026-11-21 la reserva está en `casos/` (partición `test_reservado`) y los
  CSV en `corridas/2026-11-12_evaluacion-final/test_reservado/`
  ([nota](../../experiments/slm-directo/casos/RESERVA-EN-ESTA-RAMA.md)).
- **«Desarrollo» cambia de tamaño:** 53 casos cortos (mediados de octubre), 150 (75 estafas y 75 legítimas; de fines de octubre a E14), `alcance-140` (46 estafas y 94
  legítimas entrantes; desde E15) y 244 (todos los de desarrollo, que corre la configuración congelada).

## 4. Afirmaciones superadas que siguen en los capítulos

Para quien redacte. Ya se corrigió el 2026-11-21: `c-premisa` como configuración final en CAP-03 y CAP-08, la cita
de fuentes de CAP-08 §8.3.2 y la latencia de CAP-09.

- **[CAP-10](CAP-10-GESTION-DEL-PROYECTO.md): congelado al 2026-11-03.** La tabla de hitos dice H2 «atrasado, faltan
  #54, #32 y #39» y H4 «faltan #33, #55 y #45», todos cerrados. La cronología termina en el ADR 0001: faltan Tito afuera,
  los ADR 0002 a 0009, E1 fuera, los sets externos y la evaluación final. «El piloto de 14 conversaciones sigue
  pendiente» ya no vale. Es el capítulo del proceso: este mapa y la bitácora son su fuente.
- **[CAP-02](CAP-02-MARCO-CONCEPTUAL-Y-ANTECEDENTES.md):** §2.1 describe el catálogo de septiembre («nueve semillas
  fraudulentas y ocho negativos»). §2.4 dice que el trabajo usa márgenes en segundos, pero la evaluación final informó
  en líneas. No menciona KorCCVi ni CallCenterEN.
- **[CAP-04](CAP-04-METODOLOGIA.md):** §4.2 dice que el piloto de 14 conversaciones sigue pendiente (#54) y que el
  equipo va a hacer llamadas; #54 se cerró y E1 quedó fuera. §4.3 remite a #32 como pendiente. §4.5 y §4.6 conservan
  los bloques «se congela en D08» con `δ` de 5, 10 y 20 s, que no se usaron. §4.4 ubica la reserva en
  `laboratorio-luciano`, rama borrada el 2026-11-11; hoy está en `casos/`.
- **[CAP-07](CAP-07-VERIFICACION-Y-PRUEBAS.md):** la tabla de §7.2 es del 2026-11-03. Hoy (2026-11-21) `slm-directo`
  tiene 633 tests que pasan con 11 omitidos; `replay`, 35; `metricas`, 28. `voip` y `asr-local` necesitan numpy para
  cargar algunos módulos. La fila de ayuda-memoria y el test de roles del visor ya no existen. La fila RNF-03 de §7.6
  da «p95 = 4,53 s» (E2B en la M1, E9) sin el iPhone (E21). RF-08 y RF-09 validan evidencia y alerta, que la salida
  cortada ya no genera.
- **[CAP-01](CAP-01-INTRODUCCION.md):** el objetivo 9 incluye «robustez al ASR», que quedó fuera con E1.
- **[CAP-03](CAP-03-REQUISITOS-Y-ANALISIS.md):** RF-09 exige salida con «riesgo, alerta, motivo y evidencia»; con el
  ADR 0006 y el ADR 0009 la salida es solo el riesgo y el motivo va aparte. RNF-06 dice «se mide en el test reservado»
  y no da el resultado.
- **[CAP-05](CAP-05-DISENO-Y-ARQUITECTURA.md):** la fila «Modelo por API» dice que se mide como techo en #174;
  [MAPA-DECISIONES D03](../gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución) dice que no entra «ni como
  techo experimental».
- **[CAP-06](CAP-06-IMPLEMENTACION.md):** §6.4.2 deja abierta la exigencia de repeticiones múltiples, que ya responden
  H02 y H13.

**Decisiones que el equipo todavía no tomó** (describir lo que pasó; no darlas por resueltas):

- El [ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md) (alcance) y el
  [ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md) (reglas antes de correr) no
  están aceptados: así lo dice su estado, aunque la evaluación final se hizo con los dos.
- La referencia con un modelo por API (#174): CAP-08 §8.7 la lista como pendiente y D03 la descarta.
- La meta 80/15 ([RNF-06 de CAP-03](CAP-03-REQUISITOS-Y-ANALISIS.md)) es idea del equipo y al tutor le pareció bien;
  no es criterio de aprobación. La evaluación
  final se corrió sin criterios de aprobación.
- Falta la minuta de la reunión del 2026-11-11 (el ADR 0003 dice que ese día se le explicó al tutor):
  [`seguimientos/`](../gestion/seguimientos/README.md) termina en el 2026-10-28.
- La bitácora de noviembre, [semana 2](../gestion/bitacora/2026-11-semana-02.md) y
  [semana 3](../gestion/bitacora/2026-11-semana-03.md), tiene el objetivo sin completar y solo registra algunos avances.
- La [lectura de la evaluación final](../evaluacion/CONCLUSIONES-EVALUACION-FINAL.md) de Luciano y la regla de pedido
  crítico (E20) no se discutieron en equipo.
- D07 (taxonomía y evento crítico) sigue abierta; D08 quedó «resuelta con límites» el 2026-11-21.

## 5. Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Configuración final | [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) con [0006](../ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md), [0007](../ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md), [0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md) y [0009](../ingenieria/adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md); prompt [`tarea_c_consejos.txt`](../../experiments/slm-directo/prompts/tarea_c_consejos.txt) con [`salida_json_c.txt`](../../experiments/slm-directo/prompts/salida_json_c.txt); ASR en el [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) |
| Evaluación final | [análisis](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md), [cómo se preparó](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/README.md), [lectura de los fallos](../evaluacion/CONCLUSIONES-EVALUACION-FINAL.md), [protocolo](../evaluacion/PROTOCOLO-EXPERIMENTAL.md) y [métricas](../evaluacion/METRICAS.md). La lectura de los fallos con texto (`LECTURA-FALLOS-TEST-RESERVADO.html`) quedó fuera de Git, en la copia de Mateo |
| Conjunto de desarrollo | [`casos/`](../../experiments/slm-directo/casos/README.md) (`texto/` y `referencia/`, partición `desarrollo`), [listas](../../experiments/slm-directo/casos/listas/alcance-140.txt) (`alcance-140`, `desarrollo-150`), [manifiesto](../../experiments/slm-directo/casos/MANIFIESTO-DESARROLLO.md) y [catálogo de conversaciones](../../experiments/slm-directo/casos/CATALOGO-CONVERSACIONES.md) |
| Test reservado | `casos/` con partición `test_reservado` (`CV2-T-*`), [legítimas entrantes de test](../../experiments/slm-directo/casos/legitimas-entrantes-test.jsonl), [alcance anotado a ciegas](../../experiments/slm-directo/casos/TEST-ALCANCE.md) |
| Conjuntos externos | [`casos/externo/`](../../experiments/slm-directo/casos/externo/README.md) y su [relevamiento](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md) |
| Código del detector | [`detectores.py`](../../experiments/slm-directo/detectores.py), [`correr.py`](../../experiments/slm-directo/correr.py), [`conjuntos.py`](../../experiments/slm-directo/conjuntos.py); reglas en [`reglas.py`](../../experiments/slm-directo/reglas.py); guía en el [README de slm-directo](../../experiments/slm-directo/README.md) |
| Demo en vivo | [`experiments/voip/`](../../experiments/voip/README.md) (usa la configuración final y el ASR), con [replay](../../experiments/replay/README.md) |
| ASR | [`experiments/asr-local/`](../../experiments/asr-local/README.md) y el [plan de voz real](../../experiments/asr-local/PLAN-VOZ-REAL.md) |
| Mediciones en teléfono | A56: [E13](../../experiments/slm-directo/corridas/2026-11-06-a56-diagnostico.md), [congelada](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md), [#172](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md). iPhone: [detector](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/README.md), [ASR y detector](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md), [solo el número](../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md) |
| Decisiones y hallazgos | [MAPA-DECISIONES](../gestion/MAPA-DECISIONES.md), [ADR](../ingenieria/adr/), [hallazgos](../hallazgos/README.md), [bitácora](../gestion/bitacora/README.md) |
| Estructura del informe | [esqueleto](ESQUELETO-INFORME.md) y los capítulos de esta carpeta |
