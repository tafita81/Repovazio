// app/api/skills/route.js
// Sistema de Skills Eternas -- aprende, melhora e evolui sozino
export const runtime = 'edge';
export const maxDuration = 300;
const V = 'SKILLS-V1-2026-04-28';
const REPO = 'tafita81/Repovazio';
const supa = (path, opts = {}) => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  return fetch(`${url}${path}`, { ...opts, headers: { 'apikey': key, 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json', 'Prefer': 'return=representation', ...(opts.headers || {}) } });
};
const supaGet = async (t, q = '') => (await supa(`/rest/v1/${t}?${q}`)).json();
const supaUpsert = async (t, d) => (await supa(`/rest/v1/${t}`, { method: 'POST', headers: { 'Prefer': 'resolution=merge-duplicates,return=representation' }, body: JSON.stringify(d) })).json();
const supaPatch = async (t, q, d) => (await supa(`/rest/v1/${t}?${q}`, { method: 'PATCH', body: JSON.stringify(d) })).json();
const supaDelete = async (t, q) => (await supa(`/rest/v1/${t}?${q}`, { method: 'DELETE' })).json();
const gh = async (path, method = 'GET', data) => {
  const url = path.startsWith('http') ? path : `https://api.github.com/repos/${REPO}${path}`;
  const r = await fetch(url, { method, headers: { 'Authorization': `Bearer ${process.env.GH_PAT || ''}`, 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json' }, body: data ? JSON.stringify(data) : undefined });
  const d = await r.json(); if (!r.ok) throw new Error((d.message || JSON.stringify(d)).substring(0, 200)); return d;
};
async function callAI(prompt, sys = '', max = 2000) {
  const keys = [];
  if (process.env.GROQ_API_KEY) keys.push(process.env.GROQ_API_KEY);
  for (let i = 2; i <= 5; i++) { const k = process.env[`GROQ_KEY_${i}`]; if (k) keys.push(k); }
  for (const key of keys) {
    try {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', { method: 'POST', headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' }, body: JSON.stringify({ model: 'llama-3.3-70b-versatile', messages: [...(sys ? [{ role: 'system', content: sys }] : []), { role: 'user', content: prompt }], max_tokens: max, temperature: 0.3 }) });
      if (r.ok) { const d = await r.json(); return d.choices[0].message.content; }
    } catch { continue; }
  }
  if (process.env.GEMINI_API_KEY) {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: max } }) });
    if (r.ok) { const d = await r.json(); return d.candidates?.[0]?.content?.parts?.[0]?.text; }
  }
  throw new Error('Nenhum AI disponível');
}
async function improveSkill(skill) {
  const prompt = `Voc é um otimizador de skills de IA. Melhore esta skill com base nos seguintes critérios:
1. Adicione exemplos práticos de uso
2. Melhore as instruções para serem mais claras
3. Adicione cases de erro e como lidar
4. Amplie o escopo de quando deve ser ativada
5. Mantenha em formato Markdown compacto (< 200 linhas)

SKILL ATUAL (versão ${skill.version}):
Nome: ${skill.name}
Gatilhos: ${skill.triggers}
Conteúdo:
${skill.content.substring(0, 3000)}

Retorne APENAS o conteúdo melhorado, sem introdução.`;
  const improved = await callAI(prompt, 'Você é um otimizador especialista em skills de IA. Retorne APENAS o conteúdo melhorado.', 4000);
  return improved;
}
async function synthesizeSkillFromWeb(topic) {
  const sources = [
    `https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/README.md`,
    `https://raw.githubusercontent.com/e2b-dev/awesome-ai-agents/main/README.md`,
  ];
  let webContent = '';
  for (const url of sources) {
    try { const d = await fetch(url, { signal: AbortSignal.timeout(5000) }); const r = await fetch(url, { signal: AbortSignal.timeout(5000) }); if (r.ok) { webContent += (await r.text()).substring(0, 1000); break; } } catch { }
  }
  const prompt = `Crie uma skill de IA completa sobre: "${topic}"\n${webContent ? `\nConteúdo de referência encontrado:\n${webContent.substring(0, 2000)}` : ''}\nFormato obrigatório:\n# SKILL: ${topic}\n\n## Quando usar\n[descreva os gatilhos e situações ]\n\n## Como usar\n[instruções passo a passo]\n\n## Exemplos\n[exemplos práticos]\n\n## Erros comuns e soluções \n[
]troubleshooting]\n\n## Integração com outros sistemas\n[como combinar com outras skills]\nMáximo 150 linhas. Seja prático e específico para o projeto psicologia.doc v7.`;
  return await callAI(prompt, '', 3000);
}
export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const acao = searchParams.get('acao') || 'listar';
  const id = searchParams.get('id');
  const query = searchParams.get('q');
  switch (acao) {
    case 'listar': { const skills = await supaGet('ia_skills', 'order=score.desc,updated_at.desc&limit=50'); return Response.json({ skills: Array.isArray(skills) ? skills : [], total: Array.isArray(skills) ? skills.length : 0, version: V }); }
    case 'buscar': { if (!query) return Response.json({ erro: 'Parâmetro ?q= obrigatório' }, { status: 400 }); const skills = await supaGet('ia_skills', `name=ilike.%25${query}%25&order=score.desc&limit=10`); return Response.json({ skills: Array.isArray(skills) ? skills : [] }); }
    case 'ativar': { if (!id) return Response.json({ erro: 'Parâmetro ?id= obrigatório' }, { status: 400 }); const skills = await supaGet('ia_skills', `id=eq.${id}`); const skill = Array.isArray(skills) ? skills[0] : null; if (!skill) return Response.json({ erro: 'Skill não encontrada' }, { status: 404 }); await supaPatch('ia_skills', `id=eq.${id}`, { usos: (skill.usos || 0) + 1, last_used: new Date().toISOString() }); return Response.json({ skill, conteudo: skill.content }); }
    case 'melhorar_todas': { const skills = await supaGet('ia_skills', 'order=score.asc&limit=1&active=eq.true'); const skill = Array.isArray(skills) ? skills[0] : null; if (!skill) return Response.json({ resultado: 'Nenhuma skill para melhorar' }); const improved = await improveSkill(skill); await supaPatch('ia_skills', `id=eq.${skill.id}`, { content: improved, version: (skill.version || 1) + 1, score: Math.min(100, (skill.score || 50) + 5), updated_at: new Date().toISOString() }); return Response.json({ melhorada: skill.name, nova_versao: (skill.version || 1) + 1 }); }
    default: return Response.json({ erro: 'Ação desconhecida' }, { status: 400 });
  }
}
export async function POST(req) {
  const body = await req.json();
  const { acao } = body;
  switch (acao) {
    case 'criar': { const { name, content, triggers, source_url, categoria, active = true } = body; if (!name || !content) return Response.json({ erro: 'name e content obrigatórios' }, { status: 400 }); const skill = await supaUpsert('ia_skills', { name, content, triggers: triggers || name, categoria: categoria || 'geral', source_url, version: 1, score: 50, active, usos: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }); return Response.json({ criada: skill }); }
    case 'importar_url': { const { url, name, categoria } = body; if (!url) return Response.json({ erro: 'url obrigatória' }, { status: 400 }); const fetched = await fetch(url, { headers: { 'User-Agent': 'psicologia-doc-v7/1.0' } }); if (!fetched.ok) return Response.json({ erro: `HTTP ${fetched.status}: ${url}` }, { status: 400 }); const content = (await fetched.text()).substring(0, 10000); const skillName = name || url.split('/').pop().replace(/\.(md|txt)$/, ''); await supaUpsert('ia_skills', { name: skillName, content, triggers: skillName, categoria: categoria || 'importada', source_url: url, version: 1, score: 50, active: true, usos: 0, created_at: new Date().toISOString(), updated_at: new Date().toISOString() }); return Response.json({ importada: skillName, tamanho: content.length }); }
    case 'sintetizar': { const { topic, categoria } = body; if (!topic) return Response.json({ erro: 'topic obrigatório' }, { status: 400 }); const content