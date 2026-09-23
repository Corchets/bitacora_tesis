# Primera investigación — dos ayudantes en el teléfono

**Fecha:** 2026-09-15; recortes del 2026-09-16 (catálogo Hugging Face) y 2026-09-17 (`detector` = TF–IDF)
**Sobre:** [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)
**Estado:** apuntes de trabajo de una charla de equipo. **No cierra D09.** No es un ADR.
Lo tienen que revisar los cuatro.

Este archivo es donde vive esta investigación. Los otros docs solo lo enlazan.

---

## La idea en dos frases

Queremos meter **dos ayudantes** en el teléfono, trabajando juntos. Cada uno hace **una sola cosa**.

### 1. El que escucha y escribe

Pensá en los subtítulos de un dibujito.

- **Streaming (lo que queremos):** las palabras aparecen **mientras** la persona habla.
- **Por pedazos (lo que no queremos):** el teléfono se queda callado y después escupe todo el texto de golpe.

Necesitamos streaming porque hay que avisar **antes** de que la víctima pase un código. Si esperamos a que termine de hablar, llegamos tarde.

El módulo se llama **ASR streaming**. No lo llamemos de otra forma.

### 2. El que lee y pregunta “¿esto huele a estafa?”

Este ayudante responde una sola pregunta:

> **“¿Esto se está pareciendo a una estafa?”**

Devuelve un numerito de riesgo que sube a medida que avanza la llamada.

Las explicaciones para la persona (“te están apurando”, “te piden el código”) las dan **las reglas**, no este modelo. Las reglas son el piso contra el que nos comparamos.

No ponemos un modelo que haga todo junto (urgencia + pedido + estafa + …). Eso pesa más y se pelea con el que escribe subtítulos en un teléfono chico.

---

## Lo que ya dejamos anotado

| Tema | Qué quedó | Qué falta |
|---|---|---|
| Cómo escribe | **ASR streaming** | Elegir el modelo final (Moonshine tiny-es o Zipformer Kroko). Eso cierra D09 |
| Qué analiza | **Una pregunta de riesgo.** Las explicaciones las dan **las reglas** | Cerrar D09 y el umbral |
| Tres tamaños de teléfono | Baja / media / alta. Memoria: **256 / 512 / 1024 MB**. Hilos: **2 / 4 / 6** | Cómo se limita eso en el programa |
| Dónde se prueba | **Laboratorio = PC.** **Demo en Android = solo si hay tiempo.** iPhone = solo foto de “alta” | — |
| Cómo fingimos el teléfono | Techo de memoria + hilos + **sin placa de video**. Sin emulador Android | La PC es x86 y el teléfono es ARM |
| Cómo programamos | **Un solo programa**, con una config por gama | Con qué herramienta se limita (no hay lenguaje elegido) |
| Con qué arrancamos | Config **`alta`**: Zipformer Kroko + **TF–IDF**. Reglas en las tres | ALBETO, DistilBETO, RoBERTuito quedan afuera |
| De dónde se bajan | Catálogo de trabajo = **Hugging Face** (2026-09-16) | No valen copias de desconocidos |
| `asr` de baja | **Moonshine tiny-es** (`moonshine-ai/moonshine-streaming-tiny-es`) | Vosk oficial no está en el Hub |
| Hilos para arrancar | Baja **2** (1+1). Media **4** (3 / 1). Alta **6** (4 / 2) | — |
| Cuándo trabaja cada uno | El que escribe, todo el tiempo. Las reglas miran el borrador. El que lee, al cerrar el turno | — |
| Qué lee el que lee | **Solo la última frase.** La llamada la lleva un contador: máximo de 3 turnos + esperar confirmación, salvo incendio de capa 2 | D07; hard negatives |
| Cuánto texto mira | **v0 = la frase entera.** En el piloto probamos: entera / últimos 5 s / últimos 64 pedacitos | Cuál recorte gana |

Whisper u otro que trabaja por pedazos puede servir después para comparar calidad. No es el módulo de escucha.

---

## Por qué dos y no uno solo

El teléfono tiene que **escribir** y **pensar** al mismo tiempo. Como vos cuando tomás apuntes y a la vez pensás “esto me suena raro”.

La pregunta importante no es “¿entra el que escribe?”. Es: **¿entran los dos juntos y le siguen el ritmo a la charla?**

En números: los dos juntos tienen que tardar menos de lo que dura el audio (`RTF` menor a 1). Ver [GLOSARIO.md](../GLOSARIO.md).

---

## Modelos mirados (no es una elección)

Miramos fichas públicas el **2026-09-15** y el Hub el **2026-09-16**. Ningún número de acá reemplaza nuestra propia prueba. Los WER publicados **no** son de llamadas argentinas.

### De dónde salió cada nombre

No salieron de un solo lugar. Cada ficha se abrió en su página (2026-09-15):

| Nombre | Dónde se leyó |
|---|---|
| Vosk small ES | [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) (página oficial). **No** está en el Hub de AlphaCepheus |
| Zipformer ES Kroko | [releases de sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models) |
| Moonshine Streaming ES | [documentación de Moonshine](https://moonshine-voice.readthedocs.io/en/stable/models/available-models/) |

### Lo que hay hoy en Hugging Face (2026-09-16)

Acá solo entra lo que **abrimos** en el Hub. Una copia subida por un desconocido no cuenta como “el modelo oficial”.

#### El que escribe (ASR)

| ID en Hugging Face | Qué es | ¿Escribe mientras hablan? | Notas en criollo | ¿Nos sirve? |
|---|---|---|---|---|
| [`csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06) | Zipformer en español (Kroko). El `encoder.onnx` pesa ~155 MB, más otras piecitas | Sí | Licencia: ver [Banafo/Kroko-ASR](https://huggingface.co/Banafo/Kroko-ASR). Hay otra copia en [`kouhxp/sherpa-onnx-streaming-zipformer-es-kroko`](https://huggingface.co/kouhxp/sherpa-onnx-streaming-zipformer-es-kroko) | **`asr` de media y alta** |
| [`moonshine-ai/moonshine-streaming-tiny-es`](https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-es) | Chiquito, en español, **27 M**, licencia MIT. Foto del 2026-08-24 | Sí | Dice equivocarse ~6 de cada 100 palabras en audio **leído** (no en llamadas). Tiene un poquito de audio argentino/chileno/colombiano **leído**. Lo demás se etiquetó con otro modelo, sin humanos | **`asr` de baja** |

**Vosk `small-es-0.42`:** vive en AlphaCepheus, licencia Apache 2.0. En el Hub hay una copia en [`localstack/vosk-models`](https://huggingface.co/localstack/vosk-models) subida por terceros, no por Vosk. **Queda afuera** desde el 2026-09-16: en baja usamos Moonshine tiny-es.

#### El que lee (texto)

**TF–IDF + reglas.** No se baja ningún transformer. Se aprende en el laboratorio con nuestro corpus. Las reglas explican el porqué (“te apuran”, “te piden el código”).

ALBETO, DistilBETO y RoBERTuito **no** entran en este recorte (2026-09-17).

### ¿Hablan español?

El que escribe, sí: las fichas dicen **español** (`es`). No son modelos de inglés disfrazados.

Pero ojo, eso **no** quiere decir “van a entender una llamada de estafa argentina”. En criollo:

| Ayudante | Qué español sí vimos | Qué **no** vimos |
|---|---|---|
| Moonshine tiny-es | Hecho para español. Tiene un poco de audio argentino **leído**. Se equivoca ~6 de cada 100 palabras en audio leído | Llamadas por teléfono, ruido de calle, voseo de todos los días. Gran parte se entrenó con etiquetas automáticas |
| Zipformer Kroko | Paquete **español** en el Hub | Ninguna prueba en llamadas rioplatenses |
| TF–IDF | Aprende el español **de nuestro corpus** | Todavía no hay corpus, así que tampoco hay números |

Dicho bien: *están hechos para español; no encontramos en las fichas ninguna prueba en llamadas argentinas.* Eso lo mide nuestro piloto. Es el riesgo [R06](../gestion/REGISTRO-RIESGOS.md).

Un modelo grande local no entra: el [deep research](../../deep-research-report.md) lo descarta para cuatro meses y el mapa ya lo deja afuera.

Fuentes del ASR: fichas de arriba, vistas el **2026-09-16**. Primera pasada de páginas (no Hub): 2026-09-15.

Whisper u otro que trabaja por pedazos puede servir después para comparar calidad. No es el contrato; en v0 queda apagado. El programa que lo corre importa tanto como el modelo.

---

## Tres tamaños de teléfono

No es la marca de la caja. Es cuánta memoria y aire les dejamos a **los dos** ayudantes juntos.

| Gama | Como si fuera | Presupuesto para los dos juntos |
|---|---|---|
| **Baja** | Teléfono chico, 3–4 GB de memoria, chip simple | **256 MB**; 2 hilos |
| **Media** | 6–8 GB | **512 MB**; 4 hilos |
| **Alta** | Teléfono caro de ahora (foto: iPhone 15/16 Pro, 8 GB) | **1024 MB**; 6 hilos |

**El ejemplo de alta:** un iPhone moderno (tipo iPhone 15 Pro / 16 Pro: **8 GB** y un chip muy fuerte). Fuentes de la memoria: comparativas públicas PhoneArena / GSMArena; visto el 2026-09-15.

### Un choque con el mapa (no lo escondemos)

El [mapa](../gestion/MAPA-DECISIONES.md) y el [plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md) dejan **iOS afuera**. En esta charla quedó así:

- **Alta = foto de un iPhone moderno**. No hay app para iPhone.
- El **laboratorio** no es el teléfono. Es una **PC** que corre los dos ayudantes con un techo de memoria y CPU parecido al de esa gama.
- La **demo en Android** es un extra: si da el tiempo, se muestra en un Android. Si no, la tesis se defiende con la PC limitada.

En criollo: no compramos tres teléfonos. En la compu le decimos al programa “hacé de cuenta que sos un teléfono chico / mediano / caro” y vemos si los dos ayudantes le siguen el ritmo a la charla.

_Ojo:_ no llamemos “prototipo” a la app de Android. Acá la app es **demo**. El [plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md) habla de prototipo; acá el prototipo es la PC limitada, no una app instalable. Eso choca con leerlo como “app en el teléfono” hasta que los cuatro lo confirmen.

> **Estado: propuesta sin discutir.** Va con la idea de [ARQUITECTURA.md](../ingenieria/ARQUITECTURA.md) (“el motor no sabe de dónde viene el audio” y se puede medir sin la app). No cierra D03 ni D09.

### La config por gama (un solo programa, tres disfraces)

En criollo: es **un solo juego** con calidad Baja / Media / Alta. Los botones no cambian. Cambian los “gráficos”: quién escribe, quién lee, cuánta memoria y cuántos hilos.

No hacemos tres programas. Cambiamos un **config**:

| Variable | Baja | Media | Alta (v0, se prende primero) |
|---|---|---|---|
| `asr` | **Moonshine tiny-es** [`moonshine-ai/moonshine-streaming-tiny-es`](https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-es) | Zipformer Kroko [`csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06) | **Zipformer Kroko** (el mismo) |
| `detector` | TF–IDF | TF–IDF | **TF–IDF** |
| Techo de memoria (los dos juntos) | **256 MB** | **512 MB** | **1024 MB** |
| Hilos (total) | **2** | **4** | **6** |
| Hilos del que escribe / del que lee | **1 / 1** | **3 / 1** | **4 / 2** |
| Placa de video de escritorio | no | no | no |

Whisper por pedazos **no** va en `asr` de ninguna gama (rompe el streaming). Puede ser otra prueba de calidad, apagada en v0. Las **reglas** (capa 2) van en las tres gamas; no son un modelo de Hugging Face.

**Orden de trabajo:** primero la config `alta` (vemos si la lógica anda con el ASR más pesado). Después pasamos a media y baja **sin reescribir el programa**. Si solo probamos alta, no podemos decir que entra en un teléfono chico.

**Riesgo:** Zipformer Kroko (encoder ONNX ~155 MB) en CPU, sin placa de video, puede no seguir el ritmo. El TF–IDF pesa poco; si vamos tarde, la culpa es del que escribe.

> **Estado: propuesta sin discutir.** No cierra D09: el piloto puede cambiar el ganador. Solo deja fijo *cómo programamos* y *con qué disfraz arrancamos*. Catálogo del Hub del 2026-09-16; `detector` = TF–IDF (sin ALBETO, DistilBETO ni RoBERTuito): **2026-09-17**.

Comparar las tres configs es **extensión** del [plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md) como “comparación de dispositivos”; acá es comparación de **techos en la PC**.

---

## Dónde vive cada cosa (PC vs teléfono)

| Nombre en este recorte | Qué es | ¿Hace falta para la tesis? |
|---|---|---|
| **Prototipo de laboratorio** | Los dos ayudantes en una PC, escuchando un audio como si fuera una llamada, con techo de memoria y CPU de la gama | Sí |
| **Demo Android** | La misma idea, en un teléfono Android de verdad | No: solo si hay tiempo |
| **Foto iPhone** | Muestra qué tan “alta” es la gama alta | No se instala nada en iPhone |

“El modelo a elegir” en la PC son **los dos** ayudantes de esa gama (el que escribe + el que lee), no un modelo mágico solo.

### Cómo fingimos el teléfono en la PC

En criollo: no prendemos un Android de mentira en la pantalla. Le ponemos al programa tres reglas, como cuando en un juego le bajás los gráficos:

1. **Memoria:** no puede usar más memoria que el techo de esa gama:
   baja **256 MB**, media **512 MB**, alta **1024 MB** (los dos ayudantes juntos).
2. **Hilos:** no puede usar todos los núcleos de la compu. Reparto:
   baja **2** (1 escribe / 1 lee), media **4** (3 / 1), alta **6** (4 / 2).
   El que escribe se lleva más porque no para. Se ajusta si vamos tarde.
3. **Sin placa de video de escritorio:** esas pruebas van por CPU. La placa de la PC no cuenta: un teléfono chico no la tiene.

Misma receta, **un solo programa**, tres techos. Medimos si le siguen el ritmo a la charla (`RTF` menor a 1). El lenguaje de programación y el programa que corre los modelos **todavía no se eligen**.

**Lo que hay que decir en la defensa:** la PC es x86 y el teléfono es ARM. El número no promete un Pixel. Promete: *con esta memoria y estos hilos, ¿entra o no?*

> **Estado: propuesta sin discutir.** No es un emulador Android. El emulador, si aparece, es camino a la **demo**, no al laboratorio.

### Cuándo escribe y cuándo piensa

En criollo: el que toma nota no para. El que se pregunta “¿esto es raro?” espera a que el otro **termine la frase**.

- **El que escribe:** escribe mientras hablan.
- **Reglas:** pueden mirar el borrador (texto a medias). No pesan nada.
- **El que lee:** piensa cuando se cierra un **turno** (un silencio corto dice “listo”). Eso ya está dibujado en la arquitectura como VAD / segmentación: no es un tercer modelo de tesis; es el timbre que avisa.

Sigue siendo detección paso a paso: turno a turno, sin esperar a que corten. `T_A` sigue esperando confirmación. Ver [GLOSARIO.md](../GLOSARIO.md) y [METRICAS.md](../evaluacion/METRICAS.md).

El que lee **no** piensa en cada sílaba: en gama baja se pelearía con el que escribe.

### Qué lee y quién lleva la cuenta

En criollo: el que lee mira **solo la última frase**. “¿Esta frase parece de estafa?” → un numerito.

La llamada entera la lleva un **contador**. Para el laboratorio:

- el contador es el **máximo de las últimas 3 frases**;
- la alarma suena si ese máximo se **queda alto dos veces seguidas** (`T_A` con espera);
- **excepción:** un **pedido peligroso** visto por reglas (capa 2) puede avisar **ya**, sin esperar, incluso si el texto todavía está a medias.

En criollo: si piden el código, no esperamos a juntar dos puntos. Si solo apuran o se hacen pasar por otro, sí: tiene que seguir feo un rato.

_Evitar:_ promediar toda la llamada (un “pasame el código” se pierde entre diez minutos de hola y chau) y un lector que relee los veinte minutos cada vez.

> **Estado: propuesta sin discutir.** El [mapa](../gestion/MAPA-DECISIONES.md) todavía dice “modelo con memoria o contador” como no resuelto. Este recorte elige este contador para el laboratorio. Probar con menos texto sigue abierto (abajo).

---

## Dos caminos de aviso

En criollo: hay un botón de **incendio** y un botón de **esto se está poniendo raro**.

| Camino       | Qué lo prende                                                                                                                               | ¿Espera la confirmación? | ¿Espera el fin de la frase?     |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------ | ------------------------------- |
| **Incendio** | Reglas de **pedido peligroso** (capa 2 del [manual](../datos-etica/MANUAL-ANOTACION.md): código, clave, transferencia, acceso remoto, etc.) | No                       | No, si ya se lee en el borrador |
| **Goteo**    | El que lee + máximo de 3 frases                                                                                                             | Sí, dos veces seguidas   | Sí: piensa al cerrar la frase   |

Las etiquetas de capa 2 son **propuesta** (D07 abierta). Este recorte las usa como lista de trabajo; no cierra el manual.

**Choque con las métricas:** [METRICAS.md](../evaluacion/METRICAS.md) pide esperar para no inflar `Preventive@δ`. El camino incendio es una **excepción escrita**. En el informe hay que contar por separado: avisos por regla peligrosa vs avisos por contador. Si no, parece que bajamos el umbral a escondidas.

**Riesgo (hard negative):** una llamada buena del banco también dice “código”. Las reglas solas van a molestar. Por eso el mapa pide llamadas buenas tramposas en el corpus. Todavía no está escrita la letra chica de cada regla.

> **Estado: propuesta sin discutir.** No cierra D07 ni el número del umbral.

---

## Dudas anotadas (no resueltas)

### 1. Cuánto pesa cada intento

Quedó el doble camino incendio vs goteo (arriba). Sigue abierto: cómo se escriben las reglas, D07, y cómo se cuenta `T_A` cuando avisa la regla (¿vale igual?).

### 2. Cuánto podemos achicar lo que lee

**Contrato v0:** el que lee mira la **frase entera**.

**Prueba del piloto (no es el contrato):** repetir la misma prueba dándole cada vez menos texto y anotar si se nos escapa el delito.

| Ventana | Qué sería | Para qué |
|---|---|---|
| Frase entera | v0 | piso |
| Últimos **5 s** de texto | recorte por tiempo | ¿alcanza con lo último que dijo? |
| Últimos **64 pedacitos** | recorte de modelo chico | ¿entra en gama baja sin perder “código”? |

Qué anotar en cada fila: demora, memoria, RTF de los dos juntos, y **cuántas palabras peligrosas se salvan** (código, token, transferencia). Si achicamos y perdemos “código”, no sirve. Las reglas siguen mirando el borrador, así que el camino incendio no depende de esta tabla.

> **Estado: propuesta sin discutir.** 5 s y 64 pedacitos son números para arrancar a medir, no magia. Si el piloto pide otros números, se cambian con evidencia. “64 pedacitos” es un recorte de texto, no un programa.

---

## Qué falta (próximo paso)

- Prueba de laboratorio: issue **[#29](https://github.com/Corchets/bitacora_tesis/issues/29)** (hijo de [#28](https://github.com/Corchets/bitacora_tesis/issues/28); recorte TF–IDF del 2026-09-17).
- Cómo se **ponen** los techos de memoria e hilos de forma que cualquiera los repita. La herramienta se elige al programar; este recorte no fija lenguaje.
- Escribir las reglas de capa 2 (D07) y las llamadas buenas tramposas.
- Elegir el modelo final con un piloto: errores, palabras clave, demora, memoria. Eso sí cierra D09.
- D05 y D07 siguen trabando la elección final.

Esta charla ya dejó un contrato de laboratorio. No reemplaza el ADR ni la prueba real.

---

## Relación con el resto del repo

- [ARQUITECTURA.md](../ingenieria/ARQUITECTURA.md) — el dibujo sigue en borrador; el recorte de streaming y del que lee vive acá.
- [MAPA-DECISIONES.md D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) — D09 abierta; este archivo es el apunte de trabajo.
- Prueba de laboratorio: [issue #29](https://github.com/Corchets/bitacora_tesis/issues/29) (hijo de [#28](https://github.com/Corchets/bitacora_tesis/issues/28)). Relacionados: #19 (audio → texto), #23 (contexto en el tiempo), #27 (texto local; no es un modelo grande).
- [METRICAS.md](../evaluacion/METRICAS.md) — `T_A`, espera, `RTF`.
- [deep-research-report.md](../../deep-research-report.md) — sugiere; este archivo no lo convierte en decisión del equipo.
