export const dynamic = 'force-dynamic';
export const maxDuration = 300;
const HG = process.env.HEYGEN_API_KEY;
export async function POST(req) {
  const { audio_url } = await req.json();
  if (!audio_url) return Response.json({ erro: 'audio_url obrigatorio' }, { status: 400 });
  if (!HG) return Response.json({ erro: 'HEYGEN_API_KEY nao configurada', status: 'pendente' }, { status: 202 });
  try {
    const r = await fetch('https://api.heygen.com/v1/video.generate', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Api-Key': HG },
      body: JSON.stringify({ avatar_id: 'Daniela_v1', audio_url, resolution: '1080p' })
    });
    const d = await r.json();
    if (!r.ok) return Response.json({ erro: 'HeyGen error', details: d }, { status: r.status });
    return Response.json({ video_id: d.video_id, status: d.status });
  } catch (e) { return Response.json({ erro: e.message }, { status: 500 }); }
}