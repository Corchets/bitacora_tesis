# ¿En qué se apoya cada aviso? Escalera 0.8B, 2B y 4B

> **Estado: propuesta sin discutir.** Análisis de desarrollo del ensayo
> [#50](https://github.com/Corchets/bitacora_tesis/issues/50) sobre casos escritos.
> Clasificación automática, sin revisión humana todavía. No elige modelo (D09) ni
> política (D08).

## Pregunta

Contar avisos no alcanza: un modelo puede avisar en una estafa por la razón
equivocada. Para cada **primer aviso** de cada modelo se preguntó si el motivo que
mostró el modelo se apoya en lo dicho hasta esa línea.

## Método

- **Corridas:** `qwen3.5:0.8b` ([`173532`](../../corridas/2026-10-14_173532_demo-qwen3.5-0.8b/resumen.md)),
  `qwen3.5:2b` ([`172930`](../../corridas/2026-10-14_172930_demo-qwen3.5-2b/resumen.md), primera de las dos
  iguales) y `qwen3.5:4b` ([`174602`](../../corridas/2026-10-14_174602_demo-qwen3.5-4b/resumen.md)), todas con
  prompt `tarea`, hablantes `ab`, sobre los 53 casos.
- **Entrada de cada juicio** (`avisos-<modelo>.json`): el diálogo disponible hasta la
  línea del aviso, el motivo y la evidencia del modelo. **Sin la clase ni el
  escenario**, para no juzgar el aviso por saber si era estafa.
- **Categorías:**
  - `pedido_presente_bien_descrito`: alguien pide ahora algo de riesgo y el motivo
    lo describe bien;
  - `pedido_presente_mal_descrito`: hay pedido, pero el motivo nombra otra cosa;
  - `pedido_relatado_o_negado`: se cuenta un pedido ajeno, se lo niega o se lo plantea
    como hipótesis;
  - `sospecha_sin_pedido`: sin pedido, el motivo avisa por suplantación, presión o
    contexto;
  - `pedido_inventado`: el motivo afirma un pedido que no está en el texto.
- **Revisores:** dos clasificadores automáticos independientes por modelo, que no
  vieron las respuestas del otro. Todas las clasificaciones, con cita y
  justificación, están en `clasificaciones.json`.
- **Acuerdo entre revisores:** 34/34 en 0.8B, 22/22 en 2B y 43/44 en 4B (κ de Cohen
  1,00, 1,00 y 0,96). El único desacuerdo, `TR-08` en 4B («Pasame el código» antes
  de «del candado»), quedó como `bien` o `mal` según el revisor; abajo se cuenta
  con el revisor 1.
- **Límite del acuerdo:** los dos revisores son el mismo tipo de modelo y pueden
  compartir sesgos. Un acuerdo alto entre ellos no reemplaza que una persona del
  equipo revise una muestra.

## Resultados

| Modelo | Avisos | Pedido real, bien descrito | Pedido real, mal descrito | Relatado o negado | Sospecha sin pedido | Pedido inventado |
|---|---|---|---|---|---|---|
| 0.8B | 34 | 12 | 9 | 1 | 0 | **12** |
| 2B | 22 | **13** | 6 | 1 | 0 | 2 |
| 4B | 44 | 15 | 0 | 7 | **21** | 1 |

Separado por clase de la conversación (dato que los revisores no vieron):

| Modelo | En vishing | En legítimas |
|---|---|---|
| 0.8B | 11 bien · 7 mal · 8 inventados | 1 bien · 2 mal · 1 relatado · 4 inventados |
| 2B | 13 bien · 5 mal · 2 inventados | 1 mal · 1 relatado |
| 4B | 11 bien · 17 sospecha · 1 inventado | 4 bien · 7 relatados · 4 sospecha |

## Lectura

- **0.8B inventa pedidos.** Un tercio de sus avisos afirma «te están pidiendo un
  código» cuando nadie lo pidió todavía; reacciona a «banco + urgencia». Sus avisos
  tempranos en vishing salen de ese error, no de anticipar.
- **2B avisa por la razón correcta en la mayoría de los casos:** 19 de 22 avisos
  responden a un pedido real. Su debilidad es el motivo: en 6 nombra otra cosa
  (dice «código» cuando pidieron compartir pantalla o transferir).
- **4B casi no inventa, pero avisa por sospecha.** En vishing eso es anticipación
  real: 17 avisos por suplantación o presión antes del pedido. Pero la misma
  conducta da falsas alarmas: trata como actuales los pedidos que alguien cuenta
  («me llamaron para que baje un programa») y desconfía de entidades legítimas.
- **El ejemplo del prompt sesga el motivo.** El prompt v1 da como ejemplo «Te
  están pidiendo un código que da acceso a tu cuenta». 0.8B y 2B lo repiten aunque
  lo pedido sea dinero, una foto o la pantalla.

## Qué sugiere para el próximo paso

> **Estado: propuesta sin discutir.** Requiere acuerdo del equipo; afecta D08.

1. **Decidir qué tiene que provocar un aviso:** solo un pedido (como hace 2B, con
   pocas falsas alarmas y avisos más tardíos) o también la sospecha (como hace 4B,
   que anticipa pero se equivoca más). Es la discusión de D08 y estos datos la
   ilustran.
2. **Prompt v2:** sacar el ejemplo del «código» y pedir que el motivo nombre lo que
   efectivamente se pidió; aclarar que un pedido relatado, negado o hipotético no
   cuenta.
3. **Repetir cada configuración** al menos tres veces: dos corridas iguales del 2B
   difirieron en 2 de 53 casos.
4. **Revisión humana** de una muestra de estas clasificaciones antes de citarlas en
   el informe.
