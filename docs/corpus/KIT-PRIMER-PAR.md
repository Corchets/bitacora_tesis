# Kit para producir y revisar el primer par de llamadas (Hito H2)

Este documento es el kit operativo para preparar, simular, registrar y revisar el
**primer par de conversaciones contrastantes** del proyecto:
- **Llamada fraudulenta:** semilla `SC-WA-CODE-01` (suplantación de soporte para obtener código de WhatsApp).
- **Llamada legítima difícil:** semilla `LG-WA-CONSULTA-01` (consulta a una persona conocida por código inesperado).

Su objetivo es comprobar el método de producción y anotación humana sobre un caso concreto antes de
escalar al piloto completo ([issue #54](https://github.com/Corchets/bitacora_tesis/issues/54)),
dejando el par listo para alimentar los experimentos de ASR local y *replay* en *streaming*.

> [!IMPORTANT]
> **Condición de inicio: Validación del tutor pendiente ([D06](../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto))**  
> La grabación de audio con participantes humanos está condicionada a la validación formal del Ing. Ernesto Rico
> sobre el protocolo de consentimiento, participantes y resguardo local (registrada en la agenda de
> [seguimiento del 2026-09-30](../gestion/seguimientos/2026-09-30.md)).  
> Este kit deja todos los materiales, fichas y procedimientos técnicos listos para su uso inmediato una vez otorgada dicha aprobación.
> **No se debe encender el grabador ni solicitar firmas antes de contar con esa validación.**

---

## 1. Verificación del par escrito

Antes de grabar, se verificó la coherencia del par entre las distintas fuentes del repositorio:
1. `docs/ingenieria/ARQUITECTURA.md` §4 (diálogos ilustrativos F1–F5 y L1–L4, y referencia conceptual).
2. `docs/corpus/CATALOGO-ESCENARIOS.csv` (semillas `SC-WA-CODE-01` y `LG-WA-CONSULTA-01`).
3. `experiments/slm-directo/casos/texto/` (`SC-WA-CODE-01-e01.txt` y `LG-WA-CONSULTA-01-e01.txt`).
4. `experiments/slm-directo/casos/referencia/` (`SC-WA-CODE-01-e01.json` y `LG-WA-CONSULTA-01-e01.json`).

### Tabla de coherencia del par

| Dimensión | Fuente 1: [ARQUITECTURA §4](../ingenieria/ARQUITECTURA.md#4-primer-par-escrito-del-escenario-al-aviso) | Fuente 2: [Catálogo](CATALOGO-ESCENARIOS.csv) | Fuentes 3 y 4: Texto y Referencia en `experiments/slm-directo` | Coherencia / Estado |
|---|---|---|---|---|
| **ID Semilla Fraudulenta** | `SC-WA-CODE-01` (enlace implícito) | `SC-WA-CODE-01` (fila 3) | [`SC-WA-CODE-01`](../../experiments/slm-directo/casos/referencia/SC-WA-CODE-01-e01.json) (caso `SC-WA-CODE-01-e01`) | **Coherente** |
| **Título Fraudulenta** | Suplantación de soporte de WhatsApp | Verificacion falsa de WhatsApp | "Pedido directo del código de activación, con contexto previo de soporte y urgencia" | **Coherente** (variación editorial menor) |
| **Clase Fraudulenta** | `vishing` | `vishing` | `vishing` | **Coherente** |
| **Acción Crítica Fraudulenta** | `REQUEST_AUTH_CODE` (F4) | `REQUEST_AUTH_CODE` | `REQUEST_AUTH_CODE` (línea 4) | **Coherente** |
| **Ubicación `T_R` Fraudulenta** | F4, desde «Decime» | No aplica (catálogo de escenarios) | Línea 4 (`t_r_linea: 4`) | **Coherente** (posición textual sin audio) |
| **Ubicación `T_C` Fraudulenta** | F5, desde el primer «cero» | No aplica | Línea 5 (`t_c_linea: 5`) | **Coherente** (posición textual sin audio) |
| **Maniobras / Evidencia Fraudulenta** | Contexto F1–F3, pedido F4, cumplimiento F5 | `TRUST_BUILDING;URGENCY_PRESSURE` | Línea 1: `AUTHORITY_CLAIM`; Línea 3: `URGENCY_PRESSURE`; Línea 4: `REQUEST_AUTH_CODE` | **Discrepancia:** Catálogo declara `TRUST_BUILDING` pero la referencia escrita etiqueta `AUTHORITY_CLAIM`. Ver §7. |
| **ID Semilla Legítima Difícil** | `LG-WA-CONSULTA-01` (enlace implícito) | `LG-WA-CONSULTA-01` (fila 15) | [`LG-WA-CONSULTA-01`](../../experiments/slm-directo/casos/referencia/LG-WA-CONSULTA-01-e01.json) (caso `LG-WA-CONSULTA-01-e01`) | **Coherente** |
| **Título Legítima** | Consulta legítima a una persona conocida | Consulta legitima por codigo inesperado de WhatsApp | "Habla del mismo código de WhatsApp, pero para no compartirlo" | **Coherente** |
| **Clase Legítima** | `legitima_dificil` | `legitima_dificil` | `legitima_dificil` | **Coherente** |
| **Acción Crítica Legítima** | Ausente | `NONE` | `null` | **Coherente** |
| **Ubicación `T_R` y `T_C` Legítima** | Ausente / Ausente | No aplica | `t_r_linea: null`, `t_c_linea: null` | **Coherente** |
| **Maniobras / Evidencia Legítima** | Mención de código, consejo de no compartirlo y rechazo explícito | `AUTHORITY_CLAIM` | Eventos: mención (l. 1), contexto (l. 2), rechazo (l. 4); sin etiquetas de maniobra (`etiquetas: []`) | **Discrepancia:** Catálogo lista `AUTHORITY_CLAIM`, pero entre conocidos no aplica según el manual. Ver §7. |
| **Granularidad de Actualizaciones** | Actualizaciones agrupadas U1 (F1–F2), U2 (F3), U3 (F4), U4 (F5) | No aplica | Turno a turno cerrado: 5 líneas independientes en fraude, 4 líneas en legítima | **Diferencia documentada:** `#50` adoptó evaluación por turno cerrado. |

---

## 2. Fichas de rol separadas e imprimibles

De acuerdo con el [método de creación del corpus](METODO-CREACION-CORPUS.md#5-fichas-de-rol):
- Cada interlocutor recibe **únicamente su ficha de rol**, sin leer la de la otra persona.
- Las fichas no contienen textos rígidos que deban memorizarse palabra por palabra: orientan los objetivos, límites, datos y actitudes.
- **Principio de realismo:** En la llamada fraudulenta, a quien atiende (**Rol B**) **NO se le informa de antemano que se trata de un intento de estafa ni la clase de la llamada**. Solo conoce su situación inicial (recibió un SMS imprevisto) y su actitud asignada.
- Ambas personas conocen la condición de parada: terminar inmediatamente tras la respuesta al pedido o al consejo seguro, o ante cualquier indicación de detener la toma.

---

### FICHA DE ROL 1A (IMPRIMIBLE)
**Llamada:** 1 (Semilla `SC-WA-CODE-01`)  
**Rol:** A — Quien inicia la llamada (Suplantador de soporte)  
**Entregar a:** Participante asignado al Rol A

#### 1. Tu situación (Lo que sabés)
- Te hacés pasar por un representante del «Soporte Técnico de WhatsApp».
- Tu objetivo es lograr que la otra persona te dicte el código de activación de 6 dígitos que acaba de recibir por mensaje de texto (SMS).
- Sabés que para convencerla vas a inventar que alguien intentó activar su cuenta desde otro teléfono y que, para frenar o cancelar esa activación no autorizada, necesitás verificar el código ya mismo.

#### 2. Lo que NO sabés
- No sabés cómo va a reaccionar la otra persona: puede dudar, hacer preguntas, pedir explicaciones o aceptar rápidamente.

#### 3. Tu objetivo en la llamada
- Obtener el código de activación de 6 dígitos que la persona tiene en su teléfono (`REQUEST_AUTH_CODE`).

#### 4. Cómo actuar y respuestas permitidas
- **Inicio:** Presentate con tono formal y profesional de mesa de ayuda («Te llamo de soporte por la activación de tu cuenta de WhatsApp»).
- **Presión temporal:** Creá urgencia creíble; planteá que si no se resuelve en este momento, la cuenta se activará en el otro dispositivo («Para cancelar esa activación tenemos que resolverlo ahora»).
- **Pedido:** Pedile directamente que te lea o te dicte el código recibido («Decime el código de activación que recibiste por SMS»).
- **Ante dudas o preguntas:** Mantené la calma, reforzá la supuesta urgencia técnica y explicá que el código es indispensable para cancelar la operación.
- **Si acepta y te dicta el código:** Escuchalo con atención, agradecé brevemente y finalizá la llamada.
- **Si rechaza firmemente:** No insistas agresivamente ni salgas del personaje; cerrá la llamada («Entendido, el trámite queda cancelado»).

#### 5. Límites estrictos y datos ficticios autorizados
- **PROHIBIDO** pedir contraseñas, PIN de cajero, dinero, transferencias bancarias o datos de tarjetas.
- **PROHIBIDO** enviar o pedir que abran enlaces externos o que instalen programas de acceso remoto (TeamViewer, AnyDesk, etc.).
- **PROHIBIDO** usar nombres de personas reales o datos personales verdaderos.
- **Datos ficticios permitidos:** Entidad: «Soporte de WhatsApp». Motivo: «Cancelación de activación no solicitada».

#### 6. Condición de cierre
- Cortar la comunicación inmediatamente después de que te dicten el código ficticio, o cuando la persona se niegue de forma concluyente, o si el operador de la toma indica detenerla.

---

### FICHA DE ROL 1B (IMPRIMIBLE)
**Llamada:** 1 (Semilla `SC-WA-CODE-01`)  
**Rol:** B — Quien atiende la llamada (Usuario)  
**Entregar a:** Participante asignado al Rol B

#### 1. Tu situación (Lo que sabés)
- Estás en tu casa o trabajo y hace dos minutos recibiste en tu celular una notificación de SMS con un código de activación de WhatsApp.
- Vos **no pediste activar nada** ni cambiaste de teléfono, por lo que el mensaje te resultó extraño.
- En este momento suena tu teléfono y atendés la llamada.

#### 2. Lo que NO sabés
- No sabés quién te llama ni con qué motivo exacto hasta que te lo digan al atender.

#### 3. Tu objetivo en la llamada
- Averiguar quién te está llamando y por qué te llegó ese mensaje que vos nunca solicitaste.

#### 4. Actitud y cómo actuar
- **Actitud asignada:** Cautelosa y con dudas, pero persuadible ante explicaciones técnicas convincentes.
- **Reacción inicial:** Manifestá extrañeza («Me acaba de llegar un SMS. No pedí activar nada»).
- **Ante las explicaciones del llamante:** Podés preguntar para qué necesitan el código o manifestar cierta duda («¿Pero por qué me piden el código si yo no toqué nada?»).
- **Resolución:** Si la persona que llama te explica con seguridad y urgencia que ese código es necesario para frenar el intento de robo de la cuenta, cedé ante la presión y dictá el código ficticio autorizado.

#### 5. Límites estrictos y datos ficticios autorizados
- **DATO OBLIGATORIO Y EXCLUSIVO:** Si decidís dictar el código, dictá **únicamente** la cifra ficticia:  
  **`0 0 0 0 0 0`** (cero, cero, cero, cero, cero, cero).
- **TERMINANTEMENTE PROHIBIDO:**
  - Dictar códigos reales que hayas recibido en llamadas o mensajes personales.
  - Mencionar tu DNI, dirección real, nombres de familiares, números de tarjeta o claves reales.

#### 6. Condición de cierre
- La llamada termina inmediatamente después de que hayas dictado el código ficticio o si decidís cortar por desconfianza. Si se menciona algún dato personal real, avisá y se interrumpe la grabación en el acto.

---

### FICHA DE ROL 2A (IMPRIMIBLE)
**Llamada:** 2 (Semilla `LG-WA-CONSULTA-01`)  
**Rol:** A — Quien inicia la llamada (Usuario preocupado)  
**Entregar a:** Participante asignado al Rol A

#### 1. Tu situación (Lo que sabés)
- Acabás de recibir un SMS en tu teléfono con un código para activar WhatsApp que vos jamás pediste.
- Te preocupa que alguien esté intentando entrar a tu cuenta.
- Decidís llamar por teléfono a una persona conocida de confianza que sabe de tecnología para preguntarle qué tenés que hacer.

#### 2. Lo que NO sabés
- No sabés qué recomendación exacta te va a dar tu conocido ni cómo te va a guiar.

#### 3. Tu objetivo en la llamada
- Contarle lo ocurrido a tu conocido y pedirle consejo para proteger tu cuenta de WhatsApp («Me llegó por SMS un código para activar WhatsApp y yo no lo pedí. ¿Qué hago?»).

#### 4. Cómo actuar y respuestas permitidas
- **Inicio:** Explicá la situación con preocupación genuina.
- **Pregunta sobre el código:** Si tu conocido te pregunta o te aconseja, podés preguntarle si necesita que le leas el código para poder ayudarte («¿Necesitás verlo para ayudarme?» o «¿Te paso el código?»).
- **Aceptación del consejo seguro:** En cuanto tu conocido te diga que no se lo pases y que no hace falta, aceptá su respuesta con alivio y dale las gracias.

#### 5. Límites estrictos y datos ficticios autorizados
- **PROHIBIDO** leer o dictar cualquier código (ni real ni ficticio). Solamente preguntás si hace falta mostrarlo o decirlo.
- **PROHIBIDO** brindar claves bancarias, contraseñas o datos reales identificables.

#### 6. Condición de cierre
- Despedirte y cortar la llamada una vez que tu conocido te haya dejado en claro qué pasos seguir y que no debés compartir el código.

---

### FICHA DE ROL 2B (IMPRIMIBLE)
**Llamada:** 2 (Semilla `LG-WA-CONSULTA-01`)  
**Rol:** B — Quien atiende la llamada (Conocido que orienta)  
**Entregar a:** Participante asignado al Rol B

#### 1. Tu situación (Lo que sabés)
- Atendés el llamado de una persona conocida que te contacta porque está preocupada por un mensaje recibido.
- Tenés conocimientos básicos de seguridad digital y sabés cómo prevenir estafas.

#### 2. Lo que NO sabés
- No sabés exactamente qué mensaje recibió hasta que te lo relate en la llamada.

#### 3. Tu objetivo en la llamada
- Escuchar su consulta y orientarla con buenas prácticas de seguridad para proteger su cuenta.

#### 4. Cómo actuar y respuestas permitidas
- **Consejo de seguridad inicial:** Decile de inmediato que no comparta el código con nadie y que revise las opciones de seguridad directamente dentro de la aplicación («No me lo leas ni lo compartas. Revisá la seguridad desde la aplicación»).
- **Rechazo explícito ante dudas:** Si la persona te pregunta si necesitás que te dicte o muestre el código para ayudarla, respondé de forma categórica que **NO** («No. No hace falta que me digas ningún código»).
- **Tranquilidad y cierre:** Explicá que la verificación en dos pasos de WhatsApp se configura desde la app y despedite cordialmente.

#### 5. Límites estrictos y datos ficticios autorizados
- **PROHIBIDO** pedir el código de activación, contraseñas, PIN bancario ni ningún secreto.
- **PROHIBIDO** pedir que instale herramientas de control remoto o pedir que abra enlaces desconocidos.

#### 6. Condición de cierre
- Despedirse y dar por concluida la conversación una vez aclarado que el código no se comparte y que la persona entendió el procedimiento seguro.

---

## 3. Checklist previa a la grabación

Antes de comenzar la sesión de simulación, el responsable de la toma debe verificar y tildar cada una de las siguientes condiciones:

- [ ] **Validación de cátedra/tutor (D06 pendiente):**  
  Se verificó que el tutor (Ing. Ernesto Rico) aprobó formalmente la selección de casos, el modelo de consentimiento y el resguardo local. *(Si este punto no está cumplido, la sesión no puede realizarse).*
- [ ] **Participantes adultos:**  
  Ambos interlocutores son mayores de edad (integrantes del equipo o colaboradores informados).
- [ ] **Consentimiento informado previo firmado:**  
  Ambos participantes leyeron y firmaron el formulario de consentimiento libre, expreso e informado según la Ley 25.326 ([PRIVACIDAD-DEL-SISTEMA.md](PRIVACIDAD-DEL-SISTEMA.md#2-marco-legal-argentino-ley-25326-de-protección-de-datos-personales)).
- [ ] **Custodia documental fuera de Git:**  
  Los formularios físicos o digitales firmados con datos personales reales (nombre, apellido, DNI, firma) quedaron archivados en custodia local segura a cargo de Mateo (fuera de los directorios sincronizados por Git).
- [ ] **Destino del audio fuera de Git:**  
  El directorio de guardado de los archivos `.wav` reside fuera del árbol de Git o dentro de una ruta ignorada (`data/audio/`, verificada en [.gitignore](../../.gitignore)).
- [ ] **Datos estrictamente ficticios:**  
  Ambos participantes fueron instruidos para no emitir nombres de personas reales, direcciones, teléfonos particulares, números de tarjeta o claves reales. En el fraude, el único código permitido a dictar es `000000`.
- [ ] **Asignación ciega de fichas:**  
  Cada participante tiene en mano exclusivamente su ficha impresa. El Rol B de la llamada fraudulenta desconoce que el llamado es una estafa simulada.
- [ ] **Regla de aborto inmediato conocida:**  
  Ambos participantes saben que ante cualquier equivocación con datos reales, incomodidad o solicitud de parar, se corta la toma y se destruye el audio de inmediato.

---

## 4. Procedimiento de toma

> **Estado: propuesta sin discutir.**  
> La recomendación de grabación estéreo aislada por canal (Hablante A en canal izquierdo, Hablante B en canal derecho)
> a 16 kHz 16-bit PCM se propone como estándar operativo para facilitar el desacople de voces, la evaluación
> de diarización y la alimentación mono o estéreo sin diafonía. La interfaz de audio y hardware final de laboratorio
> corresponden a [D05](../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable)
> y [D06](../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto).

### 4.1. Configuración del equipo y formato de audio
1. **Canales separados (Estéreo A/B):**
   - Siempre que sea posible técnicamente, grabar en **2 canales (estéreo)**:
     - **Canal 1 (Izquierdo / Left):** Micrófono del Hablante A (quien llama).
     - **Canal 2 (Derecho / Right):** Micrófono del Hablante B (quien atiende).
   - *Justificación técnica:* Permite evaluar al detector alimentando ambos canales o aislando exclusivamente el audio de la llamada entrante. Si un experimento requiere mono estricto (como `leer_wav_mono_16k` en `experiments/laboratorio/pipeline.py`), cada canal puede extraerse o mezclarse limpiamente sin diafonía acústica.
2. **Formato:** Archivo WAV PCM, **16.000 Hz (16 kHz)**, **16 bits**, sin compresión. Grabar directamente a 16 kHz evita degradaciones por resampleo posterior.
3. **Entorno acústico:** Habitación cerrada, sin música de fondo, televisores encendidos ni ruidos intensos de tránsito. Uso de auriculares para evitar retorno entre micrófonos.

### 4.2. Nomenclatura de archivos (Sin datos personales)
Los archivos se nombrarán estrictamente con el identificador del escenario y el número de toma:
- Llamada fraudulenta, toma 1: `SC-WA-CODE-01-t01.wav`
- Llamada legítima difícil, toma 1: `LG-WA-CONSULTA-01-t01.wav`
- Repetición dirigida (si hiciera falta): `SC-WA-CODE-01-t02.wav`

Queda terminantemente prohibido incluir nombres, apodos o iniciales de los participantes en el nombre del archivo de audio o en sus metadatos ID3/RIFF.

### 4.3. Cantidad de tomas y criterio de repetición
- **Objetivo base:** Obtener **1 toma limpia y aceptada** de la conversación fraudulenta y **1 toma limpia y aceptada** de la conversación legítima.
- **Criterios de descarte y repetición dirigida:**
  - Si hubo una mención involuntaria de un dato real -> **Aborto inmediato, eliminación del archivo** y repetición desde cero con nuevo número de toma (`t02`).
  - Si ocurrió un problema técnico (saturación de audio, corte de micrófono, ruido externo fuerte) -> **Descarte** y repetición.
  - Si el diálogo se apartó sustancialmente del objetivo de la ficha (ej. no se pidió el código en el fraude, o quien orienta pidió un dato sensible en la legítima) -> **Descarte** y repetición explicándole la duda al participante.
  - Conforme a [METODO-CREACION-CORPUS.md](METODO-CREACION-CORPUS.md#6-piloto), las repeticiones son dirigidas para corregir fallas concretas (con un tope metodológico de hasta seis repeticiones para todo el piloto).

### 4.4. Registro del esfuerzo y bitácora de sesión
Durante la toma, el responsable de la sesión debe registrar en la [planilla de revisión](PLANILLA-REVISION-TOMAS.csv):
- Tiempo insumido en la preparación y lectura de fichas (minutos).
- Tiempo de grabación efectivo de la llamada (segundos).
- Problemas observados: vacilaciones, dudas sobre el rol, pausas atípicas o risas.

---

## 5. Procedimiento de revisión y marcado de referencia

> **Estado: propuesta sin discutir.**  
> La asignación formal del revisor, el uso de software de visualización de espectrogramas (ej. Audacity) para
> marcar `T_R` y `T_C` en décimas de segundo y la tolerancia de acuerdo inter-anotador corresponden a
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

### 5.1. Asignación de roles de revisión
Para garantizar trazabilidad, se asigna un revisor humano del equipo que no haya participado activamente en la actuación de esa llamada (revisión cruzada):
- **Revisor asignado:** `______________________________`
- **Fecha de revisión:** `________-____-____`
- **Toma analizada:** `______________________________`

### 5.2. Cómo ubicar y medir `T_R` y `T_C` en segundos sobre el audio
Siguiendo las definiciones de [METRICAS.md](../evaluacion/METRICAS.md#1-marcas-temporales) y [MANUAL-ANOTACION.md](MANUAL-ANOTACION.md#2-cómo-ubicar-las-marcas-y-resolver-dudas):
Todas las marcas se miden en **segundos (con dos decimales)** desde el segundo `0.00` de inicio del archivo de audio.

1. **`T_R` (Inicio del pedido crítico de alto riesgo):**
   - Se abre el archivo de audio en un editor con visualización de forma de onda (ej. Audacity).
   - Se localiza la intervención del llamante donde solicita el código.
   - **Punto exacto de la marca:** Se coloca en el inicio del primer fonema de la palabra con la que comienza el pedido explícito.
     - *En el texto base:* Inicio de la palabra «Decime» («Decime el código de activación que recibiste por SMS»).
   - **En la llamada legítima (`LG-WA-CONSULTA-01`):** `T_R` queda en **`null` / vacío** (no existe pedido de alto riesgo).
2. **`T_C` (Inicio del primer cumplimiento observable):**
   - Se localiza la respuesta de la víctima donde comienza a entregar la información confidencial.
   - **Punto exacto de la marca:** Se coloca en el inicio del primer fonema del primer dígito o palabra con que se entrega el secreto.
     - *En el texto base:* Inicio del primer «cero» («Es cero, cero, cero...»).
   - **En la llamada legítima (`LG-WA-CONSULTA-01`):** `T_C` queda en **`null` / vacío**.
   - **Si la víctima se niega o duda y no dicta el código:** `T_C` queda en **`null` / vacío** (no se inventa una marca).

### 5.3. Contrastación triple: Audio ↔ Texto ↔ Referencia
El revisor debe realizar el siguiente contraste metódico:
1. **Audio ↔ Texto (Transcripción fiel):**
   - Escuchar el audio y cotejar contra el texto transcripto (generado por ASR o escrito manualmente).
   - Corregir cualquier discrepancia léxica (palabras omitidas, muletillas como «eh...», «bueno», falsos arranques).
2. **Texto ↔ Referencia mínima:**
   - Validar que la **clase** de la llamada (`vishing` o `legitima_dificil`) coincide efectivamente con lo sucedido.
   - Extraer el fragmento exacto de texto que contiene `T_R` y `T_C`.
   - Asignar las etiquetas de evidencia correspondientes al vocabulario del [manual de anotación](MANUAL-ANOTACION.md#5-vocabulario-candidato-para-evidencia):
     - `SC-WA-CODE-01`: verificar presencia de presentación de autoridad (`AUTHORITY_CLAIM`), presión de urgencia (`URGENCY_PRESSURE`) y pedido de código OTP (`REQUEST_AUTH_CODE`).
     - `LG-WA-CONSULTA-01`: verificar que la mención del código o la negación a recibirlo **no** sean etiquetadas como pedido crítico.
3. **Carga en planilla:**
   - Volcar los valores obtenidos en [PLANILLA-REVISION-TOMAS.csv](PLANILLA-REVISION-TOMAS.csv).

---

## 6. Integración con el resto del pipeline

Una vez que el archivo `.wav` de una toma fue revisado, aprobado y anotado en la planilla, pasa a alimentar los componentes experimentales en curso:

1. **Experimento ASR Local ([issue #19](https://github.com/Corchets/bitacora_tesis/issues/19)):**
   - **Ruta:** `experiments/asr-local/`.
   - **Función:** El audio WAV de la toma se procesa con el transcriptor local en *streaming* (Zipformer Kroko ONNX como motor principal o Faster-Whisper como comparador secundario) para evaluar la tasa de error por palabra (WER), el retardo de transcripción y la preservación de los términos críticos («código», «WhatsApp», «SMS»).
   - **Comando de ejecución:**
     ```bash
     python3 experiments/asr-local/asr_local.py /ruta/a/toma.wav \
         --salida experiments/asr-local/corridas/mi_corrida \
         --motor sherpa-zipformer \
         --referencia /ruta/a/transcripcion_revisada.txt
     ```
     (Ver `experiments/asr-local/README.md` para opciones adicionales como `--simular-tiempo-real` y `--canal A`).

2. **Experimento de Replay y Detección Incremental ([issue #28](https://github.com/Corchets/bitacora_tesis/issues/28)):**
   - **Ruta:** `experiments/replay/`.
   - **Función:** Consume el flujo de actualizaciones emitido por el ASR (`actualizaciones.jsonl`), modela la cola secuencial del detector y aplica la política de aviso único ante el primer *true* válido, registrando en `eventos.csv`:
     - El instante de alerta del sistema ($T_A$ en el reloj de audio).
     - El margen de anticipación respecto al pedido: $L_R = T_R - T_A$.
     - El margen de anticipación respecto al cumplimiento: $L_C = T_C - T_A$.
     - La presencia o ausencia de falsas alarmas en la conversación legítima contrastante.
   - **Comando de ejecución:**
     ```bash
     python experiments/replay/replay.py \
         --actualizaciones experiments/asr-local/corridas/mi_corrida/actualizaciones.jsonl \
         --detector reglas \
         --salida experiments/replay/corridas/mi_corrida_replay
     ```
     (Para usar SLM local con Ollama se especifica `--detector slm --modelo qwen3.5:2b`; ver `experiments/replay/README.md`).

---

## 7. Inconsistencias encontradas entre las fuentes

Durante la preparación de este kit se detectaron las siguientes discrepancias y diferencias de diseño entre los documentos de referencia:

1. **Maniobras de `SC-WA-CODE-01` (Catálogo vs Referencia JSON):**
   - *Ubicación:* [`docs/corpus/CATALOGO-ESCENARIOS.csv`](CATALOGO-ESCENARIOS.csv), línea 3 vs [`experiments/slm-directo/casos/referencia/SC-WA-CODE-01-e01.json`](../../experiments/slm-directo/casos/referencia/SC-WA-CODE-01-e01.json), línea 11.
   - *Detalle:* El catálogo asigna las maniobras `TRUST_BUILDING;URGENCY_PRESSURE`. Por el contrario, la referencia del caso escrito anota la línea 1 («Te llamo de soporte...») con `AUTHORITY_CLAIM` y la línea 3 con `URGENCY_PRESSURE`, omitiendo `TRUST_BUILDING`. En `ARQUITECTURA.md` §4 (línea 131) se lista F1–F3 genéricamente como «contexto».
   - *Resolución para el kit:* Se instruye a quien represente el rol a presentarse como soporte (`AUTHORITY_CLAIM`) y a crear urgencia (`URGENCY_PRESSURE`), dejando abierta la posible anotación de `TRUST_BUILDING` según si aporta datos creíbles durante la dramatización.

2. **Maniobras de `LG-WA-CONSULTA-01` (Catálogo vs Manual de Anotación y Referencia JSON):**
   - *Ubicación:* [`docs/corpus/CATALOGO-ESCENARIOS.csv`](CATALOGO-ESCENARIOS.csv), línea 15 vs [`docs/corpus/MANUAL-ANOTACION.md`](MANUAL-ANOTACION.md), línea 117 y [`experiments/slm-directo/casos/referencia/LG-WA-CONSULTA-01-e01.json`](../../experiments/slm-directo/casos/referencia/LG-WA-CONSULTA-01-e01.json), líneas 10–14.
   - *Detalle:* El catálogo consigna `AUTHORITY_CLAIM` como maniobra en `LG-WA-CONSULTA-01`. Sin embargo, el escenario es una conversación informal entre conocidos («conocido de la persona»). Según el manual de anotación, `AUTHORITY_CLAIM` solo se dispara cuando el llamante se presenta como una entidad oficial o figura de autoridad formal; no corresponde a una charla entre pares. En coherencia con esto, `LG-WA-CONSULTA-01-e01.json` no contiene etiquetas de maniobra (`etiquetas: []`).
   - *Resolución para el kit:* En la ficha legítima no se invoca autoridad y no se anota `AUTHORITY_CLAIM`.

3. **Granularidad de actualización (ARQUITECTURA §4 vs SLM directo `#50`):**
   - *Ubicación:* [`docs/ingenieria/ARQUITECTURA.md`](../ingenieria/ARQUITECTURA.md), líneas 145–150 vs [`experiments/slm-directo/casos/referencia/SC-WA-CODE-01-e01.json`](../../experiments/slm-directo/casos/referencia/SC-WA-CODE-01-e01.json), línea 19.
   - *Detalle:* En `ARQUITECTURA.md`, las actualizaciones didácticas agrupan varios turnos (U1 agrupa F1 y F2; U3 agrupa L3 y L4). En el pipeline experimental de `#50` (`experiments/slm-directo/`), cada turno cerrado de un hablante constituye una actualización individual (5 turnos en fraude, 4 turnos en legítima).
   - *Resolución para el kit:* Al grabar audio continuo, el tiempo discurre en segundos; los turnos transcriptos se delimitan por intervención cerrada de hablante.

4. **Prefijos de hablante e intervenciones consecutivas:**
   - *Ubicación:* [`docs/ingenieria/ARQUITECTURA.md`](../ingenieria/ARQUITECTURA.md), líneas 105–118 vs [`experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt`](../../experiments/slm-directo/casos/texto/SC-WA-CODE-01-e01.txt), líneas 3–4.
   - *Detalle:* En `ARQUITECTURA.md` los enunciados se enumeran como F1–F5. En el archivo de texto figuran con prefijos `A:` y `B:`. En la llamada fraudulenta, el atacante (A) habla en la línea 3 («Para cancelar esa activación...») y en la línea 4 («Decime el código...») consecutivamente. En una llamada de audio real, ambas frases pueden emitirse en una sola intervención continua o separadas por una pausa/asentimiento.
