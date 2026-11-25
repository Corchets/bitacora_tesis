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
