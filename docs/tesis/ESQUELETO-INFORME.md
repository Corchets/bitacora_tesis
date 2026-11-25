# Esqueleto del Informe Final

**Institución:** UNSTA — Ingeniería en Informática, Plan 2008
**Formato:** digital (PDF), A4, carilla simple, unas 100 páginas. Sin código.
**Redacción:** en Markdown, versionado en este repositorio.

Reemplaza al esqueleto del 2026-09, que está en el historial de Git. Lo acordó el equipo el 2026-11-25, partiendo
de lo que propuso el profesor. El borrador anterior (`INFORME-FINAL.md`, fuera de Git) y los `CAP-*.md` de esta
carpeta se usan como material de partida, no como base: estaban ordenados por fecha y contaban el proceso interno.

## 1. Criterios

**El informe se ordena por tema, no por fecha.** La evolución del proyecto se cuenta una sola vez, en el capítulo 7.
El resto describe el sistema, cómo se midió y qué dio.

**Qué va:**

- cada decisión técnica, escrita como «se eligió X porque Y, frente a Z», con la evidencia que la sostiene;
- los resultados negativos, como comparaciones o como cambios de rumbo justificados;
- los límites, dichos con claridad.

**Qué no va:**

- reuniones, acuerdos con el tutor y quién propuso o decidió qué;
- números de issue, códigos de decisión, ADR o hallazgo (D05, ADR 0002, H07), ramas, tags, carpetas y Colab;
- nombres internos: «Tito» pasa a ser «filtro previo»; los prompts se nombran por lo que hacen («prompt de
  intención»), no por su letra;
- código de ningún tipo. Los prompts son texto en lenguaje natural y van en un anexo;
- estados superados («pendiente», «en curso al…»).

**Reglas de redacción:**

- **Cada cifra aparece en un solo lugar,** en el capítulo 8 o en el 9. Los demás capítulos remiten a ella y no la
  repiten.
- Cada término se define una vez: en el texto la primera vez que aparece, y después queda en la lista de siglas.
- El sistema se describe en presente; los experimentos, en pasado.
- Fechas en el cuerpo, solo cuando hacen falta para entender algo (por ejemplo, la disponibilidad de un producto).
- Toda afirmación externa lleva su referencia; todo resultado propio sale de una corrida o de un análisis que está
  en el repositorio (la columna «Fuente» de abajo). La fuente se usa para escribir; en el informe no se cita la ruta.
- Antes de usar una fuente, leer el [mapa del proceso](MAPA-DEL-PROCESO.md), sobre todo §3 (nombres que engañan) y
  §4 (afirmaciones superadas que siguen en los capítulos viejos).

## 2. Estructura y presupuesto

| # | Capítulo | Págs. |
|---|---|---:|
| — | Preliminares | 6 |
| 1 | Introducción | 5 |
| 2 | Objetivos y alcance | 3 |
| 3 | Marco teórico | 15 |
| 4 | Arquitectura | 9 |
| 5 | Tecnologías | 6 |
| 6 | Metodologías | 11 |
| 7 | Etapas del proyecto | 10 |
| 8 | Comparaciones | 16 |
| 9 | Evaluación final y discusión | 11 |
| 10 | Conclusiones | 3 |
| 11 | Mejoras futuras y hoja de ruta | 7 |
| — | Referencias y anexos | 8 |
| | **Total** | **~110** |

Las páginas son orientativas: lo que manda es que no haya repeticiones y que todo se entienda.

### Correspondencia con lo que pidió el profesor

| Pedido del profesor | Capítulo | Cambio |
|---|---|---|
| Carátula, resumen y abstract, agradecimientos | Preliminares | — |
| Introducción, objetivos | 1 y 2 | — |
| Marco teórico | 3 | — |
| Arquitecturas | 4 | Se describe la arquitectura final; las versiones anteriores, en el 7 |
| Tecnologías | 5 | — |
| Metodologías utilizadas | 6 | Va antes de las comparaciones: sin corpus ni métricas no se entienden |
| Etapas del proyecto | 7 | — |
| Comparaciones | 8 | — |
| — | 9 | **Agregado:** evaluación final, discusión y límites |
| Conclusión | 10 | — |
| — | 11 | **Agregado:** mejoras futuras y hoja de ruta para continuar el trabajo |

## 3. Contenido por capítulo

### Preliminares

- Carátula: logo de la UNSTA, título, los cuatro integrantes, tutor y año.
- Resumen y palabras clave (una página); abstract y keywords (una página). Se escriben al final.
- Agradecimientos (opcionales).
- Índice general, de figuras y de tablas; lista de siglas.

**Fuente:** [requisitos académicos](../propuesta/REQUISITOS-ACADEMICOS.md); el título sigue abierto
([D13](../gestion/MAPA-DECISIONES.md#d13--título-definitivo)).

### 1. Introducción

1. El vishing y sus modalidades en la Argentina, con fuentes oficiales (sin cifras de prevalencia que no se tengan).
2. El problema: un aviso solo sirve si llega antes de que la persona cumpla el pedido.
3. Lo que existe (detección en el dispositivo de Google y Samsung, la patente de Google) y lo que falta: nada abierto,
   evaluable y en español rioplatense.
4. El aporte del trabajo.
5. Organización del informe.

**Fuente:** [síntesis del estado del arte](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md),
[CAP-01](CAP-01-INTRODUCCION.md) como borrador.

### 2. Objetivos y alcance

1. Objetivo general y objetivos específicos. Sacar la «robustez al ASR», que no se midió.
2. Preguntas de investigación: detección incremental y anticipación respecto del pedido.
3. Alcance: llamadas entrantes de números no agendados, ejecución en el dispositivo, español.
4. Exclusiones y por qué: la llamada telefónica común (el sistema operativo no da el audio), voces clonadas,
   biometría, prueba con usuarios.

**Fuente:** [preguntas de investigación](../investigacion/PREGUNTAS-DE-INVESTIGACION.md),
[plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md),
[ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md) (alcance; ver §5).

### 3. Marco teórico

1. Ingeniería social y vishing: autoridad, urgencia y confianza; maniobras típicas.
2. Reconocimiento automático del habla: modelos en streaming, detección de actividad de voz y WER.
3. Modelos de lenguaje: de los grandes a los chicos, cuantización, inferencia local, prompts, salida estructurada y
   caché del prefijo.
4. Clasificación temprana: decidir con información parcial y el compromiso entre anticipación y error.
5. Falsas alarmas y tasa base: por qué una tasa baja de falsas alarmas sigue molestando en uso real.
6. Datos sintéticos generados con modelos: usos y amenazas a la validez.
7. Sistemas existentes: productos comerciales, la patente de Google y trabajos académicos.
8. Privacidad: la Ley 25.326 y el procesamiento en el dispositivo.
9. Síntesis: el vacío que aborda el trabajo.

**Fuente:** [síntesis del estado del arte](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md),
[contraste entre teoría NLP y laboratorio](../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md),
[privacidad del sistema](../corpus/PRIVACIDAD-DEL-SISTEMA.md), la patente (`US20240388655A1.pdf`, fuera de Git),
[CAP-02](CAP-02-MARCO-CONCEPTUAL-Y-ANTECEDENTES.md) como borrador (desactualizado; ver el mapa §4).

### 4. Arquitectura

Describe el sistema tal como quedó. Cada decisión se justifica en una línea y remite al capítulo 8 para la evidencia.

1. Requisitos que guían el diseño: una tabla corta de funcionales y no funcionales (local, latencia por línea,
   memoria, no guardar audio, un solo aviso explicado).
2. Vista general: captura → filtro de voz → ASR → turnos → detector → política de aviso → interfaz (figura).
3. Recorrido de una llamada en el tiempo: el detector consulta al cerrar cada turno de la otra persona, compara el
   riesgo con el umbral y avisa; el motivo llega después (figura).
4. Cada componente: entrada, salida y responsabilidad.
5. Privacidad por diseño: qué se procesa, qué se descarta y qué nunca sale del teléfono.
6. Prototipo frente a producto: cómo funciona la demo (canal controlado) y cómo sería integrado en el teléfono.
7. Alternativas descartadas: una tabla con la alternativa, el motivo y la sección del capítulo 8 que lo muestra
   (cascada, filtro previo, reglas, modelo por API, el mismo modelo como ASR).

**Fuente:** [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md) (ASR),
[0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md),
[0006](../ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md),
[0007](../ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md),
[0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md) y
[0009](../ingenieria/adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md);
[alternativas de captura de audio](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md);
[CAP-03](CAP-03-REQUISITOS-Y-ANALISIS.md) y [CAP-05](CAP-05-DISENO-Y-ARQUITECTURA.md) como borradores.

### 5. Tecnologías

Describe cada tecnología y el criterio con que se eligió. Las mediciones que la eligieron van en el capítulo 8.
Una tabla por categoría, con estas columnas: qué es, para qué se usó y por qué esa.

1. Reconocimiento de voz: Parakeet, Silero VAD y Zipformer (descartado).
2. Modelos de lenguaje: Gemma 4 E2B, la familia Qwen 3.5, RoBERTuito y Llama 3.2.
3. Entornos de ejecución: Ollama, llama.cpp, Metal y Android.
4. Hardware de prueba: Mac M1, PC con GPU, Samsung Galaxy A56 e iPhone 15 Pro Max.
5. Conjuntos externos: KorCCVi y CallCenterEN.
6. Herramientas de desarrollo y gestión: Python, pytest, Google Colab, GitHub.

**Fuente:** [primera investigación de modelos](../investigacion/PRIMERA-INVESTIGACION-MODELOS.md),
[prefactibilidad técnica](../investigacion/PREFACTIBILIDAD-TECNICA.md),
[relevamiento del corpus externo](../corpus/RELEVAMIENTO-CORPUS-EXTERNO.md),
[fuentes legítimas reales](../investigacion/FUENTES-LEGITIMAS-REALES.md),
[CAP-06](CAP-06-IMPLEMENTACION.md) como borrador.

### 6. Metodologías

1. **Metodología de trabajo:** iterativa, con issues, revisión por PR y registro de decisiones y experimentos.
   Organización del equipo. Uso de asistentes de IA, en un párrafo breve que diga para qué se usaron y cómo se
   revisó lo que produjeron. Una o dos páginas, sin entrar en el detalle del repositorio.
2. **Revisión de literatura:** cómo se buscaron y se seleccionaron las fuentes.
3. **Diseño experimental:** conjunto de desarrollo para elegir y test reservado que se mira una sola vez; reglas de
   decisión escritas antes de correr. El sobreajuste del prompt v2 es el ejemplo que lo justifica (se cuenta en el 7).
4. **Corpus:** cómo se generaron las conversaciones, los escenarios, las legítimas difíciles, el ajuste al alcance y
   el sesgo de forma que se encontró y cómo se acotó.
5. **Anotación:** las marcas por conversación (pedido y cumplimiento), la revisión humana y su límite (no hubo
   medida de acuerdo entre anotadores).
6. **Conjuntos reales:** estafas coreanas y legítimas de call center; filtro, procedencia y para qué sirven.
7. **Métricas:** estafas avisadas, avisos a tiempo, anticipación en líneas, falsas alarmas y latencia por línea.
8. **Reproducibilidad y variabilidad:** qué se registra en cada corrida y cuánto mueve repetir.
9. **Pruebas del software:** estrategia y alcance de las pruebas automáticas, sin código.
10. **Ética y datos:** consentimiento, datos fuera del repositorio y descarte de audio.

**Fuente:** [método de trabajo](../gestion/METODO-DE-TRABAJO.md),
[protocolo de revisión](../investigacion/PROTOCOLO-REVISION.md),
[protocolo experimental](../evaluacion/PROTOCOLO-EXPERIMENTAL.md) y la
[ficha de D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental),
[ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md),
[diseño del corpus v2](../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md),
[ADR 0004](../ingenieria/adr/0004-legitimas-entrantes-nuevas-y-test-aparte.md),
[manual de anotación](../corpus/MANUAL-ANOTACION.md), [revisión ciega](../corpus/REVISION-CIEGA-145.md),
[conjuntos externos](../../experiments/slm-directo/casos/externo/README.md), [métricas](../evaluacion/METRICAS.md),
[H02](../hallazgos/H02-ruido-entre-corridas.md), [H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md),
[CAP-04](CAP-04-METODOLOGIA.md) y [CAP-07](CAP-07-VERIFICACION-Y-PRUEBAS.md) como borradores (desactualizados).

### 7. Etapas del proyecto

**Acá va la evolución:** qué se probó, qué se cambió, qué se mantuvo y por qué. Es el único lugar donde se cuenta en
orden. Se cuenta como evolución técnica del sistema: sin reuniones, sin nombres y sin la historia del repositorio.

**Reparto con el capítulo 8.** Este capítulo dice qué cambió y por qué, con la cifra mínima para entenderlo. La
tabla con las mediciones lado a lado está en el 8. Cada cambio remite a su sección del 8.

Cada fase lleva el mismo formato: objetivo, qué se probó, qué cambió, qué se mantuvo y qué se descartó.

1. **Investigación y prefactibilidad** (septiembre): el problema en cinco líneas, el catálogo de escenarios
   argentinos, qué modelos entran en un teléfono, la ventana de contexto y la privacidad.
2. **Laboratorio inicial** (fines de septiembre): reglas, encoders y una cascada encoder → modelo chico. La cascada
   empeora al encoder solo. Se pasa a un modelo de lenguaje que lee toda la transcripción.
3. **Primeros componentes y línea base** (octubre): reglas como referencia, escalera de tamaños de Qwen,
   reproducibilidad entre máquinas, caché del prefijo y primera integración con audio.
4. **Corpus nuevo y elección del modelo** (octubre): un corpus más grande; el prompt corregido mirando los errores no
   generaliza; combinar detectores no alcanza; filtro previo y matriz de diez modelos, que elige Gemma 4 E2B; pedir
   menos salida acelera; el reranker zero-shot mide tema y no intención.
5. **Voz real y demostración** (fines de octubre): Zipformer falla con voz real y entra Parakeet con filtro Silero;
   la demo en vivo anda de punta a punta. Usar el mismo modelo como ASR no conviene.
6. **Revisión crítica y configuración final** (noviembre): con más casos, retocar el prompt casi no mueve nada; el
   filtro previo era un punto ciego y sale; leer la probabilidad del token no sirve como puntaje; se acota el alcance
   y se escriben legítimas nuevas; la salida se corta tras el riesgo; el prompt de intención avisa antes del pedido; se
   consulta al cerrar cada turno de la otra persona; revisión de producto; se fija la configuración.
7. **Mediciones en teléfono** (noviembre): el JSON completo no entra en tiempo en el A56; la configuración final
   tarda menos de un segundo por línea en el iPhone, con el ASR corriendo a la vez; generar solo el número.
8. **Evaluación final y exploración posterior** (noviembre): una sola corrida sobre el test y los conjuntos reales;
   después, pruebas exploratorias que no cambian la configuración.

Cierra con:

- **Tabla de evolución de la configuración:** componente, primera versión, versión final y por qué cambió.
- **Figura:** línea de tiempo de las fases.
- **Riesgos principales:** qué riesgo apareció y cómo se mitigó (una tabla).

**Fuente:** [mapa del proceso](MAPA-DEL-PROCESO.md), etapas E0 a E21, una por una con su evidencia;
[hallazgos](../hallazgos/README.md); [registro de riesgos](../gestion/REGISTRO-RIESGOS.md). La
[bitácora](../gestion/bitacora/README.md) sirve para fechas, no para contenido.

### 8. Comparaciones

Ordenado por componente, no por fecha. Cada sección sigue el mismo formato: pregunta, cómo se comparó (conjunto y
condiciones), resultado (tabla o figura) y qué se adoptó. Acá viven las cifras de desarrollo.

| Sección | Qué se compara | Fuente (etapa del mapa) |
|---|---|---|
| 8.1 Reconocimiento de voz | Zipformer contra Parakeet; Silero contra corte RMS; Gemma como ASR | E9, E17 |
| 8.2 Familias de detector | Reglas, encoder, cascada, reranker/NLI zero-shot y modelo de lenguaje directo | E0, E1, E8 |
| 8.3 Tamaño y modelo | Escalera de Qwen; matriz de diez modelos | E2, E7 |
| 8.4 Filtro previo | Con y sin filtro; cobertura de la primera línea sensible | E7, E10, E12 |
| 8.5 Instrucciones | v1, v2, v3 a v5, prompt de intención y variantes finales; cuánto explica el caso y cuánto el prompt | E5, E11, E15, E18, E20 |
| 8.6 Formato de salida | JSON completo, salida cortada, solo el número, probabilidad del token | E8, E14, E15, E21 |
| 8.7 Cuándo consultar y umbral | Cada línea contra turno de la otra persona; umbral; combinación de detectores | E6, E15 |
| 8.8 Hardware y latencia | CPU, M1, GPU, A56, iPhone; caché del prefijo | E2, E3, E13, E16, E21 |
| 8.9 Variabilidad | Entre máquinas, entre corridas, según el orden y el entorno de ejecución | E2, E3, E10, E16, E20 |
| 8.10 Modelo local contra modelo por API | Gemma contra Gemini en desarrollo (exploratoria; ver §5) | [corrida de Gemini](../../experiments/slm-directo/corridas/2026-11-23_gemini-batch/README.md), [H14](../hallazgos/H14-gemini-avisa-antes-con-menos-falsas-alarmas-en-desarrollo.md) |

**Fuente general:** [comparación de candidatos](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md),
[propuesta de configuración](../evaluacion/PROPUESTA-CONFIGURACION-DETECTOR.md), las corridas que enlaza cada etapa
del [mapa](MAPA-DEL-PROCESO.md#2-las-etapas) y [CAP-08](CAP-08-RESULTADOS-EXPERIMENTALES.md) como borrador.

### 9. Evaluación final y discusión

1. Configuración evaluada: una tabla (modelo, prompt, salida, cuándo consulta, umbral, ASR).
2. Conjuntos: test reservado, estafas reales y legítimas reales, con sus tamaños.
3. Resultados en el test: estafas avisadas, avisos a tiempo, anticipación y falsas alarmas.
4. Resultados en los conjuntos reales.
5. Referencias simples sobre los mismos casos (reglas y el prompt anterior).
6. Latencia y memoria en el teléfono (la cifra final; la evolución queda en el 8.8).
7. Análisis de errores: tipos de falsas alarmas y de estafas que se pierden, con ejemplos.
8. Exploración posterior a la evaluación, separada y rotulada: no reemplaza al resultado.
9. Respuesta a las preguntas de investigación.
10. Amenazas a la validez: datos generados, referencia sin acuerdo entre anotadores, una sola corrida, transcripción
    escrita en vez de ASR.
11. Implicaciones de ingeniería, éticas y de uso.

**Fuente:** [evaluación final](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/README.md) y su
[análisis](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md),
[qué concluir de la evaluación final](../evaluacion/CONCLUSIONES-EVALUACION-FINAL.md) (ver §5), E20 y E21 del
[mapa](MAPA-DEL-PROCESO.md), [H12](../hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md),
[H13](../hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md),
[CAP-09](CAP-09-DISCUSION.md) como borrador.

### 10. Conclusiones

1. Qué se construyó y qué se aprendió, en pocas páginas.
2. Respuesta breve a cada pregunta de investigación, remitiendo al capítulo 9 sin repetir las tablas.
3. Las limitaciones principales.

**Fuente:** [CAP-11](CAP-11-CONCLUSIONES.md) como borrador.

### 11. Mejoras futuras y hoja de ruta

Para quien continúe el trabajo. Cada mejora lleva el mismo formato: qué problema resuelve, cómo se implementaría,
cómo se mediría y qué riesgos tiene.

1. **Premisas que deja el trabajo:** lo que cualquier continuación debería dar por sentado. Por ejemplo: preguntar por
   la intención y no por el pedido, cortar la salida en el campo que decide, tratar el entorno de ejecución como parte
   de la configuración y no dar por buena una mejora que no se repite.
2. **Mejoras del detector:** ajuste fino con LoRA para que la probabilidad del token sirva como puntaje
   ([#176](https://github.com/Corchets/bitacora_tesis/issues/176)); rediseñar el filtro previo para detectar lo
   sensible en vez de estafas ([#149](https://github.com/Corchets/bitacora_tesis/issues/149)); bajar la demora.
3. **Mejoras de la entrada:** que el modelo escuche el audio directo; el tono de voz; robustez a ruido, códecs y
   altavoz.
4. **Cubrir los huecos del alcance:** la estafa que hace llamar a la persona, el contacto robado y el número de una
   entidad falsificado.
5. **Del prototipo al producto:** integración con un fabricante, preguntas sugeridas a la persona para separar una
   entidad real de un estafador (sondeo activo).
6. **Validaciones pendientes:** prueba con usuarios, efecto del ASR sobre la detección, revisión humana completa del
   corpus con acuerdo entre anotadores, llamadas reales en español.
7. **Hoja de ruta:** una tabla por horizonte (corto, mediano, largo) con qué hace falta para cada paso y de qué depende.

**Fuente:** issues con label `trabajo-futuro`; el capítulo 13 del borrador anterior (`INFORME-FINAL.md`, fuera de
Git), que ya explica cómo implementar cada mejora; el comentario de trabajo futuro en
[#53](https://github.com/Corchets/bitacora_tesis/issues/53). Antes de citar una fuente externa, verificarla.

### Referencias y anexos

- Referencias en un único estilo (a definir).
- **Anexo A:** prompt final del detector y del motivo
  ([`tarea_c_consejos.txt`](../../experiments/slm-directo/prompts/tarea_c_consejos.txt),
  [`salida_json_c.txt`](../../experiments/slm-directo/prompts/salida_json_c.txt) y
  [`motivo_c_corte.txt`](../../experiments/slm-directo/prompts/motivo_c_corte.txt)). Confirmar con el profesor que no
  lo considera código.
- **Anexo B:** una conversación de ejemplo anotada, con el riesgo línea por línea y el aviso.
- **Anexo C:** catálogo de escenarios y maniobras ([catálogo](../corpus/CATALOGO-ESCENARIOS.csv)).
- **Anexo D:** tablas detalladas que no entran en el cuerpo.
- **Anexo E:** cómo reproducir los resultados y levantar la demo, en prosa (sin código).

## 4. Decisiones del 2026-11-25

- La metodología va antes de las comparaciones, y se agregan la evaluación final con discusión (9) y las mejoras
  futuras con hoja de ruta (11).
- La evolución del proyecto va en las etapas (7); las mediciones lado a lado, en las comparaciones (8).
- El prompt final va en un anexo.
- El uso de asistentes de IA se menciona en la metodología.
- Se redacta en Markdown, versionado en este repositorio.

## 5. Lo que el texto no puede dar por resuelto

Mientras sigan así, describir lo que pasó sin presentarlo como decisión tomada:

- El alcance ([ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md)) y las reglas
  escritas antes de correr ([ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md)) no
  están aceptados, aunque la evaluación final se hizo con los dos.
- [D03](../gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución) excluye el modelo por API «ni como techo
  experimental», y la comparación con Gemini se corrió e integró igual. Antes de escribir el 8.10, el equipo tiene que
  actualizar D03.
- La meta 80/15 es del equipo y no es criterio de aprobación: la evaluación final corrió sin criterios de aprobación.
- [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) (taxonomía y evento crítico) sigue
  abierta: no hay referencia humana revisada ni medida de acuerdo.
- [Qué concluir de la evaluación final](../evaluacion/CONCLUSIONES-EVALUACION-FINAL.md) y la regla de pedido crítico no
  se discutieron en equipo.
- El título ([D13](../gestion/MAPA-DECISIONES.md#d13--título-definitivo)) y la forma de armar el PDF (archivos por capítulo, conversión y
  carátula) no están definidos.
