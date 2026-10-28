import {test} from 'node:test';
import assert from 'node:assert/strict';
import {prepararAudio} from '../audio-navegador.mjs';

test('la captura avisa si no sale PCM y libera el micrófono; recibir audio cancela el aviso', async t => {
  t.mock.timers.enable({apis: ['setTimeout']});
  const originales = Object.getOwnPropertyDescriptors(globalThis);
  let nodo, socket, cierres = 0, paradas = 0, activaciones = 0;
  const cola = new ArrayBuffer(64);
  class Contexto {
    audioWorklet = {addModule: async () => {}};
    createMediaStreamSource() { return {connect() {}, disconnect() {}}; }
    async resume() { activaciones++; }
    async close() { cierres++; }
  }
  class Nodo {
    port = {postMessage: m => {
      if (m.tipo === 'finalizar') {
        this.port.onmessage({data: cola});
        this.port.onmessage({data: {tipo: 'audio_finalizado'}});
      }
    }};
    constructor() { nodo = this; }
    connect() {}
    disconnect() {}
  }
  class Socket {
    static OPEN = 1;
    readyState = 1;
    enviados = [];
    constructor() { socket = this; queueMicrotask(() => this.onopen()); }
    send(data) { this.enviados.push(data); }
    close() {}
  }
  Object.assign(globalThis, {AudioContext: Contexto, AudioWorkletNode: Nodo, WebSocket: Socket,
    location: {protocol: 'http:', host: 'localhost:8765'}});
  const errores = [];
  const pista = {stop() { paradas++; }, addEventListener() {}};
  const stream = {getTracks: () => [pista], getAudioTracks: () => [pista]};
  try {
    const captura = prepararAudio(stream, 'protegida', e => errores.push(e));
    assert.equal(activaciones, 1, 'se activa antes de esperar al servidor');
    await captura.iniciar();
    t.mock.timers.tick(5000);
    assert.match(errores[0], /no está enviando audio/);
    assert.equal(paradas, 1);
    assert.equal(cierres, 1);

    const otra = prepararAudio(stream, 'protegida', e => errores.push(e));
    await otra.iniciar();
    const bloque = new ArrayBuffer(1280);
    nodo.port.onmessage({data: bloque});
    assert.deepEqual(socket.enviados, [bloque]);
    t.mock.timers.tick(6000);
    assert.equal(errores.length, 1);
    let confirmada = false;
    const fin = otra.finalizar().then(() => { confirmada = true; });
    await Promise.resolve();
    assert.deepEqual(socket.enviados, [bloque, cola, 'fin_audio']);
    assert.equal(confirmada, false, 'no se cierra la captura antes de la confirmación del servidor');
    socket.onmessage({data: 'audio_recibido'});
    await fin;
    assert.equal(confirmada, true);
    otra.detener();
    const sinConfirmacion = prepararAudio(stream, 'protegida', e => errores.push(e));
    await sinConfirmacion.iniciar();
    const rechazo = assert.rejects(sinConfirmacion.finalizar(), /confirmar la recepción del último audio/);
    t.mock.timers.tick(8000);
    await rechazo;
    sinConfirmacion.detener();
  } finally {
    for (const key of ['AudioContext', 'AudioWorkletNode', 'WebSocket', 'location']) {
      if (originales[key]) Object.defineProperty(globalThis, key, originales[key]);
      else delete globalThis[key];
    }
  }
});
