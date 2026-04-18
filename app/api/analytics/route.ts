import { supabase } from "@/lib/supabase";

export async function GET() {
  const { data, error } = await supabase
    .from("content")
    .select("id, created_at, text")
    .order("created_at", { ascending: false })
    .limit(50);

  if (error) {
    return Response.json({ error: true, message: error.message });
  }

  return Response.json({
    status: "ok",
    count: data.length,
    items: data
  });
}
