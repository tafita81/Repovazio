export const dynamic = 'force-dynamic';

const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

async function db(path: string) {
  if (!SU || !SK) return null;
  const r = await fetch(`${SU}/rest/v1/${path}`, {
    headers: { apikey: SK!, Authorization: `Bearer ${SK}` },
  });
  return r.ok ? r.json() : null;
}

export async function GET() {
  const [registros, memoria, aprendizado] = await Promise.all([
    db("registros?order=created_at.desc&limit=5&select=topic,score,created_at,inovacao"),
    db("cerebro_memoria?order=score.desc&limit=10&select=topic,score,vezes_gerado,estilo_vencedor"),
    db("cerebro_aprendizado?order=data.desc&limit=1"),
  ]);

  const ultimos = registros || [];
  const top = memoria || [];
  const ultimo_aprendizado = (aprendizado || [])[0] || null;

  const score_medio = ultimos.length
    ? Math.round(ultimos.reduce((s: number, r: any) => s + r.score, 0) / ultimos.length)
    : 0;

  return Response.json({
    status: "online",
    ultimo_ciclo: ultimos[0]?.created_at || null,
    score_medio_recente: score_medio,
    total_memorizado: top.length,
    melhor_topic: top[0]?.topic || null,
    melhor_score: top[0]?.score || null,
    tendencia: ultimo_aprendizado?.tendencia || "iniciando",
    insight_mais_recente: ultimo_aprendizado?.insight || "Aprendizado em progresso",
    ultimas_producoes: ultimos,
    top_topics: top.slice(0, 5),
    timestamp: new Date().toISOString(),
  });
}
