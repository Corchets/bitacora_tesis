# Informe final: índice y estado

> **Nota del 2026-11-25:** el informe se reescribe con la estructura nueva del [esqueleto](ESQUELETO-INFORME.md) (11 capítulos, ordenados por tema y no por fecha). Los `CAP-*.md` de esta carpeta y la tabla de abajo quedan como material de partida, no como base a corregir.

**Para redactar:** empezá por el [mapa del proceso](MAPA-DEL-PROCESO.md), la guía de las etapas del trabajo y de dónde está la evidencia de cada una. Antes de escribir resultados, discusión o conclusiones, leé los [hallazgos](../hallazgos/README.md).

> **Nota del 2026-11-21:** la evaluación final corrió el 2026-11-19 (#52, cerrado) y los capítulos 8, 9 y 11 ya la incorporan; el párrafo siguiente es el estado al 2026-11-03. La tabla de abajo se actualizó ese día en las filas de Preliminares y de los capítulos 4, 8, 9 y 11.

Borrador completo al 2026-11-03. **La evaluación final no se corrió:** los capítulos 8, 9 y 11 quedan abiertos hasta tener el test reservado (#52). En el texto, lo pendiente aparece entre corchetes y en negrita. La estructura sale del [esqueleto](ESQUELETO-INFORME.md).

**Correcciones pendientes.** Cuando un [hallazgo](../hallazgos/README.md) contradice lo escrito y la corrección depende de una decisión abierta, el capítulo lleva una marca `> **Corregir (#N):**` donde está el texto, con el issue del que depende. Al cerrar ese issue se reescribe el texto y se borra la marca. Para listarlas: `grep -rn "Corregir (#" docs/tesis`. Al 2026-11-06, los capítulos 3 a 9 y 11 tienen marcas que dependen de [#51](https://github.com/Corchets/bitacora_tesis/issues/51) (configuración final y ADR 0002). El 2026-11-11, con el [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) registrado, se resolvieron todas.

| Capítulo | Estado | Qué falta |
|---|---|---|
| [Preliminares](CAP-00-PRELIMINARES.md) | Borrador | Contribuciones; título (D13). El resumen y el abstract ya llevan la evaluación final |
| [1. Introducción](CAP-01-INTRODUCCION.md) | Borrador completo | Revisión del equipo |
| [2. Marco conceptual y antecedentes](CAP-02-MARCO-CONCEPTUAL-Y-ANTECEDENTES.md) | Borrador completo | Estilo bibliográfico; revisión cruzada de fuentes (#25) |
| [3. Requisitos y análisis](CAP-03-REQUISITOS-Y-ANALISIS.md) | Borrador completo | RAM del teléfono de referencia, de fuente del fabricante |
| [4. Metodología](CAP-04-METODOLOGIA.md) | Borrador con propuestas | D07 sigue abierta: no hay muestra común anotada por los cuatro. D08 quedó resuelta con límites el 2026-11-21 (#33, cerrado); falta ajustar lo marcado como propuesta a lo que se fijó |
| [5. Diseño y arquitectura](CAP-05-DISENO-Y-ARQUITECTURA.md) | Borrador completo | Revisión del equipo |
| [6. Implementación](CAP-06-IMPLEMENTACION.md) | Borrador completo | Revisión del equipo |
| [7. Verificación y pruebas](CAP-07-VERIFICACION-Y-PRUEBAS.md) | Borrador actualizado | Detalle por prueba de la configuración final. #28 se cerró sin reproducción registrada por otra persona |
| [8. Resultados](CAP-08-RESULTADOS-EXPERIMENTALES.md) | Borrador del 2026-11-20, con la evaluación final (§8.3.4) | PI2 con marcas humanas, E2 y el resto de [§8.7](CAP-08-RESULTADOS-EXPERIMENTALES.md#87-pendientes-del-capítulo) |
| [9. Discusión](CAP-09-DISCUSION.md) | Borrador del 2026-11-20, propuesta de redacción sin discutir | Revisarlo entre los cuatro |
| [10. Gestión](CAP-10-GESTION-DEL-PROYECTO.md) | Borrador | Contribuciones de los cuatro |
| [11. Conclusiones](CAP-11-CONCLUSIONES.md) | Borrador del 2026-11-20, propuesta de redacción sin discutir | Revisarlo entre los cuatro |

**Sin escribir:** anexos (manual de anotación, consentimiento sin datos identificables, configuraciones, manual de instalación), agradecimientos, índices, referencias unificadas y formato final en A4.

Decisiones técnicas: el ASR, en el [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md); el detector, en los [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md), [0006](../ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md), [0007](../ingenieria/adr/0007-consulta-al-cerrar-cada-turno-de-otra.md), [0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md) y [0009](../ingenieria/adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md); el alcance y la evaluación, en los [ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md) y [0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md) (propuestas sin discutir) y [0004](../ingenieria/adr/0004-legitimas-entrantes-nuevas-y-test-aparte.md). Comparación: [candidatos de desarrollo](../evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md). Evaluación final: [análisis](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md) y [qué concluir](../evaluacion/CONCLUSIONES-EVALUACION-FINAL.md).
