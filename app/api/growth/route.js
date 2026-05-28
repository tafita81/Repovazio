export const runtime = 'edge';

import { createClient } from "@supabase/supabase-js";

export const dynamic = "force-dynamic";
export const revalidate = 0;

export async function GET() {
  try {
    const sbUrl = process.env.SUPABASE_URL || "https://tpjvalzwkqwttvmszvie.supabase.co";
    const sbKey = process.env.SUPABASE_SERVICE_KEY || process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";
    if (!sbKey) return Response.json({ error: "SUPABASE_KEY nao configurada" }, { status: 500 });

    const sb = createClient(sbUrl, sbKey);

    // Pipeline status
    const { data: pipe } = await sb.from("content_pipeline").select("status").limit(2000);
    const cnt = {};
    (pipe || []).forEach(r => { cnt[r.status] = (cnt[r.status] || 0) + 1; });

    // Canal (ultimo snapshot)
    const { data: snaps } = await sb.from("channel_snapshots").select("subscribers,views_28d,ctr_28d,total_views,watch_time_hrs,delta_subs,days_to_1k_est,snapshot_at").order("snapshot_at", { ascending: false }).limit(1);

    // Series
    const { data: seriesRows } = await sb.from("content_pipeline").select("metadata").not("metadata->>serie", "is", null).limit(500);
    const series = {};
    (seriesRows || []).forEach(r => { const s = r.metadata?.serie; if (s) series[s] = (series[s] || 0) + 1; });

    // Ultimos publicados
    const { data: ultimos } = await sb.from("content_pipeline").select("id,title,youtube_url,mp4_url,audio_url,thumbnail_url").eq("status", "published").order("id", { ascending: false }).limit(10);

    return Response.json({
      publicados: cnt.published || 0,
      mp4_ready: cnt.mp4_ready || 0,
      pipeline: cnt,
      series: Object.keys(series),
      canal: snaps?.[0] || {},
      ultimos_publicados: ultimos || [],
      timestamp: new Date().toISOString()
    });
  } catch (e) {
    return Response.json({ error: e.message }, { status: 500 });
  }
}
