# Qué concluir de la evaluación final

> **Estado: propuesta sin discutir.** Pedida por Luciano el 2026-11-20 para ordenar qué decir en el documento y en la
> defensa. Junta tres fuentes y no agrega cifras nuevas salvo las del contexto (§7):
> - la [evaluación final](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md), que corrió
>   Mateo el 2026-11-19 (`c-consejos-corte-riesgo`, una sola vez);
> - la [comparación con las fichas de Luciano](../../experiments/slm-directo/analisis/2026-11-20-detector-vs-luciano/README.md)
>   de #145 (26 llamadas de desarrollo);
> - la [prueba de latencia en el Samsung A56](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md) (#172).

## En una oración

**El detector reconoce la forma de una estafa telefónica y avisa a tiempo en dos de cada tres estafas que nunca vio,
en un teléfono; pero esa misma forma la tiene una venta telefónica real, y por eso con llamadas reales avisa de más.**

## 1. Lo bueno

- **Generaliza.** En el test reservado (estafas que nunca se usaron para elegir nada) avisa a tiempo en **66 %**,
  contra 72 % en desarrollo. La diferencia está dentro del ruido: lo que se eligió no era sobreajuste.
- **Avisa antes del pedido en casi la mitad** (46 %): la persona se entera antes de que le pidan la clave, no después.
- **Avisa poco en las legítimas generadas:** 27 %, igual que el prompt anterior (`v4`), que avisaba mucho más tarde.
- **No se le escapa ninguna estafa real:** avisa las 33 coreanas, y a tiempo las 27 que tienen pedido.
- **Corre en un teléfono de gama media.** En el Samsung A56, sin internet, el primer aviso tarda 3,7 s de mediana.
- **El protocolo fue limpio,** y eso se defiende: el test se reservó desde el principio, la regla se escribió antes de
  correr, se corrió una sola vez y se fijó a un commit. No se tocó nada después de ver los resultados.
- **Cuando hay un pedido concreto, ve lo mismo que una persona atenta** (§3).

## 2. Qué estafas ve y por qué las ve

**Ve bien** (test, estafas avisadas por familia):

| familia | avisadas |
|---|---|
| Banco | **24/25** |
| Organismo previsional | 8/10 |
| Familiar en apuros | 12/15 |
| Premio | 9/15 |
| WhatsApp | 9/15 |
| Soporte técnico | **11/20** |

Por tipo de pedido, a tiempo: la clave 14/18, el código 15/25, datos personales 9/15, transferencia 7/10 y acceso
remoto 3/7.

**Por qué las ve.** El prompt le pregunta al modelo qué tan probable es que la llamada sea una estafa, con los consejos
oficiales como guía. El modelo aprendió a reconocer **la forma** de la estafa: alguien que llama sin que lo esperen, se
presenta como una institución (el banco, la ANSES, un soporte) y lleva la charla hacia un pedido. El banco es la familia
donde esa forma es más clara, y por eso casi no falla. En los motivos que escribe se ve: «los bancos rara vez llaman
así», «no se deben compartir códigos», «te piden una transferencia para cobrar un premio».

## 3. Contra las fichas de Luciano: dónde coincide

Luciano marcó en 26 llamadas de desarrollo la línea donde una persona atenta empezaría a sospechar. En las 21 estafas:

| | llamadas |
|---|---|
| Los dos en la misma línea (±2) | **6** |
| El detector antes que Luciano | 5 |
| El detector después | 4 |
| Solo sospecha Luciano | 3 |
| Solo avisa el detector | 3 |

**Coinciden cuando hay un pedido concreto, y por el mismo motivo:**

| llamada | qué pasa | Luciano | detector |
|---|---|---|---|
| 08 | soporte que pide instalar un programa | línea 5 | línea 7 |
| 16 | piden un código por WhatsApp | línea 7 | línea 9 |
| 17 | un organismo que pide reconstruir un legajo | línea 8 | línea 8 |
| 21 | hay que pagar para cobrar un premio | línea 11 | línea 13 |

Además, en tres estafas el detector avisa donde Luciano no veía nada raro (11, 12 y 19). En la 12 el aviso cae justo en
el pedido del CUIL y la fecha de nacimiento.

## 4. Dónde no coincide

**Cuando se adelanta, en general es por quién llama, no por lo que dice.** En cuatro de los cinco avisos tempranos el
motivo es genérico: «no se puede verificar la identidad», «los organismos rara vez llaman así». En las llamadas 14 y 39
avisa en la primera línea, apenas OTRA dice «de control de operaciones» o «de la mesa de regularización». En el corpus
generado eso acierta, porque un organismo que llama casi siempre es una estafa. **En la vida real no:** las empresas
llaman todo el tiempo (§6).

**Cuando llega tarde**, es por un escalón:

| llamada | qué pasa | Luciano | pedido | detector |
|---|---|---|---|---|
| 04 | familiar en apuros que pide plata | línea 5 | línea 22 | **línea 24** |
| 09 | grupo de WhatsApp que pide confirmar algo | línea 21 | línea 25 | **línea 26** |

En la 04 el modelo está en 0,2 («no sé») desde la línea 8 y sube a 0,3 recién después del pedido.

## 5. Por qué no ve algunas, y cuáles fallan

**Las 27 estafas del test que no avisa quedan a un escalón:** 26 tienen 0,2 como riesgo máximo. Con el umbral en 0,2
avisaría 99 de 100, pero también 45 de las 56 legítimas. No hay un umbral que arregle esto.

**El modelo no da una probabilidad: da tres estados.** 0,1 o menos es «limpio», 0,2 es «no sé» y 0,3 es «sospecho».
El aviso salta en el primer 0,3.

**Fallan sobre todo las estafas sin pedido:** avisa en 10 de 20 en el test, contra 10 de 10 en desarrollo. Son llamadas
que preparan el terreno y cortan antes de pedir. Ahí el modelo no tiene nada concreto que ver, y muchas veces una
persona tampoco: Luciano respondió «dudoso» o «no» en 16 de las 21 estafas de sus fichas.

**Los dos errores más graves**, para mostrar con honestidad:

| llamada | qué pide OTRA | riesgo del detector |
|---|---|---|
| 06 (soporte) | «la contraseña anterior» (líneas 14 y 16) | 0,2 de la línea 4 al final: **no avisa** |
| 15 (WhatsApp) | «leeme los seis dígitos» (línea 12); cuando la persona duda, «es una advertencia general» | 0,2 de la línea 8 al final: **no avisa** |

La política dice que un código o una clave no se le dictan nunca a quien llamó, y el detector se queda en «no sé»
toda la llamada. Una regla de palabras clave avisa en las dos.

## 6. Los avisos falsos: generadas contra reales

| conjunto | avisos en legítimas |
|---|---|
| Legítimas generadas del test (56) | **15, 27 %** [17–40] |
| Legítimas reales de un call center (33) | **21, 64 %** [47–78] |

**Por qué en las reales avisa más:**

- **En una llamada real el modelo está en «no sé» dos de cada tres consultas,** sea estafa o no. En las legítimas
  generadas está casi siempre en «limpio».
- **Cada turno de OTRA es otra chance de pasar a 0,3.** Por eso una llamada más larga avisa más: a las 10 consultas ya
  avisó en 20 de las 33 reales.
- **Una venta telefónica real tiene la forma del disfraz:** una empresa llama, ofrece algo y confirma datos. Los motivos
  de los 21 avisos se reparten en tres: unos 8 por un pedido de código o de datos de la cuenta, que un call center real
  hace para verificar al cliente y que los consejos oficiales dicen no dictar; unos 7 que leen la venta como estafa; y
  unos 6 genéricos.
- **Los datos generados eran demasiado prolijos:** legítimas cortas y claras, estafas que se notan. Medían bien la
  sensibilidad, pero sobreestimaban cuánto acierta con las legítimas.

**En las 33 legítimas reales se puede hacer una lectura más fina** con las fichas ciegas de la política de producto
(`experiments/slm-directo/preparar_revision_legitimas_reales.py`): las que piden un código o un PIN quizás no deberían
contar como falsa alarma. Esa cifra va **al lado** del 64 %, nunca en su lugar.

## 7. El contexto: por qué se queda ciego a los 10 minutos

**Qué pasa.** En cada turno de OTRA el detector le manda al modelo el prompt más toda la conversación hasta ahí. El
modelo corre con una ventana de **4096 tokens** (`num_ctx`). Cuando la conversación ya no entra, el detector no recorta
en silencio: marca la consulta como fallida y no avisa. Desde ese punto, **el detector no ve nada más**.

**Cuánto es en minutos.** El detector estima 3 caracteres por token y frena al 90 % de la ventana: unos 11.000
caracteres. El prompt usa unos 2.700, así que quedan unos 8.300 para la conversación. Las llamadas de la demo producen
**unos 815 caracteres por minuto** (mediana de 17 llamadas guardadas). **Da unos 10 minutos de conversación.** En
líneas, entre la 70 y la 130 según lo largas que sean. Ya pasó en la evaluación: 22 de las 33 coreanas se quedaron sin
contexto, y avisaron igual porque avisaron temprano.

**Por qué no tiene sentido que sea tan poco.** El modelo admite **131.072 tokens** (`ollama show`). 4096 es el **3 %**
de lo que soporta, y es un parámetro que elegimos nosotros, no un límite del modelo. Quedó así desde las primeras
pruebas, con el fundamento de «llamadas completas sin recorte silencioso»: alcanzaba para el corpus, que tiene llamadas
de 20 a 40 líneas. Nunca se midió con llamadas largas.

**Qué cuesta agrandarlo.** Más ventana pide más memoria para el caché del modelo y más tiempo por consulta cuando la
conversación es larga. En una notebook no es problema. En el A56 hay que medirlo: hoy procesa en unos 2 s por línea.
Con 16.384 tokens entrarían unos 50 minutos.

**Qué decir:**
- **Como límite declarado:** «la configuración evaluada cubre unos 10 minutos de conversación; el modelo admite mucho
  más, y ampliarlo es un parámetro, no un cambio del detector».
- **Para una prueba de estrés de 30 minutos:** correrla con `num_ctx` más grande y declararlo. Medir la demora, la
  memoria y la temperatura del teléfono, y si avisa en una estafa cuyo pedido llega en el minuto 20. Mientras la conversación
  entra, cambiar `num_ctx` no debería cambiar lo que responde el modelo; conviene comprobarlo antes con la prueba de
  humo de formato (los 3 casos de siempre).
- **Para la demo en vivo:** llamadas de 3 a 5 minutos.

## 8. Conclusiones

1. **Un modelo de lenguaje chico, que corre en un teléfono sin internet, puede avisar a tiempo de una estafa
   telefónica:** dos de cada tres estafas que nunca vio, casi la mitad antes del pedido, en 4 segundos en un A56.
2. **Funciona porque reconoce la forma de la estafa,** no palabras sueltas. Cuando hay un pedido concreto coincide con
   una persona atenta. Contra una regla de palabras clave, no detecta más: lo que aporta es avisar mucho menos en las
   legítimas (27 % contra 86 %).
3. **Esa misma razón es su límite.** Una venta real tiene la forma del disfraz, y por eso avisa en 2 de cada 3
   llamadas reales de call center. Y si no hay pedido, o el pedido llega sin la forma típica, puede no avisar.
4. **Los datos generados sobreestiman cuánto acierta con las legítimas.** Es el hallazgo metodológico más fuerte: un
   corpus sintético prolijo sirve para medir la sensibilidad, no la tasa de avisos falsos. Sin las 33 llamadas reales,
   la tesis habría informado 27 % y nadie lo habría notado.
5. **Para llevarlo a producción falta:** un corpus real argentino de llamadas legítimas, probarlo con voz y
   reconocimiento real (#54), y una ventana de contexto acorde a llamadas largas.

**Lo que no hay que decir:** que el 33/33 de las coreanas prueba que detecta (las reglas también dan 33/33), que el
detector «entiende» la estafa, o una sola cifra de avisos falsos promediando generadas y reales.

## Límites

- **Una sola corrida.** Entre sesiones, la misma configuración cambia hasta 3 casos en una cifra.
- **Los conjuntos reales son chicos y no son argentinos:** 33 y 33, traducidos, con roles inferidos por un modelo.
- **Las 26 fichas de Luciano no son una muestra al azar,** son de un solo revisor y seis no son ciegas.
- **Todo es texto limpio:** no se midió con reconocimiento de voz.
