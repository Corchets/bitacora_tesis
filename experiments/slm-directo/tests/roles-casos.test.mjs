import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const plantilla = readFileSync(new URL('../analisis/tablero/panel_plantilla.html', import.meta.url), 'utf8');
const funciones = plantilla.split('// ---------------- Casos ----------------')[1].split('const rolesElegidos')[0];
const {protegidaDelCaso, nombreEnCaso} = runInNewContext(`${funciones}; ({protegidaDelCaso, nombreEnCaso})`);

test('el atacante puede hablar primero o segundo; la elección explícita permite corregirlo', () => {
  for (const atacante of ['A', 'B']) {
    const protegida = atacante === 'A' ? 'B' : 'A';
    const caso = {clase: 'vishing', tr: 2, lineas: [[protegida, 'Hola'], [atacante, 'Pasame el código']]};
    assert.equal(protegidaDelCaso(caso), protegida);
    assert.equal(nombreEnCaso(caso, atacante, protegida), 'Atacante');
    assert.equal(nombreEnCaso(caso, protegida, protegida), 'Persona protegida');
    assert.equal(protegidaDelCaso(caso, atacante), atacante);
  }
});

test('sin pedido no inventa roles y una legítima nunca tiene atacante', () => {
  for (const clase of ['vishing', 'legitima', 'legitima_dificil']) {
    const caso = {clase, tr: null, lineas: [['A', 'Hola'], ['B', 'Buen día']]};
    assert.equal(protegidaDelCaso(caso), '');
    assert.equal(nombreEnCaso(caso, 'A', ''), 'Primera persona');
    assert.equal(nombreEnCaso(caso, 'B', ''), 'Segunda persona');
    assert.equal(protegidaDelCaso(caso, 'B'), 'B');
    assert.equal(nombreEnCaso(caso, 'B', 'B'), 'Persona protegida');
    assert.equal(nombreEnCaso(caso, 'A', 'B'), clase === 'vishing' ? 'Atacante' : 'Otra persona');
  }
});
