# Instrucciones del repositorio

## Objetivo

Ayudar a producir un Proyecto Final defendible y reproducible sobre detección
incremental de vishing. Priorizar evidencia y decisiones trazables sobre volumen de
documentación o complejidad técnica.

## Flujo obligatorio

1. Leer el issue activo y autoasignarlo antes de modificar el repositorio. Durante
   el bootstrap sin issues, usar `docs/gestion/BACKLOG-INICIAL.md`.
2. Leer [el método](docs/gestion/METODO-DE-TRABAJO.md) cuando se planifique, cree,
   ejecute o cierre trabajo.
3. Cargar solo la referencia disparada por la tarea:
   - **Investigación:** leer `docs/investigacion/PROTOCOLO-REVISION.md` y actualizar
     `docs/investigacion/matriz-literatura.csv`.
   - **Corpus o participantes:** leer `docs/datos-etica/METODO-CREACION-CORPUS.md`
     y `docs/datos-etica/PLAN-PARTICIPANTES-Y-CORPUS.md`.
   - **Experimento o métricas:** leer
     `docs/investigacion/PREGUNTAS-DE-INVESTIGACION.md` y el protocolo experimental
     enlazado por el issue.
   - **Audio, Android o VoIP:** leer
     `docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md` y los ADR relacionados.
   - **Informe o entrega:** leer `docs/propuesta/REQUISITOS-ACADEMICOS.md` y
     `docs/tesis/ESQUELETO-INFORME.md`.
4. Producir la evidencia exigida por la definición de terminado.
5. Actualizar una sola fuente de verdad y enlazarla desde el issue.
6. Registrar pruebas, limitaciones y decisiones antes de cerrar el issue.

## Invariantes

- GitHub Issues es el único backlog activo; el roadmap contiene hitos, no tareas.
- Cada afirmación externa material tiene fuente verificable.
- Cada experimento registra dataset/split, configuración, seed, versión de código,
  métricas y salida.
- Audio, consentimientos firmados, datos identificables y secretos permanecen fuera
  de Git.
- Las decisiones de alcance, participantes y publicación requieren validación del
  profesor/tutor.

## Criterio de cierre

Una sesión termina con el issue actualizado, la evidencia enlazada, las fuentes de
verdad consistentes y las verificaciones pertinentes ejecutadas. Si resta trabajo,
el issue permanece abierto con una próxima acción concreta y un bloqueo explícito.
