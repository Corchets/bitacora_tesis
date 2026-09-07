# Guía de archivos

Esta guía responde qué contiene cada archivo, cuándo leerlo y qué evento obliga a
actualizarlo. Los archivos futuros aparecen solo cuando su primera evidencia existe.

## Raíz

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `README.md` | entrada humana y rutas rápidas | cambia la navegación o el flujo general |
| `AGENTS.md` | instrucciones breves para asistentes | cambia un invariante o un disparador de lectura |
| `.gitignore` | barrera contra datos restringidos, secretos y artefactos grandes | aparece una nueva ruta privada o regenerable |
| `deep-research-report.md` | investigación técnica inicial extensa | se conserva como antecedente; sus marcadores internos de cita se reemplazan en documentos entregables |
| `CLAUDE.md`, `GEMINI.md` | punteros a `AGENTS.md` para asistentes que buscan otro nombre | no se editan; el contenido vive en `AGENTS.md` |

## `docs/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `GUIA-DE-ARCHIVOS.md` | este documento: qué contiene cada archivo y cuándo tocarlo | se agrega, mueve o retira un archivo del repositorio |
| `GLOSARIO.md` | términos usados con sentido preciso, incluidas `T_A`, `T_R`, `T_C` | dos personas usan un término con sentidos distintos, o aparece uno nuevo |

## `docs/gestion/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `PLAN-MAESTRO.md` | hitos, gates, fechas, alcance de gestión y contingencias | cambia un hito, fecha o estrategia global |
| `METODO-DE-TRABAJO.md` | proceso de issues, sesiones, reuniones, investigación, experimentos y escritura | cambia la manera de trabajar |
| `MAPA-DECISIONES.md` | índice temporal de decisiones iniciales y niebla de alcance | hasta migrar cada decisión abierta a GitHub; luego solo enlaza decisiones duraderas |
| `REGISTRO-RIESGOS.md` | riesgos, señales, mitigaciones y contingencias | aparece evidencia que cambia probabilidad/impacto o un riesgo se materializa |
| `PLANTILLA-SEGUIMIENTO.md` | molde para reuniones con el profesor | cambia el formato de seguimiento |
| `BACKLOG-INICIAL.md` | semilla para crear los primeros issues | no se actualiza después de importar a GitHub |
| `seguimientos/AAAA-MM-DD.md` | preparación y minuta de una reunión con el profesor | 48 h antes y dentro de 24 h después de la reunión |
| `bitacora/AAAA-MM-semana-NN.md` | registro interno de la semana: qué se hizo, qué apareció, qué bloquea | durante la semana, por quien coordina |
| `bitacora/PLANTILLA-SEMANAL.md` | molde de la entrada semanal | cambia el formato de la bitácora |

## `docs/propuesta/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `REQUISITOS-ACADEMICOS.md` | requisitos confirmados y preguntas formales pendientes | el profesor aclara formato, entregables o fechas |
| `PLAN-DE-TRABAJO.md` | propuesta académica: problema, objetivos, alcance, método, entregables y cronograma | el tutor aprueba/corrige alcance o metodología |
| `ANTEPROYECTO.md` | anteproyecto presentado, en Markdown para poder diffear cambios | se aplica una corrección o el tutor pide un cambio |
| `CORRECCIONES-ANTEPROYECTO.md` | afirmaciones `C1`–`C5` que no se sostienen y supuestos `S1`–`S3` no decididos | se aplica una corrección al anteproyecto o aparece una nueva |
| `original/anteproyecto-tesis-vishing.docx` | `.docx` original, resguardo histórico | nunca; es un congelado |

## `docs/investigacion/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `PREGUNTAS-DE-INVESTIGACION.md` | preguntas centrales y cómo se responden | cambia una pregunta, variable o métrica antes del congelamiento |
| `PROTOCOLO-REVISION.md` | bases, búsquedas, inclusión, exclusión y calidad | se modifica el método de revisión, antes de ejecutar la nueva búsqueda |
| `matriz-literatura.csv` | una fila por fuente leída y evidencia extraída | se termina de evaluar una fuente |
| `report-source.md` | registro interno de fuentes usadas para fundamentar el plan | aparece evidencia que cambia el plan; no es el informe entregable |
| `SINTESIS-ESTADO-DEL-ARTE.md` | comparación razonada de sistemas existentes y qué espacio queda | se verifica una fila contra su fuente primaria o entra un trabajo nuevo |
| `lecturas/AAAA-autor-tema.md` | ficha de un paper leído, con lo que los propios autores declaran como límite | al terminar de leer un trabajo; después se carga su fila en la matriz |

Archivos que se crearán cuando exista material:

- `bibliografia.bib`: referencias citadas por el manuscrito.
- `consultas/AAAA-MM-DD.md`: registro literal de cada ola de búsqueda si la tabla
  del protocolo resulta insuficiente.

## `docs/datos-etica/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `METODO-CREACION-CORPUS.md` | quién define escenarios, cómo se escriben roles, piloto, escala y parada | cambia el diseño del corpus antes de generar nuevos datos |
| `PLAN-PARTICIPANTES-Y-CORPUS.md` | población voluntaria, consentimiento, tamaño por etapas y acceso | el tutor aprueba/corrige participantes o tratamiento |
| `CONSENTIMIENTO-BORRADOR.md` | texto a validar antes de invitar voluntarios | cambia finalidad, acceso, publicación, retención o retiro |
| `CATALOGO-ESCENARIOS.csv` | inventario de familias y semillas de llamadas | se acepta, modifica o descarta un escenario |
| `MANUAL-ANOTACION.md` | taxonomía propuesta, formato por turno y protocolo de anotación | se cierra D07, o el piloto revela ambigüedades en una etiqueta |
| `CHECKLIST-ETICA.md` | comité de ética, plazos, Ley 25.326 y reglas que ya rigen | se resuelve un ítem del checklist o cambia el circuito ético |

Archivos que se crearán al cerrar el piloto:

- `ESQUEMA-DATASET.md`: campos, tipos, validaciones y relaciones.
- `PLAN-DATOS.md`: ubicación real, backup, acceso, publicación y eliminación.

## `docs/ingenieria/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `ALTERNATIVAS-CAPTURA-AUDIO.md` | comparación replay, altavoz, VoIP y acceso privilegiado | una prueba o decisión cambia la recomendación |
| `ARQUITECTURA.md` | borrador v0: componentes, flujo y la interfaz que aísla la fuente de audio | se cierran D05/D11, o una prueba cambia el flujo |
| `adr/PLANTILLA-ADR.md` | molde de ADR, con la tabla de alternativas descartadas | cambia el formato de ADR |

Archivos que se crean con la primera evidencia correspondiente:

- `REQUISITOS-SOFTWARE.md`: requisitos funcionales/no funcionales y aceptación.
- `PLAN-PRUEBAS.md`: estrategia y trazabilidad requisito→prueba.
- `adr/NNNN-titulo.md`: una decisión arquitectónica durable por archivo.

## `docs/evaluacion/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `METRICAS.md` | definición única de cada métrica y sus unidades, incluidas `L_R`, `L_C` y `Preventive@δ` | se cierra D07/D08 o se agrega una métrica al reporte |

Se crean después de aprobar preguntas y piloto:

- `PROTOCOLO-EXPERIMENTAL.md`: datos, splits, baselines, modelos, hardware y plan
  estadístico; se congela antes de consultar el test final.
- `RESULTADOS.md`: resultados reproducibles y enlaces a salidas.
- `ANALISIS-ERRORES.md`: taxonomía y ejemplos pseudonimizados de fallos.
- `AMENAZAS-VALIDEZ.md`: límites internos, externos, de constructo y conclusión.

## `docs/tesis/`

| Archivo | Para qué sirve | Se actualiza cuando |
|---|---|---|
| `ESQUELETO-INFORME.md` | índice y presupuesto provisional de páginas | el profesor cambia la estructura o una sección madura |

Cuando empiece la redacción, cada capítulo puede vivir en un archivo propio. La
herramienta final de compilación definirá si se usa Markdown, LaTeX o DOCX; esa
decisión se registra antes de dividir el manuscrito.

## Código, datos y experimentos futuros

| Ruta | Contenido | Regla |
|---|---|---|
| `src/asr/` | adaptadores y procesamiento de audio | cada cambio incluye prueba o benchmark |
| `src/detector/` | reglas, modelos y estado temporal | mantener baselines comparables |
| `src/mobile/` | aplicación e integración | separar UI del motor evaluable |
| `tests/` | pruebas unitarias, integración y end-to-end | enlazar con requisitos |
| `experiments/` | configuraciones y scripts reproducibles | una carpeta/config por experimento |
| `data/schemas/` | esquemas versionables | sin audio ni identidad |
| `data/manifests/` | IDs y splits autorizados | pseudonimizados y versionados |
| almacenamiento externo | audio, consentimientos, identidades y datos restringidos | acceso mínimo, backup y eliminación definidos |

## Dónde registrar algo nuevo

- Es trabajo por hacer: GitHub Issue.
- Es una decisión temporal: comentario de resolución del issue.
- Es una decisión arquitectónica duradera: ADR.
- Es una fuente leída: matriz de literatura.
- Es una observación del profesor: minuta de seguimiento.
- Es un riesgo futuro: registro de riesgos.
- Es un fallo actual: issue con pasos de reproducción.
- Es un resultado numérico: salida de experimento y síntesis en `RESULTADOS.md`.
- Es texto para la entrega: capítulo correspondiente en `docs/tesis/`.
