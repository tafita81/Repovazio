export const dynamic = 'force-dynamic';

export async function GET() {
  const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const SK = process.env.SUPABASE_SERVICE_KEY;
  if (!SU || !SK) return Response.json({ error: 'env vars missing' }, { status: 500 });

  const project = SU.replace('https://', '').replace('.supabase.co', '').replace('.supabase.co/', '');

  const sql = `
    CREATE TABLE IF NOT EXISTS registros (
      id BIGSERIAL PRIMARY KEY, topic TEXT, script TEXT,
      status TEXT DEFAULT 'gerado', canal TEXT DEFAULT 'psicologia.doc',
      created_at TIMESTAMPTZ DEFAULT NOW(), plataforma TEXT,
      score INTEGER DEFAULT 80, modelo TEXT, inovacao TEXT,
      ciclo_id BIGINT, memoria_usada INTEGER DEFAULT 0,
      views INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS cerebro_memoria (
      id BIGSERIAL PRIMARY KEY, topic TEXT UNIQUE,
      score INTEGER DEFAULT 80, vezes_gerado INTEGER DEFAULT 1,
      estilo_vencedor TEXT, criado_em TIMESTAMPTZ DEFAULT NOW(),
      ultimo_ciclo TIMESTAMPTZ DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS cerebro_aprendizado (
      id BIGSERIAL PRIMARY KEY, data TIMESTAMPTZ DEFAULT NOW(),
      total_ciclos_24h INTEGER DEFAULT 0, score_medio INTEGER DEFAULT 80,
      padroes_virais JSONB DEFAULT '[]', padroes_ruins JSONB DEFAULT '[]',
      proximos_topics JSONB DEFAULT '[]', tendencia TEXT DEFAULT 'estavel',
      insight TEXT, ajuste_tom TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_registros_created ON registros(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_registros_score ON registros(score DESC);
    CREATE INDEX IF NOT EXISTS idx_memoria_score ON cerebro_memoria(score DESC);
  `;

  // Usar pg-meta API do Supabase (server-side, sem CORS)
  const resp = await fetch(`https://${project}.supabase.co/pg-meta/v1/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'x-supabase-token': SK
    },
    body: JSON.stringify({ query: sql })
  });

  const result = await resp.json();
  
  // Verificar tabelas criadas
  const checkResp = await fetch(`${SU}/rest/v1/registros?select=count&limit=1`, {
    headers: { apikey: SK, Authorization: `Bearer ${SK}` }
  });

  return Response.json({
    status: resp.ok ? 'tables_created' : 'error',
    pg_meta_status: resp.status,
    pg_meta_result: result,
    registros_accessible: checkResp.status,
    timestamp: new Date().toISOString()
  });
}