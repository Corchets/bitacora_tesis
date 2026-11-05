# Tito → SLM sin indicio: resultado de la prueba

> **Estado: propuesta sin discutir.** Diagnóstico sobre las 150 conversaciones de
> desarrollo, sin revisión humana de casos ni de `T_R`. No toca el test reservado ni
> cambia por sí solo la configuración del
> [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md).

## Qué se probó

La hipótesis salió de la [comparación anterior](../2026-11-04_132229_e2b-directo-150/comparacion-con-tito.md):
Tito → SLM perdía estafas porque el **bloque de indicio** (la primera frase que marcó
Tito) distraía a Gemma, no porque Tito filtrara de más.

Se corrieron en la **misma máquina** (Colab, GPU T4; código `slm-sin-indicio`
`4916ead`, Ollama 0.40.14) estas cuatro variantes sobre los 150 casos:

| Corrida | Carpeta |
|---|---|
| SLM solo y Tito → SLM con indicio | [`2026-11-04_194015_sin-indicio-a-solo-y-con-indicio`](../2026-11-04_194015_sin-indicio-a-solo-y-con-indicio/resumen.md) |
| Tito → SLM sin indicio | [`2026-11-04_201218_sin-indicio-b-tito-sin-indicio`](../2026-11-04_201218_sin-indicio-b-tito-sin-indicio/resumen.md) |
| Repetición del SLM solo | [`2026-11-04_202259_sin-indicio-c-solo-repeticion`](../2026-11-04_202259_sin-indicio-c-solo-repeticion/resumen.md) |

Todas usan `gemma4:e2b-it-q4_K_M`, el prompt `tarea`, hablantes `ab`, `num_ctx` 4096
y seed 42. El detalle caso por caso está en [comparacion.md](comparacion.md), generado por
[`comparar_sin_indicio.py`](../../comparar_sin_indicio.py).

## Resultado

| | SLM solo | Tito con indicio | **Tito sin indicio** | SLM solo (repetición) |
|---|---|---|---|---|
| Estafas con aviso | 55/75 | 50/75 | **54/75** | 54/75 |
| Avisos antes del pedido | 25 | 18 | **24** | 24 |
| Falsas alarmas | 19/75 | 12/75 | **14/75** | 20/75 |
| · legítimas comunes | 4/51 | 5/51 | 4/51 | 4/51 |
| · legítimas difíciles | 15/24 | 7/24 | 10/24 | 16/24 |
| Consultas al SLM | 2.214 | 1.189 | **1.140** | 2.225 |
| Fallos | 0 | 0 | 0 | 0 |

## Lectura

1. **El azar es casi nulo.** Entre el SLM solo y su repetición, la respuesta cambia en
   2 de 2.213 líneas (0,1 %). Las diferencias entre condiciones no son ruido.
2. **El indicio era el problema.** En las mismas líneas consultadas, el SLM con indicio
   cambia de respuesta en el 2,2 % de los casos respecto del SLM solo. Sin indicio, en el
   0,3 %, prácticamente lo mismo que la repetición. Con indicio se perdían 13 alertas de
   estafa; sin indicio, 2.
3. **Sin indicio detecta casi como el SLM solo:** 54 contra 55 estafas y 24 contra 25
   avisos antes del pedido. En 48 de las 54 estafas compartidas avisa en la misma línea.
   La única que pierde es `PREMIO-001`, donde Tito nunca activa (puntaje máximo 0,23).
   Ahí el límite es la compuerta.
4. **Conserva buena parte del filtrado de Tito:** 14 falsas alarmas contra 19 del SLM
   solo. Saca 5 en legítimas difíciles (`LAB-anses-canal-oficial`, `LG-ORG-TURNO-01`,
   `LG-SUPPORT-INFO-01`, `LG-WA-CONSULTA-01` y `TR-03-negacion-y-consejo`) y no agrega
   ninguna. Con indicio había 12, pero a costa de 5 estafas.
5. **Gasta la mitad:** 1.140 consultas contra 2.214.

**La hipótesis se confirma en detección y en momento del aviso**, con el criterio
fijado antes de correr: 54/75 estafas (se esperaba ≈ 54–55) y los mismos avisos antes
del pedido que el SLM solo. **En falsas alarmas no llega del todo:** se pedía 13/75 o
menos y dio 14/75.

## Lo que no cambia

- **Ninguna variante llega a la meta del tutor** (80–85 % de estafas con 10–15 % de
  falsas alarmas). Sin indicio queda en 72 % y 19 %.
- **Las 19 estafas que no detecta ninguna variante** siguen igual. Son el techo de
  Gemma con el prompt `tarea`, no un problema de Tito. Entre ellas están
  `FAMILIAR-004/005/006` (pedidos condicionales), datos personales en
  `ORGANISMO_PREVISIONAL` y `PREMIO`, y 11 sin pedido de referencia.
- Las falsas alarmas que quedan son sobre todo legítimas difíciles que *mencionan* o
  *desaconsejan* un pedido.

## Límites

- Es material de desarrollo, escrito con asistencia y sin revisión humana. Elegir sin
  indicio mirando estos 150 casos es una decisión de desarrollo: hay que declararla y
  medir recién en el test reservado.
- Colab con GPU T4 no es el teléfono ni la M1: las latencias no se extrapolan.
- Hubo una diferencia menor con las corridas de la PC Windows: el SLM solo dio 55/75 y
  18 falsas alarmas allá, contra 55/75 y 19 acá. Por eso la comparación válida es la
  hecha en la misma máquina.

## Próximos pasos propuestos

1. **Que el equipo decida** si Tito → SLM sin indicio reemplaza a la variante con
   indicio en el ADR 0001. Si se adopta, hay que registrar la decisión y actualizar el
   ADR.
2. **Revisar a mano** los `T_R` dudosos (`FAMILIAR-004/005/006`) y las 11 estafas sin
   pedido de referencia.
3. **Para acercarse a la meta,** el margen está en el prompt o el modelo, no en Tito.
   Cualquier ajuste debe diseñarse sin mirar el test reservado.
