# #52, exploración con los conjuntos reales

> **Estado: propuesta sin discutir.** La pidió Mateo el 2026-11-20, después de ver la
> [evaluación final](../2026-11-12_evaluacion-final/analisis.md): una última prueba para mantener la detección en las
> estafas reales y avisar menos en las llamadas reales de call center. **Es exploración y no reemplaza a la evaluación
> final:** lo que salga se informa aparte, y si se integra, se avisa que se eligió mirando estos conjuntos.

## Por qué

La configuración de la evaluación final (`c-consejos-corte-riesgo`, primer aviso con «riesgo ≥ 0,3») avisa las 33
estafas reales coreanas y también 21 de las 33 legítimas reales.

- **En una llamada real el modelo da 0,2 en dos de cada tres consultas,** sea estafa o no. Queda a un escalón del aviso,
  y cada turno de OTRA es otra oportunidad de escribir 0,3.
- **19 de los 21 avisos en legítimas reales son un 0,3 exacto.**
- **Los motivos de esos 21 avisos se reparten en tres grupos:** unos 8 por un pedido de código o de datos de la cuenta,
  unos 7 leen la venta como estafa (una promoción, un precio que cambia, apuro por cerrar) y unos 6 son genéricos.

## Lo que esta prueba les cuesta a los conjuntos

- **Las 33 coreanas y las 33 legítimas reales pasan a ser datos de ajuste.** Para lo que se elija acá, dejan de ser un
  test externo. La cifra que vale como evaluación sigue siendo la de la evaluación final.
- **Qué se leyó para diseñarla:** las cifras de la evaluación final y los motivos que escribió el modelo en los 21
  avisos de las legítimas reales. No se leyó ningún texto de las legítimas reales, de las coreanas ni del test.
- **La zona gris de Medicare (42) no se miró:** ni sus textos ni sus motivos. Son otras llamadas comerciales reales, y
  sirven para ver si lo que baje en las 33 baja también ahí.
- **El test reservado vuelve a correr,** solo para informar cuánto cuesta el cambio en nuestras estafas. No elige.

## Las dos palancas

### 1. La política de aviso, sin tocar el prompt

**«Confirmación»:** avisa en la primera línea de OTRA con riesgo ≥ 0,5, o en la segunda con riesgo ≥ 0,3 (no hace falta
que sean seguidas). Una señal fuerte avisa ya; una débil espera a repetirse.

- **Por qué:** si los avisos en legítimas reales son un 0,3 suelto y los de las estafas se repiten, pedir el segundo
  los separa. Las coreanas dan margen: el pedido llega en la línea 57 de mediana.
- **El costo ya se conoce en desarrollo,** simulado sobre las corridas de `c-consejos` de la
  [revisión de producto](../2026-11-10_revision-producto/analisis.md), que tienen todas las líneas:

  | `c-consejos`, alcance-140 | estafas | antes del pedido | a tiempo | FA | FA estrictas |
  |---|---|---|---|---|---|
  | primer aviso | 41/46 | 19/36 | 28/36 | 22/94 | 10/75 |
  | confirmación | 38/46 | 15/36 | 20/36 | 15/94 | 4/75 |
  | primer aviso, repetición | 42/46 | 18/36 | 28/36 | 18/94 | 7/75 |
  | confirmación, repetición | 39/46 | 15/36 | 20/36 | 14/94 | 3/75 |

  **En nuestras estafas generadas, que son cortas, confirmar cuesta 8 avisos a tiempo de 36.** Ahí el pedido llega
  enseguida y una línea de espera lo deja pasar.

### 2. Dos variantes de un párrafo

Cada una es `c-consejos-corte-riesgo` con **un solo párrafo cambiado**
([`test_exploracion_reales.py`](../../tests/test_exploracion_reales.py) lo comprueba). Salen de la
[política de producto](../2026-11-10_revision-producto/POLITICA.md) y de los tres grupos de motivos de arriba, no de la
redacción de ninguna llamada.

**`c-comercial`** ([`tarea_c_comercial.txt`](../../prompts/tarea_c_comercial.txt)) agrega dos oraciones al párrafo
final:

> Una llamada legítima también puede pedir el nombre, el DNI, la fecha de nacimiento, una dirección o un correo, avisar
> un problema u ofrecer un producto. Eso solo no la vuelve una estafa. **Tampoco la vuelve una estafa que sea una
> llamada comercial: una empresa que llama para vender, ofrecer un plan o una promoción, cambiar un precio, coordinar
> una visita o una instalación, insistir para cerrar o avisar que la llamada se graba está haciendo lo de siempre. Lo
> que cuenta es qué le pide a PROTEGIDA, no que quiera venderle algo.**

- **Por qué:** en la política, la intención «vender» no avisa por sí sola. Apunta al grupo que lee la venta como estafa.
- **Qué puede salir mal:** `c-freno` también reescribió este párrafo y sumó 9 FA estrictas. Esta no agrega condiciones para
  avisar, solo normaliza; igual, el párrafo va justo antes de la salida y es sensible. Puede tapar una estafa disfrazada
  de oferta mientras todavía no pidió nada.

**`c-rumbo`** ([`tarea_c_rumbo.txt`](../../prompts/tarea_c_rumbo.txt)) cambia el párrafo del aviso anticipado:

> Mirá la llamada entera y hacia dónde va, no solo la última frase. ~~Si ya se parece a una estafa, conviene avisar
> aunque todavía no haya un pedido.~~ **Conviene avisar antes del pedido cuando OTRA ya está llevando a PROTEGIDA hacia
> alguno de esos pedidos. Que se presente como alguien de confianza, ofrezca algo o apure, sin ir hacia un pedido,
> todavía no alcanza para avisar.**

- **Por qué:** «si ya se parece a una estafa» deja avisar por el disfraz y el gancho, y una venta real tiene los dos.
  La política juzga por lo que OTRA pide. Esta ata el aviso anticipado al rumbo hacia un pedido.
- **Qué puede salir mal:** es la oración que le da a C su ventaja de anticipación. Puede perder avisos antes del pedido
  y estafas sin pedido, que en el test ya son la mitad (10/20).

**Longitud:** `c-consejos` 2.695 caracteres; `c-comercial` 3.036 (+341); `c-rumbo` 2.840 (+145).

### La referencia que ya existe

`v4-corte`, la referencia simple de la evaluación final, ya cumple a medias: 33/33 coreanas (23/27 a tiempo) y 10/33 FA
reales. En el test da 64/100, 50/80 a tiempo y 15/56 FA. Consulta en todas las líneas, de los dos lados. No vuelve a
correr; queda como vara: lo que se elija tendría que ser mejor que eso.

## Qué corre

En Colab T4, con Ollama 0.40.14, el digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, roles,
`--sin-reglas` y `--solo-otra`. Corre **todas las líneas de OTRA** (`--seguir-tras-aviso`), así las dos políticas se
aplican después sobre los mismos riesgos.

1. **Humo de formato** en los 3 casos de siempre (48 líneas), con las tres. Si no pasa la base, no corre nada; la
   variante que no pasa no corre.
2. **Las tres** (`base`, `c-comercial` y `c-rumbo`) **sobre cada conjunto,** en este orden:
   1. las 33 coreanas de #144;
   2. las legítimas reales: las 33 y las 42 de la zona gris;
   3. desarrollo, [`alcance-140`](../../casos/listas/alcance-140.txt);
   4. el test reservado, su vista principal (100 estafas y 56 legítimas).

Las legítimas reales son obligatorias: hay que subir a Colab la carpeta `sets/` de la custodia. Dura alrededor de
1 h 30, estimado y sin medir. Las llamadas largas se quedan sin contexto (`num_ctx` 4096) cerca de la línea 70: esas
líneas son inválidas y no avisan.

## Regla, escrita antes de correr

**Referencia:** `base` con el primer aviso, corrida en esta misma sesión.

**Candidatos,** en este orden: `base` con confirmación; `c-comercial` y `c-rumbo` con el primer aviso; `c-comercial` y
`c-rumbo` con confirmación.

**Un candidato sirve** si, contra la referencia, cumple las tres:
1. en las coreanas, pierde a lo sumo una estafa avisada;
2. en las coreanas, pierde a lo sumo un aviso a tiempo;
3. en las 33 legítimas reales, baja 7 o más las FA. Es un tercio de las 21 de la evaluación final, y más del doble del
   ruido entre sesiones (hasta 3).

**Si sirven varios,** se elige el que menos pierde a tiempo en desarrollo. Si empatan, el de menos FA reales; si
empatan, el primero de la lista, que es el que cambia menos. **Si no sirve ninguno,** queda la configuración de la
evaluación final.

**El test no elige.** Se informa para todos, y se marca **costo alto** si el elegido pierde 8 o más a tiempo (de 80) o
10 o más estafas avisadas (de 100) contra la referencia.

**Integrarlo o no lo decide Mateo,** con el costo a la vista (2026-11-20: «si cambia mucho los resultados lo integramos
igual avisando»). Lo que se integre va con un ADR que diga que se eligió después de la evaluación final, mirando los
conjuntos reales.

## Solo para mirar (no decide)

- los avisos en la zona gris de Medicare, que no se miró para diseñar nada;
- las FA en las 75 legítimas de desarrollo que no deberían avisar;
- cuántas consultas con riesgo ≥ 0,3 tiene cada llamada, por conjunto;
- las líneas inválidas por contexto excedido;
- qué coreanas y qué legítimas reales cambian con el elegido.

## Después de correr

1. Descomprimir cada ZIP en un directorio vacío nuevo, **fuera del repositorio:** traen el texto del test, de las
   coreanas y de las legítimas reales. Correr todo Python con `-I`.
2. Verificar: los parciales coinciden con el final; el commit es el del tag, sin cambios sin commitear; el sha256 de
   `colab/probar_exploracion_reales.py` y el digest coinciden.
3. Correr `python -I analizar.py --datos CARPETA` desde acá.
4. Acá va solo `analisis.md`, con cifras e identificadores. Las corridas del test van a `reserva/test`; las de las
   coreanas y las legítimas reales no se suben.

[`analizar.py`](analizar.py) está escrito antes de correr y aplica esta regla tal cual. La regla que vale es la de este
README, en el commit del tag.
