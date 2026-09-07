# Plan de Trabajo v1

## Portada provisional

**Universidad del Norte Santo Tomás de Aquino**  
**Facultad de Ingeniería**  
**Ingeniería en Informática — Plan 2008**  
**Proyecto Final Integrador**

### Detección incremental y explicable de vishing en conversaciones de voz en español

**Integrantes**

- Albarracín Ignacio.
- Antenucci Mateo.
- Grosso Luciano.
- Villalobo Evaristo.

**Tutor:** pendiente de confirmación  
**Año:** 2026

> La versión final debe incorporar el logo oficial de UNSTA y respetar la plantilla
> o reglas tipográficas que confirme el profesor.

## 1. Resumen de la propuesta

El vishing es una modalidad de ingeniería social realizada mediante llamadas de voz en la que un atacante intenta obtener información sensible, inducir una transferencia o provocar otra acción riesgosa. Las defensas basadas únicamente en la reputación del número no pueden reconocer necesariamente llamadas originadas desde números todavía no reportados ni explicar la maniobra que ocurre durante la
conversación.

El proyecto propone diseñar, implementar y evaluar un prototipo que procese incrementalmente un flujo de audio en español, transcriba localmente la conversación, estime el riesgo de vishing e identifique señales como suplantación, urgencia, aislamiento y pedidos de códigos, secretos o transferencias. Cuando el riesgo supere una política definida, el sistema mostrará una advertencia contextual y accionable.

La evaluación se realizará sobre un corpus controlado de conversaciones simuladas
de vishing y llamadas legítimas difíciles. Se compararán reglas, un modelo clásico
y, si aporta una mejora justificable, un modelo neuronal liviano. Además de las
métricas de clasificación, se medirá la falsa alarma, el efecto de los errores del
reconocimiento de voz, la latencia y el tiempo de anticipación respecto de una
acción crítica. El núcleo experimental utilizará reproducción en streaming; se
evaluará una llamada VoIP controlada como integración y una prueba con altavoz como
demostración de laboratorio.

## 2. Problema

Durante una llamada de vishing, la víctima debe decidir bajo presión y con escaso
tiempo para verificar la identidad del interlocutor. Un número puede parecer normal
y el peligro solo hacerse visible en el contenido y la evolución de la conversación.
El problema de ingeniería es detectar evidencia suficiente de manipulación y de una
solicitud riesgosa mientras la llamada todavía está en curso, con una tasa de falsa
alarma aceptable y una advertencia que permita actuar antes de compartir información
o realizar una operación.

## 3. Objetivo general

Diseñar, implementar y evaluar un prototipo capaz de analizar incrementalmente un
flujo de audio de una conversación de voz en español, mediante inferencia local,
para estimar el riesgo de vishing, identificar maniobras de ingeniería social y
emitir una advertencia contextual antes de una acción crítica, cuantificando su
desempeño, falsas alarmas, latencia y margen temporal de intervención.

## 4. Objetivos específicos

1. Relevar el estado del arte, las modalidades relevantes de vishing y las
   restricciones técnicas, éticas y legales del problema.
2. Definir una taxonomía operacional de maniobras y solicitudes riesgosas.
3. Construir un corpus controlado y documentado de conversaciones simuladas de
   vishing y llamadas legítimas en español.
4. Comparar alternativas de reconocimiento de voz local sobre audio representativo.
5. Implementar baselines de reglas y aprendizaje automático clásico.
6. Desarrollar un detector incremental que acumule evidencia a lo largo del tiempo.
7. Diseñar advertencias explicables derivadas de las señales detectadas.
8. Integrar la cadena audio→ASR→detección→advertencia en un entorno controlado.
9. Evaluar clasificación, falsas alarmas, robustez al ASR, anticipación, latencia y
   consumo de recursos.
10. Documentar arquitectura, decisiones, implementación, pruebas, resultados,
    limitaciones y oportunidades de trabajo futuro.

## 5. Preguntas de investigación

- **PI1:** ¿con qué desempeño puede detectarse vishing usando solo la parte de la
  conversación disponible hasta un instante dado?
- **PI2:** ¿con cuánto margen respecto del primer pedido riesgoso y de la primera
  acción de cumplimiento puede emitirse una alerta estable?

Como evaluación diagnóstica se comparará el detector con transcripción manual y
ASR local. La explicación de maniobras será un objetivo secundario. No se presentan
como preguntas centrales independientes.

Las definiciones operativas y métricas están en
[PREGUNTAS-DE-INVESTIGACION.md](../investigacion/PREGUNTAS-DE-INVESTIGACION.md).

## 6. Alcance

### Núcleo obligatorio

- Español, priorizando variedad argentina sin afirmar representatividad nacional.
- Corpus de llamadas simuladas/representadas y llamadas legítimas difíciles.
- Transcripción local.
- Detección semántica y conversacional incremental.
- Maniobras de ingeniería social y solicitudes de alto riesgo.
- Evento crítico y medición de anticipación.
- Advertencia explicable.
- Reproducción de audio como streaming reproducible.
- Prototipo o demo en entorno controlado.

### Extensiones condicionadas al avance

- Llamada VoIP integrada en la aplicación.
- Cuantización avanzada y comparación de dispositivos.
- Features prosódicas.
- Prueba de comprensión de warnings con voluntarios.
- Evaluación adversarial o fuera de distribución.

### Fuera de alcance

- Captura universal de llamadas PSTN desde una app Android ordinaria.
- Identificación biométrica o detección de voces clonadas/deepfake.
- Reputación de números y detección de spoofing.
- iOS, múltiples idiomas, SMS, WhatsApp y malware.
- Backend de producción o publicación comercial en Play Store.
- Estudio poblacional representativo con víctimas reales.

## 7. Alternativas para obtener el audio

Se presentarán al profesor cuatro alternativas comparadas:

1. reproducción de grabaciones como stream;
2. llamada en altavoz capturada por un micrófono externo;
3. llamada VoIP controlada cuyo audio pertenece a la aplicación;
4. integración privilegiada con telefonía mediante OEM/AOSP/root.

La recomendación es aprobar **replay como base experimental**, altavoz externo como
demo temprana y VoIP como integración objetivo. La comparación completa está en
[ALTERNATIVAS-CAPTURA-AUDIO.md](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md).

## 8. Metodología

### Etapa 1 — Definición y revisión

- Cerrar problema, interesados, alcance y preguntas.
- Ejecutar una revisión bibliográfica reproducible.
- Consolidar requisitos funcionales, no funcionales y éticos.

### Etapa 2 — Factibilidad técnica

- Probar audio→ASR local→regla→alerta.
- Medir latencia básica y documentar restricciones de plataforma.
- Elegir las interfaces entre audio, ASR, detector y UI.

### Etapa 3 — Corpus y anotación

- Definir escenarios, guiones semi-estructurados y hard negatives.
- Aprobar consentimiento, almacenamiento, acceso y retención.
- Grabar un piloto, transcribir y anotar por más de un integrante.
- Ajustar manual y medir acuerdo antes de escalar.

### Etapa 4 — Modelos y estado temporal

- Implementar reglas y TF–IDF/regresión logística.
- Evaluar un modelo neuronal liviano solo si existe evidencia para hacerlo.
- Comparar predicción por turno con acumulación temporal e histéresis.

### Etapa 5 — Integración

- Construir el pipeline end-to-end.
- Mostrar riesgo, evidencia y acción recomendada.
- Instrumentar tiempos, memoria, errores y versiones.

### Etapa 6 — Evaluación

- Congelar test antes del ajuste final.
- Evaluar transcripción manual frente a ASR.
- Medir precisión, recall, F1/AUPRC, llamadas con falsa alarma, falsas alertas por
  hora, anticipación, latencia p50/p95 y consumo de recursos.
- Analizar casos de error y amenazas a la validez.

### Etapa 7 — Documentación y defensa

- Mantener el informe durante todo el proyecto.
- Reproducir tablas y figuras desde configuraciones versionadas.
- Preparar PDF, anexos, código, demo y video de respaldo.

## 9. Arquitectura conceptual

```text
Fuente de audio permitida
          ↓
VAD / segmentación / ventanas
          ↓
ASR local con texto parcial y timestamps
          ↓
Estado de conversación
          ↓
Detector de riesgo + etiquetas explicativas
          ↓
Acumulador temporal / umbral / histéresis
          ↓
Advertencia: qué ocurre + por qué importa + qué hacer
```

La interfaz se diseñará de forma independiente de Android para poder entrenar y
evaluar en computadora y desplegar el modelo seleccionado después.

## 10. Entregables

- Plan de Trabajo aprobado.
- Revisión y matriz bibliográfica.
- Requisitos y arquitectura.
- Plan de datos, consentimiento, esquema y manual de anotación.
- Corpus controlado y sus manifiestos autorizados.
- Baselines y detector incremental.
- Pipeline local e integración/demostración.
- Suite de pruebas.
- Protocolo experimental, resultados y análisis de errores.
- Informe Final digital, resúmenes español/inglés y anexos.
- Presentación, demo y respaldo audiovisual.

## 11. Cronograma

| Fechas       | Resultado principal                                                  |
| ------------ | -------------------------------------------------------------------- |
| 2–9 sep      | propuesta, preguntas, alternativas de audio y decisiones al profesor |
| 10–23 sep    | alcance aprobado y vertical slice técnico                            |
| 24 sep–7 oct | corpus/anotación piloto y protocolo ético                            |
| 8–21 oct     | benchmark ASR, reglas, TF–IDF y primer resultado temporal            |
| 22 oct–4 nov | corpus v1 y detector incremental                                     |
| 5–18 nov     | integración end-to-end e instrumentación                             |
| 19 nov–2 dic | congelamiento y evaluación final                                     |
| 3–16 dic     | informe completo, defensa y reproducción                             |
| 17–fin dic   | correcciones, PDF y entrega                                          |

## 12. Organización del equipo

El trabajo se organiza en cuatro líneas: investigación/datos/ética, ML/evaluación,
audio/ASR y producto/integración. Las tareas se publican como GitHub Issues y cada
integrante se autoasigna según capacidad. Todo issue tiene una persona responsable
y una revisora distinta cuando afecta datos, métricas, arquitectura o el informe.

Todo el equipo participa del piloto de anotación, integración, revisión del informe
y ensayo de defensa. La contribución se hace visible mediante issues, commits y
revisiones, sin imponer áreas permanentes por nombre.

## 13. Riesgos principales

- Captura PSTN no disponible para apps ordinarias.
- Corpus poco realista o insuficiente.
- Fuga de información entre entrenamiento y test.
- ASR deficiente con español argentino y ruido.
- Falsas alarmas excesivas.
- Integración o escritura tardías.
- Modelo demasiado pesado para el dispositivo.
- Tratamiento inadecuado de voces/transcripciones.

Las mitigaciones están en [REGISTRO-RIESGOS.md](../gestion/REGISTRO-RIESGOS.md).

La propuesta concreta de reclutamiento y escala está en
[PLAN-PARTICIPANTES-Y-CORPUS.md](../datos-etica/PLAN-PARTICIPANTES-Y-CORPUS.md).

## 14. Criterio de éxito

El proyecto será exitoso si responde las preguntas con un procedimiento honesto y reproducible, entrega un pipeline demostrable y documenta sus límites. No se fija una accuracy arbitraria como condición. Un resultado que muestre baja anticipación, degradación por ASR o superioridad de un baseline simple sigue siendo un resultado válido si el experimento está bien diseñado.

## 15. Decisiones solicitadas al profesor el 9 de septiembre

1. ¿Aprueba PI1 y PI2 como preguntas centrales, la comparación manual-vs-ASR como
   evaluación diagnóstica y la explicación como objetivo secundario?
2. ¿Aprueba replay como base experimental, altavoz externo como demo inicial y
   VoIP controlado como integración objetivo?
3. ¿Aprueba el alcance fuera de PSTN universal, deepfake e identificación de voz?
4. ¿Qué aprobación requiere antes de grabar voces de voluntarios?
5. ¿Qué plantilla, estilo bibliográfico, entregables y fecha exacta debemos usar?

## 16. Aprobaciones y cambios

| Fecha      | Versión | Decisión del profesor/tutor | Cambio requerido | Responsable     |
| ---------- | ------- | --------------------------- | ---------------- | --------------- |
| 2026-09-09 | 1.0     | pendiente                   | pendiente        | por autoasignar |
