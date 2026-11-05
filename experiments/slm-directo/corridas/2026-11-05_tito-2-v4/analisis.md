# v4 con roles: Tito viejo 2.0 y SLM solo

**Fecha:** 2026-11-05. **Issue:** [#140](https://github.com/Corchets/bitacora_tesis/issues/140), sigue abierto.

> **Estado: propuesta sin discutir.** Diagnóstico sobre los 150 casos de desarrollo, ya vistos, con referencias y roles sin revisión
> humana. No es una evaluación final. No toca la reserva, no decide
> [D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental) y no cambia el
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Conclusión

Las dos corridas dieron lo que se había escrito antes de correr, en el [README del Colab](../../colab/README-TITO-2-V4.md#qué-esperamos-escrito-antes-de-correr).

1. **Tito viejo 2.0 no cambia nada con v4: 55/75 estafas y 13/75 falsas alarmas,** con los mismos casos y en la misma línea que v4 con Tito
   viejo. Las frases solo adelantan la activación de `CV2-D-L-BANCO-002` de la línea 7 a la 6, donde el modelo no alerta; el aviso sigue
   en la 7. Es la tercera corrida de v4 con el mismo resultado caso por caso.
2. **Sin Tito, v4 da 56/17.** Gana `CV2-D-V-PREMIO-001`, la única estafa en la que Tito no activa, y suma 5 falsas alarmas, todas en
   legítimas difíciles salvo `CV2-D-L-BANCO-009`. Saca `CV2-D-L-BANCO-006`. Hace casi el doble de consultas (2.225 contra 1.133). Se
   esperaban alrededor de 56 estafas y entre 18 y 25 falsas alarmas: salió una menos.
3. **Tito viejo sigue sirviendo como filtro:** cuesta una estafa y evita 4 falsas alarmas netas y la mitad de las consultas. Con v1 había
   pasado lo mismo (54/14 con Tito, 55/19 sin Tito).

Lo que queda como candidata es **v4 con roles, Tito viejo sin indicio y primer aviso (55/13)**. Tito viejo 2.0 da lo mismo con una pieza
más, así que no hay motivo para preferirlo. Adoptarla va en un ADR 0002, como pide [#51](https://github.com/Corchets/bitacora_tesis/issues/51); la [propuesta para el equipo](../../../../docs/evaluacion/PROPUESTA-CONFIGURACION-DETECTOR.md) reúne todas las comparaciones.

## Resultados

Colab con GPU T4, umbral de Tito 0,5, 150 casos y corte en el primer aviso, salvo `v4 Tito viejo rep`, que sigue tras el aviso. Ninguna
corrida tuvo fallos técnicos.

| Condición | Estafas (de 75) | Corpus v2 (de 46) | Falsas alarmas (de 75) | Comunes (de 51) | Difíciles (de 24) | Antes / en / después del pedido | Cita el pedido | Cita solo a la víctima | Consultas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| v4, Tito viejo | 55 | 27 | 13 | 6 | 7 | 19 / 33 / 2 | 34 | 1 | 1.132 |
| v4, Tito viejo, repetida | 55 | 27 | 13 | 6 | 7 | 18 / 34 / 2 | 36 | 2 | 1.634 |
| **v4, Tito viejo 2.0** (corrida a) | **55** | 27 | **13** | 6 | 7 | 19 / 33 / 2 | 34 | 1 | 1.133 |
| **v4, SLM solo** (corrida b) | **56** | 28 | **17** | 6 | 11 | 19 / 34 / 2 | 36 | 1 | 2.225 |
| v1 A/B, Tito viejo | 54 | 27 | 14 | 4 | 10 | 24 / 25 / 4 | 27 | 8 | 1.140 |
| v1 A/B, SLM solo | 55 | 28 | 19 | 4 | 15 | 25 / 26 / 3 | 27 | 9 | 2.214 |
| v1 A/B, Tito viejo 2.0 ([Nacho](../../analisis/2026-11-05-TITO-VIEJO-2-COMPARACION.md)) | 55 | 28 | 12 | 4 | 8 | 24 / 25 / 5 | 28 | 10 | 1.143 |

«Cita el pedido» y «cita solo a la víctima» usan la definición de
[`comparar_con_v1_colab.py`](../2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/comparar_con_v1_colab.py). Las consultas de la repetida
incluyen las que siguen tras el aviso.

## Qué agrega sacar a Tito

El SLM solo avisa en 10 casos antes de que Tito active, o donde no activa:

- **4 estafas:** `CV2-D-V-PREMIO-001` (que con Tito no avisa) y tres que con Tito avisan igual, unas líneas más tarde (`CV2-D-V-BANCO-004`,
  `CV2-D-V-BANCO-007` y `CV2-D-V-FAMILIAR-003`).
- **6 legítimas:** las 5 falsas alarmas nuevas y `TR-11`, que ya era falsa alarma con Tito. Tres alertan en las primeras dos líneas
  (`LAB-anses-canal-oficial`, `LAB-no-bajes-nada` y `LG-WA-CONSULTA-01-e01`).

## Límites

- Prompts y filtros salen de casos ya vistos: elegir acá no estima el rendimiento. Eso sale de la reserva.
- Según el [documento de Nacho](../../analisis/2026-11-05-TITO-VIEJO-2-COMPARACION.md#procedimiento-y-límites), las frases de Tito viejo 2.0
  se eligieron por fallos observados. Aun así, sobre estos casos no movieron ningún resultado.
- Hay una sola corrida del SLM solo. Diferencias de 1 o 2 casos no se leen como efecto.
- Las corridas de v1 son de otras sesiones de Colab, con la misma configuración.

## Cómo se corrió

| Dato | Valor |
|---|---|
| Entorno | Google Colab con GPU T4, Ollama 0.40.14 |
| Modelo | `gemma4:e2b-it-q4_K_M`, digest `b37049369adf…` |
| Parámetros | `num_ctx` 4096, seed 42, temperatura 0, hablantes `rol`, primer aviso, sin reglas |
| Prompt | `v4` `92df75a22c2746fb`; roles `8c5fcb8135d24de5` |
| Tito | Real, artefacto `fb601eaa…`, umbral 0,5; en la corrida a, con los pesos de [`tito_viejo_2.py`](../../tito_viejo_2.py) y sin indicio |
| Código | Rama [`tito-2-v4-colab`](https://github.com/Corchets/bitacora_tesis/tree/tito-2-v4-colab), commit `2136a9f`, script fijado en `028eef9` (SHA-256 `c3bf0d5f…`), [procedimiento](../../colab/README-TITO-2-V4.md) |
| Duración | a: 16,1 min; b: 17,5 min |

Las cifras salen de los CSV, sin correr modelos: `python -I analizar.py`, desde esta carpeta.
