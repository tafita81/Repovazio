export const dynamic = 'force-dynamic';
export const maxDuration = 30;

export async function POST(request: Request) {
  let topic = "Ansiedade moderna";

  try {
    const body = await request.json();
    if (body?.topic) topic = body.topic;
  } catch {}

  try {
    const res = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: "claude-sonnet-4-20250514",
        max_tokens: 1000,
        system:
          "Canal psicologia.doc. Narrador anônimo especialista. CRP compliance. DSM-5/APA. " +
          "PNL espelhamento — segunda pessoa 'você'. Sem diagnósticos, sem cura.",
        messages: [
          {
            role: "user",
            content: `Roteiro Short/Reel 60s sobre "${topic}" para psicologia.doc.\nGANCHO 0-3s + REVELAÇÃO 3-20s + IDENTIFICAÇÃO 20-40s + CTA 40-60s.\nTÍTULO + 5 HASHTAGS.`,
          },
        ],
      }),
    });

    const data = await res.json();
    const content = data.content?.[0]?.text || "fallback content";

    return Response.json({
      status: "ok",
      topic,
      content,
      createdAt: new Date().toISOString(),
    });
  } catch (e: any) {
    return Response.json({
      status: "fallback",
      topic,
      content: `Conteúdo sobre ${topic}: A ciência explica por que você sente isso. Documentado em psicologia.doc.`,
      createdAt: new Date().toISOString(),
    });
  }
}
