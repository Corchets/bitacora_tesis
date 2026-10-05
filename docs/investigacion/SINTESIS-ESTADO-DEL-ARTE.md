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
