// @ts-check
import {test} from 'node:test';
import assert from 'node:assert/strict';
import {citaConRoles, textoActivacionTito} from '../conversacion.mjs';

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

test('la marca de Tito solo aparece cuando la evaluación consultó al modelo', () => {
  assert.equal(textoActivacionTito({}), '');
  assert.equal(textoActivacionTito({consulta: 'omitida', tito_puntaje: 0.12}), '');
  assert.equal(textoActivacionTito({consulta: 'slm_valida', indicio_puntaje: 0.5712}), 'Tito activó al modelo · 57%');
  assert.equal(textoActivacionTito({consulta: 'slm_fallo', indicio_puntaje: 0.5}), 'Tito activó al modelo · 50%');
  assert.equal(textoActivacionTito({consulta: 'slm_valida', tito_error: 'tito_caido'}), 'Tito falló: se consulta igual');
});
