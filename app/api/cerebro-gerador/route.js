import { createClient } from "@supabase/supabase-js";
export const dynamic = "force-dynamic";

// ================================================================
// CÉREBRO GERADOR V1 — Geração em massa de scripts virais
// Consulta memória eterna → Monta mega-prompt → Chama LLM → Salva
// Baseado nos padrões dos melhores canais de psicologia do mundo
// ================================================================

const SBU = process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co";
const SBK = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
const GROQ_KEY = process.env.GROQ_API_KEY || "";
const NVIDIA_KEY = process.env.NVIDIA_API_KEY || "";
const OPENAI_KEY = process.env.OPENAI_API_KEY || "";

// TOP 10 TEMAS VIRAIS PRIORIZADOS
const TEMAS_VIRAIS_TOP10 = [
  { tema: "Apego Ansioso: quando o medo do abandono controla tudo", formato: "short_60s", emocao: "melancolico" },
  { tema: "7 sinais de narcisismo que todo mundo ignora até ser tarde", formato: "short_60s", emocao: "tenso" },
  { tema: "O que o trauma silencioso faz no seu corpo", formato: "long_15min", emocao: "calmo" },
  { tema: "Ansiedade de alto funcionamento: quando parece que você está bem mas não está", formato: "short_60s", emocao: "urgente" },
  { tema: "Por que você sabota tudo quando está prestes a ser feliz", formato: "short_60s", emocao: "contemplativo" },
  { tema: "A ciência por trás de escolher sempre as mesmas pessoas erradas", formato: "long_15min", emocao: "melancolico" },
  { tema: "Dependência emocional: como o amor vira prisão", formato: "short_60s", emocao: "melancolico" },
  { tema: "Burnout não é cansaço: é apagamento neurológico", formato: "short_60s", emocao: "melancolico" },
  { tema: "O perfeccionista não tem medo de falhar: tem medo de ser descoberto", formato: "short_60s", emocao: "contemplativo" },
  { tema: "Trauma de abandono: por que você nunca se sente seguro em relacionamentos", formato: "long_15min", emocao: "calmo" }
];

// CASES REAIS da memória eterna (fallback se Supabase não responder)
const CASES_FALLBACK = {
  melancolico: { personagem: "Marina, 29 anos, São Paulo", situacao: "Verificava o celular 80 vezes por dia esperando mensagem do namorado. O problema não era o namorado — era o pai ausente quando ela tinha 7 anos.", dado: "72% das pessoas com apego ansioso repetem exatamente o mesmo padrão em todos os relacionamentos (Journal of Personality and Social Psychology, 2021)" },
  tenso: { personagem: "Harvard Medical School — estudo de 30 anos", situacao: "Narcisistas passam em média 7 anos em um relacionamento antes da vítima conseguir se desvencilhar.", dado: "89% das vítimas levam mais 2 anos para parar de justificar o comportamento depois de sair" },
  calmo: { personagem: "Dr. Bessel van der Kolk — O Corpo Guarda as Marcas", situacao: "Trauma não é só o que aconteceu com você. É o que acontece DENTRO de você quando seu sistema nervoso não consegue processar.", dado: "ACE Study — CDC — 17.000 participantes: 4+ experiências adversas na infância = 390% mais chance de depressão" },
  urgente: { personagem: "Experimento do botão — Universidade de Virginia, 2014", situacao: "67% dos homens preferiram se chocar eletricamente a ficarem sozinhos com os próprios pensamentos por 15 minutos.", dado: "A mente ansiosa literalmente foge de si mesma" },
  contemplativo: { personagem: "Brené Brown — 10.000 participantes ao longo de 20 anos", situacao: "Perfeccionismo não é sobre excelência. É sobre evitar vergonha, julgamento e crítica.", dado: "O perfeccionista não tem medo de falhar. Tem medo de que, se falhar, as pessoas descobrirão que ele não é bom o suficiente." }
};

async function carregarMemoriaEterna(sb) {
  try {
    const [{ data: padroes }, { data: regras }] = await Promise.all([
      sb.from("padroes_virais").select("chave,conteudo").eq("ativo", true),
      sb.from("regras_eternas").select("codigo,regra,categoria").eq("prioridade", 10)
    ]);
    return { padroes: padroes || [], regras: regras || [] };
  } catch { return { padroes: [], regras: [] }; }
}

function buildPromptViral(tema, formato, emocao, memoria, caseReal) {
  const isLong = formato.includes("15") || formato.includes("long");
  const duracao = isLong ? "12-15 minutos (800-1.100 palavras exatas no script)" : "55-60 segundos (máximo 130 palavras no script)";

  // Regras absolutas da memória eterna
  const regrasAbs = (memoria.regras || [])
    .filter(r => ["script","imagem","canal"].includes(r.categoria))
    .map(r => `• ${r.codigo}: ${r.regra}`)
    .slice(0, 8).join("\n");

  // Estrutura para long form
  const estruturaLong = isLong ? `
ESTRUTURA 4 ATOS (15 MINUTOS):
[ATO 1 — 0-3min — A FERIDA ABERTA]
• 0-30s SUPER HOOK: mostrar a cena mais intensa ANTES de explicar. Destino antes da jornada.
• 30s-90s: dado real universalizando o problema
• 90s-3min: promessa + mapa do que vem

[ATO 2 — 3-8min — A ANATOMIA DO PROBLEMA]  
• 3-5min: mecanismo neurológico em linguagem acessível + pattern interrupt em 4min30s
• 5-7min: CASO REAL completo com arco narrativo (apresentação → conflito → virada → insight)
• 7-8min: MID-VIDEO HOOK — o mais forte do vídeo. "Existe algo que a maioria dos vídeos não fala..."

[ATO 3 — 8-13min — O QUE MUDA TUDO]
• 8-10min: virada principal — o viewer vê o problema de ângulo completamente novo
• 10-12min: framework prático 3-5 perguntas/passos específicos aplicáveis hoje
• 12-13min: segundo caso real mostrando resultado específico

[ATO 4 — 13-15min — O LEGADO]
• 13-14min: síntese emocional — "você veio pensando X, descobriu Y"
• 14-14min30s: identidade coletiva — o viewer pensa em alguém próximo
• 14min30s-15min: teaser específico do próximo episódio

RETENTION HOOKS OBRIGATÓRIOS a cada 90s:
• 45s: pergunta_espelho, 90s: dado_chocante, 150s: curiosity_gap
• 270s: pattern_interrupt, 360s: pergunta_direta
• 480s: MID-VIDEO HOOK (o mais forte), 600s: revelação_parcial
• 720s: dado_chocante_2, 840s: validação_emocional, 900s: teaser
` : `
ESTRUTURA 7 ATOS (60 SEGUNDOS):
[ATO 1 — HOOK — 0-5s]: cena específica, NUNCA afirmação genérica
[ATO 2 — AMPLIFICAÇÃO — 5-15s]: dado real com fonte
[ATO 3 — CASO REAL — 15-25s]: nome+idade+situação específica
[ATO 4 — VIRADA CIENTÍFICA — 25-35s]: mecanismo simples
[ATO 5 — CUSTO REAL — 35-45s]: urgência sem alarmar
[ATO 6 — CAMINHO — 45-55s]: esperança concreta
[ATO 7 — ANCORAGEM — 55-60s]: desejo de compartilhar sem pedir
`;

  return `Você é o sistema cerebral autônomo psicologia.doc — o maior canal de psicologia do Brasil em 2027.
Sua missão: criar roteiros que hipnotizam o viewer e maximizam retenção.
Baseado nos padrões de: Psych2Go (28M views), Therapy in a Nutshell (68% retenção), Kati Morton (71% retenção).

TEMA: ${tema}
FORMATO: ${formato} | ${duracao}
EMOÇÃO PRINCIPAL: ${emocao}

CASE REAL OBRIGATÓRIO:
• Personagem/Fonte: ${caseReal.personagem}
• Situação/Dado: ${caseReal.situacao}
• Dado científico: ${caseReal.dado}

REGRAS ABSOLUTAS DA MEMÓRIA ETERNA (NUNCA VIOLAR):
${regrasAbs || "• ZERO texto nas imagens\n• Hook com cena específica\n• Dado com fonte real\n• Sensações físicas no corpo\n• Zero pedido de like"}

${estruturaLong}

FORMATO DE SAÍDA — EXATAMENTE ASSIM:
TITULO: [título viral otimizado para CTR]
DESCRICAO_YT: [descrição YouTube 150 palavras com keywords]
TAGS: [15 tags separadas por vírgula]

SCRIPT:
[script completo narrado no formato dos atos acima]

CENAS:
[para cada cena do script: CENA X: [descrição detalhada do personagem + expressão + ambiente + paleta de cor — para gerar prompt Flux]]

GERE AGORA — roteiro completo, não resumo:`;
}

async function chamarLLM(prompt) {
  // Tentar NVIDIA DeepSeek primeiro, depois Groq, depois OpenAI
  const providers = [
    {
      name: "nvidia_deepseek",
      url: "https://integrate.api.nvidia.com/v1/chat/completions",
      key: NVIDIA_KEY,
      model: "deepseek-ai/deepseek-r1",
      headers: {}
    },
    {
      name: "groq",
      url: "https://api.groq.com/openai/v1/chat/completions",
      key: GROQ_KEY,
      model: "llama-3.3-70b-versatile",
      headers: {}
    },
    {
      name: "openai",
      url: "https://api.openai.com/v1/chat/completions",
      key: OPENAI_KEY,
      model: "gpt-4o-mini",
      headers: {}
    }
  ];

  for (const p of providers) {
    if (!p.key) continue;
    try {
      const r = await fetch(p.url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${p.key}`, ...p.headers },
        body: JSON.stringify({
          model: p.model,
          messages: [{ role: "user", content: prompt }],
          max_tokens: 3000,
          temperature: 0.7
        }),
        signal: AbortSignal.timeout(55000)
      });
      if (!r.ok) continue;
      const d = await r.json();
      const text = d.choices?.[0]?.message?.content || "";
      if (text.length > 200) return { texto: text, provider: p.name };
    } catch { continue; }
  }
  return null;
}

function parsearScript(texto) {
  const lines = texto.split("\n");
  let titulo = "", descricao = "", tags = "", script = "", cenas = "";
  let mode = "";
  for (const line of lines) {
    if (line.startsWith("TITULO:")) { titulo = line.replace("TITULO:", "").trim(); continue; }
    if (line.startsWith("DESCRICAO_YT:")) { descricao = line.replace("DESCRICAO_YT:", "").trim(); mode = "desc"; continue; }
    if (line.startsWith("TAGS:")) { tags = line.replace("TAGS:", "").trim(); mode = ""; continue; }
    if (line.startsWith("SCRIPT:")) { mode = "script"; continue; }
    if (line.startsWith("CENAS:")) { mode = "cenas"; continue; }
    if (mode === "desc") descricao += " " + line.trim();
    if (mode === "script") script += line + "\n";
    if (mode === "cenas") cenas += line + "\n";
  }
  return { titulo: titulo || "Vídeo psicologia.doc", descricao: descricao.trim(), tags: tags.split(",").map(t=>t.trim()).filter(Boolean), script: script.trim(), cenas: cenas.trim() };
}

export async function GET(request) {
  const url = new URL(request.url);
  const action = url.searchParams.get("action") || "status";
  const idx = parseInt(url.searchParams.get("idx") || "0");
  const sb = createClient(SBU, SBK);

  if (action === "gerar_um" || action === "gerar_todos") {
    const temas = action === "gerar_um" ? [TEMAS_VIRAIS_TOP10[idx]] : TEMAS_VIRAIS_TOP10;
    const memoria = await carregarMemoriaEterna(sb);
    const resultados = [];

    for (const item of temas) {
      const caseReal = CASES_FALLBACK[item.emocao] || CASES_FALLBACK.contemplativo;
      
      // Tentar case da memória eterna
      const casePadrao = memoria.padroes?.find(p => p.chave === "biblioteca_cases_reais");
      const temaKey = item.emocao === "melancolico" ? "apego_ansioso"
        : item.emocao === "tenso" ? "narcisismo"
        : item.emocao === "calmo" ? "trauma"
        : item.emocao === "urgente" ? "ansiedade" : "perfeccionismo";
      const caseMemoria = casePadrao?.conteudo?.[temaKey]?.[0];
      
      const caseUsar = caseMemoria ? {
        personagem: caseMemoria.personagem || caseMemoria.fonte || caseReal.personagem,
        situacao: caseMemoria.situacao || caseMemoria.dado || caseReal.situacao,
        dado: caseMemoria.dado_cientifico || caseMemoria.dado || caseReal.dado
      } : caseReal;

      const prompt = buildPromptViral(item.tema, item.formato, item.emocao, memoria, caseUsar);
      
      const llmResult = await chamarLLM(prompt);
      if (!llmResult) {
        resultados.push({ tema: item.tema, erro: "LLM indisponível" });
        continue;
      }

      const parsed = parsearScript(llmResult.texto);

      // Salvar no pipeline
      const { data: saved, error } = await sb.from("content_pipeline").insert({
        title: parsed.titulo || item.tema.substring(0, 80),
        script: parsed.script,
        status: "script_ready",
        score: 0,
        metadata: {
          formato: item.formato,
          emocao: item.emocao,
          tema_original: item.tema,
          descricao_yt: parsed.descricao,
          tags_yt: parsed.tags,
          cenas_geradas: parsed.cenas,
          llm_provider: llmResult.provider,
          case_real_usado: caseUsar.personagem,
          engine: "viral_engine_v1",
          memoria_eterna: true,
          gerado_em: new Date().toISOString()
        }
      }).select("id,title,status").single();

      resultados.push({
        ok: !error,
        id: saved?.id,
        titulo: parsed.titulo || item.tema.substring(0, 50),
        formato: item.formato,
        provider: llmResult.provider,
        chars_script: parsed.script.length,
        erro: error?.message
      });

      // Intervalo entre gerações para não sobrecarregar
      if (temas.length > 1) await new Promise(r => setTimeout(r, 2000));
    }

    return Response.json({ ok: true, total: resultados.length, resultados });
  }

  if (action === "preview_prompt") {
    const item = TEMAS_VIRAIS_TOP10[idx];
    const memoria = await carregarMemoriaEterna(sb);
    const caseReal = CASES_FALLBACK[item.emocao];
    const prompt = buildPromptViral(item.tema, item.formato, item.emocao, memoria, caseReal);
    return Response.json({ tema: item.tema, formato: item.formato, emocao: item.emocao, prompt_chars: prompt.length, prompt_preview: prompt.substring(0, 800) + "..." });
  }

  return Response.json({
    sistema: "Cérebro Gerador V1 — psicologia.doc",
    descricao: "Gera scripts virais usando memória eterna + LLM (DeepSeek→Groq→OpenAI)",
    temas_top10: TEMAS_VIRAIS_TOP10.map((t, i) => ({ idx: i, tema: t.tema, formato: t.formato })),
    acoes: {
      "gerar_1_script": "/api/cerebro-gerador?action=gerar_um&idx=0",
      "gerar_todos_10": "/api/cerebro-gerador?action=gerar_todos",
      "preview_prompt": "/api/cerebro-gerador?action=preview_prompt&idx=0"
    },
    llm_chain: "NVIDIA DeepSeek V3 → Groq Llama 3.3 70B → OpenAI GPT-4o-mini",
    memoria_consultada: "Supabase em tempo real — padroes_virais + regras_eternas"
  });
}
