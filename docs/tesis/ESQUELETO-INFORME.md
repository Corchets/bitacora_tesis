# Esqueleto provisional del Informe Final

**Institución:** UNSTA — Ingeniería en Informática, Plan 2008  
**Formato informado:** digital, A4, carilla simple y aproximadamente 100 páginas

Debe reemplazarse por la plantilla oficial de la cátedra si aparece. La estructura
respeta los contenidos comunicados por el profesor y agrega la trazabilidad
necesaria para evaluar el producto y sus experimentos.

## Presupuesto provisional de páginas

No es una obligación hasta confirmar si las 100 páginas incluyen referencias y
anexos. Sirve para evitar que el marco teórico ocupe la mitad del trabajo.

| Bloque | Páginas orientativas |
|---|---:|
| Preliminares y resúmenes | 5–8 |
| Introducción y objetivos | 7–10 |
| Marco teórico y antecedentes | 15–20 |
| Requisitos, metodología y datos | 15–20 |
| Arquitectura, tecnologías e implementación | 20–25 |
| Pruebas y resultados | 18–25 |
| Discusión, gestión y conclusiones | 10–15 |
| Referencias y anexos | según indicación del profesor |

## Preliminares

- Carátula con logo UNSTA, título, cuatro integrantes, tutor y año.
- Resumen y palabras clave en español.
- Abstract y keywords en inglés.
- Agradecimientos opcionales.
- Índices de contenido, figuras, tablas y siglas.
- Declaración breve de contribuciones del equipo.

## 1. Introducción

- Contexto y motivación.
- Problema y beneficiarios.
- Objetivo general y objetivos específicos.
- Preguntas de investigación e hipótesis.
- Alcance, exclusiones y contribuciones.
- Organización del informe.

## 2. Marco conceptual y antecedentes

- Vishing e ingeniería social.
- Detección de llamadas y sistemas existentes.
- ASR, clasificación incremental e intervención.
- Datasets y evaluación temprana.
- Síntesis crítica y vacío que aborda el proyecto.

## 3. Requisitos y análisis del problema

- Interesados y escenarios.
- Requisitos funcionales y no funcionales.
- Restricciones Android, privacidad y ética.
- Criterios de aceptación y trazabilidad.
- Alternativas consideradas.

## 4. Metodología

- Diseño del estudio y variables.
- Construcción del corpus y muestreo.
- Taxonomía, anotación y acuerdo.
- Splits y prevención de leakage.
- Baselines, modelos y protocolo experimental.
- Métricas y análisis estadístico.
- Consideraciones éticas y plan de datos.

## 5. Diseño y arquitectura

- Contexto y componentes.
- Flujo de audio y modelo de datos.
- ASR, detector, estado temporal y warnings.
- Decisiones arquitectónicas y alternativas.
- Seguridad, privacidad y despliegue local.

## 6. Implementación

- Stack y versiones.
- Implementación por componente.
- Integración y automatización experimental.
- Aplicación/demo y limitaciones técnicas.

## 7. Verificación y pruebas de software

- Estrategia de pruebas.
- Unitarias, integración y end-to-end.
- Requisitos no funcionales.
- Trazabilidad requisito→prueba→resultado.

## 8. Resultados experimentales

- Descripción final del corpus.
- Benchmark ASR.
- Comparación de detectores.
- Gold transcript frente a ASR.
- Detección temprana y latencia.
- Falsas alarmas y hard negatives.
- Ablations y rendimiento móvil.

## 9. Discusión

- Respuesta a cada pregunta de investigación.
- Interpretación y comparación con antecedentes.
- Análisis de errores.
- Amenazas a la validez interna, externa, de constructo y conclusión.
- Implicaciones de ingeniería, éticas y de uso.

## 10. Gestión del proyecto

- Modelo de proceso y planificación.
- Evolución del alcance y decisiones.
- Riesgos y mitigaciones.
- Contribuciones y carga de trabajo.

## 11. Conclusiones

- Aportes y resultados principales.
- Qué hipótesis fueron o no respaldadas.
- Limitaciones.
- Trabajo futuro acotado.

## Anexos

- Manual de anotación y esquemas.
- Consentimiento/protocolo aprobado, sin datos identificables.
- Detalle de métricas y configuraciones.
- Matriz de trazabilidad.
- Manual de instalación/ejecución y paquete reproducible.
- Manual de usuario o demo, si se exige.

## Regla de escritura

Cada capítulo comienza como esquema y se actualiza durante el desarrollo. Las
figuras y tablas deben generarse desde datos/versiones trazables. Ningún resultado
entra al informe sin configuración, dataset, split, seed, commit y fecha.

## Correspondencia con lo solicitado por el profesor

| Contenido indicado | Ubicación propuesta |
|---|---|
| Introducción | Capítulo 1 |
| Objetivos | Capítulo 1, con sección propia |
| Marco teórico | Capítulo 2 |
| Arquitecturas | Capítulos 3 y 5 |
| Tecnologías | Capítulos 5 y 6 |
| Comparaciones | Capítulos 2 y 8 |
| Metodologías utilizadas | Capítulos 4, 7 y 10 |
| Etapas del proyecto | Capítulos 6 y 10 |
| Conclusión | Capítulo 11 |
