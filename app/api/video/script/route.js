export const dynamic = 'force-dynamic';
const GK = process.env.GROQ_API_KEY;
const GMK = process.env.GEMINI_API_KEY;
async function ai(prompt, sys, tok) {
  tok = tok || 1500;
  if (GK) {
    try {
      const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
        method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + GK },
        body: JSON.stringify({ model: 'llama-3.3-70b-versatile', max_tokens: tok, temperature: 0.9,
          messages: [{ role: 'system', content: sys }, { role: 'user', content: prompt }] })
      });
      const d = await r.json();
      if (r.ok && d.choices && d.choices[0]) return { text: d.choices[0].message.content, model: 'groq' };
    } catch {}
  }
  return { text: 'IA indisponivel', model: 'fallback' };
}
export async function POST(req) {
  const { topico } = await req.json();
  if (!topico) return Response.json({ erro: 'topico obrigatorio' }, { status: 400 });
  const sys = 'Voce e roteirista de videos de psicologia. Crie roteiros 22-28 min PT-BR. Formato: INTRO + CORPO (5 secoes) + CONCLUSAO. Tom: acessivel, empatico, cientifico.';
  const prompt = 'Crie roteiro completo sobre: ' + topico + '. Inclua titulo chamativo, intro, 5 secoes praticas, conclusao com CTA grupo WhatsApp.';
  const result = await ai(prompt, sys, 1500);
  return Response.json({ roteiro: result.text, modelo: result.model, topico, duracao_estimada: '22-28min' });
}