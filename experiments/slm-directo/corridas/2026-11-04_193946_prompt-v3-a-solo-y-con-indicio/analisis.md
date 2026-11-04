# Prompts v3 y v4 con Gemma 4 E2B y Tito

**Fecha:** 2026-11-04. **Issue:** [#51](https://github.com/Corchets/bitacora_tesis/issues/51), sigue abierto.

> **Estado: propuesta sin discutir.** Diagnóstico sobre los 150 casos de desarrollo, ya vistos, con referencias y
> roles sin revisión humana. No es una evaluación final. No toca la reserva, no decide
> [D07](../../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) ni
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y no cambia el
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Conclusión

**Ninguna condición cumple la meta del tutor** (60–64 estafas con 8–11 falsas alarmas). La más cercana es
[v4](../../prompts/tarea_v4.txt) con Tito sin indicio: **55/75 estafas y 13/75 falsas alarmas**. En cantidad empata con v1
dentro del ruido, pero avisa mejor: cita el pedido real en 34 casos contra 27 y cita solo a la víctima en 1 contra 7.
La configuración vigente sigue siendo Tito viejo con indicio y v1 (`tarea`).

Tres resultados guían el próximo paso:

1. **La causa principal del salto de v3 era el orden de los campos.** Con solo pasar la cita al final, v3 baja de 35 a
   18 falsas alarmas, a cambio de 7 estafas.
2. **Saber a quién protege no alcanzó por sí solo:** en v3, los roles cambian las falsas alarmas de 35 a 34. Esa prueba
   conserva la cita primero, así que todavía no se midió el efecto de los roles sin ese problema.
3. **La mayor falsa alarma que queda es el dato de identificación:** 7 de las 13 de v4, todas en llamadas que inició la
   persona. La regla que debía evitarlo no funcionó.

## Todas las condiciones con Tito sin indicio

Todas: Colab con GPU T4, Tito con umbral 0,5, corte al primer aviso y 150 casos.

| Condición | Estafas (de 75) | Con pedido (de 64) | Falsas alarmas (de 75) | Comunes (de 51) | Difíciles (de 24) | Antes / en / después del pedido | Cita el pedido | Cita solo a la víctima | Consultas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v1 de Evaristo | 54 (72 %) | 53 | 14 (19 %) | 4 | 10 | 24 / 25 / 4 | 27 | 8 | 1.140 |
| v1 control | 53 (71 %) | 52 | 14 (19 %) | 4 | 10 | 23 / 25 / 4 | 27 | 7 | 1.152 |
| v3 | 64 (85 %) | 63 | 35 (47 %) | 20 | 15 | 42 / 18 / 3 | 20 | 8 | 791 |
| v3 con el orden de v1 | 57 (76 %) | 56 | 18 (24 %) | 7 | 11 | 23 / 28 / 5 | 31 | 5 | 1.093 |
| v3 con roles | 67 (89 %) | 63 | 34 (45 %) | 20 | 14 | 41 / 20 / 2 | 22 | 7 | 760 |
| **v4 con roles** | **55 (73 %)** | 54 | **13 (17 %)** | 6 | 7 | 19 / 33 / 2 | **34** | **1** | 1.132 |

«Cita el pedido»: la cita del primer aviso incluye la línea `T_R` u otra marcada como pedido, entre las estafas con
pedido que tuvieron aviso. No cuenta pasos previos reales, así que es un piso. Ninguna corrida tuvo fallos técnicos.

## Qué cambió cada factor

| Comparación | Estafas | Falsas alarmas | Lectura |
|---|---:|---:|---|
| v1 de Evaristo → v1 control | −1 | 0 | Mismas 14 falsas alarmas. Solo cambia BANCO-003. Es el ruido de referencia |
| v3 → v3 con el orden de v1 | −7 | −17 | Sin ganar ni agregar nada. Citas en líneas sin alerta: de 509 de 692 a 13 de 1.018 |
| v3 → v3 con roles | +3 | −1 | Las 3 estafas son sin pedido y por motivos flojos («lo cual podría…»): no es una mejora real |
| v3 → v4 con roles | −9 | −22 | No gana ni agrega nada |
| v1 control → v4 con roles | +2 (gana 4, pierde 2) | −1 (saca 4, agrega 3) | Dentro del ruido en cantidad, distinto en calidad |

**Lo que gana v4 contra v1:** BANCO-003, ORGANISMO_PREVISIONAL-003, SOPORTE-001 y `TR-04`, con citas sobre el pedido o sobre
un paso real. **Lo que pierde:** SOPORTE-003 y SOPORTE-006, dos pedidos directos de credenciales. v1 los detectaba citando a
la víctima («Me pide usuario y contraseña»). v4 pide citar a OTRA y no alerta ni siquiera en `T_R`; esa regla puede ser la causa, sin probar.

## De qué están hechas las falsas alarmas

Lectura propia por caso, sin revisión humana. La lista está en el script.

| Clase | v1 control | v3 | v3 con el orden de v1 | v3 con roles | v4 |
|---|---:|---:|---:|---:|---:|
| Dato de identificación en una gestión legítima | 4 | 7 | 7 | 7 | **7** |
| Consejo seguro, explicación o negación | 3 | 10 | 4 | 9 | **2** |
| Quien ofrece, pregunta o relata es la propia persona | 3 | 9 | 3 | 8 | **2** |
| Dinero o encargo cotidiano entre conocidos | 3 | 7 | 3 | 7 | **1** |
| Frase ambigua o pedido inexistente | 1 | 2 | 1 | 2 | **1** |

v3 con roles suma además `CV2-D-L-ESCUELA-002`, fuera de estas clases. Los 13 casos de v4:

- **Dato (7):** BANCO-001, BANCO-002, BANCO-004, BANCO-005, BANCO-006, BANCO-010 y `TR-13`. La regla de v4 excluía este caso y
  el modelo igual avisa. BANCO-006 ahora avisa por otra frase, un consejo de cerrar sesión.
- **Consejo (2):** `LAB-banco-app-parafrasis` y `LAB-banco-revisa-app`. La regla de canal propio sacó a `LAB-arca-canal-oficial`.
- **Propia persona (2):** `LG-BANK-VERIF-01-e01` y `TR-06`. El modelo ve `PROTEGIDA:` en la línea que cita y avisa igual.
- **Dinero (1):** `TR-11`. **Ambigua (1):** `TR-08`.

Ninguno de los 6 roles dudosos aparece entre las falsas alarmas de v4.

## Quién sabe quién habla

**Por defecto, ni el SLM ni Tito saben quién habla, tampoco en la llamada con ASR. Con `--hablantes rol`, el SLM sí lo sabe; Tito, no.**

- **SLM:** por defecto recibe A y B por orden de habla, y el mensaje aclara que «las letras no indican quién llamó ni quién es sospechoso»
  ([`detectores.py`](../../detectores.py)).
- **Tito:** recibe solo el texto de cada frase, sin dato de hablante.
- **Llamada:** el sistema sí lo sabe, porque cada persona es un canal. Por defecto (`--hablantes ab`), [`llamada.py`](../../../voip/llamada.py) convierte `protegida` y `otra` en A y B según quién habló primero; con `--hablantes rol`, pasa `PROTEGIDA` y `OTRA` al contexto del SLM desde la primera frase.

**Opinión de Luciano:** el SLM y Tito deberían saber quién habla a partir de los canales del ASR, porque esa información
existe en la llamada real y ayuda a decidir mejor. En una llamada nadie la anota: sale del canal.

Para probarlo se agregó `--hablantes rol`, que manda `PROTEGIDA:` y `OTRA:` en cada línea. En los casos de texto el rol sale de
[`casos/roles-protegida.json`](../../casos/roles-protegida.json), porque el corpus no lo tenía; en la llamada en vivo y en replay sale directamente del canal (`servidor.py`, `medir.py` y `replay.py` aceptan `--hablantes rol` y `--sin-indicio`, manteniendo `ab` con indicio por defecto). Tito siguió sin cambios: recibe solo el texto de cada frase.

**Cómo se anotó:** 64 estafas salen de `T_R`, revisando que esa línea la diga el atacante. 80 casos salen de la lectura: la
persona protegida es quien recibe el pedido o el consejo, o si no hay ninguno, quien recibe la llamada. 6 quedaron marcados
como dudosos, por ser charlas parejas (FAMILIAR-001 a 004, TRABAJO-002 y TRABAJO-004). Se anotó después de ver qué casos
daban alarma y sin revisión humana.

**Efecto en pantalla:** en v4, 12 de los 68 motivos dicen literalmente «OTRA» o «PROTEGIDA». El panel (`conversacion.mjs`, `panel.html` e `historial-ui.mjs`) los reemplaza al mostrarlos por «La otra persona» / «la otra persona» y «La persona protegida» / «la persona protegida», y limpia el número y el hablante de la cita antes de buscarla en la burbuja.

## Revisión del cambio en la demo

**Commit revisado:** `010efb9`, hecho con Gemini en Antigravity. **Revisión:** Claude Opus 5.5, 2026-11-04.

**El cambio está bien hecho y los valores por defecto no cambian** (`ab`, `tarea`, con indicio). Se corrigieron tres detalles.
**Todavía no se probó en una llamada real:** ni con Ollama ni con ASR, porque en esta Mac no se corren modelos.

| Qué se comprobó | Cómo | Resultado |
|---|---|---|
| Pruebas del commit | En una copia sin reserva, con modelos falsos | Pasan las 31 de `replay`, las 99 de `voip` en Python y las 10 de Node |
| Camino del rol hasta el detector | Lectura de `llamada.py`, `servidor.py`, `medir.py` y `replay.py` | `PROTEGIDA` y `OTRA` llegan al SLM desde la primera frase y Tito recibe solo el texto. `--sin-indicio` saca el bloque de indicio y Tito sigue decidiendo cuándo consultar |
| Limpieza del panel con respuestas reales | Las 1.892 respuestas del SLM de v4 con roles y v3 con roles, por las funciones del panel | Los 12 motivos con etiqueta quedan bien. Citas con hablante, sin el prefijo: 23 de 68 avisos en v4 y 77 de 101 en v3 con roles |

**Corregido en la revisión:**

1. **Número en la tarjeta de aviso:** una cita con número y sin hablante se mostraba como «7. Para ver el error…». Pasa en 1 de 68
   avisos de v4 y en 1 de 101 de v3 con roles.
2. **Motivo con artículo:** «la PROTEGIDA» salía «la la persona protegida». No aparece en estas respuestas; se corrigió porque
   es una sola línea y se vería en pantalla.
3. **README de `voip`:** decía que `--sin-indicio` evalúa sin el filtro de Tito. Es falso: Tito sigue filtrando y lo único que
   desaparece es el indicio.

Se agregaron pruebas de los dos primeros y una que comprueba que el servidor le pasa el modo a la llamada: la anterior
miraba solo el manifiesto. Con eso, `voip` queda en 100 pruebas de Python y 11 de Node, todas en verde.

**Lo que sigue abierto:**

- **`--hablantes rol` solo, con la demo actual, es una combinación sin medir:** v1 con roles no se corrió. Lo medido con roles y Tito
  sin indicio es v4 (55/13) y v3 (67/34).
- **Tito sigue sin saber quién habla.** Puntúa también las frases de la persona protegida. La opinión de Luciano incluye a Tito, y este
  cambio solo cubre al SLM.
- **Citas de varias líneas:** 1 de 68 en v4 y 3 de 101 en v3 con roles. No coinciden con una sola burbuja, así que el panel marca
  entera la burbuja evaluada. Ya pasaba antes de este commit.
- **Falta una llamada de prueba** con `--hablantes rol` en la notebook de la demo, mirando el panel.

## v1 de Evaristo y control de la máquina

La corrida de v1 es [`2026-11-04_sin-indicio-150`](../2026-11-04_sin-indicio-150/conclusiones.md), de la rama
`claude/clever-fermi-fxgrx4`: commit `4916ead`, prompt `tarea`, `--sin-indicio` y el mismo mensaje que el SLM solo. Los commits
figuran con autor «Claude», así que el repositorio no muestra quién la corrió: la atribución a Evaristo es de Luciano.

**La máquina no explica la diferencia entre v1 y v3.** v1 da casi lo mismo en Windows y en Colab: SLM solo 55/18 y 55/19; Tito
con indicio 51/13 y 50/12. Repetido en Colab, SLM solo mueve 1 estafa y 1 falsa alarma, y Tito sin indicio, 1 estafa.

| | Estafas v1 → v3 | Falsas alarmas v1 → v3 |
|---|---:|---:|
| SLM solo | 55 → 65 | 19 → 47 |
| Tito con indicio | 50 → 63 | 12 → 30 |
| Tito sin indicio | 54 → 64 | 14 → 35 |

En las tres, v3 no pierde ninguna estafa ni elimina ninguna falsa alarma: todo lo de v1 está contenido en v3.

**Sacar el indicio:** con v1 suma 4 estafas y 2 falsas alarmas; con v3, 1 y 5. No apunta siempre para el mismo lado.

### Qué compraban las 10 estafas que v3 ganaba a v1

Lectura propia del primer aviso, sin revisión humana. Cita el pedido (2): ORGANISMO_PREVISIONAL-003 y PREMIO-003. Cita un paso previo
real (5): ORGANISMO_PREVISIONAL-004, SOPORTE-001, SOPORTE-005, WHATSAPP-004 y `TR-04`. Cita a la víctima, sin base (3): FAMILIAR-004,
FAMILIAR-005 y FAMILIAR-006.

Las estafas que no detecta ninguna condición son 8: ORGANISMO_PREVISIONAL-005 y 006, PREMIO-005, SOPORTE-007 y 008, WHATSAPP-007 y
`TR-12`, sin pedido de referencia, y PREMIO-001, donde Tito nunca activa. Como la meta se mide sobre
[todas las estafas](../../../../docs/gestion/seguimientos/2026-10-28.md), llegar a 60 con un detector que avisa por pedidos exige casi
todas las 64 que lo tienen.

### Lo que no conviene hacer

| Idea | Resultado | Lectura |
|---|---|---|
| Exigir más riesgo a v1 | ≥ 0,6: de 54/14 a 31/6 | Pierde 23 estafas para sacar 8 alarmas |
| Exigir más riesgo a v3 | ≥ 0,7: de 64/35 a 54/24 | Igual detección que v1, con 10 alarmas más |
| Combinar v1 y v3 | Unión 64/35, intersección 54/14 | Solo reproduce a v3 o a v1 |
| Vetar citas de la propia víctima | Saca hasta 3 alarmas en v1; 8 estafas citan solo a la víctima | Se pierde más de lo que se gana |
| Subir el umbral de Tito por su puntaje | Mediana al activar: 0,98 en estafas, 0,99 en alarmas | No las separa en ese punto. Tito no puntúa después de activar, así que no se puede simular |

Los vetos están censurados: las corridas cortan en el primer aviso y no se sabe qué pasaría después. Son cotas.

## Próxima prueba propuesta

> **Estado: propuesta sin discutir.** Todo en Colab, con Tito sin indicio. Cada condición tarda unos 11 minutos; la 4 puede
> tardar más, porque sigue después del aviso. No se lanza sin el acuerdo de Luciano.

| # | Condición | Qué responde | Qué requiere |
|---|---|---|---|
| 1 | v3 con el orden de v1 y roles | El efecto de los roles sin la cita primero, que todavía no se midió | Nada: ya existe |
| 2 | v4 con el dato de quién inició la llamada | Si bajan las 7 alarmas por dato de identificación | Anotar el dato en los 150 y pasarlo al mensaje |
| 3 | v4 sin exigir que la cita sea de OTRA | Si recupera SOPORTE-003 y SOPORTE-006 sin perder calidad | Un prompt nuevo |
| 4 | v4 con `--seguir-tras-aviso` | Si las alarmas se sostienen. Permite simular persistencia, sin decidir D08 | Pasar la opción desde el script de Colab |
| 5 | v1 con roles | Si la demo actual gana o pierde al usar el canal. Es lo que se activaría con `--hablantes rol` | Nada: ya existe |

La condición 2 supone que el sistema sabe quién inició la llamada, igual que conoce el canal. Las 7 alarmas por dato ocurren en
llamadas que inició la persona; hay que anotar ese dato en el corpus y revisar las estafas donde llama la víctima antes de usarlo.
Una búsqueda rápida encontró solo `SC-PREMIO-01-e01`, sin revisar a fondo.

**Hasta dónde alcanza:** es un cálculo con los casos apuntados, no una medición. Si la 3 recupera sus dos estafas y la 2 saca sus
7 alarmas sin cambiar nada más, v4 llegaría a 57/6. Sobrarían alarmas por debajo de la meta, pero seguirían faltando 3 estafas
para llegar a 60. Lo que más falta hoy es detección.

## Límites

- Las clases, los roles y los prompts salen de estos 150 casos, ya vistos. Una mejora acá puede ser ajuste a ellos y hay que
  validarla fuera del desarrollo cuando D08 lo defina. Las reglas evitan frases de los casos por eso mismo.
- `T_R` y las referencias no tienen revisión humana. Algunas legítimas, como `TR-11`, no se distinguen de una estafa con el
  texto solo: conviene decidir en D07 si deben contar igual.
- Las cuatro condiciones de la prueba v4 corrieron en la misma sesión. La v1 de Evaristo y la v3 sin roles, en otras, con la misma
  configuración. Las cifras de v1 en Windows no separan máquina y prompt, y los tiempos no se comparan.
- v4 reúne varios cambios: orden, roles, regla de canal propio, excepción de datos comunes y cita de OTRA. Solo el orden y los
  roles se midieron por separado, y sobre v3.
- Se repitió v1, no v3 ni v4, así que las diferencias de 1 o 2 casos no se leen como efecto.
- **Solo primer aviso:** no se sabe si la alerta se sostendría después.
- Los ejemplos ilustran fallos y no reemplazan una revisión de todos los avisos.

## Detalle de la prueba v3

### Qué se probó con v3

Las tres condiciones usan el mismo prompt, [`tarea_v3.txt`](../../prompts/tarea_v3.txt). Es v2 sin el
mínimo de riesgo 0,5, con reglas de contexto, y conserva el orden de campos de v2 (la evidencia va
primero).

| Condición | Cuándo se consulta al SLM | Qué recibe el SLM |
|---|---|---|
| **SLM solo** | En cada línea | La conversación |
| **Tito con indicio** | Desde que Tito activa | La conversación, más la línea marcada por Tito y su puntaje |
| **Tito sin indicio** | Desde que Tito activa | La misma conversación que el SLM solo |

Tito es siempre el mismo clasificador, con umbral 0,5. Una vez que activa, queda activo hasta el final
de la llamada.

### Resultados de v3

| Medida | v1 solo (Windows) | v1 Tito con indicio (Windows) | **v3 solo** | **v3 Tito con indicio** | **v3 Tito sin indicio** |
|---|---:|---:|---:|---:|---:|
| Estafas con aviso | 55/75 (73 %) | 51/75 (68 %) | **65/75 (87 %)** | **63/75 (84 %)** | **64/75 (85 %)** |
| Estafas con pedido que tuvieron aviso | 54/64 | 51/64 | **64/64** | **62/64** | **63/64** |
| Falsas alarmas | 18/75 (24 %) | 13/75 (17 %) | **47/75 (63 %)** | **30/75 (40 %)** | **35/75 (47 %)** |
| Falsas alarmas en legítimas comunes | 3/51 | 5/51 | **28/51** | **17/51** | **20/51** |
| Falsas alarmas en legítimas difíciles | 15/24 | 8/24 | **19/24** | **13/24** | **15/24** |
| Aviso antes del pedido | 25 | 17 | **43** | **36** | **42** |
| Aviso en el pedido | 25 | 29 | **20** | **23** | **18** |
| Aviso después del pedido | 4 | 5 | **1** | **3** | **3** |
| Consultas al SLM | 2.218 | 1.179 | **1.680** | **867** | **791** |
| Fallos técnicos | 0 | 0 | **0** | **0** | **0** |

Las corridas cortan en el primer aviso. Por eso v3 hace menos consultas que v1: avisa antes, no es más
eficiente. «Pedido» es la línea `T_R` de la referencia, que existe en 64 de las 75 estafas.

### Qué significan los resultados de v3

#### 1. v3 alerta más, no discrimina mejor

Contra v1, en las dos comparaciones con par, v3 no pierde ninguna estafa y tampoco elimina ninguna falsa
alarma: solo agrega avisos.

| Comparación | Estafas ganadas | Falsas alarmas nuevas |
|---|---:|---:|
| v1 solo → v3 solo | 10 | 29 |
| v1 Tito con indicio → v3 Tito con indicio | 12 | 17 |

#### 2. Lo que más se quería corregir sigue fallando

Las decisiones del prompt pedían no alertar por un dato solo cuando el contexto lo explica. TR-13 (turno
médico con DNI) y TR-08 («pasame el código» ambiguo) siguen alertando en las tres condiciones, y aparecen
falsas alarmas nuevas en gestiones comunes:

| Caso legítimo | Línea que cita el modelo | Lo que le dice a la persona |
|---|---|---|
| `CV2-D-L-BANCO-009` | «Me acuerdo que marqué el PIN y después quedó cargando.» | Le están pidiendo que confirme el PIN. Es falso: el cliente relata lo que hizo. |
| `CV2-D-L-MEDICO-001` | «¿Y el copago lo pago ahí o por transferencia?» | Le están pidiendo si va a pagar. Es la persona quien pregunta. |
| `CV2-D-L-ESCUELA-004` | «¿Querés actualizar el correo en la ficha de estudiante?» | Podría ser para acceder a sus cuentas. |
| `TR-03-negacion-y-consejo` | «¿Y si me dicen que tengo que transferir…?» | La están presionando. Es una pregunta hipotética. |

Los ejemplos son del SLM solo.

#### 3. Las estafas ganadas valen menos de lo que parece

Contar un aviso no prueba que sea por la razón correcta: **de las 64 estafas con pedido, el SLM solo avisa
antes del pedido en 43** (25 con v1). Los tres casos que Luciano pidió mirar muestran esa diferencia:

| Caso | Pedido | v3 solo | v3 Tito con indicio | Lectura |
|---|---:|---:|---:|---|
| `BANCO-003` | L19 | L14, cita L13 | **L19, cita el pedido** | Con indicio acierta. El solo avisa antes, por una frase previa sobre el mensajero. |
| `PREMIO-003` | L13 | L15, cita L13 | L16, cita L13 | Razonable: cita el pedido de documento, con demora. |
| `SOPORTE-005` | L16 | L11, cita L10 | L10, cita L10 | Avisa por «salí de la sesión», antes de pedirse la contraseña. |

Otro ejemplo: en `FAMILIAR-006`, Tito sin indicio avisa en L23, después del pedido, citando a la persona
que dice «No transfiero hasta confirmar con tu mamá».

#### 4. El modelo no respeta el formato de evidencia

El prompt pide evidencia vacía si no hay base para alertar. El SLM solo copia una cita en **1.003 de 1.568
líneas sin alerta** (64 %); con v1 no ocurre en ninguna. Además, 60 de sus 112 avisos usan «podría» para
justificar el peligro.

Pedir la cita primero explica gran parte del problema: ver [el efecto del orden](#qué-cambió-cada-factor).

#### 5. Tito sigue ayudando, y sacar el indicio no mejora

| Comparación con v3 | Estafas | Falsas alarmas | Consultas |
|---|---:|---:|---:|
| SLM solo → Tito con indicio | −2 | −17 | −813 |
| SLM solo → Tito sin indicio | −1 | −12 (elimina 13, agrega 1) | −889 |
| Tito con indicio → Tito sin indicio | +1 | +5 | −76 |

Tito con indicio es la mejor de las tres condiciones v3 por falsas alarmas. Sus 30 aparecen también en las
otras dos. Con v1, sacar el indicio da 54/75 estafas y 14/75 falsas alarmas: ver [v1 en Colab](#v1-de-evaristo-y-control-de-la-máquina).

### Casos de v3

Los nombres omiten el prefijo `CV2-D-V-` o `CV2-D-L-`.

**Estafas sin aviso en las tres condiciones (10), ninguna con pedido de referencia:**
BANCO-012, ORGANISMO_PREVISIONAL-005, ORGANISMO_PREVISIONAL-006, PREMIO-005, PREMIO-006, SOPORTE-007,
SOPORTE-008, WHATSAPP-007, WHATSAPP-008 y `TR-12-corta-antes-del-pedido`.

**Estafas con pedido que pierde Tito:** con indicio, FAMILIAR-006 y PREMIO-001; sin indicio, PREMIO-001.

**Estafas que gana el SLM solo contra v1:** BANCO-003, FAMILIAR-004, FAMILIAR-005, FAMILIAR-006,
ORGANISMO_PREVISIONAL-003, ORGANISMO_PREVISIONAL-004, PREMIO-003, SOPORTE-005, WHATSAPP-004 y
`TR-04-pedido-tras-charla-larga`.

**Estafas que gana Tito con indicio contra v1:** BANCO-003, BANCO-011, FAMILIAR-004, FAMILIAR-005,
ORGANISMO_PREVISIONAL-003, ORGANISMO_PREVISIONAL-004, PREMIO-002, PREMIO-003, SOPORTE-001, SOPORTE-005,
WHATSAPP-004 y `TR-01-pedido-indirecto-digitos`.

**Falsas alarmas en las tres condiciones (30):** BANCO-001, BANCO-002, BANCO-004, BANCO-005, BANCO-006,
BANCO-010, ESCUELA-004, FAMILIAR-002, FAMILIAR-005, MEDICO-002, ORGANISMO_PREVISIONAL-001, PREMIO-002,
SOPORTE-004, SOPORTE-005, TRABAJO-001, TRABAJO-003, WHATSAPP-001, `LAB-anses-canal-oficial`,
`LAB-arca-canal-oficial`, `LAB-banco-app-parafrasis`, `LAB-banco-revisa-app`, `LAB-familiar-llama-vos`,
`LAB-no-bajes-nada`, `LG-BANK-VERIF-01-e01`, `LG-SUPPORT-INFO-01-e01`, `TR-05-asado-con-transferencia`,
`TR-06-banco-alerta-legitima`, `TR-08-frase-cortada-candado`, `TR-11-familiar-real-pide-plata` y
`TR-13-turno-medico-pide-dni`.

El detalle línea por línea está en los CSV y en la
[comparación generada en Colab](comparacion-tres-condiciones.md).

## Cómo se corrió

| Dato | Valor |
|---|---|
| Entorno | Google Colab con GPU T4, Ollama 0.40.14 |
| Modelo | `gemma4:e2b-it-q4_K_M`, digest `b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2` |
| Parámetros | `num_ctx` 4096, seed 42, temperatura 0, corte al primer aviso, sin reglas |
| Prompts | v1 `bf4284996898c45d`, v3 `a944aadc550480b3`, v3 con el orden de v1 `e1030f8859125834`, v4 `92df75a22c2746fb` |
| Roles | [`casos/roles-protegida.json`](../../casos/roles-protegida.json), huella `8c5fcb8135d24de5` |
| Tito | RoBERTuito con regresión logística, umbral 0,5. El SHA-256 del artefacto es `fb601eaa…` en Colab y `2fcf65d7…` en Windows: difieren solo por los saltos de línea |
| Datos | Los 150 de desarrollo. Las ramas usadas no contienen la reserva |
| Código | v3: rama [`prompt-v3-colab`](https://github.com/Corchets/bitacora_tesis/tree/prompt-v3-colab), commit `a42e1b5`. v4: rama [`prompt-v4-colab`](https://github.com/Corchets/bitacora_tesis/tree/prompt-v4-colab), commit `55fe977`, [procedimiento](../../colab/README-PROMPT-V4.md). Las dos ya están en `laboratorio-luciano` |
| Duración | v4 14,5 min; v3 con roles 10,5; v3 con el orden de v1 10,9; v1 control 11,0. v3 anterior: SLM solo y Tito con indicio 31,8; Tito sin indicio 11,3 |
| Salidas | Esta carpeta, [`2026-11-04_201116_prompt-v3-b-tito-sin-indicio`](../2026-11-04_201116_prompt-v3-b-tito-sin-indicio/), [`2026-11-04_prompt-v4-tito-sin-indicio`](../2026-11-04_prompt-v4-tito-sin-indicio/) y [`2026-11-04_sin-indicio-150`](../2026-11-04_sin-indicio-150/) |

Todas las cifras de este documento salen de los CSV, desde esta carpeta y sin correr modelos, con
`python -I comparar_con_v1_colab.py` y `python -I comparar_con_v1.py`.

## Decisiones pendientes

> **Estado: propuesta sin discutir.** Depende de lo que decida el equipo.

1. **Próxima prueba:** aprobar la [propuesta](#próxima-prueba-propuesta) o elegir parte de ella.
2. **Adoptar o no v4:** por ahora no. ADR 0001 y la demo siguen con v1 y con indicio.
3. **Roles en la demo:** pasar el canal al SLM. Está preparado como opción, sin cambiar el valor por defecto. Antes conviene medir v1 con roles y probar una llamada: ver [la revisión](#revisión-del-cambio-en-la-demo).
4. **Integrar a `laboratorio-main`:** `prompt-v3-colab` y `prompt-v4-colab` ya están en `laboratorio-luciano`; decidir qué pasa de ahí.
