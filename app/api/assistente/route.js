export const runtime = 'edge';
export const maxDuration = 300;

const VERSION = 'V5-DEFINITIVO-2026-04-24';
const REPO = 'tafita81/Repovazio';

// ============ HELPERS GITHUB ============
async function gh(path, options = {}) {
  const r = await fetch(`https://api.github.com${path}`, {
    ...options,
    headers: {
      'Authorization': `token ${process.env.GH_PAT}`,
      'Accept': 'application/vnd.github.v3+json',
      'Content-Type': 'application/json',
      ...(options.headers || {})
    }
  });
  return r;
}

function encodeContent(text) {
  // Edge runtime safe base64 encode of UTF-8 string
  const bytes = new TextEncoder().encode(text);
  let out = '';
  for (let i = 0; i < bytes.length; i += 8192) {
    out += btoa(String.fromCharCode(...bytes.slice(i, i + 8192)));
  }
  return out;
}

async function readFile(filePath) {
  const r = await gh(`/repos/${REPO}/contents/${encodeURIComponent(filePath).replace(/%2F/g, '/')}?ref=main`, {
    headers: { 'Accept': 'application/vnd.github.v3.raw' }
  });
  if (!r.ok) throw new Error(`Não foi possível ler ${filePath}: ${r.status}`);
  return await r.text();
}

async function commitFile(filePath, content, message) {
  // 1. Get main ref
  const ref = await (await gh(`/repos/${REPO}/git/ref/heads/main`)).json();
  if (!ref.object) throw new Error('Falha ao buscar main: ' + JSON.stringify(ref).substring(0, 200));
  const baseSha = ref.object.sha;

  // 2. Get base commit (for tree)
  const baseCommit = await (await gh(`/repos/${REPO}/git/commits/${baseSha}`)).json();

  // 3. Create blob
  const blobBody = { content: encodeContent(content), encoding: 'base64' };
  const blob = await (await gh(`/repos/${REPO}/git/blobs`, {
    method: 'POST',
    body: JSON.stringify(blobBody)
  })).json();
  if (!blob.sha) throw new Error('Blob falhou: ' + JSON.stringify(blob).substring(0, 200));

  // 4. Create tree
  const tree = await (await gh(`/repos/${REPO}/git/trees`, {
    method: 'POST',
    body: JSON.stringify({
      base_tree: baseCommit.tree.sha,
      tree: [{ path: filePath, mode: '100644', type: 'blob', sha: blob.sha }]
    })
  })).json();
  if (!tree.sha) throw new Error('Tree falhou: ' + JSON.stringify(tree).substring(0, 200));

  // 5. Create commit
  const newCommit = await (await gh(`/repos/${REPO}/git/commits`, {
    method: 'POST',
    body: JSON.stringify({ message, tree: tree.sha, parents: [baseSha] })
  })).json();
  if (!newCommit.sha) throw new Error('Commit falhou: ' + JSON.stringify(newCommit).substring(0, 200));

  // 6. Update ref
  const upd = await gh(`/repos/${REPO}/git/refs/heads/main`, {
    method: 'PATCH',
    body: JSON.stringify({ sha: newCommit.sha, force: false })
  });
  if (!upd.ok) throw new Error('Ref update falhou: ' + upd.status);

  return newCommit.sha;
}

// ============ AI CALLERS ============
async function callGroq(messages, max_tokens = 1500) {
  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.GROQ_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'llama-3.3-70b-versatile',
      messages, max_tokens, temperature: 0.3
    })
  });
  if (!r.ok) throw new Error(`Groq ${r.status}: ${(await r.text()).substring(0, 200)}`);
  const d = await r.json();
  return d.choices[0].message.content;
}

async function callOpenAI(messages, max_tokens = 1500) {
  if (!process.env.OPENAI_API_KEY) throw new Error('OPENAI_API_KEY não configurada');
  const r = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      messages, max_tokens, temperature: 0.3
    })
  });
  if (!r.ok) throw new Error(`OpenAI ${r.status}`);
  const d = await r.json();
  return d.choices[0].message.content;
}

async function callAI(messages, max_tokens, stats) {
  try {
    const r = await callGroq(messages, max_tokens);
    stats.groq++;
    return { resposta: r, provider: 'groq' };
  } catch (e1) {
    try {
      const r = await callOpenAI(messages, max_tokens);
      stats.openai++;
      return { resposta: r, provider: 'openai' };
    } catch (e2) {
      throw new Error(`Groq+OpenAI falharam. Groq:${e1.message.substring(0, 80)} | OpenAI:${e2.message.substring(0, 80)}`);
    }
  }
}

// ============ INTENT DETECTION ============
function detectIntent(p) {
  const t = p.toLowerCase().trim();

  if (/^(oi|olá|ola|hi|hello|e\s*ai|eai)$/.test(t)) return 'greeting';
  if (/\bstatus\b|\bsistema\b|\bsa[uú]de\b|\bdiagn[oó]stico\b/.test(t)) return 'status';
  if (/\bdeploy\b|\bpublicar\b|\bsubir\s+(no|para|para\s+o)/.test(t)) return 'deploy';
  if (/\b(listar|listagem|lista|listing|ls)\b.*\b(arquivos|files|pasta|directory|dir)\b/.test(t)
      || /\bls\s+[\w/.\-]+/.test(t)) return 'list_files';
  if (/\b(criar|create|crie|gere|gerar|new|novo)\b.*\b(arquivo|file)\b/.test(t)) return 'create_file';
  if (/\b(ler|read|leia|mostr|veja|ver|cat|abrir)\b.*\b(arquivo|file|c[oó]digo|conte[uú]do)\b/.test(t)) return 'read_file';
  if (/\b(modificar|alterar|mudar|trocar|edit|editar|update|atualizar|substituir|replace)\b/.test(t)) return 'modify';
  if (/\b(ajuda|help|comandos|comando|capacidades|o\s+que\s+voc[eê]\s+faz)\b/.test(t)) return 'help';
  if (/\b(remover|deletar|apagar|delete|del|rm)\b.*\b(arquivo|file)\b/.test(t)) return 'delete_file';

  return 'chat';
}

// ============ MAIN HANDLER ============
export async function POST(req) {
  const t0 = Date.now();
  const log = [];
  const stats = { groq: 0, openai: 0, github: 0 };

  try {
    const body = await req.json();
    const pergunta = (body.pergunta || '').trim();
    if (!pergunta) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });

    const intent = detectIntent(pergunta);
    log.push(`intent=${intent}`);

    // ===== STATUS =====
    if (intent === 'status') {
      const [c, s] = await Promise.all([
        fetch('https://repovazio.vercel.app/api/cerebro/status').then(r => r.json()).catch(() => ({})),
        fetch('https://repovazio.vercel.app/api/state').then(r => r.json()).catch(() => ({}))
      ]);
      const ms = Date.now() - t0;
      return Response.json({
        resposta: `📊 **STATUS DO SISTEMA**\n\n` +
                  `🧠 Cérebro: ${c.status || 'offline'}\n` +
                  `📈 Score: ${c.score ?? '--'}\n` +
                  `📅 Dia: ${s.dia_atual ?? '--'}\n` +
                  `💥 Membros WhatsApp: ${s.membros_whatsapp ?? 0}\n` +
                  `🎬 Vídeos hoje: ${s.videos_hoje ?? 0}\n` +
                  `⚡ Latência: ${ms}ms\n\n` +
                  `✅ Sistema OPERACIONAL\n_v=${VERSION}_`,
        stats, log, ms
      });
    }

    // ===== DEPLOY =====
    if (intent === 'deploy') {
      const ref = await (await gh(`/repos/${REPO}/git/ref/heads/main`)).json();
      stats.github++;
      const sha = ref.object?.sha || '???????';
      return Response.json({
        resposta: `🚀 **DEPLOY**\n\n` +
                  `📌 Último commit: \`${sha.substring(0, 7)}\`\n` +
                  `🔗 [Ver deploys](https://vercel.com/tafita81s-projects/repovazio/deployments)\n\n` +
                  `Vercel detecta push automaticamente.\n_v=${VERSION}_`,
        stats, log
      });
    }

    // ===== GREETING =====
    if (intent === 'greeting') {
      return Response.json({
        resposta: `👋 Olá Rafael! Estou aqui para executar comandos no projeto psicologia.doc v7.\n\n` +
                  `Digite \`ajuda\` para ver os comandos disponíveis.\n_v=${VERSION}_`,
        stats, log
      });
    }

    // ===== HELP =====
    if (intent === 'help') {
      return Response.json({
        resposta: `🤖 **EXECUTOR ${VERSION}**\n\n` +
                  `**Comandos disponíveis:**\n\n` +
                  `📊 \`status\` — Status do sistema (cérebro, dia, membros)\n` +
                  `🚀 \`deploy\` — Último commit + link Vercel\n` +
                  `📂 \`listar arquivos em <pasta>\` — Listar conteúdo de pasta\n` +
                  `📄 \`ler arquivo <path>\` — Ler código de um arquivo\n` +
                  `✏️ \`criar arquivo <path> com <conteudo>\` — Criar novo arquivo no GitHub\n` +
                  `🔧 \`modificar arquivo <path>: <instrução>\` — Editar código existente\n` +
                  `🗑️ \`deletar arquivo <path>\` — Remover arquivo\n` +
                  `❓ \`ajuda\` — Esta mensagem\n\n` +
                  `**Chat livre:** qualquer outra pergunta vai pro Groq Llama 3.3 70B (fallback OpenAI gpt-4o-mini).\n\n` +
                  `_v=${VERSION}_`,
        stats, log
      });
    }

    // ===== LIST FILES =====
    if (intent === 'list_files') {
      const m = pergunta.match(/\b(?:em|in|de|do|da|pasta|folder)\s+([\w/.\-]+)/i)
                || pergunta.match(/\bls\s+([\w/.\-]+)/i);
      const path = m ? m[1].replace(/^\//, '') : '';
      const r = await gh(`/repos/${REPO}/contents/${path}?ref=main`);
      stats.github++;
      const dir = await r.json();

      if (!Array.isArray(dir)) {
        return Response.json({
          resposta: `❌ "${path}" não é uma pasta válida ou não existe.\n_v=${VERSION}_`,
          stats, log
        });
      }

      const files = dir
        .sort((a, b) => (a.type === 'dir' ? -1 : 1) - (b.type === 'dir' ? -1 : 1) || a.name.localeCompare(b.name))
        .map(f => `${f.type === 'dir' ? '📁' : '📄'} ${f.name}${f.size ? ` (${f.size}b)` : ''}`)
        .join('\n');

      return Response.json({
        resposta: `📂 **${path || 'raiz'}** (${dir.length} itens)\n\n${files}\n\n_v=${VERSION}_`,
        stats, log
      });
    }

    // ===== READ FILE =====
    if (intent === 'read_file') {
      const m = pergunta.match(/(?:arquivo|file|c[oó]digo|cat)\s+([\w/.\-]+)/i);
      if (!m) {
        return Response.json({
          resposta: `❌ Especifique o arquivo. Exemplo: \`ler arquivo app/page.js\`\n_v=${VERSION}_`,
          stats, log
        });
      }
      const path = m[1];
      try {
        const content = await readFile(path);
        stats.github++;
        const preview = content.length > 1800 ? content.substring(0, 1800) + '\n... [truncado, total: ' + content.length + ' chars]' : content;
        return Response.json({
          resposta: `📄 **${path}** (${content.length} chars, ${content.split('\n').length} linhas)\n\n\`\`\`\n${preview}\n\`\`\`\n_v=${VERSION}_`,
          stats, log
        });
      } catch (e) {
        return Response.json({
          resposta: `❌ Erro ao ler ${path}: ${e.message}\n_v=${VERSION}_`,
          stats, log
        });
      }
    }

    // ===== CREATE FILE =====
    if (intent === 'create_file') {
      const aiResp = await callAI([
        { role: 'system', content: 'Você extrai path e content de pedidos de criação de arquivo. Retorne APENAS um JSON válido na forma {"path": "caminho/relativo.ext", "content": "conteúdo completo do arquivo"}. Não inclua texto antes ou depois do JSON. Path deve ser relativo (sem barra inicial). Se o usuário não especificou conteúdo, gere um conteúdo razoável baseado no nome do arquivo.' },
        { role: 'user', content: pergunta }
      ], 3000, stats);

      let parsed;
      try {
        const json = aiResp.resposta.match(/\{[\s\S]*\}/)?.[0];
        parsed = JSON.parse(json);
      } catch (e) {
        return Response.json({
          resposta: `❌ AI não retornou JSON válido.\n\nResposta da AI:\n${aiResp.resposta.substring(0, 400)}\n_v=${VERSION}_`,
          stats, log
        });
      }

      if (!parsed.path || !parsed.content) {
        return Response.json({
          resposta: `❌ JSON sem path ou content: ${JSON.stringify(parsed).substring(0, 200)}\n_v=${VERSION}_`,
          stats, log
        });
      }

      try {
        const sha = await commitFile(parsed.path, parsed.content, `feat: criar ${parsed.path} via executor`);
        stats.github += 5;
        return Response.json({
          resposta: `✅ **ARQUIVO CRIADO**\n\n` +
                    `📄 Path: \`${parsed.path}\`\n` +
                    `📌 Commit: \`${sha.substring(0, 7)}\`\n` +
                    `📏 Tamanho: ${parsed.content.length} chars\n` +
                    `🤖 Conteúdo gerado por: ${aiResp.provider}\n\n` +
                    `🚀 Vercel está fazendo deploy automaticamente.\n_v=${VERSION}_`,
          stats, log
        });
      } catch (e) {
        return Response.json({
          resposta: `❌ Erro no commit: ${e.message}\n_v=${VERSION}_`,
          stats, log
        });
      }
    }

    // ===== MODIFY FILE =====
    if (intent === 'modify') {
      const m = pergunta.match(/(?:arquivo|file)\s+([\w/.\-]+)/i);
      if (!m) {
        return Response.json({
          resposta: `❌ Especifique o arquivo. Exemplo: \`modificar arquivo app/page.js: trocar título para Olá\`\n_v=${VERSION}_`,
          stats, log
        });
      }
      const path = m[1];
      const instrucao = pergunta.replace(m[0], '').replace(/^[\s,:.]+/, '').trim();

      let original;
      try { original = await readFile(path); stats.github++; }
      catch (e) {
        return Response.json({
          resposta: `❌ Não consegui ler ${path}: ${e.message}\n_v=${VERSION}_`,
          stats, log
        });
      }

      const aiResp = await callAI([
        { role: 'system', content: 'Você é um editor de código. Receberá um arquivo e uma instrução. Retorne APENAS o conteúdo COMPLETO do arquivo modificado, sem explicações, sem markdown fence (```), apenas o código puro do começo ao fim. Preserve indentação e estilo do original.' },
        { role: 'user', content: `INSTRUÇÃO: ${instrucao}\n\nARQUIVO ATUAL (${path}):\n${original}` }
      ], 4000, stats);

      // Strip markdown fences if AI included them despite instructions
      let novo = aiResp.resposta.trim();
      novo = novo.replace(/^```[\w]*\n/, '').replace(/\n```$/, '');

      if (novo === original) {
        return Response.json({
          resposta: `⚠️ AI não fez nenhuma mudança. Tente reformular a instrução.\n_v=${VERSION}_`,
          stats, log
        });
      }

      try {
        const sha = await commitFile(path, novo, `fix: ${instrucao.substring(0, 60)} via executor`);
        stats.github += 5;
        return Response.json({
          resposta: `✅ **ARQUIVO MODIFICADO**\n\n` +
                    `📄 Path: \`${path}\`\n` +
                    `📌 Commit: \`${sha.substring(0, 7)}\`\n` +
                    `📏 ${original.length} → ${novo.length} chars (Δ ${novo.length - original.length})\n` +
                    `🤖 Modificado por: ${aiResp.provider}\n` +
                    `📝 Instrução: ${instrucao.substring(0, 100)}\n\n` +
                    `🚀 Vercel está fazendo deploy.\n_v=${VERSION}_`,
          stats, log
        });
      } catch (e) {
        return Response.json({
          resposta: `❌ Erro ao commitar: ${e.message}\n_v=${VERSION}_`,
          stats, log
        });
      }
    }

    // ===== DELETE FILE =====
    if (intent === 'delete_file') {
      const m = pergunta.match(/(?:arquivo|file)\s+([\w/.\-]+)/i);
      if (!m) {
        return Response.json({
          resposta: `❌ Especifique o arquivo a deletar.\n_v=${VERSION}_`,
          stats, log
        });
      }
      const path = m[1];
      const meta = await (await gh(`/repos/${REPO}/contents/${path}?ref=main`)).json();
      stats.github++;
      if (!meta.sha) {
        return Response.json({
          resposta: `❌ Arquivo não encontrado: ${path}\n_v=${VERSION}_`,
          stats, log
        });
      }
      const r = await gh(`/repos/${REPO}/contents/${path}`, {
        method: 'DELETE',
        body: JSON.stringify({
          message: `chore: deletar ${path} via executor`,
          sha: meta.sha,
          branch: 'main'
        })
      });
      stats.github++;
      const d = await r.json();
      return Response.json({
        resposta: r.ok
          ? `🗑️ **ARQUIVO DELETADO**\n\n📄 \`${path}\`\n📌 Commit: \`${d.commit?.sha?.substring(0, 7)}\`\n_v=${VERSION}_`
          : `❌ Falha: ${d.message}\n_v=${VERSION}_`,
        stats, log
      });
    }

    // ===== CHAT (default fallback) =====
    const sysPrompt = `Você é o assistente do projeto psicologia.doc v7 (canal YouTube @psicologiadoc, persona "Daniela Coelho", dono Rafael, repo tafita81/Repovazio em repovazio.vercel.app, Next.js 14 + Supabase + Groq). Responda em PT-BR de forma direta e concisa. Se o usuário pedir algo executável (criar/modificar arquivos, status, deploy), sugira o comando exato a usar.`;
    const aiResp = await callAI([
      { role: 'system', content: sysPrompt },
      { role: 'user', content: pergunta }
    ], 1200, stats);

    return Response.json({
      resposta: aiResp.resposta + `\n\n_v=${VERSION} via ${aiResp.provider}_`,
      stats, log
    });

  } catch (error) {
    return Response.json({
      erro: error.message,
      stack: (error.stack || '').substring(0, 400),
      log,
      stats,
      version: VERSION
    }, { status: 500 });
  }
}
