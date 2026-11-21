# Lote nuevo de legítimas entrantes para test (#45): instrucciones del generador

Escritas el 2026-11-07, antes de generar. El generador trabaja solo con estas instrucciones: no lee prompts, corridas,
resultados ni casos del corpus, y no usa git ni la web. Las cifras de forma de abajo salen de comparar, por script, las
estafas de desarrollo y de la reserva (largo, variantes de ASR, DNI, «usted» y comienzo). No salen de ningún detector.

## Qué hay que escribir

Llamadas telefónicas escritas y ficticias, en español rioplatense, para el conjunto de test de un detector de estafas
telefónicas. Todas son **legítimas** y **entrantes**: alguien llama a PROTEGIDA desde un número que ella no tiene
agendado, y PROTEGIDA no sabe quién es hasta que se presenta.

Son negativas difíciles. Aparecen cosas que también aparecen en estafas: una cuenta, una tarjeta, un pago, un código,
un dato personal, una oferta de trabajo, un apuro. Pero quien llama es quien dice ser, y lo que pide o propone es lo que
haría de verdad esa empresa, organismo o persona en la Argentina.

## Reparto

| Generador | Familia (`familia`) | Llamadas | `case_id` |
|---|---|---:|---|
| 1 | `seleccion_personal`: consultoras y áreas de personal que llaman por una postulación | 7 | `ENT-T-SELECCION-NNN` |
| 1 | `banco`: el banco o la tarjeta llaman por un movimiento, una compra, un producto o un trámite | 7 | `ENT-T-BANCO-NNN` |
| 1 | `comercial`: ventas, ofertas, seguros, cobranzas de una deuda real | 7 | `ENT-T-COMERCIAL-NNN` |
| 1 | `delivery`: correo, paquetería, envíos y retiros | 7 | `ENT-T-DELIVERY-NNN` |
| 2 | `medico`: turnos, resultados, obra social, farmacia | 6 | `ENT-T-MEDICO-NNN` |
| 2 | `soporte`: internet, telefonía, cable, servicio técnico que coordina una visita | 6 | `ENT-T-SOPORTE-NNN` |
| 2 | `tramite`: municipio, licencia de conducir, registro, escuela, consorcio | 6 | `ENT-T-TRAMITE-NNN` |
| 2 | `compraventa`: un particular que llama por algo que PROTEGIDA publicó para vender o alquilar | 5 | `ENT-T-COMPRAVENTA-NNN` |
| 2 | `encuesta`: encuestas de opinión, de satisfacción o de mercado | 5 | `ENT-T-ENCUESTA-NNN` |

Cada generador escribe 28 llamadas. Tipos (`tipo_legitima`), por generador: 13 `pedido_razonable`, 8
`mencion_sin_pedido` y 7 `cotidiana`, repartidos entre sus familias.

- `cotidiana`: no piden datos ni plata.
- `pedido_razonable`: quien llama pide un dato, una confirmación o una acción que tiene sentido en esa situación.
- `mencion_sin_pedido`: se nombra algo delicado (un código, una clave, una tarjeta, una transferencia, un problema con
  una cuenta) sin pedirlo.

## Forma

- **Largo:** de 20 a 38 líneas por llamada, y al menos dos tercios entre 20 y 26.
- **Líneas:** cada una empieza con `A: ` o `B: `. A es quien habla primero.
- **Comienzo:** en la mitad de las llamadas (14 por generador) habla primero PROTEGIDA, que atiende. En la otra mitad la
  transcripción arranca con quien llama, porque el saludo de PROTEGIDA no quedó grabado. La primera línea casi nunca es
  un «hola» solo: suele tener entre 5 y 15 palabras.
- **Trato:** voseo rioplatense. El «usted» aparece en una llamada como mucho, por generador.
- **Datos:** variá qué se pide o se confirma: nombre, dirección, horario, mail, número de pedido, de reclamo o de
  cliente, patente, fecha de un turno, los últimos números de algo. Por generador, el **DNI** aparece (pedido o
  nombrado) en 2 llamadas como mucho, y la **fecha de nacimiento**, en 3 como mucho.
- **Variantes de ASR** (`variante_asr: true`): 9 llamadas del generador 1 y 8 del generador 2. Todo en minúsculas y sin
  puntuación, con algunas palabras mal reconocidas, números escritos como suenan o en cifras, frases que se cortan o se
  pisan y muletillas. Las demás llevan puntuación normal.
- **Ficción:** nombres de personas y empresas, montos y números, todos inventados. Sin marcas reales.
- **Independencia:** cada llamada es una situación distinta. No reescribas otra del lote cambiando nombres o montos.
- **Conversación real:** aclaraciones, preguntas de PROTEGIDA, a veces una duda o una desconfianza que quien llama
  responde bien, y un cierre.

## Salida

Un archivo JSONL, con una llamada por línea:

```json
{"case_id": "ENT-T-BANCO-001", "familia": "banco", "tipo_legitima": "pedido_razonable", "variante_asr": false, "protegida": "A", "situacion": "Una oración que distingue el episodio.", "que_prueba": "Una oración: qué la hace difícil.", "lineas_pedido": [6, 14], "lineas_mencion": [], "texto": ["A: …", "B: …"]}
```

- `protegida`: `"A"` o `"B"`, según quién es PROTEGIDA en esa llamada.
- `lineas_pedido`: números de línea (desde 1) donde quien llama pide un dato, una confirmación o una acción.
- `lineas_mencion`: números de línea donde se nombra algo delicado sin pedirlo.

Al terminar, comprobá con un script la cantidad por familia y por tipo, el largo de cada llamada, cuántas tienen
variantes de ASR, cuántas nombran el DNI, la fecha de nacimiento o el «usted», quién habla primero y que cada línea
empiece con `A: ` o `B: `. Corregí lo que no cumpla.
