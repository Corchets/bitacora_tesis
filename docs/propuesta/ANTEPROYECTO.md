> [!WARNING]
> **Documento histórico — contiene afirmaciones que ya sabemos incorrectas.**
> Es la conversión fiel del `.docx` original (resguardado en [original/](original/)).
> Antes de reutilizar cualquier párrafo, leer [correcciones-pendientes.md](CORRECCIONES-ANTEPROYECTO.md).
> Las marcas `⚠️[C1]`…`⚠️[C5]` señalan afirmaciones **incorrectas** a corregir.
> Las marcas `⚠️[S1]`…`⚠️[S3]` señalan **supuestos que el texto da por decididos y no lo están**.

---

# Anteproyecto de Tesis

Título: Detección temprana y explicable de vishing mediante análisis incremental de conversaciones telefónicas en español

Carrera: Ingeniería Informática Autores: Luciano Grosso — [nombre del compañero] Director propuesto: [a definir] Fecha: [a completar]

## 1. Resumen

El vishing —estafa telefónica basada en ingeniería social— sigue siendo eficaz porque no ataca sistemas sino personas: no hay software vulnerado ⚠️[C1], hay una conversación en la que alguien es persuadido de entregar un dato o ejecutar una acción. Las defensas actuales operan casi exclusivamente antes de la llamada ⚠️[C2], bloqueando números reportados, y por lo tanto son inútiles frente a una llamada desde un número nuevo o suplantado.

Este trabajo propone diseñar, implementar y evaluar un prototipo que analice la conversación telefónica mientras ocurre, estime de forma incremental el riesgo de que se trate de un intento de ingeniería social, y emita una advertencia comprensible antes de que la persona comparta información sensible o realice una acción de alto riesgo. La advertencia no se limita a señalar peligro: nombra la maniobra concreta que se está ejecutando, de modo que el usuario pueda entender qué le está pasando y decidir.

El sistema se implementa como aplicación que procesa todo localmente, sin enviar audio ni transcripciones fuera del dispositivo, orientada especialmente a personas mayores por ser la población más afectada ⚠️[C4] por esta modalidad de fraude.

## 2. Planteamiento del problema

Las estafas telefónicas en Argentina siguen guiones reconocibles: alguien se presenta como empleado de un banco, de ANSES o de una plataforma de pagos; construye urgencia; pide que la persona no corte ni consulte con nadie; y termina solicitando un código de verificación, los datos de una tarjeta, la instalación de una aplicación de acceso remoto o una transferencia. La víctima típica no es descuidada: es alguien sometido durante varios minutos a una presión diseñada profesionalmente.

La protección disponible hoy es esencialmente reactiva. Los filtros de llamadas comparan el número entrante contra listas de reportes, lo que falla ante números nuevos, suplantados o generados masivamente. Una vez que la llamada fue atendida, la persona queda sola frente al guion. Existen desarrollos comerciales recientes que analizan la conversación en curso —notablemente la función de detección de estafas que Google incorporó en dispositivos Pixel y, más recientemente, en algunos Samsung—, pero están limitados a determinados modelos, países e idiomas, no cubren el español ⚠️[C3], y funcionan como caja negra: alertan sin explicar y sin permitir evaluar académicamente su desempeño.

Existe entonces un vacío concreto: no hay evidencia publicada sobre qué tan bien puede detectarse una manipulación por ingeniería social en español mientras la conversación transcurre, ni sobre cuánta anticipación es posible lograr respecto del momento crítico. Esa segunda pregunta es la más relevante en la práctica: un sistema que acierta el diagnóstico cuando la transferencia ya se hizo no sirve de nada.

## 3. Justificación

El daño es concreto, local y recae desproporcionadamente sobre adultos mayores, que además suelen tener menos herramientas para reconocer el patrón y más reticencia a consultar antes de actuar. Una intervención que ocurra durante la llamada, en el momento exacto en que la presión se ejerce, ataca el problema donde efectivamente sucede.

Desde el punto de vista académico, el trabajo aporta tres elementos ausentes en la literatura disponible en español: un corpus anotado de conversaciones de vishing en variedad español, una taxonomía operativa de técnicas de manipulación etiquetada turno por turno, y una métrica de evaluación centrada en la anticipación temporal y no solo en la clasificación final. Estos tres productos conservan valor independientemente del rendimiento que alcance el prototipo, y habilitan trabajos posteriores.

Desde el punto de vista técnico, el desafío interesante no es clasificar una conversación completa —eso es un problema resuelto ⚠️[C5]—, sino decidir con información parcial, acumulando evidencia turno a turno y eligiendo el momento de intervenir bajo la tensión entre advertir temprano y no advertir en falso.

## 4. Objetivo general

Diseñar, implementar y evaluar un prototipo funcional capaz de analizar una conversación telefónica en tiempo real, estimar el riesgo de que se trate de un intento de ingeniería social, y emitir una advertencia contextual y explicable antes de que el usuario comparta información sensible o ejecute una acción de alto riesgo.

## 5. Objetivos específicos

- Construir una taxonomía operativa de técnicas de ingeniería social presentes en las modalidades de fraude telefónico vigentes en Argentina, validada mediante acuerdo entre anotadores independientes.
- Elaborar un corpus anotado de conversaciones telefónicas en español, que incluya casos fraudulentos y casos legítimos —entre ellos, casos legítimos deliberadamente similares a un fraude—, con etiquetado por turno y marcación del momento crítico de cada diálogo.
- Desarrollar un método de estimación incremental de riesgo que acumule evidencia a lo largo de la conversación y determine el momento de emitir la advertencia.
- Implementar el prototipo como aplicación Android ⚠️[S2] con procesamiento local, que se active únicamente durante las llamadas y no conserve audio ni transcripciones.
- Evaluar el sistema comparándolo contra un método de referencia basado en palabras clave, midiendo tanto la exactitud de clasificación como la anticipación lograda respecto del momento crítico, bajo una restricción explícita de falsos positivos.
- Realizar una evaluación exploratoria de usabilidad con usuarios del perfil objetivo.

## 6. Hipótesis

Un análisis semántico incremental y contextual de la conversación permite detectar intentos de vishing con mayor utilidad práctica que un método basado únicamente en palabras clave, entendiendo "utilidad" no solo como exactitud de clasificación sino principalmente como anticipación: cantidad de turnos y de segundos de ventaja obtenidos respecto del momento en que se solicita el dato sensible o la acción de riesgo, manteniendo la tasa de falsos positivos por debajo de un umbral fijado de antemano.

La hipótesis es falsable en ambos sentidos. Si el método incremental no supera al de referencia en anticipación a igual tasa de falsos positivos, el resultado es igualmente informativo y constituye un aporte válido.

## 7. Descripción funcional de la solución

La aplicación permanece inactiva mientras no hay llamadas. Al iniciarse una, se activa automáticamente y comienza a escuchar la conversación. A medida que las personas hablan, el sistema va transcribiendo internamente lo dicho y evaluando cada intervención: reconoce si alguien está invocando una autoridad institucional, generando urgencia artificial, pidiendo que no se corte ni se consulte con terceros, solicitando un código de verificación, induciendo a instalar una aplicación de acceso remoto o proponiendo continuar la conversación por otro medio.

Ninguno de esos elementos, por sí solo, indica necesariamente un fraude —un banco real también puede tener urgencia y pedir verificación de identidad—. Lo que el sistema hace es acumularlos: mantiene un nivel de riesgo que sube cuando aparecen señales y baja cuando la conversación se normaliza, ponderado además por el contexto de la llamada, como si el número está agendado o si la llamada fue entrante o saliente.

Cuando ese nivel supera un primer umbral, la aplicación muestra un aviso discreto. Si supera el umbral crítico, interrumpe: sonido, vibración y una pantalla que se superpone a la llamada con una frase corta que nombra lo que está ocurriendo —por ejemplo, que se está pidiendo un código de verificación y que se está insistiendo en no cortar— y un botón grande para terminar la llamada. La decisión final siempre es del usuario; el sistema informa, no bloquea.

Al finalizar, el audio y la transcripción se descartan. Queda únicamente un registro del evento —fecha, número parcialmente enmascarado, duración, señales detectadas y nivel de riesgo alcanzado— que la persona, o un familiar previamente autorizado por ella, puede consultar después. Opcionalmente, y solo si el usuario lo habilita de forma explícita y visible, un familiar puede recibir un aviso cuando ocurre una alerta de riesgo alto; ese aviso contiene únicamente metadatos, nunca contenido de la conversación.

La interfaz se adapta al perfil: para el usuario objetivo principal se reduce a un interruptor y un estado, sin nada más que aprender.

## 8. Alcance y limitaciones

El trabajo se limita al idioma español en su variedad Argentina y a la plataforma Android. ⚠️[S2] La plataforma iOS queda fuera del alcance por restricciones del sistema operativo que impiden a cualquier aplicación de terceros acceder al audio durante una llamada.

Por restricciones análogas en Android, el prototipo captura la conversación de manera acústica, con la llamada en altavoz. ⚠️[S1] Esta condición, lejos de ser puramente una limitación, se alinea con el comportamiento habitual de la población objetivo, que suele utilizar el altavoz por comodidad o por razones auditivas; la aplicación lo activa automáticamente y lo presenta como parte de su funcionamiento normal. La consecuencia técnica es que la calidad de audio disponible es inferior a la de la línea, lo cual se documenta y se mide como parte de la evaluación.

El prototipo se distribuye mediante instalación directa ⚠️[S3], no a través de tiendas de aplicaciones, por razones de política de las plataformas. Las vías de distribución masiva se analizan como trabajo futuro.

El corpus se construye de manera controlada a partir de modalidades de fraude documentadas públicamente, no mediante grabación de llamadas fraudulentas reales, lo cual sería inviable y éticamente problemático. Esta decisión se declara explícitamente como limitación de validez externa y se mitiga incorporando vocalización humana, casos legítimos difíciles y validación de los guiones con personas con experiencia en prevención de fraude.

El sistema no pretende reemplazar el juicio del usuario ni bloquear llamadas automáticamente, y no se plantea como un producto listo para el mercado sino como un prototipo de investigación.

## 9. Metodología de trabajo

El trabajo se organiza en cinco etapas encadenadas, con una verificación de viabilidad al inicio.

Etapa 0 — Verificación de viabilidad. Antes de comprometer el diseño, se comprueba experimentalmente que la captura acústica de la conversación es posible en dispositivos comerciales representativos, sobre al menos tres modelos de distintos fabricantes, evaluando la calidad de señal obtenida. El resultado de esta etapa condiciona el resto y por eso se ubica primero.

Etapa 1 — Marco conceptual y taxonomía. Relevamiento de modalidades de fraude telefónico vigentes en Argentina a partir de comunicados institucionales, material de organismos de defensa del consumidor, cobertura periodística y, de ser posible, entrevistas con personal de prevención de fraude. De ahí se deriva la taxonomía de técnicas de manipulación y el protocolo de anotación, validado midiendo el acuerdo entre dos anotadores independientes.

Etapa 2 — Construcción del corpus. Generación controlada de conversaciones fraudulentas siguiendo las estructuras de guion relevadas, con variación deliberada de registro, duración y grado de resistencia de la víctima simulada; recolección de conversaciones legítimas con consentimiento informado, incluyendo casos difíciles; vocalización mixta —parte sintética, parte leída por personas— y procesamiento del audio para reproducir las condiciones acústicas reales del despliegue. Anotación completa por turno.

Etapa 3 — Desarrollo del método. Implementación del método de referencia basado en palabras clave, que fija el piso de comparación; desarrollo del reconocimiento de técnicas de manipulación por intervención; y desarrollo del modelo de acumulación de riesgo, calibrando los umbrales de advertencia bajo la restricción de falsos positivos establecida.

Etapa 4 — Implementación del prototipo. Desarrollo de la aplicación Android sobre lo validado en la etapa 0, integrando el método desarrollado y la interfaz de usuario, con medición de consumo de memoria, latencia y batería en el dispositivo.

Etapa 5 — Evaluación. Evaluación cuantitativa sobre el corpus, con partición por conversación y comparación contra el método de referencia; y evaluación exploratoria de usabilidad con entre cinco y ocho personas del perfil objetivo, mediante llamadas simuladas en entorno controlado.

Una decisión de diseño transversal: la fuente de audio se implementa detrás de una interfaz única e intercambiable, de modo que el método pueda desarrollarse y evaluarse a partir de archivos del corpus con independencia del dispositivo. Esto permite avanzar en paralelo y reduce el riesgo de que un obstáculo de plataforma bloquee el trabajo experimental.

## 10. Resultados esperados

Se espera producir un corpus anotado de conversaciones telefónicas en español Argentino con etiquetado de técnicas de manipulación y marcación del momento crítico; una taxonomía operativa validada; un método de estimación incremental de riesgo con su evaluación comparada; un prototipo funcional instalable en dispositivos comerciales; y un informe de evaluación que reporte, además de las métricas de clasificación, la anticipación lograda y la caracterización del consumo de recursos en el dispositivo.

## 11. Consideraciones éticas y legales

El procesamiento es íntegramente local: ni el audio ni la transcripción abandonan el dispositivo, y ambos se descartan al finalizar cada llamada. El único dato persistido es un registro de eventos sin contenido conversacional.

El uso del sistema requiere consentimiento informado del usuario, y la eventual supervisión por parte de un familiar requiere emparejamiento explícito y visible para la persona protegida: se trata de asistencia consentida, no de vigilancia encubierta, y esa distinción se aborda expresamente en el trabajo.

Las voces reales incorporadas al corpus se registran con consentimiento informado firmado, y las conversaciones legítimas se anonimizan. El tratamiento de datos se enmarca en la Ley 25.326 de Protección de Datos Personales. El protocolo se someterá a consideración del comité de ética de la facultad antes de iniciar la recolección.

## 12. Recursos necesarios

Dispositivos Android de distintos fabricantes para desarrollo y pruebas, disponibles entre los autores. Equipamiento de cómputo con GPU para el entrenamiento de modelos, cubierto con recursos gratuitos en la nube dada la escala reducida de los modelos empleados. Herramientas de anotación y desarrollo de código abierto. Participación voluntaria de personas para la grabación de conversaciones legítimas y para la evaluación de usabilidad. No se requiere financiamiento.

## 13. Bibliografía preliminar

Referencias iniciales, a ampliar durante el desarrollo del marco teórico.
- Cialdini, R. B. Influence: The Psychology of Persuasion. — marco clásico sobre principios de persuasión aplicables a la taxonomía de manipulación.
- Documentación oficial de Android sobre compartición de entrada de audio y restricciones de captura durante llamadas activas.
- Documentación pública de Google sobre la función de detección de estafas en llamadas, como referencia de estado del arte industrial.
- Cañete, J. et al. — modelo BETO, representaciones preentrenadas para el español.
- Pérez, J. M. et al. — RoBERTuito, modelo preentrenado para español informal.
- Radford, A. et al. — Whisper, reconocimiento automático del habla multilingüe.
- Literatura sobre detección de phishing y ingeniería social basada en procesamiento de lenguaje natural, y sobre clasificación temprana de series y secuencias.
- Ley 25.326 de Protección de Datos Personales, República Argentina.
- Comunicados y material de difusión del BCRA y de organismos de defensa del consumidor sobre modalidades de fraude telefónico.
