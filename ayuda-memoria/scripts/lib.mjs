import { createHash } from 'node:crypto';

export const hash = text => createHash('sha256').update(text).digest('hex');
export function plain(text = '') {
  return text.replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[*`]/g, '').replace(/^>\s?/gm, '').trim();
}
export function section(text, titlePattern) {
  const lines = text.split('\n');
  const start = lines.findIndex(line => /^#{2,3}\s/.test(line) && titlePattern.test(plain(line)));
  if (start < 0) return '';
  const level = lines[start].match(/^#+/)[0].length;
  let end = start + 1;
  while (end < lines.length && !(new RegExp(`^#{1,${level}} `)).test(lines[end])) end++;
  return lines.slice(start + 1, end).join('\n').trim();
}
export function table(text) {
  return text.split('\n').filter(line => line.trim().startsWith('|')).map(line =>
    line.trim().replace(/^\||\|$/g, '').split(/(?<!\\)\|/).map(cell => cell.trim().replace(/\\\|/g, '|'))
  ).filter(cells => !cells.every(cell => /^:?-+:?$/.test(cell))).slice(1);
}
export function glossary(text, terms) {
  return table(text).filter(row => terms.some(term => plain(row[0]).includes(term)))
    .map(([term, definition]) => ({ term: plain(term), definition }));
}
export function decisions(text) {
  return [...text.matchAll(/^### (D\d+) [—–-] (.+)\n([\s\S]*?)(?=^### |^## |$(?![\s\S]))/gm)].map(match => {
    const state = match[3].match(/^- \*\*Estado:\*\* (.+)/m)?.[1] ?? 'Estado no explicitado; consultar la fuente.';
    return { id: match[1], title: match[2], state: plain(state), open: !/^(resuelt[oa]|cerrad[oa]|.*resuelta)/i.test(plain(state)) };
  });
}
export function fingerprint(issue, blockers, sources, documents) {
  return hash(JSON.stringify({
    issue: { number: issue.number, title: issue.title, body: issue.body, updatedAt: issue.updatedAt,
      milestone: issue.milestone, assignees: issue.assignees, labels: issue.labels },
    blockers: blockers.map(({ number, state, title }) => ({ number, state, title })).sort((a,b) => a.number - b.number),
    sources: sources.map(({ path, anchor = '' }) => ({ path, anchor, hash: documents[path]?.hash ?? null }))
  }));
}
export function enrichBrief(brief, issue, blockers, documents) {
  if (!brief) return { status: 'missing', sources: [], fingerprint: null };
  const currentFingerprint = fingerprint(issue, blockers, brief.sources, documents);
  const missing = brief.sources.filter(source => !documents[source.path]);
  const status = missing.length ? 'missing-source' : brief.review?.fingerprint === currentFingerprint ? 'reviewed' : 'stale';
  return { ...brief, status, currentFingerprint, missing: missing.map(source => source.path) };
}
export function normalizeIssue(issue) {
  return { number: issue.number, title: issue.title, body: issue.body ?? '', url: issue.html_url,
    updatedAt: issue.updated_at, state: issue.state, milestone: issue.milestone?.number ?? null,
    assignees: issue.assignees.map(person => person.login), labels: issue.labels.map(label => label.name),
    goal: section(issue.body ?? '', /Resultado observable|Decisión a validar/i),
    done: section(issue.body ?? '', /Terminado cuando/i),
    context: section(issue.body ?? '', /Alcance y dependencias|Dependencias y alcance|Evidencia necesaria|Alcance y momento|Alcance/i) };
}
export function validateBriefs(file, branches) {
  if (file.version !== 1 || !Array.isArray(file.briefs)) throw new Error('Formato de briefs inválido.');
  const seen = new Set();
  for (const brief of file.briefs) {
    const id = `${brief.branch}:${brief.issue}`;
    if (!branches.includes(brief.branch) || !Number.isInteger(brief.issue) || seen.has(id)) throw new Error(`Identidad de brief inválida o repetida: ${id}`);
    seen.add(id);
    for (const field of ['goal', 'start', 'done']) if (typeof brief[field] !== 'string' || !brief[field].trim()) throw new Error(`${id}: falta ${field}`);
    if (!Array.isArray(brief.sources) || !brief.sources.length) throw new Error(`${id}: faltan fuentes`);
    for (const source of brief.sources) {
      if (!/^(docs|experiments)\//.test(source.path) || source.path.includes('..') || typeof source.why !== 'string' || !source.why.trim()) throw new Error(`${id}: fuente inválida`);
    }
  }
}
export function validateRoadmap(roadmap) {
  if (roadmap.version !== 1 || !Array.isArray(roadmap.parallelFronts) || !roadmap.suspendedFront || !roadmap.currentLocation) {
    throw new Error('Formato de roadmap inválido.');
  }
  for (const front of roadmap.parallelFronts) {
    if (!front.id || !front.name || !front.state || !Array.isArray(front.issues)) {
      throw new Error(`Frente inválido: ${front.id ?? 'sin id'}`);
    }
  }
}
