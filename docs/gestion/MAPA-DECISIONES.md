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
- **Responsable:** equipo.
- **Evidencia:** problema en cinco líneas, persona/actor y tres escenarios.
- **Bloqueada por:** ninguna (D01 resuelto).
- **Desbloquea:** D06 y requisitos.
- **Estado:** ratificada por el equipo en [PLAN-DE-TRABAJO.md §2](../propuesta/PLAN-DE-TRABAJO.md#formulación-en-cinco-líneas)

### D05 — Elegir la fuente de audio demostrable

- **Pregunta:** ¿cuál será la integración objetivo entre replay en streaming, VoIP
  controlado y micrófono/altavoz de laboratorio?
- **Tipo:** decisión técnica con validación de cátedra.
- **Responsable:** Equipo.
- **Evidencia:** [minuta del 9 de septiembre](seguimientos/2026-09-09.md).
- **Desbloquea:** arquitectura y requisitos del prototipo.
- **Estado:** resuelto (2026-09-09). Replay como base experimental reproducible obligatoria; llamada VoIP propia como integración objetivo del prototipo; altavoz externo despriorizado (no separa canales); PSTN universal fuera de alcance.

Las cinco opciones con el detalle técnico se encuentran en [ALTERNATIVAS-CAPTURA-AUDIO.md](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md):

### D06 — Definir corpus y piloto

- **Pregunta:** ¿qué conversaciones se producirán y con qué piloto se probará el método?
- **Estado:** selección inicial resuelta. Se producirán conversaciones ficticias
  fraudulentas y legítimas comparables, interpretadas por el equipo o familiares.
- **Piloto:** 14 conversaciones iniciales, siete de cada clase, con hasta seis
  repeticiones dirigidas por problemas concretos. No fija el tamaño del corpus final.
- **Fuente:** [método y selección del piloto](../corpus/METODO-CREACION-CORPUS.md#6-piloto)
  y [catálogo](../corpus/CATALOGO-ESCENARIOS.csv).
- **Ejecución:** [primer par #39](https://github.com/Corchets/bitacora_tesis/issues/39)
  y [piloto completo #54](https://github.com/Corchets/bitacora_tesis/issues/54).
  El piloto permite revisar escenarios, calidad de grabación, anotación y costo.
- **Pendiente en D08:** tamaño y composición final, particiones y criterio de parada.
  El resguardo de los materiales se consulta en el método; no exige otro documento.

## Decisiones precisas de alcance y experimentación

### D03 — Congelar alcance y contribución

- **Pregunta:** ¿cuál es el núcleo obligatorio, cuáles son los stretch goals y qué
  queda fuera de alcance?
- **Evidencia:** [Plan de Trabajo §6](../propuesta/PLAN-DE-TRABAJO.md#6-alcance) y [minuta del 9 de septiembre](seguimientos/2026-09-09.md).
- **Salida:** objetivos, aporte y lista explícita de exclusiones.
- **Estado:** resuelto (2026-09-09). Núcleo obligatorio y exclusiones (no PSTN, no deepfakes, no biometría) aprobados.
- **Precisión de alcance (2026-10-04, confirmada por Mateo):** el detector conserva
  contexto de la llamada actual y recibe solo su contenido transcripto. Agenda,
  historial, memoria entre sesiones, reputación y dirección entrante/saliente quedan
  fuera de sus entradas. La ventana y la política de alerta siguen abiertas en D08.
- **Público (2026-10-04, confirmado por Mateo):** sin foco etario específico. Se retira
  D12 como decisión pendiente. La participación de personas adultas en el corpus es
  una condición de producción, no una promesa de rendimiento para un grupo etario.

### D04 — Aprobar preguntas e hipótesis

- **Pregunta:** ¿qué afirmaciones se evaluarán y qué observación podría refutarlas?
- **Evidencia:** [Plan de Trabajo §5](../propuesta/PLAN-DE-TRABAJO.md#5-preguntas-de-investigación) y [PREGUNTAS-DE-INVESTIGACION.md](../investigacion/PREGUNTAS-DE-INVESTIGACION.md).
- **Salida:** PI1–PI2 aprobadas, evaluación E1 diagnóstica y E2 secundaria.
- **Estado:** resuelto (2026-09-09).

### D07 — Aprobar taxonomía y evento crítico

- **Pregunta:** ¿qué referencia humana necesita la evaluación y cómo se anotan
  pedidos, cumplimiento y evidencia sin confundirlos con solicitudes legítimas?
- **Estado:** abierta. La referencia mínima del piloto fue acordada por Mateo el
  2026-10-04: clase por conversación, `T_R`/`T_C` cuando correspondan y evidencia
  seleccionada, sin etiquetado exhaustivo por turno. Falta probar las reglas con
  el piloto y resolver sus ambigüedades.
- **Para empezar:** una versión de trabajo del manual con criterios aplicables a
  los primeros casos. El piloto prueba esa versión; no necesita D07 cerrada.
- **Para cerrar:** manual probado en una muestra común por los cuatro integrantes,
  anotaciones originales conservadas y desacuerdos adjudicados.
- **Fuente:** [MANUAL-ANOTACION.md](../corpus/MANUAL-ANOTACION.md). Sus dos capas de
  etiquetas son un vocabulario candidato para fichas y explicaciones. El
  [catálogo](../corpus/CATALOGO-ESCENARIOS.csv) aporta casos para
  contrastar sus definiciones.

Las definiciones de las marcas viven en [METRICAS.md](../evaluacion/METRICAS.md).
D07 precisa cómo observar `T_R` y `T_C`; D08 fija la política que produce `T_A`.

### D08 — Congelar protocolo experimental

- **Pregunta:** ¿cómo se muestrea, divide y evalúa sin fuga de información?
- **Estado:** abierta. Puede prepararse el diseño con el piloto; se congela antes de
  la evaluación final, con D07 resuelta y una configuración elegida sobre desarrollo.
- **Salida:** composición del corpus, particiones, comparadores, política de alerta,
  métricas y criterio de interpretación definidos; test reservado y procedimiento repetible.
- **Antes de ampliar:** acordar separación de semillas y variantes en
  [#55](https://github.com/Corchets/bitacora_tesis/issues/55). Ver
  [método del corpus §9](../corpus/METODO-CREACION-CORPUS.md#9-división-de-datos).
- **Antes del test:** congelar el protocolo en
  [#33](https://github.com/Corchets/bitacora_tesis/issues/33): unidades e instantes de evaluación, falsas alarmas,
  referencias temporales, configuración e incertidumbre a informar. Ver
  [METRICAS.md](../evaluacion/METRICAS.md#5-pendientes-para-congelar-la-evaluación).
  Las preguntas caracterizan desempeño; no requieren inventar un umbral de éxito.
- **Antecedentes:** [ventana y alerta](../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md)
  y [diseño integrado](../investigacion/DISENO-INTEGRADO.md) proponen mecanismos.
  Sus números sintéticos no prueban rendimiento ni congelan el protocolo.

### D09 — Elegir ASR y detector

- **Pregunta:** ¿qué combinación satisface la calidad y el presupuesto de cómputo?
- **Ejecución:** [issue #51](https://github.com/Corchets/bitacora_tesis/issues/51).
- **Estado:** abierta. La elección final necesita audio y referencia del piloto,
  comparaciones sobre desarrollo y mediciones del flujo completo.
- **Salida:** ASR, detector y configuración elegidos según errores de transcripción,
  detección, falsas alarmas, tiempos y memoria, con límites del hardware medido.
- **Línea base vigente:** reglas solas. Ningún encoder, modelo generativo, cascada,
  entrenamiento ni conjunto de gamas está impuesto como arquitectura final.
- **Material para consultar cuando corresponda:**
  [recorte inicial de modelos](../investigacion/PRIMERA-INVESTIGACION-MODELOS.md),
  [estrategia NLP](../investigacion/ESTRATEGIA-MODELOS-NLP-Y-COMPRESION.md) y
  [contraste con el laboratorio](../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md).
  Son antecedentes de candidatos y pruebas, no requisitos nuevos. La comparación
  debe declarar qué código y datos reutiliza y qué cambió.

### D10 — Congelar estructura de entrega y defensa

- **Pregunta:** ¿qué índice, anexos, paquete reproducible, duración y demo se
  entregan?
- **Bloqueada por:** D01 y resultados de evaluación.
- **Salida:** checklist final aceptado por el tutor.

### D11 — Análisis lingüístico o también acústico

- **Estado:** cerrada (2026-10-04), confirmada por Mateo.
- **Decisión:** detector sobre transcripción y contexto de la llamada actual.
  El audio se usa para ASR y mediciones; los rasgos acústicos quedan como trabajo futuro.

### D13 — Título definitivo

- **Pregunta:** ¿cuál es el título final de la tesis?
- **Bloqueada por:** D03 y la composición geográfica real del corpus.
- **Salida:** título consistente con lo que el corpus efectivamente cubre.
- **Regla:** no cerrarlo antes de tener el corpus. Un título que promete "español argentino" obliga
  a un corpus que lo sostenga.

### D14 — Ayuda memoria visual del proyecto

- **Pregunta:** ¿cómo facilitar al equipo de cuatro la reincorporación al trabajo, la consulta de hitos y la entrada a los issues sin añadir sobrecarga de gestión en GitHub ni crear un segundo backlog?
- **Tipo:** herramienta de coordinación interna y consulta del repositorio.
- **Responsable:** Mateo Antenucci / Equipo.
- **Evidencia:** [issue #57](https://github.com/Corchets/bitacora_tesis/issues/57), [README de ayuda-memoria](../../ayuda-memoria/README.md), [sistema de diseño](../../ayuda-memoria/DESIGN.md) y [skill de proyecto](../../.agents/skills/actualizar-ayuda-memoria/SKILL.md).
- **Desbloquea:** incorporación fluida del equipo al hito H2 sin fricción ni reconstrucción del repositorio.
- **Estado:** resuelta (2026-10-07).
- **Conclusión:** sitio web estático (`ayuda-memoria/`, HTML/CSS/JS con generador Node sin dependencias de aplicación) con vistas para `laboratorio-main` (entrada principal) y `main`. Muestra hitos, issues abiertos agrupados, roadmap, glosario y briefs de arranque para H2 (#19, #32, #39, #50, #54). Los briefs son orientaciones mantenidas en la web, no campos obligatorios de los issues en GitHub ni un segundo backlog. Se actualizan mediante la skill explícita `$actualizar-ayuda-memoria` a nivel proyecto. El build consulta datos de GitHub y archivos de cada commit sin publicar copias viejas. Publicación por enlace en Vercel alimentada por workflow ante pushes y cambios en issues (requiere secrets de despliegue). No altera el alcance de tesis, no ejecuta IA desatendida y no cierra D07/D08/D09.

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
- **Línea base registrada:** reglas solas, según el cambio documental del
  [2026-09-29](https://github.com/Corchets/bitacora_tesis/commit/9eda2948321466124ec4789882882fb0ab8ce154).
  Ese cambio también retiró TF–IDF basándose en el laboratorio. La justificación
  debe revisarse en D09: una prueba con datos reutilizados o fuga no demuestra que
  el método sea inútil en general.

  > **Estado: propuesta sin discutir.** Mantener reglas como referencia inicial y
  > revisar la exclusión general de TF–IDF cuando se elijan comparadores en
  > [D09](#d09--elegir-asr-y-detector). No hace falta agregarlo como trabajo obligatorio.
- **Criterios de prefactibilidad (#24):** Se definieron presupuestos y umbrales de [PREFACTIBILIDAD-TECNICA.md](../investigacion/PREFACTIBILIDAD-TECNICA.md)
  como punto de partida para medir, no como evidencia de rendimiento. D09 y la elección de modelos
  permanecen abiertas; la viabilidad en Android requiere medición en ese entorno.

## No especificado todavía

- Diseño exacto del warning y método de evaluación con usuarios.
- Modelo de estado temporal, ventana y política final de alerta: los valores de
  [VENTANA-DE-CONTEXTO-Y-ALERTA.md](../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md)
  son hipótesis de laboratorio, no D08 cerrada. Las configuraciones de memoria e hilos
  de [PREFACTIBILIDAD-TECNICA.md](../investigacion/PREFACTIBILIDAD-TECNICA.md) son
  presupuestos de medición, no evidencia de que una combinación de modelos funcione
  en Android. El [recorte #29](https://github.com/Corchets/bitacora_tesis/issues/29)
  tampoco cierra D09.
  **Observación (2026-09-18, issue #23):** con el máximo de 3 turnos, "dos veces seguidas" se
  cumple con un solo pico y la histéresis no reduce las falsas alarmas. Compite con el riesgo con
  decaimiento y doble umbral de la ventana de contexto. Cuenta y opciones en
  [VENTANA-DE-CONTEXTO-Y-ALERTA.md §11](../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md#11-reconciliación-con-el-contador-del-recorte-de-modelos). Propuesta sin discutir.
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
