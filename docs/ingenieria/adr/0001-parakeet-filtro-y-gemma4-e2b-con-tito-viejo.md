# ADR 0001 — Usamos Parakeet con filtro Silero como ASR

- **Fecha:** 2026-11-03
- **Estado:** Aceptada
- **Participantes de la discusión:** equipo; la registra Luciano Grosso. El tutor dejó la arquitectura en manos del
  equipo ([minuta del 2026-10-28](../../gestion/seguimientos/2026-10-28.md#3-minuta-y-resoluciones-del-profesor)).
- **Ámbito:** arquitectura

> **Nota del 2026-11-07:** este ADR también fijaba el detector, con Tito viejo como compuerta de Gemma 4 E2B
> ([versión anterior](https://github.com/Corchets/bitacora_tesis/blob/624e71d/docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)).
> Ahora fija solo el ASR. Tito se está descartando
> ([H08](../../hallazgos/H08-tito-evita-falsas-alarmas-por-punto-ciego.md)), y el detector lo fija el ADR 0002
> ([#143](https://github.com/Corchets/bitacora_tesis/issues/143)).

## Contexto

[D09](../../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) pedía elegir el ASR. Tiene que correr en el
dispositivo, porque el tutor descartó usar un modelo por API, y tiene que ir escribiendo mientras se habla. Zipformer
Kroko, el ASR inicial, transcribía mal la voz real.

## Decisión

Usamos Parakeet TDT 0.6B v3 int8 por `sherpa-onnx`, con corte RMS 0,008 tras 0,8 s de silencio y Silero 0,5 solo como
filtro de voz (`parakeet-filtro`, opción B).

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Parakeet con Silero solo (opción A) | La frase final sale 0,75 s antes y conserva más términos críticos (76,4 % contra 70,9 %) | Parte las frases (205 segmentos contra 127) y mete inglés o portugués en 25 de 129 frases, contra 4 | Empata en etiquetas y empeora el texto (WER 32,8 % contra 25,6 %) |
| Zipformer Kroko | Streaming real, con parciales rápidos | Errores con voz real | Se retiró el 2026-10-29 |
| Whisper base | Conocido y fácil de correr | No es streaming: transcribe recién al cerrar la frase | La demo necesita ir escribiendo mientras se habla |

## Consecuencias

- El ASR sigue confundiendo «token» y «CVV», y Parakeet no permite fijar el idioma.
- La elección sale de 9 llamadas guionadas, con 4 guiones y 2 voces. No estima el rendimiento general.
- No se midió en teléfono. El ASR solo ya llega a 1 GB, por encima del techo de 512 MB de la prefactibilidad.

**Para reconsiderarla:** que los términos críticos perdidos cambien avisos en voz real, o que el ASR no entre en el
teléfono de referencia.

## Referencias

- [Medición de A contra B](../../../experiments/asr-local/corridas/2026-11-02_voz-real_dialogos-a-contra-b/resumen.md)
  y [criterio de §12.9](../../../experiments/asr-local/PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30).
- [Corrida con voz real por Meet](../../../experiments/voip/corridas/2026-11-02-voz-real-meet.md).
