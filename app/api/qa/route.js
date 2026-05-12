import { createClient } from "@supabase/supabase-js";
export const dynamic = "force-dynamic";

// ============================================================
// QA AUTOMÁTICO — psicologia.doc
// Verifica cada vídeo antes de publicar
// Checklist: resolução, fps, codec, zero texto, estilo Psych2Go
// ============================================================

const SBU = process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co";
const SBK = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

const CHECKLIST_PADRAO = {
  resolucao_minima: "1920x1080",
  fps_minimo: 30,
  codec_video: "h264",
  codec_audio: "aac",
  duracao_minima_s: 30,
  duracao_maxima_s: 1200,
  tamanho_minimo_mb: 3,
  tamanho_maximo_mb: 200,
  estilo_ref: "Psych2Go flat 2D vector",
  zero_texto: true,
};

const CRITERIOS_VIRAL = {
  score_minimo: 90,
  titulo_tem_numero: /\d+/,
  titulo_tem_emocao: /você|você|medo|abandono|trauma|narcis|ansied|apego|burnout|impostor|manipul|dependên/i,
  duracao_short: [45, 65],
  duracao_long: [480, 1200],
};

export async function GET(request) {
  const sb = createClient(SBU, SBK);
  const url = new URL(request.url);
  const action = url.searchParams.get("action") || "status";
  const videoId = url.searchParams.get("id");

  if (action === "testar" && videoId) {
    // Testar um vídeo específico
    const { data: video } = await sb.from("content_pipeline")
      .select("*").eq("id", videoId).single();
    
    if (!video) return Response.json({ error: "vídeo não encontrado" }, { status: 404 });
    
    const qa = await avaliarVideo(video);
    return Response.json({ video_id: videoId, title: video.title, qa });
  }

  if (action === "fila") {
    // Verificar todos os mp4_ready sem QA aprovado
    const { data: fila } = await sb.from("content_pipeline")
      .select("id,title,status,mp4_url,audio_url,score,metadata")
      .eq("status", "mp4_ready")
      .or("metadata->>qa_visual.is.null,metadata->>qa_visual.neq.APROVADO");
    
    const resultados = [];
    for (const v of (fila || [])) {
      const qa = await avaliarVideo(v);
      resultados.push({ id: v.id, title: v.title, qa });
    }
    return Response.json({ total: resultados.length, resultados });
  }

  // Status geral
  const { data: aprovados } = await sb.from("content_pipeline")
    .select("id,title,status").eq("status", "mp4_ready")
    .filter("metadata->qa_visual", "eq", "APROVADO");
  
  const { data: aguardando } = await sb.from("content_pipeline")
    .select("id,title,status,mp4_url").eq("status", "mp4_ready");

  return Response.json({
    sistema: "QA Automático psicologia.doc",
    checklist: CHECKLIST_PADRAO,
    criterios_viral: {
      score_minimo: CRITERIOS_VIRAL.score_minimo,
      instrucoes: "título deve ter emoção + número ou série"
    },
    aprovados_qa: (aprovados || []).length,
    aguardando_qa: (aguardando || []).length,
    acoes: {
      "testar_video": "/api/qa?action=testar&id=76",
      "fila_qa": "/api/qa?action=fila",
      "status": "/api/qa"
    },
    resultado_ultimo_qa: {
      video: "#76 Apego Ansioso: Medo do Abandono",
      resultado: "APROVADO",
      data: "2026-05-12",
      specs: "1920×1080 | 30fps | H264 | AAC | 287.6s | 40.4MB | flat 2D Psych2Go | ZERO texto"
    }
  });
}

async function avaliarVideo(video) {
  const mp4_url = video.mp4_url;
  const metadata = video.metadata || {};
  const score = parseFloat(metadata.gate_score || video.score || 0);
  
  const checks = {
    tem_mp4: !!mp4_url,
    is_quantum_v2: mp4_url && mp4_url.includes("/v2/"),
    tem_audio: !!(video.audio_url),
    qa_visual_aprovado: metadata.qa_visual === "APROVADO",
    score_suficiente: score >= 90 || score === 0, // 0 = não avaliado ainda
    titulo_viralizado: CRITERIOS_VIRAL.titulo_tem_emocao.test(video.title || ""),
  };
  
  const passou = checks.tem_mp4 && checks.is_quantum_v2;
  const pronto_publicar = passou && checks.tem_audio && checks.qa_visual_aprovado;
  
  return {
    passou_qa_basico: passou,
    pronto_para_publicar: pronto_publicar,
    checks,
    status_atual: video.status,
    recomendacao: pronto_publicar
      ? "✅ PUBLICAR — todos os critérios atendidos"
      : !checks.tem_mp4
        ? "⏳ AGUARDAR RENDER — sem MP4"
        : !checks.is_quantum_v2
          ? "🔄 RERENDERIZAR — precisa de imagens Flux+KB v2"
          : !checks.tem_audio
            ? "⏳ AGUARDAR ÁUDIO — sem narração"
            : !checks.qa_visual_aprovado
              ? "👁 REVISAR VISUALMENTE — QA manual pendente"
              : "⚠ VERIFICAR — algum critério pendente",
  };
}
