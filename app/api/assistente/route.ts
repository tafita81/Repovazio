export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const GK = process.env.GROQ_API_KEY;
const GMK = process.env.GEMINI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
async function dbQ(path: string) {
  if (!SU || !SK) return [];
  try { const r = await fetch(`${SU}/rest/v1/${path}`, { headers: { apikey: SK, Authorization: `Bearer ${SK}` } }); return r.ok ? r.json() : []; } catch { return []; }
}
async function groq(msgs: any[], sys: string, maxTok = 2048) {
  if (!GK) return '';
  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${GK}` }, body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: maxTok, temperature: 0.7, messages: [{ role: 'system', content: sys }, ...msgs] }) });
  const d = await r.json();
  if (!r.ok) throw new Error(d.error?.message || 'Groq error');
  return d.choices?.[0]?.message?.content || '';
}
async function gemini(pergunta: string, sys: string, hist: any[], maxTok = 2048) {
  if (!GMK) return '';
  const contents = [...hist.slice(-6).map((h: any) => ({ role: h.role, parts: [{ text: h.text }] })), { role: 'user', parts: [{ text: pergunta }] }];
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GMK}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ system_instruction: { parts: [{ text: sys }] }, contents, generationConfig: { maxOutputTokens: maxTok, temperature: 0.7 } }) });
  const d = await r.json();
  return d.candidates?.[0]?.content?.parts?.[0]?.text || '';
}
export async function POST(req: Request) {
  try {
    const body = await req.json();
    const pergunta = body.pergunta || '';
    const historico = body.historico || [];
    if (!pergunta) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });
    const [registros, memoria] = await Promise.all([
      dbQ('registros?order=created_at.desc&limit=5&select=topic,score,created_at,modelo'),
      dbQ('cerebro_memoria?order=score.desc&limit=10&select=topic,score,vezes_gerado'),
    ]);
    const horaSP = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
    const sys = [
      'Voce e o Cerebro Assistente do psicologia.doc v7 — canal dark YouTube PT-BR de psicologia.',
      `Hora em Sao Paulo: ${horaSP}`,
      'Stack: Next.js 14 + Supabase + Groq (llama-3.3-70b, 14400 req/dia) + Gemini fallback + Vercel Hobby.',
      'Deploy: repovazio.vercel.app | GitHub: tafita81/Repovazio | Canal: @psicologiadoc',
      'Revelacao: Daniela Coelho psicologa no Dia 261 (~31/dez/2026).',
      'APIs gratuitas ativas: Groq 14.400 req/dia (principal), Gemini 1.500 req/dia (fallback).',
      'ULTIMAS PRODUCOES: ' + ((registros as any[]) || []).map((r: any) => `${r.topic}(score:${r.score},model:${r.modelo||'groq'})`).join(', '),
      'TOP TOPICOS POR SCORE: ' + ((memoria as any[]) || []).slice(0,5).map((m: any) => `${m.topic}:${m.score}`).join(', '),
      'PENDENCIAS CRITICAS: 1.ElevenLabs(voz) 2.HeyGen(avatar) 3.YouTube OAuth 4.Instagram Token 5.TikTok Token 6.Pinterest Token 7.Publicar 1o video(Dia 1) 8.1K subs->AdSense.',
      'Responda SEMPRE em portugues brasileiro. Seja direto, pratico e acionavel.',
      'Se for codigo mostre completo pronto para usar. Atue como CTO+CMO+Especialista canais dark psicologia.',
    ].join(' ');
    let resposta = '';
    let model = 'none';
    try {
      if (GK) {
        const msgs = [
          ...historico.slice(-6).map((h: any) => ({ role: h.role === 'model' ? 'assistant' : 'user', content: h.text })),
          { role: 'user', content: pergunta }
        ];
        resposta = await groq(msgs, sys, 2048);
        if (resposta) model = 'groq-llama-3.3-70b';
      }
    } catch {}
    if (!resposta) {
      try { if (GMK) { resposta = await gemini(pergunta, sys, historico, 2048); if (resposta) model = 'gemini-2.0-flash'; } } catch {}
    }
    if (!resposta) resposta = 'Servico indisponivel. Verifique GROQ_API_KEY e GEMINI_API_KEY no Vercel.';
    return Response.json({ resposta, model, timestamp: new Date().toISOString() });
  } catch (e: any) {
    return Response.json({ erro: e.message }, { status: 500 });
  }
}