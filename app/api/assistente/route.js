export const runtime = 'edge';
export const maxDuration = 60;

export async function POST(req) {
  try {
    const { pergunta, historico = [] } = await req.json();
    
    if (!pergunta?.trim()) {
      return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });
    }

    // Usar Anthropic API (precisa adicionar ANTHROPIC_API_KEY no Vercel env)
    // Se não tiver, usa Groq como fallback (mas sem MCPs)
    const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY;
    const GROQ_KEY = process.env.GROQ_API_KEY;
    const OPENAI_KEY = process.env.OPENAI_API_KEY;

    // PRIORIDADE 1: Anthropic API (tem MCPs)
    if (ANTHROPIC_KEY) {
      const messages = [
        ...historico,
        { role: 'user', content: pergunta }
      ];

      // MCPs disponíveis (todos os que você tem conectados)
      const mcpServers = [
        { type: 'url', url: 'https://drivemcp.googleapis.com/mcp/v1', name: 'Google Drive' },
        { type: 'url', url: 'https://mcp.vercel.com', name: 'Vercel' },
        { type: 'url', url: 'https://mcp.supabase.com/mcp', name: 'Supabase' },
        { type: 'url', url: 'https://mcp.canva.com/mcp', name: 'Canva' },
        { type: 'url', url: 'https://mcp.clickup.com/mcp', name: 'ClickUp' },
        { type: 'url', url: 'https://calendarmcp.googleapis.com/mcp/v1', name: 'Google Calendar' },
        { type: 'url', url: 'https://mcp.notion.com/mcp', name: 'Notion' },
        { type: 'url', url: 'https://gmailmcp.googleapis.com/mcp/v1', name: 'Gmail' }
      ];

      const response = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'x-api-key': ANTHROPIC_KEY,
          'anthropic-version': '2023-06-01'
        },
        body: JSON.stringify({
          model: 'claude-sonnet-4-20250514',
          max_tokens: 4000,
          messages,
          mcp_servers: mcpServers,
          system: 'Você é um assistente executor completo do projeto psicologia.doc v7. Você tem acesso total ao GitHub (tafita81/Repovazio), Vercel (repovazio.vercel.app), Supabase e todas as redes sociais. Você pode fazer commits, deploys, criar rotas, modificar código, publicar posts e TUDO mais. Use os MCPs disponíveis para executar as ações solicitadas pelo usuário. Sempre confirme a ação executada e forneça detalhes do que foi feito.'
        })
      });

      if (!response.ok) {
        throw new Error(`Anthropic API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Extrair resposta (pode ter múltiplos blocos de conteúdo)
      const resposta = data.content
        .filter(item => item.type === 'text')
        .map(item => item.text)
        .join('\n');

      return Response.json({ resposta, modelo: 'anthropic-sonnet-4' });
    }

    // PRIORIDADE 2: Groq (rápido mas SEM MCPs)
    if (GROQ_KEY) {
      const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GROQ_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages: [
            {
              role: 'system',
              content: 'Você é um assistente do psicologia.doc v7. IMPORTANTE: Você NÃO tem acesso direto a GitHub, Vercel ou Supabase porque está rodando via Groq. Para executar ações reais, peça ao usuário que adicione ANTHROPIC_API_KEY no Vercel env. Por enquanto, você pode apenas SUGERIR código e comandos que o usuário pode executar manualmente.'
            },
            ...historico,
            { role: 'user', content: pergunta }
          ],
          max_tokens: 2000,
          temperature: 0.7
        })
      });

      const data = await response.json();
      return Response.json({ 
        resposta: data.choices[0].message.content,
        modelo: 'groq-llama-3.3-70b',
        aviso: 'MCPs não disponíveis. Para executar ações reais (commits, deploys, etc), adicione ANTHROPIC_API_KEY no Vercel env.'
      });
    }

    // PRIORIDADE 3: OpenAI (pago, fallback final, SEM MCPs)
    if (OPENAI_KEY) {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${OPENAI_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [
            {
              role: 'system',
              content: 'Você é um assistente do psicologia.doc v7. IMPORTANTE: Você NÃO tem acesso direto a GitHub, Vercel ou Supabase. Para executar ações reais, peça ao usuário que adicione ANTHROPIC_API_KEY no Vercel env. Por enquanto, você pode apenas SUGERIR código e comandos.'
            },
            ...historico,
            { role: 'user', content: pergunta }
          ],
          max_tokens: 2000
        })
      });

      const data = await response.json();
      return Response.json({ 
        resposta: data.choices[0].message.content,
        modelo: 'openai-gpt-4o-mini',
        aviso: 'MCPs não disponíveis. Para executar ações reais, adicione ANTHROPIC_API_KEY no Vercel env.'
      });
    }

    return Response.json({ 
      erro: 'Nenhuma API key configurada. Adicione ANTHROPIC_API_KEY (recomendado), GROQ_API_KEY ou OPENAI_API_KEY no Vercel env.' 
    }, { status: 500 });

  } catch (error) {
    console.error('API Executor erro:', error);
    return Response.json({ erro: error.message }, { status: 500 });
  }
}