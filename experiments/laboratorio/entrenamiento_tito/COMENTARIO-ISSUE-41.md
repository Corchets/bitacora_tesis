Refs #41 — avance materializado el 2026-10-02; mantener el issue abierto.

Se produjo un banco de textos argentinos para Tito (`experiments/laboratorio/entrenamiento_tito/README.md`) independiente de los casos y
resultados anteriores. Búsqueda y generación con Orca (`gpt-6-luna`, esfuerzo `medium`), con
tareas y modelos efectivos registrados en `experiments/laboratorio/entrenamiento_tito/orquestacion.json`.

- Generados: 6.000 frases/fragmentos sintéticos originales, organizados en 300 familias.
- Exportados en `experiments/laboratorio/entrenamiento_tito/semillas.json`: 5.520 textos (2.620 `estafa`, 2.900 `legitima`), compatibles con `DetectorEncoder` de esta rama.
- Apartados: 480 textos de 24 familias, con motivos en `experiments/laboratorio/entrenamiento_tito/exclusiones.json` y conservación para reescritura.
- Fuentes: 17 URL primarias únicas; respaldan modalidades y contexto, sin importar conversaciones externas.
- Verificación: exportaciones reproducibles y sin duplicados normalizados, siete pruebas aprobadas; RoBERTuito registra 14–52 tokens por texto, por debajo del límite de 128.

Las variantes son dependientes dentro de cada familia. No se creó un test, no se entrenó el
detector y no se midió mejora. D07/D08/D09 permanecen abiertas; falta la revisión humana de
etiquetas y naturalidad. La investigación de fuentes y sus límites queda en
`docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md`, §2.3.

Próxima acción: revisar familias completas, ajustar la cabeza del encoder con esta exportación
y medir errores con textos independientes de #45. El esquema definitivo del corpus y la
comparación de métodos de entrenamiento del alcance original de #41 siguen pendientes.
