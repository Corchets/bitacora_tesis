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
- **Casos, en este orden** (si la corrida se corta, quedan las primeras tandas completas):
  1. desarrollo, la vista principal [`alcance-140`](../../casos/listas/alcance-140.txt): 46 estafas y 94 legítimas
     generadas (1.313 consultas);
  2. las 33 legítimas reales de telecomunicaciones de CallCenterEN
     ([`set-legitimas`](../../casos/externo/legitimas-reales/set-legitimas/), 387 consultas);
  3. las 33 estafas reales coreanas de #144 ([`coreano`](../../casos/externo/coreano/), 4.193 consultas);
  4. la zona gris de Medicare ([`set-zona-gris`](../../casos/externo/legitimas-reales/set-zona-gris/), 42 llamadas,
     1.139 consultas): avisos que no son FA.
- **Cambio de alcance del 2026-11-20:** al principio iba solo desarrollo, porque las fuentes de las coreanas y de
  CallCenterEN no permiten redistribuir. Mateo decidió ese día mandarlas a la API: «es info publica que encontramos en
  internet». **La reserva de test sigue afuera:** no se manda ni se lee.
- **Recorte para gastar poco** (Mateo, 2026-11-20: no hay créditos de sobra). Se consulta una línea de OTRA por vez,
  en orden:
  - **desarrollo:** todas sus líneas de OTRA (1.313), sin cortar en el aviso, para mirar también otros cortes;
  - **legítimas reales, coreanas y zona gris:** se corta en el primer aviso, como el detector en el teléfono. Para
    avisar o no avisar alcanza;
  - **coreanas:** además, solo hasta la línea del pedido (`T_R`), o hasta la 60 en las 6 que no tienen `T_R`. Un
    aviso después del pedido no cuenta como a tiempo, así que «antes del pedido» y «a tiempo» no cambian. «Estafas
    avisadas» pasa a ser «avisadas antes del pedido o de la línea 60», y así se lee.
- **El modelo ve todo lo que se le manda.** E2B corre con `num_ctx` 4096: en las coreanas, 2.359 de sus 4.193 líneas
  de OTRA fueron inválidas por contexto excedido, pero E2B avisó todas antes de eso. Se mira también el aviso dentro
  de las primeras 12 consultas, que iguala el largo entre coreanas y legítimas reales.
- **Una sola pasada.** Si una consulta falla por red o por límite de la API, se reintenta; la latencia que cuenta es
  la del intento que respondió, y los reintentos se anotan.
- **La clave** se lee de un archivo fuera del repositorio y no se imprime ni se guarda.

## Qué se mide y cómo se lee

**Detección,** con la regla del detector: aviso en la primera línea de OTRA con «riesgo ≥ 0,3»; las líneas inválidas no
avisan. Las cifras son las de la evaluación final (`exitos` de
[`2026-11-12_evaluacion-final/analizar.py`](../2026-11-12_evaluacion-final/analizar.py)) y la regla, la de
[`2026-11-20_exploracion-reales/analizar.py`](../2026-11-20_exploracion-reales/analizar.py) (`riesgos` y
`primer_aviso`), sin copiarlas.

**Contra qué:** E2B con la misma configuración (`base` con el primer aviso) en la corrida del 2026-11-20
([análisis](../2026-11-20_exploracion-reales/analisis.md)), sobre los mismos casos:

| E2B, `c-consejos-corte-riesgo` | estafas avisadas | antes del pedido | a tiempo | antes del cumplimiento | FA o avisos | FA estrictas |
|---|---|---|---|---|---|---|
| Desarrollo (alcance-140) | 43/46 | 18/36 | 29/36 | 14/15 | 20/94 | 8/75 |
| Legítimas reales (33) | — | — | — | — | 23/33 | — |
| Coreanas (33) | 33/33 | 25/27 | 27/27 | 16/16 | — | — |
| Zona gris (42), avisos | — | — | — | — | 30/42 | — |

Las FA estrictas son las de las 75 legítimas que no deberían avisar según las
[etiquetas de producto](../2026-11-10_revision-producto/etiquetas-producto.json).

**Cómo se lee, escrito antes:**
- **Una diferencia de 3 casos o menos no se le atribuye al modelo** (H13: es lo que varía E2B entre dos sesiones).
- **Si el modelo grande avisa más estafas a tiempo sin más FA,** eso es lo que cuesta correr local. Si avisa parecido,
  el límite no es el tamaño del modelo sino la tarea o el prompt, que se escribió y ajustó para E2B.
- **La pregunta central es la de las legítimas reales:** si un modelo grande con el mismo prompt también avisa en las
  llamadas reales de call center (E2B: 23 de 33), las FA vienen de la tarea tal como está planteada, no del tamaño.
  Si baja a la mitad o menos sin perder coreanas, es una pérdida atribuible a correr local.
- **El prompt es el de E2B.** No se ajusta para este modelo: un resultado peor no dice que el modelo sea peor, dice que
  el prompt no le sirve igual.
- **Es una sola pasada.** Desarrollo es donde se ajustó el prompt; las coreanas y las legítimas reales ya se usaron
  para elegir en la exploración. Nada de esto es un test.
- Aparte, solo para mirar: qué valores de riesgo escribe y, en desarrollo, las cifras con «riesgo ≥ 0,5» y «≥ 0,7».

**Latencia** por consulta: mediana y p95 del tiempo de pared de cada pedido, desde esta Mac, con la conexión anotada
(`networkQuality` de macOS antes de correr). En el teléfono el detector tarda 3,60 s de mediana y 4,90 s de p95 por
línea de OTRA ([a56-congelada-latencia](../2026-11-10_a56-congelada-latencia/README.md)). La comparación es de órdenes
de magnitud: una conexión de oficina no es la de un celular en la calle.

**Costo** por consulta y por llamada, con los tokens que informa la API (entrada, entrada en caché y salida) y los
precios del 2026-11-20 de [developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing):
US$ 1 por millón de tokens de entrada, US$ 0,05 en caché y US$ 5 de salida.

**Estimado antes de correr,** con el recorte (caracteres contados sobre los pedidos, unos 3,3 por token):
- **Tope, si el modelo no avisara nunca:** 10,8 M de tokens de entrada (desarrollo 1,5; legítimas reales 0,6;
  coreanas 6,6; zona gris 2,1), unos US$ 11 sin caché y unos US$ 3 con la caché automática del prefijo, que comparten
  las consultas sucesivas de una misma llamada.
- **Lo esperable:** si avisa en las coreanas tan temprano como E2B (en la línea 6), casi todo el costo es desarrollo:
  entre US$ 1 y 3 en total. Entre 30 minutos y 1 hora.

## Cómo correr

Lo corre Ignacio (2026-11-20), con su clave de OpenAI. Hace falta Python 3.10 o más nuevo, sin paquetes extra. Desde
esta carpeta (`experiments/slm-directo/corridas/2026-11-20_referencia-frontera/`), en la rama
`exp/174-referencia-frontera`:

```bash
export OPENAI_API_KEY='...'
```

```bash
python3 -I referencia.py correr
```

En Windows: `$env:OPENAI_API_KEY='...'` y `py -I referencia.py correr`. La clave no se escribe en ningún archivo del
repositorio; también sirve `--clave ARCHIVO` con un archivo fuera del repositorio.

- `correr` arma los conjuntos en un directorio temporal (`conjuntos.preparar_desarrollo`, `preparar_externo` y
  `preparar_legitimas_reales`, desde lo que ya está en el repositorio) y escribe `resultados.csv` y `manifiesto.json`
  acá. Cada 50 consultas avisa por pantalla.
- **Si se corta** (red, `Ctrl+C`, la máquina se duerme), se vuelve a correr el mismo comando: sigue desde la última
  línea escrita. No hay que borrar nada.
- **Si se acaban los créditos** o la API devuelve un error que no se reintenta, la línea queda inválida con el error en
  el CSV. Si son muchas, cortar con `Ctrl+C` y avisar.
- La conexión se mide sola con `networkQuality` en macOS; en otro sistema queda anotado que no se pudo, y conviene
  escribir a mano en el análisis cómo era la conexión (wifi o cable, y velocidad aproximada).

Cuando termina, sin API:

```bash
python3 -I referencia.py analizar > analisis-salida.md
```

y se commitean `resultados.csv`, `manifiesto.json` y `analisis-salida.md` en la misma rama. El `analisis.md`, con la
lectura, se escribe después a partir de esa salida.
