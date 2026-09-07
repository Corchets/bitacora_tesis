# Plan maestro del Proyecto Final

**Proyecto:** detección incremental y explicable de vishing en español  
**Universidad:** UNSTA — Ingeniería en Informática, Plan 2008  
**Equipo:** Albarracín Ignacio, Antenucci Mateo, Grosso Luciano y Villalobo Evaristo  
**Versión:** 0.2 — 2 de septiembre de 2026  
**Próxima clase:** miércoles 9 de septiembre de 2026  
**Entrega objetivo:** últimos días de diciembre de 2026; fecha exacta pendiente  
**Estado:** propuesta para discutir y aprobar con el profesor/tutor

## 1. Respuesta ejecutiva

El proyecto debe administrarse como dos trabajos inseparables:

1. **Un proyecto de ingeniería de software:** problema, interesados, requisitos,
   alternativas, arquitectura, implementación, pruebas y producto demostrable.
2. **Un estudio empírico:** preguntas de investigación, corpus y protocolo,
   baselines, experimento reproducible, resultados, amenazas a la validez y
   conclusiones.

La meta no es demostrar que “la IA funciona”, sino responder con evidencia si un
detector local puede advertir vishing en español con suficiente precisión y
anticipación, dentro de un escenario de audio que una aplicación común pueda
capturar legítimamente.

Antes de desarrollar, el equipo debe cerrar alcance, preguntas, unidad de análisis,
fuente de audio, estrategia de datos, protocolo ético, criterios de éxito y fecha
real de entrega. Las elecciones de ASR, modelo y framework vienen después de un
benchmark pequeño; no son decisiones iniciales por preferencia personal.

## 2. Contrato académico disponible

El proyecto corresponde a **Ingeniería en Informática, Plan 2008, UNSTA**. La web
oficial confirma que la carrera culmina con un **Proyecto Final Integrador** y que
el perfil incluye conducción de proyectos, software, inteligencia artificial y
compromiso ético. Fuente: [Ingeniería en Informática — UNSTA](https://www.unsta.edu.ar/ingenieria/ingenieria-informatica/).

No se dispone todavía de reglamento, plantilla ni rúbrica. Para esta planificación,
las instrucciones verbales del profesor constituyen el requisito vigente:

- entrega digital;
- documento A4, carilla simple;
- portada con logo UNSTA, nombre del proyecto, integrantes, tutor y año;
- resumen en español e inglés;
- agradecimientos opcionales;
- introducción, objetivos, marco teórico, arquitecturas, tecnologías,
  comparaciones, metodologías utilizadas, etapas y conclusión;
- extensión habitual aproximada de 100 páginas;
- grupo de cuatro autorizado;
- entrega hacia fines de diciembre de 2026.

El [Repositorio Digital Institucional de UNSTA](https://rdi.unsta.edu.ar/collections/6fbdcceb-6920-47f6-935d-7183c5692153)
contiene proyectos finales de Ingeniería Informática. Uno de los ejemplos públicos
tiene 103 páginas, lo que es coherente con la orientación recibida, pero por su
antigüedad no se tomará como plantilla obligatoria.

Quedan cinco confirmaciones para la clase del 9 de septiembre:

- fecha exacta de entrega y eventuales hitos intermedios;
- tutor y mecanismo para aprobar cambios de alcance;
- estilo bibliográfico, tipografía/márgenes y plantilla si existiera;
- contenido adicional esperado: código, manuales, dataset, ejecutable, video o
  presentación;
- necesidad de aprobación previa del protocolo de participantes y consentimiento.

## 3. Definición de destino

El proyecto estará listo cuando el equipo pueda defender, con artefactos
reproducibles, que:

- definió un problema y beneficiario concretos;
- construyó y documentó un corpus controlado de vishing y llamadas legítimas en
  español, sin datos reales de víctimas;
- comparó baselines honestos y un detector incremental;
- midió falsos positivos, desempeño con transcripción manual y ASR, latencia y
  anticipación respecto de una acción crítica;
- ejecutó la inferencia localmente en un entorno de audio permitido;
- produjo advertencias explicables y evaluó al menos su comprensión básica;
- documentó requisitos, arquitectura, implementación, pruebas, decisiones,
  riesgos, privacidad, limitaciones y contribuciones individuales;
- entregó un Informe Final trazable al Plan de Trabajo aprobado y una demo de
  defensa con plan de contingencia.

## 4. Decisiones que deben cerrarse antes de escalar el trabajo

| Orden | Decisión | Resultado requerido | Fecha límite |
|---:|---|---|---|
| 1 | Entregables y calendario | Requisitos parciales consolidados y cinco confirmaciones al profesor | 9 de septiembre |
| 2 | Problema, usuario y escenario | Problema en 5 líneas, usuario primario y escenario de uso | 9 de septiembre |
| 3 | Alcance y aporte | Núcleo, objetivos de extensión y fuera de alcance | Clase 2 |
| 4 | Preguntas de investigación | Dos preguntas centrales, una evaluación diagnóstica y un objetivo secundario | 9 de septiembre |
| 5 | Acceso al audio | Comparación de altavoz, replay, VoIP y acceso privilegiado | 9 de septiembre |
| 6 | Datos y ética | Fuente del corpus, consentimiento, retención y publicación | Antes de grabar |
| 7 | Taxonomía y evento crítico | Manual v0 y definición de `T_A`, `T_R`, `T_C` | Ciclo 2 |
| 8 | Protocolo experimental | Splits, baselines, métricas y test congelado | Ciclo 3 |
| 9 | Arquitectura | Interfaces de audio, ASR, detector, estado y warning | Ciclo 3 |
| 10 | Tecnología | ASR y modelo elegidos mediante benchmark | Ciclo 4 |

El detalle y estado de cada decisión vive en [MAPA-DECISIONES.md](MAPA-DECISIONES.md).

## 5. Preguntas de investigación provisionales

Se proponen dos preguntas centrales, que deben aprobarse con el tutor:

- **PI1 — Detección parcial:** ¿con qué desempeño puede detectarse vishing usando
  únicamente el prefijo disponible de una conversación en español?
- **PI2 — Anticipación:** ¿con cuánto margen respecto del primer pedido riesgoso y
  de la primera acción de cumplimiento puede emitirse una alerta estable?
- **E1 — Impacto del ASR:** comparación diagnóstica obligatoria entre transcripción
  manual y automática; no es una pregunta central.
- **E2 — Explicación:** objetivo secundario sobre la fidelidad del motivo mostrado.

No son preguntas para entrevistar personas. Son las preguntas que los experimentos
deben responder al final. Su explicación, variables y ejemplos están en
[PREGUNTAS-DE-INVESTIGACION.md](../investigacion/PREGUNTAS-DE-INVESTIGACION.md).

## 6. Qué investigar

### Línea A — Requisitos institucionales

- Reglamento, plantilla y rúbrica vigentes.
- Proyectos finales aprobados de la misma carrera y expectativas del tribunal.
- Procedimiento de aprobación, entrega, correcciones, defensa y repositorio.

**Termina cuando:** el equipo puede convertir cada obligación en un entregable y
una fecha. No se usan reglamentos de otras carreras como si fueran aplicables.

### Línea B — Dominio y contexto argentino

- Definición operacional de vishing y frontera con spam, spoofing y deepfake.
- Familias locales de fraude, entidades suplantadas, pedidos riesgosos y medidas de
  protección comunicadas por organismos oficiales.
- Población beneficiaria, contexto de uso y daño que se intenta evitar.

**Termina cuando:** existe una taxonomía de escenarios con respaldo y cada escenario
del corpus tiene justificación.

### Línea C — Estado del arte técnico

- Datasets de vishing y sus sesgos; especialmente idioma, fuente, balance y nivel
  de anotación.
- Detección offline frente a incremental; evidencia semántica, acústica y temporal.
- ASR local en español, VAD/segmentación, clasificación liviana, calibración e
  inferencia móvil.
- Intervenciones y fatiga de alertas; sistemas comerciales solo como comparación,
  no como evidencia experimental reproducible.

La revisión de 2025 describe escasez de datos, necesidad de integración entre
señales y dificultad de intervenir en tiempo real sin fatiga de alertas:
[Triantafyllopoulos et al., 2025](https://doi.org/10.1016/j.csl.2025.101802).
VishGPT confirma que la detección en tiempo real sigue siendo un problema activo y
que los datos limitados condicionan el diseño:
[Ampel, Samtani y Chen, 2026](https://aisel.aisnet.org/misq/vol50/iss2/9/).

**Termina cuando:** se puede escribir una tabla de trabajos relacionados que deje
claro qué pregunta no responden y cuál será la comparación de la tesis.

### Línea D — Metodología y validez

- Construcción de corpus simulado, muestreo, consentimiento y pseudonimización.
- Manual de anotación, desacuerdos, acuerdo interanotador y adjudicación.
- Split por familia de guion y, si es posible, por hablante; prevención de leakage.
- Baselines, calibración, análisis estadístico, ablations y amenazas a la validez.
- Métricas de clasificación, falsa alarma por llamada/hora, WER y términos críticos,
  latencia y métricas de anticipación.

Los [estándares empíricos de ACM SIGSOFT](https://www2.sigsoft.org/EmpiricalStandards/docs/standards)
ofrecen checklists separados para experimentos, data science y revisiones. PRISMA
solo debe adoptarse si el equipo declara una revisión sistemática o de alcance; no
es necesario convertir una revisión de antecedentes del proyecto en otra tesis.

**Termina cuando:** otra persona puede reproducir la selección de literatura, el
split, el entrenamiento y cada tabla a partir de archivos versionados.

### Línea E — Factibilidad, plataforma y privacidad

- Captura de audio permitida en Android, replay y VoIP controlado.
- Rendimiento en al menos un dispositivo físico objetivo.
- Flujo y retención de audio/transcripciones, acceso, backup y eliminación.
- Consentimiento separado para usar, compartir transcripciones y publicar audio.

Android reserva la captura de `VOICE_CALL`, `VOICE_UPLINK` y `VOICE_DOWNLINK` a
componentes con un permiso no disponible para aplicaciones ordinarias:
[Android `MediaRecorder.AudioSource`](https://developer.android.com/reference/android/media/MediaRecorder.AudioSource)
y [reglas para compartir entrada de audio](https://developer.android.com/media/platform/sharing-audio-input).
Por ello, el núcleo experimental será replay en streaming y la integración se hará
en un flujo controlado; escuchar cualquier llamada PSTN queda fuera de alcance.

Las voces y transcripciones son datos personales. La [Ley 25.326 actualizada](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion)
y la [guía de derechos de la AAIP](https://www.argentina.gob.ar/aaip/datospersonales/derechos)
obligan a tratar consentimiento, finalidad, responsables, destinatarios, seguridad
y eliminación como decisiones previas a la captura, no como un apéndice tardío.

## 7. Roadmap hasta diciembre

La planificación utiliza el miércoles 9 de septiembre como primer gate y reserva
las últimas dos semanas para correcciones. La fecha final debe confirmarse.

| Ciclo | Fechas | Objetivo | Evidencia para mostrar al profesor | Gate de salida |
|---:|---|---|---|---|
| 0 | 2–9 sep | Definir la ruta | Plan de Trabajo v1, PI1–PI2, evaluaciones, alternativas de audio y preguntas | profesor corrige/aprueba dirección |
| 1 | 10–23 sep | Alcance y factibilidad vertical | WAV→ASR local→regla→alerta, problema, usuario, requisitos y arquitectura v0 | cadena técnica y alcance base aprobados |
| 2 | 24 sep–7 oct | Piloto de datos | consentimiento, taxonomía, manual y 10–20 diálogos doblemente anotados | se autoriza escalar el corpus |
| 3 | 8–21 oct | Benchmark y baselines | 30–50 conversaciones, comparación ASR, reglas y TF–IDF, primer gráfico riesgo-tiempo | ASR y dataset elegidos por evidencia |
| 4 | 22 oct–4 nov | Corpus y detector incremental | dataset v1, hard negatives, modelo principal y acumulador temporal | corpus casi congelado; pipeline reproducible |
| 5 | 5–18 nov | Integración | audio→ASR→riesgo→warning en entorno controlado; latencia y memoria | demo end-to-end repetible |
| 6 | 19 nov–2 dic | Congelamiento y evaluación | test congelado, gold vs ASR, falsos positivos, anticipación y ablations | resultados finales reproducidos |
| 7 | 3–16 dic | Informe y defensa | informe completo, análisis de errores, amenazas, presentación y video de respaldo | revisión integral del tutor |
| 8 | 17–fin dic | Correcciones y entrega | PDF final, anexos, código etiquetado y ensayo de defensa | entrega verificada |

### Plan de contingencia

- Si el corpus crece lento: reducir familias, no la calidad del test ni los hard
  negatives.
- Si el transformer no mejora: conservar reglas + modelo clásico como resultado
  válido y explicar el hallazgo.
- Si falla VoIP/móvil: demostrar el motor incremental con replay en tiempo real y
  medirlo en hardware real.
- Si no hay estudio con adultos mayores: hacer evaluación algorítmica completa y
  una inspección formativa pequeña de warnings; no bloquear la tesis.
- Si falta tiempo: cortar primero prosodia, UX ampliada, cuantización avanzada y
  escenarios adversariales. Nunca cortar trazabilidad, test congelado, privacidad
  ni análisis de errores.

## 8. Líneas de trabajo sin asignación fija

El backlog se divide por resultado, no por persona. Cada integrante se autoasigna
issues según capacidad y el equipo elige una persona revisora distinta.

| Línea | Resultados |
|---|---|
| Investigación, datos y ética | antecedentes, escenarios, protocolo, corpus, anotación y privacidad |
| ML/NLP y evaluación | preguntas, baselines, detector, calibración, métricas y errores |
| Audio/ASR y rendimiento | captura controlada, segmentación, ASR y benchmark móvil |
| Producto e integración | requisitos, UX, aplicación, arquitectura y pipeline end-to-end |

Se requiere revisión cruzada entre datos y evaluación, y entre audio e integración.
Los issues de interfaz o privacidad requieren personas de ambas líneas.

Todos deben:

- anotar el mismo piloto inicial;
- revisar al menos una sección ajena del informe por ciclo;
- poder ejecutar la demo y explicar las métricas centrales;
- registrar contribuciones en cada seguimiento como herramienta interna, aunque el
  profesor no exija evidencia individual ni horas;
- participar de ensayos de defensa y poder explicar el proyecto completo.

### Capacidad semanal sugerida

Cada persona compromete horas reales, no ideales. Para un ciclo de dos semanas:

- 60% trabajo de su línea primaria;
- 20% trabajo con la pareja revisora;
- 10% integración y reproducción;
- 10% escritura, registro y preparación de la clase.

## 9. Cadencia de trabajo y clases

### Internamente, todas las semanas

1. Lunes: elegir un máximo de un resultado principal por integrante.
2. Mitad de semana: integrar y detectar bloqueos.
3. Viernes: demo o evidencia nueva; actualizar decisiones, riesgos y horas.
4. La escritura se actualiza en el mismo cambio que el experimento o decisión.

### Para cada clase semanal o quincenal

Llevar siempre un paquete de cinco piezas:

1. **Decisiones solicitadas:** máximo tres preguntas concretas al profesor.
2. **Qué cambió:** una diapositiva o sección breve desde la clase anterior.
3. **Evidencia:** demo, gráfico, tabla, muestra del corpus o documento revisable.
4. **Plan contra resultado:** comprometido, terminado, pendiente y causa.
5. **Próximo gate:** responsables, fecha y criterio observable de aceptación.

No presentar “estuvimos investigando” sin matriz, fuentes seleccionadas,
conclusiones provisionales y decisiones que esa investigación habilita.

Usar [PLANTILLA-SEGUIMIENTO.md](PLANTILLA-SEGUIMIENTO.md) antes y después de cada
clase. La minuta debe registrar qué aprobó o corrigió el profesor; un comentario no
registrado se pierde y reaparece como discusión semanas después.

## 10. Sistema de archivos

Crear carpetas cuando aparezca el primer artefacto real; evitar una arquitectura de
directorios vacíos. Estructura objetivo:

```text
bitacora_tesis/
├── README.md
├── AGENTS.md
├── deep-research-report.md
├── docs/
│   ├── GUIA-DE-ARCHIVOS.md
│   ├── GLOSARIO.md
│   ├── gestion/
│   │   ├── PLAN-MAESTRO.md
│   │   ├── MAPA-DECISIONES.md
│   │   ├── METODO-DE-TRABAJO.md
│   │   ├── REGISTRO-RIESGOS.md
│   │   ├── seguimientos/YYYY-MM-DD.md
│   │   └── bitacora/YYYY-MM-semana-NN.md
│   ├── propuesta/
│   │   ├── PLAN-DE-TRABAJO.md
│   │   ├── ANTEPROYECTO.md
│   │   ├── CORRECCIONES-ANTEPROYECTO.md
│   │   ├── REQUISITOS-ACADEMICOS.md
│   │   └── original/            # .docx congelado
│   ├── investigacion/
│   │   ├── PROTOCOLO-REVISION.md
│   │   ├── PREGUNTAS-DE-INVESTIGACION.md
│   │   ├── SINTESIS-ESTADO-DEL-ARTE.md
│   │   ├── matriz-literatura.csv
│   │   ├── lecturas/YYYY-autor-tema.md
│   │   └── bibliografia.bib
│   ├── datos-etica/
│   │   ├── METODO-CREACION-CORPUS.md
│   │   ├── MANUAL-ANOTACION.md
│   │   ├── CHECKLIST-ETICA.md
│   │   ├── CONSENTIMIENTO-BORRADOR.md
│   │   ├── PLAN-DATOS.md
│   │   └── ESQUEMA-DATASET.md
│   ├── ingenieria/
│   │   ├── ALTERNATIVAS-CAPTURA-AUDIO.md
│   │   ├── ARQUITECTURA.md
│   │   ├── REQUISITOS-SOFTWARE.md
│   │   ├── adr/NNNN-decision.md
│   │   └── PLAN-PRUEBAS.md
│   ├── evaluacion/
│   │   ├── METRICAS.md
│   │   ├── PROTOCOLO-EXPERIMENTAL.md
│   │   ├── AMENAZAS-VALIDEZ.md
│   │   └── RESULTADOS.md
│   └── tesis/
│       ├── ESQUELETO-INFORME.md
│       └── figuras/
├── data/
│   ├── README.md
│   ├── schemas/
│   └── manifests/
├── src/
│   ├── asr/
│   ├── detector/
│   ├── evaluation/
│   └── mobile/
├── experiments/
│   └── README.md
└── tests/
```

Los audios crudos, consentimientos firmados, credenciales, nombres reales y datos
identificables no se versionan en Git. `data/README.md` documentará dónde viven,
quién accede, cómo se respaldan y cuándo se eliminan. Git solo contendrá esquemas,
manifiestos pseudonimizados y datos explícitamente autorizados.

## 11. Criterios de éxito

### Académicos

- Plan de Trabajo aprobado y trazable a los entregables.
- Todas las etapas exigidas de ingeniería documentadas.
- Informe y defensa cumplen plantilla, procedimiento y participación grupal.

### Científicos

- Preguntas respondidas con un protocolo predefinido y datos separados.
- Comparación contra reglas y baseline clásico; no solo el mejor modelo.
- Métricas de falsas alarmas y detección temporal, no solo accuracy.
- Amenazas a la validez y resultados negativos informados honestamente.

### Técnicos

- Pipeline reproducible desde audio hasta decisión.
- Inferencia local en hardware definido y latencia medida.
- Demo end-to-end con una ruta de contingencia grabada.

### Éticos

- Ninguna grabación sin protocolo y consentimiento aprobados.
- Datos ficticios en los guiones; acceso mínimo y retención definida.
- Publicación de audio separada de la autorización para participar.

## 12. Trabajo hasta el miércoles 9 de septiembre

- [x] Consolidar instrucciones disponibles y equipo autorizado.
- [x] Preparar [Plan de Trabajo v1](../propuesta/PLAN-DE-TRABAJO.md).
- [x] Separar PI1–PI2 de las evaluaciones E1–E2.
- [x] Comparar altavoz, replay, VoIP y acceso privilegiado.
- [ ] Proponer 8–10 escenarios argentinos con fuentes y redactar el
  problema/beneficiario en cinco líneas.
- [ ] Revisar objetivos, alcance, preguntas y preparar el relato de cinco minutos.
- [ ] Probar un WAV con un ASR local y registrar latencia, texto y dificultad.
- [ ] Dibujar arquitectura v0 y dos variantes simples de warning.
- [ ] Acordar qué partes son núcleo, extensión y fuera de alcance.
- [ ] Presentar al profesor cinco decisiones, no una lista abierta de tecnologías.

Estas tareas se migran a GitHub Issues desde
[BACKLOG-INICIAL.md](BACKLOG-INICIAL.md). La persona responsable se define por
autoasignación.

## 13. Decisión sobre Wayfinder

Wayfinder encaja **parcialmente**: el proyecto es grande y todavía tiene decisiones
que desbloquean otras. No conviene aplicar literalmente su flujo de issues durante
esta fase porque el artefacto oficial es el Plan de Trabajo y todavía no está
configurado un tracker con relaciones, etiquetas y responsables.

Se adopta su idea valiosa —destino, decisiones cerradas, frontera, bloqueos, niebla
y fuera de alcance— en [MAPA-DECISIONES.md](MAPA-DECISIONES.md). Después de que el
tutor apruebe el Plan, la ejecución sí puede migrarse a GitHub Issues/Projects:
issues de decisión para incertidumbre y tareas/experimentos para producir evidencia.
El mapa nunca reemplaza el cronograma, el informe, el registro de riesgos ni el
protocolo experimental.

## 14. Límites de esta versión

- No se encontró un reglamento público específico del Plan 2008; las indicaciones
  del profesor son la autoridad operativa actual.
- Faltan plantilla, rúbrica, fecha exacta, formato bibliográfico y procedimiento de
  aprobación del uso de participantes.
- La capacidad semanal todavía no fue registrada; el equipo limitará los issues del
  ciclo después de declarar disponibilidad real.
- El cronograma asume entrega a fines de diciembre. Si la fecha se adelanta, se
  recortan extensiones y no se comprime la evaluación final.
- La revisión hecha para este plan es de alcance y orientada a decisiones; no se
  presenta como revisión sistemática exhaustiva.
