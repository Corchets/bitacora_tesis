# Registro de riesgos

Escala: probabilidad e impacto de 1 (bajo) a 5 (crítico). Revisar semanalmente.

| ID | Riesgo | P | I | Señal temprana | Mitigación | Contingencia | Dueño | Estado |
|---|---|---:|---:|---|---|---|---|---|
| R01 | Pretender capturar llamadas PSTN en Android stock | 5 | 5 | spike requiere permisos privilegiados | motor desacoplado y replay/VoIP controlado | demo sobre streaming controlado | por autoasignar | mitigado por alcance |
| R02 | Entregables interpretados incorrectamente por falta de guía | 3 | 5 | profesor pide formato o etapa no planificada | confirmar por escrito el 9 de septiembre | replanificar sin ampliar núcleo | por autoasignar | abierto |
| R03 | Grabar personas sin protocolo suficiente | 2 | 5 | consentimiento o retención indefinidos | plan de datos + aval del tutor antes de grabar | usar audios sintéticos/piloto técnico sin participantes | por autoasignar | abierto |
| R04 | Corpus pequeño o artificial | 4 | 4 | pocas familias/hablantes o diálogos leídos | guiones semi-estructurados, hard negatives y seguimiento semanal | reducir familias y profundizar calidad | por autoasignar | abierto |
| R05 | Leakage entre train y test | 4 | 5 | variantes de una semilla aparecen en splits distintos | agrupar por semilla y hablante; congelar test | rehacer splits y resultados | por autoasignar | abierto |
| R06 | ASR falla con español argentino y ruido | 4 | 4 | bajo recall de términos críticos | benchmark temprano con audio piloto | reportar gold vs ASR y usar modelo alternativo | por autoasignar | abierto |
| R07 | Falsas alarmas inutilizan el sistema | 4 | 4 | casi toda llamada difícil supera el umbral | hard negatives, calibración e histéresis | bajar ambición y priorizar pedidos críticos | por autoasignar | abierto |
| R08 | Modelo demasiado pesado para móvil | 3 | 3 | real-time factor >1 o memoria excesiva | baseline liviano, ONNX/cuantización después de validar | ejecutar detector clásico en dispositivo | por autoasignar | abierto |
| R09 | Integración ocurre demasiado tarde | 4 | 4 | módulos solo funcionan en notebooks separados | vertical slice en ciclo 2 e integración semanal | replay CLI reproducible como demo base | por autoasignar | abierto |
| R10 | Escritura se posterga | 4 | 4 | resultados sin explicación/versionado | documentar junto a cada decisión/experimento | semana de congelamiento, no de redacción inicial | todos | abierto |
| R11 | Trabajo desigual o conocimiento en silos | 3 | 4 | solo una persona puede ejecutar/explicar un módulo | pareja revisora, rotación y contribuciones con evidencia | reasignar y hacer sesión de transferencia | todos | abierto |
| R12 | La entrega es anterior a fin de diciembre | 3 | 5 | el profesor fija una fecha anticipada | confirmar día el 9 de septiembre y planificar hacia atrás | recortar extensiones inmediatamente | por autoasignar | abierto |

## Reglas

- P×I igual o mayor a 15 requiere acción en el ciclo actual.
- Un riesgo materializado pasa al seguimiento como bloqueo con fecha y dueño.
- La ausencia de novedad no elimina el riesgo; solo evidencia nueva permite bajar
  probabilidad o impacto.
- Toda ampliación de alcance agrega o actualiza al menos un riesgo.
