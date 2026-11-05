> **Estado: borrador del 2026-11-03.** Las fichas completas, con páginas y citas, están en la [síntesis del estado del arte](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md). Falta pasar las referencias al estilo bibliográfico final y la revisión cruzada de fuentes (#25).

# Capítulo 2: Marco conceptual y antecedentes

## 2.1. Vishing e ingeniería social

El vishing es ingeniería social por voz: la herramienta del atacante es la persuasión, no un fallo de software. Triantafyllopoulos et al. (2025) publicaron el primer survey del tema y confirman tanto la escasez de datos públicos como la necesidad de diseñar detección e intervención juntas y en tiempo real.

En el caso argentino, el [catálogo de escenarios](../corpus/CATALOGO-ESCENARIOS.csv) reúne modalidades documentadas por [UFECRI](https://www.fiscales.gob.ar/procuracion-general/la-unidad-fiscal-especializada-en-investigacion-criminal-compleja-advierte-sobre-estafas-telefonicas-a-personas-mayores/), [BCRA](https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/), [ANSES](https://www.anses.gob.ar/noticias/anses-nunca-solicita-datos-personales-claves-o-informacion-bancaria-0) y una [fuente oficial sobre el código de WhatsApp](https://www.argentina.gob.ar/sites/default/files/2022/07/recomendaciones_evitar_fraudes_whatsapp.pdf), con nueve semillas fraudulentas candidatas y ocho negativos legítimos diseñados por el equipo. Las fuentes respaldan la modalidad o la conducta segura; no prueban que un diálogo inventado haya ocurrido.

## 2.2. Detección de llamadas y sistemas existentes

Los sistemas relevados atacan el problema en niveles distintos:

| Sistema | Nivel de análisis | Ejecución | ¿Cubre la manipulación? | Reproducible |
|---|---|---|---|---|
| Ventinel | Redirección de llamadas y OCR sobre la pantalla | Local en Android | No, detecta desvíos de malware | Sí |
| HearMeOut | Permisos y telemetría de apps | Servicio del SO en Android | No, detecta apps maliciosas | Sí |
| Modelos acústicos multimodales | F0, estrés vocal y MFCC | Servidor o GPU | Parcial, muy sensible al ruido | Parcial |
| INETCO BullzAI | Transacciones y credenciales | Servidores bancarios | No, detecta el impacto financiero | No |
| VishGPT | LLM sobre transcripción | Servidor | Sí | Parcial |
| Google Scam Detection | Contenido de la llamada | On-device (Pixel) | Sí | No |
| Samsung AI Scam Detection | Patrones de la llamada | On-device | Sí | No |

Ventinel y HearMeOut protegen contra llamadas originadas por malware, pero no ven un engaño hecho desde un teléfono común sin infectar el dispositivo. INETCO actúa cuando la transacción fraudulenta ya empezó. Google y Samsung muestran que el análisis conversacional en el dispositivo es viable en un producto, pero son cajas negras: no se pueden comparar experimentalmente. La solicitud de patente US 2024/0388655 A1 de Google describe un espacio de diseño reivindicado, no necesariamente el producto que se envía. Las cifras y la disponibilidad de los productos comerciales cambian: cada cita lleva fecha de consulta.

Los proyectos públicos en GitHub suelen clasificar la conversación ya terminada, casi siempre en inglés y sin despliegue móvil.

## 2.3. ASR, clasificación incremental e intervención

**Reconocimiento de voz.** Un modelo de streaming entrega texto mientras se habla; uno por frases espera un corte de silencio y transcribe el tramo completo. La [auditoría de ASR del proyecto](../../experiments/asr-local/PLAN-VOZ-REAL.md#10-auditoría-de-vad-preaudio-y-comparación-de-modelos-2026-10-29) distingue detección de actividad de voz, corte por energía, preaudio y streaming simulado.

**El WER no alcanza.** Balagopalan et al. (2019) muestran que las eliminaciones dañan al clasificador posterior más del doble que las sustituciones y las inserciones, aunque el WER las cuente igual. Zhou et al. (2022) cuantifican la deriva semántica que producen los errores de ASR en la detección de intenciones, en comandos breves en inglés. Por eso este trabajo informa los términos críticos perdidos además del WER.

**Modelos pequeños.** Sim y Kim (2025) evalúan Llama 3 8B ajustado con LoRA sobre bloques de transcripción. Un clasificador estándar como KoBERT cae de 98,5 % a 56,2 % ante llamadas legítimas adversariales, y los criterios estructurados en el prompt mitigan esa caída. Ampel et al. (2026) proponen VishGPT, con F1 de 87,74 %, pero orientado a servidor y sin evaluar latencia en hardware móvil.

**Datos sintéticos.** Traister et al. (2026) analizan un honeypot activo de 10.015 llamadas reales: los modelos entrenados con datos sintéticos caen de un F1 de 1,00 a 0,02–0,40 en llamadas reales, y las particiones deben ser disjuntas por llamante. Esta es la advertencia más directa para este trabajo, cuyo corpus es simulado. Es un preprint en inglés.

## 2.4. Datasets y evaluación temprana

**Datasets.** En las [fuentes verificadas](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md#23-datasets-y-límites-de-reutilización-recuperación-de-43) no se identificó un corpus con conversaciones fraudulentas y legítimas comparables del dominio argentino. Los relevados están en otro idioma o dominio, son sintéticos o tienen licencia sin verificar. Por eso se produce un corpus propio.

**Evaluación temprana.** ERDE (Losada y Crestani, 2016; Losada et al., 2017) penaliza el error y el retraso en función de la cantidad de intervenciones leídas. Mori et al. (2018) formalizan el compromiso entre exactitud y precocidad, normalizando por la duración total de la serie, que durante una llamada es desconocida. Este trabajo usa márgenes físicos en segundos respecto de un pedido y de un cumplimiento, porque el daño no depende de una curva abstracta de turnos.

**Tasa base.** Axelsson (2000) muestra que, en eventos raros, las falsas alarmas son el factor que limita a un sistema de detección. Williams (2021) modela cómo la precisión depende de la prevalencia y converge a cero cuando esta tiende a cero si la tasa de falsas alarmas es mayor que cero. Por lo tanto, la precisión medida en un corpus balanceado no se traslada al uso cotidiano.

## 2.5. Síntesis crítica y vacío que aborda el proyecto

| Área | Ya existe | Espacio para este trabajo |
|---|---|---|
| Análisis durante la llamada | Google Pixel, Samsung Galaxy recientes | Prototipo abierto y reproducible |
| Procesamiento local | Google declara on-device | Arquitectura local reproducible |
| Detección académica | VishGPT y trabajos recientes | Español y escenarios argentinos |
| Métrica principal | Predominan métricas clásicas de clasificación | El tiempo de intervención en el centro |
| Corpus argentino o en español | No se identificó uno que reúna los requisitos en la literatura revisada | Corpus controlado y anotado |

Dos formulaciones se cuidan en todo el informe: este trabajo no es el primero en analizar una llamada durante la conversación, y sobre el corpus se afirma que «no se identificó en la literatura revisada», no que no exista.

## Referencias del capítulo

- Ampel, Samtani y Chen (2026). *Automatically Detecting Voice Phishing: A Large Audio Model Approach (VishGPT)*. MIS Quarterly. [AIS eLibrary](https://aisel.aisnet.org/misq/vol50/iss2/9/).
- Axelsson (2000). *The Base-Rate Fallacy and the Difficulty of Intrusion Detection*. ACM TISSEC 3(3). [DOI](https://doi.org/10.1145/357830.357849).
- Balagopalan, Shkaruta y Novikova (2019). *Impact of ASR on Alzheimer's Disease Detection*. Interspeech. [arXiv:1904.01684](https://arxiv.org/abs/1904.01684).
- Losada y Crestani (2016). *A Test Collection for Research on Depression and Language Use*. CLEF, LNCS 9840. [DOI](https://doi.org/10.1007/978-3-319-44564-9_3).
- Losada, Crestani y Parapar (2017). *eRisk 2017*. CLEF, LNCS 10478. [DOI](https://doi.org/10.1007/978-3-319-65813-1_30).
- Mori, Mendiburu, Dasgupta y Lozano (2018). *Early Classification of Time Series by Simultaneously Optimizing the Accuracy and Earliness*. IEEE TNNLS 29(10). [DOI](https://doi.org/10.1109/TNNLS.2017.2764939).
- Sim y Kim (2025). *Detecting Voice Phishing with Precision: Fine-Tuning Small Language Models*. [arXiv:2506.06180](https://arxiv.org/abs/2506.06180).
- Traister et al. (2026). *A Corpus of Real Scam- and Spam-Call Conversations from an Active Voice-Agent Honeypot*. [arXiv:2609.29528](https://arxiv.org/abs/2609.29528).
- Triantafyllopoulos et al. (2025). *Vishing: Detecting social engineering in spoken communication*. Computer Speech & Language. [DOI](https://doi.org/10.1016/j.csl.2025.101802).
- Williams (2021). *The Effect of Class Imbalance on Precision-Recall Curves*. Neural Computation 33(4). [DOI](https://doi.org/10.1162/neco_a_01362).
- Zhou, Chong, Wang y Zeng (2022). *Calibrate and Refine!*. [arXiv:2205.11008](https://arxiv.org/abs/2205.11008).
