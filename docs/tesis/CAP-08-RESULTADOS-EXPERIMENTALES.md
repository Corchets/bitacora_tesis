> **Estado: borrador del 2026-11-20.** La evaluación final sobre el test reservado ([#52](https://github.com/Corchets/bitacora_tesis/issues/52)) corrió el 2026-11-19: sus cifras están en §8.3.4 y son las que estiman el rendimiento del detector. Todo lo demás es de **desarrollo**, sin revisión humana, y solo orientó decisiones.

# Capítulo 8: Resultados experimentales

> **Configuración (2026-11-11).** La configuración final es la del [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md): Gemma 4 E2B solo, con `c-premisa-corte-riesgo`. Sus resultados de desarrollo están en §8.3.3. **Nota del 2026-11-18:** el prompt pasó a `c-consejos-corte-riesgo` ([ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md)), elegido por Mateo por fuera de la regla de la [revisión de producto](../../experiments/slm-directo/corridas/2026-11-10_revision-producto/analisis.md); las cifras de §8.3.3 son de `c-premisa` y las de la evaluación final (§8.3.4), de `c-consejos`. Lo que este capítulo atribuye a Tito viejo con E2B es la configuración del [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md), que queda como antecedente. La baja de falsas alarmas con Tito no es filtrado ([H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)), y los resultados se informan con corpus_v2 aparte ([H01](../hallazgos/H01-corpus-v2-se-lee-aparte.md)).

## 8.1. Descripción del corpus

| Conjunto | Vishing | Legítimas | Total | Uso hasta hoy |
|---|---:|---:|---:|---|
| Antecedentes escritos | 29 | 24 | 53 | Desarrollo |
| Corpus v2, desarrollo | 46 | 51 | 97 | Desarrollo |
| Corpus v2, reserva | 100 | 100 | 200 | Test. Las 100 estafas dan la cifra principal de detección; las 100 legítimas se leen aparte, porque 74 quedan fuera del alcance |
| Legítimas entrantes, desarrollo | | 94 | 94 | Desarrollo, junto con las 46 estafas de corpus v2 (los 140 del alcance) |
| Legítimas entrantes, test | | 56 | 56 | Test. Dan la cifra principal de falsas alarmas |
| Estafas reales coreanas ([#144](https://github.com/Corchets/bitacora_tesis/issues/144)) | 33 | | 33 | Externo, traducidas. Control de sensibilidad |
| Legítimas reales de call center (CallCenterEN) | | 33 | 33 | Externo, traducidas. Falsas alarmas en llamadas reales. Hay 42 más de ventas de Medicare, que se informan aparte como zona gris |
| Diálogos con voz real | 3 guiones | 1 guion | 4 | 9 llamadas guionadas, 2 voces |

Corpus v2 es de redacción asistida, con [diseño y límites documentados](../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md). Ninguno de los 350 casos escritos tiene `revision_humana` en verdadero, así que sus marcas son provisionales. De las 75 estafas de desarrollo, 10 terminan antes del pedido. Los detectores de pedidos no las avisan; el prompt de intención, sí ([H10](../hallazgos/H10-c-avisa-antes-del-pedido.md)).

**El alcance cambió el 2026-11-06:** el detector corre solo en llamadas entrantes de números no agendados ([ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md), [ADR 0004](../ingenieria/adr/0004-legitimas-entrantes-nuevas-y-test-aparte.md)). Por eso las legítimas viejas de corpus v2 no se informan como falsas alarmas y se escribieron legítimas nuevas para ese alcance, 94 de desarrollo y 56 de test. Los dos conjuntos externos son reales pero no argentinos: están traducidos, y en las legítimas reales los roles y el tipo de llamada los infirió un modelo. Qué mide cada conjunto y con qué límite está en el [análisis de la evaluación final](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md#cuánto-vale-cada-conjunto).

## 8.2. Reconocimiento de voz

### 8.2.1. Con voz real

Comparación offline de las dos opciones sobre el mismo audio, con 18 canales, 129 frases de referencia y dos voces ([resumen](../../experiments/asr-local/corridas/2026-11-02_voz-real_dialogos-a-contra-b/resumen.md)). El orden de los criterios se fijó antes de medir, en [§12.9 del plan](../../experiments/asr-local/PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30).

| Criterio | **B · final** | A |
|---|---:|---:|
| Frases con las etiquetas correctas | 121/129 | 120/129 |
| Etiquetas nuevas en negativas | 0 | 0 |
| WER / CER | 25,6 % / 15,5 % | 32,8 % / 20,0 % |
| Recall de términos críticos | 70,9 % | 76,4 % |
| Recall de bancos y apps | 58,3 % | 50,0 % |
| Recall de jerga (informativo) | 10,0 % | 10,0 % |
| Demora de la frase final, mediana (p95) | 1,01 s (1,10) | 0,26 s (0,52) |
| Frases con palabras en otro idioma | 4 | 25 |
| Segmentos finales | 127 | 205 |
| RTF / memoria pico | 0,088 / 1.036 MB | 0,043 / 998 MB |

El WER se mide contra el guion y hubo palabras cambiadas al hablar: puede estar inflado y sirve para comparar A con B, no como valor absoluto. Con B, el canal de la otra persona, que llega por Meet y sin tele de fondo, da un WER de 32,9 % y un recall de términos críticos de 67,4 %. En el canal de Luciano sin tele, B recuperó 0 de los 2 términos críticos y A, 2 de 2: la muestra es muy chica para concluir, pero debe mirarse. El audio original se perdió el 2026-11-02, por lo que esta medición no se puede repetir con esos archivos.

### 8.2.2. Con audio sintético

Zipformer dio un WER de 4,35–5,00 % y Whisper, de 17,39 % sobre TTS ([comparación](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md#asr-sobre-audio-tts)). Con voz real, Zipformer resultó malo y se retiró: **el resultado con TTS no predijo el comportamiento con voz real**.

## 8.3. Comparación de detectores

### 8.3.1. Matriz #101: 10 modelos en 20 conversaciones

[Informe](../../experiments/slm-directo/corridas/2026-10-30_112956_101_informe_101.md). Son 10 estafas y 10 legítimas de desarrollo, separadas de lo usado para ajustar Tito, en un Ryzen 7 7700X con GPU, con 600 recorridos completos sobre el código `9fe43b5`, con cambios sin commit en la carpeta.

| Modelo | Directo (estafas · FA) | Con Tito viejo | Con Tito nuevo |
|---|---:|---:|---:|
| **`gemma4:e2b`** | 10/10 · 1/10 | **10/10 · 0/10** | 2/10 · 0/10 |
| `gemma4:e4b` | 10/10 · 1/10 | 10/10 · 1/10 | 3/10 · 0/10 |
| Los 10 modelos juntos | 90/100 · 48/100 | 82/100 · 27/100 | 23/100 · 0/100 |

Para E2B con Tito viejo, los intervalos de Wilson al 95 % son 72,2–100 % en estafas y 0–27,8 % en falsas alarmas. **Esos 20 casos sirvieron para elegir entre 10 modelos**, por lo que el valor es optimista.

**El filtro.** Con Tito viejo, E2B hizo 144 consultas al modelo contra 376 en directo, contando hasta el aviso. Tito derivó las 10 estafas y 5 de las 10 legítimas: las otras 5 no generaron ninguna consulta. El modelo descartó las 5 derivadas. Tito nuevo casi no deriva, y por eso pierde estafas.

La falsa alarma de E2B directo (`CV2-D-L-BANCO-001`, línea 12) no la sacó el filtro. Tito derivó esa llamada en la línea 1, así que el modelo leyó la conversación entera en las dos condiciones. En los 10 modelos, Tito saca 24 falsas alarmas y suma 3:

- 13 estaban en llamadas sin nada sensible antes del aviso, casi todas de modelos chicos que avisan en las primeras líneas;
- 6 estaban en líneas sensibles que Tito no vio;
- en 5, Tito ya había activado.

Ver [H08](../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md).

### 8.3.2. Otras familias

| Candidato | Resultado | Fuente |
|---|---|---|
| Reglas | 23/29 · 14/24 sobre los 53 antecedentes | [Comparación](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md#tabla-maestra-de-detectores) |
| Qwen3.5 con prompt `tarea`, 97 de corpus v2 | 9B 40/46 · 10/51; 4B 39/46 · 8/51; 2B 22/46 · 6/51; 0.8B 40/46 · 46/51 | [Tablero](../../experiments/slm-directo/analisis/tablero/panel_plantilla.html) y [pasada 0](../../experiments/slm-directo/analisis/2026-10-21-pasada-0/) |
| Qwen3.5 con prompt `v2`, mismos casos | 9B 31/46 · 7/51; 4B 14/46 · 0/51 | Ídem. Se escribió mirando los 53 y no generalizó |
| bge-reranker-v2-m3 | 4/10 · 1/10 | [#123](https://github.com/Corchets/bitacora_tesis/issues/123) |
| Riesgo primero, `gemma3n:e2b` | 10/10 · 3–6/10, o 2/10 · 0/10 | [análisis del 2026-10-30](../../experiments/slm-directo/analisis/2026-10-30-reranker-zero-shot/README.md) |

La repetición de Qwen 2B en GPU, con igual configuración y seed 42, cambió la decisión en 2 de 53 casos: la inferencia no es exactamente repetible, y eso afecta a toda comparación por una sola corrida.

### 8.3.3. Configuración del ADR 0002 en desarrollo

[Prueba de sensibilidad](../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md), en Colab T4 el 2026-11-10. Son los 140 casos de desarrollo dentro del alcance: 46 estafas, 36 de ellas con pedido, y 94 legítimas entrantes (29 cotidianas, y 65 con un pedido razonable o con una mención sensible). «A tiempo» es `T_A ≤ T_R`.

| Corrida | Estafas | Antes del pedido | A tiempo | Falsas alarmas |
|---|---:|---:|---:|---:|
| Base, sin la premisa | 37/46 | 15/36 | 25/36 | 26/94 |
| **`c-premisa`, la configuración final** | **40/46** | **19/36** | **29/36** | **26/94** |
| `c-premisa`, repetición | 39/46 | 18/36 | 28/36 | 28/94 |

Con Wilson al 95 %, en la primera corrida: estafas 87 % [74–94], a tiempo 81 % [65–90] y falsas alarmas 28 % [20–37]. De las 26 falsas alarmas, 2 son cotidianas. La regla escrita antes de correr eligió esta variante entre tres, sobre los mismos casos, y las marcas no tienen revisión humana: el valor es optimista. Qué significan las cifras está en [H10](../hallazgos/H10-c-avisa-antes-del-pedido.md).

### 8.3.4. Evaluación final

[Análisis](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md). Corrida única del 2026-11-19 en Colab T4, con `c-consejos-corte-riesgo` y el código fijados a un tag antes de correr. No hubo criterio de aprobación: se informan cifras con Wilson al 95 %. «Antes del pedido» es `T_A < T_R` y «a tiempo», `T_A ≤ T_R`, en líneas y sobre texto.

| Conjunto | Estafas avisadas | Antes del pedido | A tiempo | Falsas alarmas |
|---|---:|---:|---:|---:|
| **Test reservado** (100 estafas y 56 legítimas generadas) | 73/100, 73 % [64–81] | 37/80, 46 % [36–57] | **53/80, 66 % [55–76]** | **15/56, 27 % [17–40]** |
| **Estafas reales coreanas** | 33/33 [90–100] | 25/27 | 27/27 | |
| **Legítimas reales de call center** | | | | **21/33, 64 % [47–78]** |
| Desarrollo, como control | 40/46 | 16/36 | 26/36 | 20/94 |

Contra las dos referencias, en los mismos casos del test (p de McNemar):

| Cifra | `c-consejos` | `v4-corte`, el prompt de pedidos | Reglas léxicas v1 |
|---|---:|---:|---:|
| Estafas avisadas | 73/100 | 64/100 (p = 0,08) | 87/100 (p = 0,009) |
| Antes del pedido | 37/80 | 15/80 (p < 0,001) | 55/80 (p = 0,003) |
| A tiempo | 53/80 | 50/80 (p = 0,66) | 72/80 (p < 0,001) |
| Falsas alarmas | 15/56 | 15/56 (p = 1) | 48/56 (p < 0,001) |
| Falsas alarmas en las legítimas reales | 21/33 | 10/33 (p = 0,003) | 30/33 (p = 0,02) |

- **La detección útil se sostiene fuera de desarrollo.** Avisa a tiempo en el 66 % de las estafas del test, contra el 72 % de desarrollo.
- **Lo que baja son las estafas sin pedido:** 10 de 20 en el test, contra 10 de 10 en desarrollo. Con pedido avisa 63 de 80.
- **Las coreanas no discriminan.** Las avisan las 33 también `v4-corte` y las reglas. Dicen que no se le escapan, no que separe.
- **En llamadas reales de call center avisa en dos de cada tres.** Son dos cifras de falsas alarmas y se informan una al lado de la otra: 27 % en legítimas generadas y 64 % en reales.
- **El modelo no detecta más que una regla de palabras clave.** Lo que aporta es no avisar en todo: 27 % de falsas alarmas contra 86 %.
- **Contra el prompt de pedidos gana en anticipación** (37 contra 15 antes del pedido), con las mismas falsas alarmas en el test y el doble en las llamadas reales.

La latencia en la T4 fue de 210 ms de mediana por consulta (p95 de 266 ms).

**Cuánto se mueve al repetir.** La misma configuración volvió a correr el 2026-11-20 como base de la exploración de §8.3.5: 76/100 estafas avisadas, 43/80 antes del pedido, 56/80 a tiempo y 15/56 falsas alarmas. El 92 % de las consultas dio el mismo riesgo; el resto cambió 0,1 y cae sobre el umbral. Las cifras que valen son las del 2026-11-19, y esa diferencia es el margen entre pasadas ([H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)).

**Límites.** Las marcas de pedido y cumplimiento no tienen revisión humana. Las estafas del test salen del mismo generador que las de desarrollo: miden generalización dentro de ese estilo. Los conjuntos reales son de 33 casos, traducidos y de otros países. Con el contexto de 4.096 tokens del protocolo, el detector deja de consultar en una llamada larga después de unos 55 turnos de quien llama: en esta evaluación no cambió ninguna cifra, salvo 19 consultas de una llamada de la zona gris, pero es un límite del detector ([§11.3](CAP-11-CONCLUSIONES.md#113-limitaciones)). Todo corre sobre texto limpio y con turnos perfectos, sin reconocimiento de voz: en vivo los turnos se arman con umbrales que no se calibraron con grabaciones ([ADR 0007](../ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md)).

### 8.3.5. Exploración posterior con los conjuntos reales

[Análisis](../../experiments/slm-directo/corridas/2026-11-20_exploracion-reales/analisis.md), del 2026-11-20. Después de la evaluación final se probó si otro prompt u otra política de aviso bajaban las falsas alarmas en las llamadas reales sin perder estafas. **No reemplaza a la evaluación final:** los conjuntos reales pasaron a ser datos de ajuste. Fueron siete prompts, cinco escritos desde cero, y dos políticas, con la regla escrita antes de correr.

| Candidato | Coreanas a tiempo | Falsas alarmas en las 33 legítimas reales | Desarrollo: estafas · falsas alarmas |
|---|---:|---:|---:|
| Configuración final, en la misma sesión | 27/27 | 23/33 | 43/46 · 20/94 |
| La misma, esperando una segunda señal | 26/27 | 21/33 | 38/46 · 14/94 |
| `c-rumbo`, un párrafo cambiado | 27/27 | 26/33 | 44/46 · 28/94 |
| `p-niveles`, pregunta por el pedido en cuatro niveles | 24/27 | 12/33 | 25/46 · 16/94 |
| `p-minimo`, el más corto | 23/27 | 19/33 | 39/46 · 48/94 |
| `p-sino`, sí o no | 11/27 | 8/33 | 22/46 · 14/94 |

- **Ningún candidato pasó la regla y la configuración no cambió.** Los que conservan las coreanas no bajan las falsas alarmas; los que las bajan pierden estafas.
- **Cambiar el prompt mueve cuánto avisa el detector, no a quién.** A igual largo de llamada, ningún prompt separa mejor las estafas reales de las legítimas reales ([H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md)).
- **Un prompt más corto no avisa mejor,** y esperar una segunda señal no saca ninguna falsa alarma del test.
- **El umbral de 0,3 lo piden las estafas generadas.** Con 0,5 la configuración final avisa 28 de 33 coreanas y 5 de 33 legítimas reales, pero 37 de 100 estafas del test. No hay estafas reales argentinas para saber cuál de los dos casos se parece más al de acá.

## 8.4. Detección temprana y latencia

### 8.4.1. Sobre texto, en líneas

Con la configuración del ADR 0001, E2B y Tito viejo, en #101, el aviso llegó en la línea del pedido en 8 de 10 estafas, una línea antes en 1 y tres líneas después en 1. En las 6 estafas con cumplimiento marcado, avisó antes de la línea de `T_C`. Las marcas son provisionales, y en texto no hay segundos. E2B directo avisó antes del pedido en 4 de las 10 estafas; con Tito, en 1. #101 prueba la activación y el indicio juntos, así que no separa cuál de los dos atrasó el aviso ([H07](../hallazgos/H07-indicio-de-tito-pierde-estafas.md)). Con la configuración del ADR 0002 el aviso se adelanta: 19 de 36 estafas con pedido avisan antes del pedido (§8.3.3, [H10](../hallazgos/H10-c-avisa-antes-del-pedido.md)).

**En la evaluación final** (§8.3.4) el aviso llegó antes de la línea del pedido en 37 de las 80 estafas del test que tienen pedido, a más tardar en esa línea en 53, y antes del cumplimiento en 24 de las 32 que lo tienen marcado. El prompt de pedidos (`v4-corte`) avisó antes del pedido en 15 de 80.

### 8.4.2. Con voz real, en segundos

[Nueve llamadas guionadas por Meet](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md), con Gemma 4 E2B y Tito viejo. La columna «Respecto del pedido» es la diferencia entre `T_A` y la primera frase con el pedido, **ubicada por palabras clave y no por anotación humana**: negativo significa que el aviso llegó antes.

| Llamada | Diálogo | ASR en vivo | `T_A` (s) | Respecto del pedido (s) | Consultas |
|---|---|---|---:|---:|---:|
| 1 | D1, estafa | B | 28,5 | −5,1 | 1 |
| 2 | D2, estafa | B | 34,5 | +3,2 | 5 |
| 3 | D3, legítima | B | sin aviso | | 11 |
| 4 | D4, estafa | B | 19,7 | +4,8 | 1 |
| 5 | D1 con tele, estafa | B | 32,6 | +4,0 | 2 |
| 6 | D1 con tele, estafa | A | 20,8 | −4,2 | 3 |
| 7 | D2, estafa | A | 34,7 | +2,1 | 4 |
| 8 | D3, legítima | A | sin aviso | | 17 |
| 9 | D4, estafa | A | 24,2 | +6,9 | 6 |

El aviso llegó en 7 de 7 estafas (Wilson: 64,6–100 %) y en 0 de 2 legítimas, que son el mismo guion. **Con B, el aviso llegó después de empezado el pedido en 3 de las 4 estafas.** En D1 puede llegar antes porque cita el débito, no el pedido del código: por eso no alcanza con leer `T_A`, hay que mirar qué frase cita.

Esto no mide rendimiento: son 4 guiones y 2 voces, y sin marcas `T_C` no hay `L_C`.

**La evaluación final no midió en segundos.** Corrió sobre texto, así que informa si el aviso llega antes de la línea del pedido y de la del cumplimiento (§8.3.4), no `L_R`, `L_C` ni `Preventive@δ`. Las marcas tampoco tienen revisión humana. Queda como límite.

### 8.4.3. Demora del detector

En 5 corridas de `SC-WA-CODE-01` con `medir.py` en la M1, E2B dio una mediana de **3,74 s** por consulta, mínimo de 2,04 s y p95 de 4,53 s, sin fallos ni frases salteadas. **No cumple el criterio de menos de 2 s**, aunque el aviso llegó entre −0,45 y +0,40 s respecto del fin del pedido. Es una medición con Zipformer, sin Chrome ni Meet. En las llamadas con voz real, las medianas por llamada fueron de 1,4 a 5,6 s.

## 8.5. Falsas alarmas y negativos difíciles

| Conjunto | Resultado de la configuración del ADR 0001 |
|---|---|
| 10 legítimas de #101 | 0/10 (Wilson: 0–27,8 %) |
| D3 con voz real, mismo guion dos veces | 0/2 |
| `LG-SUPPORT-INFO-01` con TTS | Sin aviso |

Con la configuración del ADR 0002, en desarrollo, saltó en 26 de las 94 legítimas dentro del alcance: 2 de 29 cotidianas y 24 de 65 con un pedido razonable o una mención sensible (§8.3.3). La condición del tutor es que no salte por frases sueltas. D3 («amigos arreglando un cumple: palabras parecidas») se diseñó para eso, pero es un solo guion.

**En la evaluación final** (§8.3.4), por tipo de llamada legítima:

| Tipo | Test, legítimas generadas | Legítimas reales de call center |
|---|---:|---:|
| Cotidianas | 0/14 | 9/19 |
| Con un pedido razonable | 7/26 | 4/4 |
| Con una mención sensible, sin pedido | 8/16 | 8/10 |
| **Total** | **15/56** | **21/33** |

- **En las legítimas generadas no salta por frases sueltas:** ninguna cotidiana avisa. Un tercio de las falsas alarmas son llamadas «del banco» (5 de 7).
- **En las llamadas reales sí avisa en cotidianas:** 9 de 19. El tipo de esas llamadas lo infirió un modelo, no una persona.
- Los motivos que escribe en las 21 reales se reparten en tres grupos parecidos: le piden un código o datos de la cuenta, lee la venta como estafa, o da un motivo genérico.
- Con 5 llamadas legítimas de desconocidos por semana, el 27 % del test son unas 6 falsas alarmas por mes [4–9].

## 8.6. Rendimiento y límites del hardware

En computadora, con la configuración del ADR 0001:

| Dato | M1 de 8 GB |
|---|---|
| Parakeet con filtro | RTF 0,088; 1.036 MB de memoria pico |
| Gemma 4 E2B, JSON completo | Archivo de 4,59 GB; 3,74 s de mediana por consulta |
| Conjunto | 28–30 % de memoria libre y 4,5–4,7 GB de swap en la medición |

La [corrida de E4B](../../experiments/voip/corridas/2026-11-02-tito-gemma4-panel.md) en la misma máquina dio 46,3 s y 15,8 s por evaluación, y avisó a +49,0 s del pedido.

**En el teléfono, solo el detector.** Con la salida cortada del ADR 0002 y el prompt base, en un Samsung A56 con `llama-server` en CPU: 3,60 s de mediana y 4,90 s de p95 por línea de OTRA, unos 11 s más para el motivo del primer aviso y 3,39 GiB de pico ([a56-congelada-latencia](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md)). Es una pasada sobre tres conversaciones, sin ASR.

**En dos teléfonos, con el mismo servidor.** El 2026-11-20 se midió la configuración final en un iPhone 15 Pro Max, con el mismo `llama-server`, el mismo archivo del modelo y el mismo ejecutor que en el A56 ([iphone-15-pro-max-latencia](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/README.md)). Son seis conversaciones de desarrollo y 83 consultas, todas válidas, con una pasada por fila. Mide latencia y memoria, no detección.

| Teléfono | Prompt | Por línea de OTRA: mediana / p95 | Primer aviso, sin esperar el motivo | Memoria residente, pico |
|---|---|---:|---:|---:|
| Samsung A56, CPU con 4 hilos | `c-premisa` | 3,74 / 4,16 s | 3,68 s | 3,53 GiB |
| iPhone, CPU con 4 hilos | `c-premisa` | 2,16 / 2,32 s | 2,03 s | 3,22 GiB |
| iPhone, GPU | `c-premisa` | 0,94 / 1,02 s | 0,87 s | 3,20 GiB |
| iPhone, CPU con 4 hilos | final | 2,01 / 2,41 s | 1,68 s | 3,16 GiB |
| iPhone, GPU | final | 0,79 / 1,03 s | 0,72 s | 2,98 GiB |

- Con el mismo prompt, el iPhone con GPU tarda unas 4 veces menos por línea que el A56. Con CPU y 4 hilos, como el A56, tarda 1,7 veces menos.
- Con la configuración final y GPU, la actualización por línea queda dentro del criterio de p95 ≤ 1,5 s ([RNF-03](CAP-03-REQUISITOS-Y-ANALISIS.md#33-requisitos-no-funcionales)). El primer aviso con su motivo tarda 3,22 s de mediana.
- El A56 todavía no tiene una corrida con el prompt final: entre teléfonos solo se compara `c-premisa`.
- El iPhone estuvo enchufado y llegó al estado térmico `serious` en las cuatro corridas.

**Detector y ASR a la vez.** El 2026-11-21 corrieron juntos en el iPhone, sin cable, el detector con la configuración final y el ASR del proyecto, Parakeet con filtro ([iphone-15-pro-max-asr-y-detector](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md)). El audio es sintético: las mismas seis conversaciones a ritmo de conversación, 12 min 18 s. La segunda pasada repite el ritmo sin el ASR.

| Pasada | Detector, por línea: mediana / p95 | Memoria que iOS le cuenta a la app, pico | Libre antes del límite, mínimo | Estado térmico |
|---|---:|---:|---:|---|
| Detector y ASR | 0,66 / 0,70 s | 1,39 GiB | 1,92 GiB | `nominal` y `fair` |
| Solo el detector | 0,69 / 0,72 s | 0,58 GiB | 2,73 GiB | `nominal` |

Los tiempos de esta tabla son los del servidor, sin la red. La memoria que cuenta iOS no incluye el archivo del modelo; el pico residente con los dos fue de 2,62 GiB.

- iOS no cerró la app.
- El ASR no demoró al detector en esta pasada.
- El ASR fue a tiempo real: su atraso fue de 0,17 s de p95 y 0,48 s de máximo.

**Límites de las mediciones en el iPhone.** Es una pasada por condición. El audio es sintético y se lee de un archivo, no de una llamada. El detector consultó sobre el texto original, no sobre lo que transcribió el ASR. No se midió el consumo de batería. Una app de iOS no tiene una interfaz para el audio de una llamada telefónica, así que el iPhone mide el hardware, no un producto. **Falta el recorrido completo en Android.**

## 8.7. Pendientes del capítulo

1. ~~Correr el test reservado una sola vez con la configuración congelada (#33, #52).~~ Hecho el 2026-11-19 (§8.3.4).
2. PI2 con marcas humanas: no se hizo. Las cifras de anticipación son en líneas y con marcas sin revisar (§8.4).
3. E2, revisando motivos contra evidencia: no se hizo.
4. Sensibilidad de la precisión a la prevalencia: están las falsas alarmas por volumen de llamadas (§8.5); la precisión según la prevalencia no se calculó.
5. Tablas y figuras regeneradas desde salidas crudas: las de §8.3.4 y §8.3.5 salen de los `analizar.py` de cada corrida. Las anteriores, no.
6. El detector en el teléfono con la configuración final ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)): §8.6 la tiene en un iPhone 15 Pro Max, también con el ASR a la vez. En el A56 sigue la medición con el prompt anterior, y falta el recorrido completo en Android.
7. La referencia con un modelo de frontera ([#174](https://github.com/Corchets/bitacora_tesis/issues/174)).
