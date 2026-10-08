import { readFile, writeFile, mkdir, cp } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { hash, section, table, glossary, decisions, normalizeIssue, enrichBrief, validateBriefs, validateRoadmap } from './lib.mjs';

const root = fileURLToPath(new URL('../', import.meta.url));
const config = JSON.parse(await readFile(path.join(root, 'config.json'), 'utf8'));
const briefs = JSON.parse(await readFile(path.join(root, 'briefs.json'), 'utf8'));
const roadmapRaw = JSON.parse(await readFile(path.join(root, 'roadmap.json'), 'utf8'));
validateBriefs(briefs, config.branches);
validateRoadmap(roadmapRaw);
let token = process.env.GH_TOKEN || process.env.GITHUB_TOKEN;
if (!token && !process.env.CI) {
  try { token = execFileSync('gh', ['auth', 'token'], { encoding: 'utf8', stdio: ['ignore','pipe','ignore'] }).trim(); } catch { /* Public repository also works without a token. */ }
}
const apiRoot = `https://api.github.com/repos/${config.repository}`;
const headers = { Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28',
  ...(token ? { Authorization: `Bearer ${token}` } : {}) };
async function api(route) {
  const response = await fetch(`${apiRoot}/${route}`, { headers, signal: AbortSignal.timeout(30000) });
  if (!response.ok) throw new Error(`GitHub ${response.status}: ${route}. No se publicó una copia desactualizada.`);
  return response.json();
}
async function pages(route) {
  const data = [];
  for (let page = 1; ; page++) {
    const rows = await api(`${route}${route.includes('?') ? '&' : '?'}per_page=100&page=${page}`);
    data.push(...rows);
    if (rows.length < 100) return data;
  }
}
async function mapLimit(items, fn, limit = 4) {
  const result = new Array(items.length);
  let next = 0;
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, async () => {
    while (next < items.length) { const index = next++; result[index] = await fn(items[index]); }
  }));
  return result;
}
const [rawIssues, rawMilestones] = await Promise.all([pages('issues?state=all'), pages('milestones?state=all')]);
const allIssues = rawIssues.filter(issue => !issue.pull_request);
const openIssues = allIssues.filter(issue => issue.state === 'open');
const dependencies = Object.fromEntries(await mapLimit(openIssues, async issue => {
  const rows = issue.issue_dependencies_summary?.total_blocked_by === 0 ? [] : await pages(`issues/${issue.number}/dependencies/blocked_by`);
  return [issue.number, rows.map(({ number, title, state, html_url }) => ({ number, title, state, url: html_url }))];
}));
const issues = openIssues.map(normalizeIssue);
const branches = await mapLimit(config.branches, async name => {
  const commit = await api(`commits/${encodeURIComponent(name)}`);
  const tree = await api(`git/trees/${commit.commit.tree.sha}?recursive=1`);
  if (tree.truncated) throw new Error(`Árbol de ${name} incompleto; no se pueden verificar las fuentes.`);
  const paths = new Set(tree.tree.filter(node => node.type === 'blob').map(node => node.path));
  const manual = paths.has('docs/corpus/MANUAL-ANOTACION.md') ? 'docs/corpus/MANUAL-ANOTACION.md' : 'docs/datos-etica/MANUAL-ANOTACION.md';
  const corpus = paths.has('docs/corpus/METODO-CREACION-CORPUS.md') ? 'docs/corpus/METODO-CREACION-CORPUS.md' : 'docs/datos-etica/METODO-CREACION-CORPUS.md';
  const sourcePaths = new Set(['docs/propuesta/PLAN-DE-TRABAJO.md', 'docs/GLOSARIO.md', 'docs/gestion/MAPA-DECISIONES.md',
    'docs/gestion/METODO-DE-TRABAJO.md', 'docs/ingenieria/ARQUITECTURA.md', 'docs/evaluacion/METRICAS.md', manual, corpus,
    ...(name === 'laboratorio-main' ? ['docs/investigacion/GUIA-CORRIDA-LABORATORIO.md'] : []),
    ...briefs.briefs.filter(brief => brief.branch === name).flatMap(brief => brief.sources.map(source => source.path))]);
  const documents = Object.fromEntries(await mapLimit([...sourcePaths].filter(file => paths.has(file)), async file => {
    const node = tree.tree.find(node => node.path === file);
    const blob = await api(`git/blobs/${node.sha}`);
    const content = Buffer.from(blob.content, 'base64').toString('utf8');
    return [file, { hash: hash(content), content, url: `https://github.com/${config.repository}/blob/${commit.sha}/${file}` }];
  }));
  const plan = documents['docs/propuesta/PLAN-DE-TRABAJO.md'];
  const glossaryDoc = documents['docs/GLOSARIO.md'];
  const decisionsDoc = documents['docs/gestion/MAPA-DECISIONES.md'];
  if (!plan || !glossaryDoc || !decisionsDoc) throw new Error(`Falta una fuente primaria en ${name}.`);
  const timelineText = section(plan.content, /11\. Cronograma/);
  const timeline = table(timelineText).filter(row => row.length >= 2).map(([date, goal]) => ({ date, goal }));
  return { name, sha: commit.sha, committedAt: commit.commit.committer.date,
    documents, paths: [...paths].filter(file => /^(docs|experiments)\//.test(file)),
    timeline, timelineProposed: /propuesta sin discutir/i.test(timelineText),
    glossary: glossary(glossaryDoc.content, config.glossaryTerms), decisions: decisions(decisionsDoc.content),
    briefs: Object.fromEntries(issues.map(issue => [issue.number, enrichBrief(briefs.briefs.find(brief => brief.branch === name && brief.issue === issue.number), issue, dependencies[issue.number], documents)])) };
});
const milestones = rawMilestones.map(milestone => ({ number: milestone.number, title: milestone.title,
  description: milestone.description ?? '', state: milestone.state, dueAt: milestone.due_on, url: milestone.html_url,
  open: allIssues.filter(issue => issue.milestone?.number === milestone.number && issue.state === 'open').length,
  closed: allIssues.filter(issue => issue.milestone?.number === milestone.number && issue.state === 'closed').length
})).sort((a,b) => a.number - b.number);
const issueByNumber = Object.fromEntries(allIssues.map(issue => [issue.number, issue]));
const roadmap = {
  ...roadmapRaw,
  parallelFronts: roadmapRaw.parallelFronts.map(front => ({
    ...front,
    issueItems: front.issues.map(num => {
      const issue = allIssues.find(i => i.number === num);
      const pendingBlockers = (dependencies[num] ?? []).filter(item => item.state === 'open');
      return issue ? {
        number: issue.number,
        title: issue.title,
        state: issue.state,
        milestone: issue.milestone?.number ?? null,
        assignees: (issue.assignees || []).map(a => a.login || a),
        blockersCount: pendingBlockers.length,
        url: issue.html_url || `https://github.com/${config.repository}/issues/${num}`
      } : {
        number: num,
        title: `#${num}`,
        state: 'unknown',
        milestone: null,
        assignees: [],
        blockersCount: 0,
        url: `https://github.com/${config.repository}/issues/${num}`
      };
    })
  })),
  suspendedFront: roadmapRaw.suspendedFront ? {
    ...roadmapRaw.suspendedFront,
    issues: (roadmapRaw.suspendedFront.issues || []).map(iss => {
      const match = allIssues.find(i => i.number === iss.number);
      return {
        ...iss,
        state: match?.state ?? 'unknown',
        stateReason: match?.state_reason ?? null,
        title: match ? match.title : iss.title
      };
    })
  } : undefined
};
// Grafo de entregas: nodos = issues de los frentes editoriales + los bloqueos que
// referencian (incluidos cerrados, con state_reason para distinguir completed de
// not_planned). Aristas = dependencias nativas de GitHub, nunca texto narrativo.
const frontOfIssue = new Map();
for (const front of roadmapRaw.parallelFronts) for (const num of front.issues) frontOfIssue.set(num, front.id);
const graphed = new Set(frontOfIssue.keys());
for (const num of [...graphed]) for (const dep of dependencies[num] ?? []) graphed.add(dep.number);
const graphNodes = [...graphed].map(num => {
  const issue = issueByNumber[num];
  const deps = dependencies[num] ?? [];
  return {
    id: `i${num}`, kind: 'issue', number: num,
    title: issue?.title ?? `Issue #${num}`,
    state: issue?.state ?? 'unknown',
    stateReason: issue?.state_reason ?? null,
    milestone: issue?.milestone?.number ?? null,
    assignees: (issue?.assignees ?? []).map(person => person.login ?? person),
    url: issue?.html_url ?? `https://github.com/${config.repository}/issues/${num}`,
    front: frontOfIssue.get(num) ?? 'concluido',
    openBlockers: deps.filter(dep => dep.state === 'open').map(dep => dep.number),
    /* Condiciones documentales previas (p. ej. D06 para #39): no son bloqueos
     * nativos de GitHub ni aristas del grafo; restringen la ejecución libre. */
    conditions: (roadmapRaw.issueConditions ?? {})[num] ?? []
  };
});
const suspended = roadmapRaw.suspendedFront;
if (suspended) graphNodes.push({
  id: 'laboratorio', kind: 'paused', title: suspended.title,
  state: 'closed', stateReason: 'not_planned', milestone: null, assignees: [],
  url: suspended.evidence?.commentUrl ?? `https://github.com/${config.repository}/issues`,
  front: 'laboratorio', openBlockers: [], conditions: [], issueCount: (suspended.issues ?? []).length
});
const graphEdges = [];
for (const num of graphed) for (const dep of dependencies[num] ?? []) {
  const blocker = issueByNumber[dep.number];
  graphEdges.push({ id: `e${dep.number}-${num}`, source: `i${dep.number}`, target: `i${num}`, kind: 'dependency',
    state: !blocker ? 'unknown' : blocker.state === 'open' ? 'pending' : blocker.state_reason === 'not_planned' ? 'not_planned' : 'satisfied' });
}
if (suspended?.resumeFromIssue && graphed.has(suspended.resumeFromIssue)) {
  graphEdges.push({ id: 'e-resume-lab', source: `i${suspended.resumeFromIssue}`, target: 'laboratorio',
    kind: 'conditional', state: 'conditional' });
}
roadmap.graph = { nodes: graphNodes, edges: graphEdges, edgeNotes: roadmapRaw.edgeNotes ?? {} };
// Diferencia de fuentes consultadas entre ramas (misma lista de documentos).
const branchDiff = branches.length === 2 ? (() => {
  const paths = new Set([...Object.keys(branches[0].documents), ...Object.keys(branches[1].documents)]);
  const differing = [...paths].filter(file => branches[0].documents[file]?.hash !== branches[1].documents[file]?.hash).sort();
  return { base: branches[0].name, other: branches[1].name, differing, total: paths.size };
})() : null;
// Adopción local (PR #58, 2026-10-08): la vista de arquitectura toma las
// decisiones del MAPA del árbol de trabajo, que puede diferir de las ramas
// remotas publicadas. Se declara su procedencia; no se disfraza de main.
const adoption = await readFile(path.join(root, '../docs/gestion/MAPA-DECISIONES.md'), 'utf8')
  .then(content => ({
    source: 'docs/gestion/MAPA-DECISIONES.md (árbol de trabajo; adopción local del contenido del PR #58, 2026-10-08)',
    hash: hash(content),
    decisions: decisions(content)
  }))
  .catch(() => null);
const snapshot = { version: 1, repository: config.repository, generatedAt: new Date().toISOString(),
  defaultBranch: config.defaultBranch, issues, milestones, dependencies, branches, roadmap, branchDiff, adoption };
await mkdir(path.join(root, 'dist'), { recursive: true });
if (!process.argv.includes('--data-only')) {
  await cp(path.join(root, 'public'), path.join(root, 'dist'), { recursive: true });
  try {
    await cp(path.join(root, 'node_modules/cytoscape/dist/cytoscape.esm.min.mjs'), path.join(root, 'dist/cytoscape.esm.min.js'));
    await cp(path.join(root, 'node_modules/cytoscape/LICENSE'), path.join(root, 'dist/cytoscape.LICENSE.txt'));
  } catch {
    throw new Error('Falta el bundle de cytoscape. Ejecutá `npm install` en ayuda-memoria antes de generar.');
  }
  // Apartado estático: la visualización de arquitectura (PR #58) viaja con el sitio.
  // Si la carpeta no existe en la revisión, se avisa y no se corta el build.
  const arquitecturaSrc = path.join(root, '../docs/ingenieria/arquitectura-web');
  try {
    await cp(arquitecturaSrc, path.join(root, 'dist/arquitectura'), { recursive: true });
    console.log('Apartado /arquitectura/ copiado desde docs/ingenieria/arquitectura-web.');
  } catch {
    console.warn('docs/ingenieria/arquitectura-web no existe en esta revisión: se publica sin /arquitectura/.');
  }
}
await writeFile(path.join(root, 'dist/data.json'), JSON.stringify(snapshot));
console.log(`Generado: ${issues.length} issues, ${branches.length} ramas. ${branches.map(branch => `${branch.name}@${branch.sha.slice(0,7)}`).join(' · ')}`);
