export const runtime = 'edge';
export const maxDuration = 300;

export async function POST(req) {
  try {
    const { pergunta } = await req.json();
    if (!pergunta?.trim()) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const GROQ_KEY = process.env.GROQ_API_KEY;
    const GH_PAT = process.env.GH_PAT;
    
    let log = [];
    
    // PASSO 1: ANÁLISE CONTEXTUAL PROFUNDA
    log.push('🧠 Analisando contexto...');
    const contextResp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [{
          role: 'system',
          content: `Você é um analisador de intenções para o app psicologia.doc v7.

CONTEXTO DO APP:
- URL: https://repovazio.vercel.app
- Repo: tafita81/Repovazio
- Arquivo principal: app/ia/page.jsx (dashboard React)
- Stack: Next.js 14, Supabase, Groq

Quando o usuário diz algo como "troque a cor do número X" ou "mude o texto da página", você deve:
1. Identificar QUAL arquivo modificar (geralmente app/ia/page.jsx)
2. Identificar O QUE modificar (cor, texto, layout, etc)
3. Gerar um plano de ação técnico

RETORNE APENAS UM JSON:
{
  "tipo": "modificar_dashboard" | "criar_rota" | "fazer_deploy" | "status" | "outro",
  "arquivo_alvo": "app/ia/page.jsx" | "caminho/do/arquivo",
  "acao_especifica": "trocar_cor_numero" | "mudar_texto" | "adicionar_botao" | etc,
  "detalhes": {
    "elemento": "qual elemento modificar",
    "mudanca": "o que mudar",
    "novo_valor": "novo valor se aplicável"
  },
  "plano": ["passo 1", "passo 2", "passo 3"]
}

SEM EXPLICAÇÕES, APENAS JSON.`
        }, {
          role: 'user',
          content: pergunta
        }],
        temperature: 0.3,
        max_tokens: 800
      })
    });

    const contextData = await contextResp.json();
    const contextText = contextData.choices[0].message.content.trim();
    const jsonMatch = contextText.match(/{[sS]*}/);
    const contexto = JSON.parse(jsonMatch ? jsonMatch[0] : contextText);
    
    log.push(`✅ Entendi: ${contexto.tipo} em ${contexto.arquivo_alvo}`);

    // PASSO 2: BUSCAR CÓDIGO ATUAL (se modificação)
    if (contexto.tipo === 'modificar_dashboard' || contexto.tipo.includes('modificar')) {
      log.push(`📂 Buscando ${contexto.arquivo_alvo}...`);
      
      const fileResp = await fetch(`https://api.github.com/repos/tafita81/Repovazio/contents/${contexto.arquivo_alvo}`, {
        headers: H
      });
      const fileData = await fileResp.json();
      const codigoAtual = atob(fileData.content);
      
      log.push(`✅ Arquivo carregado (${codigoAtual.length} chars)`);
      
      // PASSO 3: GERAR MODIFICAÇÃO INTELIGENTE
      log.push('🔧 Gerando modificação...');
      const modResp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: [{
            role: 'system',
            content: `Você é um modificador de código React/Next.js.

REGRAS:
1. Receba o código atual
2. Aplique a modificação solicitada
3. Retorne APENAS o código completo modificado
4. SEM explicações, SEM markdown, SEM comentários extras
5. Preserve TODA a estrutura original
6. Modifique APENAS o que foi pedido

ATENÇÃO: Retorne o código COMPLETO (não apenas a parte modificada).`
          }, {
            role: 'user',
            content: `CÓDIGO ATUAL:
${codigoAtual}

MODIFICAÇÃO SOLICITADA:
Ação: ${contexto.acao_especifica}
Elemento: ${contexto.detalhes.elemento}
Mudança: ${contexto.detalhes.mudanca}
Novo valor: ${contexto.detalhes.novo_valor || ''}

Pedido original do usuário: ${pergunta}

Retorne o código COMPLETO modificado:`
          }],
          temperature: 0.2,
          max_tokens: 16000
        })
      });
      
      const modData = await modResp.json();
      let codigoNovo = modData.choices[0].message.content.trim();
      
      // Remover markdown se houver
      codigoNovo = codigoNovo.replace(/```[a-z]*\n?/g, '').replace(/```/g, '');
      
      log.push(`✅ Código modificado (${codigoNovo.length} chars)`);
      
      // PASSO 4: COMMITAR
      log.push('💾 Commitando...');
      const blobResp = await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/blobs`, {
        method: 'POST',
        headers: H,
        body: JSON.stringify({ content: codigoNovo, encoding: 'utf-8' })
      });
      const blob = await blobResp.json();
      
      const mainRef = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main`, { headers: H })).json();
      const commitData = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/commits/${mainRef.object.sha}`, { headers: H })).json();
      
      const newTree = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/trees`, {
        method: 'POST',
        headers: H,
        body: JSON.stringify({
          base_tree: commitData.tree.sha,
          tree: [{ path: contexto.arquivo_alvo, mode: '100644', type: 'blob', sha: blob.sha }]
        })
      })).json();
      
      const newCommit = await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/commits`, {
        method: 'POST',
        headers: H,
        body: JSON.stringify({
          message: `feat: ${pergunta.substring(0,60)}`,
          tree: newTree.sha,
          parents: [mainRef.object.sha]
        })
      })).json();
      
      await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/refs/heads/main`, {
        method: 'PATCH',
        headers: H,
        body: JSON.stringify({ sha: newCommit.sha, force: true })
      });
      
      log.push(`✅ Commit: ${newCommit.sha.slice(0,7)}`);
      
      // PASSO 5: AUTO-DEPLOY
      log.push('🚀 Fazendo deploy...');
      const deployResp = await fetch('https://api.vercel.com/v13/deployments?forceNew=1', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: 'repovazio',
          project: 'prj_rypXLpuS41CQt7sQYk5MM8kRQArr',
          target: 'production',
          gitSource: { type: 'github', repoId: '1075503208', ref: 'main', sha: newCommit.sha }
        })
      });
      const deployData = await deployResp.json();
      
      log.push(`✅ Deploy: ${deployData.readyState || 'INITIALIZING'}`);
      
      return Response.json({
        resposta: `✅ CONCLUÍDO!

${log.join('\n')}

📝 Resumo:
- Arquivo: ${contexto.arquivo_alvo}
- Modificação: ${contexto.acao_especifica}
- Commit: ${newCommit.sha.slice(0,7)}
- Deploy: ${deployData.readyState || 'INITIALIZING'}

🌐 Teste em: https://repovazio.vercel.app
⏱️ Aguarde ~40s para o deploy completar`,
        log,
        commit: newCommit.sha.slice(0,7)
      });
    }

    // Outros tipos (deploy, status, etc) - código anterior
    if (contexto.tipo === 'fazer_deploy') {
      const curSha = (await (await fetch(`https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main`, { headers: H })).json()).object.sha;
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
      return Response.json({ resposta: `✅ Deploy iniciado! SHA: ${curSha.slice(0,7)}\nStatus: ${deployData.readyState || 'INITIALIZING'}` });
    }

    if (contexto.tipo === 'status') {
      const [cerebro, state] = await Promise.allSettled([
        fetch('https://repovazio.vercel.app/api/cerebro/status').then(r => r.json()),
        fetch('https://repovazio.vercel.app/api/state').then(r => r.json())
      ]);
      return Response.json({ 
        resposta: `📊 STATUS\n🧠 Cérebro: ${cerebro.value?.status || 'offline'}\n📅 Dia: ${state.value?.dia_atual || '--'}` 
      });
    }

    // Fallback: resposta genérica
    const defaultResp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${GROQ_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [{ role: 'user', content: pergunta }],
        max_tokens: 1000
      })
    });
    const defaultData = await defaultResp.json();
    return Response.json({ resposta: defaultData.choices[0].message.content });

  } catch (error) {
    console.error('Super Executor erro:', error);
    return Response.json({ erro: error.message, stack: error.stack }, { status: 500 });
  }
}