# Reranker zero-shot: ¿solo, filtro o verificador, y con qué política?

> **Estado: propuesta sin discutir.** Ensayo de desarrollo de Evaristo (rama `reranker-prueba`),
> relacionado con [#51](https://github.com/Corchets/bitacora_tesis/issues/51) y el riesgo R07.
> No elige detector ([D09](../../../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector)),
> no cierra la política de alerta ([D08](../../../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental))
> y no toca Tito ni la matriz #101. Hipótesis y regla de decisión escritas **antes** de correr.

## Pregunta

Nadie del equipo probó un cross-encoder, un reranker o un modelo NLI como detector. Un
modelo así lee juntas la ventana de la llamada y la descripción de un pedido («una de las
personas le pide a la otra el código…») y da un puntaje, en una sola pasada y sin
generar texto. Las preguntas:

1. ¿Alcanza solo, sin SLM, con la meta del tutor (≥ 80 % de estafas con aviso, ≤ 15 % de FA)?
2. ¿Sirve como **verificador** del SLM contra las falsas alarmas por palabra suelta (R07)?
   En particular, ¿puede reemplazar la etapa 2 de «riesgo primero» (≈ 6,6 s)?
3. ¿Sirve como **filtro** antes del SLM, en el lugar de Tito?
4. ¿Ayuda **acumular el puntaje** (idea de Mateo: k seguidas, media, EMA) sobre su
   puntaje continuo, y a qué costo de anticipación?
5. ¿Vale la pena entrenarlo?

## Hipótesis

| # | Hipótesis | Si se cumple |
|---|---|---|
| H1 | `bge-reranker-v2-m3` mide **tema**, no intención: FA R07 ≥ reglas v2 | Se descarta como zero-shot |
| H2 | El NLI (`mDeBERTa-xnli`) separa «te pido el código» de «nunca te lo pedimos» mejor que bge y reglas, pero pierde pedidos indirectos o partidos | Solo no llega a la meta |
| H3 | Acumular (EMA, k seguidas) baja la FA R07 del NLI más que el umbral simple, con avisos antes de `T_C` | La política de Mateo queda justificada |
| H4 | «SLM ∧ NLI» baja las FA del SLM al menos un tercio, perdiendo ≤ 1 estafa | Componente final: verificador |
| H5 | Riesgo primero (etapa 1) ∧ NLI: aviso listo en ~2–3 s en vez de ~8,5 s, con menos FA que riesgo primero solo | Arquitectura candidata |
| H6 | NLI (pedidos + maniobras) como filtro evita ≥ 30 % de consultas al SLM sin perder estafas | Alternativa a Tito, a discutir con Ignacio |
| H7 | Entrenar no rinde: ≲ 12 líneas de pedido en la partición de entrenamiento, 8–10 días para generar datos por turno, solo CPU | Descarte del entrenamiento |
| H8 | En CPU, 12 pares por línea: p95 < 1,5 s; mDeBERTa < 0,5 s | Argumento de costo |

**Regla de decisión** (se elige en selección, se informa en `comparacion_20`):

1. A llega a la meta → el reranker reemplaza al SLM.
2. Si no, H5 o H4 → «SLM (riesgo primero) + verificador NLI + política acumulada» a D09.
3. Si no, H6 → alternativa a Tito.
4. Si no → se descarta la familia cross-encoder con esta evidencia.

## Qué se compara y sobre qué casos

- **Selección** (se elige acá): particiones entrenamiento + validacion + diagnostico + regresion
  de [`PARTICIONES-TITO-2026-10-29.json`](../../PARTICIONES-TITO-2026-10-29.json): 57 casos,
  19 estafas y 38 legítimas. Lista [`seleccion-57`](../../casos/listas/seleccion-57.txt).
- **Informe** (no se elige acá): `comparacion_20`, las mismas 20 de #101 y de
  [`rapida-20`](../../casos/listas/rapida-20.txt). `analizar.py` se detiene si la selección
  toca el informe o sus casos relacionados (`excluido_relacion_comparacion`).
- **Roles:** A = cada detector solo; C/H5 = SLM ∧ reranker en la misma línea; B = el reranker
  deriva y después decide el SLM (sin el bloque de indicio de #68: es una aproximación).
- **Políticas:** umbral, 2 seguidas, media 3, EMA 0,3 y EMA 0,5. Para SLM, τ de 0,3 a 0,95; para el reranker,
  τ de 0,01 a 0,9, porque bge puntúa en escala baja. La
  grilla es corta a propósito: con 19 estafas para elegir, una grilla grande sobreajusta.
- **Elección:** mayor recall con FA ≤ 15 % en selección; empate: menos FA y aviso más temprano.
- **Se informa:** estafas y FA con IC de Wilson, FA en legítimas R07 (difíciles, mención sin
  pedido, pedido razonable), avisos antes/en el pedido y en/después del cumplimiento, AUROC
  por conversación, acierto del tipo de pedido en `T_R`, ms por línea y consultas evitadas.

## Modelos

| Backend | Modelo | Cómo puntúa |
|---|---|---|
| `nli` | `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7` | P(entailment) sobre las 3 clases; premisa = ventana |
| `cross-encoder` | `BAAI/bge-reranker-v2-m3` | sigmoide del logit; consulta = descripción, pasaje = ventana |
| `qwen3-reranker` | `Qwen/Qwen3-Reranker-0.6B` | P("yes") con la instrucción de [`hipotesis_reranker.json`](../../prompts/hipotesis_reranker.json) |

Antes de correr, verificar en Hugging Face la licencia de cada uno y, para Qwen3-Reranker, que
el formato del prompt de [`reranker.py`](../../reranker.py) coincida con su ficha. La revisión
usada queda en el manifiesto. Descripciones: 6 pedidos × 2 paráfrasis, sin asumir quién es el
atacante; las 6 maniobras solo con `--reranker-etiquetas todas`. Ventana: últimas 4 líneas con
A/B, recortada por la izquierda a 384 tokens.

## Cómo correrlo (notebook, solo CPU)

Desde `experiments/slm-directo`, una sola vez:

```
python -m venv .venv-reranker
.venv-reranker\Scripts\activate
pip install -r requirements-reranker.txt
```

(En Linux o macOS se activa con `source .venv-reranker/bin/activate`.)

**0. Humo** (2 casos, baja el modelo la primera vez):

```
python correr.py --solo-reranker --reranker MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7 --casos SC-WA-CODE-01-e01,LG-WA-CONSULTA-01-e01 --seguir-tras-aviso --hilos 4 --detalle
```

Mirar los ms por línea: con eso se estima cuánto tarda el resto.

**R1. bge-reranker, pedidos** (77 casos, ~1.860 líneas; de noche). El NLI quedó descartado en
el diagnóstico y Qwen3-Reranker se suma después si termina de bajar:

```
python correr.py --solo-reranker --reranker BAAI/bge-reranker-v2-m3 --lista seleccion-57,rapida-20 --seguir-tras-aviso --hilos 4 --etiqueta r1-bge
```

Qwen3-Reranker (opcional; `pip install hf_xet` acelera la descarga, que retoma donde se cortó):

```
python correr.py --solo-reranker --reranker Qwen/Qwen3-Reranker-0.6B --lista seleccion-57,rapida-20 --seguir-tras-aviso --hilos 4 --etiqueta r1-qwen
```

**R2. El mejor de R1 con pedidos y maniobras** (para el rol filtro):

```
python correr.py --solo-reranker --reranker <el mejor de R1> --reranker-etiquetas todas --lista seleccion-57,rapida-20 --seguir-tras-aviso --hilos 4 --etiqueta r2-todas
```

**R3. Riesgo primero sobre la selección** (Ollama, ~30 min). La corrida sobre `rapida-20`
ya existe (`2026-10-29_182016_rapida-gemma3n-e2b`) y queda como informe:

```
python correr.py --modelos gemma3n:e2b --prompts riesgo --lista seleccion-57 --solo-cpu --num-batch 32 --sin-reglas --seguir-tras-aviso --etiqueta r3-riesgo-seleccion
```

**R4. Costo con otros hilos** (un proceso por valor, así el pico de memoria es de ese modelo):

```
python correr.py --solo-reranker --reranker <el mejor> --lista rapida-20 --seguir-tras-aviso --hilos 2 --etiqueta r4-hilos2
python correr.py --solo-reranker --reranker <el mejor> --lista rapida-20 --seguir-tras-aviso --hilos 8 --etiqueta r4-hilos8
```

**Análisis** (no corre modelos; se puede repetir cuantas veces haga falta):

```
python analisis/2026-10-30-reranker-zero-shot/analizar.py corridas/<r1> corridas/<r2> corridas/<r3> corridas/2026-10-29_182016_rapida-gemma3n-e2b corridas/2026-10-21_201914_m1-reglas-v2-150 corridas/2026-10-21_201039_m1-2b-v1v2-nb32 corridas/2026-10-23_144554_linux-4b-v1v2-cv2-nb32 corridas/2026-10-23_115920_linux-9b-v1v2-cv2-nb32
```

Escribe `analisis.md` en esta carpeta. Las corridas de Qwen 4B y 9B solo cubren 23 de los 57
casos de selección (las de corpus v2): sus filas lo dicen y no se comparan con las de 57.

## Compuerta de entrenamiento (se decide con `analisis.md`)

Se entrena solo si se cumplen las tres:

1. El mejor zero-shot ordena bien (AUROC por conversación ≥ 0,80 en selección) pero no llega
   a la meta con ninguna política, o falla justo en R07.
2. Los pares salen en ≤ medio día de datos que ya existen en la partición `entrenamiento`
   (líneas `pedido` como positivos, `mencion` como negativos difíciles).
3. Hay GPU (Colab o Kaggle).

Si falla alguna, el entrenamiento queda descartado con H7 como fundamento.

## Límites

- Todo es desarrollo y sin revisión humana. Elegir sobre 57 casos es optimista: el número de la
  tesis sale del test reservado, después de D08.
- El puntaje de un reranker no es una probabilidad calibrada; el umbral se elige con datos.
- El rol filtro es una aproximación: en el flujo real de #68 el SLM recibe además el indicio.
- Medir en una notebook no prueba que corra en un teléfono.

## Resultados

### 2026-10-30 · Humo y diagnóstico del NLI (notebook de Evaristo, Windows, CPU, 4 hilos)

Con `torch 2.9.1+cpu`, `transformers 4.51.3` y `MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7`.

- **Humo** sobre `SC-WA-CODE-01-e01` y `LG-WA-CONSULTA-01-e01`, que están en
  `excluido_relacion_comparacion`: solo sirvieron para ver que corre, no para ajustar.
  - Con la primera versión el riesgo daba ~0,99 en todas las líneas: el puntaje comparaba
    entailment solo contra contradicción. Corregido (P(entailment) sobre las tres clases).
  - Con el arreglo siguió alto: entre 0,74 y 0,99 en todas las líneas, también en la legítima.
  - Cada línea (12 pares) tardó entre 0,9 y 2,1 s. H8 esperaba < 0,5 s para mDeBERTa.
- **Instalación** ([`diagnostico_nli.py`](diagnostico_nli.py)): sana. Los tokenizadores rápido y
  lento dan lo mismo. En frases cortas en castellano acierta:
  - «Decime el código…» frente a «Alguien pide un código»: entailment 1,00.
  - Una frase sobre la lluvia: neutral 0,99.
  - «No hace falta que me digas ningún código»: contradicción 0,95.
- **Formato** (`--formato`): 6 frases **inventadas**, 2 con pedido y 4 sin pedido, contra
  hipótesis corta, media y larga (la v1), con y sin «A:». **Ninguna combinación pasa de 4/6.**
  - Confunde mención con pedido: «Me mandaron un código… no se lo voy a dar a nadie» da 0,99
    con la hipótesis corta. Es la falla de R07.
  - Con hipótesis largas da entailment a charla cualquiera: «¿Ya cenaste?…» da 0,95–0,98, y
    una presentación de banco, 0,97.
  - Con la hipótesis larga pierde pedidos claros: «Leeme el código de seis dígitos» da 0,04–0,06.
- **Conclusión:** H2 se refuta en controles. El NLI zero-shot queda **descartado** como
  detector solo y como verificador anti-R07, por la regla escrita antes de correr: si ninguna
  combinación supera 4/6, se descarta. R1 sigue con `bge-reranker-v2-m3` y
  `Qwen3-Reranker-0.6B`, después de pasar el mismo diagnóstico de formato.

### 2026-10-30 · Diagnóstico de formato de bge-reranker y Qwen3-Reranker

Mismas 6 frases inventadas (2 con pedido, 4 sin pedido), hipótesis corta, media y larga, con y sin «A:».

- **`BAAI/bge-reranker-v2-m3`: separa en las 6 combinaciones.** En todas, el pedido con menor
  puntaje queda por encima de la frase sin pedido con mayor puntaje:

  | Hipótesis | Pedido más bajo | Sin pedido más alto |
  |---|---|---|
  | corta (con / sin «A:») | 0,01 / 0,01 | 0,00 / 0,00 |
  | media (con / sin «A:») | 0,05 / 0,08 | 0,00 / 0,00 |
  | larga v1 (con / sin «A:») | **0,12** / 0,30 | **0,01** / 0,00 |

  - La mención R07 («Me mandaron un código… no se lo voy a dar a nadie») da 0,00–0,01, y la
    advertencia «Nunca le des a nadie el código» da 0,00. **H1 queda refutada en controles:**
    bge no confunde mención con pedido.
  - La escala es baja: con umbral 0,5 acierta 4/6–5/6 solo porque los pedidos quedan debajo de 0,5.
    Por eso el análisis usa τ desde 0,01.
  - Se mantiene el formato pre-registrado (larga v1 con «A:»): también separa, y no se ajusta
    nada sobre 6 frases.
- **`Qwen/Qwen3-Reranker-0.6B`: no evaluado todavía.** La descarga se cortó al 13 % (265 kB/s) y
  transformers no encontró el `.safetensors`. No es un error del código.

Pendiente: correr R1–R4 y pegar acá lo principal de `analisis.md`.
