# Instrucciones del repositorio

## Objetivo

Ayudar a producir un Proyecto Final defendible y reproducible sobre detección incremental de
vishing. Priorizar evidencia y decisiones trazables sobre volumen de documentación o complejidad
técnica. Español de Argentina; los nombres de etiquetas técnicas quedan en inglés
(`REQUEST_AUTH_CODE`).

Documentación y código conviven en este repositorio. La estructura objetivo está en
[README.md](README.md#3-mapa-del-repositorio-estructura-documental): las carpetas se crean
cuando aparece el primer artefacto real, nunca antes.

---

## Regla n.º 1 — No inventes decisiones

El error más caro que se puede cometer acá. El equipo todavía no cerró el alcance, el producto, la
taxonomía ni el corpus. Antes de escribir, leer
[MAPA-DECISIONES.md](docs/gestion/MAPA-DECISIONES.md): define qué está resuelto y qué no.

- **Nunca** escribas un ADR para una decisión que el equipo no tomó. Un ADR "propuesto" parece
  cerrado y nadie lo vuelve a mirar.
- **Nunca** conviertas una recomendación del deep research en una afirmación del proyecto. El
  informe *sugiere*; el equipo *decide*.
- Si hace falta elegir para poder avanzar, escribí la opción **y** marcala:
  `> **Estado: propuesta sin discutir.**` con enlace a la decisión abierta correspondiente.
- Si una decisión abierta te bloquea, decilo y parás. No la resuelvas por tu cuenta.

## Regla n.º 2 — No inventes citas

Las citas del [deep research](deep-research-report.md) son marcadores internos
(`citeturn19view5`), **no** referencias bibliográficas. Una referencia inventada en una tesis es
un problema grave en la defensa.

- No crees ni completes `bibliografia.bib` con entradas que no viste en la fuente.
- Una entrada entra al `.bib` solo cuando alguien abrió el paper y copió DOI, autores y año.
- Cifras, fechas y disponibilidad de productos (Google Scam Detection, Samsung): siempre con fuente
  y **fecha de consulta**, porque cambian.
- Sobre la ausencia de corpus en español argentino, la formulación correcta es *"no identificamos en
  la literatura revisada"*, nunca *"no existe"*.

## Regla n.º 3 — Datos personales y audio

- **Nunca** agregues audio al repositorio (`.wav`, `.mp3`, `.m4a`, `.flac`, `.ogg`). Está en
  [.gitignore](.gitignore); no lo modifiques para permitirlos.
- **Nunca** agregues datos identificatorios reales ni números privados.
- Ver [PRIVACIDAD-DEL-SISTEMA.md](docs/datos-etica/PRIVACIDAD-DEL-SISTEMA.md).

---

## Flujo obligatorio

1. Leer el issue activo en GitHub Issues y autoasignarlo antes de modificar el repositorio.
2. Leer [el método](docs/gestion/METODO-DE-TRABAJO.md) cuando se planifique, cree, ejecute o cierre
   trabajo.
3. Cargar solo la referencia disparada por la tarea:
   - **Investigación:** [PROTOCOLO-REVISION.md](docs/investigacion/PROTOCOLO-REVISION.md) y
     [SINTESIS-ESTADO-DEL-ARTE.md](docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md).
   - **Corpus o escenarios:** [METODO-CREACION-CORPUS.md](docs/datos-etica/METODO-CREACION-CORPUS.md)
     y [CATALOGO-ESCENARIOS.csv](docs/datos-etica/CATALOGO-ESCENARIOS.csv).
   - **Anotación:** [MANUAL-ANOTACION.md](docs/datos-etica/MANUAL-ANOTACION.md).
   - **Experimento o métricas:** [PREGUNTAS-DE-INVESTIGACION.md](docs/investigacion/PREGUNTAS-DE-INVESTIGACION.md)
     y [METRICAS.md](docs/evaluacion/METRICAS.md).
   - **Audio, Android o VoIP:** [ALTERNATIVAS-CAPTURA-AUDIO.md](docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md),
     [ARQUITECTURA.md](docs/ingenieria/ARQUITECTURA.md) y los ADR relacionados.
   - **Informe o entrega:** [REQUISITOS-ACADEMICOS.md](docs/propuesta/REQUISITOS-ACADEMICOS.md) y
     [ESQUELETO-INFORME.md](docs/tesis/ESQUELETO-INFORME.md).
4. Producir la evidencia exigida por la definición de terminado.
5. Actualizar una sola fuente de verdad y enlazarla desde el issue.
6. Registrar pruebas, limitaciones y decisiones antes de cerrar el issue.

## Invariantes

- GitHub Issues es el único backlog activo; el roadmap contiene hitos, no tareas.
- Cada afirmación externa material tiene fuente verificable.
- Cada experimento registra dataset/split, configuración, seed, versión de código, métricas y salida.
- Audio, consentimientos firmados, datos identificables y secretos permanecen fuera de Git.
- Las decisiones de alcance, participantes y publicación requieren validación del profesor/tutor.

---

### Dónde va cada cosa (Router del Repositorio)

Cada información tiene **una sola fuente de verdad**. Usar esta tabla para saber qué consultar y cuándo actualizar:

| Tarea o Contenido | Fuente de Verdad (Dónde vive) | Cuándo se lee / Cuándo se actualiza |
|---|---|---|
| **Plan general, alcance, cronograma** | [`docs/propuesta/PLAN-DE-TRABAJO.md`](docs/propuesta/PLAN-DE-TRABAJO.md) | **Lee:** para consultar metas, fases o exclusiones.<br/>**Actualiza:** solo si el tutor aprueba un cambio de alcance o metodología. |
| **Requisitos UNSTA, formato y defensa** | [`docs/propuesta/REQUISITOS-ACADEMICOS.md`](docs/propuesta/REQUISITOS-ACADEMICOS.md) | **Lee:** para pautas formales de entrega (A4, ~100 págs, tribunal).<br/>**Actualiza:** ante novedades administrativas de la facultad. |
| **Avance semanal del equipo** | `docs/gestion/bitacora/AAAA-MM-semana-NN.md` | **Actualiza:** al cerrar un issue o finalizar la semana, registrando qué se hizo y qué artefacto nuevo existe (ver [README](docs/gestion/bitacora/README.md)). |
| **Reunión con el tutor (Ing. Rico)** | `docs/gestion/seguimientos/AAAA-MM-DD.md` | **Crea:** 24–48 h antes con dudas/consultas a llevar.<br/>**Actualiza:** dentro de las 24 h posteriores con la minuta de acuerdos (ver [README](docs/gestion/seguimientos/README.md)). |
| **Decisiones abiertas o pendientes** | [`docs/gestion/MAPA-DECISIONES.md`](docs/gestion/MAPA-DECISIONES.md) | **Lee:** antes de asumir opciones de diseño.<br/>**Actualiza:** cuando un issue resuelve o desbloquea una disyuntiva del proyecto. |
| **Decisión arquitectónica duradera (ADR)** | `docs/ingenieria/adr/NNNN-titulo.md` | **Crea:** solo cuando se congela una decisión técnica estructural permanente (ej. contratos de interfaz, pipeline de audio). |
| **Riesgos del proyecto** | [`docs/gestion/REGISTRO-RIESGOS.md`](docs/gestion/REGISTRO-RIESGOS.md) | **Actualiza:** al descubrir un nuevo riesgo técnico/plataforma o validar una mitigación. |
| **Privacidad del sistema y normativa** | [`docs/datos-etica/PRIVACIDAD-DEL-SISTEMA.md`](docs/datos-etica/PRIVACIDAD-DEL-SISTEMA.md) | **Lee:** para fundamentar inferencia *on-device*, descarte de audio y Ley 25.326. |
| **Diseño del corpus y llamadas** | [`docs/datos-etica/METODO-CREACION-CORPUS.md`](docs/datos-etica/METODO-CREACION-CORPUS.md) | **Lee:** para crear semillas, fichas de rol y negativos difíciles.<br/>**Actualiza:** si cambia la metodología de recolección o parada. |
| **Catálogo de escenarios y fraudes** | [`docs/datos-etica/CATALOGO-ESCENARIOS.csv`](docs/datos-etica/CATALOGO-ESCENARIOS.csv) | **Actualiza:** al incorporar, modificar o descartar una semilla de llamada. |
| **Taxonomía y reglas de anotación** | [`docs/datos-etica/MANUAL-ANOTACION.md`](docs/datos-etica/MANUAL-ANOTACION.md) | **Actualiza:** si el piloto o el equipo redefinen una etiqueta de turno (`URGENCY`, `REQUEST_OTP`, etc.). |
| **Definición de métricas y marcas** | [`docs/evaluacion/METRICAS.md`](docs/evaluacion/METRICAS.md) | **Fuente única:** para fórmulas de `T_A`, `T_R`, `T_C`, márgenes `L_R`, `L_C` y falsas alarmas. |
| **Captura de audio y hardware** | [`docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md`](docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md) y [`ARQUITECTURA.md`](docs/ingenieria/ARQUITECTURA.md) | **Lee:** para diseñar interfaces de audio, ASR y prototipo. |
| **Investigación y papers leídos** | [`docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md`](docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md) | **Actualiza:** al analizar una fuente primaria siguiendo el [protocolo](docs/investigacion/PROTOCOLO-REVISION.md). |
| **Texto final del informe de tesis** | `docs/tesis/` | **Actualiza:** redactando sobre capítulos reales según el [esqueleto](docs/tesis/ESQUELETO-INFORME.md). No crear capítulos vacíos. |
| **Término con significado preciso** | [`docs/GLOSARIO.md`](docs/GLOSARIO.md) | **Actualiza:** cuando surge un término técnico nuevo o ambiguo. |

**No crear carpetas nuevas sin que el usuario lo pida.** Si algo no encaja en ninguna, consultá. El [README.md](README.md) mantiene el mapa de la estructura global.

## Convenciones

- **Archivos:** los documentos de proceso en `MAYUSCULAS-CON-GUION.md`; bitácoras
  `AAAA-MM-semana-NN.md`; seguimientos `AAAA-MM-DD.md`; ADRs `NNNN-titulo.md` con cuatro dígitos.
- **Fechas:** siempre absolutas (`2026-09-02`), nunca "la semana pasada".
- **Enlaces:** relativos entre documentos, formato Markdown. Verificá que resuelvan.

## Uso y sugerencia de Skills especializadas

El repositorio cuenta con skills en `.agents/skills/`. El agente debe sugerir proactivamente al usuario ejecutarlas según la fase de trabajo:

- **Decisiones abiertas, tickets ambiguos o diseño de alcance:** Sugerir `grill-me` o `grill-with-docs` para una entrevista estructurada que resuelva incertidumbres antes de escribir código o comprometer documentos.
- **Implementación de código:** Sugerir `implement` (y `tdd` para módulos de cálculo de métricas, reglas o parsers) para construir código trazable y probado.
- **Finalización de código o Pull Requests:** Sugerir `code-review` antes de mergear o cerrar el issue.
- **Errores, excepciones o latencias inesperadas:** Sugerir `diagnosing-bugs` para aislar y resolver la causa raíz con pruebas.
- **Pruebas de concepto rápidas o spikes descartables:** Sugerir `prototype`.
- **Descomponer discusiones en issues para GitHub:** Sugerir `to-tickets` o `to-spec`.
- **Resolución e integración de issues:** Usar `resolver-issue`.

## Ciclo de trabajo con issues: Ejecución y Barrido Documental

Para mantener el repositorio sincronizado sin caer en micro-gestión constante, todo agente o integrante debe operar en dos fases bien diferenciadas:

### Fase 1 — Durante la ejecución (Trabajo enfocado)
- Trabajar **exclusivamente** sobre el problema del issue (escribir código, realizar un spike, analizar un paper o redactar un texto).
- Editar **únicamente** la fuente de verdad primaria afectada (ej. archivo en `src/`, `experiments/`, `docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md` o un documento específico de `docs/`).
- **No tocar** bitácoras, riesgos ni archivos de gestión mientras se está programando o investigando.

### Fase 2 — Al cerrar el issue (Barrido Documental obligatorio)
Una sesión termina ejecutando este barrido en orden para sincronizar el estado vivo del proyecto:
1. **Verificar la fuente de verdad:** Asegurar que el cambio está completo, testeado y sin enlaces rotos relativos.
2. **Bitácora semanal (`docs/gestion/bitacora/AAAA-MM-semana-NN.md`):** Agregar a la tabla de la semana en curso la fila del issue con su estado (☑), y una viñeta concreta en *"Qué existe hoy que no existía la semana pasada"* describiendo el artefacto generado.
3. **Decisiones (`docs/gestion/MAPA-DECISIONES.md`):** Si el issue resolvió o redefinió una decisión abierta, actualizar su estado. Si se congeló una decisión arquitectónica duradera, redactar el ADR correspondiente en `docs/ingenieria/adr/`.
4. **Riesgos (`docs/gestion/REGISTRO-RIESGOS.md`):** Si el trabajo mitigó un riesgo o descubrió uno nuevo, actualizar la matriz.
5. **Comentario de cierre para GitHub:** Redactar y entregar el comentario listo para pegar en GitHub Issues (`Closes #N`, resumen, evidencia observable, decisiones y próxima acción).

### Reglas de higiene final
- Actualizá la fuente de verdad afectada, **nunca mantengas copias paralelas**.
- **No hagas `git commit`** salvo que el usuario lo pida explícitamente.

