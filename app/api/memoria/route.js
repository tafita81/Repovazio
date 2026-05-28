export const runtime = 'edge';

import { createClient } from "@supabase/supabase-js";
export const dynamic = "force-dynamic";
export const revalidate = 0;

// ================================================================
// MEMÓRIA ETERNA V3 — Consulta em Tempo Real com Localização Global
// Default PT-BR + SEO em 7 idiomas (PT-BR/EN/ES/FR/DE/IT/JA)
// ================================================================

const SBU = process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co";
const SBK = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

function detectarEmocao(tema="") {
  const t = tema.toLowerCase();
  if (t.includes("apego")||t.includes("abandono")||t.includes("depend")||t.includes("burnout")) return "melancolico";
  if (t.includes("narcis")||t.includes("manipula")||t.includes("abuso")) return "tenso";
  if (t.includes("trauma")||t.includes("cura")) return "calmo";
  if (t.includes("ansied")||t.includes("panico")) return "urgente";
  return "contemplativo";
}

function detectarTemaKey(tema="") {
  const t = tema.toLowerCase();
  if (t.includes("apego")) return "apego_ansioso";
  if (t.includes("narcis")) return "narcisismo";
  if (t.includes("trauma")) return "trauma";
  if (t.includes("ansied")) return "ansiedade";
  if (t.includes("burnout")) return "burnout";
  if (t.includes("depend")) return "dependencia_emocional";
  if (t.includes("perfec")) return "perfeccionismo";
  return null;
}

export async function GET(request) {
  const sb = createClient(SBU, SBK);
  const url = new URL(request.url);
  const action = url.searchParams.get("action") || "completo";
  const tema   = url.searchParams.get("tema") || "";
  const formato= url.searchParams.get("formato") || "short_60s";
  const chave  = url.searchParams.get("chave") || "";

  const [{ data: padroes }, { data: regras }] = await Promise.all([
    sb.from("padroes_virais").select("*").eq("ativo", true).order("prioridade", { ascending: false }),
    sb.from("regras_eternas").select("*").order("prioridade", { ascending: false })
  ]);
  const ALL_PADROES = padroes || [];
  const ALL_REGRAS  = regras  || [];
  const padrao = (k) => ALL_PADROES.find(p => p.chave === k)?.conteudo;

  // ── AÇÃO: localizacao_global ──────────────────────────────
  if (action === "localizacao") {
    return Response.json(padrao("seo_localizacao_7_idiomas"));
  }

  if (action === "cases_globais") {
    return Response.json(padrao("biblioteca_cases_sucesso_brasileiro_universal"));
  }

  // ── AÇÃO: gerar_video — agora inclui instruções de localização ──
  if (action === "gerar_video" && tema) {
    const emocao  = detectarEmocao(tema);
    const temaKey = detectarTemaKey(tema);
    const isLong  = formato.includes("15") || formato.includes("long");

    const estrutura = isLong ? padrao("long_form_15min_engenharia_atencao") : padrao("sete_atos_virais");
    const casesBase = padrao("biblioteca_cases_reais");
    const casesGlobais = padrao("biblioteca_cases_sucesso_brasileiro_universal");
    const caseReal  = temaKey ? casesBase?.[temaKey]?.[0] : null;
    const caseSucesso = casesGlobais?.cases_de_sucesso_real_apos_video?.[
      temaKey === "apego_ansioso" ? "marina_apego_ansioso" :
      temaKey === "narcisismo" ? "lucas_narcisismo_relacionamento" :
      temaKey === "ansiedade" ? "sofia_ansiedade_alto_funcionamento" :
      temaKey === "burnout" ? "rafael_burnout_neurologico" :
      temaKey === "dependencia_emocional" ? "isabela_dependencia_emocional" :
      temaKey === "perfeccionismo" ? "lara_perfeccionismo_burnout" : null
    ];

    const kbBase = padrao("movimento_por_emocao");
    const kbPerf = isLong ? estrutura?.ken_burns_5_perfis_15min : kbBase?.perfis?.[emocao];

    const hooksBase = padrao("formulas_hook_por_tipo");
    const imgBase   = padrao("prompts_flux_por_emocao");
    const planej    = padrao("pre_producao_cerebro_completo");
    const localizacao = padrao("seo_localizacao_7_idiomas");

    const regrasAbs = ALL_REGRAS.filter(r => r.prioridade === 10).map(r => ({
      codigo: r.codigo, regra: r.regra, ok: r.exemplo_ok, nao: r.exemplo_nao
    }));

    return Response.json({
      ok: true, tema, formato, emocao, tema_key: temaKey,
      is_long_form: isLong,
      fonte: "supabase_tempo_real_v3",
      total_padroes_carregados: ALL_PADROES.length,
      total_regras_carregadas:  ALL_REGRAS.length,

      // CONTEÚDO DEFAULT EM PT-BR
      default: { idioma: "pt-BR", obrigatorio_eterno: true, voz_tts: "pt-BR-FranciscaNeural" },
      
      // ESTRUTURA NARRATIVA
      estrutura_narrativa: estrutura,
      retention_hooks: isLong ? planej?.etapa_4_retention_hooks?.formato_15min : planej?.etapa_4_retention_hooks?.formato_60s,
      
      // CASES — DEFAULT BRASILEIRO COM SUCESSO REAL
      case_real_default: caseReal,
      case_sucesso_universal: caseSucesso,
      instrucao_nomes_BR: "Manter Marina/Lucas/Sofia/Rafael/Isabela/Lara em TODAS as traduções",
      
      // KEN BURNS + IMAGEM + ÁUDIO
      ken_burns: kbPerf,
      imagem_config: { paleta: imgBase?.paletas_por_emocao?.[emocao], sufixo: imgBase?.sufixo_obrigatorio },
      audio_config: isLong ? estrutura?.audio_variacao_obrigatoria : null,
      
      // LOCALIZAÇÃO GLOBAL
      localizacao_global: {
        idiomas_alvo: Object.keys(localizacao?.idiomas_estrategicos || {}),
        cpm_esperado: "$5-12 USD mix global vs $2-4 só BR",
        publicar_em: ["youtube_localizations","instagram_caption_camadas","tiktok_captions_auto"],
        endpoint_localizacao: "/api/localizacao?action=localizar_video&video_id=X"
      },
      
      regras_absolutas: regrasAbs,
      
      checklist_pre_render: [
        "Hook cena específica?", "Dado com fonte real?", "Personagem nome+idade brasileiro?",
        "Sensações físicas?", "Curiosity gap?", "Zero pedido like?",
        "Imagens sem texto?", "Progressão emocional dark→warm?",
        "KB correto?", "Canal UCyCkIpsVgME9yCj_oXJFheA?",
        "Áudio PT-BR (default eterno)?",
        "Será publicado com localizations em 7 idiomas?",
        "SRT extraído para auto-tradução?"
      ]
    });
  }

  if (action === "regras_absolutas") {
    return Response.json({
      total: ALL_REGRAS.filter(r=>r.prioridade===10).length,
      regras_absolutas: ALL_REGRAS.filter(r=>r.prioridade===10),
      por_categoria: ALL_REGRAS.filter(r=>r.prioridade===10).reduce((acc,r)=>{
        if(!acc[r.categoria]) acc[r.categoria]=[];
        acc[r.categoria].push(r.codigo);
        return acc;
      }, {})
    });
  }

  if (action === "long_form")    return Response.json(padrao("long_form_15min_engenharia_atencao"));
  if (action === "canais")        return Response.json(padrao("mapeamento_padroes_top_canais"));
  if (action === "planejamento")  return Response.json(padrao("pre_producao_cerebro_completo"));
  if (action === "chave" && chave) return Response.json({ chave, conteudo: padrao(chave) });

  const { data: evolucoes } = await sb.from("cerebro_evolucao")
    .select("versao,tipo,descricao,criado_em")
    .order("criado_em", { ascending: false }).limit(5);

  return Response.json({
    sistema: "Memória Eterna V3 — psicologia.doc",
    versao: "3.0",
    descricao: "Consultada em tempo real pelo cérebro. Default PT-BR + SEO global em 7 idiomas para descobribilidade mundial.",
    totais: {
      padroes_virais: ALL_PADROES.length,
      regras_eternas: ALL_REGRAS.length,
      regras_absolutas: ALL_REGRAS.filter(r=>r.prioridade===10).length,
      regras_localizacao: ALL_REGRAS.filter(r=>r.categoria==="localizacao").length
    },
    padroes_disponiveis: ALL_PADROES.map(p=>({ chave: p.chave, categoria: p.categoria, titulo: p.titulo, prioridade: p.prioridade })),
    
    localizacao_global_resumo: {
      default_eterno: "Áudio sempre PT-BR (Edge TTS FranciscaNeural)",
      idiomas_seo: ["pt-BR","en","es","fr","de","it","ja"],
      cpm_esperado: "$5-12 USD mix vs $2-4 só BR",
      facilitadores_plataforma: ["YouTube localizations + auto-captions","Instagram caption multi-camadas","TikTok auto-translation"]
    },

    acoes: {
      "gerar_60s":              "/api/memoria?action=gerar_video&tema=apego+ansioso&formato=short_60s",
      "gerar_15min":            "/api/memoria?action=gerar_video&tema=trauma&formato=long_15min",
      "localizacao_global":     "/api/memoria?action=localizacao",
      "cases_globais":          "/api/memoria?action=cases_globais",
      "ver_long_form":          "/api/memoria?action=long_form",
      "ver_canais":             "/api/memoria?action=canais",
      "ver_planejamento":       "/api/memoria?action=planejamento",
      "regras_absolutas":       "/api/memoria?action=regras_absolutas",
      "localizar_video":        "/api/localizacao?action=localizar_video&video_id=294"
    },
    
    evolucoes_recentes: evolucoes || [],
    
    regras_nunca_violar: [
      "ZERO texto nas imagens (Flux.1 Schnell)",
      "Estilo flat 2D vector — nunca fotorrealista",
      "Hook com cena específica — nunca afirmação genérica",
      "Dado científico com fonte real obrigatória",
      "Case real com nome brasileiro+idade+profissão em todo vídeo",
      "Áudio sempre PT-BR (default eterno — localização via SEO, nunca via re-narração)",
      "Toda publicação YouTube com snippet.localizations em 7 idiomas",
      "Toda publicação YouTube com SRT em pt-BR (base auto-tradução global)",
      "Nomes brasileiros mantidos em todas as traduções",
      "Cases com situações universais (não só BR-específicas)",
      "Retention hook a cada 60-90 segundos",
      "Psicologia (não psicóloga) até 01/01/2027",
      "Canal UCyCkIpsVgME9yCj_oXJFheA — NUNCA UCSH63tBfY6wEIdkC4u4zKdg"
    ]
  });
}
