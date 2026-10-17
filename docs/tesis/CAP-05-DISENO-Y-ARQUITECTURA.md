> **Estado: borrador.** Redactado el 2026-10-17 sobre la rama laboratorio-luciano; requiere revisión del equipo.

# Capítulo 5: Diseño y arquitectura del sistema

El presente capítulo expone la arquitectura técnica y el diseño conceptual del sistema de detección incremental de llamadas de ingeniería social y vishing (*voice phishing*). Se detallan la descomposición modular, el flujo temporal de procesamiento, los modelos de datos y contratos de interfaz que vinculan los componentes, la gestión del estado conversacional en memoria volátil y las decisiones de diseño adoptadas, contrastadas con sus alternativas y fundamentadas en las restricciones de seguridad, privacidad y plataforma vigentes.

## 5.1. Contexto de la solución y descomposición modular

El objetivo del sistema es asistir de manera oportuna a una persona receptora de una comunicación verbal potencialmente fraudulenta, emitiendo una advertencia comprensible y procesable antes de que se consume una acción perjudicial (como la entrega de un código de autenticación de un solo uso o una transferencia bancaria). Para satisfacer esta meta sin comprometer la privacidad del usuario ni violar las políticas de seguridad de los sistemas operativos móviles modernos, la solución se concibe como un pipeline completamente local (*on-device*) que procesa la conversación de manera incremental.

El sistema se estructura en seis componentes funcionales con responsabilidades desacopladas, vinculados en un flujo unidireccional:

```mermaid
flowchart LR
    A["1. Ingesta de audio<br/>(Replay / VoIP)"] -->|"Bloques PCM 16 kHz"| B["2. ASR local<br/>(Streaming / Segmentado)"]
    B -->|"Actualizaciones<br/>(JSONL)"| C["3. Contexto incremental<br/>(Memoria volátil)"]
    C -->|"Líneas disponibles<br/>(Prefijo temporal)"| D["4. Cola y detector<br/>(Reglas / SLM directo)"]
    D -->|"Respuesta tipada<br/>(Riesgo, alerta, motivo)"| E["5. Política de alerta<br/>(Aviso único)"]
    E -->|"Advertencia validada"| F["6. Interfaz de usuario<br/>(Aviso preventivo)"]
```

La responsabilidad de cada uno de los componentes se define con precisión:

1. **Ingesta de audio:** Suministra el flujo de audio en bloques temporales uniformes sin entregar información del futuro de la llamada. En la base experimental obligatoria del proyecto, este componente consiste en un motor de reproducción (*replay*) de archivos de audio que simula la llegada secuencial de fragmentos PCM; en la integración objetivo de demostración, se prevé una llamada VoIP bajo control del prototipo (ver [Alternativas para obtener el audio](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md)).
2. **Reconocimiento automático del habla (ASR local):** Transforma el flujo continuo de audio en actualizaciones de texto estructuradas. Debe operar de forma local y emitir segmentos con sus marcas temporales exactas de inicio, fin y momento de disponibilidad en el reloj de la llamada.
3. **Gestor de contexto incremental:** Mantiene en memoria de acceso aleatorio el estado conversacional de la llamada en curso. Su función es incorporar el texto emitido por el ASR, reemplazar los borradores preliminares cuando se recibe una transcripción más precisa y consolidar los segmentos cerrados, asegurando que el detector reciba en todo instante únicamente el prefijo de diálogo disponible hasta ese momento.
4. **Cola secuencial y detector:** Modela el acceso al detector lingüístico como un recurso secuencial y ejecuta el análisis de riesgo. El detector recibe exclusivamente el diálogo transcripto acumulado (sin etiquetas externas ni acceso a señales futuras) y produce una inferencia tipada compuesta por un puntaje numérico, una bandera de recomendación de alerta, un motivo explicativo y la evidencia textual que sustenta el juicio.
5. **Política de emisión de alerta:** Evalúa la secuencia de respuestas producidas por el detector a lo largo del tiempo y decide el instante exacto en que se debe emitir una advertencia a la persona usuaria, aplicando criterios de estabilidad e inhibición de falsas alarmas reiteradas.
6. **Módulo de aviso al usuario:** Transforma la decisión de alerta en una comunicación no obstructiva, clara y orientada a la acción inmediata (interrumpir la entrega de información o verificar por un canal alternativo), sin emitir afirmaciones categóricas ni revelar credenciales sensibles.

---

## 5.2. Flujo de procesamiento temporal

El recorrido temporal del sistema debe respetar rigurosamente la causalidad física del proceso. Un error metodológico habitual en la literatura sobre detección de vishing consiste en evaluar modelos sobre textos completos al finalizar la llamada o fechar las advertencias en el instante en que comenzó a pronunciarse una palabra, ignorando el tiempo que el hardware demora en capturar el audio, digitalizarlo, procesarlo en el transductor acústico y ejecutar la inferencia del modelo de lenguaje.

El flujo implementado distingue de manera explícita tres referencias temporales:

- **Intervalo del audio ($[\tau_{\text{inicio}}, \tau_{\text{fin}}]$):** Ventana temporal, medida en segundos desde el inicio de la conversación grabada, en la cual se pronunciaron los fonemas correspondientes al fragmento transcripto.
- **Instante de disponibilidad ($t_{\text{disp}}$):** Momento en el reloj del audio en que el transcriptor completa la inferencia de ese bloque acústico y publica el texto. Satisface estrictamente la invariante de causalidad:
  $$t_{\text{disp}} \ge \tau_{\text{fin}}$$
- **Instante de evaluación y emisión ($t_{\text{eval}}$, $T_A$):** Momento en que el detector lingüístico finaliza su cálculo sobre el texto disponible y la política resuelve emitir el aviso. Este instante absorbe tanto la demora acumulada en la cola de inferencia como el tiempo de cómputo del detector.

En la siguiente tabla se resumen las entradas, salidas y restricciones críticas de cada etapa del pipeline:

| Etapa | Entrada | Salida | Invariante crítica |
|---|---|---|---|
| **Audio** | Flujo acústico bruto (WAV/FLAC mono o estéreo, 16 kHz). | Bloques de PCM con marcas de tiempo. | Prohibido entregar muestras acústicas con timestamp posterior al reloj actual. |
| **ASR local** | Bloques de PCM de 100 ms. | Eventos de transcripción (`parcial` o `final`). | $t_{\text{disp}} \ge \tau_{\text{fin}}$. La latencia de cómputo se suma hacia adelante; no se reasignan marcas al pasado. |
| **Contexto** | Actualización de ASR (`tipo`, `segmento`, `texto`). | Tupla inmutable de líneas de diálogo cerradas y abiertas. | Aislamiento estricto entre llamadas: al cambiar de sesión el estado se vacía totalmente. |
| **Cola de evaluación** | Líneas de diálogo en $t_{\text{disp}}$ y estado del detector. | Turno de cómputo secuencial con inicio y fin de evaluación. | Inferencia monohilo: la evaluación $n$ no puede iniciar antes de que termine la $n-1$. |
| **Detector** | Prefijo conversacional acumulado hasta la línea actual. | Objeto de respuesta tipado (`riesgo`, `alerta_sugerida`, `motivo`, `evidencia`). | Ceguera hacia el futuro y ausencia de datos de referencia humana (clase, rol, marcas $T_R$/$T_C$). |
| **Política de alerta** | Respuesta del detector y estado de avisos previos. | Disparo del aviso definitivo y marca $T_A$. | Principio de aviso único: a lo sumo un aviso principal por sesión para prevenir fatiga. |

---

## 5.3. Modelo de datos y contratos de interfaz

La robustez de la integración y la reproducibilidad experimental dependen de la especificación estricta de los contratos de datos entre componentes. En el sistema coexisten tres modelos de datos primarios: el contrato de transcripción incremental emitido por el ASR (`actualizaciones.jsonl`), la traza unificada de eventos generada por el simulador de replay (`eventos.csv`) y los manifiestos de reproducibilidad técnica (`manifiesto.json`).

### 5.3.1. Contrato de salida del ASR (`actualizaciones.jsonl`)

El componente de reconocimiento de voz emite un flujo en formato JSON Lines (JSONL). La primera línea contiene un objeto de metadatos globales (`meta`), y cada línea subsiguiente representa un evento de transcripción emitido en orden cronológico no decreciente de `disponible_s`.

```json
{"meta": {"motor": "sherpa-zipformer", "modelo": "csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06", "tipo_entrega": "parciales_y_finales", "es_streaming": true, "sample_rate": 16000, "bloque_ms": 100, "hardware": {"sistema": "Darwin", "arquitectura": "arm64", "ram_total_gb": 8.0}}}
{"llamada_id": "SC-WA-CODE-01-tts", "n": 7, "tipo": "parcial", "segmento": 2, "texto": "pasame el código", "inicio_audio_s": 8.40, "fin_audio_s": 10.12, "disponible_s": 10.31, "proceso_ms": 190.0, "canal": null}
{"llamada_id": "SC-WA-CODE-01-tts", "n": 8, "tipo": "final", "segmento": 2, "texto": "Pasame el código de activación.", "inicio_audio_s": 8.40, "fin_audio_s": 11.20, "disponible_s": 11.45, "proceso_ms": 250.0, "canal": null}
```

La semántica de los campos de cada actualización se especifica a continuación:

- `llamada_id` (cadena): Identificador unívoco de la conversación a la que pertenece el audio.
- `n` (entero): Número de secuencia monótonamente creciente de la actualización en la sesión (1, 2, 3…).
- `tipo` (cadena, enumeración `{"parcial", "final"}`):
  - `"parcial"`: Transcripción preliminar y revisable de un segmento de habla actualmente abierto. Una actualización parcial posterior con idéntico valor de `segmento` reemplaza a la precedente.
  - `"final"`: Segmento de habla concluido definitivamente (tras detección de silencio o corte de locución). Su contenido queda congelado y no se modifica en actualizaciones posteriores.
- `segmento` (entero): Índice correlativo del turno o bloque de habla detectado por la segmentación acústica.
- `texto` (cadena): Cadena de texto decodificada por el motor de inferencia.
- `inicio_audio_s` y `fin_audio_s` (flotantes): Estampas temporales en segundos del reloj de audio que delimitan el tramo acústico de origen.
- `disponible_s` (flotante): Instante en el reloj de audio en el que la transcripción estuvo efectivamente lista para consumo del pipeline. Incorpora la latencia acumulada de decodificación y garantiza $disponible\_s \ge fin\_audio\_s$.
- `proceso_ms` (flotante): Tiempo de CPU/GPU en milisegundos que consumió el motor para decodificar ese bloque específico.
- `canal` (cadena opcional, enumeración `{"A", "B", null}`): Identificador del canal físico en grabaciones estéreo de dos vías (por ejemplo, llamadas VoIP donde el interlocutor local y el remoto ocupan canales separados). En audio monoaural o mezclas de altavoz, toma el valor `null`.

### 5.3.2. Traza unificada de ejecución del Replay (`eventos.csv`)

El motor de simulación de reproducción (`experiments/replay/replay.py`) integra las actualizaciones del ASR, gestiona la cola secuencial y vuelca una traza exhaustiva en formato tabular. Cada registro documenta la foto exacta del sistema ante cada actualización:

- Identificación y contenido: `llamada_id`, `n`, `tipo`, `segmento`, `canal`, `texto`, `texto_disponible_resumido`.
- Reloj de audio: `inicio_audio_s`, `fin_audio_s`, `disponible_s`.
- Reloj de cómputo y cola: `inicio_eval_s`, `fin_eval_s`, `espera_cola_ms`, `ms_detector`.
- Salida del detector: `riesgo`, `alerta_sugerida`, `motivo`, `evidencia`, `valida`, `error`.
- Decisión de política: `aviso` (booleano que indica si esa línea desencadenó la alerta pública), `t_a` (estampa en segundos del reloj de audio en que se concreta la alerta).

### 5.3.3. Manifiestos reproducibles (`manifiesto.json`)

Para garantizar la auditabilidad y trazabilidad experimental, cada corrida genera de forma automática un archivo de manifiesto estructurado que almacena:

1. **Procedencia criptográfica:** Hash SHA-256 del audio o del archivo JSONL de entrada, hash SHA-256 de las plantillas de prompt empleadas y estado del repositorio de control de versiones Git (hash del commit de cabecera y bandera booleana `cambios_sin_commit`).
2. **Entorno de ejecución:** Nombre del sistema operativo, versión del kernel, arquitectura del procesador, cantidad de núcleos físicos de CPU, memoria RAM instalada y versiones exactas de las librerías del entorno virtual (Python, Sherpa-ONNX, ONNX Runtime, Faster-Whisper, SoundFile, NumPy).
3. **Parámetros operativos:** Motor acústico, hilos de ejecución configurados, tamaño de bloque acústico, detector evaluado, modelo de lenguaje subyacente, semilla pseudoaleatoria (`seed`) o indicación explícita de `no-aplica`.
4. **Métricas globales de cómputo:** Factor de tiempo real ($RTF$), pico de memoria residente ($RSS$) medido a nivel de sistema operativo mediante la llamada `resource.getrusage(resource.RUSAGE_SELF)`, cantidad total de actualizaciones procesadas y desglose de parciales y finales.

---

## 5.4. Estado temporal, cola secuencial y política de aviso único

### 5.4.1. Gestión de contexto incremental en memoria volátil

El contexto de la llamada se gestiona en la clase [`ContextoLlamada`](../../experiments/replay/contexto.py). El estado se estructura en dos colecciones en memoria de acceso aleatorio:

- Una lista secuencial `cerrados: list[Linea]` que almacena los segmentos de habla confirmados (`tipo == "final"`).
- Un diccionario indexado `parciales: dict[int, Linea]` que retiene el borrador activo correspondiente a cada segmento abierto (`tipo == "parcial"`).

Cuando arriba una actualización parcial para el segmento $k$, el sistema sobrescribe la entrada `parciales[k]`. Cuando arriba una actualización final para el segmento $k$, el sistema extrae y elimina la entrada de `parciales` y anexa la línea definitiva al final de `cerrados`. En cada invocación, la instantánea de texto disponible entregada al detector se construye concatenando las líneas cerradas con los parciales vigentes ordenados por número de segmento:

$$\text{TextoDisponible} = \text{cerrados} + [\text{parciales}[s] \text{ para } s \in \text{sorted}(\text{parciales})]$$

Este mecanismo garantiza dos propiedades estructurales:
1. **Idempotencia de reemplazo:** Los borradores preliminares jamás duplican líneas en el diálogo acumulado.
2. **Reinicialización absoluta:** Al cambiar el identificador de la llamada (`llamada_id`), las estructuras `cerrados` y `parciales` se purgan por completo, impidiendo la filtración de contexto o vocabulario entre llamadas distintas.

### 5.4.2. Modelado de la cola secuencial del detector

Un dispositivo móvil de gama media cuenta con recursos computacionales acotados. Por ende, el detector lingüístico no puede concebirse como un servicio paralelizable sin límites: constituye un **recurso monohilo estrictamente secuencial**. Si el reconocedor ASR emite actualizaciones a un ritmo superior a la velocidad de inferencia del detector, las solicitudes de análisis deben encolarse.

El simulador implementa el cálculo exacto de la cola secuencial en el reloj continuo del audio:

$$\text{inicio\_eval}_n = \max(t_{\text{disp}, n}, \text{fin\_eval}_{n-1})$$

$$\text{fin\_eval}_n = \text{inicio\_eval}_n + \frac{\text{ms}_n}{1000}$$

$$\text{espera\_cola\_ms}_n = (\text{inicio\_eval}_n - t_{\text{disp}, n}) \times 1000$$

Donde $t_{\text{disp}, n}$ es el instante de disponibilidad de la actualización $n$ según el ASR, y $\text{ms}_n$ es la duración de la inferencia lingüística en milisegundos.

Si el detector procesa con holgura ($\text{ms} < \Delta t_{\text{audio}}$), la espera en cola se mantiene en cero y la evaluación inicia inmediatamente en $t_{\text{disp}, n}$. Si el detector se degrada o experimenta picos de latencia, $\text{inicio\_eval}_n$ queda dominado por $\text{fin\_eval}_{n-1}$, acumulando un atraso temporal medible en `espera_cola_ms`.

### 5.4.3. Política de aviso único

La política de alerta adoptada en el núcleo del sistema es la de **aviso único ante la primera respuesta válida positiva** (`aviso_unico_primer_true_valido`). 

Bajo esta regla, el instante de alerta de la conversación ($T_A$) se congela en el momento de finalización de cómputo de la primera actualización que retorne un resultado válido con $\text{alerta\_sugerida} == \text{True}$:

$$T_A = \text{fin\_eval}_n$$

Esta formulación garantiza que $T_A$ refleje la totalidad del tiempo transcurrido en el mundo real, incluyendo la duración del audio, la latencia del transcriptor ASR, el tiempo de espera en la cola secuencial y el procesamiento del detector.

El tratamiento de excepciones e inconsistencias sigue reglas rigurosas:
- **Invalidez no es predicción:** Si el modelo genera un JSON malformado, omite campos obligatorios, produce un valor numérico de riesgo fuera del rango $[0, 1]$, supera el límite de contexto o agota el tiempo de espera (*timeout*), el evento se califica como **fallo técnico** (`valida == False`). Un fallo **jamás** se computa como voto negativo ni bloquea la emisión de alertas en turnos subsiguientes.
- **Inhibición de fatiga:** Una vez que la llamada emite su primer aviso ($T_A$), las actualizaciones posteriores continúan registrándose con sus respectivos niveles de riesgo y motivos a efectos de análisis retrospectivo, pero su bandera `aviso` se fuerza a `False`. El sistema no repite alertas para un mismo nivel de riesgo, protegiendo a la persona usuaria de la saturación cognitiva durante una llamada bajo estrés.

### 5.4.4. Problemática del contexto en llamadas extensas (D08 abierta)

En llamadas de duración prolongada (de 10 a 20 minutos), la estrategia ingenua de concatenar la totalidad del diálogo acumulado introduce dos patologías severas:

1. **Acumulación binomial de falsas alarmas:** Si un detector posee una probabilidad $p$ de emitir un falso positivo en una revisión aislada de una llamada legítima, y el sistema evalúa la llamada periódicamente cada $\Delta t$ segundos generando $N$ revisiones ($N = \text{duración} / \Delta t$), la probabilidad acumulada de que la persona usuaria sufra al menos una falsa alarma en la llamada viene dada por:
   $$P(\text{al menos una falsa alarma}) = 1 - (1 - p)^N$$
   Como se demostró en la investigación de diseño de [VENTANA-DE-CONTEXTO-Y-ALERTA.md](../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md), un clasificador con un rendimiento aparentemente excepcional del $99\ \%$ de acierto por turno ($p = 0.01$), al ser consultado cada 15 segundos en una llamada de 20 minutos ($N = 80$ revisiones), genera al menos una falsa alarma en el **$55.2\ \%$** de las llamadas perfectamente legítimas.
2. **Envenenamiento contextual y saturación de memoria:** Menciones inocuas o ambiguas ocurridas al inicio de la llamada (por ejemplo, hablar de una urgencia médica o comentar una compra) permanecen indefinidamente en la ventana si no existe olvido, diluyendo la atención del modelo o provocando correlaciones espurias cuando se combinan con pedidos posteriores neutros.

Para mitigar estas patologías, se investigaron dos familias de alternativas arquitectónicas:
- **Ventana contextual con decaimiento temporal:** Estructuras donde los eventos pierden peso en función de su vida media ($h_\gamma$), diferenciando la persistencia de una suplantación de identidad (de larga retención) de la urgencia transitoria (de rápido decaimiento).
- **Registro de eventos estructurado:** Sustituir el arrastre de texto libre por un buffer de entidades tipadas y ordenadas temporalmente (quién habló, qué maniobra intentó y cómo reaccionó la contraparte), el cual consume una cantidad ínfima de tokens.

> **Estado: propuesta sin discutir.** El modelo final de estado temporal, el tamaño óptimo de la ventana y el criterio definitivo de persistencia (evaluación de cruces consecutivos frente a histéresis con doble umbral) continúan abiertos en [D08 — Congelar protocolo experimental](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

---

## 5.5. Decisiones arquitectónicas y análisis de alternativas

El diseño del sistema sintetiza una serie de elecciones de ingeniería donde se priorizó la defensa metodológica, la factibilidad técnica y la reproducibilidad sobre soluciones de mayor complejidad cosmética.

```mermaid
classDiagram
    class MotorIngesta {
        <<interface>>
        +reproducir_bloque()
    }
    class ReplayStreaming {
        +archivo_wav
        +simular_reloj_audio()
    }
    class VoIPControlada {
        +canales_separados_AB
        +stream_red()
    }
    MotorIngesta <|-- ReplayStreaming : Base obligatoria
    MotorIngesta <|-- VoIPControlada : Integración objetivo

    class DetectorVishing {
        <<interface>>
        +evaluar(lineas) Respuesta
    }
    class DetectorReglas {
        +coincidencias_lexicas()
        +patrones_peligrosos()
    }
    class DetectorSLMDirecto {
        +cliente_ollama
        +esquema_json_forzado()
        +verificar_evidencia()
    }
    class CascadaEncoderSLM {
        +encoder_robertuito()
        +zona_gris_disparo()
    }
    DetectorVishing <|-- DetectorReglas : Línea base / Comparador
    DetectorVishing <|-- DetectorSLMDirecto : Ensayo principal #50
    DetectorVishing <|-- CascadaEncoderSLM : Alternativa descartada spike #29
```

### 5.5.1. Paradigmas de detección: SLM directo, Reglas de incendio y Cascada

Para la capa de detección lingüística se analizaron tres paradigmas:

1. **Reglas léxicas de incendio (*Fire Rules*):** Consiste en un comparador determinista basado en expresiones regulares y distancia de edición Damerau-Levenshtein ($\le 1$) sobre patrones tipificados (`REQUEST_AUTH_CODE`, `REQUEST_SECRET`, `REQUEST_TRANSFER`, etc.), con filtro de negaciones explícitas ("no te pido").
   - *Ventajas:* Inferencia instantánea ($\approx 7\ \text{ms}$ en CPU), huella de memoria nula, total explicabilidad.
   - *Desventajas:* Incapacidad estructural para comprender el contexto conversacional; produce una tasa intolerable de falsas alarmas ante negativos difíciles (alcanzó un $58.3\ \%$ de falsas alarmas en el set de desarrollo de 24 casos legítimos de `experiments/metricas/`) y no detecta pedidos indirectos que omiten las palabras clave.
   - *Rol en el sistema:* Se mantiene como **línea base obligatoria y comparador independiente**, permitiendo cuantificar con rigor qué valor añade la incorporación de modelos neuronales.
2. **Cascada discriminativa-generativa (Encoder $\to$ SLM):** Planteada originalmente como un mecanismo de dos etapas: un codificador liviano (RoBERTuito con regresión logística) puntúa cada turno; si el riesgo cae en una "zona gris" ($0.35 \le s \le 0.75$), se convoca a un modelo generativo más pesado para desambiguar.
   - *Evaluación de laboratorio:* Los ensayos empíricos del laboratorio (spike #29, evaluado el 2026-09-28) demostraron que la cascada no mejoró el rendimiento del encoder solo (redujo el acierto de $12/16$ a $7/16$, degradó el AUROC de $0.666$ a $0.537$ y mantuvo idénticas $5/10$ falsas alarmas). Asimismo, la coexistencia de ambos modelos en memoria demandaba $\approx 1.7\ \text{GB}$ de RAM sin considerar el ASR, quebrantando el presupuesto de gama alta de $1024\ \text{MB}$. Su reactivación quedó descartada en el issue #41/#42.
3. **SLM local directo:** Un modelo de lenguaje pequeño (*Small Language Model*) de entre 0.8B y 4B parámetros recibe la transcripción acumulada y emite directamente una decisión estructurada bajo esquema JSON forzado.
   - *Rol en el sistema:* Adoptado como el eje de experimentación del ensayo #50 (`experiments/slm-directo/`).

> **Estado: decisión abierta.** La elección final entre modelos y configuraciones operativas permanece abierta en [D09 — Elegir ASR y detector](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

### 5.5.2. Captura de audio: Replay reproducible frente a VoIP y PSTN

La obtención del flujo acústico representa uno de los dilemas de ingeniería más relevantes del proyecto, resuelto mediante la separación tajante entre experimentación científica e integración de demostración:

1. **Replay de grabaciones en streaming (Nivel 1, obligatorio):** La simulación basada en reproducir archivos de audio WAV/FLAC en bloques secuenciales de tiempo real constituye la única alternativa que permite garantizar repetibilidad estadística idéntica, control temporal al milisegundo y medición desacoplada de la latencia.
2. **Llamada VoIP controlada (Nivel 2, integración objetivo):** En una aplicación VoIP propia (basada en protocolos abiertos o bibliotecas WebRTC/SIP), la aplicación actúa como extremo legítimo de la comunicación. Esto ofrece una ventaja decisiva: **captura multicanal con interlocutores físicamente aislados** (canal A = usuario local, canal B = interlocutor remoto). Esto suprime la necesidad de incorporar algoritmos de diarización acústica en tiempo real, cuyo costo computacional en CPU móvil es prohibitivo.
3. **Captura telefónica universal en redes celulares (PSTN):**
   - *Restricción de plataforma:* El sistema operativo Android prohíbe taxativamente que aplicaciones estándar de terceros accedan a los flujos de audio entrante y saliente de las llamadas de telefonía convencional (`VOICE_UPLINK` y `VOICE_DOWNLINK`). Dichos permisos están reservados a aplicaciones preinstaladas del sistema con la firma del fabricante que gocen del privilegio `CAPTURE_AUDIO_OUTPUT`.
   - *Decisión técnica:* Se declaró explícitamente **fuera del alcance** del Proyecto Final ([D05 — Elegir la fuente de audio demostrable](../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable)). En lugar de recurrir a vulnerabilidades (*exploits*), técnicas de *rooting* o mecanismos de captura espía que comprometerían la estabilidad y legalidad del desarrollo, el proyecto asume esta frontera como una restricción de ingeniería de la plataforma.

### 5.5.3. Enfoque lingüístico frente a acústico (D11 abierta)

El pipeline centra su análisis en el contenido semántico y pragmático de la transcripción textual, descartando deliberadamente la prosodia, el tono de voz o biomarcadores acústicos para clasificar el vishing. Esta decisión obedece a tres fundamentos:
- La variabilidad acústica introducida por los códecs de compresión telefónica (como AMR-NB a 8 kHz o G.711) destruye micro-rasgos prosódicos.
- Los indicios determinantes de una maniobra de ingeniería social (la suplantación de identidad, la creación de urgencia artificial y la solicitud de códigos secretos) son fenómenos de naturaleza intrínsecamente lingüística.
- Preserva el presupuesto de cómputo del dispositivo al evitar la inferencia simultánea de redes acústicas pesadas.

> **Estado: propuesta sin discutir.** La ratificación formal de operar exclusivamente sobre la transcripción textual y diferir el análisis acústico como trabajo futuro permanece abierta en [D11 — Análisis lingüístico o también acústico](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico).

---

## 5.6. Seguridad, privacidad y despliegue local

La operación de un detector de vishing plantea interrogantes éticos y legales inmediatos, dado que procesa la señal más íntima de las telecomunicaciones interpersonales: la voz en tiempo real. La arquitectura del sistema responde a estos desafíos mediante un enfoque estricto de **Privacidad desde el Diseño** (*Privacy by Design*).

### 5.6.1. Inferencia local estricta y descarte en memoria volátil

El sistema no se conecta a ningún servidor central, API comercial ni servicio en la nube durante el curso de la llamada:
- **Ejecución on-device:** Tanto el transcriptor ASR como el modelo de lenguaje residen y se ejecutan en el hardware del teléfono. Ni un solo byte de audio digitalizado ni una sola palabra transcripta abandonan el dispositivo.
- **Ciclo de vida en memoria volátil:** Los buffers PCM de audio y las estructuras de diálogo del contexto (`cerrados` y `parciales`) residen exclusivamente en memoria RAM. Al cortarse o finalizar la comunicación, la memoria se libera de manera inmediata mediante la destrucción de los objetos en memoria. El sistema no persiste en disco grabaciones de voz ni transcripciones textuales.

### 5.6.2. Encuadre normativo argentino (Ley 25.326)

El diseño arquitectónico satisface las exigencias de la [Ley 25.326 de Protección de Datos Personales](../corpus/PRIVACIDAD-DEL-SISTEMA.md#2-marco-legal-argentino-ley-25326-de-protección-de-datos-personales):
- **Principio de minimización y finalidad (Art. 4):** Los datos procesados son estrictamente adecuados y no excesivos respecto al fin exclusivo de proteger a la persona receptora contra el fraude; la destrucción inmediata en RAM tras la llamada cumple con el mandato legal de supresión de datos cuando han dejado de ser necesarios.
- **Consentimiento y licitud (Art. 5 y 6):** En el ámbito experimental y en la integración VoIP controlada, ambos participantes conocen de antemano el propósito del estudio y prestan su consentimiento explícito. En un producto comercial de autoprotección, la herramienta es operada por el propio titular del dispositivo de forma transparente.
- **Seguridad y confidencialidad (Arts. 9 y 10):** La arquitectura elimina el riesgo de fuga masiva de datos en tránsito o reposo al carecer de bases de datos remotas.
- **Prohibición de cesión (Art. 11):** No existe transferencia de información personal a terceros.

### 5.6.3. Secreto de las comunicaciones y no interceptación

El marco penal argentino sanciona penalmente en los artículos 153 y 153 bis del Código Penal la interceptación indebida de comunicaciones privadas y el acceso no autorizado a sistemas informáticos. Asimismo, el artículo 197 tipifica el entorpecimiento de las telecomunicaciones.

La arquitectura diseñada se alinea con la doctrina jurídica aplicable:
1. **Inexistencia de captación por terceros:** En el prototipo de laboratorio y en la llamada VoIP consentida, la aplicación forma parte del canal extremo receptor. No actúa como un agente encubierto interceptor de telecomunicaciones ajenas.
2. **No interferencia en el servicio:** El detector opera en modo de escucha pasiva en el extremo terminal. No altera la señal de red, no desvía paquetes ni interrumpe la conexión telefónica (cumpliendo con la exigencia de no entorpecer el servicio según el art. 197).
3. **Naturaleza del aviso:** La advertencia emitida es un mensaje visual o sensorial local dirigido exclusivamente a la persona usuaria para alertarla cognitivamente. El sistema no inyecta audio sintetizado en el canal de la contraparte ni ejecuta acciones invasivas sin supervisión humana.
