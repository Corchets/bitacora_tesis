// @ts-check
import {prepararAudio, verificarCaptura, mensajeErrorMicrofono} from './audio-navegador.mjs';

const FALTA_BLACKHOLE = 'No encontramos BlackHole como entrada. BlackHole 2ch puede estar instalado sin aparecer: reiniciá coreaudiod vos desde Terminal (sudo killall coreaudiod), volvé a abrir Chrome y reintentá. Revisá la guía de salida múltiple.';

/**
 * Consigue y valida los dos canales antes de permitir «iniciar»; no envía audio todavía.
 * Llamar directamente desde el clic para conservar la activación de getDisplayMedia.
 * @param {'meet'|'blackhole'} tipo
 * @param {MediaTrackConstraints} microfono
 * @param {(mensaje: string) => void} alError
 * @param {AbortSignal} signal
 */
export async function prepararFuentes(tipo, microfono, alError, signal) {
  /** @type {MediaStream[]} */
  const streams = [];
  /** @type {ReturnType<typeof prepararAudio>[]} */
  const emisores = [];
  function detener() {
    signal.removeEventListener('abort', detener);
    emisores.forEach(e => e.detener());
    streams.forEach(s => s.getTracks().forEach(t => t.stop()));
  }
  /** @param {string} mensaje */
  function fallar(mensaje) { detener(); alError(mensaje); }
  signal.addEventListener('abort', detener, {once: true});
  /** @param {MediaStream} stream */
  function registrar(stream) {
    if (signal.aborted) {
      stream.getTracks().forEach(t => t.stop());
      signal.throwIfAborted();
    }
    streams.push(stream);
  }
  let etapa = tipo === 'meet' ? 'meet' : 'microfono';
  try {
    signal.throwIfAborted();
    verificarCaptura();
    /** @type {MediaStream|undefined} */
    let otra;
    if (tipo === 'meet') {
      if (!navigator.mediaDevices.getDisplayMedia) throw new Error('Abrí este panel en Chrome para compartir la pestaña de Meet.');
      // Pedir primero conserva el gesto del clic; video es obligatorio para esta API.
      otra = await navigator.mediaDevices.getDisplayMedia({video: true, audio: true});
      registrar(otra);
      if (!otra.getAudioTracks().some(t => t.readyState === 'live')) {
        throw new Error('La pestaña compartida no trae audio. Elegí la pestaña de Meet y activá «Compartir audio de la pestaña». No se inició la llamada.');
      }
      if (otra.getVideoTracks()[0]?.getSettings().displaySurface !== 'browser') {
        throw new Error('Elegí una pestaña de Chrome, no una ventana ni la pantalla completa, y compartí su audio. No se inició la llamada.');
      }
    }
    otra?.getVideoTracks().forEach(t => t.addEventListener('ended', () => fallar('Dejaste de compartir Meet. Iniciá una nueva llamada.')));
    etapa = 'microfono';
    const protegida = await navigator.mediaDevices.getUserMedia({audio: microfono});
    registrar(protegida);
    if (/blackhole/i.test(protegida.getAudioTracks()[0]?.label || '')) {
      throw new Error('Elegí un micrófono físico para Persona protegida; BlackHole queda solo para Otra persona.');
    }
    if (tipo === 'blackhole') {
      etapa = 'blackhole';
      // El permiso del micrófono hace visibles los nombres de entradas.
      const entradas = await navigator.mediaDevices.enumerateDevices();
      signal.throwIfAborted();
      const dispositivo = entradas.find(d => d.kind === 'audioinput'
        && !['default', 'communications'].includes(d.deviceId) && /blackhole/i.test(d.label));
      if (!dispositivo) throw new Error(FALTA_BLACKHOLE);
      otra = await navigator.mediaDevices.getUserMedia({audio: {
        deviceId: {exact: dispositivo.deviceId}, echoCancellation: false,
        noiseSuppression: false, autoGainControl: false
      }});
      registrar(otra);
      if (protegida.getAudioTracks()[0]?.getSettings().deviceId === dispositivo.deviceId) {
        throw new Error('Elegí un micrófono físico para Persona protegida; BlackHole queda solo para Otra persona.');
      }
    }
    if (!otra || streams.some(s => !s.getAudioTracks().some(t => t.readyState === 'live'))) {
      throw new Error('Se desconectó una entrada antes de iniciar. Volvé a elegir las fuentes. No se inició la llamada.');
    }
    // El video solo permite seleccionar y conservar el indicador de compartir; no se transmite.
    emisores.push(prepararAudio(protegida, 'protegida', fallar));
    emisores.push(prepararAudio(otra, 'otra', fallar));
    return {detener, iniciar: async () => { await Promise.all(emisores.map(e => e.iniciar())); }};
  } catch (error) {
    detener();
    if (error instanceof Error && error.name === 'Error') throw error;
    if (etapa === 'meet') throw new Error('No pudimos compartir Meet. Permití la captura en Chrome y en los ajustes de grabación de pantalla del sistema; elegí una pestaña con audio. No se inició la llamada.');
    if (etapa === 'blackhole') throw new Error('No pudimos abrir BlackHole. Revisá el permiso de micrófono de Chrome y que el dispositivo esté disponible. No se inició la llamada.');
    throw new Error(mensajeErrorMicrofono(error));
  }
}
