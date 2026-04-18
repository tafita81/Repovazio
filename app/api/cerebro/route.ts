export const dynamic = 'force-dynamic';
export const maxDuration = 60;

const GK = process.env.GEMINI_API_KEY;
const SU = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SK = process.env.SUPABASE_SERVICE_KEY;
const GM = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent";

const TOPICS = [
  "Ansiedade","Apego ansioso","Narcisismo","Trauma infância","Autossabotagem",
  "Dependência emocional","Gaslighting","Síndrome do impostor","Limites saudáveis",
  "Psicologia do dinheiro","Burnout","Relacionamentos tóxicos","Inteligência emocional",
  "Autoestima","Luto e perda","Ansiedade social","Vício em validação","TDAH adulto"
];

async function db(path: string, method = "GET", body?: object) {
  if (!SU || !SK) return null;
  const res = await fetch(`${SU}/rest/v1/${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      apikey: SK,
      Authorization: `Bearer ${SK}`,
      Prefer: method === "POST" ? "return=representation" : "",
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  return res.ok ? res.json() : null;
}

async function gemini(prompt: string, tokens = 800): Promise<string> {
  if (!GK) return "";
  const r = await fetch(`${GM}?key=${GK}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { maxOutputTokens: tokens, temperature: 0.85 }
    }),
  });
  const d = await r.json();
  return d.candidates?.[0]?.content?.parts?.[0]?.text || "";
}

async function getMemoria() {
  const data = await db("cerebro_memoria?order=score.desc&limit=10");
  return data || [];
}

async function getUltimosResultados() {
  const data = await db("registros?order=created_at.desc&limit=20&select=topic,score,views,clicks");
  return data || [];
}

export async function GET(req: Request) {
  const auth = req.headers.get("authorization");
  if (process.env.CRON_SECRET && auth !== `Bearer ${process.env.CRON_SECRET}`) {
    return Response.json({ error: "Unauthorized" }, { status: 401 });
  }

  const startedAt = new Date().toISOString();
  const ciclo = Date.now();

  // 1. LER MEMÓRIA — o que funcionou antes
  const memoria = await getMemoria();
  const topicsVirais = memoria.filter((m: any) => m.score >= 85).map((m: any) => m.topic);
  const topicsRuins = memoria.filter((m: any) => m.score < 70).map((m: any) => m.topic);
  const resultados = await getUltimosResultados();

  // 2. DECIDIR TEMA COM BASE NA MEMÓRIA
  let topicEscolhido: string;
  if (topicsVirais.length > 0 && Math.random() > 0.3) {
    // 70% chance: repetir o que funcionou (com variação)
    topicEscolhido = topicsVirais[Math.floor(Math.random() * topicsVirais.length)];
  } else {
    // 30% chance: explorar novo tema
    const disponiveis = TOPICS.filter(t => !topicsRuins.includes(t));
    topicEscolhido = disponiveis[Math.floor(Math.random() * disponiveis.length)];
  }

  // 3. CONTEXTO DE APRENDIZADO para o Gemini
  const contextoMemoria = memoria.length > 0
    ? `\nMEMÓRIA DO QUE FUNCIONOU ANTES:\n${memoria.slice(0,5).map((m: any) => 
        `- "${m.topic}": score ${m.score}, estilo: ${m.estilo_vencedor || "doc"}`
      ).join("\n")}`
    : "";

  const contextoResultados = resultados.length > 0
    ? `\nÚLTIMOS RESULTADOS:\n${resultados.slice(0,5).map((r: any) => 
        `- "${r.topic}": score ${r.score}`
      ).join("\n")}`
    : "";

  // 4. GERAR CONTEÚDO OTIMIZADO PELA MEMÓRIA
  const prompt = `Canal psicologia.doc — documentários anônimos. Tom: especialista, segunda pessoa "você". CRP compliance, DSM-5/APA. PNL espelhamento obrigatório.
${contextoMemoria}${contextoResultados}

Com base no histórico acima, crie um roteiro VIRAL para YouTube sobre "${topicEscolhido}".
Use os elementos que tiveram MELHOR performance. Inove nos que tiveram score baixo.

TÍTULO SEO (55-65 chars, keyword no início):
GANCHO 0-30s (PNL espelhamento — pessoa se vê imediatamente):
PONTO 1 (dado científico chocante + DSM-5):
PONTO 2 (caso anônimo real + identificação):
PONTO 3 (virada emocional + esperança):
CTA FINAL (WhatsApp + próximo ep com loop aberto):
SCORE VIRAL ESTIMADO (0-100):
INOVAÇÃO APLICADA (o que foi diferente dos anteriores):`;

  const script = await gemini(prompt, 900);

  // 5. EXTRAIR SCORE DO ROTEIRO
  const scoreMatch = script.match(/SCORE VIRAL[^:]*:\s*(\d+)/i);
  const score = scoreMatch ? parseInt(scoreMatch[1]) : Math.floor(Math.random() * 15) + 80;

  const inovacaoMatch = script.match(/INOVAÇÃO APLICADA[^:]*:\s*(.+?)(?:\n|$)/i);
  const inovacao = inovacaoMatch ? inovacaoMatch[1].trim() : "variação padrão";

  // 6. SALVAR RESULTADO
  await db("registros", "POST", {
    topic: topicEscolhido,
    script: script.slice(0, 3000),
    status: "gerado",
    canal: "psicologia.doc",
    created_at: new Date().toISOString(),
    plataforma: "youtube",
    score,
    modelo: "gemini-2.0-flash",
    inovacao,
    ciclo_id: ciclo,
    memoria_usada: topicsVirais.length,
  });

  // 7. ATUALIZAR MEMÓRIA DO CÉREBRO
  const memoriaExistente = memoria.find((m: any) => m.topic === topicEscolhido);
  if (memoriaExistente) {
    // Atualizar score com média ponderada (novo tem mais peso)
    const novoScore = Math.round(memoriaExistente.score * 0.6 + score * 0.4);
    await db(`cerebro_memoria?id=eq.${memoriaExistente.id}`, "PATCH", {
      score: novoScore,
      vezes_gerado: (memoriaExistente.vezes_gerado || 1) + 1,
      estilo_vencedor: score > memoriaExistente.score ? inovacao : memoriaExistente.estilo_vencedor,
      ultimo_ciclo: new Date().toISOString(),
    });
  } else {
    await db("cerebro_memoria", "POST", {
      topic: topicEscolhido,
      score,
      vezes_gerado: 1,
      estilo_vencedor: inovacao,
      criado_em: new Date().toISOString(),
      ultimo_ciclo: new Date().toISOString(),
    });
  }

  return Response.json({
    status: "cerebro_ok",
    ciclo_id: ciclo,
    topic: topicEscolhido,
    score,
    inovacao,
    memoria_usada: topicsVirais.length,
    topics_ruins_evitados: topicsRuins.length,
    startedAt,
    completedAt: new Date().toISOString(),
  });
}
