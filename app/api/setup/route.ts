export const dynamic = 'force-dynamic';
import { createClient } from '@supabase/supabase-js';

export async function GET() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key = process.env.SUPABASE_SERVICE_KEY!;
  if (!url || !key) return Response.json({ error: 'env vars missing' }, { status: 500 });

  const sb = createClient(url, key);

  const sqls = [
    `CREATE TABLE IF NOT EXISTS registros (
      id BIGSERIAL PRIMARY KEY, topic TEXT, script TEXT,
      status TEXT DEFAULT 'gerado', canal TEXT DEFAULT 'psicologia.doc',
      created_at TIMESTAMPTZ DEFAULT NOW(), plataforma TEXT,
      score INTEGER DEFAULT 80, modelo TEXT, inovacao TEXT,
      ciclo_id BIGINT, memoria_usada INTEGER DEFAULT 0,
      views INTEGER DEFAULT 0, clicks INTEGER DEFAULT 0
    )`,
    `CREATE TABLE IF NOT EXISTS cerebro_memoria (
      id BIGSERIAL PRIMARY KEY, topic TEXT UNIQUE,
      score INTEGER DEFAULT 80, vezes_gerado INTEGER DEFAULT 1,
      estilo_vencedor TEXT, criado_em TIMESTAMPTZ DEFAULT NOW(),
      ultimo_ciclo TIMESTAMPTZ DEFAULT NOW()
    )`,
    `CREATE TABLE IF NOT EXISTS cerebro_aprendizado (
      id BIGSERIAL PRIMARY KEY, data TIMESTAMPTZ DEFAULT NOW(),
      total_ciclos_24h INTEGER DEFAULT 0, score_medio INTEGER DEFAULT 80,
      padroes_virais JSONB DEFAULT '[]', padroes_ruins JSONB DEFAULT '[]',
      proximos_topics JSONB DEFAULT '[]', tendencia TEXT DEFAULT 'estavel',
      insight TEXT, ajuste_tom TEXT
    )`,
    `CREATE INDEX IF NOT EXISTS idx_registros_created ON registros(created_at DESC)`,
    `CREATE INDEX IF NOT EXISTS idx_registros_score ON registros(score DESC)`,
    `CREATE INDEX IF NOT EXISTS idx_memoria_score ON cerebro_memoria(score DESC)`
  ];

  const results = [];
  for (const sql of sqls) {
    const { error } = await sb.rpc('exec_sql', { sql_query: sql }).single();
    // fallback: tentar via from() direto
    results.push({ sql: sql.slice(0, 40), error: error?.message || null });
  }

  // Verificar se tabelas existem
  const { data: tables } = await sb.from('registros').select('count').limit(0);
  
  return Response.json({ 
    status: 'done', 
    results,
    registros_exists: tables !== null,
    timestamp: new Date().toISOString() 
  });
}