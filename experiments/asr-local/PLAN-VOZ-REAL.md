# Plan: mejorar el ASR con voz real (acento tucumano, jerga)

> **Estado: acordado con Luciano el 2026-10-26 (sesión de preguntas).** Issue [#94](https://github.com/Corchets/bitacora_tesis/issues/94), sub-issue de
> [#87](https://github.com/Corchets/bitacora_tesis/issues/87). No cierra
> [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector): son una o dos voces, sin piloto.
> No es requisito para la demo del 2026-10-28.

## 1. Problema

«El ASR no entiende muy bien lo que hablo»: acento, jerga y palabras de acá. Hasta hoy no se midió
con voz real: las corridas de [`corridas/`](corridas/) son todas TTS.

Lo que muestran las 6 grabaciones del panel del 2026-10-26 (`experiments/voip/llamadas/`, fuera de Git):
en `202750` la frase se corta a mitad de palabra («la de | sarro que», «Como los | .») y aparece una
repetición («hola, hola, hola…»). Hay más daño por corte y nivel que por jerga. «gaucho» posiblemente
era «guacho» o «guaso»: hipótesis sin referencia.

## 2. Criterio de éxito

- **Principal:** etiquetas de [`reglas.py`](../slm-directo/reglas.py) por frase. Se corren las reglas
  sobre el texto real y sobre la transcripción y se comparan las etiquetas. Mide lo que le llega al
  detector, con su tolerancia a un typo incluida. Detalle: recall por término de `PATRONES` e
  `_IMPERATIVOS`. Las listas se usan como instrumento; D07 sigue abierta.
- **Secundario (informativo, sin umbral):** recall de una lista de jerga, con atención al habla
  tucumana (sección 6). «luca» y «mango» pasan a la lista crítica porque son plata.
- **Además:** WER y CER con [`wer.py`](wer.py).

**Regla para quedarse con un paso**, medida en la toma 2:

1. acierta etiquetas en al menos 2 frases más que el paso anterior;
2. ninguna etiqueta nueva en las frases negativas;
3. la frase final no suma más de +0,3 s de demora;
4. el WER no empeora más de 2 puntos.

## 3. Set de referencia

- Grabado desde el panel con «Guardar» y «Lo que dije en realidad»
  ([#91](https://github.com/Corchets/bitacora_tesis/issues/91), hay que cerrarlo antes).
- Guion de 30 frases: 10 con términos críticos, 5 con números y montos, 5 con bancos y apps,
  5 espontáneas con jerga y 5 negativas parecidas («estoy cómodo», «me duele el codo», «pagó la luz»,
  «el número de la casa», «el link del cumple»). Está en [`voz-real/guion.json`](voz-real/guion.json) y la
  hoja de grabación en [`voz-real/HOJA-DE-GRABACION.md`](voz-real/HOJA-DE-GRABACION.md). Dos de esos ejemplos
  salieron: `reglas.py` busca `pago` y `link` como subcadena, así que «pagó la luz» y «el link del cumple»
  disparan etiquetas y no sirven de negativas; las cinco que quedaron dan cero etiquetas (lo comprueba
  `tests/test_guion.py`). Es un falso positivo de las reglas, no del ASR; sirve de antecedente cuando se discuta D07.
- **Dos tomas:** con la toma 1 se ajustan los hotwords y el diccionario; con la toma 2 se mide.
- **Condiciones:** Luciano por micrófono, Luciano por Meet y otra voz del equipo por Meet. Si no hay
  otra voz, alcanza con las dos de Luciano. La otra persona da su consentimiento (anotado en el issue)
  y el audio queda fuera de Git.

## 4. Orden de trabajo

1. Línea base: greedy actual sobre el set.
2. Lo barato: corte de silencio, `rule2`, umbral RMS y ganancia del micrófono.
3. Hotwords de sherpa (sección 5).
4. Diccionario de corrección sobre la frase final. Va último porque un reemplazo aproximado puede
   *inventar* un «código»: lo controlan las frases negativas.
5. Techo offline: `faster-whisper` `small` y `large-v3-turbo`, int8, en la M1, con y sin `hotwords`
   (términos críticos y jerga). Nada pasa al panel; si el techo sale mucho mejor, va en otro issue.

Fuera de alcance: convertir la variante Kroko ES 128-L de Banafo.

## 5. Hotwords en sherpa-onnx 1.13.8

- Requieren `decoding_method="modified_beam_search"`, `modeling_unit="bpe"` y un `bpe_vocab`
  ([documentación de sherpa](https://k2-fsa.github.io/sherpa/onnx/hotwords/index.html)).
- El modelo no trae `bpe.vocab` y el repositorio de
  [Banafo/Kroko-ASR](https://huggingface.co/Banafo/Kroko-ASR) no publica `bpe.model` (solo `.data`).
- **Verificado el 2026-10-26:** un `bpe.vocab` sintético armado desde `tokens.txt`
  (`token<TAB>-id`) carga y decodifica. Hay que revisar a mano cómo se parte en tokens cada hotword
  (`python hotwords.py`).
- **Desvío al implementar (2026-10-26):** con puntaje `-id` sherpa (ssentencepiece) elige el camino de menor
  suma de ids y parte casi todo en letras sueltas («transferencia» → `t r a n s f e r e n ci a`), que no es lo que
  el modelo emite. Contra lo que el modelo emite al reconocer 63 palabras sueltas (voz TTS de macOS), `-id` acierta
  6 y `-(ln(id+2)+3)` acierta las 63 (y 10 de 10 en frase). Por eso el `bpe.vocab` usa ese puntaje; `beam+hotwords-id`
  queda como variante para repetir lo del plan. Detalle en `hotwords.py`.
- En los hotwords entran solo términos críticos, bancos y apps. La jerga queda afuera: subirle el
  puntaje a palabras comunes aumenta las inserciones. Se escriben con las mayúsculas del modelo,
  que distingue mayúsculas y pone puntuación.
- `faster-whisper` tiene `hotwords` (no hace nada si se usa `prefix`) e `initial_prompt` (solo la
  primera ventana) ([`transcribe.py`](https://github.com/SYSTRAN/faster-whisper/blob/master/faster_whisper/transcribe.py)).

## 6. Habla tucumana (a revisar por Luciano)

Lista candidata, sin validar: chango/changa, ñaño/ñaña, guaso, mishi, al ñudo, sonso, yapa, zafar,
al vicio, «vo'» por «vos». En la pronunciación, la hipótesis es que pesan la /s/ final aspirada o
perdida («lo' código'») y la erre arrastrada. Si el modelo pierde el plural, a las reglas no les
afecta («codigo» igual dispara); que se pierda «vos» o un imperativo sí. Se confirma o descarta con
el set.

## 7. Impacto en demora, memoria y SLM

Medido el 2026-10-26 en la M1 de 8 GB, grabación `202750` (45 s, canal A), 2 hilos, bloques de 100 ms,
dos corridas por variante:

| Variante | Proceso total (45 s de audio) | p95 por bloque | Memoria pico (RSS) |
|---|---|---|---|
| greedy (actual) | 1,06–1,09 s | 28 ms | 467–470 MB |
| beam (4 caminos) | 1,18–1,23 s | 32–33 ms | 471–477 MB |
| beam + 5 hotwords | 1,16–1,22 s | 32–33 ms | 468–472 MB |

- **ASR:** el beam suma ~10 % de cómputo, unos 4 ms por bloque en el peor caso. Es mucho menos que
  los 100 ms de cada bloque, así que la frase final no se demora de forma medible. La memoria no
  cambia: la diferencia queda dentro del ruido entre corridas. Los hotwords no suman nada medible.
- **Diccionario:** microsegundos por frase, sin modelo ni memoria extra.
- **SLM:** su demora (~1,2–1,3 s por evaluación con el 0.8B en la M1) depende de escribir el JSON, no
  del ASR. Un texto mejor no lo hace más lento. Lo que sí lo afecta es **cuántas frases finales**
  manda el ASR, porque con `disparo final` cada una es una evaluación. Por eso el ajuste del corte
  (paso 2) tiene que registrar cuántos segmentos produce: cortar más seguido adelanta el texto pero
  carga más al SLM. En `202750` el greedy dio 11 segmentos y el beam 6 (una sola grabación).
- **Whisper en vivo** (no forma parte de este plan): `faster-whisper` corre en CPU y competiría con
  sherpa y con Ollama en 8 GB que ya comparten el ASR (~470 MB) y el SLM. Su demora y memoria se
  miden en el paso 5 antes de proponer nada.

## 8. Cómo correrlo

1. **Grabar.** Seguí [`voz-real/HOJA-DE-GRABACION.md`](voz-real/HOJA-DE-GRABACION.md): 36 grabaciones (2 tomas × 3
   condiciones × 6 bloques) desde «Probar el ASR», pegando cada bloque en «Lo que dije en realidad» y tocando
   «Guardar prueba». El audio queda en `experiments/voip/llamadas/`, fuera de Git.
2. **Completar** [`voz-real/pruebas.csv`](voz-real/pruebas.csv): id de la prueba, toma (1 o 2), voz y condición.
3. **Con la toma 1**, antes de medir: `python hotwords.py` muestra cómo se parte cada hotword (editá
   [`voz-real/hotwords.txt`](voz-real/hotwords.txt)), y una corrida con `--sin-whisper` lista en su resumen las
   sustituciones frecuentes para armar [`voz-real/diccionario.csv`](voz-real/diccionario.csv). Revisá la jerga de
   [`voz-real/jerga.txt`](voz-real/jerga.txt) y el puntaje de hotwords (`--hotwords-score`).
4. **Un comando**, desde la raíz del repo (con el entorno que tiene `sherpa-onnx` y `faster-whisper`):

```bash
.venv/bin/python experiments/asr-local/medir_voz_real.py
```

Corre la línea base y cada paso del §4 sobre el audio guardado, aplica la regla del §2 en la toma 2 y escribe
`corridas/<fecha>_voz-real_<n>pruebas/` con `resumen.md`, `manifiesto.json` y `frases.jsonl` (sin audio).
Opciones útiles: `--sin-whisper` (Whisper es lento: `small` y `large-v3-turbo` bajan ~2 GB la primera vez y
`large-v3-turbo` usa ~1,8 GB de RAM), `--variantes beam,beam+hotwords` (la línea base se corre siempre),
`--pruebas <carpeta>` si las pruebas están en otra copia del repo, `--bloque-ms 100` para comparar con la tabla del §7
(por defecto 40 ms, como el panel). Detalle de los archivos en el [README](README.md#9-voz-real-94).

