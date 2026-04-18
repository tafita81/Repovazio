import { supabase } from "@/lib/supabase";

export async function GET() {
  try {
    const { data } = await supabase
      .from("content")
      .select("created_at")

    const total = data?.length || 0;

    return Response.json({
      status: "ok",
      total_content: total,
      estimated_views: total * 100,
      estimated_ctr: "3.2%"
    });

  } catch (e) {
    return Response.json({ error: true, message: e.message });
  }
}
