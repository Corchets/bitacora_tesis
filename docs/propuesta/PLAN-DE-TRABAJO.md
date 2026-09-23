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

**Tutor:** Ing. Ernesto Rico  
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

### Formulación en cinco líneas

> **Estado: propuesta sin discutir.** Borrador del [issue #18](https://github.com/Corchets/bitacora_tesis/issues/18);
> cierra [D02](../gestion/MAPA-DECISIONES.md#d02--definir-problema-usuario-y-necesidad)
> cuando lo validen los cuatro integrantes.

1. **Usuario:** una persona en Argentina que atiende en su teléfono a alguien que dice llamar de su
   banco, de un organismo como ANSES, de una mesa de soporte o de parte de un familiar.
2. **Contexto:** el número no delata nada; el engaño se ve solo en lo que se dice: autoridad,
   urgencia, pedido de secreto y, en algún momento, un pedido concreto.
3. **Decisión bajo presión:** en pocos minutos y sin poder verificar al interlocutor, tiene que
   decidir si dicta un código o una clave, transfiere dinero o comparte la pantalla.
4. **Daño evitado:** que esa acción ocurra, y con ella la toma de la cuenta o la pérdida de dinero.
   Por eso la advertencia sirve solo si llega antes de que la persona cumpla el pedido, no después.
5. **Límite de las defensas existentes:** la reputación del número no ve la conversación; el detector
   conversacional de Google es cerrado y, al 2026-09-17, no está disponible en Argentina; las
   recomendaciones de BCRA y ANSES dependen de que la persona las recuerde en el momento de presión.

**Respaldo de cada línea:**

- Líneas 1 a 3: las modalidades salen de las fuentes del
  [catálogo de escenarios](../datos-etica/CATALOGO-ESCENARIOS.csv) (issue
  [#17](https://github.com/Corchets/bitacora_tesis/issues/17), con las fuentes incorporadas en el
  PR [#31](https://github.com/Corchets/bitacora_tesis/pull/31), pendiente de revisión): BCRA, ANSES, UFECRI-MPF, Ministerio
  de Seguridad y Banco Galicia, consultadas el 2026-09-17. Tres escenarios que ilustran el problema:
  `SC-BANK-OTP-01` (código de verificación), `SC-ORG-BENEFICIO-01` (beneficio inexistente) y
  `SC-FAMILIAR-DINERO-01` (familiar que pide dinero).
- Línea 4: el "antes" es lo que mide PI2; ver `T_R` y `T_C` en
  [METRICAS.md](../evaluacion/METRICAS.md).
- Línea 5: disponibilidad de Google en
  [lecturas/2026-google-scam-detection.md §6](../investigacion/lecturas/2026-google-scam-detection.md)
  (consulta 2026-09-17). Que las recomendaciones dependan de la memoria de la persona es un argumento
  del equipo, no una afirmación con fuente.

**Beneficiario y foco en adultos mayores:** queda abierto en
[D12](../gestion/MAPA-DECISIONES.md#d12--encuadre-del-foco-en-adultos-mayores). La formulación no
restringe el usuario por edad. Si el foco se mantiene, se justifica por la gravedad potencial de las
pérdidas y la exposición a estafas de suplantación, no por "son los más afectados". UFECRI-MPF
documenta la suplantación de familiares dirigida "generalmente" a personas mayores, lo que sostiene
una modalidad, no una prevalencia.

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

**Fechas de referencia.** La defensa es presencial a fines de diciembre de 2026 y el
día exacto sigue pendiente, según la [minuta del 9 de septiembre](../gestion/seguimientos/2026-09-09.md).
El equipo fija además el **1 de diciembre** como cierre interno de informe, código,
resultados y presentación. No es una exigencia de la cátedra: es el margen que se
reserva para las correcciones del tutor y el ensayo de la defensa.

| Fechas | Resultado principal |
|---|---|
| 2–9 sep | propuesta, preguntas, alternativas de audio y decisiones al profesor |
| 10–21 sep | alcance aprobado y vertical slice técnico audio→ASR→regla→alerta |
| 22 sep–5 oct | corpus/anotación piloto, protocolo ético y marco teórico en borrador |
| 6–19 oct | benchmark ASR, reglas, TF–IDF y primer resultado temporal |
| 20 oct–2 nov | corpus v1 y detector incremental |
| 3–9 nov | integración end-to-end e instrumentación |
| 10–23 nov | congelamiento, test congelado y evaluación final |
| 24–30 nov | informe completo, presentación y reproducción de tablas y figuras |
| **1 dic** | **cierre interno: informe, código, resultados y presentación terminados** |
| 2 dic en adelante | ventana de defensa; solo correcciones pedidas por el tutor |

> **Estado: propuesta sin discutir por los cuatro integrantes.** El reparto de
> semanas es una construcción del equipo, a ratificar en la próxima reunión y con el
> tutor.

Este calendario comprime en doce semanas el trabajo que la versión anterior
distribuía en dieciséis. El recorte no es parejo y sigue una regla fija: **si la
fecha se adelanta se recortan extensiones y no se comprime la evaluación final.**

- **Se preservan dos semanas completas de congelamiento y evaluación** (10–23 nov).
  Es el bloque que sostiene la credibilidad de los resultados y el único que no se
  toca.
- **Integración baja de dos semanas a una** (3–9 nov). Lo hace viable el vertical
  slice de septiembre: en noviembre se conecta un pipeline que ya funciona por
  partes, no se construye de cero.
- **Informe baja de dos semanas a una** (24–30 nov). Lo hace viable escribir desde
  octubre en paralelo al desarrollo, como ya pide la etapa 7 de la
  [metodología](#8-metodología). Si en noviembre el marco teórico todavía está en
  blanco, esta semana no alcanza.
- **Desaparece el ciclo de correcciones de fin de diciembre.** Su función la cumple
  la ventana de defensa, que deja de ser tiempo de producción.

El margen desapareció, y conviene decirlo ahora y no en noviembre: cualquier atraso
se paga con las [extensiones condicionadas al avance](#6-alcance) —VoIP integrada,
cuantización, features prosódicas, prueba de warnings con voluntarios, evaluación
adversarial—, que son la primera reserva a sacrificar y no un compromiso. El núcleo
obligatorio no se toca. Si un atraso llega a comprometerlo, la conversación que
corresponde es con el tutor, no un recorte silencioso de la evaluación.

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

La propuesta de diseño del corpus está en
[METODO-CREACION-CORPUS.md](../datos-etica/METODO-CREACION-CORPUS.md).

## 14. Criterio de éxito

El proyecto será exitoso si responde las preguntas con un procedimiento honesto y reproducible, entrega un pipeline demostrable y documenta sus límites. No se fija una accuracy arbitraria como condición. Un resultado que muestre baja anticipación, degradación por ASR o superioridad de un baseline simple sigue siendo un resultado válido si el experimento está bien diseñado.

## 15. Decisiones resueltas con el profesor el 9 de septiembre

1. **Preguntas centrales:** Aprobadas PI1 y PI2 como preguntas principales; comparación manual vs. ASR como diagnóstica y explicación como objetivo secundario.
2. **Fuente de audio:** Aprobada la estrategia escalonada: replay de grabaciones como base experimental reproducible y VoIP controlada como integración prototipo. Altavoz despriorizado.
3. **Límites de alcance:** Aprobado dejar fuera PSTN universal, deepfake y biometría de voz.
4. **Procedimiento ético y privacidad:** UNSTA no requiere comité de ética formal. El corpus se compone de simulaciones con datos ficticios y sin víctimas reales; la privacidad se garantiza por diseño en el dispositivo (*on-device*).
5. **Requisitos académicos:** Defensa presencial última/penúltima semana de diciembre 2026. Tutor asignado: Ing. Ernesto Rico. Entrega digital promedio ~100 págs (ver [REQUISITOS-ACADEMICOS.md](REQUISITOS-ACADEMICOS.md)).

## 16. Aprobaciones y cambios

| Fecha      | Versión | Decisión del profesor/tutor | Cambio requerido | Responsable |
| ---------- | ------- | --------------------------- | ---------------- | ----------- |
| 2026-09-09 | 1.0     | Dirección y alcance aprobados sin observaciones críticas. Sugirió investigar ventana de contexto, prefactibilidad, baselines, tipos de manipulación policial y estrategia de modelos. | Actualizar requisitos académicos, mapa de decisiones y avanzar a factibilidad técnica (Ciclo 1). | Equipo |
