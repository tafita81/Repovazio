import { createClient } from "@supabase/supabase-js";

export async function GET() {
  const supabase = createClient(
    process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co",
    process.env.SUPABASE_SERVICE_KEY || ""
  );

  const [snaps, pub, mp4, series] = await Promise.all([
    supabase.from("channel_snapshots").select("*").order("snapshot_at",{ascending:false}).limit(1),
    supabase.from("content_pipeline").select("id").eq("status","published"),
    supabase.from("content_pipeline").select("id").eq("status","mp4_ready"),
    supabase.from("content_pipeline").select("status,metadata").not("metadata->>serie","is",null).neq("status","archived")
  ]);

  const snapshot = snaps.data?.[0] || {};
  const seriesData = {};
  for(const r of (series.data || [])){
    const s = r.metadata?.serie;
    if(s){
      if(!seriesData[s]) seriesData[s] = {total:0,published:0};
      seriesData[s].total++;
      if(r.status==="published") seriesData[s].published++;
    }
  }

  return Response.json({
    snapshot,
    publicados: pub.data?.length || 0,
    mp4_ready: mp4.data?.length || 0,
    series: seriesData,
    ts: new Date().toISOString()
  });
}
