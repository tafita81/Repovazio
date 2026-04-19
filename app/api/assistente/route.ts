export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const GK = process.env.GROQ_API_KEY;
const GMK = process.env.GEMINI_API_KEY;
const OAK = process.env.OPENAI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const GH_PAT = process.env.GH_PAT;
const REPO = 'tafita81/Repovazio';

async function db(path, method = 'GET', body) {
  if (!SU || !SK) return [];
  try {
    const r = await fetch(SU + '/rest/v1/' + path, {
      method, headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK, Prefer: method === 'POST' ? 'return=representation' : '' },
      body: body ? JSON.stringify(body) : undefined
    });
    return r.ok ? r.json() : [];
  } catch { return []; }
}

async function callAI(msgs, sys) {
  const providers = [
    { key: GK, call: async () => {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + GK }, body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: 4096, temperature: 0.7, messages: [{ role: 'system', content: sys }, ...msgs] }) });
      const d = await r.json(); return { text: d.choices?.[0]?.message?.content || '', model: 'groq-llama-3.3-70b' };
    }},
    { key: GMK, call: async () => {
      const r = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GMK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ system_instruction: { parts: [{ text: sys }] }, contents: msgs.map(x => ({ role: x.role === 'assistant' ? 'model' : x.role, parts: [{ text: x.content }] })), generationConfig: { maxOutputTokens: 4096, temperature: 0.7 } }) });
      const d = await r.json(); return { text: d.candidates?.[0]?.content?.parts?.[0]?.text || '', model: 'gemini-2.0-flash' };
    }},
    { key: OAK, call: async () => {
      const r = await fetch('https://api.openai.com/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + OAK }, body: JSON.stringify({ model: 'gpt-4o-mini', max_tokens: 4096, temperature: 0.7, messages: [{ role: 'system', content: sys }, ...msgs] }) });
      const d = await r.json(); return { text: d.choices?.[0]?.message?.content || '', model: 'gpt-4o-mini' };
    }},
  ];
  for (const p of providers) {
    if (!p.key) continue;
    try { const result = await p.call(); if (result.text) return result; } catch {}
  }
  return { text: 'IAs indisponiveis.', model: 'none' };
}

async function execGitHub(path, content, msg) {
  if (!GH_PAT) return 'GH_PAT nao configurado no Vercel';
  const cur = await fetch('https://api.github.com/repos/' + REPO + '/contents/' + path, { headers: { 'Authorization': 'token ' + GH_PAT } });
  const curFile = await cur.json();
  const bytes = new TextEncoder().encode(content);
  let bin = ''; for (let i = 0; i < bytes.length; i += 8192) bin += String.fromCharCode(...bytes.subarray(i, i + 8192));
  const r = await fetch('https://api.github.com/repos/' + REPO + '/contents/' + path, {
    method: 'PUT', headers: { 'Authorization': 'token ' + GH_PAT, 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg, content: btoa(bin), sha: curFile.sha })
  });
  return r.ok ? 'arquivo atualizado: ' + path : 'erro: ' + r.status;
}

export async function POST(req) {
  try {
    const body = await req.json();
    const pergunta = body.pergunta || '';
    const historico = body.historico || [];
    if (!pergunta) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const [registros, memoria, waStats] = await Promise.all([
      db('registros?order=created_at.desc&limit=10&select=topic,score,created_at,modelo'),
      db('cerebro_memoria?order=score.desc&limit=15&select=topic,score,vezes_gerado'),
      db('whatsapp_mensagens?order=created_at.desc&limit=5&select=conteudo,tipo,created_at').catch(() => []),
    ]);

    const horaSP = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

    const sys = [
      'Voce e o CEREBRO EXECUTOR do psicologia.doc v7 — canal dark YouTube PT-BR psicologia.',
      'Hora SP: ' + horaSP + '.',
      'Stack: Next.js14 + Supabase + Groq(14400req/dia) + Gemini(1500/dia) + OpenAI(fallback pago) + Vercel + GitHub tafita81/Repovazio.',
      'Deploy: repovazio.vercel.app | Canal: @psicologiadoc | WhatsApp grupo max 1024 membros.',
      'Revelacao: Daniela Coelho psicologa Dia261 ~31/dez/2026.',
      'VOCE E EXECUTOR NAO SO RESPONDEDOR: ao editar codigo coloque entre |||CODE:caminho/arquivo.ts|||codigo|||END|||',
      'PRODUCOES: ' + (registros as any[]).map((r: any) => r.topic + '(' + r.score + ')').join(', ') + '.',
      'TOP: ' + (memoria as any[]).slice(0,5).map((m: any) => m.topic + ':' + m.score).join(', ') + '.',
      'PENDENCIAS: 1.ElevenLabs 2.HeyGen 3.YouTube OAuth 4.Instagram 5.TikTok 6.Pinterest 7.1oVideo(Dia1) 8.1KsubsAdSense 9.WhatsApp API 10.Bios redes.',
      'Responda em portugues brasileiro. Seja direto e acionavel. Codigo sempre completo.',
    ].join(' ');

    const msgs = [
      ...historico.slice(-8).map((h: any) => ({ role: h.role === 'model' ? 'assistant' : 'user', content: h.text })),
      { role: 'user', content: pergunta }
    ];

    const { text: resposta, model } = await callAI(msgs, sys);

    // Auto-executar se resposta tem marcacao de codigo para commitar
    let execResult = null;
    const codeMatch = resposta.match(/|||CODE:([\w\/.-]+)|||([sS]*?)|||END|||/);
    if (codeMatch && GH_PAT) {
      try {
        execResult = await execGitHub(codeMatch[1].trim(), codeMatch[2].trim(), 'feat(cerebro-executor): ' + pergunta.slice(0, 60));
      } catch (e: any) {
        execResult = 'Erro execucao: ' + e.message;
      }
    }

    return Response.json({ resposta, model, execResult, timestamp: new Date().toISOString() });
  } catch (e: any) {
    return Response.json({ erro: e.message }, { status: 500 });
  }
}