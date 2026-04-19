export const dynamic = 'force-dynamic';

export async function GET() {
  const SU = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const SK = process.env.SUPABASE_SERVICE_KEY!;

  // Tentar criar tabelas via INSERT com ON CONFLICT ignorado
  // Como fallback, verificar se tabelas já existem
  const headers = {
    'Content-Type': 'application/json',
    'apikey': SK,
    'Authorization': `Bearer ${SK}`,
    'Prefer': 'return=minimal'
  };

  const results: any[] = [];

  // Verificar se registros existe
  const checkR = await fetch(`${SU}/rest/v1/registros?limit=1`, { headers });
  results.push({ table: 'registros', exists: checkR.status !== 404, status: checkR.status });

  const checkM = await fetch(`${SU}/rest/v1/cerebro_memoria?limit=1`, { headers });
  results.push({ table: 'cerebro_memoria', exists: checkM.status !== 404, status: checkM.status });

  const checkA = await fetch(`${SU}/rest/v1/cerebro_aprendizado?limit=1`, { headers });
  results.push({ table: 'cerebro_aprendizado', exists: checkA.status !== 404, status: checkA.status });

  const allExist = results.every(r => r.exists);

  if (!allExist) {
    // Tabelas não existem — tentar via pg-meta
    const missing = results.filter(r => !r.exists).map(r => r.table);
    return Response.json({ 
      status: 'tables_missing', 
      missing,
      message: 'Execute o SUPABASE_SETUP.sql manualmente no SQL Editor do Supabase',
      results,
      sql_url: 'https://supabase.com/dashboard/project/tpjvalzwkqwttvmszvie/sql/new'
    });
  }

  return Response.json({ status: 'all_tables_exist', results, timestamp: new Date().toISOString() });
}