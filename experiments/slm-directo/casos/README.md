# Casos de prueba del ensayo #50

Conversaciones **escritas y ficticias** para probar el detector sobre texto antes de
tener audio. Los 53 antecedentes son material de **desarrollo**. Corpus v2 agrega
97 conversaciones de desarrollo y 200 candidatas reservadas, y
[`legitimas_cotidianas`](#legítimas-cotidianas) suma 91 legítimas de desarrollo: ver
[diseño y límites](DISENO-CORPUS-V2.md), [selección para grabar](GRABACIONES-ASR.md)
y [revisión técnica](REVISION-CORPUS-V2.md). No reemplazan las grabaciones del piloto
([#39](https://github.com/Corchets/bitacora_tesis/issues/39) /
[#54](https://github.com/Corchets/bitacora_tesis/issues/54)) y no se usan como test
final aprobado ([#55](https://github.com/Corchets/bitacora_tesis/issues/55)).

> **Estado: propuesta sin discutir.** Redacción asistida. Ningún caso tiene revisión
> humana hasta que el campo `revision_humana` diga `true`. No cierra D07.

## Dos archivos por caso

Cada caso tiene el mismo nombre en dos carpetas separadas:

| Archivo | Qué contiene | ¿Llega al detector? |
|---|---|---|
| `texto/<id>.txt` | Solo el diálogo, una línea por turno. | **Sí**: es lo único que lee. |
| `referencia/<id>.json` | Clase, marcas, evidencia y notas. | **No**, nunca. Solo lo usa `resumen.py` para comparar. |

Los separamos para que sea imposible pasarle la respuesta al modelo por error.

## Formato de `texto/<id>.txt`

```text
A: Te llamo de soporte por la activación de tu cuenta de WhatsApp.
B: Me acaba de llegar un SMS. No pedí activar nada.
```

- Cada línea empieza con `A: ` o `B: ` y lleva el texto del turno. No hay comentarios,
  títulos, líneas vacías ni texto de narrador.
- **A es quien habla primero.** A y B no indican quién llamó, quién es sospechoso ni
  quién es la víctima. El detector puede recibir esas letras o no, según la variante
  de la corrida (`--hablantes`). No confundir con el «rol A» y el «rol B» de las
  [fichas](../../../docs/corpus/METODO-CREACION-CORPUS.md#5-fichas-de-rol): en la
  legítima de WhatsApp, por ejemplo, habla primero quien recibió el código.
- El visor **Casos** del tablero muestra los nombres completos de los roles. En
  vishing sugiere como atacante a quien formula el pedido marcado en `T_R`; sin
  ese dato, pide elegir la persona protegida por su primera frase. En legítimas
  usa «Persona protegida» / «Otra persona» desde el inicio, con la perspectiva
  de lectura puesta en quien habla primero si no hay una elección guardada.
  Esa perspectiva no identifica un rol anotado en el corpus. Se puede cambiar y se
  conserva solo en el navegador; no cambia el guion, la referencia ni la entrada
  del detector. Es una ayuda de lectura, no una anotación humana aprobada en D07.
  > **Estado: propuesta sin discutir.** La sugerencia de roles a partir del pedido
  > es provisional; no resuelve [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico).
- **Una línea = un turno cerrado = una actualización del detector.** Si la misma
  persona dice dos cosas seguidas que conviene evaluar por separado, van en dos
  líneas con la misma letra.
- Español rioplatense hablado, con voseo. Se escribe con acentos y puntuación, como
  una transcripción revisada, salvo los casos `variante_asr:true`, que simulan cortes,
  omisiones de puntuación y errores. Esa simulación no es una medición de ASR.
- Los nuevos `corpus_v2` tienen entre 12 y 40 líneas. Los antecedentes conservan sus
  textos y limitaciones para reproducir las corridas históricas.
- **Solo datos ficticios:** códigos tipo `000000`, nombres inventados, sin DNI,
  CBU, teléfonos ni enlaces reales.

## Formato de `referencia/<id>.json`

```json
{
  "case_id": "SC-WA-CODE-01-e01",
  "grupo": "piloto_escrito",
  "semilla": "SC-WA-CODE-01",
  "par": "LG-WA-CONSULTA-01-e01",
  "clase": "vishing",
  "t_r_linea": 4,
  "t_c_linea": 5,
  "pedido": "REQUEST_AUTH_CODE",
  "evidencia": [
    {"linea": 1, "evento": "contexto", "etiquetas": ["AUTHORITY_CLAIM"]},
    {"linea": 4, "evento": "pedido", "etiquetas": ["REQUEST_AUTH_CODE"]},
    {"linea": 5, "evento": "cumplimiento", "etiquetas": []}
  ],
  "que_prueba": "Pedido directo de código con contexto previo de soporte y urgencia.",
  "origen": "ARQUITECTURA.md §4, adaptación asistida del 2026-10-07.",
  "revision_humana": false,
  "notas": ""
}
```

| Campo | Regla |
|---|---|
| `case_id` | Igual al nombre del archivo sin extensión. |
| `grupo` | `piloto_escrito`, `trampa`, `laboratorio`, `corpus_v2` o `legitimas_cotidianas`. |
| `semilla` | `scenario_id` del [catálogo](../../../docs/corpus/CATALOGO-ESCENARIOS.csv) o `null`. |
| `par` | `case_id` del caso contrastante, o `null`. |
| `clase` | `vishing`, `legitima` (nuevas) o `legitima_dificil` (antecedentes). Ambas legítimas se cuentan como legítimas al evaluar. |
| `t_r_linea` | Línea (desde 1) del **primer pedido de alto riesgo**, según el [manual](../../../docs/corpus/MANUAL-ANOTACION.md#2-cómo-ubicar-las-marcas-y-resolver-dudas). Mencionar un código no es pedirlo. `null` si no hay pedido. En una legítima es siempre `null`. |
| `t_c_linea` | Línea del **primer cumplimiento observable** del pedido. `null` si no hay cumplimiento, por ejemplo si la persona se niega. |
| `pedido` | Etiqueta `REQUEST_*` del primer pedido, o `null` si `t_r_linea` es `null`. |
| `evidencia` | Líneas que justifican la clase y las marcas. `evento`: `contexto`, `pedido`, `cumplimiento`, `rechazo` o `mencion`. `etiquetas` usa el vocabulario candidato del manual y puede quedar vacío. Si hay `t_r_linea`, debe figurar un `pedido` en esa línea; si hay `t_c_linea`, un `cumplimiento` en esa línea. |
| `que_prueba` | Qué dificultad concreta representa el caso para el detector. |
| `origen` | De dónde sale el texto y en qué fecha. |
| `revision_humana` | `false` hasta que una persona del equipo lo revise. |
| `notas` | Ambigüedades o diferencias con la ficha. |

> **Estado: propuesta sin discutir.** Los campos siguientes son obligatorios en
> `corpus_v2` y se precisan en el [diseño](DISENO-CORPUS-V2.md), pendientes de
> [D07/D08](../../../docs/gestion/MAPA-DECISIONES.md). No llegan al detector.

| Campo nuevo | Regla |
|---|---|
| `particion` | `desarrollo` o `test_reservado`. En los antecedentes ausente equivale a desarrollo. Semillas y pares no cruzan particiones. |
| `familia` | Familia del catálogo o contexto cotidiano (`trabajo`, `delivery`, `medico`, `escuela`, `comercial`, `encuesta`). |
| `situacion` | Descripción concreta de la semilla propuesta; debe distinguir el episodio, no solo un nombre o un monto. |
| `escenario_base` | Antecedente activo del catálogo que respalda la modalidad; `null` en diseños cotidianos sin antecedente. No vuelve independientes sus derivados. |
| `dificultad` | En vishing: `directo`, `indirecto`, `sin_pedido`. En legítimas coincide con `tipo_legitima`. Es una categoría de diseño, no dificultad medida. |
| `tipo_legitima` | `cotidiana`, `pedido_razonable` o `mencion_sin_pedido`; `null` en vishing. |
| `variante_asr` | Booleano. Texto con alteraciones artificiales de transcripción, sin audio medido. |

Una legítima puede tener evidencia de pedido o cumplimiento razonable sin marcas
críticas de fraude. En una llamada abortada sin pedido estas marcas quedan nulas;
la evidencia disponible y los límites de inferir intención se explicitan en notas.

Las posiciones son **líneas**, no segundos. En texto sin audio no se inventan tiempos
([arquitectura §3](../../../docs/ingenieria/ARQUITECTURA.md#3-referencia-tiempos-y-registros)).

## Grupos y nombres

| Grupo | Nombre del archivo | Qué es |
|---|---|---|
| `piloto_escrito` | `<semilla>-e01` (`-e02` si la semilla tiene una segunda versión) | Versión escrita de cada par de la [selección del piloto](../../../docs/corpus/METODO-CREACION-CORPUS.md#selección-inicial-del-piloto). |
| `trampa` | `TR-NN-<descripcion-corta>` | Casos difíciles pedidos por #50: pedidos indirectos, menciones legítimas parecidas, negaciones, evidencia separada por texto intermedio y conversaciones largas. |
| `laboratorio` | `LAB-<nombre-original>` | Guiones del laboratorio de Ignacio (`laboratorio-main`, `experiments/laboratorio/casos/`), convertidos a este formato. |
| `corpus_v2` | `CV2-D-<V/L>-<FAMILIA>-NNN` o `CV2-T-<V/L>-<FAMILIA>-NNN` | Nuevas situaciones; el campo `particion`, y no el prefijo, gobierna la selección. |
| `legitimas_cotidianas` | `LEG-<CATEGORÍA>-NN` y `LEG2-<CATEGORÍA>-NN` (id del archivo original), o `ENT-L-<FAMILIA>-NNN` | Llamadas legítimas cotidianas que comparten rasgos con el vishing. Ver abajo. |

### Legítimas cotidianas

> **Estado: propuesta sin discutir.** Familia, `tipo_legitima` y evidencia se asignaron
> al convertir los casos; la composición del corpus sigue abierta en
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

91 llamadas legítimas escritas y ficticias, incorporadas el 2026-11-06 en tres tandas. Los
archivos originales no se guardan en el repositorio: su contenido quedó en `texto/` y
`referencia/`, y su `id` es el `case_id`.

- **Tanda 1, `LEG-*` (21):** desde `llamadas_legitimas.json`. Llama y habla primero `A`;
  quien atiende es `B`, la persona protegida en `roles-protegida.json`.
- **Tanda 2, `LEG2-*` (28):** el split `dev` de «Llamadas legítimas v2: negativas difíciles»
  (`legitimas_dev.jsonl`). Son llamadas entrantes: atiende y habla primero `A`, la persona
  protegida, y el llamante `B` se presenta en sus dos primeros turnos. Todas piden o confirman
  datos (nombre, DNI, mail, dirección, obra social) y 9 nombran un código sin pedirlo. 15 son
  reescrituras de casos de la tanda 1, como dice `notas` en cada una.
- **Tanda 3, `ENT-L-<FAMILIA>-NNN` (42):** el lote «Legítimas entrantes difíciles» del
  2026-11-06, que ya venía en este formato. Todas son entrantes: el que llama se presenta;
  según el caso habla primero A o B, y `roles-protegida.json` dice quién es la protegida.
  Tienen de 14 a 36 líneas, como las estafas de `corpus_v2`, y 14 son `variante_asr`. Por tipo:
  21 `pedido_razonable`, 12 `mencion_sin_pedido` y 9 `cotidiana`. El lote proponía entrar a
  `corpus_v2` con semillas `LG-ENT-*` y separar un test; por decisión de Evaristo van todas a
  desarrollo y a este grupo, sin semilla (la propuesta queda en `notas`). Su familia `ventas`
  pasó a `comercial`, y se agregó `tramite` (revisión técnica, licencia de conducir).
  Casos difíciles: `ENT-L-SOPORTE-005` pide acceso remoto legítimo y recibe el número de
  conexión; `ENT-L-VENTAS-009` propone una seña por transferencia a la cuenta de la empresa;
  en `ENT-L-BANCO-006`, `ENT-L-VENTAS-005` y `ENT-L-DELIVERY-005` la persona empieza a dictar
  el código y el que llama la frena; en `ENT-L-BANCO-002` y `ENT-L-VENTAS-008` se niega a dar
  el DNI.

> **Sesgo a vigilar ([R29](../../../docs/gestion/REGISTRO-RIESGOS.md)).** La sigla DNI aparece
> en 34 de las 91 legítimas (37 %) y en 3 de las 46 estafas de desarrollo de `corpus_v2` (7 %).
> Por lote: 2 de 21 en `LEG`, 15 de 28 en `LEG2` y 17 de 42 en `ENT-L`. Un detector podría
> aprender que pedir el DNI indica una llamada legítima. Evaristo propone sumar estafas que
> pidan el DNI o la fecha de nacimiento ([#154](https://github.com/Corchets/bitacora_tesis/issues/154)).
>
> **Método del conteo (2026-11-06):** una llamada cuenta si la sigla aparece al menos una vez
> como palabra, en cualquiera de los dos hablantes y sin distinguir mayúsculas, porque las
> variantes de ASR la escriben «dni». Contando solo «DNI» en mayúsculas dan 25 de 91: quedan
> afuera 9 variantes de ASR de `ENT-L`. Con el mismo método, «usted» aparece en 3 de las 42
> `ENT-L` (7 %), en ninguna `LEG` ni `LEG2`, y en 1 de las 46 estafas (2 %). Se reproduce desde
> `texto/`, por ejemplo `grep -liw dni ENT-L-*.txt | wc -l`.

| Categoría del original | Casos | `familia` | `tipo_legitima` |
|---|---|---|---|
| Call center con oferta | `LEG-CC-01` a `03` | `comercial` | `cotidiana` |
| Vendedor de vehículos | `LEG-VE-01`, `02` / `LEG-VE-03` | `comercial` | `cotidiana` / `mencion_sin_pedido` |
| Banco, movimientos sospechosos | `LEG-BA-01` a `03` | `banco` | `mencion_sin_pedido` |
| Soporte técnico pedido por el cliente | `LEG-ST-01` / `LEG-ST-02` / `LEG-ST-03` | `soporte` | `cotidiana` / `pedido_razonable` / `mencion_sin_pedido` |
| Correo y entregas | `LEG-CO-01` a `03` | `delivery` | `cotidiana` |
| Encuestas | `LEG-EN-01`, `03` / `LEG-EN-02` | `encuesta` | `cotidiana` / `pedido_razonable` |
| Confirmación de turnos | `LEG-TU-01` a `03` | `medico` | `cotidiana` |

En la tanda 2, la familia sigue la misma tabla y el tipo sale del contenido: si nombra un
código, `mencion_sin_pedido` (9); si pide DNI, mail, dirección u otro dato, `pedido_razonable`
(14); si solo confirma el nombre, `cotidiana` (5).

#### Test de la tanda 2: fuera del repositorio

El original trae además 14 llamadas de test (2 por categoría, sorteadas con semilla
`20261106`) para congelar antes de correr detectores. **No están en esta rama**, por la misma
razón que la [reserva](RESERVA-FUERA-DEL-REPO.md): el repositorio es público y las particiones
siguen abiertas en [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).
Tampoco se guardaron `fuente_llamadas.txt` ni `build.py`, que incluyen el test. Huellas
SHA-256 para comprobar después que no cambió:

| Archivo | SHA-256 |
|---|---|
| `legitimas_test.jsonl` | `6ff4a0e46fc4ac412c6f27b69744d34560c62836650703e4d3add17301488cd9` |
| `legitimas_test.csv` | `93838036c600b5f7ed6eaa0a292e31e10404523fb2d3669bf9b13e8ec9d9feeb` |

Diferencias con `corpus_v2`:

- **Sin semilla ni par** (`null`): no hay una contraparte de vishing escrita para cada una.
  Las de banco, `LEG-ST-01` y `LEG2-ST-05` se vinculan con `escenario_base` al escenario
  legítimo del catálogo (`LG-BANK-ALERT-01`, `LG-SUPPORT-INFO-01`); el resto queda en `null`.
- **De 5 a 36 líneas**: el mínimo de 12 de `corpus_v2` no se exige.
- **Fuera de `MANIFIESTO-CORPUS-V2.json`**: el manifiesto protege los 350 casos de corpus v2 y
  sus antecedentes, y `casos.py` no compara las huellas de este grupo. Así la reserva y el
  catálogo no cambian.
- Solo partición `desarrollo` y clase `legitima`; `casos.py` falla si no.

Para correr solo este grupo: `python correr.py --grupo legitimas_cotidianas ...`. La etapa 2
de [#143](https://github.com/Corchets/bitacora_tesis/issues/143) informa los resultados por
lote, y cada lote tiene su lista en [`listas/`](listas/):

| Lista | Casos |
|---|---|
| `legitimas-91` | Las 91 de Evaristo: los tres lotes juntos |
| `legitimas-leg-21` | `LEG-*` |
| `legitimas-leg2-28` | `LEG2-*` |
| `legitimas-ent-l-42` | `ENT-L-*` del lote 3 |

`--lista` acepta varias separadas por coma, por ejemplo
`python correr.py --lista legitimas-leg-21,legitimas-leg2-28 ...`.
Las corridas anteriores al 2026-11-06 son sobre 150 casos; `correr.py` usa ahora por
defecto los 241 de desarrollo. Para repetir una corrida histórica:
`python correr.py --lista desarrollo-150 ...` ([lista](listas/desarrollo-150.txt)).

## Validar

```bash
python casos.py
python casos.py --listar
```

Revisa los dos archivos de cada caso y termina con error si alguno no cumple este
formato. Con `--listar` muestra la tabla de casos.

También verifica las huellas de `MANIFIESTO-CORPUS-V2.json` cuando existe. La reserva
se crea con `python3 casos.py --congelar`; ese comando rechaza sobrescribirla. Cualquier
modificación posterior se detecta. La corrección técnica `r02` de los candidatos,
solicitada por Luciano, registra las nuevas huellas y la recuperación del manifiesto
anterior en Git; ver [revisión y límites](REVISION-CORPUS-V2.md). No congela D08 ni
sustituye la revisión humana.

`correr.py` usa desarrollo por defecto. `--casos` no permite mezclar casos de otra
partición. `--particion test_reservado` es una selección explícita para la evaluación
final una vez acordado D08, no un recurso para afinar. El panel excluye de sus datos
los textos y las referencias reservadas.

## Copia pública (`laboratorio-main`)

El repositorio es público. `laboratorio-main` lleva los 150 de desarrollo, pero no los 200
reservados (`CV2-T-*`) ni sus filas del catálogo (`*-CV2-T-*`), que resumen cada escenario.
Ahí existe `RESERVA-FUERA-DEL-REPO.md`, y con esa marca `casos.py`:

- falla si encuentra un caso reservado o una semilla reservada en el catálogo;
- verifica las huellas de desarrollo y `catalogo_desarrollo_sha256` (el catálogo sin la
  reserva), en lugar de las de la reserva completa.

Sin la marca, que falte la reserva es un error. Las huellas SHA-256 de los 200 siguen en el
manifiesto: sirven para probar después que la reserva no cambió.

La reserva completa vive en `laboratorio-luciano`. **Esa rama está en GitHub desde el
2026-10-23**, por decisión de Luciano, así que la reserva es pública. La regla pasa a ser no
correrla ni mirarla, ni con personas ni con modelos, hasta la evaluación final (sigue
`--particion test_reservado`, después de acordar D08). Solo vale como test para modelos
publicados antes del 2026-10-23, que no pudieron entrenarse con ella (Qwen3.5, por ejemplo);
con uno posterior hay que declarar la posible contaminación
([R05](../../../docs/gestion/REGISTRO-RIESGOS.md)).

**No mergear `laboratorio-luciano` en `laboratorio-main`**: traería la reserva en la historia
de la rama de integración, donde se corre sin pensar. Para integrar se arma un único commit con
`git merge --squash`, se sacan los `CV2-T-*`, se filtra el catálogo con
`casos.catalogo_sin_reserva` y se agrega la marca.
