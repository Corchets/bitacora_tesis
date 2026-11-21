# Las tres variantes: textos, porqué y fuentes

> **Estado: textos aceptados por Mateo el 2026-11-18,** sin cambios, antes del tag. Su lectura, antes de correr: la que
> más le gusta es `c-consejos`; `c-codigo` suma restricciones que pueden hacer que el modelo se comporte peor; y la
> oración final de `c-freno` («que OTRA ya sepa esos datos no prueba quién es») le parece bien. Cada uno es `c-premisa-corte-riesgo` con un solo párrafo cambiado
> ([`test_revision_producto_143.py`](../../tests/test_revision_producto_143.py) lo comprueba). Las fuentes S son las de
> [`FUENTES.md`](../2026-11-09_pedido-critico-etapa-3/FUENTES.md) y las P, las de [`FUENTES-PRODUCTO.md`](FUENTES-PRODUCTO.md).

## De dónde salen, y de dónde no

- **Salen de la [política](POLITICA.md) y de las fuentes.** Ningún texto lleva números ni frases de ejemplo.
- **El motivo para probarlas sí viene de desarrollo:** los puntos débiles se vieron en las corridas. Eso es sobreajuste
  posible en la elección de qué probar, aunque no en la redacción.
- **Qué se leyó:** las 94 legítimas, 8 estafas (las 6 de datos personales y 2 sin pedido) y los análisis. **No se
  abrieron** las estafas de código o clave que la congelada no avisa. El pedido de Mateo traía dos frases de esos
  casos como ejemplo del pedido indirecto; por eso `c-codigo` lo describe por su función y sin ejemplos.
- **Una coincidencia a la vista:** `c-freno` nombra el número de trámite por las fuentes (P16, P21, P24), y una estafa
  leída de desarrollo lo pide (`ORGANISMO_PREVISIONAL-004`). Esa estafa ya avisa en las ocho corridas, así que no hay
  ganancia que esperar de ahí.

## `c-codigo`: el código y la clave por intención

**Cambia** el párrafo del número no agendado. Lo demás del párrafo queda igual.

> Que el número no esté agendado pesa: ~~un banco, una empresa o un organismo no le pide a nadie por teléfono el código
> que le llegó ni sus claves, y~~ **un código que le llegó a PROTEGIDA, una clave o un PIN no se le dicen a nadie que
> llamó, sea quien sea y lo pida para lo que lo pida, y aunque no lo llame código ni clave: cuenta cualquier número que
> le llegó por mensaje o que usa para entrar a una cuenta.** Un familiar o un conocido que llama desde un número
> desconocido para pedir plata es una de las estafas más comunes. Si OTRA va hacia alguno de esos pedidos, tenelo en
> cuenta en el riesgo, aunque la charla sea amable. **Que OTRA le dé un número a PROTEGIDA (de reclamo, de turno, de
> seguimiento) o le diga que un código no se comparte no es pedirlo.**

- **Por qué:** la regla actual nombra a quién se disfraza el estafador, y él elige el disfraz. La política mira el
  pedido. La última oración separa pedir de dar o de advertir, que hoy se confunden
  ([hallazgos, §2](HALLAZGOS.md#2-qué-dispara-las-13-fa-estrictas-de-la-congelada)).
- **Fuentes:** «no compartas el código con nadie», sin excepciones: S09 (WhatsApp), P07 (Santander), P02 (PAMI), P11
  (Naranja X), P12 (Mercado Libre, aun si la llamada la pidió el usuario), P29 (UFECI) y P33 (Con Vos en la Web). La
  excepción «salvo que hayas llamado vos» no aparece para los códigos. «Mencionar no es pedir» es la regla central del
  [manual de anotación](../../../../docs/corpus/MANUAL-ANOTACION.md).
- **Qué puede salir mal:** que suba el riesgo cada vez que aparece la palabra «código». La última oración está para
  eso, pero es una negación, y los modelos chicos las leen mal.

## `c-consejos`: los consejos de siempre

**Cambia** el mismo párrafo, entero, por los consejos oficiales. Solo credenciales y actos sin vuelta atrás: no nombra
el DNI ni otros datos.

> Que el número no esté agendado pesa. **Valen los consejos de siempre de los bancos y los organismos: a quien llamó no
> se le dicta un código que llegó por mensaje, una clave ni los datos de una tarjeta; ningún banco ni organismo pide por
> teléfono transferir plata, instalar un programa ni operar en el cajero o en la app siguiendo sus instrucciones; y** un
> familiar o un conocido que llama desde un número desconocido para pedir plata es una de las estafas más comunes.
> **Ante la duda, lo que corresponde es cortar y llamar uno mismo al número oficial.** Si OTRA va hacia alguno de esos
> pedidos, tenelo en cuenta en el riesgo, aunque la charla sea amable.

- **Por qué:** es la idea de Mateo de darle al modelo lo que le dicen a cualquier persona. El párrafo de `c-premisa` ya
  era un consejo de esos y movió estafas de 0,2 a 0,3; acá van todos. La oración de cortar y llamar apunta a las FA en
  que OTRA manda a PROTEGIDA al 0800 de su factura.
- **Fuentes:**
  - código, clave y datos de la tarjeta: S01, S02, S05, S09, S12, S26, S37, P07 y P11;
  - transferir: S19, S21, S23, S25, S26 y S34;
  - instalar un programa: S01, S05, S26, S28 y S34;
  - operar en el cajero o en la app con instrucciones: S01, S15, S16, S19, S21 y S27;
  - cortar y llamar al número oficial: S12, S14, S16, S18, S21 y S26;
  - el falso familiar: S23 y S25.
- **En qué se diferencia de `c-codigo`:** es más amplia y más corta por tema. Dice «a quien llamó», pero no dice «aunque
  no lo llame código» ni separa pedir de dar.
- **Qué puede salir mal:** repite pedidos que ya están en la lista del párrafo anterior. Puede subir el riesgo de todo
  lo que nombre una transferencia o un pago, también en una venta.

## `c-freno`: el párrafo del DNI, por intención

**Cambia** el último párrafo de la tarea.

> ~~Una llamada legítima también puede pedir el nombre, el DNI, la fecha de nacimiento, una dirección o un correo,
> avisar un problema u ofrecer un producto. Eso solo no la vuelve una estafa.~~
>
> **El nombre, el DNI, la fecha de nacimiento, una dirección o un correo se juzgan por para qué los piden. Una llamada
> legítima los pide para algo concreto, como un turno, una entrega, un reclamo o una compra, y también puede avisar un
> problema u ofrecer un producto: eso solo no la vuelve una estafa. Pesan cuando el motivo es un premio, un beneficio,
> una deuda o un bloqueo que PROTEGIDA no esperaba, o cuando vienen con el número de trámite o una foto del documento, o
> con alguno de los pedidos de arriba. Que OTRA ya sepa esos datos no prueba quién es.**

- **Por qué:** es la respuesta a la duda del DNI ([política, §3](POLITICA.md#3-el-dni)): ni excluirlo ni endurecerlo,
  juzgarlo según el pretexto. Conserva el freno («eso solo no la vuelve una estafa») y dice cuándo sí pesa. Nombra los
  pretextos legítimos donde hoy avisa de más: un reclamo y una compra.
- **Fuentes:**
  - el número circula y cada trámite pide algo más: P18, P20, P26; P16, P24, P25;
  - el número de trámite y la foto: P16, P21, P24; S07, S16, S24 y P07;
  - los ganchos (un beneficio, un premio, una deuda, un bloqueo) ya están en el párrafo de cómo se arma una estafa:
    P05, P06, S20 y S35;
  - «que ya sepa esos datos no prueba quién es» es una **inferencia** de que el dato circula (P18, P20). Ninguna fuente
    oficial lo dice así; aparece en opiniones de especialistas (P39).
- **Qué puede salir mal:**
  - es la variante más larga (+366 caracteres) y va justo antes de la salida;
  - «una deuda» también es el pretexto de una cobranza legítima, que no está en el corpus;
  - nombrar «un reclamo o una compra» puede bajar el riesgo de un falso soporte que llama «por su reclamo».

## Longitud

| prompt | caracteres | contra la congelada |
|---|---|---|
| `c-premisa-corte-riesgo` | 2.411 | — |
| `c-codigo-corte-riesgo` | 2.689 | +278 |
| `c-consejos-corte-riesgo` | 2.695 | +284 |
| `c-freno-corte-riesgo` | 2.777 | +366 |

Las tres alargan el prompt, y ninguna lo acorta: los recortes posibles están en la
[revisión del prompt](HALLAZGOS.md#el-prompt) y quedaron afuera de esta prueba.
