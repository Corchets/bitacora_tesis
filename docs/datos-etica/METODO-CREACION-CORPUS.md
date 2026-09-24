# Método de creación del corpus

Este documento define quién diseña las llamadas, de dónde salen los diálogos y cómo
se determina la cantidad. El equipo diseña el corpus; los voluntarios interpretan
roles sin memorizar un diálogo completo; el profesor/tutor valida el método antes
de escalar la grabación.

## 1. Unidad del corpus

- **Familia:** modalidad amplia, por ejemplo “banco” o “soporte técnico”.
- **Semilla:** situación concreta, por ejemplo “compra sospechosa y pedido de OTP”.
- **Ficha de rol:** objetivos y límites separados para cada interlocutor.
- **Conversación:** una interpretación particular de una semilla.
- **Turno:** intervención de un hablante con timestamps y etiquetas.

La conversación es la unidad de clasificación. Turnos derivados de la misma
conversación permanecen en el mismo split.

## 2. De dónde salen las llamadas

El equipo construye un catálogo a partir de:

1. modalidades documentadas por organismos oficiales argentinos;
2. alertas de prevención publicadas por entidades financieras reguladas;
3. tipologías y progresiones descriptas en literatura académica;
4. negativos legítimos diseñados para compartir vocabulario con cada fraude;
5. revisión del profesor/tutor para pertinencia y seguridad.

El punto 2 se agregó al incorporar `SC-SOPORTE-REMOTO-01` con una alerta de Banco Galicia sobre
estafa de pantalla compartida. Mateo aprobó el 2026-09-23 usar alertas de entidades financieras
reguladas como fuentes para el catálogo v0, además de las oficiales: pueden documentar una modalidad
observada por la entidad, pero no permiten inferir su prevalencia nacional ni las prácticas de todos
los bancos. Se registran igual que las demás: afirmación concreta, URL y fecha de consulta.

El catálogo vive en `CATALOGO-ESCENARIOS.csv`. Una modalidad entra al corpus cuando
tiene fuente, acción crítica, evidencia observable y un negativo comparable.

### Columnas del catálogo

| Columna | Qué contiene |
|---|---|
| `scenario_id` | Identificador estable. `SC-` para fraudulenta, `LG-` para legítima difícil |
| `familia` | Modalidad amplia: `banco`, `soporte`, `organismo_previsional`, `familiar`, `premio` |
| `clase` | `vishing` o `legitima_dificil` |
| `titulo` | Nombre corto de la situación |
| `fuente` | En una fraudulenta, afirmación concreta que respalda la modalidad. En una legítima difícil, **diseño ficticio del equipo** y fuente de la conducta segura, no de la llamada exacta. Incluir URL y **fecha de consulta** |
| `identidad_suplantada_o_contexto` | Identidad que afirma el llamante o contexto de una consulta iniciada por la persona |
| `objetivo` | Qué busca conseguir |
| `maniobras` | Etiquetas de la capa 1 del [manual](MANUAL-ANOTACION.md#capa-1--técnicas-de-manipulación), separadas por `;` |
| `accion_critica` | Etiqueta de la capa 2 que marca `T_R`, o `NONE` en las legítimas |
| `negativo_pareado` | `scenario_id` de una contraparte comparable. Un negativo puede servir a varias semillas del mismo contexto; la relación no tiene que ser recíproca |
| `estado` | Ver abajo |
| `notas` | Advertencias de seguridad y datos ficticios a usar |

Las etiquetas de `maniobras` y `accion_critica` se definen en el
[manual de anotación](MANUAL-ANOTACION.md), que es su única fuente de verdad. Usarlas acá en vez de
prosa permite validar el catálogo con un script y evita que la semilla y la anotación hablen dos
idiomas distintos.

Mateo aprobó el 2026-09-23 usar etiquetas de la capa 1 en `maniobras` como contrato de trabajo del
catálogo v0. No se congela con esto la taxonomía completa ni las reglas temporales de
[D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).

### Valores de `estado`

| Valor | Significado | Qué habilita |
|---|---|---|
| `borrador` | La fila existe pero le falta algo: fuente, negativo pareado o definición | Nada. Es trabajo en curso |
| `con_fuente` | La modalidad fraudulenta o la conducta segura del negativo tiene respaldo citado; el escenario legítimo concreto se identifica como ficticio | Se puede discutir y revisar |
| `revisado` | Revisión cruzada de fuente, pertinencia, pareo y seguridad documentada bajo responsabilidad de un integrante distinto del autor; se declara si el contraste usó asistencia automatizada | Queda lista para seleccionar; la grabación sigue sujeta al método y consentimiento del piloto |
| `descartado` | Se decidió no usarla. La fila **se conserva** con el motivo en `notas` | Nada, pero deja registro |

La revisión cruzada del catálogo v0 se registró el 2026-09-23 bajo responsabilidad de Mateo, quien
leyó y valoró los escenarios y encargó a Codex el contraste detallado de fuentes, pareos y seguridad.
La revisión de las URL fue asistida; no se afirma que Mateo haya abierto personalmente cada una.
Se corrigieron afirmaciones no respaldadas y se diseñaron negativos comparables. `revisado` no
significa que una llamada haya sido grabada ni que el profesor haya aprobado el tamaño o la
composición del piloto de [#22](https://github.com/Corchets/bitacora_tesis/issues/22).

Una semilla descartada no se borra. La sección 10 exige registrar las exclusiones con su motivo, y
el mismo criterio vale acá: si alguien pregunta por qué una modalidad no está en el corpus, la
respuesta tiene que estar en el catálogo y no en el historial de Git.

### Procedencia del catálogo v0

Quien revise el catálogo necesita saber cómo se construyó cada parte, porque no todas tienen el
mismo respaldo:

| Parte | Quién la produjo |
|---|---|
| Las cuatro filas iniciales de banco y WhatsApp | El equipo, 2026-09-07 |
| Las nueve semillas fraudulentas vigentes | Derivadas de modalidades que describen los organismos públicos y la entidad financiera regulada citados en cada fila; los detalles de dramatización son ficticios |
| Los ocho negativos difíciles | Diseñados por el equipo. Las fuentes citadas respaldan conductas seguras, **no esas llamadas exactas** |
| La redacción de filas y la búsqueda de fuentes | Asistida por modelos de lenguaje. Evaristo informó una primera comprobación de URL; Mateo encargó una segunda pasada asistida de afirmaciones y enlaces el 2026-09-23 |

Un intento previo construyó las semillas primero y buscó la fuente después. Se descartó: producía
escenarios sin respaldo y dejaba afuera modalidades documentadas. El orden correcto es el de la
sección 2 — la fuente primero, la semilla después — y el catálogo vigente se rehizo con ese orden.


## 3. Cómo se diseña una semilla fraudulenta

Cada semilla especifica:

- identidad que se suplanta;
- pretexto y problema inventado;
- objetivo del atacante;
- maniobras permitidas: autoridad, urgencia, miedo, aislamiento o persistencia;
- solicitud riesgosa objetivo;
- punto `T_R`: comienzo de la solicitud;
- posible punto `T_C`: comienzo de cumplimiento;
- ramas si la otra persona duda, acepta o rechaza;
- datos ficticios que pueden mencionarse;
- condiciones de cierre y debriefing.

La ficha contiene intenciones y restricciones, no frases obligatorias. Así se evita
que todas las conversaciones sean copias léxicas.

El campo `accion_critica` del catálogo fija el pedido riesgoso principal de la semilla. Si una
dramatización agrega otro pedido de una clase distinta, se registra como variante y se anotan ambos
eventos; no se usa ese agregado para atribuir a la fuente un detalle que no documenta.

## 4. Cómo se diseña el negativo difícil

Por cada grupo de semillas fraudulentas se crea al menos un escenario legítimo con
vocabulario y contexto similares, pero conducta segura.

Ejemplo:

| Fraudulenta | Legítima difícil |
|---|---|
| “Soy del banco; decime el código para bloquear la compra” | “Detectamos una compra; no compartas claves y revisá la app oficial” |

El negativo se acepta cuando contiene señales superficiales —banco, urgencia,
seguridad, dinero— sin solicitud secreta, aislamiento ni canal irregular. Esto evita
un detector que solo aprenda palabras obvias.

## 5. Fichas de rol

### Rol A

- Contexto que debe representar.
- Objetivo conversacional.
- Información ficticia disponible.
- Maniobras o conductas permitidas.
- Respuesta ante aceptación, duda y rechazo.
- Conductas excluidas por seguridad.

### Rol B

- Contexto conocido, sin ver el texto del Rol A.
- Actitud asignada: confiado, dudoso o resistente.
- Preguntas que puede hacer.
- Si corresponde, acción ficticia de cumplimiento.
- Condición de cierre.

Los participantes reciben su propia ficha. Una persona del equipo controla que la
grabación respete el escenario y detiene cualquier uso accidental de datos reales.

## 6. Piloto

> **Estado: decisión operativa de Mateo (2026-09-24), pendiente de validación del tutor antes de
> grabar.** Las nueve semillas fraudulentas y los ocho negativos del catálogo son candidatos, no
> grabaciones obligatorias. El 4+4 del [issue #22](https://github.com/Corchets/bitacora_tesis/issues/22)
> era un punto de partida. Se eligen escenarios por cobertura de pedidos críticos, familias y
> negativos comparables. [D06](../gestion/MAPA-DECISIONES.md#d06--definir-la-gobernanza-de-datos)
> sigue abierta hasta que el tutor valide la composición y las condiciones de participación.

1. Elegir semillas fraudulentas que pongan a prueba cada clase de `accion_critica` y diseñar una
   conversación legítima comparable para cada una; un mismo negativo puede tener dos
   interpretaciones con distintos contextos.
2. Estimar minutos de preparación, grabación y anotación con las primeras conversaciones y decidir
   cuántas repeticiones dirigidas hacen falta sin desplazar el resto del proyecto.
3. Transcribirlas y anotar un subconjunto común entre los cuatro integrantes.
4. Registrar ambigüedades, duraciones, fallas técnicas y tiempo de anotación.
5. Revisar taxonomía, fichas y procedimiento.
6. Presentar resultados al profesor antes de escalar.

**Piloto terminado cuando:** cada par de escenarios seleccionado tiene una conversación fraudulenta
y una legítima utilizables, cada etiqueta tiene definición y ejemplo, los desacuerdos principales
fueron adjudicados y puede estimarse el costo de producir/anotar una conversación adicional. El
piloto prueba el procedimiento; no permite estimar con precisión la eficacia del detector.

### Selección inicial del piloto

Mateo seleccionó el 2026-09-24 una primera pasada de **14 conversaciones** (siete fraudulentas y
siete legítimas) para cubrir las seis clases de pedido crítico y las seis familias vigentes. No fija
una cuota para el corpus final. Después de revisar esas tomas, se podrán hacer **hasta seis
repeticiones dirigidas** solo para corregir una grabación inutilizable o investigar una ambigüedad
observada. El máximo de planificación es **20 conversaciones**; no hay obligación de completarlo.
Antes de grabar, el tutor debe validar esta selección y el protocolo de participación.

| Fraudulenta | Legítima comparable | Cobertura principal |
|---|---|---|
| `SC-WA-CODE-01` | `LG-WA-CONSULTA-01` | `REQUEST_AUTH_CODE`; familia WhatsApp |
| `SC-SOPORTE-CLAVE-01` | `LG-SUPPORT-INFO-01` | `REQUEST_SECRET`; familia soporte |
| `SC-ORG-BENEFICIO-01` | `LG-ORG-TURNO-01` | `REQUEST_PERSONAL_DATA`; familia organismo previsional |
| `SC-PREMIO-01` | `LG-PREMIO-CONSULTA-01` | Segunda situación de datos personales; familia premio |
| `SC-CLAVE-CAMBIO-01` | `LG-BANK-VERIF-01` | `REQUEST_SECURITY_ACTION`; familia banco |
| `SC-FAMILIAR-DINERO-01` | `LG-FAMILIAR-LLAMADO-01` | `REQUEST_TRANSFER`; familia familiar |
| `SC-SOPORTE-REMOTO-01` | `LG-SUPPORT-INFO-01` | `REQUEST_REMOTE_ACCESS`; otra interpretación del negativo de soporte |

El negativo de soporte se grabará en **dos interpretaciones**, una frente a contraseña y otra
frente a acceso remoto: son siete conversaciones legítimas aunque haya seis IDs distintos. Las
semillas `SC-BANK-OTP-01` y `SC-BANK-BILLETES-01` siguen en el catálogo para ampliar el corpus;
quedan fuera solo de este piloto porque su clase de pedido y la familia bancaria ya
están representadas. Si en la primera prueba esa elección oculta errores relevantes, se reabre la
selección antes de escalar.

### Resguardo y consentimiento del piloto

> **Estado: decisión operativa de Mateo (2026-09-24), pendiente de validación del tutor.** La PR
> documental puede integrarse antes de esa reunión, pero **no habilita grabaciones**. El equipo
> llevará al tutor la composición, la participación y este resguardo; registrará cualquier cambio
> antes de invitar voluntarios.

- Participarán personas adultas del equipo y colaboradores de confianza. Los diálogos usarán datos
  100% ficticios, pero las voces seguirán siendo datos vinculables a personas. Mateo invitará a
  los cuatro integrantes y buscará dos personas adultas conocidas más, sin asumir que aceptarán.
  Para las 14 primeras conversaciones se asignarán IDs de hablante fuera de Git y se alternarán
  parejas y roles A/B, procurando que cada voz aparezca en casos fraudulentos y legítimos. Si hay
  menos de seis voces disponibles, se registrará la menor diversidad como límite del piloto.
- Ambos interlocutores aceptarán por separado antes de cada grabación mediante el
  [modelo de consentimiento informado](CONSENTIMIENTO-INFORMADO.md). Cada conversación llevará un
  ID interno para facilitar pedidos de acceso o eliminación sin incorporar nombres al dataset;
  perder el ID no impide hacer un pedido. Cada persona recibirá copia o constancia con ID y contacto.
- **Mateo Antenucci será el responsable del archivo de datos del piloto y su custodio operativo.**
  Mantendrá el único resguardo de audio y transcripciones vinculables en almacenamiento local
  cifrado, fuera de Git y de nubes personales.
  No habrá respaldo adicional; solo los cuatro integrantes podrán acceder cuando sea necesario
  para transcribir, anotar o controlar calidad. Los consentimientos firmados y la relación entre
  nombre e ID se guardarán en una carpeta cifrada separada, accesible solo a Mateo. Cualquier copia
  de trabajo deberá volver al resguardo o eliminarse al terminar la tarea; Mateo llevará una
  relación local de copias y derivados por ID para poder atender retiros.
  No se dará acceso al tutor sin informarlo previamente a los participantes.
- La persona podrá pedir acceso o retirar su participación por el contacto entregado antes de
  grabar. Mateo localizará la conversación por ID o por nombre en la relación separada y eliminará
  la conversación completa —incluidas ambas voces—, su transcripción, anotaciones vinculables,
  copias de trabajo y consentimientos firmados; comunicará el retiro a quienes
  hayan recibido una copia. Antes de grabar se completarán y probarán el contacto y el domicilio
  del responsable en el formulario, sin publicar datos privados en Git.
- Se eliminarán audio, transcripciones vinculables y copias **dentro de los 30 días posteriores a
  la defensa o aprobación final de la tesis y, en cualquier caso, no después del 2027-06-30**.
  Los consentimientos firmados se conservarán solo por ese mismo plazo. Los 30 días permiten atender
  correcciones inmediatas de la defensa; el límite absoluto evita una conservación indefinida si
  aquella se retrasa. Si llega el 2027-06-30 sin defensa, se elimina igualmente el material
  vinculable; conservarlo más tiempo exigiría una nueva decisión y nueva información/aceptación
  antes de esa fecha.
- El permiso del piloto **no** cubre publicar voces ni el corpus completo. La difusión se limitará
  a resultados agregados, metadatos disociados y fragmentos ficticios no identificables; cualquier
  uso más amplio requerirá una decisión y autorización específicas.

## 7. Cómo se determina el tamaño final

No existe una cifra universal de 120–200 llamadas. Se decide después del piloto
usando diversidad, incertidumbre estadística, curva de aprendizaje y capacidad.

Bandas de planificación:

| Nivel | Conversaciones | Uso |
|---|---:|---|
| Piloto | 14 iniciales; hasta 20 si hacen falta repeticiones dirigidas | corregir método; no reportar como evaluación final |
| Mínimo defendible | 60–80 | baselines y evaluación exploratoria con límites explícitos |
| Objetivo | 100–120 | más diversidad y un test menos inestable |
| Extensión | 160–200 | solo si producción y anotación ya son sostenibles |

Después del piloto se estima:

- minutos para grabar, transcribir y anotar una conversación;
- cobertura por familia, semilla, hablante, actitud y condición acústica;
- intervalo de confianza de métricas clave;
- curva de aprendizaje al agregar datos;
- semanas disponibles antes de congelar el test.

**Criterio de parada:** se alcanza al menos el mínimo acordado, cada familia central
tiene cobertura suficiente, existe test independiente, la curva de aprendizaje se
aplana o producir más datos desplaza la integración/evaluación crítica. El número
final y sus límites se documentan; no se inventa una justificación retrospectiva.

## 8. Balance

El 50/50 es una decisión experimental inicial, no una estimación de prevalencia
real. Facilita comparar clases en un corpus pequeño. El test puede incluir 50/50
para medir capacidad discriminativa y una evaluación adicional con menor
prevalencia para observar falsas alarmas.

Las conversaciones fraudulentas y legítimas no se “consiguen”: el equipo las
produce mediante el catálogo y las fichas. Fuentes externas justifican modalidades;
no aportan llamadas listas para usar.

## 9. División de datos

1. Agrupar todas las variantes derivadas de una misma semilla.
2. Distribuir semillas completas entre train, validation y test.
3. Mantener las familias centrales representadas en los tres splits cuando sea
   posible.
4. Reservar hablantes del test si el tamaño lo permite; si no, reportar una segunda
   evaluación speaker-disjoint o la limitación.
5. Congelar el test antes de seleccionar modelo y umbral.

**Split terminado cuando:** ningún audio, turno ni paráfrasis de una semilla cruza
particiones, y un script valida esa condición.

## 10. Control de calidad

Una grabación se acepta cuando:

- se acuerda la participación voluntaria con datos 100% ficticios;
- no se utilizan datos de víctimas ni información real;
- respeta la ficha sin ser una lectura mecánica;
- ambos lados son inteligibles;
- tiene ID, semilla, hablantes pseudónimos y condición acústica;
- puede anotarse `T_R` y, cuando corresponda, `T_C`;
- no contiene datos identificatorios reales adicionales en el diálogo o los metadatos; la voz se
  resguarda como dato personal aun cuando el guion sea ficticio.

Las exclusiones se registran con motivo; nunca se eliminan silenciosamente para
mejorar métricas.
