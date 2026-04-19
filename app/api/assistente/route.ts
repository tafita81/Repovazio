export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const GK = process.env.GEMINI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const GM = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

async function dbQ(path: string) {
  if (!SU || !SK) return [];
  try {
    const r = await fetch(`${SU}/rest/v1/${path}`, {
      headers: { apikey: SK, Authorization: `Bearer ${SK}` }
    });
    return r.ok ? r.json() : [];
  } catch { return []; }
}

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const pergunta = body.pergunta || '';
    const historico = body.historico || [];
    if (!GK || !pergunta) return Response.json({ erro: 'Config incompleta' }, { status: 400 });

    const [registros, memoria, aprendizado] = await Promise.all([
      dbQ('registros?order=created_at.desc&limit=5&select=topic,score,created_at,inovacao'),
      dbQ('cerebro_memoria?order=score.desc&limit=10&select=topic,score,vezes_gerado'),
      dbQ('cerebro_aprendizado?order=data.desc&limit=1&select=tendencia,insight,ajuste_tom'),
    ]);

    const horasp = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

    const sistema = [
      'Voce e o Cerebro Assistente do psicologia.doc v7.',
      `Agora em Sao Paulo: ${horasp}`,
      'Stack: Next.js 14 + Supabase + Gemini 2.0 Flash + Vercel Hobby + GitHub tafita81/Repovazio',
      'Deploy: repovazio.vercel.app',
      'Canal: @psicologiadoc | Revelacao Daniela Coelho psicologa Dia 261 ~31/dez/2026',
      'Gemini Free: 1.500 req/dia, 1M tokens/dia',
      '',
      'ULTIMAS PRODUCOES:',
      ...((registros as any[]) || []).map((r: any) => `- ${r.topic} (score ${r.score})`),
      '',
      'MEMORIA EVOLUTIVA TOP:',
      ...((memoria as any[]) || []).slice(0,5).map((m: any) => `- ${m.topic}: ${m.score} pts, ${m.vezes_gerado}x gerado`),
      '',
      'PENDENCIAS CRITICAS:',
      '1. ElevenLabs API Key (voz cinematografica)',
      '2. HeyGen API Key (avatar IA video)',
      '3. YouTube OAuth Token (publicacao automatica)',
      '4. Instagram Access Token',
      '5. TikTok Content API Token',
      '6. Pinterest API Token',
      '7. Publicar primeiro video (Dia 1)',
      '8. 1K subs + 4Kh -> AdSense',
      '',
      'Responda SEMPRE em portugues brasileiro. Seja direto, pratico e acionavel.',
      'Se for codigo, mostre completo e pronto para usar.',
      'Atue como CTO + CMO + Especialista em canais dark de psicologia.',
    ].join('\n');

    const contents: any[] = [
      ...historico.slice(-6).map((h: any) => ({ role: h.role, parts: [{ text: h.text }] })),
      { role: 'user', parts: [{ text: pergunta }] }
    ];

    const body2 = {
      system_instruction: { parts: [{ text: sistema }] },
      contents,
      generationConfig: { maxOutputTokens: 2048, temperature: 0.7 }
    };

    const r = await fetch(`${GM}?key=${GK}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body2)
    });

    const d = await r.json();
    if (!r.ok) {
      return Response.json({ erro: d.error?.message || 'Gemini error', status: r.status });
    }

    const resposta = d.candidates?.[0]?.content?.parts?.[0]?.text || 'Sem resposta';
    const tokensUsados = d.usageMetadata?.totalTokenCount || 0;

    return Response.json({ resposta, tokens_usados: tokensUsados, timestamp: new Date().toISOString() });
  } catch (e: any) {
    return Response.json({ erro: e.message }, { status: 500 });
  }
}