# Prompts del ensayo #50

> **Estado: propuesta sin discutir.** Primera versión (v1, 2026-10-13). Cualquier
> cambio se registra abajo con fecha y motivo; las corridas guardan el texto
> completo y su hash en `manifiesto.json`, así que una corrida vieja siempre
> dice con qué prompt se hizo.

| Variante (`--prompts`) | Mensaje de sistema |
|---|---|
| `tarea` | [`tarea.txt`](tarea.txt) |
| `tarea+base` | [`tarea.txt`](tarea.txt) + una línea en blanco + [`base_institucional.txt`](base_institucional.txt) |
| `v2` | [`tarea_v2.txt`](tarea_v2.txt), con los campos en otro orden (`ESQUEMA_SALIDA_V2` en `detectores.py`) |
| `riesgo` | [`riesgo.txt`](riesgo.txt) en la etapa 1 (solo `{"riesgo": x}`); si x > umbral, [`riesgo_motivo.txt`](riesgo_motivo.txt) como pedido de la etapa 2 (`DetectorSLMDosEtapas`) |

El mensaje del usuario lo arma `detectores.py` en cada actualización: la
transcripción disponible numerada por línea y una aclaración sobre hablantes
según `--hablantes` (`ab`: cada línea con A o B; `sin`: sin indicar quién habla).

## Versiones del system prompt

Los textos completos se conservan en archivos separados. El número de versión
identifica el historial; **P0/P1 identifica el control y el candidato de una
comparación concreta**, no el orden histórico.

| Versión | Fecha | Texto completo | Cambio y estado |
|---|---|---|---|
| **Versión 1 — original** | 2026-10-13 | [`tarea.txt`](tarea.txt) | Criterio de alerta, seis acciones, exclusión breve de menciones y JSON con riesgo primero. Es `tarea` en el ejecutor y **P0 de las dos corridas de 150**. Commit `d9173b6`. |
| **Versión 2 — modificación previa** | 2026-10-21 | [`tarea_v2.txt`](tarea_v2.txt) | Reformula las acciones, explicita relatos/hipótesis y razones creíbles, quita el ejemplo de código, pone la evidencia primero y exige riesgo ≥ 0,5 con alerta. Es `v2` en el ejecutor; no fue el prompt de esas corridas de 150. Commit `886cff0`. |
| **Versión 3 — probada, no adoptada** | 2026-11-04 | [`tarea_v3.txt`](tarea_v3.txt) | Parte de v2: quita el mínimo de riesgo 0,5, conserva el orden de campos de v2 y agrega reglas de contexto. [Resultados en Colab](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md): más estafas con aviso y muchas más falsas alarmas. No se usa en la demo. |

## Versión 3 — 2026-11-04

> **Estado: propuesta sin discutir.** [Resultados](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md) y [ficha](V3-ATRIBUCION.md), avance de #51
> vinculado a [D07](../../../docs/gestion/MAPA-DECISIONES.md#d07--aprobar-taxonomía-y-evento-crítico) y
> [D08](../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental).

La v3 parte de la v2 y reúne varios cambios, así que un efecto no se atribuye a una frase. Usa
`ESQUEMA_SALIDA_V2`. La opción `--prompts v3` existe solo en la rama `prompt-v3-colab`: aquí no está
registrada en `PROMPTS` ni `ESQUEMAS` y la demo sigue con `tarea`. El borrador anterior, derivado de v1,
se conserva en el commit `8a718fe`.

## Criterios de la v1

- **`tarea`** define qué es una alerta con las seis acciones solicitadas del
  [manual](../../../docs/corpus/MANUAL-ANOTACION.md#acciones-solicitadas) y su
  regla central: mencionar, aconsejar o negar no es pedir. No incluye ejemplos de
  los casos de prueba, para no ajustar el prompt a las respuestas.
- **`base_institucional.txt`** es el texto del laboratorio sin cambios
  (`experiments/laboratorio/detector.py`, rama `laboratorio-main`), que a su vez
  viene del marco #27 de Luciano. Se conserva igual para poder comparar con la
  hipótesis H5 del [contraste](../../../docs/investigacion/CONTRASTE-NLP-TEORIA-Y-LABORATORIO.md).
  Sus afirmaciones **no fueron cotejadas con fuentes** en este ensayo; la regla 4,
  por ejemplo, es más absoluta que lo que respaldan las fuentes del catálogo.

## Criterios de la v2

> **Estado: propuesta sin discutir.** Sale del
> [análisis de errores del 2026-10-21](../analisis/2026-10-21-errores-y-prompt-v2/README.md)
> sobre los mismos 53 casos de desarrollo: está ajustada a ellos y solo se puede evaluar
> de forma justa con casos reservados (#55). No usar el test del corpus v2 para afinarla.

- **Sin el ejemplo del «código».** El motivo tiene que nombrar lo que se pidió. El
  ejemplo de la v1 hacía que 0.8B y 2B dijeran «código» ante pedidos de dinero, fotos
  o pantalla.
- **La cita va primero.** El esquema pide `evidencia`, después `alerta_sugerida`,
  `riesgo` y `motivo`, y la alerta se ata a haber copiado un pedido. En la v1 el
  modelo decidía la alerta antes de escribir la cita, y el 2B dejó 49 líneas con riesgo
  ≥ 0,6 sin alerta.
- **Pedido sin palabras clave o con una razón creíble.** Se aclara que cuenta aunque no
  nombre el código o la transferencia y aunque la razón parezca válida: es el error más
  repetido del 2B (deudas, accidentes, «girame a la cuenta que te dicto»).
- **Lo que no es pedido**, en una lista: mencionar, aconsejar, negar, negarse, relatar
  un pedido de otra llamada o plantearlo como hipótesis. Apunta a los avisos del 4B
  por pedidos relatados y por sospecha.
- **La sospecha sube el riesgo, pero no alerta.** Repite la regla de la v1 (alerta solo
  por pedido) de forma explícita. Si el equipo decide en D08 que la sospecha también
  avise, esto cambia.
- Riesgo de al menos 0,5 cuando hay alerta, para que `riesgo` y `alerta_sugerida` no se
  contradigan.

Los cambios se prueban juntos: no se midió el aporte de cada uno por separado.

## Historial

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-10-13 | v1 | Primera versión para el ensayo #50. |
| 2026-10-21 | v2 (`tarea_v2.txt`, variante `v2`); la v1 queda igual | Errores de la v1 en las corridas del 2026-10-14 y 2026-10-17 (ver «Criterios de la v2»). |
| 2026-10-29 | `riesgo` (`riesgo.txt` + `riesgo_motivo.txt`), en dos etapas; v1 y v2 quedan igual | Bajar la latencia por línea: escribir el JSON completo domina el tiempo ([caché de prefijo](../analisis/2026-10-21-cache-prefijo/README.md)). Escala del riesgo anclada y «una palabra suelta no es pedido» por la minuta del 2026-10-28 (R07). Ver [análisis](../analisis/2026-10-29-riesgo-primero/README.md). |
| 2026-11-04 | v3, borrador P1 (`tarea_v3.txt`), sin integrar al ejecutor; v1/P0 y v2 intactas | Una hipótesis: atribuir el pedido dentro de la llamada frente a relato, hipótesis, ofrecimiento y consejo. [Ficha y controles](V3-ATRIBUCION.md); sin inferencia nueva. |
| 2026-11-04 | v3 reemplazada por un texto basado en v2; v1 y v2 intactas | Decisiones del grill con Luciano. [Probada en Colab sobre los 150 de desarrollo](../corridas/2026-11-04_193946_prompt-v3-a-solo-y-con-indicio/analisis.md): no se adopta. |
