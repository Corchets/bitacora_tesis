# ADR 0001 — Usamos Parakeet con filtro Silero y Gemma 4 E2B con Tito viejo

- **Fecha:** 2026-11-03
- **Estado:** Aceptada
- **Participantes de la discusión:** equipo; la registra Luciano Grosso. El tutor dejó la arquitectura en manos del equipo ([minuta del 2026-10-28](../../gestion/seguimientos/2026-10-28.md#3-minuta-y-resoluciones-del-profesor)).
- **Ámbito:** arquitectura

## Contexto

[D09](../../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) pedía elegir ASR y detector por calidad, falsas alarmas, tiempos y memoria. El cierre del tutor es el 2026-11-30, y la meta que fijó es avisar en 80–85 % de las estafas con 10–15 % de falsas alarmas, sin saltar por frases sueltas como «decime la contraseña». El hardware de referencia es la gama más alta de teléfonos disponible.

La inferencia tiene que ser local: el tutor descartó por completo un modelo por API. Zipformer Kroko, el ASR inicial, transcribía mal la voz real, y ninguna política sobre los Qwen llegó a la meta sin ajustarse sobre los datos de informe.

## Decisión

Usamos como **ASR** Parakeet TDT 0.6B v3 int8 por `sherpa-onnx`, con corte RMS 0,008 tras 0,8 s de silencio y Silero 0,5 solo como filtro de voz (`parakeet-filtro`, opción B).

Usamos como **detector** Tito viejo (RoBERTuito congelado con regresión logística, frase aislada, umbral 0,5) como compuerta de `gemma4:e2b-it-q4_K_M`, con el prompt `tarea`, `num_ctx` 4096, seed 42 y aviso único. Tito no avisa: activa al modelo, y el modelo decide.

Esta es la configuración que entra a la evaluación final. No se ajusta mirando el test reservado.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Tito viejo → Gemma 4 E4B | 10/10 estafas en #101 | 1/10 falsas alarmas; en la M1 de 8 GB entra en swap y avisó a +49 s | Misma detección, más costo y sin evidencia en vivo. Queda como comparador con GPU |
| Gemma 4 E2B directo | 10/10 estafas; no depende de Tito | 1/10 falsas alarmas y consulta en todas las líneas | Tito evita consultas sin perder estafas en estos 20 casos |
| Tito nuevo → E2B | 0/10 falsas alarmas | 2/10 estafas | Pierde casi todas las estafas |
| Qwen3.5 9B con prompt `v2` | 10/10 · 1/10 en GPU | 6,6 GB, no entra en el teléfono | Se conserva como techo, no como candidato |
| Riesgo primero con `gemma3n:e2b` | 1,9 s por línea | 10/10 con 3–6/10 falsas alarmas, o 2/10 con 0/10 | [No cumple la meta sin contaminar la selección](https://github.com/Corchets/bitacora_tesis/blob/reranker-prueba/experiments/slm-directo/analisis/2026-10-30-reranker-zero-shot/README.md) |
| Cross-encoder o NLI (bge, mDeBERTa, Qwen3-Reranker) | Sin generación de texto | Miden tema y no intención; bge tarda 4,6 s por línea en CPU | [Descartados con evidencia en #123](https://github.com/Corchets/bitacora_tesis/issues/123) |
| Reglas | Instantáneas y explicables | 58,3 % de falsas alarmas en negativos difíciles | Quedan como línea base y respaldo sin modelo |
| Parakeet con Silero solo (opción A) | La frase final sale 0,75 s antes; más términos críticos (76,4 % contra 70,9 %) | Parte las frases (205 segmentos contra 127) y mete inglés o portugués en 25 de 129 frases, contra 4 | Empata en etiquetas y empeora el texto (WER 32,8 % contra 25,6 %) |
| Zipformer Kroko | Streaming real, parciales rápidos | Errores con voz real | Retirado el 2026-10-29; queda como antecedente |
| Whisper base | Conocido y fácil de correr | No es streaming; solo transcribe al cerrar la frase | La demo necesita ir escribiendo mientras se habla |

## Consecuencias

- La documentación, el panel y las herramientas de medición arrancan con esta configuración.
- Sigue abierta [D08](../../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental): política de alerta y protocolo se congelan aparte, y la configuración se mide recién en el test reservado.
- **E2B no cumple el criterio de 2 s de #84** en la M1 de 8 GB: mediana de 3,74 s por consulta, aunque el aviso llegó entre −0,45 y +0,40 s del fin del pedido.
- **Sin medición en teléfono.** No se midió latencia, memoria, batería ni temperatura en Android. El archivo de E2B pesa 4,59 GB, Tito ocupa unos 0,48 GB y el ASR llega a 1 GB, muy por encima del techo de 512 MB de la prefactibilidad.
- **La evidencia que respalda la elección es de desarrollo:** 20 conversaciones sintéticas sin revisión humana, de las que salió la elección entre 10 modelos, y 9 llamadas guionadas con 4 guiones y 2 voces. Esos números son optimistas y no estiman el rendimiento final.
- **La reserva es pública desde el 2026-10-23.** Si Gemma 4 E2B se publicó después, hay que declarar la posible contaminación del test (R05). Falta verificar su fecha.
- El ASR sigue confundiendo «token» y «CVV» con ambas opciones, y Parakeet no permite fijar el idioma.

**Para reconsiderarla:** que el test reservado quede lejos de la meta del tutor, que E2B no pueda correr en el teléfono de referencia, o que los términos críticos perdidos cambien avisos en voz real.

## Referencias

- [Matriz #101](../../../experiments/slm-directo/corridas/2026-10-30_112956_101_informe_101.md): 10 modelos, 3 condiciones y 20 conversaciones.
- [Corrida con voz real por Meet](../../../experiments/voip/corridas/2026-11-02-voz-real-meet.md), con la demora de E2B.
- [Medición de A contra B](../../../experiments/asr-local/corridas/2026-11-02_voz-real_dialogos-a-contra-b/resumen.md) y [criterio de §12.9](../../../experiments/asr-local/PLAN-VOZ-REAL.md#129-dos-candidatos-para-comparar-en-diálogos-reales-2026-10-30).
- [Tito viejo y Gemma 4 en el panel](../../../experiments/voip/corridas/2026-11-02-tito-gemma4-panel.md) y [diagnóstico de Tito](../../../experiments/slm-directo/DIAGNOSTICO-TITO-2026-10-29.md).
