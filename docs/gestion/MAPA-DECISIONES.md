# Mapa de decisiones

**Destino:** Plan de Trabajo aprobado y ruta sin decisiones críticas abiertas para
ejecutar y evaluar el Proyecto Final de vishing.

Cada decisión debe tener una sola fuente de verdad. Cuando una decisión técnica amerite detalle, se crea un
ADR en [`docs/ingenieria/adr/`](../ingenieria/adr/) y desde aquí solo se enlaza su conclusión.
Plantilla en [PLANTILLA-ADR.md](../ingenieria/adr/PLANTILLA-ADR.md).

## Frontera: decisiones que pueden tomarse ahora

### D01 — Completar el contrato académico

- **Pregunta:** ¿qué fecha exacta, plantilla, estilo bibliográfico, entregables
  adicionales y proceso ético aplican al grupo?
- **Tipo:** conversación con profesor/tutor.
- **Responsable:** Ing. Ernesto Rico (Tutor) / Equipo.
- **Evidencia:** [minuta del 9 de septiembre](seguimientos/2026-09-09.md) y [REQUISITOS-ACADEMICOS.md](../propuesta/REQUISITOS-ACADEMICOS.md).
- **Desbloquea:** D02, D03, D10 y cronograma definitivo.
- **Estado:** resuelto (2026-09-09). Defensa presencial a fines de diciembre 2026; tutor asignado; ~100 págs promedio digital; sin comité de ética universitario formal.

### D02 — Definir problema, usuario y necesidad

- **Pregunta:** ¿quién necesita qué decisión o protección, en qué momento de la
  llamada y frente a qué daño?
- **Tipo:** decisión de alcance con investigación del dominio.
- **Responsable:** por autoasignación en GitHub (Issue #18).
- **Evidencia:** problema en cinco líneas, persona/actor y tres escenarios.
- **Bloqueada por:** ninguna (D01 resuelto).
- **Desbloquea:** D06 y requisitos.
- **Estado:** en curso. Borrador escrito el 2026-09-23 en
  [PLAN-DE-TRABAJO.md §2](../propuesta/PLAN-DE-TRABAJO.md#formulación-en-cinco-líneas), marcado como
  propuesta sin discutir; falta la validación de los cuatro integrantes. El foco en adultos mayores
  sigue en D12.

### D05 — Elegir la fuente de audio demostrable

- **Pregunta:** ¿cuál será la integración objetivo entre replay en streaming, VoIP
  controlado y micrófono/altavoz de laboratorio?
- **Tipo:** decisión técnica con validación de cátedra.
- **Responsable:** Equipo.
- **Evidencia:** [minuta del 9 de septiembre](seguimientos/2026-09-09.md) e [Issue #16](https://github.com/Corchets/bitacora_tesis/issues/16).
- **Desbloquea:** arquitectura y requisitos del prototipo.
- **Estado:** resuelto (2026-09-09). Replay como base experimental reproducible obligatoria; llamada VoIP propia como integración objetivo del prototipo; altavoz externo despriorizado (no separa canales); PSTN universal fuera de alcance.

Las cinco opciones sobre la mesa, con el detalle técnico en
[ALTERNATIVAS-CAPTURA-AUDIO.md](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md):

| Opción                                                  | Qué demuestra                                               | Estado post 9 de septiembre                       |
| ------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------- |
| Motor sobre grabaciones reproducidas como stream        | Algoritmo completo, incrementalidad, latencia, anticipación | **Base experimental obligatoria aprobada**        |
| App con llamada VoIP controlada (el audio es de la app) | Funcionamiento durante una conversación real                | **Objetivo principal del prototipo aprobado**     |
| Micrófono/altavoz en laboratorio                        | Concepto interactivo rápido                                 | **Despriorizado** (mezcla canales / mala calidad) |
| AOSP / root / app de sistema                            | Acceso privilegiado a telefonía                             | Solo _stretch goal_                               |
| App stock escuchando cualquier llamada del dialer       | Producto equivalente a integración OEM                      | **Fuera de alcance confirmado**                   |

### D06 — Definir la gobernanza de datos

- **Pregunta:** ¿qué se grabará, con qué consentimiento, dónde vivirá, quién
  accederá, qué podrá publicarse y cuándo se eliminará?
- **Tipo:** decisión ética y metodológica interna.
- **Responsable:** por autoasignación (Issue #22).
- **Evidencia:** plan de datos y formulario de consentimiento informado simple.
- **Desbloquea:** corpus piloto.
- **Estado:** abierto (UNSTA no exige trámite formal; autogestión de consentimiento con voluntarios).

## Decisiones precisas de alcance y experimentación

### D03 — Congelar alcance y contribución

- **Pregunta:** ¿cuál es el núcleo obligatorio, cuáles son los stretch goals y qué
  queda fuera de alcance?
- **Evidencia:** [Plan de Trabajo §6 y §15](../propuesta/PLAN-DE-TRABAJO.md) y [minuta del 9 de septiembre](seguimientos/2026-09-09.md).
- **Salida:** objetivos, aporte y lista explícita de exclusiones.
- **Estado:** resuelto (2026-09-09). Núcleo obligatorio y exclusiones (no PSTN, no deepfakes, no biometría) aprobados.

### D04 — Aprobar preguntas e hipótesis

- **Pregunta:** ¿qué afirmaciones se evaluarán y qué observación podría refutarlas?
- **Evidencia:** [Plan de Trabajo §5 y §15](../propuesta/PLAN-DE-TRABAJO.md) y [PREGUNTAS-DE-INVESTIGACION.md](../investigacion/PREGUNTAS-DE-INVESTIGACION.md).
- **Salida:** PI1–PI2 aprobadas, evaluación E1 diagnóstica y E2 secundaria.
- **Estado:** resuelto (2026-09-09). Aprobadas por el tutor sin objeciones.

### D07 — Aprobar taxonomía y evento crítico

- **Pregunta:** ¿qué maniobras y pedidos se anotan, y cómo se marcan `T_R` y `T_C`?
- **Bloqueada por:** D02, D04 y D06.
- **Salida:** manual de anotación v0 probado por los cuatro integrantes.

Hay una propuesta concreta de dos capas multi-label de 6 etiquetas cada una en
[MANUAL-ANOTACION.md](../datos-etica/MANUAL-ANOTACION.md), con el principio de no superar la docena
de etiquetas: en cuatro meses las clases raras destruyen el análisis estadístico. Falta decidir si se
adoptan tal cual o se derivan de un relevamiento propio de modalidades argentinas (UFECI, ANSES,
PAMI, BCRA).

Sobre el evento crítico, la definición de `T_A`, `T_R` y `T_C` y por qué hacen falta las tres marcas
está en [METRICAS.md](../evaluacion/METRICAS.md). Dos puntos que esta decisión tiene que cerrar:
`T_A` se define con histéresis (no el primer cruce del umbral, sino el primero que se sostiene dos
actualizaciones), y hay que elegir si `Preventive@δ` se mide contra `T_C` o contra `T_R`.

### D08 — Congelar protocolo experimental

- **Pregunta:** ¿cómo se muestrea, divide y evalúa sin fuga de información?
- **Bloqueada por:** D04 y D07.
- **Salida:** splits, baselines, métricas, seeds, test congelado y amenazas.

Este punto puede determinar la credibilidad completa de los resultados: si dos variantes del mismo
guion caen una en train y otra en test, el modelo ya vio el escenario. El procedimiento de división
está en [METODO-CREACION-CORPUS.md §9](../datos-etica/METODO-CREACION-CORPUS.md#9-división-de-datos)
y las definiciones de métrica en [METRICAS.md](../evaluacion/METRICAS.md). Adoptarlo es barato ahora
y carísimo de arreglar después.

Falta fijar además la restricción de falsos positivos **antes** de medir. El anteproyecto la
menciona pero no la define, y sin ese número la hipótesis no es falsable.

- **Recorte de trabajo (2026-09-16, no cierra D08):**
  [VENTANA-DE-CONTEXTO-Y-ALERTA.md](../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md).
  Deriva el margen de aceptación desde el máximo de llamadas legítimas con alerta, en lugar de
  fijar un umbral a ojo, y muestra cómo se acumulan las falsas alarmas con cada actualización.
  Propone además ventana deslizante con decaimiento y un registro conjunto de eventos.
  Los números salen de llamadas sintéticas: prueban el mecanismo, no miden rendimiento.
  Issue [#23](https://github.com/Corchets/bitacora_tesis/issues/23).

### D09 — Elegir ASR y detector

- **Pregunta:** ¿qué combinación satisface la calidad y el presupuesto de cómputo?
- **Bloqueada por:** D05, D07 y benchmark piloto.
- **Salida:** decisión basada en WER/recall crítico, F1/AUPRC, latencia y memoria.
- **Candidatos a evaluar (mapa inicial):** sherpa-onnx, Vosk y whisper.cpp para ASR; TF-IDF como baseline
  obligatorio y BETO o RoBERTuito para español. La decisión sale del benchmark, no de una
  preferencia previa.
- **Recorte de trabajo (2026-09-15/16, no cierra D09):**
  [PRIMERA-INVESTIGACION-MODELOS.md](../investigacion/PRIMERA-INVESTIGACION-MODELOS.md).
  Catálogo de bajada = Hugging Face (consulta 2026-09-16). ASR del recorte:
  Moonshine tiny-es (baja) y Zipformer Kroko ONNX (media/alta). Whisper solo comparación.
  Vosk oficial queda fuera del recorte Hub. Detector: ALBETO tiny/base, DistilBETO, RoBERTuito.
  Spike de laboratorio: [issue #28](https://github.com/Corchets/bitacora_tesis/issues/28).

### D10 — Congelar estructura de entrega y defensa

- **Pregunta:** ¿qué índice, anexos, paquete reproducible, duración y demo se
  entregan?
- **Bloqueada por:** D01 y resultados de evaluación.
- **Salida:** checklist final aceptado por el tutor.

### D11 — Análisis lingüístico o también acústico

- **Pregunta:** ¿el detector trabaja solo sobre la transcripción del ASR, o también sobre rasgos
  bioacústicos (tono, estrés vocal, MFCCs)?
- **Bloqueada por:** D05. Si la captura termina siendo acústica por altavoz, la reverberación, el
  ruido y la cancelación de eco del hardware destruyen justamente los rasgos que el análisis
  acústico necesita, y la pregunta se responde sola.
- **Salida:** alcance del stack de features y, con él, el esfuerzo de las próximas semanas.
- **Recomendación del deep research:** solo NLP sobre la transcripción, con lo bioacústico como
  trabajo futuro declarado en las conclusiones. Ver
  [SINTESIS-ESTADO-DEL-ARTE.md](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md).

### D12 — Encuadre del foco en adultos mayores

- **Pregunta:** ¿se mantiene el foco en adultos mayores y con qué justificación?
- **Bloqueada por:** D02.
- **Salida:** justificación reescrita en el Plan de Trabajo.
- **Detalle:** el deep research no pide abandonar el foco, pide **cambiar la justificación**: de
  "son los más afectados" —no demostrado para Argentina— a "gravedad potencial de las pérdidas y
  exposición a estafas de suplantación". También advierte no convertir el reclutamiento de adultos
  mayores en un bloqueo del corpus: mejor incluirlos en evaluación y en la prueba de usabilidad.
  Esta corrección ya quedó integrada en el Plan de Trabajo.

### D13 — Título definitivo

- **Pregunta:** ¿cuál es el título final de la tesis?
- **Bloqueada por:** D03 y la composición geográfica real del corpus.
- **Salida:** título consistente con lo que el corpus efectivamente cubre.
- **Regla:** no cerrarlo antes de tener el corpus. Un título que promete "español argentino" obliga
  a un corpus que lo sostenga.

## Decisiones cerradas

- **Institución y equipo:** UNSTA, Ingeniería en Informática, Plan 2008; Albarracín
  Ignacio, Antenucci Mateo, Grosso Luciano y Villalobo Evaristo están autorizados
  como grupo de cuatro.
- **Formato base:** entrega digital, A4, carilla simple, portada institucional,
  resúmenes español/inglés, cuerpo técnico y unas 100 páginas como referencia.
- **Horizonte:** entrega hacia fines de diciembre de 2026; falta el día exacto. El
  equipo trabaja contra un cierre interno propio el 1 de diciembre; el reparto de
  semanas está en [PLAN-DE-TRABAJO.md §11](../propuesta/PLAN-DE-TRABAJO.md#11-cronograma)
  y es propuesta sin discutir por los cuatro.
- **No basar la tesis en capturar cualquier llamada PSTN desde una app Android
  ordinaria:** la plataforma reserva esas fuentes a componentes privilegiados.
- **Separar motor e integración:** replay en streaming es la base experimental;
  VoIP controlado es la integración preferida si el spike confirma viabilidad.
- **No hacer detección de deepfake en el núcleo:** responde una pregunta distinta
  a detectar manipulación y pedidos peligrosos.
- **Mantener baselines simples:** reglas y TF–IDF son comparadores obligatorios.
- **Criterios de prefactibilidad (#24):** Mateo informó el 2026-09-22 que el equipo revisó y aprobó
  los presupuestos y umbrales de [PREFACTIBILIDAD-TECNICA.md](../investigacion/PREFACTIBILIDAD-TECNICA.md)
  como punto de partida para medir, no como evidencia de rendimiento. D09 y la elección de modelos
  permanecen abiertas; la viabilidad en Android requiere medición en ese entorno.

## No especificado todavía

- Diseño exacto del warning y método de evaluación con usuarios.
- Modelo de estado temporal que competirá con el acumulador probabilístico.
  Recorte de grilling: red de riesgo ve **solo el último turno**; el riesgo de la
  llamada es el **máximo de los últimos k=3 turnos**, con histéresis de `T_A`,
  **salvo** pedido crítico por reglas (capa 2), que avisa ya.
  Ventana de la red en v0: **turno completo**; achique (5 s / 64 tokens) a medir
  en el piloto. Desarrollo: **un programa, config por gama**; se arranca con
  **alta** (Zipformer Kroko Hub + RoBERTuito; TF–IDF de baseline).
  Baja `asr`: Moonshine tiny-es. Media `asr`: Zipformer Kroko.
  Hilos de partida: baja 2 (1+1), media 4 (3+1), alta 6 (4+2).
  RAM: **256 / 512 / 1024 MB**. Ver
  [PRIMERA-INVESTIGACION-MODELOS.md](../investigacion/PRIMERA-INVESTIGACION-MODELOS.md).
- Dispositivo Android concreto para la demo y mediciones de rendimiento, batería y temperatura.
  Los presupuestos de laboratorio ya están definidos en
  [PREFACTIBILIDAD-TECNICA.md](../investigacion/PREFACTIBILIDAD-TECNICA.md), pero no prueban
  rendimiento móvil.
- Posibilidad y licencia de publicación del corpus o solo sus metadatos.
- Técnica estadística final, que depende del tamaño y distribución obtenidos.

## Fuera de alcance provisional

- Captura universal de llamadas PSTN en Android stock.
- iOS, múltiples idiomas, caller-ID reputation, detección de malware y análisis de
  mensajes de texto.
- Detección de voz sintética o identidad biométrica del interlocutor.
- Backend de producción, publicación en Play Store y operación comercial.
- Estudio clínico o generalización poblacional con adultos mayores.

## Regla de uso

En cada seguimiento se puede cerrar una o dos decisiones con evidencia. No se
discute tecnología bloqueada por una decisión anterior. Al cerrar una decisión:

1. registrar fecha, participantes, alternativas y evidencia;
2. escribir conclusión y consecuencias;
3. actualizar bloqueos y promover lo que ya pueda especificarse;
4. cambiar el Plan de Trabajo si altera alcance, tiempo o entregables;
5. pedir validación al tutor si afecta el contrato académico o ético.
