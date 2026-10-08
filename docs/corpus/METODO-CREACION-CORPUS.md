# Método de creación del corpus

El equipo producirá conversaciones simuladas para probar la detección incremental de
vishing. Este documento explica cómo prepararlas, grabarlas y decidir cuánto ampliar
el corpus. Las modalidades y sus fuentes viven en el
[catálogo de escenarios](CATALOGO-ESCENARIOS.csv); las etiquetas, en el
[manual de anotación](MANUAL-ANOTACION.md); las medidas, en [METRICAS.md](../evaluacion/METRICAS.md).

## 1. Unidad del corpus

- **Familia:** modalidad amplia, por ejemplo banco o soporte técnico.
- **Semilla:** situación concreta a representar.
- **Ficha de rol:** objetivos y límites de cada interlocutor.
- **Conversación:** una interpretación de una semilla.
- **Turno:** intervención de un hablante. No exige una ficha de anotación por turno.

Cada conversación conserva su clase y su vínculo con la semilla. Sus turnos y
fragmentos permanecen juntos al dividir los datos.

## 2. De dónde salen las llamadas

Primero se identifica una modalidad en fuentes oficiales argentinas, alertas de
entidades financieras reguladas o literatura académica. Después se diseña una
situación ficticia y una contraparte legítima comparable. La fuente respalda la
modalidad o la conducta segura; no prueba que el diálogo inventado haya ocurrido.

El catálogo contiene los escenarios concretos. Para mantenerlo:

| Campos | Uso |
| --- | --- |
| `scenario_id`, `familia`, `clase`, `titulo` | Identificación estable: `SC-` para vishing y `LG-` para legítima difícil. |
| `fuente` | Afirmación respaldada, URL y fecha de consulta; distinguir el diseño ficticio. |
| `identidad_suplantada_o_contexto`, `objetivo` | Contexto y propósito de la llamada. |
| `maniobras`, `accion_critica` | Etiquetas del manual: maniobras separadas por `;` y pedido riesgoso principal; `NONE` en legítimas. |
| `negativo_pareado` | ID de una contraparte comparable. Puede reutilizarse y el vínculo no tiene que ser recíproco. |
| `estado`, `notas` | Revisión, límites de la fuente, datos ficticios y motivos de descarte. |

Los estados son `borrador` (incompleto), `con_fuente` (respaldo identificado),
`revisado` (fuente, pertinencia, pareo y seguridad contrastados bajo responsabilidad
de otro integrante) y `descartado` (se conserva el motivo). Estar revisado no implica
que el escenario ya se haya grabado.

## 3. Cómo se diseña una semilla fraudulenta

Se parte de la fila del catálogo y se prepara una ficha con identidad suplantada,
pretexto, objetivo, maniobras, pedido riesgoso, datos ficticios y respuestas posibles
ante duda, aceptación o rechazo. También se define cómo terminar la conversación.

La ficha orienta la actuación sin imponer frases obligatorias. Se prevé un pedido y
un posible cumplimiento simulado; sus marcas temporales se anotan después sobre lo
que efectivamente se grabó. Si aparece otro pedido riesgoso, se registra como variante
y se anota, sin atribuir ese detalle a la fuente original.

## 4. Cómo se diseña el negativo difícil

Se usa un contexto y vocabulario similares al fraude, con una conducta legítima.
Por ejemplo, frente al pedido de un código bancario, una llamada que recomienda no
compartirlo y revisar la aplicación oficial. Así se comprueba si el detector distingue
el pedido peligroso de la mera mención de banco, código o dinero.

Un negativo puede servir a varias semillas. Cada interpretación conserva su propio
ID de conversación y su vínculo con el escenario.

## 5. Fichas de rol

El **rol A** recibe contexto, objetivo, información ficticia, conductas permitidas y
respuestas ante aceptación, duda o rechazo. El **rol B** recibe su contexto y actitud
(confiada, dudosa o resistente), posibles preguntas y, si corresponde, una acción
ficticia de cumplimiento. Ambos conocen la condición de cierre.

Cada participante recibe su ficha, sin leer la de la otra persona. Una persona del
equipo controla la grabación y la detiene si aparecen datos reales o acciones fuera
de la simulación.

## 6. Piloto

La selección está acordada en [D06](../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto).
El piloto sirve para probar el procedimiento y estimar su costo; no es la evaluación
final de eficacia del detector. El [primer par (#39)](https://github.com/Corchets/bitacora_tesis/issues/39) prueba el procedimiento;
el [piloto completo (#54)](https://github.com/Corchets/bitacora_tesis/issues/54) reúne las 14 conversaciones.

1. Preparar las fichas de los pares seleccionados.
2. Grabar la primera pasada y medir el tiempo de preparación y grabación.
3. Obtener y revisar la transcripción; completar la referencia mínima por conversación
   según el manual. Los cuatro anotan independientemente una muestra común y se mide
   ese esfuerzo.
4. Comparar anotaciones y registrar ambigüedades y fallas técnicas.
5. Ajustar fichas, manual y procedimiento; usar repeticiones dirigidas si hacen falta.

**Piloto terminado cuando:** cada par tiene una conversación fraudulenta y una
legítima utilizables, los principales desacuerdos del subconjunto común están
adjudicados y se puede estimar el costo de producir y anotar otra conversación.
Probar el piloto no cierra automáticamente D07: hay que revisar las reglas de marcado,
los desacuerdos y las etiquetas efectivamente usadas para describir evidencia.

### Selección inicial del piloto

La selección inicial comprende **14 conversaciones: siete fraudulentas
y siete legítimas**. Cubre las seis clases de pedido crítico y las seis familias del
catálogo actual.

| Semilla fraudulenta | Legítima comparable |
| --- | --- |
| `SC-WA-CODE-01` | `LG-WA-CONSULTA-01` |
| `SC-SOPORTE-CLAVE-01` | `LG-SUPPORT-INFO-01` |
| `SC-ORG-BENEFICIO-01` | `LG-ORG-TURNO-01` |
| `SC-PREMIO-01` | `LG-PREMIO-CONSULTA-01` |
| `SC-CLAVE-CAMBIO-01` | `LG-BANK-VERIF-01` |
| `SC-FAMILIAR-DINERO-01` | `LG-FAMILIAR-LLAMADO-01` |
| `SC-SOPORTE-REMOTO-01` | `LG-SUPPORT-INFO-01` |

El negativo de soporte tiene dos interpretaciones: una comparable al pedido de
contraseña y otra al de acceso remoto. Los demás escenarios siguen disponibles en
el catálogo, sin obligación de grabarlos todos.

Después de revisar las tomas se admiten **hasta seis repeticiones dirigidas** para
reemplazar una grabación inutilizable o estudiar una ambigüedad. No hay obligación
de llegar a 20 ni una cuota implícita para el corpus final.

### Resguardo y consentimiento del piloto

- Participan personas adultas del equipo o familiares, voluntariamente. Ambos
  interlocutores conocen el propósito y aceptan la grabación antes de empezar.
  Se usan únicamente datos ficticios y acciones simuladas.
- Se identifican conversaciones y hablantes con IDs, sin nombres reales en los
  metadatos del corpus. Se alternan parejas y roles cuando sea posible y se registra
  la diversidad realmente obtenida, sin exigir una cantidad fija de participantes.
- Se mantiene el resguardo local de audios y transcripciones vinculables,
  fuera de Git. El acceso queda limitado al equipo para el trabajo del corpus.
  Si alguien retira su participación, se eliminan la conversación completa y sus
  derivados vinculables, incluidas las copias de trabajo.
- Se conserva el plazo de eliminación previsto: dentro de los 30 días posteriores
  a la defensa o aprobación final y, como máximo, hasta el 2027-06-30.
- Esta participación no autoriza publicar las voces ni el corpus completo. Pueden
  compartirse resultados agregados, metadatos disociados y fragmentos ficticios
  no identificables. La publicación del corpus sigue pendiente en el mapa de decisiones.

## 7. Cómo se determina el tamaño final

**No hay un “mínimo defendible” de conversaciones fijado.** El número final se
justificará con lo aprendido en el piloto y con la evaluación que se quiera sostener.

Antes de ampliar, el equipo debe revisar:

- costo real de preparación, grabación, transcripción y anotación;
- cobertura de semillas, clases, hablantes y condiciones de grabación;
- cantidad de ejemplos que quedarían para una evaluación independiente;
- incertidumbre de las métricas y alcance de las conclusiones posibles;
- tiempo disponible para implementar, evaluar y preparar la demostración.

El tamaño, la composición y el criterio de parada deben acordarse en [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)
antes de la evaluación final. Si se entrena un modelo, podrá analizarse cuánto mejora
al agregar datos. El número obtenido y las limitaciones se informan sin justificarlo
retrospectivamente por los resultados favorables.

## 8. Balance

El piloto tiene igual cantidad de conversaciones fraudulentas y legítimas. Ese
balance no representa la frecuencia de estafas en llamadas reales. La composición
del corpus final y del test todavía se debe fijar en D08.

Las siete legítimas sirven para descubrir errores del procedimiento y del detector,
pero no para demostrar una tasa baja de falsas alarmas: cada llamada con un aviso
incorrecto representa 1 de 7. Incluso si no aparece ninguno, el resultado no prueba
que las falsas alarmas sean raras en el uso cotidiano. La interpretación de la
precisión según la frecuencia de fraude se explica en
[METRICAS.md](../evaluacion/METRICAS.md#balance-y-precisión-de-las-alertas).

> **Estado: propuesta sin discutir.** Para el corpus final, incluir llamadas
> legítimas cotidianas además de negativos difíciles y distinguir sus resultados.
> La composición y cantidad se acuerdan en
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

Las llamadas son simulaciones del equipo y sus familiares. Los resultados permitirán
hablar de ese corpus y sus condiciones; no demostrarán por sí solos protección
efectiva ni rendimiento en la población de adultos mayores.

## 9. División de datos

> **Estado: propuesta sin discutir.** La división definitiva se adopta en
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

El criterio propuesto es separar por **semilla**, manteniendo juntas sus
conversaciones, variantes, paráfrasis y turnos. Distribuir aleatoriamente esos
fragmentos permitiría evaluar sobre situaciones ya vistas durante el desarrollo.

El piloto se usa para ajustar el método y desarrollar el sistema. Para la evaluación
final se reservan semillas que no se usen para elegir modelo, reglas, umbrales ni
política de alerta. Si se entrena un modelo, se separan entrenamiento, validación y
test; sus proporciones siguen pendientes.

Grabar más interpretaciones de las mismas semillas no agrega escenarios independientes
para test. Al ampliar el corpus habrá que revisar si quedan semillas suficientes para
evaluar las clases y familias que se pretende cubrir.

También se revisa qué familias y hablantes comparten las particiones. Si no se pueden
reservar hablantes nuevos para test, se declara esa limitación. La división queda
lista cuando se registra la asignación de IDs y se verifica que ninguna semilla ni
sus derivados crucen particiones. El test se congela antes de ajustar el sistema y se
consulta para la evaluación final.

## 10. Control de calidad

Cada conversación debe tener aceptación de ambos participantes, datos ficticios,
audio inteligible de ambos lados e identificación de semilla, hablantes por ID y
condición de grabación. Se conserva la relación entre audio, transcripción y anotación.

Las marcas se anotan según el manual y las métricas: si no hubo cumplimiento
observable, `T_C` queda sin dato. Un caso ambiguo se registra para adjudicación; no se
inventa una marca para completar la planilla.

Las exclusiones y sus motivos se registran. Una llamada sin alerta o sin cumplimiento
no se descarta por ese motivo: se trata como indica [METRICAS.md](../evaluacion/METRICAS.md).
