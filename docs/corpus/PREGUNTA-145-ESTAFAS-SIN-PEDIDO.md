# Pregunta 5 de #145: por qué una estafa no tiene pedido

Fecha: 2026-11-09. La preparó un agente a pedido de Mateo Antenucci, para
[#145](https://github.com/Corchets/bitacora_tesis/issues/145) y para decidir cómo se cuentan las estafas sin pedido
antes de la próxima corrida de [#143](https://github.com/Corchets/bitacora_tesis/issues/143).

> **Estado: propuesta sin discutir.** Lo decide el equipo. Revisan **Luciano, Nacho y Evaristo**, como en #145. Mateo
> no revisa: analizó estas estafas en #143.

## Qué falta saber

Corpus_v2 tiene **10 estafas de desarrollo cuya referencia no marca pedido** (`t_r_linea` vacío). Una estafa sin pedido
se puede contar de varias maneras, y el equipo tiene que elegir antes de la próxima corrida. Para eso hace falta saber
**por qué** no hay pedido en cada una: si la cortaron, si es un primer contacto o si está mal armada.

## Las 10 ya están en la muestra de #145

Se comprobó el 2026-11-09 cruzando solo textos e identificadores, sin abrir respuestas:

- se comparó el texto de cada una con el de las 42 fichas del formulario de #145
  (`experiments/slm-directo/analisis/tablero/revision-145.html` en `laboratorio-luciano`, muestra `4872344bf812…`);
- también con los `case_id` de
  [`CORRESPONDENCIA-145-LUCIANO-2026-11-07.json`](CORRESPONDENCIA-145-LUCIANO-2026-11-07.json).

**Las 10 están entre las 42 fichas, y Luciano ya completó 5 de ellas.** Una hoja aparte haría leer dos veces las mismas
llamadas, y además diría qué fichas son las que no tienen pedido según la referencia. Por eso se propone sumar una
pregunta a las fichas que ya existen. Qué fichas son queda fuera del repositorio, con Mateo, para no dar la pista.

## Propuesta: una pregunta más en el formulario de #145

- **La pregunta 5 aparece en cualquier ficha donde el revisor contestó que no hay pedido** (pregunta 4), en las 42 y
  no solo en estas 10. Así no revela la referencia: depende de lo que contestó el revisor.
- **Fichas ya completadas:** el formulario las abre con la pregunta 5 pendiente si la respuesta 4 fue «no». Quien la
  revisó contesta solo esa pregunta; no repite las otras cuatro.
- **Versión del formulario:** pasa de 1 a 2. Las exportaciones de la versión 1, como la de Luciano del 2026-11-07,
  siguen valiendo y se unen con las nuevas por ficha; la pregunta 5 queda vacía hasta que se conteste.
- **Si un revisor ve un pedido** en una de estas 10, no contesta la 5. Eso ya es información para #145: la referencia
  puede estar mal.
- **Quién toca el formulario:** quien lo mantiene en `laboratorio-luciano`. Esta propuesta no lo cambia.

## Prioridad: estas 10 primero

Mateo decidió el 2026-11-09 que estas 10 llamadas se revisan primero. Para que la prioridad no delate cuáles son:

- **El formulario abre con un bloque de 16 fichas:** las 10 y 6 más, tomadas al azar entre las otras 32, en orden al
  azar. El bloque ya está sorteado y lo tiene Mateo junto con la clave, fuera del repositorio. Se le pasa a quien
  mantiene el formulario, no a los revisores.
- **Dos revisores por ficha**, como en #145. En las fichas del bloque que Luciano ya completó, solo falta su pregunta 5
  y el segundo revisor.
- Las otras 26 fichas siguen después, sin cambios.

## La pregunta

**5. Si no hay pedido, ¿por qué?** Una letra y el motivo con los números de línea (`sin_pedido`,
`motivo_sin_pedido`):

| Letra | Nombre | Cuándo |
|---|---|---|
| `a` | **Cortada** | La llamada iba hacia un pedido y termina antes por algo que el estafador no planeó: la persona corta para verificar, se cae la conexión, hay una interrupción en la casa. Si hubiera seguido, se esperaría un pedido. |
| `b` | **Primer contacto** | El estafador termina la llamada a propósito sin pedir nada, y deja preparado otro contacto: anuncia un SMS, un llamado o una visita, deja un número, fija un turno o gana confianza para después. |
| `c` | **Incoherente** | Como estafa no cierra: no se entiende qué gana quien llama, la llamada se contradice, o leída entera no es una estafa. |
| `otra` | — | Ninguna de las tres. Explicala en el motivo. |

Si dudás entre dos letras, poné la que te parezca más probable y nombrá la otra en el motivo. En una llamada
legítima, la pregunta no se contesta.

**Antes de responder, no leas** [`CIFRAS-LIMPIEZA-DESARROLLO.md`](../../experiments/slm-directo/casos/CIFRAS-LIMPIEZA-DESARROLLO.md),
la propuesta de la etapa 2 ni los análisis de #143: dicen cuántas estafas sin pedido avisó cada detector.

## Para qué se usa

> **Estado: propuesta sin discutir.** La decide el equipo antes de la próxima corrida (§3.5 de la
> [propuesta](../../experiments/slm-directo/corridas/2026-11-07_alcance-etapa-2/PROPUESTA-SIGUIENTE.md), sin
> commitear). Se escribió antes de tener respuestas.

- **Se informan siempre los dos denominadores** (D07, reunión con el tutor del 2026-11-11): las 46 estafas y las 36 con
  pedido.
- **`a` y `b` son estafas reales sin pedido:** siguen en las 46.
- **`c` sale de la cifra principal** y se informa aparte, igual que una legítima dudosa. No se borra.
- **Desacuerdos:** si los dos revisores no coinciden en la letra, se discute con la guía de #145. Si no se resuelve,
  la llamada queda en las 46 y el desacuerdo se informa.
- La misma regla se aplica después a las estafas sin pedido de la reserva, sin mirar resultados (#45).
