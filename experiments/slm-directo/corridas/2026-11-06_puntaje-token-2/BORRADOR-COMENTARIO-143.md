## Segunda vuelta: lectura del token y prompt C (lista cerrada antes de correr)

> **Estado: propuesta sin discutir.** Desarrollo; la reserva no se corre.

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

**Etapa 1 (ya, sobre los 150):** v4-L contra v4 JSON, con la regla de la primera vuelta (FA ≤ 7/51). Es la prueba de la
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

Colab de la etapa 1: tag `colab/143-ronda-2`, `colab/COLAB-PUNTAJE-TOKEN-2.ipynb` (~35 min en T4). Fuentes, ideas
pendientes (incluido el estafador que te hace llamar a vos) y la nota sobre Gemma 4 y la caché, en la carpeta de la
corrida.
