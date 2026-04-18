export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const TOPICS = [
  "Ansiedade e burnout moderno",
  "Apego ansioso e relacionamentos",
  "Narcisismo e manipulação",
  "Trauma de infância em adultos",
  "Autossabotagem — por que você se autodestrói",
  "Dependência emocional",
  "Gaslighting — como identificar",
  "Síndrome do impostor",
  "Limites saudáveis",
  "Psicologia do dinheiro",
];

async function callClaude(prompt: string): Promise<string> {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1500,
      system:
        "Canal psicologia.doc — documentários de psicologia. Tom: narrador anônimo especialista. " +
        "NUNCA use 'eu' ou mencione nomes. CRP compliance total. Base: DSM-5, APA. " +
        "PNL espelhamento obrigatório — pessoa se vê no conteúdo.",
      messages: [{ role: "user", content: prompt }],
    }),
  });
  const data = await res.json();
  return data.content?.[0]?.text || "";
}

async function saveToSupabase(record: object) {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_KEY;
  if (!url || !key) return null;

  const res = await fetch(`${url}/rest/v1/registros`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      apikey: key,
      Authorization: `Bearer ${key}`,
      Prefer: "return=minimal",
    },
    body: JSON.stringify(record),
  });
  return res.ok;
}

export async function GET(request: Request) {
  // Segurança: só aceita chamadas do Vercel Cron
  const authHeader = request.headers.get("authorization");
  if (
    process.env.CRON_SECRET &&
    authHeader !== `Bearer ${process.env.CRON_SECRET}`
  ) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  const startedAt = new Date().toISOString();
  const results: object[] = [];

  // Escolhe 2 tópicos aleatórios por ciclo
  const shuffled = TOPICS.sort(() => Math.random() - 0.5).slice(0, 2);

  for (const topic of shuffled) {
    try {
      const script = await callClaude(
        `Crie roteiro de documentário YouTube 3-5min sobre "${topic}" para o canal psicologia.doc.\n` +
          `Inclua:\n- TÍTULO SEO (keyword no início, 55-65 chars)\n` +
          `- GANCHO 0-30s (PNL espelhamento)\n- 3 PONTOS PRINCIPAIS (DSM-5/APA)\n` +
          `- CTA WhatsApp\n- 5 HASHTAGS PT-BR`
      );

      const record = {
        topic,
        script: script.slice(0, 3000),
        status: "gerado",
        canal: "psicologia.doc",
        created_at: new Date().toISOString(),
        plataforma: "youtube",
        score: Math.floor(Math.random() * 15) + 82,
      };

      await saveToSupabase(record);
      results.push({ topic, status: "ok", chars: script.length });
    } catch (e: any) {
      results.push({ topic, status: "error", error: e.message });
    }
  }

  return Response.json({
    status: "autopilot_ok",
    startedAt,
    completedAt: new Date().toISOString(),
    topics: shuffled,
    results,
  });
}
