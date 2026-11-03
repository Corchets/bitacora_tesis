> **Estado: borrador del 2026-11-03.** Falta el resultado de la evaluación final, que completa el resumen. El título sigue abierto en [D13](../gestion/MAPA-DECISIONES.md#d13--título-definitivo).

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

Este trabajo diseña, implementa y evalúa un prototipo local que transcribe una conversación en español mientras ocurre, estima si hay una estafa con lo dicho hasta ese momento y emite un único aviso explicado, antes de que la persona cumpla el pedido. La configuración elegida usa Parakeet TDT 0.6B v3 para transcribir, con corte por energía y filtro de voz Silero, y un filtro liviano basado en RoBERTuito que decide cuándo consultar a Gemma 4 E2B. Todo el procesamiento ocurre en el equipo.

La evaluación mide falsas alarmas y margen temporal respecto del pedido y del cumplimiento, además de las métricas habituales de clasificación. Sobre material de desarrollo, la configuración avisó en 10 de 10 estafas sin falsas alarmas en 10 legítimas, y en 9 llamadas guionadas con voz real avisó en las 7 estafas y en ninguna de las 2 legítimas. Esos valores no estiman el rendimiento final. **[Completar con el resultado del test reservado, #52.]**

**Palabras clave:** vishing, ingeniería social, detección incremental, reconocimiento de voz, modelos de lenguaje pequeños, inferencia local, español.

## Abstract

Vishing is a voice-call scam in which someone impersonates a bank, a public agency, a support desk or a relative in order to obtain a code, a password or a money transfer. Defences based on caller reputation cannot see what is said during the call, and official advice depends on the person remembering it under pressure.

This work designs, implements and evaluates a local prototype that transcribes a Spanish conversation as it happens, estimates whether a scam is under way using only what has been said so far, and issues a single explained warning before the person complies with the request. The chosen configuration uses Parakeet TDT 0.6B v3 for transcription, with energy-based segmentation and a Silero voice filter, and a lightweight RoBERTuito-based filter that decides when to query Gemma 4 E2B. All processing happens on the device.

The evaluation measures false alarms and the time margin before the request and before compliance, in addition to the usual classification metrics. On development material, the configuration warned on 10 of 10 scams with no false alarms on 10 legitimate calls, and on 9 scripted calls with real voices it warned on all 7 scams and on neither of the 2 legitimate calls. These values do not estimate final performance. **[Complete with the held-out test result, #52.]**

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
