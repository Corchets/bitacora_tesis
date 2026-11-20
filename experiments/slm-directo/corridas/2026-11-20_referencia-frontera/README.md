# #174, referencia: el detector con un modelo de frontera por API

> **Estado: propuesta sin discutir.** Escrito el 2026-11-20, antes de correr. Es una referencia para la defensa, no un
> candidato: no cambia la configuración ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)).

## Por qué

En la defensa pueden preguntar por qué no usar un modelo grande por API. Esta pasada mide cuánto de la detección se
pierde por correr Gemma 4 E2B en el teléfono, y cuánto tarda y cuesta la alternativa
([#174](https://github.com/Corchets/bitacora_tesis/issues/174)).

## Qué corre

- **Modelo:** `gpt-6.1-terra` de OpenAI, elegido por Mateo el 2026-11-20 entre los rápidos (tiene créditos de OpenAI).
  `reasoning.effort` en `none`: sin razonamiento previo, como E2B.
- **El mismo pedido que el detector:** el prompt de `c-consejos-corte-riesgo` como mensaje de sistema, el mismo mensaje
  de usuario (transcripción numerada con roles, `armar_mensaje_usuario`) y el mismo esquema JSON (`ESQUEMA_SALIDA`)
  como salida estructurada.
- **El corte tras el riesgo:** `max_output_tokens` 16, para que la respuesta termine poco después de
  `"riesgo": …,`. El riesgo se lee con `leer_riesgo_cortado`, igual que en el teléfono. Si el modelo no llega a la
  coma, la línea es inválida y no avisa. No se pide el motivo (la segunda consulta): no cambia la detección.
- **Temperatura 0** si la API la acepta con este modelo; si la rechaza, corre con el muestreo por defecto y se anota.
- **Casos:** solo desarrollo, la vista principal [`alcance-140`](../../casos/listas/alcance-140.txt): 46 estafas y 94
  legítimas generadas, sin datos personales. **No se manda a la API** la reserva de test, el set coreano de #144 ni las
  legítimas reales de CallCenterEN: sus fuentes no permiten redistribuir y esto no elige nada.
- **Consulta en todas las líneas de OTRA** (1.313), sin cortar en el primer aviso, una por vez y en orden. Así se
  aplica la misma regla que en la [exploración del 2026-11-20](../2026-11-20_exploracion-reales/README.md).
- **Una sola pasada.** Si una consulta falla por red o por límite de la API, se reintenta; la latencia que cuenta es
  la del intento que respondió, y los reintentos se anotan.
- **La clave** se lee de un archivo fuera del repositorio y no se imprime ni se guarda.

## Qué se mide y cómo se lee

**Detección,** con la regla del detector: aviso en la primera línea de OTRA con «riesgo ≥ 0,3»; las líneas inválidas no
avisan. Las cifras son las de la evaluación final (`exitos` de
[`2026-11-12_evaluacion-final/analizar.py`](../2026-11-12_evaluacion-final/analizar.py)) y la regla, la de
[`2026-11-20_exploracion-reales/analizar.py`](../2026-11-20_exploracion-reales/analizar.py) (`riesgos` y
`primer_aviso`), sin copiarlas.

**Contra qué:** E2B con la misma configuración en la corrida del 2026-11-20
([análisis](../2026-11-20_exploracion-reales/analisis.md)), sobre los mismos 140:

| | estafas avisadas | antes del pedido | a tiempo | antes del cumplimiento | FA | FA estrictas |
|---|---|---|---|---|---|---|
| E2B, `c-consejos-corte-riesgo` | 43/46 | 18/36 | 29/36 | 14/15 | 20/94 | 8/75 |

Las FA estrictas son las de las 75 legítimas que no deberían avisar según las
[etiquetas de producto](../2026-11-10_revision-producto/etiquetas-producto.json).

**Cómo se lee, escrito antes:**
- **Una diferencia de 3 casos o menos no se le atribuye al modelo** (H13: es lo que varía E2B entre dos sesiones).
- **Si el modelo grande avisa más estafas a tiempo sin más FA,** eso es lo que cuesta correr local. Si avisa parecido,
  el límite no es el tamaño del modelo sino la tarea o el prompt, que se escribió y ajustó para E2B.
- **El prompt es el de E2B.** No se ajusta para este modelo: un resultado peor no dice que el modelo sea peor, dice que
  el prompt no le sirve igual.
- **Es una sola pasada, sobre datos generados y de desarrollo,** sobre los que el prompt ya se ajustó. No es un test.
- Aparte, solo para mirar: qué valores de riesgo escribe, y las cifras con «riesgo ≥ 0,5» y «≥ 0,7».

**Latencia** por consulta: mediana y p95 del tiempo de pared de cada pedido, desde esta Mac, con la conexión anotada
(`networkQuality` de macOS antes de correr). En el teléfono el detector tarda 3,60 s de mediana y 4,90 s de p95 por
línea de OTRA ([a56-congelada-latencia](../2026-11-10_a56-congelada-latencia/README.md)). La comparación es de órdenes
de magnitud: una conexión de oficina no es la de un celular en la calle.

**Costo** por consulta y por llamada, con los tokens que informa la API (entrada, entrada en caché y salida) y los
precios del 2026-11-20 de [developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing):
US$ 1 por millón de tokens de entrada, US$ 0,05 en caché y US$ 5 de salida. Estimado antes de correr: entre US$ 1 y 2
en total.

## Cómo correr

Desde `experiments/slm-directo/corridas/2026-11-20_referencia-frontera/`, con la clave en un archivo fuera del
repositorio:

```bash
python3 -I referencia.py correr --clave ~/.config/bitacora/openai-key
```

```bash
python3 -I referencia.py analizar > analisis-salida.md
```

`correr` arma desarrollo en un directorio temporal (`conjuntos.preparar_desarrollo`), escribe `resultados.csv` y
`manifiesto.json` acá y, si se corta, sigue desde la última línea escrita. `analizar` no llama a la API.
