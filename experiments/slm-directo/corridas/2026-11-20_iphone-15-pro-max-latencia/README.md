# iphone-15-pro-max-latencia — 2026-11-20

Segunda medición en teléfono de [#141](https://github.com/Corchets/bitacora_tesis/issues/141): la configuración final
del detector ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)) en el iPhone 15 Pro
Max de Mateo, comparable con las del Samsung Galaxy A56
([2026-11-10](../2026-11-10_a56-congelada-latencia/README.md) y [2026-11-11](../2026-11-11_a56-latencia-172/README.md)).
**Mide latencia y memoria, no detección.** No cierra D08 ni D09.

> **Estado al 2026-11-20: medido.** Cuatro corridas en el teléfono, una pasada cada una. La comparación del prompt
> final contra el A56 queda a medias: el A56 todavía no tiene una corrida con `c-consejos-corte-riesgo`.

## Resultado

- **Teléfono:** iPhone 15 Pro Max (`iPhone16,2`), iOS 27.0.1 (24A446), 7,48 GiB de memoria física, 6 núcleos,
  enchufado a la Mac y cargando, batería entre 85 y 90 %.
- **Runtime:** llama.cpp `6c01da62`, el commit del A56, dentro de la app de [`app/`](app/). GPU con Metal
  (`-ngl 99`) o CPU con 4 hilos (`-ngl 0 -t 4`).
- Las 83 consultas de cada corrida fueron válidas, con 14 tokens generados. iOS no cerró la app en ninguna.

Tiempos en segundos. «Por línea» es la actualización de una línea de OTRA sin motivo (n=78); «primer aviso», la línea
del primer aviso de cada conversación (n=5 en todas). Procesar y generar son medianas de lo que informa el servidor.

| Corrida | Teléfono | Prompt | Por línea: mediana / p95 / máx. | Procesar | Generar | Primer aviso con motivo: mediana / máx. | Sin esperar el motivo: mediana / máx. |
|---|---|---|---:|---:|---:|---:|---:|
| [`metal`](metal/) | iPhone, Metal | `c-consejos` | 0,79 / 1,03 / 1,10 | 0,21 | 0,56 | 3,22 / 4,48 | 0,72 / 0,92 |
| [`cpu-t4`](cpu-t4/) | iPhone, CPU 4 hilos | `c-consejos` | 2,01 / 2,41 / 3,32 | 0,95 | 1,03 | 6,50 / 8,89 | 1,68 / 2,38 |
| [`metal-premisa`](metal-premisa/) | iPhone, Metal | `c-premisa` | 0,94 / 1,02 / 1,10 | 0,25 | 0,67 | 4,28 / 5,32 | 0,87 / 1,03 |
| [`cpu-t4-premisa`](cpu-t4-premisa/) | iPhone, CPU 4 hilos | `c-premisa` | 2,16 / 2,32 / 2,39 | 1,06 | 1,09 | 7,51 / 9,49 | 2,03 / 2,22 |
| [`s6-base-t4`](../2026-11-11_a56-latencia-172/s6-base-t4/) | A56, CPU 4 hilos | `c-premisa` | 3,74 / 4,16 / 5,49 | 1,94 | 1,75 | 13,84 / 16,08 | 3,68 / 4,01 |

Las filas salen de [`resumir.py`](resumir.py), la del A56 incluida; los números completos están en
[`resumen.json`](resumen.json).

### Lectura

- **Con el mismo prompt (`c-premisa`), el iPhone con Metal tarda 0,94 s por línea contra 3,74 s del A56**, unas 4
  veces menos. Con CPU y 4 hilos, como el A56, tarda 2,16 s, 1,7 veces menos.
- **Con la configuración final, 0,79 s por línea con Metal** (p95 1,03 s) y 2,01 s con CPU. El primer aviso tarda
  0,72 s de mediana sin esperar el motivo y 3,22 s con el motivo.
- **Falta la fila del A56 con el prompt final.** En el repo, el A56 corrió con `c-premisa-corte-riesgo` (2026-11-11)
  y con `c-json-corte-riesgo` (2026-11-10). La comparación de tiempos del prompt final se completa cuando esa
  corrida esté.
- **Que `-ngl 99` usó la GPU se infiere, no se leyó en el log:** `runtime.log` no registra las capas enviadas a Metal.
  Lo indican que la corrida con `-ngl 0` es 2,5 veces más lenta y que el riesgo de `metal` coincide en las 83 líneas
  con el de la Mac, que también corre con Metal ([`seco-mac/`](seco-mac/)).

### Memoria

| Corrida | Pico de `footprint` | Pico residente |
|---|---:|---:|
| `metal` | 0,58 GiB | 2,98 GiB |
| `cpu-t4` | 0,63 GiB | 3,16 GiB |
| `metal-premisa` | 0,71 GiB | 3,20 GiB |
| `cpu-t4-premisa` | 0,74 GiB | 3,22 GiB |
| A56 `s6-base-t4` | — | 3,53 GiB (`VmHWM`) |

El `footprint` es lo que iOS cuenta contra el límite de la app; el GGUF mapeado no entra ahí. El pico residente es lo
comparable con `VmHWM`. Al empezar la primera corrida la app tenía 3,29 GiB disponibles antes del límite.

### Estado térmico

El teléfono llegó a `serious` en las cuatro corridas, y las dos últimas corrieron enteras en ese estado:

| Corrida | Hora | Muestras por estado |
|---|---|---|
| `metal` | 20:08–20:10 | 12 `fair`, 10 `serious` |
| `cpu-t4` | 20:16–20:20 | 7 `nominal`, 8 `fair`, 26 `serious` |
| `metal-premisa` | 20:22–20:24 | 22 `serious` |
| `cpu-t4-premisa` | 20:26–20:29 | 44 `serious` |

Antes de la primera corrida se copió el modelo por el cable y el teléfono estuvo cargando todo el tiempo. No se sabe
cuánto de cada tiempo se debe a que iOS limita el rendimiento en ese estado: no hay una corrida en frío para comparar.

### Riesgo contra el A56 (dato del runtime, no de detección)

Con `c-premisa-corte-riesgo`, contra `s6-base-t4`:

- `metal-premisa`: riesgo distinto en 12 de 83 líneas.
- `cpu-t4-premisa`: riesgo distinto en 13 de 83 líneas.
- En ninguna de las dos cambia la línea del primer aviso de ninguna conversación.
- Dentro del iPhone, Metal contra CPU: 4 de 83 líneas con `c-premisa` y 7 de 83 con `c-consejos`, también sin mover
  el primer aviso.

Las líneas están en `resumen.json`. Es más que la 1 de cada 10 de
[H11](../../../../docs/hallazgos/H11-el-riesgo-cambia-con-el-runtime.md), con seis conversaciones.

## Cómo se mide

- **El mismo servidor que en el A56.** Una app mínima ([`app/`](app/main.mm)) corre dentro de su proceso el
  `llama-server` de llama.cpp `6c01da62`, el commit del A56, compilado para iOS con Metal. No tiene interfaz.
- **El mismo ejecutor, sin cambios.** [`correr_android_latencia.py`](../../correr_android_latencia.py) corre en la Mac
  contra `127.0.0.1:18080`. `iproxy` (libimobiledevice) reenvía ese puerto al teléfono por el cable, como `adb forward`
  en el A56. El tiempo total por línea incluye ese salto por USB; los tiempos de procesar y generar los informa el
  servidor y no lo incluyen.
- **[`medir.py`](medir.py)** relanza la app con los parámetros de cada corrida, corre el ejecutor y trae del teléfono
  `recursos.log` y `runtime.log`. **[`resumir.py`](resumir.py)** arma la tabla, con las corridas del A56 pasadas por
  el mismo código.
- **Se eligió este camino y no una app del App Store** porque las que exponen un servidor local (PocketPal Plus,
  LLM Server) no devuelven los tiempos de llama.cpp ni dejan leer memoria o estado térmico, y la de PocketPal no acepta
  `grammar`: sin gramática, en el A56 la coma del riesgo quedó fuera de los 14 tokens
  ([primer intento del 2026-11-10](../2026-11-10_a56-congelada-latencia/README.md#primer-intento-esquema-ignorado-por-llama-server)).
  Lo de PocketPal se leyó en su código (`src/services/localApiServer/wire.ts`, commit `ed0b9654`); lo de LLM Server,
  en su ficha del App Store, que no documenta esos campos.

## Configuración

- **Detector:** prompt `c-consejos-corte-riesgo`, `num_predict` 14, aviso con riesgo ≥ 0,3, motivo solo en el primer
  aviso, consulta solo en las líneas de OTRA, `--hablantes rol`, contexto 4096, temperatura 0, seed 42.
- **Modelo:** el mismo GGUF que el A56, la capa de modelo de `gemma4:e2b-it-q4_K_M` de Ollama, bajada del registro
  de Ollama sin Ollama. SHA-256 verificado: `6dd7ac24fe13a238898e16e253ebc7a72fa27fb83f2658c2f6c241df3af5937d`
  (3.502.493.472 bytes), el que registra el [diagnóstico del A56](../2026-11-06-a56-diagnostico.md).
- **Conversaciones:** las seis de desarrollo de
  [`conversaciones-sub-6.json`](../2026-11-11_a56-latencia-172/conversaciones-sub-6.json), 168 líneas y 83 consultas.
  Nada de la reserva de test.
- **Recorrido:** todas las líneas, aunque ya haya avisado, como en el A56.
- **Servidor:** `-c 4096 -np 1 --no-webui`, caché del prefijo activa, más lo que cambie en cada corrida (`-ngl`, `-t`).

## Qué se corrió

Una pasada por configuración, en este orden. Entre una y otra la app estuvo cerrada entre dos y seis minutos:

| Corrida | Prompt | Servidor | Para qué |
|---|---|---|---|
| `metal` | `c-consejos-corte-riesgo` | `-ngl 99` | La medición: configuración final con GPU. |
| `cpu-t4` | `c-consejos-corte-riesgo` | `-ngl 0 -t 4` | CPU con 4 hilos, como el A56. |
| `metal-premisa` | `c-premisa-corte-riesgo` | `-ngl 99` | Riesgo línea por línea contra el A56. |
| `cpu-t4-premisa` | `c-premisa-corte-riesgo` | `-ngl 0 -t 4` | Lo mismo, con el backend más parecido al del A56. |

## Prueba en seco en la Mac

[`seco-mac/`](seco-mac/) es el recorrido completo con el `llama-server` del mismo commit compilado para macOS con las
opciones previstas para iOS, en la Mac de Mateo (M4, Metal): 83/83 consultas válidas, 14 tokens generados por
consulta, 5 primeros avisos con su motivo. Sirve para saber que el ejecutor, el prompt final, la gramática y el
resumen funcionan. **No es una medición del teléfono** y sus tiempos no van a ninguna tabla.

## Qué hizo Mateo a mano

1. Instalar Xcode (27.2) desde el App Store, con el componente de iOS.
2. Iniciar sesión con su cuenta de Apple en Xcode → Settings → Accounts y crear el certificado en Manage
   Certificates → «+» → Apple Development. Alcanza la cuenta gratuita: la firma vence a los 7 días
   ([Apple](https://developer.apple.com/support/compare-memberships/)).
3. Conectar el iPhone por cable, desbloquearlo y tocar «Confiar».
4. Activar Ajustes → Privacidad y seguridad → Modo de desarrollador, que reinicia el teléfono.
5. Después de la instalación, confiar en el certificado en Ajustes → General → VPN y gestión de dispositivos.
6. Dejar el teléfono desbloqueado, con la app en pantalla, mientras corría cada configuración. iOS suspende la app, y
   con ella el servidor, si pasa a segundo plano.

Todo lo demás se hizo desde la Mac: compilar, firmar, instalar, copiar el modelo (1 min 41 s por el cable), lanzar la
app y traer los registros.

## Límites

- **Solo el detector.** No hay ASR ni audio.
- **En un iPhone el sistema completo no se puede mostrar como producto.** La documentación de Apple no ofrece a una
  app de terceros ninguna interfaz para el audio de una llamada telefónica:
  [CallKit](https://developer.apple.com/documentation/callkit) cubre la interfaz de llamada de los servicios VoIP de
  la propia app y la identificación y el bloqueo de números, y una llamada entrante interrumpe la sesión de audio de
  la app ([Handling audio interruptions](https://developer.apple.com/documentation/avfaudio/handling-audio-interruptions)).
  Ninguna de las dos páginas dice con esas palabras que esté prohibido: lo que se verificó es que la interfaz no
  existe. iOS sigue fuera de alcance como plataforma (D09 en
  [MAPA-DECISIONES.md](../../../../docs/gestion/MAPA-DECISIONES.md)).
- **Otro runtime mueve el riesgo.** Metal en vez de CPU, y otro teléfono, cambian el riesgo en parte de las líneas
  ([H11](../../../../docs/hallazgos/H11-el-riesgo-cambia-con-el-runtime.md),
  [H13](../../../../docs/hallazgos/H13-la-misma-configuracion-corrida-de-otro-modo.md)). Las diferencias de riesgo
  que salgan de acá son un dato del runtime, no una evaluación de detección.
- **La memoria no se mide igual en los dos teléfonos.** En el A56 es `VmHWM`, que cuenta las páginas del GGUF
  mapeado. En iOS se anotan dos cosas: el pico de `footprint`, que es lo que el sistema cuenta contra el límite de la
  app, y el pico residente, que es lo más parecido a `VmHWM`. El iPhone tiene 8 GB: si iOS cierra la app por memoria,
  eso es un resultado. No pasó en estas corridas.
- **Temperatura:** iOS no da la temperatura a una app; se anota el estado térmico (`nominal`, `fair`, `serious`,
  `critical`) cada 5 s.
- Seis conversaciones y una pasada por configuración: alcanza para diferencias grandes, no para estimar variabilidad.
- **Teléfono enchufado y cargando.** No se midió con batería sola ni se midió consumo.
- **El tiempo por línea incluye el salto por USB** (`iproxy`), como el de `adb forward` en el A56. Procesar y generar
  no lo incluyen.

## Archivos

- [`app/`](app/): `main.mm`, `Info.plist` y `CMakeLists.txt` de la app.
- [`construir.sh`](construir.sh): compila llama.cpp para iOS y arma la app firmada.
- [`medir.py`](medir.py) y [`resumir.py`](resumir.py).
- [`metal/`](metal/), [`cpu-t4/`](cpu-t4/), [`metal-premisa/`](metal-premisa/) y [`cpu-t4-premisa/`](cpu-t4-premisa/):
  las corridas del teléfono (`turnos.jsonl`, `manifiesto.json`, `medir.json`, `recursos.log`, `runtime.log`,
  `ejecucion.log`).
- [`resumen.json`](resumen.json): el resumen de las corridas y las diferencias de riesgo.
- [`seco-mac/`](seco-mac/): la prueba en seco (`turnos.jsonl`, `manifiesto.json`, `medir.json`, `ejecucion.log`).

## Repetir

Con Xcode, `cmake` e `iproxy` (`brew install cmake libimobiledevice`), y el GGUF bajado y verificado:

```sh
curl -L -o gemma.gguf https://registry.ollama.ai/v2/library/gemma4/blobs/sha256:6dd7ac24fe13a238898e16e253ebc7a72fa27fb83f2658c2f6c241df3af5937d
shasum -a 256 gemma.gguf
./construir.sh CARPETA_DE_TRABAJO TEAM_ID ID.DE.LA.APP UDID
xcrun devicectl device install app --device UDID CARPETA_DE_TRABAJO/app/Release-iphoneos/DetectorLab.app
xcrun devicectl device copy to --device UDID --domain-type appDataContainer --domain-identifier ID.DE.LA.APP --source gemma.gguf --destination Documents/gemma.gguf
python3 -I medir.py metal --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99
python3 -I resumir.py metal cpu-t4 metal-premisa cpu-t4-premisa ../2026-11-11_a56-latencia-172/s6-base-t4 \
    --riesgo metal-premisa ../2026-11-11_a56-latencia-172/s6-base-t4 \
    --riesgo cpu-t4-premisa ../2026-11-11_a56-latencia-172/s6-base-t4 \
    --riesgo metal cpu-t4 --riesgo metal-premisa cpu-t4-premisa --riesgo metal seco-mac
```

La prueba en seco, con un `llama-server` del mismo commit ya levantado en la Mac en el puerto 18080:

```sh
python3 -I medir.py seco-mac --local -- -ngl 99
```
