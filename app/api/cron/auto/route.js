export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
async function db(path, method, body) {
  if (!SU || !SK) return null;
  try {
    const r = await fetch(SU + '/rest/v1/' + path, {
      method: method || 'GET',
      headers: {'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK, Prefer: method === 'POST' ? 'return=representation' : ''},
      body: body ? JSON.stringify(body) : undefined
    });
    return r.ok ? r.json() : null;
  } catch { return null; }
}
export async function GET() {
  const inicio = Date.now();
  const resultado = {iniciado_em: new Date().toISOString(), acoes: []};
  const base = 'https://repovazio.vercel.app';
  try { const r = await fetch(base + '/api/cerebro'); const d = await r.json(); resultado.acoes.push({nome: 'cerebro', status: r.ok ? 'ok' : 'falha', score: d.score, topic: d.topic}); } catch(e) { resultado.acoes.push({nome: 'cerebro', status: 'erro', erro: e.message}); }
  try { const r = await fetch(base + '/api/cerebro/aprender'); resultado.acoes.push({nome: 'aprender', status: r.ok ? 'ok' : 'falha'}); } catch(e) { resultado.acoes.push({nome: 'aprender', status: 'erro', erro: e.message}); }
  const horaSP = parseInt(new Date().toLocaleString('pt-BR', {timeZone: 'America/Sao_Paulo', hour: '2-digit'}).slice(0,2));
  if (horaSP >= 8 && horaSP < 22) {
    try { const r = await fetch(base + '/api/whatsapp'); const d = await r.json(); resultado.acoes.push({nome: 'whatsapp', status: r.ok ? 'ok' : 'falha', mensagem: d.mensagem?.slice(0,50)}); } catch(e) { resultado.acoes.push({nome: 'whatsapp', status: 'erro', erro: e.message}); }
  } else { resultado.acoes.push({nome: 'whatsapp', status: 'silencio_noturno', hora: horaSP}); }
  try { const r = await fetch(base + '/api/ranking'); const d = await r.json(); resultado.acoes.push({nome: 'ranking', status: 'ok', total: d.total}); } catch(e) { resultado.acoes.push({nome: 'ranking', status: 'erro', erro: e.message}); }
  await db('cerebro_memoria', 'POST', { topic: 'ciclo_completo_' + new Date().getTime(), score: resultado.acoes.filter(a => a.status === 'ok').length * 25, metadata: JSON.stringify(resultado) });
  resultado.duracao_ms = Date.now() - inicio;
  return Response.json(resultado);
}