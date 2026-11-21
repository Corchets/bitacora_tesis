# iphone-15-pro-max-asr-y-detector — 2026-11-21

Tercera medición en teléfono de [#141](https://github.com/Corchets/bitacora_tesis/issues/141): el detector con la
configuración final ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)) y el ASR del
proyecto, `parakeet-filtro` ([ADR 0001](../../../../docs/ingenieria/adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)),
corriendo a la vez en el iPhone 15 Pro Max de Mateo, con audio sintético a ritmo de conversación. Sigue a la
[medición del detector solo](../2026-11-20_iphone-15-pro-max-latencia/README.md) del 2026-11-20. **Mide memoria,
latencia y estado térmico, no detección ni calidad de transcripción.** No cierra D08 ni D09.

> **Estado al 2026-11-21: medido.** Dos pasadas en el teléfono, sin cable, una por condición: con ASR y detector, y
> solo el detector al mismo ritmo. iOS no cerró la app.

## Resultado

- **Teléfono:** iPhone 15 Pro Max (`iPhone16,2`), iOS 27.0.1 (24A446), 7,48 GiB de memoria física. **Desenchufado**
  (`cargando=0` en todas las muestras), Modo de bajo consumo apagado (`bajo_consumo=0` en todas), estado térmico
  `nominal` al empezar las dos pasadas. Batería: 75 % → 70 % en la primera pasada y 70 % → 65 % en la segunda.
- **Red:** Wi-Fi, con `llama-server` escuchando en `0.0.0.0`. Ida y vuelta de `/health`: 16 ms de mediana en las dos
  pasadas. iOS no pidió permiso de red local.
- Las 83 consultas de cada pasada fueron válidas. **El riesgo coincide en las 83 líneas** entre las dos pasadas, con
  la corrida `metal` del 2026-11-20 y con la prueba en seco de la Mac.

### 1. Memoria: entra

| Pasada | Pico de `footprint` | Pico residente | Mínimo disponible antes del límite |
|---|---:|---:|---:|
| `asr-y-detector` | 1,39 GiB | 2,62 GiB | 1,92 GiB |
| `solo-detector` | 0,58 GiB | 3,03 GiB | 2,73 GiB |
| `metal` (2026-11-20) | 0,58 GiB | 2,98 GiB | 2,71 GiB |

El ASR suma unos 0,8 GiB de `footprint`, que es lo que iOS cuenta contra el límite de la app: con los dos corriendo
quedaron al menos 1,92 GiB libres antes del límite. iOS no cerró la app. El pico residente es menor con el ASR que sin
él: se infiere que iOS sacó de memoria páginas del GGUF mapeado (que no cuentan contra el límite y se vuelven a leer
del archivo), pero no se verificó.

### 2. Latencia del detector: el ASR no la empeora en esta pasada

Tiempos en segundos, con las definiciones de la [corrida anterior](../2026-11-20_iphone-15-pro-max-latencia/README.md#resultado).
«Por línea» incluye la red (USB en `metal`, Wi-Fi acá); «servidor por línea» es procesar + generar según
`llama-server`, sin la red, y es la columna comparable entre las tres.

| Pasada | Conexión | Ritmo | Por línea: mediana / p95 / máx. | Servidor por línea: mediana / p95 / máx. | Procesar / generar (medianas) | Primer aviso con motivo: mediana / máx. | Sin esperar el motivo: mediana / máx. |
|---|---|---|---:|---:|---:|---:|---:|
| [`asr-y-detector`](asr-y-detector/) | Wi-Fi | real | 0,75 / 0,84 / 1,15 | 0,66 / 0,70 / 1,09 | 0,15 / 0,50 | 2,97 / 3,54 | 0,75 / 0,76 |
| [`solo-detector`](solo-detector/) | Wi-Fi | real | 0,82 / 0,93 / 0,94 | 0,69 / 0,72 / 0,72 | 0,18 / 0,51 | 3,29 / 3,55 | 0,86 / 0,90 |
| [`metal`](../2026-11-20_iphone-15-pro-max-latencia/metal/) (sin ASR) | USB | seguido | 0,79 / 1,03 / 1,10 | 0,77 / 1,01 / 1,07 | 0,21 / 0,56 | 3,22 / 4,48 | 0,72 / 0,92 |

- Con el ASR, el servidor tardó 0,66 s de mediana por línea contra 0,69 s sin ASR al mismo ritmo y 0,77 s en
  `metal`. **No se ve que el ASR empeore la latencia del detector:** la diferencia es chica, va para el otro lado y sale
  de una pasada por condición. El máximo de 1,09 s con ASR es una sola línea (p95 0,70 s).
- Que las dos pasadas de hoy sean más rápidas que `metal` es compatible con que `metal` corrió enchufado y en `fair` y
  `serious`; es una inferencia, no se aisló.
- Las consultas salieron a su hora: retraso máximo de 0,006 s con ASR y 0,01 s sin ASR. Ninguna esperó a la anterior.
- La diferencia de «por línea» entre las dos pasadas de hoy (0,75 contra 0,82 s) es casi toda red: el servidor
  difiere en 0,03 s.

### 3. Estado térmico

| Pasada | Hora | Muestras por estado (cada 5 s) |
|---|---|---|
| `asr-y-detector` | 13:10–13:25 | 95 `nominal`, 86 `fair` (desde las 13:18:16, unos 5 min y medio después de empezar el audio) |
| `solo-detector` | 13:45–14:00 | 181 `nominal` |
| `metal` (2026-11-20, enchufado) | 20:08–20:10 | 12 `fair`, 10 `serious` |

Sin cable y empezando en `nominal`, ninguna pasada llegó a `serious`. Con el ASR llegó a `fair`; sin él quedó en `nominal` las 15 min.
Entre una pasada y otra la app estuvo cerrada 20 min. Se infiere que el ASR suma calor, pero es una pasada por
condición y no se sabe cuánto había reposado el teléfono antes de la primera: las dos empezaron en `nominal`.

### ASR en el teléfono

- **Va a tiempo real:** terminó el audio (18.449 bloques, 737,9 s) con atraso mediano de 0,006 s, p95 0,172 s y máximo
  0,475 s; ningún bloque con más de 1 s. Cada final quedó listo 0,235 s de mediana después del fin de su frase en el
  audio (máximo 0,475 s), y, contando el corte de 0,8 s, alrededor de 1 s después del fin de la voz.
- Transcribir una frase al cerrarla tardó 230 ms de mediana (máximo 470 ms); un borrador, 152 ms.
- Cargar Parakeet y Silero, con la pasada de calentamiento, tardó 4,4 s.
- Salieron 167 finales y 851 borradores. De los 1018 eventos, 1017 son iguales a los de la prueba en seco de la Mac;
  uno, un borrador, cambia una palabra.

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
  mismo ritmo. El `Info.plist` lleva `NSLocalNetworkUsageDescription` por si iOS pedía el permiso de red local; no lo
  pidió.
- **[`resumir.py`](resumir.py)** pasa cada pasada por `resumen()` del [`resumir.py`](../2026-11-20_iphone-15-pro-max-latencia/resumir.py)
  anterior y agrega el servidor por línea, el retraso de las consultas, el ASR y las muestras de estado térmico.

## Qué se corrió

| Pasada | Audio desde | ASR | Para qué |
|---|---|---|---|
| `asr-y-detector` | 13:12:49 | sí | La medición: memoria, latencia del detector con el ASR compitiendo, atraso del ASR, estado térmico. |
| `solo-detector` | 13:48:11 | no | Mismo ritmo y misma Wi-Fi sin ASR: separa el efecto del ASR del efecto del ritmo y de la red. |

Una pasada de cada una, en ese orden, el 2026-11-21. Entre las dos, la app estuvo cerrada 20 min para que el teléfono
se enfriara. Las dos se lanzaron por Wi-Fi con `devicectl` y [`medir.py`](medir.py); en los manifiestos se reemplazó
la IP del teléfono por `IP_DEL_TELEFONO`.

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

1. Antes de esta corrida había borrado la app del teléfono. Se reinstaló y se copiaron los archivos por Wi-Fi.
2. Volvió a confiar en el certificado (Ajustes → General → VPN y gestión de dispositivos).
3. Dejó el teléfono desbloqueado.

Se le pidió además apagar la VPN y el Modo de bajo consumo, desenchufar el teléfono y dejarlo frío en la misma Wi-Fi
que la Mac. Confirmó solo el certificado y el desbloqueo. Lo que anotó la app: desenchufado y sin bajo consumo en
todas las muestras, `nominal` al empezar. **Si la VPN estaba apagada no se sabe:** la app no lo anota. La Mac llegó
igual al servidor por la Wi-Fi local, con 16 ms de ida y vuelta.

Todo lo demás se hizo desde la Mac: compilar, firmar, instalar, copiar el modelo, lanzar la app y traer los registros.

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
- **La comparación con `metal` mezcla tres cambios:** red (USB contra Wi-Fi), ritmo (seguido contra real) y estado
  del teléfono (enchufado y caliente contra desenchufado y frío). Para el efecto del ASR, la comparación es contra
  `solo-detector`.
- **No se midió consumo de batería** más allá del nivel que informa iOS (en pasos de 5 %).
- **Que la VPN estuviera apagada no está verificado.**

## Archivos

- [`sintetizar.py`](sintetizar.py) y [`agenda.json`](agenda.json): el audio y la agenda.
- [`app/`](app/): `asr.cpp`, `asr.h`, `asr_mac.cpp` (prueba en seco) y `CMakeLists.txt`.
- [`construir.sh`](construir.sh): compila sherpa-onnx para iOS y macOS, la app y `asr-mac`. Los pasos se corrieron a
  mano con estas opciones; el script entero no se corrió de punta a punta.
- [`ejecutar_agenda.py`](ejecutar_agenda.py), [`medir.py`](medir.py), [`resumir.py`](resumir.py),
  [`comparar_con_python.py`](comparar_con_python.py).
- [`asr-y-detector/`](asr-y-detector/) y [`solo-detector/`](solo-detector/): las pasadas del teléfono
  (`turnos.jsonl`, `manifiesto.json`, `medir.json`, `recursos.log`, `runtime.log`, `ejecucion.log` y, con ASR,
  `asr.jsonl`).
- [`resumen.json`](resumen.json): la salida de `resumir.py`, con `metal` como referencia.
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
