# «Riesgo primero»: ¿baja la latencia si el SLM escribe solo el riesgo?

> **Estado: propuesta sin discutir.** Ensayo de desarrollo de Evaristo sobre
> [#50](https://github.com/Corchets/bitacora_tesis/issues/50). No elige modelo
> ([D09](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)) ni cierra la
> política de alerta ([D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)).

> **Aviso (2026-10-30, rama `reranker-prueba`).** `rapida-20` son exactamente las 20
> conversaciones de `comparacion_20` de Ignacio (#101, `PARTICIONES-TITO-2026-10-29.json`), que
> no se usan para elegir. Las políticas de abajo se eligieron mirando esas 20: valen como
> **resultado sobre el set de informe**, no como selección. Para elegir, correr riesgo primero
> con `--lista seleccion-57 --seguir-tras-aviso` y usar
> [`../2026-10-30-reranker-zero-shot/analizar.py`](../2026-10-30-reranker-zero-shot/README.md).
> Desde el merge con `laboratorio-main`, `correr.py` corta en el primer aviso salvo con
> `--seguir-tras-aviso`, y `acumular.py` rechaza corridas cortadas.

## Pregunta

Con los prompts `tarea` y `v2`, el SLM escribe en cada línea un JSON de ~40 tokens
(evidencia, alerta, riesgo, motivo). Con la caché del prefijo funcionando, escribir es lo
que domina el tiempo ([caché de prefijo](../2026-10-21-cache-prefijo/README.md)). Las
preguntas:

1. Si el modelo escribe **primero y solamente el riesgo** (`{"riesgo": 0.35}`, ~8 tokens) y
   sigue escribiendo solo cuando el riesgo supera 0,6, ¿cuánto baja el tiempo por línea y por
   llamada?
2. ¿Cuánta calidad se pierde frente al `v2`, que pide la cita **antes** de decidir?
3. ¿Ayuda **acumular el puntaje** entre líneas (idea de Mateo)? Una línea sola puede no ser
   riesgosa y dos o tres juntas sí. El contexto ya se acumula: el modelo recibe toda la
   transcripción en cada línea. Lo que se prueba acá es la acumulación en la política de aviso.

## Cómo funciona

- **Etapa 1:** prompt [`riesgo.txt`](../../prompts/riesgo.txt) con la escala anclada (0–0,3
  charla normal; 0,31–0,6 señales sin pedido; > 0,6 pedido) y esquema `{"riesgo"}`, con
  `num_predict` 24. Si riesgo ≤ 0,6, la línea termina ahí.
- **Etapa 2** (solo si riesgo > 0,6): los mismos mensajes, más la respuesta de la etapa 1
  como `assistant` y el pedido [`riesgo_motivo.txt`](../../prompts/riesgo_motivo.txt) con
  esquema `{evidencia, motivo}`. Como el comienzo es idéntico, Ollama no vuelve a leer la
  transcripción. Si la etapa 2 falla, la alerta se mantiene y el error queda como `etapa2_*`.
- `actualizaciones.csv` agrega `ms_etapa1`, `ms_etapa2`, `tokens_prompt_etapa2`,
  `tokens_salida_etapa2` y `crudo_etapa2`; `ms` es la suma de las dos etapas.

## Cómo correrlo (notebook Windows, solo CPU)

Desde `experiments/slm-directo`:

```
ollama pull gemma3n:e2b
python correr.py --modelos gemma3n:e2b --prompts riesgo --solo-cpu --num-batch 32 --sin-reglas --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01 --detalle
python correr.py --modelos gemma3n:e2b --prompts riesgo --solo-cpu --num-batch 32 --sin-reglas --etiqueta win-gemma3n-e2b-riesgo-cpu --seguir-tras-aviso
python correr.py --modelos gemma3n:e2b --prompts v2 --solo-cpu --num-batch 32 --sin-reglas --etiqueta win-gemma3n-e2b-v2-cpu --seguir-tras-aviso
python analisis/2026-10-29-riesgo-primero/acumular.py corridas/<carpeta-riesgo> corridas/<carpeta-v2>
```

1. **Prueba rápida** (2 casos, `--detalle`): la etapa 1 tiene que tardar poco, y la etapa 2
   tiene que aparecer solo en la línea donde piden el código.
2. **Corridas completas:** 150 casos de desarrollo, primero `riesgo` y después la línea base
   `v2`, en la misma máquina. En CPU puede tardar varias horas; si se corta con Ctrl+C, lo procesado queda
   guardado y `acumular.py` usa los casos completos.
3. **`acumular.py`** escribe `acumular.md` con dos cosas:
   - **latencia por config:** ms por línea p50/p95, etapa 1, etapa 2, tokens y ms por llamada;
   - **políticas:** umbral simple, k líneas seguidas, media de las últimas w y EMA (suma con
     olvido), con τ de 0,5 a 0,9, contra la meta del tutor (≥ 80 % de estafas con aviso sobre
     todas, ≤ 15 % de falsas alarmas).

   La mejor política se elige en la mitad A y se informa en la B.

**Set rápido (`--lista rapida-20`).** Son 20 conversaciones de corpus_v2 elegidas por
Evaristo (10 estafas y 10 legítimas, ~524 líneas, [`casos/listas/rapida-20.txt`](../../casos/listas/rapida-20.txt)).
Con `riesgo` tarda unos 20 min por modelo en CPU. Sirve para comparar modelos entre sí; no
para medir la meta: cada caso mueve los porcentajes 10 puntos, y las mitades A/B tienen 10 casos.

```
python correr.py --modelos gemma3n:e2b --prompts riesgo,v2 --lista rapida-20 --solo-cpu --num-batch 32 --sin-reglas --etiqueta rapida-gemma3n-e2b
```

Otros modelos para después: `qwen3.5:4b`, `qwen3.5:2b`, `gemma2:2b`, `gemma3:270m`,
`gemma3:1b`, `gemma3:4b`, `gemma3n:e4b`. Se usan los mismos comandos, siempre en la misma máquina.

## Resultados

### 2026-10-29 · `gemma3n:e2b` · set rápido (20 casos) · notebook de Evaristo, solo CPU

Corrida [`2026-10-29_182016_rapida-gemma3n-e2b`](../../corridas/2026-10-29_182016_rapida-gemma3n-e2b/resumen.md)
(Windows 11, 8 núcleos, 15,7 GB, Ollama 0.40.13), tablas completas en [`acumular.md`](acumular.md).
Son 20 casos: cada uno mueve los porcentajes 10 puntos.

**Tiempo.**

| | `v2` (JSON completo) | `riesgo` (dos etapas) | |
|---|---|---|---|
| ms por línea, p50 / p95 | 10 036 / 13 576 | 1 918 / 2 297 | **5,2× más rápido** |
| Tokens de salida por línea, p50 | 92 | 11 | |
| Primera línea de cada caso, p50 | 7 266 | 2 033 | |
| ms por llamada, p50 | 259 056 | 53 088 | |
| Demora del aviso, p50 (línea del aviso) | 9 790 | 8 466 (etapa 1 ~1,9 s + etapa 2 ~6,6 s) | casi igual |

- El salto está en las líneas sin aviso, que son casi todas. Con `v2`, cada línea tarda ~10 s,
  más de lo que dura una frase: el detector se atrasa respecto de la llamada. Con `riesgo`
  queda en ~2 s y puede seguirla.
- El aviso en sí tarda casi lo mismo, porque la etapa 2 (evidencia y motivo) escribe ~60
  tokens. La alerta podría mostrarse apenas termina la etapa 1 (~2 s) y completar el motivo
  después: esto no se probó todavía.

**Calidad** (estafas con aviso / falsas alarmas sobre 10 y 10):

| Política | `v2` | `riesgo` |
|---|---|---|
| Alerta del modelo / umbral > 0,6 (la de la corrida) | 10 / 9 | 10 / 6 |
| Umbral > 0,7 | 10 / 9 | 10 / 3 |
| 2 seguidas > 0,7 | 10 / 8 | 9 / 2 |
| EMA 0,3 > 0,7 | 10 / 7 | 8 / 1 (única ✔ meta 80/15) |
| 2 seguidas > 0,8 | 10 / 3 | 1 / 0 |

- `riesgo` no perdió estafas frente a `v2` con umbral 0,6 o 0,7, y tuvo menos falsas alarmas.
  Con `v2`, 9 de cada 10 legítimas dieron falsa alarma: con este modelo es una línea base débil.
- Con `riesgo` el modelo usa pocos valores (0,75 aparece en 103 de 524 líneas) y casi nunca
  pasa de 0,8: los umbrales ≥ 0,8 casi no avisan. En las estafas, una vez que aparece el
  pedido el riesgo se queda en 0,75 hasta el final; en varias legítimas sube a 0,65–0,75 unas
  pocas líneas y vuelve a bajar. Por eso acumular (k seguidas, EMA) baja las falsas alarmas.
- La elección hecha en la mitad A (EMA 0,3 > 0,6) dio 5/5 estafas y 3/5 falsas alarmas en la B:
  con 10 casos por mitad la elección no es estable. Hay que confirmarlo con los 150.
- Falsas alarmas de `riesgo` (motivo de la etapa 2): firma al recibir un paquete, traer un
  informe médico, número de trámite «sin datos de acceso», nombre del consultorio y letras del
  correo, código impreso en un resumen de tarjeta. Son pedidos de datos comunes, no de claves
  ni de dinero.

**Para seguir.** (1) Correr los 150 casos con `riesgo` y la política ganadora acá (umbral > 0,7
o EMA 0,3 > 0,7); (2) probar mostrar la alerta al final de la etapa 1; (3) probar otros
modelos con `--lista rapida-20`. Ajustar el prompt mirando estas falsas alarmas sería
afinar sobre desarrollo: si se hace, se registra en `prompts/README.md` y se mide en casos
que no se usaron para ajustarlo.

## Límites

- `riesgo` no está calibrado: es el número que escribe el modelo, no una probabilidad.
- Todo es desarrollo: elegir la política mirando estos 150 casos es optimista. La
  evaluación final va sobre el test reservado, después de D08.
- La etapa 2 corre una sola vez por llamada, en la primera línea con riesgo > 0,6. Si una política
  avisa en otra línea (o con τ < 0,6), la demora del aviso usa la mediana de la etapa 2.
