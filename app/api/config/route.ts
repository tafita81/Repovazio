import { supabase } from "@/lib/supabase";

export async function GET() {
  const { data } = await supabase
    .from("config")
    .select("data")
    .limit(1)
    .single();

  return Response.json(data?.data || {});
}

export async function POST(req) {
  const body = await req.json();

  await supabase.from("config").upsert({
    id: "global",
    data: body
  });

  return Response.json({ ok: true });
}
