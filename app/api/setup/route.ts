export const dynamic = 'force-dynamic';

const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

async function db(sql: string) {
  const r = await fetch(`${SU}/rest/v1/rpc/exec_raw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: SK!, Authorization: `Bearer ${SK}` },
    body: JSON.stringify({ sql })
  });
  return { status: r.status, ok: r.ok };
}

export async function GET(req: Request) {
  const auth = req.headers.get('authorization');
  if (process.env.SETUP_SECRET && auth !== `Bearer ${process.env.SETUP_SECRET}`) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const SK = process.env.SUPABASE_SERVICE_KEY;
  if (!SU || !SK) return Response.json({ error: 'Missing env vars' }, { status: 500 });

  const queries = [
    `CREATE TABLE IF NOT EXISTS registros (id BIGSERIAL PRIMARY KEY, topic TEXT, script TEXT, status TEXT DEFAULT 'gerado', canal TEXT DEFAULT 'psicologia.doc', created_at TIMESTAMPTZ DEFAULT NOW(), plataforma TEXT, score INTEGER DEFAULT 80, modelo TEXT, inovacao TEXT, ciclo_id BIGINT, memoria_usada INTEGER DEFAULT 0, views INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0)`,
    `CREATE TABLE IF NOT EXISTS cerebro_memoria (id BIGSERIAL PRIMARY KEY, topic TEXT UNIQUE, score INTEGER DEFAULT 80, vezes_gerado INTEGER DEFAULT 1, estilo_vencedor TEXT, criado_em TIMESTAMPTZ DEFAULT NOW(), ultimo_ciclo TIMESTAMPTZ DEFAULT NOW())`,
    `CREATE TABLE IF NOT EXISTS cerebro_aprendizado (id BIGSERIAL PRIMARY KEY, data TIMESTAMPTZ DEFAULT NOW(), total_ciclos_24h INTEGER DEFAULT 0, score_medio INTEGER DEFAULT 80, padroes_virais JSONB DEFAULT '[]', padroes_ruins JSONB DEFAULT '[]', proximos_topics JSONB DEFAULT '[]', tendencia TEXT DEFAULT 'estavel', insight TEXT, ajuste_tom TEXT)`,
    `CREATE INDEX IF NOT EXISTS idx_registros_created ON registros(created_at DESC)`,
    `CREATE INDEX IF NOT EXISTS idx_registros_score ON registros(score DESC)`,
    `CREATE INDEX IF NOT EXISTS idx_memoria_score ON cerebro_memoria(score DESC)`
  ];

  const results = [];
  for (const q of queries) {
    const resp = await fetch(`${SU}/rest/v1/rpc/exec_raw`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: `Bearer ${SK}`, Prefer: 'return=minimal' },
      body: JSON.stringify({ sql: q })
    });
    results.push({ q: q.slice(0, 40), status: resp.status });
  }

  return Response.json({ status: 'setup_attempted', results, timestamp: new Date().toISOString() });
}
