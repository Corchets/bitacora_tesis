# Mapa de decisiones

**Destino:** Plan de Trabajo aprobado y ruta sin decisiones críticas abiertas para
ejecutar y evaluar el Proyecto Final de vishing.

Cada decisión debe tener una sola fuente de verdad. Cuando una decisión técnica amerite detalle, se crea un
ADR en `docs/ingenieria/adr/` y desde aquí solo se enlaza su conclusión.

## Frontera: decisiones que pueden tomarse ahora

### D01 — Completar el contrato académico

- **Pregunta:** ¿qué fecha exacta, plantilla, estilo bibliográfico, entregables
  adicionales y proceso ético aplican al grupo?
- **Tipo:** conversación con profesor/tutor.
- **Responsable:** coordinador de la próxima clase.
- **Evidencia:** minuta del 9 de septiembre validada.
- **Desbloquea:** D02, D03, D10 y cronograma definitivo.
- **Estado:** parcialmente resuelto; formato general, grupo y plazo aproximado ya
  fueron informados.

### D02 — Definir problema, usuario y necesidad

- **Pregunta:** ¿quién necesita qué decisión o protección, en qué momento de la
  llamada y frente a qué daño?
- **Tipo:** decisión de alcance con investigación del dominio.
- **Responsable:** por autoasignación en GitHub.
- **Evidencia:** problema en cinco líneas, persona/actor y tres escenarios.
- **Bloqueada por:** D01 solo en su formulación final.
- **Desbloquea:** D03, D04, D06 y requisitos.
- **Estado:** abierto.

### D05 — Elegir la fuente de audio demostrable

- **Pregunta:** ¿cuál será la integración objetivo entre replay en streaming, VoIP
  controlado y micrófono/altavoz de laboratorio?
- **Tipo:** investigación + spike técnico.
- **Responsable:** por autoasignación en GitHub.
- **Evidencia:** prueba mínima, restricciones oficiales, latencia y riesgos.
- **Desbloquea:** arquitectura y requisitos del prototipo.
- **Estado:** abierto; replay es la base recomendada.

### D06 — Definir la gobernanza de datos

- **Pregunta:** ¿qué se grabará, con qué consentimiento, dónde vivirá, quién
  accederá, qué podrá publicarse y cuándo se eliminará?
- **Tipo:** decisión ética con tutor.
- **Responsable:** por autoasignación; validación del tutor.
- **Evidencia:** plan de datos y consentimiento aprobados antes de grabar.
- **Desbloquea:** corpus piloto.
- **Estado:** abierto.

## Decisiones precisas pero bloqueadas

### D03 — Congelar alcance y contribución

- **Pregunta:** ¿cuál es el núcleo obligatorio, cuáles son los stretch goals y qué
  queda fuera de alcance?
- **Bloqueada por:** D01, D02 y D05.
- **Salida:** objetivos, aporte y lista explícita de exclusiones.

### D04 — Aprobar preguntas e hipótesis

- **Pregunta:** ¿qué afirmaciones se evaluarán y qué observación podría refutarlas?
- **Bloqueada por:** D02 y D03.
- **Salida:** PI1–PI2, evaluaciones E1–E2 y tabla pregunta→evidencia.

### D07 — Aprobar taxonomía y evento crítico

- **Pregunta:** ¿qué maniobras y pedidos se anotan, y cómo se marcan `T_R` y `T_C`?
- **Bloqueada por:** D02, D04 y D06.
- **Salida:** manual de anotación v0 probado por los cuatro integrantes.

### D08 — Congelar protocolo experimental

- **Pregunta:** ¿cómo se muestrea, divide y evalúa sin fuga de información?
- **Bloqueada por:** D04 y D07.
- **Salida:** splits, baselines, métricas, seeds, test congelado y amenazas.

### D09 — Elegir ASR y detector

- **Pregunta:** ¿qué combinación satisface la calidad y el presupuesto de cómputo?
- **Bloqueada por:** D05, D07 y benchmark piloto.
- **Salida:** decisión basada en WER/recall crítico, F1/AUPRC, latencia y memoria.

### D10 — Congelar estructura de entrega y defensa

- **Pregunta:** ¿qué índice, anexos, paquete reproducible, duración y demo se
  entregan?
- **Bloqueada por:** D01 y resultados de evaluación.
- **Salida:** checklist final aceptado por el tutor.

## Decisiones cerradas

- **Institución y equipo:** UNSTA, Ingeniería en Informática, Plan 2008; Albarracín
  Ignacio, Antenucci Mateo, Grosso Luciano y Villalobo Evaristo están autorizados
  como grupo de cuatro.
- **Formato base:** entrega digital, A4, carilla simple, portada institucional,
  resúmenes español/inglés, cuerpo técnico y unas 100 páginas como referencia.
- **Horizonte:** entrega hacia fines de diciembre de 2026; falta el día exacto.
- **No basar la tesis en capturar cualquier llamada PSTN desde una app Android
  ordinaria:** la plataforma reserva esas fuentes a componentes privilegiados.
- **Separar motor e integración:** replay en streaming es la base experimental;
  VoIP controlado es la integración preferida si el spike confirma viabilidad.
- **No hacer detección de deepfake en el núcleo:** responde una pregunta distinta
  a detectar manipulación y pedidos peligrosos.
- **Mantener baselines simples:** reglas y TF–IDF son comparadores obligatorios.

## No especificado todavía

- Diseño exacto del warning y método de evaluación con usuarios.
- Modelo de estado temporal que competirá con el acumulador probabilístico.
- Dispositivo Android objetivo y presupuesto máximo de memoria/latencia.
- Posibilidad y licencia de publicación del corpus o solo sus metadatos.
- Técnica estadística final, que depende del tamaño y distribución obtenidos.

## Fuera de alcance provisional

- Captura universal de llamadas PSTN en Android stock.
- iOS, múltiples idiomas, caller-ID reputation, detección de malware y análisis de
  mensajes de texto.
- Detección de voz sintética o identidad biométrica del interlocutor.
- Backend de producción, publicación en Play Store y operación comercial.
- Estudio clínico o generalización poblacional con adultos mayores.

## Regla de uso

En cada seguimiento se puede cerrar una o dos decisiones con evidencia. No se
discute tecnología bloqueada por una decisión anterior. Al cerrar una decisión:

1. registrar fecha, participantes, alternativas y evidencia;
2. escribir conclusión y consecuencias;
3. actualizar bloqueos y promover lo que ya pueda especificarse;
4. cambiar el Plan de Trabajo si altera alcance, tiempo o entregables;
5. pedir validación al tutor si afecta el contrato académico o ético.
