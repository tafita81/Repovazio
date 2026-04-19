export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const GROQ_KEY = process.env.GROQ_API_KEY;
const GK = process.env.GEMINI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

async function dbQ(path: string) {
  if (!SU || !SK) return [];
  try { const r = await fetch(`${SU}/rest/v1/${path}`, { headers: { apikey: SK, Authorization: `Bearer ${SK}` } }); return r.ok ? r.json() : []; }
  catch { return []; }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const pergunta = body.pergunta || '';
    const historico = body.historico || [];
    if (!pergunta) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const [registros, memoria, aprendizado] = await Promise.all([
      dbQ('registros?order=created_at.desc&limit=5&select=topic,score,created_at,inovacao'),
      dbQ('cerebro_memoria?order=score.desc&limit=10&select=topic,score,vezes_gerado'),
      dbQ('cerebro_aprendizado?order=data.desc&limit=1&select=tendencia,insight,ajuste_tom'),
    ]);

    const horasp = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

    const sistema = [
      'Voce e o Cerebro Assistente do psicologia.doc v7 — IA autonoma de canal dark de psicologia.',
      `Agora em Sao Paulo: ${horasp}`,
      'Stack: Next.js 14 + Supabase + Groq (llama-3.3-70b) + Gemini fallback + Vercel + GitHub tafita81/Repovazio',
      'Canal: @psicologiadoc | Revelacao Daniela Coelho psicologa Dia 261 ~31/dez/2026',
      'Groq: 14.400 req/dia sem expiracao | Gemini: 1.500 req/dia (fallback)',
      '',
      'ULTIMAS PRODUCOES:',
      ...((registros as any[]) || []).map((r: any) => `- ${r.topic} (score ${r.score}) via ${r.inovacao || 'padrao'}`),
      '',
      'TOP TOPICS (memoria evolutiva):',
      ...((memoria as any[]) || []).slice(0,5).map((m: any) => `- ${m.topic}: ${m.score} pts, ${m.vezes_gerado}x gerado`),
      '',
      'ULTIMO APRENDIZADO:',
      ...((aprendizado as any[]) || []).slice(0,1).map((a: any) => `tendencia: ${a.tendencia} | insight: ${a.insight}`),
      '',
      'PENDENCIAS CRITICAS:',
      '1. ElevenLabs API Key (voz cinematografica PT-BR)',
      '2. HeyGen API Key (avatar IA video 4K)',
      '3. YouTube OAuth Token (publicacao automatica)',
      '4. Instagram Access Token (publicacao automatica)',
      '5. TikTok Content API Token',
      '6. Pinterest API Token',
      '7. Publicar 1o video no YouTube (ativa Dia 1)',
      '8. 1K subs + 4Kh = AdSense',
      '',
      'Responda SEMPRE em portugues brasileiro claro, direto e acionavel.',
      'Para codigo: mostre completo e pronto para usar.',
      'Para estrategia: passos numerados concretos.',
      'Atue como CTO + CMO + Especialista em canais dark de psicologia monetizados.',
    ].join('\n');

    const messages = [
      ...historico.slice(-6).map((h: any) => ({ role: h.role === 'model' ? 'assistant' : h.role, content: h.text })),
      { role: 'user', content: pergunta }
    ];

    // Tentar Groq primeiro
    if (GROQ_KEY) {
      try {
        const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'llama-3.3-70b-versatile',
            messages: [{ role: 'system', content: sistema }, ...messages],
            max_tokens: 2048,
            temperature: 0.7
          })
        });
        const d = await r.json();
        if (r.ok && d.choices?.[0]?.message?.content) {
          return Response.json({
            resposta: d.choices[0].message.content,
            engine: 'groq/llama-3.3-70b',
            tokens_usados: d.usage?.total_tokens || 0,
            timestamp: new Date().toISOString()
          });
        }
      } catch {}
    }

    // Fallback Gemini
    if (GK) {
      try {
        const contents = [
          ...historico.slice(-6).map((h: any) => ({ role: h.role === 'user' ? 'user' : 'model', parts: [{ text: h.text }] })),
          { role: 'user', parts: [{ text: pergunta }] }
        ];
        const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GK}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            system_instruction: { parts: [{ text: sistema }] },
            contents,
            generationConfig: { maxOutputTokens: 2048, temperature: 0.7 }
          })
        });
        const d = await r.json();
        if (r.ok && d.candidates?.[0]?.content?.parts?.[0]?.text) {
          return Response.json({
            resposta: d.candidates[0].content.parts[0].text,
            engine: 'gemini-2.0-flash',
            tokens_usados: d.usageMetadata?.totalTokenCount || 0,
            timestamp: new Date().toISOString()
          });
        }
      } catch {}
    }

    return Response.json({ erro: 'Todos os provedores de IA indisponiveis. Tente em alguns minutos.' }, { status: 503 });
  } catch (e: any) {
    return Response.json({ erro: e.message }, { status: 500 });
  }
}