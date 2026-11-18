> **Estado: borrador del 2026-11-03**, actualizado el 2026-11-11 con el detector del [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) y el ASR del [ADR 0001](../ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md). Requiere revisión del equipo.

# Capítulo 6: Implementación del sistema

En este capítulo se describe la materialización del sistema experimental de detección incremental de vishing, detallando el conjunto de herramientas de software y versiones adoptadas, la organización modular del código fuente, las rutinas de automatización e inspección desarrolladas y las restricciones o limitaciones técnicas advertidas durante el proceso de implementación y ejecución en hardware de laboratorio.

---

## 6.1. Pila tecnológica y versiones del entorno de ejecución

El desarrollo del software se diseñó para operar de forma autocontenida sobre la biblioteca estándar de Python y un conjunto estrictamente acotado de librerías abiertas para inferencia de modelos neuronales en formato compilado. La experimentación se llevó a cabo sobre una estación de trabajo Apple Silicon (procesador Apple M1, 8 núcleos físicos de CPU, 8 GB de memoria RAM unificada, arquitectura ARM64), que también es la notebook de la demo, y complementariamente en un entorno Windows 11 x86_64 con GPU y un Ryzen 7 7700X con 30,5 GB y GPU para la ejecución de modelos de lenguaje mediante Ollama.

Las bibliotecas y runtimes utilizados, con sus números de versión reales extraídos de los manifiestos de corrida (`manifiesto.json`) y archivos de requerimientos (`requirements.txt`), se presentan en la siguiente tabla:

| Componente | Paquete / Runtime | Versión | Función en el sistema |
|---|---|---|---|
| **Lenguaje base** | `python` | `3.13` en la llamada en vivo | Intérprete del recorrido experimental. |
| **ASR** | `sherpa-onnx` | `1.13.8` | Decodificación de Parakeet y Silero, sobre ONNX Runtime. |
| **Modelo de ASR** | `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8` | v3, int8 | Transcripción por frases, búsqueda *greedy*, 2 hilos. |
| **Filtro de voz** | `silero_vad.onnx` | Release `asr-models` de `sherpa-onnx` | Decide qué cuenta como voz (umbral 0,5). |
| **Servidor de SLM** | `ollama` | `0.40.5` (M1), `0.40.8` (Ryzen), `0.40.14` (Colab T4) | Inferencia local con API HTTP. |
| **Servidor en el teléfono** | `llama-server` (llama.cpp) | `6c01da62` | Medición en el Samsung A56, en CPU con 4 hilos. |
| **Modelo de lenguaje** | `gemma4:e2b-it-q4_K_M` | Digest `b37049369adf…`, 4,59 GB | Decisión del aviso, con temperatura 0, seed 42 y `num_ctx` 4096; la salida se corta a los 14 tokens. |
| **Llamada en vivo** | `websockets` | `>=15.0` | Audio y control entre el panel y el servidor. |
| **Panel** | HTML y módulos JavaScript | Sin dependencias externas | Captura por AudioWorklet, conversación y Presentación. |
| **Pruebas** | `unittest`, `node --test` | Bibliotecas estándar | Pruebas sin red ni modelos reales. |

Whisper y Zipformer siguen en el código como antecedentes reproducibles, así como la síntesis TTS con `say` de macOS para los ejemplos sin voz humana.

La elección de `sherpa-onnx` obedece al requerimiento de despliegue local: permite ejecutar el modelo de voz en CPU sin un framework de entrenamiento. La configuración final tampoco usa PyTorch. Sí lo usa Tito viejo, el filtro del ADR 0001, que sigue en el repositorio como antecedente: la regresión logística `tito_logreg.json` (sha256 `fb601eaa…5098eccd`) sobre `pysentimiento/robertuito-base-uncased` congelado (revisión `20cb399e…`), con `torch` 2.14.1 y `transformers` 5.20.2, y unos 0,48 GB de memoria.

---

## 6.2. Implementación por componente

El código de los experimentos se organiza de manera modular dentro del directorio `experiments/` del repositorio, dividiéndose en cinco módulos funcionales:

```mermaid
flowchart TD
    subgraph ASR["experiments/asr-local/"]
        AL["asr_local.py<br/>(CLI & Ingesta)"]
        MOT["motores.py<br/>(Parakeet + Silero)"]
        WER["wer.py<br/>(Cálculo de error)"]
        TTS["sintetizar_par.py<br/>(Generación TTS)"]
    end

    subgraph VOIP["experiments/voip/"]
        SRV["servidor.py<br/>(ASR por canal y detector)"]
        PAN["panel.html<br/>(Captura, Presentación e Historial)"]
        TUR["turnos.py<br/>(Turnos por canal)"]
    end

    subgraph REPLAY["experiments/replay/"]
        RP["replay.py<br/>(Orquestador Replay)"]
        CTX["contexto.py<br/>(ContextoLlamada & Cola)"]
    end

    subgraph SLM["experiments/slm-directo/"]
        DET["detectores.py<br/>(DetectorSLM / DetectorReglas)"]
        OLL["cliente_ollama.py<br/>(Cliente HTTP)"]
        REG["reglas.py<br/>(Reglas de incendio)"]
        CAS["casos.py<br/>(Carga de casos)"]
    end

    subgraph METRICAS["experiments/metricas/"]
        MET["metricas.py<br/>(Fórmulas canónicas)"]
        EVA["evaluar.py<br/>(CLI de ingesta)"]
    end

    AL -->|"actualizaciones.jsonl"| RP
    PAN -->|"PCM 16 kHz, 40 ms"| SRV
    SRV -->|"actualizaciones.jsonl"| RP
    SRV --> TUR
    TUR -->|"Turno de OTRA cerrado"| DET
    RP --> CTX
    CTX -->|"Líneas disponibles"| DET
    DET --> OLL
    DET --> REG
    RP -->|"eventos.csv"| EVA
    EVA --> MET
```

### 6.2.1. Reconocimiento de voz local (`experiments/asr-local/`)

El módulo implementa un procedimiento repetible y estandarizado para la transcripción incremental de audio local:

1. **Orquestador de línea de comandos ([`asr_local.py`](../../experiments/asr-local/asr_local.py)):**
   - Ingiere archivos de audio monoaurales o estéreo a una frecuencia de muestreo normalizada de 16 kHz.
   - Divide la señal en bloques acústicos uniformes de duración configurable (`--bloque-ms 100`, 100 ms por defecto).
   - Dispone de dos modos de operación: el *modo rápido*, que procesa los bloques tan pronto como el hardware lo permite para optimizar corridas en lote; y el modo `--simular-tiempo-real`, que introduce demoras calibradas con `time.sleep` para reproducir fielmente el ritmo de emisión de una llamada en vivo.
   - Mide el consumo de recursos en tiempo real mediante `time.perf_counter()` para el tiempo de procesamiento y la llamada de sistema `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss` para determinar el pico de memoria física residente (RSS).
2. **Jerarquía de motores acústicos ([`motores.py`](../../experiments/asr-local/motores.py)):**
   - Define la clase abstracta `MotorASR`, especificando la interfaz obligatoria: `inicializar()`, `procesar_bloque()`, `vaciar_final()` y `metadatos()`.
   - **`MotorSherpaParakeet` (configuración final):** Parakeet TDT 0.6B v3 por `sherpa-onnx`, con `greedy_search` y 2 hilos. Hereda de `MotorPorFrases`, que corta frases por silencio y las transcribe enteras, agrega 0,3 s de preaudio para no comerse la primera sílaba, corta una frase sin pausas a los 10 s y descarta lo que tenga menos de 0,3 s de voz. Vuelve a transcribir la frase abierta cada 0,5 s para mostrar un borrador, desde 1 s de voz, y descarta borradores que no parecen español. Los dos canales comparten el reconocedor, así que el modelo se carga una sola vez.
   - **`DetectorSilero` en modo `filtro` (opción B):** El RMS 0,008 con 0,8 s de silencio abre y cierra la frase; solo cuenta como voz lo que Silero (umbral 0,5) también oye.
   - **`MotorZipformer` (antecedente):** Implementa la decodificación continua con el modelo de Hugging Face [`csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`](https://huggingface.co/csukuangfj/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06). Utiliza un transductor ONNX (`tokens.txt`, `encoder.onnx`, `decoder.onnx`, `joiner.onnx`) configurado para búsqueda codiciosa (*greedy search*), 4 hilos de CPU y 80 dimensiones de características fbank (bancos de filtros log-mel). La segmentación de turnos combina la detección nativa de puntos finales (*endpointing*) del reconocedor (`rule1_silence=2.4`, `rule2_silence=1.0`, `rule3_utterance=20.0`) con una regla de energía RMS (`umbral_rms_silencio=0.005`) que dispara el cierre del segmento tras un silencio acumulado de 0.8 s (`corte_silencio_s`). Emite eventos de tipo `parcial` mientras el segmento está activo y un evento `final` al detectarse el corte.
   - **`MotorFasterWhisper` (antecedente):** Implementa un comparador secundario segmentado con `faster-whisper-base` en precisión int8 para CPU. No opera en streaming real; acumula el audio por turnos mediante el filtro Voice Activity Detector (VAD) de Whisper (`min_silence_duration_ms=500`) y emite únicamente eventos finales tras transcribir el lote.
   - **`MotorFalso`:** Mock determinista que emite eventos parciales y finales programados a instantes temporales prefijados, permitiendo probar la lógica de downstream sin requerir modelos pesados.
3. **Cálculo de errores de transcripción ([`wer.py`](../../experiments/asr-local/wer.py)):**
   - Implementa el cálculo de la tasa de error por palabra ($WER$) y por carácter ($CER$) mediante alineación de cadenas con distancia de Levenshtein (programación dinámica).
   - Realiza normalización canónica de texto eliminando acentos (`unicodedata.normalize`), signos de puntuación y convirtiendo a minúsculas.
   - Incluye la función `analizar_palabras_clave()`, que verifica específicamente si términos determinantes para la detección de fraude (tales como `codigo`, `cero`, `sms`, `whatsapp`, `activacion`, `soporte`, `cuenta`) fueron transcritos correctamente o si sufrieron sustitución o eliminación.
4. **Generador de audio sintético de humo ([`sintetizar_par.py`](../../experiments/asr-local/sintetizar_par.py) / [`sintetizar_par.sh`](../../experiments/asr-local/sintetizar_par.sh)):**
   - Produce audio de prueba sin violar la privacidad a partir de los textos del par de WhatsApp (`SC-WA-CODE-01-e01` y `LG-WA-CONSULTA-01-e01`).
   - Utiliza la utilidad `say` de macOS asignando la voz `Paulina` (español de México) al interlocutor A y la voz `Mónica` al interlocutor B, con pausas artificiales de 1.0 s entre turnos para ejercitar la segmentación automática.
   - Genera tanto versiones monoaurales como archivos estéreo de 16 kHz donde el canal izquierdo corresponde exclusivamente a A y el derecho a B.

### 6.2.2. Contexto incremental y simulación de Replay (`experiments/replay/`)

El módulo de reproducción y gestión temporal se implementa en:

1. **Estructura de contexto y cola ([`contexto.py`](../../experiments/replay/contexto.py)):**
   - Modela la actualización de entrada en la dataclass inmutable `Actualizacion` (`llamada_id`, `n`, `tipo`, `segmento`, `texto`, `inicio_audio_s`, `fin_audio_s`, `disponible_s`, `proceso_ms`, `canal`).
   - La clase `ContextoLlamada` mantiene las listas `cerrados: list[Linea]` y el mapa `parciales: dict[int, Linea]`. En su método `aplicar()`, procesa la actualización y devuelve la tupla ordenada de líneas visibles.
   - En su método `registrar_evaluacion()`, implementa las ecuaciones de la cola secuencial:
     $$\text{inicio\_eval}_s = \max(\text{disponible\_s}, \text{ultimo\_fin\_eval\_s})$$
     $$\text{fin\_eval}_s = \text{inicio\_eval}_s + (\text{ms} / 1000.0)$$
     $$\text{espera\_cola\_ms} = (\text{inicio\_eval}_s - \text{disponible\_s}) \times 1000.0$$
   - Implementa la política de aviso único: si la respuesta del detector es válida y `alerta_sugerida == True`, y no se había emitido alerta previa (`aviso_emitido == False`), fija `aviso_t_a = fin_eval_s` y activa la bandera de aviso para esa línea. Si la respuesta es inválida, incrementa el contador `fallos` y almacena el motivo en `errores`.
2. **Ejecutor de replay ([`replay.py`](../../experiments/replay/replay.py)):**
   - Procesa flujos de audio ASR (`--actualizaciones`) o casos de texto directo (`--texto`).
   - En modo texto sin audio, garantiza el principio metodológico de no inventar segundos: las columnas de tiempo de audio quedan vacías y el aviso se referencia por número de línea.
   - Valida el canal de audio: si el JSONL contiene `canal == null`, conmuta de forma automática el parámetro de hablantes a `sin` para evitar atribuir letras arbitrarias al modelo.
   - Genera los artefactos de salida en el directorio especificado: `eventos.csv`, `manifiesto.json` y `resumen.md`.

### 6.2.3. Modelos de lenguaje directo y reglas heurísticas (`experiments/slm-directo/`)

La capa de detección lingüística implementa el detector del [ADR 0002](../ingenieria/adr/0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md) y las reglas que sirven de línea base. El filtro Tito viejo del ADR 0001 queda descrito al final, como antecedente.

1. **Configuración final (`DetectorSLMCorteRiesgo`, en [`detectores.py`](../../experiments/slm-directo/detectores.py)):**
   - Arma el mismo pedido que el resto de los detectores JSON: el prompt [`tarea_c_premisa.txt`](../../experiments/slm-directo/prompts/tarea_c_premisa.txt), la salida [`salida_json_c.txt`](../../experiments/slm-directo/prompts/salida_json_c.txt) y la transcripción con los roles `PROTEGIDA` y `OTRA`.
   - Corta la salida con `num_predict` 14, justo después de la coma que cierra el riesgo, y lo lee del texto cortado. La regla es riesgo ≥ 0,3; `alerta_sugerida` no llega a escribirse.
   - En el primer aviso hace una segunda consulta con [`motivo_c_corte.txt`](../../experiments/slm-directo/prompts/motivo_c_corte.txt), que repite los mensajes, agrega lo ya escrito y pide motivo y evidencia. Si falla, el aviso se mantiene y el error queda con el prefijo `etapa2_`.
   - Con `--solo-otra`, las líneas de PROTEGIDA entran en el contexto y no consultan.
2. **Antecedente: filtro Tito viejo ([`filtro_tito.py`](../../experiments/slm-directo/filtro_tito.py), [`tito_real.py`](../../experiments/slm-directo/tito_real.py)):**
   - `TitoReal` obtiene la representación de RoBERTuito congelado (promedio enmascarado de la última capa, dimensión 768) y aplica la regresión logística del artefacto. Tarda unos 30 ms por frase en la M1.
   - `FlujoTitoSLM` activa al modelo ante el primer puntaje mayor o igual a 0,5 o ante un fallo de Tito, y le entrega el indicio como bloque separado, marcado como falible. El estado se reinicia entre llamadas.
   - `FlujoTitoEnVivo` ([`replay.py`](../../experiments/replay/replay.py)) adapta ese flujo a la llamada: recibe solo frases cerradas y puntúa también las que se juntaron mientras el detector estaba ocupado.
   - El ajuste del artefacto está en [`entrenar_tito.py`](../../experiments/slm-directo/entrenar_tito.py) y su [diagnóstico](../../experiments/slm-directo/DIAGNOSTICO-TITO-2026-10-29.md). En esas 10 conversaciones, Tito derivó 4 de 8 legítimas y las 2 estafas: el filtro ahorra consultas, pero es el modelo el que descarta.
3. **Detector con modelo de lenguaje local, clase base ([`detectores.py`](../../experiments/slm-directo/detectores.py) - `DetectorSLM`):**
   - Se comunica con el demonio de Ollama mediante llamadas HTTP POST a la ruta `/api/chat` implementadas en [`cliente_ollama.py`](../../experiments/slm-directo/cliente_ollama.py).
   - Configura las opciones del modelo: temperatura fija $0.0$, semilla pseudoaleatoria $42$, límite de ventana de contexto `num_ctx = 4096`, límite de predicción `num_predict = 512`. No envía `think`.
   - **Control de desborde de contexto:** Debido a que Ollama trunca silenciosamente los textos que exceden la ventana sin arrojar error, el método `evaluar()` estima previamente la longitud en tokens ($(\text{longitud\_prompt} + \text{longitud\_usuario}) / 3$). Si supera el $90\ \%$ de `num_ctx`, detiene la invocación y emite una respuesta no válida con el error `contexto_excedido`.
   - **Prompt:** En la configuración del ADR 0001 se usaba `tarea`, que pide marcar la alerta solo si alguien pide, induce o presiona para entregar códigos, claves, datos personales o dinero, instalar acceso remoto o hacer acciones de seguridad guiadas, y aclara que no alcanza con mencionarlas. La configuración final usa C con la premisa del alcance (punto 1).
   - **Forzado y validación de esquema:** Envía a la API el esquema estructurado `ESQUEMA_SALIDA` exigiendo un objeto JSON con cuatro propiedades obligatorias (`riesgo`, `alerta_sugerida`, `motivo`, `evidencia`). La función `validar_salida()` verifica exhaustivamente que el texto devuelto parsee como JSON, que los tipos coincidan, que `riesgo` esté acotado entre $0$ y $1$ y que una alerta sugerida posea obligatoriamente un motivo en texto.
   - **Verificación adversarial de evidencia:** La función `evidencia_en_texto()` normaliza la cita devuelta por el modelo y comprueba si cada uno de sus renglones existe literalmente dentro de la transcripción histórica disponible. Si el modelo inventa o parafrasea frases que no se pronunciaron, la bandera `evidencia_en_texto` se fija en `False`.
4. **Comparador de reglas de laboratorio ([`reglas.py`](../../experiments/slm-directo/reglas.py) / `DetectorReglas`):**
   - Reproduce fielmente las reglas heurísticas desarrolladas por Ignacio en el laboratorio (`experiments/laboratorio/rules.py`, commit `a39fca6`).
   - Agrupa los términos sospechosos en seis familias de patrones (`REQUEST_AUTH_CODE`, `REQUEST_SECRET`, `REQUEST_TRANSFER`, `REQUEST_PERSONAL_DATA`, `REQUEST_REMOTE_ACCESS`, `REQUEST_SECURITY_ACTION`).
   - La función `_cerca()` implementa coincidencia exacta para patrones cortos ($\le 5$ caracteres, como `pin`, `otp`, `cbu` o el término sensible `numeros`) y tolera una distancia Damerau-Levenshtein de hasta 1 edición (`_edicion1()`) en términos de 6 o más caracteres para absorber errores tipográficos o de transcripción ASR.
   - La función `_niega_el_pedido()` inhibe el disparo si la frase contiene expresiones de negación ("no te pido", "ningun", "no voy a dar"), excepto si la misma cláusula incorpora simultáneamente un verbo imperativo ("no cortes y decime").
   - `DetectorReglas` evalúa exclusivamente la última línea entregada; no conserva memoria de turnos pasados.

### 6.2.4. Llamada en vivo y panel (`experiments/voip/`)

[`servidor.py`](../../experiments/voip/servidor.py) recibe el audio de cada persona por WebSocket y arranca, salvo que se le indique otra cosa, con la configuración final: `parakeet-filtro` y E2B solo con `c-premisa-corte-riesgo`, consultando al cerrar cada turno de OTRA ([`turnos.py`](../../experiments/voip/turnos.py), ADR 0007). El panel ofrece también las reglas como respaldo sin modelo. Tito viejo queda solo por línea de comandos, como antecedente.

- **Captura ([`audio-navegador.mjs`](../../experiments/voip/audio-navegador.mjs), [`fuentes.mjs`](../../experiments/voip/fuentes.mjs)):** el AudioWorklet mezcla a mono, remuestrea a 16 kHz y envía bloques PCM16 de 40 ms. La persona protegida usa su micrófono y la otra persona llega desde una pestaña de Meet, cuyo audio se comparte en Chrome. El video que exige el selector no se transmite ni se guarda.
- **Reloj:** empieza con el primer bloque que llega; cada canal se ubica según su llegada y cuenta muestras desde ahí, de modo que los canales y el estéreo guardado quedan alineados.
- **Vistas:** consola de la llamada, «Probar el ASR», Historial y Vista de presentación, con dos teléfonos para proyectar ([#110–#115](../../experiments/voip/README.md#13-vista-de-presentación-de-la-llamada-110115)).
- **Registros:** cada llamada deja `actualizaciones.jsonl`, `detector.jsonl`, `manifiesto.json` y `estereo.wav` en una carpeta fuera de Git. [`resumen_llamada.py`](../../experiments/voip/resumen_llamada.py) arma una ficha desde esos registros y `replay.py` puede volver a correr la llamada con otro detector.
- **Medición:** [`medir.py`](../../experiments/voip/medir.py) reproduce un ejemplo al ritmo real, sin panel. Sigue usando Zipformer como ASR, porque la referencia temporal del criterio de #84 se fijó con él.

### 6.2.5. Módulo de métricas estandarizadas (`experiments/metricas/`)

Implementa en funciones puras y reutilizables la totalidad de las fórmulas de evaluación formal definidas en `METRICAS.md`:

- **Biblioteca matemática ([`metricas.py`](../../experiments/metricas/metricas.py)):**
  - `calcular_margen_lr(t_r, t_a)` y `calcular_margen_lc(t_c, t_a)`: Obtienen los márgenes de anticipación temporal ($L_R = T_R - T_A$ y $L_C = T_C - T_A$). Si no se emitió alerta ($T_A = \text{None}$), devuelven `None`.
  - `intervalo_wilson(k, n, confianza=0.95)`: Calcula el intervalo de confianza asimétrico de Wilson para proporciones binomiales (con corrección para denominadores acotados o proporciones en los extremos $0$ y $1$).
  - `resumen_distribucion(valores)`: Extrae mediana, cuartiles $Q_1$, $Q_3$ y rango intercuartílico $IQR = Q_3 - Q_1$, informando el número $n$ de muestras útiles.
  - `preventive_at(delta, referencia, casos_vishing)`: Computa la proporción de llamadas fraudulentas donde la alerta se anticipó al menos $\delta$ unidades al pedido o cumplimiento ($T_A \le X - \delta$, con $X \in \{T_R, T_C\}$). Las llamadas de vishing donde no hubo alerta se mantienen estrictamente en el denominador.
  - `tasa_falsas_alarmas(casos_legitimos)`: Determina la fracción de llamadas legítimas que sufrieron al menos una alerta espuria.
  - `precision_con_prevalencia(p, r, f)`: Aplica el teorema de Bayes para proyectar la precisión del sistema bajo prevalencias de fraude hipotéticas ($p \in \{0.1\%, 1\%, 5\%, 10\%, 50\%\}$) a partir del recall $r$ y la tasa de falsas alarmas $f$.
- **CLI de ingesta ([`evaluar.py`](../../experiments/metricas/evaluar.py)):**
  - Carga corridas de texto de `experiments/slm-directo/` o trazas de audio de `experiments/replay/`.
  - Empareja cada caso procesado con su ficha humana en `casos/referencia/*.json` mediante el identificador de conversación.
  - Genera informes comparativos consolidados en formato Markdown (`metricas.md`) y JSON estructurado (`metricas.json`).

---

## 6.3. Integración y automatización experimental

Para permitir que cualquier integrante del equipo o revisor reproduzca los experimentos en su propia máquina sin pasos manuales propensos a error, se implementó un conjunto de scripts de automatización e interfaces de usuario:

### 6.3.1. Scripts de demostración de un solo comando (`demo.sh` y `demo.ps1`)

El script de demostración interactiva (`experiments/slm-directo/demo.sh` para entornos Unix y `demo.ps1` para PowerShell en Windows) ejecuta la secuencia completa de despliegue:
1. Detecta la presencia de Python 3.9 o superior y consulta al usuario antes de instalar dependencias faltantes.
2. Comprueba el estado del servicio local de Ollama; si no se encuentra activo, asiste en su instalación y arranque.
3. Descarga el modelo objetivo predeterminado (`qwen3.5:2b` o el indicado por parámetro).
4. Ejecuta el conjunto de pruebas unitarias (`unittest`), garantizando que la lógica del cliente y los detectores sea correcta antes de consumir cómputo.
5. Ejecuta la inferencia sobre un conjunto balanceado de 8 conversaciones demostrativas (4 de vishing y 4 legítimas difíciles), imprimiendo en la terminal el diálogo incremental y las decisiones del detector.
6. Genera el informe `resumen.md` y compila de manera automática el visor web interactivo abriéndolo en el navegador del usuario.

### 6.3.2. Visor interactivo autónomo (`visor.py` y `visor_plantilla.html`)

El visor constituye una aplicación web estática autocontenida que no requiere conexión a Internet ni frameworks externos:
- El script [`visor.py`](../../experiments/slm-directo/visor.py) lee las trazas `actualizaciones.csv` y los manifiestos de una o varias corridas, inyecta los datos estructurados en formato JSON dentro de la plantilla [`visor_plantilla.html`](../../experiments/slm-directo/visor_plantilla.html) y produce un archivo HTML final autónomo.
- La interfaz permite seleccionar la llamada y el detector a inspeccionar, reproduciendo el avance del diálogo línea por línea.
- Muestra en paneles sincronizados:
  1. El texto acumulado disponible hasta la línea activa.
  2. La respuesta estructurada del modelo (nivel de riesgo, alerta sugerida, motivo y evidencia citada).
  3. La respuesta cruda devuelta por el motor de inferencia.
  4. Un gráfico dinámico en SVG que traza la curva de riesgo a lo largo de los turnos de la llamada.
  5. Una barra de advertencia destacada que señala el instante exacto en que se produjo el aviso de la llamada.
  6. La opción de alternar la visualización de las marcas de referencia humana para verificar la anticipación respecto a $T_R$ y $T_C$.

---

## 6.4. Limitaciones técnicas y desafíos encontrados

Durante la construcción e integración del pipeline experimental se identificaron las siguientes limitaciones técnicas, que condicionan la arquitectura y el despliegue del sistema:

### 6.4.1. Cola de vaciado (*lookahead flush*) en Zipformer streaming (antecedente)

El transductor acústico Zipformer empleado en `sherpa-onnx` opera mediante bloques de atención con contexto a la derecha (*chunk-based streaming with right context / lookahead*). Esta arquitectura requiere que el modelo disponga de muestras acústicas posteriores a la palabra en curso para resolver la decodificación de los últimos fonemas.

En las primeras pruebas sobre audio continuo, se observó que cuando un hablante concluía su intervención y se producía un corte abrupto del stream (o al llegar al final del archivo de audio), la última palabra pronunciada quedaba retenida indefinidamente en el buffer interno del codificador sin llegar a transcribirse, provocando omisiones sistemáticas de términos clave situados al final de los turnos (como dígitos de verificación).

Para resolver esta limitación física del motor, se introdujeron dos mecanismos compensatorios en [`motores.py`](../../experiments/asr-local/motores.py#L192-L240):
1. **Purga ante endpoint:** Al detectarse un corte de segmento por silencio, el método `procesar_bloque()` inyecta programáticamente un bloque de 0.3 segundos de silencio digital (vector de ceros en `float32`) en el flujo antes de consultar el resultado definitivo `get_result()`, forzando al modelo a vaciar su ventana de lookahead.
2. **Cola de vaciado final extendida:** Al concluir la llamada, el método `vaciar_final()` inyecta una cola de 2.0 segundos de silencio antes de marcar `input_finished()`, garantizando la decodificación íntegra de la locución final sin truncamiento.

### 6.4.2. Ausencia de determinismo estricto en inferencia de SLM con GPU

A pesar de fijar parámetros de decodificación estrictamente deterministas en Ollama (temperatura $T = 0.0$, muestreo desactivado y semilla pseudoaleatoria fija `seed: 42`), la ejecución repetida de una misma configuración (`qwen3.5:2b`, prompt `tarea`, hablantes `ab`) sobre el conjunto de 53 casos en hardware con aceleración GPU arrojó resultados divergentes:
- En las corridas registradas el 2026-10-14 ([`172930`](../../experiments/slm-directo/corridas/2026-10-14_172930_demo-qwen3.5-2b/resumen.md) y [`175451`](../../experiments/slm-directo/corridas/2026-10-14_175451_demo-qwen3.5-2b/resumen.md)), 60 de las 464 líneas procesadas difirieron en el valor numérico de riesgo devuelto, y en 2 de las 53 conversaciones cambió la decisión final de alerta (en `LAB-pantalla-sin-programa` una corrida emitió aviso y la otra no; en `TR-09` el aviso se desplazó de la línea 6 a la línea 7).

Como hipótesis técnica, se presume que esta variación podría vincularse al paralelismo asincrónico y a operaciones en punto flotante no asociativas en la GPU, aunque la causa exacta no fue medida empíricamente en el marco de este trabajo.

> **Estado: propuesta sin discutir.** La exigencia metodológica de protocolizar repeticiones múltiples e informar la dispersión o intervalo de variación en experimentos con SLM se encuentra abierta y sujeta a discusión en [D08 — Congelar protocolo experimental](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

### 6.4.3. Latencia del SLM solo con CPU (2 hilos)

Para explorar el comportamiento temporal bajo recursos restringidos de procesamiento, se ejecutó una serie de pruebas forzando la inferencia exclusivamente en CPU limitada a 2 hilos (`--solo-cpu --hilos 2`, corrida `2026-10-14_191429_cpu-2hilos` documentada en [`experiments/slm-directo/README.md`](../../experiments/slm-directo/README.md#6-escalera-de-modelos-y-gamas-de-celular)).

Los resultados empíricos mostraron un incremento sustancial de los tiempos de respuesta:
- En el modelo `qwen3.5:0.8b`, la latencia mediana por línea se elevó a 3.9 s (con un percentil 95 de 7.3 s y un máximo de 9.1 s).
- En el modelo `qwen3.5:2b`, la latencia mediana trepó a 8.2 s por línea (con un percentil 95 de 13.0 s y un máximo de 20.9 s).

Estas mediciones son de Qwen. Con la configuración del ADR 0001 (JSON completo), E2B dio en la M1 de 8 GB una **mediana de 3,74 s por consulta y un p95 de 4,53 s** ([#84](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md#demora-de-e2b-84)), con 4,5–4,7 GB de swap: no cumple el criterio de 2 s, aunque el aviso llegó entre −0,45 y +0,40 s del fin del pedido. Esa medición usó Zipformer, sin Chrome ni Meet. Con la salida cortada del ADR 0002, en el Samsung A56 tardó 3,60 s de mediana por línea de OTRA ([a56-congelada-latencia](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md)).

Bajo este régimen de operación, la cola secuencial del detector acumula un atraso creciente respecto al ritmo natural del habla. Con el modelo de 2B parámetros, el aviso llega con una demora acumulada superior a 11.7 segundos después de pronunciada la frase crítica. En esa PC de escritorio x86 evaluada, solo con CPU y 2 hilos, el modelo de 2B incumple ampliamente el gate operativo de latencia de [PREFACTIBILIDAD-TECNICA.md](../investigacion/PREFACTIBILIDAD-TECNICA.md) ($p95 \le 1.5\ \text{s}$). Como señala la propia documentación del ensayo, se trata de una medición de cota en una PC de escritorio y no en un teléfono: la viabilidad y rendimiento en dispositivos móviles reales continúa sin medirse.

### 6.4.4. Truncamiento silencioso de contexto en servidores de inferencia

Un hallazgo crítico de implementación radica en el comportamiento de los motores de inferencia locales frente al desborde de la ventana de contexto: ante prompts que exceden el tamaño máximo (`num_ctx`), Ollama trunca silenciosamente el texto inicial sin retornar un código de error HTTP ni alertar en la respuesta. En un sistema de detección de vishing, este comportamiento provocaría la pérdida inadvertida de las frases iniciales de suplantación de identidad (como "le hablo del banco"), degradando la capacidad del clasificador.

Para neutralizar este defecto, el código de `DetectorSLM` implementa una salvaguarda algorítmica preventiva: estima el volumen de tokens antes de despachar la petición HTTP; si el texto acumulado supera el $90\ \%$ de la capacidad del contexto, interrumpe el procesamiento y califica la actualización como un fallo explícito (`contexto_excedido`), preservando la integridad del registro de auditoría.

### 6.4.5. Límites descubiertos con voz real

La [corrida del 2026-11-02](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md) dejó limitaciones que las pruebas con TTS no mostraban:

- **Idioma:** Parakeet no permite fijar el idioma. En vivo, 1 de 71 frases finales salió entera en otro idioma con la opción B.
- **Términos críticos:** con la opción B, el recall de términos críticos es de 70,9 %. Las etiquetas que se pierden vienen de «toque» por «token» y «CBB» o «CBO» por «CVV» y «CBU».
- **Cierre de llamada:** cortar la llamada cancelaba la consulta en curso y descartaba lo pendiente, lo que dejaba sin aviso al ejemplo corto. Se corrigió con una espera de hasta 30 s (`7e6b971`).
- **Modelo frío:** Ollama descarga el modelo a los 10 minutos sin consultas, y la primera consulta tarda entre 12 y 16 s. Hace falta una llamada de calentamiento.
- **Tag del modelo:** en Mac, `gemma4:e2b` a secas baja otro artefacto, que pide 6,9 GiB y no carga. Por eso se usa siempre el tag completo.
- **Resguardo:** el audio original se perdió al borrar una copia de trabajo, porque Git ignora esa carpeta ([registro](../../experiments/voip/corridas/2026-11-02-voz-real-meet.md#audio-original-perdido)).
