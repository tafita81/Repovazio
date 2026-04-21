export const runtime = 'edge';
export const maxDuration = 300;

export async function POST(req) {
  try {
    const { pergunta } = await req.json();
    if (!pergunta?.trim()) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const GROQ_KEY = process.env.GROQ_API_KEY;
    const GH_PAT = process.env.GH_PAT;
    const H = { 'Authorization': 'token ' + GH_PAT, 'Content-Type': 'application/json' };
    const p = pergunta.toLowerCase();
    
    // STATUS - BUSCA APIS REAIS
    if (p.includes('status')) {
      const [cerebro, state] = await Promise.allSettled([
        fetch('https://repovazio.vercel.app/api/cerebro/status').then(r => r.json()),
        fetch('https://repovazio.vercel.app/api/state').then(r => r.json())
      ]);
      const c = cerebro.value || {};
      const s = state.value || {};
      return Response.json({ 
        resposta: \`📊 STATUS DO SISTEMA

🧠 Cérebro: \${c.status || 'offline'}
📈 Score: \${c.score || '--'}
📅 Dia: \${s.dia_atual || '--'}
💥 Membros: \${s.membros_whatsapp || 0}

✅ Sistema operacional!\` 
      });
    }
    
    // DEPLOY - FAZ DEPLOY REAL
    if (p.includes('deploy')) {
      const curSha = (await (await fetch('https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main', { headers: H })).json()).object.sha;
      const deployResp = await fetch('https://api.vercel.com/v13/deployments?forceNew=1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'repovazio',
          project: 'prj_rypXLpuS41CQt7sQYk5MM8kRQArr',
          target: 'production',
          gitSource: { type: 'github', repoId: '1075503208', ref: 'main', sha: curSha }
        })
      });
      const deployData = await deployResp.json();
      return Response.json({ 
        resposta: \`✅ Deploy iniciado!

📝 SHA: \${curSha.slice(0,7)}
🚀 Status: \${deployData.readyState || 'INITIALIZING'}

⏱️ Aguarde ~40s\`
      });
    }
    
    // FALLBACK - Resposta genérica Groq
    const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': \`Bearer \${GROQ_KEY}\`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        model: 'llama-3.3-70b-versatile', 
        messages: [{ role: 'user', content: pergunta }], 
        max_tokens: 1000 
      })
    });
    const d = await r.json();
    return Response.json({ resposta: d.choices[0].message.content });
    
  } catch (error) {
    return Response.json({ erro: error.message, stack: error.stack }, { status: 500 });
  }
}