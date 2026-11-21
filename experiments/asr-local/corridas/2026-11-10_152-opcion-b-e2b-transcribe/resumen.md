# #152, opción B: Gemma 4 E2B como ASR en lugar de Parakeet

- **Fecha:** 2026-11-10. Corrió Claude con Mateo Antenucci, en la Mac de Mateo.
- **Issue:** [#152](https://github.com/Corchets/bitacora_tesis/issues/152), opción B: E2B transcribe cada tramo y
  después lee el texto. Se compara con lo que hay hoy (A, [ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)).
- **Script:** [`comparar_e2b_transcribe.py`](../../comparar_e2b_transcribe.py).

> **Audio sintético (TTS), no voz humana.** Las 9 llamadas de Meet de #94 se perdieron el 2026-11-02, así que no hay
> voz real con referencia. Las voces de `say` son mexicanas: no hay voz rioplatense. Sirve para comparar los dos
> reconocedores sobre el mismo audio, no para estimar el WER con voz real.

## Qué pregunta

Si E2B transcribe, sobra Parakeet: un modelo menos en el teléfono. ¿Lo hace tan bien y tan rápido, y ocupa menos
memoria?

## Qué corre

- **Audio:** los 155 turnos de 6 casos de desarrollo de la lista de
  [GRABACIONES-ASR](../../../slm-directo/casos/GRABACIONES-ASR.md), con cifras dictadas: 3 estafas
  (`CV2-D-V-WHATSAPP-006`, `CV2-D-V-ORGANISMO_PREVISIONAL-001`, `CV2-D-V-SOPORTE-002`) y 3 legítimas
  (`CV2-D-L-BANCO-002`, `CV2-D-L-DELIVERY-004`, `CV2-D-L-FAMILIAR-002`).
  - Un clip por turno: 13,1 min en total con el margen de abajo, de 2,5 a 12,3 s. Todos entran en los 30 s por
    entrada de E2B.
  - Voces: A Paulina y B Eddy, las dos `es_MX`.
  - Cada clip lleva 0,3 s de silencio antes y 0,8 s después, como la frase que arma el corte real (`PREVIO_S` y el
    corte de 0,8 s de `MotorPorFrases`). Sin ese margen, Parakeet se comía el arranque (WER 6,7 % en vez de 4,9 %).
  - Dos condiciones: `16k`, y `8k`: bajado a 8 kHz y vuelto a 16 kHz, como una línea telefónica.
  - La segmentación es la misma para los dos: la diferencia sale solo del reconocedor.
- **Parakeet:** TDT 0.6B v3 int8 por `sherpa-onnx` 1.13.8, 2 hilos, el mismo decodificador que `MotorSherpaParakeet`.
  Sin el filtro Silero, que no cambia nada si cada clip ya es una frase.
- **E2B:** `unsloth/gemma-4-E2B-it-GGUF`, `gemma-4-E2B-it-Q4_K_M.gguf` (sha256 `740185b2…`) y el módulo de audio
  `mmproj-F16.gguf` (`140be8d7…`). `llama-server` de llama.cpp 0.9.0, build 12110, `-c 4096 -np 1 --seed 42`,
  temperatura 0, sin razonamiento. El prompt pide la transcripción textual en español.
  - Es la misma cuantización que el `gemma4:e2b-it-q4_K_M` de Ollama, pero otro archivo: Ollama no se usó.
  - llama.cpp marca el audio como «experimental».
- **Máquina:** Apple M4 de 24 GB, macOS 27.0.1, en CPU (`-ngl 0 -t 4`), lo más parecido a un teléfono. Se repitió E2B
  con la GPU (Metal) como el mejor caso de la Mac, en [`metal/`](metal/).
- **Métricas:**
  - WER sin tildes y con las cifras pasadas a palabras, para que «6047» y «seis mil cuarenta y siete» cuenten igual.
  - Cifras enteras: las cifras de la referencia que aparecen completas.
  - Palabras críticas: las de `wer.PALABRAS_CLAVE_DEFECTO` («código», «cuenta», «clave»...).
  - Demora por clip con el modelo ya cargado.
  - Tiempo / audio: segundos de proceso por segundo de audio.

```bash
python comparar_e2b_transcribe.py sintetizar --audio <dir fuera de Git>
python comparar_e2b_transcribe.py parakeet --audio <dir> --modelo <dir parakeet> --salida <esta carpeta>
llama-server -m gemma-4-E2B-it-Q4_K_M.gguf --mmproj mmproj-F16.gguf -c 4096 -np 1 --port 8090 --seed 42 \
  -ngl 0 --no-mmproj-offload -t 4
python comparar_e2b_transcribe.py e2b --audio <dir> --servidor http://127.0.0.1:8090 --pid <pid> --salida <esta carpeta>
python comparar_e2b_transcribe.py resumir --salida <esta carpeta>
```

El script se commiteó después de correr: los manifiestos dicen `f2450fa` más el script sin commitear.
- La normalización de cifras se corrigió después de la corrida, para aceptar «39,714,286».
- `resumir` recalcula el WER desde las transcripciones guardadas, así que la tabla ya sale con la corrección.

## Resultados

### Calidad y demora, en CPU

| Motor | Condición | WER | Clips sin error | Cifras enteras | Palabras críticas | Demora por clip, mediana (ms) | p90 (ms) | Tiempo / audio |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Parakeet | 16k | 4,9 % | 114/155 | 13/13 | 21/21 | 177 | 234 | 0,036 |
| Parakeet | 8k | 6,6 % | 107/155 | 13/13 | 20/21 | 186 | 257 | 0,038 |
| E2B | 16k | 8,5 % | 99/155 | 12/13 | 21/21 | 2.687 | 3.873 | 0,549 |
| E2B | 8k | 9,1 % | 91/155 | 11/13 | 21/21 | 3.021 | 3.958 | 0,609 |

E2B con Metal: WER 8,4 % y 9,0 %, y 528 y 698 ms por clip ([`metal/tabla.md`](metal/tabla.md)). La GPU lo hace 5
veces más rápido, pero no le cambia la calidad, y sigue 3 veces más lento que Parakeet en CPU.

Clip por clip, con 16k, E2B tiene más errores que Parakeet en 45 clips, menos en 23 y los mismos en 87 (en 8k: 47, 22
y 86). La diferencia no es ruido.

Las cifras que E2B no conserva son las que deciden un aviso:
- «Es 6047» sale «Es 2047» en 16k, y «1047» o «Safety 47» en 8k.
- «Termina en 6174» sale «Hermigua, 174» en 8k.

Los demás errores son acústicos, de los dos: «la ceramista» sale «la semana vista» con E2B, y «Le pido el DNI» sale
«Le pido el TNI» con Parakeet ([`e2b.jsonl`](e2b.jsonl), [`parakeet.jsonl`](parakeet.jsonl)).

### Memoria, en CPU

Huella física pico según `footprint` de macOS, que es lo que el sistema le cobra al proceso. El RSS suma además las
páginas del archivo del modelo mapeadas en memoria (3,1 GB), que el sistema puede liberar.

| Opción | Qué hay cargado | Huella física pico | RSS |
|---|---|---:|---:|
| A (hoy) | Parakeet (2.044 MB) + E2B solo texto (1.547 MB) | 3.591 MB | 2.055 + 4.571 = 6.626 MB |
| B | E2B con el módulo de audio | 4.206 MB | 5.866 MB |

- Parakeet: medido en un proceso aparte después de los 155 clips de 16k.
- E2B solo texto: `llama-server` sin `--mmproj`, con la misma configuración, después de tres consultas de 539 tokens.
- B: el pico de toda la corrida.

Sacar Parakeet ahorra unos 2 GB, pero el módulo de audio en F16 (1 GB en disco) y sus buffers suman otro tanto.
Con la huella física, B ocupa unos 600 MB más que A; con el RSS, unos 760 MB menos. **No hay un ahorro claro de
memoria.** Un módulo de audio cuantizado a 8 bits podría bajarlo; no se probó.

### Demora dentro de la llamada

En A, Parakeet transcribe un turno mientras E2B todavía puede estar leyendo el anterior. En B, el mismo modelo hace
las dos cosas, una detrás de otra: los 2,7 s por turno en CPU se suman enteros a la demora del aviso, antes de cada
consulta.

### Tokens por segundo de audio

En los 310 clips, la entrada de E2B mide 31 + 25 × (segundos de audio) tokens: **25 tokens por segundo de audio.**
Es el dato que pesa en la opción C (abajo).

## Lectura

> **Estado: propuesta sin discutir.** Para la reunión del equipo del 2026-11-11, que decide #152.

**Seguir con A.** Sobre el mismo audio, B:
- transcribe peor (8,5 % contra 4,9 %) y pierde cifras dictadas;
- tarda 15 veces más en CPU, y esa demora se suma al aviso porque usa el mismo modelo;
- no ahorra memoria con claridad.

Lo que B sí da: un solo modelo, un solo runtime y un archivo menos que actualizar. Y, con un prompt, se le puede pedir
español, que Parakeet no permite fijar. Eso último no se midió.

## Por qué la opción C queda afuera sin medirla

C es que E2B escuche el audio del turno y responda directo si hay riesgo, sin transcripción intermedia.

1. **El contexto no entra.** E2B acepta 30 s de audio por entrada, y cada segundo cuesta 25 tokens. Una llamada de
   5 minutos son 7.500 tokens de audio, casi el doble de los 4.096 de contexto de la configuración. Los turnos
   anteriores tendrían que ir como texto, y para tener ese texto hace falta transcribir igual: C termina siendo B con
   la consulta pegada.
2. **Sin texto, el aviso pierde lo que lo hace útil.** No hay transcripción para citar el motivo
   ([ADR 0006](../../../../docs/ingenieria/adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md))
   ni registro de la llamada.
3. **Invalida lo medido.** Toda la evaluación es sobre texto: desarrollo, la reserva y #144. Para medir C habría que
   sintetizar el audio de todos los casos, rehacer el prompt para audio y repetir las etapas 1 a 3 de #143. No entra
   antes del 2026-11-15.
4. **El oído es el mismo.** La opción B muestra que E2B escucha peor que Parakeet sobre el mismo audio, y C usaría ese
   mismo oído.

Queda como trabajo futuro.

## Límites

- TTS con voces mexicanas, sin ruido, y un solo hablante por clip.
- 6 casos y 155 turnos. Alcanza para comparar los dos reconocedores, no para estimar su WER con voz real.
- Una Mac M4, no un teléfono ([#141](https://github.com/Corchets/bitacora_tesis/issues/141)).
- Un solo prompt de transcripción para E2B, sin ajustar.
