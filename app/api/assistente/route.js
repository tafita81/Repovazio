export const runtime = 'edge';
export const maxDuration = 300;

export async function POST(req) {
  try {
    const { pergunta } = await req.json();
    if (!pergunta?.trim()) return Response.json({ erro: 'Vazio' }, { status: 400 });

    const GROQ = process.env.GROQ_API_KEY;
    const p = pergunta.toLowerCase();
    console.log('[EXECUTOR] Pergunta:', p); // FORÇAR DEPLOY NOVO
    
    if (p.includes('status')) {
      console.log('[EXECUTOR] Detectou STATUS!');
      const c = await fetch('https://repovazio.vercel.app/api/cerebro/status').then(r => r.json()).catch(() => ({}));
      const s = await fetch('https://repovazio.vercel.app/api/state').then(r => r.json()).catch(() => ({}));
      return Response.json({ resposta: '📊 STATUS\n\n🧠 Cérebro: ' + (c.status || 'offline') + '\n📈 Score: ' + (c.score || '--') + '\n📅 Dia: ' + (s.dia_atual || '--') + '\n💥 Membros: ' + (s.membros_whatsapp || 0) + '\n\n✅ Online!' });
    }
    
    console.log('[EXECUTOR] Caiu no fallback Groq');
    const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + GROQ, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: 'llama-3.3-70b-versatile', messages: [{ role: 'user', content: pergunta }], max_tokens: 1000 })
    });
    const d = await r.json();
    return Response.json({ resposta: d.choices[0].message.content });
  } catch (error) {
    return Response.json({ erro: error.message }, { status: 500 });
  }
}