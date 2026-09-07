# Mapa de decisiones

**Destino:** Plan de Trabajo aprobado y ruta sin decisiones críticas abiertas para
ejecutar y evaluar el Proyecto Final de vishing.

Cada decisión debe tener una sola fuente de verdad. Cuando una decisión técnica amerite detalle, se crea un
ADR en [`docs/ingenieria/adr/`](../ingenieria/adr/) y desde aquí solo se enlaza su conclusión.
Plantilla en [PLANTILLA-ADR.md](../ingenieria/adr/PLANTILLA-ADR.md).

**Este archivo es la única numeración válida.** Circuló una lista paralela `D1`–`D10` con otro
criterio; sus entradas fueron absorbidas acá y esa numeración queda sin efecto para evitar que dos
personas digan "D5" refiriéndose a cosas distintas. La correspondencia está al final, en
[Migración de la numeración anterior](#migración-de-la-numeración-anterior).

## Frontera: decisiones que pueden tomarse ahora

### D01 — Completar el contrato académico

- **Pregunta:** ¿qué fecha exacta, plantilla, estilo bibliográfico, entregables
  adicionales y proceso ético aplican al grupo?
- **Tipo:** conversación con profesor/tutor.
- **Responsable:** coordinador de la próxima clase.
- **Evidencia:** minuta del 9 de septiembre validada.
- **Desbloquea:** D02, D03, D10 y cronograma definitivo.
- **Estado:** parcialmente resuelto; formato general, grupo y plazo aproximado ya
  fueron informados.

### D02 — Definir problema, usuario y necesidad

- **Pregunta:** ¿quién necesita qué decisión o protección, en qué momento de la
  llamada y frente a qué daño?
- **Tipo:** decisión de alcance con investigación del dominio.
- **Responsable:** por autoasignación en GitHub.
- **Evidencia:** problema en cinco líneas, persona/actor y tres escenarios.
- **Bloqueada por:** D01 solo en su formulación final.
- **Desbloquea:** D03, D04, D06 y requisitos.
- **Estado:** abierto.

### D05 — Elegir la fuente de audio demostrable

- **Pregunta:** ¿cuál será la integración objetivo entre replay en streaming, VoIP
  controlado y micrófono/altavoz de laboratorio?
- **Tipo:** investigación + spike técnico.
- **Responsable:** por autoasignación en GitHub.
- **Evidencia:** prueba mínima, restricciones oficiales, latencia y riesgos.
- **Desbloquea:** arquitectura y requisitos del prototipo, y D11.
- **Estado:** abierto; replay es la base recomendada.

Las cinco opciones sobre la mesa, con el detalle técnico en
[ALTERNATIVAS-CAPTURA-AUDIO.md](../ingenieria/ALTERNATIVAS-CAPTURA-AUDIO.md):

| Opción | Qué demuestra | Lectura del deep research |
|---|---|---|
| Motor sobre grabaciones reproducidas como stream | Algoritmo completo, incrementalidad, latencia, anticipación | **Base experimental obligatoria** |
| App con llamada VoIP controlada (el audio es de la app) | Funcionamiento durante una conversación real | **Objetivo principal del prototipo** |
| Micrófono/altavoz en laboratorio | Concepto interactivo rápido | Útil al principio |
| AOSP / root / app de sistema | Acceso privilegiado a telefonía | Solo *stretch goal* |
| App stock escuchando cualquier llamada del dialer | Producto equivalente a integración OEM | **Fuera de alcance** |

**La captura acústica por altavoz no está decidida.** El [anteproyecto](../propuesta/ANTEPROYECTO.md)
(sección 8) la da por resuelta y hasta construye un argumento a favor —la población objetivo ya usa
el altavoz—, pero entró como supuesto, no como decisión discutida. Está marcado como `S1` en
[CORRECCIONES-ANTEPROYECTO.md](../propuesta/CORRECCIONES-ANTEPROYECTO.md).

| | A favor | En contra |
|---|---|---|
| **Altavoz / micrófono** | Funciona en cualquier teléfono, sin permisos privilegiados; se alinea con el uso real de la población objetivo | Calidad muy inferior a la de línea; ruido, reverberación y cancelación de eco degradan el ASR; solo captura bien un lado |
| **VoIP propia** | Audio limpio y separado por canal; es de la app, sin permisos especiales | No es una llamada telefónica real; hay que justificar la validez del escenario |
| **Replay de grabaciones** | Determinista y reproducible; permite medir el algoritmo sin ruido de plataforma | No demuestra funcionamiento en vivo |

No son excluyentes: lo más probable es que replay sea la base experimental y VoIP o altavoz la
demostración. Pero hay que decidirlo y escribirlo.

### D06 — Definir la gobernanza de datos

- **Pregunta:** ¿qué se grabará, con qué consentimiento, dónde vivirá, quién
  accederá, qué podrá publicarse y cuándo se eliminará?
- **Tipo:** decisión ética con tutor.
- **Responsable:** por autoasignación; validación del tutor.
- **Evidencia:** plan de datos y consentimiento aprobados antes de grabar.
- **Desbloquea:** corpus piloto.
- **Estado:** abierto.

## Decisiones precisas pero bloqueadas

### D03 — Congelar alcance y contribución

- **Pregunta:** ¿cuál es el núcleo obligatorio, cuáles son los stretch goals y qué
  queda fuera de alcance?
- **Bloqueada por:** D01, D02 y D05.
- **Salida:** objetivos, aporte y lista explícita de exclusiones.

### D04 — Aprobar preguntas e hipótesis

- **Pregunta:** ¿qué afirmaciones se evaluarán y qué observación podría refutarlas?
- **Bloqueada por:** D02 y D03.
- **Salida:** PI1–PI2, evaluaciones E1–E2 y tabla pregunta→evidencia.

### D07 — Aprobar taxonomía y evento crítico

- **Pregunta:** ¿qué maniobras y pedidos se anotan, y cómo se marcan `T_R` y `T_C`?
- **Bloqueada por:** D02, D04 y D06.
- **Salida:** manual de anotación v0 probado por los cuatro integrantes.

Hay una propuesta concreta de dos capas multi-label de 6 etiquetas cada una en
[MANUAL-ANOTACION.md](../datos-etica/MANUAL-ANOTACION.md), con el principio de no superar la docena
de etiquetas: en cuatro meses las clases raras destruyen el análisis estadístico. Falta decidir si se
adoptan tal cual o se derivan de un relevamiento propio de modalidades argentinas (UFECI, ANSES,
PAMI, BCRA).

Sobre el evento crítico, la definición de `T_A`, `T_R` y `T_C` y por qué hacen falta las tres marcas
está en [METRICAS.md](../evaluacion/METRICAS.md). Dos puntos que esta decisión tiene que cerrar:
`T_A` se define con histéresis (no el primer cruce del umbral, sino el primero que se sostiene dos
actualizaciones), y hay que elegir si `Preventive@δ` se mide contra `T_C` o contra `T_R`.

### D08 — Congelar protocolo experimental

- **Pregunta:** ¿cómo se muestrea, divide y evalúa sin fuga de información?
- **Bloqueada por:** D04 y D07.
- **Salida:** splits, baselines, métricas, seeds, test congelado y amenazas.

Este punto puede determinar la credibilidad completa de los resultados: si dos variantes del mismo
guion caen una en train y otra en test, el modelo ya vio el escenario. El procedimiento de división
está en [METODO-CREACION-CORPUS.md §9](../datos-etica/METODO-CREACION-CORPUS.md#9-división-de-datos)
y las definiciones de métrica en [METRICAS.md](../evaluacion/METRICAS.md). Adoptarlo es barato ahora
y carísimo de arreglar después.

Falta fijar además la restricción de falsos positivos **antes** de medir. El anteproyecto la
menciona pero no la define, y sin ese número la hipótesis no es falsable.

### D09 — Elegir ASR y detector

- **Pregunta:** ¿qué combinación satisface la calidad y el presupuesto de cómputo?
- **Bloqueada por:** D05, D07 y benchmark piloto.
- **Salida:** decisión basada en WER/recall crítico, F1/AUPRC, latencia y memoria.
- **Candidatos a evaluar:** sherpa-onnx, Vosk y whisper.cpp para ASR; TF-IDF como baseline
  obligatorio y BETO o RoBERTuito para español. La decisión sale del benchmark, no de una
  preferencia previa.

### D10 — Congelar estructura de entrega y defensa

- **Pregunta:** ¿qué índice, anexos, paquete reproducible, duración y demo se
  entregan?
- **Bloqueada por:** D01 y resultados de evaluación.
- **Salida:** checklist final aceptado por el tutor.

### D11 — Análisis lingüístico o también acústico

- **Pregunta:** ¿el detector trabaja solo sobre la transcripción del ASR, o también sobre rasgos
  bioacústicos (tono, estrés vocal, MFCCs)?
- **Bloqueada por:** D05. Si la captura termina siendo acústica por altavoz, la reverberación, el
  ruido y la cancelación de eco del hardware destruyen justamente los rasgos que el análisis
  acústico necesita, y la pregunta se responde sola.
- **Salida:** alcance del stack de features y, con él, el esfuerzo de las próximas semanas.
- **Recomendación del deep research:** solo NLP sobre la transcripción, con lo bioacústico como
  trabajo futuro declarado en las conclusiones. Ver
  [SINTESIS-ESTADO-DEL-ARTE.md](../investigacion/SINTESIS-ESTADO-DEL-ARTE.md).

### D12 — Encuadre del foco en adultos mayores

- **Pregunta:** ¿se mantiene el foco en adultos mayores y con qué justificación?
- **Bloqueada por:** D02.
- **Salida:** justificación reescrita en el anteproyecto y en el Plan de Trabajo.
- **Detalle:** el deep research no pide abandonar el foco, pide **cambiar la justificación**: de
  "son los más afectados" —no demostrado para Argentina— a "gravedad potencial de las pérdidas y
  exposición a estafas de suplantación". También advierte no convertir el reclutamiento de adultos
  mayores en un bloqueo del corpus: mejor incluirlos en evaluación y en la prueba de usabilidad.
  Corresponde a la corrección `C4` de
  [CORRECCIONES-ANTEPROYECTO.md](../propuesta/CORRECCIONES-ANTEPROYECTO.md).

### D13 — Título definitivo

- **Pregunta:** ¿cuál es el título final de la tesis?
- **Bloqueada por:** D03 y la composición geográfica real del corpus.
- **Salida:** título consistente con lo que el corpus efectivamente cubre.
- **Regla:** no cerrarlo antes de tener el corpus. Un título que promete "español argentino" obliga
  a un corpus que lo sostenga.

## Decisiones cerradas

- **Institución y equipo:** UNSTA, Ingeniería en Informática, Plan 2008; Albarracín
  Ignacio, Antenucci Mateo, Grosso Luciano y Villalobo Evaristo están autorizados
  como grupo de cuatro.
- **Formato base:** entrega digital, A4, carilla simple, portada institucional,
  resúmenes español/inglés, cuerpo técnico y unas 100 páginas como referencia.
- **Horizonte:** entrega hacia fines de diciembre de 2026; falta el día exacto.
- **No basar la tesis en capturar cualquier llamada PSTN desde una app Android
  ordinaria:** la plataforma reserva esas fuentes a componentes privilegiados.
- **Separar motor e integración:** replay en streaming es la base experimental;
  VoIP controlado es la integración preferida si el spike confirma viabilidad.
- **No hacer detección de deepfake en el núcleo:** responde una pregunta distinta
  a detectar manipulación y pedidos peligrosos.
- **Mantener baselines simples:** reglas y TF–IDF son comparadores obligatorios.

### Acordadas entre Antenucci y Grosso — a ratificar por los cuatro

Las dos surgieron al unificar la documentación. Alinean con lo que ya estaba escrito, pero **no
fueron discutidas por el grupo completo**; entran a la agenda de la próxima reunión.

- **El tamaño del corpus se decide después del piloto**, con el criterio de
  [METODO-CREACION-CORPUS.md §7](../datos-etica/METODO-CREACION-CORPUS.md#7-cómo-se-determina-el-tamaño-final):
  diversidad, incertidumbre estadística, curva de aprendizaje y capacidad real. Quedan descartadas
  las bandas fijas de 160/240/320 conversaciones que circulaban en la otra lista de decisiones.
  Motivo: fijar el número antes del piloto obliga después a inventar una justificación
  retrospectiva.
- **Documentación y código conviven en este repositorio.** Rige la estructura objetivo de
  [PLAN-MAESTRO.md §10](PLAN-MAESTRO.md#10-sistema-de-archivos): `src/`, `data/`, `experiments/` y
  `tests/` se crean cuando exista el primer artefacto real, no antes. Queda sin efecto la idea de
  llevar el prototipo a un repositorio aparte.

## No especificado todavía

- Diseño exacto del warning y método de evaluación con usuarios.
- Modelo de estado temporal que competirá con el acumulador probabilístico.
- Dispositivo Android objetivo y presupuesto máximo de memoria/latencia.
- Posibilidad y licencia de publicación del corpus o solo sus metadatos.
- Técnica estadística final, que depende del tamaño y distribución obtenidos.

## Fuera de alcance provisional

- Captura universal de llamadas PSTN en Android stock.
- iOS, múltiples idiomas, caller-ID reputation, detección de malware y análisis de
  mensajes de texto.
- Detección de voz sintética o identidad biométrica del interlocutor.
- Backend de producción, publicación en Play Store y operación comercial.
- Estudio clínico o generalización poblacional con adultos mayores.

## Regla de uso

En cada seguimiento se puede cerrar una o dos decisiones con evidencia. No se
discute tecnología bloqueada por una decisión anterior. Al cerrar una decisión:

1. registrar fecha, participantes, alternativas y evidencia;
2. escribir conclusión y consecuencias;
3. actualizar bloqueos y promover lo que ya pueda especificarse;
4. cambiar el Plan de Trabajo si altera alcance, tiempo o entregables;
5. pedir validación al tutor si afecta el contrato académico o ético.

## Migración de la numeración anterior

Circuló una lista `D1`–`D10` con otro criterio de ordenamiento. Sus entradas están absorbidas acá.
Esta tabla existe solo para que quien haya leído aquella lista encuentre dónde quedó cada cosa; la
numeración vieja no debe volver a usarse.

| Numeración anterior | Dónde quedó |
|---|---|
| D1 — alcance y método de captura | dividida en [D03](#d03--congelar-alcance-y-contribución) (alcance) y [D05](#d05--elegir-la-fuente-de-audio-demostrable) (captura) |
| D2 — lingüístico vs. acústico | [D11](#d11--análisis-lingüístico-o-también-acústico) |
| D3 — taxonomía de maniobras | [D07](#d07--aprobar-taxonomía-y-evento-crítico) |
| D4 — construcción y tamaño del corpus | [D06](#d06--definir-la-gobernanza-de-datos) + método del corpus; el tamaño ya está resuelto |
| D5 — partición train/val/test | [D08](#d08--congelar-protocolo-experimental) |
| D6 — definición del momento crítico | [D07](#d07--aprobar-taxonomía-y-evento-crítico) |
| D7 — ASR y modelo de clasificación | [D09](#d09--elegir-asr-y-detector) |
| D8 — reparto del trabajo | resuelto: [PLAN-MAESTRO.md §8](PLAN-MAESTRO.md#8-líneas-de-trabajo-sin-asignación-fija) usa autoasignación por issues, sin responsables fijos |
| D9 — foco en adultos mayores | [D12](#d12--encuadre-del-foco-en-adultos-mayores) |
| D10 — título de la tesis | [D13](#d13--título-definitivo) |
