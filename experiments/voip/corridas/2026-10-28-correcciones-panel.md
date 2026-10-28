# Correcciones del panel — 2026-10-28

Referencias: [#87](https://github.com/Corchets/bitacora_tesis/issues/87) y
[#94](https://github.com/Corchets/bitacora_tesis/issues/94). No cierran el ensayo con voz real,
D08 ni D09. Base de código: `b289fc8`, con los cambios del commit que incorpora este registro.

## Fallos reproducidos y cambios

- `soundfile.read` sobre el ejemplo legítimo devolvía exactamente `Error opening … System error`:
  faltaba `experiments/asr-local/audio` en la copia `bitacora_tesis-voip-asr`.
  Se enlazó localmente el audio existente de `bitacora_tesis-voip`, fuera de Git. El servidor
  ahora informa cómo generar el WAV ausente y rechaza audios ilegibles antes de abrir la llamada.
- `body` tenía alto fijo y ocultaba el desborde. La página ahora crece con la conversación,
  la prueba y el Historial, sin scroll interno obligatorio. Las actualizaciones no llevan
  la pantalla hacia una frase que quedó fuera del tramo visible que está leyendo la persona.
- «Probar el ASR» ocultaba y deshabilitaba el selector de micrófono si la llamada tenía
  seleccionada la voz del ejemplo. Ahora permite elegir y buscar la entrada en esa pestaña.
- La última prueba previa no tenía canales ni bloques de audio, ni WAV: el modelo se había
  cargado, pero la captura no le entregó sonido. Se adelantó el pedido de activación de Web Audio
  y se agregó un aviso si pasan cinco segundos sin salir PCM del AudioWorklet.
- Se generaron los ejemplos de soporte de 14 y 13 turnos a partir de textos de desarrollo
  existentes, con Paulina/Mónica y pausa de 1 s. El panel los ofrece primero y el Historial
  identifica sus diferencias. Se mantienen los ejemplos cortos de WhatsApp.

## Verificación

- 70 tests Python de VoIP, 169 de ASR y 14 de replay: pasan.
- 3 tests Node: pasan, incluido el caso sin PCM que libera el micrófono y el caso con PCM
  que cancela el aviso. Se verificó la sintaxis del script del panel y de los módulos modificados.
- Regresión del selector: se ejecutó `actualizarControles` extraída del HTML con controles
  simulados. La comprobación falla con `HEAD` previo y pasa con el cambio para prueba ASR,
  llamada con ejemplo y llamada con micrófono.
- ASR real por `/audio?rol=protegida`, PCM16 a 16 kHz en bloques de 40 ms: el canal del
  ejemplo corto de estafa produjo 12 actualizaciones y tres frases finales. Conservó
  «decime el código de activación que recibiste por SMS». Prueba de funcionamiento enviada
  más rápido que tiempo real, sin usarla para estimar latencia ni calidad de voz humana.
- Dos llamadas completas al ritmo real por `/panel` en el servidor de `127.0.0.1:8765`:

| Guion TTS | Duración del WAV | Frases finales | Evaluaciones | Avisos |
|---|---:|---:|---:|---:|
| `SC-SOPORTE-CLAVE-01` | 89,7 s | 19 | 4 | 1 |
| `LG-SUPPORT-INFO-01` | 80,4 s | 16 | 9 | 1 |

Configuración compartida: Zipformer Kroko, 2 hilos por canal, corte 0,8 s, umbral RMS
0,005, detector SLM `qwen3.5:0.8b-q8_0`, prompt `tarea`, seed 42, hablantes A/B por aparición.
Los registros locales quedaron en `llamadas/2026-10-28_121412-233764` y
`llamadas/2026-10-28_121554-922726`. No se versiona audio ni transcripciones en este registro.

El guion legítimo dio una **falsa alarma respecto de su clase de diseño** a 54,402 s:
el detector confundió la indicación «Olvidé mi contraseña» con una solicitud de contraseña.
El aviso de la estafa salió a 20,456 s, antes del pedido explícito de credenciales, con un motivo
que mencionaba un código no pedido en ese fragmento. Son límites observados del detector;
estas dos llamadas no permiten estimar su desempeño general y no justifican cambiar el prompt.

El detector mecánico de UI señaló 14 observaciones de estilo y un salto de jerarquía de títulos
en componentes existentes, fuera del alcance de estos cambios. La inspección visual por CUA
no pudo completarse: la captura devolvió `stageManagerProcessNotRunning` y el control de Chrome
se interrumpía por cambios de ventana. Se recargó el panel y se verificaron los nombres nuevos
mediante accesibilidad. Luciano confirmó que el síntoma previo era ausencia de texto y de volumen.
El dispositivo de entrada predeterminado del sistema figura como «Micrófono externo».
Una prueba posterior recibió 12,08 s de PCM con pico y RMS exactamente cero en ambos
canales. La captura ya entregaba bloques; la entrada seleccionada estaba enviando silencio.
El selector se mantenía oculto por su contenedor padre: se corrigió también esa regla y se
pidió probar la entrada explícita «Micrófono de MacBook Pro».
Luciano confirmó que el micrófono explícito del MacBook seguía sin señal. Se intentó
abrir esa entrada directamente con PortAudio, a 16 kHz y a su frecuencia nativa de 48 kHz:
ambos intentos fallaron con `Audio Hardware Not Running` / `PaErrorCode -9986`. Es evidencia
de un fallo de apertura también fuera del navegador. `sudo -n killall coreaudiod` devolvió
`sudo: a password is required`; se indicó al usuario reiniciarlo desde Terminal, con su
contraseña, y reabrir Chrome. No se modificaron permisos ni configuración de privacidad.
Falta confirmar la recuperación del audio tras ese reinicio y la lectura
de conversaciones largas en la pantalla de la demo.

## Comentario listo para GitHub

```markdown
Refs #87, #94

Corregidos el scroll general, la carga de ejemplos ausentes y el selector de micrófono
oculto en Probar el ASR. Se anticipa la activación del audio y se avisa si no sale PCM.
Agregados dos ejemplos completos de soporte, ejecutados y disponibles en el Historial.

Evidencia: experiments/voip/corridas/2026-10-28-correcciones-panel.md.
Pasan 253 tests Python y 3 Node; ASR real por WebSocket produce transcripciones.
El 0.8B dio una falsa alarma en el guion legítimo; queda registrada, sin cambiar el detector.

No se cierra #87 ni #94: próxima acción, confirmar la entrada de micrófono real en Chrome
y continuar la medición con voz humana. D08 y D09 siguen abiertas.
```
