# #52, exploración con los conjuntos reales: análisis

> **Estado: propuesta sin discutir.** Mateo la corrió en Colab T4 el 2026-11-20, una sola vez, con el tag
> `colab/52-exploracion-reales-2` (`7c52850`). Es posterior a la [evaluación final](../2026-11-12_evaluacion-final/analisis.md)
> y no la reemplaza. La regla está en el [README](README.md), escrita antes de correr. Las cifras salen de
> [`analizar.py`](analizar.py), también anterior a la corrida ([salida](analisis-salida.md)), y de
> [`aparte.py`](aparte.py), escrito después y solo para leer ([salida](aparte-salida.md)).
> **No se leyó ningún texto del test, de #144 ni de las legítimas reales.**

**En una oración:** ninguno de los 13 candidatos pasó la regla. Ningún prompt avisa menos en las llamadas reales de
call center sin perder estafas, y esperar una confirmación tampoco. **La configuración queda como en la evaluación
final** ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)).

## Verificación de los ZIP

- Cada ZIP se descomprimió en un directorio vacío nuevo, fuera del repositorio. Bajaron diez parciales; sus 18 archivos
  de corrida coinciden con los del final. El resto de las corridas está solo en el ZIP final.
- `commit.txt` y los manifiestos dan `7c52850`, el commit del tag, sin cambios sin commitear. La reserva es
  `reserva/test` en `8d563ad`.
- El sha256 de `colab/probar_exploracion_reales.py` en el tag coincide con `script-sha256.txt` (`fcfae8de…`), y el
  digest del modelo, con `digest.txt` (`b37049369adf…`). Ollama 0.40.14 en una Tesla T4.
- Humo de formato: 48/48 en los siete prompts. Las 23 corridas pasan el control.
- La corrida duró 2 h 06, contra las 2 h 40 estimadas.
- **La regla se aplicó en Colab y dio lo mismo que acá:** `fase-2.json` dice «sirven, en orden: ninguno», así que la
  fase 2 corrió solo con la base.
- Líneas inválidas: solo por contexto excedido. En las coreanas son entre 2.089 y 2.384 de las 4.193 líneas de OTRA,
  según el prompt; en la zona gris, 44 de 1.139. En las legítimas reales, desarrollo y el test no hay ninguna.

## Resultado de la regla

Fase 1. La referencia es la base con el primer aviso, corrida en esta misma sesión.

| candidato | coreanas avisadas | coreanas a tiempo | FA en las 33 legítimas reales | desarrollo: estafas · a tiempo · FA | por qué no sirve |
|---|---|---|---|---|---|
| **`base`, primer aviso (referencia)** | 33/33 | 27/27 | 23/33 | 43/46 · 29/36 · 20/94 | — |
| `base`, confirmación | 33/33 | 26/27 | 21/33 | 38/46 · 18/36 · 14/94 | las FA bajan 2 y tenían que bajar 7 |
| `c-rumbo` | 33/33 | 27/27 | 26/33 | 44/46 · 29/36 · 28/94 | las FA suben 3 |
| `c-rumbo`, confirmación | 33/33 | 26/27 | 23/33 | 41/46 · 22/36 · 21/94 | las FA no bajan |
| `p-niveles` | 32/33 | 24/27 | 12/33 | 25/46 · 20/36 · 16/94 | pierde 3 coreanas a tiempo |
| `p-minimo` | 32/33 | 23/27 | 19/33 | 39/46 · 31/36 · 48/94 | pierde 4 a tiempo; las FA bajan 4 |
| `p-lista` | 30/33 | 21/27 | 17/33 | 36/46 · 31/36 · 34/94 | pierde 3 coreanas y 6 a tiempo; las FA bajan 6 |
| `p-escalera` | 32/33 | 22/27 | 21/33 | 32/46 · 28/36 · 28/94 | pierde 5 a tiempo; las FA bajan 2 |
| `p-escalera`, confirmación | 32/33 | 20/27 | 18/33 | 30/46 · 17/36 · 19/94 | pierde 7 a tiempo; las FA bajan 5 |
| `p-sino` | 17/33 | 11/27 | 8/33 | 22/46 · 17/36 · 14/94 | pierde 16 coreanas |

En `p-niveles`, `p-lista`, `p-minimo` y `p-sino` la confirmación da lo mismo que el primer aviso: esos prompts no
escriben valores entre 0,3 y 0,5.

Fase 2, solo la base:

| conjunto | primer aviso | confirmación |
|---|---|---|
| Test, estafas avisadas | 76/100 | 71/100 |
| Test, antes del pedido | 43/80 | 30/80 |
| Test, a tiempo | 56/80 | 44/80 |
| Test, FA | 15/56 | 15/56 |
| Zona gris, avisos | 30/42 | 28/42 |

## Lectura

### 1. Nadie baja las FA reales sin perder estafas

- **Los que conservan las coreanas no bajan las FA.** La base con confirmación queda en 21 de 33; `c-rumbo`, en 26, y
  con confirmación, en 23.
- **Los que bajan las FA pierden estafas a tiempo.** `p-niveles` baja 11 FA y pierde 3 avisos a tiempo; `p-sino` baja
  15 y pierde la mitad de las coreanas.
- **Los del medio pierden de los dos lados:** `p-lista`, `p-minimo` y `p-escalera`.
- **`p-niveles` termina donde ya estaba `v4-corte`:** 32/33 coreanas, 24/27 a tiempo y 12/33 FA, contra 33/33, 23/27 y
  10/33 de `v4-corte` en la evaluación final. Es el perfil que el README esperaba de un prompt «por pedido».

### 2. Los prompts mueven el corte; ninguno separa claramente mejor

Las coreanas tienen 56 consultas válidas de mediana y las legítimas reales, 11. Con el primer aviso, una llamada más
larga tiene más oportunidades de avisar. Igualando el largo a las primeras 12 consultas:

| prompt | coreanas que ya avisaron | legítimas reales que ya avisaron | separa, reales | separa, desarrollo |
|---|---|---|---|---|
| `base` | 28/33 | 22/33 | 0,73 | 0,86 |
| `c-rumbo` | 33/33 | 25/33 | 0,74 | 0,84 |
| `p-niveles` | 24/33 | 11/33 | 0,73 | 0,73 |
| `p-sino` | 9/33 | 5/33 | 0,71 | 0,63 |
| `p-minimo` | 22/33 | 16/33 | 0,64 | 0,69 |
| `p-lista` | 17/33 | 15/33 | 0,57 | 0,74 |
| `p-escalera` | 11/33 | 19/33 | 0,49 | 0,66 |

«Separa» es la probabilidad de que una estafa tenga más riesgo promedio que una legítima en esas 12 consultas: 0,50 es
no separar.

- **En las llamadas reales ningún prompt separa mejor que la base:** van de 0,49 a 0,74 y la base da 0,73. Cambian
  cuánto avisan más que a quién.
- **En desarrollo la base es la que mejor separa** (0,86). Los prompts «por pedido» bajan a 0,63–0,74.
- **A igual largo, la base avisó 28 coreanas y 22 legítimas reales.** El 33 contra 23 de la llamada entera se debe en
  buena parte a que las coreanas son cinco veces más largas.
- **`p-niveles` es el corte que más distancia pone en los reales:** 24 contra 11 a las 12 consultas. La base con
  «riesgo ≥ 0,5» da 14 contra 4. La diferencia entre los dos es de 3 llamadas, dentro de lo que cambia al repetir.
- **Lo paga en las estafas generadas:** en desarrollo avisa 25 de 46, contra 43 de la base.
- **El umbral de 0,3 lo piden nuestras estafas generadas, no las coreanas.** La base escribe 0,7 o más en el 34 % de
  las consultas de las coreanas y en el 3 % de las del test. Con «riesgo ≥ 0,5» en la llamada entera avisa 28/33
  coreanas (17/27 a tiempo) y 5/33 legítimas reales, pero solo 37/100 estafas del test, con 6/56 FA.

### 3. Un prompt más corto no avisa mejor

- **Los dos prompts cortos avisan más en las legítimas de desarrollo y menos en las coreanas.** `p-minimo` (908
  caracteres) da 48/94 FA y `p-lista` (1.354), 34/94; la base (2.695) da 20/94. En las 75 legítimas que no deberían
  avisar: 30, 18 y 8. En las coreanas a tiempo: 23, 21 y 27.
- **Los prompts «por pedido» pierden las estafas sin pedido,** como estaba previsto: 0 a 5 de las 10 de desarrollo,
  contra 10/10 de la base y de `c-rumbo`.
- **`p-niveles` casi no avisa fuera de los pedidos críticos:** 1/75 en las legítimas que no deberían avisar, contra
  8/75 de la base. Pero deja sin aviso 21 de las 46 estafas de desarrollo.
- **El modelo respetó las escalas nuevas,** así que los resultados se pueden interpretar. En `p-escalera` no subió
  los escalones: escribe 0,3 en el 56 % de las consultas de las coreanas y 0,5 en el 2 %. La predicción para las
  legítimas reales con confirmación (entre 9 y 13) no se cumplió: dio 18.

### 4. Esperar una confirmación no sirve

- **En el test no saca ninguna FA:** 15/56 con las dos políticas. Y cuesta 12 avisos a tiempo (56 → 44) y 13 antes del
  pedido (43 → 30).
- **Las FA no son un aviso suelto.** Ninguna legítima del test tiene una sola consulta con riesgo ≥ 0,3: las 15 que
  avisan tienen dos o más, y 10 tienen cinco o más. En las legítimas reales, 14 de las 23 tienen cinco o más.
- En desarrollo sí baja las FA (20 → 14, y 8 → 3 en las estrictas), como en la simulación del README. No se traslada
  al test ni a las reales (23 → 21).

### 5. La misma configuración, corrida otra vez, mueve hasta 6 casos

La base de esta exploración es la configuración de la evaluación final, con el mismo modelo, semilla, Ollama y
conjuntos. Cambia cómo se corrió: la evaluación final pasó cada conjunto entero y cortó cada llamada en su primer
aviso; la exploración pasó solo la vista principal y siguió hasta el final.

| conjunto | cifra | evaluación final (2026-11-19) | esta corrida (2026-11-20) |
|---|---|---|---|
| Test | estafas avisadas | 73/100 | 76/100 |
| Test | antes del pedido | 37/80 | 43/80 |
| Test | a tiempo | 53/80 | 56/80 |
| Test | FA | 15/56 | 15/56 |
| Coreanas | avisadas · a tiempo | 33/33 · 27/27 | 33/33 · 27/27 |
| Legítimas reales | FA | 21/33 | 23/33 |
| Zona gris | avisos | 32/42 | 30/42 |
| Desarrollo | estafas · a tiempo · FA | 40/46 · 26/36 · 20/94 | 43/46 · 29/36 · 20/94 |

- **En las 3.060 consultas que están en las dos pasadas, el riesgo es el mismo en el 92 %.** De los 238 cambios, 228
  son de 0,1 o menos. Alcanzan para mover llamadas porque caen sobre el umbral: el modelo escribe 0,2 o 0,3 en más de
  la mitad de las consultas.
- **Las cifras que valen son las de la evaluación final.** La segunda pasada no las corrige ni las reemplaza: dice
  cuánto se mueven. En el test, 3 estafas avisadas, 6 antes del pedido y ninguna FA.
- **No se aisló la causa.** El runtime registrado es idéntico (Ollama, driver, GPU, digest, parámetros). Lo que cambia
  es el orden y la cantidad de consultas, como en [H11](../../../../docs/hallazgos/H11-el-riesgo-cambia-con-el-runtime.md).
  Es más que el ruido de repetir tal cual de [H02](../../../../docs/hallazgos/H02-ruido-entre-corridas.md) (2 de 2.213
  líneas).
- **Dentro de esta exploración la comparación es pareja:** los siete prompts corrieron en la misma sesión y del mismo
  modo. Todos fallan la regla por más que ese margen, salvo `p-niveles`, que queda a 2 avisos a tiempo del límite.

## Límites de esta lectura

- **Las coreanas y las 33 legítimas reales ya son datos de ajuste.** Se miraron 13 candidatos sobre ellas. La cifra
  de cualquier candidato elegido acá sería optimista.
- **Son 33 y 33.** Tres llamadas son 9 puntos, y al repetir cambiaron de lado 4 de las 33 legítimas reales.
- **Hay una versión de cada idea.** Que `p-lista` no sirva no prueba que ningún prompt corto sirva.
- **El test solo vio la base.** No se sabe cuánto perdería `p-niveles` ahí.
- **No se leyó ningún texto,** así que no se sabe por qué falla cada prompt.
- **Más de la mitad de las líneas de OTRA de las coreanas quedan fuera del contexto** (`num_ctx` 4096). No cambió el
  resultado porque las 33 avisan en las primeras 20 consultas, pero el detector deja de mirar esas llamadas por la mitad.

## Qué queda

> **Estado: propuesta sin discutir.**

- **No se integra nada y no hace falta un ADR:** la configuración no cambia.
- **Lo único para decidir es `p-niveles`.** En los dos conjuntos reales cambia mucho (FA de 23 a 12, con 32/33 estafas
  avisadas), que era lo que Mateo buscaba. No pasó la regla, en desarrollo avisa 25 de 46 estafas contra 43 de la base
  y no se midió en el test. La recomendación es no integrarlo. Si Mateo quiere ver el costo antes de descartarlo,
  falta una corrida de unos 30 minutos: `p-niveles` en el test y en la zona gris.
- **En la tesis va como resultado negativo,** al lado de la evaluación final: siete prompts y dos políticas, y ninguno
  mejora en llamadas reales sin perder estafas. El margen entre pasadas va con las cifras de la evaluación final.
- **Seguir cambiando el prompt no es el camino.** Lo que queda por probar es de otro tipo y es trabajo futuro: ajustar
  el modelo ([#176](https://github.com/Corchets/bitacora_tesis/issues/176)), o un aviso en dos niveles en la app, uno
  suave con «riesgo ≥ 0,3» y uno fuerte con «riesgo ≥ 0,5».
- **Falta lo que ningún conjunto tiene: estafas reales argentinas.** Las generadas piden un umbral bajo y las coreanas
  aguantan uno alto. Cuál se parece más a una estafa real de acá no se puede saber con estos datos.
- Las corridas del test y de desarrollo van a `reserva/test`. Las de las coreanas y las legítimas reales no se suben.
