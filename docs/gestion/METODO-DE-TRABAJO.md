# Método de trabajo

Este documento es la fuente de verdad del proceso. Describe cómo una persona o un
asistente inicia, ejecuta y cierra trabajo. El backlog vive en GitHub Issues; este
archivo no enumera tareas.

## 1. Modelo de trabajo

Se trabaja en ciclos semanales, agrupados por los hitos del roadmap. Cada issue
produce un resultado observable. El equipo toma trabajo
por autoasignación y revisa en pareja los cambios que afectan datos, métricas,
arquitectura o el informe.

Tres palabras gobiernan el flujo:

- **Issue:** compromiso y coordinación.
- **Evidencia:** resultado verificable.
- **Fuente de verdad:** lugar único donde queda el conocimiento durable.

## 2. Fuentes de verdad

| Información                                       | Fuente                                                     |
| ------------------------------------------------- | ---------------------------------------------------------- |
| Trabajo abierto, prioridad, responsable, bloqueos | GitHub Issues                                              |
| Hitos, gates y fechas                             | `docs/propuesta/PLAN-DE-TRABAJO.md`                        |
| Resultado de una decisión                         | `MAPA-DECISIONES.md`; detalle técnico en su fuente o ADR    |
| Riesgos                                           | `REGISTRO-RIESGOS.md`                                      |
| Seguimientos con el profesor                      | `docs/gestion/seguimientos/AAAA-MM-DD.md`                  |
| Evidencia bibliográfica y estado del arte         | `docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md`           |
| Diseño y referencia del corpus                    | `docs/corpus/METODO-CREACION-CORPUS.md` y `MANUAL-ANOTACION.md` |
| Reglas académicas                                 | `REQUISITOS-ACADEMICOS.md`                                 |
| Manuscrito final                                  | `docs/tesis/`                                              |

Cuando un issue cambia una de estas cosas, actualiza esa fuente. El issue enlaza el
resultado; no lo duplica.

## 3. Tipos de issue

### Decisión

Resuelve una elección que bloquea trabajo. La descripción contiene pregunta,
alternativas, evidencia necesaria y quién debe validar.

**Terminado cuando:** el comentario de cierre registra alternativa elegida, motivo,
evidencia, consecuencias y nuevos issues. Si la decisión cambia una interfaz o una
restricción duradera, también existe un ADR.

### Investigación

Busca evidencia externa para sostener una afirmación o decisión.

**Terminado cuando:** las consultas y criterios están registrados, cada afirmación
material tiene fuente verificable, la síntesis del estado del arte fue actualizada y el
issue contiene síntesis, incertidumbres y decisión habilitada.

### Experimento

Responde una pregunta mediante datos y mediciones.

**Terminado cuando:** registra pregunta, datos/split, configuración, seed, versión
de código, hardware, métricas, salidas, interpretación, limitaciones y comando o
procedimiento de reproducción.

### Tarea

Produce un artefacto necesario: código, esquema, guiones, UI, prueba o documento.

**Terminado cuando:** el artefacto existe, satisface los criterios del issue, fue
verificado y está enlazado.

### Redacción

Actualiza una parte del Informe Final.

**Terminado cuando:** la sección responde su objetivo, las afirmaciones están
citadas, tablas/figuras son trazables y la revisión cruzada fue incorporada.

## 4. Estado y bloqueos en GitHub

Los issues activos no necesitan etiquetas de tipo, área ni prioridad. El título
explica el resultado; el milestone ubica el hito; el assignee identifica responsable.

Una dependencia que impide comenzar se registra en **Relationships → Blocked by**
y se explica brevemente en el cuerpo. Una referencia relacionada no es un bloqueo.
Las [relaciones nativas de GitHub](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies)
permiten ver **Blocked by** y **Blocking**, con el indicador **Blocked** en los issues afectados.

**Disponible para autoasignarse:** abierto, sin responsable, sin bloqueos pendientes
y con datos/accesos disponibles. Elegir primero trabajo del hito actual. Una
investigación sin bloqueos de un hito posterior puede adelantarse si ayuda al arranque;
no desplaza la próxima entrega técnica.

Las dependencias apuntan a entregas completas. Si se necesita un resultado intermedio,
se divide el issue: por ejemplo, el primer par de llamadas libera ASR y detector sin
esperar todo el piloto. Una fecha orientativa no vuelve disponible una tarea bloqueada.

## 5. Inicio de una sesión

1. Abrir el milestone actual.
2. Elegir un issue abierto, no bloqueado y sin responsable.
3. Leer pregunta/resultado, dependencias y definición de terminado.
4. Autoasignarse y comentar el enfoque inmediato en una o dos frases.
5. Leer solo las fuentes necesarias para el resultado del issue.

**Listo para empezar cuando:** el resultado esperado es observable, las dependencias
están resueltas, los datos/accesos necesarios existen y la definición de terminado
permite distinguir finalizado de parcial. Si falta algo, el primer resultado es
corregir o dividir el issue.

## 6. Ejecución

1. Producir la unidad de evidencia más pequeña que reduzca la incertidumbre.
2. Registrar decisiones mientras ocurren.
3. Mantener código, datos, configuración y resultados trazables.
4. Pedir revisión cruzada cuando el cambio afecta validez, privacidad, interfaces o
   una conclusión del informe.
5. Crear un issue nuevo cuando aparece trabajo independiente; enlazarlo como
   dependencia. No ampliar silenciosamente el issue activo.

La documentación se modifica junto al trabajo que la vuelve verdadera. No existe
una fase posterior para “documentar todo”.

## 7. Cierre de una sesión

1. Ejecutar verificaciones relevantes.
2. Comparar el resultado con cada criterio del issue.
3. Actualizar la fuente de verdad afectada.
4. Enlazar commit, documento, datos, gráfico o salida reproducible.
5. Registrar qué se aprendió, limitaciones y consecuencias.
6. Cerrar si está completo y revisar qué dependientes quedaron habilitados. Si continúa abierto, escribir una próxima acción
   concreta y el bloqueo, sin declarar progreso genérico.

Si una tarea se retira del compromiso actual, cerrar como **no planificada**
(`not_planned`) y explicar el motivo y dónde continúa el trabajo útil. Ese cierre
no se registra como implementación terminada; se conservan antecedentes y artefactos.

**Sesión cerrada cuando:** otra persona puede entender qué cambió, verificarlo y
continuar sin depender de una explicación oral.

## 8. Ciclo semanal

### Inicio de semana — selección

- Revisar el milestone y los riesgos de prioridad alta.
- Elegir pocas evidencias compatibles con la capacidad real.
- Autoasignar issues y confirmar dependencias.

**Terminado cuando:** cada issue elegido tiene responsable, resultado, criterio de
cierre y fecha dentro del ciclo.

### Mitad de semana — integración

- Integrar al menos una vez audio, datos, detector y/o documento que hayan cambiado.
- Hacer visibles incompatibilidades y abrir decisiones necesarias.

**Terminado cuando:** existe evidencia integrada o un bloqueo reproducible.

### Fin de semana — demo y escritura

- Mostrar evidencia nueva.
- Actualizar resultados, riesgos y secciones del informe afectadas.
- Repriorizar el backlog según lo aprendido.

**Terminado cuando:** el milestone refleja la realidad y no quedan resultados solo
en notebooks personales, chats o memoria.

## 9. Seguimiento con el profesor

### Preparación, 48 horas antes

1. Crear `seguimientos/AAAA-MM-DD.md` con los temas a consultar.
2. Elegir como máximo tres decisiones que el equipo no puede cerrar solo.
3. Enlazar evidencia verificable.
4. Comparar compromisos anteriores con resultados.
5. Proponer el próximo gate con criterio observable.

**Terminado cuando:** la reunión puede conducirse mostrando archivos y resultados,
sin reconstruir oralmente lo que ocurrió.

### Durante la reunión

- Registrar la respuesta textual del profesor.
- Distinguir sugerencia, requisito y decisión.
- Confirmar fecha y evidencia esperada del siguiente seguimiento.

### Dentro de las 24 horas posteriores

1. Limpiar la minuta.
2. Actualizar requisitos, decisiones, roadmap y riesgos afectados.
3. Cerrar issues resueltos y crear los nuevos.
4. Publicar un resumen breve al equipo.

**Terminado cuando:** cada observación del profesor tiene consecuencia, futuro issue
o decisión explícita de no actuar.

## 10. Flujo de investigación

1. Formular la afirmación o decisión que necesita evidencia.
2. Buscar con el protocolo bibliográfico.
3. Extraer fuente, población/datos, método, resultados y límites.
4. Contrastar evidencia que pueda refutar la interpretación inicial.
5. Actualizar la síntesis del estado del arte con la evidencia primaria y lo necesario para decidir.

**Terminado cuando:** la afirmación importante tiene evidencia primaria aplicable,
las contradicciones están resueltas o declaradas y otra búsqueda no cambiaría la
decisión actual.

## 11. Flujo de experimento

1. Vincular el experimento con una pregunta y métrica predefinida.
2. Congelar datos/split y configuración antes de mirar el test.
3. Ejecutar baseline y variante bajo condiciones comparables.
4. Conservar salidas crudas y generar tablas/figuras mediante código.
5. Interpretar también errores y resultados negativos.

**Terminado cuando:** otra persona puede repetirlo y obtener resultados equivalentes
sin usar conocimiento no escrito.

## 12. Flujo de escritura

1. Abrir la sección del esqueleto afectada por el trabajo reciente.
2. Escribir afirmación, evidencia e interpretación.
3. Enlazar figura/tabla con su experimento.
4. Hacer revisión cruzada.

**Terminado cuando:** la sección es consistente con el estado actual y no contiene
marcadores de citas internos, resultados manuales ni promesas sin evidencia.

## 13. Pull requests

Usar una rama y un pull request cuando haya código, cambios de método, decisiones
arquitectónicas o una sección sustancial del informe. Cambios pequeños de minuta o
metadatos pueden ir directos a la rama acordada por el equipo.

El PR enlaza el issue con `Closes #N`, explica evidencia y verificaciones, y obtiene
al menos una revisión para cambios de alto impacto. Un PR no mezcla áreas sin una
razón explícita.
