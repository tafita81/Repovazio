// api/receita.js — Endpoint de receita em tempo real
export const config = { runtime: 'edge' };

const SB_URL = process.env.SUPABASE_URL;
const SB_KEY = process.env.SUPABASE_SERVICE_KEY;

export default async function handler(req) {
  const cors = { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' };
  try {
    const [vendas, wa, projetada] = await Promise.all([
      fetch(`${SB_URL}/rest/v1/vendas?select=preco,produto,criado_em&status=eq.confirmada&order=criado_em.desc&limit=10`,
        { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } }).then(r => r.json()),
      fetch(`${SB_URL}/rest/v1/produto_whatsapp?select=assinantes&limit=1`,
        { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } }).then(r => r.json()),
      fetch(`${SB_URL}/rest/v1/receita_projetada?select=*&limit=1`,
        { headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}` } }).then(r => r.json()),
    ]);

    const hoje = new Date().toISOString().split('T')[0];
    const vendas_hoje = (vendas || []).filter(v => v.criado_em?.startsWith(hoje));
    const assinantes  = wa?.[0]?.assinantes ?? 0;
    const receita_mes = projetada?.[0]?.receita_mes ?? 0;

    return new Response(JSON.stringify({
      vendas_hoje: vendas_hoje.length,
      receita_hoje: vendas_hoje.reduce((s, v) => s + (+v.preco||0), 0),
      assinantes_wa: assinantes,
      receita_mes_app: +receita_mes,
      receita_mes_wa: assinantes * 18,
      total_mes: +receita_mes + assinantes * 18,
      pct_meta: +((+receita_mes + assinantes * 18) / 50000 * 100).toFixed(1),
      ultimas_vendas: vendas?.slice(0, 5) ?? [],
    }), { status: 200, headers: cors });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), { status: 500, headers: cors });
  }
}
