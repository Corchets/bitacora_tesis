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
let selectedRoadmapNode = null;
let drawerIssue = null;
let lastFocusedNodeId = null;
let lastIsMobile = typeof window !== 'undefined' ? window.innerWidth <= 700 : false;
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
const iconArrow = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-5-5 5 5-5 5"/></svg>';
const externalIcon = '<svg class="external-icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M7 7h10v10"/></svg>';
function link(url, label, className = '') { return `<a href="${escape(url)}" class="${className}" target="_blank" rel="noopener noreferrer">${escape(label)} ${externalIcon}</a>`; }
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
function getRoadmapNodes() {
  const rm = data.roadmap;
  const sf = rm.suspendedFront;
  return [
    {
      id: 'laboratorio',
      type: 'paused',
      name: 'Laboratorio (En pausa)',
      subtitle: 'Tito, UI y cascada · Pausado',
      tag: 'Archipiélago experimental · En suspensión',
      state: 'pausado',
      stateLabel: 'Pausado (conservado)',
      iconSvg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 2v5.5L4 19a2 2 0 0 0 1.7 3h12.6a2 2 0 0 0 1.7-3L14 7.5V2M9 12h6M9 16h6"/></svg>',
      actionTitle: 'Frente suspendido formalmente el 2026-10-04 (not_planned)',
      actionDetail: 'Despriorizado en bloque (#41, #42, #44, #46, #47, #48, #49) para no asumir arquitecturas complejas (RoBERTuito o cascada con SLM) antes de validar la línea base simple (reglas) y el corpus piloto. No es un fracaso ni bloquea el avance principal; las ramas remotas se conservan intactas.',
      howToResume: 'Coordinado en #51 (D09): solo si la comparación sistemática de candidatos en H4 justifica evaluar un modelo más pesado frente a la línea base simple de reglas.',
      branches: [
        { name: 'nacho1706/feature-training-data', ref: 'bb542e1', purpose: 'Banco de 6.000 textos sintéticos argentinos en experiments/laboratorio/entrenamiento_tito/ y scripts de entrenamiento.', url: 'https://github.com/Corchets/bitacora_tesis/tree/nacho1706/feature-training-data' },
        { name: 'origin/laboratorio-main', ref: '4888277', purpose: 'UI local en Python (#44) para explorar CSVs de corridas, turnos y comparaciones.', url: 'https://github.com/Corchets/bitacora_tesis/tree/laboratorio-main' },
        { name: 'origin/nacho1706/experimento-spike-config-alta...', ref: '5ac40b5', purpose: 'Spike previo de cascada alta con Zipformer Kroko + TF-IDF (#29).', url: 'https://github.com/Corchets/bitacora_tesis/tree/nacho1706/experimento-spike-config-alta-zipformer-kroko-tf' }
      ],
      quote: { text: 'Cierre como no planificado, no completado. Artefactos en rama remota nacho1706/feature-training-data. No adopta RoBERTuito definitivo.', author: 'nacho1706 (2026-10-07)', url: 'https://github.com/Corchets/bitacora_tesis/issues/49#issuecomment-6048514393' },
      reading: { label: 'Issue #49 (Resolución nacho1706)', url: 'https://github.com/Corchets/bitacora_tesis/issues/49#issuecomment-6048514393', detail: 'Fundamentación de preservación de artefactos en ramas remotas' },
      issues: [46, 47, 48, 49, 41, 42, 44],
      activeIssue: null
    },
    {
      id: 'deteccion',
      type: 'actionable',
      name: 'Alinear detector',
      subtitle: 'Texto incremental · #50',
      tag: 'Frente B · ASR, Reglas y Replay',
      state: 'activo',
      stateLabel: 'Listo',
      iconSvg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 7 4-4 4 4"/><path d="M8 3v13"/><rect x="4" y="16" width="16" height="5" rx="2"/><path d="M14 8h6M14 12h4"/></svg>',
      actionTitle: 'Alinear disyuntiva de alcance de Mateo (#20) antes de codificar',
      actionDetail: 'En el cierre de #20, Mateo Antenucci propuso priorizar un prototipo de SLM liviano sobre texto incremental. Sin embargo, el contrato formal de #50 exige implementar reglas heurísticas como baseline estricto. Alinear esta disyuntiva sin cerrar prematuramente D09 (que compara reglas vs SLM vs Tito en H4, con reglas como línea base oficial).',
      reading: { label: 'Issue #20 (Comentario de cierre)', url: 'https://github.com/Corchets/bitacora_tesis/issues/20#issuecomment-6048718768', detail: 'Disyuntiva de alcance de Mateo: SLM liviano vs contrato de reglas de #50' },
      issues: [50, 19, 28],
      activeIssue: 50
    },
    {
      id: 'estamos_aca',
      type: 'current',
      name: 'Estamos acá',
      subtitle: 'Hito 2 en curso',
      tag: 'Núcleo activo · H2',
      state: 'en_curso',
      stateLabel: 'En curso',
      iconSvg: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="9" stroke-dasharray="3 3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3"/></svg>',
      actionTitle: 'H1 cerrado (PR #56), H2 en marcha con 3 frentes concurrentes',
      actionDetail: 'El PR #56 completó #20 (catálogo sintético y par de WhatsApp) cerrando formalmente el Hito 1. El Hito 2 avanza en paralelo sobre texto (#50), audio (#39) y metodología (#25). No requiere esperar a que un frente termine para comenzar otro.',
      reading: { label: 'docs/propuesta/PLAN-DE-TRABAJO.md §10', url: 'https://github.com/Corchets/bitacora_tesis/blob/main/docs/propuesta/PLAN-DE-TRABAJO.md#10-hitos-y-entregables', detail: 'Hitos, fases y entregables aprobados del Plan de Trabajo' },
      issues: [50, 39, 25],
      activeIssue: null
    },
    {
      id: 'corpus',
      type: 'actionable',
      name: 'Grabar primer par',
      subtitle: 'Datos y audio · #39',
      tag: 'Frente A · Datos y Llamadas',
      state: 'activo',
      stateLabel: 'Listo',
      iconSvg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v1a7 7 0 0 1-14 0v-1M12 18v4M8 22h8"/></svg>',
      actionTitle: 'Coordinar la grabación del primer par contrastante WhatsApp',
      actionDetail: 'Grabar y transcribir el primer par contrastante (1 llamada vishing, 1 legítima) con audio en dos canales. Esto habilita de inmediato la prueba de ASR local (#19) y la calibración del manual de anotación humana D07 (#32), sin esperar las 14 tomas del piloto completo (#54).',
      reading: { label: 'docs/ingenieria/ARQUITECTURA.md §4', url: 'https://github.com/Corchets/bitacora_tesis/blob/main/docs/ingenieria/ARQUITECTURA.md#4-primer-par-escrito-del-escenario-al-aviso', detail: 'Fichas de rol y guión del par WhatsApp integrado vía PR #56' },
      issues: [39, 32, 54, 55, 45],
      activeIssue: 39
    },
    {
      id: 'metodologia',
      type: 'actionable',
      name: 'Investigar antecedentes',
      subtitle: 'Literatura y métricas · #25',
      tag: 'Frente C · D08, D09 y Metodología',
      state: 'disponible',
      stateLabel: 'Disponible',
      iconSvg: '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/></svg>',
      actionTitle: 'Sintetizar antecedentes sobre métricas temporales de vishing',
      actionDetail: 'Completar en SINTESIS-ESTADO-DEL-ARTE.md la literatura sobre anticipación y métricas temporales (T_A, T_R, márgenes L_R, L_C). Este frente es totalmente autónomo y no depende de audio grabado ni de código del detector.',
      reading: { label: 'docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md', url: 'https://github.com/Corchets/bitacora_tesis/blob/main/docs/investigacion/SINTESIS-ESTADO-DEL-ARTE.md', detail: 'Estado del arte vivo sobre detección incremental y anticipación' },
      issues: [25, 33, 51],
      activeIssue: 25
    },
    {
      id: 'futuro',
      type: 'future',
      name: 'Horizonte futuro',
      subtitle: 'H4 a H6 · Test y defensa',
      tag: 'Horizonte metodológico · Previsto',
      state: 'espera',
      stateLabel: 'Previsto (más adelante)',
      iconSvg: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7"/></svg>',
      actionTitle: 'Etapas avanzadas: congelar protocolo, test ciego y defensa',
      actionDetail: 'Horizonte metodológico futuro: requiere completar el piloto (#54) y congelar particiones (#55) y protocolo (#33 / D08) antes de ejecutar la medición sobre el conjunto de test ciego (#52). Culmina con informe de tesis (~100 págs), demo y defensa ante tribunal UNSTA (#53).',
      reading: { label: 'docs/evaluacion/METRICAS.md', url: 'https://github.com/Corchets/bitacora_tesis/blob/main/docs/evaluacion/METRICAS.md', detail: 'Fórmulas unificadas de T_A, T_R, márgenes y evaluación temporal' },
      issues: [55, 45, 33, 51, 52, 53],
      activeIssue: null
    }
  ];
}

function renderSpatialSvg(isMobile) {
  if (isMobile) {
    return `<svg class="spatial-svg" viewBox="0 0 420 620" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
      <defs>
        <pattern id="sp-grid-m" width="30" height="30" patternUnits="userSpaceOnUse">
          <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#e8ede2" stroke-width="0.8"/>
        </pattern>
        <marker id="sp-arr-ink-m" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#203e37" stroke="none"/>
        </marker>
        <marker id="sp-arr-coral-m" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#ad452b" stroke="none"/>
        </marker>
        <marker id="sp-arr-green-m" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#365b35" stroke="none"/>
        </marker>
      </defs>

      <rect width="420" height="620" fill="url(#sp-grid-m)" rx="10"/>

      <!-- Isla Pausada (Top) -->
      <rect x="20" y="15" width="380" height="90" rx="10" fill="#faf3ed" stroke="#d4b49e" stroke-width="1.6" stroke-dasharray="5 3"/>
      <text x="32" y="32" font-size="9" font-weight="800" fill="#76331f" letter-spacing="0.04em" stroke="none">ARCHIPIÉLAGO PAUSADO · RAMAS CONSERVADAS</text>

      <!-- Active territory (Center) -->
      <rect x="15" y="125" width="390" height="375" rx="12" fill="#ffffff" fill-opacity="0.85" stroke="#c8d5c0" stroke-width="1.5"/>

      <!-- PR #56 Badge -->
      <g transform="translate(210, 145)">
        <rect x="-80" y="-12" width="160" height="24" rx="12" fill="#203e37"/>
        <text text-anchor="middle" y="4" font-size="10" font-weight="800" fill="#d7e9af" stroke="none">PR #56 (cerró #20) · H1 ✓</text>
      </g>

      <path d="M 160 157 C 120 170 115 175 115 180" fill="none" stroke="#365b35" stroke-width="1.8" stroke-dasharray="3 3"/>
      <path d="M 210 160 L 210 270" stroke="#203e37" stroke-width="2" marker-end="url(#sp-arr-ink-m)"/>

      <path d="M 170 295 L 125 240" stroke="#203e37" stroke-width="2" marker-end="url(#sp-arr-ink-m)"/>
      <path d="M 250 295 L 295 240" stroke="#203e37" stroke-width="2" marker-end="url(#sp-arr-ink-m)"/>
      <path d="M 190 350 L 140 405" stroke="#203e37" stroke-width="2" marker-end="url(#sp-arr-ink-m)"/>

      <!-- Audio and text feeding Replay at (210, 385) -->
      <path d="M 115 245 C 115 320 170 380 195 385" fill="none" stroke="#203e37" stroke-width="1.6" stroke-dasharray="3 3"/>
      <path d="M 305 245 C 305 320 250 380 225 385" fill="none" stroke="#203e37" stroke-width="1.6" stroke-dasharray="3 3"/>
      <circle cx="210" cy="385" r="7" fill="#e8eddb" stroke="#203e37" stroke-width="1.8"/>
      <text x="210" y="405" text-anchor="middle" font-size="9" font-weight="800" fill="#203e37" stroke="none">H3 Replay (#28)</text>

      <!-- Conditional dashed path to Paused Lab -->
      <path d="M 70 200 C 40 160 50 115 70 105" fill="none" stroke="#ad452b" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#sp-arr-coral-m)"/>

      <!-- Isla Futura (Bottom) -->
      <rect x="20" y="515" width="380" height="90" rx="10" fill="#f4f7f2" stroke="#abbcb0" stroke-width="1.6" stroke-dasharray="4 4"/>
      <text x="32" y="532" font-size="9" font-weight="800" fill="#203e37" letter-spacing="0.04em" stroke="none">HORIZONTE FUTURO · H4 A H6</text>
      <path d="M 210 395 C 210 450 250 490 270 515" fill="none" stroke="#5a6a62" stroke-width="1.8" marker-end="url(#sp-arr-ink-m)"/>
    </svg>`;
  }

  return `<svg class="spatial-svg" viewBox="0 0 1000 520" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
    <defs>
      <pattern id="sp-grid" width="40" height="40" patternUnits="userSpaceOnUse">
        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#e8ede2" stroke-width="0.8"/>
      </pattern>
      <marker id="sp-arr-ink" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#203e37" stroke="none"/>
      </marker>
      <marker id="sp-arr-coral" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#ad452b" stroke="none"/>
      </marker>
      <marker id="sp-arr-green" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#365b35" stroke="none"/>
      </marker>
      <marker id="sp-arr-muted" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#5a6a62" stroke="none"/>
      </marker>
    </defs>

    <rect width="1000" height="520" fill="url(#sp-grid)" rx="12"/>

    <!-- 1. Isla Pausada (Top Left) -->
    <rect x="20" y="12" width="250" height="115" rx="12" fill="#faf3ed" stroke="#d4b49e" stroke-width="1.8" stroke-dasharray="6 4"/>
    <rect x="30" y="20" width="160" height="18" rx="4" fill="#f4e0d2"/>
    <text x="38" y="33" font-size="9" font-weight="800" fill="#76331f" letter-spacing="0.04em" stroke="none">ARCHIPIÉLAGO PAUSADO</text>
    <text x="30" y="112" font-size="9.5" font-weight="600" fill="#8c5847" stroke="none">Pausado 2026-10-04 · Ramas intactas</text>
    <path d="M 280 15 Q 270 70 275 130" fill="none" stroke="#d5decb" stroke-width="2" stroke-dasharray="3 4"/>

    <!-- 2. Active Territory (Left-Center) -->
    <path d="M 60 170 C 60 155 360 145 615 155 C 640 155 650 330 635 370 C 610 410 560 500 220 500 C 80 500 50 390 60 170 Z" fill="#ffffff" fill-opacity="0.84" stroke="#c8d5c0" stroke-width="1.5"/>

    <!-- 3. Isla Futura (Bottom Right of active zone, shifted left) -->
    <rect x="430" y="360" width="200" height="145" rx="12" fill="#f4f7f2" stroke="#abbcb0" stroke-width="1.8" stroke-dasharray="4 4"/>
    <rect x="440" y="370" width="135" height="18" rx="4" fill="#e5ece1"/>
    <text x="448" y="383" font-size="9" font-weight="800" fill="#203e37" letter-spacing="0.04em" stroke="none">HORIZONTE FUTURO</text>
    <text x="440" y="490" font-size="9.5" font-weight="600" fill="#5a6a62" stroke="none">H4 a H6 · Test ciego y defensa</text>

    <!-- Right Territory: Clean North Orientation -->
    <g transform="translate(860, 110)">
      <circle r="30" fill="none" stroke="#d5decb" stroke-width="1.2" stroke-dasharray="2 3"/>
      <path d="M 0 -30 L 0 30 M -30 0 L 30 0" stroke="#d5decb" stroke-width="1"/>
      <polygon points="0,-26 6,-6 0,-11 -6,-6" fill="#203e37" stroke="none"/>
      <polygon points="0,26 6,6 0,11 -6,6" fill="#5a6a62" stroke="none"/>
      <text y="-34" text-anchor="middle" font-size="9" font-weight="800" fill="#203e37" stroke="none">N</text>
      <text y="44" text-anchor="middle" font-size="8" font-weight="700" fill="#5a6a62" stroke="none">ORIENTACIÓN</text>
    </g>

    <!-- PR #56 Anchor -->
    <g transform="translate(360, 130)">
      <circle r="12" fill="#203e37"/>
      <text text-anchor="middle" y="4" font-size="9" font-weight="800" fill="#d7e9af" stroke="none">H1 ✓</text>
      <text text-anchor="middle" y="-16" font-size="10.5" font-weight="700" fill="#203e37" stroke="none">PR #56 completó #20</text>
    </g>

    <path d="M 360 142 L 360 215" stroke="#203e37" stroke-width="2.5" marker-end="url(#sp-arr-ink)"/>
    <path d="M 345 132 C 260 140 200 170 180 205" fill="none" stroke="#365b35" stroke-width="1.8" stroke-dasharray="4 3" marker-end="url(#sp-arr-green)"/>
    <rect x="210" y="150" width="130" height="18" rx="4" fill="#e8eddb" stroke="#c9d6b7"/>
    <text x="275" y="163" text-anchor="middle" font-size="8.5" font-weight="700" fill="#365b35" stroke="none">Texto sin esperar audio</text>

    <!-- Estamos acá hacia Alinear detector (Frente B) -->
    <path d="M 310 250 L 240 245" stroke="#203e37" stroke-width="2.2" marker-end="url(#sp-arr-ink)"/>

    <!-- Estamos acá hacia Grabar primer par (Frente A) -->
    <path d="M 410 250 L 480 245" stroke="#203e37" stroke-width="2.2" marker-end="url(#sp-arr-ink)"/>

    <!-- Estamos acá hacia Investigar antecedentes (Frente C) -->
    <path d="M 330 280 L 265 375" stroke="#203e37" stroke-width="2.2" marker-end="url(#sp-arr-ink)"/>

    <!-- #39 Audio and #50 Text to Replay -->
    <path d="M 510 275 C 470 320 435 340 405 345" fill="none" stroke="#203e37" stroke-width="1.8" stroke-dasharray="4 3"/>
    <text x="455" y="318" font-size="9" font-weight="700" fill="#203e37" stroke="none">Audio #39</text>

    <path d="M 215 275 C 255 320 325 340 355 345" fill="none" stroke="#203e37" stroke-width="1.8" stroke-dasharray="4 3"/>
    <text x="260" y="318" font-size="9" font-weight="700" fill="#203e37" stroke="none">Texto #50</text>

    <!-- Waypoint H3 Replay (#28) -->
    <g transform="translate(380, 345)">
      <circle r="9" fill="#e8eddb" stroke="#203e37" stroke-width="2"/>
      <text text-anchor="middle" y="3" font-size="8" font-weight="800" fill="#203e37" stroke="none">H3</text>
      <text text-anchor="middle" y="20" font-size="9.5" font-weight="800" fill="#203e37" stroke="none">Replay streaming (#28)</text>
    </g>

    <!-- #25 Advances in parallel towards D08/D09 -->
    <path d="M 270 445 C 330 470 420 470 470 445" fill="none" stroke="#5a6a62" stroke-width="1.6" stroke-dasharray="3 3"/>
    <text x="370" y="465" text-anchor="middle" font-size="9" font-weight="600" fill="#5a6a62" stroke="none">Paralelo independiente hacia D08/D09</text>

    <!-- Replay to Future Horizon -->
    <path d="M 395 355 C 430 375 465 400 490 420" fill="none" stroke="#5a6a62" stroke-width="1.8" marker-end="url(#sp-arr-muted)"/>

    <!-- Conditional path to Paused Laboratory -->
    <path d="M 360 340 C 270 340 140 250 130 135" fill="none" stroke="#ad452b" stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#sp-arr-coral)"/>
    <rect x="100" y="185" width="150" height="18" rx="4" fill="#f9ece1" stroke="#ebd0be"/>
    <text x="175" y="197" text-anchor="middle" font-size="8.5" font-weight="800" fill="#76331f" stroke="none">Solo si #51 (D09) justifica</text>
  </svg>`;
}

function getNodeCoordinates(nodeId, isMobile) {
  if (isMobile) {
    switch (nodeId) {
      case 'laboratorio': return 'left:50%;top:11%;';
      case 'deteccion': return 'left:28%;top:32%;';
      case 'corpus': return 'left:72%;top:32%;';
      case 'estamos_aca': return 'left:50%;top:51%;';
      case 'metodologia': return 'left:31%;top:72%;';
      case 'futuro': return 'left:69%;top:86%;';
      default: return 'left:50%;top:50%;';
    }
  }
  switch (nodeId) {
    case 'laboratorio': return 'left:15%;top:14%;';
    case 'deteccion': return 'left:18%;top:46%;';
    case 'estamos_aca': return 'left:36%;top:48%;';
    case 'corpus': return 'left:54%;top:46%;';
    case 'metodologia': return 'left:24%;top:80%;';
    case 'futuro': return 'left:54%;top:81%;';
    default: return 'left:50%;top:50%;';
  }
}

function drawerIssueButton(num, activeNum) {
  const issue = data.issues.find(i => i.number === num);
  const suspIssue = data.roadmap.suspendedFront?.issues?.find(i => i.number === num);
  let title = issue?.title || suspIssue?.title || `#${num}`;
  let stateLabel = 'Listo';
  let pillClass = 'status-disponible';
  if (suspIssue) {
    if (suspIssue.state === 'open') {
      stateLabel = 'Reabierto en GitHub';
      pillClass = 'status-activo';
    } else {
      stateLabel = 'Pausado (not planned)';
      pillClass = 'status-paused';
    }
  } else if (issue) {
    const pending = blockers(issue);
    if (pending.length > 0) {
      stateLabel = `Espera ${pending.length}`;
      pillClass = 'status-espera';
    } else if (num === activeNum) {
      stateLabel = 'Próximo';
      pillClass = 'status-activo';
    } else {
      stateLabel = 'Listo';
      pillClass = 'status-disponible';
    }
  } else {
    stateLabel = 'Sin verificar';
    pillClass = 'status-espera';
  }
  return `<button type="button" class="drawer-issue-btn ${num === activeNum ? 'is-active-issue' : ''}" data-drawer-issue="${num}">
    <span class="d-iss-num">#${num}</span>
    <span class="d-iss-title">${escape(title)}</span>
    <span class="d-iss-status ${pillClass}">${escape(stateLabel)}</span>
    <span class="d-iss-arrow" aria-hidden="true">→</span>
  </button>`;
}

function renderDrawerIssueBrief(num, node) {
  const issue = data.issues.find(i => i.number === num);
  const suspIssue = data.roadmap.suspendedFront?.issues?.find(i => i.number === num);
  const b = branch();
  const brief = b.briefs[num];
  const pending = issue ? blockers(issue) : [];

  if (suspIssue && !issue) {
    return `<div class="drawer-subnav">
        <button type="button" class="drawer-back-btn" data-drawer-back="true">← Volver a ${escape(node.name)}</button>
      </div>
      <div class="drawer-brief-content">
        <header class="drawer-brief-header">
          <span class="brief-tag status-paused">Issue pausado en rama remota</span>
          <h3>#${suspIssue.number} · ${escape(suspIssue.title)}</h3>
          <div class="drawer-issue-links">
            ${link(suspIssue.url, 'Ver en GitHub')}
            ${suspIssue.commentUrl ? link(suspIssue.commentUrl, 'Comentario de resolución') : ''}
          </div>
        </header>
        <div class="drawer-action-callout" style="background:var(--coral);border-color:#ebd0be">
          <strong style="color:#76331f">Estado: cerrado como no planificado (2026-10-04)</strong>
          <p>Este issue pertenecía a la línea experimental de laboratorio (RoBERTuito/Tito o cascada). Fue cerrado para priorizar la línea base simple. Los artefactos y código están preservados en la rama <code>nacho1706/feature-training-data</code>.</p>
        </div>
        <div class="drawer-reading-box">
          <span class="callout-label">Condición para reabrir</span>
          <p class="reading-detail">Solo se retoma si la comparación de candidatos en #51 (D09) en el Hito 4 justifica contrastar este modelo frente a la línea base simple de reglas.</p>
        </div>
      </div>`;
  }

  if (!issue) {
    return `<div class="drawer-subnav">
        <button type="button" class="drawer-back-btn" data-drawer-back="true">← Volver a ${escape(node.name)}</button>
      </div>
      <div class="drawer-brief-content">
        <h3>Issue #${num}</h3>
        <p>No encontramos detalles locales para este issue.</p>
        ${link(`${repo}/issues/${num}`, 'Abrir en GitHub')}
      </div>`;
  }

  const reviewed = brief?.status === 'reviewed';
  const rawDone = (issue.done || '').split('\n').filter(line => /^\s*- \[[ xX]\]/.test(line));

  return `<div class="drawer-subnav">
      <button type="button" class="drawer-back-btn" data-drawer-back="true">← Volver a ${escape(node.name)}</button>
    </div>
    <div class="drawer-brief-content">
      <header class="drawer-brief-header">
        <span class="brief-tag ${reviewed ? 'reviewed' : ''}">${briefStatus(brief)}</span>
        <h3>#${issue.number} · ${escape(issue.title)}</h3>
        <div class="drawer-issue-links">
          ${link(issue.url, 'Ver en GitHub')}
          <button type="button" class="drawer-jump-issue-btn" data-jump-issue="${issue.number}">Abrir en vista de trabajo →</button>
        </div>
      </header>
      ${pending.length ? `<div class="blocker-note"><strong>Antes de ejecutar, resolver ${pending.map(item => link(item.url, `#${item.number}`)).join(', ')}.</strong><p>Podés consultar el contexto mientras tanto.</p></div>` : ''}
      <section class="brief-section">
        <h4>Qué vas a lograr</h4>
        ${paragraphs(reviewed ? brief.goal : issue.goal || 'Consultá el resultado en el issue original.')}
      </section>
      ${reviewed ? `
        <section class="brief-section">
          <h4>Para entrar en contexto</h4>
          ${documentSources(brief)}
        </section>
        <section class="brief-section start-section">
          <h4>Tu primer paso</h4>
          ${paragraphs(brief.start)}
        </section>
        <section class="brief-section">
          <h4>Cómo saber que terminaste</h4>
          ${paragraphs(brief.done)}
        </section>
      ` : `
        <section class="brief-section">
          <h4>Contexto del issue</h4>
          ${paragraphs(issue.context || 'Consultá el contrato completo en GitHub.')}
        </section>
        <section class="brief-section">
          <h4>Para empezar</h4>
          <p>Revisá el issue y sus dependencias. La skill <code>actualizar-ayuda-memoria</code> puede preparar este brief.</p>
          ${brief?.sources?.length ? documentSources(brief) : ''}
        </section>
        <section class="brief-section">
          <h4>Criterios de término</h4>
          ${rawDone.length ? `<ul class="criteria">${rawDone.map(line => `<li>${escape(plain(line.replace(/^\s*- \[[ xX]\]\s*/, '')))}</li>`).join('')}</ul>` : paragraphs(issue.done || 'Consultá en GitHub.')}
        </section>
      `}
    </div>`;
}

function renderDrawerBody(node) {
  if (drawerIssue) {
    return renderDrawerIssueBrief(drawerIssue, node);
  }

  let branchesHtml = '';
  if (node.id === 'laboratorio') {
    const hasReopened = (node.issues || []).some(num => {
      const iss = data.roadmap.suspendedFront?.issues?.find(i => i.number === num);
      return iss?.state === 'open';
    });
    branchesHtml = `<div class="drawer-branches-box">
      <span class="callout-label">Ramas y artefactos conservados</span>
      <div class="branches-mini-list">
        ${node.branches.map(br => `
          <div class="branch-mini-item">
            <div class="branch-mini-top"><code>${escape(br.name)}</code> · <small>${escape(br.ref)}</small></div>
            <p>${escape(br.purpose)}</p>
            ${link(br.url, 'Ver rama')}
          </div>
        `).join('')}
      </div>
      <div class="drawer-quote-wrap">
        <blockquote class="drawer-quote">
          <p>«${escape(node.quote.text)}»</p>
          <cite>— ${link(node.quote.url, node.quote.author)}</cite>
        </blockquote>
      </div>
      ${hasReopened ? `
        <div class="resume-precautions drawer-resume-notice">
          <strong>Aviso de discrepancia:</strong>
          <p>Se detectaron issues de este frente reabiertos en GitHub. Requiere revisión de orientación.</p>
        </div>
      ` : ''}
    </div>`;
  }

  return `
    <div class="drawer-action-callout">
      <span class="callout-label">Próximo paso concreto</span>
      <strong>${escape(node.actionTitle)}</strong>
      <p>${escape(node.actionDetail)}</p>
    </div>
    <div class="drawer-reading-box">
      <span class="callout-label">Qué leer / Fuente primaria</span>
      <div class="reading-link">${link(node.reading.url, node.reading.label)}</div>
      <p class="reading-detail">${escape(node.reading.detail)}</p>
    </div>
    ${branchesHtml}
    <div class="drawer-issues-box">
      <span class="callout-label">Issues del frente (${node.issues.length})</span>
      <p class="drawer-issues-help">Hacé clic en un issue para ver su brief y contexto aquí mismo:</p>
      <div class="drawer-issues-list">
        ${node.issues.map(num => drawerIssueButton(num, node.activeIssue)).join('')}
      </div>
    </div>
  `;
}

function roadmapView() {
  const b = branch();
  const isMobile = typeof window !== 'undefined' && window.innerWidth <= 700;
  const nodes = getRoadmapNodes();
  const currentNode = nodes.find(n => n.id === selectedRoadmapNode) || null;

  return heading('Mapa visual del proyecto.', 'Frentes de trabajo en paralelo, estado real de ejecución y opciones para retomar.', link(b.documents['docs/propuesta/PLAN-DE-TRABAJO.md'].url, 'Leer Plan de Trabajo', 'text-action'))
    + branchNotice()
    + `<div class="spatial-roadmap">
        <div class="roadmap-guide-bar">
          <div class="roadmap-guide-prompt">
            <strong>Estamos en H2.</strong> Elegí uno de los 3 frentes próximos para ver qué hacer: <strong>Grabar primer par</strong> (#39), <strong>Alinear detector</strong> (#50) o <strong>Investigar antecedentes</strong> (#25).
          </div>
          <div class="roadmap-guide-actions">
            ${link(repo + '/issues', 'Backlog en GitHub')}
          </div>
        </div>

        <div class="spatial-canvas-wrap">
          ${renderSpatialSvg(isMobile)}

          <div class="spatial-nodes-layer" role="group" aria-label="Nodos del mapa interactivo">
            ${nodes.map(node => `
              <button type="button" class="spatial-node-btn node-${node.id} node-${node.type} ${selectedRoadmapNode === node.id ? 'is-selected' : ''}" data-node-id="${node.id}" aria-expanded="${selectedRoadmapNode === node.id}" aria-haspopup="dialog" aria-label="Nodo ${escape(node.name)} (${escape(node.stateLabel)}). Clic para abrir detalle.">
                <div class="node-icon-row">${node.iconSvg}<span class="node-title">${escape(node.name)}</span></div>
                <span class="node-sub">${escape(node.subtitle)}</span>
                <span class="node-pill">${escape(node.stateLabel)}</span>
              </button>
            `).join('')}
          </div>

          <div class="drawer-backdrop ${currentNode ? 'is-open' : ''}" data-drawer-close="true"></div>

          <aside class="roadmap-drawer ${currentNode ? 'is-open' : ''}" role="dialog" aria-modal="true" aria-labelledby="drawer-title" aria-label="Detalle del nodo ${currentNode ? escape(currentNode.name) : ''}">
            ${currentNode ? `
              <header class="drawer-header">
                <div class="drawer-header-top">
                  <span class="drawer-tag">${escape(currentNode.tag)}</span>
                  <button type="button" class="drawer-close-btn" data-drawer-close="true" aria-label="Cerrar panel de detalle">✕ Cerrar <kbd>Esc</kbd></button>
                </div>
                <div class="drawer-title-row">
                  <h2 id="drawer-title">${escape(currentNode.name)}</h2>
                  <span class="drawer-status-pill status-${currentNode.state}">${escape(currentNode.stateLabel)}</span>
                </div>
              </header>
              <div class="drawer-body">
                ${renderDrawerBody(currentNode)}
              </div>
            ` : ''}
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
  const closeTrigger = event.target.closest('[data-drawer-close]');
  if (closeTrigger && selectedRoadmapNode) {
    const restoreId = lastFocusedNodeId || selectedRoadmapNode;
    selectedRoadmapNode = null;
    drawerIssue = null;
    render();
    if (restoreId) document.querySelector(`[data-node-id="${restoreId}"]`)?.focus();
    return;
  }

  if (selectedRoadmapNode && !event.target.closest('.roadmap-drawer') && !event.target.closest('.spatial-node-btn')) {
    const restoreId = lastFocusedNodeId || selectedRoadmapNode;
    selectedRoadmapNode = null;
    drawerIssue = null;
    render();
    if (restoreId) document.querySelector(`[data-node-id="${restoreId}"]`)?.focus();
    return;
  }

  const button = event.target.closest('button');
  if (!button || !data) return;
  if (button.dataset.view) {
    view = button.dataset.view;
    search = '';
    selected = null;
    selectedRoadmapNode = null;
    drawerIssue = null;
    render();
    main.focus({ preventScroll:true });
    main.scrollIntoView({ behavior:'instant', block:'start' });
  }
  if (button.dataset.branch) { branchName = button.dataset.branch; render(); }
  if (button.dataset.phase) { milestoneFilter = button.dataset.phase; view = 'issues'; selected = null; search = ''; render(); main.focus({ preventScroll:true }); main.scrollIntoView({ behavior:'instant', block:'start' }); }
  if (button.dataset.nodeId) {
    lastFocusedNodeId = button.dataset.nodeId;
    selectedRoadmapNode = button.dataset.nodeId;
    drawerIssue = null;
    render();
    const closeBtn = document.querySelector('.drawer-close-btn');
    closeBtn?.focus();
  }
  if (button.dataset.drawerIssue) {
    drawerIssue = Number(button.dataset.drawerIssue);
    render();
    const backBtn = document.querySelector('.drawer-back-btn');
    backBtn?.focus();
  }
  if (button.dataset.drawerBack) {
    drawerIssue = null;
    render();
    const closeBtn = document.querySelector('.drawer-close-btn');
    closeBtn?.focus();
  }
  if (button.dataset.jumpIssue) {
    const targetNum = Number(button.dataset.jumpIssue);
    const targetIssue = data.issues.find(i => i.number === targetNum);
    const current = currentMilestone();
    selected = targetNum;
    search = '';
    selectedRoadmapNode = null;
    drawerIssue = null;
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
      panel?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    } else {
      row?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'nearest' });
    }
  }
  if (button.dataset.issue) {
    selected = Number(button.dataset.issue); render();
    const row = document.querySelector(`[data-issue="${selected}"]`);
    row?.focus({ preventScroll:true });
    if (innerWidth <= 1000) {
      const panel = document.querySelector('#brief-panel');
      panel?.setAttribute('tabindex', '-1'); panel?.focus({ preventScroll:true }); panel?.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block:'start' });
    }
  }
});
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && selectedRoadmapNode) {
    event.preventDefault();
    const restoreId = lastFocusedNodeId || selectedRoadmapNode;
    selectedRoadmapNode = null;
    drawerIssue = null;
    render();
    if (restoreId) document.querySelector(`[data-node-id="${restoreId}"]`)?.focus();
  }
});
window.addEventListener('resize', () => {
  if (view === 'roadmap') {
    const currentIsMobile = window.innerWidth <= 700;
    if (currentIsMobile !== lastIsMobile) {
      lastIsMobile = currentIsMobile;
      render();
    }
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
document.addEventListener('change', event => { if (event.target.id === 'milestone-filter') { milestoneFilter = event.target.value; selected = null; render(); document.querySelector('#milestone-filter')?.focus({ preventScroll:true }); } });
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
