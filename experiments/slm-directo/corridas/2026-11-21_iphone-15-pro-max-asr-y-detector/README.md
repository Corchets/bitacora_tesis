# iphone-15-pro-max-asr-y-detector — 2026-11-21

Tercera medición en teléfono de [#141](https://github.com/Corchets/bitacora_tesis/issues/141): el detector con la
configuración final ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)) y el ASR del
proyecto, `parakeet-filtro` ([ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)),
corriendo a la vez en el iPhone 15 Pro Max de Mateo, con audio sintético a ritmo de conversación. Sigue a la
[medición del detector solo](../2026-11-20_iphone-15-pro-max-latencia/README.md) del 2026-11-20. **Mide memoria,
latencia y estado térmico, no detección ni calidad de transcripción.** No cierra D08 ni D09.

> **Estado al 2026-11-21: preparado y probado en seco en la Mac; falta correr en el teléfono.** La app está instalada
> y los archivos copiados por Wi-Fi, pero iOS no la deja abrir hasta que Mateo vuelva a confiar en el certificado
> (se había borrado la app).

## Preguntas

1. ¿Entra la memoria sumada (detector ~3 GiB residente, ASR) o iOS cierra la app? Si la cierra, eso es el resultado.
2. ¿Cuánto empeora la latencia del detector con el ASR compitiendo? Referencia sin ASR: [`metal`](../2026-11-20_iphone-15-pro-max-latencia/metal/),
   0,79 s de mediana por línea, p95 1,03 s.
3. ¿A qué estado térmico llega con ritmo real, frío y sin cable? En la corrida anterior, enchufado, llegó a `serious`
   en las cuatro corridas.

## Cómo se mide

- **Audio:** [`sintetizar.py`](sintetizar.py) sintetiza con `say` las seis conversaciones de desarrollo de
  [`conversaciones-sub-6.json`](../2026-11-11_a56-latencia-172/conversaciones-sub-6.json) (Paulina para OTRA, Mónica
  para PROTEGIDA, las voces de `asr-local/sintetizar_par.py`), 16 kHz, en un solo WAV estéreo de 12 min 18 s:
  izquierdo OTRA y derecho PROTEGIDA, como los ejemplos de la demo VoIP (`servidor.py` pide «izquierdo otra persona,
  derecho protegida»). Entre línea y línea, 0,6 s; entre conversaciones, 4 s. [`agenda.json`](agenda.json) tiene el
  inicio y el fin de cada línea, ya sin el silencio que deja `say`, y el SHA-256 del WAV. El WAV no va al repo.
- **ASR en la app:** [`app/asr.cpp`](app/asr.cpp) es la lógica de `MotorPorFrases`, `MotorSherpaParakeet` y
  `DetectorSilero` de [`motores.py`](../../../asr-local/motores.py) con la configuración `parakeet-filtro` de la demo
  ([`servidor.py`](../../../voip/servidor.py)): bloques de 640 muestras, corte por silencio de 0,8 s con RMS 0,008,
  Silero (0,5, ventana 512, `min_silence` y `min_speech` en 0) en modo «filtro», preaudio 0,3 s, tope de frase 10 s,
  mínimo de voz 0,3 s, borrador cada 0,5 s con al menos 1 s de voz, Parakeet TDT 0.6B v3 int8 `nemo_transducer`
  greedy con 2 hilos, un reconocedor para los dos canales y un Silero por canal. sherpa-onnx v1.13.8 (la versión del
  proyecto en Python), onnxruntime 1.28.2 estática. El reconocedor va por la API en C; Silero, por
  `sherpa_onnx::VadModel`, lo mismo que usa `VadModel.is_speech` en Python. **Sin los filtros de texto** (borradores
  en otro idioma, muletillas finales): no cambian el cómputo salvo descartar texto.
- **Ritmo real:** el ASR lee el WAV desde una hora de reloj que recibe al lanzarse y procesa cada bloque cuando
  termina en el audio, OTRA y después PROTEGIDA en un solo hilo, como `reproducir_ejemplo` de la demo. Carga los
  modelos antes de esa hora. Anota en `asr.jsonl` cada borrador y cada final (canal, inicio y fin en el audio, hora,
  ms de proceso, texto) con su **atraso**: cuánto después del fin del bloque en el audio quedó listo. Cada 5 s de
  audio anota el atraso y, al final, la mediana, el p95, el máximo y los bloques con más de 1 s.
- **Detector a la vez:** [`ejecutar_agenda.py`](ejecutar_agenda.py) usa el cliente y el detector de
  [`correr_android_latencia.py`](../../correr_android_latencia.py) sin cambios (misma configuración que la corrida
  anterior) y consulta cada línea de OTRA a la hora en que termina en el audio más el corte de 0,8 s, con la misma hora
  de inicio que el ASR. **Consulta sobre el texto original de la línea, no sobre la transcripción.** Si la consulta
  anterior no terminó, la siguiente sale apenas termina y el retraso queda anotado.
- **La app:** la de la corrida anterior ([`main.mm`](../2026-11-20_iphone-15-pro-max-latencia/app/main.mm)), compilada
  con `CON_ASR` junto con `asr.cpp` ([`app/CMakeLists.txt`](app/CMakeLists.txt)). Sin esa opción, `main.mm` es la de
  la corrida anterior; con ella y la variable `ASR_WAV`, arranca el hilo del ASR. Sigue anotando memoria y estado
  térmico cada 5 s en `recursos.log`.
- **Sin cable:** el teléfono está emparejado con la Mac por la red: `devicectl` instaló la app y copió el modelo
  (3,26 GB en unos 3 min), los modelos del ASR y el audio por Wi-Fi. Para medir, `llama-server` escucha en `0.0.0.0` y
  la Mac le pega a la IP del teléfono en la Wi-Fi. [`medir.py`](medir.py) mide antes el ida y vuelta de `/health`.
  **El tiempo por línea incluye la Wi-Fi** y no es comparable directamente con `metal`, que fue por USB: por eso se
  agrega «servidor por línea» (procesar + generar, según `llama-server`) y una segunda pasada sin ASR por Wi-Fi al
  mismo ritmo. Que el servidor de la app atienda por la red local no se pudo verificar todavía; el `Info.plist` lleva
  `NSLocalNetworkUsageDescription` por si iOS pide el permiso.
- **[`resumir.py`](resumir.py)** pasa cada pasada por `resumen()` del [`resumir.py`](../2026-11-20_iphone-15-pro-max-latencia/resumir.py)
  anterior y agrega el servidor por línea, el retraso de las consultas, el ASR y las muestras de estado térmico.

## Pasadas previstas

| Pasada | ASR | Para qué |
|---|---|---|
| `asr-y-detector` | sí | La medición: memoria, latencia del detector con el ASR compitiendo, atraso del ASR, estado térmico. |
| `solo-detector` | no | Mismo ritmo y misma Wi-Fi sin ASR: separa el efecto del ASR del efecto del ritmo y de la red. |

Una pasada de cada una, con el teléfono frío y desenchufado, la primera antes.

## Prueba en seco en la Mac

[`seco-mac/`](seco-mac/): la pasada completa, 12 min 18 s a ritmo real, con el `llama-server` del mismo commit
compilado para macOS y `asr.cpp` compilado como binario de Mac ([`app/asr_mac.cpp`](app/asr_mac.cpp)), en la Mac de
Mateo (M4). Sirve para saber que el audio, la agenda, el ASR, el ejecutor y el resumen funcionan. **No es una
medición del teléfono.**

- Detector: 83/83 consultas válidas, 5 primeros avisos con su motivo. Riesgo igual en las 83 líneas que en la prueba
  en seco del 2026-11-20 (sin ASR ni ritmo). Las consultas salieron a su hora: retraso máximo 0,01 s.
- ASR: terminó el audio (18.449 bloques) con atraso mediano de 0,006 s, p95 0,137 s y máximo 0,607 s; ningún bloque
  con más de 1 s. 167 finales y 851 borradores. Cargar Parakeet y Silero, con una pasada de calentamiento, tardó 0,9 s.
- **El ASR en C++ da lo mismo que el de Python:** [`comparar_con_python.py`](comparar_con_python.py) corre
  `MotorSherpaParakeet` de `motores.py` con `sherpa-onnx==1.13.8` sobre el mismo WAV y la misma configuración (sin
  filtros de texto). Los 1018 eventos de `seco-mac/asr.jsonl` (tipo, canal, segmento, inicio, fin y texto) coinciden
  uno a uno con los de Python.

## Qué hizo Mateo a mano

Pendiente de la pasada en el teléfono. Antes de esta corrida: borró la app del teléfono.

## Límites

- **Audio sintético (TTS):** no dice nada sobre la calidad de transcripción con voz humana.
- **El detector consulta sobre el texto original, no sobre la transcripción.** El ASR compite por recursos pero su
  salida no entra al detector.
- **Audio leído de un archivo,** no del micrófono ni de una llamada. En un iPhone, una app de terceros no tiene
  interfaz para el audio de una llamada telefónica (ver [Límites de la corrida anterior](../2026-11-20_iphone-15-pro-max-latencia/README.md#límites)).
- **Sin los filtros de texto del ASR** (idioma y muletillas).
- **Seis conversaciones, una pasada** por condición.
- **Mide recursos y latencia, no detección.**
- La hora de inicio la fija la Mac y el teléfono la usa con su propio reloj; los dos se sincronizan por red, pero la
  diferencia entre los relojes no se midió. Afecta cuándo sale cada consulta respecto del audio, no las latencias.
- El WAV entero no se carga en memoria: se lee bloque por bloque del archivo.

## Archivos

- [`sintetizar.py`](sintetizar.py) y [`agenda.json`](agenda.json): el audio y la agenda.
- [`app/`](app/): `asr.cpp`, `asr.h`, `asr_mac.cpp` (prueba en seco) y `CMakeLists.txt`.
- [`construir.sh`](construir.sh): compila sherpa-onnx para iOS y macOS, la app y `asr-mac`. Los pasos se corrieron a
  mano con estas opciones; el script entero no se corrió de punta a punta.
- [`ejecutar_agenda.py`](ejecutar_agenda.py), [`medir.py`](medir.py), [`resumir.py`](resumir.py),
  [`comparar_con_python.py`](comparar_con_python.py).
- [`seco-mac/`](seco-mac/): `turnos.jsonl`, `asr.jsonl`, `manifiesto.json`, `medir.json`, `ejecucion.log`.

## Repetir

Con lo de la [corrida anterior](../2026-11-20_iphone-15-pro-max-latencia/README.md#repetir) (Xcode, `cmake`, el GGUF
verificado, `construir.sh` de esa carpeta) y los modelos del ASR del release `asr-models` de sherpa-onnx
(`silero_vad.onnx`, SHA-256 `9e2449e1…`, el del proyecto; `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2`):

```sh
python3 -I sintetizar.py audio.wav
./construir.sh CARPETA_DE_TRABAJO TEAM_ID ID.DE.LA.APP UDID
xcrun devicectl device install app --device UDID CARPETA_DE_TRABAJO/app-asr/Release-iphoneos/DetectorLab.app
# copiar con `xcrun devicectl device copy to ... --domain-type appDataContainer --domain-identifier ID.DE.LA.APP`:
#   gemma.gguf -> Documents/gemma.gguf, audio.wav -> Documents/audio.wav,
#   silero_vad.onnx -> Documents/asr/silero_vad.onnx, los cuatro archivos de Parakeet -> Documents/asr/parakeet/
python3 -I medir.py asr-y-detector --asr --ip IP_DEL_TELEFONO --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99
python3 -I medir.py solo-detector --ip IP_DEL_TELEFONO --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99
python3 -I resumir.py asr-y-detector solo-detector seco-mac
```

La prueba en seco, con el `llama-server` de la Mac levantado en el puerto 18080:

```sh
python3 -I medir.py seco-mac --asr --local CARPETA_DE_TRABAJO/asr-mac --audio audio.wav --modelos MODELOS --margen 45 -- -ngl 99
```
