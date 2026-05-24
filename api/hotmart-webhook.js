// api/hotmart-webhook.js — Webhook Hotmart → registra venda → upsell WA
// Deploy: Vercel (sem limite de funções, sem custo extra)
// URL final: repovazio.vercel.app/api/hotmart-webhook

const SB_URL = process.env.SUPABASE_URL;
const SB_KEY = process.env.SUPABASE_SERVICE_KEY;

export const config = { runtime: 'edge' };

export default async function handler(req) {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, x-hotmart-hottok',
    'Content-Type': 'application/json',
  };

  if (req.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: cors });
  }

  if (req.method !== 'POST') {
    return new Response(JSON.stringify({ error: 'Method Not Allowed' }),
      { status: 405, headers: cors });
  }

  try {
    const body = await req.json();
    const event    = body.event || body.data?.event || 'PURCHASE_COMPLETE';
    const buyer    = body.data?.buyer || body.buyer || {};
    const purchase = body.data?.purchase || body.purchase || {};
    const preco    = purchase.price?.value || 29.90;
    const email    = buyer.email || '';
    const produto  = preco >= 200 ? 'whatsapp_anual' : 'app_psicologia';

    // Só processa compras aprovadas
    if (!['PURCHASE_COMPLETE','PURCHASE_APPROVED'].includes(event)) {
      return new Response(JSON.stringify({ status: 'ignored', event }),
        { status: 200, headers: cors });
    }

    const sbHeaders = {
      'apikey': SB_KEY,
      'Authorization': `Bearer ${SB_KEY}`,
      'Content-Type': 'application/json',
      'Prefer': 'return=minimal',
    };

    // Registrar venda na tabela vendas
    await fetch(`${SB_URL}/rest/v1/vendas`, {
      method: 'POST',
      headers: sbHeaders,
      body: JSON.stringify({
        produto, preco,
        plataforma: 'hotmart',
        email_comprador: email,
        status: 'confirmada',
        origem: 'instagram',
      }),
    });

    // Se comprou app → adicionar na fila de email upsell (WhatsApp R$216/ano)
    if (produto === 'app_psicologia' && email) {
      await fetch(`${SB_URL}/rest/v1/dm_sequencia`, {
        method: 'POST',
        headers: sbHeaders,
        body: JSON.stringify({
          step: 2,
          trigger: 'comprou_app',
          mensagem: `Upsell WA agendar para: ${email}`,
          delay_min: 60,
          ativo: true,
        }),
      });
    }

    return new Response(
      JSON.stringify({ status: 'ok', produto, preco, email: email.slice(0,3)+'***' }),
      { status: 200, headers: cors }
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ status: 'error', message: String(err) }),
      { status: 500, headers: cors }
    );
  }
}
