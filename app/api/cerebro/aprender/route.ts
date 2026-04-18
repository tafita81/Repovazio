export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const GK = process.env.GEMINI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const GM = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

async function db(path: string, method = "GET", body?: object) {
  if (!SU || !SK) return null;
  const r = await fetch(`${SU}/rest/v1/${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      apikey: SK!,
      Authorization: `Bearer ${SK}`,
      Prefer: method === "POST" ? "return=representation" : "",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return r.ok ? r.json() : null;
}

async function gemini(prompt: string): Promise<string> {
  if (!GK) return "{}";
  const r = await fetch(`${GM}?key=${GK}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { maxOutputTokens: 400, temperature: 0.3 }
    }),
  });
  const d = await r.json();
  return d.candidates?.[0]?.content?.parts?.[0]?.text || "{}";
}

export async function GET(req: Request) {
  const auth = req.headers.get("authorization");
  if (process.env.CRON_SECRET && auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  // Buscar todos os resultados das últimas 24h
  const ontemISO = new Date(Date.now() - 86400000).toISOString();
  const resultados = await db(`registros?created_at=gte.${ontemISO}&order=score.desc&select=topic,score,inovacao,ciclo_id`);
  const memoria = await db("cerebro_memoria?order=score.desc&limit=20");

  if (!resultados || resultados.length === 0) {
    return Response.json({ status: "sem_dados", message: "Nenhum resultado nas últimas 24h" });
  }

  // Análise de aprendizado via Gemini
  const analise = await gemini(`Você é o sistema de aprendizado do cérebro psicologia.doc.
Analise estes resultados das últimas 24h e gere insights de otimização.

RESULTADOS (topic, score):
${resultados.slice(0,10).map((r: any) => `${r.topic}: ${r.score} | ${r.inovacao || ""}`).join("\n")}

MEMÓRIA ACUMULADA (melhores tópicos históricos):
${(memoria || []).slice(0,5).map((m: any) => `${m.topic}: ${m.score} (${m.vezes_gerado}x gerado)`).join("\n")}

Responda APENAS com JSON válido no formato:
{
  "padroes_virais": ["padrão 1", "padrão 2"],
  "padroes_ruins": ["padrão ruim 1"],
  "proximos_topics_prioritarios": ["topic1", "topic2", "topic3"],
  "ajuste_tom": "instrução de melhoria de tom",
  "score_medio_24h": 85,
  "tendencia": "crescendo|estavel|caindo",
  "insight_principal": "o que aprendeu hoje"
}`);

  // Parse seguro do JSON
  let insights: any = {};
  try {
    const clean = analise.replace(/```json|```/g, "").trim();
    insights = JSON.parse(clean);
  } catch {
    insights = { insight_principal: "análise em processamento", tendencia: "estavel" };
  }

  // Salvar aprendizado no banco
  await db("cerebro_aprendizado", "POST", {
    data: new Date().toISOString(),
    total_ciclos_24h: resultados.length,
    score_medio: insights.score_medio_24h || Math.round(resultados.reduce((s: number, r: any) => s + r.score, 0) / resultados.length),
    padroes_virais: insights.padroes_virais || [],
    padroes_ruins: insights.padroes_ruins || [],
    proximos_topics: insights.proximos_topics_prioritarios || [],
    tendencia: insights.tendencia || "estavel",
    insight: insights.insight_principal || "",
    ajuste_tom: insights.ajuste_tom || "",
  });

  return Response.json({
    status: "aprendizado_ok",
    ciclos_analisados: resultados.length,
    insights,
    timestamp: new Date().toISOString(),
  });
}
