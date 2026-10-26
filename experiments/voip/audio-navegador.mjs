// @ts-check

/** @param {unknown} error @returns {string} */
export function mensajeErrorMicrofono(error) {
  const nombre = error instanceof Error ? error.name : '';
  if (nombre === 'NotAllowedError' || nombre === 'SecurityError') {
    return 'No tenemos permiso para usar el micrófono. Permitilo en el navegador y en los ajustes del sistema.';
  }
  if (nombre === 'NotFoundError' || nombre === 'OverconstrainedError') {
    return 'No encontramos ese micrófono. Conectalo o elegí otro dispositivo de entrada.';
  }
  if (nombre === 'NotReadableError') return 'No pudimos abrir el micrófono. Revisá si otra aplicación lo está usando.';
  return error instanceof Error ? error.message : 'No pudimos capturar el audio.';
}

export function verificarCaptura() {
  if (!globalThis.isSecureContext) {
    throw new Error('Para usar el micrófono, abrí este panel en http://localhost:8765 o http://127.0.0.1:8765 en la notebook del servidor.');
  }
  if (!navigator.mediaDevices?.getUserMedia || !globalThis.AudioWorkletNode) {
    throw new Error('Este navegador no permite capturar el micrófono con AudioWorklet. Abrí el panel en Chrome actualizado.');
  }
}

/**
 * Toma posesión del stream; detener() libera todos sus tracks incluso durante el arranque.
 * Prepará después del permiso e iniciá al recibir el «inicio» del servidor.
 * @param {MediaStream} stream
 * @param {'protegida'|'otra'} rol
 * @param {(mensaje: string) => void} alError
 */
export function prepararAudio(stream, rol, alError) {
  const contexto = new AudioContext();
  const fuente = contexto.createMediaStreamSource(stream);
  /** @type {AudioWorkletNode|null} */
  let nodo = null;
  /** @type {WebSocket|null} */
  let ws = null;
  let detenido = false;
  let iniciado = false;

  function detener() {
    if (detenido) return;
    detenido = true;
    stream.getTracks().forEach(track => track.stop());
    fuente.disconnect();
    if (nodo) { nodo.port.onmessage = null; nodo.disconnect(); }
    ws?.close();
    void contexto.close();
  }
  /** @param {string} mensaje */
  function fallar(mensaje) {
    if (detenido) return;
    detener();
    alError(mensaje);
  }
  stream.getAudioTracks().forEach(track => track.addEventListener('ended', () => {
    fallar('Se desconectó la entrada de audio. Conectala e iniciá una nueva llamada.');
  }));

  async function iniciar() {
    if (detenido || iniciado) return;
    iniciado = true;
    try {
      await contexto.audioWorklet.addModule(new URL('./audio-worklet.mjs', import.meta.url));
      if (detenido) return;
      nodo = new AudioWorkletNode(contexto, 'captura-pcm', {outputChannelCount: [1]});
      const socket = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/audio?rol=${rol}`);
      ws = socket;
      await new Promise((resolve, reject) => {
        const tiempo = setTimeout(() => reject(new Error('No se pudo conectar el audio al servidor.')), 8000);
        socket.onopen = () => { clearTimeout(tiempo); resolve(undefined); };
        socket.onerror = () => { clearTimeout(tiempo); reject(new Error('Falló la conexión de audio.')); };
        socket.onclose = () => { clearTimeout(tiempo); reject(new Error('El servidor cerró la entrada de audio.')); };
      });
      if (detenido) return;
      socket.onclose = evento => {
        if (evento.code === 1000 && evento.reason === 'llamada terminada') detener();
        else fallar('Se cerró la conexión de audio. Iniciá una nueva llamada.');
      };
      socket.onerror = () => fallar('Se perdió la conexión de audio. Iniciá una nueva llamada.');
      nodo.onprocessorerror = () => fallar('Falló la captura de audio. Iniciá una nueva llamada.');
      nodo.port.onmessage = ({data}) => {
        if (detenido || socket.readyState !== WebSocket.OPEN) return;
        // Cortar evita acumular segundos de audio viejo si la red o el servidor se frenan.
        if (socket.bufferedAmount > 32000) { fallar('El envío de audio se atrasó. Revisá la conexión e iniciá otra llamada.'); return; }
        socket.send(data);
      };
      fuente.connect(nodo);
      // La salida del worklet es silencio: mantiene el procesamiento sin reproducir el micrófono.
      nodo.connect(contexto.destination);
      await contexto.resume();
    } catch (error) {
      fallar(mensajeErrorMicrofono(error));
    }
  }
  return {iniciar, detener};
}
