// @ts-check
import { remuestrearPCM16 } from './audio-pcm.mjs';

/** @extends {AudioWorkletProcessor} */
class CapturaPCM extends AudioWorkletProcessor {
  constructor() {
    super();
    this.estado = {suma: 0, peso: 0};
    this.bloque = new ArrayBuffer(640 * 2);
    this.vista = new DataView(this.bloque);
    this.usadas = 0;
  }

  /** @param {Float32Array[][]} entradas @returns {boolean} */
  process(entradas) {
    const canales = entradas[0];
    if (!canales?.length) return true;
    const mono = new Float32Array(canales[0].length);
    for (const canal of canales) {
      for (let i = 0; i < mono.length; i++) mono[i] += canal[i] / canales.length;
    }
    const {pcm, estado} = remuestrearPCM16(mono, sampleRate, this.estado);
    this.estado = estado;
    for (const muestra of pcm) {
      this.vista.setInt16(this.usadas * 2, muestra, true);
      if (++this.usadas === 640) {
        this.port.postMessage(this.bloque, [this.bloque]);
        this.bloque = new ArrayBuffer(1280);
        this.vista = new DataView(this.bloque);
        this.usadas = 0;
      }
    }
    return true;
  }
}
registerProcessor('captura-pcm', CapturaPCM);
