# ADR 0004 — Sumamos legítimas entrantes de números desconocidos y las medimos con un test aparte

- **Fecha:** 2026-11-06
- **Estado:** propuesta sin discutir
- **Participantes de la discusión:** el equipo, con Mateo Antenucci, durante la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Evaristo Villalobo genera las legítimas nuevas. Se
  registra en [#151](https://github.com/Corchets/bitacora_tesis/issues/151). Lo redactó un agente a pedido de Mateo y
  falta la revisión del equipo.
- **Ámbito:** corpus

> **Estado: propuesta sin discutir.** Los puntos 1 y 2 de la decisión los tomó el equipo el 2026-11-06. Los puntos 3
> a 5 siguen a [#45](https://github.com/Corchets/bitacora_tesis/issues/45), que rehace la reserva para el alcance; cómo
> se rehace lo decide el equipo antes del 2026-11-11.
> Sirve de insumo para [D06](../../gestion/MAPA-DECISIONES.md#d06--definir-corpus-y-piloto) y
> [D08](../../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental), pero no las cierra.

## Contexto

El [ADR 0003](0003-detector-solo-en-entrantes-de-no-agendados.md) limita el detector a las llamadas entrantes de
números no agendados. Para medirlo hacen falta legítimas de ese tipo: las negativas difíciles que el producto sí va a
escuchar.

El 2026-11-06 se anotó a ciegas quién inició cada uno de los 150 casos de desarrollo
([`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json)). Un agente leyó solo las
transcripciones con roles, renombradas y mezcladas. No vio la clase, la referencia, los prompts ni los resultados, y
aplicó una regla escrita antes de anotar.

| Desarrollo | Estafas | Legítimas |
|---|---|---|
| corpus_v2 (97 casos) | 46, todas entrantes | 44 las inicia la persona y 7 son entrantes |
| Antecedentes (53 casos) | 29, todas entrantes | 7 las inicia la persona, 8 son entrantes y en 9 no se sabe |

- **Quién llamó predice la clase.** Las 75 estafas son entrantes. En corpus_v2, 44 de las 51 legítimas son consultas
  que hace la persona, escritas como par de cada estafa. Las 7 entrantes son de familiares y compañeros de trabajo, que
  en un teléfono real estarían agendados. Las cuotas de corpus_v2 se repartieron por familia y dificultad, no por
  dirección de la llamada ([diseño de corpus_v2](../../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md#cantidades)).
  El sesgo salió del generador, no de una decisión de diseño.
- **Las cifras dentro del alcance no se pueden defender.** Como ejemplo se usa la regla «riesgo ≥ 0,3 o alerta»: avisa
  en la primera línea en que el `riesgo` del JSON llega a 0,3 o `alerta_sugerida` es `true`. Es el umbral más bajo de
  los que exploró #143 (0,3, 0,4 y 0,5), no la regla de la candidata, que avisa solo con `alerta_sugerida` (28/46 y
  6/51). Con esa regla, v4 JSON da en corpus_v2
  41/46 estafas, 23 antes del pedido, y 21/51 falsas alarmas. Veinte de esas 21 están en llamadas que inició la
  persona. Dentro del alcance queda 1 falsa alarma sobre 7 legítimas, y parece un buen resultado solo porque casi no hay
  legítimas.
- **La reserva sale del mismo generador:** 200 casos `CV2-T-*`, 100 de cada clase. Lo más probable es que tenga el
  mismo sesgo; no se verificó para no mirarla.
- **Estafas por datos.** 6 de las 46 estafas de corpus_v2 piden un dato de identificación (semillas de ANSES y del
  premio), y 4 de ellas piden solo eso. Fuera del corpus está documentado que piden fotos del DNI y una selfie, pero es
  menos frecuente que pedir un código
  ([`FUENTES.md`, §1](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/FUENTES.md#1-estafas-y-llamadas-legítimas-en-argentina)).
  Que pidan solo el número de documento es una señal débil.

## Decisión

1. **No se sacan casos.** El corpus queda como está y el alcance se aplica en el análisis, con la anotación a ciegas.
   Las legítimas que inicia la persona y las dudosas se informan aparte, fuera del alcance.
2. **Se generan legítimas entrantes de números desconocidos.** Las escribe Evaristo. Al 2026-11-06 subió 91 de
   desarrollo, en el grupo `legitimas_cotidianas` de la rama
   [`claude/determined-wright-tsxh08`](https://github.com/Corchets/bitacora_tesis/tree/claude/determined-wright-tsxh08),
   todavía sin integrar:
   - `LEG-*` (21) y `LEG2-*` (28): cortas, de 5 a 16 líneas. 15 de las `LEG2` reescriben una `LEG`.
   - `ENT-L-*` (42): de 14 a 36 líneas y con variantes de ASR, como las estafas.

   Cubren ventas y ofertas comerciales, el banco que avisa un movimiento, el correo y las entregas, turnos médicos,
   encuestas, soporte técnico y trámites. De la lista del 2026-11-06 solo falta selección de personal.
3. **El test es la reserva rehecha.** Se mantienen sus 100 estafas, que ningún detector corrió. Las legítimas del test
   principal son un lote nuevo de entrantes de números desconocidos, generado como el de desarrollo y sin mirar
   prompts ni resultados. Ya hay 14 fuera del repo, con sus SHA-256. Hacen falta 50 o más, de largo parecido al de las
   estafas, y ninguna puede ser reescritura de una de desarrollo.
4. **El test lo corrige un agente y se congela antes de correr nada.** Un agente distinto del detector corrige la
   clase, `T_R` y `T_C` con la guía de [#145](https://github.com/Corchets/bitacora_tesis/issues/145), y el equipo lee
   una muestra para ver que no haya nada raro. Después se actualizan el manifiesto y los SHA-256, con fecha, como en
   [#144](https://github.com/Corchets/bitacora_tesis/issues/144).
5. **Quién inicia cada llamada de la reserva se anota a ciegas,** con la regla de `alcance-desarrollo.json`, en una
   pasada que no ve la clase. Anotarlo no exige correr detectores.

Así, la evaluación final se informa en dos partes:
- **dentro del alcance,** con las estafas de la reserva y las legítimas entrantes de test;
- **fuera del alcance,** con las 100 legítimas viejas de la reserva, como chequeo de qué pasaría si fallara el filtro
  de alcance.

Las 6 estafas por datos también se informan aparte, sin sacarlas.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Medir dentro del alcance con lo que hay: 46 estafas y 7 legítimas | No hace falta generar nada | Son 7 legítimas, todas de contactos que estarían agendados, y una falsa alarma vale 14 puntos | Las cifras no se pueden defender |
| Seguir midiendo sobre los 150, sin alcance | Se compara directo con las corridas anteriores | Mide un producto que no es el que se defiende, y las consultas que inicia la persona dominan las falsas alarmas | Queda como vista aparte, no como principal |
| Legítimas nuevas solo para desarrollo, y la reserva tal cual como test | Hay que generar una sola tanda | Si la reserva tiene el mismo sesgo, en el test quedan muy pocas legítimas entrantes | Hace falta un test aparte |
| Llamadas reales o un corpus externo | No salen de nuestro generador | Las llamadas reales piden consentimiento y resguardo fuera de Git. Las fuentes externas de #144, como las estafas reales de KorCCVi traducidas, no traen legítimas difíciles, y #144 es un test: no se ajusta nada mirándolo | No reemplazan el corpus: #144 complementa la evaluación como prueba de generalización |

## Consecuencias

- **La etapa 2 de #143 ya tiene legítimas, pero en una rama sin integrar.** Su vista principal son las 46 estafas de
  corpus_v2 más las legítimas nuevas de desarrollo, con falsas alarmas de hasta el 15 % de esas legítimas. El código
  de esa vista se escribe antes de correrla
  ([`analizar.py`](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/analizar.py)). Los resultados
  se informan por lote (`LEG`, `LEG2` y `ENT-L`; lo decidió Mateo el 2026-11-06), porque las `LEG` y `LEG2` son cortas
  y en las `LEG2` el DNI aparece mucho más.
- **Las falsas alarmas del test final dependen casi enteras de las legítimas nuevas de test.**
- **Las corridas viejas sobre los 150 se conservan.** Sus cifras se leen como «sin alcance».
- **La reserva todavía no está congelada, y se rehace (#45).** La rama `reserva-sin-cortes`, con la corrección de las
  llamadas cortadas, sigue sin integrar ni descartar. Como la corrige un agente y el equipo lee solo una muestra, el
  test no tiene referencia humana completa (R28). Además, la reserva es pública desde el 2026-10-23 (R05).
- **Riesgo nuevo.** Las legítimas nuevas salen de otra tanda que las estafas. Que sean variadas es bueno. El problema
  es que una diferencia de forma coincida con la clase: si todas las legítimas nuevas son cortas y prolijas y las
  estafas son largas y con ruido, la clase se vuelve a poder adivinar sin entender la llamada, como pasó con la
  dirección. Antes de usarlas se comparan con las estafas en largo, ruido de transcripción y comienzo. Si una
  diferencia separa las clases, se completan casos del otro tipo. Más adelante, generar también estafas en la misma
  tanda evitaría que una clase quede atada a una tanda. #144 lo controla con datos de afuera.
- **La comparación ya marca dos diferencias** (2026-11-06):
  - **Largo:** las `LEG` y `LEG2` tienen de 5 a 16 líneas y ninguna variante de ASR; las estafas de corpus_v2 tienen
    de 20 a 38 líneas, y 12 traen variantes. El lote `ENT-L` lo compensa: de 14 a 36 líneas y 14 variantes.
  - **Contenido:** la sigla DNI aparece en 25 de las 91 legítimas nuevas (27 %; en las `LEG2`, 54 %) y en 3 de las 46
    estafas (7 %). Evaristo lo registró como riesgo en su rama; la mitigación que propone es sumar estafas que pidan
    el DNI.
- **El ajuste fino necesita otra fuente.** Si los datos de entrenamiento salen del mismo generador, el modelo aprende
  su estilo, y el sesgo de dirección es justo eso
  ([ideas pendientes, §3](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md#3-ajuste-fino-para-leer-el-token-trabajo-futuro)).
- **Limitación declarada:** el corpus es sintético y sale de un solo generador. El sesgo de dirección se encontró en
  desarrollo, y probablemente esté en la reserva. Toda cifra calculada sin el alcance tiene que aclararlo.

**Para reconsiderarla:** que el lote nuevo de test no llegue a 50 legítimas antes de congelar. Con 14, el 15 % son 2
casos: la vista dentro del alcance queda con un margen muy ancho, y el límite se declara.

## Referencias

- [`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json): regla, método y conteo.
  Las 21 falsas alarmas salen de cruzarla con la corrida
  [`2026-11-05_tito-2-v4/b`](../../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/) (v4 solo).
- [Diseño de corpus_v2](../../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md): cantidades, semillas y reserva.
- [Método del corpus, §9](../../corpus/METODO-CREACION-CORPUS.md#9-división-de-datos): división por semilla.
- [#45](https://github.com/Corchets/bitacora_tesis/issues/45) (rehacer y congelar la reserva),
  [#145](https://github.com/Corchets/bitacora_tesis/issues/145) (guía de revisión, que absorbe #32),
  [#144](https://github.com/Corchets/bitacora_tesis/issues/144) (corpus externo) y
  [#151](https://github.com/Corchets/bitacora_tesis/issues/151) (registro de esta decisión).
- `casos/README.md` de la rama `claude/determined-wright-tsxh08`: las tres tandas de legítimas y las huellas del test.
- [Ideas pendientes](../../../experiments/slm-directo/corridas/2026-11-06_puntaje-token-2/IDEAS-PENDIENTES.md), §0 y §3.
