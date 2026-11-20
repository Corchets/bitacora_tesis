# #52, evaluación final: análisis

> **Estado: propuesta sin discutir.** Mateo la corrió en Colab T4 el 2026-11-19, una sola vez, con el tag
> `colab/143-evaluacion-final-2` (`87bb745`) y la configuración `c-consejos-corte-riesgo`. Se analizó el 2026-11-20.
> No hay criterios de aprobación (Mateo, 2026-11-18): se informan cifras con intervalo. Las cifras salen de
> [`analizar.py`](analizar.py), escrito antes de correr ([salida completa](analisis-salida.md)). La lectura es posterior.
> **No se leyó ningún texto del test ni de #144.** De las legítimas reales se leyeron solo los motivos que escribió el
> modelo en sus avisos.

**En una oración:** el detector avisa a tiempo en dos de cada tres estafas generadas que nunca vio y en todas las
estafas reales coreanas, pero también avisa en una de cada cuatro llamadas legítimas generadas y en dos de cada tres
llamadas reales de call center. **La sensibilidad se sostiene; la especificidad en llamadas reales, no.**

## Verificación de los ZIP

- Cada ZIP se descomprimió en un directorio vacío nuevo. Los diez parciales que bajaron coinciden archivo por archivo
  con el final. No bajaron los tres parciales de `legitimas_reales`; esas corridas están solo en el ZIP final.
- `commit.txt`, los `TERMINADA.txt` y los doce manifiestos dan `87bb745`, el commit del tag, sin cambios sin commitear.
  La reserva es `reserva/test` en `9089b19`.
- El sha256 de `colab/probar_evaluacion_final.py` en el tag coincide con `script-sha256.txt` (`14c2f943…`), y el digest
  del modelo, con `digest.txt` (`b37049369adf…`). Ollama 0.40.14 en una Tesla T4.
- Humo de formato: 48/48 en la configuración y en `v4-corte`. Las doce corridas pasan el control.
- **Control de reproducibilidad en desarrollo: pasa.** 40 estafas, 16 antes del pedido, 26 a tiempo y 20 FA, contra
  los rangos 40–42, 16–19, 26–28 y 18–22.
- Líneas inválidas de la configuración: ninguna, salvo 19 por contexto excedido en una sola llamada de la zona gris
  (104 líneas).

## Cifras de la configuración

Vista principal de cada conjunto, con Wilson al 95 %.

| conjunto | estafas avisadas | antes del pedido | a tiempo | FA |
|---|---|---|---|---|
| **Test reservado** (100 estafas y 56 legítimas generadas) | 73/100, 73 % [64–81] | 37/80, 46 % [36–57] | **53/80, 66 % [55–76]** | **15/56, 27 % [17–40]** |
| **Set externo de #144** (33 estafas reales coreanas) | 33/33, 100 % [90–100] | 25/27, 93 % [77–98] | 27/27, 100 % [88–100] | — |
| **Legítimas reales** (33 de telecomunicaciones, CallCenterEN) | — | — | — | **21/33, 64 % [47–78]** |
| Desarrollo (46 estafas y 94 legítimas) | 40/46, 87 % [74–94] | 16/36, 44 % [30–60] | 26/36, 72 % [56–84] | 20/94, 21 % [14–31] |

Contra las referencias, en los mismos casos:

| conjunto | cifra | `c-consejos` | `v4-corte` | reglas v1 |
|---|---|---|---|---|
| Test | estafas avisadas | 73/100 | 64/100 (p = 0,08) | 87/100 (p = 0,009) |
| Test | antes del pedido | 37/80 | 15/80 (p < 0,001) | 55/80 (p = 0,003) |
| Test | a tiempo | 53/80 | 50/80 (p = 0,66) | 72/80 (p < 0,001) |
| Test | FA | 15/56 | 15/56 (p = 1) | 48/56 (p < 0,001) |
| Externo | a tiempo | 27/27 | 23/27 (p = 0,13) | 25/27 (p = 0,50) |
| Legítimas reales | FA | 21/33 | 10/33 (p = 0,003) | 30/33 (p = 0,02) |

La latencia no cambia: 210 ms de mediana por consulta en T4 (p95 266 ms).

## Cuánto vale cada conjunto

| conjunto | qué es | límite | cómo se usa |
|---|---|---|---|
| Test, 100 estafas `CV2-T-V` | Generadas, entrantes, nunca usadas para elegir nada | Salen del mismo generador que desarrollo: miden generalización dentro de ese estilo, no estafas reales | **Cifra principal de detección** |
| Test, 56 legítimas `ENT-T` | Generadas para el alcance (entrantes de no agendados) | Sin corrección a ciegas. Son prolijas y cortas | **Cifra principal de FA en generadas** |
| Externo, 33 coreanas | Estafas reales | Traducidas, de otro país, muy largas (mediana 113 líneas). Todos los detectores dan 33/33, también las reglas | Control de sensibilidad. **Sola, no discrimina** |
| Legítimas reales, 33 | Llamadas reales salientes de call center | De EE. UU., traducidas; los roles y el tipo los infirió un modelo sobre un ASR sin hablantes | **La única evidencia de FA en llamadas reales** |
| Zona gris de Medicare, 42 | Ventas reales de seguros y equipamiento médico | No son FA ni estafas | Solo descriptiva: 32/42 avisos |
| Test, 100 legítimas viejas `CV2-T-L` | Las legítimas del corpus v2 | 74 están fuera del alcance (no son entrantes de no agendados). Las 26 de adentro son del estilo viejo | **No se informan como FA** (2/26 y 12/74) |
| Desarrollo, los 104 de «aparte» | Laboratorio, piloto, trampas y corpus v2 fuera de alcance | No aplican a la arquitectura de hoy | No se informan |

## Lectura

### 1. En las estafas generadas, la detección útil se sostiene

- **A tiempo: 66 % en test contra 72 % en desarrollo** (p = 0,67). Antes del pedido, 46 % contra 44 %. Lo que se eligió
  en desarrollo no era sobreajuste en la cifra que importa.
- **Lo que baja son las estafas avisadas en total: 73 % contra 87 %** (p = 0,09). Casi toda la baja está en las estafas
  sin pedido: 10/20 en test contra 10/10 en desarrollo (p = 0,01). Con pedido, 63/80 contra 30/36.
- Por familia, en test: banco 24/25, previsional 8/10, familiar 12/15, premio 9/15, WhatsApp 9/15 y soporte 11/20.
  **Banco casi no falla; soporte, WhatsApp y premio fallan cerca de la mitad.** En desarrollo también banco era la
  mejor y soporte la peor.
- Por pedido, a tiempo: clave 14/18, código 15/25, datos personales 9/15, transferencia 7/10, acceso remoto 3/7.
- **Las 27 que no avisa quedan a un escalón:** 26 tienen 0,2 como riesgo máximo. Con «≥ 0,2» avisaría 99/100, pero
  también 45/56 legítimas.

### 2. En las legítimas generadas, las FA son las de desarrollo

- **27 % en test contra 21 % en desarrollo** (p = 0,55). Cotidianas: 0/14.
- **Un tercio de las FA son «el banco»:** 5/7. Sin esa familia quedan 10/49 (20 %); en desarrollo, 10/81. Es la misma
  categoría que la revisión de producto dejó como tolerable, pero las 56 de test no tienen etiquetas de producto.
- Con 5 llamadas legítimas de desconocidos por semana, son unas 6 FA por mes [4–9].

### 3. Las coreanas dan 33/33, y eso solo dice que no se le escapan

- Avisa las 33, y las 27 con pedido a tiempo, con mucho margen: el aviso cae en la línea 6 de mediana y el pedido llega
  mucho después.
- **`v4-corte` y las reglas v1 también avisan las 33.** Un detector que avisara siempre daría lo mismo. El set no
  tiene legítimas del mismo origen, así que no mide si separa.
- Son llamadas largas: la mediana es de 113 líneas y la más larga tiene 603. El pedido llega en la línea 57 de
  mediana, así que para llegar a tiempo alcanza con avisar temprano, por el motivo que sea.

### 4. En las llamadas reales de call center avisa en dos de cada tres

- **21/33 (64 %), contra 27 % en las legítimas generadas** (p < 0,001). En las que se anotaron como cotidianas, 9/19
  contra 1/43 en las generadas.
- **Los motivos se reparten en tres grupos parecidos** (son 21):
  - unos 8 dicen que le piden un código, una clave o datos de la cuenta. Un call center real verifica al cliente así,
    y es justo lo que los consejos oficiales dicen que no hay que dictar. Con la política de la revisión de producto,
    varias serían tolerables;
  - unos 7 leen la venta como estafa: una promoción que no pidió, un precio que cambia, apuro para cerrar;
  - unos 6 son genéricos: le piden un correo, «conviene verificar la identidad», mencionan que la llamada se graba.
- **`v4-corte` avisa la mitad: 10/33** (p = 0,003). El prompt C avisa por hacia dónde va la llamada, y una venta
  telefónica real tiene la misma forma que el disfraz: una empresa que llama, ofrece algo y confirma datos.
- En la zona gris avisa 32/42. Las 10 que no avisa incluyen la que se quedó sin contexto.

### 5. Con datos reales separa poco

Juntando los dos conjuntos reales: **33/33 estafas contra 21/33 legítimas.** La diferencia existe (p < 0,001), pero es
mucho menor que en los generados.

| grupo | consultas hasta cortar | avisos por consulta | consultas que dan 0,2 |
|---|---|---|---|
| Test, estafas | 571 | 12,8 % | 56 % |
| Test, legítimas | 579 | 2,6 % | 37 % |
| Coreanas | 205 | 16,1 % | 74 % |
| Legítimas reales | 254 | 8,3 % | 65 % |
| Zona gris | 545 | 5,9 % | 71 % |

- **En los generados, una estafa tiene 5 veces más chance de aviso por consulta que una legítima. En los reales, 2
  veces.**
- **El modelo está tranquilo solo con las legítimas generadas.** Ahí da 0,1 o menos en el 60 % de las consultas. En
  una llamada real, sea estafa o no, da 0,2 en dos de cada tres: queda a un escalón del aviso desde el principio.
- Como cada turno de OTRA es otra oportunidad de escribir 0,3, **una llamada más larga avisa más.** A las 10 consultas
  ya avisó 20 de las 33 legítimas reales y 30 de las 33 coreanas; a las 3 consultas, 6 y 13.

### 6. Contra las referencias

- **El SLM no detecta más que una regla de palabras clave.** Las reglas v1 avisan más estafas y más a tiempo (90 %
  contra 66 %). Lo que aporta el modelo es no avisar en todo: 27 % de FA contra 86 % en test, y 64 % contra 91 % en
  las reales.
- **Contra `v4-corte`, C gana en anticipación y pierde en llamadas reales.** En test avisa antes del pedido en 37
  contra 15, con las mismas FA (15 y 15) y casi lo mismo a tiempo (53 y 50). En las legítimas reales avisa el doble.
  La ventaja en FA que C tenía en desarrollo (20 contra 42) no aparece en test.

## Límites de esta lectura

- **Los conjuntos reales son chicos y no son argentinos.** 33 y 33, traducidos, con roles inferidos por un modelo en
  las legítimas. Los intervalos son anchos: la FA real está entre 47 % y 78 %.
- **Las legítimas reales no tienen etiquetas de producto.** Parte de sus avisos son pedidos de código o de datos de la
  cuenta. Cuántas serían FA estrictas no se sabe sin que alguien las etiquete a ciegas.
- **No se sabe por qué avisa en las coreanas ni por qué falla en las 27 de test:** no se leyeron.
- **Es una sola corrida.** Entre sesiones, la misma configuración cambia hasta 3 casos en una cifra de desarrollo.

  > **Nota del 2026-11-20:** la [exploración con los conjuntos reales](../2026-11-20_exploracion-reales/analisis.md#5-la-misma-configuración-corrida-otra-vez-mueve-hasta-6-casos)
  > volvió a correr esta configuración en el test: 76/100 estafas avisadas, 43/80 antes del pedido, 56/80 a tiempo y
  > 15/56 FA. Las cifras que valen son las de arriba; la diferencia es el margen entre pasadas
  > ([H13](../../../../docs/hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)).
- Todo supone texto limpio y turnos perfectos: no se midió con ASR (#54).

## Qué queda

> **Estado: propuesta sin discutir.**

- **No tocar la configuración ni volver a correr.** La evaluación final ya corrió; lo que se cambie ahora es
  exploración y se informa así.
- **Informar dos cifras de FA, no una:** 27 % en generadas y 64 % en reales, una al lado de la otra. No promediarlas
  ni sumar las legítimas viejas.
- **Informar las coreanas junto con las legítimas reales,** como el par de datos reales: 33/33 contra 21/33.
- Los CSV del test van a `reserva/test`. Lo del set externo y las legítimas reales no se sube.

> **Nota del 2026-11-20:** Mateo pidió una última exploración sobre los conjuntos reales. Ningún candidato pasó la
> regla y la configuración no cambió. Ver su [análisis](../2026-11-20_exploracion-reales/analisis.md) y
> [H12](../../../../docs/hallazgos/H12-cambiar-el-prompt-mueve-el-corte-no-la-separacion.md).
