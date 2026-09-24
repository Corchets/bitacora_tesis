# Primera investigación — dos modelos en el teléfono

**Fecha:** 2026-09-15; recortes del 2026-09-16 (catálogo Hugging Face)  
**Sobre:** [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)  
**Estado:** recortes de trabajo de una sesión de grilling. **No cierra D09.** No es un ADR.
A ratificar por los cuatro.

Este archivo es la fuente de verdad de esta investigación. Los docs principales solo enlazan acá.

---

## En criollo

Hay que poner **dos ayudantes** en el teléfono, al mismo tiempo, y cada uno hace **una sola cosa**.

### 1. El que escucha y escribe (ASR streaming)

Imaginate los subtítulos de un dibujo animado.

- **Streaming** (lo que usamos): las letras aparecen **al mismo tiempo** que el personaje habla.
- **Por ventanas** (lo que no es el contrato): el teléfono se queda callado un rato y después tira el texto de golpe.

Usamos streaming porque hay que avisar **antes** de que la persona entregue un código. Si el teléfono espera a terminar de oír, el aviso llega tarde.

_Evitar llamar a esto “captación de texto en tiempo real”._ El nombre del módulo es **ASR streaming**.

### 2. El que lee y dice “¿esto parece una estafa?” (detector atómico)

Este ayudante responde **una sola pregunta**:  
**“¿Esto se está pareciendo a una estafa?”**  
Sale un número de riesgo que va creciendo mientras dura la llamada.

Las razones para la persona (“te apuran”, “piden el código”) las dicen **reglas**, no este modelo. Las reglas ya son el piso con el que hay que compararse.

No usamos, en el núcleo, una red que haga varias preguntas a la vez (urgencia + pedido + estafa + …). Eso ya no es un modelo de una sola tarea, y en un teléfono chico pelea con el que está escribiendo subtítulos.

---

## Recortes cerrados en esta sesión

| Recorte | Qué quedó | Qué no quedó |
|---|---|---|
| Cómo escribe | **ASR streaming** | Elegir el ID de Hub (Moonshine tiny-es vs Zipformer Kroko) cierra D09 |
| Qué analiza | **Una pregunta de riesgo.** Las explicaciones: **reglas** | Cerrar D09 ni el umbral |
| Tres tamaños de teléfono | Baja / media / alta. RAM: **256 / 512 / 1024 MB**. Hilos: **2 / 4 / 6** | Cómo se pinchan RAM e hilos en el runtime |
| Dónde corre | **Prototipo de laboratorio = PC.** **Demo Android = si hay tiempo.** iPhone = foto de “alta” | — |
| Cómo se finge el teléfono | Techo de RAM + hilos + **sin GPU**. No emulador Android como prototipo | x86 ≠ ARM |
| Cómo se desarrolla | **Una sola lógica**, config por gama | Cómo se aplican los techos (herramienta al implementar; no hay lenguaje fijado) |
| Par que se enciende primero | Config **`alta`**: Zipformer Kroko (Hub) + **RoBERTuito**. TF–IDF en las tres | Fallback DistilBETO si RTF ≥ 1 |
| De dónde se bajan | Catálogo de trabajo = **Hugging Face** (2026-09-16) | Espejos no oficiales |
| `asr` baja | **Moonshine tiny-es** (`moonshine-ai/moonshine-streaming-tiny-es`) | Vosk oficial (AlphaCepheus; no es org del Hub) |
| Hilos CPU (partida) | Baja **2** (1+1). Media **4** (3 escribir / 1 leer). Alta **6** (4 / 2) | — |
| Cuándo piensa cada uno | ASR todo el tiempo. Reglas en texto a medias. Red al cerrar el turno | — |
| Qué lee la red | **Solo el último turno.** Acumulador = máximo k=3 + histéresis, salvo incendio capa 2 | D07; hard negatives |
| Ventana de la red | **v0 = turno completo.** Piloto: completo / 5 s / 64 tokens | Qué N gana |

Whisper u otro ASR **por ventanas** puede servir después para comparar si escribe mejor. No es el contrato del módulo de captación.

---

## Por qué dos modelos, no uno solo

El teléfono tiene que **escribir** y **pensar** a la vez, como una persona que toma nota y al mismo tiempo se pregunta si la llamada es rara.

La pregunta que manda no es “¿entra el que escribe?”. Es: **¿entran los dos juntos y siguen el ritmo de la charla?**  
En números: el tiempo de los dos juntos tiene que ser menor que el audio que entra (`RTF` conjunto &lt; 1). Ver [GLOSARIO.md](../GLOSARIO.md).

---

## Candidatos (no es una elección)

Consulta de fichas públicas: **2026-09-15**. Revisión Hugging Face: **2026-09-16**. Ningún número de acá reemplaza el benchmark del piloto. Los WER publicados **no** son de llamadas argentinas.

### De dónde salieron los nombres de la primera pasada

No salieron de un único catálogo. Cada ficha se abrió en su sitio (consulta 2026-09-15):

| Candidato | Dónde se leyó (no era “todo Hugging Face”) |
|---|---|
| Vosk small ES | [alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) (oficial). **No** está en el Hub de AlphaCepheus. |
| Zipformer ES Kroko | [releases sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models) |
| Moonshine Streaming ES | [documentación Moonshine](https://moonshine-voice.readthedocs.io/en/stable/models/available-models/) |
| whisper.cpp tamaños | [ggerganov/whisper.cpp](https://huggingface.co/ggerganov/whisper.cpp) (sí Hub, pesos GGML) |
| ALBETO / DistilBETO | [repo dccuchile](https://github.com/dccuchile/lightweight-spanish-language-models) → enlaces al Hub |
| RoBERTuito | paper LREC + [pysentimiento](https://huggingface.co/pysentimiento) |

### Qué hay hoy en Hugging Face (consulta 2026-09-16)

Solo entra acá lo que se **abrió** en el Hub en esta pasada. Un espejo no oficial no cuenta como “el modelo oficial”.

#### Quien escribe (ASR)

| ID en Hugging Face | Qué es | ¿Streaming? | Notas | ¿Encaja el contrato? |
|---|---|---|---|---|
| [`csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06) | Zipformer ES (Kroko). `encoder.onnx` ~155 MB + decoder/joiner | Sí | Licencia: ver [Banafo/Kroko-ASR](https://huggingface.co/Banafo/Kroko-ASR). Copia extra: [`kouhxp/sherpa-onnx-streaming-zipformer-es-kroko`](https://huggingface.co/kouhxp/sherpa-onnx-streaming-zipformer-es-kroko). Tarball también en GitHub releases (~119 MB). | Sí, es el `asr` de media/alta del recorte |
| [`bookbot/sherpa-onnx-zipformer-streaming-robust-es-v0`](https://huggingface.co/bookbot/sherpa-onnx-zipformer-streaming-robust-es-v0) | Zipformer streaming ES, ONNX; entrenado a **fonemas** IPA (Common Voice 23 + SLR72) | Sí | No transcribe palabras de una: hay que pasar fonema → texto. | Candidato extra; no es drop-in |
| [`moonshine-ai/moonshine-streaming-tiny-es`](https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-es) | Streaming ES, **27 M**, MIT. Snapshot 2026-08-24 | Sí | WER ~6,1–6,3 en FLEURS/MLS **leído** (no teléfono argentino). Incluye OpenSLR argentino/chileno/colombiano en el set humano chico. Pseudo-etiquetas Whisper en el grueso. | **`asr` de baja** del recorte |
| [`moonshine-ai/moonshine-streaming-small-es`](https://huggingface.co/moonshine-ai/moonshine-streaming-small-es) | Streaming ES, **112,9 M**; `model.safetensors` ~452 MB | Sí | Más pesado que tiny; puede pelear el techo de 1024 MB junto a RoBERTuito | Alta / ablación |
| [`openai/whisper-tiny`](https://huggingface.co/openai/whisper-tiny) | Multilingüe, ~39 M | **No** (por ventanas) | Contrato: solo comparación de calidad | No como `asr` |
| [`openai/whisper-base`](https://huggingface.co/openai/whisper-base) | Multilingüe, ~74 M | **No** | Igual | No como `asr` |
| [`nvidia/parakeet-tdt-0.6b-v3`](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3) | 600 M, incluye español | Ficha: sobre todo *offline* / throughput | WER ES bajo en FLEURS; **no entra** en 256–1024 MB con el detector | Fuera de techos |

**Vosk `small-es-0.42`:** oficial en AlphaCepheus, Apache 2.0. En el Hub hay un zip en [`localstack/vosk-models`](https://huggingface.co/localstack/vosk-models) (espejo de terceros, no es el org de Vosk). **Fuera del recorte de trabajo** desde 2026-09-16: el `asr` de baja pasa a Moonshine tiny-es.

#### Quien lee (texto)

Estos son **modelos de lenguaje preentrenados** (fill-mask). **Ninguno viene ya entrenado para vishing.** Hay que ajustarlos (o usar TF–IDF) sobre el corpus.

| ID en Hugging Face | Qué es | Parámetros | Rol tentativo |
|---|---|---|---|
| [`dccuchile/albert-tiny-spanish`](https://huggingface.co/dccuchile/albert-tiny-spanish) | ALBETO tiny | 5 M | `detector` baja |
| [`dccuchile/albert-base-spanish`](https://huggingface.co/dccuchile/albert-base-spanish) | ALBETO base | 12 M | `detector` media |
| [`dccuchile/distilbert-base-spanish-uncased`](https://huggingface.co/dccuchile/distilbert-base-spanish-uncased) | DistilBETO (Hub 2026-09-16). El README del paper a veces escribe `distillbert` (tres l) | 67 M | fallback de alta / media |
| [`pysentimiento/robertuito-base-uncased`](https://huggingface.co/pysentimiento/robertuito-base-uncased) | RoBERTuito (también `…-cased` y `…-deacc`) | ~108 M | `detector` alta (v0) |
| [`dccuchile/bert-base-spanish-wwm-cased`](https://huggingface.co/dccuchile/bert-base-spanish-wwm-cased) | BETO | ~110 M | más pesado que DistilBETO; no hace falta si ya está RoBERTuito |

También en el Hub, **no** los metimos al recorte v0: [`dccuchile/albert-large-spanish`](https://huggingface.co/dccuchile/albert-large-spanish) (18 M), [`dccuchile/albert-xlarge-spanish`](https://huggingface.co/dccuchile/albert-xlarge-spanish) (59 M), [`dccuchile/albert-xxlarge-spanish`](https://huggingface.co/dccuchile/albert-xxlarge-spanish) (223 M; no entra con ASR en 1024 MB), [`PlanTL-GOB-ES/roberta-base-bne`](https://huggingface.co/PlanTL-GOB-ES/roberta-base-bne) (RoBERTa-base, corpus BNE de España; no es compacto ni rioplatense).

TF–IDF no vive en Hugging Face: se entrena en el laboratorio.

### ¿Hablan español?

Sí: las fichas del Hub están etiquetadas **español** (`es`). No son modelos de inglés disfrazados.

Eso **no** quiere decir “van a entender una llamada de estafa argentina”. En criollo:

| Ayudante | Qué español vimos en la ficha | Qué **no** vimos |
|---|---|---|
| Moonshine tiny-es / small-es | Entrenado para español. El set chico humano incluye OpenSLR **argentino**/chileno/colombiano **leído**. WER ~6,1–6,3 en FLEURS y MLS **leídos** | Telefonía, ruido de calle, voseo espontáneo. El grueso del entrenamiento son pseudo-etiquetas Whisper |
| Zipformer Kroko | Paquete **español** streaming en el Hub | No abrimos un WER rioplatense ni de llamada |
| ALBETO / DistilBETO / BETO | Preentrenados en **español escrito** | No vienen con vishing. No son rioplatense a propósito |
| RoBERTuito | Español **informal** (tweets) | Sigue sin saber qué es una estafa: hay que ajustarlo con el corpus |
| Whisper tiny/base | Multilingüe; **incluye** español | No es el contrato streaming |
| PlanTL BNE | Español de rastreo web de **España** | No entra al recorte v0 |

Formulación correcta: *están hechos para español; no identificamos en las fichas un WER de llamadas argentinas.* El piloto lo mide. Eso es el riesgo [R06](../gestion/REGISTRO-RIESGOS.md).

Un LLM local no entra en el núcleo: el [deep research](deep-research-report-00.md) lo descarta para cuatro meses y el mapa ya lo deja fuera.

Fuentes ASR Hub: fichas enlazadas arriba, consulta **2026-09-16**. Fuentes detector: [ALBETO y DistilBETO (repo)](https://github.com/dccuchile/lightweight-spanish-language-models), paper LREC 2022 en ACL Anthology; [RoBERTuito](https://aclanthology.org/2022.lrec-1.785). Primera pasada de sitios (no Hub): 2026-09-15.

Un banco Android publicado midió que el **mismo** Whisper Tiny corre ~50 veces más lento en whisper.cpp que en sherpa-onnx. El motor importa tanto como el modelo. Whisper queda solo como comparación de calidad, apagado en v0.

## En criollo — tres tamaños de teléfono

No es por la marca de la caja. Es por cuánta memoria y aire les dejamos a **los dos** ayudantes juntos.

| Gama | Como si fuera | Presupuesto para los dos juntos |
|---|---|---|
| **Baja** | Teléfono chico, 3–4 GB de RAM, chip simple | **256 MB** para los dos ayudantes; 2 hilos |
| **Media** | 6–8 GB | **512 MB**; 4 hilos |
| **Alta** | Teléfono caro de ahora (foto: iPhone 15/16 Pro, 8 GB) | **1024 MB**; 6 hilos |

**Alta, el ejemplo que dimos:** un iPhone moderno (clase iPhone 15 Pro / 16 Pro: **8 GB de RAM** y un chip muy fuerte). Fuentes de la RAM: comparativas públicas PhoneArena / GSMArena; consulta 2026-09-15.

### Roce con el mapa (no lo tapamos)

El [mapa](../gestion/MAPA-DECISIONES.md) y el [plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md) ponen **iOS fuera de alcance**. En esta sesión se cerró así:

- **Alta = foto de iPhone moderno** (clase 15 Pro / 16 Pro, 8 GB). No hay app iOS.
- El **prototipo de laboratorio** no es el teléfono. Es una **PC** que corre los dos ayudantes con un techo de memoria y de CPU parecido al de esa gama.
- La **demo Android** es un extra: si el tiempo alcanza, se muestra en un Android. Si no, la tesis se defiende con la PC limitada.

En criollo: no compramos tres teléfonos. En la computadora le decimos al programa “hacé de cuenta que sos un teléfono chico / mediano / caro” y miramos si los dos ayudantes siguen el ritmo de la charla.

_Evitar:_ llamar “prototipo” a la app Android. En este recorte la app es **demo**. El [plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md) habla de prototipo; acá el prototipo de laboratorio es la PC limitada, no una app instalable. Eso choca con una lectura “app en el teléfono” hasta que los cuatro lo ratifiquen.

> **Estado: propuesta sin discutir.** Encaja con el principio de [ARQUITECTURA.md](../ingenieria/ARQUITECTURA.md) (“el motor no sabe de dónde viene el audio” y se puede medir sin la app). No cierra D03 ni D09.

### Pares por gama (misma lógica, distintas variables)

En criollo: es **un solo juego** con calidad Baja / Media / Alta. Los controles no cambian. Cambian los “gráficos”: qué modelo escribe, qué modelo lee, cuánta RAM y cuántos hilos.

No se copian tres prototipos. Se cambia un **config**:

| Variable | Baja | Media | Alta (v0, se enciende primero) |
|---|---|---|---|
| `asr` | **Moonshine tiny-es** [`moonshine-ai/moonshine-streaming-tiny-es`](https://huggingface.co/moonshine-ai/moonshine-streaming-tiny-es) | Zipformer Kroko [`csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06) | **Zipformer Kroko** (mismo ID) |
| `detector` | ALBETO tiny [`dccuchile/albert-tiny-spanish`](https://huggingface.co/dccuchile/albert-tiny-spanish) | ALBETO base o DistilBETO | **RoBERTuito** [`pysentimiento/robertuito-base-uncased`](https://huggingface.co/pysentimiento/robertuito-base-uncased) |
| `baseline` | TF–IDF (siempre) | TF–IDF (siempre) | TF–IDF (siempre) |
| techo RAM (los dos juntos) | **256 MB** | **512 MB** | **1024 MB** |
| hilos (total) | **2** | **4** | **6** |
| hilos quien escribe / quien lee | **1 / 1** | **3 / 1** | **4 / 2** |
| GPU de escritorio | no | no | no |

Whisper-por-ventanas **no** va en `asr` de ninguna gama (rompe streaming). Puede ser otra variable de comparación de calidad, apagada en v0.

**Orden de desarrollo:** primero config `alta` (se ve si la lógica anda, con el par más pesado). Después se cambia la config a media y baja **sin reescribir la lógica**. Si solo corremos alta, no podemos decir que entra en un teléfono chico.

**Riesgo:** RoBERTuito (~108 M) + Zipformer Kroko (encoder ONNX ~155 MB) en CPU, sin GPU, puede no seguir el ritmo. Si el RTF conjunto ≥ 1, se cambia `detector` a DistilBETO [`dccuchile/distilbert-base-spanish-uncased`](https://huggingface.co/dccuchile/distilbert-base-spanish-uncased): misma lógica, otra config. No se duplica la lógica.

> **Estado: propuesta sin discutir.** No cierra D09: el piloto puede cambiar el ganador. Cierra *cómo se desarrolla* y *con qué disfraz se arranca*. El catálogo de bajada Hugging Face y el `asr` de baja = Moonshine tiny-es son recorte del **2026-09-16**.

Comparar las tres configs es **extensión** del [plan de trabajo](../propuesta/PLAN-DE-TRABAJO.md) como “comparación de dispositivos”; acá es comparación de **techos en la PC**.

---

## Dónde vive cada cosa (PC vs teléfono)

| Nombre en este recorte | Qué es | Obligatorio para la tesis |
|---|---|---|
| **Prototipo de laboratorio** | Los dos ayudantes en una PC, escuchando un WAV como si fuera una llamada, con un techo de RAM/CPU de la gama | Sí |
| **Demo Android** | La misma idea, en un teléfono Android de verdad | No: solo si hay tiempo |
| **Foto iPhone** | Explica qué tan “alta” es la gama alta | No se instala nada en iPhone |

“El modelo a elegir” en la PC son **los dos** ayudantes de esa gama (quien escribe + quien lee), no un solo modelo mágico.

### Cómo se finge el teléfono en la PC

En criollo: no prendemos un Android de mentira en la pantalla. Le ponemos al programa tres reglas, como cuando en un juego le bajás los gráficos:

1. **Memoria:** no puede usar más RAM que el techo de esa gama:
   baja **256 MB**, media **512 MB**, alta **1024 MB** (los dos ayudantes juntos).
2. **Hilos:** no puede usar todos los núcleos de la notebook. Partida:
   baja **2** (1 escribe / 1 lee), media **4** (3 / 1), alta **6** (4 / 2).
   El que escribe se lleva más: no para. Se ajustan si el RTF lo pide.
3. **Sin GPU de escritorio:** esas corridas van por CPU. La placa de video de la PC no cuenta: un teléfono chico no la tiene.

Misma receta, **una sola lógica**, tres techos. Se mide si siguen el ritmo de la charla (`RTF` conjunto &lt; 1). El lenguaje de programación y el motor de inferencia **no** están decididos en este recorte.

**Lo que hay que decir en la defensa:** la PC es x86 y el teléfono es ARM. El número no promete un Pixel. Promete: *con esta memoria y estos hilos, ¿entra o no?*

> **Estado: propuesta sin discutir.** No es un emulador Android. El emulador, si aparece, sería camino a la **demo**, no al prototipo de laboratorio.

### Cuándo escribe y cuándo piensa

En criollo: el que toma nota no para. El que se pregunta “¿esto es raro?” espera a que el otro **termine la frase**.

- **ASR streaming:** escribe mientras hablan.
- **Reglas:** pueden mirar el borrador (texto a medias). No pesan.
- **Red de riesgo:** piensa cuando cierra un **turno** (un silencio corto dice “listo”). Eso ya está dibujado en la arquitectura como VAD / segmentación: no es un tercer modelo de tesis; es el timbre que avisa.

Sigue siendo detección incremental: turno a turno, sin esperar a que corte la llamada. `T_A` sigue con histéresis. Ver [GLOSARIO.md](../GLOSARIO.md) y [METRICAS.md](../evaluacion/METRICAS.md).

La red **no** rumia cada sílaba: en gama baja se pelearía con el que escribe.

### Qué lee la red y quién lleva la cuenta

En criollo: la red mira **solo la última frase**. “¿Esta frase parece de estafa?” → un número.

La llamada entera la lleva un **contador** (acumulador). Para el prototipo de laboratorio:

- el contador es el **máximo de los últimos k turnos**, con **k = 3**;
- la alarma del contador suena si ese máximo se **queda alto dos veces seguidas** (`T_A` con histéresis);
- **excepción:** un **pedido crítico** detectado por reglas (capa 2) puede avisar **ya**, sin esperar el 2 ni, si el texto a medias ya lo muestra, el cierre del turno.

En criollo: si piden el código, no esperamos a que el juego sume dos puntos. Si solo te apuran o se hacen pasar, sí: tiene que mantenerse feo un rato.

_Evitar:_ promediar toda la llamada (un “decime el código” se diluye con diez minutos de saludo) y una red que lee los veinte minutos cada vez.

> **Estado: propuesta sin discutir.** El [mapa](../gestion/MAPA-DECISIONES.md) todavía lista “modelo de estado temporal vs acumulador” como no especificado. Este recorte elige este contador para el laboratorio. El achique de la ventana de texto del analizador sigue abierto (abajo).

---

## Dos caminos de aviso (prototipo)

En criollo: hay un botón de **incendio** y un botón de **esto se está poniendo raro**.

| Camino | Qué lo dispara | ¿Espera el 2 del contador? | ¿Espera el fin del turno? |
|---|---|---|---|
| **Incendio** | Reglas de **pedido crítico** (capa 2 del [manual](../datos-etica/MANUAL-ANOTACION.md): código, clave, transferencia, acceso remoto, etc.) | No | No, si ya se lee en el texto a medias |
| **Goteo** | Red de riesgo + máximo de 3 turnos | Sí, dos actualizaciones | Sí: la red piensa al cerrar el turno |

Las etiquetas de capa 2 son **propuesta** (D07 abierta). Este recorte las usa como lista de trabajo para las reglas; no congela el manual.

**Roce con las métricas:** [METRICAS.md](../evaluacion/METRICAS.md) pide histéresis para no inflar `Preventive@δ`. El camino incendio es una **excepción escrita**. En el informe hay que reportar por separado: avisos por regla crítica vs avisos por contador. Si no, parece que bajamos el umbral a escondidas.

**Riesgo (hard negative):** una llamada linda del banco también dice “código”. Las reglas sueltas van a molestar. Por eso el mapa pide hard negatives en el corpus. No está resuelto el texto exacto de cada regla.

> **Estado: propuesta sin discutir.** No cierra D07 ni el umbral numérico de la red.

---

## Desafíos abiertos (anotados, no resueltos)

### 1. Peso de intentos — recorte de prototipo, no cerrado del todo

Quedó el desdoblamiento incendio vs goteo (arriba). Sigue abierto: redacción de reglas, D07, y cómo se cuenta `T_A` cuando avisa la regla (¿es `T_A` igual?).

### 2. Cuánto se puede achicar lo que ve el analizador

**Contrato v0:** la red ve el **turno entero**.

**Experimento del piloto (no es el contrato):** repetir la misma corrida recortando lo que entra a la red y anotar si se pierde el delito.

| Ventana | Qué sería | Para qué |
|---|---|---|
| Turno completo | v0 | piso |
| Últimos **5 s** de texto del turno | recorte temporal | ¿alcanza lo último que dijo? |
| Últimos **64 tokens** | recorte de modelo chico | ¿entra en gama baja sin perder “código”? |

Qué hay que anotar en cada fila: latencia, RAM, RTF conjunto, y **recall de términos críticos** (código, token, transferencia). Si achicamos y perdemos “código”, no sirve. Las reglas siguen mirando el texto a medias, así que el camino incendio no depende de esta tabla.

> **Estado: propuesta sin discutir.** N = 5 s y 64 tokens son números de partida para medir, no magia. Si el piloto pide otros N, se cambian con evidencia. “64 tokens” nombra un recorte de texto, no un runtime.

---

## Qué falta (siguiente paso)

- Spike de laboratorio: issue **[#28](https://github.com/Corchets/bitacora_tesis/issues/28)**.
- Cómo se **aplican** los techos de RAM e hilos de forma medible y repetible. La herramienta se elige al implementar; este recorte no fija lenguaje ni runtime.
- Redacción de reglas de capa 2 (D07) y hard negatives.
- Elegir el motor concreto con un piloto: WER, palabras críticas, latencia, memoria. Eso sí cierra D09.
- D05 y D07 siguen bloqueando la elección final.

Esta ola de grilling ya tiene un contrato de laboratorio. No reemplaza el ADR ni el benchmark.

---

## Relación con el resto del repo

- [ARQUITECTURA.md](../ingenieria/ARQUITECTURA.md) — el diagrama sigue siendo borrador; el recorte de streaming y detector atómico vive acá.
- [MAPA-DECISIONES.md D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector) — D09 abierta; este archivo es el recorte de trabajo.
- Spike de laboratorio: [issue #28](https://github.com/Corchets/bitacora_tesis/issues/28). Relacionados: #19 (WAV→ASR), #23 (contexto temporal), #27 (NLP local; no es LLM en el núcleo).
- [METRICAS.md](../evaluacion/METRICAS.md) — `T_A`, histéresis, `RTF`.
- [deep-research-report-00.md](deep-research-report-00.md) — sugiere; este archivo no lo convierte en decisión de equipo.
