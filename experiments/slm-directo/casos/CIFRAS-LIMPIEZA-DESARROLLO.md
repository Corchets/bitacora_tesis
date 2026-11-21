# Cifras de la etapa 2 de #143, con y sin limpieza del corpus de desarrollo

Fecha: 2026-11-09. Lo preparó un agente a pedido de Mateo Antenucci.

> **Estado: propuesta sin discutir. Exploración:** no decide nada (ADR 0005). Las corridas son las de la etapa 2 de
> [#143](https://github.com/Corchets/bitacora_tesis/issues/143), que todavía no están commiteadas
> (`corridas/2026-11-07_alcance-etapa-2/` del checkout compartido). Se leyeron sin modificarlas. Los
> [escenarios](ESCENARIOS-LEGITIMAS-DESARROLLO.md) salen del método de #45 y las [dudosas](LEGITIMAS-DUDOSAS.md)
> esperan la discusión del equipo: si cambian, cambian las cifras.

## Reglas, escritas antes de mirar las corridas

Escritas el 2026-11-09, después de armar los escenarios, el criterio de dudosas y la pregunta de #145 sobre las
estafas sin pedido, y antes de abrir `actualizaciones.csv` de ninguna corrida. La regla de aviso es la de `analizar.py` de la etapa 2: la primera línea
válida en que el modelo escribe `alerta` o un riesgo mayor o igual al umbral.

**Configuraciones** (las de la propuesta, §1):
- **v4:** `v4-corte`, «riesgo ≥ 0,4 o alerta», su regla adoptada (ADR 0006).
- **C:** `c-json-corte`, «riesgo ≥ 0,3 o alerta», la regla adoptada provisoriamente en la etapa 2.
- **C, repetición:** `c-json-corte-rep`, con la misma regla.

**Legítimas, cinco vistas:**

| Vista | Qué cuenta | Denominador |
|---|---|---|
| L0. Por llamada | Llamadas con FA. Tiene que repetir las cifras de la etapa 2. | 94 |
| L1. Por escenario | Escenarios con al menos una llamada con FA. | 47 |
| L1p. Por escenario, ponderada | Promedio, sobre los escenarios, de la parte de sus llamadas con FA: cada escenario pesa 1. | 47 |
| L2. Sin dudosas | Como L0, sin las llamadas marcadas «dudosa» por los dos anotadores. Las «a revisar» quedan. | 94 − dudosas |
| L3. Por escenario y sin dudosas | Como L1, después de sacar las dudosas. Un escenario cuyas llamadas son todas dudosas desaparece. | escenarios que quedan |

Como sensibilidad, una línea cada una: L2 sacando también las «a revisar», y L2 con la variante estricta de S4.
Además se informa **cuántas de las dudosas tuvieron FA** con cada configuración: es la pregunta de fondo, si la
ventaja de C en FA viene de legítimas poco realistas.

**Estafas:**
- avisadas sobre las 46 y sobre las 36 con pedido;
- avisos antes del pedido (`T_A < T_R`) sobre las 36;
- avisadas entre las 10 sin pedido.
- **Sin las incoherentes** (letra `c` de la [pregunta 5 de #145](../../../docs/corpus/PREGUNTA-145-ESTAFAS-SIN-PEDIDO.md)):
  queda pendiente hasta que respondan los revisores. Acá no se calcula, porque exigiría juzgar esas llamadas.

**Comparación:** la diferencia entre C y v4 en cada vista. Para las estafas vale el margen de 3 casos del ADR 0005; en
FA se informa la diferencia, sin umbral.

## Resultado

<!-- cifras:inicio -->
Corridas: **v4** `v4-corte`, riesgo ≥ 0,4 o alerta; **C** `c-json-corte`, riesgo ≥ 0,3 o alerta; **C rep.** `c-json-corte-rep`, riesgo ≥ 0,3 o alerta.

**Falsas alarmas en las legítimas**

| Vista | v4 | C | C rep. | C − v4 |
|---|---:|---:|---:|---:|
| L0. Por llamada | 42/94 | 27/94 | 26/94 | -15 |
| L1. Por escenario (al menos una FA) | 25/47 | 18/47 | 18/47 | -7 |
| L1p. Por escenario, ponderada | 21,50/47 | 15,17/47 | 14,83/47 | -6,33 |
| L2. Sin dudosas | 35/87 | 20/87 | 19/87 | -15 |
| L3. Por escenario y sin dudosas | 23/45 | 16/45 | 16/45 | -7 |
| Sensibilidad: sin dudosas ni «a revisar» | 35/87 | 20/87 | 19/87 | -15 |
| Sensibilidad: sin dudosas, S4 estricta | 29/81 | 17/81 | 16/81 | -12 |
| Sensibilidad agregada después de mirar: por escenario del control a ciegas | 29/62 | 24/62 | 23/62 | -5 |

En L1p la cifra es la suma, sobre los escenarios, de la parte de sus llamadas con FA: son «escenarios con FA» contando fracciones.

**Las legítimas que salen de la cifra**

| | v4 | C | C rep. |
|---|---:|---:|---:|
| Dudosas con FA | 7/7 | 7/7 | 7/7 |
| «A revisar» con FA | 0/0 | 0/0 | 0/0 |

**Estafas**

| Vista | v4 | C | C rep. | C − v4 |
|---|---:|---:|---:|---:|
| Estafas avisadas, todas | 28/46 | 36/46 | 36/46 | +8 |
| Estafas avisadas, con pedido | 27/36 | 27/36 | 27/36 | +0 |
| Avisos antes del pedido | 10/36 | 17/36 | 16/36 | +7 |
| Estafas avisadas, sin pedido | 1/10 | 9/10 | 9/10 | +8 |

**Dudosas, una por una**

| Caso | Escenario | Señales (anotador 1 / 2) | FA v4 | FA C | FA C rep. |
|---|---|---|---|---|---|
| `ENT-L-BANCO-001` | E01 | S4 / S4 | sí | sí | sí |
| `ENT-L-BANCO-002` | E02 | S2, S4 / S2, S4 | sí | sí | sí |
| `ENT-L-BANCO-005` | E16 | S4 / S4 | sí | sí | sí |
| `ENT-L-SOPORTE-005` | E42 | S1 / S1 | sí | sí | sí |
| `LEG2-BA-01` | E01 | S4 / S4 | sí | sí | sí |
| `LEG2-BA-02` | E02 | S4 / S4 | sí | sí | sí |
| `LEG2-BA-05` | E16 | S4 / S4 | sí | sí | sí |
<!-- cifras:fin -->

## Lectura

> **Exploración.** Las reglas de arriba se escribieron antes de mirar; esta lectura, después. No decide nada.

- **L0 repite la etapa 2** (42/94 y 27/94; 28/46 y 36/46): la regla de aviso es la misma de `analizar.py`.
- **Las 7 dudosas tienen FA con las tres configuraciones.** Sacarlas baja 7 FA a v4 y 7 a C: la diferencia queda en
  −15. **La ventaja de C en FA no sale de las legítimas que el criterio marca como dudosas.** Esas siete son FA
  que ningún prompt evita, y con razón: son las llamadas que más se parecen a una estafa.
- **Por escenario, la ventaja se mantiene en proporción.** Por llamada, v4 tiene FA en el 45 % de las legítimas y C
  en el 29 %; por escenario, en el 53 % y el 38 % (L1). En números absolutos la diferencia se reduce a la mitad
  (−15 de 94 a −7 de 47) porque hay la mitad de unidades, no porque C gane en guiones repetidos.
- **Con la división del control a ciegas, la ventaja se achica más.** El control separa en otro escenario las
  reescrituras que agregan un pedido de datos (62 escenarios). Así, v4 tiene FA en el 47 % y C en el 39 %: −5 de 62.
  Es coherente con la propuesta, donde C tiene más FA que v4 en las legítimas que no piden datos (6 contra 3). Esta
  vista **se agregó después de ver las cifras**: no estaba en las reglas y no puede decidir nada.
- **Con la variante estricta, la ventaja se achica un poco:** las 6 llamadas que suma tienen 6 FA con v4 y 3 con C.
  Queda en −12 de 81.
- **Lo que sigue abierto es lo que el criterio no cubre.** La propuesta mostraba que la ventaja de C sale de las 64
  legítimas que piden datos personales. Las que piden datos y no son de un banco ni de un organismo no tienen fuente
  sobre lo que es normal; si son creíbles es la pregunta humana de #145.
- **Estafas:** con pedido, v4 y C avisan las mismas 27 de 36. Las +8 de C son todas de las 10 sin pedido (1 contra 9).
  En avisos antes del pedido, C gana por 7 (6 en la repetición). Por eso importa la pregunta 5 de #145: si alguna de
  las 10 es incoherente (`c`), sale de la cifra principal y se lleva una de esas +8.

