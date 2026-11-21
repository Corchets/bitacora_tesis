# ADR 0009 — En el teléfono, el modelo genera solo el número del riesgo

- **Fecha:** 2026-11-21
- **Estado:** Aceptada
- **Participantes de la discusión:** Mateo Antenucci, con la prueba del punto 2 de
  [#172](https://github.com/Corchets/bitacora_tesis/issues/172).
- **Ámbito:** arquitectura

## Contexto

Con la salida cortada tras el riesgo ([ADR 0006](0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md)),
el modelo genera 14 tokens por línea y siete son siempre los mismos: `{\n  "riesgo":`. En el iPhone 15 Pro Max,
generar es dos tercios del tiempo de cada línea.

## Decisión

En el teléfono (`llama-server`), escribimos nosotros `{\n  "riesgo":` en el turno del modelo y el modelo genera solo
el número y la coma: 6 tokens. El prompt, el umbral, el motivo y el resto de la configuración no cambian.

## Alternativas consideradas

En el iPhone con GPU, con el teléfono en el mismo estado térmico, y en 150 conversaciones de desarrollo en la Mac
([corrida](../../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md)):

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Seguir generando los 14 tokens | Es lo que corrió la evaluación final | 0,93 a 0,98 s por línea contra 0,54 s | Se paga tiempo por texto fijo |
| Prellenar con un mensaje `assistant` final | No hay que armar el prompt a mano | La plantilla de Gemma le agrega un bloque de pensamiento: es otro prompt | Cambió el riesgo en 4 de 15 consultas |

## Consecuencias

- **El aviso no cambia:** las 150 conversaciones avisan igual y en la misma línea. El riesgo cambia en 11 a 20 de
  1.392 líneas, por 0,2 o menos; repetir la configuración anterior cambia 11.
- **La demo y las corridas de Colab siguen con los 14 tokens.** Usan Ollama, y ahí no se probó el prellenado. La
  evaluación final no se repite.
- El prefijo depende del prompt: si cambia el prompt, hay que mirar de nuevo qué escribe el modelo antes del número.

**Para reconsiderarla:** que en el teléfono cambie algún aviso respecto de los 14 tokens.

## Referencias

- [Corrida `solo-el-numero`](../../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md).
- [H11](../../hallazgos/H11-el-riesgo-cambia-con-el-runtime.md).
