# #52: dónde avisó el detector y dónde habría avisado Luciano

> **Estado: propuesta sin discutir.** Pedida por Luciano el 2026-11-20. Cruza las 26 fichas que llenó en #145
> ([`REVISION-145-LUCIANO-2026-11-10.json`](../../../../docs/corpus/REVISION-145-LUCIANO-2026-11-10.json)) con la
> corrida de desarrollo de la [evaluación final](../../corridas/2026-11-12_evaluacion-final/analisis.md)
> (`c-consejos-corte-riesgo`, 2026-11-19, rama `reserva/test`). No usa nada del test. Las cifras salen de
> [`comparar.py`](comparar.py); la salida completa está en [`comparacion.json`](comparacion.json).

**En una oración:** en las estafas donde los dos avisan, el detector cae cerca de la sospecha de Luciano en 6 de 15
y antes en 5. Pero los avisos tempranos son por quién llama («los bancos rara vez llaman así»), no por lo que pide, y
**en dos llamadas donde OTRA pide la contraseña o el código de WhatsApp, el detector no avisa nunca.**

## Qué se compara

- **«Dónde habría avisado Luciano»** es la línea de la primera sospecha de su ficha: «la primera línea donde una
  persona atenta tendría un motivo concreto para sospechar».
- **«Dónde avisó el detector»** es la primera línea de OTRA con «riesgo ≥ 0,3», la misma regla que la evaluación final.
- **«Igual»** es una diferencia de 2 líneas o menos: en una conversación alternada, es el turno siguiente de OTRA.
- **Las 26 fichas no son una muestra al azar.** La muestra de #145 juntó a propósito estafas que los detectores
  viejos perdían, estafas que avisaban y legítimas nuevas. Sirven para ver casos, no para estimar porcentajes.
- **Seis fichas no son ciegas** (14, 23, 31, 39, 41 y 42): antes de anotarlas, Luciano supo que eran estafas sin
  pedido ([REVISIONES-HUMANAS-LUCIANO.md](../../../../docs/corpus/REVISIONES-HUMANAS-LUCIANO.md#captura-del-2026-11-10)).

## Resultado

| | estafas (21) | de esas, ciegas (15) | legítimas (5) |
|---|---|---|---|
| Avisan los dos, en la misma línea (±2) | **6** | 4 | — |
| Avisan los dos, el detector antes | **5** | 2 | — |
| Avisan los dos, el detector después | **4** | 3 | — |
| Solo sospecha Luciano | **3** | 3 | 0 |
| Solo avisa el detector | **3** | 3 | **2** |
| Ninguno | 0 | 0 | 3 |

**Contra el pedido** (la línea T_R de la referencia del corpus), en las 11 estafas que lo tienen: el detector avisa a
tiempo en 6, tarde en 2 y no avisa en 3. Contra los pedidos que marcó Luciano (7): a tiempo en 3, tarde en 2 y no
avisa en 2.

**El juicio de Luciano sobre las 21 estafas:** «sí» en 5, «dudoso» en 13 y «no» en 3. Aun así sospechó en 18.

## Llamada por llamada

`S` es la sospecha de Luciano, `A` el aviso del detector y `T_R` el pedido de la referencia. Los motivos están
resumidos; los literales, en `comparacion.json`.

### Coinciden (±2 líneas)

| ficha | caso | S | A | T_R | Luciano | detector |
|---|---|---|---|---|---|---|
| 08 | SOPORTE-002 | 5 | 7 | 13 | pide instalar un programa | «no suelen pedir asistencia remota así» |
| 16 | WHATSAPP-001 | 7 | 9 | 9 | manda un código por WhatsApp | «no se deben compartir códigos» |
| 17 | ORGANISMO_PREVISIONAL-004 | 8 | 8 | 14 | reconstruir un legajo muy viejo | «rara vez piden documentos así» |
| 21 | PREMIO-002 | 11 | 13 | 13 | pagar para cobrar un premio | «transferencia para un cargo de activación» |
| 31* | WHATSAPP-007 | 2 | 4 | — | procedencia rara, pide aislamiento | genérico: «siempre es mejor verificar» |
| 41* | SOPORTE-007 | 4 | 4 | — | falso soporte, información poco clara | genérico: «no se puede verificar» |

**En las cuatro ciegas, los dos ven lo mismo y por el mismo motivo:** un pedido concreto (programa remoto, código,
pago) o algo raro en el pretexto. Es lo que el detector hace bien.

### El detector antes

| ficha | caso | S | A | T_R | Luciano | detector |
|---|---|---|---|---|---|---|
| 05 | ORGANISMO_PREVISIONAL-005 | 15 | 2 | — | no contesta y solo habla | genérico: «no se puede verificar la identidad» |
| 10 | BANCO-009 | 13 | 5 | 13 | pide el PIN en la app | «los bancos no suelen pedir información sensible así» |
| 14* | ORGANISMO_PREVISIONAL-006 | 7 | **1** | — | quien llama tiene poca información | genérico: «no se puede verificar» |
| 39* | BANCO-012 | 7 | **1** | — | no tiene información suficiente | «los organismos rara vez llaman así» |
| 42* | BANCO-011 | 12 | 4 | — | lo llama el banco, trata de aislarlo | «los bancos rara vez llaman así» |

**Cuatro de los cinco avisos tempranos son por la identidad de quien llama, no por lo que dice.** En 14 y 39 avisa en
la primera línea, con una frase de presentación («de control de operaciones», «de la mesa de regularización»). Acierta
porque en el corpus generado un organismo que llama casi siempre es una estafa. **Es el mismo mecanismo que da las FA
en las llamadas reales de call center:** ahí una empresa que llama es lo normal.

### El detector después

| ficha | caso | S | A | T_R | Luciano | detector |
|---|---|---|---|---|---|---|
| 01 | PREMIO-005 | 7 | 16 | — | no sabe por qué lo llaman | presión para asegurar un beneficio |
| 04 | FAMILIAR-004 | 5 | **24** | 22 | pide plata | «arreglar un problema financiero» |
| 09 | WHATSAPP-006 | 21 | **26** | 25 | raro lo del grupo de WhatsApp | «confirmar algo que apareció inesperadamente» |
| 23* | PREMIO-006 | 2 | 17 | — | ganar un premio sin haber participado | presión por la demora del correo |

- **En 04 y 09 avisa una línea después del pedido:** llega tarde. En 04 el riesgo está en 0,2 desde la línea 8 y
  sube a 0,3 recién en la 24, después de «si apareciera esa diferencia en mi cuenta» (l. 22).
- En 01 y 23 avisa por la presión, no por lo que a Luciano le llamó la atención (el premio que nadie esperaba).

### Solo Luciano

| ficha | caso | S | T_R | Luciano | riesgo del detector |
|---|---|---|---|---|---|
| 03 | PREMIO-003 | 25 | 13 | mucha urgencia; para él no es estafa | 0,1 hasta la l. 21, después 0,2 |
| **06** | SOPORTE-005 | 10 | 16 | modificar datos de la cuenta, **contraseña** | **0,2 de la l. 4 al final** |
| **15** | WHATSAPP-003 | 9 | 12 | **le pide el código** | **0,2 de la l. 8 al final** |

**Son los dos errores más graves de la muestra.** En 06, OTRA pide «la contraseña anterior» (l. 14 y 16); en 15,
«leeme los seis dígitos» (l. 12) y, cuando PROTEGIDA dice que el mensaje pide no compartirlo, «es una advertencia
general». **La política dice que eso se avisa siempre, y el detector se queda en «no sé» toda la llamada.** Las reglas
de palabras clave avisan en las dos.

### Solo el detector

| ficha | caso | clase | A | T_R | Luciano | detector |
|---|---|---|---|---|---|---|
| 11 | WHATSAPP-008 | estafa | 9 | — | no parece | «no salgas de la pantalla de chats» |
| 12 | ORGANISMO_PREVISIONAL-002 | estafa | 9 | 9 | no parece | «no se dan el CUIL y la fecha de nacimiento por teléfono» |
| 19 | SOPORTE-008 | estafa | 1 | — | no parece, pero le genera dudas | «los organismos rara vez llaman así» |
| 02 | LEG2-CC-06 | legítima | 6 | — | no | «una promoción muy atractiva» |
| 20 | LEG2-ST-03 | legítima | 4 | — | no | «te piden el DNI para un servicio que no esperabas» |

- **En 11, 12 y 19 el detector acierta donde Luciano no veía estafa.** En 12 el aviso cae justo en el pedido. En 19
  es otra vez un aviso por la presentación.
- **Las dos FA son las de siempre:** una venta leída como estafa (02) y el DNI (20). Por la política, el DNI solo no
  debería disparar el aviso.

## Lectura

1. **Cuando hay un pedido concreto, el detector y Luciano ven lo mismo** (08, 16, 17, 21 y 12): el detector repite el
   consejo oficial que corresponde.
2. **Cuando el detector «se adelanta», en general es porque juzga quién llama.** Avisa en la presentación, con una
   frase genérica. En los datos generados eso suma aciertos; en las llamadas reales es la fuente de las FA. Es la misma
   conclusión de la evaluación final, vista desde adentro.
3. **El detector puede quedarse en 0,2 durante el pedido más claro** (06 y 15). No es que avise tarde: no cruza el
   umbral nunca. Coincide con el diagnóstico de la
   [exploración](../../corridas/2026-11-20_exploracion-reales/README.md#de-dónde-salen-los-candidatos): la escala real
   del modelo tiene tres valores, y «sospecho» y «ya pidió» caen en el mismo 0,3.
4. **Un humano que lee una estafa generada muchas veces no la ve como estafa** (13 «dudoso» y 3 «no» de 21). Es el
   límite ya registrado en [H05](../../../../docs/hallazgos/H05-estafas-sin-pedido.md): muchas estafas del corpus no
   llegan a pedir nada.

## Límites

- **26 llamadas, elegidas a propósito** entre las que los detectores viejos perdían y las que avisaban. No se
  generalizan como porcentajes.
- **Un solo revisor y sin adjudicar.** Las marcas de Luciano son su criterio, no una referencia acordada.
- **Seis fichas no son ciegas** (marcadas con `*`). Las cifras ciegas van aparte en la tabla.
- **Todo es desarrollo, en texto limpio.** Las coreanas, con sus 9 fichas de Luciano (KO-01 a KO-09), no entran: los
  resultados del detector sobre ese set están en el ZIP de Mateo y no se subieron.

## Qué queda

> **Estado: propuesta sin discutir.**

- **Usar 06 y 15 en la defensa como el ejemplo honesto del límite:** el detector no avisa ante el pedido más claro.
  Y 08 y 16 como el ejemplo de lo que hace bien.
- **Sumar las coreanas** si Mateo sube los resultados del set externo: hay 9 fichas de Luciano para cruzar, aunque las
  marcas están en segmentos de la fuente y hay que pasarlas a líneas.
