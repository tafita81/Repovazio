// api/manychat-webhook.js — Webhook ManyChat SONO → registra lead
export const config = { runtime: 'edge' };

const SB_URL = process.env.SUPABASE_URL;
const SB_KEY = process.env.SUPABASE_SERVICE_KEY;
const LINK_APP = 'https://repovazio.vercel.app/app-vendas';

export default async function handler(req) {
  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json',
  };

  if (req.method === 'OPTIONS') return new Response(null, { status: 200, headers: cors });

  try {
    const body = await req.json();
    const comentario  = (body.comment || body.text || '').toLowerCase();
    const subscriber  = body.subscriber_id || body.user_id || 'unknown';

    if (!comentario.includes('sono')) {
      return new Response(JSON.stringify({ status: 'ignored' }), { status: 200, headers: cors });
    }

    // Salvar lead no Supabase
    if (SB_URL && SB_KEY) {
      await fetch(`${SB_URL}/rest/v1/dm_sequencia`, {
        method: 'POST',
        headers: {
          'apikey': SB_KEY, 'Authorization': `Bearer ${SB_KEY}`,
          'Content-Type': 'application/json', 'Prefer': 'return=minimal',
        },
        body: JSON.stringify({
          step: 1, trigger: 'SONO',
          mensagem: `Lead SONO: ${subscriber} → ${LINK_APP}`,
          delay_min: 0, ativo: true,
        }),
      });
    }

    // Resposta para o ManyChat (formato esperado)
    return new Response(JSON.stringify({
      status: 'ok',
      messages: [{
        type: 'text',
        text: `Oi! Que bom que você se interessou 🌙\n\nAcesse agora por R$29,90:\n👉 ${LINK_APP}`,
      }],
    }), { status: 200, headers: cors });
  } catch (err) {
    return new Response(JSON.stringify({ error: String(err) }), { status: 500, headers: cors });
  }
}
