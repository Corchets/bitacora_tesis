# iphone-15-pro-max-latencia — 2026-11-20

Segunda medición en teléfono de [#141](https://github.com/Corchets/bitacora_tesis/issues/141): la configuración final
del detector ([ADR 0008](../../../../docs/ingenieria/adr/0008-prompt-del-detector-c-consejos.md)) en el iPhone 15 Pro
Max de Mateo, comparable con las del Samsung Galaxy A56
([2026-11-10](../2026-11-10_a56-congelada-latencia/README.md) y [2026-11-11](../2026-11-11_a56-latencia-172/README.md)).
**Mide latencia y memoria, no detección.** No cierra D08 ni D09.

> **Estado al 2026-11-20: la app compila para iOS, sin firmar. Falta la corrida en el teléfono.** No hay ningún número
> del iPhone todavía. Xcode 27.2 ya está instalado y el iPhone (iOS 27.0.1) está emparejado por cable con el modo de
> desarrollador activo; falta el certificado de desarrollo de la cuenta de Apple de Mateo para firmar e instalar
> ([lista](#qué-tiene-que-hacer-mateo-a-mano)).

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

## Qué se va a correr

Una pasada por configuración:

| Corrida | Prompt | Servidor | Para qué |
|---|---|---|---|
| `metal` | `c-consejos-corte-riesgo` | `-ngl 99` | La medición: configuración final con GPU. |
| `cpu-t4` | `c-consejos-corte-riesgo` | `-ngl 0 -t 4` | CPU con 4 hilos, como el A56. |
| `metal-premisa` | `c-premisa-corte-riesgo` | `-ngl 99` | Riesgo línea por línea contra el A56. |
| `cpu-t4-premisa` | `c-premisa-corte-riesgo` | `-ngl 0 -t 4` | Lo mismo, con el backend más parecido al del A56. |

Las corridas del A56 que hay en el repo usaron `c-premisa-corte-riesgo` (2026-11-11) y `c-json-corte-riesgo`
(2026-11-10), no el prompt final. Por eso el riesgo se compara con `c-premisa`, contra
[`s6-base-t4`](../2026-11-11_a56-latencia-172/s6-base-t4/). Cuando esté la corrida del A56 con el prompt final, se
compara también con esa.

## Prueba en seco en la Mac

[`seco-mac/`](seco-mac/) es el recorrido completo con el `llama-server` del mismo commit compilado para macOS con las
opciones previstas para iOS, en la Mac de Mateo (M4, Metal): 83/83 consultas válidas, 14 tokens generados por
consulta, 5 primeros avisos con su motivo. Sirve para saber que el ejecutor, el prompt final, la gramática y el
resumen funcionan. **No es una medición del teléfono** y sus tiempos no van a ninguna tabla.

## Qué tiene que hacer Mateo a mano

1. Instalar Xcode desde el App Store y abrirlo una vez para aceptar la licencia e instalar el componente de iOS.
2. Iniciar sesión con su cuenta de Apple en Xcode → Settings → Accounts. Alcanza la cuenta gratuita: la firma vence a
   los 7 días ([Apple](https://developer.apple.com/support/compare-memberships/)).
3. Conectar el iPhone por cable, desbloquearlo y tocar «Confiar».
4. Activar Ajustes → Privacidad y seguridad → Modo de desarrollador, que reinicia el teléfono.
5. Después de la primera instalación, aprobar el certificado en Ajustes → General → VPN y gestión de dispositivos.
6. Dejar el teléfono desbloqueado, con la app en pantalla, mientras corre cada configuración. iOS suspende la app, y
   con ella el servidor, si pasa a segundo plano.

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
  eso es un resultado.
- **Temperatura:** iOS no da la temperatura a una app; se anota el estado térmico (`nominal`, `fair`, `serious`,
  `critical`) cada 5 s.
- Seis conversaciones y una pasada por configuración: alcanza para diferencias grandes, no para estimar variabilidad.
- **Sin probar todavía:** la firma, `iproxy` contra este teléfono y las llamadas a `devicectl` de `medir.py`. El
  build para iOS compila y enlaza sin firmar.

## Archivos

- [`app/`](app/): `main.mm`, `Info.plist` y `CMakeLists.txt` de la app.
- [`construir.sh`](construir.sh): compila llama.cpp para iOS y arma la app firmada.
- [`medir.py`](medir.py) y [`resumir.py`](resumir.py).
- [`seco-mac/`](seco-mac/): la prueba en seco (`turnos.jsonl`, `manifiesto.json`, `medir.json`, `ejecucion.log`).

## Repetir

Con Xcode, `cmake` e `iproxy` (`brew install cmake libimobiledevice`), y el GGUF bajado y verificado:

```sh
curl -L -o gemma.gguf https://registry.ollama.ai/v2/library/gemma4/blobs/sha256:6dd7ac24fe13a238898e16e253ebc7a72fa27fb83f2658c2f6c241df3af5937d
shasum -a 256 gemma.gguf
./construir.sh CARPETA_DE_TRABAJO TEAM_ID ID.DE.LA.APP
xcrun devicectl device install app --device UDID CARPETA_DE_TRABAJO/app/Release-iphoneos/DetectorLab.app
xcrun devicectl device copy to --device UDID --domain-type appDataContainer --domain-identifier ID.DE.LA.APP --source gemma.gguf --destination Documents/gemma.gguf
python3 -I medir.py metal --dispositivo UDID --bundle ID.DE.LA.APP -- -ngl 99
python3 -I resumir.py metal ../2026-11-11_a56-latencia-172/s6-base-t4
```

La prueba en seco, con un `llama-server` del mismo commit ya levantado en la Mac en el puerto 18080:

```sh
python3 -I medir.py seco-mac --local -- -ngl 99
```
