# Llamada en vivo: ASR por canal, detector y panel (frente 1, spike)

> **Estado: propuesta sin discutir.** Spike de la llamada en vivo del panel («Llamada en vivo:
> opciones»). No cierra [D08](../../docs/gestion/MAPA-DECISIONES.md#d08--congelar-protocolo-experimental)
> ni [D09](../../docs/gestion/MAPA-DECISIONES.md#d09--elegir-asr-y-detector). Implementa la opción D
> (cualquier app de llamada + captura por persona) y deja andando la E (replay estéreo en tiempo real)
> con el mismo código. La elección de la opción sigue siendo del equipo.

> **ADVERTENCIA: las cifras de abajo salen de UNA llamada TTS (`SC-WA-CODE-01`, 22 s) en la M1 de 8 GB.
> Sirven para ubicar dónde está la demora, no como rendimiento del detector.**

## 1. Qué hace

```text
notebook de la persona protegida ── micrófono ──┐
                                                │  WebSocket, PCM 16 kHz en bloques de 40 ms
notebook de la otra persona ──────── micrófono ─┤
   (o BlackHole: lo que sale de la app de llamada en la misma notebook)
   (o un canal de un WAV al ritmo real: plan B y pruebas)
                                                ▼
servidor.py ── Zipformer streaming por canal ── actualizaciones.jsonl (contrato de asr-local)
            ── detector (reglas o SLM) sobre la foto más reciente ── detector.jsonl
            ── panel web: transcripción, riesgo, aviso y demoras
            ── al cortar: estereo.wav (fuera de Git) y manifiesto.json
```

- **Cada persona es un canal.** El rol (`protegida` u `otra`) lo dice el cliente al conectarse; cada
  línea del JSONL trae `canal: "protegida" | "otra"`, sin un campo `rol` duplicado. El detector
  sigue viendo A/B por orden del primer texto (incluidos parciales), como en los casos de texto.
  Replay reconstruye esa asignación por llamada y sigue aceptando los registros anteriores con A/B.
  Los eventos ASR del panel conservan `canal: "A" | "B"` y `rol` por compatibilidad con su interfaz
  (roles «Vos» / «La otra persona» para el detector son del frente 3).
- **Reloj de la llamada.** Empieza con el primer bloque que llega. Cada canal se ubica según cuándo llegó
  su primer bloque y desde ahí cuenta muestras: los dos quedan alineados aunque vengan de notebooks
  distintas, y el estéreo guardado tiene el mismo reloj que el JSONL.
- **El detector nunca hace cola.** Si llega texto mientras evalúa, la siguiente evaluación toma lo último
  disponible y las intermedias se saltean (`saltadas` en `detector.jsonl`). En el replay se evalúan
  todas en orden; acá eso haría crecer la demora en una llamada larga.
- **Toda llamada en vivo se puede medir después:** `replay.py --actualizaciones <llamada>/actualizaciones.jsonl`
  la vuelve a correr con cualquier detector (verificado: el replay de `reglas-final` da `T_A` = 18,447 s contra 18,457 s en vivo; la diferencia es el tiempo de las reglas).

## 2. Opciones de llamada

| Opción | Cómo es | Estado acá |
|---|---|---|
| **D1. Dos notebooks** (recomendada para la demo) | Cada persona habla por WhatsApp o Meet con auriculares y corre `cliente.py` con su micrófono. | Anda: probado con el micrófono de la M1. Falta la prueba con dos personas. |
| **D2. Una notebook** | La persona protegida corre dos clientes: su micrófono (`--rol protegida`) y lo que sale de la app de llamada vía [BlackHole](https://github.com/ExistentialAudio/BlackHole) (`--rol otra --dispositivo BlackHole`). Es lo más parecido al teléfono: un solo dispositivo con los dos canales. | Mismo código; falta instalar BlackHole y probarlo. |
| E. Replay estéreo en tiempo real (plan B) | Elegí el ejemplo en el panel y tocá «Iniciar llamada»; el servidor manda ambos canales al ritmo real. También sigue disponible `cliente.py --wav`. | Anda: misma entrada de audio y detector que los clientes. |
| A. WebRTC propia / B. LiveKit / C. Asterisk | Ver el panel. | No empezadas: solo si D no alcanza. |

D1 y D2 no cambian el servidor: solo cambia de dónde sale el audio del canal `otra`.

## 3. Cómo correrlo

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r experiments/asr-local/requirements.txt -r experiments/voip/requirements.txt
cd experiments/voip

# En la máquina que analiza (la del ASR y el detector):
python servidor.py --detector reglas
python servidor.py --detector slm --modelo qwen3.5:0.8b-q8_0
python servidor.py --detector slm --modelo qwen3.5:4b-q4_K_M --ollama-url http://<pc-con-gpu>:11434

# Panel para el público:   http://<ip-del-servidor>:8765/
# Pantalla de la protegida: http://<ip-del-servidor>:8765/?vista=protegida

# En cada notebook (D1), con auriculares:
python cliente.py --listar
python cliente.py --servidor ws://<ip-del-servidor>:8765 --rol protegida
python cliente.py --servidor ws://<ip-del-servidor>:8765 --rol otra

# Plan B / pruebas sin personas (E): los dos canales de un estéreo al ritmo real
python cliente.py --rol otra --wav ../asr-local/audio/SC-WA-CODE-01-tts-estereo.wav --canal izq &
python cliente.py --rol protegida --wav ../asr-local/audio/SC-WA-CODE-01-tts-estereo.wav --canal der

python -m unittest discover -s tests
```

### Ejemplo desde el panel (sin terminales de clientes)

Arrancá una vez el servidor desde `experiments/voip/`:

```bash
../../.venv/bin/python servidor.py --host 127.0.0.1 --detector reglas --salida /tmp/voip-demo-llamadas
```

Abrí `http://127.0.0.1:8765/`, elegí **Ejemplo · estafa SC-WA-CODE-01** o
**Ejemplo · legítima LG-WA-CONSULTA-01** y tocá **Iniciar llamada**. No pide micrófono ni
captura audio del navegador. Los WAV locales deben existir en `experiments/asr-local/audio/`:
`SC-WA-CODE-01-tts-estereo.wav` y `LG-WA-CONSULTA-01-tts-estereo.wav` (estéreo PCM a 16 kHz).
El servidor lee izquierdo = otra persona, derecho = protegida y entrega pares de bloques
cada 40 ms por la misma entrada que usa `/audio`, después de precargar los dos ASR.
El estéreo **guardado** conserva su formato anterior: izquierdo = protegida, derecho = otra.

**Terminar** corta la reproducción, cierra los clientes conectados y guarda lo recibido.
El ejemplo también termina automáticamente cuando se acaba el archivo. **Nueva llamada**
limpia conversación, aviso, riesgo y demoras; después podés elegir otro ejemplo e iniciarlo.
Cada llamada usa una carpeta distinta, incluso si abrís dos dentro del mismo segundo.
Para usar `cliente.py`, elegí **Segunda notebook · cliente.py** y tocá **Iniciar llamada**;
el arranque automático con el primer bloque del cliente sigue funcionando.

El control viaja por `/panel`:

```json
{"tipo":"iniciar","modo":"llamada","fuentes":{"otra":{"tipo":"ejemplo","escenario":"SC-WA-CODE-01","canal":"izq"},"protegida":{"tipo":"ejemplo","escenario":"SC-WA-CODE-01","canal":"der"}},"corte_silencio_s":null,"umbral_rms_silencio":null}
{"tipo":"terminar"}
```

Para clientes, ambas fuentes son `{"tipo":"cliente"}`. Corte y umbral quedan reservados
para #81; por ahora deben omitirse o ser `null` y se conserva la configuración del servidor.
Un control inválido devuelve `{"tipo":"error","mensaje":"…"}` al panel que lo mandó.
La fuente y el modo elegidos quedan en `inicio_panel` en el manifiesto.

### Eventos del panel: transcripción y volumen

Los mensajes de transcripción llevan `tipo: "asr"` y `entrega: "parcial" | "final"`.
`rol` identifica a la persona y `canal` conserva la letra A/B. El JSONL sigue usando
su contrato previo: `tipo: "parcial" | "final"` y `canal` con el rol.

Durante la llamada, el servidor manda una foto de ambos niveles cada 100 ms (aproximadamente
10 Hz; puede demorar más si el procesamiento ocupa el servidor):

```json
{"tipo":"niveles","llamada_id":"VIVO-…","t_s":1.2,"canales":{"protegida":{"rms":0.0,"fin_audio_s":1.2},"otra":{"rms":0.125,"fin_audio_s":1.2}}}
```

`rms` es el RMS del último bloque PCM16, normalizado a 0–1; `fin_audio_s` usa el reloj
de audio de cada canal y es `null` hasta su primer bloque. `t_s` usa el reloj de la llamada.
Si un canal deja de mandar bloques por más de 250 ms, su nivel se muestra en cero.
Para #81, el objeto de cada rol permite agregar `silencio_acum_s`, `corte_silencio_s`
y `umbral_rms_silencio` sin cambiar el agrupamiento ni mezclar silencio con volumen.
Esos campos todavía no se emiten: los debe informar el motor con la configuración aplicada.

Los niveles son efímeros: no van al JSONL, manifiesto ni historial de reconexión. El panel
conserva solo la última foto y actualiza ambos medidores en un `requestAnimationFrame`.
Al terminar, iniciar otra llamada o perder la conexión, limpia los medidores.
La verificación de #79 está en [la evidencia de niveles](corridas/2026-10-26-niveles-79.md).

Verificación real del 2026-10-26, commit `3dc9269` con árbol limpio
([manifiestos y salidas sin audio](corridas/2026-10-26-panel-77/README.md)),
con Zipformer local y `--detector reglas`, sin Ollama:
la estafa avisó a **18,455 s** (referencia `reglas-final`: 18,457 s; diferencia −0,002 s).
Ambos canales comenzaron en 0,000 s y conservaron 22,217 s de audio.
La legítima conserva 16,326 s, pero el detector actual de reglas produjo una **falsa alarma
a 5,214 s** con «Me llegó por ese MS un código para activar WhatsApp y yo no lo pedí».
Es una limitación del detector, no se oculta por escenario: el criterio «legítima sin aviso»
se verifica con el detector de la demo: Qwen3.5 0.8B local, no con el respaldo de reglas.
Con `--detector slm --modelo qwen3.5:0.8b-q8_0 --ollama-url http://127.0.0.1:11434`,
la legítima **no produjo aviso**: tres evaluaciones válidas, sin fallos. Se conservó la
misma configuración de audio y corte de silencio (0,8 s). La primera comprobación,
antes del commit, había dado 18,460 s para la estafa y 5,211 s para la falsa alarma de reglas.

La llamada también empieza con el primer bloque de audio y termina cuando se desconectan todos los clientes
(o con Ctrl+C en el servidor). Queda en `llamadas/<fecha>_<hora>_<microsegundos>/`, que Git ignora: son voces y
transcripciones del equipo; si una sirve como evidencia, se copia a `corridas/` sin el WAV.

El modelo de Zipformer se baja solo la primera vez (149 MB, a `experiments/asr-local/modelos/`).

## 4. Dónde está la demora (TTS, una llamada, M1 8 GB)

Corridas en [`corridas/2026-10-26-spike-tts/`](corridas/2026-10-26-spike-tts/), commit `b33b1d7`,
audio `SC-WA-CODE-01-tts-estereo.wav` (canal izquierdo = estafador, derecho = protegida), Ollama 0.40.5,
seed 42. «Pedido» = la frase «decime el código de activación que recibiste por SMS», cuya voz termina
en el segundo 17,6.

| Corrida | Detector | Disparo | Corte de silencio | Detector por evaluación (mediana) | `T_A` − fin del pedido |
|---|---|---|---|---|---|
| `reglas-final` | reglas | final | 0,8 s | 0,01 s | **+0,85 s** |
| `reglas-corte05` | reglas | final | 0,5 s | 0,01 s | **+0,53 s** |
| `reglas-parcial` | reglas | parcial | 0,8 s | 0,00 s | **−2,19 s** (avisa a mitad de la frase) |
| `slm08-final` | Qwen3.5 0.8B | final | 0,8 s | 1,23 s | **+2,79 s** |
| `slm08-parcial` | Qwen3.5 0.8B | parcial | 0,8 s | 1,15 s | **−0,08 s** |
| `slm4b-final` | Qwen3.5 4B | final | 0,8 s | 6,71 s | +0,13 s (avisó por la urgencia de la frase anterior, no por el pedido) |

Lo que se ve:

1. **El ASR no es el problema.** Zipformer da el texto parcial a 60–140 ms del audio (mediana por canal) y los dos canales llegan
   alineados (desfase de llegada ≤ 0,24 s en todas las corridas). Una frase se cierra cuando pasan
   `--corte-silencio` segundos sin voz: ese corte es toda la demora del ASR (0,8 s → 0,5 s).
2. **El SLM sí.** El 0.8B tarda ~1,2 s por evaluación porque escribe un JSON de ~40 tokens con motivo y
   cita. El 4B en la M1 tarda 6–7 s: en vivo no alcanza a seguir la charla (solo hizo 2 evaluaciones
   en 22 s). En la PC con GPU el 4B tarda 0,61 s de mediana (handoff del detector, 2026-10-23).
3. **Evaluar con parciales adelanta el aviso**, porque no espera el corte de silencio: con reglas el aviso
   sale 2,2 s antes de que termine el pedido. Con el SLM ocupa la máquina todo el tiempo y en
   corpus_v2 nunca se midió sobre texto provisorio: puede subir las falsas alarmas.

Prueba aparte, sin registrar como corrida (un caso, prompt improvisado): pidiéndole al SLM un solo token
(«SI»/«NO») con logprobs, el 0.8B baja de ~1,2 s a **~0,3 s** por evaluación y el 4B a ~1,9 s en la M1.
En el 4B, p(SI) pasó de 0,50 a 0,89 al llegar el pedido del código. Es la hipótesis 1 del frente 3 y
hay que medirla en los 150 de desarrollo antes de usarla.

## 5. Para bajar la demora, en orden de impacto

1. **SLM de un token** (frente 3): 4–6 veces menos por evaluación; motivo y cita se piden aparte solo
   cuando avisa, mientras el aviso ya está en pantalla.
2. **SLM en la PC con GPU** (`--ollama-url`): el ASR queda en la notebook y el 4B corre en ~0,6 s.
   Riesgo para la demo: depende de la red del lugar.
3. **Disparo con parciales + foto más reciente**: el aviso puede salir antes de que termine la frase.
   Requiere un detector rápido (reglas, RoBERTuito o SLM de un token) y medir falsas alarmas.
4. **Corte de silencio 0,5 s**: −0,3 s por frase; con voces reales puede partir frases en dos.
5. **Caché de prefijo real** (llama-server, frente 3): hoy cada evaluación reprocesa toda la transcripción.

Whisper no sirve para esto: no es streaming y en la prueba de asr-local tardó más (RTF 0,27 contra 0,03–0,17 de Zipformer).

## 6. Límites conocidos

- Las cifras históricas de §4 usan una sola llamada sintética: voces TTS, pausas de 1 s entre turnos, sin ruido ni solapamiento.
- El respaldo de reglas da una falsa alarma en `LG-WA-CONSULTA-01` a 5,214 s por
  «Me llegó por ese MS un código para activar WhatsApp y yo no lo pedí»; no distingue
  mencionar un código de pedirlo. Con Qwen3.5 0.8B local la misma llamada no avisó.
- La verificación de #77 ejercitó el servidor real por `/panel`; queda comprobar visualmente
  los controles en la notebook de demo y ensayar voz real, Meet y otra notebook.
- Sin auriculares, cada micrófono capta también la otra voz (no hay cancelación de eco).
- El fin de la voz se estima por energía (RMS ≥ 0,005, el umbral del motor). Con ruido de fondo real
  puede no haber «silencio» y la frase se cierra por el endpoint del modelo (1,0 s).
- El panel no tiene autenticación: usar solo en una red propia.
- El aviso se ve en el navegador de la notebook, no dentro de la app de llamada.

## 7. Próximos pasos del spike

1. Dos personas, dos notebooks, misma red (D1): confirmar alineación y demoras con voz real.
2. BlackHole en la M1 (D2) con WhatsApp Desktop o Meet.
3. Conectar el SLM de un token cuando el frente 3 lo tenga medido.
4. Modo guion (cada persona ve su próxima línea) para grabar los 24 casos de `GRABACIONES-ASR.md`.

## 8. Medir la notebook sin panel (#84)

Con el entorno Python de §3 activo, Zipformer ya descargado y el TTS original de
`SC-WA-CODE-01` en `experiments/asr-local/audio/`, corré desde `experiments/voip/`:

```bash
python medir.py --detector slm --modelo qwen3.5:4b-q4_K_M
# Comparación con el modelo chico o el respaldo:
python medir.py --detector slm --modelo qwen3.5:0.8b-q8_0
python medir.py --detector reglas
```

Para SLM, abrí Ollama local antes de correrlo y descargá el modelo una vez con
`ollama pull qwen3.5:4b-q4_K_M` (o `ollama pull qwen3.5:0.8b-q8_0`). Si falta
Ollama o el modelo, el comando indica cómo resolverlo antes de empezar la llamada.
La medición usa solo archivos y modelos locales; no descarga audio ni ASR.
Si están en otra carpeta, agregá `--audio /ruta/SC-WA-CODE-01-tts-estereo.wav`
y `--modelo-asr /ruta/sherpa-onnx-streaming-zipformer-es-kroko-2025-08-06`.
`--audio` debe apuntar al mismo TTS original: otro audio invalida la referencia
al fin del pedido (17,6 s, según §4).

El comando precarga el SLM y los dos ASR, reproduce los ~22 s del ejemplo al ritmo
real con la fuente de #77 y espera la evaluación pendiente al terminar. Conserva
el disparo `final`, silencio de 0,8 s, prompt `tarea`, seed 42, hablantes A/B,
foto más reciente sin cola y aviso único del servidor. No abre un puerto ni un panel.
La carga inicial queda fuera de la mediana; la demora del ASR queda fuera del tiempo
por evaluación, pero sí influye en el momento del aviso.

Al terminar imprime **CUMPLE** o **NO CUMPLE** el criterio de **mediana < 2 s por
evaluación**, seguido de la mediana, cantidad de evaluaciones, salteadas, fallos y
el aviso respecto del fin del pedido. Con fallos o sin evaluaciones dice NO CUMPLE
y devuelve código de salida 1; superar 2 s con respuestas válidas es una medición
completa y devuelve 0. «Sin aviso» se informa explícitamente; un aviso anterior al
pedido puede responder a otra frase, y no demuestra que detectó el pedido.

Cada ejecución deja `actualizaciones.jsonl`, `detector.jsonl` y `manifiesto.json`
en `corridas/<fecha>_<hora>_<microsegundos>/`, **sin WAV**. El manifiesto conserva
configuración, máquina, commit, digest del modelo, hash del TTS y referencia de
17,6 s. Para pruebas descartables usá `--salida /tmp/voip-medicion`; no versiones
esas corridas. Estas cifras sirven para elegir la notebook de demo, no para medir
rendimiento sobre corpus real ni para cerrar D08/D09.

**Pendiente humano:** correr en la M4 con 0.8B y 4B; este ticket no da por hecha
esa prueba ni las de voz real, Meet u otra notebook.

Verificación del 2026-10-26 en M1 de 8 GB: el 0.8B dio mediana **1,312 s**, cuatro
evaluaciones, cero salteadas y fallos, y aviso **+2,803 s** respecto del fin del pedido.
Se conserva [esa corrida sin WAV](corridas/2026-10-26-medicion-84-m1-08b/README.md).
