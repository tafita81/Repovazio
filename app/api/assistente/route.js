export const runtime = 'edge';
export const maxDuration = 300;

// EXECUTOR INTELIGENTE - Funciona igual Claude
export async function POST(req) {
  try {
    const { pergunta } = await req.json();
    if (!pergunta?.trim()) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const GROQ_KEY = process.env.GROQ_API_KEY;
    const GH_PAT = process.env.GH_PAT;
    const VERCEL_TOKEN = process.env.VERCEL_TOKEN || null;
    
    // 1. Usar Groq para ENTENDER o que fazer
    const intentResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [{
          role: 'system',
          content: `Você é um analisador de intenções. Analise a pergunta do usuário e retorne APENAS um JSON com:
{
  "acao": "criar_rota" | "fazer_deploy" | "atualizar_dashboard" | "criar_arquivo" | "modificar_arquivo" | "query_supabase" | "status_sistema" | "outro",
  "detalhes": {objeto com detalhes específicos da ação}
}

Exemplos:
- "criar rota /api/teste" → {"acao":"criar_rota","detalhes":{"path":"app/api/teste/route.js"}}
- "fazer deploy" → {"acao":"fazer_deploy","detalhes":{}}
- "atualizar dashboard para mostrar X" → {"acao":"modificar_arquivo","detalhes":{"path":"app/ia/page.jsx","modificacao":"adicionar X"}}
- "status do sistema" → {"acao":"status_sistema","detalhes":{}}

RETORNE APENAS O JSON, SEM EXPLICAÇÕES.`
        }, {
          role: 'user',
          content: pergunta
        }],
        temperature: 0.3,
        max_tokens: 500
      })
    });

    const intentData = await intentResponse.json();
    const intentText = intentData.choices[0].message.content.trim();
    let intent;
    
    try {
      const jsonMatch = intentText.match(/{[sS]*}/);
      intent = JSON.parse(jsonMatch ? jsonMatch[0] : intentText);
    } catch (e) {
      intent = { acao: 'outro', detalhes: {} };
    }

    let acoes = [];
    let resultado = '';

    // 2. EXECUTAR a ação identificada
    switch (intent.acao) {
      case 'fazer_deploy':
        // Trigger deploy no Vercel
        const curSha = (await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main`, { headers: { 'Authorization': `token ${GH_PAT}` } })).json()).object.sha;
        
        const deployResp = await fetch('https://api.vercel.com/v13/deployments?forceNew=1', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${VERCEL_TOKEN || ''}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: 'repovazio',
            project: 'prj_rypXLpuS41CQt7sQYk5MM8kRQArr',
            target: 'production',
            gitSource: { type: 'github', repoId: '1075503208', ref: 'main', sha: curSha }
          })
        });
        
        const deployData = await deployResp.json();
        acoes.push({ tipo: 'deploy', status: deployData.readyState || 'iniciado' });
        resultado = `✅ Deploy iniciado! SHA: ${curSha.slice(0,7)}
Status: ${deployData.readyState || 'INITIALIZING'}
URL: https://repovazio.vercel.app`;
        break;

      case 'status_sistema':
        // Buscar status de todas as APIs
        const [cerebro, state, ranking] = await Promise.allSettled([
          fetch('https://repovazio.vercel.app/api/cerebro/status').then(r => r.json()),
          fetch('https://repovazio.vercel.app/api/state').then(r => r.json()),
          fetch('https://repovazio.vercel.app/api/ranking').then(r => r.json())
        ]);
        
        resultado = `📊 STATUS DO SISTEMA

🧠 Cérebro: ${cerebro.status === 'fulfilled' ? cerebro.value.status : 'offline'}
📈 Score médio: ${cerebro.status === 'fulfilled' ? cerebro.value.score_medio_recente : '--'}
📅 Dia atual: ${state.status === 'fulfilled' ? state.value.dia_atual : '--'}
👥 Membros WA: ${state.status === 'fulfilled' ? state.value.membros_wa : 0}
🏆 Top ranking: ${ranking.status === 'fulfilled' && ranking.value.ranking?.[0] ? ranking.value.ranking[0].score : '--'}

✅ Sistema operacional!`;
        break;

      case 'criar_rota':
      case 'criar_arquivo':
        // Gerar código da rota usando Groq
        const codeResponse = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'llama-3.3-70b-versatile',
            messages: [{
              role: 'system',
              content: `Você é um gerador de código Next.js. Gere APENAS o código completo, sem explicações. Use export const runtime = 'edge' quando apropriado.`
            }, {
              role: 'user',
              content: `Crie o arquivo ${intent.detalhes.path || 'app/api/nova/route.js'} com: ${pergunta}`
            }],
            temperature: 0.5,
            max_tokens: 2000
          })
        });
        
        const codeData = await codeResponse.json();
        const code = codeData.choices[0].message.content.trim().replace(/```[a-z]*\n?/g, '').replace(/```/g, '');
        
        // Criar blob no GitHub
        const blobResp = await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/blobs`, {
          method: 'POST',
          headers: { 'Authorization': `token ${GH_PAT}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ content: code, encoding: 'utf-8' })
        });
        const blob = await blobResp.json();
        
        // Criar commit
        const mainRef = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main`, { headers: { 'Authorization': `token ${GH_PAT}` } })).json();
        const commitData = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/commits/${mainRef.object.sha}`, { headers: { 'Authorization': `token ${GH_PAT}` } })).json();
        
        const newTree = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/trees`, {
          method: 'POST',
          headers: { 'Authorization': `token ${GH_PAT}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            base_tree: commitData.tree.sha,
            tree: [{ path: intent.detalhes.path || 'app/api/nova/route.js', mode: '100644', type: 'blob', sha: blob.sha }]
          })
        })).json();
        
        const newCommit = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/commits`, {
          method: 'POST',
          headers: { 'Authorization': `token ${GH_PAT}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: `feat: ${pergunta.substring(0,50)}`,
            tree: newTree.sha,
            parents: [mainRef.object.sha]
          })
        })).json();
        
        await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/refs/heads/main`, {
          method: 'PATCH',
          headers: { 'Authorization': `token ${GH_PAT}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ sha: newCommit.sha, force: true })
        });
        
        acoes.push({ tipo: 'commit', commit: newCommit.sha.slice(0,7) });
        resultado = `✅ Arquivo criado e commitado!
📁 Path: ${intent.detalhes.path || 'app/api/nova/route.js'}
🔗 Commit: ${newCommit.sha.slice(0,7)}
🚀 Fazendo deploy...`;
        
        // Auto-deploy após criar arquivo
        const autoDeploy = await fetch('https://api.vercel.com/v13/deployments?forceNew=1', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${VERCEL_TOKEN || ''}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'repovazio',
            project: 'prj_rypXLpuS41CQt7sQYk5MM8kRQArr',
            target: 'production',
            gitSource: { type: 'github', repoId: '1075503208', ref: 'main', sha: newCommit.sha }
          })
        });
        const autoDeployData = await autoDeploy.json();
        resultado += `
✅ Deploy: ${autoDeployData.readyState || 'INITIALIZING'}`;
        break;

      default:
        // Para outras ações, apenas responder com Groq
        const defaultResp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: 'llama-3.3-70b-versatile',
            messages: [{
              role: 'system',
              content: 'Você é o assistente do psicologia.doc v7. Responda de forma concisa e útil.'
            }, {
              role: 'user',
              content: pergunta
            }],
            max_tokens: 1000
          })
        });
        const defaultData = await defaultResp.json();
        resultado = defaultData.choices[0].message.content;
    }

    return Response.json({
      resposta: resultado,
      intent: intent.acao,
      acoes_executadas: acoes
    });

  } catch (error) {
    console.error('Executor erro:', error);
    return Response.json({ erro: error.message, stack: error.stack }, { status: 500 });
  }
}