## Segunda vuelta: lectura del token y prompt C

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre.

### Resultado de la etapa 2 (corrida el 2026-11-07, analizada el 2026-11-09)

La regla se escribió antes de correr, y Mateo la confirmó (tag `colab/143-etapa-2`, commit `d127953`).
- **Prompts:** los tres usan el JSON cortado (ADR 0006).
- **Vista, la del alcance:** las 46 estafas de corpus_v2 (36 con pedido) y las 94 legítimas entrantes de #155.
- **Punto de comparación:** las FA de `v4-corte` con «riesgo ≥ 0,4 o alerta», F = 42/94. Cada configuración usa su
  regla con FA ≤ F que avisa más estafas.
- **Humo:** pasó en los dos prompts nuevos (48/48), y no se ajustó nada.

| configuración | regla | estafas (de 46) | antes del pedido (de 36) | FA (de 94) | repetición, misma regla |
|---|---|---|---|---|---|
| `v4-corte` (referencia) | riesgo ≥ 0,4 o alerta | 28 | 10 | 42 | — |
| C (`c-json-corte`) | riesgo ≥ 0,3 o alerta | 36 | 17 | 27 | 36 / 16 / 26 |
| `v4-premisa-corte` | riesgo ≥ 0,4 o alerta | 27 | 11 | 41 | 27 / 11 / 42 |

- **Según la regla, se adopta C con «riesgo ≥ 0,3 o alerta», provisorio hasta la reserva.**
  - Avisa 8 estafas más y 7 avisos más antes del pedido, con 15 FA menos, y la repetición lo sostiene.
  - `v4-premisa` queda dentro de ±2: la oración del alcance sola no cambia a v4.
- **Dónde gana** (diagnóstico, escrito después de ver los resultados):
  - las 8 de más son todas estafas sin pedido: C avisa 9 de 10, y v4 1;
  - con pedido, los dos detectan 27/36, pero C avisa antes: la mediana del adelanto es de 4 líneas, contra 0. La
    detección útil (antes o en el pedido) queda en 25/36 para los dos;
  - las FA bajan porque C deja de alertar por el DNI: 35 de las 42 FA de v4 caen justo en la línea en que la legítima
    pide un dato personal, y 6 de las de C.
- **Lo que le queda a C:**
  - 14 de sus 27 FA caen al comienzo de llamadas legítimas del banco o de soporte, que empiezan igual que una estafa;
  - no ve pedidos explícitos de un código o una contraseña cuando el contexto no parece estafa (un taller, un club, un
    curso): son 7 de sus 12 errores de detección.
- **Cuidados:**
  - el punto de C está en un solo escalón: con 0,4 da 15/46 y 9/94;
  - 59 de sus 63 avisos son solo por riesgo, y el motivo de esos avisos no se midió;
  - fuera del alcance avisa más: 13/51 FA en corpus_v2 entero.
- **Propuesta para seguir (la decide el equipo):**
  - avisar en dos niveles: precaución con C ≥ 0,3 y alerta con un pedido crítico;
  - probar C más una pregunta literal de pedidos críticos, sin datos personales. Con la referencia como oráculo, el
    techo de esa suma es de 44/46 estafas y 35/36 avisos a tiempo, sin FA nuevas.

Detalle en `experiments/slm-directo/corridas/2026-11-07_alcance-etapa-2/analisis.md`.

### Resultado de la etapa 1 (corrida el 2026-11-06, analizada el 2026-11-07)

La regla de más abajo se escribió antes de correr: está en `analizar.py` desde el commit `b9fd09a` (tag
`colab/143-ronda-2`, 2026-11-06 a las 19:53 de Argentina). Colab corrió a las 20:21, con el mismo setup que la línea
base. La humo de formato pasó en las tres variantes (48/48) y no se ajustó nada.

| corpus_v2, FA ≤ 7/51 | punto | estafas (de 46) | antes del pedido (de 36) | FA (de 51) | repetición, mismo punto |
|---|---|---|---|---|---|
| v4-L | umbral 0,4 sobre el riesgo esperado | 27 | 11 | 7 | 27 / 11 / 8 |
| v4 JSON (línea base) | riesgo ≥ 0,4 o alerta | 29 | 11 | 7 | — |

- **Según la regla, −2 queda dentro de ±2, así que decide la latencia.** La repetición confirma el −2.
- **Latencia de la etapa 1** (T4, en las mismas 2.225 líneas): v4-L tarda 237 / 327 ms (p50 / p95), contra 432 / 546 del
  JSON, porque escribe 12 tokens en vez de 41.
- **Adopción, según la regla: sí, v4-L por latencia.** El equipo decidió otra cosa (ver abajo).
- **Pero la ganancia es el corte, no la lectura:**
  - v4-L corta el JSON antes de `alerta_sugerida`. Sin ese campo, la base da lo mismo que v4-L (27/46, 11 antes, 7/51):
    las 2 estafas de diferencia salen de ahí.
  - Con el mismo corte, el riesgo escrito da 26/46. Leer la distribución suma 1, dentro del ruido.
  - Esta vez el puntaje sí sale continuo: el dígito más probable tiene P < 0,9 en el 70 % de las líneas. Pero con
    FA ≤ 7 no aparece un punto mejor.
- **Decisión del equipo (2026-11-07): se queda el JSON de v4 con «riesgo ≥ 0,4 o alerta»** (29/46). La regla se
  escribió para un SÍ/NO de un token, donde leer y cortar eran lo mismo; con v4-L se separan, y v4-L perdía las 2
  estafas de `alerta_sugerida`.
  - Para bajar la latencia, el JSON se corta después de `alerta_sugerida` (unos 20 tokens en vez de 41). El riesgo y la
    alerta salen del mismo cálculo que en el JSON completo, así que la detección no cambia más que por el ruido entre
    corridas. Se estiman 270 a 320 ms por línea, contra 432.
  - `motivo` y `evidencia` se piden en una segunda consulta, solo al avisar. Las dos consultas ya se midieron en Colab
    (ver «JSON cortado», abajo); falta el teléfono (#141).
  - La lectura del token queda para después de un ajuste fino: en Open-Jev (arXiv 2609.23959), leer el token dio un
    AUROC de 0,69 sin ajustar y ~0,97 con LoRA.
- **Solo para mirar:**
  - Dentro del alcance, v4-L llega a 46/46 con 1/7 FA. Pero el umbral (0,11) sale de 7 legítimas fáciles: sobre las 51
    de corpus_v2 avisaría en 36.
  - En los controles, v4 JSON y v4-L también avisan en las 3 legítimas de ventas y préstamos.

Detalle en `experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analisis.md`.

### JSON cortado (corrido y analizado el 2026-11-07)

El criterio se escribió antes de correr (tag `colab/143-json-cortado`): entre el cortado y el JSON completo en la misma
sesión, el riesgo escrito igual en al menos el 93 % de las líneas, y como mucho un 1 % de líneas inválidas. La humo
pasó: con el JSON completo, la alerta termina en el token 23 en las 48 líneas, y el corte es a los 24.

- **Pasa:** el riesgo escrito coincide en el 93,4 % de las 2.773 líneas (95,0 % hasta el aviso), y no hay inválidas.
  La regla avisa en la misma línea en los 150 casos. En corpus_v2, las dos corridas dan 29/46, 12 antes del pedido y
  7/51 FA.
- **Latencia antes del aviso** (T4, p50 / p95): 288 / 362 ms contra 393 / 482 del JSON completo, 105 ms menos por
  línea.
- **En la línea del aviso:**
  - la decisión se conoce a los 269 ms, y motivo y evidencia llegan con la segunda consulta, 661 / 811 ms después;
  - si la app espera el motivo, el total es de 938 ms, contra 783 del JSON completo en esas mismas líneas;
  - la segunda consulta da motivo en 74 de los 78 avisos, y el JSON completo en 59, porque no lo escribe cuando avisa
    solo por el riesgo.
- **Falta** medir las dos consultas en el teléfono (#141).

Detalle en `experiments/slm-directo/corridas/2026-11-07_json-cortado/analisis.md`.

### Por qué hay una segunda vuelta

La primera vuelta no fue una prueba justa para el token, por dos motivos:

- **A1 hacía otra pregunta.** «¿OTRA le pide algo de la lista?» tiene un SÍ literal cuando piden el nombre o el DNI, y las
  excepciones del prompt hablan de *alertar*, no de *pedir*.
- **La pregunta quedaba antes de la transcripción.**

### Alcance

**Lo decidió el equipo el 2026-11-06:** el detector corre solo en **llamadas entrantes de números no agendados**.

**Por qué:**
- Lo mismo hacen Scam Detection de Google, que no se usa en llamadas con contactos, y el detector de Samsung.
- 7 de las 13 falsas alarmas de v4 eran pedidos de datos en llamadas que inició la persona, y en el producto esas
  llamadas no se escuchan.

**Agujeros conocidos:** números de bancos falsificados, la cuenta de WhatsApp robada a un familiar y las estafas que
te hacen llamar a vos.

**Cómo se anotó:** quién inició cada caso de desarrollo se anotó a ciegas, sin la clase ni los resultados, con una regla
escrita antes (`casos/alcance-desarrollo.json`).

**Problema del corpus:**
- En corpus_v2, las 46 estafas son entrantes y 44 de las 51 legítimas las inicia la persona. Dentro del alcance quedan
  7 legítimas, todas de familiares y compañeros de trabajo.
- Como dato, v4 JSON con «riesgo ≥ 0,3 o alerta» avisa 41/46 estafas, 23 antes del pedido, con 1 falsa alarma sobre 7
  legítimas.
- Evaristo genera legítimas entrantes de números desconocidos: ventas, el banco que avisa un movimiento, el correo,
  turnos y encuestas.

### Dos etapas

**Etapa 1 (corrida el 2026-11-06, sobre los 150):** v4-L contra v4 JSON, con la regla de la primera vuelta (FA ≤ 7/51). Es la prueba de la
forma de leer: el mismo prompt y los mismos casos. La humo controla además el formato de `c-sino` y `c-digito`, sin mirar
sus resultados.

| Configuración | Qué responde | Contra qué |
|---|---|---|
| `v4-lectura` (v4-L): el JSON de v4 tal cual, cortado después del primer decimal del riesgo | ¿Leer la distribución del riesgo dentro del mismo JSON le gana al riesgo escrito? | v4 JSON |

**Etapa 2 (con las legítimas nuevas; lo que se corrió, según las decisiones de Mateo del 2026-11-07):**
- **Configuraciones:** solo JSON, todos cortados.
  - `v4-corte` es la referencia.
  - `c-json-corte` (el prompt C con el alcance: mira la intención y permite avisar antes del pedido) y
    `v4-premisa-corte` (v4 con la oración del alcance) son las candidatas.
  - Cada candidata corrió dos veces; la repetición, sobre los 140 dentro del alcance.
  - Sin `c-sino`, `c-digito` ni v4-L: la lectura del token quedó para después de LoRA.
- **Vista:** las 46 estafas de corpus_v2 y las 94 legítimas entrantes de desarrollo.
- **FA:** no hay un límite fijo. Se compara en la curva, con las FA de `v4-corte` como punto (ver arriba).
- El código de esa vista se escribió antes de correrla.

### Regla (las dos etapas)

- **Puntaje:** P(SÍ), el dígito esperado dividido por 9, o el riesgo esperado. Se usan las mismas políticas, la misma
  grilla y la misma elección que en la primera vuelta. Se elige en la primera corrida.
- **Adopción, como dice #143:** con 3 estafas más o mejor, se adopta, provisorio hasta la reserva. Con 3 menos o peor,
  no. Dentro de ±2, decide la latencia.
- **Repetición:** una configuración de token solo cuenta si su repetición, en el mismo punto, tampoco queda 3 o más
  estafas por debajo de la base.
- **Filtro:** solo la humo de formato. Los manuales no se usan para filtrar.
- **Aparte, solo para mirar:**
  - las estafas sin pedido;
  - las 6 estafas que piden un dato de identificación;
  - las 6 falsas alarmas de v4 por datos;
  - los manuales;
  - 6 controles de ventas y préstamos escritos a ciegas con fuentes externas.

Colab de la etapa 1: tag `colab/143-ronda-2`, `colab/COLAB-PUNTAJE-TOKEN-2.ipynb` (29 min de corridas en T4). En la
carpeta de la corrida están las corridas, el análisis, las fuentes, las ideas pendientes (incluido el estafador que te
hace llamar a vos) y la nota sobre Gemma 4 y la caché.
