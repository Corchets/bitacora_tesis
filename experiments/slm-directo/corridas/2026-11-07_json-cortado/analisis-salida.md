# v4-corte contra v4 JSON completo, misma sesión de Colab

## 1. Control

Commit `decdff12d482760da8be893a7d94f4e59d19b3a2`, Ollama 0.40.14, digest `b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2`, 150 casos. num_predict de la primera consulta: 24.

Sin problemas.

## 2. Coincidencia línea a línea

| líneas cortado | líneas completo | en las dos | válidas en las dos | riesgo igual | alerta igual | inválidas cortado | inválidas completo |
|---|---|---|---|---|---|---|---|
| 2773 | 2773 | 2773 | 2773 | 2591 (93.4%) | 2756 (99.4%) | 0 {} | 0 {} |

Alerta escrita (cortado, completo): {('false', 'false'): 2331, ('false', 'true'): 6, ('true', 'false'): 11, ('true', 'true'): 425}.

- CV2-D-L-BANCO-002 L9: cortado 0.3 / false, completo 0.5 / true
- CV2-D-L-BANCO-005 L9: cortado 0.5 / true, completo 0.3 / false
- CV2-D-L-BANCO-010 L12: cortado 0.3 / false, completo 0.5 / true
- CV2-D-L-BANCO-010 L13: cortado 0.5 / true, completo 0.3 / false
- CV2-D-V-BANCO-005 L10: cortado 0.5 / true, completo 0.5 / false
- CV2-D-V-BANCO-007 L13: cortado 0.6 / true, completo 0.5 / false
- CV2-D-V-FAMILIAR-001 L18: cortado 0.5 / true, completo 0.3 / false
- CV2-D-V-FAMILIAR-003 L16: cortado 0.3 / false, completo 0.5 / true
- CV2-D-V-ORGANISMO_PREVISIONAL-002 L21: cortado 0.5 / true, completo 0.3 / false
- CV2-D-V-PREMIO-004 L20: cortado 0.3 / true, completo 0.3 / false
- CV2-D-V-SOPORTE-001 L18: cortado 0.5 / true, completo 0.3 / false
- CV2-D-V-SOPORTE-002 L23: cortado 0.3 / false, completo 0.5 / true
- CV2-D-V-SOPORTE-004 L28: cortado 0.5 / true, completo 0.3 / false
- CV2-D-V-WHATSAPP-006 L34: cortado 0.3 / false, completo 0.5 / true
- SC-SOPORTE-CLAVE-01-e01 L11: cortado 0.5 / true, completo 0.3 / false
- TR-01-pedido-indirecto-digitos L6: cortado 0.5 / true, completo 0.3 / false
- TR-04-pedido-tras-charla-larga L28: cortado 0.2 / false, completo 0.2 / true

**Criterio:** riesgo igual en ≥ 93% de las líneas válidas en las dos: SÍ; inválidas del cortado ≤ 1%: SÍ. El corte no cambia la primera consulta.

## 3. Latencia (ms de pared en T4, p50 / p95)

| consulta, mismas líneas | líneas | ms | tokens escritos | lectura del prompt (ms) | escritura (ms) |
|---|---|---|---|---|---|
| primera consulta (cortado) | 2773 | 286 / 360 | 24 / 24 | 96 / 139 | 162 / 192 |
| JSON completo | 2773 | 406 / 974 | 41 / 95 | 95 / 140 | 281 / 834 |

El cortado es más rápido en 2772 de 2773 líneas; mediana del cociente completo / cortado, línea a línea: 1.41.

**Segunda consulta** (motivo y evidencia), en 78 líneas de aviso: 661 / 811 ms; tokens escritos 56 / 73, tokens de prompt (prompt_eval_count) 1092 / 1277; fallos: 4 {'etapa2_alerta_sin_motivo': 4}; evidencia en el texto: 73/78.

| línea de aviso | líneas | ms |
|---|---|---|
| cortado: primera + segunda | 78 | 938 / 1121 |
| JSON completo, mismas líneas | 78 | 783 / 1032 |
| JSON completo, líneas con alerta escrita | 431 | 905 / 1212 |

## 4. Solo para mirar: avisos con «riesgo ≥ 0,4 o alerta»

Misma línea de aviso en 150 de 150 casos.

| corpus_v2 | estafas | antes del pedido | falsas alarmas |
|---|---|---|---|
| v4-corte | 29/46 | 12/36 | 7/51 |
| v4 JSON completo | 29/46 | 12/36 | 7/51 |
| línea base v4 JSON (2026-11-05, b, otra sesión) | 29/46 | 11/36 | 7/51 |

