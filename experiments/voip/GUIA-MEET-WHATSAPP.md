GUÍA · Probar el panel solo, con el celular como «Otra persona»

Sirve para ensayar sin depender de nadie. La notebook hace de **Persona protegida** (su micrófono)
y el celular hace de **Otra persona** (su voz llega por Meet o por WhatsApp).
Hacé primero la receta de Meet: no necesita instalar nada. Si querés el detalle técnico, está en
[README §11](README.md#11-otra-persona-desde-meet-o-blackhole-80).

Antes de cualquiera de las dos: **ponete auriculares** y bajá a cero el volumen del celular
(o usá también auriculares en el celular). Si el micrófono de la notebook escucha al celular,
las dos voces se mezclan y el ensayo no sirve.

## Receta 1 · Meet (pestaña de Chrome, sin BlackHole)

1. En una terminal, dentro de `experiments/voip`, levantá el servidor:
   `python servidor.py --detector slm --modelo qwen3.5:0.8b-q8_0`
   (para probar sin modelo: `--detector reglas`).
2. Abrí Chrome en `http://localhost:8765/`. Dejá esa pestaña para el final.
3. En otra pestaña abrí `meet.google.com`, tocá «Nueva reunión» y entrá. Apagá el micrófono
   de la notebook en Meet (la protegida se toma desde el panel, no desde Meet).
4. Con el celular, entrá a la misma reunión (app de Meet y el código o enlace de la reunión).
5. En el panel: «Otra persona» → **Meet · pestaña de Chrome**; «Persona protegida» → **Micrófono**.
   Tocá **Iniciar llamada**, elegí la pestaña de Meet (no el panel, ni una ventana, ni la pantalla)
   y activá **Compartir audio de la pestaña**.
6. Hablá por el celular, por ejemplo: «Hola, te llamo del banco, necesito el código que te llegó por SMS».
   Después hablá vos por la notebook.

**Comprobación:** sube el medidor de *Otra persona* cuando habla el celular, y aparece su texto
a la izquierda. Cuando hablás vos, sube el de *Persona protegida*, no el otro.

Si falla:
- **No inicia y dice que la pestaña no comparte audio.** Elegiste una ventana o la pantalla, o no
  activaste «Compartir audio de la pestaña». Tocá Iniciar de nuevo y elegí la pestaña de Meet.
- **Se escucha eco, o suben los dos medidores a la vez.** El micrófono de la notebook oye lo que
  suena por los parlantes. Dejá tildada «Cancelar eco (sin auriculares)»: Chrome resta del micrófono
  lo que reproduce la pestaña de Meet o WhatsApp Web. Si igual sube, bajá el volumen o usá auriculares
  y destildala para mandar el audio crudo. Cada llamada guarda la elección en `inicio_panel`.
- **No sube ningún medidor.** Revisá que el celular esté con el micrófono encendido en Meet y
  que la pestaña de Meet no esté silenciada.

## Receta 2 · WhatsApp Desktop con BlackHole

Hace falta [BlackHole 2ch](https://github.com/ExistentialAudio/BlackHole) instalado y **dos cuentas
de WhatsApp distintas**: WhatsApp no deja llamarse a uno mismo, así que el celular tiene que usar
otra cuenta que la de la notebook.

1. Levantá el servidor y abrí el panel igual que en la receta de Meet (pasos 1 y 2).
2. Abrí **Configuración de Audio MIDI**, mostrá los dispositivos de audio y tocá
   **+ → Crear dispositivo de salida múltiple**. Marcá **tus auriculares** y **BlackHole 2ch**.
   Poné los auriculares como dispositivo principal (reloj) y tildá **Corrección de deriva**
   en BlackHole 2ch.
3. Subí el volumen de los auriculares ahora: con la salida múltiple, las teclas de volumen no funcionan.
4. En **Ajustes del Sistema → Sonido**, elegí esa salida múltiple como salida y tu micrófono físico
   como entrada. Cerrá notificaciones y otros sonidos del sistema.
5. Llamá a la notebook por WhatsApp desde el celular y atendé en WhatsApp Desktop.
6. En el panel: «Otra persona» → **WhatsApp / escritorio · BlackHole**; «Persona protegida» →
   **Micrófono**. Tocá **Iniciar llamada** y hablá por el celular.

**Comprobación:** igual que en Meet: sube el medidor de *Otra persona* y aparece su texto.

Al terminar, volvé la salida de Sonido a tus auriculares.

Si falla:
- **BlackHole no aparece.** Está instalado pero macOS no lo cargó. En una terminal,
  `sudo killall coreaudiod`, y volvé a abrir Chrome. Corta el audio de las apps unos segundos:
  hacelo antes del ensayo.
- **No te escuchás en los auriculares.** La salida del sistema no es la múltiple, o los auriculares
  no están tildados en ella.
- **Sube el medidor pero no aparece texto, o no sube nada.** La salida del sistema no es la múltiple,
  así que BlackHole no recibe la voz. Revisá el paso 4.
- **Se escucha eco.** El micrófono oye al celular; bajale el volumen.
- **El selector de WhatsApp no ofrece BlackHole.** El 2026-10-28, WhatsApp Desktop listó en
  «Altavoz» solo «Utiliza los ajustes del sistema (Bocinas…)» y «Bocinas de MacBook Pro», aunque
  macOS tenía la salida múltiple elegida, y BlackHole midió silencio. En ese caso usá WhatsApp Web
  en Chrome con la receta 1, compartiendo esa pestaña.
