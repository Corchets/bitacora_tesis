# H12 — Cambiar el prompt mueve cuánto avisa el detector, no a quién: ninguno baja las falsas alarmas en llamadas reales sin perder estafas

- **Fecha:** 2026-11-20
- **Tipo:** resultado
- **Estado:** vigente
- **Evidencia:** [exploración con los conjuntos reales](../../experiments/slm-directo/corridas/2026-11-20_exploracion-reales/analisis.md),
  posterior a la [evaluación final](../../experiments/slm-directo/corridas/2026-11-12_evaluacion-final/analisis.md)
  de [#52](https://github.com/Corchets/bitacora_tesis/issues/52).
- **Afecta a:** el [ADR 0008](../ingenieria/adr/0008-prompt-del-detector-c-consejos.md), que queda como está; los
  resultados y la discusión de la tesis ([capítulo 8](../tesis/CAP-08-RESULTADOS-EXPERIMENTALES.md) y
  [capítulo 9](../tesis/CAP-09-DISCUSION.md)); y [#176](https://github.com/Corchets/bitacora_tesis/issues/176).

## Qué encontramos

Siete prompts y dos políticas de aviso, 13 candidatos, sobre las 33 estafas reales coreanas, las 33 legítimas reales de
call center y desarrollo. La referencia es `c-consejos-corte-riesgo` en la misma sesión: 33/33 coreanas, 27/27 a tiempo
y 23/33 falsas alarmas (FA).

- **Ningún candidato pasó la regla escrita antes de correr.** Los que conservan las coreanas no bajan las FA (21 a 26
  de 33). Los que las bajan pierden estafas a tiempo: `p-niveles` da 12/33 FA con 24/27 a tiempo, y `p-sino`, 8/33 FA
  con 17/33 coreanas.
- **A igual largo, la separación en llamadas reales no mejora.** Con las primeras 12 consultas de cada llamada, la
  probabilidad de que una estafa puntúe más que una legítima va de 0,49 a 0,74 según el prompt; la base da 0,73. En
  desarrollo la base da 0,86 y los prompts nuevos, entre 0,63 y 0,84.
- **Un prompt más corto no avisa mejor.** `p-minimo` (908 caracteres) da 48/94 FA en desarrollo y `p-lista` (1.354),
  34/94, contra 20/94 de la base (2.695). Los dos avisan menos coreanas a tiempo.
- **Esperar una segunda señal no saca FA.** En el test son 15/56 con y sin confirmación, y la confirmación cuesta 12 de
  los 56 avisos a tiempo. Las legítimas del test que avisan tienen dos o más consultas con riesgo ≥ 0,3.
- **El umbral de 0,3 lo piden las estafas generadas.** Con «riesgo ≥ 0,5» la base avisa 28/33 coreanas y 5/33
  legítimas reales, pero 37/100 estafas del test.

## Qué tan seguro es

- Son 33 y 33 llamadas reales, traducidas y de otros países. Tres llamadas son 9 puntos.
- Una corrida por prompt y una versión de cada idea. Que estos prompts no sirvan no prueba que ninguno sirva.
- Las coreanas tienen 56 consultas de mediana y las legítimas reales, 11. La comparación a igual largo usa solo el
  comienzo de las coreanas.
- No se leyó ningún texto: no se sabe por qué falla cada prompt.
- Los conjuntos reales ya se usaron para elegir. Cualquier cifra de un candidato elegido ahí sería optimista.

## Qué cambia

- **La configuración del detector no cambia.** Vale la de la evaluación final.
- **La tesis informa la exploración como resultado negativo,** junto a la evaluación final: el 64 % de FA en llamadas
  reales de call center no se corrige con el prompt.
- **Con estos datos no se puede elegir el umbral para estafas reales de acá.** Las generadas piden uno bajo y las
  coreanas aguantan uno alto; no hay estafas reales argentinas para decidir.

> **Estado: propuesta sin discutir.** Lo que queda por probar no es otro prompt: ajustar el modelo
> ([#176](https://github.com/Corchets/bitacora_tesis/issues/176)) o un aviso en dos niveles en la app, uno suave con
> «riesgo ≥ 0,3» y uno fuerte con «riesgo ≥ 0,5». Las dos son trabajo futuro. `p-niveles` es el único candidato que
> cambia mucho los conjuntos reales; integrarlo o no lo decide Mateo.
