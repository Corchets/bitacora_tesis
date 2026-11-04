// @ts-check
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {citaConRoles, textoActivacionTito, limpiarCita, formatearMotivo} from '../conversacion.mjs';

test('la cita identifica roles con cualquiera de las dos personas hablando primero', () => {
  const cita = 'A: Hágame el código\\nB: Ágame el\nCódigo\nB: Pasame el código';
  for (const [a, b] of [['protegida', 'otra'], ['otra', 'protegida']]) {
    const nombres = {protegida: 'Persona protegida', otra: 'Otra persona'};
    assert.equal(citaConRoles(cita, new Map([['A', a], ['B', b]])),
      `${nombres[a]}: Hágame el código\n${nombres[b]}: Ágame el\nCódigo\n${nombres[b]}: Pasame el código`);
  }
});

test('conserva citas sin etiquetas, letras dentro del texto y hablantes desconocidos', () => {
  const roles = new Map([['A', 'otra']]);
  for (const cita of ['', 'Pasame el código', 'la opción A: ingresar', 'B: ¿Qué código?']) {
    assert.equal(citaConRoles(cita, roles), cita);
  }
});

test('citaConRoles reconoce hablantes directos PROTEGIDA, OTRA y prefijos de número', () => {
  assert.equal(citaConRoles('PROTEGIDA: Decime.'), 'Persona protegida: Decime.');
  assert.equal(citaConRoles('OTRA: Pasame el código.'), 'Otra persona: Pasame el código.');
  assert.equal(citaConRoles('3. OTRA: Pasame el código.'), 'Otra persona: Pasame el código.');

  const roles = new Map([['B', 'otra'], ['A', 'protegida']]);
  assert.equal(citaConRoles('12. B: Pasame el código.', roles), 'Otra persona: Pasame el código.');
  assert.equal(citaConRoles('1. A: Hola\n12. B: Chau', roles), 'Persona protegida: Hola\nOtra persona: Chau');

  const rolesSinB = new Map([['A', 'protegida']]);
  assert.equal(citaConRoles('12. B: Pasame el código.', rolesSinB), '12. B: Pasame el código.');
});

test('limpiarCita remueve puntuación inicial, espacios finales y prefijos de número y hablante', () => {
  assert.equal(limpiarCita('3. OTRA: Pasame el código.'), 'Pasame el código.');
  assert.equal(limpiarCita('12. B: Pasame el código.'), 'Pasame el código.');
  assert.equal(limpiarCita('PROTEGIDA: Decime.'), 'Decime.');
  assert.equal(limpiarCita('la opción A: ingresar'), 'la opción A: ingresar');
  assert.equal(limpiarCita('OTRA: Pasame el código.'), 'Pasame el código.');
  assert.equal(limpiarCita('Persona protegida: Hola.'), 'Hola.');
  assert.equal(limpiarCita('Otra persona: Chau.'), 'Chau.');
  assert.equal(limpiarCita('3. Pasame el código'), 'Pasame el código');
  assert.equal(limpiarCita('  : 3. OTRA: Pasame el código.  '), 'Pasame el código.');
  assert.equal(limpiarCita(''), '');
});

test('formatearMotivo reemplaza OTRA y PROTEGIDA respetando mayúsculas según posición', () => {
  assert.equal(formatearMotivo('OTRA te está pidiendo un código.'), 'La otra persona te está pidiendo un código.');
  assert.equal(formatearMotivo('No le pases el código a OTRA.'), 'No le pases el código a la otra persona.');
  assert.equal(formatearMotivo('OTRA pide a PROTEGIDA que transfiera.'), 'La otra persona pide a la persona protegida que transfiera.');
  assert.equal(formatearMotivo('Alerta: OTRA te pide clave. PROTEGIDA no debe transferir.'), 'Alerta: La otra persona te pide clave. La persona protegida no debe transferir.');
  assert.equal(formatearMotivo('¡OTRA está solicitando datos!'), '¡La otra persona está solicitando datos!');
  assert.equal(formatearMotivo('¿OTRA te pidió la clave?'), '¿La otra persona te pidió la clave?');
  assert.equal(formatearMotivo(''), '');
});

test('la marca de Tito solo aparece cuando la evaluación consultó al modelo', () => {
  assert.equal(textoActivacionTito({}), '');
  assert.equal(textoActivacionTito({consulta: 'omitida', tito_puntaje: 0.12}), '');
  assert.equal(textoActivacionTito({consulta: 'slm_valida', indicio_puntaje: 0.5712}), 'Tito activó al modelo · 57%');
  assert.equal(textoActivacionTito({consulta: 'slm_fallo', indicio_puntaje: 0.5}), 'Tito activó al modelo · 50%');
  assert.equal(textoActivacionTito({consulta: 'slm_valida', tito_error: 'tito_caido'}), 'Tito falló: se consulta igual');
});
