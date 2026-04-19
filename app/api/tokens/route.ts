export const dynamic = 'force-dynamic';

const SU = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const SK = process.env.SUPABASE_SERVICE_KEY!;

const LIMITS = {
  requests_per_day: 1500,
  tokens_per_day: 1_000_000,
  tokens_per_minute: 32_000,
  // Tokens médios por operação (input+output estimados)
  tokens_por_cerebro: 1350,     // /api/cerebro
  tokens_por_aprender: 700,     // /api/cerebro/aprender
  tokens_por_assistente: 2500,  // /api/assistente (maior contexto)
  tokens_por_cron: 1700,        // /api/cron
};

async function db(path: string) {
  if (!SU || !SK) return null;
  try {
    const r = await fetch(`${SU}/rest/v1/${path}`, {
      headers: { apikey: SK, Authorization: `Bearer ${SK}`, 'Cache-Control': 'no-cache' }
    });
    return r.ok ? r.json() : null;
  } catch { return null; }
}

export async function GET() {
  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);
  const hojeISO = hoje.toISOString();
  
  // Horário São Paulo
  const agora_sp = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });

  const [registros, aprendizado] = await Promise.all([
    db(`registros?created_at=gte.${hojeISO}&select=id,modelo,created_at`),
    db(`cerebro_aprendizado?data=gte.${hojeISO}&select=id,data`),
  ]);

  const ciclosCerebro = (registros || []).length;
  const ciclosAprender = (aprendizado || []).length;
  const requests = ciclosCerebro + ciclosAprender;

  // Tokens estimados por tipo
  const tokensCerebro = ciclosCerebro * LIMITS.tokens_por_cerebro;
  const tokensAprender = ciclosAprender * LIMITS.tokens_por_aprender;
  const tokensTotal = tokensCerebro + tokensAprender;

  const pctTokens = Math.min(100, (tokensTotal / LIMITS.tokens_per_day) * 100);
  const pctReqs = Math.min(100, (requests / LIMITS.requests_per_day) * 100);

  // Meta: usar 85% do limite (850.000 tokens/dia)
  const META_DIARIA = 850_000;
  const tokensRestantes = LIMITS.tokens_per_day - tokensTotal;
  const pctMeta = Math.min(100, (tokensTotal / META_DIARIA) * 100);
  
  // Quantos ciclos ainda cabem hoje
  const ciclosRestantes = Math.floor(tokensRestantes / LIMITS.tokens_por_cerebro);
  const saude = pctTokens > 90 ? 'critico' : pctTokens > 70 ? 'atencao' : 'saudavel';

  return Response.json({
    status: 'ok',
    agora_sp,
    gemini_model: 'gemini-2.0-flash',
    plano: 'free',
    limites: LIMITS,
    uso_hoje: {
      ciclos_cerebro: ciclosCerebro,
      ciclos_aprender: ciclosAprender,
      requests_total: requests,
      tokens_estimados: tokensTotal,
      tokens_cerebro: tokensCerebro,
      tokens_aprender: tokensAprender,
    },
    percentuais: {
      tokens: parseFloat(pctTokens.toFixed(4)),
      requests: parseFloat(pctReqs.toFixed(4)),
      meta_85pct: parseFloat(pctMeta.toFixed(2)),
    },
    saude,
    tokens_restantes: tokensRestantes,
    requests_restantes: LIMITS.requests_per_day - requests,
    ciclos_restantes_hoje: ciclosRestantes,
    meta_diaria_tokens: META_DIARIA,
    timestamp: new Date().toISOString(),
  });
}