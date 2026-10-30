# Demo de detección de vishing

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

HTML/CSS/JavaScript sin dependencias ni build, `// @ts-check` y JSDoc. Python sirve el panel y WebSockets. Fuentes del sistema, sin CDN ni recursos de internet; ASR y detector locales.

## Users

Quien presenta opera la llamada desde una notebook con auriculares. El público (tutor y tribunal) sigue la pantalla proyectada desde el fondo del aula. El profesor prueba después sus propias llamadas y el ASR.

## Product Purpose

Hacer observable la detección incremental: quién habla, qué se transcribe ahora y qué decide el detector con cada frase, sin explicación previa. Es una herramienta de demo del spike, no una elección del sistema final.

## Operating Context

Demo prevista para el 2026-10-28. Fuentes existentes: ejemplos SC-WA-CODE-01, SC-SOPORTE-CLAVE-01 y LG-SUPPORT-INFO-01 (LG-WA-CONSULTA-01 salió del panel el 2026-10-28), micrófono, Meet en Chrome, WhatsApp Desktop mediante BlackHole y segunda notebook con cliente.py. El servidor guarda las llamadas fuera de Git.

## Capabilities and Constraints

- Nombres exactos: «Persona protegida» y «Otra persona»; con aviso, «Otra persona · posible estafa». No inferir que toda llamada es fraudulenta.
- Conversación: otra persona a la izquierda, protegida a la derecha. Evaluación junto a la frase que la disparó, con riesgo, sí/no, demora y salteadas. Línea de riesgo en el tiempo y momento del aviso.
- Detector fijo al arrancar el servidor: mostrar nombre y modelo, sin selector.
- Conservar fuentes, iniciar, terminar, nueva llamada, validaciones y errores. «Probar el ASR» es un modo aparte, solo micrófono y sin detector.
- Corte de silencio elegible en llamada (inicial 0,9 s) y en prueba ASR (inicial 0,8 s). Umbral RMS de silencio fijo en 0,003 en llamada; elegible en prueba ASR, inicial 0,008 (medido con voz real, `asr-local/PLAN-VOZ-REAL.md` §11).
- Aviso en franja visible y breve, nunca modal, con motivo, cita, frase culpable resaltada, tono corto desactivable y botón para cerrarla.
- Vista `?vista=protegida` simple y existente, sin rediseñar.
- D05/D08/D09 permanecen abiertas; esta demo no congela captura, política ni modelos.

## Accessibility & Inclusion

Pantalla proyectada en aula: conversación y tarjetas con tipografía grande y alto contraste. Los proyectores lavan colores: decisiones y estados deben tener texto y forma, además del color. Controles operables con teclado y foco visible; respeta `prefers-reduced-motion`.

## Vista de presentación — requisitos acordados (2026-10-29)

En definición mediante `/grill-with-docs` para [#110](https://github.com/Corchets/bitacora_tesis/issues/110); todavía sin implementar. Acuerdos confirmados por Luciano:

- Sumar una vista con dos siluetas de iPhone y conservar el panel actual, la prueba de ASR, el Historial y la vista de la persona protegida.
- Al iniciar el análisis desde los controles actuales, entrar automáticamente a Presentación. Permitir volver al panel durante la misma llamada sin reiniciar captura, transcripción ni detector.
- El diálogo grande ocupa el centro; los teléfonos indican quién habla. El resultado de cada análisis acompaña a la frase correspondiente y las métricas detalladas quedan en un panel desplegable.
- Cada teléfono muestra una pantalla de llamada y actividad de voz. El aviso «Posible estafa» aparece en el teléfono de la persona protegida, con motivo y frase resaltada en el diálogo central; el otro teléfono conserva el nombre «Otra persona».
- Los teléfonos permanecen visibles mientras el diálogo se desplaza en el centro siguiendo lo último. Si quien presenta sube para revisar una frase anterior, el seguimiento se pausa hasta tocar «Volver al vivo».
- La vista comunica «Analizando», «Sin aviso», «Posible estafa», «No evaluado» y «Error» según los eventos reales. La puntuación del detector y las demoras quedan en los detalles; la puntuación no se presenta como probabilidad calibrada de estafa.
- Los teléfonos representan la conversación y la actividad de la captura actual. La llamada se abre en Meet o WhatsApp; iniciar o terminar el análisis no marca, atiende ni cuelga la llamada externa.
- Usar los eventos reales disponibles, incluidos estados como «Esperando audio» y «Analizando». Esta vista no elige modelos ni agrega telefonía propia.
- El video de respaldo con ejemplo hardcodeado y voces sincronizadas se prepara al final, después de la integración; continúa pendiente en [#53](https://github.com/Corchets/bitacora_tesis/issues/53).

Referencia visual aportada por Luciano el 2026-10-29: pantalla de llamada de WhatsApp, con foto de perfil circular grande, nombre y estado sobre un fondo oscuro. Adoptar esa composición para las pantallas de los teléfonos; la captura sirve de referencia visual y no se incorpora al repositorio.

Pendientes del grill: correspondencia entre la foto y la persona representada por cada teléfono; transcripción provisoria y correcciones del ASR; cierre de la escena, errores y acciones disponibles. El diseño exacto del aviso del sistema final sigue pendiente en [D10](../../docs/gestion/MAPA-DECISIONES.md#d10--congelar-estructura-de-entrega-y-defensa).

## Brand Commitments

Español de Argentina, voseo. Etiquetas técnicas en inglés cuando corresponda.

## Evidence on Hand

Requisitos: [#75](https://github.com/Corchets/bitacora_tesis/issues/75), [#82](https://github.com/Corchets/bitacora_tesis/issues/82), [#83](https://github.com/Corchets/bitacora_tesis/issues/83) y confirmación del coordinador del 2026-10-26. Recorridos existentes y comandos en [README.md](README.md). Los ejemplos TTS son demostraciones, no evidencia de desempeño con voz humana.
