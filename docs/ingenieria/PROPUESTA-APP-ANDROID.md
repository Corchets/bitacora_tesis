# Propuesta: la app Android que corre entera en el teléfono durante una llamada

> **Estado: propuesta sin discutir.** Luciano Grosso, 2026-11-22. No sale de un issue y no cambia ninguna decisión:
> respeta [D05](../gestion/MAPA-DECISIONES.md#d05--elegir-la-fuente-de-audio-demostrable) (llamada VoIP propia
> como integración objetivo y telefonía universal fuera de alcance), el
> [ADR 0003](adr/0003-detector-solo-en-entrantes-de-no-agendados.md) (solo entrantes de números no agendados, también
> sin discutir) y la configuración final de los ADR [0001](adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)
> y [0006](adr/0006-salida-cortada-tras-el-campo-que-decide-y-motivo-al-avisar.md)–[0009](adr/0009-en-el-telefono-el-modelo-genera-solo-el-numero.md).
> Todo lo que dice «se propone» está para discutir. Si se hace, es trabajo futuro (label `trabajo-futuro`).

Cada punto separa lo **verificado**, con enlace a la corrida o a la fuente, de lo **inferido**, que es lo que se
espera pero nadie midió ni leyó en una fuente.

## En una página

- **El audio de una llamada telefónica común no se puede capturar desde una app de terceros.** Android solo entrega
  los dos lados de la llamada a apps del sistema preinstaladas. Un servicio de accesibilidad puede abrir el micrófono
  durante la llamada, pero Google Play prohíbe usarlo para grabar llamadas y, además, el micrófono mezcla las dos voces
  (§1).
- **La versión completa que sí se puede hacer es una app de llamadas VoIP propia.** La app es la dueña del audio: el
  micrófono es PROTEGIDA y lo que llega por la red es OTRA, separados, que es lo que necesita el armado de turnos
  ([ADR 0007](adr/0007-consulta-al-cerrar-cada-turno-de-otra.md)). Es lo que ya había decidido D05.
- **Adentro corre lo mismo que se midió por partes:** el ASR de [`asr.cpp`](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/app/asr.cpp),
  ya portado a C++ y comparado evento por evento con Python, y `llama-server` embebido en el proceso, como en la app del
  iPhone. La lógica de turnos, consulta y aviso, que hoy está en Python, se reescribe en C++ para que la compartan
  Android e iOS (§2).
- **Lo que no se sabe y decide si anda en el A56:** si el ASR y el detector juntos entran en la CPU sin atrasar el
  aviso, cuánto calientan y cuánta batería gastan sin cable. En el A56 nunca corrieron juntos ni desenchufados (§4–§5).
- **El orden para validarla** está en §8: primero ASR + detector a ritmo real con audio sintético en el A56 (la
  réplica de la corrida del iPhone), después la app VoIP entre dos teléfonos, y recién al final voz humana.

## 0. De dónde se parte

| Pieza | Qué se midió | Dónde | Lo que falta para la versión completa |
|---|---|---|---|
| Detector en el A56 | `llama-server` en Termux, cliente Python por adb, enchufado. 3,74 s por línea con 14 tokens y 2,85 s generando solo el número; motivo 11 s; 3,4–3,5 GiB de memoria | [2026-11-10](../../experiments/slm-directo/corridas/2026-11-10_a56-congelada-latencia/README.md), [2026-11-11](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md) | Se midió con `c-json-corte-riesgo` y `c-premisa`, no con `c-consejos` ([ADR 0008](adr/0008-prompt-del-detector-c-consejos.md)). Nunca dentro de una app, nunca sin cable |
| Detector en el iPhone 15 Pro Max | `llama-server` embebido en una app, con Metal. 0,54 s por línea con solo el número | [2026-11-20](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/README.md), [solo el número](../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md) | — |
| ASR + detector a la vez | Solo en el iPhone, sin cable, audio sintético desde un archivo a ritmo real. El ASR va a tiempo real y suma ~0,8 GiB; llegó a `fair` | [2026-11-21](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md) | En Android no corrió nunca. El detector consultó sobre el texto original, no sobre lo que transcribió el ASR |
| Turnos, aviso único, motivo diferido | En Python, en la demo de la compu | [`turnos.py`](../../experiments/voip/turnos.py), [`llamada.py`](../../experiments/voip/llamada.py), [`detectores.py`](../../experiments/slm-directo/detectores.py) | En el teléfono no corrió nunca: en todas las mediciones la lógica corrió en la Mac o en Termux |
| Llamada real | Por Meet, en la compu, con voz humana | [`experiments/voip/`](../../experiments/voip/README.md) | Nunca en un teléfono |

## 1. El audio de la llamada: qué deja Android de verdad

### 1.1 Lo que dicen las fuentes (verificado)

- **Durante una llamada, la llamada se queda con el audio.** La guía
  [Sharing audio input](https://developer.android.com/media/platform/sharing-audio-input), en el caso «llamada de voz
  + app común», dice: «The call always receives audio», «The app can capture audio if it is an accessibility service»
  y «The app can capture the voice call if it is a privileged (pre-installed) app with permission
  `CAPTURE_AUDIO_OUTPUT`». Para los dos lados hay que usar `VOICE_UPLINK` o `VOICE_DOWNLINK`.
  La misma guía dice que «two ordinary apps can never capture audio at the same time».
- **Las fuentes de la llamada no son para nosotros.** En
  [`MediaRecorder.AudioSource`](https://developer.android.com/reference/android/media/MediaRecorder.AudioSource),
  `VOICE_CALL`, `VOICE_UPLINK` y `VOICE_DOWNLINK` piden `CAPTURE_AUDIO_OUTPUT`, que «is reserved for use by system
  components and is not available to third-party applications».
- **Capturar lo que suena tampoco sirve.** [AudioPlaybackCapture](https://developer.android.com/media/platform/av-capture)
  solo captura audio con uso `USAGE_MEDIA`, `USAGE_GAME` o `USAGE_UNKNOWN`, y pide la autorización de captura de
  pantalla (MediaProjection). La llamada no está en esa lista (es inferencia de la lista: la página no nombra las
  llamadas).
- **Accesibilidad para grabar llamadas: prohibido en Play.** La política
  [Permissions and APIs that Access Sensitive Information](https://support.google.com/googleplay/android-developer/answer/16558241)
  dice: «The Accessibility API is not designed and cannot be requested for: remote call audio recording».
- **Google lo hace porque es la app de teléfono.** Scam Detection corre dentro de la app Teléfono de Pixel, en
  segundo plano, nunca con contactos, apagado por defecto y con un pitido audible para la otra parte
  ([lectura, §5.1](../investigacion/lecturas/2026-google-scam-detection.md#51-scam-detection-en-llamadas--análisis-del-contenido)).

### 1.2 Las opciones

| Opción | Qué audio da | Canales separados (ADR 0007) | Llamada real | Distribuible por Play | Veredicto |
|---|---|---|---|---|---|
| **A. App VoIP propia** | Los dos lados: el micrófono propio y el audio que llega por la red | Sí, por construcción | Sí, pero entre dos personas que usan la app | Sí | **Se propone** |
| **A′. VoIP propia + número virtual** | Igual que A | Sí | Sí, desde cualquier teléfono, si la persona desvía su línea a un número SIP que suena en la app | Sí | Variante para después (inferida, ver abajo) |
| B. Altavoz + micrófono de una app común | Probablemente nada o silencio mientras la llamada tiene el audio (inferido de §1.1: la guía solo habilita a accesibilidad y apps del sistema) | No | Sí | Sí | No sirve |
| C. Altavoz + servicio de accesibilidad | El micrófono, con las dos voces mezcladas, el eco de la sala y el procesamiento de la llamada | No | Sí | **No** (política de Play) | Solo como prueba de laboratorio instalada a mano; rompe el ADR 0007 |
| D. App de sistema o ROM propia con `CAPTURE_AUDIO_OUTPUT` | Los dos lados de la llamada celular | Sí | Sí | No: hay que firmar con la plataforma o tener root | Fuera de alcance, como ya dice [ALTERNATIVAS-CAPTURA-AUDIO.md](ALTERNATIVAS-CAPTURA-AUDIO.md) |
| E. Ser la app de teléfono por defecto (`ROLE_DIALER`) | Control de la llamada, no el audio (inferido: la guía de §1.1 no la nombra entre las que capturan) | — | Sí | Sí | No resuelve el audio |

Sobre **A′** (inferido, no probado): un proveedor SIP da un número que entra a la app, y la persona desvía su línea
(desvío del operador) a ese número. El audio pasa por el proveedor, aunque el análisis siga en el teléfono, y el
número de quien llama llega por SIP, lo que permite aplicar el ADR 0003. Habría que revisar costos, el desvío en las
operadoras argentinas y qué dice [PRIVACIDAD-DEL-SISTEMA.md](../corpus/PRIVACIDAD-DEL-SISTEMA.md).

### 1.3 Recomendación

> **Estado: propuesta sin discutir.** Opción A para la versión completa, con dos teléfonos con la app (por ejemplo,
> el A56 como PROTEGIDA y otro como OTRA). C, si se quiere, solo como experimento aparte para medir cuánto pierde el
> ASR con las voces mezcladas, declarado como limitación y sin publicar.

Con A, la app hace de las dos cosas: es el teléfono (una llamada VoIP registrada en el sistema con
[Core-Telecom](https://developer.android.com/develop/connectivity/telecom/voip-app/telecom)) y es el detector. El
transporte de la llamada (WebRTC u otro) es trabajo a elegir; lo que importa para el detector es que entrega el audio
de cada lado antes de mezclarlo.

## 2. Cómo se arma la app

```text
                   ┌────────────────────── servicio en primer plano (tipos phoneCall + microphone) ─────────────────────┐
  micrófono ──────►│ PROTEGIDA 16 kHz ─┐                                                                                 │
  (VOICE_COMM.)    │                   ├─► ASR parakeet-filtro (asr.cpp) ─► frases por canal ─► Turnos ─► Contexto        │
  red VoIP ───────►│ OTRA 16 kHz ──────┘                                                          │           │          │
  (audio remoto)   │                                                     al cerrar turno de OTRA ─┘           ▼          │
                   │                                        Detector: llama-server embebido (127.0.0.1) ◄── transcripción │
                   │                                                │ riesgo ≥ 0,3, primera vez                           │
                   │                                                ▼                                                     │
                   │                                   Aviso (texto fijo, vibración) ── luego ──► motivo (2.ª consulta)   │
                   └──────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Servicio en primer plano (verificado en la documentación)

Un servicio en primer plano es la forma que tiene Android de dejar trabajar a una app con la pantalla apagada o con
otra app adelante: muestra una notificación fija y el sistema lo mata último.

- Desde Android 14 hay que declarar el tipo. El tipo `microphone` pide `FOREGROUND_SERVICE_MICROPHONE` y el permiso
  `RECORD_AUDIO`; el tipo `phoneCall` pide `FOREGROUND_SERVICE_PHONE_CALL` y `MANAGE_OWN_CALLS` o ser la app de
  teléfono por defecto ([tipos de servicio](https://developer.android.com/develop/background-work/services/fgs/service-types)).
- **No se puede arrancar un servicio con micrófono desde segundo plano**, ni siquiera con las excepciones generales
  ([restricciones](https://developer.android.com/develop/background-work/services/fgs/restrictions-bg-start)). Por eso
  el servicio arranca cuando la persona atiende en la pantalla de la app (visible), o desde la notificación de la
  llamada, que es una acción de la persona sobre la app. Con la opción A es natural: atender es tocar la app.
- Los tipos `microphone` y `phoneCall` no tienen el tope de 6 horas de `dataSync` y `mediaProcessing`
  ([timeout](https://developer.android.com/develop/background-work/services/fgs/timeout)).
- Core-Telecom pide alojar la llamada en un servicio en primer plano de tipo `phoneCall` y publicar la notificación
  de llamada dentro de los 5 s ([guía](https://developer.android.com/develop/connectivity/telecom/voip-app/telecom)).

**Inferido:** Samsung tiene su propio ahorro de batería que suspende apps; hay que probar que el servicio sobrevive
con la pantalla apagada y que la persona no tenga que tocar ajustes (§8, M6).

**ADR 0003 en la opción A:** el número de quien llama lo trae la señalización de la propia app, y la agenda se
consulta con `READ_CONTACTS`. En una variante con llamadas celulares, `CallScreeningService` (rol
`ROLE_CALL_SCREENING`) da el número y la dirección de la llamada antes de que suene
([referencia](https://developer.android.com/reference/android/telecom/CallScreeningService)), pero no el audio.

### 2.2 ASR

- **Se lleva casi tal cual** [`asr.cpp`](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/app/asr.cpp):
  es `MotorPorFrases`, `MotorSherpaParakeet` y `DetectorSilero` de
  [`motores.py`](../../experiments/asr-local/motores.py) con la configuración `parakeet-filtro`, y sus 1018 eventos
  coinciden uno a uno con Python (verificado, [corrida del iPhone](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md#prueba-en-seco-en-la-mac)).
- **Hay que cambiarle la entrada.** Hoy `asr_correr()` lee un WAV estéreo a ritmo de reloj
  ([`asr.h`](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/app/asr.h)). Se
  propone separar el motor de la lectura: `asr_bloque(canal, muestras, n)` que recibe bloques de 640 muestras de cada
  canal y una función de aviso por cada borrador y cada final. El WAV queda como una fuente más, para repetir las
  mediciones (es lo que hace `reproducir_ejemplo` en la demo).
- sherpa-onnx compila para Android: el repositorio tiene ejemplos Android, entre ellos ASR con VAD
  ([`android/`](https://github.com/k2-fsa/sherpa-onnx/tree/master/android)). Se usa la misma versión del proyecto,
  1.13.8.
- **Faltan los filtros de texto** (borradores en otro idioma, muletillas): están en Python y no se portaron. Son
  chicos, pero cambian qué texto le llega al detector.
- **Inferido:** con la opción A, PROTEGIDA llega del micrófono con el cancelador de eco de la fuente
  `VOICE_COMMUNICATION`, y OTRA llega limpia de la red, con el códec de la llamada. Ninguna de las dos cosas se midió
  con Parakeet.

### 2.3 Detector: `llama-server` embebido o `libllama` directo

| | `llama-server` embebido | `libllama` directo |
|---|---|---|
| Qué es | El servidor de llama.cpp compilado como biblioteca y lanzado en un hilo de la app, escuchando en `127.0.0.1`. La app le habla por HTTP local | La app llama a las funciones de llama.cpp (tokenizar, procesar, muestrear) sin servidor |
| Ya probado | **Sí:** es la app del iPhone ([`main.mm`](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/app/main.mm) llama a `llama_server(argc, argv)`), y el mismo `llama-server` del A56 | No. llama.cpp trae un ejemplo Android con JNI en ese commit ([`examples/llama.android`](https://github.com/ggml-org/llama.cpp/tree/6c01da6278ab6c69ed67d9124806b50d2b299ba7/examples/llama.android)) |
| Mismo cálculo que lo medido | Sí: `/apply-template`, `/completion`, la gramática GBNF, el prefijo `{\n  "riesgo":` y la caché del prefijo son los de las corridas | Hay que reescribir la plantilla, la gramática, el prellenado y la reutilización de la caché. Según [H11](../hallazgos/H11-el-riesgo-cambia-con-el-runtime.md), cualquier cambio en cómo se calcula mueve el riesgo en algunas líneas |
| Costo | HTTP local en cada consulta (inferido: pocos ms; en el iPhone, por Wi-Fi, la ida y vuelta fue de 16 ms) y un puerto abierto en el teléfono | Más código propio; a cambio, control total de la caché y sin puerto |
| Seguridad | **Inferido:** cualquier app del teléfono con permiso de red puede conectarse a `127.0.0.1`. Hay que usar `--api-key` con una clave generada en cada arranque, o no exponer el puerto | Sin superficie de red |

> **Estado: propuesta sin discutir.** Empezar con `llama-server` embebido, con el mismo commit (`6c01da62`) y el
> mismo build del A56 (CPU, 4 hilos, sin i8mm), porque es lo único que reproduce las corridas línea por línea. Pasar a
> `libllama` solo si una medición muestra que el HTTP local pesa, y entonces compararlo línea por línea contra
> `llama-server`, como se hizo con la consulta de solo el número.

Otras dos cosas que vienen de las corridas:

- **Los builds más rápidos mueven el riesgo.** El build con dotprod+i8mm baja procesar de 1,94 a 1,27 s y Vulkan a
  1,25 s, pero cambian el riesgo en 10/83 y 16/83 líneas
  ([corrida del 2026-11-11](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md#lo-que-esto-cambia-el-riesgo-no-es-estable-ante-cambios-del-runtime)).
  Adoptarlos sigue siendo la decisión abierta que dejó esa corrida.
- **Inferido:** conviene correr el detector en un proceso aparte de la app (`android:process`), para que si el
  sistema lo mata por memoria no se corte la llamada; la llamada sigue y el aviso pasa a «detector no disponible».

### 2.4 Turnos, contexto, aviso y motivo

Es lo que hoy hace la demo en Python, y en el teléfono no existe todavía:

1. **Turnos** ([`turnos.py`](../../experiments/voip/turnos.py), 85 líneas): junta las frases de cada canal; cierra
   el turno de un lado cuando el otro habla en serio (3 palabras o más de 1 s) o tras 2 s de silencio; un turno de
   OTRA de más de 15 s consulta igual al cerrar la frase siguiente. Los umbrales son provisorios
   ([ADR 0007](adr/0007-consulta-al-cerrar-cada-turno-de-otra.md)).
2. **Contexto:** la transcripción con roles, numerada, armada como
   [`armar_mensaje_usuario`](../../experiments/slm-directo/detectores.py) (`--hablantes rol`). El comienzo tiene que
   ser idéntico entre consultas para que la caché sirva.
3. **Consulta** (ADR 0006 y 0009): prompt `c-consejos-corte-riesgo` armado con `/apply-template`, más
   `{\n  "riesgo":` escrito por nosotros, a `/completion` con la gramática que solo deja el número y la coma
   (`gramatica_numero` y `PREFIJOS` de [`correr_android_latencia.py`](../../experiments/slm-directo/correr_android_latencia.py)).
   Temperatura 0, seed 42.
4. **Aviso:** riesgo ≥ 0,3, una sola vez por llamada. Sale enseguida con un texto fijo («Posible estafa detectada»)
   y vibración, en la pantalla de la llamada.
5. **Motivo:** la segunda consulta repite los mensajes, agrega lo escrito por el modelo cerrado como JSON y el pedido
   de [`motivo_c_corte.txt`](../../experiments/slm-directo/prompts/motivo_c_corte.txt). Se muestra cuando llega
   (`motivo_diferido` en `detectores.py`). En el A56 la segunda consulta tardó 11 s de mediana; en el iPhone, el aviso con motivo llegó a unos 3 s. Si falla, queda el
   texto fijo.
6. **Cola:** si un turno de OTRA cierra mientras la consulta anterior sigue, la siguiente sale apenas termina, con
   toda la transcripción, como en la corrida del iPhone. Tras el primer aviso no se consulta más, como en la demo.

**Presupuesto de tiempo en el A56 (inferido, sumando piezas medidas por separado):** fin de la voz de OTRA → final del
ASR, ~1 s (0,8 s de corte más el proceso, medido en el iPhone) → cierre del turno, entre 0 y 2 s → consulta,
2,85 s con solo el número (medido con `c-premisa`) → aviso. Del orden de 4 a 6 s después de que OTRA termina de
hablar, **si** el ASR no le quita CPU al detector. Eso es justo lo que no se sabe (§5).

### 2.5 Dónde vive cada pieza

> **Estado: propuesta sin discutir.** Un núcleo en C++ (ASR, turnos, contexto, cliente del detector, aviso) y una
> cáscara en Kotlin (llamada, permisos, servicio, pantalla). El núcleo lo pueden usar Android (por JNI) e iOS (desde
> `main.mm`), y se prueba en la Mac como ya se hizo con `asr_mac.cpp`.

La alternativa es meter Python en la app (por ejemplo, con Chaquopy) y usar `detectores.py` y `turnos.py` tal cual. Es
lo más fiel a lo evaluado, pero agrega un intérprete a la app y no le sirve a iOS. Para demostrar que el núcleo en
C++ hace lo mismo alcanza con repetir el método de `comparar_con_python.py`: mismas entradas, mismas salidas, una por
una (§8, M4).

## 3. Llamadas largas (más de ~55 turnos)

**Verificado:** con 4096 tokens de contexto el detector deja de consultar después de unos 55 turnos de quien llama,
unos 10 minutos ([CAP-11, §11.3](../tesis/CAP-11-CONCLUSIONES.md)). La demo usa 16.384, que alcanza para unos 50
minutos, y en tres llamadas de desarrollo dio el mismo riesgo que 4096; Gemma 4 E2B admite 131.072
([README de la demo](../../experiments/voip/README.md)). La evaluación final no se repitió con 16.384, y su costo en
un teléfono no se midió.

Opciones:

| Opción | Qué ve el modelo | Costo | Riesgo |
|---|---|---|---|
| **16.384 tokens, como la demo** | Toda la llamada hasta ~50 min | Más memoria de caché y consultas más lentas al final de la llamada (inferido: la atención crece con el largo, aunque la caché evite reprocesar) | Hay que medir memoria y latencia en el turno 55, 100 y 200 |
| Ventana que descarta lo más viejo | Los últimos N turnos | Fijo | Pierde la presentación («le hablo del banco»), que es parte de la estafa. No se evaluó |
| Resumen de lo viejo | Un resumen más lo reciente | Una consulta más de vez en cuando | Es otro detector. No se evaluó |

> **Estado: propuesta sin discutir.** 16.384 tokens, como la demo, y al llegar al 90 % del contexto la app no trunca
> en silencio: deja de consultar y lo muestra («la llamada es demasiado larga para analizarla»), como el arnés con
> `contexto_excedido` ([CAP-06](../tesis/CAP-06-IMPLEMENTACION.md)). Tras el primer aviso no se consulta más, así que
> el contexto largo solo importa en llamadas que todavía no avisaron.

## 4. Memoria

**Verificado:**

- El A56 tiene 11,1 GiB de RAM física ([diagnóstico del 2026-11-06](../../experiments/slm-directo/corridas/2026-11-06-a56-diagnostico.md)).
- `llama-server` llegó a 3,39–3,53 GiB de pico residente con contexto 4096; 4,36 GiB con el build i8mm
  ([2026-11-11](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md)).
- En el iPhone, el ASR sumó unos 0,8 GiB de lo que cuenta el sistema contra el límite de la app
  ([2026-11-21](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md#1-memoria-entra)).
  En la Mac, el ASR solo llegó a 2,0 GB ([ADR 0001](adr/0001-parakeet-filtro-y-gemma4-e2b-con-tito-viejo.md)).
- Android puede sacar de memoria las páginas de un archivo mapeado que no se modificó, pero no la memoria que la app
  escribió ([memory overview](https://developer.android.com/topic/performance/memory-overview)). Los pesos del GGUF
  mapeado son del primer tipo; la caché del contexto, del segundo.

**Inferido:** detector + ASR + la llamada VoIP rondarían 4,5 a 5 GiB residentes con 4096, más la caché adicional de
16.384. En 11 GiB debería entrar, pero el A56 corre otras apps y Android mata procesos cuando falta memoria. Hay que
medirlo con la app real, con otras apps abiertas, no con `am kill-all` como en las corridas.

## 5. CPU, temperatura y batería

**Verificado:**

- El A56 tiene cuatro núcleos A720 rápidos y cuatro A520 lentos; con 6 u 8 hilos el detector empeora (4,40 y 5,61 s
  por línea contra 3,74 s con 4) ([2026-11-11](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md#3-hilos-y-gpu)).
- En el A56 solo se anotó la temperatura de la batería, entre 33 y 37 °C, siempre enchufado y sin ASR.
- En el iPhone, sin cable, con ASR llegó a `fair` a los 5 minutos y medio; sin ASR quedó en `nominal`. Enchufado, el
  detector solo llegó a `serious`. La batería bajó 5 % en cada pasada de unos 15 minutos
  ([2026-11-21](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md#3-estado-térmico)).
- Android informa el estado térmico con `PowerManager.getCurrentThermalStatus()` (API 29, de `NONE` a `SHUTDOWN`) y
  el margen con `getThermalHeadroom()` (API 30, no más de una vez cada 10 s); algunos equipos devuelven siempre `NONE`
  ([PowerManager](https://developer.android.com/reference/android/os/PowerManager),
  [ADPF térmico](https://developer.android.com/games/optimize/adpf/thermal)).

**Inferido:**

- El detector usa los cuatro A720 y el ASR pide dos hilos más: van a competir. Las salidas posibles son darle al ASR
  los núcleos lentos, bajar el detector a 3 hilos o pasar el detector a la GPU (Vulkan), que libera CPU pero mueve el
  riesgo (H11). Ninguna se midió.
- Una llamada de 10 a 15 minutos sin cable probablemente calienta el A56 más que el iPhone, que tiene GPU para el
  detector. Si el teléfono baja la frecuencia, cada consulta tarda más y el aviso llega más tarde: la app tiene que
  anotar el estado térmico en cada consulta para poder explicarlo.

> **Estado: propuesta sin discutir.** La app no cambia de configuración según la temperatura (cambiar hilos o
> backend mueve el riesgo). Solo la anota, y si la consulta tarda más que el turno siguiente, la cola de §2.4 lo
> absorbe y queda registrado.

## 6. El modelo en el teléfono

**Verificado:** el GGUF pesa 3,26 GB ([corrida del iPhone](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md#cómo-se-mide)).
En Google Play cada paquete de recursos puede pesar hasta 1,5 GB, lo que se instala con la app suma hasta 4 GB, y lo
que se baja después (fast-follow u on-demand) hasta 30 GB
([límites de tamaño](https://support.google.com/googleplay/android-developer/answer/9859372)). Las bibliotecas
nativas tienen que estar alineadas a páginas de 16 KB para apps que apunten a Android 15; el NDK r28 o posterior ya lo
hace por defecto, y el A56 se compiló con el NDK 28.2
([page sizes](https://developer.android.com/guide/practices/page-sizes)).

**Inferido:** para el prototipo de la tesis alcanza con copiar el GGUF y los modelos del ASR por adb, como ahora. Para
publicar, el GGUF habría que partirlo en paquetes de menos de 1,5 GB o bajarlo de un servidor propio en el primer
uso, y verificar su SHA-256 (`6dd7ac24…5937d`) antes de cargarlo.

## 7. Qué se lleva tal cual y qué hay que escribir

| Pieza | Qué hay | Qué se hace |
|---|---|---|
| llama.cpp `6c01da62`, build del A56 (NDK 28.2, `android-28`, CPU, `GGML_OPENMP=OFF`) | [Repetir de la corrida del 2026-11-11](../../experiments/slm-directo/corridas/2026-11-11_a56-latencia-172/README.md#repetir) | **Tal cual.** Se agrega el blanco `llama-server-impl` como biblioteca, igual que en el iPhone |
| Prompts `tarea_c_consejos.txt`, `salida_json_c.txt`, `motivo_c_corte.txt` | [`prompts/`](../../experiments/slm-directo/prompts/) | **Tal cual,** como recursos de la app, con su SHA-256 en el manifiesto |
| GGUF y modelos del ASR (Parakeet int8, Silero) | Los de las corridas | **Tal cual** |
| `asr.cpp` | [corrida del 2026-11-21](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/app/asr.cpp) | **Se adapta:** entrada por bloques en vez de WAV; el motor no cambia |
| Lanzar `llama-server` dentro de la app | [`main.mm`](../../experiments/slm-directo/corridas/2026-11-20_iphone-15-pro-max-latencia/app/main.mm) | **Se escribe** el equivalente en JNI (chico) |
| Gramática y prefijo de solo el número | `gramatica_numero`, `PREFIJOS` en [`correr_android_latencia.py`](../../experiments/slm-directo/correr_android_latencia.py) | **Se porta** a C++ |
| Armado del mensaje, consulta, motivo diferido | `armar_mensaje_usuario`, `DetectorSLMCorteRiesgo`, `DetectorSLMJSONCortado` en [`detectores.py`](../../experiments/slm-directo/detectores.py) | **Se porta** a C++ |
| Turnos | [`turnos.py`](../../experiments/voip/turnos.py) y sus pruebas en [`voip/tests/`](../../experiments/voip/tests/) | **Se porta;** las pruebas de Python sirven de casos de referencia |
| Aviso único y estado de la llamada | [`llamada.py`](../../experiments/voip/llamada.py) | **Se porta** la parte de disparo y aviso |
| Filtros de texto del ASR | [`motores.py`](../../experiments/asr-local/motores.py) | **Se porta** |
| Medición por adb (agenda, memoria, temperatura, resumen) | `medir.py`, `resumir.py`, `ejecutar_agenda.py`, `sintetizar.py` de las corridas del A56 y del iPhone | **Se reutiliza** con cambios menores |
| Llamada VoIP, permisos, servicio en primer plano, pantalla de llamada y aviso | — | **Se escribe** desde cero (Kotlin). Es la parte más grande |
| Muestreo de memoria, estado térmico y batería dentro de la app | El de `main.mm`, para iOS | **Se escribe** con las API de Android (`PowerManager`, `BatteryManager`) |

## 8. Qué medir para validarla

En orden: cada paso usa lo que validó el anterior. Las mediciones repiten las definiciones de las corridas del A56 y
del iPhone (por línea, procesar, generar, primer aviso, atraso del ASR) para que se puedan comparar.

| | Medición | Cómo | Qué responde |
|---|---|---|---|
| M1 | Detector con la configuración final en el A56 | `correr_android_latencia.py --consulta numero` con `c-consejos`, 6 conversaciones, como el 2026-11-11 | La línea de base que falta: nunca se midió `c-consejos` en el A56 |
| M2 | ASR solo en el A56 | `asr.cpp` sobre el WAV de la corrida del iPhone, a ritmo real | ¿Va a tiempo real? Atraso mediano, p95, bloques con más de 1 s, memoria |
| M3 | **ASR + detector en el A56, sin cable** | La réplica de la [corrida del iPhone](../../experiments/slm-directo/corridas/2026-11-21_iphone-15-pro-max-asr-y-detector/README.md): misma agenda, 12 min, una pasada con ASR y una sin, teléfono frío y desenchufado | La pregunta que decide todo: ¿el ASR atrasa al detector?, ¿cuánto calienta?, ¿cuánta batería? |
| M4 | El núcleo en C++ hace lo mismo que Python | Mismas entradas al núcleo y a `turnos.py` + `detectores.py`: turnos cerrados, consultas y riesgo por línea | Que la app mide lo que se evaluó. El riesgo puede diferir como entre dos corridas iguales (11 de 1.392 líneas en [solo el número](../../experiments/slm-directo/corridas/2026-11-21_solo-el-numero/README.md)), no más |
| M5 | Llamada larga | Audio sintético de 60 min, contexto 16.384 | Memoria y tiempo por consulta en el turno 55, 100 y 200; que el desborde se avise y no trunque |
| M6 | Segundo plano | Con la app real: pantalla apagada, otra app adelante, 30 min, con el ahorro de batería de Samsung en su valor de fábrica | Que el servicio no muera ni pierda audio |
| M7 | Llamada VoIP entre dos teléfonos con audio sintético | El teléfono OTRA reproduce la agenda por la llamada | Atraso del aviso de punta a punta (fin de la voz de OTRA → aviso en pantalla), cortes de turno reales contra los de la agenda |
| M8 | Llamada VoIP con voz humana | Guiones de la demo, con consentimiento | Que anda con eco, ruido y red reales. **No mide detección:** son pocos guiones |

Cada medición anota, como las anteriores: commit, hashes del GGUF y de los prompts, parámetros del servidor, modelo
de teléfono y versión de Android, si estaba enchufado, el estado térmico y la batería al empezar y al terminar.

**Para leer M3 (propuesta sin discutir):** la app «entra» en el A56 si el ASR sigue a tiempo real con el detector
corriendo (p95 del atraso menor a 1 s), ninguna consulta espera a la anterior más de un turno y el sistema no mata la
app. Estos criterios se escriben antes de correr, como pide el [ADR 0005](adr/0005-reglas-de-evaluacion-escritas-antes-de-correr.md).

## 9. Lo que esta versión no resuelve

- **Las llamadas celulares comunes.** Con la opción A, la estafa tiene que llegar por la app. A′ lo acerca, pero
  agrega un proveedor y el desvío de línea.
- **La calidad de la detección en llamadas reales.** La validación de §8 mide si la app funciona, no si detecta bien;
  eso sigue dependiendo del corpus y de la evaluación final.
- **El aviso a la otra parte y el consentimiento.** Google usa un pitido audible; la tesis no lo decidió. Lo que dice
  la ley está en [PRIVACIDAD-DEL-SISTEMA.md](../corpus/PRIVACIDAD-DEL-SISTEMA.md).
- **El audio nunca se guarda ni sale del teléfono para el análisis.** Las mediciones con voz humana siguen la regla
  del repositorio: audio fuera de Git.
