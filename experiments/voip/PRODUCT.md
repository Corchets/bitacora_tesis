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

Demo prevista para el 2026-10-28. Fuentes existentes: ejemplos SC-WA-CODE-01 y LG-WA-CONSULTA-01, micrófono, Meet en Chrome, WhatsApp Desktop mediante BlackHole y segunda notebook con cliente.py. El servidor guarda las llamadas fuera de Git.

## Capabilities and Constraints

- Nombres exactos: «Persona protegida» y «Otra persona»; con aviso, «Otra persona · posible estafa». No inferir que toda llamada es fraudulenta.
- Conversación: otra persona a la izquierda, protegida a la derecha. Evaluación junto a la frase que la disparó, con riesgo, sí/no, demora y salteadas. Línea de riesgo en el tiempo y momento del aviso.
- Detector fijo al arrancar el servidor: mostrar nombre y modelo, sin selector.
- Conservar fuentes, iniciar, terminar, nueva llamada, validaciones y errores. «Probar el ASR» es un modo aparte, solo micrófono y sin detector.
- Corte de silencio de 0,8 s fijo en llamada; elegible en prueba ASR.
- Aviso en franja visible y breve, nunca modal; su implementación completa pertenece a #83.
- Vista `?vista=protegida` simple y existente, sin rediseñar.
- D05/D08/D09 permanecen abiertas; esta demo no congela captura, política ni modelos.

## Accessibility & Inclusion

Pantalla proyectada en aula: conversación y tarjetas con tipografía grande y alto contraste. Los proyectores lavan colores: decisiones y estados deben tener texto y forma, además del color. Controles operables con teclado y foco visible.

## Brand Commitments

Español de Argentina, voseo. Etiquetas técnicas en inglés cuando corresponda.

## Evidence on Hand

Requisitos: [#75](https://github.com/Corchets/bitacora_tesis/issues/75), [#82](https://github.com/Corchets/bitacora_tesis/issues/82) y confirmación del coordinador del 2026-10-26. Recorridos existentes y comandos en [README.md](README.md). Los ejemplos TTS son demostraciones, no evidencia de desempeño con voz humana.
