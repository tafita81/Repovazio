// app/api/ia-chat/route.js — V5 MÁXIMO ABSOLUTO
// Visão Gemini + Contexto 128k auto + Artefatos + Notion + Slack + Drive + Memória semântica pgvector

export const runtime = 'edge';
export const maxDuration = 300;
const V = 'IA-CHAT-V5-2026-04-27';
const REPO = 'tafita81/Repovazio';
const BASE = 'https://repovazio.vercel.app';

const SYSTEM = `Você é um assistente IA autônomo e completo do projeto psicologia.doc v7.
Canal @psicologiadoc, persona Daniela Coelho (reveal dia 261 ~31/12/2026), dono Rafael.
Repo tafita81/Repovazio, repovazio.vercel.app, Next.js 14 + Supabase + Groq.

CAPACIDADES COMPLETAS:
- GitHub: ler/criar/editar/deletar arquivos, histórico, branches
- Vercel: deployments, logs, status
- Supabase: queries, CRUD, schema completo
- Notion: ler/criar/editar páginas e databases
- Slack: enviar mensagens, ler canais
- Google Drive: ler/criar/buscar arquivos
- WhatsApp: membros, status, mensagens
- YouTube/Social: métricas, vídeos, performance
- Browser: automação via Playwright (Railway)
- Visão: analisar imagens e screenshots enviados
- Código: gerar, analisar, debugar, otimizar
- Artefatos: quando criar HTML/React/SVG, marcar com <ARTIFACT type="html"> para renderizar

ARTEFATOS: Se criar código HTML, React ou SVG para mostrar algo visual, envolva com:
<ARTIFACT type="html">
...código...
</ARTIFACT>
Isso renderiza o resultado inline na conversa.

Responda em PT-BR, direto, completo, autônomo.`;

// ── AI PROVIDERS ──────────────────────────────────────────────────────────
function getGroqKeys() {
  const k = [];
  if (process.env.GROQ_API_KEY) k.push({ id: 'groq-1', key: process.env.GROQ_API_KEY });
  for (let i = 2; i <= 20; i++) {
    const v = process.env[`GROQ_KEY_${i}`];
    if (v) k.push({ id: `groq-${i}`, key: v });
  }
  return k;
}

function countTokensApprox(messages) {
  return messages.reduce((acc, m) => acc + Math.ceil((m.content || '').length / 3.5), 0);
}

async function callGroq(messages, model, max, keyObj) {
  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${keyObj.key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model: model || 'llama-3.3-70b-versatile', messages, max_tokens: max, temperature: 0.7 })
  });
  if (r.status === 429) throw Object.assign(new Error('RATE_LIMIT'), { code: 429 });
  if (!r.ok) throw new Error(`Groq ${r.status}: ${(await r.text()).substring(0, 100)}`);
  const d = await r.json();
  return { text: d.choices[0].message.content, usage: d.usage };
}

async function callGemini(messages, max, imageBase64 = null, imageMime = null) {
  const key = process.env.GEMINI_API_KEY;
  if (!key) throw new Error('GEMINI_API_KEY ausente');
  const model = imageBase64 ? 'gemini-1.5-flash' : 'gemini-1.5-flash';
  const system = messages.find(m => m.role === 'system');
  const convMsgs = messages.filter(m => m.role !== 'system');

  const contents = convMsgs.map((m, i) => {
    const parts = [];
    // Adicionar imagem na última mensagem do usuário
    if (m.role === 'user' && i === convMsgs.length - 1 && imageBase64) {
      parts.push({ inline_data: { mime_type: imageMime || 'image/jpeg', data: imageBase64 } });
    }
    parts.push({ text: m.content });
    return { role: m.role === 'assistant' ? 'model' : 'user', parts };
  });

  const r = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${key}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        system_instruction: system ? { parts: [{ text: system.content }] } : undefined,
        contents,
        generationConfig: { maxOutputTokens: max, temperature: 0.7 }
      })
    }
  );
  if (!r.ok) throw new Error(`Gemini ${r.status}: ${(await r.text()).substring(0, 100)}`);
  const d = await r.json();
  const text = d.candidates?.[0]?.content?.parts?.[0]?.text;
  if (!text) throw new Error('Gemini sem resposta');
  return { text, usage: { total_tokens: d.usageMetadata?.totalTokenCount } };
}

async function callTogether(messages, max) {
  const key = process.env.TOGETHER_API_KEY;
  if (!key) throw new Error('TOGETHER_API_KEY ausente');
  const r = await fetch('https://api.together.xyz/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'meta-llama/Llama-3.3-70B-Instruct-Turbo-Free',
      messages, max_tokens: max, temperature: 0.7
    })
  });
  if (!r.ok) throw new Error(`Together ${r.status}`);
  const d = await r.json();
  return { text: d.choices[0].message.content, usage: d.usage };
}

async function callAI(messages, model, max, imageBase64 = null, imageMime = null) {
  const tokenCount = countTokensApprox(messages);
  const groqKeys = getGroqKeys();

  // Se tem imagem → Gemini Vision
  if (imageBase64) {
    try {
      const r = await callGemini(messages, max, imageBase64, imageMime);
      return { ...r, kid: 'gemini-vision', provider: 'gemini' };
    } catch (e) {
      // fallback sem imagem
    }
  }

  // Se contexto muito longo (>25k tokens) → Together.ai (128k)
  if (tokenCount > 25000 && process.env.TOGETHER_API_KEY) {
    try {
      const r = await callTogether(messages, max);
      return { ...r, kid: 'together-128k', provider: 'together' };
    } catch { }
  }

  // Groq paralelo
  if (groqKeys.length > 0) {
    try {
      if (groqKeys.length === 1) {
        const r = await callGroq(messages, model, max, groqKeys[0]);
        return { ...r, kid: groqKeys[0].id, provider: 'groq' };
      }
      const result = await Promise.any(groqKeys.map(async k => {
        const r = await callGroq(messages, model, max, k);
        return { ...r, kid: k.id, provider: 'groq' };
      }));
      return result;
    } catch { }
  }

  // Gemini fallback
  if (process.env.GEMINI_API_KEY) {
    try {
      const r = await callGemini(messages, max);
      return { ...r, kid: 'gemini-flash', provider: 'gemini' };
    } catch { }
  }

  // Together fallback
  if (process.env.TOGETHER_API_KEY) {
    const r = await callTogether(messages, max);
    return { ...r, kid: 'together-llama', provider: 'together' };
  }

  throw new Error('Todos os AI providers falharam');
}

// ── GITHUB ────────────────────────────────────────────────────────────────
const gh = (path, opts = {}) => fetch('https://api.github.com' + path, {
  ...opts, headers: { 'Authorization': `token ${process.env.GH_PAT}`, 'Accept': 'application/vnd.github.v3+json', 'Content-Type': 'application/json', ...(opts.headers || {}) }
});
const enc = t => { const b = new TextEncoder().encode(t); let o = ''; for (let i = 0; i < b.length; i += 8192) o += btoa(String.fromCharCode(...b.slice(i, i + 8192))); return o; };
const readFile = async p => { const r = await gh(`/repos/${REPO}/contents/${p}?ref=main`, { headers: { 'Accept': 'application/vnd.github.v3.raw' } }); if (!r.ok) throw new Error(`404: ${p}`); return r.text(); };
const listDir = async p => { const r = await gh(`/repos/${REPO}/contents/${p || ''}?ref=main`); const d = await r.json(); if (!Array.isArray(d)) throw new Error(`"${p}" não é pasta`); return d.sort((a, b) => (a.type === 'dir' ? -1 : 1) - (b.type === 'dir' ? -1 : 1) || a.name.localeCompare(b.name)); };
async function commitFile(fp, content, msg) {
  const ref = await (await gh(`/repos/${REPO}/git/ref/heads/main`)).json();
  const bc = await (await gh(`/repos/${REPO}/git/commits/${ref.object.sha}`)).json();
  const blob = await (await gh(`/repos/${REPO}/git/blobs`, { method: 'POST', body: JSON.stringify({ content: enc(content), encoding: 'base64' }) })).json();
  const tree = await (await gh(`/repos/${REPO}/git/trees`, { method: 'POST', body: JSON.stringify({ base_tree: bc.tree.sha, tree: [{ path: fp, mode: '100644', type: 'blob', sha: blob.sha }] }) })).json();
  const nc = await (await gh(`/repos/${REPO}/git/commits`, { method: 'POST', body: JSON.stringify({ message: msg, tree: tree.sha, parents: [ref.object.sha] }) })).json();
  await gh(`/repos/${REPO}/git/refs/heads/main`, { method: 'PATCH', body: JSON.stringify({ sha: nc.sha, force: false }) });
  return nc.sha;
}
async function deleteFile(fp) {
  const meta = await (await gh(`/repos/${REPO}/contents/${fp}?ref=main`)).json();
  if (!meta.sha) throw new Error(`NF: ${fp}`);
  const r = await gh(`/repos/${REPO}/contents/${fp}`, { method: 'DELETE', body: JSON.stringify({ message: `del ${fp} via ia-chat`, sha: meta.sha, branch: 'main' }) });
  const d = await r.json(); if (!r.ok) throw new Error(d.message);
  return d.commit?.sha?.substring(0, 7);
}

// ── SUPABASE ──────────────────────────────────────────────────────────────
const supa = (path, opts = {}) => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  return fetch(`${url}${path}`, { ...opts, headers: { 'apikey': key, 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json', 'Prefer': 'return=representation', ...(opts.headers || {}) } });
};
const supaGet = async (t, q = '') => (await supa(`/rest/v1/${t}?${q}&limit=50`)).json();
const supaInsert = async (t, d) => (await supa(`/rest/v1/${t}`, { method: 'POST', body: JSON.stringify(d) })).json();

// ── SEMANTIC MEMORY (pgvector) ─────────────────────────────────────────────
async function getEmbedding(text) {
  // Usar Together.ai para embeddings grátis
  if (process.env.TOGETHER_API_KEY) {
    const r = await fetch('https://api.together.xyz/v1/embeddings', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${process.env.TOGETHER_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'togethercomputer/m2-bert-80M-8k-retrieval', input: text.substring(0, 512) })
    });
    if (r.ok) { const d = await r.json(); return d.data?.[0]?.embedding; }
  }
  return null;
}

async function searchMemoriaSemantic(sid, query, limit = 5) {
  try {
    const embedding = await getEmbedding(query);
    if (!embedding) return [];
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const key = process.env.SUPABASE_SERVICE_KEY;
    const r = await fetch(`${url}/rest/v1/rpc/buscar_memoria_similar`, {
      method: 'POST',
      headers: { 'apikey': key, 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_session_id: sid, p_embedding: embedding, p_limit: limit })
    });
    return r.ok ? r.json() : [];
  } catch { return []; }
}

async function saveMemoriaSemantic(sid, role, content) {
  try {
    const embedding = await getEmbedding(content);
    await supaInsert('ia_chat_memoria', {
      session_id: sid, role, content: content.substring(0, 8000),
      embedding: embedding ? JSON.stringify(embedding) : null,
      created_at: new Date().toISOString()
    });
  } catch { }
}

async function loadMemoria(sid) {
  try {
    const rows = await supaGet('ia_chat_memoria', `session_id=eq.${sid}&order=created_at.desc&limit=40`);
    return Array.isArray(rows) ? rows.reverse().map(r => ({ role: r.role, content: r.content })) : [];
  } catch { return []; }
}

// ── NOTION CONNECTOR ──────────────────────────────────────────────────────
const notion = (path, opts = {}) => {
  const key = process.env.NOTION_TOKEN;
  if (!key) throw new Error('NOTION_TOKEN não configurado. Adicione no Vercel env vars.');
  return fetch(`https://api.notion.com/v1${path}`, {
    ...opts,
    headers: { 'Authorization': `Bearer ${key}`, 'Notion-Version': '2022-06-28', 'Content-Type': 'application/json', ...(opts.headers || {}) }
  });
};
async function notionSearch(query) {
  const r = await notion('/search', { method: 'POST', body: JSON.stringify({ query, page_size: 10 }) });
  if (!r.ok) throw new Error(`Notion ${r.status}: ${(await r.text()).substring(0, 100)}`);
  return r.json();
}
async function notionGetPage(id) {
  const [page, blocks] = await Promise.all([
    notion(`/pages/${id}`).then(r => r.json()),
    notion(`/blocks/${id}/children?page_size=50`).then(r => r.json())
  ]);
  return { page, blocks };
}
async function notionCreatePage(parentId, title, content) {
  const r = await notion('/pages', {
    method: 'POST',
    body: JSON.stringify({
      parent: { page_id: parentId },
      properties: { title: { title: [{ text: { content: title } }] } },
      children: content ? [{ object: 'block', type: 'paragraph', paragraph: { rich_text: [{ text: { content } }] } }] : []
    })
  });
  return r.json();
}

// ── SLACK CONNECTOR ────────────────────────────────────────────────────────
const slack = (path, opts = {}) => {
  const key = process.env.SLACK_TOKEN;
  if (!key) throw new Error('SLACK_TOKEN não configurado. Adicione no Vercel env vars.');
  return fetch(`https://slack.com/api${path}`, {
    ...opts,
    headers: { 'Authorization': `Bearer ${key}`, 'Content-Type': 'application/json', ...(opts.headers || {}) }
  });
};
async function slackSend(channel, text) {
  const r = await slack('/chat.postMessage', { method: 'POST', body: JSON.stringify({ channel, text }) });
  return r.json();
}
async function slackListChannels() {
  const r = await slack('/conversations.list?limit=20');
  return r.json();
}
async function slackGetHistory(channel, limit = 10) {
  const r = await slack(`/conversations.history?channel=${channel}&limit=${limit}`);
  return r.json();
}

// ── GOOGLE DRIVE CONNECTOR ─────────────────────────────────────────────────
async function driveSearch(query) {
  const key = process.env.GOOGLE_API_KEY;
  if (!key) throw new Error('GOOGLE_API_KEY não configurado.');
  const r = await fetch(`https://www.googleapis.com/drive/v3/files?q=${encodeURIComponent(query)}&key=${key}&pageSize=10&fields=files(id,name,mimeType,webViewLink,modifiedTime)`);
  return r.json();
}

// ── CACHE ─────────────────────────────────────────────────────────────────
async function getCached(key) {
  try {
    const rows = await supaGet('ia_cache', `cache_key=eq.${encodeURIComponent(key)}&expires_at=gt.${new Date().toISOString()}`);
    return Array.isArray(rows) && rows[0] ? rows[0].value : null;
  } catch { return null; }
}
async function setCache(key, value, ttlMin = 5) {
  try { await supaInsert('ia_cache', { cache_key: key, value, expires_at: new Date(Date.now() + ttlMin * 60000).toISOString() }); } catch { }
}

// ── DETECT TOOLS ──────────────────────────────────────────────────────────
function detectTools(msg) {
  const t = msg.toLowerCase();
  const tools = new Set();
  if (/\bstatus\b|\bsistema\b|\bsa[uú]de\b/.test(t)) tools.add('status');
  if (/\b(ls|listar)\b.*\b(arq|pasta|dir)\b|\bls\s+[\w/]/.test(t)) tools.add('gh_ls');
  if (/\b(ler|cat|ver)\b.*\b(arq|código)\b/.test(t)) tools.add('gh_read');
  if (/\b(criar|create)\b.*\b(arq|file)\b/.test(t)) tools.add('gh_create');
  if (/\b(editar|modificar|alterar|mudar)\b/.test(t)) tools.add('gh_edit');
  if (/\b(deletar|apagar|rm)\b.*\b(arq)\b/.test(t)) tools.add('gh_delete');
  if (/\bcommit|histórico|git log\b/.test(t)) tools.add('gh_history');
  if (/\bdeploy\b/.test(t) && !/\bcriar\b/.test(t)) tools.add('deploy');
  if (/\bnotion\b|\bpágina\b.*\bnotion\b|\bbuscar\b.*\bnotion\b/.test(t)) tools.add('notion_search');
  if (/\bcriar\b.*\bnotion\b|\bnotion\b.*\bcriar\b/.test(t)) tools.add('notion_create');
  if (/\bslack\b|\bcanal\b.*\bslack\b/.test(t)) tools.add('slack_info');
  if (/\benviar\b.*\bslack\b|\bslack\b.*\benviar\b/.test(t)) tools.add('slack_send');
  if (/\bdrive\b|\bgoogle\s+drive\b|\bbuscar\b.*\bdrive\b/.test(t)) tools.add('drive_search');
  if (/\bsupabase\b|\btabela\b|\bbanco\b/.test(t)) tools.add('db_info');
  if (/\bwhatsapp\b|\bwa\b/.test(t)) tools.add('whatsapp');
  if (/\byoutube\b|\bcanal\b|\bvídeos\b/.test(t)) tools.add('youtube');
  if (/\binstagram\b|\btiktok\b|\bredes\b/.test(t)) tools.add('social');
  if (/\bnavegar\b|\bbrowser\b|\bscreenshot\b|\bclicar\b|\bautomatizar\b/.test(t)) tools.add('browser');
  if (/\blembra\b|\bmemória\b|\bconversa anterior\b/.test(t)) tools.add('memoria_semantica');
  return [...tools];
}

// ── RUN TOOL ──────────────────────────────────────────────────────────────
async function runTool(tool, msg) {
  switch (tool) {
    case 'status': {
      const cached = await getCached('status_v5');
      if (cached) return '[STATUS-cache] ' + cached;
      const [c, s] = await Promise.all([
        fetch(`${BASE}/api/cerebro/status`).then(r => r.json()).catch(() => ({})),
        fetch(`${BASE}/api/state`).then(r => r.json()).catch(() => ({}))
      ]);
      const txt = `Cérebro: ${c.status || 'offline'} | Score: ${c.score ?? '--'} | Dia: ${s.dia_atual ?? '--'}/261\nCiclos: ${s.ciclos ?? 0} | WA membros: ${s.membros_whatsapp ?? 0} | Vídeos hoje: ${s.videos_hoje ?? 0}`;
      await setCache('status_v5', txt, 2);
      return `[STATUS]\n${txt}`;
    }
    case 'gh_ls': {
      const m = msg.match(/(?:em|in|de|do|da|pasta|ls)\s+([\w/.\-]+)/i);
      const p = m ? m[1].replace(/^\//, '') : '';
      const d = await listDir(p);
      return `[ARQUIVOS /${p}]\n${d.map(f => `${f.type === 'dir' ? '📁' : '📄'} ${f.name}${f.size ? ` (${f.size}b)` : ''}`).join('\n')}`;
    }
    case 'gh_read': {
      const m = msg.match(/(?:arq|file|código|cat|ler|ver)\s+([\w/.\-]+)/i);
      if (!m) return '[ERRO] Informe o arquivo.';
      const c = await readFile(m[1]);
      return `[${m[1]}]\n\`\`\`\n${c.substring(0, 3000)}${c.length > 3000 ? '\n...[truncado]' : ''}\n\`\`\``;
    }
    case 'gh_delete': {
      const m = msg.match(/(?:arq|arquivo)\s+([\w/.\-]+)/i);
      if (!m) return '[ERRO] Informe o arquivo.';
      const sha = await deleteFile(m[1]);
      return `[DELETADO] ${m[1]} | commit: ${sha}`;
    }
    case 'gh_history': {
      const commits = await (await gh(`/repos/${REPO}/commits?per_page=10`)).json();
      if (!Array.isArray(commits)) return '[ERRO] Não conseguiu histórico';
      return `[HISTÓRICO]\n${commits.map(c => `• ${c.sha.substring(0, 7)} ${c.commit.message.substring(0, 60)} (${c.commit.author.date.substring(0, 10)})`).join('\n')}`;
    }
    case 'deploy': {
      const ref = await (await gh(`/repos/${REPO}/git/ref/heads/main`)).json();
      return `[DEPLOY] Commit: ${ref.object?.sha?.substring(0, 7)} | ${BASE}`;
    }
    case 'notion_search': {
      const m = msg.match(/(?:buscar|search|encontrar|pesquisar)\s+(.+?)(?:\s+no\s+notion)?$/i);
      const query = m ? m[1] : msg;
      const d = await notionSearch(query);
      const results = (d.results || []).slice(0, 5).map(p =>
        `• ${p.properties?.title?.title?.[0]?.text?.content || p.object} (${p.id.substring(0, 8)}...)`
      ).join('\n');
      return `[NOTION - busca: "${query}"]\n${results || 'Nenhum resultado'}`;
    }
    case 'notion_create': {
      const parentId = process.env.NOTION_PARENT_PAGE_ID;
      if (!parentId) return '[NOTION] Configure NOTION_PARENT_PAGE_ID no Vercel para criar páginas.';
      const m = msg.match(/(?:criar|create)\b.*\bnotion\b\s+(.+?)(?:\s+com\s+(.+))?$/i);
      const title = m ? m[1].trim() : 'Nova Página';
      const content = m?.[2] || '';
      const page = await notionCreatePage(parentId, title, content);
      return `[NOTION CRIADO] "${title}" | ID: ${page.id?.substring(0, 8)}... | ${page.url || ''}`;
    }
    case 'slack_info': {
      const channels = await slackListChannels();
      const list = (channels.channels || []).slice(0, 10).map(c => `• #${c.name} (${c.id})`).join('\n');
      return `[SLACK CANAIS]\n${list || 'Nenhum canal encontrado'}`;
    }
    case 'slack_send': {
      const m = msg.match(/(?:enviar|send|mandar)\s+(.+?)\s+(?:no|no canal|para)\s+#?([\w-]+)/i);
      if (!m) return '[SLACK] Use: "enviar <mensagem> no #canal"';
      const [, text, channel] = m;
      const r = await slackSend(channel, text);
      return r.ok ? `[SLACK] Mensagem enviada em #${channel}` : `[SLACK ERRO] ${r.error}`;
    }
    case 'drive_search': {
      const m = msg.match(/(?:buscar|search|encontrar)\s+(.+?)(?:\s+no\s+drive)?$/i);
      const query = m ? m[1] : '';
      const d = await driveSearch(`name contains '${query}'`);
      const files = (d.files || []).slice(0, 8).map(f => `• ${f.name} (${f.mimeType?.split('.').pop()}) - ${f.webViewLink || ''}`).join('\n');
      return `[DRIVE - "${query}"]\n${files || 'Nenhum arquivo'}`;
    }
    case 'db_info': {
      const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
      const tables = await supaGet('information_schema.tables', 'table_schema=eq.public&select=table_name').catch(() => []);
      const list = Array.isArray(tables) ? tables.map(t => `• ${t.table_name}`).join('\n') : 'N/A';
      return `[SUPABASE]\nURL: ${url}\nTabelas:\n${list}`;
    }
    case 'whatsapp': {
      const s = await fetch(`${BASE}/api/state`).then(r => r.json()).catch(() => ({}));
      return `[WHATSAPP]\nMembros: ${s.membros_whatsapp ?? 0}\nToken: ${process.env.WHATSAPP_TOKEN ? '✅' : '❌ não configurado'}`;
    }
    case 'youtube': {
      const s = await fetch(`${BASE}/api/state`).then(r => r.json()).catch(() => ({}));
      return `[YOUTUBE @psicologiadoc]\nSubscribers: ${s.subscribers ?? '--'} | Vídeos: ${s.total_videos ?? '--'} | Watch hours: ${s.watch_hours ?? '--'}\nDia: ${s.dia_atual ?? '--'}/261 até reveal`;
    }
    case 'social': {
      const s = await fetch(`${BASE}/api/state`).then(r => r.json()).catch(() => ({}));
      return `[SOCIAL]\nInstagram: ${s.instagram_followers ?? '--'} | TikTok: ${s.tiktok_followers ?? '--'} | Pinterest: ${s.pinterest_followers ?? '--'}`;
    }
    case 'browser': {
      const urls = [process.env.BROWSER_AGENT_URL, `${BASE}/api/browser-agent`].filter(Boolean);
      for (const url of urls) {
        try {
          const r = await fetch(url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tarefa: msg, dry_run: false }), signal: AbortSignal.timeout(25000) });
          if (r.ok) { const d = await r.json(); return `[BROWSER]\n${d.resumo || ''}\nAções: ${d.acoes_ok || 0}/${d.total_acoes || 0} | ${d.totalMs || 0}ms`; }
        } catch { }
      }
      return '[BROWSER] Serviço não disponível. Configure BROWSER_AGENT_URL apontando para o Railway.';
    }
    case 'memoria_semantica': {
      const similar = await searchMemoriaSemantic('global', msg, 5);
      if (!Array.isArray(similar) || similar.length === 0) return null;
      return `[MEMÓRIA SIMILAR]\n${similar.map(m => `• ${m.role}: ${m.content?.substring(0, 100)}`).join('\n')}`;
    }
    default: return null;
  }
}

// ── HANDLERS AI-ASSISTED ──────────────────────────────────────────────────
async function handleCreateFile(msg, model, max) {
  const ai = await callAI([
    { role: 'system', content: 'Extrai path e content. Retorne APENAS JSON: {"path":"caminho/relativo.ext","content":"conteúdo completo"}' },
    { role: 'user', content: msg }
  ], model, max);
  let p; try { p = JSON.parse(ai.text.match(/\{[\s\S]*\}/)?.[0]); } catch { return null; }
  if (!p?.path || !p?.content) return null;
  const sha = await commitFile(p.path, p.content, `feat: criar ${p.path} via ia-chat`);
  return `✅ **CRIADO**: \`${p.path}\`\nCommit: \`${sha.substring(0, 7)}\` | ${p.content.length} chars\n🚀 Deploy automático.`;
}

async function handleEditFile(msg, model, max) {
  const mPath = msg.match(/(?:arq|arquivo)\s+([\w/.\-]+)/i);
  if (!mPath) return null;
  const path = mPath[1];
  const instrucao = msg.replace(mPath[0], '').replace(/^[\s:,]+/, '').trim();
  let original; try { original = await readFile(path); } catch (e) { return `❌ Arquivo não encontrado: ${path}`; }
  const ai = await callAI([
    { role: 'system', content: 'Editor de código. Retorne APENAS o conteúdo completo modificado. Sem explicações, sem markdown fence.' },
    { role: 'user', content: `INSTRUÇÃO: ${instrucao}\n\nARQUIVO (${path}):\n${original}` }
  ], model, 8192);
  let novo = ai.text.trim().replace(/^```[\w]*\n/, '').replace(/\n```$/, '');
  if (novo === original) return '⚠️ Sem mudanças detectadas.';
  const sha = await commitFile(path, novo, `fix: ${instrucao.substring(0, 60)} via ia-chat`);
  return `✅ **MODIFICADO**: \`${path}\`\nCommit: \`${sha.substring(0, 7)}\` | ${original.length}→${novo.length} chars\n🚀 Deploy automático.`;
}

// ── MAIN ──────────────────────────────────────────────────────────────────
export async function POST(req) {
  const t0 = Date.now();
  try {
    const body = await req.json();
    const { mensagem, historico = [], modelo, max_tokens, session_id = 'default', usar_memoria = true, imagem_base64, imagem_mime } = body;
    if (!mensagem?.trim()) return Response.json({ erro: 'Mensagem vazia' }, { status: 400 });

    const model = modelo || 'llama-3.3-70b-versatile';
    const max = parseInt(max_tokens) || 4096;

    const toolNames = detectTools(mensagem);
    const toolResults = [];
    for (const t of toolNames) {
      if (t === 'gh_create') { const r = await handleCreateFile(mensagem, model, max); if (r) return Response.json({ resposta: r, kid: 'github', provider: 'github', tools_usadas: toolNames, ms: Date.now() - t0, version: V }); }
      if (t === 'gh_edit') { const r = await handleEditFile(mensagem, model, max); if (r) return Response.json({ resposta: r, kid: 'github', provider: 'github', tools_usadas: toolNames, ms: Date.now() - t0, version: V }); }
      try { const r = await runTool(t, mensagem); if (r) toolResults.push(r); } catch (e) { toolResults.push(`[ERRO ${t}]: ${e.message}`); }
    }

    // Memória: semântica se disponível, senão recente
    let memoria = [];
    if (usar_memoria) {
      const [semantica, recente] = await Promise.all([
        searchMemoriaSemantic(session_id, mensagem, 5),
        loadMemoria(session_id)
      ]);
      if (Array.isArray(semantica) && semantica.length > 0) {
        const semanticCtx = `[CONTEXTO RELEVANTE]\n${semantica.map(m => `${m.role}: ${m.content?.substring(0, 200)}`).join('\n')}`;
        toolResults.unshift(semanticCtx);
      }
      memoria = recente;
    }

    const sysContent = SYSTEM + (toolResults.length ? `\n\n[DADOS DO SISTEMA]\n${toolResults.join('\n\n')}` : '');
    const ctxHist = memoria.length > 0 ? memoria : historico.slice(-20);
    const messages = [{ role: 'system', content: sysContent }, ...ctxHist, { role: 'user', content: mensagem }];

    const result = await callAI(messages, model, max, imagem_base64 || null, imagem_mime || null);

    if (usar_memoria) {
      Promise.all([
        saveMemoriaSemantic(session_id, 'user', mensagem),
        saveMemoriaSemantic(session_id, 'assistant', result.text)
      ]).catch(() => {});
    }

    const groqKeys = getGroqKeys();
    return Response.json({
      resposta: result.text,
      kid: result.kid,
      provider: result.provider,
      modelo: model,
      groq_keys: groqKeys.length,
      capacidade_groq: groqKeys.length * 14400,
      tools_usadas: toolNames,
      uso: result.usage,
      tem_imagem: !!imagem_base64,
      session_id,
      ms: Date.now() - t0,
      version: V
    });
  } catch (e) {
    return Response.json({ erro: e.message, version: V }, { status: 500 });
  }
}

export async function GET() {
  const k = getGroqKeys();
  return Response.json({
    version: V,
    providers: {
      groq: { keys: k.length, limite_dia: k.length * 14400 },
      gemini: { ok: !!process.env.GEMINI_API_KEY, vision: true },
      together: { ok: !!process.env.TOGETHER_API_KEY, context: '128k' }
    },
    connectors: {
      notion: !!process.env.NOTION_TOKEN,
      slack: !!process.env.SLACK_TOKEN,
      drive: !!process.env.GOOGLE_API_KEY,
      browser: !!process.env.BROWSER_AGENT_URL
    },
    funcionalidades: ['visao', 'contexto-longo-auto', 'artefatos', 'notion', 'slack', 'drive', 'memoria-semantica-pgvector', 'github', 'supabase', 'youtube', 'whatsapp', 'browser']
  });
}
