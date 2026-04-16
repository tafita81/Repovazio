import { getSupabase } from "@/lib/supabaseServer";

export const dynamic = "force-dynamic";

export async function GET() {
  const supabase = getSupabase();
  if (!supabase) {
    return Response.json(
      { error: "Supabase not configured. Set NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_KEY." },
      { status: 503 }
    );
  }
  const { data, error } = await supabase.from("registros").select("*");
  if (error) {
    return Response.json({ error: error.message }, { status: 500 });
  }
  return Response.json(data || []);
}
