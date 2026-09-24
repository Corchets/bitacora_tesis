# Detector de vishing en tiempo real para una tesis de Ingeniería Informática: factibilidad, diseño y hoja de ruta

## Diagnóstico ejecutivo y correcciones al planteo

La idea es **buena, actual y perfectamente defendible como tesis**, pero hay una modificación crítica que conviene hacer antes de escribir una sola línea de código: **no planteen como requisito central que una aplicación Android convencional pueda escuchar cualquier llamada telefónica celular del usuario**. En Android, el audio de subida y bajada de una llamada de voz está protegido por permisos reservados a componentes privilegiados del sistema. La documentación oficial indica que capturar `VOICE_CALL`, `VOICE_UPLINK` o `VOICE_DOWNLINK` requiere `CAPTURE_AUDIO_OUTPUT`, permiso no disponible para aplicaciones de terceros. Una aplicación ordinaria tampoco puede simplemente “escuchar en paralelo” el audio que utiliza la aplicación telefónica. citeturn19view3turn16search14

Esa limitación no invalida la tesis. Al contrario: permite separar correctamente **el problema científico** —detectar una estafa con información parcial y advertir a tiempo— del **problema de integración privilegiada con el sistema telefónico**, que depende de Google, Samsung, fabricantes u operadores. Mi recomendación es construir el detector como un motor independiente del origen del audio y demostrarlo en una **llamada VoIP controlada cuyo flujo de audio pertenece a la aplicación**, además de evaluarlo exhaustivamente sobre grabaciones reproducidas en tiempo real. Así pueden demostrar el funcionamiento completo sin prometer una capacidad que Android deliberadamente reserva al sistema.

A agosto de 2026 también hace falta actualizar algunas afirmaciones del borrador. La protección contra estafas ya no opera “casi exclusivamente antes de la llamada”. Google dispone de Scam Detection durante llamadas: analiza la conversación mientras ocurre, procesa los datos en el dispositivo y genera alertas cuando estima una alta probabilidad de estafa. Actualmente está restringido a Pixel; la documentación oficial lista Pixel 6 o posteriores en Estados Unidos y Pixel 9 o posteriores en varios países, incluidos México y España, pero **Argentina no aparece en la lista**. Google afirma además que no almacena ni envía a sus servidores el audio o la transcripción utilizados por Scam Detection. citeturn19view0 Samsung, por su parte, incorporó AI Scam Detection en dispositivos Galaxy con Android 16 y One UI 8.5 o superior, donde analiza patrones de llamadas en tiempo real y avisa mediante tono o vibración. citeturn19view1turn17search1

Por eso, el diferencial de la tesis **no debe ser “somos los primeros en analizar una llamada durante la conversación”**. Eso ya existe comercialmente y también académicamente. El diferencial defendible es mucho más interesante:

> **detección incremental, reproducible y explicable de vishing en español en escenarios argentinos, evaluada explícitamente por cuánto tiempo antes del evento crítico consigue intervenir, con inferencia local y una taxonomía de maniobras de ingeniería social.**

Ese planteo tiene suficiente contenido científico aun si el prototipo nunca llega a monitorear una llamada PSTN real en un Android comercial.

También recomiendo corregir otras afirmaciones del texto original:

| Afirmación actual | Problema | Redacción recomendable |
|---|---|---|
| “No hay software vulnerado, hay una conversación.” | Es demasiado absoluta. Una llamada puede terminar en robo de cuenta, instalación de acceso remoto o compromiso digital. UFECI documenta, por ejemplo, llamadas para obtener códigos de activación de WhatsApp. citeturn19view2 | “El vishing explota principalmente decisiones humanas durante una interacción de voz y puede culminar en divulgación de secretos, transferencias o compromiso posterior de cuentas y dispositivos.” |
| “Las defensas actuales operan casi exclusivamente antes de la llamada.” | Ya no es cierto en 2026: Google y Samsung tienen detección durante la llamada. citeturn19view0turn19view1 | “Las defensas basadas en reputación del número siguen siendo relevantes, pero recientemente aparecieron sistemas comerciales de análisis de contenido en tiempo real, restringidos a determinados ecosistemas.” |
| “Google y Samsung no cubren español.” | La evidencia pública actual no permite sostenerlo así. Google lista México y España para Scam Detection, aunque la página específica de llamadas no documenta claramente todos los idiomas soportados. citeturn19view0 | “La disponibilidad depende de dispositivo y región y, en la documentación consultada, Argentina no se encuentra entre los países habilitados por Google.” |
| “Clasificar una conversación completa es un problema resuelto.” | Demasiado fuerte. Un trabajo de MIS Quarterly publicado en 2026 sigue describiendo la detección como desafiante por la naturaleza en tiempo real y la escasez de datos. citeturn19view5 | “La clasificación offline de llamadas completas tiene antecedentes sólidos, pero la generalización, los datos disponibles y la detección temprana continúan siendo problemas abiertos.” |
| “Los adultos mayores son la población más afectada.” | No está demostrado así para Argentina con los datos que encontré. En datos de la FTC, las personas mayores incluso reportan pérdidas con menor frecuencia que grupos jóvenes, aunque las pérdidas cuando ocurren pueden ser mucho mayores y ciertos tipos de estafa las afectan desproporcionadamente. citeturn20search0turn20search6 | “Los adultos mayores constituyen una población de especial interés por la gravedad potencial de las pérdidas y su exposición a determinadas estafas de suplantación.” |

La dimensión argentina está bien justificada. UFECI recibió **34.468 reportes de delitos informáticos durante 2024**, un aumento interanual de 21,1%; 21.729 correspondieron a fraude en línea. El organismo describe específicamente llamadas en las que se solicita a las víctimas un código de WhatsApp bajo un supuesto proceso de verificación, que en realidad permite activar la cuenta en otro dispositivo. citeturn19view2 ANSES advierte expresamente que no solicita por teléfono datos personales ni bancarios, y PAMI mantiene recomendaciones específicas contra estafas dirigidas a sus afiliados. citeturn15search2turn15search5turn20search1

**Veredicto de factibilidad:**

| Componente | Factibilidad en cuatro meses | Evaluación |
|---|---:|---|
| Corpus propio en español | Alta | Totalmente viable si es simulado/representado |
| Taxonomía turno a turno | Alta | Es uno de los mejores aportes de la tesis |
| ASR completamente local | Alta | Ya existen motores adecuados |
| Clasificación incremental | Alta | Viable con modelos pequeños |
| Explicación de la maniobra | Alta | Mejor mediante etiquetas que mediante un LLM |
| Evaluación del tiempo de anticipación | Alta | Excelente contribución académica |
| Prototipo Android local | Alta | Si recibe un flujo de audio permitido |
| Demo durante llamada VoIP propia | Media-alta | Recomendable como integración final |
| Escuchar cualquier llamada celular en Android stock | Muy baja/no viable como app ordinaria | Restricción de la plataforma, no de su algoritmo citeturn19view3turn16search14 |
| Producto listo para Play Store | Baja | No debería ser objetivo de la tesis |
| Estudio grande con adultos mayores reales | Media-baja | Puede ser complemento, no dependencia crítica |

En otras palabras: **la tesis es viable; la versión “producto universal de Android que escucha llamadas celulares” no lo es.**

## Estado del arte y diferencial académico defendible

La investigación sobre vishing está creciendo muy rápidamente. En 2025 apareció una revisión específicamente titulada *Vishing: Detecting social engineering in spoken communication — A first survey & urgent roadmap to address an emerging societal challenge*, señal de que el área está pasando de estudios aislados a constituirse como un problema de investigación propio. citeturn18search0turn18search4

En 2026, Ampel, Samtani y Chen publicaron en *MIS Quarterly* VishGPT, un sistema específicamente orientado a detectar vishing en tiempo real. Los propios autores señalan que el problema es difícil tanto por su naturaleza temporal como por la limitada disponibilidad de datasets. En su evaluación reportan 86,18% de accuracy, 90,63% de precision, 85,02% de recall y 87,74% de F1, empleando además preentrenamiento con datos sintéticos. citeturn19view5 Es una referencia importante para ustedes precisamente porque demuestra dos cosas: que el problema es científicamente vigente y que **ni siquiera un modelo sofisticado permite afirmar que el problema esté “resuelto”**.

Otro antecedente especialmente relevante es el trabajo presentado en NDSS sobre scam-baiting calls. Los investigadores observaron progresiones consistentes entre etapas de las llamadas, compatibles con guiones relativamente estructurados; además simularon un escenario de reconocimiento durante una conversación entregando al modelo solamente las primeras intervenciones disponibles. Su conjunto de datos provenía de interacciones de scam-baiters de Estados Unidos, y los propios autores aclaran que esos participantes no representan perfectamente a víctimas reales. citeturn19view6 Para la tesis, ese trabajo es una excelente justificación de la idea de **acumulación temporal de evidencia**.

Los estudios psicológicos sobre vishing también muestran que no conviene reducir la detección a palabras como “transferencia” o “contraseña”. Investigaciones de ataques reales han identificado uso sistemático de autoridad, distracción, prueba social y otras técnicas persuasivas. citeturn12search4 Ese resultado encaja muy bien con su propuesta de explicar *qué maniobra está ocurriendo*, pero sugiero no copiar literalmente una taxonomía psicológica como etiqueta del detector. “Autoridad” es útil; “está pidiendo tu código de verificación mientras te presiona para que no cortes” es mucho más útil para una persona que está siendo estafada.

Existen además corpus de otros idiomas. Por ejemplo, KorCCVi v2 reúne llamadas de voice phishing y conversaciones legítimas en coreano con anotaciones a nivel de utterance, lo que demuestra que este tipo de recurso académico es viable. citeturn3search4 En la búsqueda realizada para este informe **no encontré un corpus público comparable específicamente orientado a vishing en español argentino que combine conversaciones, anotaciones turno a turno de maniobras y la marca temporal del evento crítico**. Esto debe redactarse prudentemente en la tesis como “no identificamos en la literatura revisada” y no como “no existe”, porque es un campo que está cambiando rápidamente.

### Qué existe frente a qué aportarían ustedes

| Área | Ya existe | Espacio útil para la tesis |
|---|---|---|
| Reputación de números | Caller ID, spam lists, bloqueo y reportes; Google continúa ofreciendo estas funciones. citeturn16search24 | No es el foco |
| Análisis durante llamada | Google Pixel y Samsung Galaxy recientes. citeturn19view0turn19view1 | Prototipo abierto/reproducible para investigación |
| Procesamiento local | Google declara análisis completamente on-device para Scam Detection. citeturn19view0 | Arquitectura local reproducible |
| Detección académica de vishing | VishGPT y otros trabajos recientes. citeturn19view5 | Español y escenarios argentinos |
| Modelado de etapas | Hay evidencia de progresiones y guiones. citeturn19view6 | Anotación explícita de eventos críticos |
| Persuasión | Se han estudiado principios psicológicos utilizados por atacantes. citeturn12search4 | Convertirlos en explicaciones operativas |
| Métrica principal | Predominan métricas clásicas de clasificación | Poner el **tiempo de intervención** en el centro |
| Corpus argentino/español | No identifiqué uno que reúna todos los requisitos anteriores | Corpus controlado y anotado |
| Producto comercial | Modelos cerrados y dependientes de fabricante | Código, metodología y experimentos reproducibles |

El diferencial más defendible no es entonces una sola innovación, sino la combinación:

**vishing en español + contexto argentino + procesamiento incremental + intervención explicable + evento crítico anotado + evaluación temporal + ejecución local.**

Esto también da origen a cuatro preguntas de investigación muy claras:

| Pregunta | Formulación propuesta |
|---|---|
| Detección parcial | ¿Con qué precisión puede detectarse vishing utilizando únicamente el prefijo de una conversación en español? |
| Anticipación | ¿Con cuánto margen temporal respecto del primer pedido/acción crítica puede generarse una alerta fiable? |
| Robustez al ASR | ¿Cuánto se degrada el detector al pasar de transcripciones manuales a transcripciones generadas localmente en tiempo real? |
| Explicabilidad | ¿Qué técnicas de manipulación y pedidos de alto riesgo pueden identificarse suficientemente bien como para generar una explicación contextual? |

Una quinta pregunta opcional sería el compromiso entre calidad y recursos computacionales: **¿qué combinación ASR + detector ofrece la mejor relación entre anticipación, precisión y latencia en un dispositivo móvil?**

Un título de tesis mucho más fuerte que “Sistema detector de Vishing” sería:

> **Detección incremental y explicable de vishing en conversaciones de voz en español mediante procesamiento local y evaluación del margen temporal de intervención**

Y si efectivamente consiguen suficiente diversidad geográfica en el corpus:

> **Detección incremental y explicable de vishing en español de Argentina: corpus anotado, procesamiento local y evaluación de alerta temprana**

No utilizaría “español rioplatense” si la mayoría de los participantes son de Tucumán u otras zonas que no corresponden lingüísticamente a esa variedad. “Español de Argentina” es más seguro, y aun eso debería estar respaldado por la composición del corpus.

## Alcance técnico y arquitectura recomendada

El principal riesgo técnico debe resolverse **durante la primera semana**, no en el tercer mes.

Android documenta explícitamente que una llamada de voz siempre conserva prioridad sobre el audio y que una aplicación privilegiada preinstalada con `CAPTURE_AUDIO_OUTPUT` puede capturar la llamada. Las fuentes `VOICE_CALL`, `VOICE_UPLINK` y `VOICE_DOWNLINK` requieren ese permiso, reservado a componentes del sistema. citeturn19view3turn16search14 Esto explica en parte por qué Google y Samsung pueden integrar funciones que una aplicación común de terceros no puede reproducir directamente.

No intentaría basar la tesis en accesibilidad como “truco” para eludirlo. Android permite algunos escenarios especiales de captura para servicios de accesibilidad, pero la documentación distingue claramente esa captura de la captura de uplink/downlink de la llamada. Además de ser técnicamente frágil, convertir una función de accesibilidad en mecanismo para escuchar conversaciones sería una mala base de ingeniería para un prototipo que pretende defender privacidad. citeturn19view3

La decisión de alcance que recomiendo es:

| Alternativa | Qué demostrarían | Recomendación |
|---|---|---|
| Motor sobre grabaciones reproducidas como stream | El algoritmo completo, incrementalidad, latencia y anticipación | **Obligatoria como base experimental** |
| Aplicación con llamada VoIP controlada | Funcionamiento durante una conversación real cuyo audio pertenece a la app | **Objetivo principal del prototipo** |
| Micrófono/altavoz en entorno de laboratorio | Concepto interactivo rápido | Útil al principio |
| AOSP/root/app de sistema | Acceso privilegiado a telefonía | Solo *stretch goal* |
| Aplicación Android stock escuchando cualquier llamada del dialer | Producto equivalente a una integración OEM | **Fuera de alcance** |

La arquitectura debería estar desacoplada del transporte:

```text
            ┌──────────────────────┐
            │   Flujo de audio     │
            │ RX / TX / grabación  │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ VAD / segmentación   │
            │ ventanas temporales  │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │     ASR local        │
            │ parciales + tiempos  │
            └──────────┬───────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │ Estado conversacional│
            │ turnos / contexto    │
            └──────────┬───────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
    ┌─────────────────┐  ┌─────────────────┐
    │ Riesgo de scam  │  │ Etiquetas de    │
    │     P(scam)     │  │ manipulación    │
    └────────┬────────┘  └────────┬────────┘
             └─────────┬─────────┘
                       ▼
            ┌──────────────────────┐
            │ Acumulador temporal  │
            │ umbral + histéresis  │
            └──────────┬───────────┘
                       ▼
            ┌──────────────────────┐
            │ Advertencia local    │
            │ motivo + acción      │
            └──────────────────────┘
```

La interfaz entre módulos debería ser independiente de Android. Por ejemplo, el detector puede recibir objetos conceptualmente equivalentes a:

```json
{
  "timestamp_start_ms": 35200,
  "timestamp_end_ms": 38100,
  "speaker": "remote",
  "text": "decime el código que te acaba de llegar y solucionamos el bloqueo",
  "asr_confidence": 0.81
}
```

Eso permite desarrollar y evaluar todo el modelo en Python primero, para después portar solamente la inferencia necesaria a Android.

### Reconocimiento de voz

Para un MVP local tienen alternativas suficientemente maduras. Vosk ofrece modelos offline y soporte para español; su modelo pequeño de español publicado ocupa aproximadamente 39 MB, por lo que constituye una excelente línea base para dispositivos modestos. Sus resultados publicados son de benchmarks generales, no específicamente de llamadas argentinas, así que deberán medir ustedes mismos el rendimiento sobre su corpus. citeturn6search5turn6search2

`whisper.cpp` permite ejecutar modelos Whisper localmente, soporta cuantización y tiene implementaciones orientadas a Android; su propia documentación recomienda modelos pequeños para entornos móviles. citeturn7search0turn7search3 Whisper no tiene por qué convertirse en otra tesis dentro de la tesis: pueden alimentarlo con ventanas cortas con solapamiento y consolidar fragmentos reconocidos.

Mi propuesta sería evaluar inicialmente:

| ASR | Función en la tesis |
|---|---|
| Vosk small Spanish | Baseline muy liviano |
| whisper.cpp tiny | Compromiso velocidad/calidad |
| whisper.cpp base | Candidato si el dispositivo mantiene tiempo real |

El ganador **no debe decidirse por reputación**, sino con un benchmark propio sobre 30-50 llamadas piloto: WER, reconocimiento de términos críticos, latencia y consumo de memoria.

Un detalle metodológico particularmente importante es que el WER global no cuenta toda la historia. Para su aplicación es mucho peor transcribir incorrectamente “código”, “token”, “transferencia” o el nombre de una herramienta de acceso remoto que equivocarse en una palabra irrelevante. Por eso agregaría una métrica propia de **recall de términos críticos**.

### Detector textual

No empezaría con un LLM. Para cuatro personas y cuatro meses, es muy probable que un LLM local complique inferencia, cuantización, memoria y evaluación sin aportar una ventaja proporcional.

Construiría tres niveles de baseline:

**Baseline interpretable:** reglas y expresiones de riesgo. Ejemplo: pedido de código + urgencia + suplantación.

**Baseline clásico:** TF-IDF de palabras/caracteres + regresión logística. Es rápido, pequeño y les da una línea base difícil de “hacer trampa” accidentalmente.

**Modelo principal:** un transformer español liviano ajustado al problema. El grupo que desarrolló BETO dispone también de ALBETO y DistilBETO; DistilBETO tiene 67 millones de parámetros y la familia ALBETO incluye modelos mucho más pequeños, pensados precisamente para reducir costo de entrenamiento e inferencia manteniendo rendimiento competitivo en tareas de español. citeturn14search10turn14academia26

El modelo principal puede ser **multi-task**:

\[
f(X_{1:t}) \rightarrow
\begin{cases}
P(\text{vishing}\mid X_{1:t})\\
P(\text{urgencia})\\
P(\text{suplantación})\\
P(\text{pedido de código})\\
P(\text{transferencia})\\
\dots
\end{cases}
\]

Así, una misma red entrega el riesgo y las razones utilizadas para explicarlo.

Una vez elegido el modelo, ONNX Runtime ofrece oficialmente un flujo para desplegar modelos ONNX en aplicaciones móviles, siempre que el modelo y sus operadores sean compatibles con el runtime y entren en memoria del dispositivo. citeturn14search3 Primero optimicen el modelo correcto; **la cuantización debe venir después**, no antes de disponer de una evaluación confiable.

### Estado temporal del riesgo

Este módulo es el verdadero corazón conceptual de la tesis.

No deberían calcular independientemente:

```text
turno 1 → 12 %
turno 2 → 84 %
turno 3 → 21 %
turno 4 → 89 %
```

y disparar cualquier valor mayor al umbral. Eso produciría alertas inestables.

Mantengan un estado acumulado. Una versión simple podría ser:

\[
R_t=\alpha R_{t-1}+(1-\alpha)P_t
\]

junto con reglas para eventos críticos. Una petición inequívoca de un OTP, una transferencia o la instalación de una aplicación remota puede elevar inmediatamente el riesgo aunque la puntuación textual general todavía sea moderada.

Otra alternativa que me gusta todavía más para una tesis es comparar dos estrategias:

1. **acumulador probabilístico**, que suaviza la salida del clasificador;
2. **máquina de estados explicable**, en la que combinaciones como autoridad → problema → urgencia → acción riesgosa cambian el estado de la conversación.

El segundo enfoque conecta muy bien con la literatura que encontró progresiones relativamente estructuradas en scam calls. citeturn19view6

No generaría las explicaciones con un modelo generativo. Usaría plantillas construidas a partir de las etiquetas:

> **Posible estafa: te están pidiendo un código de verificación mientras te apuran. No compartas el código. Cortá la llamada y verificá por un canal oficial.**

o

> **Alerta: la persona dice representar a una entidad y te pide transferir dinero para “proteger” tu cuenta. Verificá la situación por separado antes de realizar la operación.**

Ese mecanismo es más rápido, determinista, auditable y evita que un LLM invente una explicación.

### Qué dejar explícitamente fuera

No agregaría al MVP detección de voces clonadas, identificación biométrica del interlocutor, reputación del número, detección de spoofing, emotion recognition, análisis de WhatsApp/SMS, iOS, múltiples idiomas, modelos generativos conversacionales ni detección de malware.

Algunas de esas cosas son interesantes, pero responderían preguntas diferentes. Un deepfake puede utilizarse en una estafa, pero **una voz humana real puede realizar exactamente el mismo vishing**. El problema de su tesis es reconocer la manipulación y el pedido peligroso, no demostrar si las cuerdas vocales que produjeron el sonido eran humanas o sintéticas.

## Corpus, taxonomía y diseño experimental

El corpus puede terminar siendo uno de los activos académicos más importantes de la tesis.

Sin embargo, recomendaría llamarlo desde el inicio:

> **corpus de conversaciones simuladas/representadas de vishing y llamadas legítimas en español**

y no “corpus de llamadas reales de vishing” salvo que realmente consigan ese material con una base ética y jurídica sólida.

Conseguir conversaciones reales es difícil. El trabajo de scam-baiting de NDSS explica precisamente que las víctimas verdaderas normalmente no graban sus conversaciones, motivo por el que los investigadores recurrieron a interacciones públicas con scammers; también advierten que un scam-baiter no se comporta necesariamente como una víctima auténtica. citeturn18search2turn19view6 Para un trabajo de cuatro meses, las representaciones controladas son mucho más razonables.

### Tamaño alcanzable

No intentaría generar miles de llamadas humanas.

Propongo tres escalas:

| Nivel | Conversaciones | Audio aproximado | Interpretación |
|---|---:|---:|---|
| Mínimo defendible | 160 | 8-12 h | Suficiente para metodología + baselines |
| **Objetivo recomendado** | **240** | **12-16 h** | Buen equilibrio para cuatro meses |
| Stretch | 320+ | 18-25 h | Solo si la recolección marcha muy bien |

Para 240 llamadas, pueden hacer aproximadamente 120 fraudulentas y 120 legítimas. Ese balance sirve para experimentación, pero debe aclararse que **no representa la prevalencia de estafas en el mundo real**.

Intentaría conseguir entre 20 y 30 hablantes, mezclando roles y parejas. No necesitan que todos sean adultos mayores. De hecho, para desarrollar el detector sería mejor no convertir el reclutamiento de adultos mayores en un bloqueo del corpus. Posteriormente pueden incluir algunas voces de personas mayores en evaluación o realizar una prueba de usabilidad específica.

Los scripts deberían ser **semi-estructurados**, no leídos palabra por palabra. Por ejemplo, una ficha puede decir:

```text
Rol atacante:
- Fingís ser del banco.
- Decís que hubo una compra sospechosa.
- Generás urgencia.
- Pedís que la persona permanezca en línea.
- Intentás obtener un código ficticio.
- Si se niega, insistís una vez.

Rol víctima:
- No conocés la redacción exacta del atacante.
- Hacé preguntas naturales.
- Podés dudar.
- Finalmente aceptá o rechazá según la variante asignada.
```

Eso produce variabilidad lingüística mucho mayor que 200 personas leyendo el mismo libreto.

Las semillas de escenarios pueden basarse en patrones documentados oficialmente. UFECI describe la solicitud telefónica de códigos de activación de WhatsApp; ANSES advierte sobre suplantación de agentes que buscan datos; BCRA señala expresamente que los intentos de estafa pueden llegar mediante llamadas; PAMI mantiene instrucciones específicas contra estafas. citeturn19view2turn15search0turn14search24turn20search1

Un conjunto razonable de familias sería:

| Familia fraudulenta | Evento final |
|---|---|
| Banco: compra sospechosa | Código/token o transferencia |
| Banco: “cuenta comprometida” | Transferencia a supuesta cuenta segura |
| Billetera digital | Código/credencial |
| WhatsApp | Código de activación |
| ANSES/PAMI | Datos personales/bancarios |
| Soporte técnico | Instalar/control remoto |
| Familiar en emergencia | Transferencia |
| Premio/reintegro/beneficio | Datos o pago |
| Comercio/plataforma | “Validar” tarjeta o cuenta |

ANSES declara expresamente que no se comunica para solicitar datos personales o bancarios, por lo que es un excelente ejemplo de escenario de suplantación. citeturn15search2turn15search3

Pero **la mitad más importante del dataset quizá no sean las estafas sino los negativos difíciles**.

No utilicen solamente:

> “Hola, ¿cómo estás? Feliz cumpleaños.”

como llamada legítima.

Incluyan llamadas como:

> “Te llamamos por una operación sospechosa de tu tarjeta. Por seguridad no me digas ninguna clave; ingresá vos mismo a la app oficial.”

Eso contiene *banco*, *operación sospechosa*, *seguridad*, *tarjeta* y *urgencia*, pero es legítimo.

Otros hard negatives:

| Llamada legítima | Por qué es difícil |
|---|---|
| Banco avisando una anomalía sin pedir secretos | Comparte vocabulario con estafa |
| Familiar con situación urgente sin pedir dinero | Urgencia y emoción |
| Soporte real que guía una configuración inocua | Instrucciones técnicas |
| Turno médico/PAMI | Entidad sensible y datos personales mínimos |
| Entrega de paquete | Dirección/identidad |
| Cobranza legítima | Dinero + presión |
| Comercio resolviendo devolución | Reintegro + datos transaccionales |

Si entrenan solamente con “estafas muy obvias” frente a conversaciones sociales triviales obtendrán 98% de accuracy y un detector inútil.

### Taxonomía recomendada

No haría 30 etiquetas. En cuatro meses, las clases raras destruirían el análisis estadístico.

Usaría **dos capas multi-label**.

La primera representa técnicas de manipulación:

| Etiqueta | Qué debe observar el anotador |
|---|---|
| `IMPERSONATION_AUTHORITY` | Se presenta como entidad/persona con autoridad o confianza |
| `URGENCY_PRESSURE` | Impone tiempo, rapidez o consecuencias por demorar |
| `THREAT_FEAR` | Plantea pérdida, bloqueo, delito, sanción o peligro |
| `ISOLATION_SECRECY` | Pide no cortar, no consultar, no hablar con terceros |
| `TRUST_BUILDING` | Utiliza datos o procedimientos para parecer legítimo |
| `PERSISTENCE_DISTRACTION` | Insiste, redirige objeciones o mantiene al usuario cognitivamente ocupado |

La segunda representa **acciones solicitadas**, que son más directamente protectoras:

| Etiqueta | Ejemplos |
|---|---|
| `REQUEST_AUTH_CODE` | OTP, token, código de WhatsApp |
| `REQUEST_SECRET` | clave, PIN, CVV, contraseña |
| `REQUEST_PERSONAL_DATA` | DNI, domicilio, identificación |
| `REQUEST_TRANSFER` | transferencia, pago, cripto, efectivo |
| `REQUEST_REMOTE_ACCESS` | instalar acceso remoto, compartir pantalla |
| `REQUEST_SECURITY_ACTION` | abrir enlace, cambiar configuración, autorizar dispositivo |

La literatura de persuasión puede fundamentar conceptualmente la primera capa, pero las etiquetas operativas están diseñadas deliberadamente para que el sistema pueda explicarlas. citeturn12search4

Cada turno podría quedar anotado así:

```json
{
  "call_id": "SCAM_BANK_037",
  "turn_id": 11,
  "speaker": "attacker",
  "start_ms": 70200,
  "end_ms": 75400,
  "text": "No cortes porque se bloquea el procedimiento. Decime el código de seis dígitos.",
  "labels": [
    "URGENCY_PRESSURE",
    "ISOLATION_SECRECY",
    "REQUEST_AUTH_CODE"
  ],
  "critical_request": true
}
```

Añadiría tres tipos de marcas temporales extremadamente importantes:

\[
T_A=\text{momento de la alerta del sistema}
\]

\[
T_R=\text{inicio del primer pedido de alto riesgo}
\]

\[
T_C=\text{inicio de la primera acción de cumplimiento de la víctima}
\]

Por ejemplo:

```text
00:31 atacante: "tenemos que resolver esto ahora"     URGENCY
00:43 atacante: "no cortes la llamada"                ISOLATION
00:58 atacante: "decime el código que recibiste"      T_R
01:04 víctima:  "el código dice..."                    T_C
```

Si su sistema avisa en `00:47`, no alcanzó a anticipar el pedido, pero **sí protegió a la víctima antes de revelar el código**. Esa distinción es importantísima y mejora la idea original.

### La métrica central de la tesis

Definiría:

\[
L_R=T_R-T_A
\]

como anticipación respecto del primer pedido riesgoso, y

\[
L_C=T_C-T_A
\]

como margen de intervención antes de que la víctima empiece a cumplir.

Valores positivos son buenos.

Además:

\[
Preventive@\delta =
\frac{
\#\{i:T_{A,i}\leq T_{C,i}-\delta\}
}{
\#\{\text{llamadas de vishing}\}
}
\]

Por ejemplo:

- `Preventive@5s`
- `Preventive@10s`
- `Preventive@20s`

Responderían preguntas extremadamente fáciles de entender durante la defensa:

> “El 72% de las estafas fue advertido al menos diez segundos antes de la primera acción crítica.”

Ese resultado sería mucho más significativo para la tesis que simplemente:

> “Obtuvimos accuracy de 91,4%.”

La idea se relaciona directamente con el campo de *early classification*, cuyo objetivo es clasificar secuencias tan temprano como sea posible sin destruir el rendimiento predictivo. citeturn13search3

La evaluación completa debería contener:

| Dimensión | Métricas |
|---|---|
| ASR | WER, recall de términos críticos |
| Clasificación global | precision, recall, F1, AUPRC, AUROC |
| Llamadas legítimas | porcentaje con al menos una falsa alarma |
| Carga de falsas alarmas | falsas alertas por hora |
| Detección temporal | `Preventive@5/10/20s`, mediana de `L_R` y `L_C` |
| Evolución | métricas usando solo 25%, 50%, 75% y 100% de la llamada |
| Maniobras | macro-F1 de etiquetas multi-label |
| Latencia | p50/p95 desde audio hasta decisión |
| Rendimiento móvil | memoria, CPU, real-time factor |
| Explicación | correspondencia entre motivo mostrado y etiqueta real |

Para una alerta estable, definiría `T_A` como **la primera predicción sobre el umbral que se mantenga durante dos actualizaciones consecutivas**, o utilizaría histéresis. Esto evita que un pico aislado de 200 ms cuente fraudulentamente como una “detección temprana”.

### El experimento más importante: gold transcript frente a ASR

Ejecuten exactamente el mismo detector dos veces.

Primero:

```text
Transcripción manual perfecta
        ↓
Detector
        ↓
Resultado A
```

Después:

```text
Audio
 ↓
ASR local
 ↓
Detector idéntico
 ↓
Resultado B
```

La diferencia A-B cuantifica cuánto cuesta utilizar reconocimiento de voz real.

Eso les permite concluir, por ejemplo:

> El modelo de lenguaje detecta adecuadamente la manipulación, pero la principal fuente de fallos es el ASR.

o lo contrario:

> Incluso con transcripción perfecta, los primeros turnos no contienen suficiente evidencia.

Ambas serían conclusiones científicas valiosas.

### Evitar contaminación entre train y test

Este punto puede determinar la credibilidad completa de los resultados.

Supongan:

```text
Script original:
"Soy del banco y detectamos una compra sospechosa."

Variante A:
"Llamo del banco por una operación extraña."

Variante B:
"Tenemos una compra que necesitamos verificar."
```

Si A va a entrenamiento y B a test, el modelo prácticamente ya vio el escenario.

Por lo tanto, los splits deben hacerse por **familia/semilla de guion**, no por turno aleatorio. Todos los diálogos derivados de una misma semilla deben permanecer en el mismo split. Idealmente, los hablantes del test tampoco deberían aparecer en entrenamiento, o al menos deben realizar una evaluación adicional *speaker-disjoint*.

Una distribución razonable sería 60% entrenamiento, 20% validación y 20% test, agrupada por escenario y, donde sea posible, por hablante. El conjunto test debe “congelarse”: una vez creado, no se utiliza para elegir umbrales, modelos ni prompts.

Si usan un LLM para generar variaciones sintéticas, esas conversaciones pueden servir para **entrenamiento**, especialmente porque el uso de datos sintéticos ya aparece en trabajos modernos como VishGPT, pero el test debería permanecer humano y separado. citeturn19view5

Otra prueba muy interesante sería un test de **paráfrasis adversarial**: mantener la misma intención pero eliminar palabras obvias como “código”, “urgente” o “banco”. Estudios recientes ya están investigando ataques que reformulan conversaciones para reducir la efectividad de clasificadores de vishing manteniendo la intención fraudulenta. citeturn2search5

## Privacidad, ética, seguridad y experiencia de usuario

El objetivo “todo local” es acertado, pero deben definirlo con precisión.

Una llamada telefónica obviamente transmite audio al interlocutor. La promesa correcta es:

> **El sistema no transmite a servicios externos audio, transcripciones ni inferencias adicionales con fines de análisis; la cadena ASR → detección → explicación se ejecuta localmente.**

Google utiliza un diseño similar en su función de Scam Detection y declara que el procesamiento se realiza en el dispositivo sin almacenar ni enviar el audio o la transcripción utilizados por esa función. citeturn19view0 Eso constituye un precedente comercial fuerte de que el requisito de privacidad tiene sentido.

Sin embargo, “local” no significa automáticamente “sin obligaciones de privacidad”. La Ley argentina 25.326 establece que el tratamiento de datos personales requiere, como regla general, consentimiento libre, expreso e informado; también establece principios de seguridad, confidencialidad y eliminación de datos cuando dejan de ser necesarios para la finalidad por la que fueron recogidos. citeturn21search0 La AAIP también indica que debe informarse claramente finalidad, consecuencias, destinatarios y responsable del tratamiento. citeturn16search1

Para la tesis implementaría dos modos completamente diferentes:

| Modo | Comportamiento |
|---|---|
| **Investigación** | Guarda audio/transcripción únicamente de participantes consentidos, con ID pseudónimo |
| **Demostración/producción conceptual** | Audio en buffer temporal; transcripción y riesgo únicamente en memoria; no persistencia por defecto |

Las grabaciones de actores voluntarios deberían incluir un consentimiento que cubra explícitamente:

- grabación de voz;
- generación de transcripción;
- uso para entrenamiento/evaluación;
- quién tendrá acceso;
- período de conservación;
- eventual publicación de transcripciones;
- **por separado**, eventual publicación de audio.

No asumiría que dar consentimiento para “participar de la tesis” implica aceptar que la propia voz sea publicada como dataset.

No pondría en el repositorio audios de participantes. Mantendría un almacenamiento cifrado y separado del código. Los scripts utilizarían DNI, nombres, tarjetas, cuentas y códigos totalmente ficticios.

Tampoco recopilaría llamadas reales a empleados de bancos, PAMI, ANSES o comercios sin un esquema jurídico y de consentimiento muy claro. No necesitan hacerlo para responder las preguntas de investigación.

### Adultos mayores: cambiar la justificación, no abandonar el foco

La motivación sobre adultos mayores es válida, pero conviene evitar una formulación paternalista como:

> “son los que menos herramientas tienen”

si no tienen datos propios para demostrarlo.

La evidencia internacional es más matizada. La FTC reporta que los adultos mayores presentan menor tasa de pérdidas reportadas que adultos más jóvenes en el conjunto general, pero tienden a sufrir pérdidas individuales mayores; en estafas de suplantación con pérdidas muy grandes, los mayores están fuertemente sobrerrepresentados. En 2024, el 41% de los mayores que reportaron perder USD 10.000 o más frente a impostores de empresas o gobierno dijeron que el contacto inicial había sido una llamada telefónica. citeturn20search0turn20search6 En Argentina, PAMI mantiene un recurso específico para prevenir estafas y recomienda no compartir datos personales y comunicarse por sus canales oficiales ante sospechas. citeturn20search1

Una formulación académicamente más sólida sería:

> “El prototipo prioriza criterios de accesibilidad para adultos mayores, una población de especial interés por la severidad que pueden alcanzar determinadas estafas de suplantación. El trabajo no presupone menor capacidad de sus usuarios, sino que busca reducir la carga cognitiva de decidir bajo presión.”

Eso es mucho mejor defendible.

### El warning es parte del problema científico

No hagan solamente:

```text
⚠️ ESTAFA DETECTADA
```

Un warning ideal tiene tres componentes:

```text
QUÉ DETECTÉ
"Te están pidiendo un código de verificación"

POR QUÉ IMPORTA
"Compartirlo puede permitir que otra persona acceda a tu cuenta"

QUÉ HACER
"No lo compartas. Cortá y verificá por un canal oficial."
```

En una pantalla pequeña, mostraría como máximo **una o dos razones**.

Podrían usar niveles:

```text
RIESGO MODERADO
La persona está generando urgencia y dice representar a una entidad.

RIESGO ALTO
Te están pidiendo un código de seguridad.
No lo compartas.
```

Evitaría que el software corte automáticamente la llamada. Un falso positivo en una conversación bancaria legítima puede tener consecuencias y también disminuir la confianza en el sistema. Que el usuario mantenga el control es una decisión mucho más defendible para un prototipo académico.

Google reconoce explícitamente que su Scam Detection no es 100% preciso y que los atacantes cambian continuamente de tácticas. citeturn19view0 La falsa alarma no puede ser por tanto una métrica secundaria en su trabajo; debe estar junto a la sensibilidad.

Para una pequeña evaluación de usabilidad, no necesitan 100 adultos mayores. Un estudio formativo con un número reducido de participantes puede comparar dos diseños de warning y responder preguntas como:

> ¿Entendió qué estaba pasando?

> ¿Supo qué acción debía evitar?

> ¿La advertencia fue suficientemente visible?

> ¿La explicación fue más útil que un simple “posible estafa”?

No simularía pérdidas reales ni pediría información auténtica. Todos los códigos, cuentas y acciones deben ser ficticios, con consentimiento y debriefing.

Si no consiguen reclutar adultos mayores a tiempo, **el modelo no debe depender de ello para terminar la tesis**. La evaluación algorítmica puede completarse sobre el corpus, y la evaluación UX puede presentarse como estudio preliminar o trabajo futuro.

## Plan de cuatro meses, división del equipo y equipamiento

El mayor error posible sería hacer cuatro meses de trabajo secuencial:

```text
mes 1 corpus
→ mes 2 IA
→ mes 3 Android
→ mes 4 tesis
```

Necesitan cuatro líneas paralelas desde la primera semana.

### Cronograma recomendado

| Semanas | Trabajo principal | Resultado que debe existir |
|---|---|---|
| 1 | Spike técnico de audio, revisión bibliográfica, alcance | Decisión definitiva: VoIP/replay como integración |
| 2 | Taxonomía v0, scripts piloto, consentimiento, arquitectura | Vertical slice mínimo funcionando |
| 3-4 | Corpus piloto + ASR benchmark + baseline de reglas | 30-50 llamadas anotadas y primer detector |
| 5-6 | Recolección masiva + TF-IDF + modelo transformer inicial | Corpus >100 llamadas y resultados comparativos |
| 7-8 | Completar corpus + acumulación temporal + ASR elegido | Dataset prácticamente congelado |
| 9-10 | Integración Android/VoIP + exportación móvil | Audio → ASR → riesgo → warning en dispositivo |
| 11 | Hard negatives, tuning con validation, instrumentación | Prototipo candidato final |
| 12-13 | Test congelado, ablations, latencia, errores | Todas las tablas/figuras principales |
| 14 | Evaluación UX/accesibilidad y casos de fallo | Resultados de interacción |
| 15 | Escritura intensiva y reproducción de experimentos | Borrador completo |
| 16 | Correcciones, demo, defensa, contingencias | Release final |

La **semana uno** debe incluir un spike extremadamente sencillo:

```text
WAV de una llamada
   ↓
ASR local
   ↓
buscar "código"
   ↓
mostrar alerta
```

No importa que sea tonto. Si esa vertical slice existe durante los primeros días, ya comprobaron la cadena tecnológica fundamental.

La semana siguiente pueden reemplazar “buscar código” por el detector real sin modificar toda la aplicación.

### Reparto entre cuatro personas

No dividiría la tesis en cuatro silos totalmente independientes, pero sí establecería un responsable primario por subsistema:

| Integrante | Responsabilidad principal | Responsabilidad secundaria |
|---|---|---|
| A | Corpus, scripts, protocolo de anotación, privacidad | Error analysis |
| B | NLP/ML, baselines, multi-label, calibración | Métricas |
| C | Audio, VAD, ASR, rendimiento móvil | Integración VoIP |
| D | Android, motor temporal, warning/UX, integración | Infraestructura/evaluación |

Hay dos áreas que deberían tener siempre dos personas:

**Corpus:** A responsable + B revisor.

**Integración end-to-end:** C + D.

Así, si una persona se atrasa o algo no funciona, no existe un módulo que solamente entienda un integrante.

Todo el equipo debe participar de la anotación piloto. Si cuatro personas anotan los mismos 10-20 diálogos al principio, van a descubrir rápidamente frases ambiguas y definiciones defectuosas. Después pueden dual-annotar una fracción del corpus y adjudicar discrepancias.

Una dinámica semanal razonable sería:

```text
inicio de semana:
objetivos y experimentos

mitad:
integración

fin:
demo del sistema + resultados nuevos
```

Cada viernes debería poder demostrarse algo que no existía el viernes anterior. Eso evita pasar tres semanas “mejorando la arquitectura” sin obtener resultados.

### Hardware necesario

No necesitan un laboratorio costoso.

| Elemento | Cantidad | Necesidad |
|---|---:|---|
| Laptops de desarrollo | 4 | Ya deberían bastar |
| Android físico relativamente reciente | 1 mínimo, 2 ideal | **Necesario** para inferencia/audio real |
| Segundo teléfono o laptop | 1 | Interlocutor de la llamada VoIP |
| Auriculares con micrófono | 2 | Muy útiles para corpus/pruebas |
| Almacenamiento cifrado | 1 | Corpus y backups |
| GPU NVIDIA | 1 opcional | Facilita fine-tuning, pero no es requisito |
| Servidor | 0 | No es necesario para inferencia |
| Equipo de telefonía especial | 0 | No es necesario |

Android recomienda probar grabación de audio en hardware real; su emulador no es sustituto para estas pruebas. citeturn16search8

Como dispositivo de evaluación, tendría idealmente dos extremos:

**un teléfono relativamente modesto**, para demostrar que no diseñaron exclusivamente para hardware premium;

**un teléfono más potente**, como referencia y backup.

No hace falta comprar específicamente un Pixel a menos que quieran experimentar con AOSP o comparar la experiencia de Google. Para su implementación normal, cualquier Android ARM64 razonablemente moderno puede servir; la capacidad exacta deberá determinarse al benchmarkear los modelos.

Para entrenar un clasificador lineal no necesitan GPU. Para ajustar DistilBETO/ALBETO, disponer de GPU hace el proceso mucho más cómodo, pero entrenamiento e inferencia son problemas diferentes. Pueden entrenar en una workstation universitaria y seguir afirmando correctamente que **la inferencia del prototipo es local**. Los datos con información de participantes no deberían subirse a servicios externos salvo que el consentimiento y la política de tratamiento lo permitan.

### Stack recomendable

No complicaría el stack:

```text
Investigación / entrenamiento
Python
PyTorch / Transformers
scikit-learn
pandas
scripts propios de evaluación

ASR
whisper.cpp
y/o Vosk

Modelo móvil
ONNX Runtime

Aplicación
Kotlin
Android Studio

Datos
WAV/FLAC
JSONL de anotaciones
CSV/Parquet para experimentos

Control
Git
tests
CI
```

Vosk está diseñado para reconocimiento offline, mientras que whisper.cpp está orientado a inferencia local eficiente y ofrece cuantización; ONNX Runtime dispone de soporte oficial para despliegue móvil. citeturn6search5turn7search0turn14search3

Una estructura inicial de repositorio que luego pueden trasladar prácticamente sin cambios a Codex sería:

```text
vishing-thesis/
│
├── docs/
│   ├── research/
│   ├── taxonomy/
│   ├── ethics/
│   └── architecture/
│
├── data/
│   ├── schemas/
│   ├── scripts/
│   └── README.md
│
├── annotation/
│
├── asr/
│   ├── benchmarks/
│   └── adapters/
│
├── detector/
│   ├── rules/
│   ├── classical/
│   ├── transformer/
│   └── temporal/
│
├── evaluation/
│   ├── early_detection/
│   ├── classification/
│   ├── latency/
│   └── error_analysis/
│
├── mobile/
│
├── voip_demo/
│
├── experiments/
│
├── tests/
│
└── thesis/
```

No pondría `data/raw_audio/` dentro de Git. El repositorio puede guardar IDs y manifiestos; los audios deben estar en almacenamiento controlado.

Además, desde el primer experimento guarden:

```text
commit
modelo
dataset_version
split
seed
configuración
métricas
fecha
```

La reproducibilidad puede parecer burocracia ahora, pero en la semana trece evitará la pregunta clásica:

> “¿Con cuál de los seis checkpoints generamos esa tabla que quedó tan bien?”

## Riesgos, criterios de éxito y especificación final recomendada

El proyecto tiene un riesgo dominante y varios secundarios. Todos son manejables si se deciden temprano.

| Riesgo | Impacto | Probabilidad | Mitigación |
|---|---|---|---|
| No poder capturar llamadas PSTN en Android | Crítico | Prácticamente seguro para una app ordinaria | VoIP controlado + motor desacoplado; documentar limitación de plataforma. citeturn19view3turn16search14 |
| Corpus poco realista | Alto | Alta | Role-play semi-improvisado, speakers múltiples, ruido y hard negatives |
| Dataset demasiado pequeño | Alto | Media | Pretrained models + baseline clásico + datos sintéticos solo para training |
| Leakage entre scripts | Crítico para la validez | Alta si hacen split aleatorio | Split por familia/semilla y hablante |
| Falsos positivos | Alto | Alta | Hard negatives, calibración, histéresis, medir falsa alarma explícitamente |
| ASR falla con español/localidad/ruido | Alto | Media-alta | Benchmark Vosk vs Whisper + gold-vs-ASR |
| Modelo demasiado pesado | Medio | Media | TF-IDF/ALBETO/DistilBETO, ONNX, cuantización |
| Querer detectar deepfakes además | Alto | Alta tentación | Declararlo fuera de alcance |
| Reclutamiento de adultos mayores | Medio | Media | Hacer UX adicional, no dependencia del detector |
| Problemas de privacidad | Crítico | Evitable | Consentimiento, datos ficticios, almacenamiento seguro, minimización. citeturn21search0 |
| Atacantes cambian lenguaje | Alto a largo plazo | Seguro en despliegue real | Evaluar paráfrasis/out-of-distribution y reconocer limitación; incluso Google advierte que los scammers cambian sus tácticas. citeturn19view0 |

### Qué consideraría una tesis exitosa

No pondría como condición:

> “Accuracy superior al 95%.”

Eso podría obligarlos a ajustar el corpus para conseguir un número bonito.

La tesis es exitosa si al terminar demuestra rigurosamente lo siguiente:

| Entregable | Condición |
|---|---|
| Corpus | Conversaciones fraudulentas y benignas, esquema documentado y test congelado |
| Taxonomía | Etiquetas operativas con manual de anotación |
| Baselines | Reglas + modelo clásico + al menos un modelo neuronal |
| ASR | Al menos dos configuraciones comparadas localmente |
| Detección | Funcionamiento incremental, no solo al terminar la llamada |
| Timing | `T_A`, `T_R`, `T_C` y métricas de anticipación |
| Explicación | Warning derivado de técnicas/acciones detectadas |
| Privacidad | Inferencia sin API externa |
| Prototipo | Funcionamiento end-to-end en dispositivo o entorno móvil controlado |
| Evaluación | Clasificación, falsa alarma, anticipación y latencia |
| Reproducibilidad | Código/configuración/splits/versiones |
| Limitaciones | Discusión honesta de Android, simulación y generalización |

Y algo importante: **un resultado negativo también puede ser una buena tesis**.

Supongan que terminan demostrando:

> “El modelo obtiene buen F1 global pero solo detecta el 35% de las llamadas diez segundos antes de la acción crítica.”

Eso sigue siendo muy interesante. Demuestra que la clasificación convencional sobreestima la utilidad práctica de un detector.

O podrían descubrir:

> “Con transcripción manual se detecta temprano, pero con ASR móvil el desempeño cae 18 puntos.”

La conclusión sería que la barrera está en speech recognition.

O:

> “Los clasificadores semánticos mejoran muy poco a un sistema basado en seis reglas de alto riesgo.”

También sería un resultado válido y útil.

La tesis no debe demostrar que ya construyeron un producto comercial. Debe responder una pregunta científica de manera reproducible.

### Alcance que congelaría desde ahora

**Núcleo obligatorio**

```text
Español
        +
vishing semántico
        +
corpus simulado y anotado
        +
ASR local
        +
clasificación incremental
        +
técnicas de manipulación
        +
evento crítico
        +
margen de anticipación
        +
advertencia explicable
        +
prototipo móvil/controlado
```

**Stretch goals**

```text
VoIP totalmente integrado
cuantización avanzada
features prosódicas
evaluación con adultos mayores
escenarios adversariales
AOSP privilegiado
```

**Fuera de alcance**

```text
monitorización universal de llamadas PSTN Android
iOS
detección de deepfake
caller-ID reputation
malware detection
SMS / WhatsApp chat
producto para Play Store
múltiples idiomas
backend de producción
```

Esta división es especialmente importante porque, con cuatro integrantes, es muy fácil mirar el proyecto y pensar que “también podríamos agregar deepfake”. No. Cada agregado debe competir contra la pregunta:

> **¿Mejora nuestra capacidad de responder cuánto antes de una acción crítica podemos detectar la ingeniería social?**

Si la respuesta es no, se posterga.

### Objetivo general que recomiendo

Reformularía su objetivo actual así:

> **Diseñar, implementar y evaluar un prototipo capaz de analizar incrementalmente un flujo de audio de una conversación de voz en español, mediante procesamiento de inferencia local, para estimar el riesgo de vishing, identificar maniobras de ingeniería social y emitir una advertencia contextual antes de una acción crítica, cuantificando su precisión, tasa de falsas alarmas, latencia y margen temporal de intervención.**

Y agregaría explícitamente al alcance técnico:

> **La evaluación en tiempo real se realizará sobre un entorno de llamadas controlado en el que el prototipo tenga acceso legítimo al flujo de audio. La integración con llamadas celulares de aplicaciones telefónicas del sistema queda fuera del alcance debido a las restricciones de captura de audio de las plataformas móviles.**

Eso les evita una objeción potencialmente devastadora durante la defensa.

### Objetivos específicos recomendados

La descomposición natural es:

| Objetivo específico | Resultado |
|---|---|
| Construir una taxonomía operacional de vishing | Manual de etiquetas |
| Construir un corpus anotado en español | Dataset |
| Evaluar ASR offline/local | Benchmark |
| Desarrollar baselines de clasificación | Referencias |
| Desarrollar detector incremental | Modelo central |
| Diseñar política de intervención | `T_A` y warning |
| Implementar inferencia local | Prototipo |
| Evaluar anticipación | `Preventive@δ`, `L_R`, `L_C` |
| Evaluar explicaciones | Etiquetas/UX |
| Analizar limitaciones | Discusión científica |

### Hipótesis razonables

En vez de formular una hipótesis vaga como “la IA puede detectar vishing”, podrían trabajar con:

> **H1:** la incorporación de contexto acumulado de turnos mejora la detección respecto de clasificar cada turno de manera independiente.

> **H2:** una proporción significativa de intentos de vishing puede identificarse antes de la primera acción crítica del usuario.

> **H3:** el uso de transcripción ASR local degrada el rendimiento respecto de transcripciones manuales, pero mantiene capacidad de intervención útil.

> **H4:** un clasificador multi-label de maniobras permite producir advertencias específicas sin recurrir a generación libre de texto.

No es necesario que todas resulten verdaderas.

### Qué deberían hacer literalmente al comenzar

Durante los **primeros diez días**, yo intentaría llegar a este estado:

```text
[ ] Alcance de la tesis firmado por los cuatro
[ ] PSTN universal declarado fuera de alcance
[ ] Diagrama de arquitectura
[ ] Taxonomía v0
[ ] Definición formal de evento crítico
[ ] 10 scripts de scam
[ ] 10 scripts benignos
[ ] Consentimiento/protocolo de datos
[ ] 20-30 conversaciones piloto
[ ] Transcripción/anotación piloto
[ ] Vosk benchmark
[ ] whisper.cpp benchmark
[ ] Regla "pedido de código" funcionando
[ ] TF-IDF baseline
[ ] Primer gráfico riesgo vs tiempo
[ ] Primer cálculo de T_alert y T_critical
[ ] App/demo capaz de mostrar una alerta
```

Ese primer **gráfico riesgo vs tiempo** debería aparecer muy temprano. Conceptualmente:

```text
riesgo
1.0 |                             █████████
    |                        █████
0.8 |                   █████
    |              █████
0.6 |         █████
    |
0.4 |    ████
    |
0.2 |████
    |
0.0 +-------------------------------------- tiempo
        autoridad   urgencia     código
                      ↑            ↑
                   ALERTA       CRÍTICO
```

Todo el resto del proyecto es, en esencia, lograr que esa figura sea científicamente válida.

### La tesis que yo intentaría defender

La narrativa final debería ser aproximadamente ésta:

> Los detectores tradicionales basados en metadatos de llamadas no pueden reconocer por sí mismos una estafa originada desde un número todavía no reputado. Sistemas comerciales recientes demuestran que el análisis de contenido durante la llamada es técnicamente posible, pero su disponibilidad depende del ecosistema y su evaluación interna no es reproducible públicamente. Google, por ejemplo, ofrece actualmente Scam Detection on-device únicamente en determinados dispositivos y países, sin incluir Argentina en la lista publicada. citeturn19view0 Samsung también dispone de detección basada en IA en dispositivos recientes. citeturn19view1

> La literatura académica reciente confirma que la detección automatizada de vishing en tiempo real es un área activa y todavía condicionada por la disponibilidad de datos. citeturn18search0turn19view5 Asimismo, se ha observado que las llamadas fraudulentas pueden presentar progresiones estructuradas y técnicas de manipulación identificables. citeturn19view6turn12search4

> Sobre esa base, este trabajo estudia un problema más específico: determinar si esas señales permiten intervenir **antes** de que ocurra una acción de riesgo. Para ello se construye un corpus controlado de conversaciones en español, se anotan maniobras y eventos críticos, se implementa una cadena de reconocimiento de voz y clasificación incremental con inferencia local, y se evalúan conjuntamente precisión, falsas alarmas, latencia y margen temporal de intervención.

Eso es una tesis coherente. Tiene **ciberseguridad, inteligencia artificial, procesamiento de lenguaje natural, speech-to-text, sistemas móviles, privacidad, HCI, ingeniería de software y evaluación experimental**, pero todos esos componentes están subordinados a una sola pregunta central.

Y, sobre todo, es realizable por cuatro personas en cuatro meses siempre que no intenten convertirla en un producto comercial universal.

**La decisión más importante para empezar es congelar desde el primer día que el aporte principal es el detector incremental y su evaluación temporal; la telefonía celular privilegiada de Android es una limitación de integración y no el problema que la tesis pretende resolver.** Android confirma que las fuentes de audio de una llamada están reservadas a componentes privilegiados, mientras que los productos de Google demuestran que el análisis local durante llamadas es viable cuando se dispone de integración a nivel del sistema. citeturn19view3turn16search14turn19view0