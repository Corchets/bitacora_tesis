---
name: resolver-issue
description: Guía y ejecuta el ciclo de vida completo de resolución o actualización de un issue de GitHub en el proyecto de vishing. Sincroniza fuentes de verdad, bitácora semanal, mapa de decisiones, registro de riesgos y entrega el comentario listo para GitHub.
---

# Skill: Resolver Issue

Esta skill implementa el ciclo de trabajo obligatorio para resolver o integrar trabajo de un issue en el proyecto de tesis de detección de vishing.

## Cuándo activar esta skill

- Cuando el usuario menciona que está trabajando en un issue (`Issue #N`, `tarea #N`, etc.).
- Cuando el usuario trae notas, respuestas de clase/profesor o resultados externos para integrar al proyecto.
- Cuando el usuario pide asistencia técnica, experimental o de redacción para completar un issue del backlog.

---

## Procedimiento paso a paso

### Paso 1: Identificar el issue y clasificar el tipo de trabajo
1. Identificar número, título y tipo (`type:decision`, `type:research`, `type:experiment`, `type:task`, `type:writing`).
2. Determinar la **fuente de verdad principal** afectada usando la tabla de `AGENTS.md` / `GUIA-DE-ARCHIVOS.md`.
3. Leer los archivos involucrados antes de proponer o aplicar cambios.

### Paso 2: Ejecutar el trabajo respetando las 3 Reglas de Oro
- **Regla 1 (No inventar decisiones):** Si la resolución implica una elección no acordada previamente por el equipo o el profesor, marcarla explícitamente:
  `> **Estado: propuesta sin discutir.**` y enlazar la decisión abierta.
- **Regla 2 (No inventar citas):** No usar marcadores de deep research (`citeturn...`) como citas bibliográficas formales ni inventar papers.
- **Regla 3 (No datos personales ni audio):** Mantener audios (`.wav`, `.mp3`, etc.) y PII fuera de Git.
- Respetar el estilo del proyecto: Español de Argentina para prosa técnica, términos de etiquetas técnicas en inglés.

### Paso 3: Sincronizar el estado vivo del proyecto
Todo trabajo cerrado o con avance significativo debe impactar los siguientes archivos:

1. **Fuente de verdad temática:**
   - Escribir o editar el archivo correspondiente (`PLAN-DE-TRABAJO.md`, `CATALOGO-ESCENARIOS.csv`, `matriz-literatura.csv`, etc.).
2. **Bitácora semanal (`docs/gestion/bitacora/AAAA-MM-semana-NN.md`):**
   - Localizar el archivo de la semana en curso (o crear el nuevo si cambió la semana).
   - En la sección `## Qué se hizo`: agregar la fila con la persona, trabajo y estado `☑` o `⏳`.
   - En `## Qué existe hoy que no existía el viernes pasado`: agregar la viñeta con el artefacto o evidencia nueva generada.
3. **Mapa de decisiones (`docs/gestion/MAPA-DECISIONES.md`):**
   - Si el issue resuelve una decisión (ej. D01, D02, D05), cambiar su estado a cerrado y enlazar la evidencia.
   - Si es una decisión arquitectónica duradera, crear el ADR en `docs/ingenieria/adr/NNNN-titulo.md` (siguiendo `PLANTILLA-ADR.md`).
4. **Registro de riesgos (`docs/gestion/REGISTRO-RIESGOS.md`):**
   - Si el resultado mitiga un riesgo (ej. R01, R06), ajustar probabilidad/impacto y estado.
   - Si se detecta un riesgo nuevo no mapeado, agregarlo con su mitigación y contingencia.

### Paso 4: Entregar el comentario de cierre para GitHub
Al finalizar la respuesta, generar un bloque Markdown delimitado listo para que el usuario lo copie y pegue en el issue de GitHub:

```markdown
### Cierre del Issue #<NÚMERO> — <TÍTULO>

**Resultado:**
<Resumen de lo resuelto o descubierto>

**Evidencia y archivos modificados:**
- [<Archivo 1>](<ruta>): <descripción de cambio>
- [Bitácora semanal](<ruta>): registrado
- [Decisiones/Riesgos]: <actualizado si corresponde>

**Decisiones tomadas / abiertas:**
- <Detalle o 'Ninguna nueva'>

**Nuevos riesgos o preguntas detectadas:**
- <Detalle o 'Ninguno'>

**Próxima acción:**
- <Próximo issue o tarea recomendada>

Closes #<NÚMERO>
```
