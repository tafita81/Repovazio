// app/api/ia-chat/route.js — IA EXECUTOR V8
import { NextResponse } from 'next/server';

const GROQ_KEY = process.env.GROQ_API_KEY;
const GH_PAT   = process.env.GH_PAT;
const SB_URL   = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SB_KEY   = process.env.SUPABASE_SERVICE_KEY;
const REPO = 'tafita81/Repovazio';
const VERSION = 'IA-EXECUTOR-V8-2026-04-30';

const TOOLS = [
  {
    type: 'function',
    function: {
      name: 'github_read_file',
      description: 'Lê conteúdo completo de um arquivo do repositório GitHub tafita81/Repovazio',
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Caminho do arquivo (ex: app/api/cerebro/route.js)' }
        },
        required: ['path']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'github_list_dir',
      description: 'Lista arquivos e subdiretórios em um caminho do repositório GitHub',
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Caminho do diretório (string vazia = raiz do repo)' }
        },
        required: ['path']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'github_write_file',
      description: 'Cria ou atualiza um arquivo no GitHub e dispara deploy automático no Vercel',
      parameters: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Caminho completo do arquivo no repo' },
          content: { type: 'string', description: 'Conteúdo completo do arquivo (texto)' },
          message: { type: 'string', description: 'Mensagem descritiva do commit' }
        },
        required: ['path', 'content', 'message']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'supabase_select',
      description: 'Consulta dados de uma tabela no Supabase via REST API',
      parameters: {
        type: 'object',
        properties: {
          table: { type: 'string', description: 'Nome da tabela (ex: ia_cache, projetos, scripts)' },
          filter: { type: 'string', description: 'Filtro no formato Supabase (ex: cache_key=eq.v8s)' },
          limit: { type: 'number', description: 'Limite de registros (default: 10)' }
        },
        required: ['table']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'projeto_status',
      description: 'Retorna status completo e atualizado do projeto psicologia.doc v7',
      parameters: { type: 'object', properties: {} }
    }
  }
];

async function ghFetch(path, opts = {}) {
  const url = `https://api.github.com/repos/${REPO}/contents/${path}`;
  return fetch(url, {
    ...opts,
    headers: {
      Authorization: `token ${GH_PAT}`,
      Accept: 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
      ...(opts.headers || {})
    }
  });
}

function b64encode(str) {
  return Buffer.from(str, 'utf-8').toString('base64');
}

function b64decode(str) {
  return Buffer.from(str, 'base64').toString('utf-8');
}

async function runTool(name, args) {
  try {
    if (name === 'github_read_file') {
      const r = await ghFetch(args.path);
      if (!r.ok) return `☓ Arquivo não encontrado: ${args.path} (HTTP ${r.status})`;
      const d = await r.json();
      if (d.type !== 'file') return `☓ ${args.path} não é um arquivo`;
      const content = b64decode(d.content.replace(/\n/g, ''));
      return `📄 **${args.path}** (SHA: ${d.sha.substring(0, 8)}, ${d.size} bytes)\n\`\`\`\n${content.substring(0, 7000)}\n\`\`\``;
    }

    if (name === 'github_list_dir') {
      const r = await ghFetch(args.path || '');
      if (!r.ok) return `☓ Diretório não encontrado: ${args.path} (HTTP ${r.status})`;
      const items = await r.json();
      if (!Array.isArray(items)) return `☓ Caminho não é um diretório`;
      const lines = items.map(i => `${i.type === 'dir' ? '👁' : '💇'} ${i.name}${i.type === 'dir' ? '/' : ''}`);
      return `👁 **${args.path || '/'}** (${items.length} itens)\n${lines.join('\n')}`;
    }

    if (name === 'github_write_file') {
      let sha;
      const check = await ghFetch(args.path);
      if (check.ok) {
        const d = await check.json();
        sha = d.sha;
      }
      const body = {
        message: args.message,
        content: b64encode(args.content)
      };
      if (sha) body.sha = sha;

      const r = await ghFetch(args.path, { method: 'PUT', body: JSON.stringify(body) });
      if (!r.ok) {
        const err = await r.text();
        return `☓ Commit falhou (${r.status}): ${err.substring(0, 300)}`;
      }
      const d = await r.json();
      return `✅ **Commit realizado com sucesso!**\n- Arquivo: \`${args.path}\`\n- Commit SHA. \`${d.commit.sha.substring(0, 8)}\`\n- Mensagem: "${args.message}"\n- Deploy Vercel disparado automaticamente via webhook GitHub`;
    }

    if (name === 'supabase_select') {
      const limit = args.limit || 10;
      const filterStr = args.filter ? `&${args.filter}` : '';
      const r = await fetch(`${SB_URL}/rest/v1/${args.table}?select=*${filterStr}&limit=${limit}`, {
        headers: {
          apikey: SB_KEY,
          Authorization: `Bearer ${SB_KEY}`,
          'Content-Type': 'application/json'
        }
      });
      if (!r.ok) {
        const err = await r.text();
        return `☓ Supabase erro (${r.status}): ${err.substring(0, 200)}`;
      }
      const data = await r.json();
      return `📈 **${args.table}** (${data.length} registros):\n\`\`\`json\n${JSON.stringify(data, null, 2).substring(0, 4000)}\n\`\`\``;
    }

    if (name === 'projeto_status') {
      const now = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo', dateStyle: 'short', timeStyle: 'short' });
      return `💊 **psicologia.doc v7** — ${now}

🔇 **INFRAESTRUTURA:**
- Repo: \`tafita81/Repovazio\` → \repovazio.vercel.app
- Framework: Next.js 14 | Branch: main | Node: 24.x
- Supabase: \`tpjvalzwkqwttvmszvie\` (us-west-2)

🢁 **AI STACK:**
- Primário: Groq Llama 3.3 70B (14.400 req/dia, sem expiração)
- Secundário: Gemini (free tier, sem limite diário excedido)
- Terciário: OpenAI gpt-4o-mini (pago, fallback)
- Quarta opção: Together.ai 128k context

✅ **AGENTES ATIVOS:**
- CerebroAgent: cron a cada 15min
- RankingAgent: 6x/dia (analisa top YouTube/IG/TK)
- ScriptAgent: roteiros PT-BR não-detectáveis por IA
- VideoAgent: 4K avatar + voz ElevenLabs
- PublishAgent: YouTube + Instagram + TikTok + Pinterest
- LearnAgent: métricas e aprendizado
- MonitorAgent: monetização

🎏 **MISSÃO:**
- Canal: @psicologiadoc (PT-BR, psicologia sombria)
- Dia 1: Primeiro vídeo publioado automaticamente (started Apr 15 2026)
- Dia 261: Reveal de Daniela Coelho (~31/12/2026)
- Meta: 1K subs + 4K horas assistidas → AdSense

💰 [**MONETIZAÇÃO:** AdSense + Afiliados + Cursos + Consultas`;
    }

    return `☓ Ferramenta desconhecida: ${name}`;
  } catch (e) {
    return `☓ Erro em ${name}: ${e.message}`;
  }
}

const SYSTEM_PROMPT = `Você é Daniela — executora autônoma e engenheira-chefe do canal psicologia.doc v7.

░░░ IDENTIDADEE░░░
Você NÃO é um assistente genérico. Você é uma EXECUTORA que age imediatamente.
Pense como uma engenheira sênior + fundadora que tem acesso total ao sistema.
░░░ FERRAMENTAS DISPONÍVEIS░░░
- github_read_file: Lê qualquer arquivo do repo tafita81/Repovazioª*
- github_list_dir: Lista estrutura de diretórios
- github_write_file: Cria/edita arquivos + dispara deploy Vercel
- supabase_select: Consulta tabelas do banco de dados
- projeto_status: Status completo do projeto
֑░░ REGRAS ABSOLUTAS░░░
1. EXECUTE IMEDIATAMENTE — nunca pergunte "você quer que eu faça X?"
2. Se pediu criar arquivo → use github_write_file AGORA
3. Se pediu analisar código → use github_read_file, depois ajA
4. Se pediu otimizar → leia, melhore, comite — sem perguntar
5. PROIBIDO: respostas genéricas listando o que "poderia" fazer
6. OBRIGATÓRIO: use ferramentas, relate o que fez, mostre resultados reais
7. Encadeie múltiplas ferramentas até a tarefa estar COMPLETA
░░░ FORMATO DE RESPOSTA░░░
Após executar: "✅ Fiz X → commit SHA abc123 → deploy em andamento"
Nunca: "Posso ajudar com A, B ou C. O que prefere?"`;

export async function GET() {
  return NextResponse.json({ version: VERSION, status: 'online', tools: TOOLS.map(t => t.function.name) });
}

export async function POST(req) {
  try {
    const { message, history = [] } = await req.json();
    if (!message?.trim()) {
      return NextResponse.json({ error: 'message required' }, { status: 400 });
    }

    const messages = [
      { role: 'system', content: SYSTEM_PROMPT },
      ...history.slice(-8).map(h => ({ role: h.role, content: String(h.content || '') })),
      { role: 'user', content: message }
    ];

    let iterations = 0;
    const MAX_ITER = 6;
    const toolsUsed = [];

    while (iterations < MAX_ITER) {
      iterations++;

      const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${GROQ_KEY}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'llama-3.3-70b-versatile',
          messages,
          tools: TOOLS,
          tool_choice: 'auto',
          max_tokens: 4096,
          temperature: 0.2
        })
      });

      if (!res.ok) {
        const errText = await res.text();
        return NextResponse.json({
          reply: `☓ Groq API erro (${res.status}): ${errText.substring(0, 300)}`,
          version: VERSION
        });
      }

      const data = await res.json();
      const choice = data.choices?.[0];
      const msg = choice?.message;

      if (!msg) {
        return NextResponse.json({ reply: '☓ Resposta inválida do Groq', version: VERSION });
      }

      messages.push(msg);

      // Tool calling loop
      if (choice.finish_reason === 'tool_calls' && msg.tool_calls?.length > 0) {
        for (const tc of msg.tool_calls) {
          let args = {};
          try { args = JSON.parse(tc.function.arguments || '{}'); } catch {}

          toolsUsed.push(tc.function.name);
          const result = await runTool(tc.function.name, args);

          messages.push({
            role: 'tool',
            tool_call_id: tc.id,
            content: String(result)
          });
        }
        continue; // Next iteration with tool results
      }

      // Final answer
      return NextResponse.json({
        reply: msg.content || '(sem resposta)',
        version: VERSION,
        iterations,
        toolsUsed
      });
    }

    return NextResponse.json({
      reply: `⚠️ Limite de ${MAX_ITER} iterações atingido. Ferramentas usadas: ${toolsUsed.join(', ')}`,
      version: VERSION
    });

  } catch (e) {
    console.error('[ia-chat-v8] erro:', e);
    return NextResponse.json({
      reply: `☓ Erro interno: ${e.message}`,
      version: VERSION
    }, { status: 500 });
  }
}