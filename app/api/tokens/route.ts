export const dynamic = 'force-dynamic';

const SU = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SK = process.env.SUPABASE_SERVICE_KEY!;

// Limites do Gemini 2.0 Flash - Free Tier
const LIMITS = {
  requests_per_day: 1500,
  tokens_per_day: 1_000_000,
  tokens_per_minute: 32_000,
  output_tokens_per_request: 1500, // configurado no código
};

// Estimativa de tokens por ciclo (input prompt + output)
// /api/cerebro: ~450 input + 900 output = ~1350 tokens
// /api/cerebro/aprender: ~300 input + 400 output = ~700 tokens  
// /api/cron: ~200 input + 1500 output = ~1700 tokens por tópico × 2 = ~3400
const TOKENS_PER_CYCLE = 1350;
const TOKENS_APRENDER = 700;

async function db(path: string) {
  if (!SU || !SK) return null;
  const r = await fetch(`${SU}/rest/v1/${path}`, {
    headers: { apikey: SK, Authorization: `Bearer ${SK}` }
  });
  return r.ok ? r.json() : null;
}

export async function GET() {
  // Contar ciclos de hoje
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const hojeISO = hoje.toISOString();

  const [registros, aprendizado] = await Promise.all([
    db(`registros?created_at=gte.${hojeISO}&select=id,topic,score,modelo,created_at`),
    db(`cerebro_aprendizado?data=gte.${hojeISO}&select=id,total_ciclos_24h,score_medio,data`),
  ]);

  const ciclosHoje = (registros || []).length;
  const ciclosAprender = (aprendizado || []).length;

  // Calcular tokens estimados
  const tokensGastos = (ciclosHoje * TOKENS_PER_CYCLE) + (ciclosAprender * TOKENS_APRENDER);
  const requestsUsadas = ciclosHoje + ciclosAprender;

  // Percentuais
  const pctTokens = Math.min(100, Math.round((tokensGastos / LIMITS.tokens_per_day) * 100 * 100) / 100);
  const pctRequests = Math.min(100, Math.round((requestsUsadas / LIMITS.requests_per_day) * 100 * 100) / 100);

  // Status de saúde
  const saude = pctTokens > 90 ? 'critico' : pctTokens > 70 ? 'atencao' : 'saudavel';

  return Response.json({
    status: 'ok',
    data_hoje: hojeISO,
    gemini_model: 'gemini-2.0-flash',
    plano: 'free',
    limites: LIMITS,
    uso_hoje: {
      ciclos_cerebro: ciclosHoje,
      ciclos_aprender: ciclosAprender,
      requests_total: requestsUsadas,
      tokens_estimados: tokensGastos,
    },
    percentuais: {
      tokens: pctTokens,
      requests: pctRequests,
    },
    saude,
    tokens_restantes: LIMITS.tokens_per_day - tokensGastos,
    requests_restantes: LIMITS.requests_per_day - requestsUsadas,
    ultimos_registros: (registros || []).slice(0, 5).map((r: any) => ({
      topic: r.topic,
      score: r.score,
      created_at: r.created_at,
    })),
    timestamp: new Date().toISOString(),
  });
}