# Proyecto Final Integrador — detector de vishing

Repositorio de trabajo del Proyecto Final de Ingeniería en Informática, Plan 2008,
UNSTA.

El proyecto investiga si un sistema que procesa audio en español de manera local e
incremental puede advertir un posible vishing antes de que la persona realice una
acción riesgosa. El resultado incluye investigación, corpus controlado, software,
evaluación reproducible e Informe Final.

## Empezar una sesión de trabajo

1. Abrir el backlog en GitHub Issues y elegir un issue no bloqueado.
2. Autoasignarse antes de trabajar.
3. Leer la definición de terminado del issue y la documentación que corresponda.
4. Producir evidencia verificable: documento, decisión, código, prueba o resultado.
5. Actualizar la fuente de verdad afectada y enlazar la evidencia en el issue.
6. Cerrar el issue solo cuando cumple todos sus criterios.

El flujo completo, los tipos de issue y las reglas de cierre están en
[Método de trabajo](docs/gestion/METODO-DE-TRABAJO.md). La función y momento de
actualización de cada archivo están en [Guía de archivos](docs/GUIA-DE-ARCHIVOS.md).
Los asistentes de código deben leer [AGENTS.md](AGENTS.md).

## Para la próxima clase

- [Paquete del 9 de septiembre](docs/gestion/seguimientos/2026-09-09.md)
- [Plan de Trabajo v1](docs/propuesta/PLAN-DE-TRABAJO.md)
- [Alternativas para obtener audio](docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md)
- [Preguntas de investigación](docs/investigacion/PREGUNTAS-DE-INVESTIGACION.md)

## Documentos principales

| Necesidad | Documento |
|---|---|
| Entender alcance, fases y fechas | [Plan maestro](docs/gestion/PLAN-MAESTRO.md) |
| Saber cómo trabajar cada sesión | [Método de trabajo](docs/gestion/METODO-DE-TRABAJO.md) |
| Saber dónde registrar algo | [Guía de archivos](docs/GUIA-DE-ARCHIVOS.md) |
| Preparar la propuesta académica | [Plan de Trabajo](docs/propuesta/PLAN-DE-TRABAJO.md) |
| Investigar y registrar fuentes | [Protocolo bibliográfico](docs/investigacion/PROTOCOLO-REVISION.md) |
| Diseñar grabaciones simuladas | [Método del corpus](docs/datos-etica/METODO-CREACION-CORPUS.md) |
| Consultar riesgos activos | [Registro de riesgos](docs/gestion/REGISTRO-RIESGOS.md) |
| Redactar el informe | [Esqueleto del informe](docs/tesis/ESQUELETO-INFORME.md) |

## Fuentes de verdad

- **Trabajo pendiente y responsables:** GitHub Issues.
- **Fases y fechas:** `docs/gestion/PLAN-MAESTRO.md`.
- **Decisiones cerradas:** comentario de resolución del issue; un ADR si es una
  decisión arquitectónica duradera.
- **Fuentes y afirmaciones:** `matriz-literatura.csv` y documentos de investigación.
- **Resultados:** configuración y salida versionada de cada experimento.
- **Texto entregable:** `docs/tesis/`.

Una tarea no se copia a varios documentos. Los documentos explican; los issues
coordinan el trabajo.

## Guardrails

- Audio, consentimientos firmados, datos identificables y credenciales viven fuera
  de Git.
- El corpus usa conversaciones representadas y datos ficticios.
- Replay en streaming es la base reproducible; VoIP es una integración candidata.
- La captura universal de llamadas celulares desde una app Android ordinaria queda
  fuera del núcleo.
- Un resultado negativo bien medido también es un resultado válido.

## Estado de GitHub Issues

Las plantillas ya están en `.github/ISSUE_TEMPLATE/`. La creación del backlog
remoto está pendiente porque la sesión local de `gh` no está autenticada. Después
de ejecutar `gh auth login -h github.com`, se crean los issues de
[Backlog inicial](docs/gestion/BACKLOG-INICIAL.md) y ese archivo deja de actualizarse.
