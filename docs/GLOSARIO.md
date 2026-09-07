# Glosario

Términos que usamos con un sentido preciso. Si en una discusión dos personas usan uno de estos con
sentidos distintos, se define acá.

| Término | Definición |
|---|---|
| **Vishing** | *Voice phishing*. Estafa por ingeniería social ejecutada en una conversación de voz. |
| **ASR** | *Automatic Speech Recognition*. Transcripción automática de voz a texto. |
| **On-device / inferencia local** | Todo el procesamiento ocurre en el dispositivo; ni el audio ni la transcripción salen de él. |
| **Turno conversacional** | Unidad de anotación: una intervención continua de un hablante. La definición operativa (qué pasa con solapamientos) está pendiente — ver [MANUAL-ANOTACION.md](datos-etica/MANUAL-ANOTACION.md). |
| **`T_A`** | Momento en que el sistema emite la alerta. Definido con histéresis: primera predicción sobre el umbral que se sostiene dos actualizaciones. |
| **`T_R`** | Momento en que el atacante hace el primer **pedido** de alto riesgo. |
| **`T_C`** | Momento en que la víctima inicia la primera **acción de cumplimiento**. |
| **`L_R`** | `T_R − T_A`. Anticipación respecto del pedido. Positivo = bien. |
| **`L_C`** | `T_C − T_A`. Margen antes de que la víctima empiece a obedecer. Positivo = bien. |
| **`Preventive@δ`** | Proporción de llamadas de vishing alertadas al menos δ segundos antes de `T_C`. |
| **Detección incremental** | Decidir con información parcial, acumulando evidencia turno a turno, sin esperar a que la llamada termine. |
| **Early classification** | Campo que estudia clasificar secuencias lo antes posible sin destruir el rendimiento predictivo. |
| **Baseline** | Método de referencia contra el que se compara. Acá: un detector por palabras clave. Fija el piso: si el método incremental no lo supera, no hay aporte. |
| **Multi-label** | Cada turno puede tener varias etiquetas simultáneas, o ninguna. |
| **Kappa (Cohen / Fleiss)** | Coeficiente de acuerdo entre anotadores que descuenta el acuerdo por azar. Cohen para dos anotadores, Fleiss para más. |
| **Speaker-disjoint** | Partición en la que los hablantes de test no aparecen en entrenamiento. |
| **Familia / semilla de guion** | Conjunto de conversaciones derivadas del mismo guion base. Todas deben caer en el mismo split, o hay contaminación. |
| **Hard negative** | Llamada legítima deliberadamente parecida a un fraude. Es lo que distingue un sistema útil de uno molesto. |
| **WER** | *Word Error Rate*. Métrica de calidad del ASR. |
| **Real-time factor (RTF)** | Tiempo de procesamiento dividido por la duración del audio. RTF < 1 = procesa más rápido de lo que escucha. |
| **`CAPTURE_AUDIO_OUTPUT`** | Permiso de Android reservado a componentes privilegiados del sistema, necesario para capturar `VOICE_CALL` / `VOICE_UPLINK` / `VOICE_DOWNLINK`. Es la restricción que define el alcance del proyecto. |
| **ADR** | *Architecture Decision Record*. Registro fechado de una decisión y sus alternativas descartadas. |
| **UFECI** | Unidad Fiscal Especializada en Ciberdelincuencia (Argentina). |
| **Ley 25.326** | Ley argentina de Protección de Datos Personales. |
