# Plan integral para el Proyecto Final de vishing

**Audiencia:** equipo de cuatro estudiantes y profesor/tutor  
**Fecha:** 2 de septiembre de 2026  
**Alcance:** requisitos académicos, proceso de tesis/proyecto final, investigación,
roadmap, gobernanza, división del equipo y documentación inicial.  
**Contexto confirmado:** Ingeniería en Informática, Plan 2008, UNSTA; grupo de
cuatro autorizado y entrega hacia fines de diciembre de 2026.

## Respuesta ejecutiva

No se dispone de un reglamento específico público para el Plan 2008. El profesor
indicó entrega digital A4, portada institucional, resúmenes español/inglés, cuerpo
técnico con introducción, objetivos, teoría, arquitecturas, tecnologías,
comparaciones, metodología, etapas y conclusiones, y unas 100 páginas como
referencia. El detector debe estructurarse como producto de software con un estudio
empírico reproducible embebido. El trabajo comienza cerrando decisiones
de alcance, plataforma, datos, ética y evaluación, y continúa en iteraciones que
siempre producen evidencia demostrable para el profesor.

## Hallazgos determinantes

1. La web oficial de UNSTA confirma el Proyecto Final Integrador y un perfil
   orientado a proyectos, software e inteligencia artificial.
2. El repositorio UNSTA conserva ejemplos de proyectos finales de la carrera; uno
   público tiene 103 páginas, consistente con la indicación del profesor.
3. Android impide que una aplicación ordinaria capture uplink/downlink de una
   llamada PSTN mediante las fuentes reservadas; replay y VoIP controlado preservan
   la pregunta científica sin depender de privilegios de sistema.
4. La literatura 2025–2026 muestra que vishing en tiempo real es un campo activo,
   con escasez de datos y problemas abiertos de intervención y falsas alarmas.
5. Grabar voces y almacenar transcripciones requiere decidir antes consentimiento,
   finalidad, acceso, seguridad, publicación y eliminación.
6. La ruta más defendible combina corpus controlado en español, detector
   incremental, evento crítico, evaluación gold-vs-ASR, falsas alarmas, latencia,
   anticipación e inferencia local.

## Recomendación metodológica

Usar una revisión de alcance reproducible para fundamentar decisiones, guiada por
checklists empíricos de ACM SIGSOFT. No afirmar una revisión sistemática salvo que
se amplíe el protocolo y se adopte formalmente PRISMA/PRISMA-ScR. Congelar las
preguntas antes de escalar el corpus, pilotear anotación con los cuatro integrantes,
separar splits por semilla y hablante, conservar baselines simples y congelar el
test antes de elegir el modelo final.

## Limitaciones y desacuerdos

- No se encontró un reglamento público específico del Plan 2008. Faltan plantilla,
  rúbrica, estilo de citas, fecha exacta y circuito ético; solo la cátedra puede
  resolverlos.
- El informe técnico previo contiene una investigación amplia, pero sus marcadores
  de cita internos no son referencias entregables; deben reemplazarse por URLs/DOI
  y metadatos verificables durante la revisión.
- El calendario usa como horizonte los últimos días de diciembre, pero la fecha
  exacta debe confirmarse el 9 de septiembre.
- La búsqueda fue de alcance, no exhaustiva. Se detuvo cuando las decisiones del
  proceso quedaron respaldadas por regulación primaria, documentación de
  plataforma, normativa y trabajos académicos centrales.

## Registro de afirmaciones y fuentes

| Afirmación | Fuente | Autor/editor | Fecha | URL | Acceso/notas |
|---|---|---|---|---|---|
| La carrera culmina con Proyecto Final Integrador y su perfil incluye proyectos, software e IA | Ingeniería en Informática | UNSTA | vigente en consulta | https://www.unsta.edu.ar/ingenieria/ingenieria-informatica/ | web oficial, consultada 2026-09-02 |
| Existen proyectos finales públicos de la carrera; un ejemplo tiene 103 páginas | Colección Proyecto Final Ingeniería Informática y Metodología de evaluación de carreras universitarias | Repositorio UNSTA | 2013, disponible en 2026 | https://rdi.unsta.edu.ar/collections/6fbdcceb-6920-47f6-935d-7183c5692153 | repositorio oficial, consultado 2026-09-02 |
| Ingeniería argentina exige experiencia significativa de proyecto y diseño integrado | Resolución 1557/2021 y rectificación 1575/2022 | Ministerio de Educación | 2021–2022 | https://servicios.infoleg.gob.ar/infolegInternet/anexos/345000-349999/349970/norma.htm | índice oficial; acceso directo presentó restricción durante consulta |
| Fuentes de audio de llamada requieren permiso reservado | MediaRecorder.AudioSource | Android Developers | actualización 2026 | https://developer.android.com/reference/android/media/MediaRecorder.AudioSource | documentación oficial |
| Una llamada siempre recibe audio; una app captura la llamada solo si es privilegiada | Sharing audio input | Android Developers | actualización 2026 | https://developer.android.com/media/platform/sharing-audio-input | documentación oficial |
| Vishing presenta escasez de datos y desafíos de intervención | Vishing: first survey & roadmap | Triantafyllopoulos et al. | 2025 | https://doi.org/10.1016/j.csl.2025.101802 | artículo revisado por pares |
| Existe investigación reciente de detección en tiempo real con datos sintéticos | Automatically Detecting Voice Phishing | Ampel, Samtani y Chen | 2026 | https://aisel.aisnet.org/misq/vol50/iss2/9/ | MIS Quarterly |
| SIGSOFT ofrece estándares por método empírico | Empirical Standards | ACM SIGSOFT | vigentes en consulta | https://www2.sigsoft.org/EmpiricalStandards/docs/standards | fuente profesional primaria |
| PRISMA 2020 es una guía de reporte para revisiones sistemáticas | PRISMA 2020 | PRISMA Executive | 2020, sitio vigente | https://www.prisma-statement.org/prisma-2020 | no usar como evaluación de calidad por sí sola |
| La ley argentina regula el tratamiento de datos personales | Ley 25.326, texto actualizado | Estado argentino | 2000 y modificaciones | https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion | texto oficial |
| Se debe informar finalidad, consecuencias, destinatarios y responsable | Derechos sobre datos personales | AAIP | vigente en consulta | https://www.argentina.gob.ar/aaip/datospersonales/derechos | guía oficial |
| ISO/IEC 25010:2023 ofrece un modelo de calidad de producto software | ISO/IEC 25010:2023 | ISO/IEC | 2023 | https://www.iso.org/standard/78176.html | resumen oficial; estándar completo de pago |
