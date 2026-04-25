export const runtime = 'edge';
export const maxDuration = 300;
export const dynamic = 'force-dynamic';

const VERSION = 'EXECUTOR-V3-OPUS47-' + '2026-04-23';

const RX_STATUS = /\\b(status|estado|situa[cç][aã]o|sa[uú]de|info|como.{0,5}(esta|t[aá])|monitor)\\b/i;
const RX_DEPLOY = /\\b(deploy|publica[rt]?|atualizar|build|sha|commit)\\b/i;
const RX_LIST   = /\\b(list[ae]r?|mostr[ae]|quais|files?|arquivos?|estrutura|tree)\\b/i;
const RX_HELP   = /\\b(ajuda|help|comandos?|o que.{0,5}faz|capabilities)\\b/i;

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
    
    debug.push((Date.now()-t0) + 'ms recebido: ' + pergunta.substring(0, 80));
    
    const GROQ = process.env.GROQ_API_KEY;
    const GH = process.env.GH_PAT;
    const p = pergunta.toLowerCase();
    
    // FAST PATH: STATUS
    if (RX_STATUS.test(p)) {
      debug.push((Date.now()-t0) + 'ms FAST_PATH=status');
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
        '✅ Sistema ' + (cerebro.status === 'online' ? 'OPERACIONAL' : 'verificar logs'),
        '',
        '_v=' + VERSION + '_'
      ];
      return Response.json({ resposta: lines.join('\\n'), _debug: debug, _fast: 'status' });
    }
    
    // FAST PATH: DEPLOY
    if (RX_DEPLOY.test(p)) {
      debug.push((Date.now()-t0) + 'ms FAST_PATH=deploy');
      const ref = await jget('https://api.github.com/repos/' + 'tafita81/Repovazio' + '/git/ref/heads/main', { 'Authorization': 'token ' + GH });
      const sha = ref?.object?.sha?.slice(0,7) || '???';
      
      return Response.json({
        resposta: '🚀 **DEPLOY STATUS**\\n\\nÚltimo commit: `' + sha + '`\\n\\nVercel detecta push automaticamente.\\n\\n[Ver deploys](https://vercel.com/tafita81s-projects/repovazio/deployments)',
        _debug: debug,
        _fast: 'deploy'
      });
    }
    
    // FAST PATH: LIST FILES
    if (RX_LIST.test(p)) {
      debug.push((Date.now()-t0) + 'ms FAST_PATH=list');
      const tree = await jget('https://api.github.com/repos/tafita81/Repovazio/git/trees/main?recursive=1', { 'Authorization': 'token ' + GH });
      const files = (tree.tree || []).filter(t => t.type === 'blob').slice(0, 50).map(t => '• ' + t.path);
      return Response.json({
        resposta: '📁 **ARQUIVOS DO PROJETO** (top 50)\\n\\n' + files.join('\\n'),
        _debug: debug,
        _fast: 'list'
      });
    }
    
    // FAST PATH: HELP
    if (RX_HELP.test(p)) {
      return Response.json({
        resposta: '🤖 **COMANDOS DISPONÍVEIS**\\n\\n• `status` - status do sistema\\n• `deploy` - info do último deploy\\n• `listar arquivos` - listar arquivos\\n• Qualquer outra pergunta - chat com IA\\n\\n_v=' + VERSION + '_',
        _debug: debug,
        _fast: 'help'
      });
    }
    
    // SMART PATH: Groq com contexto
    debug.push((Date.now()-t0) + 'ms SMART_PATH=groq');
    if (!GROQ) {
      return Response.json({ resposta: '❌ GROQ_API_KEY não configurada', _debug: debug });
    }
    
    const ctx = await getStatus();
    const sysPrompt = 'Você é o assistente do psicologia.doc v7, projeto YouTube autônomo PT-BR. Stack: Next.js 14, Supabase, Groq, Vercel. Repo: tafita81/Repovazio. Status atual: cérebro=' + (ctx.cerebro.status || '?') + ', dia=' + (ctx.state.dia_atual ?? '?') + '. Responda direto e útil em português.';
    
    const groqR = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: { 'Authorization': 'Bearer ' + GROQ, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama-3.3-70b-versatile',
        messages: [
          { role: 'system', content: sysPrompt },
          { role: 'user', content: pergunta }
        ],
        max_tokens: 1500,
        temperature: 0.7
      })
    });
    const groqD = await groqR.json();
    debug.push((Date.now()-t0) + 'ms groq respondeu');
    
    if (groqD.error) return Response.json({ resposta: '❌ Erro Groq: ' + groqD.error.message, _debug: debug });
    
    return Response.json({
      resposta: groqD.choices?.[0]?.message?.content || 'Sem resposta',
      _debug: debug,
      _model: 'groq-llama-3.3-70b',
      _version: VERSION
    });
    
  } catch (error) {
    return Response.json({ erro: error.message, _debug: debug, stack: (error.stack || '').substring(0, 300) }, { status: 500 });
  }
}