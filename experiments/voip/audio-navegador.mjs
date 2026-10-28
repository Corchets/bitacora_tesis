// @ts-check
class ErrorCaptura extends Error {}

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
  return error instanceof ErrorCaptura ? error.message : 'No pudimos capturar el audio.';
}

export function verificarCaptura() {
  if (!globalThis.isSecureContext) {
    throw new ErrorCaptura('Para usar el micrófono, abrí este panel en http://localhost:8765 o http://127.0.0.1:8765 en la notebook del servidor.');
  }
  if (!navigator.mediaDevices?.getUserMedia || !globalThis.AudioWorkletNode) {
    throw new ErrorCaptura('Este navegador no permite capturar el micrófono con AudioWorklet. Abrí el panel en Chrome actualizado.');
  }
}

/**
 * Toma posesión del stream; detener() libera todos sus tracks incluso durante el arranque.
 * Prepará después del permiso e iniciá al recibir el «inicio» del servidor.
 * Si la pista termina sola (macOS cambia la entrada, se reconectan los auriculares, el sistema
 * la reinicia) y hay `reabrir`, se pide otra igual y se sigue por el mismo WebSocket, sin cortar
 * la llamada; solo se falla si no se puede reabrir o si pasa muchas veces seguidas.
 * @param {MediaStream} stream
 * @param {'protegida'|'otra'} rol
 * @param {(mensaje: string) => void} alError
 * @param {{reabrir?: () => Promise<MediaStream>, alReconectar?: (nombre: string) => void}} [opciones]
 */
export function prepararAudio(stream, rol, alError, opciones = {}) {
  const contexto = new AudioContext();
  // Pedir la activación durante el clic, antes de esperar el inicio por WebSocket.
  void contexto.resume().catch(() => {});
  let fuente = contexto.createMediaStreamSource(stream);
  /** @type {AudioWorkletNode|null} */
  let nodo = null;
  /** @type {WebSocket|null} */
  let ws = null;
  let detenido = false;
  let iniciado = false;
  /** @type {ReturnType<typeof setTimeout>|undefined} */
  let esperaAudio;
  /** @type {number[]} */
  let reaperturas = [];

  function detener() {
    if (detenido) return;
    detenido = true;
    clearTimeout(esperaAudio);
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
  /** @param {MediaStream} s */
  const nombre = s => s.getAudioTracks()[0]?.label || 'el micrófono';
  /** @param {MediaStream} vigilado */
  async function alTerminarPista(vigilado) {
    if (detenido || vigilado !== stream) return;
    const perdido = nombre(vigilado);
    const ahora = performance.now();
    reaperturas = reaperturas.filter(t => ahora - t < 10000);
    if (!opciones.reabrir || reaperturas.length >= 3) {
      fallar(`Se desconectó la entrada de audio (${perdido}). Conectala o elegí otra en «Micrófono» e iniciá de nuevo.`);
      return;
    }
    reaperturas.push(ahora);
    try {
      const nuevo = await opciones.reabrir();
      if (detenido) { nuevo.getTracks().forEach(t => t.stop()); return; }
      fuente.disconnect();
      stream = nuevo;
      fuente = contexto.createMediaStreamSource(nuevo);
      vigilar(nuevo);
      if (nodo) fuente.connect(nodo);
      opciones.alReconectar?.(nombre(nuevo));
    } catch {
      fallar(`Se desconectó la entrada de audio (${perdido}) y no se pudo volver a abrir. Conectala o elegí otra en «Micrófono» e iniciá de nuevo.`);
    }
  }
  /** @param {MediaStream} s */
  function vigilar(s) {
    s.getAudioTracks().forEach(track => track.addEventListener('ended', () => { void alTerminarPista(s); }));
  }
  vigilar(stream);

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
        const tiempo = setTimeout(() => reject(new ErrorCaptura('No se pudo conectar el audio al servidor.')), 8000);
        socket.onopen = () => { clearTimeout(tiempo); resolve(undefined); };
        socket.onerror = () => { clearTimeout(tiempo); reject(new ErrorCaptura('Falló la conexión de audio.')); };
        socket.onclose = () => { clearTimeout(tiempo); reject(new ErrorCaptura('El servidor cerró la entrada de audio.')); };
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
        clearTimeout(esperaAudio);
        // Cortar evita acumular segundos de audio viejo si la red o el servidor se frenan.
        if (socket.bufferedAmount > 32000) { fallar('El envío de audio se atrasó. Revisá la conexión e iniciá otra llamada.'); return; }
        socket.send(data);
      };
      fuente.connect(nodo);
      // La salida del worklet es silencio: mantiene el procesamiento sin reproducir el micrófono.
      nodo.connect(contexto.destination);
      esperaAudio = setTimeout(() => fallar(
        'El navegador abrió el micrófono pero no está enviando audio. Revisá la entrada de sonido y los permisos de Chrome; elegí un micrófono físico y volvé a iniciar.'
      ), 5000);
      await contexto.resume();
    } catch (error) {
      fallar(mensajeErrorMicrofono(error));
    }
  }
  return {iniciar, detener};
}
