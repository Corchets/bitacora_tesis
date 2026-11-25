# Capítulo 1. Introducción

## 1.1. Contexto

El *vishing*, contracción de *voice phishing*, es una forma de ingeniería social que se realiza por llamada de voz.
Quien llama no aprovecha una falla del software, sino la confianza, la urgencia y la autoridad. Se presenta como
empleado de un banco, agente de un organismo público, técnico de una empresa o familiar en apuros, y lleva la
conversación hasta un pedido concreto: dictar el código que llegó por SMS, decir una clave, transferir dinero, instalar
una aplicación de acceso remoto o seguir instrucciones en el teléfono que terminan entregando el control de una cuenta.

En la Argentina, distintas fuentes oficiales describen estas modalidades. La Unidad Fiscal Especializada en
Investigación Criminal Compleja advierte sobre estafas telefónicas dirigidas a personas mayores, entre ellas la del
familiar que pide dinero y la del falso cambio de billetes (Ministerio Público Fiscal de la Nación, s. f.). El Banco
Central de la República Argentina recuerda que ninguna entidad pide códigos ni claves por teléfono (BCRA, s. f.-a). La
ANSES aclara que nunca solicita datos personales, claves ni información bancaria (ANSES, s. f.). El Estado nacional
publicó recomendaciones específicas contra el robo de cuentas de WhatsApp mediante el código de activación (Gobierno de
la Nación Argentina, 2022). Estas fuentes muestran que las modalidades existen y son conocidas, pero no miden su
frecuencia. Este trabajo tampoco afirma cifras de prevalencia.

## 1.2. El problema

Una llamada de vishing puede llegar desde un número que parece normal. El peligro se vuelve visible en lo que se dice
y en cómo avanza la conversación. Las defensas habituales no llegan a ese punto. Los filtros por reputación del número
no conocen el contenido de la llamada. Las campañas de prevención dependen de que la persona recuerde el consejo justo
cuando está bajo presión, sin poder verificar quién le habla y, muchas veces, con alguien que le pide no cortar.

El problema que aborda este trabajo es detectar, **mientras la llamada está en curso**, evidencia suficiente de que la
conversación lleva a la persona hacia una entrega riesgosa, y avisarle a tiempo para que pueda frenar. Tres condiciones
le dan forma:

1. **El aviso sirve solo si llega antes de que la persona cumpla el pedido.** Una detección perfecta al final de la
   llamada no protege a nadie. Lo que se mide no es solo si el sistema avisa, sino cuándo.
2. **Las falsas alarmas tienen costo.** La gran mayoría de las llamadas que recibe una persona son legítimas. Un aviso
   que salta seguido en llamadas normales se aprende a ignorar, y un aviso ignorado no protege.
3. **El contenido no prueba la identidad.** Si una llamada legítima y una estafa dicen lo mismo, el sistema dispone de
   la misma evidencia en las dos. Por eso el aviso no afirma que la llamada sea una estafa: sugiere cortar y verificar
   por otro canal.

A esas condiciones se suma una restricción de privacidad. Para analizar una llamada hay que procesar la voz de dos
personas. Si la transcripción viajara a un servidor, la protección contra un fraude abriría otro riesgo. El análisis
tiene que ocurrir en el propio teléfono, sin guardar el audio.

## 1.3. Lo que existe y lo que falta

La industria llegó a una conclusión parecida. Desde noviembre de 2024, Google ofrece en sus teléfonos Pixel una función
que analiza el contenido de la llamada en el dispositivo y avisa cuando detecta patrones de estafa (Farafonova y
Kafka, 2024). En los modelos más recientes la impulsa un modelo de lenguaje que corre en el teléfono (Google, 2025). La
función viene desactivada, no se usa en llamadas con contactos y no está disponible en la Argentina (Google, s. f.).
Samsung ofrece una función comparable en sus equipos Galaxy recientes, y operadores coreanos ofrecen servicios de
detección en el teléfono (SK Telecom, s. f.; GSMA, 2025).

> **Falta fuente:** la afirmación sobre Samsung no tiene fuente primaria en el repositorio. Conseguirla o reformular.

Estos productos muestran que analizar la conversación en el dispositivo es viable y que la industria lo considera el
lugar adecuado para intervenir. Pero son cerrados: no publican cómo procesan la llamada a medida que avanza, con qué
precisión detectan ni cuántas falsas alarmas producen, y no explican al usuario por qué lo alertan. No se pueden
reproducir ni comparar experimentalmente. Una solicitud de patente de Google describe el espacio de diseño de una
detección de este tipo (Farafonova et al., 2024), pero una patente no informa resultados.

En la literatura académica, la detección de vishing sobre transcripciones avanzó en los últimos años. Hay trabajos que
usan modelos de lenguaje grandes en servidores (Ampel et al., 2026), que ajustan modelos chicos para la tarea (Sim y
Kim, 2025) y que estudian el compromiso entre detectar más y avisar a tiempo (Shen et al., 2025). La mayoría trabaja
en inglés, coreano o chino, clasifica la llamada completa o corre en servidores, y no mide el costo en un teléfono. Un
relevamiento reciente señala además la escasez de datos públicos y la necesidad de diseñar la detección y la
intervención juntas (Triantafyllopoulos et al., 2025).

Lo que falta es un enfoque abierto y evaluable para el español rioplatense y los escenarios argentinos, que procese la
conversación mientras ocurre, corra en el teléfono y mida cuándo avisa respecto del pedido. Este trabajo apunta a eso.

## 1.4. Propuesta y aporte

Este trabajo diseña, implementa y evalúa un prototipo de detección de vishing durante la llamada. El sistema transcribe
el audio en el dispositivo y, cada vez que la otra persona termina de hablar, le pregunta a un modelo de lenguaje chico
qué riesgo hay en lo dicho hasta ese momento. Cuando el riesgo supera un umbral, muestra un único aviso con un motivo
breve. Nada sale del teléfono y el audio no se guarda.

Para evaluarlo se construyó un corpus de conversaciones en español con escenarios argentinos, que incluye estafas y
llamadas legítimas difíciles, con el momento del pedido y del cumplimiento marcados en cada una. El detector se eligió
sobre una parte de ese corpus y se evaluó una sola vez sobre otra parte reservada, con las reglas de lectura escritas
antes de correr. La evaluación se completó con estafas y llamadas legítimas reales de fuentes públicas, y el costo se
midió en dos teléfonos.

El análisis de la conversación durante la llamada no es una idea nueva. El aporte de este trabajo es la combinación
de:

- vishing en español, con escenarios argentinos;
- procesamiento incremental, en el que el detector solo ve lo dicho hasta cada momento;
- un aviso único, con un motivo que la persona puede entender;
- una evaluación centrada en el momento del aviso respecto del pedido y del cumplimiento;
- ejecución completamente local, medida en teléfonos;
- un registro reproducible de cada decisión y cada experimento, incluidos los resultados negativos.

En la literatura revisada no se identificó un corpus que reúna conversaciones fraudulentas y legítimas comparables del
dominio argentino con las marcas de tiempo que exige esta evaluación. Eso no significa que no exista.

## 1.5. Beneficiarios

La beneficiaria directa es la persona que recibe la llamada. El trabajo pone el foco en las personas mayores, por la
gravedad de las pérdidas que pueden sufrir y porque las fuentes oficiales las señalan como blanco de la suplantación.
Ese foco es parcial. Las conversaciones del corpus no fueron producidas por personas mayores y no se hizo una prueba
con usuarios, así que no se afirma un rendimiento particular para ese grupo.

Los beneficiarios indirectos son las entidades suplantadas, que hoy solo pueden advertir con campañas, y los
fabricantes de teléfonos y operadores, para quienes el trabajo documenta una arquitectura abierta, sus decisiones y
sus límites medidos.

## 1.6. Organización del informe

El capítulo 2 fija los objetivos, las preguntas de investigación y el alcance. El capítulo 3 presenta el marco
teórico: la ingeniería social, el reconocimiento del habla, los modelos de lenguaje, la clasificación temprana, el
problema de las falsas alarmas, los sistemas existentes y el marco normativo. El capítulo 4 describe la arquitectura
del sistema y el 5, las tecnologías que lo componen. El capítulo 6 explica las metodologías de trabajo, de
investigación y de evaluación, incluidos el corpus y las métricas. El capítulo 7 recorre las etapas del proyecto: qué
se probó, qué cambió y por qué. El capítulo 8 reúne las comparaciones que sostienen cada decisión, y el 9 presenta la
evaluación final y su discusión. El capítulo 10 concluye y el 11 propone las mejoras futuras y una hoja de ruta para
continuar el trabajo.

---

# Capítulo 2. Objetivos y alcance

## 2.1. Objetivo general

Diseñar, implementar y evaluar un prototipo que analice de manera incremental una conversación de voz en español,
mediante inferencia local, para estimar el riesgo de vishing, identificar maniobras de ingeniería social y emitir una
advertencia contextual antes de una acción crítica, cuantificando su desempeño, sus falsas alarmas, su latencia y su
margen temporal de intervención.

## 2.2. Objetivos específicos

1. Relevar el estado del arte, las modalidades de vishing relevantes en la Argentina y las restricciones técnicas,
   éticas y legales del problema.
2. Definir una taxonomía operativa de maniobras y de pedidos riesgosos.
3. Construir un corpus controlado y documentado de conversaciones de vishing y de llamadas legítimas difíciles en
   español.
4. Comparar alternativas de reconocimiento de voz que corran en el dispositivo.
5. Evaluar reglas de palabras clave como línea base para comparar los detectores candidatos.
6. Desarrollar un detector incremental que considere toda la conversación disponible hasta cada momento.
7. Diseñar advertencias explicables, derivadas de la evidencia de la conversación.
8. Integrar el recorrido audio → transcripción → detección → advertencia en un entorno controlado.
9. Evaluar la detección, las falsas alarmas, la anticipación respecto del pedido, la latencia y el consumo de recursos.
10. Documentar la arquitectura, las decisiones, los resultados, las limitaciones y el trabajo futuro.

## 2.3. Preguntas de investigación

El trabajo se organiza alrededor de dos preguntas:

- **Detección incremental.** ¿Con qué desempeño y con qué tasa de falsas alarmas puede detectarse vishing usando solo
  la parte de la conversación disponible hasta cada momento?
- **Utilidad temporal.** ¿Con cuánto margen respecto del primer pedido riesgoso y del primer cumplimiento puede
  emitirse el aviso?

Como objetivo secundario se plantea revisar si el motivo que muestra el aviso corresponde a lo que efectivamente se
dijo en la llamada.

> **Corregir:** no hay una evaluación registrada del motivo. Antes de cerrar el capítulo 9, decidir si se informa
> como no realizada o si se hace una revisión acotada.

Las preguntas no presuponen un resultado favorable. Un experimento que muestre poca anticipación, o que un método
simple rinde igual que uno complejo, es un resultado válido si está bien diseñado.

## 2.4. Alcance

**Idioma y escenarios.** Español, con prioridad de la variedad rioplatense y de las modalidades documentadas en la
Argentina. No se afirma representatividad nacional ni regional.

**Llamadas.** El detector se activa en llamadas entrantes de números que no están en la agenda del teléfono. Es la
situación típica del vishing y la misma que usan los productos comerciales comparables. Las consultas que inicia la
propia persona, en las que es normal que le pidan datos, quedan fuera. La aplicación decide si activa el detector; el
modelo recibe solo la transcripción.

> **Estado: propuesta sin discutir.** El alcance de entrantes de números no agendados
> ([ADR 0003](../ingenieria/adr/0003-detector-solo-en-entrantes-de-no-agendados.md)) se usó en la evaluación final,
> pero no está aceptado formalmente.

**Procesamiento.** Todo ocurre en el dispositivo: la transcripción, la detección y el aviso. La conversación no sale
del teléfono y el audio no se guarda. El sistema no consulta modelos remotos.

> **Estado: propuesta sin discutir.** Un modelo remoto se usó como referencia de comparación sobre conversaciones
> ficticias (capítulo 8). [D03](../gestion/MAPA-DECISIONES.md#d03--congelar-alcance-y-contribución) dice que no
> entra ni como referencia: el equipo tiene que actualizarla antes de cerrar este párrafo.

**Detección.** Sobre la transcripción de la llamada en curso, sin memoria de llamadas anteriores. El sistema emite un
solo aviso por llamada, con un motivo breve.

**Prototipo.** Un recorrido completo, desde el audio hasta el aviso, que funciona en vivo sobre una llamada por
internet en la que el sistema recibe la voz de cada persona por separado.

**Evaluación.** La detección se mide sobre conversaciones escritas: un corpus propio y conjuntos externos de llamadas
reales. El reconocimiento de voz se mide aparte, con voz real. La latencia y la memoria se miden en teléfonos.

## 2.5. Exclusiones

| Fuera del alcance | Motivo |
|---|---|
| Analizar llamadas telefónicas comunes desde una aplicación instalada por el usuario | En Android, el audio de una llamada telefónica está reservado a aplicaciones del sistema (Android Developers, s. f.-a, s. f.-b). Un producto real tendría que integrarse con el fabricante (capítulo 4) |
| Biometría de voz y detección de voces clonadas | Es otro problema, con otras técnicas y otros datos |
| Rasgos acústicos (tono, estrés en la voz) para detectar fraude | El audio se usa para transcribir. El análisis del tono queda como mejora futura |
| Reputación del número y detección de números falsificados | Ya existen soluciones para eso, y no ven el contenido de la llamada |
| Medir cuánto cambia la detección entre una transcripción manual y la automática sobre las mismas llamadas | Requería grabar y transcribir a mano todo el corpus. El reconocimiento de voz se midió por separado |
| Prueba con usuarios | No se midió si el aviso cambia la conducta de la persona |
| Aplicación para el público, otros idiomas, análisis de mensajes y servicios en la nube | Fuera del tiempo y del objetivo del trabajo |

## 2.6. Criterio de éxito

El trabajo es exitoso si responde las preguntas con un procedimiento honesto y reproducible, entrega un recorrido
demostrable de punta a punta y documenta sus límites.

El equipo fijó una meta de referencia: avisar en el 80 % a 85 % de las estafas, con 10 % a 15 % de falsas alarmas,
contando todas las estafas, incluso las que terminan antes de que aparezca un pedido. No es un umbral de aprobación.
Se busca el mejor resultado posible sin ajustar el sistema para alcanzar esa cifra, y el resultado se informa aunque
no la alcance. Además, se pide que el detector no avise por una frase suelta (por ejemplo, «pasame el código») en una
conversación que no tiene nada que ver con una estafa.

---

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

---

# Referencias

> **Nota de edición.** Estilo APA 7.ª edición, en orden alfabético. Se suman entradas a medida que se redactan los
> capítulos; cada entrada lleva al lado los capítulos que la citan. Las marcadas con † tienen datos incompletos
> (autores o publicación) y hay que completarlas desde la fuente original antes de la entrega. Las fuentes web llevan
> la fecha de consulta registrada en el repositorio. Esta nota y los capítulos entre corchetes se borran en la versión
> final.

Administración Nacional de la Seguridad Social. (s. f.). *ANSES nunca solicita datos personales, claves o información
bancaria*. Recuperado el 23 de septiembre de 2026, de
https://www.anses.gob.ar/noticias/anses-nunca-solicita-datos-personales-claves-o-informacion-bancaria-0 [1, 3]

† AIxBlock. (s. f.). *92k real-world call center scripts (English)* [Conjunto de datos]. Hugging Face.
https://huggingface.co/datasets/AIxBlock/92k-real-world-call-center-scripts-english [3]

Ampel, B., Samtani, S., & Chen, H. (2026). Automatically detecting voice phishing: A large audio model approach
(VishGPT). *MIS Quarterly, 50*(2). https://aisel.aisnet.org/misq/vol50/iss2/9/ [1, 3]

Android Developers. (s. f.-a). *MediaRecorder.AudioSource*. https://developer.android.com/reference/android/media/MediaRecorder.AudioSource [2, 3]

Android Developers. (s. f.-b). *Sharing audio input*. https://developer.android.com/media/platform/sharing-audio-input [2, 3]

Axelsson, S. (2000). The base-rate fallacy and the difficulty of intrusion detection. *ACM Transactions on
Information and System Security, 3*(3), 186–205. https://doi.org/10.1145/357830.357849 [3]

Balagopalan, A., Shkaruta, K., & Novikova, J. (2019). *Impact of ASR on Alzheimer's disease detection: All errors are
equal, but deletions are more equal than others* [Preprint]. arXiv. https://arxiv.org/abs/1904.01684 [3]

Banco Central de la República Argentina. (s. f.-a). *Cómo prevenir estafas virtuales*. Recuperado el 23 de septiembre
de 2026, de https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/ [1, 3]

Banco Central de la República Argentina. (s. f.-b). *Recomendaciones en el Día Internacional de la Seguridad de la
Información*. Recuperado el 23 de septiembre de 2026, de
https://www.bcra.gob.ar/noticias/recomendaciones-en-el-dia-internacional-de-la-seguridad-de-la-informacion/ [3]

Banco Galicia. (s. f.). *Alerta por estafa de pantalla compartida*. Recuperado el 17 de septiembre de 2026, de
https://www.galicia.ar/personas/educacion-financiera/alerta-por-estafa-de-pantalla-compartida [3]

† BothBosu. (s. f.). *scam-dialogue* [Conjunto de datos]. Hugging Face.
https://huggingface.co/datasets/BothBosu/scam-dialogue [3]

Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient finetuning of quantized LLMs. En
*Advances in Neural Information Processing Systems 36*. https://arxiv.org/abs/2305.14314 [3]

Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for
language understanding. En *Proceedings of the 2019 Conference of the North American Chapter of the Association for
Computational Linguistics* (pp. 4171–4186). https://doi.org/10.18653/v1/N19-1423 [3]

Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). The reusable holdout: Preserving
validity in adaptive data analysis. *Science, 349*(6248), 636–638. https://doi.org/10.1126/science.aaa9375 [3]

Farafonova, L., & Kafka, S. (2024, 13 de noviembre). Safer with Google: New intelligent, real-time protections on
Android to keep you safe. *Google Online Security Blog*.
https://security.googleblog.com/2024/11/new-real-time-protections-on-Android.html [1, 3]

Farafonova, L., Geng, Y., Abdullah, U., & Chiou, R. (2024). *In-call scam detection* (Publicación de solicitud de
patente de EE. UU. N.º US 2024/0388655 A1). Google LLC. https://patents.google.com/patent/US20240388655A1/en [1, 3]

Gemma Team, Google DeepMind. (2026). *Gemma 4 model card*. Recuperado el 6 de noviembre de 2026, de
https://ai.google.dev/gemma/docs/core/model_card_4 [3]

Gobierno de la Nación Argentina. (2022). *Recomendaciones para evitar fraudes en WhatsApp*.
https://www.argentina.gob.ar/sites/default/files/2022/07/recomendaciones_evitar_fraudes_whatsapp.pdf [1, 3]

Google. (s. f.). *Use Scam Detection*. Ayuda de la app Teléfono. Recuperado el 17 de septiembre de 2026, de
https://support.google.com/phoneapp/answer/15654065 [1, 3]

Google. (2025, 4 de marzo). New AI-powered scam detection features to help protect you on Android. *The Keyword*.
https://blog.google/security/new-ai-powered-scam-detection-features/ [1, 3]

† GSMA. (2025). *Case study: Real-time on-device vishing detection and anti-deepvoice protection*.
https://www.gsma.com/solutions-and-impact/technologies/security/scams/wp-content/uploads/2025/08/Case-Study_Real-time-On-device-Vishing-Detection-and-Anti-DeepVoice-Protection-v2.pdf [1]

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). LoRA: Low-rank
adaptation of large language models. En *International Conference on Learning Representations*.
https://arxiv.org/abs/2106.09685 [3]

Ley 11.179. (1921). *Código Penal de la Nación Argentina* (arts. 153, 153 bis y 197). Boletín Oficial de la República
Argentina. [3]

Ley 25.326. (2000). *Protección de los datos personales*. Boletín Oficial de la República Argentina. [3]

Liu, Y., Ott, M., Goyal, N., Du, J., Joshi, M., Chen, D., Levy, O., Lewis, M., Zettlemoyer, L., & Stoyanov, V. (2019).
*RoBERTa: A robustly optimized BERT pretraining approach* [Preprint]. arXiv. https://arxiv.org/abs/1907.11692 [3]

Losada, D. E., & Crestani, F. (2016). A test collection for research on depression and language use. En
*Experimental IR meets multilinguality, multimodality, and interaction: CLEF 2016*. Springer.
https://doi.org/10.1007/978-3-319-44564-9_3 [3]

Losada, D. E., Crestani, F., & Parapar, J. (2017). eRISK 2017: CLEF lab on early risk prediction on the internet:
Experimental foundations. En *Experimental IR meets multilinguality, multimodality, and interaction: CLEF 2017*.
Springer. https://doi.org/10.1007/978-3-319-65813-1_30 [3]

Ministerio de Seguridad de la Nación. (s. f.). *Recomendaciones para evitar estafas en internet*. Recuperado el 17 de
septiembre de 2026, de https://www.argentina.gob.ar/seguridad/ciberdelito/recomendaciones-para-evitar-estafas-en-internet [3]

Ministerio Público Fiscal de la Nación. (s. f.). *La Unidad Fiscal Especializada en Investigación Criminal Compleja
advierte sobre estafas telefónicas a personas mayores*. Recuperado el 23 de septiembre de 2026, de
https://www.fiscales.gob.ar/procuracion-general/la-unidad-fiscal-especializada-en-investigacion-criminal-compleja-advierte-sobre-estafas-telefonicas-a-personas-mayores/ [1, 3]

Mizrahi, M., Kaplan, G., Malkin, D., Dror, R., Shahaf, D., & Stanovsky, G. (2024). State of what art? A call for
multi-prompt LLM evaluation. *Transactions of the Association for Computational Linguistics, 12*.
https://arxiv.org/abs/2401.00595 [3]

Mori, U., Mendiburu, A., Dasgupta, S., & Lozano, J. A. (2018). Early classification of time series by simultaneously
optimizing the accuracy and earliness. *IEEE Transactions on Neural Networks and Learning Systems, 29*(10), 4569–4578.
https://doi.org/10.1109/TNNLS.2017.2764939 [3]

Pérez, J. M., Furman, D. A., Alonso Alemany, L., & Luque, F. M. (2022). RoBERTuito: A pre-trained language model for
social media text in Spanish. En *Proceedings of the Thirteenth Language Resources and Evaluation Conference*.
European Language Resources Association. https://aclanthology.org/2022.lrec-1.785 [3]

Radford, A., Kim, J. W., Xu, T., Brockman, G., McLeavey, C., & Sutskever, I. (2023). Robust speech recognition via
large-scale weak supervision. En *Proceedings of the 40th International Conference on Machine Learning*. PMLR.
https://arxiv.org/abs/2212.04356 [3]

Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). Quantifying language models' sensitivity to spurious features in
prompt design or: How I learned to start worrying about prompt formatting. En *International Conference on Learning
Representations*. https://arxiv.org/abs/2310.11324 [3]

† selfcontrol7. (s. f.). *Korean Voice Phishing Detection (KorCCVi v2)* [Conjunto de datos; transcripciones, no
redistribuibles]. GitHub. https://github.com/selfcontrol7/Korean_Voice_Phishing_Detection [3]

† SentinelEdge. (2026). En *Proceedings of the 2026 Conference on Empirical Methods in Natural Language Processing:
System Demonstrations*. https://aclanthology.org/2026.emnlp-demos.60/ [3]

† Shen et al. (2025). *«It warned me just at the right moment»* [Preprint]. arXiv. https://arxiv.org/abs/2502.03964 [1, 3]

† Sim y Kim. (2025). *Detecting voice phishing with precision: Fine-tuning small language models* [Preprint]. arXiv.
https://arxiv.org/abs/2506.06180 [1, 3]

† SK Telecom. (s. f.). [Servicio de detección de vishing en el teléfono]. SK Telecom Newsroom.
https://news.sktelecom.com/221425 [1]

† TeleAntiFraud-28k. (2025). [Preprint]. arXiv. https://arxiv.org/abs/2503.24115 [3]

† Traister et al. (2026). *A corpus of real scam- and spam-call conversations from an active voice-agent honeypot*
[Preprint]. arXiv. https://arxiv.org/abs/2609.29528 [3]

† Triantafyllopoulos, A., et al. (2025). Vishing: Detecting social engineering in spoken communication. *Computer
Speech & Language*. https://doi.org/10.1016/j.csl.2025.101802 [1, 3]

Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, Ł., & Polosukhin, I. (2017).
Attention is all you need. En *Advances in Neural Information Processing Systems 30*. https://arxiv.org/abs/1706.03762 [3]

Vicomtech. (2018). *ES-Port corpus* [Conjunto de datos, CC BY-SA 3.0 ES]. GitHub.
https://github.com/Vicomtech/esport-corpus [3]

Williams, C. K. I. (2021). The effect of class imbalance on precision-recall curves. *Neural Computation, 33*(4),
853–857. https://doi.org/10.1162/neco_a_01362 [3]

Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2024). Can LLMs express their uncertainty? An empirical
evaluation of confidence elicitation in LLMs. En *International Conference on Learning Representations*.
https://arxiv.org/abs/2306.13063 [3]

Xu, H., Jia, F., Majumdar, S., Huang, H., Watanabe, S., & Ginsburg, B. (2023). Efficient sequence transduction by
jointly predicting tokens and durations. En *Proceedings of the 40th International Conference on Machine Learning*.
PMLR. https://arxiv.org/abs/2304.06795 [3]

† Yin, W., Hay, J., & Roth, D. (2019). Benchmarking zero-shot text classification: Datasets, evaluation and entailment
approach. En *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th
International Joint Conference on Natural Language Processing*. https://arxiv.org/abs/1909.00161 [3]

† Zhou et al. (2022). *Calibrate and refine! A novel and agile framework for ASR-error robust intent detection*
[Preprint]. arXiv. https://arxiv.org/abs/2205.11008 [3]

