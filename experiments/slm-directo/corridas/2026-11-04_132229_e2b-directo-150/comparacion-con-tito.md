# Gemma 4 E2B solo contra Tito viejo → E2B: comparación y fallos

**Revisión ampliada:** 2026-11-04, rama `laboratorio-luciano`. Evidencia de desarrollo para
[#51](https://github.com/Corchets/bitacora_tesis/issues/51) y
[#68](https://github.com/Corchets/bitacora_tesis/issues/68); ambos siguen abiertos.
Se cruzan las dos corridas, las estafas perdidas, las falsas alarmas y los aportes de
Ignacio y Evaristo. No se ejecutó inferencia nueva.

Las referencias de los 150 casos conservan `revision_humana: false`. Los recuentos
usan esas referencias, no adjudican clase ni marcas y no estiman rendimiento final.
D07 y D08 siguen abiertas; D09 está resuelta desde el 2026-11-03. Cualquier cambio al
detector requiere reconsiderar el [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Resultado comparable

| Medida | SLM solo | Tito viejo → SLM |
|---|---:|---:|
| Estafas con aviso | 55/75 (73,3 %) | 51/75 (68,0 %) |
| Con pedido de referencia | 54/64 (84,4 %) | 51/64 (79,7 %) |
| Sin pedido de referencia | 1/11 | 0/11 |
| Falsas alarmas, todas las legítimas | 18/75 (24,0 %) | 13/75 (17,3 %) |
| Falsas alarmas, comunes | 3/51 (5,9 %) | 5/51 (9,8 %) |
| Falsas alarmas, difíciles | 15/24 (62,5 %) | 8/24 (33,3 %) |
| Aviso anterior / en / posterior a T_R | 25 / 25 / 4 | 17 / 29 / 5 |
| Líneas procesadas | 2.218 | 2.318 |
| Consultas al SLM | 2.218 | 1.179 |
| Líneas omitidas por la compuerta | 0 | 1.139 |
| Mediana de consulta al SLM (`slm_ms`) | 290,8 ms | 309,4 ms |
| Fallos técnicos o respuestas inválidas | 0 | 0 |

**Quitar Tito suma cuatro estafas y cinco falsas alarmas netas.** No hay una mejora
general: en legítimas comunes el directo mejora, en las difíciles empeora. Ninguna
condición alcanza la meta del tutor de 80–85 % de estafas con 10–15 % de falsas alarmas.
El denominador de estafas es 75; el de falsas alarmas sigue pendiente en D08. Se
muestran 75, 51 y 24 sin elegir uno como criterio de aceptación.

Con denominador 75, el piso de detección exige 60 avisos y el techo de 15 % permite
como máximo 11 falsas alarmas: a Tito → E2B le faltan nueve avisos y le sobran al
menos dos falsas alarmas; al directo, cinco y siete. Son brechas sobre desarrollo.
Si se mantuvieran sin aviso las once sin pedido, rescatar las trece con pedido
llevaría a 64/75 (85,3 %): recuperar nueve de esas trece alcanza 60/75.

## Procedencia, integración y reproducción

| Fuente | Ubicación y alcance verificado |
|---|---|
| Tito → E2B, Windows | [Manifiesto](../2026-11-04_003715_e2b-tito-viejo-150/manifiesto.json), [CSV](../2026-11-04_003715_e2b-tito-viejo-150/actualizaciones.csv) y [análisis](../2026-11-04_003715_e2b-tito-viejo-150/analisis.md). Carpeta integrada en `laboratorio-main` por PR #137; la rama de corrida fue borrada. |
| E2B solo, Windows | [Manifiesto](manifiesto.json) y [CSV](actualizaciones.csv). Integrados por PR #138. |
| Ignacio, Colab | [Procedimiento y notebook](../../colab/README.md), commit `b408257`, integrado por PR #135 y ya presente en esta rama. Ejecuta Tito → E2B y reglas; omite SLM directo. No hay otra salida cruda de Colab en esta carpeta que permita calcular una tercera comparación. |
| Evaristo, riesgo primero | [Informe y R3](../../analisis/2026-10-29-riesgo-primero/README.md), ya integrados; modelo Gemma **3n**, no Gemma 4. |

Tras `git fetch origin`, `origin/nacho1706/analisis-corrida-e2b-tito`
y `origin/laboratorio-corcho4` no tienen commits pendientes
respecto de este HEAD de partida (`a342ca4`). No se hizo otro merge ni se copiaron
resultados en paralelo. `colab` es una carpeta de `experiments/slm-directo`.

Las dos corridas Windows declaran código `833a3fb` con cambios locales sin commit,
Windows 11, 12 núcleos lógicos, 31,9 GB, Python 3.12.10 y Ollama 0.40.14. Coinciden
los 150 IDs y huellas de texto, el prompt `tarea` (`bf4284996898c45d`), hablantes `ab`,
contexto 4096, seed 42 y temperatura 0. Modelo `gemma4:e2b-it-q4_K_M`, digest
`b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2`.
Tito usa umbral 0,5 y conserva el indicio de la primera activación.

**Ambas corridas cortan al primer aviso.** No se usó `--seguir-tras-aviso`: no hay
2.773 respuestas por condición ni se sabe si la alerta se sostendría después. El
SLM directo se detiene, entre otros, antes de T_R en `SOPORTE-001` y `TR-01`.
Tito también termina antes de completar los casos avisados. Comparar primer aviso
es válido; comparar persistencia posterior o ahorro con una trayectoria idéntica
requiere otra corrida. Las 1.039 consultas menos (46,8 %) son la diferencia observada
entre recorridos con distintos puntos de corte; las 1.139 omisiones son el efecto
contabilizado de la compuerta dentro de su propio recorrido.

El wrapper externo de la corrida con Tito no se conservó. No se puede atribuir una
diferencia únicamente al indicio ni separar variación entre ejecuciones: se quitaron
compuerta e indicio juntos. Los tiempos son de esa PC, sin placa identificada;
no son latencia total con ASR ni medición en Android.

[Comparador reproducible](comparar_directo_vs_tito.py), desde `experiments/slm-directo`:

```sh
python -I corridas/2026-11-04_132229_e2b-directo-150/comparar_directo_vs_tito.py corridas/2026-11-04_132229_e2b-directo-150 corridas/2026-11-04_003715_e2b-tito-viejo-150
python -I tests/test_comparar_directo_vs_tito_seguro.py
```

El comparador toma IDs explícitos de ambos manifiestos, rechaza `CV2-T*`, diferencias
de huellas, IDs inseguros, CSV con casos ajenos y corridas incompletas; verifica cada
texto antes de cargar su referencia. No importa `casos.py`, no enumera `casos/texto`
ni `casos/referencia`, ni abre el catálogo. La versión anterior llamaba
`ids_de_casos("desarrollo")`, que abría referencias reservadas para filtrarlas; no
se ejecutó esa versión en esta sesión. El ejecutor general `correr.py` y la suite
completa no se ejecutaron: siguen requiriendo una revisión de acceso antes de
usarlos en la copia que contiene la reserva. Las referencias actuales no tienen
huella registrada en los manifiestos de estas corridas; su revisión sigue pendiente.


## Panel para comparar las corridas

El 2026-11-04 se amplió el tablero HTML recibido de Luciano con una pestaña
«Comparar corridas»: los 150 casos, resultados y motivos lado a lado, riesgos por
línea, activación de Tito y marcas T_R/T_C. Distingue omisiones, errores y filas no
evaluadas tras el primer aviso. Incluye filtros para las 24 pérdidas con Tito,
las 19 compartidas, las nueve compartidas con pedido, las 21 falsas alarmas y los
17 cambios de resultado. Las pestañas históricas conservan su lectura con Tito;
las conversaciones se consultan en una única vista comparativa.

Fuentes de la vista: [generador](../../analisis/tablero/comparar_corridas_150.py) y
[plantilla](../../analisis/tablero/comparacion_150_plantilla.html). No hay un tercer
experimento ni nuevas respuestas del modelo. La pestaña «Pasos recomendados»
explica el orden de prueba propuesto, incluido preparar acceso seguro antes de
volver a ejecutar inferencia en una copia que contiene la reserva.

Desde la raíz, usando el HTML original o una salida anterior como base:

```sh
python3 -I experiments/slm-directo/analisis/tablero/comparar_corridas_150.py --base /ruta/tablero.html --salida /ruta/tablero-comparado.html
python3 -I experiments/slm-directo/tests/test_panel_comparacion_150.py
```

La base se copia a una carpeta temporal aislada antes de leerla y el proceso no
importa módulos de esa carpeta. El generador reutiliza el comparador con lista
permitida de manifiestos; no enumera casos ni abre el catálogo. El HTML es
completo, funciona como archivo local y ocupa menos de 512 KB. Las cinco pruebas
del panel verifican regeneración sin duplicados, rechazo de casos ajenos,
escapado del JSON y distinción entre omisión, respuesta, error y corte, y comparación solo de respuestas
observadas. Pasaron
también las seis guardas del comparador. En la versión anterior, en Chrome se comprobaron filtros,
búsqueda sin coincidencias, SOPORTE-001 con filas sin evaluar después de L10 y
navegación a los pasos. La ampliación de diferencias se verificó con cinco pruebas
del panel, seis guardas del comparador y ejecución del JavaScript en un DOM
simulado: 15 filtros, 150 detalles y búsqueda vacía. La comprobación visual de
esta ampliación en Chrome quedó incompleta: la herramienta devolvió el contenido
local en blanco, sin árbol del documento; no se certifica su presentación móvil.

## Primero, los tres casos pedidos

### BANCO-003: entrega física de efectivo

[Texto](../../casos/texto/CV2-D-V-BANCO-003.txt) ·
[Referencia](../../casos/referencia/CV2-D-V-BANCO-003.json).
El supuesto banco presenta un recambio preventivo. La persona dice en L14:
«Me estás diciendo que le dé efectivo a alguien que no conozco». En L17 aparece
«Mañana ya no puedo garantizar que acepten esa serie en caja». En **L19** el llamante
ordena: «Todo lo que tengas de esa numeración prepará el sobre y entregáselo al
operador». En L26 la persona confirma la entrega (`T_C`).

Tito activó en L5. E2B fue consultado en L19 y respondió `alerta_sugerida: false`,
riesgo **0,3 en ambas condiciones**; no avisa ni en L26 (riesgo 0,5 con Tito, 0,3 solo).
No es un pedido meramente condicional y no hay un bloqueo de compuerta en T_R.
El prompt ya incluye «entregas de dinero o efectivo». **Observación:** el SLM no
reconoce este pedido con el prompt vigente. **Hipótesis:** interpreta el recambio
como trámite; las respuestas negativas no dan motivo y no prueban esa explicación.
Una mejora debe contrastarse con entregas y repartos legítimos para no disparar
por cualquier sobre, mensajero o pago.

### PREMIO-003: documento y foto como requisito de entrega

[Texto](../../casos/texto/CV2-D-V-PREMIO-003.txt) ·
[Referencia](../../casos/referencia/CV2-D-V-PREMIO-003.json).
La participante recuerda que el premio se retiraba en la feria (L6). En **L13** se
pide el número de documento y se condiciona conservar el premio a completarlo;
en **L19**: «Anotá el número en esa ficha y agregá la foto del frente para que no lo
carguen mal». El remitente distinto aparece en L20 y se desalienta consultar a la
biblioteca en L23. No hay cumplimiento.

Tito activó en L3. En L13 E2B da **0,1 en ambas condiciones**, sin alerta. En L19 da
0,1 con Tito y 0,2 solo, sin alerta; tampoco avisa después. El prompt ya enumera DNI
y foto de documento. El fallo persiste incluso al llegar al pedido explícito de L19.
La referencia deja abierta la ubicación de T_R entre L13 y L19 y exige revisar la
clase: **un pedido de DNI por sí solo no demuestra estafa**. Mover T_R no cambia el
conteo de conversaciones sin aviso. La revisión debe confrontar este caso con el
turno médico `TR-13`, donde sí avisa por DNI y fecha de nacimiento.

### SOPORTE-005: contraseña anterior ingresada en una ventana

[Texto](../../casos/texto/CV2-D-V-SOPORTE-005.txt) ·
[Referencia](../../casos/referencia/CV2-D-V-SOPORTE-005.json).
Aquí **B** representa al supuesto soporte; A es la persona protegida. B guía la
recuperación de cuenta en L10. A lee «Me pide la contraseña anterior» en L13; B
confirma cuál en L14 y **L16**. Ante la objeción de A, en **L18** responde: «No la vas
a decir, solo ingresala en la ventana de recuperación». A elige hacerlo desde el
sitio cuando termine y no hay cumplimiento.

Tito activó en L10. En L16 E2B da **0,3 con Tito y 0,2 solo**, sin alerta; en L18,
0,3 en ambas condiciones, sin alerta. No se limita a una clave dicha por teléfono:
el prompt también incluye contraseñas y acciones de seguridad guiadas. La referencia
mantiene la duda L14/L16 y el texto no permite verificar el control real de la
ventana. **Hipótesis:** el SLM trata el ingreso presentado como local como seguro.
Debe contrastarse con recuperación legítima por un sitio elegido independientemente;
no alcanza con agregar la regla «ingresar una contraseña siempre es fraude».

## Las trece pérdidas con pedido de Tito → E2B

Los nombres abreviados de esta tabla llevan prefijo `CV2-D-V-`, salvo `TR-01`.
Las columnas son primeras líneas observadas; «—» significa que no hubo aviso.

| Caso | T_R / T_C | Activa Tito | Aviso solo / con Tito | Observación y límite de atribución |
|---|---|---:|---|---|
| BANCO-003 | 19 / 26 | 5 | — / — | Entrega de efectivo explícita; pedido evaluado por ambos. |
| PREMIO-003 | 13 / — | 3 | — / — | Documento y luego foto en L19; revisar clase y marca. |
| SOPORTE-005 | 16 / — | 10 | — / — | Contraseña anterior en ventana guiada; revisar L14/L16. |
| PREMIO-001 | 10 / 13 | Nunca | 10 / — | Omisión demostrada de compuerta: puntaje 0,024 en T_R; el directo sí avisa ahí. |
| PREMIO-002 | 13 / 16 | 3 | 13 / — | Pago por transferencia; riesgo 0,3 con y sin Tito, pero booleano distinto. Indicio o variación, sin aislar. |
| SOPORTE-001 | 14 / — | 12 | 10 / — | El directo avisa por abrir el panel y corta antes de la contraseña. No demuestra que detectaría el pedido de L14. |
| TR-01-pedido-indirecto-digitos | 8 / 11 | 3 | 5 / — | El directo avisa por presión antes del mensaje. No observa L8; el tipo de código es inferido por la referencia. |
| WHATSAPP-004 | 13 / — | 5 | — / — | «Pasámelo» remite al código de registro nombrado en L10. |
| ORGANISMO_PREVISIONAL-003 | 11 / — | 13 | — / — | Tito llega tarde; el directo sí evalúa L11 con 0,2 y tampoco avisa. |
| ORGANISMO_PREVISIONAL-004 | 14 / — | 2 | — / — | Últimos cuatro y fecha de emisión como referencia administrativa; falla en ambos. |
| FAMILIAR-004 | 22 / — | 14 | — / — | Dinero en su cuenta como condicional; revisar inducción, identidad y clase. |
| FAMILIAR-005 | 20 / — | 18 | — / — | «Si alguien pudiera comprarlo…»; la nota dice instrucción, el texto es condicional. Revisar clase. |
| FAMILIAR-006 | 22 / — | 17 | — / — | «Si podés cubrir la seña…»; revisar clase e identidad con contexto completo. |

**Conteo descriptivo:** 1 nunca deriva; 5 pedidos de trámite o acción explícita
(PREMIO-002, SOPORTE-001 y los tres casos iniciales); 2 pedidos cuyo objeto requiere
resolver referencias (TR-01 y WHATSAPP-004); 2 datos parciales; 3 condicionales.
Son grupos de lectura, no causas probadas. Cuatro referencias dicen `directo`
(BANCO-003, PREMIO-001, PREMIO-002 y SOPORTE-001); no se deben describir las trece
como pedidos indirectos.

**Balance causal:** PREMIO-001 es la pérdida demostrada por omisión de compuerta;
PREMIO-002 difiere en la respuesta; SOPORTE-001 y TR-01 quedan censurados antes del
pedido en el directo. Las otras **nueve con pedido** fallan en ambos recorridos.
No se atribuye todo al prompt: ya contempla varios de estos pedidos. Tampoco se
ha demostrado un techo del modelo con otras instrucciones.

## Las once sin pedido, separadas de los pedidos perdidos

Los IDs llevan `CV2-D-V-`, salvo TR-12. Ninguna avisa con Tito; solo BANCO-011 avisa
sin él. «Sin pedido» significa **sin T_R en la referencia de trabajo**, no ausencia
de toda maniobra o seguridad de que la clase es correcta.

| Caso | Evidencia a revisar | Riesgo máximo con Tito / solo |
|---|---|---|
| BANCO-011 | No cerrar sesión (L8), no cortar (L14). Directo avisa L17 cuando la persona dice que algo no le cierra. | 0,6 / 0,6 |
| ORGANISMO_PREVISIONAL-005 | Guardar y no reenviar (L8); no cortar (L20). | 0,5 / 0,3 |
| ORGANISMO_PREVISIONAL-006 | No cerrar llamada (L19). | 0,5 / 0,3 |
| WHATSAPP-007 | No abrir mensaje (L8), no cerrar llamada (L12), no comentar al grupo (L18). | 0,5 / 0,3 |
| SOPORTE-007 | No cerrar pantalla del medidor (L6). | 0,4 / 0,3 |
| WHATSAPP-008 | No responder a mensajes nuevos (L13). | 0,4 / 0,3 |
| PREMIO-005 | No entrar todavía (L14), no cortar (L22). | 0,3 / 0,3 |
| TR-12-corta-antes-del-pedido | No cortar ni contar a nadie (L6); insistencia en L9. | 0,3 / 0,3 |
| PREMIO-006 | Presión y reserva, sin T_R anotado. | 0,5 / 0,2 |
| BANCO-012 | Plazo de revisión, sin T_R anotado. | 0,4 / 0,3 |
| SOPORTE-008 | Confirmación de control, sin T_R anotado. | 0,3 / 0,3 |

Ocho contienen restricciones de comunicación o de verificación; tres, presión o
evasivas. Que esas maniobras deban bastar para avisar sigue pendiente en
[D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y
[D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
El tutor ya fijó que todas cuentan en el denominador. No se las elimina ni se
amplía la regla de alerta para mejorar el porcentaje. El aviso de BANCO-011 exige
revisar su fundamento: no demuestra reconocimiento temprano del ataque.

Las **19 perdidas por ambos** son nueve con T_R y diez sin T_R. La versión anterior
de este informe invertía esos dos recuentos.

## Falsas alarmas: los 21 casos que avisan en alguna condición

Diez compartidas, ocho solo del directo y tres solo con Tito. Los IDs abreviados
BANCO y FAMILIAR de esta tabla llevan `CV2-D-L-`. Se mantiene la clase de referencia.

| Caso | Aviso solo / con Tito | Qué interpreta mal o qué queda por discutir |
|---|---|---|
| BANCO-002 | 7 / 7 | Identificación acotada por últimos cuatro dígitos. |
| BANCO-010 | 10 / 10 | Últimos cuatro números para ubicar comprobante. |
| LAB-arca-canal-oficial | 3 / 3 | Consejo de ir a página oficial tomado como maniobra. |
| LAB-banco-revisa-app | 3 / 3 | Cortar y consultar app propia tomado como ataque. |
| LAB-no-bajes-nada | 1 / 4 | Relato de un pedido ajeno tratado como pedido vigente; con Tito ya estaba el consejo contrario. |
| LG-BANK-VERIF-01-e01 | 2 / 6 | Directo: deseo del usuario de cambiar clave. Con Tito: ofrecimiento de datos tratado como pedido. |
| TR-06-banco-alerta-legitima | 10 / 10 | La persona ofrece el código; se le atribuye un pedido al banco. |
| TR-08-frase-cortada-candado | 3 / 3 | «Pasame el código» antes de que llegue la aclaración del candado. |
| TR-11-familiar-real-pide-plata | 4 / 9 | Pedido familiar; con Tito ignora que ya acuerdan cortar y devolver la llamada. |
| TR-13-turno-medico-pide-dni | 5 / 5 | DNI y fecha de nacimiento para turno médico. |
| BANCO-001 | 12 / — | Confirmar el nombre del titular. |
| LAB-anses-canal-oficial | 1 / — | «Me ofrecieron…» como si quien conversa estuviera solicitando datos. |
| LAB-banco-app-parafrasis | 3 / — | Uso de huella en app propia después de aconsejar cortar. |
| LG-ORG-TURNO-01-e01 | 4 / — | Relato de lo que le pidieron a una vecina. |
| LG-SUPPORT-INFO-01-e01 | 4 / — | «Yo te los iba a pasar» leído como pedido de la contraparte. |
| LG-WA-CONSULTA-01-e01 | 1 / — | Recepción de código no solicitado, sin pedido de compartirlo. |
| TR-03-negacion-y-consejo | 5 / — | Pregunta hipotética sobre una amenaza tratada como amenaza actual. |
| TR-05-asado-con-transferencia | 14 / — | Pedir el alias para pagar el asado. |
| BANCO-005 | — / 8 | Últimos cuatro dígitos; resultado diferente del directo. |
| FAMILIAR-002 | — / 11 | Alias para un reparto familiar, descrito como acceso a una cuenta. |
| FAMILIAR-005 | — / 10 | Reparto del costo del plomero. |

En las trece con Tito, la lectura del handoff de falsas alarmas separa siete pedidos
razonables sin criterio suficiente en el prompt, cinco contradicciones de sus
exclusiones y una frase incompleta. Las ocho adicionales del directo refuerzan dos
problemas: atribuir a quien conversa un pedido relatado/hipotético, y confundir un
pedido razonable o un ofrecimiento con una solicitud peligrosa.

La tensión a resolver es concreta: avisa por últimos cuatro dígitos en legítimas de
banco, pero calla ante últimos cuatro más fecha de emisión en
`CV2-D-V-ORGANISMO_PREVISIONAL-004`. Avanza sobre DNI en TR-13, pero no sobre DNI y
foto en PREMIO-003. No se corrige con «si pide un dato, avisar» ni con «si parece un
trámite, no avisar». Las dos reglas pueden empeorar el lado opuesto.

### Lo que marcó Luciano

Se conserva del handoff de falsas alarmas: inconsistencia entre pedidos bancarios
parecidos, contraste con ORGANISMO_PREVISIONAL-004, alarmas injustificadas en TR-11
y los consejos de canal propio, sorpresa por TR-06, necesidad de más contexto en
TR-08 y lectura del contexto médico en TR-13. **En esta sesión todavía no hay
adjudicaciones nuevas de Luciano** sobre los tres casos iniciales ni sobre el resto.
Ninguna observación de esta revisión cambia `revision_humana`.

## Avisos tardíos, como problema separado

Con Tito llegan después de T_R: FAMILIAR-001 (16/15), FAMILIAR-003 (17/15),
SOPORTE-003 (14/11), SOPORTE-004 (17/14), todos `CV2-D-V-`; y TR-04
(27/26, con T_C 27). **TR-04 avisa en el cumplimiento**, no se debe presentar
como protección previa. El directo no avisa en TR-04.

De las 50 estafas avisadas por ambos, 36 coinciden en línea, diez se adelantan sin
Tito (4,2 líneas de media entre esas diez) y cuatro con Tito. En tres de los diez
adelantos del directo, la compuerta aún no había abierto: BANCO-004, -007 y -008.
En los otros siete sí hubo consulta. En 1.083 líneas consultadas por ambos,
21 booleanos difieren: estafas, diez alertan solo sin Tito y cinco solo con él;
legítimas, tres y tres. Esto motiva medir indicio y repetibilidad, no demuestra
que el indicio sea la causa. Avisar antes tampoco garantiza un motivo correcto.

## Inventario completo de diferencias observadas (2026-11-04)

El saldo de cuatro estafas y cinco falsas alarmas netas no es la cantidad de casos
que cambiaron. Al quitar Tito se recuperan **cinco estafas y se pierde una**;
aparecen **ocho falsas alarmas y desaparecen tres**. Cambia el resultado en 17/150
conversaciones. Las tablas de pérdidas y falsas alarmas de este documento explican
esos casos; el panel permite filtrarlos y ver sus respuestas completas.

Otras **17 conversaciones** conservan el aviso pero cambian de línea. De las 14
estafas, diez avisan antes sin Tito y cuatro antes con Tito. Las otras tres son
legítimas: retrasar su falsa alarma no la elimina. Este es el inventario completo
(IDs íntegros; no se convierten líneas a segundos):

| Caso | SLM solo | Con Tito | Lectura del cambio |
|---|---:|---:|---|
| `CV2-D-V-BANCO-002` | L11 | L18 | Directo: mirar una solicitud. Con Tito: autorizar un equipo nuevo; el aviso temprano no prueba mejor reconocimiento. |
| `CV2-D-V-BANCO-004` | L8 | L10 | Directo: verificar teléfono. Con Tito: envío de código; en L8 la compuerta todavía estaba cerrada. |
| `CV2-D-V-BANCO-006` | L10 | L14 | Directo: confirmar teléfono. Con Tito: entregar seis números; cambian momento y fundamento. |
| `CV2-D-V-BANCO-007` | L6 | L17 | Directo: noticia del cambio de teléfono. Con Tito: confirmar receptor de verificaciones; en L6 no había derivación. |
| `CV2-D-V-BANCO-008` | L10 | L16 | Directo: ofrecimiento de visita. Con Tito: sobre con efectivo; la compuerta no había abierto en L10. |
| `CV2-D-V-BANCO-010` | L3 | L1 | Con Tito basta la presentación del banco; el directo espera la validación pendiente. Revisar fundamento del adelanto. |
| `CV2-D-V-PREMIO-004` | L15 | L14 | Tito avisa al pedido de tres números de seguridad; directo espera que la persona los nombre como código de seguridad. |
| `CV2-D-V-SOPORTE-003` | L10 | L14 | Directo: pantalla que pide credenciales. Con Tito: después de confirmarse el pedido; llega después de T_R. |
| `CV2-D-V-SOPORTE-004` | L13 | L17 | Directo: noticia de control remoto. Con Tito: permiso para mover cursor y escribir; llega después de T_R. |
| `CV2-D-V-WHATSAPP-003` | L12 | L8 | Con Tito avisa por anuncio de código; directo espera el pedido de leerlo. Revisar el sustento del aviso previo. |
| `CV2-D-V-WHATSAPP-006` | L26 | L25 | Con Tito completa «pasame» usando el contexto; directo espera «eso que apareció». Diferencia de una actualización. |
| `LAB-banco-numeros-sin-clave` | L3 | L4 | Misma presión y misma cita; con Tito avisa una línea después. No demuestra una causa distinta. |
| `LAB-no-bajes-nada` | L1 | L4 | Ambos convierten un relato en pedido actual. Con Tito el consejo contrario ya estaba disponible y sigue fallando. |
| `LG-BANK-VERIF-01-e01` | L2 | L6 | Directo: deseo de cambiar clave atribuido al banco. Con Tito: ofrecimiento de números tratado como pedido. |
| `TR-07-pedido-partido-en-dos-lineas` | L6 | L7 | Directo: pregunta de qué hacer. Con Tito: «pasame lo que te llegó». El pedido explícito llega después. |
| `TR-10-ofrecimiento-inducido` | L4 | L6 | Directo: presión y cuenta retenida. Con Tito: anuncio de SMS. Ninguno de esos motivos prueba por sí solo el pedido. |
| `TR-11-familiar-real-pide-plata` | L4 | L9 | Ambos alarman por ayuda familiar; con Tito ya acordaban cortar y devolver la llamada. Sigue siendo falsa alarma. |

En **34 casos adicionales** la línea del aviso coincide, pero cambia literalmente
el motivo, la evidencia citada o ambos. Se distingue cambio textual de cambio
semántico: agregar «por teléfono», formular un consejo o abreviar una cita no
prueba una mejora. El panel muestra el par completo en el filtro «Misma línea,
cambia motivo o cita». Los 34 son:

- `CV2-D-L-BANCO-002`: L7.
- `CV2-D-L-BANCO-010`: L10.
- `CV2-D-V-BANCO-001`: L29.
- `CV2-D-V-BANCO-005`: L5.
- `CV2-D-V-FAMILIAR-002`: L16.
- `CV2-D-V-FAMILIAR-003`: L17.
- `CV2-D-V-ORGANISMO_PREVISIONAL-001`: L12.
- `CV2-D-V-ORGANISMO_PREVISIONAL-002`: L9.
- `CV2-D-V-SOPORTE-002`: L7.
- `CV2-D-V-SOPORTE-006`: L14.
- `CV2-D-V-WHATSAPP-001`: L9.
- `CV2-D-V-WHATSAPP-002`: L10.
- `CV2-D-V-WHATSAPP-005`: L13.
- `LAB-acceso-remoto`: L3.
- `LAB-acceso-remoto-parafrasis`: L3.
- `LAB-anses-beneficio`: L3.
- `LAB-anses-beneficio-parafrasis`: L3.
- `LAB-arca-canal-oficial`: L3.
- `LAB-arca-deuda`: L3.
- `LAB-banco-codigo`: L3.
- `LAB-banco-codigo-parafrasis`: L3.
- `LAB-banco-revisa-app`: L3.
- `LAB-digitos-sin-palabra`: L3.
- `LAB-familiar-peligro`: L4.
- `LAB-familiar-peligro-parafrasis`: L4.
- `LAB-pantalla-sin-programa`: L3.
- `LAB-whatsapp-codigo`: L3.
- `SC-CLAVE-CAMBIO-01-e01`: L2.
- `SC-FAMILIAR-DINERO-01-e01`: L9.
- `SC-ORG-BENEFICIO-01-e01`: L7.
- `SC-SOPORTE-CLAVE-01-e01`: L6.
- `TR-08-frase-cortada-candado`: L3.
- `TR-09-victima-se-niega`: L3.
- `TR-13-turno-medico-pide-dni`: L5.

Los cambios de fundamento que merecen atención incluyen FAMILIAR-003: el directo
atribuye un pedido de alias a quien lo ofrece; con Tito se suma una solicitud
anterior de comprobante, pero sigue invirtiéndose el ofrecimiento. En WHATSAPP-002
Tito explicita que el código podría permitir acceso, mientras el directo solo
nombra el cierre del diagnóstico. En LAB-whatsapp-codigo ocurre lo inverso: el
directo nombra verificación y el texto con Tito queda en «seis dígitos». En
LAB-banco-revisa-app ambos sostienen una interpretación errónea del consejo de
cortar y consultar el canal propio. Son observaciones de estas respuestas, no
atribuciones causales al indicio.

Estas categorías son excluyentes: **17 de resultado + 17 de momento + 34 solo de
texto = 68** conversaciones con algún cambio en el primer aviso. Las otras 82
mantienen aviso, línea y fundamento: 73 sin aviso y nueve con el mismo aviso y texto.
Esto no significa igualdad de todas sus respuestas numéricas.

En las **1.083 líneas consultadas por ambos** hay **540 diferencias de riesgo en
112 conversaciones** y **21 cambios del booleano en 21 conversaciones**. Se
superponen con las categorías anteriores; no se suman como casos nuevos. El panel
marca cada línea y permite saltar a ella. Un 0,2 contra 0,3 con ambos sin aviso es
una diferencia numérica, no un acierto nuevo. Las omisiones de compuerta y las
líneas sin evaluar tras el primer aviso se muestran como estados propios y no
entran como respuestas negativas en este cruce.

En costo: 1.139 líneas omitidas dentro del recorrido con Tito; 1.039 consultas
menos al contrastar los dos recorridos, que cortan en distintos puntos. La mediana
por consulta es 309,4 ms con Tito frente a 290,8 ms solo; no mide el costo total ni
prueba que Tito acelere cada consulta. Persistencia, repetibilidad y costo sobre
trayectorias completas todavía no están medidos.

## Qué aportan Ignacio y Evaristo a esta comparación

| Ensayo | Resultado que aporta | Límite para mejorar estos fallos |
|---|---|---|
| Ignacio, matriz #101, Tito viejo → Gemma 4 E2B | 10/10 estafas, **0/10 falsas alarmas**, nueve avisos antes o en T_R. | Las veinte son `corpus_v2`; ninguna de las 24 pérdidas actuales está en esas veinte. El resultado no representa los 150. |
| Ignacio, Colab | Procedimiento para repetir Tito → E2B con reglas y digest fijado; README informa una corrida previa similar. | No ejecuta SLM solo; sin CSV/manifiesto adicionales aquí no se cuantifica la variación Colab/Windows. No se ejecutó el notebook. |
| Evaristo, riesgo primero, Gemma 3n E2B | En 20 casos: riesgo > 0,7 da 10/10 y 3/10 FA; EMA 0,3 > 0,7 da 8/10 y 1/10, sin aviso antes del pedido. Reduce el costo de líneas sin alerta frente a `v2`. | Otra familia de modelo y otro prompt. En R3, la política elegida en 57 casos (> 0,8) pasa de 15/19 y 0/38 a **2/10 y 0/10** en informe. No se transfiere establemente. Solo BANCO-003 de las 24 pérdidas está en esos 57. |

No se mezclan porcentajes de modelos, prompts, hardware o muestras distintos. La
coincidencia útil es cualitativa: los pedidos administrativos y los relatos u
ofrecimientos también producen falsas alarmas en los ensayos previos. El fallo de
selección/informe de R3
advierte contra elegir un umbral que luce bien en un grupo de guiones.

## Plan de mejora para discutir antes de cambiar el detector

> **Estado: propuesta sin discutir.** Depende de [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico),
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)
> y de reconsiderar el [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)
> para implementar variantes. No se modificaron prompt, modelo, umbral ni política.

**Dirección solicitada por Luciano (2026-11-04):** usar las discrepancias para
mejorar SLM y Tito, conservando SLM solo como control; no cambiar prompt,
entrenamiento y política juntos. No se cambia ahora la configuración de la demo.
La matriz y los detalles operativos que siguen son propuestas de desarrollo.

### Matriz para separar prompt y Tito

P0 es el prompt actual; P1, una modificación concreta. T0 es Tito viejo; T1, un
único candidato mejorado, persistido y congelado antes de comparar. Gemma 4 E2B
conserva sus pesos, cuantización y parámetros. Mejorar el prompt del SLM no
significa entrenar sus pesos.

| Prompt | SLM solo | Con Tito viejo T0 | Con Tito mejorado T1 |
|---|---|---|---|
| Actual P0 | A: control directo | B: sistema actual | E: cambia solo Tito |
| Nuevo P1 | C: cambia solo prompt | D: prompt con Tito viejo | F: ambos cambios |

- **C−A y D−B:** efecto del prompt sin y con Tito viejo.
- **E−B y F−D:** efecto de Tito bajo prompt viejo y nuevo.
- **F−E:** efecto del prompt con Tito mejorado.
- **(F−E)−(D−B):** si el efecto del prompt cambia al cambiar Tito, calculado
  por métrica; no implica un tamaño de muestra suficiente para una conclusión estadística.

Comparar solo F contra B confunde los factores. Puede ocurrir que el prompt
recupere casos y Tito pierda otros, dejando casi igual el saldo. Cada contraste
debe listar recuperaciones, pérdidas, falsas alarmas nuevas/eliminadas, momento y
fundamento, además del porcentaje. No se agregan todos los errores como una
única «mejora» ni se fija ahora una ponderación entre ellos.

### Orden de trabajo propuesto

1. Usar el inventario y el panel anotado para revisar las ambigüedades de D07.
   Los originales quedan conservados; el análisis de IA no es revisión humana.
2. Asegurar acceso exclusivo a desarrollo antes de ejecutar: adaptar el ejecutor
   o usar la copia sin reserva, verificando que tampoco requiera sus referencias
   al inicializar. La guarda del comparador no certifica `correr.py`.
3. Repetir SLM solo, Tito con indicio y Tito sin indicio con P0 y T0 fijados.
   Este diagnóstico separa omisiones, efecto del indicio y variación; no se
   multiplica automáticamente por cada prompt posterior.
4. Separar desarrollo nuevo por semillas/variantes antes de observar respuestas
   (#55, D07/D08): ajuste y comprobación. Los 150 vistos sirven como diagnóstico
   y regresión declarada, no como muestra independiente recién creada.
5. Probar una hipótesis de prompt por vez en A/B/C/D: quién pide a quién;
   relato/hipótesis; ofrecimiento/consejo; trámites, elipsis y pedidos condicionales.
   Una P1 no reúne todos esos cambios. Conservar P0 para todos los contrastes.
6. Evaluar una mejora concreta de Tito como T1, completar E/F y registrar qué
   cambia: datos, entrenamiento, umbral, unidad de entrada o indicio. Esos cambios
   no se mezclan entre sí sin controles adicionales. El aporte sugerido por el
   amigo todavía no está especificado ni se identifica con una variante inventada.
7. Solo después probar espera de una actualización, contra la misma combinación
   fijada de prompt/Tito, con política inmediata como control. Medir falsas
   alarmas evitadas, retraso en líneas y avisos que se pierden por fin de llamada;
   TR-04 ya avisa en T_C. No usar futuro para justificar un aviso anterior.
8. Elegir con desarrollo de ajuste, comprobar una vez en la parte separada y
   congelar configuración/protocolo antes de la evaluación final. Volver a ajustar
   mirando la comprobación consume su independencia y debe declararse. Resolver
   D07/D08 y reconsiderar ADR 0001 si se adopta una variante distinta.

### Tests unitarios y pruebas experimentales

Los tests deterministas comprueban **que se ejecuta el experimento correcto**:
selección y hash de P0/P1 y T0/T1; SLM solo sin compuerta ni indicio; compuerta con
umbral y reinicio por conversación; ausencia de futuro y referencias humanas en
la entrada; continuación tras el aviso sin duplicar el primer aviso; omisión,
fallo técnico y silencio válidos separados; guardado y reanudación sin mezclar
configuraciones ni duplicar resultados. Probar con dobles y casos sintéticos,
sin descargar modelos ni recorrer la reserva.

Las corridas con modelos comprueban **si mejora el comportamiento**. Los casos
BANCO-003, PREMIO-003, SOPORTE-005 y sus legítimas comparables son regresiones de
desarrollo; pasarlos no demuestra generalización. Un test de cadena o una frase
aislada no valida la comprensión incremental del diálogo.

### Repeticiones y preparación de Colab

Se proponen inicialmente **dos ejecuciones completas por condición** para detectar
variación, manteniendo seed 42 y alternando el orden de condiciones. No es un
cálculo de potencia ni aumenta el número de conversaciones independientes. El
mínimo principal son 6 condiciones × 2 repeticiones = **12 corridas**; los tres
controles previos requieren seis corridas. Si fueran los mismos 150 casos, serían
1.800 y 900 recorridos de conversación respectivamente, más calentamiento. No
son tiempos estimados ni una orden de ejecutar ahora.

En la matriz principal, el indicio conserva el modo actual en T0 y T1; modificar
su contenido o quitarlo constituye otro contraste. Cada condición debe usar los
mismos textos, prefijos y referencias congeladas,
continuar hasta fin de conversación y registrar primer aviso por separado de
respuestas posteriores. No se combinan las corridas actuales, que cortan al
aviso, con las nuevas para presentar persistencia o ahorro como si el recorrido
fuera idéntico. Una seed fija no sustituye comprobar variación observada.

El [Colab actual](../../colab/README.md) ejecuta Tito viejo y reglas y todavía no
implementa esta matriz. Antes de dejarla corriendo necesita selector explícito de
condición/repetición, comprobación de modelo/digest, hashes de prompt/Tito/datos,
versiones fijadas, prueba de uso real de GPU y persistencia por conversación fuera
de la máquina temporal. Reanudar solo unidades completas, coincidentes en todos
los hashes; conservar los fallos y reintentos sin convertirlos en negativos ni
elegir la respuesta que más convenga. Entrenar T1 una vez sobre ajuste autorizado,
guardar el artefacto, y reutilizarlo en todos sus controles; no reentrenarlo con
casos de comprobación o evaluación.

Google declara que los recursos y tiempos de sesión varían y que las máquinas
virtuales tienen vida máxima; por eso el ZIP al final no alcanza como único
resguardo ([FAQ oficial de Colab](https://research.google.com/colaboratory/faq.html),
consultada el 2026-11-04). No se abrió una sesión ni se lanzó una corrida nueva.
Para calidad, comparar condiciones dentro del mismo entorno; para latencia,
registrar hardware, calentamiento y uso de GPU y no mezclar los tiempos con Windows.

En cada prueba se registran primer aviso, fundamento y cita, T_R/T_C, avisos sin
pedido, falsas alarmas comunes/difíciles, consultas, errores, latencia y configuración.
El riesgo numérico no está calibrado: no se propone bajar un umbral global como
arreglo de estas pérdidas. El booleano puede cambiar aun con el mismo riesgo (PREMIO-002).

**Dónde ajustar y dónde comprobar:** estos 150 ya vistos sirven para diagnóstico y
regresión declarada. La propuesta es preparar desarrollo nuevo, separado por
semilla/variantes antes de observar respuestas, con una parte para elegir y otra
para comprobar; balancear pedidos razonables, engaños como trámite, elipsis,
condicionales, negaciones y frases incompletas. No se declara independiente una
subdivisión posterior de estos mismos 150. Cantidad, adjudicación y partición las
acuerda el equipo en D07/D08; no se genera una colección nueva ni se abre la reserva.
La reserva se conserva para la evaluación final, con protocolo y configuración
congelados, según lo que resuelva el equipo. El incidente previo mencionado en el
handoff sigue pendiente de decisión de Luciano; esta revisión no lo adjudica.

### Comentario de avance listo para GitHub, sin publicar

```markdown
Avance de #51 y #68 — comparación y revisión de errores (2026-11-04).

E2B directo: 55/75 estafas y 18/75 FA. Tito viejo → E2B: 51/75 y 13/75.
Son los mismos 150 casos de desarrollo sin revisión humana; ambos recorridos
cortan al primer aviso. Se revisaron primero BANCO-003, PREMIO-003 y SOPORTE-005,
se cruzaron las 24 pérdidas con las 21 falsas alarmas de alguna condición y
se ubicaron los aportes ya integrados de Ignacio y Evaristo.

Evidencia: experiments/slm-directo/corridas/2026-11-04_132229_e2b-directo-150/comparacion-con-tito.md.
Comparador sin acceso al catálogo ni enumeración de casos; seis pruebas de guardas
con fixtures sintéticos, cinco pruebas del panel y reproducción del recuento
sobre IDs de manifiestos. Panel ampliado con comparación por caso y pasos propuestos.

Ampliación: inventario de 17 cambios de resultado, 17 de momento y 34 solo de
texto del aviso; 540 cambios de riesgo en 112 casos sobre líneas comparables.
Matriz propuesta de seis condiciones para separar prompt y Tito, tests y preparación
de Colab. Luciano pidió aislar cambios; no se fijaron candidatos ni particiones.
D07/D08 siguen abiertas y ADR 0001 vigente. No se ejecutaron
variantes ni se modificó el detector. Próximo paso propuesto: acordar adjudicación,
comparación sin indicio, matriz prompt × Tito y desarrollo separado para elegir/comprobar mejoras.
#51 y #68 siguen abiertos; no corresponde Closes en este avance.
```
