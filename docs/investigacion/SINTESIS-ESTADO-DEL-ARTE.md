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
- **Consecuencia para la tesis:** el 2026-10-04 se confirmó el detector sobre transcripción y
  contexto de la llamada actual; los rasgos acústicos quedan como trabajo futuro según
  [D11](../gestion/MAPA-DECISIONES.md#d11--análisis-lingüístico-o-también-acústico).

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
| **S003** | *A Test Collection for Research on Depression and Language Use* / *eRisk 2017: CLEF lab on early risk prediction on the internet*<br/>Losada, Crestani y Parapar | 2016 / 2017<br/>*CLEF 2016 (LNCS 9840) / CLEF 2017 (LNCS 10478)*<br/>[DOI: 10.1007/978-3-319-44564-9_3](https://doi.org/10.1007/978-3-319-44564-9_3) / [DOI: 10.1007/978-3-319-65813-1_30](https://doi.org/10.1007/978-3-319-65813-1_30) / [CEUR-WS Vol-1866](http://ceur-ws.org/Vol-1866/invited_paper_5.pdf) | Introduce la métrica ERDE (Early Risk Detection Error) que penaliza demoras en detección secuencial de textos con una función sigmoidea sobre el conteo de intervenciones. | Mide retraso en conteo discreto de publicaciones ($k$), no tiempo físico continuo; penaliza la demora sin anclaje a un evento crítico externo. |
| **S004** | *Early Classification of Time Series by Simultaneously Optimizing the Accuracy and Earliness*<br/>Mori, Mendiburu, Dasgupta y Lozano | 2018 (online 2017)<br/>*IEEE TNNLS*, 29(10)<br/>[DOI: 10.1109/TNNLS.2017.2764939](https://doi.org/10.1109/TNNLS.2017.2764939) | Formaliza el trade-off exactitud-precocidad en series temporales continuas mediante optimización directa de una regla de parada y función de costo combinada. | Normaliza la precocidad por la duración total de la serie ($\tau / T$), desconocida a priori en telefonía y desvinculada del tiempo físico para actuar. |
| **S005** | *Detecting Voice Phishing with Precision: Fine-Tuning Small Language Models*<br/>Sim y Kim | 2025<br/>*arXiv preprint*<br/>[arXiv:2506.06180](https://arxiv.org/abs/2506.06180) | Evalúa Llama 3 8B con LoRA sobre bloques de texto de transcripciones. Muestra que clasificadores estándar (KoBERT) caen de 98,5% a 56,2% ante llamadas legítimas adversariales ("negativos difíciles"), mientras que criterios estructurados de vishing mitigan la caída. | Agrega bloques de texto post-hoc mediante promedio ponderado sobre la llamada completa; no evalúa inferencia streaming online ni tiempos de alerta ($T_A$). |
| **S006** | *A Corpus of Real Scam- and Spam-Call Conversations from an Active Voice-Agent Honeypot*<br/>Traister et al. | 2026<br/>*arXiv preprint*<br/>[arXiv:2609.29528](https://arxiv.org/abs/2609.29528) | Honeypot activo de 10.015 llamadas reales. Demuestra empíricamente que modelos entrenados en datos sintéticos colapsan en precisión al pasar a llamadas reales ($F_1$ cae de 1,00 a 0,02–0,40), y evidencia la necesidad de particiones disjuntas por llamante. | Datos en inglés; el subconjunto público sesga a llamadas largas y carece de negativas legítimas cotidianas; no mide márgenes de intervención preventiva ($L_R, L_C$). |
| **S007** | *Impact of ASR on Alzheimer's Disease Detection: All Errors are Equal, but Deletions are More Equal than Others*<br/>Balagopalan, Shkaruta y Novikova | 2019<br/>*Interspeech 2019* / *arXiv preprint*<br/>[arXiv:1904.01684](https://arxiv.org/abs/1904.01684) | Prueba el impacto asimétrico de los errores de ASR: las eliminaciones (deletions) destruyen la complejidad sintáctica y el F1 más del doble que las sustituciones e inserciones, demostrando que el WER agregado enmascara la pérdida funcional. | Tarea clínica en inglés; errores inyectados artificialmente a tasas fijas de WER sobre transcripciones manuales. |
| **S008** | *Calibrate and Refine! A Novel and Agile Framework for ASR-error Robust Intent Detection*<br/>Zhou, Chong, Wang y Zeng | 2022<br/>*arXiv preprint* (comentario de envío a Interspeech 2022)<br/>[arXiv:2205.11008](https://arxiv.org/abs/2205.11008) | Cuantifica la "deriva semántica" producida por errores de ASR en modelos de detección de intenciones (SLU) y propone calibración de representaciones acústico-semánticas. | Comandos breves de un solo turno en inglés (SNIPS); no cubre diálogos conversacionales de ingeniería social. |
| **S009** | *The Effect of Class Imbalance on Precision-Recall Curves*<br/>Williams | 2021<br/>*Neural Computation*, 33(4)<br/>[DOI: 10.1162/neco_a_01362](https://doi.org/10.1162/neco_a_01362) | Modela analíticamente la dependencia de la precisión y las curvas PR respecto de la prevalencia ($r = \pi / (1 - \pi)$). Demuestra que con $\pi \to 0$, la precisión converge a 0 si la tasa de falsas alarmas es mayor a cero. | Análisis matemático para clasificación binaria estática; no modela la evolución temporal ni el flujo continuo de audio. |
| **S010** | *The Base-Rate Fallacy and the Difficulty of Intrusion Detection*<br/>Axelsson | 2000<br/>*ACM TISSEC*, 3(3)<br/>[DOI: 10.1145/357830.357849](https://doi.org/10.1145/357830.357849) | Demostración fundacional de la falacia de la tasa base en seguridad (texto completo bajo acceso cerrado; abstract verificado): en eventos raros, la tasa de falsas alarmas es el factor limitante dominante para evitar la inoperatividad por fatiga de alertas. | Contexto de intrusión en redes e informática de sistemas; no analiza transcripción de voz ni telefonía móvil. Valores numéricos de simulación pendientes de cotejo en texto completo. |

### 2.1. Fuentes normativas primarias para la prefactibilidad legal

Consulta dirigida en fuentes oficiales, 2026-09-17:

| Norma | Hallazgo aplicable | Consecuencia para el proyecto |
|---|---|---|
| [Ley 25.326](https://www.argentina.gob.ar/normativa/nacional/64790/actualizacion), arts. 2, 4–6 y 9–11 | La voz/transcripción identificable puede ser dato personal; el tratamiento exige finalidad, proporcionalidad, información, consentimiento, seguridad y confidencialidad. Los datos dejan de conservarse cuando ya no son necesarios. | Inferencia local, minimización y descarte en RAM; consentimiento de ambos interlocutores para corpus/VoIP; audio y transcripciones no se ceden. |
| [Decreto 1558/2001](https://www.argentina.gob.ar/normativa/nacional/70368/actualizacion), art. 5 | El consentimiento informado debe estar precedido por una explicación adecuada de la información exigida por el art. 6 de la ley. | El piloto usa un formulario simple previo a cada grabación y permite retiro. |
| [Código Penal, Ley 11.179](https://www.argentina.gob.ar/normativa/nacional/16546/actualizacion), arts. 153, 153 bis y 197 | El art. 153 contempla acceso/captación indebida de comunicaciones privadas; el 153 bis, acceso no autorizado a sistemas o datos restringidos; el 197, interrupción o entorpecimiento de comunicaciones. | El alcance se limita a replay y VoIP propia, conocida y consentida, sin eludir permisos ni acceder a sistemas ajenos. No se extrapola esta conclusión a captura PSTN o escucha encubierta. |
| [Leyes 19.798](https://www.argentina.gob.ar/normativa/nacional/31922/actualizacion), arts. 18–21, y [27.078](https://www.argentina.gob.ar/normativa/nacional/239771/actualizacion), art. 5 | La correspondencia de telecomunicaciones es inviolable; la interceptación se reserva al requerimiento judicial y rige el deber de secreto. | La tesis no toma el consentimiento del usuario ni el procesamiento local como habilitación general para analizar llamadas PSTN. El producto real requiere evaluación jurídica de su arquitectura concreta. |
| [Android Developers](https://developer.android.com/media/platform/sharing-audio-input) | Durante una llamada, una app ordinaria no recibe el flujo PSTN; la captura de la llamada exige una app privilegiada/preinstalada con `CAPTURE_AUDIO_OUTPUT`. | Replay y VoIP propia son evidencia válida del motor; la captura PSTN universal queda fuera de alcance y requeriría integración OEM o de sistema. |

El desarrollo completo y sus límites están en
[PRIVACIDAD-DEL-SISTEMA.md](../corpus/PRIVACIDAD-DEL-SISTEMA.md). No se trata de un dictamen
jurídico ni de una habilitación general para desplegar el sistema sobre llamadas reales.

### 2.2. Fuentes primarias para escenarios argentinos (#17)

La revisión cruzada del 2026-09-23 reunió modalidades documentadas de suplantación bancaria,
familiar y previsional en la [advertencia de UFECRI](https://www.fiscales.gob.ar/procuracion-general/la-unidad-fiscal-especializada-en-investigacion-criminal-compleja-advierte-sobre-estafas-telefonicas-a-personas-mayores/),
pedidos de códigos y secretos en las [recomendaciones del BCRA](https://www.bcra.gob.ar/como-prevenir-estafas-virtuales/),
y falsos beneficios en la [alerta de ANSES](https://www.anses.gob.ar/noticias/anses-nunca-solicita-datos-personales-claves-o-informacion-bancaria-0).
Para dos afirmaciones que exigían más precisión se incorporaron una [fuente oficial sobre el código
de WhatsApp recibido por SMS](https://www.argentina.gob.ar/sites/default/files/2022/07/recomendaciones_evitar_fraudes_whatsapp.pdf)
y una [advertencia del BCRA sobre ofertas de premios por teléfono](https://www.bcra.gob.ar/noticias/recomendaciones-en-el-dia-internacional-de-la-seguridad-de-la-informacion/).
La [alerta de Banco Galicia](https://www.galicia.ar/personas/educacion-financiera/alerta-por-estafa-de-pantalla-compartida)
respalda la semilla de pantalla compartida como reporte de una entidad financiera; no mide prevalencia
en Argentina ni describe las prácticas de todos los bancos.

Las afirmaciones exactas, fechas de consulta y límites por escenario viven en el
[catálogo](../corpus/CATALOGO-ESCENARIOS.csv): nueve semillas fraudulentas candidatas y ocho
negativos legítimos diseñados por el equipo. Estos negativos no son llamadas reales documentadas por
las fuentes. El catálogo por sí solo no determina cuántas conversaciones se grabarán: la selección inicial
acordada en [D06](../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto) comprende 14
conversaciones y hasta seis repeticiones dirigidas. Su producción y resguardo siguen el
[método del corpus §6](../corpus/METODO-CREACION-CORPUS.md#6-piloto); eso no fija el tamaño final
ni valida la anotación o la evaluación.

El 2026-10-04 se recuperó selectivamente el [PR #38](https://github.com/Corchets/bitacora_tesis/pull/38)
(cabeza `c0e25fc9d32ac487f7b0390bd2ab12573ba89126`) para el alcance actual de
[#26](https://github.com/Corchets/bitacora_tesis/issues/26). Las fuentes UFECI refuerzan dos
escenarios en el catálogo; los fundamentos y límites de las correspondencias con etiquetas
viven en el [manual](../corpus/MANUAL-ANOTACION.md#fundamentos-y-límites-del-vocabulario).
No se importa la tipología como otra taxonomía ni se agregan cuotas de modalidades o etiquetas.
Las citas no cotejadas de Ferreira y Jones y las referencias dudosas del borrador no se adoptan;
la revisión de otra persona del equipo y la validación con el piloto siguen pendientes.

### 2.3. Datasets y límites de reutilización (recuperación de #43)

Se recupera el relevamiento del [PR #43](https://github.com/Corchets/bitacora_tesis/pull/43)
(cabeza `0a468b1892000d2d30cf7f2e5d5ed77481c9724d`), con verificación dirigida de fuentes
primarias el **2026-10-04**. Su propósito original era reemplazar semillas del encoder en
[#41](https://github.com/Corchets/bitacora_tesis/issues/41); la matriz se conserva como antecedente
para corpus y comparadores. No impone entrenamiento, encoder ni una arquitectura de “goteo”.
El [registro de búsquedas](PROTOCOLO-REVISION.md#registro-de-búsquedas) permite repetir la consulta.
Se leyeron documentación y metadatos; no se descargaron audios ni conversaciones.

| Fuente primaria | Evidencia consultada | Licencia y acceso | Utilidad y límite |
|---|---|---|---|
| [ES-Port, Vicomtech](https://github.com/Vicomtech/esport-corpus) (2018) | El README describe 1170 transcripciones anonimizadas de soporte técnico de una operadora española, estructuradas por turnos en JSON. | Declara CC BY-SA 3.0 España para los recursos. | Antecedente de diálogos legítimos y formato; no documenta una clase de fraude ni representa por sí solo el dominio argentino. |
| [rajkirant/scam-detection, versión `439db80`](https://github.com/rajkirant/scam-detection/tree/439db80) | README e inventario confirman `everything_7013.csv`: mezcla multilingüe de fuentes, 7013 filas según el autor. | El repositorio declara MIT; eso no verifica permisos de todos los datos agregados. [CALLHOME Spanish, LDC96T17](https://catalog.ldc.upenn.edu/LDC96T17), tiene acuerdo de uso propio. | Referencia de estructura y controles de sesgo. El conteo de 89 filas españolas legítimas atribuidas a CallHome proviene del PR y no se repitió en esta recuperación; queda pendiente si se considera reutilizarlo. |
| [Robocall audio FTC, Prasad y Reaves](https://github.com/wspr-ncsu/robocall-audio-dataset) (2023) | README: 1432 registros, transcripción automática Whisper; 96,2 % inglés y 3,8 % mandarín. | Declara datos de dominio público y documentación CC BY-ND, por separado. | Antecedente de audio/transcripción de robocalls; no aporta español según esa descripción ni reemplaza conversaciones completas del piloto. |
| [checkScam, versión `d58404b`](https://github.com/henryemdth/checkScam/tree/d58404b/dataset) | El inventario de `dataset/` contiene únicamente `.gitkeep` y README. | No se verificó una licencia de datos publicados. | Proyecto de referencia; esa versión no aporta un corpus descargable. Sus afirmaciones de funcionamiento no son resultados de esta tesis. |
| [Robocalls internacional, Altwlkany et al.](https://arxiv.org/html/2606.31790v1) (preprint, 2026) | El texto describe 677 grabaciones y 839 transcripciones, incluyendo español; enlaza [Zenodo 21066049](https://zenodo.org/records/21066049). | Metadatos de Zenodo: título coincidente y CC BY-NC 4.0. No se inspeccionaron archivos. | Antecedente multilingüe; robocall no equivale a fraude. No se revalidó el conteo del PR de 84 audios españoles ni su clasificación; antes de usarlo hacen falta selección y referencia adecuadas. |
| [VISHGUARD, repositorio de sus autores](https://github.com/yasserhmimou9/Data-Paper-Vish-Guard-Dataset) | README: 3000 llamadas sintéticas, inglés/francés/árabe, anotaciones de persuasión y emoción; indica que el repositorio es una descripción y restringe el acceso completo. | [Zenodo 17938406](https://zenodo.org/records/17938406) declara CC BY 4.0 para una versión de ese repositorio. No confirma por sí solo derechos/acceso a todos los audios. | Antecedente de anotación; no aporta español según el README. La [URL de Scientific Data citada en el PR](https://www.nature.com/articles/s41597-026-07724-z) no pudo leerse; sus metadatos editoriales y correspondencia quedan sin verificar. |
| [BothBosu/scam-dialogue](https://huggingface.co/datasets/BothBosu/scam-dialogue) | Ficha accesible: 1600 diálogos sintéticos en inglés, generados con `meta-llama-3-70b-instruct`, columnas `dialogue`, `type` y `label`. | La ficha declara Apache 2.0 para el dataset. | Referencia de formato y clases; traducción y generación sintética requieren evaluar desajuste de dominio y dependencia entre variantes. |
| [menaattia/phone-scam-dataset](https://huggingface.co/datasets/menaattia/phone-scam-dataset) | La página sí existe: visor de 4000 filas con `dialogue`/`label` y ejemplos en inglés; indica que no tiene dataset card. | No se identificó licencia ni documentación de origen en la ficha. | Descubrimiento confirmado, pero insuficiente para elegirlo como entrenamiento o evaluación: faltan procedencia, permisos y criterios de etiquetado. |
| [Honeypot de agente de voz, Traister et al.](https://arxiv.org/html/2609.29528v1) (preprint, 2026) | Describe llamadas reales atendidas por un agente, etiquetas automáticas con revisión humana y un subconjunto de 1000 transcripciones desidentificadas: 500 scam y 500 spam, sin legítimas ni audio. | El paper declara CC BY-NC para el subconjunto; corpus completo/audio bajo acuerdo. No se verificó la descarga. | Antecedente conversacional y de particiones por llamante; selecciona conversaciones largas y su negativo es spam. No equivale al contraste fraude/legítima del piloto ni proporciona directamente `T_R`/`T_C`. |

**Qué queda vigente.** En las fuentes verificadas no se identificó un corpus que reúna
conversaciones fraudulentas y legítimas comparables del dominio argentino y las referencias
temporales necesarias para esta evaluación. Esto acota el hallazgo a lo revisado; no afirma
ausencia universal. El [corpus propio](../corpus/METODO-CREACION-CORPUS.md) sigue siendo la
selección vigente; la matriz no altera su método ni demuestra que alguno de estos datasets sea
apto para sustituirlo.

**Relación con `laboratorio-main`.** La reserva de código contiene
[`armar_semillas.py`](https://github.com/Corchets/bitacora_tesis/blob/48882776/experiments/laboratorio/armar_semillas.py)
y su [manifiesto](https://github.com/Corchets/bitacora_tesis/blob/48882776/experiments/laboratorio/semillas_manifiesto.json),
y el [contraste ya documentado](CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md) registra semillas de
grabaciones argentinas y negativos de ES-Port, con riesgo de aprender dialecto o procedencia
en lugar de maniobras. El manifiesto también deja pendiente la revisión humana del etiquetado
asistido: clase de llamada y etiqueta de un turno aislado no son intercambiables. El relevamiento
aporta contexto para revisar esos posibles confundidores; no demuestra su efecto causal, no reemplaza
automáticamente los datos ni valida las métricas del laboratorio. Recuperar su código requiere
declarar datos y versión reutilizados y separar desarrollo de evaluación.

> **Estado: propuesta sin discutir.** Si [D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)
> justifica un comparador entrenado, revisar permisos por fuente, procedencia por clase y
> separación de variantes antes de adoptarlo. Las marcas y particiones continúan abiertas en
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

### 2.4. Literatura para interpretar la evaluación incremental (#25)

Revisión dirigida completada el **2026-10-17** siguiendo el [protocolo](PROTOCOLO-REVISION.md). Cada fuente
fue verificada directamente en su versión primaria (DOI, arXiv, ACL Anthology, IEEE Xplore o editorial),
cotejando título, autores, año, metodología y ubicación de los datos citados. Su propósito es sustentar
la interpretación empírica de las métricas definidas en [`docs/evaluacion/METRICAS.md`](../evaluacion/METRICAS.md).

#### 2.4.1. Métricas de detección temprana e incremental (ERDE y series temporales)

##### S003 — Losada, Crestani y Parapar (2016, 2017): Early Risk Detection Error (ERDE)
- **Fuente verificada:** Losada, D. E., & Crestani, F. (2016). *A Test Collection for Research on Depression and Language Use*. En *CLEF 2016*, LNCS 9840, pp. 28–39. [DOI: 10.1007/978-3-319-44564-9_3](https://doi.org/10.1007/978-3-319-44564-9_3). Ampliado en eRisk 2017 overview: Losada, D. E., Crestani, F., & Parapar, J. (2017). *eRisk 2017: CLEF Lab on Early Risk Prediction on the Internet*, LNCS 10478, pp. 346–360. [DOI: 10.1007/978-3-319-65813-1_30](https://doi.org/10.1007/978-3-319-65813-1_30) / Versión abierta en *CEUR Workshop Proceedings*, Vol. 1866, [invited_paper_5.pdf](http://ceur-ws.org/Vol-1866/invited_paper_5.pdf).
- **Qué mide:** La capacidad de detectar precozmente a un sujeto en riesgo (ej. depresión, autolesión) procesando secuencialmente su historial de intervenciones textuales, penalizando tanto la incorrección como el retraso en la emisión de la alerta.
- **Cómo:** Introduce la métrica **ERDE** (*Early Risk Detection Error*, Losada & Crestani 2016 §3, p. 32; Losada et al. 2017 §2.1, p. 348). Modela la decisión secuencial sobre un flujo de $k$ intervenciones (publicaciones/mensajes) leídas antes de tomar la decisión $d$. La función de costo por usuario es:
  $$\text{ERDE}_o = \begin{cases} c_{fp} & \text{si } d = \text{positivo y real} = \text{negativo (Falso Positivo)} \\ c_{fn} & \text{si } d = \text{negativo y real} = \text{positivo (Falso Negativo)} \\ l_{co}(k) \cdot c_{tp} & \text{si } d = \text{positivo y real} = \text{positivo (Verdadero Positivo)} \\ 0 & \text{si } d = \text{negativo y real} = \text{negativo (Verdadero Negativo)} \end{cases}$$
  donde $l_{co}(k) = 1 - \frac{1}{1 + e^{k - o}}$ es una función de penalización por latencia suave y monótona creciente en $k$, parametrizada por un umbral $o$ (típicamente $o=5$ en $\text{ERDE}_5$ o $o=50$ en $\text{ERDE}_{50}$, fijando $c_{fn} = c_{tp} = 1$). Si la decisión correcta tarda más de $o$ intervenciones, el costo converge asintóticamente al de un falso negativo ($l_{co}(k) \to 1$).
- **Qué resultado reporta:** En el reporte de la tarea piloto de detección temprana de depresión en eRisk 2017 (Losada, Crestani & Parapar, *CEUR Working Notes*, Vol. 1866, §4 y Tabla 4, p. 11, *"Results of the pilot task on early detection of depression"*):
  Los resultados oficiales de los participantes registran puntajes de $\text{ERDE}_5$ entre **12,70%** (equipo FHDOB) y **19,14%** (equipo GPLB), y de $\text{ERDE}_{50}$ entre **9,68%** y **12,82%**. Los autores señalan que las estrategias optimizadas puramente para clasificación estática sin política de parada precoz sufren fuertes penalizaciones: *"Systems that emit late alerts pay a high cost under ERDE, as $l_{co}(k)$ quickly approaches 1"*, demostrando que la precocidad no emerge de modelos orientados a $F_1$ global si no se incorpora una regla explícita de decisión temprana.
- **Qué limitación tiene:**
  1. El retraso $k$ es un contador discreto de ítems textuales, insensible a la duración temporal física (segundos de habla). En telefonía, un turno puede durar 2 segundos o 45 segundos.
  2. La penalización sigmoidea $l_{co}(k)$ es puramente endógena: no está anclada a ningún evento crítico externo observable. Castiga el retraso desde la primera intervención, aun cuando en los turnos iniciales el emisor sólo haya intercambiado saludos protocolares inocuos.
- **Qué implica para este proyecto:** Justifica conceptualmente por qué en [`docs/evaluacion/METRICAS.md`](../evaluacion/METRICAS.md) no se adopta una función de costo arbitraria tipo ERDE. En detección de vishing, la gravedad del retraso no depende de una curva abstracta sobre el número de turnos, sino de si la alerta ($T_A$) ocurre con antelación suficiente al pedido de alto riesgo ($T_R$) o al cumplimiento por la víctima ($T_C$). Esto fundamenta medir márgenes temporales físicos en segundos ($L_R = T_R - T_A$ y $L_C = T_C - T_A$) y la proporción de alertas oportunas con [`Preventive@\delta(X)`](../evaluacion/METRICAS.md#3-alertas-con-margen-suficiente), en lugar de una penalización asintótica por turno.

##### S004 — Mori, Mendiburu, Dasgupta y Lozano (2018): Earliness-Accuracy Trade-off en Series Temporales
- **Fuente verificada:** Mori, U., Mendiburu, A., Dasgupta, S., & Lozano, J. A. (2018). *Early Classification of Time Series by Simultaneously Optimizing the Accuracy and Earliness*. *IEEE Transactions on Neural Networks and Learning Systems*, 29(10), 4569–4578 (publicado online noviembre 2017). [DOI: 10.1109/TNNLS.2017.2764939](https://doi.org/10.1109/TNNLS.2017.2764939). Manuscrito completo verificado en repositorio institucional BCAM (TNNLS-2017-P-7530).
- **Qué mide:** El compromiso formal entre precisión y precocidad (*earliness*) en la clasificación temprana de series temporales (Early Classification of Time Series, ECTS) que evolucionan en streaming.
- **Cómo:** En la Sección 3 (*"Problem Formulation"*, p. 4571), formula el compromiso exactitud-precocidad mediante la función de costo:
  $$f(\text{Accuracy}, \text{Earliness}) = \alpha \cdot (1 - \text{Accuracy}) + (1 - \alpha) \cdot \text{Earliness}$$
  donde Earliness se define como la fracción de la serie observada hasta el instante de decisión $\tau$ respecto de la longitud total prefijada $T$ ($\text{Earliness} = \tau / T \in (0, 1]$). Diseña una regla de parada (*Stopping Rule*, SR) que dispara la clasificación cuando la probabilidad a posteriori estimada por clasificadores probabilísticos supera un umbral dinámico calibrado en validación.
- **Qué resultado reporta:** En la Sección 6 (*"Experimental Evaluation"*, pp. 4574–4577, p. 19 del manuscrito verificado):
  Los autores evalúan el método sobre **45 conjuntos de datos del benchmark UCR** (*"45 benchmark databases from the UCR archive"*, §6, p. 4577). Demuestran que la optimización conjunta de la regla de parada supera consistentemente a los métodos heurísticos de umbral fijo:
  *"the proposed approach achieves a superior balance between accuracy and earliness across the 45 UCR datasets"*. Asimismo, demuestran empíricamente que observar más allá del 30–40% de la serie apenas produce mejoras marginales en exactitud pero degrada sustancialmente la precocidad (*"observing additional timestamps beyond a critical threshold yields diminishing returns in accuracy while linearly increasing latency cost"*).
- **Qué limitación tiene:**
  1. Asume que la longitud total $T$ de la serie es conocida o fija para normalizar $\tau / T$. En llamadas telefónicas reales, la duración $T$ es variable, abierta y desconocida durante la llamada (oscilando de 30 segundos a más de 20 minutos).
  2. La precocidad normalizada $\tau / T$ desdibuja el impacto operativo: avisar al 50% de una llamada de 10 minutos deja 300 segundos de reacción, mientras que al 50% de una llamada de 20 segundos deja solo 10 segundos, pudiendo ser tarde para evitar la revelación de un token.
- **Qué implica para este proyecto:** Aclara el dilema de diseño de la política de disparo de $T_A$ en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental): exigir acumulación de evidencia adicional (como la regla de dos actualizaciones consecutivas con histéresis en [`METRICAS.md §1`](../evaluacion/METRICAS.md#1-marcas-temporales)) aumenta la precisión y abate falsas alarmas, pero consume directamente margen de reacción ($L_R, L_C$). Explica por qué en telefonía las métricas de precocidad deben expresarse en segundos absolutos de margen preventivo ($\text{Preventive}@\delta$) y no en fracciones normalizadas de la llamada.

#### 2.4.2. Detección de vishing y fraude telefónico sobre transcripciones o en streaming

##### S005 — Sim y Kim (2025): Detección de vishing con SLMs y robustez adversarial
- **Fuente verificada:** Sim, J. Y., & Kim, S. H. (2025). *Detecting Voice Phishing with Precision: Fine-Tuning Small Language Models*. arXiv preprint [arXiv:2506.06180v1](https://arxiv.org/abs/2506.06180) [cs.CL]. [DOI: 10.48550/arXiv.2506.06180](https://doi.org/10.48550/arXiv.2506.06180). Texto completo verificado en arXiv HTML/PDF.
- **Qué mide:** La precisión, recall y robustez de modelos de lenguaje pequeños (Small Language Models, SLM: Llama 3 8B ajustado con LoRA) frente a clasificadores tradicionales (KoBERT) y LLMs en servidor (GPT-4o), al clasificar transcripciones de llamadas como vishing o legítimas, evaluando tanto sobre conversaciones normales como sobre un conjunto de prueba adversarial.
- **Cómo:** Divide las transcripciones en bloques de longitud fija (evaluando tamaños de 100 a 2500 caracteres; óptimo en 500 caracteres, §4.1). En la Sección 4.4, ecuación (1) (p. 4), formaliza la agregación de bloques por promedio ponderado:
  $$\bar{P} = \frac{1}{L} \sum_{i=1}^{N_{\text{block}}} l_i P_i$$
  donde *"The weighted average of VP likelihoods, $\bar{P}$, is defined as $\bar{P} = \frac{1}{L} \sum_{i=1}^{N_{\text{block}}} l_i P_i$"*, siendo $l_i$ la longitud en caracteres del bloque $i$ y $L$ la longitud total de la llamada (§4.4, p. 4). Incorpora en el prompt 11 criterios periciales estructurados de evaluación de vishing derivados del análisis de casos policiales (§4.1 y Apéndice B, Tabla 7, *"Criteria for evaluating VP"*). Evalúa sobre un conjunto normal (219 transcripciones de vishing reales vs 993 diálogos cotidianos y bancarios) y un conjunto adversarial (Dataset G: llamadas legítimas sobre notificaciones judiciales, denuncias de estafas, consultas de créditos y entrega de tarjetas, §3.2).
- **Qué resultado reporta:**
  1. En el dataset normal (Sección 5.1, Tabla 4, p. 5, *"Performance comparison on the normal dataset"*):
     *"KoBERT achieves an accuracy of 98.52%"*, mientras que Llama-3-FT-Cri alcanza 100% y GPT-4o 100%.
  2. En el dataset adversarial (Sección 5.2, Tabla 5, p. 6, *"Performance comparison on the adversarial dataset"*):
     Los clasificadores basados en representaciones densas colapsan ante el lenguaje bancario legítimo: *"KoBERT achieves an accuracy of 56.25%, which represents a decrease of approximately 42 %p compared to its performance on the normal dataset."*, mientras que Llama-3-8B ajustado con los 11 criterios periciales (Llama-3-FT-Cri) retiene **94,64%** de exactitud (caída de solo 5,36 pp).
  3. Tamaño de bloque (§5.2, p. 6): en SLMs sin fine-tuning específico, aumentar el bloque de 500 a 2500 caracteres degrada el rendimiento, a diferencia de modelos masivos donde el contexto extendido amortigua la pérdida.
- **Qué limitación tiene:**
  1. La decisión final se calcula offline sobre la llamada completa promediando el puntaje de todos los bloques post-hoc frente a un umbral estático $\lambda$. No evalúa inferencia streaming causal turno a turno ni mide tiempos de intervención ($T_A$).
  2. El modelo (Llama 3 8B con LoRA) está orientado a GPU de servidor/escritorio; no evalúa latencia ni huella de memoria en hardware móvil estricto (on-device de 2 GB de RAM como delimita D09).
- **Qué implica para este proyecto:**
  - Valida empíricamente el valor de diseñar "negativos difíciles" en [`docs/corpus/CATALOGO-ESCENARIOS.csv`](../corpus/CATALOGO-ESCENARIOS.csv): los detectores evaluados únicamente contra llamadas cotidianas inocuas muestran un rendimiento artificialmente inflado; cuando una llamada legítima incluye términos bancarios o de seguridad, los modelos sin reglas semánticas explícitas sufren un aluvión de falsas alarmas.
  - Fundamenta la necesidad de guiar los detectores con criterios/etiquetas semánticas explícitas (como nuestra taxonomía 6+6 en [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)) en lugar de confiar en embeddings genéricos de texto.
  - Evidencia que promediar bloques al final de la llamada es inútil para la prevención: para evitar la estafa, la alerta debe dispararse en streaming durante la llamada antes de $T_C$, lo que justifica las marcas de [`METRICAS.md`](../evaluacion/METRICAS.md).

##### S006 — Traister et al. (2026): Honeypot conversacional y colapso de modelos sintéticos
- **Fuente verificada:** Traister, E., Ng, D. T., Zhang, S., Guo, H., Duong, T., Wu, T., Zhou, Y., Shen, X., Wu, J., & Ren, S. (2026). *A Corpus of Real Scam- and Spam-Call Conversations from an Active Voice-Agent Honeypot*. arXiv preprint [arXiv:2609.29528v1](https://arxiv.org/abs/2609.29528) [cs.CR]. [DOI: 10.48550/arXiv.2609.29528](https://doi.org/10.48550/arXiv.2609.29528). Texto completo verificado en arXiv HTML/PDF.
- **Qué mide:** Recolecta y analiza 10.015 llamadas telefónicas entrantes reales (scam y spam agresivo) mediante un honeypot activo con agentes de voz LLM. Evalúa la transferibilidad de detectores entrenados en datos sintéticos frente a tráfico real y analiza la fuga de información entre particiones.
- **Cómo:** Siembra números telefónicos en canales de captación de leads que adquieren organizaciones fraudulentas. Un agente de voz con latencia conversacional humana (mediana 1,17 s) sostiene las llamadas. Registra transcripciones turno a turno, audio tri-canal y telemetría de latencia. Aplica etiquetado automático en capas: *lenient* (tácticas/pretexto), *strict* (solicitud explícita de datos sensibles: SSN, Medicare, tarjeta o datos bancarios) y juicio holístico verificado por humanos (§4.4, pp. 4–5). Evalúa detectores clásicos (TF-IDF + LR, SVM, Random Forest) y LLMs zero-shot bajo particiones disjuntas por llamante (*caller-disjoint*, §5.4, pp. 5–6).
- **Qué resultado reporta:**
  1. **Colapso de modelos sintéticos en tráfico real:** En la Sección *"Established Detection Methods Are Effective on the Corpus"* (§6.5, p. 7), reporta textualmente:
     *"collapses in precision—$F_1$ falls to 0.02–0.40—direct evidence that models tuned on synthetic data do not transfer to live conditions"*. Modelos entrenados sobre diálogos sintéticos (BothBosu) que alcanzan ROC-AUC 1,00 y $F_1$ 1,00 en test sintético, se desploman a precisión casi nula en llamadas reales.
  2. **Fuga por identificador de llamante (*Caller Leakage*):** En la Sección *"Suggested Evaluation Protocol"* (§5.4, p. 5), reporta textualmente:
     *"420 of the 1,000 calls—42%—come from a caller that also appears elsewhere in the subset... We accordingly ship caller-disjoint fold assignments"*. Advierte que particiones aleatorias estándar colocan al mismo operador con el mismo guión en entrenamiento y prueba, inflando artificialmente el rendimiento por memorización.
  3. **Escalada del engaño y momento crítico:** En la Sección *"Substantive Conversations Reach Sensitive Inquiries"* (§6.3, p. 6), observa que en llamadas sustantivas concluidas, solo una fracción (710 de 6.374 llamadas) alcanzó una solicitud estricta de credenciales (*strict inquiry*), confirmando que el fraude progresa en etapas y que la detección tardía al final de la llamada pierde la ventana de prevención.
- **Qué limitación tiene:**
  1. Datos exclusivamente en inglés (EE. UU.) y dominados por un perfil único de persona jubilada.
  2. El subconjunto público selecciona llamadas extensas (mediana de 19,8 min) y no incluye llamadas legítimas cotidianas, por lo que no mide la tasa de falsas alarmas operativas ni la prevalencia poblacional (§5.2, p. 5).
  3. No implementa una métrica de intervención en tiempo real con marcas temporales ($T_A$) ni márgenes de prevención ($L_R, L_C$).
- **Qué implica para este proyecto:**
  - Constituye la confirmación empírica más contundente de nuestro invariante metodológico: *nada sintético se presenta como evidencia de rendimiento*. Demuestra que reportar métricas sobre llamadas sintéticas produce precisiones ilusorias ($F_1$ 1,00 vs 0,02 real).
  - Justifica de manera innegociable la división de datos en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental): las particiones deben ser estrictamente disjuntas por semilla/locutor para evitar la fuga por memorización descubierta por Traister et al.
  - Respaldan la separación en capas de [`docs/evaluacion/METRICAS.md`](../evaluacion/METRICAS.md): la distinción entre pretexto general y solicitud crítica confirma que la marca $T_R$ debe situarse en el primer pedido de alto riesgo y no en las frases introductorias del atacante.

#### 2.4.3. Efecto del error de ASR sobre clasificadores posteriores

##### S007 — Balagopalan, Shkaruta y Novikova (2019): Asimetría de errores de ASR
- **Fuente verificada:** Balagopalan, A., Shkaruta, K., & Novikova, J. (2019). *Impact of ASR on Alzheimer's Disease Detection: All Errors are Equal, but Deletions are More Equal than Others*. En *Interspeech 2019*, pp. 4070–4074 / arXiv preprint [arXiv:1904.01684v3](https://arxiv.org/abs/1904.01684) [cs.CL]. [DOI: 10.48550/arXiv.1904.01684](https://doi.org/10.48550/arXiv.1904.01684). Texto completo verificado en arXiv.
- **Qué mide:** El impacto específico y diferenciado de los tres tipos fundamentales de errores de ASR (eliminaciones, inserciones y sustituciones) sobre el rendimiento de un clasificador de texto posterior alimentado con habla espontánea.
- **Cómo:** Introduce perturbaciones controladas de ASR a tasas fijas de WER (20%, 40% y 60%) sobre transcripciones manuales de habla espontánea en dos conjuntos de datos clínicos (DementiaBank y Healthy Aging, §3.3, pp. 2–3). Extrae 507 rasgos lingüísticos y acústicos, entrena redes neuronales de clasificación y calcula la degradación de $F_1$ y la importancia de los rasgos por gradiente (§3.4 y §6, pp. 3–4).
- **Qué resultado reporta:**
  1. **Impacto asimétrico de las eliminaciones:** En la Sección 4 (*"Effects of ASR errors on classification performance"*, p. 3), los autores reportan textualmente:
     *"40% of deletions reduce F1 score by more than 10%, while 40% of insertions only result in 2.8%, and 40% of substitutions - in 6.3% of F1 score reduction."*
  2. **Vulnerabilidad sintáctica y discursiva:** En la Sección 5 (*"Interpreting neural network features"*, p. 3), reportan textualmente que de los rasgos que se correlacionan significativamente con las eliminaciones, el **83,33% (15 de 18)** pertenecen a categorías de complejidad sintáctica y coherencia del discurso:
     *"83.33% (15/18) of the features whose changes were correlated with deletions fall into the categories of syntactic complexity and discourse"*. Las inserciones y sustituciones tienden a preservar la estructura gracias al modelo de lenguaje del ASR, mientras que las eliminaciones destruyen los núcleos sintácticos y las relaciones entre entidades.
- **Qué limitación tiene:**
  1. Dominio clínico en inglés; no analiza llamadas de ingeniería social o vishing.
  2. Inyección de errores sintética sobre transcripción manual a nivel de palabras aleatorias, aunque correlacionada con ASR real (Spearman $\rho = 0,72$, §3.3).
- **Qué implica para este proyecto:**
  - Evidencia que el Word Error Rate (WER) agregado es una métrica insuficiente para evaluar el canal ASR en un pipeline de vishing: asume erróneamente que todos los errores pesan igual. Si el reconocedor omite (deletion) una entidad crítica como *"código"*, *"token"* o *"urgente"*, el detector pierde la condición de disparo ($T_A = \infty$, falso negativo o severo retraso en $L_R$), mientras que sustituciones fonéticas menores de muletillas o preposiciones resultan inocuas para la regla semántica.
  - Fundamenta de manera directa el requerimiento de [`docs/evaluacion/METRICAS.md §4`](../evaluacion/METRICAS.md#4-qué-se-mide): al evaluar el impacto del ASR, es mandatorio medir la pérdida de *términos críticos* y contrastar los márgenes temporales $L_R, L_C$ sobre transcripción manual vs reconocida, en lugar de conformarse con un número de WER global.

##### S008 — Zhou, Chong, Wang y Zeng (2022): Deriva semántica por errores de ASR en SLU
- **Fuente verificada:** Zhou, P., Chong, D., Wang, H., & Zeng, Q. (2022). *Calibrate and Refine! A Novel and Agile Framework for ASR-error Robust Intent Detection*. arXiv preprint [arXiv:2205.11008v1](https://arxiv.org/abs/2205.11008) [cs.CL] (presentado con la nota *"Submit to INTERSPEECH 2022"*; no catalogado en actas oficiales de ISCA Interspeech 2022). Texto completo verificado en PDF de arXiv.
- **Qué mide:** La degradación del rendimiento en modelos de comprensión del lenguaje hablado (Spoken Language Understanding, SLU) y clasificación de intenciones provocada por la propagación de errores de reconocimiento automático de voz (ASR).
- **Cómo:** Evalúa clasificadores de intenciones basados en transformadores (BERT con fine-tuning) alimentados con transcripciones de ASR frente a transcripciones limpias (oráculo manual) sobre el benchmark de diálogos SNIPS (§3.3, pp. 3–4). Formaliza el fenómeno de la **deriva semántica** (*semantic drift*): los errores del ASR modifican las palabras clave y desplazan las representaciones contextuales en el espacio de incrustación, alejándolas de la intención real del hablante.
- **Qué resultado reporta:**
  En la Sección 3.3, Tabla 1 (*"Performance of different methods on the SNIPS dataset"*, p. 4):
  - El clasificador BERT con fine-tuning alcanza una exactitud de **97,59%** sobre el texto manual limpio (*Clean/Manual text*), pero cae a **82,01%** sobre la transcripción reconocida por ASR (*ASR text*), lo que representa una **caída de 15,58 puntos porcentuales** atribuible directamente a los errores del transcriptor acústico.
  - El framework propuesto *Calibrate and Refine* (CR-ID) recupera la exactitud a **87,27%** (ganancia de 5,26 pp sobre el baseline de ASR), demostrando que mitigar la deriva semántica en las representaciones fonético-léxicas rescata la intención sin tener que reentrenar todo el ASR.
- **Qué limitación tiene:**
  - Evaluado sobre comandos breves de voz de un solo turno en inglés (asistente virtual), no sobre diálogos telefónicos conversacionales extensos ni en español.
- **Qué implica para este proyecto:**
  - Confirma que la arquitectura en cascada (Audio $\to$ ASR local $\to$ Detector NLP) adoptada para el prototipo móvil en Android sufre de degradación por deriva semántica en las palabras clave.
  - Justifica el protocolo de contraste pareado establecido en [`docs/evaluacion/METRICAS.md §4`](../evaluacion/METRICAS.md#4-qué-se-mide) (*"Mismo detector sobre texto manual y texto reconocido"*): evaluar el detector sobre el oráculo manual y sobre la salida del ASR local (Whisper / Sherpa-ONNX) es imprescindible para aislar la degradación debida estrictamente a los errores del transcriptor acústico frente a las fallas de la lógica de alerta.

#### 2.4.4. Prevalencia, falsas alarmas y precisión en detección de anomalías

##### S009 — Williams (2021): Desbalance de clases y curvas Precision-Recall
- **Fuente verificada:** Williams, C. K. I. (2021). *The Effect of Class Imbalance on Precision-Recall Curves*. *Neural Computation*, 33(4), 853–857. [DOI: 10.1162/neco_a_01362](https://doi.org/10.1162/neco_a_01362). Versión preprint abierta verificada: arXiv preprint [arXiv:2007.01905v3](https://arxiv.org/abs/2007.01905) [cs.LG].
- **Qué mide:** La relación analítica exacta entre la proporción de casos positivos y negativos en la población ($r = P/N = \pi / (1 - \pi)$) y el comportamiento de la precisión, la curva Precision-Recall (PR) y el puntaje $F_\beta$.
- **Cómo:** En la Sección 2 (p. 854), define la razón de prevalencia $r = P/N = \pi / (1 - \pi)$ y deriva algebraicamente la expresión exacta de la precisión como función de $r$ (Ecuación 2, p. 854):
  $$\text{Precision}(r) = \frac{r \cdot \text{TPR}}{r \cdot \text{TPR} + \text{FPR}} = \frac{\pi \cdot \text{TPR}}{\pi \cdot \text{TPR} + (1 - \pi) \cdot \text{FPR}}$$
  Demuestra que mientras la curva ROC es invariante a la razón de clases $r$, la precisión y la curva PR son extraordinariamente sensibles a $r$.
- **Qué resultado reporta:**
  En la página 854, demuestra analíticamente:
  *"Note that Prec $\to 1$ as $\pi \to 1$, and also that Prec $\to 0$ as $\pi \to 0$ if $\text{FPR} > 0$"*.
  Esto formaliza que para cualquier clasificador cuya tasa de falsas alarmas no sea idénticamente cero ($\text{FPR} > 0$), la precisión real tiende a 0 cuando la prevalencia del evento tiende a 0, sin importar cuán alto sea el recall. Asimismo, en la Sección 2 y Figura 1 (p. 855), describe cómo transformar las curvas PR obtenidas en un conjunto de prueba balanceado ($r = 1$) hacia una prevalencia operativa arbitraria ($r \ll 1$) mediante reponderación analítica.
- **Qué limitación tiene:**
  - Análisis matemático para clasificación binaria estática; no modela la evolución temporal ni el flujo continuo de audio.
- **Qué implica para este proyecto:**
  - Constituye el sustento matemático primario de la fórmula de [`docs/evaluacion/METRICAS.md §4`](../evaluacion/METRICAS.md#balance-y-precisión-de-las-alertas):
    $$\text{precision}(p) = \frac{p \times r}{p \times r + (1 - p) \times f}$$
  - Advierte que un valor de precisión o $F_1$ medido sobre un corpus de prueba balanceado (ej. 50% vishing y 50% legítimas) es ficticio y no refleja la efectividad del sistema en uso cotidiano. Dado que el vishing es un evento de baja prevalencia en telefonía ($p \le 0,01$), cualquier tasa de falsa alarma $f$ sobre llamadas legítimas destruye la precisión efectiva de las alertas.
  - Obliga a incorporar en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) un análisis de sensibilidad frente a prevalencias hipotéticas de fraude $p$.

##### S010 — Axelsson (2000): La falacia de la tasa base en sistemas de detección
- **Fuente verificada:** Axelsson, S. (2000). *The Base-Rate Fallacy and the Difficulty of Intrusion Detection*. *ACM Transactions on Information and System Security* (TISSEC), 3(3), 186–205. [DOI: 10.1145/357830.357849](https://doi.org/10.1145/357830.357849).
  > **Nota de verificación:** Texto completo bajo acceso cerrado institucional en ACM Digital Library. El análisis y las citas se restringen al resumen verificado y al desarrollo analítico formal del teorema de Bayes; los parámetros numéricos de simulación empírica quedan clasificados como **pendientes de cotejo en texto completo por acceso cerrado**.
- **Qué mide:** El impacto operativo de la falacia de la tasa base (*base-rate fallacy*) en sistemas de detección de intrusiones y anomalías de seguridad donde los incidentes son eventos raros dentro de un volumen masivo de actividad benigna.
- **Cómo:** Aplica el teorema de Bayes para cuantificar el valor predictivo positivo o probabilidad a posteriori de que una alarma indique una intrusión real:
  $$P(\text{Intrusión} \mid \text{Alerta}) = \frac{P(\text{Intrusión}) \cdot P(\text{Alerta} \mid \text{Intrusión})}{P(\text{Intrusión}) \cdot P(\text{Alerta} \mid \text{Intrusión}) + P(\neg \text{Intrusión}) \cdot P(\text{Alerta} \mid \neg \text{Intrusión})}$$
- **Qué resultado reporta:**
  En el resumen formal verificado, Axelsson formula la conclusión teórica y operativa dominante en detección de amenazas infrecuentes:
  *"This paper shows that the false alarm rate is the limiting factor for the performance of an intrusion detection system. This is due to the base-rate fallacy phenomenon, that in order to achieve substantial values of the Bayesian detection rate, $P(\text{Intrusion}\mid\text{Alarm})$, we have to achieve a perhaps 'unattainably low' false alarm rate."*
  Subraya que ante prevalencias mínimas de ataque, la tasa de falsas alarmas domina de manera aplastante el denominador bayesiano, volviendo inútil el sistema por saturación de falsas alarmas si no se reduce la tasa de error a niveles extremadamente rigurosos. (Los valores numéricos específicos de las simulaciones en el paper quedan pendientes de cotejo en texto completo).
- **Qué limitación tiene:**
  - Orientado a sistemas de auditoría y detección de intrusiones en redes e infraestructura; no estudia el canal acústico ni la interacción conversacional en telefonía móvil.
  - Texto completo no accesible abiertamente para verificación de tablas específicas de simulación.
- **Qué implica para este proyecto:**
  - Fundamenta la severidad de la métrica de falsas alarmas en [`docs/evaluacion/METRICAS.md §4`](../evaluacion/METRICAS.md#4-qué-se-mide) (*"Llamadas legítimas con al menos una alerta / total de llamadas legítimas evaluadas"*).
  - Demuestra que en un dispositivo telefónico de uso personal, donde el usuario recibe cientos de llamadas inocuas por cada llamada de fraude, una tasa de falsas alarmas no controlada destruirá la confianza y provocará la desinstalación inmediata de la defensa. Justifica fijar en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) políticas estrictas de disparo con histéresis y supresión de falsas alertas sobre llamadas legítimas comunes y negativos difíciles.

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

### Auditoría técnica de ASR local (2026-10-29, #94)

La [comparación con el código del laboratorio](../../experiments/asr-local/PLAN-VOZ-REAL.md#10-auditoría-de-vad-preaudio-y-comparación-de-modelos-2026-10-29)
registra fuentes primarias, criterios de consulta y límites de Whisper, Parakeet, Silero y
sherpa-onnx. Distingue VAD, corte RMS, preaudio y streaming simulado; no aporta una nueva
medición de voz ni acredita rendimiento móvil. La selección final sigue en
[D09](../gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

## 7. Qué cambia para la evaluación

A partir de la literatura analizada en [§2.4](#24-literatura-para-interpretar-la-evaluación-incremental-25), se formulan las siguientes cuatro propuestas metodológicas para interpretar y congelar el protocolo experimental en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), sin modificar las definiciones vigentes en [`docs/evaluacion/METRICAS.md`](../evaluacion/METRICAS.md):

1. **Adopción estricta de plazos físicos ($T_A$, $L_R$, $L_C$, $\text{Preventive}@\delta$) y descarte de penalizaciones abstractas:**
   - A diferencia de las métricas de penalización por turno (ERDE de Losada & Crestani, [S003, §2.4.1](#241-métricas-de-detección-temprana-e-incremental-erde-y-series-temporales)) o de precocidad normalizada por duración total ($\tau / T$ de Mori et al., [S004, §2.4.1](#241-métricas-de-detección-temprana-e-incremental-erde-y-series-temporales)), la evaluación de este proyecto no penaliza la duración inocua inicial ni normaliza sobre duraciones totales desconocidas.
   > **Estado: propuesta sin discutir.** En [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), adoptar como criterio primario de precocidad los márgenes físicos $L_R = T_R - T_A$ y $L_C = T_C - T_A$ y fijar los umbrales de $\text{Preventive}@\delta$ en $\delta \in \{5\,\text{s}, 10\,\text{s}\}$ basados en tiempos mínimos plausibles de reacción humana, reportando la distribución completa sin inventar un único puntaje escalar penalizado.

2. **Evaluación de ASR orientada a la tarea y enfocada en omisiones críticas:**
   - La evidencia empírica de Balagopalan et al. ([S007, §2.4.3](#243-efecto-del-error-de-asr-sobre-clasificadores-posteriores)) y Zhou et al. ([S008, §2.4.3](#243-efecto-del-error-de-asr-sobre-clasificadores-posteriores)) demuestra que el WER agregado es ciego a la severidad semántica: las eliminaciones (*deletions*) de palabras clave provocan fallas catastróficas en el clasificador posterior, mientras que sustituciones menores de relleno son tolerables.
   > **Estado: propuesta sin discutir.** Para la evaluación del impacto del ASR en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), calcular obligatoriamente el contraste pareado del detector sobre transcripción manual (oráculo) vs transcripción ASR real, reportando: (a) tasa de omisión/eliminación de términos críticos del vocabulario (`REQUEST_AUTH_CODE`, verbos de urgencia y canales de transferencia), y (b) la variación neta en $T_A$ y en los márgenes $L_R / L_C$, desaconsejando el uso exclusivo del WER global como criterio de selección del modelo acústico.

3. **Particiones disjuntas por llamante y por semilla (*caller/seed-disjoint*):**
   - El hallazgo de Traister et al. ([S006, §2.4.2](#242-detección-de-vishing-y-fraude-telefónico-sobre-transcripciones-o-en-streaming)) demostró que particiones aleatorias sobre llamadas con números o guiones repetidos sufren fuga severa de información, inflando artificialmente el rendimiento por memorización.
   > **Estado: propuesta sin discutir.** En [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), prohibir la partición aleatoria ingenua a nivel de llamada o turno. Exigir que los splits de desarrollo y evaluación sean estrictamente disjuntos tanto por semilla del catálogo de escenarios ([`CATALOGO-ESCENARIOS.csv`](../corpus/CATALOGO-ESCENARIOS.csv)) como por interlocutores/voces, asegurando que el conjunto de prueba evalúe generalización frente a formulaciones lingüísticas no vistas.

4. **Análisis obligatorio de sensibilidad a la prevalencia y contraste con "negativos difíciles":**
   - Siguiendo a Williams ([S009, §2.4.4](#244-prevalencia-falsas-alarmas-y-precisión-en-detección-de-anomalías)) y Axelsson ([S010, §2.4.4](#244-prevalencia-falsas-alarmas-y-precisión-en-detección-de-anomalías)), un clasificador evaluado en un conjunto balanceado produce una ilusión de precisión que colapsa ante la baja prevalencia real del vishing. Asimismo, Sim & Kim ([S005, §2.4.2](#242-detección-de-vishing-y-fraude-telefónico-sobre-transcripciones-o-en-streaming)) demostraron que los clasificadores colapsan (caída de 42 pp en exactitud) ante llamadas legítimas que mencionan trámites de seguridad o bancos.
   > **Estado: propuesta sin discutir.** En [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), prohibir la presentación del $F_1$ o precisión sobre el corpus experimental como estimación de rendimiento en producción. Reportar obligatoriamente: (a) curvas de sensibilidad de la precisión analítica $\text{precision}(p)$ para $p \in [0{,}001;\, 0{,}05]$ según la formulación de Williams, y (b) la tasa de falsas alarmas desglosada entre llamadas legítimas cotidianas neutras y negativos difíciles con vocabulario bancario/seguridad.
