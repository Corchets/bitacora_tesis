# Backlog inicial para importar a GitHub Issues

Este archivo es una semilla transitoria porque `gh` no está autenticado. Después de
crear estos issues en GitHub, agregar aquí la fecha de importación y dejar de
actualizarlo. Desde ese momento GitHub será la única fuente del backlog.

**Estado de importación:** pendiente  
**Milestone sugerido:** `M0 — Dirección aprobada — 2026-09-09`

## 1. `[Decisión] Aprobar preguntas y alcance base`

- **Etiquetas:** `type:decision`, `area:planning`, `priority:p0`
- **Resultado:** respuesta del profesor sobre PI1–PI2, E1–E2, núcleo, extensiones y
  fuera de alcance.
- **Evidencia:** Plan de Trabajo y minuta del 9 de septiembre.
- **Dependencias:** ninguna.
- **Terminado cuando:** la respuesta textual está registrada, el Plan de Trabajo
  fue actualizado y toda corrección se convirtió en issue.

## 2. `[Decisión] Elegir estrategia de acceso al audio`

- **Etiquetas:** `type:decision`, `area:asr-audio`, `priority:p0`
- **Resultado:** replay, altavoz y VoIP tienen un rol aprobado; telefonía
  privilegiada tiene alcance explícito.
- **Evidencia:** comparación técnica y respuesta del profesor.
- **Dependencias:** ninguna.
- **Terminado cuando:** alternativa base, integración objetivo y contingencia están
  registradas; se abre ADR si corresponde.

## 3. `[Investigación] Construir catálogo inicial de escenarios argentinos`

- **Etiquetas:** `type:research`, `area:data-ethics`, `priority:p0`
- **Resultado:** 6–8 semillas fraudulentas y sus negativos legítimos pareados.
- **Evidencia:** fuentes oficiales/académicas y filas completas en
  `CATALOGO-ESCENARIOS.csv`.
- **Dependencias:** ninguna.
- **Terminado cuando:** cada semilla tiene fuente, objetivo, maniobras, acción
  crítica y negativo; otra persona revisó pertinencia y seguridad.

## 4. `[Tarea] Redactar problema, beneficiario y daño evitado`

- **Etiquetas:** `type:writing`, `area:planning`, `priority:p0`
- **Resultado:** formulación de cinco líneas utilizable en clase e Informe Final.
- **Dependencias:** puede avanzar junto al catálogo de escenarios.
- **Terminado cuando:** identifica usuario, contexto, decisión bajo presión, daño y
  limitación de defensas existentes; está incorporado al Plan de Trabajo.

## 5. `[Experimento] Ejecutar spike WAV → ASR local`

- **Etiquetas:** `type:experiment`, `area:asr-audio`, `priority:p0`
- **Resultado:** una grabación simulada se transcribe localmente con tiempos y
  errores visibles.
- **Datos:** audio creado por el equipo, sin información real; no pertenece todavía
  al corpus final.
- **Métricas:** duración, tiempo de proceso, real-time factor aproximado, texto y
  errores sobre términos críticos.
- **Terminado cuando:** comando/configuración, hardware, audio de entrada autorizado,
  salida y observaciones permiten repetir la prueba.

## 6. `[Tarea] Dibujar arquitectura v0 y dos warnings`

- **Etiquetas:** `type:task`, `area:mobile-ux`, `priority:p1`
- **Resultado:** diagrama audio→ASR→estado→detector→alerta y mockups de riesgo
  moderado/alto.
- **Dependencias:** estrategia de audio puede seguir abierta; representar la
  interfaz como desacoplada.
- **Terminado cuando:** cada componente tiene responsabilidad, entradas/salidas y
  restricción principal; los warnings dicen qué ocurre, por qué importa y qué hacer.

## 7. `[Investigación] Confirmar requisitos académicos faltantes`

- **Etiquetas:** `type:research`, `area:thesis`, `priority:p0`
- **Resultado:** fecha, plantilla, citas, extensión, entregables, tutor, defensa y
  procedimiento de participantes confirmados.
- **Evidencia:** respuesta textual del profesor o documento institucional.
- **Dependencias:** clase del 9 de septiembre.
- **Terminado cuando:** `REQUISITOS-ACADEMICOS.md` no contiene pendientes que
  bloqueen el hito siguiente.

## 8. `[Decisión] Aprobar método y tamaño del piloto del corpus`

- **Etiquetas:** `type:decision`, `area:data-ethics`, `priority:p0`
- **Resultado:** población, consentimiento, 4+4 semillas y 12–20 conversaciones
  piloto autorizadas o corregidas.
- **Evidencia:** método del corpus, plan de participantes y respuesta del profesor.
- **Dependencias:** issues 1, 3 y 7.
- **Terminado cuando:** se puede grabar el piloto sin decisiones éticas, de datos o
  de diseño abiertas.

## Importación

1. Autenticar GitHub CLI con `gh auth login -h github.com`.
2. Crear las etiquetas definidas en `METODO-DE-TRABAJO.md`.
3. Crear el milestone M0 con vencimiento 2026-09-09.
4. Crear estos ocho issues sin assignee.
5. Enlazar dependencias en los cuerpos.
6. Cambiar arriba el estado a `importado AAAA-MM-DD` y congelar este archivo.
