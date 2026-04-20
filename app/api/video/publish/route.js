export const dynamic = 'force-dynamic';
export const maxDuration = 60;
const YT_CID = process.env.YOUTUBE_CLIENT_ID;
const YT_CS = process.env.YOUTUBE_CLIENT_SECRET;
const YT_RT = process.env.YOUTUBE_REFRESH_TOKEN;
export async function POST(req) {
  const { video_url, titulo, descricao } = await req.json();
  if (!video_url || !titulo) return Response.json({ erro: 'video_url e titulo obrigatorios' }, { status: 400 });
  if (!YT_CID || !YT_CS || !YT_RT) return Response.json({ erro: 'YouTube OAuth pendente', status: 'pendente' }, { status: 202 });
  try {
    const tokenR = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({ client_id: YT_CID, client_secret: YT_CS, refresh_token: YT_RT, grant_type: 'refresh_token' })
    });
    const tokenD = await tokenR.json();
    if (!tokenD.access_token) return Response.json({ erro: 'OAuth refresh falhou' }, { status: 500 });
    const uploadR = await fetch('https://www.googleapis.com/upload/youtube/v3/videos?part=snippet,status', {
      method: 'POST', headers: { 'Authorization': 'Bearer ' + tokenD.access_token, 'Content-Type': 'application/json' },
      body: JSON.stringify({ snippet: { title: titulo, description: descricao || '' }, status: { privacyStatus: 'public' } })
    });
    const uploadD = await uploadR.json();
    return Response.json({ video_id: uploadD.id, status: 'published', url: 'https://youtube.com/watch?v=' + uploadD.id });
  } catch (e) { return Response.json({ erro: e.message }, { status: 500 }); }
}