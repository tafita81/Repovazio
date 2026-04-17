import { getSupabase } from "@/lib/supabaseServer";

export const dynamic = "force-dynamic";

// Rate limiting simples em memória (para Netlify Edge, use Upstash Redis)
const requestLog = new Map();
const RATE_LIMIT = 60; // requests por minuto por IP
const WINDOW_MS = 60_000;

function checkRateLimit(ip) {
  const now = Date.now();
  const key = `${ip}-${Math.floor(now / WINDOW_MS)}`;
  const count = (requestLog.get(key) || 0) + 1;
  requestLog.set(key, count);
  // Cleanup keys antigos
  for (const [k] of requestLog) {
    if (!k.endsWith(String(Math.floor(now / WINDOW_MS)))) requestLog.delete(k);
  }
  return count <= RATE_LIMIT;
}

export async function GET(request) {
  // Rate limiting
  const ip =
    request.headers.get("x-forwarded-for")?.split(",")[0] ||
    request.headers.get("x-real-ip") ||
    "unknown";

  if (!checkRateLimit(ip)) {
    return Response.json(
      { error: "Muitas requisições. Tente novamente em um minuto." },
      {
        status: 429,
        headers: { "Retry-After": "60" },
      }
    );
  }

  const supabase = getSupabase();

  if (!supabase) {
    return Response.json(
      {
        error:
          "Supabase não configurado. Adicione NEXT_PUBLIC_SUPABASE_URL e SUPABASE_SERVICE_KEY nas variáveis de ambiente do Netlify.",
        docs: "https://app.netlify.com/sites/[seu-site]/settings/env",
      },
      { status: 503 }
    );
  }

  try {
    const { data, error } = await supabase
      .from("registros")
      .select("*")
      .order("created_at", { ascending: false })
      .limit(100); // Limite de segurança

    if (error) {
      console.error("[Analytics API] Supabase error:", error);
      return Response.json(
        { error: `Erro no banco de dados: ${error.message}` },
        { status: 500 }
      );
    }

    return Response.json(data || [], {
      headers: {
        "Cache-Control": "private, no-cache, no-store, must-revalidate",
        "X-Total-Count": String((data || []).length),
      },
    });
  } catch (e) {
    console.error("[Analytics API] Unexpected error:", e);
    return Response.json(
      { error: "Erro interno do servidor" },
      { status: 500 }
    );
  }
}
