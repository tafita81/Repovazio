export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const GK = process.env.GEMINI_API_KEY;
const GROQ_KEY = process.env.GROQ_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

const GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions';
const GM_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

const TOPICS = [
  'Ansiedade','Apego ansioso','Narcisismo','Trauma infancia','Autossabotagem',
  'Dependencia emocional','Gaslighting','Sindrome do impostor','Limites saudaveis',
  'Psicologia do dinheiro','Burnout','Relacionamentos toxicos','Inteligencia emocional',
  'Autoestima','Luto e perda','Ansiedade social','Vicio em validacao','TDAH adulto'
];

async function db(path: string, method = 'GET', body?: object) {
  if (!SU || !SK) return null;
  try {
    const r = await fetch(`${SU}/rest/v1/${path}`, {
      method,
      headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: `Bearer ${SK}`, Prefer: method === 'POST' ? 'return=representation' : '' },
      body: body ? JSON.stringify(body) : undefined
    });
    return r.ok ? r.json() : null;
  } catch { return null; }
}

async function groq(prompt: string, tokens = 800): Promise<string> {
  if (!GROQ_KEY) return '';
  try {
    const r = await fetch(GROQ_URL, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: 'Voce e o narrator do canal psicologia.doc — documentarios de psicologia anonimos em PT-BR. Tom: especialista anonimo, segunda pessoa voce, CRP compliance, base DSM-5/APA. NUNCA use eu ou mencione nomes. PNL espelhamento obrigatorio. Responda SEMPRE em portugues brasileiro humanizado.' },
          { role: 'user', content: prompt }
        ],
        max_tokens: tokens,
        temperature: 0.85
      })
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error?.message || 'Groq error');
    return d.choices?.[0]?.message?.content || '';
  } catch (e: any) {
    console.error('Groq error:', e.message);
    return '';
  }
}

async function gemini(prompt: string, tokens = 800): Promise<string> {
  if (!GK) return '';
  try {
    const r = await fetch(`${GM_URL}?key=${GK}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: tokens, temperature: 0.85 } })
    });
    const d = await r.json();
    return d.candidates?.[0]?.content?.parts?.[0]?.text || '';
  } catch { return ''; }
}

async function callAI(prompt: string, tokens = 800): Promise<{ text: string; engine: string }> {
  // Tenta Groq primeiro (14.400 req/dia, sem expiração)
  const groqResp = await groq(prompt, tokens);
  if (groqResp.length > 50) return { text: groqResp, engine: 'groq/llama-3.3-70b' };
  // Fallback: Gemini
  const gemResp = await gemini(prompt, tokens);
  if (gemResp.length > 50) return { text: gemResp, engine: 'gemini-2.0-flash' };
  return { text: '', engine: 'none' };
}

export async function GET(req: Request) {
  const auth = req.headers.get('authorization');
  if (process.env.CRON_SECRET && auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const startedAt = new Date().toISOString();
  const ciclo = Date.now();

  const memoria = await db('cerebro_memoria?order=score.desc&limit=10') || [];
  const topicsVirais = (memoria as any[]).filter((m: any) => m.score >= 85).map((m: any) => m.topic);
  const topicsRuins = (memoria as any[]).filter((m: any) => m.score < 70).map((m: any) => m.topic);
  const resultados = await db('registros?order=created_at.desc&limit=20&select=topic,score') || [];

  // Escolher tema inteligente
  let topicEscolhido: string;
  if (topicsVirais.length > 0 && Math.random() > 0.3) {
    topicEscolhido = topicsVirais[Math.floor(Math.random() * topicsVirais.length)];
  } else {
    const disponiveis = TOPICS.filter(t => !topicsRuins.includes(t));
    topicEscolhido = disponiveis[Math.floor(Math.random() * disponiveis.length)];
  }

  const contexto = memoria.length > 0
    ? `MEMORIA DO QUE FUNCIONOU:\n${(memoria as any[]).slice(0,5).map((m: any) => `- ${m.topic}: score ${m.score}, estilo: ${m.estilo_vencedor || 'doc'}`).join('\n')}`
    : '';

  const prompt = `Canal psicologia.doc. Tom: especialista, segunda pessoa voce. CRP, DSM-5/APA. PNL espelhamento.\n${contexto}\n\nCrie roteiro VIRAL YouTube sobre "${topicEscolhido}".\nTITULO SEO (55-65 chars):\nGANCHO 0-30s (espelhamento PNL):\nPONTO 1 (dado cientifico DSM-5):\nPONTO 2 (caso anonimo + identificacao):\nPONTO 3 (virada emocional + esperanca):\nCTA FINAL (WhatsApp + proximo ep loop aberto):\nSCORE VIRAL (0-100):\nINOVACAO APLICADA:`;

  const { text: script, engine } = await callAI(prompt, 900);
  if (!script) return Response.json({ status: 'ai_unavailable', topic: topicEscolhido, engine: 'none' });

  const scoreMatch = script.match(/SCORE VIRAL[^:]*:\s*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1]) : Math.floor(Math.random() * 15) + 80;
  const inovacaoMatch = script.match(/INOVACAO APLICADA[^:]*:\s*(.+?)(?:\n|$)/i);
  const inovacao = inovacaoMatch ? inovacaoMatch[1].trim() : 'variacao padrao';

  await db('registros', 'POST', {
    topic: topicEscolhido, script: script.slice(0, 3000), status: 'gerado',
    canal: 'psicologia.doc', created_at: new Date().toISOString(),
    plataforma: 'youtube', score, modelo: engine, inovacao, ciclo_id: ciclo,
    memoria_usada: topicsVirais.length
  });

  // Atualizar memoria evolutiva
  const memExistente = (memoria as any[]).find((m: any) => m.topic === topicEscolhido);
  if (memExistente) {
    const novoScore = Math.round(memExistente.score * 0.6 + score * 0.4);
    await db(`cerebro_memoria?id=eq.${memExistente.id}`, 'PATCH', {
      score: novoScore, vezes_gerado: (memExistente.vezes_gerado || 1) + 1,
      estilo_vencedor: score > memExistente.score ? inovacao : memExistente.estilo_vencedor,
      ultimo_ciclo: new Date().toISOString()
    });
  } else {
    await db('cerebro_memoria', 'POST', {
      topic: topicEscolhido, score, vezes_gerado: 1, estilo_vencedor: inovacao,
      criado_em: new Date().toISOString(), ultimo_ciclo: new Date().toISOString()
    });
  }

  return Response.json({
    status: 'cerebro_ok', ciclo_id: ciclo, topic: topicEscolhido, score, inovacao,
    engine, memoria_usada: topicsVirais.length, topics_ruins_evitados: topicsRuins.length,
    startedAt, completedAt: new Date().toISOString()
  });
}