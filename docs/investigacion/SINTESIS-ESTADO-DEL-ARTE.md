# Síntesis del estado del arte

> Síntesis de antecedentes tecnológicos y literatura primaria analizada para fundamentar las decisiones y el vacío de investigación del Proyecto Final.

## 1. Antecedentes por sistema

### Ventinel (Android, académico)

Sistema de defensa para Android contra *call redirection* y *display overlay* ejecutados por malware
de vishing. Usa OCR para comparar en tiempo real el número marcado en pantalla con el que
efectivamente se conecta, y verifica contactos duplicados creados por aplicaciones maliciosas.

- **Diferencia de enfoque:** combate la intercepción maliciosa por software. Esta tesis combate la
  persuasión de un atacante humano que llama desde una línea común.
- **Aporte:** antecedente para "trabajos relacionados". Muestra supervisión de llamadas no invasiva
  en Android, por un vector totalmente distinto (visión por computadora sobre la UI, no ASR/PLN
  sobre el audio).

### HearMeOut (ACM MobiSys)

Detecta comportamientos anómalos de aplicaciones de vishing dentro de Android en tiempo real,
rastreando solicitudes de permisos en runtime, estado de llamadas y patrones de comportamiento.

- **Diferencia de enfoque:** telemetría del sistema operativo y permisos. No interpreta el contenido
  conversacional.
- **Aporte:** justifica la necesidad del proyecto. Protege contra llamadas originadas por troyanos,
  pero es completamente ciego ante un engaño donde el atacante llama a un teléfono convencional sin
  haber infectado el dispositivo.

### Modelos acústico-lingüísticos multimodales

Analizan simultáneamente variables bioacústicas (F0, estrés vocal, MFCCs con CNN-BiLSTM) y la
transcripción textual.

- **Viabilidad en móvil: media-baja.** El análisis acústico fino requiere señal limpia. Si la
  captura es acústica por altavoz, la reverberación, el ruido ambiental y la cancelación de eco del
  hardware distorsionan justamente los rasgos de tono y estrés.
- **Consecuencia para la tesis:** es más prudente enfocar el prototipo en análisis lingüístico y
  semántico sobre la transcripción del ASR, y reservar lo bioacústico como trabajo futuro. Esto
  todavía no está decidido —
  ver [D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico).

### Defensas antifraude telefónico de Google (Pixel / Android)

Ficha completa con fuentes primarias y fechas de consulta:
[lecturas/2026-google-scam-detection.md](lecturas/2026-google-scam-detection.md)
(consulta 2026-09-17).

- **Qué son:** funciones comerciales cerradas, no un trabajo académico. No hay paper, ni código, ni
  dataset. Primer anuncio de Scam Detection en llamadas: 13/11/2024.
- **Cuidado con el nombre:** Google llama "Scam Detection" a cuatro cosas distintas (llamadas,
  Google Messages, notificaciones de apps de terceros), y además existen "Fake Call Detection" y
  "Call Screen". Las propias páginas de soporte mezclan sus listas de países e idiomas. La ficha los
  separa; conviene no citarlos como si fueran un solo producto.
- **Fuente más informativa:** la solicitud de patente US 2024/0388655 A1, *In-call scam detection*
  (Google LLC, presentada el 13/05/2024). Describe el espacio de diseño reivindicado, no
  necesariamente el producto que se envía: en la tesis se cita como *"una solicitud de patente de
  Google describe…"*, nunca como la arquitectura de Scam Detection.
- **Aporte a la justificación:** confirma que el análisis conversacional durante la llamada y
  on-device ya es viable en producto, y que el hueco reproducible sigue abierto.
- **Límite:** caja negra. No es comparable experimentalmente, y lo que Google no publica queda
  marcado como no publicado en la ficha.

### Soluciones comerciales (INETCO, Brightside)

- **INETCO (BullzAI / Insight):** ciberseguridad transaccional para instituciones financieras.
  Detecta el *resultado* del vishing analizando patrones anómalos en la red de pagos, transferencias
  sospechosas o uso de credenciales robadas a nivel de servidor bancario.
- **Brightside:** concientización, entrenamiento y postura de seguridad corporativa.
- **Diferencia de enfoque:** infraestructura centralizada orientada a empresas.
- **Aporte:** fundamenta la justificación práctica. INETCO actúa cuando la transacción fraudulenta ya
  fue iniciada; la propuesta actúa en el dispositivo antes de que el usuario entregue el token.

### Repositorios de GitHub (voiceguard, Vishing-detector y similares)

Proyectos de graduación o experimentos con clasificadores de texto (TF-IDF + scikit-learn, o
fine-tuning de BERT/RoBERTa) sobre transcripciones completas, casi siempre en inglés.

- **Estático vs. incremental:** clasifican la conversación cuando ya terminó.
- **Sin despliegue móvil:** rara vez optimizados para correr on-device.
- **Sesgo idiomático:** inglés o español neutro, sin la pragmática de la ingeniería social argentina.

## 2. Literatura académica primaria analizada

| ID | Trabajo y autores | Año / Publicación | Aporte principal | Límites identificados para la tesis |
|---|---|---|---|---|
| **S001** | *Vishing: Detecting social engineering in spoken communication — A first survey & urgent roadmap*<br/>Triantafyllopoulos et al. | 2025<br/>*Computer Speech & Language*<br/>[DOI: 10.1016/j.csl.2025.101802](https://doi.org/10.1016/j.csl.2025.101802) | Primer survey exhaustivo sobre vishing. Confirma la escasez crítica de datos públicos y la necesidad de diseñar detección e intervención conjuntamente en tiempo real. | Es una revisión narrativa interdisciplinaria; no implementa ni evalúa modelos empíricos sobre audio en español ni despliegue en dispositivos móviles. |
| **S002** | *Automatically Detecting Voice Phishing: A Large Audio Model Approach (VishGPT)*<br/>Ampel, Samtani y Chen | 2026<br/>*MIS Quarterly*<br/>[AIS eLibrary](https://aisel.aisnet.org/misq/vol50/iss2/9/) | Propone VishGPT con preentrenamiento sintético y fine-tuning por refuerzo sobre transcripciones. Reporta F1 de 87,74% en detección conversacional. | Depende de LLMs pesados orientados a servidor/GPU; no evalúa latencia on-device en hardware móvil ni cubre modismos argentinos. |

## 3. Matriz comparativa

| Sistema | Nivel de análisis | Vector de detección | Ejecución | ¿Cubre manipulación psicológica? | Reproducible académicamente |
|---|---|---|---|---|---|
| Ventinel | Sistema / pantalla | Redirección de llamadas + OCR sobre UI | Local en Android | No — detecta desvíos de malware | Sí (académico) |
| HearMeOut | Sistema / permisos | Permisos y telemetría de apps | Servicio de SO en Android | No — detecta apps maliciosas | Sí (académico) |
| Modelos acústicos multimodales | Audio / prosodia | F0, estrés vocal, MFCC (CNN-BiLSTM) | Servidor / GPU | Parcial — muy sensible al ruido | Parcial |
| INETCO BullzAI | Red / pagos | Transacciones y credenciales | Servidores bancarios | No — detecta el impacto financiero | No (comercial) |
| VishGPT | Conversacional | LLM sobre transcripción, tiempo real | Servidor | Sí | Parcial — paper publicado |
| Google Scam Detection | Conversacional | Contenido de la llamada | On-device (Pixel) | Sí | No — caja negra |
| Samsung AI Scam Detection | Conversacional | Patrones de llamada, tiempo real | On-device (One UI 8.5+) | Sí | No — caja negra |
| **Propuesta de esta tesis** | Conversacional | Semántica incremental ASR + NLP | Local | Sí, con taxonomía explícita | **Sí — ese es el punto** |

Las cifras, fechas y disponibilidad de los productos comerciales cambian: cada vez que se citen,
llevan fuente y **fecha de consulta**.

## 4. Qué existe frente a qué aportaríamos

| Área | Ya existe | Espacio para la tesis |
|---|---|---|
| Reputación de números | Caller ID, listas de spam, bloqueo | No es el foco |
| Análisis durante la llamada | Google Pixel, Samsung Galaxy recientes | Prototipo abierto y reproducible |
| Procesamiento local | Google declara on-device en Scam Detection | Arquitectura local reproducible |
| Detección académica de vishing | VishGPT y trabajos recientes | Español y escenarios argentinos |
| Modelado de etapas | Hay evidencia de progresiones y guiones | Anotación explícita de eventos críticos |
| Persuasión | Principios psicológicos estudiados | Convertirlos en explicaciones operativas |
| Métrica principal | Predominan métricas clásicas de clasificación | Poner el **tiempo de intervención** en el centro |
| Corpus argentino/español | No se identificó uno que reúna todos los requisitos | Corpus controlado y anotado |

## 5. El diferencial no es una innovación, es una combinación

> vishing en español + contexto argentino + procesamiento incremental + intervención explicable +
> evento crítico anotado + evaluación temporal + ejecución local + **reproducible**.

Hay una clara separación entre la seguridad a nivel de software/malware (Ventinel, HearMeOut) y la
seguridad a nivel conversacional (esta propuesta). Demostrar esa separación en la introducción es lo
que sostiene la justificación del trabajo.

## 6. Advertencias de redacción

Dos formulaciones que hay que cuidar en el informe:

1. **No afirmar que somos los primeros en analizar una llamada durante la conversación.** Eso ya
   existe comercial y académicamente (Google, Samsung, VishGPT). El aporte es la combinación y la
   reproducibilidad, no la primicia.
2. Sobre la ausencia de corpus en español argentino, la formulación correcta es *"no identificamos
   en la literatura revisada"*, nunca *"no existe"*. El campo se mueve rápido y una afirmación
   absoluta es indefendible frente al tribunal.
