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
En ese punto faltaba confirmar la recuperación del audio; el resultado posterior se registra
a continuación. La lectura en la pantalla de la demo sigue pendiente.

## Referencia por frase y recuperación del micrófono

Después de reiniciar `coreaudiod`, Luciano confirmó que volvió el volumen. El servidor
registró seis actualizaciones con texto y tres frases finales en su prueba posterior.
Esto confirma la recuperación del recorrido, sin medir calidad de voz ni cerrar #94/D09.

Por pedido del usuario, cada frase final de una prueba nueva tiene ahora su propio campo
«Lo que dije en realidad». Se conserva en `referencias_por_segmento`, validado contra los
segmentos finales del JSONL. La referencia global se deriva de esos textos para mantener
compatibilidad con las herramientas existentes. El Historial permite editar cada campo;
las pruebas anteriores conservan su referencia global. La medición offline omite referencias
por frase incompletas, en lugar de medir audio completo contra una parte de lo dicho.

Verificación posterior: 71 tests VoIP, 37 de la herramienta de medición y 3 Node pasan.
El test del servidor cubre claves ajenas/incompletas, tipos y largos inválidos, orden de las
frases, guardado, consulta y edición. Se verificó también en Chrome, por accesibilidad:
tres campos debajo de sus transcripciones, ingreso de referencias TTS, «Guardar prueba»,
respuesta de éxito, persistencia en disco y los tres campos editables en el Historial.
El detector mecánico señaló seis observaciones de estilo preexistentes, sin nuevos errores.

Antes de reiniciar el servidor para cargar el cambio, se preservó fuera de Git una copia
local de la prueba de voz todavía sin guardar; no se publica audio ni texto de esa prueba.
La prueba nueva usada para verificar los campos envió PCM sintético con
`inicio_panel.fuentes.protegida.origen = verificacion_pcm_tts`; no se considera voz humana.
Al terminar se retiró únicamente esa prueba sintética temporal del Historial.

## Terminar prueba conserva el audio pendiente

Otro pedido del usuario: al tocar «Terminar prueba», mostrar lo grabado hasta ese instante,
aunque no se haya cumplido el corte de silencio. Se reprodujo un fallo en el AudioWorklet:
384 muestras a 48 kHz producían un bloque parcial de 128 muestras a 16 kHz que no se enviaba
al detener la captura. El test nuevo falló con el código anterior.

Ahora el worklet entrega la cola incompleta y confirma que dejó de capturar. El navegador
manda `fin_audio` por el mismo socket del PCM y espera `audio_recibido`, emitido después de
procesar los bloques anteriores. Recién entonces libera la entrada y solicita terminar por
el socket del panel. El ASR vacía su lookahead y emite los finales antes de `fin`. Los controles
muestran «procesando el último audio» durante el cierre. La confirmación tiene un máximo de
8 s y, si falla, se informa el error. Meet/BlackHole vacían ambos emisores antes de cerrar.

Verificación: 72 tests Python de VoIP y 4 Node pasan. Se cubren la cola del worklet, el orden
de envío, la espera de confirmación, su timeout, la conservación exacta del PCM y finales antes
de `fin`. Con Zipformer real y el canal de otra persona del TTS `SC-WA-CODE-01`, se quitó todo
el silencio posterior a la última voz: se enviaron y guardaron exactamente 281384 muestras,
incluida una cola de 424 muestras. Al terminar apareció «Decime el código de activación que
recibiste por sms» dentro del último final. Se usó corte de 3 s y umbral 0,005; la entrada se
envió acelerada para verificar el cierre, sin estimar latencia ni calidad. Se preservó localmente
la prueba humana aún sin guardar antes de reiniciar el servidor para cargar el cambio.

## Comentario listo para GitHub

```markdown
Closes #91
Refs #87, #94

Probar el ASR permite guardar «Lo que dije en realidad» por frase final, y editar cada
referencia desde el Historial. El servidor valida los segmentos y deriva el texto global
para mantener compatibilidad. La medición omite pruebas con referencias incompletas.
Terminar vacía también el audio pendiente del navegador, espera su recepción y muestra la
última frase sin esperar el corte por silencio. Se conservan Borrar sin cortar el micrófono,
guardado explícito y compatibilidad con pruebas anteriores.

Evidencia: experiments/voip/corridas/2026-10-28-correcciones-panel.md.
Pasan 72 tests VoIP, 37 de medición y 4 Node. Guardado y lectura de tres referencias
verificados desde Chrome hasta el manifiesto; cierre sin silencio final probado con Zipformer real.
El micrófono volvió tras reiniciar coreaudiod;
el servidor recibió tres frases reales con texto.

D08 y D09 siguen abiertas. Próxima acción de #94: completar referencias humanas por frase
y medir calidad con voz real. El 0.8B mantiene la falsa alarma documentada en soporte legítimo.
```
