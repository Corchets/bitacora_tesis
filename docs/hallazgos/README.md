# Hallazgos

Un **hallazgo** es algo que aprendimos y que cambia cómo leemos los resultados, cómo diseñamos el detector o qué dice la tesis. Puede ser un resultado, una causa, un problema de método o un cambio de enfoque.

Es la capa entre la evidencia y la tesis:

- **La evidencia** (corridas y análisis en `experiments/`) guarda los números y cómo reproducirlos.
- **El hallazgo** dice qué significan, con qué seguridad y qué cambian.
- **La tesis** lo cuenta y lo cita.

## Cuándo se escribe uno

- Cuando un análisis deja una conclusión que el equipo necesita para decidir o para escribir la tesis. El resultado de rutina de una corrida queda en su carpeta.
- Cuando una conclusión anterior queda superada. Se escribe el hallazgo nuevo, el anterior pasa a `superado por HNN`, y el documento que la contenía recibe una nota con fecha que enlaza el hallazgo nuevo. El texto original no se reescribe.

## Cómo se escribe

- Un archivo por hallazgo, `HNN-titulo-corto.md`, con la [plantilla](PLANTILLA-HALLAZGO.md). El número es correlativo y no se reutiliza.
- **Estado:**
  - `vigente`;
  - `en revisión`: falta confirmarlo, por ejemplo con otra corrida;
  - `hipótesis`: sin verificar;
  - `superado por HNN`.
- **Las opiniones y propuestas** van en un bloque `> **Estado: propuesta sin discutir.**`.
- **Lo que hay que hacer** va a un issue. Lo que no se va a hacer antes de la entrega va a un issue con el label `trabajo-futuro`.
- **Si contradice algo de la tesis,** se marca en el capítulo con `> **Corregir (#N):**`, donde `#N` es el issue del que depende la corrección.
- **Cada hallazgo nuevo** suma una fila al índice.

## Índice

| ID | Fecha | Hallazgo | Tipo | Estado |
|---|---|---|---|---|
| [H01](H01-corpus-v2-se-lee-aparte.md) | 2026-11-05 | La reserva es toda corpus_v2: los resultados se leen aparte de los 53 casos cortos | método | vigente |
| [H02](H02-ruido-entre-corridas.md) | 2026-11-04 | Repetir una corrida mueve 1 o 2 casos: ±2 sobre 150 es ruido | método | vigente |
| [H03](H03-el-slm-avisa-en-el-pedido.md) | 2026-11-05 | El SLM avisa en la línea del pedido, no antes | resultado | superado por H10 |
| [H04](H04-riesgo-escrito-no-es-puntaje.md) | 2026-11-05 | El riesgo que escribe el modelo no sirve como puntaje | resultado | vigente |
| [H05](H05-estafas-sin-pedido.md) | 2026-11-05 | Un detector de pedidos no avisa las estafas sin pedido | resultado | vigente |
| [H06](H06-v4-avisa-mas-tarde-y-cita-mejor.md) | 2026-11-05 | v4 detecta lo mismo que v1 en corpus_v2, pero avisa más tarde y cita mejor | resultado | superado por H10 |
| [H07](H07-indicio-de-tito-pierde-estafas.md) | 2026-11-04 | El indicio de Tito le hace perder estafas al SLM | resultado | vigente |
| [H08](H08-tito-evita-falsas-alarmas-por-punto-ciego.md) | 2026-11-06 | Las falsas alarmas que Tito «evita» son casi todas punto ciego | resultado | vigente |
| [H09](H09-tito-clasificador-en-vez-de-compuerta.md) | 2026-11-06 | Tito se entrenó como clasificador de estafas; tenía que ser una compuerta de lo sensible | cambio de enfoque | vigente |
| [H10](H10-c-avisa-antes-del-pedido.md) | 2026-11-10 | Con el prompt de intención (C), el SLM avisa antes del pedido y suma las estafas sin pedido | resultado | vigente |
