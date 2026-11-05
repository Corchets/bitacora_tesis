import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
import {remuestrearPCM16} from '../audio-pcm.mjs';

test('finalizar entrega el bloque incompleto antes de confirmar el fin de captura', () => {
  const mensajes = [];
  let Processor;
  const codigo = readFileSync(new URL('../audio-worklet.mjs', import.meta.url), 'utf8')
    .replace(/^import .*;\s*$/m, '');
  runInNewContext(codigo, {remuestrearPCM16, sampleRate: 48000,
    AudioWorkletProcessor: class { port = {postMessage: m => mensajes.push(m)}; },
    registerProcessor: (_nombre, clase) => { Processor = clase; }});
  const captura = new Processor();
  captura.process([[new Float32Array(384).fill(0.5)]]);
  assert.equal(mensajes.length, 0, 'todavía no se completaron los 40 ms');
  assert.equal(typeof captura.port.onmessage, 'function', 'debe poder vaciar la última fracción');
  captura.port.onmessage({data: {tipo: 'finalizar'}});
  assert.equal(mensajes[0].byteLength, 128 * 2);
  assert.equal(new DataView(mensajes[0]).getInt16(0, true), 16383);
  assert.equal(mensajes[1].tipo, 'audio_finalizado');
  assert.equal(captura.process([[new Float32Array(384)]]), false);
  assert.equal(mensajes.length, 2, 'no entra audio nuevo después de finalizar');
});
