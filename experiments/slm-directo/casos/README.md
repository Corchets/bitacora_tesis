# Casos de prueba del ensayo #50

Conversaciones **escritas y ficticias** para probar el detector sobre texto antes de
tener audio. Los 53 antecedentes son material de **desarrollo**. Corpus v2 agrega
97 conversaciones de desarrollo y 200 candidatas reservadas: ver
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
| `grupo` | `piloto_escrito`, `trampa`, `laboratorio` o `corpus_v2`. |
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
| `familia` | Familia del catálogo o contexto cotidiano (`trabajo`, `delivery`, `medico`, `escuela`). |
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
