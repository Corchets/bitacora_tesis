# H10 — Con el prompt de intención (C), el SLM avisa antes del pedido y suma las estafas sin pedido

- **Fecha:** 2026-11-10
- **Tipo:** resultado
- **Estado:** vigente
- **Evidencia:**
  - [Etapa 2 de #143](../../experiments/slm-directo/corridas/2026-11-07_alcance-etapa-2/analisis.md#resumen): C contra `v4-corte`.
  - [Prueba de sensibilidad](../../experiments/slm-directo/corridas/2026-11-10_sensibilidad-c/analisis.md): `c-premisa`, la configuración congelada.
- **Afecta a:** PI2 (margen temporal) en el [capítulo 9](../tesis/CAP-09-DISCUSION.md#91-respuesta-a-las-preguntas-de-investigación) y la elección de prompt en [#51](https://github.com/Corchets/bitacora_tesis/issues/51). Supera a [H03](H03-el-slm-avisa-en-el-pedido.md) y [H06](H06-v4-avisa-mas-tarde-y-cita-mejor.md).

## Qué encontramos

- **C pregunta por la intención, no por el pedido.** En `alcance-140`, contra `v4-corte` (etapa 2):
  - con pedido, los dos detectan 27 de 36, pero C avisa antes del pedido en 17 contra 10, con una mediana de adelanto de 4 líneas contra 0 en los avisos a tiempo;
  - sin pedido, C avisa 9 de 10 y v4 1 de 10;
  - las FA bajan de 42 a 27 de 94.
- **La configuración congelada** (`c-premisa-corte-riesgo`, «≥ 0,3», solo OTRA) da 40/46 estafas, 19 de 36 antes del pedido, 29 de 36 a tiempo y 26/94 FA. La repetición queda dentro de ±2.
- Confirma la causa que daba H03: el aviso caía en el pedido porque el prompt definía el aviso como «hay un pedido».

## Qué tan seguro es

Es desarrollo: el prompt se eligió sobre estos casos y la reserva no se corrió. Las marcas de `T_R` siguen sin revisión humana. El aviso sale casi siempre de un 0,3 exacto ([H04](H04-riesgo-escrito-no-es-puntaje.md)), así que un cambio chico de prompt mueve varias cifras.

## Qué cambia

- PI2 se responde con C: el margen preventivo existe, pero depende de cómo se define el aviso.
- La elección de prompt en #51 deja de ser el intercambio entre v1 y v4 de H06.
