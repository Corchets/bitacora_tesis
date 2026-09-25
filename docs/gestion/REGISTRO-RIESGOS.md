# Registro de riesgos

Escala: probabilidad e impacto de 1 (bajo) a 5 (crítico). Revisar semanalmente.

| ID | Riesgo | P | I | Señal temprana | Mitigación | Contingencia | Dueño | Estado |
|---|---|---:|---:|---|---|---|---|---|
| R01 | Pretender capturar llamadas PSTN en Android stock | 5 | 5 | apk requiere permisos privilegiados | motor desacoplado y replay/VoIP controlado | demo sobre streaming controlado | por autoasignar | mitigado por alcance |
| R02 | Entregables interpretados incorrectamente por falta de guía | 3 | 5 | profesor pide formato o etapa no planificada | confirmar por escrito el 9 de septiembre | replanificar sin ampliar núcleo | por autoasignar | abierto |
| R03 | Grabar personas sin protocolo suficiente | 2 | 5 | se invita a grabar antes del aval del tutor, falta una aceptación o aparece un dato real | [método](../datos-etica/METODO-CREACION-CORPUS.md#resguardo-y-consentimiento-del-piloto), consentimiento de ambos, custodio y eliminación definidos; validar con tutor y completar datos de contacto antes de grabar | detener y eliminar la toma; usar audio sintético si no puede garantizarse el protocolo | Mateo / #22 | abierto; protocolo documental no habilita grabaciones |
| R04 | Corpus pequeño o artificial | 4 | 4 | pocas familias/hablantes o diálogos leídos | [catálogo #17](../datos-etica/CATALOGO-ESCENARIOS.csv) y piloto de 14 conversaciones con hasta seis repeticiones dirigidas; fichas semi-estructuradas y seguimiento semanal | revisar pares y profundizar calidad si el piloto no alcanza | equipo / #22 | abierto; diversidad diseñada, todavía no grabada ni evaluada |
| R05 | Leakage entre train y test | 4 | 5 | variantes de una semilla aparecen en splits distintos | agrupar por semilla y hablante; congelar test; spike #29 (2026-09-23) mostró el mecanismo en miniatura (las semillas-espejo tunean y evalúan a la vez) | rehacer splits y resultados | por autoasignar | abierto |
| R06 | ASR falla con español argentino y ruido | 4 | 4 | bajo recall de términos críticos; WER de ficha es FLEURS/MLS leído, no telefonía AR | benchmark temprano con audio piloto; recorte Hub 2026-09-16 usa Moonshine tiny-es y Zipformer Kroko (español de ficha, no llamada AR) | reportar gold vs ASR y usar modelo alternativo del mismo catálogo | por autoasignar | abierto |
| R07 | Falsas alarmas inutilizan el sistema | 4 | 4 | casi toda llamada difícil supera el umbral | negativos comparables del [catálogo #17](../datos-etica/CATALOGO-ESCENARIOS.csv), calibración e histéresis | bajar ambición y priorizar pedidos críticos | equipo / evaluación | abierto; aún sin medición de falsas alarmas |
| R08 | Modelo demasiado pesado para móvil | 3 | 3 | `RTF ≥ 1`, p95 por turno >1,5 s o memoria sobre el techo del perfil | medir contra los [criterios de prefactibilidad](../investigacion/PREFACTIBILIDAD-TECNICA.md): 256/512/1024 MB y 2/4/6 hilos; comparar con TF–IDF | probar un detector más liviano; no afirmar viabilidad Android con mediciones solo en PC | equipo / benchmark #29 | abierto; criterios ratificados, rendimiento no medido |
| R13 | El laboratorio en PC se toma por un teléfono | 3 | 4 | se omite x86 ≠ ARM en el informe | declarar el límite en cada corrida | no generalizar a Pixel/iPhone | por autoasignar | abierto |
| R14 | El aviso por regla crítica infla `Preventive@δ` | 2 | 4 | no se separa `T_A` por incendio vs goteo | spike #29 (2026-09-23) ya emite incendio y goteo por separado; falta aplicarlo a la evaluación sobre corpus | redefinir `T_A` con el tutor | por autoasignar | abierto |
| R09 | Integración ocurre demasiado tarde | 4 | 4 | módulos solo funcionan en notebooks separados | vertical slice en ciclo 2 e integración semanal | replay CLI reproducible como demo base | por autoasignar | abierto |
| R10 | Escritura se posterga | 4 | 4 | resultados sin explicación/versionado | documentar junto a cada decisión/experimento | semana de congelamiento, no de redacción inicial | todos | abierto |
| R11 | Trabajo desigual o conocimiento en silos | 3 | 4 | solo una persona puede ejecutar/explicar un módulo | pareja revisora, rotación y contribuciones con evidencia | reasignar y hacer sesión de transferencia | todos | abierto |
| R12 | La entrega es anterior a fin de diciembre | 3 | 5 | el profesor fija una fecha anticipada | confirmar día el 9 de septiembre y planificar hacia atrás | recortar extensiones inmediatamente | por autoasignar | abierto |
| R15 | `T_A` operativa ≠ definida; umbral insensible en el spike | 3 | 4 | la histéresis dispara con un solo turno alto; el barrido de umbral da idéntico | spike #29 (2026-09-23): dispara con 1 alto + cualquier opinión; umbral 0,3–0,5 idéntico — congelar semántica exacta en D08 antes de medir | redefinir `T_A` con el tutor y re-computar | por autoasignar | abierto |

## Reglas

- P×I igual o mayor a 15 requiere acción en el ciclo actual.
- Un riesgo materializado pasa al seguimiento como bloqueo con fecha y dueño.
- La ausencia de novedad no elimina el riesgo; solo evidencia nueva permite bajar
  probabilidad o impacto.
- Toda ampliación de alcance agrega o actualiza al menos un riesgo.
