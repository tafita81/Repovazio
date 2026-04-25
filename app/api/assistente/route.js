export const runtime = 'edge';
export const maxDuration = 300;
export const dynamic = 'force-dynamic';

const VERSION = 'EXECUTOR-V4-OPUS47-2026-04-23-includes';

function detectIntent(p) {
  // p já em lowercase
  const KW = {
    status: ['status','estado do sistema','situação','situacao','saúde','saude','como está','como esta','health','monitor'],
    deploy: ['deploy','publicar','publicação','publicacao','build','sha','commit atual','último commit','ultimo commit','vercel'],
    list:   ['listar arquivos','liste arquivos','mostrar arquivos','quais arquivos','arquivos do projeto','estrutura','tree do projeto','file tree'],
    help:   ['ajuda','help','comandos','o que você faz','o que voce faz','capabilities','o que pode fazer']
  };
  for (const [intent, kws] of Object.entries(KW)) {
    for (const kw of kws) {
      if (p.includes(kw)) return intent;
    }
  }
  // Fallback simples por palavra única
  if (p.includes('status')) return 'status';
  if (p.includes('deploy')) return 'deploy';
  if (p.includes('listar') || p.includes('arquivos')) return 'list';
  if (p.includes('ajuda') || p.includes('help')) return 'help';
  return 'chat';
}

async function jget(u, h) {
  try {
    const r = await fetch(u, { headers: h || {}, cache: 'no-store' });
    return await r.json();
  } catch (e) { return { _erro: e.message }; }
}

async function getStatus() {
  const [c, s] = await Promise.all([
    jget('https://repovazio.vercel.app/api/cerebro/status'),
    jget('https://repovazio.vercel.app/api/state')
  ]);
  return { cerebro: c, state: s };
}

export async function POST(req) {
  const t0 = Date.now();
  const debug = [VERSION];
  try {
    const body = await req.json();
    const pergunta = body?.pergunta;
    if (!pergunta?.trim()) return Response.json({ erro: 'Pergunta vazia' }, { status: 400 });
    debug.push((Date.now()-t0) + 'ms recebido');
    const GROQ = process.env.GROQ_API_KEY;
    const GH = process.env.GH_PAT;
    const p = pergunta.toLowerCase();
    const intent = detectIntent(p);
    debug.push((Date.now()-t0) + 'ms intent=' + intent);

    if (intent === 'status') {
      const { cerebro, state } = await getStatus();
      debug.push((Date.now()-t0) + 'ms apis ok');
      const lines = [
        '📊 **STATUS DO SISTEMA**',
        '',
        '🧠 Cérebro: ' + (cerebro.status || 'offline'),
        '📈 Score: ' + (cerebro.score ?? '--'),
        '📅 Dia: ' + (state.dia_atual ?? '--'),
        '💥 Membros WhatsApp: ' + (state.membros_whatsapp ?? 0),
        '🎬 Vídeos hoje: ' + (cerebro.videos_hoje ?? 0),
        '',
        '✅ ' + (cerebro.status === 'online' ? 'Sistema OPERACIONAL' : 'Verificar logs'),
        '',
        '_v=' + VERSION + '_'
      ];
      return Response.json({ resposta: lines.join('\n'), _debug: debug, _fast: 'status', _version: VERSION });
    }

    if (intent === 'deploy') {
      const ref = await jget('https://api.github.com/repos/tafita81/Repovazio/git/ref/heads/main', { 'Authorization': 'token ' + GH });
      const sha = ref?.object?.sha?.slice(0,7) || '???';
      return Response.json({
        resposta: '🚀 **DEPLOY**\n\nÚltimo commit: `' + sha + '`\n\nVercel detecta push automaticamente.\n\n[Ver deploys](https://vercel.com/tafita81s-projects/repovazio/deployments)',
        _debug: debug, _fast: 'deploy', _version: VERSION
      });
    }

    if (intent === 'list') {
      const tree = await jget('https://api.github.com/repos/tafita81/Repovazio/git/trees/main?recursive=1', { 'Authorization': 'token ' + GH });
      const files = (tree.tree || []).filter(t => t.type === 'blob').slice(0, 50).map(t => '• ' + t.path);
      return Response.json({
        resposta: '📁 **ARQUIVOS** (top 50)\n\n' + files.join('\n'),
        _debug: debug, _fast: 'list', _version: VERSION
      });
    }

    if (intent === 'help') {
      return Response.json({
        resposta: '🤖 **COMANDOS**\n\n• `status` - status do sistema\n• `deploy` - info do último deploy\n• `listar arquivos` - listar arquivos\n• Qualquer outra pergunta - chat com IA contextualizada',
        _debug: debug, _fast: 'help', _version: VERSION
      });
    }

    // CHAT com Groq + contexto
    debug.push((Date.now()-t0) + 'ms groq');
    if (!GROQ) return Response.json({ resposta: '❌ GROQ_API_KEY ausente', _debug: debug });
    const ctx = await getStatus();
    const sys = 'Você é o assistente do psicologia.doc v7, projeto YouTube autônomo PT-BR. Stack: Next.js 14, Supabase, Groq, Vercel. Repo: tafita81/Repovazio. Status atual: cérebro=' + (ctx.cerebro.status || '?') + ', dia=' + (ctx.state.dia_atual ?? '?') + ', score=' + (ctx.cerebro.score ?? '?') + '. Responda direto e útil em português brasileiro.';
    const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + GROQ, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [{ role: 'system', content: sys }, { role: 'user', content: pergunta }],
        max_tokens: 1500, temperature: 0.7
      })
    });
    const d = await r.json();
    if (d.error) return Response.json({ resposta: '❌ Erro Groq: ' + d.error.message, _debug: debug });
    return Response.json({
      resposta: d.choices?.[0]?.message?.content || 'Sem resposta',
      _debug: debug, _model: 'groq-llama-3.3-70b', _version: VERSION
    });
  } catch (error) {
    return Response.json({ erro: error.message, _debug: debug, stack: (error.stack || '').substring(0, 300) }, { status: 500 });
  }
}