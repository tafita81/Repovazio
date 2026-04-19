export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const GK = process.env.GEMINI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const GM = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

async function dbQuery(path: string) {
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
    const { pergunta, historico = [] } = await req.json();
    if (!GK || !pergunta) return Response.json({ erro: 'Config incompleta' }, { status: 400 });

    // Buscar contexto completo do app em paralelo
    const [registros, memoria, aprendizado, tokens] = await Promise.all([
      dbQuery('registros?order=created_at.desc&limit=10&select=topic,score,created_at,inovacao,status'),
      dbQuery('cerebro_memoria?order=score.desc&limit=20&select=topic,score,vezes_gerado,estilo_vencedor'),
      dbQuery('cerebro_aprendizado?order=data.desc&limit=3&select=total_ciclos_24h,score_medio,padroes_virais,tendencia,insight,ajuste_tom'),
      dbQuery('registros?select=count&created_at=gte.' + new Date(new Date().setHours(0,0,0,0)).toISOString()),
    ]);

    const hoje = new Date().toLocaleDateString('pt-BR', { weekday:'long', day:'2-digit', month:'long', year:'numeric', timeZone:'America/Sao_Paulo' });
    const horasp = new Date().toLocaleTimeString('pt-BR', { timeZone:'America/Sao_Paulo' });

    const contexto = `Você é o Cérebro Assistente do psicologia.doc v7 — IA autônoma de um canal de documentários de psicologia no YouTube/Instagram/TikTok/Pinterest.

CONTEXTO COMPLETO DO SISTEMA:
- Canal: @psicologiadoc | Persona: anônima 2026 → Daniela Coelho psicóloga em ~31/dez/2026 (Dia 261)
- Stack: Next.js 14 + Supabase + Gemini 2.0 Flash + Vercel (Hobby) + GitHub tafita81/Repovazio
- Deploy: repovazio.vercel.app | Horário: São Paulo (BRT/UTC-3) | Agora: ${hoje} ${horasp}
- APIs: GEMINI_API_KEY, SUPABASE_SERVICE_KEY, NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY
- GitHub PAT: ativo (tafita81/Repovazio) | Vercel team: team_zr9vAef0Zz3njNAiGm3v5Y3h | Project: prj_rypXLpuS41CQt7sQYk5MM8kRQArr
- Supabase project: tpjvalzwkqwttvmszvie | URL: https://tpjvalzwkqwttvmszvie.supabase.co
- Gemini Free: 1.500 req/dia, 1.000.000 tokens/dia, 32.000 tokens/min

ÚLTIMAS PRODUÇÕES (${registros?.length || 0} registros):
${(registros||[]).map((r:any) => `• ${r.topic} | score:${r.score} | ${new Date(r.created_at).toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'})}`).join('\n') || 'Nenhum ainda'}

MEMÓRIA EVOLUTIVA (top tópicos):
${(memoria||[]).slice(0,10).map((m:any) => `• ${m.topic}: score ${m.score}, ${m.vezes_gerado}x gerado`).join('\n') || 'Iniciando'}

ÚLTIMO APRENDIZADO:
${(aprendizado||[]).slice(0,1).map((a:any) => `tendência: ${a.tendencia} | insight: ${a.insight} | ajuste: ${a.ajuste_tom}`).join('') || 'Aguardando dados'}

FASES DO PROJETO:
- Fase 1 (Dias 1-14): SEO → 1K inscritos
- Fase 2 (Dias 15-30): Viral → 5K inscritos
- Fase 3 (Dias 31-60): Escala → 10K + AdSense
- Fase 4 (Dias 61-180): 50K → R$10-40K/mês
- Fase 5 (Dias 181-260): 100K+ → autoridade máxima
- Fase 6 (Dia 261+): Revelação Daniela Coelho + consultas

PENDÊNCIAS CRÍTICAS (configurar para app funcionar 100%):
1. ElevenLabs API key (voz cinematográfica PT-BR)
2. HeyGen API key (avatar IA vídeo)
3. YouTube OAuth token (publicação automática)
4. Instagram Access Token (publicação automática)
5. TikTok Content API token (publicação automática)
6. Pinterest API token (publicação automática)

Você pode ajudar com: análise, otimização de código, estratégia, debug, configuração de APIs, criação de conteúdo, análise de métricas, e QUALQUER coisa relacionada ao projeto.
Responda SEMPRE em português brasileiro, de forma direta, clara e acionável.
Se for código, mostre o código completo e pronto para usar.
Se for estratégia, dê passos numerados concretos.
Seja como um CTO + CMO + Produtor de conteúdo especialista em canais dark de psicologia.
`;

    // Montar histórico para contexto multi-turno
    const messages = [
      ...historico.slice(-6).map((h: any) => ({
        role: h.role,
        parts: [{ text: h.text }]
      })),
      { role: 'user', parts: [{ text: pergunta }] }
    ];

    const body = {
      system_instruction: { parts: [{ text: contexto }] },
      contents: messages,
      generationConfig: {
        maxOutputTokens: 2048,
        temperature: 0.7,
        topP: 0.95,
      }
    };

    const r = await fetch(`${GM}?key=${GK}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    const d = await r.json();
    const resposta = d.candidates?.[0]?.content?.parts?.[0]?.text || 'Sem resposta do Gemini';
    const tokensUsados = d.usageMetadata?.totalTokenCount || 0;

    return Response.json({
      resposta,
      tokens_usados: tokensUsados,
      timestamp: new Date().toISOString()
    });

  } catch (e: any) {
    return Response.json({ erro: e.message }, { status: 500 });
  }
}