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
const snapshot = { version: 1, repository: config.repository, generatedAt: new Date().toISOString(),
  defaultBranch: config.defaultBranch, issues, milestones, dependencies, branches, roadmap };
await mkdir(path.join(root, 'dist'), { recursive: true });
if (!process.argv.includes('--data-only')) {
  await cp(path.join(root, 'public'), path.join(root, 'dist'), { recursive: true });
  // Apartado estático: la visualización de arquitectura vive en docs/ y viaja con el sitio.
  // Si la carpeta no existe en la rama (ej. checkout viejo de laboratorio-main), se avisa y no se corta el build.
  const arquitecturaSrc = path.join(root, '../docs/ingenieria/arquitectura-web');
  try {
    await cp(arquitecturaSrc, path.join(root, 'dist/arquitectura'), { recursive: true });
    console.log('Apartado /arquitectura/ copiado desde docs/ingenieria/arquitectura-web.');
  } catch {
    console.warn('Sin docs/ingenieria/arquitectura-web en esta revisión: se publica sin el apartado /arquitectura/.');
  }
}
await writeFile(path.join(root, 'dist/data.json'), JSON.stringify(snapshot));
console.log(`Generado: ${issues.length} issues, ${branches.length} ramas. ${branches.map(branch => `${branch.name}@${branch.sha.slice(0,7)}`).join(' · ')}`);
