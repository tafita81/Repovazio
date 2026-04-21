export const runtime = 'edge';
export const maxDuration = 300;

// SUPER EXECUTOR v2 - Capaz de criar apps do zero + autocorreção + testes
export async function POST(req) {
  try {
    const { pergunta, context } = await req.json();
    if (!pergunta?.trim()) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const GROQ_KEY = process.env.GROQ_API_KEY;
    const GH_PAT = process.env.GH_PAT;
    const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY || null;
    
    const H = { 'Authorization': 'token ' + GH_PAT, 'Content-Type': 'application/json' };
    
    let log = [];
    let usedGroq = 0;
    let usedAnthropic = 0;
    
    // FUNÇÃO: Chamar Groq com retry
    const callGroq = async (messages, maxTokens = 4000, retries = 3) => {
      for (let i = 0; i < retries; i++) {
        try {
          const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: { 'Authorization': \`Bearer \${GROQ_KEY}\`, 'Content-Type': 'application/json' },
            body: JSON.stringify({
              model: 'llama-3.3-70b-versatile',
              messages,
              temperature: 0.2,
              max_tokens: maxTokens
            })
          });
          const data = await resp.json();
          if (data.choices?.[0]?.message?.content) {
            usedGroq++;
            return data.choices[0].message.content.trim();
          }
        } catch (e) {
          if (i === retries - 1) throw e;
          await new Promise(r => setTimeout(r, 1000 * (i + 1)));
        }
      }
      throw new Error('Groq failed after retries');
    };
    
    // FUNÇÃO: Fallback Anthropic (só usa se Groq falhar)
    const callAnthropic = async (messages) => {
      if (!ANTHROPIC_KEY) throw new Error('Anthropic API key não configurada');
      const resp = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'x-api-key': ANTHROPIC_KEY,
          'anthropic-version': '2023-06-01',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4000,
          messages: messages.map(m => ({ role: m.role === 'system' ? 'user' : m.role, content: m.content }))
        })
      });
      const data = await resp.json();
      usedAnthropic++;
      return data.content[0].text;
    };
    
    // PASSO 1: ANÁLISE PROFUNDA
    log.push('🧠 Analisando pedido...');
    const analise = await callGroq([{
      role: 'system',
      content: \`Você é um analisador de pedidos para criar apps, modificar código, fazer deploys, etc.

CONTEXTO DO SISTEMA:
- App: psicologia.doc v7 (YouTube channel automático)
- Repo: tafita81/Repovazio
- Deploy: repovazio.vercel.app
- Stack: Next.js 14, Supabase, Groq, Vercel
- Arquivo principal: app/ia/page.jsx

RETORNE APENAS UM JSON:
{
  "tipo": "criar_app" | "modificar_codigo" | "fazer_deploy" | "testar" | "conectar_api" | "outro",
  "complexidade": "baixa" | "media" | "alta",
  "passos": ["passo 1", "passo 2", ...],
  "arquivos_criar": ["caminho/arquivo.js", ...],
  "arquivos_modificar": ["caminho/arquivo.js", ...],
  "testes_necessarios": ["teste 1", "teste 2", ...],
  "apis_conectar": ["api1", "api2", ...],
  "resumo": "resumo do que será feito"
}

SEM EXPLICAÇÕES, APENAS JSON.\`
    }, {
      role: 'user',
      content: pergunta
    }], 2000);
    
    const plano = JSON.parse(analise.match(/{[sS]*}/)[0]);
    log.push(\`✅ Plano: \${plano.resumo}\`);
    log.push(\`📊 Complexidade: \${plano.complexidade}\`);
    log.push(\`🎯 Tipo: \${plano.tipo}\`);
    
    // PASSO 2: EXECUÇÃO BASEADA NO TIPO
    
    // TIPO: MODIFICAR CÓDIGO
    if (plano.tipo === 'modificar_codigo' && plano.arquivos_modificar?.length > 0) {
      for (const arquivo of plano.arquivos_modificar) {
        log.push(\`📂 Modificando \${arquivo}...\`);
        
        // Buscar código atual
        const fileResp = await fetch(\`https://api.github.com/repos/tafita81/Repovazio/contents/\${arquivo}\`, { headers: H });
        const fileData = await fileResp.json();
        const codigoAtual = atob(fileData.content);
        
        // Gerar modificação com Groq
        let tentativas = 0;
        let codigoNovo = null;
        
        while (tentativas < 3 && !codigoNovo) {
          try {
            const mod = await callGroq([{
              role: 'system',
              content: 'Você modifica código. Retorne APENAS o código completo modificado, SEM markdown, SEM explicações.'
            }, {
              role: 'user',
              content: \`CÓDIGO ATUAL:
\${codigoAtual}

MODIFICAÇÃO: \${pergunta}

Retorne o código COMPLETO modificado:\`
            }], 16000);
            
            codigoNovo = mod.replace(/\`\`\`[a-z]*\\n?/g, '').replace(/\`\`\`/g, '');
            
            // TESTAR sintaxe básica
            if (arquivo.endsWith('.js') || arquivo.endsWith('.jsx')) {
              try {
                new Function(codigoNovo);
                log.push('✅ Sintaxe válida');
              } catch (e) {
                log.push(\`⚠️ Erro sintaxe: \${e.message}\`);
                if (tentativas < 2) {
                  log.push('🔄 Tentando corrigir...');
                  const correcao = await callGroq([{
                    role: 'system',
                    content: 'Corrija o erro de sintaxe. Retorne APENAS o código corrigido.'
                  }, {
                    role: 'user',
                    content: \`CÓDIGO COM ERRO:
\${codigoNovo}

ERRO: \${e.message}

Corrija:\`
                  }], 16000);
                  codigoNovo = correcao.replace(/\`\`\`[a-z]*\\n?/g, '').replace(/\`\`\`/g, '');
                }
              }
            }
          } catch (e) {
            tentativas++;
            if (tentativas >= 3) throw e;
          }
        }
        
        if (!codigoNovo) throw new Error('Falha ao gerar código após 3 tentativas');
        
        // Commitar
        log.push('💾 Commitando...');
        const blobResp = await fetch('https://api.github.com/repos/tafita81/Repovazio/git/blobs', {
          method: 'POST', headers: H,
          body: JSON.stringify({ content: codigoNovo, encoding: 'utf-8' })
        });
        const blob = await blobResp.json();
        
        const mainRef = await (await fetch('https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main', { headers: H })).json();
        const commitData = await (await fetch(\`https://api.github.com/repos/tafita81/Repovazio/git/commits/\${mainRef.object.sha}\`, { headers: H })).json();
        
        const newTree = await (await fetch('https://api.github.com/repos/tafita81/Repovazio/git/trees', {
          method: 'POST', headers: H,
          body: JSON.stringify({
            base_tree: commitData.tree.sha,
            tree: [{ path: arquivo, mode: '100644', type: 'blob', sha: blob.sha }]
          })
        })).json();
        
        const newCommit = await (await fetch('https://api.github.com/repos/tafita81/Repovazio/git/commits', {
          method: 'POST', headers: H,
          body: JSON.stringify({
            message: \`feat: \${pergunta.substring(0,60)}\`,
            tree: newTree.sha,
            parents: [mainRef.object.sha]
          })
        })).json();
        
        await fetch('https://api.github.com/repos/tafita81/Repovazio/git/refs/heads/main', {
          method: 'PATCH', headers: H,
          body: JSON.stringify({ sha: newCommit.sha, force: true })
        });
        
        log.push(\`✅ Commit: \${newCommit.sha.slice(0,7)}\`);
        
        // Auto-deploy
        log.push('🚀 Fazendo deploy...');
        await fetch('https://api.vercel.com/v13/deployments?forceNew=1', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'repovazio',
            project: 'prj_rypXLpuS41CQt7sQYk5MM8kRQArr',
            target: 'production',
            gitSource: { type: 'github', repoId: '1075503208', ref: 'main', sha: newCommit.sha }
          })
        });
   