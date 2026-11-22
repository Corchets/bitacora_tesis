# #52, mejoras de Luciano: análisis

> **Estado: propuesta sin discutir.** Corrida en Colab T4 (Colab Pro) el 2026-11-20, una sola vez, con el tag
> `colab/52-mejoras-luciano` (`5ef3da6`). Duró 2 h. Es exploración posterior a la evaluación final: no la reemplaza.
> La regla y [`analizar.py`](analizar.py) son anteriores a la corrida ([README](README.md)); la salida está en
> [`salida-final.md`](salida-final.md), transcrita de la terminal de Colab. El 2026-11-21 llegaron 10 de los ZIP parciales
> (la base en los cinco conjuntos y `p-niveles` en tres): reanalizados en la Mac, dan las mismas cifras de la base
> ([`salida-local.md`](salida-local.md)), y de ahí sale la sección «Con los datos crudos».

**En una oración:** de las cuatro mejoras, **dos funcionan**. La regla de pedido crítico sube los avisos a tiempo del
test de 53 a 64 sin sumar avisos falsos, y el nivel «cortá» deja la alarma fuerte en solo 5 de las 33 llamadas reales
de call center. **Las otras dos no sirven:** los prompts que preguntan por el pedido pierden estafas reales, y la
confirmación cuesta más de lo que ahorra.

## Verificación

- Digest `b37049369adf…`, Ollama 0.40.14, T4. Humo de formato: 48/48 con los tres prompts.
- Las 15 corridas dan «bien» en el control, con `num_ctx` 16384.
- **Ninguna consulta inválida.** Las coreanas se leyeron enteras: 0 de 4.193, contra más de 2.000 inválidas por
  contexto excedido en la exploración de Mateo, con 4096.
- **La base reproduce la evaluación final** dentro del ruido: test 75 · 53 · 16 contra 73 · 53 · 15; legítimas
  reales 21 contra 21; coreanas 33/33 y 27/27 en las dos; desarrollo 42 · 28 · 21 contra 40 · 26 · 20.

## Qué se probó y cómo salió

La referencia es la base con el primer aviso, en esta misma sesión.

| mejora | qué cambió | resultado | veredicto |
|---|---|---|---|
| **1. Regla de pedido crítico** | El aviso es el primero entre el modelo y la regla | Test a tiempo **53 → 64**, avisos falsos iguales (16/56 y 21/33) | **Sirve** |
| **2. Prompt por el pedido** (`p-niveles`, `p-lista`) | Otra pregunta al modelo | `p-niveles`: menos avisos reales (13), pero test a tiempo 29. `p-lista`: test a tiempo 70, pero pierde 5 coreanas a tiempo y avisa en 36/94 de desarrollo | No sirve |
| **3. Aviso en dos niveles** | «Cortá» = regla o riesgo ≥ 0,5 | Alarma fuerte en **5/33** reales y **4/56** del test; a tiempo en 20/27 coreanas | **Sirve** (como segundo nivel) |
| **4. Confirmación** | Dos 0,3, o un 0,5 | Avisos reales 21 → 17, pero test a tiempo 53 → 42 | No sirve |

### 1. La regla: la mejora es real

| corrida | modelo solo | modelo + regla | avisos falsos |
|---|---|---|---|
| Evaluación final (2026-11-19), sin correr de nuevo | 53/80 | 63/80 | sin cambio |
| Exploración de Mateo (2026-11-20), sin correr de nuevo | 56/80 | 65/80 | sin cambio |
| **Esta corrida** | **53/80** | **64/80** | **sin cambio** |

- **Tres corridas distintas del modelo, la misma mejora:** entre 9 y 11 avisos a tiempo más en el test. No es ruido.
- **La regla sola nunca se equivocó:** cero avisos en las 183 legítimas de las tres fuentes y en las 42 de la zona
  gris.
- **Ojo:** la regla se ajustó mirando estos casos. La parte del modelo es nueva en cada corrida; la de la regla, no.
  Por eso la cifra va como exploración. Con llamadas nuevas, la regla va a tener algún aviso falso.

### 3. Dos niveles: la alarma fuerte casi no molesta

| nivel | cuándo salta | coreanas a tiempo | test a tiempo | avisos en legítimas reales | en legítimas del test |
|---|---|---|---|---|---|
| **Atención** (base + regla) | riesgo ≥ 0,3 o regla | 27/27 | 64/80 | 21/33 | 16/56 |
| **Cortá** | riesgo ≥ 0,5 o regla | 20/27 | 39/80 | **5/33** | **4/56** |

- **En una llamada real de call center, la alarma fuerte salta en 5 de 33.** Las otras 16 que hoy avisan recibirían
  solo el aviso discreto.
- **En la zona gris de Medicare** (probablemente fraudes) el «cortá» salta en 12 de 42.
- **El costo:** el «cortá» llega a tiempo en 39 de las 80 estafas del test. El resto lo cubre el «atención».
- Es un cambio de producto: el modelo es el mismo, cambia cómo se muestra el aviso.

### 2. Los prompts por el pedido mueven el corte, no separan mejor

- **`p-niveles`** baja los avisos reales a 13, pero se pierde la mitad de las estafas del test (29 a tiempo), y en las
  legítimas del test avisa **más** (19 contra 16). La regla le devuelve algunas (42), pero no alcanza.
- **`p-lista` es lo más llamativo de la corrida:** 70 de 80 a tiempo en el test, con 15 avisos falsos. Pero pierde 2
  coreanas y 5 a tiempo, avisa en 17 de 33 reales y en 36 de 94 legítimas de desarrollo. Le va bien con las estafas
  generadas y mal con las reales. Coincide con la exploración de Mateo.
- En los dos, la confirmación no cambia nada: no escriben valores entre 0,3 y 0,5.

### 4. La confirmación cuesta más de lo que ahorra

Baja 4 avisos reales (21 → 17) y 7 de desarrollo, pero pierde 11 avisos a tiempo en el test. Con la regla el test
queda en 56 a tiempo, apenas 3 más que la referencia, y los avisos reales siguen bajando solo 4: no alcanza para
ninguno de los dos lados. Es lo mismo que encontró Mateo.

## Con los datos crudos

Sale de los ZIP parciales de la base, reanalizados en la Mac el 2026-11-21 (`profundo.py`, en esta carpeta).

**1. En los datos reales, el 0,5 separa muy bien.** Riesgos que escribe la base en las consultas de OTRA:

| conjunto | 0,2 o menos | 0,3 | 0,5 o más |
|---|---|---|---|
| Coreanas (estafas reales) | 25 % | 15 % | **58 %** |
| Legítimas reales | 73 % | 23 % | **4 %** |
| Zona gris de Medicare | 64 % | 27 % | 9 % |
| Test, estafas generadas | 55 % | 31 % | 13 % |
| Test, legítimas generadas | 87 % | 11 % | 1 % |

- **El modelo está muy seguro con las estafas reales:** en más de la mitad de las consultas de las coreanas escribe
  0,5 o más (28 % un 0,8). En las legítimas reales, casi nunca.
- **Las estafas generadas son más sutiles que las reales:** solo el 13 % de sus consultas llega a 0,5. Por eso el
  umbral de 0,3 lo piden nuestras estafas generadas, no las reales (lo mismo vio Mateo).
- **Por eso funciona el «cortá»:** en datos reales, 0,5 es casi un clasificador limpio.

**2. Cómo escala el aviso en dos niveles.** En una estafa, primero salta «atención» y, si la llamada sigue hacia el
pedido, «cortá»:

| conjunto | atención | cortá alguna vez | cortá antes de que la persona cumpla | líneas entre los dos (mediana) |
|---|---|---|---|---|
| Coreanas | 33/33 | 29/33 | 13/16 | 6 |
| Desarrollo | 43/46 | 24/46 | 10/15 | 3 |
| Test | 82/100 | 50/100 | 21/32 | 1 |

De las 7 coreanas con pedido donde «cortá» no llega a tiempo, 4 llegan después a 0,6 o 0,7 y 3 nunca pasan de 0,4.

**3. La ventana de 16.384 no cambia lo que responde el modelo.** En las consultas que están en esta corrida y en la
evaluación final (con 4096), el riesgo es el mismo en el 93,4 % (925, desarrollo) y el 93,3 % (1.150, test). Es lo
mismo que cambia entre dos corridas con la misma ventana (92 % en la exploración de Mateo).

**4. La ventana tampoco cambia la demora en la T4:** 206 a 255 ms de mediana por consulta (210 ms en la evaluación
final). Las coreanas, que son las llamadas largas, dan 255 ms de mediana y 379 ms de p95.

## Qué queda

> **Estado: propuesta sin discutir.**

- **Para la tesis**, como exploración posterior a la evaluación final:
  - «Una regla de pedidos críticos sumada al modelo sube los avisos a tiempo del 66 % al 80 % en el test, sin avisos
    falsos nuevos, en tres corridas distintas.» Aclarar que se ajustó con el test a la vista.
  - «Con un aviso en dos niveles, la alarma fuerte salta en 5 de 33 llamadas reales de call center (15 %), contra 21
    de 33 (64 %) del aviso único.»
  - Los prompts por el pedido y la confirmación, probados dos veces (Mateo y esta corrida), no mejoran.
- **Para la demo:** base + regla como aviso discreto y «cortá» como alarma fuerte. Antes, probar la regla con
  transcripciones del ASR, que pueden venir sin acentos.
- **Los datos crudos:** el ZIP final y los parciales de `p-lista` quedaron solo en la sesión de Colab. Los 10
  parciales que llegaron están en `~/Downloads` de la Mac de Luciano. Los del test traen sus textos, así que van a
  `reserva/test`, no a una rama de laboratorio.
