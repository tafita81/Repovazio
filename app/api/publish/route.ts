// Mock publisher – replace with real integrations (TikTok/YouTube/IG)
import { supabase } from "@/lib/supabase";

export async function POST() {
  try {
    // get latest content
    const { data } = await supabase
      .from("content")
      .select("id, text")
      .order("created_at", { ascending: false })
      .limit(1)
      .single();

    if (!data) return Response.json({ error: true, message: "no content" });

    // simulate publish
    const published = {
      id: data.id,
      status: "published",
      platform: "mock",
      publishedAt: new Date().toISOString()
    };

    return Response.json({ status: "ok", published });
  } catch (e) {
    return Response.json({ error: true, message: e.message });
  }
}
