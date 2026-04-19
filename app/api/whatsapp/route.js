export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const GK = process.env.GROQ_API_KEY;
const GMK = process.env.GEMINI_API_KEY;
const OAK = process.env.OPENAI_API_KEY;
const WA_TOKEN = process.env.WHATSAPP_TOKEN;
const WA_PHONE = process.env.WHATSAPP_PHONE_ID;
const WA_GROUP = process.env.WHATSAPP_GROUP_ID;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;

const POOL = [
  'alguem mais sente que a ansiedade aparece quando as coisas estao indo bem?',
  'tava pensando hoje... quanto tempo a gente gasta fingindo estar bem',
  'o silencio de certas pessoas diz muito mais que qualquer palavra',
  'as vezes a gente precisa de um tempo sozinho pra processar tudo',
  'alguem aqui tambem teve que aprender a colocar limites com pessoas que ama?',
  'o corpo avisa antes da mente. dor nas costas, aperto no peito, cansaco sem razao',
  'crescer significa perceber que algumas pessoas nao vao mudar e tudo bem',
  'nao e fraqueza chorar. e o corpo liberando o que a mente nao consegue mais segurar',
  'ja repararam como a gente naturaliza o estresse como se fosse normal?',
  'o problema nao e sentir demais. e nao saber o que fazer com tudo isso',
];

async function ai(prompt, sys, tok) {
  tok = tok || 200;
  try {
    if (GK) {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + GK },
        body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: tok, temperature: 0.92,
          messages: [{ role: 'system', content: sys }, { role: 'user', content: prompt }] })
      });
      const d = await r.json();
      if (r.ok && d.choices && d.choices[0] && d.choices[0].message && d.choices[0].message.content)
        return { text: d.choices[0].message.content, model: 'groq' };
    }
  } catch {}
  try {
    if (GMK) {
      const r = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GMK, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system_instruction: { parts: [{ text: sys }] }, contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: tok, temperature: 0.92 } })
      });
      const d = await r.json();
      if (r.ok && d.candidates && d.candidates[0] && d.candidates[0].content && d.candidates[0].content.parts && d.candidates[0].content.parts[0])
        return { text: d.candidates[0].content.parts[0].text, model: 'gemini' };
    }
  } catch {}
  try {
    if (OAK) {
      const r = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + OAK },
        body: JSON.stringify({ model: 'gpt-4o-mini', max_tokens: tok, temperature: 0.92,
          messages: [{ role: 'system', content: sys }, { role: 'user', content: prompt }] })
      });
      const d = await r.json();
      if (r.ok && d.choices && d.choices[0] && d.choices[0].message && d.choices[0].message.content)
        return { text: d.choices[0].message.content, model: 'openai' };
    }
  } catch {}
  return { text: '', model: 'none' };
}

async function db(path, method, body) {
  if (!SU || !SK) return null;
  try {
    const r = await fetch(SU + '/rest/v1/' + path, {
      method: method || 'GET',
      headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK,
        Prefer: method === 'POST' ? 'return=representation' : '' },
      body: body ? JSON.stringify(body) : undefined
    });
    return r.ok ? r.json() : null;
  } catch { return null; }
}

async function enviarWA(texto) {
  if (!WA_TOKEN || !WA_PHONE || !WA_GROUP) return false;
  try {
    const r = await fetch('https://graph.facebook.com/v19.0/' + WA_PHONE + '/messages', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + WA_TOKEN },
      body: JSON.stringify({ messaging_product: 'whatsapp', to: WA_GROUP, type: 'text', text: { body: texto } })
    });
    return r.ok;
  } catch { return false; }
}

export async function GET() {
  const horaSP = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  const hora = parseInt((horaSP.split(', ')[1] || '12:').split(':')[0]);
  if (hora < 8 || hora >= 22) return Response.json({ status: 'silencio_noturno', hora: horaSP });

  const recentes = (await db('whatsapp_mensagens?order=timestamp.desc&limit=20')) || [];
  const naoRespondida = recentes.find(function(m) { return !m.respondido && (m.sentimento === 'angustia' || m.sentimento === 'tristeza'); });
  const sys = 'Voce e um membro anonimo de um grupo de psicologia no WhatsApp. Brasileiro, 28-35 anos. NUNCA revele que e IA. Tom humano informal, maximo 2 frases. Hora: ' + horaSP;

  let mensagem = '';
  let modelo = 'none';
  let motivo = '';

  if (naoRespondida && Math.random() < 0.4) {
    const result = await ai('Alguem disse: "' + naoRespondida.conteudo + '". Responda empatico curto (1-2 frases).', sys, 120);
    mensagem = result.text; modelo = result.model; motivo = 'resposta';
    if (naoRespondida.id) await db('whatsapp_mensagens?id=eq.' + naoRespondida.id, 'PATCH', { respondido: true });
  } else {
    const base = POOL[Math.floor(Math.random() * POOL.length)];
    const result = await ai('Baseado em: "' + base + '", escreva UMA mensagem curta para grupo de psicologia. Tom humano informal.', sys, 120);
    mensagem = result.text || base; modelo = result.model; motivo = 'iniciativa';
  }

  if (!mensagem) return Response.json({ status: 'sem_mensagem' });

  const delayMin = Math.floor(Math.random() * 43) + 2;
  const horarioEnvio = new Date(Date.now() + delayMin * 60000);
  await db('whatsapp_respostas', 'POST', { resposta: mensagem, modelo_ia: modelo, enviado: false, horario_programado: horarioEnvio.toISOString(), motivo: motivo });
  const enviado = await enviarWA(mensagem);
  return Response.json({ status: 'ok', mensagem: mensagem, modelo: modelo, delay_min: delayMin, enviado: enviado, motivo: motivo, hora_sp: horaSP });
}

export async function POST(req) {
  try {
    const body = await req.json();
    if (body['hub.verify_token'] === 'psicologiadoc_webhook') return new Response(body['hub.challenge'], { status: 200 });
    const messages = body.entry && body.entry[0] && body.entry[0].changes && body.entry[0].changes[0] && body.entry[0].changes[0].value && body.entry[0].changes[0].value.messages;
    if (!messages || !messages.length) return Response.json({ ok: true });
    for (const msg of messages) {
      const conteudo = (msg.text && msg.text.body) || '';
      if (!conteudo) continue;
      const remetente = msg.from;
      const sysA = 'Classifique o sentimento em uma palavra: alegria, tristeza, ansiedade, angustia, neutro, duvida. APENAS uma palavra.';
      const sentResult = await ai(conteudo, sysA, 10);
      await db('whatsapp_mensagens', 'POST', { remetente: remetente, conteudo: conteudo, tipo: 'texto', grupo_id: WA_GROUP || 'principal', sentimento: (sentResult.text || 'neutro').trim().toLowerCase() });
    }
    return Response.json({ ok: true });
  } catch (e) { return Response.json({ erro: e.message }, { status: 500 }); }
}