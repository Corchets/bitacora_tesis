# H01 — La reserva es toda corpus_v2: los resultados se leen aparte de los 53 casos cortos

- **Fecha:** 2026-11-05
- **Tipo:** método
- **Estado:** vigente
- **Evidencia:**
  - Corridas [`2026-11-04_sin-indicio-150`](../../experiments/slm-directo/corridas/2026-11-04_sin-indicio-150/conclusiones.md) y [`2026-11-05_tito-2-v4`](../../experiments/slm-directo/corridas/2026-11-05_tito-2-v4/analisis.md).
  - [Comentario de Mateo en #51](https://github.com/Corchets/bitacora_tesis/issues/51) del 2026-11-05.
- **Afecta a:** [#33](https://github.com/Corchets/bitacora_tesis/issues/33) (protocolo), [#51](https://github.com/Corchets/bitacora_tesis/issues/51) y el capítulo 8.

## Qué encontramos

- La reserva (200 casos) es toda corpus_v2.
- Los otros 53 casos de desarrollo (laboratorio, piloto escrito y trampa) son llamadas de 5 a 12 líneas, con la palabra sensible al principio, y no están en el test.
- Los totales sobre 150 mezclan los dos grupos, y casi todas las diferencias entre configuraciones vienen de los 53 cortos. En corpus_v2:

| Configuración | Estafas (de 46) | Avisos antes del pedido (de 36) | Falsas alarmas (de 51) |
|---|---:|---:|---:|
| v1 solo | 28 | 13 | 4 |
| v1 + Tito | 27 | 12 | 4 |
| v4 solo | 28 | 9 | 6 |
| v4 + Tito | 27 | 8 | 6 |

En los 53 cortos, las falsas alarmas (de 24) son: 15 con v1 solo, 10 con v1 + Tito, 11 con v4 solo y 7 con v4 + Tito.

## Qué tan seguro es

Los conteos salen directo de las corridas. Las referencias no tienen revisión humana, y las diferencias de ±2 casos son ruido ([H02](H02-ruido-entre-corridas.md)).

## Qué cambia

- Toda comparación entre configuraciones informa corpus_v2 por separado, porque es lo que más se parece a la reserva.
- Una mejora que aparece solo en los 53 cortos no anticipa una mejora en el test. Ver [H08](H08-tito-evita-falsas-alarmas-por-punto-ciego.md).
