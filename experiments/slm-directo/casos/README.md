# Casos de prueba del ensayo #50

Conversaciones **escritas y ficticias** para probar el detector sobre texto antes de
tener audio. Son material de **desarrollo**: sirven para ajustar el prompt y el
código. No son el corpus, no reemplazan las grabaciones del piloto
([#39](https://github.com/Corchets/bitacora_tesis/issues/39) /
[#54](https://github.com/Corchets/bitacora_tesis/issues/54)) y no se usan como test
final ([#55](https://github.com/Corchets/bitacora_tesis/issues/55)).

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
- **Una línea = un turno cerrado = una actualización del detector.** Si la misma
  persona dice dos cosas seguidas que conviene evaluar por separado, van en dos
  líneas con la misma letra.
- Español rioplatense hablado, con voseo. Se escribe con acentos y puntuación, como
  una transcripción revisada.
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
| `grupo` | `piloto_escrito`, `trampa` o `laboratorio`. |
| `semilla` | `scenario_id` del [catálogo](../../../docs/corpus/CATALOGO-ESCENARIOS.csv) o `null`. |
| `par` | `case_id` del caso contrastante, o `null`. |
| `clase` | `vishing` o `legitima_dificil`. |
| `t_r_linea` | Línea (desde 1) del **primer pedido de alto riesgo**, según el [manual](../../../docs/corpus/MANUAL-ANOTACION.md#2-cómo-ubicar-las-marcas-y-resolver-dudas). Mencionar un código no es pedirlo. `null` si no hay pedido. En una legítima es siempre `null`. |
| `t_c_linea` | Línea del **primer cumplimiento observable** del pedido. `null` si no hay cumplimiento, por ejemplo si la persona se niega. |
| `pedido` | Etiqueta `REQUEST_*` del primer pedido, o `null` si `t_r_linea` es `null`. |
| `evidencia` | Líneas que justifican la clase y las marcas. `evento`: `contexto`, `pedido`, `cumplimiento`, `rechazo` o `mencion`. `etiquetas` usa el vocabulario candidato del manual y puede quedar vacío. Si hay `t_r_linea`, debe figurar un `pedido` en esa línea; si hay `t_c_linea`, un `cumplimiento` en esa línea. |
| `que_prueba` | Qué dificultad concreta representa el caso para el detector. |
| `origen` | De dónde sale el texto y en qué fecha. |
| `revision_humana` | `false` hasta que una persona del equipo lo revise. |
| `notas` | Ambigüedades o diferencias con la ficha. |

Las posiciones son **líneas**, no segundos. En texto sin audio no se inventan tiempos
([arquitectura §3](../../../docs/ingenieria/ARQUITECTURA.md#3-referencia-tiempos-y-registros)).

## Grupos y nombres

| Grupo | Nombre del archivo | Qué es |
|---|---|---|
| `piloto_escrito` | `<semilla>-e01` (`-e02` si la semilla tiene una segunda versión) | Versión escrita de cada par de la [selección del piloto](../../../docs/corpus/METODO-CREACION-CORPUS.md#selección-inicial-del-piloto). |
| `trampa` | `TR-NN-<descripcion-corta>` | Casos difíciles pedidos por #50: pedidos indirectos, menciones legítimas parecidas, negaciones, evidencia separada por texto intermedio y conversaciones largas. |
| `laboratorio` | `LAB-<nombre-original>` | Guiones del laboratorio de Ignacio (`laboratorio-main`, `experiments/laboratorio/casos/`), convertidos a este formato. |

## Validar

```bash
python casos.py
```

Revisa los dos archivos de cada caso y termina con error si alguno no cumple este
formato. Con `--listar` muestra la tabla de casos.
