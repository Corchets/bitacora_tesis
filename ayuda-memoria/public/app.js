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
let componentFilter = 'all';
let selectedComponentId = null;
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
  if (view === 'roadmap' && selectedComponentId) url.searchParams.set('componente', selectedComponentId);
  if (view === 'roadmap' && componentFilter !== 'all') url.searchParams.set('filtro', componentFilter);
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

// ---------- Roadmap por componentes del sistema ----------
// Componentes y avances editoriales: roadmap.json. Estados y bloqueos: GitHub.
const rm = () => data.roadmap;
const graphNode = id => rm().graph?.nodes.find(n => n.id === id);
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
const systemComponents = () => rm().systemMap?.components ?? [];
const componentById = id => systemComponents().find(c => c.id === id);
const componentNodes = c => c.issues.map(num => graphNode(`i${num}`)).filter(Boolean);
const componentArtifacts = c => c.artifacts.filter(path => branch().paths.includes(path));
const availableNode = n => n.state === 'open' && !n.openBlockers.length && !n.conditions?.length;
function componentStatus(c) {
  const nodes = componentNodes(c);
  if (c.issues.length && nodes.length === c.issues.length && nodes.every(n => n.state === 'closed' && n.stateReason === 'completed')) {
    return { key:'done', label:'Entregas cerradas', symbol:'✓' };
  }
  if (c.exists && componentArtifacts(c).length) return { key:'partial', label:'Avance parcial', symbol:'◐' };
  return { key:'pending', label:'Pendiente', symbol:'○' };
}
function componentVisible(c) {
  const nodes = componentNodes(c);
  if (componentFilter === 'open') return nodes.some(n => n.state === 'open');
  if (componentFilter === 'available') return nodes.some(availableNode);
  if (componentFilter === 'untracked') return !c.issues.length;
  if (componentFilter === 'pending') return componentStatus(c).key !== 'done';
  return true;
}
function componentCardHTML(c, index) {
  const status = componentStatus(c);
  const nodes = componentNodes(c);
  const open = nodes.filter(n => n.state === 'open');
  const done = nodes.filter(n => n.state === 'closed' && n.stateReason === 'completed');
  const available = open.filter(availableNode).length;
  return `<button type="button" class="system-node progress-${status.key} ${selectedComponentId === c.id ? 'is-selected' : ''}" data-component="${escape(c.id)}" aria-pressed="${selectedComponentId === c.id}" aria-controls="rm-panel-body">
    <span class="system-node-top"><span class="system-code">${String(index + 1).padStart(2, '0')}</span><span class="progress-label"><span aria-hidden="true">${status.symbol}</span> ${status.label}</span></span>
    <strong>${escape(c.name)}</strong><span class="system-role">${escape(c.role)}</span><span class="system-missing-preview"><b>Falta</b> ${escape(c.missing)}</span>
    <span class="system-node-bottom">${open.length ? `<b>${open.length} ${open.length === 1 ? 'issue abierto' : 'issues abiertos'}</b>` : c.issues.length ? '<b>Sin issues abiertos</b>' : '<b class="untracked">Sin issue específico</b>'}<span>${available ? `${available} sin bloqueos` : done.length ? `${done.length} completado${done.length === 1 ? '' : 's'}` : 'Ver qué falta'} →</span></span>
  </button>`;
}
function roadmapListHTML() {
  const groups = rm().systemMap?.groups ?? [];
  let index = 0;
  const html = groups.map((group, i) => {
    const components = group.components.map(componentById).filter(Boolean);
    const cards = components.map(c => { const cardIndex = index++; return componentVisible(c) ? componentCardHTML(c, cardIndex) : ''; }).join('');
    if (!cards) return '';
    return `<section class="system-group ${group.support ? 'system-support' : ''}" aria-labelledby="system-group-${escape(group.id)}">
      <header><span class="system-step">${group.support ? '+' : String(i + 1).padStart(2, '0')}</span><div><h2 id="system-group-${escape(group.id)}">${escape(group.name)}</h2><p>${escape(group.flow)}</p></div>${!group.support && i < 4 ? '<span class="system-flow-arrow" aria-hidden="true">→</span>' : ''}</header>
      <div class="system-group-nodes">${cards}</div></section>`;
  }).join('');
  return html || '<p class="empty">No hay componentes con este filtro. Elegí «Todo el sistema» para volver al mapa completo.</p>';
}
function updateGraphSelection() {
  document.querySelectorAll('[data-graph-id]').forEach(btn => {
    const on = btn.dataset.graphId === selectedGraphId;
    btn.classList.toggle('is-selected', on);
    btn.setAttribute('aria-pressed', String(on));
  });
  document.querySelectorAll('[data-component]').forEach(btn => {
    const on = btn.dataset.component === selectedComponentId;
    btn.classList.toggle('is-selected', on);
    btn.setAttribute('aria-pressed', String(on));
  });
  renderRoadmapPanel();
  urlState();
}
function focusRoadmapPanel() {
  const panel = document.querySelector('#rm-panel-body');
  panel?.focus({ preventScroll:true });
  panel?.scrollIntoView({ behavior:reducedMotion() ? 'instant' : 'smooth', block:'start' });
}
function selectComponent(id) {
  if (!componentById(id)) return;
  selectedComponentId = id;
  selectedGraphId = null;
  updateGraphSelection();
  focusRoadmapPanel();
}
function selectGraph(id) {
  selectedGraphId = id;
  updateGraphSelection();
  focusRoadmapPanel();
}
function clearGraphSelection() {
  const component = selectedComponentId;
  selectedComponentId = null;
  selectedGraphId = null;
  updateGraphSelection();
  document.querySelector(`[data-component="${component}"]`)?.focus({ preventScroll:true });
}
function setRoadmapMode(mode) {
  roadmapMode = mode;
  document.querySelector('.system-roadmap')?.classList.toggle('mode-lista', mode === 'lista');
  document.querySelectorAll('[data-rm-mode]').forEach(btn => btn.setAttribute('aria-pressed', String(btn.dataset.rmMode === mode)));
  urlState();
}
function handleRmAction(action) {
  if (action === 'clear') clearGraphSelection();
  if (action === 'back-component') { selectedGraphId = null; updateGraphSelection(); focusRoadmapPanel(); }
  if (action === 'reset') { componentFilter = 'all'; selectedComponentId = null; selectedGraphId = null; render(); }
}
function renderRoadmapList() {
  const container = document.querySelector('#rm-list');
  if (container) container.innerHTML = roadmapListHTML();
}
function renderRoadmapPanel() {
  const container = document.querySelector('#rm-panel-body');
  if (container) container.innerHTML = roadmapPanelHTML();
}
function componentDetailHTML(c) {
  const st = componentStatus(c);
  const nodes = componentNodes(c);
  const open = nodes.filter(n => n.state === 'open');
  const closed = nodes.filter(n => n.state === 'closed');
  const artifacts = componentArtifacts(c);
  const front = rm().parallelFronts.find(f => f.id === c.front);
  const decisions = c.decisions.map(id => branch().decisions.find(d => d.id === id)).filter(Boolean);
  const isArchComponent = Boolean(c.archComponent);
  return panelHeader('Componente del sistema', escape(c.name), `<span class="progress-label progress-${st.key}">${st.symbol} ${st.label}</span>`)
    + `<div class="drawer-body component-detail">
      <div><section class="component-section"><h3>Qué existe hoy</h3><p>${escape(artifacts.length ? c.exists : 'No hay un artefacto identificado en las fuentes de esta rama.')}</p>
      ${artifacts.length ? `<ul class="component-artifacts">${artifacts.map(path => `<li>${link(`${repo}/blob/${branch().sha}/${path}`, path)}</li>`).join('')}</ul>` : ''}</section>
      <section class="component-section component-missing"><h3>Qué falta</h3><p>${escape(c.missing)}</p></section>
      ${isArchComponent ? `<p class="component-arch-link">${ilink(`/arquitectura/?c=${encodeURIComponent(c.archComponent)}`, 'Ver este componente en arquitectura')}</p>` : ''}
      ${decisions.length ? `<section class="component-section"><h3>Decisiones relacionadas · ${escape(branchName)}</h3><ul class="component-decisions">${decisions.map(d => `<li>${link(`${branch().documents['docs/gestion/MAPA-DECISIONES.md'].url}#${d.id.toLowerCase()}--${d.title.toLowerCase().replace(/[^\p{L}\p{N}_ -]/gu,'').replace(/ /g,'-')}`, `${d.id} · ${d.title}`)}<p>${escape(d.state)}</p></li>`).join('')}</ul></section>` : ''}
      </div><div>
      <section class="component-section"><h3>Issues abiertos relacionados <span>(${open.length})</span></h3>
        ${open.length ? `<p class="drawer-issues-help">Elegí uno para ver objetivo, responsable, condiciones y dependencias.</p><div class="drawer-issues-list">${open.map(n => frontIssueButton(n.number)).join('')}</div>` : `<p>${c.issues.length ? 'No hay issues abiertos relacionados en este snapshot.' : 'Este componente todavía no tiene un issue específico asociado. El pendiente sigue visible para planificarlo.'}</p>`}
      </section>
      ${closed.length ? `<details class="component-history"><summary>Entregas cerradas relacionadas (${closed.length})</summary><div class="drawer-issues-list">${closed.map(n => frontIssueButton(n.number)).join('')}</div></details>` : ''}
      ${front ? `<details class="component-history"><summary>Avances y evidencia del frente · ${escape(front.name)}</summary><p>${escape(front.whatExists)}</p>${link(front.evidence.url, front.evidence.label)}<p>${escape(front.evidence.detail)}</p><p class="rm-rel-note">Actualización editorial: ${escape(rm().updatedAt)}. La fuente enlazada puede pertenecer a otra rama.</p></details>` : ''}
      </div>
    </div>`;
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
 * correspondencia componente→issues vive en systemMap; archComponents
 * conserva únicamente decisiones y secciones complementarias. */
function archLinksHTML(num) {
  const meta = (rm().archComponents || {})[num] ?? {};
  const components = systemComponents().filter(c => c.archComponent && c.issues.includes(num)).map(c => c.archComponent);
  if (!components.length && !(meta.decisions || []).length && !meta.section) return '';
  const parts = [];
  for (const c of components) parts.push(ilink(`/arquitectura/?c=${encodeURIComponent(c)}`, `componente ${c}`));
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
  if (!id && selectedComponentId) return componentDetailHTML(componentById(selectedComponentId));
  if (!id) return `<div class="rm-panel-empty"><span class="callout-label">Del sistema al trabajo concreto</span><h2>Elegí un componente</h2><p>Vas a ver qué existe, qué falta y los issues abiertos para trabajar en ese tema.</p></div>`;
  if (id === 'laboratorio' || id === 'frente-laboratorio') return pausedDetailHTML();
  if (id.startsWith('frente-')) {
    const front = graphFronts().find(f => f.id === id.slice(7));
    return front ? frontDetailHTML(front) : '';
  }
  const n = graphNode(id);
  return n ? `${selectedComponentId ? '<button type="button" class="component-back" data-rm-action="back-component">← Volver al componente</button>' : ''}${issueNodeDetailHTML(n)}` : '';
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
  roadmapMode ??= params.get('modo') === 'lista' ? 'lista' : 'mapa';
  if (!['all','open','available','untracked','pending'].includes(componentFilter)) componentFilter = 'all';
  const components = systemComponents();
  const partial = components.filter(c => componentStatus(c).key === 'partial').length;
  const pending = components.filter(c => componentStatus(c).key === 'pending').length;
  const done = components.filter(c => componentStatus(c).key === 'done').length;
  const untracked = components.filter(c => !c.issues.length).length;
  const openCount = new Set(components.flatMap(c => componentNodes(c).filter(n => n.state === 'open').map(n => n.number))).size;
  return heading('El sistema, de punta a punta.', 'Recorré los componentes, ubicá lo que falta y elegí los issues para avanzar.', ilink('/arquitectura/', 'Ver arquitectura'))
    + branchNotice()
    + `<div class="system-roadmap ${roadmapMode === 'lista' ? 'mode-lista' : ''}">
      <div class="system-overview"><div><span class="callout-label">${escape(currentMilestone()?.title ?? 'Roadmap del proyecto')}</span><h2>¿En qué parte querés trabajar?</h2><p>Elegí un bloque del recorrido para ver sus avances y pendientes.</p></div><div class="system-totals"><span><strong>${partial}</strong> con avances</span><span><strong>${pending}</strong> pendientes</span>${done ? `<span><strong>${done}</strong> con entregas cerradas</span>` : ''}<span><strong>${openCount}</strong> issues abiertos</span></div></div>
      <div class="rm-toolbar">
        <div class="rm-modes" role="group" aria-label="Cómo ver el roadmap"><button type="button" data-rm-mode="mapa" aria-pressed="${roadmapMode !== 'lista'}">Mapa del sistema</button><button type="button" data-rm-mode="lista" aria-pressed="${roadmapMode === 'lista'}">Lista</button></div>
        <label class="rm-filter"><span>Mostrar</span><select id="rm-component-filter" aria-label="Filtrar componentes">${[['all','Todo el sistema'],['open','Con issues abiertos'],['available','Con issues sin bloqueos'],['pending','Con trabajo pendiente'],['untracked',`Sin issue específico (${untracked})`]].map(([value,label]) => `<option value="${value}" ${componentFilter === value ? 'selected' : ''}>${label}</option>`).join('')}</select></label>
        <button type="button" class="rm-focus-btn" data-rm-action="reset">Restablecer</button>
        <span class="system-flow-note">Las etapas indican el recorrido del sistema.</span>
      </div>
      <div class="system-legend" aria-label="Cómo leer el avance"><span class="progress-label progress-done">✓ Entregas cerradas</span><span class="progress-label progress-partial">◐ Avance parcial</span><span class="progress-label progress-pending">○ Pendiente</span><p>El código experimental y los documentos son avances parciales. Un issue cerrado como no planificado no cuenta como completado.</p></div>
      <div class="system-map-scroll" role="region" tabindex="0" aria-label="Recorrido de componentes; desplazamiento horizontal en pantallas angostas"><div class="system-map" id="rm-list">${roadmapListHTML()}</div></div>
      <aside class="rm-panel system-detail" aria-label="Detalle del componente o issue seleccionado"><div id="rm-panel-body" tabindex="-1">${roadmapPanelHTML()}</div></aside>
      <details class="system-context"><summary>Por dónde seguir · avances recientes y laboratorio en pausa</summary><p>${escape(rmData.currentLocation.summary)}</p><p class="rm-rel-note">Actualización editorial: ${escape(rmData.updatedAt)}; fuentes enlazadas en cada componente.</p><div class="roadmap-guide-bar"><div class="roadmap-guide-prompt">${nextActions.map(a => `<button type="button" class="rm-next-btn" data-graph-id="i${a.issue}" title="${escape(a.description)}"><span class="rm-next-num">#${a.issue}</span> ${escape(a.title)}</button>`).join('')}</div></div><button type="button" class="component-back" data-graph-id="laboratorio">Consultar encoder y cascada · laboratorio en pausa →</button></details>
      <div class="rm-meta"><span>GitHub consultado: ${fullDate(data.generatedAt)} (Argentina)</span>${branchDiffHTML()}${link(repo + '/issues', 'Backlog en GitHub')}</div>
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
  urlState();
}
document.addEventListener('click', event => {
  const componentBtn = event.target.closest('[data-component]');
  if (componentBtn && data) { selectComponent(componentBtn.dataset.component); return; }
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
    selectedComponentId = null;
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
  if (event.key === 'Escape' && (selectedGraphId || selectedComponentId)) {
    event.preventDefault();
    clearGraphSelection();
  }
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
  if (event.target.id === 'rm-component-filter') { componentFilter = event.target.value; renderRoadmapList(); urlState(); }
});
async function load() {
  main.setAttribute('aria-busy', 'true');
  try {
    const response = await fetch('/data.json', { cache:'no-cache' });
    if (!response.ok) throw new Error('No se pudieron cargar los datos.');
    data = await response.json();
    if (data.version !== 1 || !data.branches?.some(item => item.name === branchName)) throw new Error('Formato de datos no disponible.');
    const component = params.get('componente');
    if (componentById(component)) selectedComponentId = component;
    const node = params.get('nodo');
    if (graphNode(node) || graphFronts().some(f => `frente-${f.id}` === node)) selectedGraphId = node;
    componentFilter = params.get('filtro') || 'all';
    render();
  } catch {
    main.setAttribute('aria-busy', 'false');
    app.className = 'page error-state';
    app.innerHTML = '<h1>No pudimos recuperar el contexto.</h1><p>Reintentá la carga o consultá las fuentes en GitHub.</p><button type="button" id="retry">Volver a intentar</button>' + link(repo, 'Abrir repositorio');
    document.querySelector('#retry').addEventListener('click', load);
  }
}
load();
