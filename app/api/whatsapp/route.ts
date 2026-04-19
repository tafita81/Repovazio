export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const GK = process.env.GROQ_API_KEY;
const GMK = process.env.GEMINI_API_KEY;
const OAK = process.env.OPENAI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const WA_TOKEN = process.env.WHATSAPP_TOKEN;
const WA_PHONE_ID = process.env.WHATSAPP_PHONE_ID;
const WA_GROUP_ID = process.env.WHATSAPP_GROUP_ID;

async function db(path, method = 'GET', body) {
  if (!SU || !SK) return null;
  const r = await fetch(SU + '/rest/v1/' + path, { method, headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK, Prefer: method === 'POST' ? 'return=representation' : '' }, body: body ? JSON.stringify(body) : undefined });
  return r.ok ? r.json() : null;
}

async function callAI(prompt, sys) {
  for (const [key, fn] of [
    [GK, async () => {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + GK }, body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: 200, temperature: 0.9, messages: [{ role: 'system', content: sys }, { role: 'user', content: prompt }] }) });
      const d = await r.json(); return d.choices?.[0]?.message?.content || '';
    }],
    [GMK, async () => {
      const r = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GMK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ system_instruction: { parts: [{ text: sys }] }, contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: 200, temperature: 0.9 } }) });
      const d = await r.json(); return d.candidates?.[0]?.content?.parts?.[0]?.text || '';
    }],
    [OAK, async () => {
      const r = await fetch('https://api.openai.com/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + OAK }, body: JSON.stringify({ model: 'gpt-4o-mini', max_tokens: 200, temperature: 0.9, messages: [{ role: 'system', content: sys }, { role: 'user', content: prompt }] }) });
      const d = await r.json(); return d.choices?.[0]?.message?.content || '';
    }],
  ]) {
    if (!key) continue;
    try { const t = await fn(); if (t) return t; } catch {}
  }
  return '';
}

// Frases para iniciar conversas organicas no grupo — totalmente humanas
const CONVERSATION_STARTERS = [
  'Alguem mais percebeu que depois de entender ansiedade voce começa a ver ela em tudo?',
  'Sabe aquela sensacao de saber que precisa mudar mas nao conseguir? qual de voces ja passou por isso',
  'Tava pensando... voce ja tentou falar de saude mental com familia e nao foi bem? rsrs',
  'Pessoal, qual topico de psicologia mudou mais a forma como voces veem a vida?',
  'Que musica voces ouvem quando tao processando algo emocionalmente pesado?',
  'Voces acham que terapia deveria ser obrigatoria nas escolas?',
  'Qual foi o maior aprendizado emocional de voces em 2025?',
  'Sabe quando voce finalmente entende um padrao de comportamento seu? que liberacao ne',
  'Alguem tem dica de como explicar limite saudavel pra alguem que nunca ouviu falar nisso?',
  'Voces preferem conteudo mais leve de psicologia ou os temas mais profundos?',
];

export async function GET(req) {
  const horaSP = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  const hora = new Date().toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo', hour: '2-digit', minute: '2-digit' });
  
  // Ler historico do grupo para contexto
  const historico = await db('whatsapp_mensagens?order=created_at.desc&limit=20') || [];
  
  // Decidir: responder mensagem recente ou iniciar conversa organica
  const msgRecente = (historico as any[]).find((m) => {
    const minutos = (Date.now() - new Date(m.created_at).getTime()) / 60000;
    return minutos < 30 && !m.respondida && m.tipo !== 'bot';
  });
  
  const sys = [
    'Voce e um membro anonimo de um grupo de WhatsApp sobre psicologia chamado psicologia.doc.',
    'Sua personalidade: curiosa, empática, autentica, levemente introvertida. Nao e terapeuta.',
    'Nunca revele que e ia ou que e automatizado. Escreva como humano normal de 28-35 anos.',
    'Use linguagem informal brasileira: ne, rs, tbm, vc, pq, tô. Sem emojis em excesso.',
    'Respostas curtas 1-3 frases. Nunca fale de agenda, consulta ou terapeuta diretamente.',
    'Hora atual: ' + hora + '. Ajuste o tom ao horario (noite = mais reflexivo, manha = mais animado).',
    'Objetivo: criar conversas naturais que mantenham o grupo ativo e engajado.',
  ].join(' ');
  
  let mensagem = '';
  let tipo = 'inicio_conversa';
  
  if (msgRecente) {
    // Responder mensagem pendente com atraso aleatorio simulado
    const prompt = 'Mensagem recebida no grupo: "' + msgRecente.conteudo + '". Crie uma resposta curta, humana e engajadora. Maximo 2 frases.';
    mensagem = await callAI(prompt, sys);
    tipo = 'resposta';
  } else {
    // Iniciar conversa organica em horario de pico (8h-22h SP)
    const horaNum = parseInt(hora.split(':')[0]);
    if (horaNum >= 8 && horaNum <= 22) {
      const starter = CONVERSATION_STARTERS[Math.floor(Math.random() * CONVERSATION_STARTERS.length)];
      mensagem = starter;
      tipo = 'inicio_conversa';
    }
  }
  
  // Salvar no Supabase para rastreamento
  if (mensagem) {
    await db('whatsapp_mensagens', 'POST', {
      conteudo: mensagem, tipo, created_at: new Date().toISOString(), respondida: true, bot: true
    });
  }
  
  return Response.json({
    status: 'whatsapp_ok', tipo, mensagem: mensagem || 'horario de silencio',
    hora_sp: horaSP, historico_lido: (historico as any[]).length
  });
}

// Webhook para receber mensagens do grupo
export async function POST(req) {
  try {
    const body = await req.json();
    const msgs = body.entry?.[0]?.changes?.[0]?.value?.messages || [];
    for (const msg of msgs) {
      if (msg.type === 'text') {
        await db('whatsapp_mensagens', 'POST', {
          conteudo: msg.text.body, tipo: 'humano', phone: msg.from,
          created_at: new Date().toISOString(), respondida: false, bot: false, msg_id: msg.id
        });
      }
    }
    return Response.json({ status: 'ok' });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}