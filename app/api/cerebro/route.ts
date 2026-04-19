export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const GK = process.env.GROQ_API_KEY;
const GMK = process.env.GEMINI_API_KEY;
const OAK = process.env.OPENAI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const TOPICS = ['Ansiedade','Apego ansioso','Narcisismo','Trauma infancia','Autossabotagem','Dependencia emocional','Gaslighting','Sindrome do impostor','Limites saudaveis','Psicologia do dinheiro','Burnout','Relacionamentos toxicos','Inteligencia emocional','Autoestima','Luto e perda','Ansiedade social','Vicio em validacao','TDAH adulto','Codependencia','Trauma de abandono','Apego evitativo','Alexitimia','Hipersensibilidade','Mindfulness','Psicossomatica','Depressao','Autocompaixao','Autoconhecimento'];
async function db(path: string, method = 'GET', body?: object) {
  if (!SU || !SK) return null;
  const r = await fetch(`${SU}/rest/v1/${path}`, { method, headers: { 'Content-Type': 'application/json', apikey: SK, Authorization: `Bearer ${SK}`, Prefer: method === 'POST' ? 'return=representation' : '' }, body: body ? JSON.stringify(body) : undefined });
  return r.ok ? r.json() : null;
}
async function groq(prompt: string, sys: string, maxTok = 1200) {
  if (!GK) return '';
  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', { method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${GK}` }, body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: maxTok, temperature: 0.85, messages: [{ role: 'system', content: sys }, { role: 'user', content: prompt }] }) });
  const d = await r.json();
  if (!r.ok) throw new Error(d.error?.message || 'Groq error');
  return d.choices?.[0]?.message?.content || '';
}
async function gemini(prompt: string, sys: string, maxTok = 900) {
  if (!GMK) return '';
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GMK}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ system_instruction: { parts: [{ text: sys }] }, contents: [{ parts: [{ text: prompt }] }], generationConfig: { maxOutputTokens: maxTok, temperature: 0.85 } }) });
  const d = await r.json();
  return d.candidates?.[0]?.content?.parts?.[0]?.text || '';
}
async function callAI(prompt: string, sys: string, maxTok = 1200): Promise<{text: string, model: string}> {
  try { if (GK) { const t = await groq(prompt, sys, maxTok); if (t) return { text: t, model: 'groq-llama-3.3-70b' }; } } catch {}
  try { if (GMK) { const t = await gemini(prompt, sys, Math.min(maxTok, 900)); if (t) return { text: t, model: 'gemini-2.0-flash' }; } } catch {}
  return { text: '', model: 'none' };
}
export async function GET(req: Request) {
  const auth = req.headers.get('authorization');
  if (process.env.CRON_SECRET && auth !== `Bearer ${process.env.CRON_SECRET}`) return Response.json({ error: 'Unauthorized' }, { status: 401 });
  const startedAt = new Date().toISOString();
  const ciclo = Date.now();
  const horaSP = new Date().toLocaleString('pt-BR', { timeZone: 'America/Sao_Paulo' });
  const memoria = (await db('cerebro_memoria?order=score.desc&limit=15')) || [];
  const topicsVirais = (memoria as any[]).filter((m: any) => m.score >= 85).map((m: any) => m.topic);
  const topicsRuins = (memoria as any[]).filter((m: any) => m.score < 70).map((m: any) => m.topic);
  let topicEscolhido: string;
  if (topicsVirais.length > 0 && Math.random() > 0.3) { topicEscolhido = topicsVirais[Math.floor(Math.random() * topicsVirais.length)]; }
  else { const disp = TOPICS.filter(t => !topicsRuins.includes(t)); topicEscolhido = disp[Math.floor(Math.random() * disp.length)]; }
  const sys = `Canal psicologia.doc documentarios anonimos psicologia. Tom narrador especialista anonimo segunda pessoa voce. CRP: zero diagnosticos zero promessa cura. Base DSM-5 APA. PNL espelhamento obrigatorio. NUNCA mencione IA nome pessoa. Linguagem 100pct humana. Hora Sao Paulo: ${horaSP}`;
  const ctxMem = (memoria as any[]).length > 0 ? `MEMORIA:\n${(memoria as any[]).slice(0,5).map((m: any) => `- ${m.topic}: score ${m.score}`).join('\n')}\n\n` : '';
  const prompt = `${ctxMem}Crie roteiro viral documentario YouTube 22-28min sobre "${topicEscolhido}".\nTITULO SEO (55-65 chars keyword inicio):\nGANCHO 0-30s (PNL espelhamento):\nPONTO 1 (dado cientifico DSM-5):\nPONTO 2 (caso anonimo identificacao):\nPONTO 3 (virada emocional esperanca):\nCTA FINAL (WhatsApp loop aberto):\nSCORE VIRAL ESTIMADO (0-100):\nINOVACAO APLICADA:`;
  const { text: script, model } = await callAI(prompt, sys, 1200);
  if (!script) return Response.json({ status: 'no_ai_available', model, hora_sp: horaSP }, { status: 503 });
  const scoreMatch = script.match(/SCORE VIRAL[^:]*:\s*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1]) : Math.floor(Math.random() * 15) + 80;
  const inovacaoMatch = script.match(/INOVACAO APLICADA[^:]*:\s*(.+?)(?:\n|$)/i);
  const inovacao = inovacaoMatch ? inovacaoMatch[1].trim() : 'variacao padrao';
  await db('registros', 'POST', { topic: topicEscolhido, script: script.slice(0, 3000), status: 'gerado', canal: 'psicologia.doc', created_at: new Date().toISOString(), plataforma: 'youtube', score, modelo: model, inovacao, ciclo_id: ciclo, memoria_usada: topicsVirais.length });
  const memEx = (memoria as any[]).find((m: any) => m.topic === topicEscolhido);
  if (memEx) { await db(`cerebro_memoria?id=eq.${memEx.id}`, 'PATCH', { score: Math.round(memEx.score * 0.6 + score * 0.4), vezes_gerado: (memEx.vezes_gerado || 1) + 1, estilo_vencedor: score > memEx.score ? inovacao : memEx.estilo_vencedor, ultimo_ciclo: new Date().toISOString() }); }
  else { await db('cerebro_memoria', 'POST', { topic: topicEscolhido, score, vezes_gerado: 1, estilo_vencedor: inovacao, criado_em: new Date().toISOString(), ultimo_ciclo: new Date().toISOString() }); }
  return Response.json({ status: 'cerebro_ok', ciclo_id: ciclo, topic: topicEscolhido, score, inovacao, model, memoria_usada: topicsVirais.length, topics_ruins_evitados: topicsRuins.length, hora_sp: horaSP, startedAt, completedAt: new Date().toISOString() });
}