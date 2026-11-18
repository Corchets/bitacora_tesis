# ADR 0008 — El prompt del detector pasa a `c-consejos-corte-riesgo`

- **Fecha:** 2026-11-18
- **Estado:** Aceptada
- **Participantes de la discusión:** Mateo Antenucci, al cerrar la revisión de producto de
  [#143](https://github.com/Corchets/bitacora_tesis/issues/143). Cambia una fila del
  [ADR 0002](0002-detector-gemma4-e2b-solo-con-prompt-c-premisa.md), que registró el equipo.
- **Ámbito:** arquitectura

## Contexto

La [revisión de producto](../../../experiments/slm-directo/corridas/2026-11-10_revision-producto/README.md) probó tres
variantes de `c-premisa-corte-riesgo`, con un párrafo cambiado cada una y una regla escrita antes de correr
([ADR 0005](0005-reglas-de-evaluacion-escritas-antes-de-correr.md)). **Ninguna pasó la regla,** que dejaba
`c-premisa-corte-riesgo` ([análisis](../../../experiments/slm-directo/corridas/2026-11-10_revision-producto/analisis.md)).

## Decisión

Usamos `c-consejos-corte-riesgo`:
[`tarea_c_consejos.txt`](../../../experiments/slm-directo/prompts/tarea_c_consejos.txt) (sha256 `5f0fc84c…`) con
[`salida_json_c.txt`](../../../experiments/slm-directo/prompts/salida_json_c.txt). El resto del ADR 0002 no cambia.

**Es una elección de Mateo por fuera de la regla, hecha después de ver los resultados.** Era la variante que prefería
antes de correr, y así quedó anotado en la regla.

## Alternativas consideradas

Cifras de desarrollo en `alcance-140`, contra la base de la misma tanda (41/46 estafas, 20/36 antes del pedido, 29/36 a
tiempo, 24/94 FA).

| Alternativa | A favor | En contra | Por qué se descartó |
|---|---|---|---|
| Dejar `c-premisa-corte-riesgo` | Es lo que dice la regla escrita antes de correr | Deja sin aviso dos de las 17 estafas de código o clave; 11 a 13 FA en las 75 legítimas que no deberían avisar | Mateo prefirió `c-consejos` |
| `c-codigo-corte-riesgo` | Recupera, tarde, las dos de código o clave que faltaban | −5 antes del pedido y −3 a tiempo | Pierde detección |
| `c-freno-corte-riesgo` | +4 antes del pedido | +9 FA en las 75 que no deberían avisar | Las FA se disparan |

## Consecuencias

- **No es una mejora demostrada.** `c-consejos` queda igual que la base en detección (41/46, 19/36, 28/36). Avisa 16
  de las 17 de código o clave contra 15, y baja las FA de 24 a 22 (18 contra 25 en la repetición). Con un ruido de ±2
  entre tandas, esa diferencia no está firme.
- **En la tesis se informa como lo que es:** una elección posterior a los resultados, sobre los mismos 140 casos. El
  número honesto lo siguen dando la reserva y #144, que no se tocaron.
- La evaluación final de [#52](https://github.com/Corchets/bitacora_tesis/issues/52) y `servidor.py` corren con este
  prompt.
- **La latencia en el teléfono no se midió con este prompt,** que es 284 caracteres más largo. En T4 la consulta tarda
  lo mismo (unos 220 ms).

**Para reconsiderarla:** que en la reserva o en #144 quede 3 o más por debajo de lo esperado en detección.

## Referencias

- [Análisis de la revisión de producto](../../../experiments/slm-directo/corridas/2026-11-10_revision-producto/analisis.md).
- [Los tres textos y sus fuentes](../../../experiments/slm-directo/corridas/2026-11-10_revision-producto/VARIANTES.md).
