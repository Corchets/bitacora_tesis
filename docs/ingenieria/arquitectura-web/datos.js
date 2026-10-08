/* ============================================================================
 * datos.js — Contenido de la visualización de arquitectura.
 *
 * Fuente de cada bloque (rutas relativas a docs/ingenieria/arquitectura-web/):
 *   - ../ARQUITECTURA.md
 *   - ../gestion/MAPA-DECISIONES.md
 *   - ../investigacion/DISENO-INTEGRADO.md
 *   - ../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md
 *   - ../investigacion/PRIMERA-INVESTIGACION-MODELOS.md
 *   - ../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md
 *   - ../investigacion/ESTRATEGIA-MODELOS-NLP-Y-COMPRESION.md
 *   - ../investigacion/PREFACTIBILIDAD-TECNICA.md
 *   - ../evaluacion/METRICAS.md
 *   - ../datos-etica/MANUAL-ANOTACION.md
 *   - ../datos-etica/PRIVACIDAD-DEL-SISTEMA.md
 *   - ../../../experiments/laboratorio/  (código Python del spike #29)
 *
 * REGLA: nada de esto inventa decisiones. Cada entrada conserva el estado que
 * tiene en MAPA-DECISIONES.md. Lo que es propuesta sin discutir se marca.
 * ==========================================================================*/

window.DATOS = {

  meta: {
    titulo: "Arquitectura incremental de detección de vishing",
    subtitulo: "Motor on-device en español rioplatense — visualización del estado del proyecto",
    fecha: "2026-10-07",
    notaEstado: "La arquitectura v0 es propuesta sin discutir (issue #20). No cierra D07, D08, D09 ni D11."
  },

  /* ------------------------------------------------------------------------
   * DECISIONES — texto completo para el panel/modal al hacer clic en un chip D0x
   * estado: "resuelto" | "parcial" | "abierto" | "propuesta"
   * ----------------------------------------------------------------------*/
  decisiones: [
    {
      id: "D01",
      titulo: "Completar el contrato académico",
      estado: "resuelto",
      pregunta: "¿Qué fecha exacta, plantilla, estilo bibliográfico, entregables adicionales y proceso ético aplican al grupo?",
      detalle: "Resuelto el 2026-09-09 (minuta con el tutor). Defensa presencial a fines de diciembre de 2026; tutor asignado (Ing. Ernesto Rico); entrega digital ~100 páginas como referencia; no hay comité de ética universitario formal.",
      desbloquea: "D02, D03, D10 y el cronograma definitivo.",
      evidencia: ["docs/gestion/seguimientos/2026-09-09.md", "docs/propuesta/REQUISITOS-ACADEMICOS.md"],
      comoSeguir: "Sin acción técnica pendiente; alimenta el checklist de entrega (D10)."
    },
    {
      id: "D02",
      titulo: "Definir problema, usuario y necesidad",
      estado: "parcial",
      pregunta: "¿Quién necesita qué decisión o protección, en qué momento de la llamada y frente a qué daño?",
      detalle: "Ratificada por el equipo (los cuatro aprobaron las cinco líneas del Plan de Trabajo §2, producidas en el issue #18), pendiente de la respuesta del tutor registrada en el seguimiento del 2026-09-30. El foco en adultos mayores sigue en D12.",
      desbloquea: "D06 y requisitos.",
      evidencia: ["docs/propuesta/PLAN-DE-TRABAJO.md", "docs/gestion/seguimientos/2026-09-30.md"],
      comoSeguir: "Esperar ratificación del tutor; si cambia el encuadre, revisar presentación y corpus."
    },
    {
      id: "D03",
      titulo: "Congelar alcance y contribución",
      estado: "resuelto",
      pregunta: "¿Cuál es el núcleo obligatorio, cuáles son los stretch goals y qué queda fuera de alcance?",
      detalle: "Resuelto el 2026-09-09. Núcleo obligatorio y exclusiones aprobados: no PSTN, no deepfakes, no biometría. La contribución defendible es la arquitectura incremental documentada (capas 3 y 4 del diseño integrado), el hueco que deja la patente de Google.",
      evidencia: ["docs/propuesta/PLAN-DE-TRABAJO.md", "docs/investigacion/DISENO-INTEGRADO.md"],
      comoSeguir: "Toda nueva funcionalidad se contrasta contra la lista de exclusiones."
    },
    {
      id: "D04",
      titulo: "Aprobar preguntas e hipótesis",
      estado: "resuelto",
      pregunta: "¿Qué afirmaciones se evaluarán y qué observación podría refutarlas?",
      detalle: "Resuelto el 2026-09-09, aprobadas por el tutor sin objeciones. PI1–PI2 aprobadas; evaluación E1 diagnóstica y E2 secundaria. Candidata nueva: agregar «cuánto contexto mira el detector» como eje de PI1 (VENTANA §9).",
      evidencia: ["docs/investigacion/PREGUNTAS-DE-INVESTIGACION.md"],
      comoSeguir: "Discutir entre los cuatro el eje de ventana en PI1."
    },
    {
      id: "D05",
      titulo: "Elegir la fuente de audio demostrable",
      estado: "resuelto",
      pregunta: "¿Cuál es la integración objetivo entre replay en streaming, VoIP controlado y micrófono/altavoz de laboratorio?",
      detalle: "Resuelto el 2026-09-09. Replay como base experimental reproducible obligatoria; llamada VoIP propia como integración objetivo del prototipo; altavoz externo despriorizado (mezcla canales); PSTN universal fuera de alcance confirmado.",
      evidencia: ["docs/ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md", "docs/gestion/seguimientos/2026-09-09.md"],
      comoSeguir: "Construir el entorno de pruebas VoIP (conversaciones simuladas por canal) — paso 0 de VENTANA §10."
    },
    {
      id: "D06",
      titulo: "Definir la gobernanza de datos",
      estado: "parcial",
      pregunta: "¿Qué se grabará, con qué consentimiento, dónde vivirá, quién accederá, qué podrá publicarse y cuándo se eliminará?",
      detalle: "En curso. Acordado el 2026-09-24: primera pasada de 14 conversaciones con hasta 6 repeticiones dirigidas, participantes adultos con datos ficticios, consentimiento de ambos interlocutores, custodio operativo Mateo, resguardo local cifrado, sin permiso de publicar voces. PR #35 documenta la decisión operativa pero NO habilita grabaciones: falta validación del tutor y completar domicilio/contacto reales fuera de Git.",
      desbloquea: "Corpus piloto (issue #39, bloqueado hasta #22 + validación del tutor).",
      evidencia: ["docs/datos-etica/METODO-CREACION-CORPUS.md", "docs/datos-etica/CONSENTIMIENTO-INFORMADO.md", "docs/datos-etica/CATALOGO-ESCENARIOS.csv"],
      comoSeguir: "Llevar composición, participantes y protocolo al tutor; sin su validación no se graba."
    },
    {
      id: "D07",
      titulo: "Aprobar taxonomía y evento crítico",
      estado: "abierto",
      pregunta: "¿Qué maniobras y pedidos se anotan, y cómo se marcan T_R y T_C?",
      detalle: "Abierta con acuerdos parciales. Propuesta de dos capas multi-label de 6 etiquetas cada una (MANUAL-ANOTACION.md); principio: no superar la docena de etiquetas. Mateo aprobó el 2026-09-23 usar AUTHORITY_CLAIM en lugar de IMPERSONATION_AUTHORITY. Acuerdo del 2026-10-02 (Luciano): selección 6+6, incluir menciones de códigos en REQUEST_AUTH_CODE, T_C como referencia principal de Preventive@δ reportando ambos márgenes. Falta: probar la taxonomía completa con el piloto, adjudicar ambigüedades, fijar marcas temporales operativas y el tratamiento de llamadas sin cumplimiento. T_A se define con histéresis (primer cruce que se sostiene dos actualizaciones).",
      bloqueadaPor: "D02, D04 y D06.",
      evidencia: ["docs/datos-etica/MANUAL-ANOTACION.md", "docs/evaluacion/METRICAS.md", "docs/datos-etica/CATALOGO-ESCENARIOS.csv"],
      comoSeguir: "Anotar el piloto con las 6+6, medir acuerdo entre anotadores, completar el esqueleto §4 del manual (reglas por etiqueta, casos límite, marcado temporal)."
    },
    {
      id: "D08",
      titulo: "Congelar protocolo experimental",
      estado: "abierto",
      pregunta: "¿Cómo se muestrea, divide y evalúa sin fuga de información?",
      detalle: "Abierta. Define la credibilidad de los resultados: si dos variantes del mismo guion caen una en train y otra en test, el modelo ya vio el escenario. Falta fijar ANTES de medir: la restricción de falsos positivos (método propuesto en VENTANA §7.1: se fija el máximo de llamadas legítimas con alerta y se deriva el acierto requerido por revisión), la regla de persistencia del contador (opciones A/B/C en VENTANA §11), el reloj de actualización, el conteo de alertas y las franjas de duración. El modelo de estado temporal (ventana con decaimiento, registro de eventos, doble umbral) sigue siendo propuesta sin discutir.",
      bloqueadaPor: "D04 y D07.",
      evidencia: ["docs/datos-etica/METODO-CREACION-CORPUS.md", "docs/evaluacion/METRICAS.md", "docs/investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md"],
      comoSeguir: "Decidir la regla de persistencia (2 seguidas vs 2 de los últimos 3 vs escalera completa), fijar el presupuesto de falsas alarmas y correr los dos brazos (base vs propuesta) del experimento de DISENO-INTEGRADO §5."
    },
    {
      id: "D09",
      titulo: "Elegir ASR y detector",
      estado: "abierto",
      pregunta: "¿Qué combinación satisface la calidad y el presupuesto de cómputo?",
      detalle: "Abierta. Recorte de trabajo vigente (propuesta sin discutir): ASR = Moonshine tiny-es en gama baja, Zipformer Kroko ONNX en media/alta; detector = LLM/SLM local (candidato Llama-3.2-1B-Instruct, modos clasificador|agente|base). La cascada encoder→SLM (RoBERTuito + LR, zona gris 0,35–0,75) se midió el 2026-09-28 y NO mejoró al encoder solo (goteo 12/16→7/16, AUROC 0,666→0,537, mismas 5/10 falsas alarmas); tampoco entra en 1024 MB de RAM junto al SLM (~1,7 GB sin ASR). TF-IDF eliminado del proyecto (2026-09-29): la línea base son las reglas solas. Todo lo medido es con semillas provisorias — sesgo de dialecto (R16) — así que ninguna cifra cierra D09.",
      bloqueadaPor: "D05, D07 y benchmark piloto.",
      evidencia: ["docs/investigacion/PRIMERA-INVESTIGACION-MODELOS.md", "docs/investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md", "docs/investigacion/ESTRATEGIA-MODELOS-NLP-Y-COMPRESION.md"],
      comoSeguir: "En orden (CONTRASTE §9): 1) datos reales para el encoder (#41); 2) cambiar/duplicar la regla de alerta; 3) medir RoBERTuito INT8/ONNX vs fp32; 4) probar SmolLM2-360M y prompt corto en zona gris, o sacar el SLM si sigue sin aportar; 5) cascada con audio (#42)."
    },
    {
      id: "D10",
      titulo: "Congelar estructura de entrega y defensa",
      estado: "abierto",
      pregunta: "¿Qué índice, anexos, paquete reproducible, duración y demo se entregan?",
      detalle: "Abierta. Depende de D01 y de los resultados de evaluación. Incluye el diseño exacto del warning y el método de evaluación con usuarios (no especificado todavía).",
      bloqueadaPor: "D01 y resultados de evaluación.",
      evidencia: ["docs/propuesta/REQUISITOS-ACADEMICOS.md", "docs/tesis/ESQUELETO-INFORME.md"],
      comoSeguir: "Definir la demo (replay/VoIP) y la prueba de comprensión de avisos con personas."
    },
    {
      id: "D11",
      titulo: "Análisis lingüístico o también acústico",
      estado: "abierto",
      pregunta: "¿El detector trabaja solo sobre la transcripción del ASR, o también sobre rasgos bioacústicos (tono, estrés vocal, MFCCs)?",
      detalle: "Abierta. Recomendación del deep research: solo NLP sobre la transcripción, con lo bioacústico como trabajo futuro declarado en las conclusiones. D05 ya descartó el altavoz como camino principal.",
      evidencia: ["docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md"],
      comoSeguir: "Ratificar entre los cuatro «solo transcripción» para acotar el pipeline."
    },
    {
      id: "D12",
      titulo: "Encuadre del foco en adultos mayores",
      estado: "parcial",
      pregunta: "¿Se mantiene el foco en adultos mayores y con qué justificación?",
      detalle: "El deep research no pide abandonar el foco, pide cambiar la justificación: de «son los más afectados» (no demostrado para Argentina) a «gravedad potencial de las pérdidas y exposición a estafas de suplantación». No convertir el reclutamiento de adultos mayores en bloqueo del corpus: mejor incluirlos en evaluación y prueba de usabilidad. Ya integrado en el Plan de Trabajo.",
      bloqueadaPor: "D02.",
      evidencia: ["docs/propuesta/PLAN-DE-TRABAJO.md"],
      comoSeguir: "Usar adultos mayores en la prueba de usabilidad de avisos, no como requisito del corpus."
    },
    {
      id: "D13",
      titulo: "Título definitivo",
      estado: "abierto",
      pregunta: "¿Cuál es el título final de la tesis?",
      detalle: "Regla: no cerrarlo antes de tener el corpus. Un título que promete «español argentino» obliga a un corpus que lo sostenga.",
      bloqueadaPor: "D03 y la composición geográfica real del corpus.",
      comoSeguir: "Definir al conocer la cobertura real del corpus."
    }
  ],

  /* Decisiones emergentes del issue #23 (VENTANA §9) — candidatas, ninguna tomada */
  decisionesEmergentes: [
    { id: "E-REG", pregunta: "¿Se adopta el registro conjunto atacante/víctima como estructura central?", relacion: "Arquitectura · nueva" },
    { id: "E-CT", pregunta: "Forma de C_t: ¿graduado con precursores? ¿Qué niveles?", relacion: "PI2 · nueva" },
    { id: "E-FORM", pregunta: "Fórmula de acoplamiento: ¿σ(a·M + b·C + c·M·C + sesgo) en lugar de C·σ(M)?", relacion: "PI2 · nueva" },
    { id: "E-HIST", pregunta: "Histéresis: ¿persistencia de 2 actualizaciones, doble umbral o ambos?", relacion: "METRICAS.md · nueva" },
    { id: "E-RELOJ", pregunta: "Reloj de actualización: ¿cada cuántos segundos, contra qué presupuesto de falsas alarmas?", relacion: "D08 · nueva" },
    { id: "E-FP", pregunta: "Restricción de falsos positivos: ¿qué % máximo de llamadas legítimas con alerta se tolera?", relacion: "D08 · existente" },
    { id: "E-CONTEO", pregunta: "¿Una alerta que se apaga y vuelve a prender cuenta una o dos veces?", relacion: "METRICAS.md · nueva" },
    { id: "E-MEM", pregunta: "Memoria del registro: ¿decaimiento por tipo de evento? ¿Con qué ritmos?", relacion: "Arquitectura · nueva" },
    { id: "E-VICTIMA", pregunta: "Eventos de la víctima: ¿resistencia al modelo y cumplimiento solo como marca y freno aparte?", relacion: "D07 · nueva" },
    { id: "E-FRANJAS", pregunta: "¿Qué franjas de duración se reportan y qué peso tienen las llamadas cortas?", relacion: "D08 · nueva" },
    { id: "E-EJE", pregunta: "¿Se agrega «cuánto contexto mira el detector» como variable del experimento (PI1)?", relacion: "D04 · nueva" },
    { id: "E-PERS", pregunta: "Persistencia del contador de goteo: ¿dos seguidas, 2 de los últimos 3, o el diseño completo?", relacion: "#28/#29 · nueva" },
    { id: "E-RESUMEN", pregunta: "¿Se descarta el resumen generativo a favor del registro de eventos?", relacion: "Arquitectura · nueva" }
  ],

  /* ------------------------------------------------------------------------
   * COMPONENTES del pipeline. versiones: en qué diagramas aparece el nodo.
   * ----------------------------------------------------------------------*/
  componentes: [
    {
      id: "fuente-replay",
      nombre: "Replay de audio",
      capa: "fuente",
      versiones: ["slm", "cascada"],
      resumen: "Base experimental obligatoria (D05): WAV reproducido como stream. Reproducible, con commit y seed.",
      entrada: "Archivo WAV 16 kHz mono 16-bit (fuera de Git)",
      salida: "Fragmentos de audio en orden temporal",
      restriccion: "El motor no sabe de dónde viene el audio: replay y VoIP entran por el mismo contrato.",
      archivos: [
        { path: "experiments/laboratorio/pipeline.py", nota: "leer_wav_mono_16k() exige WAV 16kHz mono; correr() lo corta en pedazos de chunk_ms=300 sin sleep (RTF = cómputo/duración)" }
      ],
      decisiones: ["D05"],
      recomendacion: "Mantener el replay como base de TODA medición: es lo que hace reproducible el experimento.",
      comoProbar: "Correr la suite de casos/ en modo texto y en modo audio (#42).",
      estado: "propuesta"
    },
    {
      id: "fuente-voip",
      nombre: "VoIP propia",
      capa: "fuente",
      versiones: ["slm", "cascada"],
      resumen: "Integración objetivo del prototipo (D05): la app es el cliente de la llamada; cada hablante llega por su canal.",
      entrada: "Llamada VoIP consentida",
      salida: "Fragmentos de audio por canal (atacante / víctima separados)",
      restriccion: "Elimina la diarización del pipeline — ventaja clave frente a altavoz/micrófono. Requiere consentimiento de ambos interlocutores (D06).",
      archivos: [],
      decisiones: ["D05", "D06"],
      recomendacion: "Entorno de pruebas VoIP con dos roles grabados por canal: es lo que convierte la ventana de contexto en evidencia (VENTANA §10 paso 0).",
      comoProbar: "Construir el entorno de llamadas simuladas; PSTN universal queda fuera de alcance.",
      estado: "propuesta"
    },
    {
      id: "adaptador",
      nombre: "Adaptador de audio",
      capa: "entrada",
      versiones: ["slm", "cascada"],
      resumen: "Entrega fragmentos en orden temporal desde la fuente permitida: audio + tiempo relativo a la sesión + canal si se conoce.",
      entrada: "Sesión de replay o VoIP",
      salida: "audio, tiempo relativo, canal",
      restriccion: "El motor no depende de permisos de captura PSTN ni infiere quién habla cuando la fuente no separa canales.",
      archivos: [
        { path: "experiments/laboratorio/pipeline.py", nota: "correr(): bucle de pedazos de 300 ms con t_s = posición/16000; mide t_computo para el RTF" }
      ],
      decisiones: ["D05"],
      recomendacion: "Contrato mínimo ya correcto: fragmentos + timestamp. No agregar lógica acá.",
      comoProbar: "Ya corre en el spike; falta el caso VoIP real.",
      estado: "propuesta"
    },
    {
      id: "vad",
      nombre: "VAD / segmentación",
      capa: "entrada",
      versiones: ["slm", "cascada"],
      resumen: "Identifica tramos de voz y arma unidades aptas para el ASR. En el lab: corta el turno tras 400 ms de silencio (RMS < 0,02).",
      entrada: "Fragmentos de audio",
      salida: "Tramos con inicio y fin",
      restriccion: "No perder la referencia temporal ni convertir silencio en texto. El cortador del spike NO es un VAD de tesis: son umbrales de spike, no decisiones congeladas.",
      archivos: [
        { path: "experiments/laboratorio/turns.py", nota: "CortadorTurnos: RMS ≥ 0,02 = voz; 400 ms de silencio cierran el turno" },
        { path: "experiments/laboratorio/asr.py", nota: "enable_endpoint_detection=False: el turno lo cierra el silencio, no el ASR" }
      ],
      decisiones: ["D08"],
      recomendacion: "El fin de turno define cuándo piensa el detector: medir sensibilidad a 400 vs 600 ms (H11 sin probar).",
      comoProbar: "Barrido de silencio_ms sobre las grabaciones; hoy las transcripciones se partieron en bloques fijos de 25 palabras porque el cortador no está definido (dificultad 6 del contraste).",
      estado: "propuesta"
    },
    {
      id: "asr",
      nombre: "ASR local (el que escribe)",
      capa: "modelo",
      versiones: ["slm", "cascada"],
      resumen: "Transcribe en streaming: texto parcial (borrador) o final con intervalo temporal. Streaming obligatorio: hay que avisar ANTES de que la víctima pase el código.",
      entrada: "Tramos de voz",
      salida: "texto parcial o final + intervalo temporal",
      restriccion: "Los parciales pueden corregirse; una palabra reconocida no es evidencia infalible. Whisper por pedazos NO va como ASR (rompe el streaming): solo para comparación de calidad.",
      archivos: [
        { path: "experiments/laboratorio/asr.py", nota: "descargar_modelo() del Hub + crear_reconocedor() sherpa_onnx.OnlineRecognizer.from_transducer (16kHz, greedy_search, CPU); alimentar() devuelve el borrador del turno" },
        { path: "experiments/laboratorio/gamas.json", nota: "asr por gama: moonshine-streaming-tiny-es (baja) / sherpa-onnx-streaming-zipformer-es-kroko (media y alta)" }
      ],
      decisiones: ["D09"],
      recomendacion: "Zipformer Kroko corre hoy en gama alta; Moonshine tiny-es quedó solo como id (no implementado) para baja.",
      comoProbar: "Medir WER y recall de términos críticos sobre llamadas argentinas reales (ninguna ficha mide vishing rioplatense — riesgo R06). Corrida de audio del 2026-09-25: RTF 0,16–0,72 con TF-IDF, falta con encoder/cascada (#42).",
      estado: "propuesta"
    },
    {
      id: "estado",
      nombre: "Estado conversacional",
      capa: "memoria",
      versiones: ["slm", "cascada"],
      resumen: "Mantiene turnos, contexto y la última revisión válida de cada tramo. En la propuesta: registro de eventos e_k = (k, τ, ρ, γ, c) que solo crece — hechos tipados con tiempo y rol, no texto.",
      entrada: "Transcripciones y revisiones",
      salida: "Estado temporal consultable",
      restriccion: "Reemplazar un parcial por su revisión final sin duplicar evidencia; descartar contenido al terminar (PRIVACIDAD). El registro de eventos cuesta ~0 tokens y puede durar la llamada entera.",
      archivos: [
        { path: "experiments/laboratorio/pipeline.py", nota: "historial: lista de turnos cerrados que se pasa al detector (últimos 5–8 según modo). El registro de eventos con decaimiento NO está implementado: es propuesta del #23" }
      ],
      decisiones: ["D08", "D07"],
      recomendacion: "El registro conjunto atacante/víctima es el aporte propio: separa estafa de llamada legítima con los mismos marcadores (δ). La víctima registra RESISTENCIA (entra al score) y CUMPLIMIENTO (solo marca T_C, nunca alimenta el score).",
      comoProbar: "Implementar como segundo brazo del experimento (DISENO-INTEGRADO §5): mismo pipeline, solo cambia la política de decisión.",
      estado: "propuesta",
      detalleExtra: "Indicadores propuestos sobre el registro: κ = fases del guion presentes/5 · Ω = pares de eventos en orden (suavizado m=3) · δ = resistencias respondidas con presión. Decaimiento por vida media por tipo: URGENCIA 60 s, AISLAMIENTO 180 s, SUPLANTACION 600 s (valores iniciales, a calibrar en validación)."
    },
    {
      id: "reglas",
      nombre: "Reglas de incendio (capa 2)",
      capa: "reglas",
      versiones: ["slm", "cascada"],
      resumen: "Miran el borrador del ASR (cada 300 ms) y disparan el aviso más fuerte ante un pedido peligroso explícito — sin esperar histéresis ni fin de turno.",
      entrada: "Texto a medias del ASR (borrador)",
      salida: "Etiquetas REQUEST_* tipadas → nivel «pedido crítico»",
      restriccion: "Son la LÍNEA BASE del detector desde el 2026-09-29 (TF-IDF eliminado). Cada falso positivo de regla es una alerta sin histéresis (R14: puede inflar Preventive@δ — se reporta por separado).",
      archivos: [
        { path: "experiments/laboratorio/rules.py", nota: "incendio_en(): PATRONES por 6 etiquetas capa 2; tolera 1 typo en patrones ≥6 letras (_edicion1, Damerau); _niega_el_pedido() respeta negaciones salvo imperativo; _SOLO_EXACTO={'numeros'} por el falso amigo «numero»" },
        { path: "experiments/laboratorio/pipeline.py", nota: "las reglas corren sobre el borrador en cada chunk de 300 ms" }
      ],
      decisiones: ["D07"],
      recomendacion: "Confirmada como vía rápida con límites (incendio 13/16): fallan los casos difíciles sin palabra clave (dígitos, pantalla, giro) y hay un incendio falso con «código de la puerta». Escribirlas contra la columna «qué no la dispara» del manual de anotación (#17). Sumar reglas de maniobras (autoridad, urgencia, aislamiento) para que la capa 3 tenga qué recordar.",
      comoProbar: "casos/ + chequear_casos.py: 21 guiones + 5 difíciles con oracle (typos, mayúsculas, tildes, muletillas, negaciones).",
      estado: "vigente"
    },
    {
      id: "detector",
      nombre: "Detector de goteo (el que lee)",
      capa: "modelo",
      versiones: ["slm", "cascada"],
      resumen: "Puntaje de estafa 0–1 por turno cerrado. Piensa al cerrar la frase, no en cada sílaba: en gama baja se pelearía con el ASR.",
      entrada: "Turno cerrado (+ historial según modo)",
      salida: "puntaje 0–1 o «sin opinión» (None)",
      restriccion: "No presentar un puntaje sin calibración como probabilidad de fraude; la taxonomía y el modelo siguen abiertos (D09). Turno «sin opinión»: no entra en la ventana ni sostiene ni corta la racha de T_A.",
      archivos: [
        { path: "experiments/laboratorio/detector.py", nota: "DetectorLlm: SLM por API OpenAI-compatible (LLM_BASE_URL, Ollama). Modos: clasificador (últimos 5 turnos → {\"riesgo\":0..1}), agente (checklist de etiquetas + riesgo), base (base institucional offline del #27 en el system prompt). response_format json_object obligatorio: sin eso el Q4 contesta prosa. Sin server → sin opinión." },
        { path: "experiments/laboratorio/detector.py", nota: "crear() lee env DETECTOR=llm|encoder|cascada" }
      ],
      decisiones: ["D09", "D11"],
      recomendacion: "Candidato de arranque: meta-llama/Llama-3.2-1B-Instruct (Ollama llama3.2:1b-instruct-q4_K_M, contexto 1024). Medido: ~3,9 s/turno y ~860 MB de RAM en PC x86 — 5× lo supuesto. SmolLM2-360M sin medir es la alternativa liviana.",
      comoProbar: "Medir clasificador vs agente vs base (#27/#29). Sin datos reales (#41) ninguna comparación de calidad sirve.",
      estado: "propuesta"
    },
    {
      id: "encoder",
      nombre: "Encoder (capa rápida)",
      capa: "modelo",
      versiones: ["cascada"],
      resumen: "RoBERTuito congelado + regresión logística: puntúa CADA turno barato. Solo existe en la versión encoder+SLM.",
      entrada: "Turno cerrado",
      salida: "puntaje 0–1 (predict_proba de la LR)",
      restriccion: "El encoder no clasifica vishing de fábrica: embebe semillas.json y la LR (seed 42) pone el número. Con semillas provisorias aprende dialecto/forma, no maniobras (R16).",
      archivos: [
        { path: "experiments/laboratorio/detector_encoder.py", nota: "DetectorEncoder: AutoModel congelado fp32, mean-pooling con attention_mask, max_length=128, LogisticRegression(random_state=42). Entrena su cabeza con SEMILLAS_PATH al construirse." },
        { path: "experiments/laboratorio/armar_semillas.py", nota: "semillas: turnos del estafador de 8 grabaciones argentinas de YouTube + turnos legítimos + 70 de ES-Port; al repo va solo el manifiesto (voces de terceros fuera de Git)" }
      ],
      decisiones: ["D09"],
      recomendacion: "Medido fp32: ~152 ms p50/turno, ~875 MB RAM pico (incluye PyTorch+transformers). El marco #27 suponía INT8/ONNX: 38–42 ms y 145 MB — sin probar todavía.",
      comoProbar: "Cuantizar a INT8/ONNX y medir en ARM; con 24 frases los 4 encoders dan alerta en todo (16/16 y 10/10).",
      estado: "propuesta"
    },
    {
      id: "cascada",
      nombre: "Zona gris → SLM",
      capa: "modelo",
      versiones: ["cascada"],
      resumen: "Si el puntaje del encoder cae en [0,35; 0,75] se consulta al SLM y su riesgo REEMPLAZA al del encoder; si el SLM no contesta, queda el del encoder.",
      entrada: "puntaje del encoder + turno + historial",
      salida: "puntaje final del turno",
      restriccion: "θ 0,35/0,75 son el ejemplo del #27, no umbrales calibrados (H9). En la corrida del 2026-09-28 el 24% de los turnos (126/523) fueron a zona gris: el costo del SLM no es marginal.",
      archivos: [
        { path: "experiments/laboratorio/detector_cascada.py", nota: "DetectorCascada: theta_low=0.35, theta_high=0.75; registra n_zona_gris, ms por capa y slm_mem_mb" },
        { path: "experiments/laboratorio/docker-compose.yml", nota: "servicio `slm`: Ollama llama3.2:1b-instruct-q4_K_M, contexto 1024" }
      ],
      decisiones: ["D09"],
      recomendacion: "En esta corrida la cascada EMPEORÓ al encoder solo (goteo 12/16→7/16; AUROC 0,666→0,537). Llama 1B sin ajuste responde riesgo 0 a casi todo y la base institucional no salvó la suplantación de ANSES (H5 refutada). La idea no queda descartada: depende de datos (#41).",
      comoProbar: "Re-correr con datos reales; probar SmolLM2-360M o sacar el SLM de la cascada si sigue sin aportar (CONTRASTE §9).",
      estado: "propuesta"
    },
    {
      id: "contador",
      nombre: "Memoria y persistencia",
      capa: "memoria",
      versiones: ["slm", "cascada"],
      resumen: "HOY: ContadorGoteo — máximo de los últimos 3 puntajes con opinión; dispara si se mantiene alto dos turnos. PROPUESTO: registro de eventos con decaimiento + doble umbral.",
      entrada: "Puntajes por turno (o eventos tipados)",
      salida: "¿El riesgo se sostiene?",
      restriccion: "DEFECTO DEMOSTRADO (VENTANA §11): un solo pico deja el máximo alto 3 turnos → «alto dos veces» se cumple solo. Al 99% de acierto por revisión deja 54,8% de llamadas legítimas con alerta ≈ sin regla. El spike implementa el recorte al pie de la letra: el problema es la regla, no el código.",
      archivos: [
        { path: "experiments/laboratorio/pipeline.py", nota: "ContadorGoteo.agregar(): None=sin opinión (no entra ni sostiene); alto = max(últimos 3) ≥ umbral(0,5); dispara si alto y prev_alto" }
      ],
      decisiones: ["D08"],
      recomendacion: "Arreglo inmediato — opción B «2 de los últimos 3»: conserva la ventana, baja a 1,5% (vs 0,8% de «dos seguidas puras» y 54,8% del máximo). Propuesta de fondo — opción C: S_t con κ/Ω/δ, decaimiento y doble umbral.",
      comoProbar: "Correr las dos variantes para separar el efecto de la regla del efecto del detector (recomendación CONTRASTE §6, decide D08/#33).",
      estado: "propuesta"
    },
    {
      id: "alerta",
      nombre: "Política de alerta",
      capa: "decision",
      versiones: ["slm", "cascada"],
      resumen: "Escalera de tres niveles: moderado (zona dudosa sostenida, con histéresis) → alto (S_t ≥ θ_high dos actualizaciones) → pedido crítico (regla confirma, SIN histéresis, en el momento del pedido = T_R).",
      entrada: "Puntaje + evidencia + tiempo",
      salida: "nivel, motivo y T_A si hay alerta estable",
      restriccion: "Un aviso por nivel por llamada, solo se escala. NO hay corte automático (un falso positivo cortaría una llamada legítima; Google tampoco lo implementó). Los avisos por pedido crítico y por riesgo sostenido se reportan por separado.",
      archivos: [
        { path: "experiments/laboratorio/pipeline.py", nota: "t_incendio = primer evento de reglas; t_goteo = primer disparo del contador; latencia_decision = min(ambos)" }
      ],
      decisiones: ["D07", "D08"],
      recomendacion: "θ_high ≈ 0,75 / θ_low ≈ 0,40 son valores iniciales a calibrar (sin justificación en el informe). El encendido combina «dos actualizaciones» (METRICAS) con doble umbral (Schmitt). Reloj de actualización independiente de los eventos: si solo se actualiza con eventos, «dos actualizaciones» pueden ser dos minutos.",
      comoProbar: "Fijar presupuesto de falsas alarmas ANTES de medir y derivar cadencia/umbrales (VENTANA §7.1).",
      estado: "propuesta"
    },
    {
      id: "presentacion",
      nombre: "Presentación",
      capa: "salida",
      versiones: ["slm", "cascada"],
      resumen: "Aviso comprensible que permite actuar durante la conversación: título, motivo, consecuencia y acción. El signo «!» y el nombre del nivel comunican gravedad sin depender solo del color.",
      entrada: "Evento de alerta",
      salida: "título + motivo + qué hacer",
      restriccion: "No afirmar que la llamada ES una estafa ni prometer cortar/bloquear si la integración no lo hace. Ningún aviso reproduce un código, una clave ni un fragmento literal de la conversación. «Entendido» solo cierra el aviso, no la llamada.",
      archivos: [],
      decisiones: ["D10", "D12", "D02"],
      recomendacion: "Dos mockups propuestos: moderado «Revisá esta llamada» y alto «No compartas el código». Probar comprensión, accesibilidad en pantalla chica y comportamiento ante alerta errónea con personas (incluir adultos mayores en la prueba de usabilidad, D12).",
      comoProbar: "Diseño de UI abierto: prueba de comprensión con usuarios pendiente.",
      estado: "propuesta"
    },
    {
      id: "salida",
      nombre: "Salida y evaluación",
      capa: "salida",
      versiones: ["slm", "cascada"],
      resumen: "JSON/CSV por corrida: T_R (primer incendio), T_A (goteo), RTF, memoria pico, puntajes por turno, términos críticos recuperados y stats de la cascada.",
      entrada: "Todos los eventos de la corrida",
      salida: "CSV en resultados/AAAA-MM-DD/ + glosario de columnas",
      restriccion: "Cada corrida registra commit, seed, config y hardware. El registro mínimo vive fuera del contenido: sin audio ni transcripciones en el persistente (PRIVACIDAD).",
      archivos: [
        { path: "experiments/laboratorio/correr_encoders.py", nota: "corre la suite por detector y escribe un CSV por corrida" },
        { path: "experiments/laboratorio/resultados/GLOSARIO-COLUMNAS.md", nota: "glosario de cada columna de los CSV" },
        { path: "experiments/laboratorio/chequear_casos.py", nota: "oracle: falla si el incendio no da lo esperado por caso" }
      ],
      decisiones: ["D08", "D04"],
      recomendacion: "Reportar Preventive@5/10/20s (referencia T_C), mediana de L_R y L_C, % de legítimas con alerta, falsas alertas/hora, macro-F1 de maniobras, curva de evolución 25/50/75/100%.",
      comoProbar: "El primer gráfico a producir: riesgo vs tiempo con T_A/T_R/T_C superpuestos (ver página del simulador).",
      estado: "vigente"
    }
  ],

  /* ------------------------------------------------------------------------
   * VERSIONES del detector — el toggle principal del diagrama
   * ----------------------------------------------------------------------*/
  versiones: {
    slm: {
      id: "slm",
      nombre: "SLM solo",
      lema: "El SLM puntúa cada turno directamente",
      descripcion: "DETECTOR=llm → DetectorLlm por API local (Ollama). Un solo modelo generativo decide el puntaje de goteo en cada turno cerrado; las reglas siguen siendo la vía de incendio.",
      flujo: "turno cerrado → SLM (clasificador|agente|base) → puntaje 0–1 → ContadorGoteo",
      mediciones: [
        "Llama 3.2 1B Q4_K_M: ~3.884 ms p50/turno (el marco suponía 450–850 ms) y ~860 MB RAM (Ollama /api/ps)",
        "Contexto recortado a 1024 tokens; turnos del historial a 300 caracteres (con 4096 reservaba ~1,4 GB)",
        "Sin response_format JSON contesta en prosa → turno sin opinión",
        "Modo agente (checklist de etiquetas) a medir en #27/#29"
      ],
      lectura: "Entra de a uno en cada gama; el costo es fijo por turno. Sin ajuste, responde riesgo 0 a casi todo: la calidad depende del prompt/datos, no solo del modelo."
    },
    cascada: {
      id: "cascada",
      nombre: "Encoder + SLM (cascada)",
      lema: "Encoder barato en cada turno; el SLM solo en la zona gris",
      descripcion: "DETECTOR=cascada → DetectorCascada: RoBERTuito + LR puntúa cada turno; si el puntaje cae en [0,35; 0,75] el SLM lo reemplaza. Hipótesis del marco #27 (PR #40).",
      flujo: "turno cerrado → RoBERTuito+LR → ¿0,35 ≤ p ≤ 0,75? → sí: SLM decide · no: queda el encoder → ContadorGoteo",
      mediciones: [
        "24% de los turnos (126/523) cayeron en zona gris — el SLM no es marginal",
        "Cascada vs encoder solo: goteo 12/16 → 7/16; AUROC 0,666 → 0,537; falsas alarmas iguales (5/10)",
        "Encoder ~875 MB + SLM ~860 MB ≈ 1,7 GB RAM sin el ASR → no entra en 1024 MB; propuesta subir alta a 2048 MB (cambia lo aprobado en #24)",
        "Suite completa: ~624 s con cascada vs ~100 s con encoder solo"
      ],
      lectura: "Refutada en ESTA configuración (SLM sin ajuste, encoder congelado, semillas provisorias, umbrales sin calibrar). La idea sigue como hipótesis: depende de datos reales (#41) y de cuantizar el encoder."
    }
  },

  /* ------------------------------------------------------------------------
   * GAMAS — un solo programa, tres disfraces
   * ----------------------------------------------------------------------*/
  gamas: {
    nota: "Laboratorio = PC x86 con techo de memoria + hilos + sin GPU. No es un emulador Android. Demo Android solo si hay tiempo; iPhone solo como foto de «alta». Fuente: gamas.json y PRIMERA-INVESTIGACION-MODELOS.md.",
    tabla: [
      { gama: "Baja",  asr: "Moonshine tiny-es (27 M, MIT)", detector: "LLM/SLM local", techo: "256 MB", hilos: "2 (1 escribe / 1 lee)", nota: "Moonshine solo como id: no implementado en #29" },
      { gama: "Media", asr: "Zipformer Kroko (sherpa-onnx)", detector: "LLM/SLM local", techo: "512 MB", hilos: "4 (3 / 1)", nota: "" },
      { gama: "Alta",  asr: "Zipformer Kroko (sherpa-onnx)", detector: "LLM/SLM local — se prende primero", techo: "2048 MB", hilos: "6 (4 / 2)", nota: "Techo subido de 1024 → 2048 MB el 2026-09-28 para la cascada; propuesta, falta revalidar (#24)" }
    ],
    regla: "Los dos ayudantes juntos tienen que tardar menos que el audio: RTF < 1. El lenguaje del programa todavía no se eligió — el laboratorio actual es Python."
  },

  /* ------------------------------------------------------------------------
   * MEDICIONES — marco teórico vs medido en laboratorio (2026-09-28)
   * ----------------------------------------------------------------------*/
  mediciones: {
    nota: "Las columnas no son comparables uno a uno: el marco supone ARM + INT8/ONNX; el laboratorio midió PC x86, fp32, sin GPU. Fuente: CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md §3.",
    tabla: [
      { que: "RoBERTuito ms/turno", marco: "38–42 ms (INT8)", medido: "~152 ms p50 (fp32 + LR)", lectura: "La cuantización INT8/ONNX queda pendiente de medir" },
      { que: "RoBERTuito RAM", marco: "145 MB (INT8)", medido: "~875 MB pico RSS (con PyTorch)", lectura: "El pico incluye el runtime; en INT8 sería ~4× más chico (a medir)" },
      { que: "Llama 3.2 1B Q4 ms/turno", marco: "450–850 ms", medido: "~3.884 ms p50", lectura: "~5× lo supuesto, contexto 1024 en x86" },
      { que: "Llama 3.2 1B Q4 RAM", marco: "780 MB", medido: "~860 MB (pesos + caché)", lectura: "Del mismo orden" },
      { que: "Encoder + SLM en alta", marco: "Entra en 1024 MB con ASR", medido: "~1,7 GB sin ASR", lectura: "No entra; propuesta 2048 MB sin revalidar" },
      { que: "Turnos al SLM (zona gris)", marco: "«Pocos» (85% inocentes simulado)", medido: "24% (126/523)", lectura: "El costo del SLM no es marginal" },
      { que: "Negación «no te voy a dar la clave»", marco: "Encoder 0,09 (simulado)", medido: "máx 0,189, sin goteo", lectura: "Coincide en el único caso probado" },
      { que: "«Código de la puerta» (inocente)", marco: "Encoder 0,12 (simulado)", medido: "goteo máx 0,211, pero las REGLAS sí disparan incendio", lectura: "El encoder no se confunde; la vía rápida sí" },
      { que: "Cascada vs encoder (calidad)", marco: "El SLM mejora la zona gris", medido: "goteo 12/16→7/16, AUROC 0,666→0,537", lectura: "H4 refutada en esta corrida" },
      { que: "Reglas incendio", marco: "vía rápida", medido: "13/16", lectura: "Confirmada con límites: falla sin palabra clave" }
    ]
  },

  /* ------------------------------------------------------------------------
   * TAXONOMÍA 6+6 (D07 abierta — selección de trabajo)
   * ----------------------------------------------------------------------*/
  taxonomia: {
    nota: "Dos capas multi-label de 6 etiquetas (acuerdo parcial 2026-10-02). Principio: no superar la docena — en cuatro meses las clases raras destruyen el análisis. Fuente: MANUAL-ANOTACION.md.",
    capa1: {
      nombre: "Capa 1 — Técnicas de manipulación",
      etiquetas: [
        { id: "AUTHORITY_CLAIM", dispara: "Quien llama se presenta como entidad/persona con autoridad o confianza", noDispara: "Que la persona suponga con quién habla" },
        { id: "URGENCY_PRESSURE", dispara: "Impone tiempo, rapidez o consecuencias por demorar", noDispara: "Que el tema sea urgente en sí mismo" },
        { id: "THREAT_FEAR", dispara: "Plantea pérdida, bloqueo, delito, sanción o peligro hacia la persona", noDispara: "Informar un hecho negativo sin atribuir consecuencia" },
        { id: "ISOLATION_SECRECY", dispara: "Pide no cortar, no consultar, no hablar con terceros", noDispara: "Pedir silencio por ruido o para poder explicar" },
        { id: "TRUST_BUILDING", dispara: "Usa datos, procedimientos o jerga para parecer legítimo", noDispara: "El solo hecho de ser legítimo" },
        { id: "PERSISTENCE_DISTRACTION", dispara: "Insiste tras una objeción, redirige la duda, mantiene ocupada a la persona", noDispara: "Repreguntar una vez porque no se escuchó" }
      ]
    },
    capa2: {
      nombre: "Capa 2 — Acciones solicitadas (marcan T_R)",
      etiquetas: [
        { id: "REQUEST_AUTH_CODE", dispara: "Pide O MENCIONA un código de autenticación (OTP, token, WhatsApp)", noDispara: "Código ajeno a la autenticación (ej. puerta)", enReglas: true },
        { id: "REQUEST_SECRET", dispara: "Pide credencial permanente: clave, PIN, CVV, contraseña", noDispara: "Confirmar datos que la entidad ya tiene", enReglas: true },
        { id: "REQUEST_PERSONAL_DATA", dispara: "Pide DNI, CUIL, domicilio, foto de identificación", noDispara: "Que la persona los diga por su cuenta", enReglas: true },
        { id: "REQUEST_TRANSFER", dispara: "Pide mover dinero: transferencia, pago, cripto, efectivo, cajero", noDispara: "Hablar de un movimiento ya ocurrido", enReglas: true },
        { id: "REQUEST_REMOTE_ACCESS", dispara: "Pide instalar acceso remoto o compartir pantalla", noDispara: "Pedir que se abra una app para mirar uno mismo", enReglas: true },
        { id: "REQUEST_SECURITY_ACTION", dispara: "Pide ejecutar acción de seguridad: enlace, cambiar clave, autorizar dispositivo", noDispara: "Recomendar el canal oficial (conducta segura)", enReglas: true }
      ]
    }
  },

  /* ------------------------------------------------------------------------
   * MÉTRICAS (fuente única: METRICAS.md)
   * ----------------------------------------------------------------------*/
  metricas: {
    marcas: [
      { id: "T_A", def: "Momento de la alerta del sistema. NO es el primer cruce del umbral: es el primero que se MANTIENE dos actualizaciones consecutivas (histéresis). Un turno «sin opinión» no es una actualización." },
      { id: "T_R", def: "Inicio del primer pedido de alto riesgo (el atacante lo pide)." },
      { id: "T_C", def: "Inicio de la primera acción de cumplimiento de la víctima (empieza a obedecer). Referencia principal de Preventive@δ (acuerdo 2026-10-02)." }
    ],
    margenes: [
      { id: "L_R = T_R − T_A", def: "Anticipación respecto del primer pedido riesgoso." },
      { id: "L_C = T_C − T_A", def: "Margen de intervención antes de que la víctima empiece a cumplir. Positivo = llegó a tiempo. Se reportan mediana e IQR, no promedio." }
    ],
    preventiva: "Preventive@δ = #{ i : T_A,i ≤ T_C,i − δ } / #{ llamadas de vishing }, para δ = 5, 10, 20 s. La métrica de titular de la tesis.",
    evaluacion: [
      "ASR: WER, recall de términos críticos",
      "Clasificación global: precision, recall, F1, AUPRC, AUROC",
      "Llamadas legítimas: % con al menos una falsa alarma",
      "Carga de falsas alarmas: falsas alertas por hora",
      "Detección temporal: Preventive@5/10/20s, mediana de L_R y L_C",
      "Evolución: métricas con 25%, 50%, 75%, 100% de la llamada (evidencia de incrementalidad)",
      "Maniobras: macro-F1 de etiquetas multi-label",
      "Latencia: p50/p95 desde audio hasta decisión",
      "Rendimiento móvil: memoria, CPU, real-time factor",
      "Explicación: correspondencia entre motivo mostrado y etiqueta real"
    ]
  },

  /* ------------------------------------------------------------------------
   * SIMULADOR — datos para la página riesgo.html
   * ----------------------------------------------------------------------*/
  simulador: {
    /* Llamada de prueba «falso soporte bancario» — VENTANA §6.1 (sintética) */
    llamadaEstafa: [
      { t: 5,   rol: "A", evento: "SUPLANTACION",      texto: "«Le hablo de prevención de fraude del banco»" },
      { t: 20,  rol: "A", evento: "URGENCIA",           texto: "«Detectamos una compra de $340.000»" },
      { t: 35,  rol: "V", evento: "RESISTENCIA",        texto: "«¿Quién habla? ¿De dónde me llama?»" },
      { t: 42,  rol: "A", evento: "URGENCIA",           texto: "«Hay que resolverlo ahora o se confirma»" },
      { t: 65,  rol: "A", evento: "AISLAMIENTO",        texto: "«No corte ni consulte con nadie»" },
      { t: 90,  rol: "V", evento: "RESISTENCIA",        texto: "«¿Por qué no puedo llamar yo al banco?»" },
      { t: 98,  rol: "A", evento: "AISLAMIENTO",        texto: "«Si corta se confirma, quédese conmigo»" },
      { t: 130, rol: "A", evento: "DESVIO",             texto: "«Abra la app, vamos a hacer el reverso»" },
      { t: 185, rol: "A", evento: "SOLICITUD_CRITICA",  texto: "«Díctame los seis dígitos del SMS»", marca: "T_R" },
      { t: 200, rol: "V", evento: "CUMPLIMIENTO",       texto: "«El código es 4 8 2…»", marca: "T_C" }
    ],
    /* Dos versiones calculadas en VENTANA §6 (coeficientes elegidos a mano:
       prueban el mecanismo, no miden rendimiento) */
    trazas: {
      informe: {
        nombre: "Fórmula del informe (C·σ(M))",
        puntos: [ {t: 65, m: 0.84, c: 0, s: 0}, {t: 98, m: 0.84, c: 0, s: 0}, {t: 130, m: 0.92, c: 0.30, s: 0.28}, {t: 185, m: 1.0, c: 1.0, s: 0.95}, {t: 200, m: 1.0, c: 1.0, s: 0.95, alerta: true} ],
        resultado: "T_A = 200 s · L_R = −15 s · L_C = 0 s — la alerta llega cuando la víctima ya dicta el código. C_t compuerta: sin pedido, S = 0 → PI2 estructuralmente imposible."
      },
      corregido: {
        nombre: "Diseño corregido σ(a·M + b·C + c·M·C + sesgo)",
        puntos: [ {t: 120, m: 0.84, c: 0, s: 0.30}, {t: 135, m: 0.92, c: 0.30, s: 0.76}, {t: 150, m: 0.92, c: 0.30, s: 0.76, alerta: true} ],
        resultado: "T_A = 150 s · L_R = +35 s · L_C = +50 s — alerta 35 s ANTES del pedido (coeficientes a=4, b=1, c=5, sesgo=−4,2 elegidos a mano: muestra que anticipar es posible, no que funcione)."
      }
    },
    controles: [
      { caso: "Llamada legítima del banco (4 de 5 marcadores)", riesgoMax: 0.38, resultado: "No alerta" },
      { caso: "«Pasame el código» sin contexto (C=1, M=0)", riesgoMax: 0.08, resultado: "No alerta · con la fórmula del informe daba 0,50" }
    ],
    /* §5.5 — vidas medias ilustrativas, no calibradas */
    vidasMedias: [
      { tipo: "URGENCIA", h: 60, pesos: { "0 s": 1.00, "1 min": 0.50, "2 min": 0.25, "5 min": 0.03, "10 min": 0.00, "15 min": 0.00 } },
      { tipo: "AISLAMIENTO", h: 180, pesos: { "0 s": 1.00, "1 min": 0.79, "2 min": 0.63, "5 min": 0.31, "10 min": 0.10, "15 min": 0.03 } },
      { tipo: "SUPLANTACION", h: 600, pesos: { "0 s": 1.00, "1 min": 0.93, "2 min": 0.87, "5 min": 0.71, "10 min": 0.50, "15 min": 0.35 } }
    ],
    indicadores: [
      { id: "κ", nombre: "Cobertura de fases", formula: "fases del guion presentes / 5", pregunta: "¿Cuántas partes del guion de estafa aparecieron?", guion: "1 suplantación → 2 urgencia → 3 aislamiento → 4 desvío → 5 solicitud crítica" },
      { id: "Ω", nombre: "Orden de la escalada", formula: "(pares en orden + m·0,5) / (pares totales + m), m=3", pregunta: "¿Los hechos aparecieron en el orden en que se arma una estafa?" },
      { id: "δ", nombre: "Respuesta a la resistencia", formula: "resistencias respondidas con presión / resistencias totales", pregunta: "Cuando la víctima desconfió, ¿el otro dio datos o apretó más? — es lo que más separa estafa de llamada real del banco", nota: "Si la víctima nunca desconfía δ=0 y no aporta: la más vulnerable recibe menos ayuda de este indicador. Notación: METRICAS usa δ para Preventive@δ — conviene renombrarlo." }
    ],
    formulaRiesgo: {
      M: "M_t = 0,40·κ + 0,30·Ω + 0,30·δ",
      C: "C_t: nivel más alto alcanzado, no baja — nada 0,00 · desvío («abrí la app») 0,30 · solicitud crítica 1,00",
      S: "S_t = σ(4·M_t + 1·C_t + 5·M_t·C_t − 4,2)",
      umbrales: "θ_high ≈ 0,75 enciende (sostenido dos actualizaciones) · θ_low ≈ 0,40 apaga — valores iniciales a calibrar",
      tablaCasos: [
        { caso: "Nada", m: 0, c: 0, crudo: -4.20, s: 0.01 },
        { caso: "Pedido sin manipulación", m: 0, c: 1.0, crudo: -3.20, s: 0.04 },
        { caso: "Mucha manipulación sin pedido", m: 0.90, c: 0, crudo: -0.60, s: 0.35 },
        { caso: "Llamada legítima del banco", m: 0.62, c: 0.30, crudo: -0.49, s: 0.38 },
        { caso: "Estafa: pide abrir la app", m: 0.92, c: 0.30, crudo: 1.16, s: 0.76 },
        { caso: "Estafa: pide el código", m: 1.0, c: 1.0, crudo: 5.80, s: 1.00 }
      ]
    },
    /* §7.1 — cuenta de probabilidad que vale para cualquier detector */
    falsasAlarmas: {
      formula: "P(al menos una falsa alarma) = 1 − (1 − p)^N · N = duración / cadencia",
      tablaCadencia: {
        encabezados: ["Cadencia", "N (20 min)", "acierta 99,9%", "acierta 99,5%", "acierta 99%", "acierta 98%"],
        filas: [
          ["cada 5 s", 240, "21,3%", "70,0%", "91,0%", "99,2%"],
          ["por turno (~10 s)", 120, "11,3%", "45,2%", "70,1%", "91,1%"],
          ["cada 15 s", 80, "7,7%", "33,0%", "55,2%", "80,1%"],
          ["cada 30 s", 40, "3,9%", "18,2%", "33,1%", "55,4%"],
          ["cada 60 s", 20, "2,0%", "9,5%", "18,2%", "33,2%"]
        ]
      },
      margenAceptacion: [
        { tolera: "1 de cada 100 llamadas legítimas con alerta", cada15: "1 error cada 7.960 revisiones", cada60: "1 error cada 1.990 revisiones" },
        { tolera: "5 de cada 100", cada15: "1 cada 1.560", cada60: "1 cada 390" },
        { tolera: "10 de cada 100", cada15: "1 cada 759", cada60: "1 cada 190" }
      ],
      reglaDosSeguidas: {
        nota: "80 revisiones por llamada; estimación optimista (errores independientes — en la realidad vienen en racha)",
        encabezados: ["Acierto por revisión", "Sin regla", "Dos seguidas", "Máx 3 + dos seguidas", "2 de los últimos 3"],
        filas: [
          ["99,5%", "32,9%", "0,2%", "32,8%", "0,4%"],
          ["99%", "55,2%", "0,8%", "54,8%", "1,5%"],
          ["98%", "80,2%", "3,1%", "79,7%", "5,9%"]
        ]
      }
    },
    /* §7.2 — ventana dura vs decaimiento, llamada de 19 min */
    ventana: {
      nota: "Mecanismo sostenido; los segundos salen de una llamada inventada. Sin ventana: el ruido viejo invierte Ω (cae de 1,00 a 0,33 cuando empieza la estafa). Con ventana deslizante de 300 s el orden queda limpio pero corta brusco y borra la suplantación de hace 5 min — por eso se propone decaimiento por tipo.",
      sinVentana: [
        { min: "10,0", k: 0.40, o: 1.00, m: 0.46, s: 0.20, que: "Ruido de la charla" },
        { min: "15,0", k: 0.60, o: 0.33, m: 0.34, s: 0.12, que: "Empieza la estafa" },
        { min: "16,0", k: 0.80, o: 0.58, m: 0.80, s: 0.62, que: "" },
        { min: "18,0", k: 1.00, o: 0.81, m: 0.94, s: 0.99, que: "Piden el código" },
        { min: "18,2", k: 1.00, o: 0.81, m: 0.94, s: 0.99, que: "ALERTA (tarde)" }
      ],
      conVentana: [
        { min: "14,8", k: 0.20, o: 0.50, m: 0.23, s: 0.07, que: "El ruido viejo ya no cuenta" },
        { min: "15,2", k: 0.40, o: 1.00, m: 0.46, s: 0.20, que: "Empieza la estafa, orden limpio" },
        { min: "17,2", k: 0.80, o: 1.00, m: 0.92, s: 0.76, que: "" },
        { min: "17,5", k: null, o: null, m: null, s: null, que: "ALERTA (antes del pedido)" },
        { min: "18,0", k: 1.00, o: 1.00, m: 1.00, s: 1.00, que: "Piden el código" }
      ]
    }
  },

  /* ------------------------------------------------------------------------
   * ESCALERA de avisos (DISENO-INTEGRADO §3)
   * ----------------------------------------------------------------------*/
  escalera: [
    { nivel: "Moderado", cuando: "El riesgo entra a la zona dudosa y se sostiene", ve: "Un aviso de que algo no cierra", histeresis: "Sí" },
    { nivel: "Alto", cuando: "El riesgo supera θ_high dos actualizaciones seguidas", ve: "El aviso de estafa, con la etiqueta que lo disparó como explicación", histeresis: "Sí — se apaga debajo de θ_low" },
    { nivel: "Pedido crítico", cuando: "Una regla confirma pedido de código, clave, transferencia o acceso remoto", ve: "El aviso más fuerte, en el momento del pedido (T_R)", histeresis: "No — es el momento de mayor daño" }
  ],

  /* ------------------------------------------------------------------------
   * MOCKUPS de aviso (ARQUITECTURA.md — propuesta sin discutir)
   * ----------------------------------------------------------------------*/
  mockups: [
    {
      nivel: "Riesgo moderado — presión para abrir la aplicación",
      titulo: "Revisá esta llamada",
      que: "Dice llamar del banco y te apura para abrir la aplicación.",
      porque: "La urgencia dificulta verificar quién llama. Puede ser un engaño.",
      hacer: "No compartas códigos ni claves. Buscá el número oficial y consultá vos.",
      boton: "Entendido"
    },
    {
      nivel: "Riesgo alto — pedido de código",
      titulo: "No compartas el código",
      que: "En esta llamada te pidieron un código de verificación.",
      porque: "Alguien podría usarlo para entrar a tu cuenta. Puede ser una estafa.",
      hacer: "No lo dictes. Cortá y llamá vos al número oficial del banco.",
      boton: "Entendido"
    }
  ],

  /* ------------------------------------------------------------------------
   * ARCHIVOS del laboratorio (mapa código → componente)
   * ----------------------------------------------------------------------*/
  laboratorio: {
    nota: "Carpeta experiments/laboratorio/ del spike #29 (rama de Ignacio, commit 5ac40b5 del 2026-09-28, todavía fuera de main al momento del contraste). Docker + docker-compose (servicios `corrida` y `slm`).",
    archivos: [
      { path: "pipeline.py", que: "Une todo: replay WAV→ASR→reglas→turnos→detector→ContadorGoteo→JSON/CSV. Modo --texto sin ASR (brazo transcripción de E1). Contiene ContadorGoteo y leer_wav_mono_16k." },
      { path: "asr.py", que: "Quien escribe: Zipformer Kroko streaming vía sherpa-onnx. Moonshine solo como id en gamas.json." },
      { path: "turns.py", que: "CortadorTurnos: silencio RMS < 0,02 por 400 ms cierra el turno. No es un VAD de tesis." },
      { path: "rules.py", que: "Incendio: 6 patrones REQUEST_*, fuzzy de 1 typo, negaciones + imperativos." },
      { path: "detector.py", que: "DetectorLlm (clasificador|agente|base) + crear() que lee env DETECTOR=llm|encoder|cascada." },
      { path: "detector_encoder.py", que: "DetectorEncoder: RoBERTuito congelado fp32 + LR seed 42 sobre semillas.json." },
      { path: "detector_cascada.py", que: "DetectorCascada: zona gris 0,35–0,75 consulta al SLM; registra ms por capa." },
      { path: "config.py + gamas.json", que: "Un programa, tres gamas: baja/media/alta con techo_mb e hilos." },
      { path: "correr_encoders.py", que: "Corre la suite con cada detector y escribe CSV por corrida." },
      { path: "chequear_casos.py", que: "Oracle: falla si el incendio no da lo esperado; pruebas de typos/tildes/muletillas." },
      { path: "armar_semillas.py + semillas_manifiesto.json", que: "Semillas de entrenamiento (YouTube argentino + ES-Port); al repo va solo el manifiesto." },
      { path: "casos/", que: "21 guiones (13 vishing + 8 legítimas difíciles) + 5 casos difíciles, con README de 25 pasadas del stub." },
      { path: "resultados/", que: "CSV por fecha + GLOSARIO-COLUMNAS.md." },
      { path: "ui_laboratorio.py / ui_resultados.py", que: "UIs del laboratorio para correr e inspeccionar resultados." },
      { path: "Dockerfile / docker-compose.yml", que: "Servicios `corrida` (ASR + detector) y `slm` (Ollama llama3.2:1b-instruct-q4_K_M, ctx 1024)." }
    ]
  },

  /* ------------------------------------------------------------------------
   * LECTURA EN CRIOLLO (para el panel «en simple»)
   * ----------------------------------------------------------------------*/
  enSimple: [
    "El que escribe (ASR) no para; el que lee (detector) piensa solo al cerrar la frase. Las reglas miran el borrador y son la vía de incendio.",
    "Un anotador guarda solo los hechos importantes con hora y quién los dijo — no la charla. Cuesta ~0 tokens y dura toda la llamada.",
    "Hace falta presión Y pedido juntos: «pasame el código» en contexto legítimo no dispara nada.",
    "La alerta no salta por un pico: el riesgo tiene que sostenerse dos revisiones; el pedido crítico es la excepción escrita.",
    "Revisar seguido junta falsas alarmas: acertar 99% por revisión revisando cada 15 s deja el 55% de las legítimas de 20 min con al menos un aviso falso."
  ],

  fuentes: [
    { path: "../ARQUITECTURA.md", que: "Arquitectura v0 — propuesta sin discutir" },
    { path: "../gestion/MAPA-DECISIONES.md", que: "Estado de D01–D13" },
    { path: "../investigacion/DISENO-INTEGRADO.md", que: "Cómo encajan recorte de modelos + ventana; escalera; dos brazos" },
    { path: "../investigacion/VENTANA-DE-CONTEXTO-Y-ALERTA.md", que: "Registro de eventos, κ/Ω/δ, fórmula de riesgo, falsas alarmas" },
    { path: "../investigacion/PRIMERA-INVESTIGACION-MODELOS.md", que: "Contrato de laboratorio, gamas, incendio vs goteo" },
    { path: "../investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md", que: "Marco vs medido; dificultades; próximas pruebas" },
    { path: "../evaluacion/METRICAS.md", que: "T_A/T_R/T_C, L_R/L_C, Preventive@δ" },
    { path: "../datos-etica/MANUAL-ANOTACION.md", que: "Taxonomía 6+6" },
    { path: "../datos-etica/PRIVACIDAD-DEL-SISTEMA.md", que: "Procesamiento local, descarte de contenido" },
    { path: "../../../experiments/laboratorio/", que: "Código Python del spike #29" }
  ]
};
