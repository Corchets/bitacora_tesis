# Registro de riesgos

Escala: probabilidad e impacto de 1 (bajo) a 5 (crítico). Revisar semanalmente.

| ID | Riesgo | P | I | Señal temprana | Mitigación | Contingencia | Dueño | Estado |
|---|---|---:|---:|---|---|---|---|---|
| R01 | Pretender capturar llamadas PSTN en Android stock | 5 | 5 | spike requiere permisos privilegiados | motor desacoplado y replay/VoIP controlado | demo sobre streaming controlado | por autoasignar | mitigado por alcance |
| R02 | Entregables interpretados incorrectamente por falta de guía | 3 | 5 | profesor pide formato o etapa no planificada | confirmar por escrito el 9 de septiembre | replanificar sin ampliar núcleo | por autoasignar | abierto |
| R03 | Grabar personas sin protocolo suficiente | 2 | 5 | consentimiento o retención indefinidos | plan de datos + aval del tutor antes de grabar | usar audios sintéticos/piloto técnico sin participantes | por autoasignar | abierto |
| R04 | Corpus pequeño o artificial | 4 | 4 | pocas familias/hablantes o diálogos leídos | [catálogo #17](../datos-etica/CATALOGO-ESCENARIOS.csv) con 9 modalidades y 8 negativos revisados; fichas semi-estructuradas y seguimiento semanal | seleccionar menos familias y profundizar calidad si el piloto no alcanza | equipo / #22 | abierto; diversidad diseñada, todavía no grabada ni evaluada |
| R05 | Leakage entre train y test | 4 | 5 | variantes de una semilla aparecen en splits distintos | agrupar por semilla y hablante; congelar test | rehacer splits y resultados | por autoasignar | abierto |
| R06 | ASR falla con español argentino y ruido | 4 | 4 | bajo recall de términos críticos; WER de ficha es FLEURS/MLS leído, no telefonía AR | benchmark temprano con audio piloto; recorte Hub 2026-09-16 usa Moonshine tiny-es y Zipformer Kroko (español de ficha, no llamada AR) | reportar gold vs ASR y usar modelo alternativo del mismo catálogo | por autoasignar | abierto |
| R07 | Falsas alarmas inutilizan el sistema | 4 | 4 | casi toda llamada difícil supera el umbral | negativos comparables del [catálogo #17](../datos-etica/CATALOGO-ESCENARIOS.csv), calibración e histéresis | bajar ambición y priorizar pedidos críticos | equipo / evaluación | abierto; aún sin medición de falsas alarmas |
| R08 | Modelo demasiado pesado para móvil | 3 | 3 | `RTF ≥ 1`, p95 por turno >1,5 s o memoria sobre el techo del perfil | medir contra los [criterios de prefactibilidad](../investigacion/PREFACTIBILIDAD-TECNICA.md): 256/512/1024 MB y 2/4/6 hilos; comparar con TF–IDF | probar un detector más liviano; no afirmar viabilidad Android con mediciones solo en PC | equipo / benchmark #29 | abierto; criterios ratificados, rendimiento no medido |
| R13 | El laboratorio en PC se toma por un teléfono | 3 | 4 | se omite x86 ≠ ARM en el informe | declarar el límite en cada corrida | no generalizar a Pixel/iPhone | por autoasignar | abierto |
| R14 | El aviso por regla crítica infla `Preventive@δ` | 3 | 4 | no se separa `T_A` por incendio vs goteo | reportar las dos fuentes de alerta por separado | redefinir `T_A` con el tutor | por autoasignar | abierto |
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
