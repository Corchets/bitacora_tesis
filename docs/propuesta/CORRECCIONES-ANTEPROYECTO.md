# Correcciones pendientes al anteproyecto

El [deep research](../../deep-research-report.md) identificó cinco afirmaciones del
anteproyecto que **no se sostienen con la evidencia disponible a 2026**. Están marcadas inline en
[anteproyecto_oficial.md](ANTEPROYECTO.md) como `⚠️[C1]`…`⚠️[C5]`.

Este archivo es la lista de trabajo: se corrigen antes de entregar cualquier versión al director.
Ninguna está corregida todavía.

| # | Estado | Afirmación actual | Por qué es un problema | Redacción propuesta |
|---|---|---|---|---|
| C1 | ☐ | "No hay software vulnerado, hay una conversación." | Demasiado absoluta. Una llamada puede terminar en robo de cuenta, instalación de acceso remoto o compromiso digital. UFECI documenta llamadas para obtener códigos de activación de WhatsApp. | "El vishing explota principalmente decisiones humanas durante una interacción de voz y puede culminar en divulgación de secretos, transferencias o compromiso posterior de cuentas y dispositivos." |
| C2 | ☐ | "Las defensas actuales operan casi exclusivamente antes de la llamada." | Falso en 2026: Google (Pixel) y Samsung (One UI 8.5+) tienen detección durante la llamada. | "Las defensas basadas en reputación del número siguen siendo relevantes, pero recientemente aparecieron sistemas comerciales de análisis de contenido en tiempo real, restringidos a determinados ecosistemas." |
| C3 | ☐ | "Google y Samsung no cubren español." | La evidencia pública no lo sostiene. Google lista México y España para Scam Detection. Lo que sí es verificable es que **Argentina no está en la lista**. | "La disponibilidad depende de dispositivo y región y, en la documentación consultada, Argentina no se encuentra entre los países habilitados por Google." |
| C4 | ☐ | "Los adultos mayores son la población más afectada." | No demostrado para Argentina. En datos de FTC los mayores reportan pérdidas con **menor** frecuencia que grupos jóvenes, aunque el monto por caso es mayor. | "Los adultos mayores constituyen una población de especial interés por la gravedad potencial de las pérdidas y su exposición a determinadas estafas de suplantación." |
| C5 | ☐ | "Clasificar una conversación completa es un problema resuelto." | Demasiado fuerte. VishGPT (MIS Quarterly, 2026) sigue describiendo la detección como desafiante por su naturaleza temporal y la escasez de datos. | "La clasificación offline de llamadas completas tiene antecedentes sólidos, pero la generalización, los datos disponibles y la detección temprana continúan siendo problemas abiertos." |

## Supuestos que el texto da por decididos y no lo están

Distinto de las correcciones: acá no hay nada *falso*, pero el anteproyecto redacta como resuelto
algo que el equipo nunca discutió. Si queda así, esas decisiones se toman solas por inercia.

| # | Estado | Supuesto en el texto | Por qué está abierto |
|---|---|---|---|
| S1 | ☐ | "El prototipo captura la conversación de manera acústica, con la llamada en altavoz" (sec. 8) | Es **una** de cinco opciones de captura, y el deep research recomienda replay como base experimental y VoIP propia como demo. Ver [D05](../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable). |
| S2 | ☐ | "aplicación Android", iOS fuera de alcance (sec. 5 y 8) | La justificación de descartar iOS es correcta, pero que el entregable sea *una app Android* depende de D1. Si el alcance termina siendo replay + VoIP, el entregable puede no ser una app de telefonía. |
| S3 | ☐ | "Se distribuye mediante instalación directa, no por tiendas" (sec. 8) | Razonable, pero es una decisión de producto que nadie tomó. Trivial de confirmar; solo hay que confirmarla. |

Todos estos se resuelven en la misma reunión que D1. No hace falta un ADR por cada uno: uno solo de
alcance puede cubrirlos.

## Además: el título

El anteproyecto dice *"Detección temprana y explicable de vishing mediante análisis incremental de
conversaciones telefónicas en español"*. El informe propone dos alternativas más fuertes, según la
composición real del corpus:

- Sin diversidad geográfica confirmada: *"Detección incremental y explicable de vishing en conversaciones de voz en español mediante procesamiento local y evaluación del margen temporal de intervención"*.
- Con diversidad confirmada: *"Detección incremental y explicable de vishing en español de Argentina: corpus anotado, procesamiento local y evaluación de alerta temprana"*.

Advertencia del informe: **no usar "español rioplatense"** si la mayoría de los participantes son de
Tucumán u otras zonas que no corresponden a esa variedad. "Español de Argentina" es más seguro, y aun
así debe estar respaldado por la composición del corpus.

## Cómo verificar cada corrección

Ninguna de estas correcciones debe darse por buena citando este archivo. Antes de cerrarlas hay que
ir a la fuente primaria (documentación de Google/Samsung, informe UFECI 2024, paper de MIS Quarterly)
y guardar la cita en `referencias.bib` con su DOI o URL y fecha de consulta.
