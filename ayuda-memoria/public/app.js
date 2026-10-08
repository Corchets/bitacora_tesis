const app = document.querySelector('#app');
const main = document.querySelector('main');
let data;
const params = new URLSearchParams(location.search);
const views = ['ahora', 'roadmap', 'issues', 'glosario'];
let view = views.includes(params.get('vista')) ? params.get('vista') : 'ahora';
let branchName = params.get('rama') === 'main' ? 'main' : 'laboratorio-main';
let selected = Number(params.get('issue')) || null;
let milestoneFilter = params.get('hito') || 'all';
let search = '';
let glossarySearch = '';
let selectedGraphId = null;
let roadmapMode = null;
let frontFilter = 'all';
let onlyAvailable = false;
let focusNext = false;
let cy = null;
let cyModule = null;
const escape = text => String(text ?? '').replace(/[&<>"']/g, char => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[char]));
const plain = text => String(text ?? '').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[*`]/g, '').replace(/^>\s?/gm, '').trim();
const repo = 'https://github.com/Corchets/bitacora_tesis';
const date = value => {
  if (!value) return 'Sin fecha';
  const parts = Object.fromEntries(new Intl.DateTimeFormat('es-AR', { day:'2-digit', month:'2-digit', year:'numeric', timeZone:'America/Argentina/Tucuman' }).formatToParts(new Date(value)).map(part => [part.type, part.value]));
  return `${parts.year}-${parts.month}-${parts.day}`;
};
// GitHub milestone due dates are calendar dates at midnight UTC, not local events.
const dueDate = value => value ? value.slice(0,10) : 'Sin fecha';
const fullDate = value => `${date(value)} · ${new Intl.DateTimeFormat('es-AR', { hour:'2-digit', minute:'2-digit', hourCycle:'h23', timeZone:'America/Argentina/Tucuman' }).format(new Date(value))}`;
const branch = () => data.branches.find(item => item.name === branchName);
const currentMilestone = () => data.milestones.find(item => item.state === 'open' && item.open > 0);
const blockers = issue => (data.dependencies[issue.number] ?? []).filter(item => item.state === 'open');
const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;
const iconArrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>';
const externalIcon = '<svg class="external-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>';
function link(url, label, className = '') { return `<a href="${escape(url)}" class="${className}" target="_blank" rel="noopener noreferrer">${escape(label)} ${externalIcon}</a>`; }
function ilink(url, label) { return `<a href="${escape(url)}" class="d-iss-link">${escape(label)} →</a>`; }
function rich(text, documentPath) {
  // Source Markdown is rendered as text plus safe links, never as raw HTML.
  const doc = branch()?.documents[documentPath];
  let result = escape(text);
  result = result.replace(/\[([^\]]+)\]\(([^)]+)\)/g, (_, label, href) => {
    let url;
    try {
      const raw = href.replace(/&amp;/g, '&');
      if (raw.startsWith('https://')) url = new URL(raw);
      else if (doc && !/^[a-z]+:/i.test(raw) && !raw.startsWith('//')) url = new URL(raw, doc.url);
      else return label;
      if (url.protocol !== 'https:') return label;
    } catch { return label; }
    return `<a href="${escape(url.href)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  });
  result = result.replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
  return result;
}
function paragraphs(text) {
  return String(text ?? '').split(/\n\s*\n/).filter(Boolean).map(part => `<p>${escape(plain(part)).replace(/\n/g, '<br>')}</p>`).join('');
}
function urlState() {
  const url = new URL(location.href);
  url.search = '';
  url.searchParams.set('rama', branchName);
  if (view !== 'ahora') url.searchParams.set('vista', view);
  if (selected && ['ahora','issues'].includes(view)) url.searchParams.set('issue', selected);
  if (milestoneFilter !== 'all' && view === 'issues') url.searchParams.set('hito', milestoneFilter);
  if (view === 'roadmap' && roadmapMode === 'lista') url.searchParams.set('modo', 'lista');
  if (view === 'roadmap' && selectedGraphId) url.searchParams.set('nodo', selectedGraphId);
  history.replaceState(null, '', url);
}
function heading(title, description, action = '') {
  return `<div class="page-heading"><div><h1>${title}</h1><p>${description}</p></div>${action}</div>`;
}
function branchNotice() {
  if (branchName !== 'laboratorio-main') return '';
  return `<div class="branch-note"><span class="branch-dot" aria-hidden="true"></span><p>Estás viendo las fuentes de <strong>laboratorio-main</strong>. Los issues son el backlog actual compartido; la documentación de esta rama puede diferir de Main.</p></div>`;
}
function phaseRail() {
  const current = currentMilestone();
  return `<div class="phase-rail" aria-label="Hitos del proyecto">${data.milestones.filter(item => item.state === 'open').map(item => {
    const [code, name] = item.title.split(' — ');
    return `<button class="phase ${item.number === current?.number ? 'current' : ''}" data-phase="${item.number}" aria-label="${escape(item.title)}, ${item.open} issues abiertos"><span class="phase-mark">${escape(code)}</span><span class="phase-name">${escape(name ?? item.title)}</span><span class="phase-count">${item.open} abiertos · ${item.closed} cerrados</span></button>`;
  }).join('')}</div>`;
}
function briefStatus(brief) {
  return ({ reviewed:'Brief revisado', stale:'Revisar brief', 'missing-source':'Fuente pendiente', missing:'Brief pendiente' })[brief?.status] ?? 'Brief pendiente';
}
function issueRow(issue) {
  const pending = blockers(issue);
  const brief = branch().briefs[issue.number];
  return `<button class="issue-row ${selected === issue.number ? 'selected' : ''}" data-issue="${issue.number}" aria-pressed="${selected === issue.number}">
    <span class="issue-number">#${issue.number}</span><span class="issue-info"><strong>${escape(issue.title)}</strong><span class="issue-meta"><span class="status ${pending.length ? 'blocked' : 'ready'}">${pending.length ? `Espera ${pending.map(item => `#${item.number}`).join(', ')}` : 'Sin bloqueos abiertos'}</span><span>${escape(issue.assignees.join(', ') || 'Sin responsable')}</span></span></span>
    <span class="issue-end"><span class="brief-tag ${brief.status === 'reviewed' ? 'reviewed' : ''}">${briefStatus(brief)}</span>${iconArrow}</span>
  </button>`;
}
function documentSources(brief) {
  return `<ol class="source-list">${brief.sources.map(source => {
    const doc = branch().documents[source.path];
    return `<li>${doc ? link(`${doc.url}${source.anchor ? `#${source.anchor}` : ''}`, source.label ?? source.path.split('/').at(-1)) : `<span class="missing-link">${escape(source.path)} · no existe en esta rama</span>`}<p>${escape(source.why)}</p></li>`;
  }).join('')}</ol>`;
}
function issueDetail(issue) {
  if (!issue) return `<aside class="detail-pane empty-detail"><h2>Elegí un issue</h2><p>Acá aparece el contexto para empezar, sin perder tu lugar en el mapa.</p></aside>`;
  const brief = branch().briefs[issue.number];
  const pending = blockers(issue);
  const reviewed = brief.status === 'reviewed';
  const rawDone = issue.done.split('\n').filter(line => /^\s*- \[[ xX]\]/.test(line));
  return `<aside class="detail-pane" id="brief-panel" aria-labelledby="detail-title">
    <h2 id="detail-title">#${issue.number} · ${escape(issue.title)}</h2>
    <div class="detail-top">${link(issue.url, 'Ver en GitHub')}</div>
    <div class="brief-state ${reviewed ? 'fresh' : 'pending'}">${briefStatus(brief)}${reviewed ? `<span>Revisado el ${date(brief.review.at)}</span>` : `<span>${brief.status === 'stale' ? 'Cambió el issue o una de sus fuentes. La orientación anterior espera una nueva revisión.' : brief.status === 'missing-source' ? 'Una fuente del brief no está disponible en esta rama. Consultá el contrato del issue.' : 'Todavía no tiene una orientación revisada para esta rama. Consultá el contrato del issue.'}</span>`}</div>
    ${pending.length ? `<div class="blocker-note"><strong>Antes de ejecutar, resolver ${pending.map(item => link(item.url, `#${item.number}`)).join(', ')}.</strong><p>Podés recuperar contexto mientras tanto. El brief no habilita saltar estas dependencias.</p></div>` : ''}
    <section class="brief-section"><h3>Qué vas a lograr</h3>${paragraphs(reviewed ? brief.goal : issue.goal || 'El resultado se consulta en el issue original.')}</section>
    ${reviewed ? `<section class="brief-section"><h3>Para entrar en contexto</h3>${documentSources(brief)}</section><section class="brief-section start-section"><h3>Tu primer paso</h3>${paragraphs(brief.start)}</section><section class="brief-section"><h3>Cómo saber que terminaste</h3>${paragraphs(brief.done)}</section>` : `<section class="brief-section"><h3>Contexto del issue</h3>${paragraphs(issue.context || 'El issue no explicita contexto en una sección reconocible. Abrilo en GitHub para revisar el contrato completo.')}</section><section class="brief-section"><h3>Para empezar</h3><p>Revisá el issue completo y sus dependencias. La skill <code>$actualizar-ayuda-memoria</code> puede preparar o revisar este brief.</p>${brief.sources.length ? documentSources(brief) : ''}</section><section class="brief-section"><h3>El issue está terminado cuando…</h3>${rawDone.length ? `<ul class="criteria">${rawDone.map(line => `<li>${escape(plain(line.replace(/^\s*- \[[ xX]\]\s*/, '')))}</li>`).join('')}</ul>` : paragraphs(issue.done || 'Consultá los criterios en GitHub.')}</section>`}
    <div class="detail-bottom"><p>La asignación, los bloqueos y el cierre se gestionan en GitHub.</p>${link(issue.url, 'Abrir issue completo', 'text-action')}</div>
  </aside>`;
}
function workView(now) {
  const current = currentMilestone();
  let visible = data.issues.filter(issue => !now || issue.milestone === current?.number);
  if (!now && milestoneFilter !== 'all') visible = visible.filter(issue => String(issue.milestone ?? 'none') === milestoneFilter);
  const query = search.toLocaleLowerCase('es-AR');
  visible = visible.filter(issue => `${issue.number} ${issue.title} ${issue.assignees.join(' ')}`.toLocaleLowerCase('es-AR').includes(query));
  visible.sort((a,b) => blockers(a).length - blockers(b).length || a.number - b.number);
  if (!visible.some(issue => issue.number === selected)) selected = visible[0]?.number ?? null;
  const groups = now ? [{ title:'Issues del hito actual', items:visible }] : [...data.milestones.map(item => ({ title:item.title, items:visible.filter(issue => issue.milestone === item.number) })), { title:'Sin hito asignado', items:visible.filter(issue => !issue.milestone) }].filter(group => group.items.length);
  const currentName = current?.title.split(' — ')[1] ?? 'No hay un hito con issues abiertos';
  return heading(now ? 'Volvé a tomar el hilo.' : 'Encontrá tu próximo issue.', now ? 'Ubicate en el proyecto, elegí un issue y recuperá el contexto para empezar.' : 'El backlog de GitHub, agrupado por hito y con una entrada al contexto.')
    + branchNotice() + (now ? phaseRail() + `<section class="current-stage"><div><h2>${escape(currentName)}</h2><p>${escape(current?.description.split('. La documentación')[0] ?? 'Consultá el estado de los hitos en GitHub.')}</p></div><div class="stage-date"><span>Referencia del hito</span><strong>${dueDate(current?.dueAt)}</strong><span>Fecha orientativa</span></div></section>` : '')
    + `<div class="work-layout"><section class="issues-pane" aria-label="Elegir un issue"><div class="issues-toolbar"><label class="search-box"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input id="issue-search" type="search" placeholder="Buscar issue, número o responsable" aria-label="Buscar issues" value="${escape(search)}"></label>${!now ? `<label class="filter-label"><span class="sr-only">Filtrar por hito</span><select id="milestone-filter"><option value="all">Todos los hitos</option>${data.milestones.map(item => `<option value="${item.number}" ${milestoneFilter === String(item.number) ? 'selected' : ''}>${escape(item.title)}</option>`).join('')}<option value="none" ${milestoneFilter === 'none' ? 'selected' : ''}>Sin hito</option></select></label>` : ''}</div><div class="issue-results" aria-live="polite">${visible.length ? groups.map(group => `<div class="issue-group"><div class="group-heading"><h2>${escape(group.title)}</h2><span>${group.items.length} ${group.items.length === 1 ? 'issue' : 'issues'}</span></div>${group.items.map(issueRow).join('')}</div>`).join('') : `<div class="empty"><h2>${search ? 'No encontramos ese issue.' : 'No hay issues abiertos acá.'}</h2><p>${search ? 'Probá otro término, número o responsable.' : 'Podés consultar otros hitos desde Todos los issues.'}</p></div>`}</div></section>${issueDetail(visible.find(issue => issue.number === selected))}</div>`;
}

// ---------- Roadmap: grafo interactivo de entregas ----------
// Las aristas salen de las dependencias nativas de GitHub (data.roadmap.graph);
// roadmap.json aporta la orientación editorial (frentes, próximos pasos, laboratorio).
const FRONT_COLORS = { corpus:'#365b35', deteccion:'#203e37', metodologia:'#5a6a62', cierre:'#9fae9e', concluido:'#427345', laboratorio:'#ad452b' };
const FRONT_BG = { corpus:'#eef3e2', deteccion:'#e9efe4', metodologia:'#f1f4ec', cierre:'#f6f9f3', concluido:'#e8eddb', laboratorio:'#faf3ed' };
const rm = () => data.roadmap;
const graphNode = id => rm().graph?.nodes.find(n => n.id === id);
const nextActionIds = () => new Set((rm().currentLocation.nextActions ?? []).map(a => `i${a.issue}`));
const milestoneCode = num => data.milestones.find(m => m.number === num)?.title.split(' — ')[0] ?? null;

function graphFronts() {
  const fronts = [...rm().parallelFronts];
  if (rm().concludedContext) fronts.push({ ...rm().concludedContext, concluded: true, state: 'done',
    issues: (rm().graph?.nodes ?? []).filter(n => n.front === 'concluido').map(n => n.number) });
  const sf = rm().suspendedFront;
  if (sf) fronts.push({ id: 'laboratorio', name: 'Laboratorio (pausado)', tag: sf.tag, state: 'pausado',
    stateLabel: sf.stateLabel, paused: true, issues: (sf.issues ?? []).map(i => i.number) });
  return fronts;
}
function nodeStatus(n) {
  if (n.kind === 'paused') return { label: 'Pausado (conservado)', cls: 'status-paused' };
  if (n.state === 'closed') return n.stateReason === 'not_planned'
    ? { label: 'Cerrado sin hacer', cls: 'status-paused' }
    : { label: 'Completado', cls: 'status-done' };
  if (n.state === 'open') {
    if (n.openBlockers.length) return { label: `Espera ${n.openBlockers.map(num => `#${num}`).join(', ')}`, cls: 'status-espera' };
    if (n.conditions?.length) return { label: 'Disponible con condición', cls: 'status-espera' };
    return { label: 'Disponible', cls: 'status-disponible' };
  }
  return { label: 'Sin verificar', cls: 'status-espera' };
}
function nodeClasses(n) {
  const cls = [`front-${n.front}`];
  if (n.kind === 'paused') cls.push('is-paused');
  else if (n.state === 'closed') cls.push(n.stateReason === 'not_planned' ? 'is-notplanned' : 'is-done');
  else if (n.state !== 'open') cls.push('is-unknown');
  else cls.push(n.openBlockers.length ? 'is-blocked' : (n.conditions?.length ? 'is-conditional' : 'is-free'));
  if (nextActionIds().has(n.id)) cls.push('is-next');
  return cls.join(' ');
}
function shortTitle(title) {
  if (title.length <= 42) return title;
  const cut = title.slice(0, 42);
  return `${cut.slice(0, cut.lastIndexOf(' '))}…`;
}
function cyStyle() {
  const frontRules = Object.entries(FRONT_COLORS).map(([id, color]) => (
    { selector: `node:parent.front-${id}`, style: { 'background-color': FRONT_BG[id], 'border-color': color } }
  ));
  return [
    { selector: 'node', style: {
      'font-family': 'Manrope, sans-serif', 'font-size': 12.5, 'font-weight': 700, 'color': '#203e37',
      'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': '170px', 'text-valign': 'bottom', 'text-margin-y': 7,
      'text-line-height': 1.3, 'text-background-color': '#fffef9', 'text-background-opacity': 0.9,
      'text-background-padding': '2.5px', 'text-background-shape': 'roundrectangle',
      'width': 34, 'height': 34, 'border-width': 2.2, 'border-color': '#203e37', 'background-color': '#fffef9',
      'overlay-opacity': 0
    }},
    { selector: 'node:parent', style: {
      'label': 'data(label)', 'text-valign': 'top', 'text-halign': 'center', 'text-margin-y': -10,
      'font-size': 10, 'font-weight': 800, 'color': '#5a6a62', 'text-background-opacity': 0,
      'background-opacity': 0.55, 'border-width': 1.4, 'border-style': 'solid', 'border-color': '#c8d5c0',
      'padding': 18, 'shape': 'round-rectangle', 'text-wrap': 'wrap', 'text-max-width': '230px', 'min-zoomed-font-size': 8
    }},
    ...frontRules,
    { selector: 'node:parent.front-laboratorio', style: { 'border-style': 'dashed', 'border-width': 1.8, 'color': '#76331f' } },
    { selector: 'node.is-done', style: { 'background-color': '#427345', 'border-color': '#365b35' } },
    { selector: 'node.is-notplanned', style: { 'background-color': '#f9ece1', 'border-color': '#ad452b', 'border-style': 'dashed' } },
    { selector: 'node.is-unknown', style: { 'background-color': '#fffef9', 'border-color': '#9fae9e', 'border-style': 'dashed' } },
    { selector: 'node.is-free', style: { 'background-color': '#fffef9', 'border-color': '#203e37' } },
    { selector: 'node.is-conditional', style: { 'background-color': '#fffef9', 'border-color': '#ad452b', 'border-style': 'dashed' } },
    { selector: 'node.is-blocked', style: { 'background-color': '#f9ece1', 'border-color': '#ad452b', 'border-width': 2.4 } },
    { selector: 'node.is-next', style: { 'underlay-color': '#d7e9af', 'underlay-opacity': 0.95, 'underlay-padding': 9, 'underlay-shape': 'ellipse' } },
    { selector: 'node.is-paused', style: { 'background-color': '#f9ece1', 'border-color': '#ad452b', 'border-style': 'dashed', 'shape': 'round-rectangle', 'width': 56, 'height': 38 } },
    { selector: 'edge', style: {
      'width': 1.8, 'line-color': '#9fae9e', 'curve-style': 'bezier',
      'target-arrow-shape': 'triangle', 'target-arrow-color': '#9fae9e', 'arrow-scale': 1.05,
      'font-size': 9, 'color': '#5a6a62'
    }},
    { selector: 'edge.edge-pending', style: { 'line-color': '#ad452b', 'target-arrow-color': '#ad452b', 'width': 2.4 } },
    { selector: 'edge.edge-satisfied', style: { 'line-color': '#427345', 'target-arrow-color': '#427345', 'width': 1.7 } },
    { selector: 'edge.edge-not_planned', style: { 'line-color': '#b9a99c', 'target-arrow-color': '#b9a99c', 'line-style': 'dashed' } },
    { selector: 'edge.edge-unknown', style: { 'line-color': '#9fae9e', 'target-arrow-color': '#9fae9e', 'line-style': 'dashed' } },
    { selector: 'edge.edge-conditional', style: { 'line-color': '#ad452b', 'target-arrow-color': '#ad452b', 'line-style': 'dashed', 'width': 1.7, 'line-dash-pattern': [6,4],
      'label': 'data(note)', 'font-size': 9.5, 'font-weight': 700, 'color': '#76331f', 'text-wrap': 'wrap', 'text-max-width': '160px',
      'text-background-color': '#fffef9', 'text-background-opacity': 0.9, 'text-background-padding': '3px', 'text-background-shape': 'roundrectangle', 'text-margin-y': -10 } },
    { selector: 'node.sel', style: { 'border-color': '#203e37', 'border-width': 3.4, 'overlay-color': '#d7e9af', 'overlay-opacity': 0.4, 'overlay-padding': 7 } },
    { selector: 'edge.dep-in', style: { 'line-color': '#ad452b', 'target-arrow-color': '#ad452b', 'width': 3 } },
    { selector: 'node.dep-in', style: { 'border-color': '#ad452b', 'border-width': 3 } },
    { selector: 'edge.dep-out', style: { 'line-color': '#365b35', 'target-arrow-color': '#365b35', 'width': 3 } },
    { selector: 'node.dep-out', style: { 'border-color': '#365b35', 'border-width': 3 } },
    { selector: '.dimmed', style: { 'opacity': 0.2 } },
    { selector: '.focus-dim', style: { 'opacity': 0.15 } },
    { selector: '.f-hidden', style: { 'display': 'none' } }
  ];
}
// Carriles: cada frente es una columna y las dependencias reales fluyen de
// izquierda a derecha. El laboratorio queda separado y debajo: está pausado y
// nunca bloquea. Posiciones fijas (sin simulación), ordenadas por profundidad.
const LANE_ORDER = ['concluido', 'corpus', 'deteccion', 'metodologia', 'cierre'];
const LANE_X = 236, NODE_Y = 118;
function graphDepths(g) {
  const preds = {};
  for (const e of g.edges) if (e.kind === 'dependency') (preds[e.target] ??= []).push(e.source);
  const memo = {};
  const visit = (id, seen) => {
    if (id in memo) return memo[id];
    if (seen.has(id)) return 0;
    return memo[id] = preds[id]?.length ? 1 + Math.max(...preds[id].map(p => visit(p, new Set([...seen, id])))) : 0;
  };
  for (const n of g.nodes) visit(n.id, new Set());
  return memo;
}
function graphPositions(g) {
  const depth = graphDepths(g);
  const lanes = new Map();
  for (const n of g.nodes) {
    const lane = LANE_ORDER.includes(n.front) ? n.front : n.front === 'laboratorio' ? 'laboratorio' : 'concluido';
    if (!lanes.has(lane)) lanes.set(lane, []);
    lanes.get(lane).push(n);
  }
  const pos = {};
  let bottom = 0;
  for (const lane of LANE_ORDER) {
    const list = lanes.get(lane) ?? [];
    list.sort((a, b) => (depth[a.id] - depth[b.id]) || (a.number - b.number));
    const x = LANE_ORDER.indexOf(lane) * LANE_X;
    list.forEach((n, i) => { pos[n.id] = { x, y: i * NODE_Y }; });
    bottom = Math.max(bottom, list.length * NODE_Y);
  }
  (lanes.get('laboratorio') ?? []).forEach((n, i) => { pos[n.id] = { x: 2 * LANE_X + i * 110, y: bottom + 96 }; });
  return pos;
}
const edgeNoteKey = (src, dst) => `${String(src).replace(/^i/, '')}>${String(dst).replace(/^i/, '')}`;
async function initCy() {
  if (cy || roadmapMode === 'lista') return;
  const container = document.querySelector('#cy-roadmap');
  if (!container || !rm().graph) return;
  if (!cyModule) {
    try { cyModule = (await import('./cytoscape.esm.min.js')).default; }
    catch { document.querySelector('.cy-fallback')?.removeAttribute('hidden'); return; }
  }
  try { await Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 700))]); } catch { /* Manrope puede tardar; el fallback sigue legible. */ }
  const g = rm().graph;
  const pos = graphPositions(g);
  const notes = g.edgeNotes ?? {};
  const elements = [];
  for (const f of graphFronts()) {
    elements.push({ group: 'nodes', selectable: true, grabbable: false,
      data: { id: `frente-${f.id}`, kind: 'front', label: f.name, frontId: f.id },
      classes: `front-${f.id}` });
  }
  for (const n of g.nodes) {
    elements.push({ group: 'nodes', position: pos[n.id],
      data: { id: n.id, parent: `frente-${n.front}`, front: n.front, kind: n.kind,
        state: n.state, blocked: n.openBlockers.length > 0, conditional: (n.conditions?.length ?? 0) > 0,
        label: n.kind === 'paused' ? `Laboratorio\n${n.issueCount} issues en pausa` : `#${n.number}\n${shortTitle(n.title)}` },
      classes: nodeClasses(n) });
  }
  for (const e of g.edges) elements.push({ group: 'edges',
    data: { id: e.id, source: e.source, target: e.target, note: notes[edgeNoteKey(e.source, e.target)] ?? '' },
    classes: `edge-${e.state}` });
  cy = cyModule({
    container, elements, style: cyStyle(),
    wheelSensitivity: 1.5, minZoom: 0.25, maxZoom: 2.8,
    layout: { name: 'preset', fit: false, animate: false }
  });
  cy.on('tap', 'node', event => selectGraph(event.target.id()));
  cy.on('tap', event => { if (event.target === cy) clearGraphSelection(); });
  applyGraphFilters();
  applyFocus();
  updateGraphSelection();
  cy.fit(cy.elements().not('.f-hidden'), 36);
}
function nodeHiddenByFilter(n) {
  if (n.isParent()) return frontFilter !== 'all' && n.data('frontId') !== frontFilter;
  if (frontFilter !== 'all' && n.data('front') !== frontFilter) return true;
  if (onlyAvailable && !(n.data('state') === 'open' && !n.data('blocked') && !n.data('conditional'))) return true;
  return false;
}
function applyGraphFilters() {
  if (cy) {
    cy.batch(() => {
      cy.elements().removeClass('f-hidden');
      cy.nodes().filter(nodeHiddenByFilter).addClass('f-hidden');
      cy.nodes().filter(n => n.isParent() && !n.hasClass('f-hidden') && n.descendants().not('.f-hidden').length === 0).addClass('f-hidden');
      cy.edges().filter(e => e.source().hasClass('f-hidden') || e.target().hasClass('f-hidden')).addClass('f-hidden');
    });
  }
  renderRoadmapList();
}
function applyFocus() {
  if (!cy) return;
  cy.batch(() => {
    cy.elements().removeClass('focus-dim');
    if (!focusNext) return;
    const ids = nextActionIds();
    const keep = cy.nodes().filter(n => ids.has(n.id()) || n.isParent());
    const keepEdges = cy.edges().filter(e => ids.has(e.source().id()) || ids.has(e.target().id()));
    cy.elements().difference(keep.union(keepEdges)).addClass('focus-dim');
  });
}
function updateGraphSelection() {
  if (cy) {
    cy.elements().removeClass('sel dep-in dep-out dimmed');
    const ele = selectedGraphId ? cy.getElementById(selectedGraphId) : null;
    if (ele?.length) {
      ele.addClass('sel');
      if (ele.isParent()) {
        ele.union(ele.descendants()).removeClass('focus-dim');
        ele.descendants().addClass('dep-out');
        cy.nodes().filter(n => !n.isParent() && n.data('front') !== ele.data('frontId')).addClass('dimmed');
      } else {
        const incoming = ele.predecessors().filter(el => !el.isParent());
        const outgoing = ele.successors().filter(el => !el.isParent());
        incoming.addClass('dep-in');
        outgoing.addClass('dep-out');
        ele.union(incoming).union(outgoing).removeClass('focus-dim');
        cy.nodes().filter(n => !n.isParent() && n !== ele && !incoming.contains(n) && !outgoing.contains(n)).addClass('dimmed');
        cy.edges().filter(e => !incoming.contains(e) && !outgoing.contains(e)).addClass('dimmed');
      }
    }
  }
  document.querySelectorAll('[data-graph-id]').forEach(btn => {
    const on = btn.dataset.graphId === selectedGraphId;
    btn.classList.toggle('is-selected', on);
    if (btn.classList.contains('rl-node')) btn.setAttribute('aria-pressed', on);
  });
  renderRoadmapPanel();
  urlState();
}
function selectGraph(id) {
  selectedGraphId = id;
  const ele = cy?.getElementById(id);
  if (ele?.length && ele.hasClass('f-hidden')) {
    frontFilter = 'all'; onlyAvailable = false;
    const sel = document.querySelector('#rm-front-filter'); if (sel) sel.value = 'all';
    const chk = document.querySelector('#rm-available'); if (chk) chk.checked = false;
    applyGraphFilters();
  }
  updateGraphSelection();
}
function clearGraphSelection() { selectedGraphId = null; updateGraphSelection(); }
function setRoadmapMode(mode) {
  roadmapMode = mode;
  document.querySelector('.spatial-roadmap')?.classList.toggle('mode-lista', mode === 'lista');
  document.querySelectorAll('[data-rm-mode]').forEach(btn => btn.setAttribute('aria-pressed', String(btn.dataset.rmMode === mode)));
  if (mode === 'mapa') { initCy(); requestAnimationFrame(() => cy?.resize()); }
  urlState();
}
function handleRmAction(action) {
  if (action === 'focus-next') {
    focusNext = !focusNext;
    document.querySelector('[data-rm-action="focus-next"]')?.setAttribute('aria-pressed', String(focusNext));
    applyFocus();
    return;
  }
  if (action === 'clear') { clearGraphSelection(); return; }
  if (!cy) return;
  const rect = cy.container().getBoundingClientRect();
  const center = { x: rect.width / 2, y: rect.height / 2 };
  if (action === 'zoom-in') cy.zoom({ level: cy.zoom() * 1.3, renderedPosition: center });
  if (action === 'zoom-out') cy.zoom({ level: cy.zoom() / 1.3, renderedPosition: center });
  if (action === 'fit') cy.fit(cy.elements().not('.f-hidden'), 36);
  if (action === 'reset') {
    frontFilter = 'all'; onlyAvailable = false; focusNext = false;
    selectedGraphId = null;
    const sel = document.querySelector('#rm-front-filter'); if (sel) sel.value = 'all';
    const chk = document.querySelector('#rm-available'); if (chk) chk.checked = false;
    document.querySelector('[data-rm-action="focus-next"]')?.setAttribute('aria-pressed', 'false');
    applyGraphFilters();
    applyFocus();
    cy.fit(cy.elements().not('.f-hidden'), 36);
    updateGraphSelection();
  }
}
function renderRoadmapList() {
  const container = document.querySelector('#rm-list');
  if (container) container.innerHTML = roadmapListHTML();
}
function renderRoadmapPanel() {
  const container = document.querySelector('#rm-panel-body');
  if (container) container.innerHTML = roadmapPanelHTML();
  document.querySelector('.rm-panel')?.classList.toggle('has-sel', !!selectedGraphId);
}
function roadmapListHTML() {
  const groups = graphFronts().filter(f => frontFilter === 'all' || f.id === frontFilter);
  return groups.map(f => {
    const nodes = (rm().graph?.nodes ?? []).filter(n => n.front === f.id)
      .filter(n => !onlyAvailable || (n.state === 'open' && n.openBlockers.length === 0 && !(n.conditions?.length)));
    return `<section class="rl-front rl-front-${f.id}">
      <h3><span class="rl-dot" aria-hidden="true" style="background:${FRONT_COLORS[f.id] ?? '#5a6a62'}"></span>${escape(f.name)}<span class="rl-state">${escape(f.stateLabel ?? '')}</span></h3>
      ${nodes.length ? `<ul class="rl-items">${nodes.map(n => {
        const st = nodeStatus(n);
        return `<li><button type="button" class="rl-node ${selectedGraphId === n.id ? 'is-selected' : ''}" data-graph-id="${n.id}" aria-pressed="${selectedGraphId === n.id}">
          <span class="rl-num">${n.kind === 'paused' ? 'LAB' : `#${n.number}`}</span>
          <span class="rl-title">${escape(n.title)}</span>
          ${n.milestone ? `<span class="rl-ms">${escape(milestoneCode(n.milestone) ?? '')}</span>` : ''}
          <span class="rl-pill ${st.cls}">${escape(st.label)}</span>
        </button></li>`;
      }).join('')}</ul>` : '<p class="rl-empty">Sin entregas con este filtro.</p>'}
    </section>`;
  }).join('');
}
function panelHeader(tag, title, pill) {
  return `<header class="drawer-header">
    <div class="drawer-header-top">
      <span class="drawer-tag">${escape(tag)}</span>
      <button type="button" class="drawer-close-btn" data-rm-action="clear" aria-label="Limpiar selección y cerrar detalle">✕ <kbd>Esc</kbd></button>
    </div>
    <div class="drawer-title-row"><h2>${title}</h2>${pill}</div>
  </header>`;
}
function depEdgeList(ids, emptyText, noteFor) {
  if (!ids.length) return `<p class="rm-rel-empty">${escape(emptyText)}</p>`;
  return `<ul class="rm-rel-list">${ids.map(id => {
    const n = graphNode(id);
    if (!n) return '';
    const st = nodeStatus(n);
    const num = n.kind === 'paused' ? 'LAB' : `#${n.number}`;
    const note = noteFor?.(n);
    return `<li><button type="button" class="rm-rel-btn" data-graph-id="${n.id}"><span class="rl-num">${num}</span><span class="rl-title">${escape(n.title)}</span><span class="rl-pill ${st.cls}">${escape(st.label)}</span></button>${note ? `<p class="rm-edge-note">${escape(note)}</p>` : ''}</li>`;
  }).join('')}</ul>`;
}
/* Vínculos del roadmap hacia la vista de arquitectura (PR #58): la
 * correspondencia issue→componentes/decisiones es editorial y vive en
 * roadmap.json > archComponents. */
function archLinksHTML(num) {
  const meta = (rm().archComponents || {})[num];
  if (!meta || (!(meta.components || []).length && !(meta.decisions || []).length && !meta.section)) return '';
  const parts = [];
  for (const c of meta.components || []) parts.push(ilink(`/arquitectura/?c=${encodeURIComponent(c)}`, `componente ${c}`));
  for (const d of meta.decisions || []) parts.push(ilink(`/arquitectura/?d=${encodeURIComponent(d)}`, `decisión ${d}`));
  if (meta.section) parts.push(ilink(`/arquitectura/#${encodeURIComponent(meta.section)}`, 'sección del visor'));
  return `<div class="drawer-reading-box"><span class="callout-label">En arquitectura</span><div class="rm-arch-links">${parts.join(' ')}</div></div>`;
}
function issueNodeDetailHTML(n) {
  const issue = data.issues.find(i => i.number === n.number);
  const brief = branch().briefs[n.number];
  const reviewed = brief?.status === 'reviewed';
  const st = nodeStatus(n);
  const front = graphFronts().find(f => f.id === n.front);
  const edges = rm().graph?.edges ?? [];
  const incoming = edges.filter(e => e.target === n.id);
  const pending = incoming.filter(e => e.state === 'pending').map(e => e.source);
  const doneDeps = incoming.filter(e => e.state === 'satisfied').map(e => e.source);
  const unknownDeps = incoming.filter(e => e.state === 'unknown' || e.state === 'not_planned').map(e => e.source);
  const unlocks = edges.filter(e => e.source === n.id && e.kind === 'dependency').map(e => e.target);
  const conditional = edges.filter(e => e.source === n.id && e.kind === 'conditional').map(e => e.target);
  const notes = rm().graph?.edgeNotes ?? {};
  const keyOf = other => other.kind === 'paused' ? 'laboratorio' : String(other.number);
  const inNote = id => { const o = graphNode(id); return o ? notes[`${keyOf(o)}>${n.number}`] : null; };
  const outNote = id => { const o = graphNode(id); return o ? notes[`${n.number}>${keyOf(o)}`] : null; };
  const ms = milestoneCode(n.milestone);
  const rawDone = (issue?.done ?? '').split('\n').filter(line => /^\s*- \[[ xX]\]/.test(line));
  const closed = n.state === 'closed';
  return panelHeader(front ? `${front.tag}` : 'Entrega', `${escape(`#${n.number} · ${n.title}`)}`,
      `<span class="drawer-status-pill ${st.cls}">${escape(st.label)}</span>`)
    + `<div class="drawer-body">
      <div class="rm-panel-meta">
        ${ms ? `<span class="rl-ms">${escape(ms)}</span>` : ''}
        ${front ? `<button type="button" class="rm-front-chip" data-graph-id="frente-${front.id}">Frente: ${escape(front.name)} →</button>` : ''}
        ${n.assignees.length ? `<span class="rm-assignee">${escape(n.assignees.join(', '))}</span>` : '<span class="rm-assignee">Sin responsable</span>'}
      </div>
      <div class="drawer-issue-links">
        ${link(n.url, 'Ver en GitHub')}
        ${issue ? `<button type="button" class="drawer-jump-issue-btn" data-jump-issue="${n.number}">Abrir en vista de trabajo →</button>` : ''}
      </div>
      ${closed ? (n.stateReason === 'not_planned'
        ? `<div class="drawer-action-callout" style="background:var(--coral);border-color:#ebd0be"><span class="callout-label">Retirada sin hacerse</span><p>Esta entrega se cerró como no planificada: no es trabajo completado. Aparece en el mapa solo como contexto.</p></div>`
        : `<div class="drawer-action-callout" style="background:var(--green);border-color:#c9d6b7"><span class="callout-label">Ya terminada</span><p>Esta entrega está cerrada como completada. Aparece en el mapa como contexto de lo que habilitó el trabajo actual.</p></div>`) : ''}
      ${unknownDeps.length ? `<div class="drawer-issues-box"><span class="callout-label">Dependencias sin verificar</span><p class="drawer-issues-help">GitHub marca estas relaciones, pero el issue origen no está en el snapshot actual.</p>${depEdgeList(unknownDeps, '', inNote)}</div>` : ''}
      ${pending.length ? `<div class="blocker-note"><strong>Espera a ${pending.map(id => `#${graphNode(id)?.number}`).join(', ')}.</strong><p>Podés leer el contexto, pero la ejecución depende de esas entregas.</p></div>
        <div class="drawer-issues-box"><span class="callout-label">Bloqueos vigentes</span>${depEdgeList(pending, '', inNote)}</div>` : ''}
      ${!closed && (n.conditions?.length) ? `<div class="drawer-action-callout" style="background:var(--paper);border-color:#d8b98a"><span class="callout-label">Condición documental previa</span>${n.conditions.map(c => `<p>${escape(c.text)}</p>`).join('')}<p class="rm-rel-note">No es un bloqueo de GitHub: viene del mapa de decisiones adoptado.</p></div>` : ''}
      ${!closed && issue ? `
        ${reviewed ? `<div class="brief-state fresh">${briefStatus(brief)}<span>Revisado el ${date(brief.review.at)}</span></div>` : `<div class="brief-state pending">${briefStatus(brief)}<span>${brief?.status === 'stale' ? 'Cambió el issue o una fuente; la orientación espera revisión.' : 'Sin orientación revisada en esta rama; se muestra el contrato del issue.'}</span></div>`}
        <section class="brief-section"><h4>Qué vas a lograr</h4>${paragraphs(reviewed ? brief.goal : issue.goal || 'Consultá el resultado en el issue original.')}</section>
        <section class="brief-section start-section"><h4>Siguiente acción</h4>${paragraphs(reviewed ? brief.start : issue.context || 'Revisá el issue completo en GitHub y sus dependencias.')}</section>
        ${reviewed ? `<section class="brief-section"><h4>Para entrar en contexto</h4>${documentSources(brief)}</section>` : ''}
        <section class="brief-section"><h4>Cómo saber que terminaste</h4>${rawDone.length ? `<ul class="criteria">${rawDone.map(line => `<li>${escape(plain(line.replace(/^\s*- \[[ xX]\]\s*/, '')))}</li>`).join('')}</ul>` : paragraphs(reviewed ? brief.done : issue.done || 'Consultá los criterios en GitHub.')}</section>` : ''}
      ${!closed && !issue ? '<p>No encontramos el detalle local del issue; consultalo en GitHub.</p>' : ''}
      ${unlocks.length || conditional.length ? `<div class="drawer-issues-box"><span class="callout-label">Al terminar, desbloquea</span>${depEdgeList([...unlocks, ...conditional], '', outNote)}${conditional.length ? '<p class="rm-rel-note">La flecha hacia el laboratorio es una condición de retomo, no un bloqueo.</p>' : ''}</div>` : ''}
      ${doneDeps.length ? `<div class="drawer-issues-box"><span class="callout-label">Habilitada por (ya cerradas)</span>${depEdgeList(doneDeps, '', inNote)}</div>` : ''}
      ${front?.evidence ? `<div class="drawer-reading-box"><span class="callout-label">Evidencia del frente</span><div class="reading-link">${link(front.evidence.url, front.evidence.label)}</div><p class="reading-detail">${escape(front.evidence.detail)}</p></div>` : ''}
      ${archLinksHTML(n.number)}
    </div>`;
}
function frontIssueButton(num) {
  const n = graphNode(`i${num}`);
  const susp = rm().suspendedFront?.issues?.find(i => i.number === num);
  const title = n?.title ?? susp?.title ?? `Issue #${num}`;
  const st = n ? nodeStatus(n) : { label: susp ? 'Pausado (not planned)' : 'Sin verificar', cls: susp ? 'status-paused' : 'status-espera' };
  if (!n) {
    const url = susp?.url ?? `${repo}/issues/${num}`;
    return `<a class="drawer-issue-btn" href="${escape(url)}" target="_blank" rel="noopener noreferrer">
      <span class="d-iss-num">#${num}</span><span class="d-iss-title">${escape(title)}</span>
      <span class="d-iss-status ${st.cls}">${escape(st.label)}</span>${externalIcon}</a>`;
  }
  return `<button type="button" class="drawer-issue-btn ${selectedGraphId === n.id ? 'is-active-issue' : ''}" data-graph-id="${n.id}">
    <span class="d-iss-num">#${num}</span><span class="d-iss-title">${escape(title)}</span>
    <span class="d-iss-status ${st.cls}">${escape(st.label)}</span><span class="d-iss-arrow" aria-hidden="true">→</span></button>`;
}
function frontDetailHTML(front) {
  const issueNums = front.paused ? [] : (front.concluded ? (rm().graph?.nodes ?? []).filter(n => n.front === 'concluido').map(n => n.number) : front.issues);
  return panelHeader(front.tag ?? 'Frente', escape(front.name),
      `<span class="drawer-status-pill status-${front.state === 'pausado' ? 'paused' : (front.state ?? 'activo')}">${escape(front.stateLabel ?? '')}</span>`)
    + `<div class="drawer-body">
      ${front.purpose ? `<div class="drawer-reading-box"><span class="callout-label">Para qué existe</span><p class="reading-detail">${escape(front.purpose)}</p></div>` : ''}
      ${front.whatExists ? `<div class="drawer-reading-box"><span class="callout-label">Qué existe hoy</span><p class="reading-detail">${escape(front.whatExists)}</p></div>` : ''}
      ${front.nextStep ? `<div class="drawer-action-callout"><span class="callout-label">Siguiente paso del frente</span><p>${escape(front.nextStep)}</p></div>` : ''}
      ${front.evidence ? `<div class="drawer-reading-box"><span class="callout-label">Evidencia</span><div class="reading-link">${link(front.evidence.url, front.evidence.label)}</div><p class="reading-detail">${escape(front.evidence.detail)}</p></div>` : ''}
      ${issueNums.length ? `<div class="drawer-issues-box"><span class="callout-label">Entregas del frente (${issueNums.length})</span><p class="drawer-issues-help">Elegí una entrega para ver su detalle:</p><div class="drawer-issues-list">${issueNums.map(frontIssueButton).join('')}</div></div>` : ''}
      ${front.archLink ? `<div class="drawer-reading-box"><span class="callout-label">Visualización</span><div class="rm-arch-links">${ilink(front.archLink, 'Ver en la visualización de arquitectura (pipeline propuesto)')}</div></div>` : ''}
    </div>`;
}
function pausedDetailHTML() {
  const sf = rm().suspendedFront;
  if (!sf) return '';
  const hasReopened = (sf.issues ?? []).some(i => i.state === 'open');
  return panelHeader(sf.tag ?? 'Laboratorio', escape('Laboratorio (pausado)'),
      `<span class="drawer-status-pill status-paused">${escape(sf.stateLabel ?? 'Pausado')}</span>`)
    + `<div class="drawer-body">
      <div class="drawer-action-callout" style="background:var(--coral);border-color:#ebd0be">
        <strong style="color:#76331f">${escape(sf.title)}</strong>
        <p>${escape(sf.summary)}</p>
      </div>
      <div class="drawer-reading-box"><span class="callout-label">Por qué está pausado</span><p class="reading-detail">${escape(sf.whySuspended)}</p></div>
      <div class="drawer-reading-box"><span class="callout-label">Condición de retomo</span><p class="reading-detail">${escape(sf.howToResume?.condition ?? 'Sin condición registrada.')}</p></div>
      <div class="drawer-branches-box"><span class="callout-label">Ramas y artefactos conservados</span>
        <div class="branches-mini-list">${(sf.howToResume?.branches ?? []).map(br => `
          <div class="branch-mini-item"><div class="branch-mini-top"><code>${escape(br.name)}</code> · <small>${escape(br.ref)}</small></div>
          <p>${escape(br.purpose)}</p>${link(br.url, 'Ver rama')}</div>`).join('')}
        </div>
        <div class="drawer-quote-wrap"><blockquote class="drawer-quote"><p>«${escape(sf.evidence?.text ?? '')}»</p><cite>— ${link(sf.evidence?.commentUrl ?? `${repo}/issues`, sf.evidence?.author ?? 'Comentario')}</cite></blockquote></div>
        ${sf.howToResume?.precautions ? `<p class="reading-detail" style="margin-top:10px">${escape(sf.howToResume.precautions)}</p>` : ''}
        ${hasReopened ? `<div class="resume-precautions drawer-resume-notice"><strong>Aviso de discrepancia:</strong><p>Se detectaron issues de este frente reabiertos en GitHub. Requiere revisión de orientación.</p></div>` : ''}
      </div>
      <div class="drawer-issues-box"><span class="callout-label">Issues conservados (${(sf.issues ?? []).length})</span>
        <div class="drawer-issues-list">${(sf.issues ?? []).map(i => frontIssueButton(i.number)).join('')}</div>
        <p class="drawer-issues-help">Nunca cuentan como bloqueo ni como trabajo completado: son piezas pausadas en sus ramas.</p>
      </div>
      ${sf.retiredRecommendations ? `<div class="drawer-issues-box"><span class="callout-label">Recomendaciones del análisis (requieren replanificación)</span>
        <p class="drawer-issues-help">${escape(sf.retiredRecommendations.text)}</p>
        <div class="rm-arch-links">${ilink('/arquitectura/#seccion-laboratorio', 'Mapa del código de laboratorio en arquitectura')}</div>
      </div>` : ''}
    </div>`;
}
function roadmapPanelHTML() {
  const id = selectedGraphId;
  if (!id) return `<div class="rm-panel-empty"><span class="callout-label">Detalle</span><h2>Elegí una entrega</h2><p>Tocá un nodo del mapa o de la lista para ver qué existe, la siguiente acción, sus bloqueos y su evidencia.</p><p>Los recuadros agrupan frentes; las flechas muestran dependencias reales de GitHub.</p></div>`;
  if (id === 'laboratorio' || id === 'frente-laboratorio') return pausedDetailHTML();
  if (id.startsWith('frente-')) {
    const front = graphFronts().find(f => f.id === id.slice(7));
    return front ? frontDetailHTML(front) : '';
  }
  const n = graphNode(id);
  return n ? issueNodeDetailHTML(n) : '';
}
function legendHTML() {
  return `<div class="rm-legend-body">
    <div class="rm-legend-group"><span class="callout-label">Frentes</span><ul>${graphFronts().map(f => `<li><span class="rl-dot" style="background:${FRONT_COLORS[f.id] ?? '#5a6a62'}"></span>${escape(f.name)}</li>`).join('')}</ul></div>
    <div class="rm-legend-group"><span class="callout-label">Estado del nodo</span><ul>
      <li><span class="lg-node lg-free"></span>Disponible</li>
      <li><span class="lg-node lg-conditional"></span>Con condición documental</li>
      <li><span class="lg-node lg-blocked"></span>Espera otra entrega</li>
      <li><span class="lg-node lg-done"></span>Completado</li>
      <li><span class="lg-node lg-paused"></span>Pausado (no bloquea)</li>
      <li><span class="lg-node lg-unknown"></span>Sin verificar</li>
      <li><span class="lg-node lg-next"></span>Próximo paso sugerido</li>
    </ul></div>
    <div class="rm-legend-group"><span class="callout-label">Flechas</span><ul>
      <li><span class="lg-edge" style="background:#ad452b"></span>Bloqueo vigente</li>
      <li><span class="lg-edge" style="background:#427345"></span>Dependencia ya resuelta</li>
      <li><span class="lg-edge lg-dashed"></span>Condición de retomo / sin verificar</li>
    </ul></div>
  </div>`;
}
function branchDiffHTML() {
  const diff = data.branchDiff;
  if (!diff || !diff.differing.length) return '';
  const [a, b] = diff.base === branchName ? [diff.base, diff.other] : [diff.other, diff.base];
  return `<details class="rm-diff"><summary>${escape(a)} difiere de ${escape(b)} en ${diff.differing.length} de ${diff.total} fuentes consultadas</summary><ul>${diff.differing.map(p => `<li><code>${escape(p)}</code></li>`).join('')}</ul></details>`;
}
function roadmapView() {
  const b = branch();
  const rmData = rm();
  const nextActions = rmData.currentLocation.nextActions ?? [];
  const params = new URLSearchParams(location.search);
  roadmapMode ??= (params.get('modo') === 'lista' || (typeof window !== 'undefined' && window.innerWidth <= 700)) ? 'lista' : 'mapa';
  const nodoParam = params.get('nodo');
  if (nodoParam && selectedGraphId === null && (graphNode(nodoParam) || graphFronts().some(f => `frente-${f.id}` === nodoParam))) selectedGraphId = nodoParam;
  return heading('Mapa de entregas.', 'Grafo de issues y dependencias reales de GitHub: qué está hecho, qué espera a qué y por dónde seguir.', link(b.documents['docs/propuesta/PLAN-DE-TRABAJO.md'].url, 'Leer Plan de Trabajo', 'text-action'))
    + branchNotice()
    + `<div class="spatial-roadmap ${roadmapMode === 'lista' ? 'mode-lista' : 'mode-mapa'}">
      <div class="roadmap-guide-bar">
        <div class="roadmap-guide-prompt">
          <strong>${escape(rmData.currentLocation.activeMilestone ?? 'Hito actual')}.</strong> Próximos pasos sugeridos:
          ${nextActions.map(a => `<button type="button" class="rm-next-btn" data-graph-id="i${a.issue}" title="${escape(a.description)}"><span class="rm-next-num">#${a.issue}</span> ${escape(a.title)}</button>`).join('')}
        </div>
        <div class="roadmap-guide-actions">${link(repo + '/issues', 'Backlog en GitHub')}</div>
      </div>
      <div class="rm-toolbar">
        <div class="rm-modes" role="group" aria-label="Cómo ver el roadmap">
          <button type="button" data-rm-mode="mapa" aria-pressed="${roadmapMode !== 'lista'}">Mapa</button>
          <button type="button" data-rm-mode="lista" aria-pressed="${roadmapMode === 'lista'}">Lista</button>
        </div>
        <label class="rm-filter"><span>Frente</span><select id="rm-front-filter" aria-label="Filtrar por frente">
          <option value="all">Todos</option>
          ${graphFronts().map(f => `<option value="${f.id}" ${frontFilter === f.id ? 'selected' : ''}>${escape(f.name)}</option>`).join('')}
        </select></label>
        <label class="rm-check"><input type="checkbox" id="rm-available" ${onlyAvailable ? 'checked' : ''}> Solo disponibles</label>
        <button type="button" class="rm-focus-btn" data-rm-action="focus-next" aria-pressed="${focusNext}">Foco en próximos pasos</button>
        <div class="rm-zoom" role="group" aria-label="Controles del mapa">
          <button type="button" data-rm-action="zoom-out" aria-label="Alejar el mapa">−</button>
          <button type="button" data-rm-action="zoom-in" aria-label="Acercar el mapa">+</button>
          <button type="button" data-rm-action="fit">Encuadrar</button>
          <button type="button" data-rm-action="reset" title="Restablecer vista, filtros y selección">Restablecer</button>
        </div>
        <details class="rm-legend"><summary>Leyenda</summary>${legendHTML()}</details>
      </div>
      <div class="rm-meta">
        <span>Snapshot: ${fullDate(data.generatedAt)} (Argentina)</span>
        ${branchDiffHTML()}
      </div>
      <div class="roadmap-body">
        <div class="cy-wrap">
          <div id="cy-roadmap" class="cy-canvas" role="application" aria-label="Mapa interactivo de entregas y dependencias"></div>
          <p class="cy-fallback" hidden>No pudimos cargar el grafo interactivo. Cambiá a la vista <strong>Lista</strong>, que tiene la misma información.</p>
        </div>
        <div class="roadmap-list" id="rm-list">${roadmapListHTML()}</div>
        <aside class="rm-panel" aria-label="Detalle de la entrega seleccionada">
          <div id="rm-panel-body" aria-live="polite">${roadmapPanelHTML()}</div>
        </aside>
      </div>
      <details class="roadmap-secondary-accordion">
        <summary>Consultar calendario académico y decisiones abiertas de la rama</summary>
        <div class="roadmap-secondary-body">
          <div class="roadmap-bottom-grid">
            <section class="calendar-pane">
              <h2>Calendario académico de ${branchName === 'main' ? 'Main' : 'Laboratorio'}</h2>
              <div class="calendar-state">${b.timelineProposed ? 'Propuesta sin discutir' : 'Consultar validación en el Plan'}<p>Las fechas orientan el trabajo; no acreditan que una etapa esté terminada.</p></div>
              <ol class="calendar">${b.timeline.map(row => `<li><strong>${escape(plain(row.date))}</strong><p>${escape(plain(row.goal))}</p></li>`).join('')}</ol>
              ${link(b.documents['docs/propuesta/PLAN-DE-TRABAJO.md'].url + '#11-cronograma', 'Ver calendario en la fuente')}
            </section>
            <section class="decisions-section">
              <div class="section-heading">
                <div><h2>Decisiones para tener presentes</h2><p>Estado declarado en los documentos de esta rama.</p></div>
                ${link(b.documents['docs/gestion/MAPA-DECISIONES.md'].url, 'Abrir mapa de decisiones')}
              </div>
              <div class="decision-list">${b.decisions.filter(item => item.open).map(item => `<article><span>${escape(item.id)}</span><div><h3>${escape(item.title)}</h3><p>${escape(item.state)}</p></div></article>`).join('')}</div>
            </section>
          </div>
        </div>
      </details>
    </div>`;
}
function setupRoadmap() {
  if (cy) { cy.destroy(); cy = null; }
  if (roadmapMode !== 'lista') initCy();
}
function glossaryView() {
  const b = branch();
  return heading('Las palabras que más usamos.', 'Una selección breve para leer issues, corridas y resultados con el mismo significado.', link(b.documents['docs/GLOSARIO.md'].url, 'Abrir glosario completo', 'text-action')) + branchNotice()
    + `<label class="search-box glossary-search"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/></svg><input id="glossary-search" type="search" aria-label="Buscar términos" placeholder="Buscá ASR, baseline, marcas…" value="${escape(glossarySearch)}"></label><dl class="glossary-list" aria-live="polite">${glossaryRows()}</dl>`;
}
function glossaryRows() {
  const terms = branch().glossary.filter(item => plain(`${item.term} ${item.definition}`).toLowerCase().includes(glossarySearch.toLowerCase()));
  return terms.length ? terms.map(item => `<div><dt>${escape(item.term)}</dt><dd>${rich(item.definition, 'docs/GLOSARIO.md')}</dd></div>`).join('') : '<div class="empty"><dt>No encontramos ese término.</dt><dd>Probá otra palabra o abrí el glosario completo.</dd></div>';
}
function render() {
  if (!data) return;
  document.querySelectorAll('[data-view]').forEach(button => {
    if (button.dataset.view === view) button.setAttribute('aria-current', 'page'); else button.removeAttribute('aria-current');
  });
  document.querySelectorAll('[data-branch]').forEach(button => button.setAttribute('aria-pressed', button.dataset.branch === branchName));
  app.className = `page view-${view}`;
  app.innerHTML = view === 'roadmap' ? roadmapView() : view === 'glosario' ? glossaryView() : workView(view === 'ahora');
  main.setAttribute('aria-busy', 'false');
  const b = branch();
  document.querySelector('#source-footer').innerHTML = `<span>Datos consultados: ${fullDate(data.generatedAt)} (Argentina)</span><span>${link(`${repo}/commit/${b.sha}`, `${b.name} · ${b.sha.slice(0,7)}`)} · fuentes del ${date(b.committedAt)}</span>`;
  if (Date.now() - Date.parse(data.generatedAt) > 24 * 60 * 60 * 1000) document.querySelector('#source-footer').insertAdjacentHTML('afterbegin', '<strong class="stale-snapshot">Esta publicación tiene más de 24 horas. Verificá el estado actual en GitHub.</strong>');
  if (view === 'roadmap') setupRoadmap();
  urlState();
}
document.addEventListener('click', event => {
  const rmMode = event.target.closest('[data-rm-mode]');
  if (rmMode && data) { setRoadmapMode(rmMode.dataset.rmMode); return; }
  const rmAction = event.target.closest('[data-rm-action]');
  if (rmAction && data) { handleRmAction(rmAction.dataset.rmAction); return; }
  const graphBtn = event.target.closest('[data-graph-id]');
  if (graphBtn && data) { selectGraph(graphBtn.dataset.graphId); return; }

  const button = event.target.closest('button');
  if (!button || !data) return;
  if (button.dataset.view) {
    view = button.dataset.view;
    search = '';
    selected = null;
    selectedGraphId = null;
    render();
    main.focus({ preventScroll:true });
    main.scrollIntoView({ behavior:'instant', block:'start' });
  }
  if (button.dataset.branch) { branchName = button.dataset.branch; render(); }
  if (button.dataset.phase) { milestoneFilter = button.dataset.phase; view = 'issues'; selected = null; search = ''; render(); main.focus({ preventScroll:true }); main.scrollIntoView({ behavior:'instant', block:'start' }); }
  if (button.dataset.jumpIssue) {
    const targetNum = Number(button.dataset.jumpIssue);
    const targetIssue = data.issues.find(i => i.number === targetNum);
    const current = currentMilestone();
    selected = targetNum;
    search = '';
    selectedGraphId = null;
    if (targetIssue && targetIssue.milestone === current?.number) {
      milestoneFilter = 'all';
      view = 'ahora';
    } else {
      view = 'issues';
      milestoneFilter = targetIssue?.milestone ? String(targetIssue.milestone) : 'all';
    }
    render();
    main.focus({ preventScroll: true });
    const row = document.querySelector(`[data-issue="${selected}"]`);
    row?.focus({ preventScroll: true });
    if (innerWidth <= 1000) {
      const panel = document.querySelector('#brief-panel');
      panel?.setAttribute('tabindex', '-1');
      panel?.focus({ preventScroll: true });
      panel?.scrollIntoView({ behavior: reducedMotion() ? 'instant' : 'smooth', block: 'start' });
    } else {
      row?.scrollIntoView({ behavior: reducedMotion() ? 'instant' : 'smooth', block: 'nearest' });
    }
  }
  if (button.dataset.issue) {
    selected = Number(button.dataset.issue); render();
    const row = document.querySelector(`[data-issue="${selected}"]`);
    row?.focus({ preventScroll:true });
    if (innerWidth <= 1000) {
      const panel = document.querySelector('#brief-panel');
      panel?.setAttribute('tabindex', '-1'); panel?.focus({ preventScroll:true }); panel?.scrollIntoView({ behavior: reducedMotion() ? 'instant' : 'smooth', block:'start' });
    }
  }
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && selectedGraphId) {
    event.preventDefault();
    clearGraphSelection();
  }
});
let resizeTimer = null;
window.addEventListener('resize', () => {
  if (view !== 'roadmap' || !cy) return;
  clearTimeout(resizeTimer);
  resizeTimer = setTimeout(() => cy?.resize(), 120);
});
document.addEventListener('input', event => {
  if (event.target.id === 'issue-search') {
    const focus = event.target.selectionStart;
    search = event.target.value; render();
    const input = document.querySelector('#issue-search'); input?.focus({ preventScroll:true });
    if (input?.type !== 'search') input?.setSelectionRange(focus, focus);
  }
  if (event.target.id === 'glossary-search') { glossarySearch = event.target.value; document.querySelector('.glossary-list').innerHTML = glossaryRows(); }
});
document.addEventListener('change', event => {
  if (event.target.id === 'milestone-filter') { milestoneFilter = event.target.value; selected = null; render(); document.querySelector('#milestone-filter')?.focus({ preventScroll:true }); }
  if (event.target.id === 'rm-front-filter') { frontFilter = event.target.value; applyGraphFilters(); }
  if (event.target.id === 'rm-available') { onlyAvailable = event.target.checked; applyGraphFilters(); }
});
async function load() {
  main.setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/data.json', { cache:'no-cache' });
    if (!response.ok) throw new Error('No se pudieron cargar los datos.');
    data = await response.json();
    if (data.version !== 1 || !data.branches?.some(item => item.name === branchName)) throw new Error('Formato de datos no disponible.');
    render();
  } catch {
    main.setAttribute('aria-busy', 'false');
    app.className = 'page error-state';
    app.innerHTML = '<h1>No pudimos recuperar el contexto.</h1><p>Reintentá la carga o consultá las fuentes en GitHub.</p><button type="button" id="retry">Volver a intentar</button>' + link(repo, 'Abrir repositorio');
    document.querySelector('#retry').addEventListener('click', load);
  }
}
load();
