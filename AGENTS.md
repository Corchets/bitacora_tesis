# Instrucciones del repositorio

## Objetivo

Ayudar a producir un Proyecto Final defendible y reproducible sobre detección incremental de
vishing. Priorizar evidencia y decisiones trazables sobre volumen de documentación o complejidad
técnica. Español de Argentina; los nombres de etiquetas técnicas quedan en inglés
(`REQUEST_AUTH_CODE`).

Documentación y código conviven en este repositorio. La estructura objetivo está en
[PLAN-MAESTRO.md §10](docs/gestion/PLAN-MAESTRO.md#10-sistema-de-archivos): las carpetas se crean
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
- **Nunca** agregues consentimientos firmados, nombres de participantes, ni transcripciones con
  datos identificatorios.
- Ver [CHECKLIST-ETICA.md](docs/datos-etica/CHECKLIST-ETICA.md).

---

## Flujo obligatorio

1. Leer el issue activo y autoasignarlo antes de modificar el repositorio. Durante el bootstrap sin
   issues, usar [BACKLOG-INICIAL.md](docs/gestion/BACKLOG-INICIAL.md).
2. Leer [el método](docs/gestion/METODO-DE-TRABAJO.md) cuando se planifique, cree, ejecute o cierre
   trabajo.
3. Cargar solo la referencia disparada por la tarea:
   - **Investigación:** [PROTOCOLO-REVISION.md](docs/investigacion/PROTOCOLO-REVISION.md) y
     actualizar [matriz-literatura.csv](docs/investigacion/matriz-literatura.csv).
   - **Corpus o participantes:** [METODO-CREACION-CORPUS.md](docs/datos-etica/METODO-CREACION-CORPUS.md)
     y [PLAN-PARTICIPANTES-Y-CORPUS.md](docs/datos-etica/PLAN-PARTICIPANTES-Y-CORPUS.md).
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

## Dónde va cada cosa

| Si el contenido es… | Va a |
|---|---|
| Una decisión **pendiente** | [MAPA-DECISIONES.md](docs/gestion/MAPA-DECISIONES.md), o un issue `type:decision` |
| Una decisión **arquitectónica duradera ya tomada** | `docs/ingenieria/adr/NNNN-titulo.md`, copiando [PLANTILLA-ADR.md](docs/ingenieria/adr/PLANTILLA-ADR.md) |
| Qué pasó esta semana | `docs/gestion/bitacora/AAAA-MM-semana-NN.md` |
| Qué se habló con el profesor | `docs/gestion/seguimientos/AAAA-MM-DD.md` |
| Un paper leído | `docs/investigacion/lecturas/AAAA-autor-tema.md` + fila en `matriz-literatura.csv` |
| Comparación con otros sistemas | [SINTESIS-ESTADO-DEL-ARTE.md](docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md) |
| Definición de etiquetas o reglas de anotación | [MANUAL-ANOTACION.md](docs/datos-etica/MANUAL-ANOTACION.md) |
| Definición de una métrica | [METRICAS.md](docs/evaluacion/METRICAS.md) |
| Texto de la tesis | `docs/tesis/`. **No crear capítulos vacíos.** |
| Un término que se usa con sentido preciso | [GLOSARIO.md](docs/GLOSARIO.md) |
| Un diagrama | `.md` con bloque ` ```mermaid `. **No usar `.mmd`**: GitHub no lo renderiza |
| Consentimiento, comité de ética o Ley 25.326 | `docs/datos-etica/` |

La [Guía de archivos](docs/GUIA-DE-ARCHIVOS.md) tiene el detalle de cuándo se actualiza cada uno.
**No crear carpetas nuevas sin que el usuario lo pida.** Si algo no encaja en ninguna, preguntá.

## Convenciones

- **Archivos:** los documentos de proceso en `MAYUSCULAS-CON-GUION.md`; bitácoras
  `AAAA-MM-semana-NN.md`; seguimientos `AAAA-MM-DD.md`; ADRs `NNNN-titulo.md` con cuatro dígitos.
- **Fechas:** siempre absolutas (`2026-09-02`), nunca "la semana pasada".
- **Enlaces:** relativos entre documentos, formato Markdown. Verificá que resuelvan.
- **Marcas de estado en el anteproyecto:** `⚠️[C1]`…`⚠️[C5]` = afirmaciones incorrectas;
  `⚠️[S1]`…`⚠️[S3]` = supuestos no decididos. No las borres sin aplicar la corrección
  correspondiente en [CORRECCIONES-ANTEPROYECTO.md](docs/propuesta/CORRECCIONES-ANTEPROYECTO.md).

## Al terminar un cambio

1. Actualizá la fuente de verdad afectada, no varias copias.
2. Si el cambio es sustantivo, anotalo en la bitácora de la semana en curso.
3. Verificá que no quedaron enlaces rotos.
4. **No hagas `git commit` salvo que te lo pidan.**

Una sesión termina con el issue actualizado, la evidencia enlazada, las fuentes de verdad
consistentes y las verificaciones pertinentes ejecutadas. Si resta trabajo, el issue permanece
abierto con una próxima acción concreta y un bloqueo explícito.
