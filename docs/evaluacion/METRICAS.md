# Métricas

> **Estado: propuesta sin discutir.** Definiciones para revisar junto al equipo.
> Las marcas de referencia se precisan en
> [D07](../gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico)
> y la política de alerta y evaluación en
> [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

Define las mediciones de las [preguntas del proyecto](../investigacion/PREGUNTAS-DE-INVESTIGACION.md):
detección incremental (PI1) y margen temporal de la alerta (PI2).

## 1. Marcas temporales

Todas se expresan en segundos desde el inicio de la grabación.

| Marca | Qué representa | De dónde sale |
|---|---|---|
| `T_A` | Momento en que el sistema emite la primera alerta según la política evaluada | Registro de ejecución del sistema |
| `T_R` | Inicio del primer pedido de alto riesgo | Anotación humana de la conversación |
| `T_C` | Inicio del primer cumplimiento observable del pedido por la víctima simulada | Anotación humana; queda sin dato si no ocurre o no se puede observar |

El [manual de anotación](../corpus/MANUAL-ANOTACION.md) debe precisar pedido,
cumplimiento y ambigüedades. Un disparo de reglas no determina el `T_R` de referencia.

`T_R` y `T_C` pueden caer dentro de una intervención: no se asignan automáticamente
al comienzo del turno que los contiene. Al comparar tiempos se usa el mismo origen
temporal. `T_A` registra la emisión efectiva del aviso, incluidas las demoras del ASR
y del detector; no se retrotrae al instante del audio que produjo la evidencia.

La política que produce `T_A` se fija antes de evaluar. Exigir dos actualizaciones
es una alternativa pendiente en D08. Si hay varios caminos de alerta, se registran
por separado y se identifica cuál generó el primer aviso mostrado.

## 2. Margen de la alerta

- `L_R = T_R − T_A`: margen respecto del pedido peligroso.
- `L_C = T_C − T_A`: margen respecto del cumplimiento simulado.

Positivo significa que la alerta llegó antes; cero, al mismo tiempo; negativo,
después. Por ejemplo:

| Evento | Tiempo |
|---|---:|
| Atacante empieza a pedir el código (`T_R`) | 58 s |
| Sistema alerta (`T_A`) | 61 s |
| Víctima empieza a dictarlo (`T_C`) | 64 s |

En ese caso, `L_R = −3 s` y `L_C = 3 s`: el aviso llegó después del pedido y antes
del cumplimiento. Esto describe la simulación; no demuestra que una persona real
habría evitado el daño.

Se informa la distribución, mediana y rango intercuartil de los márgenes y cuántas
conversaciones permiten calcularlos. Sin alerta, la llamada cuenta como no detectada
y el margen queda sin dato. Sin cumplimiento, no se infiere prevención lograda.

## 3. Alertas con margen suficiente

`Preventive@δ` mide la proporción de llamadas de vishing advertidas al menos `δ`
segundos antes de una marca de referencia `X`:

```text
Preventive@δ(X) = (llamadas de vishing con T_A ≤ X − δ) / (llamadas de vishing evaluables para X)
```

Se identifica la referencia (`T_R` o `T_C`). Las llamadas sin alerta permanecen en
el denominador. Si falta una marca, se informa cuántas quedaron fuera y por qué.

La referencia principal y los valores de `δ` se acuerdan en D07/D08 antes del test.
Los 5, 10 y 20 segundos del borrador anterior son candidatos, sin aprobación registrada.

## 4. Qué se mide

| Pregunta | Medida e interpretación |
|---|---|
| ¿Distingue fraude de llamadas legítimas? | Precision, recall y F1 sobre decisiones tomadas con prefijos de la conversación. Se define qué instante y qué unidad se comparan. |
| ¿Cuántas legítimas reciben un aviso incorrecto? | Llamadas legítimas con al menos una alerta / total de llamadas legítimas evaluadas. |
| ¿Cuándo avisa? | Llamadas detectadas y sin alerta; márgenes `L_R` y `L_C`; alertas con margen suficiente. |
| ¿Qué cambia por el ASR? | Mismo detector sobre texto manual y texto reconocido: errores de transcripción (WER), términos críticos perdidos y cambios en detección, falsas alarmas y márgenes. |
| ¿Sigue el ritmo del audio? | Tiempo de cómputo / duración del audio (`RTF`), demora entre evidencia disponible y aviso, y memoria usada. Se registra el hardware. |
| ¿Explica el motivo correctamente? | Revisión del motivo mostrado contra los fragmentos humanos de referencia; declarar qué casos se revisaron. Una anotación parcial no permite medir todas las etiquetas como presentes/ausentes. |

AUPRC/AUROC requieren puntajes; macro-F1, etiquetas por clase. Falsas alertas por hora
requiere definir avisos distintos. Su uso se acuerda en el protocolo.

En texto sin timestamps se informa el turno del aviso, sin convertirlo a segundos
con una duración supuesta. Las mediciones en computadora se reportan como tales.

### Balance y precisión de las alertas

La precisión observada depende de la proporción de fraude del conjunto evaluado;
no se traslada directamente de un corpus balanceado al uso cotidiano.
[Williams (2021)](https://arxiv.org/abs/2007.01905) explica esta relación.

> **Estado: propuesta sin discutir.** Analizar frecuencias hipotéticas de fraude
> como parte de [D08](../gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

Para decisiones por conversación, si `r` es la proporción de fraudes con alerta,
`f` la proporción de legítimas con alerta y `p` la frecuencia hipotética de fraude:

```text
precision(p) = (p × r) / (p × r + (1 − p) × f)
```

Se usa la misma política y horizonte de evaluación para `r` y `f`. Este cálculo
supone que ambas tasas se mantienen al cambiar `p`; es un análisis de sensibilidad,
no evidencia de rendimiento real ni una estimación de la frecuencia de estafas.
No se calcula precisión si el denominador es cero.

Se informan conteos y denominadores de detección y falsas alarmas, junto con su
incertidumbre. Si se incluyen legítimas cotidianas y negativos difíciles, se
desglosan: tampoco se supone que su mezcla represente el uso cotidiano.

## 5. Pendientes para congelar la evaluación

- Validar las marcas `T_R`/`T_C` y la referencia mínima por conversación (D07).
- Acordar la política de alerta que produce `T_A` y las referencias de `Preventive@δ` (D08).
- Elegir los instantes o prefijos comparables y los márgenes `δ` (D08).
- Fijar el criterio de falsas alarmas, los datos para ajustar y el test reservado (D08).
- Acordar la composición de legítimas, el análisis de frecuencias hipotéticas y cómo
  informar incertidumbre con el tamaño obtenido (D08).

El primer resultado útil es una conversación con su evidencia disponible, alertas
y marcas de referencia sobre una línea de tiempo. Si el detector produce un puntaje,
se agrega su evolución. La figura debe mostrar también los errores y avisos tardíos.
