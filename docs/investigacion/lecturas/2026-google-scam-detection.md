# Defensas antifraude telefónico de Google (Scam Detection, Fake Call Detection, Call Screen)

- **Qué es:** conjunto de funciones comerciales cerradas de Google para Android / Pixel, no un
  trabajo académico. No hay paper, no hay código, no hay dataset.
- **Empresa:** Google LLC.
- **Primer anuncio de Scam Detection en llamadas:** 13/11/2024 (Google Online Security Blog) [F3].
- **Fecha de consulta de todas las fuentes de esta ficha:** **2026-09-17**.
- **Clave BibTeX:** *(pendiente — son fuentes web, van como `@misc` con `urldate = {2026-09-17}`)*

> **Advertencia de método.** Esta ficha está escrita contra fuentes primarias de Google (blog.google,
> security.googleblog.com, support.google.com, developer.android.com, developers.google.com, el
> reporte técnico de Gemini en arXiv y una solicitud de patente de Google LLC). Todo lo que Google no
> publica figura como **"no publicado"**. Donde extrapolo desde documentación de desarrollador hacia
> el producto interno, está marcado como **extrapolación**. Nada se completó con conocimiento previo.

> **Advertencia de alcance.** Google usa el nombre "Scam Detection" para **cuatro** cosas distintas:
> en llamadas, en Google Messages, en notificaciones de apps de chat de terceros, y hay además un
> "Fake Call Detection" y un "Call Screen". Las páginas de soporte de Google mezclan las listas de
> países e idiomas de unas y otras (ver §6). Esta ficha separa los productos.

---

## 1. Qué modelo es, exactamente

### 1.1 Lo que Google afirma del producto

| Afirmación | Fuente | Fecha del anuncio |
|---|---|---|
| "For Pixel 9 and later devices: Scam Detection is powered by Gemini Nano on-device. For earlier devices: Scam Detection uses Google's on-device machine learning models." | [F1] | página vigente al 2026-09-17 |
| "During our limited beta, we analyzed calls with Gemini Nano, Google's built-in, on-device foundation model, on Pixel 9 devices and used smaller, robust on-device machine-learning models for Pixel 6+ users. Our testing showed that Gemini Nano outperformed other models" | [F2] | 2025-03-04 |
| "Gemini Nano, our advanced on-device AI model, powers Scam Detection on Pixel 9 series devices." | [F3] | 2024-11-13 |
| "Powered by Gemini's on-device model" | [F4] | 2026-02-25 |

Obsérvese la degradación del lenguaje: en 2024–2025 Google nombra **"Gemini Nano"**; en 2026 pasa a
decir **"Gemini's on-device model"**, sin versión. Nunca dice cuál.

### 1.2 Lo que Google NO publica sobre el modelo de Scam Detection

- **Si es Gemini Nano genérico o una variante fine-tuneada para la tarea: no publicado.** No hay
  ninguna frase de Google que diga "adaptador específico para detección de estafas", ni lo contrario.
- **Versión concreta (nano-v2 / nano-v3 / nano-v4): no publicado** para Scam Detection.
- **Cantidad de parámetros del modelo que corre en Scam Detection: no publicado.**
- **Cuantización y footprint del modelo en Scam Detection: no publicado.**
- **Qué modelo exactamente es el de "Pixel 6+" ("smaller, robust on-device machine-learning models"):
  no publicado.** Ni familia, ni arquitectura, ni tamaño.

### 1.3 Lo que sí está publicado sobre Gemini Nano como familia

Del reporte técnico *Gemini: A Family of Highly Capable Multimodal Models* [F11]:

> "Nano, with 1.8B (Nano-1) and 3.25B (Nano-2) parameters, targeting low and high memory devices
> respectively. It is trained by distilling from larger Gemini models. **It is 4-bit quantized for
> deployment** and provides best-in-class performance."

También:

> "Models are trained to support 32K context length, employing efficient attention mechanisms such as
> multi-query attention" — dicho de la familia Gemini 1.0 en general, arquitectura *decoder-only
> Transformer* [F11].

**Cuidado:** esas cifras son de **Gemini 1.0 Nano (2023)**. Las variantes que Google despliega hoy en
Android se llaman `nano-v2`, `nano-v3` y `nano-v4` [F12] y **Google no publica sus parámetros ni su
cuantización**. Atribuirle 1.8B/3.25B al modelo que corre hoy en un Pixel 10 sería un error.

### 1.4 Distribución y actualización en el dispositivo: AICore

Esto sí está documentado como fuente primaria de desarrollador:

- "Gemini Nano runs in Android's **AICore** system service, which leverages device hardware to enable
  low inference latency and **keeps the model up-to-date**." [F15]
- "**AICore manages the distribution of Gemini Nano and handles future updates.** You don't need to
  worry about downloading or updating large models over the network, nor impact on your app's disk
  and runtime memory budget." [F15]
- "To address this challenge, we developed **AICore, a new system service in Android**. AICore allows
  you to benefit from AI running directly on the device without needing to distribute runtimes,
  models and other components yourself." [F17]
- "**Every app is able to use the shared Gemini Nano model that is on the device.** This avoids the
  need to have to wait for a model to be downloaded if it already exists on a device." [F12]
- El acceso de terceros pasa por el **Google AI Edge SDK** (`com.google.ai.edge.aicore`) [F17] o por
  las **ML Kit GenAI APIs**, que "are built on top of AICore" [F12].
- Para saber qué versión corre en el equipo: "Different versions of Gemini Nano run on different
  devices. To return the version of Gemini Nano on a device, use `getBaseModelName()`." [F12]

### 1.5 Fine-tuning: lo único que Google documenta es para las APIs de desarrollador

El Android Developers Blog describe cómo Google mantiene la calidad de sus *propias* GenAI APIs sobre
distintas versiones del modelo base:

> "**Adapter training:** With results from the evaluation pipeline, we then determine if we need to
> train **feature-specific LoRA adapters to be deployed on top of the Gemini Nano base model**. By
> shipping GenAI APIs with LoRA adapters, we ensure each API meets our quality bar regardless of the
> version of Gemini Nano running on a device." [F16]

La página de Gemini Nano en developer.android.com muestra además "runtime with model weights and
LoRAs" en su diagrama de arquitectura de AICore [F15].

> **Extrapolación propia, explícitamente no confirmada por Google:** el patrón *modelo base compartido
> + adaptador LoRA por función* es el mecanismo que Google documenta para sus APIs de GenAI, y sería
> el camino natural para Scam Detection. **Google nunca dice que Scam Detection use un adaptador
> LoRA.** Si esto se cita en la tesis, tiene que citarse como inferencia, no como hecho.

### 1.6 Lo documentado para desarrolladores NO es necesariamente lo que corre adentro de Scam Detection

Hay que ser explícito en la tesis: Scam Detection es una función de sistema de Google (app Teléfono +
servicios de Pixel), no una app que consuma la API pública. Dos indicios de que el camino público es
más restringido que el interno:

- "GenAI API inference is permitted only when the app is **the top foreground application**. Using the
  API when the app is not in the foreground, **including using a foreground service**, will result in
  an `ErrorCode.BACKGROUND_USE_BLOCKED` response." [F12]
- "AICore enforces an **inference quota per app**. Making too many GenAI API requests in a short
  period will result in an `ErrorCode.BUSY` response. Also,
  `ErrorCode.PER_APP_BATTERY_USE_QUOTA_EXCEEDED` can be returned if an app exceeds a long-duration
  quota (e.g. daily quota)." [F12]

Esto es directamente relevante para el prototipo de la tesis: **una app de terceros no puede hoy
correr inferencia repetida de Gemini Nano durante una llamada en segundo plano por la vía pública
documentada.** Es una restricción de plataforma, no un problema de diseño del prototipo.

---

## 2. Ventana de contexto

### 2.1 Para Scam Detection específicamente

**No publicado.** Google no dice cuántos tokens de conversación sostiene Scam Detection, ni cuánto
historial conserva, ni qué pasa en una llamada larga. Se buscó en blog.google, security.googleblog.com,
las páginas de soporte de la app Teléfono y de Pixel, developer.android.com y Google Research: no hay
ninguna cifra.

### 2.2 Para Gemini Nano vía las APIs públicas: 4.000 tokens de entrada

Esta es la **única cifra dura publicada** y aplica a las ML Kit GenAI APIs:

> "**Input must be under 4000 tokens (or approximately 3000 English words).** For more information,
> see the `countTokens` reference." — *Get started with Prompt API* [F13]
>
> "Use cases that require long output (**more than 4K tokens**) should be avoided." [F13]

La misma restricción aparece en la API de resumen, con una recomendación de manejo de desbordamiento
que vale la pena registrar porque es exactamente el problema de la tesis:

> "Input must be under 4000 tokens (or approximately 3000 English words). **If the input exceeds 4000
> tokens, consider these options: Prioritize summarization of the first 4000 tokens** [...];
> **Segment the input into groups of 4000 tokens, and summarize them** [...]" — *Summarization API* [F14]

### 2.3 Parámetros de generación documentados

`GenerationConfig` del Google AI Edge SDK (`com.google.ai.edge.aicore`) expone [F18]:

| Campo | Documentación textual | Máximo documentado |
|---|---|---|
| `maxOutputTokens` | "The max tokens to generate per response" | **ninguno** |
| `temperature` | "The degree of randomness in token selection, typically between 0 and 1" | rango orientativo |
| `topK` | "How many tokens to select amongst the highest probabilities" | **ninguno** |
| `candidateCount` | "The max *unique* responses to return" | **ninguno** |

Los ejemplos de código del blog de Android usan `topK = 30`, `candidateCount = 4`,
`maxOutputTokens = 300` [F17], pero son valores de ejemplo, no límites.

### 2.4 Conclusión operativa de esta sección

La cifra a citar en la tesis es **4.000 tokens de entrada (~3.000 palabras en inglés)** como límite
documentado de la superficie pública de Gemini Nano en Android [F13][F14]. Es una ventana **chica**:
una llamada de estafa de diez minutos con transcripción completa la desborda. Cualquier diseño
incremental sobre un LLM on-device tiene que resolver el desbordamiento — con ventana deslizante, con
resumen acumulado, o con clasificación por turno. **Que Google publique explícitamente la estrategia
de segmentación en 4.000 tokens para resumen [F14] y no publique nada equivalente para Scam Detection
es en sí un hallazgo.**

Nota de honestidad: el límite de 4.000 tokens es de las **ML Kit GenAI APIs**, no de Scam Detection.
Es plausible que el producto interno use una ventana distinta. **Google no lo dice.**

---

## 3. Cómo funciona lo incremental — pregunta central

### 3.1 Conclusión primero

**Google NO publica la arquitectura incremental de Scam Detection.** La expectativa del coordinador
queda **confirmada** para blog, documentación de soporte y documentación de desarrollador. Se revisó:
blog.google (seguridad, Android, Pixel), security.googleblog.com, support.google.com (Teléfono, Pixel,
Android), developer.android.com, developers.google.com/ml-kit, Google Research y arXiv. **No hay paper
de Google sobre Scam Detection en llamadas.**

Lo único que Google afirma públicamente sobre el mecanismo son frases de producto:

- "We use AI models processed on-device to **analyze conversations in real-time** and warn users of
  potential scams." [F2]
- "Scam Detection uses powerful on-device AI to notify you of a potential scam call happening in
  real-time by **detecting conversation patterns commonly associated with scams**." [F3]
- "Scam Detection alerts you if a caller uses **speech patterns commonly associated with fraud**." [F4]
- "Scam Detection is based on **the corpus of knowledge about how scammers scam victims**." [F1]

Ninguna de esas frases dice si clasifica sobre transcripción acumulada, ventana deslizante o turno; ni
cada cuánto reevalúa; ni si mantiene estado.

### 3.2 La solicitud de patente — leída y verificada sobre el PDF original

**US 2024/0388655 A1 — "In-call scam detection", Google LLC.** [F19]

Datos de portada, **verificados visualmente sobre el PDF de la USPTO** el 2026-09-17:

| Campo | Valor |
|---|---|
| Título | IN-CALL SCAM DETECTION |
| Applicant | Google LLC, Mountain View, CA (US) |
| Inventores | **Lyubov Farafonova** (San Francisco), **Yixuan Geng** (Mountain View), **Usman Abdullah** (Albany), **Rebecca Chiou** (San Mateo) |
| Appl. No. | 18/662,999 |
| Filed | May 13, 2024 |
| Pub. Date | Nov. 21, 2024 |
| Prioridad | Provisional 63/502,298, filed May 15, 2023 |
| Clasificación | Int. Cl. H04M 3/22; CPC H04M 3/2281, H04M 3/2218 |

Farafonova es la misma Product Manager que firma los anuncios de Scam Detection en blog.google
[F2][F4] y en el Security Blog [F3].

> **Nota de método.** El PDF son 42 páginas de escaneo bitonal (`CCITTFaxDecode`), sin capa de texto:
> la verificación automática por extracción no es posible. El contenido se obtuvo por OCR y las
> páginas que sostienen las afirmaciones de esta sección (portada, 9, 15 y 17 de la numeración
> impresa) **se inspeccionaron visualmente una por una**. Los números de párrafo `[00NN]` son la
> referencia estable.

> **Cautela obligatoria, sin cambios.** Una solicitud de patente describe el espacio de
> reivindicación, no el producto embarcado, y **está pendiente, no concedida**. Google nunca dijo
> "este es el diseño de Scam Detection". En la tesis se cita como *"una solicitud de patente de
> Google LLC cuya inventora principal es la PM del producto describe el siguiente mecanismo"*, nunca
> como *"Scam Detection funciona así"*.

> **El documento describe DOS modos que comparten componentes** y conviene no mezclarlos: el
> filtrado previo por asistente (*call screening*, FIGS. 1A-1B y 3A-3B, `conversation model 152/252`)
> y la detección durante la llamada en curso (*in-call scam detection*, FIGS. 8-13, `AI model 890`).

**a) Granularidad: por turno (utterance), con contexto acumulado.** [0085], p. 9:

> "in response to receiving an utterance in the call, perform automatic speech recognition to convert
> the utterance into text and to input the converted text into conversation model 252 along with any
> other relevant contextual information, such as previous utterances in the conversation during the
> call (e.g., words, phrases, and/or sentences previously spoken by the parties on the call), **the
> vocal characteristics (e.g., intonation) of utterances received in the call**, whether the identity
> of the remote computing device is listed in the contacts [...] the location [...] the current time
> and/or date, events listed in an calendar application [...] previous conversations with the party"

**ASR primero, modelo sobre texto después**, con los turnos previos como contexto. Acumulación
conversacional, no ventana deslizante explícita.

**b) CORRECCIÓN — sí hay una señal prosódica.** Una versión anterior de esta ficha afirmaba que el
análisis era *puramente lingüístico* y que la patente no mencionaba prosodia. **Es incorrecto.** El
párrafo [0085] incluye "**vocal characteristics (e.g., intonation)**" entre las entradas contextuales.
Matices que igual hay que conservar:

- Las palabras `prosody`, `prosodic`, `voice stress`, `deepfake`, `synthetic audio`,
  `voice biometrics` y `speaker verification` **no aparecen** en el documento.
- [0085] está en la parte de *call screening* (`conversation model 252`), no en la de detección en
  llamada (`AI model 890`). Que la entonación alimente al 890 **no está dicho**.
- El peso de las señales enumeradas en [0140] y en las reivindicaciones es abrumadoramente
  lingüístico: palabras, frases, sentimiento, categoría temática. La entonación aparece una vez.

Redacción defendible: *"la solicitud contempla entonación como una entrada contextual más, pero el
mecanismo que describe es dominantemente lingüístico y no menciona biometría de voz ni detección de
audio sintético."*

**c) Estado entre evaluaciones: un valor de confianza que sube y baja.** [0138], p. 15. No se
menciona KV cache ni resumen acumulado. El estado explícito es el *confidence value*.

**d) CORRECCIÓN — no son dos umbrales, son CUATRO niveles.** Esto también estaba mal en la versión
anterior:

| Nivel | Condición | Acción |
|---|---|---|
| **suspected scam call threshold** | por debajo del principal — "suspect [...] and yet, lack sufficient confidence" [0138] | notifica sospecha **y pide al usuario que lea en voz alta una pregunta guionada** (*scripted inquiry*) |
| **scam call threshold** | umbral principal [0139] | alerta de estafa con opciones *descartar* / *cortar*; **corta solo si el usuario lo pide** |
| **secondary scam call threshold** | más alto; se evalúa si el usuario **descartó o ignoró** la primera alerta y la llamada sigue [0154]-[0156] | segunda alerta en la misma llamada |
| **critical scam call threshold** | "sufficiently high level of confidence [...] takes automatic action" [0157] | **corta la llamada sin input del usuario** y emite una notificación con los motivos |

**e) El mecanismo más interesante: *scripted inquiry* (sondeo activo).** [0138], p. 15:

> "processing circuitry may send for output by mobile computing device 802, **a request for a scripted
> inquiry to be read aloud by a callee** during the conversation. [...] the on-device large language
> model monitors for **responsive utterances from the caller**. In such examples, processing circuitry
> may **increase or decrease a confidence value** [...] based on the callee reading the script prompted
> by AI model 890"

Cuando la confianza queda **entre** el umbral de sospecha y el principal, el sistema **no espera
pasivamente**: le pide al usuario que le haga una pregunta al llamante y usa la respuesta para
resolver la ambigüedad. Ver §3.4.

**f) Dos capas de señal, baratas y caras.** Las reivindicaciones separan:

- **Matching conditions** (p. 19, reivindicaciones): coincidencia con *key-word list*, *phrase list*,
  *sentiment watch list* y *subject matter watch list*.
- **Evaluaciones del LLM** (p. 20): 19 condiciones semánticas — pedido de OTP, *callee* empezando a
  leer el OTP, pedido de acceso remoto, robo-dialer, número *spoofed*, mensaje pregrabado, saludo
  genérico, "no cortes", "fue elegido para un premio", amenaza, **tono amenazante**, **tono urgente**,
  venta a presión, oferta por tiempo limitado, negarse a decir qué empresa representa o dar teléfono
  de retorno, pedir confirmación de datos personales, pago con instrumento que no sea tarjeta de
  crédito, y pago con tarjeta para cubrir envío.

**g) Nueve condiciones sustantivas de estafa.** [0140], p. 15: defraudar, declaraciones ilegales,
extorsionar dinero, obtener información de autenticación, y suplantar entidad gubernamental, fuerza
de seguridad, soporte técnico, banco del usuario o atención al cliente de e-commerce.

**h) Explicabilidad y realimentación.** [0141]-[0143], p. 15: *scam report* posterior que explica por
qué se sospechó ("a threatening tone from the caller or a request for money"); pedido de feedback
cuando el usuario descarta una alerta; y el feedback entra al modelo **como datos de reinforcement
learning**, on-device, con variante en la nube bajo autorización [0143]. Las GUIs de feedback listan
qué pidió el estafador (*Full Name, Contact info, Remote access, Download app, Password*) y a quién
suplantaba (*IRS, Bank, Friend, FBI, Relative, Police*).

**i) Desbordamiento de ventana, límites de tokens, resumen o descarte de turnos viejos: NO APARECEN
en el documento.** Se buscó explícitamente. La patente no dice qué pasa en una llamada larga.

**j) Latencia desde el patrón hasta la alerta: no publicada**, ni acá ni en ningún otro lado.

**k) Declaración del problema, citable.** [0158], p. 17:

> "Previous solutions cannot identify a scam call without a user first speaking with the potential
> scammer. The problem is made worse by scammers rotating and/or spoofing their phone numbers [...]
> crowdsourcing, though helpful, is insufficient to identify scam calls based on the originating
> phone number. With previously known techniques, there is no mechanism by which to reliably identify
> that a call is a scam."

Es Google declarando que la reputación de números no alcanza — exactamente el argumento de §3 del
anteproyecto.


### 3.3 Privacidad y procesamiento (relevante para el diseño incremental)

- "Data processing for Scam Detection is all done on-device. **No conversation audio or transcription
  is stored on the device, sent to Google servers or anywhere else.**" [F1]
- "Call audio is processed **ephemerally** and no conversation audio or transcription is recorded,
  stored on the device, or sent to Google or third parties." [F2]
- "no conversation audio or transcription is stored on the device, sent to Google servers or anywhere
  else, or **retrievable after the call**." [F3]
- La patente formaliza esto: "**no portion of the call data** from the call is retained by the mobile
  computing device or transmitted off of the mobile computing device subsequent to the ephemeral
  evaluation" [F19]. Aunque también contempla, con permiso, el camino contrario: "In other examples,
  off-device AI models are utilized with user permission." [F19]

Consecuencia para la tesis: el modelo de Google **no puede** hacer una pasada global al final de la
llamada ni guardar la transcripción para reanálisis. Está obligado a ser incremental y a descartar.
Eso es exactamente la restricción que la tesis adopta por diseño.

---

---

### 3.4 De qué nos podemos inspirar

Ocho ideas transferibles. Ninguna obliga a copiar el diseño de Google: son mecanismos, y varios son
mejorables.

**1. Sondeo activo (*scripted inquiry*) — la idea más fuerte.** Un detector incremental pasivo está
atrapado en el compromiso de ERDE: cortar temprano con poca evidencia, o acertar tarde. El sondeo
activo **rompe ese compromiso** porque genera evidencia en vez de esperarla. En la zona de
ambigüedad, sugerirle al usuario una pregunta ("¿me das el número de sucursal y te llamo yo?") separa
mucho a un banco real de un estafador: el primero responde sin problema, el segundo evade o presiona.
Es un mecanismo **novedoso, implementable y medible**, y encaja con el vector acústico por altavoz
—no hace falta inyectar audio, habla el usuario. Candidato fuerte a contribución propia.

**2. Confianza no monótona.** El valor **sube y baja**. La mayoría de los clasificadores incrementales
ingenuos solo acumulan. Que una respuesta satisfactoria del llamante **baje** el riesgo es lo que
permite convivir con falsos positivos sin volverse inusable.

**3. Escalera de umbrales con acción graduada.** Cuatro niveles con cuatro respuestas distintas, en
vez de un umbral binario. Y sobre todo el **secundario**: qué hacer cuando el usuario ya descartó la
alerta y la llamada sigue — justo el caso de la víctima bajo presión social, que es la que más
importa. Se puede reportar una métrica por nivel.

**4. Dos capas de costo.** Listas léxicas baratas (palabras, frases, sentimiento, categoría) que
pueden **disparar** la inferencia cara del LLM. Dado el presupuesto de cómputo de un teléfono y los
4.000 tokens de ventana, correr el modelo grande en cada turno probablemente no cierre. Esta
arquitectura en cascada es directamente aplicable, y **es contrastable**: se puede medir cuánto se
pierde por usar la cascada en lugar del LLM en cada turno.

**5. Semilla de taxonomía, gratis y citable.** Las 19 condiciones de (f) más las 9 de (g) más los
ítems de las GUIs de feedback son un punto de partida para `MANUAL-ANOTACION.md` y **D07**, que
todavía está abierto. No se copian: se **adaptan** a la pragmática argentina, y ahí está el aporte —
"entidad gubernamental" acá es AFIP/ANSES, el premio es el cupón, el soporte técnico es el del banco.
Poder decir "partimos de la taxonomía implícita en la patente de Google y la adaptamos, con estas
diferencias medidas" es mucho más fuerte que inventar una taxonomía de cero.

**6. Las GUIs de feedback son un esquema de anotación.** "¿Qué te pidió?" (nombre, contacto, acceso
remoto, instalar app, contraseña) y "¿de quién se hacía pasar?" (IRS, banco, amigo, FBI, familiar,
policía) son, literalmente, campos de etiquetado por llamada. Sirven para el manual de anotación y
para el instrumento post-llamada del estudio con voluntarios.

**7. Explicación obligatoria.** El *scam report* dice **por qué** se disparó. Como la tesis va a tener
una taxonomía explícita —que es su ventaja sobre la caja negra— la explicación sale casi gratis: la
etiqueta que disparó el umbral **es** la explicación. Google lo promete en la patente y **no lo
entrega en el producto**. Ahí hay un hueco concreto para ocupar.

**8. Lo efímero como restricción de diseño, no como limitación.** Sin almacenar audio ni
transcripción, no hay pasada global al final: **el sistema está obligado a ser incremental**. Conviene
adoptarlo explícitamente en `ARQUITECTURA.md` y en el consentimiento: es a la vez garantía ética y
justificación metodológica del enfoque incremental.

**Lo que NO conviene copiar:** el corte automático sin intervención del usuario (umbral crítico). Es
la parte más riesgosa —un falso positivo corta una llamada legítima— y en el producto embarcado
**Google tampoco lo implementó**. Para una tesis con voluntarios, además, dispara problemas éticos
que no valen la pena. Conviene dejarlo documentado como alternativa descartada, con su motivo.

## 4. Qué NO publica Google (la sección que más vale para el capítulo 2)

1. **Ninguna métrica de rendimiento.** Ni precisión, ni recall, ni F1, ni tasa de falsos positivos, ni
   curva ROC, ni matriz de confusión — para ningún producto de los tres. La única afirmación
   comparativa es cualitativa y sin números: "Our testing showed that **Gemini Nano outperformed other
   models**" [F2]. Es un hallazgo citable: **el estado del arte comercial en detección conversacional
   de vishing no reporta ninguna métrica de clasificación.**
2. **Ninguna evaluación reproducible.** No hay benchmark, no hay protocolo, no hay baseline.
3. **Ningún dataset.** No se publica corpus de entrenamiento ni de evaluación. Solo "the corpus of
   knowledge about how scammers scam victims" [F1], que no es una referencia verificable, y la mención
   de que "we partnered with financial institutions around the world to better understand the latest
   advanced and most common scams their customers are facing" [F2], sin detalle.
4. **Ninguna taxonomía pública de patrones de estafa para llamadas.** Los blogs dan dos ejemplos
   sueltos: pago con gift cards para completar una entrega [F2] y un supuesto banco pidiendo
   transferir fondos con urgencia por una brecha de cuenta [F3]. La lista de nueve categorías de §3.2g
   está en la **patente**, no en documentación de producto.
5. **Ninguna cifra de latencia.**
6. **Ninguna descripción de la arquitectura incremental** (frecuencia de reevaluación, manejo de
   estado, desbordamiento de ventana, histéresis) fuera de la patente.
7. **La versión y el tamaño del modelo que corre en Scam Detection.**
8. **La lista de idiomas soportados por Scam Detection en llamadas** (ver §6).
9. **Qué es exactamente el modelo de Pixel 6–8** ("smaller, robust on-device machine-learning models").
10. **Ningún paper de Google Research sobre el tema.** Verificado: no existe.
11. **Cifras de escala sin desagregar:** "over **10 billion** suspected malicious calls and messages
    every month" [F4], con la nota al pie "This total comprises all instances where a message or call
    was proactively blocked **or** where a user was alerted to potential spam or scam activity" [F4].
    Mezcla llamadas y mensajes, bloqueos y alertas: **no es utilizable como métrica de detección.**
12. **Las evaluaciones de terceros que Google cita están financiadas por Google.** "Based on
    third-party research **funded by Google LLC** in Feb 2025 comparing the Pixel 9 Pro, iPhone 16
    Pro, Samsung S24+ and Xiaomi 14 Ultra" (Leviathan Security Group) [F2]; y una evaluación de
    Counterpoint Research citada sin enlace ni metodología [F4]. **No son evidencia independiente.**

---

## 5. Los tres productos, separados (resumen breve)

### 5.1 Scam Detection en llamadas — análisis del contenido

- **Momento de intervención:** durante la llamada, en segundo plano, "automatically runs in the
  background of calls that could be scams" [F1]. "Scam Detection only applies to calls that could
  potentially be scams, and is **never used during calls with your contacts**" [F2].
- **Qué hace al disparar:** "alerts you with notification, sound, and vibration" [F1]; botones "Not a
  scam" y "End call" [F1].
- **Aviso a la otra parte:** "Scam Detection will have an **audible beep at the start of the call and
  every few minutes after**" [F1]. Dato de diseño relevante para la tesis: Google resuelve el problema
  legal/ético de escuchar la conversación con un tono audible periódico, no con consentimiento previo
  del llamante.
- **Ejecución:** on-device (§3.3).
- **Por defecto:** **desactivado**, opt-in explícito. "The feature is **off by default**. The user has
  to actively opt in to turn on the feature." [F1] Justificación de Google: "phone call audio is more
  ephemeral compared to messages, which are stored on devices" [F2].
- **Limitaciones declaradas por Google:** "**Not all scam calls can be detected. Scam Detection is not
  100% accurate** and scammers constantly change their tactics. Always use caution when you answer
  calls from unknown numbers." [F1]
- **Disponibilidad al 2026-09-17** [F1]: solo dispositivos Google Pixel; requiere SIM asociada a un
  país soportado **y** el equipo físicamente en ese país.
  - Pixel 6 y posteriores: **EE.UU.**
  - Pixel 9 y posteriores: Alemania, Australia, Canadá, España, Francia, India, Irlanda, Italia,
    Japón, México, Reino Unido, Singapur.
  - Pixel 9a y Pixel 10a: solo EE.UU.
  - Expansión anunciada a **Samsung Galaxy S26 en EE.UU.** [F4].
  - **Contradicción entre fuentes de Google:** la página de soporte dice "Scam Detection only works on
    Google Pixel devices" [F1], mientras el blog de junio de 2026 dice "Pixel and Samsung users can
    also enable Scam Detection in the Phone by Google app" [F5]. Además, el blog de febrero de 2026
    lista los países **sin Singapur** [F4] y la página de soporte **sí lo incluye** [F1].

### 5.2 Fake Call Detection — verificación de identidad del llamante

- **Momento de intervención:** al recibir la llamada, antes / al inicio, no durante la conversación.
- **Mecanismo publicado** [F5]: "Think of it like a **digital handshake between devices**. When a
  contact calls you and you're both using Phone by Google, their device sends a **silent confirmation
  signal in real time** to your device to verify the call is legitimate and truly coming from the
  contact's device. Because this digital handshake uses **end-to-end encrypted Rich Communication
  Services (RCS)** technology, it is completely private." Y ante la ausencia de la señal: "Your device
  will instantly notice this and **ping your contact's actual device to double-check**. If their real
  device says, 'I'm not making a call right now,' you'll get a warning on your screen advising you to
  hang up immediately."
- **No analiza contenido ni audio.** Es verificación de origen. **No detecta deepfakes por análisis de
  voz**: detecta que el dispositivo real del contacto no está llamando.
- **Requisitos** [F5][F6]: Android 12+; apps Phone by Google, Contacts y Google Messages instaladas;
  RCS activado en Google Messages; **ambas partes** deben usar Phone by Google.
- **Por defecto:** **activado**. "This feature is **on by default** and works automatically behind the
  scenes." [F5] Se puede desactivar en ajustes de la app Teléfono [F5].
- **Disponibilidad:** "We are rolling out fake call detection **globally** in Phone by Google to
  Android 12+ devices this month **starting with Pixel devices**" (junio 2026) [F5]. No hay lista de
  países ni de idiomas — por su naturaleza es agnóstico del idioma.
- **Estándar abierto:** "we built this feature on top of **Rich Communication Services (RCS), an open
  standard** – making it possible for other apps and device manufacturers to adopt this technology"
  [F5]. **Google no publica la especificación concreta del intercambio** (formato de mensaje, timeouts,
  claves): solo dice que es sobre RCS E2EE. No hay RFC ni documento GSMA citado.
- **Métricas:** ninguna.
- **Limitación estructural declarada:** solo funciona si ambas partes usan Phone by Google [F5]. En
  vishing real el atacante nunca es un contacto agendado, así que **esta función no cubre el escenario
  de la tesis**; cubre la suplantación de un contacto conocido.
- **Matiz de privacidad:** el handshake se declara E2EE, pero la función vive dentro de "caller ID &
  spam protection", sobre la cual Google dice: "To use caller ID and spam protection, **your phone may
  need to send information about your calls to Google**" [F6].
- **Función hermana, distinta:** *verified financial calls* — el teléfono le pregunta a la app oficial
  del banco si realmente está llamando, y si el banco no lo confirma "your Android phone
  **automatically ends the call**"; requiere Android 11+, app del banco instalada y sesión iniciada, y
  la disponibilidad "varies by financial institution" [F10].

### 5.3 Call Screen / Filtro de llamadas — el asistente atiende

- **Momento de intervención:** **antes** de atender. El asistente ("Call Assist") contesta, pregunta
  quién llama y por qué, y transcribe en tiempo real [F7].
- **Ejecución:** "Call Screen works on your device and **doesn't use Wi-Fi or mobile data**" [F7].
- **Cómo decide:** "Call Screen detects spam based on **what a caller says**, or if **matched in
  Google's database of known spammers and robocallers**" [F8]. Es decir, contenido **más** reputación
  centralizada.
- **Qué se graba:** a diferencia de Scam Detection, **sí guarda**. "All screened calls will save a
  **transcript** of the screening on your phone. You can have your Pixel phone also save
  **recordings**." [F7] "To protect your privacy, transcripts and recordings are **stored only on your
  phone**." [F8]
- **Qué puede salir del dispositivo (voluntario):** el usuario puede compartir audio, transcripción y
  detalles con Google; entonces "**Humans may review** caller data to help improve machine learning
  and spam detection in Call Screen" y Google declara "Store your Call Screen data on Google servers
  for **up to 2 years**" [F8].
- **Límite explícito:** "**We're not processing call data outside of the screening phase** (when a
  user joins the call)." [F8] Es decir, **Call Screen no analiza la conversación una vez que el
  usuario atiende**. Ahí es donde entra Scam Detection, y donde entra la tesis.
- **Disponibilidad** [F7]: filtrado automático en Australia, Canadá, Irlanda, Reino Unido y EE.UU.;
  filtrado manual además en Francia, Alemania, India (solo Pixel 10/11), Italia, Japón y España.
  Manual también en equipos Android seleccionados en EE.UU. y Canadá. **Inconsistencia interna de
  Google:** otra página de soporte todavía afirma que el filtrado automático está "In English, In the
  United States, On all Pixel phones with Android 10 and up" [F8].
- **Limitaciones declaradas:** "Not all spam calls and robocalls can be detected"; "Call Screen won't
  always fully understand and transcribe what a caller said"; no funciona con apps de grabación de
  terceros; no filtra automáticamente en roaming; incompatible con desvío de llamadas [F7].
- **Respuestas con IA:** "AI replies are generated **on device** based on information from the
  screening phase of the call. **Replies may be inaccurate** and don't represent Google's views." [F7]

---

## 6. Disponibilidad en español y en Argentina (párrafo corto)

**Argentina no figura en ninguna lista de disponibilidad de Scam Detection en llamadas** [F1], ni en
inglés ni en la versión es-419 de la misma página, consultadas el 2026-09-17. Tampoco figura en Call
Screen [F7]. Como la función exige SIM de un país soportado **y** presencia física en ese país [F1],
en Argentina no es utilizable. Sobre el **español**: Google **no publica la lista de idiomas de Scam
Detection en llamadas**; se puede inferir soporte de español porque **España y México** están en la
lista de países [F1], pero es inferencia propia. Lo que sí está publicado son idiomas de **otros**
productos homónimos: Scam Detection en Google Messages soporta "English, Arabic, French, German,
Portuguese, and Spanish" [F4], y Scam Detection **para mensajes de chat en Pixel** lista árabe,
inglés, francés, alemán, indonesio, japonés, portugués y español [F9]. **Esas listas no son de
llamadas** — la página de Pixel las publica bajo el encabezado "Scam Detection for chat messages"
[F9], y confundirlas es un error fácil de cometer. Para la tesis alcanza con: **en Argentina no
funciona; para español en llamadas no hay confirmación documental directa.**

---

## 7. Relación con nuestra tesis

**En qué se parece.** Mismo nivel de análisis (conversacional, sobre el contenido), misma ejecución
(on-device), misma intervención (alerta durante la llamada), misma restricción de privacidad
(procesamiento efímero, sin retención). Confirma que el enfoque es técnicamente viable en hardware
móvil actual y que la industria lo considera el lugar correcto para intervenir.

**En qué se diferencia.** Google es una caja negra sin métricas, sin taxonomía de producto, sin
dataset, sin protocolo de evaluación y sin arquitectura publicada. La tesis propone lo contrario: un
prototipo reproducible, con taxonomía explícita de patrones de manipulación, evaluación temporal
(tiempo de intervención) y corpus anotado en español rioplatense.

**Qué espacio deja libre.**
1. **La evaluación.** Nadie publicó jamás precisión/recall de detección conversacional de vishing en
   producto. Una evaluación honesta con protocolo abierto es aporte legítimo.
2. **El español argentino.** Sin disponibilidad en Argentina y sin idiomas publicados para llamadas.
3. **La explicabilidad.** El producto de Google alerta pero no explica por qué [F1]; la explicación
   aparece solo como aspiración en la patente [F19].
4. **La arquitectura incremental documentada.** Nadie publicó cómo resolver la reevaluación continua
   bajo una ventana de contexto chica. Esa es, hoy, la contribución técnica más defendible.

**Qué queda justificado.** Procesamiento local; descarte del audio; alerta durante la llamada en lugar
de post-mortem; aviso audible a la contraparte como solución al problema ético de escuchar (Google lo
hace con un beep periódico [F1] — precedente citable); y el par de umbrales alerta/acción, que la
patente de Google formaliza [F19].

**Qué queda amenazado.**
1. **La novedad.** No se puede afirmar primicia. Google lleva desde noviembre de 2024 con un producto
   embarcado [F3]. La redacción correcta es "combinación y reproducibilidad", no "primero".
2. **La utilidad práctica**, si Google llega a Argentina antes de la defensa. Mitigación: el aporte es
   el método y el corpus, no el producto.
3. **La vía de implementación.** Las APIs públicas de Gemini Nano hoy **prohíben inferencia en
   background** [F12], lo cual bloquea la ruta más obvia para un prototipo que corra durante la
   llamada. Hay que decidir explícitamente qué motor local usa el prototipo — esto debería alimentar
   una decisión en `MAPA-DECISIONES.md`.

---

## 8. Verificación de la matriz del estado del arte

Fila "Google Scam Detection" de `SINTESIS-ESTADO-DEL-ARTE.md`, celda por celda. **No se editó ese
archivo**; esto es solo un reporte.

| Celda | Valor actual | Veredicto | Fundamento |
|---|---|---|---|
| Nivel de análisis | Conversacional | **Confirmado** | "analyze conversations in real-time" [F2]; "detecting conversation patterns commonly associated with scams" [F3] |
| Vector de detección | Contenido de la llamada | **Confirmado, con precisión a agregar** | Es **dominantemente** lingüístico: ASR por turno → texto → modelo [0085]. Pero la patente **sí** lista "vocal characteristics (e.g., intonation)" entre las entradas contextuales [0085], así que decir "cero prosodia" sería falso. No menciona biometría de voz, estrés vocal ni audio sintético. Celda sugerida: "Contenido de la llamada, dominantemente lingüístico (ASR + NLP)" |
| Ejecución | On-device (Pixel) | **Confirmado, pero desactualizado** | On-device: sí [F1][F2][F3]. "(Pixel)" ya no alcanza: Google anunció expansión a **Samsung Galaxy S26 en EE.UU.** [F4]. Sugerido: "On-device (Pixel; Samsung S26 desde 2026)" |
| ¿Cubre manipulación psicológica? | Sí | **Confirmado** | Google define el objetivo como "conversational scams, which can often appear initially harmless before evolving into harmful situations" [F2] y describe presión por urgencia bancaria [F3]. La patente enumera extorsión, suplantación y obtención de credenciales [F19] |
| Reproducible académicamente | No — caja negra | **Confirmado y reforzable** | Sin métricas, sin dataset, sin protocolo, sin paper. Sugerido reforzar: "No — caja negra; **cero métricas publicadas**" |

**Celda ausente que convendría agregar a la matriz:** *"¿Publica métricas?"*. Sería la columna donde
la propuesta de la tesis se distingue con más claridad, y donde Google, Samsung y las soluciones
comerciales quedan todas en "No".

**Además:** la matriz no distingue **Fake Call Detection** de **Scam Detection**. Son productos
distintos con vectores distintos (verificación criptográfica de origen vs. análisis de contenido).
Convendría una fila propia para Fake Call Detection, con vector "identidad del llamante (handshake
RCS E2EE)", ejecución "entre dispositivos", manipulación psicológica "No", reproducible "Parcial — se
apoya en RCS, estándar abierto, pero el protocolo concreto no está publicado".

---

## 9. Literatura citable para el diseño incremental

Como Google no publica la arquitectura, esto es lo que el tesista **sí** puede citar para fundamentar
su propio diseño incremental. **Todas las referencias fueron verificadas por DOI contra Crossref o
contra la API de arXiv el 2026-09-17.** No hay ninguna referencia incluida sin verificar.

### 9.1 Clasificación temprana de texto (lo más cercano al problema)

1. **Dulac-Arnold, G.; Denoyer, L.; Gallinari, P. (2011).** *Text Classification: A Sequential Reading
   Approach.* ECIR 2011, LNCS. DOI: `10.1007/978-3-642-20161-5_41`. — Formaliza leer el texto de a
   fragmentos y decidir cuándo parar. Antecedente directo del "clasificar sin haber terminado de leer".
2. **Escalante, H. J.; Villatoro-Tello, E.; Garza, S. E.; López-Monroy, A. P.; Montes-y-Gómez, M.;
   Villaseñor-Pineda, L. (2017).** *Early detection of deception and aggressiveness using
   profile-based representations.* Expert Systems with Applications. DOI:
   `10.1016/j.eswa.2017.07.040`. — Detección temprana de **engaño**, que es literalmente el fenómeno
   de la tesis, con métricas que penalizan la demora.

### 9.2 Detección temprana de riesgo (eRisk / CLEF) — el marco de evaluación

3. **Losada, D. E.; Crestani, F. (2016).** *A Test Collection for Research on Depression and Language
   Use.* CLEF 2016, LNCS. DOI: `10.1007/978-3-319-44564-9_3`. — Paper fundacional de eRisk. Introduce
   la métrica **ERDE** (*Early Risk Detection Error*), que penaliza acertar tarde. **Esto es
   exactamente lo que la tesis necesita para poner "el tiempo de intervención en el centro".**
4. **Losada, D. E.; Crestani, F.; Parapar, J. (2018).** *Overview of eRisk: Early Risk Prediction on
   the Internet.* CLEF 2018, LNCS. DOI: `10.1007/978-3-319-98932-7_30`. — Y las ediciones siguientes:
   2019 (`10.1007/978-3-030-28577-7_27`) y 2020 (`10.1007/978-3-030-58219-7_20`). Diez años de
   protocolo de evaluación temprana sobre flujos de texto, con *baselines* y métricas consensuadas.

### 9.3 Clasificación temprana de series temporales (la formalización del trade-off)

5. **Xing, Z.; Pei, J.; Yu, P. S. (2011).** *Early classification on time series.* Knowledge and
   Information Systems. DOI: `10.1007/s10115-011-0400-x`. — El planteo canónico del compromiso
   precisión/anticipación.
6. **Mori, U.; Mendiburu, A.; Dasgupta, S.; Lozano, J. A. (2018).** *Early Classification of Time
   Series by Simultaneously Optimizing the Accuracy and Earliness.* IEEE TNNLS. DOI:
   `10.1109/tnnls.2017.2764939`. — Optimización conjunta de acierto y anticipación; base formal para
   justificar un umbral de disparo.

### 9.4 Vishing y alertas durante la llamada

7. **Sharevski, F.; Vander Loop, J.; Evans, B.; Ponticello, A. (2024).** *(Blind) Users Really Do Heed
   Aural Telephone Scam Warnings.* arXiv
   preprint `arXiv:2412.04014` (v1, 2024-12-05). — Estudio con 36 personas legalmente ciegas y 36
   videntes sobre cómo reaccionan a advertencias **auditivas** de estafa telefónica, comparando sin
   advertencia / advertencia corta / advertencia contextual. Relevante para el diseño de la
   intervención y para argumentar que la **modalidad** de la alerta importa. *Preprint: verificar si
   tiene versión publicada antes de citarlo como definitivo.*
8. **Biswal, S. (2021).** *Real-Time Intelligent Vishing Prediction and Awareness Model (RIVPAM).*
   2021 International Conference on Cyber Situational Awareness, Data Analytics and Assessment
   (CyberSA), 14/06/2021. DOI: `10.1109/cybersa52016.2021.9478240`. — Antecedente de predicción de
   vishing en tiempo real. Autoría y venue verificados contra Crossref el 2026-09-17.

> **Nota:** **VishGPT**, citado en `SINTESIS-ESTADO-DEL-ARTE.md`, **no se pudo verificar en Crossref**
> con los términos usados. Antes de citarlo en el informe hay que localizar su DOI o su venue real. No
> se agrega acá una entrada que no se pudo verificar.

---

## 10. Citas textuales que podríamos usar

> "Not all scam calls can be detected. Scam Detection is not 100% accurate and scammers constantly
> change their tactics." — Ayuda de la app Teléfono de Google [F1]

> "Scam Detection is based on the corpus of knowledge about how scammers scam victims." — Ayuda de la
> app Teléfono de Google [F1]

> "Our testing showed that Gemini Nano outperformed other models" — Google, blog de seguridad,
> 2025-03-04 [F2] *(única afirmación de rendimiento publicada; sin ninguna cifra)*

> "Traditional spam protections are focused on protecting users before the conversation starts, and
> are less effective against these latest tactics from scammers that turn dangerous mid-conversation
> and use social engineering techniques." — Google, 2025-03-04 [F2] *(justifica el enfoque de la tesis
> con palabras de Google)*

> "We're not processing call data outside of the screening phase (when a user joins the call)." —
> Ayuda de la app Teléfono, sobre Call Screen [F8] *(delimita exactamente el hueco que cubre la tesis)*

> "Input must be under 4000 tokens (or approximately 3000 English words)." — ML Kit GenAI, Prompt API
> [F13]

---

## 11. Fuentes

Todas consultadas el **2026-09-17**.

- **[F1]** Google. *Use Scam Detection — Phone app Help.* https://support.google.com/phoneapp/answer/15654065?hl=en
  (versión es-419: https://support.google.com/phoneapp/answer/15654065?hl=es-419). Sin fecha de
  publicación visible; contenido vigente al 2026-09-17. **Primaria.**
- **[F2]** Google. *New AI-Powered Scam Detection Features to Help Protect You on Android.* blog.google,
  2025-03-04. https://blog.google/security/new-ai-powered-scam-detection-features/ (espejo en
  https://security.googleblog.com/2025/03/new-ai-powered-scam-detection-features.html). **Primaria.**
- **[F3]** Farafonova, L.; Kafka, S. *Safer with Google: New intelligent, real-time protections on
  Android to keep you safe.* Google Online Security Blog, 2024-11-13.
  https://security.googleblog.com/2024/11/new-real-time-protections-on-Android.html. **Primaria.**
- **[F4]** Farafonova, L.; Pastor Nieto, A. *Staying One Step Ahead: Strengthening Android's Lead in
  Scam Protection.* blog.google, 2026-02-25.
  https://blog.google/security/staying-one-step-ahead-strengthening-androids-lead-in-scam-protection/.
  **Primaria.**
- **[F5]** Lynch, E.; Kensinger, T.; Schetrit, O. *How Android helps keep you safe from impersonation
  scams with fake call detection.* blog.google, 2026-06-02.
  https://blog.google/security/android-fake-call-detection/. **Primaria.**
- **[F6]** Google. *Use caller ID & spam protection — Phone app Help.*
  https://support.google.com/phoneapp/answer/3459196?hl=en. **Primaria.**
- **[F7]** Google. *Screen your calls before you answer them — Phone app Help.*
  https://support.google.com/phoneapp/answer/9118387?hl=en. **Primaria.**
- **[F8]** Google. *Keep your calls private — Phone app Help.*
  https://support.google.com/phoneapp/answer/9094888?hl=en. **Primaria.**
- **[F9]** Google. *Protect yourself with spam & scam detection on your Pixel phone — Pixel Phone Help.*
  https://support.google.com/pixelphone/answer/16704479?hl=en. **Primaria.**
- **[F10]** Google. *Protect yourself from likely scam calls — Android Help.*
  https://support.google.com/android/answer/17080867?hl=en. **Primaria.**
- **[F11]** Gemini Team, Google. *Gemini: A Family of Highly Capable Multimodal Models.* arXiv:2312.11805.
  https://arxiv.org/abs/2312.11805 (versión HTML consultada: https://arxiv.org/html/2312.11805v4).
  **Primaria.**
- **[F12]** Google. *Overview of the ML Kit GenAI APIs.* https://developers.google.com/ml-kit/genai.
  **Primaria.**
- **[F13]** Google. *Get started with Prompt API — ML Kit.*
  https://developers.google.com/ml-kit/genai/prompt/android/get-started. **Primaria.**
- **[F14]** Google. *GenAI Summarization API — ML Kit.*
  https://developers.google.com/ml-kit/genai/summarization/android. **Primaria.**
- **[F15]** Google. *Gemini Nano — Android Developers.* https://developer.android.com/ai/gemini-nano.
  **Primaria.**
- **[F16]** Google. *The latest Gemini Nano with on-device ML Kit GenAI APIs.* Android Developers Blog,
  2025-08. https://android-developers.googleblog.com/2025/08/the-latest-gemini-nano-with-on-device-ml-kit-genai-apis.html.
  **Primaria.**
- **[F17]** Google. *Gemini Nano is now available on Android via experimental access.* Android Developers
  Blog, 2024-10. https://android-developers.googleblog.com/2024/10/gemini-nano-experimental-access-available-on-android.html.
  **Primaria.**
- **[F18]** Google. *GenerationConfig — `com.google.ai.edge.aicore` (Google AI Edge SDK).*
  https://developer.android.com/ai/reference/kotlin/com/google/ai/edge/aicore/GenerationConfig.
  **Primaria.**
- **[F19]** Farafonova, L.; Geng, Y.; Abdullah, U.; Chiou, R. (Google LLC). *In-call scam detection.*
  Solicitud de patente US 2024/0388655 A1. Prioridad 2023-05-15, presentada 2024-05-13, publicada
  2024-11-21. **Estado: pendiente.** https://patents.google.com/patent/US20240388655A1/en.
  **Primaria, pero documento legal, no descripción del producto embarcado.**

### Fuentes secundarias (ninguna usada como evidencia)

No se utilizó ninguna nota de prensa, blog de terceros ni agregador como evidencia en esta ficha.
Cuando un dato no estaba en fuente primaria, se escribió "no publicado".

### Evaluaciones de terceros citadas por Google (no independientes)

- Leviathan Security Group, "funded evaluation" comparando Pixel 9 Pro, iPhone 16 Pro, Samsung S24+ y
  Xiaomi 14 Ultra, feb. 2025 — citada en [F2], **financiada por Google**, sin enlace al informe.
- Counterpoint Research — citada en [F4] sin enlace ni metodología.

---

## 12. Preguntas abiertas para el seguimiento

1. ¿Qué motor de inferencia local va a usar el prototipo, dado que las APIs públicas de Gemini Nano
   prohíben inferencia en background [F12]? → candidata a decisión en `MAPA-DECISIONES.md`.
2. ¿Se adopta ERDE (o una variante) como métrica temporal principal? → depende de [F11-9.2/9.3].
3. ¿Se adopta el esquema de dos umbrales (alerta / acción) que describe la patente de Google [F19]?
4. ¿Se replica el beep periódico como solución al problema ético de escuchar la conversación [F1]?
5. Verificar el venue/DOI de VishGPT antes de seguir citándolo.
