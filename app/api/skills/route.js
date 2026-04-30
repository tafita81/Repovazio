// app/api/skills/route.js
// Sistema de Skills Eternas — aprende, melhora e evolui sozinho
// Compatível com ZIPs do Claude, Manus e outros

export const runtime = 'edge';
export const maxDuration = 300;
const V = 'SKILLS-V1-2026-04-28';
const REPO = 'tafita81/Repovazio';

// ── SUPABASE ──────────────────────────────────────────────────────────────
const supa = (path, opts = {}) => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  return fetch(`${url}${path}`, {
    ...opts, headers: {
      'apikey': key, 'Authorization': `Bearer ${key}`,
      'Content-Type': 'application/json', 'Prefer': 'return=representation',
      ...(opts.headers || {})
    }
  });
};
const supaGet = async (t, q = '') => (await supa(`/rest/v1/${t}?${q}`)).json();
const supaUpsert = async (t, d) => (await supa(`/rest/v1/${t}`, {
  method: 'POST', headers: { 'Prefer': 'resolution=merge-duplicates,return=representation' }, body: JSON.stringify(d)
})).json();
const supaPatch = async (t, q, d) => (await supa(`/rest/v1/${t}?${q}`, { method: 'PATCH', body: JSON.stringify(d) })).json();
const supaDelete = async (t, q) => (await supa(`/rest/v1/${t}?${q}`, { method: 'DELETE' })).json();

// ── AI CALL ───────────────────────────────────────────────────────────────
async function callAI(prompt, sys = '', max = 2000) {
  const keys = [];
  if (process.env.GROQ_API_KEY) keys.push(process.env.GROQ_API_KEY);
  for (let i = 2; i <= 5; i++) { const k = process.env[`GROQ_KEY_${i}`]; if (k) keys.push(k); }

  for (const key of keys) {
    try {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: [...(sys ? [{ role: 'system', content: sys }] : []), { role: 'user', content: prompt }],
          max_tokens: max, temperature: 0.3
        })
      });
      if (r.ok) { const d = await r.json(); return d.choices[0].message.content; }
    } catch { continue; }
  }

  // Gemini fallback
  if (process.env.GEMINI_API_KEY) {
    const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${process.env.GEMINI_API_KEY}`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: max } })
    });
    if (r.ok) { const d = await r.json(); return d.candidates?.[0]?.content?.parts?.[0]?.text; }
  }
  throw new Error('Nenhum AI disponível');
}

// ── FETCH SKILL DA INTERNET ───────────────────────────────────────────────
async function fetchSkillFromUrl(url) {
  const r = await fetch(url, { headers: { 'User-Agent': 'psicologia-doc-v7/1.0' } });
  if (!r.ok) throw new Error(`HTTP ${r.status}: ${url}`);
  const content = await r.text();
  // Se é ZIP — instrução para futuro (Railway com suporte a unzip)
  if (url.endsWith('.zip')) return { tipo: 'zip', content, url };
  return { tipo: 'markdown', content, url };
}

// ── SKILL IMPROVER (AI melhora a skill) ──────────────────────────────────
async function improveSkill(skill) {
  const prompt = `Você é um otimizador de skills de IA. Melhore esta skill com base nos seguintes critérios:
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

Retorne APENAS o conteúdo melhorado da skill, sem introdução ou explicação extra.`;

  const improved = await callAI(prompt, 'Você é um otimizador especialista em skills de IA. Retorne APENAS o conteúdo melhorado.', 4000);
  return improved;
}

// ── SKILL SYNTHESIZER (cria nova skill da internet) ───────────────────────
async function synthesizeSkillFromWeb(topic) {
  // Buscar conhecimento da internet via Together.ai ou web search
  const sources = [
    `https://raw.githubusercontent.com/anthropics/anthropic-cookbook/main/skills/${topic}.md`,
    `https://raw.githubusercontent.com/awslabs/manus-skills/main/${topic}/SKILL.md`,
  ];

  let webContent = '';
  for (const url of sources) {
    try { const d = await fetchSkillFromUrl(url); webContent += d.content + '\n\n'; break; } catch { }
  }

  const prompt = `Crie uma skill de IA completa sobre: "${topic}"
${webContent ? `\nConteúdo de referência encontrado:\n${webContent.substring(0, 2000)}` : ''}

Formato obrigatório:
# SKILL: ${topic}

## Quando usar
[descreva os gatilhos e situações]

## Como usar
[instruções passo a passo]

## Exemplos
[exemplos práticos]

## Erros comuns e soluções
[troubleshooting]

## Integração com outros sistemas
[como combinar com outras skills]

Máximo 150 linhas. Seja prático e específico para o projeto psicologia.doc v7.`;

  return await callAI(prompt, '', 3000);
}

// ── ENDPOINTS ─────────────────────────────────────────────────────────────

export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const acao = searchParams.get('acao') || 'listar';
  const id = searchParams.get('id');
  const query = searchParams.get('q');

  switch (acao) {
    case 'listar': {
      const skills = await supaGet('ia_skills', 'order=score.desc,updated_at.desc&limit=50');
      return Response.json({ skills: Array.isArray(skills) ? skills : [], total: Array.isArray(skills) ? skills.length : 0, version: V });
    }

    case 'buscar': {
      if (!query) return Response.json({ erro: 'Parâmetro ?q= obrigatório' }, { status: 400 });
      const skills = await supaGet('ia_skills', `name=ilike.%25${query}%25&order=score.desc&limit=10`);
      return Response.json({ skills: Array.isArray(skills) ? skills : [] });
    }

    case 'ativar': {
      if (!id) return Response.json({ erro: 'Parâmetro ?id= obrigatório' }, { status: 400 });
      const skills = await supaGet('ia_skills', `id=eq.${id}`);
      const skill = Array.isArray(skills) ? skills[0] : null;
      if (!skill) return Response.json({ erro: 'Skill não encontrada' }, { status: 404 });
      // Incrementar uso
      await supaPatch('ia_skills', `id=eq.${id}`, { usos: (skill.usos || 0) + 1, last_used: new Date().toISOString() });
      return Response.json({ skill, conteudo: skill.content });
    }

    case 'melhorar_todas': {
      // Melhora a skill com menor score
      const skills = await supaGet('ia_skills', 'order=score.asc&limit=1&active=eq.true');
      const skill = Array.isArray(skills) ? skills[0] : null;
      if (!skill) return Response.json({ resultado: 'Nenhuma skill para melhorar' });
      const improved = await improveSkill(skill);
      await supaPatch('ia_skills', `id=eq.${skill.id}`, {
        content: improved, version: (skill.version || 1) + 1,
        score: Math.min(100, (skill.score || 50) + 5),
        updated_at: new Date().toISOString()
      });
      return Response.json({ melhorada: skill.name, nova_versao: (skill.version || 1) + 1 });
    }

    default:
      return Response.json({ erro: 'Ação desconhecida' }, { status: 400 });
  }
}

export async function POST(req) {
  const body = await req.json();
  const { acao } = body;

  switch (acao) {

    case 'criar': {
      const { name, content, triggers, categoria, active = true } = body;
      if (!name || !content) return Response.json({ erro: 'name e content obrigatórios' }, { status: 400 });
      const skill = await supaUpsert('ia_skills', {
        name, content, triggers: triggers || name, categoria: categoria || 'geral',
        version: 1, score: 50, active, usos: 0,
        created_at: new Date().toISOString(), updated_at: new Date().toISOString()
      });
      return Response.json({ criada: skill });
    }

    case 'importar_url': {
      const { url, name, categoria } = body;
      if (!url) return Response.json({ erro: 'url obrigatória' }, { status: 400 });
      const fetched = await fetchSkillFromUrl(url);
      const skillName = name || url.split('/').pop().replace(/\.(md|txt)$/, '');
      const skill = await supaUpsert('ia_skills', {
        name: skillName, content: fetched.content.substring(0, 10000),
        triggers: skillName, categoria: categoria || 'importada',
        source_url: url, version: 1, score: 50, active: true, usos: 0,
        created_at: new Date().toISOString(), updated_at: new Date().toISOString()
      });
      return Response.json({ importada: skillName, tamanho: fetched.content.length });
    }

    case 'importar_zip': {
      // Suporte a ZIPs de skills do Claude/Manus
      const { zip_base64, nome_pasta } = body;
      if (!zip_base64) return Response.json({ erro: 'zip_base64 obrigatório' }, { status: 400 });
      // Parsear ZIP no Railway browser agent se disponível
      const browserUrl = process.env.BROWSER_AGENT_URL;
      if (browserUrl) {
        const r = await fetch(browserUrl.replace('/execute', '/parse-zip'), {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ zip_base64 })
        }).catch(() => null);
        if (r?.ok) {
          const files = await r.json();
          const skillFile = files.find(f => f.name === 'SKILL.md' || f.name === 'skill.md');
          if (skillFile) {
            await supaUpsert('ia_skills', {
              name: nome_pasta || 'skill-importada', content: skillFile.content,
              triggers: nome_pasta || 'skill-importada', categoria: 'zip-importado',
              version: 1, score: 50, active: true, usos: 0,
              created_at: new Date().toISOString(), updated_at: new Date().toISOString()
            });
            return Response.json({ importada: nome_pasta, arquivos: files.length });
          }
        }
      }
      return Response.json({ aviso: 'ZIP importado mas parse requer Browser Agent no Railway', zip_base64_recebido: zip_base64.length > 0 });
    }

    case 'sintetizar': {
      const { topic, categoria } = body;
      if (!topic) return Response.json({ erro: 'topic obrigatório' }, { status: 400 });
      const content = await synthesizeSkillFromWeb(topic);
      const skill = await supaUpsert('ia_skills', {
        name: topic, content, triggers: topic, categoria: categoria || 'sintetizada',
        version: 1, score: 60, active: true, usos: 0,
        created_at: new Date().toISOString(), updated_at: new Date().toISOString()
      });
      return Response.json({ sintetizada: topic, linhas: content.split('\n').length });
    }

    case 'avaliar': {
      // Registrar feedback de uso de uma skill
      const { skill_id, sucesso, feedback } = body;
      const skills = await supaGet('ia_skills', `id=eq.${skill_id}`);
      const skill = Array.isArray(skills) ? skills[0] : null;
      if (!skill) return Response.json({ erro: 'Skill não encontrada' }, { status: 404 });
      const newScore = sucesso
        ? Math.min(100, (skill.score || 50) + 2)
        : Math.max(0, (skill.score || 50) - 3);
      await supaPatch('ia_skills', `id=eq.${skill_id}`, {
        score: newScore, usos: (skill.usos || 0) + 1,
        last_feedback: feedback || '', last_used: new Date().toISOString()
      });
      return Response.json({ score_novo: newScore, skill: skill.name });
    }

    case 'aprender_conversa': {
      // Extrai nova skill de uma conversa
      const { conversa, session_id } = body;
      if (!conversa || conversa.length < 100) return Response.json({ resultado: 'Conversa muito curta' });
      const prompt = `Analise esta conversa e extraia UMA nova skill ou melhoria para skills existentes.

CONVERSA:
${conversa.substring(0, 3000)}

Se identificou uma nova skill, retorne JSON:
{"action":"criar","name":"nome-da-skill","content":"# conteúdo em markdown","triggers":"palavras-gatilho","categoria":"categoria"}

Se não há nova skill, retorne:
{"action":"nenhuma"}

Retorne APENAS o JSON.`;

      const result = await callAI(prompt, 'Analisa conversas e extrai skills. Retorna APENAS JSON.', 1000);
      const match = result?.match(/\{[\s\S]*\}/);
      if (!match) return Response.json({ resultado: 'Nenhuma skill extraída' });

      const parsed = JSON.parse(match[0]);
      if (parsed.action === 'criar' && parsed.name && parsed.content) {
        await supaUpsert('ia_skills', {
          name: parsed.name, content: parsed.content,
          triggers: parsed.triggers || parsed.name, categoria: parsed.categoria || 'auto-aprendida',
          version: 1, score: 55, active: true, usos: 0,
          created_at: new Date().toISOString(), updated_at: new Date().toISOString()
        });
        return Response.json({ skill_criada: parsed.name });
      }
      return Response.json({ resultado: 'Nenhuma skill nova identificada' });
    }

    default:
      return Response.json({ erro: `Ação desconhecida: ${acao}` }, { status: 400 });
  }
}
