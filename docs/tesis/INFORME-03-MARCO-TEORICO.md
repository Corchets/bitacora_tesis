# Capítulo 3. Marco teórico

Este capítulo presenta los conceptos que hacen falta para entender el resto del informe. Sigue el orden en que la
información atraviesa el sistema: primero el fenómeno que se quiere detectar, después el reconocimiento del habla, la
clasificación del texto y los modelos de lenguaje, y por último cómo se evalúa una detección que tiene que ocurrir a
tiempo. Cierra con los sistemas existentes, el marco normativo y el espacio que queda para este trabajo.

## 3.1. Ingeniería social y vishing

La ingeniería social es el conjunto de técnicas que buscan que una persona haga algo o entregue información en contra
de su propio interés, apoyándose en mecanismos de persuasión antes que en fallas técnicas. El vishing es su variante
por llamada de voz. Triantafyllopoulos et al. (2025) publicaron el primer relevamiento del vishing como problema de
procesamiento del habla. Señalan dos condiciones que este trabajo adopta: hay muy pocos datos públicos, y la detección
y la intervención deben diseñarse juntas, porque una detección que llega tarde no sirve.

En una llamada de vishing la manipulación se construye por etapas. Primero, quien llama establece una identidad
creíble («le hablo del área de seguridad de su banco»). Después plantea un problema («detectamos un movimiento
extraño», «su cuenta va a quedar bloqueada»). Luego genera urgencia o apela a la autoridad, y aísla a la persona
(«no corte», «no hable con nadie»). Al final aparece el pedido. No todas las llamadas recorren todas las etapas ni en
ese orden, pero la estructura ayuda a distinguir tres tipos de señales:

- **Maniobras:** suplantación de una entidad o de un familiar, urgencia, amenaza, aislamiento, oferta de un beneficio.
- **Pedidos de alto riesgo:** un código de verificación, una clave o un PIN, los datos de una tarjeta, una
  transferencia o una entrega de dinero, la instalación de una aplicación de acceso remoto, una operación guiada en la
  aplicación del banco.
- **Cumplimiento:** el momento en que la persona entrega lo que le pidieron.

Esta distinción tiene consecuencias para la detección. Una llamada legítima del banco puede mencionar «código» o
«transferencia» sin pedir nada riesgoso, un familiar puede hablar de dinero y un servicio de atención real puede
pedir el nombre y el DNI. Un detector útil tiene que distinguir *mencionar* algo sensible de *pedirlo*. Y como el
aviso tiene que llegar antes de la entrega, conviene que reconozca hacia dónde va la conversación antes de que el
pedido se formule. Hay además estafas que terminan sin un pedido explícito, porque la persona corta o la llamada se
interrumpe: también cuentan como estafas, aunque no haya un pedido contra el cual medir la anticipación.

## 3.2. Modalidades en la Argentina

Las fuentes oficiales argentinas describen varias familias de vishing. La Tabla 3.1 las resume con el pedido típico de
cada una y la fuente que la documenta.

| Familia | Pedido típico | Fuente |
|---|---|---|
| Falso empleado del banco | Código recibido por SMS, clave, transferencia «a una cuenta segura» | BCRA (s. f.-a) |
| Cambio de clave guiado | Cambiar la clave o habilitar un dispositivo siguiendo instrucciones por teléfono | Ministerio de Seguridad de la Nación (s. f.) |
| Falso soporte técnico | Usuario y contraseña, o compartir la pantalla | BCRA (s. f.-a); Banco Galicia (s. f.) |
| Código de WhatsApp | Dictar el código de activación de la cuenta | Gobierno de la Nación Argentina (2022) |
| Falso organismo previsional | Datos personales y bancarios para «cobrar un beneficio» | ANSES (s. f.) |
| Falso premio | Datos personales o de la tarjeta para «retirar el premio» | BCRA (s. f.-b) |
| Familiar en apuros | Una transferencia urgente | Ministerio Público Fiscal de la Nación (s. f.) |
| Falso cambio de billetes | Entregar dinero en efectivo a un supuesto empleado | Ministerio Público Fiscal de la Nación (s. f.) |

*Tabla 3.1. Familias de vishing documentadas por fuentes argentinas.*

Las fuentes respaldan que la modalidad existe y cuál es la conducta segura. No dicen con qué frecuencia ocurre cada
una ni describen conversaciones completas.

## 3.3. Reconocimiento automático del habla

Un sistema de reconocimiento automático del habla (ASR, por *automatic speech recognition*) convierte audio en texto.
Para este trabajo importan tres aspectos.

**Transcripción continua o por segmentos.** Un modelo de transcripción continua (*streaming*) entrega texto mientras
la persona habla y corrige los resultados parciales a medida que escucha más. Un modelo por segmentos espera a que
termine un fragmento de habla, delimitado por un silencio, y lo transcribe completo. El primero da texto antes; el
segundo suele transcribir mejor, porque ve el fragmento entero. Entre los modelos actuales, los transductores
procesan el audio de manera eficiente y predicen a la vez el texto y su duración (Xu et al., 2023). Los modelos de
codificador y decodificador, como Whisper (Radford et al., 2023), trabajan sobre ventanas de audio de duración fija y
no están pensados para la transcripción continua.

**Detección de actividad de voz.** Para delimitar los fragmentos hay que decidir qué es voz y qué es silencio o
ruido. La forma más simple es un umbral de energía: si la energía de la señal queda por debajo de un valor durante un
tiempo, el fragmento terminó. Un detector de actividad de voz (VAD, por *voice activity detection*) entrenado con
redes neuronales distingue mejor la voz del ruido de fondo, aunque puede partir las frases en lugares inconvenientes.

**La tasa de error por palabra no alcanza.** La medida estándar de calidad es la tasa de error por palabra (WER, por
*word error rate*): la cantidad de palabras sustituidas, eliminadas e insertadas, dividida por la cantidad de palabras
de la referencia. El WER trata a todos los errores por igual, pero su efecto sobre un sistema posterior no es igual.
Balagopalan et al. (2019) muestran que las eliminaciones dañan al clasificador posterior más que las sustituciones y
las inserciones, y Zhou et al. (2022) cuantifican cómo los errores de transcripción desvían el significado en la
detección de intenciones. Para un detector de vishing, perder la palabra «código» o una cifra dictada pesa mucho más
que escribir mal un artículo. Por eso, además del WER, conviene mirar si se conservan los términos críticos.

## 3.4. Clasificación de texto

Decidir si una conversación transcripta es una estafa es un problema de clasificación de texto. Las técnicas
disponibles van de lo más simple a lo más general.

**Reglas de palabras clave.** Una lista de términos («código», «clave», «transferí») que disparan una alerta cuando
aparecen. Son rápidas, transparentes y no necesitan datos de entrenamiento. Su límite es conocido: no distinguen
mencionar de pedir, así que avisan también en las conversaciones legítimas que usan esas palabras.

**Clasificadores supervisados.** Aprenden de ejemplos etiquetados. Los clásicos representan el texto como un vector de
frecuencias de palabras ponderadas (TF-IDF) y lo separan con un modelo lineal. Necesitan muchos ejemplos y se apoyan
en el vocabulario más que en el sentido.

**Codificadores preentrenados.** Los modelos de la familia Transformer (Vaswani et al., 2017) que se entrenan para
representar texto, como BERT (Devlin et al., 2019) y RoBERTa (Liu et al., 2019), producen representaciones que
capturan el contexto de cada palabra. Sobre esas representaciones se entrena un clasificador con pocos ejemplos, o se
ajusta el modelo completo. Para el español existen variantes como RoBERTuito, entrenada con texto de redes sociales
(Pérez et al., 2022).

**Clasificación sin ejemplos (*zero-shot*).** Un modelo entrenado para decidir si un texto implica a otro puede
clasificar sin ejemplos de la tarea: se le pregunta si la conversación implica una frase como «esta llamada es una
estafa» (Yin et al., 2019). Una variante usa modelos que puntúan qué tan relacionados están dos textos. Estas técnicas
miden afinidad entre textos, y la afinidad temática no es lo mismo que la intención.

**Modelos de lenguaje generativos.** Un modelo de lenguaje general recibe una instrucción en lenguaje natural (el
*prompt*) con la conversación y responde con la clasificación. No necesita entrenamiento para la tarea, puede razonar
sobre la conversación completa y puede dar el motivo de su decisión. Su costo es mucho mayor que el de las técnicas
anteriores. La sección siguiente describe sus propiedades.

## 3.5. Modelos de lenguaje y su ejecución en el dispositivo

Un modelo de lenguaje es una red neuronal entrenada para predecir el siguiente fragmento de texto, llamado *token*.
Los modelos grandes, de decenas o cientos de miles de millones de parámetros, corren en centros de datos. Los modelos
chicos (SLM, por *small language models*), de uno a unos pocos miles de millones, pueden correr en una computadora
personal o en un teléfono reciente. Algunos se diseñan específicamente para eso (Gemma Team, Google DeepMind, 2026).

**Cuantización.** Para que un modelo entre en la memoria de un teléfono, sus pesos se representan con menos bits, por
ejemplo 4 en lugar de 16. El modelo ocupa una fracción de la memoria original y corre más rápido, a cambio de una
pérdida de calidad acotada (Dettmers et al., 2023).

**El costo de leer y el de escribir.** Un modelo procesa la entrada completa en paralelo, pero genera la respuesta de a
un token por vez, y cada token generado cuesta tiempo. Leer una conversación larga es relativamente rápido; escribir un
párrafo de explicación es lento. Pedirle al modelo un motivo detallado en cada consulta multiplica la demora.

**Caché del prefijo.** Mientras procesa la entrada, el modelo calcula estados intermedios por cada token. Si dos
consultas seguidas comparten el comienzo, como una instrucción fija seguida de una conversación que solo crece, esos
estados se pueden guardar y reutilizar, y solo se procesa lo nuevo. En un detector que consulta al modelo a medida que
avanza la llamada, esto reduce mucho el trabajo por consulta.

**Sensibilidad a la instrucción.** Con una instrucción y un formato de salida definido, un modelo general clasifica sin
entrenamiento. Pero la calidad depende de cómo se escribe la instrucción: cambios chicos de redacción o de formato
mueven el resultado (Sclar et al., 2024), y una evaluación con una sola instrucción puede llevar a conclusiones que no
se sostienen con otra (Mizrahi et al., 2024). Ajustar la instrucción mirando los errores en un conjunto de casos
tiende a sobreajustarla a esos casos.

**Salida estructurada.** Se le puede pedir al modelo que responda en un formato fijo, por ejemplo un objeto JSON con
campos definidos. Eso permite leer la respuesta de manera automática. El orden de los campos importa: el modelo
escribe en orden, y lo que escribe primero condiciona lo que escribe después.

**El número que escribe el modelo no es una probabilidad.** Si se le pide un riesgo entre 0 y 1, el modelo escribe un
número como texto. Ese número no está calibrado como una probabilidad (Xiong et al., 2024). Una alternativa es leer
directamente la probabilidad que el modelo asigna a un token de respuesta, como «sí» o «no». Sin un ajuste específico,
esa probabilidad tampoco está garantizada como buena medida.

**Ajuste fino.** Un modelo se puede especializar con ejemplos de la tarea. LoRA entrena solo matrices de bajo rango
agregadas a las capas del modelo, lo que reduce mucho la memoria necesaria (Hu et al., 2022), y QLoRA lo hace sobre un
modelo cuantizado (Dettmers et al., 2023). Sim y Kim (2025) ajustan con LoRA un modelo de 8 mil millones de parámetros
para detectar vishing, y muestran que un clasificador convencional cae del 98,5 % al 56,2 % de exactitud frente a
llamadas legítimas diseñadas para parecer estafas, una caída que los criterios explícitos en la instrucción mitigan.

## 3.6. Clasificación temprana

Detectar una estafa al final de la llamada es fácil e inútil. El problema es de **clasificación temprana**: decidir
con información parcial, equilibrando exactitud y anticipación. Cuanto antes se decide, menos evidencia hay y más
probable es equivocarse; cuanto más se espera, más tarde llega el aviso.

Losada y Crestani (2016) y Losada et al. (2017) proponen para la detección temprana de riesgo en textos una medida,
ERDE, que penaliza tanto el error como el retraso, contado en cantidad de mensajes leídos. Mori et al. (2018)
formalizan el compromiso entre exactitud y precocidad en series temporales, midiendo la precocidad como la fracción
de la serie observada. Ninguna de las dos se traslada directo a una llamada. La primera penaliza el retraso desde el
comienzo, aunque los primeros turnos sean saludos. La segunda necesita conocer la duración total, que durante una
llamada no se conoce.

Para una llamada importa otra cosa: si el aviso llega antes de que la persona cumpla. Por eso este trabajo mide la
anticipación respecto de dos eventos de la propia conversación, el primer pedido riesgoso y el primer cumplimiento, en
lugar de una curva abstracta sobre la cantidad de turnos. Las definiciones están en el capítulo 6.

Hay antecedentes directos de esta formulación. Shen et al. (2025) estudian la detección de estafas telefónicas en
tiempo real con un modelo de lenguaje que evalúa la conversación a medida que avanza, y muestran el compromiso entre
detectar más y avisar a tiempo: permitir una respuesta de «incierto» sube la precisión pero atrasa el aviso. Otros
sistemas puntúan cada oración y suavizan los puntajes en el tiempo antes de compararlos con un umbral (SentinelEdge,
2026).

## 3.7. Falsas alarmas y tasa base

Axelsson (2000) mostró, para la detección de intrusiones informáticas, que cuando el evento a detectar es raro las
falsas alarmas son lo que limita la utilidad de un detector. Williams (2021) formaliza cómo la precisión depende de la
prevalencia: si la tasa de falsas alarmas es mayor que cero, la precisión tiende a cero cuando la prevalencia tiende a
cero.

La precisión esperada para una prevalencia *p*, con una proporción *r* de estafas avisadas y una tasa *f* de falsas
alarmas, es:

> precisión(*p*) = *p* · *r* / (*p* · *r* + (1 − *p*) · *f*)

La consecuencia es directa. La precisión que se mide en un corpus con tantas estafas como llamadas legítimas no se
traslada al uso cotidiano, donde la enorme mayoría de las llamadas son legítimas. Por eso conviene informar por
separado la detección y las falsas alarmas, y la precisión solo para prevalencias supuestas.

Hay un segundo efecto, propio de la detección incremental. Si en una llamada legítima cada consulta tiene una
probabilidad *q* de dar una falsa alarma, y la llamada se consulta *N* veces, la probabilidad de al menos una falsa
alarma es 1 − (1 − *q*)^*N*. Un detector que acierta el 99 % de las veces en cada consulta, consultado cada 15 segundos
durante una llamada de 20 minutos (*N* = 80), avisa al menos una vez en el 55 % de las llamadas legítimas. Por eso, en
un detector incremental, la falsa alarma se cuenta por llamada y no por consulta, y cada consulta que se evita o que se
vuelve más precisa pesa mucho en el resultado final.

## 3.8. Datos para detectar vishing

Los conjuntos de datos públicos de llamadas de estafa son escasos (Triantafyllopoulos et al., 2025). Los que existen
tienen límites para este problema: están en otros idiomas, tienen solo estafas o solo llamadas legítimas, son
sintéticos, o no tienen marcado el momento del pedido. La Tabla 3.2 resume algunos.

| Conjunto | Contenido | Límite para este trabajo |
|---|---|---|
| KorCCVi (selfcontrol7, s. f.) | Transcripciones automáticas de estafas reales en coreano, publicadas por el regulador financiero de Corea | Solo estafas; otro idioma y otras modalidades |
| Honeypot de Traister et al. (2026) | Llamadas reales de estafa y spam atendidas por un agente automático, en inglés | Sin llamadas legítimas ni audio en la parte pública |
| TeleAntiFraud-28k (2025) | Pares de audio y texto de llamadas de fraude y normales, en chino | Otro idioma y otras modalidades |
| CallCenterEN (AIxBlock, s. f.) | Transcripciones reales de centros de atención, en inglés | Solo legítimas; parte de las llamadas de venta no son legítimas |
| ES-Port (Vicomtech, 2018) | Transcripciones de soporte técnico de una operadora española | Solo legítimas; español de España |
| scam-dialogue (BothBosu, s. f.) | Diálogos sintéticos de estafa y legítimos, en inglés | Sintético y en otro idioma |

*Tabla 3.2. Conjuntos públicos relacionados y sus límites.*

**Datos sintéticos.** Ante la falta de datos reales, una opción es generar conversaciones con modelos de lenguaje. Es
útil para cubrir escenarios y controlar las condiciones, pero tiene un riesgo documentado. Traister et al. (2026)
muestran que modelos que separan perfectamente estafas sintéticas caen a un F1 de entre 0,02 y 0,40 en llamadas
reales, y recomiendan particiones separadas por llamante. Las conversaciones generadas pueden delatar su clase por la
forma (quién inicia la llamada, el largo, el estilo) y no solo por el contenido.

**Reutilizar el conjunto de prueba.** Dwork et al. (2015) muestran que, si se toman decisiones mirando el conjunto de
prueba, sus resultados dejan de ser una estimación válida del rendimiento. Elegir una instrucción, un umbral o un
modelo mirando los casos con los que después se evalúa sobreestima el resultado. De ahí la práctica de separar un
conjunto de desarrollo, sobre el que se decide, de un conjunto reservado que se mira una sola vez.

## 3.9. Sistemas existentes

Los sistemas relacionados atacan el problema en niveles distintos. La Tabla 3.3 los resume.

| Sistema | Qué analiza | Dónde corre | ¿Ve la manipulación? | ¿Es reproducible? |
|---|---|---|---|---|
| Ventinel | Desvío de llamadas y texto en pantalla causados por software malicioso | Android | No | Sí |
| HearMeOut | Permisos y comportamiento de aplicaciones maliciosas | Android | No | Sí |
| Modelos acústicos | Tono y estrés en la voz | Servidor | En parte, y son sensibles al ruido | En parte |
| VishGPT (Ampel et al., 2026) | Transcripción, con un modelo de lenguaje | Servidor | Sí | En parte |
| Shen et al. (2025) | Conversación en curso, con un modelo de lenguaje | Servidor | Sí | En parte |
| Google Scam Detection | Contenido de la llamada | Teléfono (Pixel) | Sí | No |
| Servicios de Samsung y de operadores coreanos | Contenido de la llamada | Teléfono | Sí | No |

*Tabla 3.3. Sistemas relacionados y nivel en que actúan.*

> **Falta fuente:** Ventinel, HearMeOut y Samsung no tienen referencia completa en el repositorio.

Los dos primeros protegen contra aplicaciones maliciosas instaladas en el teléfono, no contra una persona que engaña
por una línea común. Los modelos acústicos analizan cómo se habla y no qué se pide. VishGPT reporta un F1 de 87,74 %
sobre transcripciones, pero corre en servidores y no evalúa la latencia en un teléfono.

**Google.** Google usa el nombre *Scam Detection* para varias funciones distintas. La que importa acá analiza el
contenido de la llamada en el teléfono y avisa con una notificación, un sonido y una vibración, con opciones para
seguir o cortar (Farafonova y Kafka, 2024; Google, s. f.). En los Pixel 9 y posteriores la impulsa un modelo de
lenguaje que corre en el teléfono; en equipos anteriores, modelos más chicos (Google, 2025). Viene desactivada, no se
usa en llamadas con contactos, emite un tono audible al principio de la llamada y cada algunos minutos para que la
otra parte sepa que se analiza, y solo funciona en algunos países, entre los que no está la Argentina (Google, s. f.).
Google aclara que no detecta todas las estafas. No publica cómo procesa la llamada a medida que avanza, con qué
precisión detecta ni cuántas falsas alarmas produce, y tampoco le explica al usuario por qué lo alerta.

**La solicitud de patente de Google.** Una solicitud de patente de Google, *In-call scam detection* (Farafonova et al.,
2024), describe el espacio de diseño de una detección durante la llamada. No es necesariamente el producto que se
distribuye, pero describe ideas útiles: dos capas de costo, en las que señales baratas despiertan a un modelo caro;
umbrales escalonados con acciones graduadas; un riesgo que puede bajar si quien llama responde de manera
satisfactoria; un reporte que explica por qué se disparó el aviso; preguntas sugeridas a la persona para separar a una
entidad real de un estafador; y el procesamiento efímero, sin guardar el audio ni la transcripción, lo que obliga a
decidir de manera incremental.

## 3.10. Privacidad y marco normativo

Un sistema que analiza una llamada procesa la voz de dos personas. En la Argentina, la Ley 25.326 de Protección de los
Datos Personales exige que los datos sean adecuados y no excesivos respecto de su finalidad (art. 4), que se recojan
con consentimiento informado (arts. 5 y 6), que se protejan (arts. 9 y 10) y que no se cedan sin autorización (art.
11). Un diseño que procesa todo en el teléfono, no guarda el audio, descarta la transcripción al terminar la llamada y
no envía nada a un servidor atiende esos principios por construcción.

El Código Penal sanciona la interceptación indebida de comunicaciones y el acceso no autorizado a sistemas (arts. 153
y 153 bis), y el entorpecimiento de las telecomunicaciones (art. 197). Un sistema que forma parte del teléfono de quien
recibe la llamada, escucha de manera pasiva, no altera la señal y solo le muestra un aviso a su usuario no intercepta
una comunicación ajena. Aun así, la otra parte no sabe que se analiza la conversación: el producto de Google lo
resuelve con el tono audible periódico.

La plataforma agrega una restricción técnica. En Android, una aplicación común no puede acceder al audio de una
llamada telefónica: las fuentes de audio de la llamada requieren un permiso reservado a aplicaciones del sistema
(Android Developers, s. f.-a, s. f.-b). La restricción coincide con la protección del secreto de las comunicaciones y
explica por qué un producto de este tipo tiene que integrarse con el fabricante del teléfono.

## 3.11. El espacio que aborda este trabajo

La Tabla 3.4 resume lo que existe y el espacio que queda.

| Aspecto | Lo que existe | Espacio para este trabajo |
|---|---|---|
| Análisis durante la llamada | Productos comerciales cerrados | Un prototipo abierto y reproducible |
| Procesamiento en el dispositivo | Declarado por los productos, sin detalle | Una arquitectura local documentada y medida en teléfonos |
| Detección académica | Trabajos en servidores y en otros idiomas | Español y escenarios argentinos |
| Medida principal | Métricas sobre la llamada completa | El momento del aviso respecto del pedido |
| Explicación del aviso | Prometida en la patente, ausente en el producto | Un motivo breve en el aviso |
| Datos | Conjuntos en otros idiomas, sin marcas de pedido | Un corpus en español con el pedido y el cumplimiento marcados |

*Tabla 3.4. Lo que existe y el espacio que ocupa este trabajo.*
