# #143, revisión de producto y última prueba antes de congelar

> **Estado: propuesta sin discutir.** Desarrollo; la reserva, las legítimas de test y #144 no se tocan. Preparada el
> 2026-11-10, a pedido de Mateo, sobre la configuración congelada `c-premisa-corte-riesgo`
> ([análisis de la sensibilidad](../2026-11-10_sensibilidad-c/analisis.md)). El 2026-11-18 Mateo aceptó las etiquetas y
> los tres textos, sacó de la regla la vía para pasar solo por bajar las FA, y dio el OK para correr. La regla de abajo
> es la del tag `colab/143-revision-producto`, anterior a cualquier resultado.
>
> **Resultado (2026-11-18): no pasa ninguna.** Está en [`analisis.md`](analisis.md). Mateo adoptó igual `c-consejos-corte-riesgo`,
> por fuera de la regla ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)).

## Qué hay en esta carpeta

| archivo | qué es | cuándo se escribió |
|---|---|---|
| [`POLITICA.md`](POLITICA.md) | Cuándo le sirve un aviso a una persona y cuándo molesta, y qué hacer con el DNI y los códigos | Antes de abrir casos y resultados (el borrador está en el commit `c638eda`) |
| [`FUENTES-PRODUCTO.md`](FUENTES-PRODUCTO.md) | Fuentes nuevas (P01…) sobre el DNI y los códigos | Relevamiento aparte, sin ver casos ni resultados |
| [`REVISION-LEGITIMAS.md`](REVISION-LEGITIMAS.md) y [`etiquetas-producto.json`](etiquetas-producto.json) | Las 94 legítimas de `alcance-140`, una por una, con esa política | Antes de abrir resultados (commit `6c1fca0`) |
| [`HALLAZGOS.md`](HALLAZGOS.md) | Los resultados de la sensibilidad cruzados con las etiquetas, y la revisión del prompt | Después de ver resultados: no decide |
| [`VARIANTES.md`](VARIANTES.md) | Los tres textos, con su porqué y sus fuentes | Después de ver resultados; los textos salen de la política y de las fuentes |
| [`analizar.py`](analizar.py) | Aplica la regla de abajo | Antes de correr |
| [`analisis.md`](analisis.md) y [`analisis-salida.md`](analisis-salida.md) | El resultado de la regla, la verificación de los ZIP y la lectura | Después de correr (2026-11-18) |

## Por qué

- **La mitad de las falsas alarmas no lo son.** De las 26 FA de la configuración congelada, 13 caen en llamadas que no
  deberían avisar, 12 en llamadas donde el aviso coincide con un consejo oficial (casi todas, «el banco» que llama por
  seguridad) y 1 en un soporte que pide acceso remoto ([hallazgos](HALLAZGOS.md)).
- **Siguen sin aviso 3 de las 17 estafas con pedido de código o clave.** La regla del código está atada a «un banco,
  una empresa o un organismo». Para Mateo (2026-11-10) la regla es la intención: ningún código se le dicta a quien
  llamó, se presente como se presente.
- **El párrafo del DNI no frena lo que debería.** 6 de las 13 FA estrictas avisan justo cuando un soporte o un vendedor
  pide el DNI, y en los turnos y las entregas casi no avisa (1 de 28).

**El riesgo sigue siendo de sobreajuste:** es la segunda búsqueda a mano sobre los mismos 140 casos. Por eso cada
variante cambia un solo párrafo, el texto sale de la política y de fuentes externas, y el número honesto lo dan
después la reserva y #144.

## Las tres variantes

Cada una es la configuración congelada con **un solo párrafo cambiado**. El resto es igual: corte tras el riesgo
(`num_predict` 14), «riesgo ≥ 0,3», el motivo de C en el primer aviso y solo OTRA. Los textos completos, con lo que
cambia y sus fuentes, están en [`VARIANTES.md`](VARIANTES.md).

| variante | qué cambia | hipótesis |
|---|---|---|
| `c-codigo` | [`tarea_c_codigo.txt`](../../prompts/tarea_c_codigo.txt): en el párrafo del número no agendado, la regla del código deja de depender de quién llama («un código que le llegó, una clave o un PIN no se le dicen a nadie que llamó, sea quien sea y lo pida para lo que lo pida, y aunque no lo llame código ni clave»), y aclara que dar un código o decir que no se comparte no es pedirlo. | El modelo deja en 0,2 los pedidos de código con un pretexto que no es institucional, porque la regla nombra instituciones. Y avisa cuando OTRA nombra un código sin pedirlo. |
| `c-consejos` | [`tarea_c_consejos.txt`](../../prompts/tarea_c_consejos.txt): ese mismo párrafo, cambiado por los consejos de siempre de los bancos y los organismos, solo de credenciales y actos sin vuelta atrás, más «ante la duda, cortar y llamar uno mismo al número oficial». | Es la idea de Mateo: que razone como una persona a la que le dieron esos consejos. Es más amplia que `c-codigo` y no nombra el caso indirecto. |
| `c-freno` | [`tarea_c_freno.txt`](../../prompts/tarea_c_freno.txt): el párrafo final («una llamada legítima también puede pedir el nombre, el DNI…») reescrito por intención: esos datos se juzgan por para qué los piden, pesan con un premio, un beneficio, una deuda o un bloqueo inesperados, y que OTRA ya los sepa no prueba quién es. | El freno actual es parejo para todos los pretextos. Juzgado por el pretexto, debería avisar menos en ventas y reclamos, y no perder las estafas que piden datos. |

**Lo que quedó afuera, y por qué:**
- **Sacar «Que el número no esté agendado pesa»** y **acortar la salida** (describe tres campos que ya no se generan):
  son los dos recortes que deja la [revisión del prompt](HALLAZGOS.md#el-prompt). No buscan avisar más, y cada uno
  sería otra variable. Quedan anotados para después de congelar.
- **Combinar variantes:** sería otra prueba, con otra regla. Si pasan dos, la regla elige una.
- **Cambiar la definición del riesgo** («qué tan probable es que sea una estafa») por una atada al pedido: cambia la
  salida y la escala, y `c-ancla` ya mostró que tocar esa línea mueve todo el medio.

## Qué corre

En Colab T4, con Ollama 0.40.14, el digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, roles,
`--sin-reglas` y `--solo-otra`. Corre todas las líneas de OTRA (`--seguir-tras-aviso`). El aviso es la primera línea de
OTRA con «riesgo ≥ 0,3».

1. **Humo de formato** en los 3 casos de siempre (48 líneas), con las cuatro: la base (`c-premisa-corte-riesgo`) y las
   tres variantes. Pasa la que lee el riesgo, con su coma, en las 48. La que no pasa no corre; si no pasa la base, no
   corre nada.
2. **Sobre los 244:** la base, `c-codigo`, `c-consejos` y `c-freno`, en ese orden.
3. **Repeticiones sobre [`alcance-140`](../../casos/listas/alcance-140.txt),** en el mismo orden.

Dura alrededor de 1 h 10. El Colab está en
[`colab/README-PUNTAJE-TOKEN.md` §9](../../colab/README-PUNTAJE-TOKEN.md#9-revisión-de-producto-tag-colab143-revision-producto).

## Regla, escrita antes de correr

> La regla se calcula en dos versiones y se informan las dos. **Decide «producto»:** Mateo aceptó las
> [etiquetas](REVISION-LEGITIMAS.md) el 2026-11-18 (`DECIDE` en `analizar.py`). La «original» no decide.

**Vista:** dentro del alcance, `alcance-140`. Son 46 estafas (36 con pedido y 15 con cumplimiento) y 94 legítimas.

**Cifras de detección,** las mismas de la sensibilidad:
- estafas avisadas (/46);
- avisos antes del pedido (T_A < T_R, /36);
- avisos a tiempo (T_A ≤ T_R, /36);
- avisos antes del cumplimiento (T_A < T_C, /15).

**Falsas alarmas,** según la versión. Las líneas inválidas no avisan.

| versión | FA con tope | FA total | lo que no cuenta |
|---|---|---|---|
| **producto** (decide) | **FA estrictas:** avisos en las 75 «no debería avisar» | las mismas, /75 | Los avisos en las 18 tolerables y en ENT-L-SOPORTE-005 («debería avisar») se informan aparte |
| **original** (se informa) | FA en las 29 cotidianas (`tipo_legitima`) | FA en las 94 | — |

Cada variante se compara con la base de la misma sesión.

**Pasa** si cumple las cuatro condiciones:
1. suma 3 o más en al menos una cifra de detección;
2. no pierde 3 o más en ninguna cifra de detección;
3. no suma 3 o más en las FA con tope;
4. en la repetición, contra la repetición de la base, suma 3 o más en una cifra en que ganó la primera corrida, sin
   perder 3 o más en ninguna y sin sumar 3 o más en las FA con tope.

**Bajar las FA no alcanza para pasar** (Mateo, 2026-11-18): una variante que no suma 3 o más en ninguna cifra de
detección no pasa, aunque avise menos. Lo que baje se informa aparte.

**Si pasan varias,** se elige la que más suma en estafas y a tiempo, juntas, en la primera corrida. Si empatan, la de
menos FA total. **Si no pasa ninguna,** queda `c-premisa-corte-riesgo`.

**La preferencia de Mateo no decide.** El 2026-11-18 dijo que la que más le gusta es `c-consejos`, y que `c-codigo`
suma restricciones que pueden hacer que el modelo se comporte peor. Queda anotado antes de correr; elige la regla.

Lo que se adopte reemplaza a la base en la evaluación final, con todo lo demás igual. Es provisorio, como siempre, hasta
la reserva y #144.

## Solo para mirar (no decide)

- **las estafas con pedido de código o clave (/17):** cuántas avisa cada una y cuántas a tiempo;
- las 6 estafas que piden datos personales;
- las FA por intención de la llamada, por escenario, en las legítimas «ejemplares» y en las que piden el DNI;
- los avisos en las tolerables y en ENT-L-SOPORTE-005, caso por caso;
- la otra versión de la regla;
- la curva con u = 0,1…0,9, los avisos de un 0,3 exacto, la latencia, el motivo de cada FA estricta nueva y
  `alcance-91`.

## Después de correr

1. Descomprimir cada ZIP en un directorio vacío nuevo, y correr todo Python con `-I`.
2. Verificar: los parciales coinciden con el final; el commit es el del tag, sin cambios sin commitear; el sha256 de
   `colab/probar_revision_producto.py` y el digest coinciden; no hay casos de la reserva.
3. Copiar las carpetas acá y correr `python -I analizar.py`.

`analizar.py` está escrito antes de correr y aplica esta regla tal cual. La regla que vale es la de este README, en el
commit del tag.
