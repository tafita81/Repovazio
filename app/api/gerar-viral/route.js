import { createClient } from "@supabase/supabase-js";
export const dynamic = "force-dynamic";

// ================================================================
// GERADOR VIRAL V2 — Consulta memória eterna antes de gerar
// /api/memoria é chamado para carregar padrões em tempo real
// Garante que TODOS os vídeos seguem os padrões eternos
// ================================================================

const SBU = process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co";
const SBK = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

async function consultarMemoriaEterna(tema) {
  try {
    // Buscar padrões diretamente do Supabase em tempo real
    const sb = createClient(SBU, SBK);
    const [
      { data: regras },
      { data: padroes }
    ] = await Promise.all([
      sb.from("regras_eternas").select("*").order("prioridade", { ascending: false }),
      sb.from("padroes_virais").select("*").eq("ativo", true).order("prioridade", { ascending: false })
    ]);
    return { regras: regras || [], padroes: padroes || [] };
  } catch { return { regras: [], padroes: [] }; }
}

function detectarEmocao(tema) {
  const t = tema.toLowerCase();
  if (t.includes("apego")||t.includes("abandono")||t.includes("dependência")||t.includes("burnout")) return "melancolico";
  if (t.includes("narcis")||t.includes("manipula")||t.includes("abuso")) return "tenso";
  if (t.includes("trauma")||t.includes("cura")) return "calmo";
  if (t.includes("ansied")||t.includes("pânico")||t.includes("medo")) return "urgente";
  return "contemplativo";
}

function detectarTemaKey(tema) {
  const t = tema.toLowerCase();
  if (t.includes("apego")) return "apego_ansioso";
  if (t.includes("narcis")) return "narcisismo";
  if (t.includes("trauma")) return "trauma";
  if (t.includes("ansied")) return "ansiedade";
  if (t.includes("burnout")||t.includes("esgotamento")) return "burnout";
  if (t.includes("depend")||t.includes("amor")) return "dependencia_emocional";
  if (t.includes("perfec")||t.includes("impostor")) return "perfeccionismo";
  return null;
}

function buildMegaPromptViral(tema, formato, memoriaEterna, emoção, temaKey) {
  const isShort = formato.includes("60s")||formato.includes("short");
  const duracao = isShort ? "55-60 segundos | máximo 130 palavras" : "8-12 minutos | 800-1.200 palavras";

  // Extrair regras absolutas da memória eterna
  const regrasAbsolutas = (memoriaEterna.regras||[])
    .filter(r => r.prioridade === 10 && ["script","imagem","canal"].includes(r.categoria))
    .map(r => `${r.codigo}: ${r.regra}`)
    .join("\n");

  // Extrair case real
  const casesPadrao = memoriaEterna.padroes?.find(p => p.chave === "biblioteca_cases_reais");
  const caseReal = temaKey ? casesPadrao?.conteudo?.[temaKey]?.[0] : null;
  const caseStr = caseReal
    ? `\nCASE REAL OBRIGATÓRIO:\n- ${caseReal.personagem||caseReal.fonte||""}\n- ${caseReal.situacao||caseReal.dado||""}\n- Reviravolta: ${caseReal.reviravolta||caseReal.choque||""}`
    : "";

  // Extrair hook recomendado
  const hooksPadrao = memoriaEterna.padroes?.find(p => p.chave === "formulas_hook_por_tipo");
  const hooksExemplos = hooksPadrao?.conteudo?.tipos?.espelho_dor?.exemplos || [];

  return `Você é o sistema cerebral autônomo psicologia.doc.
Sua missão: gerar roteiros que hipnotizam o viewer e maximizam retenção.

TEMA: ${tema}
FORMATO: ${formato} | ${duracao}
EMOÇÃO PRINCIPAL: ${emoção}
${caseStr}

═══════ REGRAS ABSOLUTAS DA MEMÓRIA ETERNA (NUNCA VIOLAR) ═══════
${regrasAbsolutas}
════════════════════════════════════════════════════════════════

EXEMPLOS DE HOOK (escolher ou adaptar):
${hooksExemplos.slice(0,3).map((h,i) => `${i+1}. "${h}"`).join("\n")}

ESTRUTURA DOS 7 ATOS OBRIGATÓRIA:
[ATO 1 — HOOK — 0-5s]
Narrador: [cena específica — 2 frases impactantes]
Visual: [personagem + expressão + ambiente]

[ATO 2 — AMPLIFICAÇÃO — 5-15s]
Narrador: [dado com fonte real + implicação chocante]
Visual: [personagem reagindo ao dado]

[ATO 3 — CASO REAL — 15-25s]
Narrador: [nome + idade + profissão + situação específica]
Visual: [personagem em situação do caso]

[ATO 4 — VIRADA CIENTÍFICA — 25-35s]
Narrador: [mecanismo simples + analogia visual]
Visual: [expressão de insight/revelação]

[ATO 5 — CUSTO REAL — 35-45s]
Narrador: [consequência sem alarmar + o que se perde]
Visual: [cenário futuro ou dois personagens]

[ATO 6 — CAMINHO — 45-55s]
Narrador: [esperança concreta + insight específico]
Visual: [expressão de determinação ou alívio]

[ATO 7 — ANCORAGEM — 55-60s]
Narrador: [cria desejo de compartilhar — identidade coletiva]
Visual: [expressão de esperança ou insight suave]

CHECKLIST ANTES DE FINALIZAR:
□ Hook começa com cena específica
□ Pelo menos 1 dado com fonte real
□ Pelo menos 1 personagem com nome+idade
□ Sensações físicas no corpo (não abstrações)
□ Pelo menos 1 gancho de curiosidade
□ Zero pedido de like/inscrição direto
□ ZERO indicação de texto nas descrições de imagem

GERE O ROTEIRO AGORA:`;
}

export async function GET(request) {
  const url = new URL(request.url);
  const action = url.searchParams.get("action") || "status";
  const tema = url.searchParams.get("tema") || "";
  const formato = url.searchParams.get("formato") || "short_60s";

  if (action === "gerar" && tema) {
    // CONSULTAR MEMÓRIA ETERNA EM TEMPO REAL
    const memoriaEterna = await consultarMemoriaEterna(tema);
    const emoção = detectarEmocao(tema);
    const temaKey = detectarTemaKey(tema);

    // Ken Burns da memória eterna
    const kbPadrao = memoriaEterna.padroes?.find(p => p.chave === "movimento_por_emocao");
    const kbParams = kbPadrao?.conteudo?.perfis?.[emoção] || {};

    // Case real
    const casesPadrao = memoriaEterna.padroes?.find(p => p.chave === "biblioteca_cases_reais");
    const caseReal = temaKey ? casesPadrao?.conteudo?.[temaKey]?.[0] : null;

    // Imagem params
    const imgPadrao = memoriaEterna.padroes?.find(p => p.chave === "prompts_flux_por_emocao");
    const imagemParams = {
      sufixo: imgPadrao?.conteudo?.sufixo_obrigatorio,
      paleta: imgPadrao?.conteudo?.paletas_por_emocao?.[emoção],
      shots: imgPadrao?.conteudo?.shots_por_contexto,
      personagens: imgPadrao?.conteudo?.personagens_rotativos
    };

    const megaPrompt = buildMegaPromptViral(tema, formato, memoriaEterna, emoção, temaKey);

    return Response.json({
      ok: true,
      tema, formato, emocao: emoção, tema_key: temaKey,
      fonte: "memoria_eterna_supabase_tempo_real",
      total_regras_carregadas: memoriaEterna.regras.length,
      total_padroes_carregados: memoriaEterna.padroes.length,
      mega_prompt_script: megaPrompt,
      case_real: caseReal,
      ken_burns: kbParams,
      imagem: imagemParams,
      checklist: [
        "ZERO texto nas imagens",
        "Flat 2D vector style",
        "Hook com cena específica",
        "Dado com fonte real",
        "Case real com nome+idade",
        "Sensações físicas no corpo",
        "Ken Burns por emoção",
        "Canal UCyCkIpsVgME9yCj_oXJFheA"
      ]
    });
  }

  return Response.json({
    sistema: "Gerador Viral V2 — Integrado com Memória Eterna",
    versao: "2.0",
    diferencial: "Consulta Supabase em tempo real antes de cada geração",
    acoes: {
      "gerar_short": "/api/gerar-viral?action=gerar&tema=apego+ansioso&formato=short_60s",
      "gerar_long": "/api/gerar-viral?action=gerar&tema=trauma+invisivel&formato=long_8min",
      "ver_memoria": "/api/memoria",
      "ver_memoria_geracao": "/api/memoria?action=padroes_geracao&tema=apego+ansioso"
    }
  });
}
