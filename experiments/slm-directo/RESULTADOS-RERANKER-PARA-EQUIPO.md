# Pruebas del reranker para detectar vishing

**Fecha:** 2026-11-03  
**Objetivo:** comparar cómo cambia la detección cuando el reranker deriva la conversación a Gemma.

> Resultados de desarrollo sobre **20 conversaciones: 10 estafas y 10 legítimas**. Ya fueron usadas en pruebas anteriores y sus referencias aún no tienen revisión humana. No son una evaluación final.

## Prueba más reciente

Se quitó «posible engaño» del catálogo. Qwen3-Reranker elige entre las diez opciones restantes y consulta a **Gemma 4 E2B** en cada actualización. También se probó poner a **Tito viejo** como filtro previo.

```text
                         Estafas avisadas       Falsas alarmas
Una línea, sin Tito      ██████████  10/10      ███████░░░  7/10
Una línea, con Tito      ██████████  10/10      ███░░░░░░░  3/10
Pares, sin Tito          ██████████  10/10      ███████░░░  7/10
Pares, con Tito          ██████████  10/10      ███░░░░░░░  3/10
```

Cada bloque representa una conversación. **Con Tito se mantuvieron los diez avisos de estafa y bajaron las falsas alarmas de siete a tres.** Ese 3/10 sigue por encima de la meta de trabajo de 10–15 %; la muestra es demasiado pequeña para extrapolar.

En las estafas, el aviso llegó antes o en la línea del pedido en **8/10 casos** con una línea y Tito, y en **6/10** con pares y Tito. La misma línea no garantiza que el aviso haya ocurrido antes del pedido dentro de esa intervención.

## Comparación con Tito viejo + Gemma anterior

La [corrida anterior de Tito viejo y Gemma](corridas/2026-10-30_112956_101_informe_101.md#gemma4e2b) usó las mismas 20 conversaciones y el mismo archivo de `gemma4:e2b`. Los textos y las referencias coinciden.

| Configuración | Estafas avisadas | Falsas alarmas | Aviso antes o en la línea del pedido |
|---|---:|---:|---:|
| Tito viejo → Gemma, sin reranker | 10/10 | 0/10 | 9/10 |
| Tito viejo → reranker → Gemma, una línea | 10/10 | 3/10 | 8/10 |
| Tito viejo → reranker → Gemma, pares | 10/10 | 3/10 | 6/10 |

En estos casos, la configuración anterior mantuvo la misma detección y tuvo menos falsas alarmas. **No podemos atribuir la diferencia solo al reranker:** la corrida anterior seguía consultando a Gemma después de la primera activación de Tito y usaba otra instrucción; la nueva comprueba a Tito en cada actualización y agrega los puntajes del catálogo. Además, la variante nueva con Tito se reconstruyó a partir de las respuestas registradas.

## Comparación con el catálogo anterior

La prueba anterior consultaba a Gemma solo cuando la categoría principal era «posible engaño». La tabla muestra los resultados de Gemma **sin umbral**, sobre las mismas 20 conversaciones. Cada celda indica **estafas avisadas · falsas alarmas**.

| Entrada | Tito | Prueba anterior | Prueba nueva |
|---|---|---:|---:|
| Una línea | No | 6/10 · 3/10 | 10/10 · 7/10 |
| Una línea | Sí | 2/10 · 1/10 | 10/10 · 3/10 |
| Pares | No | 5/10 · 1/10 | 10/10 · 7/10 |
| Pares | Sí | 3/10 · 0/10 | 10/10 · 3/10 |

La prueba nueva detectó más estafas en estos casos, pero también generó más falsas alarmas. Cambiaron juntos el catálogo, la regla de consulta y el mensaje a Gemma; no sabemos cuál de esos cambios produjo la diferencia.

## Comparación con los experimentos de Evaristo

En los mismos 20 casos, el ensayo de Evaristo con **BGE como detector** avisó en **4/10 estafas** y produjo **1/10 falsas alarmas**. La prueba nueva con **Tito → Qwen3-Reranker → Gemma** avisó en **10/10 estafas** y produjo **3/10 falsas alarmas**.

Son configuraciones distintas: Evaristo usó BGE sin Gemma para ese resultado; la prueba nueva combina tres componentes. También probó Qwen3-Reranker en un control de seis frases, pero no hizo una corrida completa con ese modelo sobre los 20 casos. [Ver el informe de Evaristo](analisis/2026-10-30-reranker-zero-shot/README.md#2026-10-31--r1-completa-con-bge-reranker-77-casos--decisión).

## Costo y límites

- Qwen se ejecutó **524 veces** con una línea y **258 veces** con pares. Gemma recibió las mismas cantidades. La variante con Tito se reconstruyó después: habría derivado **52 y 32 consultas**, respectivamente; no se midió como cascada en vivo.
- En GPU, las medianas por consulta fueron **165 ms para Qwen y 297 ms para Gemma** con una línea; **180 ms y 285 ms** con pares. No representan la latencia total: faltan ASR, procesamiento previo y espera de la segunda línea.
- En ocho conversaciones quedó una última línea sin pareja, por lo que la variante de pares no la evaluó. Usar pares cambia a la vez el contexto y la frecuencia de evaluación.

[Resultados completos de la prueba nueva](ENSAYO-CATALOGO-DIEZ.md) · [Resultados anteriores y todas las configuraciones](ENSAYO-CATALOGO-LINEAS.md) · [Cuatro líneas e historial acumulado](ENSAYO-CATALOGO-QWEN.md) · [Antecedente de Evaristo](analisis/2026-10-30-reranker-zero-shot/README.md).

## Cómo trabajar las falsas alarmas

Las tres llamadas legítimas que alertaron con Tito eran una consulta bancaria, una entrega y una consulta sobre WhatsApp. Gemma interpretó como riesgosas acciones o datos que también pueden aparecer en trámites legítimos.

> **Estado: propuesta sin discutir.** Revisar esas llamadas junto con ejemplos de estafa similares y ajustar la instrucción para que Gemma considere el contexto antes de alertar, sin tratar un pedido sensible como prueba suficiente. Después, elegir los cambios en desarrollo y medirlos en casos separados, controlando también cuántas estafas se pierden o se avisan más tarde. Ver [D07 y D08](../../docs/gestion/MAPA-DECISIONES.md).
