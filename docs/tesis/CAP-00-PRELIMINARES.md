> **Estado: borrador del 2026-11-03.** Falta el resultado de la evaluación final, que completa el resumen. **Al 2026-11-21:** el resumen y el abstract ya llevan la evaluación final del 2026-11-19. El título sigue abierto en [D13](../gestion/MAPA-DECISIONES.md#d13--título-definitivo).

# Preliminares

**Universidad del Norte Santo Tomás de Aquino**
**Facultad de Ingeniería · Ingeniería en Informática, Plan 2008**
**Proyecto Final Integrador**

**Título provisional:** Detección incremental y explicable de vishing en conversaciones de voz en español

**Integrantes:** Albarracín Ignacio, Antenucci Mateo, Grosso Luciano y Villalobo Evaristo.
**Tutor:** Ing. Ernesto Rico.
**Año:** 2026.

## Resumen

El vishing es una estafa por llamada de voz en la que alguien se hace pasar por un banco, un organismo, una mesa de soporte o un familiar para conseguir un código, una clave o una transferencia. Las defensas basadas en la reputación del número no ven lo que se dice durante la llamada, y las recomendaciones oficiales dependen de que la persona las recuerde en el momento de presión.

Este trabajo diseña, implementa y evalúa un prototipo local que transcribe una conversación en español mientras ocurre, estima si hay una estafa con lo dicho hasta ese momento y emite un único aviso explicado, antes de que la persona cumpla el pedido. La configuración elegida usa Parakeet TDT 0.6B v3 para transcribir, con corte por energía y filtro de voz Silero, y consulta a Gemma 4 E2B al cierre de cada turno de quien llama, con un prompt que pregunta por su intención. Todo el procesamiento ocurre en el equipo.

La evaluación mide falsas alarmas y margen temporal respecto del pedido y del cumplimiento, además de las métricas habituales de clasificación. En la evaluación final, sobre conversaciones escritas, el detector avisó 73 de 100 estafas generadas que no habían intervenido en ninguna elección, llegó a tiempo en 53 de las 80 que tienen pedido y dio 15 falsas alarmas en 56 llamadas legítimas. Avisó las 33 estafas reales de un conjunto externo, pero también 21 de 33 llamadas reales legítimas de call center, y cambiar el prompt no corrigió esa falsa alarma. En 9 llamadas guionadas con voz real, una configuración anterior avisó en las 7 estafas y en ninguna de las 2 legítimas. Medido en dos teléfonos, el detector tardó 3,7 s por turno en un Samsung A56, con el prompt anterior, y 0,8 s en un iPhone 15 Pro Max, con la configuración final y también con el reconocimiento de voz corriendo a la vez.

**Palabras clave:** vishing, ingeniería social, detección incremental, reconocimiento de voz, modelos de lenguaje pequeños, inferencia local, español.

## Abstract

Vishing is a voice-call scam in which someone impersonates a bank, a public agency, a support desk or a relative in order to obtain a code, a password or a money transfer. Defences based on caller reputation cannot see what is said during the call, and official advice depends on the person remembering it under pressure.

This work designs, implements and evaluates a local prototype that transcribes a Spanish conversation as it happens, estimates whether a scam is under way using only what has been said so far, and issues a single explained warning before the person complies with the request. The chosen configuration uses Parakeet TDT 0.6B v3 for transcription, with energy-based segmentation and a Silero voice filter, and queries Gemma 4 E2B at the end of each turn of the caller, with a prompt that asks about the caller's intent. All processing happens on the device.

The evaluation measures false alarms and the time margin before the request and before compliance, in addition to the usual classification metrics. In the final evaluation, on written conversations, the detector warned on 73 of 100 generated scams that had played no part in any design choice, was on time for 53 of the 80 that contain a request, and raised 15 false alarms on 56 legitimate calls. It warned on all 33 real scams of an external set, but also on 21 of 33 real legitimate call-centre calls, and changing the prompt did not fix that false-alarm rate. On 9 scripted calls with real voices, an earlier configuration warned on all 7 scams and on neither of the 2 legitimate calls. Measured on two phones, the detector took 3.7 s per turn on a Samsung A56, with the previous prompt, and 0.8 s on an iPhone 15 Pro Max, with the final configuration and also with speech recognition running at the same time.

**Keywords:** vishing, social engineering, incremental detection, speech recognition, small language models, on-device inference, Spanish.

## Siglas

| Sigla | Significado |
|---|---|
| ASR | Reconocimiento automático del habla |
| CER / WER | Tasa de error por carácter / por palabra |
| RMS | Valor cuadrático medio, usado como medida de energía del audio |
| RTF | Factor de tiempo real: tiempo de cómputo sobre duración del audio |
| SLM | Modelo de lenguaje pequeño |
| VAD | Detección de actividad de voz |
| VoIP | Voz sobre IP |
| `T_A`, `T_R`, `T_C` | Instantes del aviso, del primer pedido riesgoso y del primer cumplimiento |
| `L_R`, `L_C` | Márgenes del aviso respecto de `T_R` y de `T_C` |

## Contribuciones del equipo

**[Completar entre los cuatro.]** La [gestión del proyecto](CAP-10-GESTION-DEL-PROYECTO.md#105-contribuciones-y-carga-de-trabajo) reúne lo que ya está registrado en la bitácora.
