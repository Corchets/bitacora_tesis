# Micrófono del navegador — verificación de #78 (2026-10-26)

Prueba de desarrollo, sin split ni selección de modelos: una llamada TTS conocida
`SC-WA-CODE-01`, sin reserva CV2-T. No mide generalización ni voz real.

Servidor en M1 arm64, 8 núcleos lógicos, 8 GB de RAM, macOS 27.0.1, Python 3.13.15;
Chrome headless 156.0.0.0. Zipformer español local, 2 hilos por motor,
`--detector reglas --disparo final --corte-silencio 0.8`. Seed no aplica a reglas;
la captura y el remuestreo son deterministas, con temporización real del SO.

Versión: `c4a8dd2` más los ajustes posteriores del mismo ticket para traducir errores
nativos desconocidos y cancelar el arranque si se pierde el micrófono. Los manifiestos
conservan su referencia original. **El campo heredado `cambios_sin_commit` consulta la
carpeta de replay y no cubre cambios en voip**: no certifica árbol limpio de esta prueba.
El commit de cierre de #78 contiene dichos ajustes y esta evidencia.

## Resultados

| Camino de protegida | Parciales | Mediana | p95 | Máximo |
|---|---:|---:|---:|---:|
| Micrófono falso → AudioWorklet → `/audio?rol=protegida` | 5 | 0,049 s | 0,053 s | 0,054 s |
| `cliente.mandar_wav` → `/audio?rol=protegida` | 5 | 0,060 s | 0,083 s | 0,087 s |

Medida: `disponible_s - fin_audio_s` de parciales, como `cliente.py`; ambas medianas
son ≤ 0,2 s. El navegador usa el canal derecho convertido a WAV mono de 44,1 kHz como
entrada falsa y un AudioContext de 48 kHz; el cliente lee el estéreo original de 16 kHz.
Es una comprobación funcional, no un benchmark emparejado ni una medición de voz a pantalla.

- La protegida se transcribe: «Me acaba de llegar un SMS, no pedí activar nada» y
  «Es cero, cero, cero, cero, cero, cero». El panel la muestra en burbujas de protegida.
- Navegador + ejemplo: solamente el canal izquierdo del ejemplo entra como `otra`.
  El transporte envió 554 mensajes de **1.280 bytes**; intervalo mediano 38,1 ms
  (bloques de audio de 40 ms con variación del planificador). Se recibieron 22,16 s
  de protegida antes de finalizar el ejemplo de 22,217 s.
- El ejemplo finaliza y libera la captura: todos los tracks inspeccionados quedan
  en `ended`; el panel termina sin error ni rechazos de promesas.
- Se enumeraron tres entradas falsas; seleccionar la última aplica su `deviceId`
  exacto al stream. Otra llamada con esa entrada + fuente `cliente.py` se terminó
  manualmente por el botón: track `ended` y registro guardado.
- Casos inyectados en Chrome: `NotAllowedError`, `NotFoundError`,
  `OverconstrainedError`, `NotReadableError`, `AbortError` y contexto inseguro.
  Todos dejan un mensaje en castellano y permiten reintentar. Son simulaciones de
  API/contexto, no pruebas del diálogo de permisos del sistema operativo.
- Regresión de revisión: evento `ended` entre preparar el emisor y enviar `iniciar`.
  El panel muestra «Se desconectó la entrada de audio…», cancela el arranque,
  deja el botón habilitado y todos los tracks terminados.
- Recursos de página observados: módulo local y favicon local; el worklet y su import
  se sirven por el mismo servidor. Sin dependencias ni recursos externos en el panel.

Archivos: [navegador](navegador/manifiesto.json), [cliente](cliente/manifiesto.json),
[comprobaciones del navegador](comprobaciones.json),
[captura con micrófono](panel-microfono.png). JSONL y manifiestos conservados sin WAV.
Audio y scripts temporales usados: `/tmp/voip78-microfono.wav`, `/tmp/voip78-llamadas/`,
`/tmp/voip78-cdp.py`, `/tmp/voip78-guion.py`, `/tmp/voip78-casos.py`,
`/tmp/voip78-baseline.py`. No se incorporaron a Git.

## Reproducción

Desde la raíz del repo, prepará el canal derecho como entrada falsa fuera de Git:

```bash
.venv/bin/python - <<'PY'
import numpy as np
import soundfile as sf
x, hz = sf.read('experiments/asr-local/audio/SC-WA-CODE-01-tts-estereo.wav')
y = np.interp(np.arange(round(len(x)*44100/hz))*hz/44100, np.arange(len(x)), x[:, 1])
sf.write('/tmp/voip78-microfono.wav', y, 44100, subtype='PCM_16')
PY
cd experiments/voip
../../.venv/bin/python servidor.py --host 127.0.0.1 --puerto 8788 --detector reglas --salida /tmp/voip78-llamadas
```

Copiá el ayudante CDP `/tmp/voip-orq/cdp.py` a tu propia ruta temporal. Usá un perfil
separado y un puerto CDP libre (esta prueba: `/tmp/voip78-chrome`, 9388). Agregá:

```text
--use-fake-ui-for-media-stream
--use-fake-device-for-media-stream
--use-file-for-fake-audio-capture=/tmp/voip78-microfono.wav
--disable-features=AudioServiceSandbox
```

Los tres primeros son los flags del [ensayo WebRTC](https://webrtc.org/getting-started/testing).
En esta máquina, la lectura del archivo falso daba silencio con el sandbox del servicio
de audio; deshabilitar **solo ese sandbox en el Chrome de prueba** permitió leerlo.
Chromium documenta el [problema de acceso al archivo desde el sandbox](https://chromium.googlesource.com/chromium/src.git/+/167f34ae932ed8f702d9127339acbff246b4eb47).
No es una opción necesaria ni recomendada para el Chrome que captura voz real.

En CDP abrí `http://127.0.0.1:8788/`. Si se repone una llamada terminada, pulsá
«Nueva llamada» antes de iniciar. Elegí `protegida-fuente=microfono`,
`fuente=SC-WA-CODE-01` y pulsá `iniciar`; esperá el fin (~23 s).
Observá las burbujas `.protegida`, los mensajes binarios de `/audio` y el estado de
los tracks del stream (instrumentando `getUserMedia` antes del clic).
Para la comparación, iniciá ambos roles como `cliente` y ejecutá simultáneamente:

```bash
../../.venv/bin/python cliente.py --servidor ws://127.0.0.1:8788 --rol otra --wav ../asr-local/audio/SC-WA-CODE-01-tts-estereo.wav --canal izq &
../../.venv/bin/python cliente.py --servidor ws://127.0.0.1:8788 --rol protegida --wav ../asr-local/audio/SC-WA-CODE-01-tts-estereo.wav --canal der
```

Compará `canales.protegida.retraso_parcial_s` en los dos manifiestos. Para errores,
inyectá rechazos de `getUserMedia` con las DOMException nombradas arriba y un `ended`
antes del inicio; comprobá mensaje y posibilidad de reintento. Cerrá Chrome y el
servidor al finalizar. El procedimiento con voz real está en el [README del spike](../../README.md#8-micrófono-desde-el-navegador-78).

## Pruebas y revisión

- `node --test tests/audio-pcm.test.mjs`: **2 tests pasan** (tono de 1 kHz a 48/44,1/16 kHz,
  duración, frecuencia, RMS y saturación PCM16).
- `../../.venv/bin/python -m unittest discover -s tests`: **16 tests pasan** en 1,185 s.
- TypeScript ya disponible en caché local, sin instalar: chequeo estricto `--allowJs
  --checkJs --noEmit --target ES2022 --module esnext --moduleResolution bundler` de
  los tres módulos y el script extraído del panel; sin errores. Se declararon los
  globales de AudioWorklet (`sampleRate`, `AudioWorkletProcessor`, `registerProcessor`)
  en un archivo temporal para ese chequeo.
- `git diff --check`: sin errores.
- `code-review`, ejes Standards y Spec en workers independientes, sobre
  `d5a17d8...c4a8dd2`: un hallazgo por eje. Corregidos: traducción de errores nativos
  desconocidos (P3) y cancelación al perder la entrada antes de `inicio` (P2).
  La regresión se reprodujo y volvió a verificar en Chrome.

Pendiente humano: voces reales y ruido, diálogo de permisos real, indicador del
sistema apagado, Meet, BlackHole y otra notebook. Los tracks terminados en headless
no reemplazan ver el indicador en la notebook de demo.
