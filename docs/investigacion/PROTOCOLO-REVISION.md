# Protocolo de revisión bibliográfica

**Versión:** 0.1  
**Tipo propuesto:** revisión de alcance reproducible, no revisión sistemática plena  
**Propósito:** fundamentar decisiones del Proyecto Final y establecer el vacío que
responden sus preguntas de investigación.

## Preguntas de la revisión

1. ¿Qué señales lingüísticas, conversacionales, acústicas o contextuales se han
   usado para detectar vishing?
2. ¿Qué trabajos detectan durante la conversación y cómo miden la detección
   temprana o el momento de intervención?
3. ¿Qué datasets existen y cuáles son sus idiomas, orígenes, unidades de anotación,
   licencias y amenazas de leakage/sesgo?
4. ¿Qué métodos de ASR local en español e inferencia móvil son viables bajo las
   restricciones del prototipo?
5. ¿Cómo se diseñan y evalúan advertencias de seguridad durante interacciones bajo
   presión?
6. ¿Qué restricciones legales, éticas y de plataforma afectan la captura y el
   procesamiento de conversaciones en Argentina y Android?

## Fuentes

### Académicas

- IEEE Xplore, ACM Digital Library, Scopus o Web of Science si la UNSTA tiene acceso.
- Google Scholar para descubrimiento y seguimiento de citas, no como único índice.
- Crossref/DOI y sitio del editor para verificar metadatos.
- arXiv/OpenReview solo cuando no exista versión revisada; etiquetar preprints.

### Primarias no académicas

- UNSTA, su repositorio institucional y normativa nacional para requisitos
  institucionales y legales.
- Android Developers para capacidades de plataforma.
- Documentación de los proyectos/modelos para versiones, licencias y despliegue.
- Organismos argentinos para patrones de fraude y recomendaciones públicas.

## Cadenas iniciales

Adaptar sintaxis por base y guardar literalmente cada consulta ejecutada.

```text
(vishing OR "voice phishing" OR "phone scam" OR "scam call")
AND (detect* OR classif* OR intervention OR warning)

(vishing OR "voice phishing" OR "scam call")
AND ("real time" OR realtime OR incremental OR early OR prefix OR streaming)

(vishing OR "voice phishing")
AND (dataset OR corpus OR annotation OR transcript)

(security warning OR risk warning)
AND (voice call OR phone OR conversational)
AND (usability OR comprehension OR intervention)

(Spanish OR español OR Argentina OR Latin America)
AND (vishing OR "voice phishing" OR "phone scam")
```

## Inclusión

- Estudio primario, survey relevante o documentación oficial.
- Explica método, datos o restricciones suficientes para extraer evidencia.
- Relación directa con al menos una pregunta de revisión.
- Para estado del arte técnico: preferencia 2019–2026; trabajos anteriores se
  incluyen si son fundacionales.
- Idioma español o inglés.

## Exclusión

- Phishing escrito sin una transferencia clara al canal de voz.
- Detección exclusiva de caller-ID/spoofing o deepfake si no informa el detector
  semántico/conversacional.
- Artículo duplicado, resumen sin texto verificable o fuente comercial sin método.
- Métricas sin descripción del dataset o split.
- Fuente secundaria que solo repite una afirmación accesible en la fuente primaria.

## Selección y control de calidad

1. Registrar búsqueda, fecha, base, cadena, filtros y cantidad de resultados.
2. Deduplicar por DOI/título.
3. Cribado de título/resumen por una persona; revisar exclusiones dudosas en pareja.
4. Texto completo y motivo de exclusión explícito.
5. Extraer evidencia en `matriz-literatura.csv`.
6. Hacer snowballing hacia atrás y adelante sobre los trabajos centrales.
7. Detener cuando cada afirmación material tenga respaldo primario, las
   contradicciones estén acotadas y otra búsqueda no cambie decisiones.

Evaluar, como mínimo:

- correspondencia entre población/datos y la afirmación;
- origen y licencia del dataset;
- independencia de train/validation/test;
- baselines y métricas apropiadas;
- medición real de tiempo/latencia si se afirma “real time”;
- código/datos disponibles y versión;
- limitaciones y conflictos de interés.

Los [estándares empíricos de ACM SIGSOFT](https://www2.sigsoft.org/EmpiricalStandards/docs/standards)
se usarán como checklist metodológico. Si el tutor exige declarar una revisión
sistemática o scoping review formal, se amplía este protocolo y se utiliza la guía
[PRISMA 2020](https://www.prisma-statement.org/prisma-2020) o PRISMA-ScR según
corresponda; PRISMA guía el reporte y no reemplaza la evaluación de calidad.

## Familias de evidencia

Cada familia se crea como issue de investigación y se toma por autoasignación. La
persona revisora debe ser distinta cuando la síntesis afecte el método o alcance.

| Familia | Revisión requerida | Salida |
|---|---|---|
| Requisitos académicos y proceso UNSTA | otra persona del equipo | checklist del Plan de Trabajo |
| Dominio, escenarios argentinos y ética | revisión cruzada de datos/evaluación | taxonomía de escenarios y plan de datos |
| Datasets y anotación | revisión cruzada de datos/evaluación | tabla comparativa + manual v0 |
| Detectores y modelado temporal | revisión cruzada de ML/datos | tabla de métodos/baselines |
| ASR local y restricciones Android | revisión cruzada de audio/integración | benchmark y ADR de audio |
| Intervención, warning y evaluación UX | revisión cruzada de UX/ética | requisitos de warning y prueba formativa |

Una afirmación crítica requiere revisión cruzada y fuente accesible. La cantidad de
papers no es una métrica de avance.

## Fuentes semilla verificadas

- [Ingeniería en Informática — UNSTA](https://www.unsta.edu.ar/ingenieria/ingenieria-informatica/)
- [Proyectos finales de Ingeniería Informática — repositorio UNSTA](https://rdi.unsta.edu.ar/collections/6fbdcceb-6920-47f6-935d-7183c5692153)
- [Triantafyllopoulos et al., 2025 — survey de vishing](https://doi.org/10.1016/j.csl.2025.101802)
- [Ampel, Samtani y Chen, 2026 — VishGPT](https://aisel.aisnet.org/misq/vol50/iss2/9/)
- [An analysis of scam-baiting calls](https://arxiv.org/abs/2307.01965)
- [ACM SIGSOFT Empirical Standards](https://www2.sigsoft.org/EmpiricalStandards/)
- [Android: compartir entrada de audio](https://developer.android.com/media/platform/sharing-audio-input)
- [Gobierno argentino: qué es el vishing](https://www.argentina.gob.ar/justicia/convosenlaweb/situaciones/que-hago-si-me-piden-datos-personales-por-telefono)
- [Ley argentina 25.326, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion)

## Registro de búsquedas

| Fecha | Base | Cadena/filtros | Resultados | Seleccionados | Responsable | Notas |
|---|---|---|---:|---:|---|---|
| | | | | | | |
