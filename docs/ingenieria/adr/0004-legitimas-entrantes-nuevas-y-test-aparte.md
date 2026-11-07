# ADR 0004 — Sumamos legítimas entrantes de números desconocidos y las medimos con un test aparte

- **Fecha:** 2026-11-06
- **Estado:** propuesta sin discutir
- **Participantes de la discusión:** el equipo, con Mateo Antenucci, en la segunda vuelta de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Evaristo Villalobo generó las legítimas de desarrollo.
  Cómo se rehace la reserva se define en [#45](https://github.com/Corchets/bitacora_tesis/issues/45). Se registra en
  [#151](https://github.com/Corchets/bitacora_tesis/issues/151).
- **Ámbito:** corpus

## Contexto

Con el alcance del [ADR 0003](0003-detector-solo-en-entrantes-de-no-agendados.md), las legítimas que importan son las
entrantes de números desconocidos, y el corpus casi no las tiene. Quién inició cada llamada se anotó a ciegas, sin ver
la clase:

| | Estafas entrantes | Legítimas que inicia la persona | Legítimas entrantes |
|---|---:|---:|---:|
| corpus_v2, desarrollo | 46 de 46 | 44 de 51 | 7 de 51 |
| Reserva | 100 de 100 | 74 de 100 | 26 de 100 |

Quién llamó predice la clase. Además, las legítimas entrantes son casi todas de familiares, compañeros o contactos de
WhatsApp, que en un teléfono real estarían agendados. El sesgo salió del generador, no del
[diseño](../../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md#cantidades).

## Decisión

1. **No se sacan casos.** El alcance se aplica en el análisis, con la anotación a ciegas.
2. **Desarrollo suma 94 legítimas entrantes de números desconocidos:** las 91 de Evaristo, en los lotes `LEG`, `LEG2` y
   `ENT-L`, y 3 de selección de personal ([PR #155](https://github.com/Corchets/bitacora_tesis/pull/155)).
3. **El test es la reserva rehecha:** sus 100 estafas, que ningún detector corrió, y un lote nuevo de 50 o más
   legítimas entrantes. El lote se genera a ciegas, con un largo parecido al de las estafas y sin reescribir casos de
   desarrollo. El test queda en `laboratorio-luciano`, con la reserva, y no entra en `laboratorio-main`.
4. **Un agente distinto del detector corrige el test** con la guía de
   [#145](https://github.com/Corchets/bitacora_tesis/issues/145). El equipo lee una muestra, y después el test se
   congela con SHA-256.

La evaluación final se informa en dos partes. La principal es dentro del alcance, con las estafas de la reserva y las
legítimas nuevas de test. Aparte se informan las 100 legítimas viejas de la reserva.

## Alternativas consideradas

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Medir dentro del alcance con lo que hay | No hay que generar nada | En desarrollo hay 7 legítimas: una falsa alarma vale 14 puntos | Las cifras no se pueden defender |
| Seguir midiendo sin alcance | Se compara con las corridas anteriores | Mide otro producto: las consultas que inicia la persona dominan las falsas alarmas | Queda como vista aparte |
| La reserva tal cual como test | No hay que generar otro lote | Tiene 26 legítimas entrantes, casi todas de contactos | Hace falta un lote nuevo |
| Llamadas reales o un corpus externo | No salen de nuestro generador | Las reales piden consentimiento, y las externas ([#144](https://github.com/Corchets/bitacora_tesis/issues/144)) no traen legítimas difíciles | #144 queda como prueba de generalización |

## Consecuencias

- Las falsas alarmas del test dependen casi enteras del lote nuevo.
- Las legítimas nuevas salen de otra tanda que las estafas, y una diferencia de forma puede delatar la clase. Ya se
  vieron dos:
  - las `LEG` y `LEG2` son más cortas que las estafas;
  - el DNI aparece en el 37 % de las legítimas de Evaristo y en el 7 % de las estafas (R29,
    [#154](https://github.com/Corchets/bitacora_tesis/issues/154)).

  Por eso los resultados de desarrollo se informan por lote.
- Las corridas anteriores sobre los 150 casos se leen como «sin alcance».
- El test no tiene referencia humana completa (R28), y la reserva es pública desde el 2026-10-23 (R05).
- **Limitación declarada:** el corpus es sintético y sale de un solo generador.

**Para reconsiderarla:** que el lote de test no llegue a 50 legítimas antes de congelarlo.

## Referencias

- [`alcance-desarrollo.json`](../../../experiments/slm-directo/casos/alcance-desarrollo.json): regla y conteo de
  desarrollo. La anotación de la reserva va por #45.
- [Diseño de corpus_v2](../../../experiments/slm-directo/casos/DISENO-CORPUS-V2.md) y
  [método del corpus, §9](../../corpus/METODO-CREACION-CORPUS.md#9-división-de-datos).
