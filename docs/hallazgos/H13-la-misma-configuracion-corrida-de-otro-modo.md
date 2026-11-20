# H13 — La misma configuración, corrida en otro orden, cambia el riesgo en el 8 % de las consultas y hasta 6 casos de una cifra

- **Fecha:** 2026-11-20
- **Tipo:** método
- **Estado:** vigente
- **Evidencia:** [exploración con los conjuntos reales, lectura 5](../../experiments/slm-directo/corridas/2026-11-20_exploracion-reales/analisis.md#5-la-misma-configuración-corrida-otra-vez-mueve-hasta-6-casos)
  y sus [cuentas aparte](../../experiments/slm-directo/corridas/2026-11-20_exploracion-reales/aparte-salida.md).
- **Afecta a:** cómo se informan las cifras de la evaluación final de
  [#52](https://github.com/Corchets/bitacora_tesis/issues/52) en el
  [capítulo 8](../tesis/CAP-08-RESULTADOS-EXPERIMENTALES.md); la tolerancia del
  [ADR 0005](../ingenieria/adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md); [H02](H02-ruido-entre-corridas.md) y
  [H11](H11-el-riesgo-cambia-con-el-runtime.md), que complementa.

## Qué encontramos

`c-consejos-corte-riesgo` corrió dos veces en Colab T4: en la evaluación final (2026-11-19) y como base de la
exploración (2026-11-20). Mismo modelo, digest, semilla, `num_ctx`, Ollama 0.40.14, driver y conjuntos. Cambió cómo se
corrió: la primera pasó cada conjunto entero y cortó cada llamada en su primer aviso; la segunda pasó solo la vista
principal y todas las líneas.

- **En las 3.060 consultas que están en las dos pasadas, el riesgo es el mismo en el 92 %.** De los 238 cambios, 228
  son de 0,1 o menos.
- **Alcanzan para mover llamadas,** porque el modelo escribe 0,2 o 0,3 en más de la mitad de las consultas y el umbral
  es 0,3:

  | conjunto | cifra | evaluación final | segunda pasada |
  |---|---|---|---|
  | Test | estafas avisadas | 73/100 | 76/100 |
  | Test | antes del pedido | 37/80 | 43/80 |
  | Test | a tiempo | 53/80 | 56/80 |
  | Test | FA | 15/56 | 15/56 |
  | Legítimas reales | FA | 21/33 | 23/33 |
  | Zona gris | avisos | 32/42 | 30/42 |
  | Desarrollo | estafas · a tiempo · FA | 40/46 · 26/36 · 20/94 | 43/46 · 29/36 · 20/94 |
  | Coreanas | avisadas · a tiempo | 33/33 · 27/27 | 33/33 · 27/27 |

- **Cambian de lado pocas llamadas, pero no ninguna:** 3 de las 156 del test, 3 de las 140 de desarrollo, 4 de las 33
  legítimas reales y ninguna coreana. En otras 18 del test el aviso cae en otra línea.

## Qué tan seguro es

- Son dos pasadas, y difieren en dos cosas a la vez: la sesión de Colab y el modo de correr. No se aisló cuál pesa.
- La causa probable es la de [H11](H11-el-riesgo-cambia-con-el-runtime.md): otro orden de consultas cambia cómo se
  calcula. No se comprobó.
- En cuatro conjuntos el riesgo sube más veces de las que baja, y en la zona gris es al revés. Con dos pasadas no se
  puede decir si hay un sesgo.

## Qué cambia

- **Las cifras de la evaluación final son las del 2026-11-19 y no se reemplazan.** La segunda pasada se informa al
  lado, como margen: hasta 3 casos en estafas avisadas y a tiempo, y hasta 6 antes del pedido.
- **[H02](H02-ruido-entre-corridas.md) sigue valiendo para repetir tal cual.** Entre corridas que no se lanzan igual,
  el margen es mayor que ±2.
- **Dos configuraciones se comparan en la misma sesión y del mismo modo,** como hizo la exploración. Una diferencia de
  3 casos contra una cifra de otra corrida no se le atribuye a la configuración.
