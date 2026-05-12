import { createClient } from "@supabase/supabase-js";
export const dynamic = "force-dynamic";
export const revalidate = 0;

// ================================================================
// MEMÓRIA ETERNA — Consulta em Tempo Real
// Cérebro consulta ANTES de gerar qualquer script, imagem ou vídeo
// Garante que TODOS os vídeos seguem os padrões virais eternos
// ================================================================

const SBU = process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co";
const SBK = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

export async function GET(request) {
  const sb = createClient(SBU, SBK);
  const url = new URL(request.url);
  const action = url.searchParams.get("action") || "completo";
  const tema = url.searchParams.get("tema") || "";
  const categoria = url.searchParams.get("categoria") || "";

  try {
    if (action === "regras_absolutas") {
      // Regras que NUNCA podem ser violadas (prioridade 10)
      const { data } = await sb.from("regras_eternas")
        .select("codigo,categoria,descricao,regra,exemplo_ok,exemplo_nao")
        .eq("prioridade", 10)
        .order("categoria");
      return Response.json({ total: (data||[]).length, regras_absolutas: data });
    }

    if (action === "padroes_geracao") {
      // Tudo que o cérebro precisa para GERAR um vídeo
      const emoção = detectarEmocao(tema);
      const [{ data: padroes }, { data: regras }] = await Promise.all([
        sb.from("padroes_virais").select("*").eq("ativo", true).order("prioridade", { ascending: false }),
        sb.from("regras_eternas").select("*").order("prioridade", { ascending: false })
      ]);

      // Filtrar padrão Ken Burns para a emoção
      const kbPadrao = padroes?.find(p => p.chave === "movimento_por_emocao");
      const kbParams = kbPadrao?.conteudo?.perfis?.[emoção] || kbPadrao?.conteudo?.perfis?.contemplativo;

      // Selecionar case real para o tema
      const casesPadrao = padroes?.find(p => p.chave === "biblioteca_cases_reais");
      const temaKey = detectarTemaKey(tema);
      const caseReal = casesPadrao?.conteudo?.[temaKey]?.[0] || null;

      // Estrutura dos 7 atos
      const seteAtos = padroes?.find(p => p.chave === "sete_atos_virais")?.conteudo;

      // Hooks
      const hooks = padroes?.find(p => p.chave === "formulas_hook_por_tipo")?.conteudo;

      // Prompts de imagem
      const imgPadroes = padroes?.find(p => p.chave === "prompts_flux_por_emocao")?.conteudo;

      // Regras absolutas (nunca podem ser violadas)
      const regrasAbsolutas = (regras || []).filter(r => r.prioridade === 10);

      return Response.json({
        tema, emocao: emoção, tema_key: temaKey,
        instrucao: "Consulte estes padrões ANTES de gerar qualquer conteúdo. Todas as regras absolutas devem ser seguidas.",
        regras_absolutas: regrasAbsolutas.map(r => ({
          codigo: r.codigo,
          regra: r.regra,
          exemplo_correto: r.exemplo_ok,
          exemplo_errado: r.exemplo_nao
        })),
        estrutura_script: { sete_atos: seteAtos?.atos, referencias_virais: seteAtos?.referencias_virais },
        hook_recomendado: hooks?.tipos?.espelho_dor?.exemplos?.[0] || "",
        case_real_injetado: caseReal,
        ken_burns: kbParams,
        imagem: {
          sufixo_obrigatorio: imgPadroes?.sufixo_obrigatorio,
          paleta_emocao: imgPadroes?.paletas_por_emocao?.[emoção],
          shots_por_contexto: imgPadroes?.shots_por_contexto,
          personagens_rotativos: imgPadroes?.personagens_rotativos
        },
        checklist_pre_publicacao: [
          "Imagem: ZERO texto/números/letras",
          "Imagem: estilo flat 2D vector (nunca fotorrealista)",
          "Script: hook começa com cena específica",
          "Script: pelo menos 1 dado com fonte real",
          "Script: pelo menos 1 personagem com nome+idade",
          "Script: sensações físicas (não abstrações)",
          "Script: zero pedido de like/inscrição direto",
          "Áudio: voz varia emoção ao longo do script",
          "Ken Burns: movimento calculado pela emoção do tema",
          "Canal: publicar APENAS em UCyCkIpsVgME9yCj_oXJFheA"
        ]
      });
    }

    if (action === "por_categoria" && categoria) {
      const { data: padroes } = await sb.from("padroes_virais")
        .select("*").eq("categoria", categoria).eq("ativo", true);
      const { data: regras } = await sb.from("regras_eternas")
        .select("*").eq("categoria", categoria);
      return Response.json({ categoria, padroes, regras });
    }

    // Resposta COMPLETA — tudo na memória eterna
    const [{ data: padroes }, { data: regras }, { data: evolucoes }] = await Promise.all([
      sb.from("padroes_virais").select("id,categoria,chave,titulo,prioridade,versao,atualizado_em").eq("ativo", true).order("prioridade", { ascending: false }),
      sb.from("regras_eternas").select("codigo,categoria,descricao,prioridade").order("prioridade", { ascending: false }),
      sb.from("cerebro_evolucao").select("versao,tipo,descricao,criado_em").order("criado_em", { ascending: false }).limit(5)
    ]);

    return Response.json({
      sistema: "Memória Eterna psicologia.doc",
      versao: "v1.0",
      descricao: "Consultada em tempo real pelo cérebro antes de gerar qualquer vídeo",
      totais: {
        padroes_virais: (padroes||[]).length,
        regras_eternas: (regras||[]).length,
        regras_absolutas: (regras||[]).filter(r=>r.prioridade===10).length
      },
      padroes_virais: padroes,
      regras_eternas: regras,
      evolucoes_recentes: evolucoes,
      acoes_disponiveis: {
        "gerar_video": "/api/memoria?action=padroes_geracao&tema=apego+ansioso",
        "regras_absolutas": "/api/memoria?action=regras_absolutas",
        "por_categoria": "/api/memoria?action=por_categoria&categoria=imagem",
        "completo": "/api/memoria"
      },
      regras_nunca_violar: [
        "ZERO texto nas imagens (Flux.1 Schnell)",
        "Estilo flat 2D vector — nunca fotorrealista",
        "Hook com cena específica — nunca afirmação genérica",
        "Dado científico com fonte real obrigatória",
        "Psicologia (não psicóloga) até 01/01/2027",
        "Canal UCyCkIpsVgME9yCj_oXJFheA apenas — nunca UCSH63tBfY6wEIdkC4u4zKdg"
      ]
    });

  } catch(e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}

function detectarEmocao(tema) {
  const t = tema.toLowerCase();
  if (t.includes("apego") || t.includes("abandono") || t.includes("dependência") || t.includes("burnout")) return "melancolico";
  if (t.includes("narcis") || t.includes("manipula") || t.includes("abuso")) return "tenso";
  if (t.includes("trauma") || t.includes("cura") || t.includes("integra")) return "calmo";
  if (t.includes("ansied") || t.includes("pânico") || t.includes("medo")) return "urgente";
  if (t.includes("perfec") || t.includes("impostor") || t.includes("autoestima")) return "contemplativo";
  return "contemplativo";
}

function detectarTemaKey(tema) {
  const t = tema.toLowerCase();
  if (t.includes("apego")) return "apego_ansioso";
  if (t.includes("narcis")) return "narcisismo";
  if (t.includes("trauma")) return "trauma";
  if (t.includes("ansied")) return "ansiedade";
  if (t.includes("burnout") || t.includes("esgotamento")) return "burnout";
  if (t.includes("depend") || t.includes("amor")) return "dependencia_emocional";
  if (t.includes("perfec") || t.includes("impostor")) return "perfeccionismo";
  return null;
}
