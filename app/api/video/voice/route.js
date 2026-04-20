export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const EL = process.env.ELEVENLABS_API_KEY;
export async function POST(req) {
  const { texto } = await req.json();
  if (!texto) return Response.json({ erro: 'texto obrigatorio' }, { status: 400 });
  if (!EL) return Response.json({ erro: 'ELEVENLABS_API_KEY nao configurada', status: 'pendente' }, { status: 202 });
  try {
    const r = await fetch('https://api.elevenlabs.io/v1/text-to-speech/Rachel', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'xi-api-key': EL },
      body: JSON.stringify({ text: texto, model_id: 'eleven_multilingual_v2' })
    });
    if (!r.ok) return Response.json({ erro: 'ElevenLabs error' }, { status: r.status });
    const buffer = await r.arrayBuffer();
    return new Response(buffer, { headers: { 'Content-Type': 'audio/mpeg' } });
  } catch (e) { return Response.json({ erro: e.message }, { status: 500 }); }
}