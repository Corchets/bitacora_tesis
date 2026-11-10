# H04 — El riesgo que escribe el modelo no sirve como puntaje

- **Fecha:** 2026-11-05
- **Tipo:** resultado
- **Estado:** vigente
- **Evidencia:** [descripción de #143](https://github.com/Corchets/bitacora_tesis/issues/143), sección «Pregunta y comparación», con la corrida de `tarea` del 2026-11-04.
- **Afecta a:** la política de aviso ([#33](https://github.com/Corchets/bitacora_tesis/issues/33), D08) y [#143](https://github.com/Corchets/bitacora_tesis/issues/143).

## Qué encontramos

- El campo `riesgo` del JSON se amontona en pocos valores: 0,1, 0,2 o 0,3 en casi todas las líneas y 0,5 al avisar. El 0,4 apareció en 4 de unas 2.200 líneas.
- Por eso, en corpus_v2 solo hay dos puntos de operación:
  - avisar cuando el modelo lo sugiere: alrededor de 60 % de detección con 8 % de falsas alarmas;
  - avisar con riesgo ≥ 0,3: alrededor de 91 % con 41 %.

## Qué tan seguro es

Es una propiedad de E2B con estos prompts. Otro modelo puede escribir el número de otra forma.

## Qué cambia

No se puede elegir un umbral intermedio sobre el riesgo escrito. Por eso #143 prueba leer la probabilidad del token «SÍ»: la primera vuelta no lo adoptó y la segunda está en curso.

> **Nota (2026-11-10):** la segunda vuelta tampoco lo adoptó. Leer la distribución del dígito del riesgo (v4-L) da un puntaje continuo, pero empata con el número escrito (+1); la latencia que ganaba venía de cortar el JSON ([ADR 0006](../ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md)). Con C, el amontonamiento sigue: 31 de 36 avisos en estafas y 25 de 27 FA salen de un 0,3 exacto ([etapa 3](../../experiments/slm-directo/corridas/2026-11-09_pedido-critico-etapa-3/analisis.md#qué-se-aprende-diagnóstico-después-de-ver-los-resultados)). #143 se cerró, y el token queda atado a un ajuste fino en [#176](https://github.com/Corchets/bitacora_tesis/issues/176), trabajo futuro.
