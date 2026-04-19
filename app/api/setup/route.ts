export const dynamic = 'force-dynamic';
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

async function sql(query: string) {
  if (!SU || !SK) return { error: 'env missing' };
  const r = await fetch(`${SU}/rest/v1/`, {
    method: 'HEAD', headers: { apikey: SK, Authorization: `Bearer ${SK}` }
  });
  // Usar o endpoint de query SQL do Supabase via REST
  const r2 = await fetch(`${SU}/rest/v1/rpc/exec`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: `Bearer ${SK}` },
    body: JSON.stringify({ sql: query })
  });
  return { status: r2.status, ok: r2.ok };
}

export async function GET() {
  const results: string[] = [];

  // Verificar tabelas existentes
  const tables = ['registros', 'cerebro_memoria', 'cerebro_aprendizado', 'whatsapp_mensagens', 'whatsapp_respostas', 'whatsapp_membros', 'planejamento_revelacao'];
  const checks = await Promise.all(tables.map(async (t) => {
    if (!SU || !SK) return { table: t, ok: false };
    const r = await fetch(`${SU}/rest/v1/${t}?limit=1`, {
      headers: { apikey: SK, Authorization: `Bearer ${SK}` }
    });
    return { table: t, ok: r.ok, status: r.status };
  }));

  // Inserir plano se tabela existe mas vazia
  const planoCheck = checks.find(c => c.table === 'planejamento_revelacao');
  if (planoCheck?.ok) {
    const existR = await fetch(`${SU}/rest/v1/planejamento_revelacao?select=count`, {
      headers: { apikey: SK, Authorization: `Bearer ${SK}`, Prefer: 'count=exact' }
    });
    const count = parseInt(existR.headers.get('content-range')?.split('/')[1] || '0');
    if (count === 0) {
      const plano = [
        { dia: 1, fase: 'lancamento', acao: 'Publicar 1o video YouTube — ativa Dia 1' },
        { dia: 30, fase: 'crescimento', acao: 'Meta 500 subs — WhatsApp grupo ativo' },
        { dia: 60, fase: 'engajamento', acao: 'Meta 1000 subs — solicitar AdSense' },
        { dia: 90, fase: 'monetizacao', acao: 'Primeiros ganhos AdSense — adicionar afiliados' },
        { dia: 120, fase: 'expansao', acao: 'Meta 5000 subs — TikTok e Instagram ativos' },
        { dia: 180, fase: 'consolidacao', acao: 'Meta 10000 subs — curso gratuito lead magnet' },
        { dia: 240, fase: 'pre-revelacao', acao: 'Hints sobre Daniela Coelho nos videos' },
        { dia: 261, fase: 'revelacao', acao: 'REVELAR Daniela Coelho Psicologa — agenda consultas online' },
        { dia: 270, fase: 'pos-revelacao', acao: 'Converter grupo WhatsApp em clientes consulta' },
        { dia: 365, fase: 'escala', acao: 'Meta 100000 subs — canal EUA ingles' },
      ];
      await fetch(`${SU}/rest/v1/planejamento_revelacao`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: `Bearer ${SK}`, Prefer: 'return=minimal' },
        body: JSON.stringify(plano)
      });
      results.push('plano inserido');
    }
  }

  return Response.json({
    setup_ok: true,
    tabelas: checks,
    results,
    hora: new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' })
  });
}