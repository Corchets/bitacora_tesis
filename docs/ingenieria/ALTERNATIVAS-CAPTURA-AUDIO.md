# Alternativas para obtener el audio

**Estado:** comparación preparada para la reunión del 2026-09-09. La decisión D05 se tomó ese día; ver la [minuta](../gestion/seguimientos/2026-09-09.md) y el [mapa de decisiones](../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable).

## La distinción clave

Hay que separar dos preguntas:

1. **¿Cómo evaluamos científicamente el detector?** Requiere reproducibilidad,
   timestamps exactos y ejecutar muchas veces el mismo audio.
2. **¿Cómo demostramos una interacción parecida a una llamada?** Requiere una
   integración visible, pero no necesariamente es la fuente de los experimentos.

Una sola alternativa no tiene por qué resolver ambas cosas.

## Comparación

| Alternativa | Ventajas | Desventajas | Uso recomendado |
|---|---|---|---|
| Replay de WAV/FLAC como stream | reproducible, control temporal exacto, permite repetir modelos, medir latencia y testear cientos de llamadas | no es una llamada telefónica real | base obligatoria de experimentación y contingencia de demo |
| Llamada en altavoz + micrófono externo | simple, intuitiva para una demostración, incorpora ruido y eco reales | audio variable, mezcla ambos hablantes, depende del ambiente, difícil de reproducir | despriorizada por mezcla de canales; no es la demo objetivo ni el dataset principal |
| Misma app intentando grabar una llamada celular en altavoz | parece cercana al producto deseado | Android da prioridad a la llamada y no entrega uplink/downlink a apps ordinarias; puede recibir silencio o solo micrófono según dispositivo/estado | no usar como dependencia del proyecto |
| Llamada VoIP controlada dentro de la solución | la app posee el flujo de audio, permite experiencia end-to-end y separa canales si se diseña así | integración, eco, red y permisos agregan trabajo; podría consumir varias semanas | integración objetivo después de validar el motor |
| AOSP/root/app OEM privilegiada | acceso potencial al audio de telefonía del sistema | requiere dispositivo/ROM especial, permisos privilegiados, baja portabilidad y alto riesgo | únicamente extensión experimental, fuera del núcleo |

Android documenta que una llamada siempre conserva el audio y que una app solo
puede capturar uplink/downlink si es una aplicación privilegiada preinstalada con
`CAPTURE_AUDIO_OUTPUT`: [Sharing audio input](https://developer.android.com/media/platform/sharing-audio-input).
Las fuentes `VOICE_CALL`, `VOICE_UPLINK` y `VOICE_DOWNLINK` requieren ese permiso,
que no está disponible para aplicaciones de terceros:
[`MediaRecorder.AudioSource`](https://developer.android.com/reference/android/media/MediaRecorder.AudioSource).

## Implementación escalonada tras D05

### Nivel 1 — Base científica, obligatoria

```text
archivo de audio
      ↓ reproducido en ventanas de tiempo real
ASR local
      ↓
detector incremental
      ↓
riesgo + explicación + timestamp de alerta
```

Sirve para entrenar, comparar, probar y reproducir los resultados.

### Nivel 2 — Integración objetivo

Una llamada VoIP controlada entrega a la aplicación el audio permitido. Solo se
inicia cuando el Nivel 1 funciona y se mide el esfuerzo de integración.

### Alternativa despriorizada — Altavoz externo

Una llamada entre dos dispositivos podría reproducirse por altavoz y captarse con
un tercer dispositivo o notebook, pero mezcla hablantes y ambiente. El tutor la
despriorizó el 2026-09-09; no reemplaza el benchmark reproducible ni es un hito
obligatorio de demostración.

## Decisión validada el 2026-09-09

El tutor aprobó el *replay* de grabaciones como base experimental reproducible y la
llamada VoIP controlada como integración objetivo del prototipo. PSTN universal
desde una app Android ordinaria queda fuera de alcance. Esta decisión no demuestra
todavía la factibilidad de la integración VoIP ni el rendimiento en Android.

## Prueba mínima de factibilidad propuesta

El issue del spike debe producir una evidencia mínima:

1. elegir un audio corto en español sin datos reales;
2. reproducirlo como archivo/stream;
3. pasarlo por un ASR local disponible;
4. registrar texto, tiempo total y errores visibles;
5. marcar manualmente dónde debería aparecer una alerta por “código”;
6. llevar a clase el resultado, aunque todavía sea imperfecto.

No hace falta resolver VoIP antes de esta prueba. La finalidad es demostrar que el motor
puede recibir audio incremental y hacer visible el mayor riesgo técnico temprano.
