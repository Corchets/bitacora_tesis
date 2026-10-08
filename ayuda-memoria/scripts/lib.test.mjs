import test from 'node:test';
import assert from 'node:assert/strict';
import { hash, section, table, decisions, enrichBrief, fingerprint } from './lib.mjs';

test('un brief pierde vigencia al cambiar issue, documentos o bloqueos', () => {
  const issue = { number: 50, title: 'Reglas', body: 'Contrato', updatedAt: '2026-10-07', milestone: 3, assignees: [], labels: [] };
  const blockers = [{ number: 20, title: 'Revisar', state: 'closed' }];
  const documents = { 'docs/ejemplo.md': { hash: hash('v1') } };
  const brief = { sources: [{ path: 'docs/ejemplo.md', why: 'Contrato' }] };
  brief.review = { fingerprint: fingerprint(issue, blockers, brief.sources, documents) };
  assert.equal(enrichBrief(brief, issue, blockers, documents).status, 'reviewed');
  assert.equal(enrichBrief(brief, { ...issue, body: 'Nuevo contrato' }, blockers, documents).status, 'stale');
  assert.equal(enrichBrief(brief, issue, [{ ...blockers[0], state: 'open' }], documents).status, 'stale');
  assert.equal(enrichBrief(brief, issue, blockers, { 'docs/ejemplo.md': { hash: hash('v2') } }).status, 'stale');
  assert.equal(enrichBrief(brief, issue, blockers, {}).status, 'missing-source');
  assert.equal(enrichBrief(undefined, issue, blockers, documents).status, 'missing');
});
test('extrae contratos sin absorber secciones siguientes ni perder subtítulos', () => {
  const body = '### Resultado observable\nUn comando.\n#### Detalle\nIncremental.\n### Terminado cuando\n- [ ] Repetible.';
  assert.equal(section(body, /Resultado observable/), 'Un comando.\n#### Detalle\nIncremental.');
  assert.equal(section(body, /Terminado cuando/), '- [ ] Repetible.');
});
test('respeta pipes escapados en tablas y propuestas de decisiones abiertas', () => {
  assert.deepEqual(table('| Término | Definición |\n|---|---|\n| A | X\\|Y |'), [['A', 'X|Y']]);
  const rows = decisions('### D07 — Taxonomía\n- **Estado:** abierta.\n\n### D09 — Modelos\n- **Estado:** resuelto (2026-10-07).\n');
  assert.equal(rows.length, 2);
  assert.equal(rows[0].open, true);
  assert.equal(rows[1].open, false);
});
