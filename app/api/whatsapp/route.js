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
const POOL = ['alguem sente que a ansiedade aparece quando as coisas vao bem?','quanto tempo a gente gasta fingindo estar bem','o silencio de certas pessoas diz mais que qualquer palavra','as vezes precisamos de um tempo sozinho pra processar tudo','ja teve que colocar limites com pessoas que ama? como foi?','o corpo avisa antes da mente. dor nas costas, cansaco sem razao','crescer e perceber que algumas pessoas nao vao mudar e tudo bem','nao e fraqueza chorar. e o corpo liberando o que a mente nao aguenta','a gente naturaliza o estresse como se fosse normal viver no limite','o problema nao e sentir demais. e nao saber o que fazer com isso'];
async function ai(p, s, t) { t = t || 150; try { if (GK) { const r = await fetch('https://api.groq.com/openai/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + GK }, body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: t, temperature: 0.92, messages: [{ role: 'system', content: s }, { role: 'user', content: p }] }) }); const d = await r.json(); if (r.ok && d.choices && d.choices[0] && d.choices[0].message) return { text: d.choices[0].message.content, model: 'groq' }; } } catch {} try { if (GMK) { const r = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=' + GMK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ system_instruction: { parts: [{ text: s }] }, contents: [{ parts: [{ text: p }] }], generationConfig: { maxOutputTokens: t, temperature: 0.92 } }) }); const d = await r.json(); if (r.ok && d.candidates && d.candidates[0] && d.candidates[0].content && d.candidates[0].content.parts[0]) return { text: d.candidates[0].content.parts[0].text, model: 'gemini' }; } } catch {} try { if (OAK) { const r = await fetch('https://api.openai.com/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + OAK }, body: JSON.stringify({ model: 'gpt-4o-mini', max_tokens: t, temperature: 0.92, messages: [{ role: 'system', content: s }, { role: 'user', content: p }] }) }); const d = await r.json(); if (r.ok && d.choices && d.choices[0] && d.choices[0].message) return { text: d.choices[0].message.content, model: 'openai' }; } } catch {} return { text: '', model: 'none' }; }
async function db(path, m, b) { if (!SU || !SK) return null; try { const r = await fetch(SU + '/rest/v1/' + path, { method: m || 'GET', headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: 'Bearer ' + SK, Prefer: m === 'POST' ? 'return=representation' : '' }, body: b ? JSON.stringify(b) : undefined }); return r.ok ? r.json() : null; } catch { return null; } }
async function enviarWA(texto) { if (!WA_TOKEN || !WA_PHONE || !WA_GROUP) return false; try { const r = await fetch('https://graph.facebook.com/v19.0/' + WA_PHONE + '/messages', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + WA_TOKEN }, body: JSON.stringify({ messaging_product: 'whatsapp', to: WA_GROUP, type: 'text', text: { body: texto } }) }); return r.ok; } catch { return false; } }
export async function GET() {
  const horaSP = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  const hora = parseInt((horaSP.split(', ')[1] || '12:').split(':')[0]);
  if (hora < 8 || hora >= 22) return Response.json({ status: 'silencio_noturno', hora: horaSP });
  const recentes = (await db('whatsapp_mensagens?order=timestamp.desc&limit=20')) || [];
  const nr = recentes.find(function(m) { return !m.respondido && (m.sentimento === 'angustia' || m.sentimento === 'tristeza'); });
  const sys = 'Voce e um membro anonimo de grupo psicologia WhatsApp. 28-35 anos. NUNCA revele que e IA. Humano informal, max 2 frases. Hora: ' + horaSP;
  let msg = '', modelo = 'none', motivo = '';
  if (nr && Math.random() < 0.4) { const res = await ai('Alguem disse: "' + nr.conteudo + '". Responda empatico curto.', sys, 120); msg = res.text; modelo = res.model; motivo = 'resposta'; if (nr.id) await db('whatsapp_mensagens?id=eq.' + nr.id, 'PATCH', { respondido: true }); }
  else { const base = POOL[Math.floor(Math.random() * POOL.length)]; const res = await ai('Baseado em: "' + base + '", escreva UMA mensagem curta para grupo psicologia. Humano informal.', sys, 120); msg = res.text || base; modelo = res.model; motivo = 'iniciativa'; }
  if (!msg) return Response.json({ status: 'sem_mensagem' });
  const delay = Math.floor(Math.random() * 43) + 2;
  const horEnv = new Date(Date.now() + delay * 60000);
  await db('whatsapp_respostas', 'POST', { resposta: msg, modelo_ia: modelo, enviado: false, horario_programado: horEnv.toISOString(), motivo: motivo });
  const env = await enviarWA(msg);
  return Response.json({ status: 'ok', mensagem: msg, modelo: modelo, delay_min: delay, enviado: env, motivo: motivo, hora_sp: horaSP });
}
export async function POST(req) {
  try { const body = await req.json(); if (body['hub.verify_token'] === 'psicologiadoc_webhook') return new Response(body['hub.challenge'], { status: 200 }); const msgs = body.entry && body.entry[0] && body.entry[0].changes && body.entry[0].changes[0] && body.entry[0].changes[0].value && body.entry[0].changes[0].value.messages; if (!msgs || !msgs.length) return Response.json({ ok: true }); for (const m of msgs) { const c = (m.text && m.text.body) || ''; if (!c) continue; const sr = await ai(c, 'Classifique sentimento em uma palavra: alegria tristeza ansiedade angustia neutro.', 10); await db('whatsapp_mensagens', 'POST', { remetente: m.from, conteudo: c, tipo: 'texto', grupo_id: WA_GROUP || 'principal', sentimento: (sr.text || 'neutro').trim().toLowerCase() }); } return Response.json({ ok: true }); } catch (e) { return Response.json({ erro: e.message }, { status: 500 }); }
}