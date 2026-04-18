export async function GET() {
  return Response.json({
    status: "ok",
    total_content: 0,
    estimated_views: 0,
    estimated_ctr: "0%"
  });
}
