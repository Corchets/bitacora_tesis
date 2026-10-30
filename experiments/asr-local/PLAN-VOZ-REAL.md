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
   Si se guardó sin escribir «Lo que dije en realidad», la columna `bloque` (1 a 6) toma como referencia el texto
   de ese bloque del guion; lo escrito en el panel manda sobre el bloque.
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
`--solo-parakeet` (solo Parakeet con cada corte y umbral de `VARIANTES_PARAKEET`, cada uno contra el del panel,
sin la cadena de Zipformer), `--pruebas <carpeta>` si las pruebas están en otra copia del repo, `--bloque-ms 100` para comparar con la tabla del §7
(por defecto 40 ms, como el panel). Detalle de los archivos en el [README](README.md#9-voz-real-94).


## 9. Zipformer anda mal con voz real: probamos Parakeet (2026-10-28)

> **Actualización del 2026-10-29, Luciano Grosso:** Zipformer Kroko queda como antecedente
> histórico, retirado de la selección activa por los errores observados con su voz. Se conservan
> código y corridas para reproducir el laboratorio. Esto no selecciona un reemplazo ni cierra
> [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

> **Estado: propuesta sin discutir.** Es una prueba de otro modelo para la demo, no la elección de
> [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector). El código conserva Zipformer
> como valor por defecto; para ensayar Parakeet hay que elegirlo en el panel o iniciar con
> `--asr parakeet`. Retirar el candidato no equivale a modificar el arranque de la demo.

**Qué pasa.** Con la voz de Luciano en el panel, Zipformer Kroko transcribe mal: parte palabras al
medio («la concha de tu ma | dre», «Alambre el | código»), cambia palabras («la alergia» por «la
alerta») y deja frases que son solo un punto. Con TTS daba 4–5 % de WER, así que ese número no
anticipaba lo que pasa con voz real. La app de dictado Wispr Flow transcribe bien la misma
voz, pero es un producto cerrado: no se puede correr como modelo local, que es lo que pide la
[privacidad del sistema](../../docs/corpus/PRIVACIDAD-DEL-SISTEMA.md).

**Qué probamos.** Dos modelos locales sobre 4 llamadas reales del panel del 2026-10-28 (micrófono y
Meet/BlackHole, 2 canales cada una, fuera de Git en `experiments/voip/llamadas/`), con el mismo corte
de silencio (0,8 s, umbral RMS 0,005) y bloques de 40 ms como los manda el panel. No hay
transcripción de referencia: la comparación se hizo leyendo las salidas, no con WER.

| Modelo | Tiempo real | Lo que se vio | Bloque más lento (M1, 2 hilos) | RSS (TTS, `asr_local.py`) |
|---|---|---|---|---|
| Zipformer Kroko (actual) | Sí, palabra por palabra | Corta palabras y cambia términos | ~80 ms | ~475 MB |
| **Parakeet TDT 0.6B v3** int8 ([`csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8`](https://huggingface.co/csukuangfj/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8)) | Borrador cada 0,5 s; frase completa al cerrar | Frases enteras y bien escritas («Podés hablar bien la concha de tu madre», «salta una vez la alerta»). Con ruido o respiración a veces inventa palabras en inglés o portugués («Thank you», «Olá») | ~450 ms | ~1,0–1,2 GB |
| Whisper large-v3-turbo int8 (`faster-whisper`) | No: solo al cerrar la frase | Inventa «Gracias», «Suscríbete al canal» en los silencios | 4–10 s | — |

Con TTS los tres empatan (Zipformer 0–2,2 % de WER, Parakeet 2,2–2,5 %): ese audio no sirve para
elegir entre ellos.

**Qué cambió en el código.**

- [`motores.py`](motores.py): `MotorPorFrases` corta frases con el mismo umbral y corte de silencio
  del panel, descarta frases con menos de 0,3 s de voz, corta a los 10 s y vuelve a transcribir la
  frase abierta cada 0,5 s para el borrador. `MotorSherpaParakeet` (los dos canales comparten el
  modelo) y `MotorWhisperPorFrases` (solo para comparar, no está en el panel).
- Panel y servidor: selector «Modelo de ASR» en Llamada en vivo y en Probar el ASR; `servidor.py --asr`
  fija el de arranque. El manifiesto de cada llamada guarda `config.asr` y los metadatos del motor.
- [`asr_local.py`](asr_local.py): `--motor sherpa-parakeet` y `--motor whisper-frases`.

**Límites.** Son 4 llamadas con una o dos voces y sin referencia escrita. Parakeet usa unos 600 MB
más que Zipformer, lo que pesa en la pregunta de gama de D09. Escribe números como dígitos («0, 0,
1, 2, 3», «958 679 123») y no se puede fijar el idioma, así que hay que revisar si las reglas
siguen viendo los códigos. Mientras transcribe bloquea el bucle del servidor hasta ~0,45 s.

**Siguiente paso (actualizado el 2026-10-29; hecho con micrófono, ver §11).** Grabar el set de la sección 3 con «Probar el ASR» y medir Parakeet con
`medir_voz_real.py` (etiquetas de reglas por frase, WER y CER). Parakeet ya está como variante en
[`variantes_voz_real.py`](variantes_voz_real.py) (`--solo-parakeet`, 2026-10-29). Las variantes de Zipformer se
conservan como reproducción histórica; no son trabajo activo de mejora.

### 9.1 El borrador sale en inglés y después se corrige (2026-10-29)

Pasó en la reunión con el tutor del 2026-10-28: Parakeet escribe unas palabras en inglés y al
cerrar la frase las cambia por el texto en español.

**Por qué pasa.** Parakeet v3 detecta el idioma solo, a partir del audio; no hay forma de
pedirle español ([tarjeta del modelo](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)). El
primer borrador sale con apenas 0,3 s de voz más 0,5 s de espera. Con tan poco audio el modelo
adivina el idioma y a veces arranca en inglés; al cerrar la frase tiene todo el audio y la
escribe bien. El detector evalúa al cerrar la frase (`servidor.py --disparo final`, el valor por
defecto), así que esas palabras no disparan el aviso: el problema es lo que se ve en pantalla. El
panel ya muestra el borrador con borde punteado y en gris.

> **Estado: opciones 1 y 2 implementadas (2026-10-29, #94); la 3 no se hizo.**

1. **Esperar más audio para el primer borrador.** `MotorPorFrases.MIN_VOZ_PARCIAL_S = 1.0`
   (aparte de `MIN_VOZ_S = 0.3`, que sigue valiendo para el final). El primer borrador aparece
   más tarde, pero con más audio el modelo se equivoca menos de idioma.
2. **No mostrar un borrador que no parece español.** `parece_otro_idioma()` en
   [`motores.py`](motores.py): si el borrador trae palabras comunes de inglés o portugués («the»,
   «you», «yeah», «thank», «olá»…) y ninguna de español, no se emite y queda el anterior. Una frase
   final se descarta solo si todas sus palabras son una muletilla inventada («thank», «you»,
   «yeah», «yes», «olá», «obrigado», «tchau», «bye»). **Decisión: «ok» y «okay» no se filtran
   nunca** (se usan en Argentina), ni anglicismos corrientes como link, token, mail o app. El
   manifiesto de cada llamada guarda `min_voz_parcial_s` y `filtro_idioma` en `segmentacion`.
3. **Cambiar de modelo** a uno que acepte el idioma fijo o que sea solo de español. No está
   verificado qué opciones de ese tipo corren en `sherpa-onnx` ni cuánto pesan.

**Medición (6 llamadas Parakeet del 2026-10-28, código `c0938f4` más estos cambios).** Se repasó
el `estereo.wav` de cada una por el mismo motor, con la configuración vieja (0,3 s de voz, sin
filtro) y la nueva. Parciales con inglés (regex independiente del filtro): 15 de 625 antes, 0 de
523 ahora, ninguno con menos de 1,5 s de audio. Costo: el primer borrador de cada frase tarda
más, mediana 0,80 s → 1,46 s y p90 1,20 s → 2,68 s desde el inicio de la frase, y 4 de 26 frases
cortas ya no muestran ningún borrador. El único final que cambió fue un «Yeah.» (muletilla); no se
perdió ninguna frase en español. Quedan finales en inglés que el filtro no toca por diseño («No
one.», «You're»). Repetir: `python experiments/asr-local/comparar_filtro_idioma.py --prefijo
2026-10-28` (las transcripciones van a `experiments/voip/llamadas/_filtro_idioma/`, fuera de Git).

### 9.2 Cómo se entrenó cada modelo y cuánto pesa (2026-10-29)

**No entrenamos ningún ASR.** Los dos vienen entrenados. Bajamos la conversión a ONNX que publica
`sherpa-onnx` y solo los usamos para transcribir. Lo que se ajusta en #94 (corte de silencio,
umbral, borrador, *hotwords*) es configuración, no los pesos del modelo.

- **Parakeet TDT 0.6B v3:** lo entrenó NVIDIA. Codificador FastConformer con decodificador TDT,
  unos 600 millones de parámetros, 25 idiomas europeos. Datos: unas 10 000 h transcriptas por
  personas y unas 660 000 h del conjunto Granary transcriptas automáticamente, en 128 GPU A100.
  Licencia CC BY 4.0 ([tarjeta del modelo](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)).
  Se puede reentrenar con NeMo sobre audio propio transcripto, pero hacen falta GPU y muchas más
  horas que las 30 frases de la sección 3. No está planificado.
- **Zipformer Kroko:** modelo streaming de español de Kroko, también entrenado por terceros.

| | Zipformer Kroko | Parakeet TDT 0.6B v3 int8 | Relación |
|---|---|---|---|
| Archivos del modelo en disco | ~156 MB (`float32`) | ~670 MB (`int8`) | ~4× |
| Parámetros | ~39 M (estimado: 156 MB / 4 bytes) | ~600 M | ~15× |
| Memoria del proceso (RSS) | ~475 MB | ~1,0–1,2 GB | ~2–2,5× |
| Bloque más lento (M1, 2 hilos) | ~80 ms | ~450 ms | ~5–6× |
| Cómo transcribe | Palabra por palabra mientras se habla | Vuelve a transcribir la frase entera cada 0,5 s | |

Los tamaños en disco salen de los archivos descargados; la memoria y los tiempos, de la tabla
de la sección 9.

**Cómo corre hoy.** En la CPU de la Mac M1 con 2 hilos (`hilos=2` en `MotorSherpaParakeet`), sin GPU
ni Neural Engine. No usa toda la potencia de la computadora ni imita un teléfono: es una
configuración fija y no se midió en ningún teléfono. Como cada borrador repite la frase desde el
principio, el costo sube a medida que la frase se alarga, hasta el corte de 10 s.

**En un teléfono de gama alta.** `sherpa-onnx` tiene soporte para Android e iOS. El RSS de la
Mac no demuestra que el conjunto ASR + detector entre en la memoria disponible para una app
del teléfono. No sabemos cuánto tarda cada borrador, cuánta batería consume ni cuánto calienta
en ese dispositivo. Con la
[gama acordada el 2026-10-28](https://github.com/Corchets/bitacora_tesis/blob/laboratorio-luciano/docs/gestion/seguimientos/2026-10-28.md#3-minuta-y-resoluciones-del-profesor)
(la más alta a la fecha, optimizar después), esto queda como límite declarado, no como
bloqueo.

## 10. Auditoría de VAD, preaudio y comparación de modelos (2026-10-29)

Consulta de Luciano, vinculada a [#94](https://github.com/Corchets/bitacora_tesis/issues/94)
y a la comparación de [#51](https://github.com/Corchets/bitacora_tesis/issues/51).
Inspección de [`motores.py`](motores.py) sobre el código base `2a61d8d`; no es una nueva
corrida de reconocimiento ni una medición de batería.

### 10.1 Qué tenemos implementado

| Parte | Implementación comprobada | Alcance |
|---|---|---|
| Inicio/fin de habla en Parakeet | `MotorPorFrases` compara RMS con `0.005`; cierra tras `0.8 s` de silencio por defecto. El panel admite «Automático» o `0.1–3.0 s`. | Es un detector por energía. No distingue voz y ruido con un modelo como Silero. Un segmento acústico no garantiza un turno conversacional. |
| Preaudio de Parakeet y Whisper por frases | `PREVIO_S = 0.3`; `previo` retiene bloques anteriores al inicio detectado y los antepone a la frase. | Sí cumple la función del búfer rotatorio de 200–400 ms. Es una lista acotada, no un anillo literal; con bloques de 40 ms retiene hasta 280 ms por descarte de bloques enteros. |
| Trabajo durante silencios | Sin frase abierta, se actualiza el preaudio y se retorna sin llamar al reconocedor. Se exige `MIN_VOZ_S = 0.3` para transcribir el final. | Evita inferencia sobre silencio inicial; ruido por encima del umbral puede activar el ASR y voz débil puede quedar debajo. |
| Frases largas y parciales | Máximo de 10 s; Parakeet vuelve a reconocer toda la frase cada 0.5 s, desde 1 s de voz acumulada, y al cerrar. | Es entrega incremental construida sobre un reconocedor offline. Repite cómputo; el consumo sostenido en el teléfono está sin medir. |
| Zipformer histórico | Recibe todos los bloques, incluidos los silencios; cierra por endpoint nativo o RMS. | No había una compuerta VAD previa que evitara enviar silencio. No necesitaba recuperar un inicio descartado por esa compuerta. |
| Whisper base del procedimiento original | `MotorFasterWhisper` acumula el audio completo y transcribe en `vaciar_final()`, con `vad_filter=True` y silencio mínimo de 500 ms. | Tiene filtrado VAD de faster-whisper al procesar el lote; no es el VAD continuo de la llamada. |

La cola de silencio artificial de Zipformer (purga/lookahead) y los búferes de transporte
no son el preaudio: cumplen otras funciones. Tampoco el cortador RMS de 400 ms del spike
[`turns.py`](../laboratorio/turns.py) demuestra que se hubiera integrado Silero.

**Verificación del 2026-10-29:** pasan las 11 pruebas de `tests/test_motor_por_frases.py`.
Una comprobación adicional con bloques sintéticos de 40 ms confirmó 4480 muestras de
preaudio (280 ms a 16 kHz), conservación del audio anterior al inicio y cero llamadas al
transcriptor durante el silencio inicial. No verifica reconocimiento ni ahorro de energía.

### 10.2 Comparación con la recomendación recibida

Las observaciones propias conservan las condiciones de §9 y de las
[corridas TTS](../../docs/evaluacion/COMPARACION-CANDIDATOS-DESARROLLO.md#asr-sobre-audio-tts).
No son comparaciones pareadas de calidad con referencia humana.

| Opción | Relación con nuestro trabajo | Evidencia y límite |
|---|---|---|
| Whisper base/small cuantizado con whisper.cpp | La recomendación propone otra implementación y cuantización. Probamos **base multilingüe int8 con faster-whisper en CPU**, no whisper.cpp Q4. | En un audio TTS: RTF 0.2745, RSS 276.91 MB, WER 17.39 % y omisión de «cero». No permite descartar ni recomendar base/small Q4 en un teléfono. |
| **Parakeet TDT 0.6B v3 int8 con sherpa-onnx** | Candidato que se ensaya ahora, con segmentación y borradores de §10.1. Incluye español. | En la inspección de 4 llamadas reales se vio mejor que Zipformer; sin referencia ni WER humano. En M1: RSS ~1.0–1.2 GB y bloque más lento ~450 ms. El filtro de §9.1 reduce inglés visible, sin garantizar transcripciones correctas. |
| Whisper large-v3-turbo int8 con faster-whisper | Comparador por frases, sin borradores. | En esa prueba de CPU: 4–10 s por frase e inserciones en silencio. Inadecuado para esa demo/configuración; no es un resultado universal sobre Whisper ni sobre whisper.cpp. |
| Zipformer Kroko | **Antecedente retirado de la selección activa por Luciano el 2026-10-29.** | Era streaming nativo y más liviano (~156 MB en disco, ~475 MB RSS en §9), pero cortó/cambió palabras con voz real. El buen WER TTS no justificaba mantenerlo. Se preservan sus resultados, sin afirmar que toda la familia Zipformer falle. |
| MMS / Squeezeformer con sherpa-onnx | No se probaron en este laboratorio. Sherpa es un runtime; no define una única arquitectura ni un costo de memoria. | No hay comparación propia para llamarlos más rápidos, más livianos o mejores en acento argentino. |
| API en la nube | No integra la ruta de inferencia del proyecto. | El procesamiento local es una restricción del [diseño de privacidad](../../docs/corpus/PRIVACIDAD-DEL-SISTEMA.md). |

En el detector de texto, la recomendación propone un encoder pequeño entrenado. Nosotros
conservamos reglas como línea base, antecedentes de RoBERTuito/Tito y ensayos de SLM directo
con Qwen y Llama. La cascada no está adoptada. Como referencia del costo, el Qwen3.5 0.8B
de la [demo M1](../voip/corridas/2026-10-26-medicion-84-m1-08b/README.md) tardó 1.312 s de
mediana por evaluación y avisó 2.803 s después del fin del pedido (una estafa TTS, 4 evaluaciones).
No demuestra rendimiento móvil, ni permite afirmar que cualquier SLM sea inviable. Un encoder
semántico tampoco garantiza reconstruir una negación, un dígito o un pedido perdido por el ASR.

### 10.3 Correcciones a la recomendación y fuentes primarias

Consulta del 2026-10-29 a documentación oficial de los proyectos, contrastada con el código
local. Se incluyeron fichas, APIs y ejemplos que permiten verificar arquitectura e integración;
se excluyeron promesas de rendimiento sin medición del teléfono y las equivalencias entre
tamaño de pesos, RSS y RAM disponible. No se analizaron nuevos datos del corpus ni del test.

- **VAD no es universalmente obligatorio para cualquier ASR.** whisper.cpp lo ofrece como
  [opción para filtrar segmentos](https://github.com/ggml-org/whisper.cpp#voice-activity-detection-vad).
  En nuestra integración por frases es razonable comparar un VAD con el RMS; no hay evidencia
  para afirmar que sin Silero la batería se agotaría «en minutos».
- **Whisper español usa el modelo multilingüe `base`, no `base.en`.** `.en` es inglés y
  `base.es` no es una variante oficial. La [tabla de OpenAI](https://github.com/openai/whisper#available-models-and-languages)
  identifica 74 M de parámetros para base; el tamaño de pesos cuantizados no equivale al RSS.
- **El VAD de nuestro Whisper base proviene de faster-whisper.** La librería integra
  [Silero VAD](https://github.com/SYSTRAN/faster-whisper#vad-filter); no significa que el panel
  Parakeet use ese filtro. [Silero](https://github.com/snakers4/silero-vad) ofrece ONNX y audio
  a 8/16 kHz, sin garantizar el costo de nuestra integración en un teléfono concreto.
- **sherpa-onnx ya es nuestro runtime de Parakeet.** Lo cataloga como
  [transducer offline, con ejemplos de streaming simulado](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/offline-transducer/nemo-transducer-models.html#sherpa-onnx-nemo-parakeet-tdt-0-6b-v3-int8-25-european-languages).
  Cambiar a sherpa no es una alternativa a Parakeet: ya usamos ambos juntos.
- **MMS y Squeezeformer no son el mismo modelo.** [MMS-1B-all de Meta](https://huggingface.co/facebook/mms-1b-all)
  es Wav2Vec2-CTC de ~1 B de parámetros; [Squeezeformer](https://arxiv.org/abs/2206.00888)
  es otra arquitectura. Hace falta identificar checkpoint, idioma y conversión antes de
  compararlos. No se verificó aquí una integración MMS español lista para sherpa.
- **CTC/Transducer no justifica prometer cero inserciones o alucinaciones.** Nuestro Parakeet
  TDT ya produjo texto ajeno al habla (§9.1). Tampoco los embeddings garantizan recuperar
  información perdida: la tolerancia del detector debe medirse con el mismo audio y referencia.
- **Un LLM móvil no es imposible por definición.** Meta publica
  [Llama 3.2 1B/3B y variantes cuantizadas para uso on-device](https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/MODEL_CARD.md).
  Eso no demuestra que ASR + SLM de nuestro proyecto cumplan los presupuestos del teléfono.

### 10.4 Qué falta comprobar

> **Estado: propuesta sin discutir.** En [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector),
> comparar el RMS actual contra un VAD de voz (por ejemplo Silero), manteniendo ASR, audio y
> preaudio constantes. No se adopta una librería ni un umbral nuevo con esta auditoría.

Medir voz tenue, ruido, inicios de palabra, pausas y números con referencia humana. Para el
teléfono de gama alta acordado con el tutor faltan latencia y cola sostenidas, memoria conjunta,
batería y temperatura durante la llamada. El costo de los borradores de Parakeet debe separarse
del costo del resultado final y del detector. D08 y D09 permanecen abiertas.

## 11. Voz real con Parakeet: corte y umbral (2026-10-29)

> **Decisión de Luciano (2026-10-29):** «Probar el ASR» arranca en **0,8 s / 0,008** (antes 0,9 s / 0,003).
> La llamada en vivo no cambia (0,9 s / 0,003). No pasa la regla del §2 (+0 frases con etiquetas correctas):
> se adopta por WER y CER. Es un valor del laboratorio con una sola voz; no cierra
> [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector).

Primera medición con referencia escrita sobre la voz de Luciano: el set de la sección 3, condición
`luciano-microfono`, más cuatro grabaciones extra para la comparación de corte y de VAD pendiente del §10.4.

### 11.1 Qué se grabó

Todo con «Probar el ASR», Parakeet, micrófono de la Mac en la pieza de Luciano y bloques del guion leídos de
una hoja en el celular. El panel guardó el audio entero; los cortes y umbrales distintos de los del panel se
rehicieron offline sobre ese mismo audio. Audio fuera de Git (copia `bitacora_tesis-voip-asr`,
`experiments/voip/llamadas/`); ids en [`voz-real/pruebas.csv`](voz-real/pruebas.csv). Las referencias son el texto
del guion por bloque (columna `bloque`): Luciano no informó desvíos.

| Grabaciones | Toma | Panel | Qué |
|---|---|---|---|
| G01–G05 | 1 | 0,9 / 0,003 | bloques 1 a 5, tele apagada. G06 (bloque 6) se borró del Historial antes de medir ([R24](../../docs/gestion/REGISTRO-RIESGOS.md)) |
| G07 | 1 | 0,9 / 0,003 | bloque 1 con voz baja (salió casi al mismo volumen) |
| G08 | 1 | 0,9 / 0,003 | bloque 2 con una serie de fondo |
| G09 | 1 | 0,9 / 0,003 | bloque 3 con una pausa de ~1 s dentro de cada frase |
| G10 y otra | — | 0,9 / 0,003 | 30–44 s sin hablar: con la tele apagada y con la serie. Sin referencia: no entran en el WER |
| G11–G16 | 2 | 0,9 / 0,003 | bloques 1 a 6 otra vez (G14 se grabó al final) |
| G11–G16 | 3 | **0,8 / 0,008** | bloques 1 a 6, para confirmar con audio nuevo lo elegido mirando la toma 2 |

### 11.2 Qué pasaba con 0,9 s / 0,003

Una simulación del corte RMS (bloques de 40 ms, mismas reglas que `MotorPorFrases`) reproduce exactamente los
segmentos del panel, y sirvió para probar combinaciones antes de correr el ASR.

- **Las pausas reales entre frases fueron de 0,5 a 1,4 s**, aunque la consigna era «dos segundos». Las de dentro
  de una frase (comas, respiración) llegan a 0,76 s. Las dos zonas se tocan cerca de 0,8 s.
- **Con 0,9 s casi ninguna pausa alcanzaba el corte**: 5 de 25 segmentos de G01–G06 y 4 de 22 de la toma 2 sin G14
  se cerraron por el tope de 10 s (`MAX_FRASE_S`), juntando dos o tres frases y cortando palabras en el borde
  («…con este | enlace y pásame el pin»). En G14 la frase F17 («pasame el PIN y el CVV») se perdió entera.
- **0,003 queda pegado al ruido de la pieza** (RMS p10 ≈ 0,001, p25 ≈ 0,002): el final de la respiración cuenta
  como voz y las pausas parecen más cortas.

### 11.3 Resultados

`medir_voz_real.py --solo-parakeet`: cada corte y umbral sobre el mismo audio, contra el del panel.

**Toma 2** (G11–G16, 30 frases; [corrida](corridas/2026-10-29_voz-real_parakeet-cortes/resumen.md)):

| Corte / umbral | Frases OK | WER | CER | Demora final mediana | Segmentos |
|---|---|---|---|---|---|
| 0,9 / 0,003 (panel) | 27/30 | 20,8 % | 13,6 % | 1,16 s | 24 |
| 0,8 / 0,003 | 27/30 | 21,1 % | 12,8 % | 1,03 s | 27 |
| 0,5 / 0,003 | 28/30 | 13,0 % | 4,9 % | 0,74 s | 34 |
| 0,3 / 0,008 | 27/30 | 16,3 % | 6,9 % | 0,47 s | 46 |
| 0,5 / 0,008 | 28/30 | 13,8 % | 5,5 % | 0,74 s | 36 |
| 0,6 / 0,008 | 28/30 | 13,8 % | 5,5 % | 0,84 s | 35 |
| **0,8 / 0,008** | **28/30** | **13,3 %** | **5,5 %** | **1,06 s** | **30** |

**Toma 3** (grabada en vivo con 0,8 / 0,008; [corrida](corridas/2026-10-29_voz-real_parakeet-confirmacion/resumen.md)):

| Corte / umbral | Frases OK | WER | CER | Demora final mediana | Segmentos |
|---|---|---|---|---|---|
| 0,9 / 0,003 (panel anterior) | 28/30 | 18,3 % | 10,6 % | 0,95 s | 21 |
| 0,5 / 0,008 | 27/30 | 16,8 % | 7,5 % | 0,73 s | 34 |
| **0,8 / 0,008** | **28/30** | **13,0 %** | **5,2 %** | **1,03 s** | **28** |

- **La toma 3 confirma lo que predijo la toma 2 para 0,8 / 0,008** (28/30, WER ~13 %). 0,5 / 0,008, que se veía
  bien en la toma 1, no se sostuvo: parte frases y empeora.
- **Lo que mejora es dejar de cerrar por el tope de 10 s**: el WER baja 5–8 puntos y el CER a la mitad.
- **Ninguna negativa disparó etiquetas** en ninguna variante ni toma.
- **Regla del §2: no pasa ninguna.** Pide +2 frases y la base ya acierta 27–28 de 30; la mejora es de +1 (toma 2)
  y +0 (toma 3). La regla se pensó para Zipformer, que partía de mucho más abajo.
- En vivo la toma 3 dio 28 segmentos para 30 frases (tres pares juntos y una frase partida): con esta voz
  ningún corte RMS separa siempre bien, porque hay pausas entre frases de 0,80 s justos.
- Demora y proceso son offline en la M1 (reloj simulado del §8), algunas corridas mientras se grababa.

### 11.4 Extras (toma 1, con 0,9 / 0,003 en el panel)

| Grabación | Etiquetas | Qué mostró |
|---|---|---|
| G07 voz baja | 5/5 | con 0,8 / 0,008 salen las 5 frases separadas. No prueba voz baja: el volumen fue casi el normal |
| G08 serie de fondo | 5/5 en todas las variantes | el ruido de la tele nunca baja de 0,008 (p10 ≈ 0,008): con cualquier corte y umbral fijo las frases se cierran cada 10 s justos y se cortan en medio de una palabra |
| G09 pausas | 5/5 | cada pausa de ~1 s parte la frase con cualquier corte menor a 1 s; se perdió entero «es para verificar» y «siete» salió «seis» |
| G10 sin hablar | — | 8 ruidos (respiración, movimiento) pasaron el umbral y fueron al ASR; salió una frase inventada: «Shh. Uh-uh.» |
| Serie sin hablar | — | transcribió habla real de la serie («una más») y palabras inventadas en inglés y portugués |

G08 y G10 son el caso para comparar RMS contra un VAD de voz (§10.4): un VAD debería ahorrar el ASR sobre ruidos
(G10), pero la tele también es voz humana, así que no resolvería G08; para eso haría falta otra cosa (un umbral
que siga el ruido de fondo, sin probar).

### 11.5 Errores que no dependen del corte

Se repiten con cualquier corte y umbral; son del modelo con esta voz.

- **«Compartí pantalla» pierde la primera palabra en las tres tomas** y queda sin `REQUEST_REMOTE_ACCESS`.
- Términos críticos cambiados: «token» → «toque», «OTP» → «lo Tp», «CVV» → «código de seguridad» o «CBB»,
  «CBU» → «servicio» o «CvU». Bancos y apps: «Ualá» → «igual», «AnyDesk» → «ni desk» / «Anidesk»,
  «Brubank» → «Bluebank».
- Números: Parakeet los escribe en dígitos («842105», «30 lucas»); las reglas siguen viendo el código salvo cuando
  se pierde la palabra que lo pide. Hubo un monto invertido («mil doscientos» → «doscientos mil») y un dígito
  cambiado («siete» → «seis»).
- Una negación inventada: «que sea en efectivo» → «que no sean en efectivo».
- Jerga: «ñaño» desaparece casi siempre; «guaso» → «juazo» / «aguaso»; «al ñudo» → «al pedo».

### 11.6 Qué sigue

1. Comparar Silero contra RMS con este mismo audio, modelo y preaudio (§10.4), mirando G08, G10, palabras
   cortadas al inicio y demora.
2. Si el corte RMS sigue sin margen con esta voz, probar un umbral que siga el ruido de fondo o un corte
   apoyado en el texto (frase terminada), antes de tocar la llamada en vivo.
3. Grabar la condición Meet y otra voz (sección 3) y medir en el teléfono al final.
