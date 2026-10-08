# Glosario

Términos que usamos con un sentido preciso. Si en una discusión dos personas usan uno de estos con
sentidos distintos, se define acá.

| Término | Definición |
|---|---|
| **Vishing** | *Voice phishing*. Estafa por ingeniería social ejecutada en una conversación de voz. |
| **ASR** | *Automatic Speech Recognition*. Transcripción automática de voz a texto. |
| **On-device / inferencia local** | Todo el procesamiento ocurre en el dispositivo; ni el audio ni la transcripción salen de él. |
| **Turno conversacional** | Intervención de un hablante. No tiene que coincidir con un bloque de audio ni una actualización del ASR. El [manual](corpus/MANUAL-ANOTACION.md) define cómo se usa al anotar. |
| **`T_A`, `T_R`, `T_C`** | Marcas de alerta del sistema, pedido riesgoso y cumplimiento observable. Definiciones, fuentes y casos sin dato en [METRICAS.md](evaluacion/METRICAS.md#1-marcas-temporales). |
| **`L_R`, `L_C`, `Preventive@δ`** | Márgenes y proporción de alertas con anticipación suficiente respecto de una referencia. Fórmulas y denominadores en [METRICAS.md](evaluacion/METRICAS.md). |
| **Detección incremental** | Decidir con información disponible hasta cada actualización, usando contexto previo de la llamada, sin consultar lo que se dirá después. |
| **Early classification** | Campo que estudia clasificar secuencias lo antes posible sin destruir el rendimiento predictivo. |
| **Baseline** | Método de referencia contra el que se compara. La línea base acordada son reglas solas; su implementación se debe explicitar. Que un candidato no la supere también es un resultado válido. |
| **Multi-label** | Cada turno puede tener varias etiquetas simultáneas, o ninguna. |
| **Kappa (Cohen / Fleiss)** | Coeficiente de acuerdo entre anotadores que descuenta el acuerdo por azar. Cohen para dos anotadores, Fleiss para más. |
| **Speaker-disjoint** | Partición en la que los hablantes de test no aparecen en entrenamiento. |
| **Familia** | Modalidad amplia, como banco o soporte. Puede contener varias semillas; ver [método del corpus](corpus/METODO-CREACION-CORPUS.md#1-unidad-del-corpus). |
| **Semilla** | Situación concreta que puede tener distintas interpretaciones. Separación de variantes y particiones pendiente de adoptar en [D08](gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental). |
| **Hard negative** | Llamada legítima deliberadamente parecida a un fraude. Es lo que distingue un sistema útil de uno molesto. |
| **Sin opinión** | Turno en el que el goteo no tiene evidencia para puntuar el riesgo. No es una estafa ni una llamada que parece legítima, y no cuenta como actualización de `T_A`. Propuesta del spike #29 (2026-09-23); no cierra D09. |
| **WER** | *Word Error Rate*. Métrica de calidad del ASR. |
| **Real-time factor (RTF)** | Tiempo de procesamiento dividido por la duración del audio. RTF < 1 = procesa más rápido de lo que escucha. |
| **Corrida** | Ejecución única del prototipo de laboratorio: entra, procesa un audio autorizado, escribe evidencia y termina. No es un servicio levantado ni la demo Android. |
| **Replay en streaming** | Alimentar un WAV autorizado al ASR en pedazos ordenados, como si la llamada estuviera llegando. No es transcribir el archivo de un saque ni una llamada en vivo. |
| **`CAPTURE_AUDIO_OUTPUT`** | Permiso de Android reservado a componentes privilegiados del sistema, necesario para capturar `VOICE_CALL` / `VOICE_UPLINK` / `VOICE_DOWNLINK`. Es la restricción que define el alcance del proyecto. |
| **ADR** | *Architecture Decision Record*. Registro fechado de una decisión y sus alternativas descartadas. |
| **UFECI** | Unidad Fiscal Especializada en Ciberdelincuencia (Argentina). |
| **Ley 25.326** | Ley argentina de Protección de Datos Personales. |
| **Brief** | En el ayuda memoria del proyecto: orientación técnica breve derivada para un issue que explica resultado observable, contexto necesario (fuentes de esa rama), primer paso ejecutable y evidencia de terminado. No es un campo obligatorio del issue en GitHub ni un segundo backlog. |
