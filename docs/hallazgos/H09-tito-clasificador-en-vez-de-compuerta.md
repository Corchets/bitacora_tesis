# H09 — Tito se entrenó como clasificador de estafas; tenía que ser una compuerta de lo sensible

- **Fecha:** 2026-11-06
- **Tipo:** cambio de enfoque
- **Estado:** vigente. El mecanismo de las palabras sueltas es una hipótesis.
- **Evidencia:** [análisis del 2026-11-06](../../experiments/slm-directo/analisis/2026-11-06-tito-compuerta-sensible/README.md#5-por-qué-tito-se-entrenó-para-otra-cosa) y [H08](H08-tito-evita-falsas-alarmas-por-punto-ciego.md).
- **Afecta a:**
  - [ARQUITECTURA §8.5](../ingenieria/ARQUITECTURA.md#85-qué-tiene-que-cumplir-la-compuerta);
  - el [glosario](../GLOSARIO.md);
  - el trabajo futuro de [#TRABAJO-FUTURO](https://github.com/Corchets/bitacora_tesis/issues/TRABAJO-FUTURO);
  - los capítulos [5](../tesis/CAP-05-DISENO-Y-ARQUITECTURA.md#551-detector), [9](../tesis/CAP-09-DISCUSION.md#93-análisis-de-errores) y [11](../tesis/CAP-11-CONCLUSIONES.md#114-trabajo-futuro-acotado).

## Para qué estaba Tito

**Objetivo:** reducir las consultas al SLM sin perder detecciones. El SLM decide; Tito solo deja sin consulta lo trivial.

**Por qué reducir consultas:**

- La inferencia tiene que ser local en el teléfono (RNF-04).
- E2B tarda 3,74 s de mediana por consulta y no cumple RNF-03. Tito tarda unos 30 ms.
- En vivo el detector no hace cola: si está ocupado, se saltean líneas.
- La mayoría de las llamadas de una persona son cotidianas, y consultar un SLM en cada línea de cada llamada es un costo continuo por un evento raro.
- Batería, temperatura y memoria en Android no se midieron ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)).

## Qué encontramos

- **El objetivo de entrenamiento fue otro.** Tito aprendió a distinguir estafa de legítima con 5.520 textos sintéticos. Las legítimas incluyen a propósito usos inocentes de códigos y claves (319 mencionan clave, código, PIN, documento o tarjeta) para que no reaccione a esas palabras solas. Así se entrena un clasificador preciso. Una compuerta necesita lo contrario: despertar con cualquier cosa sensible, sea de quien sea y aunque sea inocente.
- **Los datos no se parecen a una línea de llamada.**
  - Las estafas del banco son monólogos del estafador de 18 a 39 palabras, con presentación y pedido juntos.
  - Ninguna está contada por la víctima («me llamaron», «me llegó»): los 42 textos así son legítimos.
  - Ningún texto tiene menos de 10 palabras.
  - En una llamada, la maniobra se reparte en varias líneas, la mitad las dice la persona protegida y muchas son cortas.
  - Por eso Tito reacciona a la presentación («te llamo del banco») y no a lo sensible.
- **La frase aislada no alcanza.** Tito no conecta la presentación de la línea 2 con el pedido de la línea 8.
- **Las palabras sueltas son un artefacto, no el banco.** «bien», «gracias» y «corta» pasan de 0,5, pero «gracias» aparece solo en legítimas del banco y «Perfecto, gracias.» saca 0,000. Hipótesis: con una sola palabra, el promedio de RoBERTuito queda dominado por los tokens especiales de inicio y fin.
- **Corregirlo no es un ajuste.**
  - Tito nuevo, con historial acumulado ([#99](https://github.com/Corchets/bitacora_tesis/issues/99)), avisó 2 de 10 estafas.
  - Tito viejo 2.0 ([#140](https://github.com/Corchets/bitacora_tesis/issues/140)) suma de 0,03 a 0,10 por frase clave, y no despierta una línea que sacó 0,000.
  - Tito o reglas v1, sin ajustar nada, cubre 63/64 y 30/43, pero deja sin consultar el 23 % de las líneas en vez del 41 %.

## Qué tan seguro es

- El objetivo y los datos de entrenamiento son hechos: están en el banco.
- La relación causal con el punto ciego es la explicación más directa. No se probó reentrenando.
- El mecanismo de las palabras sueltas no se verificó con el modelo.

## Qué cambia

- **Cambio de enfoque.** Una compuerta no clasifica: es un detector de lo sensible, de alta cobertura. Se diseña y se mide por cobertura, y recién después por ahorro.
- La [arquitectura](../ingenieria/ARQUITECTURA.md#85-qué-tiene-que-cumplir-la-compuerta) y el [glosario](../GLOSARIO.md) lo registran.
- Hay alrededor de un tercio de líneas sin nada sensible (32 % en los 150), así que la idea de una compuerta sigue en pie. Lo que falló es esta implementación.
- El rediseño queda como trabajo futuro en [#TRABAJO-FUTURO](https://github.com/Corchets/bitacora_tesis/issues/TRABAJO-FUTURO): primero medir en el teléfono si el ahorro hace falta.
