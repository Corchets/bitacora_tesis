# Privacidad y consideraciones éticas del sistema

Este documento define la postura técnica de privacidad para el diseño del detector de vishing,
su justificación bajo la normativa argentina y las reglas de resguardo para los datos del proyecto.

---

## 1. Privacidad por diseño en el producto (Privacy by Design)

Un detector de vishing opera sobre una de las señales más sensibles de un usuario: su voz y sus
conversaciones en tiempo real. Para garantizar una protección legítima y segura, el sistema se
diseña bajo los siguientes principios técnicos:

1. **Inferencia local estricta (*on-device*):**
   - El reconocimiento de voz (ASR) y el modelo de detección de riesgo se ejecutan en el hardware local.
   - Ni el flujo de audio ni las transcripciones textuales se transmiten a servidores externos ni a servicios en la nube.
2. **Descarte inmediato en memoria volátil:**
   - El buffer de audio y las transcripciones intermedias residen exclusivamente en memoria RAM durante la llamada.
   - Al finalizar o cortarse la comunicación, los buffers se liberan inmediatamente; el sistema no persiste el contenido de lo conversado.
3. **Registro mínimo de eventos:**
   - La aplicación solo conserva un log de metadatos de seguridad: fecha, hora, duración, nivel máximo de riesgo alcanzado y maniobras identificadas (ej. `URGENCY`, `REQUEST_OTP`).
   - Nunca se guardan números de cuenta, códigos dictados ni fragmentos de audio.
4. **Asistencia consentida vs. vigilancia encubierta:**
   - La herramienta es operada por el propio usuario para su autoprotección.
   - No actúa como un agente silencioso o espía: el usuario tiene control explícito de activación y visualización de advertencias.

## 2. Marco legal argentino (Ley 25.326 de Protección de Datos Personales)

La [Ley 25.326](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion) protege los datos
personales y las comunicaciones privadas:

- **Finalidad específica:** El tratamiento de la señal tiene como única finalidad la prevención inmediata del fraude en beneficio directo del titular del dispositivo.
- **Sin cesión a terceros:** Al no existir almacenamiento persistente ni backend comercial, no hay transferencia, comercialización ni riesgo de filtración masiva de datos en reposo.

## 3. Justificación de las restricciones de plataforma (Android)

Android restringe a nivel de sistema operativo la captura del audio de llamadas telefónicas convencionales (`VOICE_CALL`, `VOICE_DOWNLINK`) mediante permisos exclusivos (`CAPTURE_AUDIO_OUTPUT`).

- **Motivo de la restricción:** Proteger la privacidad de los interlocutores frente a aplicaciones espía de terceros.
- **Decisión en la tesis:** En lugar de implementar exploits, root o técnicas de spyware, el proyecto asume formalmente esta restricción como parte del problema de ingeniería. Por ello, la experimentación se fundamenta en reproducción de audio (*replay*) y la integración de demostración en un flujo controlado (VoIP), donde el audio pertenece legítimamente a la aplicación.

## 4. Reglas éticas para los datos del corpus

Para la construcción del corpus de entrenamiento y evaluación:

1. **Datos 100% ficticios:** En las simulaciones se emplean identidades, bancos, montos, códigos OTP y números de tarjeta completamente inventados.
2. **Sin víctimas reales:** No se graban llamadas de incidentes reales de víctimas ni se realiza contacto encubierto con estafadores.
3. **El audio no entra a Git:** Los archivos de audio (`.wav`) y cualquier material no anonimizado permanecen fuera del repositorio en cumplimiento de `.gitignore`. Git almacena exclusivamente código, esquemas y manifiestos de datos procesados.
