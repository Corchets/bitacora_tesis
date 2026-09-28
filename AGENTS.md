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

## Regla - No inventes decisiones

Antes de escribir, leer
[MAPA-DECISIONES.md](docs/gestion/MAPA-DECISIONES.md): define qué está resuelto y qué no.

- Si hace falta elegir para poder avanzar, escribí la opción **y** marcala:
  `> **Estado: propuesta sin discutir.**` con enlace a la decisión abierta correspondiente.
- Si una decisión abierta te bloquea, decilo y parás. No la resuelvas por tu cuenta.

---

## Flujo de trabajo con issues

Todo trabajo parte de un issue en GitHub Issues y se ejecuta en tres momentos:

### 1. Orientación y arranque

- **Si no hay tarea clara o el usuario no sabe por dónde arrancar:** inspeccionar los issues abiertos del milestone activo en GitHub Issues, verificar bloqueos en [MAPA-DECISIONES.md](docs/gestion/MAPA-DECISIONES.md) y proponer la próxima tarea concreta de mayor impacto técnico.
- **Si ya hay un issue asignado:** leer su objetivo y definición de terminado en [METODO-DE-TRABAJO.md](docs/gestion/METODO-DE-TRABAJO.md), autoasignarlo y cargar **únicamente** la referencia técnica que dispara la tarea (ver tabla _Dónde va cada cosa_).

### 2. Ejecución (Trabajo enfocado)

- Trabajar **exclusivamente** sobre el problema técnico del issue (código en `src/`, experimentos en `experiments/` o textos en `docs/`).
- Editar **únicamente** la fuente de verdad primaria afectada.
- No tocar bitácoras ni archivos de gestión mientras se está programando o investigando.

### 3. Cierre (Barrido Documental e integración)

Al completar el objetivo, sincronizar el repositorio en este orden antes de cerrar:

1. **Fuente de verdad:** verificar cambios, pruebas y enlaces relativos.
2. **Bitácora semanal (`docs/gestion/bitacora/AAAA-MM-semana-NN.md`):** registrar la fila en la tabla semanal con estado (`☑`) y agregar viñeta en _"Qué existe hoy que no existía la semana pasada"_ con el artefacto real generado.
3. **Decisiones (`docs/gestion/MAPA-DECISIONES.md`):** actualizar estado si se resolvió una decisión abierta. Si congeló una decisión arquitectónica duradera, crear el ADR correspondiente en `docs/ingenieria/adr/`.
4. **Riesgos (`docs/gestion/REGISTRO-RIESGOS.md`):** registrar mitigaciones o nuevos riesgos descubiertos.
5. **Comentario para GitHub:** entregar el bloque Markdown listo para copiar y cerrar el issue (`Closes #N`, resumen, evidencia observable, decisiones y próxima acción).

### Reglas de higiene

- Actualizá la fuente de verdad afectada; nunca mantengas copias paralelas.
- **No hagas `git commit`** salvo que el usuario lo pida explícitamente.

## Invariantes

- GitHub Issues es el único backlog activo; el roadmap contiene hitos, no tareas.
- Cada afirmación externa material tiene fuente verificable.
- Cada experimento registra dataset/split, configuración, seed, versión de código, métricas y salida.
- Audio, consentimientos firmados, datos identificables y secretos permanecen fuera de Git.

---

### Dónde va cada cosa (Router del Repositorio)

Cada información tiene **una sola fuente de verdad**. Usar esta tabla para saber qué consultar y cuándo actualizar:

| Tarea o Contenido                                | Fuente de Verdad (Dónde vive)                                                                                                                           | Cuándo se lee / Cuándo se actualiza                                                                                                                                                    |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Plan general, alcance, cronograma**            | [`docs/propuesta/PLAN-DE-TRABAJO.md`](docs/propuesta/PLAN-DE-TRABAJO.md)                                                                                | **Lee:** para consultar metas, fases o exclusiones.<br/>**Actualiza:** solo si se aprueba un cambio de alcance o metodología.                                                          |
| **Requisitos UNSTA, formato y defensa**          | [`docs/propuesta/REQUISITOS-ACADEMICOS.md`](docs/propuesta/REQUISITOS-ACADEMICOS.md)                                                                    | **Lee:** para pautas formales de entrega (A4, ~100 págs, tribunal).<br/>**Actualiza:** ante novedades administrativas de la facultad.                                                  |
| **Método de trabajo y flujo de issues**          | [`docs/gestion/METODO-DE-TRABAJO.md`](docs/gestion/METODO-DE-TRABAJO.md)                                                                                | **Lee:** al planificar, crear, ejecutar o cerrar trabajo.                                                                                                                              |
| **Avance semanal del equipo**                    | `docs/gestion/bitacora/AAAA-MM-semana-NN.md`                                                                                                            | **Actualiza:** al cerrar un issue o finalizar la semana, registrando qué se hizo y qué artefacto nuevo existe (ver [README](docs/gestion/bitacora/README.md)).                         |
| **Reunión con el tutor (Ing. Rico)**             | `docs/gestion/seguimientos/AAAA-MM-DD.md`                                                                                                               | **Crea:** 24–48 h antes con dudas/consultas a llevar.<br/>**Actualiza:** dentro de las 24 h posteriores con la minuta de acuerdos (ver [README](docs/gestion/seguimientos/README.md)). |
| **Decisiones abiertas o pendientes**             | [`docs/gestion/MAPA-DECISIONES.md`](docs/gestion/MAPA-DECISIONES.md)                                                                                    | **Lee:** antes de asumir opciones de diseño.<br/>**Actualiza:** cuando un issue resuelve o desbloquea una disyuntiva del proyecto.                                                     |
| **Decisión arquitectónica duradera (ADR)**       | `docs/ingenieria/adr/NNNN-titulo.md`                                                                                                                    | **Crea:** solo cuando se congela una decisión técnica estructural permanente (ej. contratos de interfaz, pipeline de audio).                                                           |
| **Riesgos del proyecto**                         | [`docs/gestion/REGISTRO-RIESGOS.md`](docs/gestion/REGISTRO-RIESGOS.md)                                                                                  | **Actualiza:** al descubrir un nuevo riesgo técnico/plataforma o validar una mitigación.                                                                                               |
| **Privacidad del sistema y normativa**           | [`docs/datos-etica/PRIVACIDAD-DEL-SISTEMA.md`](docs/datos-etica/PRIVACIDAD-DEL-SISTEMA.md)                                                              | **Lee:** para fundamentar inferencia _on-device_, descarte de audio y Ley 25.326.                                                                                                      |
| **Diseño del corpus y llamadas**                 | [`docs/datos-etica/METODO-CREACION-CORPUS.md`](docs/datos-etica/METODO-CREACION-CORPUS.md)                                                              | **Lee:** para crear semillas, fichas de rol y negativos difíciles.<br/>**Actualiza:** si cambia la metodología de recolección o parada.                                                |
| **Catálogo de escenarios y fraudes**             | [`docs/datos-etica/CATALOGO-ESCENARIOS.csv`](docs/datos-etica/CATALOGO-ESCENARIOS.csv)                                                                  | **Actualiza:** al incorporar, modificar o descartar una semilla de llamada.                                                                                                            |
| **Taxonomía y reglas de anotación**              | [`docs/datos-etica/MANUAL-ANOTACION.md`](docs/datos-etica/MANUAL-ANOTACION.md)                                                                          | **Actualiza:** si el piloto o el equipo redefinen una etiqueta de turno (`URGENCY`, `REQUEST_OTP`, etc.).                                                                              |
| **Definición de métricas y marcas**              | [`docs/evaluacion/METRICAS.md`](docs/evaluacion/METRICAS.md)                                                                                            | **Fuente única:** para fórmulas de `T_A`, `T_R`, `T_C`, márgenes `L_R`, `L_C` y falsas alarmas.                                                                                        |
| **Captura de audio y hardware**                  | [`docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md`](docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md) y [`ARQUITECTURA.md`](docs/ingenieria/ARQUITECTURA.md) | **Lee:** para diseñar interfaces de audio, ASR y prototipo.                                                                                                                            |
| **Investigación y papers leídos**                | [`docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md`](docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md)                                                      | **Actualiza:** al analizar una fuente primaria siguiendo el [protocolo](docs/investigacion/PROTOCOLO-REVISION.md).                                                                     |
| **Ventana de contexto y lógica de alerta (D08)** | [`docs/investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md`](docs/investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md)                                              | **Lee:** ventana con decaimiento, registro de eventos, margen de falsas alarmas y disparo de la alerta.<br/>**No cierra D08.** Sus números salen de llamadas sintéticas.               |
| **Recorte de modelos on-device (D09)**           | [`docs/investigacion/PRIMERA-INVESTIGACION-MODELOS.md`](docs/investigacion/PRIMERA-INVESTIGACION-MODELOS.md)                                            | **Lee:** contrato de laboratorio, gamas y catálogo Hugging Face.<br/>**No cierra D09.**                                                                                                |
| **Texto final del informe de tesis**             | `docs/tesis/`                                                                                                                                           | **Actualiza:** redactando sobre capítulos reales según el [esqueleto](docs/tesis/ESQUELETO-INFORME.md). No crear capítulos vacíos.                                                     |
| **Término con significado preciso**              | [`docs/GLOSARIO.md`](docs/GLOSARIO.md)                                                                                                                  | **Actualiza:** cuando surge un término técnico nuevo o ambiguo.                                                                                                                        |

**No crear carpetas nuevas sin que el usuario lo pida.** Si algo no encaja en ninguna, consultá. El [README.md](README.md) mantiene el mapa de la estructura global.

## Convenciones

- **Archivos:** los documentos de proceso en `MAYUSCULAS-CON-GUION.md`; bitácoras
  `AAAA-MM-semana-NN.md`; seguimientos `AAAA-MM-DD.md`; ADRs `NNNN-titulo.md` con cuatro dígitos.
- **Fechas:** siempre absolutas (`2026-09-02`), nunca "la semana pasada".
- **Enlaces:** relativos entre documentos, formato Markdown. Verificá que resuelvan.

## Uso y sugerencia de Skills especializadas

El repositorio cuenta con skills en `.agents/skills/`. El agente debe sugerir proactivamente al usuario ejecutarlas según la fase de trabajo:

- **Decisiones abiertas, tickets ambiguos o diseño de alcance:** Sugerir `grill-with-docs` para una entrevista estructurada que resuelva incertidumbres antes de escribir código o comprometer documentos.
- **Implementación de código:** Sugerir `implement` (y `tdd` para módulos de cálculo de métricas, reglas o parsers) para construir código trazable y probado.
- **Finalización de código o Pull Requests:** Sugerir `code-review` antes de mergear o cerrar el issue.
- **Errores, excepciones o latencias inesperadas:** Sugerir `diagnosing-bugs` para aislar y resolver la causa raíz con pruebas.
- **Pruebas de concepto rápidas o spikes descartables:** Sugerir `prototype`.
- **Descomponer discusiones en issues para GitHub:** Sugerir `to-tickets` o `to-spec`.
