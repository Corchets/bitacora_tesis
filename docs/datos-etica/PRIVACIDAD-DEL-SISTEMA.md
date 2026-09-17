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

> Este encuadre documenta requisitos de diseño para el proyecto académico; no reemplaza un dictamen
> jurídico para desplegar un producto sobre llamadas reales.

La [Ley 25.326](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion) define como dato
personal cualquier información referida a una persona determinada o determinable y adopta una
definición amplia de tratamiento automatizado (art. 2). La voz, una transcripción y las inferencias
de riesgo pueden quedar alcanzadas cuando permiten identificar o perfilar a una persona. Que el
procesamiento ocurra en RAM no lo vuelve automáticamente ajeno a la ley: funciona como una medida
de minimización y seguridad.

El diseño adopta los siguientes requisitos:

| Norma | Consecuencia de diseño |
|---|---|
| Art. 4, incs. 1–3 y 7 | Datos adecuados y no excesivos, uso exclusivo para prevención/investigación declarada y destrucción cuando dejan de ser necesarios. |
| Art. 5 | Consentimiento libre, expreso e informado. En el corpus y en la VoIP controlada consienten ambos interlocutores antes del tratamiento. |
| Art. 6 | Antes de grabar se informa finalidad, responsable, destinatarios, carácter voluntario y posibilidad de acceso/supresión. |
| Arts. 9 y 10 | Medidas técnicas y organizativas de seguridad, acceso restringido y confidencialidad aun después del tratamiento. |
| Art. 11 | No hay cesión ni transferencia del audio o la transcripción a terceros. Una reutilización distinta exige base y consentimiento propios. |

Para el producto conceptual, la finalidad es la prevención inmediata del fraude; ASR y detector se
ejecutan localmente, el contenido no sale del dispositivo y los buffers se destruyen al terminar la
llamada. Para el corpus piloto sí existe una grabación temporal y consentida; su gobernanza se
define en el [issue #22](https://github.com/Corchets/bitacora_tesis/issues/22) y no se cierra en este
documento.

## 3. Comunicaciones privadas y no interceptación

El [Código Penal actualizado](https://www.argentina.gob.ar/normativa/nacional/16546/actualizacion)
distingue tres conductas relevantes:

- el **art. 153** sanciona abrir o acceder indebidamente a una comunicación no dirigida al autor y
  también interceptar o captar indebidamente comunicaciones electrónicas o telecomunicaciones de
  sistemas privados o restringidos;
- el **art. 153 bis** sanciona acceder sin autorización o excediendo la autorización a un sistema o
  dato informático de acceso restringido; y
- el **art. 197** sanciona interrumpir o entorpecer una comunicación. No es la figura que define la
  interceptación.

Además, la [Ley 27.078](https://www.argentina.gob.ar/normativa/nacional/239771/actualizacion), art. 5,
declara inviolables las comunicaciones cursadas por redes y servicios de telecomunicaciones y exige
requerimiento judicial para su interceptación, registro y análisis. La
[Ley 19.798](https://www.argentina.gob.ar/normativa/nacional/31922/actualizacion), arts. 18–21,
protege la inviolabilidad y el secreto de la correspondencia de telecomunicaciones.

El replay experimental no intercepta una telecomunicación en curso. En la VoIP propia, la aplicación
administra el flujo en el extremo y ambos participantes saben y consienten que será procesado. Sobre
esa base, la **hipótesis jurídica de trabajo** es que el prototipo controlado no constituye captación
indebida por un tercero: no accede a sistemas restringidos ajenos, no elude permisos y no interrumpe
ni desvía la comunicación. Esta es una inferencia de alcance académico, no una habilitación legal.

Esta conclusión es **acotada al laboratorio y a la VoIP propia y consentida**. No habilita capturar
llamadas PSTN ajenas, activar escucha encubierta, instalar la herramienta en el dispositivo de otra
persona, usar `root` para superar controles, ni procesar la voz de un interlocutor sin el aviso y la
base jurídica correspondientes. Un despliegue real fuera de ese entorno requiere revisión legal
específica. El consentimiento del usuario del teléfono y la ejecución local, por sí solos, no
resuelven automáticamente el régimen aplicable a la comunicación del otro interlocutor.

## 4. Justificación de las restricciones de plataforma (Android)

Android restringe la captura del audio de llamadas telefónicas convencionales (`VOICE_UPLINK`,
`VOICE_DOWNLINK`) a aplicaciones privilegiadas, preinstaladas y con `CAPTURE_AUDIO_OUTPUT`. Una
aplicación ordinaria no obtiene ese flujo durante una llamada ([Android Developers: compartir la
entrada de audio](https://developer.android.com/media/platform/sharing-audio-input), consulta
2026-09-17).

- **Motivo de la restricción:** Proteger la privacidad de los interlocutores frente a aplicaciones espía de terceros.
- **Decisión en la tesis:** En lugar de implementar exploits, root o técnicas de spyware, el proyecto asume formalmente esta restricción como parte del problema de ingeniería. Por ello, la experimentación se fundamenta en reproducción de audio (*replay*) y la integración de demostración en un flujo controlado (VoIP), donde el audio pertenece legítimamente a la aplicación.

## 5. Del prototipo al producto ideal

La tesis debe explicar la brecha hacia un producto real, pero no necesita demostrar aquello que dejó
fuera de alcance. Los tres escenarios no son equivalentes:

| Escenario | Qué puede sostener la tesis | Qué queda pendiente |
|---|---|---|
| Replay en laboratorio | Evalúa el motor incremental, latencia, memoria y anticipación de forma reproducible. | No demuestra integración con una llamada real. |
| VoIP propia y consentida | Demuestra una conversación real cuyo flujo administra la aplicación. | Requiere completar la interfaz, seguridad y revisión legal del despliegue. |
| Llamada PSTN en Android stock | Es el caso ideal de producto, pero una app ordinaria no puede capturar ambos sentidos de la llamada. | Requiere integración OEM/app de sistema con permisos privilegiados —o cooperación equivalente de plataforma— y análisis jurídico específico. |

Procesar en el extremo no implica necesariamente modificar ni interrumpir la red del prestador, pero
tampoco convierte a la aplicación en jurídicamente neutra. Si el camino de producto exige integración
con fabricante, sistema o prestador, habrá que determinar responsabilidades, avisos, consentimiento,
seguridad y normativa sectorial para esa arquitectura concreta. El Proyecto Final documenta esa
brecha como limitación y trabajo futuro; no afirma prefactibilidad legal ni técnica de captura PSTN
universal.

## 6. Reglas éticas para los datos del corpus

Para la construcción del corpus de entrenamiento y evaluación:

1. **Datos 100% ficticios:** En las simulaciones se emplean identidades, bancos, montos, códigos OTP y números de tarjeta completamente inventados.
2. **Sin víctimas reales:** No se graban llamadas de incidentes reales de víctimas ni se realiza contacto encubierto con estafadores.
3. **El audio no entra a Git:** Los archivos de audio (`.wav`) y cualquier material no anonimizado permanecen fuera del repositorio en cumplimiento de `.gitignore`. Git almacena exclusivamente código, esquemas y manifiestos de datos procesados.

## 7. Fuentes normativas y técnicas consultadas

- [Ley 25.326, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion),
  arts. 2, 4, 5, 6, 9, 10 y 11; consulta 2026-09-17.
- [Decreto 1558/2001, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/70368/actualizacion),
  reglamentación del consentimiento informado del art. 5; consulta 2026-09-17.
- [Código Penal, Ley 11.179, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/16546/actualizacion),
  arts. 153, 153 bis y 197; consulta 2026-09-17.
- [Ley 19.798, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/31922/actualizacion),
  arts. 18–21; consulta 2026-09-17.
- [Ley 27.078, texto actualizado](https://www.argentina.gob.ar/normativa/nacional/239771/actualizacion),
  art. 5; consulta 2026-09-17.
- [Android Developers: compartir la entrada de audio](https://developer.android.com/media/platform/sharing-audio-input),
  captura de llamadas por aplicaciones privilegiadas; consulta 2026-09-17.
