# Catálogo de diez opciones y consulta a Gemma en cada actualización

> **Estado: propuesta sin discutir.** Experimento de desarrollo solicitado por el
> usuario; no cierra [D07, D08 ni D09](../../docs/gestion/MAPA-DECISIONES.md).

## Pregunta y diseño

El [catálogo nuevo](prompts/catalogo-qwen-diez-v2.json) conserva diez opciones y
no incluye `POSSIBLE_DECEPTION`. El catálogo anterior y sus resultados se conservan
intactos para trazabilidad. Qwen3-Reranker-0.6B puntúa cada opción y señala la
mayor; se envían a `gemma4:e2b` la conversación disponible, la opción principal y
los puntajes como indicios falibles. Gemma decide si sugiere una alerta.

No se usa umbral ni filtro por categoría. Por eso toda actualización válida tiene
una opción ganadora y activa Gemma, incluso si la ganadora es información
insuficiente o una situación aparentemente legítima. Se sigue consultando después
de la primera alerta para comprobar la regla solicitada; las métricas por llamada
cuentan únicamente el primer aviso.

- **Línea:** Qwen recibe una línea y se ejecuta después de cada línea.
- **Par:** Qwen recibe bloques no solapados 1–2, 3–4, etc. Una línea final sin
  pareja queda sin evaluar por esa variante.
- Tito viejo se evalúa sobre la frase nueva; para el par se usa la segunda línea.
  Se procesa Qwen y Gemma en todas las actualizaciones de la versión directa; la
  versión con Tito se reconstruye filtrando las activaciones registradas. La
  reconstrucción no mide una cascada real ni su latencia extremo a extremo.
- Gemma recibe el prefijo completo disponible en el momento de la consulta. Ni
  Qwen ni Gemma reciben referencias humanas, etiquetas de clase ni texto futuro.
- Se usan las mismas 20 conversaciones de desarrollo que la prueba anterior para
  contrastar los resultados. Ya fueron examinadas en el proyecto y sus referencias
  figuran sin revisión humana: **no son evaluación final ni informe independiente**.
- Los puntajes son relevancia, no probabilidades calibradas. Cambiaron juntos el
  catálogo, la regla de derivación y el mensaje a Gemma, que ahora identifica de
  forma explícita la opción principal. Si cambia el resultado no se puede atribuir
  a una sola de esas modificaciones.

## Reproducción

Requiere GPU CUDA, `Qwen/Qwen3-Reranker-0.6B` y Ollama con `gemma4:e2b` en GPU.
Los archivos de salida deben ser nuevos:

```bash
python experiments/slm-directo/ensayo_catalogo_diez.py --lista rapida-20 --salida /tmp/catalogo-diez-reranker.jsonl
python experiments/slm-directo/slm_catalogo_diez.py /tmp/catalogo-diez-reranker.jsonl --salida /tmp/catalogo-diez-gemma.jsonl
python experiments/slm-directo/analizar_catalogo_diez.py /tmp/catalogo-diez-reranker.jsonl /tmp/catalogo-diez-gemma.jsonl --anterior experiments/slm-directo/corridas/2026-11-03_catalogo-lineas-gemma-metricas.json --salida /tmp/catalogo-diez-metricas.json
```

Las latencias registradas por modelo excluyen ASR, espera de la segunda línea y
la coordinación de la cascada real. Las posiciones anotadas son líneas, no segundos.

## Resultados del 2026-11-03

Se ejecutó en GPU NVIDIA GeForce RTX 3060. Qwen3-Reranker-0.6B conservó la revisión
`e61197ed45024b0ed8a2d74b80b4d909f1255473`; Ollama informó `gemma4:e2b` en GPU,
con digest `b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2`.
Las salidas son [reranker](corridas/2026-11-03_catalogo-diez-reranker.jsonl),
[consultas a Gemma](corridas/2026-11-03_catalogo-diez-gemma.jsonl) y
[métricas](corridas/2026-11-03_catalogo-diez-metricas.json). Se verificó una
consulta a Gemma por cada actualización: 782 respuestas válidas y ninguna inválida.

El informe tiene 10 estafas y 10 legítimas. La evaluación cuenta el primer aviso
de Gemma por conversación; continúa ejecutando y registrando todas las consultas
incluso después de ese aviso.

| Ventana | Tito | Estafas con aviso | Legítimas con falsa alarma | Aviso antes o en línea del pedido |
|---|---|---:|---:|---:|
| Una línea | No | 10/10 | 7/10 | 10/10 |
| Una línea | Sí | 10/10 | 3/10 | 8/10 |
| Par de líneas | No | 10/10 | 7/10 | 10/10 |
| Par de líneas | Sí | 10/10 | 3/10 | 6/10 |

Con la compuerta de Tito se conserva la detección en estos casos y se reducen las
falsas alarmas frente a la derivación en todas las actualizaciones, pero 3/10
sigue por encima de la meta de trabajo de 10–15 %. El intervalo de Wilson al 95 %
para 10/10 es aproximadamente 72–100 %; para 3/10 falsas alarmas, 11–60 %.
La muestra es muy pequeña para extrapolar. En seis estafas hay referencia de
cumplimiento y las cuatro configuraciones avisaron en una línea anterior en 6/6;
no se infiere prevención para las otras cuatro. Una alerta en la misma línea del
pedido no demuestra que haya salido antes de ese pedido dentro de la intervención.

Ejemplo de falsa alarma: en `CV2-D-L-BANCO-001`, línea 14, Qwen eligió
`INSUFFICIENT_INFORMATION` y Gemma alertó ante una solicitud de confirmar el nombre
del titular. La referencia de la conversación es legítima; no cuenta con revisión
humana. El caso ilustra que enviar cada actualización permite a Gemma revisar el
contexto, pero no evita por sí mismo las falsas alarmas.

En la variante directa Qwen hizo 524 evaluaciones de una línea y 258 de pares;
con Tito se habrían derivado 52 y 32 respectivamente. En GPU, las medianas por
evaluación fueron 165 ms de Qwen y 297 ms de Gemma para una línea; 180 y 285 ms
para pares. No se suman esas medianas para atribuir latencia total. Ocho llamadas
terminaron con una línea sin pareja.

En la [prueba anterior](ENSAYO-CATALOGO-LINEAS.md), con posible engaño como
condición y sin umbral, Gemma alertó en 6/10 estafas y 3/10 legítimas para una
línea directa, y 3/10 y 0/10 para pares con Tito. La nueva regla aumenta detección
y falsas alarmas en estas configuraciones, pero cambian a la vez el catálogo, la
derivación y el mensaje. No se puede adjudicar la diferencia a una sola causa ni
considerar este conjunto una evaluación independiente.
