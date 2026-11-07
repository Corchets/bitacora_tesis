## Segunda vuelta: lectura del token y prompt C

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre.

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
  - `motivo` y `evidencia` se piden en una segunda consulta, solo al avisar. Falta medir las dos consultas en Colab y
    después en el teléfono (#141).
  - La lectura del token queda para después de un ajuste fino: en Open-Jev (arXiv 2609.23959), leer el token dio un
    AUROC de 0,69 sin ajustar y ~0,97 con LoRA.
- **Solo para mirar:**
  - Dentro del alcance, v4-L llega a 46/46 con 1/7 FA. Pero el umbral (0,11) sale de 7 legítimas fáciles: sobre las 51
    de corpus_v2 avisaría en 36.
  - En los controles, v4 JSON y v4-L también avisan en las 3 legítimas de ventas y préstamos.

Detalle en `experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analisis.md`.

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

**Etapa 2 (con las legítimas nuevas):**
- **Configuraciones:** el prompt C con el alcance (`c-json`, `c-sino`, `c-digito`: mira la intención y permite avisar
  antes del pedido) y `v4-premisa`, que es v4 con la oración del alcance. v4 y v4-L se corren también sobre las
  legítimas nuevas.
- **Vista principal:** las 46 estafas de corpus_v2 y las legítimas nuevas de desarrollo, con FA ≤ 15 % de esas
  legítimas.
- **Línea base:** el mejor JSON entre v4, `v4-premisa` y `c-json`.
- El código de esa vista se escribe antes de correrla.

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
