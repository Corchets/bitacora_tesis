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
  línea del JSONL trae `rol`. La letra A/B sigue siendo «quien habló primero», como en los casos de
  texto, para no cambiar lo que ve el detector (roles «Vos» / «La otra persona» son del frente 3).
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
| E. Replay estéreo en tiempo real (plan B) | `cliente.py --wav` manda cada canal al ritmo real. | Anda: es lo que generó las cifras de §4. |
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

La llamada empieza con el primer bloque de audio y termina cuando se desconectan todos los clientes
(o con Ctrl+C en el servidor). Queda en `llamadas/<fecha>_<hora>/`, que Git ignora: son voces y
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

- Una sola llamada sintética: voces TTS, pausas de 1 s entre turnos, sin ruido ni solapamiento.
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
