# #52, exploración con los conjuntos reales

> **Estado: propuesta sin discutir.** La pidió Mateo el 2026-11-20, después de ver la
> [evaluación final](../2026-11-12_evaluacion-final/analisis.md): una última prueba para mantener la detección en las
> estafas reales y avisar menos en las llamadas reales de call center. **Es exploración y no reemplaza a la evaluación
> final:** lo que salga se informa aparte, y si se integra, se avisa que se eligió mirando estos conjuntos.
>
> **Resultado (2026-11-20):** corrió con el tag `colab/52-exploracion-reales-2` y ningún candidato pasó la regla. La
> configuración queda como en la evaluación final. Ver el [análisis](analisis.md).

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
- **El test reservado lo tocan solo la base y lo que la regla ya eligió** sin mirarlo.
- **Son trece candidatos sobre 33 y 33 casos:** elegir el mejor entre tantos favorece al que tuvo suerte. Por eso la
  regla pide una baja grande, y la zona gris y el test se miran después.

## De dónde salen los candidatos

Mateo, el 2026-11-20: no seguir agregando párrafos del tipo «esto no es una estafa, esto sí», probar algo más simple con
los puntos importantes marcados, y pensar el problema desde afuera en vez de emparchar.

**Se pidieron tres diseños desde cero a subagentes con contexto limpio.** Recibieron el producto, el contrato técnico,
la política y las cifras de arriba. No leyeron ningún archivo del repositorio ni ningún caso. Sus textos entran tal
cual, sin retoques:
- uno escribió el prompt más simple que pudiera funcionar (`p-lista` y `p-minimo`);
- otro rediseñó qué se le pregunta al modelo (`p-niveles` y `p-sino`);
- el tercero hizo una crítica de afuera y una apuesta (`p-escalera`).

**El diagnóstico del crítico,** que es una hipótesis y es lo que esta prueba pone a prueba:
- **El modelo no tiene una probabilidad, tiene tres estados:** 0,1 o menos es «limpio», 0,2 es «no sé» y 0,3 es
  «sospecho». El umbral cae justo entre los dos últimos, así que no hay umbral que mover.
- **«Qué tan probable es que sea una estafa» obliga a juzgar quién es OTRA,** que es lo que la política dice que no se
  juzga y lo que el propio prompt admite que no se puede verificar.
- **El párrafo que describe cómo se arma una estafa describe también una llamada de telemarketing,** y «conviene avisar
  aunque todavía no haya un pedido» autoriza el 0,3 sin evidencia.
- **Avisar en el primer 0,3 es un máximo sobre toda la llamada:** con unas 12 consultas, 2,6 % por consulta da 27 % de
  FA y 8,3 % da 64 %. Las dos cifras medidas salen de la misma cuenta.
- **El 33/33 en las coreanas no es detección del pedido:** avisa en la línea 6, unas 50 líneas antes, por el mismo
  mecanismo que da las FA.
- **Confirmar sobre la escala actual demora todo por igual,** porque la escala no distingue «sospecho» de «ya pidió».

## Los candidatos

Todos corren como la configuración congelada: salida cortada tras el riesgo (`num_predict` 14), aviso con
«riesgo ≥ 0,3» y solo en las líneas de OTRA.

| prompt | idea | qué es el riesgo | caracteres |
|---|---|---|---|
| `base` (`c-consejos`) | La configuración de la evaluación final | Qué tan probable es que sea una estafa | 2.695 |
| [`p-lista`](../../prompts/tarea_p_lista.txt) | Una sola pregunta: qué le pide OTRA. La lista de pedidos peligrosos, qué es prepararlos y «cualquier otro pedido es normal». No nombra disfraz, apuro ni estafa | Tres niveles: 0.0 nada, 0.5 lo prepara, 0.9 lo hizo | 1.354 |
| [`p-escalera`](../../prompts/tarea_p_escalera.txt) | Registrar hasta dónde llegó OTRA hacia un pedido crítico, sobre los valores que el modelo ya escribe. El «no sé» tiene dónde caer sin avisar | Seis escalones acumulados: 0.2 plantea algo que toca la plata, 0.3 prepara el pedido, 0.5 lo hizo | 2.824 |
| [`p-niveles`](../../prompts/tarea_p_niveles.txt) | Ubicar la llamada en un casillero. La llamada comercial tiene el suyo, aunque insista o apure | Cuatro niveles: 0.0 no dijo para qué llama, 0.1 comercial, 0.5 lleva a un pedido, 0.9 lo pidió | 1.945 |
| [`c-rumbo`](../../prompts/tarea_c_rumbo.txt) | El único que parte del congelado: un párrafo cambiado, que ata el aviso anticipado a que OTRA vaya hacia un pedido | El de la base | 2.840 |
| [`p-sino`](../../prompts/tarea_p_sino.txt) | Una pregunta de sí o no: si PROTEGIDA sigue y hace lo que le pidan, ¿termina haciendo algo de la lista? | Dos valores: 0.1 no, 0.9 sí | 1.871 |
| [`p-minimo`](../../prompts/tarea_p_minimo.txt) | `p-lista` en menos de 500 caracteres, sin definir «preparar». Mide cuánto de eso hace falta | Los tres niveles de `p-lista` | 908 |

Las salidas están en [`salida_json_p_tres.txt`](../../prompts/salida_json_p_tres.txt),
[`salida_json_p_escalera.txt`](../../prompts/salida_json_p_escalera.txt),
[`salida_json_p_niveles.txt`](../../prompts/salida_json_p_niveles.txt) y
[`salida_json_p_sino.txt`](../../prompts/salida_json_p_sino.txt).

**Lo que tienen en común los cinco «p-»:**
- Preguntan por el pedido y no nombran la palabra «estafa».
- Son de la familia del prompt viejo `v4`, así que se espera su perfil: menos FA y aviso más tardío. Lo nuevo es el
  nivel intermedio («lo prepara») y que no llevan lista de excepciones.
- **Una empresa real que pide un código o los datos de una tarjeta va a seguir avisando:** es un pedido crítico según
  la política. Ese tercio de las FA reales es un piso que ningún prompt baja.

**Lo que quedó afuera:**
- `c-comercial`, que le agregaba al párrafo final que una llamada comercial no es una estafa. Es el tipo de parche que
  Mateo pidió no seguir probando.
- **La cascada que propuso el crítico:** las reglas de palabras clave marcan el momento, el modelo contesta solo sobre
  la última intervención de OTRA y la app lleva la memoria. Necesita una regla nueva en la app; queda como trabajo futuro.
- **Leer los logits del primer número** para tener un puntaje continuo. Es [#176](https://github.com/Corchets/bitacora_tesis/issues/176).

## Las dos políticas de aviso

Se aplican después, sobre los mismos riesgos, sin volver a correr:
- **«Primer aviso»,** la de hoy: la primera línea de OTRA con riesgo ≥ 0,3.
- **«Confirmación»:** la primera línea de OTRA con riesgo ≥ 0,5, o la segunda con riesgo ≥ 0,3 (no hace falta que sean
  seguidas). Una señal fuerte avisa ya; una débil espera a repetirse.

En `p-lista`, `p-minimo`, `p-niveles` y `p-sino` las dos dan lo mismo si el modelo respeta sus niveles, porque no hay
nivel entre 0,3 y 0,5. En `p-escalera` es la regla para la que se diseñó: 0.3 es «lo prepara» y 0.5 es «ya lo pidió».

**Sobre la escala actual, confirmar ya se sabe que cuesta.** Simulado en desarrollo con las corridas de `c-consejos` de
la [revisión de producto](../2026-11-10_revision-producto/analisis.md):

| `c-consejos`, alcance-140 | estafas | antes del pedido | a tiempo | FA | FA estrictas |
|---|---|---|---|---|---|
| primer aviso | 41/46 | 19/36 | 28/36 | 22/94 | 10/75 |
| confirmación | 38/46 | 15/36 | 20/36 | 15/94 | 4/75 |
| primer aviso, repetición | 42/46 | 18/36 | 28/36 | 18/94 | 7/75 |
| confirmación, repetición | 39/46 | 15/36 | 20/36 | 14/94 | 3/75 |

## Predicciones, escritas antes de correr

Son del subagente que diseñó `p-escalera`, para esa variante con confirmación. Son apuestas, no mediciones.
- Legítimas reales: de 21 a entre 9 y 13 de 33.
- Legítimas generadas del test: 12 o menos de 56.
- Estafas del test con pedido: 50 o más de 80 a tiempo.
- Estafas del test sin pedido: de 10 a entre 4 y 6 de 20. Es el costo declarado de preguntar por el pedido.
- Coreanas: entre 31 y 33, con la línea del aviso corrida de la 6 hacia la del pedido. Si sigue en la 6, el modelo no
  está leyendo la escala.

**Lo primero que hay que mirar** es qué valores escribe cada prompt. Si un «p-» sigue escribiendo 0.2 y 0.3 cuando su
escala no los tiene, el anclaje no prendió y el resto no se puede interpretar.

## Qué corre

En Colab T4, con Ollama 0.40.14, el digest `b37049369adf…`, `num_ctx` 4096, seed 42, temperatura 0, roles,
`--sin-reglas` y `--solo-otra`. Corre **todas las líneas de OTRA** (`--seguir-tras-aviso`).

1. **Humo de formato** en los 3 casos de siempre (48 líneas), con los siete. Si no pasa la base, no corre nada; el que
   no pasa no corre.
2. **Fase 1, con los siete, prompt por prompt:** las 33 coreanas, las 33 legítimas reales y desarrollo
   ([`alcance-140`](../../casos/listas/alcance-140.txt)). Es lo que usa la regla. Corren en el orden de la tabla: si
   Colab se corta, los primeros quedan completos.
3. **La regla se aplica en Colab** (`analizar.para_fase_2`) y dice qué prompts siguen.
4. **Fase 2, solo con la base y con los prompts de los dos primeros candidatos que sirven:** la zona gris de Medicare
   (42) y la vista principal del test (100 estafas y 56 legítimas). Si no sirve ninguno, corre solo la base.

**No corre todo con todos a propósito.** Lo que decide son los reales y nuestras estafas de desarrollo; el test y la
zona gris son para medir el costo de lo elegido, y así no se los mira trece veces.

Las legítimas reales son obligatorias: hay que subir a Colab el ZIP de la custodia (`legitimas-reales-sets.zip`) o la
carpeta `sets/`. El script las busca solo en `/content`, descomprime el ZIP y arma una copia sin archivos de más; si
faltan, corta en los primeros segundos, antes de instalar nada.

**Duración:** alrededor de 2 h 40, estimado y sin medir. La fase 1 son unas 3.500 consultas por prompt (16 minutos) y
la fase 2, unas 2.900 (13 minutos), para tres prompts como mucho.

**Las llamadas largas se quedan sin contexto** (`num_ctx` 4096) entre las líneas 70 y 130: de ahí en más las líneas son
inválidas y no avisan. Pasa en 22 de las 33 coreanas, y en más de la mitad de sus líneas de OTRA. Lo midió un ensayo
sin modelo, con el Ollama falso de los tests sobre los conjuntos armados. Los prompts más cortos dejan más lugar.

## Regla, escrita antes de correr

**Referencia:** `base` con el primer aviso, corrida en esta misma sesión.

**Candidatos,** en este orden: `base` con confirmación; cada variante con el primer aviso, en el orden de la tabla;
cada variante con confirmación.

**Un candidato sirve** si, contra la referencia, cumple las cuatro:
1. en las coreanas, pierde a lo sumo una estafa avisada;
2. en las coreanas, pierde a lo sumo un aviso a tiempo;
3. en las 33 legítimas reales, baja 7 o más las FA. Es un tercio de las 21 de la evaluación final, y más del doble del
   ruido entre sesiones (hasta 3);
4. en desarrollo, conserva más de la mitad de los avisos a tiempo de la referencia. Es un piso contra un detector que
   no avisa nada: las coreanas no alcanzan para verlo, porque las avisan hasta las reglas de palabras clave.

**Si sirven varios,** se ordenan por el que menos pierde a tiempo en desarrollo. Si empatan, el de menos FA reales; si
empatan, el primero de la lista, que es el que cambia menos. El primero es el elegido. **Si no sirve ninguno,** queda la
configuración de la evaluación final.

**El test no elige.** Lo corren la base y los dos primeros, y se marca **costo alto** si el elegido pierde 8 o más a
tiempo (de 80) o 10 o más estafas avisadas (de 100) contra la referencia.

**La vara es `v4-corte`,** la referencia simple de la evaluación final, que no vuelve a correr: 33/33 coreanas (23/27 a
tiempo), 10/33 FA reales, y en el test 64/100, 50/80 a tiempo y 15/56 FA. Consulta en todas las líneas, de los dos
lados. Si lo elegido no es mejor que eso, se dice.

**Integrarlo o no lo decide Mateo,** con el costo a la vista (2026-11-20: «si cambia mucho los resultados lo integramos
igual avisando»). Lo que se integre va con un ADR que diga que se eligió después de la evaluación final, mirando los
conjuntos reales.

## Solo para mirar (no decide)

- qué valores escribe cada prompt, por tanda;
- cada prompt con «riesgo ≥ 0,5» y con «riesgo ≥ 0,7» como único corte: en los «p-» de tres y cuatro niveles, el
  segundo es avisar solo cuando el pedido ya se hizo;
- cuántas veces baja el riesgo de una consulta a la siguiente;
- las FA en las 75 legítimas de desarrollo que no deberían avisar;
- cuántas consultas con riesgo ≥ 0,3 tiene cada llamada;
- las líneas inválidas por contexto excedido;
- qué coreanas y qué legítimas reales cambian con el elegido.

## Después de correr

1. Descomprimir cada ZIP en un directorio vacío nuevo, **fuera del repositorio:** traen el texto del test, de las
   coreanas y de las legítimas reales. Correr todo Python con `-I`.
2. Verificar: los parciales coinciden con el final; el commit es el del tag, sin cambios sin commitear; el sha256 de
   `colab/probar_exploracion_reales.py` y el digest coinciden; `fase-2.json` dice lo mismo que el análisis.
3. Correr `python -I analizar.py --datos CARPETA` desde acá. [`aparte.py`](aparte.py) suma cuentas para leer el
   resultado y, con `--final`, compara la base con la pasada de la evaluación final. Se escribió después de correr y no
   toca la regla.
4. Acá va solo `analisis.md`, con cifras e identificadores. Las corridas del test van a `reserva/test`; las de las
   coreanas y las legítimas reales no se suben.

[`analizar.py`](analizar.py) está escrito antes de correr y aplica esta regla tal cual. La regla que vale es la de este
README, en el commit del tag.
