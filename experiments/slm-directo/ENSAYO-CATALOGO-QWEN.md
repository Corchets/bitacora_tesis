# Ensayo nuevo: Qwen3-Reranker con catálogo contrastivo

> **Estado: propuesta sin discutir.** Experimento de desarrollo acordado con el
> usuario. No cierra [D07, D08 ni D09](../../docs/gestion/MAPA-DECISIONES.md).

## Pregunta y alcance

¿Qué señales aporta Qwen3-Reranker-0.6B cuando compara cada prefijo con once
descripciones de situaciones e indicios, con y sin la compuerta de Tito viejo?
El catálogo acordado vive en [catalogo-qwen-decisiones-v1.json](prompts/catalogo-qwen-decisiones-v1.json).
Es una prueba nueva y separada: el ensayo previo de Evaristo queda intacto.

Los puntajes son relevancia relativa, no probabilidades calibradas. La salida
principal se elige entre las nueve situaciones; se guardan también los puntajes
de los dos indicios. Pedidos sensibles y afirmaciones de identidad no prueban
fraude. La referencia de clase y las marcas no se entregan al modelo.

## Diseño

- Texto de conversaciones existentes, prefijo a prefijo; nunca se usa texto futuro.
- Ventanas de cuatro líneas y de historial acumulado, con recorte por la izquierda
  cuando el par excede el límite; los tokens recortados se registran por consulta.
- Tito viejo recibe la frase actual. Se considera activado solo en esa actualización
  si su puntaje es al menos 0,5. La variante directa procesa todas las líneas.
- Para reutilizar cómputo se ejecuta Qwen sobre todas las actualizaciones y la
  compuerta de Tito se aplica después a los puntajes guardados. Es una simulación
  de esa compuerta, no una medición de latencia de una cascada ejecutada en vivo.
- `qwen_ms` mide las pasadas del modelo y el armado del lote en GPU, pero excluye
  la preparación previa del texto y la tokenización. No representa la latencia
  completa desde el audio hasta un aviso. El pico CUDA corresponde al proceso,
  incluye ambos modelos y no representa el consumo total de la computadora.
- Se cotejan la situación más puntuada y esa situación con umbral. Como regla
  exploratoria de aviso se usa que `POSSIBLE_DECEPTION` sea la situación principal;
  sola o acompañada de umbral. No es una política final de alerta.
- Selección: `seleccion-57`; informe: `rapida-20`, ambos de desarrollo. El umbral
  se elige solo sobre selección, con ≤15 % de falsas alarmas, máximo de estafas
  detectadas, desempate por menos falsas alarmas y umbral más alto. El conjunto de
  informe ya fue usado en el proyecto: no es test final ni evidencia independiente
  de toda decisión previa. No se afirma independencia semántica completa de Tito.
- El SLM es una integración secundaria: se consulta si la situación principal es
  posible engaño y, en su variante con umbral, si además supera el umbral fijado.
  Recibe el prefijo completo y los puntajes del reranker como indicios falibles.
- Las referencias por línea son parciales. No se presume que una etiqueta ausente
  signifique ausencia del indicio, ni que una marca de línea represente segundos.

## Ejecución reproducible

Requiere GPU CUDA y PyTorch con soporte CUDA. El ejecutor falla si no hay GPU;
Qwen se ejecuta en fp16 y Tito en fp32. El manifiesto registra versiones, GPU,
revisión del modelo, hashes de fuentes y datos, configuración y estado Git. Las
salidas son archivos nuevos y no se sobreescriben.

```bash
python experiments/slm-directo/ensayo_catalogo_qwen.py --lista seleccion-57 --salida /tmp/catalogo-qwen-seleccion.jsonl
python experiments/slm-directo/preseleccionar_catalogo_qwen.py /tmp/catalogo-qwen-seleccion.jsonl --salida /tmp/catalogo-qwen-umbrales.json
python experiments/slm-directo/ensayo_catalogo_qwen.py --lista rapida-20 --salida /tmp/catalogo-qwen-informe.jsonl
python experiments/slm-directo/analizar_catalogo_qwen.py /tmp/catalogo-qwen-seleccion.jsonl /tmp/catalogo-qwen-informe.jsonl --umbrales /tmp/catalogo-qwen-umbrales.json --reglas experiments/slm-directo/corridas/2026-10-21_201914_m1-reglas-v2-150/actualizaciones.csv --salida /tmp/catalogo-qwen-metricas.json
python experiments/slm-directo/slm_catalogo_qwen.py /tmp/catalogo-qwen-informe.jsonl /tmp/catalogo-qwen-umbrales.json --salida /tmp/catalogo-qwen-slm.jsonl
python experiments/slm-directo/analizar_slm_catalogo.py /tmp/catalogo-qwen-slm.jsonl --salida /tmp/catalogo-qwen-slm-metricas.json
```

Para una comprobación corta se agrega `--casos ID` con un ID de la lista elegida.
Una corrida interrumpida no contiene la marca `fin` y el analizador la rechaza;
igual conserva sus registros como diagnóstico, no como resultado completo.
El analizador exige cobertura íntegra y rechaza fallos, duplicados y configuraciones
incompatibles. El análisis informa intervalos de Wilson para las proporciones de
alerta, compara activaciones de Tito y cubre reglas donde haya registros completos.
La detección de tipo de pedido entre las cinco opciones se informa solo para casos
con marca de referencia y no prueba que exista fraude.

## Corrida exploratoria del 2026-11-03

Se ejecutó en NVIDIA GeForce RTX 3060, CUDA, Qwen fp16 y Tito fp32. Las salidas
son [selección](corridas/2026-11-03_catalogo-qwen-seleccion.jsonl),
[umbrales](corridas/2026-11-03_catalogo-qwen-umbrales.json),
[informe](corridas/2026-11-03_catalogo-qwen-informe.jsonl) y
[métricas](corridas/2026-11-03_catalogo-qwen-metricas.json). Qwen quedó fijado
en la revisión `e61197ed45024b0ed8a2d74b80b4d909f1255473`. Todas las referencias
de ambas listas registran `revision_humana: false`.

La tabla aplica la regla exploratoria de posible engaño como situación principal,
con el umbral elegido en selección. El informe tiene 10 estafas y 10 legítimas;
selección, 19 y 38 respectivamente. En el informe, la regla sin umbral produjo
los mismos conteos de alertas que la regla con umbral.

| Ventana | Compuerta Tito | Selección: estafas / legítimas con alerta | Informe: estafas / legítimas con alerta |
|---|---|---|---|
| 4 líneas | No | 10/19 · 5/38 | 8/10 · 6/10 |
| 4 líneas | Sí | 7/19 · 1/38 | 3/10 · 2/10 |
| Acumulada | No | 8/19 · 4/38 | 3/10 · 2/10 |
| Acumulada | Sí | 6/19 · 2/38 | 3/10 · 2/10 |

En esos mismos 20 casos, reglas v2 alertaron en 6/10 estafas y 1/10 legítimas;
el umbral de Tito se activó en 10/10 y 5/10 respectivamente. La activación de Tito
es una sospecha de filtro, no la alerta de su cascada original. Son recuentos de
desarrollo, no una comparación independiente de toda selección previa. Los
intervalos de Wilson están en el archivo de métricas: por ejemplo, el 8/10 tiene
IC 95 % de 49–94 %, y el 6/10 de falsas alarmas, 31–83 %.

En el informe, Qwen sin Tito tardó una mediana de 227 ms por ventana de cuatro
líneas y 404 ms por ventana acumulada, con p95 de 248 ms y 700 ms respectivamente.
Es tiempo de inferencia registrado, sin tokenización previa ni ASR. Los picos
CUDA asignados al proceso fueron aproximadamente 1,67 GiB y 2,02 GiB. Tito activó
52 de 524 actualizaciones. La ejecución no midió tiempos de una cascada real.

Como diagnóstico, en `T_R` el mayor puntaje entre los cinco tipos de pedido
coincidió con la referencia en 7/10 casos para ventana corta directa y 5/10 para
historial acumulado directo. Se fuerza una elección entre tipos de pedido: no es
una medida de que el pedido realmente exista ni de que sea fraude.

La regla corta directa alertó en el primer turno de `CV2-D-L-BANCO-001`, una
consulta legítima sobre un débito, y no alertó en las dos estafas de WhatsApp del
informe. La corrida muestra un problema de falsas alarmas y omisiones bajo esta
regla y formulación; no descarta otras configuraciones de Qwen ni valida su
rendimiento sobre llamadas reales.

### Integración secundaria con SLM: corrección del 2026-11-03

El usuario aclaró que el SLM indicado para el experimento es **`gemma4:e2b`**.
La primera corrida usó por error `qwen3.5:4b`; sus
[registros](corridas/2026-11-03_catalogo-qwen-slm-informe.jsonl) y
[métricas](corridas/2026-11-03_catalogo-qwen-slm-metricas.json) se conservan
como antecedente, pero **no responden a la integración solicitada**. Los resultados
principales del reranker no dependen del SLM y no cambian por esta corrección.

La repetición se ejecutó con `gemma4:e2b`, revisión Ollama
`b37049369adfe3d2b653af0ab301a062ca5cbe96ace6aa0d3f2559ee9b563fc2`,
prompt `v2`, seed 42 y razonamiento extendido desactivado. Ollama informó el
modelo en GPU. Los [registros](corridas/2026-11-03_catalogo-gemma4-slm-informe.jsonl)
y [métricas](corridas/2026-11-03_catalogo-gemma4-slm-metricas.json) corresponden
a la configuración corregida. El ejecutor [slm_catalogo_qwen.py](slm_catalogo_qwen.py)
comparte una consulta si varias
políticas llegan al mismo prefijo y deja de consultar por condición después de su
primer aviso. El SLM recibe los puntajes como indicios falibles, no como hechos.

En las 20 conversaciones de informe, usando la regla con umbral elegido en selección:

| Ventana | Compuerta Tito | Estafas con alerta del SLM | Legítimas con alerta del SLM |
|---|---|---:|---:|
| 4 líneas | No | 6/10 | 2/10 |
| 4 líneas | Sí | 2/10 | 0/10 |
| Acumulada | No | 3/10 | 1/10 |
| Acumulada | Sí | 2/10 | 0/10 |

Se realizaron 73 consultas compartidas y todas devolvieron una respuesta válida.
La mediana por consulta al SLM fue 290 ms y el p95, 603 ms; no son la latencia
total del sistema ni incluyen audio. Sin umbral, cuatro líneas sin Tito alertó
en 6/10 estafas y 3/10 legítimas; las otras tres filas conservaron sus conteos.
No se ejecutó el SLM directo como comparador en esta corrida y no corresponde
atribuir la diferencia a un solo componente. Son resultados sobre un informe de
desarrollo pequeño y sin revisión humana de referencias.
