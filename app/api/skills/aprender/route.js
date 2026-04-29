// app/api/skills/aprender/route.js
// Cron de aprendizado contínuo -- melhora skills a cada ciclo
// Chamado pelo cerebro a cada 15min, ou diretamente

export const runtime = 'edge';
export const maxDuration = 120;
const V = 'SKILLS-LEARN-V1';
const supa = (path, opts = {}) => {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  return fetch(`${url}${path}`, { ...opts, headers: {'apikey':key,'Authorization':`Bearer ${key}`,'Content-Type':'application/json','Prefer':'return=representation',...(opts.headers||{})}});};
const supaGet = async (t, q = '') => (await supa(`/rest/v1/${t}?${q}`)).json();
const supaPatch = async (t, q, d) => (await supa(`/rest/v1/${t}?${q}`, {method:'PATCH',body:JSON.stringify(d)})).json();
const supaInsert = async (t, d) => (await supa(`/rest/v1/${t}`, {method:'POST',body:JSON.stringify(d)})).json();
async function ai(prompt, max = 2000) {
  const keys = [];
  if (process.env.GROQ_API_KEY) keys.push(process.env.GROQ_API_KEY);
  for (let i = 2; i <= 5; i++) { const k = process.env[`GROQ_KEY_${i}`]; if (k) keys.push(k); }
  for (const key of keys) {
    try {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {method:'POST',headers:{'Authorization':`Bearer ${key}`,'Content-Type':'application/json'},body:JSON.stringify({model:'lolama-3.3-70b-versatile',messages:[{role:'user',content:prompt}],max_tokens:max,temperature:0.3})});
      if (r.ok) { return (await r.json()).choices[0].message.content; }
    } catch { continue; }
  }
  throw new Error('AI indisponvel');
}
const improveSkill = async (s) => await ai('Melhore esta skill em Markdown: '+s.name+'\nConteudo: '+s.content.substring(0,1000), 2000);
export async function GET(req) {
  const { searchParams } = new URL(req.url);
  const acao = searchParams.get('acao') || 'ciclo';
  const t0 = Date.now(); const log = [];
  try {
    if (acao === 'ciclo') {
      const skills = await supaGet('ia_skills', 'active=eq.true&order=score.asc&updated_at.asc&limit=1');
      if (Array.isArray(skills) && skills[0]) {
        const s = skills[0];
        const imp = await improveSkill(s);
        await supaPatch('ia_skills','id=eq.'+s.id,{content:imp,version:(s.version||1)+1,score:Math.min(100,(s.score||50)+3),updated_at:new Date().toISOString()});
        log.push('Melhorada: '+s.name);
      }
      const now = new Date().toISOString();
      await supa('/rest/v1/ia_cache?expires_at=lt.'+now,{method:'DELETE'}).catch(()=>{});
      log.push('Cache limpo');
      return Response.json({ok:true,log,ms:Date.now()-t0,version:V});
    }
    return Response.json({erro:'Acao desconhecida'},{status:400});
  } catch(e) { return Response.json({erro:e.message,version:V},{status:500}); }
}
export async function POST(req) { return GET(req); }
