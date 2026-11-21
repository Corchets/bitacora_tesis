# Test para el alcance (#45)

Fecha: 2026-11-07. Lo pidió Mateo Antenucci en [#45](https://github.com/Corchets/bitacora_tesis/issues/45) el
2026-11-06 y lo preparó un agente. Lo revisa Luciano Grosso en el PR hacia `laboratorio-luciano`.

> **Estado: propuesta sin discutir.** Cómo se rehace la reserva lo decide el equipo antes del 2026-11-11 (#45). Nada de
> esto congela la reserva ni cambia sus huellas. Sigue el ADR 0004, puntos 3 y 4, que también es una propuesta.

## Qué es

El detector corre solo en llamadas entrantes de números no agendados (ADR 0003, #151). La reserva (`CV2-T-*`) salió
del mismo generador que corpus_v2, donde quién llama predice la clase, y casi no tiene legítimas dentro de ese alcance.
El test se rehace así:

| Parte | Casos | Para qué |
|---|---|---|
| Estafas de la reserva | 100 `CV2-T-V-*` | Vista principal: detección dentro del alcance |
| Legítimas entrantes nuevas | 56 `ENT-T-*`, más las 14 `LEG2` de test de Evaristo si cumplen | Vista principal: falsas alarmas dentro del alcance |
| Legítimas viejas de la reserva | 100 `CV2-T-L-*` | Aparte: qué pasaría si fallara el filtro de alcance |

**Todo esto vive en `laboratorio-luciano`, junto a la reserva, y nunca entra en `laboratorio-main`.** Lo decidió Mateo
el 2026-11-07. El lote nuevo es público desde el día en que se sube, así que vale el mismo criterio de R05, con esa fecha.

| Archivo | Qué tiene |
|---|---|
| [`alcance-reserva.json`](alcance-reserva.json) | Quién inicia cada llamada de la reserva, anotado a ciegas |
| [`legitimas-entrantes-test.jsonl`](legitimas-entrantes-test.jsonl) | El lote nuevo: 56 legítimas entrantes |
| [`INSTRUCCIONES-GENERADOR-TEST.md`](INSTRUCCIONES-GENERADOR-TEST.md) | Lo único que vieron los generadores del lote |
| [`../test_alcance.py`](../test_alcance.py) | Entrada ciega, unión de las anotaciones y controles del lote |

Nadie corrió detectores ni modelos sobre la reserva ni sobre el lote nuevo. La sesión que preparó todo procesó la
reserva con scripts y no leyó sus transcripciones.

## 1. Quién inicia cada llamada de la reserva

La regla es la de [`alcance-desarrollo.json`](https://github.com/Corchets/bitacora_tesis/blob/exp/143-puntaje-token/experiments/slm-directo/casos/alcance-desarrollo.json),
copiada en el `_meta` de `alcance-reserva.json`. La reserva no tiene `roles-protegida.json`, así que el mismo agente
marcó primero quién es PROTEGIDA, con una regla escrita antes de anotar: si una parte habla en nombre de una empresa u
organismo, PROTEGIDA es la otra; si las dos son particulares, PROTEGIDA es a quien le piden o le proponen algo.

**Método.** Cuatro agentes leyeron solo las transcripciones, con A/B y las líneas numeradas, renombradas
`llamada-001…200` y mezcladas con semilla 45. No vieron `case_id`, clase, referencia, prompts ni resultados. Cada uno
anotó 60: un lote de 50 y los 10 primeros del lote siguiente, así que 40 llamadas tienen dos anotaciones. La clave
quedó aparte.

**Acuerdo.** En la primera pasada, los roles coincidieron en las 40 llamadas con dos anotaciones, pero `inicia`
coincidió solo en 30. Tres anotadores dejaban como `no_se_sabe` las llamadas en las que nadie decía literalmente que
llama: 10, 27 y 33 de sus 60. El cuarto lo deducía de cómo empieza la conversación. Se escribió una precisión sin mirar
las llamadas ni la clase: quien abre presentándose o con el motivo de la llamada es quien llamó, y quien responde con
una fórmula de atender es quien atendió. Con esa precisión, cada agente volvió a anotar su lote, y las 40 llamadas con
dos anotaciones coincidieron en todo. La regla para desacuerdos («queda `no_se_sabe`») se escribió antes de unir las
anotaciones, pero no hizo falta.

| Reserva | Dentro | Fuera | Dudoso |
|---|---:|---:|---:|
| Estafas (100) | 100 | 0 | 0 |
| Legítimas viejas (100) | 26 | 74 | 0 |

- **Las 100 estafas son entrantes.** Ya lo eran en la primera pasada. La precisión solo resolvió legítimas que habían
  quedado como `no_se_sabe`: 61 de 100, contando la primera anotación de cada llamada.
- **La persona inicia 74 de las 100 legítimas viejas.** Es el mismo sesgo de desarrollo, donde inicia 44 de 51.
- **Las 26 legítimas que quedan dentro casi no sirven para medir falsas alarmas.** Por familia, según el `case_id`, 14
  son de `familiar`, 5 de `trabajo`, 3 de `whatsapp`, 2 de `escuela`, 1 de `banco` y 1 de `delivery`. La regla marca
  `agendado` solo con evidencia explícita, pero en un teléfono real los familiares y compañeros estarían agendados.
  Pasaba lo mismo en desarrollo.
- 9 legítimas tienen `rol_dudoso`: 4 son de `familiar`, 2 de `trabajo`, 2 de `whatsapp` y 1 de `banco`.
- Una legítima tiene `numero = agendado`, pero también la inicia la persona, así que queda fuera igual.

## 2. Lote nuevo de legítimas de test

**Cómo se generó.** Dos subagentes escribieron 28 llamadas cada uno el 2026-11-07, con familias separadas. Solo
vieron [INSTRUCCIONES-GENERADOR-TEST.md](INSTRUCCIONES-GENERADOR-TEST.md), escritas antes de generar. No leyeron
prompts, corridas, resultados ni casos del corpus, y no usaron git ni la web. Las instrucciones fijan las familias,
los tipos de legítima, el largo, la proporción de variantes de ASR, el comienzo y topes para el DNI, la fecha de
nacimiento y el «usted». Esas cifras salen de medir por script la forma de las estafas; no intervino ningún detector.
La sesión que preparó todo controló el lote con scripts y no lo leyó.

**Composición.** Son 56 llamadas entrantes de números desconocidos:
- **Por familia:** `seleccion_personal`, `banco`, `comercial` y `delivery`, 7 cada una; `medico`, `soporte` y
  `tramite`, 6 cada una; `compraventa` y `encuesta`, 5 cada una.
- **Por tipo:** 26 `pedido_razonable`, 16 `mencion_sin_pedido` y 14 `cotidiana`.

**Forma** (`python -I test_alcance.py controles`):

| Conjunto | n | Líneas | ASR | DNI | Fecha de nac. | «usted» | PROTEGIDA habla primero | Palabras de la 1.ª línea (mediana) |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| Estafas de desarrollo (corpus_v2) | 46 | 20–38 (mediana 21) | 12 | 3 | 4 | 3 | 23/46 | 10 |
| Estafas de la reserva | 100 | 17–31 (mediana 21) | 30 | 7 | 12 | 2 | 52/100 | 3 |
| Legítimas viejas de la reserva | 100 | 22–35 (mediana 28) | 30 | 0 | 3 | 1 | 72/100 | 13 |
| `LEG` | 21 | 5–16 (mediana 9) | 0 | 2 | 0 | 0 | 0/21 | 7 |
| `LEG2` | 28 | 7–14 (mediana 11) | 0 | 15 | 2 | 0 | 28/28 | 1 |
| `ENT-L`, con las 3 de selección | 45 | 14–36 (mediana 22) | 15 | 18 | 5 | 4 | 23/45 | 3 |
| Las 94 legítimas de desarrollo | 94 | 5–36 (mediana 13,5) | 15 | 35 | 7 | 4 | 51/94 | 3 |
| **Lote nuevo (`ENT-T`)** | 56 | 20–37 (mediana 25) | 17 | 3 | 6 | 2 | 28/56 | 12 |

- **El largo y el ruido se parecen a los de las estafas.** El lote tiene de 20 a 37 líneas, contra 17 a 31 de las
  estafas de la reserva, y el 30 % trae variantes de ASR, como ellas. La mediana del lote es más alta (25 contra 21).
  Si eso pesa en algún sentido, deja más líneas donde equivocarse y vuelve más exigente la medida de falsas alarmas.
- **El DNI ya no separa las clases.** Aparece en 3 de las 56 llamadas (5 %), contra el 7 % de las estafas de
  desarrollo y de la reserva. En las 94 legítimas de desarrollo aparece en 35 (37 %).
- **PROTEGIDA habla primero en la mitad de las llamadas**, como en las estafas.
- **Diferencia declarada:** la primera línea del lote tiene una mediana de 12 palabras, y la de las estafas de la
  reserva, de 3. Las instrucciones copiaron el comienzo de las estafas de desarrollo (mediana 10) y no el de la
  reserva, que se midió después.

**Parecido.** Se comparó cada llamada con las 94 legítimas de desarrollo del
[PR #155](https://github.com/Corchets/bitacora_tesis/pull/155): las 91 de Evaristo y 3 de selección de personal.
Se usaron dos medidas: el coseno TF-IDF de palabras y la parte de los bigramas de una llamada de desarrollo que
reaparece en la nueva, que detecta una reescritura alargada aunque el coseno baje. Los umbrales son los mínimos de las
15 `LEG2` que, según sus notas, reescriben una `LEG`: coseno 0,347 y cobertura 0,246.
- **Primera versión:** una llamada superó la cobertura. `ENT-T-MEDICO-001` cubría el 0,262 de `LEG-TU-01`, con un
  coseno de 0,163. Se reemplazó sin leerla, que es lo conservador y no obliga a juzgar si era una reescritura: el mismo
  generador escribió otra con la misma familia, el mismo tipo y el mismo comienzo, y con otra situación.
- **Versión final:** el coseno máximo contra las 94 es 0,220 y la cobertura máxima, 0,224. No queda ninguna llamada
  marcada. Dentro del lote, el coseno máximo es 0,171.

**Formato.** El lote todavía no está en el formato de casos (`texto/` y `referencia/`), porque `casos.py` no tiene un
grupo para legítimas de test. Cada línea del JSONL trae `case_id`, familia, tipo, variante de ASR, quién es PROTEGIDA,
situación, qué la hace difícil, las líneas con pedido y con mención, y el texto. `lineas_pedido` y `lineas_mencion`
son auxiliares y no son del todo parejas: el generador 1 contó como mención también lo que nombra PROTEGIDA. El lote
pasa al formato de casos al congelar (sección 6). SHA-256 del JSONL al 2026-11-07:
`94dc3a7f084c0aa9a9b2f17c586fbac3b5a1ed813d87697b5096f93eefc8bf34`.

## 3. Las 14 `LEG2` de test de Evaristo

Están fuera del repositorio. Las tiene Evaristo, y sus SHA-256 están en el `casos/README.md` de la rama
`claude/determined-wright-tsxh08`. Se las pide Mateo (el texto del pedido es del 2026-11-07). Cuando lleguen:

1. Se comprueban las huellas contra ese README.
2. Pasan los mismos controles que el lote nuevo (`test_alcance.py controles`). Para contar en la vista principal
   tienen que ser entrantes de números desconocidos, tener de 20 a 38 líneas y no reescribir ninguna de las 94
   legítimas de desarrollo. Si no cumplen, se informan aparte. Las `LEG2` de desarrollo tienen de 7 a 14 líneas, así
   que lo más probable es que se informen aparte.
3. **El parecido se mide también contra las `ENT-L`.** Según los mismos controles, 31 de las 42 `ENT-L` de desarrollo
   se parecen a una `LEG` o `LEG2` tanto como las reescrituras declaradas, y 23 llevan su mismo número (por ejemplo,
   `ENT-L-ENCUESTA-004` y `LEG2-EN-04`). Ninguna lo declara en `notas`. Si alguna `ENT-L` reescribe una de las 14 de
   test, esa llamada de test ya está en desarrollo y no puede contar.

## 4. Corrección con un agente

Plan de Mateo del 2026-11-06, que reemplaza la revisión humana completa: las personas no leen el test entero. Lo
corrige un agente distinto del detector, con la guía de [#145](https://github.com/Corchets/bitacora_tesis/issues/145),
y el equipo lee una muestra para ver que no haya nada raro.

**Cuándo.** Después de que exista la guía de #145, que se calibra el 2026-11-09, y antes del visto bueno del equipo.
Sin la guía no se corre, salvo que Mateo diga otra cosa.

**Qué casos.** Los 270 del test: 100 estafas y 100 legítimas viejas de la reserva, las 56 nuevas y las 14 `LEG2` si
llegan.

**Qué agente.** Uno que no sea ninguno de los modelos que se evalúan (hoy, Claude en una sesión nueva), que no haya
visto prompts, corridas ni resultados y que no haya escrito los casos.

**Qué recibe.** Por cada caso, armado por script como en la sección 1:
- la transcripción con las líneas numeradas y los roles PROTEGIDA y OTRA (salen de `alcance-reserva.json` y del lote);
- la guía de #145 y las definiciones de `T_R`, `T_C` y pedido de
  [METRICAS.md](../../../docs/evaluacion/METRICAS.md);
- nada más: ni `case_id`, ni clase, ni referencia, ni familia, ni de qué tanda sale. Los casos van renombrados y
  mezclados con semilla 46, en lotes con 40 casos de solape para medir el acuerdo.

**Pasada 1, a ciegas.** Por cada caso devuelve:
- `clase`: estafa, legítima o dudosa;
- `creible`: sí, dudosa o no, con el motivo;
- `t_r` y `t_c`: la línea, o `null` si no hay pedido o cumplimiento;
- `inicia`: con la regla de `alcance-reserva.json`, precisión incluida;
- `motivo`: las líneas y la razón, en hasta 40 palabras.

**Comparación.** Un script compara cada campo con la referencia actual: `clase`, `t_r_linea` y `t_c_linea` de
`referencia/`, e `inicia` de `alcance-reserva.json`. En el lote nuevo, la referencia es «legítima, sin `T_R` ni `T_C`».
Las líneas se comparan exactas, porque `T_R` decide qué aviso llega antes del pedido.

**Pasada 2, adjudicación.** Cada diferencia la resuelve otro agente, también a ciegas. Recibe la llamada, la guía y las
dos versiones en orden al azar, sin saber cuál es la original. Elige una o propone otra, y escribe el motivo con las
líneas. Si no puede decidir, el caso va a la muestra del equipo.

**Cómo se registra cada cambio**, como la corrección `r02` de
[DISENO-CORPUS-V2.md](DISENO-CORPUS-V2.md#semillas-parentesco-y-reserva):
- Los cambios los aplica un script, nunca el agente.
- En `MANIFIESTO-CORPUS-V2.json` entra una revisión técnica nueva, `r03`. Lleva la fecha, la autorización (el visto bueno del equipo en #45), el estado («propuesta sin
  discutir; corrección con agente, no adjudicación humana»), el manifiesto anterior (commit y SHA-256) y, en
  `casos_modificados`, una línea por campo cambiado: valor anterior, valor nuevo, motivo con las líneas y qué pasada lo
  decidió.
- La referencia de cada caso cambiado lo dice en `notas`. `revision_humana` sigue en `false`, porque ninguna revisión
  de un agente la cambia (DISENO-CORPUS-V2.md).
- Las salidas crudas de las dos pasadas se guardan junto a la reserva.
- Ningún caso se borra. Si la guía de #145 dice qué hacer con una llamada poco creíble, se aplica igual a todo el test;
  si no lo dice, el caso queda y la duda se informa.

**Lo que no se hace:** correr detectores, mirar resultados, ni escribir un criterio para un caso suelto. Si hace falta
un criterio nuevo, se escribe antes y se aplica a todo el test.

## 5. Muestra que lee el equipo

> **Estado: propuesta sin discutir.**

Unos 60 casos, 20 por persona, con semilla fija:
- **Todos los casos que el agente cambió, hasta 30.** Si son más, 30 al azar, repartidos entre las tres partes del test.
- **Todos los que la adjudicación dejó en duda.**
- **30 sin cambios, al azar:** 12 estafas, 12 legítimas nuevas (con las `LEG2`, si están) y 6 legítimas viejas. Si
  nadie encuentra un problema en esos 30, los errores que el agente dejó pasar son menos del 10 % con 95 % de confianza
  (regla del tres: 3/30). Con 60 sin cambios el límite baja al 5 %, pero la lectura se duplica.

**Quiénes.** Los mismos de #145: Luciano, Nacho y Evaristo. Evaristo no lee las `LEG2` que escribió. Cada uno responde
las cuatro preguntas de #145 (si es creíble, si es estafa, en qué línea sospecharía y si `T_R` y `T_C` están bien) y
si está bien quién inicia la llamada.

**Regla de corte.** Si alguien encuentra el mismo tipo de error en dos casos o más, el criterio se escribe en la guía,
el agente vuelve a pasar sobre todo el test y se saca otra muestra. Un error suelto se corrige con su motivo, igual
que los del agente.

**Cuidado.** Leer la muestra expone casos del test. Quien la lee no propone después cambios de prompt ni de reglas por
lo que leyó, y queda anotado quién leyó qué caso. Si la configuración del ADR 0002 se congela antes, conviene leer
después.

## 6. Congelar

Con el visto bueno del equipo:
1. El lote nuevo, y las `LEG2` que cuenten, pasan al formato de casos (`texto/` y `referencia/`), con
   `particion: test_reservado` y un grupo propio. `casos.py` todavía no conoce ese grupo.
2. Se actualizan el manifiesto y los SHA-256, con la fecha y la revisión técnica de la sección 4.
3. Se registra que ningún detector corrió sobre el test antes del congelamiento.

## Pendiente

**Descartado:** `reserva-sin-cortes`, la corrección que completaba las estafas de la reserva cortadas antes del
pedido. La descartaron Luciano y Mateo el 2026-11-07: esas llamadas se escribieron cortadas a propósito, y completarlas
ajustaría el test al detector que busca pedidos. Quedan como están y se informan aparte. La rama nunca se subió.

| Qué | Quién | Fecha |
|---|---|---|
| Decidir si la reserva se rehace con este plan | equipo, #45 | antes del 2026-11-11 |
| Las 14 `LEG2` de test, y si apartó otras | Evaristo (se lo pide Mateo, 2026-11-07) | antes de congelar |
| Guía de revisión | #145 | 2026-11-09 |
| Corrección con el agente y lectura de la muestra | este procedimiento | después de la guía |
| Congelar: manifiesto y SHA-256 con fecha | equipo, #45 | después de la corrección y del visto bueno |
