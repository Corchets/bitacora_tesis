// @ts-check
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { remuestrearPCM16 } from '../audio-pcm.mjs';

test('tono de 1 kHz: conserva duración, frecuencia y amplitud a 48 y 44,1 kHz', () => {
  for (const hz of [48000, 44100, 16000]) {
    const entrada = Float32Array.from({length: hz}, (_, i) => 0.5 * Math.sin(2 * Math.PI * 1000 * i / hz - Math.PI / 2));
    // Los bloques de un AudioWorklet tienen 128 muestras: probar también sus costuras.
    let estado = {suma: 0, peso: 0};
    const salida = [];
    for (let i = 0; i < entrada.length; i += 128) {
      const resultado = remuestrearPCM16(entrada.subarray(i, i + 128), hz, estado);
      estado = resultado.estado;
      salida.push(...resultado.pcm);
    }
    assert.equal(salida.length, 16000);
    const cruces = salida.filter((v, i) => i > 0 && v > 0 && salida[i - 1] <= 0).length;
    assert.equal(cruces, 1000);
    const rms = Math.sqrt(salida.reduce((s, v) => s + (v / 32768) ** 2, 0) / salida.length);
    assert.ok(Math.abs(rms - Math.SQRT1_2 * 0.5) < 0.012, `RMS ${rms} a ${hz} Hz`);
  }
});

test('PCM16 satura y usa la escala de cliente.py; no modifica el estado recibido', () => {
  const estado = {suma: 0, peso: 0};
  const resultado = remuestrearPCM16(Float32Array.of(-2, -1, 0, 0.5, 1, 2), 16000, estado);
  assert.deepEqual([...resultado.pcm], [-32767, -32767, 0, 16383, 32767, 32767]);
  assert.deepEqual(estado, {suma: 0, peso: 0});
  assert.throws(() => remuestrearPCM16(new Float32Array(), 0), /16 kHz/);
});
