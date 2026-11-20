# Regla de pedido crítico sumada al modelo (exploración)

> **Estado: propuesta sin discutir.** Pedida por Luciano el 2026-11-20, solo en `laboratorio-luciano`. **Es
> exploración posterior a la evaluación final:** la regla se escribió y se ajustó después de leer los fallos del test
> reservado y de desarrollo, así que sus cifras no reemplazan a las de la evaluación. Se informan al lado.

**En una oración:** una regla que solo mira si OTRA pide dictar un código o una clave, transferir o instalar algo,
sumada al modelo, sube los avisos a tiempo del test de 53 a 63 sobre 80, sin sumar ningún aviso falso en desarrollo,
en el test ni en las 33 legítimas reales.

## Qué hace

[`regla_pedido_critico.py`](../../regla_pedido_critico.py). Una línea de OTRA dispara si pide:
- **dictar** un código, una clave o un PIN a OTRA («leeme los seis dígitos», «decímelo» después de «me llegó un
  código»), o **escribir una clave** donde dice OTRA («ingresala en el campo»);
- los datos de la tarjeta, **transferir** o pagar, **instalar** un programa o compartir la pantalla, una foto del
  documento o el número de trámite.

No disparan las menciones ni las advertencias: «ese código lo cargás vos en la app», «no se paga nada», «no compartas
el código», «lo hacemos por acceso remoto». El número de DNI, el nombre y la dirección no cuentan. Es la lista de la
[política de producto](../../corridas/2026-11-10_revision-producto/POLITICA.md) (§2 y §4), escrita antes.

**El híbrido** avisa en la primera línea en que avisa el modelo o la regla. El aviso del modelo sale de las corridas
de la evaluación final, así que no hubo que correr nada: [`evaluar.py`](evaluar.py), salida en [`salida.md`](salida.md).

## Resultado

| conjunto | detector | estafas avisadas | a tiempo | avisos en legítimas |
|---|---|---|---|---|
| **Test** (100 + 56) | modelo | 73 | 53/80 (66 %) | 15/56 |
| | **híbrido** | **80** | **63/80 (79 %)** | **15/56** |
| Desarrollo (46 + 94) | modelo | 40 | 26/36 | 20/94 |
| | híbrido | 44 | 28/36 | 20/94 |
| Legítimas reales (33) | modelo | — | — | 21/33 |
| | híbrido | — | — | 21/33 |

La regla sola avisa poco (30 de 100 estafas del test), pero no se equivoca nunca: cero avisos en las 183 legítimas.

**Lo que arregla:** casi todo son los pedidos de código y de clave que el modelo dejaba pasar. En desarrollo agarra
las dos fichas de Luciano que el modelo no avisaba: «leeme los seis dígitos» (15, a tiempo) y «la contraseña
anterior» (06, dos líneas después del pedido). En el test, siete estafas que no avisaba pasan a avisar a tiempo, y
otras tres que avisaba tarde pasan a avisar a tiempo.

**Lo que no arregla:** los avisos falsos. La regla no los suma, pero tampoco los baja: siguen siendo los del modelo.

## Cómo se llegó

Tres versiones, todas sobre los mismos datos:
1. objeto crítico en la línea o en las dos anteriores, con cualquier pedido dirigido: +11 avisos a tiempo en el test,
   pero +7 FA en desarrollo, por menciones («te va a llegar un código, lo cargás vos en la app»);
2. el código o la clave solo si se los dictan a OTRA, y el objeto anterior solo si la frase lo retoma («decímelo»):
   +11 FA en desarrollo, porque sin acentos «pagá» es igual a «está paga» o «no se paga nada»;
3. los imperativos sin pronombre se buscan con acento, y el acceso remoto y el documento también exigen un pedido: la
   versión de arriba. El último ajuste salió de una legítima real (`EXT-3361`, «la mejora la hace el departamento
   técnico por acceso remoto»).

## Límites

- **Se ajustó mirando estos mismos casos.** El cero en las legítimas es optimista; con otras llamadas va a aparecer
  alguno.
- **Depende de los acentos y del voseo escrito.** El texto del ASR en vivo puede no traer acentos ni puntuación: ahí
  la regla avisa menos. Hay que probarla con transcripciones de la demo antes de usarla en vivo.
- **Mira una línea y dos de contexto.** Un pedido armado a lo largo de varias líneas («aceptá y pasame la serie que
  sale abajo») se le escapa.

## Qué queda

> **Estado: propuesta sin discutir.**

- **Para la tesis:** informarla como exploración, al lado de la evaluación final: «con una regla de pedidos críticos
  sumada, los avisos a tiempo del test suben de 66 % a 79 % sin sumar avisos falsos». Aclarar que se ajustó con el
  test a la vista.
- **Para la demo:** sumarla al servidor como un detector `slm+regla`, si se decide, y probarla antes con
  transcripciones reales del ASR.
