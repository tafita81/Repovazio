import { supabase } from "@/lib/supabase";

export async function GET() {
  try {
    const result: any = await supabase
      .from("content")
      .select("id, created_at, text");

    const data = result?.data || [];

    return Response.json({
      status: "ok",
      count: data.length,
      items: data
    });

  } catch (error: any) {
    return Response.json({
      status: "fallback",
      count: 0,
      items: []
    });
  }
}
