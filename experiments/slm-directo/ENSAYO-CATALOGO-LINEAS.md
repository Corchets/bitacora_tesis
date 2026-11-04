# Qwen3-Reranker: una línea y bloques de dos

> **Estado: propuesta sin discutir.** Comparación exploratoria solicitada por el
> usuario; no cierra [D07, D08 ni D09](../../docs/gestion/MAPA-DECISIONES.md).

## Pregunta y diseño

Se compara la prueba del catálogo de once descripciones con dos entradas nuevas:

1. **Línea:** el reranker se ejecuta por cada línea y recibe solo esa línea.
2. **Par:** se ejecuta cada dos líneas nuevas y recibe los bloques 1–2, 3–4,
   etc. No se solapan. Una línea final impar se registra como no evaluada.

Se usan los mismos datos de desarrollo, modelo, catálogo, reglas de alerta y
políticas con y sin Tito del [ensayo anterior](ENSAYO-CATALOGO-QWEN.md). Los
umbrales se eligen de nuevo sobre las 57 conversaciones de selección y luego se
aplican a las 20 de informe. Esas 20 ya fueron examinadas en el proyecto y no
son un conjunto independiente ni el test final. Las referencias de las 77
conversaciones figuran sin revisión humana.

Tito viejo puntúa cada frase. En la variante de pares, la compuerta se comprueba
en la **segunda línea** del par, como en la regla de activar solo si Tito supera
su umbral en la actualización evaluada. Eso puede perder una activación que solo
ocurre en la primera línea. Se calcula offline desde los puntajes guardados; no
se mide una cascada ejecutada en vivo. Qwen no recibe referencias ni texto futuro.

Como prueba secundaria se consulta `gemma4:e2b` únicamente cuando la situación
principal del reranker es posible engaño. Gemma recibe el historial completo
disponible, además de los puntajes como indicios falibles. No se cambia la entrada
de Gemma para igualarla a la ventana más corta del reranker.

## Reproducción

Requiere GPU CUDA y el modelo `Qwen/Qwen3-Reranker-0.6B`; Gemma requiere Ollama con
`gemma4:e2b` completamente en GPU. Los archivos de salida deben ser nuevos.

```bash
python experiments/slm-directo/ensayo_catalogo_lineas.py --lista seleccion-57 --salida /tmp/catalogo-lineas-seleccion.jsonl
python experiments/slm-directo/analizar_catalogo_lineas.py /tmp/catalogo-lineas-seleccion.jsonl --salida /tmp/catalogo-lineas-umbrales.json
python experiments/slm-directo/ensayo_catalogo_lineas.py --lista rapida-20 --salida /tmp/catalogo-lineas-informe.jsonl
python experiments/slm-directo/analizar_catalogo_lineas.py /tmp/catalogo-lineas-seleccion.jsonl --informe /tmp/catalogo-lineas-informe.jsonl --umbrales /tmp/catalogo-lineas-umbrales.json --anterior experiments/slm-directo/corridas/2026-11-03_catalogo-qwen-metricas.json --salida /tmp/catalogo-lineas-metricas.json
python experiments/slm-directo/slm_catalogo_lineas.py /tmp/catalogo-lineas-informe.jsonl /tmp/catalogo-lineas-umbrales.json --salida /tmp/catalogo-lineas-gemma.jsonl
python experiments/slm-directo/analizar_slm_catalogo_lineas.py /tmp/catalogo-lineas-gemma.jsonl --salida /tmp/catalogo-lineas-gemma-metricas.json
```

Los puntajes no son probabilidades calibradas. La medición de `qwen_ms` excluye
tokenización previa, ASR y latencia de cola. Las marcas en estos textos son de
línea: no se convierten a segundos.

## Resultados del 2026-11-03

Ambos modelos se ejecutaron en la GPU NVIDIA GeForce RTX 3060; Qwen en fp16,
Tito en fp32 y Ollama informó `gemma4:e2b` en GPU. Las corridas separadas son
[selección](corridas/2026-11-03_catalogo-lineas-seleccion.jsonl),
[umbrales](corridas/2026-11-03_catalogo-lineas-umbrales.json),
[informe](corridas/2026-11-03_catalogo-lineas-informe.jsonl),
[métricas del reranker](corridas/2026-11-03_catalogo-lineas-metricas.json),
[consultas a Gemma](corridas/2026-11-03_catalogo-lineas-gemma-informe.jsonl) y
[métricas de Gemma](corridas/2026-11-03_catalogo-lineas-gemma-metricas.json).
Ambas corridas del reranker terminaron sin errores; Gemma completó 42 consultas
válidas y ninguna inválida.

La regla exploratoria de alerta exige que `POSSIBLE_DECEPTION` sea la situación
principal y supere el umbral elegido en selección. Las 20 conversaciones de informe
incluyen 10 estafas y 10 legítimas; selección contiene 19 y 38 respectivamente.

| Entrada de Qwen | Tito | Selección: estafas · falsas alarmas | Informe: estafas · falsas alarmas |
|---|---|---|---|
| Una línea | No | 1/19 · 1/38 | 1/10 · 3/10 |
| Una línea | Sí | 5/19 · 3/38 | 2/10 · 1/10 |
| Par de líneas | No | 2/19 · 3/38 | 3/10 · 4/10 |
| Par de líneas | Sí | 0/19 · 0/38 | 0/10 · 0/10 |

El último 0/10 no es evidencia de buena clasificación: ninguna estafa de selección
quedó detectada para pares con Tito; el desempate eligió umbral 1,0 y la regla usa
`>`; ningún puntaje puede superarlo. Sin umbral, los conteos de informe fueron:
una línea sin/con Tito, 6/10 · 7/10 y 2/10 · 2/10; pares sin/con Tito,
6/10 · 6/10 y 3/10 · 0/10. La tabla del ensayo anterior para ventana de cuatro
líneas directa con umbral fue 8/10 · 6/10; su informe usa los mismos veinte casos.

En informe, la versión de una línea ejecutó Qwen 524 veces y la de pares 258 veces;
ocho llamadas terminaron con una línea sin pareja. Las medianas por evaluación en
GPU fueron 178 ms y 200 ms respectivamente, con p95 de 188 y 208 ms. La suma de
los tiempos registrados de Qwen para los veinte casos fue 93,5 s y 51,2 s; no
incluye tokenización previa, Tito, ASR, Gemma ni el tiempo de espera real para que
llegue la segunda línea. En selección hubo 34 finales sin pareja entre 57 llamadas.

La integración secundaria con `gemma4:e2b` y la regla con umbral produjo en
informe: una línea sin/con Tito, 1/10 estafas · 1/10 legítimas y 2/10 · 0/10;
pares sin/con Tito, 3/10 · 1/10 y 0/10 · 0/10. El SLM recibió el prefijo completo
solo cuando Qwen señaló posible engaño. Estos resultados dependen de la compuerta
y no miden Gemma como detector directo.

La evidencia muestra que, con este catálogo y esta regla, las ventanas más cortas
no resolvieron el compromiso entre detección y falsas alarmas en el conjunto
examinado. La variante de pares cambia a la vez el tamaño de contexto y la frecuencia
de evaluación: no permite atribuir la diferencia a uno solo de esos factores.
