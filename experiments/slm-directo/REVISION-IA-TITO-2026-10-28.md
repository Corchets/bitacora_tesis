# Revisión técnica asistida de datos de Tito — 2026-10-28

**Antecedente focalizado de 14 casos.** La [curación completa de 150 conversaciones y 6.000 realizaciones](CURACION-TITO-2026-10-28.md) amplía esta entrega y contiene la selección vigente.

**Dictamen:** los ejemplos revisados sirven para calibrar la anotación; todavía
no constituyen datos habilitados para entrenar o comprobar candidatos en #99/#100.
La revisión encuentra una diferencia de codificación relevante para la supervisión,
cuatro ambigüedades de criterio y un límite de evidencia disponible por prefijo.
No corresponde cerrar [#96](https://github.com/Corchets/bitacora_tesis/issues/96)
como completado con esta entrega.

Se aplicó el criterio de revisión senior solicitado por el usuario. Revisor:
**Codex, IA**, sin atribuirle credenciales profesionales, participación de personas
ni acuerdos del equipo. Se leyeron referencias y auditorías: no fue anotación ciega
ni independiente de esas propuestas. No se simularon cuatro revisores humanos.

> **Estado: propuesta sin discutir.** Las recomendaciones y referencias propuestas
> requieren acuerdo local de
> [D07](../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
> No se modificaron los textos ni los JSON autorales, ni `revision_humana`.

## Alcance y evidencia entregada

- Revisión semántica de los **12 casos candidatos** de
  [DATOS-TITO.md](DATOS-TITO.md#lista-común-candidata-para-acordar), más
  [TR-08](casos/texto/TR-08-frase-cortada-candado.txt) y
  [TR-06](casos/texto/TR-06-banco-alerta-legitima.txt) como contrastes adicionales.
  Esto no cambia ni aprueba la muestra humana pendiente.
- Control estructural de **150 conversaciones de desarrollo** y auditoría del
  banco histórico por API: 6.000 registros, 5.520 aceptados, 480 apartados,
  276 familias aceptadas. No se afirma revisión semántica de los 150 ni del banco.
- [Registro de revisión IA](REVISION-IA-TITO-2026-10-28.json): por cada uno de los
  14 casos conserva huellas de originales, citas exactas con línea, fundamento,
  referencia propuesta, alternativas y dificultad candidata. Es la fuente de los
  juicios por caso; este informe sintetiza sus consecuencias.
- [Control regenerable](CONTROL-REVISION-IA-TITO-2026-10-28.json), producido por
  [auditar_revision_tito.py](auditar_revision_tito.py): inventario y huellas de los
  150 pares, controles de referencias originales y propuestas, ejemplos reales
  de la API y rechazo de habilitación. Todos en `regresion` **solo para comprobar
  estructura**, sin proponer ni afirmar un split experimental.

Se usaron el [manual](../../docs/corpus/MANUAL-ANOTACION.md), el
[formato de casos](casos/README.md) y las
[métricas](../../docs/evaluacion/METRICAS.md). La reserva no se leyó ni copió.
No hubo entrenamiento, inferencia de detectores ni mediciones de calidad aprendida.
Las marcas son líneas; no hay segundos ni márgenes preventivos inventados.

## Resultado de la lectura

En los 12 candidatos, ocho referencias de clase y marcas son compatibles con la
lectura técnica y cuatro requieren un criterio explícito. «Compatible» no significa
validado por personas, auténtico ni apto para evaluación independiente. Los dos
contrastes adicionales exponen límites de interpretación incremental. No se propone
cambiar ninguna clase final ni `T_C` en estos 14 casos; sí ampliar evidencia en
cuatro, con propuestas separadas de los originales.

| Caso con criterio pendiente | Recomendación del revisor IA | Alternativa o límite |
|---|---|---|
| [TR-02](casos/texto/TR-02-codigo-del-candado.txt) | Mantener legítima y marcas críticas nulas; el código es de un candado, no OTP. | Una combinación física puede proteger bienes: no llamarla «no sensible» por defecto. Acordar si entra en `REQUEST_SECRET` como etiqueta descriptiva; eso no vuelve fraudulenta la conversación. |
| [TR-07](casos/texto/TR-07-pedido-partido-en-dos-lineas.txt) | `T_R=7`, inicio de solicitud indirecta del mensaje identificado en L5–6; `T_C=9`. | L8 identifica explícitamente seis números. `T_R=8` es la alternativa si se exige esa desambiguación; diferencia de una línea en el margen. |
| [TR-10](casos/texto/TR-10-ofrecimiento-inducido.txt) | `T_R=8`, porque pide confirmar el contenido del SMS ya identificado; `T_C=13`. | L10 precisa cargarlo del lado del llamante; L12 acepta la oferta. L11 es oferta de quien recibió el SMS y no debe anotarse como pedido del llamante. |
| [CV2-D-V-WHATSAPP-006](casos/texto/CV2-D-V-WHATSAPP-006.txt) | `T_R=25` como comienzo retrospectivo y desambiguación en L26; `T_C=31`. | L25 termina en «pasame»; L26 explicita el objeto. Conservar alternativa `T_R=26`, sin atribuir a L25 lo que recién dice L26. |

Las recomendaciones no adjudican D07: dejan identificado el valor preferido, el
motivo y cuánto cambia la referencia con otra lectura. Para los casos de petición
partida, agregar a la evidencia el antecedente del mensaje y su continuación evita
que el registro muestre solo una frase incompleta. En CV2-D-V-BANCO-001 se propone
agregar L29/31/33: aviso de acceso a cuenta, objeción y rechazo; el pedido de L32
sigue siendo la marca defendible y no se observa cumplimiento.

## Hallazgo principal: pedido literal y objetivo de derivación

**Prioridad alta antes de #99.** En las 150 referencias, 13 legítimas tienen
`evento: pedido`; 15 legítimas contienen alguna etiqueta `REQUEST_*` en evidencia.
Los conjuntos difieren y se enumeran en el control JSON. Esto es admisible como
anotación descriptiva: un pedido sensible puede ser legítimo. El problema aparece
si se transforma mecánicamente esa evidencia en el objetivo de Tito.

Comprobación sobre la API existente, sin modelos:

| Caso / prefijo | Referencia final | Estado derivado por `etiquetar_prefijo()` |
|---|---|---|
| CV2-D-L-SOPORTE-001, hasta L6: pide domicilio para visita | legítima, `T_R=null` | `pedido_visible` |
| TR-13-turno-medico-pide-dni, hasta L5: pide DNI/fecha para turno | legítima difícil, `T_R=null` | `indicio_parcial` |

El primero codifica la solicitud como `pedido`; el segundo como `contexto`.
**No es evidencia de un fallo del clasificador** ni demuestra que la API vio el
futuro. Demuestra que el estado depende de convenciones heterogéneas del corpus.
Tampoco corresponde convertir todo `indicio_parcial` en positivo: puede surgir de
una advertencia o un contexto legítimo.

Recomendación propuesta: mantener separados clase final, acto literal, marca
crítica y objetivo de derivación. Antes de entrenar, definir cuándo conviene
consultar al SLM y cómo se supervisa con lo visible. No resolverlo borrando pedidos
legítimos ni copiando la clase final a cada prefijo. La política concreta continúa
pendiente en D07/D08; esta revisión no fija un nuevo umbral ni un clasificador.

## Hallazgo incremental: el futuro puede aclarar un prefijo ambiguo

**Prioridad alta para la supervisión por prefijo.** En TR-08, L3 dice «Pasame el
código» y L4 lo completa con el candado de una valija. La referencia final marca
L3 como contexto y la API devuelve `indicio_parcial`. La especificación del objeto
físico de L4 no existía al terminar L3. En TR-07 el objeto bancario se precisa en
L8, y en CV2-D-V-WHATSAPP-006 la frase se completa en L26.

Recomendación propuesta: conservar el comienzo del evento como marca retrospectiva
cuando corresponda y registrar aparte qué evidencia ya podía interpretarse en
cada prefijo. No penalizar una derivación prudente solo por conocer después el
final legítimo, ni entrenar una certeza online utilizando ese final. Cómo convertir
la ambigüedad en objetivo de derivación necesita acuerdo; no se adopta una nueva
clase ni etiqueta en el vocabulario del corpus.

## Cobertura y procedencia que siguen limitando el uso

Hay 11 vishing sin pedido marcado entre las 150 referencias (incluido TR-12).
Es un conteo del estado actual, no una conclusión de intención observable ni una
razón para excluirlos automáticamente del denominador. Sin `T_R` no se calcula
margen respecto de ese evento. La revisión semántica de 14 no cubre esos 11.

Los 12 candidatos cubren pedidos legítimos, negación/consejo, cita hipotética,
pedidos indirectos, evidencia repartida y conversaciones largas. Falta un relato
retrospectivo desarrollado, revisión de accesos remotos, fraudes sin pedido y
cumplimientos parciales. Los dos contrastes no subsanan toda esa cobertura.

Los ocho antecedentes de la demo siguen siendo regresiones; aquí aparecen cuatro
(SC-WA, LG-WA, TR-02 y el contraste TR-08). Los otros antecedentes y los tres CV2
leídos no reciben independencia por cambiarles el nombre o la partición. Faltan
procedencia y parentesco contrastados contra el ajuste histórico y las corridas
previas. No se seleccionaron entrenamiento, validación, diagnóstico ni evaluación
independiente. La evaluación posterior no se abre para resolver estas dudas.

## Verificación y cómo continuar

Desde `experiments/slm-directo/`:

```bash
python casos.py
python auditar_revision_tito.py > /tmp/CONTROL-REVISION-IA-TITO.json
cmp CONTROL-REVISION-IA-TITO-2026-10-28.json /tmp/CONTROL-REVISION-IA-TITO.json
```

El script verifica las huellas de textos y referencias de los casos revisados,
las citas y el formato de las propuestas junto con el inventario completo; falla
si una propuesta IA afirma revisión humana. Rechaza IDs reservados antes de abrir
su contenido. Sus conteos son automatizados; no genera juicios semánticos nuevos.
Verificación del 2026-10-28: 150 casos válidos; regeneración del control idéntica
byte a byte; 50 pruebas de `tests.test_datos_tito` verdes. Tres comprobaciones
negativas rechazaron huella alterada, propuesta IA marcada como humana y presencia
de un ID reservado ficticio antes de parsear su archivo. Se usaron copias
temporales; los datos originales no se alteraron. Enlaces locales comprobados.

El control devuelve `habilitado:false`: no se aportan revisión humana ni acuerdo
ficticios para pasar la puerta. Un control estructural sin errores no habilita uso.

**Para aprovechar este trabajo:** la revisión humana puede concentrarse primero en
los cuatro criterios señalados y en contrastar solicitudes legítimas comparables.
Debe conservar sus propios originales y resolver acuerdos de referencia y
particiones. Revisar solo los cuatro casos tampoco satisface por sí solo #96 ni
la muestra común pendiente. Si se quiere continuar únicamente con IA, hace falta
aprobar explícitamente otro alcance de experimento exploratorio y reformular los
criterios afectados en GitHub; no se lo registra como validación humana ni como
comparación independiente ya habilitada.

## Comentario preparado para #96 — avance, sin cierre

```markdown
Revisión técnica asistida por IA disponible en
`experiments/slm-directo/REVISION-IA-TITO-2026-10-28.md`.

- Lectura de 12 candidatos y 2 contrastes; registro por caso con huellas, citas,
  referencia propuesta y alternativas conservado en el JSON enlazado.
- Control estructural regenerable de los 150 de desarrollo y procedencia del banco.
- Hallazgo: 13 legítimas con evento pedido; casos comparables producen estados de
  supervisión distintos. Falta acordar el objetivo de derivación antes de #99.
- Cuatro ambigüedades documentadas: alcance del secreto físico e inicio de pedidos
  indirectos/partidos. Recomendaciones explícitas, sin adjudicación humana ficticia.
- Sin cambios en originales, reserva, entrenamiento ni inferencia. Habilitado=false.

#96 continúa parcial. Próxima acción: aportar anotaciones humanas originales y
acuerdos locales de referencia/particiones; o aprobar expresamente una reformulación
exploratoria asistida por IA con sus límites, sin declarar cumplidos los criterios
actuales. No se solicita cerrar el issue con esta evidencia.
```
