# Alternativas para obtener el audio

**Decisión a solicitar:** miércoles 9 de septiembre de 2026.

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
| Llamada en altavoz + micrófono externo | simple, intuitiva para una demostración, incorpora ruido y eco reales | audio variable, mezcla ambos hablantes, depende del ambiente, difícil de reproducir | demo temprana y prueba de robustez, no dataset principal |
| Misma app intentando grabar una llamada celular en altavoz | parece cercana al producto deseado | Android da prioridad a la llamada y no entrega uplink/downlink a apps ordinarias; puede recibir silencio o solo micrófono según dispositivo/estado | no usar como dependencia del proyecto |
| Llamada VoIP controlada dentro de la solución | la app posee el flujo de audio, permite experiencia end-to-end y separa canales si se diseña así | integración, eco, red y permisos agregan trabajo; podría consumir varias semanas | integración objetivo después de validar el motor |
| AOSP/root/app OEM privilegiada | acceso potencial al audio de telefonía del sistema | requiere dispositivo/ROM especial, permisos privilegiados, baja portabilidad y alto riesgo | únicamente extensión experimental, fuera del núcleo |

Android documenta que una llamada siempre conserva el audio y que una app solo
puede capturar uplink/downlink si es una aplicación privilegiada preinstalada con
`CAPTURE_AUDIO_OUTPUT`: [Sharing audio input](https://developer.android.com/media/platform/sharing-audio-input).
Las fuentes `VOICE_CALL`, `VOICE_UPLINK` y `VOICE_DOWNLINK` requieren ese permiso,
que no está disponible para aplicaciones de terceros:
[`MediaRecorder.AudioSource`](https://developer.android.com/reference/android/media/MediaRecorder.AudioSource).

## Propuesta concreta

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

### Nivel 2 — Demo inmediata

Una llamada entre dos dispositivos se reproduce por altavoz. Un tercer dispositivo
o notebook capta el ambiente y ejecuta el detector. Demuestra interacción y ruido,
pero sus resultados no reemplazan el benchmark reproducible.

### Nivel 3 — Integración objetivo

Una llamada VoIP controlada entrega a la aplicación el audio permitido. Solo se
inicia cuando el Nivel 1 funciona y se mide el esfuerzo de integración.

## Recomendación

Pedir al profesor que apruebe esta formulación:

> La evaluación principal será sobre grabaciones reproducidas como flujo en tiempo
> real, para garantizar repetibilidad y marcas temporales. Se hará una demostración
> temprana mediante altavoz y micrófono externo. La integración final deseada será
> una llamada VoIP controlada, siempre que no comprometa la evaluación del motor.
> La captura universal de llamadas celulares desde una aplicación Android ordinaria
> queda fuera de alcance por restricciones documentadas de la plataforma.

## Preguntas al profesor

1. ¿Considera suficiente replay en tiempo real para validar científicamente el
   detector?
2. ¿Acepta que la llamada VoIP sea integración objetivo y no requisito absoluto?
3. ¿Desea una demostración con altavoz como evidencia de robustez/interacción?
4. ¿Prefiere que el prototipo sea móvil desde el inicio o que primero se valide el
   motor en computadora y luego se despliegue?

## Spike de esta semana

El issue del spike debe producir una evidencia mínima:

1. elegir un audio corto en español sin datos reales;
2. reproducirlo como archivo/stream;
3. pasarlo por un ASR local disponible;
4. registrar texto, tiempo total y errores visibles;
5. marcar manualmente dónde debería aparecer una alerta por “código”;
6. llevar a clase el resultado, aunque todavía sea imperfecto.

No hace falta resolver VoIP esta semana. La finalidad es demostrar que el motor
puede recibir audio incremental y hacer visible el mayor riesgo técnico temprano.
